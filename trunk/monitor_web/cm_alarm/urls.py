'''
Created on 2014-9-23

@author: Administrator
'''
from django.conf.urls import patterns, url,include
from cm_alarm import group_user_views, project_rule_views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'historys', project_rule_views.AlarmHistoryViewset)

urlpatterns = patterns('',
                       url(r'^', include(router.urls)),
                       url(r'^group/(?P<group_id>\d+)/$', group_user_views.GroupUserMappingDetail.as_view(),
                           name='group'),
                       url(r'^groups/$', group_user_views.GroupUserMappingList.as_view(), name='groups'),
                       url(r'^groups/count/$', group_user_views.GroupCountView.as_view(), name='groups_count'),
                       url(r'^users/$', group_user_views.UserList.as_view(), name='users'),
                       url(r'^user/(?P<user_id>\d+)/$', group_user_views.UserDetail.as_view(), name='user'),
                       url(r'^users/count/$', group_user_views.UserCountView.as_view(), name='users_count'),

                       url(r'^objects/$', project_rule_views.MappingsList.as_view(), name='objects'),
                       url(r'^metrics/$', project_rule_views.MetricsList.as_view(), name='metrics'),
                       url(r'^projects/$', project_rule_views.ProjectsList.as_view(), name='projects'),
                       url(r'^project/(?P<project_id>\d+)/$', project_rule_views.ProjectDetail.as_view(), name='project'),
                       url(r'^projects/count/$', project_rule_views.ProjectCountView.as_view(), name='projects_count'),
                       url(r'^all/count/$', project_rule_views.allCountView.as_view(), name='all_count'),
                       url(r'^rule/(?P<rule_id>\d+)/$', project_rule_views.RuleDetail.as_view(), name='rule'),
)