"""
Session 962 Phase 1: Deliberation Persistence Models

Makes deliberation sessions, turns, contracts, and doc versions durable and queryable.
DeliberationSession wraps HiveMindSession/ConceptForgeRun as a unifying envelope.

Models:
  - DeliberationSession: Unifying wrapper for any multi-agent session
  - DeliberationTurn: Individual agent turn within a session
  - ContractRecord: Persisted ResearchContract/SynthesisContract/ExecutionMandate
  - DocVersion: Version history for agent-written documents
"""

import uuid
import hashlib

from django.db import models


class DeliberationSession(models.Model):
    """Unifying envelope for HiveMindSession, ConceptForgeRun, and agent sessions."""

    SESSION_TYPE_CHOICES = [
        ('hivemind', 'Hive Mind'),
        ('conceptforge', 'ConceptForge'),
        ('agent', 'Agent'),
        ('composite', 'Composite'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    FAILURE_REASON_CHOICES = [
        ('', 'N/A'),
        ('TIMEOUT', 'Soft/hard time limit exceeded'),
        ('LLM_UPSTREAM', 'LLM provider error or rate limit'),
        ('EMPTY_TURN', 'Zero turns produced'),
        ('TOOL_ERROR', 'Tool call or spider failure'),
        ('GATE_REJECT', 'Publish gate or contract rejection'),
        ('DRAFT_FAILED', 'Draft generation failed'),
        ('UNKNOWN', 'Unclassified failure'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_type = models.CharField(
        max_length=20, choices=SESSION_TYPE_CHOICES, default='hivemind'
    )
    objective = models.TextField(blank=True, default='')
    participants = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    evidence_pack = models.JSONField(default=dict, blank=True)
    trace = models.JSONField(default=dict, blank=True)
    parent_session = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='children'
    )
    trace_id = models.CharField(max_length=64, blank=True, default='')
    failure_reason_code = models.CharField(
        max_length=20, choices=FAILURE_REASON_CHOICES, blank=True, default='',
        help_text='Structured reason code when status=failed',
    )
    failure_detail = models.TextField(
        blank=True, default='',
        help_text='Human-readable failure detail (exception message, stage info)',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Deliberation Session'
        verbose_name_plural = 'Deliberation Sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['trace_id']),
            models.Index(fields=['failure_reason_code']),
        ]

    def __str__(self):
        return f"Deliberation({self.session_type}, {self.status}) {self.objective[:60]}"


class DeliberationTurn(models.Model):
    """Individual agent turn within a deliberation session."""

    session = models.ForeignKey(
        DeliberationSession, on_delete=models.CASCADE, related_name='turns'
    )
    turn_number = models.IntegerField()
    agent_name = models.CharField(max_length=128)
    role = models.CharField(max_length=64, blank=True, default='')
    content = models.TextField()
    content_hash = models.CharField(max_length=64, blank=True, default='')
    contract_state = models.JSONField(null=True, blank=True)
    trace_id = models.CharField(max_length=64, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Deliberation Turn'
        verbose_name_plural = 'Deliberation Turns'
        ordering = ['session', 'turn_number']
        constraints = [
            models.UniqueConstraint(
                fields=['session', 'turn_number'],
                name='unique_session_turn'
            ),
        ]
        indexes = [
            models.Index(fields=['trace_id']),
        ]

    def __str__(self):
        return f"Turn {self.turn_number}: {self.agent_name} ({self.role})"

    def save(self, *args, **kwargs):
        if self.content and not self.content_hash:
            self.content_hash = hashlib.sha256(
                self.content.encode('utf-8')
            ).hexdigest()
        super().save(*args, **kwargs)


class ContractRecord(models.Model):
    """Persisted contract (Research/Synthesis/Execution) from a deliberation."""

    CONTRACT_TYPE_CHOICES = [
        ('research', 'Research'),
        ('synthesis', 'Synthesis'),
        ('execution', 'Execution'),
    ]

    session = models.ForeignKey(
        DeliberationSession, on_delete=models.CASCADE, related_name='contracts'
    )
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPE_CHOICES)
    contract_data = models.JSONField(default=dict)
    trace_id = models.CharField(max_length=64, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Contract Record'
        verbose_name_plural = 'Contract Records'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['contract_type']),
            models.Index(fields=['trace_id']),
        ]

    def __str__(self):
        return f"Contract({self.contract_type}) session={self.session_id}"


class DocVersion(models.Model):
    """Version history for agent-written documents."""

    doc_path = models.CharField(max_length=512)
    version_number = models.IntegerField()
    content_hash = models.CharField(max_length=64)
    content_snapshot = models.TextField()
    author_agent = models.CharField(max_length=128, blank=True, default='')
    deliberation_session = models.ForeignKey(
        DeliberationSession, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='doc_versions'
    )
    trace_id = models.CharField(max_length=64, blank=True, default='')
    change_reason = models.CharField(max_length=255, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Doc Version'
        verbose_name_plural = 'Doc Versions'
        ordering = ['doc_path', '-version_number']
        constraints = [
            models.UniqueConstraint(
                fields=['doc_path', 'version_number'],
                name='unique_doc_version'
            ),
        ]
        indexes = [
            models.Index(fields=['doc_path']),
            models.Index(fields=['trace_id']),
        ]

    def __str__(self):
        return f"{self.doc_path} v{self.version_number} by {self.author_agent}"
