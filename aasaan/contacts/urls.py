from contacts.views import ListContactView, ContactSummaryDashboard, s_refresh
from django.urls import include, path

app_name = 'contacts'
urlpatterns = [path('list', ListContactView.as_view(), name='list_contacts'),
                       path('summary', ContactSummaryDashboard.as_view(), name='contact-summary'),
                       path('s_refresh', s_refresh, name='s_refresh')]