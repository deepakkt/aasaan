from django.contrib import admin
from .models import AshramVisit


class AshramVisitAdmin(admin.ModelAdmin):
    date_hierarchy = 'arrival_date'
    list_display = ('__str__', 'arrival_date', 'departure_time', 'contact_person', 'mobile_no', 'lunch', 'dinner')

admin.site.register(AshramVisit, AshramVisitAdmin)
