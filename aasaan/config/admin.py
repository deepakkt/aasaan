import json

from django.contrib import admin
from django.contrib.admin.utils import unquote
from .models import Configuration, Tag, AdminQuery, MasterDeploy, \
                    DatabaseRefresh

class AuditAdmin(admin.ModelAdmin):
    object_history_template = "config/admin/object_history.html"

    def history_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, unquote(object_id))
        extra_context = extra_context or dict()
        extra_context["audit_meta"] = json.loads(obj.audit_meta)

        return super().history_view(request, object_id, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        obj.save(_meta_user=request.user.username)
        


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