"""F2F (Rigby Face-to-Face) realtime avatar session model.

Session 1118 F2F.2. Durable session record for the push-to-speak
voice loop. The broker creates one row per ``/api/pa/voice_session/``
that talks to a provider; Redis holds the hot session_key + cap
counters keyed off this row's UUID.

Design lock from Rigby (memory_id 5 + F2F.2 design pass):

* ``session_key`` is **not** stored here — it lives in Redis at
  ``f2f:session_key:{f2f_session_uuid}`` with TTL 600s, refreshed on
  every speak() / poll_session(). Off disk by design.
* Cap counters live in Redis (``f2f:cap:daily``, ``f2f:cap:monthly``,
  ``f2f:cap:session``) for fast atomic INCRBY-style gating. This
  table holds the durable audit + reconciliation truth.
* Status is the single source of truth for "is this session
  spendable". Cap-exceeded statuses are terminal.

Pattern mirrors ``core/models_audio_cache.py``: plain ``models.Model``
+ inline UUID PK, ``app_label='core'`` in Meta, registered via
``core/models/__init__.py``.
"""
from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class F2FSessionStatus(models.TextChoices):
    """Terminal-or-active status for an F2F session.

    ``ACTIVE`` is the only spendable status. Everything else is
    terminal — once set, never reverts. Cap-exceeded variants carry
    enough info that the SPA can render the right error (daily vs
    monthly vs session-spend vs session-duration).
    """

    ACTIVE = "active", "Active"
    ENDED = "ended", "Ended (normal)"
    CAP_EXCEEDED_DAILY = "cap_exceeded_daily", "Cap exceeded — daily"
    CAP_EXCEEDED_MONTHLY = "cap_exceeded_monthly", "Cap exceeded — monthly"
    CAP_EXCEEDED_SESSION_SPEND = (
        "cap_exceeded_session_spend",
        "Cap exceeded — session spend",
    )
    CAP_EXCEEDED_SESSION_DURATION = (
        "cap_exceeded_session_duration",
        "Cap exceeded — session duration",
    )
    PROVIDER_ERROR = "provider_error", "Provider error"
    BROKER_ERROR = "broker_error", "Broker error"


# Statuses that are terminal — broker must never mutate counters once
# the session reaches one of these. Keep in sync with F2FSessionStatus.
TERMINAL_STATUSES = frozenset(
    {
        F2FSessionStatus.ENDED,
        F2FSessionStatus.CAP_EXCEEDED_DAILY,
        F2FSessionStatus.CAP_EXCEEDED_MONTHLY,
        F2FSessionStatus.CAP_EXCEEDED_SESSION_SPEND,
        F2FSessionStatus.CAP_EXCEEDED_SESSION_DURATION,
        F2FSessionStatus.PROVIDER_ERROR,
        F2FSessionStatus.BROKER_ERROR,
    }
)


class F2FSession(models.Model):
    """One push-to-speak avatar session bound to a workspace + user.

    Lifecycle:
    1. Broker creates row with ``status=ACTIVE``, ``started_at=now``.
    2. Each ``speak()`` updates ``last_activity_at`` and the counters.
    3. Cap trip or normal close sets ``ended_at`` + a terminal status
       + ``ended_reason``.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="F2F session UUID. Also keys the Redis session_key entry.",
    )

    # ---- Ownership ----------------------------------------------

    workspace = models.ForeignKey(
        "core.ProjectWorkspace",
        on_delete=models.CASCADE,
        related_name="f2f_sessions",
        db_index=True,
        help_text="Workspace this session bills against.",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="f2f_sessions",
        db_index=True,
        help_text="User who opened this session.",
    )

    # ---- Provider identity --------------------------------------

    provider_name = models.CharField(
        max_length=32,
        db_index=True,
        help_text="Realtime avatar provider — 'heygen' or 'mock'.",
    )
    provider_session_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Provider's own session id (returned by create_session).",
    )
    mock_mode = models.BooleanField(
        default=False,
        db_index=True,
        help_text=(
            "True when F2F_PROVIDER_MOCK is on. Mock sessions log usage "
            "but do not move cost caps."
        ),
    )

    # ---- Status -------------------------------------------------

    status = models.CharField(
        max_length=40,
        choices=F2FSessionStatus.choices,
        default=F2FSessionStatus.ACTIVE,
        db_index=True,
    )
    ended_reason = models.TextField(
        blank=True,
        default="",
        help_text="Human-readable reason for the terminal status.",
    )
    error_message = models.TextField(
        blank=True,
        default="",
        help_text="Provider or broker error detail. Never operator-visible.",
    )

    # ---- Timestamps ---------------------------------------------

    started_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Session creation timestamp. Drives the duration cap.",
    )
    last_activity_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Updated on every speak() / poll_session() call.",
    )
    ended_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Set when status transitions to a terminal value.",
    )

    # ---- Counters (durable audit; Redis holds the hot copy) -----

    total_chars_spoken = models.PositiveIntegerField(
        default=0,
        help_text="Sum of characters successfully sent via speak().",
    )
    total_cost_cents = models.PositiveIntegerField(
        default=0,
        help_text=(
            "Realized spend across all cost buckets (stt+llm+tts+avatar) "
            "in whole cents. Source of truth for reconciliation."
        ),
    )
    speak_call_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of speak() invocations that returned accepted=True.",
    )

    # ---- Provider-specific extras + audit ------------------------

    avatar_id = models.CharField(
        max_length=128,
        blank=True,
        default="",
        help_text="Provider's avatar identifier — HeyGen avatar persona id, etc.",
    )
    voice_id = models.CharField(
        max_length=128,
        blank=True,
        default="",
        help_text="Provider's voice identifier (when TTS is provider-side).",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Free-form provider extras (HeyGen region, Cartesia voice "
            "params, request_id seeds for future idempotency, etc.). "
            "Never PII; never the session_key."
        ),
    )

    class Meta:
        app_label = "core"
        ordering = ("-started_at",)
        indexes = [
            # Cap aggregation: "what did this workspace spend today?"
            models.Index(
                fields=("workspace", "started_at"),
                name="f2f_ws_started_idx",
            ),
            # Per-workspace active-session lookup.
            models.Index(
                fields=("workspace", "status"),
                name="f2f_ws_status_idx",
            ),
            # Per-user session listings for the SPA history surface.
            models.Index(
                fields=("user", "started_at"),
                name="f2f_user_started_idx",
            ),
        ]

    # ---- Helpers ------------------------------------------------

    def __str__(self) -> str:
        return f"F2FSession({self.id} {self.provider_name} {self.status})"

    @property
    def is_active(self) -> bool:
        """True iff broker may still spend on this session."""
        return self.status == F2FSessionStatus.ACTIVE

    @property
    def is_terminal(self) -> bool:
        return self.status in TERMINAL_STATUSES

    def duration_seconds(self) -> float:
        """Elapsed wall-clock seconds. Uses ``ended_at`` when set,
        else now. Broker compares this against the 90s duration cap
        before each speak()."""
        end = self.ended_at or timezone.now()
        return (end - self.started_at).total_seconds()

    def mark_ended(
        self,
        status: str = F2FSessionStatus.ENDED,
        reason: str = "",
        error_message: str = "",
    ) -> None:
        """Transition to a terminal status. Idempotent — calling
        twice on an already-terminal session is a no-op. Caller is
        responsible for ``save()``.
        """
        if self.is_terminal:
            return
        self.status = status
        self.ended_reason = reason
        if error_message:
            self.error_message = error_message
        self.ended_at = timezone.now()

    def record_speak(self, chars: int, cost_cents: int) -> None:
        """Bump counters after a successful speak(). Caller is
        responsible for ``save(update_fields=[...])``."""
        self.total_chars_spoken += chars
        self.total_cost_cents += cost_cents
        self.speak_call_count += 1
        self.last_activity_at = timezone.now()
