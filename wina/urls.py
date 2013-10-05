from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	# Include the routes for the cms module
	url(r'^cms/', include('cms.urls')),
)
