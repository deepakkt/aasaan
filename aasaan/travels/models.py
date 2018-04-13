from django.db import models
from contacts.models import Contact, Zone
from django.contrib.auth.models import User
import datetime


class TravelRequest(models.Model):
    source = models.CharField('From', max_length=100,default='')
    destination = models.CharField('To', max_length=100,default='')
    onward_date = models.DateField('Date of Journey', default=datetime.date.today)
    TRAVEL_MODE_VALUES = (('TR', 'Train'),
                           ('BS', 'Bus'),
                           ('FL', 'Flight'))

    travel_mode = models.CharField(max_length=2, choices=TRAVEL_MODE_VALUES,
                                    default=TRAVEL_MODE_VALUES[0][0])
    zone = models.ForeignKey(Zone, verbose_name='Zone', on_delete=models.CASCADE)
    remarks = models.CharField('Remarks', max_length=200, blank=True, null=True)
    STATUS_VALUES = (('IP', 'In-Progress'),
                          ('BK', 'Booked'),
                          ('CL', 'Cancelled'),
                          ('PD', 'Processed'))

    status = models.CharField(max_length=2, choices=STATUS_VALUES,
                                   default=STATUS_VALUES[0][0])
    email_sent = models.BooleanField(blank=True, default=False)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)



    def status_flag(self):
        if self.status == "CL":
            return "<span style='color : red;'>&#10006;</span>"
        if self.status == "PD":
            return "<span style='color : green;'>&#10004;</span>"

        return "<span style='color : black;'>&#9940;</span>"

    status_flag.allow_tags = True
    status_flag.short_description = " "

    def __str__(self):
        vd = Travellers.objects.filter(travel_request=self)
        if vd and len(vd)>1:
            return vd[0].teacher.full_name + ' + ' +str(len(vd) - 1)
        if vd and len(vd) == 1:
            return vd[0].teacher.full_name
        else:
            return ''

    class Meta:
        ordering = ['onward_date', ]
        verbose_name = 'Travel Request'


class Travellers(models.Model):
    travel_request = models.ForeignKey(TravelRequest, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Contact, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.teacher.full_name

    class Meta:
        verbose_name = 'Traveller'




