from django import forms
from .models import VoucherDetails
from tinymce.widgets import TinyMCE


class RCOAccountsForm(forms.ModelForm):
    copy_voucher = forms.BooleanField(label='Copy Voucher', required=False)

    class Meta:
        model = VoucherDetails
        fields = '__all__'


class MessageForm(forms.Form):
    sender = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'size': '88'}))
    to = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'size': '88'}))
    cc = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'size': '88'}))
    subject = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'size': '88'}))
    message = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30, 'theme': "advanced", 'plugins': "table", 'menubar': "table",  'toolbar': "table",  'table_tab_navigation': 'true',}))

