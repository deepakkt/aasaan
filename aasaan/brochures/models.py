from django.db import models
from django_markdown.models import MarkdownField
from django.utils.text import slugify
from contacts.models import Zone
from schedulemaster.models import ProgramSchedule, LanguageMaster, ProgramMaster
from django.core.exceptions import ValidationError
from django.conf import settings
import os, os.path
from PIL import Image
import datetime


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(active=True)


class StockPointMaster(models.Model):
    name = models.CharField(max_length=50)
    zone = models.ForeignKey(Zone)
    active = models.BooleanField(default=True)
    description = MarkdownField(blank=True)

    objects = models.Manager()
    active_objects = ActiveManager()

    def __str__(self):
        return "%s - %s" % (self.name, self.zone)

    class Meta:
        verbose_name = 'Stock Point Master'
        ordering = ['zone', 'name']


class StockPointAddress(models.Model):
    stock_point = models.ForeignKey(StockPointMaster)
    address_line_1 = models.CharField(max_length=100, blank=True)
    address_line_2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    state = models.CharField(max_length=25, blank=True)
    country = models.CharField(max_length=25, blank=True)
    contact_number1 = models.CharField("contact Number1", max_length=15, blank=True)
    contact_number2 = models.CharField("contact Number2", max_length=15, blank=True)


def _brochure_image_path(instance, filename):
    image_extension = os.path.splitext(filename)[-1]
    brochure_image = slugify(
        instance.name + instance.version + instance.language.name + "brochure image") + image_extension
    return os.path.join('brochure_image', brochure_image)


class BrochureMaster(models.Model):
    name = models.CharField(max_length=50)
    version = models.CharField(max_length=10, blank=True)
    language = models.ForeignKey(LanguageMaster, default=1)
    active = models.BooleanField(default=True)
    brochure_image = models.ImageField(upload_to=_brochure_image_path, blank=True)
    description = MarkdownField(blank=True)

    objects = models.Manager()
    active_objects = ActiveManager()

    def __init__(self, *args, **kwargs):
        super(BrochureMaster, self).__init__(*args, **kwargs)

        # setup a function to give expanded status values
        # instead of the short code stored in database
        self.__display_func = lambda x: 'get_' + x + '_display'

        # store old values of following fields to track changes
        self.old_field_list = ['__old_' + x.name for x in self._meta.fields]
        self.field_list = [x.name for x in self._meta.fields]

        self.__reset_changed_values()

    # set __old_* fields to current model fields
    # use it for first time init or after comparisons for
    # changes and actions are all done
    def __reset_changed_values(self):
        for each_field in self.field_list:
            try:
                setattr(self, '__old_' + each_field, getattr(self, self.__display_func(each_field))())
            except AttributeError:
                setattr(self, '__old_' + each_field, getattr(self, each_field))

    def __str__(self):
        return "%s %s (%s)" % (self.name, self.version, self.language)

    def __changed_fields(self):
        changed_fields = {}
        for old_field, new_field in zip(self.old_field_list, self.field_list):
            try:
                new_field_value = getattr(self, self.__display_func(new_field))()
            except AttributeError:
                new_field_value = getattr(self, new_field)
            old_field_value = getattr(self, old_field)

            if new_field_value != getattr(self, old_field):
                changed_fields[new_field] = (old_field_value,
                                             new_field_value)
        return changed_fields

    def get_brochure_image(self):
        image_style = 'style="width:50px; height:50px"'
        if self.brochure_image != "":
            image_url = "%s/%s" % (settings.MEDIA_URL, self.brochure_image)
            image_html = '<img src="%s" %s/>' % (image_url, image_style)
            image_hyperlink = '<a href="%s">%s</a>' % (image_url, image_html)
            return image_hyperlink
        else:
            no_picture = "profile_pictures/no-photo.jpg"
            image_url = "%s/%s" % (settings.MEDIA_URL, no_picture)
            image_html = '<img src="%s" %s/>' % (image_url, image_style)
            return image_html

    get_brochure_image.short_description = "Brochure picture"
    get_brochure_image.allow_tags = True

    def brochure_image_display(self):
        image_style = 'style="width:240px; height:300px"'
        if self.brochure_image != "":
            image_url = "%s/%s" % (settings.MEDIA_URL, self.brochure_image)
            image_html = '<img src="%s" %s/>' % (image_url, image_style)
            image_hyperlink = '<a href="%s">%s</a>' % (image_url, image_html)
            return image_hyperlink
        else:
            return "<strong>No brochure picture available</strong>"

    brochure_image_display.short_description = "Brochure picture"
    brochure_image_display.allow_tags = True

    def save(self, *args, **kwargs):
        # get a map of field changes
        changed_fields = self.__changed_fields()
        super(BrochureMaster, self).save(*args, **kwargs)
        if 'brochure_image' in changed_fields:
            old_picture_file = changed_fields['brochure_image'][0]
            if old_picture_file:
                old_picture_file.file.close()
                os.remove(old_picture_file.file.name)

            if self.brochure_image:
                brochure_img = Image.open(self.brochure_image.file.name)
                resized_image = brochure_img.resize((595, 842))
                resized_image.save(self.brochure_image.file.name)
        self.__reset_changed_values()

    class Meta:
        verbose_name = 'Brochure Master'
        ordering = ['name']
        unique_together = ('name', 'version', 'language')


class StockPoint(StockPointMaster):
    class Meta:
        verbose_name = 'Materials in Stock Point'
        proxy = True


class Brochures(models.Model):
    item = models.ForeignKey(BrochureMaster)
    stock_point = models.ForeignKey(StockPointMaster)
    quantity = models.SmallIntegerField()
    remarks = models.CharField(max_length=100, blank=True)
    STATUS_VALUES = (('ACTV', 'Active'),
                     ('DMGD', 'Damaged'),
                     ('LOST', 'Lost'),
                     )
    status = models.CharField(max_length=6, choices=STATUS_VALUES, blank=True,
                              default=STATUS_VALUES[0][0])

    def __str__(self):
        return ""

    class Meta:
        verbose_name = "brochure"
        verbose_name_plural = "brochures"


class StockPointNote(models.Model):
    stock_point = models.ForeignKey(StockPoint)
    note = MarkdownField()
    note_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.stock_point, self.note)

    class Meta:
        ordering = ['-note_timestamp']
        verbose_name = 'Stock Point & Materials note'
        verbose_name_plural = 'notes about Stock Point & Materials'


class BrochureSet(models.Model):
    name = models.CharField(max_length=50)
    remarks = models.CharField(max_length=100, blank=True)
    program = models.ForeignKey(ProgramMaster, blank=True, null=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = "Brochure Set"
        verbose_name_plural = "Brochure Sets"


class BrochureSetItem(models.Model):
    brochure_set = models.ForeignKey(BrochureSet)
    item = models.ForeignKey(BrochureMaster)
    quantity = models.SmallIntegerField()


class BrochuresTransaction(models.Model):
    TRANSFER_TYPE_VALUES = (('ABSP', 'Add Brochures to Stock Point'),
                            ('BLSP', 'Brochures Lost/Damaged in a Stock Point'),
                            ('PRSP', 'Printer to Stock Point'),
                            ('SPSC', 'Stock Point to Schedule'),
                            ('SCSP', 'Schedule to Stock Point'),
                            ('SPSP', 'Stock Point to Stock Point'),
                            ('SPGT', 'Stock Point to Guest'),)
    transfer_type = models.CharField('transaction type', max_length=6, choices=TRANSFER_TYPE_VALUES, blank=True,
                                     default='SPSP')
    STATUS_VALUES = (('NEW', 'Transfer Initiated'),
                     ('IT', 'In Transit'),
                     ('DD', 'Delivered'),
                     ('TC', 'Cancelled'),
                     ('LOST', 'Lost/Damaged'),
                     ('CLS', 'Closed'),)
    status = models.CharField(max_length=6, choices=STATUS_VALUES, blank=True,
                              default=STATUS_VALUES[0][0])
    brochure_set = models.ForeignKey(BrochureSet, blank=True, null=True)

    source_printer = models.CharField(max_length=100, blank=True, null=True)
    source_stock_point = models.ForeignKey(StockPointMaster, blank=True, null=True)
    source_program_schedule = models.ForeignKey(ProgramSchedule, blank=True, null=True)
    destination_stock_point = models.ForeignKey(StockPointMaster, related_name='destination_sp', blank=True, null=True)
    destination_program_schedule = models.ForeignKey(ProgramSchedule, related_name='destination_sch', blank=True,
                                                     null=True)
    guest_name = models.CharField(max_length=100, blank=True, null=True)
    guest_phone = models.CharField(max_length=15, blank=True, null=True)
    guest_email = models.EmailField(max_length=50, blank=True, null=True)
    transaction_status = models.CharField(max_length=15, blank=True, null=True, default='NEW')
    transaction_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return "%s, %s - %s" % (self.get_transfer_type_display(), self.source(), self.destination())

    def clean(self):
        if not self.transfer_type=='ABSP' and not self.transfer_type=='BLSP':
            if not self.id and self.status=='DD' or self.status=='TC' or self.status=='LOST' or self.status=='CLS':
                raise ValidationError("New entry can not be created with %s status" % self.get_status_display())
        if self.transfer_type=='ABSP' or self.transfer_type=='BLSP':
            if not self.source_stock_point:
                raise ValidationError("Please enter stock point")
        if self.transfer_type == 'PRSP':
            if not self.source_printer:
                raise ValidationError("Please enter source printer")
            if not self.destination_stock_point:
                raise ValidationError("Please enter destination stock point")
        if self.transfer_type == 'SPSC':
            if not self.source_stock_point:
                raise ValidationError("Please enter source stock point")
            if not self.destination_program_schedule:
                raise ValidationError("Please enter destination Program Schedule")
        if self.transfer_type == 'SCSP':
            if not self.source_program_schedule:
                raise ValidationError("Please enter source Program Schedule")
            if not self.destination_stock_point:
                raise ValidationError("Please enter destination stock point")
        if self.transfer_type == 'SPSP':
            if not self.destination_stock_point or not self.source_stock_point:
                raise ValidationError("Source and destination stock points needs to be selected.")
        if self.transfer_type == 'SPGT':
            if not self.source_stock_point:
                raise ValidationError("Please enter source stock point")
            if not self.guest_name:
                raise ValidationError("Please enter Guest name")

    def save(self, *args, **kwargs):
        if not self.id:
            new_entry = True
            if self.transfer_type=='ABSP' or self.transfer_type=='BLSP':
                self.status = 'CLS'
        else:
            new_entry = False
            old_status = BrochuresTransaction.objects.get(pk=self.id).get_status_display()
            new_status = self.get_status_display()
        self.transaction_status = 'OLD'
        super(BrochuresTransaction, self).save(*args, **kwargs)
        transfer_note = BroucherTransferNote()
        transfer_note.brochure_transfer = self
        now = datetime.datetime.now()
        if not new_entry:
            if (old_status != new_status) and (old_status != ""):
                transfer_note.note = "Automatic Log: Status of %s changed from '%s' to '%s' at '%s'" % \
                                     (self.transfer_type, old_status, new_status, now)
                transfer_note.save()
        else:
            transfer_note.note = "Automatic Log: New transfer created with status '%s' at '%s'" % \
                                 (self.get_status_display(), now)
            transfer_note.save()

    def source(self):
        if self.transfer_type == 'PRSP':
            return self.source_printer
        elif self.transfer_type == 'SCSP':
            return self.source_program_schedule.__str__()[:35]
        else:
            return self.source_stock_point

    def destination(self):
        if self.transfer_type == 'ABSP' or self.transfer_type == 'BLSP':
            return 'Not Applicable'
        elif self.transfer_type == 'SPSC':
            return self.destination_program_schedule.__str__()[:35]
        elif self.transfer_type == 'SPGT':
            return self.guest_name
        else:
            return self.destination_stock_point


class Meta:
    verbose_name = "Brochures Transfer"
    verbose_name_plural = "Brochures Transfers"


class BroucherTransferNote(models.Model):
    brochure_transfer = models.ForeignKey(BrochuresTransaction)
    note = MarkdownField()
    note_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.brochure_transfer, self.note)

    class Meta:
        ordering = ['-note_timestamp']
        verbose_name = 'brochure transfer note'
        verbose_name_plural = 'notes about brochure transfer'


class BrochuresTransactionItem(models.Model):
    brochures = models.ForeignKey(BrochureMaster)
    brochures_transfer = models.ForeignKey(BrochuresTransaction)
    sent_quantity = models.SmallIntegerField('quantity')
    received_quantity = models.SmallIntegerField(null=True, blank=True)

    def __str__(self):
        return ""


class BrochuresShipment(models.Model):
    brochures_transfer = models.ForeignKey(BrochuresTransaction)
    sent_from = models.CharField(max_length=50, blank=True)
    sent_to = models.CharField(max_length=50, blank=True)
    sent_date = models.DateField(blank=True)
    received_date = models.DateField(blank=True)
    courier_vendor = models.CharField(max_length=50, blank=True)
    courier_no = models.CharField(max_length=50, blank=True)
    STATUS_VALUES = (('CS', 'Courier Sent'),
                     ('NEW', 'Not Initiated'),
                     ('CR', 'Received'),
                     ('IT', 'In Transit'),)
    courier_status = models.CharField(max_length=3, choices=STATUS_VALUES, blank=True,
                                      default='NEW')
    remarks = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return "%s - %s" % (self.sent_from, self.sent_to)

    class Meta:
        verbose_name = 'Brochure Shipment'
        ordering = ['sent_date']
