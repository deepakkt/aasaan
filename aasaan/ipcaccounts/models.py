from django.db import models
from django.contrib.postgres.fields import JSONField
from contacts.models import Center, Contact
from schedulemaster.models import ProgramSchedule
from django_markdown.models import MarkdownField
# Create your models here.


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(active=True)


class VoucherMaster(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()

    def __str__(self):
        return "%s" % self.name


class EntityMaster(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()

    def __str__(self):
        return "%s" % self.name


class VoucherStatusMaster(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()

    def __str__(self):
        return "%s" % self.name


def increment_tracking_number():
    last_account = AccountsMaster.objects.all().order_by('id').last()
    if not last_account:
         return 'ACC0001'
    tracking_no = last_account.tracking_no
    tracking_int = int(tracking_no.split('ACC')[-1])
    new_tracking_int = tracking_int + 1
    new_tracking_no = 'ACC' + str(new_tracking_int)
    return new_tracking_no


class AccountsMaster(models.Model):

    ACCOUNT_TYPE_VALUES = (('TEACH', 'Teachers Accounts'),
                              ('CLASS', 'Class Accounts'),
                              ('OTHER', 'Other Accounts'),
                              )
    account_type = models.CharField(max_length=6, choices=ACCOUNT_TYPE_VALUES,
                                       default=ACCOUNT_TYPE_VALUES[1][0])
    tracking_no = models.CharField(max_length=100,default=increment_tracking_number, blank=True)
    voucher_status = models.ForeignKey(VoucherStatusMaster)
    voucher_date = models.DateField()
    nature_of_voucher = models.ForeignKey(VoucherMaster)
    entity_name = models.ForeignKey(EntityMaster)
    center = models.ForeignKey(Center, null=True)
    teacher = models.ForeignKey(Contact, null=True)
    head_of_expenses = models.CharField(max_length=100, blank=True)
    program_schedule = models.ForeignKey(ProgramSchedule, null=True)
    budget_code = models.CharField(max_length=100, blank=True)
    expenses_description = models.CharField(max_length=100, blank=True)
    party_name = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    approval_sent_date = models.DateField(null=True)
    approved_date = models.DateField(null=True)
    APPROVAL_STATUS_VALUES = (('SENT', 'Sent for Approval'), ('NOT', 'Not Approved'),
                        ('MAIL', 'Mail Approved'),
                      ('PHY', 'Physically Approved'),
                      )
    approval_status = models.CharField(max_length=6, choices=APPROVAL_STATUS_VALUES, blank=True,
                                    default=APPROVAL_STATUS_VALUES[0][0])
    finance_submission_date = models.DateField(null=True)
    movement_sheet_no = models.CharField(max_length=100, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    utr_no = models.CharField('UTR NO', max_length=100, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    active_objects = ActiveManager()

    def __str__(self):
        return "%s - %s - %s - %s" % (self.entity_name, self.voucher_date, self.center if self.center else self.teacher, self.voucher_status)


class CourierDetails(models.Model):
    accounts_master = models.ForeignKey(AccountsMaster)
    source = models.CharField(max_length=100, null=True, blank=True)
    destination = models.CharField(max_length=100, null=True, blank=True)
    agency = models.CharField(max_length=100, null=True, blank=True)
    tracking_no = models.CharField(max_length=100, null=True, blank=True)
    sent_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    remarks = MarkdownField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class TransactionNotes(models.Model):
    accounts_master = models.ForeignKey(AccountsMaster)
    note = MarkdownField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s - Note #%d" % (self.accounts_master, self.id)

    class Meta:
        ordering = ['-created']