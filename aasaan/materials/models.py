import os.path
from django.db import models
from django.utils.text import slugify
from contacts.models import Center


# Create your models here.
class ItemMaster(models.Model):
    name = models.CharField("Name", max_length=50)
    description = models.CharField("Description", max_length=50)
    model_no = models.CharField("Model No", max_length=50)
    remarks = models.TextField(max_length=500, blank=True)


class CenterMaterial(models.Model):
    contact = models.ForeignKey(Contact)
    itemMaster = models.ForeignKey(ItemMaster)
    quantity = models.IntegerField("Quantity", max_length=3)
    STATUS_VALUES = (('ACT', 'Active'),
                     ('DMGD', 'Damaged'),
                     ('LOST', 'Lost'),
                     ('LOAN', 'Loaned'))
    status = models.CharField(max_length=6, choices=STATUS_VALUES, blank=True)


class CenterMaterialNotes(models.Model):
    centerMaterial = models.ForeignKey(CenterMaterial)
    note = models.TextField(max_length=500)
    create_timestamp = models.DateTimeField(auto_now_add=True)
    modify_timestamp = models.DateTimeField()


class ItemTransMaster(models.Model):
    TRANS_VALUES = (('IKD', 'In-Kind Donation'),
                    ('PURC', 'Cash Purchase'))
    trans_type = models.CharField(max_length=6, choices=TRANS_VALUES, blank=True)
    description = models.CharField("Description", max_length=50)
    trans_date = models.DateTimeField()
    center = models.ForeignKey(Center)
    total_cost = models.IntegerField("Total Cost", max_length=10)


class ItemTransDetail(models.Model):
    itemTransMaster = models.ForeignKey(ItemTransMaster)
    itemMaster = models.ForeignKey(ItemMaster)
    quantity = models.IntegerField("Quantity", max_length=3)
    unit_cost = models.IntegerField("Unit Cost", max_length=10)
