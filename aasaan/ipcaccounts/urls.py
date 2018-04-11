from django.conf.urls import patterns, url
from ipcaccounts import views

urlpatterns = patterns('',
                       url(r'^get_budget_code', views.get_budget_code, name='get_budget_code'),
                       url(r'^compose_email', views.compose_email, name='compose_email'),
                       url(r'^sendApprovalMessage', views.SendEmailView.as_view(), name='ipcaccounts'),
                       url(r'^treasurer_report', views.TreasurerSummaryDashboard.as_view(), name='treasurer_report'),
                       url(r'^treasurer_refresh', views.treasurer_refresh, name='treasurer_refresh'),
                       url(r'^voucher_report', views.VoucherSummaryDashboard.as_view(), name='voucher_report'),
                       url(r'^voucher_refresh', views.voucher_refresh, name='voucher_refresh'),
                       url(r'^get_program_schedules', views.get_program_schedules, name='schedules_list'),
                       )
