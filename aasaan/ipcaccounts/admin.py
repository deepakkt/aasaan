from django.contrib import admin
from .models import AccountsMaster, CourierDetails, TransactionNotes, VoucherMaster, EntityMaster, VoucherStatusMaster


class TransactionNotesInline(admin.StackedInline):
    model = TransactionNotes
    extra = 0
    exclude = ('created_by',)

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
    #exclude = ('tracking_no',)
    #fields = ('tracking_no', 'voucher_status', 'entity_name', 'voucher_date', 'nature_of_voucher', 'center', 'expense_type',
              #'program_schedule', 'budget_code')
    list_display = ('tracking_no', 'voucher_status', 'nature_of_voucher',)

    fieldsets = (
        ('', {
            'fields': ('account_type', 'tracking_no', 'entity_name', 'voucher_status', 'nature_of_voucher', 'voucher_date', 'center',
            'program_schedule', 'budget_code', 'teacher', 'head_of_expenses', 'expenses_description', 'party_name', 'amount')
        }),
        ('Approval', {'fields': (('approval_sent_date', 'approved_date', 'approval_status'),), 'classes': ['collapse', 'has-cols', 'cols-3']}),

        ('Finance', {'fields': (('finance_submission_date','movement_sheet_no',), ('payment_date', 'utr_no',)), 'classes': ['collapse', 'has-cols', 'cols-3']}),
    )
    #readonly_fields = ('tracking_no',)
    inlines = [CourierDetailsInline, TransactionNotesInline]

    save_on_top = True

    list_per_page = 30

    class Media:
        js = ('/static/aasaan/js/ipc_accounts.js',)



admin.site.register(AccountsMaster, AccountsMasterAdmin)
admin.site.register(VoucherMaster, admin.ModelAdmin)
admin.site.register(EntityMaster, admin.ModelAdmin)
admin.site.register(VoucherStatusMaster, admin.ModelAdmin)