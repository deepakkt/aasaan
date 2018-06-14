from django.db import models
from contacts.models import Contact, Zone
from django.contrib.auth.models import User
import datetime
from django.utils.html import format_html
from ipcaccounts.models import RCOAccountsMaster
from django.core.exceptions import ValidationError


class TravelRequest(models.Model):
    source = models.CharField('From', max_length=100,default='')
    destination = models.CharField('To', max_length=100,default='')
    onward_date = models.DateTimeField('Date of Journey')
    TRAVEL_MODE_VALUES = (('TR', 'Train'),
                           ('BS', 'Bus'),
                           ('FL', 'Flight'))

    travel_mode = models.CharField(max_length=2, choices=TRAVEL_MODE_VALUES,
                                    default=TRAVEL_MODE_VALUES[0][0])
    train_list = [('1', 'SL'), ('2', '2 AC'), ('3', '3 AC'), ('4', '2S'),('5', 'Chair Car'),]
    bus_list = [('6', 'Sleeper Non AC'), ('7', 'Sleeper AC'), ('10', 'Semi Sleeper Non AC'), ('11', 'Semi Sleeper AC')]
    flight_list = [('8', 'Economy'), ('9', 'Business')]
    item_list = (('Train', tuple(train_list)), ('Bus', tuple(bus_list)),('Flight', tuple(flight_list)))

    travel_class = models.CharField(max_length=2, choices=tuple(item_list))
    zone = models.ForeignKey(Zone, verbose_name='Zone', on_delete=models.CASCADE)
    remarks = models.TextField('Remarks', max_length=200, blank=True, null=True)
    STATUS_VALUES = (('IP', 'Requested'),
                     ('BO', 'Approved'),
                          ('BK', 'Booked'),
                          ('VC', 'Voucher Created'),
                          ('CL', 'Cancelled'),
                          ('CB', 'Booked Ticket Cancelled'),
                          ('PD', 'Voucher Processed'))

    status = models.CharField(max_length=2, choices=STATUS_VALUES,
                                   default=STATUS_VALUES[0][0])
    email_sent = models.BooleanField(blank=True, default=False)
    invoice_no = models.CharField(max_length=200, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    attachments = models.FileField(upload_to='documents/%Y/%m/%d/', null=True, blank=True)
    invoice = models.FileField(upload_to='invoice/%Y/%m/%d/', null=True, blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    booked_date = models.DateField('Booked Date', blank=True, null=True, default=datetime.date.today)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    teacher = models.ManyToManyField(Contact, blank=True)
    voucher = models.ForeignKey(RCOAccountsMaster, blank=True, null=True, on_delete=models.CASCADE)
    is_others = models.BooleanField('Others', blank=True, default=False)

    def status_flag(self):
        if self.status == "CL":
            return format_html("<span style='color : red;'>&#10006;</span>")
        if self.status == "PD":
            return format_html("<span style='color : green;'>&#10004;</span>")

        return format_html("<span style='color : black;'>&#9940;</span>")

    status_flag.allow_tags = True
    status_flag.short_description = " "

    def __str__(self):
        if self.teacher.all().exists():
            vd = self.teacher.all()
            if len(vd) > 1:
                return "%s %s + %s - %s (%s)" % (vd[0].first_name, vd[0].last_name, str(len(vd) - 1),
                                                    self.get_travel_mode_display(), self.get_travel_class_display())
            else:
                return "%s %s - %s (%s)" % (vd[0].first_name, vd[0].last_name,
                                            self.get_travel_mode_display(), self.get_travel_class_display())
        else:
            _travels_others = tuple(self.others_set.all().values_list('full_name'))
            other  = [x[0] for x in _travels_others]
            if len(other) > 1:
                return 'Others : %s + %s' %(other[0], str(len(other) - 1))
            elif len(other) == 1:
                return 'Others : %s' % other[0]
            else:
                return 'Others : No Teacher Added'

    class Meta:
        ordering = ['onward_date', ]
        verbose_name = 'Teacher Travel Request'


class TrTravelRequest(TravelRequest):
    class Meta:
        proxy = True
        verbose_name = 'Travel Request'


class AgentTravelRequest(TravelRequest):
    class Meta:
        proxy = True
        verbose_name = 'IPC Teachers Travel Request'


class Others(models.Model):
    travel_request = models.ForeignKey(TravelRequest, on_delete=models.CASCADE)
    full_name = models.CharField("full Name", max_length=50)
    age = models.PositiveSmallIntegerField()
    GENDER_VALUES = (('M', 'Male'),
                     ('F', 'Female'))
    gender = models.CharField(max_length=2, choices=GENDER_VALUES)
    mobile = models.CharField("Mobile Number", max_length=15, blank=True)

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ['full_name']
        verbose_name = 'Others detail'


class TravelNotes(models.Model):
    travel_request = models.ForeignKey(TravelRequest, on_delete=models.CASCADE)
    note = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return ""

    class Meta:
        ordering = ['-created']
        verbose_name = 'Travel Note'


class Attachment(models.Model):
    def validate_image(fieldfile_obj):
        filesize = fieldfile_obj.file.size
        megabyte_limit = 2.0
        if filesize > megabyte_limit * 1024 * 1024:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    event = models.ForeignKey(TravelRequest, on_delete=models.CASCADE)
    photos_multiple = models.ImageField(upload_to='teacher_travels/%Y/%m/%d/', verbose_name='Upload image file',validators=[validate_image],  blank=True, null=True)

    def __str__(self):
        return ""

    class Meta:
        ordering = ['event']
