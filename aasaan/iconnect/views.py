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

        rgitem = request.POST.get('include_role_group')
        rgitem = [int(x) for x in rgitem.split('|') if x]
        myobjs = [RoleGroup.objects.get(pk=x) for x in rgitem]
        for i in myobjs:
            print(i.role_name)

        iritem = request.POST.get('include_contact_group')
        iritem = [int(x) for x in iritem.split('|') if x]
        myobjs = [IndividualRole.objects.get(pk=x) for x in iritem]
        for i in myobjs:
            print(i.role_name)

        ecitem = request.POST.get('exclude_contacts')
        ecitem = [int(x) for x in ecitem.split('|') if x]
        myobjs = [Contact.objects.get(pk=x) for x in ecitem]
        for i in myobjs:
            print(i.first_name + ' '+ i.primary_email)

        return render(request, 'iconnect/viewsummary.html')


class ConfirmSendView(FormView):
    def post(self, request, *args, **kwargs):
        return render(request, 'iconnect/confirm.html')
