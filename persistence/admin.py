"""
Django admin interface for Data Persistence models.
"""

from django.contrib import admin
from django.db.models import Count, Avg, Sum
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    UnifiedEmbedding, AgentKnowledge, SpiderData, SpiderDataRoute,
    AgentCollaborationSession, DataPersistenceMetrics
)


@admin.register(UnifiedEmbedding)
class UnifiedEmbeddingAdmin(admin.ModelAdmin):
    list_display = (
        'content_type', 'content_title_short', 'source_system', 'creator_agent',
        'importance_score', 'access_count', 'created_at'
    )
    list_filter = (
        'content_type', 'source_system', 'embedding_model', 'created_at',
        'importance_score'
    )
    search_fields = ('content_title', 'content_text', 'creator_agent', 'tags')
    readonly_fields = (
        'content_hash', 'embedding_dimension', 'generation_cost',
        'generation_time_ms', 'access_count', 'last_accessed'
    )
    fieldsets = (
        ('Content Information', {
            'fields': ('content_type', 'content_id', 'content_title', 'content_text')
        }),
        ('Embedding Configuration', {
            'fields': ('embedding_model', 'embedding_dimension', 'embedding')
        }),
        ('Source and Creation', {
            'fields': ('source_system', 'creator_agent', 'creator_user')
        }),
        ('Scoring and Relevance', {
            'fields': ('importance_score', 'relevance_score', 'confidence_score')
        }),
        ('Categorization', {
            'fields': ('tags', 'category', 'content_metadata')
        }),
        ('Usage Tracking', {
            'fields': ('access_count', 'last_accessed', 'search_count')
        }),
        ('Performance Metrics', {
            'fields': ('generation_cost', 'generation_time_ms')
        }),
        ('Timestamps', {
            'fields': ('content_timestamp', 'expires_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def content_title_short(self, obj):
        title = obj.content_title or obj.content_text
        return title[:50] + '...' if len(title) > 50 else title
    content_title_short.short_description = 'Content'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('creator_user')


@admin.register(AgentKnowledge)
class AgentKnowledgeAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'agent_name', 'knowledge_type', 'confidence_score',
        'usage_count', 'success_rate', 'is_public', 'created_at'
    )
    list_filter = (
        'knowledge_type', 'agent_name', 'is_public', 'access_level',
        'domain_tags', 'created_at'
    )
    search_fields = ('title', 'summary', 'agent_name', 'domain_tags')
    readonly_fields = (
        'validation_count', 'success_rate', 'failure_count',
        'usage_count', 'last_used', 'accessed_by'
    )
    filter_horizontal = ('related_knowledge',)

    fieldsets = (
        ('Knowledge Information', {
            'fields': ('title', 'knowledge_type', 'summary', 'content')
        }),
        ('Agent and Ownership', {
            'fields': ('agent_name', 'agent_id')
        }),
        ('Context and Applicability', {
            'fields': ('context', 'domain_tags', 'applicable_agents')
        }),
        ('Sharing and Access', {
            'fields': ('is_public', 'access_level', 'shared_with')
        }),
        ('Quality Metrics', {
            'fields': ('confidence_score', 'validation_count', 'success_rate', 'failure_count')
        }),
        ('Usage Tracking', {
            'fields': ('usage_count', 'last_used', 'accessed_by')
        }),
        ('Relationships', {
            'fields': ('related_knowledge', 'superseded_by', 'embedding'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('related_knowledge')

    actions = ['mark_as_verified', 'share_with_all_agents']

    def mark_as_verified(self, request, queryset):
        queryset.update(confidence_score=1.0)
        self.message_user(request, f"Marked {queryset.count()} knowledge entries as verified.")
    mark_as_verified.short_description = "Mark selected knowledge as verified"

    def share_with_all_agents(self, request, queryset):
        for knowledge in queryset:
            knowledge.is_public = True
            knowledge.access_level = 'read'
            knowledge.save()
        self.message_user(request, f"Shared {queryset.count()} knowledge entries with all agents.")
    share_with_all_agents.short_description = "Share with all agents"


@admin.register(SpiderData)
class SpiderDataAdmin(admin.ModelAdmin):
    list_display = (
        'title_short', 'spider_name', 'source_platform', 'data_type',
        'opportunity_score', 'conversion_status', 'revenue_generated',
        'is_processed', 'discovered_at'
    )
    list_filter = (
        'spider_name', 'source_platform', 'data_type', 'conversion_status',
        'is_processed', 'discovered_at'
    )
    search_fields = ('title', 'content', 'spider_name', 'tags')
    readonly_fields = (
        'content_hash', 'spider_execution_id', 'routed_to_agents',
        'agent_responses', 'discovered_at', 'last_updated_at'
    )

    fieldsets = (
        ('Discovery Information', {
            'fields': ('spider_name', 'spider_version', 'spider_execution_id')
        }),
        ('Source Details', {
            'fields': ('source_url', 'source_platform', 'source_metadata')
        }),
        ('Content', {
            'fields': ('title', 'content', 'structured_data', 'raw_html')
        }),
        ('Classification', {
            'fields': ('data_type', 'category', 'tags')
        }),
        ('Scoring', {
            'fields': ('relevance_score', 'opportunity_score', 'quality_score', 'urgency_score')
        }),
        ('Processing Status', {
            'fields': ('is_processed', 'processed_at', 'processing_result')
        }),
        ('Agent Routing', {
            'fields': ('routed_to_agents', 'agent_responses')
        }),
        ('Revenue Tracking', {
            'fields': ('revenue_generated', 'revenue_potential', 'conversion_status')
        }),
        ('Duplicate Detection', {
            'fields': ('content_hash', 'similar_discoveries'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('discovered_at', 'expires_at', 'last_updated_at'),
            'classes': ('collapse',)
        }),
    )

    def title_short(self, obj):
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_short.short_description = 'Title'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('similar_discoveries')

    actions = ['route_to_income_builder', 'mark_as_processed', 'mark_as_converted']

    def route_to_income_builder(self, request, queryset):
        for spider_data in queryset:
            spider_data.route_to_agent('income_builder', 'high')
        self.message_user(request, f"Routed {queryset.count()} items to Income Builder.")
    route_to_income_builder.short_description = "Route to Income Builder agent"

    def mark_as_processed(self, request, queryset):
        queryset.update(is_processed=True, processed_at=timezone.now())
        self.message_user(request, f"Marked {queryset.count()} items as processed.")
    mark_as_processed.short_description = "Mark as processed"

    def mark_as_converted(self, request, queryset):
        queryset.update(conversion_status='converted')
        self.message_user(request, f"Marked {queryset.count()} items as converted.")
    mark_as_converted.short_description = "Mark as converted"


@admin.register(SpiderDataRoute)
class SpiderDataRouteAdmin(admin.ModelAdmin):
    list_display = (
        'spider_data_title', 'target_agent', 'priority', 'status',
        'created_at', 'processed_at'
    )
    list_filter = ('target_agent', 'priority', 'status', 'created_at')
    search_fields = ('spider_data__title', 'target_agent', 'routing_reason')
    readonly_fields = ('created_at', 'processed_at')

    def spider_data_title(self, obj):
        return obj.spider_data.title[:50]
    spider_data_title.short_description = 'Spider Data'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('spider_data')


@admin.register(AgentCollaborationSession)
class AgentCollaborationSessionAdmin(admin.ModelAdmin):
    list_display = (
        'session_name', 'participating_agents_count', 'session_status',
        'knowledge_generated_count', 'created_at'
    )
    list_filter = ('session_status', 'created_at')
    search_fields = ('session_name', 'session_goal', 'participating_agents')
    filter_horizontal = ('knowledge_generated',)

    def participating_agents_count(self, obj):
        return len(obj.participating_agents)
    participating_agents_count.short_description = 'Agents'

    def knowledge_generated_count(self, obj):
        return obj.knowledge_generated.count()
    knowledge_generated_count.short_description = 'Knowledge Generated'


@admin.register(DataPersistenceMetrics)
class DataPersistenceMetricsAdmin(admin.ModelAdmin):
    list_display = (
        'metric_name', 'subsystem', 'metric_type', 'metric_value',
        'timestamp'
    )
    list_filter = ('subsystem', 'metric_type', 'timestamp')
    search_fields = ('metric_name', 'subsystem')
    readonly_fields = ('timestamp',)

    def changelist_view(self, request, extra_context=None):
        # Add summary statistics to the changelist view
        response = super().changelist_view(request, extra_context=extra_context)

        try:
            qs = response.context_data['cl'].queryset

            # Calculate summary statistics
            summary_stats = {
                'total_metrics': qs.count(),
                'subsystems': qs.values('subsystem').distinct().count(),
                'recent_metrics': qs.filter(
                    timestamp__gte=timezone.now() - timedelta(hours=24)
                ).count(),
            }

            response.context_data['summary_stats'] = summary_stats
        except (AttributeError, KeyError):
            pass

        return response


# Inline admin for embedding relationships
class UnifiedEmbeddingInline(admin.TabularInline):
    model = UnifiedEmbedding
    extra = 0
    readonly_fields = ('content_type', 'embedding_model', 'importance_score', 'access_count')
    fields = ('content_type', 'embedding_model', 'importance_score', 'access_count')

    def has_add_permission(self, request, obj):
        return False  # Prevent manual creation of embeddings


# Custom admin site configuration
admin.site.site_header = "Unified Donkey Betz - Data Persistence"
admin.site.site_title = "Data Persistence Admin"
admin.site.index_title = "Data Persistence Infrastructure"