from datetime import datetime

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
        self.save()

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
    communication_date = models.DateField(auto_now_add=True)
    communication_hash = models.CharField(max_length=100)
    communication_notes = MarkdownField()
    communication_message = MarkdownField()

    def recipient_count(self):
        return PayloadDetail.objects.filter(communication=self).count()

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
        return " - ".join([self.communication, self.communication_recipient])

    class Meta:
        ordering = ['communication', 'communication_recipient']