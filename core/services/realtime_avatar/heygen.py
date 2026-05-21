"""HeyGen Streaming Avatar adapter — F2F v1 provider.

F2F.1 ships the scaffolding only. Constructor validates
``HEYGEN_API_KEY`` so a missing key fails fast with
``F2FUnavailableError`` instead of surfacing as a confusing 401
from HeyGen's API mid-session.

Real HTTP wiring lands in F2F.3 (STT → PA → TTS → avatar). The
broker (F2F.2) can be built against this surface using the mock
provider; switch to ``F2F_PROVIDER_MOCK=False`` once real-mode is
exercised.

References:
* HeyGen Streaming Avatar API docs (verify URLs before F2F.3 — they
  reorganized in late 2025).
* Cost model from Session 1118 F2F.0: ~$2.50/min mid-case avatar
  streaming (HeyGen tier-dependent). Caps wire into the F2F.2 broker.
"""
from __future__ import annotations

from django.conf import settings

from . import (
    F2FUnavailableError,
    SessionCreate,
    SessionState,
    SpeakResult,
)


class HeyGenF2FProvider:
    """HeyGen Streaming Avatar implementation. F2F.1 = stub.

    Constructor reads the API key from Django settings. Methods raise
    NotImplementedError with a pointer to the F2F slice that wires
    them. The mock provider exercises the contract until then.
    """

    provider_name = "heygen"

    # HeyGen API base. Documented as v2 streaming as of F2F.0 review;
    # verify in F2F.3 before first real call.
    api_base_url = "https://api.heygen.com"

    def __init__(self) -> None:
        api_key = getattr(settings, "HEYGEN_API_KEY", "") or ""
        if not api_key:
            raise F2FUnavailableError(
                "HEYGEN_API_KEY is not set. Either configure it in "
                "the environment or set F2F_PROVIDER_MOCK=True to "
                "use the deterministic mock."
            )
        self._api_key = api_key

    def create_session(
        self,
        avatar_id: str,
        voice_id: str | None = None,
    ) -> SessionCreate:
        raise NotImplementedError(
            "HeyGenF2FProvider.create_session: wired in F2F.3. Use "
            "MockF2FProvider until then (F2F_PROVIDER_MOCK=True)."
        )

    def speak(self, session_id: str, text: str) -> SpeakResult:
        raise NotImplementedError(
            "HeyGenF2FProvider.speak: wired in F2F.3."
        )

    def poll_session(self, session_id: str) -> SessionState:
        raise NotImplementedError(
            "HeyGenF2FProvider.poll_session: wired in F2F.3."
        )

    def end_session(self, session_id: str) -> None:
        raise NotImplementedError(
            "HeyGenF2FProvider.end_session: wired in F2F.3."
        )
