"""
Admin interface for the Agent Registry system
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json

# Session 392: Updated to use canonical import path
from core.models.agents_registry import (
    UnifiedAgentTemplate,
    AgentExecution,
    AgentOrchestration,
    AgentTool,
    AgentRegistry
)


@admin.register(UnifiedAgentTemplate)
class UnifiedAgentTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'display_name', 'specialization', 'llm_provider', 
        'success_rate', 'usage_count', 'avg_user_rating', 'is_active',
        'is_verified', 'is_public'
    ]
    list_filter = [
        'specialization', 'llm_provider', 'is_active', 'is_verified', 
        'is_public', 'supports_streaming', 'learning_enabled'
    ]
    search_fields = ['name', 'display_name', 'description', 'capabilities']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'usage_count', 'success_rate',
        'avg_completion_time', 'avg_user_rating', 'version'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name', 'display_name', 'description', 'specialization',
                'creator', 'organization'
            )
        }),
        ('Capabilities & Configuration', {
            'fields': (
                'capabilities', 'required_tools', 'optional_tools',
                'system_prompt', 'personality_traits'
            )
        }),
        ('AI Model Configuration', {
            'fields': (
                'llm_provider', 'llm_model', 'llm_config',
                'fallback_provider', 'fallback_model'
            )
        }),
        ('Routing & Discovery', {
            'fields': (
                'routing_keywords', 'routing_patterns', 'domain_tags',
                'confidence_score'
            )
        }),
        ('Performance & Metrics', {
            'fields': (
                'usage_count', 'success_rate', 'avg_completion_time',
                'avg_user_rating', 'estimated_cost_per_execution',
                'avg_token_usage', 'resource_requirements'
            )
        }),
        ('Version & Lifecycle', {
            'fields': (
                'agent_version', 'parent_template', 'is_template',
                'is_public', 'is_verified'
            )
        }),
        ('Advanced Features', {
            'fields': (
                'supports_streaming', 'supports_interruption', 
                'supports_collaboration', 'max_concurrent_executions',
                'learning_enabled', 'self_improvement_enabled'
            )
        }),
        ('System Fields', {
            'fields': ('id', 'created_at', 'updated_at', 'version', 'is_active'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('creator', 'parent_template')


@admin.register(AgentExecution)
class AgentExecutionAdmin(admin.ModelAdmin):
    list_display = [
        'execution_id', 'template_name', 'status', 'priority', 
        'progress_percentage', 'started_at', 'execution_time_seconds',
        'total_cost', 'user_rating'
    ]
    list_filter = [
        'status', 'priority', 'template__specialization',
        'started_at', 'completed_at'
    ]
    search_fields = [
        'execution_id', 'template__name', 'task_description', 
        'user__username'
    ]
    readonly_fields = [
        'id', 'execution_id', 'created_at', 'updated_at', 
        'started_at', 'completed_at', 'execution_time_seconds'
    ]
    
    def template_name(self, obj):
        return obj.template.name
    template_name.short_description = 'Agent Template'
    template_name.admin_order_field = 'template__name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('template', 'user')


@admin.register(AgentOrchestration)
class AgentOrchestrationAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'status', 'execution_strategy', 'current_agent_index', 
        'progress_percentage', 'agent_count', 'total_cost', 'created_at'
    ]
    list_filter = ['status', 'execution_strategy', 'created_at']
    search_fields = ['name', 'description', 'agent_sequence']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'progress_percentage',
        'total_execution_time'
    ]
    
    def agent_count(self, obj):
        return len(obj.agent_sequence)
    agent_count.short_description = 'Agent Count'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(AgentTool)
class AgentToolAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'display_name', 'tool_type', 'usage_count', 
        'avg_response_time_ms', 'success_rate', 'is_active'
    ]
    list_filter = ['tool_type', 'is_active']
    search_fields = ['name', 'display_name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'usage_count']
    filter_horizontal = ['compatible_agents']


@admin.register(AgentRegistry)
class AgentRegistryAdmin(admin.ModelAdmin):
    list_display = [
        'registry_name', 'total_agents', 'active_agents', 
        'total_executions', 'avg_success_rate', 'last_updated'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'total_agents', 'active_agents',
        'total_executions', 'avg_success_rate', 'avg_execution_time', 'last_updated'
    ]
    
    actions = ['rebuild_indexes']
    
    def rebuild_indexes(self, request, queryset):
        for registry in queryset:
            registry.rebuild_indexes()
        self.message_user(request, f"Rebuilt indexes for {queryset.count()} registries.")
    rebuild_indexes.short_description = "Rebuild agent indexes"


# Custom admin site configuration
admin.site.site_header = 'Unified Donkey Betz Platform Administration'
admin.site.site_title = 'Unified Platform Admin'
admin.site.index_title = 'Platform Management'
