from ajax_select.fields import AutoCompleteField
from django import forms
from django_markdown.fields import MarkdownFormField
from django_markdown.widgets import MarkdownWidget
import ajax_select


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    email = forms.EmailField(required=False, label='Your e-mail address')
    message = forms.CharField(widget=forms.Textarea)
    include_list = forms.CharField(widget=forms.HiddenInput(), initial=123)


class CommunicationForm(forms.Form):
    subject = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'size': '88'}))
    STATUS_CHOICES = (
        (1, "Email"),
        (2, "SMS"),)
    communication_type = forms.ChoiceField(choices=STATUS_CHOICES, label="Communication Type", initial='',
                                           widget=forms.Select(), required=True)
    message = forms.CharField(widget=MarkdownWidget())
    reason = MarkdownFormField()


# class PricingDeviceForm(forms.Form):
#     device = ajax_select.fields.AutoCompleteSelectField(
#         ('contact'),
#         help_text=None,
#         required=False,
#     )
#
#     def __init__(self, *args, **kwargs):
#         super(PricingDeviceForm, self).__init__(*args, **kwargs)
#         self.fields['device'].widget.attrs.update({
#             'placeholder': "Add more devices",
#             'class': 'span12',
#         })


class Form2(forms.Form):
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


class Form3(forms.Form):
    subject = forms.CharField(widget=forms)


class Form4(forms.Form):
    subject4 = forms.CharField(max_length=200)
