from django.contrib import admin

from .models import (Tags)


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug', 'color')
    list_editable = ('name', 'slug', 'color')