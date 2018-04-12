from django.conf.urls import patterns, url
from travels import views

urlpatterns = patterns('',
                       url(r'^compose_email', views.send_email, name='compose_email'),
                       url(r'^sendApprovalMessage', views.SendEmailView.as_view(), name='ipcaccounts')
                       )
