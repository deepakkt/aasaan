from django.conf.urls import patterns, url
from ipcaccounts import views

urlpatterns = patterns('',
                       url(r'^get_budget_code', views.get_budget_code, name='get_budget_code'),
                       url(r'^send_email', views.send_email, name='send_email'),
                       url(r'^sendApprovalMessage', views.SendEmailView.as_view(), name='ipcaccounts'),
                       )
