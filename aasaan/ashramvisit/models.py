from django.db import models
from contacts.models import Center, Contact, IndividualContactRoleZone, Zone
from smart_selects.db_fields import GroupedForeignKey


class AshramVisit(models.Model):
    Center = GroupedForeignKey(Center, 'zone')
    arrival_date = models.DateTimeField("Arrival Date & Time")
    departure_time = models.TimeField("Departure Time")
    participant_count = models.IntegerField()
    lunch = models.BooleanField()
    dinner = models.BooleanField()
    contact_person = models.CharField(max_length=100)
    mobile_no = models.CharField("Mobile Number", max_length=15)

    def __str__(self):
        return "%s - %s" %(self.Center, self.participant_count)