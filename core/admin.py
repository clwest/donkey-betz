"""
Django admin configuration for core models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UnifiedUser, SystemConfiguration, PlatformMetrics, GeneratedProject, GeneratedCode


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


@admin.register(GeneratedProject)
class GeneratedProjectAdmin(admin.ModelAdmin):
    """Admin interface for generated projects."""

    list_display = ('name', 'project_type', 'status', 'user', 'created_at', 'agents_count', 'advisors_count')
    list_filter = ('project_type', 'status', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'agents_used', 'advisors_consulted')
    readonly_fields = ('id', 'created_at', 'updated_at', 'version')

    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('name', 'project_type', 'description', 'status')
        }),
        ('AI Contributors', {
            'fields': ('agents_used', 'advisors_consulted')
        }),
        ('User & Status', {
            'fields': ('user', 'is_active')
        }),
        ('System Info', {
            'fields': ('id', 'created_at', 'updated_at', 'version', 'metadata'),
            'classes': ('collapse',)
        }),
    )

    def agents_count(self, obj):
        """Display count of agents used."""
        return len(obj.agents_used) if obj.agents_used else 0
    agents_count.short_description = 'Agents'

    def advisors_count(self, obj):
        """Display count of advisors consulted."""
        return len(obj.advisors_consulted) if obj.advisors_consulted else 0
    advisors_count.short_description = 'Advisors'


@admin.register(GeneratedCode)
class GeneratedCodeAdmin(admin.ModelAdmin):
    """Admin interface for generated code."""

    list_display = ('filename', 'project', 'language', 'agent_creator', 'execution_status', 'is_latest', 'created_at')
    list_filter = ('language', 'execution_status', 'is_latest', 'is_active', 'created_at', 'agent_creator')
    search_fields = ('filename', 'file_path', 'agent_creator', 'task_description', 'project__name')
    readonly_fields = ('id', 'created_at', 'updated_at', 'version')

    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('project', 'filename', 'file_path', 'language')
        }),
        ('Code Content', {
            'fields': ('content',),
            'classes': ('collapse',)
        }),
        ('AI Attribution', {
            'fields': ('agent_creator', 'task_description')
        }),
        ('Execution', {
            'fields': ('execution_status', 'execution_output'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_latest', 'is_active', 'user')
        }),
        ('System Info', {
            'fields': ('id', 'created_at', 'updated_at', 'version', 'metadata'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with related objects."""
        return super().get_queryset(request).select_related('project', 'user')