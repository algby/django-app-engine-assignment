from django.conf.urls import patterns, url
from api import views

urlpatterns = patterns('',
    # Media Routes
    url(r'^/media$', views.media, name='api-media'),
    url(r'^/media/(?P<id>\d+)$', views.media_lookup, name='api-media-lookup'),

    # Search routes
    url(r'^/search$', views.search, name='api-search'),

    # Catch all route
    url(r'^$', views.index, name = 'index')
)