from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Include the routes for the api module
    url(r'^api/', include('api.urls')),

    # Include the routes for the cms module
    url(r'^cms/', include('cms.urls')),

    # Include the routes for the site frontend
    url(r'^$', include('frontend.urls')),
)
