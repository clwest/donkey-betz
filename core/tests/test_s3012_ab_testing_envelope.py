"""T-ENVELOPE-3 PR 1 (S3012) — Family E envelope tests for views_ab_testing.

Locks envelope shape + status code per Rigby A1 STRENGTHEN #1: one test per
category (not_found / invalid_input / validation_error / internal_error) so
CI catches drift if a future edit reverts a site or breaks the helper.

Wired goals endpoints (list_goals / create_goal / goal_detail /
update_goal_progress) are exercised through the URL router. Dead A/B
testing handlers are migrated in-place per Rigby DECIDE Shape A but not
covered here (URL routes removed at S1103c).
"""

from __future__ import annotations

import json
import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class ABTestingEnvelopeShapeTests(TestCase):
    """One test per reason_code category — envelope shape + status."""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="s3012-envelope-user",
            email="s3012-envelope@donkeybetz.local",
        )
        self.user.set_unusable_password()
        self.user.save()
        self.client = Client()
        self.client.force_login(self.user)

    def _assert_envelope(self, payload, *, reason_code):
        # Family E envelope keys per contract §3.1.
        self.assertEqual(payload.get("reason_code"), reason_code)
        for key in ("support_code", "human_message", "retryable", "terminal_state", "timestamp"):
            self.assertIn(key, payload, f"envelope missing {key}")
        self.assertNotIn("success", payload, "Family E envelope must not carry legacy `success` key")
        self.assertNotIn("error", payload, "Family E envelope must not carry legacy `error` key")

    def test_goal_detail_not_found_returns_family_e_envelope(self):
        random_id = uuid.uuid4()
        response = self.client.get(reverse("goals-detail", args=[random_id]))
        self.assertEqual(response.status_code, 404)
        self._assert_envelope(response.json(), reason_code="not_found")

    def test_create_goal_missing_field_returns_invalid_input(self):
        response = self.client.post(
            reverse("goals-create"),
            data=json.dumps({"name": "only-a-name"}),  # missing goal_type / target_value / start_date
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self._assert_envelope(response.json(), reason_code="invalid_input")

    def test_create_goal_invalid_json_returns_invalid_input(self):
        response = self.client.post(
            reverse("goals-create"),
            data="{not-json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self._assert_envelope(response.json(), reason_code="invalid_input")

    def test_update_goal_progress_missing_current_value_returns_invalid_input(self):
        # UserGoal.objects.get(id=...) runs before the current_value check,
        # so we need a real goal to reach the validation branch.
        from core.models_unified_system import UserGoal
        from datetime import date

        goal = UserGoal.objects.create(
            user=self.user,
            name="s3012-envelope-fixture",
            goal_type="revenue",
            target_value=100,
            start_date=date.today(),
        )
        response = self.client.post(
            reverse("goals-update-progress", args=[goal.id]),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self._assert_envelope(response.json(), reason_code="invalid_input")

    def test_list_goals_internal_error_returns_family_e_envelope(self):
        # Force UserGoal.objects.filter() to raise; validates the wired
        # `except Exception` path emits internal_error + does not leak str(e).
        with patch("core.views_ab_testing.UserGoal") as mock_model:
            mock_model.objects.filter.side_effect = RuntimeError("db-blew-up-secret-connstring")
            response = self.client.get(reverse("goals-list"))
        self.assertEqual(response.status_code, 500)
        payload = response.json()
        self._assert_envelope(payload, reason_code="internal_error")
        # Safety: raw exception message MUST NOT appear in user-facing body.
        self.assertNotIn("db-blew-up-secret-connstring", json.dumps(payload))
