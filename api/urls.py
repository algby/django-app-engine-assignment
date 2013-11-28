from django.conf.urls import patterns, url

from api import views

urlpatterns = patterns('',
	# Media Routes
    url(r'^/media$', views.media, name='api-media'),

    # Catch all route
    url(r'^$', views.index, name = 'index')
)