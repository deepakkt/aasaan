import contacts.urls
import travels.urls
import ipcaccounts.urls
import schedulemaster.urls
from django.contrib import admin
from django.urls import include, path
from django.conf.urls import url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contacts/', include(contacts.urls, namespace='contacts'), name='contacts'),
    path('ipcaccounts/', include(ipcaccounts.urls, namespace='ipcaccounts'), name='ipcaccounts'),
    path('schedules/', include(schedulemaster.urls, namespace='schedules'), name='schedules'),
    path('travels/', include(travels.urls, namespace='travels'), name='travels'),
    url('tinymce/', include('tinymce.urls')),
]