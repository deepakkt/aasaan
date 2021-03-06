from copy import copy

from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist

from contacts.models import Contact, IndividualRole, Zone, Center
from .models import LanguageMaster, ProgramCategory, ProgramMaster, \
    ProgramMasterCategory, ProgramSchedule, ProgramVenueAddress, ProgramScheduleNote, \
    ProgramTeacher, BatchMaster, ProgramBatch, ProgramScheduleCounts, \
    ProgramCountMaster, ProgramAdditionalLanguages, ProgramAdditionalInformation, \
    ProgramTag, ProgramReceiptAmounts

from config.models import Tag
from utils.filters import RelatedDropdownFilter

class LanguageMasterAdmin(admin.ModelAdmin):
    list_display = ('name',)


class BatchMasterAdmin(admin.ModelAdmin):
    list_display = ('name',)


class ProgramCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


class ProgramCountMasterAdmin(admin.ModelAdmin):
    list_display = ('count_category',)


class ProgramMasterCategoryAdmin(admin.TabularInline):
    model = ProgramMasterCategory
    extra = 1


class ProgramMasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'active')
    list_filter = ('active',)

    inlines = [ProgramMasterCategoryAdmin]


class ProgramBatchAdmin(admin.TabularInline):
    model = ProgramBatch
    extra = 0

class ProgramReceiptAmountsAdmin(admin.TabularInline):
    model = ProgramReceiptAmounts
    extra = 0

class ProgramTeacherAdmin(admin.TabularInline):
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'teacher':
            try:
                teacher_role = IndividualRole.objects.get(role_name='Teacher', role_level='ZO')
                _teacher_list = Contact.objects.filter(individualcontactrolezone__role=teacher_role)
                kwargs["queryset"] = _teacher_list.distinct()
            except ObjectDoesNotExist:
                kwargs["queryset"] = Contact.objects.none()

        return super(ProgramTeacherAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    model = ProgramTeacher
    extra = 0


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


class ProgramScheduleNoteAdmin(admin.TabularInline):
    model = ProgramScheduleNote
    fields = ('note',)
    extra = 0


class ProgramLanguageAdmin(admin.TabularInline):
    model = ProgramAdditionalLanguages
    extra = 0


class ProgramAdditionalInformationAdmin(admin.TabularInline):
    model = ProgramAdditionalInformation
    extra = 0


class ProgramTagAdmin(admin.TabularInline):
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'tag':
            kwargs["queryset"] = Tag.objects.filter(tag_name__startswith='schedule-')

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    model = ProgramTag
    extra = 0


class ProgramScheduleZoneFilter(admin.SimpleListFilter):
    title = 'zones'
    parameter_name = 'zones'

    def lookups(self, request, model_admin):
        return tuple([(x.zone_name, x.zone_name) for x in Zone.objects.all()])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(center__zone__zone_name=self.value())


class ProgramScheduleProgramFilter(admin.SimpleListFilter):
    title = 'program'
    parameter_name = 'program'

    def lookups(self, request, model_admin):
        base_queryset = ProgramMaster.objects.all()
        base_queryset = base_queryset if request.user.is_superuser else base_queryset.filter(admin=False)
        return tuple([(x.name, x.name) for x in base_queryset])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(program__name=self.value())


class ProgramScheduleHiddenFilter(admin.SimpleListFilter):
    title = 'program visibility'
    parameter_name = 'hidden'

    def lookups(self, request, model_admin):
        if request.user.is_superuser:
            return (('hidden', 'Hidden Programs'),)
        else:
            return (('', ''),)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(hidden=True)


class ProgramScheduleTagFilter(admin.SimpleListFilter):
    title = 'tag'
    parameter_name = 'tag'

    def lookups(self, request, model_admin):
        return ((x, x) for x in Tag.objects.filter(tag_name__startswith='schedule-'))

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(programtag__tag__tag_name=self.value())


class ProgramScheduleAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        self._base_obj = None
        super(ProgramScheduleAdmin, self).__init__(*args, **kwargs)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'program':
            kwargs["queryset"] = ProgramMaster.active_objects.all()
        if not request.user.is_superuser and db_field.name == 'center':
            user_zones = [x.zone for x in request.user.aasaanuserzone_set.all()]
            user_zone_centers = [x.id for x in Center.objects.filter(zone__in=user_zones)]
            user_centers = [x.center.id for x in request.user.aasaanusercenter_set.all()] +\
                user_zone_centers
            user_centers = list(set(user_centers))
            kwargs["queryset"] = Center.objects.filter(pk__in=user_centers)
        return super(ProgramScheduleAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        self._base_obj = obj
        super(ProgramScheduleAdmin, self).save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        teachers_before = [x.teacher for x in self._base_obj.programteacher_set.all()]
        super(ProgramScheduleAdmin, self).save_related(request, form, formsets, change)
        teachers_after = [x.teacher for x in self._base_obj.programteacher_set.all()]

    # filter schedule records based on user permissions
    def get_queryset(self, request):
        qs = super(ProgramScheduleAdmin, self).get_queryset(request)

        # give entire set if user is a superuser irrespective of zone and center assignments
        if (request.user.is_superuser) or ('view-all' in [x.name for x in request.user.groups.all()]):
            return qs if request.user.is_superuser else qs.filter(program__admin=False)

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

        return all_schedules.filter(program__admin=False)

    date_hierarchy = 'start_date'
    list_display = ['is_cancelled', 'program_name', 'center',
                    'start_date', 'end_date',
                    'gender', 'primary_language', 'event_management_code', 
                    'online_registration_code']

    list_display_links = ['is_cancelled', 'program_name']

    exclude = ('cancelled_date', 'receipts')

    list_filter = [('primary_language',RelatedDropdownFilter), ProgramScheduleProgramFilter, ProgramScheduleZoneFilter,
                   ProgramScheduleTagFilter,
                   ProgramScheduleHiddenFilter, 'status']

    search_fields = ['program__name', 'center__center_name', 'event_name', 'event_management_code', 'online_registration_code']

    save_on_top = True

    list_per_page = 30

    inlines = [ProgramTagAdmin, ProgramLanguageAdmin, ProgramBatchAdmin, ProgramTeacherAdmin,
               ProgramScheduleCountsAdmin, ProgramReceiptAmountsAdmin, ProgramVenueAdmin,
               ProgramScheduleNoteAdmin, ProgramAdditionalInformationAdmin]

    actions = ['mark_hidden', 'mark_unhidden', 'make_schedule_copy']

    class Media:
        js = ('/static/aasaan/schedulemaster/js/new_schedule_default_rows.js',
              '/static/aasaan/js/disable_notes_v2.js',
              '/static/aasaan/schedulemaster/js/validate_event.js')

    def mark_hidden(self, request, queryset):
        if not request.user.is_superuser:
            self.message_user(request, 'You do not have permission to mark programs hidden')
            return

        rows_updated = queryset.update(hidden=True)

        self.message_user(request, 'Done! Number of programs marked hidden: %s' %(rows_updated))
        return
    mark_hidden.short_description = "Mark programs hidden"

    def mark_unhidden(self, request, queryset):
        if not request.user.is_superuser:
            self.message_user(request, 'You do not have permission to unhide programs')
            return

        rows_updated = queryset.update(hidden=False)

        self.message_user(request, 'Done! Number of programs unhidden: %s' %(rows_updated))
        return
    mark_unhidden.short_description = "Mark programs unhidden"

    def make_schedule_copy(self, request, queryset):
        if queryset.count() > 1:
            self.message_user(request, 'Select just one program to duplicate')
            return

        schedule = queryset[0]

        new_schedule = copy(schedule)
        new_schedule.id = None
        new_schedule.save()
        self.message_user(request, 'Done! New schedule created with id: %d' % new_schedule.id)

    make_schedule_copy.short_description = "Make a copy of schedule"


admin.site.register(LanguageMaster, LanguageMasterAdmin)
admin.site.register(BatchMaster, BatchMasterAdmin)
admin.site.register(ProgramCategory, ProgramCategoryAdmin)
admin.site.register(ProgramMaster, ProgramMasterAdmin)
admin.site.register(ProgramCountMaster, ProgramCountMasterAdmin)
admin.site.register(ProgramSchedule, ProgramScheduleAdmin)