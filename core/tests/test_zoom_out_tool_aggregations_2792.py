"""S2792 — zoom_out_tool PA-tool aggregations parity contract.

Locks the S2791 aggregations block (shipped for the Sign Ledger UI drill-down
via REST at ``core/views_governance.py``) at the PA-tool schema surface so
Rigby can invoke it directly through GPT-5.2 function-calling.

Scope of this PR: schema-only exposure of the ``include`` parameter.
Handler code path (``_zoom_out_list`` in ``core/services/td_handlers_governance.py``)
already emits ``result['aggregations']`` when ``payload['include']`` contains
``'aggregations'`` — this test suite verifies that the schema now advertises
the capability and that the handler contract holds across the same payload
shapes Rigby would send through function-calling.

Contracts locked:

  1. Passing ``include='aggregations'`` returns an ``aggregations`` key with
     ``top_arcs_by_count`` / ``future_trigger_rule_targets`` / ``sessions_covered``.

  2. Omitting ``include`` returns no ``aggregations`` key (opt-in, not
     always-on — matches S2791 REST behavior).

  3. Advisory posture markers are present inside the aggregations block
     (``is_gate: false`` + ``semantics: "advisory_pattern_evidence"``) —
     redundant with response-envelope markers per S2791 F3 "belt-and-braces"
     defense against advisory→gate drift.

  4. ``future_trigger_rule_targets`` regex only aggregates rows whose
     ``classification`` == ``future_trigger`` (S2791 REST invariant —
     ``same_pr_actionable`` and ``same_pr_mitigatable`` rows do not
     contribute rule-target counts even when their concern_text mentions
     PLAYBOOK-x.y).

  5. Empty ledger returns an ``aggregations`` block with empty lists
     (fail-soft — matches ``total_rows: 0`` fail-soft path).

  6. ``aggregations`` computed over ALL rows, not the filtered tail (S2791
     REST invariant — enables Rigby to reason about full-corpus population
     even when items[] is filter-scoped). This is S2792 Fold 3 substrate
     (future_trigger — deferred until ~200 rows or first user complaint).

  7. PA-tool schema at ``core/services/pa_tool_schemas.py`` advertises
     ``include`` as a top-level property (function-calling contract) with
     advisory language matching S2792 Folds 1+2 mitigations.

  8. Comma-separated + list-form ``include`` token parsing (handler
     already supports both — locking to prevent regression if Rigby sends
     ``['aggregations']`` vs ``'aggregations'``).

Ratified: S2792 T1 Rigby joint SIGN — tool-grounded read_file × 3 verified
handler+schema+REST claims (i)/(ii)/(iii); AGREE on all with minor
sessions_covered int-only defensive-code note (skipped as separate fold —
record_zoom_out_concern already coerces session to int at line 140). Three
folds classified + persisted BEFORE D-verdict per PLAYBOOK-6.10.8/9:
ledger rows 51 (same_pr_mitigatable, F1 → schema advisory language),
52 (same_pr_actionable, F2 → rule_target-not-proposal warning),
53 (future_trigger, F3 → aggregation_scope metadata deferred).
Chris D-verdict: "go — SHIP schema-only with F1+F2 mitigations inline".
"""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

from core.services.td_handlers_governance import GovernanceHandlersMixin
from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS


class _StubHandler:
    pass


class _ZoomOutToolHandler(GovernanceHandlersMixin, _StubHandler):
    pass


# Mixed-classification corpus with PLAYBOOK-x.y mentions in BOTH future_trigger
# rows (should count) AND non-future_trigger rows (should NOT count) — locks
# the regex-only-future_trigger invariant.
_SAMPLE_ROWS = [
    {
        "ts": "2026-07-14T00:00:00+00:00",
        "schema_version": 1,
        "session": 2784,
        "arc": "arc_alpha",
        "classification": "same_pr_actionable",
        # PLAYBOOK-6.10.9 mention here MUST NOT count (not future_trigger).
        "concern_text": "Related to PLAYBOOK-6.10.9 evidence admission.",
        "evidence_ref": None,
        "backfilled": False,
        "entered_by": "claude",
    },
    {
        "ts": "2026-07-14T00:01:00+00:00",
        "schema_version": 1,
        "session": 2785,
        "arc": "arc_alpha",
        "classification": "future_trigger",
        # Two hits, one row: PLAYBOOK-6.10.7 + PLAYBOOK-6.10.8 both count.
        "concern_text": "Extends PLAYBOOK-6.10.7 and PLAYBOOK-6.10.8 discipline.",
        "evidence_ref": None,
        "backfilled": False,
        "entered_by": "claude",
    },
    {
        "ts": "2026-07-14T00:02:00+00:00",
        "schema_version": 1,
        "session": 2786,
        "arc": "arc_beta",
        "classification": "future_trigger",
        # Third hit for PLAYBOOK-6.10.7 (repeat across rows counts).
        "concern_text": "Also touches PLAYBOOK-6.10.7 boundary.",
        "evidence_ref": None,
        "backfilled": False,
        "entered_by": "claude",
    },
    {
        "ts": "2026-07-14T00:03:00+00:00",
        "schema_version": 1,
        "session": 2787,
        "arc": "arc_beta",
        "classification": "same_pr_mitigatable",
        # PLAYBOOK-7.4.4 mention here MUST NOT count (not future_trigger).
        "concern_text": "PLAYBOOK-7.4.4 recycle cadence.",
        "evidence_ref": None,
        "backfilled": False,
        "entered_by": "claude",
    },
]


class AggregationsParityTests(SimpleTestCase):
    """Contracts 1-6 — handler behavior under aggregations opt-in."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        (self.tmpdir / "logs").mkdir()
        self.handler = _ZoomOutToolHandler()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_ledger(self, rows):
        path = self.tmpdir / "logs" / "zoom_out_classifications.jsonl"
        path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        return path

    def _list(self, payload=None):
        base = {"action": "list"}
        if payload:
            base.update(payload)
        with patch("django.conf.settings.BASE_DIR", str(self.tmpdir)):
            return self.handler._handle_zoom_out(
                "zoom_out_tool", base, user_id=None, trace_id="s2792-test"
            )

    # ── Contract 1: opt-in returns aggregations block ────────────────────
    def test_include_aggregations_returns_block(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"include": "aggregations"})
        self.assertIn("aggregations", result)
        agg = result["aggregations"]
        self.assertIn("top_arcs_by_count", agg)
        self.assertIn("future_trigger_rule_targets", agg)
        self.assertIn("sessions_covered", agg)

    # ── Contract 2: omitted include -> no aggregations key ───────────────
    def test_omitted_include_returns_no_aggregations_key(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list()  # no include
        self.assertNotIn("aggregations", result)

    def test_include_without_aggregations_token_returns_no_block(self):
        self._write_ledger(_SAMPLE_ROWS)
        # Passing include with a non-aggregations token still opts OUT.
        result = self._list({"include": "some_other_expansion"})
        self.assertNotIn("aggregations", result)

    # ── Contract 3: advisory markers present inside block ────────────────
    def test_aggregations_block_repeats_advisory_markers(self):
        """S2791 Row 50 regression assertion — carried forward at S2792.

        The aggregations block MUST embed ``is_gate: false`` +
        ``semantics: 'advisory_pattern_evidence'`` even though the same
        markers exist in the response envelope. Belt-and-braces per S2791
        F3 defense against advisory→gate drift if a future PR mutates
        the block extraction path.
        """
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"include": "aggregations"})
        agg = result["aggregations"]
        self.assertIs(agg.get("is_gate"), False)
        self.assertEqual(agg.get("semantics"), "advisory_pattern_evidence")

    # ── Contract 4: regex only aggregates future_trigger rows ────────────
    def test_rule_targets_only_from_future_trigger_rows(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"include": "aggregations"})
        rule_targets = {
            entry["rule_id"]: entry["count"]
            for entry in result["aggregations"]["future_trigger_rule_targets"]
        }
        # Expected from _SAMPLE_ROWS future_trigger rows only:
        #   Row 1 (session 2785): PLAYBOOK-6.10.7 + PLAYBOOK-6.10.8
        #   Row 2 (session 2786): PLAYBOOK-6.10.7
        # NOT counted:
        #   session 2784 (same_pr_actionable): PLAYBOOK-6.10.9
        #   session 2787 (same_pr_mitigatable): PLAYBOOK-7.4.4
        self.assertEqual(rule_targets.get("PLAYBOOK-6.10.7"), 2)
        self.assertEqual(rule_targets.get("PLAYBOOK-6.10.8"), 1)
        self.assertNotIn("PLAYBOOK-6.10.9", rule_targets)
        self.assertNotIn("PLAYBOOK-7.4.4", rule_targets)

    # ── Contract 5: empty ledger returns empty aggregations ──────────────
    def test_empty_ledger_returns_empty_aggregations(self):
        self._write_ledger([])
        result = self._list({"include": "aggregations"})
        self.assertIn("aggregations", result)
        agg = result["aggregations"]
        self.assertEqual(agg["top_arcs_by_count"], [])
        self.assertEqual(agg["future_trigger_rule_targets"], [])
        self.assertEqual(agg["sessions_covered"], [])
        self.assertIs(agg["is_gate"], False)

    # ── Contract 6: aggregations computed over ALL rows, not filter tail ─
    def test_aggregations_over_all_rows_not_filtered_tail(self):
        """S2792 Fold 3 substrate — future_trigger deferred.

        When items[] is filtered (e.g., classification=future_trigger),
        the aggregations block still reflects the full-corpus population.
        This test locks the current invariant so Fold 3's eventual
        aggregation_scope metadata / dual-block refactor is a visible
        contract change.
        """
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({
            "include": "aggregations",
            "classification": "future_trigger",
        })
        # items[] filtered to future_trigger only (2 rows).
        self.assertEqual(result["count"], 2)
        # But sessions_covered contains ALL sessions (all 4).
        self.assertEqual(
            set(result["aggregations"]["sessions_covered"]),
            {2784, 2785, 2786, 2787},
        )
        # And top_arcs_by_count contains BOTH arcs.
        arcs = {
            entry["arc"] for entry in result["aggregations"]["top_arcs_by_count"]
        }
        self.assertEqual(arcs, {"arc_alpha", "arc_beta"})

    # ── Bonus: list-form include (Rigby function-calling variant) ────────
    def test_include_as_list_also_activates_aggregations(self):
        """Handler supports both str and list — lock both."""
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"include": ["aggregations"]})
        self.assertIn("aggregations", result)

    def test_include_comma_separated_activates_aggregations(self):
        """Handler supports comma-separated string — lock the token parse."""
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"include": "aggregations,other_expansion"})
        self.assertIn("aggregations", result)


class SchemaContractTests(SimpleTestCase):
    """Contract 7 — PA-tool schema advertises the capability.

    Function-calling contract: unless GPT-5.2 sees ``include`` in the
    schema properties, Rigby has no path to invoke aggregations even
    though the handler supports it. Lock the advertisement.
    """

    def _zoom_out_schema(self):
        for schema in PA_TOOL_SCHEMAS:
            if schema.get("name") == "zoom_out_tool":
                return schema
        self.fail("zoom_out_tool schema not found in PA_TOOL_SCHEMAS")
        return None  # unreachable

    def test_zoom_out_schema_declares_include_property(self):
        schema = self._zoom_out_schema()
        props = schema["parameters"]["properties"]
        self.assertIn("include", props)
        self.assertEqual(props["include"]["type"], "string")

    def test_include_description_declares_aggregations_value(self):
        """S2792 Fold 1 mitigation locked in schema copy."""
        schema = self._zoom_out_schema()
        include_desc = schema["parameters"]["properties"]["include"]["description"]
        # Must mention the currently-supported token.
        self.assertIn("aggregations", include_desc)
        # Must include the S2791 block shape hints.
        self.assertIn("top_arcs_by_count", include_desc)
        self.assertIn("future_trigger_rule_targets", include_desc)
        self.assertIn("sessions_covered", include_desc)

    def test_include_description_carries_advisory_warning(self):
        """S2792 Fold 1 — advisory posture spelled out at schema level."""
        schema = self._zoom_out_schema()
        include_desc = schema["parameters"]["properties"]["include"]["description"]
        lowered = include_desc.lower()
        self.assertIn("advisory", lowered)
        self.assertIn("is_gate:false", include_desc.replace(" ", ""))
        self.assertIn(
            "semantics:advisory_pattern_evidence",
            include_desc.replace(" ", ""),
        )

    def test_include_description_carries_rule_target_pushback(self):
        """S2792 Fold 2 mitigation — rule_target counts are NOT proposals."""
        schema = self._zoom_out_schema()
        include_desc = schema["parameters"]["properties"]["include"]["description"]
        lowered = include_desc.lower()
        # Fold 2: rule_target counts are pattern evidence, not proposals.
        self.assertIn("rule_target", lowered)
        self.assertIn("not", lowered)
        # Fold 2: Chris D-verdict remains the codification gate.
        self.assertIn("chris d-verdict", lowered)

    def test_include_not_in_required_list(self):
        """Opt-in only — never required."""
        schema = self._zoom_out_schema()
        required = schema["parameters"].get("required", [])
        self.assertNotIn("include", required)

    def test_schema_top_level_description_mentions_include(self):
        """Function-calling top-level description also carries the capability."""
        schema = self._zoom_out_schema()
        self.assertIn("include", schema["description"].lower())
        self.assertIn("aggregations", schema["description"].lower())
