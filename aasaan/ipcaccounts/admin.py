from django.contrib import admin
from .models import AccountsMaster, CourierDetails, TransactionNotes, VoucherMaster, EntityMaster, VoucherStatusMaster, VoucherDetails, ClassExpensesTypeMaster, TeacherExpensesTypeMaster
from schedulemaster.models import ProgramSchedule
from contacts.models import Contact, IndividualRole, Zone, Center, ContactRoleGroup, RoleGroup, IndividualContactRoleZone
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta
from django.utils import timezone
from AasaanUser.models import AasaanUserContact
from django.contrib.auth.models import User


class TransactionNotesInline(admin.StackedInline):
    model = TransactionNotes
    extra = 0
    exclude = ('created_by',)

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return False


class VoucherDetailsInline(admin.StackedInline):
    model = VoucherDetails
    extra = 1

    fieldsets = (
        ('', {
            'fields': ('nature_of_voucher', 'voucher_status', 'voucher_date',
                       'ca_head_of_expenses', 'ta_head_of_expenses', 'expenses_description', 'party_name', 'amount', 'delayed_approval'),

        }),
    )

    def has_delete_permission(self, request, obj=None):
        return False


class CourierDetailsInline(admin.StackedInline):
    model = CourierDetails
    extra = 0

    fieldsets = (
        ('', {
            'fields': (('source', 'destination'), ('agency', 'tracking_no'),
                       ('sent_date', 'received_date'), ('remarks')),
            'classes': ('has-cols', 'cols-3')
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return False


class AccountsMasterAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):

        if db_field.name == 'voucher_status':
            kwargs["queryset"] = VoucherStatusMaster.active_objects.all()

        if db_field.name == 'nature_of_voucher':
            kwargs["queryset"] = VoucherMaster.active_objects.all()

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
            time_threshold = timezone.now() - timedelta(days=60)
            qs = ProgramSchedule.objects.filter(end_date__gte=time_threshold)
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
        user_centers = [x.center for x in request.user.aasaanusercenter_set.all()]
        user_zones = [x.zone for x in request.user.aasaanuserzone_set.all()]
        center_accounts = AccountsMaster.objects.filter(center__in=user_centers)
        center_zonal_accounts = AccountsMaster.objects.filter(center__zone__in=user_zones)
        all_accounts = center_accounts | center_zonal_accounts
        all_accounts = all_accounts.distinct()

        cfg_trs_role_group = 'Teachers Vouchers'
        cfg_acc_role_group = 'IPC Accounts Vouchers'

        login_user = User.objects.get(username=request.user.username)
        contact = AasaanUserContact.objects.get(user=login_user)
        trs_role_group = RoleGroup.objects.filter(role_name=cfg_trs_role_group)
        acc_role_group = RoleGroup.objects.filter(role_name=cfg_acc_role_group)
        try:
            contact_role_group = ContactRoleGroup.objects.filter(contact=contact.contact)
        except ObjectDoesNotExist:
            return AccountsMaster.objects.none()
        if contact_role_group.get(role=trs_role_group):
            trs_account = all_accounts.filter(account_type='TEACH')
        if contact_role_group.get(role=acc_role_group):
            class_accounts = all_accounts.filter(account_type='CLASS')
        if contact_role_group.get(role=acc_role_group) and contact_role_group.get(role=trs_role_group):
            all_accounts = trs_account | class_accounts
            all_accounts = all_accounts.distinct()

        return all_accounts

    list_display = ('account_type', '__str__', 'tracking_no', 'payment_date', 'utr_no', 'approval_status')
    list_filter = ('account_type', 'entity_name', )

    fieldsets = (
        ('', {
            'fields': ('account_type', 'entity_name', 'budget_code', 'center',
            'program_schedule', 'teacher',)
        }),
        ('Approval', {'fields': (('approval_sent_date', 'approved_date', 'approval_status'),), 'classes': ['collapse', 'has-cols', 'cols-3']}),

        ('Finance', {'fields': (('finance_submission_date','movement_sheet_no',), ('payment_date', 'utr_no',)), 'classes': ['collapse', 'has-cols', 'cols-3']}),
           )
    fieldsets_and_inlines_order = ('f', 'i', 'f', 'f', 'i', 'i')

    inlines = [VoucherDetailsInline, CourierDetailsInline, TransactionNotesInline]

    save_on_top = True

    list_per_page = 30

    class Media:
        js = ('/static/aasaan/ipcaccounts/ipc_accounts.js',)


admin.site.register(AccountsMaster, AccountsMasterAdmin)
admin.site.register(VoucherMaster, admin.ModelAdmin)
admin.site.register(EntityMaster, admin.ModelAdmin)
admin.site.register(ClassExpensesTypeMaster, admin.ModelAdmin)
admin.site.register(TeacherExpensesTypeMaster, admin.ModelAdmin)
admin.site.register(VoucherStatusMaster, admin.ModelAdmin)

