from django.contrib import admin
from .models import ProgramMaster, ProgramSchedule, VenueAddress, ScheduleNote, ClassTeachers, \
    LanguageMaster, ProgramCategory, ProgramBatch, BatchMaster, ProgramDetails
from django_markdown.admin import MarkdownModelAdmin, MarkdownInlineAdmin


class VenueAddressInline(admin.StackedInline):
    model = VenueAddress
    extra = 0
    max_num = 1


class ScheduleNoteInline(MarkdownInlineAdmin, admin.TabularInline):
    model = ScheduleNote
    extra = 0
    max_num = 1


class TeachersInline(admin.TabularInline):
    model = ClassTeachers
    extra = 0
    max_num = 10


class BatchMasterInline(admin.TabularInline):
    model = ProgramBatch
    extra = 0
    max_num = 10


class ProgramDetailsInline(admin.StackedInline):
    model = ProgramDetails
    extra = 0
    max_num = 1


class ProgramScheduleAdmin(MarkdownModelAdmin):
    list_display = ('program', 'zone_name', 'center', 'status', 'contact_phone1')

    list_filter = ('program', 'status')

    search_fields = ('program', 'center', 'status')

    inlines = [VenueAddressInline, ScheduleNoteInline, TeachersInline, BatchMasterInline, ProgramDetailsInline]


# Register your models here.
admin.site.register(LanguageMaster)
admin.site.register(ProgramCategory)
admin.site.register(ProgramMaster)
admin.site.register(BatchMaster)
admin.site.register(ProgramSchedule, ProgramScheduleAdmin)
