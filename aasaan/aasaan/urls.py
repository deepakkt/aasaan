import contacts.urls
import travels.urls
import ipcaccounts.urls
import schedulemaster.urls
from django.contrib import admin
from django.urls import include, path
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from api.aasaan_api import ScheduleResource
from tastypie.api import Api
from django.shortcuts import redirect

aasaan_v1_api = Api(api_name='v1')
aasaan_v1_api.register(ScheduleResource())

urlpatterns = [
    path('', lambda _: redirect('admin:index'), name="index"),
    path('admin/', admin.site.urls),
    path('aasaan_api/', include(aasaan_v1_api.urls)),
    path('contacts/', include(contacts.urls, namespace='contacts'), name='contacts'),
    path('admin/ipcaccounts/', include(ipcaccounts.urls, namespace='ipcaccounts'), name='ipcaccounts'),
    path('schedules/', include(schedulemaster.urls, namespace='schedules'), name='schedules'),
    path('admin/travels/', include(travels.urls, namespace='travels'), name='travels'),
    url('tinymce/', include('tinymce.urls')),
    url('accounts/', include('allauth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.ASYNC:
    urlpatterns += [url('django-rq/', include('django_rq.urls'))]

