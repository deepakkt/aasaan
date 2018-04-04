from django import forms
from .models import VoucherDetails, AccountTypeMaster, NPVoucherStatusMaster, RCOVoucherStatusMaster
from tinymce.widgets import TinyMCE
from contacts.models import Zone

class RCOAccountsForm(forms.ModelForm):
    copy_voucher = forms.BooleanField(label='Copy Voucher', required=False)

    class Meta:
        model = VoucherDetails
        fields = '__all__'


class MessageForm(forms.Form):
    sender = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'size': '88'}))
    to = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'size': '88', 'type' : 'email', 'multiple':'true', 'pattern' :'^((\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*)\s*[;,.]{0,1}\s*)+$'}))
    cc = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'size': '88', 'type' : 'email', 'multiple':'true', 'pattern' :'^((\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*)\s*[;,.]{0,1}\s*)+$'}))
    bcc = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'size': '88', 'type' : 'email', 'multiple':'true', 'pattern' :'^((\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*)\s*[;,.]{0,1}\s*)+$'}))
    subject = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'size': '88'}))
    message = forms.CharField(widget=TinyMCE(attrs={'cols': 90, 'rows': 30, 'theme': "advanced", 'plugins': "table", 'menubar': "table",  'toolbar': "table",  'table_tab_navigation': 'true',}))
    account_id = forms.CharField(widget = forms.HiddenInput(), required = False)


class FilterFieldsForm(forms.Form):
    zone = forms.ModelMultipleChoiceField(queryset=Zone.objects.all())


class VoucherAdvancedSearchFieldsForm(forms.Form):
    zone = forms.ModelMultipleChoiceField(queryset=Zone.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    account_type = forms.ModelMultipleChoiceField(queryset=AccountTypeMaster.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    np_voucher_status = forms.ModelMultipleChoiceField(queryset=NPVoucherStatusMaster.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    rco_voucher_status = forms.ModelMultipleChoiceField(queryset=RCOVoucherStatusMaster.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'form-control'}))

