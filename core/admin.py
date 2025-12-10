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