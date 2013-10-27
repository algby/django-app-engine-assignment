from django.conf.urls import patterns, url

from frontend import views

urlpatterns = patterns('',
    # Used to server media from the blobstore in a development environment
    url(r'^blob/view/(?P<blob_key>.*)$', views.blob_view, name='blob-view'),

    # Catch all route
    url(r'^$', views.index, name='index')
)