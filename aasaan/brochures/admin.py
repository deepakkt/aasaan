from contacts.models import Zone
from django.contrib import admin
from django_markdown.admin import MarkdownInlineAdmin
from .models import Brochures, BrochureMaster, StockPointMaster, StockPoint, BrochuresTransaction, \
    BrochuresTransactionItem, TransactionTypeMaster, \
    StockPointAddress, BrochuresShipment, BrochureSet, BrochureSetItem, BroucherTransferNote, StockPointNote
import datetime
from django.utils import formats
from schedulemaster.models import ProgramSchedule


class BrochuresInline(admin.TabularInline):
    fields = ('item', 'quantity', 'status', 'brochure_image')
    model = Brochures
    extra = 1
    can_delete = False

    def has_add_permission(self, request):
        return False


class BrochureSetItemInline(admin.TabularInline):
    model = BrochureSetItem
    extra = 1

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'item':
            kwargs["queryset"] = BrochureMaster.active_objects.all()
        return super(BrochureSetItemInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class StockPointAddressInline(admin.StackedInline):
    model = StockPointAddress
    extra = 0
    max_num = 1


class BrochuresTransactionItemInline(admin.TabularInline):
    model = BrochuresTransactionItem
    extra = 0
    can_delete = False
    fields = ('item', 'sent_quantity', 'received_quantity')

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'item':
            kwargs["queryset"] = BrochureMaster.active_objects.all()
        return super(BrochuresTransactionItemInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def has_add_permission(self, request, obj=None):
        if obj:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if obj:
            return False
        return True


class BrochuresShipmentInline(admin.StackedInline):
    model = BrochuresShipment
    extra = 1
    max_num = 1
    fieldsets = (
        ('', {
            'fields': (('sent_from', 'sent_to', 'sent_date'), ('courier_vendor', 'courier_no', 'courier_status'),
                       ('received_date', 'remarks')),
            'classes': ('has-cols', 'cols-3')
        }),
    )


class BroucherTransferNoteInline(MarkdownInlineAdmin, admin.TabularInline):
    model = BroucherTransferNote
    extra = 1
    can_delete = False


class StockPointNoteInline(MarkdownInlineAdmin, admin.TabularInline):
    model = StockPointNote
    extra = 0
    can_delete = False


class BrochuresAdmin(admin.ModelAdmin):
    fieldsets = (
        ('', {
            'fields': (('name', 'contact_name'), ('zone', 'contact_phone')),
            'classes': ('has-cols', 'cols-2')
        }),
    )
    list_display = ('name', 'zone', 'contact_name', 'contact_phone')
    inlines = [BrochuresInline, StockPointNoteInline]
    list_per_page = 30
    list_filter = ('zone',)

    class Media:
        js = ('/static/aasaan/js/brochures.js',)

    def has_add_permission(self, request):
        return False


class ZoneFilter(admin.SimpleListFilter):
    title = 'zones'
    parameter_name = 'zones'

    def lookups(self, request, model_admin):
        return tuple([(x.zone_name, x.zone_name) for x in Zone.objects.all()])

    def queryset(self, request, queryset):
        if self.value():
            zone = Zone.objects.filter(zone_name=self.value())
            src_sp_brochures = BrochuresTransaction.objects.filter(source_stock_point__zone__in=zone)
            dest_sp_brochures = BrochuresTransaction.objects.filter(destination_stock_point__zone__in=zone)
            dest_sch_brochures = BrochuresTransaction.objects.filter(
                destination_program_schedule__center__zone__in=zone)
            brochure_trans_all = src_sp_brochures | dest_sp_brochures | dest_sch_brochures
            return brochure_trans_all


class BrochuresTransactionAdmin(admin.ModelAdmin):

    def get_changeform_initial_data(self, request):
        if request.user.is_superuser:
            pass
        get_data = super(BrochuresTransactionAdmin, self).get_changeform_initial_data(request)
        user_zones = [x.zone for x in request.user.aasaanuserzone_set.all()]
        if user_zones:
            get_data['zone'] = user_zones[0].pk if user_zones[0] else []
            get_data['destination_program_schedule'] = ProgramSchedule.objects.filter(center__zone__in=user_zones)
            return get_data

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'source_stock_point' or db_field.name == 'destination_stock_point':
            kwargs["queryset"] = StockPointMaster.active_objects.all()
        if db_field.name == 'transfer_type' and not request.user.is_superuser:
            kwargs["queryset"] = TransactionTypeMaster.objects.filter(admin=False)
        return super(BrochuresTransactionAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def __init__(self, *args, **kwargs):
        self.transfer_id = None
        super(BrochuresTransactionAdmin, self).__init__(*args, **kwargs)

    inlines = [BrochuresTransactionItemInline, BrochuresShipmentInline, BroucherTransferNoteInline]
    list_filter = (ZoneFilter, 'status')
    list_display = (
        'transfer_type', 'source', 'destination', 'transaction_date', 'get_status')
    save_on_top = True

    fieldsets = [
        ('', {'fields': ('transfer_type', 'status', 'brochure_set', 'source_printer', 'source_stock_point',
                         'destination_stock_point', 'zone', 'destination_program_schedule',
                         'guest_name', 'guest_phone', 'guest_email'), }),
        ('Hidden Fields',
         {'fields': [('transaction_status',)], 'classes': ['hidden']}),
    ]

    class Media:
        js = ('/static/aasaan/js/brochures_transfer.js', '/static/aasaan/js/disable_notes_brochures_v2.js',)

    def get_queryset(self, request):
        qs = super(BrochuresTransactionAdmin, self).get_queryset(request)

        # give entire set if user is a superuser irrespective of zone
        if request.user.is_superuser:
            return qs

        user_zones = [x.zone.id for x in request.user.aasaanuserzone_set.all()]
        src_sp_brochures = BrochuresTransaction.objects.filter(source_stock_point__zone__in=user_zones)
        dest_sp_brochures = BrochuresTransaction.objects.filter(destination_stock_point__zone__in=user_zones)
        dest_sch_brochures = BrochuresTransaction.objects.filter(
            destination_program_schedule__center__zone__in=user_zones)
        brochure_trans_all = src_sp_brochures | dest_sp_brochures | dest_sch_brochures
        return brochure_trans_all

    def save_model(self, request, obj, form, change):
        self.transfer_id = obj.id
        super(BrochuresTransactionAdmin, self).save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        trans_type = form.instance.transfer_type.value
        status = form.instance.status
        if self.transfer_id is None:
            if trans_type == 'ABSP':
                add_brochure(formsets, form.instance.source_stock_point)
            elif trans_type == 'PRSP' or trans_type == 'SCSP':
                add_brochure(formsets, form.instance.destination_stock_point)
            elif trans_type == 'DBSP':
                delete_brochure(formsets, form.instance.source_stock_point)
            elif trans_type == 'SPSC' or trans_type == 'SPSP' or trans_type == 'SPGT':
                if status == 'NEW' or status == 'DD':
                    delete_brochure(formsets, form.instance.source_stock_point)
        if trans_type == 'SPSC' or trans_type == 'SPSP' or trans_type == 'SPGT':
            if status == 'TC':
                add_brochure(formsets, form.instance.source_stock_point)
            if status == 'DD':
                transfer_stock(request, form, formsets)
        super(BrochuresTransactionAdmin, self).save_related(request, form, formsets, change)


def add_brochure(formsets, stock_point):
    for formset in formsets:
        for fs in formset:
            if isinstance(fs.instance, BrochuresTransactionItem) and fs.cleaned_data:
                try:
                    brochure = Brochures.objects.get(stock_point=stock_point, item=fs.instance.item)
                    brochure.quantity = brochure.quantity + fs.instance.sent_quantity
                    brochure.save()
                except Brochures.DoesNotExist:
                    brochure = Brochures()
                    brochure.stock_point = stock_point
                    brochure.item = fs.instance.item
                    brochure.quantity = fs.instance.sent_quantity
                    brochure.save()


def delete_brochure(formsets, stock_point):
    for formset in formsets:
        for fs in formset:
            if isinstance(fs.instance, BrochuresTransactionItem) and fs.cleaned_data:
                brochure = Brochures.objects.get(stock_point=stock_point, item=fs.instance.item)
                brochure.quantity = brochure.quantity - fs.instance.sent_quantity
                brochure.save()


def transfer_stock(request, form, formsets):
    transfer_note = ''
    is_note = False
    for formset in formsets:
        for fs in formset:
            if isinstance(fs.instance, BrochuresTransactionItem) and fs.cleaned_data:
                if fs.instance.item:
                    stock_point = form.instance.destination_stock_point
                    try:
                        brochure = Brochures.objects.get(stock_point=stock_point, item=fs.instance.item)
                        if fs.instance.received_quantity < fs.instance.sent_quantity:
                            brochure.quantity = brochure.quantity + fs.instance.received_quantity
                            transfer_note = transfer_note + brochure.item.__str__() + 'sent quantity is ' + str(
                                fs.instance.sent_quantity) + ' but received only ' + str(
                                fs.instance.received_quantity)
                            is_note = True
                        else:
                            brochure.quantity = brochure.quantity + fs.instance.sent_quantity
                    except Brochures.DoesNotExist:
                        brochure = Brochures()
                        brochure.stock_point = stock_point
                        brochure.item = fs.instance.item
                        brochure.quantity = fs.instance.sent_quantity
                    brochure.save()
    if is_note:
        formatted_datetime = formats.date_format(datetime.datetime.now(), "DATETIME_FORMAT")
        t_note = BroucherTransferNote()
        t_note.brochure_transfer = form.instance
        t_note.note = "Quantity Lost/Damaged during Transfer :" + transfer_note + '''\n-----------------------\n %s \n %s''' % request.user, formatted_datetime
        t_note.save()


class StockPointMasterAdmin(admin.ModelAdmin):
    inlines = [StockPointAddressInline]
    list_display = ('name', 'zone', 'contact_name', 'contact_phone')
    extra = 0
    list_filter = ('zone',)


class BrochureMasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'language', 'active', 'get_brochure_image')
    readonly_fields = ('brochure_image_display',)


class TransactionTypeMasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'admin',)
    list_editable = ('admin',)


class BrochuresSetAdmin(admin.ModelAdmin):
    inlines = [BrochureSetItemInline]


admin.site.register(BrochureMaster, BrochureMasterAdmin)
admin.site.register(StockPointMaster, StockPointMasterAdmin)
admin.site.register(StockPoint, BrochuresAdmin)
admin.site.register(BrochuresTransaction, BrochuresTransactionAdmin)
admin.site.register(BrochureSet, BrochuresSetAdmin)
admin.site.register(TransactionTypeMaster, TransactionTypeMasterAdmin)
