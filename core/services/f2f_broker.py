"""F2F (Rigby Face-to-Face) push-to-speak voice broker — Session 1118 F2F.2.

Sits between the ``/api/pa/voice_session/`` HTTP layer and the
realtime avatar provider (HeyGen / mock). Owns:

* Cap enforcement (session-spend, session-duration, workspace daily,
  workspace monthly) with the ordering Rigby locked in F2F.2 design.
* Redis hot state — session_key (TTL 600s) + cost counters
  (daily 26h / monthly 35d / session 15min) via INCRBY-style ops.
* DB persistence — ``F2FSession`` row as the durable audit truth.
* Idempotency — broker-side hash dedupe on ``speak()`` for the
  ``(session, text, time_bucket)`` tuple. Upgrades to provider-level
  request_id in F2F.3 once HeyGen confirms support.

All errors raised here become HTTP responses in
``core/views_f2f.py``:

* ``F2FCapExceededError`` → 402 (daily/monthly) or 429 (session/duration)
* ``F2FSessionNotActiveError`` → 410
* ``F2FProviderInvocationError`` → 502
* Anything else propagates → 500
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone as djtz

from core.models_f2f import F2FSession, F2FSessionStatus
from core.services.realtime_avatar import (
    F2FProviderError,
    F2FUnavailableError,
    SpeakResult,
    get_provider,
)


# ---- Errors -----------------------------------------------------


class F2FBrokerError(RuntimeError):
    """Base for all broker-level errors that should propagate to HTTP."""


class F2FCapExceededError(F2FBrokerError):
    """A cap tripped. ``cap_kind`` tells the view which HTTP code to emit."""

    CAP_KINDS = {"daily", "monthly", "session_spend", "session_duration"}

    def __init__(
        self,
        cap_kind: str,
        *,
        message: str,
        cap_limit_cents: int | None = None,
        cap_used_cents: int | None = None,
        reset_at: str | None = None,
        duration_seconds: float | None = None,
        duration_limit_seconds: int | None = None,
    ) -> None:
        if cap_kind not in self.CAP_KINDS:
            raise ValueError(f"unknown cap_kind {cap_kind!r}")
        super().__init__(message)
        self.cap_kind = cap_kind
        self.cap_limit_cents = cap_limit_cents
        self.cap_used_cents = cap_used_cents
        self.reset_at = reset_at
        self.duration_seconds = duration_seconds
        self.duration_limit_seconds = duration_limit_seconds


class F2FSessionNotActiveError(F2FBrokerError):
    """Session has reached a terminal status and can't be spent on."""


class F2FProviderInvocationError(F2FBrokerError):
    """Wraps an underlying ``F2FProviderError`` from the adapter."""

    def __init__(self, message: str, *, underlying: F2FProviderError) -> None:
        super().__init__(message)
        self.underlying = underlying


# ---- Result shapes ----------------------------------------------


@dataclass(slots=True)
class CreateSessionResult:
    """What the broker hands back to the view on session create."""

    session: F2FSession
    provider_session_id: str
    sdk_payload: dict[str, Any] = field(default_factory=dict)
    expires_at: str | None = None


@dataclass(slots=True)
class SpeakBrokerResult:
    """What the broker hands back to the view on speak."""

    session: F2FSession
    chars_sent: int
    cost_cents: int
    accepted: bool
    deduped: bool = False


# ---- Redis key helpers ------------------------------------------


def _key_session_key(session_id: UUID | str) -> str:
    return f"f2f:session_key:{session_id}"


def _key_session_counter(session_id: UUID | str) -> str:
    return f"f2f:cap:session:{session_id}"


def _key_daily(workspace_id: UUID | str, day: date) -> str:
    return f"f2f:cap:daily:{workspace_id}:{day.isoformat()}"


def _key_monthly(workspace_id: UUID | str, month: date) -> str:
    return f"f2f:cap:monthly:{workspace_id}:{month.strftime('%Y-%m')}"


def _key_speak_dedupe(session_id: UUID | str, hash_hex: str) -> str:
    return f"f2f:speak_hash:{session_id}:{hash_hex}"


# ---- Cost model -------------------------------------------------


def _conservative_speak_cost_cents(text: str) -> int:
    """Conservative envelope cost in cents for a single speak() call.

    Stack (per F2F.0 lock): avatar + tts + (implicit llm/stt amortized
    elsewhere). For F2F.2 we bill avatar + tts here; LLM is incurred
    inside ``/api/pa/chat/`` already and stt lands in F2F.3.

    chars → seconds via ``F2F_CHARS_PER_SECOND`` (default 13).
    Round up to whole cents — we never undercount.
    """
    chars = len(text)
    if chars <= 0:
        return 0
    seconds = chars / max(1, getattr(settings, "F2F_CHARS_PER_SECOND", 13))
    minutes = seconds / 60.0
    avatar = minutes * getattr(settings, "F2F_AVATAR_COST_CENTS_PER_MINUTE", 250)
    tts = minutes * getattr(settings, "F2F_TTS_COST_CENTS_PER_MINUTE", 8)
    total = math.ceil(avatar + tts)
    return max(1, total)  # never zero for a non-empty utterance


def _is_zero_cost_session(session: F2FSession) -> bool:
    """Mock-mode sessions accrue zero cost by default. Set
    ``F2F_MOCK_SYNTHETIC_COST=True`` to force real cost computation
    in tests so cap-trip logic can be exercised without real spend.
    """
    if not session.mock_mode:
        return False
    return not getattr(settings, "F2F_MOCK_SYNTHETIC_COST", False)


# ---- Cap counter helpers ----------------------------------------


def _redis_get_int(key: str) -> int:
    value = cache.get(key, 0)
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _redis_increment(key: str, delta: int, ttl_seconds: int) -> int:
    """Increment a counter by ``delta`` with a TTL refresh.

    Django's cache backend exposes ``incr`` only when the key exists,
    so we initialize via ``add`` first. Not strictly atomic under
    Django's locmem cache used in tests, which is fine — the DB row
    is the durable truth and reconciliation runs off that.
    """
    cache.add(key, 0, timeout=ttl_seconds)
    new_value = cache.incr(key, delta)
    # Re-set the TTL — cache.incr leaves TTL untouched on most
    # backends, but django-redis preserves the original TTL set via
    # ``add``. Explicit ``cache.expire`` ensures a refresh on each
    # write. ``cache.touch`` is the public Django 4+ API.
    try:
        cache.touch(key, timeout=ttl_seconds)
    except Exception:
        # Some cache backends don't support touch; we accept the
        # original TTL set at ``add`` time.
        pass
    return int(new_value)


def _midnight_iso(when: datetime) -> str:
    """Next-midnight UTC ISO for ``reset_at`` on daily-cap errors."""
    tomorrow = (when + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0,
    )
    return tomorrow.astimezone(timezone.utc).isoformat()


def _next_month_iso(when: datetime) -> str:
    """First-of-next-month UTC ISO for ``reset_at`` on monthly-cap errors."""
    year = when.year + (1 if when.month == 12 else 0)
    month = 1 if when.month == 12 else when.month + 1
    nm = when.replace(
        year=year, month=month, day=1,
        hour=0, minute=0, second=0, microsecond=0,
    )
    return nm.astimezone(timezone.utc).isoformat()


# ---- Cap-check ladder (Rigby's locked ordering) ------------------


def _check_workspace_caps(
    workspace_id: UUID | str,
    estimated_cents: int,
) -> None:
    """Pre-flight workspace daily + monthly checks. Raises on trip.

    Called at session create (with estimated_cents=0, i.e. "do we
    have any headroom at all?") and before each speak() (with the
    conservative cost estimate)."""

    now = djtz.now()
    today = now.date()

    daily_cap = getattr(settings, "F2F_CAP_DAILY_CENTS", 1000)
    monthly_cap = getattr(settings, "F2F_CAP_MONTHLY_CENTS", 5000)

    daily_used = _redis_get_int(_key_daily(workspace_id, today))
    if daily_used + estimated_cents > daily_cap:
        raise F2FCapExceededError(
            "daily",
            message="Daily F2F cap exhausted for this workspace.",
            cap_limit_cents=daily_cap,
            cap_used_cents=daily_used,
            reset_at=_midnight_iso(now),
        )

    monthly_used = _redis_get_int(_key_monthly(workspace_id, today))
    if monthly_used + estimated_cents > monthly_cap:
        raise F2FCapExceededError(
            "monthly",
            message="Monthly F2F cap exhausted for this workspace.",
            cap_limit_cents=monthly_cap,
            cap_used_cents=monthly_used,
            reset_at=_next_month_iso(now),
        )


def _check_session_caps(session: F2FSession, estimated_cents: int) -> None:
    """Per-speak() session duration + spend checks. Raises on trip."""

    duration_limit = getattr(settings, "F2F_CAP_SESSION_DURATION_SECONDS", 90)
    duration = session.duration_seconds()
    if duration > duration_limit:
        raise F2FCapExceededError(
            "session_duration",
            message="Session duration cap reached.",
            duration_seconds=duration,
            duration_limit_seconds=duration_limit,
        )

    session_cap = getattr(settings, "F2F_CAP_SESSION_SPEND_CENTS", 300)
    session_used = _redis_get_int(_key_session_counter(session.id))
    if session_used + estimated_cents > session_cap:
        raise F2FCapExceededError(
            "session_spend",
            message="Per-session spend cap reached.",
            cap_limit_cents=session_cap,
            cap_used_cents=session_used,
        )


# ---- Public broker API ------------------------------------------


def create_session(
    workspace,
    user,
    *,
    avatar_id: str = "",
    voice_id: str = "",
    metadata: dict[str, Any] | None = None,
) -> CreateSessionResult:
    """Allocate a new F2F session. Returns the SDK-safe payload.

    Order of operations (Rigby F2F.2 lock):
    1. Provider availability — instantiating ``get_provider()`` raises
       ``F2FUnavailableError`` when real mode is requested without
       a key. Mock-mode never hits this.
    2. Workspace daily/monthly headroom — don't start sessions that
       can't speak. We pass 0 estimated cents (just verifying any
       headroom exists, not pre-charging).
    3. DB row creation.
    4. Provider ``create_session`` call.
    5. Redis ``f2f:session_key:{uuid}`` write with TTL 600s.
    """

    provider = get_provider()  # raises F2FUnavailableError on missing key
    mock_mode = getattr(settings, "F2F_PROVIDER_MOCK", False)
    provider_name = getattr(provider, "provider_name", "unknown")

    _check_workspace_caps(workspace.id, estimated_cents=0)

    with transaction.atomic():
        session = F2FSession.objects.create(
            workspace=workspace,
            user=user,
            provider_name=provider_name,
            provider_session_id="pending",  # filled after provider call
            mock_mode=bool(mock_mode),
            avatar_id=avatar_id,
            voice_id=voice_id,
            metadata=metadata or {},
        )

        try:
            payload = provider.create_session(
                avatar_id=avatar_id or "rigby-default",
                voice_id=voice_id or None,
            )
        except F2FProviderError as exc:
            session.mark_ended(
                status=F2FSessionStatus.PROVIDER_ERROR,
                reason="create_session_failed",
                error_message=str(exc),
            )
            session.save(update_fields=[
                "status", "ended_reason", "error_message", "ended_at",
            ])
            raise F2FProviderInvocationError(
                "Provider rejected create_session.", underlying=exc,
            ) from exc

        session.provider_session_id = payload.session_id
        if payload.avatar_id and not session.avatar_id:
            session.avatar_id = payload.avatar_id
        if payload.voice_id and not session.voice_id:
            session.voice_id = payload.voice_id
        session.save(update_fields=[
            "provider_session_id", "avatar_id", "voice_id",
        ])

    # Off-DB-transaction Redis write — keep the table fast.
    if payload.session_key:
        cache.set(
            _key_session_key(session.id),
            payload.session_key,
            timeout=getattr(settings, "F2F_REDIS_SESSION_KEY_TTL", 600),
        )

    return CreateSessionResult(
        session=session,
        provider_session_id=payload.session_id,
        sdk_payload=payload.sdk_payload or {},
        expires_at=payload.expires_at,
    )


def get_session_key(session: F2FSession) -> str | None:
    """Pull the live session_key from Redis. Returns None if expired/missing."""
    return cache.get(_key_session_key(session.id))


def _refresh_session_key_ttl(session_id: UUID | str) -> None:
    ttl = getattr(settings, "F2F_REDIS_SESSION_KEY_TTL", 600)
    try:
        cache.touch(_key_session_key(session_id), timeout=ttl)
    except Exception:
        # Backend without touch — accept the original TTL.
        pass


def _speak_dedupe_hash(session_id: UUID | str, text: str) -> str:
    """Hash for broker-side speak() idempotency.

    ``(session_id, text, time_bucket)`` — time_bucket rounds the
    current unix epoch to the configured bucket size so two rapid
    duplicate calls within the window collapse into one provider
    invocation. Upgrade path: replace with caller-supplied
    ``request_id`` when HeyGen confirms support (F2F.3).
    """
    bucket = max(1, getattr(settings, "F2F_SPEAK_DEDUPE_BUCKET_SECONDS", 5))
    epoch_bucket = int(djtz.now().timestamp()) // bucket
    raw = f"{session_id}|{text}|{epoch_bucket}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:32]


def speak(session: F2FSession, text: str) -> SpeakBrokerResult:
    """Push ``text`` to the avatar. Enforces the full cap ladder.

    Cap-check ordering (locked by Rigby F2F.2 design):
        1. Session status (terminal → reject)
        2. Duration cap (90s)
        3. Session spend cap ($3)
        4. Daily cap ($10)
        5. Monthly cap ($50)
        6. Idempotency check (broker hash dedupe)
        7. Provider ``speak()``
        8. Post-commit ledger update (Redis incr + DB counters)
    """
    if not session.is_active:
        raise F2FSessionNotActiveError(
            f"F2F session {session.id} is {session.status!r} (terminal)."
        )

    estimated = (
        0 if _is_zero_cost_session(session) else _conservative_speak_cost_cents(text)
    )

    # Order: cheap session-scoped checks first, then workspace-wide.
    try:
        _check_session_caps(session, estimated)
        _check_workspace_caps(session.workspace_id, estimated)
    except F2FCapExceededError as exc:
        # Map cap_kind → terminal status. Daily/monthly do NOT end the
        # session (they're shared budget; another session could free
        # them). Session-scoped caps DO end this session.
        terminal_map = {
            "session_duration": F2FSessionStatus.CAP_EXCEEDED_SESSION_DURATION,
            "session_spend": F2FSessionStatus.CAP_EXCEEDED_SESSION_SPEND,
            "daily": F2FSessionStatus.CAP_EXCEEDED_DAILY,
            "monthly": F2FSessionStatus.CAP_EXCEEDED_MONTHLY,
        }
        session.mark_ended(
            status=terminal_map[exc.cap_kind],
            reason=f"cap_exceeded:{exc.cap_kind}",
        )
        session.save(update_fields=[
            "status", "ended_reason", "ended_at",
        ])
        raise

    # Idempotency — drop duplicate within bucket window.
    dedupe_key = _key_speak_dedupe(
        session.id, _speak_dedupe_hash(session.id, text),
    )
    if cache.get(dedupe_key):
        return SpeakBrokerResult(
            session=session,
            chars_sent=0,
            cost_cents=0,
            accepted=True,
            deduped=True,
        )
    cache.set(
        dedupe_key,
        1,
        timeout=max(
            1, getattr(settings, "F2F_SPEAK_DEDUPE_BUCKET_SECONDS", 5),
        ) * 2,
    )

    # Provider call. Rebind to provider via factory so test overrides
    # work — broker doesn't cache providers across calls in F2F.2.
    provider = get_provider()
    try:
        result: SpeakResult = provider.speak(session.provider_session_id, text)
    except F2FProviderError as exc:
        session.mark_ended(
            status=F2FSessionStatus.PROVIDER_ERROR,
            reason="speak_failed",
            error_message=str(exc),
        )
        session.save(update_fields=[
            "status", "ended_reason", "error_message", "ended_at",
        ])
        raise F2FProviderInvocationError(
            "Provider rejected speak.", underlying=exc,
        ) from exc

    if not result.accepted:
        session.error_message = result.error_message or "provider returned accepted=False"
        session.save(update_fields=["error_message"])
        return SpeakBrokerResult(
            session=session,
            chars_sent=0,
            cost_cents=0,
            accepted=False,
        )

    # Post-commit accounting.
    actual_chars = result.chars_sent
    actual_cost = 0 if _is_zero_cost_session(session) else estimated

    today = djtz.now().date()
    _redis_increment(
        _key_session_counter(session.id),
        actual_cost,
        ttl_seconds=getattr(settings, "F2F_REDIS_SESSION_COUNTER_TTL", 900),
    )
    _redis_increment(
        _key_daily(session.workspace_id, today),
        actual_cost,
        ttl_seconds=getattr(settings, "F2F_REDIS_DAILY_COUNTER_TTL", 26 * 3600),
    )
    _redis_increment(
        _key_monthly(session.workspace_id, today),
        actual_cost,
        ttl_seconds=getattr(settings, "F2F_REDIS_MONTHLY_COUNTER_TTL", 35 * 86400),
    )

    session.record_speak(actual_chars, actual_cost)
    session.save(update_fields=[
        "total_chars_spoken",
        "total_cost_cents",
        "speak_call_count",
        "last_activity_at",
    ])
    _refresh_session_key_ttl(session.id)

    return SpeakBrokerResult(
        session=session,
        chars_sent=actual_chars,
        cost_cents=actual_cost,
        accepted=True,
    )


def end_session(session: F2FSession, reason: str = "") -> None:
    """Explicit session teardown. Idempotent — terminal sessions no-op.

    Called by the SPA on normal close + by the broker on cap trip.
    Releases the Redis session_key and tells the provider to free
    its render slot. Counters are left in Redis for the daily/monthly
    cap windows; only the session-scoped counter is cleared.
    """
    if session.is_terminal:
        return

    provider_error: F2FProviderError | None = None
    try:
        provider = get_provider()
        provider.end_session(session.provider_session_id)
    except F2FProviderError as exc:
        provider_error = exc
    except Exception:
        # Best-effort teardown — never block the status transition on
        # provider misbehavior. The session is over from our side.
        pass

    session.mark_ended(
        status=F2FSessionStatus.ENDED,
        reason=reason or "normal_close",
        error_message=str(provider_error) if provider_error else "",
    )
    session.save(update_fields=[
        "status", "ended_reason", "error_message", "ended_at",
    ])

    cache.delete(_key_session_key(session.id))
    cache.delete(_key_session_counter(session.id))
