"""
Intelligence Learning Models
Persistent storage for agent learning and knowledge management
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import json
import uuid

User = get_user_model()


class AgentLearningEvent(models.Model):
    """Store every learning event for persistent agent memory"""

    # Unique identifier
    event_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)

    # Agent Information
    agent_id = models.CharField(max_length=100, db_index=True)
    agent_name = models.CharField(max_length=200)
    agent_specialization = models.CharField(max_length=100)

    # Learning Signal Information
    signal_id = models.CharField(max_length=100, db_index=True)
    signal_type = models.CharField(max_length=50)  # 'market_data', 'social_trend', 'news', etc.
    signal_strength = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])

    # Source Information
    source_spider = models.CharField(max_length=100)
    source_api = models.CharField(max_length=50)  # 'bluesky', 'reddit', 'polygon'
    source_url = models.URLField(blank=True)

    # Learning Content
    raw_content = models.JSONField()  # Original data from spider
    processed_content = models.JSONField()  # Processed learning signal
    learned_insights = models.JSONField()  # What the agent actually learned

    # Learning Metadata
    learning_type = models.CharField(max_length=50)  # 'knowledge_update', 'skill_improvement', 'pattern_recognition'
    confidence_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    quality_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])

    # Timing
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    processing_time_ms = models.FloatField(default=0.0)

    # Relationships
    related_events = models.ManyToManyField('self', blank=True, symmetrical=False)

    class Meta:
        app_label = 'backend'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['agent_id', '-timestamp']),
            models.Index(fields=['signal_type', '-timestamp']),
            models.Index(fields=['source_api', '-timestamp']),
            models.Index(fields=['confidence_score']),
        ]

    def __str__(self):
        return f"Learning({self.agent_id}: {self.signal_type} at {self.timestamp})"


class LearningDocument(models.Model):
    """Auto-generated documents from learning events"""

    DOCUMENT_TYPES = [
        ('insight', 'Agent Insight'),
        ('summary', 'Learning Summary'),
        ('analysis', 'Data Analysis'),
        ('prediction', 'Prediction Report'),
        ('recommendation', 'Recommendation'),
        ('knowledge_synthesis', 'Knowledge Synthesis'),
    ]

    # Document Identity
    document_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    title = models.CharField(max_length=300)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)

    # Agent Information
    agent_id = models.CharField(max_length=100, db_index=True)
    agent_name = models.CharField(max_length=200)

    # Document Content
    content = models.TextField()
    summary = models.TextField()
    key_insights = models.JSONField(default=list)  # List of key insights
    confidence_level = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])

    # Source Learning Events
    source_events = models.ManyToManyField(AgentLearningEvent, related_name='generated_documents')
    event_count = models.IntegerField(default=0)

    # Metadata
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    word_count = models.IntegerField(default=0)

    # Tags and Categories
    tags = models.JSONField(default=list)
    categories = models.JSONField(default=list)

    class Meta:
        app_label = 'backend'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agent_id', '-created_at']),
            models.Index(fields=['document_type', '-created_at']),
            models.Index(fields=['confidence_level']),
        ]

    def __str__(self):
        return f"Document({self.agent_id}: {self.title})"


class AgentKnowledgeBase(models.Model):
    """Persistent knowledge base for each agent"""

    # Agent Identity
    agent_id = models.CharField(max_length=100, unique=True, db_index=True)
    agent_name = models.CharField(max_length=200)
    agent_specialization = models.CharField(max_length=100)

    # Knowledge Domains
    primary_domains = models.JSONField(default=list)  # ['financial', 'social', etc.]
    secondary_domains = models.JSONField(default=list)

    # Knowledge Statistics
    total_learning_events = models.IntegerField(default=0)
    total_documents_generated = models.IntegerField(default=0)
    total_insights = models.IntegerField(default=0)

    # Knowledge Items (structured knowledge)
    financial_knowledge = models.JSONField(default=dict)  # Market patterns, trends, etc.
    social_knowledge = models.JSONField(default=dict)    # Social trends, engagement patterns
    technical_knowledge = models.JSONField(default=dict)  # Technical insights, innovations
    general_knowledge = models.JSONField(default=dict)    # General insights

    # Learning Performance
    learning_accuracy = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    knowledge_retention_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    avg_confidence_score = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(1)])

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    last_learning_event = models.DateTimeField(blank=True, null=True)

    # Learning Configuration
    learning_rate = models.FloatField(default=0.1, validators=[MinValueValidator(0), MaxValueValidator(1)])
    curiosity_factor = models.FloatField(default=0.5, validators=[MinValueValidator(0), MaxValueValidator(1)])

    class Meta:
        app_label = 'backend'
        indexes = [
            models.Index(fields=['agent_specialization']),
            models.Index(fields=['last_updated']),
            models.Index(fields=['learning_accuracy']),
        ]

    def __str__(self):
        return f"KnowledgeBase({self.agent_id}: {self.total_learning_events} events)"


class LearningEmbedding(models.Model):
    """Vector embeddings of learned content for semantic search"""

    # Embedding Identity
    embedding_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)

    # Source Information
    learning_event = models.OneToOneField(AgentLearningEvent, on_delete=models.CASCADE, related_name='embedding')
    document = models.ForeignKey(LearningDocument, on_delete=models.CASCADE, blank=True, null=True, related_name='embeddings')

    # Content Information
    content_text = models.TextField()
    content_hash = models.CharField(max_length=64, db_index=True)  # SHA-256 hash
    content_type = models.CharField(max_length=50)  # 'learning_event', 'document', 'insight'

    # Embedding Data
    embedding_vector = models.JSONField()  # Vector representation
    embedding_model = models.CharField(max_length=100, default='text-embedding-3-small')
    vector_dimensions = models.IntegerField(default=1536)

    # Agent Context
    agent_id = models.CharField(max_length=100, db_index=True)
    agent_specialization = models.CharField(max_length=100)

    # Metadata
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    token_count = models.IntegerField(default=0)
    quality_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])

    class Meta:
        app_label = 'backend'
        unique_together = ['content_hash', 'embedding_model']
        indexes = [
            models.Index(fields=['agent_id', '-created_at']),
            models.Index(fields=['content_type']),
            models.Index(fields=['quality_score']),
        ]

    def __str__(self):
        return f"Embedding({self.agent_id}: {self.content_type})"


class AgentLearningSession(models.Model):
    """Track learning sessions and batch processing"""

    # Session Identity
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    session_name = models.CharField(max_length=200)

    # Session Scope
    agents_involved = models.JSONField(default=list)  # List of agent IDs
    signal_types_processed = models.JSONField(default=list)
    data_sources = models.JSONField(default=list)  # ['bluesky', 'reddit', 'polygon']

    # Session Statistics
    events_processed = models.IntegerField(default=0)
    documents_generated = models.IntegerField(default=0)
    embeddings_created = models.IntegerField(default=0)

    # Performance Metrics
    avg_processing_time = models.FloatField(default=0.0)
    avg_confidence_score = models.FloatField(default=0.0)
    success_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(1)])

    # Timing
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(blank=True, null=True)
    duration_seconds = models.FloatField(default=0.0)

    # Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('paused', 'Paused'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        app_label = 'backend'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['status', '-started_at']),
            models.Index(fields=['success_rate']),
        ]

    def __str__(self):
        return f"Session({self.session_name}: {self.status})"


class LearningInsight(models.Model):
    """High-level insights generated from multiple learning events"""

    INSIGHT_TYPES = [
        ('pattern', 'Pattern Recognition'),
        ('trend', 'Trend Analysis'),
        ('correlation', 'Correlation Discovery'),
        ('anomaly', 'Anomaly Detection'),
        ('prediction', 'Predictive Insight'),
        ('recommendation', 'Strategic Recommendation'),
    ]

    # Insight Identity
    insight_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    title = models.CharField(max_length=300)
    insight_type = models.CharField(max_length=50, choices=INSIGHT_TYPES)

    # Insight Content
    description = models.TextField()
    key_findings = models.JSONField(default=list)
    implications = models.JSONField(default=list)
    recommended_actions = models.JSONField(default=list)

    # Source Data
    contributing_agents = models.JSONField(default=list)  # List of agent IDs
    source_events = models.ManyToManyField(AgentLearningEvent, related_name='insights')
    data_sources = models.JSONField(default=list)

    # Confidence and Impact
    confidence_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    impact_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    urgency_level = models.CharField(max_length=20, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')])

    # Timing and Relevance
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    relevant_until = models.DateTimeField(blank=True, null=True)

    # Validation
    is_validated = models.BooleanField(default=False)
    validation_score = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(1)])

    class Meta:
        app_label = 'backend'
        ordering = ['-impact_score', '-created_at']
        indexes = [
            models.Index(fields=['insight_type', '-created_at']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['impact_score']),
            models.Index(fields=['urgency_level']),
        ]

    def __str__(self):
        return f"Insight({self.title}: {self.insight_type})"