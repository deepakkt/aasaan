from django.shortcuts import render
from config.models import Configuration
import json
from config.management.commands.notify_utils import dispatch_notification, setup_sendgrid_connection
from django.utils import formats
from django.conf import settings
from .models import TravelRequest, Travellers
from ipcaccounts.forms import MessageForm
from datetime import date, timedelta
from django.views.generic import TemplateView
from braces.views import LoginRequiredMixin

class ComposeEmailView(LoginRequiredMixin, TemplateView):
    def get(self, request):
        if request.method == 'GET':
            request_id = request.GET['emailforid']
            if request_id.find(',') > 0:
                rd = request_id.split(',')
            else:
                rd = [request_id, ]
            t_request = TravelRequest.objects.filter(pk__in=rd)

            cft = Configuration.objects.get(configuration_key='IPCTRAVELS_EMAIL_NOTIFY')
            data = json.loads(cft.configuration_value)
            sender = request.user.email
            travels_incharge = request.user.get_full_name()
            cc = ''
            bcc = ''
            travel_agent = ''

            namaskaram = Configuration.objects.get(
                configuration_key='IPCTRAVELS_EMAIL_CONTENT_START_TEMPLATE').configuration_value
            ticket_details = Configuration.objects.get(
                configuration_key='IPCTRAVELS_EMAIL_TICKET_TEMPLATE').configuration_value
            pranam = Configuration.objects.get(
                configuration_key='IPCTRAVELS_EMAIL_CONTENT_END_TEMPLATE').configuration_value
            message_body = ''
            for t in t_request:
                ticket_request = add_travel_request_details(t, ticket_details)
                zone = t.zone.zone_name
                ticket_request = ticket_request.replace('TRAVELS_INCHARGE', travels_incharge)
                ticket_request = ticket_request.replace('ZONE_NAME', zone)
                travel_agent = data[zone]['travel_agent']
                message_body += ticket_request
            subject = 'Ticket booking request'
            pranam = pranam.replace('SENDER_SIGNATURE', travels_incharge)
            message_body = namaskaram + message_body + pranam
            form = MessageForm(
                initial={'sender':sender, 'to':travel_agent, 'cc':cc, 'bcc':bcc, 'subject': subject, 'message': message_body, 'account_id' : request_id})
            return render(request, 'travels/mailer.html', {'form': form})


def add_travel_request_details(travel_request, ticket_details):
        ticket_row = str(ticket_details)
        ticket_row = ticket_row.replace('TRACKING NO', 'TR'+ str(travel_request.id).zfill(6))
        ticket_row = ticket_row.replace('FROM', travel_request.source)
        ticket_row = ticket_row.replace('TO', travel_request.destination)
        onward_date = formats.date_format(travel_request.onward_date, "DATE_FORMAT")
        ticket_row = ticket_row.replace('DATEOFJOURNEY', onward_date)
        ticket_row = ticket_row.replace('TRAVELMODE', travel_request.get_travel_mode_display())
        ticket_row = ticket_row.replace('REMARKS', travel_request.remarks)

        traveller_details = Travellers.objects.filter(travel_request=travel_request)

        traveller_details_start = Configuration.objects.get(
            configuration_key='IPCTRAVELS_EMAIL_TRAVELLER_START_TEMPLATE').configuration_value
        traveller_row = Configuration.objects.get(
            configuration_key='IPCTRAVELS_EMAIL_TRAVELLER_LIST_TEMPLATE').configuration_value
        traveller_row = str(traveller_row)
        t_data = ''

        for index, tr in enumerate(traveller_details):
            t_row = traveller_row
            t_row = t_row.replace('#SNO#', str(index+1))
            t_row = t_row.replace('NAME', tr.teacher.full_name)
            age = 'Age not known'
            if tr.teacher.date_of_birth:
                age = (date.today() - tr.teacher.date_of_birth) // timedelta(days=365.2425)
            t_row = t_row.replace('GENDER_AGE', tr.teacher.get_gender_display() + ' - ' +str(age))
            t_row = t_row.replace('MOBILENO', tr.teacher.primary_mobile)
            # t_row = t_row.replace('IDCARD_TYPE', tr.teacher.id_proof_type)
            # t_row = t_row.replace('IDCARDNO', tr.teacher.id_proof_number)
            t_data+=t_row

        traveller_details_end = Configuration.objects.get(
            configuration_key='IPCTRAVELS_EMAIL_TRAVELLER_END_TEMPLATE').configuration_value

        return ticket_row + traveller_details_start + t_data + traveller_details_end


class SendEmailView(LoginRequiredMixin, TemplateView):
    def post(self, request):
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
            request_id = request.POST.get('account_id')
            if request_id.find(',') > 0:
                rd = request_id.split(',')
            else:
                rd = [request_id, ]
            t_request = TravelRequest.objects.filter(pk__in=rd)
            for t in t_request:
                t.email_sent = True
                t.save()
            return render(request, 'travels/confirm.html')
        else:
            return render(request, 'travels/error.html')


def get_email_list(_emails):
    if _emails.find(',') > 1:
        e_list = _emails.split(',')
    else:
        e_list = [_emails, ]
    return e_list