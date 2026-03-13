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


# =============================================================================
# Session 406: Legal Case Management Admin
# =============================================================================
from .models_legal import CaseProfile, Party, Attorney, Child, CaseDocument


class PartyInline(admin.TabularInline):
    """Inline display of parties in case profile."""
    model = Party
    extra = 0
    fields = ('party_type', 'full_name', 'email', 'phone', 'is_pro_se')


class ChildInline(admin.TabularInline):
    """Inline display of children in case profile."""
    model = Child
    extra = 0
    fields = ('full_name', 'date_of_birth', 'age')
    readonly_fields = ('age',)


class CaseDocumentInline(admin.TabularInline):
    """Inline display of documents in case profile."""
    model = CaseDocument
    extra = 0
    fields = ('document_type', 'title', 'entered_date', 'file')


@admin.register(CaseProfile)
class CaseProfileAdmin(admin.ModelAdmin):
    """Admin interface for legal case profiles."""

    list_display = ('case_number', 'case_type', 'county', 'status', 'user', 'updated_at')
    list_filter = ('case_type', 'status', 'county', 'state')
    search_fields = ('case_number', 'case_title', 'county')
    readonly_fields = ('id', 'created_at', 'updated_at')

    inlines = [PartyInline, ChildInline, CaseDocumentInline]

    fieldsets = (
        (None, {
            'fields': ('user', 'case_number', 'case_title', 'case_type', 'status')
        }),
        ('Court Information', {
            'fields': ('county', 'state', 'district', 'division', 'courtroom', 'court_address')
        }),
        ('Dates', {
            'fields': ('filing_date',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('System Info', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class AttorneyInline(admin.TabularInline):
    """Inline display of attorneys for a party."""
    model = Attorney
    extra = 0
    fields = ('full_name', 'firm_name', 'email', 'phone', 'bar_number')


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    """Admin interface for parties."""

    list_display = ('full_name', 'party_type', 'case_profile', 'is_pro_se', 'email')
    list_filter = ('party_type', 'is_pro_se')
    search_fields = ('full_name', 'email', 'case_profile__case_number')
    readonly_fields = ('id', 'created_at', 'updated_at')

    inlines = [AttorneyInline]

    fieldsets = (
        (None, {
            'fields': ('case_profile', 'party_type', 'full_name', 'first_name', 'is_pro_se')
        }),
        ('Contact Information', {
            'fields': ('address', 'city', 'state', 'zip_code', 'phone', 'email')
        }),
        ('System Info', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Attorney)
class AttorneyAdmin(admin.ModelAdmin):
    """Admin interface for attorneys."""

    list_display = ('full_name', 'firm_name', 'party', 'email', 'bar_number')
    search_fields = ('full_name', 'firm_name', 'email', 'bar_number')
    readonly_fields = ('id', 'created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('party', 'full_name', 'first_name', 'firm_name')
        }),
        ('Contact Information', {
            'fields': ('address', 'city', 'state', 'zip_code', 'phone', 'email')
        }),
        ('Bar Information', {
            'fields': ('bar_number',)
        }),
        ('System Info', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    """Admin interface for children."""

    list_display = ('full_name', 'case_profile', 'date_of_birth', 'age')
    search_fields = ('full_name', 'case_profile__case_number')
    readonly_fields = ('id', 'created_at', 'updated_at', 'age')

    fieldsets = (
        (None, {
            'fields': ('case_profile', 'full_name', 'first_name', 'date_of_birth')
        }),
        ('System Info', {
            'fields': ('id', 'age', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CaseDocument)
class CaseDocumentAdmin(admin.ModelAdmin):
    """Admin interface for case documents."""

    list_display = ('title', 'document_type', 'case_profile', 'entered_date', 'uploaded_at')
    list_filter = ('document_type', 'entered_date')
    search_fields = ('title', 'case_profile__case_number')
    readonly_fields = ('id', 'uploaded_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('case_profile', 'document_type', 'title', 'file')
        }),
        ('Dates', {
            'fields': ('entered_date',)
        }),
        ('Content', {
            'fields': ('extracted_text', 'notes'),
            'classes': ('collapse',)
        }),
        ('System Info', {
            'fields': ('id', 'uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ==================== SKIN Layer Models (Session 695) ====================
# Updated Session 785: Added WorkspaceTrigger and WorkspaceTriggerConfig
from .models_skin_layer import (
    ProjectWorkspace, WorkspaceOperation, WorkspaceContext,
    WorkspaceTrigger, WorkspaceTriggerConfig
)


@admin.register(ProjectWorkspace)
class ProjectWorkspaceAdmin(admin.ModelAdmin):
    """Admin interface for project workspaces (SKIN layer)."""

    list_display = (
        'name', 'user', 'workspace_type', 'is_active',
        'frontend_framework', 'backend_framework',
        'total_operations', 'total_files_written', 'updated_at'
    )
    list_filter = ('workspace_type', 'is_active', 'allow_file_write', 'require_human_review')
    search_fields = ('name', 'root_path', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at', 'total_operations', 'total_files_written', 'total_commits')

    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('name', 'user', 'description', 'is_active')
        }),
        ('Location', {
            'fields': ('workspace_type', 'root_path', 'git_remote_url', 'current_branch')
        }),
        ('Tech Stack', {
            'fields': ('tech_stack', 'entry_points')
        }),
        ('Permissions', {
            'fields': (
                'allow_file_write', 'allow_file_delete',
                'allow_command_execution', 'allow_git_operations',
                'protected_paths', 'require_human_review'
            )
        }),
        ('Statistics', {
            'fields': ('total_operations', 'total_files_written', 'total_commits', 'last_operation_at'),
            'classes': ('collapse',)
        }),
        ('System Info', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WorkspaceOperation)
class WorkspaceOperationAdmin(admin.ModelAdmin):
    """Admin interface for workspace operations (SKIN layer audit trail)."""

    list_display = (
        'operation_type', 'file_path_short', 'agent_name',
        'success', 'workspace', 'requires_review', 'reviewed_by_human', 'created_at'
    )
    list_filter = ('operation_type', 'success', 'requires_review', 'reviewed_by_human', 'rolled_back')
    search_fields = ('file_path', 'agent_name', 'agent_task', 'command')
    readonly_fields = (
        'id', 'created_at', 'file_size_before', 'file_size_after',
        'execution_time_ms', 'reviewed_at'
    )

    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('workspace', 'user', 'agent_name', 'agent_task', 'operation_type')
        }),
        ('File Operation', {
            'fields': ('file_path', 'file_content_before', 'file_content_after', 'file_size_before', 'file_size_after'),
            'classes': ('collapse',)
        }),
        ('Command Operation', {
            'fields': ('command', 'command_output', 'command_error', 'exit_code'),
            'classes': ('collapse',)
        }),
        ('Result', {
            'fields': ('success', 'error_message', 'execution_time_ms')
        }),
        ('Human Review', {
            'fields': ('requires_review', 'reviewed_by_human', 'human_approved', 'human_feedback', 'reviewed_at')
        }),
        ('Rollback', {
            'fields': ('can_rollback', 'rolled_back', 'rollback_operation')
        }),
        ('System Info', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def file_path_short(self, obj):
        """Truncate file path for display."""
        if obj.file_path and len(obj.file_path) > 40:
            return f"...{obj.file_path[-37:]}"
        return obj.file_path or obj.command[:40] if obj.command else '-'
    file_path_short.short_description = 'File/Command'


@admin.register(WorkspaceContext)
class WorkspaceContextAdmin(admin.ModelAdmin):
    """Admin interface for workspace context (SKIN layer understanding)."""

    list_display = (
        'workspace', 'total_files', 'total_directories',
        'total_lines_of_code', 'last_scanned_at'
    )
    search_fields = ('workspace__name',)
    readonly_fields = ('workspace', 'last_scanned_at', 'scan_duration_ms')

    fieldsets = (
        (None, {
            'fields': ('workspace',)
        }),
        ('File Structure', {
            'fields': ('file_tree', 'key_files', 'directory_purposes'),
            'classes': ('collapse',)
        }),
        ('Patterns & Dependencies', {
            'fields': ('coding_patterns', 'dependencies', 'import_aliases'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': (
                'total_files', 'total_directories', 'total_lines_of_code',
                'file_type_counts'
            )
        }),
        ('Scan Info', {
            'fields': ('last_scanned_at', 'scan_depth', 'scan_duration_ms', 'excluded_patterns'),
            'classes': ('collapse',)
        }),
    )


# ==================== Session 785: Workspace Trigger System ====================

@admin.register(WorkspaceTrigger)
class WorkspaceTriggerAdmin(admin.ModelAdmin):
    """Admin interface for workspace triggers (hybrid autopilot work queue)."""

    list_display = (
        'title_short', 'trigger_type', 'priority', 'status',
        'target_agent_display', 'source_spider', 'expires_at', 'created_at'
    )
    list_filter = ('status', 'trigger_type', 'priority', 'target_category')
    search_fields = ('title', 'description', 'target_agent', 'source_spider')
    readonly_fields = (
        'id', 'dedupe_hash', 'source_spider_data_id', 'execution_id',
        'created_at', 'updated_at', 'queued_at', 'started_at', 'completed_at',
        'execution_time_ms'
    )

    date_hierarchy = 'created_at'
    ordering = ['-priority', '-created_at']

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'trigger_type', 'priority', 'status')
        }),
        ('Target', {
            'fields': ('workspace', 'target_agent', 'target_category')
        }),
        ('Source', {
            'fields': ('source_spider', 'source_spider_data_id', 'source_agent', 'source_user_id'),
            'classes': ('collapse',)
        }),
        ('Context', {
            'fields': ('context_data',),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('ttl_hours', 'expires_at', 'queued_at', 'started_at', 'completed_at', 'execution_time_ms')
        }),
        ('Execution', {
            'fields': ('execution_id', 'result_summary', 'error_message'),
            'classes': ('collapse',)
        }),
        ('System Info', {
            'fields': ('id', 'dedupe_hash', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_expired', 'mark_pending', 'delete_completed']

    def title_short(self, obj):
        """Truncate title for display."""
        if obj.title and len(obj.title) > 50:
            return f"{obj.title[:47]}..."
        return obj.title
    title_short.short_description = 'Title'

    def target_agent_display(self, obj):
        """Show agent or category."""
        return obj.target_agent or f"[{obj.target_category}]" or 'Auto'
    target_agent_display.short_description = 'Agent/Category'

    @admin.action(description='Mark selected as expired')
    def mark_expired(self, request, queryset):
        count = queryset.update(status='expired')
        self.message_user(request, f"Marked {count} triggers as expired.")

    @admin.action(description='Reset selected to pending')
    def mark_pending(self, request, queryset):
        count = queryset.update(status='pending')
        self.message_user(request, f"Reset {count} triggers to pending.")

    @admin.action(description='Delete completed triggers')
    def delete_completed(self, request, queryset):
        count = queryset.filter(status='completed').delete()[0]
        self.message_user(request, f"Deleted {count} completed triggers.")


@admin.register(WorkspaceTriggerConfig)
class WorkspaceTriggerConfigAdmin(admin.ModelAdmin):
    """Admin interface for workspace trigger configurations (rules)."""

    list_display = (
        'name', 'is_active', 'trigger_type', 'target_agent',
        'target_category', 'priority', 'total_triggers_created', 'last_triggered_at'
    )
    list_filter = ('is_active', 'trigger_type', 'match_operator', 'priority')
    search_fields = ('name', 'description', 'target_agent', 'match_value')
    readonly_fields = ('total_triggers_created', 'last_triggered_at', 'created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Spider Matching', {
            'fields': ('target_spiders',)
        }),
        ('Content Matching', {
            'fields': ('match_field', 'match_operator', 'match_value')
        }),
        ('Trigger Settings', {
            'fields': ('trigger_type', 'trigger_title_template', 'target_agent', 'target_category', 'priority', 'ttl_hours')
        }),
        ('Rate Limiting', {
            'fields': ('cooldown_minutes', 'last_triggered_at')
        }),
        ('Statistics', {
            'fields': ('total_triggers_created',),
            'classes': ('collapse',)
        }),
        ('System Info', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['enable_configs', 'disable_configs']

    @admin.action(description='Enable selected configs')
    def enable_configs(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"Enabled {count} configs.")

    @admin.action(description='Disable selected configs')
    def disable_configs(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"Disabled {count} configs.")


# =============================================================================
# Session 701: HEART Service (System Health Monitoring)
# =============================================================================

from core.models_heart import HeartBeat, ComponentStatus


@admin.register(HeartBeat)
class HeartBeatAdmin(admin.ModelAdmin):
    """Admin interface for system heartbeat records."""

    list_display = (
        'recorded_at', 'overall_status', 'health_score',
        'components_healthy', 'components_checked', 'check_duration_ms', 'alerts_sent'
    )
    list_filter = ('overall_status', 'is_alive', 'alerts_sent', 'recorded_at')
    search_fields = ('id',)
    readonly_fields = (
        'id', 'recorded_at', 'health_score', 'overall_status', 'is_alive',
        'components', 'check_duration_ms', 'components_checked',
        'components_healthy', 'alerts_sent'
    )
    date_hierarchy = 'recorded_at'
    ordering = ('-recorded_at',)

    fieldsets = (
        ('Health Status', {
            'fields': ('overall_status', 'health_score', 'is_alive', 'alerts_sent')
        }),
        ('Component Summary', {
            'fields': ('components_checked', 'components_healthy', 'check_duration_ms')
        }),
        ('Component Details', {
            'fields': ('components',),
            'classes': ('collapse',)
        }),
        ('System Info', {
            'fields': ('id', 'recorded_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ComponentStatus)
class ComponentStatusAdmin(admin.ModelAdmin):
    """Admin interface for component status records."""

    list_display = (
        'component', 'display_name', 'status', 'is_healthy',
        'response_time_ms', 'uptime_percent_24h', 'last_check'
    )
    list_filter = ('status', 'is_healthy')
    search_fields = ('component', 'display_name')
    readonly_fields = (
        'component', 'last_check', 'last_healthy', 'check_count_24h',
        'error_count_24h', 'created_at', 'updated_at'
    )
    ordering = ('component',)

    fieldsets = (
        ('Component Info', {
            'fields': ('component', 'display_name', 'description')
        }),
        ('Current Status', {
            'fields': ('status', 'is_healthy', 'response_time_ms', 'last_error')
        }),
        ('24-Hour Metrics', {
            'fields': ('uptime_percent_24h', 'check_count_24h', 'error_count_24h')
        }),
        ('Details', {
            'fields': ('details',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('last_check', 'last_healthy', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =============================================================================
# SESSION 702: LUNGS SERVICE ADMIN (Resource & Capacity Management)
# =============================================================================

from core.models_lungs import Budget, BreathCycle, RespiratoryStatus


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    """Admin interface for budget configuration."""

    list_display = (
        'name', 'scope', 'scope_identifier', 'period',
        'cost_limit', 'token_limit', 'warning_threshold',
        'is_active', 'enforce_hard_limit', 'updated_at'
    )
    list_filter = ('scope', 'period', 'is_active', 'enforce_hard_limit')
    search_fields = ('name', 'scope_identifier')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('scope', 'name')

    fieldsets = (
        ('Budget Info', {
            'fields': ('name', 'scope', 'scope_identifier', 'period')
        }),
        ('Limits', {
            'fields': ('cost_limit', 'token_limit')
        }),
        ('Thresholds', {
            'fields': ('warning_threshold', 'critical_threshold')
        }),
        ('Settings', {
            'fields': ('is_active', 'enforce_hard_limit')
        }),
        ('System Info', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BreathCycle)
class BreathCycleAdmin(admin.ModelAdmin):
    """Admin interface for breath cycle records."""

    list_display = (
        'budget', 'period_start', 'tokens_used', 'cost_incurred',
        'call_count', 'utilization_percent', 'warning_sent',
        'critical_sent', 'recorded_at'
    )
    list_filter = (
        'budget__scope', 'warning_sent', 'critical_sent',
        'on_pace_to_exceed', 'period_start'
    )
    search_fields = ('budget__name',)
    readonly_fields = (
        'id', 'budget', 'period_start', 'period_end', 'tokens_used',
        'cost_incurred', 'call_count', 'tokens_remaining', 'cost_remaining',
        'utilization_percent', 'projected_end_usage', 'on_pace_to_exceed',
        'warning_sent', 'critical_sent', 'recorded_at'
    )
    date_hierarchy = 'period_start'
    ordering = ('-period_start',)

    fieldsets = (
        ('Period', {
            'fields': ('budget', 'period_start', 'period_end')
        }),
        ('Consumption', {
            'fields': ('tokens_used', 'cost_incurred', 'call_count')
        }),
        ('Remaining', {
            'fields': ('tokens_remaining', 'cost_remaining', 'utilization_percent')
        }),
        ('Forecast', {
            'fields': ('projected_end_usage', 'on_pace_to_exceed')
        }),
        ('Alerts', {
            'fields': ('warning_sent', 'critical_sent')
        }),
        ('System Info', {
            'fields': ('id', 'recorded_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RespiratoryStatus)
class RespiratoryStatusAdmin(admin.ModelAdmin):
    """Admin interface for respiratory status cache."""

    list_display = (
        'component', 'display_name', 'status', 'oxygen_level',
        'cost_today', 'calls_today', 'daily_cost_limit', 'last_check'
    )
    list_filter = ('status',)
    search_fields = ('component', 'display_name')
    readonly_fields = (
        'component', 'tokens_used_today', 'cost_today', 'calls_today',
        'last_breath', 'last_check'
    )
    ordering = ('component',)

    fieldsets = (
        ('Component Info', {
            'fields': ('component', 'display_name')
        }),
        ('Current Status', {
            'fields': ('status', 'oxygen_level', 'respiratory_rate')
        }),
        ('Today\'s Usage', {
            'fields': ('tokens_used_today', 'cost_today', 'calls_today')
        }),
        ('Limits', {
            'fields': ('daily_token_limit', 'daily_cost_limit')
        }),
        ('Timestamps', {
            'fields': ('last_breath', 'last_check'),
            'classes': ('collapse',)
        }),
    )


# =============================================================================
# SESSION 703: CIRCULATORY SYSTEM ADMIN (Data Flow Monitoring)
# =============================================================================

from core.models_circulatory import FlowRoute, CirculationPulse, FlowStatus


@admin.register(FlowRoute)
class FlowRouteAdmin(admin.ModelAdmin):
    """Admin interface for flow route configuration."""

    list_display = (
        'name', 'display_name', 'route_type', 'identifier',
        'max_depth', 'max_latency_ms', 'is_active', 'is_critical'
    )
    list_filter = ('route_type', 'is_active', 'is_critical')
    search_fields = ('name', 'display_name', 'identifier')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('route_type', 'name')

    fieldsets = (
        ('Route Info', {
            'fields': ('name', 'display_name', 'route_type', 'identifier')
        }),
        ('Thresholds', {
            'fields': ('max_depth', 'max_latency_ms', 'min_throughput')
        }),
        ('Settings', {
            'fields': ('is_active', 'is_critical', 'description')
        }),
        ('System Info', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CirculationPulse)
class CirculationPulseAdmin(admin.ModelAdmin):
    """Admin interface for circulation pulse records."""

    list_display = (
        'recorded_at', 'overall_status', 'flow_score',
        'total_routes_checked', 'routes_healthy', 'routes_blocked',
        'bottleneck_count', 'total_items_in_transit', 'check_duration_ms'
    )
    list_filter = ('overall_status', 'recorded_at')
    search_fields = ()
    readonly_fields = (
        'id', 'overall_status', 'flow_score', 'total_routes_checked',
        'routes_healthy', 'routes_slow', 'routes_congested', 'routes_blocked',
        'total_items_in_transit', 'total_throughput', 'avg_latency_ms',
        'max_latency_ms', 'bottlenecks', 'bottleneck_count', 'route_details',
        'check_duration_ms', 'recorded_at'
    )
    date_hierarchy = 'recorded_at'
    ordering = ('-recorded_at',)

    fieldsets = (
        ('Overall Status', {
            'fields': ('overall_status', 'flow_score')
        }),
        ('Route Counts', {
            'fields': ('total_routes_checked', 'routes_healthy', 'routes_slow',
                       'routes_congested', 'routes_blocked')
        }),
        ('Flow Metrics', {
            'fields': ('total_items_in_transit', 'total_throughput',
                       'avg_latency_ms', 'max_latency_ms')
        }),
        ('Bottlenecks', {
            'fields': ('bottleneck_count', 'bottlenecks')
        }),
        ('Details', {
            'fields': ('route_details', 'check_duration_ms', 'recorded_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FlowStatus)
class FlowStatusAdmin(admin.ModelAdmin):
    """Admin interface for flow status cache."""

    list_display = (
        'route', 'status', 'is_healthy', 'health_score',
        'current_depth', 'current_throughput', 'current_latency_ms',
        'active_workers', 'last_check'
    )
    list_filter = ('status', 'is_healthy')
    search_fields = ('route__name', 'route__display_name')
    readonly_fields = (
        'route', 'status', 'is_healthy', 'health_score', 'current_depth',
        'current_throughput', 'current_latency_ms', 'items_processed_24h',
        'errors_24h', 'avg_latency_24h_ms', 'peak_depth_24h', 'peak_latency_24h_ms',
        'active_workers', 'active_tasks', 'reserved_tasks', 'last_activity',
        'last_check', 'status_changed_at', 'congestion_alert_sent',
        'blocked_alert_sent', 'last_alert_at', 'details', 'error_message'
    )
    ordering = ('route__route_type', 'route__name')

    fieldsets = (
        ('Route Info', {
            'fields': ('route',)
        }),
        ('Current Status', {
            'fields': ('status', 'is_healthy', 'health_score')
        }),
        ('Current Metrics', {
            'fields': ('current_depth', 'current_throughput', 'current_latency_ms')
        }),
        ('24h Metrics', {
            'fields': ('items_processed_24h', 'errors_24h', 'avg_latency_24h_ms',
                       'peak_depth_24h', 'peak_latency_24h_ms')
        }),
        ('Worker Info', {
            'fields': ('active_workers', 'active_tasks', 'reserved_tasks')
        }),
        ('Timestamps', {
            'fields': ('last_activity', 'last_check', 'status_changed_at')
        }),
        ('Alerts', {
            'fields': ('congestion_alert_sent', 'blocked_alert_sent', 'last_alert_at')
        }),
        ('Details', {
            'fields': ('details', 'error_message'),
            'classes': ('collapse',)
        }),
    )


# =============================================================================
# SESSION 704: SPINE SYSTEM ADMIN (Central API Router)
# =============================================================================

from core.models_spine import RoutePattern, RouteMetrics, SpineStatus, RequestTrace


@admin.register(RoutePattern)
class RoutePatternAdmin(admin.ModelAdmin):
    """Admin interface for route pattern configuration."""

    list_display = (
        'pattern', 'display_name', 'category', 'priority',
        'max_latency_ms', 'max_error_rate', 'is_active', 'is_monitored'
    )
    list_filter = ('category', 'priority', 'is_active', 'is_monitored')
    search_fields = ('pattern', 'display_name', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('category', 'pattern')

    fieldsets = (
        ('Pattern Info', {
            'fields': ('pattern', 'display_name', 'category', 'priority', 'description')
        }),
        ('Health Thresholds', {
            'fields': ('max_latency_ms', 'max_error_rate', 'min_availability')
        }),
        ('Rate Limiting', {
            'fields': ('rate_limit_per_minute', 'rate_limit_per_hour')
        }),
        ('Routing Configuration', {
            'fields': ('requires_healthy_heart', 'requires_healthy_lungs', 'fallback_response')
        }),
        ('Status', {
            'fields': ('is_active', 'is_monitored')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RouteMetrics)
class RouteMetricsAdmin(admin.ModelAdmin):
    """Admin interface for route metrics records."""

    list_display = (
        'recorded_at', 'pattern', 'health_score', 'is_healthy',
        'total_requests', 'error_rate', 'avg_latency_ms', 'p95_latency_ms'
    )
    list_filter = ('is_healthy', 'recorded_at', 'pattern__category')
    search_fields = ('pattern__pattern', 'pattern__display_name')
    readonly_fields = (
        'id', 'pattern', 'total_requests', 'successful_requests', 'failed_requests',
        'rate_limited_requests', 'status_2xx', 'status_3xx', 'status_4xx', 'status_5xx',
        'avg_latency_ms', 'p50_latency_ms', 'p95_latency_ms', 'p99_latency_ms', 'max_latency_ms',
        'success_rate', 'error_rate', 'throughput', 'is_healthy', 'health_score',
        'period_start', 'period_end', 'period_duration_seconds', 'recorded_at'
    )
    date_hierarchy = 'recorded_at'
    ordering = ('-recorded_at',)

    fieldsets = (
        ('Pattern', {
            'fields': ('pattern',)
        }),
        ('Health', {
            'fields': ('is_healthy', 'health_score')
        }),
        ('Request Counts', {
            'fields': ('total_requests', 'successful_requests', 'failed_requests', 'rate_limited_requests')
        }),
        ('Status Codes', {
            'fields': ('status_2xx', 'status_3xx', 'status_4xx', 'status_5xx')
        }),
        ('Latency', {
            'fields': ('avg_latency_ms', 'p50_latency_ms', 'p95_latency_ms', 'p99_latency_ms', 'max_latency_ms')
        }),
        ('Derived Metrics', {
            'fields': ('success_rate', 'error_rate', 'throughput')
        }),
        ('Period', {
            'fields': ('period_start', 'period_end', 'period_duration_seconds', 'recorded_at')
        }),
    )


@admin.register(SpineStatus)
class SpineStatusAdmin(admin.ModelAdmin):
    """Admin interface for spine status cache."""

    list_display = (
        'status', 'health_score', 'is_healthy',
        'total_patterns', 'healthy_patterns', 'degraded_patterns', 'failed_patterns',
        'routes_blocked', 'last_check'
    )
    list_filter = ('status', 'is_healthy')
    readonly_fields = (
        'id', 'status', 'is_healthy', 'health_score',
        'total_patterns', 'healthy_patterns', 'degraded_patterns', 'failed_patterns',
        'total_requests', 'requests_per_second', 'avg_latency_ms', 'error_rate',
        'category_health', 'heart_status', 'lungs_status', 'circulatory_status',
        'routes_blocked', 'routes_rate_limited', 'fallbacks_active',
        'last_check', 'status_changed_at', 'alert_sent', 'last_alert_at'
    )

    fieldsets = (
        ('Overall Status', {
            'fields': ('status', 'is_healthy', 'health_score')
        }),
        ('Pattern Counts', {
            'fields': ('total_patterns', 'healthy_patterns', 'degraded_patterns', 'failed_patterns')
        }),
        ('Request Metrics', {
            'fields': ('total_requests', 'requests_per_second', 'avg_latency_ms', 'error_rate')
        }),
        ('Integration Status', {
            'fields': ('heart_status', 'lungs_status', 'circulatory_status')
        }),
        ('Routing Status', {
            'fields': ('routes_blocked', 'routes_rate_limited', 'fallbacks_active')
        }),
        ('Category Health', {
            'fields': ('category_health',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('last_check', 'status_changed_at')
        }),
        ('Alerts', {
            'fields': ('alert_sent', 'last_alert_at')
        }),
    )


@admin.register(RequestTrace)
class RequestTraceAdmin(admin.ModelAdmin):
    """Admin interface for request traces."""

    list_display = (
        'correlation_id', 'method', 'path', 'status_code',
        'duration_ms', 'is_authenticated', 'started_at'
    )
    list_filter = ('method', 'status_code', 'is_authenticated', 'was_rate_limited', 'used_fallback')
    search_fields = ('correlation_id', 'path', 'routed_to_agent', 'error_type')
    readonly_fields = (
        'id', 'correlation_id', 'method', 'path', 'pattern',
        'user_id', 'is_authenticated', 'client_ip',
        'started_at', 'ended_at', 'duration_ms',
        'status_code', 'response_size',
        'was_rate_limited', 'used_fallback', 'health_check_result',
        'routed_to_agent', 'llm_model_used',
        'error_type', 'error_message'
    )
    date_hierarchy = 'started_at'
    ordering = ('-started_at',)

    fieldsets = (
        ('Request', {
            'fields': ('correlation_id', 'method', 'path', 'pattern')
        }),
        ('User', {
            'fields': ('user_id', 'is_authenticated', 'client_ip')
        }),
        ('Timing', {
            'fields': ('started_at', 'ended_at', 'duration_ms')
        }),
        ('Response', {
            'fields': ('status_code', 'response_size')
        }),
        ('Routing', {
            'fields': ('was_rate_limited', 'used_fallback', 'health_check_result',
                       'routed_to_agent', 'llm_model_used')
        }),
        ('Errors', {
            'fields': ('error_type', 'error_message'),
            'classes': ('collapse',)
        }),
    )


# =============================================================================
# SESSION 705: IMMUNE SYSTEM ADMIN (Security & Threat Detection)
# =============================================================================

from core.models_immune import ThreatPattern, ThreatEvent, ImmuneResponse, Quarantine, ImmuneStatus


@admin.register(ThreatPattern)
class ThreatPatternAdmin(admin.ModelAdmin):
    """Admin interface for threat pattern configuration."""

    list_display = (
        'name', 'display_name', 'category', 'severity',
        'detection_type', 'auto_respond', 'response_action',
        'total_detections', 'is_active'
    )
    list_filter = ('category', 'severity', 'detection_type', 'auto_respond', 'is_active', 'is_builtin')
    search_fields = ('name', 'display_name', 'description', 'pattern')
    readonly_fields = ('id', 'total_detections', 'last_detection', 'created_at', 'updated_at')
    ordering = ('severity', 'category', 'name')

    fieldsets = (
        ('Pattern Info', {
            'fields': ('name', 'display_name', 'category', 'severity', 'detection_type', 'description')
        }),
        ('Detection Configuration', {
            'fields': ('pattern', 'threshold_count', 'threshold_window_seconds')
        }),
        ('Response Configuration', {
            'fields': ('auto_respond', 'response_action', 'block_duration_minutes')
        }),
        ('Status', {
            'fields': ('is_active', 'is_builtin')
        }),
        ('Statistics', {
            'fields': ('total_detections', 'last_detection'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ThreatEvent)
class ThreatEventAdmin(admin.ModelAdmin):
    """Admin interface for threat events."""

    list_display = (
        'detected_at', 'category', 'severity', 'status',
        'source_ip', 'source_user_id', 'confidence_score', 'response_taken'
    )
    list_filter = ('status', 'severity', 'category', 'detected_at')
    search_fields = ('source_ip', 'source_path', 'source_user_agent', 'notes')
    readonly_fields = (
        'id', 'pattern', 'status', 'severity', 'category',
        'source_ip', 'source_user_id', 'source_user_agent', 'source_path', 'source_method',
        'detection_details', 'confidence_score', 'request_count', 'correlation_ids',
        'response_taken', 'response_at', 'detected_at', 'resolved_at', 'notes'
    )
    date_hierarchy = 'detected_at'
    ordering = ('-detected_at',)

    fieldsets = (
        ('Event Info', {
            'fields': ('pattern', 'status', 'severity', 'category')
        }),
        ('Source', {
            'fields': ('source_ip', 'source_user_id', 'source_user_agent', 'source_path', 'source_method')
        }),
        ('Detection', {
            'fields': ('detection_details', 'confidence_score', 'request_count', 'correlation_ids')
        }),
        ('Response', {
            'fields': ('response_taken', 'response_at')
        }),
        ('Timestamps', {
            'fields': ('detected_at', 'resolved_at')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ImmuneResponse)
class ImmuneResponseAdmin(admin.ModelAdmin):
    """Admin interface for immune responses."""

    list_display = (
        'responded_at', 'action', 'target_type', 'target_value',
        'is_automatic', 'success', 'duration_minutes'
    )
    list_filter = ('action', 'target_type', 'is_automatic', 'success')
    search_fields = ('target_value', 'responded_by')
    readonly_fields = (
        'id', 'event', 'action', 'is_automatic', 'success',
        'target_type', 'target_value', 'duration_minutes', 'expires_at',
        'details', 'responded_at', 'responded_by'
    )
    date_hierarchy = 'responded_at'
    ordering = ('-responded_at',)

    fieldsets = (
        ('Response Info', {
            'fields': ('event', 'action', 'is_automatic', 'success')
        }),
        ('Target', {
            'fields': ('target_type', 'target_value')
        }),
        ('Duration', {
            'fields': ('duration_minutes', 'expires_at')
        }),
        ('Metadata', {
            'fields': ('details', 'responded_at', 'responded_by')
        }),
    )


@admin.register(Quarantine)
class QuarantineAdmin(admin.ModelAdmin):
    """Admin interface for quarantine entries."""

    list_display = (
        'entity_type', 'entity_value', 'reason', 'is_permanent',
        'is_active', 'blocked_requests', 'created_at', 'expires_at'
    )
    list_filter = ('entity_type', 'reason', 'is_permanent', 'is_active')
    search_fields = ('entity_value', 'notes')
    readonly_fields = (
        'id', 'entity_type', 'entity_value', 'reason', 'is_permanent', 'expires_at',
        'total_events', 'blocked_requests', 'last_blocked_at',
        'created_at', 'created_by', 'updated_at'
    )
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        ('Entity', {
            'fields': ('entity_type', 'entity_value')
        }),
        ('Block Details', {
            'fields': ('reason', 'is_permanent', 'expires_at', 'is_active')
        }),
        ('Statistics', {
            'fields': ('total_events', 'blocked_requests', 'last_blocked_at')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'created_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ImmuneStatus)
class ImmuneStatusAdmin(admin.ModelAdmin):
    """Admin interface for immune status cache."""

    list_display = (
        'status', 'health_score', 'is_healthy', 'threat_level',
        'active_threats', 'threats_detected_24h', 'total_quarantined', 'last_scan'
    )
    list_filter = ('status', 'is_healthy', 'threat_level')
    readonly_fields = (
        'id', 'status', 'is_healthy', 'health_score', 'threat_level',
        'active_threats', 'threats_detected_24h', 'threats_blocked_24h', 'false_positives_24h',
        'quarantined_ips', 'quarantined_users', 'total_quarantined',
        'active_patterns', 'patterns_triggered_24h',
        'auto_responses_24h', 'manual_responses_24h', 'avg_response_time_ms',
        'threats_by_category', 'threats_by_severity',
        'spine_connected', 'heart_connected',
        'last_scan', 'last_threat', 'status_changed_at',
        'alert_sent', 'last_alert_at'
    )

    fieldsets = (
        ('Overall Status', {
            'fields': ('status', 'is_healthy', 'health_score', 'threat_level')
        }),
        ('Threat Activity', {
            'fields': ('active_threats', 'threats_detected_24h', 'threats_blocked_24h', 'false_positives_24h')
        }),
        ('Quarantine Status', {
            'fields': ('quarantined_ips', 'quarantined_users', 'total_quarantined')
        }),
        ('Pattern Activity', {
            'fields': ('active_patterns', 'patterns_triggered_24h')
        }),
        ('Response Metrics', {
            'fields': ('auto_responses_24h', 'manual_responses_24h', 'avg_response_time_ms')
        }),
        ('Category Breakdown', {
            'fields': ('threats_by_category', 'threats_by_severity'),
            'classes': ('collapse',)
        }),
        ('Integration Status', {
            'fields': ('spine_connected', 'heart_connected')
        }),
        ('Timestamps', {
            'fields': ('last_scan', 'last_threat', 'status_changed_at')
        }),
        ('Alerts', {
            'fields': ('alert_sent', 'last_alert_at')
        }),
    )


# =============================================================================
# SESSION 706: DIGESTIVE SYSTEM ADMIN (Data Ingestion & Processing)
# =============================================================================

from core.models_digestive import IngestionRoute, DigestivePulse, DigestionStatus


@admin.register(IngestionRoute)
class IngestionRouteAdmin(admin.ModelAdmin):
    """Admin interface for ingestion route configuration."""

    list_display = (
        'name', 'display_name', 'route_type', 'stage', 'is_active',
        'is_critical', 'total_items_processed', 'total_errors', 'last_activity'
    )
    list_filter = ('route_type', 'stage', 'is_active', 'is_critical', 'is_builtin')
    search_fields = ('name', 'display_name', 'identifier', 'description')
    readonly_fields = (
        'id', 'total_items_processed', 'total_errors', 'last_activity',
        'created_at', 'updated_at'
    )
    date_hierarchy = 'created_at'
    ordering = ('stage', 'name')

    fieldsets = (
        ('Identification', {
            'fields': ('name', 'display_name', 'identifier', 'description')
        }),
        ('Route Type', {
            'fields': ('route_type', 'stage')
        }),
        ('Thresholds', {
            'fields': ('max_queue_depth', 'target_throughput', 'max_processing_time_ms')
        }),
        ('Status', {
            'fields': ('is_active', 'is_critical', 'is_builtin')
        }),
        ('Statistics', {
            'fields': ('total_items_processed', 'total_errors', 'last_activity'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DigestivePulse)
class DigestivePulseAdmin(admin.ModelAdmin):
    """Admin interface for digestive pulse history."""

    list_display = (
        'overall_status', 'digestion_score', 'items_ingested_24h',
        'items_processed_24h', 'items_pending', 'processing_throughput',
        'check_duration_ms', 'recorded_at'
    )
    list_filter = ('overall_status', 'recorded_at')
    readonly_fields = (
        'id', 'overall_status', 'digestion_score',
        'items_ingested_24h', 'spiders_executed_24h', 'intake_errors_24h',
        'items_processed_24h', 'items_pending', 'processing_throughput', 'avg_processing_time_ms',
        'embeddings_generated_24h', 'embedding_coverage_pct',
        'items_routed_24h', 'items_filtered_24h',
        'bottlenecks', 'check_duration_ms', 'recorded_at'
    )
    date_hierarchy = 'recorded_at'
    ordering = ('-recorded_at',)

    fieldsets = (
        ('Overall Status', {
            'fields': ('overall_status', 'digestion_score')
        }),
        ('Intake Stage', {
            'fields': ('items_ingested_24h', 'spiders_executed_24h', 'intake_errors_24h')
        }),
        ('Processing Stage', {
            'fields': ('items_processed_24h', 'items_pending', 'processing_throughput', 'avg_processing_time_ms')
        }),
        ('Enrichment Stage', {
            'fields': ('embeddings_generated_24h', 'embedding_coverage_pct')
        }),
        ('Routing Stage', {
            'fields': ('items_routed_24h', 'items_filtered_24h')
        }),
        ('Bottlenecks', {
            'fields': ('bottlenecks',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'check_duration_ms', 'recorded_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DigestionStatus)
class DigestionStatusAdmin(admin.ModelAdmin):
    """Admin interface for per-route digestion status cache."""

    list_display = (
        'route', 'status', 'is_healthy', 'current_queue_depth',
        'current_throughput', 'success_rate_24h', 'last_check'
    )
    list_filter = ('status', 'is_healthy')
    search_fields = ('route__name', 'route__display_name')
    readonly_fields = (
        'route', 'status', 'is_healthy',
        'current_queue_depth', 'current_throughput', 'current_latency_ms',
        'items_ingested_24h', 'items_processed_24h', 'items_output_24h',
        'errors_24h', 'success_rate_24h',
        'last_intake', 'last_output', 'last_check'
    )
    ordering = ('route__stage', 'route__name')

    fieldsets = (
        ('Route', {
            'fields': ('route',)
        }),
        ('Current Status', {
            'fields': ('status', 'is_healthy')
        }),
        ('Current Metrics', {
            'fields': ('current_queue_depth', 'current_throughput', 'current_latency_ms')
        }),
        ('24h Metrics', {
            'fields': ('items_ingested_24h', 'items_processed_24h', 'items_output_24h', 'errors_24h', 'success_rate_24h')
        }),
        ('Timestamps', {
            'fields': ('last_intake', 'last_output', 'last_check')
        }),
    )


# =============================================================================
# Session 707: MUSCULAR SYSTEM Admin
# =============================================================================

from core.models_muscular import MuscleGroup, MuscularPulse, MuscleStatus


@admin.register(MuscleGroup)
class MuscleGroupAdmin(admin.ModelAdmin):
    """Admin interface for muscle group configuration."""

    list_display = (
        'name', 'display_name', 'category', 'is_active',
        'is_critical', 'total_executions', 'total_successful', 'total_failed', 'last_execution'
    )
    list_filter = ('category', 'is_active', 'is_critical', 'is_builtin')
    search_fields = ('name', 'display_name', 'description')
    readonly_fields = (
        'id', 'total_executions', 'total_successful', 'total_failed', 'last_execution',
        'created_at', 'updated_at'
    )
    ordering = ('category', 'name')

    fieldsets = (
        ('Group Info', {
            'fields': ('id', 'name', 'display_name', 'category', 'description')
        }),
        ('Agents', {
            'fields': ('agent_names',)
        }),
        ('Thresholds', {
            'fields': ('target_success_rate', 'max_avg_execution_time_ms', 'max_fatigue_level', 'max_daily_executions')
        }),
        ('Status', {
            'fields': ('is_active', 'is_critical', 'is_builtin')
        }),
        ('Statistics', {
            'fields': ('total_executions', 'total_successful', 'total_failed', 'last_execution'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MuscularPulse)
class MuscularPulseAdmin(admin.ModelAdmin):
    """Admin interface for muscular pulse history."""

    list_display = (
        'overall_status', 'strength_score', 'total_executions_24h',
        'successful_executions_24h', 'success_rate_24h', 'active_agents',
        'check_duration_ms', 'recorded_at'
    )
    list_filter = ('overall_status', 'recorded_at')
    readonly_fields = (
        'id', 'overall_status', 'strength_score',
        'total_executions_24h', 'successful_executions_24h', 'failed_executions_24h',
        'success_rate_24h', 'avg_execution_time_ms', 'total_tokens_used_24h',
        'total_cost_24h', 'total_agents', 'active_agents', 'idle_agents',
        'fatigued_agents', 'strained_agents', 'group_metrics', 'weak_muscles',
        'overworked_muscles', 'groups_checked', 'groups_strong', 'groups_fit',
        'groups_fatigued', 'groups_strained', 'groups_paralyzed',
        'heart_connected', 'digestive_connected', 'check_duration_ms', 'recorded_at'
    )
    ordering = ('-recorded_at',)

    fieldsets = (
        ('Overall Status', {
            'fields': ('id', 'overall_status', 'strength_score', 'is_strong')
        }),
        ('Execution Metrics (24h)', {
            'fields': ('total_executions_24h', 'successful_executions_24h', 'failed_executions_24h', 'success_rate_24h')
        }),
        ('Performance Metrics', {
            'fields': ('avg_execution_time_ms', 'min_execution_time_ms', 'max_execution_time_ms',
                      'total_tokens_used_24h', 'total_cost_24h')
        }),
        ('Agent Metrics', {
            'fields': ('total_agents', 'active_agents', 'idle_agents', 'fatigued_agents', 'strained_agents')
        }),
        ('Group Status', {
            'fields': ('groups_checked', 'groups_strong', 'groups_fit', 'groups_fatigued',
                      'groups_strained', 'groups_paralyzed'),
            'classes': ('collapse',)
        }),
        ('Issues', {
            'fields': ('weak_muscles', 'overworked_muscles'),
            'classes': ('collapse',)
        }),
        ('Integrations', {
            'fields': ('heart_connected', 'digestive_connected')
        }),
        ('Metadata', {
            'fields': ('check_duration_ms', 'recorded_at')
        }),
    )


@admin.register(MuscleStatus)
class MuscleStatusAdmin(admin.ModelAdmin):
    """Admin interface for per-group muscle status cache."""

    list_display = (
        'group', 'status', 'is_healthy', 'strength_score',
        'fatigue_level', 'strain_level', 'success_rate_24h', 'last_check'
    )
    list_filter = ('status', 'is_healthy')
    search_fields = ('group__name', 'group__display_name')
    readonly_fields = (
        'group', 'status', 'is_healthy', 'strength_score',
        'fatigue_level', 'strain_level', 'executions_24h', 'successful_24h',
        'failed_24h', 'success_rate_24h', 'avg_execution_time_ms',
        'tokens_used_24h', 'cost_24h', 'total_agents', 'active_agents', 'idle_agents',
        'top_performer', 'worst_performer',
        'last_execution', 'last_success', 'last_failure', 'last_check'
    )
    ordering = ('group__category', 'group__name')

    fieldsets = (
        ('Group', {
            'fields': ('group',)
        }),
        ('Current Status', {
            'fields': ('status', 'is_healthy', 'strength_score', 'fatigue_level', 'strain_level')
        }),
        ('24h Metrics', {
            'fields': ('executions_24h', 'successful_24h', 'failed_24h', 'success_rate_24h',
                      'avg_execution_time_ms', 'tokens_used_24h', 'cost_24h')
        }),
        ('Agent Counts', {
            'fields': ('total_agents', 'active_agents', 'idle_agents')
        }),
        ('Performers', {
            'fields': ('top_performer', 'worst_performer')
        }),
        ('Timestamps', {
            'fields': ('last_execution', 'last_success', 'last_failure', 'last_check')
        }),
    )


# ── Preview System (Workspace Hosted Previews + Magic Links) ─────────────

from .models_preview_system import (
    WorkspaceProject, ProjectRepo, ProjectEnvVar,
    PreviewEnvironment, PreviewDeployment, DeployJob, PreviewService,
    MagicLink, FeedbackItem,
)


@admin.register(WorkspaceProject)
class WorkspaceProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'workspace', 'default_preview_ttl_minutes', 'created_at')
    search_fields = ('name', 'slug')
    list_filter = ('workspace',)


@admin.register(ProjectRepo)
class ProjectRepoAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'type', 'build_system', 'default_ref')
    list_filter = ('type', 'build_system', 'provider')


@admin.register(ProjectEnvVar)
class ProjectEnvVarAdmin(admin.ModelAdmin):
    list_display = ('key', 'environment', 'project', 'repo', 'is_secret')
    list_filter = ('environment', 'is_secret')


@admin.register(PreviewEnvironment)
class PreviewEnvironmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'status', 'ttl_expires_at', 'created_at')
    list_filter = ('status',)


@admin.register(PreviewDeployment)
class PreviewDeploymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'preview_env', 'trigger', 'status', 'started_at', 'finished_at')
    list_filter = ('status', 'trigger')


@admin.register(DeployJob)
class DeployJobAdmin(admin.ModelAdmin):
    list_display = ('repo', 'deployment', 'status', 'started_at', 'finished_at')
    list_filter = ('status',)


@admin.register(PreviewService)
class PreviewServiceAdmin(admin.ModelAdmin):
    list_display = ('service_type', 'preview_env', 'repo', 'public_url', 'health_status')
    list_filter = ('service_type', 'health_status')


@admin.register(MagicLink)
class MagicLinkAdmin(admin.ModelAdmin):
    list_display = ('label', 'preview_env', 'scope', 'uses', 'max_uses', 'expires_at', 'created_at')
    list_filter = ('scope',)
    readonly_fields = ('token_hash', 'uses')


@admin.register(FeedbackItem)
class FeedbackItemAdmin(admin.ModelAdmin):
    list_display = ('message_preview', 'severity', 'status', 'category', 'source', 'reporter_name', 'created_at')
    list_filter = ('severity', 'status', 'category', 'source')
    search_fields = ('message', 'reporter_name', 'reporter_email')

    def message_preview(self, obj):
        return obj.message[:80]
    message_preview.short_description = 'Message'