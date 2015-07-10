from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from rrdapi import views

urlpatterns = patterns('',
   # url(r'^rrddata/$', 'rrddata_detail'),
    url(r'^rrddata/$', views.RRDDataDetail.as_view()),
)

urlpatterns = format_suffix_patterns(urlpatterns)
