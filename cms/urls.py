from django.conf.urls import patterns, url

from cms import views

urlpatterns = patterns('',
    # Authentication Routes
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'cms/auth/login.html'}, name='login'),
    url(r'^logout/$', views.logout, name='logout'),

    # Catch all route
    url(r'^$', views.index, name='index')
)