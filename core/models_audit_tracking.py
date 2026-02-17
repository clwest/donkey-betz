"""
Session 819: Audit Tracking System

Models for tracking audit findings, remediation tasks, and verification runs.
Enables actionable audits that drive actual fixes.
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class AuditReport(models.Model):
    """
    Represents a single audit report (parsed from markdown files).
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
        related_name='audit_reports',
        help_text="Session 843: Project this report belongs to"
    )

    # Identity
    file_path = models.CharField(max_length=500, unique=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    # Classification
    AUDIT_TYPES = [
        ('system', 'System Audit'),
        ('security', 'Security Audit'),
        ('integration', 'Integration Audit'),
        ('performance', 'Performance Audit'),
        ('database', 'Database Audit'),
        ('api', 'API Audit'),
        ('agent', 'Agent Audit'),
        ('session', 'Session Audit'),
        ('other', 'Other'),
    ]
    audit_type = models.CharField(max_length=50, choices=AUDIT_TYPES, default='other')

    # Source
    auditor = models.CharField(max_length=100, default='Claude')
    session_number = models.IntegerField(null=True, blank=True)
    audit_date = models.DateField(null=True, blank=True)

    # Content
    raw_content = models.TextField(blank=True)
    executive_summary = models.TextField(blank=True)

    # Stats
    total_findings = models.IntegerField(default=0)
    p0_findings = models.IntegerField(default=0)
    p1_findings = models.IntegerField(default=0)
    p2_findings = models.IntegerField(default=0)
    open_findings = models.IntegerField(default=0)
    fixed_findings = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_parsed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'core_audit_report'
        ordering = ['-audit_date', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.audit_type})"

    def update_stats(self):
        """Update finding statistics."""
        findings = self.findings.all()
        self.total_findings = findings.count()
        self.p0_findings = findings.filter(priority='P0').count()
        self.p1_findings = findings.filter(priority='P1').count()
        self.p2_findings = findings.filter(priority='P2').count()
        self.open_findings = findings.filter(status='open').count()
        self.fixed_findings = findings.filter(status='fixed').count()
        self.save(update_fields=[
            'total_findings', 'p0_findings', 'p1_findings', 'p2_findings',
            'open_findings', 'fixed_findings', 'updated_at'
        ])


class AuditFinding(models.Model):
    """
    Individual finding from an audit report.
    Tracks status, remediation, and verification.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Source
    audit_report = models.ForeignKey(
        AuditReport,
        on_delete=models.CASCADE,
        related_name='findings'
    )

    # Identity
    finding_id = models.CharField(max_length=50, blank=True)  # e.g., "W001", "SEC-01"
    title = models.CharField(max_length=255)
    description = models.TextField()

    # Classification
    PRIORITY_CHOICES = [
        ('P0', 'P0 - Critical'),
        ('P1', 'P1 - High'),
        ('P2', 'P2 - Medium'),
        ('P3', 'P3 - Low'),
    ]
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='P2')

    CATEGORY_CHOICES = [
        ('security', 'Security'),
        ('authentication', 'Authentication'),
        ('performance', 'Performance'),
        ('consistency', 'Consistency'),
        ('documentation', 'Documentation'),
        ('integration', 'Integration'),
        ('data_integrity', 'Data Integrity'),
        ('code_quality', 'Code Quality'),
        ('other', 'Other'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')

    # Status
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('fixed', 'Fixed'),
        ('verified', 'Verified'),
        ('wontfix', "Won't Fix"),
        ('deferred', 'Deferred'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    # Impact
    IMPACT_CHOICES = [
        ('critical', 'Critical - System compromised'),
        ('high', 'High - Major functionality affected'),
        ('medium', 'Medium - Some functionality affected'),
        ('low', 'Low - Minor issue'),
    ]
    impact = models.CharField(max_length=20, choices=IMPACT_CHOICES, default='medium')

    # Location
    affected_files = models.JSONField(default=list)  # List of file paths
    affected_components = models.JSONField(default=list)  # e.g., ["API", "Auth"]

    # Remediation
    recommendation = models.TextField(blank=True)
    remediation_notes = models.TextField(blank=True)
    fixed_by = models.CharField(max_length=100, blank=True)  # Session number or PR
    fixed_at = models.DateTimeField(null=True, blank=True)

    # Verification
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)

    # Assignment
    assigned_agent = models.CharField(max_length=100, blank=True)
    assigned_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    raw_text = models.TextField(blank=True)  # Original text from audit
    metadata = models.JSONField(default=dict)

    # Session 949: Link findings to documents for RAG retrieval
    # This enables the RAG system to find related docs when incidents occur
    linked_document = models.ForeignKey(
        'content.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_findings',
        help_text="Document describing or related to this finding"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_audit_finding'
        ordering = ['priority', '-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['category']),
            models.Index(fields=['status', 'priority']),
        ]

    def __str__(self):
        return f"[{self.priority}] {self.title} ({self.status})"

    def mark_in_progress(self, agent_name: str = None):
        """Mark finding as being worked on."""
        self.status = 'in_progress'
        if agent_name:
            self.assigned_agent = agent_name
            self.assigned_at = timezone.now()
        self.save()

    def mark_fixed(self, fixed_by: str, notes: str = ''):
        """Mark finding as fixed."""
        self.status = 'fixed'
        self.fixed_by = fixed_by
        self.fixed_at = timezone.now()
        self.remediation_notes = notes
        self.save()
        self.audit_report.update_stats()

    def mark_verified(self, notes: str = ''):
        """Mark finding as verified."""
        self.status = 'verified'
        self.is_verified = True
        self.verified_at = timezone.now()
        self.verification_notes = notes
        self.save()
        self.audit_report.update_stats()

    def mark_wontfix(self, reason: str):
        """Mark finding as won't fix."""
        self.status = 'wontfix'
        self.remediation_notes = reason
        self.save()
        self.audit_report.update_stats()


class AuditRemediationTask(models.Model):
    """
    Task created to fix an audit finding.
    Can be assigned to agents or tracked manually.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Source
    finding = models.ForeignKey(
        AuditFinding,
        on_delete=models.CASCADE,
        related_name='remediation_tasks'
    )

    # Task details
    title = models.CharField(max_length=255)
    description = models.TextField()

    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('spec_complete', 'Spec Complete'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Assignment
    assigned_agent = models.CharField(max_length=100, blank=True)
    assigned_at = models.DateTimeField(null=True, blank=True)

    # Execution
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    execution_result = models.JSONField(default=dict)

    # Verification
    requires_verification = models.BooleanField(default=True)
    verification_command = models.TextField(blank=True)

    # Evidence of real work (commit, PR, diff, etc.)
    EVIDENCE_TYPE_CHOICES = [
        ('none', 'No Evidence'),
        ('commit', 'Git Commit'),
        ('pr', 'Pull Request'),
        ('diff', 'Diff/Patch'),
        ('patch_artifact', 'Patch Artifact'),
        ('manual_verify', 'Manually Verified'),
    ]
    evidence_type = models.CharField(
        max_length=30, choices=EVIDENCE_TYPE_CHOICES, default='none'
    )
    evidence_ref = models.CharField(
        max_length=500, blank=True,
        help_text="Commit hash, PR URL, or CodeArtifact UUID"
    )
    verified_by = models.CharField(
        max_length=100, blank=True,
        help_text="User or agent that verified the evidence"
    )
    evidence_verified_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_audit_remediation_task'
        ordering = ['-created_at']

    def __str__(self):
        return f"Task: {self.title} ({self.status})"

    def assign_to_agent(self, agent_name: str):
        """Assign task to an agent."""
        self.assigned_agent = agent_name
        self.assigned_at = timezone.now()
        self.status = 'assigned'
        self.save()

        # Update finding status
        self.finding.mark_in_progress(agent_name)

    def mark_spec_complete(self, result: dict = None):
        """Mark task as spec complete (agent produced output but no real code artifacts)."""
        self.status = 'spec_complete'
        self.completed_at = timezone.now()
        self.evidence_type = 'none'
        if result:
            self.execution_result = result
        self.save()

    def mark_completed(self, result: dict = None, evidence_type: str = 'manual_verify',
                       evidence_ref: str = '', verified_by: str = ''):
        """Mark task as completed with evidence of real work."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.evidence_type = evidence_type
        self.evidence_ref = evidence_ref
        self.verified_by = verified_by
        if evidence_type != 'none':
            self.evidence_verified_at = timezone.now()
        if result:
            self.execution_result = result
        self.save()


class AuditVerificationRun(models.Model):
    """
    Verification run to confirm a fix actually worked.
    Re-runs the relevant check after remediation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Source
    finding = models.ForeignKey(
        AuditFinding,
        on_delete=models.CASCADE,
        related_name='verification_runs'
    )

    # Execution
    verification_type = models.CharField(max_length=50)  # e.g., "grep_check", "api_test"
    verification_command = models.TextField(blank=True)

    # Results
    passed = models.BooleanField(default=False)
    result_summary = models.TextField(blank=True)
    result_details = models.JSONField(default=dict)

    # Timestamps
    executed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_audit_verification_run'
        ordering = ['-executed_at']

    def __str__(self):
        status = "PASS" if self.passed else "FAIL"
        return f"Verification [{status}]: {self.finding.title}"
