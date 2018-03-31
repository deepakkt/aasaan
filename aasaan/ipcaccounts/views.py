import json
from django.contrib.auth.decorators import login_required
from schedulemaster.models import ProgramSchedule, ProgramMaster
from django.http import JsonResponse
from django.utils import formats
from django.shortcuts import render
from django.views.generic.edit import FormView, View
from .forms import MessageForm
from .models import RCOAccountsMaster, VoucherDetails
from config.management.commands.notify_utils import dispatch_notification, setup_sendgrid_connection
from django.conf import settings
from config.models import Configuration

@login_required
def get_budget_code(request):
    if request.method == 'GET':
        program_id = request.GET['program_schedule']
        program_schedule = ProgramSchedule.objects.get(id=program_id)
        program_master = ProgramMaster.objects.get(name=program_schedule.program.name)
        cft = Configuration.objects.get(configuration_key='IPC_ACCOUNTS_TRACKING_CONST')
        data = json.loads(cft.configuration_value)
        prefix = data[program_schedule.center.zone.zone_name]['prefix']
        formatted_start_date = formats.date_format(program_schedule.start_date, "DATE_FORMAT")
        budget_code = prefix+'-'+program_schedule.center.center_name+'-'+program_master.abbreviation+ '-'+formatted_start_date
        return JsonResponse(budget_code, safe=False)

@login_required
def send_email(request):
    if request.method == 'GET':
        account_id = request.GET['account_id']
        account_master = RCOAccountsMaster.objects.get(id=account_id)
        if account_master.account_type.name == 'Class Accounts':
            zone = account_master.program_schedule.center.zone.zone_name
        else:
            zone = account_master.zone.zone_name
        cft = Configuration.objects.get(configuration_key='IPCACCOUNTS_EMAIL_NOTIFY')
        data = json.loads(cft.configuration_value)
        sender = request.user.email
        if account_master.account_type.name == 'Teacher Accounts':
            approvar = data[zone]['ta_approvar']
        else:
            approvar = data[zone]['ca_approvar']
        accounts_incharge = request.user.get_full_name()
        cc = data[zone]['cc']
        bcc = data[zone]['bcc']

        voucher_details = VoucherDetails.objects.filter(accounts_master=account_master)
        message_body = add_voucher_details(account_master, voucher_details)

        subject = ''
        if (len(voucher_details) > 2):
            subject = voucher_details[0].tracking_no + ' - ' + voucher_details[len(voucher_details) - 1].tracking_no
        elif (len(voucher_details) == 2):
            subject = voucher_details[0].tracking_no + ' & ' + voucher_details[len(voucher_details) - 1].tracking_no
        elif (len(voucher_details) == 1):
            subject = voucher_details[0].tracking_no

        subject = '('+subject + ') - Voucher Approval needed'

        message_body = message_body.replace('ACCOUNTS_INCHARGE', accounts_incharge)
        message_body = message_body.replace('ZONE_NAME', zone)
        form = MessageForm(
            initial={'sender':sender, 'to':approvar, 'cc':cc, 'bcc':bcc, 'subject': subject, 'message': message_body})
    return render(request, 'ipcaccounts/mailer.html', {'form': form})


class MessageView(FormView):
    def get(self, request, *args, **kwargs):
        form = MessageForm(
            initial={'reason': 'TESTING - IPC Communication system', 'subject': 'Test Message',
                     'communication_type': 'Email',
                     'message': 'Namaskaram, IPC Communication system test message. Pranam'})
        return render(request, 'ipcaccounts/mailer.html', {'form': form})


def add_voucher_details(account_master, voucher_details):

    message_body = Configuration.objects.get(configuration_key='IPCACCOUNTS_EMAIL_APPROVAL_TEMPLATE').configuration_value
    message_content = Configuration.objects.get(configuration_key='IPCACCOUNTS_EMAIL_CONTENT_TEMPLATE').configuration_value
    message_body_end = Configuration.objects.get(
        configuration_key='IPCACCOUNTS_EMAIL_CONTENT_END_TEMPLATE').configuration_value
    for v in voucher_details:
        table_row = str(message_content)
        table_row = table_row.replace('TRACKING_NO', v.tracking_no)
        table_row = table_row.replace('ENTITY', account_master.entity_name.name)
        voucher_date = formats.date_format(account_master.voucher_date, "DATE_FORMAT")
        table_row = table_row.replace('VOUCHER_DATE', voucher_date)
        table_row = table_row.replace('NAME_OF_VOUCHER', v.nature_of_voucher.name)
        table_row = table_row.replace('BUDGET_CODE', account_master.budget_code)
        table_row = table_row.replace('EXPENSES_DESC', v.expenses_description)
        table_row = table_row.replace('PARTY_NAME', v.party_name)
        table_row = table_row.replace('AMOUNT', str(v.amount))
        message_body = message_body+table_row
    message = message_body + message_body_end
    return message

class SendEmailView(FormView):
    def post(self, request, *args, **kwargs):
        msg_subject = request.POST.get('subject')
        message_body = request.POST.get('temp_message')
        sender = request.user.email
        to = get_email_list(request.POST.get('to'))
        cc = get_email_list(request.POST.get('cc'))
        bcc = get_email_list(request.POST.get('bcc'))

        sendgrid_contnection = setup_sendgrid_connection(settings.SENDGRID_KEY)
        _dispatch_status = dispatch_notification(sender, to, msg_subject,
                                                 message_body, sendgrid_contnection, cc, bcc)
        if _dispatch_status:
            return render(request, 'ipcaccounts/confirm.html')
        else:
            return render(request, 'ipcaccounts/error.html')

def get_email_list(_emails):
    if _emails.find(',') > 1:
        e_list = _emails.split(',')
    else:
        e_list = [_emails, ]
    return e_list