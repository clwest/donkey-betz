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