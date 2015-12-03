from django.contrib import admin
from .models import Contact, ContactNote, ContactZone, \
    ContactAddress, ContactRole, Role, Zone

admin.AdminSite.site_header = "aasaan"
admin.AdminSite.site_title = "aasaan"

# Register your models here.

class ContactNoteInline(admin.TabularInline):
    model = ContactNote
    extra = 1

class ContactZoneInline(admin.TabularInline):
    model = ContactZone
    extra = 1

class ContactAddressInline(admin.StackedInline):
    model = ContactAddress
    extra = 0

class ContactRoleInline(admin.TabularInline):
    model = ContactRole
    extra = 1

class ContactRoleInline2(admin.TabularInline):
    model = ContactRole
    extra = 20

class ContactAdmin(admin.ModelAdmin):
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

    inlines = [ContactAddressInline, ContactZoneInline,
               ContactNoteInline, ContactRoleInline]

class RoleAdmin(admin.ModelAdmin):
    inlines = [ContactRoleInline2]

admin.site.register(Contact, ContactAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Zone)