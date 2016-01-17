from django.db import models
from contacts.models import Center, Contact, Zone, Sector
from django_markdown.models import MarkdownField


# Create your models here.
class ProgramMaster(models.Model):
    name = models.CharField(max_length=50)
    PROG_TYPE = (('NONE', 'Please Select'),
                 ('IP', 'Introductory Programs'),
                 ('AP', 'Advanced Programs'),
                 ('RP', 'Rejuvenation Programs'),
                 ('CP', 'Childrens Programs'),
                 ('SS', 'Sadhgurus Schedule'),
                 ('SP', 'Special Events & Other Programs'),)
    program_type = models.CharField(max_length=4, choices=PROG_TYPE, blank=True,
                                    default='NONE')

    LANG_TYPE = (('NONE', 'Please Select'),
                 ('TM', 'Tamil'),
                 ('EG', 'English'),
                 ('HI', 'Hindi'),
                 ('BI', 'bilingual'),
                 ('CH', 'Chinese'),)

    language_type = models.CharField(max_length=4, choices=LANG_TYPE, blank=True,
                                     default='NONE')

    description = MarkdownField(blank=True)

    def __str__(self):
        return "%s (%s)" % (self.name, self.program_type)

    class Meta:
        ordering = ['name', 'program_type']

    def save(self, *args, **kwargs):
        # clean up the name of all redundant spaces and title case it
        self.name = ' '.join([each_word if each_word.upper() == each_word
                              else each_word.title()
                              for each_word in self.name.split()])

        super(ProgramMaster, self).save(*args, **kwargs)


class ProgramSchedule(models.Model):
    center = models.ForeignKey(Center)
    program = models.ForeignKey(ProgramMaster)
    start_date = models.DateField("start Date", null=True, blank=True)
    end_date = models.DateField("end Date", null=True, blank=True)
    donation = models.DecimalField(default=0, max_digits=9, decimal_places=0)
    teacher_name = models.CharField("teacher Name", null=True, blank=True, max_length=50)
    coteacher_name = models.CharField("co-teacher Name", null=True, blank=True, max_length=50)
    ONLINE_REG_VALUES = (('Y', 'Yes'),
                         ('N', 'No'))

    online_registration = models.CharField(max_length=2, choices=ONLINE_REG_VALUES, default='Y', null=True,
                                           blank=True, )
    session_details = models.CharField(max_length=50, default='6.0.6')
    contact_name = models.CharField("contact Name", null=True, blank=True, max_length=50)
    contact_phone1 = models.CharField("Contact Phone1", max_length=15, blank=True)
    contact_phone2 = models.CharField("Contact Phone2", max_length=15, blank=True)
    contact_email = models.EmailField("contact Email", default='xyz@gmail.com', max_length=50)
    STATUS_VALUES = (('NW', 'New'),
                     ('RO', 'Registration Open'),
                     ('RC', 'Registration Close'),
                     ('CA', 'Cancelled'),
                     ('CO', 'Closed'),
                     ('PE', 'Preponed'),
                     ('PO', 'Postponed'))

    status = models.CharField(max_length=2, choices=STATUS_VALUES, default='Y', null=True,
                              blank=True, )

    def __str__(self):
        return "%s, %s" % (self.program, self.center)

    def sector_name(self):
        return Sector.objects.get(zone=self.zone_name)

    def zone_name(self):
        return Zone.objects.get(center=self.center)


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


class ScheduleNote(models.Model):
    contact = models.ForeignKey(ProgramSchedule)
    note = MarkdownField(max_length=500)

    class Meta:
        verbose_name = 'Intro Session Detail'
