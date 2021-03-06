from django.conf.urls import patterns, url
from cms import views

urlpatterns = patterns('',
    # Media Routes
    url(r'^/media$', views.media, name='media-home'),
    url(r'^/media/view/(?P<id>\d+)$', views.media_view, name='media-view'),
    url(r'^/media/add$', views.media_add_or_edit, name='media-add'),
    url(r'^/media/edit/(?P<id>\d+)$', views.media_add_or_edit, name='media-edit'),
    url(r'^/media/delete/(?P<id>\d+)$', views.media_delete, name='media-delete'),
    url(r'^/media/search/tinymce$', views.media_search_tinymce, name='media-search-tinymce'),

    # Story Routes
    url(r'^/stories$', views.story, name='story-home'),
    url(r'^/story/view/(?P<id>\d+)$', views.story_view, name='story-view'),
    url(r'^/story/add$', views.story_add_or_edit, name='story-add'),
    url(r'^/story/edit/(?P<id>\d+)$', views.story_add_or_edit, name='story-edit'),
    url(r'^/story/delete/(?P<id>\d+)$', views.story_delete, name='story-delete'),

    # User Routes
    url(r'^/users$', views.user, name='user-home'),
    url(r'^/user/view/(?P<id>\d+)$', views.user_view, name='user-view'),
    url(r'^/user/add$', views.user_add_or_edit, name='user-add'),
    url(r'^/user/edit/(?P<id>\d+)$', views.user_add_or_edit, name='user-edit'),
    url(r'^/user/activate/(?P<id>\d+)$', views.user_activate, name='user-activate'),
    url(r'^/user/deactivate/(?P<id>\d+)$', views.user_deactivate, name='user-deactivate'),

    # Group Routes
    url(r'^/groups$', views.group, name='group-home'),
    url(r'^/group/view/(?P<id>\d+)$', views.group_view, name='group-view'),
    url(r'^/group/add$', views.group_add_or_edit, name='group-add'),
    url(r'^/group/edit/(?P<id>\d+)$', views.group_add_or_edit, name='group-edit'),
    url(r'^/group/delete/(?P<id>\d+)$', views.group_delete, name='group-delete'),

    # Catch all route
    url(r'^$', views.index, name='cms-home')
)