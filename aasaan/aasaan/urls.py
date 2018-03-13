import contacts.urls
import reports.urls
import misc.urls
import schedulemaster.urls
from ajax_select import urls as ajax_select_urls
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
import statistics.urls
from api.aasaan_api import ScheduleResource
from tastypie.api import Api


aasaan_v1_api = Api(api_name='v1')
aasaan_v1_api.register(ScheduleResource())

urlpatterns = patterns('',
    url(r'^aasaan_api/', include(aasaan_v1_api.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(admin.site.urls)),
    url(r'^contacts/', include(contacts.urls, namespace='contacts')),
    url(r'^reports/', include(reports.urls, namespace='reports')),
    url(r'^misc/', include(misc.urls, namespace='misc')),
    url(r'^markdown/', include('django_markdown.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^comm/', include('iconnect.urls')),
    url(r'^admin/lookups/', include(ajax_select_urls)),
    url(r'^admin/brochures/', include('brochures.urls', namespace='brochures')),
    url(r'^admin/ipcaccounts/', include('ipcaccounts.urls', namespace='ipcaccounts')),
	url(r'^statistics/', include(statistics.urls, namespace='statistics')),
    url(r'^schedules/', include(schedulemaster.urls, namespace='schedules')),
    url(r'^chaining/', include('smart_selects.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
)

if settings.ASYNC:
    urlpatterns += patterns('',
    url(r'^django-rq/', include('django_rq.urls')),
                            )

if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
                            (r'^media/(?P<path>.*)',
                            'serve',
                            {'document_root': settings.MEDIA_ROOT}),)

    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)