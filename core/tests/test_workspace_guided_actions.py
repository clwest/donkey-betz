"""
Tests for Workspace Home v1 PR4 Guided Actions endpoints (S2984).

Spec §2.4 (Guided Actions) + §5 (Instrumentation). Two backend surfaces:
  - POST /api/workspaces/<id>/shift-brief/  — invokes build_shift_brief
  - POST /api/v1/telemetry/event/           — generic UI event counter

Run::

    USE_PGBOUNCER=0 python manage.py test core.tests.test_workspace_guided_actions -v 2
"""

from __future__ import annotations

import json
import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from core.models_skin_layer import ProjectWorkspace


User = get_user_model()


class ShiftBriefEndpointTests(TestCase):
    """POST /api/workspaces/<id>/shift-brief/ — invokes build_shift_brief."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            username=f"s2984-sb-{uuid.uuid4().hex[:8]}",
            email="s2984-sb@example.com",
            password="x",
            is_superuser=True,
        )
        cls.other_user = User.objects.create_user(
            username=f"s2984-sb-other-{uuid.uuid4().hex[:8]}",
            email="s2984-sb-other@example.com",
            password="x",
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user,
            name="S2984 PR4 Workspace",
            allow_autonomous_writes=True,
        )

    def setUp(self) -> None:
        self.client = APIClient()

    def test_requires_authentication(self) -> None:
        url = reverse("workspace-shift-brief", args=[self.workspace.id])
        resp = self.client.post(url)
        self.assertIn(resp.status_code, (401, 403))

    def test_returns_brief_shape_on_success(self) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse("workspace-shift-brief", args=[self.workspace.id])
        fake_brief = {
            "ok": True,
            "summary_text": "All systems green. No blockers.",
            "traffic_light": "GREEN",
            "sections": {"ops": {"runs": 0}},
            "metadata": {"runtime_ms": 12, "degraded_fields": []},
        }
        with patch(
            "core.services.rigby_shift_brief.build_shift_brief", return_value=fake_brief
        ) as mocked:
            resp = self.client.post(url)

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["ok"])
        self.assertEqual(body["summary_text"], "All systems green. No blockers.")
        self.assertEqual(body["traffic_light"], "GREEN")
        self.assertEqual(body["workspace_id"], str(self.workspace.id))
        self.assertIn("generated_at", body)
        mocked.assert_called_once()
        # Called with user_id + conversation_id=None + window="24h" (v1 unscoped).
        _, kwargs = mocked.call_args
        self.assertEqual(kwargs["user_id"], self.user.id)
        self.assertIsNone(kwargs["conversation_id"])
        self.assertEqual(kwargs["window"], "24h")

    def test_returns_502_on_brief_failure(self) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse("workspace-shift-brief", args=[self.workspace.id])
        with patch(
            "core.services.rigby_shift_brief.build_shift_brief",
            side_effect=RuntimeError("simulated"),
        ):
            resp = self.client.post(url)
        self.assertEqual(resp.status_code, 502)
        body = resp.json()
        self.assertFalse(body["ok"])
        self.assertEqual(body["error"], "shift_brief_failed")

    def test_non_owner_gets_404(self) -> None:
        self.client.force_authenticate(user=self.other_user)
        url = reverse("workspace-shift-brief", args=[self.workspace.id])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 404)

    def test_missing_workspace_returns_404(self) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse("workspace-shift-brief", args=[uuid.uuid4()])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 404)


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
class TelemetryEventEndpointTests(TestCase):
    """POST /api/v1/telemetry/event/ — never blocks UI, always 204."""

    def setUp(self) -> None:
        self.client = Client()

    def test_valid_event_returns_204(self) -> None:
        resp = self.client.post(
            "/api/v1/telemetry/event/",
            data=json.dumps({"event": "guided_action_clicked", "workspace_id": "wsid-1"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 204)

    def test_missing_event_returns_204_no_op(self) -> None:
        resp = self.client.post(
            "/api/v1/telemetry/event/",
            data=json.dumps({"workspace_id": "wsid-1"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 204)

    def test_bad_json_returns_204(self) -> None:
        resp = self.client.post(
            "/api/v1/telemetry/event/",
            data="not json",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 204)

    def test_no_auth_required(self) -> None:
        """
        Matches page_view_api behavior — telemetry is best-effort and must
        never require auth (would silently break UI on session drift).
        """
        resp = self.client.post(
            "/api/v1/telemetry/event/",
            data=json.dumps({"event": "workspace_home_viewed"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 204)

    def test_counter_increments_on_valid_event(self) -> None:
        from django.core.cache import cache
        from datetime import date

        cache.clear()
        for _ in range(3):
            self.client.post(
                "/api/v1/telemetry/event/",
                data=json.dumps({"event": "guided_action_clicked"}),
                content_type="application/json",
            )
        today = date.today().isoformat()
        self.assertEqual(cache.get(f"ui_events:{today}:guided_action_clicked", 0), 3)
