from django import forms
from .models import TravelRequest
from django.contrib.admin.widgets import AdminSplitDateTime
from tinymce.widgets import TinyMCE

TRAVEL_MODE_VALUES = (('TR', 'Train'),
                           ('BS', 'Bus'),
                           ('FL', 'Flight'))

class TravelRequestForm(forms.ModelForm):
    remarks = forms.CharField(widget=forms.Textarea(attrs={'rows':2, 'cols':40}), required=False)
    source = forms.CharField(label='From')
    destination = forms.CharField(label='To')
    onward_date = forms.DateTimeField(label = 'Date of Journey',widget = AdminSplitDateTime)
    travel_mode = forms.ChoiceField(choices=TRAVEL_MODE_VALUES, widget=forms.Select(),
                      required=True)

    class Meta:
        model = TravelRequest
        fields = ['source', 'destination', 'onward_date', 'travel_mode', 'remarks']


class MessageForm(forms.Form):
    sender = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'size': '88'}))
    to = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'size': '88', 'type': 'email', 'multiple': 'true',
               'pattern': '^((\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*)\s*[;,.]{0,1}\s*)+$'}))
    cc = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'size': '88', 'type': 'email', 'multiple': 'true',
               'pattern': '^((\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*)\s*[;,.]{0,1}\s*)+$'}))
    bcc = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'size': '88', 'type': 'email', 'multiple': 'true',
               'pattern': '^((\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*)\s*[;,.]{0,1}\s*)+$'}))
    subject = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'size': '88', 'required':False,}))
    message = forms.CharField(widget=TinyMCE(attrs={'cols': 90, 'rows': 30, 'theme': "advanced", 'plugins': "table", 'menubar': "table",  'toolbar': "table",  'table_tab_navigation': 'true',}))
    # attachments = forms.FileField(widget=forms.ClearableFileInput(attrs={'label':'Attachments', 'multiple': True, 'required':False}))
    account_id = forms.CharField(widget = forms.HiddenInput(), required = False)