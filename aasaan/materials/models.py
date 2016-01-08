from django.db import models
from contacts.models import Center
from django_markdown.models import MarkdownField


# Create your models here.

class MaterialsCenter(Center):

    def item_count(self):
        center_items_count = CenterMaterial.objects.filter(center=self).count()
        return center_items_count

    class Meta:
        proxy = True
        verbose_name = 'Material for Center'


class ItemMaster(models.Model):
    name = models.CharField(max_length=50)
    model_no = models.CharField(max_length=50, blank=True)
    description = MarkdownField(blank=True)

    def __str__(self):
        if self.model_no:
            return "%s (%s)" % (self.name, self.model_no)
        else:
            return self.name

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        # clean up the name of all redundant spaces and title case it
        self.name = ' '.join([each_word if each_word.upper() == each_word
                              else each_word.title()
                              for each_word in self.name.split()])

        super(ItemMaster, self).save(*args, **kwargs)


class CenterMaterial(models.Model):
    center = models.ForeignKey(Center)
    item = models.ForeignKey(ItemMaster)
    quantity = models.SmallIntegerField()
    STATUS_VALUES = (('ACTV', 'Active'),
                     ('DMGD', 'Damaged'),
                     ('LOST', 'Lost'),
                     ('LOAN', 'Loaned'),)
    status = models.CharField(max_length=6, choices=STATUS_VALUES, blank=True,
                              default='ACTV')

    def __str__(self):
        return "%s - %s (%d)" % (self.center, self.item, self.quantity)


class CenterItemNotes(models.Model):
    center = models.ForeignKey(Center)
    note = MarkdownField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "(%s)-%s" % (self.center, self.note[:25])


class Transaction(models.Model):
    center = models.ForeignKey(Center)
    TRANSACTION_VALUES = (('IKDN', 'In-Kind Donation'),
                          ('PURC', 'Cash Purchase'),
                          ('LOAN', 'Loan'),
                          ('LOCL', 'Loan Closure'))
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_VALUES, blank=True)
    transaction_date = models.DateField(auto_now_add=True)
    description = MarkdownField(blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s (%s) - %s" % (self.center, self.transaction_type,
                                 self.transaction_date.isoformat())

    class Meta:
        ordering = ['-transaction_date', 'transaction_type']


class TransactionItems(models.Model):
    transaction = models.ForeignKey(Transaction)
    item = models.ForeignKey(ItemMaster)
    quantity = models.SmallIntegerField()
    unit_cost = models.DecimalField(default=0, max_digits=9, decimal_places=2)

    def __str__(self):
        return "%s - %s" % (self.item, self.quantity)


class TransactionNotes(models.Model):
    transaction = models.ForeignKey(Transaction)
    note = MarkdownField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s - Note #%d" % (self.transaction, self.id)

    class Meta:
        ordering = ['-created']


# Cash Purchase
class PurchaseTransaction(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE,
                                       primary_key=True)
    invoice_number = models.CharField(max_length=50)
    supplier_name = models.CharField(max_length=100)
    bill_date = models.DateTimeField(auto_now_add=True)
    bill_soft_copy = models.FileField(blank=True)
    total_cost = models.DecimalField(default=0, max_digits=9, decimal_places=2)
    payment_remarks = MarkdownField(blank=True)

    def __str__(self):
        return self.transaction


# In-Kind Donation
class DonationTransaction(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE,
                                       primary_key=True)

    donor_first_name = models.CharField(max_length=50)
    donor_last_name = models.CharField(max_length=50, blank=True)
    donor_mobile = models.CharField(max_length=15, blank=True)
    donor_email = models.EmailField(max_length=50, blank=True)
    donated_date = models.DateField(auto_now_add=True)

    donation_remarks = MarkdownField(blank=True)

    def __str__(self):
        return self.transaction


# LoanInfo
class LoanTransaction(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE,
                                       primary_key=True)

    destination_center = models.ForeignKey(Center)
    loan_date = models.DateField(auto_now_add=True)
    STATUS_VALUES = (('LOND', 'Loaned'),
                     ('LOCL', 'Loan Closed'),
                     ('LOPR', 'Loan - Partially Returned'),
                     ('LCPR', 'Loan Closed - Partially Returned'))  # need to check
    loan_status = models.CharField(max_length=6, choices=STATUS_VALUES, blank=True)

    def __str__(self):
        return self.transaction
