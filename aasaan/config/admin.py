from django.contrib import admin
from .models import Configuration, Tag

class ConfigAdmin(admin.ModelAdmin):
    list_display = search_fields = ('configuration_key',)


# Register your models here.
admin.site.register(Configuration, ConfigAdmin)
admin.site.register(Tag)