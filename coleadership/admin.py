"""
Co-Leadership Django Admin - Session 99

Admin interface for managing co-leadership decisions, recommendations, and outcomes.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    CoLeadershipDecision,
    AdvisorDecisionRecommendation,
    HumanDecision,
    DecisionOutcome,
    CoLeadershipPreferences
)


class AdvisorDecisionRecommendationInline(admin.TabularInline):
    model = AdvisorDecisionRecommendation
    extra = 0
    readonly_fields = ['created_at', 'confidence']
    fields = ['agent_template', 'stance', 'summary', 'confidence', 'created_at']


class HumanDecisionInline(admin.StackedInline):
    model = HumanDecision
    extra = 0
    readonly_fields = ['created_at']


class DecisionOutcomeInline(admin.StackedInline):
    model = DecisionOutcome
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CoLeadershipDecision)
class CoLeadershipDecisionAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'initiated_by',
        'created_at',
        'frozen_status',
        'outcome_status',
        'project',
        'session'
    ]
    list_filter = ['created_at', 'frozen_at']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'created_at', 'frozen_at']
    inlines = [AdvisorDecisionRecommendationInline, HumanDecisionInline, DecisionOutcomeInline]

    fieldsets = (
        ('Decision Details', {
            'fields': ('id', 'title', 'description')
        }),
        ('Context', {
            'fields': ('project', 'session')
        }),
        ('Timeline', {
            'fields': ('initiated_by', 'created_at', 'frozen_at')
        }),
    )

    def frozen_status(self, obj):
        if obj.is_frozen:
            return format_html('<span style="color: green;">✅ Frozen</span>')
        return format_html('<span style="color: orange;">⏳ Open</span>')
    frozen_status.short_description = 'Status'

    def outcome_status(self, obj):
        if obj.has_outcome:
            outcome = obj.outcome
            color_map = {
                'success': 'green',
                'failure': 'red',
                'mixed': 'orange',
                'pending': 'gray'
            }
            color = color_map.get(outcome.status, 'black')
            return format_html(
                '<span style="color: {};">{}</span>',
                color,
                outcome.get_status_display()
            )
        return format_html('<span style="color: gray;">No outcome</span>')
    outcome_status.short_description = 'Outcome'


@admin.register(AdvisorDecisionRecommendation)
class AdvisorDecisionRecommendationAdmin(admin.ModelAdmin):
    list_display = [
        'decision',
        'agent_template',
        'stance',
        'confidence',
        'created_at'
    ]
    list_filter = ['stance', 'agent_template', 'created_at']
    search_fields = ['decision__title', 'summary', 'recommendation_text']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Decision Context', {
            'fields': ('decision', 'agent_template')
        }),
        ('Recommendation', {
            'fields': ('stance', 'summary', 'recommendation_text')
        }),
        ('Analysis', {
            'fields': ('risk_analysis', 'alternative_paths')
        }),
        ('Metadata', {
            'fields': ('confidence', 'time_horizon', 'created_at')
        }),
        ('Raw Data', {
            'fields': ('raw_payload',),
            'classes': ('collapse',)
        }),
    )


@admin.register(HumanDecision)
class HumanDecisionAdmin(admin.ModelAdmin):
    list_display = [
        'decision',
        'chosen_path_summary_short',
        'is_override',
        'overridden_agent',
        'created_at'
    ]
    list_filter = ['is_override', 'created_at']
    search_fields = ['decision__title', 'chosen_path_summary', 'justification']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Decision', {
            'fields': ('decision',)
        }),
        ('Human Choice', {
            'fields': ('chosen_path_summary', 'justification')
        }),
        ('Override Information', {
            'fields': ('is_override', 'overridden_agent')
        }),
        ('Timeline', {
            'fields': ('created_at',)
        }),
    )

    def chosen_path_summary_short(self, obj):
        return obj.chosen_path_summary[:50] + '...' if len(obj.chosen_path_summary) > 50 else obj.chosen_path_summary
    chosen_path_summary_short.short_description = 'Chosen Path'


@admin.register(DecisionOutcome)
class DecisionOutcomeAdmin(admin.ModelAdmin):
    list_display = [
        'decision',
        'status',
        'attribution',
        'told_you_so_triggered',
        'realized_at',
        'created_at'
    ]
    list_filter = ['status', 'attribution', 'told_you_so_triggered', 'created_at']
    search_fields = ['decision__title', 'outcome_summary', 'told_you_so_message']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Decision', {
            'fields': ('decision',)
        }),
        ('Outcome Details', {
            'fields': ('status', 'realized_at', 'outcome_summary', 'metrics')
        }),
        ('Attribution', {
            'fields': ('attribution', 'ai_confidence_snapshot', 'human_confidence_snapshot')
        }),
        ('I Told You So', {
            'fields': ('told_you_so_triggered', 'told_you_so_message')
        }),
        ('Timeline', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(CoLeadershipPreferences)
class CoLeadershipPreferencesAdmin(admin.ModelAdmin):
    """Admin for user co-leadership preferences"""
    list_display = ['user', 'allow_told_you_so', 'tone', 'updated_at']
    list_filter = ['allow_told_you_so', 'tone', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Preferences', {
            'fields': ('allow_told_you_so', 'tone'),
            'description': 'Control how the AI interacts with you in co-leadership decisions.'
        }),
        ('Timeline', {
            'fields': ('created_at', 'updated_at')
        }),
    )
