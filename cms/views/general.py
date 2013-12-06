from django.shortcuts import redirect, render
from django.contrib.auth import logout as logout_user
from django.contrib.auth.decorators import user_passes_test
from cms.helpers import can_access_cms
from api.models import Media, Story, CustomGroup, CustomUser

# Render the CMS home page if the user is logged in
@user_passes_test(can_access_cms)
def index(request):
    # Get counts of all the content types
    media_count = Media.objects.count()
    story_count = Story.objects.count()
    user_count = CustomUser.objects.count()
    group_count = CustomGroup.objects.count()

    # Get the count for story statuses
    published_count = Story.objects.filter(status='published').count()
    draft_count = Story.objects.filter(status='draft').count()

    return render(request, 'cms/index.html', {
        'title': 'Welcome, %s' % request.user.first_name,
        'media_count': media_count,
        'story_count': story_count,
        'user_count': user_count,
        'group_count': group_count,
        'published_count': published_count,
        'draft_count': draft_count,
    })

# Log out the user and redirect to them to /
@user_passes_test(can_access_cms)
def logout(request):
    # Logout the user
    logout_user(request)

    # Redirect them to the home page
    return redirect('/')
