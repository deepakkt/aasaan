from django.contrib import admin

from contacts.models import Contact, IndividualRole
from .models import LanguageMaster, ProgramCategory, ProgramMaster, \
    ProgramMasterCategory, ProgramSchedule, ProgramVenueAddress, ProgramScheduleNote, \
    ProgramTeacher, BatchMaster, ProgramBatch, ProgramScheduleCounts, \
    ProgramCountMaster

from django_markdown.admin import MarkdownModelAdmin, MarkdownInlineAdmin


class LanguageMasterAdmin(MarkdownModelAdmin):
    list_display = ('name',)


class BatchMasterAdmin(MarkdownModelAdmin):
    list_display = ('name',)


class ProgramCategoryAdmin(MarkdownModelAdmin):
    list_display = ('name',)


class ProgramCountMasterAdmin(admin.ModelAdmin):
    list_display = ('count_category',)


class ProgramMasterCategoryAdmin(admin.TabularInline):
    model = ProgramMasterCategory
    extra = 1


class ProgramMasterAdmin(MarkdownModelAdmin):
    list_display = ('name', 'active')
    list_filter = ('active',)

    inlines = [ProgramMasterCategoryAdmin]


class ProgramBatchAdmin(admin.TabularInline):
    model = ProgramBatch
    extra = 1


class ProgramTeacherAdmin(admin.TabularInline):
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'teacher':
            teacher_role = IndividualRole.objects.get(role_name='Teacher', role_level='ZO')
            kwargs["queryset"] = Contact.objects.filter(individualcontactrolezone__role=teacher_role)
        return super(ProgramTeacherAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    model = ProgramTeacher
    extra = 1


class ProgramScheduleCountsAdmin(admin.TabularInline):
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'category':
            kwargs["queryset"] = ProgramCountMaster.active_objects.all()
        return super(ProgramScheduleCountsAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    model = ProgramScheduleCounts
    extra = 0


class ProgramVenueAdmin(admin.StackedInline):
    model = ProgramVenueAddress
    extra = 0


class ProgramScheduleNoteAdmin(MarkdownInlineAdmin, admin.TabularInline):
    model = ProgramScheduleNote
    extra = 0


class ProgramScheduleAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'program':
            kwargs["queryset"] = ProgramMaster.active_objects.all()
        return super(ProgramScheduleAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    list_display = ['program_name', 'center', 'program_location', 'start_date',
                    'status']

    list_filter = ['status']

    search_fields = ['center', 'program_location']

    inlines = [ProgramBatchAdmin, ProgramTeacherAdmin,
               ProgramScheduleCountsAdmin, ProgramVenueAdmin,
               ProgramScheduleNoteAdmin]


admin.site.register(LanguageMaster, LanguageMasterAdmin)
admin.site.register(BatchMaster, BatchMasterAdmin)
admin.site.register(ProgramCategory, ProgramCategoryAdmin)
admin.site.register(ProgramMaster, ProgramMasterAdmin)
admin.site.register(ProgramCountMaster, ProgramCountMasterAdmin)
admin.site.register(ProgramSchedule, ProgramScheduleAdmin)