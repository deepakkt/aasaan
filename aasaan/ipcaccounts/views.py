import json
from django.contrib.auth.decorators import login_required
from schedulemaster.models import ProgramSchedule, ProgramMaster
from django.utils import formats
from django.shortcuts import render
from django.views.generic.edit import FormView, View
from .forms import MessageForm
from .models import RCOAccountsMaster, VoucherDetails, Treasurer, AccountTypeMaster, NPVoucherStatusMaster, RCOVoucherStatusMaster
from config.management.commands.notify_utils import dispatch_notification, setup_sendgrid_connection
from django.conf import settings
from config.models import Configuration

from django.views.generic import TemplateView
from django.http import JsonResponse
from braces.views import LoginRequiredMixin
from .forms import FilterFieldsForm, VoucherAdvancedSearchFieldsForm
from contacts.models import Contact, Zone, IndividualRole, IndividualContactRoleZone, IndividualContactRoleCenter
from datetime import timedelta
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.conf import settings

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
        budget_code = prefix+'-'+program_schedule.center.center_name+'-'+program_master.abbreviation+ '-'+formatted_start_date + ' ('+program_id+')'
        return JsonResponse(budget_code, safe=False)


class ComposeEmailView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):

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
        if len(voucher_details) > 2:
            subject = voucher_details[0].tracking_no + ' - ' + voucher_details[len(voucher_details) - 1].tracking_no
        elif len(voucher_details) == 2:
            subject = voucher_details[0].tracking_no + ' & ' + voucher_details[len(voucher_details) - 1].tracking_no
        elif len(voucher_details) == 1:
            subject = voucher_details[0].tracking_no

        subject = '('+subject + ') - Voucher Approval needed'

        message_body = message_body.replace('ACCOUNTS_INCHARGE', accounts_incharge)
        message_body = message_body.replace('ZONE_NAME', zone)
        message_body = message_body.replace('SENDER_SIGNATURE', accounts_incharge)
        form = MessageForm(
            initial={'sender':sender, 'to':approvar, 'cc':cc, 'bcc':bcc, 'subject': subject, 'message': message_body, 'account_id' : account_id})
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
        message_body += table_row
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
        bcc.append(request.user.email)
        files = request.FILES.getlist('attachments')
        for f in files:
            fs = FileSystemStorage()
            fs.location = settings.MEDIA_ROOT+'/ipcaccounts/vouchers/email/'
            filename = fs.save(f.name, f)
            uploaded_file_url = fs.url(filename)


        sendgrid_contnection = setup_sendgrid_connection(settings.SENDGRID_KEY)
        _dispatch_status = dispatch_notification(sender, to, msg_subject,
                                                 message_body, sendgrid_contnection, cc, bcc)
        if _dispatch_status:
            account_id = request.POST.get('account_id')
            account_master = RCOAccountsMaster.objects.get(id=account_id)
            account_master.email_sent = True
            account_master.save()
            return render(request, 'ipcaccounts/confirm.html')
        else:
            return render(request, 'ipcaccounts/error.html')


def get_email_list(_emails):
    if _emails.find(',') > 1:
        e_list = _emails.split(',')
    else:
        e_list = [_emails, ]
    return e_list


class TreasurerSummaryDashboard(LoginRequiredMixin, TemplateView):
    template = "ipcaccounts/treasurer_adv_search.html"
    template_name = "ipcaccounts/treasurer_adv_search.html"
    login_url = "/admin/login/?next=/"

    def get(self, request):
        form = FilterFieldsForm()
        return render(request, self.template, {'form': form})


def treasurer_refresh(request):
    teacher_role = IndividualRole.objects.get(role_name='Center Treasurer', role_level='CE')
    _teacher_list = Contact.objects.filter(individualcontactrolecenter__role=teacher_role)
    summary = {}
    data = []
    for c in _teacher_list:
        icrz = IndividualContactRoleZone.objects.filter(contact=c)
        z_role_list = [x.role.role_name for x in icrz]
        z_zone_list = [x.zone.zone_name for x in icrz]
        icrc = IndividualContactRoleCenter.objects.filter(contact=c)
        c_role_list = [x.role.role_name for x in icrc]
        c_zone_list = [x.center.zone.zone_name for x in icrc]
        center_list = list(set([x.center.center_name for x in icrc]))
        role_list = list(set(z_role_list + c_role_list))
        zone_list = list(set(z_zone_list + c_zone_list))
        try:
            tr = Treasurer.objects.filter(new_treasurer=c)[:1]
        except Treasurer.DoesNotExist:
            tr = None
        account_holder = ''
        bank_name = ''
        branch_name = ''
        account_number = ''
        ifsc_code = ''
        if tr :
            account_holder = tr[0].account_holder
            bank_name = tr[0].bank_name
            branch_name = tr[0].branch_name
            account_number = tr[0].account_number
            ifsc_code = tr[0].ifsc_code

        data.append(
            {'id': c.pk, 'name': c.full_name, 'phone_number': c.primary_mobile, 'primary_email': c.primary_email,
             'account_holder': account_holder, 'bank_name': bank_name, 'branch_name': branch_name, 'account_number': account_number,'ifsc_code': ifsc_code,
             'zone': zone_list, 'center': center_list, 'roles': role_list})
        summary['data'] = data
    return JsonResponse(summary, safe=False)


class VoucherSummaryDashboard(LoginRequiredMixin, TemplateView):
    template = "ipcaccounts/voucher_adv_search.html"
    template_name = "ipcaccounts/voucher_adv_search.html"
    login_url = "/admin/login/?next=/"

    def get(self, request):
        form = VoucherAdvancedSearchFieldsForm()
        return render(request, self.template, {'form': form})


def voucher_refresh(request):
    summary = {}
    data = []
    zone = request.GET['zone']
    account_type = request.GET['account_type']
    # np_voucher_status = request.GET['np_voucher_status']
    rco_voucher_status = request.GET['rco_voucher_status']

    if account_type and account_type.find(',') > 0:
        account_type = account_type.split(',')
        account_type = list(AccountTypeMaster.objects.filter(pk__in=account_type))
    elif account_type != 'null':
        account_type = [account_type, ]
        account_type = list(AccountTypeMaster.objects.filter(pk__in=account_type))
    else:
        account_type = list(AccountTypeMaster.objects.all())

    if rco_voucher_status.find(',') > 0:
        rco_voucher_status = rco_voucher_status.split(',')
    elif rco_voucher_status!= 'null':
        rco_voucher_status = [rco_voucher_status, ]
        rco_voucher_status = list(RCOVoucherStatusMaster.objects.filter(pk__in=rco_voucher_status))
    else:
        rco_voucher_status = list(RCOVoucherStatusMaster.objects.all())

    # if np_voucher_status.find(',') > 0:
    #     np_voucher_status = np_voucher_status.split(',')
    #     np_voucher_status = list(NPVoucherStatusMaster.objects.filter(pk__in=np_voucher_status))
    # elif np_voucher_status != 'null':
    #     np_voucher_status = [np_voucher_status, ]
    #     np_voucher_status = list(NPVoucherStatusMaster.objects.filter(pk__in=np_voucher_status))
    # else:
    #     np_voucher_status = list(NPVoucherStatusMaster.objects.all())

    if request.user.is_superuser and zone != 'null':
        if zone.find(',') > 0:
            zs = zone.split(',')
        else:
            zs = [zone, ]
        z = list(Zone.objects.filter(pk__in=zs))

        vd = VoucherDetails.objects.filter(accounts_master__zone__in=z, accounts_master__account_type__in=account_type,
                                           accounts_master__rco_voucher_status__in=rco_voucher_status)
    elif request.user.is_superuser and zone == 'null':
        vd = VoucherDetails.objects.filter(accounts_master__account_type__in=account_type,
                                           accounts_master__rco_voucher_status__in=rco_voucher_status)
    elif request.user.is_superuser is not True:
        user_zones = [x.zone for x in request.user.aasaanuserzone_set.all()]
        vd = VoucherDetails.objects.filter(accounts_master__zone__in=user_zones, accounts_master__account_type__in=account_type,
                                           accounts_master__rco_voucher_status__in=rco_voucher_status)
    for v in vd:
        am = v.accounts_master
        data.append(
            {'id': am.pk, 'tracking_no': v.tracking_no, 'voucher_type': v.get_voucher_type_display() if v.voucher_type else '', 'nature_of_voucher': v.nature_of_voucher.name, 'head_of_expenses': v.head_of_expenses.name if v.head_of_expenses else '', 'party_name': v.party_name,
             'amount': v.amount, 'utr_no': v.utr_no, 'budget_code': am.budget_code, 'rco_voucher_status': am.rco_voucher_status.name, 'entity_name': am.entity_name.name,'account_type': am.account_type.name,
             'np_voucher_status': am.np_voucher_status.name if am.np_voucher_status else '', 'zone': am.zone.zone_name})
        summary['data'] = data
    if not vd:
        data.append(
            {'id': '', 'tracking_no': '',
             'voucher_type': '', 'nature_of_voucher': '',
             'head_of_expenses': '', 'party_name': '',
             'amount': '', 'utr_no':'', 'budget_code': '', 'rco_voucher_status': '',
             'entity_name': '', 'account_type': '',
             'np_voucher_status': '', 'zone': ''})
        summary['data'] = data
    return JsonResponse(summary, safe=False)

@login_required
def get_program_schedules(request):
    if request.method == 'GET':
        zone_id = request.GET['zone']
        program_type = request.GET['program_type']
    pt = ProgramMaster.objects.get(pk=program_type)
    zone = Zone.objects.get(pk=zone_id)
    obj_id = request.META['PATH_INFO'].rstrip('/').split('/')[-2]
    schedule_days_to_show = Configuration.objects.get(
        configuration_key='IPC_ACCOUNTS_SCHEDULE_DAYS').configuration_value
    time_threshold = timezone.now() - timedelta(days=int(schedule_days_to_show))
    qs = ProgramSchedule.objects.filter(center__zone=zone, program=pt, end_date__gte=time_threshold)
    if obj_id.isdigit():
        am = RCOAccountsMaster.objects.get(pk=obj_id)
        if am.program_schedule:
            qs = qs | ProgramSchedule.objects.filter(pk=am.program_schedule.pk)
    ps_list = [(x.id, str(x)) for x in qs]
    return JsonResponse(ps_list, safe=False)