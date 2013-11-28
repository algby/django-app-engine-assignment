from django.http import HttpResponse
from django.utils.dateformat import format

import json

from api.models import Media

def index(request):
    return HttpResponse(json.dumps({'message': 'Welcome to the WINA API!'}), mimetype='application/json')

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
        response['data'].append({
            'id': object.id,
            'title': object.title,
            'type': object.type,
            'content': object.content,
            'author': {
                'id': object.author_id,
                'username': object.author.username,
                'first_name': object.author.first_name,
                'last_name': object.author.last_name,
            },
            'date_created': int(format(object.date_created, 'U')),
        })

    # Return the response as json
    return HttpResponse(json.dumps(response), mimetype='application/json')
