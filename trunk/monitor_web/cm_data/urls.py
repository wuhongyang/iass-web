'''
Created on 2014-10-10
@author: Chaser
'''
from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
import views

router = DefaultRouter()
router.register(r'departs', views.CMDepartViewSet)
router.register(r'users', views.CMUserViewSet)
router.register(r'hosts', views.CmHostViewset)
router.register(r'instance', views.CmInstanceViewset)
router.register(r'platform', views.CmPlatformViewset)
router.register(r'orders', views.CmWorkOrderViewset)
router.register(r'devices', views.CmDeviceViewset)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
)