"""
GovernanceState — Autonomy control plane state tracking.

Session: Autonomy #26 — Policy 30

Tracks global autonomy mode, per-agent overrides, and kill switches
with TTL-based auto-expiry. Single source of truth for system-wide
autonomy state.
"""

import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class GovernanceState(models.Model):
    """
    Global autonomy mode + per-scope overrides.

    Only ONE row should have scope='global' at a time.
    Additional rows act as per-agent or per-desk overrides.

    Modes: normal, throttle, freeze, safe_mode
    - normal:    all systems go, full autonomy
    - throttle:  reduced batch sizes, deferred non-critical tasks
    - freeze:    only critical LLM calls allowed
    - safe_mode: all autonomous actions paused, human approval required for everything
    """

    MODE_CHOICES = [
        ('normal', 'Normal'),
        ('throttle', 'Throttle'),
        ('freeze', 'Freeze'),
        ('safe_mode', 'Safe Mode'),
    ]

    SCOPE_CHOICES = [
        ('global', 'Global'),
        ('agent', 'Per-Agent'),
        ('desk', 'Per-Desk'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    scope = models.CharField(
        max_length=20, choices=SCOPE_CHOICES, default='global', db_index=True,
    )
    scope_target = models.CharField(
        max_length=200, blank=True,
        help_text="Agent name or desk name (empty for global)",
    )

    mode = models.CharField(
        max_length=20, choices=MODE_CHOICES, default='normal', db_index=True,
    )

    reason = models.TextField(
        blank=True,
        help_text="Why this mode was set",
    )

    set_by = models.CharField(
        max_length=100, blank=True,
        help_text="Who/what set this mode (user, autopilot, kill_switch)",
    )

    # TTL-based auto-expiry
    expires_at = models.DateTimeField(
        null=True, blank=True, db_index=True,
        help_text="Auto-revert to normal after this time (null = permanent until changed)",
    )

    # Tracking
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        db_table = 'core_governance_state'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['scope', 'scope_target']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['scope', 'scope_target'],
                name='unique_governance_scope_target',
            ),
        ]

    @property
    def is_expired(self):
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False

    @property
    def effective_mode(self):
        """Return 'normal' if expired, else the stored mode."""
        if self.is_expired:
            return 'normal'
        return self.mode

    def __str__(self):
        expired = ' [EXPIRED]' if self.is_expired else ''
        target = f':{self.scope_target}' if self.scope_target else ''
        ttl = f' (expires {self.expires_at.strftime("%Y-%m-%d %H:%M")})' if self.expires_at else ''
        return f"{self.scope}{target} → {self.mode}{ttl}{expired}"


class KillSwitch(models.Model):
    """
    Emergency kill switches with TTL-based auto-expiry.

    Each kill switch targets a specific action that should be blocked.
    Kill switches auto-expire to prevent permanent deadlocks.
    """

    TARGET_CHOICES = [
        ('scheduler', 'Pause all schedulers'),
        ('queue', 'Pause specific queue'),
        ('agent_family', 'Block agent family by tag'),
        ('publishing', 'Halt publishing'),
        ('outbound', 'Halt outbound messages'),
        ('deploys', 'Halt deploys'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    target = models.CharField(
        max_length=30, choices=TARGET_CHOICES, db_index=True,
    )
    target_detail = models.CharField(
        max_length=200, blank=True,
        help_text="Queue name, agent tag, etc.",
    )

    reason = models.TextField(
        blank=True,
        help_text="Why this kill switch was activated",
    )

    activated_by = models.CharField(
        max_length=100, blank=True,
        help_text="Who activated: user, autopilot, SLO_breach",
    )

    # TTL — kill switches MUST have an expiry to prevent permanent deadlocks
    expires_at = models.DateTimeField(
        db_index=True,
        help_text="Auto-deactivate after this time (required — no permanent kill switches)",
    )

    is_active = models.BooleanField(default=True, db_index=True)

    # Tracking
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        db_table = 'core_kill_switch'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['target', 'is_active']),
        ]

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def deactivate(self):
        self.is_active = False
        self.deactivated_at = timezone.now()
        self.save(update_fields=['is_active', 'deactivated_at'])

    def __str__(self):
        status = 'ACTIVE' if self.is_active and not self.is_expired else 'expired'
        detail = f':{self.target_detail}' if self.target_detail else ''
        return f"[{status}] {self.target}{detail} — {self.reason[:50]}"
