from django.http import HttpResponse, HttpResponseNotFound

from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore

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

    # Remove the content-type that is set by default and let app engine work it out itself
    del response['Content-Type']

    return response

def index(request):
    return HttpResponse('frontend')
