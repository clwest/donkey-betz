"""
Session 471: Narrative Drift Detector Models

Tier 1 Autonomous Situation #2
"The system watches the world for story shifts."

This module tracks narratives over time and detects when stories change.
"""

import uuid
from django.db import models
from django.utils import timezone


class NarrativeDomain(models.TextChoices):
    """Categories of narratives to track."""
    POLITICS = 'politics', 'Politics & Government'
    MARKETS = 'markets', 'Financial Markets'
    TECH = 'tech', 'Technology & AI'
    CULTURE = 'culture', 'Culture & Society'
    GEOPOLITICS = 'geopolitics', 'Geopolitics & International'
    CRYPTO = 'crypto', 'Crypto & Web3'
    CLIMATE = 'climate', 'Climate & Environment'
    HEALTH = 'health', 'Health & Medicine'


class NarrativeStatus(models.TextChoices):
    """Status of a tracked narrative."""
    EMERGING = 'emerging', 'Emerging (new narrative forming)'
    DOMINANT = 'dominant', 'Dominant (widely accepted)'
    SHIFTING = 'shifting', 'Shifting (change detected)'
    FADING = 'fading', 'Fading (losing relevance)'
    DEAD = 'dead', 'Dead (no longer relevant)'


class Narrative(models.Model):
    """
    A tracked narrative/story in the world.

    Examples:
    - "AI will take all jobs" (tech)
    - "Inflation is transitory" (markets)
    - "China is the next superpower" (geopolitics)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Core narrative info
    title = models.CharField(
        max_length=200,
        help_text="Short title for the narrative"
    )
    description = models.TextField(
        help_text="Detailed description of what this narrative claims"
    )
    domain = models.CharField(
        max_length=20,
        choices=NarrativeDomain.choices,
        default=NarrativeDomain.TECH
    )

    # Key phrases that indicate this narrative
    keywords = models.JSONField(
        default=list,
        help_text="Keywords/phrases that indicate this narrative"
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=NarrativeStatus.choices,
        default=NarrativeStatus.EMERGING
    )
    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.5,
        help_text="Confidence in narrative status (0-1)"
    )

    # Metrics
    mention_count = models.IntegerField(default=0)
    last_mention = models.DateTimeField(null=True, blank=True)
    peak_mentions = models.IntegerField(default=0)
    peak_date = models.DateTimeField(null=True, blank=True)

    # Historical strength tracking (for detecting drift)
    strength_history = models.JSONField(
        default=list,
        help_text="List of {date, strength, sources} over time"
    )

    # Auto-detected from spider data
    auto_detected = models.BooleanField(default=False)

    # Timestamps
    first_detected = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        db_table = 'narrative'
        ordering = ['-mention_count', '-updated_at']
        indexes = [
            models.Index(fields=['domain', 'status']),
            models.Index(fields=['status', '-mention_count']),
        ]

    def __str__(self):
        return f"{self.title} [{self.status}]"


class NarrativeShift(models.Model):
    """
    A detected shift/change in narrative.

    This is the core output of the Narrative Drift Detector.
    "The story just changed"
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # What shifted
    old_narrative = models.ForeignKey(
        Narrative,
        on_delete=models.CASCADE,
        related_name='shifts_from',
        help_text="The narrative that was dominant before"
    )
    new_narrative = models.ForeignKey(
        Narrative,
        on_delete=models.CASCADE,
        related_name='shifts_to',
        null=True,
        blank=True,
        help_text="The new narrative replacing it (if identified)"
    )

    domain = models.CharField(
        max_length=20,
        choices=NarrativeDomain.choices
    )

    # The shift details
    shift_summary = models.TextField(
        help_text="What changed in plain language"
    )
    old_narrative_summary = models.TextField(
        help_text="What people believed before"
    )
    new_narrative_summary = models.TextField(
        help_text="What people believe now"
    )

    # Evidence
    trigger_events = models.JSONField(
        default=list,
        help_text="Events that triggered this shift"
    )
    evidence_sources = models.JSONField(
        default=list,
        help_text="Sources supporting this shift detection"
    )

    # Second-order effects (the alpha!)
    second_order_effects = models.JSONField(
        default=list,
        help_text="Predicted downstream effects of this shift"
    )

    # Agent analysis
    historian_analysis = models.TextField(
        blank=True,
        help_text="NarrativeHistorianAgent's analysis"
    )
    trend_break_analysis = models.TextField(
        blank=True,
        help_text="TrendBreakDetectorAgent's analysis"
    )
    contrarian_analysis = models.TextField(
        blank=True,
        help_text="ContrarianAgent's counter-view"
    )
    cultural_impact_analysis = models.TextField(
        blank=True,
        help_text="CulturalImpactAgent's analysis"
    )

    # Confidence and importance
    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.5,
        help_text="Confidence this is a real shift (0-1)"
    )
    importance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.5,
        help_text="How significant is this shift (0-1)"
    )

    # Verification
    verified = models.BooleanField(
        default=False,
        help_text="Has this shift been verified by human review"
    )

    # Timestamps
    detected_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        db_table = 'narrative_shift'
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['domain', '-detected_at']),
            models.Index(fields=['-importance', '-detected_at']),
        ]

    def __str__(self):
        return f"Shift: {self.old_narrative.title} -> {self.new_narrative.title if self.new_narrative else 'Unknown'}"


class NarrativeEvidence(models.Model):
    """
    Individual pieces of evidence supporting a narrative.
    Links SpiderData to Narratives.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    narrative = models.ForeignKey(
        Narrative,
        on_delete=models.CASCADE,
        related_name='evidence'
    )

    # Source info
    spider_data = models.ForeignKey(
        'core.SpiderData',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='narrative_evidence'
    )

    source_url = models.URLField(max_length=500, blank=True)
    source_title = models.CharField(max_length=300, blank=True)
    source_type = models.CharField(max_length=50, blank=True)  # news, social, political, etc.

    # Content
    excerpt = models.TextField(
        help_text="Relevant excerpt from the source"
    )
    sentiment = models.CharField(
        max_length=20,
        choices=[
            ('supports', 'Supports narrative'),
            ('contradicts', 'Contradicts narrative'),
            ('neutral', 'Neutral mention'),
        ],
        default='supports'
    )

    # Strength
    strength = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.5,
        help_text="How strongly this supports/contradicts (0-1)"
    )

    # Timestamps
    source_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        db_table = 'narrative_evidence'
        ordering = ['-source_date', '-created_at']


class NarrativeAlert(models.Model):
    """
    Alerts generated by the Narrative Drift Detector.
    Sent to Discord and stored for review.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # What triggered the alert
    shift = models.ForeignKey(
        NarrativeShift,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alerts'
    )
    narrative = models.ForeignKey(
        Narrative,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alerts'
    )

    # Alert content
    alert_type = models.CharField(
        max_length=30,
        choices=[
            ('shift_detected', 'Narrative Shift Detected'),
            ('new_narrative', 'New Narrative Emerging'),
            ('narrative_dying', 'Narrative Fading'),
            ('contradictions', 'Contradictions Detected'),
            ('high_importance', 'High Importance Alert'),
        ]
    )
    title = models.CharField(max_length=200)
    summary = models.TextField()

    # Delivery
    sent_to_discord = models.BooleanField(default=False)
    discord_message_id = models.CharField(max_length=100, blank=True)

    # User interaction
    read = models.BooleanField(default=False)
    dismissed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        db_table = 'narrative_alert'
        ordering = ['-created_at']
