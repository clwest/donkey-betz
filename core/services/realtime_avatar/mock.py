"""Deterministic mock F2F provider.

Used for:
* Tests — same inputs round-trip to the same session_id.
* Local dev when ``F2F_PROVIDER_MOCK=True`` (default when
  ``HEYGEN_API_KEY`` is empty).
* CI runs that need predictable output without burning credits.

Implements every Protocol method so F2F.2 (broker) and F2F.3 (real
wiring) can test the full happy path without touching HeyGen.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

from . import SessionCreate, SessionState, SpeakResult


def _digest(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


def _iso_future(seconds: int = 600) -> str:
    return (
        datetime.now(tz=timezone.utc) + timedelta(seconds=seconds)
    ).isoformat()


class MockF2FProvider:
    """Deterministic stubs. Same key inputs → same outputs so tests
    can assert on session_id round-trip and broker state machines."""

    provider_name = "mock"

    def create_session(
        self,
        avatar_id: str,
        voice_id: str | None = None,
    ) -> SessionCreate:
        digest = _digest(avatar_id, voice_id or "")
        return SessionCreate(
            session_id=f"mock_session_{digest}",
            session_key=f"mock_session_key_{digest}",
            status="ready",  # mock skips creating → not_ready
            expires_at=_iso_future(),
            avatar_id=avatar_id,
            voice_id=voice_id,
            sdk_payload={"mock": True},
        )

    def speak(self, session_id: str, text: str) -> SpeakResult:
        return SpeakResult(
            session_id=session_id,
            chars_sent=len(text),
            accepted=True,
        )

    def poll_session(self, session_id: str) -> SessionState:
        return SessionState(
            session_id=session_id,
            status="ready",
            expires_at=_iso_future(),
        )

    def end_session(self, session_id: str) -> None:
        return None
