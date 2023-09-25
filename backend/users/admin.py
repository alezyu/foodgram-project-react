from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from .models import CustomUser


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
    )
    repeat_password = forms.CharField(
        label='Введите повторно',
        widget=forms.PasswordInput,
    )

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
        )

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        repeat_password = self.cleaned_data.get('repeat_password')
        if password and repeat_password and password != repeat_password:
            raise ValidationError('Пароли не совпадают')
        return repeat_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class ChangePasswordForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'password',
            'username',
            'first_name',
            'last_name',
            'is_active',
            'is_admin',
            'is_staff',
        )

    def clean_password(self):
        return self.initial['password']


class UserAdmin(BaseUserAdmin):
    form = ChangePasswordForm
    add_form = RegisterForm
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
        'is_admin',
    )
    list_filter = ('is_admin', 'email', 'username')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'username',
                    'first_name',
                    'last_name',
                    'password',
                    'repeat_password',
                ),
            },
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(CustomUser, UserAdmin)

admin.site.unregister(Group)
