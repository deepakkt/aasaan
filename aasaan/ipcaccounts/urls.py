from django.conf.urls import patterns, url
from ipcaccounts import views

urlpatterns = patterns('',
                       url(r'^get_budget_code', views.get_budget_code, name='budget_code'),
                       )
