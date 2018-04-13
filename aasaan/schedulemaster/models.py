from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError

from datetime import date

from contacts.models import Center, Contact, Zone, Sector
from config.models import SmartModel, Tag
from smart_selects.db_fields import GroupedForeignKey
from utils.datedeux import DateDeux


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(active=True)


class LanguageMaster(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'Language Master'
        ordering = ['name']


class BatchMaster(models.Model):
    name = models.CharField(max_length=50)
    batch_code = models.CharField(max_length=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return "%s (%s)" % (self.name, self.batch_code)

    class Meta:
        verbose_name = 'Batch Master'
        ordering = ['name']


class ProgramCategory(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    display = models.BooleanField(default=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'Program Category'
        verbose_name_plural = 'Program Categories'
        ordering = ['name']


class ProgramMaster(models.Model):
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    admin = models.BooleanField(default=False)
    abbreviation = models.CharField(max_length=10, blank=True)

    objects = models.Manager()
    active_objects = ActiveManager()

    description = models.TextField(blank=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'Program Master'
        ordering = ['name']


class ProgramMasterCategory(models.Model):
    program = models.ForeignKey(ProgramMaster, on_delete=models.CASCADE)
    category = models.ForeignKey(ProgramCategory, on_delete=models.CASCADE)

    def __str__(self):
        return "%s - %s" % (self.program, self.category)

    class Meta:
        ordering = ['program', 'category']


class ProgramCountMaster(models.Model):
    count_category = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()

    notes = models.TextField(blank=True)

    def __str__(self):
        return self.count_category

    class Meta:
        verbose_name = 'program count type'
        ordering = ['count_category']


class ProgramSchedule(SmartModel):
    program = models.ForeignKey(ProgramMaster, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=100, blank=True)

    center = GroupedForeignKey(Center, 'zone')
    program_location = models.CharField(max_length=100)

    # don't change choice orders, will impact default value setting
    GENDER_VALUES = (('BO', 'All'),
                     ('M', 'Gents'),
                     ('F', 'Ladies'),)

    gender = models.CharField(max_length=2, choices=GENDER_VALUES,
                              default=GENDER_VALUES[0][0])

    primary_language = models.ForeignKey(LanguageMaster, on_delete=models.CASCADE)

    start_date = models.DateField(verbose_name='Program Start Date')
    end_date = models.DateField(verbose_name='Program End Date')
    donation_amount = models.IntegerField()

    hidden = models.BooleanField(default=False)

    event_management_software = models.CharField(max_length=15, blank=True)
    event_management_code = models.CharField(verbose_name="ORS Code",
                                             max_length=15, blank=True)

    online_registration = models.BooleanField(default=True)
    online_registration_code = models.CharField(verbose_name = "joomla Code", 
                                                max_length=15, blank=True)

    contact_name = models.CharField("contact Name", max_length=50)
    contact_phone1 = models.CharField("Contact Phone1", max_length=15)
    contact_phone2 = models.CharField("Contact Phone2", max_length=15, blank=True)
    contact_email = models.EmailField("contact Email", max_length=50)

    STATUS_VALUES = (('RO', 'Registration Open'),
                     ('RC', 'Registration Closed'),
                     ('CA', 'Cancelled'),
                     ('CO', 'Closed'))

    status = models.CharField(max_length=2, choices=STATUS_VALUES,
                              default=STATUS_VALUES[0][0])

    receipts = JSONField()

    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    cancelled_date = models.DateField(null=True)

    def __str__(self):
        if self.gender != self.GENDER_VALUES[0][0]:
            return "%s %s - %s - %s" % (self.program, self.get_gender_display(), self.center,
                                        self.start_date.isoformat())
        else:
            return "%s - %s - %s" % (self.program, self.center,
                                        self.start_date.isoformat())

    def _sector_name(self):
        return Sector.objects.get(zone=self.zone_name)
    sector = property(_sector_name)

    def _zone_name(self):
        return Zone.objects.get(center=self.center)
    zone = property(_zone_name)

    def _program_name(self):
        try:
            return self.event_name or self.program.name
        except:
            return ""
    program_name = property(_program_name)

    def _cancelled(self, field_value):
        if self.get_status_display() == "Cancelled":
            return "<span style='background-color: rgb(222, 186, 99);'>%s</span>" % field_value
        else:
            return field_value

    def is_cancelled(self):
        return "<span style='color : red;'>&#10006;</span>" \
            if self.get_status_display() == "Cancelled" \
            else "<span style='color : green;'>&#10004;</span>"
    is_cancelled.allow_tags = True
    is_cancelled.short_description = " "

    class Meta:
        verbose_name = 'Program Schedule'
        ordering = ['-start_date', 'center']

    @property
    def venue_address(self):
        venues = self.programvenueaddress_set.all()
        if venues:
            current_venue = venues[0]

            return "\n".join([current_venue.address_line_1,
                             current_venue.address_line_2,
                              current_venue.address_line_3])
        else:
            return ""

    @property
    def venue_city(self):
        venues = self.programvenueaddress_set.all()
        if venues:
            return venues[0].city
        else:
            return ""

    @property
    def venue_name(self):
        venues = self.programvenueaddress_set.all()
        if venues:
            return venues[0].venue_name
        else:
            return ""

    @property
    def joomla_configurations(self):
        configurations = self.programadditionalinformation_set.all()

        return {x.key: x.value for x in configurations if x.key.startswith('JOOMLA')}

    @property
    def tally_name(self):
        return "%s - %s - %s - %d" % (self.program.abbreviation,
                                    self.center.center_name,
                                    DateDeux.frompydate(self.start_date).dateformat("dd-mmm-yyyy"),
                                    self.id)



    def clean(self):
        if (self.end_date and self.start_date):
            if self.end_date < self.start_date:
                raise ValidationError('End date cannot be before start date')

        if (self.contact_phone1):
            if bool(self.contact_phone1.strip().find(' ') + 1) or \
                    bool(self.contact_phone2.strip().find(' ') + 1):
                raise ValidationError('Do not use spaces for contact number')

        if self.program_name == "Special Event":
            if not self.event_name:
                raise ValidationError("Event name is required for special events")

        if self.id:
            _template = "%s cannot be changed once set. "
            _error_list = ""
            _onetime_field_list = ["program", "center", "primary_language",
                                    "start_date", "end_date", "donation_amount"]

            _changed_fields = self.changed_fields()
            print(_changed_fields)

            for _field in _onetime_field_list:
                if _field in _changed_fields:
                    _field_display = " ".join([x.title() for x in _field.split("_")])
                    _error_list += _template % _field_display

            if "status" in _changed_fields:
                if _changed_fields["status"][0] == "Cancelled":
                    _error_list += "Cancelled program cannot be reinstated"

            if _error_list:
                raise ValidationError(_error_list)



    def save(self, *args, **kwargs):
        changed_fields = self.changed_fields()

        if not self.id:
            self.receipts = []

        if 'status' in changed_fields and changed_fields['status'][-1] == "Cancelled":
            self.cancelled_date = date.today()

        if 'status' in changed_fields and changed_fields['status'][0] == "Cancelled":
            self.cancelled_date = None

        super().save(*args, **kwargs)
        self.reset_changed_values()

class ProgramAdditionalLanguages(models.Model):
    program = models.ForeignKey(ProgramSchedule, on_delete=models.CASCADE)
    language = models.ForeignKey(LanguageMaster, on_delete=models.CASCADE)

    def __str__(self):
        return "%s - %s" % (self.program, self.language)


class ProgramVenueAddress(models.Model):
    program = models.ForeignKey(ProgramSchedule, on_delete=models.CASCADE)
    venue_name = models.CharField(max_length=100)
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100)
    address_line_3 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    state = models.CharField(max_length=25, blank=True)
    country = models.CharField(max_length=25, blank=True)

    contact_number = models.CharField("contact number for this address", max_length=15, blank=True)
    contact_email = models.EmailField("email for this address", max_length=100, blank=True)

    @property
    def address(self):
        base_list = [self.venue_name,
                     self.address_line_1,
                     self.address_line_2,
                     self.address_line_3,
                     self.city,
                     self.postal_code,
                     self.country]
        return "\n".join([x for x in base_list if x])

    def __str__(self):
        return "%s - venue for program" % self.program

    def clean(self):
        if not self.city:
            raise ValidationError('City cannot be empty')

        if self.postal_code.find(' ') != -1:
            raise ValidationError('Postal Code cannot contain spaces')

    def save(self, *args, **kwargs):
        def clean_address_line(address_line):
            "This function cleans up special characters from an address line \
            and squeezes multiple spaces into a single space."
            new_address_line = address_line.replace(",", " ")
            new_address_line = new_address_line.replace("-", " ")
            new_address_line = new_address_line.replace(".", " ")
            new_address_line = new_address_line.replace(":", " ")
            new_address_line = new_address_line.replace("  ", " ")
            new_address_line = new_address_line.replace("  ", " ")
            new_address_line = new_address_line.replace("  ", " ")
            new_address_line = new_address_line.title()
            return new_address_line.strip()

        self.city = self.city.strip().capitalize()

        self.venue_name = self.venue_name.strip().title()

        self.address_line_1 = clean_address_line(self.address_line_1)
        self.address_line_2 = clean_address_line(self.address_line_2)

        if self.address_line_3:
            self.address_line_3 = clean_address_line(self.address_line_3)

        if self.state:
            self.state = self.state.title().strip()

        if self.country:
            self.country = self.country.title().strip()

        super(ProgramVenueAddress, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'venue address'
        verbose_name_plural = 'venue addresses'


class ProgramScheduleNote(models.Model):
    program = models.ForeignKey(ProgramSchedule, on_delete=models.CASCADE)
    note = models.TextField()
    note_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.program, self.note)

    class Meta:
        ordering = ['-note_timestamp']
        verbose_name = 'program note'
        verbose_name_plural = 'notes about program'


class ProgramTeacher(models.Model):
    program = models.ForeignKey(ProgramSchedule, on_delete=models.CASCADE)

    TEACHER_VALUES = (('MO', 'Morning'),
                      ('NO', 'Noon'),
                      ('EV', 'Evening'),
                      ('MN', 'Morning and Noon'),
                      ('ME', 'Morning and Evening'),
                      ('NE', 'Noon and Evening'),
                      ('AL', 'Morning, Noon and Evening'),
                      ('FD', 'Full Day'),)

    teacher_type = models.CharField(max_length=2, choices=TEACHER_VALUES,
                                    null=True,
                                    blank=True)

    teacher = models.ForeignKey(Contact,
                                    null=True,
                                    blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return '%s - %s' % (self.program, self.teacher)

    class Meta:
        verbose_name = 'teacher for class'
        verbose_name_plural = 'teachers for class'
        unique_together = ['program', 'teacher']


class ProgramBatch(models.Model):
    program = models.ForeignKey(ProgramSchedule, on_delete=models.CASCADE)
    batch = models.ForeignKey(BatchMaster, on_delete=models.CASCADE)
    start_time = models.CharField(max_length=10, blank=True)
    end_time = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return "%s - %s" % (self.program, self.batch)

    class Meta:
        verbose_name = 'Program Batch'


class ProgramScheduleCounts(models.Model):
    program = models.ForeignKey(ProgramSchedule, on_delete=models.CASCADE)
    category = models.ForeignKey(ProgramCountMaster, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)

    def __str__(self):
        return "%s - %s - count" % (self.program, self.category)

    class Meta:
        verbose_name = 'program count'
        unique_together = ['program', 'category']



class ProgramReceiptAmounts(models.Model):
    program = models.ForeignKey(ProgramSchedule, on_delete=models.CASCADE)
    category = models.ForeignKey(ProgramCountMaster, on_delete=models.CASCADE)
    receipt_count = models.IntegerField(default=0)
    receipt_amount = models.DecimalField(max_digits=9, decimal_places=2)


    def __str__(self):
        return "%s - %s" % (self.program, self.category)

    class Meta:
        verbose_name = 'program receipt counts'
        unique_together = ['program', 'category']


class ProgramAdditionalInformation(models.Model):
    program = models.ForeignKey(ProgramSchedule, on_delete=models.CASCADE)
    key = models.CharField('title', max_length=50)
    value = models.TextField('information')

    def __str__(self):
        return "%s - %s" % (self.program, self.key)

    class Meta:
        verbose_name = 'additional program information. (Do not use if not required)'


class ProgramTag(models.Model):
    program = models.ForeignKey(ProgramSchedule, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return '%s - %s' % (self.program, self.tag)

    class Meta:
        ordering = ['program', 'tag']
        unique_together = ['program', 'tag']