from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.conf import settings
from django.utils.text import slugify
import os.path

from django_markdown.models import MarkdownField

from datetime import date

def _generate_profile_path(instance, filename):
    image_extension = os.path.splitext(filename)[-1]
    profile_picture_name = slugify(instance.full_name + " profile picture") + image_extension
    return os.path.join('profile_pictures', profile_picture_name)

# Create your models here.
class Contact(models.Model):
    """Main contact model"""
    first_name = models.CharField("first Name", max_length=50)
    last_name = models.CharField("last Name", max_length=50)
    teacher_tno = models.CharField("teacher number", max_length=7, blank=True)

    date_of_birth = models.DateField("date of birth", null=True, blank=True)

    GENDER_VALUES = (('M', 'Male'),
                     ('F', 'Female'),
                     ('TG', 'Transgender'))

    gender = models.CharField(max_length=2, choices=GENDER_VALUES)

    STATUS_VALUES = (('STAFF', 'Staff'),
                     ('INACTV', 'Inactive'),
                     ('EXPD', 'Deceased'),
                     ('FT', 'Full Time'),
                     ('PT', 'Part Time'),
                     ('VOL', 'Volunteer'))

    status = models.CharField(max_length=6, choices=STATUS_VALUES, blank=True)

    cug_mobile = models.CharField("cUG phone number", max_length=15, blank=True)
    other_mobile_1 = models.CharField("alternate mobile 1", max_length=15, blank=True)
    other_mobile_2 = models.CharField("alternate mobile 2", max_length=15, blank=True)
    whatsapp_number = models.CharField('whatsapp number', max_length=15, blank=True)

    primary_email = models.EmailField("primary Email", max_length=50)
    secondary_email = models.EmailField("secondary Email", max_length=50, blank=True)

    pushbullet_token = models.CharField('pushbullet Token', max_length=64, blank=True)

    id_card_type = models.CharField("Ashram ID Card Type", max_length=10, blank=True)
    id_card_number = models.CharField("Ashram ID Card Number", max_length=20, blank=True)

    ID_PROOF_VALUES = (('DL', 'Driving License'),
                       ('PP', 'Passport'),
                       ('RC', 'Ration Card'),
                       ('VC', 'Voters ID'),
                       ('AA', 'Aadhaar'),
                       ('PC', 'PAN Card'),
                       ('OT', 'Other Government Issued'))

    id_proof_type = models.CharField("govt ID Proof Type", max_length=2,
                                     choices=ID_PROOF_VALUES, blank=True)
    id_proof_number = models.CharField("govt ID Card Number", max_length=30, blank=True)
    id_proof_other = models.CharField("type of govt ID if other", max_length=30, blank=True)

    profile_picture = models.ImageField(upload_to=_generate_profile_path, blank=True)

    remarks = MarkdownField(max_length=500, blank=True)

    def profile_image(self):
        image_style = 'style="width:50px; height:50px"'
        if self.profile_picture != "":
            image_url = "%s/%s" %(settings.MEDIA_URL, self.profile_picture)
            image_html = '<img src="%s" %s/>' % (image_url, image_style)
            image_hyperlink = '<a href="%s">%s</a>' %(image_url, image_html)
            return image_hyperlink
        else:
            no_picture = "profile_pictures/no-photo.jpg"
            image_url = "%s/%s" %(settings.MEDIA_URL, no_picture)
            image_html = '<img src="%s" %s/>' % (image_url, image_style)
            return image_html

    profile_image.short_description = "Profile picture"
    profile_image.allow_tags = True


    def _get_full_name(self):
        "Returns full name of contact"
        return "%s %s" %(self.first_name, self.last_name)
    full_name = property(_get_full_name)

    def _get_age(self):
        "Get age of contact"
        return self.date_of_birth.year - date.today().year
    age = property(_get_age)

    def _get_primary_mobile(self):
        "If CUG number is available get that. Otherwise get first alternate mobile"

        if self.cug_mobile:
            primary_mobile = self.cug_mobile
        else:
            primary_mobile = self.other_mobile_1
        return primary_mobile
    primary_mobile = property(_get_primary_mobile)

    def __str__(self):
        if self.teacher_tno:
            return "%s (%s)" % (self.full_name, self.teacher_tno)
        else:
            return self.full_name

    def clean(self):
        if (not self.cug_mobile) and (not self.other_mobile_1):
            raise ValidationError("At least one mobile number needs to be entered")

        if (self.id_proof_type == 'OT') and (not self.id_proof_other):
            raise ValidationError("Need ID proof type under 'Other' column")

        if (len(self.id_proof_type) > 0) and (not self.id_proof_number):
            raise ValidationError("ID Proof Number is missing")

        if (self.teacher_tno):
            if (self.teacher_tno[0].upper() != 'T'):
                raise ValidationError("Teacher number must be in Tnnnn format")

            try:
                teacher_no_int = int(self.teacher_tno[1:])
            except ValueError:
                raise ValidationError("Teacher number must be in Tnnnn format")

    def save(self, *args, **kwargs):
        self.teacher_tno = self.teacher_tno.rstrip().capitalize()

        #Check if status is being changed. Need to log note if so
        if not self.id:
            new_entry = True
        else:
            new_entry = False
            old_status = Contact.objects.get(pk=self.id).get_status_display()
            new_status = self.get_status_display()

        self.first_name = self.first_name.strip().capitalize()
        self.last_name = self.last_name.strip().capitalize()

        super(Contact, self).save(*args, **kwargs)

        #Create and save status change note if it has changed
        if not new_entry:
            if (old_status != new_status) and (old_status != ""):
                status_change_note = ContactNote()
                status_change_note.contact = self
                status_change_note.note_type = 'SC'
                status_change_note.note = "Automatic Log: Status of %s changed from '%s' to '%s'" % \
                                          (self.full_name, old_status, new_status)
                status_change_note.save()

    class Meta:
        ordering = ['first_name', 'last_name']
        verbose_name = 'PCC Contact'


class ContactNote(models.Model):
    """Notes about the contact"""
    contact = models.ForeignKey(Contact)

    NOTE_TYPE_VALUES = (('SC', 'Status Change'),
                        ('CN', 'Critical Note'),
                        ('MN', 'Medical Note'),
                        ('IN', 'Information Note'),)

    note_type = models.CharField(max_length=2, choices=NOTE_TYPE_VALUES)

    note = MarkdownField(max_length=500)

    note_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "(%s)-%s-%s" %(self.contact.full_name, self.note_type, self.note[:25])

    class Meta:
        ordering = ['-note_timestamp']


class ContactAddress(models.Model):
    """Addresses of contacts"""

    contact = models.ForeignKey(Contact)

    ADDRESS_TYPE_VALUES = (('WO', 'Work'),
                           ('HO', 'Home'))

    address_type = models.CharField("address Type", max_length=2, choices=ADDRESS_TYPE_VALUES)

    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100)
    address_line_3 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    state = models.CharField(max_length=25, blank=True)
    country = models.CharField(max_length=25, blank=True)

    contact_number = models.CharField("contact number for this address", max_length=15, blank=True)

    def __str__(self):
        return "%s (%s)" %(self.contact.full_name, self.get_address_type_display())

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

        super(ContactAddress, self).save(*args, **kwargs)


class RoleGroup(models.Model):
    """Roles of contacts"""
    role_name = models.CharField(max_length=50, unique=True)
    role_remarks = models.TextField(blank=True)

    def _get_contacts_with_role(self):
        return [item.contact for item in self.contactrole_set.all()]
    contacts = property(_get_contacts_with_role)

    def __str__(self):
        return self.role_name

    class Meta:
        verbose_name = 'PCC Role Group'
        ordering = ['role_name']

    def clean(self):
        try:
            table_role_groups = Role.objects.get(role_name = self.role_name)
        except ObjectDoesNotExist:
            return

        if table_role_groups:
            raise ValidationError('The role group already exists!')


class ContactRoleGroup(models.Model):
    """Mapping of roles and contacts"""
    contact = models.ForeignKey(Contact)
    role = models.ForeignKey(RoleGroup)

    def __str__(self):
        return "%s (%s)" %(self.contact.full_name, self.role.role_name)


class Zone(models.Model):
    """Zone definitions"""
    zone_name = models.CharField(max_length=50, unique=True)

    def _get_centers_in_zone(self):
        return self.center_set.all()
    centers = property(_get_centers_in_zone)

    def __str__(self):
        return self.zone_name

    class Meta:
        verbose_name = 'PCC Zone'
        ordering = ['zone_name']

    def save(self, *args, **kwargs):
        zone_word_list = [eachword.upper() if eachword.upper() == eachword else eachword.title() for eachword in self.zone_name.split()]
        self.zone_name = ' '.join(zone_word_list).strip()

        super(Zone, self).save(*args, **kwargs)

        default_sector = Sector()
        default_sector.zone = self
        default_sector.sector_name = "Default Sector for %s" %(self.zone_name)

        default_sector.save()


class Sector(models.Model):
    """Sector definitions. All sectors should be mapped to a zone"""
    zone = models.ForeignKey(Zone)
    sector_name = models.CharField(max_length=50)

    def __str__(self):
        return "%s (%s)" %(self.sector_name, self.zone.zone_name)


class Center(models.Model):
    """Center definitions. All centers should be mapped to sectors and zones"""
    zone = models.ForeignKey(Zone)
    center_name = models.CharField(max_length=50)

    def __str__(self):
        return "%s (%s)" % (self.center_name, self.zone.zone_name)

    class Meta:
        ordering = ['center_name']
        verbose_name = 'PCC Center'

    def save(self, *args, **kwargs):
        self.center_name = self.center_name.title().strip()
        super(Center, self).save(*args, **kwargs)


class IndividualRole(models.Model):
    """Definition for individual roles
    like 'Treasurer', 'Organizer' etc
    The role can be at center level, sector level
    or zone level
    """
    role_name = models.CharField(max_length=50, unique=True)

    ROLE_LEVEL_CHOICES = (('ZO', 'Zone'),
                          ('SC', 'Sector'),
                          ('CE', 'Center'),)
    role_level = models.CharField(max_length=2, choices=ROLE_LEVEL_CHOICES)
    role_remarks = models.TextField(blank=True)

    def __str__(self):
        return "%s (%s)" %(self.role_name, self.get_role_level_display())

    def save(self, *args, **kwargs):
        self.role_name = self.role_name.title().strip()
        super(IndividualRole, self).save(*args, **kwargs)

    class Meta:
        ordering = ['role_name', 'role_level']
        verbose_name = 'PCC Role'

    def clean(self):
        try:
            table_roles = IndividualRole.objects.get(role_name = self.role_name.title().strip())
        except ObjectDoesNotExist:
            return

        if table_roles:
            raise ValidationError('The role already exists!')


class IndividualContactRoleCenter(models.Model):
    """ Maps individual contacts to individual roles.
    They always need to be mapped to a center
    """
    contact = models.ForeignKey(Contact)
    center = models.ForeignKey(Center)
    role = models.ForeignKey(IndividualRole)

    class Meta:
        ordering = ['contact', 'role', 'center']
        verbose_name = 'PCC center level contact role'

    def clean(self):
        if (self.role.get_role_level_display() != 'Center'):
            raise ValidationError("Only center level roles can be mapped to a center")

        existing_contact_roles = IndividualContactRoleCenter.objects.filter(contact=self.contact)
        center_role_combos = [(item.center, item.role) for item in existing_contact_roles]

        if ((self.center, self.role) in center_role_combos) and (not self.id):
            raise ValidationError("This role has already been mapped for this contact and center")

    def __str__(self):
        return "%s - %s - %s" % (self.contact.full_name, self.center.center_name,
                               self.role.role_name)


class IndividualContactRoleZone(models.Model):
    """ Maps individual contacts to individual roles.
    They always need to be mapped to a center
    """
    contact = models.ForeignKey(Contact)
    zone = models.ForeignKey(Zone)
    role = models.ForeignKey(IndividualRole)

    class Meta:
        ordering = ['contact', 'role', 'zone']
        verbose_name = 'PCC zone level contact role'

    def clean(self):
        if (self.role.get_role_level_display() != 'Zone'):
            raise ValidationError("Only zone level roles can be mapped to a zone")

        existing_contact_roles = IndividualContactRoleZone.objects.filter(contact=self.contact)
        zone_role_combos = [(item.zone, item.role) for item in existing_contact_roles]

        if ((self.zone, self.role) in zone_role_combos) and (not self.id):
            raise ValidationError("This role has already been mapped for this contact and zone")


class IndividualContactRoleSector(models.Model):
    """ Maps individual contacts to individual roles.
    They always need to be mapped to a center
    """
    contact = models.ForeignKey(Contact)
    sector = models.ForeignKey(Sector)
    role = models.ForeignKey(IndividualRole)

    class Meta:
        ordering = ['contact', 'role', 'sector']
        verbose_name = 'PCC sector level contact role'

    def clean(self):
        if (self.role.get_role_level_display() != 'Sector'):
            raise ValidationError("Only sector level roles can be mapped to a sector")

        existing_contact_roles = IndividualContactRoleSector.objects.filter(contact=self.contact)
        sector_role_combos = [(item.sector, item.role) for item in existing_contact_roles]

        if ((self.sector, self.role) in sector_role_combos) and (not self.id):
            raise ValidationError("This role has already been mapped for this contact and sector")
