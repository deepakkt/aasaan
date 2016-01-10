from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AasaanUserCenter, AasaanUserZone

# Register your models here.

class AasaanUserZoneInline(admin.StackedInline):
    model = AasaanUserZone
    extra = 1
    verbose_name = "user zone"
    verbose_name_plural = "user zones"

class AasaanUserCenterInline(admin.StackedInline):
    model = AasaanUserCenter
    extra = 1
    verbose_name = "user center"
    verbose_name_plural = "user centers"


class UserAdmin(BaseUserAdmin):
    inlines = (AasaanUserZoneInline,
               AasaanUserCenterInline)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)