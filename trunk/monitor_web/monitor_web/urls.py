from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import patterns, include, url

# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'monitor_web.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^alarm/', include('cm_alarm.urls',namespace ="cm_alarm")),
    url(r'^data/', include('cm_data.urls',namespace ="cm_data")),
    url(r'^vmware/', include('cm_vmware.urls', namespace="cm_vmware"))
    # url(r'^admin/', include(admin.site.urls)),
)
urlpatterns += staticfiles_urlpatterns()
