from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wina.views.home', name='home'),
    # url(r'^wina/', include('wina.foo.urls')),

    # Django Admin
    url(r'^admin/', include(admin.site.urls)),
)
