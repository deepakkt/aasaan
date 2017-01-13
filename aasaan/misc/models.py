from django.db import models

from contacts.models import Zone, Center

# Create your models here.

class LocalEvents(models.Model):
    zone = models.ForeignKey(Zone)
    center = models.ForeignKey(Center)
    submitter_name = models.CharField(max_length=50)
    submitter_mobile = models.CharField(max_length=10)

    EVENT_CATEGORIES = (
        ('Public', 'Public'),
        ('Private', 'Private'),
        ('Educational Instituations', 'Educational Instituations'),
        ('Corporate', 'Corporate'),
        ('Government', 'Government'),
        ('Religious', 'Religious'),
        ('Other', 'Other'),
    )

    event_category = models.CharField(max_length=50, choices=EVENT_CATEGORIES)
    event_name = models.CharField(max_length=100)
    number_of_people = models.IntegerField()

    PEOPLE_CATEGORIES = (
        ('Isha Meditator', 'Isha Meditator'),
        ('General Public', 'General Public'),
        ('Devotees', 'Devotees'),
        ('Corporate', 'Corporate'),
        ('Students', 'Students'),
        ('VIPs', 'VIPs'),
        ('Other', 'Other'),
    )

    people_category = models.CharField(max_length=50, choices=PEOPLE_CATEGORIES)
    event_details = models.TextField()
    isha_aspect = models.CharField(max_length=100)
    event_start_date = models.DateField()
    event_end_date = models.DateField()
    event_timing = models.CharField(max_length=20)

    EVENT_ENTRY_CATEGORIES = (
        ('Free', 'Free'),
        ('Walk In', 'Walk In'),
        ('RSVP', 'RSVP'),
        ('Paid Registration', 'Paid Registration'),
        ('By Invite Only', 'By Invite Only'),
    )

    event_entry_category = models.CharField(max_length=50, choices=EVENT_ENTRY_CATEGORIES)
    event_url = models.URLField(max_length=100, blank=True)
    ashram_contact_name = models.CharField(max_length=50)
    ashram_contact_mobile = models.CharField(max_length=10)

    final_remarks = models.TextField(blank=True)
    admin_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['zone', 'center', '-event_start_date', 'event_name']

    def __str__(self):
        return "%s - %s - %s - %s" % (self.zone.zone_name, self.center.center_name,
                                      self.event_start_date.isoformat(), self.event_name)


