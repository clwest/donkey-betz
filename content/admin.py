"""
Content Management System Admin

Django admin interface for content management models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    ContentTemplate, Document, DocumentEmbedding, KnowledgeBase,
    ContentGeneration, ContentWorkflow, WorkflowExecution, ContentAnalytics,
    ImageHistory, VideoHistory, MiniFigAsset, CreativeProject, ProjectWorkflow
)


@admin.register(ContentTemplate)
class ContentTemplateAdmin(admin.ModelAdmin):
    """Admin interface for content templates"""
    
    list_display = [
        'display_name', 'template_type', 'category', 'usage_count', 
        'success_rate', 'is_public', 'is_verified', 'creator_name', 'created_at'
    ]
    list_filter = [
        'template_type', 'category', 'llm_provider', 'is_public', 
        'is_verified', 'is_active', 'created_at'
    ]
    search_fields = ['name', 'display_name', 'description', 'tags']
    readonly_fields = [
        'usage_count', 'avg_generation_time', 'success_rate', 
        'avg_user_rating', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'display_name', 'description', 'template_type', 'category')
        }),
        ('Template Configuration', {
            'fields': ('system_prompt', 'user_prompt_template', 'variables', 'output_format')
        }),
        ('AI Configuration', {
            'fields': ('llm_provider', 'llm_model', 'generation_config')
        }),
        ('Metadata', {
            'fields': ('tags', 'routing_keywords', 'capabilities')
        }),
        ('Statistics', {
            'fields': ('usage_count', 'avg_generation_time', 'success_rate', 'avg_user_rating'),
            'classes': ('collapse',)
        }),
        ('Access Control', {
            'fields': ('creator', 'is_public', 'is_verified', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def creator_name(self, obj):
        return obj.creator.username if obj.creator else 'System'
    creator_name.short_description = 'Creator'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new template
            obj.creator = request.user
        super().save_model(request, obj, form, change)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin interface for documents"""
    
    list_display = [
        'title', 'document_type', 'status', 'owner_name', 'file_size_mb',
        'word_count', 'view_count', 'has_embeddings', 'created_at'
    ]
    list_filter = [
        'document_type', 'status', 'source', 'language', 'category',
        'is_public', 'created_at', 'source_system'
    ]
    search_fields = ['title', 'description', 'tags', 'key_phrases']
    readonly_fields = [
        'content_hash', 'word_count', 'readability_score', 'extracted_metadata',
        'key_phrases', 'entities', 'view_count', 'download_count', 
        'last_accessed', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'document_type', 'category', 'collection')
        }),
        ('File Information', {
            'fields': ('file_path', 'original_filename', 'file_size', 'mime_type')
        }),
        ('Content', {
            'fields': ('raw_content', 'processed_content'),
            'classes': ('collapse',)
        }),
        ('Processing', {
            'fields': ('status', 'processing_log', 'error_message')
        }),
        ('Analysis', {
            'fields': (
                'content_hash', 'language', 'word_count', 'readability_score',
                'extracted_metadata', 'key_phrases', 'entities'
            ),
            'classes': ('collapse',)
        }),
        ('Organization', {
            'fields': ('tags', 'owner', 'is_public')
        }),
        ('Usage Statistics', {
            'fields': ('view_count', 'download_count', 'last_accessed'),
            'classes': ('collapse',)
        }),
        ('Cross-System Integration', {
            'fields': ('source_system', 'source_reference', 'cross_references'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def owner_name(self, obj):
        return obj.owner.username
    owner_name.short_description = 'Owner'
    
    def file_size_mb(self, obj):
        if obj.file_size:
            return f"{obj.file_size / (1024*1024):.2f} MB"
        return "N/A"
    file_size_mb.short_description = 'File Size'
    
    def has_embeddings(self, obj):
        return obj.embeddings.exists()
    has_embeddings.boolean = True
    has_embeddings.short_description = 'Has Embeddings'


@admin.register(DocumentEmbedding)
class DocumentEmbeddingAdmin(admin.ModelAdmin):
    """Admin interface for document embeddings"""
    
    list_display = [
        'document_title', 'embedding_model', 'chunk_index', 'chunk_size',
        'embedding_dimension', 'processing_time_ms', 'embedding_cost', 'created_at'
    ]
    list_filter = ['embedding_model', 'created_at']
    search_fields = ['document__title', 'chunk_text']
    readonly_fields = [
        'embedding_dimension', 'processing_time_ms', 'embedding_cost',
        'created_at', 'updated_at'
    ]
    
    def document_title(self, obj):
        return obj.document.title
    document_title.short_description = 'Document'


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    """Admin interface for knowledge bases"""
    
    list_display = [
        'name', 'domain', 'document_count', 'total_chunks', 'total_tokens',
        'owner_name', 'is_public', 'last_indexed'
    ]
    list_filter = ['domain', 'embedding_model', 'is_public', 'created_at']
    search_fields = ['name', 'description', 'tags', 'categories']
    readonly_fields = [
        'document_count', 'total_chunks', 'total_tokens', 'last_indexed',
        'created_at', 'updated_at'
    ]
    
    def owner_name(self, obj):
        return obj.owner.username
    owner_name.short_description = 'Owner'


@admin.register(ContentGeneration)
class ContentGenerationAdmin(admin.ModelAdmin):
    """Admin interface for content generations"""
    
    list_display = [
        'id', 'template_name', 'user_name', 'status', 'generation_time_ms',
        'generation_cost', 'user_rating', 'created_at'
    ]
    list_filter = [
        'status', 'source_system', 'template', 'knowledge_base', 
        'user_rating', 'created_at'
    ]
    search_fields = ['prompt', 'generated_content', 'user_feedback']
    readonly_fields = [
        'generated_content', 'generation_time_ms', 'token_usage',
        'generation_cost', 'quality_score', 'retry_count', 'output_document',
        'created_at', 'updated_at'
    ]
    
    def template_name(self, obj):
        return obj.template.display_name if obj.template else 'Custom'
    template_name.short_description = 'Template'
    
    def user_name(self, obj):
        return obj.user.username
    user_name.short_description = 'User'


@admin.register(ContentWorkflow)
class ContentWorkflowAdmin(admin.ModelAdmin):
    """Admin interface for content workflows"""
    
    list_display = [
        'name', 'domain', 'execution_count', 'success_rate',
        'avg_execution_time', 'creator_name', 'is_public', 'created_at'
    ]
    list_filter = ['domain', 'is_public', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = [
        'execution_count', 'success_rate', 'avg_execution_time',
        'created_at', 'updated_at'
    ]
    
    def creator_name(self, obj):
        return obj.creator.username if obj.creator else 'System'
    creator_name.short_description = 'Creator'


@admin.register(WorkflowExecution)
class WorkflowExecutionAdmin(admin.ModelAdmin):
    """Admin interface for workflow executions"""
    
    list_display = [
        'id', 'workflow_name', 'user_name', 'status', 'progress_percentage',
        'execution_time_seconds', 'started_at', 'completed_at'
    ]
    list_filter = ['status', 'workflow', 'created_at']
    search_fields = ['workflow__name', 'user__username']
    readonly_fields = [
        'status', 'current_step', 'progress_percentage', 'step_results',
        'final_output', 'started_at', 'completed_at', 'execution_time_seconds',
        'created_at', 'updated_at'
    ]
    
    def workflow_name(self, obj):
        return obj.workflow.name
    workflow_name.short_description = 'Workflow'
    
    def user_name(self, obj):
        return obj.user.username
    user_name.short_description = 'User'


@admin.register(ContentAnalytics)
class ContentAnalyticsAdmin(admin.ModelAdmin):
    """Admin interface for content analytics"""
    
    list_display = [
        'metric_name', 'subsystem', 'metric_value', 'metric_type',
        'user_name', 'timestamp'
    ]
    list_filter = ['subsystem', 'metric_type', 'time_period', 'timestamp']
    search_fields = ['metric_name', 'context']
    readonly_fields = ['timestamp']
    
    def user_name(self, obj):
        return obj.user.username if obj.user else 'System'
    user_name.short_description = 'User'
    
    def has_add_permission(self, request):
        # Analytics are automatically generated
        return False


@admin.register(ImageHistory)
class ImageHistoryAdmin(admin.ModelAdmin):
    """Admin interface for image history (Session 36: Feature 9)"""

    list_display = [
        'thumbnail_preview', 'filename', 'image_type', 'model_used', 'style',
        'user_name', 'dimensions', 'file_size_display', 'is_favorite',
        'view_count', 'download_count', 'created_at'
    ]
    list_filter = [
        'image_type', 'model_used', 'style', 'is_favorite',
        'is_active', 'created_at'
    ]
    search_fields = ['filename', 'prompt', 'user_notes', 'tags']
    readonly_fields = [
        'thumbnail_display', 'image_display', 'id', 'filename', 'file_path',
        'image_width', 'image_height', 'file_size_bytes',
        'view_count', 'download_count', 'created_at', 'updated_at'
    ]

    fieldsets = (
        ('Image Information', {
            'fields': ('thumbnail_display', 'filename', 'file_path', 'image_type')
        }),
        ('Generation/Edit Parameters', {
            'fields': ('prompt', 'model_used', 'style', 'parameters')
        }),
        ('Image Metadata', {
            'fields': ('image_width', 'image_height', 'file_size_bytes')
        }),
        ('User Organization', {
            'fields': ('user', 'is_favorite', 'user_notes', 'tags')
        }),
        ('Lineage', {
            'fields': ('parent_image',),
            'classes': ('collapse',)
        }),
        ('Usage Statistics', {
            'fields': ('view_count', 'download_count'),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('id', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def user_name(self, obj):
        return obj.user.username
    user_name.short_description = 'User'

    def dimensions(self, obj):
        if obj.image_width and obj.image_height:
            return f"{obj.image_width}×{obj.image_height}"
        return "N/A"
    dimensions.short_description = 'Dimensions'

    def file_size_display(self, obj):
        if obj.file_size_bytes:
            mb = obj.file_size_bytes / (1024 * 1024)
            if mb >= 1:
                return f"{mb:.2f} MB"
            else:
                kb = obj.file_size_bytes / 1024
                return f"{kb:.1f} KB"
        return "N/A"
    file_size_display.short_description = 'File Size'

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.get_thumbnail_url()
            )
        elif obj.file_path:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.get_full_url()
            )
        return "No image"
    thumbnail_preview.short_description = 'Preview'

    def thumbnail_display(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 8px;" />',
                obj.get_thumbnail_url()
            )
        elif obj.file_path:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 8px;" />',
                obj.get_full_url()
            )
        return "No thumbnail"
    thumbnail_display.short_description = 'Thumbnail'

    def image_display(self, obj):
        if obj.file_path:
            return format_html(
                '<img src="{}" style="max-width: 600px; border-radius: 8px;" />',
                obj.get_full_url()
            )
        return "No image"
    image_display.short_description = 'Full Image'


@admin.register(VideoHistory)
class VideoHistoryAdmin(admin.ModelAdmin):
    """Admin interface for video history (Session 44: Video Gallery)"""

    list_display = [
        'video_preview', 'video_id', 'video_type', 'model_used',
        'user_name', 'duration_display', 'ratio', 'status',
        'is_favorite', 'view_count', 'download_count', 'created_at'
    ]
    list_filter = [
        'video_type', 'model_used', 'status', 'is_favorite',
        'is_active', 'created_at'
    ]
    search_fields = ['video_id', 'prompt', 'user_notes', 'tags']
    readonly_fields = [
        'video_player', 'thumbnail_display', 'id', 'video_id',
        'video_url', 'thumbnail_url', 'duration', 'ratio',
        'view_count', 'download_count', 'generation_time_seconds',
        'generation_started', 'generation_completed', 'created_at', 'updated_at'
    ]

    fieldsets = (
        ('Video Information', {
            'fields': ('video_player', 'thumbnail_display', 'video_id', 'video_url', 'thumbnail_url', 'video_type', 'status')
        }),
        ('Generation Parameters', {
            'fields': ('prompt', 'model_used', 'parameters')
        }),
        ('Video Metadata', {
            'fields': ('duration', 'ratio', 'video_width', 'video_height', 'file_size_bytes')
        }),
        ('User Organization', {
            'fields': ('user', 'is_favorite', 'user_notes', 'tags')
        }),
        ('Source', {
            'fields': ('source_image',),
            'classes': ('collapse',)
        }),
        ('Usage Statistics', {
            'fields': ('view_count', 'download_count'),
            'classes': ('collapse',)
        }),
        ('Generation Timing', {
            'fields': ('generation_started', 'generation_completed', 'generation_time_seconds'),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('id', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def user_name(self, obj):
        return obj.user.username
    user_name.short_description = 'User'

    def duration_display(self, obj):
        if obj.duration:
            return f"{obj.duration}s"
        return "N/A"
    duration_display.short_description = 'Duration'

    def video_preview(self, obj):
        if obj.thumbnail_url:
            return format_html(
                '<img src="{}" style="width: 80px; height: 45px; object-fit: cover; border-radius: 4px;" />',
                obj.thumbnail_url
            )
        return "No thumbnail"
    video_preview.short_description = 'Preview'

    def thumbnail_display(self, obj):
        if obj.thumbnail_url:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 225px; border-radius: 8px;" />',
                obj.thumbnail_url
            )
        return "No thumbnail"
    thumbnail_display.short_description = 'Thumbnail'

    def video_player(self, obj):
        if obj.video_url:
            return format_html(
                '''
                <video controls style="max-width: 800px; border-radius: 8px;">
                    <source src="{}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                ''',
                obj.video_url
            )
        return "No video"
    video_player.short_description = 'Video Player'


@admin.register(MiniFigAsset)
class MiniFigAssetAdmin(admin.ModelAdmin):
    """Admin interface for MiniFig assets (Session 111: MiniFig Pipeline v1)"""

    list_display = [
        'preview_thumbnail', 'title', 'provider', 'status',
        'user_name', 'is_favorite', 'view_count', 'download_count', 'created_at'
    ]
    list_filter = [
        'provider', 'status', 'is_favorite', 'created_at'
    ]
    search_fields = ['title', 'user_notes', 'tags']
    readonly_fields = [
        'preview_display', 'id', 'three_d_file', 'preview_image_url',
        'view_count', 'download_count', 'created_at', 'updated_at'
    ]

    fieldsets = (
        ('MiniFig Information', {
            'fields': ('preview_display', 'title', 'provider', 'status', 'three_d_file', 'preview_image_url')
        }),
        ('Source', {
            'fields': ('source_pipeline_run', 'source_image_asset'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata', 'error_message'),
            'classes': ('collapse',)
        }),
        ('User Organization', {
            'fields': ('user', 'is_favorite', 'user_notes', 'tags')
        }),
        ('Usage Statistics', {
            'fields': ('view_count', 'download_count'),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def user_name(self, obj):
        return obj.user.username
    user_name.short_description = 'User'

    def preview_thumbnail(self, obj):
        """Small preview for list view"""
        if obj.preview_image_url and not obj.preview_image_url.startswith('data:'):
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px;" />',
                obj.preview_image_url
            )
        return "No preview"
    preview_thumbnail.short_description = 'Preview'

    def preview_display(self, obj):
        """Larger preview for detail view"""
        if obj.preview_image_url and not obj.preview_image_url.startswith('data:'):
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 400px; border-radius: 8px;" />',
                obj.preview_image_url
            )
        return "No preview available"
    preview_display.short_description = 'Preview Image'


# =============================================================================
# SESSION 60: PHASE C - PROJECT MANAGEMENT ADMIN
# =============================================================================

@admin.register(CreativeProject)
class CreativeProjectAdmin(admin.ModelAdmin):
    """Admin interface for creative projects (Session 60: Phase C.1.1)"""

    list_display = [
        'name', 'user_name', 'status', 'progress_display',
        'workflow_count', 'deadline', 'created_at'
    ]
    list_filter = ['status', 'category', 'is_shared', 'created_at']
    search_fields = ['name', 'description', 'goal', 'tags']
    readonly_fields = [
        'id', 'progress_percentage', 'is_overdue',
        'total_workflows', 'completed_workflows',
        'created_at', 'updated_at'
    ]

    fieldsets = (
        ('Project Information', {
            'fields': ('user', 'name', 'description', 'goal')
        }),
        ('Timeline', {
            'fields': ('deadline', 'status')
        }),
        ('Organization', {
            'fields': ('category', 'tags')
        }),
        ('Progress', {
            'fields': ('total_workflows', 'completed_workflows', 'progress_percentage', 'is_overdue'),
            'classes': ('collapse',)
        }),
        ('Collaboration', {
            'fields': ('is_shared',),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def user_name(self, obj):
        return obj.user.username
    user_name.short_description = 'User'

    def workflow_count(self, obj):
        return f"{obj.completed_workflows}/{obj.total_workflows}"
    workflow_count.short_description = 'Workflows'

    def progress_display(self, obj):
        percentage = obj.progress_percentage
        if percentage == 100:
            color = '#10b981'  # Green
        elif percentage >= 50:
            color = '#f59e0b'  # Amber
        else:
            color = '#ef4444'  # Red

        return format_html(
            '<div style="width: 100px; background: #e5e7eb; border-radius: 4px; overflow: hidden;">'
            '<div style="width: {}%; background: {}; height: 20px; line-height: 20px; text-align: center; color: white; font-size: 11px; font-weight: bold;">'
            '{}%'
            '</div>'
            '</div>',
            percentage, color, percentage
        )
    progress_display.short_description = 'Progress'


@admin.register(ProjectWorkflow)
class ProjectWorkflowAdmin(admin.ModelAdmin):
    """Admin interface for project-workflow links (Session 60: Phase C.1.1)"""

    list_display = [
        'project_name', 'workflow_name', 'order',
        'workflow_status', 'added_at'
    ]
    list_filter = ['project__status', 'workflow_history__status', 'added_at']
    search_fields = [
        'project__name', 'workflow_history__workflow_name',
        'notes'
    ]
    readonly_fields = ['added_at']

    fieldsets = (
        ('Links', {
            'fields': ('project', 'workflow_history')
        }),
        ('Organization', {
            'fields': ('order', 'notes')
        }),
        ('System', {
            'fields': ('added_at',),
            'classes': ('collapse',)
        })
    )

    def project_name(self, obj):
        return obj.project.name
    project_name.short_description = 'Project'

    def workflow_name(self, obj):
        return obj.workflow_history.workflow_name
    workflow_name.short_description = 'Workflow'

    def workflow_status(self, obj):
        status = obj.workflow_history.status
        status_colors = {
            'completed': '#10b981',  # Green
            'running': '#3b82f6',  # Blue
            'failed': '#ef4444',  # Red
            'pending': '#6b7280',  # Gray
            'cancelled': '#f59e0b',  # Amber
        }
        color = status_colors.get(status, '#6b7280')

        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
            color, status.upper()
        )
    workflow_status.short_description = 'Status'