from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth import logout as logout_user
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from google.appengine.ext import blobstore
from api.models import Story, StoryVote, FrontEndUserForm, MediaForm, WinaUser
from modules.django_gcs_get_serving_url import get_serving_url
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
    # Get the top 20 stories with the highest vote count
    story_votes = StoryVote.query(StoryVote.status == 'published').order(-StoryVote.total).fetch(10)

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
    db_stories = Story.objects.filter(pk__in=ids, status='published')

    # Due to the limitations in django tempaltes we need to combine the lists here
    stories = []
    for story in db_stories:
        stories.append({
            'story': story,
            'votes': votes[str(story.id)]
        })

    # Now we have the story objects out the db we need to resort them
    stories = sorted(stories, key=lambda x: x['votes']['total'], reverse=True)

    return render(request, 'frontend/index.html', {
        'title': 'Home',
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
