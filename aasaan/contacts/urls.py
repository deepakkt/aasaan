from django.conf.urls import patterns, url
from contacts.views import ListContactView, ContactSummaryDashboard, s_refresh

urlpatterns = patterns('',
                       url(r'^list$', ListContactView.as_view(), name='list_contacts'),
                       url(r'^summary', ContactSummaryDashboard.as_view(), name='contact-summary'),
                       url(r'^s_refresh', s_refresh, name='s_refresh'),)