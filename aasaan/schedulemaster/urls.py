from django.urls import include, path
from . import views

app_name = 'schedules'
urlpatterns = [path('list/([0-9]+)/', views.display_single_schedule, name='display_single_schedule'),]