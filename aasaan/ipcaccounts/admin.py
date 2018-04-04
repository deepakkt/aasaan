from django.contrib import admin
from .models import RCOAccountsMaster, NPAccountsMaster, CourierDetails, TransactionNotes, VoucherMaster, EntityMaster, RCOVoucherStatusMaster, VoucherDetails, ExpensesTypeMaster, NPVoucherStatusMaster, AccountType, AccountTypeMaster, Treasurer
from schedulemaster.models import ProgramSchedule
from contacts.models import Contact, IndividualRole, Zone, Center, ContactRoleGroup, RoleGroup, IndividualContactRoleZone
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta
from django.utils import timezone
from AasaanUser.models import AasaanUserContact
from django.contrib.auth.models import User
from config.models import Configuration
from django.db.models import Q
from django.utils.html import format_html
from utils.daterange_filter import DateRangeFilter
from utils.filters import RelatedDropdownFilter

class TreasurerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'old_treasurer', 'new_treasurer')

    fieldsets = (
        ('', {
            'fields': (('request_type', 'center'),('new_treasurer', 'old_treasurer'), ('bank_name', 'branch_name'),('account_holder', 'account_number'),('ifsc_code', 'document'),
                       ),
            'classes': ('has-cols', 'cols-2')
        }),
    )

    class Media:
        js = ('/static/aasaan/ipcaccounts/treasurer.js',)


class TransactionNotesInline(admin.StackedInline):
    model = TransactionNotes
    extra = 0
    fields = ['note', ]

    def has_change_permission(self, request, obj=None):
        return False


class TransactionNotesInline1(admin.StackedInline):

    model = TransactionNotes
    extra = 0
    readonly_fields = ['note',]

    fieldsets = [
        ('', {'fields': ('note',), }),
        ('Hidden Fields',
         {'fields': ['created_by',], 'classes': ['hidden']}),
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CourierDetailsInline(admin.TabularInline):
    model = CourierDetails
    extra = 0

    def has_delete_permission(self, request, obj=None):
        return False


class ExpensesTypeMasterAdmin(admin.ModelAdmin):
    list_filter = ('type',)


class VoucherDetailsInline(admin.StackedInline):
    model = VoucherDetails
    extra = 0

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):

        if db_field.name == 'nature_of_voucher':
            kwargs["queryset"] = VoucherMaster.active_objects.all()
        return super(VoucherDetailsInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    fieldsets = (
        ('', {
            'fields': (('tracking_no', 'voucher_type', 'nature_of_voucher'),
                       ('head_of_expenses','expenses_description', 'party_name'),
                       ('amount',)),
            'classes': ('has-cols', 'cols-3')
        }),
        ('', {
            'fields': (('payment_date', 'utr_no', 'tds_amount'),),
            'classes': ('has-cols', 'cols-3')
        }),
    )


class RCOAccountsMasterAdmin(admin.ModelAdmin):

    def account_actions(self, obj):
        if obj.email_sent:
            button_text = 'Resend Email'
        else:
            button_text = 'Send Email'
        url = '/admin/ipcaccounts/send_email?account_id='+str(obj.id)+''
        return format_html(
            '<a class="button" target="_blank" href="{}">'+button_text+'</a>&nbsp;', url, obj.id)

    account_actions.short_description = 'Email Approval'
    account_actions.allow_tags = True

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):

        if db_field.name == 'entity_name':
            kwargs["queryset"] = EntityMaster.active_objects.all()

        if not request.user.is_superuser and db_field.name == 'center':
            user_zones = [x.zone for x in request.user.aasaanuserzone_set.all()]
            user_zone_centers = [x.id for x in Center.objects.filter(zone__in=user_zones)]
            user_centers = [x.center.id for x in request.user.aasaanusercenter_set.all()] +\
                user_zone_centers
            user_centers = list(set(user_centers))
            kwargs["queryset"] = Center.objects.filter(pk__in=user_centers)

        if db_field.name == 'program_schedule':
            obj_id = request.META['PATH_INFO'].rstrip('/').split('/')[-2]
            schedule_days_to_show = Configuration.objects.get(configuration_key='IPC_ACCOUNTS_SCHEDULE_DAYS').configuration_value
            time_threshold = timezone.now() - timedelta(days=int(schedule_days_to_show))
            qs = ProgramSchedule.objects.filter(end_date__gte=time_threshold)
            if obj_id.isdigit():
                am = RCOAccountsMaster.objects.get(pk=obj_id)
                if am.program_schedule:
                    qs = qs | ProgramSchedule.objects.filter(pk=am.program_schedule.pk)
            if not request.user.is_superuser:
                user_zones = [x.zone for x in request.user.aasaanuserzone_set.all()]
                user_zone_centers = [x.id for x in Center.objects.filter(zone__in=user_zones)]
                user_centers = [x.center.id for x in request.user.aasaanusercenter_set.all()] + \
                               user_zone_centers
                user_centers = list(set(user_centers))
                kwargs["queryset"] = qs.filter(center__in=user_centers)
            else:
                kwargs["queryset"] = qs

        if db_field.name == 'teacher':
            try:
                teacher_role = IndividualRole.objects.get(role_name='Teacher', role_level='ZO')
                _teacher_list = Contact.objects.filter(individualcontactrolezone__role=teacher_role)
                kwargs["queryset"] = _teacher_list.distinct()
            except ObjectDoesNotExist:
                kwargs["queryset"] = Contact.objects.none()

        return super(RCOAccountsMasterAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    # filter accounts records based on user permissions
    def get_queryset(self, request):

        qs = super(RCOAccountsMasterAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        user_zones = [x.zone for x in request.user.aasaanuserzone_set.all()]

        login_user = User.objects.get(username=request.user.username)
        contact = AasaanUserContact.objects.get(user=login_user)
        trs_role_group = RoleGroup.objects.filter(role_name=Configuration.objects.get(configuration_key='IPC_ACCOUNTS_TEACHERS_GROUP').configuration_value)
        acc_role_group = RoleGroup.objects.filter(role_name=Configuration.objects.get(configuration_key='IPC_ACCOUNTS_CLASS_GROUP').configuration_value)

        try:
            contact_role_group = ContactRoleGroup.objects.filter(contact=contact.contact)
        except ObjectDoesNotExist:
            return RCOAccountsMaster.objects.none()
        try:
            if contact_role_group.get(role=trs_role_group):
                trs_account = RCOAccountsMaster.objects.filter(zone__in=user_zones).filter(account_type__name='Teacher Accounts')
                all_accounts = trs_account
        except ContactRoleGroup.DoesNotExist:
            all_accounts = None
        try:
            if contact_role_group.get(role=acc_role_group):
                class_accounts = RCOAccountsMaster.objects.filter(program_schedule__center__zone__in=user_zones)
                other_accounts = RCOAccountsMaster.objects.filter(zone__in=user_zones).filter(~Q(account_type__name='Teacher Accounts'))
                all_accounts = class_accounts | other_accounts
        except ContactRoleGroup.DoesNotExist:
            pass
        try:
            if contact_role_group.get(role=acc_role_group) and contact_role_group.get(role=trs_role_group):
                all_accounts = trs_account | class_accounts | other_accounts
        except ContactRoleGroup.DoesNotExist:
            pass

        return all_accounts.distinct()

    fieldsets = (
        ('', {
            'fields': (('account_type', 'entity_name'),('rco_voucher_status', 'voucher_date'),
                       ),
            'classes': ('has-cols', 'cols-2')
        }),
        ('', {
            'fields': ('program_schedule', 'teacher', 'budget_code', 'zone')
        }),
        ('IPC Accounts', {
            'fields': (('np_voucher_status', 'finance_submission_date', 'movement_sheet_no'),
                       ),
            'classes': ('has-cols', 'cols-3')
        }),
    )
    date_hierarchy = 'voucher_date'
    list_editable = ('rco_voucher_status',)
    list_display = ('__str__', 'rco_voucher_status', 'approved_date', 'email_sent', 'account_actions', 'np_voucher_status')
    list_filter = (('program_schedule__start_date', DateRangeFilter), ('account_type', RelatedDropdownFilter), ('rco_voucher_status', RelatedDropdownFilter), ('np_voucher_status',RelatedDropdownFilter), ('zone',RelatedDropdownFilter),('entity_name', RelatedDropdownFilter))

    search_fields = ('program_schedule__program__name', )

    list_display_links = ['__str__']

    inlines = [VoucherDetailsInline, CourierDetailsInline, TransactionNotesInline1, TransactionNotesInline]

    save_on_top = True

    list_per_page = 30

    class Media:
        js = ('/static/aasaan/ipcaccounts/ipc_accounts.js',)


class NPAccountsMasterAdmin(RCOAccountsMasterAdmin):
    list_editable = ('np_voucher_status', 'movement_sheet_no')
    list_display = ('__str__', 'np_voucher_status', 'finance_submission_date', 'movement_sheet_no')


admin.site.register(RCOAccountsMaster, RCOAccountsMasterAdmin)
admin.site.register(NPAccountsMaster, NPAccountsMasterAdmin)
admin.site.register(VoucherMaster, admin.ModelAdmin)
admin.site.register(EntityMaster, admin.ModelAdmin)
admin.site.register(ExpensesTypeMaster, ExpensesTypeMasterAdmin)
admin.site.register(RCOVoucherStatusMaster, admin.ModelAdmin)
admin.site.register(NPVoucherStatusMaster, admin.ModelAdmin)
admin.site.register(AccountType, admin.ModelAdmin)
admin.site.register(AccountTypeMaster, admin.ModelAdmin)
admin.site.register(Treasurer, TreasurerAdmin)
