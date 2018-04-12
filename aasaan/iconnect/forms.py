from django import forms

import ajax_select
from tinymce.widgets import TinyMCE

class MessageForm(forms.Form):
    subject = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'size': '88'}))
    STATUS_CHOICES = (
        ('EMail', "EMail"),
        ('SMS', "SMS"),)
    communication_type = forms.ChoiceField(choices=STATUS_CHOICES, label="Communication Type", initial='',
                                           widget=forms.Select(), required=True)
    message = forms.CharField(widget=TinyMCE(attrs={'cols': 90, 'rows': 30, 'theme': "advanced", 'plugins': "table", 'menubar': "table",  'toolbar': "table",  'table_tab_navigation': 'true',}))
    reason =forms.CharField(widget=TinyMCE(attrs={'cols': 90, 'rows': 30, 'theme': "advanced", 'plugins': "table", 'menubar': "table",  'toolbar': "table",  'table_tab_navigation': 'true',}))

class RecipientForm(forms.Form):
    zone = ajax_select.fields.AutoCompleteSelectMultipleField('zone',
                                                              required=True,
                                                              help_text="",
                                                              label="Zone",
                                                              )

    center = ajax_select.fields.AutoCompleteSelectMultipleField('center',
                                                                required=True,
                                                                help_text="",
                                                                label="Center",
                                                                )

    roles = ajax_select.fields.AutoCompleteSelectMultipleField('ipc_role',
                                                               required=True,
                                                               help_text="",
                                                               label="Roles (Ex: Organizer, Teacher)",
                                                               )

    role_group = ajax_select.fields.AutoCompleteSelectMultipleField('ipc_role_group',
                                                                    required=True,
                                                                    help_text="",
                                                                    label="Role Group / Communication Group",
                                                                    )

    contacts = ajax_select.fields.AutoCompleteSelectMultipleField('contact',
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
    communication_hash = forms.CharField(widget=forms.HiddenInput())
    contacts = forms.CharField(widget=forms.HiddenInput())
