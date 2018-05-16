from django.db import models

# Create your models here.
class NotifyContext(models.Model):
    context_title = models.CharField(max_length=50)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.context_title


class Notifier(models.Model):
    notify_title = models.CharField(max_length=100)
    notify_context = models.ForeignKey(NotifyContext, on_delete=models.CASCADE)

    NOTIFY_STATUS = (('Draft', 'Draft'),
                        ('Scheduled', 'Scheduled'),
                        ('Completed', 'Completed'),
                        ('Incomplete', 'Incomplete'),
                        ('Failed', 'Failed'))

    notify_status = models.CharField(max_length=10, choices=NOTIFY_STATUS,
                                    default=NOTIFY_STATUS[0][0])

    NOTIFY_TYPE = (('Email', 'Email'),
                    ('SMS', 'SMS'))

    notify_type = models.CharField(max_length=10, choices=NOTIFY_TYPE,
                                    default=NOTIFY_TYPE[0][0])

    SENDING_MODE = (('Classic', 'Classic'),
                    ('Individual', 'Individual'),
                    )

    sending_mode = models.CharField(max_length=10, choices=SENDING_MODE,
                                    default=SENDING_MODE[0][0])                    

    notify_from = models.CharField(max_length=100)
    notify_to = models.TextField(blank=True)
    notify_cc = models.TextField(blank=True)
    attachments = models.TextField(blank=True)
    zones = models.TextField(blank=True)
    roles = models.TextField(blank=True)

    message = models.TextField()
    detailed_status = models.TextField(blank=True)
    delete_attachments = models.BooleanField("Delete attachments after send", default=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.notify_title

    def _line_split(self, tosplit):
        return tuple([x for x in tosplit.split('\r\n') if x 
                and not x.startswith('---')])

    def _name_email_pairs(self, name_list):
        _split = lambda x: tuple(x.split('|') * 2) if x.find('|') == -1 else tuple(x.split('|'))
        _to_dict = lambda x: {"name": x[0], "email": x[1]}
        return tuple([_to_dict(_split(x)) for x in name_list])

    def zone_list(self):
        return self._line_split(self.zones)

    def role_list(self):
        return self._line_split(self.roles)

    def to_list(self):
        return self._line_split(self.notify_to)

    def to_pairs(self):
        return self._name_email_pairs(self.to_list())

    def cc_pairs(self):
        return self._name_email_pairs(self.cc_list())

    def cc_list(self):
        return self._line_split(self.notify_cc)

    def attachment_list(self):
        _referenced = self._line_split(self.attachments)
        _attached = tuple((x.attachment.path for x in self.notifyattachment_set.all()))

        return tuple(_referenced + _attached)

    @property
    def from_email(self):
        return self._name_email_pairs([self.notify_from])[0]

    class Meta:
        ordering = ['-created']


class NotifyAttachment(models.Model):
    notification = models.ForeignKey(Notifier, on_delete=models.CASCADE)
    attachment = models.FileField(upload_to='notifications/')

    def __str__(self):
        return self.attachment.name