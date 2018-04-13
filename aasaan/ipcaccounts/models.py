from django.db import models
from contacts.models import Center, Contact, IndividualContactRoleZone, Zone
from schedulemaster.models import ProgramSchedule, ProgramMaster
import json
from config.models import Configuration, SmartModel
from django.core.exceptions import ValidationError
from smart_selects.db_fields import GroupedForeignKey
import datetime
from django.utils.translation import gettext as _
from django.utils import formats


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
    type = models.ForeignKey(AccountType, on_delete=models.CASCADE)

    objects = models.Manager()
    active_objects = ActiveManager()

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'NP Voucher Status Master'


class ExpensesTypeMaster(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    type = models.ForeignKey(AccountTypeMaster, on_delete=models.CASCADE)

    objects = models.Manager()
    active_objects = ActiveManager()

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'Expense master'
        unique_together = ['name', 'type']


class Treasurer(models.Model):
    TYPE_VALUES = (('ADD', 'Add Treasurer'),
                   ('CHG', 'Change Treasurer'),
                   )
    request_type = models.CharField(max_length=3, choices=TYPE_VALUES,
                                    default=TYPE_VALUES[0][0])
    center = GroupedForeignKey(Center, 'zone')
    old_treasurer = models.ForeignKey(Contact, related_name="old_treasurer", blank=True, null=True, on_delete=models.CASCADE)
    new_treasurer = models.ForeignKey(Contact, related_name="new_treasurer", on_delete=models.CASCADE)
    ifsc_code = models.CharField("IFSCode", max_length=15)
    bank_name = models.CharField("Bank Name", max_length=100)
    branch_name = models.CharField("Branch Name", max_length=100)
    account_holder = models.CharField("Account Holder Name", max_length=50)
    account_number = models.CharField("Account Number", max_length=15)
    document = models.FileField(upload_to='documents/%Y/%m/%d/', blank=True, null=True)

    def __str__(self):
        return "%s" % self.center

    class Meta:
        verbose_name = 'Treasurer'


class RCOAccountsMaster(SmartModel):
    account_type = models.ForeignKey(AccountTypeMaster, default=1, verbose_name='Account Type', on_delete=models.CASCADE)
    entity_name = models.ForeignKey(EntityMaster, default=1, verbose_name='Entity', on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, verbose_name='Zone', on_delete=models.CASCADE)
    teacher = models.ForeignKey(Contact, blank=True, null=True, on_delete=models.CASCADE)
    budget_code = models.CharField(max_length=100, blank=True)
    program_type = models.ForeignKey(ProgramMaster, blank=True, null=True, verbose_name='Program Type', on_delete=models.CASCADE)
    program_schedule = models.ForeignKey(ProgramSchedule, blank=True, null=True, on_delete=models.CASCADE)
    voucher_date = models.DateField(_("Voucher Date"), default=datetime.date.today)
    approval_sent_date = models.DateField('Approval request Date', blank=True, null=True)
    approved_date = models.DateField(blank=True, null=True)
    np_voucher_status = GroupedForeignKey(NPVoucherStatusMaster, 'type', blank=True, null=True, verbose_name='NP Voucher Status', on_delete=models.CASCADE)
    finance_submission_date = models.DateField(blank=True, null=True)
    rco_voucher_status = models.ForeignKey(RCOVoucherStatusMaster, default=1, verbose_name='RCO Voucher Status', on_delete=models.CASCADE)
    movement_sheet_no = models.CharField(max_length=100, blank=True)
    email_sent = models.BooleanField(blank=True, default=False)

    def __init__(self, *args, **kwargs):
        super(RCOAccountsMaster, self).__init__(*args, **kwargs)
        self.old_rco_voucher_status = self.rco_voucher_status
        self.old_np_voucher_status = self.np_voucher_status

    def save(self, *args, **kwargs):
        if self.account_type.name == 'Class Accounts':
            self.zone = self.program_schedule.center.zone
        if self.old_rco_voucher_status.name != 'Panel Treasurer Approved' and self.rco_voucher_status.name == 'Panel Treasurer Approved':
            self.approved_date = datetime.date.today()
        if self.np_voucher_status:
            if self.old_np_voucher_status is None or self.old_np_voucher_status.name != 'Submitted to Finance' and self.np_voucher_status.name == 'Submitted to Finance':
                self.finance_submission_date = datetime.date.today()
        super(RCOAccountsMaster, self).save(*args, **kwargs)

    def total_no_vouchers(self):
        items_count = VoucherDetails.objects.filter(accounts_master=self).count()
        return items_count
    total_no_vouchers.allow_tags = True
    total_no_vouchers.short_description = "Vouchers"

    def is_cancelled(self):
        if self.rco_voucher_status.name == "Cancelled":
            return "<span style='color : red;'>&#10006;</span>"
        if self.np_voucher_status and self.np_voucher_status.name == "Voucher Processed":
            return "<span style='color : green;'>&#10004;</span>"

        return "<span style='color : black;'>&#9940;</span>"

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

        voucher_details = VoucherDetails.objects.filter(accounts_master=self).order_by('tracking_no')
        if len(voucher_details) > 2:
            tracking_numbers = voucher_details[0].tracking_no + ' - ' + voucher_details[len(voucher_details) - 1].tracking_no[-2:]
        elif len(voucher_details) == 2:
            tracking_numbers = voucher_details[0].tracking_no + ' & ' + voucher_details[len(voucher_details) - 1].tracking_no[-2:]
        elif len(voucher_details) == 1:
            tracking_numbers = voucher_details[0].tracking_no
        else:
            tracking_numbers = 'No Voucher'

        if self.account_type.name == 'Class Accounts':
            program_master = ProgramMaster.objects.get(name=self.program_schedule.program.name)
            cft = Configuration.objects.get(configuration_key='IPC_ACCOUNTS_TRACKING_CONST')
            data = json.loads(cft.configuration_value)
            prefix = data[self.program_schedule.center.zone.zone_name]['prefix']
            formatted_start_date = formats.date_format(self.program_schedule.start_date, "DATE_FORMAT")
            budget_code = prefix + '-' + self.program_schedule.center.center_name + '-' + program_master.abbreviation + '-' + formatted_start_date
            return "%s : %s %s" % (tracking_numbers, self.entity_name, budget_code)
        elif self.account_type.name == 'Teacher Accounts':
            return "%s : %s %s %s" % (tracking_numbers, self.entity_name, self.zone, self.teacher)
        elif self.account_type.name == 'RCO Accounts':
            return "%s : %s %s %s" % (tracking_numbers, self.entity_name, self.budget_code, self.zone)
        else:
            return "%s : %s %s %s" % (tracking_numbers, self.entity_name, self.budget_code, self.zone)

    class Meta:
        ordering = ['account_type', 'entity_name']
        verbose_name = 'RCO Voucher'


class VoucherDetails(SmartModel):
    accounts_master = models.ForeignKey(RCOAccountsMaster, on_delete=models.CASCADE)
    tracking_no = models.CharField(max_length=100, blank=True)
    VOUCHER_TYPE_VALUES = (('BV', 'Bank Voucher'),
                     ('CV', 'Cash Voucher'),
                     ('JV', 'Journal Voucher'))

    voucher_type = models.CharField(max_length=2, choices=VOUCHER_TYPE_VALUES,
                              default=VOUCHER_TYPE_VALUES[0][0])
    nature_of_voucher = models.ForeignKey(VoucherMaster, default=1, on_delete=models.CASCADE)
    head_of_expenses = GroupedForeignKey(ExpensesTypeMaster, 'type', blank=True, null=True, verbose_name='Head of Expenses', on_delete=models.CASCADE)
    expenses_description = models.CharField(max_length=100, blank=True)
    party_name = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    utr_no = models.CharField('UTR NO', max_length=100, blank=True)
    tds_amount = models.DecimalField('TDS Amount', max_digits=10, decimal_places=2, blank=True, null=True)
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
            elif self.accounts_master.account_type.name == 'Teacher Accounts':
                key = data[self.accounts_master.zone.zone_name]['ta_key']
                prefix = data[self.accounts_master.zone.zone_name]['prefix']
                tracking_no = 'T' + prefix + str(key).zfill(6)
                data[self.accounts_master.zone.zone_name]['ta_key'] = key + 1
                cft.configuration_value = json.dumps(data)
                cft.save()
                if not self.party_name:
                    self.party_name = self.accounts_master.teacher.full_name + ' - ' + self.accounts_master.teacher.teacher_tno
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
        return "%s -- %s - %s" % (self.accounts_master.entity_name, self.nature_of_voucher, self.amount)

    class Meta:
        ordering = ['tracking_no', 'nature_of_voucher',]
        verbose_name = 'Voucher'


class NPAccountsMaster(RCOAccountsMaster):

    class Meta:
        proxy = True
        verbose_name = 'NP Voucher'


class CourierDetails(models.Model):
    accounts_master = models.ForeignKey(RCOAccountsMaster, on_delete=models.CASCADE)
    agency = models.CharField(max_length=100, null=True, blank=True)
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    sent_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['agency', 'sent_date']
        verbose_name = 'Courier Detail'


class TransactionNotes(models.Model):
    accounts_master = models.ForeignKey(RCOAccountsMaster, on_delete=models.CASCADE)
    note = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return ""

    class Meta:
        ordering = ['-created']
        verbose_name = 'Transaction Note'

