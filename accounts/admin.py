from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, UserPreferences, Device, PasswordReset, Follower

class UserPreferencesInline(admin.StackedInline):
    model = UserPreferences
    can_delete = False
    verbose_name_plural = 'preferences'

class DeviceInline(admin.TabularInline):
    model = Device
    extra = 0

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    inlines = (UserPreferencesInline, DeviceInline)
    list_display = ('email', 'username', 'first_name', 'last_name', 'role', 'is_premium', 'is_staff')
    list_filter = ('role', 'is_premium', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('username', 'first_name', 'last_name', 'profile_picture', 'bio', 'date_of_birth', 'country')}),
        (_('Permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Subscription'), {'fields': ('is_premium', 'subscription_date', 'plan')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role'),
        }),
    )

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'user', 'last_active', 'is_active')
    list_filter = ('is_active', 'last_active')
    search_fields = ('device_name', 'user__email', 'device_id')
    ordering = ('-last_active',)

@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'token')
    ordering = ('-created_at',)
    readonly_fields = ('token', 'created_at')

@admin.register(Follower)
class FollowerAdmin(admin.ModelAdmin):
    list_display = ('user', 'follows', 'followed_at')
    list_filter = ('followed_at',)
    search_fields = ('user__email', 'follows__email')
    ordering = ('-followed_at',)
