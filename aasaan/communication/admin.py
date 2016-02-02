from django.contrib import admin

from .models import Payload, PayloadDetail, EmailProfile

from django_markdown.admin import MarkdownModelAdmin
from django.forms import ModelForm, PasswordInput



# Register your models here.
class EmailProfileForm(ModelForm):
    class Meta:
        model = EmailProfile
        widgets = {
            'password' : PasswordInput
        }

class PayloadDetailAdmin(admin.TabularInline):
    model = PayloadDetail
    fields = ('communication_recipient', 'communication_send_time',
              'communication_status', 'communication_status_message')
    readonly_fields = ('communication_send_time', 'communication_status',
                       'communication_status_message')
    extra = 1


class PayloadAdmin(MarkdownModelAdmin):
    list_display = ('communication_title', 'communication_type', 'communication_date',
                    'communication_status', 'communication_hash', 'recipient_count')

    search_fields = ('communication_title',)

    list_filter = ('communication_type', 'communication_status')

    fields = ('communication_title', 'communication_type', 'communication_date',
              'communication_status',
              'communication_hash', 'communication_notes', 'communication_message')

    readonly_fields = ('communication_date', 'communication_hash')

    inlines = [PayloadDetailAdmin]


class EmailProfileAdmin(admin.ModelAdmin):
    form = EmailProfileForm

    list_display = ('profile_name', 'user_name', 'smtp_server', 'smtp_port')
    search_fields = ('profile_name',)

admin.site.register(Payload, PayloadAdmin)
admin.site.register(EmailProfile, EmailProfileAdmin)
