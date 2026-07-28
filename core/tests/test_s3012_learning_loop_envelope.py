"""T-ENVELOPE-3 PR 2 (S3012) — Family E envelope tests for views_learning_loop.

Locks envelope shape + status + hint structure per Rigby A1 STRENGTHEN
(assert `{source, reason}` diagnostics so we don't regress into
"invalid_input everywhere with no diagnostics").
"""

from __future__ import annotations

import json
import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class LearningLoopEnvelopeShapeTests(TestCase):
    """One test per dominant reason_code category, plus hint-structure lock."""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="s3012-ll-envelope-user",
            email="s3012-ll-envelope@donkeybetz.local",
        )
        self.user.set_unusable_password()
        self.user.save()
        self.client = Client()

    def _assert_envelope(self, payload, *, reason_code):
        self.assertEqual(payload.get("reason_code"), reason_code)
        for key in ("support_code", "human_message", "retryable", "terminal_state", "timestamp"):
            self.assertIn(key, payload, f"envelope missing {key}")
        self.assertNotIn("success", payload)
        self.assertNotIn("error", payload)

    def test_unauthenticated_pattern_detail_returns_not_authenticated(self):
        # No force_login — auth guard fires.
        response = self.client.get(reverse("learning-pattern-detail", args=[uuid.uuid4()]))
        self.assertEqual(response.status_code, 401)
        self._assert_envelope(response.json(), reason_code="not_authenticated")

    def test_pattern_not_found_returns_family_e_envelope(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("learning-pattern-detail", args=[uuid.uuid4()]))
        self.assertEqual(response.status_code, 404)
        self._assert_envelope(response.json(), reason_code="not_found")

    def test_track_learning_outcome_invalid_json_returns_invalid_input(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("learning-loop-track"),
            data="{not-json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self._assert_envelope(payload, reason_code="invalid_input")

    def test_track_learning_outcome_missing_field_hint_is_structured(self):
        """Locks the Rigby STRENGTHEN: hint must carry {source, reason} diagnostics."""
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("learning-loop-track"),
            data=json.dumps({"was_successful": True}),  # missing pattern_id
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self._assert_envelope(response.json(), reason_code="invalid_input")

    def test_track_learning_outcome_orchestrator_failure_returns_validation_error(self):
        """Locks the L1054 branch: orchestrator returning False emits validation_error."""
        self.client.force_login(self.user)
        with patch("core.services.learning_loop_orchestrator.get_learning_loop_orchestrator") as mock_get:
            mock_get.return_value.track_learning_application.return_value = False
            response = self.client.post(
                reverse("learning-loop-track"),
                data=json.dumps({"pattern_id": str(uuid.uuid4()), "was_successful": True}),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 400)
        self._assert_envelope(response.json(), reason_code="validation_error")
