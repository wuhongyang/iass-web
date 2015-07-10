from django.conf.urls import patterns, include, url
from rest_framework import routers

#from django.contrib import admin
#admin.autodiscover()


urlpatterns = patterns('',
#    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('rrdapi.urls')),
#    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)

