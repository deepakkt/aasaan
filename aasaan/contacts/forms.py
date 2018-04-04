from django import forms
from .models import Zone, IndividualRole


class FilterFieldsForm(forms.Form):
    zone = forms.ModelMultipleChoiceField(queryset=Zone.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    roles = forms.ModelMultipleChoiceField(queryset=IndividualRole.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'form-control'}))