"""Session 2992 — finding_type classifier at ingest (v2 item #2).

Three orthogonal axes now on DocResearchFinding:
- status (lifecycle: open/fixed/dismissed) — S2989
- close_mode (closure mechanism, nullable) — S2991
- finding_type (classification: decision_evidence/executable/unknown) — S2992

Classifier is a deterministic regex over (text, source_heading) applied at
ingest via `_classify_finding_type` in `index_doc_research_findings`.
Precedence: decision_evidence beats executable on collision (per Rigby T1
SIGN framing fold — a decision record that cites a file:line is still
primarily a decision record).

Existing 900 rows default to `unknown` via schema default (migration
0400). Reclassification of the existing corpus is a separate step:
`python manage.py index_doc_research_findings --reclassify-existing`
(dry-run) then `--reclassify-existing --apply` (persist).
"""
from __future__ import annotations

from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from core.management.commands.index_doc_research_findings import (
    _classify_finding_type,
)
from core.models_audit_findings import DocResearchFinding
from core.services.tool_dispatcher import get_tool_dispatcher


def _run(payload):
    dispatcher = get_tool_dispatcher()
    handler = dispatcher._tool_handlers["orm_inspect_tool"]
    return handler(
        tool_name="orm_inspect_tool",
        payload=payload,
        user_id=None,
        trace_id="test-s2992-trace",
    )


class ClassifierUnitTests(TestCase):
    """_classify_finding_type is deterministic over (text, source_heading)."""

    def test_default_is_unknown(self):
        self.assertEqual(
            _classify_finding_type("random observation without signals", ""),
            DocResearchFinding.FINDING_TYPE_UNKNOWN,
        )

    def test_cat_a_matches_decision_evidence(self):
        for text in (
            "Cat A boundary decision to preserve tool split",
            "Category A framing per Chris",
            "This is a cat a level concern",
        ):
            self.assertEqual(
                _classify_finding_type(text, ""),
                DocResearchFinding.FINDING_TYPE_DECISION_EVIDENCE,
                msg=text,
            )

    def test_boundary_observation_matches_decision_evidence(self):
        self.assertEqual(
            _classify_finding_type("Boundary observation on the auth surface", ""),
            DocResearchFinding.FINDING_TYPE_DECISION_EVIDENCE,
        )

    def test_boundary_violation_matches_decision_evidence(self):
        self.assertEqual(
            _classify_finding_type("boundary violations noted", ""),
            DocResearchFinding.FINDING_TYPE_DECISION_EVIDENCE,
        )

    def test_xx99_reference_matches_decision_evidence(self):
        self.assertEqual(
            _classify_finding_type("See xx99 canonical summary for context", ""),
            DocResearchFinding.FINDING_TYPE_DECISION_EVIDENCE,
        )

    def test_d_verdict_matches_decision_evidence(self):
        self.assertEqual(
            _classify_finding_type("Chris D-verdict pending", ""),
            DocResearchFinding.FINDING_TYPE_DECISION_EVIDENCE,
        )

    def test_boundary_violations_heading_matches_decision_evidence(self):
        self.assertEqual(
            _classify_finding_type("some bullet with no strong text signal", "Boundary Violations"),
            DocResearchFinding.FINDING_TYPE_DECISION_EVIDENCE,
        )

    def test_file_line_matches_executable(self):
        for text in (
            "See td_handlers_agents.py:868 for the guardrail",
            "Fix at core/models_audit_findings.py:126",
            "See frontend/src/App.tsx:42 for the router",
        ):
            self.assertEqual(
                _classify_finding_type(text, ""),
                DocResearchFinding.FINDING_TYPE_EXECUTABLE,
                msg=text,
            )

    def test_imperative_verbs_match_executable(self):
        for text in (
            "Rename the confusing helper",
            "Delete dead code path",
            "Add missing test coverage",
            "Implement the fallback",
            "Wire up the missing signal",
            "Fix the flaky retry",
            "Refactor duplicate helpers",
            "Migrate the noisy row",
            "Bump the wrapper pin",
            "Backfill the null rows",
        ):
            self.assertEqual(
                _classify_finding_type(text, ""),
                DocResearchFinding.FINDING_TYPE_EXECUTABLE,
                msg=text,
            )

    def test_next_actions_heading_matches_executable(self):
        self.assertEqual(
            _classify_finding_type("a plain observation", "Next Actions"),
            DocResearchFinding.FINDING_TYPE_EXECUTABLE,
        )

    def test_decision_evidence_wins_over_executable_on_collision(self):
        # Real corpus pattern: a Cat A boundary observation that also cites
        # a file:line pointer as evidence. Should classify as
        # decision_evidence, not executable.
        text = "Cat A boundary observation: see td_handlers_agents.py:868"
        self.assertEqual(
            _classify_finding_type(text, "Recommended Future Research"),
            DocResearchFinding.FINDING_TYPE_DECISION_EVIDENCE,
        )

    def test_empty_text_and_heading_are_safe(self):
        self.assertEqual(
            _classify_finding_type("", ""),
            DocResearchFinding.FINDING_TYPE_UNKNOWN,
        )


class ModelFieldTests(TestCase):
    """finding_type field defaults + choices."""

    def test_finding_type_defaults_to_unknown(self):
        f = DocResearchFinding.objects.create(
            doc_path="docs/research/x.md",
            text_hash="hash-default",
            text="no signal",
        )
        self.assertEqual(f.finding_type, DocResearchFinding.FINDING_TYPE_UNKNOWN)

    def test_finding_type_choices_are_three_values(self):
        values = {c[0] for c in DocResearchFinding.FINDING_TYPE_CHOICES}
        self.assertEqual(
            values, {"decision_evidence", "executable", "unknown"}
        )

    def test_finding_type_accepts_all_three_values(self):
        for ft in ("decision_evidence", "executable", "unknown"):
            f = DocResearchFinding.objects.create(
                doc_path=f"docs/research/{ft}.md",
                text_hash=f"hash-{ft}",
                text="bullet",
                finding_type=ft,
            )
            self.assertEqual(f.finding_type, ft)


class ReclassifyExistingCommandTests(TestCase):
    """`index_doc_research_findings --reclassify-existing` dry-run vs --apply."""

    def setUp(self):
        # Seed 4 rows with mixed classifications and stale finding_type.
        self.decision_row = DocResearchFinding.objects.create(
            doc_path="docs/research/a.md",
            text_hash="h-a",
            text="Cat A boundary observation on X",
            finding_type=DocResearchFinding.FINDING_TYPE_UNKNOWN,
        )
        self.executable_row = DocResearchFinding.objects.create(
            doc_path="docs/research/b.md",
            text_hash="h-b",
            text="Refactor td_handlers_agents.py:868",
            finding_type=DocResearchFinding.FINDING_TYPE_UNKNOWN,
        )
        self.unknown_row = DocResearchFinding.objects.create(
            doc_path="docs/research/c.md",
            text_hash="h-c",
            text="A quiet observation with no strong signal words at all",
            finding_type=DocResearchFinding.FINDING_TYPE_UNKNOWN,
        )
        # Already-classified row that should NOT flip (idempotent).
        self.stable_row = DocResearchFinding.objects.create(
            doc_path="docs/research/d.md",
            text_hash="h-d",
            text="Cat A boundary observation on Y",
            finding_type=DocResearchFinding.FINDING_TYPE_DECISION_EVIDENCE,
        )

    def _call(self, *, apply_writes: bool) -> str:
        out = StringIO()
        args = ["--reclassify-existing"]
        if apply_writes:
            args.append("--apply")
        call_command("index_doc_research_findings", *args, stdout=out)
        return out.getvalue()

    def test_dry_run_prints_distribution_and_does_not_write(self):
        output = self._call(apply_writes=False)
        self.assertIn("Total rows: 4", output)
        self.assertIn("decision_evidence", output)
        self.assertIn("executable", output)
        self.assertIn("(dry-run", output)
        # 2 rows would flip: decision_row + executable_row (both start unknown).
        self.assertIn("Rows that would change: 2", output)
        # No writes.
        self.decision_row.refresh_from_db()
        self.executable_row.refresh_from_db()
        self.assertEqual(
            self.decision_row.finding_type, DocResearchFinding.FINDING_TYPE_UNKNOWN
        )
        self.assertEqual(
            self.executable_row.finding_type, DocResearchFinding.FINDING_TYPE_UNKNOWN
        )

    def test_apply_persists_reclassification(self):
        output = self._call(apply_writes=True)
        self.assertIn("Applied: 2 row(s) updated", output)
        self.decision_row.refresh_from_db()
        self.executable_row.refresh_from_db()
        self.unknown_row.refresh_from_db()
        self.stable_row.refresh_from_db()
        self.assertEqual(
            self.decision_row.finding_type,
            DocResearchFinding.FINDING_TYPE_DECISION_EVIDENCE,
        )
        self.assertEqual(
            self.executable_row.finding_type,
            DocResearchFinding.FINDING_TYPE_EXECUTABLE,
        )
        self.assertEqual(
            self.unknown_row.finding_type,
            DocResearchFinding.FINDING_TYPE_UNKNOWN,
        )
        # Already-classified row untouched.
        self.assertEqual(
            self.stable_row.finding_type,
            DocResearchFinding.FINDING_TYPE_DECISION_EVIDENCE,
        )


class OrmInspectFindingTypeTests(TestCase):
    """count_by(finding_type) via orm_inspect_tool works for the new field."""

    def setUp(self):
        DocResearchFinding.objects.create(
            doc_path="docs/research/e.md", text_hash="h-e", text="e",
            finding_type=DocResearchFinding.FINDING_TYPE_DECISION_EVIDENCE,
        )
        DocResearchFinding.objects.create(
            doc_path="docs/research/f.md", text_hash="h-f", text="f",
            finding_type=DocResearchFinding.FINDING_TYPE_EXECUTABLE,
        )
        DocResearchFinding.objects.create(
            doc_path="docs/research/g.md", text_hash="h-g", text="g",
            finding_type=DocResearchFinding.FINDING_TYPE_EXECUTABLE,
        )
        DocResearchFinding.objects.create(
            doc_path="docs/research/h.md", text_hash="h-h", text="h",
        )  # defaults to unknown

    def test_describe_model_surfaces_finding_type(self):
        result = _run({"action": "describe_model", "model": "DocResearchFinding"})
        self.assertTrue(result["ok"], msg=result)
        field_names = {f["name"] for f in result["fields"]}
        self.assertIn("finding_type", field_names)

    def test_count_by_finding_type(self):
        result = _run({
            "action": "count_by",
            "model": "DocResearchFinding",
            "field": "finding_type",
        })
        self.assertTrue(result["ok"], msg=result)
        by_type = {g["value"]: g["count"] for g in result["groups"]}
        self.assertEqual(by_type.get("decision_evidence"), 1)
        self.assertEqual(by_type.get("executable"), 2)
        self.assertEqual(by_type.get("unknown"), 1)

    def test_filter_by_finding_type(self):
        result = _run({
            "action": "filter",
            "model": "DocResearchFinding",
            "filter_kwargs": {"finding_type": "executable"},
            "limit": 10,
        })
        self.assertTrue(result["ok"], msg=result)
        self.assertEqual(result["total_matching"], 2)


class SerializerAndListFilterTests(TestCase):
    """Serializer surfaces finding_type; list endpoint accepts filter."""

    def test_serializer_includes_finding_type(self):
        from core.views_doc_research_findings import _serialize_finding

        f = DocResearchFinding.objects.create(
            doc_path="docs/research/i.md", text_hash="h-i", text="i",
            finding_type=DocResearchFinding.FINDING_TYPE_DECISION_EVIDENCE,
        )
        payload = _serialize_finding(f)
        self.assertEqual(payload["finding_type"], "decision_evidence")
