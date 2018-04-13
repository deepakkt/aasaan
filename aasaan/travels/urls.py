from django.urls import include, path
from travels import views

app_name = 'travels'
urlpatterns = [path('compose_email', views.send_email, name='compose_email'),
               path('send_email', views.SendEmailView.as_view(), name='send_email'),
             ]