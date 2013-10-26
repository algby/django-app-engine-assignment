from django.conf.urls import patterns, url

from cms import views

urlpatterns = patterns('',
    # Authentication Routes
    url(r'^/login$', 'django.contrib.auth.views.login', {'template_name': 'cms/auth/login.html'}, name='login'),
    url(r'^/logout$', views.logout, name='logout'),

    # Media Routes
    url(r'^/media$', views.media, name='media-home'),
    url(r'^/media/view/(?P<id>\d+)$', views.media_view, name='media-view'),
    url(r'^/media/add$', views.media_add_or_edit, name='media-add'),
    url(r'^/media/edit/(?P<id>\d+)$', views.media_add_or_edit, name='media-edit'),
    url(r'^/media/delete/(?P<id>\d+)$', views.media_delete, name='media-delete'),
    url(r'^/media/search/ajax/(?P<query>.*)$', views.media_search_ajax, name='media-search-ajax'),
    url(r'^/media/search/ui$', views.media_search_ui, name='media-search-ui'),

    # Story Routes
    url(r'^/story$', views.story, name='story-home'),
    url(r'^/story/view/(?P<id>\d+)$', views.story_view, name='story-view'),
    url(r'^/story/add$', views.story_add_or_edit, name='story-add'),
    url(r'^/story/edit/(?P<id>\d+)$', views.story_add_or_edit, name='story-edit'),
    url(r'^/story/delete/(?P<id>\d+)$', views.story_delete, name='story-delete'),

    # User Routes
    url(r'^/user$', views.user, name='user-home'),

    # Catch all route
    url(r'^$', views.index, name='cms-home')
)