from django.shortcuts import render
from django.views.generic import ListView

from .models import Contact
# Create your views here.

class ListContactView(ListView):
    model = Contact
    template_name = 'contacts/contacts_list.html'




