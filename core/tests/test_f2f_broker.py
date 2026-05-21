"""Tests for the F2F broker + voice session HTTP endpoints — Session 1118 F2F.2.

Two suites:
* ``F2FBrokerTests`` — service-level cap ladder, mock-mode accounting,
  dedupe, terminal-session handling.
* ``F2FVoiceSessionAPITests`` — DRF endpoint shape: status codes,
  JSON body keys, workspace ownership, error mapping.

All tests run with ``F2F_PROVIDER_MOCK=True`` so no provider creds
are required. ``F2F_MOCK_SYNTHETIC_COST=True`` is layered on cap-trip
tests so the mock provider accrues real cost and we can exercise the
cap ladder without burning money.
"""
from __future__ import annotations

from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APIClient

from core.models_skin_layer import ProjectWorkspace
from core.models_f2f import F2FSession, F2FSessionStatus
from core.services import f2f_broker

User = get_user_model()


# ---- Broker-level tests ----------------------------------------


@override_settings(F2F_PROVIDER_MOCK=True)
class F2FBrokerTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="rigby-broker", password="x", email="b@test.local",
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name="Broker WS",
        )

    def setUp(self):
        # Each test starts with a clean Redis (cache) state — broker
        # writes counters there and we don't want bleed-over.
        cache.clear()

    # ---- create_session --------------------------------------------

    def test_create_session_happy_path(self):
        result = f2f_broker.create_session(
            self.workspace, self.user, avatar_id="rigby", voice_id="v1",
        )
        self.assertEqual(result.session.status, F2FSessionStatus.ACTIVE)
        self.assertTrue(result.session.mock_mode)
        self.assertEqual(result.session.provider_name, "mock")
        self.assertEqual(result.session.avatar_id, "rigby")
        self.assertEqual(result.session.voice_id, "v1")
        # session_key must land in Redis under the F2FSession UUID.
        self.assertIsNotNone(f2f_broker.get_session_key(result.session))

    def test_create_session_blocked_by_daily_cap(self):
        # Pre-populate the daily cap counter at the limit.
        today = timezone.now().date()
        cache.set(
            f"f2f:cap:daily:{self.workspace.id}:{today.isoformat()}",
            1000,
            timeout=3600,
        )
        with self.assertRaises(f2f_broker.F2FCapExceededError) as ctx:
            f2f_broker.create_session(self.workspace, self.user)
        self.assertEqual(ctx.exception.cap_kind, "daily")

    # ---- speak — happy path ----------------------------------------

    def test_speak_zero_cost_for_mock(self):
        result = f2f_broker.create_session(self.workspace, self.user)
        speak = f2f_broker.speak(result.session, "Hello there.")
        self.assertTrue(speak.accepted)
        self.assertEqual(speak.cost_cents, 0)
        self.assertEqual(speak.chars_sent, len("Hello there."))
        self.assertFalse(speak.deduped)
        result.session.refresh_from_db()
        self.assertEqual(result.session.total_chars_spoken, len("Hello there."))
        self.assertEqual(result.session.speak_call_count, 1)
        self.assertEqual(result.session.total_cost_cents, 0)

    @override_settings(
        F2F_PROVIDER_MOCK=True, F2F_SPEAK_DEDUPE_BUCKET_SECONDS=60,
    )
    def test_speak_dedupes_repeat_within_bucket(self):
        # 60s bucket — two calls within the same test run will never
        # straddle a bucket boundary (the default 5s is tight enough
        # to flake under load).
        result = f2f_broker.create_session(self.workspace, self.user)
        first = f2f_broker.speak(result.session, "Same text.")
        second = f2f_broker.speak(result.session, "Same text.")
        self.assertFalse(first.deduped)
        self.assertTrue(second.deduped)
        self.assertEqual(second.cost_cents, 0)
        result.session.refresh_from_db()
        # Dedupe must not double-bump the counter.
        self.assertEqual(result.session.speak_call_count, 1)

    def test_speak_rejects_terminal_session(self):
        result = f2f_broker.create_session(self.workspace, self.user)
        result.session.mark_ended(reason="t")
        result.session.save(update_fields=["status", "ended_reason", "ended_at"])
        with self.assertRaises(f2f_broker.F2FSessionNotActiveError):
            f2f_broker.speak(result.session, "Hi")

    # ---- speak — cap trips (synthetic cost enabled) ----------------

    @override_settings(
        F2F_PROVIDER_MOCK=True,
        F2F_MOCK_SYNTHETIC_COST=True,
    )
    def test_speak_trips_session_spend_cap(self):
        # Pre-populate session counter near the $3 cap.
        result = f2f_broker.create_session(self.workspace, self.user)
        cache.set(
            f"f2f:cap:session:{result.session.id}", 295, timeout=900,
        )
        with self.assertRaises(f2f_broker.F2FCapExceededError) as ctx:
            f2f_broker.speak(result.session, "Long enough to cost a few cents.")
        self.assertEqual(ctx.exception.cap_kind, "session_spend")
        result.session.refresh_from_db()
        self.assertEqual(
            result.session.status,
            F2FSessionStatus.CAP_EXCEEDED_SESSION_SPEND,
        )
        self.assertTrue(result.session.is_terminal)

    @override_settings(
        F2F_PROVIDER_MOCK=True,
        F2F_MOCK_SYNTHETIC_COST=True,
        F2F_CAP_SESSION_DURATION_SECONDS=5,
    )
    def test_speak_trips_duration_cap(self):
        result = f2f_broker.create_session(self.workspace, self.user)
        # Simulate the session having started 10 seconds ago.
        F2FSession.objects.filter(id=result.session.id).update(
            started_at=timezone.now() - timedelta(seconds=10),
        )
        result.session.refresh_from_db()
        with self.assertRaises(f2f_broker.F2FCapExceededError) as ctx:
            f2f_broker.speak(result.session, "Tick tock.")
        self.assertEqual(ctx.exception.cap_kind, "session_duration")
        result.session.refresh_from_db()
        self.assertEqual(
            result.session.status,
            F2FSessionStatus.CAP_EXCEEDED_SESSION_DURATION,
        )

    @override_settings(
        F2F_PROVIDER_MOCK=True,
        F2F_MOCK_SYNTHETIC_COST=True,
        F2F_CAP_DAILY_CENTS=10,  # very low cap → first speak should trip
    )
    def test_speak_trips_daily_cap(self):
        result = f2f_broker.create_session(self.workspace, self.user)
        # Burn the daily cap right up to the limit before speak() runs.
        today = timezone.now().date()
        cache.set(
            f"f2f:cap:daily:{self.workspace.id}:{today.isoformat()}",
            10,
            timeout=3600,
        )
        with self.assertRaises(f2f_broker.F2FCapExceededError) as ctx:
            f2f_broker.speak(result.session, "Even a tiny utterance trips this.")
        self.assertEqual(ctx.exception.cap_kind, "daily")
        result.session.refresh_from_db()
        self.assertEqual(
            result.session.status,
            F2FSessionStatus.CAP_EXCEEDED_DAILY,
        )

    @override_settings(
        F2F_PROVIDER_MOCK=True,
        F2F_MOCK_SYNTHETIC_COST=True,
        F2F_CAP_MONTHLY_CENTS=10,
    )
    def test_speak_trips_monthly_cap(self):
        result = f2f_broker.create_session(self.workspace, self.user)
        today = timezone.now().date()
        cache.set(
            f"f2f:cap:monthly:{self.workspace.id}:{today.strftime('%Y-%m')}",
            10,
            timeout=3600,
        )
        with self.assertRaises(f2f_broker.F2FCapExceededError) as ctx:
            f2f_broker.speak(result.session, "Tip the monthly cap.")
        self.assertEqual(ctx.exception.cap_kind, "monthly")
        result.session.refresh_from_db()
        self.assertEqual(
            result.session.status,
            F2FSessionStatus.CAP_EXCEEDED_MONTHLY,
        )

    # ---- end_session -----------------------------------------------

    def test_end_session_releases_redis_state(self):
        result = f2f_broker.create_session(self.workspace, self.user)
        self.assertIsNotNone(f2f_broker.get_session_key(result.session))
        f2f_broker.end_session(result.session, reason="manual")
        result.session.refresh_from_db()
        self.assertEqual(result.session.status, F2FSessionStatus.ENDED)
        self.assertEqual(result.session.ended_reason, "manual")
        self.assertIsNone(f2f_broker.get_session_key(result.session))

    def test_end_session_is_idempotent(self):
        result = f2f_broker.create_session(self.workspace, self.user)
        f2f_broker.end_session(result.session, reason="first")
        f2f_broker.end_session(result.session, reason="second")
        result.session.refresh_from_db()
        # First call wins — never overwrite the original reason.
        self.assertEqual(result.session.ended_reason, "first")


# ---- HTTP endpoint tests ----------------------------------------


@override_settings(F2F_PROVIDER_MOCK=True)
class F2FVoiceSessionAPITests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="rigby-api", password="x", email="api@test.local",
        )
        cls.other_user = User.objects.create_user(
            username="rigby-other", password="x", email="o@test.local",
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name="API WS",
        )
        cls.other_workspace = ProjectWorkspace.objects.create(
            user=cls.other_user, name="Other WS",
        )

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    # ---- create ----------------------------------------------------

    def test_create_returns_201_with_sdk_payload(self):
        response = self.client.post(
            reverse("f2f-voice-session-create"),
            {"workspace_id": str(self.workspace.id), "avatar_id": "rigby"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertIn("session_id", body)
        self.assertEqual(body["mock_mode"], True)
        self.assertEqual(body["provider_name"], "mock")
        self.assertEqual(body["status"], "active")
        self.assertEqual(body["avatar_id"], "rigby")
        self.assertIn("sdk_payload", body)

    def test_create_missing_workspace_id_returns_400(self):
        response = self.client.post(
            reverse("f2f-voice-session-create"), {}, format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error_code"], "F2F_WORKSPACE_REQUIRED",
        )

    def test_create_other_users_workspace_returns_404(self):
        response = self.client.post(
            reverse("f2f-voice-session-create"),
            {"workspace_id": str(self.other_workspace.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json()["error_code"], "F2F_WORKSPACE_NOT_FOUND",
        )

    @override_settings(F2F_PROVIDER_MOCK=False, HEYGEN_API_KEY="")
    def test_create_when_provider_unavailable_returns_503(self):
        response = self.client.post(
            reverse("f2f-voice-session-create"),
            {"workspace_id": str(self.workspace.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json()["error_code"], "F2F_PROVIDER_UNAVAILABLE",
        )

    # ---- speak -----------------------------------------------------

    def _create_session_via_api(self) -> str:
        response = self.client.post(
            reverse("f2f-voice-session-create"),
            {"workspace_id": str(self.workspace.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        return response.json()["session_id"]

    def test_speak_happy_path(self):
        session_id = self._create_session_via_api()
        response = self.client.post(
            reverse(
                "f2f-voice-session-speak",
                kwargs={"session_id": session_id},
            ),
            {"text": "Hello, operator."},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["accepted"])
        self.assertFalse(body["deduped"])
        self.assertEqual(body["chars_sent"], len("Hello, operator."))
        self.assertEqual(body["cost_cents"], 0)
        self.assertEqual(body["status"], "active")

    def test_speak_missing_text_returns_400(self):
        session_id = self._create_session_via_api()
        response = self.client.post(
            reverse(
                "f2f-voice-session-speak",
                kwargs={"session_id": session_id},
            ),
            {},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error_code"], "F2F_TEXT_REQUIRED")

    def test_speak_on_terminal_session_returns_410(self):
        session_id = self._create_session_via_api()
        # End it first.
        end_url = reverse(
            "f2f-voice-session-end",
            kwargs={"session_id": session_id},
        )
        self.client.post(end_url, {}, format="json")
        # Now try to speak.
        response = self.client.post(
            reverse(
                "f2f-voice-session-speak",
                kwargs={"session_id": session_id},
            ),
            {"text": "Still here?"},
            format="json",
        )
        self.assertEqual(response.status_code, 410)
        self.assertEqual(
            response.json()["error_code"], "F2F_SESSION_NOT_ACTIVE",
        )

    @override_settings(
        F2F_PROVIDER_MOCK=True,
        F2F_MOCK_SYNTHETIC_COST=True,
        F2F_CAP_DAILY_CENTS=10,
    )
    def test_speak_daily_cap_trip_returns_402_with_locked_body(self):
        session_id = self._create_session_via_api()
        today = timezone.now().date()
        cache.set(
            f"f2f:cap:daily:{self.workspace.id}:{today.isoformat()}",
            10,
            timeout=3600,
        )
        response = self.client.post(
            reverse(
                "f2f-voice-session-speak",
                kwargs={"session_id": session_id},
            ),
            {"text": "Trip the cap."},
            format="json",
        )
        self.assertEqual(response.status_code, 402)
        body = response.json()
        self.assertEqual(body["error_code"], "F2F_CAP_EXCEEDED_DAILY")
        self.assertEqual(body["cap_kind"], "daily")
        self.assertIn("reset_at", body)
        self.assertEqual(body["provider_name"], "mock")
        self.assertEqual(body["mock_mode"], True)

    @override_settings(
        F2F_PROVIDER_MOCK=True,
        F2F_MOCK_SYNTHETIC_COST=True,
        F2F_CAP_SESSION_DURATION_SECONDS=5,
    )
    def test_speak_duration_cap_trip_returns_429(self):
        session_id = self._create_session_via_api()
        F2FSession.objects.filter(id=session_id).update(
            started_at=timezone.now() - timedelta(seconds=10),
        )
        response = self.client.post(
            reverse(
                "f2f-voice-session-speak",
                kwargs={"session_id": session_id},
            ),
            {"text": "Time's up."},
            format="json",
        )
        self.assertEqual(response.status_code, 429)
        body = response.json()
        self.assertEqual(
            body["error_code"], "F2F_CAP_EXCEEDED_SESSION_DURATION",
        )
        self.assertEqual(body["cap_kind"], "session_duration")
        self.assertIn("duration_seconds", body)
        self.assertEqual(body["duration_limit_seconds"], 5)

    # ---- end -------------------------------------------------------

    def test_end_returns_200_with_terminal_state(self):
        session_id = self._create_session_via_api()
        response = self.client.post(
            reverse(
                "f2f-voice-session-end",
                kwargs={"session_id": session_id},
            ),
            {"reason": "operator_close"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ended")
        self.assertEqual(body["ended_reason"], "operator_close")
        self.assertIsNotNone(body["ended_at"])

    def test_end_other_users_session_returns_404(self):
        # Other user creates a session…
        other_client = APIClient()
        other_client.force_authenticate(self.other_user)
        other_session_id = other_client.post(
            reverse("f2f-voice-session-create"),
            {"workspace_id": str(self.other_workspace.id)},
            format="json",
        ).json()["session_id"]
        # …we shouldn't be able to end it.
        response = self.client.post(
            reverse(
                "f2f-voice-session-end",
                kwargs={"session_id": other_session_id},
            ),
            {},
            format="json",
        )
        self.assertEqual(response.status_code, 404)

    # ---- auth ------------------------------------------------------

    def test_unauthenticated_create_returns_401_or_403(self):
        anon = APIClient()
        response = anon.post(
            reverse("f2f-voice-session-create"),
            {"workspace_id": str(self.workspace.id)},
            format="json",
        )
        self.assertIn(response.status_code, (401, 403))
