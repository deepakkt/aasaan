from django.contrib import admin
from .models import AccountsMaster, CourierDetails, TransactionNotes, VoucherMaster, EntityMaster, VoucherStatusMaster
from schedulemaster.models import ProgramSchedule
from contacts.models import Contact, IndividualRole, Zone, Center
from django.core.exceptions import ObjectDoesNotExist


class TransactionNotesInline(admin.StackedInline):
    model = TransactionNotes
    extra = 0
    exclude = ('created_by',)

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        obj.save()


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

        if not request.user.is_superuser and db_field.name == 'program_schedule':
            user_zones = [x.zone for x in request.user.aasaanuserzone_set.all()]
            user_zone_centers = [x.id for x in Center.objects.filter(zone__in=user_zones)]
            user_centers = [x.center.id for x in request.user.aasaanusercenter_set.all()] + \
                           user_zone_centers
            user_centers = list(set(user_centers))
            kwargs["queryset"] = ProgramSchedule.objects.filter(center__in=user_centers)

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
        center_schedules = AccountsMaster.objects.filter(center__in=user_centers)
        center_zonal_schedules = AccountsMaster.objects.filter(center__zone__in=user_zones)
        all_schedules = center_schedules | center_zonal_schedules
        all_schedules = all_schedules.distinct()

        return all_schedules


    list_display = ('__str__', 'tracking_no', 'amount', 'payment_date', 'utr_no', 'approval_status')
    list_filter = ('account_type', 'entity_name', 'voucher_status', 'nature_of_voucher')

    fieldsets = (
        ('', {
            'fields': ('account_type', 'tracking_no', 'entity_name', 'voucher_status', 'nature_of_voucher', 'voucher_date', 'center',
            'program_schedule', 'budget_code', 'teacher', 'head_of_expenses', 'expenses_description', 'party_name', 'amount')
        }),
        ('Approval', {'fields': (('approval_sent_date', 'approved_date', 'approval_status'),), 'classes': ['collapse', 'has-cols', 'cols-3']}),

        ('Finance', {'fields': (('finance_submission_date','movement_sheet_no',), ('payment_date', 'utr_no',)), 'classes': ['collapse', 'has-cols', 'cols-3']}),
           )
    inlines = [CourierDetailsInline, TransactionNotesInline]

    save_on_top = True

    list_per_page = 30

    class Media:
        js = ('/static/aasaan/ipcaccounts/ipc_accounts.js',)


admin.site.register(AccountsMaster, AccountsMasterAdmin)
admin.site.register(VoucherMaster, admin.ModelAdmin)
admin.site.register(EntityMaster, admin.ModelAdmin)
admin.site.register(VoucherStatusMaster, admin.ModelAdmin)