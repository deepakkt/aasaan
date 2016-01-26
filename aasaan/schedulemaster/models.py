from django.db import models
from contacts.models import Center, Contact, Zone, Sector
from django_markdown.models import MarkdownField


class LanguageMaster(models.Model):
    name = models.CharField(max_length=50)
    description = MarkdownField(blank=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'Language Master'
        ordering = ['name']


class ProgramCategory(models.Model):
    name = models.CharField(max_length=50)
    description = MarkdownField(blank=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'Program Category'
        ordering = ['name']


class ProgramMaster(models.Model):
    category = models.ForeignKey(ProgramCategory)
    name = models.CharField(max_length=50)
    STATUS_VALUES = (('A', 'Active'),
                     ('IA', 'In-Active'))
    status = models.CharField(max_length=2, choices=STATUS_VALUES, blank=True,
                              default='A')
    description = MarkdownField(blank=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'Program Master'
        ordering = ['name']


class ProgramSchedule(models.Model):
    center = models.ForeignKey(Center)
    program = models.ForeignKey(ProgramMaster)
    language = models.ForeignKey(LanguageMaster)
    second_language = models.ForeignKey(LanguageMaster, null=True, blank=True, related_name='second_language')
    start_date = models.DateField("start Date", null=True, blank=True)
    end_date = models.DateField("end Date", null=True, blank=True)
    donation_amount = models.IntegerField()
    online_registration = models.CharField(null=True, blank=True, max_length=15)

    contact_name = models.CharField("contact Name", max_length=50)
    contact_phone1 = models.CharField("Contact Phone1", max_length=15)
    contact_phone2 = models.CharField("Contact Phone2", max_length=15, blank=True)
    contact_email = models.EmailField("contact Email", max_length=50)
    STATUS_VALUES = (('AN', 'Announced'),
                     ('RO', 'Registration Open'),
                     ('RC', 'Registration Closed'),
                     ('CA', 'Cancelled'),
                     ('CO', 'Closed'))

    status = models.CharField(max_length=2, choices=STATUS_VALUES, default='RO')
    total_participant_count = models.IntegerField(null=True, blank=True)
    description = MarkdownField(blank=True)


    def __str__(self):
        return "%s, %s" % (self.program, self.center)

    def sector_name(self):
        return Sector.objects.get(zone=self.zone_name)

    def zone_name(self):
        return Zone.objects.get(center=self.center)

    class Meta:
        verbose_name = 'Program Schedule'
        ordering = ['start_date', 'status']


class VenueAddress(models.Model):
    schedule = models.ForeignKey(ProgramSchedule)
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100)
    address_line_3 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    state = models.CharField(max_length=25, blank=True)
    country = models.CharField(max_length=25, blank=True)

    contact_number = models.CharField("contact number for this address", max_length=15, blank=True)

    def __str__(self):
        return "%s (%s)" % (self.contact.full_name, self.get_address_type_display())

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
        verbose_name = 'Venue Address'


class ScheduleNote(models.Model):
    program = models.ForeignKey(ProgramSchedule)
    note = MarkdownField(max_length=500)

    class Meta:
        verbose_name = 'Intro Session Detail'


class ClassTeachers(models.Model):
    program = models.ForeignKey(ProgramSchedule)

    TEACHER_VALUES = (('MT', 'Main Teacher'),
                      ('CT', 'Co Teacher'),
                      ('OT', 'Observation Teacher'))

    teacher_type = models.CharField(max_length=2, choices=TEACHER_VALUES, default='MT', null=True,
                                    blank=True)
    teachers = models.ForeignKey(Contact)

    class Meta:
        verbose_name = 'Class Teachers'


class BatchMaster(models.Model):
    name = models.CharField(max_length=50)
    description = MarkdownField(blank=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'Batch Master'
        ordering = ['name']


class ProgramBatch(models.Model):
    program = models.ForeignKey(ProgramSchedule)
    batch = models.ForeignKey(BatchMaster)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Program Batch'
