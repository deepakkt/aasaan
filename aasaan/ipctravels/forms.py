from django import forms
from django.contrib.admin import widgets
from django.contrib.admin.widgets import AdminDateWidget
from functools import partial
from .models import TravelModeMaster, AgentMaster
from contacts.models import Zone

DateInput = partial(forms.DateInput, {'class': 'datepicker'})


class SummaryForm(forms.Form):

    STATUS_VALUES = (('NW', 'New Request'),
                     ('BK', 'Booked'),
                     ('PB', 'Partially Booked'),
                     ('CD', 'Cancelled'),
                     ('PC', 'Partially Cancelled'),
                     ('NP', 'Not processed'),)
    status = forms.CharField(
        max_length=3,
        widget=forms.Select(choices=STATUS_VALUES), required=False
    )
    journey_start_date = forms.DateField(widget=DateInput())
    journey_end_date = forms.DateField(widget=DateInput())
    booking_start_date = forms.DateField(widget=DateInput())
    booking_end_date = forms.DateField(widget=DateInput())
    travel_mode = forms.ModelChoiceField(queryset=TravelModeMaster.objects.all())
    agent = forms.ModelChoiceField(queryset=AgentMaster.objects.all())
    zone = forms.ModelMultipleChoiceField(queryset=Zone.objects.all(), widget=forms.CheckboxSelectMultiple())
