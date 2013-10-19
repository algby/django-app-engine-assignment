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

    # Story Routes
    url(r'^/story$', views.story, name='story-home'),

    # User Routes
    url(r'^/user$', views.user, name='user-home'),

    # Catch all route
    url(r'^$', views.index, name='cms-home')
)