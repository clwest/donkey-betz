"""Session 2993 — briefing_spec_generator prompt branching on finding_type
(Findings-surface v2 item #3).

`generate_spec_body` now accepts an optional `finding_type` kwarg. When
`decision_evidence`, the prompt is rebuilt to CAPTURE the boundary/verdict
the finding records (acceptance_criteria become verification steps) rather
than propose engineering work. `executable`, `unknown`, None, or unrecognized
values fall through to the pre-existing engineering-spec prompt.

Tests here cover:
- prompt-shape resolver per finding_type value
- system-prompt distinguishing text
- generate_spec_body extras (spec_prompt_shape + finding_type_used)
- fail-open placeholder copy diverges per shape
- send-to-rigby view forwards finding.finding_type
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


class ResolvePromptShapeTests(TestCase):
    """finding_type → prompt shape mapping is total + case-tolerant."""

    def test_decision_evidence_maps_to_evidence(self):
        self.assertEqual(
            bsg._resolve_prompt_shape("decision_evidence"),
            bsg.PROMPT_SHAPE_EVIDENCE,
        )

    def test_executable_maps_to_engineering(self):
        self.assertEqual(
            bsg._resolve_prompt_shape("executable"),
            bsg.PROMPT_SHAPE_ENGINEERING,
        )

    def test_unknown_maps_to_engineering(self):
        self.assertEqual(
            bsg._resolve_prompt_shape("unknown"),
            bsg.PROMPT_SHAPE_ENGINEERING,
        )

    def test_none_maps_to_engineering(self):
        self.assertEqual(
            bsg._resolve_prompt_shape(None),
            bsg.PROMPT_SHAPE_ENGINEERING,
        )

    def test_unrecognized_falls_through_to_engineering(self):
        self.assertEqual(
            bsg._resolve_prompt_shape("something_new"),
            bsg.PROMPT_SHAPE_ENGINEERING,
        )

    def test_case_insensitive(self):
        self.assertEqual(
            bsg._resolve_prompt_shape("Decision_Evidence"),
            bsg.PROMPT_SHAPE_EVIDENCE,
        )


class PromptRouterTests(TestCase):
    """_build_spec_prompt routes to the correct sub-builder per shape."""

    CITATIONS = [{"path": "docs/example.md", "snippet": "boundary snippet"}]

    def test_engineering_shape_uses_imperative_framing(self):
        system, _user = bsg._build_spec_prompt(
            bullet_text="Add pagination to feed endpoint",
            section_title="Executable Actions",
            anchor_path="docs/example.md",
            citations=self.CITATIONS,
            prompt_shape=bsg.PROMPT_SHAPE_ENGINEERING,
        )
        # Engineering prompt asks for imperative goal, testable acceptance criteria.
        self.assertIn("code-writing AI agent will pick up and implement", system)
        self.assertNotIn("boundary/verdict", system)

    def test_evidence_shape_reframes_goal_and_ac(self):
        system, _user = bsg._build_spec_prompt(
            bullet_text="Zero visibility into 9.8% of frontend HTTP surface.",
            section_title="Boundary Violations",
            anchor_path="docs/example.md",
            citations=self.CITATIONS,
            prompt_shape=bsg.PROMPT_SHAPE_EVIDENCE,
        )
        # Evidence prompt reframes goal + acceptance_criteria semantics.
        self.assertIn("boundary/verdict", system)
        self.assertIn("VERIFICATION", system)
        self.assertIn("Do NOT propose an implementation", system)

    def test_default_shape_is_engineering(self):
        system_default, _u1 = bsg._build_spec_prompt(
            bullet_text="x",
            section_title="s",
            anchor_path="p",
            citations=self.CITATIONS,
        )
        system_eng, _u2 = bsg._build_spec_prompt(
            bullet_text="x",
            section_title="s",
            anchor_path="p",
            citations=self.CITATIONS,
            prompt_shape=bsg.PROMPT_SHAPE_ENGINEERING,
        )
        self.assertEqual(system_default, system_eng)


class GenerateSpecBodyExtrasTests(TestCase):
    """generate_spec_body threads finding_type through to extras + prompt selection."""

    SPEC_JSON = json.dumps({
        "goal": "Record that the frontend HTTP surface has visibility gaps.",
        "context": "Boundary evidence from S2404 audit.",
        "open_question": "None",
        "files_implicated": [
            {"path": "docs/example.md", "source": "citation"},
        ],
        "acceptance_criteria": [
            "Re-audit visibility coverage at next release.",
            "Confirm token-attach coverage still <100%.",
            "Confirm bypass-path list has not grown.",
        ],
    })

    def _run(self, finding_type):
        captured = {}

        def fake_llm(system, user, model):
            captured["system"] = system
            captured["user"] = user
            return self.SPEC_JSON

        with patch.object(bsg, "_call_spec_llm", side_effect=fake_llm):
            body, extras = bsg.generate_spec_body(
                bullet_text="Zero visibility into 9.8% of frontend HTTP surface.",
                section_key="boundary_violations",
                section_title="Boundary Violations",
                anchor_path="docs/example.md",
                citations=[{"path": "docs/example.md", "snippet": "example"}],
                finding_type=finding_type,
            )
        return body, extras, captured

    def test_decision_evidence_sets_evidence_shape_in_extras(self):
        _body, extras, captured = self._run("decision_evidence")
        self.assertEqual(extras["spec_prompt_shape"], bsg.PROMPT_SHAPE_EVIDENCE)
        self.assertEqual(extras["finding_type_used"], "decision_evidence")
        # System prompt actually differs.
        self.assertIn("decision-evidence record", captured["system"])

    def test_executable_uses_engineering_shape(self):
        _body, extras, captured = self._run("executable")
        self.assertEqual(extras["spec_prompt_shape"], bsg.PROMPT_SHAPE_ENGINEERING)
        self.assertEqual(extras["finding_type_used"], "executable")
        self.assertIn("code-writing AI agent", captured["system"])

    def test_unknown_uses_engineering_shape(self):
        _body, extras, captured = self._run("unknown")
        self.assertEqual(extras["spec_prompt_shape"], bsg.PROMPT_SHAPE_ENGINEERING)
        self.assertEqual(extras["finding_type_used"], "unknown")

    def test_none_finding_type_defaults_to_engineering(self):
        _body, extras, captured = self._run(None)
        self.assertEqual(extras["spec_prompt_shape"], bsg.PROMPT_SHAPE_ENGINEERING)
        self.assertIsNone(extras["finding_type_used"])

    def test_extras_still_carry_schema_and_model(self):
        _body, extras, _c = self._run("decision_evidence")
        self.assertEqual(extras["spec_schema_version"], "SPEC_V1")
        self.assertTrue(extras["llm_success"])
        self.assertIn("spec_model", extras)


class FailOpenPlaceholderTests(TestCase):
    """LLM failures swap placeholder copy per prompt shape."""

    def test_evidence_shape_placeholder_says_evidence(self):
        with patch.object(bsg, "_call_spec_llm", side_effect=RuntimeError("boom")):
            body, extras = bsg.generate_spec_body(
                bullet_text="Boundary bullet",
                section_key="k",
                section_title="t",
                anchor_path="a",
                citations=[],
                finding_type="decision_evidence",
            )
        self.assertFalse(extras["llm_success"])
        self.assertEqual(extras["spec_prompt_shape"], bsg.PROMPT_SHAPE_EVIDENCE)
        self.assertIn("evidence capture failed", body)
        self.assertIn("verification steps manually", body)

    def test_engineering_shape_placeholder_says_spec(self):
        with patch.object(bsg, "_call_spec_llm", side_effect=RuntimeError("boom")):
            body, extras = bsg.generate_spec_body(
                bullet_text="Engineering bullet",
                section_key="k",
                section_title="t",
                anchor_path="a",
                citations=[],
                finding_type="executable",
            )
        self.assertFalse(extras["llm_success"])
        self.assertEqual(extras["spec_prompt_shape"], bsg.PROMPT_SHAPE_ENGINEERING)
        self.assertIn("spec generation failed", body)
        self.assertIn("acceptance criteria manually", body)


class SendToRigbyViewForwardsFindingTypeTests(TestCase):
    """The send-to-rigby view passes finding.finding_type to generate_spec_body."""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="s2993_tester", password="pw", email="s2993@test.local"
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

    def _make_finding(self, finding_type):
        return DocResearchFinding.objects.create(
            source_type="research_bullet",
            source_heading="Boundary Violations",
            doc_path="docs/example.md",
            domain_slug="auth",
            text=f"Test bullet for {finding_type}",
            text_hash=f"hash-{finding_type}-{timezone.now().timestamp()}"[:64],
            confidence="high",
            status=DocResearchFinding.STATUS_OPEN,
            finding_type=finding_type,
        )

    def _post(self, finding_id):
        return self.client.post(
            f"/api/repo/doc-research-findings/{finding_id}/send-to-rigby/",
        )

    def _stub_llm(self):
        return json.dumps({
            "goal": "Test goal",
            "context": "Test context",
            "open_question": "None",
            "files_implicated": [
                {"path": "docs/example.md", "source": "citation"},
            ],
            "acceptance_criteria": [
                "AC 1.",
                "AC 2.",
                "AC 3.",
            ],
        })

    def test_decision_evidence_finding_uses_evidence_prompt(self):
        finding = self._make_finding(
            DocResearchFinding.FINDING_TYPE_DECISION_EVIDENCE
        )
        with patch.object(bsg, "_call_spec_llm", return_value=self._stub_llm()):
            resp = self._post(finding.id)
        self.assertEqual(resp.status_code, 201, resp.content[:400])
        d = Deliverable.objects.get(id=resp.json()["deliverable_id"])
        self.assertEqual(d.metadata.get("spec_prompt_shape"), bsg.PROMPT_SHAPE_EVIDENCE)
        self.assertEqual(d.metadata.get("finding_type_used"), "decision_evidence")

    def test_executable_finding_uses_engineering_prompt(self):
        finding = self._make_finding(DocResearchFinding.FINDING_TYPE_EXECUTABLE)
        with patch.object(bsg, "_call_spec_llm", return_value=self._stub_llm()):
            resp = self._post(finding.id)
        self.assertEqual(resp.status_code, 201, resp.content[:400])
        d = Deliverable.objects.get(id=resp.json()["deliverable_id"])
        self.assertEqual(
            d.metadata.get("spec_prompt_shape"), bsg.PROMPT_SHAPE_ENGINEERING
        )
        self.assertEqual(d.metadata.get("finding_type_used"), "executable")

    def test_unknown_finding_uses_engineering_prompt(self):
        finding = self._make_finding(DocResearchFinding.FINDING_TYPE_UNKNOWN)
        with patch.object(bsg, "_call_spec_llm", return_value=self._stub_llm()):
            resp = self._post(finding.id)
        self.assertEqual(resp.status_code, 201, resp.content[:400])
        d = Deliverable.objects.get(id=resp.json()["deliverable_id"])
        self.assertEqual(
            d.metadata.get("spec_prompt_shape"), bsg.PROMPT_SHAPE_ENGINEERING
        )
        self.assertEqual(d.metadata.get("finding_type_used"), "unknown")
