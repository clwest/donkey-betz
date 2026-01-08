"""
Conversation and memory-related models
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

# Session 729: Import pgvector for native vector operations
try:
    from pgvector.django import VectorField, HnswIndex
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False
    VectorField = None
    HnswIndex = None


class ConversationMemory(models.Model):
    """
    Store conversation history for personalization.
    Session 729: Added pgvector embedding field for semantic search.
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='conversation_memories')
    message = models.TextField()
    response = models.TextField()
    agents_used = models.JSONField(default=list)
    intent = models.CharField(max_length=100, blank=True)
    success = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Session 729: pgvector embedding for fast semantic search
    # Dimension 1536 matches OpenAI text-embedding-3-small
    embedding = VectorField(
        dimensions=1536,
        null=True,
        blank=True,
        help_text="Vector embedding for semantic search (pgvector)"
    ) if HAS_PGVECTOR else models.JSONField(
        null=True,
        blank=True,
        help_text="Vector embedding for semantic search (JSON fallback)"
    )

    class Meta:
        db_table = 'core_conversation_memory'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            # Session 729: HNSW index for fast approximate nearest neighbor search
            # Only works with pgvector extension
        ]
        # Note: HNSW index added via migration for pgvector

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"


class ChatConversation(models.Model):
    """
    Model for storing chat conversations separately from document embeddings
    Fixes the confusion between chat memory and RAG document embeddings
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    conversation_id = models.CharField(max_length=255, db_index=True)
    user_message = models.TextField()
    assistant_response = models.TextField()

    # Context and metadata
    context_used = models.JSONField(default=dict)  # RAG context if any
    metadata = models.JSONField(default=dict)

    # Performance metrics
    response_time_ms = models.IntegerField(null=True, blank=True)
    model_used = models.CharField(max_length=100, blank=True)
    provider_used = models.CharField(max_length=50, blank=True)

    # Agent execution info
    agents_used = models.JSONField(default=list)
    agent_results = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_conversations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['conversation_id']),
        ]
        verbose_name = 'Chat Conversation'
        verbose_name_plural = 'Chat Conversations'

    def __str__(self):
        return f"{self.user.username}: {self.user_message[:50]}..."


class UserMemoryContext(models.Model):
    """
    Contextual memory storage for user interactions.
    Links profile data with specific memories for better retrieval.
    """

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='memory_contexts')
    profile = models.ForeignKey('EnhancedUserProfile', on_delete=models.CASCADE)

    memory_type = models.CharField(
        max_length=50,
        choices=[
            ('decision', 'Decision Made'),
            ('preference', 'Preference Stated'),
            ('feedback', 'Feedback Given'),
            ('instruction', 'Instruction Provided'),
            ('context', 'Context Shared'),
            ('goal', 'Goal Mentioned'),
            ('constraint', 'Constraint Identified'),
            ('interaction', 'User Interaction'),
            ('agent_action', 'Agent Action'),
            ('agent_learning', 'Agent Learning'),
            ('agent_recommendation', 'Agent Recommendation'),
            ('cross_agent', 'Cross-Agent Communication'),
            ('system_insight', 'System Insight'),
            ('agent_usage', 'Agent Usage'),
            ('skill', 'Skill Identified'),
            ('project', 'Project Information'),
            ('learning', 'System Learning'),
            ('pattern', 'Pattern Detected')
        ]
    )

    content = models.TextField()
    source = models.CharField(
        max_length=100,
        default='assistant',
        help_text="Source of memory (e.g., 'assistant', 'agent:JobMatcher')"
    )

    related_project = models.CharField(max_length=200, blank=True)
    related_goal = models.CharField(max_length=200, blank=True)

    importance = models.IntegerField(
        default=5,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )

    tags = models.JSONField(default=list)

    context_metadata = models.JSONField(
        default=dict,
        help_text="Additional context like mood, energy level, time of day"
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this memory becomes less relevant"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    accessed_count = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-importance', '-created_at']
        indexes = [
            models.Index(fields=['user', 'memory_type', '-created_at']),
            models.Index(fields=['user', '-importance']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.memory_type}: {self.content[:50]}..."
