from django.contrib import admin
from .models import TravelRequest
from .forms import TravelRequestForm
from contacts.models import Contact, IndividualRole, Zone, Center
from django.core.exceptions import ObjectDoesNotExist
from utils.filters import RelatedDropdownFilter, ChoiceDropdownFilter
from django.shortcuts import render
from django.utils import formats
from datetime import date, timedelta
from ipcaccounts.models import RCOAccountsMaster, VoucherDetails, AccountTypeMaster,EntityMaster,RCOVoucherStatusMaster,ExpensesTypeMaster, VoucherMaster
from django.contrib import messages
import json
from config.models import Configuration, SmartModel
from django.http import HttpResponse, HttpResponseNotFound, Http404,  HttpResponseRedirect


class TravelRequestAdmin(admin.ModelAdmin):
    form = TravelRequestForm
    list_display = ('status_flag', '__str__', 'source', 'destination', 'onward_date', 'zone', 'status', 'email_sent')
    list_editable = ('status',)
    list_display_links = ['status_flag', '__str__']
    save_on_top = True
    date_hierarchy = 'onward_date'
    list_filter = (('zone', RelatedDropdownFilter), ('status',ChoiceDropdownFilter))
    fieldsets = (
        ('', {
            'fields': (('source', 'destination'),),
            'classes': ('has-cols', 'cols-2')
        }),
        ('', {
            'fields': ('onward_date', 'travel_mode', 'zone', 'teacher', 'remarks')

        }),
        ('Booking details', {
            'fields': ('invoice_no', 'amount', 'attachments', 'invoice'),
            'classes': ('collapse', 'open')
        }),
    )
    filter_horizontal = ('teacher',)

    def create_voucher(self, request, queryset):
        rc = RCOAccountsMaster()
        rc.account_type = AccountTypeMaster.objects.get(id=3)
        amount = 0
        for tr in list(queryset):
            if tr.status=='VC' or tr.status=='CL' or tr.status=='PD' or tr.statur=='IP':
                self.message_user(request, "Voucher already created or processed", level=messages.WARNING)
                return
            rc.zone = tr.zone
            amount += tr.amount


            cft = Configuration.objects.get(configuration_key='IPC_ACCOUNTS_TRACKING_CONST')
            data = json.loads(cft.configuration_value)
            prefix = data[rc.zone.zone_name]['prefix']
            rc.budget_code = 'Teachers budget '+prefix
            rc.save()
            v1 = VoucherDetails()
            v1.voucher_type = 'BV'
            v1.nature_of_voucher = VoucherMaster.objects.get(id=4)
            v1.head_of_expenses = ExpensesTypeMaster.objects.get(id=5)
            v1.expenses_description = 'Booked tickets for Teachers'
            v1.party_name = 'Kathir Travel Line'
            v1.amount = amount
            v1.accounts_master = rc
            v1.save()

            v2 = VoucherDetails()
            v2.voucher_type = 'JV'
            v2.nature_of_voucher = VoucherMaster.objects.get(id=3)
            v2.head_of_expenses = ExpensesTypeMaster.objects.get(id=5)
            v2.expenses_description = 'Booked tickets for Teachers'
            v2.party_name = 'Kathir Travel Line'
            v2.amount = amount
            v2.accounts_master = rc
            v2.save()

            for tr in list(queryset):
                tr.status = 'VC'
                tr.save()

        return HttpResponseRedirect('/admin/ipcaccounts/rcoaccountsmaster/'+str(rc.id)+'/change/')

    create_voucher.short_description = "Create Vouchers"

    def email_ticket_passanger(self, request, queryset):
        pass

    email_ticket_passanger.short_description = "Email ticket to Teacher"

    def make_email(self, request, queryset):
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

    actions = [make_email, view_passanger_details, create_voucher, email_ticket_passanger]

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
