from .forms import MessageForm, RecipientForm, SummaryForm
from django.views.generic.edit import FormView, View
from django.shortcuts import render
from communication.api import send_communication
from contacts.models import Contact, RoleGroup, IndividualRole, Center, Zone, IndividualContactRoleZone, \
    IndividualContactRoleCenter, ContactRoleGroup
from communication.models import Payload, PayloadDetail


class MessageView(FormView):
    def get(self, request, *args, **kwargs):
        form = MessageForm(
            initial={'reason': 'TESTING - IPC Communication system', 'subject': 'Test Message',
                     'communication_type': 'Email',
                     'message': 'Namaskaram, IPC Communication system test message. Pranam'})
        return render(request, 'iconnect/travel_report.html', {'form': form})


class RecipientView(FormView):
    def post(self, request, *args, **kwargs):
        form = RecipientForm(
            initial={'reason': request.POST.get('reason'), 'communication_type': request.POST.get('communication_type'),
                     'subject': request.POST.get('subject'), 'message': request.POST.get('message')})
        return render(request, 'iconnect/recipients.html', {'form': form})


class SummaryView(FormView):
    def post(self, request, *args, **kwargs):

        roles = [int(x) for x in request.POST.get('roles').split('|') if x]
        center = [int(x) for x in request.POST.get('center').split('|') if x]
        zone = [int(x) for x in request.POST.get('zone').split('|') if x]
        zone_contacts = Contact.objects.filter(individualcontactrolezone__zone__in=zone)
        center_zonal_contacts = Contact.objects.filter(individualcontactrolecenter__center__zone__in=zone)
        center_contacts = Contact.objects.filter(individualcontactrolecenter__center__in=center)
        if roles:
            if zone:
                zone_contacts = zone_contacts.filter(individualcontactrolezone__role__in=roles)
                center_zonal_contacts = center_zonal_contacts.filter(individualcontactrolecenter__role__in=roles)
            if center:
                center_contacts = center_contacts.filter(individualcontactrolecenter__role__in=roles)
        role_group = [int(x) for x in request.POST.get('role_group').split('|') if x]
        rolegroup_contacts = Contact.objects.filter(contactrolegroup__role__in=role_group)
        all_contacts = zone_contacts | center_contacts | rolegroup_contacts | center_zonal_contacts
        all_contacts = all_contacts.distinct()
        exclude_contacts = [int(x) for x in request.POST.get('contacts').split('|') if x]
        all_contacts = all_contacts.exclude(pk__in=exclude_contacts)

        communication_type = request.POST.get('communication_type')
        if communication_type == 'EMail':
            recipients = ['%s' % (x.primary_email if x.primary_email else x.secondary_email) for x in all_contacts]
            contact_details = [
                '%s %s <%s>' % (x.first_name, x.last_name, x.primary_email if x.primary_email else x.secondary_email)
                for x in all_contacts]
        elif communication_type == 'SMS':
            recipients = ['%s' % (x.cug_mobile if x.cug_mobile else x.other_mobile_1) for x in all_contacts]
            contact_details = [
                '%s %s (%s)' % (x.first_name, x.last_name, x.cug_mobile if x.cug_mobile else x.other_mobile_1) for x in
                all_contacts]

        payload = Payload()
        payload.communication_title = request.POST.get('subject')
        payload.communication_type = communication_type
        payload.communication_notes = request.POST.get('reason')
        payload.communication_message = request.POST.get('message')
        payload.save()
        for recipient in recipients:
            payload_detail = PayloadDetail()
            payload_detail.communication = payload
            payload_detail.communication_recipient = recipient
            payload_detail.save()
        communication_hash = payload.communication_hash

        form = SummaryForm(
            initial={'reason': request.POST.get('reason'), 'communication_type': request.POST.get('communication_type'),
                     'subject': request.POST.get('subject'), 'message': request.POST.get('message'),
                     'contacts': contact_details, 'communication_hash': communication_hash})
        return render(request, 'iconnect/viewsummary.html', {'form': form,
                                                             'contact_list': contact_details})


class ConfirmSendView(FormView):
    def post(self, request, *args, **kwargs):
        status = send_communication(communication_type=request.POST.get('communication_type'),
                                    message_key=request.POST.get('communication_hash'))
        if (status == 'Complete'):
            return render(request, 'iconnect/confirm.html')

        return render(request, 'iconnect/travel_report.html', {'form': MessageForm(
            initial={'reason': 'TEST - ', 'subject': 'Test Message', 'communication_type': 'Email',
                     'message': 'Namaskaram, Testing IPC Communication system. Pranam'})})
