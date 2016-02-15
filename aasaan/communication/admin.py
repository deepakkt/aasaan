from django.contrib import admin

from .models import Payload, PayloadDetail, CommunicationProfile

from django_markdown.admin import MarkdownModelAdmin
from django.forms import ModelForm, PasswordInput
from django.core.exceptions import ValidationError

from .api_refactor import send_communication



# Register your models here.
class CommunicationProfileForm(ModelForm):

    class Meta:
        model = CommunicationProfile
        fields = '__all__'
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
              'communication_status', 'communication_status_message',
              'communication_hash', 'communication_notes', 'communication_message')

    readonly_fields = ('communication_date', 'communication_hash', 'communication_status_message')

    inlines = [PayloadDetailAdmin]

    actions = ['send_selected_messages']

    def send_selected_messages(self, request, queryset):
        if queryset.count() > 1:
            self.message_user(request, 'For efficiency reasons, sending more than one message at a time is not allowed.')
            return

        payload = queryset[0]

        try:
            message_status = send_communication(payload.communication_type,
                                                payload.communication_hash)
        except ValidationError as e:
            message_status = e.args[0]

        self.message_user(request, 'Communication dispatched. API reports ==> %s' % message_status)

    send_selected_messages.short_description = "Send selected message"


class CommunicationProfileAdmin(MarkdownModelAdmin):
    form = CommunicationProfileForm

    list_display = ('profile_name', 'user_name', 'communication_type')
    search_fields = ('profile_name',)
    list_filter = ('communication_type',)

admin.site.register(Payload, PayloadAdmin)
admin.site.register(CommunicationProfile, CommunicationProfileAdmin)
