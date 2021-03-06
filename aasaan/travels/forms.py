from django import forms
from tinymce.widgets import TinyMCE
from .models import TravelRequest
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from contacts.models import Zone

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


class TravelForm(forms.ModelForm):
    class Meta:
        model = TravelRequest
        exclude = ['created', 'modified',]

    def clean(self):
        teacher = self.cleaned_data.get('teacher')
        is_others = self.cleaned_data.get('is_others')
        if not teacher and not is_others:
                raise ValidationError("Both Techer and Others cannot be empty")
        return self.cleaned_data


class TicketAdvancedSearchFieldsForm(forms.Form):
    zone = forms.ModelMultipleChoiceField(queryset=Zone.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'form-control'}))


class TravelOtherDetailsInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        count = 0
        for form in self.forms:
            try:
                if form.cleaned_data:
                    count += 1
            except AttributeError:
                pass
        if self.data.get('is_others', False):
            if count==0:
                raise forms.ValidationError('Please fill others passanger details')
