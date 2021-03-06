from django.contrib import admin

from .models import Contact, ContactNote, \
    ContactAddress, ContactRoleGroup, RoleGroup, Zone, \
    Center, IndividualRole, IndividualContactRoleCenter, \
    IndividualContactRoleZone, ContactTag
from config.models import Tag


admin.AdminSite.site_header = "aasaan"
admin.AdminSite.site_title = "aasaan"


# Register your models here.


class ContactNoteInline(admin.TabularInline):
    model = ContactNote
    extra = 0


class ContactAddressInline(admin.StackedInline):
    model = ContactAddress
    extra = 0
    max_num = 1



class ContactRoleGroupInline(admin.TabularInline):
    model = ContactRoleGroup
    extra = 1


class ContactRoleGroupInline2(admin.TabularInline):
    model = ContactRoleGroup
    extra = 20


class ContactTagInline(admin.TabularInline):
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'tag':
            kwargs["queryset"] = Tag.objects.filter(tag_name__startswith='contact-')

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    model = ContactTag
    extra = 0


class CenterInline(admin.TabularInline):
    def __init__(self, *args, **kwargs):
        self.zone = None
        super(CenterInline, self).__init__(*args, **kwargs)

    # store zone being edited for filtering purpose in next section
    def get_fields(self, request, obj=None):
        self.zone = obj
        return super(CenterInline, self).get_fields(request, obj)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        # display only current zone centers under parent center
        if db_field.name == 'parent_center':
            kwargs["queryset"] = Center.objects.filter(zone=self.zone)

        return super(CenterInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    model = Center
    extra = 5


class IndividualContactRoleCenterInline(admin.TabularInline):
    def __init__(self, *args, **kwargs):
        super(IndividualContactRoleCenterInline, self).__init__(*args, **kwargs)
        self.parent_contact = None

    def get_fields(self, request, obj=None):
        self.parent_contact = obj
        return super(IndividualContactRoleCenterInline, self).get_fields(request, obj)


    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'role':
            if request.user.is_superuser:
                kwargs["queryset"] = IndividualRole.objects.filter(role_level='CE')
            else:
                kwargs["queryset"] = IndividualRole.objects.filter(role_level='CE', admin_role=False)

        if db_field.name == 'center':
            if (request.user.is_superuser) or ('view-all' in [x.name for x in request.user.groups.all()]):
                pass
            else:
                user_zones = [x.zone.id for x in request.user.aasaanuserzone_set.all()]
                user_zone_centers = [x.id for x in Center.objects.filter(zone__pk__in=user_zones)]
                user_centers = [x.center.id for x in request.user.aasaanusercenter_set.all()] + \
                    user_zone_centers
                if self.parent_contact:
                    user_centers += [x.center.id for x in self.parent_contact.individualcontactrolecenter_set.all()]
                user_centers = list(set(user_centers))
                kwargs["queryset"] = Center.objects.filter(pk__in=user_centers)

        return super(IndividualContactRoleCenterInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    model = IndividualContactRoleCenter
    extra = 1


class IndividualContactRoleZoneInline(admin.TabularInline):
    def __init__(self, *args, **kwargs):
        super(IndividualContactRoleZoneInline, self).__init__(*args, **kwargs)
        self.parent_contact = None

    def get_fields(self, request, obj=None):
        self.parent_contact = obj
        return super(IndividualContactRoleZoneInline, self).get_fields(request, obj)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'role':
            if request.user.is_superuser:
                kwargs["queryset"] = IndividualRole.objects.filter(role_level='ZO')
            else:
                kwargs["queryset"] = IndividualRole.objects.filter(role_level='ZO', admin_role=False)

        if db_field.name == 'zone':
            if (request.user.is_superuser) or ('view-all' in [x.name for x in request.user.groups.all()]):
                pass
            else:
                user_zones = [x.zone.id for x in request.user.aasaanuserzone_set.all()]
                if self.parent_contact:
                    user_zones += [x.zone.id for x in self.parent_contact.individualcontactrolezone_set.all()]
                user_zones = list(set(user_zones))
                kwargs["queryset"] = Zone.objects.filter(pk__in=user_zones)

        return super(IndividualContactRoleZoneInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    model = IndividualContactRoleZone
    fields = ['zone', 'role']
    extra = 1


# Implement filter logic based on roles assigned for centers or zones
# Zone => Role assigned directly to zone
# Center => Role assigned to center which belongs to zone
class ContactZoneFilter(admin.SimpleListFilter):
    title = 'zones'
    parameter_name = 'zones'

    def lookups(self, request, model_admin):
        return tuple([(x.zone_name, x.zone_name) for x in Zone.objects.all()])

    def queryset(self, request, queryset):
        if self.value():
            contact_zones = queryset.filter(individualcontactrolezone__zone__zone_name=self.value())
            contact_center_zones = queryset.filter(individualcontactrolecenter__center__zone__zone_name=self.value())
            all_zones = contact_zones | contact_center_zones
            return all_zones.distinct()


# Similar to zone filter above, for roles
class ContactRoleFilter(admin.SimpleListFilter):
    title = 'roles'
    parameter_name = 'roles'

    def lookups(self, request, model_admin):
        role_list = IndividualRole.objects.all().order_by('role_level', 'role_name')
        if request.user.is_superuser:
            lookup_list = [(x.role_name, str(x)) for x in role_list]
        else:
            lookup_list = [(x.role_name, str(x)) for x in role_list if not x.admin_role]

        return tuple(lookup_list)

    def queryset(self, request, queryset):
        if self.value():
            contact_role_zones = queryset.filter(individualcontactrolezone__role__role_name=self.value())
            contact_role_centers = queryset.filter(individualcontactrolecenter__role__role_name=self.value())
            all_roles = contact_role_centers | contact_role_zones
            return all_roles.distinct()


class ContactTagFilter(admin.SimpleListFilter):
    title = 'tag'
    parameter_name = 'tag'

    def lookups(self, request, model_admin):
        return ((x, x) for x in Tag.objects.filter(tag_name__startswith='contact-'))

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(contacttag__tag__tag_name=self.value())


class ContactAdmin(admin.ModelAdmin):

    def get_actions(self, request):
        actions = super(ContactAdmin, self).get_actions(request)
        if 'Teacher' in [x.name for x in request.user.groups.all()] and  'delete_selected' in actions:
            del actions['delete_selected']
            return actions
        return actions

    # filter contact records based on user permissions
    def get_queryset(self, request):
        qs = super(ContactAdmin, self).get_queryset(request)

        self.list_filter = (ContactRoleFilter, ContactZoneFilter, ContactTagFilter)

        self.search_fields = ('teacher_tno', 'first_name', 'last_name',
                         'cug_mobile', 'other_mobile_1', 'primary_email',
                         'individualcontactrolecenter__center__center_name')
        # give entire set if user is a superuser irrespective of zone and center assignments
        if request.user.is_superuser:
            return qs

        if 'Teacher' in [x.name for x in request.user.groups.all()]:
            self.list_filter = []
            self.search_fields = []
            return Contact.objects.filter(primary_email=request.user.email)

        # get all centers this user belongs to
        user_centers = [x.center for x in request.user.aasaanusercenter_set.all()]
        user_zones = [x.zone for x in request.user.aasaanuserzone_set.all()]

        # get all contacts who have a role in above user's centers
        center_contacts = Contact.objects.filter(individualcontactrolecenter__center__in=user_centers)

        # contacts may belong to centers which belong to zones above user has permission for. get those too
        center_zonal_contacts = Contact.objects.filter(individualcontactrolecenter__center__zone__in=user_zones)

        # finally directly get contacts belonging to zone the user has access to
        zone_contacts = Contact.objects.filter(individualcontactrolezone__zone__in=user_zones)

        # merge all of them
        all_contacts = center_contacts | zone_contacts | center_zonal_contacts
        # and de-dupe them!
        all_contacts = all_contacts.distinct()

        return all_contacts

    list_display = ('full_name', 'primary_mobile', 'whatsapp_number',
                    'primary_email', 'teacher_tno', 'status', 'profile_image')

    list_filter = (ContactRoleFilter, ContactZoneFilter, ContactTagFilter)

    search_fields = ('teacher_tno', 'first_name', 'last_name',
                     'cug_mobile', 'other_mobile_1', 'primary_email', 'individualcontactrolecenter__center__center_name')

    list_per_page = 30

    fieldsets = [
        ('Core Information', {'fields': ['profile_image_display', 'first_name', 'last_name',
                                         'teacher_tno', 'date_of_birth',
                                         'gender', 'category', 'status', 'marital_status',
                                         'cug_mobile', 'other_mobile_1',
                                         'whatsapp_number',
                                         'primary_email', 'profile_picture'
                                         ]}),
        ('Secondary Information', {'fields': ['other_mobile_2', 'secondary_email',
                                              'id_proof_type',
                                              'id_proof_number',
                                              'id_proof_scan',
                                              'name_as_in_id',
                                              'remarks',
                                              ], 'classes': ['collapse']}),
    ]

    readonly_fields = ('profile_image', 'profile_image_display',)

    inlines = [ContactTagInline, ContactAddressInline,
               IndividualContactRoleZoneInline,
               IndividualContactRoleCenterInline,
               ContactNoteInline, ContactRoleGroupInline]


class RoleGroupAdmin(admin.ModelAdmin):
    inlines = [ContactRoleGroupInline2]


class ZoneAdmin(admin.ModelAdmin):
    inlines = [CenterInline]



admin.site.register(Contact, ContactAdmin)
admin.site.register(RoleGroup, RoleGroupAdmin)
admin.site.register(Zone, ZoneAdmin)
admin.site.register(IndividualRole, admin.ModelAdmin)
