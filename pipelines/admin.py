"""
Django Admin for Creative Pipelines

Session 109 - Creative Pipelines v1
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import CreativePipelineTemplate, CreativePipelineRun


@admin.register(CreativePipelineTemplate)
class CreativePipelineTemplateAdmin(admin.ModelAdmin):
    """Admin interface for Creative Pipeline Templates"""

    list_display = ('slug', 'name', 'is_active', 'created_at', 'runs_count')
    list_filter = ('is_active', 'created_at')
    search_fields = ('slug', 'name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'runs_count')

    fieldsets = (
        ('Basic Information', {
            'fields': ('slug', 'name', 'description', 'is_active')
        }),
        ('Configuration', {
            'fields': ('config',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'runs_count'),
            'classes': ('collapse',)
        }),
    )

    def runs_count(self, obj):
        """Display total number of runs for this template"""
        count = obj.runs.count()
        return format_html('<b>{}</b> runs', count)
    runs_count.short_description = 'Total Runs'


@admin.register(CreativePipelineRun)
class CreativePipelineRunAdmin(admin.ModelAdmin):
    """Admin interface for Creative Pipeline Runs"""

    list_display = (
        'id',
        'template_name',
        'user',
        'status_badge',
        'progress',
        'created_at',
        'duration_display'
    )
    list_filter = ('status', 'template', 'created_at')
    search_fields = ('id', 'user__username', 'template__name')
    readonly_fields = (
        'id',
        'created_at',
        'updated_at',
        'completed_at',
        'duration_display',
        'progress_percentage'
    )

    fieldsets = (
        ('Run Information', {
            'fields': (
                'id',
                'user',
                'template',
                'project',
                'session',
                'status'
            )
        }),
        ('Progress', {
            'fields': ('current_step', 'total_steps', 'progress_percentage')
        }),
        ('Data', {
            'fields': ('input_payload', 'output_payload'),
            'classes': ('collapse',)
        }),
        ('Execution Log', {
            'fields': ('log', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at', 'duration_display'),
            'classes': ('collapse',)
        }),
    )

    def template_name(self, obj):
        """Display template name"""
        return obj.template.name
    template_name.short_description = 'Template'
    template_name.admin_order_field = 'template__name'

    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'pending': '#FFA500',     # Orange
            'running': '#2196F3',     # Blue
            'completed': '#4CAF50',   # Green
            'failed': '#F44336',      # Red
        }
        color = colors.get(obj.status, '#9E9E9E')  # Default gray
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def progress(self, obj):
        """Display progress bar"""
        percentage = obj.progress_percentage
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; '
            'border-radius: 3px; overflow: hidden;">'
            '<div style="width: {}%; background-color: #2196F3; '
            'height: 20px; text-align: center; color: white; '
            'font-size: 12px; line-height: 20px;">{:.0f}%</div></div>',
            percentage,
            percentage
        )
    progress.short_description = 'Progress'

    def duration_display(self, obj):
        """Display run duration"""
        seconds = obj.duration
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds / 60:.1f}m"
        else:
            return f"{seconds / 3600:.1f}h"
    duration_display.short_description = 'Duration'
