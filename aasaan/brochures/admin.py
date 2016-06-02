from django.contrib import admin
from .models import Brochures, BrochureMaster, StockPointMaster, StockPoint, BrochuresTransfer, BrochuresTransferItem, \
    StockPointAddress, BrochuresShipment, BrochureSet, BrochureSetItem


# Register your models here.


class BrochuresInline(admin.TabularInline):
    list_display = ('item', 'quantity', 'status', 'remarks')
    # readonly_fields = ('item', 'quantity')
    model = Brochures
    extra = 1
    can_delete = False

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        result = list(set(
                [field.name for field in self.opts.local_fields] +
                [field.name for field in self.opts.local_many_to_many]
            ))
        result.remove('id')
        return result


class BrochureSetItemInline(admin.TabularInline):
    model = BrochureSetItem
    extra = 1


class StockPointAddressInline(admin.StackedInline):
    model = StockPointAddress
    extra = 0
    max_num = 1

    # def has_delete_permission(self, request, obj=None):
    #     return False


class BrochuresTransferItemInline(admin.TabularInline):
    model = BrochuresTransferItem
    extra = 1


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


class BrochuresAdmin(admin.ModelAdmin):
    list_display = ('stock_point',)
    fields = ('stock_point',)
    inlines = [BrochuresInline]
    list_per_page = 30
    readonly_fields = ('stock_point',)
    extra_context = {}
    extra_context['readonly'] = True
    extra_context['really_hide_save_and_add_another_damnit'] = True

    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     extra_context = extra_context or {}
    #     # extra_context['readonly'] = True
    #     extra_context['really_hide_save_and_add_another_damnit'] = True
    #     extra_context['show_save_and_add_another'] = False,
    #     extra_context['show_save_and_continue'] = False
    #     extra_context['show_save'] = False
    #     return super(BrochuresAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)
    #
    # def has_add_permission(self, request):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False

    class Media:
        js = ('/static/aasaan/js/brochures.js',)

    # def has_change_permission(self, request, obj=None):
    #     return False

class BrochuresTransferAdmin(admin.ModelAdmin):
    inlines = [BrochuresTransferItemInline, BrochuresShipmentInline]
    list_filter = ('source_stock_point__zone',)
    list_display = ('transfer_type', 'source_stock_point', 'destination_stock_point', 'transfer_date', 'status')

    class Media:
        js = ('/static/aasaan/js/brochures.js',)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        # extra_context['readonly'] = True
        extra_context['show_save_and_add_another'] = False
        extra_context['really_hide_save_and_add_another_damnit'] = True
        return super(BrochuresTransferAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

class StockPointMasterAdmin(admin.ModelAdmin):
    inlines = [StockPointAddressInline]
    extra = 0
    list_filter = ('zone',)


class BrochureMasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'language', 'active', 'get_brochure_image')

    readonly_fields = ('brochure_image_display',)


class BrochuresSetAdmin(admin.ModelAdmin):
    inlines = [BrochureSetItemInline]

# Register your models here.
admin.site.register(BrochureMaster, BrochureMasterAdmin)
admin.site.register(StockPointMaster, StockPointMasterAdmin)
admin.site.register(StockPoint, BrochuresAdmin)
admin.site.register(BrochuresTransfer, BrochuresTransferAdmin)
admin.site.register(BrochureSet, BrochuresSetAdmin)
