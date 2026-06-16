from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, UserSession, UserActivity


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    readonly_fields = ['employee_id', 'created_at', 'updated_at']
    max_num = 1
    min_num = 0
    extra = 0
    fieldsets = (
        ('Work Information', {'fields': ('job_title', 'department', 'manager', 'location')}),
        ('Contact Information', {'fields': ('phone', 'mobile')}),
        ('System Preferences', {'fields': ('timezone', 'language', 'notifications_enabled', 'email_notifications')}),
        ('Other', {'fields': ('employee_id', 'avatar', 'created_at', 'updated_at')}),
    )


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'employee_id', 'job_title', 'department', 
        'location', 'phone', 'created_at'
    ]
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name', 
        'employee_id', 'job_title'
    ]
    list_filter = ['department', 'location', 'created_at']
    raw_id_fields = ['user', 'department', 'manager', 'location']
    readonly_fields = ['employee_id', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {'fields': ('user', 'employee_id')}),
        ('Personal Information', {'fields': ('phone', 'mobile')}),
        ('Work Information', {'fields': ('job_title', 'department', 'manager', 'location')}),
        ('System Preferences', {'fields': ('timezone', 'language', 'notifications_enabled', 'email_notifications')}),
        ('Other', {'fields': ('avatar', 'created_at', 'updated_at')}),
    )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'ip_address', 'login_time', 'logout_time', 'is_active'
    ]
    search_fields = ['user__username', 'ip_address']
    list_filter = ['is_active', 'login_time']
    raw_id_fields = ['user']
    readonly_fields = ['session_key', 'login_time', 'logout_time']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'action', 'description_short', 'ip_address', 'timestamp'
    ]
    search_fields = ['user__username', 'description']
    list_filter = ['action', 'timestamp']
    raw_id_fields = ['user']
    readonly_fields = ['timestamp']

    def description_short(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
    description_short.short_description = 'Description'
