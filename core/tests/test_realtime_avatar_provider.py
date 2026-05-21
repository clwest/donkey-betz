"""Tests for the F2F realtime avatar provider abstraction.

F2F.1 contract:
* Protocol is satisfied by the mock.
* ``get_provider`` resolves to mock when ``F2F_PROVIDER_MOCK=True``,
  regardless of name.
* ``get_provider`` resolves to HeyGen stub when mock disabled +
  key present.
* HeyGen constructor raises ``F2FUnavailableError`` when the API
  key is missing.
* Unknown provider name raises ``F2FProviderError``.

The HeyGen adapter's HTTP methods are NotImplementedError stubs
in F2F.1; we don't test them — F2F.3 will replace and cover them.
"""
from __future__ import annotations

from django.test import TestCase, override_settings

from core.services.realtime_avatar import (
    F2FProvider,
    F2FProviderError,
    F2FUnavailableError,
    SessionCreate,
    SessionState,
    SpeakResult,
    get_provider,
)
from core.services.realtime_avatar.mock import MockF2FProvider


@override_settings(F2F_PROVIDER_MOCK=True)
class MockProviderTests(TestCase):
    """The mock must obey the Protocol and round-trip deterministically."""

    def test_mock_satisfies_protocol(self):
        provider = MockF2FProvider()
        self.assertIsInstance(provider, F2FProvider)

    def test_create_session_deterministic(self):
        provider = MockF2FProvider()
        a = provider.create_session("rigby-avatar", voice_id="rigby-voice")
        b = provider.create_session("rigby-avatar", voice_id="rigby-voice")
        self.assertEqual(a.session_id, b.session_id)
        self.assertEqual(a.session_key, b.session_key)
        self.assertEqual(a.status, "ready")
        self.assertEqual(a.avatar_id, "rigby-avatar")
        self.assertEqual(a.voice_id, "rigby-voice")
        self.assertIsInstance(a, SessionCreate)

    def test_create_session_distinct_inputs(self):
        provider = MockF2FProvider()
        a = provider.create_session("rigby-avatar")
        b = provider.create_session("other-avatar")
        self.assertNotEqual(a.session_id, b.session_id)

    def test_speak_records_char_count(self):
        provider = MockF2FProvider()
        session = provider.create_session("rigby-avatar")
        result = provider.speak(session.session_id, "Hello, world.")
        self.assertIsInstance(result, SpeakResult)
        self.assertEqual(result.chars_sent, len("Hello, world."))
        self.assertTrue(result.accepted)

    def test_poll_session_returns_ready(self):
        provider = MockF2FProvider()
        session = provider.create_session("rigby-avatar")
        state = provider.poll_session(session.session_id)
        self.assertIsInstance(state, SessionState)
        self.assertEqual(state.status, "ready")

    def test_end_session_is_idempotent(self):
        provider = MockF2FProvider()
        session = provider.create_session("rigby-avatar")
        self.assertIsNone(provider.end_session(session.session_id))
        self.assertIsNone(provider.end_session(session.session_id))


class GetProviderResolutionTests(TestCase):
    """``get_provider`` must obey the registry + mock-mode rules."""

    @override_settings(F2F_PROVIDER_MOCK=True)
    def test_mock_mode_returns_mock_regardless_of_name(self):
        self.assertIsInstance(get_provider(), MockF2FProvider)
        self.assertIsInstance(get_provider("heygen"), MockF2FProvider)
        # Even an unknown name is overridden by mock mode (mock is
        # the safety net; missing keys must never crash a test run).
        self.assertIsInstance(get_provider("nonexistent"), MockF2FProvider)

    @override_settings(F2F_PROVIDER_MOCK=False, HEYGEN_API_KEY="test-key")
    def test_real_mode_returns_heygen_stub(self):
        from core.services.realtime_avatar.heygen import HeyGenF2FProvider

        provider = get_provider()
        self.assertIsInstance(provider, HeyGenF2FProvider)

    @override_settings(F2F_PROVIDER_MOCK=False, HEYGEN_API_KEY="")
    def test_real_mode_missing_key_raises_unavailable(self):
        with self.assertRaises(F2FUnavailableError):
            get_provider("heygen")

    @override_settings(F2F_PROVIDER_MOCK=False, HEYGEN_API_KEY="test-key")
    def test_unknown_provider_name_raises(self):
        with self.assertRaises(F2FProviderError):
            get_provider("nonexistent")


@override_settings(F2F_PROVIDER_MOCK=False, HEYGEN_API_KEY="test-key")
class HeyGenStubTests(TestCase):
    """F2F.1 ships HeyGen as a stub. Constructor works; methods raise."""

    def test_constructor_succeeds_with_key(self):
        from core.services.realtime_avatar.heygen import HeyGenF2FProvider

        provider = HeyGenF2FProvider()
        self.assertEqual(provider.provider_name, "heygen")

    def test_create_session_raises_not_implemented(self):
        from core.services.realtime_avatar.heygen import HeyGenF2FProvider

        provider = HeyGenF2FProvider()
        with self.assertRaises(NotImplementedError):
            provider.create_session("rigby-avatar")

    def test_speak_raises_not_implemented(self):
        from core.services.realtime_avatar.heygen import HeyGenF2FProvider

        provider = HeyGenF2FProvider()
        with self.assertRaises(NotImplementedError):
            provider.speak("session-1", "hi")
