import os.path
from django.db import models
from django.utils.text import slugify
from contacts.models import Center


def _generate_profile_path(instance, filename):
    image_extension = os.path.splitext(filename)[-1]
    profile_picture_name = slugify(instance.full_name + " profile picture") + image_extension
    return os.path.join('profile_pictures', profile_picture_name)


# Create your models here.
class ItemMaster(models.Model):
    name = models.CharField(max_length=50)
    model_no = models.CharField(max_length=50)
    description = models.TextField("Description", blank=True)

    def __str__(self):
        return self.name


class CenterMaterial(models.Model):
    center = models.ForeignKey(Center)
    item = models.ForeignKey(ItemMaster)
    quantity = models.SmallIntegerField()
    STATUS_VALUES = (('ACTV', 'Active'),
                     ('DMGD', 'Damaged'),
                     ('LOST', 'Lost'),
                     ('LOAN', 'Loaned'))
    status = models.CharField(max_length=6, choices=STATUS_VALUES, blank=True)

    def __str__(self):
        return "%s - %s (%d)" % (self.center, self.item, self.quantity)


class CenterNotes(models.Model):
    center = models.ForeignKey(Center)
    note = models.TextField()
    create_timestamp = models.DateTimeField(auto_now_add=True)
    modify_timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "(%s)-%s" % (self.center, self.note[:25])


class TransMaster(models.Model):
    center = models.ForeignKey(Center)
    TRANS_VALUES = (('IKDN', 'In-Kind Donation'),
                    ('PURC', 'Cash Purchase'),
                    ('LEND', 'Lend'),
                    ('LOCL', 'Loan Closure'))# need to check
    trans_type = models.CharField(max_length=6, choices=TRANS_VALUES, blank=True)
    center = models.ForeignKey(Center)#, null=True, blank=True)  # make nullable
    description = models.TextField()
    #trans_date = models.DateTimeField(auto_now_add=True)
    total_cost = models.IntegerField("Total Cost", max_length=10)  # calculated, nullable for donations and loans
    create_timestamp = models.DateTimeField(auto_now_add=True)
    #modify_timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.trans_type


#Inkind or Purchase?
class TransDetail(models.Model):
    trans_master = models.ForeignKey(TransMaster)
    item = models.ForeignKey(ItemMaster)
    quantity = models.IntegerField("Quantity", max_length=3)
    unit_cost = models.IntegerField("Unit Cost", max_length=10)


# Cash Purchase
class BillInfo(models.Model):
    trans_master = models.OneToOneField(TransMaster, blank=True, null=True)
    bill_no = models.CharField(max_length=20)
    supplier_name = models.CharField(max_length=50)
    bill_date = models.DateTimeField(auto_now_add=True)
    bill_soft_copy = models.FileField(upload_to=_generate_profile_path, blank=True)# If bill is PDF? FileField?
    payment_remark = models.TextField()


# In-Kind Donation
class Donor(models.Model):
    trans_master = models.OneToOneField(TransMaster, blank=True, null=True)
    first_name = models.CharField("first Name", max_length=50)
    last_name = models.CharField("last Name", max_length=50)
    mobile = models.CharField("mobile", max_length=15, blank=True)
    email = models.EmailField("Email", max_length=50)
    donated_date = models.DateTimeField(auto_now_add=True) # diff from trans_date?
    remark = models.TextField()


# Loan
class LoanInfo(models.Model):
    trans_master = models.OneToOneField(TransMaster, blank=True, null=True)
    destination_center = models.ForeignKey(Center)
    loan_date = models.DateTimeField(auto_now_add=True)
    STATUS_VALUES = (('LOAN', 'Loaned'),
                    ('LOCL', 'Loan Closed'),
                    ('LOPR', 'Loan - Partially Returned')
                    ('LCPR', 'Loan Closed - Partially Returned'))# need to check
    trans_type = models.CharField(max_length=6, choices=STATUS_VALUES, blank=True)

#loan status
#Assumptions for scensrios
