from django.contrib import admin
from .models import Configuration, Tag, AdminQuery, MasterDeploy

class ConfigAdmin(admin.ModelAdmin):
    list_display = search_fields = ('configuration_key',)

class QueryAdmin(admin.ModelAdmin):
    list_display = ('query_title', 'query_status', 'created', 'executed')
    exclude = ('created',)
    readonly_fields = ('executed',)

class MasterDeployAdmin(admin.ModelAdmin):
    list_display = ('commit_title', 'deploy_status', 'created', 'executed')
    exclude = ('created',)
    readonly_fields = ('executed',)

# Register your models here.
admin.site.register(Configuration, ConfigAdmin)
admin.site.register(Tag)
admin.site.register(AdminQuery, QueryAdmin)
admin.site.register(MasterDeploy, MasterDeployAdmin)