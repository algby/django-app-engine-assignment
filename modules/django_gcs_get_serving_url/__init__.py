import os
from django.core.urlresolvers import reverse

def get_serving_url(blob_key=None, file_name=None, development_route='blob-view', bucket_name='wina-assignment-media'):
    # What environment are we in, Is it production?
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        return 'https://storage.cloud.google.com/' + bucket_name + '/' + file_name

    # Is it development?
    elif os.getenv('SERVER_SOFTWARE', '').startswith('Development/'):
        # Grab the blob key route and append the blob key
        return reverse(development_route, kwargs={'blob_key': blob_key})

    # Well, where the hell are we then??
    else:
        raise Exception('Unable to determine environment from SERVER_SOFTWARE = ' + os.getenv('SERVER_SOFTWARE', ''))
