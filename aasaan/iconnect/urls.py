from django.conf.urls import patterns, url
from iconnect import views

urlpatterns = patterns('',
                       url(r'^comm$', views.CommunicationView.as_view(), name='mailer'),
                       url(r'^addRecipient', views.Form2View.as_view(), name='addRecipient'),
                       url(r'^viewSummary', views.Form3View.as_view(), name='viewSummary'),
                       url(r'^sendMessage', views.Form4View.as_view(), name='sendMessage'),
                       )
