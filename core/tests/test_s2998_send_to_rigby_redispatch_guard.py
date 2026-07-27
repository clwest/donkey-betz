"""Session 2998 — send-to-rigby re-dispatch guard (Fold D from S2997).

send-to-rigby now refuses to re-dispatch a finding whose
`deliverable_id` is already set, unless the caller explicitly passes
`{"force": true}` in the request body. Returns 409 Conflict with
`existing_deliverable_id` so callers (UI/PA/curl) can navigate to what
was already produced.

Frontend (S2995 hotfix) already transforms the button to "View
deliverable" so the UI is dispatch-safe — this guard is defense-in-
depth for direct API calls, PA-tool dispatches, and bulk ops.

Force flag is strict boolean True per Rigby T1 SIGN extra: truthy
strings like `"true"`, `"yes"`, or integer `1` do NOT count. Force use
is server-logged (WARNING level) for audit since it's a token-burn
escape hatch.
"""
from __future__ import annotations

import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from core.services import briefing_spec_generator as bsg
from core.models_audit_findings import DocResearchFinding
from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace


DONKEY_BETZ_WORKSPACE_ID = "b4503364-2573-4401-9e28-61a739e0ce50"
EXISTING_DELIVERABLE_ID = "aaaaaaaa-1111-2222-3333-444444444444"


class RedispatchGuardTests(TestCase):
    """POST /send-to-rigby/ refuses when deliverable_id set; force overrides."""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="s2998_tester", password="pw", email="s2998@test.local"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        ProjectWorkspace.objects.get_or_create(
            id=DONKEY_BETZ_WORKSPACE_ID,
            defaults={
                "name": "Donkey Betz (test)",
                "user": self.user,
                "root_path": "/tmp/test-donkey-betz",
            },
        )

    def _make_finding(self, *, deliverable_id=""):
        return DocResearchFinding.objects.create(
            source_type="audit",
            source_heading="Executable Actions",
            doc_path="docs/x.md",
            domain_slug="test",
            text=f"Test bullet {deliverable_id or 'fresh'}",
            text_hash=f"h-{timezone.now().timestamp()}-{deliverable_id or 'x'}"[:64],
            confidence="high",
            status=DocResearchFinding.STATUS_OPEN,
            finding_type=DocResearchFinding.FINDING_TYPE_EXECUTABLE,
            staleness=DocResearchFinding.STALENESS_FRESH,
            deliverable_id=deliverable_id,
        )

    def _stub_llm(self):
        return json.dumps({
            "goal": "Test goal",
            "context": "Test context",
            "open_question": "None",
            "files_implicated": [],
            "acceptance_criteria": ["AC1.", "AC2.", "AC3."],
        })

    def _post(self, finding_id, body=None):
        kwargs = {}
        if body is not None:
            kwargs["data"] = json.dumps(body)
            kwargs["content_type"] = "application/json"
        return self.client.post(
            f"/api/repo/doc-research-findings/{finding_id}/send-to-rigby/",
            **kwargs,
        )

    # ---- fresh finding path (unchanged) ----

    def test_fresh_finding_no_body_dispatches(self):
        finding = self._make_finding(deliverable_id="")
        with patch.object(bsg, "_call_spec_llm", return_value=self._stub_llm()):
            resp = self._post(finding.id)
        self.assertEqual(resp.status_code, 201, resp.content[:400])

    def test_fresh_finding_empty_body_dispatches(self):
        finding = self._make_finding(deliverable_id="")
        with patch.object(bsg, "_call_spec_llm", return_value=self._stub_llm()):
            resp = self._post(finding.id, body={})
        self.assertEqual(resp.status_code, 201, resp.content[:400])

    # ---- refusal path (deliverable_id set) ----

    def test_dispatched_finding_no_body_refuses(self):
        finding = self._make_finding(deliverable_id=EXISTING_DELIVERABLE_ID)
        with patch.object(bsg, "_call_spec_llm") as mock_llm:
            resp = self._post(finding.id)
        self.assertEqual(resp.status_code, 409, resp.content[:400])
        # No LLM call should have happened.
        mock_llm.assert_not_called()
        payload = resp.json()
        self.assertEqual(payload["reason_code"], "deliverable_already_exists")
        self.assertEqual(payload["existing_deliverable_id"], EXISTING_DELIVERABLE_ID)
        self.assertEqual(payload["finding_id"], str(finding.id))

    def test_dispatched_finding_empty_body_refuses(self):
        finding = self._make_finding(deliverable_id=EXISTING_DELIVERABLE_ID)
        with patch.object(bsg, "_call_spec_llm") as mock_llm:
            resp = self._post(finding.id, body={})
        self.assertEqual(resp.status_code, 409)
        mock_llm.assert_not_called()

    def test_dispatched_finding_force_false_refuses(self):
        finding = self._make_finding(deliverable_id=EXISTING_DELIVERABLE_ID)
        with patch.object(bsg, "_call_spec_llm") as mock_llm:
            resp = self._post(finding.id, body={"force": False})
        self.assertEqual(resp.status_code, 409)
        mock_llm.assert_not_called()

    # ---- strict force=True (per Rigby T1 SIGN extra) ----

    def test_dispatched_finding_force_true_string_refuses(self):
        # "true" is truthy but not strict True; MUST NOT override.
        finding = self._make_finding(deliverable_id=EXISTING_DELIVERABLE_ID)
        with patch.object(bsg, "_call_spec_llm") as mock_llm:
            resp = self._post(finding.id, body={"force": "true"})
        self.assertEqual(resp.status_code, 409)
        mock_llm.assert_not_called()

    def test_dispatched_finding_force_one_int_refuses(self):
        # 1 is truthy but not strict True; MUST NOT override.
        finding = self._make_finding(deliverable_id=EXISTING_DELIVERABLE_ID)
        with patch.object(bsg, "_call_spec_llm") as mock_llm:
            resp = self._post(finding.id, body={"force": 1})
        self.assertEqual(resp.status_code, 409)
        mock_llm.assert_not_called()

    def test_dispatched_finding_force_true_boolean_overrides(self):
        finding = self._make_finding(deliverable_id=EXISTING_DELIVERABLE_ID)
        with patch.object(bsg, "_call_spec_llm", return_value=self._stub_llm()):
            resp = self._post(finding.id, body={"force": True})
        self.assertEqual(resp.status_code, 201, resp.content[:400])
        # New deliverable replaces old ID.
        finding.refresh_from_db()
        new_id = resp.json()["deliverable_id"]
        self.assertEqual(finding.deliverable_id, new_id)
        self.assertNotEqual(new_id, EXISTING_DELIVERABLE_ID)

    # ---- invalid body handling ----

    def test_invalid_json_body_returns_400(self):
        finding = self._make_finding(deliverable_id=EXISTING_DELIVERABLE_ID)
        # Send raw non-JSON body.
        resp = self.client.post(
            f"/api/repo/doc-research-findings/{finding.id}/send-to-rigby/",
            data="not json",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_non_dict_body_ignored_still_refuses(self):
        # Body is a valid JSON array, not an object — force can't be
        # extracted; guard still refuses.
        finding = self._make_finding(deliverable_id=EXISTING_DELIVERABLE_ID)
        with patch.object(bsg, "_call_spec_llm") as mock_llm:
            resp = self.client.post(
                f"/api/repo/doc-research-findings/{finding.id}/send-to-rigby/",
                data=json.dumps(["force", True]),
                content_type="application/json",
            )
        self.assertEqual(resp.status_code, 409)
        mock_llm.assert_not_called()

    # ---- audit log on force use ----

    def test_force_override_emits_warning_log(self):
        finding = self._make_finding(deliverable_id=EXISTING_DELIVERABLE_ID)
        with self.assertLogs(
            "core.views_doc_research_findings", level="WARNING"
        ) as log_capture:
            with patch.object(bsg, "_call_spec_llm", return_value=self._stub_llm()):
                resp = self._post(finding.id, body={"force": True})
        self.assertEqual(resp.status_code, 201)
        # Log message includes finding id, replaced deliverable id, and user.
        joined = "\n".join(log_capture.output)
        self.assertIn("FORCE re-dispatch", joined)
        self.assertIn(str(finding.id), joined)
        self.assertIn(EXISTING_DELIVERABLE_ID, joined)
        self.assertIn("s2998_tester", joined)
