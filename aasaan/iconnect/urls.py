from django.conf.urls import patterns, url
from iconnect import views

urlpatterns = patterns('',
                       url(r'^addMessage$', views.MessageView.as_view(), name='addMessage$'),
                       url(r'^addRecipient', views.RecipientView.as_view(), name='addRecipient'),
                       url(r'^viewSummary', views.SummaryView.as_view(), name='viewSummary'),
                       url(r'^sendMessage', views.ConfirmSendView.as_view(), name='sendMessage'),
                       )
