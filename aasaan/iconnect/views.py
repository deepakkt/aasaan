from .forms import MessageForm, RecipientForm, SummaryForm
from django.views.generic.edit import FormView, View
from django.shortcuts import render
from contacts.models import Contact, RoleGroup, IndividualRole, Center, Zone, IndividualContactRoleZone, \
    IndividualContactRoleCenter, ContactRoleGroup


class MessageView(FormView):
    def get(self, request, *args, **kwargs):
        form = MessageForm(
            initial={'reason': 'TO Organizer abt MSR', 'subject': 'Seating Pass', 'communication_type': '1',
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

        zone = [int(x) for x in request.POST.get('zone').split('|') if x]
        zcontacts = [x.contact for x in
                     IndividualContactRoleZone.objects.filter(zone__in=Zone.objects.filter(pk__in=zone))]

        center = [int(x) for x in request.POST.get('center').split('|') if x]
        ccontacts = [x.contact for x in
                     IndividualContactRoleCenter.objects.filter(center__in=Center.objects.filter(pk__in=center))]
        print(ccontacts)

        role_group = [int(x) for x in request.POST.get('role_group').split('|') if x]
        print(role_group)
        rcontacts = [x.contact for x in
                     ContactRoleGroup.objects.filter(pk__in=role_group)]
        print(rcontacts)

        roles = request.POST.get('roles')
        roles = [int(x) for x in roles.split('|') if x]
        rolesobj = [IndividualRole.objects.get(pk=x) for x in roles]
        for i in rolesobj:
            print(i.role_name)

        contacts = request.POST.get('contacts')
        contacts = [int(x) for x in contacts.split('|') if x]
        contactobjs = [Contact.objects.get(pk=x) for x in contacts]
        for i in contactobjs:
            print(i.first_name + ' ' + i.primary_email)

        form = SummaryForm(
            initial={'reason': request.POST.get('reason'), 'communication_type': request.POST.get('communication_type'),
                     'subject': request.POST.get('subject'), 'message': request.POST.get('message'),
                     'role_group': role_group, 'roles': roles, 'contacts': contacts})
        return render(request, 'iconnect/viewsummary.html', {'form': form})


class ConfirmSendView(FormView):
    def post(self, request, *args, **kwargs):
        return render(request, 'iconnect/confirm.html')
