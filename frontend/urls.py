from django.conf.urls import patterns, url

from frontend import views

urlpatterns = patterns('',
    # Used to serve media from the blobstore in a development environment
    url(r'^blob/view/(?P<blob_key>.*)$', views.blob_view, name='blob-view'),

    # View a story
    url(r'^story/(?P<slug>.*)/(?P<id>\d+)$', views.story_view, name='story-view'),

    # Vote on a story
    url(r'^vote$', views.vote, name='story-vote'),

    # Public user sign up
    url(r'^join$', views.join, name='join'),

    # User login
    url(r'^login$', 'django.contrib.auth.views.login', {'template_name': 'frontend/login.html'}, name='login'),
    url(r'^logout$', views.logout, name='logout'),

    # Public user submission
    url(r'^submit$', views.submit, name='submit'),

    # Latest stories
    url(r'^latest$', views.latest, name='latest'),

    # Search
    url(r'^search$', views.search, name='search'),

    # Home Page
    url(r'^$', views.index, name='index')
)
