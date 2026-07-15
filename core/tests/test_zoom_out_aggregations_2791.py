"""S2791 — Sign Ledger drill-down aggregations contract.

Locks four contracts for the opt-in ``include=aggregations`` extension to
``GET /api/governance/zoom-out-ledger/`` (feeds the Chris-facing Sign
Ledger drill-down UI shipped this session):

  1. **Aggregations shape** — when ``include=aggregations`` is passed,
     response embeds an ``aggregations`` dict with
     ``top_arcs_by_count`` (descending), ``future_trigger_rule_targets``
     (regex-parsed ``PLAYBOOK-\\d+\\.\\d+(\\.\\d+)?`` mentions on
     ``future_trigger`` rows only), and ``sessions_covered`` (sorted).

  2. **Advisory preservation** — ``is_gate: false`` +
     ``semantics: "advisory_pattern_evidence"`` survive on the outer
     response AND inside the aggregations block. Explicit guardrail
     against the S2791 T1 SIGN row 50 (``future_trigger``) fold:
     "aggregation semantics drift risk — richer ledger UI accretes
     gate-y feel." If a downstream consumer ever treats aggregation
     output as gate input, THIS TEST catches the contract break.

  3. **Backward compatibility** — no ``include`` param → response is
     byte-for-byte the S2780 contract (no ``aggregations`` key). Existing
     ``test_zoom_out_tool_2780`` assertions remain intact.

  4. **View-layer allowlist** — the ``include`` param is now allowed at
     ``/api/governance/zoom-out-ledger/`` (was rejected as unknown
     pre-S2791); genuinely unknown params still 400. Row 48
     (``same_pr_actionable``) fold: without allowlist add,
     ``?include=aggregations`` 400s before payload build.

Ratified: S2791 T1 Rigby joint SIGN — 3 folds persisted before D-verdict
per PLAYBOOK-6.10.8/9 (ledger rows 48 + 49 + 50, arc
``sign_ledger_drilldown_s2791``); Chris D-verdict "yes build it".
"""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, SimpleTestCase, TestCase

from core.services.td_handlers_governance import GovernanceHandlersMixin


class _StubHandler:
    pass


class _ZoomOutToolHandler(GovernanceHandlersMixin, _StubHandler):
    pass


# Row fixtures span 3 arcs across 4 sessions with 2 future_trigger rows
# mentioning distinct PLAYBOOK rules — enough to exercise every
# aggregation dimension without over-fitting to specific counts.
_SAMPLE_ROWS = [
    {
        "ts": "2026-07-15T00:00:00+00:00",
        "schema_version": 1,
        "session": 2787,
        "arc": "csrf_exempt_cross_file_cleanup",
        "classification": "same_pr_actionable",
        "concern_text": (
            "Ship-shape convergence. Mentions PLAYBOOK-6.10.7 for context "
            "but is NOT a future_trigger row — must not appear in "
            "rule_targets aggregation."
        ),
        "evidence_ref": "PR#3189",
        "backfilled": False,
        "entered_by": "claude",
    },
    {
        "ts": "2026-07-15T00:01:00+00:00",
        "schema_version": 1,
        "session": 2789,
        "arc": "broader_public_paths_audit",
        "classification": "future_trigger",
        "concern_text": (
            "PUBLIC_PATHS wrong-pattern — 263 entries need opt-in decorator. "
            "Trigger: PLAYBOOK-6.10.10 codification candidate."
        ),
        "evidence_ref": "PR#3191",
        "backfilled": False,
        "entered_by": "claude",
    },
    {
        "ts": "2026-07-15T00:02:00+00:00",
        "schema_version": 1,
        "session": 2790,
        "arc": "per_prefix_authz_sweep_shape",
        "classification": "future_trigger",
        "concern_text": (
            "Pattern stabilizing as 'one prefix + regression test file + "
            "audit doc update'. PLAYBOOK-6.10.11 candidate for codifying "
            "'per-prefix authZ sweep' execution unit."
        ),
        "evidence_ref": "S2790_T1_SIGN",
        "backfilled": False,
        "entered_by": "claude",
    },
    {
        "ts": "2026-07-15T00:03:00+00:00",
        "schema_version": 1,
        "session": 2791,
        "arc": "sign_ledger_drilldown_s2791",
        "classification": "same_pr_mitigatable",
        "concern_text": (
            "No shadcn Dialog primitive — reuse ConversationDetailModal "
            "overlay pattern."
        ),
        "evidence_ref": "S2791_T1_SIGN#fold2",
        "backfilled": False,
        "entered_by": "claude",
    },
    {
        "ts": "2026-07-15T00:04:00+00:00",
        "schema_version": 1,
        "session": 2791,
        "arc": "sign_ledger_drilldown_s2791",
        "classification": "future_trigger",
        "concern_text": (
            "Aggregation semantics drift risk — richer ledger UI accretes "
            "gate-y feel. PLAYBOOK-6.10.11 escalation candidate if drift "
            "observed."
        ),
        "evidence_ref": "S2791_T1_SIGN#fold3",
        "backfilled": False,
        "entered_by": "claude",
    },
]


class ZoomOutAggregationsShapeTest(SimpleTestCase):
    """Contract 1 — aggregations shape when include=aggregations."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        (self.tmpdir / "logs").mkdir()
        path = self.tmpdir / "logs" / "zoom_out_classifications.jsonl"
        path.write_text("\n".join(json.dumps(r) for r in _SAMPLE_ROWS) + "\n")
        self.handler = _ZoomOutToolHandler()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _list(self, payload=None):
        base = {"action": "list"}
        if payload:
            base.update(payload)
        with patch("django.conf.settings.BASE_DIR", str(self.tmpdir)):
            return self.handler._handle_zoom_out(
                "zoom_out_tool", base, user_id=None, trace_id="trace-test"
            )

    def test_include_aggregations_adds_aggregations_key(self):
        result = self._list({"include": "aggregations"})
        self.assertIn("aggregations", result)

    def test_top_arcs_by_count_descending(self):
        result = self._list({"include": "aggregations"})
        arcs = result["aggregations"]["top_arcs_by_count"]
        # sign_ledger_drilldown_s2791 appears twice; the other three arcs
        # once each. Descending by count.
        self.assertEqual(arcs[0]["arc"], "sign_ledger_drilldown_s2791")
        self.assertEqual(arcs[0]["count"], 2)
        counts = [entry["count"] for entry in arcs]
        self.assertEqual(counts, sorted(counts, reverse=True))
        # Every arc across the fixture rows appears exactly once in the
        # aggregation — no over-count or omission.
        arc_names = {entry["arc"] for entry in arcs}
        self.assertEqual(
            arc_names,
            {
                "csrf_exempt_cross_file_cleanup",
                "broader_public_paths_audit",
                "per_prefix_authz_sweep_shape",
                "sign_ledger_drilldown_s2791",
            },
        )

    def test_rule_targets_only_parsed_from_future_trigger_rows(self):
        result = self._list({"include": "aggregations"})
        targets = result["aggregations"]["future_trigger_rule_targets"]
        rule_ids = {entry["rule_id"] for entry in targets}
        # PLAYBOOK-6.10.7 mentioned in a same_pr_actionable row → must
        # NOT appear (aggregation is future_trigger-scoped by design).
        self.assertNotIn("PLAYBOOK-6.10.7", rule_ids)
        # Both future_trigger-scoped rules present, case-normalized upper.
        self.assertIn("PLAYBOOK-6.10.10", rule_ids)
        self.assertIn("PLAYBOOK-6.10.11", rule_ids)
        # 6.10.11 appears in two distinct future_trigger rows.
        by_id = {e["rule_id"]: e["count"] for e in targets}
        self.assertEqual(by_id["PLAYBOOK-6.10.11"], 2)
        self.assertEqual(by_id["PLAYBOOK-6.10.10"], 1)

    def test_sessions_covered_sorted_distinct(self):
        result = self._list({"include": "aggregations"})
        sessions = result["aggregations"]["sessions_covered"]
        self.assertEqual(sessions, [2787, 2789, 2790, 2791])

    def test_aggregations_computed_over_all_rows_not_filter_window(self):
        # arc filter narrows items but aggregations should still span
        # the full ledger (this is the guarantee the UI chips depend on
        # so counts don't collapse to zero after clicking a chip).
        result = self._list({
            "include": "aggregations",
            "arc": "sign_ledger_drilldown_s2791",
        })
        arcs = result["aggregations"]["top_arcs_by_count"]
        arc_names = {entry["arc"] for entry in arcs}
        self.assertIn("csrf_exempt_cross_file_cleanup", arc_names)
        self.assertIn("per_prefix_authz_sweep_shape", arc_names)


class ZoomOutAggregationsAdvisoryPreservationTest(SimpleTestCase):
    """Contract 2 — advisory posture survives aggregations (row 50 guardrail)."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        (self.tmpdir / "logs").mkdir()
        path = self.tmpdir / "logs" / "zoom_out_classifications.jsonl"
        path.write_text("\n".join(json.dumps(r) for r in _SAMPLE_ROWS) + "\n")
        self.handler = _ZoomOutToolHandler()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _list(self, payload=None):
        base = {"action": "list"}
        if payload:
            base.update(payload)
        with patch("django.conf.settings.BASE_DIR", str(self.tmpdir)):
            return self.handler._handle_zoom_out(
                "zoom_out_tool", base, user_id=None, trace_id="trace-test"
            )

    def test_outer_is_gate_false_with_aggregations(self):
        result = self._list({"include": "aggregations"})
        self.assertFalse(result["is_gate"])
        self.assertEqual(result["semantics"], "advisory_pattern_evidence")
        self.assertIn("pattern evidence", result["advisory"])

    def test_aggregations_block_repeats_advisory_markers(self):
        result = self._list({"include": "aggregations"})
        agg = result["aggregations"]
        # Redundant markers — belt-and-suspenders per S2780 V5 fold. Any
        # downstream consumer that would treat aggregation output as a
        # gate signal MUST see these markers.
        self.assertIn("is_gate", agg)
        self.assertFalse(agg["is_gate"])
        self.assertEqual(agg["semantics"], "advisory_pattern_evidence")

    def test_missing_log_still_advisory_when_aggregations_requested(self):
        # Rebuild without writing the log file.
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        self.tmpdir.mkdir()
        (self.tmpdir / "logs").mkdir()
        result = self._list({"include": "aggregations"})
        self.assertFalse(result["is_gate"])
        self.assertEqual(result["semantics"], "advisory_pattern_evidence")


class ZoomOutAggregationsBackwardCompatTest(SimpleTestCase):
    """Contract 3 — no ``include`` → response unchanged from S2780 shape."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        (self.tmpdir / "logs").mkdir()
        path = self.tmpdir / "logs" / "zoom_out_classifications.jsonl"
        path.write_text("\n".join(json.dumps(r) for r in _SAMPLE_ROWS) + "\n")
        self.handler = _ZoomOutToolHandler()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _list(self, payload=None):
        base = {"action": "list"}
        if payload:
            base.update(payload)
        with patch("django.conf.settings.BASE_DIR", str(self.tmpdir)):
            return self.handler._handle_zoom_out(
                "zoom_out_tool", base, user_id=None, trace_id="trace-test"
            )

    def test_no_include_omits_aggregations_key(self):
        result = self._list()
        self.assertNotIn("aggregations", result)

    def test_unknown_include_token_omits_aggregations_key(self):
        # Extension surface stays additive; ``include=other`` is treated
        # as no-op rather than raising (prevents typo → 500).
        result = self._list({"include": "other"})
        self.assertNotIn("aggregations", result)

    def test_include_list_form_accepted(self):
        # PA-tool callers may pass a list; view callers pass a
        # comma-separated string. Both parsed the same way.
        result = self._list({"include": ["aggregations"]})
        self.assertIn("aggregations", result)

    def test_include_comma_separated_string(self):
        result = self._list({"include": "aggregations,other"})
        self.assertIn("aggregations", result)


class ZoomOutAggregationsViewAllowlistTest(TestCase):
    """Contract 4 — view-layer allowlist accepts ``include``; unknown still 400."""

    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.staff = U.objects.create_user(
            username="s2791-staff-fixture",
            email="s2791-staff@donkeybetz.test",
        )
        cls.staff.is_staff = True
        cls.staff.save()

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.staff)

    def test_include_param_no_longer_rejected(self):
        # Pre-S2791: 'include' was not in _GOVERNANCE_ALLOWED_PARAMS →
        # ?include=aggregations returned 400. Post-S2791: pass-through.
        response = self.client.get(
            "/api/governance/zoom-out-ledger/?include=aggregations&limit=1"
        )
        self.assertNotEqual(response.status_code, 400)

    def test_genuinely_unknown_param_still_rejected(self):
        # Allowlist tightening from S2773 must not regress — random
        # params still hit _reject_unknown_query_params.
        response = self.client.get(
            "/api/governance/zoom-out-ledger/?zzz_random=1"
        )
        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertEqual(body.get("code"), "unknown_query_params")
        self.assertIn("zzz_random", body.get("unknown", []))
