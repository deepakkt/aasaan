from django.contrib import admin
from .models import Configuration, Tag, AdminQuery, MasterDeploy, \
                    DatabaseRefresh

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

class DatabaseRefreshAdmin(admin.ModelAdmin):
    list_display = ('created', 'executed', 'refresh_status')
    readonly_fields = ('created', 'executed', 'refresh_status')

# Register your models here.
admin.site.register(Configuration, ConfigAdmin)
admin.site.register(Tag)
admin.site.register(AdminQuery, QueryAdmin)
admin.site.register(MasterDeploy, MasterDeployAdmin)
admin.site.register(DatabaseRefresh, DatabaseRefreshAdmin)