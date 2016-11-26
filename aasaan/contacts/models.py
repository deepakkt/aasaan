from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.conf import settings
from django.utils.text import slugify

from datetime import date
import os, os.path

from .settings import GENDER_VALUES, STATUS_VALUES, ID_PROOF_VALUES,\
                        ROLE_LEVEL_CHOICES, NOTE_TYPE_VALUES, \
                        ADDRESS_TYPE_VALUES, CATEGORY_VALUES, \
                        CENTER_CATEGORY_VALUES

from django_markdown.models import MarkdownField
from config.models import SmartModel, Tag

from PIL import Image


def _generate_profile_path(instance, filename):
    image_extension = os.path.splitext(filename)[-1]
    profile_picture_name = slugify(instance.full_name + " profile picture") + image_extension
    return os.path.join('profile_pictures', profile_picture_name)

def _generate_idproof_path(instance, filename):
    image_extension = os.path.splitext(filename)[-1]
    id_proof_name = slugify(instance.full_name + " - " +
                            instance.id_proof_number +
                            " - id proof") + image_extension
    return os.path.join('id_proof_scans', id_proof_name)


def _word_clean(word_to_clean):
    word_list = [eachword.upper() if eachword.upper() == eachword else eachword.title() for eachword in word_to_clean.split()]
    return ' '.join(word_list).strip()


# Create your models here.
class Contact(SmartModel):
    """Main contact model"""
    first_name = models.CharField("first Name", max_length=50)
    last_name = models.CharField("last Name", max_length=50)
    teacher_tno = models.CharField("teacher number", max_length=7, blank=True)
    date_of_birth = models.DateField("date of birth", null=True, blank=True)
    gender = models.CharField(max_length=2, choices=GENDER_VALUES)
    category = models.CharField(max_length=6, choices=CATEGORY_VALUES)
    status = models.CharField(max_length=6, choices=STATUS_VALUES)
    cug_mobile = models.CharField("cUG phone number", max_length=15, blank=True)
    other_mobile_1 = models.CharField("alternate mobile 1", max_length=15, blank=True)
    other_mobile_2 = models.CharField("alternate mobile 2", max_length=15, blank=True)
    whatsapp_number = models.CharField('whatsapp number', max_length=15, blank=True)
    primary_email = models.EmailField("primary Email", max_length=50, unique=True)
    secondary_email = models.EmailField("secondary Email", max_length=50, blank=True)
    pushbullet_token = models.CharField('pushbullet Token', max_length=64, blank=True)
    pushover_token = models.CharField('pushover Token', max_length=64, blank=True)
    id_card_type = models.CharField("Ashram ID Card Type", max_length=10, blank=True)
    id_card_number = models.CharField("Ashram ID Card Number", max_length=20, blank=True)
    id_proof_type = models.CharField("govt ID Proof Type", max_length=2,
                                     choices=ID_PROOF_VALUES, blank=True)
    id_proof_number = models.CharField("govt ID Card Number", max_length=30, blank=True)
    id_proof_other = models.CharField("type of govt ID if other", max_length=30, blank=True)
    id_proof_scan = models.ImageField(upload_to=_generate_idproof_path, blank=True)
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

    def profile_image_display(self):
        image_style = 'style="width:240px; height:300px"'
        if self.profile_picture != "":
            image_url = "%s/%s" %(settings.MEDIA_URL, self.profile_picture)
            image_html = '<img src="%s" %s/>' % (image_url, image_style)
            image_hyperlink = '<a href="%s">%s</a>' %(image_url, image_html)
            return image_hyperlink
        else:
            return "<strong>No profile picture available</strong>"

    profile_image_display.short_description = "Profile picture"
    profile_image_display.allow_tags = True

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
        def _validate_mobile():
            def _validate_length(mobile, min_length=10):
                if mobile:
                    if len(mobile) < min_length:
                        return False
                    else:
                        return True
                else:
                    return True

            return _validate_length(self.cug_mobile)  \
                   and _validate_length(self.other_mobile_1) \
                   and _validate_length(self.other_mobile_2)

        if not self.primary_mobile:
            raise ValidationError("At least one mobile number needs to be entered")

        if not _validate_mobile():
            raise ValidationError('Mobile number must be at least 10 digits')

        if (self.id_proof_type == 'OT') and (not self.id_proof_other):
            raise ValidationError("Need ID proof type under 'Other' column")

        if (len(self.id_proof_type) > 0) and (not self.id_proof_number):
            raise ValidationError("ID Proof Number is missing")

        if self.id_proof_number and not self.id_proof_type:
            raise ValidationError("ID proof number provided without ID proof type")

        if self.id_proof_scan and not self.id_proof_number:
            raise ValidationError("ID proof scan provided without other ID details")

        if (self.teacher_tno):
            if (self.teacher_tno[0].upper() != 'T'):
                raise ValidationError("Teacher number must be in Tnnnn format")

            try:
                teacher_no_int = int(self.teacher_tno[1:])
            except ValueError:
                raise ValidationError("Teacher number must be in Tnnnn format. Example T1234 or T0567")

    def save(self, *args, **kwargs):
        # get a map of field changes
        changed_fields = self.changed_fields()

        self.teacher_tno = self.teacher_tno.rstrip().capitalize()

        # Check if status is being changed. Need to log note if so
        new_entry = False if self.id else True

        self.first_name = self.first_name.title()
        self.last_name = self.last_name.title()

        super().save(*args, **kwargs)

        # Create and save status change note if it has changed
        if not new_entry:
            if 'status' in changed_fields or 'category' in changed_fields:
                status_change_note = ContactNote()
                status_change_note.contact = self
                status_change_note.note_type = 'SC'
                status_change_note.note = ""

                if 'status' in changed_fields:
                    status_change_note.note += "\nAutomatic Log: Status of %s changed from '%s' to '%s'\n" % \
                                              (self.full_name, changed_fields['status'][0],
                                               changed_fields['status'][-1])

                if 'category' in changed_fields:
                    status_change_note.note += "\nAutomatic Log: Category of %s changed from '%s' to '%s'\n" % \
                                              (self.full_name, changed_fields['category'][0],
                                               changed_fields['category'][-1])

                status_change_note.save()

        # profile picture / id card scan has been updated. clean up old one and
        # resize the new one
        if 'profile_picture' in changed_fields:
            old_picture_file = changed_fields['profile_picture'][0]
            if old_picture_file:
                old_picture_file.file.close()
                os.remove(old_picture_file.file.name)

            if self.profile_picture:
                profile_image = Image.open(self.profile_picture.file.name)
                resized_image = profile_image.resize((480, 640))
                resized_image.save(self.profile_picture.file.name)

        if 'id_proof_scan' in changed_fields:
            old_picture_file = changed_fields['id_proof_scan'][0]
            if old_picture_file:
                old_picture_file.file.close()
                os.remove(old_picture_file.file.name)

            if self.id_proof_scan:
                id_proof_image = Image.open(self.id_proof_scan.file.name)
                resized_image = id_proof_image.resize((640, 480))
                resized_image.save(self.id_proof_scan.file.name)

        self.reset_changed_values()

    class Meta:
        ordering = ['first_name', 'last_name']
        verbose_name = 'IPC Contact'


class ContactNote(models.Model):
    """Notes about the contact"""
    contact = models.ForeignKey(Contact)
    note_type = models.CharField(max_length=2, choices=NOTE_TYPE_VALUES,
                                 default=NOTE_TYPE_VALUES[0][0])
    note = MarkdownField(max_length=500)
    note_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "(%s)-%s-%s" %(self.contact.full_name, self.note_type, self.note[:25])

    class Meta:
        ordering = ['-note_timestamp']


class ContactAddress(models.Model):
    """Addresses of contacts"""

    contact = models.ForeignKey(Contact)
    address_type = models.CharField("address Type", max_length=2, choices=ADDRESS_TYPE_VALUES)

    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100)
    address_line_3 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    state = models.CharField(max_length=25, blank=True)
    country = models.CharField(max_length=25, blank=True)

    contact_number = models.CharField("contact number for this address", max_length=15, blank=True)

    @property
    def address(self):
        base_list = [self.get_address_type_display() + " Address",
                     self.address_line_1,
                     self.address_line_2,
                     self.address_line_3,
                     self.city,
                     self.postal_code,
                     self.country]
        return "\n".join([x for x in base_list if x])

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


class ContactTag(models.Model):
    contact= models.ForeignKey(Contact)
    tag = models.ForeignKey(Tag)

    class Meta:
        unique_together = ['contact', 'tag']
        ordering = ['contact', 'tag']

    def __str__(self):
        return "%s -%s" % (self.contact, self.tag)


class RoleGroup(models.Model):
    """Roles of contacts"""
    role_name = models.CharField(max_length=50, unique=True)
    role_remarks = models.TextField(blank=True)

    def _get_contacts_with_role(self):
        return [item.contact for item in self.contactrolegroup_set.all()]
    contacts = property(_get_contacts_with_role)

    def __str__(self):
        return self.role_name

    class Meta:
        verbose_name = 'IPC Role Group'
        ordering = ['role_name']

    def clean(self):
        try:
            table_role_groups = RoleGroup.objects.get(role_name=self.role_name)
        except ObjectDoesNotExist:
            return

        if table_role_groups and not self.id:
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
        verbose_name = 'IPC Zone'
        ordering = ['zone_name']

    def save(self, *args, **kwargs):
        self.zone_name = _word_clean(self.zone_name)

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


class PreCenterManager(models.Manager):
    def get_queryset(self):
        return super(PreCenterManager, self).get_queryset().filter(pre_center=False)


class Center(models.Model):
    """Center definitions. All centers should be mapped to sectors and zones"""
    zone = models.ForeignKey(Zone)
    center_name = models.CharField(max_length=50)
    center_category = models.CharField(max_length=1, choices=CENTER_CATEGORY_VALUES,
                                       default=CENTER_CATEGORY_VALUES[0][0])
    pre_center = models.BooleanField(default=False)
    parent_center = models.ForeignKey('self', null=True, blank=True)

    latitude = models.CharField(max_length=15, blank=True)
    longitude = models.CharField(max_length=15, blank=True)

    objects = models.Manager()
    main_centers = PreCenterManager()

    def __str__(self):
        if self.pre_center:
            try:
                return "(Pre) %s [%s] (%s)" % (self.center_name, self.parent_center.center_name,
                                               self.zone.zone_name)
            except:
                pass

        return "%s (%s)" % (self.center_name, self.zone.zone_name)

    class Meta:
        ordering = ['center_name']
        verbose_name = 'IPC Center'

    def clean(self):
        if self.pre_center:
            if not self.parent_center:
                raise ValidationError('Pre-centers must have a parent center')

            if self.parent_center.pre_center:
                raise ValidationError('Parent center cannot be a pre-center')

            if Center.objects.filter(parent_center=self).exists():
                raise ValidationError('This center is a parent center for one or more centers. Cannot make it a pre-center')
        else:
            if self.parent_center:
                raise ValidationError('Non pre-centers cannot have a parent center')

    def save(self, *args, **kwargs):
        self.center_name = _word_clean(self.center_name)
        super(Center, self).save(*args, **kwargs)


class IndividualRole(models.Model):
    """Definition for individual roles
    like 'Treasurer', 'Organizer' etc
    The role can be at center level, sector level
    or zone level
    """
    role_name = models.CharField(max_length=50, unique=True)
    role_level = models.CharField(max_length=2, choices=ROLE_LEVEL_CHOICES)
    role_remarks = models.TextField(blank=True)
    admin_role = models.BooleanField(default=False)

    def __str__(self):
        return "%s (%s)" %(self.role_name, self.get_role_level_display())

    def save(self, *args, **kwargs):
        self.role_name = _word_clean(self.role_name)
        super(IndividualRole, self).save(*args, **kwargs)

    class Meta:
        ordering = ['role_name', 'role_level']
        verbose_name = 'IPC Role'


class IndividualContactRoleCenter(models.Model):
    """ Maps individual contacts to individual roles.
    They always need to be mapped to a center
    """
    contact = models.ForeignKey(Contact)
    center = models.ForeignKey(Center)
    role = models.ForeignKey(IndividualRole)

    class Meta:
        ordering = ['contact', 'role', 'center']
        verbose_name = 'IPC center level contact role'

    def clean(self):
        try:
            if (self.role.get_role_level_display() != 'Center'):
                raise ValidationError("Only center level roles can be mapped to a center")

            existing_contact_roles = IndividualContactRoleCenter.objects.filter(contact=self.contact)
            center_role_combos = [(item.center, item.role) for item in existing_contact_roles]

            if ((self.center, self.role) in center_role_combos) and (not self.id):
                raise ValidationError("This role has already been mapped for this contact and center")
        except ObjectDoesNotExist:
            raise ValidationError("Need to choose both role and center")

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
        verbose_name = 'IPC zone level contact role'

    def clean(self):
        try:
            if (self.role.get_role_level_display() != 'Zone'):
                raise ValidationError("Only zone level roles can be mapped to a zone")

            existing_contact_roles = IndividualContactRoleZone.objects.filter(contact=self.contact)
            zone_role_combos = [(item.zone, item.role) for item in existing_contact_roles]

            if ((self.zone, self.role) in zone_role_combos) and (not self.id):
                raise ValidationError("This role has already been mapped for this contact and zone")
        except ObjectDoesNotExist:
            raise ValidationError('Need to choose both role and zone')

    def __str__(self):
        return "%s - %s - %s" % (self.contact.full_name, self.zone.zone_name,
                               self.role.role_name)


class IndividualContactRoleSector(models.Model):
    """ Maps individual contacts to individual roles.
    They always need to be mapped to a center
    """
    contact = models.ForeignKey(Contact)
    sector = models.ForeignKey(Sector)
    role = models.ForeignKey(IndividualRole)

    class Meta:
        ordering = ['contact', 'role', 'sector']
        verbose_name = 'IPC sector level contact role'

    def clean(self):
        if (self.role.get_role_level_display() != 'Sector'):
            raise ValidationError("Only sector level roles can be mapped to a sector")

        existing_contact_roles = IndividualContactRoleSector.objects.filter(contact=self.contact)
        sector_role_combos = [(item.sector, item.role) for item in existing_contact_roles]

        if ((self.sector, self.role) in sector_role_combos) and (not self.id):
            raise ValidationError("This role has already been mapped for this contact and sector")

    def __str__(self):
        return "%s - %s - %s" % (self.contact.full_name, self.sector.sector_name,
                               self.role.role_name)
