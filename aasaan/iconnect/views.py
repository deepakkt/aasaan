from .forms import MessageForm, RecipientForm
from django.views.generic.edit import FormView, View
from django.shortcuts import render
from itertools import chain
from contacts.models import Contact, RoleGroup, IndividualRole, Center, Zone, IndividualContactRoleZone, \
    IndividualContactRoleCenter, ContactRoleGroup


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


class SummaryView(View):
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
        exclude_contacts = Contact.objects.filter(pk__in=exclude_contacts)
        context  = {'reason': request.POST.get('reason'), 'communication_type': request.POST.get('communication_type'),
                     'subject': request.POST.get('subject'), 'message': request.POST.get('message'),
                     'role_group': role_group, 'roles': roles, 'all_contacts': all_contacts}

        return render(request, 'iconnect/viewsummary.html', context)


class ConfirmSendView(FormView):
    def post(self, request, *args, **kwargs):
        return render(request, 'iconnect/confirm.html')
