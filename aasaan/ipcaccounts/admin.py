from django.contrib import admin
from .models import RCOAccountsMaster, NPAccountsMaster, CourierDetails, TransactionNotes, VoucherMaster, EntityMaster, RCOVoucherStatusMaster, VoucherDetails, ExpensesTypeMaster, NPVoucherStatusMaster, AccountType, AccountTypeMaster
from schedulemaster.models import ProgramSchedule
from contacts.models import Contact, IndividualRole, Zone, Center, ContactRoleGroup, RoleGroup, IndividualContactRoleZone
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta
from django.utils import timezone
from AasaanUser.models import AasaanUserContact
from django.contrib.auth.models import User
from config.models import Configuration
from .forms import RCOAccountsForm
from django.db.models import Q
from django.utils.html import format_html
from utils.filters import RelatedDropdownFilter, DropdownFilter, RelatedOnlyFieldListFilter


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


class VoucherDetailsInline(admin.StackedInline):
    form = RCOAccountsForm
    model = VoucherDetails
    extra = 0

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):

        if db_field.name == 'nature_of_voucher':
            kwargs["queryset"] = VoucherMaster.active_objects.all()
        return super(VoucherDetailsInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    fieldsets = (
        ('', {
            'fields': (('tracking_no', 'voucher_type',), ('nature_of_voucher', 'voucher_status', 'voucher_date'),
                       ('head_of_expenses','expenses_description', 'party_name')),
            'classes': ('has-cols', 'cols-3')
        }),

        ('', {
            'fields': (('amount', 'approval_sent_date', 'approved_date'),),
            'classes': ('has-cols', 'cols-3')
        }),

        ('', {
            'fields': (('np_voucher_status', 'finance_submission_date', 'movement_sheet_no'),),
            'classes': ('has-cols', 'cols-3')
        }),

        ('', {
            'fields': (('payment_date', 'utr_no', 'amount_after_tds'),),
            'classes': ('has-cols', 'cols-3')
        }),
        ('', {
            'fields': (('cheque', 'address1', 'address2'),),
            'classes': ('has-cols', 'cols-3')
        }),
        ('', {
            'fields': ('copy_voucher',),

        }),
    )


class CourierDetailsInline(admin.TabularInline):
    model = CourierDetails
    extra = 0

    def has_delete_permission(self, request, obj=None):
        return False


class ExpensesTypeMasterAdmin(admin.ModelAdmin):
    list_filter = ('type',)


class AccountsMasterAdmin(admin.ModelAdmin):

    def account_actions(self, obj):

        url = '/admin/ipcaccounts/send_email?account_id='+str(obj.id)+''
        return format_html(
            '<a class="button" target="_blank" href="{}">Send E-Mail</a>&nbsp;', url, obj.id)

    account_actions.short_description = 'Email Approval'
    account_actions.allow_tags = True


    def save_related(self, request, form, formsets, change):
        for formset in formsets:
            for fs in formset:
                if isinstance(fs.instance, TransactionNotes) and fs.cleaned_data:
                    if fs.instance.pk is None:
                        fs.instance.accounts_master = form.instance
                        fs.instance.created_by = request.user.username
                        fs.instance.note = fs.instance.note + ' created_by : ' + request.user.username + ' created at : ' + timezone.now().strftime("%b %d %Y %H:%M:%S")
                        fs.instance.save()
                if isinstance(fs.instance, VoucherDetails) and fs.cleaned_data:
                    if fs.instance.pk:
                        voucher_details = VoucherDetails.objects.get(tracking_no=fs.instance.tracking_no)
                        if fs.instance.voucher_status != voucher_details.voucher_status:
                            status_change_note = TransactionNotes()
                            status_change_note.accounts_master = form.instance
                            status_change_note.created_by = request.user.username
                            note =  "\nAutomatic Log: RCO Status of %s changed from '%s' to '%s'\n" % \
                                                           (fs.instance.tracking_no, voucher_details.voucher_status,
                                                            fs.instance.voucher_status)
                            note = note + ' created_by : ' + request.user.username + ' created at : ' + timezone.now().strftime("%b %d %Y %H:%M:%S")
                            status_change_note.note = note
                            status_change_note.save()

        super(AccountsMasterAdmin, self).save_related(request, form, formsets, change)

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

        return super(AccountsMasterAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    # filter accounts records based on user permissions
    def get_queryset(self, request):

        qs = super(AccountsMasterAdmin, self).get_queryset(request)
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

    list_display = ('is_cancelled', '__str__', 'tracking_no', 'rco_status', 'np_status', 'total_no_vouchers', 'account_actions', 'last_modified',)
    list_filter = ('account_type', 'entity_name', ('zone', RelatedDropdownFilter))

    search_fields = ('teacher__first_name', 'budget_code', 'program_schedule__program__name')

    list_display_links = ['is_cancelled', '__str__']

    fieldsets = (
        ('', {
            'fields': ('account_type', 'entity_name', 'teacher', 'zone','program_schedule', 'budget_code',
             'status')
        }),
        )

    inlines = [VoucherDetailsInline, CourierDetailsInline, TransactionNotesInline1, TransactionNotesInline]

    save_on_top = True

    list_per_page = 30

    class Media:
        js = ('/static/aasaan/ipcaccounts/ipc_accounts.js','/static/aasaan/ipcaccounts/validation.js')


class NPAccountsMasterAdmin(admin.ModelAdmin):

    def save_related(self, request, form, formsets, change):
        for formset in formsets:
            for fs in formset:
                if isinstance(fs.instance, TransactionNotes) and fs.cleaned_data:
                    if fs.instance.pk is None:
                        fs.instance.accounts_master = form.instance
                        fs.instance.created_by = request.user.username
                        fs.instance.note = fs.instance.note + ' created_by : ' + request.user.username + ' created at : ' + timezone.now().strftime("%b %d %Y %H:%M:%S")
                        fs.instance.save()
                if isinstance(fs.instance, VoucherDetails) and fs.cleaned_data:
                    if fs.instance.pk:
                        voucher_details = VoucherDetails.objects.get(tracking_no=fs.instance.tracking_no)
                        if fs.instance.voucher_status != voucher_details.voucher_status:
                            status_change_note = TransactionNotes()
                            status_change_note.accounts_master = form.instance
                            status_change_note.created_by = request.user.username
                            note =  "\nAutomatic Log: RCO Status of %s changed from '%s' to '%s'\n" % \
                                                           (fs.instance.tracking_no, voucher_details.voucher_status,
                                                            fs.instance.voucher_status)
                            note = note + ' created_by : ' + request.user.username + ' created at : ' + timezone.now().strftime("%b %d %Y %H:%M:%S")
                            status_change_note.note = note
                            status_change_note.save()
                        if fs.instance.np_voucher_status != voucher_details.np_voucher_status:
                            status_change_note = TransactionNotes()
                            status_change_note.accounts_master = form.instance
                            status_change_note.created_by = request.user.username
                            note = "\nAutomatic Log: NP Status of %s changed from '%s' to '%s'\n" % \
                                                           (fs.instance.tracking_no, voucher_details.np_voucher_status,
                                                            fs.instance.np_voucher_status)
                            note = note + ' created_by : ' + request.user.username + ' created at : ' + timezone.now().strftime("%b %d %Y %H:%M:%S")
                            status_change_note.note = note
                            status_change_note.save()

        super(NPAccountsMasterAdmin, self).save_related(request, form, formsets, change)

    # filter accounts records based on user permissions
    def get_queryset(self, request):

        qs = super(NPAccountsMasterAdmin, self).get_queryset(request)
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
                all_accounts = all_accounts.distinct()
        except ContactRoleGroup.DoesNotExist:
            pass

        return all_accounts.distinct()

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):

        if db_field.name == 'entity_name':
            kwargs["queryset"] = EntityMaster.active_objects.all()

        if not request.user.is_superuser and db_field.name == 'center':
            user_zones = [x.zone for x in request.user.aasaanuserzone_set.all()]
            user_zone_centers = [x.id for x in Center.objects.filter(zone__in=user_zones)]
            user_centers = [x.center.id for x in request.user.aasaanusercenter_set.all()] + \
                           user_zone_centers
            user_centers = list(set(user_centers))
            kwargs["queryset"] = Center.objects.filter(pk__in=user_centers)

        if db_field.name == 'program_schedule':
            obj_id = request.META['PATH_INFO'].rstrip('/').split('/')[-2]
            schedule_days_to_show = Configuration.objects.get(
                configuration_key='IPC_ACCOUNTS_SCHEDULE_DAYS').configuration_value
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

        return super(NPAccountsMasterAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    list_display = ('is_cancelled', '__str__', 'rco_status', 'np_status', 'total_no_vouchers', 'last_modified')
    list_filter = ('account_type', 'entity_name', )

    list_display_links = ['is_cancelled', '__str__']

    fieldsets = (
        ('', {
            'fields': ('account_type', 'entity_name', 'budget_code', 'teacher', 'zone',
                       'program_schedule', 'status')
        }),
    )

    inlines = [VoucherDetailsInline, CourierDetailsInline, TransactionNotesInline1, TransactionNotesInline]

    save_on_top = True

    list_per_page = 30

    def has_add_permission(self, request, obj=None):
        return False

    class Media:
        js = ('/static/aasaan/ipcaccounts/ipc_accounts.js',)


admin.site.register(RCOAccountsMaster, AccountsMasterAdmin)
admin.site.register(NPAccountsMaster, NPAccountsMasterAdmin)
admin.site.register(VoucherMaster, admin.ModelAdmin)
admin.site.register(EntityMaster, admin.ModelAdmin)
admin.site.register(ExpensesTypeMaster, ExpensesTypeMasterAdmin)
admin.site.register(RCOVoucherStatusMaster, admin.ModelAdmin)
admin.site.register(NPVoucherStatusMaster, admin.ModelAdmin)
admin.site.register(AccountType, admin.ModelAdmin)
admin.site.register(AccountTypeMaster, admin.ModelAdmin)
