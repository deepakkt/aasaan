import os.path
#dkt - can be removed

from django.db import models
from django.utils.text import slugify
#dkt - slugify is not needed. can be removed

from contacts.models import Center

#dkt - all Textfields need to use markdown. Check schedules model and admin
# to see how it is implemented. I will later explain what it is and why
# it is required.


def _generate_profile_path(instance, filename):
    image_extension = os.path.splitext(filename)[-1]
    profile_picture_name = slugify(instance.full_name + " profile picture") + image_extension
    return os.path.join('profile_pictures', profile_picture_name)
#dkt this function is not relevant. can be removed

# Create your models here.
class ItemMaster(models.Model):
    name = models.CharField(max_length=50)
    model_no = models.CharField(max_length=50, blank=True)
    description = models.TextField()

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


class TransactionMaster(models.Model):
    center = models.ForeignKey(Center)
    TRANSACTION_VALUES = (('IKDN', 'In-Kind Donation'),
                          ('PURC', 'Cash Purchase'),
                          ('LEND', 'Lend'),
                          ('LOCL', 'Loan Closure'))
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_VALUES, blank=True)
    center = models.ForeignKey(Center)
    description = models.TextField()
    total_cost = models.IntegerField()
    create_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.trans_type


# Inkind or Purchase
class TransactionDetail(models.Model):
    transaction_master = models.ForeignKey(TransactionMaster)
    item = models.ForeignKey(ItemMaster)
    quantity = models.SmallIntegerField()
    unit_cost = models.IntegerField()

    def __str__(self):
        return "%s - %s (%d)" % (self.item, self.quantity, self.unit_cost)


# Cash Purchase
class BillInfo(models.Model):
    transaction_master = models.OneToOneField(TransactionMaster)
    bill_no = models.CharField(max_length=20)
    supplier_name = models.CharField(max_length=50)
    bill_date = models.DateTimeField(auto_now_add=True)
    bill_soft_copy = models.FileField(upload_to=_generate_profile_path, blank=True)
    payment_remark = models.TextField()

    def __str__(self):
        return "%s (%s)" % (self.bill_no, self.supplier_name)


# In-Kind Donation
class DonorInfo(models.Model):
    transaction_master = models.OneToOneField(TransactionMaster)
    first_name = models.CharField("first Name", max_length=50)
    last_name = models.CharField("last Name", max_length=50, blank=True)
    mobile = models.CharField("mobile", max_length=15, blank=True)
    email = models.EmailField("Email", max_length=50, blank=True)
    donated_date = models.DateTimeField(auto_now_add=True)
    remark = models.TextField()

    def __str__(self):
        return "%s (%s)" % (self.first_name, self.mobile)

    class Meta:
        ordering = ['first_name', 'last_name']
        verbose_name = 'Donor Contact'


# LoanInfo
class LoanInfo(models.Model):
    transaction_master = models.OneToOneField(TransMaster)
    destination_center = models.ForeignKey(Center)
    loan_date = models.DateTimeField(auto_now_add=True)
    STATUS_VALUES = (('LOND', 'Loaned'),
                     ('LOCL', 'Loan Closed'),
                     ('LOPR', 'Loan - Partially Returned')
                     ('LCPR', 'Loan Closed - Partially Returned'))  # need to check
    loan_status = models.CharField(max_length=6, choices=STATUS_VALUES, blank=True)

    def __str__(self):
        return "%s (%s)" % (self.destination_center, self.loan_status)

# loan status
# Assumptions for scensrios
