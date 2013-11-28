from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as logout_user
from django.core import serializers
from django.http import HttpResponse

from itertools import chain

from api.models import Media, Story, CustomGroup, CustomUser

# Render the CMS home page if the user is logged in
@login_required
def index(request):
    # Get counts of all the content types
    media_count = Media.objects.count()
    story_count = Story.objects.count()
    user_count = CustomUser.objects.count()
    group_count = CustomGroup.objects.count()

    return render(request, 'cms/index.html', {
        'title': 'Welcome, %s' % request.user.first_name,
        'media_count': media_count,
        'story_count': story_count,
        'user_count': user_count,
        'group_count': group_count,
    })

# Log out the user and redirect to them to /
def logout(request):
    # Logout the user
    logout_user(request)

    # Redirect them to the home page
    return redirect('/')

# Handles searching Media and Stories and returning as JSON
def search(request, query):
    # Search for the Media objects
    media = Media.objects.filter(title__icontains=query)

    # Search for the Story objects
    stories = Story.objects.filter(title__icontains=query)

    # Serialize the data as json
    data = serializers.serialize('json', list(chain(media, stories)))

    return HttpResponse(data, mimetype='application/json')
