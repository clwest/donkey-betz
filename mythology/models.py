"""
Mythology tracking and prevention models for unified-donkey-betz.
Based on the donkey_betz mythology lab system.
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class MythologyEvent(models.Model):
    """
    Tracks mythology creation and mutation events in the system.
    """
    EVENT_TYPES = [
        ('creation', 'Creation'),
        ('mutation', 'Mutation'),
        ('propagation', 'Propagation'),
        ('detection', 'Detection'),
        ('prevention', 'Prevention'),
    ]
    
    MUTATION_TYPES = [
        ('context_loss', 'Context Loss'),
        ('inflation', 'Numeric Inflation'),
        ('semantic_drift', 'Semantic Drift'),
        ('confidence_decay', 'Confidence Decay'),
        ('expansion', 'Content Expansion'),
        ('condensation', 'Content Condensation'),
        ('false_claim', 'False Claim'),
        ('capability_exaggeration', 'Capability Exaggeration'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    original_content = models.TextField()
    mutated_content = models.TextField(blank=True)
    mutation_type = models.CharField(max_length=50, choices=MUTATION_TYPES, blank=True)
    
    # Source tracking
    source_type = models.CharField(max_length=50, blank=True)  # 'conversation', 'embedding', 'agent'
    source_id = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Scoring
    confidence_score = models.FloatField(default=0.0)
    risk_level = models.FloatField(default=0.0)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    patterns_detected = models.JSONField(default=list, blank=True)
    
    # Prevention tracking
    was_prevented = models.BooleanField(default=False)
    prevention_method = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        app_label = 'mythology'
        db_table = 'mythology_events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['source_type', 'source_id']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.mutation_type or 'N/A'} - {self.created_at}"


class MythPattern(models.Model):
    """
    Tracks recurring patterns in mythology creation to help prevent future occurrences.
    """
    PATTERN_TYPES = [
        ('numeric_inflation', 'Numeric Inflation'),
        ('false_authority', 'False Authority'),
        ('capability_exaggeration', 'Capability Exaggeration'),
        ('temporal_confusion', 'Temporal Confusion'),
        ('context_loss', 'Context Loss'),
        ('semantic_drift', 'Semantic Drift'),
        ('confidence_decay', 'Confidence Decay'),
        ('false_action_claims', 'False Action Claims'),
        ('unverified_stats', 'Unverified Statistics'),
        ('false_technology', 'False Technology Claims'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pattern_type = models.CharField(max_length=50, choices=PATTERN_TYPES, unique=True)
    description = models.TextField()
    
    # Pattern detection
    regex_pattern = models.TextField(blank=True)
    detection_keywords = models.JSONField(default=list)
    
    # Statistics
    frequency_count = models.IntegerField(default=0)
    last_seen = models.DateTimeField(null=True, blank=True)
    times_prevented = models.IntegerField(default=0)
    prevention_success_rate = models.FloatField(default=0.0)
    
    # Prevention strategies
    prevention_strategies = models.JSONField(default=list)
    severity_weight = models.FloatField(default=0.1)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'mythology'
        db_table = 'myth_patterns'
        ordering = ['-frequency_count', 'pattern_type']
    
    def __str__(self):
        return f"{self.get_pattern_type_display()} (seen {self.frequency_count} times)"


class MythologyGuard(models.Model):
    """
    Guards to prevent mythology in prompts and responses.
    """
    GUARD_TYPES = [
        ('pattern', 'Pattern Detection'),
        ('instruction', 'Instruction Injection'),
        ('validation', 'Response Validation'),
        ('filter', 'Content Filter'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    guard_type = models.CharField(max_length=50, choices=GUARD_TYPES)
    
    # Guard configuration
    pattern = models.TextField(blank=True)  # For pattern guards
    instruction = models.TextField(blank=True)  # For instruction guards
    validation_rules = models.JSONField(default=dict, blank=True)  # For validation guards
    
    # Effectiveness tracking
    times_triggered = models.IntegerField(default=0)
    times_successful = models.IntegerField(default=0)
    effectiveness_rate = models.FloatField(default=0.0)
    
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)  # Higher priority guards run first
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'mythology'
        db_table = 'mythology_guards'
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_guard_type_display()})"


class MythologyCleanup(models.Model):
    """
    Track mythology cleanup operations.
    """
    CLEANUP_TYPES = [
        ('embedding', 'Embedding Cleanup'),
        ('conversation', 'Conversation Cleanup'),
        ('agent', 'Agent Memory Cleanup'),
        ('full', 'Full System Cleanup'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cleanup_type = models.CharField(max_length=50, choices=CLEANUP_TYPES)
    
    # Cleanup statistics
    items_scanned = models.IntegerField(default=0)
    items_cleaned = models.IntegerField(default=0)
    patterns_found = models.JSONField(default=dict)
    
    # Specific cleanups
    dart_flutter_removed = models.IntegerField(default=0)
    fitness_dashboard_removed = models.IntegerField(default=0)
    deployments_350_removed = models.IntegerField(default=0)
    capability_exaggerations_removed = models.IntegerField(default=0)
    
    # Execution details
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    
    # User tracking
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        app_label = 'mythology'
        db_table = 'mythology_cleanups'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.get_cleanup_type_display()} - {self.started_at}"


class MythologyAlert(models.Model):
    """
    Alerts generated by the mythology monitoring system.
    """
    ALERT_TYPES = [
        ('new_myth', 'New Myth Detected'),
        ('rapid_inflation', 'Rapid Numeric Inflation'),
        ('high_context_loss', 'High Context Loss'),
        ('wide_propagation', 'Wide Myth Propagation'),
        ('pattern_detected', 'Pattern Detected'),
        ('cleanup_needed', 'Cleanup Needed'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='medium')
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    mythology_event = models.ForeignKey(
        MythologyEvent, 
        on_delete=models.CASCADE,
        related_name='alerts', 
        null=True, 
        blank=True
    )
    
    data = models.JSONField(default=dict)
    
    # Alert handling
    acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    # Auto-cleanup
    auto_cleanup_triggered = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'mythology_alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['alert_type', 'severity']),
            models.Index(fields=['acknowledged', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.severity.upper()} - {self.title}"


class FlaggedHallucination(models.Model):
    """
    Stores flagged hallucinations for review and learning.
    """
    FLAGGED_TYPES = [
        ('blocked_content', 'Blocked Content'),
        ('suspicious_response', 'Suspicious Response'),
        ('user_reported', 'User Reported'),
        ('auto_detected', 'Auto Detected'),
        ('verification_failed', 'Verification Failed'),
    ]
    
    VERIFICATION_STATUS = [
        ('pending', 'Pending Review'),
        ('verified_safe', 'Verified Safe'),
        ('verified_hallucination', 'Verified Hallucination'),
        ('needs_human_review', 'Needs Human Review'),
        ('false_positive', 'False Positive'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    flagged_type = models.CharField(max_length=50, choices=FLAGGED_TYPES)
    
    # Content that was flagged
    original_prompt = models.TextField()
    flagged_content = models.TextField()
    context = models.TextField(blank=True)
    
    # Detection details
    patterns_detected = models.JSONField(default=list)
    risk_score = models.FloatField(default=0.0)
    confidence_score = models.FloatField(default=0.0)
    detection_method = models.CharField(max_length=100, blank=True)
    
    # Verification
    verification_status = models.CharField(max_length=50, choices=VERIFICATION_STATUS, default='pending')
    verification_notes = models.TextField(blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_hallucinations')
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Auto-verification by second agent
    auto_verification_attempted = models.BooleanField(default=False)
    auto_verification_result = models.JSONField(default=dict, blank=True)
    auto_verification_agent = models.CharField(max_length=100, blank=True)
    
    # Priority and handling
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium')
    requires_immediate_attention = models.BooleanField(default=False)
    
    # User and session tracking
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=255, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Learning integration
    added_to_training = models.BooleanField(default=False)
    pattern_updated = models.BooleanField(default=False)
    guard_updated = models.BooleanField(default=False)
    
    # Timestamps
    flagged_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Related mythology event
    mythology_event = models.ForeignKey(
        MythologyEvent, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='flagged_hallucinations'
    )
    
    class Meta:
        db_table = 'flagged_hallucinations'
        ordering = ['-flagged_at']
        indexes = [
            models.Index(fields=['flagged_type', 'verification_status']),
            models.Index(fields=['priority', 'flagged_at']),
            models.Index(fields=['user', 'flagged_at']),
            models.Index(fields=['verification_status', 'flagged_at']),
            models.Index(fields=['requires_immediate_attention', 'flagged_at']),
        ]
    
    def __str__(self):
        return f"{self.get_flagged_type_display()} - {self.get_verification_status_display()} - {self.flagged_at}"
    
    def get_severity_color(self):
        """Return color for frontend display"""
        colors = {
            'low': 'green',
            'medium': 'yellow', 
            'high': 'orange',
            'critical': 'red'
        }
        return colors.get(self.priority, 'gray')


class HallucinationReview(models.Model):
    """
    Track reviews and actions taken on flagged hallucinations.
    """
    REVIEW_ACTIONS = [
        ('approved', 'Approved as Safe'),
        ('rejected', 'Confirmed Hallucination'),
        ('needs_investigation', 'Needs Investigation'),
        ('pattern_updated', 'Pattern Updated'),
        ('guard_created', 'Guard Created'),
        ('training_added', 'Added to Training'),
        ('false_positive', 'Marked False Positive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    flagged_hallucination = models.ForeignKey(
        FlaggedHallucination, 
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    review_action = models.CharField(max_length=50, choices=REVIEW_ACTIONS)
    
    # Review details
    review_notes = models.TextField()
    confidence_rating = models.IntegerField(default=5)  # 1-10 scale
    
    # Actions taken
    pattern_changes = models.JSONField(default=dict, blank=True)
    guard_changes = models.JSONField(default=dict, blank=True)
    training_data_added = models.BooleanField(default=False)
    
    # Metadata
    review_time_seconds = models.FloatField(default=0.0)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'hallucination_reviews'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['review_action', 'created_at']),
            models.Index(fields=['reviewer', 'created_at']),
        ]
    
    def __str__(self):
        return f"Review: {self.get_review_action_display()} - {self.created_at}"