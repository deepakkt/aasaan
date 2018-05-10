from django import forms
from tinymce.widgets import TinyMCE

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