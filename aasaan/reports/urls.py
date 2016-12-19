from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
                       url(r'^irc-dashboard', views.IRCDashboard.as_view(), name='reports_irc_dashboard'),)