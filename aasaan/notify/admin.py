from django.contrib import admin

# Register your models here.
from .models import NotifyContext, Notifier, \
                    NotifyAttachment

class ContextAdmin(admin.ModelAdmin):
    list_display = ('context_title', 'active')                    


class NotifyAttachmentAdmin(admin.TabularInline):
    model = NotifyAttachment
    extra = 0

class NotifierAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'notify_context':
            kwargs["queryset"] = NotifyContext.objects.filter(active=True)

        return super(NotifierAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)            
    
    list_display = ('notify_title', 'notify_status',
                    'created')

    search_fields = ('notify_title',)                    

    list_per_page = 10

    list_filter = ('notify_status',)

    readonly_fields = ('created', 'modified')

    inlines = (NotifyAttachmentAdmin,)


admin.site.register(NotifyContext, ContextAdmin)
admin.site.register(Notifier, NotifierAdmin)
    