from django.http import HttpResponse
from django.utils.dateformat import format
from google.appengine.api import search as gsearch
from api.models import Media
import json

def index(request):
    return HttpResponse(json.dumps({'message': 'Welcome to the WINA API!'}), mimetype='application/json')

# Slightly messy method that abstracts away the differences between search and db objects
def __formatMediaOrStory(object, type='db_object'):
    return {
        'id': object['id'] if type == 'search_object' else object.id,
        'title': object['title'] if type == 'search_object' else object.title,
        'doc_type': object['doc_type'] if type == 'search_object' else object.doc_type,
        'type': object['type'] if type == 'search_object' else object.type,
        'content': object['content'] if type == 'search_object' else object.content,
        'author': {
            'id': object['author_id'] if type == 'search_object' else object.author_id,
            'username': object['author_username'] if type == 'search_object' else object.author.username,
            'first_name': object['author_first_name'] if type == 'search_object' else object.author.first_name,
            'last_name': object['author_last_name'] if type == 'search_object' else object.author.last_name,
        },
        'date_created': int(format(object['date_created'] if type == 'search_object' else object.date_created, 'U')),
    }

# Return all media as json
def media(request):
    # Get all the media objects
    media = Media.objects.all()

    # Set up a dict to return
    response = {
        'message': None,
        'data': [],
    }

    # Append all the media objects to the response object
    for object in media:
        response['data'].append(__formatMedia(object))

    # Return the response as json
    return HttpResponse(json.dumps(response), mimetype='application/json')

# Look up an individual piece of media
def media_lookup(request, id):
    # Get the media object
    media = Media.objects.get(id=id)

    # Set up a dict to return
    response = {
        'message': None,
        'data': [__formatMedia(media)],
    }

    # Return the response as json
    return HttpResponse(json.dumps(response), mimetype='application/json')

# Search for a story
def search(request):
    # Get the query and type
    query = request.GET.get('query', None)
    doc_type = request.GET.get('doc_type', None)

    # Was a query passed?
    if query:
        # Set the index to use
        index = gsearch.Index(name='stories-and-media')

        # Append a type filter if it was specified
        if doc_type:
            query += ' doc_type = %s' % doc_type

        # Run the search and set up the default response object
        results = index.search(query)
        response = {
            'error': None,
            'data': []
        }

        # Format the results in the same way as the rest of the API methods
        for search_item in results:
            item = {'id': int(search_item.doc_id.split(':')[1])}

            for field in search_item.fields:
                item[field.name] = field.value

            response['data'].append(__formatMediaOrStory(item, type='search_object'))

    else:
        response = {
            'error': 'Please pass a query to make a search!',
            'data': []
        }

    return HttpResponse(json.dumps(response), mimetype='application/json')
