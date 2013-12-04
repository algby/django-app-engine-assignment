from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from google.appengine.ext import blobstore
from api.models import Story

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

    return render(request, 'frontend/story.html', {
        'title': story.title,
        'story': story,
    })

def index(request):
    stories = Story.objects.filter(status='published')

    return render(request, 'frontend/index.html', {
        'title': 'Home',
        'stories': stories,
    })
