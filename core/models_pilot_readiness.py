"""
Session 590: Pilot Readiness Gate Models

This module implements the missing layer between Boardroom decisions and execution:

    Dream → Boardroom Decision → [PILOT READINESS GATE] → Action/Pilot

The system identified (Cycles #12-14) that the bottleneck is not ideation or sensing,
but operationalization of safety-sensitive decisions. This gate ensures:

1. Required artifacts exist before execution
2. Time-in-phase is tracked for throughput analysis
3. Safety-sensitive work proceeds with appropriate governance
4. The "phantom backlog" feeling is eliminated with explicit status

Based on ChatGPT strategic analysis of ThinkingAgent insights.
"""

import uuid
from django.db import models
from django.utils import timezone


class PilotReadinessGate(models.Model):
    """
    Session 590: Gate between Boardroom decision and pilot execution.

    This model captures whether a decision is ready for execution by tracking:
    - Required artifacts (threat models, consent flows, etc.)
    - Approval status from stakeholders
    - Time spent in each phase (for throughput analysis)

    A decision cannot proceed to pilot until the gate status is 'approved'.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to the Boardroom decision
    decision = models.OneToOneField(
        'AgentDecisionSummary',
        on_delete=models.CASCADE,
        related_name='readiness_gate',
        help_text="The Boardroom decision this gate controls"
    )

    # Gate status
    GATE_STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('ready', 'Ready for Review'),
        ('approved', 'Approved for Pilot'),
        ('blocked', 'Blocked'),
        ('waived', 'Waived (Low Risk)'),
    ]
    status = models.CharField(
        max_length=20,
        choices=GATE_STATUS_CHOICES,
        default='not_started'
    )

    # Risk classification determines required artifacts
    RISK_LEVEL_CHOICES = [
        ('low', 'Low - Auto-waivable'),
        ('medium', 'Medium - Requires basic checklist'),
        ('high', 'High - Full safety review'),
        ('critical', 'Critical - Executive approval required'),
    ]
    risk_level = models.CharField(
        max_length=20,
        choices=RISK_LEVEL_CHOICES,
        default='medium'
    )

    # Risk factors that contributed to classification
    risk_factors = models.JSONField(
        default=list,
        help_text="List of factors that determined risk level"
    )

    # Summary and notes
    summary = models.TextField(
        blank=True,
        help_text="Human-readable summary of what this pilot will test"
    )
    success_criteria = models.TextField(
        blank=True,
        help_text="What would make this pilot successful?"
    )
    failure_criteria = models.TextField(
        blank=True,
        help_text="What would cause us to stop the pilot?"
    )

    # Approval tracking
    approved_by = models.CharField(max_length=100, blank=True)
    approval_notes = models.TextField(blank=True)

    # Phase timestamps for latency tracking
    # Decision → Readiness
    decision_made_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When the Boardroom decision was made"
    )
    gate_started_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When readiness work began"
    )
    gate_ready_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When all checklist items were completed"
    )
    gate_approved_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When the gate was approved for pilot"
    )

    # Readiness → Pilot
    pilot_started_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When the pilot actually began"
    )
    pilot_completed_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When the pilot concluded"
    )

    # Standard timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Pilot Readiness Gate"
        verbose_name_plural = "Pilot Readiness Gates"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['risk_level']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Gate: {self.decision.topic[:50]} [{self.status}]"

    # =========================================================================
    # Status Transitions
    # =========================================================================

    def start_readiness(self):
        """Begin working on readiness artifacts."""
        if self.status == 'not_started':
            self.status = 'in_progress'
            self.gate_started_at = timezone.now()
            self.save()
            return True
        return False

    def mark_ready(self):
        """Mark gate as ready for approval review."""
        if self.status == 'in_progress' and self.checklist_complete:
            self.status = 'ready'
            self.gate_ready_at = timezone.now()
            self.save()
            return True
        return False

    def approve(self, approved_by: str, notes: str = ''):
        """Approve the gate for pilot execution."""
        if self.status in ('ready', 'in_progress'):
            self.status = 'approved'
            self.approved_by = approved_by
            self.approval_notes = notes
            self.gate_approved_at = timezone.now()
            self.save()
            return True
        return False

    def block(self, reason: str):
        """Block the gate with a reason."""
        self.status = 'blocked'
        self.approval_notes = f"BLOCKED: {reason}"
        self.save()
        return True

    def waive(self, reason: str = 'Low risk - auto-waived'):
        """Waive the gate for low-risk decisions."""
        if self.risk_level == 'low':
            self.status = 'waived'
            self.approval_notes = reason
            self.gate_approved_at = timezone.now()
            self.save()
            return True
        return False

    def start_pilot(self):
        """Mark that the pilot has started."""
        if self.status in ('approved', 'waived'):
            self.pilot_started_at = timezone.now()
            self.save()
            return True
        return False

    def complete_pilot(self):
        """Mark that the pilot has completed."""
        if self.pilot_started_at:
            self.pilot_completed_at = timezone.now()
            self.save()
            return True
        return False

    # =========================================================================
    # Checklist Status
    # =========================================================================

    @property
    def checklist_complete(self) -> bool:
        """Check if all required checklist items are done."""
        required_items = self.checklist_items.filter(is_required=True)
        if not required_items.exists():
            return True  # No required items = complete
        return all(
            item.status in ('completed', 'waived')
            for item in required_items
        )

    @property
    def checklist_progress(self) -> dict:
        """Get checklist completion progress."""
        items = self.checklist_items.all()
        total = items.count()
        if total == 0:
            return {'total': 0, 'completed': 0, 'percentage': 100}

        completed = items.filter(status__in=('completed', 'waived')).count()
        return {
            'total': total,
            'completed': completed,
            'percentage': round((completed / total) * 100, 1)
        }

    # =========================================================================
    # Latency Metrics
    # =========================================================================

    @property
    def decision_to_readiness_hours(self) -> float:
        """Hours from decision to starting readiness work."""
        if self.decision_made_at and self.gate_started_at:
            delta = self.gate_started_at - self.decision_made_at
            return round(delta.total_seconds() / 3600, 1)
        return None

    @property
    def readiness_duration_hours(self) -> float:
        """Hours spent in readiness phase."""
        if self.gate_started_at:
            end = self.gate_ready_at or timezone.now()
            delta = end - self.gate_started_at
            return round(delta.total_seconds() / 3600, 1)
        return None

    @property
    def approval_wait_hours(self) -> float:
        """Hours waiting for approval after ready."""
        if self.gate_ready_at:
            end = self.gate_approved_at or timezone.now()
            delta = end - self.gate_ready_at
            return round(delta.total_seconds() / 3600, 1)
        return None

    @property
    def total_gate_hours(self) -> float:
        """Total hours from decision to approved/pilot."""
        if self.decision_made_at:
            end = self.gate_approved_at or self.pilot_started_at or timezone.now()
            delta = end - self.decision_made_at
            return round(delta.total_seconds() / 3600, 1)
        return None

    @property
    def pilot_duration_hours(self) -> float:
        """Hours spent in pilot execution."""
        if self.pilot_started_at:
            end = self.pilot_completed_at or timezone.now()
            delta = end - self.pilot_started_at
            return round(delta.total_seconds() / 3600, 1)
        return None

    def get_latency_metrics(self) -> dict:
        """Get all latency metrics for this gate."""
        return {
            'decision_to_readiness_hours': self.decision_to_readiness_hours,
            'readiness_duration_hours': self.readiness_duration_hours,
            'approval_wait_hours': self.approval_wait_hours,
            'total_gate_hours': self.total_gate_hours,
            'pilot_duration_hours': self.pilot_duration_hours,
            'status': self.status,
            'risk_level': self.risk_level,
        }

    # =========================================================================
    # Factory Methods
    # =========================================================================

    @classmethod
    def create_for_decision(cls, decision, risk_level='medium', auto_generate_content=True):
        """
        Create a readiness gate for a Boardroom decision.

        Automatically sets decision_made_at from decision.created_at.

        Args:
            decision: The AgentDecisionSummary to create a gate for
            risk_level: Risk level ('low', 'medium', 'high', 'critical')
            auto_generate_content: If True, queue AI content generation (Session 594)
        """
        gate = cls.objects.create(
            decision=decision,
            risk_level=risk_level,
            decision_made_at=decision.created_at,
            summary=f"Pilot readiness for: {decision.topic}",
        )

        # Auto-create standard checklist items based on risk level
        gate.create_standard_checklist()

        # Session 594: Queue AI content generation for checklist items
        if auto_generate_content:
            try:
                from core.tasks import generate_checklist_content_async
                generate_checklist_content_async.delay(str(gate.id))
                import logging
                logging.getLogger(__name__).info(
                    f"Session 594: Queued content generation for gate {gate.id}"
                )
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(
                    f"Session 594: Failed to queue content generation: {e}"
                )

        return gate

    def create_standard_checklist(self):
        """Create standard checklist items based on risk level."""

        # Define items per risk level
        standard_items = {
            'low': [
                ('basic_review', 'Basic Review', 'Quick review of approach', False),
            ],
            'medium': [
                ('threat_model', 'Threat Model', 'Document potential threats and mitigations', True),
                ('rollback_procedure', 'Rollback Procedure', 'How to undo if things go wrong', True),
                ('success_metrics', 'Success Metrics', 'How we measure success', False),
            ],
            'high': [
                ('threat_model', 'Threat Model', 'Comprehensive threat analysis', True),
                ('consent_lifecycle', 'Consent Lifecycle', 'User consent flow documented', True),
                ('encryption_choice', 'Encryption/KMS Choice', 'Data protection approach selected', True),
                ('adversarial_test', 'Adversarial Test Plan', 'How to test for abuse/failure', True),
                ('kill_switch', 'Kill Switch Criteria', 'When and how to stop the pilot', True),
                ('rollback_procedure', 'Rollback Procedure', 'How to undo if things go wrong', True),
            ],
            'critical': [
                ('threat_model', 'Threat Model', 'Comprehensive threat analysis with external review', True),
                ('consent_lifecycle', 'Consent Lifecycle', 'Full user consent flow with legal review', True),
                ('encryption_choice', 'Encryption/KMS Choice', 'Data protection with security team approval', True),
                ('adversarial_test', 'Adversarial Test Plan', 'Red team testing planned', True),
                ('kill_switch', 'Kill Switch Criteria', 'Automated kill switch implemented', True),
                ('rollback_procedure', 'Rollback Procedure', 'Tested rollback with data recovery', True),
                ('executive_approval', 'Executive Approval', 'Sign-off from leadership', True),
                ('legal_review', 'Legal Review', 'Legal team has reviewed', True),
            ],
        }

        items = standard_items.get(self.risk_level, standard_items['medium'])

        for item_type, title, description, is_required in items:
            ReadinessChecklistItem.objects.create(
                gate=self,
                item_type=item_type,
                title=title,
                description=description,
                is_required=is_required,
            )


class ReadinessChecklistItem(models.Model):
    """
    Session 590: Individual checklist item for pilot readiness.

    Each item represents an artifact or approval needed before
    a decision can proceed to pilot execution.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to gate
    gate = models.ForeignKey(
        PilotReadinessGate,
        on_delete=models.CASCADE,
        related_name='checklist_items'
    )

    # Item type (for filtering and templates)
    ITEM_TYPE_CHOICES = [
        ('threat_model', 'Threat Model'),
        ('consent_lifecycle', 'Consent Lifecycle'),
        ('encryption_choice', 'Encryption/KMS Choice'),
        ('adversarial_test', 'Adversarial Test Plan'),
        ('kill_switch', 'Kill Switch Criteria'),
        ('rollback_procedure', 'Rollback Procedure'),
        ('success_metrics', 'Success Metrics'),
        ('basic_review', 'Basic Review'),
        ('executive_approval', 'Executive Approval'),
        ('legal_review', 'Legal Review'),
        ('security_review', 'Security Review'),
        ('custom', 'Custom Item'),
    ]
    item_type = models.CharField(max_length=30, choices=ITEM_TYPE_CHOICES)

    # Human-readable details
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('waived', 'Waived'),
        ('blocked', 'Blocked'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Is this item required or optional?
    is_required = models.BooleanField(default=True)

    # Documentation and evidence
    documentation_url = models.URLField(blank=True, help_text="Link to artifact document")
    documentation_notes = models.TextField(blank=True, help_text="Notes about the artifact")

    # Assignment and ownership
    assigned_to = models.CharField(max_length=100, blank=True, help_text="Person/agent responsible")

    # Completion tracking
    completed_by = models.CharField(max_length=100, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    completion_notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Readiness Checklist Item"
        verbose_name_plural = "Readiness Checklist Items"
        ordering = ['gate', 'item_type']

    def __str__(self):
        status_icon = {
            'pending': '⬜',
            'in_progress': '🔄',
            'completed': '✅',
            'waived': '⏭️',
            'blocked': '🚫',
        }.get(self.status, '?')
        return f"{status_icon} {self.title}"

    def complete(self, completed_by: str, notes: str = '', documentation_url: str = ''):
        """Mark this item as completed."""
        self.status = 'completed'
        self.completed_by = completed_by
        self.completed_at = timezone.now()
        self.completion_notes = notes
        if documentation_url:
            self.documentation_url = documentation_url
        self.save()

        # Check if this completes the gate
        if self.gate.checklist_complete and self.gate.status == 'in_progress':
            self.gate.mark_ready()

    def waive(self, waived_by: str, reason: str):
        """Waive this item (not required)."""
        self.status = 'waived'
        self.completed_by = waived_by
        self.completed_at = timezone.now()
        self.completion_notes = f"WAIVED: {reason}"
        self.save()

    def block(self, reason: str):
        """Block this item."""
        self.status = 'blocked'
        self.completion_notes = f"BLOCKED: {reason}"
        self.save()

        # Also block the gate
        self.gate.block(f"Checklist item blocked: {self.title}")


class PilotExecution(models.Model):
    """
    Session 590: Track pilot execution and outcomes.

    Once a gate is approved, pilots are executed and tracked here.
    This enables the learning loop and provides data for blogs.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to approved gate
    gate = models.ForeignKey(
        PilotReadinessGate,
        on_delete=models.CASCADE,
        related_name='pilot_executions'
    )

    # Pilot metadata
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Execution status
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('stopped', 'Stopped Early'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')

    # Scope and constraints
    scope = models.TextField(blank=True, help_text="What is being tested")
    constraints = models.JSONField(default=list, help_text="Limits on the pilot")

    # Outcomes
    OUTCOME_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success - Proceed'),
        ('partial', 'Partial - Iterate'),
        ('failure', 'Failure - Do Not Proceed'),
        ('inconclusive', 'Inconclusive - Need More Data'),
    ]
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES, default='pending')
    outcome_summary = models.TextField(blank=True)

    # Metrics collected
    metrics = models.JSONField(default=dict, help_text="Quantitative results")

    # Learnings (for blogs!)
    learnings = models.JSONField(default=list, help_text="What we learned")

    # Was the kill switch triggered?
    kill_switch_triggered = models.BooleanField(default=False)
    kill_switch_reason = models.TextField(blank=True)

    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Pilot Execution"
        verbose_name_plural = "Pilot Executions"
        ordering = ['-created_at']

    def __str__(self):
        return f"Pilot: {self.name} [{self.status}]"

    def start(self):
        """Start the pilot."""
        if self.status == 'planned':
            self.status = 'running'
            self.started_at = timezone.now()
            self.save()

            # Update gate
            self.gate.start_pilot()
            return True
        return False

    def complete(self, outcome: str, summary: str, learnings: list = None):
        """Complete the pilot with outcome."""
        self.status = 'completed'
        self.outcome = outcome
        self.outcome_summary = summary
        self.completed_at = timezone.now()
        if learnings:
            self.learnings = learnings
        self.save()

        # Update gate
        self.gate.complete_pilot()

    def trigger_kill_switch(self, reason: str):
        """Stop the pilot via kill switch."""
        self.status = 'stopped'
        self.outcome = 'failure'
        self.kill_switch_triggered = True
        self.kill_switch_reason = reason
        self.completed_at = timezone.now()
        self.outcome_summary = f"KILL SWITCH TRIGGERED: {reason}"
        self.save()

        # Update gate
        self.gate.complete_pilot()

    def add_learning(self, learning: str, category: str = 'general'):
        """Add a learning from the pilot."""
        self.learnings.append({
            'learning': learning,
            'category': category,
            'recorded_at': timezone.now().isoformat(),
        })
        self.save()

    def get_duration_hours(self) -> float:
        """Get pilot duration in hours."""
        if self.started_at:
            end = self.completed_at or timezone.now()
            delta = end - self.started_at
            return round(delta.total_seconds() / 3600, 1)
        return None


class Experiment(models.Model):
    """
    Session 596: Experiment Tracking Registry.

    Converts pilots into tracked experiments with KPI ownership.
    Based on ThinkingAgent insight about reducing decision fatigue
    through systematic experiment tracking.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to pilot
    pilot = models.OneToOneField(
        PilotExecution,
        on_delete=models.CASCADE,
        related_name='experiment'
    )

    # Experiment details
    name = models.CharField(max_length=255)
    hypothesis = models.TextField(blank=True, help_text="What we're testing")

    # KPI Ownership
    kpi_owner = models.CharField(max_length=100, blank=True, help_text="Who owns the outcome")
    primary_kpi = models.CharField(max_length=255, blank=True, help_text="Main metric to track")
    target_value = models.CharField(max_length=100, blank=True, help_text="Target KPI value")
    current_value = models.CharField(max_length=100, blank=True, null=True, help_text="Current KPI value")

    # Secondary KPIs (JSON list)
    secondary_kpis = models.JSONField(default=list, blank=True)

    # Status
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('success', 'Success'),
        ('failure', 'Failure'),
        ('partial', 'Partial Success'),
        ('inconclusive', 'Inconclusive'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')

    # Results
    result_summary = models.TextField(blank=True, null=True)
    learnings = models.TextField(blank=True, null=True)

    # AI-extracted data from checklist
    extracted_metrics = models.JSONField(default=dict, blank=True, help_text="Metrics extracted from AI-generated success_metrics")

    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Experiment"
        verbose_name_plural = "Experiments"
        ordering = ['-created_at']

    def __str__(self):
        return f"Experiment: {self.name} [{self.status}]"

    @classmethod
    def create_from_pilot(cls, pilot: PilotExecution):
        """
        Create an experiment from a pilot execution.
        Extracts KPIs from the AI-generated success_metrics checklist item.
        """
        gate = pilot.gate
        decision = gate.decision

        # Get success metrics from checklist
        success_metrics_item = gate.checklist_items.filter(item_type='success_metrics').first()
        extracted = {}
        primary_kpi = ""
        target_value = ""

        if success_metrics_item and success_metrics_item.documentation_notes:
            # Parse the AI-generated content for KPIs
            content = success_metrics_item.documentation_notes
            extracted = {
                'raw_content': content[:1000],  # Store first 1000 chars
                'source': 'ai_generated',
            }

            # Try to extract primary KPI (look for patterns like "5%", "150%", etc.)
            import re
            kpi_matches = re.findall(r'(\d+(?:\.\d+)?%?)\s*(?:engagement|ROI|rate|score)', content, re.IGNORECASE)
            if kpi_matches:
                target_value = kpi_matches[0]
                primary_kpi = "Engagement/ROI target"

        experiment = cls.objects.create(
            pilot=pilot,
            name=f"Experiment: {decision.topic[:100]}",
            hypothesis=f"Testing: {decision.topic}",
            primary_kpi=primary_kpi,
            target_value=target_value,
            extracted_metrics=extracted,
            kpi_owner="Unassigned",  # To be filled in
        )

        return experiment

    def complete(self, status: str, result_summary: str = None, learnings: str = None):
        """Complete the experiment with results."""
        self.status = status
        self.ended_at = timezone.now()
        if result_summary:
            self.result_summary = result_summary
        if learnings:
            self.learnings = learnings
        self.save()

    def update_kpi(self, current_value: str):
        """Update the current KPI value."""
        self.current_value = current_value
        self.save()
