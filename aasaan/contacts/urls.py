from django.conf.urls import patterns, url
from contacts import views

urlpatterns = patterns('',
                       url(r'^list$', views.ListContactView.as_view(), name='list_contacts'),)