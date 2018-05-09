from django.db import models
from contacts.models import Contact, Zone
from django.contrib.auth.models import User
import datetime
from django.utils.html import format_html
from ipcaccounts.models import RCOAccountsMaster


class TravelRequest(models.Model):
    source = models.CharField('From', max_length=100,default='')
    destination = models.CharField('To', max_length=100,default='')
    onward_date = models.DateTimeField('Date of Journey')
    TRAVEL_MODE_VALUES = (('TR', 'Train'),
                           ('BS', 'Bus'),
                           ('FL', 'Flight'))

    travel_mode = models.CharField(max_length=2, choices=TRAVEL_MODE_VALUES,
                                    default=TRAVEL_MODE_VALUES[0][0])
    zone = models.ForeignKey(Zone, verbose_name='Zone', on_delete=models.CASCADE)
    remarks = models.TextField('Remarks', max_length=200, blank=True, null=True)
    STATUS_VALUES = (('IP', 'In-Progress'),
                          ('BK', 'Booked'),
                          ('VC', 'Voucher Created'),
                          ('CL', 'Cancelled'),
                          ('CB', 'Cancel Booked Ticket'),
                          ('PD', 'Processed'))

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
    teacher = models.ManyToManyField(Contact)
    voucher = models.ForeignKey(RCOAccountsMaster, blank=True, null=True, on_delete=models.CASCADE)

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
                return vd[0].first_name + ' ' + vd[0].last_name + ' + ' + str(len(vd) - 1)
            else:
                return vd[0].first_name + ' ' + vd[0].last_name
        return self.remarks[:25]



    class Meta:
        ordering = ['onward_date', ]
        verbose_name = 'Travel Request'



