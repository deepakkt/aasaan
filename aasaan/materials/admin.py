from django.contrib import admin
from .models import ClassMaterialsMaster, MaterialsRequest, ClassMaterialItem, MaterialTypeMaster, ClassTypeMaster,\
    CenterMaterialsMaster,CenterMaterialItem, CourierDetails,MaterialStatusMaster, KitsMaster, OtherMaterialsMasterItem,\
    KitsItem,OtherMaterialsMaster,MaterialsRequestIncharge, MaterialNotes
from contacts.models import Zone, Center
from utils.filters import RelatedDropdownFilter, ChoiceDropdownFilter
from django.utils import timezone

class MaterialNotesInline(admin.StackedInline):
    model = MaterialNotes
    extra = 0
    fields = ['note', ]

    def has_change_permission(self, request, obj=None):
        return False


class MaterialNotesInline1(admin.StackedInline):

    model = MaterialNotes
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

class ClassMaterialItemInline(admin.TabularInline):
    model = ClassMaterialItem
    extra = 1


class CenterMaterialItemInline(admin.TabularInline):
    model = CenterMaterialItem
    extra = 1


class OtherMaterialsMasterItemInline(admin.TabularInline):
    model = OtherMaterialsMasterItem
    extra = 1


class KitsItemItemInline(admin.TabularInline):
    model = KitsItem
    extra = 1


class CourierDetailsInline(admin.TabularInline):
    model = CourierDetails
    extra = 0

    def has_delete_permission(self, request, obj=None):
        return False


class MaterialsRequestAdmin(admin.ModelAdmin):
    inlines = [ClassMaterialItemInline, CenterMaterialItemInline, KitsItemItemInline, OtherMaterialsMasterItemInline, CourierDetailsInline, MaterialNotesInline1, MaterialNotesInline]
    list_filter = ('created', ('material_type', RelatedDropdownFilter), ('status', RelatedDropdownFilter), ('zone',RelatedDropdownFilter))
    list_display = ('__str__', 'status', 'material_type', 'created_by', 'created', 'delivery_date')
    list_editable = ('status',)
    really_hide_save_and_add_another_damnit = True

    fieldsets = (
        ('', {
            'fields': ('material_type', 'zone', 'center', 'delivery_date', 'status')
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

        return super(MaterialsRequestAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super(MaterialsRequestAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        if 'Materials Incharge' in [x.name for x in request.user.groups.all()]:
            return qs.filter(created_by=request.user)
        user_zones = [x.zone.id for x in request.user.aasaanuserzone_set.all()]
        return qs.filter(zone__in=user_zones)

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        obj.save()

    def save_related(self, request, form, formsets, change):
        for formset in formsets:
            for fs in formset:
                if isinstance(fs.instance, MaterialNotes) and fs.cleaned_data:
                    if fs.instance.pk is None:
                        fs.instance.material_request = form.instance
                        fs.instance.created_by = request.user.username
                        fs.instance.note = fs.instance.note + ' - created_by : ' + request.user.username + ' created at : ' + timezone.now().strftime(
                            "%b %d %Y %H:%M:%S")
                        fs.instance.save()
        super(MaterialsRequestAdmin, self).save_related(request, form, formsets, change)

    class Media:
        js = ('/static/aasaan/materials/materials_request.js',)


class MaterialsRequestInchargeAdmin(MaterialsRequestAdmin):
    pass


admin.site.register(ClassMaterialsMaster, admin.ModelAdmin)
admin.site.register(MaterialsRequest, MaterialsRequestAdmin)
admin.site.register(MaterialsRequestIncharge, MaterialsRequestInchargeAdmin)
admin.site.register(MaterialTypeMaster, admin.ModelAdmin)
admin.site.register(ClassTypeMaster, admin.ModelAdmin)
admin.site.register(CenterMaterialsMaster, admin.ModelAdmin)
admin.site.register(MaterialStatusMaster, admin.ModelAdmin)
admin.site.register(KitsMaster, admin.ModelAdmin)
admin.site.register(OtherMaterialsMaster, admin.ModelAdmin)

