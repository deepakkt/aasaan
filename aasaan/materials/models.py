import os.path

from django.db import models
from django.utils.text import slugify
from contacts.models import Center

def _generate_profile_path(instance, filename):
    image_extension = os.path.splitext(filename)[-1]
    profile_picture_name = slugify(instance.full_name + " profile picture") + image_extension
    return os.path.join('profile_pictures', profile_picture_name)


# Create your models here.
class Materials(models.Model):
    """Materials model"""
    MATERIAL_VALUES = (('PJ', 'Projector'),
                       ('SC', 'Screen'),
                       ('AV', 'Audio'),
                       ('VD', 'Video'),
                       ('CP', 'Carpet'),
                       ('SP', 'Sadhguru Photo'),
                       ('GS', 'Gurupooja Set'))

    material_type = models.CharField(max_length=2, choices=MATERIAL_VALUES)

    name = models.CharField("Name", max_length=50)

    model_no = models.CharField("Model No", max_length=50)

    purchase_date = models.DateField("purchase date", null=True, blank=True)

    PURCHASE_VALUES = (('AP', 'Ashram Purchase'),
                       ('SELF', 'Own Purchase'),
                       ('IK', 'In Kind Donation'))

    purchase_type = models.CharField(max_length=2, choices=PURCHASE_VALUES)

    STATUS_VALUES = (('ACT', 'Active'),
                     ('INACTV', 'Inactive'))

    status = models.CharField(max_length=6, choices=STATUS_VALUES, blank=True)
    unit = models.IntegerField("Quantity", max_length=10)
    unit_price = models.IntegerField("Unit price", max_length=10)
    remarks = models.TextField(max_length=500, blank=True)


class Brochure(models.Model):
    """Paper Materials model"""

    item_name = models.CharField("Item Name", max_length=50)
    item_type = models.CharField("Item Type", max_length=50)
    version = models.CharField("Version No", max_length=2)
    unit = models.IntegerField("Quantity", max_length=10)
    unit_price = models.IntegerField("Unit price", max_length=10)
    remarks = models.TextField(max_length=500, blank=True)
    STATUS_VALUES = (('ACT', 'Active'),
                     ('INACTV', 'Inactive'))
    status = models.CharField(max_length=6, choices=STATUS_VALUES, blank=True)


class Sponsor(models.Model):
    materials = models.ForeignKey(Materials)
    first_name = models.CharField("first Name", max_length=50)
    last_name = models.CharField("last Name", max_length=50)
    mail = models.EmailField("Email", max_length=50)
    phone = models.CharField("Mobile", max_length=15, blank=True)


class Inventory(models.Model):
    materials = models.ForeignKey(Center)
    first_name = models.CharField("Inventory Name", max_length=50)
    remarks = models.TextField(max_length=500, blank=True)


class InboundOutbound(models.Model):

    brochure = models.ForeignKey(Brochure)
    source = models.CharField("source Name", max_length=50)
    destination = models.CharField("destination Name", max_length=50)
    sent_date = models.DateField("sent date", null=True, blank=True)
    received_date = models.DateField("received date", null=True, blank=True)
    unit = models.IntegerField("Quantity", max_length=10)
    remarks = models.TextField(max_length=500, blank=True)
    STATUS_VALUES = (('RR', 'Request Received'),
                     ('SH', 'Shipped'),
                     ('DD', 'Delivered'))
    status = models.CharField(max_length=6, choices=STATUS_VALUES, blank=True)


