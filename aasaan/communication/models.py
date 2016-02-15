from datetime import datetime
from hashlib import md5
import random

from django.core.exceptions import ValidationError
from django.db import models
from django_markdown.models import MarkdownField
from .settings import COMMUNICATION_TYPES, COMMUNICATION_STATUS, \
    COMMUNICATION_CONTEXTS, RECIPIENT_VISIBILITY


# Create your models here.
class AbstractPayload(models.Model):
    communication_status = models.CharField(max_length=25, choices=COMMUNICATION_STATUS,
                                            default=COMMUNICATION_STATUS[0][0])
    communication_status_message = MarkdownField(blank=True)

    def _set_status(self, status):
        self.communication_status = status

    def set_success(self):
        self._set_status("Complete")

    def set_in_progress(self):
        self._set_status("In Progress")

    def set_error(self):
        self._set_status("Error")

    def _is_status(self, status):
        if self.communication_status == status:
            return True
        else:
            return False

    def is_status_pending(self):
        return self._is_status("Pending")

    class Meta:
        abstract = True


class Payload(AbstractPayload):
    communication_title = models.CharField(max_length=100, blank=True)
    communication_type = models.CharField(max_length=15, choices=COMMUNICATION_TYPES,
                                          default=COMMUNICATION_TYPES[0][0], blank=True)
    communication_context = models.CharField(max_length=15, choices=COMMUNICATION_CONTEXTS,
                                             default=COMMUNICATION_CONTEXTS[0][0])
    communication_date = models.DateTimeField(auto_now_add=True)
    communication_hash = models.CharField(max_length=100, blank=True)
    communication_notes = MarkdownField()
    communication_message = MarkdownField()

    recipient_visibility = models.CharField("recipient visibility (applies only to email profiles)",
                                            max_length=20, blank="",
                                            choices=RECIPIENT_VISIBILITY,
                                            default=RECIPIENT_VISIBILITY[0][0])

    def recipient_count(self):
        return PayloadDetail.objects.filter(communication=self).count()

    def generate_message_key(self):
        hash_digest = md5()

        for value in (self.communication_title, self.communication_context,
                      self.communication_date, self.communication_message,
                      self.communication_notes, str(random.random())):
            hash_digest.update(bytes(repr(value), 'utf-8'))

        self.communication_hash = hash_digest.hexdigest()

    def __str__(self):
        recipient_count = self.recipient_count()

        if recipient_count == 1:
            recipient_text = 'recipient'
        else:
            recipient_text = 'recipients' \
                             ''
        recipient_count_text = "%d %s" % (self.recipient_count(), recipient_text)

        return "(%s) %s (%s)" % (self.communication_type, self.communication_title,
                                 recipient_count_text)

    def save(self, *args, **kwargs):
        if not self.id:
            self.generate_message_key()

        super(Payload, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-communication_date', 'communication_title']


class PayloadDetail(AbstractPayload):
    communication = models.ForeignKey(Payload, on_delete=models.CASCADE)
    communication_recipient = models.CharField(max_length=100)
    communication_send_time = models.DateTimeField(null=True)

    def set_send_time(self):
        self.communication_send_time = datetime.now()
        self.save()

    def __str__(self):
        return "%s - %s" % (self.communication, self.communication_recipient)

    class Meta:
        ordering = ['communication', 'communication_recipient']


class CommunicationProfile(models.Model):
    communication_type = models.CharField(max_length=25, choices=COMMUNICATION_TYPES,
                                          default=COMMUNICATION_TYPES[0][0])
    profile_name = models.CharField(max_length=255)
    sender_name = models.CharField("sender name to use", max_length=100, blank=True)
    sender_id = models.CharField("from email or ID to use", max_length=100, blank=True)
    user_name = models.CharField("user name or API key", max_length=100)
    password = models.CharField("password (if applicable)", max_length=255, blank=True)
    smtp_server = models.CharField("SMTP server address (for email only)", max_length=100,
                                   default="smtp.gmail.com")
    smtp_port = models.SmallIntegerField("SMTP port (for email only)", default=587)
    use_tls = models.BooleanField("TLS settings (email only)", default=True)
    use_ssl = models.BooleanField("SSL settings (email only)", default=False)
    default = models.BooleanField("use this as default profile?", default=False)
    remarks = MarkdownField(blank=True)

    def __str__(self):
        return "%s (%s)" % (self.profile_name, self.communication_type)

    def save(self, *args, **kwargs):
        # if this profile is made default, mark others as not default
        if self.default:
            for profile in CommunicationProfile.objects.all():
                if profile == self:
                    pass
                else:
                    if profile.default and profile.communication_type \
                            == self.communication_type:
                        profile.default = False
                        profile.save()

        self.profile_name = self.profile_name.strip().title()
        super(CommunicationProfile, self).save(*args, **kwargs)

    class Meta:
        unique_together = ['communication_type', 'profile_name']
