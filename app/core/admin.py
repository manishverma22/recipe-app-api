"""
Django admin customizations.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from core import models

@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    """Define the admin pages for the user."""
    ordering = ['id']
    list_display = ['email', 'name', 'is_active', 'is_staff']
    list_filter = ['is_active', 'is_staff']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff')}),
        (_('Important Dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'name', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser')}),
    )
    readonly_fields = ['last_login']

admin.site.register(models.Recipe)
