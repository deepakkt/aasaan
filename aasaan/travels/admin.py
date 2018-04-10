from django.contrib import admin
from .models import TravelRequest,Travellers
from .forms import TravelRequestForm
from contacts.models import Contact, IndividualRole, Zone, Center
from django.core.exceptions import ObjectDoesNotExist


class TravellersInline(admin.TabularInline):
    model = Travellers
    extra = 0

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
    list_display = ('status_flag', '__str__', '_from', '_to', 'onward_date', 'status')
    list_editable = ('status',)
    list_display_links = ['status_flag', '__str__']

    fieldsets = (
        ('', {
            'fields': (('_from', '_to'),('onward_date', 'travel_mode'), ('status', 'zone'), ('remarks',)
                       ),
            'classes': ('has-cols', 'cols-2')
        }),
    )

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):

        if not request.user.is_superuser and db_field.name == 'zone':
            user_zones = [x.zone.id for x in request.user.aasaanuserzone_set.all()]
            kwargs["queryset"] = Zone.objects.filter(pk__in=user_zones)
        return super(TravelRequestAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    inlines = [TravellersInline,]
    class Media:
        js = ('/static/aasaan/ipcaccounts/treasurer.js',)

admin.site.register(TravelRequest, TravelRequestAdmin)
