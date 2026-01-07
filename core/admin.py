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
from .models_skin_layer import ProjectWorkspace, WorkspaceOperation, WorkspaceContext


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