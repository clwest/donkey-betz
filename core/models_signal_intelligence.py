"""
Signal Intelligence Models - Session 900

Provides provenance tracking for why conversations and initiatives happen.
Links spider signals → patterns → auto-topics → conversations → decisions → initiatives.

This transforms "scheduled conversation" from useless metadata into
actionable intelligence showing WHY a discussion happened.

The chain:
    SpiderData[] (multiple signals)
        ↓
    SignalCluster (pattern from signals)
        ↓
    AutoTopic (why THIS topic was chosen)
        ↓
    HiveMindSession (linked to AutoTopic)
        ↓
    AgentDecisionSummary
        ↓
    Initiative
"""

import uuid
from django.db import models
from django.utils import timezone


class SignalCluster(models.Model):
    """
    Session 900: Groups related spider signals into a detected pattern.

    When multiple spiders detect related signals (e.g., Bluesky posts about
    personas, Reddit threads about customer research, job listings for persona
    roles), they form a SignalCluster that represents a meaningful pattern.

    This answers: "What signals triggered this conversation?"

    Example:
        SignalCluster(
            name="Persona research demand spike",
            source_breakdown={"bluesky": 12, "reddit": 6, "job_listings": 4},
            strength=0.81,
            keywords=["persona", "customer research", "user profiles"]
        )
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Session 1131: monotonic cursor for the signal-studio replay endpoint
    # (GET /api/fleet/signals/clusters?since=<seq>). Postgres-managed
    # sequence; Django 5 db_default keeps the INSERT free of the column
    # so the server-side nextval() fires. See migration 0347.
    seq = models.BigIntegerField(
        unique=True,
        editable=False,
        db_default=models.expressions.RawSQL(
            "nextval('core_signalcluster_seq')", []
        ),
        help_text=(
            "Monotonic cluster sequence number assigned by Postgres at "
            "INSERT via the `core_signalcluster_seq` sequence. Canonical "
            "ordering cursor for the signal-studio replay endpoint "
            "(`?since=<seq>` is exclusive). Django 5 `db_default` omits "
            "this column from INSERTs so the sequence fires server-side."
        ),
    )

    # Human-readable pattern name
    name = models.CharField(
        max_length=200,
        help_text="Descriptive name for this signal pattern"
    )

    # Pattern classification
    PATTERN_TYPE_CHOICES = [
        ('demand_spike', 'Demand Spike'),           # Increased interest in topic
        ('trend_emergence', 'Trend Emergence'),     # New trend appearing
        ('sentiment_shift', 'Sentiment Shift'),     # Opinion change detected
        ('opportunity_window', 'Opportunity Window'), # Time-sensitive opportunity
        ('knowledge_gap', 'Knowledge Gap'),         # Missing information detected
        ('competitive_signal', 'Competitive Signal'), # Competitor activity
        ('market_movement', 'Market Movement'),     # Market/price signals
        ('skill_demand', 'Skill Demand'),           # Job market signals
        ('content_gap', 'Content Gap'),             # Underserved content area
        ('user_need', 'User Need'),                 # Direct user need detected
    ]
    pattern_type = models.CharField(
        max_length=30,
        choices=PATTERN_TYPE_CHOICES,
        default='demand_spike',
        help_text="Classification of the detected pattern"
    )

    # Linked spider data (IDs for efficiency)
    spider_data_ids = models.JSONField(
        default=list,
        help_text="List of SpiderData UUIDs that contributed to this cluster"
    )

    # Linked trigger events (if pattern came from triggers)
    trigger_event_ids = models.JSONField(
        default=list,
        blank=True,
        help_text="List of TriggerEvent UUIDs that contributed"
    )

    # Source breakdown by spider/source type
    source_breakdown = models.JSONField(
        default=dict,
        help_text="Count of signals per source: {'bluesky': 12, 'reddit': 6}"
    )

    # Pattern metrics
    strength = models.FloatField(
        default=0.0,
        help_text="Overall signal strength (0-1)"
    )
    novelty = models.FloatField(
        default=0.0,
        help_text="How new/unusual is this pattern (0-1)"
    )
    confidence = models.FloatField(
        default=0.0,
        help_text="Confidence in pattern validity (0-1)"
    )
    urgency = models.FloatField(
        default=0.0,
        help_text="Time-sensitivity of this pattern (0-1)"
    )

    # Scoring contract fields (Session 1025)
    reach_score = models.FloatField(
        default=0.0,
        help_text="0-1: viral/audience potential"
    )
    intent_score = models.FloatField(
        default=0.0,
        help_text="0-1: commercial/actionable potential"
    )
    replicability_score = models.FloatField(
        default=0.0,
        help_text="0-1: can we act on this repeatedly"
    )
    source_confidence = models.FloatField(
        default=0.0,
        help_text="0-1: trustworthiness of sources"
    )
    TRACK_CHOICES = [
        ('attention', 'Attention Radar'),
        ('intent', 'Intent Engine'),
        ('unclassified', 'Unclassified'),
    ]
    track = models.CharField(
        max_length=20,
        default='unclassified',
        choices=TRACK_CHOICES,
        help_text="Pipeline track: attention (content) or intent (micro-products)"
    )

    # Keywords extracted from signals
    keywords = models.JSONField(
        default=list,
        help_text="Keywords that define this cluster"
    )

    # Sample signal content for context
    sample_signals = models.JSONField(
        default=list,
        help_text="Sample signal snippets for display: [{'source': 'bluesky', 'text': '...'}]"
    )

    # Time window of signals
    signal_window_start = models.DateTimeField(
        null=True, blank=True,
        help_text="Earliest signal timestamp in cluster"
    )
    signal_window_end = models.DateTimeField(
        null=True, blank=True,
        help_text="Latest signal timestamp in cluster"
    )

    # Lifecycle
    STATUS_CHOICES = [
        ('detecting', 'Detecting'),      # Still accumulating signals
        ('active', 'Active'),            # Pattern confirmed, actionable
        ('triggered', 'Triggered'),      # Has triggered a conversation
        ('decayed', 'Decayed'),           # Pattern no longer relevant
        ('archived', 'Archived'),        # Kept for history
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='detecting'
    )

    # When pattern was detected/confirmed
    detected_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    # Pattern decay
    decay_rate = models.FloatField(
        default=0.1,
        help_text="How fast this pattern loses relevance (per day)"
    )
    expires_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When this pattern should be considered stale"
    )

    class Meta:
        app_label = 'core'
        verbose_name = "Signal Cluster"
        verbose_name_plural = "Signal Clusters"
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['status', '-detected_at']),
            models.Index(fields=['pattern_type', '-strength']),
        ]

    def __str__(self):
        return f"SignalCluster: {self.name} ({self.strength:.2f})"

    @property
    def total_signals(self):
        """Total number of signals in this cluster."""
        return sum(self.source_breakdown.values()) if self.source_breakdown else 0

    @property
    def is_actionable(self):
        """Whether this cluster should trigger action."""
        return (
            self.status == 'active' and
            self.strength >= 0.5 and
            self.confidence >= 0.5
        )

    def add_signal(self, spider_data):
        """Add a spider data signal to this cluster."""
        if str(spider_data.id) not in self.spider_data_ids:
            self.spider_data_ids.append(str(spider_data.id))

            # Update source breakdown
            source = spider_data.spider_name
            if source not in self.source_breakdown:
                self.source_breakdown[source] = 0
            self.source_breakdown[source] += 1

            # Update time window
            if not self.signal_window_start or spider_data.created_at < self.signal_window_start:
                self.signal_window_start = spider_data.created_at
            if not self.signal_window_end or spider_data.created_at > self.signal_window_end:
                self.signal_window_end = spider_data.created_at

            self.save()

    def calculate_metrics(self):
        """Recalculate pattern metrics based on current signals."""
        total = self.total_signals
        if total == 0:
            return

        # Strength based on signal count and diversity
        source_count = len(self.source_breakdown)
        self.strength = min(1.0, (total / 20) * (source_count / 5))

        # Novelty decays over time
        if self.detected_at:
            age_hours = (timezone.now() - self.detected_at).total_seconds() / 3600
            self.novelty = max(0, 1.0 - (age_hours / 72))  # Decays over 3 days

        # Confidence based on source diversity
        self.confidence = min(1.0, source_count / 3)

        self.save()


# ─── Session 1131 Phase 2 — Curated signal snapshots ──────────────────


class CuratedSignalSnapshot(models.Model):
    """
    Session 1131 Phase 2 (Rigby's path C): one row per SignalCuratorAgent run.

    Rigby's lock #2 (curated-persistence shape, conversation
    pa-d19c1674b936): typed snapshot table, not a column-on-cluster.
    Reasons (her words): "preserves history (what did we curate
    yesterday vs today?), makes debugging and demoing much stronger,
    avoids 'last run wins' ambiguity."

    Each snapshot carries the provenance needed to explain "WHY this
    set, WHY in this order" without re-running the scoring:
    - `scoring_formula_version` — versioned identifier of the formula
    - `dedup_strategy` — human-readable description of the grouping rule
    - `pattern_type_cap` — per-pattern_type diversity cap config
    - `excluded_duplicates` — JSON audit of clusters dropped by dedup

    Top entries live in the child `CuratedSignalEntry` table, one row
    per ranked cluster.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    scoring_formula_version = models.CharField(
        max_length=80,
        help_text=(
            "Versioned identifier of the scoring formula used to produce "
            "this snapshot (e.g. 'v1_strength_0.9_recency_0.1_tau72'). "
            "Changing the formula bumps the version; the snapshot record "
            "keeps the link to the formula it was scored with."
        ),
    )

    dedup_strategy = models.CharField(
        max_length=120,
        help_text=(
            "Human-readable dedup strategy identifier (e.g. "
            "'group_best_by(pattern_type, topic_key)'). Lets the audit "
            "trail name HOW duplicates were collapsed."
        ),
    )

    pattern_type_cap = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Per-pattern_type diversity cap config (e.g. "
            "{'cap': 3, 'rule': 'max(2, ceil(N/4))'}). Empty dict means "
            "no per-type cap was applied."
        ),
    )

    pool_size = models.IntegerField(
        help_text=(
            "Total cluster candidates scored before dedup (everything "
            "matching the Phase 1 quality bar at snapshot time)."
        ),
    )

    top_n = models.IntegerField(
        help_text="Number of entries actually persisted on this snapshot.",
    )

    excluded_duplicates = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "Audit list of clusters dropped by dedup grouping. Shape per "
            "entry: {cluster_id, group_key, score, lost_to_cluster_id}. "
            "JSON for v1; promote to a child table if we ever need to "
            "query historical exclusions across snapshots."
        ),
    )

    class Meta:
        app_label = 'core'
        verbose_name = "Curated Signal Snapshot"
        verbose_name_plural = "Curated Signal Snapshots"
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"CuratedSignalSnapshot {self.id} "
            f"({self.top_n} entries, "
            f"formula={self.scoring_formula_version})"
        )


class CuratedSignalEntry(models.Model):
    """
    Session 1131 Phase 2: one curated cluster within a snapshot.

    Stores enough provenance to answer "why was this cluster picked?"
    without rerunning the score (cluster.strength/size could drift
    between snapshot time and read time).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    snapshot = models.ForeignKey(
        'CuratedSignalSnapshot',
        on_delete=models.CASCADE,
        related_name='entries',
    )
    cluster = models.ForeignKey(
        'SignalCluster',
        on_delete=models.CASCADE,
        related_name='curated_entries',
    )

    rank = models.IntegerField(
        help_text=(
            "1-based rank within the snapshot. rank=1 is the highest "
            "curated_score; ties broken by cluster.seq ASC (older row "
            "wins) so ranking is deterministic."
        ),
    )
    curated_score = models.FloatField(
        help_text="Composite score this cluster earned in the snapshot run.",
    )
    group_key = models.CharField(
        max_length=200,
        help_text=(
            "Dedup group key the cluster won (e.g. 'demand_spike::react'). "
            "Stored verbatim so we can trace which group it competed in."
        ),
    )

    # Snapshot of the cluster's metrics at curation time. These are
    # IMMUTABLE — they record what the curator saw, not the current
    # state of the cluster row.
    strength_at_pick = models.FloatField(
        help_text="Cluster.strength at snapshot time (immutable record).",
    )
    cluster_size_at_pick = models.IntegerField(
        help_text="sum(source_breakdown.values()) at snapshot time.",
    )
    age_hours_at_pick = models.FloatField(
        help_text="Hours since detected_at when the snapshot ran.",
    )

    class Meta:
        app_label = 'core'
        verbose_name = "Curated Signal Entry"
        verbose_name_plural = "Curated Signal Entries"
        ordering = ['snapshot', 'rank']
        constraints = [
            models.UniqueConstraint(
                fields=['snapshot', 'rank'],
                name='curated_signal_entry_unique_rank_per_snapshot',
            ),
        ]
        indexes = [
            models.Index(
                fields=['cluster', '-snapshot'],
                name='curated_entry_cluster_idx',
            ),
        ]

    def __str__(self):
        return (
            f"CuratedSignalEntry rank={self.rank} "
            f"score={self.curated_score:.3f} "
            f"cluster={self.cluster_id}"
        )


class AutoTopic(models.Model):
    """
    Session 900: Records WHY a specific topic was chosen for discussion.

    Links a SignalCluster to a generated conversation topic, providing
    the provenance for "why this topic, why now?"

    Example:
        AutoTopic(
            name="Formalize Persona Research",
            signal_cluster=<SignalCluster: persona demand spike>,
            derived_from_pattern="demand_spike",
            confidence=0.83,
            rationale="12 Bluesky posts + 6 Reddit threads indicate demand..."
        )
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Topic name (what will be discussed)
    name = models.CharField(
        max_length=300,
        help_text="The auto-generated topic name"
    )

    # Full topic description
    description = models.TextField(
        blank=True,
        help_text="Extended description of the topic"
    )

    # Provenance link to signals
    signal_cluster = models.ForeignKey(
        SignalCluster,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='auto_topics',
        help_text="The signal cluster that triggered this topic"
    )

    # Pattern that was matched
    derived_from_pattern = models.CharField(
        max_length=100,
        blank=True,
        help_text="Pattern type that generated this topic"
    )

    # Why this topic was chosen
    rationale = models.TextField(
        blank=True,
        help_text="Explanation of why this topic was auto-generated"
    )

    # Metrics
    confidence = models.FloatField(
        default=0.0,
        help_text="Confidence that this topic is worth discussing (0-1)"
    )
    urgency = models.FloatField(
        default=0.0,
        help_text="Time-sensitivity of this topic (0-1)"
    )
    relevance = models.FloatField(
        default=0.0,
        help_text="Relevance to user/system goals (0-1)"
    )

    # Suggested agents for this topic
    suggested_agent_names = models.JSONField(
        default=list,
        help_text="Agent names recommended for this topic"
    )

    # Suggested conversation type
    SUGGESTED_CONVERSATION_TYPES = [
        ('analytical', 'Analytical'),
        ('creative', 'Creative'),
        ('debate', 'Debate'),
        ('planning', 'Planning'),
        ('critique', 'Critique'),
    ]
    suggested_conversation_type = models.CharField(
        max_length=20,
        choices=SUGGESTED_CONVERSATION_TYPES,
        default='analytical',
        help_text="Recommended conversation type for this topic"
    )

    # Has this topic been used?
    STATUS_CHOICES = [
        ('pending', 'Pending'),          # Not yet triggered
        ('scheduled', 'Scheduled'),      # Queued for conversation
        ('triggered', 'Triggered'),      # Has triggered a conversation
        ('skipped', 'Skipped'),          # Was not used
        ('expired', 'Expired'),          # Timed out
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Link to triggered session (set after conversation starts)
    # Note: This is a string FK to avoid circular imports
    # The actual FK is on HiveMindSession.auto_topic
    triggered_session_id = models.UUIDField(
        null=True, blank=True,
        help_text="ID of the HiveMindSession this topic triggered"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    triggered_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When this topic should be considered stale"
    )

    class Meta:
        app_label = 'core'
        verbose_name = "Auto Topic"
        verbose_name_plural = "Auto Topics"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['-confidence', '-urgency']),
        ]

    def __str__(self):
        return f"AutoTopic: {self.name[:50]} ({self.confidence:.2f})"

    @property
    def is_actionable(self):
        """Whether this topic should trigger a conversation."""
        return (
            self.status == 'pending' and
            self.confidence >= 0.5 and
            (not self.expires_at or timezone.now() < self.expires_at)
        )

    def mark_triggered(self, session_id):
        """Mark this topic as having triggered a conversation."""
        self.status = 'triggered'
        self.triggered_at = timezone.now()
        self.triggered_session_id = session_id
        self.save()

        # Also update the signal cluster
        if self.signal_cluster:
            self.signal_cluster.status = 'triggered'
            self.signal_cluster.save()


class TopicSuggestion(models.Model):
    """
    Session 900: Alternative/related topic suggestions from signal analysis.

    When analyzing signals, multiple topic angles might be identified.
    This stores the alternatives that weren't chosen as the primary AutoTopic.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Parent auto topic
    auto_topic = models.ForeignKey(
        AutoTopic,
        on_delete=models.CASCADE,
        related_name='alternatives',
        help_text="The primary auto topic this is an alternative to"
    )

    # Alternative topic
    name = models.CharField(max_length=300)
    description = models.TextField(blank=True)

    # Why this wasn't chosen as primary
    reason_not_primary = models.CharField(
        max_length=200,
        blank=True,
        help_text="Why this wasn't the primary topic"
    )

    # Metrics
    confidence = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Topic Suggestion"
        verbose_name_plural = "Topic Suggestions"

    def __str__(self):
        return f"Alternative: {self.name[:50]}"
