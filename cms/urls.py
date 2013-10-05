from django.conf.urls import patterns, url

from cms import views

urlpatterns = patterns('',
	# Catch all route
    url(r'^$', views.index, name = 'index')
)