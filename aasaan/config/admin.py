from django.contrib import admin
from .models import Configuration, Tag

# Register your models here.
admin.site.register(Configuration)
admin.site.register(Tag)