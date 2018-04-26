from django.contrib import admin
from .models import TravelRequest
from .forms import TravelRequestForm
from contacts.models import Contact, IndividualRole, Zone, Center
from django.core.exceptions import ObjectDoesNotExist
from utils.filters import RelatedDropdownFilter
from django.shortcuts import render
from django.utils import formats
from datetime import date, timedelta

class TravelRequestAdmin(admin.ModelAdmin):
    form = TravelRequestForm
    list_display = ('status_flag', '__str__', 'source', 'destination', 'onward_date', 'zone', 'status', 'email_sent')
    list_editable = ('status',)
    list_display_links = ['status_flag', '__str__']
    save_on_top = True
    date_hierarchy = 'onward_date'
    list_filter = (('zone', RelatedDropdownFilter),)
    fieldsets = (
        ('', {
            'fields': (('source', 'destination'),),
            'classes': ('has-cols', 'cols-2')
        }),
        ('', {
            'fields': ('onward_date', 'travel_mode', 'zone', 'teacher', 'remarks')

        }),
        ('Booking details', {
            'fields': ('invoice_no', 'amount', 'attachments'),
            'classes': ('collapse', 'open')
        }),
    )
    filter_horizontal = ('teacher',)
    def make_email(modeladmin, request, queryset):
        pass

    make_email.short_description = "Send selected as Email"

    def view_passanger_details(self, request, queryset):
        all_tickets = []

        for tr in list(queryset):
            ticket_request = {}
            ticket_request['tracking_no'] = 'TR' + str(tr.id).zfill(6)
            ticket_request['zone'] = tr.zone.zone_name
            ticket_request['source'] = tr.source
            ticket_request['destination'] = tr.destination
            onward_date = formats.date_format(tr.onward_date, "DATE_FORMAT")
            ticket_request['onward_date'] = onward_date
            ticket_request['travel_mode'] = tr.get_travel_mode_display()
            ticket_request['remarks'] = tr.remarks
            traveller_details = list(tr.teacher.all())
            t_list = []
            for index, t in enumerate(traveller_details):
                age = 'Age not known'
                if t.date_of_birth:
                    age = (date.today() - t.date_of_birth) // timedelta(days=365.2425)
                t_dict = {}
                t_dict['SNo'] = str(index + 1)
                t_dict['full_name'] =t.full_name
                t_dict['age'] = t.get_gender_display() + ' - ' + str(age)
                t_dict['primary_mobile'] =t.primary_mobile
                t_list.append(t_dict)
            ticket_request['travellers'] = t_list
            all_tickets.append(ticket_request)

        return render(request,
                      'travels/view_details.html',
                      context={'travel_request':all_tickets})

    view_passanger_details.short_description = "View Passanger Details"

    actions = [make_email, view_passanger_details]

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):

        if not request.user.is_superuser and db_field.name == 'zone':
            user_zones = [x.zone.id for x in request.user.aasaanuserzone_set.all()]
            kwargs["queryset"] = Zone.objects.filter(pk__in=user_zones)
        return super(TravelRequestAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == 'teacher':
            try:
                teacher_role = IndividualRole.objects.get(role_name='Teacher', role_level='ZO')
                _teacher_list = Contact.objects.filter(individualcontactrolezone__role=teacher_role)
                kwargs["queryset"] = _teacher_list.distinct()
            except ObjectDoesNotExist:
                kwargs["queryset"] = Contact.objects.none()
            return super(TravelRequestAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    # filter tickets records based on user permissions
    def get_queryset(self, request):
        qs = super(TravelRequestAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        user_zones = [x.zone for x in request.user.aasaanuserzone_set.all()]
        return TravelRequest.objects.filter(zone__in=user_zones)

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        obj.save()

    class Media:
        js = ('/static/aasaan/travels/travels.js',)


admin.site.register(TravelRequest, TravelRequestAdmin)
