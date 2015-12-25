from django.contrib import admin
from .models import Schedule, SyncLog

# Register your models here.

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('program_title', 'program_code', 'start_date',
                    'center', 'match_confidence')

    search_fields = ('program_title', 'program_code',
                     'center__center_name')

    list_filter = ('matched', 'match_overridden',
                   'match_approved')

    fields = ('program_title', 'program_code', 'program_code_source',
              'start_date', 'program_type', 'center', 'match_approved',
              'remarks')

admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(SyncLog)