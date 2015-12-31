from django.db import models
from contacts.models import Center

from django_markdown.models import MarkdownField

from datetime import datetime

# Create your models here.
class Schedule(models.Model):
    program_title = models.CharField(max_length=200, blank=True)
    program_code = models.CharField(max_length=50, blank=True)
    program_code_source = models.CharField(max_length=10, blank=True,
                                           verbose_name="scheduling software")
    start_date = models.DateField()
    program_type = models.CharField(max_length=10, blank=True)
    center = models.ForeignKey(Center)

    YES_OR_NO = (('Y', 'Yes'),
                 ('N', 'No'),)
    matched = models.CharField(max_length=1, default="N", choices=YES_OR_NO)
    match_confidence = models.PositiveSmallIntegerField()

    MATCH_OVERRIDDEN = (('Y', 'Match Overridden'),
                        ('N', 'System Match'))

    match_overridden = models.CharField(max_length=1, default="N", choices=MATCH_OVERRIDDEN)

    MATCH_APPROVED = (('Y', 'Match Approved'),
                      ('N', 'Match to be approved'))

    match_approved = models.CharField(max_length=1, default="N", choices=MATCH_APPROVED)

    remarks = MarkdownField(blank=True)
    date_created= models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "'%s' - %s (%s)" %(self.program_title,
                                self.program_code, self.program_code_source)

    def save(self, *args, **kwargs):
        additional_remarks = ""
        if self.id:
            #Do the below only if the entry is already there
            #if admin is keying in a new program, let him do per his whim
            existing_entry = Schedule.objects.get(id=self.id)

            if (self.center != existing_entry.center):
                #User has overridden system assigned center

                self.match_confidence = 100
                self.match_approved = 'Y'
                self.matched = 'Y'
                self.match_overridden = 'Y'

                base_remarks = """

%s:
Changed center from "%s" to "%s"
Setting match as success, confidence to 100 percent, override and approved as positive!
"""
                additional_remarks = base_remarks %(datetime.now().isoformat(),
                                                   existing_entry.center.center_name,
                                                    self.center.center_name)

            elif (self.match_approved != existing_entry.match_approved):
                base_remarks = """

%s:
Admin approved system generated match. Setting match as success and confidence to 100 percent!
"""
                self.match_confidence = 100
                self.matched = 'Y'
                additional_remarks = base_remarks % (datetime.now().isoformat())

        self.remarks += additional_remarks
        super(Schedule, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-start_date', '-program_code']
        verbose_name = 'program schedule'


class SyncLog(models.Model):
    sync_date = models.DateTimeField(auto_now_add=True)
    records_fetched = models.IntegerField(default=0)
    new_records_added = models.IntegerField(default=0)
    old_records_skipped = models.IntegerField(default=0)
    matched_centers = models.IntegerField(default=0)

    def __str__(self):
        return "Sync @ %s, %d of %d programs added" %(self.sync_date.isoformat(),
                                                self.new_records_added, self.records_fetched)

    class Meta:
        ordering = ['-sync_date']