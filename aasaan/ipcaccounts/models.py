from django.db import models
from contacts.models import Center, Contact, IndividualContactRoleZone, Zone
from schedulemaster.models import ProgramSchedule
from django_markdown.models import MarkdownField
import json
from config.models import Configuration, SmartModel
from django.core.exceptions import ValidationError


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


class ClassExpensesTypeMaster(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'Class Expenses'


class TeacherExpensesTypeMaster(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'Teacher Expenses'


class AccountsMaster(SmartModel):

    ACCOUNT_TYPE_VALUES = (('TA', 'Teachers Accounts'),
                           ('CA', 'Classes Accounts'),
                           ('OA', 'Other Accounts'),

    )
    account_type = models.CharField(max_length=6, choices=ACCOUNT_TYPE_VALUES,
                                       default=ACCOUNT_TYPE_VALUES[1][0])

    entity_name = models.ForeignKey(EntityMaster)
    center = models.ForeignKey(Center, blank=True, null=True)
    zone = models.ForeignKey(Zone, blank=True, null=True)
    teacher = models.ForeignKey(Contact, blank=True, null=True)
    budget_code = models.CharField(max_length=100, blank=True)
    program_schedule = models.ForeignKey(ProgramSchedule, blank=True, null=True)
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

        return "OA : %s %s: %s" % (self.entity_name, self.budget_code, self.center)



    class Meta:
        ordering = ['account_type', 'entity_name']
        verbose_name = 'Voucher Approval Tracking'


class CourierDetails(models.Model):
    accounts_master = models.ForeignKey(AccountsMaster)
    source = models.CharField(max_length=100, null=True, blank=True)
    destination = models.CharField(max_length=100, null=True, blank=True)
    agency = models.CharField(max_length=100, null=True, blank=True)
    tracking_no = models.CharField(max_length=100, null=True, blank=True, unique=True)
    sent_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    remarks = MarkdownField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class VoucherDetails(SmartModel):
    accounts_master = models.ForeignKey(AccountsMaster)
    tracking_no = models.CharField(max_length=100, blank=True, unique=True)
    nature_of_voucher = models.ForeignKey(VoucherMaster)
    voucher_status = models.ForeignKey(VoucherStatusMaster)
    voucher_date = models.DateField()
    ca_head_of_expenses = models.ForeignKey(ClassExpensesTypeMaster, blank=True, null=True, verbose_name='Head of Expenses')
    ta_head_of_expenses = models.ForeignKey(TeacherExpensesTypeMaster, blank=True, null=True, verbose_name='Head of Expenses')
    oa_head_of_expenses = models.CharField(max_length=100, blank=True, verbose_name='Head of Expenses')
    expenses_description = models.CharField(max_length=100, blank=True)
    party_name = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    delayed_approval =  models.BooleanField(default=False)

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

    def save(self, *args, **kwargs):
        # Create and save status change note if it has changed
        changed_fields = self.changed_fields()
        if self.pk:
            if 'status' in changed_fields or 'category' in changed_fields:
                status_change_note = TransactionNotes()
                status_change_note.accounts_master = self.accounts_master
                status_change_note.created_by = 'SC'
                status_change_note.note = ""

                if 'status' in changed_fields:
                    status_change_note.note += "\nAutomatic Log: Status of %s changed from '%s' to '%s'\n" % \
                                               (self.full_name, changed_fields['status'][0],
                                                changed_fields['status'][-1])

                if 'category' in changed_fields:
                    status_change_note.note += "\nAutomatic Log: Category of %s changed from '%s' to '%s'\n" % \
                                               (self.full_name, changed_fields['category'][0],
                                                changed_fields['category'][-1])

                status_change_note.save()

        if self.pk is None and self.tracking_no == '':
            cft = Configuration.objects.get(configuration_key='IPC_ACCOUNTS_TRACKING_CONST')
            data = json.loads(cft.configuration_value)
            if self.accounts_master.account_type == 'CA':
                key = data[self.accounts_master.center.zone.zone_name]['ca_key']
                prefix = data[self.accounts_master.center.zone.zone_name]['prefix']
                tracking_no = 'CA' + prefix + str(key).zfill(10)
                data[self.accounts_master.center.zone.zone_name]['ca_key'] = key + 1
                cft.configuration_value = json.dumps(data)
                cft.save()

            if self.accounts_master.account_type == 'TA':
                key = data[self.accounts_master.zone.zone_name]['ta_key']
                prefix = data[self.accounts_master.zone.zone_name]['prefix']
                tracking_no = 'TA' + prefix + str(key).zfill(10)
                data[self.accounts_master.zone.zone_name]['ta_key'] = key + 1
                cft.configuration_value = json.dumps(data)
                cft.save()
            if self.accounts_master.account_type == 'OA':
                key = data[self.accounts_master.zone.zone_name]['oa_key']
                prefix = data[self.accounts_master.zone.zone_name]['prefix']
                tracking_no = 'OA' + prefix + str(key).zfill(10)
                data[self.accounts_master.zone.zone_name]['oa_key'] = key + 1
                cft.configuration_value = json.dumps(data)
                cft.save()
            self.tracking_no = tracking_no
        super(VoucherDetails, self).save(*args, **kwargs)

    def __str__(self):
        return "%s -- %s - %s - %s - %s" % (self.accounts_master.entity_name, self.nature_of_voucher, self.voucher_status, self.accounts_master.center if self.accounts_master.center else self.accounts_master.teacher, self.amount)

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
        return ""

    class Meta:
        ordering = ['-created']
        verbose_name = 'Transaction Note'

