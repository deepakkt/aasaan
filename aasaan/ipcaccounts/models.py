from django.db import models
from contacts.models import Center, Contact, IndividualContactRoleZone, Zone
from schedulemaster.models import ProgramSchedule
from django_markdown.models import MarkdownField
import json
from config.models import Configuration, SmartModel
from django.core.exceptions import ValidationError
from smart_selects.db_fields import GroupedForeignKey


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


class VoucherStatusMaster(models.Model):
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
        verbose_name = 'Account Type'


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


class ClassExpensesTypeMaster(models.Model):
    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'Class Expense'


class TeacherExpensesTypeMaster(models.Model):
    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'Teacher Expense'


class AccountsMaster(SmartModel):

    ACCOUNT_TYPE_VALUES = (('TA', 'Teachers Accounts'),
                           ('CA', 'Classes Accounts'),
                           ('OA', 'Other Accounts'),

    )
    account_type = models.CharField(max_length=6, choices=ACCOUNT_TYPE_VALUES,
                                       default=ACCOUNT_TYPE_VALUES[1][0])

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
        if self.account_type == 'CA':
            return "CA : %s %s" % (self.entity_name, self.program_schedule)

        if self.account_type == 'TA':
            return "TA : %s %s: %s" % (self.entity_name, self.zone, self.teacher)

        return "OA : %s %s: %s" % (self.entity_name, self.budget_code, self.zone)

    class Meta:
        ordering = ['account_type', 'entity_name']
        verbose_name = 'RCO Voucher Approval Tracking'


class NPAccountsMaster(AccountsMaster):

    class Meta:
        proxy = True
        verbose_name = 'NP Voucher Approval Tracking'


class CourierDetails(models.Model):
    accounts_master = models.ForeignKey(AccountsMaster)
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
    accounts_master = models.ForeignKey(AccountsMaster)
    tracking_no = models.CharField(max_length=100, blank=True)
    nature_of_voucher = models.ForeignKey(VoucherMaster)
    voucher_status = models.ForeignKey(VoucherStatusMaster)
    voucher_date = models.DateField()
    ca_head_of_expenses = models.ForeignKey(ClassExpensesTypeMaster, blank=True, null=True, verbose_name='Head of Expenses')
    ta_head_of_expenses = models.ForeignKey(TeacherExpensesTypeMaster, blank=True, null=True, verbose_name='Head of Expenses')
    oa_head_of_expenses = models.CharField(max_length=100, blank=True, verbose_name='Head of Expenses')
    expenses_description = models.CharField(max_length=100, blank=True)
    party_name = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    copy_voucher =  models.BooleanField('Copy Voucher', default=False)
    approval_sent_date = models.DateField(blank=True, null=True)
    approved_date = models.DateField(blank=True, null=True)

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
            if self.accounts_master.account_type == 'CA':
                z_name = self.accounts_master.program_schedule.center.zone.zone_name
                key = data[z_name]['ca_key']
                prefix = data[z_name]['prefix']
                tracking_no = prefix + str(key).zfill(6)
                data[z_name]['ca_key'] = key + 1
                cft.configuration_value = json.dumps(data)
                cft.save()

            if self.accounts_master.account_type == 'TA':
                key = data[self.accounts_master.zone.zone_name]['ta_key']
                prefix = data[self.accounts_master.zone.zone_name]['prefix']
                tracking_no = 'T' + prefix + str(key).zfill(6)
                data[self.accounts_master.zone.zone_name]['ta_key'] = key + 1
                cft.configuration_value = json.dumps(data)
                cft.save()
            if self.accounts_master.account_type == 'OA':
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
        verbose_name = 'RCO Voucher'


class TransactionNotes(models.Model):
    accounts_master = models.ForeignKey(AccountsMaster)
    note = MarkdownField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return ""

    class Meta:
        ordering = ['-created']
        verbose_name = 'Transaction Note'

