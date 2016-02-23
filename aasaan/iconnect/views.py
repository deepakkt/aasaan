from .forms import PricingDeviceForm, CommunicationForm, Form2, Form3, Form4
from django.views.generic.edit import FormView, View
from django.http import HttpResponse
from .forms import ContactForm
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
import datetime
from contacts.models import Contact


class CommunicationView(FormView):
    def get(self, request, *args, **kwargs):
        form = CommunicationForm(
            initial={'reason': 'TO Organizer abt MSR', 'subject': 'Seating Pass', 'communication_type': '1',
                     'message': 'Seating Pass Over'})
        return render(request, 'iconnect/mailer.html', {'form': form})


class Form2View(FormView):
    def post(self, request, *args, **kwargs):
        form = Form2(
            initial={'reason': request.POST.get('reason'), 'communication_type': request.POST.get('communication_type'),
                     'subject': request.POST.get('subject'), 'message': request.POST.get('message')})
        return render(request, 'iconnect/recipients.html', {'form': form})


class Form3View(View):
    def post(self, request, *args, **kwargs):
        item = request.POST.get('include_role_group')
        item = [int(x) for x in item.split('|') if x]
        myobjs = [Contact.objects.get(pk=x) for x in item]
        return render(request, 'iconnect/viewsummary.html')


class Form4View(FormView):
    def post(self, request, *args, **kwargs):
        return render(request, 'iconnect/form4.html')
