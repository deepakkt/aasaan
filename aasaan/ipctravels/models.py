from django.db import models
import datetime, time
from contacts.models import Zone, Contact
from schedulemaster.models import ProgramSchedule
import os, os.path
from django.utils.text import slugify
from django.utils import timezone
from django_markdown.models import MarkdownField

class AgentMaster(models.Model):
    name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return "%s" % self.name


class TravelModeMaster(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return "%s" % self.name


class BudgetCodeMaster(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return "%s" % self.name


class TravelRequest(models.Model):
    STATUS_VALUES = (('NW', 'New Request'),
                     ('BK', 'Booked'),
                     ('PB', 'Partially Booked'),
                     ('CD', 'Cancelled'),
                     ('PC', 'Partially Cancelled'),
                     ('NP', 'Not processed'),)
    status = models.CharField(max_length=6, choices=STATUS_VALUES, blank=False,
                              default=STATUS_VALUES[0][0])
    request_date = models.DateField(default=timezone.now)
    total_fare = models.IntegerField(blank=True, null=True)
    cancellation_charge = models.IntegerField(blank=True, null=True)
    refund_amount = models.IntegerField(blank=True, null=True)
    REQMODE_VALUES = (('SMS', 'SMS'),
                     ('CL', 'Call'),
                     ('EM', 'Email'),
                     ('WA', 'Whatsapp'),
                     ('OT', 'Others'),)
    request_mode = models.CharField(max_length=6, choices=REQMODE_VALUES, blank=False, null=True,
                              default=REQMODE_VALUES[0][0])

    def __str__(self):
        return ' || '.join(["%s, %s, %s, %s -- by %s" %(m2.source, m2.destination, m2.date_of_journey, m2.travel_mode.name, m2.booked_by.name) for m2 in self.bookingdetails_set.all()])

    class Meta:
        verbose_name = 'Ticket Request'
        ordering = ['status']

    def get_status(self):

        return self.get_status_display()

    get_status.short_description = 'Status'

    @property
    def traveller(self):
        return ', '.join([m2.traveller.full_name if m2.traveller else m2.non_ipc_contacts for m2 in self.travellerdetails_set.all()])

    @property
    def travel_details(self):
        return ' || '.join(["%s, %s, %s, %s -- by %s" %(m2.source, m2.destination, m2.date_of_journey, m2.travel_mode.name, m2.booked_by.name) for m2 in self.bookingdetails_set.all()])


class BookingDetails(models.Model):
    request = models.ForeignKey(TravelRequest)
    date_of_journey = models.DateField()
    source = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    description = models.CharField('Remarks', max_length=300, blank=True, null=True)
    date_of_booking = models.DateField(blank=True, null=True)
    travel_mode = models.ForeignKey(TravelModeMaster, default=1)
    booked_by = models.ForeignKey(AgentMaster, default=1)

    def __str__(self):
        return "%s" % self.date_of_journey


class TravellerDetails(models.Model):
    request = models.ForeignKey(TravelRequest)
    traveller = models.ForeignKey(Contact, blank=True, null=True)
    non_ipc_contacts = models.CharField(max_length=150, blank=True, null=True)
    fare = models.IntegerField(blank=True, null=True)
    refund_amount = models.IntegerField(blank=True, null=True)
    zone = models.ForeignKey(Zone, blank=True, null=True)
    schedule = models.ForeignKey(ProgramSchedule, blank=True, null=True)
    PURPOSE_VALUES = (('SC', 'Schedule'),
                     ('BK', 'Break'),
                     ('OA', 'Other Activities'),
                     )
    purpose = models.CharField(max_length=6, choices=PURPOSE_VALUES, blank=False,
                              default=PURPOSE_VALUES[0][0])
    STATUS_VALUES = (('NB', 'NotBooked'),
                     ('BK', 'Booked'),
                     ('CD', 'Cancelled'),
                     )
    status = models.CharField(max_length=6, choices=STATUS_VALUES, blank=False,
                              default=STATUS_VALUES[0][0])
    budget_code = models.ForeignKey(BudgetCodeMaster, default=1)


def _generate_file_path(instance, filename):
    file_extension = os.path.splitext(filename)[-1]
    travel_ticket_name = slugify(time.strftime(os.path.splitext(filename)[0] +'_'+ "%Y%m%d%H%M%S")) + file_extension
    return os.path.join('travel_tickets', travel_ticket_name)


class TicketDetails(models.Model):
    request = models.ForeignKey(TravelRequest)
    attachment = models.FileField(upload_to=_generate_file_path, blank=True)


class AddtionalDetails(models.Model):
    request = models.ForeignKey(TravelRequest)
    note = MarkdownField(max_length=500)