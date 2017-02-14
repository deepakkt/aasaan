from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
                       url(r'^local-events', views.LocalEventsView.as_view(), name='misc_local_events'),
                       url(r'^admin-dashboard', views.AdminDashboardDispatch.as_view(), name='admin_dashboard'),)