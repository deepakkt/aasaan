from django.contrib import admin
from .models import TravelRequest, AgentMaster, TravelModeMaster, BudgetCodeMaster, BookingDetails, TravellerDetails, \
    TicketDetails, AddtionalDetails
from daterange_filter.filter import DateRangeFilter
from django.utils.text import slugify
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from import_export.admin import ImportExportMixin, ExportActionModelAdmin, ExportMixin
from import_export.formats import base_formats
from import_export import fields
from import_export.widgets import ForeignKeyWidget
import tablib
class BookingDetailsInline(admin.StackedInline):
    model = BookingDetails
    extra = 1
    max_num = 5
    fieldsets = (
        ('', {
            'fields': (('date_of_journey', 'date_of_booking'), ('source', 'destination'),
                       ('travel_mode', 'description'), ('booked_by')),
            'classes': ('has-cols', 'cols-2')
        }),
    )


class TravellerDetailsInline(admin.StackedInline):
    model = TravellerDetails
    extra = 1
    max_num = 5
    fieldsets = (
        ('', {
            'fields': (('traveller', 'non_ipc_contacts'),
                       ('zone', 'status'), ('fare', 'refund_amount'), ('budget_code', 'purpose')),
            'classes': ('has-cols', 'cols-2')
        }),
    )


class TicketDetailsInline(admin.TabularInline):
    model = TicketDetails
    extra = 1


class AddtionalDetailsInline(admin.TabularInline):
    model = AddtionalDetails
    extra = 1
    max_num = 1


def send_email(modeladmin, request, queryset):
    email_list = []
    for qs in queryset:
        t = TravellerDetails.objects.get(request__pk=qs.pk)
        email_list.append(t.traveller.primary_email)
    print(email_list)
send_email.short_description = "Send Email"


class TravelRequestResource(resources.ModelResource):
    formats = base_formats.XLS
    zone = fields.Field(column_name='zone', attribute='travellerdetails',
                            widget=ForeignKeyWidget(TravellerDetails, 'zone'))
    #
    # def export(self, queryset=None):
    #     if queryset is None:
    #         queryset = self.get_queryset()
    #     headers = self.get_export_headers()
    #     data = tablib.Dataset(headers=headers)
    #     for obj in queryset.iterator():
    #             data.append(self.export_resource(obj))
    #     return data
    class Meta:
        model = TravelRequest
        fields = ('zone', )

        # widgets = {
        #         'request_date': {'format': '%d.%m.%Y'},
        #         }


class TravelRequestAdmin(ImportExportActionModelAdmin):
    fieldsets = (
        ('',
         {
             'fields': (('status', 'request_mode', 'request_date'), ('total_fare', 'refund_amount', 'cancellation_charge')),
             'classes': ('has-cols', 'cols-3')
         }),
    )
    list_display = ('traveller', 'travel_details', 'get_status',)
    list_display_links = ('traveller', 'travel_details')
    inlines = [BookingDetailsInline, TravellerDetailsInline, TicketDetailsInline, AddtionalDetailsInline]
    save_on_top = True
    list_filter = ('status', 'travellerdetails__zone', ('bookingdetails__date_of_booking', DateRangeFilter),
                   ('bookingdetails__date_of_journey', DateRangeFilter), ('request_date', DateRangeFilter), 'bookingdetails__booked_by',
                   'bookingdetails__travel_mode')
    actions = [send_email]
    formats = [base_formats.XLS,]
    to_encoding = 'utf-8'
    resource_class = TravelRequestResource

admin.site.register(AgentMaster, admin.ModelAdmin)
admin.site.register(TravelModeMaster, admin.ModelAdmin)
admin.site.register(BudgetCodeMaster, admin.ModelAdmin)
admin.site.register(TravelRequest, TravelRequestAdmin)