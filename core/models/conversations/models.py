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
    Model for storing chat conversations separately from document embeddings.

    Session 455: Extended for cross-platform session continuity (web <-> Discord)
    - Tracks which platform originated the conversation
    - Stores Discord-specific fields for unlinked users
    - Enables session resumption across platforms
    """
    # User association - nullable for Discord users who haven't linked accounts
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Linked user (null for unlinked Discord users)"
    )
    conversation_id = models.CharField(max_length=255, db_index=True)
    user_message = models.TextField()
    assistant_response = models.TextField()

    # Session 1074: Actor source — who posted this message
    SOURCE_CHOICES = [
        ('web', 'Web App'),
        ('mobile', 'Mobile App'),
        ('discord', 'Discord'),
        ('api', 'API'),
        ('claude-code', 'Claude Code'),
        ('pa', 'Personal Assistant'),
    ]
    source = models.CharField(
        max_length=30,
        choices=SOURCE_CHOICES,
        default='web',
        db_index=True,
        help_text="Actor who posted this message (user via web/mobile, claude-code, pa)"
    )

    # Session 455: Cross-platform tracking
    PLATFORM_CHOICES = [
        ('web', 'Web App'),
        ('discord', 'Discord'),
        ('api', 'API'),
        ('mobile', 'Mobile App'),
    ]
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        default='web',
        db_index=True,
        help_text="Platform where this message originated"
    )

    # Discord-specific fields (for conversations from unlinked Discord users)
    discord_user_id = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        db_index=True,
        help_text="Discord user ID (for unlinked users or reference)"
    )
    discord_channel_id = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        help_text="Discord channel where conversation occurred"
    )
    discord_guild_id = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        help_text="Discord server (guild) ID"
    )

    # Session management
    session_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Auto-generated title for the conversation session"
    )
    session_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this session is still active/resumable"
    )

    # Workspace binding — conversations started in a workspace stay bound to it
    workspace = models.ForeignKey(
        'core.ProjectWorkspace',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_conversations',
        db_index=True,
        help_text="Workspace this conversation is bound to (set when started from a workspace)"
    )

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
            models.Index(fields=['platform', '-created_at']),
            models.Index(fields=['discord_user_id', '-created_at']),
            models.Index(fields=['session_active', '-created_at']),
        ]
        verbose_name = 'Chat Conversation'
        verbose_name_plural = 'Chat Conversations'

    def __str__(self):
        platform_indicator = f"[{self.platform}]" if self.platform != 'web' else ""
        user_str = self.user.username if self.user else f"Discord:{self.discord_user_id}"
        return f"{platform_indicator} {user_str}: {self.user_message[:50]}..."

    @classmethod
    def get_or_create_session(cls, user=None, discord_user_id=None, platform='web'):
        """
        Get the active session for a user or create a new one.

        Returns (conversation_id, is_new_session)
        """
        import uuid

        # Build filter for finding existing active session
        filters = {'session_active': True}
        if user:
            filters['user'] = user
        elif discord_user_id:
            filters['discord_user_id'] = discord_user_id
            filters['user__isnull'] = True
        else:
            # No identifier - create new session
            return str(uuid.uuid4()), True

        # Look for recent active session (within last 24 hours)
        from django.utils import timezone
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(hours=24)

        recent = cls.objects.filter(
            **filters,
            created_at__gte=cutoff
        ).order_by('-created_at').first()

        if recent:
            return recent.conversation_id, False

        return str(uuid.uuid4()), True

    @classmethod
    def get_session_history(cls, conversation_id, limit=20):
        """Get conversation history for a session."""
        return list(cls.objects.filter(
            conversation_id=conversation_id
        ).order_by('created_at')[:limit].values(
            'user_message', 'assistant_response', 'platform',
            'created_at', 'agents_used'
        ))

    def generate_session_title(self):
        """Auto-generate a title based on the first message."""
        if self.session_title:
            return self.session_title

        # Take first 50 chars of message, clean up
        title = self.user_message[:50]
        if len(self.user_message) > 50:
            title += "..."

        # Update all messages in this session with the title
        ChatConversation.objects.filter(
            conversation_id=self.conversation_id
        ).update(session_title=title)

        self.session_title = title
        return title


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
