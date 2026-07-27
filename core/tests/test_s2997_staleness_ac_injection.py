"""Session 2997 — stale-ref AC injection at spec generation (v2 item #8).

When a finding has `staleness=suspected` (per S2995), sending it to
Rigby now produces a spec deliverable with:
1. A system-prompt hint telling the LLM the finding's refs are suspect
2. Deterministically-prepended verification ACs (one per failed ref)
3. A "Staleness note" section in the rendered markdown
4. `staleness_failed_refs_injected: True` in extras metadata

Belt-and-suspenders (Rigby T1 SIGN Ask #2): LLM hint alone risks silent
dedupe; deterministic prepend alone loses narrative integration. Both.

Wording differs per prompt_shape (Rigby T1 SIGN Ask #3(a)):
- engineering (executable/unknown) — "supports the claim"
- evidence (decision_evidence) — "supports the evidence assertion"
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


class StalenessACTemplateTests(TestCase):
    """_staleness_ac_for picks wording per prompt shape."""

    def test_engineering_shape_uses_claim_wording(self):
        ac = bsg._staleness_ac_for(
            "core/foo.py:12", bsg.PROMPT_SHAPE_ENGINEERING
        )
        self.assertIn("`core/foo.py:12`", ac)
        self.assertIn("supports the claim", ac)
        self.assertNotIn("evidence assertion", ac)

    def test_evidence_shape_uses_evidence_wording(self):
        ac = bsg._staleness_ac_for(
            "docs/audit.md:99", bsg.PROMPT_SHAPE_EVIDENCE
        )
        self.assertIn("`docs/audit.md:99`", ac)
        self.assertIn("evidence assertion", ac)
        self.assertNotIn("supports the claim", ac)


class StalenessPromptHintTests(TestCase):
    """_staleness_prompt_hint produces the LLM system-prompt addendum."""

    def test_hint_lists_refs_and_directs_verification(self):
        hint = bsg._staleness_prompt_hint(["a.py:1", "b.py:2"])
        self.assertIn("STALENESS NOTE", hint)
        self.assertIn("`a.py:1`", hint)
        self.assertIn("`b.py:2`", hint)
        self.assertIn("verification steps", hint)

    def test_hint_caps_at_8_refs(self):
        many = [f"path{i}.py:1" for i in range(20)]
        hint = bsg._staleness_prompt_hint(many)
        # Only the first 8 refs should appear.
        for ref in many[:8]:
            self.assertIn(f"`{ref}`", hint)
        for ref in many[8:]:
            self.assertNotIn(f"`{ref}`", hint)


class InjectStalenessACsTests(TestCase):
    """_inject_staleness_acs prepends + dedupes + caps."""

    def _spec(self, acs):
        return bsg.BriefingSpec(
            goal="g", context="c", open_question="None",
            files_implicated=[], acceptance_criteria=acs, warnings=[],
        )

    def test_no_refs_is_noop(self):
        spec = self._spec(["AC1", "AC2"])
        result = bsg._inject_staleness_acs(spec, [], bsg.PROMPT_SHAPE_ENGINEERING)
        self.assertEqual(result.acceptance_criteria, ["AC1", "AC2"])

    def test_prepends_one_per_failed_ref(self):
        spec = self._spec(["AC1", "AC2"])
        result = bsg._inject_staleness_acs(
            spec, ["foo.py:1", "bar.py:2"], bsg.PROMPT_SHAPE_ENGINEERING
        )
        self.assertEqual(len(result.acceptance_criteria), 4)
        self.assertIn("`foo.py:1`", result.acceptance_criteria[0])
        self.assertIn("`bar.py:2`", result.acceptance_criteria[1])
        self.assertEqual(result.acceptance_criteria[2], "AC1")
        self.assertEqual(result.acceptance_criteria[3], "AC2")

    def test_dedupes_exact_match_against_llm_output(self):
        # Simulate the LLM having taken the prompt hint and produced the
        # same AC we would prepend. We should not double it up.
        injected_ac = bsg._staleness_ac_for(
            "foo.py:1", bsg.PROMPT_SHAPE_ENGINEERING
        )
        spec = self._spec([injected_ac, "AC2"])
        result = bsg._inject_staleness_acs(
            spec, ["foo.py:1"], bsg.PROMPT_SHAPE_ENGINEERING
        )
        self.assertEqual(len(result.acceptance_criteria), 2)
        self.assertEqual(result.acceptance_criteria[0], injected_ac)
        self.assertEqual(result.acceptance_criteria[1], "AC2")

    def test_caps_at_max_acceptance_criteria(self):
        # 6 existing + 4 injected = 10; cap at MAX_ACCEPTANCE_CRITERIA (8)
        spec = self._spec([f"AC{i}" for i in range(6)])
        result = bsg._inject_staleness_acs(
            spec,
            [f"path{i}.py:1" for i in range(4)],
            bsg.PROMPT_SHAPE_ENGINEERING,
        )
        self.assertEqual(len(result.acceptance_criteria), bsg.MAX_ACCEPTANCE_CRITERIA)
        # Prepended (injected) ACs win; later original ACs get pushed out.
        self.assertTrue(
            all("`path" in a for a in result.acceptance_criteria[:4])
        )


class GenerateSpecBodyWithStalenessTests(TestCase):
    """generate_spec_body integrates staleness end-to-end."""

    SPEC_JSON = json.dumps({
        "goal": "Some engineering goal",
        "context": "context",
        "open_question": "None",
        "files_implicated": [],
        "acceptance_criteria": ["Existing AC 1.", "Existing AC 2.", "Existing AC 3."],
    })

    def _run(self, staleness_failed_refs=None, finding_type=None):
        captured = {}

        def fake_llm(system, user, model):
            captured["system"] = system
            captured["user"] = user
            return self.SPEC_JSON

        with patch.object(bsg, "_call_spec_llm", side_effect=fake_llm):
            body, extras = bsg.generate_spec_body(
                bullet_text="Test bullet",
                section_key="k",
                section_title="t",
                anchor_path="docs/x.md",
                citations=[{"path": "docs/x.md", "snippet": "example"}],
                finding_type=finding_type,
                staleness_failed_refs=staleness_failed_refs,
            )
        return body, extras, captured

    def test_no_refs_no_injection(self):
        body, extras, captured = self._run()
        self.assertFalse(extras["staleness_failed_refs_injected"])
        self.assertNotIn("STALENESS NOTE", captured["system"])
        self.assertNotIn("Staleness note", body)

    def test_engineering_finding_with_refs_injects_all(self):
        body, extras, captured = self._run(
            staleness_failed_refs=["executor/models.py:271"],
            finding_type="executable",
        )
        # Extras flag flipped
        self.assertTrue(extras["staleness_failed_refs_injected"])
        # LLM prompt hint present
        self.assertIn("STALENESS NOTE", captured["system"])
        self.assertIn("`executor/models.py:271`", captured["system"])
        # Rendered markdown carries a Staleness note section
        self.assertIn("## Staleness note", body)
        self.assertIn("`executor/models.py:271`", body)
        # AC prepended
        self.assertIn(
            "Open `executor/models.py:271` at HEAD and confirm it supports the claim",
            body,
        )

    def test_decision_evidence_uses_evidence_wording_in_ac(self):
        body, extras, _ = self._run(
            staleness_failed_refs=["docs/audit.md:99"],
            finding_type="decision_evidence",
        )
        self.assertTrue(extras["staleness_failed_refs_injected"])
        self.assertEqual(extras["spec_prompt_shape"], bsg.PROMPT_SHAPE_EVIDENCE)
        self.assertIn("evidence assertion", body)
        self.assertNotIn("supports the claim", body)

    def test_empty_ref_list_treated_as_no_refs(self):
        _body, extras, captured = self._run(staleness_failed_refs=[])
        self.assertFalse(extras["staleness_failed_refs_injected"])
        self.assertNotIn("STALENESS NOTE", captured["system"])

    def test_non_string_refs_filtered(self):
        # Defensive: metadata might contain garbage from a manual write.
        _body, extras, captured = self._run(
            staleness_failed_refs=["good.py:1", None, "", "  ", 42]
        )
        self.assertTrue(extras["staleness_failed_refs_injected"])
        self.assertIn("`good.py:1`", captured["system"])
        # The others should be silently dropped, not raise.

    def test_fail_open_still_gets_injection(self):
        # LLM failure → placeholder spec — should STILL get the
        # staleness note in markdown + injection in extras so the
        # downstream reader knows the finding is suspect.
        with patch.object(bsg, "_call_spec_llm", side_effect=RuntimeError("boom")):
            body, extras = bsg.generate_spec_body(
                bullet_text="Test bullet",
                section_key="k",
                section_title="t",
                anchor_path="docs/x.md",
                citations=[],
                finding_type="executable",
                staleness_failed_refs=["foo.py:1"],
            )
        self.assertFalse(extras["llm_success"])
        self.assertTrue(extras["staleness_failed_refs_injected"])
        self.assertIn("## Staleness note", body)
        self.assertIn("`foo.py:1`", body)


class SendToRigbyViewForwardsStalenessTests(TestCase):
    """The send-to-rigby view passes finding.metadata.staleness_failed_refs when suspected."""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="s2997_tester", password="pw", email="s2997@test.local"
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

    def _make_finding(self, *, staleness, failed_refs=None):
        metadata = {}
        if failed_refs:
            metadata["staleness_failed_refs"] = failed_refs
        return DocResearchFinding.objects.create(
            source_type="audit",
            source_heading="Executable Actions",
            doc_path="docs/x.md",
            domain_slug="test",
            text=f"Test bullet with staleness={staleness}",
            text_hash=f"h-{staleness}-{timezone.now().timestamp()}"[:64],
            confidence="high",
            status=DocResearchFinding.STATUS_OPEN,
            finding_type=DocResearchFinding.FINDING_TYPE_EXECUTABLE,
            staleness=staleness,
            metadata=metadata,
        )

    def _stub_llm(self):
        return json.dumps({
            "goal": "Test goal",
            "context": "Test context",
            "open_question": "None",
            "files_implicated": [],
            "acceptance_criteria": ["AC1.", "AC2.", "AC3."],
        })

    def _post(self, finding_id):
        return self.client.post(
            f"/api/repo/doc-research-findings/{finding_id}/send-to-rigby/",
        )

    def test_suspected_finding_gets_ac_injection(self):
        finding = self._make_finding(
            staleness=DocResearchFinding.STALENESS_SUSPECTED,
            failed_refs=["executor/models.py:271"],
        )
        with patch.object(bsg, "_call_spec_llm", return_value=self._stub_llm()):
            resp = self._post(finding.id)
        self.assertEqual(resp.status_code, 201, resp.content[:400])
        d = Deliverable.objects.get(id=resp.json()["deliverable_id"])
        self.assertTrue(d.metadata.get("staleness_failed_refs_injected"))
        # Deliverable body contains the injection.
        self.assertIn("## Staleness note", d.content)
        self.assertIn("`executor/models.py:271`", d.content)
        self.assertIn(
            "Open `executor/models.py:271` at HEAD and confirm",
            d.content,
        )

    def test_fresh_finding_no_injection(self):
        finding = self._make_finding(
            staleness=DocResearchFinding.STALENESS_FRESH,
            failed_refs=None,
        )
        with patch.object(bsg, "_call_spec_llm", return_value=self._stub_llm()):
            resp = self._post(finding.id)
        self.assertEqual(resp.status_code, 201, resp.content[:400])
        d = Deliverable.objects.get(id=resp.json()["deliverable_id"])
        self.assertFalse(d.metadata.get("staleness_failed_refs_injected"))
        self.assertNotIn("## Staleness note", d.content)

    def test_suspected_finding_but_empty_metadata_list_no_injection(self):
        # Defensive: staleness=suspected but metadata was cleared/garbled.
        # Don't crash; treat as no refs.
        finding = self._make_finding(
            staleness=DocResearchFinding.STALENESS_SUSPECTED,
            failed_refs=[],  # empty list stored explicitly
        )
        with patch.object(bsg, "_call_spec_llm", return_value=self._stub_llm()):
            resp = self._post(finding.id)
        self.assertEqual(resp.status_code, 201, resp.content[:400])
        d = Deliverable.objects.get(id=resp.json()["deliverable_id"])
        self.assertFalse(d.metadata.get("staleness_failed_refs_injected"))
