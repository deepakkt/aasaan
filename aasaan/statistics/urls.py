from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
                       url(r'^statistics-dashboard', views.StatisticsDashboard.as_view(), name='statistics_dashboard'),
                       url(r'^ajax_refresh', views.ajax_refresh, name='ajax_refresh'),
                       )