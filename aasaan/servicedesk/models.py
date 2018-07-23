from django.db import models
from contacts.models import Zone, Center
from django.contrib.auth.models import User
from smart_selects.db_fields import GroupedForeignKey
from config.models import NotifyModel
from django.core.exceptions import ValidationError
from django.utils.html import format_html

class IPCSystemMaster(models.Model):
    name = models.CharField(max_length=100, unique=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, default=2)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'IPC System Master'
        verbose_name_plural = 'IPC System Master'


class ServiceStatusMaster(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'Service Status Master'
        verbose_name_plural = 'Service Status Master'


class ServiceRequest(NotifyModel):
    system_type = models.ForeignKey(IPCSystemMaster, verbose_name='Service Request', on_delete=models.CASCADE)
    status = models.ForeignKey(ServiceStatusMaster, verbose_name='Status', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField('Description', max_length=200)
    PRIORITY_VALUES = (('ME', 'Medium'),
                          ('HI', 'High'),
                          ('Low', 'Low'),
                          ('UR', 'Urgent'))
    priority = models.CharField(max_length=2, choices=PRIORITY_VALUES,
                                   default=PRIORITY_VALUES[0][0])
    expected_date = models.DateField('Expected Date')
    zone = models.ForeignKey(Zone, verbose_name='Zone', on_delete=models.CASCADE)
    center = GroupedForeignKey(Center, 'zone', blank=True, null=True)
    exp_resolved_date = models.DateField('Expected Resolve Date', blank=True, null=True)
    resolved_date = models.DateField('Actual Resolve Date', blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % self.title

    def status_flag(self):
        if self.status == "CL":
            return format_html("<span style='color : red;'>&#10006;</span>")
        if self.status == "PD":
            return format_html("<span style='color : green;'>&#10004;</span>")

        return format_html("<span style='color : black;'>&#9940;</span>")

    status_flag.allow_tags = True
    status_flag.short_description = " "

    class Meta:
        ordering = ['-created']
        verbose_name = 'Service Desk'
        verbose_name_plural = 'Service Desk'

    class NotifyMeta:
        notify_fields = ['status', 'priority', 'exp_resolved_date']
        notify_creation = True

        def get_recipients(self):
            _recipients = []
            _recipients.append(self.created_by.email)
            return _recipients

        def get_attachments(self):
            _attachments = []
            if self.attachments:
                _attachments.append(self.attachments.path)
            return _attachments


class IPCServiceRequest(ServiceRequest):

    class Meta:
        proxy = True
        verbose_name = 'IPC Service Desk'
        verbose_name_plural = 'IPC Service Desk'

class ServiceRequestNotes(models.Model):
    travel_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE)
    note = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return ""

    class Meta:
        ordering = ['-created']
        verbose_name = 'Service Note'


class Attachment(models.Model):
    def validate_image(fieldfile_obj):
        filesize = fieldfile_obj.file.size
        megabyte_limit = 2.0
        if filesize > megabyte_limit * 1024 * 1024:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    service = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE)
    photos_multiple = models.ImageField(upload_to='service_request/%Y/%m/%d/', verbose_name='Upload image file',validators=[validate_image],  blank=True, null=True)

    def __str__(self):
        return ""

    class Meta:
        ordering = ['service']