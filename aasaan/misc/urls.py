from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
                       url(r'^local-events', views.LocalEventsView.as_view(), name='misc_local_events'),)