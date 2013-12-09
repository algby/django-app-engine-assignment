from django.http import HttpResponse
from django.utils.dateformat import format
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from google.appengine.api import search as gsearch
from modules.django_gcs_get_serving_url import get_serving_url
from api.models import Story, StoryForm, Media, MediaForm, WinaUser
import json

# Default view
def index(request):
    return HttpResponse(json.dumps({'message': 'Welcome to the WINA API!'}), mimetype='application/json')

# Helper to authenticate api users based on http headers
def __authenticate_user(request):
        username = request.META.get('HTTP_X_WINA_USERNAME', None)
        password = request.META.get('HTTP_X_WINA_PASSWORD', None)
        user = authenticate(username=username, password=password)

        # Check that the user exists
        if user is not None:
            # Check that their account is still valid
            if user.is_active:
                return user

            else:
                raise Exception('Your account has been disabled')

        else:
            raise Exception('Your username and/or password were incorrect')

# Slightly messy method that abstracts away the differences between search and db objects
def __formatMediaOrStory(object, type='db_object'):
    # Append the doc type for db objects as it isn't stored natively
    if type == 'db_object':
        # Patch the story object to include the type attr
        if isinstance(object, Story):
            object.type = 'story'

        object.doc_type = 'media' if object.type in ['image', 'audio', 'video'] else 'story'

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
        'slug': object['slug'] if type == 'search_object' else object.slug,
    }

# Return all media as json when a GET request is issued or when POST try and process an upload
@csrf_exempt
def media(request):
    # Set up a dict to return
    response = {
        'error': None,
        'data': [],
    }

    # Is media being uploaded?
    if request.method == 'POST':
        try:
            # Authenticate the api user
            user = __authenticate_user(request)

            # Check the user has sufficient permissions to add media
            if user.has_perm('api.wina_add_media'):
                media_form = MediaForm(request.POST, request.FILES)

                # Check that the request passes validation
                if media_form.is_valid():
                    # Save the form data to the db
                    media_form = media_form.save(commit=False)
                    media_form.author = WinaUser.objects.get(id=user.id)

                    # Is audio/video/image being submitted? If so we need to override content with the uploaded file url
                    if media_form.type in ['audio', 'video', 'image']:
                        media_form.content = get_serving_url(blob_key=request.FILES['file'].blob_key, file_name=request.FILES['file'].name)

                    media_form.save()

                    # And finally append the newly created media object to the return response
                    response['data'].append(__formatMediaOrStory(media_form))

                else:
                    raise Exception('Invalid request')

            else:
                raise Exception('You do not have sufficient permisisons to do that')

        except Exception as e:
            response['message'] = str(e)

    # Else assume it's a GET method and get all media
    else:
        # Get all the media objects
        media = Media.objects.all()

        # Append all the media objects to the response object
        for object in media:
            response['data'].append(__formatMediaOrStory(object))

    # Return the response as json
    return HttpResponse(json.dumps(response), mimetype='application/json')

# Return all stories as json
def story(request):
    # Set up a dict to return
    response = {
        'error': None,
        'data': [],
    }

    # Get all the story objects
    story = Story.objects.filter(status='published')

    # Append all the story objects to the response object
    for object in story:
        response['data'].append(__formatMediaOrStory(object))

    # Return the response as json
    return HttpResponse(json.dumps(response), mimetype='application/json')

# Look up an individual piece of media
def media_lookup(request, id):
    # Get the media object
    media = Media.objects.get(id=id)

    # Set up a dict to return
    response = {
        'error': None,
        'data': [__formatMediaOrStory(media)],
    }

    # Return the response as json
    return HttpResponse(json.dumps(response), mimetype='application/json')

# Look up an individual story
def story_lookup(request, id):
    # Get the story object, only allow retrieval of published stories as this is a public api
    story = Story.objects.get(id=id, status='published')

    # Set up a dict to return
    response = {
        'error': None,
        'data': [__formatMediaOrStory(story)],
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
