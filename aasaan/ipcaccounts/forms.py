from django import forms
from .models import VoucherDetails


class RCOAccountsForm(forms.ModelForm):
    copy_voucher = forms.BooleanField(label='Copy Voucher', required=False)

    class Meta:
        model = VoucherDetails
        fields = '__all__'

