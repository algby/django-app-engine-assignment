from django.conf.urls import patterns, url

from cms import views

urlpatterns = patterns('',
    # Authentication Routes
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'cms/auth/login.html'}, name='login'),
    url(r'^logout/$', views.logout, name='logout'),

    # Media Routes
    url(r'^media/$', views.media, name='media-home'),

    # Story Routes
    url(r'^story/$', views.story, name='story-home'),

    # User Routes
    url(r'^user/$', views.user, name='user-home'),

    # Catch all route
    url(r'^$', views.index, name='cms-home')
)