from django.contrib import admin
from .models import Attachment, ServiceRequestNotes, ServiceRequest, ServiceStatusMaster, IPCSystemMaster, IPCServiceRequest
from contacts.models import Zone, Center
from utils.filters import RelatedDropdownFilter, ChoiceDropdownFilter
from django.utils import timezone


class AttachmentInline(admin.StackedInline):
    model = Attachment
    extra = 1
    max_num = 10

class ServiceRequestNotesInline(admin.StackedInline):
    model = ServiceRequestNotes
    extra = 0
    fields = ['note', ]

    def has_change_permission(self, request, obj=None):
        return False


class ServiceRequestNotesInline1(admin.StackedInline):

    model = ServiceRequestNotes
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


class ServiceRequestAdmin(admin.ModelAdmin):
    inlines = [ServiceRequestNotesInline1, ServiceRequestNotesInline, AttachmentInline]
    list_filter = ('created', ('system_type', RelatedDropdownFilter), ('status', RelatedDropdownFilter), ('priority',ChoiceDropdownFilter), ('zone',RelatedDropdownFilter))
    list_display = ('status_flag', '__str__', 'system_type', 'status', 'priority', 'created_by', 'expected_date', 'exp_resolved_date')
    list_editable = ('status',)
    really_hide_save_and_add_another_damnit = True
    list_display_links = ['status_flag', '__str__']

    fieldsets = (
        ('', {
            'fields': ('system_type', 'status', 'title', 'description', 'priority', 'zone', 'center', 'expected_date',
                       'exp_resolved_date', 'resolved_date')
        }),
    )

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):

        if not request.user.is_superuser and db_field.name == 'zone':
            user_zones = [x.zone.id for x in request.user.aasaanuserzone_set.all()]
            kwargs["queryset"] = Zone.objects.filter(pk__in=user_zones)

        if not request.user.is_superuser and db_field.name == 'center':
            user_zones = [x.zone for x in request.user.aasaanuserzone_set.all()]
            user_zone_centers = [x.id for x in Center.objects.filter(zone__in=user_zones)]
            user_centers = [x.center.id for x in request.user.aasaanusercenter_set.all()] +\
                user_zone_centers
            user_centers = list(set(user_centers))
            kwargs["queryset"] = Center.objects.filter(pk__in=user_centers)

        return super(ServiceRequestAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super(ServiceRequestAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        if 'Regional Coordination Office' in [x.name for x in request.user.groups.all()]:
            user_zones = [x.zone.id for x in request.user.aasaanuserzone_set.all()]
            return qs.filter(zone__in=user_zones)
        return qs.filter(created_by=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        obj.save()

    def save_related(self, request, form, formsets, change):
        for formset in formsets:
            for fs in formset:
                if isinstance(fs.instance, ServiceRequestNotes) and fs.cleaned_data:
                    if fs.instance.pk is None:
                        fs.instance.material_request = form.instance
                        fs.instance.created_by = request.user.username
                        fs.instance.note = fs.instance.note + ' - created_by : ' + request.user.username + ' created at : ' + timezone.now().strftime(
                            "%b %d %Y %H:%M:%S")
                        fs.instance.save()
        super(ServiceRequestAdmin, self).save_related(request, form, formsets, change)

    class Media:
        js = ('/static/aasaan/servicedesk/service_request.js',)


class IPCServiceRequestAdmin(ServiceRequestAdmin):
    fieldsets = (
        ('', {
            'fields': ('system_type', 'status', 'title', 'description', 'priority', 'zone', 'center', 'expected_date',
                       )
        }),
    )

admin.site.register(ServiceStatusMaster, admin.ModelAdmin)
admin.site.register(IPCSystemMaster, admin.ModelAdmin)
admin.site.register(ServiceRequest, ServiceRequestAdmin)
admin.site.register(IPCServiceRequest, IPCServiceRequestAdmin)