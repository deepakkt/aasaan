from django.urls import path
from travels import views

app_name = 'travels'
urlpatterns = [
               path('compose_email', views.ComposeEmailView.as_view(), name='compose_email'),
               path('send_email', views.SendEmailView.as_view(), name='send_email'),
               path('passanger_list', views.PassengerListView.as_view(), name='passanger_list'),
               path('passanger_refresh', views.passanger_refresh, name='passanger_refresh'),
               path('get_passanger_details', views.PassangerDetailsView.as_view(), name='passanger_details'),
               path('ticket_list', views.TicketListView.as_view(), name='ticket_list'),
               path('ticketlist_refresh', views.ticketlist_refresh, name='ticketlist_refresh'),
             ]