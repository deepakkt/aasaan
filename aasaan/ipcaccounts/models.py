from django.db import models
from django.contrib.postgres.fields import JSONField
from contacts.models import Center, Contact, IndividualContactRoleZone
from schedulemaster.models import ProgramSchedule
from django_markdown.models import MarkdownField
import json
from config.models import Configuration


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


class AccountsMaster(models.Model):

    ACCOUNT_TYPE_VALUES = (('TA', 'Teachers Accounts'),
                           ('CA', 'Classes Accounts'),
                           ('OA', 'Other Accounts'),

    )
    account_type = models.CharField(max_length=6, choices=ACCOUNT_TYPE_VALUES,
                                       default=ACCOUNT_TYPE_VALUES[1][0])

    entity_name = models.ForeignKey(EntityMaster)
    center = models.ForeignKey(Center, blank=True, null=True)
    teacher = models.ForeignKey(Contact, blank=True, null=True)
    budget_code = models.CharField(max_length=100, blank=True)
    program_schedule = models.ForeignKey(ProgramSchedule, blank=True, null=True)
    tracking_no = models.CharField(max_length=100, blank=True)
    approval_sent_date = models.DateField(blank=True, null=True)
    approved_date = models.DateField(blank=True, null=True)
    APPROVAL_STATUS_VALUES = (('SENT', 'Sent for Approval'), ('NOT', 'Not Approved'),
                        ('MAIL', 'Mail Approved'),
                      ('PHY', 'Physically Approved'),
                      )
    approval_status = models.CharField(max_length=6, choices=APPROVAL_STATUS_VALUES, blank=True,
                                    default=APPROVAL_STATUS_VALUES[0][0])
    finance_submission_date = models.DateField(blank=True, null=True)
    movement_sheet_no = models.CharField(max_length=100, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    utr_no = models.CharField('UTR NO', max_length=100, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    active_objects = ActiveManager()

    def save(self, *args, **kwargs):

        if self.pk is None:
            cft = Configuration.objects.get(configuration_key='IPC_ACCOUNTS_TRACKING_CONST')
            data = json.loads(cft.configuration_value)
            if self.account_type == 'CA':
                key = data[self.center.zone.zone_name]['ca_key']
                prefix = data[self.center.zone.zone_name]['prefix']
                tracking_no = 'CA' + prefix + str(key).zfill(10)
                data[self.center.zone.zone_name]['ca_key'] = key + 1
                cft.configuration_value = json.dumps(data)
                cft.save()

            if self.account_type == 'TA':
                contact_role_zone = IndividualContactRoleZone.objects.get(contact=self.teacher)
                key = data[contact_role_zone.zone.zone_name]['ta_key']
                prefix = data[contact_role_zone.zone.zone_name]['prefix']
                tracking_no = 'TA'+ prefix + str(key).zfill(10)
                data[contact_role_zone.zone.zone_name]['ta_key'] = key + 1
                cft.configuration_value = json.dumps(data)
                cft.save()

        self.tracking_no = tracking_no
        super(AccountsMaster, self).save(*args, **kwargs)

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


class VoucherDetails(models.Model):
    accounts_master = models.ForeignKey(AccountsMaster)
    tracking_no = models.CharField(max_length=100, blank=True)
    nature_of_voucher = models.ForeignKey(VoucherMaster)
    voucher_status = models.ForeignKey(VoucherStatusMaster)
    voucher_date = models.DateField()
    head_of_expenses = models.CharField(max_length=100, blank=True)
    expenses_description = models.CharField(max_length=100, blank=True)
    party_name = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    delayed_approval =  models.BooleanField(default=True)

    class Meta:
        ordering = ['nature_of_voucher',]
        verbose_name = 'Voucher'


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

