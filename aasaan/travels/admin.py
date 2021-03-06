from django.contrib import admin
from .models import TravelRequest, TrTravelRequest, AgentTravelRequest, TravelNotes, Attachment, Others
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
from AasaanUser.models import AasaanUserContact, AasaanUserZone
from django.contrib.auth.models import User
from django.utils import timezone
from .forms import TravelForm, TravelOtherDetailsInlineFormset


class OthersInline(admin.TabularInline):
    formset = TravelOtherDetailsInlineFormset
    model = Others
    extra = 0
    max_num = 10

class AttachmentInline(admin.StackedInline):
    model = Attachment
    extra = 1
    max_num = 5

class TravelNotesInline(admin.StackedInline):
    model = TravelNotes
    extra = 0
    fields = ['note', ]

    def has_change_permission(self, request, obj=None):
        return False


class TravelNotesInline1(admin.StackedInline):

    model = TravelNotes
    extra = 0
    readonly_fields = ['note',]

    fieldsets = [
        ('', {'fields': ('note',), }),
        ('Hidden Fields',
         {'fields': ['created_by',], 'classes': ['hidden']}),
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class BaseTravelAdmin(admin.ModelAdmin):

    date_hierarchy = 'onward_date'
    inlines = [OthersInline, TravelNotesInline1, TravelNotesInline, AttachmentInline]

    def save_related(self, request, form, formsets, change):
        for formset in formsets:
            for fs in formset:
                if isinstance(fs.instance, TravelNotes) and fs.cleaned_data:
                    if fs.instance.pk is None:
                        fs.instance.travel_request = form.instance
                        fs.instance.created_by = request.user.username
                        fs.instance.note = fs.instance.note + ' - created_by : ' + request.user.username + ' created at : ' + timezone.now().strftime(
                            "%b %d %Y %H:%M:%S")
                        fs.instance.save()
        super(BaseTravelAdmin, self).save_related(request, form, formsets, change)

    class Media:
        js = ('/static/aasaan/travels/travels.js',)


class TravelRequestAdmin(BaseTravelAdmin):
    form = TravelForm
    list_display = ('status_flag', 'ticket_number', '__str__', 'source', 'destination', 'onward_date', 'zone', 'status', 'invoice_no', 'created_by')
    list_editable = ('status',)
    list_display_links = ['status_flag', '__str__', 'ticket_number']
    list_filter = ('created',('travel_mode', ChoiceDropdownFilter), ('status', ChoiceDropdownFilter), ('zone', RelatedDropdownFilter), )
    search_fields = ('source', 'destination', 'teacher__first_name', 'teacher__last_name', 'created_by__first_name', 'invoice_no', 'ticket_number')
    fieldsets = (
        ('', {
            'fields': ('ticket_number', 'source', 'destination', 'onward_date', 'travel_mode', 'travel_class', 'zone', 'teacher', 'is_others')

        }),
        ('Booking details', {
            'fields': ('status', 'booked_date', 'invoice_no', 'amount', 'attachments', 'invoice', 'refund_amount'),
            'classes': ('collapse', 'open')
        }),
    )
    filter_horizontal = ('teacher',)

    def create_voucher(self, request, queryset):
        accounts_voucher = RCOAccountsMaster()
        accounts_voucher.account_type = AccountTypeMaster.objects.get(id=3)
        amount = 0
        for tr in list(queryset):
            if tr.status=='VC' or tr.status=='CL' or tr.status=='PD' or tr.status=='IP':
                self.message_user(request, "Voucher already created or processed or Inprogress. Update booking details to create vouchers", level=messages.WARNING)
                return
            accounts_voucher.zone = tr.zone
            amount += tr.amount
            cft = Configuration.objects.get(configuration_key='IPC_ACCOUNTS_TRACKING_CONST')
            data = json.loads(cft.configuration_value)
            prefix = data[accounts_voucher.zone.zone_name]['prefix']
            accounts_voucher.budget_code = 'Teachers budget '+prefix
            accounts_voucher.save()
            bank_voucher = VoucherDetails()
            bank_voucher.voucher_type = 'BV'
            bank_voucher.nature_of_voucher = VoucherMaster.objects.get(id=4)
            bank_voucher.head_of_expenses = ExpensesTypeMaster.objects.get(id=5)
            bank_voucher.expenses_description = 'Booked Teachers Tickets'
            bank_voucher.party_name = 'Kathir Travel Line'
            bank_voucher.amount = amount
            bank_voucher.accounts_master = accounts_voucher
            bank_voucher.save()

            journal_voucher= VoucherDetails()
            journal_voucher.voucher_type = 'JV'
            journal_voucher.nature_of_voucher = VoucherMaster.objects.get(id=3)
            journal_voucher.head_of_expenses = ExpensesTypeMaster.objects.get(id=5)
            journal_voucher.expenses_description = 'Booked tickets for Teachers'
            journal_voucher.party_name = 'Kathir Travel Line'
            journal_voucher.amount = amount
            journal_voucher.accounts_master = accounts_voucher
            journal_voucher.save()

            for tr in list(queryset):
                tr.status = 'VC'
                tr.voucher = accounts_voucher
                tr.save()

        return HttpResponseRedirect('/admin/ipcaccounts/rcoaccountsmaster/'+str(accounts_voucher.id)+'/change/')

    create_voucher.short_description = "Create Vouchers"

    def email_ticket_passanger(self, request, queryset):
        pass

    email_ticket_passanger.short_description = "Email ticket to Teacher"

    def make_email(self, request, queryset):
        pass

    make_email.short_description = "Send Email to Travel Agency"

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

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
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
        if 'Teacher' in [x.name for x in request.user.groups.all()]:
            return TravelRequest.objects.filter(created_by=request.user)
        else:
            user_zones = [x.zone for x in request.user.aasaanuserzone_set.all()]
            return TravelRequest.objects.filter(zone__in=user_zones)


    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        obj.save()

    def get_actions(self, request):
        actions = super(TravelRequestAdmin, self).get_actions(request)
        if request.user.is_superuser:
            return actions
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class TeachersTravelRequestAdmin(BaseTravelAdmin):
    list_editable = []
    list_filter = []
    list_display = ('status_flag', 'ticket_number', '__str__', 'source', 'destination', 'onward_date', 'status')
    search_fields = []
    list_display_links = ['status_flag', '__str__', 'ticket_number']

    def get_actions(self, request):
        actions = super(TeachersTravelRequestAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    fieldsets = (
        ('', {
            'fields': ('ticket_number', 'source', 'destination','onward_date', 'travel_mode', 'travel_class', 'zone')
        }),
    )

    def get_queryset(self, request):
        return TravelRequest.objects.filter(created_by=request.user, status__in=['IP', 'BO','BK', 'CL', 'CB'])

    def save_model(self, request, obj, form, change):
        login_user = User.objects.get(username=request.user.username)
        contact = AasaanUserContact.objects.get(user=login_user)
        obj.created_by = request.user
        obj.save()
        obj.teacher.add(contact.contact)

    def get_form(self, request, obj=None, **kwargs):
        login_user = User.objects.get(username=request.user.username)
        try:
            AasaanUserContact.objects.get(user=login_user)
        except AasaanUserContact.DoesNotExist:
            self.message_user(request,
                              "Contact is not mapped to User. Contact aasaan admin",
                              level=messages.WARNING)
        try:
            AasaanUserZone.objects.get(user=login_user)
        except AasaanUserZone.DoesNotExist:
            self.message_user(request,
                              "Zone is not mapped to User. Contact aasaan admin",
                              level=messages.WARNING)

        return super(TeachersTravelRequestAdmin, self).get_form(request, obj=None, **kwargs)


class AgentTravelRequestAdmin(BaseTravelAdmin):
    date_hierarchy = 'created'
    list_display = ('status_flag', 'ticket_number', '__str__', 'source', 'destination', 'onward_date', 'zone', 'status', 'created_by')
    list_editable = ('status',)
    list_display_links = ['status_flag', '__str__', 'ticket_number']
    list_filter = ('onward_date', ('travel_mode', ChoiceDropdownFilter), ('status', ChoiceDropdownFilter),
                   ('zone', RelatedDropdownFilter),)
    search_fields = ('source', 'destination', 'teacher__first_name', 'teacher__last_name', 'created_by__first_name','invoice_no', 'ticket_number')
    fieldsets = (
        ('', {
            'fields': ('ticket_number','source', 'destination', 'onward_date', 'travel_mode', 'travel_class', 'zone', 'remarks')

        }),
        ('Passanger details', {
            'fields': ('teacher', )
        }),
        ('Booking details', {
            'fields': ('status', 'booked_date', 'invoice_no', 'amount', 'attachments', 'invoice', 'refund_amount'),
            'classes': ('collapse', 'open')
        }),
    )
    readonly_fields = ['source', 'destination', 'teacher', 'onward_date', 'travel_mode', 'travel_class', 'zone', 'remarks']

    def get_queryset(self, request):
       return TravelRequest.objects.filter(status__in=['BO', 'BK', 'CL', 'CB'])

    def get_actions(self, request):
        actions = super(AgentTravelRequestAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(TravelRequest, TravelRequestAdmin)
admin.site.register(TrTravelRequest, TeachersTravelRequestAdmin)
admin.site.register(AgentTravelRequest, AgentTravelRequestAdmin)


