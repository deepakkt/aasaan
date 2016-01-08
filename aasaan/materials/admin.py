from django.contrib import admin
from .models import LoanTransaction, ItemMaster, Transaction, CenterMaterial, \
    CenterItemNotes, CenterMaterial, MaterialsCenter


class CenterItemNotesInline(admin.TabularInline):
    model = CenterItemNotes
    extra = 1


class CenterMaterialInline(admin.TabularInline):
    model = CenterMaterial
    extra = 1

    def has_delete_permission(self, request, obj=None):
        return False


class MaterialsAdmin(admin.ModelAdmin):
    list_display = ('center_name', 'zone', 'item_count')

    readonly_fields = ('zone', 'center_name')

    inlines = [CenterMaterialInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Register your models here.
admin.site.register(ItemMaster)
admin.site.register(MaterialsCenter, MaterialsAdmin)
# admin.site.register(Transaction)
# admin.site.register(LoanTransaction)
