from .forms import MessageForm, RecipientForm, SummaryForm
from django.views.generic.edit import FormView, View
from django.shortcuts import render
from contacts.models import Contact, RoleGroup, IndividualRole


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

        role_group = request.POST.get('role_group')
        role_group = [int(x) for x in role_group.split('|') if x]
        rgobjs = [RoleGroup.objects.get(pk=x) for x in role_group]
        for i in rgobjs:
            print(i.role_name)

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
