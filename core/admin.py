"""
Django admin configuration for core models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UnifiedUser, SystemConfiguration, PlatformMetrics


@admin.register(UnifiedUser)
class UnifiedUserAdmin(UserAdmin):
    """Admin interface for unified user model."""
    
    list_display = ('username', 'email', 'platform_role', 'subscription_tier', 'is_active', 'monthly_api_calls')
    list_filter = ('platform_role', 'subscription_tier', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Platform Settings', {
            'fields': ('platform_role', 'subscription_tier', 'api_key', 'monthly_api_calls', 'api_call_limit')
        }),
        ('Preferences', {
            'fields': ('preferences',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    """Admin interface for system configuration."""
    
    list_display = ('key', 'category', 'description', 'is_active', 'updated_at')
    list_filter = ('category', 'is_active', 'is_sensitive')
    search_fields = ('key', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at', 'version')
    
    fieldsets = (
        (None, {
            'fields': ('key', 'value', 'description')
        }),
        ('Classification', {
            'fields': ('category', 'is_sensitive')
        }),
        ('Status', {
            'fields': ('is_active', 'metadata')
        }),
        ('System Info', {
            'fields': ('id', 'created_at', 'updated_at', 'version'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PlatformMetrics)
class PlatformMetricsAdmin(admin.ModelAdmin):
    """Admin interface for platform metrics."""
    
    list_display = ('metric_name', 'metric_value', 'metric_type', 'subsystem', 'timestamp')
    list_filter = ('metric_type', 'subsystem', 'timestamp')
    search_fields = ('metric_name',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'timestamp')
    
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        (None, {
            'fields': ('metric_name', 'metric_value', 'metric_type')
        }),
        ('Context', {
            'fields': ('subsystem', 'labels')
        }),
        ('System Info', {
            'fields': ('id', 'timestamp', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )