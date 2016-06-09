from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from .models import Brochures, BrochureMaster, StockPointMaster, StockPoint, BrochuresTransfer, BrochuresTransferItem, \
    StockPointAddress, BrochuresShipment, BrochureSet, BrochureSetItem


class BrochuresInline(admin.TabularInline):
    list_display = ('item', 'quantity', 'status')
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

    class Media:
        js = ('/static/aasaan/js/brochures.js',)

    def has_add_permission(self, request):
        return False


class BrochuresTransferAdmin(admin.ModelAdmin):
    inlines = [BrochuresTransferItemInline, BrochuresShipmentInline]
    list_filter = ('source_stock_point__zone',)
    list_display = (
        'transfer_type', 'source_stock_point', 'destination_stock_point', 'transfer_date', 'status')
    save_on_top = True
    exclude = ('save_new',)

    class Media:
        js = ('/static/aasaan/js/brochures_transfer.js',)

    def save_related(self, request, form, formsets, change):

        if form.instance.status == 'DD' or form.instance.status == 'TC':
            for formset in formsets:
                for fs in formset:
                    form_data = fs.cleaned_data
                    if form_data:
                        if form.instance.status == 'DD':
                            try:
                                sp = StockPoint.objects.get(stock_point=form.instance.destination_stock_point)
                            except ObjectDoesNotExist:
                                sp = StockPoint()
                                sp.stock_point = form.instance.destination_stock_point
                                sp.save()
                        else:
                            sp = StockPoint.objects.get(stock_point=form.instance.source_stock_point)
                        try:
                            brs = Brochures.objects.get(stock_point=sp, item=fs.instance.brochures)
                            brs.quantity = brs.quantity + fs.instance.quantity
                        except ObjectDoesNotExist:
                            brs = Brochures()
                            brs.stock_point = sp
                            brs.item = fs.instance.brochures
                            brs.quantity = fs.instance.quantity
                        brs.save()
        elif form.instance.status == 'NEW' and (
                            form.instance.transfer_type == 'SPSH' or form.instance.transfer_type == 'STPT'
                or form.instance.transfer_type == 'GUST'):
            for formset in formsets:
                for fs in formset:
                    form_data = fs.cleaned_data
                    if form_data:
                        sp = StockPoint.objects.get(stock_point=form.instance.source_stock_point)
                        try:
                            brs = Brochures.objects.get(stock_point=sp, item=fs.instance.brochures)
                            if not brs.quantity >= fs.instance.quantity:
                                raise ValidationError('Not enough Quantity')
                            else:
                                brs.quantity = brs.quantity - fs.instance.quantity
                                brs.save()
                        except ObjectDoesNotExist:
                            raise ValidationError('Not enough Quantity')

        super(BrochuresTransferAdmin, self).save_related(request, form, formsets, change)


class StockPointMasterAdmin(admin.ModelAdmin):
    inlines = [StockPointAddressInline]
    extra = 0
    list_filter = ('zone',)


class BrochureMasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'language', 'active', 'get_brochure_image')
    readonly_fields = ('brochure_image_display',)


class BrochuresSetAdmin(admin.ModelAdmin):
    inlines = [BrochureSetItemInline]


admin.site.register(BrochureMaster, BrochureMasterAdmin)
admin.site.register(StockPointMaster, StockPointMasterAdmin)
admin.site.register(StockPoint, BrochuresAdmin)
admin.site.register(BrochuresTransfer, BrochuresTransferAdmin)
admin.site.register(BrochureSet, BrochuresSetAdmin)
