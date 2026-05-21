"""Realtime avatar provider abstraction — F2F (Rigby Face-to-Face).

Push-to-speak shape: u-d-b's PA owns the LLM and conversation
history, so the avatar provider only renders text-in → lip-synced
audio/video-out. No conversational LLM inside the provider, no
document attachment, no transcript pull — those concerns already
live in /api/pa/chat/ + ChatConversation.

This is the architectural pivot from Character OS Session 215:
Runway's conversational realtime avatar can't be steered via tool
descriptions (greeting-bias class of bug). u-d-b sidesteps that by
keeping STT → LLM → TTS server-side and treating the avatar as a
dumb lip-sync renderer.

F2F.1 scope: define the Protocol, ship a deterministic mock, scaffold
the HeyGen adapter as a not-yet-wired stub. F2F.2 wires
``/api/pa/voice_session/`` against this Protocol. F2F.3 wires real
HeyGen calls in ``heygen.py``.

Pattern lifted from character-os/media-engine RealtimeProvider with
the conversational methods (attach_documents, create_document,
fetch_transcript) dropped because they don't apply to push-to-speak.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

# ---- Provider-shared dataclasses --------------------------------


@dataclass(slots=True)
class SessionCreate:
    """Result of ``create_session``. SDK-safe payload the SPA needs
    to connect via WebRTC / WebSocket."""

    session_id: str
    # Opaque provider token. NEVER logged. The F2F.2 broker
    # persists this on the F2FSession row.
    session_key: str
    status: str  # 'creating' | 'not_ready' | 'ready' | 'failed'
    expires_at: str | None = None
    avatar_id: str | None = None
    voice_id: str | None = None
    # Provider-specific WebRTC offer / connection params. Shape
    # varies by provider; the SPA passes it through to the SDK.
    sdk_payload: dict = field(default_factory=dict)


@dataclass(slots=True)
class SessionState:
    """Result of ``poll_session`` — drives the
    creating → not_ready → ready transition."""

    session_id: str
    status: str
    expires_at: str | None = None
    error_message: str = ""


@dataclass(slots=True)
class SpeakResult:
    """Result of ``speak``. Most providers fire-and-forget the text;
    the return carries enough metadata for the cost ledger to record
    a usage line."""

    session_id: str
    chars_sent: int
    accepted: bool = True
    error_message: str = ""


# ---- Protocol ---------------------------------------------------


@runtime_checkable
class F2FProvider(Protocol):
    """Push-to-speak avatar provider contract. Single named adapter
    pattern — call sites use ``get_provider`` and never branch on
    provider name.

    For F2F.1 the Protocol is text-in. If HeyGen turns out to need
    pre-rendered audio bytes from Cartesia (instead of doing its own
    TTS), F2F.3 will add a ``speak_audio`` variant. Keeping the
    surface minimal so the broker can ship in F2F.2 without waiting.
    """

    def create_session(
        self,
        avatar_id: str,
        voice_id: str | None = None,
    ) -> SessionCreate:
        """Start a live avatar streaming session."""
        ...

    def speak(self, session_id: str, text: str) -> SpeakResult:
        """Push text to the avatar for TTS + lip-sync rendering."""
        ...

    def poll_session(self, session_id: str) -> SessionState:
        """Check session status. Cheap; safe to poll."""
        ...

    def end_session(self, session_id: str) -> None:
        """Explicit teardown. Always called on session close, even
        on error, so the provider can release its render slot."""
        ...


# ---- Errors -----------------------------------------------------


class F2FProviderError(RuntimeError):
    """Wraps upstream / configuration failures. The F2F.2 broker
    turns these into F2FSession.status='failed' rows + HTTP 5xx."""


class F2FUnavailableError(F2FProviderError):
    """Configuration says F2F can't run right now — mock-mode
    without explicit allow, missing HEYGEN_API_KEY, etc. Maps to
    HTTP 503; operator can retry or check config."""


# ---- Registry ---------------------------------------------------


# Provider name registry. Order matters only for the unknown-name
# error message. Add new providers here + a branch in ``get_provider``.
KNOWN_PROVIDERS = ("heygen",)


def get_provider(name: str | None = None) -> F2FProvider:
    """Look up a provider by name. v1 ships HeyGen + a mock.

    Resolution rules (mirrors core/services/realtime_provider in COS):

    1. If ``F2F_PROVIDER_MOCK`` is True (settings.py or env), return
       the mock regardless of ``name``. Tests + local dev use this
       path so nothing burns HeyGen credits.
    2. If ``name`` is None, use ``settings.F2F_PROVIDER_NAME``
       (default 'heygen').
    3. If the named provider is unknown, raise ``F2FProviderError``.
    4. If the provider requires an API key and it's missing, raise
       ``F2FUnavailableError`` (the provider's own constructor does
       this check; this function just propagates).
    """
    from django.conf import settings

    if getattr(settings, "F2F_PROVIDER_MOCK", False):
        from .mock import MockF2FProvider

        return MockF2FProvider()

    resolved = name or getattr(settings, "F2F_PROVIDER_NAME", "heygen")

    if resolved == "heygen":
        from .heygen import HeyGenF2FProvider

        return HeyGenF2FProvider()

    raise F2FProviderError(
        f"unknown F2F provider {resolved!r}. "
        f"Registered: {list(KNOWN_PROVIDERS)}"
    )


__all__ = [
    "F2FProvider",
    "F2FProviderError",
    "F2FUnavailableError",
    "KNOWN_PROVIDERS",
    "SessionCreate",
    "SessionState",
    "SpeakResult",
    "get_provider",
]
