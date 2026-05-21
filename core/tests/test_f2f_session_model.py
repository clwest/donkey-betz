"""Tests for the F2FSession model — Session 1118 F2F.2.

Covers the durable record's lifecycle helpers (status transitions,
counter bumps, duration math) without touching the broker.
"""
from __future__ import annotations

from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.models_skin_layer import ProjectWorkspace
from core.models_f2f import (
    F2FSession,
    F2FSessionStatus,
    TERMINAL_STATUSES,
)


User = get_user_model()


class F2FSessionLifecycleTests(TestCase):
    """Model-level lifecycle: create, status transitions, counters."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="rigby-user",
            password="x",
            email="rigby@test.local",
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name="Test Workspace",
        )

    def _make_session(self, **overrides) -> F2FSession:
        defaults = {
            "workspace": self.workspace,
            "user": self.user,
            "provider_name": "mock",
            "provider_session_id": "mock_session_abc123",
            "mock_mode": True,
        }
        defaults.update(overrides)
        return F2FSession.objects.create(**defaults)

    # ---- Defaults --------------------------------------------------

    def test_new_session_starts_active(self):
        session = self._make_session()
        self.assertEqual(session.status, F2FSessionStatus.ACTIVE)
        self.assertTrue(session.is_active)
        self.assertFalse(session.is_terminal)
        self.assertEqual(session.total_chars_spoken, 0)
        self.assertEqual(session.total_cost_cents, 0)
        self.assertEqual(session.speak_call_count, 0)
        self.assertIsNone(session.ended_at)
        self.assertEqual(session.ended_reason, "")

    # ---- mark_ended ------------------------------------------------

    def test_mark_ended_default_uses_ended_status(self):
        session = self._make_session()
        session.mark_ended(reason="normal_close")
        self.assertEqual(session.status, F2FSessionStatus.ENDED)
        self.assertEqual(session.ended_reason, "normal_close")
        self.assertIsNotNone(session.ended_at)
        self.assertTrue(session.is_terminal)
        self.assertFalse(session.is_active)

    def test_mark_ended_with_cap_status(self):
        session = self._make_session()
        session.mark_ended(
            status=F2FSessionStatus.CAP_EXCEEDED_SESSION_SPEND,
            reason="cap_exceeded:session_spend",
        )
        self.assertEqual(
            session.status,
            F2FSessionStatus.CAP_EXCEEDED_SESSION_SPEND,
        )
        self.assertTrue(session.is_terminal)

    def test_mark_ended_is_idempotent(self):
        session = self._make_session()
        session.mark_ended(reason="first")
        first_ended_at = session.ended_at
        # Calling again must not overwrite status or ended_at.
        session.mark_ended(reason="second", status=F2FSessionStatus.PROVIDER_ERROR)
        self.assertEqual(session.status, F2FSessionStatus.ENDED)
        self.assertEqual(session.ended_reason, "first")
        self.assertEqual(session.ended_at, first_ended_at)

    def test_mark_ended_carries_error_message(self):
        session = self._make_session()
        session.mark_ended(
            status=F2FSessionStatus.PROVIDER_ERROR,
            reason="speak_failed",
            error_message="HeyGen 500",
        )
        self.assertEqual(session.error_message, "HeyGen 500")

    # ---- record_speak ----------------------------------------------

    def test_record_speak_bumps_counters(self):
        session = self._make_session()
        session.record_speak(chars=42, cost_cents=15)
        session.record_speak(chars=58, cost_cents=20)
        self.assertEqual(session.total_chars_spoken, 100)
        self.assertEqual(session.total_cost_cents, 35)
        self.assertEqual(session.speak_call_count, 2)

    def test_record_speak_updates_last_activity(self):
        session = self._make_session()
        original = session.last_activity_at
        with patch(
            "core.models_f2f.timezone.now",
            return_value=timezone.now() + timedelta(seconds=30),
        ):
            session.record_speak(chars=10, cost_cents=5)
        self.assertGreater(session.last_activity_at, original)

    # ---- duration --------------------------------------------------

    def test_duration_seconds_uses_now_when_active(self):
        session = self._make_session()
        # Simulate the session started 45s ago.
        session.started_at = timezone.now() - timedelta(seconds=45)
        duration = session.duration_seconds()
        self.assertGreater(duration, 44)
        self.assertLess(duration, 46)

    def test_duration_seconds_uses_ended_at_when_terminal(self):
        session = self._make_session()
        session.started_at = timezone.now() - timedelta(seconds=120)
        session.mark_ended(reason="t")
        session.ended_at = session.started_at + timedelta(seconds=89)
        self.assertAlmostEqual(session.duration_seconds(), 89.0, places=2)

    # ---- Terminal set invariant ------------------------------------

    def test_terminal_set_excludes_active(self):
        self.assertNotIn(F2FSessionStatus.ACTIVE, TERMINAL_STATUSES)

    def test_all_non_active_statuses_are_terminal(self):
        for status in F2FSessionStatus:
            if status == F2FSessionStatus.ACTIVE:
                continue
            with self.subTest(status=status):
                self.assertIn(status, TERMINAL_STATUSES)

    # ---- __str__ ---------------------------------------------------

    def test_str_includes_id_and_status(self):
        session = self._make_session()
        rep = str(session)
        self.assertIn(str(session.id), rep)
        self.assertIn("mock", rep)
        self.assertIn("active", rep)
