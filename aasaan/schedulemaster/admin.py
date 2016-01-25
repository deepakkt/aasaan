from django.contrib import admin
from .models import ProgramMaster, ProgramSchedule, VenueAddress, ScheduleNote, ClassTeachers, \
    LanguageMaster
from django_markdown.admin import MarkdownModelAdmin, MarkdownInlineAdmin


class VenueAddressInline(admin.StackedInline):
    model = VenueAddress
    extra = 0
    max_num = 1


class ScheduleNoteInline(MarkdownInlineAdmin, admin.TabularInline):
    model = ScheduleNote
    extra = 0
    max_num = 1


class TeachersInline(MarkdownInlineAdmin, admin.TabularInline):
    model = ClassTeachers
    extra = 0
    max_num = 1


class ProgramScheduleAdmin(MarkdownModelAdmin):
    list_display = ('program', 'zone_name', 'center', 'status', 'session_details', 'contact_phone1')

    list_filter = ('program', 'status')

    search_fields = ('program', 'center', 'status')

    inlines = [VenueAddressInline, ScheduleNoteInline, TeachersInline]


# Register your models here.
admin.site.register(LanguageMaster)
admin.site.register(ProgramMaster)
admin.site.register(ProgramSchedule, ProgramScheduleAdmin)
