# encoding: utf-8
'''
Created on 2014年10月11日

@author: mhjlq1989@gmail.com
'''
from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
import views

router = DefaultRouter()
router.register(r'host', views.VMwareHostViewSet)
router.register(r'instance', views.VMwareInstanceViewSet)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
)