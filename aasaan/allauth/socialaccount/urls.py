from django.urls import include, path
from django.conf.urls import url
from . import views

app_name = 'socialaccount'
urlpatterns = [
    path('login/cancelled/', views.login_cancelled,
        name='socialaccount_login_cancelled'),
    path('login/error/', views.login_error,
        name='socialaccount_login_error'),
    path('signup/', views.signup, name='socialaccount_signup'),
    path('connections/', views.connections, name='socialaccount_connections')
]
