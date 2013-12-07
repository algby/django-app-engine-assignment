from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from cms.helpers import can_access_cms
from api.models import Media, Story, WinaGroup, WinaUser

# Render the CMS home page if the user is logged in
@user_passes_test(can_access_cms)
def index(request):
    # Get counts of all the content types
    media_count = Media.objects.count()
    story_count = Story.objects.count()
    user_count = WinaUser.objects.count()
    group_count = WinaGroup.objects.count()

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
