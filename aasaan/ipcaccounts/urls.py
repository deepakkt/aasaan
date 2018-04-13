from django.urls import include, path
from ipcaccounts import views
app_name = 'ipcaccounts'
urlpatterns = [path('get_budget_code', views.get_budget_code, name='get_budget_code'),
               path('compose_email', views.compose_email, name='compose_email'),
               path('sendApprovalMessage', views.SendEmailView.as_view(), name='ipcaccounts'),
               path('treasurer_report', views.TreasurerSummaryDashboard.as_view(), name='treasurer_report'),
               path('treasurer_refresh', views.treasurer_refresh, name='treasurer_refresh'),
               path('voucher_report', views.VoucherSummaryDashboard.as_view(), name='voucher_report'),
               path('voucher_refresh', views.voucher_refresh, name='voucher_refresh'),
               path('get_program_schedules', views.get_program_schedules, name='schedules_list')]
