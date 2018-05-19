from django.shortcuts import render
from config.models import Configuration
import json
from notify.api.sendgrid_api import stage_classic_notification
from django.utils import formats
from django.conf import settings
from .models import TravelRequest, TravelNotes
from .forms import MessageForm
from datetime import date, timedelta
from django.views.generic import TemplateView
from braces.views import LoginRequiredMixin
from contacts.models import Contact,Zone, IndividualRole, IndividualContactRoleZone, IndividualContactRoleCenter
from django.http import JsonResponse, HttpResponse


class PassangerDetailsView(LoginRequiredMixin, TemplateView):
    def get(self, request):
        if request.method == 'GET':
            travel_id = request.GET['id']
            t_request = TravelRequest.objects.get(pk=travel_id)
            message_body = get_passanger_details_list(t_request)
            print()
            return HttpResponse(message_body)


def get_passanger_details_list(travel_request):
    traveller_details = list(travel_request.teacher.all())
    traveller_row = Configuration.objects.get(
        configuration_key='IPCTRAVELS_PASSANGER_LIST_TEMPLATE').configuration_value
    traveller_row = str(traveller_row)
    t_data = ''
    for index, tr in enumerate(traveller_details):
        t_row = traveller_row
        t_row = t_row.replace('#SNO#', str(index + 1))
        t_row = t_row.replace('NAME', tr._get_actual_name())
        age = 'Age not known'
        if tr.date_of_birth:
            age = (date.today() - tr.date_of_birth) // timedelta(days=365.2425)
        t_row = t_row.replace('GENDER_AGE', tr.get_gender_display() + ' - ' + str(age))
        t_row = t_row.replace('MOBILENO', tr.primary_mobile)
        t_data += t_row
    return '<table>' + t_data + '</table>'


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
        notes = TravelNotes.objects.filter(travel_request=travel_request)
        note = [x.note.split('created_by')[0] for x in notes]
        ticket_row = ticket_row.replace('REMARKS', '\n'.join(note))
        traveller_details = list(travel_request.teacher.all())
        traveller_details_start = Configuration.objects.get(
            configuration_key='IPCTRAVELS_EMAIL_TRAVELLER_START_TEMPLATE').configuration_value
        traveller_row = Configuration.objects.get(
            configuration_key='IPCTRAVELS_EMAIL_TRAVELLER_LIST_TEMPLATE').configuration_value
        traveller_row = str(traveller_row)
        t_data = ''
        for index, tr in enumerate(traveller_details):
            t_row = traveller_row
            t_row = t_row.replace('#SNO#', str(index+1))
            t_row = t_row.replace('NAME', tr._get_actual_name())
            age = 'Age not known'
            if tr.date_of_birth:
                age = (date.today() - tr.date_of_birth) // timedelta(days=365.2425)
            t_row = t_row.replace('GENDER_AGE', tr.get_gender_display() + ' - ' +str(age))
            t_row = t_row.replace('MOBILENO', tr.primary_mobile)
            t_data+=t_row

        traveller_details_end = Configuration.objects.get(
            configuration_key='IPCTRAVELS_EMAIL_TRAVELLER_END_TEMPLATE').configuration_value

        return ticket_row + traveller_details_start + t_data + traveller_details_end


class SendEmailView(LoginRequiredMixin, TemplateView):
    def post(self, request):
        msg_subject = request.POST.get('subject')
        message_body = request.POST.get('temp_message')
        sender = request.user.first_name + "|" + request.user.email
        to = get_email_list(request.POST.get('to'))
        cc = get_email_list(request.POST.get('cc'))
        bcc = get_email_list(request.POST.get('bcc'))

        stage_classic_notification("IPC Travels", sender, to, cc,
                                    msg_subject, message_body)
        _dispatch_status = True              
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


class PassengerListView(LoginRequiredMixin, TemplateView):
    template = "travels/passanger_list.html"
    template_name = "travels/passanger_list.html"
    login_url = "/admin/login/?next=/"

    def get(self, request):

        return render(request, self.template)


def passanger_refresh(request):
    teacher_role = IndividualRole.objects.get(role_name='Teacher', role_level='ZO')
    _teacher_list = Contact.objects.filter(individualcontactrolezone__role=teacher_role)
    summary = { }
    data = []
    for c in _teacher_list:
        icrz = IndividualContactRoleZone.objects.filter(contact=c)
        zone_list = list(set([x.zone.zone_name for x in icrz]))
        zone = str(zone_list).replace('[', '').replace(']','').replace("'", '')
        age = '-'
        if c.date_of_birth:
            age = (date.today() - c.date_of_birth) // timedelta(days=365.2425)

        data.append({'id':c.pk, 'name':c._get_actual_name(), 't_no':c.teacher_tno, 'category':c.get_category_display(),
                     'gender':c.get_gender_display(), 'age':age,
                      'primary_email':c.primary_email,'phone_number':c.primary_mobile,
                     'id_proof_type': c.get_id_proof_type_display(), 'id_proof_number': c.id_proof_number,
                     'zone':zone})
    summary['data'] = data
    return JsonResponse( summary , safe=False)
