from django.conf.urls import patterns, url
from ipctravels import views

urlpatterns = patterns('',
                       url(r'^viewSummary', views.SummaryView.as_view(), name='viewSummary'),
                       url(r'^viewReport', views.ReportView.as_view(), name='viewReport'),

                       )
