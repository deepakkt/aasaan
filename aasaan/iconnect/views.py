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
            initial={'reason': 'TO Organizer abt MSR', 'subject': 'Seating Pass', 'communication_type': 'Email',
                     'message': 'Seating Pass Over'})
        return render(request, 'iconnect/mailer.html', {'form': form})


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
        center_contacts = Contact.objects.filter(individualcontactrolecenter__center__in=center)
        if roles:
            if zone:
                zone_contacts = zone_contacts.filter(individualcontactrolezone__role__in=roles)
            if center:
                center_contacts = center_contacts.filter(individualcontactrolecenter__role__in=roles)
        role_group = [int(x) for x in request.POST.get('role_group').split('|') if x]
        rolegroup_contacts = Contact.objects.filter(contactrolegroup__role__in=role_group)
        all_contacts = zone_contacts | center_contacts | rolegroup_contacts
        all_contacts = all_contacts.distinct()
        exclude_contacts = [int(x) for x in request.POST.get('contacts').split('|') if x]
        all_contacts = all_contacts.exclude(pk__in=exclude_contacts)

        communication_type = request.POST.get('communication_type')
        if communication_type == 'EMail':
            recipients = all_contacts.values_list('primary_email', flat=True)
        elif communication_type == 'SMS':
            recipients = all_contacts.values_list('cug_mobile', flat=True)

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
        contact_details = all_contacts.values_list('first_name', flat=True).order_by('first_name')
        form = SummaryForm(
            initial={'reason': request.POST.get('reason'), 'communication_type': request.POST.get('communication_type'),
                     'subject': request.POST.get('subject'), 'message': request.POST.get('message'),
                     'contacts': contact_details, 'communication_hash': communication_hash})
        return render(request, 'iconnect/viewsummary.html', {'form': form})


class ConfirmSendView(FormView):
    def post(self, request, *args, **kwargs):
        communication_hash = request.POST.get('communication_hash')
        send_communication(communication_hash)
        return render(request, 'iconnect/confirm.html')
