from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth import logout as logout_user
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from api.models import Story, StoryVote, FrontEndUserForm, MediaForm, WinaUser
from modules.django_gcs_get_serving_url import get_serving_url
from google.appengine.api import search as gsearch
import json

def blob_view(request, blob_key):
    # Try and retrieve the blob
    blob = blobstore.get(blob_key)

    # If we couldn't retrieve it then return a 404
    if not blob:
        return HttpResponseNotFound('404, Blob not found')

    # Set up the HTTP Response for the blob
    response = HttpResponse()

    # Add the X-AppEngine-BlobKey header
    response[blobstore.BLOB_KEY_HEADER] = str(blob_key)

    # Remove the content-type text/html that is set by default and let app engine work it out itself
    del response['Content-Type']

    return response

def story_view(request, slug, id):
    # Try and retrieve the story based on the id, the slug can change and it doesn't matter
    story = Story.objects.get(id=id)

    # Get the number of votes the story has
    votes = story.get_votes()

    return render(request, 'frontend/story.html', {
        'title': story.title,
        'story': story,
        'votes': votes,
    })

def index(request):
    # Get the top 10 stories with the highest vote count with at least 1 vote
    story_votes = StoryVote.query(StoryVote.status == 'published', StoryVote.total >= 1).order(-StoryVote.total).fetch(10)

    # Used to store all the ids needed for the sql query
    ids = []

    # Used to provide a way to easily access the vote data for a story in the template
    votes = {}

    for story in story_votes:
        id = story.key.id().split(':')[1]
        ids.append(id)
        votes[id] = {
            'upvotes': story.upvotes,
            'downvotes': story.downvotes,
            'total': story.total,
        }

    # Query for the full story object from the database
    db_stories = Story.objects.filter(pk__in=ids, status='published').order_by('-date_created')

    # Due to the limitations in django templates we need to combine the lists here
    stories = []
    for story in db_stories:
        stories.append({
            'story': story,
            'votes': votes[str(story.id)]
        })

    # Now we have the story objects out the db we need to resort them
    stories = sorted(stories, key=lambda x: x['votes']['total'], reverse=True)

    return render(request, 'frontend/stories.html', {
        'title': 'Home',
        'page_title': 'Trending Stories',
        'stories': stories,
    })

def latest(request):
    # Query for the full story object from the database
    db_stories = Story.objects.filter(status='published').order_by('-date_created')

    # Used to store all the keys needed for the datastore query
    keys = []

    for story in db_stories:
        keys.append(ndb.Key('StoryVote', 'StoryVote:%s' % story.id))

    # Get the stories based on the ids we pulled from the db
    story_votes = ndb.get_multi(keys)

    # Used to provide a way to easily access the vote data for a story in the template
    votes = {}

    for story in story_votes:
        id = story.key.id().split(':')[1]
        votes[id] = {
            'upvotes': story.upvotes,
            'downvotes': story.downvotes,
            'total': story.total,
        }

    # Due to the limitations in django templates we need to combine the lists here
    stories = []
    for story in db_stories:
        stories.append({
            'story': story,
            'votes': votes[str(story.id)]
        })

    # Sort them by date in asc order again, damn it python..
    stories = sorted(stories, key=lambda x: x['story'].date_created, reverse=True)

    return render(request, 'frontend/stories.html', {
        'title': 'Latest',
        'page_title': 'Latest Stories',
        'stories': stories,
    })

def vote(request):
    # Set up a dict to return
    response = {
        'error': None,
        'data': [],
    }

    # Grab the data we expect to be passed
    story_id = request.GET.get('story_id', None)
    type = request.GET.get('type', None)

    # Check that a story id was passed
    if not story_id:
        response['error'] = 'A story_id must be passed'
        return HttpResponse(json.dumps(response), mimetype='application/json')

    # Check the type of vote is valid
    if not type or type not in ['up', 'down']:
        response['error'] = 'type must be either up or desc'
        return HttpResponse(json.dumps(response), mimetype='application/json')

    # Try and look up the story to check it exists
    try:
        story = Story.objects.get(id=story_id)

    except:
        response['error'] = 'Unable to find that story'
        return HttpResponse(json.dumps(response), mimetype='application/json')

    # Add the votes
    try:
        if type == 'up':
            story.upvote()

        elif type == 'down':
            story.downvote()

        response['data'] = story.get_votes()

        return HttpResponse(json.dumps(response), mimetype='application/json')

    except:
        response['error'] = 'Error adding vote to story'
        return HttpResponse(json.dumps(response), mimetype='application/json')

def join(request):
    # Is it a POST request, i.e is the form being submitted
    if request.method == 'POST':
        user_form = FrontEndUserForm(request.POST)

        # Run through any validation rules we have
        if user_form.is_valid():
            # Save the form data to the db
            user = user_form.save()

            # Show a success message to the user
            messages.success(request, 'Account successfully created!')

            # Log the user in!
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            # Redirect them back to the user home page
            return redirect('/')

    form = user_form if request.method == 'POST' else FrontEndUserForm()

    return render(request, 'frontend/form.html', {
        'title': 'Join',
        'submit': 'Create Account',
        'form': form,
    })

@login_required
def logout(request):
    # Logout the user
    logout_user(request)

    # Redirect them to the home page
    return redirect('/')

@login_required
def submit(request):
    # Is it a POST request, i.e is the form being submitted
    if request.method == 'POST':
        form = MediaForm(request.POST, request.FILES)

        # Run through any validation rules we have
        if form.is_valid():
            # Save the form data to the db
            form = form.save(commit=False)
            form.author = WinaUser.objects.get(id=request.user.id)

            # Is audio/video/image being submitted? If so we need to override content
            if form.type in ['audio', 'video', 'image']:
                form.content = get_serving_url(blob_key=request.FILES['file'].blob_key, file_name=request.FILES['file'].name)

            form.save()

            # Show a success message to the user
            messages.success(request, 'Submission recieved, thank you!')

            # Redirect them back to the media home page
            return redirect('/')

    form = form if request.method == 'POST' else MediaForm()

    return render(request, 'frontend/form.html', {
        'title': 'Media Submission',
        'form': form,
        'submit': 'Submit',
    })

def search(request):
    # Grab the search term from the url
    query = request.GET.get('query', '')

    try:
        # Set the index to use
        index = gsearch.Index(name='stories-and-media-index')

        # Run the search
        search_results = index.search(query + ' doc_type=story status=published')

    # If something went wrong just return 0 results
    except:
        search_results = []

    # Set up the result dict for the template
    results = []

    # Populate the result dict
    for search_item in search_results:
        item = {'id': int(search_item.doc_id.split(':')[1])}

        for field in search_item.fields:
            item[field.name] = field.value

        # Patch in the votes, in a real app this would be done outide the loop to reduce round trips to the datastore
        item['votes'] = StoryVote.get_by_id('StoryVote:%s' % item['id'])

        # Patch in the avatar, again this is sub-optimal and could be implemented in a more efficient way
        # were this not a prototype. Most likely by including the author email in the search index so that
        # the gravatar url can be calculated on the fly
        user = WinaUser.objects.get(id=item['author_id'])
        item['author_avatar'] = user.get_avatar()

        results.append(item)

    return render(request, 'frontend/search.html', {
        'title': 'Search for "%s"' % query,
        'query': query,
        'results': results,
    })
