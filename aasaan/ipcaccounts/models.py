from django.db import models
from contacts.models import Center, Contact, IndividualContactRoleZone, Zone
from schedulemaster.models import ProgramSchedule
from django_markdown.models import MarkdownField
import json
from config.models import Configuration, SmartModel
from django.core.exceptions import ValidationError
from smart_selects.db_fields import GroupedForeignKey
from django.db.models import Sum


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(active=True)


class VoucherMaster(models.Model):
    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()

    def __str__(self):
        return "%s" % self.name


class EntityMaster(models.Model):
    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()

    def __str__(self):
        return "%s" % self.name


class RCOVoucherStatusMaster(models.Model):
    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    objects = models.Manager()
    active_objects = ActiveManager()

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'RCO Voucher Status Master'


class AccountType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    objects = models.Manager()
    active_objects = ActiveManager()

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'NP Vouchers Type Master'


class AccountTypeMaster(models.Model):
    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    objects = models.Manager()
    active_objects = ActiveManager()

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'Account Type Master'


class NPVoucherStatusMaster(models.Model):
    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    type = models.ForeignKey(AccountType)

    objects = models.Manager()
    active_objects = ActiveManager()

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'NP Voucher Status Master'


class ExpensesTypeMaster(models.Model):
    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    type = models.ForeignKey(AccountTypeMaster)

    objects = models.Manager()
    active_objects = ActiveManager()

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'Expense master'


class RCOAccountsMaster(SmartModel):

    account_type = models.ForeignKey(AccountTypeMaster)
    entity_name = models.ForeignKey(EntityMaster)
    zone = models.ForeignKey(Zone, blank=True, null=True)
    teacher = models.ForeignKey(Contact, blank=True, null=True)
    budget_code = models.CharField(max_length=100, blank=True)
    program_schedule = GroupedForeignKey(ProgramSchedule, 'program', blank=True, null=True)
    STATUS_VALUES = (('AO', 'Open'),
                     ('CL', 'Closed'),
                     ('CA', 'Cancelled'))

    status = models.CharField(max_length=2, choices=STATUS_VALUES,
                              default=STATUS_VALUES[0][0])

    objects = models.Manager()
    active_objects = ActiveManager()

    def rco_status(self):
        vd = VoucherDetails.objects.filter(accounts_master=self).order_by('modified')
        if len(vd) >= 1:
            v = vd[len(vd)-1]
            return v.nature_of_voucher.name + ' : ' + v.voucher_status.name
        else:
            return ''

    def np_status(self):
        vd = VoucherDetails.objects.filter(accounts_master=self).order_by('modified')
        if len(vd) >= 1:
            v = vd[len(vd) - 1]
            tmp = ''
            if v.np_voucher_status:
                tmp = v.np_voucher_status.name
            return tmp
        else:
            return ''

    def total_amount(self):
        total_amount = VoucherDetails.objects.filter(accounts_master=self).aggregate(Sum('amount'))['amount__sum']
        return total_amount

    def total_no_vouchers(self):
        items_count = VoucherDetails.objects.filter(accounts_master=self).count()
        return items_count

    def last_modified(self):
        vd = VoucherDetails.objects.filter(accounts_master=self).order_by('modified')
        if len(vd)>=1:
            return vd[len(vd)-1].modified
        else:
            return ''

    def _cancelled(self, field_value):
        if self.get_status_display() == "Cancelled":
            return "<span style='background-color: rgb(222, 186, 99);'>%s</span>" % field_value
        else:
            return field_value

    def is_cancelled(self):
        if self.get_status_display() == "Cancelled":
            return "<span style='color : red;'>&#10006;</span>"
        if self.get_status_display() == "Closed":
            return "<span style='color : black;'>&#9940;</span>"

        return "<span style='color : green;'>&#10004;</span>"
    is_cancelled.allow_tags = True
    is_cancelled.short_description = " "

    def clean(self):

        if self.id:
            _template = "%s cannot be changed once set. "
            _error_list = ""
            _onetime_field_list = ["account_type", "entity_name"]

            _changed_fields = self.changed_fields()

            for _field in _onetime_field_list:
                if _field in _changed_fields:
                    _field_display = " ".join([x.title() for x in _field.split("_")])
                    _error_list += _template % _field_display

            if _error_list:
                raise ValidationError(_error_list)

    def __str__(self):
        if self.account_type.name == 'Class Accounts':
            return "CA : %s %s" % (self.entity_name, self.program_schedule)

        if self.account_type.name == 'Teachers Accounts':
            return "TA : %s %s: %s" % (self.entity_name, self.zone, self.teacher)

        return "OA : %s %s: %s" % (self.entity_name, self.budget_code, self.zone)

    class Meta:
        ordering = ['account_type', 'entity_name']
        verbose_name = 'RCO Voucher Approval Tracking'


class NPAccountsMaster(RCOAccountsMaster):

    class Meta:
        proxy = True
        verbose_name = 'NP Voucher Approval Tracking'


class CourierDetails(models.Model):
    accounts_master = models.ForeignKey(RCOAccountsMaster)
    agency = models.CharField(max_length=100, null=True, blank=True)
    tracking_number = models.CharField(max_length=100, null=True, blank=True, unique=True)
    sent_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['agency', 'sent_date']
        verbose_name = 'Courier Detail'


class VoucherDetails(SmartModel):
    accounts_master = models.ForeignKey(RCOAccountsMaster)
    tracking_no = models.CharField(max_length=100, blank=True)
    nature_of_voucher = models.ForeignKey(VoucherMaster)
    voucher_status = models.ForeignKey(RCOVoucherStatusMaster)
    voucher_date = models.DateField()
    head_of_expenses = GroupedForeignKey(ExpensesTypeMaster, 'type', blank=True, null=True, verbose_name='Head of Expenses')
    expenses_description = models.CharField(max_length=100, blank=True)
    party_name = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    approval_sent_date = models.DateField(blank=True, null=True)
    approved_date = models.DateField(blank=True, null=True)
    cheque = models.BooleanField('Cheque Party', default=False)
    address1 = models.CharField(max_length=200, blank=True)
    address2 = models.CharField(max_length=200, blank=True)
    np_voucher_status = GroupedForeignKey(NPVoucherStatusMaster, 'type', blank=True, null=True)
    finance_submission_date = models.DateField(blank=True, null=True)
    movement_sheet_no = models.CharField(max_length=100, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    utr_no = models.CharField('UTR NO', max_length=100, blank=True)
    amount_after_tds = models.DecimalField('Amount after TDS', max_digits=10, decimal_places=2, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk is None and self.tracking_no == '':
            cft = Configuration.objects.get(configuration_key='IPC_ACCOUNTS_TRACKING_CONST')
            data = json.loads(cft.configuration_value)
            if self.accounts_master.account_type.name == 'Class Accounts':
                z_name = self.accounts_master.program_schedule.center.zone.zone_name
                key = data[z_name]['ca_key']
                prefix = data[z_name]['prefix']
                tracking_no = prefix + str(key).zfill(6)
                data[z_name]['ca_key'] = key + 1
                cft.configuration_value = json.dumps(data)
                cft.save()
            elif self.accounts_master.account_type.name == 'Teachers Accounts':
                key = data[self.accounts_master.zone.zone_name]['ta_key']
                prefix = data[self.accounts_master.zone.zone_name]['prefix']
                tracking_no = 'T' + prefix + str(key).zfill(6)
                data[self.accounts_master.zone.zone_name]['ta_key'] = key + 1
                cft.configuration_value = json.dumps(data)
                cft.save()
            else:
                key = data[self.accounts_master.zone.zone_name]['oa_key']
                prefix = data[self.accounts_master.zone.zone_name]['prefix']
                tracking_no = 'O' + prefix + str(key).zfill(6)
                data[self.accounts_master.zone.zone_name]['oa_key'] = key + 1
                cft.configuration_value = json.dumps(data)
                cft.save()
            self.tracking_no = tracking_no
        super(VoucherDetails, self).save(*args, **kwargs)

    def __str__(self):
        return "%s -- %s - %s - %s" % (self.accounts_master.entity_name, self.nature_of_voucher, self.voucher_status, self.amount)

    class Meta:
        ordering = ['nature_of_voucher',]
        verbose_name = 'Voucher'


class TransactionNotes(models.Model):
    accounts_master = models.ForeignKey(RCOAccountsMaster)
    note = MarkdownField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return ""

    class Meta:
        ordering = ['-created']
        verbose_name = 'Transaction Note'

