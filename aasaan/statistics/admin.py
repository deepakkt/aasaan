from django.contrib import admin
from .models import StatisticsProgramCounts, OverseasEnrollement, UyirNokkamEnrollement, TrainingStatistics
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.admin import ImportExportMixin
from import_export.formats import base_formats
from .forms import OverseasEnrollementForm

class OverseasEnrollmentResource(resources.ModelResource):
    formats = base_formats.XLS
    class Meta:
        model = OverseasEnrollement
        ordering = 'country'
        widgets = {
                'start_date': {'format': '%Y-%m-%d'},
                'end_date': {'format': '%Y-%m-%d'},
                }

class UyirNokkamEnrollmentResource(resources.ModelResource):
    form = OverseasEnrollementForm
    formats = base_formats.XLS
    class Meta:
        model = UyirNokkamEnrollement
        ordering = 'zone'
        widgets = {
                'date': {'format': '%d.%m.%Y'},
                }



class OverseasEnrollmentAdmin(ImportExportMixin, admin.ModelAdmin):
    form = OverseasEnrollementForm
    formats = [base_formats.XLS,]
    to_encoding = 'utf-8'
    resource_class = OverseasEnrollmentResource


class UyirNokkamEnrollmentAdmin(ImportExportMixin, admin.ModelAdmin):
    formats = [base_formats.XLS,]
    to_encoding = 'utf-8'
    resource_class = UyirNokkamEnrollmentResource

admin.site.register(StatisticsProgramCounts, admin.ModelAdmin)
admin.site.register(OverseasEnrollement, OverseasEnrollmentAdmin)
admin.site.register(UyirNokkamEnrollement, UyirNokkamEnrollmentAdmin)
admin.site.register(TrainingStatistics, admin.ModelAdmin)