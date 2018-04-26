from django.urls import path
from travels import views

app_name = 'travels'
urlpatterns = [
               path('compose_email', views.ComposeEmailView.as_view(), name='compose_email'),
               path('send_email', views.SendEmailView.as_view(), name='send_email'),
               path('passanger_list', views.PassengerListView.as_view(), name='passanger_list'),
               path('passanger_refresh', views.passanger_refresh, name='passanger_refresh')
             ]