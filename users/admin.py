from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser  # Import your custom user model

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')

    # Add the 'role' field to the fieldsets so it's editable in the admin
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
