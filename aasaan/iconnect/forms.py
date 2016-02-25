from ajax_select.fields import AutoCompleteField
from django import forms
from django_markdown.fields import MarkdownFormField
from django_markdown.widgets import MarkdownWidget
import ajax_select


class MessageForm(forms.Form):
    subject = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'size': '88'}))
    STATUS_CHOICES = (
        (1, "Email"),
        (2, "SMS"),)
    communication_type = forms.ChoiceField(choices=STATUS_CHOICES, label="Communication Type", initial='',
                                           widget=forms.Select(), required=True)
    message = forms.CharField(widget=MarkdownWidget())
    reason = MarkdownFormField()


class RecipientForm(forms.Form):
    include_role_group = ajax_select.fields.AutoCompleteSelectMultipleField('ipc_roles',
                                                                            required=True,
                                                                            help_text="",
                                                                            label="IPC Role",
                                                                            )
    include_contact_group = ajax_select.fields.AutoCompleteSelectMultipleField('individual_role',
                                                                               required=True,
                                                                               help_text="",
                                                                               label="Contact Group",
                                                                               )
    exclude_contacts = ajax_select.fields.AutoCompleteSelectMultipleField('contact',
                                                                          required=True,
                                                                          help_text="",
                                                                          label="Contacts to exclude",
                                                                          )
    reason = forms.CharField(widget=forms.HiddenInput())
    subject = forms.CharField(widget=forms.HiddenInput())
    communication_type = forms.CharField(widget=forms.HiddenInput())
    message = forms.CharField(widget=forms.HiddenInput())


class SummaryForm(forms.Form):
    reason = forms.CharField(widget=forms.HiddenInput())
    subject = forms.CharField(widget=forms.HiddenInput())
    communication_type = forms.CharField(widget=forms.HiddenInput())
    message = forms.CharField(widget=forms.HiddenInput())
    include_role_group = forms.CharField(widget=forms.HiddenInput())
    include_contact_group = forms.CharField(widget=forms.HiddenInput())
    exclude_contacts = forms.CharField(widget=forms.HiddenInput())
