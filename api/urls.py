from django.conf.urls import patterns, url
from api import views

urlpatterns = patterns('',
    # Media routes
    url(r'^/media$', views.media, name='api-media'),
    url(r'^/media/(?P<id>\d+)$', views.media_lookup, name='api-media-lookup'),

    # Story routes
    url(r'^/story$', views.story, name='api-story'),
    url(r'^/story/(?P<id>\d+)$', views.story_lookup, name='api-story-lookup'),

    # Search routes
    url(r'^/search$', views.search, name='api-search'),

    # Catch all route
    url(r'^$', views.index, name = 'index')
)