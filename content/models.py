"""
Unified Content Management System Models

This module provides comprehensive content generation, document processing, 
RAG (Retrieval-Augmented Generation), and knowledge management capabilities
for the Unified Donkey Betz Platform.

Features:
- Multi-format document processing and storage
- Vector embeddings for semantic search
- Content generation templates and workflows
- Knowledge base with tagging and categorization
- Content analytics and usage tracking
- Cross-domain content integration (sports, betting, agents)
- Real-time content processing pipeline
"""

import uuid
import json
import hashlib
from decimal import Decimal
from enum import Enum
from pathlib import Path

from django.db import models
from django.db.models import F
from django.contrib.auth import get_user_model
# from django.contrib.postgres.fields import ArrayField  # Not available in SQLite
from django.core.files.storage import default_storage
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# Session 179: Import pgvector for native vector operations
try:
    from pgvector.django import VectorField, HnswIndex, IvfflatIndex
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False
    VectorField = None

from core.models import UnifiedBaseModel

User = get_user_model()


class DocumentType(models.TextChoices):
    """Document type classification"""
    TEXT = 'text', 'Plain Text'
    MARKDOWN = 'markdown', 'Markdown'
    HTML = 'html', 'HTML'
    PDF = 'pdf', 'PDF Document'
    DOCX = 'docx', 'Word Document'
    RTF = 'rtf', 'Rich Text Format'
    
    # Structured data
    JSON = 'json', 'JSON Data'
    CSV = 'csv', 'CSV Data'
    XML = 'xml', 'XML Data'
    YAML = 'yaml', 'YAML Data'
    
    # Code files
    PYTHON = 'python', 'Python Code'
    JAVASCRIPT = 'javascript', 'JavaScript Code'
    TYPESCRIPT = 'typescript', 'TypeScript Code'
    SQL = 'sql', 'SQL Code'
    
    # Media
    IMAGE = 'image', 'Image File'
    AUDIO = 'audio', 'Audio File'
    VIDEO = 'video', 'Video File'
    
    # Specialized content
    SPORTS_DATA = 'sports_data', 'Sports Analytics Data'
    BETTING_ANALYSIS = 'betting_analysis', 'Betting Analysis'
    AGENT_LOG = 'agent_log', 'Agent Execution Log'
    KNOWLEDGE_EXTRACT = 'knowledge_extract', 'Knowledge Base Extract'

    # Web content (Session 402)
    YOUTUBE = 'youtube', 'YouTube Video Transcript'
    URL = 'url', 'Web Page Content'


class ContentStatus(models.TextChoices):
    """Content processing status"""
    PENDING = 'pending', 'Pending Processing'
    PROCESSING = 'processing', 'Currently Processing'
    PROCESSED = 'processed', 'Successfully Processed'
    FAILED = 'failed', 'Processing Failed'
    ARCHIVED = 'archived', 'Archived'
    DELETED = 'deleted', 'Soft Deleted'


class ContentSource(models.TextChoices):
    """Source of content"""
    UPLOAD = 'upload', 'User Upload'
    GENERATED = 'generated', 'AI Generated'
    IMPORTED = 'imported', 'Imported from External System'
    SCRAPED = 'scraped', 'Web Scraped'
    API = 'api', 'API Integration'
    WORKFLOW = 'workflow', 'Workflow Generated'
    SPORTS_FEED = 'sports_feed', 'Sports Data Feed'
    BETTING_SYSTEM = 'betting_system', 'Betting Analysis System'


class MediaSourceType(models.TextChoices):
    """
    Session 451: Track how media content was created
    Used by ImageHistory, VideoHistory, AudioHistory
    """
    GENERATED = 'generated', 'AI Generated'
    UPLOADED = 'uploaded', 'User Uploaded'
    IMPORTED = 'imported', 'External Import'
    EDITED = 'edited', 'Edited Version'


class EmbeddingModel(models.TextChoices):
    """Vector embedding models"""
    OPENAI_SMALL = 'openai_text_embedding_3_small', 'OpenAI text-embedding-3-small'
    OPENAI_LARGE = 'openai_text_embedding_3_large', 'OpenAI text-embedding-3-large'
    OPENAI_ADA = 'openai_text_embedding_ada_002', 'OpenAI text-embedding-ada-002'
    SENTENCE_TRANSFORMER = 'sentence_transformer', 'Sentence Transformer'
    COHERE = 'cohere_embed_english', 'Cohere Embed English'
    LOCAL = 'local_model', 'Local Embedding Model'


class ContentTemplate(UnifiedBaseModel):
    """
    Reusable content generation templates
    """
    
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Unique template name"
    )
    
    display_name = models.CharField(
        max_length=250,
        help_text="Human-friendly display name"
    )
    
    description = models.TextField(
        help_text="Template description and usage instructions"
    )
    
    # Template configuration
    template_type = models.CharField(
        max_length=100,
        choices=[
            ('article', 'Article/Blog Post'),
            ('summary', 'Content Summary'),
            ('analysis', 'Analysis Report'),
            ('sports_report', 'Sports Analysis Report'),
            ('betting_guide', 'Betting Strategy Guide'),
            ('news_brief', 'News Brief'),
            ('social_post', 'Social Media Post'),
            ('email', 'Email Content'),
            ('documentation', 'Technical Documentation'),
            ('creative', 'Creative Writing'),
            ('translation', 'Translation Template'),
            ('qa', 'Question & Answer'),
        ],
        help_text="Type of content this template generates"
    )
    
    # Template structure
    system_prompt = models.TextField(
        help_text="System prompt that defines content generation behavior"
    )
    
    user_prompt_template = models.TextField(
        help_text="Template for user prompts with variable placeholders"
    )
    
    variables = models.JSONField(
        default=dict,
        help_text="Template variables and their configuration"
    )
    
    output_format = models.CharField(
        max_length=50,
        choices=[
            ('text', 'Plain Text'),
            ('markdown', 'Markdown'),
            ('html', 'HTML'),
            ('json', 'JSON Structure'),
            ('structured', 'Structured Data'),
        ],
        default='markdown',
        help_text="Expected output format"
    )
    
    # AI configuration
    llm_provider = models.CharField(
        max_length=50,
        choices=[
            ('openai', 'OpenAI'),
            ('anthropic', 'Anthropic'),
            ('google', 'Google AI'),
            ('local', 'Local Model'),
        ],
        default='openai'
    )
    
    llm_model = models.CharField(
        max_length=100,
        default='gpt-5-mini',
        help_text="Specific AI model to use"
    )
    
    generation_config = models.JSONField(
        default=dict,
        help_text="Model-specific generation parameters"
    )
    
    # Template metadata
    tags = models.JSONField(
        default=list,
        help_text="Tags for categorization and discovery"
    )
    
    category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Primary category"
    )
    
    # Usage statistics
    usage_count = models.PositiveIntegerField(
        default=0
    )
    
    avg_generation_time = models.FloatField(
        default=0.0,
        help_text="Average generation time in seconds"
    )
    
    success_rate = models.FloatField(
        default=1.0,
        help_text="Success rate for content generation"
    )
    
    avg_user_rating = models.FloatField(
        default=0.0,
        help_text="Average user satisfaction rating"
    )
    
    # Access control
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='content_templates'
    )
    
    is_public = models.BooleanField(
        default=True,
        help_text="Whether template is available to all users"
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether template has been verified for quality"
    )
    
    class Meta:
        verbose_name = "Content Template"
        verbose_name_plural = "Content Templates"
        ordering = ['-usage_count', 'name']
        indexes = [
            models.Index(fields=['template_type']),
            models.Index(fields=['category']),
            models.Index(fields=['is_public', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.display_name} ({self.template_type})"
    
    def render_prompt(self, **kwargs):
        """Render the user prompt template with provided variables"""
        import re
        
        prompt = self.user_prompt_template
        
        # Replace variables in the template
        for var_name, var_config in self.variables.items():
            if var_name in kwargs:
                value = kwargs[var_name]
                prompt = re.sub(f"{{{{ *{var_name} *}}}}", str(value), prompt)
            elif var_config.get('required', False):
                raise ValueError(f"Required variable '{var_name}' not provided")
        
        return prompt
    
    def update_stats(self, generation_time=None, success=True, rating=None):
        """Update template usage statistics using atomic F() expressions to prevent race conditions"""
        # Phase 2 P1: Use atomic update for usage_count to prevent race conditions
        PromptTemplate.objects.filter(pk=self.pk).update(usage_count=F('usage_count') + 1)

        # Refresh from DB to get the new count for calculations
        self.refresh_from_db(fields=['usage_count'])

        update_fields = []

        if generation_time is not None:
            total_time = self.avg_generation_time * (self.usage_count - 1) + generation_time
            self.avg_generation_time = total_time / self.usage_count
            update_fields.append('avg_generation_time')

        if success is not None:
            total_success = self.success_rate * (self.usage_count - 1) + (1 if success else 0)
            self.success_rate = total_success / self.usage_count
            update_fields.append('success_rate')

        if rating is not None:
            total_rating = self.avg_user_rating * (self.usage_count - 1) + rating
            self.avg_user_rating = total_rating / self.usage_count
            update_fields.append('avg_user_rating')

        if update_fields:
            self.save(update_fields=update_fields)


class Document(UnifiedBaseModel):
    """
    Comprehensive document storage and processing
    """
    
    # Basic identification
    title = models.CharField(
        max_length=500,
        help_text="Document title"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Optional document description"
    )
    
    document_type = models.CharField(
        max_length=50,
        choices=DocumentType.choices,
        help_text="Type of document"
    )
    
    # File information
    file_path = models.CharField(
        max_length=1000,
        blank=True,
        help_text="Path to the stored file"
    )
    
    original_filename = models.CharField(
        max_length=500,
        blank=True,
        help_text="Original filename when uploaded"
    )
    
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )
    
    mime_type = models.CharField(
        max_length=200,
        blank=True,
        help_text="MIME type of the document"
    )
    
    # Content and processing
    raw_content = models.TextField(
        blank=True,
        help_text="Raw extracted text content"
    )
    
    processed_content = models.TextField(
        blank=True,
        help_text="Cleaned and processed text content"
    )
    
    content_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="SHA-256 hash of content for deduplication"
    )
    
    # Status and processing
    status = models.CharField(
        max_length=20,
        choices=ContentStatus.choices,
        default=ContentStatus.PENDING
    )
    
    source = models.CharField(
        max_length=50,
        choices=ContentSource.choices,
        default=ContentSource.UPLOAD
    )
    
    processing_log = models.JSONField(
        default=list,
        help_text="Log of processing steps and results"
    )
    
    error_message = models.TextField(
        blank=True,
        help_text="Error message if processing failed"
    )
    
    # Content analysis
    language = models.CharField(
        max_length=10,
        blank=True,
        help_text="Detected language code (e.g., 'en', 'es')"
    )
    
    word_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of words in the document"
    )
    
    readability_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Automated readability assessment"
    )
    
    # Metadata extraction
    extracted_metadata = models.JSONField(
        default=dict,
        help_text="Metadata extracted from document"
    )
    
    key_phrases = models.JSONField(
        default=list,
        help_text="Extracted key phrases and topics"
    )
    
    entities = models.JSONField(
        default=list,
        help_text="Named entities found in the document"
    )
    
    # Organization
    tags = models.JSONField(
        default=list,
        help_text="User-defined tags"
    )
    
    category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Document category"
    )
    
    collection = models.CharField(
        max_length=200,
        blank=True,
        help_text="Collection or folder this document belongs to"
    )
    
    # Relationships
    parent_document = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='child_documents',
        help_text="Parent document if this is a section/chapter"
    )
    
    related_documents = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=True,
        help_text="Related documents"
    )
    
    # Access control
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    
    is_public = models.BooleanField(
        default=False,
        help_text="Whether document is publicly accessible"
    )
    
    allowed_users = models.ManyToManyField(
        User,
        blank=True,
        related_name='accessible_documents',
        help_text="Users with explicit access to this document"
    )
    
    # Usage tracking
    view_count = models.PositiveIntegerField(
        default=0
    )
    
    download_count = models.PositiveIntegerField(
        default=0
    )
    
    last_accessed = models.DateTimeField(
        null=True,
        blank=True
    )
    
    # Cross-domain integration
    source_system = models.CharField(
        max_length=100,
        blank=True,
        choices=[
            ('sports', 'Sports Analytics'),
            ('agents', 'Agent System'),
            ('betting', 'Betting Analysis'),
            ('manual', 'Manual Upload'),
            ('api', 'API Integration'),
        ],
        help_text="System that created this document"
    )
    
    source_reference = models.CharField(
        max_length=500,
        blank=True,
        help_text="Reference ID in source system"
    )

    # Session 402: URL source for web/YouTube documents
    source_url = models.URLField(
        max_length=2000,
        blank=True,
        help_text="Original URL for web pages and YouTube videos"
    )
    
    cross_references = models.JSONField(
        default=dict,
        help_text="References to related objects in other systems"
    )

    # Session 949: Risk-Aware RAG Fields
    # These fields enable defensive retrieval that prioritizes dangerous/critical docs
    RISK_LEVEL_CHOICES = [
        ('critical', 'Critical - Must always retrieve'),
        ('high', 'High - Boost in retrieval'),
        ('medium', 'Medium - Standard retrieval'),
        ('low', 'Low - May be skipped under budget pressure'),
    ]

    DOCUMENT_CLASS_CHOICES = [
        ('reference', 'Reference Documentation'),
        ('postmortem', 'Incident Postmortem'),
        ('incident_report', 'Incident Report'),
        ('constraint', 'Constraint/Policy Document'),
        ('security', 'Security Advisory'),
        ('architecture', 'Architecture Decision'),
        ('runbook', 'Operational Runbook'),
        ('changelog', 'Changelog/Release Notes'),
    ]

    is_critical = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Always include in retrieval regardless of similarity score"
    )

    risk_level = models.CharField(
        max_length=20,
        choices=RISK_LEVEL_CHOICES,
        default='medium',
        db_index=True,
        help_text="Risk level for retrieval prioritization"
    )

    document_class = models.CharField(
        max_length=30,
        choices=DOCUMENT_CLASS_CHOICES,
        default='reference',
        db_index=True,
        help_text="Classification for retrieval channel routing"
    )

    incident_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date of incident (for postmortems/incident reports)"
    )

    retrieval_boost = models.FloatField(
        default=1.0,
        help_text="Multiplier for retrieval score (1.0 = normal, 2.0 = double priority)"
    )

    # Session G2: Data sensitivity classification
    DATA_SENSITIVITY_CHOICES = [
        ('public', 'Public'),
        ('internal', 'Internal'),
        ('confidential', 'Confidential'),
        ('restricted', 'Restricted'),
    ]
    data_sensitivity = models.CharField(
        max_length=20,
        choices=DATA_SENSITIVITY_CHOICES,
        default='internal',
        db_index=True,
        help_text="Data sensitivity level for retention and redaction policies"
    )
    is_pinned = models.BooleanField(
        default=False,
        help_text="Pinned documents override retention policies (never auto-deleted)"
    )

    # Promotion gate — external-origin docs start as 'staged', must be promoted before embedding/retrieval
    PROMOTION_STATUS_CHOICES = [
        ('promoted', 'Promoted'),
        ('staged', 'Staged'),
        ('blocked', 'Blocked'),
    ]
    promotion_status = models.CharField(
        max_length=10,
        choices=PROMOTION_STATUS_CHOICES,
        default='promoted',
        db_index=True,
        help_text="Promotion gate: staged docs are not embedded or retrievable until promoted"
    )

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document_type']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['owner']),
            models.Index(fields=['content_hash']),
            models.Index(fields=['-created_at']),
            # Session 949: Risk-Aware RAG indexes
            models.Index(fields=['is_critical', 'risk_level']),
            models.Index(fields=['document_class']),
            models.Index(fields=['document_class', 'risk_level']),
            # Session G2: Retention query indexes
            models.Index(fields=['data_sensitivity', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.document_type})"
    
    def save(self, *args, **kwargs):
        # Generate content hash for deduplication
        if self.processed_content and not self.content_hash:
            self.content_hash = hashlib.sha256(
                self.processed_content.encode('utf-8')
            ).hexdigest()

        # Session G2: Auto-classify data sensitivity on first save only
        # Never overwrite explicit manual changes (update_fields targeting data_sensitivity)
        update_fields = kwargs.get('update_fields')
        is_new = self._state.adding
        if is_new and self.data_sensitivity == 'internal':
            source = getattr(self, 'source', '')
            doc_type = getattr(self, 'document_type', '')
            if doc_type == 'youtube' or source == 'scraped':
                self.data_sensitivity = 'public'
            elif source in ('api', 'imported') or doc_type in ('email', 'crm'):
                self.data_sensitivity = 'confidential'

        # Auto-stage external-origin documents on first save
        if is_new and self.promotion_status == 'promoted':
            meta = self.extracted_metadata or {}
            if meta.get('auto_research') or source == 'scraped':
                self.promotion_status = 'staged'

        super().save(*args, **kwargs)
    
    def get_content(self):
        """Get the best available content representation"""
        return self.processed_content or self.raw_content or ""
    
    def add_processing_log(self, step, status, details=None):
        """Add entry to processing log"""
        log_entry = {
            'step': step,
            'status': status,
            'timestamp': timezone.now().isoformat(),
            'details': details or {}
        }
        self.processing_log.append(log_entry)
        self.save(update_fields=['processing_log'])
    
    def increment_view_count(self):
        """Increment view count and update last accessed using atomic F() expression"""
        # Phase 2 P1: Use atomic update to prevent race conditions
        Document.objects.filter(pk=self.pk).update(
            view_count=F('view_count') + 1,
            last_accessed=timezone.now()
        )
        self.refresh_from_db(fields=['view_count', 'last_accessed'])


class DocumentEmbedding(UnifiedBaseModel):
    """
    Vector embeddings for semantic search and RAG

    Session 179: Upgraded to use native pgvector VectorField for efficient
    similarity search operations directly in PostgreSQL.
    """

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='embeddings'
    )

    # Embedding configuration
    embedding_model = models.CharField(
        max_length=100,
        choices=EmbeddingModel.choices,
        help_text="Model used to generate embeddings"
    )

    # Content segmentation
    chunk_index = models.PositiveIntegerField(
        help_text="Index of this chunk within the document"
    )

    chunk_text = models.TextField(
        help_text="Text content of this chunk"
    )

    chunk_size = models.PositiveIntegerField(
        help_text="Size of text chunk in characters"
    )

    overlap_size = models.PositiveIntegerField(
        default=0,
        help_text="Overlap with adjacent chunks in characters"
    )

    # Session 179: Vector embedding storage
    # Session 730: Migrated to pgvector VectorField for native PostgreSQL vector ops
    embedding_vector = VectorField(
        dimensions=1536,
        null=True,
        blank=True,
        help_text="Vector embedding for semantic search (pgvector)"
    ) if HAS_PGVECTOR else models.JSONField(
        null=True,
        blank=True,
        help_text="Vector embedding (JSON fallback)"
    )

    embedding_dimension = models.PositiveIntegerField(
        help_text="Dimension of the embedding vector"
    )

    # Context and metadata
    context_before = models.TextField(
        blank=True,
        help_text="Context text before this chunk"
    )

    context_after = models.TextField(
        blank=True,
        help_text="Context text after this chunk"
    )

    metadata = models.JSONField(
        default=dict,
        help_text="Additional metadata for this chunk"
    )

    # Processing info
    processing_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Time taken to generate embedding in milliseconds"
    )

    embedding_cost = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        default=Decimal('0.000000'),
        help_text="Cost to generate this embedding"
    )

    # Provenance tracking — where did this chunk originate?
    SOURCE_TYPE_CHOICES = [
        ('internal', 'Internal'),
        ('web', 'Web'),
        ('spider', 'Spider'),
        ('user_upload', 'User Upload'),
        ('api', 'API'),
        ('unknown', 'Unknown'),
    ]
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPE_CHOICES,
        default='unknown',
        db_index=True,
        help_text="Origin of the source document (internal/web/spider/user_upload/api/unknown)"
    )

    INGESTED_VIA_CHOICES = [
        ('auto_research', 'Auto Research'),
        ('manual', 'Manual Upload'),
        ('spider_pipeline', 'Spider Pipeline'),
        ('sync_docs', 'Docs Index Sync'),
        ('backfill', 'Backfill'),
        ('unknown', 'Unknown'),
    ]
    ingested_via = models.CharField(
        max_length=20,
        choices=INGESTED_VIA_CHOICES,
        default='unknown',
        help_text="Pipeline that created this embedding"
    )

    class Meta:
        verbose_name = "Document Embedding"
        verbose_name_plural = "Document Embeddings"
        ordering = ['document', 'chunk_index']
        indexes = [
            models.Index(fields=['document', 'chunk_index']),
            models.Index(fields=['embedding_model']),
            models.Index(fields=['source_type']),
        ] + ([
            HnswIndex(name='docembed_vector_hnsw_idx', fields=['embedding_vector'],
                      m=16, ef_construction=64, opclasses=['vector_cosine_ops']),
        ] if HAS_PGVECTOR else [])
        unique_together = ['document', 'chunk_index', 'embedding_model']

    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"

    def similarity_search_preview(self, max_length=200):
        """Get preview text for similarity search results"""
        text = self.chunk_text
        if len(text) > max_length:
            text = text[:max_length] + "..."
        return text

    def get_vector_as_list(self):
        """Get embedding vector as Python list (works with both VectorField and JSONField)."""
        if isinstance(self.embedding_vector, list):
            return self.embedding_vector
        # pgvector returns a numpy-like object
        return list(self.embedding_vector)

    @classmethod
    def cosine_similarity_search(cls, query_vector, limit=10, min_similarity=0.7):
        """
        Perform native pgvector cosine similarity search.

        Session 179: Uses PostgreSQL's native vector operations for fast search.

        Args:
            query_vector: The query embedding as a list
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold (0-1)

        Returns:
            QuerySet with annotated similarity scores
        """
        if not HAS_PGVECTOR:
            raise NotImplementedError("Native vector search requires pgvector. Use Python-based search instead.")

        from pgvector.django import CosineDistance

        # Calculate cosine distance (1 - similarity) and filter/order
        # Exclude orphan chunks whose parent Document has no file_path
        # (e.g. "Agent Activity Knowledge Base" entries that pollute results)
        return cls.objects.filter(
            document__file_path__isnull=False,
        ).exclude(
            document__file_path='',
        ).annotate(
            distance=CosineDistance('embedding_vector', query_vector)
        ).filter(
            distance__lt=(1 - min_similarity)  # Convert similarity to distance threshold
        ).order_by('distance')[:limit]

    @classmethod
    def l2_distance_search(cls, query_vector, limit=10, max_distance=None):
        """
        Perform native pgvector L2 (Euclidean) distance search.

        Args:
            query_vector: The query embedding as a list
            limit: Maximum number of results
            max_distance: Maximum L2 distance threshold

        Returns:
            QuerySet with annotated distance scores
        """
        if not HAS_PGVECTOR:
            raise NotImplementedError("Native vector search requires pgvector.")

        from pgvector.django import L2Distance

        qs = cls.objects.filter(
            document__file_path__isnull=False,
        ).exclude(
            document__file_path='',
        ).annotate(
            distance=L2Distance('embedding_vector', query_vector)
        ).order_by('distance')

        if max_distance is not None:
            qs = qs.filter(distance__lt=max_distance)

        return qs[:limit]


class KnowledgeBase(UnifiedBaseModel):
    """
    Structured knowledge base with semantic organization
    """
    
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Knowledge base name"
    )
    
    description = models.TextField(
        help_text="Description of the knowledge base"
    )
    
    # Configuration
    embedding_model = models.CharField(
        max_length=100,
        choices=EmbeddingModel.choices,
        default=EmbeddingModel.OPENAI_SMALL,
        help_text="Default embedding model for this knowledge base"
    )
    
    chunk_size = models.PositiveIntegerField(
        default=1000,
        help_text="Default chunk size for document processing"
    )
    
    chunk_overlap = models.PositiveIntegerField(
        default=200,
        help_text="Default overlap between chunks"
    )
    
    # Organization
    categories = models.JSONField(
        default=list,
        help_text="Available categories for documents in this KB"
    )
    
    tags = models.JSONField(
        default=list,
        help_text="Available tags for documents in this KB"
    )
    
    # Statistics
    document_count = models.PositiveIntegerField(
        default=0
    )
    
    total_chunks = models.PositiveIntegerField(
        default=0
    )
    
    total_tokens = models.PositiveIntegerField(
        default=0
    )
    
    last_indexed = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time the knowledge base was fully indexed"
    )
    
    # Access control
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='knowledge_bases'
    )
    
    contributors = models.ManyToManyField(
        User,
        blank=True,
        related_name='contributed_knowledge_bases',
        help_text="Users who can add/edit documents in this KB"
    )
    
    is_public = models.BooleanField(
        default=False,
        help_text="Whether this knowledge base is publicly searchable"
    )
    
    # Cross-domain specialization
    domain = models.CharField(
        max_length=100,
        choices=[
            ('general', 'General Knowledge'),
            ('sports', 'Sports Analytics'),
            ('betting', 'Betting & Gambling'),
            ('agents', 'AI Agents & Automation'),
            ('technical', 'Technical Documentation'),
            ('business', 'Business Intelligence'),
        ],
        default='general',
        help_text="Domain specialization of this knowledge base"
    )
    
    integration_config = models.JSONField(
        default=dict,
        help_text="Configuration for cross-system integration"
    )
    
    class Meta:
        verbose_name = "Knowledge Base"
        verbose_name_plural = "Knowledge Bases"
        ordering = ['name']
        indexes = [
            models.Index(fields=['domain']),
            models.Index(fields=['is_public', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.domain})"
    
    def get_documents(self):
        """Get all documents in this knowledge base"""
        return Document.objects.filter(
            collection=self.name,
            is_active=True
        )
    
    def update_statistics(self):
        """Update knowledge base statistics"""
        documents = self.get_documents()
        self.document_count = documents.count()
        
        embeddings = DocumentEmbedding.objects.filter(
            document__in=documents
        )
        self.total_chunks = embeddings.count()
        
        # Calculate total tokens (approximate)
        total_chars = documents.aggregate(
            total=models.Sum('word_count')
        )['total'] or 0
        self.total_tokens = int(total_chars * 0.75)  # Rough token estimate
        
        self.save(update_fields=['document_count', 'total_chunks', 'total_tokens'])


class ContentGeneration(UnifiedBaseModel):
    """
    Content generation requests and results
    """
    
    # Request information
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='content_generations'
    )
    
    template = models.ForeignKey(
        ContentTemplate,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='generations'
    )
    
    # Generation parameters
    prompt = models.TextField(
        help_text="The prompt used for content generation"
    )
    
    system_prompt = models.TextField(
        blank=True,
        help_text="System prompt for this generation"
    )
    
    generation_config = models.JSONField(
        default=dict,
        help_text="AI model configuration used"
    )
    
    # Context and RAG
    context_documents = models.ManyToManyField(
        Document,
        blank=True,
        related_name='content_generations',
        help_text="Documents used as context for RAG"
    )
    
    knowledge_base = models.ForeignKey(
        KnowledgeBase,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='generations'
    )
    
    rag_context = models.TextField(
        blank=True,
        help_text="Retrieved context for RAG generation"
    )
    
    # Generation results
    generated_content = models.TextField(
        blank=True,
        help_text="The generated content"
    )
    
    status = models.CharField(
        max_length=20,
        choices=ContentStatus.choices,
        default=ContentStatus.PENDING
    )
    
    # Performance metrics
    generation_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Time taken to generate content in milliseconds"
    )
    
    token_usage = models.JSONField(
        default=dict,
        help_text="Token usage statistics"
    )
    
    generation_cost = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        default=Decimal('0.000000'),
        help_text="Cost of content generation"
    )
    
    # Quality assessment
    quality_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Automated quality assessment (0-1)"
    )
    
    user_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="User satisfaction rating (1-5)"
    )
    
    user_feedback = models.TextField(
        blank=True,
        help_text="User feedback on generated content"
    )
    
    # Error handling
    error_message = models.TextField(
        blank=True,
        help_text="Error message if generation failed"
    )
    
    retry_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of retry attempts"
    )
    
    # Integration
    source_system = models.CharField(
        max_length=100,
        blank=True,
        choices=[
            ('web', 'Web Interface'),
            ('api', 'API Request'),
            ('workflow', 'Workflow System'),
            ('agent', 'Agent Generated'),
            ('sports', 'Sports Analysis'),
            ('betting', 'Betting System'),
        ],
        help_text="System that initiated this generation"
    )
    
    workflow_context = models.JSONField(
        default=dict,
        help_text="Context from workflow or orchestration system"
    )
    
    # Output management
    output_document = models.OneToOneField(
        Document,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='generation_source',
        help_text="Document created from this generation"
    )
    
    export_formats = models.JSONField(
        default=list,
        help_text="Formats this content has been exported to"
    )
    
    class Meta:
        verbose_name = "Content Generation"
        verbose_name_plural = "Content Generations"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['template']),
            models.Index(fields=['status']),
            models.Index(fields=['source_system']),
        ]
    
    def __str__(self):
        return f"Generation {self.id} - {self.status}"
    
    def save(self, *args, **kwargs):
        """
        Save and trigger learning loops

        LEARNING LOOP: Update template performance based on user ratings
        """
        super().save(*args, **kwargs)

        # Trigger learning if user has rated the content
        if self.user_rating and self.template:
            self._update_template_learning()

    def _update_template_learning(self):
        """
        LEARNING LOOP: Update template stats and trigger improvement if needed
        """
        try:
            # Update template statistics
            self.template.update_stats(
                generation_time=self.generation_time_ms / 1000 if self.generation_time_ms else 0,
                success=(self.user_rating >= 4),
                rating=self.user_rating
            )

            # Check if template needs improvement
            if hasattr(self.template, 'avg_user_rating'):
                # If consistently low-rated with enough samples, flag for improvement
                if (self.template.avg_user_rating < 3.0 and
                    self.template.usage_count > 10):
                    self._request_template_optimization()

        except Exception as e:
            import logging
            logging.error(f"Failed to update template learning: {e}")

    def _request_template_optimization(self):
        """
        LEARNING LOOP: Queue template for AI-powered improvement
        """
        try:
            # Get recent low-rated generations
            low_rated = ContentGeneration.objects.filter(
                template=self.template,
                user_rating__lt=3
            ).order_by('-created_at')[:5]

            if low_rated.count() == 0:
                return

            # Analyze common issues from feedback
            feedback_list = [g.user_feedback for g in low_rated if g.user_feedback]

            if feedback_list:
                # Create improvement task in metadata
                if not self.template.metadata:
                    self.template.metadata = {}

                self.template.metadata['needs_improvement'] = True
                self.template.metadata['low_ratings_count'] = low_rated.count()
                self.template.metadata['recent_feedback'] = feedback_list[:3]
                self.template.metadata['improvement_requested_at'] = str(timezone.now())

                self.template.save()

                import logging
                logging.warning(
                    f"🔧 Template improvement requested: {self.template.display_name} "
                    f"(avg rating: {self.template.avg_user_rating:.1f})"
                )

        except Exception as e:
            import logging
            logging.error(f"Failed to request template optimization: {e}")

    def create_document(self):
        """Create a Document from the generated content"""
        if not self.generated_content or self.output_document:
            return self.output_document

        # Determine document type based on template
        doc_type = DocumentType.MARKDOWN
        if self.template:
            if self.template.output_format == 'html':
                doc_type = DocumentType.HTML
            elif self.template.output_format == 'json':
                doc_type = DocumentType.JSON
            elif self.template.output_format == 'text':
                doc_type = DocumentType.TEXT

        # Create document
        document = Document.objects.create(
            title=f"Generated: {self.template.display_name if self.template else 'Custom'}",
            document_type=doc_type,
            processed_content=self.generated_content,
            status=ContentStatus.PROCESSED,
            source=ContentSource.GENERATED,
            owner=self.user,
            source_system='content_generation',
            source_reference=str(self.id),
            metadata={
                'generation_id': str(self.id),
                'template_id': str(self.template.id) if self.template else None,
                'generation_config': self.generation_config,
                'token_usage': self.token_usage,
            }
        )

        self.output_document = document
        self.save(update_fields=['output_document'])

        return document


class ContentWorkflow(UnifiedBaseModel):
    """
    Multi-step content generation workflows
    """
    
    name = models.CharField(
        max_length=200,
        help_text="Workflow name"
    )
    
    description = models.TextField(
        help_text="Workflow description and purpose"
    )
    
    # Workflow definition
    workflow_steps = models.JSONField(
        help_text="Ordered list of workflow steps with configurations"
    )
    
    # Default configuration
    default_config = models.JSONField(
        default=dict,
        help_text="Default configuration for workflow execution"
    )
    
    # Templates and dependencies
    required_templates = models.ManyToManyField(
        ContentTemplate,
        blank=True,
        related_name='workflows',
        help_text="Templates required for this workflow"
    )
    
    required_knowledge_bases = models.ManyToManyField(
        KnowledgeBase,
        blank=True,
        related_name='workflows',
        help_text="Knowledge bases required for this workflow"
    )
    
    # Usage statistics
    execution_count = models.PositiveIntegerField(
        default=0
    )
    
    success_rate = models.FloatField(
        default=1.0
    )
    
    avg_execution_time = models.FloatField(
        default=0.0,
        help_text="Average execution time in seconds"
    )
    
    # Access control
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='content_workflows'
    )
    
    is_public = models.BooleanField(
        default=True
    )
    
    # Cross-domain integration
    domain = models.CharField(
        max_length=100,
        choices=[
            ('general', 'General Content'),
            ('sports', 'Sports Content'),
            ('betting', 'Betting Analysis'),
            ('news', 'News and Updates'),
            ('social', 'Social Media'),
            ('documentation', 'Documentation'),
            ('marketing', 'Marketing Content'),
        ],
        default='general'
    )
    
    integration_points = models.JSONField(
        default=dict,
        help_text="Integration points with other platform systems"
    )
    
    class Meta:
        verbose_name = "Content Workflow"
        verbose_name_plural = "Content Workflows"
        ordering = ['name']
        indexes = [
            models.Index(fields=['domain']),
            models.Index(fields=['is_public', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.domain})"


class WorkflowExecution(UnifiedBaseModel):
    """
    Individual workflow execution instances
    """
    
    workflow = models.ForeignKey(
        ContentWorkflow,
        on_delete=models.CASCADE,
        related_name='executions'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workflow_executions'
    )
    
    # Execution parameters
    input_data = models.JSONField(
        default=dict,
        help_text="Input data for workflow execution"
    )
    
    execution_config = models.JSONField(
        default=dict,
        help_text="Configuration overrides for this execution"
    )
    
    # Status and progress
    status = models.CharField(
        max_length=20,
        choices=ContentStatus.choices,
        default=ContentStatus.PENDING
    )
    
    current_step = models.PositiveIntegerField(
        default=0,
        help_text="Currently executing step index"
    )
    
    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Step results
    step_results = models.JSONField(
        default=list,
        help_text="Results from each completed step"
    )
    
    final_output = models.JSONField(
        null=True,
        blank=True,
        help_text="Final workflow output"
    )
    
    # Performance
    started_at = models.DateTimeField(
        null=True,
        blank=True
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )
    
    execution_time_seconds = models.FloatField(
        null=True,
        blank=True
    )
    
    # Generated content
    generated_documents = models.ManyToManyField(
        Document,
        blank=True,
        related_name='workflow_executions',
        help_text="Documents generated by this workflow"
    )
    
    generated_content = models.ManyToManyField(
        ContentGeneration,
        blank=True,
        related_name='workflow_executions',
        help_text="Content generations from this workflow"
    )
    
    # Error handling
    error_message = models.TextField(
        blank=True
    )
    
    error_step = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Step where error occurred"
    )
    
    # Integration
    agent_execution = models.CharField(
        max_length=200,
        blank=True,
        help_text="Agent execution ID if triggered by agent"
    )
    
    websocket_channel = models.CharField(
        max_length=255,
        blank=True,
        help_text="WebSocket channel for real-time updates"
    )
    
    class Meta:
        verbose_name = "Workflow Execution"
        verbose_name_plural = "Workflow Executions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workflow', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.workflow.name} execution {self.id} - {self.status}"


class ContentAnalytics(UnifiedBaseModel):
    """
    Analytics and metrics for content system usage
    """
    
    # Metric identification
    metric_name = models.CharField(
        max_length=100,
        help_text="Name of the metric"
    )
    
    metric_type = models.CharField(
        max_length=50,
        choices=[
            ('counter', 'Counter'),
            ('gauge', 'Gauge'),
            ('histogram', 'Histogram'),
            ('rate', 'Rate'),
        ]
    )
    
    # Metric value and context
    metric_value = models.FloatField(
        help_text="Numeric value of the metric"
    )
    
    context = models.JSONField(
        default=dict,
        help_text="Additional context and dimensions"
    )
    
    # Categorization
    subsystem = models.CharField(
        max_length=100,
        choices=[
            ('documents', 'Document Processing'),
            ('generation', 'Content Generation'),
            ('embeddings', 'Vector Embeddings'),
            ('knowledge_base', 'Knowledge Base'),
            ('workflows', 'Workflow Execution'),
            ('templates', 'Template Usage'),
            ('search', 'Semantic Search'),
            ('system', 'System Performance'),
        ]
    )
    
    # Time series data
    timestamp = models.DateTimeField(
        default=timezone.now
    )
    
    time_period = models.CharField(
        max_length=20,
        choices=[
            ('instant', 'Instant'),
            ('minute', 'Per Minute'),
            ('hour', 'Per Hour'),
            ('day', 'Per Day'),
            ('week', 'Per Week'),
            ('month', 'Per Month'),
        ],
        default='instant'
    )
    
    # Associated objects
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='content_analytics'
    )
    
    document = models.ForeignKey(
        Document,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    
    template = models.ForeignKey(
        ContentTemplate,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    
    knowledge_base = models.ForeignKey(
        KnowledgeBase,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    
    class Meta:
        verbose_name = "Content Analytics"
        verbose_name_plural = "Content Analytics"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric_name', '-timestamp']),
            models.Index(fields=['subsystem', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.subsystem}.{self.metric_name}: {self.metric_value}"
    
    @classmethod
    def record_metric(cls, name, value, metric_type='gauge', subsystem='system', 
                     context=None, user=None, document=None, template=None, 
                     knowledge_base=None):
        """Record a new metric value"""
        return cls.objects.create(
            metric_name=name,
            metric_value=value,
            metric_type=metric_type,
            subsystem=subsystem,
            context=context or {},
            user=user,
            document=document,
            template=template,
            knowledge_base=knowledge_base
        )


class Feedback(UnifiedBaseModel):
    """
    User feedback on generated content
    """
    
    # Content identification
    content_type = models.CharField(
        max_length=50,
        choices=[
            ('text', 'Text Content'),
            ('image', 'Image Content'),
            ('video', 'Video Content'),
            ('blog', 'Blog Post'),
            ('social', 'Social Media Post'),
            ('ebook', 'eBook Content'),
            ('voice', 'Voice Content'),
            ('research', 'Research Content'),
        ],
        help_text="Type of content being rated"
    )
    
    content_id = models.PositiveIntegerField(
        help_text="ID of the content item being rated"
    )
    
    # User and rating
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='feedback_given'
    )
    
    overall_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Overall rating from 1-5 stars"
    )
    
    # Detailed ratings (optional)
    quality_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Quality rating from 1-5 stars"
    )
    
    accuracy_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Accuracy rating from 1-5 stars"
    )
    
    usefulness_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Usefulness rating from 1-5 stars"
    )
    
    # Feedback details
    feedback_type = models.CharField(
        max_length=50,
        choices=[
            ('quality', 'Quality Issue'),
            ('accuracy', 'Accuracy Issue'),
            ('usefulness', 'Usefulness Issue'),
            ('general', 'General Feedback'),
            ('suggestion', 'Improvement Suggestion'),
        ],
        default='general'
    )
    
    comments = models.TextField(
        blank=True,
        help_text="Written feedback comments"
    )
    
    suggestions = models.TextField(
        blank=True,
        help_text="Suggestions for improvement"
    )
    
    # Quick answers
    would_recommend = models.BooleanField(
        null=True,
        blank=True,
        help_text="Would recommend this content to others"
    )
    
    met_expectations = models.BooleanField(
        null=True,
        blank=True,
        help_text="Content met user expectations"
    )
    
    saved_time = models.BooleanField(
        null=True,
        blank=True,
        help_text="Content saved user time"
    )
    
    # Metadata
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags associated with this feedback"
    )
    
    generation_params = models.JSONField(
        default=dict,
        blank=True,
        help_text="Parameters used to generate the rated content"
    )
    
    # Admin response
    admin_response = models.TextField(
        blank=True,
        help_text="Admin response to user feedback"
    )
    
    admin_response_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When admin responded to feedback"
    )
    
    class Meta:
        verbose_name = "User Feedback"
        verbose_name_plural = "User Feedback"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'content_id']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['overall_rating']),
            models.Index(fields=['feedback_type']),
        ]
        # Ensure one feedback per user per content item
        unique_together = ['user', 'content_type', 'content_id']
    
    def __str__(self):
        return f"{self.user.username} - {self.content_type} {self.content_id} - {self.overall_rating}★"
    
    @property
    def is_positive(self):
        """Check if feedback is positive (4-5 stars)"""
        return self.overall_rating >= 4
    
    @property
    def is_negative(self):
        """Check if feedback is negative (1-2 stars)"""
        return self.overall_rating <= 2
    
    @property
    def is_neutral(self):
        """Check if feedback is neutral (3 stars)"""
        return self.overall_rating == 3

class ImageHistory(UnifiedBaseModel):
    """
    Track all AI-generated and edited images for user gallery
    """

    # User identification
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='image_history',
        help_text="User who created/edited this image"
    )

    # Session 63: Phase C.4++ - Link images to projects for client management
    project = models.ForeignKey(
        'core.PartnershipProject',  # Session 324: Unified from CreativeProject
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='project_images',
        help_text="Optional project this image belongs to"
    )

    # Workspace linkage — connects images to project workspaces
    workspace = models.ForeignKey(
        'core.ProjectWorkspace',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='images',
        db_index=True,
        help_text="Workspace this image belongs to"
    )

    # Session 96: Weekend Project - Link images to AI conversation sessions
    session = models.ForeignKey(
        'AISession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='session_images',
        help_text="AI session that created this image"
    )

    # Session 120: Track which agent created this image
    agent = models.ForeignKey(
        'agents.UnifiedAgentTemplate',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='generated_images',
        help_text="Agent that generated this image (if created by agent)"
    )

    # Image identification
    filename = models.CharField(
        max_length=255,
        help_text="Stored filename"
    )
    
    file_path = models.TextField(
        help_text="Full path to image file in storage (can be data URI)"
    )
    
    thumbnail = models.CharField(
        max_length=500,
        blank=True,
        help_text="Path to thumbnail version"
    )
    
    # Image classification
    image_type = models.CharField(
        max_length=50,
        choices=[
            ('generated', 'AI Generated'),
            ('erased', 'Object Erased'),
            ('inpainted', 'Inpainted/Smart Fill'),
            ('outpainted', 'Outpainted/Extended'),
            ('upscaled_fast', 'Upscaled (Fast 4x)'),
            ('upscaled_conservative', 'Upscaled (Conservative 4K)'),
            ('upscaled_creative', 'Upscaled (Creative)'),
            ('recolored', 'Recolored'),
            ('background_removed', 'Background Removed'),
            ('sketch_control', 'Sketch to Image'),
            ('structure_control', 'Structure Transfer'),
            ('uploaded', 'User Uploaded'),  # Session 451: User uploads
        ],
        help_text="Type of operation that created this image"
    )
    
    # Generation/editing parameters
    prompt = models.TextField(
        blank=True,
        help_text="Prompt used for generation or editing"
    )
    
    parameters = models.JSONField(
        default=dict,
        help_text="Complete parameters used (style, model, settings, etc.)"
    )
    
    # Model information
    model_used = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('core', 'Stability Core'),
            ('sdxl', 'Stability SDXL'),
            ('sd3', 'Stability SD3'),
            ('ultra', 'Stability Ultra'),
        ],
        help_text="AI model used for generation"
    )
    
    style = models.CharField(
        max_length=100,
        blank=True,
        help_text="Style preset used (e.g., Pixar, Photographic, etc.)"
    )
    
    # Image metadata
    image_width = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Image width in pixels"
    )
    
    image_height = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Image height in pixels"
    )
    
    file_size_bytes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )

    # Session 451: User Upload Support
    source_type = models.CharField(
        max_length=20,
        choices=MediaSourceType.choices,
        default=MediaSourceType.GENERATED,
        help_text="How this content was created (generated, uploaded, imported, edited)"
    )

    original_file = models.FileField(
        upload_to='uploads/images/%Y/%m/',
        null=True,
        blank=True,
        help_text="Original uploaded file (for uploaded images)"
    )

    original_filename = models.CharField(
        max_length=255,
        blank=True,
        help_text="Original filename from upload"
    )

    mime_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="MIME type of the file"
    )

    # Lineage tracking for composite workflows
    parent_image = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='child_images',
        help_text="Parent image if this is an edit of another image"
    )
    
    # Usage tracking
    download_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times downloaded"
    )
    
    view_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times viewed"
    )
    
    is_favorite = models.BooleanField(
        default=False,
        help_text="User marked as favorite"
    )
    
    # User notes
    user_notes = models.TextField(
        blank=True,
        help_text="User's personal notes about this image"
    )
    
    tags = models.JSONField(
        default=list,
        help_text="User-defined tags for organization"
    )

    # CreativeDirectorAgent fields (Session 90 - Multi-option generation + learning)
    # Session 172: Changed to BigIntegerField - Stability AI seeds can exceed 2^31
    seed = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Random seed used for generation (enables exact reproduction)"
    )

    generation_batch_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="UUID linking related options generated together"
    )

    option_number = models.IntegerField(
        null=True,
        blank=True,
        help_text="Option number in batch (1, 2, 3, etc.)"
    )

    was_selected = models.BooleanField(
        default=False,
        help_text="Did user select this option? (agent learns from this!)"
    )

    selection_timestamp = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When user selected this option"
    )

    # Session 182: Persistent sequential number for consistent ID across frontend/backend
    sequential_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Permanent sequential number per user (never changes, even if earlier images deleted)"
    )

    class Meta:
        verbose_name = "Image History"
        verbose_name_plural = "Image History"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['image_type']),
            models.Index(fields=['model_used']),
            models.Index(fields=['style']),
            models.Index(fields=['is_favorite']),
            # CreativeDirectorAgent indexes
            models.Index(fields=['generation_batch_id']),
            models.Index(fields=['user', 'was_selected']),
            # Session 182: Sequential number lookup
            models.Index(fields=['user', 'sequential_number']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.image_type} - {self.filename}"
    
    def get_full_url(self):
        """Get full URL for the image"""
        # Session 64: If file_path is already a data URI, return it directly
        if self.file_path.startswith('data:'):
            return self.file_path
        # Session 800: If file_path is already a Cloudinary/external URL, return directly
        # This eliminates egress costs by serving from CDN instead of through Railway
        if self.file_path.startswith('http'):
            return self.file_path
        return default_storage.url(self.file_path)
    
    def get_thumbnail_url(self):
        """Get thumbnail URL or fallback to full image"""
        if self.thumbnail:
            # Session 64: If thumbnail is a data URI, return it directly
            if self.thumbnail.startswith('data:'):
                return self.thumbnail
            # Session 800: If thumbnail is already a Cloudinary/external URL, return directly
            if self.thumbnail.startswith('http'):
                return self.thumbnail
            return default_storage.url(self.thumbnail)
        return self.get_full_url()

    def save(self, *args, **kwargs):
        """
        Session 182: Auto-assign sequential_number on creation.
        Apr 2026: Auto-generate filename if empty (prevents missing metadata).
        """
        # Auto-generate filename if missing
        if not self.filename:
            ext = 'png'  # default for generated images
            if self.file_path:
                import os
                _, file_ext = os.path.splitext(self.file_path.split('?')[0])
                if file_ext:
                    ext = file_ext.lstrip('.')
            from django.utils import timezone as _tz
            ts = _tz.now().strftime('%Y%m%d_%H%M%S')
            self.filename = f"{self.image_type or 'generated'}_{ts}.{ext}"

        if self._state.adding and self.sequential_number is None:
            # Get the highest sequential number for this user
            from django.db.models import Max
            max_seq = ImageHistory.objects.filter(user=self.user).aggregate(
                Max('sequential_number')
            )['sequential_number__max']

            # If no existing sequential numbers, start from count of existing images
            if max_seq is None:
                # Backfill scenario: count existing images
                existing_count = ImageHistory.objects.filter(user=self.user).count()
                self.sequential_number = existing_count + 1
            else:
                self.sequential_number = max_seq + 1

        super().save(*args, **kwargs)

    def get_sequential_number(self):
        """
        Get sequential number for this image (per user, chronological)

        Session 96 Weekend Project: Hybrid Image ID system
        Session 182: Now returns persistent sequential_number if set

        Returns 1-based sequential number for easy voice commands
        Example: "Use image 12" instead of "Use image d4f7b3c2-8a9e-4d1f..."
        """
        # Session 182: Return stored sequential number if available
        if self.sequential_number is not None:
            return self.sequential_number

        # Fallback: Calculate dynamically (for legacy images without sequential_number)
        earlier_images = ImageHistory.objects.filter(
            user=self.user,
            created_at__lt=self.created_at
        ).count()

        return earlier_images + 1

    def increment_view_count(self):
        """Increment view counter using atomic F() expression"""
        # Phase 2 P1: Use atomic update to prevent race conditions
        ImageHistory.objects.filter(pk=self.pk).update(view_count=F('view_count') + 1)
        self.refresh_from_db(fields=['view_count'])

    def increment_download_count(self):
        """Increment download counter using atomic F() expression"""
        # Phase 2 P1: Use atomic update to prevent race conditions
        ImageHistory.objects.filter(pk=self.pk).update(download_count=F('download_count') + 1)
        self.refresh_from_db(fields=['download_count'])
    
    def get_lineage(self):
        """Get full lineage of edits (parent chain)"""
        lineage = []
        current = self.parent_image
        while current:
            lineage.append(current)
            current = current.parent_image
        return lineage
    
    def get_descendants(self):
        """Get all child images (edits made from this image)"""
        return ImageHistory.objects.filter(parent_image=self)


class VideoHistory(UnifiedBaseModel):
    """
    Track all AI-generated videos for user gallery
    """

    # User identification
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='video_history',
        help_text="User who created this video"
    )

    # Session 63: Phase C.4++ - Link videos to projects for client management
    project = models.ForeignKey(
        'core.PartnershipProject',  # Session 324: Unified from CreativeProject
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='project_videos',
        help_text="Optional project this video belongs to"
    )

    # Workspace linkage — connects videos to project workspaces
    workspace = models.ForeignKey(
        'core.ProjectWorkspace',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='videos',
        db_index=True,
        help_text="Workspace this video belongs to"
    )

    # Session 96: Weekend Project - Link videos to AI conversation sessions
    session = models.ForeignKey(
        'AISession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='session_videos',
        help_text="AI session that created this video"
    )

    # Session 120: Track which agent created this video
    agent = models.ForeignKey(
        'agents.UnifiedAgentTemplate',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='generated_videos',
        help_text="Agent that generated this video (if created by agent)"
    )

    # Video identification
    video_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Runway ML task/video ID"
    )

    video_url = models.URLField(
        max_length=1000,
        blank=True,
        help_text="URL to the generated video file"
    )

    thumbnail_url = models.URLField(
        max_length=1000,
        blank=True,
        help_text="URL to video thumbnail"
    )

    # Video classification
    video_type = models.CharField(
        max_length=50,
        choices=[
            ('text_to_video', 'Text to Video'),
            ('image_to_video', 'Image to Video'),
            ('extend_video', 'Video Extension'),  # Session 66 Part 2: Runway Extend
            ('chained_video', 'Chained Video'),  # Session 67: DaVinci Resolve chaining
            ('talking_character', 'Talking Character'),  # Talking-head pipeline
            ('uploaded', 'User Uploaded'),  # Session 451: User uploads
        ],
        help_text="Type of video generation"
    )

    # Generation parameters
    prompt = models.TextField(
        help_text="Prompt used for video generation"
    )

    parameters = models.JSONField(
        default=dict,
        help_text="Complete parameters used (model, duration, ratio, etc.)"
    )

    # Model information
    model_used = models.CharField(
        max_length=50,
        choices=[
            ('veo3.1_fast', 'Runway Veo 3.1 Fast'),
            ('veo3.1', 'Runway Veo 3.1'),
            ('gen4_turbo', 'Runway Gen-4 Turbo'),
            ('runway_gen4_turbo', 'Runway Gen-4 Turbo (Pipeline)'),
        ],
        help_text="AI model used for generation"
    )

    # Video metadata
    duration = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Video duration in seconds"
    )

    ratio = models.CharField(
        max_length=20,
        blank=True,
        help_text="Aspect ratio (e.g., 1920:1080)"
    )

    video_width = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Video width in pixels"
    )

    video_height = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Video height in pixels"
    )

    file_size_bytes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )

    # Session 451: User Upload Support
    source_type = models.CharField(
        max_length=20,
        choices=MediaSourceType.choices,
        default=MediaSourceType.GENERATED,
        help_text="How this content was created (generated, uploaded, imported, edited)"
    )

    video_file = models.FileField(
        upload_to='uploads/videos/%Y/%m/',
        null=True,
        blank=True,
        help_text="Uploaded video file (for user uploads)"
    )

    original_filename = models.CharField(
        max_length=255,
        blank=True,
        help_text="Original filename from upload"
    )

    mime_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="MIME type of the file"
    )

    fps = models.FloatField(
        null=True,
        blank=True,
        help_text="Frames per second"
    )

    codec = models.CharField(
        max_length=50,
        blank=True,
        help_text="Video codec (h264, hevc, etc.)"
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='processing',
        help_text="Generation status"
    )

    error_message = models.TextField(
        blank=True,
        help_text="Error message if generation failed"
    )

    # Source image for image-to-video
    source_image = models.ForeignKey(
        ImageHistory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='generated_videos',
        help_text="Source image if this is image-to-video"
    )

    # Session 66 Part 2: Parent video for extension tracking
    parent_video_url = models.URLField(
        max_length=1000,
        blank=True,
        help_text="URL of parent video if this is an extension (for tracking 8s→18s→28s→38s chains)"
    )

    # Usage tracking
    download_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times downloaded"
    )

    view_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times viewed"
    )

    is_favorite = models.BooleanField(
        default=False,
        help_text="User marked as favorite"
    )

    # User notes
    user_notes = models.TextField(
        blank=True,
        help_text="User's personal notes about this video"
    )

    tags = models.JSONField(
        default=list,
        help_text="User-defined tags for organization"
    )

    # Generation timing
    generation_started = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When video generation started"
    )

    generation_completed = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When video generation completed"
    )

    generation_time_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Total generation time in seconds"
    )

    class Meta:
        verbose_name = "Video History"
        verbose_name_plural = "Video History"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['video_type']),
            models.Index(fields=['model_used']),
            models.Index(fields=['status']),
            models.Index(fields=['is_favorite']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.video_type} - {self.video_id}"

    def increment_view_count(self):
        """Increment view counter using atomic F() expression"""
        # Phase 2 P1: Use atomic update to prevent race conditions
        VideoHistory.objects.filter(pk=self.pk).update(view_count=F('view_count') + 1)
        self.refresh_from_db(fields=['view_count'])

    def increment_download_count(self):
        """Increment download counter using atomic F() expression"""
        # Phase 2 P1: Use atomic update to prevent race conditions
        VideoHistory.objects.filter(pk=self.pk).update(download_count=F('download_count') + 1)
        self.refresh_from_db(fields=['download_count'])

    def get_sequential_number(self):
        """
        Get sequential number for this video (per user, chronological)

        Session 119: Add sequential numbering to videos (like images and projects)
        Returns 1-based sequential number for easy voice commands
        Example: "Use video 12" instead of "Use video d4f7b3c2-8a9e-4d1f..."
        """
        # Count how many videos this user has created BEFORE this one
        earlier_videos = VideoHistory.objects.filter(
            user=self.user,
            created_at__lt=self.created_at
        ).count()

        # Sequential number is count + 1 (1-based indexing)
        return earlier_videos + 1


class VideoTranscript(UnifiedBaseModel):
    """
    Persisted video transcription (Whisper or other provider).
    Linked to VideoHistory; stores full text + timestamped segments.
    """

    video = models.ForeignKey(
        VideoHistory,
        on_delete=models.CASCADE,
        related_name='transcripts',
        help_text="Source video"
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('queued', 'Queued'),
            ('running', 'Running'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='queued',
    )

    provider = models.CharField(
        max_length=50,
        default='whisper',
        help_text="Transcription provider (whisper, etc.)"
    )

    language = models.CharField(
        max_length=10,
        blank=True,
        help_text="Detected or requested language code (e.g. en)"
    )

    text = models.TextField(
        blank=True,
        help_text="Full transcript text"
    )

    segments_json = models.JSONField(
        default=list,
        help_text="Timestamped segments: [{start, end, text}, ...]"
    )

    duration_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Audio duration processed"
    )

    error = models.TextField(
        blank=True,
        help_text="Error message if transcription failed"
    )

    class Meta:
        app_label = 'content'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['video', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Transcript {self.id} ({self.status}) for video {self.video_id}"


class AudioHistory(UnifiedBaseModel):
    """
    Track all AI-generated audio for user gallery.
    Session 305: Created for AudioAgent tracking (TTS, voice clones, SFX)
    """

    # User identification
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='audio_history',
        help_text="User who created this audio"
    )

    # Link to projects
    project = models.ForeignKey(
        'core.PartnershipProject',  # Session 324: Unified from CreativeProject
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='project_audio',
        help_text="Optional project this audio belongs to"
    )

    # Workspace linkage — connects audio to project workspaces
    workspace = models.ForeignKey(
        'core.ProjectWorkspace',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audio',
        db_index=True,
        help_text="Workspace this audio belongs to"
    )

    # Link to AI sessions
    session = models.ForeignKey(
        'AISession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='session_audio',
        help_text="AI session that created this audio"
    )

    # Track which agent created this audio
    agent = models.ForeignKey(
        'agents.UnifiedAgentTemplate',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='generated_audio',
        help_text="Agent that generated this audio (if created by agent)"
    )

    # Audio identification
    filename = models.CharField(
        max_length=255,
        help_text="Stored filename"
    )

    file_path = models.TextField(
        help_text="Full path to audio file in storage"
    )

    # Audio classification
    audio_type = models.CharField(
        max_length=50,
        choices=[
            ('tts', 'Text to Speech'),
            ('voice_clone', 'Voice Clone'),
            ('sfx', 'Sound Effect'),
            ('voice_design', 'Voice Design'),
            ('audio_isolation', 'Audio Isolation'),
        ],
        help_text="Type of audio generation"
    )

    # Generation parameters
    prompt = models.TextField(
        blank=True,
        help_text="Text/prompt used for generation"
    )

    parameters = models.JSONField(
        default=dict,
        help_text="Complete parameters used (voice, model, settings, etc.)"
    )

    # Voice information
    voice_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="ElevenLabs voice ID used"
    )

    voice_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Human-readable voice name"
    )

    # Model information
    model_used = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('eleven_multilingual_v2', 'ElevenLabs Multilingual v2'),
            ('eleven_turbo_v2', 'ElevenLabs Turbo v2'),
            ('eleven_english_v1', 'ElevenLabs English v1'),
            ('eleven_monolingual_v1', 'ElevenLabs Monolingual v1'),
        ],
        help_text="AI model used for generation"
    )

    # Audio metadata
    duration_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Audio duration in seconds"
    )

    file_size_bytes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )

    sample_rate = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Audio sample rate in Hz"
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='completed',
        help_text="Generation status"
    )

    error_message = models.TextField(
        blank=True,
        help_text="Error message if generation failed"
    )

    # Usage tracking
    download_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times downloaded"
    )

    play_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times played"
    )

    is_favorite = models.BooleanField(
        default=False,
        help_text="User marked as favorite"
    )

    # User notes
    user_notes = models.TextField(
        blank=True,
        help_text="User's personal notes about this audio"
    )

    tags = models.JSONField(
        default=list,
        help_text="User-defined tags for organization"
    )

    class Meta:
        verbose_name = "Audio History"
        verbose_name_plural = "Audio History"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['audio_type']),
            models.Index(fields=['model_used']),
            models.Index(fields=['status']),
            models.Index(fields=['is_favorite']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.audio_type} - {self.filename}"

    def increment_play_count(self):
        """Increment play counter using atomic F() expression"""
        AudioHistory.objects.filter(pk=self.pk).update(play_count=F('play_count') + 1)
        self.refresh_from_db(fields=['play_count'])

    def increment_download_count(self):
        """Increment download counter using atomic F() expression"""
        AudioHistory.objects.filter(pk=self.pk).update(download_count=F('download_count') + 1)
        self.refresh_from_db(fields=['download_count'])

    def get_sequential_number(self):
        """
        Get sequential number for this audio (per user, chronological)
        Returns 1-based sequential number for easy voice commands
        """
        earlier_audio = AudioHistory.objects.filter(
            user=self.user,
            created_at__lt=self.created_at
        ).count()
        return earlier_audio + 1


class MiniFigAsset(UnifiedBaseModel):
    """
    Track 3D Mini-Fig assets created from AI-generated images
    Session 111 - MiniFig Pipeline v1
    """

    # User identification
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='minifig_assets',
        help_text="User who created this mini-fig"
    )

    # Source tracking
    source_pipeline_run = models.ForeignKey(
        'pipelines.CreativePipelineRun',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_minifigs',
        help_text="Pipeline run that created this mini-fig"
    )

    source_image_asset = models.ForeignKey(
        ImageHistory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_minifigs',
        help_text="Source image used for mini-fig generation"
    )

    # Session 137: Add project field
    project = models.ForeignKey(
        'core.PartnershipProject',  # Session 324: Unified from CreativeProject
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='three_d_models',
        help_text="Creative project this 3D model belongs to"
    )

    # MiniFig identification
    title = models.CharField(
        max_length=200,
        help_text="User-friendly title for this mini-fig"
    )

    provider = models.CharField(
        max_length=100,
        default='placeholder',
        choices=[
            ('placeholder', 'Placeholder (v1)'),
            ('external_service', 'External 3D Service (v2+)'),
        ],
        help_text="Provider used for 3D generation"
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending',
        help_text="Generation status"
    )

    # 3D File output
    three_d_file = models.URLField(
        max_length=1000,
        help_text="URL to 3D file (STL, OBJ, etc.) - CDN URL from Replicate (expires in 24-48hrs)"
    )

    # Session 139: Local file persistence (prevents data loss after CDN expiration)
    glb_file = models.FileField(
        upload_to='3d_models/',
        null=True,
        blank=True,
        help_text="Local GLB file (permanent storage)"
    )

    local_glb_path = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Path to local GLB file relative to MEDIA_ROOT"
    )

    download_completed = models.BooleanField(
        default=False,
        help_text="Whether the CDN file has been downloaded to local storage"
    )

    download_error = models.TextField(
        blank=True,
        help_text="Error message if file download failed"
    )

    preview_image_url = models.URLField(
        max_length=1000,
        blank=True,
        help_text="URL to preview/thumbnail image"
    )

    # Generation parameters and metadata
    metadata = models.JSONField(
        default=dict,
        help_text="Additional metadata (style, scale, generation params, etc.)"
    )

    # Error tracking
    error_message = models.TextField(
        blank=True,
        help_text="Error message if generation failed"
    )

    # Usage tracking
    download_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times downloaded"
    )

    view_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times viewed"
    )

    is_favorite = models.BooleanField(
        default=False,
        help_text="User marked as favorite"
    )

    # User notes
    user_notes = models.TextField(
        blank=True,
        help_text="User's personal notes about this mini-fig"
    )

    tags = models.JSONField(
        default=list,
        help_text="User-defined tags for organization"
    )

    class Meta:
        verbose_name = "MiniFig Asset"
        verbose_name_plural = "MiniFig Assets"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['provider']),
            models.Index(fields=['is_favorite']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def get_sequential_number(self):
        """
        Get sequential number for this 3D model (per user, chronological)

        Session 172: Added for consistency with ImageHistory and VideoHistory
        Returns 1-based sequential number for easy voice commands
        Example: "Download 3D model 2" instead of "Download 3D model de49ce16-..."
        """
        # Count how many 3D models this user has created BEFORE this one
        earlier_models = MiniFigAsset.objects.filter(
            user=self.user,
            created_at__lt=self.created_at
        ).count()

        # Sequential number is count + 1 (1-based indexing)
        return earlier_models + 1

    def increment_view_count(self):
        """Increment view counter using atomic F() expression"""
        # Phase 2 P1: Use atomic update to prevent race conditions
        MiniFigAsset.objects.filter(pk=self.pk).update(view_count=F('view_count') + 1)
        self.refresh_from_db(fields=['view_count'])

    def increment_download_count(self):
        """Increment download counter using atomic F() expression"""
        # Phase 2 P1: Use atomic update to prevent race conditions
        MiniFigAsset.objects.filter(pk=self.pk).update(download_count=F('download_count') + 1)
        self.refresh_from_db(fields=['download_count'])


class WorkflowHistory(UnifiedBaseModel):
    """
    Track all AI workflow executions for user history and analysis
    Supports Logo Creator, Portrait Enhancer, Style Explorer, etc.
    """

    # User identification
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workflow_history',
        help_text="User who executed this workflow"
    )

    # Session 62: Phase C.4 - Link workflows to projects for client management
    project = models.ForeignKey(
        'core.PartnershipProject',  # Session 324: Unified from CreativeProject
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workflow_executions',
        help_text="Optional project this workflow belongs to"
    )

    # Workflow identification
    workflow_type = models.CharField(
        max_length=50,
        choices=[
            ('logo_creator', 'Logo Creator'),
            ('portrait_enhancer', 'Portrait Enhancer'),
            ('style_explorer', 'Style Explorer'),
            ('social_media_pack', 'Social Media Pack'),
            ('product_mockup', 'Product Mockup'),
            ('creative_upscale', 'Creative Upscale'),
        ],
        help_text="Type of workflow executed"
    )

    workflow_name = models.CharField(
        max_length=200,
        help_text="Display name of the workflow"
    )

    # Input parameters
    prompt = models.TextField(
        blank=True,
        help_text="User's original prompt"
    )

    improved_prompt = models.TextField(
        blank=True,
        help_text="AI-improved prompt (if used)"
    )

    config = models.JSONField(
        default=dict,
        help_text="Complete workflow configuration (steps, parameters, etc.)"
    )

    # Session 59: Fixed IntegerField → UUIDField (ImageHistory uses UUID primary keys)
    input_image_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="ImageHistory UUID if workflow used an input image"
    )

    # Execution tracking
    execution_time = models.FloatField(
        default=0.0,
        help_text="Total execution time in seconds"
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('running', 'Running'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending',
        help_text="Workflow execution status"
    )

    error_message = models.TextField(
        blank=True,
        help_text="Error details if workflow failed"
    )

    # Results
    result_images = models.JSONField(
        default=list,
        help_text="List of result image URLs/IDs from workflow execution"
    )

    result_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of images generated by workflow"
    )

    # Usage tracking
    is_favorite = models.BooleanField(
        default=False,
        help_text="User marked this execution as favorite"
    )

    rerun_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this workflow was re-run"
    )

    # User notes
    user_notes = models.TextField(
        blank=True,
        help_text="User's personal notes about this workflow execution"
    )

    tags = models.JSONField(
        default=list,
        help_text="User-defined tags for organization"
    )

    class Meta:
        verbose_name = "Workflow History"
        verbose_name_plural = "Workflow History"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['workflow_type']),
            models.Index(fields=['status']),
            models.Index(fields=['is_favorite']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.workflow_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def mark_completed(self, execution_time, result_images):
        """Mark workflow as completed with results"""
        self.status = 'completed'
        self.execution_time = execution_time
        self.result_images = result_images
        self.result_count = len(result_images)
        self.save(update_fields=['status', 'execution_time', 'result_images', 'result_count'])

    def mark_failed(self, error_message):
        """Mark workflow as failed with error details"""
        self.status = 'failed'
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message'])

    def increment_rerun_count(self):
        """Increment rerun counter"""
        self.rerun_count += 1
        self.save(update_fields=['rerun_count'])


class WorkflowFavorite(UnifiedBaseModel):
    """
    User's favorite workflow configurations for quick access
    """

    # User identification
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workflow_favorites',
        help_text="User who saved this favorite"
    )

    # Link to original execution
    workflow_history = models.ForeignKey(
        WorkflowHistory,
        on_delete=models.CASCADE,
        related_name='favorites',
        help_text="Original workflow execution this favorite is based on"
    )

    # Custom naming
    name = models.CharField(
        max_length=200,
        help_text="User-given name for this favorite (e.g., 'My Logo Style')"
    )

    description = models.TextField(
        blank=True,
        help_text="User's description of this favorite workflow"
    )

    # Quick access tracking
    use_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this favorite was used"
    )

    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this favorite was executed"
    )

    # Organization
    category = models.CharField(
        max_length=50,
        blank=True,
        help_text="User-defined category for organization"
    )

    tags = models.JSONField(
        default=list,
        help_text="User-defined tags"
    )

    class Meta:
        verbose_name = "Workflow Favorite"
        verbose_name_plural = "Workflow Favorites"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', '-last_used_at']),
        ]
        # Prevent duplicate favorites of same workflow
        unique_together = [['user', 'workflow_history']]

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    def increment_use_count(self):
        """Increment use counter and update last used timestamp"""
        self.use_count += 1
        self.last_used_at = timezone.now()
        self.save(update_fields=['use_count', 'last_used_at'])


# =============================================================================
# SESSION 60: PHASE C - DECISION COMMAND / PROJECT MANAGEMENT
# =============================================================================
# SESSION 324: DEPRECATED - CreativeProject is now an alias for PartnershipProject
# The PartnershipProject model in core/models_partnership.py is the unified project model.
# This alias exists for backward compatibility with existing code.
# =============================================================================

from core.models_partnership import PartnershipProject as CreativeProject  # noqa: F401

# DEPRECATED: The original CreativeProject class below is kept for reference only
# All new code should use PartnershipProject from core.models_partnership
# The alias above ensures existing imports continue to work

class _DeprecatedCreativeProject(UnifiedBaseModel):
    """
    DEPRECATED - Session 324
    This class is kept for reference only. Use PartnershipProject instead.
    The CreativeProject name is now an alias pointing to PartnershipProject.

    A creative project containing multiple workflows
    Session 60: Phase C.1.1 - Project Management System

    Examples:
    - "Brand Launch Campaign" (logo + social media + marketing materials)
    - "Client Portfolio" (multiple portraits + upscaling)
    - "Social Media Series" (style explorer + variations)
    """

    # User identification
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='deprecated_creative_projects',
        help_text="User who owns this project"
    )

    # Project details
    name = models.CharField(
        max_length=200,
        help_text="Project name (e.g., 'Brand Launch Campaign')"
    )

    description = models.TextField(
        blank=True,
        help_text="Detailed description of the project"
    )

    goal = models.TextField(
        help_text="What's the objective of this project?"
    )

    # Timeline
    deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Project deadline"
    )

    # Project status
    status = models.CharField(
        max_length=20,
        choices=[
            ('planning', 'Planning'),
            ('in_progress', 'In Progress'),
            ('review', 'Under Review'),
            ('completed', 'Completed'),
            ('archived', 'Archived')
        ],
        default='planning',
        help_text="Current project status"
    )

    # Metadata and tracking
    total_workflows = models.PositiveIntegerField(
        default=0,
        help_text="Total number of workflows in this project"
    )

    completed_workflows = models.PositiveIntegerField(
        default=0,
        help_text="Number of completed workflows"
    )

    # Organization
    category = models.CharField(
        max_length=50,
        blank=True,
        help_text="Project category (e.g., 'Branding', 'Marketing', 'Personal')"
    )

    # Session 63: Client intake field - professional agency-style form
    colors = models.CharField(
        max_length=200,
        blank=True,
        help_text="Color palette for this project (e.g., 'navy blue, gold, white')"
    )

    tags = models.JSONField(
        default=list,
        help_text="Project tags for organization"
    )

    # Collaboration (future feature)
    is_shared = models.BooleanField(
        default=False,
        help_text="Whether project is shared with others"
    )

    # Session 97: Quick Starts default project
    is_quick_starts = models.BooleanField(
        default=False,
        help_text="Special project for ad-hoc/spontaneous work"
    )

    # Session 293: Store rich intelligence data from workflow engine
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Rich metadata: research_sources, executive_recommendations, creative_direction, suggested_next_steps"
    )

    class Meta:
        verbose_name = "Deprecated Creative Project"
        verbose_name_plural = "Deprecated Creative Projects"
        ordering = ['-created_at']
        # Session 324: Disable migrations for deprecated model
        managed = False
        abstract = True  # Prevent table creation

    def __str__(self):
        return f"{self.name} ({self.status})"

    @property
    def progress_percentage(self):
        """
        Calculate project completion percentage

        Session 97: Enhanced to calculate from actual content when no workflows
        - Workflow-based: If total_workflows > 0, use completed/total ratio
        - Content-based: Count images + videos, 10 items = 100% progress
        """
        # Workflow-based progress (professional workflow system)
        if self.total_workflows > 0:
            return int((self.completed_workflows / self.total_workflows) * 100)

        # Content-based progress (auto-created projects from AI sessions)
        # Session 97: Count actual images and videos in project
        try:
            # Import here to avoid circular import
            from content.models import ImageHistory, VideoHistory

            # Count content items
            image_count = ImageHistory.objects.filter(project=self).count()
            video_count = VideoHistory.objects.filter(project=self).count()
            total_content = image_count + video_count

            # Calculate progress: 10 items = 100% (reasonable target for a project)
            # Cap at 100% for projects with more content
            if total_content == 0:
                return 0

            progress = min(100, int((total_content / 10) * 100))
            return progress

        except Exception:
            # Fallback if query fails
            return 0

    @property
    def is_overdue(self):
        """Check if project is past deadline"""
        if not self.deadline:
            return False
        return timezone.now() > self.deadline and self.status not in ['completed', 'archived']

    def update_workflow_counts(self):
        """Recalculate workflow counts from linked workflows"""
        from django.db.models import Count, Q

        counts = self.workflows.aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(workflow_history__status='completed'))
        )

        self.total_workflows = counts['total'] or 0
        self.completed_workflows = counts['completed'] or 0
        self.save(update_fields=['total_workflows', 'completed_workflows'])

    def get_sequential_number(self):
        """
        Get sequential number for this project (per user, chronological)

        Session 117: Hybrid Project ID system
        Returns 1-based sequential number for easy referencing
        Example: "Project #5" instead of "Project d4f7b3c2-8a9e-4d1f..."
        """
        # Count how many projects this user has created BEFORE this one
        earlier_projects = CreativeProject.objects.filter(
            user=self.user,
            created_at__lt=self.created_at
        ).count()

        # Sequential number is count + 1 (1-based indexing)
        return earlier_projects + 1


class ProjectWorkflow(models.Model):
    """
    Links workflows to projects
    Session 60: Phase C.1.1 - Project Management System

    Many-to-many relationship between CreativeProject and WorkflowHistory
    with additional metadata (order, notes, etc.)
    """

    # Relationships
    # Session 60: Using UUIDField for foreign keys (following UUID pattern)
    # Session 324: Updated to use string reference for unified PartnershipProject
    project = models.ForeignKey(
        'core.PartnershipProject',
        on_delete=models.CASCADE,
        related_name='workflows',
        help_text="Project this workflow belongs to"
    )

    workflow_history = models.ForeignKey(
        WorkflowHistory,
        on_delete=models.CASCADE,
        related_name='projects',
        help_text="Workflow execution linked to this project"
    )

    # Organization
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order in project sequence (0-indexed)"
    )

    notes = models.TextField(
        blank=True,
        help_text="Notes about this workflow in the project context"
    )

    # Timestamps
    added_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When workflow was added to project"
    )

    class Meta:
        verbose_name = "Project Workflow"
        verbose_name_plural = "Project Workflows"
        ordering = ['order', 'added_at']
        indexes = [
            models.Index(fields=['project', 'order']),
        ]
        # Prevent duplicate workflow assignments to same project
        unique_together = [['project', 'workflow_history']]

    def __str__(self):
        return f"{self.project.name} - {self.workflow_history.workflow_name}"

    def save(self, *args, **kwargs):
        """Override save to update project counts"""
        super().save(*args, **kwargs)
        # Update project workflow counts
        self.project.update_workflow_counts()

    def delete(self, *args, **kwargs):
        """Override delete to update project counts"""
        project = self.project
        super().delete(*args, **kwargs)
        # Update project workflow counts after deletion
        project.update_workflow_counts()


# ==============================================================================
# CHARACTER TRAINING MODELS (Session 74: Replicate Integration)
# ==============================================================================

class CharacterModel(models.Model):
    """
    Trained character model for consistent image generation
    Uses Replicate's FLUX LoRA training for character consistency

    Workflow:
    1. User uploads 10-12 training images
    2. System creates zip file and submits to Replicate
    3. Training takes 30-60 minutes
    4. Once complete, model can generate unlimited consistent images
    """

    # User & identification
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='character_models',
        help_text="User who owns this character"
    )

    name = models.CharField(
        max_length=100,
        help_text="Character name (e.g., 'RoboBuddy', 'LogoMascot')"
    )

    description = models.TextField(
        blank=True,
        help_text="Description of the character"
    )

    trigger_word = models.CharField(
        max_length=50,
        default="TOK",
        help_text="Trigger word to use in prompts for this character"
    )

    # Replicate training details
    replicate_model_owner = models.CharField(
        max_length=100,
        blank=True,
        help_text="Replicate model owner (username)"
    )

    replicate_model_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Replicate model name"
    )

    replicate_version_id = models.CharField(
        max_length=200,
        blank=True,
        help_text="Specific version ID of trained model"
    )

    training_id = models.CharField(
        max_length=200,
        blank=True,
        help_text="Replicate training job ID"
    )

    # Training status
    training_status = models.CharField(
        max_length=20,
        choices=[
            ('preparing', 'Preparing'),
            ('pending', 'Pending'),
            ('training', 'Training'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
        ],
        default='preparing',
        help_text="Current training status"
    )

    training_progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Training progress percentage (0-100)"
    )

    error_message = models.TextField(
        blank=True,
        help_text="Error message if training failed"
    )

    # Training data
    training_images_count = models.IntegerField(
        default=0,
        help_text="Number of training images uploaded"
    )

    training_zip_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Path to training images zip file"
    )

    training_zip_url = models.URLField(
        max_length=1000,
        blank=True,
        help_text="Public URL for training zip (for Replicate)"
    )

    # Training parameters
    training_steps = models.IntegerField(
        default=1000,
        help_text="Number of training steps"
    )

    learning_rate = models.FloatField(
        default=0.0004,
        help_text="Learning rate for training"
    )

    # Timing
    training_started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When training started"
    )

    training_completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When training completed"
    )

    training_duration_seconds = models.IntegerField(
        null=True,
        blank=True,
        help_text="Total training time in seconds"
    )

    # Usage tracking
    generations_count = models.IntegerField(
        default=0,
        help_text="Number of images generated with this character"
    )

    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this character was used for generation"
    )

    # Display
    thumbnail = models.ImageField(
        upload_to='character_training/thumbnails/',
        null=True,
        blank=True,
        help_text="Thumbnail image representing this character"
    )

    # Metadata
    is_public = models.BooleanField(
        default=False,
        help_text="Whether this character can be used by other users"
    )

    is_favorite = models.BooleanField(
        default=False,
        help_text="User has marked this as favorite"
    )

    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated tags for organization"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When character was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update time"
    )

    class Meta:
        verbose_name = "Character Model"
        verbose_name_plural = "Character Models"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'training_status']),
            models.Index(fields=['training_id']),
        ]

    def __str__(self):
        return f"{self.name} ({self.trigger_word}) - {self.training_status}"

    def get_full_model_path(self):
        """Get full Replicate model path"""
        if self.replicate_model_owner and self.replicate_model_name:
            return f"{self.replicate_model_owner}/{self.replicate_model_name}"
        return None

    def increment_usage(self):
        """Increment generation counter"""
        self.generations_count += 1
        self.last_used_at = timezone.now()
        self.save(update_fields=['generations_count', 'last_used_at'])


class CharacterTrainingImage(models.Model):
    """
    Individual training image uploaded by user for character training
    Stores metadata about each image in the training set
    """

    # Relationship
    character_model = models.ForeignKey(
        CharacterModel,
        on_delete=models.CASCADE,
        related_name='training_images',
        help_text="Character model this image belongs to"
    )

    # Image file
    image = models.ImageField(
        upload_to='character_training/uploads/',
        help_text="Training image file"
    )

    # File metadata
    original_filename = models.CharField(
        max_length=255,
        help_text="Original filename when uploaded"
    )

    file_size = models.IntegerField(
        help_text="File size in bytes"
    )

    # Image dimensions
    width = models.IntegerField(
        help_text="Image width in pixels"
    )

    height = models.IntegerField(
        help_text="Image height in pixels"
    )

    # Image quality checks
    is_valid = models.BooleanField(
        default=True,
        help_text="Whether image passes quality checks"
    )

    validation_notes = models.TextField(
        blank=True,
        help_text="Notes about validation (warnings, suggestions)"
    )

    # Processing
    is_processed = models.BooleanField(
        default=False,
        help_text="Whether image has been processed for training"
    )

    processed_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Path to processed/optimized image"
    )

    # Order in training set
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order in training set"
    )

    # Timestamps
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When image was uploaded"
    )

    class Meta:
        verbose_name = "Character Training Image"
        verbose_name_plural = "Character Training Images"
        ordering = ['order', 'uploaded_at']
        indexes = [
            models.Index(fields=['character_model', 'order']),
        ]

    def __str__(self):
        return f"{self.original_filename} ({self.character_model.name})"


# Session 90: CreativeDirectorAgent - User Preference Learning
class UserCreativePreference(models.Model):
    """
    Track user's creative preferences for AI-powered personalization.

    The CreativeDirectorAgent learns which styles, models, and aesthetics
    each user prefers by analyzing their choices. Over time, the agent gets
    smarter at generating options the user will love!

    Philosophy: AI suggests → Human chooses → Agent learns → Gets better!
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='creative_preferences',
        help_text="User these preferences belong to"
    )

    # Style preferences (learned from user choices)
    preferred_styles = models.JSONField(
        default=list,
        blank=True,
        help_text="List of preferred styles (photographic, digital-art, etc.) ordered by preference"
    )

    preferred_models = models.JSONField(
        default=list,
        blank=True,
        help_text="List of preferred AI models (sdxl, ultra, etc.) ordered by preference"
    )

    # Advanced preferences (future enhancement)
    color_preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="Color palette preferences (warm: 0.7, cool: 0.3, etc.)"
    )

    composition_preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="Composition preferences (centered: 0.6, rule_of_thirds: 0.9, etc.)"
    )

    # Learning statistics
    total_choices = models.IntegerField(
        default=0,
        help_text="Total number of choices user has made (agent learning progress)"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When user started using CreativeDirector"
    )

    last_updated = models.DateTimeField(
        auto_now=True,
        help_text="Last time preferences were updated"
    )

    class Meta:
        verbose_name = "User Creative Preference"
        verbose_name_plural = "User Creative Preferences"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['total_choices']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.total_choices} choices learned"

    def get_learning_stage(self):
        """Get user's learning stage for messaging"""
        if self.total_choices == 0:
            return "new"
        elif self.total_choices < 5:
            return "learning"
        elif self.total_choices < 10:
            return "patterns"
        else:
            return "knows_taste"

    def get_learning_message(self):
        """Get personalized message based on learning stage"""
        stage = self.get_learning_stage()

        messages = {
            "new": "I'm ready to learn your creative taste!",
            "learning": f"I'm learning... {self.total_choices} choices recorded!",
            "patterns": f"Pattern emerging! {self.total_choices} choices analyzed",
            "knows_taste": f"I know your taste! {self.total_choices} choices learned"
        }

        return messages.get(stage, "Learning your preferences...")


class AISession(UnifiedBaseModel):
    """
    Track AI Assistant conversations and link all created content

    Session 96: Weekend Project - Fix orphaned content problem
    Automatically create sessions from AI conversations and link all generated assets
    """

    # User identification
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ai_sessions',
        help_text="User who owns this session"
    )

    # Session identification
    session_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text="Unique session identifier for tracking"
    )

    # Session metadata
    title = models.CharField(
        max_length=255,
        help_text="Session title (auto-generated or user-defined)"
    )

    description = models.TextField(
        blank=True,
        help_text="Brief description of what was created in this session"
    )

    # Conversation data
    conversation_transcript = models.JSONField(
        default=list,
        help_text="Complete conversation history (messages and responses)"
    )

    first_prompt = models.TextField(
        blank=True,
        help_text="The initial user prompt that started this session"
    )

    # Project linkage
    project = models.ForeignKey(
        'core.PartnershipProject',  # Session 324: Unified from CreativeProject
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sessions',
        help_text="Optional project this session belongs to (can auto-create)"
    )

    auto_created_project = models.BooleanField(
        default=False,
        help_text="Whether we auto-created a project from this session"
    )

    # Session status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this session is currently active"
    )

    ended_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the session was ended/closed"
    )

    # Content counters (for quick stats)
    total_images = models.PositiveIntegerField(
        default=0,
        help_text="Total images created in this session"
    )

    total_videos = models.PositiveIntegerField(
        default=0,
        help_text="Total videos created in this session"
    )

    total_audio = models.PositiveIntegerField(
        default=0,
        help_text="Total audio files created in this session"
    )

    # Session tags and categorization
    tags = models.JSONField(
        default=list,
        help_text="Auto-generated and user-defined tags"
    )

    session_type = models.CharField(
        max_length=50,
        blank=True,
        default='default',
        choices=[
            ('default', 'Default Session'),
            ('boardroom', 'Executive Boardroom Meeting'),
            ('branding', 'Branding Package'),
            ('logo_design', 'Logo Design'),
            ('video_creation', 'Video Creation'),
            ('content_package', 'Complete Content Package'),
            ('exploration', 'Creative Exploration'),
            ('refinement', 'Content Refinement'),
            ('general', 'General Creation'),
        ],
        help_text="Type of session or creative work"
    )

    # Boardroom meeting fields (Session 98)
    participants = models.JSONField(
        default=list,
        blank=True,
        help_text="List of agent names participating in boardroom meetings"
    )

    meeting_topic = models.TextField(
        blank=True,
        help_text="Topic/agenda for boardroom meetings"
    )

    meeting_summary = models.TextField(
        blank=True,
        help_text="Summary of boardroom meeting discussion"
    )

    decisions = models.JSONField(
        default=list,
        blank=True,
        help_text="Decisions made during boardroom meeting"
    )

    action_items = models.JSONField(
        default=list,
        blank=True,
        help_text="Action items from boardroom meeting"
    )

    agent_responses = models.JSONField(
        default=dict,
        blank=True,
        help_text="Individual agent responses in boardroom meetings"
    )

    class Meta:
        verbose_name = "AI Session"
        verbose_name_plural = "AI Sessions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['session_id']),
            models.Index(fields=['is_active']),
            models.Index(fields=['project']),
        ]

    def __str__(self):
        return f"{self.title} ({self.user.username}) - {self.total_images}i/{self.total_videos}v/{self.total_audio}a"

    def end_session(self):
        """Mark session as ended"""
        self.is_active = False
        self.ended_at = timezone.now()
        self.save(update_fields=['is_active', 'ended_at'])

    def update_counters(self):
        """Update content counters from related objects"""
        self.total_images = self.session_images.count()
        self.total_videos = self.session_videos.count()
        self.total_audio = 0  # TODO: Add when AudioHistory model is ready
        self.save(update_fields=['total_images', 'total_videos', 'total_audio'])

    def get_all_content(self):
        """Get all content created in this session"""
        return {
            'images': list(self.session_images.all()),
            'videos': list(self.session_videos.all()),
            # 'audio': list(self.session_audio.all()),  # TODO: Add when ready
        }

    def export_summary(self):
        """Export session summary for display"""
        return {
            'session_id': str(self.session_id),
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active,
            'total_images': self.total_images,
            'total_videos': self.total_videos,
            'total_audio': self.total_audio,
            'first_prompt': self.first_prompt,
            'tags': self.tags,
            'session_type': self.session_type,
            'project_id': self.project_id if self.project else None,
            'project_name': self.project.name if self.project else None,
        }


# ============================================================================
# SESSION 149: PROJECT SHARE LINKS
# ============================================================================

class ProjectShare(models.Model):
    """
    Public share link for a project
    Session 149: Public Share Links

    Enables users to share projects publicly with optional password protection
    and expiration dates. Tracks view analytics for shared projects.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Session 324: Updated to use string reference for unified PartnershipProject
    project = models.ForeignKey(
        'core.PartnershipProject',
        on_delete=models.CASCADE,
        related_name='shares',
        help_text="Project being shared"
    )

    share_token = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
        help_text="Unique token for share URL (auto-generated)"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether the share link is active"
    )

    password_hash = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="Hashed password for protected shares"
    )

    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the share link expires (null = never)"
    )

    view_count = models.IntegerField(
        default=0,
        help_text="Number of times the shared project has been viewed"
    )

    last_viewed = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the share link was last viewed"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_shares'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['share_token']),
            models.Index(fields=['project', 'is_active']),
            models.Index(fields=['expires_at']),
        ]
        verbose_name = "Project Share"
        verbose_name_plural = "Project Shares"

    def __str__(self):
        status = "Active" if self.is_accessible() else "Inactive"
        return f"{self.project.name} - {status} ({self.view_count} views)"

    def save(self, *args, **kwargs):
        """Generate share token on first save"""
        if not self.share_token:
            import secrets
            self.share_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def set_password(self, raw_password):
        """Hash and set password"""
        from django.contrib.auth.hashers import make_password
        if raw_password:
            self.password_hash = make_password(raw_password)
        else:
            self.password_hash = None

    def check_password(self, raw_password):
        """Check if password matches"""
        from django.contrib.auth.hashers import check_password
        if not self.password_hash:
            return True  # No password set
        return check_password(raw_password, self.password_hash)

    def is_expired(self):
        """Check if share link has expired"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    def is_accessible(self):
        """Check if share link is accessible"""
        return self.is_active and not self.is_expired()

    def increment_view_count(self):
        """Increment view count and update last_viewed using atomic F() expression"""
        # Phase 2 P1: Use atomic update to prevent race conditions
        ShareableLink.objects.filter(pk=self.pk).update(
            view_count=F('view_count') + 1,
            last_viewed=timezone.now()
        )
        self.refresh_from_db(fields=['view_count', 'last_viewed'])

    def get_share_url(self, request=None):
        """Get full share URL"""
        if request:
            return request.build_absolute_uri(f'/share/{self.share_token}/')
        return f'/share/{self.share_token}/'

    def revoke(self):
        """Revoke the share link"""
        self.is_active = False
        self.save(update_fields=['is_active'])


class UploadSession(models.Model):
    """
    Session 451: Track multi-part/chunked uploads for large files.
    Enables resume capability for failed uploads.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='upload_sessions')

    # Upload metadata
    filename = models.CharField(max_length=255, help_text="Original filename")
    file_size = models.BigIntegerField(help_text="Total file size in bytes")
    mime_type = models.CharField(max_length=100, help_text="MIME type of the file")
    content_type = models.CharField(
        max_length=20,
        choices=[
            ('image', 'Image'),
            ('video', 'Video'),
            ('audio', 'Audio'),
        ],
        default='video',
        help_text="Type of content being uploaded"
    )
    chunk_size = models.IntegerField(default=5242880, help_text="Chunk size in bytes (default 5MB)")

    # Progress tracking
    chunks_received = models.IntegerField(default=0, help_text="Number of chunks received")
    chunks_total = models.IntegerField(help_text="Total number of chunks expected")
    bytes_received = models.BigIntegerField(default=0, help_text="Bytes received so far")

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('uploading', 'Uploading'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending',
        help_text="Upload status"
    )

    # Temp storage path
    temp_path = models.CharField(max_length=500, blank=True, help_text="Path to temp directory for chunks")

    # Error tracking
    error_message = models.TextField(blank=True, help_text="Error message if upload failed")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(help_text="Auto-cleanup incomplete uploads after this time")

    # Result - link to created content
    result_content_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Type of content created (image, video, audio)"
    )
    result_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="ID of the created ImageHistory, VideoHistory, or AudioHistory"
    )

    # Optional project association
    project = models.ForeignKey(
        'core.PartnershipProject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='upload_sessions',
        help_text="Project to associate uploaded content with"
    )

    class Meta:
        verbose_name = "Upload Session"
        verbose_name_plural = "Upload Sessions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.filename} ({self.status})"

    @property
    def progress_percent(self):
        """Calculate upload progress percentage"""
        if self.file_size == 0:
            return 0
        return round(self.bytes_received / self.file_size * 100, 1)

    @property
    def is_complete(self):
        """Check if all chunks have been received"""
        return self.chunks_received >= self.chunks_total
