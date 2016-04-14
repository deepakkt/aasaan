from django.contrib import admin
from .models import LoanTransaction, ItemMaster, Transaction, CenterMaterial, \
    CenterItemNotes, CenterMaterial, MaterialsCenter


class CenterItemNotesInline(admin.TabularInline):
    model = CenterItemNotes
    extra = 1

    def has_delete_permission(self, request, obj=None):
        return False


class CenterMaterialInline(admin.TabularInline):
    model = CenterMaterial
    extra = 1

    def has_delete_permission(self, request, obj=None):
        return False


class MaterialsAdmin(admin.ModelAdmin):
    #filter center records based on user permissions
    def get_queryset(self, request):
        qs = super(MaterialsAdmin, self).get_queryset(request)

        #give entire set if user is a superuser irrespective of zone and center assignments
        if (request.user.is_superuser) or ('view-all' in [x.name for x in request.user.groups.all()]):
            return qs

        # get all centers this user belongs to
        user_centers = [x.center.id for x in request.user.aasaanusercenter_set.all()]
        # get all zones this user belongs to
        user_zones = [x.zone.id for x in request.user.aasaanuserzone_set.all()]

        # get all materials who have a role in above user's centers
        material_centers = MaterialsCenter.objects.filter(pk__in=user_centers)

        #contacts may belong to centers which belong to zones above user has permission for. get those too
        material_zones = MaterialsCenter.objects.filter(zone__id__in=user_zones)

        #merge all of them
        all_materials = material_centers | material_zones
        #and de-dupe them!
        all_materials = all_materials.distinct()

        return all_materials

    list_display = ('center_name', 'zone', 'item_count')
    fields = ('center_name', 'zone')
    readonly_fields = ('zone', 'center_name')

    inlines = [CenterMaterialInline, CenterItemNotesInline]

    list_per_page = 30

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Register your models here.
admin.site.register(ItemMaster)
admin.site.register(MaterialsCenter, MaterialsAdmin)
# admin.site.register(Transaction)
# admin.site.register(LoanTransaction)
