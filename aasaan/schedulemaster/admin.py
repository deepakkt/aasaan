from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist

from contacts.models import Contact, IndividualRole, Zone
from .models import LanguageMaster, ProgramCategory, ProgramMaster, \
    ProgramMasterCategory, ProgramSchedule, ProgramVenueAddress, ProgramScheduleNote, \
    ProgramTeacher, BatchMaster, ProgramBatch, ProgramScheduleCounts, \
    ProgramCountMaster, ProgramAdditionalLanguages, ProgramAdditionalInformation

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
    extra = 0


class ProgramTeacherAdmin(admin.TabularInline):
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'teacher':
            try:
                teacher_role = IndividualRole.objects.get(role_name='Teacher', role_level='ZO')
                kwargs["queryset"] = Contact.objects.filter(individualcontactrolezone__role=teacher_role)
            except ObjectDoesNotExist:
                kwargs["queryset"] = Contact.objects.none()

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


class ProgramLanguageAdmin(admin.TabularInline):
    model = ProgramAdditionalLanguages
    extra = 0


class ProgramAdditionalInformationAdmin(admin.TabularInline):
    model = ProgramAdditionalInformation
    extra = 0


class ProgramScheduleZoneFilter(admin.SimpleListFilter):
    title = 'zones'
    parameter_name = 'zones'

    def lookups(self, request, model_admin):
        return tuple([(x.zone_name, x.zone_name) for x in Zone.objects.all()])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(center__zone__zone_name=self.value())


class ProgramScheduleAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'program':
            kwargs["queryset"] = ProgramMaster.active_objects.all()
        return super(ProgramScheduleAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    # filter schedule records based on user permissions
    def get_queryset(self, request):
        qs = super(ProgramScheduleAdmin, self).get_queryset(request)

        # give entire set if user is a superuser irrespective of zone and center assignments
        if (request.user.is_superuser) or ('view-all' in [x.name for x in request.user.groups.all()]):
            return qs

        # get all centers this user belongs to
        user_centers = [x.center for x in request.user.aasaanusercenter_set.all()]
        user_zones = [x.zone for x in request.user.aasaanuserzone_set.all()]

        # get all schedules for user's centers
        center_schedules = ProgramSchedule.objects.filter(center__in=user_centers)

        # user may belong to a zone that contains this center's schedules. pull those too
        center_zonal_schedules = ProgramSchedule.objects.filter(center__zone__in=user_zones)

        # merge all of them
        all_schedules = center_schedules | center_zonal_schedules
        # and de-dupe them!
        all_schedules = all_schedules.distinct()

        return all_schedules


    list_display = ['program_name', 'center', 'start_date', 'end_date',
                    'gender']


    list_filter = [ProgramScheduleZoneFilter, 'program']

    search_fields = ['center__center_name', 'program_location']

    save_on_top = True

    inlines = [ProgramLanguageAdmin, ProgramBatchAdmin, ProgramTeacherAdmin,
               ProgramScheduleCountsAdmin, ProgramVenueAdmin,
               ProgramScheduleNoteAdmin, ProgramAdditionalInformationAdmin]

    class Media:
        js = ('/static/schedulemaster/js/new_schedule_default_batches.js',)


admin.site.register(LanguageMaster, LanguageMasterAdmin)
admin.site.register(BatchMaster, BatchMasterAdmin)
admin.site.register(ProgramCategory, ProgramCategoryAdmin)
admin.site.register(ProgramMaster, ProgramMasterAdmin)
admin.site.register(ProgramCountMaster, ProgramCountMasterAdmin)
admin.site.register(ProgramSchedule, ProgramScheduleAdmin)