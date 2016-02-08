from django.db import models
from django.core.exceptions import ValidationError

from contacts.models import Center, Contact, Zone, Sector
from django_markdown.models import MarkdownField


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(active=True)


class LanguageMaster(models.Model):
    name = models.CharField(max_length=50)
    description = MarkdownField(blank=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'Language Master'
        ordering = ['name']


class BatchMaster(models.Model):
    name = models.CharField(max_length=50)
    description = MarkdownField(blank=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'Batch Master'
        ordering = ['name']


class ProgramCategory(models.Model):
    name = models.CharField(max_length=50)
    description = MarkdownField(blank=True)
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

    objects = models.Manager()
    active_objects = ActiveManager()

    description = MarkdownField(blank=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'Program Master'
        ordering = ['name']


class ProgramMasterCategory(models.Model):
    program = models.ForeignKey(ProgramMaster)
    category = models.ForeignKey(ProgramCategory)

    def __str__(self):
        return "%s - %s" % (self.program, self.category)

    class Meta:
        ordering = ['program', 'category']


class ProgramCountMaster(models.Model):
    count_category = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()

    notes = MarkdownField(blank=True)

    def __str__(self):
        return self.count_category

    class Meta:
        verbose_name = 'program count type'
        ordering = ['count_category']


class ProgramSchedule(models.Model):
    program = models.ForeignKey(ProgramMaster)
    center = models.ForeignKey(Center)
    program_location = models.CharField(max_length=100)
    language = models.ForeignKey(LanguageMaster)
    second_language = models.ForeignKey(LanguageMaster, null=True,
                                        related_name='second_language')
    start_date = models.DateField("start Date")
    end_date = models.DateField("end Date")
    donation_amount = models.IntegerField()

    event_management_code = models.CharField(verbose_name="code from event management software",
                                             max_length=15, blank=True)

    online_registration = models.BooleanField(default=True)
    online_registration_code = models.CharField(max_length=15, blank=True)

    contact_name = models.CharField("contact Name", max_length=50)
    contact_phone1 = models.CharField("Contact Phone1", max_length=15)
    contact_phone2 = models.CharField("Contact Phone2", max_length=15, blank=True)
    contact_email = models.EmailField("contact Email", max_length=50)

    STATUS_VALUES = (('RO', 'Registration Open'),
                     ('AN', 'Announced'),
                     ('RC', 'Registration Closed'),
                     ('CA', 'Cancelled'),
                     ('CO', 'Closed'))

    status = models.CharField(max_length=2, choices=STATUS_VALUES,
                              default=STATUS_VALUES[0][0])

    def __str__(self):
        return "%s - %s - %s - %s" % (self.program, self.center, self.program_location,
                                 self.start_date.isoformat())

    def _sector_name(self):
        return Sector.objects.get(zone=self.zone_name)
    sector = property(_sector_name)

    def _zone_name(self):
        return Zone.objects.get(center=self.center)
    zone = property(_zone_name)

    def _program_name(self):
        return self.program.name
    program_name = property(_program_name)

    class Meta:
        verbose_name = 'Program Schedule'
        ordering = ['-start_date', 'center']


class ProgramVenueAddress(models.Model):
    program = models.ForeignKey(ProgramSchedule)
    venue_name = models.CharField(max_length=100)
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100)
    address_line_3 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    state = models.CharField(max_length=25, blank=True)
    country = models.CharField(max_length=25, blank=True)

    contact_number = models.CharField("contact number for this address", max_length=15, blank=True)

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

        super(VenueAddress, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'venue address'
        verbose_name_plural = 'venue addresses'


class ProgramScheduleNote(models.Model):
    program = models.ForeignKey(ProgramSchedule)
    note = MarkdownField()

    class Meta:
        verbose_name = 'program note'
        verbose_name_plural = 'notes about program'


class ProgramTeacher(models.Model):
    program = models.ForeignKey(ProgramSchedule)

    TEACHER_VALUES = (('MT', 'Main Teacher'),
                      ('CT', 'Co-Teacher'),
                      ('OT', 'Observation Teacher'))

    teacher_type = models.CharField(max_length=2, choices=TEACHER_VALUES,
                                    default=TEACHER_VALUES[0][0],
                                    null=True,
                                    blank=True)

    teacher = models.ForeignKey(Contact)

    class Meta:
        verbose_name = 'teacher for class'
        verbose_name_plural = 'teachers for class'


class ProgramBatch(models.Model):
    program = models.ForeignKey(ProgramSchedule)
    batch = models.ForeignKey(BatchMaster)
    start_time = models.CharField(max_length=10, blank=True)
    end_time = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return "%s - %s" % (self.program, self.batch)

    class Meta:
        verbose_name = 'Program Batch'


class ProgramScheduleCounts(models.Model):
    program = models.ForeignKey(ProgramSchedule)
    category = models.ForeignKey(ProgramCountMaster)
    value = models.IntegerField(default=0)

    def __str__(self):
        return "%s - %s - count" % self.program, self.category

    class Meta:
        verbose_name = 'program count'
