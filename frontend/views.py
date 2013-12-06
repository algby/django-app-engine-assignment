from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from google.appengine.ext import blobstore
from api.models import Story, StoryVote
import json

# Helper for the vote action
def __return_json_error(self, error_message):
    return HttpResponse(json.dumps({
        'error': error_message,
        'data': [],
    }), mimetype='application/json')

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
