from django.contrib import admin

from .models import LocalEvents

# Register your models here.

class LocalEventsAdmin(admin.ModelAdmin):
    list_display = ('zone', 'center', 'admin_approved', 'event_start_date', 'event_name')

    list_filter = ('admin_approved', 'zone', 'event_start_date')

    search_fields = ('center__center_name',)

    list_per_page = 30


admin.site.register(LocalEvents, LocalEventsAdmin)