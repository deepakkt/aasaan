from django.contrib import admin
from .models import TravelRequest,Travellers
from .forms import TravelRequestForm
from contacts.models import Contact, IndividualRole, Zone, Center
from django.core.exceptions import ObjectDoesNotExist
from utils.filters import RelatedDropdownFilter

class TravellersInline(admin.TabularInline):
    model = Travellers
    extra = 1

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):

        if db_field.name == 'teacher':
            try:
                teacher_role = IndividualRole.objects.get(role_name='Teacher', role_level='ZO')
                _teacher_list = Contact.objects.filter(individualcontactrolezone__role=teacher_role)
                kwargs["queryset"] = _teacher_list.distinct()
            except ObjectDoesNotExist:
                kwargs["queryset"] = Contact.objects.none()

        return super(TravellersInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


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
            'fields': (('source', 'destination'),('onward_date', 'travel_mode'), ('status', 'zone'), ('remarks',)
                       ),
            'classes': ('has-cols', 'cols-2')
        }),
    )

    def make_email(modeladmin, request, queryset):
        pass

    make_email.short_description = "Send selected as Email"

    actions = [make_email]

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):

        if not request.user.is_superuser and db_field.name == 'zone':
            user_zones = [x.zone.id for x in request.user.aasaanuserzone_set.all()]
            kwargs["queryset"] = Zone.objects.filter(pk__in=user_zones)
        return super(TravelRequestAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    inlines = [TravellersInline,]

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
