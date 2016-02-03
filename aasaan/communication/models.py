from datetime import datetime
from hashlib import md5
import random

from django.core.exceptions import ValidationError
from django.db import models
from django_markdown.models import MarkdownField
from .settings import COMMUNICATION_TYPES, COMMUNICATION_STATUS, \
    COMMUNICATION_CONTEXTS


# Create your models here.
class AbstractPayload(models.Model):
    communication_status = models.CharField(max_length=25, choices=COMMUNICATION_STATUS,
                                            default=COMMUNICATION_STATUS[0][0])

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
    communication_status_message = models.TextField(blank=True)

    def set_send_time(self):
        self.communication_send_time = datetime.now()
        self.save()

    def __str__(self):
        return "%s - %s" % (self.communication, self.communication_recipient)

    class Meta:
        ordering = ['communication', 'communication_recipient']


class EmailSetting(models.Model):
    RECIPIENT_VISIBILITY = (('BCC', 'All recipients in BCC'),
                            ('TO/CC', 'First recipient in "To", others in CC'),
                            ('TO/BCC', 'First recipient in "To", others in BCC'),
                            ('Individual', 'Send individual email to all (Slower)'),)
    recipient_visibility = models.CharField(max_length=10, choices=RECIPIENT_VISIBILITY,
                                            default=RECIPIENT_VISIBILITY[0][0])

    def __str__(self):
        return "!!Do not delete this row -AND- do not add another row!!"


class EmailProfile(models.Model):
    profile_name = models.CharField(max_length=100)
    display_name = models.CharField("name to display in the 'From' field", max_length=100)
    user_name = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    smtp_server = models.CharField(max_length=100, default="smtp.gmail.com")
    smtp_port = models.SmallIntegerField(default=587)
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    default = models.BooleanField("use this as default profile?", default=False)
    remarks = MarkdownField(blank=True)

    def __str__(self):
        return self.profile_name

    def clean(self):
        if self.use_ssl and self.use_tls:
            raise ValidationError('Both SSL and TLS cannot be true. Uncheck one of them')

    def save(self, *args, **kwargs):
        # if this profile is made default, mark others as not default
        if self.default:
            for profile in EmailProfile.objects.all():
                if profile == self:
                    pass
                else:
                    if profile.default:
                        profile.default = False
                        profile.save()

        super(EmailProfile, self).save(*args, **kwargs)