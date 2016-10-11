from django.contrib import admin
from .models import TravelRequest, AgentMaster, TravelModeMaster, BudgetCodeMaster, BookingDetails, TravellerDetails, \
    TicketDetails, AddtionalDetails
from daterange_filter.filter import DateRangeFilter
from django.utils.text import slugify

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


class TravelRequestAdmin(admin.ModelAdmin):
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

admin.site.register(AgentMaster, admin.ModelAdmin)
admin.site.register(TravelModeMaster, admin.ModelAdmin)
admin.site.register(BudgetCodeMaster, admin.ModelAdmin)
admin.site.register(TravelRequest, TravelRequestAdmin)