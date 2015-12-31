from django.contrib import admin
from .models import Contact, ContactNote, \
    ContactAddress, ContactRoleGroup, RoleGroup, Zone, \
    Center, IndividualRole, IndividualContactRoleCenter, \
    IndividualContactRoleZone

from django_markdown.admin import MarkdownModelAdmin, MarkdownInlineAdmin

admin.AdminSite.site_header = "aasaan"
admin.AdminSite.site_title = "aasaan"

# Register your models here.


class ContactNoteInline(MarkdownInlineAdmin, admin.TabularInline):
    model = ContactNote
    extra = 1


class ContactAddressInline(admin.StackedInline):
    model = ContactAddress
    extra = 0


class ContactRoleGroupInline(admin.TabularInline):
    model = ContactRoleGroup
    extra = 1


class ContactRoleGroupInline2(admin.TabularInline):
    model = ContactRoleGroup
    extra = 20


class CenterInline(admin.TabularInline):
    model = Center
    extra = 5


class IndividualContactRoleCenterInline(admin.TabularInline):
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'role':
            kwargs["queryset"] = IndividualRole.objects.filter(role_level='CE')
        return super(IndividualContactRoleCenterInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    model = IndividualContactRoleCenter
    extra = 1


class IndividualContactRoleZoneInline(admin.TabularInline):
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'role':
            kwargs["queryset"] = IndividualRole.objects.filter(role_level='ZO')
        return super(IndividualContactRoleZoneInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    model = IndividualContactRoleZone
    extra = 1


class ContactAdmin(MarkdownModelAdmin):
    list_display = ('full_name', 'primary_mobile', 'whatsapp_number',
                    'primary_email', 'teacher_tno', 'status', 'profile_image')

    list_filter = ('status', 'gender')

    search_fields = ('teacher_tno', 'first_name', 'last_name',
                     'cug_mobile', 'other_mobile_1')

    fieldsets = [
        ('Core Information', {'fields': ['first_name', 'last_name',
                                         'teacher_tno', 'date_of_birth',
                                         'gender', 'status',
                                         'cug_mobile', 'other_mobile_1',
                                         'whatsapp_number',
                                         'primary_email', 'profile_picture'
                                         ]}),
        ('Secondary Information', {'fields': ['other_mobile_2', 'secondary_email',
                                              'id_card_type', 'id_card_number',
                                              'id_proof_type', 'id_proof_other',
                                              'id_proof_number',
                                              'pushbullet_token'
                                         ], 'classes' : ['collapse']}),
        ('Remarks', {'fields': ['remarks']}),
    ]

    readonly_fields = ('profile_image', )

    inlines = [ContactAddressInline,
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
admin.site.register(IndividualRole)