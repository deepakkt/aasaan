from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
                       url(r'^list/([0-9]+)/$', views.display_single_schedule, name='display_single_schedule'),)