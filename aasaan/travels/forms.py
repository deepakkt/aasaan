from django import forms
from .models import TravelRequest
from django.contrib.admin.widgets import AdminDateWidget

TRAVEL_MODE_VALUES = (('TR', 'Train'),
                           ('BS', 'Bus'),
                           ('FL', 'Flight'))

class TravelRequestForm(forms.ModelForm):
    remarks = forms.CharField(widget=forms.Textarea(attrs={'rows':2, 'cols':40}), required=False)
    _to = forms.CharField(label='To')
    _from = forms.CharField(label='From')
    onward_date = forms.DateField(label = 'Onward Date',widget = AdminDateWidget)
    return_date = forms.DateField(label='Return Date', widget = AdminDateWidget, required=False)
    travel_mode = forms.ChoiceField(choices=TRAVEL_MODE_VALUES, widget=forms.Select(),
                      required=True)

    class Meta:
        model = TravelRequest
        fields = ['_to', '_from', 'onward_date', 'return_date', 'travel_mode', 'remarks']