from __future__ import annotations

"""
Data Persistence Models for Unified Donkey Betz Platform
"""

import hashlib
from decimal import Decimal
from typing import Dict, List, Optional
from datetime import timedelta

from django.db import models
from django.db.models import Q, Sum, Count
from django.contrib.auth import get_user_model
from django.utils import timezone

# ---------------------------------------------------------------------
# ArrayField fallback (keeps SQLite/dev workable)
# ---------------------------------------------------------------------
try:
    from django.contrib.postgres.fields import ArrayField as _PGArrayField  # type: ignore
    ArrayField = _PGArrayField  # type: ignore
    POSTGRES_AVAILABLE = True
except Exception:
    POSTGRES_AVAILABLE = False

    # JSON fallback with same call-site shape
    def ArrayField(base_field, **kwargs):  # type: ignore
        return models.JSONField(**kwargs)

# ---------------------------------------------------------------------
# pgvector detection (VectorField, HnswIndex, CosineDistance)
# ---------------------------------------------------------------------
PGVECTOR_AVAILABLE = False
try:
    from pgvector.django import VectorField as _VectorField  # type: ignore
    from pgvector.django import HnswIndex as _HnswIndex  # type: ignore
    from pgvector.django import CosineDistance  # type: ignore
    PGVECTOR_AVAILABLE = True
except Exception:
    # Fallbacks to keep the app running on environments without pgvector
    class _VectorField(models.JSONField):  # type: ignore
        """
        JSON fallback. No ANN index or cosine ops—just storage.
        """
        def __init__(self, *args, **kwargs):
            kwargs.pop("dimensions", None)  # ignore pgvector-only arg
            super().__init__(*args, **kwargs)

    class _HnswIndex(models.Index):  # type: ignore
        """
        Dummy index fallback so Meta.indexes doesn't break when pgvector is absent.
        """
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

# Single aliases used throughout
VectorField = _VectorField
HnswIndex = _HnswIndex

from core.models import UnifiedBaseModel
User = get_user_model()


# =============================================================================
# UNIFIED EMBEDDING SYSTEM
# =============================================================================

class UnifiedEmbedding(UnifiedBaseModel):
    """
    Unified embedding storage for all content types across the platform.
    """

    # Who/what produced it
    creator_agent = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default="system",
        help_text="Agent that created this embedding (if applicable)",
    )

    content_type = models.CharField(
        max_length=50,
        choices=[
            ('agent_knowledge', 'Agent Knowledge'),
            ('spider_data', 'Spider Discovered Data'),
            ('document_chunk', 'Document Chunk'),
            ('code_snippet', 'Code Snippet'),
            ('conversation', 'Agent Conversation'),
            ('opportunity', 'Revenue Opportunity'),
            ('system_log', 'System Log Entry'),
            ('user_interaction', 'User Interaction'),
            ('workflow_result', 'Workflow Result'),
            ('research_finding', 'Research Finding'),
        ],
        db_index=True,
        help_text="Type of content this embedding represents",
    )

    # NOTE: make sure service layer supplies a real UUID
    content_id = models.UUIDField(
        db_index=True,
        help_text="UUID of the content object this embedding represents",
    )

    # Raw content
    content_text = models.TextField(help_text="The actual text content that was embedded")
    content_title = models.CharField(max_length=500, blank=True, help_text="Title/summary")
    content_metadata = models.JSONField(default=dict, help_text="Additional metadata")

    embedding_model = models.CharField(
        max_length=100,
        default='text-embedding-3-small',
        choices=[
            ('text-embedding-3-small', 'OpenAI text-embedding-3-small'),
            ('text-embedding-3-large', 'OpenAI text-embedding-3-large'),
            ('text-embedding-ada-002', 'OpenAI text-embedding-ada-002'),
            ('sentence-transformer', 'Sentence Transformer'),
            ('local-model', 'Local Embedding Model'),
        ],
        help_text="Model used to generate the embedding",
    )

    # The actual vector. Nullable first so migrations don't block in new envs.
    # Default dimension aligns with OpenAI text-embedding-3-small (1536).
    embedding_dimension = models.PositiveIntegerField(
        default=1536, help_text="Vector dimension"
    )
    embedding = VectorField(dimensions=1536, null=True, blank=True)

    source_system = models.CharField(
        max_length=100,
        choices=[
            ('agents', 'Agent System'),
            ('spiders', 'Spider Network'),
            ('content', 'Content System'),
            ('intelligence', 'Intelligence Layer'),
            ('users', 'User System'),
            ('workflows', 'Workflow Engine'),
            ('self_awareness', 'Self-Awareness System'),
        ],
        help_text="System that created this embedding",
    )

    creator_user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_embeddings',
        help_text="User that created this embedding (if applicable)",
    )

    importance_score = models.FloatField(default=0.5)
    relevance_score = models.FloatField(default=0.5)
    confidence_score = models.FloatField(default=0.5)

    access_count = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    search_count = models.PositiveIntegerField(default=0)

    generation_cost = models.DecimalField(max_digits=10, decimal_places=6, default=Decimal('0.000000'))
    generation_time_ms = models.PositiveIntegerField(null=True, blank=True)

    content_hash = models.CharField(max_length=64, db_index=True, blank=True)

    tags = ArrayField(models.CharField(max_length=100), default=list, blank=True)
    category = models.CharField(max_length=100, blank=True)

    content_timestamp = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'persistence'
        verbose_name = "Unified Embedding"
        verbose_name_plural = "Unified Embeddings"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'content_id']),
            models.Index(fields=['source_system', '-created_at']),
            models.Index(fields=['content_hash']),
            models.Index(fields=['-importance_score', '-created_at']),
            models.Index(fields=['category', 'content_type']),
            models.Index(fields=['expires_at']),
            # Optional ANN index (only meaningful when pgvector is installed)
            # For cosine search; you can tune m / ef_construction in a migration if desired.
            *( [
                HnswIndex(
                    name='unified_embedding_hnsw_cosine',
                    fields=['embedding'],
                    opclasses=['vector_cosine_ops'],
                    m=16,
                    ef_construction=64,
                    # The pgvector-django HnswIndex picks the operator class from the field
                    # metric (cosine) implicitly. If you need explicit ops, add opclasses=['vector_cosine_ops'].
                )
            ] if PGVECTOR_AVAILABLE else [] ),
        ]

    def __str__(self):
        title = (self.content_title or self.content_text or '')[:50]
        return f"{self.content_type}: {title}..."

    def save(self, *args, **kwargs):
        if self.content_text and not self.content_hash:
            self.content_hash = hashlib.sha256(self.content_text.encode('utf-8')).hexdigest()
        # Keep embedding_dimension in sync if a service passes a different length
        if isinstance(self.embedding, (list, tuple)) and self.embedding and self.embedding_dimension != len(self.embedding):
            self.embedding_dimension = len(self.embedding)
        super().save(*args, **kwargs)

    def increment_access(self):
        self.access_count += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=['access_count', 'last_accessed'])

    def is_expired(self) -> bool:
        return bool(self.expires_at and timezone.now() > self.expires_at)

    @classmethod
    def search_similar(
        cls,
        query_embedding: List[float],
        content_types: Optional[List[str]] = None,
        limit: int = 10,
        min_score: float = 0.0,  # kept for API compatibility (cosine similarity threshold)
        filters: Optional[Dict] = None,
    ):
        """
        Cosine similarity search via pgvector; graceful no-op when unavailable.

        Note: CosineDistance returns (1 - cosine_similarity) for normalized vectors.
        If `min_score` is provided as *similarity*, we translate to distance threshold.
        """
        if not PGVECTOR_AVAILABLE:
            return cls.objects.none()

        qs = cls.objects.filter(is_active=True)
        if content_types:
            qs = qs.filter(content_type__in=content_types)
        if filters:
            qs = qs.filter(**filters)
        qs = qs.filter(Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()))

        qs = qs.annotate(distance=CosineDistance('embedding', query_embedding))

        # If user supplies a similarity threshold in [0..1], filter by distance <= 1 - min_score
        if min_score and 0.0 <= float(min_score) <= 1.0:
            qs = qs.filter(distance__lte=1.0 - float(min_score))

        return qs.order_by('distance')[:limit]


# =============================================================================
# AGENT KNOWLEDGE AND COLLABORATION SYSTEM
# =============================================================================

class AgentKnowledge(UnifiedBaseModel):
    """
    Shared knowledge base accessible to all agents for collaborative learning.
    """

    # Agent and ownership
    agent_name = models.CharField(
        max_length=200,
        db_index=True,
        help_text="Name of the agent that created this knowledge",
    )

    agent_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="UUID of the specific agent execution instance",
    )

    # Knowledge content
    knowledge_type = models.CharField(
        max_length=50,
        choices=[
            ('fact', 'Factual Information'),
            ('skill', 'Learned Skill or Technique'),
            ('pattern', 'Identified Pattern'),
            ('solution', 'Problem Solution'),
            ('experience', 'Execution Experience'),
            ('insight', 'Strategic Insight'),
            ('warning', 'Warning or Caution'),
            ('best_practice', 'Best Practice'),
            ('optimization', 'Performance Optimization'),
            ('integration', 'System Integration Knowledge'),
        ],
        help_text="Type of knowledge being shared",
    )

    title = models.CharField(
        max_length=255,
        help_text="Clear, descriptive title for the knowledge",
    )

    content = models.JSONField(
        help_text="Structured knowledge content",
    )

    summary = models.TextField(
        help_text="Human-readable summary of the knowledge",
    )

    # Context and applicability
    context = models.JSONField(
        default=dict,
        help_text="Context in which this knowledge is applicable",
    )

    domain_tags = ArrayField(
        models.CharField(max_length=100),
        default=list,
        help_text="Domain tags (sports, content, agents, etc.)",
    )

    applicable_agents = ArrayField(
        models.CharField(max_length=200),
        default=list,
        blank=True,
        help_text="Specific agents this knowledge applies to (empty = all agents)",
    )

    # Sharing and access control
    is_public = models.BooleanField(
        default=True,
        help_text="Whether this knowledge is available to all agents",
    )

    access_level = models.CharField(
        max_length=20,
        choices=[
            ('read', 'Read Only'),
            ('read_write', 'Read and Modify'),
            ('restricted', 'Restricted Access'),
        ],
        default='read',
        help_text="Access level for other agents",
    )

    shared_with = ArrayField(
        models.CharField(max_length=200),
        default=list,
        blank=True,
        help_text="Specific agents this knowledge is shared with",
    )

    # Quality and validation metrics
    confidence_score = models.FloatField(
        default=0.5,
        help_text="Confidence in the accuracy of this knowledge (0.0-1.0)",
    )

    validation_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this knowledge has been validated",
    )

    success_rate = models.FloatField(
        default=0.0,
        help_text="Success rate when this knowledge is applied",
    )

    failure_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times applying this knowledge failed",
    )

    # Usage tracking
    accessed_by = ArrayField(
        models.CharField(max_length=200),
        default=list,
        blank=True,
        help_text="Agents that have accessed this knowledge",
    )

    usage_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this knowledge has been used",
    )

    last_used = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this knowledge was used",
    )

    # Embedding for semantic search
    embedding = models.OneToOneField(
        UnifiedEmbedding,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='agent_knowledge',
        help_text="Embedding for semantic search",
    )

    # Related knowledge
    related_knowledge = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=True,
        help_text="Related knowledge entries",
    )

    superseded_by = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='supersedes',
        help_text="Knowledge entry that supersedes this one",
    )

    class Meta:
        app_label = 'persistence'
        verbose_name = "Agent Knowledge"
        verbose_name_plural = "Agent Knowledge"
        ordering = ['-confidence_score', '-created_at']
        indexes = [
            models.Index(fields=['agent_name', '-created_at']),
            models.Index(fields=['knowledge_type', 'is_public']),
            models.Index(fields=['-confidence_score', '-usage_count']),
            models.Index(fields=['is_public', 'is_active']),
        ]

    def __str__(self):
        return f"{self.agent_name}: {self.title} ({self.knowledge_type})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Generate embedding for semantic search
        if is_new and not self.embedding:
            self.generate_embedding()

    def generate_embedding(self):
        """Generate embedding for semantic search"""
        from .services import EmbeddingService

        text_content = f"{self.title}\n\n{self.summary}"
        if isinstance(self.content, dict):
            for key in ['description', 'steps', 'solution', 'details']:
                if key in self.content:
                    text_content += f"\n\n{self.content[key]}"

        try:
            embedding_service = EmbeddingService()
            embedding = embedding_service.create_embedding(
                content_text=text_content,
                content_type='agent_knowledge',
                content_id=self.id,
                source_system='agents',
                creator_agent=self.agent_name,
                metadata={
                    'knowledge_type': self.knowledge_type,
                    'domain_tags': self.domain_tags,
                    'agent_name': self.agent_name,
                },
            )
            self.embedding = embedding
            self.save(update_fields=['embedding'])
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to generate embedding for AgentKnowledge {self.id}: {e}")

    def record_usage(self, agent_name: str, success: bool = True):
        """Record usage of this knowledge by an agent"""
        self.usage_count += 1
        self.last_used = timezone.now()

        if agent_name not in self.accessed_by:
            self.accessed_by.append(agent_name)

        if success:
            self.validation_count += 1
            total_attempts = self.validation_count + self.failure_count
            self.success_rate = self.validation_count / total_attempts if total_attempts > 0 else 1.0
            self.confidence_score = min(1.0, self.confidence_score + 0.05)
        else:
            self.failure_count += 1
            total_attempts = self.validation_count + self.failure_count
            self.success_rate = self.validation_count / total_attempts if total_attempts > 0 else 0.0
            self.confidence_score = max(0.0, self.confidence_score - 0.1)

        self.save()

    @classmethod
    def search_knowledge(
        cls,
        query: str,
        agent_name: Optional[str] = None,
        knowledge_types: Optional[List[str]] = None,
        domain_tags: Optional[List[str]] = None,
        limit: int = 10,
    ):
        """
        Search agent knowledge using semantic search with fallback to text search.
        """
        from .services import EmbeddingService

        try:
            embedding_service = EmbeddingService()
            query_embedding = embedding_service.generate_embedding_vector(query)

            filters: Dict = {'is_public': True, 'is_active': True}
            if agent_name:
                filters['agent_name'] = agent_name
            if knowledge_types:
                filters['knowledge_type__in'] = knowledge_types

            similar_embeddings = UnifiedEmbedding.search_similar(
                query_embedding=query_embedding,
                content_types=['agent_knowledge'],
                limit=limit,
                filters=filters,
            )

            knowledge_ids = [emb.content_id for emb in similar_embeddings]
            knowledge_entries = cls.objects.filter(id__in=knowledge_ids, is_active=True)

            if domain_tags:
                knowledge_entries = knowledge_entries.filter(domain_tags__overlap=domain_tags)

            knowledge_dict = {str(k.id): k for k in knowledge_entries}
            ordered_results = [
                knowledge_dict[str(emb.content_id)]
                for emb in similar_embeddings
                if str(emb.content_id) in knowledge_dict
            ]
            return ordered_results

        except Exception:
            # Fallback to a simple text search
            queryset = cls.objects.filter(is_public=True, is_active=True)
            if agent_name:
                queryset = queryset.filter(agent_name=agent_name)
            if knowledge_types:
                queryset = queryset.filter(knowledge_type__in=knowledge_types)
            if domain_tags:
                queryset = queryset.filter(domain_tags__overlap=domain_tags)

            return list(
                queryset.filter(Q(title__icontains=query) | Q(summary__icontains=query))[:limit]
            )


class AgentCollaborationSession(UnifiedBaseModel):
    """
    Track collaborative sessions between agents for shared problem solving.
    """

    session_name = models.CharField(
        max_length=255,
        help_text="Name of the collaboration session",
    )

    participating_agents = ArrayField(
        models.CharField(max_length=200),
        help_text="Agents participating in this session",
    )

    session_goal = models.TextField(
        help_text="Goal or objective of the collaboration",
    )

    session_status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('paused', 'Paused'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='active',
    )

    shared_context = models.JSONField(
        default=dict,
        help_text="Shared context and data between agents",
    )

    results = models.JSONField(
        default=dict,
        help_text="Results and outcomes of the collaboration",
    )

    knowledge_generated = models.ManyToManyField(
        AgentKnowledge,
        blank=True,
        related_name='collaboration_sessions',
        help_text="Knowledge generated during this session",
    )

    class Meta:
        app_label = 'persistence'
        verbose_name = "Agent Collaboration Session"
        verbose_name_plural = "Agent Collaboration Sessions"
        ordering = ['-created_at']


# =============================================================================
# SPIDER DATA PERSISTENCE SYSTEM
# =============================================================================

class SpiderData(UnifiedBaseModel):
    """
    Persistent storage for all data discovered by spiders across platforms.
    """

    # Spider identification
    spider_name = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Name of the spider that discovered this data",
    )

    spider_version = models.CharField(
        max_length=20,
        default='1.0.0',
        help_text="Version of the spider",
    )

    spider_execution_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="UUID of the spider execution instance",
    )

    # Source information
    source_url = models.URLField(
        max_length=2000,
        help_text="URL where this data was discovered",
    )

    source_platform = models.CharField(
        max_length=50,
        choices=[
            ('reddit', 'Reddit'),
            ('upwork', 'Upwork'),
            ('fiverr', 'Fiverr'),
            ('freelancer', 'Freelancer.com'),
            ('linkedin', 'LinkedIn'),
            ('twitter', 'Twitter/X'),
            ('facebook', 'Facebook'),
            ('instagram', 'Instagram'),
            ('youtube', 'YouTube'),
            ('github', 'GitHub'),
            ('stackoverflow', 'Stack Overflow'),
            ('medium', 'Medium'),
            ('substack', 'Substack'),
            ('producthunt', 'Product Hunt'),
            ('craigslist', 'Craigslist'),
            ('indeed', 'Indeed'),
            ('glassdoor', 'Glassdoor'),
            ('angellist', 'AngelList'),
            ('other', 'Other Platform'),
        ],
        help_text="Platform where this data was discovered",
    )

    source_metadata = models.JSONField(
        default=dict,
        help_text="Additional metadata about the source",
    )

    # Content data
    title = models.CharField(
        max_length=500,
        help_text="Title or headline of the discovered content",
    )

    content = models.TextField(
        help_text="Raw content text discovered by spider",
    )

    structured_data = models.JSONField(
        default=dict,
        help_text="Structured data extracted from the content",
    )

    raw_html = models.TextField(
        blank=True,
        help_text="Raw HTML content (if applicable)",
    )

    # Classification and categorization
    data_type = models.CharField(
        max_length=50,
        choices=[
            ('opportunity', 'Revenue Opportunity'),
            ('job_posting', 'Job Posting'),
            ('market_data', 'Market Intelligence'),
            ('competitor_info', 'Competitor Information'),
            ('trend_data', 'Trend Data'),
            ('user_feedback', 'User Feedback'),
            ('product_info', 'Product Information'),
            ('pricing_data', 'Pricing Information'),
            ('content_idea', 'Content Creation Idea'),
            ('collaboration', 'Collaboration Opportunity'),
            ('news', 'News or Updates'),
            ('research', 'Research Material'),
            ('tool_discovery', 'Tool or Service Discovery'),
            ('learning_resource', 'Learning Resource'),
        ],
        help_text="Type of data discovered",
    )

    category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Specific category within the data type",
    )

    tags = ArrayField(
        models.CharField(max_length=100),
        default=list,
        help_text="Tags for categorization and search",
    )

    # Scoring and ranking
    relevance_score = models.FloatField(
        default=0.0,
        help_text="Relevance score assigned by spider (0.0-1.0)",
    )

    opportunity_score = models.FloatField(
        default=0.0,
        help_text="Opportunity/revenue potential score (0.0-1.0)",
    )

    quality_score = models.FloatField(
        default=0.0,
        help_text="Content quality score (0.0-1.0)",
    )

    urgency_score = models.FloatField(
        default=0.0,
        help_text="Urgency score for time-sensitive opportunities (0.0-1.0)",
    )

    # Processing status
    is_processed = models.BooleanField(
        default=False,
        help_text="Whether this data has been processed by agents",
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this data was processed",
    )

    processing_result = models.JSONField(
        default=dict,
        help_text="Results of processing by agents",
    )

    # Agent routing
    routed_to_agents = ArrayField(
        models.CharField(max_length=200),
        default=list,
        blank=True,
        help_text="Agents this data has been routed to",
    )

    agent_responses = models.JSONField(
        default=list,
        help_text="Responses from agents that processed this data",
    )

    # Revenue tracking
    revenue_generated = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Revenue generated from this discovery",
    )

    revenue_potential = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated revenue potential",
    )

    conversion_status = models.CharField(
        max_length=20,
        choices=[
            ('discovered', 'Discovered'),
            ('analyzed', 'Analyzed'),
            ('pursued', 'Being Pursued'),
            ('converted', 'Converted to Revenue'),
            ('failed', 'Failed to Convert'),
            ('expired', 'Opportunity Expired'),
        ],
        default='discovered',
    )

    # Embedding for search
    embedding = models.OneToOneField(
        UnifiedEmbedding,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='spider_data',
        help_text="Embedding for semantic search",
    )

    # Duplicate detection
    content_hash = models.CharField(
        max_length=64,
        db_index=True,
        blank=True,
        help_text="SHA-256 hash for duplicate detection",
    )

    similar_discoveries = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=True,
        help_text="Similar discoveries found by other spiders",
    )

    # Time tracking
    discovered_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this data was first discovered",
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this opportunity expires",
    )

    last_updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last time this data was updated",
    )

    class Meta:
        app_label = 'persistence'
        verbose_name = "Spider Data"
        verbose_name_plural = "Spider Data"
        ordering = ['-opportunity_score', '-discovered_at']
        indexes = [
            models.Index(fields=['spider_name', '-discovered_at']),
            models.Index(fields=['source_platform', 'data_type']),
            models.Index(fields=['-opportunity_score', '-relevance_score']),
            models.Index(fields=['is_processed', 'conversion_status']),
            models.Index(fields=['content_hash']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.spider_name}: {self.title[:50]}... ({self.data_type})"

    def save(self, *args, **kwargs):
        # Generate content hash for duplicate detection
        if self.content and not self.content_hash:
            combined_content = f"{self.title}\n{self.content}"
            self.content_hash = hashlib.sha256(combined_content.encode('utf-8')).hexdigest()

        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Generate embedding for semantic search
        if is_new and not self.embedding:
            self.generate_embedding()

    def generate_embedding(self):
        """Generate embedding for semantic search"""
        from .services import EmbeddingService

        text_content = f"{self.title}\n\n{self.content}"

        try:
            embedding_service = EmbeddingService()
            embedding = embedding_service.create_embedding(
                content_text=text_content,
                content_type='spider_data',
                content_id=self.id,
                source_system='spiders',
                creator_agent=self.spider_name,
                metadata={
                    'data_type': self.data_type,
                    'source_platform': self.source_platform,
                    'spider_name': self.spider_name,
                    'opportunity_score': self.opportunity_score,
                    'relevance_score': self.relevance_score,
                },
            )
            self.embedding = embedding
            self.save(update_fields=['embedding'])
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to generate embedding for SpiderData {self.id}: {e}")

    def route_to_agent(self, agent_name: str, priority: str = 'normal'):
        """Route this data to a specific agent for processing"""
        if agent_name not in self.routed_to_agents:
            self.routed_to_agents.append(agent_name)
            self.save(update_fields=['routed_to_agents'])

            SpiderDataRoute.objects.create(
                spider_data=self,
                target_agent=agent_name,
                routing_reason=f"Routed based on {self.data_type} classification",
                priority=priority,
            )

    def record_agent_response(self, agent_name: str, response: Dict):
        """Record response from an agent that processed this data"""
        response_record = {
            'agent_name': agent_name,
            'timestamp': timezone.now().isoformat(),
            'response': response,
        }
        self.agent_responses.append(response_record)

        if not self.is_processed:
            self.is_processed = True
            self.processed_at = timezone.now()

        self.save(update_fields=['agent_responses', 'is_processed', 'processed_at'])

    def update_conversion_status(self, status: str, revenue: Optional[Decimal] = None):
        """Update conversion status and revenue"""
        self.conversion_status = status
        if revenue is not None:
            self.revenue_generated = revenue

        self.save(update_fields=['conversion_status', 'revenue_generated'])

    @classmethod
    def find_similar(cls, content: str, threshold: float = 0.8):
        """Find similar spider discoveries using content hash and semantic search"""
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        exact_matches = cls.objects.filter(content_hash=content_hash)
        if exact_matches.exists():
            return exact_matches

        from .services import EmbeddingService
        try:
            embedding_service = EmbeddingService()
            query_embedding = embedding_service.generate_embedding_vector(content)

            similar_embeddings = UnifiedEmbedding.search_similar(
                query_embedding=query_embedding,
                content_types=['spider_data'],
                limit=10,
                min_score=threshold,
            )

            similar_ids = [emb.content_id for emb in similar_embeddings]
            return cls.objects.filter(id__in=similar_ids)

        except Exception:
            return cls.objects.none()


class SpiderDataRoute(UnifiedBaseModel):
    """
    Track routing of spider data to agents for processing.
    """

    spider_data = models.ForeignKey(
        SpiderData,
        on_delete=models.CASCADE,
        related_name='routing_records',
    )

    target_agent = models.CharField(
        max_length=200,
        help_text="Agent this data was routed to",
    )

    routing_reason = models.TextField(
        help_text="Reason for routing to this agent",
    )

    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Priority'),
            ('normal', 'Normal Priority'),
            ('high', 'High Priority'),
            ('urgent', 'Urgent'),
        ],
        default='normal',
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending',
    )

    agent_response = models.JSONField(
        null=True,
        blank=True,
        help_text="Response from the agent",
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        app_label = 'persistence'
        verbose_name = "Spider Data Route"
        verbose_name_plural = "Spider Data Routes"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['target_agent', 'status']),
            models.Index(fields=['priority', '-created_at']),
        ]


# =============================================================================
# REVENUE TRACKING SYSTEM
# =============================================================================

class RevenueTracker(UnifiedBaseModel):
    """
    Track actual revenue generation from all platform activities.
    """

    # Revenue identification
    revenue_source = models.CharField(
        max_length=50,
        choices=[
            ('spider_discovery', 'Spider Discovery'),
            ('agent_execution', 'Agent Execution'),
            ('content_generation', 'Content Generation'),
            ('betting_recommendation', 'Betting Recommendation'),
            ('workflow_automation', 'Workflow Automation'),
            ('user_subscription', 'User Subscription'),
            ('api_usage', 'API Usage'),
            ('affiliate_commission', 'Affiliate Commission'),
            ('consulting_service', 'Consulting Service'),
            ('data_licensing', 'Data Licensing'),
        ],
        db_index=True,
        help_text="Source system that generated this revenue",
    )

    # Financial data
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Revenue amount in USD",
    )

    currency = models.CharField(
        max_length=3,
        default='USD',
        help_text="Currency code (ISO 4217)",
    )

    # Source tracking
    source_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="ID of the source object that generated this revenue",
    )

    source_agent = models.CharField(
        max_length=200,
        blank=True,
        help_text="Agent that contributed to this revenue",
    )

    source_spider = models.CharField(
        max_length=100,
        blank=True,
        help_text="Spider that discovered the opportunity",
    )

    # Revenue details
    description = models.TextField(
        help_text="Description of how this revenue was generated",
    )

    transaction_id = models.CharField(
        max_length=200,
        blank=True,
        help_text="External transaction ID (PayPal, Stripe, etc.)",
    )

    verification_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Verification'),
            ('verified', 'Verified'),
            ('disputed', 'Disputed'),
            ('refunded', 'Refunded'),
            ('settled', 'Settled'),
        ],
        default='pending',
        help_text="Status of revenue verification",
    )

    # Attribution and conversion tracking
    opportunity_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="Related opportunity that led to this revenue",
    )

    conversion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Conversion rate from opportunity to revenue",
    )

    conversion_time = models.DurationField(
        null=True,
        blank=True,
        help_text="Time from opportunity discovery to revenue conversion",
    )

    # Performance metrics
    roi_percentage = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Return on investment percentage",
    )

    confidence_score = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Confidence in revenue attribution (0.0-1.0)",
    )

    # Time tracking
    earned_at = models.DateTimeField(
        help_text="When the revenue was actually earned",
    )

    reported_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the revenue was recorded in the system",
    )

    # Metadata and context
    metadata = models.JSONField(
        default=dict,
        help_text="Additional revenue context and metadata",
    )

    tags = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True,
        help_text="Tags for categorizing revenue",
    )

    class Meta:
        app_label = 'persistence'
        verbose_name = "Revenue Tracker"
        verbose_name_plural = "Revenue Trackers"
        ordering = ['-earned_at', '-amount']
        indexes = [
            models.Index(fields=['revenue_source', '-earned_at']),
            models.Index(fields=['-amount', '-earned_at']),
            models.Index(fields=['verification_status', '-reported_at']),
            models.Index(fields=['source_agent', '-earned_at']),
            models.Index(fields=['source_spider', '-earned_at']),
            models.Index(fields=['opportunity_id']),
        ]

    def __str__(self):
        return f"${self.amount} from {self.revenue_source} ({self.earned_at.date()})"

    @classmethod
    def record_revenue(cls, amount: Decimal, source: str, description: str,
                       agent: Optional[str] = None, spider: Optional[str] = None, **kwargs):
        """
        Record new revenue with proper attribution.
        """
        return cls.objects.create(
            amount=amount,
            revenue_source=source,
            description=description,
            source_agent=agent,
            source_spider=spider,
            earned_at=timezone.now(),
            **kwargs,
        )

    @classmethod
    def get_total_revenue(cls, days: Optional[int] = None, source: Optional[str] = None):
        """
        Get total revenue with optional filters.
        """
        queryset = cls.objects.filter(verification_status='verified')

        if days:
            since = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(earned_at__gte=since)

        if source:
            queryset = queryset.filter(revenue_source=source)

        return queryset.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    @classmethod
    def get_revenue_by_agent(cls, days: int = 30):
        """
        Get revenue breakdown by agent for the last N days.
        """
        since = timezone.now() - timedelta(days=days)
        return (
            cls.objects.filter(
                earned_at__gte=since,
                verification_status='verified',
                source_agent__isnull=False,
            )
            .values('source_agent')
            .annotate(total=Sum('amount'), count=Count('id'))
            .order_by('-total')
        )

    @classmethod
    def get_revenue_by_spider(cls, days: int = 30):
        """
        Get revenue breakdown by spider for the last N days.
        """
        since = timezone.now() - timedelta(days=days)
        return (
            cls.objects.filter(
                earned_at__gte=since,
                verification_status='verified',
                source_spider__isnull=False,
            )
            .values('source_spider')
            .annotate(total=Sum('amount'), count=Count('id'))
            .order_by('-total')
        )


# =============================================================================
# PERSISTENCE SERVICES AND UTILITIES
# =============================================================================

class DataPersistenceMetrics(UnifiedBaseModel):
    """
    Track metrics and performance of the data persistence system.
    """

    metric_name = models.CharField(
        max_length=100,
        help_text="Name of the metric",
    )

    metric_type = models.CharField(
        max_length=20,
        choices=[
            ('counter', 'Counter'),
            ('gauge', 'Gauge'),
            ('histogram', 'Histogram'),
            ('timer', 'Timer'),
        ],
    )

    metric_value = models.FloatField(
        help_text="Numeric value of the metric",
    )

    subsystem = models.CharField(
        max_length=50,
        choices=[
            ('embeddings', 'Embedding System'),
            ('agent_knowledge', 'Agent Knowledge'),
            ('spider_data', 'Spider Data'),
            ('search', 'Search System'),
            ('collaboration', 'Agent Collaboration'),
            ('routing', 'Data Routing'),
            ('performance', 'System Performance'),
        ],
    )

    metadata = models.JSONField(
        default=dict,
        help_text="Additional metric metadata",
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'persistence'
        verbose_name = "Data Persistence Metric"
        verbose_name_plural = "Data Persistence Metrics"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric_name', '-timestamp']),
            models.Index(fields=['subsystem', '-timestamp']),
        ]

    @classmethod
    def record_metric(
        cls,
        name: str,
        value: float,
        metric_type: str = 'gauge',
        subsystem: str = 'performance',
        metadata: Optional[Dict] = None,
    ):
        """Record a new metric value"""
        return cls.objects.create(
            metric_name=name,
            metric_value=value,
            metric_type=metric_type,
            subsystem=subsystem,
            metadata=metadata or {},
        )