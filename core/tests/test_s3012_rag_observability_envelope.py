"""T-ENVELOPE-3 PR 3 (S3012) — Family E envelope tests for views_rag_observability.

Per Rigby A1 STRENGTHEN: locks the behavior restoration in the bundled
bug fix (auth checks were returning 500 due to bad `status_code=` kwarg
→ TypeError → middleware; now correctly return 401/403/500 per intent).
"""

from __future__ import annotations

import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class RAGObservabilityEnvelopeShapeTests(TestCase):
    """Locks the 401/403/500 restoration + Family E envelope shape."""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="s3012-rag-envelope-user",
            email="s3012-rag-envelope@donkeybetz.local",
        )
        self.user.set_unusable_password()
        self.user.save()
        # `rag_run_classification` has `@superuser_required` which runs
        # BEFORE the in-view auth/staff checks — those checks are
        # technically unreachable via the URL router. To exercise our
        # migrated internal_error branch we need a superuser to clear
        # the decorator.
        self.superuser = User.objects.create_user(
            username="s3012-rag-superuser",
            email="s3012-rag-super@donkeybetz.local",
        )
        self.superuser.is_staff = True
        self.superuser.is_superuser = True
        self.superuser.set_unusable_password()
        self.superuser.save()
        self.client = Client()

    def _assert_envelope(self, payload, *, reason_code):
        self.assertEqual(payload.get("reason_code"), reason_code)
        for key in ("support_code", "human_message", "retryable", "terminal_state", "timestamp"):
            self.assertIn(key, payload, f"envelope missing {key}")
        self.assertNotIn("success", payload)
        self.assertNotIn("error", payload)

    def test_unauthenticated_dashboard_returns_401_not_500(self):
        """Locks bug fix: was returning 500 due to bad `status_code=` kwarg."""
        response = self.client.get(reverse("rag-observability-dashboard"))
        self.assertEqual(response.status_code, 401, "auth check must return 401, not 500")
        self._assert_envelope(response.json(), reason_code="not_authenticated")

    def test_run_classification_internal_error_no_secret_leak(self):
        """Locks str(e) leak elimination — was in body via `f'Classification failed: {str(e)}'`."""
        self.client.force_login(self.superuser)
        # rag_run_classification queries content.models.Document; force the
        # first Q().filter chain to raise so we exercise the outer except.
        with patch("content.models.Document") as mock_doc:
            mock_doc.objects.filter.side_effect = RuntimeError("rag-secret-connstring-do-not-leak")
            response = self.client.post(
                reverse("rag-observability-classify"),
                data=json.dumps({"limit": 1, "force": True}),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 500)
        payload = response.json()
        self._assert_envelope(payload, reason_code="internal_error")
        self.assertNotIn("rag-secret-connstring-do-not-leak", json.dumps(payload),
                         "str(e) MUST NOT leak into user-facing body")
