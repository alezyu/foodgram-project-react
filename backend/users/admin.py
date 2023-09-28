from django.contrib import admin
from django.contrib.auth.models import Group

from .models import CustomUser, Subscribe


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
    )
    list_filter = (
        'is_staff',
        'email',
        'username',
    )
    search_fields = ('email', )
    ordering = ('email', )
    filter_horizontal = ()


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    model = Subscribe
    list_display = (
        'id',
        'user',
        'author',
    )
    list_filter = ('user', 'author', )
    search_fields = ('user', 'author', )


admin.site.unregister(Group)
