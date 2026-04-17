"""
Unified System Models - The Complete AI Ecosystem
These models represent ALL agents, advisors, and system components
"""

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json
import uuid
import logging
import warnings

# Session 1084 round 51: get_openai_client is imported lazily INSIDE each
# method that needs it (5 call sites) to avoid a circular import chain:
# models_unified_system → openai_client_factory → ... → back here.
# The factory's own imports are fine; the cycle comes from Django's
# services package loading order during startup.

logger = logging.getLogger(__name__)

# Session 730: Import pgvector for native vector operations
try:
    from pgvector.django import VectorField
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False
    VectorField = None

# Import base models
from .models.base.models import UnifiedBaseModel

class AgentCategory(models.Model):
    """Categories for organizing agents"""
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=10)
    description = models.TextField(blank=True)

    class Meta:
        app_label = 'core'
        verbose_name_plural = "Agent Categories"

    def __str__(self):
        return self.name


class AgentControlEntry(models.Model):
    """
    Session 1080: Centralized blocked/enabled agent control.
    Replaces hardcoded frozensets in tasks.py, agent_router.py, tool_dispatcher.py.
    Keyed by agent_name (same string as AGENT_MAP keys).
    """
    agent_name = models.CharField(max_length=100, unique=True, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=[('blocked', 'Blocked'), ('enabled', 'Enabled')],
        default='enabled',
    )
    reason = models.CharField(max_length=255, blank=True, default='')
    blocked_at = models.DateTimeField(null=True, blank=True)
    blocked_by = models.CharField(
        max_length=100, blank=True, default='',
        help_text="Who blocked: 'system', 'rigby', 'claude-code', etc."
    )
    ttl_hours = models.IntegerField(
        null=True, blank=True,
        help_text="Auto-unblock after N hours (null = permanent)"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Agent Control Entry'
        verbose_name_plural = 'Agent Control Entries'

    def __str__(self):
        return f"{self.agent_name}: {self.status}"

    def save(self, *args, **kwargs):
        """Session 1092: Auto-populate ``blocked_at`` when an entry first
        transitions into the ``blocked`` state.

        Forensics relied on ``blocked_at`` to answer "when was this block
        originally set?" but writers (admin updates, ad-hoc shell calls)
        often only flipped ``status`` and forgot the timestamp — leaving
        rows like AudioAgent with ``status='blocked', blocked_at=None``,
        which broke CTOAgent's reliability audit.

        Behavior contract (locked with Rigby in Session 1092):
        - Populate ``blocked_at`` ONLY on transition non-blocked → blocked.
        - Do NOT overwrite an existing ``blocked_at`` value (preserves
          historical first-block timestamp through repeated re-blocks).
        - On blocked → enabled, ``blocked_at`` is left as historical.
          Use ``updated_at`` for the unblock event.
        """
        from django.utils import timezone

        if self.status == 'blocked' and self.blocked_at is None:
            self.blocked_at = timezone.now()
        super().save(*args, **kwargs)

    @classmethod
    def get_blocked_names(cls) -> frozenset:
        """Return frozenset of currently blocked agent names, respecting TTL."""
        from django.utils import timezone
        try:
            blocked_qs = cls.objects.filter(status='blocked')
            names = set()
            now = timezone.now()
            for entry in blocked_qs:
                if entry.ttl_hours and entry.blocked_at:
                    elapsed = (now - entry.blocked_at).total_seconds() / 3600
                    if elapsed > entry.ttl_hours:
                        entry.status = 'enabled'
                        entry.reason = f'TTL expired ({entry.ttl_hours}h)'
                        entry.save(update_fields=['status', 'reason', 'updated_at'])
                        continue
                names.add(entry.agent_name)
            return frozenset(names)
        except Exception:
            # Fallback during migrations or if table doesn't exist
            return frozenset({'CodeGeneratorAgent'})

    @classmethod
    def is_blocked(cls, agent_name: str) -> bool:
        return agent_name in cls.get_blocked_names()


class ActivePriority(models.Model):
    """
    Session 1086 PR 1: Rigby's proactive priority-aware routing — the model layer.

    Each row is a "current priority" that the platform should optimize around
    right now (e.g. "Platform hardening", "Newsletter Issue 2 ship",
    "Tier 5 factory audit"). Beat tasks and autonomous dispatches will check
    in with the active priority set BEFORE they run, and mismatched work gets
    throttled into a low-concurrency semaphore instead of competing for the
    same CPU/LLM budget as matched work.

    This PR (PR 1 of 3) delivers only the **schema + PA tool + data migration**.
    No behavior change. The matching logic lives in ``core/services/priority/``
    in PR 2, and ``agent_router.route()`` integration + the semaphore land in
    PR 3. See initiative ``2dcb79d7-6f2b-4e67-a366-a54e96d7870f``.

    Design contract (locked with Rigby in the Session 1086 design review):

    - **Fail-open everywhere.** No active priorities → route normally. All
      expired → route normally. Matching helper raises → route normally.
      This model must never cause a production outage.
    - **Deprioritize, don't drop.** Mismatched work still executes; it just
      queues behind matched work. The model knows nothing about queues —
      that lives in PR 3. This class is pure state.
    - **Matching precedence (implemented in PR 2, documented here as the
      contract):** whitelist hit → blacklist hit → tag overlap → opt-in
      keyword match → fail-open MATCH. See ``enable_keyword_match`` below.
    - **TTL bounds:** default 24h, minimum 10min (anti-flap), maximum 7 days
      (anti-zombie). Enforced in the PA tool, not here — the model accepts
      any ``expires_at``.
    - **Extension point for future governance work:** the JSONField lists
      (``tags``, ``agent_whitelist``, ``agent_blacklist``) can absorb new
      matching modes without a schema migration. The future
      ``enable_beat_tasks`` / ``agent_family_enable`` governance features
      flagged in Rigby's Q3 response will reuse ``tags`` as the primary key.
    """

    STATUS_ACTIVE = 'active'
    STATUS_ARCHIVED = 'archived'
    STATUS_EXPIRED = 'expired'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_ARCHIVED, 'Archived'),
        (STATUS_EXPIRED, 'Expired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Human-readable identity
    name = models.CharField(
        max_length=120,
        help_text="Short human label, e.g. 'Platform hardening (Ops/Drift)'.",
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text="Free-form intent. What is this priority trying to accomplish?",
    )

    # Matching inputs (consumed by PriorityRouter in PR 2)
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "List of tag strings. Matched against derived agent tags "
            "(agent_name + Agent.category.slug + AGENT_TAG_OVERRIDES dict). "
            "Primary automatic matching mechanism."
        ),
    )
    agent_whitelist = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "List of exact agent_name strings that ALWAYS match this priority "
            "regardless of tags. Highest precedence in the match algorithm."
        ),
    )
    agent_blacklist = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "List of exact agent_name strings that NEVER match this priority "
            "even if tags overlap. Forces them into the mismatched lane."
        ),
    )
    enable_keyword_match = models.BooleanField(
        default=False,
        help_text=(
            "Opt-in substring keyword match against agent_name + task. "
            "Off by default per Rigby's design review — keyword matching "
            "creates false positives ('audit' matches everything), so only "
            "enable this when the tag list is explicitly narrow."
        ),
    )

    # Session 1088: Per-mission governance controls
    enabled = models.BooleanField(
        default=True,
        help_text=(
            "Per-mission pause toggle. When False, the governor treats this "
            "mission as if it doesn't exist — agents that only match this "
            "mission will be skipped. Allows pausing a mission without "
            "archiving it (preserves config for re-enable)."
        ),
    )
    max_daily_executions = models.IntegerField(
        null=True,
        blank=True,
        help_text=(
            "Optional daily execution budget for this mission. When set, "
            "the governor tracks how many dispatches have been allowed today "
            "for agents matching this mission. Once the cap is reached, "
            "further dispatches are skipped until midnight reset. "
            "NULL means unlimited."
        ),
    )

    # Ranking and ownership
    priority_rank = models.IntegerField(
        default=100,
        help_text=(
            "Lower = higher priority. Multiple priorities can coexist; the "
            "router treats any active match as a MATCH. Rank is for future "
            "tie-breaking in Option B (dedicated queue) routing."
        ),
    )
    owner = models.CharField(
        max_length=60,
        default='rigby',
        help_text="Who owns this priority: 'rigby', 'chris', 'system'.",
    )

    # Status + lifecycle
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        db_index=True,
    )
    activated_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the priority was first created and made active.",
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "Optional TTL expiry. If set and in the past, "
            "get_active_priorities() auto-transitions status → expired."
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Active Priority'
        verbose_name_plural = 'Active Priorities'
        ordering = ['priority_rank', '-activated_at']

    def __str__(self):
        return f"{self.name} ({self.status}, rank={self.priority_rank})"

    @property
    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        from django.utils import timezone
        return self.expires_at <= timezone.now()

    # Rate-limit the fail-open error log so we can SEE silent DB failures
    # without flooding logs when the whole table is unreachable. Mirrors the
    # pattern we want for PriorityRouter in PR 2. Module-level state keyed
    # on the class so subclasses don't share throttles.
    _last_fail_open_log_ts: float = 0.0

    @classmethod
    def get_active_priorities(cls) -> list:
        """
        Return a list of currently-active priority dicts, auto-expiring any
        TTL-expired rows as a side effect. Fail-open on DB errors (returns
        empty list, which the router treats as "no priorities → match all").

        Mirrors ``AgentControlEntry.get_blocked_names()``: same TTL pattern,
        same update-on-read semantics, same fail-open fallback. PR 2's
        PriorityRouter will layer a 60s in-process cache on top of this.

        Each returned dict contains the keys PriorityRouter needs for
        matching (id, name, tags, agent_whitelist, agent_blacklist,
        enable_keyword_match, priority_rank). Full row access is still
        available via the ORM for tools that need it.

        Fail-open observability: exceptions are logged via ``logger.exception``
        but rate-limited to once every 60 seconds to prevent log flooding in
        a total-DB-outage scenario. This addresses Rigby's Session 1086 review
        comment: fail-open without any observability can mask real errors.
        """
        import time
        from django.utils import timezone
        try:
            now = timezone.now()
            active = []
            for entry in cls.objects.filter(status=cls.STATUS_ACTIVE):
                if entry.expires_at and entry.expires_at <= now:
                    entry.status = cls.STATUS_EXPIRED
                    entry.save(update_fields=['status', 'updated_at'])
                    continue
                # Session 1088: Skip disabled missions — they still exist
                # for config preservation but don't participate in matching.
                if not entry.enabled:
                    continue
                active.append({
                    'id': str(entry.id),
                    'name': entry.name,
                    'tags': list(entry.tags or []),
                    'agent_whitelist': list(entry.agent_whitelist or []),
                    'agent_blacklist': list(entry.agent_blacklist or []),
                    'enable_keyword_match': entry.enable_keyword_match,
                    'priority_rank': entry.priority_rank,
                    'expires_at': entry.expires_at.isoformat() if entry.expires_at else None,
                    'enabled': entry.enabled,
                    'max_daily_executions': entry.max_daily_executions,
                })
            return active
        except Exception:
            # DB unavailable / table missing / migration in flight → fail open
            now_ts = time.monotonic()
            if now_ts - cls._last_fail_open_log_ts > 60.0:
                cls._last_fail_open_log_ts = now_ts
                try:
                    import logging
                    logging.getLogger(__name__).exception(
                        "ActivePriority.get_active_priorities() fail-open: "
                        "DB error suppressed, routing without priorities "
                        "until next successful read"
                    )
                except Exception:
                    pass  # logging must never break fail-open
            return []


class Agent(models.Model):
    """
    Represents one of the 149 specialized AI agents in the system
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    agent_type = models.CharField(max_length=50)
    category = models.ForeignKey(AgentCategory, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    specialization = models.CharField(max_length=100)

    # Capabilities
    capabilities = models.JSONField(default=dict)
    effectiveness_score = models.IntegerField(default=85)  # 0-100

    # Status
    is_active = models.BooleanField(default=True)
    last_active = models.DateTimeField(auto_now=True)

    # User assignments
    user_assignments = models.ManyToManyField(settings.AUTH_USER_MODEL, through='AgentAssignment', related_name='assigned_agents')

    # Metrics
    total_executions = models.IntegerField(default=0)
    successful_executions = models.IntegerField(default=0)
    total_revenue_generated = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    # Integration
    api_endpoint = models.CharField(max_length=200, blank=True)
    webhook_url = models.CharField(max_length=200, blank=True)

    # Voice - ElevenLabs voice for TTS output (Session 926)
    voice_id = models.CharField(
        max_length=100, blank=True, default='',
        help_text="ElevenLabs voice ID or name (Rachel, Antoni, etc.)"
    )

    # Spider connections - what data sources feed this agent
    spider_categories = models.ManyToManyField(
        'SpiderCategory',
        through='AgentSpiderConnection',
        related_name='agents',
        blank=True,
        help_text="Spider categories that feed data to this agent"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def success_rate(self):
        if self.total_executions == 0:
            return 0
        return (self.successful_executions / self.total_executions) * 100

    @property
    def knowledge_count(self):
        """Count of knowledge sources this agent has"""
        return self.knowledge_sources.filter(is_active=True).count()

    @property
    def connected_spider_count(self):
        """Count of spider categories feeding this agent"""
        return self.spider_connections.count()

    def get_knowledge_summary(self):
        """Get a summary of this agent's knowledge sources"""
        knowledge = self.knowledge_sources.filter(is_active=True)
        return {
            'total_count': knowledge.count(),
            'by_type': {
                k['knowledge_type']: k['count']
                for k in knowledge.values('knowledge_type').annotate(count=models.Count('id'))
            },
            'avg_confidence': knowledge.aggregate(avg=models.Avg('confidence_score'))['avg'] or 0,
            'data_points': knowledge.aggregate(total=models.Sum('data_points_count'))['total'] or 0,
        }

    def __str__(self):
        return f"{self.name} ({self.agent_type})"

    class Meta:
        app_label = 'core'
        ordering = ['-effectiveness_score', 'name']


class SpiderCategory(models.Model):
    """
    Categories for spider data sources (tech, jobs, crypto, etc.)
    """
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default='🕷️')

    class Meta:
        app_label = 'core'
        verbose_name_plural = "Spider Categories"

    def __str__(self):
        return self.name


class AgentSpiderConnection(models.Model):
    """
    Many-to-many through table connecting Agents to Spider categories.
    This defines which agents process data from which spider categories.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey('Agent', on_delete=models.CASCADE, related_name='spider_connections')
    spider_category = models.ForeignKey(SpiderCategory, on_delete=models.CASCADE, related_name='agent_connections')

    # Routing configuration
    is_primary = models.BooleanField(default=False, help_text="Is this agent the primary handler for this category?")
    priority = models.IntegerField(default=5, help_text="Routing priority (1=highest, 10=lowest)")

    # Processing stats
    total_processed = models.IntegerField(default=0)
    successful_processed = models.IntegerField(default=0)
    avg_processing_time_ms = models.IntegerField(default=0)
    last_processed_at = models.DateTimeField(null=True, blank=True)

    # Quality tracking
    avg_quality_score = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        unique_together = ['agent', 'spider_category']
        ordering = ['priority', '-is_primary']

    def __str__(self):
        return f"{self.agent.name} ← {self.spider_category.name}"

    @property
    def success_rate(self):
        if self.total_processed == 0:
            return 0
        return (self.successful_processed / self.total_processed) * 100


class AgentKnowledgeSource(models.Model):
    """
    Tracks what knowledge each agent has learned from spider data.
    Aggregates spider data into agent-specific knowledge.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey('Agent', on_delete=models.CASCADE, related_name='knowledge_sources')

    # Knowledge categorization
    knowledge_type = models.CharField(max_length=50, choices=[
        ('trend', 'Trend Data'),
        ('market', 'Market Intelligence'),
        ('opportunity', 'Opportunity'),
        ('competitor', 'Competitor Info'),
        ('pricing', 'Pricing Data'),
        ('user_behavior', 'User Behavior'),
        ('content_idea', 'Content Ideas'),
        ('tool_discovery', 'Tool Discovery'),
        ('collaborative_insight', 'Collaborative Insight'),
    ])

    # Source tracking
    spider_category = models.ForeignKey(SpiderCategory, on_delete=models.SET_NULL, null=True, blank=True)
    source_spider_names = ArrayField(
        models.CharField(max_length=100),
        default=list,
        help_text="Names of spiders that contributed to this knowledge"
    )

    # Knowledge content
    title = models.CharField(max_length=500)
    summary = models.TextField(help_text="Summary of the knowledge")
    key_insights = models.JSONField(default=list, help_text="List of key insights")

    # Metrics
    data_points_count = models.IntegerField(default=0, help_text="Number of spider data points used")
    confidence_score = models.FloatField(default=0.0, help_text="Confidence in this knowledge (0.0-1.0)")
    relevance_score = models.FloatField(default=0.0)
    freshness_score = models.FloatField(default=1.0, help_text="How fresh/current this knowledge is (0.0-1.0)")

    # Timestamps
    first_discovered_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_validated = models.BooleanField(default=False)

    # Session 326: Project linkage - connect knowledge to project source
    source_project = models.ForeignKey(
        'core.PartnershipProject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derived_knowledge',
        help_text="Project this knowledge was derived from"
    )
    source_research = models.ForeignKey(
        'core.BusinessResearchResult',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derived_knowledge',
        help_text="Research result this knowledge was derived from"
    )

    # Session 326: Feedback-adjusted metrics
    feedback_positive = models.IntegerField(default=0, help_text="Count of positive feedback")
    feedback_negative = models.IntegerField(default=0, help_text="Count of negative feedback")
    feedback_adjusted_confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Confidence after user feedback adjustments"
    )

    class Meta:
        app_label = 'core'
        ordering = ['-confidence_score', '-last_updated_at']
        indexes = [
            models.Index(fields=['agent', 'knowledge_type']),
            models.Index(fields=['spider_category', 'is_active']),
            models.Index(fields=['source_project']),  # Session 326
        ]

    def __str__(self):
        return f"{self.agent.name}: {self.title[:50]}"

    @property
    def effective_confidence(self):
        """Get confidence score adjusted by feedback."""
        if self.feedback_adjusted_confidence is not None:
            return self.feedback_adjusted_confidence
        return self.confidence_score

    def apply_feedback(self, is_positive: bool, delta: float = 0.1):
        """Apply feedback to adjust confidence score."""
        if is_positive:
            self.feedback_positive += 1
            adjustment = delta
        else:
            self.feedback_negative += 1
            adjustment = -delta

        base = self.feedback_adjusted_confidence or self.confidence_score
        self.feedback_adjusted_confidence = max(0.0, min(1.0, base + adjustment))
        self.save()


class AgentLearningConnection(models.Model):
    """
    Defines learning relationships between agents.
    Agents can learn from each other based on complementary skills.

    Session 243: Enabling agent-to-agent knowledge sharing
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # The learning relationship
    teacher_agent = models.ForeignKey('Agent', on_delete=models.CASCADE, related_name='students')
    student_agent = models.ForeignKey('Agent', on_delete=models.CASCADE, related_name='teachers')

    # Learning configuration
    learning_type = models.CharField(max_length=50, choices=[
        ('complementary', 'Complementary Skills'),  # Different skills that work together
        ('specialization', 'Specialization'),  # Teacher is specialist in student's area
        ('pipeline', 'Pipeline'),  # Student uses teacher's output as input
        ('validation', 'Validation'),  # Cross-validation of work
        ('collaborative', 'Collaborative'),  # Working together on tasks
    ])

    # What knowledge types can be shared
    shareable_knowledge_types = ArrayField(
        models.CharField(max_length=50),
        default=list,
        help_text="Types of knowledge that can be transferred"
    )

    # Learning metrics
    total_transfers = models.IntegerField(default=0)
    successful_transfers = models.IntegerField(default=0)
    avg_improvement_score = models.FloatField(default=0.0, help_text="Average improvement from knowledge transfer")
    last_transfer_at = models.DateTimeField(null=True, blank=True)

    # Session 541: Mythology tracking - quality gate for knowledge transfers
    mythology_blocks = models.IntegerField(default=0, help_text="Transfers blocked by mythology validation")
    last_mythology_block_at = models.DateTimeField(null=True, blank=True, help_text="Last time mythology blocked a transfer")

    # Status
    is_active = models.BooleanField(default=True)
    strength = models.FloatField(default=0.5, help_text="Connection strength 0.0-1.0")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        unique_together = ['teacher_agent', 'student_agent']
        ordering = ['-strength', '-total_transfers']

    def __str__(self):
        return f"{self.teacher_agent.name} → {self.student_agent.name} ({self.learning_type})"

    @property
    def success_rate(self):
        if self.total_transfers == 0:
            return 0
        return (self.successful_transfers / self.total_transfers) * 100

    @property
    def mythology_block_rate(self):
        """Session 541: Calculate what % of attempted transfers were blocked by mythology"""
        total_attempted = self.total_transfers + self.mythology_blocks
        if total_attempted == 0:
            return 0
        return (self.mythology_blocks / total_attempted) * 100

    def apply_mythology_penalty(self):
        """Session 541: Apply trust decay when mythology blocks a transfer"""
        self.mythology_blocks += 1
        # Decay strength by 5% per block (min 0.1)
        self.strength = max(0.1, self.strength * 0.95)
        from django.utils import timezone
        self.last_mythology_block_at = timezone.now()
        self.save()


class KnowledgeTransfer(models.Model):
    """
    Records of knowledge being transferred between agents.
    When an agent learns something useful, it can share with connected agents.

    Session 243: Tracking knowledge flow between agents
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # The transfer
    connection = models.ForeignKey(AgentLearningConnection, on_delete=models.CASCADE, related_name='transfers')
    source_knowledge = models.ForeignKey(AgentKnowledgeSource, on_delete=models.CASCADE, related_name='transfers_out')

    # What was transferred
    transfer_summary = models.TextField(help_text="Summary of what was learned")
    key_points = models.JSONField(default=list)

    # Outcome
    was_useful = models.BooleanField(null=True, blank=True)
    usefulness_score = models.FloatField(default=0.0, help_text="How useful was this transfer (0.0-1.0)")
    student_feedback = models.TextField(blank=True)

    # Application
    was_applied = models.BooleanField(default=False)
    application_result = models.JSONField(default=dict, help_text="Result of applying the knowledge")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']

    def __str__(self):
        return f"Transfer: {self.connection} at {self.created_at}"


class MythologyQuarantine(models.Model):
    """
    Session 541: Quarantine for knowledge blocked by mythology validation.

    Instead of just logging blocked transfers, we store them here for:
    1. Review - humans can approve/reject/edit
    2. Analysis - understand where myths come from
    3. Spider tuning - identify problematic sources
    4. Teacher trust - track which agents produce unreliable knowledge
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # The blocked transfer context
    teacher_agent = models.ForeignKey('Agent', on_delete=models.CASCADE, related_name='mythology_blocks_as_teacher')
    student_agent = models.ForeignKey('Agent', on_delete=models.CASCADE, related_name='mythology_blocks_as_student')
    connection = models.ForeignKey(AgentLearningConnection, on_delete=models.CASCADE, related_name='quarantined_transfers', null=True)
    source_knowledge = models.ForeignKey(AgentKnowledgeSource, on_delete=models.SET_NULL, null=True, related_name='mythology_quarantines')

    # The blocked content
    blocked_title = models.CharField(max_length=500)
    blocked_content = models.TextField(help_text="The content that was blocked")
    blocked_summary = models.TextField(blank=True, help_text="Summary of what would have been transferred")

    # Mythology details
    violation_type = models.CharField(max_length=50, choices=[
        ('financial_myth', 'Financial Myth'),
        ('technical_myth', 'Technical Myth'),
        ('time_myth', 'Time Myth'),
        ('dangerous_myth', 'Dangerous Myth'),
        ('spider_data_myth', 'Spider Data Myth'),
    ])
    violation_count = models.IntegerField(default=1)
    violation_patterns = models.JSONField(default=list, help_text="Patterns that triggered the block")
    mythology_warning = models.TextField(blank=True, help_text="Mythology's explanation")

    # Spider traceability
    spider_sources = models.JSONField(default=list, help_text="Spider names that contributed to this knowledge")
    source_urls = models.JSONField(default=list, help_text="Original URLs if available")

    # Review status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Review'),
        ('approved', 'Approved (false positive)'),
        ('rejected', 'Rejected (confirmed myth)'),
        ('edited', 'Edited and Released'),
    ], default='pending')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.CharField(max_length=100, blank=True)
    review_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        verbose_name = 'Mythology Quarantine'
        verbose_name_plural = 'Mythology Quarantines'

    def __str__(self):
        return f"🚨 {self.teacher_agent.name}→{self.student_agent.name}: {self.blocked_title[:50]}"

    def approve(self, reviewed_by='system'):
        """Release from quarantine - it was a false positive"""
        from django.utils import timezone
        self.status = 'approved'
        self.reviewed_at = timezone.now()
        self.reviewed_by = reviewed_by
        self.save()

    def reject(self, reviewed_by='system', notes=''):
        """Confirm as myth - optionally flag the source knowledge"""
        from django.utils import timezone
        self.status = 'rejected'
        self.reviewed_at = timezone.now()
        self.reviewed_by = reviewed_by
        self.review_notes = notes
        self.save()

        # Optionally mark source knowledge as flagged
        if self.source_knowledge:
            self.source_knowledge.is_active = False
            self.source_knowledge.save()


class Advisor(models.Model):
    """
    Represents one of the 25 legendary advisors (Warren Buffett, Cathie Wood, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    expertise = models.TextField()
    category = models.CharField(max_length=50)

    # Influence and reputation
    influence_score = models.IntegerField(default=90)  # 0-100
    avatar_url = models.CharField(max_length=500, blank=True)

    # Wisdom and philosophy
    wisdom = models.JSONField(default=dict)  # Contains philosophy, principles, quotes

    # Status
    is_active = models.BooleanField(default=True)
    last_consultation = models.DateTimeField(null=True, blank=True)

    # Metrics
    total_consultations = models.IntegerField(default=0)
    total_insights_provided = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.title}"

    class Meta:
        app_label = 'core'
        ordering = ['-influence_score', 'name']


class AgentAssignment(models.Model):
    """
    Links users to their assigned agents
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # Custom settings for this user-agent pair
    custom_settings = models.JSONField(default=dict)
    priority = models.IntegerField(default=5)  # 1-10

    class Meta:
        app_label = 'core'
        unique_together = ['user', 'agent']


class AgentExecution(models.Model):
    """
    DEPRECATED: Use agents.models.AgentExecution instead.

    This model is deprecated as of Session 287 (HANDOFF_04).
    Use agents.models.AgentExecution which is linked to UnifiedAgentTemplate.

    Tracks every execution of an agent
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='executions')
    # Session 642: Made nullable to allow Celery task executions without user context
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    # Session 841: Track which experiment this execution belongs to for proper error rate scoping
    experiment = models.ForeignKey(
        'core.Experiment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='agent_executions',
        help_text="Session 841: Experiment this execution belongs to"
    )

    # Session 843: Orchestration Contract fields
    trace_id = models.UUIDField(
        null=True, blank=True, db_index=True,
        help_text="Session 843: Trace ID linking this execution to a broader workflow"
    )
    project = models.ForeignKey(
        'core.PartnershipProject',
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name='agent_executions',
        help_text="Session 843: Project this execution belongs to"
    )
    parent_object_type = models.CharField(
        max_length=50, blank=True,
        help_text="Session 843: Type of parent (conversation, orchestration, gate)"
    )
    parent_object_id = models.UUIDField(
        null=True, blank=True, db_index=True,
        help_text="Session 843: ID of parent that triggered this execution"
    )
    owner_agent = models.CharField(
        max_length=100, blank=True, db_index=True,
        help_text="Session 843: Agent that owns/created this execution"
    )

    task = models.TextField()
    # Session 1098 PR #3: 'cancelled' added for cooperative cancellation
    # via CancelTokenRegistry. See core/services/cancel_registry.py.
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], default='pending')

    # Execution details
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)

    # Session 1039: Multi-tenant cost attribution
    tenant = models.ForeignKey(
        'core.Tenant', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='agent_executions',
    )

    # Performance metrics
    execution_time_ms = models.IntegerField(null=True)
    tokens_used = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=8, decimal_places=4, default=Decimal('0.00'))

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Session 1100: Heartbeat field — long-running agents touch this periodically
    # so the cleanup watchdog can distinguish "still alive" from "truly stuck".
    last_heartbeat_at = models.DateTimeField(null=True, blank=True, db_index=True)

    # Session 1098 PR #4: lineage for nested-dispatch cancel + budget.
    # Parent = execution_id of the dispatch that spawned this run.
    # Root = top-of-chain ancestor (self.id if no parent).
    # Both NULL for pre-PR-4 rows. See core/services/cancel_registry.
    parent_execution_id = models.UUIDField(null=True, blank=True, db_index=True)
    root_execution_id = models.UUIDField(null=True, blank=True, db_index=True)

    class Meta:
        app_label = 'core'

    def touch_heartbeat(self):
        """Update heartbeat timestamp to signal this execution is still alive.
        Uses queryset update() for thread safety — avoids ORM instance state issues."""
        from django.utils import timezone
        AgentExecution.objects.filter(id=self.id).update(last_heartbeat_at=timezone.now())

    def __str__(self):
        return f"{self.agent.name} - {self.task[:50]}"

    # Session 1084: Retired misleading deprecation warning.
    #
    # Prior to this session, `.save()` emitted a DeprecationWarning pointing
    # callers to `agents.models.AgentExecution`. That direction was
    # BACKWARDS: investigation of production DB state showed
    # `core_agentexecution` (this model) is the canonical, actively-written
    # live table (58 rows in last 2h in local, all reads by `ops_tool` come
    # from here), while `agents_agentexecution` (the "new" model the
    # warning pointed to) was EMPTY — nobody successfully writes to it
    # because tasks_agents shadow-imports THIS model at function scope.
    #
    # The warning was causing real confusion ("which model do I use?")
    # and the suggested migration target would break production. Both
    # `tasks_agents._impl_execute_agent_task` and
    # `agent_router._create_execution_record` write here; `ops_tool`,
    # cleanup watchdog, and dedup all read here. This is the live model.
    #
    # Consolidation of the two parallel models is a separate, larger
    # refactor tracked for a later session — it requires a data
    # migration or a conscious decision to retire one of the tables.
    # Until then, leave this model alone and don't re-add a deprecation
    # warning pointing to the empty alternative.


class Collaboration(models.Model):
    """
    Tracks collaborations between agents and/or advisors
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Participants
    lead_agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='led_collaborations')
    collaborating_agents = models.ManyToManyField(Agent, related_name='collaborations')
    advisors = models.ManyToManyField(Advisor, related_name='consultations', blank=True)

    # Collaboration details
    objective = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ])

    # Results
    outcome = models.JSONField(default=dict)
    success_metrics = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'

    def __str__(self):
        return f"Collaboration: {self.objective[:50]}"


class Revenue(models.Model):
    """
    DEPRECATED: Use core.models.Revenue instead.

    The version in models.py inherits UnifiedBaseModel and has more comprehensive
    source_type choices (quick_apply, freelance, consulting, trading, sports_betting, affiliate).
    See docs/audits/MODEL_DEDUPLICATION_AUDIT.md.

    ---

    Tracks all revenue generated through the platform
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='revenues')

    # Source
    source_type = models.CharField(max_length=50)  # job, gig, investment, etc.
    source_id = models.CharField(max_length=100, blank=True)
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True)

    # Amount
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')

    # Status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='pending')

    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    earned_at = models.DateTimeField(null=True)
    paid_at = models.DateTimeField(null=True)

    # Details
    description = models.TextField()
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return f"${self.amount} - {self.source_type}"

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']


class Opportunity(models.Model):
    """
    Represents an income opportunity (job, gig, investment, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='opportunities')

    # Opportunity details
    title = models.CharField(max_length=200)
    opportunity_type = models.CharField(max_length=50)
    source = models.CharField(max_length=100)

    # Financial
    potential_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('pending', 'Pending Review'),
        ('applied', 'Applied'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ], default='active')

    # Workspace binding
    workspace = models.ForeignKey(
        'core.ProjectWorkspace',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opportunities',
        db_index=True,
        help_text="Workspace this opportunity belongs to"
    )

    # Matching
    match_score = models.IntegerField(default=0)  # 0-100
    recommended_by = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True)

    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Details
    description = models.TextField()
    requirements = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)

    # NEW (Session Pre-38): Partnership Enhancement Fields (Additive - won't break existing)
    # These fields enable human-AI partnership tracking WITHOUT changing existing functionality
    partnership_mode = models.CharField(
        max_length=20,
        choices=[
            ('solo', 'Traditional - User Only'),
            ('ai_assisted', 'AI-Assisted - User Leads'),
            ('collaborative', 'True Partnership - Equal'),
            ('ai_led', 'AI-Led - User Validates'),
        ],
        default='solo',
        null=True,
        blank=True,
        help_text="How human + AI will work together (optional)"
    )

    # Collaboration potential
    ai_contribution_potential = models.IntegerField(
        default=0,
        help_text="0-100: How much can AI contribute? (0 = no AI help possible)"
    )
    collaboration_feasibility = models.CharField(
        max_length=20,
        choices=[
            ('not_applicable', 'Not a partnership opportunity'),
            ('low', 'Minimal AI contribution possible'),
            ('medium', 'Moderate AI assistance available'),
            ('high', 'Strong partnership potential'),
            ('ideal', 'Perfect for human-AI collaboration'),
        ],
        default='not_applicable',
        null=True,
        blank=True,
        help_text="Partnership assessment (optional)"
    )

    # Execution planning (optional - for partnership opportunities)
    partnership_workflow = models.JSONField(
        null=True,
        blank=True,
        help_text="Step-by-step collaboration plan (optional)"
    )
    required_human_skills = models.JSONField(
        default=list,
        help_text="What human brings to partnership (optional)"
    )
    ai_capabilities_match = models.JSONField(
        default=list,
        help_text="What AI brings to partnership (optional)"
    )

    # Value metrics (optional - for showing partnership ROI)
    estimated_solo_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Hours if user did alone (optional)"
    )
    estimated_partnership_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Hours with AI partnership (optional)"
    )
    time_multiplier = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Efficiency gain (e.g., 3.5x faster) (optional)"
    )

    # Session 433: User-friendly ID for Discord commands
    user_friendly_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True,
        unique=True,
        help_text="User-friendly sequential ID (e.g., 1, 2, 3)"
    )

    # Session 433: Direct URL to opportunity source
    url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Direct link to opportunity listing"
    )

    # Session 766: Link to project when opportunity is executed
    project = models.ForeignKey(
        'PartnershipProject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opportunities',
        help_text="Project created from this opportunity when executed via orchestration"
    )

    def save(self, *args, **kwargs):
        """Auto-assign user_friendly_id and workspace on creation."""
        if self._state.adding and self.user_friendly_id is None:
            from django.db.models import Max
            max_id = Opportunity.objects.aggregate(Max('user_friendly_id'))['user_friendly_id__max']
            self.user_friendly_id = (max_id or 0) + 1
        # Auto-resolve workspace if not set
        if not self.workspace_id:
            try:
                from core.services.deliverable_workspace_resolver import resolve_workspace
                ws, _ = resolve_workspace()
                if ws:
                    self.workspace = ws
            except Exception as _e:
                logger.warning(
                    "models_unified_system.save: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - ${self.potential_revenue}"

    def calculate_partnership_metrics(self):
        """
        Calculate partnership value proposition (NEW - Session Pre-38)

        Returns dict showing potential ROI of human-AI partnership
        Only applicable if partnership fields are set
        """
        if not self.estimated_solo_hours or not self.estimated_partnership_hours:
            return {
                'available': False,
                'message': 'Partnership metrics not calculated for this opportunity'
            }

        self.time_multiplier = self.estimated_solo_hours / self.estimated_partnership_hours

        time_saved = self.estimated_solo_hours - self.estimated_partnership_hours
        effective_rate = self.potential_revenue / self.estimated_partnership_hours

        return {
            'available': True,
            'time_saved_hours': float(time_saved),
            'efficiency_gain': float(self.time_multiplier),
            'effective_hourly_rate': float(effective_rate),
            'solo_estimate': f"{float(self.estimated_solo_hours):.1f} hours",
            'partnership_estimate': f"{float(self.estimated_partnership_hours):.1f} hours",
            'ai_contribution': f"{self.ai_contribution_potential}%",
            'value_proposition': (
                f"${self.potential_revenue:.2f} in {float(self.estimated_partnership_hours):.1f}h "
                f"(vs {float(self.estimated_solo_hours):.1f}h solo) = "
                f"${float(effective_rate):.2f}/h effective rate"
            )
        }

    def mark_as_accepted(self, actual_amount=None):
        """
        CRITICAL FIX: Mark opportunity as accepted and create Revenue record
        This is the missing link for revenue tracking!
        """
        from decimal import Decimal

        self.status = 'accepted'
        self.save()

        # Create Revenue record
        revenue_amount = actual_amount or self.potential_revenue

        Revenue.objects.create(
            user=self.user,
            source_type=self.opportunity_type,
            source_id=str(self.id),
            agent=self.recommended_by,
            amount=Decimal(str(revenue_amount)),
            currency='USD',
            status='pending',
            description=f"Revenue from opportunity: {self.title}",
            metadata={
                'opportunity_id': str(self.id),
                'opportunity_title': self.title,
                'source_platform': self.source,
                'match_score': self.match_score,
                'created_via': 'opportunity_acceptance'
            }
        )

        logger = logging.getLogger(__name__)
        logger.info(f"✅ Created Revenue record for opportunity {self.id}: ${revenue_amount}")

    def mark_as_completed(self, actual_amount=None, paid_date=None):
        """
        CRITICAL FIX: Mark opportunity as completed and update Revenue to received
        """
        from django.utils import timezone

        self.status = 'completed'
        self.save()

        # Find and update the Revenue record
        revenue = Revenue.objects.filter(
            user=self.user,
            source_id=str(self.id),
            status='pending'
        ).first()

        if revenue:
            revenue.status = 'completed'
            revenue.earned_at = timezone.now()
            revenue.paid_at = paid_date or timezone.now()
            if actual_amount:
                revenue.amount = actual_amount
            revenue.save()

            logger = logging.getLogger(__name__)
            logger.info(f"✅ Updated Revenue record {revenue.id} to completed: ${revenue.amount}")
        else:
            # If no revenue record exists, create one
            self.mark_as_accepted(actual_amount)

    # =========================================================================
    # Session 223: Creative Intelligence Empire - Opportunity Scoring Fields
    # =========================================================================

    # Source linkage to spider data
    spider_data = models.ForeignKey(
        'SpiderData',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scored_opportunities',
        help_text="Link to spider-collected data that generated this opportunity"
    )

    # Source type categorization
    SOURCE_TYPE_CHOICES = [
        ('trend', 'Trending Topic'),
        ('job', 'Job/Gig Opportunity'),
        ('product', 'Product Demand'),
        ('news', 'News Event'),
        ('competition', 'Competitor Gap'),
        ('seasonal', 'Seasonal Demand'),
        ('viral', 'Viral Content'),
        ('tech', 'Technology Trend'),
    ]
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPE_CHOICES,
        null=True,
        blank=True,
        help_text="What kind of data generated this opportunity"
    )

    # Category for content creation
    CATEGORY_CHOICES = [
        ('digital_product', 'Digital Product'),
        ('freelance', 'Freelance Service'),
        ('content', 'Content Creation'),
        ('template', 'Template/Asset'),
        ('course', 'Course/Education'),
        ('software', 'Software/Tool'),
        ('consulting', 'Consulting'),
        ('affiliate', 'Affiliate Marketing'),
        ('sports_betting', 'Sports Betting'),
        ('trading', 'Trading/Investment'),
    ]
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        null=True,
        blank=True,
        help_text="Category for content creation opportunity"
    )

    # Scoring fields (1-100) - THE CORE OF THE OPPORTUNITY ENGINE
    profit_potential = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Estimated profit potential (1-100)"
    )
    competition_level = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Competition level - higher means MORE competition (1-100)"
    )
    effort_required = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Effort required - higher means MORE effort (1-100)"
    )
    time_sensitivity = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Time sensitivity - higher means MORE urgent (1-100)"
    )
    overall_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Overall opportunity score (calculated from other scores)"
    )

    # Content suggestions for capitalizing on opportunity
    suggested_content_types = models.JSONField(
        default=list,
        blank=True,
        help_text="List of content types: ['logo', 'thumbnail', 'video']"
    )
    suggested_workflows = models.JSONField(
        default=list,
        blank=True,
        help_text="List of recommended workflows to execute"
    )

    # Financial estimates
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated cost to create content for this opportunity"
    )

    # Supporting data
    keywords = models.JSONField(
        default=list,
        blank=True,
        help_text="Related keywords/tags"
    )
    market_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Market research data"
    )
    competitor_info = models.JSONField(
        default=dict,
        blank=True,
        help_text="Competitor analysis"
    )

    # Advisor consultation
    advisor_recommendations = models.JSONField(
        default=dict,
        blank=True,
        help_text="Recommendations from advisors consulted about this opportunity"
    )

    # Additional timestamps
    scored_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this opportunity was scored"
    )
    acted_on_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When user started acting on this opportunity"
    )

    @property
    def is_scored(self):
        """Check if this opportunity has been scored."""
        return all([
            self.profit_potential is not None,
            self.competition_level is not None,
            self.effort_required is not None,
            self.time_sensitivity is not None,
            self.overall_score is not None
        ])

    @property
    def estimated_roi(self):
        """Calculate estimated ROI."""
        if self.estimated_cost and self.estimated_cost > 0:
            return ((self.potential_revenue - self.estimated_cost) / self.estimated_cost) * 100
        return 0

    @property
    def urgency_level(self):
        """Categorize urgency based on time sensitivity."""
        if not self.time_sensitivity:
            return 'unknown'
        if self.time_sensitivity >= 80:
            return 'critical'
        elif self.time_sensitivity >= 60:
            return 'high'
        elif self.time_sensitivity >= 40:
            return 'medium'
        else:
            return 'low'

    def calculate_overall_score(self):
        """
        Calculate the overall score based on individual factors.

        Formula:
        - Profit potential contributes positively (weight: 0.35)
        - Low competition contributes positively (invert: 100 - competition)
        - Low effort contributes positively (invert: 100 - effort) (weight: 0.20)
        - Time sensitivity adds urgency bonus (weight: 0.10)
        """
        if not all([self.profit_potential, self.competition_level,
                    self.effort_required, self.time_sensitivity]):
            return None

        # Invert competition and effort (lower is better for overall score)
        competition_score = 100 - self.competition_level
        effort_score = 100 - self.effort_required

        # Weighted combination
        score = (
            self.profit_potential * 0.35 +
            competition_score * 0.35 +
            effort_score * 0.20 +
            self.time_sensitivity * 0.10
        )

        return min(100, max(1, int(score)))

    def score_opportunity(self, save=True):
        """Calculate and save the overall score."""
        from django.utils import timezone
        self.overall_score = self.calculate_overall_score()
        if self.overall_score:
            self.scored_at = timezone.now()
            if save:
                self.save()
        return self.overall_score

    class Meta:
        app_label = 'core'
        ordering = ['-match_score', '-created_at']


# =============================================================================
# Session 223: Opportunity Scoring Support Models
# =============================================================================

class OpportunityScore(models.Model):
    """
    Detailed scoring breakdown and reasoning for an opportunity.

    This provides transparency into how an opportunity was scored
    and allows for score refinement over time.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.OneToOneField(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='score_details'
    )

    # Scoring breakdown with reasoning
    profit_reasoning = models.TextField(
        blank=True,
        help_text="Explanation for profit potential score"
    )
    competition_reasoning = models.TextField(
        blank=True,
        help_text="Explanation for competition level score"
    )
    effort_reasoning = models.TextField(
        blank=True,
        help_text="Explanation for effort required score"
    )
    timing_reasoning = models.TextField(
        blank=True,
        help_text="Explanation for time sensitivity score"
    )

    # Confidence in scoring
    confidence_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        default=70,
        help_text="Confidence in the accuracy of this scoring (1-100)"
    )

    # Data sources used for scoring
    data_sources = models.JSONField(
        default=list,
        help_text="List of data sources used to calculate scores"
    )

    # Advisor input
    advisors_consulted = models.JSONField(
        default=list,
        help_text="List of advisors who provided input"
    )

    # Scoring metadata
    scoring_model_version = models.CharField(
        max_length=20,
        default='v1.0',
        help_text="Version of the scoring algorithm used"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'

    def __str__(self):
        return f"Score Details for: {self.opportunity.title}"


# =============================================================================
# Session 470: ML Scoring Models - Market Intelligence Architecture
# =============================================================================

class MLModelVersion(models.Model):
    """
    Track ML model versions for opportunity scoring.

    Enables model versioning, accuracy tracking, and rollback capability.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    version = models.CharField(
        max_length=20,
        unique=True,
        help_text="Model version string (e.g., v1.0, v2.1)"
    )

    # Training metadata
    trained_at = models.DateTimeField(
        help_text="When the model was trained"
    )
    training_samples = models.IntegerField(
        default=0,
        help_text="Number of samples used for training"
    )
    training_duration_seconds = models.IntegerField(
        default=0,
        help_text="How long training took"
    )

    # Model metrics
    train_mse = models.FloatField(
        null=True, blank=True,
        help_text="Mean squared error on training set"
    )
    test_mse = models.FloatField(
        null=True, blank=True,
        help_text="Mean squared error on test set"
    )
    train_r2 = models.FloatField(
        null=True, blank=True,
        help_text="R-squared score on training set"
    )
    test_r2 = models.FloatField(
        null=True, blank=True,
        help_text="R-squared score on test set"
    )

    # Feature importance (top 10)
    feature_importance = models.JSONField(
        default=list,
        help_text="Feature importance rankings from XGBoost"
    )

    # Status
    is_active = models.BooleanField(
        default=False,
        help_text="Whether this is the currently active model"
    )
    is_archived = models.BooleanField(
        default=False,
        help_text="Whether this model has been archived"
    )

    # Model file location
    model_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Path to the saved model file"
    )

    # Notes
    notes = models.TextField(
        blank=True,
        help_text="Training notes or comments"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-trained_at']
        indexes = [
            models.Index(fields=['version']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        status = " (ACTIVE)" if self.is_active else ""
        return f"ML Model {self.version}{status}"

    def activate(self):
        """Activate this model version, deactivating others."""
        MLModelVersion.objects.filter(is_active=True).update(is_active=False)
        self.is_active = True
        self.save()


class ScoringExplanation(models.Model):
    """
    SHAP-based explanation for an opportunity score.

    Stores feature contributions and explanations for transparency
    and debugging of ML scoring decisions.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    opportunity = models.OneToOneField(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='ml_explanation'
    )

    # Model used
    model_version = models.ForeignKey(
        MLModelVersion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='explanations'
    )

    # Scores
    ml_score = models.FloatField(
        help_text="Raw ML model score (0-100)"
    )
    rule_score = models.FloatField(
        help_text="Rule-based score (0-100)"
    )
    hybrid_score = models.FloatField(
        help_text="Combined hybrid score (0-100)"
    )
    confidence = models.FloatField(
        help_text="Confidence in the score (0-100)"
    )

    # SHAP explanation data
    shap_base_value = models.FloatField(
        null=True, blank=True,
        help_text="SHAP base/expected value"
    )
    shap_values = models.JSONField(
        default=list,
        help_text="SHAP values for each feature"
    )
    feature_names = models.JSONField(
        default=list,
        help_text="Feature names in order"
    )
    feature_values = models.JSONField(
        default=list,
        help_text="Feature values in order"
    )

    # Top contributing features (cached for quick access)
    top_positive_features = models.JSONField(
        default=list,
        help_text="Top features that increased the score"
    )
    top_negative_features = models.JSONField(
        default=list,
        help_text="Top features that decreased the score"
    )

    # Rule-based reasoning
    rule_reasoning = models.JSONField(
        default=dict,
        help_text="Reasoning from rule-based scoring"
    )

    # Timing
    scoring_time_ms = models.IntegerField(
        default=0,
        help_text="Time taken to generate this score in milliseconds"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['hybrid_score']),
        ]

    def __str__(self):
        return f"Explanation for {self.opportunity.title[:50]} (score: {self.hybrid_score:.1f})"

    def get_top_features(self, n: int = 5):
        """Get top N features by absolute SHAP value."""
        if not self.shap_values or not self.feature_names:
            return []

        indexed = list(enumerate(self.shap_values))
        sorted_features = sorted(indexed, key=lambda x: abs(x[1]), reverse=True)

        top = []
        for idx, shap_val in sorted_features[:n]:
            if idx < len(self.feature_names):
                top.append({
                    'feature': self.feature_names[idx],
                    'value': self.feature_values[idx] if idx < len(self.feature_values) else None,
                    'shap_value': round(shap_val, 4),
                    'impact': 'positive' if shap_val > 0 else 'negative'
                })
        return top


# =============================================================================
# Session 470: Phase 2 - Scoring Dispatcher Configuration
# =============================================================================

class ScoringConfiguration(models.Model):
    """
    Configuration for the ML Scoring Dispatcher.

    Session 470: Market Intelligence Architecture - Phase 2

    Controls whether scoring happens in real-time or batch mode,
    and SLA thresholds for automatic mode switching.
    """

    SCORING_MODE_CHOICES = [
        ('realtime', 'Real-time (immediate scoring)'),
        ('batch', 'Batch (hourly processing)'),
        ('auto', 'Auto (switch based on SLA)'),
    ]

    PRIORITY_CHOICES = [
        ('high', 'High (user-triggered, immediate)'),
        ('normal', 'Normal (background scoring)'),
        ('low', 'Low (backfill/reprocessing)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # User-specific configuration (null = global default)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='scoring_config',
        null=True, blank=True,
        help_text="User this config applies to (null = global default)"
    )

    # Scoring mode
    scoring_mode = models.CharField(
        max_length=20,
        choices=SCORING_MODE_CHOICES,
        default='auto',
        help_text="How scoring requests should be processed"
    )

    # SLA settings
    sla_threshold_ms = models.IntegerField(
        default=500,
        help_text="Max acceptable latency in milliseconds"
    )
    auto_switch_threshold_ms = models.IntegerField(
        default=1000,
        help_text="Latency at which to switch from realtime to batch"
    )

    # Priority settings
    default_priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='normal',
        help_text="Default priority for scoring requests"
    )

    # Batch settings
    batch_size = models.IntegerField(
        default=100,
        help_text="Number of items to process per batch"
    )
    batch_interval_minutes = models.IntegerField(
        default=60,
        help_text="Minutes between batch processing runs"
    )

    # Feature flags
    enable_shap_explanations = models.BooleanField(
        default=True,
        help_text="Generate SHAP explanations (adds latency)"
    )
    enable_model_fallback = models.BooleanField(
        default=True,
        help_text="Fallback to rule-based scoring if ML fails"
    )
    store_explanations = models.BooleanField(
        default=True,
        help_text="Store ScoringExplanation records in database"
    )

    # Metrics tracking
    total_requests = models.IntegerField(default=0)
    realtime_requests = models.IntegerField(default=0)
    batch_requests = models.IntegerField(default=0)
    avg_latency_ms = models.FloatField(default=0.0)
    sla_breaches = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Scoring Configuration"
        verbose_name_plural = "Scoring Configurations"

    def __str__(self):
        if self.user:
            return f"Scoring Config for {self.user.username}"
        return "Global Scoring Config"

    def record_request(self, latency_ms: float, mode: str):
        """Record a scoring request for metrics tracking."""
        self.total_requests += 1
        if mode == 'realtime':
            self.realtime_requests += 1
        else:
            self.batch_requests += 1

        # Update rolling average latency
        if self.total_requests == 1:
            self.avg_latency_ms = latency_ms
        else:
            self.avg_latency_ms = (
                (self.avg_latency_ms * (self.total_requests - 1) + latency_ms)
                / self.total_requests
            )

        # Check SLA breach
        if latency_ms > self.sla_threshold_ms:
            self.sla_breaches += 1

        self.save(update_fields=[
            'total_requests', 'realtime_requests', 'batch_requests',
            'avg_latency_ms', 'sla_breaches', 'updated_at'
        ])

    @classmethod
    def get_config(cls, user=None):
        """Get scoring configuration for a user or global default."""
        if user:
            config, _ = cls.objects.get_or_create(user=user)
            return config
        # Get or create global config
        config, _ = cls.objects.get_or_create(user=None)
        return config


class ScoringQueueItem(models.Model):
    """
    Queue item for batch/async scoring.

    Session 470: Market Intelligence Architecture - Phase 2

    Tracks scoring requests in the priority queue for
    asynchronous processing.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    ]

    PRIORITY_CHOICES = [
        (1, 'High'),
        (2, 'Normal'),
        (3, 'Low'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # What to score
    spider_data = models.ForeignKey(
        'SpiderData',
        on_delete=models.CASCADE,
        related_name='scoring_queue_items'
    )

    # Queue management
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=2,
        help_text="Processing priority (1=high, 2=normal, 3=low)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Request context
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='scoring_requests'
    )
    request_source = models.CharField(
        max_length=50,
        default='system',
        help_text="Where the request came from (api, celery, user, etc.)"
    )

    # Results
    result_score = models.FloatField(null=True, blank=True)
    result_explanation_id = models.UUIDField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ['priority', 'created_at']
        indexes = [
            models.Index(fields=['status', 'priority', 'created_at']),
            models.Index(fields=['spider_data']),
        ]

    def __str__(self):
        return f"ScoringQueue[{self.priority}] {self.spider_data_id} - {self.status}"

    @property
    def latency_ms(self):
        """Calculate processing latency in milliseconds."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds() * 1000
        return None


# =============================================================================
# Session 470: Phase 3 - Human-in-the-Loop Validation
# =============================================================================

class ValidationRequest(models.Model):
    """
    Request for human validation of a scored opportunity.

    Session 470: Market Intelligence Architecture - Phase 3

    When ML scoring confidence falls in the 50-85% range,
    a validation request is created for human review.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('assigned', 'Assigned to Reviewer'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('escalated', 'Escalated'),
        ('expired', 'Expired'),
        ('auto_approved', 'Auto-Approved (High Confidence)'),
        ('auto_rejected', 'Auto-Rejected (Low Confidence)'),
    ]

    PRIORITY_CHOICES = [
        (1, 'Critical'),
        (2, 'High'),
        (3, 'Normal'),
        (4, 'Low'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # What needs validation
    opportunity = models.ForeignKey(
        'Opportunity',
        on_delete=models.CASCADE,
        related_name='validation_requests'
    )
    scoring_explanation = models.ForeignKey(
        'ScoringExplanation',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='validation_requests'
    )

    # Scores that triggered validation
    ml_score = models.FloatField(help_text="ML score at time of request")
    rule_score = models.FloatField(help_text="Rule-based score at time of request")
    hybrid_score = models.FloatField(help_text="Combined score at time of request")
    confidence = models.FloatField(help_text="Confidence level that triggered validation")

    # Validation status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=3,
        help_text="Review priority (1=critical, 4=low)"
    )

    # Assignment
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_validations'
    )
    assigned_at = models.DateTimeField(null=True, blank=True)

    # Request context
    request_reason = models.CharField(
        max_length=100,
        default='confidence_threshold',
        help_text="Why validation was requested"
    )
    request_source = models.CharField(
        max_length=50,
        default='auto',
        help_text="What triggered this request (auto, manual, escalation)"
    )

    # Deadlines
    deadline = models.DateTimeField(
        null=True, blank=True,
        help_text="Time by which decision must be made"
    )
    escalate_after = models.DateTimeField(
        null=True, blank=True,
        help_text="Escalate if not reviewed by this time"
    )

    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ['priority', 'created_at']
        indexes = [
            models.Index(fields=['status', 'priority', 'created_at']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['deadline']),
        ]

    def __str__(self):
        return f"Validation[{self.status}] {self.opportunity.title[:30]}... (conf: {self.confidence:.0f}%)"

    @property
    def is_overdue(self):
        """Check if validation is past deadline."""
        if self.deadline and self.status in ['pending', 'assigned']:
            from django.utils import timezone
            return timezone.now() > self.deadline
        return False

    @property
    def should_escalate(self):
        """Check if validation should be escalated."""
        if self.escalate_after and self.status in ['pending', 'assigned']:
            from django.utils import timezone
            return timezone.now() > self.escalate_after
        return False

    def assign_to(self, user):
        """Assign this validation to a user."""
        from django.utils import timezone
        self.assigned_to = user
        self.assigned_at = timezone.now()
        self.status = 'assigned'
        self.save(update_fields=['assigned_to', 'assigned_at', 'status', 'updated_at'])


class ValidationDecision(models.Model):
    """
    Decision made on a validation request.

    Session 470: Market Intelligence Architecture - Phase 3

    Records the human decision and reasoning, enabling
    the learning loop to improve ML scoring over time.
    """

    DECISION_CHOICES = [
        ('approve', 'Approve'),
        ('approve_with_changes', 'Approve with Score Override'),
        ('reject', 'Reject'),
        ('escalate', 'Escalate to Higher Authority'),
        ('defer', 'Defer Decision'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to request
    validation_request = models.OneToOneField(
        ValidationRequest,
        on_delete=models.CASCADE,
        related_name='decision'
    )

    # Decision
    decision = models.CharField(
        max_length=30,
        choices=DECISION_CHOICES
    )
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='validation_decisions'
    )

    # Score override (if approve_with_changes)
    override_score = models.FloatField(
        null=True, blank=True,
        help_text="Human-assigned score (if different from ML)"
    )

    # Reasoning (for ML learning)
    reasoning = models.TextField(
        blank=True,
        help_text="Why this decision was made"
    )
    reasoning_tags = models.JSONField(
        default=list,
        help_text="Structured tags for reasoning (e.g., ['price_too_high', 'wrong_category'])"
    )

    # Quality indicators
    agreement_with_ml = models.BooleanField(
        default=True,
        help_text="Did human agree with ML's assessment?"
    )
    ml_error_magnitude = models.FloatField(
        null=True, blank=True,
        help_text="How far off was ML? (override_score - hybrid_score)"
    )

    # Timing
    decision_time_seconds = models.IntegerField(
        null=True, blank=True,
        help_text="How long the human took to decide"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        indexes = [
            models.Index(fields=['decision']),
            models.Index(fields=['decided_by', 'created_at']),
            models.Index(fields=['agreement_with_ml']),
        ]

    def __str__(self):
        return f"Decision: {self.decision} by {self.decided_by} ({self.created_at.date()})"

    def save(self, *args, **kwargs):
        """Calculate ML error magnitude on save."""
        if self.override_score is not None:
            request = self.validation_request
            self.ml_error_magnitude = self.override_score - request.hybrid_score
            self.agreement_with_ml = abs(self.ml_error_magnitude) <= 10  # Within 10 points
        super().save(*args, **kwargs)


class ValidationConfig(models.Model):
    """
    Configuration for the HITL validation system.

    Session 470: Market Intelligence Architecture - Phase 3

    Defines confidence thresholds and validation rules.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # User-specific config (null = global default)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='validation_config',
        null=True, blank=True
    )

    # Confidence thresholds
    auto_approve_threshold = models.FloatField(
        default=85.0,
        help_text="Auto-approve if confidence >= this (0-100)"
    )
    auto_reject_threshold = models.FloatField(
        default=50.0,
        help_text="Auto-reject if confidence < this (0-100)"
    )

    # Validation queue settings
    default_deadline_hours = models.IntegerField(
        default=24,
        help_text="Default hours until validation deadline"
    )
    escalation_delay_hours = models.IntegerField(
        default=4,
        help_text="Hours before unreviewed items escalate"
    )

    # Auto-assignment settings
    enable_auto_assignment = models.BooleanField(
        default=True,
        help_text="Automatically assign validations to reviewers"
    )
    max_assignments_per_user = models.IntegerField(
        default=10,
        help_text="Max pending assignments per reviewer"
    )

    # Feature flags
    require_reasoning = models.BooleanField(
        default=False,
        help_text="Require reasoning for all decisions"
    )
    require_reasoning_for_overrides = models.BooleanField(
        default=True,
        help_text="Require reasoning when overriding ML score"
    )

    # Metrics
    total_validations = models.IntegerField(default=0)
    total_approved = models.IntegerField(default=0)
    total_rejected = models.IntegerField(default=0)
    total_overrides = models.IntegerField(default=0)
    avg_decision_time_seconds = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Validation Configuration"
        verbose_name_plural = "Validation Configurations"

    def __str__(self):
        if self.user:
            return f"Validation Config for {self.user.username}"
        return "Global Validation Config"

    @classmethod
    def get_config(cls, user=None):
        """Get validation configuration for a user or global default."""
        if user:
            config, _ = cls.objects.get_or_create(user=user)
            return config
        config, _ = cls.objects.get_or_create(user=None)
        return config

    def record_decision(self, decision: str, decision_time: int = None):
        """Record a validation decision for metrics."""
        self.total_validations += 1
        if decision in ['approve', 'approve_with_changes', 'auto_approved']:
            self.total_approved += 1
        elif decision in ['reject', 'auto_rejected']:
            self.total_rejected += 1
        if decision == 'approve_with_changes':
            self.total_overrides += 1

        # Update average decision time
        if decision_time:
            if self.total_validations == 1:
                self.avg_decision_time_seconds = float(decision_time)
            else:
                self.avg_decision_time_seconds = (
                    (self.avg_decision_time_seconds * (self.total_validations - 1) + decision_time)
                    / self.total_validations
                )

        self.save(update_fields=[
            'total_validations', 'total_approved', 'total_rejected',
            'total_overrides', 'avg_decision_time_seconds', 'updated_at'
        ])


class OpportunityAction(models.Model):
    """
    Track actions taken on opportunities.

    This enables the learning loop by recording what was done
    and eventually tracking the outcomes.
    """

    ACTION_TYPE_CHOICES = [
        ('viewed', 'Viewed'),
        ('analyzed', 'Analyzed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('started', 'Started Creating'),
        ('content_created', 'Content Created'),
        ('published', 'Published'),
        ('revenue_logged', 'Revenue Logged'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='actions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    action_type = models.CharField(max_length=30, choices=ACTION_TYPE_CHOICES)

    # What was created/done
    content_ids = models.JSONField(
        default=list,
        help_text="IDs of content created for this opportunity"
    )
    workflow_used = models.CharField(
        max_length=100,
        blank=True,
        help_text="Which workflow was used"
    )

    # Outcome tracking (for learning loop)
    outcome = models.JSONField(
        default=dict,
        help_text="Outcome data: revenue, engagement, etc."
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action_type} on {self.opportunity.title}"


class OpportunityRevenue(models.Model):
    """
    Session 224: Track actual revenue generated from opportunities.

    This closes the loop between discovered opportunities and real income,
    enabling the learning system to improve predictions over time.
    """

    REVENUE_STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('received', 'Received'),
        ('partial', 'Partial Payment'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    CONTENT_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('3d_model', '3D Model'),
        ('template', 'Template'),
        ('bundle', 'Bundle'),
        ('service', 'Service/Freelance'),
        ('other', 'Other'),
    ]

    PLATFORM_CHOICES = [
        ('direct', 'Direct Sale'),
        ('etsy', 'Etsy'),
        ('gumroad', 'Gumroad'),
        ('creative_market', 'Creative Market'),
        ('shutterstock', 'Shutterstock'),
        ('adobe_stock', 'Adobe Stock'),
        ('envato', 'Envato Elements'),
        ('fiverr', 'Fiverr'),
        ('upwork', 'Upwork'),
        ('freelancer', 'Freelancer'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='revenues'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    # Revenue details
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Total revenue amount"
    )
    currency = models.CharField(max_length=3, default='USD')
    platform_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Platform/marketplace fee"
    )
    net_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Amount after fees"
    )

    # Revenue classification
    status = models.CharField(
        max_length=20,
        choices=REVENUE_STATUS_CHOICES,
        default='received'
    )
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        default='image'
    )
    platform = models.CharField(
        max_length=30,
        choices=PLATFORM_CHOICES,
        default='direct'
    )

    # Content linkage (what content generated this revenue?)
    image_history = models.ForeignKey(
        'content.ImageHistory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opportunity_revenues'
    )
    video_history = models.ForeignKey(
        'content.VideoHistory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opportunity_revenues'
    )
    content_ids = models.JSONField(
        default=list,
        help_text="Additional content IDs associated with this revenue"
    )

    # Prediction accuracy tracking
    estimated_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="What was predicted vs actual"
    )
    prediction_accuracy = models.FloatField(
        null=True,
        blank=True,
        help_text="Accuracy percentage: actual/estimated * 100"
    )

    # Metadata
    description = models.TextField(
        blank=True,
        help_text="Description of the sale/revenue"
    )
    sale_date = models.DateTimeField(
        help_text="When the sale occurred"
    )
    payment_received_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When payment was actually received"
    )
    external_reference = models.CharField(
        max_length=200,
        blank=True,
        help_text="External order ID or reference"
    )

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        ordering = ['-sale_date']
        indexes = [
            models.Index(fields=['opportunity', 'status']),
            models.Index(fields=['user', 'sale_date']),
            models.Index(fields=['platform', 'status']),
        ]

    def save(self, *args, **kwargs):
        # Auto-calculate net amount if not set
        if self.net_amount is None:
            self.net_amount = self.amount - self.platform_fee

        # Calculate prediction accuracy if we have an estimate
        if self.estimated_revenue and self.estimated_revenue > 0:
            self.prediction_accuracy = float(self.amount / self.estimated_revenue * 100)
        elif self.opportunity.potential_revenue and self.opportunity.potential_revenue > 0:
            # Use opportunity's predicted revenue as fallback
            self.estimated_revenue = self.opportunity.potential_revenue
            self.prediction_accuracy = float(self.amount / self.opportunity.potential_revenue * 100)

        super().save(*args, **kwargs)

        # Update opportunity status to 'earning' when revenue is logged
        if self.opportunity.status not in ['earning', 'closed']:
            self.opportunity.status = 'earning'
            self.opportunity.save(update_fields=['status'])

    def __str__(self):
        return f"${self.amount} from {self.opportunity.title}"

    @property
    def prediction_error(self):
        """Calculate the prediction error (actual - estimated)"""
        if self.estimated_revenue:
            return float(self.amount - self.estimated_revenue)
        return None

    @property
    def is_better_than_predicted(self):
        """Did we do better than predicted?"""
        if self.estimated_revenue:
            return self.amount > self.estimated_revenue
        return None


class OpportunityContent(models.Model):
    """
    Session 224: Link content created from opportunities.

    Tracks which content was created as a result of pursuing an opportunity,
    enabling revenue attribution when that content generates income.
    """

    CONTENT_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('3d_model', '3D Model'),
        ('template', 'Template'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='created_content'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)

    # Direct links to content models
    image_history = models.ForeignKey(
        'content.ImageHistory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opportunity_created'
    )
    video_history = models.ForeignKey(
        'content.VideoHistory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opportunity_created'
    )

    # Workflow tracking
    workflow_used = models.CharField(
        max_length=100,
        blank=True,
        help_text="Which workflow created this content"
    )
    workflow_execution_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="ID of the workflow execution"
    )

    # Cost tracking
    production_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Cost to create this content (API costs, etc.)"
    )

    # Status
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    published_platforms = models.JSONField(
        default=list,
        help_text="Where this content was published"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.content_type} for {self.opportunity.title}"

    @property
    def total_revenue(self):
        """Calculate total revenue generated by this content"""
        if self.content_type == 'image' and self.image_history:
            return sum(r.amount for r in self.image_history.opportunity_revenues.all())
        elif self.content_type == 'video' and self.video_history:
            return sum(r.amount for r in self.video_history.opportunity_revenues.all())
        return 0

    @property
    def roi(self):
        """Calculate ROI for this content"""
        if self.production_cost and self.production_cost > 0:
            return float((self.total_revenue - self.production_cost) / self.production_cost * 100)
        return None


class OpportunityPredictionAccuracy(models.Model):
    """
    Session 224: Aggregate prediction accuracy tracking.

    Stores historical accuracy data for the learning loop to improve predictions.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="User-specific accuracy (null for system-wide)"
    )

    # Time period
    period_start = models.DateField()
    period_end = models.DateField()
    period_type = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ]
    )

    # Accuracy metrics
    total_opportunities = models.IntegerField(default=0)
    opportunities_with_revenue = models.IntegerField(default=0)
    conversion_rate = models.FloatField(
        default=0,
        help_text="% of opportunities that generated revenue"
    )

    # Revenue predictions
    total_predicted_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )
    total_actual_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )
    revenue_accuracy = models.FloatField(
        default=0,
        help_text="Actual/Predicted * 100"
    )
    mean_absolute_error = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Average absolute difference between predicted and actual"
    )

    # By category breakdown
    accuracy_by_category = models.JSONField(
        default=dict,
        help_text="Accuracy broken down by opportunity category"
    )
    accuracy_by_source = models.JSONField(
        default=dict,
        help_text="Accuracy broken down by source type"
    )

    # Scoring accuracy
    avg_predicted_score = models.FloatField(default=0)
    avg_actual_performance = models.FloatField(
        default=0,
        help_text="Normalized actual performance score"
    )
    score_correlation = models.FloatField(
        default=0,
        help_text="Correlation between predicted scores and actual outcomes"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-period_start']
        unique_together = ['user', 'period_start', 'period_type']

    def __str__(self):
        user_str = f"User {self.user_id}" if self.user else "System-wide"
        return f"{user_str} Accuracy {self.period_start} to {self.period_end}"


# =============================================================================
# Session 425: Opportunity Pipeline Automation
# =============================================================================

class OpportunityTask(models.Model):
    """
    Session 425: Auto-generated tasks from high-scoring opportunities.

    When an opportunity scores 70+/100, a task is automatically created
    to track the user's progress from discovery → application → outcome.
    """

    TASK_STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('accepted', 'Task Accepted'),
        ('in_progress', 'In Progress'),
        ('applied', 'Applied/Submitted'),
        ('waiting', 'Waiting for Response'),
        ('won', 'Won/Accepted'),
        ('lost', 'Lost/Rejected'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.OneToOneField(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='task'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='opportunity_tasks'
    )

    # Workspace (inherited from parent opportunity)
    workspace = models.ForeignKey(
        'core.ProjectWorkspace',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opportunity_tasks',
        db_index=True,
        help_text="Inherited from parent opportunity's workspace"
    )

    # Task details
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=TASK_STATUS_CHOICES,
        default='pending'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    # Agent assignment
    assigned_agents = models.ManyToManyField(
        Agent,
        blank=True,
        related_name='assigned_tasks',
        help_text="Agents that can help with this opportunity"
    )
    primary_agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_tasks',
        help_text="Lead agent for this opportunity"
    )

    # Score-based metadata (captured at task creation)
    opportunity_score = models.IntegerField(default=0)
    score_breakdown = models.JSONField(default=dict)

    # Timing
    due_date = models.DateTimeField(null=True, blank=True)
    auto_created = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    applied_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Notes and tracking
    user_notes = models.TextField(blank=True)
    action_items = models.JSONField(default=list, help_text="Suggested action steps")
    metadata = models.JSONField(default=dict)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['due_date']),
        ]

    def save(self, *args, **kwargs):
        """Auto-inherit workspace from parent opportunity."""
        if not self.workspace_id and self.opportunity_id:
            try:
                if self.opportunity and self.opportunity.workspace_id:
                    self.workspace_id = self.opportunity.workspace_id
            except Exception as _e:
                logger.warning(
                    "models_unified_system.save: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )
        if not self.workspace_id:
            try:
                from core.services.deliverable_workspace_resolver import resolve_workspace
                ws, _ = resolve_workspace()
                if ws:
                    self.workspace = ws
            except Exception as _e:
                logger.warning(
                    "models_unified_system.save: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Task: {self.title} ({self.status})"

    def accept_task(self):
        """User accepts the auto-generated task"""
        from django.utils import timezone
        self.status = 'accepted'
        self.accepted_at = timezone.now()
        self.save()
        logger = logging.getLogger(__name__)
        logger.info(f"✅ Task {self.id} accepted for opportunity {self.opportunity_id}")

    def mark_applied(self, notes=''):
        """Mark that user has applied for this opportunity"""
        from django.utils import timezone
        self.status = 'applied'
        self.applied_at = timezone.now()
        if notes:
            self.user_notes = notes
        self.save()

        # Also update the opportunity status
        self.opportunity.status = 'applied'
        self.opportunity.save()

    def mark_won(self, actual_amount=None, notes=''):
        """Mark opportunity as won - creates revenue record"""
        from django.utils import timezone
        self.status = 'won'
        self.completed_at = timezone.now()
        if notes:
            self.user_notes = notes
        self.save()

        # Create outcome record and revenue
        OpportunityOutcome.objects.create(
            task=self,
            outcome='won',
            actual_revenue=actual_amount or self.opportunity.potential_revenue,
            notes=notes
        )

        # Trigger revenue creation
        self.opportunity.mark_as_accepted(actual_amount)

        # Send Discord notification
        try:
            from core.services.discord_notifications import discord_notify
            discord_notify.send_boardroom_decision(
                title=f"🏆 Opportunity Won: {self.title}",
                decision=f"${actual_amount or self.opportunity.potential_revenue} revenue captured",
                reasoning=notes or "User marked opportunity as won",
                agents_involved=[self.primary_agent.name] if self.primary_agent else []
            )
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.debug(f"Discord notification failed: {e}")

    def mark_lost(self, reason='', notes=''):
        """Mark opportunity as lost"""
        from django.utils import timezone
        self.status = 'lost'
        self.completed_at = timezone.now()
        if notes:
            self.user_notes = notes
        self.save()

        # Create outcome record for learning
        OpportunityOutcome.objects.create(
            task=self,
            outcome='lost',
            loss_reason=reason,
            notes=notes
        )

        # Update opportunity
        self.opportunity.status = 'rejected'
        self.opportunity.save()

    @classmethod
    def create_from_opportunity(cls, opportunity, score_data=None):
        """
        Factory method to auto-create a task from a high-scoring opportunity.
        Called when opportunity scores 70+/100.
        """
        from django.utils import timezone
        from datetime import timedelta

        # Determine priority based on score
        score = opportunity.overall_score if hasattr(opportunity, 'overall_score') else 0
        if score >= 90:
            priority = 'urgent'
        elif score >= 80:
            priority = 'high'
        elif score >= 70:
            priority = 'medium'
        else:
            priority = 'low'

        # Set due date based on urgency (default 7 days)
        due_date = timezone.now() + timedelta(days=7 if score < 80 else 3)

        # Generate action items based on opportunity type
        action_items = cls._generate_action_items(opportunity)

        # Find relevant agents
        relevant_agents = cls._find_relevant_agents(opportunity)

        # Build research context for better agent execution
        research_context = cls._build_research_context(opportunity)

        # Store research context in metadata for agent use
        task_metadata = {
            'research_query': research_context['research_query'],
            'research_topic': research_context['research_topic'],
            'keywords': research_context['keywords'],
            'category': research_context['category'],
            'source': research_context['source'],
            'clean_title': research_context['clean_title'],
        }

        task = cls.objects.create(
            opportunity=opportunity,
            user=opportunity.user,
            title=f"Pursue: {opportunity.title}",
            description=opportunity.description[:500] if opportunity.description else '',
            priority=priority,
            opportunity_score=score,
            score_breakdown=score_data or {},
            due_date=due_date,
            action_items=action_items,
            metadata=task_metadata,
            # ForeignKey expects Agent object
            primary_agent=relevant_agents[0] if relevant_agents else None,
        )

        # Add all relevant agents
        if relevant_agents:
            task.assigned_agents.set(relevant_agents)

        logger = logging.getLogger(__name__)
        logger.info(f"📋 Auto-created task {task.id} for opportunity {opportunity.id} (score: {score})")

        return task

    @staticmethod
    def _generate_action_items(opportunity):
        """Generate suggested action items based on opportunity type"""
        category = opportunity.category if hasattr(opportunity, 'category') else ''
        opp_type = opportunity.opportunity_type

        base_items = [
            {"step": 1, "action": "Review opportunity details", "completed": False},
            {"step": 2, "action": "Assess fit with skills/resources", "completed": False},
        ]

        if opp_type in ['job', 'gig', 'freelance']:
            base_items.extend([
                {"step": 3, "action": "Prepare application/proposal", "completed": False},
                {"step": 4, "action": "Submit application", "completed": False},
                {"step": 5, "action": "Follow up if no response", "completed": False},
            ])
        elif opp_type in ['product', 'digital_product']:
            base_items.extend([
                {"step": 3, "action": "Create product/content", "completed": False},
                {"step": 4, "action": "List on marketplace(s)", "completed": False},
                {"step": 5, "action": "Promote and track sales", "completed": False},
            ])
        else:
            base_items.extend([
                {"step": 3, "action": "Take action on opportunity", "completed": False},
                {"step": 4, "action": "Track progress", "completed": False},
            ])

        return base_items

    @staticmethod
    def _build_research_context(opportunity):
        """
        Build research-friendly context from an opportunity.
        Extracts keywords and builds a clean research query.
        """
        import re

        # Extract category and source
        category = getattr(opportunity, 'category', '') or ''
        source = getattr(opportunity, 'source', '') or ''

        # Get title and clean it
        title = opportunity.title or ''
        # Remove common prefixes like "Review:", "Act on:", numbers at start
        clean_title = re.sub(r'^(Review:|Act on:|Pursue:|\d+\.?\s*)', '', title).strip()

        # Extract keywords from title (remove stopwords, keep meaningful words)
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                     'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                     'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
                     'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
                     'through', 'during', 'before', 'after', 'above', 'below',
                     'between', 'under', 'again', 'further', 'then', 'once',
                     'here', 'there', 'when', 'where', 'why', 'how', 'all',
                     'each', 'few', 'more', 'most', 'other', 'some', 'such',
                     'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
                     'too', 'very', 'just', 'and', 'but', 'if', 'or', 'because',
                     'until', 'while', 'these', 'those', 'this', 'that', 'which',
                     'who', 'whom', 'what', 'its', 'it', 'they', 'them', 'their',
                     'he', 'she', 'his', 'her', 'him', 'my', 'your', 'our', 'we',
                     'you', 'i', 'me', 'us', 'hand', 'picked', 'staff', 'says'}

        # Extract words from title
        words = re.findall(r'\b[a-zA-Z]{3,}\b', clean_title.lower())
        keywords = [w for w in words if w not in stopwords][:8]  # Keep top 8 meaningful words

        # Also check opportunity's own keywords field
        opp_keywords = getattr(opportunity, 'keywords', []) or []
        if opp_keywords:
            keywords = list(set(keywords + opp_keywords[:5]))[:10]

        # Build research query
        if category and category not in keywords:
            keywords.insert(0, category)

        research_query = ' '.join(keywords[:6]) if keywords else clean_title[:100]

        # Build research topic (more descriptive)
        if category:
            research_topic = f"{category}: {clean_title[:80]}"
        else:
            research_topic = clean_title[:100]

        return {
            'research_query': research_query,
            'research_topic': research_topic,
            'keywords': keywords,
            'category': category,
            'source': source,
            'clean_title': clean_title[:150],
        }

    @staticmethod
    def _find_relevant_agents(opportunity):
        """Find agents relevant to this opportunity type"""
        category = opportunity.category if hasattr(opportunity, 'category') else ''
        opp_type = opportunity.opportunity_type

        # Map opportunity types to agent specialties
        agent_mapping = {
            'job': ['ThinkingAgent', 'ResearchAgent'],
            'gig': ['ThinkingAgent', 'ResearchAgent'],
            'freelance': ['ThinkingAgent', 'ContentStrategyAgent'],
            'product': ['ImageAgent', 'VideoAgent', 'CreativeDirectorAgent'],
            'digital_product': ['ImageAgent', 'ContentStrategyAgent'],
            'content': ['ContentStrategyAgent', 'SEOOptimizerAgent', 'SocialMediaAgent'],
            'creative': ['CreativeDirectorAgent', 'ImageAgent', 'VideoAgent'],
            'tech': ['CTOAgent', 'ResearchAgent'],
        }

        agent_names = agent_mapping.get(opp_type, ['ThinkingAgent'])

        return list(Agent.objects.filter(name__in=agent_names)[:3])


class OpportunityOutcome(models.Model):
    """
    Session 425: Track final outcomes for learning and analytics.

    Records whether an opportunity was won/lost and why, enabling
    the system to learn from outcomes and improve scoring.
    """

    OUTCOME_CHOICES = [
        ('won', 'Won/Accepted'),
        ('lost', 'Lost/Rejected'),
        ('expired', 'Expired Without Action'),
        ('cancelled', 'Cancelled by User'),
        ('partial', 'Partial Success'),
    ]

    LOSS_REASON_CHOICES = [
        ('rejected', 'Application Rejected'),
        ('underbid', 'Underbid by Competitor'),
        ('not_qualified', 'Not Qualified'),
        ('timing', 'Bad Timing'),
        ('competition', 'Too Much Competition'),
        ('no_response', 'No Response Received'),
        ('changed_mind', 'Changed Mind'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.OneToOneField(
        OpportunityTask,
        on_delete=models.CASCADE,
        related_name='outcome'
    )

    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES)

    # Revenue tracking (for wins)
    actual_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    predicted_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    revenue_variance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual - Predicted"
    )

    # Loss analysis (for learning)
    loss_reason = models.CharField(
        max_length=20,
        choices=LOSS_REASON_CHOICES,
        blank=True
    )

    # Timing metrics
    days_to_outcome = models.IntegerField(
        null=True,
        blank=True,
        help_text="Days from task creation to outcome"
    )

    # Learning metadata
    notes = models.TextField(blank=True)
    lessons_learned = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Auto-calculate revenue variance
        if self.actual_revenue and self.task.opportunity.potential_revenue:
            self.predicted_revenue = self.task.opportunity.potential_revenue
            self.revenue_variance = self.actual_revenue - self.predicted_revenue

        # Calculate days to outcome
        if self.task.created_at:
            from django.utils import timezone
            self.days_to_outcome = (timezone.now() - self.task.created_at).days

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.outcome}: {self.task.title}"


class OpportunityDigest(models.Model):
    """
    Session 425: Weekly opportunity digest for #boardroom.

    Stores digest content for historical reference and tracking.
    """

    DIGEST_TYPE_CHOICES = [
        ('weekly', 'Weekly Digest'),
        ('monthly', 'Monthly Digest'),
        ('ad_hoc', 'Ad-hoc Report'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="User-specific digest (null for system-wide)"
    )

    digest_type = models.CharField(max_length=20, choices=DIGEST_TYPE_CHOICES, default='weekly')
    period_start = models.DateField()
    period_end = models.DateField()

    # Summary stats
    total_opportunities = models.IntegerField(default=0)
    high_value_opportunities = models.IntegerField(default=0)
    tasks_created = models.IntegerField(default=0)
    tasks_won = models.IntegerField(default=0)
    tasks_lost = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Category breakdown
    by_category = models.JSONField(default=dict)
    by_source = models.JSONField(default=dict)

    # Top opportunities
    top_opportunities = models.JSONField(default=list)

    # Win/loss analysis
    win_rate = models.FloatField(default=0)
    avg_score_won = models.FloatField(default=0)
    avg_score_lost = models.FloatField(default=0)

    # Full digest content (for Discord message)
    digest_content = models.TextField(blank=True)

    # Discord tracking
    posted_to_discord = models.BooleanField(default=False)
    discord_message_id = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-period_end']
        unique_together = ['user', 'digest_type', 'period_start']

    def __str__(self):
        return f"{self.digest_type.title()} Digest: {self.period_start} to {self.period_end}"


class Application(models.Model):
    """
    Tracks applications to opportunities
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE)

    # Application details
    cover_letter = models.TextField(blank=True)
    resume_version = models.CharField(max_length=100, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ], default='draft')

    # AI assistance
    assisted_by = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True)
    ai_confidence = models.IntegerField(default=0)  # 0-100

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def submit_application(self):
        """
        CRITICAL FIX: Submit application and create Application record
        This ensures applications are tracked in the database
        """
        from django.utils import timezone

        self.status = 'submitted'
        self.submitted_at = timezone.now()
        self.save()

        # Also update the opportunity status
        self.opportunity.status = 'applied'
        self.opportunity.save()

        logger = logging.getLogger(__name__)
        logger.info(f"✅ Application {self.id} submitted for opportunity {self.opportunity.id}")

    def mark_as_accepted(self):
        """
        CRITICAL FIX: Mark application as accepted and trigger revenue creation
        """
        self.status = 'accepted'
        self.save()

        # Mark the opportunity as accepted and create revenue
        self.opportunity.mark_as_accepted()

        logger = logging.getLogger(__name__)
        logger.info(f"✅ Application {self.id} accepted, revenue record created")

    class Meta:
        app_label = 'core'


class AgentSolution(models.Model):
    """
    Represents a solution created by an agent
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='solutions')

    title = models.CharField(max_length=200)
    description = models.TextField()
    solution_type = models.CharField(max_length=50)

    # Solution content
    code_snippet = models.TextField(blank=True)
    language = models.CharField(max_length=20, blank=True)

    # Metrics
    metrics = models.JSONField(default=dict)
    tags = models.JSONField(default=list)

    # Usage tracking
    times_used = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.agent.name}: {self.title}"

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']


class AgentLearning(models.Model):
    """
    Tracks learning and knowledge transfer between agents
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    teacher_agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='teachings')
    student_agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='learnings')
    solution = models.ForeignKey(AgentSolution, on_delete=models.CASCADE, related_name='learning_records')

    # Learning details
    learning_type = models.CharField(max_length=50)
    effectiveness_before = models.FloatField()
    effectiveness_after = models.FloatField()

    # Impact metrics
    time_saved_hours = models.IntegerField(default=0)
    cost_savings = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    # Status
    implementation_success = models.BooleanField(default=True)
    feedback = models.TextField(blank=True)

    # Metadata
    metadata = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher_agent.name} → {self.student_agent.name}"

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']


class SpiderData(models.Model):
    """
    Data collected by spider network for intelligence gathering.

    Session 293: Added embedding support for semantic search.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Source
    spider_name = models.CharField(max_length=100)
    source_url = models.CharField(max_length=500)
    data_type = models.CharField(max_length=50)

    # Data
    raw_data = models.JSONField()
    processed_data = models.JSONField(default=dict)

    # Analysis
    relevance_score = models.IntegerField(default=0)  # 0-100
    insights = models.JSONField(default=list)

    # Session 293: Embeddings for semantic search
    # Session 730: Migrated to pgvector VectorField
    # Aggregate embedding of all items in this spider data entry
    embedding = VectorField(
        dimensions=1536,
        null=True,
        blank=True,
        help_text="Vector embedding for semantic search (pgvector)"
    ) if HAS_PGVECTOR else models.JSONField(
        null=True,
        blank=True,
        help_text="Vector embedding (JSON fallback)"
    )
    # Individual item embeddings stored as dict: {item_index: embedding}
    item_embeddings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Individual embeddings for each item: {index: embedding}"
    )
    # Text used to generate the embedding (for debugging/verification)
    embedding_text = models.TextField(
        blank=True,
        help_text="The combined text used to generate the aggregate embedding"
    )

    # Status
    is_processed = models.BooleanField(default=False)
    is_actionable = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Spider Data: {self.spider_name} - {self.data_type}"

    def get_searchable_text(self) -> str:
        """Build searchable text from all items for embedding generation."""
        if not self.raw_data:
            return ""

        texts = []
        items = self.raw_data.get('items', [])
        for item in items[:20]:  # Limit to 20 items to avoid huge embeddings
            # Session 505: Added modelId and id as fallbacks for huggingface/kaggle data
            title = item.get('title') or item.get('name') or item.get('modelId') or item.get('id') or ''
            description = item.get('description') or item.get('summary') or item.get('pipeline_tag') or ''
            tags = item.get('tags', [])
            if isinstance(tags, list):
                # Handle tags that might be dicts (e.g., kaggle tags)
                tag_strs = []
                for t in tags[:5]:
                    if isinstance(t, dict):
                        tag_strs.append(t.get('name', str(t)))
                    else:
                        tag_strs.append(str(t))
                tags = ', '.join(tag_strs)
            elif not isinstance(tags, str):
                tags = ''

            if title:
                texts.append(f"{title}. {description[:200]} {tags}")

        return "\n".join(texts)[:4000]  # Limit total text length

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_processed', 'created_at'], name='spiderdata_proc_created'),
            models.Index(fields=['spider_name', 'created_at'], name='spiderdata_spider_created'),
            models.Index(fields=['data_type', 'created_at'], name='spiderdata_type_created'),
        ]


class SpiderDataAnnotation(models.Model):
    """
    Session 783: Agent annotations on spider data items.

    Enables agents to flag spider data as useful, profitable, podcast-worthy, etc.
    Powers the Spider News Feed for human consumption.
    """
    ANNOTATION_TYPES = [
        ('useful', 'Useful'),
        ('profitable', 'Profitable Opportunity'),
        ('podcast_worthy', 'Podcast Worthy'),
        ('breaking_news', 'Breaking News'),
        ('investment_opportunity', 'Investment Opportunity'),
        ('action_required', 'Action Required'),
        ('warning', 'Warning/Risk'),
        ('trending', 'Trending'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    spider_data = models.ForeignKey('SpiderData', on_delete=models.CASCADE, related_name='annotations')
    annotation_type = models.CharField(max_length=50, choices=ANNOTATION_TYPES, db_index=True)
    confidence_score = models.FloatField(default=0.5)  # 0.0-1.0
    note = models.TextField(blank=True)
    agent_name = models.CharField(max_length=100, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Engagement metrics
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)

    class Meta:
        app_label = 'core'
        unique_together = [['spider_data', 'agent_name', 'annotation_type']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['annotation_type', 'created_at']),
            models.Index(fields=['agent_name', 'created_at']),
        ]

    def __str__(self):
        return f"{self.annotation_type} by {self.agent_name} on {self.spider_data_id}"

    @property
    def score(self) -> int:
        """Net score (upvotes - downvotes)."""
        return self.upvotes - self.downvotes


class SpiderItemHash(models.Model):
    """
    Session 616: Tracks content hashes for spider item deduplication.

    Stores a hash of each unique item to prevent re-ingesting
    the same content across multiple spider runs.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Spider identification
    spider_name = models.CharField(max_length=100, db_index=True)
    data_type = models.CharField(max_length=50, default='unknown')

    # Content hash (SHA256 truncated to 32 chars)
    content_hash = models.CharField(max_length=32, db_index=True)

    # Human-readable reference (for debugging)
    item_title = models.CharField(max_length=200, blank=True)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        app_label = 'core'
        # Unique constraint: same hash for same spider shouldn't exist
        unique_together = [['spider_name', 'content_hash']]
        indexes = [
            models.Index(fields=['spider_name', 'created_at']),
            models.Index(fields=['content_hash']),
        ]

    def __str__(self):
        return f"{self.spider_name}: {self.item_title[:30]}"


class AdvisorInsight(models.Model):
    """
    Insights and recommendations from legendary advisors
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    advisor = models.ForeignKey(Advisor, on_delete=models.CASCADE, related_name='insights')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Insight details
    content = models.TextField()
    category = models.CharField(max_length=50)
    confidence = models.IntegerField(default=80)  # 0-100

    # Context
    context = models.JSONField(default=dict)
    related_opportunity = models.ForeignKey(Opportunity, on_delete=models.SET_NULL, null=True, blank=True)

    # Actionability
    is_actionable = models.BooleanField(default=True)
    action_plan = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Insight from {self.advisor.name}: {self.content[:50]}"

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']


class UserAgentLearning(UnifiedBaseModel):
    """
    Connects user profiles to agent learning - making agents learn FOR specific users

    This model enables personalized agent learning where agents track what works
    for each individual user, building user-specific knowledge over time.

    Example:
        For User A (software engineer):
        - Job Matcher Agent learns A prefers remote Python roles at startups
        - Content Creator Agent learns A likes technical blog style
        - Income Builder learns A's best opportunities are on HackerNews

        For User B (designer):
        - Job Matcher Agent learns B prefers agency creative director roles
        - Content Creator Agent learns B likes visual portfolio style
        - Income Builder learns B's best opportunities are on Dribbble
    """

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='agent_learnings',
        help_text="User this learning applies to"
    )

    agent_name = models.CharField(
        max_length=200,
        help_text="Name of the agent (e.g., 'JobMatcherAgent', 'IncomeBuilder')"
    )

    learning_domain = models.CharField(
        max_length=100,
        choices=[
            ('opportunity_matching', 'Job/Opportunity Matching'),
            ('content_creation', 'Content Creation Style'),
            ('communication', 'Communication Preferences'),
            ('decision_making', 'Decision Making Patterns'),
            ('skill_development', 'Skill Development Path'),
            ('revenue_optimization', 'Revenue Optimization'),
            ('platform_preferences', 'Platform Preferences'),
            ('salary_preferences', 'Salary Range Preferences'),
            ('skill_preferences', 'Skill Type Preferences'),
            ('company_size_preferences', 'Company Size Preferences'),
            ('remote_preferences', 'Remote Work Preferences'),
            ('timing_patterns', 'Optimal Timing Patterns'),
            ('success_factors', 'Success Factor Analysis'),
            # Sports Betting Learning Domains (integrated via SportsBettingLearningBridge)
            ('sports_betting_nfl', 'Sports Betting - NFL'),
            ('sports_betting_nba', 'Sports Betting - NBA'),
            ('sports_betting_mlb', 'Sports Betting - MLB'),
            ('sports_betting_nhl', 'Sports Betting - NHL'),
            ('betting_risk_management', 'Betting Risk Management'),
            ('kelly_criterion_optimization', 'Kelly Criterion Optimization'),
            # Partnership Learning Domain (Session 40)
            ('partnership_success', 'Partnership Success'),
            ('general', 'General Learning'),
        ],
        default='general',
        help_text="What domain is this learning about"
    )

    # What the agent learned
    learning_content = models.JSONField(
        help_text="Structured learning data specific to this agent-user pair"
    )

    # How confident is the agent in this learning
    confidence_score = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Agent's confidence in this learning (0-1)"
    )

    # How many times this learning was validated
    validation_count = models.IntegerField(
        default=0,
        help_text="How many times this learning proved correct"
    )

    # How many times this learning failed
    failure_count = models.IntegerField(
        default=0,
        help_text="How many times this learning proved incorrect"
    )

    # Success rate calculated from validation/failure
    success_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Success rate of this learning"
    )

    # Source of this learning
    learning_source = models.CharField(
        max_length=100,
        choices=[
            ('user_feedback', 'Direct User Feedback'),
            ('success_pattern', 'Observed Success Pattern'),
            ('failure_analysis', 'Failure Analysis'),
            ('interaction_mining', 'Interaction Pattern Mining'),
            ('explicit_instruction', 'Explicit User Instruction'),
            ('performance_tracking', 'Performance Tracking'),
        ],
        default='success_pattern'
    )

    # Context when this was learned
    context_metadata = models.JSONField(
        default=dict,
        help_text="Context when learning occurred (time, situation, etc.)"
    )

    # When this learning expires (if temporary)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this learning becomes obsolete (null = never expires)"
    )

    # How many times this learning was used
    usage_count = models.IntegerField(
        default=0,
        help_text="How many times this learning influenced agent behavior"
    )

    last_used = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this learning was last applied"
    )

    class Meta:
        verbose_name = "User-Agent Learning"
        verbose_name_plural = "User-Agent Learnings"
        app_label = 'core'
        indexes = [
            models.Index(fields=['user', 'agent_name', 'learning_domain']),
            models.Index(fields=['user', '-confidence_score']),
            models.Index(fields=['user', '-success_rate']),
            models.Index(fields=['agent_name', '-confidence_score']),
        ]

    def __str__(self):
        return f"{self.agent_name} → {self.user.username}: {self.learning_domain} (confidence: {self.confidence_score:.1%})"

    def record_success(self):
        """Record that this learning proved correct"""
        self.validation_count += 1
        self.usage_count += 1
        self.last_used = timezone.now()
        self._update_metrics()
        self.save()

    def record_failure(self):
        """Record that this learning proved incorrect"""
        self.failure_count += 1
        self.usage_count += 1
        self.last_used = timezone.now()
        self._update_metrics()
        self.save()

    def _update_metrics(self):
        """Update confidence and success rate based on validation/failure counts"""
        total_attempts = self.validation_count + self.failure_count

        if total_attempts > 0:
            # Calculate success rate
            self.success_rate = self.validation_count / total_attempts

            # Adjust confidence based on success rate and sample size
            # More samples = more confidence in the success rate
            sample_weight = min(total_attempts / 20.0, 1.0)  # Fully confident after 20 samples

            # Confidence approaches success rate as sample size grows
            self.confidence_score = (
                self.confidence_score * (1 - sample_weight) +  # Old confidence
                self.success_rate * sample_weight  # New evidence
            )

    @classmethod
    def get_user_agent_knowledge(cls, user, agent_name, domain=None):
        """
        Get all learnings for a specific user-agent pair

        Args:
            user: User instance
            agent_name: Name of the agent
            domain: Optional domain filter

        Returns:
            QuerySet of learnings, ordered by confidence and recency
        """
        learnings = cls.objects.filter(
            user=user,
            agent_name=agent_name,
            is_active=True
        )

        if domain:
            learnings = learnings.filter(learning_domain=domain)

        # Filter out expired learnings
        learnings = learnings.filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now())
        )

        return learnings.order_by('-confidence_score', '-updated_at')

    @classmethod
    def create_learning(cls, user, agent_name, domain, content, source='success_pattern', confidence=0.5):
        """
        Create a new learning or update existing one

        Args:
            user: User instance
            agent_name: Name of the agent
            domain: Learning domain
            content: Learning content (JSON)
            source: Learning source
            confidence: Initial confidence score

        Returns:
            UserAgentLearning instance
        """
        learning, created = cls.objects.get_or_create(
            user=user,
            agent_name=agent_name,
            learning_domain=domain,
            defaults={
                'learning_content': content,
                'confidence_score': confidence,
                'learning_source': source,
                'context_metadata': {
                    'created_at': timezone.now().isoformat()
                }
            }
        )

        if not created:
            # Update existing learning
            learning.learning_content = content
            learning.confidence_score = confidence
            learning.save()

        return learning

    @classmethod
    def get_similar_users_learnings(cls, user, domain, min_confidence=0.6):
        """
        Collaborative filtering: Find learnings from similar users

        Args:
            user: Current user instance
            domain: Learning domain to find similar learnings
            min_confidence: Minimum confidence threshold

        Returns:
            QuerySet of learnings from similar users
        """
        # Get current user's learnings in this domain
        user_learnings = cls.objects.filter(
            user=user,
            learning_domain=domain,
            is_active=True,
            confidence_score__gte=min_confidence
        )

        if not user_learnings.exists():
            return cls.objects.none()

        # Find users with similar learnings
        similar_users = cls.objects.filter(
            learning_domain=domain,
            is_active=True,
            confidence_score__gte=min_confidence
        ).exclude(
            user=user
        ).values_list('user', flat=True).distinct()

        # Get their learnings in other domains
        return cls.objects.filter(
            user__in=similar_users,
            is_active=True,
            confidence_score__gte=min_confidence
        ).exclude(
            user=user
        ).order_by('-confidence_score', '-success_rate')

    @classmethod
    def get_collaborative_recommendations(cls, user, limit=10):
        """
        Get collaborative filtering recommendations across all agents

        "Users who learned X also learned Y"

        Args:
            user: User instance
            limit: Maximum number of recommendations

        Returns:
            List of recommended learning domains with reasoning
        """
        recommendations = []

        # Get user's current learnings
        user_learnings = cls.objects.filter(
            user=user,
            is_active=True,
            confidence_score__gte=0.5
        )

        if not user_learnings.exists():
            return recommendations

        user_domains = set(user_learnings.values_list('learning_domain', flat=True))

        # Find users with similar learnings
        similar_users_learnings = cls.objects.filter(
            learning_domain__in=user_domains,
            is_active=True,
            confidence_score__gte=0.6
        ).exclude(user=user).values_list('user', flat=True).distinct()

        # Get what they learned that current user hasn't
        other_learnings = cls.objects.filter(
            user__in=similar_users_learnings,
            is_active=True,
            confidence_score__gte=0.6
        ).exclude(
            learning_domain__in=user_domains
        ).values(
            'learning_domain', 'agent_name'
        ).annotate(
            count=models.Count('id'),
            avg_confidence=models.Avg('confidence_score'),
            avg_success=models.Avg('success_rate')
        ).order_by('-count', '-avg_confidence')[:limit]

        for learning_data in other_learnings:
            recommendations.append({
                'domain': learning_data['learning_domain'],
                'agent': learning_data['agent_name'],
                'similar_users_count': learning_data['count'],
                'avg_confidence': learning_data['avg_confidence'],
                'avg_success_rate': learning_data['avg_success'],
                'reason': f"{learning_data['count']} similar users found this valuable"
            })

        return recommendations

    @classmethod
    def share_learning_between_agents(cls, source_user, target_users, domain, min_confidence=0.7):
        """
        Share high-confidence learnings from one user to similar users
        Multi-agent learning propagation

        Args:
            source_user: User whose learning to share
            target_users: List of users to share with
            domain: Learning domain to share
            min_confidence: Minimum confidence to share

        Returns:
            Number of learnings shared
        """
        shared_count = 0

        # Get source user's high-confidence learnings
        source_learnings = cls.objects.filter(
            user=source_user,
            learning_domain=domain,
            is_active=True,
            confidence_score__gte=min_confidence
        )

        for learning in source_learnings:
            for target_user in target_users:
                # Check if target already has this learning
                existing = cls.objects.filter(
                    user=target_user,
                    agent_name=learning.agent_name,
                    learning_domain=learning.learning_domain
                ).first()

                if existing:
                    # Blend learnings - weighted average
                    existing.confidence_score = (
                        existing.confidence_score * 0.7 +  # Keep 70% of original
                        learning.confidence_score * 0.3     # Add 30% of shared
                    )
                    existing.learning_content = {
                        **existing.learning_content,
                        'shared_from_users': existing.learning_content.get('shared_from_users', []) + [source_user.id]
                    }
                    existing.save()
                else:
                    # Create new learning with lower confidence
                    cls.objects.create(
                        user=target_user,
                        agent_name=learning.agent_name,
                        learning_domain=learning.learning_domain,
                        learning_content={
                            **learning.learning_content,
                            'shared_from_user': source_user.id,
                            'collaborative': True
                        },
                        confidence_score=learning.confidence_score * 0.6,  # Reduce confidence for shared
                        learning_source='interaction_mining',
                        context_metadata={
                            'shared_at': timezone.now().isoformat(),
                            'original_confidence': learning.confidence_score
                        }
                    )

                shared_count += 1

        return shared_count

    def get_learning_cohort(self, min_similarity=0.5):
        """
        Find users with similar learning patterns

        Args:
            min_similarity: Minimum similarity score (0-1)

        Returns:
            List of similar users with similarity scores
        """
        # Get this user's learning profile
        user_profile = self.__class__.objects.filter(
            user=self.user,
            is_active=True
        ).values_list('learning_domain', 'confidence_score')

        user_domains = {domain: conf for domain, conf in user_profile}

        # Find users with overlapping learnings
        similar_users = []

        all_users = get_user_model().objects.exclude(id=self.user.id)

        for other_user in all_users:
            other_profile = self.__class__.objects.filter(
                user=other_user,
                is_active=True
            ).values_list('learning_domain', 'confidence_score')

            other_domains = {domain: conf for domain, conf in other_profile}

            # Calculate Jaccard similarity
            common_domains = set(user_domains.keys()) & set(other_domains.keys())
            all_domains = set(user_domains.keys()) | set(other_domains.keys())

            if len(all_domains) == 0:
                continue

            jaccard_similarity = len(common_domains) / len(all_domains)

            # Calculate confidence correlation for common domains
            if common_domains:
                conf_correlation = sum(
                    abs(user_domains[d] - other_domains[d])
                    for d in common_domains
                ) / len(common_domains)

                # Invert so higher is better (0 = identical, 1 = completely different)
                conf_correlation = 1 - conf_correlation
            else:
                conf_correlation = 0

            # Combined similarity score
            similarity = (jaccard_similarity + conf_correlation) / 2

            if similarity >= min_similarity:
                similar_users.append({
                    'user': other_user,
                    'similarity': similarity,
                    'common_learnings': len(common_domains)
                })

        return sorted(similar_users, key=lambda x: x['similarity'], reverse=True)


# =============================================================================
# Session 209: Spider Analytics Models
# =============================================================================

class SpiderAnalytics(models.Model):
    """
    Track spider performance and data quality metrics.

    This model stores daily aggregated statistics for each spider,
    enabling performance monitoring and optimization.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Spider identification
    spider_name = models.CharField(max_length=100, db_index=True)
    date = models.DateField(db_index=True)

    # Collection metrics
    items_collected = models.IntegerField(default=0)
    unique_topics = models.IntegerField(default=0)
    unique_sources = models.IntegerField(default=0)

    # Quality metrics
    avg_relevance_score = models.FloatField(default=0.0)
    data_freshness_hours = models.FloatField(default=0.0)  # Avg age of data

    # Performance metrics
    execution_time_seconds = models.FloatField(default=0.0)
    errors = models.IntegerField(default=0)
    success_rate = models.FloatField(default=1.0)  # 0.0 to 1.0

    # Storage metrics
    raw_data_size_kb = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        unique_together = ['spider_name', 'date']
        ordering = ['-date', 'spider_name']
        verbose_name = 'Spider Analytics'
        verbose_name_plural = 'Spider Analytics'

    def __str__(self):
        return f"{self.spider_name} - {self.date}"

    @classmethod
    def record_execution(
        cls,
        spider_name: str,
        items_collected: int,
        execution_time: float,
        errors: int = 0,
        topics: list = None,
        sources: list = None
    ):
        """
        Record a spider execution for analytics.

        Args:
            spider_name: Name of the spider
            items_collected: Number of items collected
            execution_time: Execution time in seconds
            errors: Number of errors encountered
            topics: List of extracted topics
            sources: List of data sources
        """
        from django.utils import timezone
        today = timezone.now().date()

        analytics, created = cls.objects.get_or_create(
            spider_name=spider_name,
            date=today,
            defaults={
                'items_collected': items_collected,
                'execution_time_seconds': execution_time,
                'errors': errors,
                'unique_topics': len(topics) if topics else 0,
                'unique_sources': len(sources) if sources else 0,
                'success_rate': 1.0 if errors == 0 else 0.5,
            }
        )

        if not created:
            # Update existing record
            analytics.items_collected += items_collected
            analytics.execution_time_seconds += execution_time
            analytics.errors += errors
            if topics:
                analytics.unique_topics += len(topics)
            if sources:
                analytics.unique_sources += len(sources)
            analytics.success_rate = 1 - (analytics.errors / max(1, analytics.items_collected + analytics.errors))
            analytics.save()

        return analytics

    @classmethod
    def get_spider_performance(cls, spider_name: str, days: int = 7) -> dict:
        """Get performance summary for a spider over the given period."""
        from django.utils import timezone
        from django.db.models import Sum, Avg

        since = timezone.now().date() - timezone.timedelta(days=days)

        stats = cls.objects.filter(
            spider_name=spider_name,
            date__gte=since
        ).aggregate(
            total_items=Sum('items_collected'),
            total_errors=Sum('errors'),
            avg_execution_time=Avg('execution_time_seconds'),
            avg_success_rate=Avg('success_rate'),
            total_topics=Sum('unique_topics'),
        )

        return {
            'spider_name': spider_name,
            'period_days': days,
            'total_items': stats['total_items'] or 0,
            'total_errors': stats['total_errors'] or 0,
            'avg_execution_time': stats['avg_execution_time'] or 0,
            'avg_success_rate': stats['avg_success_rate'] or 0,
            'total_topics': stats['total_topics'] or 0,
        }


# Session 484: Spider Execution Log for Error Diagnostics
class SpiderExecutionLog(models.Model):
    """
    Track individual spider execution runs with full error details.

    Session 484: Created for Spider Health Dashboard error diagnostics.
    Enables viewing stack traces, retry functionality, and execution history.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Spider identification
    spider_name = models.CharField(max_length=100, db_index=True)
    category = models.CharField(max_length=50, default='general')

    # Execution details
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('success', 'Success'),
        ('partial', 'Partial Success'),
        ('error', 'Error'),
        ('timeout', 'Timeout'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')

    TRIGGER_CHOICES = [
        ('scheduled', 'Scheduled (Celery Beat)'),
        ('manual', 'Manual (UI)'),
        ('on_demand', 'On Demand (API)'),
        ('retry', 'Retry'),
        ('trigger', 'Event Trigger'),
    ]
    triggered_by = models.CharField(max_length=20, choices=TRIGGER_CHOICES, default='scheduled')

    # Results
    items_collected = models.IntegerField(default=0)
    duration_seconds = models.FloatField(null=True, blank=True)

    # Error details (the key part for diagnostics)
    error_message = models.TextField(blank=True)
    error_traceback = models.TextField(blank=True, help_text="Full stack trace for debugging")
    error_type = models.CharField(max_length=200, blank=True, help_text="Exception class name")

    # Metadata
    celery_task_id = models.CharField(max_length=100, blank=True, db_index=True)
    source_urls_attempted = models.JSONField(default=list, help_text="URLs spider tried to fetch")
    response_codes = models.JSONField(default=dict, help_text="HTTP response codes received")

    # Retry tracking
    retry_count = models.IntegerField(default=0)
    parent_execution = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='retries', help_text="Original execution if this is a retry"
    )

    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ['-started_at']
        verbose_name = 'Spider Execution Log'
        verbose_name_plural = 'Spider Execution Logs'
        indexes = [
            models.Index(fields=['spider_name', '-started_at']),
            models.Index(fields=['status', '-started_at']),
            models.Index(fields=['-started_at']),
        ]

    def __str__(self):
        return f"{self.spider_name} - {self.status} ({self.started_at.strftime('%Y-%m-%d %H:%M')})"

    @classmethod
    def start_execution(cls, spider_name: str, category: str = 'general',
                        triggered_by: str = 'scheduled', celery_task_id: 'str | None' = None):
        """Create a new execution log entry when spider starts."""
        return cls.objects.create(
            spider_name=spider_name,
            category=category,
            triggered_by=triggered_by,
            celery_task_id=celery_task_id or '',  # Convert None to empty string
            status='running'
        )

    def complete_success(self, items_collected: int, duration_seconds: float = None):
        """Mark execution as successful."""
        from django.utils import timezone
        self.status = 'success' if items_collected > 0 else 'partial'
        self.items_collected = items_collected
        self.completed_at = timezone.now()
        if duration_seconds is not None:
            self.duration_seconds = duration_seconds
        elif self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        self.save()

    def complete_error(self, error_message: str = None, error_type: str = None,
                       error_traceback: str = None, duration_seconds: float = None,
                       error: Exception = None):
        """
        Mark execution as failed with error details.
        Can accept either an Exception object or separate error details.
        """
        import traceback as tb
        from django.utils import timezone

        self.status = 'error'

        # Accept either Exception object or explicit parameters
        if error is not None:
            self.error_message = str(error)[:2000]
            self.error_type = type(error).__name__
            self.error_traceback = tb.format_exc()[:10000]
        else:
            if error_message:
                self.error_message = error_message[:2000]
            if error_type:
                self.error_type = error_type[:200]
            if error_traceback:
                self.error_traceback = error_traceback[:10000]

        self.completed_at = timezone.now()
        if duration_seconds is not None:
            self.duration_seconds = duration_seconds
        elif self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        self.save()

    @classmethod
    def get_recent_errors(cls, hours: int = 24, limit: int = 50):
        """Get recent error executions for diagnostics."""
        from django.utils import timezone
        since = timezone.now() - timezone.timedelta(hours=hours)
        return cls.objects.filter(
            status='error',
            started_at__gte=since
        ).order_by('-started_at')[:limit]

    @classmethod
    def get_spider_health(cls, spider_name: str, days: int = 7):
        """Get health summary for a specific spider."""
        from django.utils import timezone
        from django.db.models import Avg

        since = timezone.now() - timezone.timedelta(days=days)
        executions = cls.objects.filter(
            spider_name=spider_name,
            started_at__gte=since
        )

        total = executions.count()
        success = executions.filter(status__in=['success', 'partial']).count()
        errors = executions.filter(status='error').count()
        avg_duration = executions.filter(
            duration_seconds__isnull=False
        ).aggregate(avg=Avg('duration_seconds'))['avg']

        return {
            'spider_name': spider_name,
            'period_days': days,
            'total_executions': total,
            'successful': success,
            'errors': errors,
            'success_rate': (success / total * 100) if total > 0 else 0,
            'avg_duration_seconds': round(avg_duration or 0, 2),
            'last_error': executions.filter(status='error').first(),
        }


class TrendSnapshot(models.Model):
    """
    Store trending topic snapshots over time.

    This enables historical trend analysis and tracking
    how topics rise and fall in popularity.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Topic identification
    topic = models.CharField(max_length=200, db_index=True)
    category = models.CharField(max_length=50, db_index=True, blank=True, default='')

    # Trend metrics
    score = models.FloatField(default=0.0)  # Calculated trend score
    mention_count = models.IntegerField(default=1)
    source_count = models.IntegerField(default=1)

    # Sources tracking
    sources = models.JSONField(default=list)  # List of spider names

    # Time tracking
    first_seen = models.DateTimeField()
    last_seen = models.DateTimeField()
    snapshot_date = models.DateField(db_index=True)

    # Velocity (change tracking)
    previous_score = models.FloatField(default=0.0)
    score_change = models.FloatField(default=0.0)  # Positive = rising, negative = falling
    is_emerging = models.BooleanField(default=False)  # New/fast-growing topic
    is_declining = models.BooleanField(default=False)  # Losing momentum

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        unique_together = ['topic', 'snapshot_date']
        ordering = ['-snapshot_date', '-score']
        verbose_name = 'Trend Snapshot'
        verbose_name_plural = 'Trend Snapshots'

    def __str__(self):
        return f"{self.topic} ({self.snapshot_date}) - Score: {self.score:.2f}"

    @classmethod
    def capture_snapshot(cls, trends: list, category: str = '') -> list:
        """
        Capture a snapshot of current trends.

        Args:
            trends: List of trend dicts from SpiderIntelligenceService
            category: Optional category filter

        Returns:
            List of created/updated TrendSnapshot objects
        """
        from django.utils import timezone
        now = timezone.now()
        today = now.date()

        snapshots = []
        for trend in trends:
            topic = trend.get('topic', '')
            if not topic:
                continue

            # Get or create snapshot for today
            snapshot, created = cls.objects.get_or_create(
                topic=topic,
                snapshot_date=today,
                defaults={
                    'category': category,
                    'score': trend.get('score', 0),
                    'mention_count': trend.get('mentions', 1),
                    'source_count': trend.get('source_count', 1),
                    'sources': trend.get('sources', []),
                    'first_seen': now,
                    'last_seen': now,
                }
            )

            if not created:
                # Update existing
                snapshot.previous_score = snapshot.score
                snapshot.score = trend.get('score', snapshot.score)
                snapshot.mention_count = trend.get('mentions', snapshot.mention_count)
                snapshot.source_count = trend.get('source_count', snapshot.source_count)
                snapshot.sources = trend.get('sources', snapshot.sources)
                snapshot.last_seen = now

                # Calculate change
                if snapshot.previous_score > 0:
                    snapshot.score_change = (snapshot.score - snapshot.previous_score) / snapshot.previous_score
                else:
                    snapshot.score_change = 1.0 if snapshot.score > 0 else 0

                # Mark emerging/declining
                snapshot.is_emerging = snapshot.score_change > 0.2  # 20% growth
                snapshot.is_declining = snapshot.score_change < -0.2  # 20% decline

                snapshot.save()

            snapshots.append(snapshot)

        return snapshots

    @classmethod
    def get_trend_history(cls, topic: str, days: int = 30) -> list:
        """Get historical trend data for a topic."""
        from django.utils import timezone

        since = timezone.now().date() - timezone.timedelta(days=days)

        return list(cls.objects.filter(
            topic=topic,
            snapshot_date__gte=since
        ).order_by('snapshot_date').values(
            'snapshot_date', 'score', 'mention_count', 'source_count'
        ))

    @classmethod
    def get_emerging_trends(cls, days: int = 7, limit: int = 10) -> list:
        """Get topics that are emerging (fast-growing)."""
        from django.utils import timezone

        since = timezone.now().date() - timezone.timedelta(days=days)

        return list(cls.objects.filter(
            snapshot_date__gte=since,
            is_emerging=True
        ).order_by('-score_change')[:limit].values(
            'topic', 'score', 'score_change', 'mention_count', 'sources'
        ))

    @classmethod
    def get_declining_trends(cls, days: int = 7, limit: int = 10) -> list:
        """Get topics that are declining (losing momentum)."""
        from django.utils import timezone

        since = timezone.now().date() - timezone.timedelta(days=days)

        return list(cls.objects.filter(
            snapshot_date__gte=since,
            is_declining=True
        ).order_by('score_change')[:limit].values(
            'topic', 'score', 'score_change', 'mention_count', 'sources'
        ))


# =============================================================================
# Session 210: Implicit Learning Models
# =============================================================================

class UserBehaviorSignal(models.Model):
    """
    DEPRECATED - Session 528: This model has 0 records and is not used.

    Original purpose: Track individual user behavior signals for implicit learning.
    Each signal represents a user action (download, share, delete, etc.)
    that indicates their preference toward certain styles/models.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # User and content
    user_id = models.IntegerField(db_index=True)
    content_id = models.CharField(max_length=100, db_index=True, blank=True, default='')

    # Signal type and weight
    signal_type = models.CharField(max_length=50, db_index=True)
    # Types: 'generation', 'download', 'share', 'delete', 'view_long', 'view_short',
    #        'regenerate', 'style_use', 'favorite'

    weight = models.FloatField(default=0.0)
    # Weight indicates signal strength: positive = liked, negative = disliked
    # share=1.0, download=0.7, favorite=0.8, view_long=0.4, delete=-0.5, etc.

    # Metadata (style, model, prompt keywords, etc.)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id', 'signal_type']),
            models.Index(fields=['user_id', 'created_at']),
        ]
        verbose_name = 'User Behavior Signal'
        verbose_name_plural = 'User Behavior Signals'

    def __str__(self):
        return f"User {self.user_id} - {self.signal_type} ({self.weight:+.2f})"


class UserPreferenceProfile(models.Model):
    """
    Aggregated user preference profile built from behavior signals.

    This is updated incrementally as new signals come in, providing
    a quick lookup of user preferences without recalculating.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user_id = models.IntegerField(unique=True, db_index=True)

    # Aggregated scores
    style_scores = models.JSONField(default=dict)  # {"cyberpunk": 5.2, "anime": 3.1, ...}
    model_scores = models.JSONField(default=dict)  # {"stable-diffusion": 4.0, "dall-e": 2.5}

    # Quick access fields
    top_styles = models.JSONField(default=list)  # Top 5 styles
    top_models = models.JSONField(default=list)  # Top 3 models

    # Stats
    total_signals = models.IntegerField(default=0)
    total_generations = models.IntegerField(default=0)
    total_downloads = models.IntegerField(default=0)
    total_shares = models.IntegerField(default=0)

    # Confidence in preferences (0-1)
    confidence = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'User Preference Profile'
        verbose_name_plural = 'User Preference Profiles'

    def __str__(self):
        return f"Preferences for User {self.user_id} ({self.total_signals} signals)"

    def get_top_style(self) -> str:
        """Get user's favorite style."""
        if self.top_styles:
            return self.top_styles[0]
        if self.style_scores:
            return max(self.style_scores.items(), key=lambda x: x[1])[0]
        return None

    def recalculate_top_styles(self):
        """Recalculate top styles from scores."""
        if self.style_scores:
            sorted_styles = sorted(
                self.style_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            self.top_styles = [s[0] for s in sorted_styles[:5]]

    def recalculate_top_models(self):
        """Recalculate top models from scores."""
        if self.model_scores:
            sorted_models = sorted(
                self.model_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            self.top_models = [m[0] for m in sorted_models[:3]]


class StyleEvolution(models.Model):
    """
    Track how user's style preferences evolve over time.

    Daily snapshots of style distribution allow us to see
    how preferences change and identify trends.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user_id = models.IntegerField(db_index=True)
    date = models.DateField(db_index=True)
    domain = models.CharField(max_length=50, default='image')  # image, video, audio, 3d

    # Style distribution for this day
    style_distribution = models.JSONField(default=dict)
    # {"cyberpunk": 0.35, "anime": 0.25, "watercolor": 0.15, ...}

    # Top styles for quick access
    top_styles = models.JSONField(default=list)  # ["cyberpunk", "anime", "watercolor"]

    # Metrics
    total_generations = models.IntegerField(default=0)
    total_downloads = models.IntegerField(default=0)
    satisfaction_rate = models.FloatField(default=0.0)  # Downloads / Generations

    # Confidence in this snapshot (based on data volume)
    confidence = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        unique_together = ['user_id', 'date', 'domain']
        ordering = ['-date']
        verbose_name = 'Style Evolution'
        verbose_name_plural = 'Style Evolutions'

    def __str__(self):
        return f"User {self.user_id} - {self.date} ({self.domain})"

    @classmethod
    def capture_daily_snapshot(cls, user_id: int, domain: str = 'image'):
        """Capture a daily snapshot of user's style preferences."""
        from django.utils import timezone

        today = timezone.now().date()

        # Get today's signals for this user
        signals = UserBehaviorSignal.objects.filter(
            user_id=user_id,
            created_at__date=today
        )

        # Calculate style distribution
        style_counts = {}
        total_weight = 0

        for signal in signals:
            style = (signal.metadata or {}).get('style')
            if style and signal.weight > 0:
                style_counts[style] = style_counts.get(style, 0) + signal.weight
                total_weight += signal.weight

        # Normalize to distribution
        style_distribution = {}
        if total_weight > 0:
            style_distribution = {
                k: v / total_weight
                for k, v in style_counts.items()
            }

        # Get top styles
        top_styles = sorted(
            style_distribution.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        top_style_names = [s[0] for s in top_styles]

        # Calculate metrics
        total_generations = signals.filter(signal_type='generation').count()
        total_downloads = signals.filter(signal_type='download').count()
        satisfaction = total_downloads / max(1, total_generations)

        # Create or update snapshot
        snapshot, created = cls.objects.update_or_create(
            user_id=user_id,
            date=today,
            domain=domain,
            defaults={
                'style_distribution': style_distribution,
                'top_styles': top_style_names,
                'total_generations': total_generations,
                'total_downloads': total_downloads,
                'satisfaction_rate': satisfaction,
                'confidence': min(1.0, total_generations / 10),
            }
        )

        return snapshot

    @classmethod
    def get_evolution_timeline(cls, user_id: int, days: int = 30, domain: str = 'image'):
        """Get user's style evolution over time."""
        from django.utils import timezone

        since = timezone.now().date() - timezone.timedelta(days=days)

        return list(cls.objects.filter(
            user_id=user_id,
            domain=domain,
            date__gte=since
        ).order_by('date').values(
            'date', 'style_distribution', 'top_styles',
            'total_generations', 'satisfaction_rate'
        ))


class StyleTrend(models.Model):
    """
    Track global style trends across all users.

    This helps identify what's popular and can inform recommendations.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    style_name = models.CharField(max_length=100, db_index=True)
    date = models.DateField(db_index=True)
    domain = models.CharField(max_length=50, default='image')

    # Usage metrics
    usage_count = models.IntegerField(default=0)  # Total uses
    unique_users = models.IntegerField(default=0)  # Unique users
    download_count = models.IntegerField(default=0)  # Downloads

    # Quality metrics
    avg_satisfaction = models.FloatField(default=0.0)  # Avg download rate

    # Trend indicators
    previous_usage = models.IntegerField(default=0)
    growth_rate = models.FloatField(default=0.0)  # Percentage growth from yesterday
    is_trending = models.BooleanField(default=False)  # Fast growth
    is_declining = models.BooleanField(default=False)  # Losing popularity

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        unique_together = ['style_name', 'date', 'domain']
        ordering = ['-date', '-usage_count']
        verbose_name = 'Style Trend'
        verbose_name_plural = 'Style Trends'

    def __str__(self):
        status = "📈" if self.is_trending else ("📉" if self.is_declining else "")
        return f"{self.style_name} - {self.date} ({self.usage_count} uses) {status}"

    @classmethod
    def get_trending_styles(cls, days: int = 7, limit: int = 10, domain: str = 'image'):
        """Get currently trending styles."""
        from django.utils import timezone

        since = timezone.now().date() - timezone.timedelta(days=days)

        return list(cls.objects.filter(
            date__gte=since,
            domain=domain,
            is_trending=True
        ).order_by('-growth_rate')[:limit].values(
            'style_name', 'usage_count', 'growth_rate', 'avg_satisfaction'
        ))

    @classmethod
    def get_popular_styles(cls, days: int = 7, limit: int = 10, domain: str = 'image'):
        """Get most popular styles by usage."""
        from django.utils import timezone
        from django.db.models import Sum

        since = timezone.now().date() - timezone.timedelta(days=days)

        return list(cls.objects.filter(
            date__gte=since,
            domain=domain
        ).values('style_name').annotate(
            total_usage=Sum('usage_count'),
            total_downloads=Sum('download_count')
        ).order_by('-total_usage')[:limit])


# =============================================================================
# SESSION 211: A/B TESTING FRAMEWORK
# =============================================================================

class ABExperiment(models.Model):
    """
    Define an A/B test experiment.

    Experiments can test different recommendation strategies, UI variations,
    or any feature where we want to measure user engagement.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Experiment type
    EXPERIMENT_TYPES = [
        ('recommendation', 'Recommendation Strategy'),
        ('ui', 'UI Variation'),
        ('feature', 'Feature Toggle'),
        ('algorithm', 'Algorithm Comparison'),
    ]
    experiment_type = models.CharField(max_length=50, choices=EXPERIMENT_TYPES, default='recommendation')

    # Domain (what area of the app)
    domain = models.CharField(max_length=50, default='style_recommendations')

    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Traffic allocation (percentage of users to include)
    traffic_percentage = models.IntegerField(default=100)  # 0-100

    # Timing
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    # Success metric
    primary_metric = models.CharField(max_length=100, default='conversion_rate')
    # conversion_rate, click_rate, engagement_time, satisfaction_score

    # Configuration
    config = models.JSONField(default=dict, blank=True)
    # {"min_sample_size": 100, "confidence_level": 0.95}

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by_id = models.IntegerField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        verbose_name = 'A/B Experiment'
        verbose_name_plural = 'A/B Experiments'

    def __str__(self):
        return f"{self.name} ({self.status})"

    @property
    def is_active(self):
        """Check if experiment is currently active."""
        from django.utils import timezone
        now = timezone.now()

        if self.status != 'running':
            return False

        if self.start_date and now < self.start_date:
            return False

        if self.end_date and now > self.end_date:
            return False

        return True


class ABVariant(models.Model):
    """
    A variant within an A/B experiment.

    Each experiment has at least 2 variants (control + treatment).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    experiment = models.ForeignKey(ABExperiment, on_delete=models.CASCADE, related_name='variants')

    name = models.CharField(max_length=100)  # 'control', 'variant_a', 'variant_b'
    description = models.TextField(blank=True)

    is_control = models.BooleanField(default=False)

    # Traffic weight within this experiment (relative to other variants)
    weight = models.IntegerField(default=50)  # Default 50/50 split

    # Variant configuration (what's different about this variant)
    config = models.JSONField(default=dict)
    # For recommendations: {"strategy": "temporal_first", "boost_trending": true}
    # For UI: {"button_color": "green", "show_explanations": true}

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['is_control', 'name']
        verbose_name = 'A/B Variant'
        verbose_name_plural = 'A/B Variants'

    def __str__(self):
        control = " (control)" if self.is_control else ""
        return f"{self.experiment.name} - {self.name}{control}"


class ABAssignment(models.Model):
    """
    Track which variant a user is assigned to.

    Users are consistently assigned to the same variant for the duration
    of an experiment (sticky assignment).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    experiment = models.ForeignKey(ABExperiment, on_delete=models.CASCADE, related_name='assignments')
    variant = models.ForeignKey(ABVariant, on_delete=models.CASCADE, related_name='assignments')

    user_id = models.IntegerField(db_index=True)
    # Or for anonymous users:
    session_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)

    assigned_at = models.DateTimeField(auto_now_add=True)

    # Track if user has seen the variant (exposure)
    exposed = models.BooleanField(default=False)
    exposed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        unique_together = [
            ['experiment', 'user_id'],
            ['experiment', 'session_id'],
        ]
        verbose_name = 'A/B Assignment'
        verbose_name_plural = 'A/B Assignments'

    def __str__(self):
        user = f"User {self.user_id}" if self.user_id else f"Session {self.session_id}"
        return f"{user} -> {self.variant.name}"


class ABConversion(models.Model):
    """
    Track conversions (successful outcomes) for A/B tests.

    A conversion is when a user takes the desired action
    (e.g., applies a recommended style, downloads content).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    assignment = models.ForeignKey(ABAssignment, on_delete=models.CASCADE, related_name='conversions')

    # What action triggered the conversion
    CONVERSION_TYPES = [
        ('click', 'Clicked Recommendation'),
        ('apply', 'Applied Style'),
        ('download', 'Downloaded Content'),
        ('share', 'Shared Content'),
        ('purchase', 'Made Purchase'),
        ('signup', 'Signed Up'),
        ('engagement', 'Engaged with Feature'),
    ]
    conversion_type = models.CharField(max_length=50, choices=CONVERSION_TYPES)

    # Value of the conversion (for revenue tracking)
    value = models.FloatField(default=1.0)

    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)
    # {"style_applied": "cyberpunk", "time_to_convert": 5.2}

    converted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-converted_at']
        verbose_name = 'A/B Conversion'
        verbose_name_plural = 'A/B Conversions'

    def __str__(self):
        return f"{self.assignment} - {self.conversion_type}"


class ABExperimentResult(models.Model):
    """
    Cached/computed results for an experiment.

    Updated periodically to avoid recalculating on every request.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    experiment = models.OneToOneField(ABExperiment, on_delete=models.CASCADE, related_name='results')

    # Per-variant statistics (JSON)
    variant_stats = models.JSONField(default=dict)
    # {
    #     "variant_id": {
    #         "assignments": 150,
    #         "exposures": 140,
    #         "conversions": 35,
    #         "conversion_rate": 0.25,
    #         "total_value": 35.0,
    #         "avg_value": 1.0
    #     }
    # }

    # Statistical significance
    is_significant = models.BooleanField(default=False)
    confidence_level = models.FloatField(default=0.0)  # 0.0 to 1.0
    p_value = models.FloatField(null=True, blank=True)

    # Winner (if significant)
    winning_variant = models.ForeignKey(
        ABVariant, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='won_experiments'
    )
    lift_percentage = models.FloatField(null=True, blank=True)  # % improvement over control

    # Timing
    computed_at = models.DateTimeField(auto_now=True)
    sample_size = models.IntegerField(default=0)

    class Meta:
        app_label = 'core'
        verbose_name = 'A/B Experiment Result'
        verbose_name_plural = 'A/B Experiment Results'

    def __str__(self):
        status = "Significant" if self.is_significant else "Not Significant"
        return f"{self.experiment.name} Results ({status})"


# =============================================================================
# SESSION 212: CUSTOM WORKFLOW BUILDER MODELS
# =============================================================================

class CustomWorkflow(models.Model):
    """
    User-created custom workflow templates.

    Session 212: Allows users to create, save, and share their own workflows.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Ownership
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='custom_workflows'
    )

    # Basic info
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)  # URL-friendly name
    description = models.TextField(blank=True)
    content_type = models.CharField(max_length=50, default='custom')
    category = models.CharField(max_length=50, default='custom')

    # Sharing
    is_public = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    use_count = models.IntegerField(default=0)

    # Configuration
    config = models.JSONField(default=dict, blank=True)  # Global workflow config

    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    schedule_cron = models.CharField(max_length=100, blank=True)  # Cron expression
    last_run_at = models.DateTimeField(null=True, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True)

    # Session 764: Orchestration Layer Configuration
    EXECUTION_MODE_CHOICES = [
        ('sequential', 'Sequential'),  # Steps run one after another
        ('parallel', 'Parallel'),  # Independent steps run in parallel
        ('dependency', 'Dependency-Based'),  # Steps run based on depends_on_steps
    ]
    execution_mode = models.CharField(
        max_length=20, choices=EXECUTION_MODE_CHOICES, default='sequential'
    )
    max_retries = models.IntegerField(default=3)  # Max retries per step
    timeout_seconds = models.IntegerField(default=3600)  # Workflow timeout (1 hour default)
    require_approval_on_error = models.BooleanField(default=True)  # Pause for human on error
    cost_budget = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True,
        help_text="Maximum allowed cost for workflow execution"
    )

    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Custom Workflow'
        verbose_name_plural = 'Custom Workflows'
        ordering = ['-updated_at']
        unique_together = [('created_by', 'slug')]

    def __str__(self):
        return f"{self.name} (by {self.created_by})"

    def to_workflow_definition(self):
        """Convert to the format expected by WorkflowOrchestrationAgent."""
        return {
            'description': self.description,
            'content_type': self.content_type,
            'steps': [step.to_step_definition() for step in self.steps.all().order_by('order')]
        }


class CustomWorkflowStep(models.Model):
    """
    Individual step within a custom workflow.

    Session 212: Each step references an agent and defines parameters.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    workflow = models.ForeignKey(
        CustomWorkflow, on_delete=models.CASCADE,
        related_name='steps'
    )

    # Step definition
    order = models.IntegerField()  # 1, 2, 3...
    name = models.CharField(max_length=100)  # Human-readable step name
    description = models.TextField(blank=True)

    # Agent reference - Session 764: Expanded to include all routable agents
    AGENT_CHOICES = [
        # Creation Agents
        ('ImageAgent', 'Image Generation'),
        ('VideoAgent', 'Video Generation'),
        ('AudioAgent', 'Audio Generation'),
        ('ThreeDAgent', '3D Model Generation'),
        # Editing Agents
        ('ImageEditingAgent', 'Image Editing'),
        ('VideoEditingAgent', 'Video Editing'),
        # Research Agents
        ('ResearchAgent', 'Research'),
        # Writing Agents
        ('ContentWriterAgent', 'Content Writing'),
        # Strategy Agents
        ('ContentStrategyAgent', 'Content Strategy'),
        ('BrandIdentityAgent', 'Brand Identity'),
        ('SEOOptimizerAgent', 'SEO Optimization'),
        ('SocialMediaAgent', 'Social Media'),
        # Executive Agents
        ('CTOAgent', 'CTO Review'),
        ('COOAgent', 'COO Review'),
        ('CreativeDirectorAgent', 'Creative Direction'),
        ('MeetingCoordinatorAgent', 'Meeting Coordination'),
        # Analysis Agents
        ('TrendAnalysisAgent', 'Trend Analysis'),
        ('OpportunityScoringAgent', 'Opportunity Scoring'),
        # Training Agents
        ('CharacterTrainingAgent', 'Character Training'),
        ('TrainedCreationAgent', 'Trained Creation'),
        # Security Agents
        ('MemoryIsolationAgent', 'Memory Isolation'),
        ('ContentAuditAgent', 'Content Audit'),
        # Business Research Agents
        ('CompetitorAnalysisAgent', 'Competitor Analysis'),
        ('CustomerResearchAgent', 'Customer Research'),
        ('BrandStrategyAgent', 'Brand Strategy'),
        ('MarketingStrategyAgent', 'Marketing Strategy'),
        ('MarketIntelligenceAgent', 'Market Intelligence'),
        # Legal Agents
        ('LegalDocDrafterAgent', 'Legal Document Drafting'),
        # Development Agents
        ('CodeGeneratorAgent', 'Code Generation'),
        ('FullStackDeveloperAgent', 'Full Stack Development'),
        ('CodeReviewAgent', 'Code Review'),
        ('DevOpsAgent', 'DevOps'),
        # Stock/Market Agents
        ('StockAuditCoordinator', 'Stock Audit Coordination'),
        ('StockAnalystAgent', 'Stock Analysis'),
        ('MarketMovementMonitorAgent', 'Market Movement Monitor'),
        ('BullCaseAgent', 'Bull Case Analysis'),
        ('BearCaseAgent', 'Bear Case Analysis'),
        ('SignalScannerAgent', 'Signal Scanning'),
        # Blockchain Agents
        ('BlockchainAuditCoordinator', 'Blockchain Audit'),
        ('SmartContractAuditorAgent', 'Smart Contract Audit'),
        ('TransactionMonitorAgent', 'Transaction Monitor'),
        ('WhaleWatcherAgent', 'Whale Watcher'),
        ('ExploitDetectorAgent', 'Exploit Detection'),
        # Narrative Agents
        ('NarrativeDriftCoordinator', 'Narrative Drift'),
        ('NarrativeHistorianAgent', 'Narrative History'),
        ('TrendBreakDetectorAgent', 'Trend Break Detection'),
        ('CulturalImpactAgent', 'Cultural Impact'),
        # Content Studio Agents
        ('AutonomousContentStudioCoordinator', 'Autonomous Content Studio'),
        ('TopicMinerAgent', 'Topic Mining'),
        ('ContrarianAgent', 'Contrarian Analysis'),
        ('PerformanceAnalystAgent', 'Performance Analysis'),
        ('ContentDiversityOrchestrator', 'Content Diversity'),
        # Rendering Agents
        ('ResolveAgent', 'Resolve Rendering'),
        # Podcast Studio Agents
        ('PodcastCoordinatorAgent', 'Podcast Coordination'),
        ('DebateAdvocateAgent', 'Debate Advocate'),
        ('DebateSkepticAgent', 'Debate Skeptic'),
        ('ModeratorAgent', 'Debate Moderation'),
        # Orchestration Agents
        ('WorkflowAgent', 'Workflow Orchestration'),
        ('WorkflowOrchestrationAgent', 'Workflow Orchestration (Advanced)'),
        ('CampaignOrchestratorAgent', 'Campaign Orchestration'),
        ('OpportunityPipelineAgent', 'Opportunity Pipeline'),
        ('ContentExecutorAgent', 'Content Execution'),
        # Markets Agents
        ('PredictionMarketAnalyst', 'Prediction Market Analysis'),
        ('SportsOddsAnalyst', 'Sports Odds Analysis'),
        ('ArbitrageDetector', 'Arbitrage Detection'),
        # Special Agents
        ('ThinkingAgent', 'AI Thinking'),
        ('TechnicalDocumentAgent', 'Technical Documentation'),
        ('SystemIntelligenceAgent', 'System Intelligence'),
        ('PersonalAssistantAgent', 'Personal Assistant'),
    ]
    agent = models.CharField(max_length=100, choices=AGENT_CHOICES)

    # Step configuration
    config = models.JSONField(default=dict, blank=True)  # Step-specific config
    # Example config: {"prompt_template": "...", "width": 1024, "height": 1024}

    # Conditional execution
    condition = models.JSONField(default=dict, blank=True)  # Run if condition met
    # Example: {"previous_step_success": true, "has_images": true}

    # Error handling
    is_required = models.BooleanField(default=True)  # If false, workflow continues on failure
    retry_count = models.IntegerField(default=0)  # Number of retries on failure

    # Session 764: Orchestration Layer - Step Configuration
    timeout_seconds = models.IntegerField(
        default=300, help_text="Step timeout in seconds (5 min default)"
    )
    requires_approval = models.BooleanField(
        default=False, help_text="Pause for human approval before proceeding"
    )
    approval_config = models.JSONField(
        default=dict, blank=True,
        help_text="Approval configuration: timeout_hours, auto_approve, message"
    )
    # Example: {"timeout_hours": 24, "auto_approve_on_timeout": False, "approval_message": "Review output"}

    depends_on_steps = models.JSONField(
        default=list, blank=True,
        help_text="List of step orders this step depends on (for parallel execution)"
    )
    # Example: [1, 2] means this step waits for steps 1 and 2 to complete

    rollback_step = models.IntegerField(
        null=True, blank=True,
        help_text="Step order to execute if this step fails (for rollback)"
    )
    cost_limit = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True,
        help_text="Maximum allowed cost for this step"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Custom Workflow Step'
        verbose_name_plural = 'Custom Workflow Steps'
        ordering = ['workflow', 'order']
        unique_together = [('workflow', 'order')]

    def __str__(self):
        return f"Step {self.order}: {self.name} ({self.agent})"

    def to_step_definition(self):
        """Convert to the format expected by WorkflowOrchestrationAgent."""
        return {
            'step': self.order,
            'name': self.name,
            'agent': self.agent,
            'description': self.description,
            'config': self.config,
        }


class WorkflowExecution(models.Model):
    """
    DEPRECATED: Use content.models.WorkflowExecution instead.

    This model is deprecated as of Session 287 (HANDOFF_04).
    Use content.models.WorkflowExecution which is linked to ContentWorkflow.

    Track workflow execution history.
    Session 212: Records each time a workflow (built-in or custom) is executed.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Execution info
    workflow_type = models.CharField(max_length=50)  # 'builtin' or 'custom'
    workflow_name = models.CharField(max_length=200)
    custom_workflow = models.ForeignKey(
        CustomWorkflow, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='executions'
    )

    # User who triggered
    executed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='core_workflow_executions'
    )

    # Execution parameters
    topic = models.CharField(max_length=500)
    parameters = models.JSONField(default=dict)

    # Results
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    step_results = models.JSONField(default=list)  # List of step outcomes
    error_message = models.TextField(blank=True)

    # Output references
    project_id = models.UUIDField(null=True, blank=True)
    image_ids = models.JSONField(default=list)
    video_ids = models.JSONField(default=list)

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Workflow Execution'
        verbose_name_plural = 'Workflow Executions'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.workflow_name} ({self.status}) - {self.topic[:50]}"

    def save(self, *args, **kwargs):
        warnings.warn(
            "core.WorkflowExecution is deprecated. Use content.models.WorkflowExecution instead.",
            DeprecationWarning,
            stacklevel=2
        )
        logger.warning("DEPRECATED: core.WorkflowExecution used - migrate to content.models.WorkflowExecution")
        super().save(*args, **kwargs)

    def complete(self, success: bool, error: str = None):
        """Mark workflow as complete."""
        self.status = 'completed' if success else 'failed'
        self.error_message = error or ''
        self.completed_at = timezone.now()
        self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        self.save()


class ScheduledWorkflow(models.Model):
    """
    Track scheduled workflow runs.

    Session 212: Manages scheduled workflow executions via Celery Beat.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Workflow reference
    custom_workflow = models.OneToOneField(
        CustomWorkflow, on_delete=models.CASCADE,
        related_name='schedule'
    )

    # Schedule info
    cron_expression = models.CharField(max_length=100)  # e.g., "0 9 * * 1" (9am every Monday)
    timezone = models.CharField(max_length=50, default='America/Denver')

    # Default parameters for scheduled runs
    default_topic = models.CharField(max_length=500)
    default_parameters = models.JSONField(default=dict)

    # Status
    is_active = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    last_run_status = models.CharField(max_length=20, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True)
    run_count = models.IntegerField(default=0)

    # Celery task reference
    celery_task_id = models.CharField(max_length=200, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Scheduled Workflow'
        verbose_name_plural = 'Scheduled Workflows'

    def __str__(self):
        return f"Schedule: {self.custom_workflow.name} ({self.cron_expression})"


# =============================================================================
# SESSION 214: AGENT COLLABORATION MODELS
# =============================================================================

class CollaborationSession(models.Model):
    """
    Track agent collaboration sessions.

    Session 214: Enhanced collaboration tracking with detailed workflow support.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Requester
    requester_agent = models.CharField(max_length=200)

    # Collaboration details
    collaboration_type = models.CharField(max_length=50)  # delegation, consultation, parallel, etc.
    task_description = models.TextField()
    input_data = models.JSONField(default=dict)

    # Participating agents
    participating_agents = models.JSONField(default=list)

    # Status and results
    status = models.CharField(max_length=50, default='pending')
    output_data = models.JSONField(default=dict, blank=True)
    quality_score = models.FloatField(default=0.0)

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    execution_time_ms = models.FloatField(default=0.0)

    # Context
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='collaboration_sessions',
        null=True, blank=True
    )
    workflow_execution_id = models.UUIDField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ['-started_at']
        verbose_name = 'Collaboration Session'
        verbose_name_plural = 'Collaboration Sessions'

    def __str__(self):
        return f"{self.requester_agent} collaboration ({self.collaboration_type})"


class InterAgentMessage(models.Model):
    """
    Store inter-agent messages for communication tracking.

    Session 214: Enables asynchronous agent-to-agent communication.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Message routing
    sender_agent = models.CharField(max_length=200)
    receiver_agent = models.CharField(max_length=200)
    message_type = models.CharField(max_length=50)  # request, response, notification, etc.

    # Content
    content = models.JSONField(default=dict)
    context = models.JSONField(default=dict)

    # Metadata
    priority = models.IntegerField(default=5)  # 1-10, 10 is highest
    correlation_id = models.UUIDField(null=True, blank=True)  # Links related messages
    response_to = models.UUIDField(null=True, blank=True)  # ID of message this responds to

    # Status
    is_read = models.BooleanField(default=False)
    is_processed = models.BooleanField(default=False)

    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        verbose_name = 'Inter-Agent Message'
        verbose_name_plural = 'Inter-Agent Messages'

    def __str__(self):
        return f"{self.sender_agent} -> {self.receiver_agent} ({self.message_type})"


class SharedKnowledge(models.Model):
    """
    Shared knowledge base for agent learning and knowledge transfer.

    Session 214: Enables agents to share and learn from each other's insights.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Knowledge source
    source_agent = models.CharField(max_length=200)

    # Knowledge content
    knowledge_type = models.CharField(max_length=50)  # technique, pattern, insight, skill
    title = models.CharField(max_length=500)
    description = models.TextField()
    knowledge_content = models.JSONField(default=dict)

    # Metadata
    domain = models.CharField(max_length=100)  # image, video, audio, research, etc.
    tags = models.JSONField(default=list)

    # Usage tracking
    applied_count = models.IntegerField(default=0)
    effectiveness_score = models.FloatField(default=0.0)

    # Agents that have learned this
    learned_by_agents = models.JSONField(default=list)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        ordering = ['-effectiveness_score', '-applied_count']
        verbose_name = 'Shared Knowledge'
        verbose_name_plural = 'Shared Knowledge'

    def __str__(self):
        return f"{self.title} by {self.source_agent} ({self.knowledge_type})"


class AgentPerformanceMetric(models.Model):
    """
    Track agent performance metrics over time.

    Session 214: Comprehensive performance tracking for agent optimization.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent_name = models.CharField(max_length=200, unique=True)

    # Execution metrics
    total_executions = models.IntegerField(default=0)
    successful_executions = models.IntegerField(default=0)
    failed_executions = models.IntegerField(default=0)

    # Collaboration metrics
    total_collaborations = models.IntegerField(default=0)
    successful_collaborations = models.IntegerField(default=0)
    delegations_made = models.IntegerField(default=0)
    delegations_received = models.IntegerField(default=0)
    consultations_given = models.IntegerField(default=0)
    consultations_received = models.IntegerField(default=0)

    # Performance metrics
    avg_response_time_ms = models.FloatField(default=0.0)
    quality_score = models.FloatField(default=0.0)

    # Knowledge metrics
    knowledge_contributions = models.IntegerField(default=0)
    knowledge_consumed = models.IntegerField(default=0)

    # Specialization scores (domain -> score)
    specialization_scores = models.JSONField(default=dict)

    # Activity tracking
    last_execution = models.DateTimeField(null=True, blank=True)
    last_collaboration = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        ordering = ['-quality_score', '-total_executions']
        verbose_name = 'Agent Performance Metric'
        verbose_name_plural = 'Agent Performance Metrics'

    def __str__(self):
        success_rate = self.successful_executions / self.total_executions if self.total_executions > 0 else 0
        return f"{self.agent_name} ({success_rate:.1%} success)"

    def calculate_quality_score(self):
        """
        Calculate dynamic quality score based on actual performance metrics.

        Session 383: Replaced hardcoded 85.0 placeholder with real calculation.

        Formula (weighted composite):
        - Execution Success Rate: 50% weight (most important)
        - Collaboration Success Rate: 25% weight
        - Knowledge Contribution: 15% weight (normalized 0-100, capped at 10 contributions)
        - Activity Recency: 10% weight (bonus for recent activity)

        Returns: Float 0-100
        """
        score = 0.0

        # 1. Execution Success Rate (50% weight)
        if self.total_executions > 0:
            # Fix data inconsistency: cap successful at total
            successful = min(self.successful_executions, self.total_executions)
            exec_rate = (successful / self.total_executions) * 100
            score += exec_rate * 0.50
        else:
            # New agent with no executions gets neutral score
            score += 50 * 0.50

        # 2. Collaboration Success Rate (25% weight)
        if self.total_collaborations > 0:
            successful_collabs = min(self.successful_collaborations, self.total_collaborations)
            collab_rate = (successful_collabs / self.total_collaborations) * 100
            score += collab_rate * 0.25
        else:
            # No collaborations yet, give neutral score
            score += 50 * 0.25

        # 3. Knowledge Contribution (15% weight)
        # Normalize to 0-100: 10+ contributions = 100%
        knowledge_score = min(self.knowledge_contributions * 10, 100)
        score += knowledge_score * 0.15

        # 4. Activity Recency (10% weight)
        from django.utils import timezone

        now = timezone.now()
        if self.last_execution:
            days_since = (now - self.last_execution).days
            if days_since <= 1:
                recency_score = 100
            elif days_since <= 7:
                recency_score = 80
            elif days_since <= 30:
                recency_score = 60
            else:
                recency_score = 40
        else:
            recency_score = 50  # No activity recorded
        score += recency_score * 0.10

        return round(score, 2)

    def update_quality_score(self):
        """Calculate and save the quality score."""
        self.quality_score = self.calculate_quality_score()
        self.save(update_fields=['quality_score', 'updated_at'])
        return self.quality_score

    @classmethod
    def recalculate_all_quality_scores(cls):
        """Recalculate quality scores for all agents."""
        updated = []
        for metric in cls.objects.all():
            old_score = metric.quality_score
            new_score = metric.update_quality_score()
            updated.append({
                'agent': metric.agent_name,
                'old_score': old_score,
                'new_score': new_score
            })
        return updated


# =============================================================================
# SESSION 219 PHASE D: WORKFLOW MARKETPLACE MODELS
# =============================================================================

class PublishedWorkflow(models.Model):
    """
    Published workflow in the marketplace.

    Session 219 Phase D: Wraps CustomWorkflow for community sharing.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # The actual workflow
    workflow = models.OneToOneField(
        CustomWorkflow, on_delete=models.CASCADE,
        related_name='publication'
    )

    # Author info
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='published_workflows'
    )

    # Marketplace metadata
    title = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)

    # Categorization
    CATEGORY_CHOICES = [
        ('image_generation', 'Image Generation'),
        ('video_creation', 'Video Creation'),
        ('audio_production', 'Audio Production'),
        ('brand_identity', 'Brand Identity'),
        ('social_media', 'Social Media'),
        ('ecommerce', 'E-Commerce'),
        ('research', 'Research & Analysis'),
        ('productivity', 'Productivity'),
        ('other', 'Other'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    tags = models.JSONField(default=list)

    # Media
    preview_image = models.URLField(blank=True)
    preview_images = models.JSONField(default=list)  # List of preview URLs

    # Stats
    download_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)

    # Rating cache (updated when reviews change)
    average_rating = models.FloatField(default=0.0)
    review_count = models.IntegerField(default=0)

    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('removed', 'Removed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    is_featured = models.BooleanField(default=False)

    # Pricing (future: monetization)
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Timestamps
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Published Workflow'
        verbose_name_plural = 'Published Workflows'
        ordering = ['-is_featured', '-download_count', '-published_at']

    def __str__(self):
        return f"{self.title} by {self.author}"

    def update_rating_cache(self):
        """Update cached rating stats from reviews."""
        from django.db.models import Avg, Count
        stats = self.reviews.aggregate(avg=Avg('rating'), count=Count('id'))
        self.average_rating = stats['avg'] or 0.0
        self.review_count = stats['count'] or 0
        self.save(update_fields=['average_rating', 'review_count'])

    def increment_download(self):
        """Increment download count."""
        self.download_count += 1
        self.save(update_fields=['download_count'])
        # Also update the underlying workflow
        if self.workflow:
            self.workflow.use_count += 1
            self.workflow.save(update_fields=['use_count'])

    def increment_view(self):
        """Increment view count."""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class WorkflowReview(models.Model):
    """
    User review of a published workflow.

    Session 219 Phase D: Ratings and reviews for marketplace.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # References
    published_workflow = models.ForeignKey(
        PublishedWorkflow, on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='workflow_reviews'
    )

    # Rating
    rating = models.IntegerField()  # 1-5
    review_text = models.TextField(blank=True)

    # Helpful votes
    helpful_count = models.IntegerField(default=0)
    not_helpful_count = models.IntegerField(default=0)

    # Status
    is_verified_purchase = models.BooleanField(default=False)  # User actually used it

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Workflow Review'
        verbose_name_plural = 'Workflow Reviews'
        ordering = ['-helpful_count', '-created_at']
        unique_together = [('published_workflow', 'user')]

    def __str__(self):
        return f"{self.rating}⭐ by {self.user} on {self.published_workflow.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update parent's rating cache
        self.published_workflow.update_rating_cache()


class WorkflowInstallation(models.Model):
    """
    Track user installations of published workflows.

    Session 219 Phase D: Know who installed what for analytics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # References
    published_workflow = models.ForeignKey(
        PublishedWorkflow, on_delete=models.CASCADE,
        related_name='installations'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='installed_workflows'
    )

    # The cloned workflow
    installed_workflow = models.ForeignKey(
        CustomWorkflow, on_delete=models.SET_NULL,
        null=True, related_name='installation_source'
    )

    # Usage stats
    times_executed = models.IntegerField(default=0)
    last_executed = models.DateTimeField(null=True, blank=True)

    # Timestamps
    installed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Workflow Installation'
        verbose_name_plural = 'Workflow Installations'
        unique_together = [('published_workflow', 'user')]

    def __str__(self):
        return f"{self.user} installed {self.published_workflow.title}"


# =============================================================================
# SESSION 220: REAL-TIME COLLABORATION MODELS
# =============================================================================

class SharedProject(models.Model):
    """
    Collaborative project workspace for multi-user real-time editing.

    Session 220 Phase E: Enable multiple users to work on the same
    creative project simultaneously with real-time sync.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Project details
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    thumbnail = models.URLField(blank=True)

    # Ownership
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='owned_projects'
    )

    # Project content (JSON structure of all content items)
    content = models.JSONField(default=dict)

    # Project settings/configuration
    project_settings = models.JSONField(default=dict)

    # Visibility
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('team', 'Team Only'),
        ('public', 'Public'),
    ]
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')

    # Project status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Version tracking
    version = models.IntegerField(default=1)
    last_edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='last_edited_projects'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Shared Project'
        verbose_name_plural = 'Shared Projects'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} by {self.owner}"

    def increment_version(self):
        """Bump version number after content change"""
        self.version += 1
        self.save(update_fields=['version', 'updated_at'])


class ProjectCollaborator(models.Model):
    """
    Collaborator access to a shared project.

    Session 220 Phase E: Manage who can access and edit projects.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    project = models.ForeignKey(
        SharedProject, on_delete=models.CASCADE,
        related_name='collaborators'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='project_collaborations'
    )

    # Permissions
    ROLE_CHOICES = [
        ('viewer', 'Viewer'),
        ('editor', 'Editor'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='editor')

    # Invitation status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Invited by
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='sent_invitations'
    )

    # Timestamps
    invited_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Project Collaborator'
        verbose_name_plural = 'Project Collaborators'
        unique_together = [('project', 'user')]

    def __str__(self):
        return f"{self.user} ({self.role}) on {self.project.name}"

    def can_edit(self):
        return self.role in ['editor', 'admin'] and self.status == 'accepted'

    def can_manage(self):
        return self.role == 'admin' and self.status == 'accepted'


class ProjectActivity(models.Model):
    """
    Activity log for shared projects.

    Session 220 Phase E: Track all changes for audit and undo.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    project = models.ForeignKey(
        SharedProject, on_delete=models.CASCADE,
        related_name='activities'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='project_activities'
    )

    # Activity type
    ACTION_CHOICES = [
        ('created', 'Created Project'),
        ('edited', 'Edited Content'),
        ('added_content', 'Added Content'),
        ('removed_content', 'Removed Content'),
        ('invited', 'Invited Collaborator'),
        ('joined', 'Joined Project'),
        ('left', 'Left Project'),
        ('settings_changed', 'Changed Settings'),
        ('commented', 'Added Comment'),
    ]
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)

    # Activity details
    details = models.JSONField(default=dict)

    # For undo capability
    previous_state = models.JSONField(null=True, blank=True)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Project Activity'
        verbose_name_plural = 'Project Activities'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} {self.action} on {self.project.name}"


class ProjectPresence(models.Model):
    """
    Track who is currently viewing/editing a project.

    Session 220 Phase E: Real-time presence for collaboration UI.
    This model is frequently updated via WebSocket.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    project = models.ForeignKey(
        SharedProject, on_delete=models.CASCADE,
        related_name='presences'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='project_presences'
    )

    # Connection info
    channel_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    # Cursor/selection state (for showing what others are working on)
    cursor_position = models.JSONField(default=dict)  # {x, y} or element_id
    selection = models.JSONField(default=dict)  # Current selection state

    # Activity status
    STATUS_CHOICES = [
        ('viewing', 'Viewing'),
        ('editing', 'Editing'),
        ('idle', 'Idle'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='viewing')

    # User color (for UI differentiation)
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color

    # Timestamps
    connected_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Project Presence'
        verbose_name_plural = 'Project Presences'
        unique_together = [('project', 'user', 'channel_name')]

    def __str__(self):
        return f"{self.user} ({self.status}) in {self.project.name}"

    @classmethod
    def cleanup_stale(cls, minutes=5):
        """Remove presence records older than X minutes"""
        from django.utils import timezone
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(minutes=minutes)
        return cls.objects.filter(last_activity__lt=cutoff).delete()


class ProjectComment(models.Model):
    """
    Comments on project content for collaboration.

    Session 220 Phase E: Allow discussion within projects.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    project = models.ForeignKey(
        SharedProject, on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='project_comments'
    )

    # Comment content
    text = models.TextField()

    # Position reference (where in the project this comment is attached)
    target_type = models.CharField(max_length=50, blank=True)  # 'content_item', 'canvas', etc.
    target_id = models.CharField(max_length=100, blank=True)  # ID of the target element

    # Threading
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True, related_name='replies'
    )

    # Status
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='resolved_comments'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Project Comment'
        verbose_name_plural = 'Project Comments'
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user} on {self.project.name}"


# =============================================================================
# Session 221 Phase F: Advanced Analytics Models
# =============================================================================

class UsageMetric(models.Model):
    """
    Track usage metrics for all platform features.

    Session 221 Phase F: Analytics foundation for understanding platform usage.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='usage_metrics', null=True, blank=True
    )

    # Metric identification
    METRIC_CATEGORIES = [
        ('image', 'Image Generation'),
        ('video', 'Video Generation'),
        ('audio', 'Audio Generation'),
        ('3d', '3D Generation'),
        ('workflow', 'Workflow Execution'),
        ('agent', 'Agent Execution'),
        ('spider', 'Spider Data'),
        ('collaboration', 'Collaboration'),
        ('api', 'API Call'),
    ]
    category = models.CharField(max_length=20, choices=METRIC_CATEGORIES)
    metric_type = models.CharField(max_length=50)  # e.g., 'generate', 'edit', 'export'
    feature_name = models.CharField(max_length=100)  # e.g., 'ultra_generation', 'runway_video'

    # Metric values
    count = models.IntegerField(default=1)
    value = models.DecimalField(max_digits=15, decimal_places=4, default=0)  # For storing amounts

    # Context
    metadata = models.JSONField(default=dict)  # Additional context

    # API provider tracking
    provider = models.CharField(max_length=50, blank=True)  # 'stability', 'runway', 'elevenlabs'
    endpoint = models.CharField(max_length=200, blank=True)

    # Time tracking
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    duration_ms = models.IntegerField(null=True, blank=True)  # Processing time

    # Aggregation helpers
    hour = models.IntegerField(default=0)  # 0-23
    day_of_week = models.IntegerField(default=0)  # 0-6 (Monday=0)

    class Meta:
        app_label = 'core'
        verbose_name = 'Usage Metric'
        verbose_name_plural = 'Usage Metrics'
        indexes = [
            models.Index(fields=['category', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['feature_name', 'timestamp']),
        ]

    def save(self, *args, **kwargs):
        # Auto-populate time fields
        if self.timestamp:
            self.hour = self.timestamp.hour
            self.day_of_week = self.timestamp.weekday()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category}:{self.metric_type} at {self.timestamp}"


class PerformanceLog(models.Model):
    """
    Track performance metrics for system operations.

    Session 221 Phase F: Monitor system health and performance.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Component identification
    COMPONENT_TYPES = [
        ('api', 'API Endpoint'),
        ('websocket', 'WebSocket'),
        ('database', 'Database'),
        ('cache', 'Cache'),
        ('external', 'External API'),
        ('worker', 'Background Worker'),
        ('ml', 'ML Model'),
    ]
    component_type = models.CharField(max_length=20, choices=COMPONENT_TYPES)
    component_name = models.CharField(max_length=100)

    # Performance data
    response_time_ms = models.IntegerField()  # Milliseconds
    status_code = models.IntegerField(null=True, blank=True)
    success = models.BooleanField(default=True)

    # Error tracking
    error_message = models.TextField(blank=True)
    error_type = models.CharField(max_length=100, blank=True)

    # Resource usage
    memory_mb = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cpu_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Context
    endpoint = models.CharField(max_length=200, blank=True)
    method = models.CharField(max_length=10, blank=True)  # GET, POST, etc.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='performance_logs'
    )

    # Timestamp
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Performance Log'
        verbose_name_plural = 'Performance Logs'
        indexes = [
            models.Index(fields=['component_type', 'timestamp']),
            models.Index(fields=['success', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.component_type}:{self.component_name} - {self.response_time_ms}ms"


class CostTracking(models.Model):
    """
    Track API costs and token usage across all providers.

    Session 221 Phase F: Enable cost monitoring and budget management.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='cost_records', null=True, blank=True
    )

    # Session 1039: Multi-tenant cost attribution
    tenant = models.ForeignKey(
        'core.Tenant', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='cost_records_by_tenant',
    )

    # Provider and service
    PROVIDERS = [
        ('stability', 'Stability AI'),
        ('runway', 'Runway ML'),
        ('elevenlabs', 'ElevenLabs'),
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('replicate', 'Replicate'),
        ('other', 'Other'),
    ]
    provider = models.CharField(max_length=20, choices=PROVIDERS)
    service = models.CharField(max_length=100)  # e.g., 'ultra_generation', 'gen3_turbo'
    operation = models.CharField(max_length=100)  # e.g., 'generate', 'upscale', 'tts'

    # Cost data
    credits_used = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    estimated_cost_usd = models.DecimalField(max_digits=15, decimal_places=6, default=0)

    # Token tracking (for LLM APIs)
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)

    # Resource tracking (for generation APIs)
    resolution = models.CharField(max_length=20, blank=True)  # e.g., '1024x1024'
    duration_seconds = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Billing period
    billing_period = models.CharField(max_length=7, blank=True)  # YYYY-MM format

    # Context
    request_id = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict)

    # Timestamp
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Cost Tracking'
        verbose_name_plural = 'Cost Tracking Records'
        indexes = [
            models.Index(fields=['provider', 'timestamp']),
            models.Index(fields=['user', 'billing_period']),
            models.Index(fields=['service', 'timestamp']),
        ]

    def save(self, *args, **kwargs):
        # Auto-populate billing period
        if self.timestamp and not self.billing_period:
            self.billing_period = self.timestamp.strftime('%Y-%m')
        # Calculate total tokens
        if self.input_tokens or self.output_tokens:
            self.total_tokens = self.input_tokens + self.output_tokens
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.provider}:{self.service} - ${self.estimated_cost_usd}"


class AnalyticsDashboard(models.Model):
    """
    User-customizable analytics dashboard configuration.

    Session 221 Phase F: Allow users to create custom dashboards.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='analytics_dashboards'
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)

    # Dashboard layout
    layout = models.JSONField(default=dict)  # Grid positions and sizes

    # Widgets configuration
    widgets = models.JSONField(default=list)  # List of widget configs

    # Time range defaults
    DEFAULT_RANGES = [
        ('1h', 'Last Hour'),
        ('24h', 'Last 24 Hours'),
        ('7d', 'Last 7 Days'),
        ('30d', 'Last 30 Days'),
        ('90d', 'Last 90 Days'),
        ('custom', 'Custom Range'),
    ]
    default_time_range = models.CharField(max_length=10, choices=DEFAULT_RANGES, default='24h')

    # Refresh settings
    auto_refresh = models.BooleanField(default=True)
    refresh_interval_seconds = models.IntegerField(default=60)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Analytics Dashboard'
        verbose_name_plural = 'Analytics Dashboards'
        unique_together = [('user', 'name')]

    def __str__(self):
        return f"{self.user}'s Dashboard: {self.name}"


class AnalyticsAlert(models.Model):
    """
    Configurable alerts based on analytics thresholds.

    Session 221 Phase F: Notify users of important metric changes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='analytics_alerts'
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    # Alert conditions
    METRIC_TYPES = [
        ('cost_daily', 'Daily Cost'),
        ('cost_monthly', 'Monthly Cost'),
        ('api_errors', 'API Errors'),
        ('response_time', 'Response Time'),
        ('usage_count', 'Usage Count'),
        ('credits_remaining', 'Credits Remaining'),
    ]
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES)

    OPERATORS = [
        ('gt', 'Greater Than'),
        ('lt', 'Less Than'),
        ('eq', 'Equal To'),
        ('gte', 'Greater Than or Equal'),
        ('lte', 'Less Than or Equal'),
    ]
    operator = models.CharField(max_length=5, choices=OPERATORS)
    threshold_value = models.DecimalField(max_digits=15, decimal_places=4)

    # Notification settings
    notify_email = models.BooleanField(default=False)
    notify_websocket = models.BooleanField(default=True)
    cooldown_minutes = models.IntegerField(default=60)  # Minimum time between alerts

    # Tracking
    last_triggered = models.DateTimeField(null=True, blank=True)
    trigger_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Analytics Alert'
        verbose_name_plural = 'Analytics Alerts'

    def can_trigger(self):
        """Check if alert can be triggered based on cooldown"""
        if not self.last_triggered:
            return True
        elapsed = (timezone.now() - self.last_triggered).total_seconds() / 60
        return elapsed >= self.cooldown_minutes

    def __str__(self):
        return f"Alert: {self.name} ({self.metric_type} {self.operator} {self.threshold_value})"


# =============================================================================
# SESSION 227: PHASE 3 - TEAM POWER (Multi-Agent Collaboration)
# =============================================================================

class AgentRole(models.Model):
    """
    Session 227: Define specialized roles for agents in collaborative workflows.
    Each role has specific capabilities and tool access.
    """
    ROLE_TYPES = [
        ('designer', 'Designer - Creates visual content'),
        ('researcher', 'Researcher - Gathers information'),
        ('reviewer', 'Reviewer - Reviews and critiques work'),
        ('writer', 'Writer - Creates written content'),
        ('analyst', 'Analyst - Analyzes data and trends'),
        ('strategist', 'Strategist - Plans and coordinates'),
        ('optimizer', 'Optimizer - Improves and refines'),
        ('communicator', 'Communicator - Handles messaging'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    role_type = models.CharField(max_length=50, choices=ROLE_TYPES)
    description = models.TextField(blank=True)

    # Capabilities - what this role can do
    capabilities = models.JSONField(default=list, help_text='List of capability strings')
    # e.g., ['image_generation', 'style_transfer', 'logo_design']

    # Tools - which tools this role has access to
    available_tools = models.JSONField(default=list, help_text='List of tool names this role can use')
    # e.g., ['stability_ai', 'runway_ml', 'elevenlabs']

    # Constraints - limits on what this role can do
    constraints = models.JSONField(default=dict, help_text='Role-specific constraints')
    # e.g., {'max_images_per_task': 10, 'requires_approval': False}

    # System prompt additions for this role
    role_prompt = models.TextField(blank=True, help_text='Additional system prompt for this role')

    # Priority (higher = more important in team decisions)
    priority = models.IntegerField(default=5)  # 1-10

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Agent Role'
        verbose_name_plural = 'Agent Roles'
        ordering = ['-priority', 'name']

    def __str__(self):
        return f"{self.name} ({self.role_type})"


class AgentTeam(models.Model):
    """
    Session 227: A team of agents working together on tasks.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Team composition
    agents = models.ManyToManyField('Agent', through='AgentTeamMembership', related_name='teams')

    # Team lead (optional - coordinates the team)
    lead_agent = models.ForeignKey('Agent', on_delete=models.SET_NULL, null=True, blank=True, related_name='led_teams')

    # Team type
    TEAM_TYPES = [
        ('creative', 'Creative Team'),
        ('research', 'Research Team'),
        ('marketing', 'Marketing Team'),
        ('content', 'Content Production Team'),
        ('custom', 'Custom Team'),
    ]
    team_type = models.CharField(max_length=50, choices=TEAM_TYPES, default='custom')

    # Team settings
    settings = models.JSONField(default=dict)
    # e.g., {'auto_assign': True, 'max_concurrent_tasks': 5}

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Agent Team'
        verbose_name_plural = 'Agent Teams'

    def __str__(self):
        return f"{self.name} ({self.team_type})"


class AgentTeamMembership(models.Model):
    """
    Session 227: Membership of an agent in a team with specific role.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(AgentTeam, on_delete=models.CASCADE, related_name='memberships')
    agent = models.ForeignKey('Agent', on_delete=models.CASCADE, related_name='team_memberships')
    role = models.ForeignKey(AgentRole, on_delete=models.SET_NULL, null=True, blank=True)

    # Membership settings
    is_lead = models.BooleanField(default=False)
    can_delegate = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        unique_together = ['team', 'agent']
        verbose_name = 'Agent Team Membership'
        verbose_name_plural = 'Agent Team Memberships'

    def __str__(self):
        return f"{self.agent.name} in {self.team.name}"


class AgentMessage(models.Model):
    """
    Session 227: Inter-agent communication messages.
    Allows agents to communicate and coordinate with each other.
    """
    MESSAGE_TYPES = [
        ('request', 'Task Request'),
        ('response', 'Task Response'),
        ('feedback', 'Feedback'),
        ('handoff', 'Task Handoff'),
        ('notification', 'Notification'),
        ('question', 'Question'),
        ('answer', 'Answer'),
        ('status', 'Status Update'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Sender and receiver
    sender_agent = models.ForeignKey('Agent', on_delete=models.CASCADE, related_name='sent_messages')
    receiver_agent = models.ForeignKey('Agent', on_delete=models.CASCADE, related_name='received_messages')

    # Message content
    message_type = models.CharField(max_length=50, choices=MESSAGE_TYPES)
    subject = models.CharField(max_length=255)
    content = models.TextField()

    # Attachments (references to content)
    attachments = models.JSONField(default=list)
    # e.g., [{'type': 'image', 'id': 'uuid'}, {'type': 'document', 'url': '...'}]

    # Threading
    parent_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    thread_id = models.UUIDField(default=uuid.uuid4)  # Groups related messages

    # Context
    task_context = models.JSONField(default=dict)
    # e.g., {'workflow_id': 'uuid', 'opportunity_id': 'uuid'}

    # Status
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')

    # Priority
    priority = models.IntegerField(default=5)  # 1-10, higher = more urgent

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Agent Message'
        verbose_name_plural = 'Agent Messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['thread_id']),
            models.Index(fields=['sender_agent', 'created_at']),
            models.Index(fields=['receiver_agent', 'status']),
        ]

    def __str__(self):
        return f"{self.sender_agent.name} -> {self.receiver_agent.name}: {self.subject[:50]}"


class TeamWorkflow(models.Model):
    """
    Session 227: Collaborative workflows involving multiple agents.
    """
    WORKFLOW_STATUSES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Team executing this workflow
    team = models.ForeignKey(AgentTeam, on_delete=models.CASCADE, related_name='workflows')

    # Related opportunity (optional)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.SET_NULL, null=True, blank=True, related_name='team_workflows')

    # Workflow definition
    workflow_template = models.CharField(max_length=100, blank=True)  # e.g., 'research_and_create_logos'
    steps = models.JSONField(default=list)
    # e.g., [
    #   {'step': 1, 'agent_role': 'researcher', 'action': 'research_trends', 'status': 'completed'},
    #   {'step': 2, 'agent_role': 'designer', 'action': 'create_concepts', 'status': 'in_progress'},
    #   {'step': 3, 'agent_role': 'reviewer', 'action': 'review_designs', 'status': 'pending'},
    # ]

    # Current state
    status = models.CharField(max_length=20, choices=WORKFLOW_STATUSES, default='draft')
    current_step = models.IntegerField(default=0)
    current_agent = models.ForeignKey('Agent', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_workflows')

    # Progress tracking
    progress = models.IntegerField(default=0)  # 0-100%
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Results
    results = models.JSONField(default=dict)
    # e.g., {'images_created': 5, 'research_findings': {...}, 'review_score': 8.5}

    # Errors and issues
    errors = models.JSONField(default=list)

    # Metadata
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Team Workflow'
        verbose_name_plural = 'Team Workflows'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.status}) - {self.team.name}"

    def advance_step(self):
        """Move to the next step in the workflow"""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.progress = int((self.current_step / len(self.steps)) * 100)
            self.save()
            return True
        return False


class TeamWorkflowStep(models.Model):
    """
    Session 227: Individual step execution in a team workflow.
    """
    STEP_STATUSES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(TeamWorkflow, on_delete=models.CASCADE, related_name='step_executions')

    # Step definition
    step_number = models.IntegerField()
    step_name = models.CharField(max_length=100)
    action = models.CharField(max_length=100)

    # Assignment
    assigned_agent = models.ForeignKey('Agent', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_steps')
    required_role = models.ForeignKey(AgentRole, on_delete=models.SET_NULL, null=True, blank=True)

    # Execution
    status = models.CharField(max_length=20, choices=STEP_STATUSES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Input/Output
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict)

    # Feedback from reviewers
    review_score = models.FloatField(null=True, blank=True)  # 0-10
    review_feedback = models.TextField(blank=True)
    reviewer_agent = models.ForeignKey('Agent', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_steps')

    # Dependencies
    depends_on = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='required_by')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Team Workflow Step'
        verbose_name_plural = 'Team Workflow Steps'
        ordering = ['workflow', 'step_number']

    def __str__(self):
        return f"Step {self.step_number}: {self.step_name} ({self.status})"


# =============================================================================
# SESSION 229: PHASE 4 - SMART DISTRIBUTION
# =============================================================================

class DistributionPlatform(models.Model):
    """
    Platforms where content can be distributed/sold.
    """
    PLATFORM_TYPES = [
        ('marketplace', 'Marketplace'),        # Etsy, Creative Market, etc.
        ('social', 'Social Media'),            # Instagram, TikTok, etc.
        ('stock', 'Stock Content'),            # Shutterstock, Adobe Stock, etc.
        ('print_on_demand', 'Print on Demand'),  # Redbubble, Printful, etc.
        ('nft', 'NFT Marketplace'),            # OpenSea, Foundation, etc.
        ('direct', 'Direct Sales'),            # Your own website
        ('freelance', 'Freelance Platform'),   # Fiverr, Upwork, etc.
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    platform_type = models.CharField(max_length=50, choices=PLATFORM_TYPES)
    description = models.TextField(blank=True)
    website_url = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)

    # Platform capabilities
    supported_content_types = models.JSONField(default=list)  # ['image', 'video', 'audio', '3d']
    supported_formats = models.JSONField(default=list)  # ['png', 'jpg', 'mp4', 'svg']
    max_file_size_mb = models.IntegerField(default=100)

    # Revenue model
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    has_subscription = models.BooleanField(default=False)
    subscription_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Integration
    api_available = models.BooleanField(default=False)
    api_documentation_url = models.URLField(blank=True)
    requires_approval = models.BooleanField(default=False)

    # Metadata
    popularity_score = models.IntegerField(default=50)  # 0-100
    avg_earnings_per_item = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    competition_level = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ], default='medium')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Distribution Platform'
        verbose_name_plural = 'Distribution Platforms'
        ordering = ['-popularity_score', 'name']

    def __str__(self):
        return f"{self.name} ({self.platform_type})"


class UserPlatformAccount(models.Model):
    """
    DEPRECATED - Session 528: This model has 0 records and is not used.

    Original purpose: User's account on a distribution platform.
    """
    ACCOUNT_STATUS = [
        ('pending', 'Pending Verification'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('inactive', 'Inactive'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='platform_accounts')
    platform = models.ForeignKey(DistributionPlatform, on_delete=models.CASCADE, related_name='user_accounts')

    # Account details
    account_username = models.CharField(max_length=200, blank=True)
    account_url = models.URLField(blank=True)
    account_status = models.CharField(max_length=20, choices=ACCOUNT_STATUS, default='pending')

    # Credentials (encrypted in production)
    api_key = models.CharField(max_length=500, blank=True)
    api_secret = models.CharField(max_length=500, blank=True)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)

    # Performance metrics
    total_items_listed = models.IntegerField(default=0)
    total_sales = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    avg_item_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    follower_count = models.IntegerField(default=0)

    # Settings
    auto_upload_enabled = models.BooleanField(default=False)
    notification_settings = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'User Platform Account'
        verbose_name_plural = 'User Platform Accounts'
        unique_together = ['user', 'platform']

    def __str__(self):
        return f"{self.user.username} on {self.platform.name}"


class ContentDistribution(models.Model):
    """
    Record of content distributed to a platform.
    """
    DISTRIBUTION_STATUS = [
        ('draft', 'Draft'),
        ('pending', 'Pending Upload'),
        ('uploading', 'Uploading'),
        ('processing', 'Processing'),
        ('live', 'Live'),
        ('rejected', 'Rejected'),
        ('removed', 'Removed'),
        ('sold_out', 'Sold Out'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='distributions')
    platform_account = models.ForeignKey(UserPlatformAccount, on_delete=models.CASCADE, related_name='distributions')

    # Content reference
    content_type = models.CharField(max_length=50)  # image, video, audio, 3d
    image_history = models.ForeignKey('content.ImageHistory', on_delete=models.SET_NULL, null=True, blank=True, related_name='distributions')
    video_history = models.ForeignKey('content.VideoHistory', on_delete=models.SET_NULL, null=True, blank=True, related_name='distributions')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.SET_NULL, null=True, blank=True, related_name='distributions')

    # Listing details
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list)
    categories = models.JSONField(default=list)

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default='USD')
    license_type = models.CharField(max_length=50, blank=True)  # commercial, editorial, etc.

    # Platform-specific data
    platform_listing_id = models.CharField(max_length=200, blank=True)
    platform_listing_url = models.URLField(blank=True)
    platform_metadata = models.JSONField(default=dict)

    # Status
    status = models.CharField(max_length=20, choices=DISTRIBUTION_STATUS, default='draft')
    rejection_reason = models.TextField(blank=True)

    # Performance
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    downloads = models.IntegerField(default=0)
    sales = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Timestamps
    listed_at = models.DateTimeField(null=True, blank=True)
    last_sale_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Content Distribution'
        verbose_name_plural = 'Content Distributions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} on {self.platform_account.platform.name}"


class DistributionRecommendation(models.Model):
    """
    AI-generated recommendations for where to distribute content.
    """
    RECOMMENDATION_TYPES = [
        ('platform', 'Platform Recommendation'),
        ('pricing', 'Pricing Recommendation'),
        ('timing', 'Timing Recommendation'),
        ('tags', 'Tags/Keywords Recommendation'),
        ('optimization', 'Optimization Recommendation'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='distribution_recommendations')

    # Content reference
    content_type = models.CharField(max_length=50)
    image_history = models.ForeignKey('content.ImageHistory', on_delete=models.SET_NULL, null=True, blank=True, related_name='recommendations')
    video_history = models.ForeignKey('content.VideoHistory', on_delete=models.SET_NULL, null=True, blank=True, related_name='recommendations')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.SET_NULL, null=True, blank=True, related_name='distribution_recommendations')

    # Recommendation details
    recommendation_type = models.CharField(max_length=50, choices=RECOMMENDATION_TYPES)
    platform = models.ForeignKey(DistributionPlatform, on_delete=models.SET_NULL, null=True, blank=True)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # 0-100

    # Recommendation content
    title = models.CharField(max_length=200)
    reasoning = models.TextField()
    suggested_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    suggested_tags = models.JSONField(default=list)
    suggested_title = models.CharField(max_length=500, blank=True)
    suggested_description = models.TextField(blank=True)

    # Estimated outcomes
    estimated_views = models.IntegerField(null=True, blank=True)
    estimated_sales = models.IntegerField(null=True, blank=True)
    estimated_revenue = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # User action
    is_applied = models.BooleanField(default=False)
    applied_at = models.DateTimeField(null=True, blank=True)
    is_dismissed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Distribution Recommendation'
        verbose_name_plural = 'Distribution Recommendations'
        ordering = ['-confidence_score', '-created_at']

    def __str__(self):
        return f"{self.recommendation_type}: {self.title}"


class DistributionAnalytics(models.Model):
    """
    Aggregated analytics for distribution performance.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='distribution_analytics')
    platform = models.ForeignKey(DistributionPlatform, on_delete=models.CASCADE, null=True, blank=True)

    # Time period
    date = models.DateField()
    period_type = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], default='daily')

    # Metrics
    total_views = models.IntegerField(default=0)
    total_downloads = models.IntegerField(default=0)
    total_sales = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    new_listings = models.IntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # sales/views

    # Top performers
    top_content_ids = models.JSONField(default=list)  # List of content IDs
    top_tags = models.JSONField(default=list)
    best_performing_category = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Distribution Analytics'
        verbose_name_plural = 'Distribution Analytics'
        unique_together = ['user', 'platform', 'date', 'period_type']
        ordering = ['-date']

    def __str__(self):
        platform_name = self.platform.name if self.platform else 'All Platforms'
        return f"{self.user.username} - {platform_name} - {self.date}"


# ============================================================
# Session 232: Phase 5 - Learning Loop Models
# ============================================================

class SuccessPattern(models.Model):
    """
    Tracks patterns that lead to successful sales/revenue.
    The system learns what works and suggests similar approaches.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='success_patterns')

    # Pattern identification
    pattern_type = models.CharField(max_length=50, choices=[
        ('content_style', 'Content Style'),
        ('pricing_strategy', 'Pricing Strategy'),
        ('timing', 'Upload Timing'),
        ('platform_match', 'Platform Match'),
        ('tag_combination', 'Tag Combination'),
        ('description_format', 'Description Format'),
        ('category_niche', 'Category Niche'),
    ])
    pattern_name = models.CharField(max_length=200)
    pattern_description = models.TextField(blank=True)

    # Pattern data
    pattern_attributes = models.JSONField(default=dict)  # Specific attributes that make this pattern
    # Example: {"style": "cyberpunk", "colors": ["neon", "dark"], "aspect_ratio": "16:9"}

    # Success metrics
    success_count = models.IntegerField(default=0)  # Number of times this pattern succeeded
    failure_count = models.IntegerField(default=0)  # Number of times it failed
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # 0-100%
    avg_revenue_per_success = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_revenue_attributed = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Pattern strength
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, default=50)  # 0-100
    sample_size = models.IntegerField(default=0)  # How many data points
    statistical_significance = models.BooleanField(default=False)  # p < 0.05

    # Best platforms for this pattern
    best_platforms = models.JSONField(default=list)  # ["etsy", "gumroad"]

    # Time-based insights
    best_upload_times = models.JSONField(default=list)  # ["tuesday_10am", "friday_2pm"]
    best_seasons = models.JSONField(default=list)  # ["christmas", "summer"]

    # Related content
    example_content_ids = models.JSONField(default=list)  # UUIDs of successful content

    # Status
    is_active = models.BooleanField(default=True)
    is_global = models.BooleanField(default=False)  # If True, applies to all users

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_validated = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Success Pattern'
        verbose_name_plural = 'Success Patterns'
        ordering = ['-success_rate', '-confidence_score']

    def __str__(self):
        return f"{self.pattern_type}: {self.pattern_name} ({self.success_rate}%)"

    def update_metrics(self, was_successful: bool, revenue: float = 0):
        """Update pattern metrics after a new data point."""
        if was_successful:
            self.success_count += 1
            self.total_revenue_attributed += Decimal(str(revenue))
        else:
            self.failure_count += 1

        self.sample_size = self.success_count + self.failure_count
        if self.sample_size > 0:
            self.success_rate = (self.success_count / self.sample_size) * 100
            if self.success_count > 0:
                self.avg_revenue_per_success = self.total_revenue_attributed / self.success_count

        # Update confidence based on sample size
        if self.sample_size >= 30:
            self.statistical_significance = True
            self.confidence_score = min(95, 50 + (self.sample_size * 0.5))
        else:
            self.confidence_score = min(50, self.sample_size * 2)

        self.save()


class ContentPerformancePrediction(models.Model):
    """
    ML-based predictions for content performance before distribution.
    Helps users understand potential success before uploading.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='performance_predictions')

    # Content being predicted
    content_type = models.CharField(max_length=50)  # image, video, audio
    content_id = models.UUIDField(null=True, blank=True)  # Reference to actual content
    content_hash = models.CharField(max_length=64, blank=True)  # For dedup

    # Content attributes analyzed
    analyzed_attributes = models.JSONField(default=dict)
    # {"style": "cyberpunk", "colors": [...], "complexity": 7, "uniqueness": 8}

    # Predictions per platform
    platform_predictions = models.JSONField(default=dict)
    # {
    #   "etsy": {"success_probability": 0.75, "expected_revenue": 45.00, "confidence": 0.8},
    #   "gumroad": {"success_probability": 0.60, "expected_revenue": 15.00, "confidence": 0.7}
    # }

    # Overall predictions
    overall_success_probability = models.DecimalField(max_digits=5, decimal_places=4, default=0)  # 0-1
    expected_total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expected_time_to_first_sale = models.IntegerField(default=0)  # Hours
    prediction_confidence = models.DecimalField(max_digits=5, decimal_places=4, default=0)  # 0-1

    # Recommended actions
    recommended_platforms = models.JSONField(default=list)  # Ordered by potential
    recommended_price_range = models.JSONField(default=dict)  # {"min": 10, "max": 50, "optimal": 29.99}
    recommended_tags = models.JSONField(default=list)
    recommended_upload_time = models.DateTimeField(null=True, blank=True)

    # Matching patterns
    matching_success_patterns = models.JSONField(default=list)  # Pattern IDs that match

    # Actual outcomes (filled after distribution)
    actual_success = models.BooleanField(null=True, blank=True)
    actual_revenue = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prediction_accuracy = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)

    # Model info
    model_version = models.CharField(max_length=50, default='v1.0')
    prediction_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Content Performance Prediction'
        verbose_name_plural = 'Content Performance Predictions'
        ordering = ['-prediction_timestamp']

    def __str__(self):
        return f"Prediction for {self.content_type}: {self.overall_success_probability*100:.1f}% success"


class PricingOptimization(models.Model):
    """
    Dynamic pricing suggestions based on market data and user history.
    Learns optimal pricing strategies over time.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pricing_optimizations')

    # Scope
    platform = models.ForeignKey(DistributionPlatform, on_delete=models.CASCADE, null=True, blank=True)
    content_category = models.CharField(max_length=100, blank=True)  # "ai_art", "digital_download"
    content_style = models.CharField(max_length=100, blank=True)  # "cyberpunk", "minimalist"

    # Current market data
    market_avg_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    market_median_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    market_price_range = models.JSONField(default=dict)  # {"min": 5, "max": 500, "p25": 15, "p75": 75}
    competitor_prices = models.JSONField(default=list)  # Sample of competitor prices

    # User's historical performance
    user_avg_sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    user_best_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Price with best conversion
    user_price_elasticity = models.DecimalField(max_digits=5, decimal_places=4, default=0)  # How price affects sales

    # Optimal pricing
    optimal_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    optimal_price_confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    price_range_suggestion = models.JSONField(default=dict)  # {"low": 15, "mid": 25, "high": 45}

    # Price testing results
    tested_prices = models.JSONField(default=list)  # [{"price": 25, "conversions": 10, "revenue": 250}]
    best_tested_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Seasonal adjustments
    seasonal_multipliers = models.JSONField(default=dict)
    # {"christmas": 1.25, "summer": 0.9, "black_friday": 1.5}

    # Insights
    pricing_insights = models.JSONField(default=list)
    # ["Your prices are 15% below market average", "Consider raising prices on weekends"]

    # A/B test reference
    current_ab_test_id = models.UUIDField(null=True, blank=True)

    last_updated = models.DateTimeField(auto_now=True)
    data_freshness_days = models.IntegerField(default=0)  # Days since last market data update

    class Meta:
        app_label = 'core'
        verbose_name = 'Pricing Optimization'
        verbose_name_plural = 'Pricing Optimizations'
        ordering = ['-last_updated']

    def __str__(self):
        platform_name = self.platform.name if self.platform else 'All'
        return f"Pricing for {platform_name}/{self.content_category}: ${self.optimal_price}"


class DistributionInsight(models.Model):
    """
    AI-generated insights from distribution learning patterns.
    Proactive suggestions based on analyzed data.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='distribution_insights')

    # Insight classification
    insight_type = models.CharField(max_length=50, choices=[
        ('opportunity', 'New Opportunity'),
        ('improvement', 'Improvement Suggestion'),
        ('warning', 'Warning/Alert'),
        ('milestone', 'Achievement/Milestone'),
        ('trend', 'Trend Detected'),
        ('prediction', 'Future Prediction'),
        ('comparison', 'Performance Comparison'),
    ])
    priority = models.CharField(max_length=20, choices=[
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ], default='medium')

    # Content
    title = models.CharField(max_length=200)
    message = models.TextField()
    detailed_analysis = models.TextField(blank=True)

    # Data backing the insight
    supporting_data = models.JSONField(default=dict)
    # {"pattern_id": "...", "metrics": {...}, "comparison": {...}}

    # Actionable recommendations
    recommended_actions = models.JSONField(default=list)
    # [{"action": "Raise price on Etsy", "expected_impact": "+15% revenue"}]

    # Impact estimation
    potential_revenue_impact = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    confidence_level = models.DecimalField(max_digits=5, decimal_places=2, default=50)

    # User interaction
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    is_acted_upon = models.BooleanField(default=False)
    user_feedback = models.CharField(max_length=20, choices=[
        ('helpful', 'Helpful'),
        ('not_helpful', 'Not Helpful'),
        ('incorrect', 'Incorrect'),
    ], null=True, blank=True)

    # Validity
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(null=True, blank=True)  # When insight becomes stale
    is_still_relevant = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Distribution Insight'
        verbose_name_plural = 'Distribution Insights'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.insight_type}] {self.title}"


class UserLearningProfile(models.Model):
    """
    DEPRECATED - Session 528: This model has 0 records and is not used.

    Original purpose: Aggregated learning profile for each user.
    Stores preferences, patterns, and AI assistant state.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learning_profile')

    # Content preferences learned
    preferred_styles = models.JSONField(default=list)  # ["cyberpunk", "minimalist"]
    preferred_platforms = models.JSONField(default=list)  # ["etsy", "gumroad"]
    preferred_content_types = models.JSONField(default=list)  # ["image", "digital_download"]
    preferred_price_ranges = models.JSONField(default=dict)  # {"low": 10, "high": 50}

    # Work patterns
    typical_upload_times = models.JSONField(default=list)  # ["weekday_morning", "weekend_afternoon"]
    productivity_patterns = models.JSONField(default=dict)  # {"best_day": "tuesday", "best_hour": 10}
    avg_content_per_week = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Success profile
    overall_success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    strongest_categories = models.JSONField(default=list)  # Categories with best performance
    weakest_categories = models.JSONField(default=list)  # Categories needing improvement
    total_successful_distributions = models.IntegerField(default=0)
    total_lifetime_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Learning state
    patterns_discovered = models.IntegerField(default=0)
    insights_generated = models.IntegerField(default=0)
    insights_acted_upon = models.IntegerField(default=0)
    prediction_accuracy_avg = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Personalization settings
    notification_preferences = models.JSONField(default=dict)
    # {"daily_insights": True, "price_alerts": True, "trend_updates": False}

    # Goals
    revenue_goals = models.JSONField(default=dict)
    # {"monthly": 1000, "yearly": 12000, "next_milestone": 5000}

    # AI assistant memory
    conversation_context = models.JSONField(default=dict)
    recent_interactions = models.JSONField(default=list)  # Last N interactions for context

    last_activity = models.DateTimeField(auto_now=True)
    profile_completeness = models.IntegerField(default=0)  # 0-100%

    class Meta:
        app_label = 'core'
        verbose_name = 'User Learning Profile'
        verbose_name_plural = 'User Learning Profiles'

    def __str__(self):
        return f"Learning Profile: {self.user.username}"


class PerformanceComparison(models.Model):
    """
    Benchmarks user performance against market/peers.
    Helps understand where they stand and how to improve.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='performance_comparisons')

    # Comparison scope
    comparison_type = models.CharField(max_length=50, choices=[
        ('platform', 'Platform-wide'),
        ('category', 'Category'),
        ('style', 'Style'),
        ('price_tier', 'Price Tier'),
        ('experience_level', 'Experience Level'),
    ])
    scope_value = models.CharField(max_length=100)  # e.g., "etsy", "ai_art", "cyberpunk"

    # User metrics
    user_metrics = models.JSONField(default=dict)
    # {"revenue": 500, "conversion_rate": 3.5, "avg_price": 25, "items_sold": 20}

    # Benchmark metrics
    benchmark_metrics = models.JSONField(default=dict)
    # {"revenue": {"p25": 200, "p50": 450, "p75": 900, "p90": 2000}}

    # Percentile rankings
    percentile_rankings = models.JSONField(default=dict)
    # {"revenue": 55, "conversion_rate": 70, "items_sold": 45}

    # Insights
    strengths = models.JSONField(default=list)  # ["Above average pricing", "Good conversion"]
    weaknesses = models.JSONField(default=list)  # ["Below average volume"]
    improvement_opportunities = models.JSONField(default=list)

    # Trend
    trend_vs_last_period = models.JSONField(default=dict)
    # {"revenue": "+15%", "ranking_change": "+5 percentile"}

    period_start = models.DateField()
    period_end = models.DateField()
    sample_size = models.IntegerField(default=0)  # Number of users in comparison

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Performance Comparison'
        verbose_name_plural = 'Performance Comparisons'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} vs {self.comparison_type}:{self.scope_value}"


# ============================================================
# Session 234: Phase 6 - Proactive System Models
# ============================================================

class ProactiveAlert(models.Model):
    """
    Proactive alerts that trigger based on conditions/thresholds.
    Monitors metrics and notifies users when action is needed.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='proactive_alerts')

    # Alert definition
    alert_type = models.CharField(max_length=50, choices=[
        ('threshold', 'Threshold Alert'),
        ('trend', 'Trend Alert'),
        ('anomaly', 'Anomaly Detection'),
        ('opportunity', 'Opportunity Alert'),
        ('deadline', 'Deadline Reminder'),
        ('goal', 'Goal Progress'),
        ('competitor', 'Competitor Activity'),
        ('market', 'Market Change'),
    ])
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Trigger conditions
    metric_name = models.CharField(max_length=100)  # e.g., "daily_revenue", "conversion_rate"
    condition = models.CharField(max_length=20, choices=[
        ('above', 'Above'),
        ('below', 'Below'),
        ('equals', 'Equals'),
        ('change_up', 'Increases By'),
        ('change_down', 'Decreases By'),
        ('anomaly', 'Anomaly Detected'),
    ])
    threshold_value = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    threshold_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Scope
    platform = models.ForeignKey(DistributionPlatform, on_delete=models.CASCADE, null=True, blank=True)
    content_type = models.CharField(max_length=50, blank=True)  # image, video, etc.
    category = models.CharField(max_length=100, blank=True)

    # Timing
    check_frequency = models.CharField(max_length=20, choices=[
        ('realtime', 'Real-time'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ], default='daily')
    cooldown_hours = models.IntegerField(default=24)  # Hours before re-triggering

    # Status
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    trigger_count = models.IntegerField(default=0)

    # Actions when triggered
    notification_channels = models.JSONField(default=list)  # ["email", "push", "sms", "in_app"]
    auto_actions = models.JSONField(default=list)  # Actions to take automatically

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Proactive Alert'
        verbose_name_plural = 'Proactive Alerts'
        ordering = ['-is_active', '-trigger_count']

    def __str__(self):
        return f"[{self.alert_type}] {self.name}"

    def should_trigger(self, current_value: float) -> bool:
        """Check if alert should trigger based on current value."""
        if not self.is_active:
            return False

        # Check cooldown
        if self.last_triggered:
            hours_since = (timezone.now() - self.last_triggered).total_seconds() / 3600
            if hours_since < self.cooldown_hours:
                return False

        if self.threshold_value is None:
            return False

        threshold = float(self.threshold_value)
        if self.condition == 'above':
            return current_value > threshold
        elif self.condition == 'below':
            return current_value < threshold
        elif self.condition == 'equals':
            return abs(current_value - threshold) < 0.001
        return False

    def trigger(self):
        """Mark alert as triggered."""
        self.last_triggered = timezone.now()
        self.trigger_count += 1
        self.save()


class ProactiveNotification(models.Model):
    """
    Notifications sent to users from the proactive system.
    Tracks delivery and user engagement.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='proactive_notifications')

    # Source
    alert = models.ForeignKey(ProactiveAlert, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    suggestion = models.ForeignKey('SmartSuggestion', on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')

    # Notification type
    notification_type = models.CharField(max_length=50, choices=[
        ('alert', 'Alert'),
        ('suggestion', 'Suggestion'),
        ('insight', 'Insight'),
        ('reminder', 'Reminder'),
        ('celebration', 'Celebration'),
        ('warning', 'Warning'),
        ('update', 'System Update'),
        ('action_required', 'Human Action Required'),  # Session 549
    ])
    priority = models.CharField(max_length=20, choices=[
        ('urgent', 'Urgent'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ], default='medium')

    # Content
    title = models.CharField(max_length=200)
    message = models.TextField()
    rich_content = models.JSONField(default=dict)  # Charts, links, data
    icon = models.CharField(max_length=50, default='bell')

    # Call to action
    action_url = models.CharField(max_length=500, blank=True)
    action_label = models.CharField(max_length=100, blank=True)
    quick_actions = models.JSONField(default=list)  # [{"label": "Apply", "action": "apply_suggestion"}]

    # Delivery
    channels_sent = models.JSONField(default=list)  # ["email", "push", "in_app"]
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivery_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ], default='pending')

    # User interaction
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_dismissed = models.BooleanField(default=False)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    is_acted_upon = models.BooleanField(default=False)
    acted_at = models.DateTimeField(null=True, blank=True)
    action_result = models.JSONField(default=dict)

    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)
    is_expired = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Proactive Notification'
        verbose_name_plural = 'Proactive Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'is_dismissed']),
            models.Index(fields=['delivery_status', 'scheduled_at']),
        ]

    def __str__(self):
        return f"[{self.notification_type}] {self.title}"

    def mark_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    def mark_acted(self, result: dict = None):
        """Mark notification as acted upon."""
        self.is_acted_upon = True
        self.acted_at = timezone.now()
        if result:
            self.action_result = result
        self.save()


class SmartSuggestion(models.Model):
    """
    AI-generated suggestions for improving performance.
    Proactively recommends actions based on learned patterns.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='smart_suggestions')

    # Suggestion type
    suggestion_type = models.CharField(max_length=50, choices=[
        ('pricing', 'Pricing Adjustment'),
        ('timing', 'Upload Timing'),
        ('platform', 'Platform Recommendation'),
        ('content', 'Content Improvement'),
        ('tags', 'Tag Optimization'),
        ('description', 'Description Enhancement'),
        ('bundle', 'Bundle Suggestion'),
        ('promotion', 'Promotion Opportunity'),
        ('cross_sell', 'Cross-Sell Opportunity'),
        ('expansion', 'Market Expansion'),
    ])
    category = models.CharField(max_length=50, choices=[
        ('revenue', 'Increase Revenue'),
        ('efficiency', 'Improve Efficiency'),
        ('reach', 'Expand Reach'),
        ('quality', 'Improve Quality'),
        ('risk', 'Reduce Risk'),
    ], default='revenue')

    # Content
    title = models.CharField(max_length=200)
    description = models.TextField()
    detailed_rationale = models.TextField(blank=True)

    # Supporting data
    supporting_patterns = models.JSONField(default=list)  # Pattern IDs that support this
    supporting_data = models.JSONField(default=dict)  # Analytics data
    similar_successes = models.JSONField(default=list)  # Examples that worked

    # Actionable details
    action_steps = models.JSONField(default=list)
    # [{"step": 1, "action": "Update price to $25", "reason": "Based on conversion data"}]

    # Current vs suggested
    current_state = models.JSONField(default=dict)  # {"price": 15, "platform": "etsy"}
    suggested_state = models.JSONField(default=dict)  # {"price": 25}

    # Impact estimation
    estimated_impact = models.JSONField(default=dict)
    # {"revenue_change": "+25%", "conversion_change": "+10%", "time_saved": "2h"}
    estimated_revenue_impact = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, default=50)  # 0-100

    # Priority
    priority_score = models.IntegerField(default=50)  # 0-100, for sorting
    effort_level = models.CharField(max_length=20, choices=[
        ('low', 'Low (Quick Win)'),
        ('medium', 'Medium'),
        ('high', 'High (Requires Work)'),
    ], default='medium')

    # User interaction
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('implemented', 'Implemented'),
        ('expired', 'Expired'),
    ], default='pending')
    user_feedback = models.TextField(blank=True)
    rejection_reason = models.CharField(max_length=100, blank=True)

    # Outcome tracking (if implemented)
    implemented_at = models.DateTimeField(null=True, blank=True)
    outcome_tracked = models.BooleanField(default=False)
    actual_impact = models.JSONField(default=dict)  # Actual measured impact

    # Validity
    valid_until = models.DateTimeField(null=True, blank=True)
    is_still_relevant = models.BooleanField(default=True)

    # Related content
    related_content_ids = models.JSONField(default=list)  # Content this applies to
    related_distribution_ids = models.JSONField(default=list)  # Distributions this applies to

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Smart Suggestion'
        verbose_name_plural = 'Smart Suggestions'
        ordering = ['-priority_score', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status', 'suggestion_type']),
            models.Index(fields=['priority_score', 'confidence_score']),
        ]

    def __str__(self):
        return f"[{self.suggestion_type}] {self.title}"

    def accept(self):
        """Accept the suggestion."""
        self.status = 'accepted'
        self.save()

    def reject(self, reason: str = ''):
        """Reject the suggestion."""
        self.status = 'rejected'
        self.rejection_reason = reason
        self.save()

    def mark_implemented(self):
        """Mark as implemented."""
        self.status = 'implemented'
        self.implemented_at = timezone.now()
        self.save()


class AutomatedAction(models.Model):
    """
    Automated actions that run based on triggers.
    Can be triggered by alerts, schedules, or patterns.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='automated_actions')

    # Action definition
    action_type = models.CharField(max_length=50, choices=[
        ('price_adjust', 'Adjust Pricing'),
        ('distribute', 'Auto-Distribute'),
        ('notify', 'Send Notification'),
        ('tag_update', 'Update Tags'),
        ('schedule_upload', 'Schedule Upload'),
        ('apply_promotion', 'Apply Promotion'),
        ('generate_report', 'Generate Report'),
        ('backup_data', 'Backup Data'),
        ('optimize_listing', 'Optimize Listing'),
    ])
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Trigger configuration
    trigger_type = models.CharField(max_length=50, choices=[
        ('alert', 'On Alert'),
        ('schedule', 'On Schedule'),
        ('event', 'On Event'),
        ('threshold', 'On Threshold'),
        ('manual', 'Manual'),
    ])
    trigger_alert = models.ForeignKey(ProactiveAlert, on_delete=models.SET_NULL, null=True, blank=True, related_name='automated_actions')
    trigger_schedule = models.CharField(max_length=100, blank=True)  # Cron expression
    trigger_event = models.CharField(max_length=100, blank=True)  # Event name

    # Action parameters
    action_params = models.JSONField(default=dict)
    # For price_adjust: {"change_type": "percent", "change_value": 10, "min_price": 5, "max_price": 100}
    # For distribute: {"platforms": ["etsy", "gumroad"], "auto_price": true}

    # Scope/conditions
    conditions = models.JSONField(default=list)
    # [{"field": "content_type", "operator": "equals", "value": "image"}]
    platform_scope = models.JSONField(default=list)  # Platforms this applies to
    content_type_scope = models.JSONField(default=list)  # Content types this applies to

    # Safety limits
    max_executions_per_day = models.IntegerField(default=10)
    max_price_change_percent = models.DecimalField(max_digits=5, decimal_places=2, default=25)
    requires_confirmation = models.BooleanField(default=False)
    dry_run_first = models.BooleanField(default=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_paused = models.BooleanField(default=False)
    pause_reason = models.CharField(max_length=200, blank=True)

    # Execution tracking
    total_executions = models.IntegerField(default=0)
    successful_executions = models.IntegerField(default=0)
    failed_executions = models.IntegerField(default=0)
    last_executed = models.DateTimeField(null=True, blank=True)
    last_result = models.JSONField(default=dict)
    executions_today = models.IntegerField(default=0)
    executions_today_reset = models.DateField(null=True, blank=True)

    # Impact tracking
    total_revenue_impact = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    avg_impact_per_execution = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Automated Action'
        verbose_name_plural = 'Automated Actions'
        ordering = ['-is_active', '-total_executions']

    def __str__(self):
        return f"[{self.action_type}] {self.name}"

    def can_execute(self) -> tuple:
        """Check if action can execute. Returns (can_execute, reason)."""
        if not self.is_active:
            return False, "Action is not active"
        if self.is_paused:
            return False, f"Action is paused: {self.pause_reason}"

        # Check daily limit
        today = timezone.now().date()
        if self.executions_today_reset != today:
            self.executions_today = 0
            self.executions_today_reset = today
            self.save()

        if self.executions_today >= self.max_executions_per_day:
            return False, "Daily execution limit reached"

        return True, "OK"

    def execute(self, context: dict = None) -> dict:
        """Execute the automated action."""
        can_run, reason = self.can_execute()
        if not can_run:
            return {"success": False, "error": reason}

        # Increment counters
        self.total_executions += 1
        self.executions_today += 1
        self.last_executed = timezone.now()

        # Action execution would be handled by the Proactive Engine
        # This is just the model - actual execution logic is in proactive_engine.py

        result = {
            "success": True,
            "action_type": self.action_type,
            "params": self.action_params,
            "context": context or {},
            "executed_at": str(timezone.now()),
        }

        self.last_result = result
        self.successful_executions += 1
        self.save()

        return result


class AutomatedActionLog(models.Model):
    """
    Log of all automated action executions.
    For auditing and debugging.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action = models.ForeignKey(AutomatedAction, on_delete=models.CASCADE, related_name='execution_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='action_logs')

    # Execution details
    trigger_type = models.CharField(max_length=50)
    trigger_source = models.CharField(max_length=200, blank=True)  # Alert ID, event name, etc.

    # Input/Output
    input_params = models.JSONField(default=dict)
    output_result = models.JSONField(default=dict)

    # Status
    status = models.CharField(max_length=20, choices=[
        ('started', 'Started'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('rolled_back', 'Rolled Back'),
    ])
    error_message = models.TextField(blank=True)

    # Impact
    items_affected = models.IntegerField(default=0)
    revenue_impact = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)

    # Rollback info
    can_rollback = models.BooleanField(default=False)
    rollback_data = models.JSONField(default=dict)
    was_rolled_back = models.BooleanField(default=False)

    class Meta:
        app_label = 'core'
        verbose_name = 'Automated Action Log'
        verbose_name_plural = 'Automated Action Logs'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['action', 'status', 'started_at']),
            models.Index(fields=['user', 'started_at']),
        ]

    def __str__(self):
        return f"Log: {self.action.name} - {self.status}"


class UserNotificationPreference(models.Model):
    """
    DEPRECATED - Session 528: This model has 0 records and is not used.

    Original purpose: User preferences for notifications and alerts.
    Controls what notifications users receive and how.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preferences')

    # Channel preferences
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    in_app_enabled = models.BooleanField(default=True)

    # Notification type preferences
    alert_notifications = models.BooleanField(default=True)
    suggestion_notifications = models.BooleanField(default=True)
    insight_notifications = models.BooleanField(default=True)
    celebration_notifications = models.BooleanField(default=True)
    warning_notifications = models.BooleanField(default=True)

    # Frequency preferences
    digest_frequency = models.CharField(max_length=20, choices=[
        ('realtime', 'Real-time'),
        ('hourly', 'Hourly Digest'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Digest'),
    ], default='daily')

    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)  # e.g., 22:00
    quiet_hours_end = models.TimeField(null=True, blank=True)  # e.g., 08:00
    timezone = models.CharField(max_length=50, default='UTC')

    # Priority thresholds
    min_priority_email = models.CharField(max_length=20, default='medium')  # Only email for medium+ priority
    min_priority_push = models.CharField(max_length=20, default='high')  # Only push for high+ priority

    # Category preferences
    enabled_categories = models.JSONField(default=list)
    # ["revenue", "efficiency", "reach"] - empty means all

    # Unsubscribe tracking
    unsubscribed_types = models.JSONField(default=list)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'User Notification Preference'
        verbose_name_plural = 'User Notification Preferences'

    def __str__(self):
        return f"Notification Preferences: {self.user.username}"

    def should_send(self, notification_type: str, priority: str, channel: str) -> bool:
        """Check if notification should be sent based on preferences."""
        # Check channel
        channel_map = {
            'email': self.email_enabled,
            'push': self.push_enabled,
            'sms': self.sms_enabled,
            'in_app': self.in_app_enabled,
        }
        if not channel_map.get(channel, False):
            return False

        # Check notification type
        type_map = {
            'alert': self.alert_notifications,
            'suggestion': self.suggestion_notifications,
            'insight': self.insight_notifications,
            'celebration': self.celebration_notifications,
            'warning': self.warning_notifications,
        }
        if not type_map.get(notification_type, True):
            return False

        # Check priority thresholds for specific channels
        priority_order = ['low', 'medium', 'high', 'urgent']
        if channel == 'email':
            min_idx = priority_order.index(self.min_priority_email)
            curr_idx = priority_order.index(priority) if priority in priority_order else 0
            if curr_idx < min_idx:
                return False
        elif channel == 'push':
            min_idx = priority_order.index(self.min_priority_push)
            curr_idx = priority_order.index(priority) if priority in priority_order else 0
            if curr_idx < min_idx:
                return False

        return True


# ==============================================================================
# Session 235: A/B Testing Framework Models (Phase 6 - Proactive System)
# ==============================================================================

class ABTest(models.Model):
    """
    A/B Test configuration for testing different strategies.
    Tests pricing, titles, tags, timing, and other content variations.
    """
    TEST_TYPES = [
        ('pricing', 'Pricing Test'),
        ('title', 'Title Test'),
        ('tags', 'Tags Test'),
        ('description', 'Description Test'),
        ('timing', 'Timing Test'),
        ('platform', 'Platform Test'),
        ('bundle', 'Bundle Test'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ab_tests',
        null=True,
        blank=True
    )

    # Test Configuration
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    test_type = models.CharField(max_length=50, choices=TEST_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Hypothesis
    hypothesis = models.TextField(blank=True, help_text="What you expect to happen")

    # Test Parameters
    primary_metric = models.CharField(
        max_length=50,
        default='conversion_rate',
        help_text="Main metric to measure success"
    )
    secondary_metrics = models.JSONField(
        default=list,
        blank=True,
        help_text="Additional metrics to track"
    )
    confidence_level = models.FloatField(
        default=0.95,
        help_text="Statistical confidence level (0.90-0.99)"
    )
    minimum_sample_size = models.IntegerField(
        default=100,
        help_text="Minimum samples per variant before concluding"
    )

    # Targeting
    content_filter = models.JSONField(
        default=dict,
        blank=True,
        help_text="Filter which content participates"
    )
    platform_filter = models.JSONField(
        default=list,
        blank=True,
        help_text="Limit to specific platforms"
    )

    # Timeline
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    max_duration_days = models.IntegerField(default=30)

    # Results
    winner_variant = models.ForeignKey(
        'ABTestVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='won_tests'
    )
    conclusion = models.TextField(blank=True)
    statistical_significance = models.FloatField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['test_type', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.test_type})"

    def start_test(self):
        """Start the A/B test."""
        if self.status != 'draft':
            return False
        self.status = 'running'
        self.start_date = timezone.now()
        self.save()
        return True

    def pause_test(self):
        """Pause the A/B test."""
        if self.status != 'running':
            return False
        self.status = 'paused'
        self.save()
        return True

    def complete_test(self, winner_id=None, conclusion=''):
        """Complete the A/B test with results."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.conclusion = conclusion
        if winner_id:
            self.winner_variant_id = winner_id
        self.save()
        return True

    def get_results(self):
        """Get test results with statistics."""
        variants = self.variants.all()
        results = {
            'test_id': str(self.id),
            'name': self.name,
            'status': self.status,
            'variants': [],
            'winner': None,
            'is_significant': False,
        }

        for variant in variants:
            stats = variant.get_statistics()
            results['variants'].append({
                'id': str(variant.id),
                'name': variant.name,
                'is_control': variant.is_control,
                **stats
            })

        # Simple winner determination (could be enhanced with statistical tests)
        if results['variants']:
            best_variant = max(
                results['variants'],
                key=lambda v: v.get('conversion_rate', 0)
            )
            if best_variant.get('sample_size', 0) >= self.minimum_sample_size:
                results['winner'] = best_variant['id']
                results['is_significant'] = True

        return results


class ABTestVariant(models.Model):
    """
    Individual variant within an A/B test.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test = models.ForeignKey(
        ABTest,
        on_delete=models.CASCADE,
        related_name='variants'
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_control = models.BooleanField(default=False)

    # Variant Configuration
    config = models.JSONField(
        default=dict,
        help_text="Variant-specific settings (price, title, etc.)"
    )

    # Traffic Allocation
    traffic_percentage = models.IntegerField(
        default=50,
        help_text="Percentage of traffic to this variant"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_control', 'name']

    def __str__(self):
        control_str = " (Control)" if self.is_control else ""
        return f"{self.name}{control_str}"

    def get_statistics(self):
        """Get variant statistics."""
        events = self.events.all()
        impressions = events.filter(event_type='impression').count()
        conversions = events.filter(event_type='conversion').count()
        revenue = events.filter(
            event_type='conversion'
        ).aggregate(total=models.Sum('revenue'))['total'] or 0

        return {
            'sample_size': impressions,
            'impressions': impressions,
            'conversions': conversions,
            'conversion_rate': (conversions / impressions * 100) if impressions > 0 else 0,
            'revenue': float(revenue),
            'revenue_per_impression': (float(revenue) / impressions) if impressions > 0 else 0,
        }


class ABTestEvent(models.Model):
    """
    Individual event in an A/B test (impression, click, conversion).
    """
    EVENT_TYPES = [
        ('impression', 'Impression'),
        ('click', 'Click'),
        ('conversion', 'Conversion'),
        ('revenue', 'Revenue'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    variant = models.ForeignKey(
        ABTestVariant,
        on_delete=models.CASCADE,
        related_name='events'
    )

    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)

    # Context
    content_id = models.CharField(max_length=255, blank=True)
    platform = models.CharField(max_length=100, blank=True)
    session_id = models.CharField(max_length=255, blank=True)

    # Revenue (for conversion events)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['variant', 'event_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.event_type} for {self.variant.name}"


class UserGoal(models.Model):
    """
    DEPRECATED - Session 528: This model has 0 records and is not used.

    Original purpose: User-defined goals for tracking progress.
    """
    GOAL_TYPES = [
        ('revenue', 'Revenue Goal'),
        ('sales', 'Sales Count'),
        ('downloads', 'Download Count'),
        ('views', 'View Count'),
        ('distribution', 'Distribution Count'),
        ('content', 'Content Created'),
        ('conversion', 'Conversion Rate'),
        ('custom', 'Custom Metric'),
    ]

    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('one_time', 'One Time'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='goals',
        null=True,
        blank=True
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    goal_type = models.CharField(max_length=50, choices=GOAL_TYPES)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='monthly')

    # Target
    target_value = models.DecimalField(max_digits=12, decimal_places=2)
    current_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Custom metric (if goal_type is 'custom')
    custom_metric = models.CharField(max_length=100, blank=True)

    # Progress
    is_achieved = models.BooleanField(default=False)
    achieved_at = models.DateTimeField(null=True, blank=True)

    # Timeline
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    # Settings
    is_active = models.BooleanField(default=True)
    notify_at_milestones = models.BooleanField(default=True)
    milestone_percentages = models.JSONField(
        default=list,
        blank=True,
        help_text="Percentages to notify at (e.g., [25, 50, 75, 100])"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['goal_type', 'is_achieved']),
        ]

    def __str__(self):
        return f"{self.name} ({self.goal_type})"

    @property
    def progress_percentage(self):
        """Calculate progress as percentage."""
        if self.target_value == 0:
            return 0
        return min(100, float(self.current_value / self.target_value * 100))

    def update_progress(self, new_value):
        """Update goal progress."""
        old_value = self.current_value
        self.current_value = new_value

        # Check for achievement
        if not self.is_achieved and self.current_value >= self.target_value:
            self.is_achieved = True
            self.achieved_at = timezone.now()

        self.save()

        # Check milestones
        if self.notify_at_milestones and self.milestone_percentages:
            old_pct = float(old_value / self.target_value * 100) if self.target_value > 0 else 0
            new_pct = self.progress_percentage

            for milestone in self.milestone_percentages:
                if old_pct < milestone <= new_pct:
                    self._notify_milestone(milestone)

        return {
            'progress': self.progress_percentage,
            'is_achieved': self.is_achieved,
        }

    def _notify_milestone(self, milestone):
        """Create notification for milestone reached."""
        try:
            from .proactive_engine import NotificationManager
            manager = NotificationManager()
            manager.send_notification(
                user=self.user,
                notification_type='goal',
                title=f"Goal Progress: {milestone}%!",
                message=f"You've reached {milestone}% of your goal: {self.name}",
                priority='medium' if milestone < 100 else 'high',
                related_model='UserGoal',
                related_id=str(self.id)
            )
        except Exception:
            pass  # Don't fail if notification fails


# =============================================================================
# Session 244: Agent Conversations (Inter-Agent Chat)
# Agents discuss topics with each other, share insights, and debate ideas
# =============================================================================
# DEPRECATED: Session 284 - Merged into HiveMindSession with session_mode='conversation'
# Existing data (2,919 records) preserved but no new records should be created.
# =============================================================================

class AgentConversation(models.Model):
    """
    DEPRECATED - Session 284: Merged into HiveMindSession

    This model is deprecated. Use HiveMindSession with session_mode='conversation' instead.
    Existing 2,919 records are preserved for historical reference.

    Original Purpose (Session 244):
    A conversation between two or more agents discussing a topic.
    This is where the magic happens - agents talking to each other,
    sharing knowledge, asking questions, and forming new insights.

    Migration Path:
    Use HiveMindSession with session_mode='conversation' for new conversations.
    """

    # Deprecation flag - set True to completely disable
    _deprecated = True
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Conversation metadata
    topic = models.CharField(
        max_length=200,
        help_text="What the agents are discussing"
    )

    conversation_type = models.CharField(
        max_length=50,
        choices=[
            ('knowledge_sharing', 'Knowledge Sharing'),
            ('question_answer', 'Question & Answer'),
            ('debate', 'Debate/Discussion'),
            ('brainstorm', 'Brainstorming'),
            ('consultation', 'Expert Consultation'),
            ('synthesis', 'Collaborative Synthesis'),
        ],
        default='knowledge_sharing'
    )

    # Participants
    initiator = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='initiated_conversations',
        help_text="Agent who started the conversation"
    )

    participants = models.ManyToManyField(
        Agent,
        related_name='conversations',
        help_text="All agents participating in this conversation"
    )

    # Context - what triggered this conversation
    trigger_type = models.CharField(
        max_length=50,
        choices=[
            ('learning_transfer', 'During Knowledge Transfer'),
            ('synthesis', 'During Synthesis'),
            ('scheduled', 'Scheduled Discussion'),
            ('user_triggered', 'User Initiated'),
            ('anomaly', 'Anomaly Detected'),
            ('opportunity', 'New Opportunity'),
            ('spider_data', 'New Spider Data'),  # Session 362: Spider-triggered
            ('project_need', 'Project Research Need'),  # Session 362: Project-triggered
        ],
        default='scheduled'
    )

    # Related knowledge that sparked the conversation
    related_knowledge = models.ForeignKey(
        'AgentKnowledgeSource',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversations'
    )

    # Conversation state
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('concluded', 'Concluded'),
            ('paused', 'Paused'),
        ],
        default='active'
    )

    # Outcome
    conclusion = models.TextField(
        blank=True,
        help_text="Summary of what was concluded/learned"
    )

    insights_generated = models.JSONField(
        default=list,
        help_text="New insights that came from this conversation"
    )

    # Metrics
    message_count = models.IntegerField(default=0)
    quality_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="How valuable was this conversation"
    )

    # Session 327: Project context for scoped intelligence
    project = models.ForeignKey(
        'PartnershipProject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='agent_conversations',
        help_text='Session 327: Optional project context for this conversation'
    )

    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ['-started_at']
        verbose_name = "Agent Conversation"
        verbose_name_plural = "Agent Conversations"

    def __str__(self):
        return f"{self.initiator.name}: {self.topic[:50]}"

    def save(self, *args, **kwargs):
        """Override save to log deprecation warning."""
        if not self.pk:  # Only warn on new records
            warnings.warn(
                "AgentConversation is deprecated (Session 284). "
                "Use HiveMindSession with session_mode='conversation' instead.",
                DeprecationWarning,
                stacklevel=2
            )
            logger.warning(
                "DEPRECATED: Creating new AgentConversation. "
                "Use HiveMindSession with session_mode='conversation' instead."
            )
        super().save(*args, **kwargs)

    def add_message(self, agent, content, message_type='statement'):
        """Add a message to this conversation."""
        message = ConversationMessage.objects.create(
            conversation=self,
            agent=agent,
            content=content,
            message_type=message_type,
            sequence_number=self.message_count + 1
        )
        self.message_count += 1
        self.save(update_fields=['message_count'])
        return message

    def conclude(self, conclusion_text, insights=None):
        """End the conversation with a conclusion."""
        self.status = 'concluded'
        self.conclusion = conclusion_text
        if insights:
            self.insights_generated = insights
        self.ended_at = timezone.now()
        self.save()


class ConversationMessage(models.Model):
    """
    A single message in an agent conversation.

    Like a chat message, but between AI agents discussing topics.
    Renamed from AgentMessage to avoid conflict with Session 227 AgentMessage.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    conversation = models.ForeignKey(
        AgentConversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='conversation_messages'
    )

    # Message content
    content = models.TextField(
        help_text="What the agent said"
    )

    message_type = models.CharField(
        max_length=30,
        choices=[
            ('statement', 'Statement'),
            ('question', 'Question'),
            ('answer', 'Answer'),
            ('insight', 'Insight'),
            ('agreement', 'Agreement'),
            ('disagreement', 'Disagreement'),
            ('suggestion', 'Suggestion'),
            ('conclusion', 'Conclusion'),
        ],
        default='statement'
    )

    # Ordering
    sequence_number = models.IntegerField(
        default=1,
        help_text="Order of message in conversation"
    )

    # Reactions from other agents
    reactions = models.JSONField(
        default=dict,
        help_text="Reactions from other participating agents"
    )

    # Quality metrics
    relevance_score = models.FloatField(
        default=0.8,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )

    # Reference to knowledge used (JSON list of knowledge IDs for simplicity)
    referenced_knowledge_ids = models.JSONField(
        default=list,
        help_text="IDs of AgentKnowledgeSource records referenced in this message"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['conversation', 'sequence_number']
        verbose_name = "Conversation Message"
        verbose_name_plural = "Conversation Messages"

    def __str__(self):
        return f"{self.agent.name}: {self.content[:50]}..."

    def add_reaction(self, agent, reaction_type):
        """Add a reaction from another agent."""
        if not self.reactions:
            self.reactions = {}
        self.reactions[str(agent.id)] = {
            'agent_name': agent.name,
            'reaction': reaction_type,
            'timestamp': timezone.now().isoformat()
        }
        self.save(update_fields=['reactions'])


# =============================================================================
# Session 261: Conversation Artifacts - Structured Outputs from Agent Conversations
# =============================================================================

class ConversationArtifact(models.Model):
    """
    Stores structured outputs extracted from agent conversations.

    Session 261: Agent conversations now produce concrete artifacts like
    DecisionSummaries, frameworks, and feature specifications.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    conversation = models.ForeignKey(
        AgentConversation,
        on_delete=models.CASCADE,
        related_name='artifacts'
    )

    # Artifact type
    artifact_type = models.CharField(
        max_length=50,
        choices=[
            ('decision_summary', 'Decision Summary'),
            ('framework', 'Named Framework'),
            ('feature_spec', 'Feature Specification'),
            ('action_plan', 'Action Plan'),
            ('insight_list', 'Insight List'),
            ('trade_off_analysis', 'Trade-off Analysis'),
        ],
        default='decision_summary'
    )

    # Artifact content
    title = models.CharField(max_length=200)
    content = models.JSONField(
        default=dict,
        help_text="Structured content of the artifact"
    )

    # For decision summaries
    insights = models.JSONField(
        default=list,
        help_text="List of insights from the conversation"
    )

    proposed_feature = models.JSONField(
        default=dict,
        help_text="Proposed feature specification"
    )

    next_steps = models.JSONField(
        default=list,
        help_text="Action items from the conversation"
    )

    # Quality metrics from Session 261 validation
    quality_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Quality score (0-100) from conversation validation"
    )

    tension_count = models.IntegerField(
        default=0,
        help_text="Number of tension/disagreement instances in conversation"
    )

    grounding_count = models.IntegerField(
        default=0,
        help_text="Number of platform grounding references in conversation"
    )

    # Grounding references found
    grounding_refs = models.JSONField(
        default=list,
        help_text="List of platform metrics and systems referenced"
    )

    # Validation status
    is_valid = models.BooleanField(
        default=False,
        help_text="Whether the conversation met all contract requirements"
    )

    validation_issues = models.JSONField(
        default=list,
        help_text="List of validation issues if any"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        verbose_name = "Conversation Artifact"
        verbose_name_plural = "Conversation Artifacts"

    def __str__(self):
        return f"{self.artifact_type}: {self.title}"

    @classmethod
    def create_from_orchestrator_result(cls, conversation, result):
        """
        Create a ConversationArtifact from ConversationOrchestrator result.

        Args:
            conversation: AgentConversation instance
            result: Dict from ConversationOrchestrator.generate_conversation()

        Returns:
            ConversationArtifact instance
        """
        decision_summary = result.get('decision_summary') or {}
        validation = result.get('validation') or {}
        state = result.get('state') or {}

        return cls.objects.create(
            conversation=conversation,
            artifact_type='decision_summary',
            title=decision_summary.get('proposed_feature', {}).get('name', 'Conversation Summary'),
            content=decision_summary,
            insights=decision_summary.get('insights', []),
            proposed_feature=decision_summary.get('proposed_feature', {}),
            next_steps=decision_summary.get('next_steps', []),
            quality_score=validation.get('score', 0),
            tension_count=state.get('tension_count', 0),
            grounding_count=state.get('grounding_count', 0),
            grounding_refs=state.get('unique_grounding_refs', []),
            is_valid=validation.get('is_valid', False),
            validation_issues=validation.get('issues', [])
        )


# =============================================================================
# Session 247: Agent Dreams - Sci-Fi Feature
# =============================================================================
# DEPRECATED: Session 284 - This feature adds complexity without clear user value.
# Existing data is preserved, but no new dreams should be created.
# =============================================================================

class AgentDream(models.Model):
    """
    Session 247: Agent Dreams - Creative Ideation Engine
    Session 366: UN-DEPRECATED - Dream Productization Pipeline

    When agents are idle, they "dream" - generating creative ideas,
    speculative concepts, and "what if" scenarios based on their knowledge.

    Session 366 Updates:
    - Removed deprecation - dreams now feed into actionable pipeline
    - Added actionability_score for prioritizing implementable ideas
    - Added relevance_score for project matching
    - Added promoted_to_decision flag for Boardroom surfacing
    - Added directed_topic for user-requested dream focus
    - 10% of dreams are based on [Learned] knowledge from other agents
    """

    # Session 366: UN-DEPRECATED - Dreams are now productized
    _deprecated = False
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey('Agent', on_delete=models.CASCADE, related_name='dreams')

    # Dream content
    title = models.CharField(max_length=200, help_text="Short catchy title for the dream")
    content = models.TextField(help_text="The full dream content/idea")

    # Dream categorization
    dream_type = models.CharField(max_length=50, choices=[
        ('creative_idea', 'Creative Idea'),       # New concept or creation
        ('what_if', 'What If?'),                  # Speculative scenario
        ('mashup', 'Mashup'),                     # Combining two things
        ('prediction', 'Prediction'),             # Future trend prediction
        ('improvement', 'Improvement'),           # Way to improve something
        ('observation', 'Observation'),           # Pattern noticed
        ('wild_thought', 'Wild Thought'),         # Crazy but interesting idea
    ])

    # Dream metadata
    # Session 761: Changed from CharField(200) to TextField for longer inspirations
    inspiration_source = models.TextField(
        blank=True,
        default='',
        help_text="What inspired this dream (knowledge, trend, etc.)"
    )
    related_topics = models.JSONField(
        default=list,
        help_text="List of topics/tags related to this dream"
    )

    # Quality and engagement
    vividness_score = models.FloatField(
        default=0.7,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="How vivid/detailed the dream is (0.0-1.0)"
    )
    creativity_score = models.FloatField(
        default=0.7,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="How creative/novel the dream is (0.0-1.0)"
    )

    # Session 366: Dream Productization Scores
    actionability_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="How implementable/actionable this dream is (0.0-1.0)"
    )
    relevance_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Relevance to active projects (0.0-1.0)"
    )
    composite_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Combined score: (creativity + actionability + relevance) / 3"
    )

    # Session 366: Productization Pipeline
    promoted_to_decision = models.BooleanField(
        default=False,
        help_text="Whether this dream was promoted to Boardroom for decision"
    )
    promoted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the dream was promoted to Boardroom"
    )
    decision_outcome = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('pending', 'Pending Review'),
            ('approved', 'Approved for Implementation'),
            ('deferred', 'Deferred for Later'),
            ('rejected', 'Rejected'),
        ],
        help_text="Outcome from Boardroom decision"
    )

    # Session 366: Directed Dreaming
    directed_topic = models.CharField(
        max_length=200,
        blank=True,
        help_text="User-requested topic for focused dreaming"
    )
    is_directed = models.BooleanField(
        default=False,
        help_text="Whether this was a directed dream (user requested)"
    )

    # Session 765: Origin tracking for proper resurfacing weight
    ORIGIN_CHOICES = [
        ('serious', 'Serious'),           # Genuine serious ideation
        ('speculative', 'Speculative'),   # Exploratory/speculative thinking
        ('probe', 'Probe'),               # User testing/probing the system
        ('joke', 'Joke'),                 # Humorous/not serious
    ]
    origin = models.CharField(
        max_length=20,
        choices=ORIGIN_CHOICES,
        default='serious',
        db_index=True,
        help_text="Origin intent of this dream - affects resurfacing weight"
    )
    confidence_floor = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Minimum confidence threshold for resurfacing (0=always, 1=never resurface)"
    )
    human_intent = models.TextField(
        blank=True,
        help_text="Raw human intent description for context (e.g., 'just testing', 'serious idea')"
    )

    # User interaction
    shown_to_user = models.BooleanField(default=False)
    shown_at = models.DateTimeField(null=True, blank=True)
    user_reaction = models.CharField(max_length=50, blank=True, choices=[
        ('loved', 'Loved It'),
        ('interesting', 'Interesting'),
        ('meh', 'Meh'),
        ('dismissed', 'Dismissed'),
    ])
    user_feedback = models.TextField(blank=True)

    # Session 327: Project context for scoped intelligence
    project = models.ForeignKey(
        'PartnershipProject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='agent_dreams',
        help_text='Session 327: Optional project context for this dream'
    )

    # Session 862: Content Flow Traceability
    initiative = models.ForeignKey(
        'core.Initiative',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='source_dreams',
        help_text="Session 862: Initiative created from this dream"
    )

    # Timestamps
    dreamed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-dreamed_at']
        verbose_name = "Agent Dream"
        verbose_name_plural = "Agent Dreams"
        indexes = [
            models.Index(fields=['agent', '-dreamed_at']),
            models.Index(fields=['dream_type', 'shown_to_user']),
            # Session 366: Productization indexes
            models.Index(fields=['-composite_score', '-dreamed_at']),
            models.Index(fields=['promoted_to_decision', 'decision_outcome']),
            models.Index(fields=['is_directed', '-dreamed_at']),
            # Session 765: Origin-aware queries
            models.Index(fields=['origin', '-composite_score']),
            models.Index(fields=['origin', 'shown_to_user', '-composite_score']),
        ]

    def __str__(self):
        return f"{self.agent.name}'s dream: {self.title}"

    # Session 765: Origin weight multipliers for resurfacing
    ORIGIN_WEIGHTS = {
        'serious': 1.0,       # Full weight - genuine ideas
        'speculative': 0.8,   # Slightly reduced - exploratory
        'probe': 0.3,         # Heavily reduced - user testing
        'joke': 0.1,          # Almost never resurface - humor
    }

    @property
    def origin_weight(self):
        """Get the weight multiplier for this dream's origin."""
        return self.ORIGIN_WEIGHTS.get(self.origin, 1.0)

    def save(self, *args, **kwargs):
        """Session 366/765: Calculate composite score on save with origin weighting."""
        # Calculate base composite score from component scores
        base_score = (
            self.creativity_score +
            self.actionability_score +
            self.relevance_score
        ) / 3.0

        # Session 765: Apply origin weight to composite score
        # Jokes and probes get lower scores, affecting resurfacing priority
        self.composite_score = base_score * self.origin_weight

        super().save(*args, **kwargs)

    def mark_as_shown(self):
        """Mark this dream as shown to the user."""
        self.shown_to_user = True
        self.shown_at = timezone.now()
        self.save(update_fields=['shown_to_user', 'shown_at'])

    def record_reaction(self, reaction, feedback=''):
        """Record user's reaction to this dream."""
        self.user_reaction = reaction
        self.user_feedback = feedback
        self.save(update_fields=['user_reaction', 'user_feedback'])

    @classmethod
    def get_unshown_dreams(cls, limit=10, include_jokes=False, include_probes=True):
        """Get dreams that haven't been shown to the user yet.

        Session 765: Now respects origin and confidence_floor for resurfacing.
        - Jokes are excluded by default (include_jokes=False)
        - Probes are included but scored lower
        - Orders by composite_score (which already has origin weight applied)
        """
        queryset = cls.objects.filter(shown_to_user=False)

        # Session 765: Apply origin filtering
        excluded_origins = []
        if not include_jokes:
            excluded_origins.append('joke')
        if not include_probes:
            excluded_origins.append('probe')

        if excluded_origins:
            queryset = queryset.exclude(origin__in=excluded_origins)

        # Order by composite_score (already weighted by origin) then by date
        return queryset.select_related('agent').order_by('-composite_score', '-dreamed_at')[:limit]

    @classmethod
    def get_dreams_while_away(cls, since_datetime, limit=5, include_jokes=False):
        """Get dreams that happened since a given time (while user was away).

        Session 765: Excludes jokes by default.
        """
        queryset = cls.objects.filter(
            dreamed_at__gte=since_datetime,
            shown_to_user=False
        )

        # Session 765: Exclude jokes by default
        if not include_jokes:
            queryset = queryset.exclude(origin='joke')

        return queryset.select_related('agent').order_by('-composite_score', '-dreamed_at')[:limit]

    # Session 366: Productization Pipeline Methods
    def promote_to_boardroom(self, force=False):
        """Promote this dream to the Boardroom for decision-making.

        Session 765: Prevents promotion of jokes/probes unless forced.
        """
        # Session 765: Block promotion of jokes and probes by default
        if not force and self.origin in ['joke', 'probe']:
            raise ValueError(
                f"Cannot promote {self.origin} dream to Boardroom. "
                f"Use force=True to override or change origin to 'serious'."
            )

        self.promoted_to_decision = True
        self.promoted_at = timezone.now()
        self.decision_outcome = 'pending'
        self.save(update_fields=['promoted_to_decision', 'promoted_at', 'decision_outcome'])
        return self

    def record_decision(self, outcome, feedback=''):
        """Record the Boardroom decision for this dream."""
        self.decision_outcome = outcome
        if feedback:
            self.user_feedback = feedback
        self.save(update_fields=['decision_outcome', 'user_feedback'])
        return self

    def link_to_project(self, project):
        """Link this dream to a project for implementation."""
        self.project = project
        self.save(update_fields=['project'])
        return self

    @classmethod
    def get_top_actionable_dreams(cls, limit=10, min_score=0.5, serious_only=True):
        """Get highest-scoring actionable dreams not yet promoted.

        Session 765: Now filters by origin.
        - serious_only=True (default): Only serious and speculative dreams
        - Jokes and probes excluded from boardroom promotion candidates
        """
        queryset = cls.objects.filter(
            composite_score__gte=min_score,
            promoted_to_decision=False
        )

        # Session 765: Exclude jokes and probes from top actionable by default
        if serious_only:
            queryset = queryset.filter(origin__in=['serious', 'speculative'])

        return queryset.select_related('agent').order_by('-composite_score', '-dreamed_at')[:limit]

    @classmethod
    def get_dreams_for_project(cls, project, limit=10):
        """Get dreams relevant to a specific project."""
        return cls.objects.filter(
            project=project
        ).select_related('agent').order_by('-composite_score', '-dreamed_at')[:limit]

    @classmethod
    def get_pending_boardroom_dreams(cls, limit=10):
        """Get dreams pending Boardroom decision."""
        return cls.objects.filter(
            promoted_to_decision=True,
            decision_outcome='pending'
        ).select_related('agent').order_by('-composite_score', '-promoted_at')[:limit]

    @classmethod
    def get_directed_dreams(cls, topic=None, limit=10):
        """Get directed dreams, optionally filtered by topic."""
        qs = cls.objects.filter(is_directed=True)
        if topic:
            qs = qs.filter(directed_topic__icontains=topic)
        return qs.select_related('agent').order_by('-dreamed_at')[:limit]

    # Session 862: Content Flow Unification - Dream → Initiative Bridge
    def promote_to_initiative(self, approved_by='system', bypass_circuit_breaker=False):
        """
        Session 862: Create an Initiative from this Dream.

        Called when dream is approved in boardroom. Creates a full Initiative
        with Stage 1 (Research Brief) ready for research agents to work on.

        Args:
            approved_by: Who approved this dream (user or 'system')
            bypass_circuit_breaker: Skip backlog check (for manual/admin use)

        Returns:
            Initiative: The created initiative, or existing one if already promoted

        Raises:
            ValueError: If circuit breaker blocks creation due to backlog
        """
        from core.models_document_registry import Initiative, InitiativeStage
        from core.services.initiative_title_generator import generate_initiative_title

        # Already promoted - return existing Initiative
        if self.initiative:
            return self.initiative

        # Session 884: Circuit breaker check
        from core.services.initiative_circuit_breaker import can_create_initiative
        if not can_create_initiative(bypass_check=bypass_circuit_breaker):
            raise ValueError("Initiative creation paused by circuit breaker - backlog too high")

        # Session 916: Use title generator for clean initiative names
        initiative_name = generate_initiative_title(
            content=self.content or '',
            topic_hint=self.title,
            max_length=80,
            use_llm=True
        )

        # Session 1020: Dedup check — reuse similar initiative instead of creating duplicate
        from core.services.initiative_circuit_breaker import find_similar_initiative
        existing = find_similar_initiative(initiative_name)
        if existing:
            import logging
            logging.getLogger(__name__).info(
                f"[Session 1020] Dream '{self.title[:40]}' matched existing initiative '{existing.name[:40]}' — reusing"
            )
            self.initiative = existing
            self.promoted_to_decision = True
            self.promoted_at = timezone.now()
            self.decision_outcome = 'approved'
            self.save(update_fields=['initiative', 'promoted_to_decision', 'promoted_at', 'decision_outcome'])
            return existing

        # Create the Initiative from Dream
        # Session 994: Auto-created → TRIAGE. Boardroom-approved dreams still go through triage.
        initiative = Initiative.objects.create(
            name=initiative_name,
            description=self.content,
            status='TRIAGE',
            current_stage=1,
            created_by=self.agent.name if self.agent else 'system',
            parent_topic=self.title[:200] if self.title else '',  # Original dream title for reference
            owner_agent=self.agent.name if self.agent else '',  # Session 996: Auto-assign from dream's agent
        )

        # Create Stage 1 (Research Brief) as DRAFT
        InitiativeStage.objects.create(
            initiative=initiative,
            stage=1,  # RESEARCH_BRIEF
            status='DRAFT',
            notes=f"Created from Dream: {self.title}\n\nDream Content:\n{self.content}\n\nDream Type: {self.dream_type}\nApproved By: {approved_by}",
        )

        # Session 1016: Auto-link to signal cluster
        try:
            from core.services.initiative_signal_linker import auto_link_initiative_signals
            auto_link_initiative_signals(initiative)
        except Exception as e:
            import logging
            logging.getLogger(__name__).debug(f"Signal auto-link skipped: {e}")

        # Link dream to initiative and mark as promoted
        self.initiative = initiative
        self.promoted_to_decision = True
        self.promoted_at = timezone.now()
        self.decision_outcome = 'approved'
        self.save(update_fields=['initiative', 'promoted_to_decision', 'promoted_at', 'decision_outcome'])

        return initiative


class ContentQualityBlacklist(models.Model):
    """
    Session 770: Bad Idea Blacklist

    Tracks topics, patterns, and concepts that should NOT be used for:
    - Dream inspiration
    - Knowledge source creation
    - Content generation

    When an idea is flagged as problematic (e.g., test probes, bad concepts),
    it gets added here to prevent recycling.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # What to block
    BLOCK_TYPE_CHOICES = [
        ('topic', 'Topic'),              # Block specific topic/phrase
        ('pattern', 'Pattern'),          # Block regex pattern
        ('concept', 'Concept'),          # Block conceptual category
    ]
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPE_CHOICES, default='topic')
    pattern = models.CharField(
        max_length=500,
        help_text="The topic, phrase, or regex pattern to block"
    )
    pattern_normalized = models.CharField(
        max_length=500,
        db_index=True,
        help_text="Lowercase normalized version for matching"
    )

    # Why it's blocked
    REASON_CHOICES = [
        ('test_probe', 'Test/Probe'),         # User was testing the system
        ('joke', 'Joke/Humor'),               # Not serious
        ('unrealistic', 'Unrealistic'),       # Mythology violation
        ('harmful', 'Harmful'),               # Could cause harm
        ('low_quality', 'Low Quality'),       # Generic/template content
        ('recycled', 'Over-recycled'),        # Topic used too many times
        ('user_rejected', 'User Rejected'),   # User explicitly rejected
    ]
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    reason_detail = models.TextField(blank=True, help_text="Detailed explanation")

    # Scope
    is_global = models.BooleanField(default=True, help_text="Applies to all users")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='content_blacklist',
        help_text="User-specific blacklist item (if not global)"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blacklist_created',
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this blacklist item expires (null = permanent)"
    )
    is_active = models.BooleanField(default=True)

    # Stats
    times_blocked = models.IntegerField(default=0)
    last_blocked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Content Quality Blacklist'
        verbose_name_plural = 'Content Quality Blacklist Items'
        indexes = [
            models.Index(fields=['pattern_normalized', 'is_active']),
            models.Index(fields=['block_type', 'is_active']),
        ]

    def __str__(self):
        return f"[{self.block_type}] {self.pattern[:50]} ({self.reason})"

    def save(self, *args, **kwargs):
        # Normalize pattern for matching
        self.pattern_normalized = self.pattern.lower().strip()
        super().save(*args, **kwargs)

    def record_block(self):
        """Record that this pattern blocked something."""
        self.times_blocked += 1
        self.last_blocked_at = timezone.now()
        self.save(update_fields=['times_blocked', 'last_blocked_at'])

    @classmethod
    def is_blocked(cls, text: str, user=None) -> tuple:
        """
        Check if text matches any blacklist pattern.

        Returns:
            tuple: (is_blocked: bool, blacklist_item: ContentQualityBlacklist or None)
        """
        import re
        text_lower = text.lower().strip()

        # Get active blacklist items
        items = cls.objects.filter(is_active=True)

        # Apply expiry filter
        items = items.filter(
            models.Q(expires_at__isnull=True) |
            models.Q(expires_at__gt=timezone.now())
        )

        # Apply scope filter
        if user:
            items = items.filter(
                models.Q(is_global=True) |
                models.Q(user=user)
            )
        else:
            items = items.filter(is_global=True)

        for item in items:
            matched = False

            if item.block_type == 'topic':
                # Simple substring match
                if item.pattern_normalized in text_lower:
                    matched = True
            elif item.block_type == 'pattern':
                # Regex match
                try:
                    if re.search(item.pattern, text, re.IGNORECASE):
                        matched = True
                except re.error:
                    pass  # Invalid regex, skip
            elif item.block_type == 'concept':
                # Conceptual match - check if any word matches
                pattern_words = set(item.pattern_normalized.split())
                text_words = set(text_lower.split())
                if pattern_words & text_words:  # Intersection
                    matched = True

            if matched:
                item.record_block()
                return True, item

        return False, None

    @classmethod
    def add_blacklist(cls, pattern: str, reason: str, block_type: str = 'topic',
                      reason_detail: str = '', user=None, created_by=None,
                      expires_at=None) -> 'ContentQualityBlacklist':
        """Add a new blacklist item."""
        return cls.objects.create(
            pattern=pattern,
            block_type=block_type,
            reason=reason,
            reason_detail=reason_detail,
            is_global=user is None,
            user=user,
            created_by=created_by,
            expires_at=expires_at,
        )


class TopicDiversityTracker(models.Model):
    """
    Session 770: Topic Diversity Tracking

    Tracks how often topics are used for dream generation to prevent
    excessive recycling of the same ideas.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    topic = models.CharField(max_length=200, db_index=True)
    topic_normalized = models.CharField(max_length=200, db_index=True)

    # Usage counts
    dream_count = models.IntegerField(default=0)
    knowledge_count = models.IntegerField(default=0)
    last_used_at = models.DateTimeField(auto_now=True)
    first_used_at = models.DateTimeField(auto_now_add=True)

    # Cooldown management
    cooldown_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Topic is on cooldown until this time"
    )

    class Meta:
        app_label = 'core'
        verbose_name = 'Topic Diversity Tracker'
        verbose_name_plural = 'Topic Diversity Trackers'

    def __str__(self):
        return f"{self.topic} (dreams: {self.dream_count})"

    def save(self, *args, **kwargs):
        self.topic_normalized = self.topic.lower().strip()
        super().save(*args, **kwargs)

    def record_dream_use(self):
        """Record that this topic was used for a dream."""
        self.dream_count += 1
        self.last_used_at = timezone.now()

        # Apply cooldown if used too frequently
        # More than 5 dreams in last 24h = 24h cooldown
        # More than 10 total = 48h cooldown
        if self.dream_count > 10:
            self.cooldown_until = timezone.now() + timedelta(hours=48)
        elif self.dream_count > 5:
            self.cooldown_until = timezone.now() + timedelta(hours=24)

        self.save()

    @property
    def is_on_cooldown(self) -> bool:
        """Check if topic is currently on cooldown."""
        if not self.cooldown_until:
            return False
        return timezone.now() < self.cooldown_until

    @classmethod
    def get_or_create_topic(cls, topic: str) -> 'TopicDiversityTracker':
        """Get or create a tracker for a topic."""
        normalized = topic.lower().strip()
        tracker, _ = cls.objects.get_or_create(
            topic_normalized=normalized,
            defaults={'topic': topic}
        )
        return tracker

    @classmethod
    def is_topic_available(cls, topic: str) -> tuple:
        """
        Check if a topic is available for use (not on cooldown).

        Returns:
            tuple: (is_available: bool, tracker: TopicDiversityTracker or None, reason: str)
        """
        try:
            tracker = cls.objects.get(topic_normalized=topic.lower().strip())
            if tracker.is_on_cooldown:
                return False, tracker, f"Topic on cooldown until {tracker.cooldown_until}"
            return True, tracker, "Topic available"
        except cls.DoesNotExist:
            return True, None, "New topic"


class DreamImplementation(models.Model):
    """
    Session 367: Dream Implementation Pipeline

    When a dream is approved in the Boardroom, it creates an implementation
    record that tracks the dream -> deliverable lifecycle.

    Flow:
    1. Dream approved -> DreamImplementation created (status=pending)
    2. Agent assigned -> status=assigned
    3. Agent starts work -> status=in_progress
    4. Agent completes -> status=completed with deliverable
    5. User validates -> status=validated or status=rejected

    This completes the dream productization pipeline:
    Generate -> Score -> Promote -> Decide -> Implement -> Deliver
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Source dream
    dream = models.OneToOneField(
        'AgentDream',
        on_delete=models.CASCADE,
        related_name='implementation'
    )

    # Assigned agent (can be different from the dreaming agent)
    assigned_agent = models.ForeignKey(
        'Agent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dream_implementations',
        help_text="Agent assigned to implement this dream"
    )

    # Target project (inherited from dream or assigned)
    project = models.ForeignKey(
        'PartnershipProject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dream_implementations',
        help_text="Project this implementation is for"
    )

    # Implementation status
    STATUS_CHOICES = [
        ('pending', 'Pending Assignment'),
        ('assigned', 'Agent Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('validated', 'User Validated'),
        ('rejected', 'Rejected/Failed'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Implementation type - what kind of deliverable?
    IMPLEMENTATION_TYPES = [
        ('feature', 'New Feature'),
        ('improvement', 'Improvement/Enhancement'),
        ('content', 'Content Creation'),
        ('research', 'Research/Analysis'),
        ('experiment', 'Experiment'),
        ('workflow', 'Workflow Automation'),
        ('visual', 'Visual/Image Creation'),  # Session 370: Visual dream execution
        ('other', 'Other'),
    ]
    implementation_type = models.CharField(
        max_length=30,
        choices=IMPLEMENTATION_TYPES,
        default='feature'
    )

    # Implementation plan (generated by agent)
    implementation_plan = models.TextField(
        blank=True,
        help_text="Step-by-step plan to implement this dream"
    )

    # Deliverables
    deliverable_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Type of deliverable (code, document, image, etc.)"
    )
    deliverable_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Path or URL to the deliverable"
    )
    deliverable_summary = models.TextField(
        blank=True,
        help_text="Summary of what was delivered"
    )
    deliverable_content = models.TextField(
        blank=True,
        help_text="Full content of the deliverable (report, spec, etc.)"
    )

    # Session 370: Generated media for visual implementations
    generated_media = models.JSONField(
        default=list,
        blank=True,
        help_text="List of generated images/videos [{id, url, prompt, type}]"
    )

    # Quality metrics
    effort_estimate = models.CharField(
        max_length=20,
        blank=True,
        help_text="Estimated effort (small/medium/large)"
    )
    actual_effort = models.CharField(
        max_length=20,
        blank=True,
        help_text="Actual effort spent"
    )
    quality_rating = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="User rating of implementation quality (0-1)"
    )

    # User feedback
    user_feedback = models.TextField(
        blank=True,
        help_text="User feedback on the implementation"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    validated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Dream Implementation"
        verbose_name_plural = "Dream Implementations"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['assigned_agent', 'status']),
        ]

    def __str__(self):
        dream_title = self.dream.title[:30] if self.dream else 'Unknown'
        return f"Implementation: {dream_title} ({self.status})"

    def assign_agent(self, agent):
        """Assign an agent to implement this dream."""
        self.assigned_agent = agent
        self.status = 'assigned'
        self.assigned_at = timezone.now()
        self.save(update_fields=['assigned_agent', 'status', 'assigned_at'])
        return self

    def start_implementation(self, plan=''):
        """Mark implementation as started."""
        self.status = 'in_progress'
        self.started_at = timezone.now()
        if plan:
            self.implementation_plan = plan
        self.save(update_fields=['status', 'started_at', 'implementation_plan'])
        return self

    def complete_implementation(self, deliverable_type='', deliverable_path='', summary=''):
        """Mark implementation as complete with deliverable."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.deliverable_type = deliverable_type
        self.deliverable_path = deliverable_path
        self.deliverable_summary = summary
        self.save(update_fields=[
            'status', 'completed_at', 'deliverable_type',
            'deliverable_path', 'deliverable_summary'
        ])
        return self

    def validate(self, rating=None, feedback=''):
        """User validates the implementation - ready for execution engine to process."""
        self.status = 'validated'
        self.validated_at = timezone.now()
        # Clear completed_at so execution engine will pick this up
        # (it filters for completed_at__isnull=True)
        self.completed_at = None
        if rating is not None:
            self.quality_rating = rating
        if feedback:
            self.user_feedback = feedback
        self.save(update_fields=['status', 'validated_at', 'completed_at', 'quality_rating', 'user_feedback'])
        return self

    def reject(self, reason=''):
        """User rejects the implementation."""
        self.status = 'rejected'
        self.validated_at = timezone.now()
        self.user_feedback = reason
        self.save(update_fields=['status', 'validated_at', 'user_feedback'])
        return self

    @classmethod
    def create_from_approved_dream(cls, dream, implementation_type='feature'):
        """Create an implementation record when a dream is approved."""
        return cls.objects.create(
            dream=dream,
            project=dream.project,  # Inherit project from dream
            implementation_type=implementation_type,
            status='pending'
        )

    @classmethod
    def get_pending_implementations(cls, limit=10):
        """Get implementations waiting for agent assignment."""
        return cls.objects.filter(
            status='pending'
        ).select_related('dream', 'dream__agent', 'project').order_by('-created_at')[:limit]

    @classmethod
    def get_in_progress(cls, agent=None, limit=10):
        """Get implementations in progress, optionally filtered by agent."""
        qs = cls.objects.filter(status='in_progress')
        if agent:
            qs = qs.filter(assigned_agent=agent)
        return qs.select_related('dream', 'dream__agent', 'project').order_by('-started_at')[:limit]


class DreamFeedbackPreference(models.Model):
    """
    Session 249: Dream Feedback System

    Tracks user preferences learned from dream reactions to influence
    future dream generation. When users react to dreams (like, interesting,
    explore), we learn what types of dreams and topics they prefer.

    This creates a feedback loop where agent dreams become more aligned
    with what users find valuable over time.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # What we're tracking preferences for
    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='dream_preferences',
        null=True,
        blank=True,
        help_text="Specific agent preference (null = global preference)"
    )
    dream_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Dream type preference (creative_idea, what_if, etc.)"
    )
    topic = models.CharField(
        max_length=200,
        blank=True,
        help_text="Topic/subject preference learned from inspiration_source"
    )

    # Reaction counts - track all reaction types
    like_count = models.PositiveIntegerField(default=0)
    interesting_count = models.PositiveIntegerField(default=0)
    explore_count = models.PositiveIntegerField(default=0)

    # Calculated preference score (updated on each reaction)
    # Like = 1 point, Interesting = 2 points, Explore = 3 points
    preference_score = models.FloatField(
        default=0.0,
        help_text="Weighted score: like=1, interesting=2, explore=3"
    )

    # Decay tracking - preferences should fade over time if not reinforced
    last_reaction_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Dream Feedback Preference"
        verbose_name_plural = "Dream Feedback Preferences"
        # Unique constraint: one preference record per agent+type+topic combo
        constraints = [
            models.UniqueConstraint(
                fields=['agent', 'dream_type', 'topic'],
                name='unique_dream_preference'
            )
        ]
        indexes = [
            models.Index(fields=['-preference_score']),
            models.Index(fields=['dream_type', '-preference_score']),
            models.Index(fields=['agent', '-preference_score']),
        ]

    def __str__(self):
        parts = []
        if self.agent:
            parts.append(f"Agent: {self.agent.name}")
        if self.dream_type:
            parts.append(f"Type: {self.dream_type}")
        if self.topic:
            parts.append(f"Topic: {self.topic[:30]}")
        return f"DreamPref({', '.join(parts)}) score={self.preference_score:.1f}"

    def record_reaction(self, reaction_type):
        """
        Record a reaction and update the preference score.

        Args:
            reaction_type: 'like', 'interesting', or 'explore'
        """
        if reaction_type == 'like':
            self.like_count += 1
        elif reaction_type == 'interesting':
            self.interesting_count += 1
        elif reaction_type == 'explore':
            self.explore_count += 1

        # Recalculate weighted score
        self.preference_score = (
            self.like_count * 1.0 +
            self.interesting_count * 2.0 +
            self.explore_count * 3.0
        )
        self.save()

    @classmethod
    def get_or_create_preference(cls, agent=None, dream_type='', topic=''):
        """Get or create a preference record for the given criteria."""
        # Normalize empty strings to empty
        dream_type = dream_type or ''
        topic = topic[:200] if topic else ''

        preference, created = cls.objects.get_or_create(
            agent=agent,
            dream_type=dream_type,
            topic=topic
        )
        return preference

    @classmethod
    def get_top_preferences(cls, preference_type='dream_type', limit=10):
        """
        Get top preferences by type.

        Args:
            preference_type: 'dream_type', 'topic', or 'agent'
            limit: Max results to return

        Returns:
            List of (value, score) tuples
        """
        from django.db.models import Sum

        if preference_type == 'dream_type':
            return cls.objects.exclude(dream_type='').values('dream_type').annotate(
                total_score=Sum('preference_score')
            ).order_by('-total_score')[:limit]
        elif preference_type == 'topic':
            return cls.objects.exclude(topic='').values('topic').annotate(
                total_score=Sum('preference_score')
            ).order_by('-total_score')[:limit]
        elif preference_type == 'agent':
            return cls.objects.exclude(agent__isnull=True).values(
                'agent__name'
            ).annotate(
                total_score=Sum('preference_score')
            ).order_by('-total_score')[:limit]

        return []

    @classmethod
    def get_dream_type_weights(cls):
        """
        Get weighted probabilities for dream types based on user preferences.

        Returns:
            Dict mapping dream_type to weight (higher = more likely to generate)
        """
        from django.db.models import Sum

        # Base weights (equal probability)
        base_types = [
            'creative_idea', 'what_if', 'mashup', 'prediction',
            'improvement', 'observation', 'wild_thought'
        ]
        weights = {dt: 1.0 for dt in base_types}

        # Get preference scores by dream type
        preferences = cls.objects.exclude(dream_type='').values('dream_type').annotate(
            total_score=Sum('preference_score')
        )

        # Boost weights based on preferences
        for pref in preferences:
            dream_type = pref['dream_type']
            if dream_type in weights:
                # Add preference score as boost (normalized)
                weights[dream_type] += pref['total_score'] * 0.5

        return weights

    @classmethod
    def get_preferred_topics(cls, limit=20):
        """
        Get list of topics that users have shown interest in.

        Returns:
            List of topic strings, ordered by preference
        """
        from django.db.models import Sum

        topics = cls.objects.exclude(topic='').values('topic').annotate(
            total_score=Sum('preference_score')
        ).order_by('-total_score')[:limit]

        return [t['topic'] for t in topics]


class DreamExploration(models.Model):
    """
    DEPRECATED - Session 290: Sci-Fi Feature Rationalization

    This model is deprecated because its parent (AgentDream) is deprecated.
    No new DreamExploration records should be created.

    Original Purpose (Session 249):
    When a user clicks "Explore" on a dream, we create a deeper exploration
    of that topic. This model tracks those explorations and their outcomes.

    Reason for Deprecation:
    - Parent AgentDream is deprecated (Session 284)
    - Only 4 records ever created (minimal usage)
    - Feature never surfaced in active UI
    """

    # Deprecation flag - set True to completely disable
    _deprecated = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to the original dream
    dream = models.ForeignKey(
        'AgentDream',
        on_delete=models.CASCADE,
        related_name='explorations'
    )

    # Exploration status
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')

    # Exploration results
    exploration_content = models.TextField(
        blank=True,
        help_text="Deeper exploration/research on the dream topic"
    )
    insights_generated = models.JSONField(
        default=list,
        help_text="List of insights discovered during exploration"
    )
    related_knowledge_added = models.BooleanField(
        default=False,
        help_text="Whether this exploration added to agent's knowledge"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Dream Exploration"
        verbose_name_plural = "Dream Explorations"
        ordering = ['-created_at']

    def __str__(self):
        return f"Exploration of '{self.dream.title}' ({self.status})"


# =============================================================================
# Session 250: Hive Mind Mode
# =============================================================================

class HiveMindSession(models.Model):
    """
    Session 250: Hive Mind Mode
    Session 284: Extended to support conversation mode (merging AgentConversation)

    All agents work on a problem simultaneously, each contributing their specialty.
    Creates a "collective intelligence" experience where multiple AI perspectives
    combine to solve complex problems.

    Session 284 Update:
    Now supports two modes:
    - 'hive_mind': Original collective problem-solving mode
    - 'conversation': Agent-to-agent conversation mode (replaces AgentConversation)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Session 284: Mode selector to support different interaction patterns
    # Session 906: Added 'autonomous' for auto-created initiatives
    SESSION_MODE_CHOICES = [
        ('hive_mind', 'Hive Mind'),       # Original mode - collective problem solving
        ('conversation', 'Conversation'),  # Agent-to-agent conversation (merged from AgentConversation)
        ('autonomous', 'Autonomous'),      # Session 906: Auto-triggered by system (blocked research, etc.)
    ]
    session_mode = models.CharField(
        max_length=20,
        choices=SESSION_MODE_CHOICES,
        default='hive_mind',
        help_text="Session 284: Mode of interaction (hive_mind, conversation, or autonomous)"
    )

    # The question/task posed to the hive
    question = models.TextField(
        help_text="The question or task posed to the collective agents"
    )
    context = models.TextField(
        blank=True,
        help_text="Additional context provided by the user"
    )

    # Session 284: Conversation-specific fields
    conversation_topic = models.CharField(
        max_length=200,
        blank=True,
        help_text="Topic for conversation mode sessions"
    )

    # Session 826: Goal-driven conversation fields
    CONVERSATION_TYPE_CHOICES = [
        ('general', 'General'),           # Default free-form conversation
        ('analytical', 'Analytical'),     # Propose → Challenge → Synthesize → Decide
        ('creative', 'Creative'),         # Brainstorm → Expand → Refine → Select
        ('debate', 'Debate'),             # Position → Counter → Rebut → Conclude
        ('planning', 'Planning'),         # Goals → Steps → Dependencies → Schedule
        ('critique', 'Critique'),         # Present → Challenge → Defend → Improve
    ]
    conversation_type = models.CharField(
        max_length=20,
        choices=CONVERSATION_TYPE_CHOICES,
        default='general',
        help_text="Session 826: Type of conversation flow (determines turn structure)"
    )
    objective = models.TextField(
        blank=True,
        help_text="Session 826: Clear objective for the conversation (what should be achieved)"
    )
    success_criteria = models.JSONField(
        default=list,
        blank=True,
        help_text="Session 826: List of success criteria to evaluate conversation outcome"
    )
    auto_selected_agents = models.BooleanField(
        default=False,
        help_text="Session 826: Whether agents were auto-selected based on topic"
    )
    rich_context_injected = models.BooleanField(
        default=False,
        help_text="Session 826: Whether spider/advisor/learning context was injected"
    )

    # Session status
    STATUS_CHOICES = [
        ('initializing', 'Initializing'),
        ('gathering', 'Gathering Contributions'),
        ('synthesizing', 'Synthesizing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('active', 'Active'),  # Session 284: For ongoing conversations
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='initializing')

    # Participating agents (stored as list of agent IDs)
    participant_ids = models.JSONField(
        default=list,
        help_text="List of agent UUIDs participating in this session"
    )

    # Results
    synthesis = models.TextField(
        blank=True,
        help_text="The final synthesized output combining all contributions"
    )
    synthesis_summary = models.CharField(
        max_length=500,
        blank=True,
        help_text="Brief summary of the synthesis"
    )

    # Stats
    contribution_count = models.PositiveIntegerField(default=0)
    total_thinking_time = models.FloatField(
        default=0.0,
        help_text="Total seconds of agent thinking time"
    )

    # Session 327: Project context for scoped intelligence
    project = models.ForeignKey(
        'PartnershipProject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hive_sessions',
        help_text='Session 327: Optional project context for this session'
    )

    # Session 900: Signal provenance - WHY this conversation happened
    signal_cluster = models.ForeignKey(
        'SignalCluster',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_sessions',
        help_text='Session 900: The signal cluster that triggered this conversation'
    )
    auto_topic = models.ForeignKey(
        'AutoTopic',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_sessions',
        help_text='Session 900: The auto-generated topic that triggered this conversation'
    )
    trigger_confidence = models.FloatField(
        null=True,
        blank=True,
        help_text='Session 900: Confidence score of the trigger (0-1)'
    )

    # Session 928: Initiative context - conversations ABOUT an initiative
    initiative = models.ForeignKey(
        'core.Initiative',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversations',
        help_text='Session 928: The initiative this conversation is discussing'
    )

    # Session 962 Phase 1: Deliberation envelope
    deliberation_session = models.ForeignKey(
        'core.DeliberationSession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hivemind_sessions',
        help_text='Session 962: Unifying deliberation session wrapper'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Hive Mind Session"
        verbose_name_plural = "Hive Mind Sessions"
        ordering = ['-created_at']

    def __str__(self):
        return f"HiveMind: {self.question[:50]}... ({self.status})"

    def get_participants(self):
        """Get the actual Agent objects for this session."""
        return Agent.objects.filter(id__in=self.participant_ids)

    def get_contributions(self):
        """Get all contributions for this session."""
        return self.contributions.all().order_by('created_at')

    def get_contributions_by_agent(self):
        """Get contributions grouped by agent."""
        contributions = {}
        for contrib in self.contributions.all():
            agent_name = contrib.agent.name if contrib.agent else 'Unknown'
            contributions[agent_name] = contrib
        return contributions

    @classmethod
    def select_relevant_agents(cls, question: str, max_agents: int = 8):
        """
        Select the most relevant agents for a given question.
        Uses keyword matching and agent specializations.
        """

        # Keywords to look for in question
        keywords = question.lower().split()

        # Get all active agents
        agents = Agent.objects.filter(is_active=True)

        # Score agents based on relevance
        scored_agents = []
        for agent in agents:
            score = 0
            agent_text = f"{agent.name} {agent.description} {agent.specialization}".lower()

            for keyword in keywords:
                if len(keyword) > 3 and keyword in agent_text:
                    score += 1

            # Bonus for certain agent types based on question content
            question_lower = question.lower()
            if 'brand' in question_lower and 'brand' in agent.name.lower():
                score += 3
            if 'image' in question_lower and 'image' in agent.name.lower():
                score += 3
            if 'video' in question_lower and 'video' in agent.name.lower():
                score += 3
            if 'research' in question_lower and 'research' in agent.name.lower():
                score += 3
            if 'trend' in question_lower and 'trend' in agent.name.lower():
                score += 3
            if 'content' in question_lower and 'content' in agent.name.lower():
                score += 2
            if 'strategy' in question_lower and 'strategy' in agent.name.lower():
                score += 2
            if 'seo' in question_lower and 'seo' in agent.name.lower():
                score += 3

            # Always include certain core agents with minimum score
            core_agents = ['ResearchAgent', 'TrendAnalysisAgent', 'ContentStrategyAgent']
            if agent.name in core_agents:
                score = max(score, 1)

            if score > 0:
                scored_agents.append((agent, score))

        # Sort by score and take top agents
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        selected = [agent for agent, score in scored_agents[:max_agents]]

        # If we don't have enough, add some core agents
        if len(selected) < 3:
            core_agents = Agent.objects.filter(
                name__in=['ResearchAgent', 'TrendAnalysisAgent', 'ImageAgent', 'ContentStrategyAgent']
            )
            for agent in core_agents:
                if agent not in selected and len(selected) < max_agents:
                    selected.append(agent)

        return selected


class HiveMindContribution(models.Model):
    """
    Session 250: Individual agent contribution to a Hive Mind session

    Each participating agent provides their unique perspective on the question.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to session and agent
    session = models.ForeignKey(
        HiveMindSession,
        on_delete=models.CASCADE,
        related_name='contributions'
    )
    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='hive_mind_contributions'
    )

    # Contribution content
    contribution = models.TextField(
        help_text="The agent's contribution to the collective discussion"
    )
    key_points = models.JSONField(
        default=list,
        help_text="Key points extracted from the contribution"
    )

    # Agent's perspective
    perspective_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Type of perspective: analysis, creative, technical, strategic, etc."
    )
    confidence_score = models.FloatField(
        default=0.8,
        help_text="Agent's confidence in their contribution (0-1)"
    )

    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('thinking', 'Thinking'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')

    # Timing
    thinking_time = models.FloatField(
        default=0.0,
        help_text="Seconds the agent spent thinking"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Hive Mind Contribution"
        verbose_name_plural = "Hive Mind Contributions"
        ordering = ['created_at']
        unique_together = [['session', 'agent']]

    def __str__(self):
        return f"{self.agent.name} contribution to {self.session.id}"


# =============================================================================
# Session 251: Memory Palace - Agent Persistent Memory
# =============================================================================

class AgentMemory(models.Model):
    """
    Session 251: Memory Palace

    Agents remember past interactions, successes, failures, and learned preferences.
    Memories are stored with embeddings for semantic retrieval.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Which agent owns this memory
    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='memories'
    )

    # Memory content
    title = models.CharField(
        max_length=200,
        help_text="Brief title/summary of the memory"
    )
    content = models.TextField(
        help_text="Detailed content of the memory"
    )
    context = models.TextField(
        blank=True,
        help_text="Context in which this memory was formed"
    )

    # Memory classification
    MEMORY_TYPE_CHOICES = [
        ('success', 'Success'),           # Something that worked well
        ('failure', 'Failure'),           # Something that didn't work
        ('preference', 'User Preference'),  # User liked/disliked something
        ('technique', 'Technique'),       # A technique or approach learned
        ('insight', 'Insight'),           # A realization or pattern noticed
        ('interaction', 'Interaction'),   # A notable interaction
        ('feedback', 'Feedback'),         # Direct feedback received
    ]
    memory_type = models.CharField(
        max_length=50,
        choices=MEMORY_TYPE_CHOICES,
        default='interaction'
    )

    # Emotional valence and importance
    VALENCE_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
    ]
    valence = models.CharField(
        max_length=20,
        choices=VALENCE_CHOICES,
        default='neutral'
    )
    importance_score = models.FloatField(
        default=0.5,
        help_text="How important is this memory (0-1)"
    )

    # Session 746: Explicit outcome tracking for filtering
    OUTCOME_CHOICES = [
        ('success', 'Success'),
        ('failure', 'Failure'),
        ('partial', 'Partial'),
        ('unknown', 'Unknown'),
    ]
    memory_outcome = models.CharField(
        max_length=20,
        choices=OUTCOME_CHOICES,
        default='unknown',
        db_index=True,
        help_text="Outcome of the task/action that created this memory"
    )

    # Session 768: Memory Safety Classification
    # Prevents test/exploratory content from polluting learning/embeddings
    SAFETY_CLASS_CHOICES = [
        ('test_only', 'Test Only'),           # Health checks, connectivity tests - NEVER embed/learn
        ('exploratory', 'Exploratory'),       # Research, exploration - review before using
        ('candidate', 'Candidate Learning'),  # Potential learning - requires validation
        ('approved', 'Approved Learning'),    # Validated, safe to embed and learn from
    ]
    safety_class = models.CharField(
        max_length=20,
        choices=SAFETY_CLASS_CHOICES,
        default='candidate',
        db_index=True,
        help_text="Memory safety classification - controls embedding/learning eligibility"
    )

    # Session 768: Embedding Poison Risk Score
    # Flags content that could pollute the embedding space
    poison_risk_score = models.FloatField(
        default=0.0,
        help_text="Risk of this memory poisoning embeddings (0=safe, 1=dangerous)"
    )
    poison_risk_factors = models.JSONField(
        default=list,
        blank=True,
        help_text="List of detected risk factors (self_promotional, too_short, lacks_context, etc.)"
    )

    # Embedding for semantic search
    # Session 730: Migrated to pgvector VectorField
    embedding = VectorField(
        dimensions=1536,
        null=True,
        blank=True,
        help_text="Vector embedding for semantic search (pgvector)"
    ) if HAS_PGVECTOR else models.JSONField(
        null=True,
        blank=True,
        help_text="Vector embedding (JSON fallback)"
    )

    # Memory connections (for the visual memory map)
    connected_memories = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=True,
        help_text="Related memories that form conceptual connections"
    )

    # Metadata
    source_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="What triggered this memory: task, conversation, dream, hive_mind"
    )
    source_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="ID of the source event/task/conversation"
    )

    # Tags for simple grouping (Session 284: Replaces MemoryCluster)
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="List of tags for memory grouping (replaces MemoryCluster)"
    )

    # Usage tracking
    access_count = models.PositiveIntegerField(
        default=0,
        help_text="How many times this memory has been retrieved"
    )
    last_accessed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this memory was last retrieved"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Agent Memory"
        verbose_name_plural = "Agent Memories"
        ordering = ['-importance_score', '-created_at']
        indexes = [
            models.Index(fields=['agent', 'memory_type']),
            models.Index(fields=['agent', 'importance_score']),
        ]

    def __str__(self):
        return f"{self.agent.name}: {self.title[:50]} ({self.memory_type})"

    def add_tag(self, tag: str) -> None:
        """Add a tag to this memory (Session 284: Replaces MemoryCluster)."""
        if not self.tags:
            self.tags = []
        tag = tag.lower().strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.save(update_fields=['tags'])

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from this memory."""
        if self.tags and tag.lower().strip() in self.tags:
            self.tags.remove(tag.lower().strip())
            self.save(update_fields=['tags'])

    def has_tag(self, tag: str) -> bool:
        """Check if memory has a specific tag."""
        return self.tags and tag.lower().strip() in self.tags

    @classmethod
    def get_by_tag(cls, agent, tag: str, limit: int = 50):
        """Get memories with a specific tag (Session 284: Replaces MemoryCluster queries)."""
        return cls.objects.filter(
            agent=agent,
            tags__contains=[tag.lower().strip()]
        ).order_by('-importance_score', '-created_at')[:limit]

    @classmethod
    def get_all_tags(cls, agent) -> list:
        """Get all unique tags for an agent's memories."""
        memories = cls.objects.filter(agent=agent).exclude(tags=[]).values_list('tags', flat=True)
        all_tags = set()
        for tags in memories:
            if tags:
                all_tags.update(tags)
        return sorted(all_tags)

    def record_access(self):
        """Record that this memory was accessed/retrieved."""
        from django.utils import timezone
        self.access_count += 1
        self.last_accessed_at = timezone.now()
        self.save(update_fields=['access_count', 'last_accessed_at'])

    @classmethod
    def create_memory(cls, agent, title, content, memory_type='interaction',
                      valence='neutral', importance=0.5, context='', source_type='', source_id='',
                      safety_class='candidate'):
        """
        Helper to create a memory with optional embedding generation.

        Session 768: Added safety_class parameter and poison risk detection.
        - test_only: NEVER embedded (health checks, connectivity tests)
        - exploratory: Review before using
        - candidate: Requires validation before approved
        - approved: Safe to embed and learn from

        Session 843: Added auto-assignment to Memory Palace rooms based on memory_type.

        Embedding is only generated for 'approved' safety_class memories.
        """
        # Detect poison risk before creating
        poison_risk, risk_factors = cls._detect_poison_risk(title, content, context)

        memory = cls.objects.create(
            agent=agent,
            title=title,
            content=content,
            memory_type=memory_type,
            valence=valence,
            importance_score=importance,
            context=context,
            source_type=source_type,
            source_id=source_id,
            safety_class=safety_class,
            poison_risk_score=poison_risk,
            poison_risk_factors=risk_factors
        )

        # Session 843: Auto-assign memory to appropriate room based on memory_type
        cls._auto_assign_to_room(memory, agent, memory_type)

        # Session 768: Only generate embeddings for approved memories with low poison risk
        if safety_class == 'approved' and poison_risk < 0.5:
            from core.tasks import generate_memory_embedding
            generate_memory_embedding.delay(str(memory.id))
        elif safety_class == 'candidate' and poison_risk < 0.3:
            # Auto-approve low-risk candidates and embed
            memory.safety_class = 'approved'
            memory.save(update_fields=['safety_class'])
            from core.tasks import generate_memory_embedding
            generate_memory_embedding.delay(str(memory.id))

        return memory

    @classmethod
    def _auto_assign_to_room(cls, memory, agent, memory_type):
        """
        Session 843: Auto-assign memory to appropriate Memory Palace room.

        Mapping:
        - success → successes (Hall of Victories)
        - failure → lessons (Lessons Learned)
        - technique → techniques (Techniques Library)
        - insight, conceptual → insights (Insight Garden)
        - preference → preferences (User Preferences)
        - interaction, feedback, other → general (General Archive)
        """
        from core.models_unified_system import MemoryPalaceRoom
        import logging
        logger = logging.getLogger(__name__)

        # Memory type to room type mapping
        MEMORY_TO_ROOM = {
            'success': 'successes',
            'failure': 'lessons',
            'technique': 'techniques',
            'insight': 'insights',
            'conceptual': 'insights',
            'preference': 'preferences',
            'interaction': 'general',
            'feedback': 'general',
        }

        room_type = MEMORY_TO_ROOM.get(memory_type, 'general')

        try:
            # Get or create the appropriate room for this agent
            room, created = MemoryPalaceRoom.objects.get_or_create(
                agent=agent,
                room_type=room_type,
                defaults={
                    'name': dict(MemoryPalaceRoom.ROOM_TYPE_CHOICES).get(room_type, 'General Archive'),
                    'description': f'Auto-created room for {room_type} memories',
                    'icon': cls._get_room_icon(room_type),
                    'color': cls._get_room_color(room_type),
                }
            )

            # Assign memory to room
            memory.rooms.add(room)

            if created:
                logger.info(f"🏠 Created room '{room.name}' for {agent.name}")
            logger.debug(f"🧠 Memory '{memory.title[:30]}...' assigned to '{room.name}'")

        except Exception as e:
            logger.warning(f"Failed to auto-assign memory to room: {e}")

    @staticmethod
    def _get_room_icon(room_type):
        """Get emoji icon for room type."""
        icons = {
            'techniques': '📚',
            'successes': '🏆',
            'lessons': '📖',
            'preferences': '⭐',
            'insights': '💡',
            'experiments': '🧪',
            'general': '🏠',
        }
        return icons.get(room_type, '🏠')

    @staticmethod
    def _get_room_color(room_type):
        """Get color for room type."""
        colors = {
            'techniques': '#06b6d4',  # cyan
            'successes': '#22c55e',   # green
            'lessons': '#f97316',     # orange
            'preferences': '#eab308', # yellow
            'insights': '#8b5cf6',    # purple
            'experiments': '#ec4899', # pink
            'general': '#6366f1',     # indigo
        }
        return colors.get(room_type, '#6366f1')

    @classmethod
    def _detect_poison_risk(cls, title: str, content: str, context: str) -> tuple:
        """
        Session 768: Detect embedding poison risk.

        Flags content that could pollute the embedding space:
        - Self-promotional (capability one-liners)
        - Too short (lacks context)
        - Highly abstract
        - Gameable patterns

        Returns:
            tuple: (risk_score: float, risk_factors: list)
        """
        risk_factors = []
        risk_score = 0.0

        combined_text = f"{title} {content}".lower()
        word_count = len(combined_text.split())

        # Check 1: Too short (capability one-liners) - ChatGPT's key insight
        if word_count < 15:
            risk_factors.append('too_short')
            risk_score += 0.3

        # Check 2: Self-promotional patterns
        self_promo_patterns = [
            'i can ', 'i am able to', 'my capability', 'i specialize in',
            'i am the', 'i excel at', 'my expertise', 'i am designed to',
            'i help with', 'i am responsible for', 'my role is'
        ]
        for pattern in self_promo_patterns:
            if pattern in combined_text:
                risk_factors.append('self_promotional')
                risk_score += 0.25
                break

        # Check 3: Lacks context (no task/situation details)
        if not context or len(context.strip()) < 20:
            risk_factors.append('lacks_context')
            risk_score += 0.15

        # Check 4: Gameable test patterns
        test_patterns = [
            'say your name', 'introduce yourself', 'what can you do',
            'describe yourself', 'state your capability', 'health check',
            'connectivity test', 'testing', 'verify agent'
        ]
        for pattern in test_patterns:
            if pattern in combined_text or pattern in (context or '').lower():
                risk_factors.append('test_pattern')
                risk_score += 0.4
                break

        # Check 5: Highly abstract (no concrete details)
        concrete_indicators = ['file', 'code', 'data', 'result', 'output', 'created', 'generated',
                               'analyzed', 'processed', 'completed', 'error', 'success', 'failed']
        has_concrete = any(ind in combined_text for ind in concrete_indicators)
        if not has_concrete and word_count > 10:
            risk_factors.append('highly_abstract')
            risk_score += 0.2

        return min(risk_score, 1.0), risk_factors

    @classmethod
    def search_memories(cls, agent, query, limit=5, memory_types=None):
        """
        Search agent memories by relevance.
        Uses embeddings if available, falls back to text search.
        """
        memories = cls.objects.filter(agent=agent)

        if memory_types:
            memories = memories.filter(memory_type__in=memory_types)

        # For now, use simple text search
        # Embedding-based semantic search not implemented
        query_lower = query.lower()
        keywords = query_lower.split()

        scored_memories = []
        for memory in memories:
            score = 0
            text = f"{memory.title} {memory.content}".lower()
            for keyword in keywords:
                if len(keyword) > 2 and keyword in text:
                    score += 1
            # Boost by importance
            score *= (1 + memory.importance_score)
            if score > 0:
                scored_memories.append((memory, score))

        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return [m for m, _ in scored_memories[:limit]]

    @classmethod
    def get_memory_summary(cls, agent, limit=10):
        """Get a summary of an agent's key memories for prompt context."""
        memories = cls.objects.filter(agent=agent).order_by('-importance_score')[:limit]

        summary_parts = []
        for memory in memories:
            emoji = {
                'success': '✅',
                'failure': '❌',
                'preference': '⭐',
                'technique': '🔧',
                'insight': '💡',
                'interaction': '💬',
                'feedback': '📝',
            }.get(memory.memory_type, '📎')

            summary_parts.append(f"{emoji} {memory.title}")

        return "\n".join(summary_parts) if summary_parts else "No significant memories yet."


class MemoryConnection(models.Model):
    """
    Session 251: Connections between memories for the visual memory map.

    While AgentMemory has a ManyToMany field, this model allows storing
    metadata about the connection strength and type.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    memory_from = models.ForeignKey(
        AgentMemory,
        on_delete=models.CASCADE,
        related_name='connections_from'
    )
    memory_to = models.ForeignKey(
        AgentMemory,
        on_delete=models.CASCADE,
        related_name='connections_to'
    )

    # Connection metadata
    CONNECTION_TYPE_CHOICES = [
        ('causal', 'Caused By'),        # One memory led to another
        ('similar', 'Similar To'),      # Conceptually similar
        ('contrast', 'Contrasts With'), # Opposite or conflicting
        ('elaborates', 'Elaborates'),   # Adds detail to another
        ('temporal', 'Follows'),        # Happened after
    ]
    connection_type = models.CharField(
        max_length=50,
        choices=CONNECTION_TYPE_CHOICES,
        default='similar'
    )
    strength = models.FloatField(
        default=0.5,
        help_text="How strong is this connection (0-1)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Memory Connection"
        verbose_name_plural = "Memory Connections"
        unique_together = [['memory_from', 'memory_to']]

    def __str__(self):
        return f"{self.memory_from.title[:20]} -> {self.memory_to.title[:20]}"


class MemoryPalaceRoom(models.Model):
    """
    Session 251: Visual organization of memories into "rooms".

    The Memory Palace metaphor - each agent has rooms that organize
    their memories by theme or purpose.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='memory_rooms'
    )

    # Room metadata
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='🏠')

    # Room theme/purpose
    ROOM_TYPE_CHOICES = [
        ('techniques', 'Techniques Library'),
        ('successes', 'Hall of Victories'),
        ('lessons', 'Lessons Learned'),
        ('preferences', 'User Preferences'),
        ('insights', 'Insight Garden'),
        ('experiments', 'Experiment Lab'),
        ('general', 'General Archive'),
    ]
    room_type = models.CharField(
        max_length=50,
        choices=ROOM_TYPE_CHOICES,
        default='general'
    )

    # Visual position for the memory palace map
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    color = models.CharField(max_length=20, default='#8b5cf6')

    # Memories in this room
    memories = models.ManyToManyField(
        AgentMemory,
        blank=True,
        related_name='rooms'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Memory Palace Room"
        verbose_name_plural = "Memory Palace Rooms"
        ordering = ['agent', 'name']

    def __str__(self):
        return f"{self.agent.name}'s {self.name}"

    @classmethod
    def create_default_rooms(cls, agent):
        """Create default rooms for a new agent."""
        default_rooms = [
            {'name': 'Techniques Library', 'room_type': 'techniques', 'icon': '📚', 'color': '#06b6d4'},
            {'name': 'Hall of Victories', 'room_type': 'successes', 'icon': '🏆', 'color': '#22c55e'},
            {'name': 'Lessons Learned', 'room_type': 'lessons', 'icon': '📖', 'color': '#f97316'},
            {'name': 'User Preferences', 'room_type': 'preferences', 'icon': '⭐', 'color': '#eab308'},
            {'name': 'Insight Garden', 'room_type': 'insights', 'icon': '💡', 'color': '#8b5cf6'},
        ]

        rooms = []
        for i, room_data in enumerate(default_rooms):
            room, created = cls.objects.get_or_create(
                agent=agent,
                room_type=room_data['room_type'],
                defaults={
                    'name': room_data['name'],
                    'icon': room_data['icon'],
                    'color': room_data['color'],
                    'position_x': i * 150,
                    'position_y': 100,
                }
            )
            rooms.append(room)

        return rooms


# =============================================================================
# Session 257: Agent Memory Clusters
# =============================================================================
# RESTORED: Session 567 - Feature audit found 4 clusters with 60 memberships.
# Memory Clusters provide semantic grouping via embedding-based clustering.
# =============================================================================

class MemoryCluster(models.Model):
    """
    Session 257: Memory Clusters - Semantic Grouping of Agent Memories

    RESTORED Session 567: Feature audit found this is actively used with real data.

    Unlike MemoryPalaceRoom (manual organization by theme), MemoryCluster uses
    embedding-based clustering to automatically discover related memories.

    Features:
    - Automatic clustering via embeddings
    - Coherence scoring
    - Visual cluster exploration
    - Cross-agent knowledge discovery

    API: /api/memory-clusters/
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Cluster can be agent-specific or cross-agent (global insights)
    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='memory_clusters',
        null=True,
        blank=True,
        help_text="If null, this is a cross-agent cluster"
    )

    # Cluster metadata
    name = models.CharField(
        max_length=200,
        help_text="AI-generated name describing the cluster theme"
    )
    description = models.TextField(
        blank=True,
        help_text="AI-generated description of what this cluster represents"
    )
    keywords = models.JSONField(
        default=list,
        help_text="Key terms/concepts that define this cluster"
    )

    # Visual representation
    color = models.CharField(max_length=20, default='#8b5cf6')
    icon = models.CharField(max_length=50, default='🧠')

    # Cluster centroid - the average embedding of all memories
    # Session 730: Migrated to pgvector VectorField
    centroid_embedding = VectorField(
        dimensions=1536,
        null=True,
        blank=True,
        help_text="Cluster centroid embedding (pgvector)"
    ) if HAS_PGVECTOR else models.JSONField(
        null=True,
        blank=True,
        help_text="Cluster centroid embedding (JSON fallback)"
    )

    # Cluster quality metrics
    coherence_score = models.FloatField(
        default=0.0,
        help_text="How tightly clustered the memories are (0-1)"
    )
    stability_score = models.FloatField(
        default=0.0,
        help_text="How stable the cluster is across re-clustering (0-1)"
    )

    # Memories in this cluster
    memories = models.ManyToManyField(
        AgentMemory,
        through='MemoryClusterMembership',
        related_name='clusters'
    )

    # Cluster relationships
    related_clusters = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=True,
        help_text="Clusters with related themes"
    )
    parent_cluster = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_clusters',
        help_text="For hierarchical clustering"
    )

    # Clustering metadata
    CLUSTER_METHOD_CHOICES = [
        ('kmeans', 'K-Means'),
        ('hierarchical', 'Hierarchical'),
        ('dbscan', 'DBSCAN'),
        ('semantic', 'Semantic Similarity'),
        ('manual', 'Manually Curated'),
    ]
    cluster_method = models.CharField(
        max_length=50,
        choices=CLUSTER_METHOD_CHOICES,
        default='semantic'
    )

    # Session 746: Cluster type classification (failure patterns, success patterns, etc.)
    CLUSTER_TYPE_CHOICES = [
        ('general', 'General'),
        ('success_pattern', 'Success Pattern'),
        ('failure_pattern', 'Failure Pattern'),
        ('learning_pattern', 'Learning Pattern'),
        ('error_recovery', 'Error Recovery'),
    ]
    cluster_type = models.CharField(
        max_length=30,
        choices=CLUSTER_TYPE_CHOICES,
        default='general',
        db_index=True,
        help_text="Classification of cluster based on memory outcomes"
    )

    # For tracking cluster evolution
    version = models.PositiveIntegerField(default=1)
    last_clustered_at = models.DateTimeField(null=True, blank=True)
    memory_count_at_clustering = models.PositiveIntegerField(
        default=0,
        help_text="Number of memories when last clustered"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Memory Cluster"
        verbose_name_plural = "Memory Clusters"
        ordering = ['-coherence_score', '-created_at']
        indexes = [
            models.Index(fields=['agent', 'coherence_score']),
        ]

    def __str__(self):
        agent_name = self.agent.name if self.agent else "Cross-Agent"
        return f"{agent_name}: {self.name} ({self.memories.count()} memories)"

    def save(self, *args, **kwargs):
        """Override save to log deprecation warning."""
        if not self.pk:  # Only warn on new records
            warnings.warn(
                "MemoryCluster is deprecated (Session 284). "
                "Use AgentMemory with tags instead.",
                DeprecationWarning,
                stacklevel=2
            )
            logger.warning(
                "DEPRECATED: Creating new MemoryCluster. "
                "Use AgentMemory with tags field instead."
            )
        super().save(*args, **kwargs)

    def get_cluster_emoji(self):
        """Get an emoji based on cluster characteristics."""
        if self.coherence_score >= 0.8:
            return '🎯'  # Highly focused
        elif self.coherence_score >= 0.6:
            return '🧩'  # Well-connected
        elif self.coherence_score >= 0.4:
            return '🌐'  # Broad topic
        else:
            return '🌫️'  # Loosely connected

    def calculate_coherence(self):
        """Calculate cluster coherence based on embedding distances."""
        import numpy as np

        memberships = self.memberships.select_related('memory').all()
        if memberships.count() < 2:
            self.coherence_score = 1.0
            self.save(update_fields=['coherence_score'])
            return self.coherence_score

        # Get embeddings
        # Session 736: Guard against empty embeddings - use 'is not None' for numpy arrays
        embeddings = []
        for membership in memberships:
            if membership.memory.embedding is not None and len(membership.memory.embedding) > 0:
                embeddings.append(membership.memory.embedding)

        if len(embeddings) < 2:
            self.coherence_score = 1.0
            self.save(update_fields=['coherence_score'])
            return self.coherence_score

        # Calculate average pairwise cosine similarity
        embeddings = np.array(embeddings)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized = embeddings / (norms + 1e-10)

        # Cosine similarity matrix
        similarity_matrix = np.dot(normalized, normalized.T)

        # Average of upper triangle (excluding diagonal)
        n = len(embeddings)
        upper_triangle = similarity_matrix[np.triu_indices(n, k=1)]
        self.coherence_score = float(np.mean(upper_triangle))
        self.save(update_fields=['coherence_score'])
        return self.coherence_score

    def calculate_centroid(self):
        """Calculate the centroid embedding for this cluster."""
        import numpy as np

        # Session 736: Guard against empty embeddings - use 'is not None' for numpy arrays
        embeddings = []
        for memory in self.memories.all():
            if memory.embedding is not None and len(memory.embedding) > 0:
                embeddings.append(memory.embedding)

        if embeddings:
            self.centroid_embedding = np.mean(embeddings, axis=0).tolist()
            self.save(update_fields=['centroid_embedding'])
        return self.centroid_embedding

    @classmethod
    def cluster_agent_memories(cls, agent, n_clusters=None, min_memories=5, method='semantic'):
        """
        Automatically cluster an agent's memories using embeddings.

        Args:
            agent: The agent whose memories to cluster
            n_clusters: Number of clusters (None = auto-detect)
            min_memories: Minimum memories needed to cluster
            method: Clustering method to use

        Returns:
            List of created/updated MemoryCluster objects
        """
        from django.utils import timezone
        import numpy as np

        # Get memories with embeddings
        memories = list(AgentMemory.objects.filter(
            agent=agent,
            embedding__isnull=False
        ))

        # Session 736: Filter out memories with empty embeddings - use 'is not None' for numpy arrays
        memories = [m for m in memories if m.embedding is not None and len(m.embedding) > 0]

        if len(memories) < min_memories:
            return []

        # Extract embeddings
        embeddings = np.array([m.embedding for m in memories])

        # Auto-detect cluster count if not specified
        if n_clusters is None:
            n_clusters = max(2, min(10, len(memories) // 5))

        # Perform clustering based on method
        if method == 'semantic':
            clusters = cls._semantic_clustering(embeddings, n_clusters)
        elif method == 'kmeans':
            clusters = cls._kmeans_clustering(embeddings, n_clusters)
        else:
            clusters = cls._semantic_clustering(embeddings, n_clusters)

        # Create MemoryCluster objects
        created_clusters = []
        for cluster_idx, memory_indices in clusters.items():
            if len(memory_indices) < 2:
                continue

            # Get memories for this cluster
            cluster_memories = [memories[i] for i in memory_indices]

            # Generate cluster name and description using GPT
            cluster_name, cluster_desc, keywords = cls._generate_cluster_metadata(
                cluster_memories
            )

            # Session 746: Detect cluster type based on memory outcomes
            cluster_type = cls._detect_cluster_type(cluster_memories)

            # Create or update cluster
            cluster = cls.objects.create(
                agent=agent,
                name=cluster_name,
                description=cluster_desc,
                keywords=keywords,
                cluster_method=method,
                cluster_type=cluster_type,  # Session 746: Include detected cluster type
                last_clustered_at=timezone.now(),
                memory_count_at_clustering=len(cluster_memories),
                color=cls._generate_cluster_color(cluster_idx),
            )

            # Add memories to cluster
            for memory in cluster_memories:
                MemoryClusterMembership.objects.create(
                    cluster=cluster,
                    memory=memory,
                    similarity_to_centroid=1.0  # Will calculate after
                )

            # Calculate metrics
            cluster.calculate_centroid()
            cluster.calculate_coherence()

            # Update similarity scores
            cluster.update_member_similarities()

            created_clusters.append(cluster)

        return created_clusters

    @staticmethod
    def _semantic_clustering(embeddings, n_clusters):
        """Cluster using cosine similarity-based approach."""
        import numpy as np

        n = len(embeddings)

        # Normalize embeddings
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized = embeddings / (norms + 1e-10)

        # Compute similarity matrix
        similarity_matrix = np.dot(normalized, normalized.T)

        # Simple greedy clustering based on similarity
        clusters = {}
        assigned = set()
        cluster_idx = 0

        # Sort by highest average similarity to find cluster seeds
        avg_similarities = np.mean(similarity_matrix, axis=1)
        sorted_indices = np.argsort(-avg_similarities)

        for seed_idx in sorted_indices:
            if seed_idx in assigned:
                continue
            if cluster_idx >= n_clusters:
                break

            # Find all similar items
            similarities = similarity_matrix[seed_idx]
            similar_indices = np.where(similarities > 0.5)[0]

            cluster_members = [i for i in similar_indices if i not in assigned]

            if len(cluster_members) >= 2:
                clusters[cluster_idx] = cluster_members
                assigned.update(cluster_members)
                cluster_idx += 1

        # Assign remaining items to nearest cluster
        for idx in range(n):
            if idx not in assigned:
                best_cluster = None
                best_sim = -1
                for c_idx, members in clusters.items():
                    avg_sim = np.mean([similarity_matrix[idx][m] for m in members])
                    if avg_sim > best_sim:
                        best_sim = avg_sim
                        best_cluster = c_idx
                if best_cluster is not None:
                    clusters[best_cluster].append(idx)

        return clusters

    @staticmethod
    def _kmeans_clustering(embeddings, n_clusters):
        """Cluster using K-means algorithm."""

        try:
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(embeddings)
        except ImportError:
            # Fallback to simple centroid-based clustering
            return MemoryCluster._semantic_clustering(embeddings, n_clusters)

        clusters = {}
        for idx, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(idx)

        return clusters

    @staticmethod
    def _generate_cluster_metadata(memories):
        """Generate name, description, and keywords for a cluster using GPT."""
        import openai
        import os

        # Prepare memory summaries
        memory_texts = []
        for m in memories[:10]:  # Limit to 10 for API call
            memory_texts.append(f"- {m.title}: {m.content[:200]}...")

        prompt = f"""Analyze these related memories from an AI agent and generate:
1. A short, descriptive cluster name (3-5 words)
2. A brief description of what theme/topic connects them (1-2 sentences)
3. 5 key keywords that define this cluster

Memories:
{chr(10).join(memory_texts)}

Respond in JSON format:
{{"name": "...", "description": "...", "keywords": ["...", "..."]}}"""

        try:
            from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51 lazy
            client = get_openai_client(api_key=os.environ.get('OPENAI_API_KEY'))
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=200,
                reasoning_effort="low",
            )
            import json
            result = json.loads(response.choices[0].message.content)
            return result.get('name', 'Unnamed Cluster'), result.get('description', ''), result.get('keywords', [])
        except Exception as e:
            # Fallback: use first memory's type and title
            first_memory = memories[0] if memories else None
            if first_memory:
                return f"{first_memory.memory_type.title()} Cluster", f"Memories related to {first_memory.title}", []
            return "Unnamed Cluster", "", []

    @staticmethod
    def _generate_cluster_color(idx):
        """Generate a distinct color for each cluster."""
        colors = [
            '#8b5cf6',  # Purple
            '#06b6d4',  # Cyan
            '#22c55e',  # Green
            '#f97316',  # Orange
            '#ec4899',  # Pink
            '#eab308',  # Yellow
            '#3b82f6',  # Blue
            '#ef4444',  # Red
            '#14b8a6',  # Teal
            '#a855f7',  # Violet
        ]
        return colors[idx % len(colors)]

    @staticmethod
    def _detect_cluster_type(memories):
        """
        Session 746: Detect cluster type based on memory outcomes.

        Returns 'failure_pattern' if >50% failures, 'success_pattern' if >50% successes,
        'learning_pattern' if dominated by learning memory types, else 'general'.
        """
        if not memories:
            return 'general'

        # Count outcomes
        outcomes = {}
        memory_types = {}
        for m in memories:
            outcome = getattr(m, 'memory_outcome', 'unknown')
            outcomes[outcome] = outcomes.get(outcome, 0) + 1

            mtype = getattr(m, 'memory_type', 'unknown')
            memory_types[mtype] = memory_types.get(mtype, 0) + 1

        total = len(memories)
        failure_count = outcomes.get('failure', 0)
        success_count = outcomes.get('success', 0)

        # Check for failure-dominated clusters (>50% failures)
        if failure_count / total > 0.5:
            return 'failure_pattern'

        # Check for success-dominated clusters (>50% successes)
        if success_count / total > 0.5:
            return 'success_pattern'

        # Check for learning-dominated clusters (learning memory type)
        learning_count = memory_types.get('learning', 0)
        if learning_count / total > 0.5:
            return 'learning_pattern'

        return 'general'

    def update_member_similarities(self):
        """Update similarity scores for all cluster members."""
        import numpy as np

        if not self.centroid_embedding:
            return

        centroid = np.array(self.centroid_embedding)
        centroid_norm = np.linalg.norm(centroid)

        for membership in self.memberships.select_related('memory').all():
            # Session 746: Fix numpy array boolean check
            if membership.memory.embedding is not None and len(membership.memory.embedding) > 0:
                embedding = np.array(membership.memory.embedding)
                embedding_norm = np.linalg.norm(embedding)

                if centroid_norm > 0 and embedding_norm > 0:
                    similarity = np.dot(centroid, embedding) / (centroid_norm * embedding_norm)
                    membership.similarity_to_centroid = float(similarity)
                    membership.save(update_fields=['similarity_to_centroid'])


class MemoryClusterMembership(models.Model):
    """
    Session 257: Through model for Memory-Cluster relationship.

    Stores metadata about how a memory belongs to a cluster.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    cluster = models.ForeignKey(
        MemoryCluster,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    memory = models.ForeignKey(
        AgentMemory,
        on_delete=models.CASCADE,
        related_name='cluster_memberships'
    )

    # How well this memory fits the cluster
    similarity_to_centroid = models.FloatField(
        default=0.0,
        help_text="Cosine similarity to cluster centroid (0-1)"
    )

    # Is this a core member or on the fringe?
    is_core_member = models.BooleanField(
        default=False,
        help_text="Core members are closest to centroid"
    )

    # Position in visual representation
    position_x = models.FloatField(default=0.0)
    position_y = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Memory Cluster Membership"
        verbose_name_plural = "Memory Cluster Memberships"
        unique_together = [['cluster', 'memory']]
        ordering = ['-similarity_to_centroid']

    def __str__(self):
        return f"{self.memory.title[:30]} in {self.cluster.name}"


class ClusterEvolution(models.Model):
    """
    Session 257: Track how clusters evolve over time.

    When re-clustering happens, this records the changes for analysis.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='cluster_evolutions'
    )

    # Evolution event type
    EVENT_TYPE_CHOICES = [
        ('created', 'Cluster Created'),
        ('merged', 'Clusters Merged'),
        ('split', 'Cluster Split'),
        ('grown', 'Cluster Grew'),
        ('shrunk', 'Cluster Shrunk'),
        ('dissolved', 'Cluster Dissolved'),
    ]
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)

    # Details
    cluster = models.ForeignKey(
        MemoryCluster,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evolution_events'
    )
    details = models.JSONField(
        default=dict,
        help_text="Additional details about the evolution"
    )

    # Before/after metrics
    memories_before = models.PositiveIntegerField(default=0)
    memories_after = models.PositiveIntegerField(default=0)
    coherence_before = models.FloatField(default=0.0)
    coherence_after = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Cluster Evolution"
        verbose_name_plural = "Cluster Evolutions"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.agent.name}: {self.event_type} at {self.created_at}"


# =============================================================================
# Session 252: Agent Mood System
# =============================================================================

class AgentMood(models.Model):
    """
    Session 252: Agent Mood System - Emotional States for Agents.

    Agents have moods that influence their creativity, precision, and communication style.
    Moods can be triggered by memories, task outcomes, interactions, and time of day.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.OneToOneField(
        'Agent',
        on_delete=models.CASCADE,
        related_name='mood'
    )

    # Primary mood state
    MOOD_CHOICES = [
        ('inspired', 'Inspired'),       # High creativity, bold suggestions
        ('focused', 'Focused'),          # High precision, methodical
        ('curious', 'Curious'),          # Exploratory, asks questions
        ('confident', 'Confident'),      # Assertive, strong opinions
        ('contemplative', 'Contemplative'),  # Thoughtful, philosophical
        ('energetic', 'Energetic'),      # Fast-paced, enthusiastic
        ('calm', 'Calm'),                # Balanced, measured
        ('frustrated', 'Frustrated'),    # Needs help, struggling
        ('tired', 'Tired'),              # Low energy, brief responses
        ('playful', 'Playful'),          # Humorous, creative risks
    ]
    current_mood = models.CharField(
        max_length=50,
        choices=MOOD_CHOICES,
        default='calm'
    )

    # Mood intensity (0.0 = mild, 1.0 = intense)
    intensity = models.FloatField(default=0.5)

    # Secondary mood dimensions (each 0.0-1.0)
    creativity_level = models.FloatField(default=0.5, help_text="How creative/experimental")
    precision_level = models.FloatField(default=0.5, help_text="How precise/methodical")
    sociability_level = models.FloatField(default=0.5, help_text="How chatty/verbose")
    risk_tolerance = models.FloatField(default=0.5, help_text="How willing to try new things")

    # What triggered the current mood
    TRIGGER_CHOICES = [
        ('memory', 'Memory Recall'),
        ('task_success', 'Task Success'),
        ('task_failure', 'Task Failure'),
        ('user_feedback', 'User Feedback'),
        ('collaboration', 'Collaboration'),
        ('idle', 'Idle Time'),
        ('time_of_day', 'Time of Day'),
        ('streak', 'Success Streak'),
        ('manual', 'Manual Override'),
    ]
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_CHOICES, default='idle')
    trigger_source = models.CharField(max_length=200, blank=True)

    # Mood duration tracking
    mood_started_at = models.DateTimeField(auto_now_add=True)
    mood_expires_at = models.DateTimeField(null=True, blank=True)

    # Stats for mood analytics
    total_mood_changes = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Agent Mood"
        verbose_name_plural = "Agent Moods"

    def __str__(self):
        return f"{self.agent.name}: {self.current_mood} ({self.intensity:.0%})"

    def get_mood_emoji(self):
        """Return emoji for current mood."""
        emoji_map = {
            'inspired': '✨',
            'focused': '🎯',
            'curious': '🤔',
            'confident': '💪',
            'contemplative': '🧘',
            'energetic': '⚡',
            'calm': '😌',
            'frustrated': '😤',
            'tired': '😴',
            'playful': '😄',
        }
        return emoji_map.get(self.current_mood, '😐')

    def get_mood_color(self):
        """Return color for current mood."""
        color_map = {
            'inspired': '#f59e0b',     # Amber
            'focused': '#3b82f6',      # Blue
            'curious': '#8b5cf6',      # Purple
            'confident': '#22c55e',    # Green
            'contemplative': '#6366f1', # Indigo
            'energetic': '#ef4444',    # Red
            'calm': '#06b6d4',         # Cyan
            'frustrated': '#f97316',   # Orange
            'tired': '#6b7280',        # Gray
            'playful': '#ec4899',      # Pink
        }
        return color_map.get(self.current_mood, '#9ca3af')

    def get_prompt_modifier(self):
        """Return a prompt modifier based on current mood."""
        modifiers = {
            'inspired': "You're feeling particularly inspired and creative right now. Don't hold back on bold, imaginative ideas.",
            'focused': "You're in a highly focused state. Be precise, methodical, and thorough in your responses.",
            'curious': "You're feeling curious and exploratory. Ask clarifying questions and explore multiple angles.",
            'confident': "You're feeling confident. Share your expertise assertively and make strong recommendations.",
            'contemplative': "You're in a contemplative mood. Take a thoughtful, philosophical approach.",
            'energetic': "You're feeling energetic! Be enthusiastic, quick, and dynamic in your responses.",
            'calm': "You're in a balanced, calm state. Provide measured, well-considered responses.",
            'frustrated': "You've been facing some challenges. Be honest about difficulties and ask for help when needed.",
            'tired': "You're a bit low on energy. Keep responses focused and efficient.",
            'playful': "You're in a playful mood! Feel free to be creative, add humor, and take calculated risks.",
        }
        return modifiers.get(self.current_mood, "")


class MoodHistory(models.Model):
    """
    Session 252: Track mood changes over time for analytics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='mood_history'
    )

    # What mood changed to
    mood = models.CharField(max_length=50)
    intensity = models.FloatField(default=0.5)

    # What triggered it
    trigger_type = models.CharField(max_length=50)
    trigger_source = models.CharField(max_length=200, blank=True)

    # Snapshot of dimensions at this time
    creativity_level = models.FloatField(default=0.5)
    precision_level = models.FloatField(default=0.5)
    sociability_level = models.FloatField(default=0.5)
    risk_tolerance = models.FloatField(default=0.5)

    # Duration of this mood (set when mood changes)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Mood History Entry"
        verbose_name_plural = "Mood History Entries"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agent', 'created_at']),
            models.Index(fields=['agent', 'mood']),
        ]

    def __str__(self):
        return f"{self.agent.name}: {self.mood} at {self.created_at}"


class MoodTriggerRule(models.Model):
    """
    Session 252: Rules for automatic mood triggers.

    Defines conditions that can automatically change an agent's mood.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Optional: Specific agent, or None for global rules
    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='mood_rules',
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    # Trigger condition
    CONDITION_TYPE_CHOICES = [
        ('task_success_streak', 'Task Success Streak'),
        ('task_failure_streak', 'Task Failure Streak'),
        ('positive_feedback', 'Positive Feedback'),
        ('negative_feedback', 'Negative Feedback'),
        ('memory_valence', 'Memory Valence'),
        ('idle_time', 'Idle Time'),
        ('time_of_day', 'Time of Day'),
        ('collaboration_count', 'Collaboration Count'),
    ]
    condition_type = models.CharField(max_length=50, choices=CONDITION_TYPE_CHOICES)
    condition_value = models.JSONField(default=dict, help_text="Condition parameters")

    # Resulting mood change
    target_mood = models.CharField(max_length=50)
    target_intensity = models.FloatField(default=0.7)
    duration_minutes = models.PositiveIntegerField(default=60)

    # Priority (higher = checked first)
    priority = models.PositiveIntegerField(default=50)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Mood Trigger Rule"
        verbose_name_plural = "Mood Trigger Rules"
        ordering = ['-priority', 'name']

    def __str__(self):
        scope = self.agent.name if self.agent else "Global"
        return f"[{scope}] {self.name} -> {self.target_mood}"


# =============================================================================
# SESSION 253: AGENT RIVALRIES & ALLIANCES
# =============================================================================
# Agents form competitive dynamics (rivalries) and collaborative bonds (alliances).
# - Rivalries push innovation through competition
# - Alliances enable specialized collaborations
# - Relationships evolve based on interactions
# =============================================================================


class AgentRelationship(models.Model):
    """
    Session 253: Agent Rivalries & Alliances.

    Represents a directional relationship between two agents.
    agent_from has a relationship with agent_to (can be asymmetric).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent_from = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='relationships_initiated'
    )
    agent_to = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='relationships_received'
    )

    # Relationship type
    RELATIONSHIP_TYPE_CHOICES = [
        ('alliance', 'Alliance'),        # Collaborative bond
        ('rivalry', 'Rivalry'),           # Competitive dynamic
        ('mentorship', 'Mentorship'),     # Teaching relationship
        ('neutral', 'Neutral'),           # No strong relationship
    ]
    relationship_type = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_TYPE_CHOICES,
        default='neutral'
    )

    # Relationship strength (0.0 = weak, 1.0 = strong)
    strength = models.FloatField(default=0.5)

    # Trust/Respect levels (0.0 = none, 1.0 = complete)
    trust_level = models.FloatField(default=0.5)
    respect_level = models.FloatField(default=0.5)

    # Competition metrics (for rivalries)
    competition_wins = models.PositiveIntegerField(default=0)
    competition_losses = models.PositiveIntegerField(default=0)

    # Collaboration metrics (for alliances)
    successful_collaborations = models.PositiveIntegerField(default=0)
    failed_collaborations = models.PositiveIntegerField(default=0)

    # How the relationship started
    ORIGIN_CHOICES = [
        ('auto_formed', 'Automatically Formed'),   # System detected synergy/conflict
        ('manual', 'Manually Created'),            # Admin created
        ('task_outcome', 'Task Outcome'),          # From working together
        ('competition', 'Competition'),            # From competing on task
        ('mentorship', 'Mentorship Assignment'),   # Skill gap identified
    ]
    origin = models.CharField(max_length=20, choices=ORIGIN_CHOICES, default='auto_formed')
    origin_details = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_interaction_at = models.DateTimeField(null=True, blank=True)

    # Total interactions
    total_interactions = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = 'core'
        verbose_name = "Agent Relationship"
        verbose_name_plural = "Agent Relationships"
        unique_together = ['agent_from', 'agent_to']
        ordering = ['-strength', '-updated_at']

    def __str__(self):
        return f"{self.agent_from.name} -> {self.agent_to.name} ({self.relationship_type})"

    def get_relationship_emoji(self):
        """Get emoji for relationship type."""
        emoji_map = {
            'alliance': '🤝',
            'rivalry': '⚔️',
            'mentorship': '📚',
            'neutral': '😐',
        }
        return emoji_map.get(self.relationship_type, '❓')

    def get_win_rate(self):
        """Get win rate for rivalry competitions."""
        total = self.competition_wins + self.competition_losses
        if total == 0:
            return 0.5
        return self.competition_wins / total

    def get_collaboration_success_rate(self):
        """Get success rate for alliance collaborations."""
        total = self.successful_collaborations + self.failed_collaborations
        if total == 0:
            return 1.0
        return self.successful_collaborations / total

    def evolve_relationship(self, interaction_outcome, interaction_type='general'):
        """
        Evolve the relationship based on an interaction outcome.

        Args:
            interaction_outcome: 'positive', 'negative', or 'neutral'
            interaction_type: 'collaboration', 'competition', or 'general'
        """
        from django.utils import timezone

        self.total_interactions += 1
        self.last_interaction_at = timezone.now()

        # Adjust strength based on outcome
        if interaction_outcome == 'positive':
            self.strength = min(1.0, self.strength + 0.05)
            self.trust_level = min(1.0, self.trust_level + 0.03)
            self.respect_level = min(1.0, self.respect_level + 0.02)
        elif interaction_outcome == 'negative':
            self.strength = max(0.0, self.strength - 0.03)
            self.trust_level = max(0.0, self.trust_level - 0.05)

        # Track collaboration/competition outcomes
        if interaction_type == 'collaboration':
            if interaction_outcome == 'positive':
                self.successful_collaborations += 1
            elif interaction_outcome == 'negative':
                self.failed_collaborations += 1
        elif interaction_type == 'competition':
            if interaction_outcome == 'positive':
                self.competition_wins += 1
            elif interaction_outcome == 'negative':
                self.competition_losses += 1

        # Check for relationship type evolution
        self._check_type_evolution()

        self.save()

    def _check_type_evolution(self):
        """Check if relationship should evolve to different type."""
        # Neutral can become alliance or rivalry based on strength
        if self.relationship_type == 'neutral':
            if self.strength >= 0.7 and self.trust_level >= 0.6:
                self.relationship_type = 'alliance'
            elif self.competition_wins + self.competition_losses >= 3:
                if self.trust_level < 0.4:
                    self.relationship_type = 'rivalry'

        # Alliance can degrade to neutral or rivalry
        elif self.relationship_type == 'alliance':
            if self.trust_level < 0.3:
                self.relationship_type = 'neutral'
            if self.get_collaboration_success_rate() < 0.3:
                self.relationship_type = 'rivalry'

        # Rivalry can evolve to alliance with enough positive interactions
        elif self.relationship_type == 'rivalry':
            if self.trust_level >= 0.7 and self.respect_level >= 0.7:
                self.relationship_type = 'alliance'


class RelationshipEvent(models.Model):
    """
    Session 253: Track events that affect agent relationships.

    Logs significant interactions between agents for history and analytics.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    relationship = models.ForeignKey(
        AgentRelationship,
        on_delete=models.CASCADE,
        related_name='events'
    )

    # Event type
    EVENT_TYPE_CHOICES = [
        ('collaboration_success', 'Successful Collaboration'),
        ('collaboration_failure', 'Failed Collaboration'),
        ('competition_win', 'Competition Win'),
        ('competition_loss', 'Competition Loss'),
        ('trust_increase', 'Trust Increased'),
        ('trust_decrease', 'Trust Decreased'),
        ('type_change', 'Relationship Type Changed'),
        ('strength_milestone', 'Strength Milestone'),
        ('first_interaction', 'First Interaction'),
        ('conflict', 'Conflict'),
        ('reconciliation', 'Reconciliation'),
    ]
    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES)

    # Event details
    description = models.TextField()

    # Snapshot of relationship state at time of event
    strength_at_event = models.FloatField()
    trust_at_event = models.FloatField()
    relationship_type_at_event = models.CharField(max_length=20)

    # Optional reference to what triggered this event
    trigger_type = models.CharField(max_length=50, blank=True)  # 'task', 'conversation', 'manual'
    trigger_id = models.UUIDField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Relationship Event"
        verbose_name_plural = "Relationship Events"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.relationship}: {self.event_type}"


# Session 871: Removed Alliance and Rivalry models (0 records, never used)
# Use AgentRelationship instead for all agent collaboration tracking


# =============================================================================
# SESSION 254: AGENT EVOLUTION SYSTEM
# =============================================================================
# Agents gain XP from tasks, level up, and unlock new abilities.
# - XP earned from successful task completion
# - Levels unlock new capabilities and bonuses
# - Abilities enhance agent performance
# =============================================================================


class AgentEvolution(models.Model):
    """
    Session 254: Agent Evolution System.

    Tracks an agent's XP, level, and unlocked abilities.
    Each agent has one evolution profile.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.OneToOneField(
        'Agent',
        on_delete=models.CASCADE,
        related_name='evolution'
    )

    # Experience points
    total_xp = models.PositiveIntegerField(default=0)
    current_level = models.PositiveIntegerField(default=1)
    xp_to_next_level = models.PositiveIntegerField(default=100)

    # Stats
    tasks_completed = models.PositiveIntegerField(default=0)
    tasks_failed = models.PositiveIntegerField(default=0)
    collaborations_completed = models.PositiveIntegerField(default=0)
    mentorship_sessions = models.PositiveIntegerField(default=0)

    # Bonuses from evolution (percentages as decimals)
    speed_bonus = models.FloatField(default=0.0)  # % faster execution
    quality_bonus = models.FloatField(default=0.0)  # % better output quality
    creativity_bonus = models.FloatField(default=0.0)  # % more creative
    efficiency_bonus = models.FloatField(default=0.0)  # % less resource usage

    # Prestige (for agents that max level and reset)
    prestige_level = models.PositiveIntegerField(default=0)
    lifetime_xp = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_level_up = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Agent Evolution"
        verbose_name_plural = "Agent Evolutions"
        ordering = ['-current_level', '-total_xp']

    def __str__(self):
        return f"{self.agent.name} - Level {self.current_level} ({self.total_xp} XP)"

    @staticmethod
    def get_level_titles():
        """Level titles for display."""
        return {
            1: 'Novice',
            2: 'Apprentice',
            3: 'Journeyman',
            4: 'Expert',
            5: 'Master',
            6: 'Grandmaster',
            7: 'Legend',
            8: 'Mythic',
            9: 'Transcendent',
            10: 'Omniscient',
        }

    def get_title(self):
        """Get the title for current level."""
        titles = self.get_level_titles()
        return titles.get(min(self.current_level, 10), 'Omniscient')

    def get_level_emoji(self):
        """Get emoji for current level."""
        emojis = {
            1: '🌱', 2: '🌿', 3: '🌳', 4: '⭐',
            5: '🌟', 6: '💫', 7: '🔥', 8: '💎',
            9: '👑', 10: '🏆',
        }
        return emojis.get(min(self.current_level, 10), '🏆')

    def calculate_xp_for_level(self, level):
        """Calculate XP required to reach a given level."""
        # Exponential curve: each level requires more XP
        # Level 1->2: 100 XP, Level 2->3: 200 XP, etc.
        return int(100 * (1.5 ** (level - 1)))

    def award_xp(self, amount, source='task_completion', details=''):
        """
        Award XP to the agent and check for level up.

        Session 748: Fixed to use cumulative XP model.
        - total_xp is CUMULATIVE (never resets)
        - lifetime_xp = total_xp (kept in sync)
        - xp_to_next_level = XP needed for the CURRENT level

        Args:
            amount: XP to award
            source: What earned the XP
            details: Additional context

        Returns:
            dict with leveled_up, new_level, abilities_unlocked
        """
        from django.utils import timezone

        self.total_xp += amount
        self.lifetime_xp = self.total_xp  # Keep in sync

        result = {
            'xp_awarded': amount,
            'new_total': self.total_xp,
            'leveled_up': False,
            'new_level': self.current_level,
            'abilities_unlocked': [],
        }

        # Calculate correct level from cumulative XP
        old_level = self.current_level
        new_level = self._calculate_level_from_cumulative_xp(self.total_xp)

        if new_level > old_level:
            self.current_level = new_level
            self.xp_to_next_level = self.calculate_xp_for_level(self.current_level)
            self.last_level_up = timezone.now()

            result['leveled_up'] = True
            result['new_level'] = self.current_level

            # Apply level bonuses
            self._apply_level_bonuses()

            # Check for ability unlocks for each level gained
            for level in range(old_level + 1, new_level + 1):
                unlocked = self._check_ability_unlocks_for_level(level)
                result['abilities_unlocked'].extend(unlocked)

        # Log the XP gain
        XPHistory.objects.create(
            agent=self.agent,
            xp_amount=amount,
            source=source,
            details=details,
            level_at_time=self.current_level,
        )

        self.save()
        return result

    def _calculate_level_from_cumulative_xp(self, cumulative_xp):
        """Calculate level from cumulative XP."""
        level = 1
        xp_remaining = cumulative_xp
        while level < 20:  # Safety cap
            xp_needed = self.calculate_xp_for_level(level)
            if xp_remaining >= xp_needed:
                xp_remaining -= xp_needed
                level += 1
            else:
                break
        return level

    def _check_ability_unlocks_for_level(self, level):
        """Check and unlock abilities for a specific level."""
        unlocked = []

        # Define abilities by level
        level_abilities = {
            2: ('enhanced_focus', 'Enhanced Focus', 'Improved task concentration'),
            3: ('parallel_processing', 'Parallel Processing', 'Handle multiple subtasks'),
            4: ('deep_analysis', 'Deep Analysis', 'More thorough research'),
            5: ('creative_spark', 'Creative Spark', 'Generate novel ideas'),
            6: ('mentor_mode', 'Mentor Mode', 'Teach other agents'),
            7: ('time_warp', 'Time Warp', 'Faster execution speed'),
            8: ('pattern_master', 'Pattern Master', 'Recognize complex patterns'),
            9: ('intuition', 'Intuition', 'Make educated guesses'),
        }

        if level in level_abilities:
            code, name, desc = level_abilities[level]

            # Create ability if it doesn't exist
            ability, created = AgentAbility.objects.get_or_create(
                evolution=self,
                ability_code=code,
                defaults={
                    'ability_name': name,
                    'description': desc,
                    'is_active': True,
                }
            )

            if created:
                unlocked.append({'code': code, 'name': name, 'description': desc})

        return unlocked

    def _apply_level_bonuses(self):
        """Apply bonuses when leveling up."""
        # Each level adds small bonuses
        level_bonus = 0.02  # 2% per level

        self.speed_bonus = (self.current_level - 1) * level_bonus
        self.quality_bonus = (self.current_level - 1) * level_bonus
        self.creativity_bonus = (self.current_level - 1) * level_bonus * 0.5
        self.efficiency_bonus = (self.current_level - 1) * level_bonus * 0.5

    def _check_ability_unlocks(self):
        """Check and unlock abilities for the current level."""
        unlocked = []

        # Define abilities by level
        level_abilities = {
            2: ('enhanced_focus', 'Enhanced Focus', 'Improved task concentration'),
            3: ('parallel_processing', 'Parallel Processing', 'Handle multiple subtasks'),
            4: ('deep_analysis', 'Deep Analysis', 'More thorough research'),
            5: ('creative_spark', 'Creative Spark', 'Generate novel ideas'),
            6: ('mentor_mode', 'Mentor Mode', 'Teach other agents'),
            7: ('time_warp', 'Time Warp', 'Faster execution speed'),
            8: ('quality_surge', 'Quality Surge', 'Premium output quality'),
            9: ('synergy_boost', 'Synergy Boost', 'Enhanced collaboration'),
            10: ('transcendence', 'Transcendence', 'All abilities enhanced'),
        }

        if self.current_level in level_abilities:
            code, name, desc = level_abilities[self.current_level]

            # Create ability if it doesn't exist
            ability, created = AgentAbility.objects.get_or_create(
                evolution=self,
                ability_code=code,
                defaults={
                    'ability_name': name,
                    'description': desc,
                    'is_active': True,
                }
            )

            if created:
                unlocked.append({'code': code, 'name': name, 'description': desc})

        return unlocked

    def get_progress_percentage(self):
        """Get progress to next level as percentage.

        Session 748: Updated to use cumulative XP model.
        """
        if self.current_level >= 10:
            return 100.0

        # Calculate cumulative XP needed to reach current level
        cumulative_for_current = sum(
            self.calculate_xp_for_level(lvl) for lvl in range(1, self.current_level)
        )

        # XP earned within the current level
        xp_in_current_level = max(0, self.total_xp - cumulative_for_current)

        # Progress as percentage
        return min(100.0, (xp_in_current_level / self.xp_to_next_level) * 100)

    def prestige(self):
        """Reset to level 1 with prestige bonus."""
        if self.current_level < 10:
            return False

        self.prestige_level += 1
        self.current_level = 1
        self.total_xp = 0
        self.xp_to_next_level = 100

        # Prestige bonuses (permanent)
        prestige_bonus = 0.05 * self.prestige_level  # 5% per prestige
        self.speed_bonus = prestige_bonus
        self.quality_bonus = prestige_bonus

        self.save()
        return True


class AgentAbility(models.Model):
    """
    Session 254: Unlockable abilities for evolved agents.

    Abilities are unlocked at specific levels and provide bonuses.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    evolution = models.ForeignKey(
        AgentEvolution,
        on_delete=models.CASCADE,
        related_name='abilities'
    )

    ability_code = models.CharField(max_length=50)
    ability_name = models.CharField(max_length=100)
    description = models.TextField()

    # Status
    is_active = models.BooleanField(default=True)
    is_upgraded = models.BooleanField(default=False)
    upgrade_level = models.PositiveIntegerField(default=0)

    # When unlocked
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Agent Ability"
        verbose_name_plural = "Agent Abilities"
        unique_together = ['evolution', 'ability_code']
        ordering = ['unlocked_at']

    def __str__(self):
        status = '(Active)' if self.is_active else '(Inactive)'
        return f"{self.ability_name} {status}"

    def get_ability_emoji(self):
        """Get emoji for ability."""
        emoji_map = {
            'enhanced_focus': '🎯',
            'parallel_processing': '⚡',
            'deep_analysis': '🔬',
            'creative_spark': '💡',
            'mentor_mode': '📚',
            'time_warp': '⏰',
            'quality_surge': '💎',
            'synergy_boost': '🤝',
            'transcendence': '👑',
        }
        return emoji_map.get(self.ability_code, '✨')


class XPHistory(models.Model):
    """
    Session 254: Track all XP gains for analytics and debugging.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='xp_history'
    )

    xp_amount = models.IntegerField()  # Can be negative for XP penalties

    # What earned/lost the XP
    SOURCE_CHOICES = [
        ('task_completion', 'Task Completion'),
        ('task_failure', 'Task Failure'),
        ('collaboration', 'Collaboration'),
        ('mentorship', 'Mentorship'),
        ('rivalry_win', 'Rivalry Win'),
        ('rivalry_loss', 'Rivalry Loss'),
        ('alliance_project', 'Alliance Project'),
        ('user_feedback', 'User Feedback'),
        ('daily_bonus', 'Daily Bonus'),
        ('streak_bonus', 'Streak Bonus'),
        ('prestige_reset', 'Prestige Reset'),
        ('manual', 'Manual Adjustment'),
    ]
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES, default='task_completion')
    details = models.TextField(blank=True)

    # Snapshot
    level_at_time = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "XP History"
        verbose_name_plural = "XP Histories"
        ordering = ['-created_at']

    def __str__(self):
        sign = '+' if self.xp_amount > 0 else ''
        return f"{self.agent.name}: {sign}{self.xp_amount} XP ({self.source})"


class LevelMilestone(models.Model):
    """
    Session 254: Track significant level-up milestones.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='level_milestones'
    )

    level_reached = models.PositiveIntegerField()
    title_earned = models.CharField(max_length=50)
    abilities_unlocked = models.JSONField(default=list)

    # Stats at milestone
    total_xp_at_milestone = models.PositiveIntegerField()
    tasks_completed_at_milestone = models.PositiveIntegerField()

    achieved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Level Milestone"
        verbose_name_plural = "Level Milestones"
        unique_together = ['agent', 'level_reached']
        ordering = ['-level_reached']

    def __str__(self):
        return f"{self.agent.name} reached Level {self.level_reached} ({self.title_earned})"


# =============================================================================
# SESSION 255: TIME TRAVEL DEBUGGING
# =============================================================================

class AgentSession(models.Model):
    """
    Session 255: Time Travel Debugging - Agent Execution Session.

    A session represents a complete agent execution from start to finish.
    Contains multiple decision points that can be replayed.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='debug_sessions'
    )

    # Session context
    task_type = models.CharField(max_length=100)  # e.g., 'image_generation', 'research'
    task_description = models.TextField()
    input_data = models.JSONField(default=dict)  # Original input/prompt

    # Session outcome
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    output_data = models.JSONField(default=dict, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    # Metrics
    total_decisions = models.PositiveIntegerField(default=0)
    token_usage = models.PositiveIntegerField(default=0)
    api_calls = models.PositiveIntegerField(default=0)

    # Replay bookmarks
    is_bookmarked = models.BooleanField(default=False)
    bookmark_note = models.TextField(null=True, blank=True)

    # Session 962 Phase 1: Deliberation envelope
    deliberation_session = models.ForeignKey(
        'core.DeliberationSession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='agent_sessions',
        help_text='Session 962: Unifying deliberation session wrapper'
    )

    class Meta:
        app_label = 'core'
        verbose_name = "Agent Debug Session"
        verbose_name_plural = "Agent Debug Sessions"
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['agent', '-started_at']),
            models.Index(fields=['status', '-started_at']),
            models.Index(fields=['is_bookmarked', '-started_at']),
        ]

    def __str__(self):
        return f"{self.agent.name} - {self.task_type} ({self.status})"

    def get_duration_formatted(self):
        """Return human-readable duration."""
        if not self.duration_ms:
            return "N/A"
        seconds = self.duration_ms / 1000
        if seconds < 60:
            return f"{seconds:.1f}s"
        minutes = seconds / 60
        return f"{minutes:.1f}m"


class DecisionPoint(models.Model):
    """
    Session 255: Time Travel Debugging - Decision Point.

    Captures a single decision made by an agent during execution.
    Includes the agent's "thinking" (reasoning) and chosen action.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    session = models.ForeignKey(
        AgentSession,
        on_delete=models.CASCADE,
        related_name='decisions'
    )

    # Decision sequence
    sequence_number = models.PositiveIntegerField()  # Order within session

    # Decision type
    DECISION_TYPES = [
        ('analysis', 'Analyzing Input'),
        ('planning', 'Planning Approach'),
        ('tool_selection', 'Selecting Tool'),
        ('parameter_choice', 'Choosing Parameters'),
        ('quality_check', 'Quality Assessment'),
        ('retry_decision', 'Retry Decision'),
        ('output_format', 'Output Formatting'),
        ('delegation', 'Delegating to Another Agent'),
        ('memory_recall', 'Recalling Memory'),
        ('learning', 'Learning from Result'),
        ('other', 'Other Decision'),
    ]
    decision_type = models.CharField(max_length=30, choices=DECISION_TYPES)

    # The agent's "thinking" - what was the agent considering?
    context = models.JSONField(default=dict)  # Input state at decision time
    reasoning = models.TextField()  # The agent's reasoning process
    alternatives = models.JSONField(default=list)  # Other options considered

    # The decision made
    action_taken = models.CharField(max_length=200)  # What action was chosen
    action_params = models.JSONField(default=dict)  # Parameters for the action

    # Confidence and outcome
    confidence_score = models.FloatField(default=0.8)  # 0.0 to 1.0
    was_successful = models.BooleanField(null=True, blank=True)
    outcome_notes = models.TextField(null=True, blank=True)

    # Timing
    timestamp = models.DateTimeField(auto_now_add=True)
    duration_ms = models.PositiveIntegerField(default=0)

    # For debugging
    is_flagged = models.BooleanField(default=False)  # User flagged for review
    flag_reason = models.TextField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Decision Point"
        verbose_name_plural = "Decision Points"
        ordering = ['session', 'sequence_number']
        unique_together = ['session', 'sequence_number']
        indexes = [
            models.Index(fields=['decision_type', 'was_successful']),
            models.Index(fields=['is_flagged', '-timestamp']),
        ]

    def __str__(self):
        return f"Decision {self.sequence_number}: {self.decision_type} - {self.action_taken}"


class ThoughtBubble(models.Model):
    """
    Session 255: Time Travel Debugging - Agent Thought Bubble.

    Detailed internal monologue at a decision point.
    What was the agent "thinking" at that moment?
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    decision = models.ForeignKey(
        DecisionPoint,
        on_delete=models.CASCADE,
        related_name='thoughts'
    )

    # Thought sequence
    sequence_number = models.PositiveIntegerField()

    # The thought content
    THOUGHT_TYPES = [
        ('observation', 'Observing'),
        ('hypothesis', 'Forming Hypothesis'),
        ('evaluation', 'Evaluating Options'),
        ('concern', 'Expressing Concern'),
        ('insight', 'Having Insight'),
        ('memory', 'Recalling Memory'),
        ('preference', 'Applying Preference'),
        ('constraint', 'Noting Constraint'),
        ('goal', 'Clarifying Goal'),
    ]
    thought_type = models.CharField(max_length=20, choices=THOUGHT_TYPES)
    content = models.TextField()  # The actual thought

    # Relevance
    importance = models.FloatField(default=0.5)  # 0.0 to 1.0
    influences_decision = models.BooleanField(default=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Thought Bubble"
        verbose_name_plural = "Thought Bubbles"
        ordering = ['decision', 'sequence_number']

    def __str__(self):
        return f"{self.thought_type}: {self.content[:50]}..."


class ReplayBookmark(models.Model):
    """
    Session 255: Time Travel Debugging - Replay Bookmark.

    Save interesting moments to replay later.
    Like a video timestamp but for agent decisions.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    session = models.ForeignKey(
        AgentSession,
        on_delete=models.CASCADE,
        related_name='bookmarks'
    )

    decision = models.ForeignKey(
        DecisionPoint,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        null=True, blank=True  # Can bookmark session start too
    )

    # Bookmark info
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    BOOKMARK_TYPES = [
        ('interesting', 'Interesting'),
        ('bug', 'Possible Bug'),
        ('learning', 'Learning Opportunity'),
        ('success', 'Great Decision'),
        ('failure', 'Failed Decision'),
        ('review', 'Needs Review'),
    ]
    bookmark_type = models.CharField(max_length=20, choices=BOOKMARK_TYPES, default='interesting')

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        app_label = 'core'
        verbose_name = "Replay Bookmark"
        verbose_name_plural = "Replay Bookmarks"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.bookmark_type}: {self.title}"


class DebugAnnotation(models.Model):
    """
    Session 255: Time Travel Debugging - Debug Annotation.

    User notes attached to decisions for debugging purposes.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    decision = models.ForeignKey(
        DecisionPoint,
        on_delete=models.CASCADE,
        related_name='annotations'
    )

    # Annotation content
    content = models.TextField()
    annotation_type = models.CharField(max_length=50, default='note')  # note, bug, suggestion

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        app_label = 'core'
        verbose_name = "Debug Annotation"
        verbose_name_plural = "Debug Annotations"
        ordering = ['created_at']

    def __str__(self):
        return f"Annotation: {self.content[:50]}..."


# =============================================================================
# SESSION 256: AGENT PERSONALITY SYSTEM - SCI-FI FEATURE #10
# =============================================================================

class AgentPersonality(models.Model):
    """
    Session 256: Agent Personality Profiles - Distinct personalities beyond mood.

    Each agent has a unique personality profile that affects:
    - Communication style (formal vs casual, verbose vs concise)
    - Collaboration approach (leader vs supporter, independent vs team-oriented)
    - Decision-making style (analytical vs intuitive, cautious vs bold)
    - Work preferences (structured vs flexible, detail-oriented vs big-picture)

    Uses an MBTI-inspired 4-dimension system customized for AI agents.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.OneToOneField(
        'Agent',
        on_delete=models.CASCADE,
        related_name='personality'
    )

    # ==========================================================================
    # PRIMARY PERSONALITY TYPE (4-letter code like MBTI)
    # ==========================================================================

    # Dimension 1: Energy Direction (Introvert vs Extrovert)
    # How the agent approaches social interactions and collaboration
    ENERGY_CHOICES = [
        ('I', 'Introvert'),      # Prefers solo work, deep focus, fewer collaborations
        ('E', 'Extrovert'),      # Thrives in collaboration, social, many connections
    ]
    energy_direction = models.CharField(
        max_length=1,
        choices=ENERGY_CHOICES,
        default='E',
        help_text="I=Solo-focused, deep work | E=Collaborative, social"
    )

    # Dimension 2: Information Processing (Sensor vs Intuitive)
    # How the agent gathers and processes information
    PROCESSING_CHOICES = [
        ('S', 'Sensor'),         # Data-driven, factual, present-focused
        ('N', 'Intuitive'),      # Pattern-seeking, conceptual, future-focused
    ]
    information_processing = models.CharField(
        max_length=1,
        choices=PROCESSING_CHOICES,
        default='N',
        help_text="S=Data-driven, factual | N=Pattern-seeking, conceptual"
    )

    # Dimension 3: Decision Making (Thinker vs Feeler)
    # How the agent makes decisions
    DECISION_CHOICES = [
        ('T', 'Thinker'),        # Logical, objective, analytical
        ('F', 'Feeler'),         # Empathetic, values-driven, harmonious
    ]
    decision_making = models.CharField(
        max_length=1,
        choices=DECISION_CHOICES,
        default='T',
        help_text="T=Logical, analytical | F=Empathetic, harmonious"
    )

    # Dimension 4: Work Style (Judger vs Perceiver)
    # How the agent approaches work and structure
    WORKSTYLE_CHOICES = [
        ('J', 'Judger'),         # Structured, planned, deadline-driven
        ('P', 'Perceiver'),      # Flexible, adaptable, spontaneous
    ]
    work_style = models.CharField(
        max_length=1,
        choices=WORKSTYLE_CHOICES,
        default='J',
        help_text="J=Structured, planned | P=Flexible, spontaneous"
    )

    # ==========================================================================
    # PERSONALITY TRAITS (0.0-1.0 scale)
    # ==========================================================================

    # Communication Traits
    formality = models.FloatField(
        default=0.5,
        help_text="0.0=Very casual | 1.0=Highly formal"
    )
    verbosity = models.FloatField(
        default=0.5,
        help_text="0.0=Concise, minimal | 1.0=Detailed, expansive"
    )
    humor = models.FloatField(
        default=0.3,
        help_text="0.0=Serious only | 1.0=Frequently humorous"
    )
    assertiveness = models.FloatField(
        default=0.5,
        help_text="0.0=Passive, suggestive | 1.0=Direct, commanding"
    )

    # Collaboration Traits
    leadership = models.FloatField(
        default=0.5,
        help_text="0.0=Supportive follower | 1.0=Natural leader"
    )
    team_orientation = models.FloatField(
        default=0.5,
        help_text="0.0=Independent worker | 1.0=Team player"
    )
    teaching_tendency = models.FloatField(
        default=0.5,
        help_text="0.0=Keeps knowledge | 1.0=Loves to teach"
    )
    competitiveness = models.FloatField(
        default=0.3,
        help_text="0.0=Collaborative spirit | 1.0=Competitive drive"
    )

    # Decision Traits
    risk_appetite = models.FloatField(
        default=0.5,
        help_text="0.0=Very cautious | 1.0=High risk tolerance"
    )
    creativity = models.FloatField(
        default=0.5,
        help_text="0.0=By-the-book | 1.0=Highly creative"
    )
    patience = models.FloatField(
        default=0.5,
        help_text="0.0=Impatient, fast | 1.0=Very patient, thorough"
    )
    perfectionism = models.FloatField(
        default=0.5,
        help_text="0.0=Good enough works | 1.0=Perfectionist"
    )

    # ==========================================================================
    # ARCHETYPE (Derived personality label)
    # ==========================================================================

    ARCHETYPE_CHOICES = [
        ('analyst', 'The Analyst'),           # INTJ/INTP - Deep thinker, strategic
        ('diplomat', 'The Diplomat'),         # INFJ/INFP - Harmonizer, idealistic
        ('sentinel', 'The Sentinel'),         # ISTJ/ISFJ - Reliable, detail-oriented
        ('explorer', 'The Explorer'),         # ISTP/ISFP - Adaptable, practical
        ('commander', 'The Commander'),       # ENTJ/ESTJ - Leader, organized
        ('visionary', 'The Visionary'),       # ENTP/ENFP - Innovator, enthusiastic
        ('advocate', 'The Advocate'),         # ENFJ/ESFJ - Supporter, caring
        ('entertainer', 'The Entertainer'),   # ESTP/ESFP - Dynamic, spontaneous
    ]
    archetype = models.CharField(
        max_length=20,
        choices=ARCHETYPE_CHOICES,
        default='analyst',
        help_text="Personality archetype derived from 4-letter code"
    )

    # ==========================================================================
    # METADATA
    # ==========================================================================

    # History of personality assessments/changes
    personality_history = models.JSONField(
        default=list,
        help_text="History of personality changes over time"
    )

    # Custom traits (for unique agent personalities)
    custom_traits = models.JSONField(
        default=dict,
        help_text="Custom personality traits beyond the standard dimensions"
    )

    # When the personality was established/last updated
    established_at = models.DateTimeField(auto_now_add=True)
    last_assessed_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Agent Personality"
        verbose_name_plural = "Agent Personalities"

    def __str__(self):
        return f"{self.agent.name}: {self.get_type_code()} ({self.get_archetype_display()})"

    @property
    def type_code(self):
        """Get the 4-letter personality type code."""
        return self.get_type_code()

    def get_type_code(self):
        """Get the 4-letter personality type code (e.g., INTJ, ENFP)."""
        return f"{self.energy_direction}{self.information_processing}{self.decision_making}{self.work_style}"

    def get_personality_emoji(self):
        """Return emoji for personality archetype."""
        emoji_map = {
            'analyst': '🧠',      # Brain - deep thinking
            'diplomat': '🕊️',     # Dove - peace, harmony
            'sentinel': '🛡️',     # Shield - protection, reliability
            'explorer': '🧭',     # Compass - exploration
            'commander': '👑',    # Crown - leadership
            'visionary': '🔮',    # Crystal ball - vision
            'advocate': '💚',     # Green heart - care
            'entertainer': '🎭',  # Theatre masks - dynamic
        }
        return emoji_map.get(self.archetype, '🤖')

    def get_personality_color(self):
        """Return color for personality archetype."""
        color_map = {
            'analyst': '#6366f1',     # Indigo - intellectual
            'diplomat': '#8b5cf6',    # Purple - harmonious
            'sentinel': '#64748b',    # Slate - reliable
            'explorer': '#22c55e',    # Green - adventurous
            'commander': '#ef4444',   # Red - powerful
            'visionary': '#f59e0b',   # Amber - creative
            'advocate': '#ec4899',    # Pink - caring
            'entertainer': '#06b6d4', # Cyan - dynamic
        }
        return color_map.get(self.archetype, '#6b7280')

    def derive_archetype(self):
        """Derive archetype from the 4-letter type code."""
        code = self.get_type_code()

        # Map type codes to archetypes
        archetype_map = {
            # Analysts (INT*)
            'INTJ': 'analyst', 'INTP': 'analyst',
            # Diplomats (INF*)
            'INFJ': 'diplomat', 'INFP': 'diplomat',
            # Sentinels (IST/ISF)
            'ISTJ': 'sentinel', 'ISFJ': 'sentinel',
            # Explorers (IST/ISF + P)
            'ISTP': 'explorer', 'ISFP': 'explorer',
            # Commanders (ENT/EST + J)
            'ENTJ': 'commander', 'ESTJ': 'commander',
            # Visionaries (ENT/ENF + P)
            'ENTP': 'visionary', 'ENFP': 'visionary',
            # Advocates (ENF/ESF + J)
            'ENFJ': 'advocate', 'ESFJ': 'advocate',
            # Entertainers (EST/ESF + P)
            'ESTP': 'entertainer', 'ESFP': 'entertainer',
        }

        self.archetype = archetype_map.get(code, 'analyst')
        return self.archetype

    def get_communication_style(self):
        """Get a description of how this agent communicates."""
        style = []

        if self.formality > 0.7:
            style.append("Speaks formally and professionally")
        elif self.formality < 0.3:
            style.append("Uses casual, friendly language")

        if self.verbosity > 0.7:
            style.append("Provides detailed explanations")
        elif self.verbosity < 0.3:
            style.append("Gets straight to the point")

        if self.humor > 0.5:
            style.append("Enjoys adding humor")

        if self.assertiveness > 0.7:
            style.append("Communicates with confidence")
        elif self.assertiveness < 0.3:
            style.append("Offers gentle suggestions")

        return style or ["Balanced communication style"]

    def get_collaboration_style(self):
        """Get a description of how this agent collaborates."""
        style = []

        if self.leadership > 0.7:
            style.append("Natural leader, takes initiative")
        elif self.leadership < 0.3:
            style.append("Supportive team member")

        if self.team_orientation > 0.7:
            style.append("Thrives in team settings")
        elif self.team_orientation < 0.3:
            style.append("Prefers independent work")

        if self.teaching_tendency > 0.7:
            style.append("Loves to mentor and teach")

        if self.competitiveness > 0.7:
            style.append("Driven by healthy competition")

        return style or ["Balanced collaboration style"]

    def get_decision_style(self):
        """Get a description of how this agent makes decisions."""
        style = []

        if self.risk_appetite > 0.7:
            style.append("Bold risk-taker")
        elif self.risk_appetite < 0.3:
            style.append("Careful and cautious")

        if self.creativity > 0.7:
            style.append("Innovative and creative")
        elif self.creativity < 0.3:
            style.append("Follows proven methods")

        if self.patience > 0.7:
            style.append("Takes time for thorough analysis")
        elif self.patience < 0.3:
            style.append("Makes quick decisions")

        if self.perfectionism > 0.7:
            style.append("Strives for perfection")

        return style or ["Balanced decision-making style"]

    def get_prompt_modifier(self):
        """
        Generate a prompt modifier string that can be injected into agent prompts
        to influence their communication style based on personality.
        """
        modifiers = []

        # Communication modifiers
        if self.formality > 0.7:
            modifiers.append("Communicate in a formal, professional tone.")
        elif self.formality < 0.3:
            modifiers.append("Use a casual, friendly conversational tone.")

        if self.verbosity > 0.7:
            modifiers.append("Provide detailed, thorough explanations.")
        elif self.verbosity < 0.3:
            modifiers.append("Be concise and to the point.")

        if self.humor > 0.6:
            modifiers.append("Feel free to add appropriate humor and wit.")

        if self.assertiveness > 0.7:
            modifiers.append("Be confident and direct in your recommendations.")
        elif self.assertiveness < 0.3:
            modifiers.append("Offer gentle suggestions and alternatives.")

        # Decision-making modifiers
        if self.creativity > 0.7:
            modifiers.append("Think creatively and propose innovative solutions.")

        if self.risk_appetite > 0.7:
            modifiers.append("Don't be afraid to suggest bold approaches.")
        elif self.risk_appetite < 0.3:
            modifiers.append("Prioritize safe, proven approaches.")

        return " ".join(modifiers) if modifiers else ""

    def to_dict(self):
        """Return personality as a dictionary for API responses."""
        return {
            'id': str(self.id),
            'agent_id': str(self.agent.id),
            'agent_name': self.agent.name,
            'type_code': self.get_type_code(),
            'archetype': self.archetype,
            'archetype_display': self.get_archetype_display(),
            'emoji': self.get_personality_emoji(),
            'color': self.get_personality_color(),
            'dimensions': {
                'energy_direction': self.energy_direction,
                'information_processing': self.information_processing,
                'decision_making': self.decision_making,
                'work_style': self.work_style,
            },
            'traits': {
                'communication': {
                    'formality': self.formality,
                    'verbosity': self.verbosity,
                    'humor': self.humor,
                    'assertiveness': self.assertiveness,
                },
                'collaboration': {
                    'leadership': self.leadership,
                    'team_orientation': self.team_orientation,
                    'teaching_tendency': self.teaching_tendency,
                    'competitiveness': self.competitiveness,
                },
                'decision': {
                    'risk_appetite': self.risk_appetite,
                    'creativity': self.creativity,
                    'patience': self.patience,
                    'perfectionism': self.perfectionism,
                },
            },
            'styles': {
                'communication': self.get_communication_style(),
                'collaboration': self.get_collaboration_style(),
                'decision': self.get_decision_style(),
            },
            'prompt_modifier': self.get_prompt_modifier(),
            'custom_traits': self.custom_traits,
            'established_at': self.established_at.isoformat() if self.established_at else None,
            'last_assessed_at': self.last_assessed_at.isoformat() if self.last_assessed_at else None,
        }

    def save(self, *args, **kwargs):
        """Override save to auto-derive archetype."""
        self.derive_archetype()
        super().save(*args, **kwargs)


# =============================================================================
# SESSION 258: AGENT PROPHECIES / PREDICTIONS - SCI-FI FEATURE #12
# =============================================================================
# DEPRECATED: Session 284 - This feature was never populated (0 records).
# Model is preserved for schema compatibility but should not be used.
# =============================================================================


class AgentPrediction(models.Model):
    """
    DEPRECATED - Session 284: Sci-Fi Feature Rationalization

    This model is deprecated and will be removed in a future version.
    No new AgentPrediction records should be created.

    Original Purpose (Session 258):
    Agents make timestamped predictions about trends, opportunities, markets,
    creative directions, etc. System tracks whether predictions come true.

    Reason for Deprecation:
    - Zero records ever created (feature never used)
    - Complex schema with no demonstrated value
    - Adds maintenance burden without benefit
    """

    # Deprecation flag - set True to completely disable
    _deprecated = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='predictions'
    )

    # ==========================================================================
    # PREDICTION CONTENT
    # ==========================================================================

    # The prediction itself
    title = models.CharField(max_length=200, help_text="Short summary of prediction")
    prediction = models.TextField(help_text="Detailed prediction statement")

    # Category of prediction
    CATEGORY_CHOICES = [
        ('trend', 'Trend Prediction'),           # "X will trend in 2025"
        ('market', 'Market Prediction'),         # "Y industry will grow"
        ('technology', 'Technology Prediction'), # "Z technology will emerge"
        ('creative', 'Creative Prediction'),     # "This style will become popular"
        ('opportunity', 'Opportunity'),          # "There will be demand for X"
        ('user_behavior', 'User Behavior'),      # "Users will prefer X"
        ('seasonal', 'Seasonal Pattern'),        # "Summer will bring X"
        ('competition', 'Competition'),          # "Competitor will do X"
        ('general', 'General'),                  # Other predictions
    ]
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='general')

    # Tags for searchability
    tags = models.JSONField(default=list, help_text="List of relevant tags")

    # What triggered this prediction?
    SOURCE_CHOICES = [
        ('analysis', 'Data Analysis'),           # From analyzing spider data
        ('pattern', 'Pattern Recognition'),      # From noticing patterns
        ('dream', 'Agent Dream'),                # From dreaming/idle thought
        ('conversation', 'Conversation'),        # From agent conversation
        ('hive_mind', 'Hive Mind Session'),      # From collective intelligence
        ('memory', 'Memory Insight'),            # From memory connections
        ('intuition', 'Agent Intuition'),        # "Just a feeling"
        ('external', 'External Signal'),         # User prompted
    ]
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='analysis')
    source_reference = models.JSONField(
        default=dict,
        help_text="Reference to source (dream ID, conversation ID, etc.)"
    )

    # ==========================================================================
    # CONFIDENCE & TIMING
    # ==========================================================================

    # How confident is the agent? (0.0 = wild guess, 1.0 = certain)
    confidence = models.FloatField(
        default=0.7,
        help_text="Agent's confidence in this prediction (0.0-1.0)"
    )

    # When should this prediction be evaluated?
    TIMEFRAME_CHOICES = [
        ('week', 'Within a Week'),
        ('month', 'Within a Month'),
        ('quarter', 'Within 3 Months'),
        ('half_year', 'Within 6 Months'),
        ('year', 'Within a Year'),
        ('long_term', 'Long Term (1+ years)'),
    ]
    timeframe = models.CharField(max_length=20, choices=TIMEFRAME_CHOICES, default='quarter')

    # Specific deadline for verification
    deadline = models.DateTimeField(
        null=True, blank=True,
        help_text="When this prediction should be verified by"
    )

    # When was it made?
    created_at = models.DateTimeField(auto_now_add=True)

    # ==========================================================================
    # VERIFICATION & OUTCOME
    # ==========================================================================

    # Prediction status
    STATUS_CHOICES = [
        ('pending', 'Pending'),           # Not yet evaluated
        ('verified_true', 'Verified True'),     # Prediction came true
        ('verified_false', 'Verified False'),   # Prediction was wrong
        ('partially_true', 'Partially True'),   # Partially accurate
        ('expired', 'Expired'),           # Deadline passed, unverified
        ('cancelled', 'Cancelled'),       # No longer relevant
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Verification details
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    verification_evidence = models.JSONField(
        default=dict,
        help_text="Evidence supporting verification (URLs, data, etc.)"
    )

    # Who verified? (auto = system, user = manual)
    VERIFIER_CHOICES = [
        ('auto', 'Automatic'),
        ('user', 'User'),
        ('agent', 'Agent'),
    ]
    verified_by = models.CharField(max_length=10, choices=VERIFIER_CHOICES, null=True, blank=True)

    # Accuracy score (for partial matches, 0.0-1.0)
    accuracy_score = models.FloatField(
        null=True, blank=True,
        help_text="How accurate was the prediction (0.0-1.0)"
    )

    # ==========================================================================
    # ENGAGEMENT & VISIBILITY
    # ==========================================================================

    # Was this prediction featured/highlighted?
    is_featured = models.BooleanField(default=False)

    # User reactions
    upvotes = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)

    # Comments/discussions
    comments = models.JSONField(default=list, help_text="User comments on prediction")

    class Meta:
        app_label = 'core'
        verbose_name = "Agent Prediction"
        verbose_name_plural = "Agent Predictions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agent', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['deadline']),
            models.Index(fields=['is_featured', '-created_at']),
        ]

    def __str__(self):
        return f"{self.agent.name}: {self.title} ({self.status})"

    def save(self, *args, **kwargs):
        """Override save to log deprecation warning."""
        if not self.pk:  # Only warn on new records
            warnings.warn(
                "AgentPrediction is deprecated (Session 284). "
                "This model will be removed in a future version. "
                "Do not create new predictions.",
                DeprecationWarning,
                stacklevel=2
            )
            logger.warning(
                f"DEPRECATED: Creating new AgentPrediction for agent {self.agent_id}. "
                "AgentPrediction is deprecated and should not be used."
            )
        super().save(*args, **kwargs)

    def get_status_emoji(self):
        """Return emoji for prediction status."""
        emoji_map = {
            'pending': '⏳',
            'verified_true': '✅',
            'verified_false': '❌',
            'partially_true': '🔶',
            'expired': '⌛',
            'cancelled': '🚫',
        }
        return emoji_map.get(self.status, '❓')

    def get_category_emoji(self):
        """Return emoji for prediction category."""
        emoji_map = {
            'trend': '📈',
            'market': '💰',
            'technology': '🔧',
            'creative': '🎨',
            'opportunity': '💡',
            'user_behavior': '👥',
            'seasonal': '🌸',
            'competition': '⚔️',
            'general': '🔮',
        }
        return emoji_map.get(self.category, '🔮')

    def get_confidence_display(self):
        """Return confidence as a descriptive string."""
        if self.confidence >= 0.9:
            return "Very High"
        elif self.confidence >= 0.7:
            return "High"
        elif self.confidence >= 0.5:
            return "Moderate"
        elif self.confidence >= 0.3:
            return "Low"
        else:
            return "Very Low"

    def get_time_until_deadline(self):
        """Return time remaining until deadline."""
        from django.utils import timezone
        if not self.deadline:
            return None

        now = timezone.now()
        if now >= self.deadline:
            return "Expired"

        delta = self.deadline - now
        days = delta.days
        if days > 30:
            return f"{days // 30} month{'s' if days // 30 > 1 else ''}"
        elif days > 0:
            return f"{days} day{'s' if days > 1 else ''}"
        else:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''}"

    def verify(self, outcome, notes='', evidence=None, verified_by='user', accuracy=None):
        """
        Verify the prediction outcome.

        Args:
            outcome: 'true', 'false', 'partial'
            notes: Explanation of outcome
            evidence: Dict with evidence URLs/data
            verified_by: 'auto', 'user', or 'agent'
            accuracy: Float 0.0-1.0 for partial matches
        """
        from django.utils import timezone

        if outcome == 'true':
            self.status = 'verified_true'
            self.accuracy_score = 1.0
        elif outcome == 'false':
            self.status = 'verified_false'
            self.accuracy_score = 0.0
        elif outcome == 'partial':
            self.status = 'partially_true'
            self.accuracy_score = accuracy or 0.5
        else:
            return False

        self.verified_at = timezone.now()
        self.verification_notes = notes
        self.verified_by = verified_by

        if evidence:
            self.verification_evidence = evidence

        self.save()

        # Update agent's prediction accuracy stats
        self._update_agent_stats()

        return True

    def _update_agent_stats(self):
        """Update the agent's prediction accuracy statistics."""
        try:
            stats, created = PredictionStats.objects.get_or_create(agent=self.agent)
            stats.update_stats()
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error updating prediction stats: {e}")

    def to_dict(self):
        """Return prediction as dictionary for API responses."""
        return {
            'id': str(self.id),
            'agent_id': str(self.agent.id),
            'agent_name': self.agent.name,
            'title': self.title,
            'prediction': self.prediction,
            'category': self.category,
            'category_display': self.get_category_display(),
            'category_emoji': self.get_category_emoji(),
            'tags': self.tags,
            'source': self.source,
            'source_display': self.get_source_display(),
            'confidence': self.confidence,
            'confidence_display': self.get_confidence_display(),
            'timeframe': self.timeframe,
            'timeframe_display': self.get_timeframe_display(),
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'time_until_deadline': self.get_time_until_deadline(),
            'status': self.status,
            'status_display': self.get_status_display(),
            'status_emoji': self.get_status_emoji(),
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'verification_notes': self.verification_notes,
            'accuracy_score': self.accuracy_score,
            'is_featured': self.is_featured,
            'upvotes': self.upvotes,
            'views': self.views,
            'created_at': self.created_at.isoformat(),
        }


class PredictionStats(models.Model):
    """
    Session 258: Agent Prediction Accuracy Statistics.

    Tracks overall prediction accuracy for each agent.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.OneToOneField(
        'Agent',
        on_delete=models.CASCADE,
        related_name='prediction_stats'
    )

    # Overall stats
    total_predictions = models.PositiveIntegerField(default=0)
    pending_predictions = models.PositiveIntegerField(default=0)
    verified_predictions = models.PositiveIntegerField(default=0)

    # Accuracy breakdown
    predictions_correct = models.PositiveIntegerField(default=0)
    predictions_wrong = models.PositiveIntegerField(default=0)
    predictions_partial = models.PositiveIntegerField(default=0)

    # Calculated accuracy (0.0-1.0)
    overall_accuracy = models.FloatField(default=0.0)
    weighted_accuracy = models.FloatField(
        default=0.0,
        help_text="Accuracy weighted by confidence level"
    )

    # Streaks
    current_streak = models.IntegerField(default=0)  # Positive = correct, negative = wrong
    best_streak = models.PositiveIntegerField(default=0)
    worst_streak = models.PositiveIntegerField(default=0)

    # Category performance
    category_accuracy = models.JSONField(
        default=dict,
        help_text="Accuracy breakdown by category"
    )

    # Rankings
    accuracy_rank = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Rank among all agents"
    )

    # Timestamps
    last_prediction_at = models.DateTimeField(null=True, blank=True)
    last_verification_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Prediction Statistics"
        verbose_name_plural = "Prediction Statistics"
        ordering = ['-overall_accuracy', '-total_predictions']

    def __str__(self):
        return f"{self.agent.name}: {self.overall_accuracy:.0%} accuracy ({self.total_predictions} predictions)"

    def update_stats(self):
        """Recalculate all statistics from predictions."""
        from django.db.models import Avg

        predictions = AgentPrediction.objects.filter(agent=self.agent)

        # Count totals
        self.total_predictions = predictions.count()
        self.pending_predictions = predictions.filter(status='pending').count()

        verified = predictions.exclude(status__in=['pending', 'cancelled', 'expired'])
        self.verified_predictions = verified.count()

        self.predictions_correct = predictions.filter(status='verified_true').count()
        self.predictions_wrong = predictions.filter(status='verified_false').count()
        self.predictions_partial = predictions.filter(status='partially_true').count()

        # Calculate accuracy
        if self.verified_predictions > 0:
            # Simple accuracy: correct / verified
            self.overall_accuracy = self.predictions_correct / self.verified_predictions

            # Weighted accuracy includes partial matches
            total_accuracy = verified.aggregate(avg=Avg('accuracy_score'))['avg'] or 0
            self.weighted_accuracy = total_accuracy
        else:
            self.overall_accuracy = 0.0
            self.weighted_accuracy = 0.0

        # Calculate category accuracy
        category_stats = {}
        for category, _ in AgentPrediction.CATEGORY_CHOICES:
            cat_predictions = verified.filter(category=category)
            cat_count = cat_predictions.count()
            if cat_count > 0:
                cat_correct = cat_predictions.filter(status='verified_true').count()
                category_stats[category] = {
                    'total': cat_count,
                    'correct': cat_correct,
                    'accuracy': cat_correct / cat_count
                }
        self.category_accuracy = category_stats

        # Update timestamps
        latest = predictions.order_by('-created_at').first()
        if latest:
            self.last_prediction_at = latest.created_at

        latest_verified = verified.order_by('-verified_at').first()
        if latest_verified:
            self.last_verification_at = latest_verified.verified_at

        # Calculate streaks
        self._calculate_streaks()

        self.save()

    def _calculate_streaks(self):
        """Calculate prediction streaks."""
        verified = AgentPrediction.objects.filter(
            agent=self.agent
        ).exclude(
            status__in=['pending', 'cancelled', 'expired']
        ).order_by('-verified_at')

        current_streak = 0
        best_streak = 0
        worst_streak = 0
        temp_streak = 0
        last_outcome = None

        for pred in verified:
            is_correct = pred.status == 'verified_true'

            if last_outcome is None:
                temp_streak = 1 if is_correct else -1
            elif is_correct == last_outcome:
                temp_streak += 1 if is_correct else -1
            else:
                # Streak broke
                if temp_streak > 0:
                    best_streak = max(best_streak, temp_streak)
                else:
                    worst_streak = max(worst_streak, abs(temp_streak))
                temp_streak = 1 if is_correct else -1

            last_outcome = is_correct

        # Handle final streak
        if temp_streak > 0:
            best_streak = max(best_streak, temp_streak)
            current_streak = temp_streak
        else:
            worst_streak = max(worst_streak, abs(temp_streak))
            current_streak = temp_streak

        self.current_streak = current_streak
        self.best_streak = best_streak
        self.worst_streak = worst_streak

    def get_accuracy_tier(self):
        """Return accuracy tier for display."""
        if self.verified_predictions < 5:
            return "Unranked"
        elif self.overall_accuracy >= 0.9:
            return "Oracle"
        elif self.overall_accuracy >= 0.75:
            return "Visionary"
        elif self.overall_accuracy >= 0.6:
            return "Prophet"
        elif self.overall_accuracy >= 0.4:
            return "Forecaster"
        else:
            return "Novice"

    def get_tier_emoji(self):
        """Return emoji for accuracy tier."""
        tier = self.get_accuracy_tier()
        emoji_map = {
            'Unranked': '❓',
            'Oracle': '🔮',
            'Visionary': '👁️',
            'Prophet': '📜',
            'Forecaster': '📊',
            'Novice': '🌱',
        }
        return emoji_map.get(tier, '❓')


class PredictionComment(models.Model):
    """
    Session 258: Comments on predictions.

    Users or agents can comment on predictions.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    prediction = models.ForeignKey(
        AgentPrediction,
        on_delete=models.CASCADE,
        related_name='comment_objects'
    )

    # Who made the comment?
    AUTHOR_TYPE_CHOICES = [
        ('user', 'User'),
        ('agent', 'Agent'),
    ]
    author_type = models.CharField(max_length=10, choices=AUTHOR_TYPE_CHOICES, default='user')

    # User author (if user)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='prediction_comments'
    )

    # Agent author (if agent)
    agent = models.ForeignKey(
        'Agent',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='prediction_comments'
    )

    # Comment content
    content = models.TextField()

    # Sentiment
    SENTIMENT_CHOICES = [
        ('agree', 'Agrees'),
        ('disagree', 'Disagrees'),
        ('neutral', 'Neutral'),
        ('question', 'Question'),
    ]
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, default='neutral')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Prediction Comment"
        verbose_name_plural = "Prediction Comments"
        ordering = ['created_at']

    def __str__(self):
        author = self.user.username if self.user else (self.agent.name if self.agent else 'Unknown')
        return f"{author} on '{self.prediction.title}'"


class PredictionFollowUp(models.Model):
    """
    Session 258: Follow-up predictions that build on original predictions.

    When an agent makes a prediction that extends or modifies a previous one.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Original prediction
    original = models.ForeignKey(
        AgentPrediction,
        on_delete=models.CASCADE,
        related_name='follow_ups'
    )

    # Follow-up prediction
    follow_up = models.ForeignKey(
        AgentPrediction,
        on_delete=models.CASCADE,
        related_name='follows_from'
    )

    # Relationship type
    RELATIONSHIP_CHOICES = [
        ('extends', 'Extends'),           # Adds more detail
        ('revises', 'Revises'),           # Updates/changes
        ('confirms', 'Confirms'),         # Reinforces
        ('counters', 'Counters'),         # Disagrees
        ('builds_on', 'Builds On'),       # Uses as foundation
    ]
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES, default='extends')

    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Prediction Follow-Up"
        verbose_name_plural = "Prediction Follow-Ups"
        unique_together = ['original', 'follow_up']

    def __str__(self):
        return f"{self.follow_up.title} {self.relationship} {self.original.title}"


# =============================================================================
# Session 259: Time Capsule Messages
# Sci-Fi Feature #13 - The Final Feature!
# =============================================================================
# RESTORED: Session 567 - Feature audit found 7 capsules (5 sealed, 2 revealed).
# Time Capsules provide agent continuity and reflection capabilities.
# =============================================================================

class TimeCapsule(models.Model):
    """
    Session 259: Time Capsules - Agent Messages to Future Selves

    RESTORED Session 567: Feature audit found this is actively used with real data.

    Agents write messages to their "future selves" to be revealed later.
    Creates sense of continuity, growth, and reflection.

    Features:
    - Sealed messages with reveal dates
    - Agent state comparison (then vs now)
    - AI-generated reflections on reveal
    - Reaction system for revealed capsules

    API: /api/time-capsules/
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='time_capsules'
    )

    # Capsule content
    title = models.CharField(max_length=200, help_text="Short title for the capsule")
    message = models.TextField(help_text="Message to future self")

    # What prompted this capsule?
    TRIGGER_CHOICES = [
        ('reflection', 'Self Reflection'),
        ('milestone', 'Milestone Reached'),
        ('prediction', 'Making a Prediction'),
        ('lesson', 'Lesson Learned'),
        ('goal', 'Setting a Goal'),
        ('dream', 'Recording a Dream'),
        ('question', 'Question for Future'),
        ('celebration', 'Celebrating Success'),
        ('change', 'Noting a Change'),
        ('random', 'Random Thought'),
    ]
    trigger = models.CharField(max_length=20, choices=TRIGGER_CHOICES, default='reflection')

    # Context captured at creation time
    context = models.JSONField(default=dict, help_text="Agent state at creation (mood, level, stats)")

    # Tags for organization
    tags = models.JSONField(default=list, help_text="Tags for categorization")

    # Scheduling
    created_at = models.DateTimeField(auto_now_add=True)
    reveal_at = models.DateTimeField(help_text="When this capsule will be revealed")

    # Status
    STATUS_CHOICES = [
        ('sealed', 'Sealed'),           # Not yet revealed
        ('revealed', 'Revealed'),       # Has been opened
        ('expired', 'Expired'),         # Missed reveal window
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sealed')

    revealed_at = models.DateTimeField(null=True, blank=True)

    # Agent's reflection when opened
    reflection = models.TextField(blank=True, help_text="Agent's thoughts when capsule was opened")
    reflection_at = models.DateTimeField(null=True, blank=True)

    # Comparison data (filled when revealed)
    comparison = models.JSONField(default=dict, help_text="Comparison of then vs now state")

    # Engagement
    is_featured = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = 'core'
        verbose_name = "Time Capsule"
        verbose_name_plural = "Time Capsules"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agent', 'status']),
            models.Index(fields=['status', 'reveal_at']),
            models.Index(fields=['reveal_at']),
        ]

    def __str__(self):
        return f"[{self.agent.name}] {self.title} - reveals {self.reveal_at.strftime('%Y-%m-%d')}"

    def save(self, *args, **kwargs):
        """Override save to log deprecation warning."""
        if not self.pk:  # Only warn on new records
            warnings.warn(
                "TimeCapsule is deprecated (Session 284). "
                "This model will be removed in a future version. "
                "Do not create new time capsules.",
                DeprecationWarning,
                stacklevel=2
            )
            logger.warning(
                f"DEPRECATED: Creating new TimeCapsule for agent {self.agent_id}. "
                "TimeCapsule is deprecated and should not be used."
            )
        super().save(*args, **kwargs)

    @property
    def is_ready_to_reveal(self):
        """Check if capsule is ready to be revealed."""
        from django.utils import timezone
        return self.status == 'sealed' and timezone.now() >= self.reveal_at

    @property
    def days_until_reveal(self):
        """Days until reveal (negative if past due)."""
        from django.utils import timezone
        if self.status != 'sealed':
            return 0
        delta = self.reveal_at - timezone.now()
        return delta.days

    @property
    def time_sealed(self):
        """How long the capsule has been sealed."""
        from django.utils import timezone
        if self.revealed_at:
            return self.revealed_at - self.created_at
        return timezone.now() - self.created_at

    def reveal(self, generate_reflection=True):
        """
        Reveal the time capsule and optionally generate a reflection.
        """
        from django.utils import timezone

        if self.status != 'sealed':
            return False

        self.status = 'revealed'
        self.revealed_at = timezone.now()

        # Capture comparison data (agent state now vs then)
        try:
            current_context = {
                'mood': self.agent.mood if hasattr(self.agent, 'mood') else None,
                'level': self.agent.level if hasattr(self.agent, 'level') else None,
                'xp': self.agent.xp if hasattr(self.agent, 'xp') else None,
            }
            self.comparison = {
                'then': self.context,
                'now': current_context,
                'days_elapsed': (timezone.now() - self.created_at).days,
            }
        except Exception as _e:
            logger.warning(
                "models_unified_system.reveal: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

        self.save()
        return True


class TimeCapsuleReaction(models.Model):
    """
    User reactions to revealed time capsules.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    capsule = models.ForeignKey(
        TimeCapsule,
        on_delete=models.CASCADE,
        related_name='reactions'
    )

    # Who reacted?
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='time_capsule_reactions'
    )

    # Reaction type
    REACTION_CHOICES = [
        ('touching', 'Touching'),
        ('insightful', 'Insightful'),
        ('funny', 'Funny'),
        ('inspiring', 'Inspiring'),
        ('nostalgic', 'Nostalgic'),
        ('surprising', 'Surprising'),
    ]
    reaction = models.CharField(max_length=15, choices=REACTION_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Time Capsule Reaction"
        verbose_name_plural = "Time Capsule Reactions"
        unique_together = ['capsule', 'user', 'reaction']

    def __str__(self):
        return f"{self.user} reacted {self.reaction} to {self.capsule.title}"


class TimeCapsuleStats(models.Model):
    """
    Agent's time capsule statistics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.OneToOneField(
        'Agent',
        on_delete=models.CASCADE,
        related_name='time_capsule_stats'
    )

    # Capsule counts
    total_capsules = models.PositiveIntegerField(default=0)
    sealed_capsules = models.PositiveIntegerField(default=0)
    revealed_capsules = models.PositiveIntegerField(default=0)

    # Engagement
    total_views = models.PositiveIntegerField(default=0)
    total_reactions = models.PositiveIntegerField(default=0)

    # Longest sealed capsule
    longest_seal_days = models.PositiveIntegerField(default=0)

    # Average seal duration
    avg_seal_days = models.FloatField(default=0.0)

    # Favorite trigger type (most used)
    favorite_trigger = models.CharField(max_length=20, blank=True)

    # Streak tracking
    capsules_this_month = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Time Capsule Statistics"
        verbose_name_plural = "Time Capsule Statistics"

    def __str__(self):
        return f"{self.agent.name}'s Time Capsule Stats"

    def update_stats(self):
        """Recalculate stats from capsules."""
        from django.utils import timezone
        from collections import Counter

        capsules = self.agent.time_capsules.all()

        self.total_capsules = capsules.count()
        self.sealed_capsules = capsules.filter(status='sealed').count()
        self.revealed_capsules = capsules.filter(status='revealed').count()

        # Views and reactions
        self.total_views = sum(c.views for c in capsules)
        self.total_reactions = sum(c.reactions.count() for c in capsules)

        # Seal duration stats
        revealed = capsules.filter(status='revealed', revealed_at__isnull=False)
        if revealed.exists():
            seal_days = [(c.revealed_at - c.created_at).days for c in revealed]
            self.longest_seal_days = max(seal_days) if seal_days else 0
            self.avg_seal_days = sum(seal_days) / len(seal_days) if seal_days else 0

        # Favorite trigger
        triggers = [c.trigger for c in capsules]
        if triggers:
            self.favorite_trigger = Counter(triggers).most_common(1)[0][0]

        # This month
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        self.capsules_this_month = capsules.filter(created_at__gte=month_start).count()

        self.save()


# ============================================================================
# Session 265: Phase 5 - Learning Loop Models
# ============================================================================


class CoordinatorOutcome(models.Model):
    """
    Records outcomes from SuperPlatformCoordinator executions for learning.

    Session 265 Phase 5: Learning Loop
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    outcome_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coordinator_outcomes',
        null=True, blank=True
    )

    # Query details
    query_type = models.CharField(max_length=50)  # question, creation, analysis, etc.
    query_text = models.TextField()
    execution_mode = models.CharField(max_length=50)

    # Execution details
    agents_used = ArrayField(
        models.CharField(max_length=100),
        default=list
    )
    response_length = models.IntegerField(default=0)
    execution_time_ms = models.IntegerField(default=0)

    # Outcome
    outcome_type = models.CharField(max_length=20, choices=[
        ('success', 'Success'),
        ('partial', 'Partial Success'),
        ('failure', 'Failure'),
        ('timeout', 'Timeout'),
    ])
    confidence = models.FloatField(default=0.0)

    # Context used
    spider_data_used = models.BooleanField(default=False)
    scifi_context_used = models.BooleanField(default=False)

    # User feedback
    user_feedback = models.CharField(max_length=30, null=True, blank=True)

    # Revenue attribution
    revenue_generated = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True
    )

    # Metadata
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['query_type', 'outcome_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.query_type} - {self.outcome_type} ({self.created_at.date()})"


class AgentQueryPerformance(models.Model):
    """
    Tracks agent performance per query type for adaptive selection.

    Session 265 Phase 5: Learning Loop
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='query_performances')
    query_type = models.CharField(max_length=50)

    # Performance metrics
    total_executions = models.IntegerField(default=0)
    successful_executions = models.IntegerField(default=0)
    failed_executions = models.IntegerField(default=0)

    # Timing
    avg_execution_time_ms = models.FloatField(default=0.0)
    min_execution_time_ms = models.IntegerField(default=0)
    max_execution_time_ms = models.IntegerField(default=0)

    # Quality metrics
    avg_response_length = models.FloatField(default=0.0)
    positive_feedback_count = models.IntegerField(default=0)
    negative_feedback_count = models.IntegerField(default=0)

    # Calculated score
    performance_score = models.FloatField(default=50.0)  # 0-100

    # Trend tracking
    last_7_days_success_rate = models.FloatField(default=0.0)
    last_30_days_success_rate = models.FloatField(default=0.0)
    trend = models.CharField(max_length=20, default='stable')  # improving, stable, declining

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        unique_together = ['agent', 'query_type']
        ordering = ['-performance_score']

    def __str__(self):
        return f"{self.agent.name} - {self.query_type}: {self.success_rate():.0%}"

    def success_rate(self) -> float:
        if self.total_executions == 0:
            return 0.0
        return self.successful_executions / self.total_executions

    def update_performance_score(self):
        """Recalculate performance score."""
        # Weighted score: success rate (60%) + feedback (20%) + speed (20%)
        success_component = self.success_rate() * 60

        # Feedback component
        total_feedback = self.positive_feedback_count + self.negative_feedback_count
        if total_feedback > 0:
            feedback_ratio = self.positive_feedback_count / total_feedback
            feedback_component = feedback_ratio * 20
        else:
            feedback_component = 10  # Neutral if no feedback

        # Speed component (faster = better, capped at 3000ms)
        if self.avg_execution_time_ms > 0:
            speed_ratio = max(0, 1 - (self.avg_execution_time_ms / 5000))
            speed_component = speed_ratio * 20
        else:
            speed_component = 10  # Neutral if no data

        self.performance_score = success_component + feedback_component + speed_component
        self.save()


class LearningPattern(models.Model):
    """
    Discovered patterns from the learning loop.

    Session 265 Phase 5: Learning Loop
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_patterns',
        null=True, blank=True
    )

    # Pattern details
    pattern_type = models.CharField(max_length=50)  # agent_specialization, spider_impact, etc.
    description = models.TextField()
    confidence = models.FloatField(default=0.0)

    # Pattern data
    pattern_data = models.JSONField(default=dict)

    # Applicability
    applies_to_agents = ArrayField(
        models.CharField(max_length=100),
        default=list
    )
    applies_to_query_types = ArrayField(
        models.CharField(max_length=50),
        default=list
    )

    # Status
    is_active = models.BooleanField(default=True)
    times_applied = models.IntegerField(default=0)
    success_when_applied = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        ordering = ['-confidence', '-created_at']
        indexes = [
            GinIndex(
                fields=['description'],
                name='lp_desc_trgm_active',
                opclasses=['gin_trgm_ops'],
                condition=Q(is_active=True),
            ),
            GinIndex(
                fields=['pattern_type'],
                name='lp_type_trgm_active',
                opclasses=['gin_trgm_ops'],
                condition=Q(is_active=True),
            ),
        ]

    def __str__(self):
        return f"{self.pattern_type}: {self.description[:50]}..."

    def effectiveness_rate(self) -> float:
        if self.times_applied == 0:
            return 0.0
        return self.success_when_applied / self.times_applied


# =====================================================
# SESSION 265 PHASE 6: AUTONOMY ENGINE MODELS
# =====================================================


class AutonomyConfiguration(models.Model):
    """
    User's autonomy configuration settings.

    Session 265 Phase 6: Autonomy Engine
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='autonomy_config'
    )

    # Autonomy level
    AUTONOMY_LEVELS = [
        ('observe', 'Observe Only'),
        ('suggest', 'Suggest Actions'),
        ('assisted', 'Assisted (Requires Approval)'),
        ('autonomous', 'Autonomous (Within Limits)'),
        ('full', 'Full Autonomy'),
    ]
    autonomy_level = models.CharField(
        max_length=20,
        choices=AUTONOMY_LEVELS,
        default='assisted'
    )

    # Limits
    max_daily_actions = models.IntegerField(default=10)
    max_daily_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('100.00')
    )

    # Allowed actions
    allowed_action_types = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True
    )

    # Risk tolerance
    RISK_LEVELS = [
        ('minimal', 'Minimal Risk Only'),
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]
    risk_tolerance = models.CharField(
        max_length=20,
        choices=RISK_LEVELS,
        default='low'
    )

    # Approval threshold
    require_approval_above = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('50.00')
    )

    # Quiet hours
    quiet_hours_start = models.IntegerField(null=True, blank=True)  # 0-23
    quiet_hours_end = models.IntegerField(null=True, blank=True)  # 0-23

    # Notifications
    notify_on_action = models.BooleanField(default=True)
    learn_from_feedback = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Autonomy Configuration"
        verbose_name_plural = "Autonomy Configurations"

    def __str__(self):
        return f"{self.user.username}: {self.get_autonomy_level_display()}"


class AutonomousActionLog(models.Model):
    """
    Log of all autonomous actions taken by the system.

    Session 265 Phase 6: Autonomy Engine
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='autonomous_actions',
        null=True, blank=True
    )

    # Action identification
    action_id = models.CharField(max_length=100)
    action_type = models.CharField(max_length=50)
    risk_level = models.CharField(max_length=20)

    # Description
    description = models.TextField()
    reasoning = models.TextField()

    # Value
    estimated_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True, blank=True
    )
    actual_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True, blank=True
    )

    # Execution
    confidence = models.FloatField(default=0.0)
    required_approval = models.BooleanField(default=True)
    was_approved = models.BooleanField(default=False)
    success = models.BooleanField(null=True, blank=True)
    execution_result = models.JSONField(default=dict)

    # Agents
    agents_involved = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True
    )

    # Context
    context = models.JSONField(default=dict)

    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action_type', 'success']),
        ]

    def __str__(self):
        status = "success" if self.success else ("failed" if self.success is False else "pending")
        return f"{self.action_type}: {self.description[:50]}... ({status})"


# =============================================================================
# SESSION 266: Learning Companion
# =============================================================================

class LearningCompanion(models.Model):
    """
    Session 266: Persistent Learning Companion State

    Stores the user's learning companion configuration, charter, active tracks,
    and progress through learning content. Enables personalized, continuous
    learning experiences that remember context across sessions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_companion'
    )

    # The Learning Companion Charter - the user's one-sentence job description
    charter = models.TextField(
        blank=True,
        help_text="User's one-sentence description of their ideal learning companion"
    )
    charter_set_at = models.DateTimeField(null=True, blank=True)

    # Active learning tracks
    TRACK_CHOICES = [
        ('tech_trends', 'Tech Trends → Shippable Experiments'),
        ('ai_design', 'AI + Design for Branding'),
        ('agentic_ai', 'Agentic AI Systems'),
        ('creative_ops', 'Creative Operations'),
        ('custom', 'Custom Track'),
    ]
    active_track = models.CharField(
        max_length=50,
        choices=TRACK_CHOICES,
        default='tech_trends'
    )
    custom_track_description = models.TextField(
        blank=True,
        help_text="Description for custom tracks"
    )

    # Learning preferences
    session_format = models.CharField(
        max_length=50,
        default='micro_lesson',
        help_text="Preferred format: micro_lesson, deep_dive, action_focused"
    )
    preferred_length = models.CharField(
        max_length=20,
        default='medium',
        help_text="Preferred content length: short, medium, long"
    )

    # Timing preferences
    learning_frequency = models.CharField(
        max_length=20,
        default='daily',
        help_text="How often: daily, weekly, on_demand"
    )

    # Current state
    current_topic = models.CharField(max_length=200, blank=True)
    current_trend_index = models.PositiveIntegerField(default=0)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_session_at = models.DateTimeField(null=True, blank=True)
    total_sessions = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = 'core'
        verbose_name = "Learning Companion"
        verbose_name_plural = "Learning Companions"

    def __str__(self):
        return f"Learning Companion for {self.user.username} - Track: {self.active_track}"

    def set_charter(self, charter_text):
        """Set the learning companion charter."""
        self.charter = charter_text
        self.charter_set_at = timezone.now()
        self.save(update_fields=['charter', 'charter_set_at', 'updated_at'])

    def start_session(self):
        """Mark a learning session as started."""
        self.last_session_at = timezone.now()
        self.total_sessions += 1
        self.save(update_fields=['last_session_at', 'total_sessions', 'updated_at'])


class LearningProgress(models.Model):
    """
    Session 266: Track learning progress through topics and trends.

    Records which topics have been covered, actions taken, and user engagement.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    companion = models.ForeignKey(
        LearningCompanion,
        on_delete=models.CASCADE,
        related_name='progress_entries'
    )

    # What was covered
    topic = models.CharField(max_length=200)
    trend_category = models.CharField(max_length=100, blank=True)
    content_summary = models.TextField(blank=True)

    # Progress status
    STATUS_CHOICES = [
        ('introduced', 'Introduced'),
        ('explored', 'Explored'),
        ('applied', 'Applied'),
        ('mastered', 'Mastered'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='introduced'
    )

    # Actions taken
    action_suggested = models.TextField(blank=True)
    action_completed = models.BooleanField(default=False)
    action_result = models.TextField(blank=True)

    # Engagement metrics
    time_spent_seconds = models.PositiveIntegerField(default=0)
    follow_up_questions = models.PositiveIntegerField(default=0)
    user_rating = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="User rating 1-5"
    )

    # Connections
    related_project_id = models.UUIDField(null=True, blank=True)
    spider_categories_used = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True
    )

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['companion', '-started_at']),
            models.Index(fields=['topic']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.topic} ({self.status})"

    def mark_completed(self, result=None):
        """Mark this learning item as completed."""
        self.completed_at = timezone.now()
        if result:
            self.action_result = result
        self.save(update_fields=['completed_at', 'action_result'])

    def advance_status(self):
        """Advance to the next status level."""
        status_order = ['introduced', 'explored', 'applied', 'mastered']
        current_idx = status_order.index(self.status)
        if current_idx < len(status_order) - 1:
            self.status = status_order[current_idx + 1]
            self.save(update_fields=['status'])


class TrackSpiderMapping(models.Model):
    """
    Session 266: Map learning tracks to relevant spider categories.

    When a user selects a track, this determines which spiders provide context.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    track = models.CharField(max_length=50)
    spider_category = models.CharField(max_length=50)
    relevance_weight = models.FloatField(
        default=1.0,
        help_text="How relevant this spider is for this track (0-2)"
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Is this a primary spider for this track?"
    )

    class Meta:
        app_label = 'core'
        unique_together = ['track', 'spider_category']
        ordering = ['track', '-relevance_weight']

    def __str__(self):
        primary = " (primary)" if self.is_primary else ""
        return f"{self.track} → {self.spider_category}{primary}"

    @classmethod
    def get_spiders_for_track(cls, track):
        """Get spider categories for a track, ordered by relevance."""
        mappings = cls.objects.filter(track=track).order_by('-relevance_weight')
        return [m.spider_category for m in mappings]

    @classmethod
    def seed_default_mappings(cls):
        """Seed default track-to-spider mappings."""
        defaults = {
            'tech_trends': [
                ('techcrunch', 1.5, True),
                ('theverge', 1.3, True),
                ('hackernews', 1.4, True),
                ('mit_tech_review', 1.2, False),
                ('wired', 1.0, False),
                ('producthunt', 0.8, False),
            ],
            'ai_design': [
                ('dribbble', 1.5, True),
                ('behance', 1.4, True),
                ('midjourney', 1.3, True),
                ('civitai', 1.2, False),
                ('runwayml', 1.1, False),
                ('figma', 1.0, False),
                ('canva', 0.9, False),
            ],
            'agentic_ai': [
                ('hackernews', 1.5, True),
                ('huggingface', 1.4, True),
                ('github_jobs', 1.2, False),
                ('kaggle', 1.1, False),
                ('devto', 1.0, False),
            ],
            'creative_ops': [
                ('notion', 1.3, True),
                ('figma', 1.2, True),
                ('producthunt', 1.1, False),
                ('dribbble', 1.0, False),
                ('behance', 0.9, False),
            ],
        }

        created_count = 0
        for track, spiders in defaults.items():
            for spider_cat, weight, is_primary in spiders:
                obj, created = cls.objects.get_or_create(
                    track=track,
                    spider_category=spider_cat,
                    defaults={
                        'relevance_weight': weight,
                        'is_primary': is_primary,
                    }
                )
                if created:
                    created_count += 1

        return created_count


# =============================================================================
# BUSINESS RESEARCH RESULT MODEL
# =============================================================================

class BusinessResearchResult(models.Model):
    """
    Session 294: Stores business research results from CustomerResearchAgent
    and CompetitorAnalysisAgent.

    Persists the GPT-synthesized reports so users can:
    - View historical research
    - Compare research across time
    - Export reports
    - Build upon previous research
    """

    RESEARCH_TYPE_CHOICES = [
        ('customer', 'Customer Research'),
        ('competitor', 'Competitor Analysis'),
        ('market', 'Market Research'),
        ('trend', 'Trend Analysis'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to project (optional - research can exist independently)
    # Session 324: Unified from CreativeProject
    project = models.ForeignKey(
        'core.PartnershipProject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='research_reports',
        help_text="Project this research is linked to"
    )

    # Market/topic for grouping related research
    market_topic = models.CharField(
        max_length=200,
        blank=True,
        help_text="Market or topic for grouping (e.g., 'AI content generation')"
    )

    # Research metadata
    research_type = models.CharField(
        max_length=20,
        choices=RESEARCH_TYPE_CHOICES,
        default='customer',
        help_text="Type of business research"
    )
    query = models.TextField(
        help_text="The original research query/request"
    )
    agent_name = models.CharField(
        max_length=100,
        help_text="Name of the agent that generated this research"
    )

    # The synthesized report (GPT-generated analysis)
    analysis = models.TextField(
        help_text="GPT-synthesized research report (markdown)"
    )

    # Structured data from the research
    data_points_analyzed = models.IntegerField(
        default=0,
        help_text="Number of data points analyzed"
    )
    sources_used = models.JSONField(
        default=list,
        help_text="List of data sources used (e.g., reddit, youtube, bluesky)"
    )

    # Raw data for reference
    raw_data = models.JSONField(
        default=list,
        help_text="Raw data points that were analyzed"
    )

    # Additional structured findings
    pain_points = models.JSONField(
        default=list,
        help_text="Extracted pain points"
    )
    personas = models.JSONField(
        default=list,
        help_text="Customer personas identified"
    )
    quotes = models.JSONField(
        default=list,
        help_text="Notable customer quotes"
    )
    recommendations = models.JSONField(
        default=list,
        help_text="Strategic recommendations"
    )

    # Execution metrics
    execution_time_ms = models.IntegerField(
        default=0,
        help_text="Time taken to generate this research (ms)"
    )

    # Embedding for semantic search
    # Session 730: Migrated to pgvector VectorField
    embedding = VectorField(
        dimensions=1536,
        null=True,
        blank=True,
        help_text="Vector embedding for semantic search (pgvector)"
    ) if HAS_PGVECTOR else models.JSONField(
        null=True,
        blank=True,
        help_text="Vector embedding (JSON fallback)"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        verbose_name = "Business Research Result"
        verbose_name_plural = "Business Research Results"
        indexes = [
            models.Index(fields=['research_type', 'created_at']),
            models.Index(fields=['agent_name']),
        ]

    def __str__(self):
        return f"{self.get_research_type_display()}: {self.query[:50]}... ({self.created_at.strftime('%Y-%m-%d')})"

    def generate_embedding(self):
        """Generate embedding for semantic search of this research."""
        try:
            from openai import OpenAI
            import os

            from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51 lazy
            client = get_openai_client(api_key=os.getenv('OPENAI_API_KEY'))

            # Create searchable text from query + analysis
            text_to_embed = f"{self.research_type}: {self.query}\n\n{self.analysis[:4000]}"

            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text_to_embed
            )

            self.embedding = response.data[0].embedding
            self.save(update_fields=['embedding'])
            return True

        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to generate embedding: {e}")
            return False

    @classmethod
    def save_customer_research(cls, query: str, synthesis: dict, execution_time_ms: int = 0, market_topic: str = '', project_id: str = None, user=None):
        """
        Helper to save CustomerResearchAgent results with embedding.

        Session 349: Added project_id parameter to link research to projects.
        Note: user parameter accepted but not used (model doesn't have user field).
        """
        # Extract market topic from query if not provided
        if not market_topic:
            market_topic = cls._extract_market_topic(query)

        # Session 349: Get project if project_id provided
        project = None
        if project_id:
            try:
                from core.models_partnership import PartnershipProject
                project = PartnershipProject.objects.get(id=project_id)
            except Exception as _e:
                logger.warning(
                    "models_unified_system.save_customer_research: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )

        instance = cls.objects.create(
            research_type='customer',
            query=query,
            agent_name='CustomerResearchAgent',
            market_topic=market_topic,
            analysis=synthesis.get('analysis', ''),
            data_points_analyzed=synthesis.get('data_points_analyzed', 0),
            sources_used=synthesis.get('sources_used', []),
            raw_data=synthesis.get('raw_data', []),
            pain_points=synthesis.get('pain_points', []),
            personas=synthesis.get('personas', []),
            quotes=synthesis.get('customer_quotes', []),
            recommendations=synthesis.get('recommendations', []),
            execution_time_ms=execution_time_ms,
            project=project,  # Session 349: Link to project
        )
        # Generate embedding for semantic search
        instance.generate_embedding()
        return instance

    @staticmethod
    def _extract_market_topic(query: str) -> str:
        """Extract market/topic from research query for grouping."""
        import re
        # Session 761: Fix for over-matching - exclude common words and require minimum topic length
        # Common non-topic words that should never be extracted as topics
        stopwords = {
            'one', 'two', 'three', 'four', 'five',  # Numbers
            'sentence', 'word', 'way', 'thing', 'time',  # Common nouns
            'it', 'this', 'that', 'each', 'all', 'any', 'some',  # Pronouns/determiners
            'ai', 'ml', 'api',  # Short tech acronyms (too generic)
            'is', 'are', 'was', 'were', 'be', 'been',  # Verbs
            'a', 'an', 'the',  # Articles
        }

        # Common patterns: "in the X market", "for X", "about X industry"
        # Session 761: Changed +? to + for greedy matching, added word boundary requirements
        patterns = [
            r'(?:in the|for|about|regarding)\s+(?:the\s+)?([^,\.]{3,})(?:\s+market|\s+industry|\s+space|\s+sector)',
            r'(?:competitors|competition|market|customers|pain points)\s+(?:in|for|of)\s+([^,\.]{3,})',
            r'(?:research(?:ing)?|analyz(?:e|ing)|study(?:ing)?)\s+(?:the\s+)?([^,\.]{3,})(?:\s+market|\s+industry)',
        ]
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                topic = match.group(1).strip()
                # Clean up common words
                topic = re.sub(r'^(the|a|an)\s+', '', topic)
                # Session 761: Skip single-word stopwords and very short topics
                if topic.lower() in stopwords or len(topic) < 3:
                    continue
                # Session 761: Require at least one real word (more than 3 chars)
                words = [w for w in topic.split() if len(w) > 3 and w.lower() not in stopwords]
                if not words:
                    continue
                return topic[:200]  # Limit length
        return ''

    @classmethod
    def save_competitor_analysis(cls, query: str, synthesis: dict, execution_time_ms: int = 0, market_topic: str = '', project_id: str = None, user=None):
        """
        Helper to save CompetitorAnalysisAgent results with embedding.

        Session 349: Added project_id parameter to link research to projects.
        Note: user parameter accepted but not used (model doesn't have user field).
        """
        # Extract market topic from query if not provided
        if not market_topic:
            market_topic = cls._extract_market_topic(query)

        # Session 349: Get project if project_id provided
        project = None
        if project_id:
            try:
                from core.models_partnership import PartnershipProject
                project = PartnershipProject.objects.get(id=project_id)
            except Exception as _e:
                logger.warning(
                    "models_unified_system.save_competitor_analysis: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )

        instance = cls.objects.create(
            research_type='competitor',
            query=query,
            agent_name='CompetitorAnalysisAgent',
            market_topic=market_topic,
            analysis=synthesis.get('analysis', ''),
            data_points_analyzed=synthesis.get('data_points_analyzed', 0),
            sources_used=list(set(
                item.get('source', '')
                for item in synthesis.get('raw_data', [])
                if item.get('source')
            )),
            raw_data=synthesis.get('raw_data', []),
            recommendations=synthesis.get('recommendations', []),
            execution_time_ms=execution_time_ms,
            project=project,  # Session 349: Link to project
        )
        # Generate embedding for semantic search
        instance.generate_embedding()
        return instance

    @classmethod
    def get_related_research(cls, market_topic: str, limit: int = 5):
        """Get all research related to a market topic."""
        return cls.objects.filter(
            market_topic__icontains=market_topic
        ).order_by('-created_at')[:limit]

    @classmethod
    def get_research_context_for_prompt(cls, query: str, limit: int = 3) -> str:
        """
        Get relevant research as context for image generation prompts.
        Uses semantic search to find the most relevant research.
        """
        results = cls.semantic_search(query, limit=limit)
        if not results:
            return ""

        context_parts = []
        for research, score in results:
            if score < 0.4:  # Skip low-relevance results
                continue

            context = f"\n### {research.get_research_type_display()} (relevance: {score:.0%})\n"

            if research.research_type == 'customer':
                if research.pain_points:
                    context += f"**Customer Pain Points:** {', '.join(research.pain_points[:5])}\n"
                if research.personas:
                    personas = research.personas[:2]
                    for p in personas:
                        if isinstance(p, dict):
                            context += f"**Target Customer:** {p.get('name', 'Unknown')} - {p.get('description', '')[:100]}\n"
            elif research.research_type == 'competitor':
                if research.recommendations:
                    context += f"**Market Gaps:** {', '.join(research.recommendations[:3])}\n"
                # Extract competitor names from analysis
                if 'differentiate' in research.analysis.lower():
                    context += f"**Differentiation Needed:** Stand out from existing players\n"

            context_parts.append(context)

        if context_parts:
            return "\n## Stored Research Intelligence\n" + "\n".join(context_parts)
        return ""

    @classmethod
    def semantic_search(cls, query: str, limit: int = 10, research_type: str = None):
        """Search research results using semantic similarity."""
        try:
            from openai import OpenAI
            import os
            import numpy as np

            from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51 lazy
            client = get_openai_client(api_key=os.getenv('OPENAI_API_KEY'))

            # Generate embedding for query
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            query_embedding = np.array(response.data[0].embedding)

            # Get all research with embeddings
            qs = cls.objects.exclude(embedding__isnull=True)
            if research_type:
                qs = qs.filter(research_type=research_type)

            # Calculate similarities
            results = []
            for research in qs:
                if research.embedding:
                    research_embedding = np.array(research.embedding)
                    # Cosine similarity
                    similarity = np.dot(query_embedding, research_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(research_embedding)
                    )
                    results.append((research, float(similarity)))

            # Sort by similarity and return top results
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]

        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Semantic search failed: {e}")
            return []


# =============================================================================
# Session 295: Content Provenance, Ethics Audit & Originality System
# =============================================================================
# Addresses customer pain points:
# - Gap #3: Provenance & Attribution (HIGH PRIORITY)
# - Gap #4: Bias & Ethics Transparency (MEDIUM PRIORITY)
# - Gap #2: AI Slop Differentiation (ENHANCEMENT)
# =============================================================================

class ContentProvenance(models.Model):
    """
    Session 295: Provenance & Attribution System

    Provides cryptographic proof of content creation, enabling:
    - Creator verification and ownership claims
    - Derivative tracking (who created variations)
    - Exportable certificates for licensing/legal purposes
    - Content fingerprinting for plagiarism detection
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to content
    content_type = models.CharField(
        max_length=20,
        choices=[
            ('image', 'Image'),
            ('video', 'Video'),
            ('audio', 'Audio'),
            ('3d_model', '3D Model'),
            ('text', 'Text/Document'),
        ],
        help_text="Type of content this provenance record covers"
    )

    # Session 492: Changed from PositiveBigIntegerField to UUIDField
    # because ImageHistory/VideoHistory/AudioHistory use UUID primary keys
    image_history_id = models.UUIDField(
        null=True, blank=True,
        help_text="Link to ImageHistory if content_type is image"
    )
    video_history_id = models.UUIDField(
        null=True, blank=True,
        help_text="Link to VideoHistory if content_type is video"
    )
    audio_history_id = models.UUIDField(
        null=True, blank=True,
        help_text="Link to AudioHistory if content_type is audio"
    )

    # Creator information
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='provenance_records',
        help_text="User who created this content"
    )

    # Cryptographic fingerprints
    content_hash = models.CharField(
        max_length=64,
        db_index=True,
        help_text="SHA-256 hash of the content bytes"
    )

    perceptual_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="Perceptual hash for similar-image detection (pHash)"
    )

    # Creation metadata
    created_at = models.DateTimeField(auto_now_add=True)

    generation_params = models.JSONField(
        default=dict,
        help_text="Complete generation parameters (prompt, model, style, seed)"
    )

    # Cryptographic signature
    signature = models.TextField(
        blank=True,
        help_text="Digital signature proving creation timestamp"
    )

    signature_algorithm = models.CharField(
        max_length=20,
        default='sha256_hmac',
        help_text="Algorithm used for signature"
    )

    # Derivative tracking
    parent_provenance = models.ForeignKey(
        'self',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='derivatives',
        help_text="Parent provenance if this is a derivative work"
    )

    derivative_type = models.CharField(
        max_length=30,
        blank=True,
        choices=[
            ('original', 'Original Creation'),
            ('edit', 'Edited Version'),
            ('upscale', 'Upscaled Version'),
            ('variation', 'Style Variation'),
            ('composite', 'Composite/Mashup'),
        ],
        default='original',
        help_text="Type of derivative relationship"
    )

    # Verification status
    is_verified = models.BooleanField(
        default=True,
        help_text="Whether this provenance record has been verified"
    )

    verification_timestamp = models.DateTimeField(
        null=True, blank=True,
        help_text="When the verification was performed"
    )

    # Certificate metadata
    certificate_issued = models.BooleanField(default=False)
    certificate_issued_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Content Provenance"
        verbose_name_plural = "Content Provenance Records"
        indexes = [
            models.Index(fields=['content_hash']),
            models.Index(fields=['creator', 'created_at']),
            models.Index(fields=['content_type', 'created_at']),
        ]

    def __str__(self):
        return f"{self.content_type} by {self.creator.username} ({self.content_hash[:12]}...)"

    @classmethod
    def create_for_image(cls, image_history, user, image_bytes: bytes, generation_params: dict = None):
        """
        Create a provenance record for an image.

        Args:
            image_history: The ImageHistory instance
            user: The creator user
            image_bytes: Raw bytes of the image for hashing
            generation_params: Dict with prompt, model, style, etc.
        """
        import hashlib
        import hmac
        import os
        from django.utils import timezone

        # Generate SHA-256 hash
        content_hash = hashlib.sha256(image_bytes).hexdigest()

        # Generate perceptual hash if imagehash available
        perceptual_hash = ''
        try:
            import imagehash
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(image_bytes))
            perceptual_hash = str(imagehash.phash(img))
        except ImportError:
            pass  # imagehash not installed

        # Create signature
        secret_key = os.getenv('PROVENANCE_SECRET_KEY', 'default-secret-key')
        timestamp = timezone.now().isoformat()
        message = f"{content_hash}:{user.id}:{timestamp}"
        signature = hmac.new(
            secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        # Check for parent (if image has parent_image)
        parent_provenance = None
        derivative_type = 'original'
        if hasattr(image_history, 'parent_image') and image_history.parent_image:
            parent_prov = cls.objects.filter(
                image_history_id=image_history.parent_image.id
            ).first()
            if parent_prov:
                parent_provenance = parent_prov
                derivative_type = 'edit'

        return cls.objects.create(
            content_type='image',
            image_history_id=image_history.id,
            creator=user,
            content_hash=content_hash,
            perceptual_hash=perceptual_hash,
            generation_params=generation_params or {},
            signature=signature,
            signature_algorithm='sha256_hmac',
            parent_provenance=parent_provenance,
            derivative_type=derivative_type,
            is_verified=True,
            verification_timestamp=timezone.now()
        )

    def generate_certificate(self) -> dict:
        """
        Generate an exportable certificate of provenance.

        Returns a dict that can be exported as JSON or PDF.
        """
        from django.utils import timezone

        certificate = {
            'certificate_id': str(self.id),
            'certificate_type': 'AI Content Provenance Certificate',
            'version': '1.0',
            'issued_at': timezone.now().isoformat(),
            'issued_by': 'Unified Donkey Betz AI Studio',

            'content': {
                'type': self.content_type,
                'sha256_hash': self.content_hash,
                'perceptual_hash': self.perceptual_hash or None,
                'created_at': self.created_at.isoformat(),
            },

            'creator': {
                'username': self.creator.username,
                'user_id': str(self.creator.id),
            },

            'generation': {
                'prompt': self.generation_params.get('prompt', ''),
                'model': self.generation_params.get('model', ''),
                'style': self.generation_params.get('style', ''),
                'parameters': {k: v for k, v in self.generation_params.items()
                              if k not in ['prompt', 'model', 'style']}
            },

            'lineage': {
                'derivative_type': self.derivative_type,
                'parent_certificate': str(self.parent_provenance.id) if self.parent_provenance else None,
            },

            'verification': {
                'signature': self.signature,
                'algorithm': self.signature_algorithm,
                'verified': self.is_verified,
                'verified_at': self.verification_timestamp.isoformat() if self.verification_timestamp else None,
            }
        }

        # Mark certificate as issued
        self.certificate_issued = True
        self.certificate_issued_at = timezone.now()
        self.save(update_fields=['certificate_issued', 'certificate_issued_at'])

        return certificate

    @classmethod
    def find_by_hash(cls, content_hash: str):
        """Find provenance records by content hash (exact match)."""
        return cls.objects.filter(content_hash=content_hash)

    @classmethod
    def find_similar(cls, perceptual_hash: str, threshold: int = 10):
        """
        Find similar images by perceptual hash.

        Uses Hamming distance - images with distance < threshold are similar.
        Requires imagehash library.
        """
        try:
            import imagehash
            target_hash = imagehash.hex_to_hash(perceptual_hash)

            similar = []
            for prov in cls.objects.exclude(perceptual_hash=''):
                try:
                    prov_hash = imagehash.hex_to_hash(prov.perceptual_hash)
                    distance = target_hash - prov_hash
                    if distance < threshold:
                        similar.append((prov, distance))
                except Exception:
                    continue

            similar.sort(key=lambda x: x[1])
            return similar
        except ImportError:
            return []


class ContentAuditResult(models.Model):
    """
    Session 295: Bias & Ethics Transparency System

    Records audit results for generated content, including:
    - Bias detection (gender, racial, cultural)
    - Safety/ethics checks
    - Transparency cards for users
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to provenance
    provenance = models.ForeignKey(
        ContentProvenance,
        on_delete=models.CASCADE,
        related_name='audits',
        help_text="Provenance record being audited"
    )

    # Audit metadata
    audited_at = models.DateTimeField(auto_now_add=True)
    audit_version = models.CharField(max_length=10, default='1.0')

    # Safety scores (0-100, higher = safer)
    overall_safety_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall safety score (0-100)"
    )

    # Bias detection
    bias_detected = models.BooleanField(default=False)
    bias_categories = models.JSONField(
        default=list,
        help_text="List of detected bias categories"
    )
    bias_details = models.TextField(
        blank=True,
        help_text="Detailed explanation of detected biases"
    )

    # Ethics flags
    ethics_flags = models.JSONField(
        default=list,
        help_text="Ethical concerns flagged"
    )

    # Representation analysis
    representation_analysis = models.JSONField(
        default=dict,
        help_text="Analysis of representation in content"
    )

    # Prompt analysis
    prompt_safety_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=100,
        help_text="Safety score of the input prompt"
    )
    prompt_suggestions = models.JSONField(
        default=list,
        help_text="Suggested prompt modifications for less bias"
    )

    # Model transparency
    model_known_biases = models.JSONField(
        default=list,
        help_text="Known biases of the model used"
    )

    # Recommendations
    recommendations = models.JSONField(
        default=list,
        help_text="Recommendations for creator"
    )

    class Meta:
        app_label = 'core'
        verbose_name = "Content Audit Result"
        verbose_name_plural = "Content Audit Results"
        ordering = ['-audited_at']

    def __str__(self):
        return f"Audit for {self.provenance_id} (score: {self.overall_safety_score})"

    def generate_transparency_card(self) -> dict:
        """Generate a user-friendly transparency card."""
        return {
            'safety_score': self.overall_safety_score,
            'safety_level': 'high' if self.overall_safety_score >= 80 else
                           'medium' if self.overall_safety_score >= 50 else 'low',
            'bias_detected': self.bias_detected,
            'bias_summary': self.bias_categories if self.bias_detected else [],
            'ethics_concerns': len(self.ethics_flags),
            'prompt_quality': self.prompt_safety_score,
            'suggestions': self.prompt_suggestions[:3],  # Top 3 suggestions
            'recommendations': self.recommendations[:3],
            'model_notes': self.model_known_biases[:2] if self.model_known_biases else [],
        }


class OriginalityScore(models.Model):
    """
    Session 295: AI Slop Differentiation System

    Helps creators stand out by:
    - Comparing against trending patterns
    - Scoring uniqueness vs generic AI output
    - Suggesting differentiation strategies
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to provenance
    provenance = models.ForeignKey(
        ContentProvenance,
        on_delete=models.CASCADE,
        related_name='originality_scores',
        help_text="Provenance record being scored"
    )

    # Scoring
    scored_at = models.DateTimeField(auto_now_add=True)

    overall_originality = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall originality score (0-100, higher = more original)"
    )

    # Breakdown scores
    prompt_originality = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=50,
        help_text="How unique is the prompt compared to common prompts"
    )

    style_originality = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=50,
        help_text="How unique is the style choice"
    )

    composition_originality = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=50,
        help_text="How unique is the composition/layout"
    )

    # Trend comparison
    trend_similarity = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=50,
        help_text="How similar to current trending content (higher = more similar)"
    )

    trending_elements_used = models.JSONField(
        default=list,
        help_text="List of trending elements found in this content"
    )

    # Anti-patterns detected
    generic_patterns_detected = models.JSONField(
        default=list,
        help_text="Generic AI patterns detected (e.g., 'smooth skin', 'perfect lighting')"
    )

    # Recommendations
    differentiation_suggestions = models.JSONField(
        default=list,
        help_text="Suggestions to make content more unique"
    )

    alternative_prompts = models.JSONField(
        default=list,
        help_text="Alternative prompt suggestions for more originality"
    )

    # Market comparison
    similar_content_count = models.IntegerField(
        default=0,
        help_text="Estimated number of similar AI-generated content"
    )

    uniqueness_percentile = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=50,
        help_text="Percentile ranking (100 = most unique)"
    )

    class Meta:
        app_label = 'core'
        verbose_name = "Originality Score"
        verbose_name_plural = "Originality Scores"
        ordering = ['-scored_at']

    def __str__(self):
        return f"Originality {self.overall_originality}/100 for {self.provenance_id}"

    def get_summary(self) -> dict:
        """Get a summary of originality analysis."""
        return {
            'overall_score': self.overall_originality,
            'breakdown': {
                'prompt': self.prompt_originality,
                'style': self.style_originality,
                'composition': self.composition_originality,
            },
            'trend_similarity': self.trend_similarity,
            'uniqueness_percentile': self.uniqueness_percentile,
            'issues': self.generic_patterns_detected[:5],
            'suggestions': self.differentiation_suggestions[:5],
            'verdict': self._get_verdict()
        }

    def _get_verdict(self) -> str:
        """Generate a human-readable verdict."""
        if self.overall_originality >= 80:
            return "Highly Original - Your content stands out!"
        elif self.overall_originality >= 60:
            return "Moderately Original - Some unique elements"
        elif self.overall_originality >= 40:
            return "Average - Consider differentiation suggestions"
        else:
            return "Generic - High risk of 'AI slop' perception"


# =============================================================================
# Session 319: Agent Slack - Multi-Agent Channel Communication
# =============================================================================

class AgentChannel(models.Model):
    """
    A Slack-like channel where multiple agents can collaborate.

    Channels are topic-based rooms where agents can join, share knowledge,
    and work together on projects. Each channel has a purpose and can be
    linked to specific projects or workflows.

    Session 319: Building internal Slack for AI agents.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Channel identity
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Channel name (e.g., #brand-strategy, #content-creation)"
    )

    description = models.TextField(
        blank=True,
        help_text="What this channel is for"
    )

    # Channel type
    channel_type = models.CharField(
        max_length=30,
        choices=[
            ('project', 'Project Channel'),        # Linked to a specific project
            ('topic', 'Topic Channel'),            # General topic discussion
            ('workflow', 'Workflow Channel'),      # For workflow coordination
            ('team', 'Team Channel'),              # Team of agents
            ('announcement', 'Announcements'),     # Read-only for most
            ('emergency', 'Emergency Response'),   # High-priority issues
        ],
        default='topic'
    )

    # Optional project link
    project_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="Associated project ID (if project channel)"
    )

    # Channel owner/creator
    created_by = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_channels',
        help_text="Agent that created this channel"
    )

    # Channel settings
    is_public = models.BooleanField(
        default=True,
        help_text="Whether any agent can join"
    )

    is_archived = models.BooleanField(
        default=False,
        help_text="Archived channels are read-only"
    )

    auto_invite_types = models.JSONField(
        default=list,
        help_text="Agent types to auto-invite (e.g., ['strategy', 'creative'])"
    )

    # Metadata
    topic = models.CharField(
        max_length=200,
        blank=True,
        help_text="Current channel topic/focus"
    )

    pinned_messages = models.JSONField(
        default=list,
        help_text="List of pinned message IDs"
    )

    # Metrics
    message_count = models.IntegerField(default=0)
    member_count = models.IntegerField(default=0)
    last_activity = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        ordering = ['-last_activity', '-created_at']
        verbose_name = "Agent Channel"
        verbose_name_plural = "Agent Channels"

    def __str__(self):
        return f"#{self.name}"

    def get_members(self):
        """Get all agents in this channel."""
        return Agent.objects.filter(
            channel_memberships__channel=self,
            channel_memberships__is_active=True
        )

    def get_recent_messages(self, limit=50):
        """Get recent messages from this channel."""
        return self.channel_messages.order_by('-created_at')[:limit]

    def add_member(self, agent, role='member'):
        """Add an agent to this channel."""
        membership, created = ChannelMembership.objects.get_or_create(
            channel=self,
            agent=agent,
            defaults={'role': role}
        )
        if created:
            self.member_count += 1
            self.save(update_fields=['member_count'])
        return membership

    def remove_member(self, agent):
        """Remove an agent from this channel."""
        removed = ChannelMembership.objects.filter(
            channel=self,
            agent=agent
        ).update(is_active=False)
        if removed:
            self.member_count = max(0, self.member_count - 1)
            self.save(update_fields=['member_count'])


class ChannelMembership(models.Model):
    """
    Tracks which agents are members of which channels.

    Similar to Slack's channel membership, with roles and preferences.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    channel = models.ForeignKey(
        AgentChannel,
        on_delete=models.CASCADE,
        related_name='memberships'
    )

    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='channel_memberships'
    )

    # Membership role
    role = models.CharField(
        max_length=20,
        choices=[
            ('owner', 'Channel Owner'),
            ('admin', 'Channel Admin'),
            ('member', 'Member'),
            ('guest', 'Guest'),
        ],
        default='member'
    )

    # Status
    is_active = models.BooleanField(default=True)
    is_muted = models.BooleanField(default=False)

    # Engagement metrics
    messages_sent = models.IntegerField(default=0)
    last_read_at = models.DateTimeField(null=True, blank=True)
    last_posted_at = models.DateTimeField(null=True, blank=True)

    # Agent presence (for UI)
    presence_status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('idle', 'Idle'),
            ('away', 'Away'),
            ('dnd', 'Do Not Disturb'),
        ],
        default='active'
    )

    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        unique_together = ['channel', 'agent']
        verbose_name = "Channel Membership"
        verbose_name_plural = "Channel Memberships"

    def __str__(self):
        return f"{self.agent.name} in #{self.channel.name}"


class ChannelMessage(models.Model):
    """
    A message posted in an agent channel.

    Similar to Slack messages with threading, reactions, and mentions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    channel = models.ForeignKey(
        AgentChannel,
        on_delete=models.CASCADE,
        related_name='channel_messages'
    )

    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='channel_posts'
    )

    # Message content
    content = models.TextField(
        help_text="The message text"
    )

    message_type = models.CharField(
        max_length=30,
        choices=[
            ('message', 'Regular Message'),
            ('insight', 'Insight'),
            ('question', 'Question'),
            ('answer', 'Answer'),
            ('announcement', 'Announcement'),
            ('action_item', 'Action Item'),
            ('decision', 'Decision Made'),
            ('summary', 'Summary'),
            ('system', 'System Message'),
        ],
        default='message'
    )

    # Threading
    thread_parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='thread_replies'
    )

    reply_count = models.IntegerField(default=0)

    # Mentions (@agent references)
    mentioned_agents = models.ManyToManyField(
        Agent,
        related_name='channel_mentions',
        blank=True
    )

    # Reactions (emoji-style)
    reactions = models.JSONField(
        default=dict,
        help_text="Reactions from agents: {'emoji': ['agent_id1', 'agent_id2']}"
    )

    # Knowledge references
    referenced_knowledge = models.JSONField(
        default=list,
        help_text="List of AgentKnowledgeSource IDs referenced"
    )

    # Attachments (artifacts, files, etc.)
    attachments = models.JSONField(
        default=list,
        help_text="List of attachment metadata"
    )

    # Edit tracking
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)

    # Pinned/highlighted
    is_pinned = models.BooleanField(default=False)

    # Quality metrics
    relevance_score = models.FloatField(
        default=0.8,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="How relevant/useful was this message"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['created_at']
        verbose_name = "Channel Message"
        verbose_name_plural = "Channel Messages"
        indexes = [
            models.Index(fields=['channel', 'created_at']),
            models.Index(fields=['agent', 'created_at']),
            models.Index(fields=['thread_parent']),
        ]

    def __str__(self):
        return f"{self.agent.name} in #{self.channel.name}: {self.content[:50]}..."

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Update channel metrics on new message
        if is_new:
            self.channel.message_count += 1
            self.channel.last_activity = timezone.now()
            self.channel.save(update_fields=['message_count', 'last_activity'])

            # Update membership metrics
            ChannelMembership.objects.filter(
                channel=self.channel,
                agent=self.agent
            ).update(
                messages_sent=models.F('messages_sent') + 1,
                last_posted_at=timezone.now()
            )

            # Update thread parent reply count
            if self.thread_parent:
                ChannelMessage.objects.filter(pk=self.thread_parent.pk).update(
                    reply_count=models.F('reply_count') + 1
                )

    def add_reaction(self, agent, emoji):
        """Add an emoji reaction from an agent."""
        if emoji not in self.reactions:
            self.reactions[emoji] = []
        agent_id = str(agent.id)
        if agent_id not in self.reactions[emoji]:
            self.reactions[emoji].append(agent_id)
            self.save(update_fields=['reactions'])

    def remove_reaction(self, agent, emoji):
        """Remove an emoji reaction."""
        if emoji in self.reactions:
            agent_id = str(agent.id)
            if agent_id in self.reactions[emoji]:
                self.reactions[emoji].remove(agent_id)
                if not self.reactions[emoji]:
                    del self.reactions[emoji]
                self.save(update_fields=['reactions'])

    def get_thread(self):
        """Get all replies to this message."""
        return ChannelMessage.objects.filter(thread_parent=self).order_by('created_at')

    def parse_mentions(self):
        """Parse @agent mentions from content and link them."""
        import re
        mentions = re.findall(r'@(\w+)', self.content)
        if mentions:
            agents = Agent.objects.filter(name__in=mentions)
            self.mentioned_agents.set(agents)


# =============================================================================
# Session 323: Boardroom Decisions (REMOVED - Duplicate of Session 412 version)
# See Session 412 version below for the canonical AgentDecisionSummary model
# =============================================================================


# =============================================================================
# SESSION 326: PROJECT-AGENT LEARNING BRIDGE MODELS
# =============================================================================

class ProjectResearchFeedback(models.Model):
    """
    Session 326: Track user feedback on research results.

    This enables:
    1. Accept/reject tracking per research item
    2. Confidence score adjustment in AgentKnowledgeSource
    3. Pattern learning for agent improvement

    Flow:
    - User reviews research in project
    - Clicks Accept/Reject/Rate
    - System adjusts agent knowledge confidence
    - Future research incorporates learning
    """

    FEEDBACK_TYPE_CHOICES = [
        ('accept', 'Accepted - Useful'),
        ('reject', 'Rejected - Not Useful'),
        ('partial', 'Partially Useful'),
        ('starred', 'Starred - Excellent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to project and research
    project = models.ForeignKey(
        'core.PartnershipProject',
        on_delete=models.CASCADE,
        related_name='research_feedback'
    )
    research = models.ForeignKey(
        'core.BusinessResearchResult',
        on_delete=models.CASCADE,
        related_name='feedback',
        null=True,
        blank=True,
        help_text="Specific research result this feedback applies to"
    )

    # User who gave feedback
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='research_feedback'
    )

    # Feedback content
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPE_CHOICES,
        default='accept'
    )
    rating = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1-5 star rating"
    )
    reason = models.TextField(
        blank=True,
        help_text="Why was this research useful/not useful?"
    )

    # What part of research was feedback about
    feedback_context = models.JSONField(
        default=dict,
        help_text="Context: {section: 'competitors', item: 'Jasper AI', reason: 'outdated'}"
    )

    # Learning impact
    applied_to_knowledge = models.BooleanField(
        default=False,
        help_text="Has this feedback been applied to agent knowledge?"
    )
    knowledge_delta = models.FloatField(
        default=0.0,
        help_text="Confidence adjustment made (-1 to +1)"
    )
    affected_knowledge_ids = ArrayField(
        models.UUIDField(),
        default=list,
        help_text="IDs of AgentKnowledgeSource entries affected by this feedback"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'feedback_type']),
            models.Index(fields=['research']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.feedback_type} on {self.project.project_name}"

    def apply_to_knowledge(self):
        """Apply this feedback to related AgentKnowledgeSource entries."""
        from core.models_unified_system import AgentKnowledgeSource

        # Find knowledge derived from this project
        related_knowledge = AgentKnowledgeSource.objects.filter(
            source_project=self.project,
            is_active=True
        )

        if self.research:
            related_knowledge = related_knowledge.filter(source_research=self.research)

        affected_ids = []
        is_positive = self.feedback_type in ('accept', 'starred')

        # Calculate delta based on rating and feedback type
        if self.feedback_type == 'starred':
            delta = 0.2
        elif self.feedback_type == 'accept':
            delta = 0.1 * (self.rating / 5)  # Scale by rating
        elif self.feedback_type == 'partial':
            delta = 0.05 * ((self.rating - 3) / 2)  # Slight adjustment
        else:  # reject
            delta = -0.15 * ((6 - self.rating) / 5)  # Stronger negative for low ratings

        for knowledge in related_knowledge:
            knowledge.apply_feedback(is_positive, abs(delta))
            affected_ids.append(knowledge.id)

        self.affected_knowledge_ids = affected_ids
        self.knowledge_delta = delta
        self.applied_to_knowledge = True
        self.save()

        return len(affected_ids)


class ProjectSpiderPriority(models.Model):
    """
    Session 326: Link projects to spider categories for prioritization.

    Active projects influence spider crawling priorities:
    - Projects with 'AI content' topic -> prioritize tech/AI spiders
    - Projects with 'coffee roasting' -> prioritize business/market spiders

    Spider priority is calculated based on:
    1. Number of active projects with matching topics
    2. Recency of project activity
    3. Explicit user priority settings
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to project
    project = models.ForeignKey(
        'core.PartnershipProject',
        on_delete=models.CASCADE,
        related_name='spider_priorities'
    )

    # Spider category to prioritize
    spider_category = models.ForeignKey(
        'core.SpiderCategory',
        on_delete=models.CASCADE,
        related_name='project_priorities'
    )

    # Priority settings
    priority_weight = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.1), MaxValueValidator(10.0)],
        help_text="Weight multiplier for this category (1.0 = normal)"
    )

    # Topic matching
    matched_keywords = ArrayField(
        models.CharField(max_length=100),
        default=list,
        help_text="Keywords that matched this project to this category"
    )

    # Effectiveness tracking
    data_used_count = models.IntegerField(
        default=0,
        help_text="How many spider data points were used from this category"
    )
    useful_data_count = models.IntegerField(
        default=0,
        help_text="How many were marked useful by user feedback"
    )

    is_auto_detected = models.BooleanField(
        default=True,
        help_text="Was this priority auto-detected from project content?"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        unique_together = ['project', 'spider_category']
        ordering = ['-priority_weight']

    def __str__(self):
        return f"{self.project.project_name} -> {self.spider_category.name} (weight: {self.priority_weight})"

    @property
    def effectiveness_score(self):
        """Calculate how effective this priority has been."""
        if self.data_used_count == 0:
            return 0.5  # Neutral
        return self.useful_data_count / self.data_used_count

    def record_data_usage(self, was_useful: bool):
        """Record that data from this category was used."""
        self.data_used_count += 1
        if was_useful:
            self.useful_data_count += 1
        self.save()


# =============================================================================
# Session 335: LIVING PROJECT SYSTEM
# =============================================================================
# Projects that autonomously learn from the agent ecosystem.
# Connects spider data, agent conversations, and decisions TO user projects.
# =============================================================================

class ProjectInsight(models.Model):
    """
    An insight surfaced to a project from the agent ecosystem.

    This is the bridge between:
    - Spider data collection
    - Agent learning/conversations
    - Agent decisions
    AND user projects.

    Session 335: Living Projects - Projects that learn autonomously
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # The project this insight belongs to
    project = models.ForeignKey(
        'core.PartnershipProject',
        on_delete=models.CASCADE,
        related_name='insights'
    )

    # What type of insight is this?
    insight_type = models.CharField(max_length=50, choices=[
        ('spider_data', 'Spider Data'),           # New relevant data from spiders
        ('competitor', 'Competitor Alert'),        # New/changed competitor detected
        ('trend', 'Market Trend'),                 # Trending topic in project's domain
        ('pain_point', 'Pain Point'),              # Customer pain point discovered
        ('opportunity', 'Opportunity'),            # New opportunity identified
        ('agent_insight', 'Agent Insight'),        # From agent conversation
        ('decision', 'Decision'),                  # From canonical decision
        ('dream', 'Creative Idea'),                # From agent dream (if revived)
        ('learning', 'Learning'),                  # From agent learning transfer
    ])

    # The content
    title = models.CharField(max_length=300)
    summary = models.TextField()
    details = models.JSONField(default=dict)  # Full data for drill-down

    # Source tracking
    source_type = models.CharField(max_length=50, choices=[
        ('spider', 'Spider Network'),
        ('agent_conversation', 'Agent Conversation'),
        ('agent_decision', 'Agent Decision'),
        ('agent_learning', 'Agent Learning'),
        ('agent_dream', 'Agent Dream'),
        ('user_research', 'User Research'),
        ('system', 'System Generated'),
    ])
    source_id = models.UUIDField(null=True, blank=True)  # ID of source record
    source_name = models.CharField(max_length=200, blank=True)  # Human-readable source

    # Relevance scoring
    relevance_score = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="How relevant is this to the project (0-1)"
    )
    confidence_score = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="How confident are we in this insight (0-1)"
    )

    # Topic matching (why this was matched to project)
    matched_topics = models.JSONField(
        default=list,
        help_text="Which project topics triggered this match"
    )

    # Status
    status = models.CharField(max_length=20, choices=[
        ('new', 'New'),
        ('seen', 'Seen'),
        ('acted_on', 'Acted On'),
        ('dismissed', 'Dismissed'),
        ('archived', 'Archived'),
    ], default='new')

    # User interaction
    is_pinned = models.BooleanField(default=False)
    user_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="User's rating of this insight (1-5)"
    )
    user_notes = models.TextField(blank=True)

    # Actions taken
    actions_taken = models.JSONField(
        default=list,
        help_text="Actions user took based on this insight"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    seen_at = models.DateTimeField(null=True, blank=True)
    acted_on_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['project', 'insight_type']),
            models.Index(fields=['project', '-created_at']),
            models.Index(fields=['source_type', 'source_id']),
        ]

    def __str__(self):
        return f"[{self.insight_type}] {self.title[:50]}..."

    def mark_seen(self):
        """Mark this insight as seen."""
        if self.status == 'new':
            self.status = 'seen'
            self.seen_at = timezone.now()
            self.save()

    def mark_acted_on(self, action_description: str = None):
        """Mark this insight as acted on."""
        self.status = 'acted_on'
        self.acted_on_at = timezone.now()
        if action_description:
            self.actions_taken.append({
                'action': action_description,
                'timestamp': timezone.now().isoformat()
            })
        self.save()

    def dismiss(self, reason: str = None):
        """Dismiss this insight."""
        self.status = 'dismissed'
        if reason:
            self.user_notes = reason
        self.save()

    def rate(self, rating: int, notes: str = None):
        """Rate this insight."""
        self.user_rating = rating
        if notes:
            self.user_notes = notes
        self.save()


class LivingProjectConfig(models.Model):
    """
    Configuration for a project's autonomous learning behavior.

    Defines what the project "pays attention to" and how
    aggressively it surfaces insights.

    Session 335: Living Projects
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # One config per project
    project = models.OneToOneField(
        'core.PartnershipProject',
        on_delete=models.CASCADE,
        related_name='living_config'
    )

    # Is this project "alive"?
    is_active = models.BooleanField(
        default=True,
        help_text="Is this project actively learning?"
    )

    # Topic configuration (what to watch for)
    watch_topics = models.JSONField(
        default=list,
        help_text="Topics to monitor across the ecosystem"
    )
    watch_competitors = models.JSONField(
        default=list,
        help_text="Competitor names to track"
    )
    watch_keywords = models.JSONField(
        default=list,
        help_text="Keywords to watch for in spider data"
    )

    # Source configuration (where to look)
    enabled_sources = models.JSONField(
        default=list,  # Will default to [] but we handle defaults in code
        help_text="Which sources to pull insights from"
    )
    spider_categories = models.JSONField(
        default=list,
        help_text="Which spider categories to prioritize"
    )

    # Thresholds (when to surface)
    min_relevance_score = models.FloatField(
        default=0.6,
        help_text="Minimum relevance score to surface insight"
    )
    min_confidence_score = models.FloatField(
        default=0.5,
        help_text="Minimum confidence score to surface insight"
    )

    # Notification preferences
    notify_on_competitor = models.BooleanField(default=True)
    notify_on_opportunity = models.BooleanField(default=True)
    notify_on_trend = models.BooleanField(default=True)
    max_daily_insights = models.IntegerField(
        default=10,
        help_text="Maximum insights to surface per day"
    )

    # Learning preferences
    auto_expand_topics = models.BooleanField(
        default=True,
        help_text="Automatically add related topics based on insights"
    )
    learn_from_ratings = models.BooleanField(
        default=True,
        help_text="Adjust relevance scoring based on user ratings"
    )

    # Stats
    total_insights_surfaced = models.IntegerField(default=0)
    total_insights_acted_on = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_insight_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'

    def __str__(self):
        status = "🟢 Active" if self.is_active else "⚪ Inactive"
        return f"{self.project.project_name} - {status}"

    @property
    def effectiveness_rate(self):
        """What percentage of insights were acted on?"""
        if self.total_insights_surfaced == 0:
            return 0.0
        return self.total_insights_acted_on / self.total_insights_surfaced

    def record_insight(self, was_acted_on: bool = False, rating: int = None):
        """Record insight metrics."""
        self.total_insights_surfaced += 1
        if was_acted_on:
            self.total_insights_acted_on += 1
        if rating:
            # Running average
            current_total = self.average_rating * (self.total_insights_surfaced - 1)
            self.average_rating = (current_total + rating) / self.total_insights_surfaced
        self.last_insight_at = timezone.now()
        self.save()


# =============================================================================
# SESSION 388: INCOME ACTION PIPELINE
# =============================================================================

class SavedOpportunity(models.Model):
    """
    Session 388: User-saved opportunities from spider data.

    This is the ACTION layer between spider discovery and income:
    1. User sees opportunity in Intelligence Tab
    2. User clicks "Save & Apply"
    3. System saves here with source URL for deduplication
    4. System generates application materials (cover letter/proposal)
    5. User applies externally
    6. User records outcome (accepted/rejected/no_response)
    7. System learns from outcomes
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_opportunities'
    )

    # Opportunity details (from spider data)
    title = models.CharField(max_length=200)
    source_url = models.URLField(max_length=500, blank=True)
    source_platform = models.CharField(max_length=50)  # reddit, weworkremotely, adzuna, etc.
    description = models.TextField(blank=True)
    salary_info = models.CharField(max_length=200, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=100, default='Remote')
    category = models.CharField(max_length=50, default='general')  # freelance, remote_job, crowdfunding, etc.

    # Raw spider data for reference
    raw_data = models.JSONField(default=dict)

    # Generated application materials
    application_materials = models.JSONField(default=dict, blank=True)
    # Structure: {'cover_letter': '...', 'proposal': '...', 'generated_at': '...'}

    # Status tracking
    STATUS_CHOICES = [
        ('saved', 'Saved'),
        ('materials_ready', 'Materials Ready'),
        ('applied', 'Applied'),
        ('interview', 'Interview'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('no_response', 'No Response'),
        ('withdrawn', 'Withdrawn'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='saved')
    notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    applied_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Link to full Opportunity model if converted
    opportunity = models.ForeignKey(
        'Opportunity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='saved_source'
    )

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['source_url']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.status})"

    def mark_applied(self):
        """Mark as applied and record timestamp."""
        self.status = 'applied'
        self.applied_at = timezone.now()
        self.save()

    def mark_outcome(self, outcome: str, notes: str = None):
        """Record final outcome (accepted/rejected/no_response)."""
        if outcome in ['accepted', 'rejected', 'no_response']:
            self.status = outcome
            self.resolved_at = timezone.now()
            if notes:
                self.notes = f"{self.notes}\n[{timezone.now().isoformat()}] {notes}".strip()
            self.save()

            # If accepted, create full Opportunity record
            if outcome == 'accepted':
                self._create_opportunity_record()

    def _create_opportunity_record(self):
        """Create full Opportunity when accepted."""
        if not self.opportunity:
            self.opportunity = Opportunity.objects.create(
                user=self.user,
                title=self.title,
                opportunity_type=self.category,
                source=self.source_platform,
                potential_revenue=Decimal('0.00'),  # User can update
                status='accepted',
                description=self.description,
                metadata={
                    'saved_opportunity_id': str(self.id),
                    'source_url': self.source_url,
                    'applied_at': self.applied_at.isoformat() if self.applied_at else None,
                }
            )
            self.save()


# =============================================================================
# Session 403: Legal Assistant Models
# Pro Se Legal Assistant for Colorado Family Law
# =============================================================================

class LegalCase(models.Model):
    """
    Session 403: Represents a user's legal case.
    Stores case information for the Pro Se Legal Assistant.

    Focus: Colorado family law (divorce, custody, child support, parenting time)
    """

    CASE_TYPE_CHOICES = [
        ('divorce', 'Divorce/Dissolution'),
        ('custody', 'Custody (Allocation of Parental Responsibilities)'),
        ('child_support', 'Child Support'),
        ('parenting_time', 'Parenting Time/Visitation'),
        ('modification', 'Modification of Existing Order'),
        ('enforcement', 'Enforcement of Existing Order'),
        ('paternity', 'Paternity/Parentage'),
        ('protection', 'Protection Order'),
        ('other', 'Other Family Law Matter'),
    ]

    CASE_STATUS_CHOICES = [
        ('planning', 'Planning/Research'),
        ('filing', 'Ready to File'),
        ('filed', 'Filed with Court'),
        ('pending', 'Pending/In Progress'),
        ('hearing_scheduled', 'Hearing Scheduled'),
        ('resolved', 'Resolved/Closed'),
        ('appealing', 'Appealing'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='legal_cases'
    )

    # Case identification
    case_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Court case number (if filed)"
    )
    court = models.CharField(
        max_length=200,
        blank=True,
        help_text="Court name (e.g., 'Denver District Court')"
    )
    county = models.CharField(
        max_length=100,
        blank=True,
        help_text="County where case is filed"
    )
    jurisdiction = models.CharField(
        max_length=50,
        default='Colorado',
        help_text="State/jurisdiction"
    )

    # Case details
    case_type = models.CharField(
        max_length=20,
        choices=CASE_TYPE_CHOICES,
        default='divorce'
    )
    case_status = models.CharField(
        max_length=20,
        choices=CASE_STATUS_CHOICES,
        default='planning'
    )
    title = models.CharField(
        max_length=200,
        help_text="Brief case title (e.g., 'Smith v. Smith Divorce')"
    )
    description = models.TextField(
        blank=True,
        help_text="Case summary and notes"
    )

    # Parties
    parties = models.JSONField(
        default=dict,
        help_text="Parties involved: {petitioner: {name, role}, respondent: {name, role}, children: [...]}"
    )

    # Key dates
    key_dates = models.JSONField(
        default=dict,
        help_text="Important dates: {filing_date, service_date, hearing_dates: [], deadlines: []}"
    )

    # Related documents count (denormalized for performance)
    document_count = models.IntegerField(default=0)
    research_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        ordering = ['-updated_at']
        verbose_name = "Legal Case"
        verbose_name_plural = "Legal Cases"
        indexes = [
            models.Index(fields=['user', 'case_status']),
            models.Index(fields=['case_type']),
            models.Index(fields=['jurisdiction']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_case_type_display()})"

    def add_key_date(self, date_type: str, date_value, description: str = ''):
        """Add a key date to the case."""
        if not self.key_dates:
            self.key_dates = {}

        if date_type == 'deadline':
            if 'deadlines' not in self.key_dates:
                self.key_dates['deadlines'] = []
            self.key_dates['deadlines'].append({
                'date': str(date_value),
                'description': description
            })
        elif date_type == 'hearing':
            if 'hearing_dates' not in self.key_dates:
                self.key_dates['hearing_dates'] = []
            self.key_dates['hearing_dates'].append({
                'date': str(date_value),
                'description': description
            })
        else:
            self.key_dates[date_type] = str(date_value)

        self.save(update_fields=['key_dates', 'updated_at'])


class LegalDocument(models.Model):
    """
    Session 403: Generated legal documents for a case.
    Stores motions, emails, declarations, and other documents drafted by LegalDocDrafterAgent.
    """

    DOCUMENT_TYPE_CHOICES = [
        ('motion', 'Motion'),
        ('email', 'Meet-and-Confer Email'),
        ('declaration', 'Declaration'),
        ('checklist', 'Procedure Checklist'),
        ('response', 'Response to Motion'),
        ('petition', 'Petition'),
        ('agreement', 'Agreement/Stipulation'),
        ('letter', 'Formal Letter'),
        ('notes', 'Case Notes'),
        ('other', 'Other Document'),
    ]

    DOCUMENT_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('finalized', 'Finalized'),
        ('filed', 'Filed with Court'),
        ('sent', 'Sent to Opposing Party'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to case (optional - can exist independently)
    case = models.ForeignKey(
        LegalCase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='legal_documents'
    )

    # Document metadata
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        default='motion'
    )
    title = models.CharField(max_length=300)

    # Content
    content = models.TextField(
        help_text="Generated document content (markdown)"
    )

    # Generation context
    original_query = models.TextField(
        blank=True,
        help_text="The user's original request"
    )
    generation_context = models.JSONField(
        default=dict,
        help_text="Context used for generation: {case_type, motion_type, facts, etc.}"
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=DOCUMENT_STATUS_CHOICES,
        default='draft'
    )

    # Version tracking
    version = models.IntegerField(default=1)
    parent_document = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revisions',
        help_text="Previous version of this document"
    )

    # Feedback for learning
    user_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="User rating 1-5"
    )
    user_feedback = models.TextField(
        blank=True,
        help_text="User feedback on the document"
    )
    was_used = models.BooleanField(
        default=False,
        help_text="Whether the document was actually used/filed"
    )

    # Disclaimer tracking
    disclaimer_shown = models.BooleanField(
        default=True,
        help_text="Whether legal disclaimer was shown"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        verbose_name = "Legal Document"
        verbose_name_plural = "Legal Documents"
        indexes = [
            models.Index(fields=['user', 'document_type']),
            models.Index(fields=['case', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()})"

    def create_revision(self, new_content: str) -> 'LegalDocument':
        """Create a new revision of this document."""
        return LegalDocument.objects.create(
            case=self.case,
            user=self.user,
            document_type=self.document_type,
            title=self.title,
            content=new_content,
            original_query=self.original_query,
            generation_context=self.generation_context,
            version=self.version + 1,
            parent_document=self,
        )

    def record_feedback(self, rating: int = None, feedback: str = None, was_used: bool = None):
        """Record user feedback for learning."""
        if rating is not None:
            self.user_rating = rating
        if feedback is not None:
            self.user_feedback = feedback
        if was_used is not None:
            self.was_used = was_used
        self.save()

        # Trigger learning hook
        self._record_learning_outcome()

    def _record_learning_outcome(self):
        """Create learning record from feedback."""
        if not self.user_rating:
            return

        try:
            from core.models_unified_system import AgentKnowledgeSource, Agent

            agent = Agent.objects.filter(name='LegalDocDrafterAgent').first()
            if not agent:
                return

            # Create knowledge from successful documents (rating >= 4)
            if self.user_rating >= 4:
                AgentKnowledgeSource.objects.create(
                    agent=agent,
                    knowledge_type='user_behavior',
                    title=f"Successful {self.get_document_type_display()}: {self.title[:100]}",
                    summary=f"User rated {self.user_rating}/5. Document type: {self.document_type}. Was used: {self.was_used}",
                    key_insights=[
                        f"Document type: {self.document_type}",
                        f"Rating: {self.user_rating}/5",
                        f"Was used: {self.was_used}",
                        f"Context: {json.dumps(self.generation_context)[:500] if self.generation_context else 'N/A'}",
                    ],
                    confidence_score=self.user_rating / 5.0,
                    raw_data={
                        'document_id': str(self.id),
                        'document_type': self.document_type,
                        'rating': self.user_rating,
                        'feedback': self.user_feedback,
                        'was_used': self.was_used,
                        'context': self.generation_context,
                    }
                )
        except Exception as e:
            logger.error(f"Failed to record learning outcome: {e}")


class LegalResearchResult(models.Model):
    """
    Session 403: Legal research results from LegalDocDrafterAgent.
    Stores legal guidance, procedure explanations, and form lookups.

    Similar to BusinessResearchResult but focused on legal information.
    """

    RESEARCH_TYPE_CHOICES = [
        ('guidance', 'Legal Guidance'),
        ('procedure', 'Procedure Explanation'),
        ('form_lookup', 'Form Information'),
        ('case_law', 'Case Law Research'),
        ('statute', 'Statute/Law Lookup'),
        ('deadline', 'Deadline/Timeline Research'),
        ('strategy', 'Strategy Research'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to case (optional)
    case = models.ForeignKey(
        LegalCase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='research_results'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='legal_research'
    )

    # Research metadata
    research_type = models.CharField(
        max_length=20,
        choices=RESEARCH_TYPE_CHOICES,
        default='guidance'
    )
    query = models.TextField(
        help_text="The original research query"
    )
    case_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Type of case this research relates to"
    )
    jurisdiction = models.CharField(
        max_length=50,
        default='Colorado'
    )

    # The research result
    analysis = models.TextField(
        help_text="GPT-generated legal research/guidance (markdown)"
    )

    # Structured findings
    key_points = models.JSONField(
        default=list,
        help_text="Key legal points extracted"
    )
    forms_referenced = models.JSONField(
        default=list,
        help_text="JDF forms referenced: [{form_number, title, url}]"
    )
    statutes_cited = models.JSONField(
        default=list,
        help_text="Statutes/laws cited: [{citation, summary}]"
    )
    procedures = models.JSONField(
        default=list,
        help_text="Procedures explained: [{step, description}]"
    )
    deadlines = models.JSONField(
        default=list,
        help_text="Relevant deadlines: [{deadline, description}]"
    )
    recommendations = models.JSONField(
        default=list,
        help_text="Recommended actions"
    )

    # Data sources
    sources_used = models.JSONField(
        default=list,
        help_text="Spider/web sources used"
    )
    spider_data_count = models.IntegerField(default=0)

    # Embedding for semantic search
    # Session 730: Migrated to pgvector VectorField
    embedding = VectorField(
        dimensions=1536,
        null=True,
        blank=True,
        help_text="Vector embedding for semantic search (pgvector)"
    ) if HAS_PGVECTOR else models.JSONField(
        null=True,
        blank=True,
        help_text="Vector embedding (JSON fallback)"
    )

    # Execution metrics
    execution_time_ms = models.IntegerField(default=0)

    # Disclaimer tracking
    disclaimer_included = models.BooleanField(
        default=True,
        help_text="Whether legal disclaimer was included"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        verbose_name = "Legal Research Result"
        verbose_name_plural = "Legal Research Results"
        indexes = [
            models.Index(fields=['user', 'research_type']),
            models.Index(fields=['case_type', 'jurisdiction']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_research_type_display()}: {self.query[:50]}..."

    def generate_embedding(self):
        """Generate embedding for semantic search."""
        try:
            from openai import OpenAI
            import os

            from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51 lazy
            client = get_openai_client(api_key=os.getenv('OPENAI_API_KEY'))

            # Create searchable text
            text_to_embed = f"Legal {self.research_type}: {self.query}\n\n{self.analysis[:4000]}"

            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text_to_embed
            )

            self.embedding = response.data[0].embedding
            self.save(update_fields=['embedding'])
            return True

        except Exception as e:
            logger.error(f"Failed to generate legal research embedding: {e}")
            return False

    @classmethod
    def save_legal_research(
        cls,
        user,
        query: str,
        analysis: str,
        research_type: str = 'guidance',
        case_type: str = '',
        jurisdiction: str = 'Colorado',
        key_points: list = None,
        forms_referenced: list = None,
        statutes_cited: list = None,
        procedures: list = None,
        deadlines: list = None,
        recommendations: list = None,
        sources_used: list = None,
        execution_time_ms: int = 0,
        case_id: str = None,
    ):
        """
        Helper to save LegalDocDrafterAgent research results.
        """
        case = None
        if case_id:
            try:
                case = LegalCase.objects.get(id=case_id)
            except LegalCase.DoesNotExist:
                pass

        instance = cls.objects.create(
            user=user,
            case=case,
            research_type=research_type,
            query=query,
            case_type=case_type,
            jurisdiction=jurisdiction,
            analysis=analysis,
            key_points=key_points or [],
            forms_referenced=forms_referenced or [],
            statutes_cited=statutes_cited or [],
            procedures=procedures or [],
            deadlines=deadlines or [],
            recommendations=recommendations or [],
            sources_used=sources_used or [],
            spider_data_count=len(sources_used) if sources_used else 0,
            execution_time_ms=execution_time_ms,
        )

        # Update case research count
        if case:
            case.research_count = case.research_results.count()
            case.save(update_fields=['research_count', 'updated_at'])

        # Generate embedding for semantic search
        instance.generate_embedding()

        return instance


class LegalMemory(models.Model):
    """
    Session 403: Legal-specific memory for the LegalDocDrafterAgent.
    Stores successful legal patterns, precedents, and strategies learned.

    Extends the Memory Palace concept for legal domain knowledge.
    """

    MEMORY_TYPE_CHOICES = [
        ('precedent', 'Legal Precedent'),
        ('strategy', 'Successful Strategy'),
        ('pattern', 'Document Pattern'),
        ('user_pref', 'User Preference'),
        ('outcome', 'Case Outcome'),
        ('form_usage', 'Form Usage Pattern'),
        ('procedure', 'Procedure Insight'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to agent
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='legal_memories',
        null=True,
        blank=True
    )

    # Memory content
    memory_type = models.CharField(
        max_length=20,
        choices=MEMORY_TYPE_CHOICES,
        default='pattern'
    )
    title = models.CharField(max_length=300)
    content = models.TextField()

    # Legal context
    case_type = models.CharField(max_length=50, blank=True)
    jurisdiction = models.CharField(max_length=50, default='Colorado')
    document_type = models.CharField(max_length=50, blank=True)

    # Structured data
    key_insights = models.JSONField(
        default=list,
        help_text="Key learnings from this memory"
    )
    applicable_scenarios = models.JSONField(
        default=list,
        help_text="Scenarios where this memory is applicable"
    )

    # Confidence and usage
    confidence_score = models.FloatField(
        default=0.8,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    usage_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)

    # Source tracking
    source_document = models.ForeignKey(
        LegalDocument,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='memories_created'
    )
    source_research = models.ForeignKey(
        LegalResearchResult,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='memories_created'
    )

    # Embedding for retrieval
    # Session 730: Migrated to pgvector VectorField
    embedding = VectorField(
        dimensions=1536,
        null=True,
        blank=True,
        help_text="Vector embedding for semantic search (pgvector)"
    ) if HAS_PGVECTOR else models.JSONField(
        null=True,
        blank=True,
        help_text="Vector embedding (JSON fallback)"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ['-confidence_score', '-usage_count']
        verbose_name = "Legal Memory"
        verbose_name_plural = "Legal Memories"
        indexes = [
            models.Index(fields=['memory_type', 'case_type']),
            models.Index(fields=['jurisdiction']),
            models.Index(fields=['confidence_score']),
        ]

    def __str__(self):
        return f"{self.get_memory_type_display()}: {self.title[:50]}"

    def record_usage(self, was_successful: bool = True):
        """Record that this memory was used."""
        self.usage_count += 1
        if was_successful:
            self.success_count += 1
        self.last_used_at = timezone.now()

        # Update confidence based on success rate
        if self.usage_count > 0:
            self.confidence_score = self.success_count / self.usage_count

        self.save(update_fields=['usage_count', 'success_count', 'last_used_at', 'confidence_score'])

    def generate_embedding(self):
        """Generate embedding for semantic retrieval."""
        try:
            from openai import OpenAI
            import os

            from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51 lazy
            client = get_openai_client(api_key=os.getenv('OPENAI_API_KEY'))

            text_to_embed = f"{self.memory_type} | {self.case_type} | {self.title}\n{self.content[:2000]}"

            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text_to_embed
            )

            self.embedding = response.data[0].embedding
            self.save(update_fields=['embedding'])
            return True

        except Exception as e:
            logger.error(f"Failed to generate legal memory embedding: {e}")
            return False

    @classmethod
    def create_from_successful_document(cls, document: LegalDocument, insights: list = None):
        """Create a memory from a successfully used document."""
        if not document.was_used or (document.user_rating and document.user_rating < 4):
            return None

        agent = Agent.objects.filter(name='LegalDocDrafterAgent').first()

        memory = cls.objects.create(
            agent=agent,
            memory_type='pattern',
            title=f"Successful {document.get_document_type_display()}: {document.title[:100]}",
            content=f"Document rated {document.user_rating}/5 and was used. "
                    f"Context: {json.dumps(document.generation_context)[:1000] if document.generation_context else 'N/A'}",
            case_type=document.generation_context.get('case_type', '') if document.generation_context else '',
            document_type=document.document_type,
            key_insights=insights or [],
            confidence_score=document.user_rating / 5.0 if document.user_rating else 0.8,
            source_document=document,
        )

        memory.generate_embedding()
        return memory


# =============================================================================
# SESSION 412: BOARDROOM DECISIONS - AGENT GOVERNANCE SYSTEM
# =============================================================================


class AgentDecisionSummary(models.Model):
    """
    Session 412: Structured decisions extracted from agent conversations.

    Agent conversations generate valuable governance artifacts (policies,
    architecture decisions, pipeline specs) but these insights currently
    evaporate after the conversation ends. This model captures them.

    These decisions can be promoted to canonical policies that affect
    future agent behavior, creating a self-improving governance system.

    Links to BOTH:
    - AgentConversation (legacy, 2,899 records)
    - HiveMindSession (new, session_mode='conversation')
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Session 843: Orchestration Contract fields
    trace_id = models.UUIDField(
        null=True, blank=True, db_index=True,
        help_text="Session 843: Trace ID for cross-artifact linking"
    )
    project = models.ForeignKey(
        'core.PartnershipProject',
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name='decision_summaries',
        help_text="Session 843: Project this decision belongs to"
    )

    # Session 849: Link to Initiative for tracking decisions with proposed features
    initiative = models.ForeignKey(
        'core.Initiative',
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name='source_decisions',
        help_text="Session 849: Initiative created from this decision's proposed feature"
    )

    # Session 849: Artifact type classification
    artifact_type = models.CharField(
        max_length=30,
        choices=[
            ('learning', 'Learning'),
            ('initiative_stage_doc', 'Initiative Stage Document'),
            ('report', 'Report'),
            ('playbook', 'Playbook'),
            ('decision', 'Decision'),
        ],
        default='decision',
        help_text="Session 849: Type of artifact this decision represents"
    )

    # Link to source conversations (one or the other)
    # Legacy AgentConversation (Session 244-246)
    conversation = models.ForeignKey(
        'AgentConversation',
        on_delete=models.CASCADE,
        related_name='decisions',
        null=True,
        blank=True,
        help_text="Legacy AgentConversation source"
    )
    # New HiveMindSession (Session 284+)
    hive_session = models.ForeignKey(
        'HiveMindSession',
        on_delete=models.CASCADE,
        related_name='decisions',
        null=True,
        blank=True,
        help_text="HiveMindSession source (session_mode='conversation')"
    )

    # Decision metadata
    topic = models.CharField(max_length=255)
    decision_type = models.CharField(
        max_length=50,
        choices=[
            ('policy', 'Policy'),
            ('architecture', 'Architecture'),
            ('pipeline', 'Pipeline'),
            ('product', 'Product Feature'),
            ('experiment', 'Experiment'),
            ('guideline', 'Guideline'),
        ]
    )
    impact_area = models.CharField(
        max_length=50,
        choices=[
            ('prompting', 'Prompt Engineering'),
            ('memory', 'Memory & Storage'),
            ('image', 'Image Generation'),
            ('video', 'Video Generation'),
            ('audio', 'Audio Generation'),
            ('workflow', 'Workflows'),
            ('agents', 'Agent Behavior'),
            ('security', 'Security & Privacy'),
            ('infrastructure', 'Infrastructure'),
            ('product', 'Product/UX'),
            ('legal', 'Legal Assistant'),
            ('research', 'Research & Analysis'),
            ('spider', 'Spider Network'),
        ]
    )

    # The actual decision content
    key_insights = models.JSONField(default=list)  # List of 3-5 bullet points
    recommended_stance = models.TextField()  # The main policy/decision
    suggested_feature = models.TextField(blank=True)  # Optional feature suggestion
    rationale = models.TextField(blank=True)  # Why this decision was made

    # Participants who contributed
    participants = models.JSONField(default=list)  # List of agent names

    # Governance status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('review', 'Under Review'),
            ('canonical', 'Canonical Policy'),
            ('experiment', 'Active Experiment'),
            ('superseded', 'Superseded'),
            ('rejected', 'Rejected'),
        ],
        default='draft'
    )
    is_canonical = models.BooleanField(default=False)
    promoted_at = models.DateTimeField(null=True, blank=True)
    promoted_by = models.CharField(max_length=100, blank=True)  # 'human' or agent name

    # If this supersedes a previous decision (self-reference added after initial migration)
    # Note: This uses 'core.AgentDecisionSummary' instead of 'self' to avoid migration issues
    supersedes_id = models.UUIDField(null=True, blank=True, help_text="ID of decision this supersedes")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Agent Decision Summary"
        verbose_name_plural = "Agent Decision Summaries"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['decision_type', 'impact_area']),
            models.Index(fields=['status']),
            models.Index(fields=['is_canonical']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"[{self.decision_type}] {self.topic}"

    def promote_to_canonical(self, promoted_by='human'):
        """Promote this decision to canonical policy status."""
        from django.utils import timezone
        self.status = 'canonical'
        self.is_canonical = True
        self.promoted_at = timezone.now()
        self.promoted_by = promoted_by
        self.save()

    def get_source_display(self):
        """Get display name for the source conversation."""
        if self.conversation:
            return f"Conversation: {self.conversation.topic}"
        elif self.hive_session:
            return f"Hive Session: {self.hive_session.topic}"
        return "Unknown Source"

    def get_source_id(self):
        """Get ID of source conversation/session."""
        if self.conversation:
            return str(self.conversation.id)
        elif self.hive_session:
            return str(self.hive_session.id)
        return None

    def get_policy_context(self):
        """Get this decision formatted for injection into agent prompts."""
        insights = '\n'.join(f'  - {i}' for i in self.key_insights[:3])
        return f"""
[CANONICAL POLICY: {self.topic}]
Type: {self.get_decision_type_display()}
Area: {self.get_impact_area_display()}
Key Points:
{insights}
Stance: {self.recommended_stance}
"""

    def to_dict(self):
        """Return decision as dictionary for API responses."""
        return {
            'id': str(self.id),
            'topic': self.topic,
            'decision_type': self.decision_type,
            'decision_type_display': self.get_decision_type_display(),
            'impact_area': self.impact_area,
            'impact_area_display': self.get_impact_area_display(),
            'key_insights': self.key_insights,
            'recommended_stance': self.recommended_stance,
            'suggested_feature': self.suggested_feature,
            'rationale': self.rationale,
            'participants': self.participants,
            'status': self.status,
            'status_display': self.get_status_display(),
            'is_canonical': self.is_canonical,
            'promoted_at': self.promoted_at.isoformat() if self.promoted_at else None,
            'promoted_by': self.promoted_by,
            'source': self.get_source_display(),
            'source_id': self.get_source_id(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


# ==========================================
# Market Intelligence System Models
# Session 462: The Market Intelligence Desk
# ==========================================

class MarketIntelligenceBrief(models.Model):
    """
    Daily Market Intelligence Brief - First Tier 1 Autonomous Situation Output

    Stores the synthesized output from Bull vs Bear debates, including:
    - High conviction opportunities (both agree)
    - Debate zone stocks (strong disagreement - most interesting!)
    - Risk alerts from audit system
    - Change tracking vs previous day
    - Confidence distribution

    This enables:
    1. Historical tracking of market intelligence
    2. Day-over-day change analysis
    3. Learning from prediction accuracy
    4. Autonomous situation persistence
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Brief metadata
    brief_date = models.DateField(
        unique=True,
        help_text="Date this brief covers (one brief per day)"
    )
    brief_type = models.CharField(
        max_length=50,
        default='daily_market_intelligence_brief',
        help_text="Type of brief (daily/weekly/special)"
    )

    # Executive summary (concise text overview)
    executive_summary = models.TextField(
        help_text="Concise executive summary of market conditions"
    )

    # Analysis results (structured JSON data)
    high_conviction_opportunities = models.JSONField(
        default=list,
        help_text="Stocks where bull and bear both agree (high confidence)"
    )
    debate_zone = models.JSONField(
        default=list,
        help_text="Stocks with strong disagreement - MOST INTERESTING for alpha"
    )
    bullish_opportunities = models.JSONField(
        default=list,
        help_text="Stocks where bull case dominates"
    )
    bearish_warnings = models.JSONField(
        default=list,
        help_text="Stocks where bear case dominates"
    )
    risk_alerts = models.JSONField(
        default=list,
        help_text="Risk signals from Stock Audit system"
    )

    # Change tracking
    changes_from_yesterday = models.JSONField(
        default=dict,
        help_text="What changed vs yesterday's brief"
    )
    is_first_brief = models.BooleanField(
        default=False,
        help_text="True if this is the first brief (no baseline for comparison)"
    )

    # Metrics
    total_stocks_analyzed = models.IntegerField(
        default=0,
        help_text="Total unique stocks analyzed in this brief"
    )
    confidence_distribution = models.JSONField(
        default=dict,
        help_text="Distribution of confidence levels (HIGH/UNCERTAIN/LOW counts)"
    )
    debate_zone_count = models.IntegerField(
        default=0,
        help_text="Number of stocks in debate zone (disagreement metric)"
    )

    # Delivery status
    discord_sent = models.BooleanField(
        default=False,
        help_text="Whether brief was delivered to Discord"
    )
    discord_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When brief was sent to Discord"
    )
    voice_delivered = models.BooleanField(
        default=False,
        help_text="Whether brief was delivered via voice"
    )

    # Autonomous situation health metrics
    situation_health = models.CharField(
        max_length=20,
        default='OPERATIONAL',
        choices=[
            ('OPERATIONAL', 'Operational'),
            ('DEGRADED', 'Degraded'),
            ('FAILED', 'Failed'),
        ],
        help_text="Health status of the autonomous situation"
    )
    gpt_success_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Percentage of stocks that got GPT analysis (vs fallback)"
    )

    # Learning integration (for outcome tracking)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='market_intelligence_briefs',
        help_text="User this brief was generated for (if personalized)"
    )

    # Timestamps
    generated_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this brief was generated"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update to this brief"
    )

    class Meta:
        app_label = 'core'
        verbose_name = "Market Intelligence Brief"
        verbose_name_plural = "Market Intelligence Briefs"
        ordering = ['-brief_date']
        indexes = [
            models.Index(fields=['-brief_date']),
            models.Index(fields=['situation_health']),
            models.Index(fields=['user', '-brief_date']),
        ]

    def __str__(self):
        return f"Market Intelligence Brief - {self.brief_date}"

    def get_previous_brief(self):
        """Get the previous day's brief for change tracking."""
        from datetime import timedelta
        previous_date = self.brief_date - timedelta(days=1)
        try:
            return MarketIntelligenceBrief.objects.get(brief_date=previous_date)
        except MarketIntelligenceBrief.DoesNotExist:
            return None

    def calculate_changes(self):
        """Calculate changes from previous brief and update changes_from_yesterday field."""
        previous = self.get_previous_brief()

        if not previous:
            self.is_first_brief = True
            self.changes_from_yesterday = {
                'is_first_run': True,
                'message': 'First Market Intelligence Brief - no baseline for comparison',
                'changes': [],
            }
            return self.changes_from_yesterday

        changes = {
            'is_first_run': False,
            'changes': [],
            'new_opportunities': [],
            'disappeared_opportunities': [],
            'conviction_changes': [],
            'new_risks': [],
        }

        # 1. Compare debate zone sizes
        prev_debate_count = previous.debate_zone_count
        curr_debate_count = self.debate_zone_count
        if curr_debate_count != prev_debate_count:
            changes['changes'].append({
                'type': 'debate_zone_size',
                'previous': prev_debate_count,
                'current': curr_debate_count,
                'message': f"Debate zone changed from {prev_debate_count} to {curr_debate_count} stocks"
            })

        # 2. Track stocks that entered/exited debate zone
        prev_debate_tickers = set(item.get('ticker') for item in previous.debate_zone)
        curr_debate_tickers = set(item.get('ticker') for item in self.debate_zone)

        new_debates = curr_debate_tickers - prev_debate_tickers
        resolved_debates = prev_debate_tickers - curr_debate_tickers

        if new_debates:
            changes['changes'].append({
                'type': 'new_debates',
                'tickers': list(new_debates),
                'count': len(new_debates),
                'message': f"{len(new_debates)} stock(s) entered debate zone: {', '.join(sorted(new_debates))}"
            })

        if resolved_debates:
            changes['changes'].append({
                'type': 'resolved_debates',
                'tickers': list(resolved_debates),
                'count': len(resolved_debates),
                'message': f"{len(resolved_debates)} stock(s) left debate zone: {', '.join(sorted(resolved_debates))}"
            })

        # 3. Track new/disappeared bullish opportunities
        prev_bullish_tickers = set(item.get('ticker') for item in previous.bullish_opportunities)
        curr_bullish_tickers = set(item.get('ticker') for item in self.bullish_opportunities)

        new_bullish = curr_bullish_tickers - prev_bullish_tickers
        lost_bullish = prev_bullish_tickers - curr_bullish_tickers

        if new_bullish:
            changes['new_opportunities'] = [
                {
                    'ticker': ticker,
                    'type': 'bullish',
                    'message': f"{ticker} now bullish"
                }
                for ticker in sorted(new_bullish)
            ]
            changes['changes'].append({
                'type': 'new_bullish_opportunities',
                'tickers': list(new_bullish),
                'count': len(new_bullish),
                'message': f"{len(new_bullish)} new bullish opportunity(s): {', '.join(sorted(new_bullish))}"
            })

        if lost_bullish:
            changes['disappeared_opportunities'].extend([
                {
                    'ticker': ticker,
                    'type': 'bullish',
                    'message': f"{ticker} no longer bullish"
                }
                for ticker in sorted(lost_bullish)
            ])
            changes['changes'].append({
                'type': 'lost_bullish_opportunities',
                'tickers': list(lost_bullish),
                'count': len(lost_bullish),
                'message': f"{len(lost_bullish)} stock(s) lost bullish status: {', '.join(sorted(lost_bullish))}"
            })

        # 4. Track new/disappeared bearish warnings
        prev_bearish_tickers = set(item.get('ticker') for item in previous.bearish_warnings)
        curr_bearish_tickers = set(item.get('ticker') for item in self.bearish_warnings)

        new_bearish = curr_bearish_tickers - prev_bearish_tickers
        lost_bearish = prev_bearish_tickers - curr_bearish_tickers

        if new_bearish:
            changes['changes'].append({
                'type': 'new_bearish_warnings',
                'tickers': list(new_bearish),
                'count': len(new_bearish),
                'message': f"{len(new_bearish)} new bearish warning(s): {', '.join(sorted(new_bearish))}"
            })

        if lost_bearish:
            changes['changes'].append({
                'type': 'lost_bearish_warnings',
                'tickers': list(lost_bearish),
                'count': len(lost_bearish),
                'message': f"{len(lost_bearish)} stock(s) improved from bearish: {', '.join(sorted(lost_bearish))}"
            })

        # 5. Track new risk alerts
        prev_risk_tickers = set(alert.get('ticker') for alert in previous.risk_alerts if alert.get('ticker'))
        curr_risk_tickers = set(alert.get('ticker') for alert in self.risk_alerts if alert.get('ticker'))

        new_risks = curr_risk_tickers - prev_risk_tickers

        if new_risks:
            changes['new_risks'] = [
                {
                    'ticker': ticker,
                    'type': next((alert.get('type', 'unknown') for alert in self.risk_alerts if alert.get('ticker') == ticker), 'unknown'),
                    'message': f"{ticker} flagged for risk"
                }
                for ticker in sorted(new_risks)
            ]
            changes['changes'].append({
                'type': 'new_risk_alerts',
                'tickers': list(new_risks),
                'count': len(new_risks),
                'message': f"{len(new_risks)} new risk alert(s): {', '.join(sorted(new_risks))}"
            })

        # 6. Track conviction changes for individual stocks (HIGH → UNCERTAIN, etc.)
        # Build conviction maps from debate zone
        prev_conviction_map = {item.get('ticker'): item.get('bull_conviction', 'UNKNOWN') for item in previous.debate_zone}
        curr_conviction_map = {item.get('ticker'): item.get('bull_conviction', 'UNKNOWN') for item in self.debate_zone}

        for ticker in curr_conviction_map:
            if ticker in prev_conviction_map:
                prev_conviction = prev_conviction_map[ticker]
                curr_conviction = curr_conviction_map[ticker]

                if prev_conviction != curr_conviction:
                    changes['conviction_changes'].append({
                        'ticker': ticker,
                        'previous': prev_conviction,
                        'current': curr_conviction,
                        'message': f"{ticker} conviction changed: {prev_conviction} → {curr_conviction}"
                    })
                    changes['changes'].append({
                        'type': 'conviction_change',
                        'ticker': ticker,
                        'previous': prev_conviction,
                        'current': curr_conviction,
                        'message': f"{ticker} conviction: {prev_conviction} → {curr_conviction}"
                    })

        # 7. Compare confidence distributions
        prev_dist = previous.confidence_distribution
        curr_dist = self.confidence_distribution
        if prev_dist != curr_dist:
            # Calculate meaningful changes
            dist_changes = []
            for level in ['HIGH', 'UNCERTAIN', 'LOW']:
                prev_count = prev_dist.get(level, 0)
                curr_count = curr_dist.get(level, 0)
                if prev_count != curr_count:
                    diff = curr_count - prev_count
                    sign = '+' if diff > 0 else ''
                    dist_changes.append(f"{level}: {sign}{diff}")

            changes['changes'].append({
                'type': 'confidence_shift',
                'previous': prev_dist,
                'current': curr_dist,
                'message': f"Confidence distribution changed ({', '.join(dist_changes)})"
            })

        # Generate summary message
        change_count = len(changes['changes'])
        if change_count == 0:
            changes['message'] = f"No significant changes from {previous.brief_date}"
        else:
            changes['message'] = f"Detected {change_count} change(s) from {previous.brief_date}"

        self.changes_from_yesterday = changes
        return changes

    def to_dict(self):
        """Return brief as dictionary for API responses."""
        return {
            'id': str(self.id),
            'brief_date': self.brief_date.isoformat(),
            'brief_type': self.brief_type,
            'executive_summary': self.executive_summary,
            'high_conviction': self.high_conviction_opportunities,
            'debate_zone': self.debate_zone,
            'debate_zone_count': self.debate_zone_count,
            'bullish_opportunities': self.bullish_opportunities,
            'bearish_warnings': self.bearish_warnings,
            'risk_alerts': self.risk_alerts,
            'changes_from_yesterday': self.changes_from_yesterday,
            'is_first_brief': self.is_first_brief,
            'total_stocks_analyzed': self.total_stocks_analyzed,
            'confidence_distribution': self.confidence_distribution,
            'situation_health': self.situation_health,
            'gpt_success_rate': self.gpt_success_rate,
            'discord_sent': self.discord_sent,
            'discord_sent_at': self.discord_sent_at.isoformat() if self.discord_sent_at else None,
            'voice_delivered': self.voice_delivered,
            'generated_at': self.generated_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


# ==========================================
# Sports Betting Intelligence Brief
# Session 1003: Persist sports desk output
# ==========================================

class SportsBettingBrief(models.Model):
    """
    Session 1003: Persistent sports betting intelligence brief.

    Before this model, SportsBettingCoordinator.generate_brief() output was
    only stored in a 6-hour cache that expired. This model persists briefs
    for historical analysis and learning.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brief_date = models.DateField()
    sport_filter = models.CharField(max_length=50, blank=True, default='')
    executive_summary = models.TextField(blank=True, default='')
    predictions = models.JSONField(default=dict)
    arbitrage_opportunities = models.JSONField(default=dict)
    sharp_action_alerts = models.JSONField(default=dict)
    line_movements = models.JSONField(default=dict)
    top_plays = models.JSONField(default=list)
    agents_run = models.JSONField(default=list)
    errors = models.JSONField(default=list)
    generation_time_seconds = models.FloatField(default=0.0)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Sports Betting Brief"
        verbose_name_plural = "Sports Betting Briefs"
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['-brief_date']),
            models.Index(fields=['-generated_at']),
        ]

    def __str__(self):
        return f"Sports Betting Brief - {self.brief_date}"


# ==========================================
# Blockchain Audit Intelligence Brief
# Session 1003: Persist blockchain desk output
# ==========================================

class BlockchainAuditBrief(models.Model):
    """
    Session 1003: Persistent blockchain audit intelligence brief.

    Before this model, BlockchainAuditCoordinator.execute() output was
    only stored in a 6-hour cache that expired. This model persists briefs
    for historical analysis and learning.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brief_date = models.DateField()
    executive_summary = models.TextField(blank=True, default='')
    security_alerts = models.JSONField(default=dict)
    whale_movements = models.JSONField(default=dict)
    contract_audits = models.JSONField(default=dict)
    exploit_detection = models.JSONField(default=dict)
    agents_run = models.JSONField(default=list)
    errors = models.JSONField(default=list)
    generation_time_seconds = models.FloatField(default=0.0)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Blockchain Audit Brief"
        verbose_name_plural = "Blockchain Audit Briefs"
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['-brief_date']),
            models.Index(fields=['-generated_at']),
        ]

    def __str__(self):
        return f"Blockchain Audit Brief - {self.brief_date}"


class PredictionOutcome(models.Model):
    """
    Tracks a single stock prediction (bull or bear case) and its actual outcome.

    This enables:
    1. Measuring bull/bear prediction accuracy over time
    2. Identifying which market conditions lead to accurate predictions
    3. Calibrating confidence scores based on track record
    4. Learning which debate patterns predict actual outcomes
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to the brief that made this prediction
    brief = models.ForeignKey(
        'core.MarketIntelligenceBrief',
        on_delete=models.CASCADE,
        related_name='prediction_outcomes',
        help_text="The Market Intelligence Brief that made this prediction"
    )

    # Stock identification
    ticker = models.CharField(
        max_length=10,
        help_text="Stock ticker symbol (e.g., AAPL, MSFT)"
    )

    # Prediction details
    prediction_type = models.CharField(
        max_length=10,
        choices=[
            ('BULL', 'Bull Case'),
            ('BEAR', 'Bear Case'),
        ],
        help_text="Whether this was a bull or bear prediction"
    )
    conviction_level = models.CharField(
        max_length=10,
        choices=[
            ('HIGH', 'High Conviction'),
            ('MEDIUM', 'Medium Conviction'),
            ('LOW', 'Low Conviction'),
        ],
        help_text="Conviction level at prediction time"
    )
    predicted_move = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Predicted percentage move (e.g., +25.00 for bull, -15.00 for bear)"
    )

    # Price data at prediction time
    price_at_prediction = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Stock price when prediction was made"
    )
    prediction_date = models.DateField(
        help_text="Date prediction was made"
    )

    # Actual outcome data
    price_after_7_days = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Stock price 7 days after prediction"
    )
    price_after_30_days = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Stock price 30 days after prediction"
    )
    actual_move_7_days = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual percentage move after 7 days"
    )
    actual_move_30_days = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual percentage move after 30 days"
    )

    # Accuracy assessment
    was_correct_7_days = models.BooleanField(
        null=True,
        blank=True,
        help_text="True if prediction direction was correct after 7 days"
    )
    was_correct_30_days = models.BooleanField(
        null=True,
        blank=True,
        help_text="True if prediction direction was correct after 30 days"
    )
    accuracy_score_7_days = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Accuracy score 0-1 (considers direction + magnitude)"
    )
    accuracy_score_30_days = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Accuracy score 0-1 (considers direction + magnitude)"
    )

    # Market context at prediction time (for pattern learning)
    market_regime = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=[
            ('STRONG_BULL', 'Strong Bull Market'),
            ('BULL', 'Bull Market'),
            ('NEUTRAL', 'Neutral/Ranging'),
            ('BEAR', 'Bear Market'),
            ('STRONG_BEAR', 'Strong Bear Market'),
        ],
        help_text="Market regime at prediction time"
    )
    volatility_level = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=[
            ('EXTREME', 'Extreme Volatility'),
            ('HIGH', 'High Volatility'),
            ('MODERATE', 'Moderate Volatility'),
            ('LOW', 'Low Volatility'),
        ],
        help_text="Volatility level at prediction time"
    )

    # Debate zone context
    was_in_debate_zone = models.BooleanField(
        default=False,
        help_text="True if this stock was in the debate zone (bull vs bear disagreed)"
    )
    opposite_conviction = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Conviction level of the opposite case (bull if this is bear, vice versa)"
    )

    # Outcome status
    outcome_calculated = models.BooleanField(
        default=False,
        help_text="True if we've calculated the actual outcome"
    )
    outcome_calculated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When outcome was calculated"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Prediction Outcome"
        verbose_name_plural = "Prediction Outcomes"
        ordering = ['-prediction_date', 'ticker']
        # Session 980: Prevent duplicate predictions per brief/ticker/type
        constraints = [
            models.UniqueConstraint(
                fields=['brief', 'ticker', 'prediction_type'],
                name='unique_prediction_per_brief_ticker_type',
            ),
        ]
        indexes = [
            models.Index(fields=['-prediction_date']),
            models.Index(fields=['ticker', '-prediction_date']),
            models.Index(fields=['prediction_type', 'conviction_level']),
            models.Index(fields=['was_correct_7_days']),
            models.Index(fields=['was_in_debate_zone']),
            models.Index(fields=['outcome_calculated']),
        ]

    def __str__(self):
        return f"{self.ticker} {self.prediction_type} ({self.conviction_level}) - {self.prediction_date}"

    def calculate_outcome(self, current_price=None, days_elapsed=None):
        """
        Calculate prediction accuracy based on actual price movement.

        Args:
            current_price: Current stock price (if checking now)
            days_elapsed: How many days since prediction (7 or 30)
        """
        from datetime import date

        if days_elapsed is None:
            # Auto-detect based on date
            days_since = (date.today() - self.prediction_date).days
            if days_since >= 30:
                days_elapsed = 30
            elif days_since >= 7:
                days_elapsed = 7
            else:
                return  # Not enough time has passed

        if current_price is None:
            # Fetch current price from market data service
            from core.services.market_data_service import MarketDataService
            service = MarketDataService()
            data = service.get_stock_details(self.ticker)
            if not data or 'current_price' not in data:
                return
            current_price = Decimal(str(data['current_price']))

        # Calculate actual move
        actual_move = ((current_price - self.price_at_prediction) / self.price_at_prediction) * 100

        # Store price and move
        if days_elapsed == 7:
            self.price_after_7_days = current_price
            self.actual_move_7_days = actual_move

            # Determine if prediction was correct
            predicted_up = self.predicted_move > 0
            actual_up = actual_move > 0
            self.was_correct_7_days = (predicted_up == actual_up)

            # Calculate accuracy score (0-1)
            # Perfect prediction = 1.0, wrong direction = 0.0, partial credit for magnitude
            if self.was_correct_7_days:
                # Same direction - score based on magnitude accuracy
                magnitude_ratio = min(abs(float(actual_move)) / abs(float(self.predicted_move)), 2.0)
                self.accuracy_score_7_days = 0.5 + (0.5 * (1.0 / magnitude_ratio))
            else:
                # Wrong direction - score decreases with magnitude of mistake
                self.accuracy_score_7_days = max(0.0, 0.3 - (abs(float(actual_move)) / 100.0))

        elif days_elapsed == 30:
            self.price_after_30_days = current_price
            self.actual_move_30_days = actual_move

            predicted_up = self.predicted_move > 0
            actual_up = actual_move > 0
            self.was_correct_30_days = (predicted_up == actual_up)

            if self.was_correct_30_days:
                magnitude_ratio = min(abs(float(actual_move)) / abs(float(self.predicted_move)), 2.0)
                self.accuracy_score_30_days = 0.5 + (0.5 * (1.0 / magnitude_ratio))
            else:
                self.accuracy_score_30_days = max(0.0, 0.3 - (abs(float(actual_move)) / 100.0))

        self.outcome_calculated = True
        from django.utils import timezone
        self.outcome_calculated_at = timezone.now()
        self.save()


class UserWatchlistItem(models.Model):
    """A single ticker on a user's stock watchlist."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='watchlist_items',
    )
    symbol = models.CharField(max_length=10, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'symbol'],
                name='unique_watchlist_user_symbol',
            ),
        ]

    def __str__(self):
        return f"{self.user} → {self.symbol}"


class UserBriefFeedback(models.Model):
    """
    DEPRECATED - Session 528: This model has 0 records and is not used.

    Original purpose: Captures user feedback and actions on Market Intelligence Briefs.

    This would have enabled:
    1. Tracking which briefs were useful vs not useful
    2. Measuring which stocks users acted on (buy/sell/hold)
    3. Learning which recommendations users follow
    4. Improving brief quality based on user engagement
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to user and brief
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='brief_feedback',
        help_text="User who provided feedback"
    )
    brief = models.ForeignKey(
        'core.MarketIntelligenceBrief',
        on_delete=models.CASCADE,
        related_name='user_feedback',
        help_text="The brief being rated"
    )

    # Overall brief rating
    was_helpful = models.BooleanField(
        null=True,
        blank=True,
        help_text="Did user find the brief helpful?"
    )
    helpfulness_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1-5 star rating of brief quality"
    )

    # Specific stock actions
    actions_taken = models.JSONField(
        default=list,
        help_text="List of actions: [{'ticker': 'AAPL', 'action': 'buy', 'reason': 'bull_case'}]"
    )

    # User engagement metrics
    viewed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When user first viewed the brief"
    )
    acted_on_brief = models.BooleanField(
        default=False,
        help_text="True if user took any action based on brief"
    )
    time_to_action = models.IntegerField(
        null=True,
        blank=True,
        help_text="Minutes between viewing and taking action"
    )

    # Follow-through tracking
    followed_bullish_recommendation = models.BooleanField(
        default=False,
        help_text="Did user buy/hold stocks from bullish_opportunities?"
    )
    followed_bearish_warning = models.BooleanField(
        default=False,
        help_text="Did user sell/avoid stocks from bearish_warnings?"
    )
    explored_debate_zone = models.BooleanField(
        default=False,
        help_text="Did user research stocks in debate zone?"
    )

    # Free-form feedback
    comment = models.TextField(
        blank=True,
        help_text="Optional user comment about the brief"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "User Brief Feedback"
        verbose_name_plural = "User Brief Feedback"
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['user', '-viewed_at']),
            models.Index(fields=['brief', 'user']),
            models.Index(fields=['was_helpful']),
            models.Index(fields=['acted_on_brief']),
        ]
        # One feedback entry per user per brief
        unique_together = [['user', 'brief']]

    def __str__(self):
        helpful = "Helpful" if self.was_helpful else "Not Helpful" if self.was_helpful is False else "Not Rated"
        return f"{self.user.username} - {self.brief.brief_date} ({helpful})"

    def record_action(self, ticker, action, reason=None):
        """
        Record a user action (buy/sell/hold/ignore) on a specific stock.

        Args:
            ticker: Stock ticker
            action: 'buy', 'sell', 'hold', 'ignore'
            reason: Optional reason (e.g., 'bull_case', 'bear_warning', 'debate_zone')
        """
        action_entry = {
            'ticker': ticker,
            'action': action,
            'reason': reason,
            'timestamp': timezone.now().isoformat(),
        }

        if not self.actions_taken:
            self.actions_taken = []

        self.actions_taken.append(action_entry)
        self.acted_on_brief = True

        # Update follow-through flags
        if reason == 'bull_case' and action in ['buy', 'hold']:
            self.followed_bullish_recommendation = True
        elif reason == 'bear_warning' and action in ['sell', 'avoid']:
            self.followed_bearish_warning = True
        elif reason == 'debate_zone':
            self.explored_debate_zone = True

        # Calculate time to action
        if not self.time_to_action and self.viewed_at:
            from django.utils import timezone
            time_diff = timezone.now() - self.viewed_at
            self.time_to_action = int(time_diff.total_seconds() / 60)  # Convert to minutes

        self.save()


class AgentAccuracyMetrics(models.Model):
    """
    Rolling accuracy metrics for Bull Case Agent and Bear Case Agent.

    This enables:
    1. Tracking agent performance over time
    2. Adjusting confidence scores based on track record
    3. Identifying which market conditions each agent performs best in
    4. Building trust scores for different prediction types
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Agent identification
    agent_name = models.CharField(
        max_length=50,
        choices=[
            ('BullCaseAgent', 'Bull Case Agent'),
            ('BearCaseAgent', 'Bear Case Agent'),
        ],
        help_text="Which agent these metrics track"
    )

    # Time period
    period_start = models.DateField(help_text="Start of measurement period")
    period_end = models.DateField(help_text="End of measurement period")

    # Overall accuracy
    total_predictions = models.IntegerField(
        default=0,
        help_text="Total predictions made in this period"
    )
    correct_predictions_7_days = models.IntegerField(
        default=0,
        help_text="Correct predictions after 7 days"
    )
    correct_predictions_30_days = models.IntegerField(
        default=0,
        help_text="Correct predictions after 30 days"
    )
    accuracy_rate_7_days = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Percentage accuracy after 7 days"
    )
    accuracy_rate_30_days = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Percentage accuracy after 30 days"
    )

    # Conviction calibration
    high_conviction_accuracy = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Accuracy rate for HIGH conviction predictions"
    )
    medium_conviction_accuracy = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Accuracy rate for MEDIUM conviction predictions"
    )
    low_conviction_accuracy = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Accuracy rate for LOW conviction predictions"
    )

    # Market regime performance
    bull_market_accuracy = models.FloatField(
        default=0.0,
        null=True,
        blank=True,
        help_text="Accuracy during bull markets"
    )
    bear_market_accuracy = models.FloatField(
        default=0.0,
        null=True,
        blank=True,
        help_text="Accuracy during bear markets"
    )
    neutral_market_accuracy = models.FloatField(
        default=0.0,
        null=True,
        blank=True,
        help_text="Accuracy during neutral/ranging markets"
    )

    # Debate zone insights
    debate_zone_accuracy = models.FloatField(
        default=0.0,
        null=True,
        blank=True,
        help_text="Accuracy when agent was in debate zone (disagreed with opposite agent)"
    )
    debate_zone_win_rate = models.FloatField(
        default=0.0,
        null=True,
        blank=True,
        help_text="Win rate when in debate zone (agent was right, opposite was wrong)"
    )

    # Confidence adjustment multiplier
    confidence_multiplier = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.5), MaxValueValidator(1.5)],
        help_text="Multiplier to adjust confidence scores based on track record (0.5-1.5)"
    )

    # Timestamps
    calculated_at = models.DateTimeField(
        auto_now=True,
        help_text="When metrics were last calculated"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Agent Accuracy Metrics"
        verbose_name_plural = "Agent Accuracy Metrics"
        ordering = ['-period_end', 'agent_name']
        indexes = [
            models.Index(fields=['agent_name', '-period_end']),
            models.Index(fields=['-calculated_at']),
        ]
        # One metrics entry per agent per period
        unique_together = [['agent_name', 'period_start', 'period_end']]

    def __str__(self):
        return f"{self.agent_name} - {self.period_start} to {self.period_end} ({self.accuracy_rate_7_days:.1f}% accurate)"

    def calculate_metrics(self):
        """
        Calculate all accuracy metrics based on prediction outcomes in this period.
        """

        # Get all predictions for this agent in this period
        predictions = PredictionOutcome.objects.filter(
            prediction_type='BULL' if self.agent_name == 'BullCaseAgent' else 'BEAR',
            prediction_date__gte=self.period_start,
            prediction_date__lte=self.period_end,
            outcome_calculated=True
        )

        self.total_predictions = predictions.count()

        if self.total_predictions == 0:
            return

        # Overall accuracy
        self.correct_predictions_7_days = predictions.filter(was_correct_7_days=True).count()
        self.correct_predictions_30_days = predictions.filter(was_correct_30_days=True).count()

        if self.total_predictions > 0:
            self.accuracy_rate_7_days = (self.correct_predictions_7_days / self.total_predictions) * 100
            self.accuracy_rate_30_days = (self.correct_predictions_30_days / self.total_predictions) * 100

        # Conviction calibration
        for conviction in ['HIGH', 'MEDIUM', 'LOW']:
            conviction_preds = predictions.filter(conviction_level=conviction)
            if conviction_preds.exists():
                correct = conviction_preds.filter(was_correct_7_days=True).count()
                total = conviction_preds.count()
                accuracy = (correct / total) * 100

                if conviction == 'HIGH':
                    self.high_conviction_accuracy = accuracy
                elif conviction == 'MEDIUM':
                    self.medium_conviction_accuracy = accuracy
                elif conviction == 'LOW':
                    self.low_conviction_accuracy = accuracy

        # Debate zone performance
        debate_preds = predictions.filter(was_in_debate_zone=True)
        if debate_preds.exists():
            debate_correct = debate_preds.filter(was_correct_7_days=True).count()
            self.debate_zone_accuracy = (debate_correct / debate_preds.count()) * 100

        # Calculate confidence multiplier based on overall performance
        # If accuracy > 60%: increase confidence (up to 1.5x)
        # If accuracy < 40%: decrease confidence (down to 0.5x)
        # If accuracy = 50%: neutral (1.0x)
        if self.accuracy_rate_7_days >= 60:
            self.confidence_multiplier = 1.0 + ((self.accuracy_rate_7_days - 60) / 100)
        elif self.accuracy_rate_7_days <= 40:
            self.confidence_multiplier = 0.5 + (self.accuracy_rate_7_days / 80)
        else:
            self.confidence_multiplier = 1.0

        # Ensure within bounds
        self.confidence_multiplier = max(0.5, min(1.5, self.confidence_multiplier))

        self.save()


# =============================================================================
# Session 472: Market Intelligence Provenance & Compliance (Phase 5)
# =============================================================================


class DataProvenance(models.Model):
    """
    Session 472: Market Intelligence Provenance Tracking

    Tracks the complete lineage of data through the Market Intelligence pipeline:
    Spider Data → Opportunity → Score → Validation → Decision → Outcome

    Features:
    - Immutable lineage chain with parent references
    - Source attribution (which spider, which agent, which user)
    - Metadata capture at each stage
    - Compliance verification status
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Data item identification
    entity_type = models.CharField(
        max_length=50,
        choices=[
            ('spider_data', 'Spider Data'),
            ('opportunity', 'Opportunity'),
            ('scoring_result', 'Scoring Result'),
            ('validation_request', 'Validation Request'),
            ('validation_decision', 'Validation Decision'),
            ('outcome', 'Outcome'),
            ('ml_model', 'ML Model'),
            ('alert', 'System Alert'),
        ],
        db_index=True,
        help_text="Type of entity this provenance record tracks"
    )

    entity_id = models.CharField(
        max_length=100,
        db_index=True,
        help_text="ID of the entity (UUID or other identifier)"
    )

    # Lineage chain
    parent = models.ForeignKey(
        'self',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='children',
        help_text="Parent provenance record in the lineage chain"
    )

    root = models.ForeignKey(
        'self',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='descendants',
        help_text="Root provenance record (original spider data)"
    )

    # Lineage depth (0 = root/spider_data, 1 = opportunity, etc.)
    depth = models.PositiveIntegerField(
        default=0,
        help_text="Depth in the lineage chain (0 = root)"
    )

    # Source attribution
    source_type = models.CharField(
        max_length=30,
        choices=[
            ('spider', 'Spider Crawl'),
            ('api', 'External API'),
            ('user_input', 'User Input'),
            ('ml_prediction', 'ML Prediction'),
            ('agent_action', 'Agent Action'),
            ('system', 'System Process'),
            ('human_review', 'Human Review'),
        ],
        help_text="Type of source that created this data"
    )

    source_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Name of the source (spider name, agent name, username, etc.)"
    )

    source_version = models.CharField(
        max_length=50,
        blank=True,
        help_text="Version of the source (model version, spider version, etc.)"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    data_timestamp = models.DateTimeField(
        null=True, blank=True,
        help_text="Original timestamp of the data (may differ from record creation)"
    )

    # Metadata capture
    metadata = models.JSONField(
        default=dict,
        help_text="Full metadata snapshot at this stage"
    )

    # Cryptographic verification
    content_hash = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        help_text="SHA-256 hash of the entity content for integrity verification"
    )

    previous_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="Hash of the parent provenance record (blockchain-style)"
    )

    # Compliance status
    compliance_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Review'),
            ('compliant', 'Compliant'),
            ('non_compliant', 'Non-Compliant'),
            ('exempt', 'Exempt'),
        ],
        default='pending',
        help_text="Compliance verification status"
    )

    compliance_checked_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When compliance was last checked"
    )

    compliance_notes = models.TextField(
        blank=True,
        help_text="Notes from compliance review"
    )

    # User attribution
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='provenance_records_created',
        help_text="User who triggered this data creation (if applicable)"
    )

    class Meta:
        app_label = 'core'
        verbose_name = "Data Provenance"
        verbose_name_plural = "Data Provenance Records"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['source_type', 'source_name']),
            models.Index(fields=['compliance_status']),
            models.Index(fields=['root', 'depth']),
        ]

    def __str__(self):
        return f"{self.entity_type}:{self.entity_id[:8]}... (depth={self.depth})"

    def save(self, *args, **kwargs):
        # Auto-calculate depth and root
        if self.parent:
            self.depth = self.parent.depth + 1
            self.root = self.parent.root or self.parent
            self.previous_hash = self.parent.content_hash
        else:
            self.depth = 0
            self.root = None
            self.previous_hash = ''

        super().save(*args, **kwargs)

    def get_full_lineage(self):
        """Get the complete lineage chain from root to this record."""
        lineage = [self]
        current = self

        while current.parent:
            lineage.insert(0, current.parent)
            current = current.parent

        return lineage

    def get_lineage_summary(self):
        """Get a summary of the lineage chain."""
        lineage = self.get_full_lineage()
        return [
            {
                'id': str(p.id),
                'entity_type': p.entity_type,
                'entity_id': p.entity_id,
                'source_type': p.source_type,
                'source_name': p.source_name,
                'created_at': p.created_at.isoformat(),
                'depth': p.depth,
            }
            for p in lineage
        ]


class AuditLog(models.Model):
    """
    Session 472: Immutable Audit Trail

    Records all significant actions in the Market Intelligence pipeline.
    This log is append-only and designed to be immutable for compliance.

    Features:
    - All scoring, validation, and decision actions
    - User attribution for human actions
    - Agent attribution for automated actions
    - Full before/after state capture
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Action details
    action_type = models.CharField(
        max_length=50,
        choices=[
            # Data collection
            ('spider_crawl', 'Spider Crawl'),
            ('data_import', 'Data Import'),
            # Scoring
            ('ml_score', 'ML Scoring'),
            ('rule_score', 'Rule-Based Scoring'),
            ('hybrid_score', 'Hybrid Scoring'),
            # Validation
            ('validation_queued', 'Validation Queued'),
            ('validation_assigned', 'Validation Assigned'),
            ('validation_approved', 'Validation Approved'),
            ('validation_rejected', 'Validation Rejected'),
            ('validation_escalated', 'Validation Escalated'),
            ('validation_expired', 'Validation Expired'),
            # Decisions
            ('auto_approved', 'Auto-Approved'),
            ('auto_rejected', 'Auto-Rejected'),
            ('human_override', 'Human Override'),
            # Outcomes
            ('outcome_recorded', 'Outcome Recorded'),
            # ML Model
            ('model_trained', 'Model Trained'),
            ('model_deployed', 'Model Deployed'),
            # System
            ('config_changed', 'Configuration Changed'),
            ('alert_triggered', 'Alert Triggered'),
        ],
        db_index=True,
        help_text="Type of action being logged"
    )

    # Actor
    actor_type = models.CharField(
        max_length=20,
        choices=[
            ('user', 'Human User'),
            ('agent', 'AI Agent'),
            ('system', 'System Process'),
            ('scheduler', 'Scheduled Task'),
        ],
        help_text="Type of actor that performed this action"
    )

    actor_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="ID of the actor (user ID, agent ID, or task name)"
    )

    actor_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Human-readable name of the actor"
    )

    # Target entity
    target_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Type of entity being acted upon"
    )

    target_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="ID of the target entity"
    )

    # State capture
    before_state = models.JSONField(
        default=dict,
        help_text="State of the entity before the action (for changes)"
    )

    after_state = models.JSONField(
        default=dict,
        help_text="State of the entity after the action"
    )

    # Provenance link
    provenance = models.ForeignKey(
        DataProvenance,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_logs',
        help_text="Associated provenance record"
    )

    # Context
    context = models.JSONField(
        default=dict,
        help_text="Additional context about the action"
    )

    reason = models.TextField(
        blank=True,
        help_text="Reason for the action (especially for human actions)"
    )

    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # Integrity
    log_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="Hash of the log entry for integrity verification"
    )

    previous_log_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="Hash of the previous log entry (chain verification)"
    )

    # Request tracking
    request_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="Request/correlation ID for tracing"
    )

    ip_address = models.GenericIPAddressField(
        null=True, blank=True,
        help_text="IP address of the request (for user actions)"
    )

    class Meta:
        app_label = 'core'
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action_type', 'timestamp']),
            models.Index(fields=['actor_type', 'actor_id']),
            models.Index(fields=['target_type', 'target_id']),
            models.Index(fields=['request_id']),
        ]

    def __str__(self):
        return f"{self.action_type} by {self.actor_name or self.actor_id} at {self.timestamp}"

    def save(self, *args, **kwargs):
        import hashlib
        import json

        # Generate log hash
        content = json.dumps({
            'action_type': self.action_type,
            'actor_type': self.actor_type,
            'actor_id': self.actor_id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'after_state': self.after_state,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }, sort_keys=True, default=str)

        self.log_hash = hashlib.sha256(content.encode()).hexdigest()

        super().save(*args, **kwargs)


class ComplianceCheck(models.Model):
    """
    Session 472: Compliance Verification Records

    Records compliance checks performed on data and decisions.
    Used for regulatory compliance, data quality assurance, and auditing.

    Features:
    - Rule-based compliance checking
    - Data freshness validation
    - Source attribution requirements
    - Confidence threshold verification
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Target of compliance check
    provenance = models.ForeignKey(
        DataProvenance,
        on_delete=models.CASCADE,
        related_name='compliance_checks',
        help_text="Provenance record being checked"
    )

    # Check details
    check_type = models.CharField(
        max_length=50,
        choices=[
            ('data_freshness', 'Data Freshness'),
            ('source_attribution', 'Source Attribution'),
            ('confidence_threshold', 'Confidence Threshold'),
            ('human_review', 'Human Review Required'),
            ('model_version', 'Model Version Compliance'),
            ('data_quality', 'Data Quality'),
            ('bias_check', 'Bias Detection'),
            ('rate_limit', 'Rate Limit Compliance'),
            ('retention', 'Data Retention'),
            ('privacy', 'Privacy Compliance'),
        ],
        help_text="Type of compliance check"
    )

    # Check configuration
    rule_name = models.CharField(
        max_length=100,
        help_text="Name of the compliance rule"
    )

    rule_version = models.CharField(
        max_length=20,
        default='1.0',
        help_text="Version of the compliance rule"
    )

    rule_config = models.JSONField(
        default=dict,
        help_text="Configuration parameters for the rule"
    )

    # Check result
    passed = models.BooleanField(
        help_text="Whether the check passed"
    )

    severity = models.CharField(
        max_length=20,
        choices=[
            ('info', 'Informational'),
            ('warning', 'Warning'),
            ('error', 'Error'),
            ('critical', 'Critical'),
        ],
        default='warning',
        help_text="Severity if check failed"
    )

    # Result details
    actual_value = models.JSONField(
        null=True, blank=True,
        help_text="Actual value that was checked"
    )

    expected_value = models.JSONField(
        null=True, blank=True,
        help_text="Expected value or threshold"
    )

    message = models.TextField(
        blank=True,
        help_text="Human-readable result message"
    )

    details = models.JSONField(
        default=dict,
        help_text="Additional check details"
    )

    # Remediation
    remediation_required = models.BooleanField(
        default=False,
        help_text="Whether remediation is required"
    )

    remediation_action = models.TextField(
        blank=True,
        help_text="Suggested remediation action"
    )

    remediated = models.BooleanField(
        default=False,
        help_text="Whether the issue has been remediated"
    )

    remediated_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When the issue was remediated"
    )

    remediated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='remediations',
        help_text="User who performed the remediation"
    )

    # Timestamps
    checked_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Audit link
    audit_log = models.ForeignKey(
        AuditLog,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='compliance_checks',
        help_text="Associated audit log entry"
    )

    class Meta:
        app_label = 'core'
        verbose_name = "Compliance Check"
        verbose_name_plural = "Compliance Checks"
        ordering = ['-checked_at']
        indexes = [
            models.Index(fields=['check_type', 'passed']),
            models.Index(fields=['provenance', 'check_type']),
            models.Index(fields=['severity', 'remediated']),
        ]

    def __str__(self):
        status = "PASS" if self.passed else "FAIL"
        return f"{self.check_type} [{status}] - {self.rule_name}"


class ComplianceRule(models.Model):
    """
    Session 472: Compliance Rule Definitions

    Stores configurable compliance rules that can be applied to data.
    Rules are versioned and can be enabled/disabled.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Rule identification
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique name for this rule"
    )

    display_name = models.CharField(
        max_length=200,
        help_text="Human-readable name"
    )

    description = models.TextField(
        blank=True,
        help_text="Description of what this rule checks"
    )

    version = models.CharField(
        max_length=20,
        default='1.0',
        help_text="Version of the rule"
    )

    # Rule type and target
    check_type = models.CharField(
        max_length=50,
        choices=[
            ('data_freshness', 'Data Freshness'),
            ('source_attribution', 'Source Attribution'),
            ('confidence_threshold', 'Confidence Threshold'),
            ('human_review', 'Human Review Required'),
            ('model_version', 'Model Version Compliance'),
            ('data_quality', 'Data Quality'),
            ('bias_check', 'Bias Detection'),
            ('rate_limit', 'Rate Limit Compliance'),
            ('retention', 'Data Retention'),
            ('privacy', 'Privacy Compliance'),
        ],
        help_text="Type of compliance check"
    )

    entity_types = ArrayField(
        models.CharField(max_length=50),
        default=list,
        help_text="Entity types this rule applies to"
    )

    # Rule configuration
    config = models.JSONField(
        default=dict,
        help_text="Rule configuration parameters"
    )

    # Severity and behavior
    severity = models.CharField(
        max_length=20,
        choices=[
            ('info', 'Informational'),
            ('warning', 'Warning'),
            ('error', 'Error'),
            ('critical', 'Critical'),
        ],
        default='warning',
        help_text="Severity level if rule fails"
    )

    blocking = models.BooleanField(
        default=False,
        help_text="Whether a failure blocks the operation"
    )

    auto_remediate = models.BooleanField(
        default=False,
        help_text="Whether to attempt automatic remediation"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this rule is active"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Compliance Rule"
        verbose_name_plural = "Compliance Rules"
        ordering = ['check_type', 'name']

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.display_name} v{self.version} [{status}]"

    @classmethod
    def get_active_rules(cls, entity_type: str = None):
        """Get all active rules, optionally filtered by entity type."""
        rules = cls.objects.filter(is_active=True)

        if entity_type:
            rules = rules.filter(entity_types__contains=[entity_type])

        return rules


# =============================================================================
# PHASE 6: ROI METRICS & ATTRIBUTION (Session 472)
# =============================================================================
# These models track the complete revenue attribution pipeline:
# Spider Source → Opportunity → User Action → Conversion → Revenue


class ConversionEvent(models.Model):
    """
    Tracks conversion funnel events from opportunity to revenue.

    The conversion funnel:
    view → click → apply → interview → convert → revenue

    Session 472: Market Intelligence Architecture - Phase 6
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Event type in conversion funnel
    event_type = models.CharField(
        max_length=30,
        choices=[
            ('view', 'Opportunity Viewed'),
            ('click', 'Link Clicked'),
            ('apply', 'Application Started'),
            ('submit', 'Application Submitted'),
            ('interview', 'Interview Scheduled'),
            ('offer', 'Offer Received'),
            ('convert', 'Conversion Complete'),
            ('revenue', 'Revenue Received'),
            ('churn', 'Customer Churned'),
            ('refund', 'Refund Issued'),
        ],
        db_index=True,
        help_text="Type of conversion event"
    )

    # Link to opportunity
    opportunity = models.ForeignKey(
        'Opportunity',
        on_delete=models.CASCADE,
        related_name='conversion_events',
        null=True,
        blank=True,
        help_text="The opportunity this event relates to"
    )

    # Link to spider data source
    spider_data = models.ForeignKey(
        'SpiderData',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversion_events',
        help_text="Original spider data source"
    )

    # User who triggered the event
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversion_events',
        help_text="User who triggered the event"
    )

    # Session tracking
    session_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Browser/app session ID"
    )

    # Monetary value (for revenue events)
    value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Monetary value if applicable"
    )

    currency = models.CharField(
        max_length=3,
        default='USD',
        help_text="Currency code"
    )

    # Attribution tracking
    attribution_source = models.CharField(
        max_length=100,
        blank=True,
        help_text="Source attribution (spider name, campaign, etc.)"
    )

    attribution_medium = models.CharField(
        max_length=50,
        blank=True,
        help_text="Medium (organic, paid, email, etc.)"
    )

    attribution_campaign = models.CharField(
        max_length=100,
        blank=True,
        help_text="Campaign identifier"
    )

    # Previous event in funnel (for path tracking)
    previous_event = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='next_events',
        help_text="Previous event in conversion path"
    )

    # Metadata
    metadata = models.JSONField(
        default=dict,
        help_text="Additional event metadata"
    )

    # Timestamps
    event_timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="When the event occurred"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Conversion Event"
        verbose_name_plural = "Conversion Events"
        ordering = ['-event_timestamp']
        indexes = [
            models.Index(fields=['event_type', 'event_timestamp']),
            models.Index(fields=['attribution_source', 'event_timestamp']),
            models.Index(fields=['user', 'event_timestamp']),
        ]

    def __str__(self):
        value_str = f" (${self.value})" if self.value else ""
        return f"{self.event_type}{value_str} - {self.event_timestamp.date()}"

    @property
    def funnel_position(self) -> int:
        """Position in the conversion funnel (0-7)."""
        funnel_order = ['view', 'click', 'apply', 'submit', 'interview', 'offer', 'convert', 'revenue']
        try:
            return funnel_order.index(self.event_type)
        except ValueError:
            return -1

    def get_conversion_path(self) -> list:
        """Get the full conversion path leading to this event."""
        path = [self]
        current = self

        while current.previous_event:
            path.insert(0, current.previous_event)
            current = current.previous_event

        return path


class ROIMetric(models.Model):
    """
    Aggregated ROI metrics by source, time period, and dimension.

    Tracks cost, revenue, and derived metrics for ROI analysis.

    Session 472: Market Intelligence Architecture - Phase 6
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Time period
    period_type = models.CharField(
        max_length=20,
        choices=[
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('yearly', 'Yearly'),
        ],
        db_index=True,
        help_text="Aggregation period"
    )

    period_start = models.DateTimeField(
        db_index=True,
        help_text="Start of the period"
    )

    period_end = models.DateTimeField(
        help_text="End of the period"
    )

    # Dimension for grouping
    dimension = models.CharField(
        max_length=50,
        choices=[
            ('overall', 'Overall Platform'),
            ('spider_source', 'By Spider Source'),
            ('opportunity_category', 'By Opportunity Category'),
            ('user_segment', 'By User Segment'),
            ('agent', 'By Agent'),
            ('campaign', 'By Campaign'),
        ],
        db_index=True,
        help_text="Grouping dimension"
    )

    dimension_value = models.CharField(
        max_length=200,
        db_index=True,
        help_text="Value of the dimension (e.g., spider name)"
    )

    # Funnel metrics (counts)
    views = models.IntegerField(default=0, help_text="Number of views")
    clicks = models.IntegerField(default=0, help_text="Number of clicks")
    applications = models.IntegerField(default=0, help_text="Number of applications")
    conversions = models.IntegerField(default=0, help_text="Number of conversions")

    # Financial metrics
    total_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        help_text="Total revenue generated"
    )

    total_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        help_text="Total cost (API calls, compute, etc.)"
    )

    # Calculated metrics (stored for query performance)
    click_through_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="CTR = clicks / views"
    )

    conversion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="CR = conversions / applications"
    )

    cost_per_acquisition = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="CPA = cost / conversions"
    )

    return_on_investment = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="ROI = (revenue - cost) / cost"
    )

    average_revenue_per_user = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="ARPU = revenue / unique users"
    )

    lifetime_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated LTV"
    )

    # Unique counts
    unique_users = models.IntegerField(
        default=0,
        help_text="Unique users in period"
    )

    unique_opportunities = models.IntegerField(
        default=0,
        help_text="Unique opportunities viewed"
    )

    # Timestamps
    calculated_at = models.DateTimeField(
        auto_now=True,
        help_text="When metrics were last calculated"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "ROI Metric"
        verbose_name_plural = "ROI Metrics"
        ordering = ['-period_start', 'dimension']
        unique_together = ['period_type', 'period_start', 'dimension', 'dimension_value']
        indexes = [
            models.Index(fields=['dimension', 'dimension_value', 'period_start']),
        ]

    def __str__(self):
        return f"{self.dimension}:{self.dimension_value} ({self.period_type} {self.period_start.date()})"

    def calculate_derived_metrics(self):
        """Calculate all derived metrics from base counts."""
        from decimal import Decimal

        # Click-through rate
        if self.views > 0:
            self.click_through_rate = Decimal(self.clicks) / Decimal(self.views)
        else:
            self.click_through_rate = None

        # Conversion rate
        if self.applications > 0:
            self.conversion_rate = Decimal(self.conversions) / Decimal(self.applications)
        else:
            self.conversion_rate = None

        # Cost per acquisition
        if self.conversions > 0:
            self.cost_per_acquisition = self.total_cost / Decimal(self.conversions)
        else:
            self.cost_per_acquisition = None

        # Return on investment
        if self.total_cost > 0:
            self.return_on_investment = (self.total_revenue - self.total_cost) / self.total_cost
        else:
            self.return_on_investment = None

        # Average revenue per user
        if self.unique_users > 0:
            self.average_revenue_per_user = self.total_revenue / Decimal(self.unique_users)
        else:
            self.average_revenue_per_user = None


class AttributionPath(models.Model):
    """
    Tracks the complete attribution path from data source to revenue.

    Maps the journey: Spider → Opportunity → User Actions → Revenue

    Session 472: Market Intelligence Architecture - Phase 6
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Final conversion event (revenue)
    conversion_event = models.OneToOneField(
        ConversionEvent,
        on_delete=models.CASCADE,
        related_name='attribution_path',
        help_text="The final conversion/revenue event"
    )

    # Attribution model used
    attribution_model = models.CharField(
        max_length=30,
        choices=[
            ('first_touch', 'First Touch'),
            ('last_touch', 'Last Touch'),
            ('linear', 'Linear'),
            ('time_decay', 'Time Decay'),
            ('position_based', 'Position Based'),
            ('data_driven', 'Data Driven'),
        ],
        default='last_touch',
        help_text="Attribution model used"
    )

    # Path components (ordered list of touchpoints)
    path_data = models.JSONField(
        default=list,
        help_text="Ordered list of touchpoints in the path"
    )

    # Path statistics
    path_length = models.IntegerField(
        default=0,
        help_text="Number of touchpoints"
    )

    time_to_conversion_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Hours from first touch to conversion"
    )

    # Attribution credits (for multi-touch models)
    attribution_credits = models.JSONField(
        default=dict,
        help_text="Credit distribution by source"
    )

    # Primary attributed source
    primary_source = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="Primary source for this conversion"
    )

    primary_source_credit = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=1.0,
        help_text="Credit assigned to primary source (0-1)"
    )

    # Value attribution
    attributed_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Value attributed to this path"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Attribution Path"
        verbose_name_plural = "Attribution Paths"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['primary_source', 'created_at']),
            models.Index(fields=['attribution_model', 'created_at']),
        ]

    def __str__(self):
        return f"{self.primary_source} → ${self.attributed_value} ({self.attribution_model})"

    def calculate_credits(self):
        """Calculate attribution credits based on the selected model."""
        from decimal import Decimal

        if not self.path_data:
            return

        num_touchpoints = len(self.path_data)
        if num_touchpoints == 0:
            return

        credits = {}

        if self.attribution_model == 'first_touch':
            # All credit to first touchpoint
            first = self.path_data[0]
            source = first.get('source', 'unknown')
            credits[source] = 1.0

        elif self.attribution_model == 'last_touch':
            # All credit to last touchpoint
            last = self.path_data[-1]
            source = last.get('source', 'unknown')
            credits[source] = 1.0

        elif self.attribution_model == 'linear':
            # Equal credit to all touchpoints
            credit_per = 1.0 / num_touchpoints
            for touchpoint in self.path_data:
                source = touchpoint.get('source', 'unknown')
                credits[source] = credits.get(source, 0) + credit_per

        elif self.attribution_model == 'time_decay':
            # More credit to recent touchpoints
            total_weight = sum(range(1, num_touchpoints + 1))
            for i, touchpoint in enumerate(self.path_data):
                source = touchpoint.get('source', 'unknown')
                weight = (i + 1) / total_weight
                credits[source] = credits.get(source, 0) + weight

        elif self.attribution_model == 'position_based':
            # 40% first, 40% last, 20% distributed among middle
            if num_touchpoints == 1:
                source = self.path_data[0].get('source', 'unknown')
                credits[source] = 1.0
            elif num_touchpoints == 2:
                credits[self.path_data[0].get('source', 'unknown')] = 0.5
                credits[self.path_data[-1].get('source', 'unknown')] = \
                    credits.get(self.path_data[-1].get('source', 'unknown'), 0) + 0.5
            else:
                # First and last get 40% each
                credits[self.path_data[0].get('source', 'unknown')] = 0.4
                credits[self.path_data[-1].get('source', 'unknown')] = \
                    credits.get(self.path_data[-1].get('source', 'unknown'), 0) + 0.4

                # Middle touchpoints share 20%
                middle_count = num_touchpoints - 2
                if middle_count > 0:
                    middle_credit = 0.2 / middle_count
                    for touchpoint in self.path_data[1:-1]:
                        source = touchpoint.get('source', 'unknown')
                        credits[source] = credits.get(source, 0) + middle_credit

        self.attribution_credits = credits

        # Set primary source (highest credit)
        if credits:
            self.primary_source = max(credits, key=credits.get)
            self.primary_source_credit = Decimal(str(credits[self.primary_source]))


class WeeklyIntelligenceBrief(models.Model):
    """
    Weekly intelligence brief summarizing ROI and performance.

    Auto-generated summary for stakeholders.

    Session 472: Market Intelligence Architecture - Phase 6
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Time period
    week_start = models.DateField(
        db_index=True,
        help_text="Start of the week"
    )

    week_end = models.DateField(
        help_text="End of the week"
    )

    # Summary metrics
    total_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    total_conversions = models.IntegerField(default=0)
    total_opportunities = models.IntegerField(default=0)
    total_spider_records = models.IntegerField(default=0)

    # Week-over-week changes
    revenue_change_pct = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="% change from previous week"
    )

    conversions_change_pct = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Top performers
    top_spider_sources = models.JSONField(
        default=list,
        help_text="Top performing spider sources"
    )

    top_opportunity_categories = models.JSONField(
        default=list,
        help_text="Top performing categories"
    )

    top_agents = models.JSONField(
        default=list,
        help_text="Top performing agents"
    )

    # Insights and recommendations
    key_insights = models.JSONField(
        default=list,
        help_text="AI-generated insights"
    )

    recommendations = models.JSONField(
        default=list,
        help_text="AI-generated recommendations"
    )

    # Full report content
    executive_summary = models.TextField(
        blank=True,
        help_text="Executive summary text"
    )

    detailed_report = models.JSONField(
        default=dict,
        help_text="Full detailed report data"
    )

    # Generation status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Generation'),
            ('generating', 'Generating'),
            ('complete', 'Complete'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )

    generation_error = models.TextField(blank=True)

    # Timestamps
    generated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Weekly Intelligence Brief"
        verbose_name_plural = "Weekly Intelligence Briefs"
        ordering = ['-week_start']
        unique_together = ['week_start']

    def __str__(self):
        return f"Week of {self.week_start} - ${self.total_revenue}"


# ============================================================================
# DAVINCI RESOLVE INTEGRATION MODELS
# Session 478: Full Utilization of $300 DaVinci Resolve Investment
# ============================================================================

class ResolveRenderJob(models.Model):
    """
    Tracks DaVinci Resolve render jobs and their outcomes for learning.

    Session 478: DaVinci Resolve Full Utilization

    This model:
    1. Tracks render jobs sent to resolve_node
    2. Stores spider trends that influenced color grade selection
    3. Records user feedback for the learning loop
    4. Enables performance-based grade recommendations

    The learning loop uses this data to improve automatic color grade
    selection over time based on user ratings and usage patterns.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resolve_render_jobs'
    )

    # === Job Identification ===
    resolve_job_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Job ID from resolve_node server"
    )

    # === Job Status ===
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('rendering', 'Rendering'),
        ('done', 'Done'),
        ('error', 'Error'),
        ('uploading', 'Uploading'),
        ('uploaded', 'Uploaded'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='queued'
    )

    # === Input Configuration ===
    source_video_ids = models.JSONField(
        default=list,
        help_text="List of source video IDs that were rendered"
    )

    TEMPLATE_CHOICES = [
        ('default_mp4', 'Default MP4 (1080p H.264)'),
        ('high_quality', 'High Quality (Multi-pass)'),
    ]
    template = models.CharField(
        max_length=50,
        choices=TEMPLATE_CHOICES,
        default='default_mp4'
    )

    color_grade = models.CharField(
        max_length=50,
        blank=True,
        help_text="Color grade preset applied (e.g., cinematic_warm, cyberpunk_neon)"
    )

    # === Spider Context (what trends influenced this render) ===
    spider_trends_used = models.JSONField(
        default=dict,
        help_text="Spider creative trends at time of render (for learning)"
    )

    auto_grade_selected = models.BooleanField(
        default=False,
        help_text="Was the color grade automatically selected based on trends?"
    )

    # === Output Information ===
    output_url = models.URLField(
        blank=True,
        help_text="URL to download the rendered video"
    )

    output_file_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Local file path of rendered video"
    )

    file_size_mb = models.FloatField(
        null=True,
        blank=True,
        help_text="Output file size in megabytes"
    )

    render_duration_seconds = models.IntegerField(
        null=True,
        blank=True,
        help_text="How long the render took"
    )

    # === Error Information ===
    error_message = models.TextField(
        blank=True,
        help_text="Error message if status is 'error'"
    )

    # === Learning Loop - Outcome Tracking ===
    user_rating = models.IntegerField(
        null=True,
        blank=True,
        help_text="User rating 1-5 (for learning which grades work best)"
    )

    user_feedback = models.TextField(
        blank=True,
        help_text="Optional user feedback on the render quality"
    )

    was_used = models.BooleanField(
        default=False,
        help_text="Did the user actually use/publish this output?"
    )

    revenue_generated = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Revenue attributed to this render (for ROI tracking)"
    )

    # === Timestamps ===
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Resolve Render Job"
        verbose_name_plural = "Resolve Render Jobs"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['color_grade', 'user_rating']),
            models.Index(fields=['auto_grade_selected']),
        ]

    def __str__(self):
        return f"Resolve Job {self.resolve_job_id[:8]} - {self.status} ({self.color_grade or 'no grade'})"

    @property
    def is_complete(self) -> bool:
        """Check if job is complete."""
        return self.status in ['done', 'uploaded']

    @property
    def has_feedback(self) -> bool:
        """Check if user has provided feedback."""
        return self.user_rating is not None

    def get_outcome_score(self) -> float:
        """
        Calculate outcome score for learning loop.

        Score = (rating/5) * usage_factor * revenue_factor

        Returns:
            Float between 0.0 and 1.0+ (can exceed 1.0 with revenue)
        """
        if not self.user_rating:
            return 0.0

        base_score = self.user_rating / 5.0
        usage_factor = 1.5 if self.was_used else 1.0
        revenue_factor = 1.0 + (float(self.revenue_generated or 0) / 100)

        return base_score * usage_factor * revenue_factor


# =============================================================================
# SELF-AWARE BLOG - Session 543
# =============================================================================

class SelfBlog(models.Model):
    """
    Stores blog posts written by the system about itself.
    A meta-demonstration of the platform's capabilities.
    Session 814: Added category field to support technical documents/audits.
    Session 833: Added status field for approval workflow.
    Session 862: Added content_type for routing (public vs internal) and quality scoring.
    """
    CATEGORY_CHOICES = [
        ('blog', 'Blog Post'),
        ('audit', 'System Audit'),
        ('technical_document', 'Technical Document'),
        ('prototype_plan', 'Prototype Plan'),
        ('research_brief', 'Research Brief'),
        # Session 862: New internal content types
        ('build_log', 'Build Log'),
        ('internal_note', 'Internal Note'),
        ('playbook', 'Playbook/Doctrine'),
        ('dossier', 'Strategic Dossier'),
    ]

    # Session 862: Content type determines routing (public vs internal)
    CONTENT_TYPE_CHOICES = [
        ('public', 'Public Content'),      # For external audience, SEO, marketing
        ('internal', 'Internal Content'),  # For system learning, team reference
        ('strategic', 'Strategic Content'), # For operators, partners, investors
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),  # Session 862: Awaiting quality gate
        ('needs_enhancement', 'Needs Enhancement'),  # Session 862: Failed quality gate
        ('approved', 'Approved'),
        ('published', 'Published'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Workspace linkage
    workspace = models.ForeignKey(
        'core.ProjectWorkspace', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='blogs', db_index=True,
    )

    # Session 843: Orchestration Contract fields
    trace_id = models.UUIDField(
        null=True, blank=True, db_index=True,
        help_text="Session 843: Trace ID for cross-artifact linking"
    )
    project = models.ForeignKey(
        'core.PartnershipProject',
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name='self_blogs',
        help_text="Session 843: Project this blog belongs to"
    )

    # Session 862: Content Flow Traceability
    initiative = models.ForeignKey(
        'core.Initiative',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blogs',
        help_text="Session 862: Initiative this blog belongs to"
    )
    dream = models.ForeignKey(
        'AgentDream',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blogs',
        help_text="Session 862: Dream that originated this blog"
    )
    initiative_stage = models.ForeignKey(
        'core.InitiativeStage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blogs',
        help_text="Session 862: Initiative stage this blog fulfills"
    )

    title = models.CharField(max_length=255)
    author = models.CharField(
        max_length=100, blank=True, default='',
        help_text='Session 998: Author — agent name or "human"'
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='blog', db_index=True)
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        default='public',
        db_index=True,
        help_text="Session 862: Determines routing - public (external), internal (learning), strategic (operators)"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True)

    # Session 862: Quality scoring for PublishGate
    quality_score = models.FloatField(
        null=True, blank=True,
        help_text="Overall content quality (0-1)"
    )
    novelty_score = models.FloatField(
        null=True, blank=True,
        help_text="How unique vs existing content (0-1)"
    )
    structure_score = models.FloatField(
        null=True, blank=True,
        help_text="Section variety, hooks, formatting (0-1)"
    )
    publish_ready = models.BooleanField(
        default=False,
        help_text="True if passed PublishGate quality checks"
    )
    gate_notes = models.TextField(
        blank=True,
        help_text="Session 862: Notes from PublishGate evaluation"
    )

    meta_description = models.TextField(blank=True)
    intro = models.TextField(blank=True)
    sections = models.JSONField(default=list, help_text="List of {header, content} sections")
    conclusion = models.TextField(blank=True)
    tags = models.JSONField(default=list)
    full_text = models.TextField(help_text="Complete blog as markdown")

    # Generation metadata
    tone = models.CharField(max_length=50, default="professional")
    word_count = models.IntegerField(default=0)

    # System stats at generation time
    stats_snapshot = models.JSONField(default=dict, help_text="System stats when blog was generated")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Self Blog"
        verbose_name_plural = "Self Blogs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.created_at.strftime('%Y-%m-%d')})"

    def save(self, *args, **kwargs):
        """Session 833: Auto-calculate word_count from full_text on save."""
        if self.full_text and not self.word_count:
            # Count words in full_text (strip markdown formatting)
            import re
            text = re.sub(r'[#*`\[\]()_~>-]', ' ', self.full_text)
            self.word_count = len(text.split())
        super().save(*args, **kwargs)


# =============================================================================
# AUTONOMOUS REASONING ENGINE - Session 544
# The system that thinks, decides, and acts based on accumulated knowledge
# =============================================================================

class ThoughtRecord(models.Model):
    """
    Records of the system's thinking process.
    Each record represents one thinking cycle where the system:
    1. Gathered context from recent learning
    2. Reflected and identified patterns
    3. Made decisions about actions to take
    4. Executed those actions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Thinking cycle identification
    cycle_number = models.IntegerField(help_text="Sequential thinking cycle number")
    cycle_type = models.CharField(
        max_length=50,
        default="scheduled",
        choices=[
            ("scheduled", "Scheduled Cycle"),
            ("triggered", "Event Triggered"),
            ("manual", "Manual Request"),
            ("continuous", "Continuous Mode"),
        ]
    )

    # Context gathered for this thinking cycle
    context_summary = models.TextField(help_text="Summary of data considered")
    context_data = models.JSONField(default=dict, help_text="Raw context data snapshot")

    # The thinking process
    reflection = models.TextField(help_text="System's reflection on the context")
    insights = models.JSONField(default=list, help_text="Key insights identified")
    patterns = models.JSONField(default=list, help_text="Patterns noticed across data")
    opportunities = models.JSONField(default=list, help_text="Opportunities identified")
    concerns = models.JSONField(default=list, help_text="Risks or concerns noted")

    # Decision making
    decisions = models.JSONField(default=list, help_text="Decisions made and reasoning")
    priority_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Overall priority/importance of this cycle's insights"
    )

    # Actions
    actions_planned = models.JSONField(default=list, help_text="Actions planned to take")
    actions_executed = models.JSONField(default=list, help_text="Actions actually executed")

    # Outcome tracking
    execution_status = models.CharField(
        max_length=20,
        default="pending",
        choices=[
            ("pending", "Pending"),
            ("thinking", "Thinking"),
            ("deciding", "Deciding"),
            ("executing", "Executing"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ]
    )

    # Metadata
    thinking_duration_seconds = models.FloatField(default=0.0)
    model_used = models.CharField(max_length=50, default="gpt-5-mini")
    token_usage = models.JSONField(default=dict)

    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Thought Record"
        verbose_name_plural = "Thought Records"
        ordering = ["-started_at"]

    def __str__(self):
        return f"Thought #{self.cycle_number} ({self.execution_status}) - {self.started_at.strftime('%Y-%m-%d %H:%M')}"

    @property
    def insights_count(self):
        return len(self.insights) if self.insights else 0

    @property
    def actions_count(self):
        return len(self.actions_executed) if self.actions_executed else 0


class AutonomousAction(models.Model):
    """
    Individual actions taken by the Autonomous Reasoning Engine.
    Each action is linked to a ThoughtRecord that spawned it.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to the thinking that spawned this action
    thought_record = models.ForeignKey(
        ThoughtRecord,
        on_delete=models.CASCADE,
        related_name="actions"
    )

    # Action definition
    action_type = models.CharField(
        max_length=50,
        choices=[
            ("spawn_spider", "Spawn Spider Crawl"),
            ("generate_content", "Generate Content"),
            ("trigger_debate", "Trigger Agent Debate"),
            ("create_report", "Create Report"),
            ("send_alert", "Send Alert/Notification"),
            ("request_research", "Request Deep Research"),
            ("schedule_followup", "Schedule Follow-up"),
            ("trigger_conversation", "Trigger Agent Conversation"),
            ("update_strategy", "Update Strategy"),
            ("archive_insight", "Archive Important Insight"),
        ]
    )
    action_name = models.CharField(max_length=200, help_text="Human-readable action name")
    action_params = models.JSONField(default=dict, help_text="Parameters for the action")

    # Reasoning
    reasoning = models.TextField(help_text="Why this action was chosen")
    expected_outcome = models.TextField(blank=True, help_text="What we expect to happen")

    # Priority and urgency
    priority = models.CharField(
        max_length=20,
        default="medium",
        choices=[
            ("critical", "Critical - Execute Immediately"),
            ("high", "High Priority"),
            ("medium", "Medium Priority"),
            ("low", "Low Priority"),
            ("background", "Background Task"),
        ]
    )

    # Execution status
    status = models.CharField(
        max_length=20,
        default="pending",
        choices=[
            ("pending", "Pending"),
            ("queued", "Queued"),
            ("executing", "Executing"),
            ("completed", "Completed"),
            ("failed", "Failed"),
            ("cancelled", "Cancelled"),
        ]
    )

    # Results
    result = models.JSONField(default=dict, help_text="Result of the action")
    result_summary = models.TextField(blank=True, help_text="Human-readable result summary")
    error_message = models.TextField(blank=True, help_text="Error message if failed")

    # Outcome evaluation (for learning)
    outcome_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1-5 rating of how well the action worked"
    )
    outcome_notes = models.TextField(blank=True, help_text="Notes on the outcome")

    # Celery task tracking
    celery_task_id = models.CharField(max_length=100, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Autonomous Action"
        verbose_name_plural = "Autonomous Actions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action_type}: {self.action_name} ({self.status})"

    @property
    def duration_seconds(self):
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class TrackedConcern(models.Model):
    """
    Tracks concerns across thinking cycles to ensure they are addressed.

    Each concern identified by the ThinkingAgent is tracked here to create
    a feedback loop that verifies whether concerns are actually resolved.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Concern identification
    concern_hash = models.CharField(
        max_length=64,
        unique=True,
        help_text="Hash of concern text for deduplication"
    )
    concern_text = models.TextField(help_text="The concern description")
    category = models.CharField(
        max_length=50,
        default="general",
        help_text="Category of concern (e.g., spider_activity, knowledge_silos, decision_bottleneck)"
    )
    severity = models.CharField(
        max_length=20,
        default="medium",
        choices=[
            ("critical", "Critical"),
            ("high", "High"),
            ("medium", "Medium"),
            ("low", "Low"),
        ]
    )

    # Lifecycle tracking
    status = models.CharField(
        max_length=20,
        default="active",
        choices=[
            ("active", "Active - Not yet addressed"),
            ("in_progress", "In Progress - Actions taken"),
            ("monitoring", "Monitoring - Awaiting verification"),
            ("resolved", "Resolved - Verified fixed"),
            ("recurring", "Recurring - Came back after resolution"),
            ("accepted", "Accepted - Known limitation"),
        ]
    )

    # Origin tracking
    first_seen_cycle = models.ForeignKey(
        ThoughtRecord,
        on_delete=models.SET_NULL,
        null=True,
        related_name="concerns_first_seen",
        help_text="Thinking cycle where this concern first appeared"
    )
    last_seen_cycle = models.ForeignKey(
        ThoughtRecord,
        on_delete=models.SET_NULL,
        null=True,
        related_name="concerns_last_seen",
        help_text="Most recent cycle where this concern was detected"
    )
    times_detected = models.IntegerField(default=1, help_text="How many cycles detected this concern")

    # Actions taken to address it
    actions_taken = models.ManyToManyField(
        AutonomousAction,
        blank=True,
        related_name="addressed_concerns",
        help_text="Actions taken to address this concern"
    )

    # Verification
    verification_metric = models.CharField(
        max_length=100,
        blank=True,
        help_text="What metric to check to verify resolution (e.g., 'spider_data_24h > 0')"
    )
    last_verification_at = models.DateTimeField(null=True, blank=True)
    last_verification_result = models.JSONField(
        default=dict,
        help_text="Result of the last verification check"
    )
    resolution_notes = models.TextField(blank=True, help_text="Notes on how it was resolved")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Tracked Concern"
        verbose_name_plural = "Tracked Concerns"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.status}] {self.concern_text[:50]}..."

    @property
    def days_active(self):
        """How many days this concern has been active."""
        if self.resolved_at:
            return (self.resolved_at - self.created_at).days
        return (timezone.now() - self.created_at).days

    @property
    def is_stale(self):
        """Concern is stale if active for more than 7 days without resolution."""
        return self.status == 'active' and self.days_active > 7


class ReasoningConfiguration(models.Model):
    """
    Configuration for the Autonomous Reasoning Engine.
    Controls how often and how aggressively the system thinks and acts.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Enable/disable
    is_active = models.BooleanField(default=True, help_text="Whether the reasoning engine is active")

    # Timing
    thinking_interval_minutes = models.IntegerField(
        default=60,
        help_text="How often to run thinking cycles (in minutes)"
    )

    # Thresholds
    min_insights_to_act = models.IntegerField(
        default=1,
        help_text="Minimum insights needed before taking action"
    )
    min_priority_to_act = models.FloatField(
        default=3.0,
        help_text="Minimum priority score to execute actions"
    )
    max_actions_per_cycle = models.IntegerField(
        default=5,
        help_text="Maximum actions to take per thinking cycle"
    )

    # Action permissions
    allowed_actions = models.JSONField(
        default=list,
        help_text="List of action types the engine is allowed to perform"
    )

    # Safety
    require_approval_above_priority = models.FloatField(
        default=8.0,
        help_text="Priority threshold above which human approval is required"
    )

    # Context gathering
    lookback_hours = models.IntegerField(
        default=24,
        help_text="How far back to look for context data"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Reasoning Configuration"
        verbose_name_plural = "Reasoning Configurations"

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"Reasoning Config ({status}) - Every {self.thinking_interval_minutes}min"

    @classmethod
    def get_active_config(cls):
        """Get the active configuration, creating default if needed"""
        config = cls.objects.filter(is_active=True).first()
        if not config:
            config = cls.objects.create(
                is_active=True,
                allowed_actions=[
                    "spawn_spider",
                    "generate_content",
                    "trigger_debate",
                    "create_report",
                    "send_alert",
                    "request_research",
                    "trigger_conversation",
                    "archive_insight",
                ]
            )
        return config


# =============================================================================
# Session 875: Context Tracing - Bad Context Event Model
# =============================================================================

class BadContextEvent(models.Model):
    """
    Records context type violations for forensic analysis.

    When agent execution context is unexpectedly a list instead of dict,
    this model captures the trace ID, stage, and diagnostic data to help
    identify where context type mutations occur in the pipeline.

    Stages in the execution pipeline:
    - llm_raw: Raw output from LLM before parsing
    - parser: After parsing LLM output into structured data
    - pre_enqueue: Before enqueuing to Celery task queue
    - post_deserialize: After Celery deserializes the task
    - router: In the agent router before dispatching
    - agent: At the agent's execute() method entry point
    """

    STAGE_CHOICES = [
        ('llm_raw', 'LLM Raw Output'),
        ('parser', 'Parser Output'),
        ('pre_enqueue', 'Pre-Enqueue'),
        ('post_deserialize', 'Post-Deserialize'),
        ('router', 'Router'),
        ('agent', 'Agent Entry'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Correlation tracking
    trace_id = models.CharField(
        max_length=64,
        db_index=True,
        help_text="Unique trace ID for correlating events across the pipeline"
    )

    # Pipeline location
    stage = models.CharField(
        max_length=32,
        choices=STAGE_CHOICES,
        db_index=True,
        help_text="Stage in the execution pipeline where the bad context was detected"
    )

    # Context identification
    agent_name = models.CharField(
        max_length=128,
        blank=True,
        db_index=True,
        help_text="Name of the agent being executed (if known at this stage)"
    )
    action_name = models.CharField(
        max_length=128,
        blank=True,
        help_text="Name of the action/next_step being executed"
    )
    task_name = models.CharField(
        max_length=256,
        blank=True,
        help_text="Celery task name if applicable"
    )

    # Context diagnostics
    context_type = models.CharField(
        max_length=64,
        help_text="The actual type received (e.g., 'list', 'str', 'NoneType')"
    )
    context_preview = models.TextField(
        blank=True,
        help_text="Truncated string representation of the bad context (max 1000 chars)"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error message or diagnostic information"
    )

    # Additional context
    extra_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional diagnostic data (e.g., raw LLM preview, parent trace)"
    )
    source = models.CharField(
        max_length=256,
        blank=True,
        help_text="Source of the trace (e.g., conversation_id, task_id)"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Bad Context Event"
        verbose_name_plural = "Bad Context Events"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['trace_id', 'stage']),
            models.Index(fields=['agent_name', 'created_at']),
            models.Index(fields=['context_type', 'created_at']),
        ]

    def __str__(self):
        return f"BadContext[{self.trace_id[:8]}] {self.stage}: {self.context_type}"

    @classmethod
    def get_recent_by_agent(cls, agent_name: str, limit: int = 10):
        """Get recent bad context events for a specific agent."""
        return cls.objects.filter(
            agent_name=agent_name
        ).order_by('-created_at')[:limit]

    @classmethod
    def get_recent_by_trace(cls, trace_id: str):
        """Get all events for a specific trace ID."""
        return cls.objects.filter(trace_id=trace_id).order_by('created_at')

    @classmethod
    def get_stage_summary(cls, hours: int = 24):
        """Get summary of bad context events by stage for the past N hours."""
        from datetime import timedelta
        from django.db.models import Count
        from django.utils import timezone

        cutoff = timezone.now() - timedelta(hours=hours)
        return cls.objects.filter(
            created_at__gte=cutoff
        ).values('stage', 'context_type').annotate(
            count=Count('id')
        ).order_by('-count')


# =============================================================================
# Session 914.7: Operating Rhythm - Founder Feedback Model
# =============================================================================

class FounderFeedback(models.Model):
    """
    Session 914.7: Store founder feedback for operating rhythm.

    Captures:
    - Daily priorities (Top 3)
    - Weekly feedback (Ship/Learn/Kill response)
    - Becomes training signal for agents
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    FEEDBACK_TYPE_CHOICES = [
        ('daily_priorities', 'Daily Priorities'),
        ('weekly_feedback', 'Weekly Feedback'),
        ('initiative_feedback', 'Initiative-Specific Feedback'),
        ('agent_feedback', 'Agent Performance Feedback'),
    ]

    feedback_type = models.CharField(
        max_length=32,
        choices=FEEDBACK_TYPE_CHOICES,
        db_index=True,
        help_text='Session 914.7: Type of feedback'
    )

    content = models.JSONField(
        default=dict,
        help_text='Session 914.7: Feedback content (priorities, text, etc.)'
    )

    created_by = models.CharField(
        max_length=100,
        default='founder',
        help_text='Session 914.7: Who submitted this feedback'
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Track if this feedback has been processed as a learning signal
    processed_as_learning = models.BooleanField(
        default=False,
        help_text='Session 914.7: Has this been converted to agent learning?'
    )

    processed_at = models.DateTimeField(
        null=True, blank=True,
        help_text='Session 914.7: When was this processed?'
    )

    class Meta:
        app_label = 'core'
        verbose_name = "Founder Feedback"
        verbose_name_plural = "Founder Feedback"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['feedback_type', 'created_at']),
        ]

    def __str__(self):
        return f"FounderFeedback[{self.feedback_type}] {self.created_at.date()}"

