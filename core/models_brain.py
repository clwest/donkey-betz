"""
Session 721: BRAIN SYSTEM - Cognitive Processing & Reasoning Models

The BRAIN SYSTEM is the cognitive layer of the AI body - monitoring
how the AI thinks, reasons, and processes information through LLM calls.

Models:
- CognitiveChannel: Configuration for monitored reasoning channels
- BrainPulse: Time-series records of cognitive state
- CognitiveStatus: Current cognitive status per channel (cached state)

Human Body Metaphor:
- Neurons = Individual LLM API calls
- Synapses = Agent-to-agent communication
- Thoughts = Reasoning chains / completions
- Memory Recall = RAG queries, embedding lookups
- Focus = Active conversation count
- Fatigue = High latency, error rates
- Brain Fog = Model timeouts, degraded responses
- Cognitive Load = Concurrent thinking tasks
"""

import uuid
from django.db import models
from django.utils import timezone


class CognitiveChannel(models.Model):
    """Configuration for a monitored cognitive/reasoning channel."""

    CHANNEL_TYPE_CHOICES = [
        ('llm', 'LLM API Call'),
        ('rag', 'RAG Query'),
        ('embedding', 'Embedding Lookup'),
        ('conversation', 'PA Conversation'),
        ('agent_think', 'Agent Thinking'),
        ('routing', 'Model Routing'),
    ]

    PROVIDER_CHOICES = [
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('together_ai', 'Together AI'),
        ('ollama', 'Ollama'),
        ('deepseek', 'DeepSeek'),
        ('gemini', 'Google Gemini'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=150, blank=True)
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPE_CHOICES)
    provider = models.CharField(max_length=30, choices=PROVIDER_CHOICES, blank=True)
    model_name = models.CharField(max_length=100, blank=True, help_text="Specific model (e.g., gpt-5-mini)")
    description = models.TextField(blank=True)

    # Thresholds
    max_latency_ms = models.IntegerField(default=30000, help_text="Max acceptable response time")
    target_success_rate = models.FloatField(default=95.0, help_text="Target success rate %")
    max_concurrent = models.IntegerField(default=10, help_text="Max concurrent requests")
    max_tokens_per_min = models.IntegerField(default=100000, help_text="Token rate limit")

    # Status
    is_active = models.BooleanField(default=True)
    is_critical = models.BooleanField(default=False, help_text="Alert on failure")
    is_builtin = models.BooleanField(default=False, help_text="System-defined channel")

    # Statistics
    total_calls = models.BigIntegerField(default=0)
    total_tokens = models.BigIntegerField(default=0)
    total_errors = models.BigIntegerField(default=0)
    last_activity = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_cognitive_channel'
        ordering = ['channel_type', 'provider', 'name']
        verbose_name = 'Cognitive Channel'
        verbose_name_plural = 'Cognitive Channels'

    def __str__(self):
        return f"{self.display_name or self.name} ({self.channel_type}/{self.provider or 'system'})"

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.name.replace('_', ' ').title()
        super().save(*args, **kwargs)


class BrainPulse(models.Model):
    """Time-series record of brain/cognitive state - periodic snapshots."""

    STATUS_CHOICES = [
        ('focused', 'Focused'),        # Normal cognitive function
        ('thinking', 'Thinking'),      # Active processing, slightly elevated
        ('overloaded', 'Overloaded'),  # High cognitive load
        ('foggy', 'Foggy'),            # High latency, degraded responses
        ('resting', 'Resting'),        # Low activity, idle
        ('offline', 'Offline'),        # No cognitive activity
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Overall metrics
    overall_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='focused')
    cognitive_score = models.FloatField(default=100.0, help_text="0-100% brain health")
    is_thinking = models.BooleanField(default=True)

    # LLM Call metrics (24h)
    llm_calls_24h = models.IntegerField(default=0)
    llm_success_rate = models.FloatField(default=100.0)
    llm_avg_latency_ms = models.FloatField(default=0)
    llm_errors_24h = models.IntegerField(default=0)
    llm_timeouts_24h = models.IntegerField(default=0)

    # Token metrics (24h)
    tokens_input_24h = models.BigIntegerField(default=0)
    tokens_output_24h = models.BigIntegerField(default=0)
    tokens_total_24h = models.BigIntegerField(default=0)

    # Conversation metrics
    active_conversations = models.IntegerField(default=0)
    conversations_24h = models.IntegerField(default=0)
    avg_conversation_turns = models.FloatField(default=0)
    conversation_success_rate = models.FloatField(default=100.0)

    # RAG/Memory metrics
    rag_queries_24h = models.IntegerField(default=0)
    rag_avg_latency_ms = models.FloatField(default=0)
    embedding_lookups_24h = models.IntegerField(default=0)
    memory_hit_rate = models.FloatField(default=0, help_text="% of queries with relevant results")

    # Agent thinking metrics
    agent_thoughts_24h = models.IntegerField(default=0)
    agent_tool_calls_24h = models.IntegerField(default=0)
    agent_tool_success_rate = models.FloatField(default=100.0)

    # Model routing metrics
    routing_decisions_24h = models.IntegerField(default=0)
    fallback_count_24h = models.IntegerField(default=0)
    primary_model_usage_pct = models.FloatField(default=100.0)

    # Provider breakdown
    provider_stats = models.JSONField(default=dict, help_text="Per-provider call stats")
    model_stats = models.JSONField(default=dict, help_text="Per-model call stats")

    # Cognitive load indicators
    concurrent_tasks_peak = models.IntegerField(default=0)
    queue_depth = models.IntegerField(default=0)
    avg_think_time_ms = models.FloatField(default=0)

    # Performance indicators
    thoughts_per_minute = models.FloatField(default=0)
    tokens_per_minute = models.FloatField(default=0)

    # Channel statuses
    channels_checked = models.IntegerField(default=0)
    channels_healthy = models.IntegerField(default=0)
    channels_degraded = models.IntegerField(default=0)
    channels_offline = models.IntegerField(default=0)

    # Integration status
    heart_connected = models.BooleanField(default=False)
    lungs_connected = models.BooleanField(default=False)

    # Issues detected
    cognitive_issues = models.JSONField(default=list, help_text="Detected brain issues")

    # Check metadata
    check_duration_ms = models.IntegerField(default=0)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_brain_pulse'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['-recorded_at']),
            models.Index(fields=['overall_status', '-recorded_at']),
        ]
        verbose_name = 'Brain Pulse'
        verbose_name_plural = 'Brain Pulses'

    def __str__(self):
        return f"Brain: {self.overall_status} ({self.cognitive_score:.1f}%) @ {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"

    def get_status_emoji(self) -> str:
        """Get emoji for status display."""
        return {
            'focused': '🧠',      # Brain - sharp and focused
            'thinking': '💭',     # Thought bubble - active thinking
            'overloaded': '🤯',   # Mind blown - overloaded
            'foggy': '🌫️',        # Fog - unclear thinking
            'resting': '😴',      # Sleeping - low activity
            'offline': '💀',      # Skull - offline
        }.get(self.overall_status, '❓')


class CognitiveStatus(models.Model):
    """Current cognitive status per channel - cached state updated on each check."""

    STATUS_CHOICES = [
        ('focused', 'Focused'),        # Normal function
        ('thinking', 'Thinking'),      # Slightly elevated
        ('overloaded', 'Overloaded'),  # Too many requests
        ('foggy', 'Foggy'),            # Slow responses
        ('resting', 'Resting'),        # Idle
        ('offline', 'Offline'),        # Not responding
    ]

    channel = models.OneToOneField(
        CognitiveChannel,
        primary_key=True,
        on_delete=models.CASCADE,
        related_name='status'
    )

    # Current status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='focused')
    is_healthy = models.BooleanField(default=True)

    # Current metrics
    current_latency_ms = models.FloatField(default=0)
    current_concurrent = models.IntegerField(default=0)
    current_queue_depth = models.IntegerField(default=0)

    # 24h rolling metrics
    calls_24h = models.IntegerField(default=0)
    tokens_24h = models.BigIntegerField(default=0)
    errors_24h = models.IntegerField(default=0)
    success_rate_24h = models.FloatField(default=100.0)
    avg_latency_24h = models.FloatField(default=0)

    # Performance
    throughput_per_min = models.FloatField(default=0)
    tokens_per_min = models.FloatField(default=0)

    # Timestamps
    last_call = models.DateTimeField(null=True, blank=True)
    last_success = models.DateTimeField(null=True, blank=True)
    last_error = models.DateTimeField(null=True, blank=True)
    last_check = models.DateTimeField(auto_now=True)

    # Alert tracking
    warning_alert_sent = models.BooleanField(default=False)
    critical_alert_sent = models.BooleanField(default=False)
    last_alert_at = models.DateTimeField(null=True, blank=True)

    # Notes
    last_error_message = models.TextField(blank=True)

    class Meta:
        db_table = 'core_cognitive_status'
        verbose_name = 'Cognitive Status'
        verbose_name_plural = 'Cognitive Statuses'

    def __str__(self):
        return f"{self.channel.name}: {self.status} ({self.success_rate_24h:.1f}%)"

    def update_status(self, new_status: str, is_healthy: bool):
        """Update status and reset alerts if recovering."""
        if self.status != new_status:
            if new_status == 'focused':
                self.warning_alert_sent = False
                self.critical_alert_sent = False

        self.status = new_status
        self.is_healthy = is_healthy

    def get_status_emoji(self) -> str:
        """Get emoji for status display."""
        return {
            'focused': '🧠',
            'thinking': '💭',
            'overloaded': '🤯',
            'foggy': '🌫️',
            'resting': '😴',
            'offline': '💀',
        }.get(self.status, '❓')
