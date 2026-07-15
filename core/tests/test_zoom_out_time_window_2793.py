"""S2793 — zoom_out_tool N22 v2 time-window filter contract.

Adds ``since_session`` / ``until_session`` integer params to
``_zoom_out_list`` in ``core/services/td_handlers_governance.py`` +
``core/views_governance.py`` REST view + ``core/services/pa_tool_schemas.py``
PA-tool schema + the ``ZoomOutLedgerSection.tsx`` UI. Deferred trigger
per S2793 open doc line 73 (ledger 53-row temporal spread hit).

Contracts locked (10 across 2 classes):

  1. ``since_session`` narrows items[] to sessions >= bound (inclusive).

  2. ``until_session`` narrows items[] to sessions <= bound (inclusive).

  3. Both together intersect (window == [since_session, until_session]).

  4. ``since_session=0`` / negative treated as no-filter (autofill guard
     mirrors existing ``session`` filter pattern at ``td_handlers_governance.py``
     lines 105-113).

  5. ``until_session=0`` / negative treated as no-filter.

  6. **F3 substrate — aggregations remain over ALL rows even under window
     filter.** Extends S2792 contract 6 (which locked the invariant for
     ``classification`` filter) to the S2793 window filter. Third instance
     of the future-trigger-encoded-as-test pattern after S2791 F3 +
     S2792 F3 — Playbook amendment candidate per S2793 open doc line 86.
     Any future dual-aggregations refactor becomes a visible contract
     change here.

  7. ``since_session > until_session`` returns empty items[] (not error),
     yet aggregations still populated.

  8. Response echoes ``since_session_filter`` / ``until_session_filter``
     fields ONLY when the corresponding filter was applied (F1 same-PR
     mitigation — never emit noise fields).

  9. PA-tool schema at ``core/services/pa_tool_schemas.py`` declares
     ``since_session`` and ``until_session`` integer properties with F1
     advisory language ("aggregations remain longitudinal / global").

 10. REST allowlist at ``core/views_governance.py`` includes both params
     so UI queries don't 400 (F2 must-do).

Ratified: S2793 T1 Rigby joint SIGN — tool-grounded read_file × 4 verified
(i) session autofill guard at ``td_handlers_governance.py:105-113``,
(ii) REST allowlist frozenset at ``views_governance.py:32-38``,
(iii) S2792 contract 6 invariant at ``test_zoom_out_tool_aggregations_2792.py:229-255``,
(iv) PA-tool schema block at ``pa_tool_schemas.py:2614-2695``.
SIGN-with-edits — 3 folds classified + persisted BEFORE Chris D-verdict
per PLAYBOOK-6.10.8/9: rows 54 (same_pr_mitigatable, F1 — advisory copy),
55 (same_pr_actionable, F2 — REST wiring + allowlist), 56 (future_trigger,
F3 — aggregation scope metadata / dual aggregations, deferred and encoded
here as contract 6). Chris D-verdict: "yes go".
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


# Temporal-spread corpus spanning S2780-S2792 so window queries have
# clear inside/outside partitions to assert against.
_SAMPLE_ROWS = [
    {
        "ts": "2026-07-13T00:00:00+00:00",
        "schema_version": 1,
        "session": 2780,
        "arc": "arc_alpha",
        "classification": "same_pr_actionable",
        "concern_text": "S2780 fold.",
        "evidence_ref": None,
        "backfilled": False,
        "entered_by": "claude",
    },
    {
        "ts": "2026-07-14T00:00:00+00:00",
        "schema_version": 1,
        "session": 2785,
        "arc": "arc_alpha",
        "classification": "future_trigger",
        # PLAYBOOK-6.10.7 mention — should count toward rule_targets.
        "concern_text": "Extends PLAYBOOK-6.10.7 discipline.",
        "evidence_ref": None,
        "backfilled": False,
        "entered_by": "claude",
    },
    {
        "ts": "2026-07-15T00:00:00+00:00",
        "schema_version": 1,
        "session": 2790,
        "arc": "arc_beta",
        "classification": "same_pr_mitigatable",
        "concern_text": "S2790 fold.",
        "evidence_ref": None,
        "backfilled": False,
        "entered_by": "claude",
    },
    {
        "ts": "2026-07-15T00:00:00+00:00",
        "schema_version": 1,
        "session": 2792,
        "arc": "arc_beta",
        "classification": "future_trigger",
        # PLAYBOOK-6.10.9 mention — should count toward rule_targets.
        "concern_text": "Corroborates PLAYBOOK-6.10.9 pattern.",
        "evidence_ref": None,
        "backfilled": False,
        "entered_by": "claude",
    },
]


class TimeWindowFilterTests(SimpleTestCase):
    """Contracts 1-8 — handler behavior under session-int window filters."""

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
                "zoom_out_tool", base, user_id=None, trace_id="s2793-test"
            )

    # ── Contract 1: since_session narrows items[] (inclusive lower) ──────
    def test_since_session_filters_inclusive_lower_bound(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"since_session": 2790})
        sessions = {r["session"] for r in result["items"]}
        self.assertEqual(sessions, {2790, 2792})
        self.assertEqual(result["count"], 2)

    # ── Contract 2: until_session narrows items[] (inclusive upper) ──────
    def test_until_session_filters_inclusive_upper_bound(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"until_session": 2785})
        sessions = {r["session"] for r in result["items"]}
        self.assertEqual(sessions, {2780, 2785})
        self.assertEqual(result["count"], 2)

    # ── Contract 3: since + until intersect ──────────────────────────────
    def test_since_and_until_intersect_as_window(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"since_session": 2785, "until_session": 2790})
        sessions = {r["session"] for r in result["items"]}
        self.assertEqual(sessions, {2785, 2790})
        self.assertEqual(result["count"], 2)

    # ── Contract 4: since_session=0 / negative = no filter ───────────────
    def test_since_session_zero_treated_as_no_filter(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"since_session": 0})
        self.assertEqual(result["count"], 4)
        # Filter field should NOT appear in response.
        self.assertNotIn("since_session_filter", result)

    def test_since_session_negative_treated_as_no_filter(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"since_session": -1})
        self.assertEqual(result["count"], 4)
        self.assertNotIn("since_session_filter", result)

    # ── Contract 5: until_session=0 / negative = no filter ───────────────
    def test_until_session_zero_treated_as_no_filter(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"until_session": 0})
        self.assertEqual(result["count"], 4)
        self.assertNotIn("until_session_filter", result)

    def test_until_session_string_non_numeric_treated_as_no_filter(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"until_session": "not-a-number"})
        self.assertEqual(result["count"], 4)
        self.assertNotIn("until_session_filter", result)

    # ── Contract 6: F3 — aggregations still over ALL rows under window ──
    def test_aggregations_over_all_rows_under_window_filter(self):
        """S2793 Fold 3 substrate — future_trigger deferred.

        Locks the invariant that ``since_session``/``until_session`` only
        narrow ``items[]`` — the aggregations block (when
        ``include=aggregations``) still reflects the full-corpus
        population regardless of the window.

        Third instance of the future-trigger-encoded-as-test pattern
        after S2791 F3 (``test_aggregations_block_repeats_advisory_markers``)
        and S2792 F3 (``test_aggregations_over_all_rows_not_filtered_tail``).
        Playbook amendment candidate per S2793 open doc line 86 — do not
        propose amendment this PR; watch for consumer complaint or the
        aggregation_scope metadata refactor to make this a visible
        contract change.
        """
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({
            "include": "aggregations",
            "since_session": 2790,
        })
        # items[] narrowed to {2790, 2792} — 2 rows.
        self.assertEqual(result["count"], 2)
        # sessions_covered still contains ALL sessions (all 4).
        self.assertEqual(
            set(result["aggregations"]["sessions_covered"]),
            {2780, 2785, 2790, 2792},
        )
        # top_arcs_by_count still contains BOTH arcs (arc_alpha survives
        # even though its rows are outside the window).
        arcs = {
            entry["arc"] for entry in result["aggregations"]["top_arcs_by_count"]
        }
        self.assertEqual(arcs, {"arc_alpha", "arc_beta"})
        # rule_targets still aggregates across ALL future_trigger rows
        # (both PLAYBOOK-6.10.7 from S2785 outside window + PLAYBOOK-6.10.9
        # from S2792 inside window). Full corpus population preserved.
        rule_targets = {
            entry["rule_id"]
            for entry in result["aggregations"]["future_trigger_rule_targets"]
        }
        self.assertIn("PLAYBOOK-6.10.7", rule_targets)
        self.assertIn("PLAYBOOK-6.10.9", rule_targets)

    # ── Contract 7: inverted window returns empty items, no error ────────
    def test_inverted_window_returns_empty_items_not_error(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({
            "since_session": 2792,
            "until_session": 2780,
            "include": "aggregations",
        })
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["items"], [])
        # No error field emitted.
        self.assertNotIn("error", result)
        # Aggregations still populated over ALL rows.
        self.assertEqual(len(result["aggregations"]["sessions_covered"]), 4)

    # ── Contract 8: filter-echo fields only when applied ─────────────────
    def test_filter_echo_only_when_applied(self):
        self._write_ledger(_SAMPLE_ROWS)
        # Neither filter applied → neither echoed.
        r_no = self._list()
        self.assertNotIn("since_session_filter", r_no)
        self.assertNotIn("until_session_filter", r_no)
        # Only since → only since echoed.
        r_since = self._list({"since_session": 2785})
        self.assertEqual(r_since["since_session_filter"], 2785)
        self.assertNotIn("until_session_filter", r_since)
        # Only until → only until echoed.
        r_until = self._list({"until_session": 2790})
        self.assertEqual(r_until["until_session_filter"], 2790)
        self.assertNotIn("since_session_filter", r_until)
        # Both applied → both echoed.
        r_both = self._list({"since_session": 2785, "until_session": 2790})
        self.assertEqual(r_both["since_session_filter"], 2785)
        self.assertEqual(r_both["until_session_filter"], 2790)


class SchemaAndAllowlistTests(SimpleTestCase):
    """Contracts 9-10 — PA-tool schema advertises the params + REST
    allowlist accepts them.

    Function-calling contract: without schema advertisement, Rigby can't
    invoke the window filter through GPT-5.2. Without REST allowlist,
    UI queries return 400.
    """

    def _zoom_out_schema(self):
        for schema in PA_TOOL_SCHEMAS:
            if schema.get("name") == "zoom_out_tool":
                return schema
        self.fail("zoom_out_tool schema not found in PA_TOOL_SCHEMAS")
        return None  # unreachable

    # ── Contract 9: schema declares both properties as integer ───────────
    def test_schema_declares_since_session_integer_property(self):
        schema = self._zoom_out_schema()
        props = schema["parameters"]["properties"]
        self.assertIn("since_session", props)
        self.assertEqual(props["since_session"]["type"], "integer")

    def test_schema_declares_until_session_integer_property(self):
        schema = self._zoom_out_schema()
        props = schema["parameters"]["properties"]
        self.assertIn("until_session", props)
        self.assertEqual(props["until_session"]["type"], "integer")

    def test_since_session_description_carries_advisory_copy(self):
        """S2793 Fold 1 mitigation locked in schema copy.

        Window narrows items[] only; aggregations remain longitudinal.
        Rigby MUST see this in the function-calling schema so she can't
        drift into "window-scoped aggregations" reasoning.
        """
        schema = self._zoom_out_schema()
        desc = schema["parameters"]["properties"]["since_session"]["description"].lower()
        # Advisory language: window narrows items only + aggregations global.
        self.assertIn("items", desc)
        self.assertIn("aggregations", desc)
        self.assertTrue(
            "longitudinal" in desc or "all rows" in desc or "global" in desc,
            f"Schema copy must state aggregations remain global; got: {desc}",
        )

    def test_until_session_description_carries_advisory_copy(self):
        schema = self._zoom_out_schema()
        desc = schema["parameters"]["properties"]["until_session"]["description"].lower()
        # Advisory language: mirrors since_session (either "no filter"
        # phrasing OR aggregations-stay-global phrasing acceptable).
        self.assertTrue(
            "no filter" in desc or "aggregations" in desc,
            f"until_session description must carry advisory framing; got: {desc}",
        )

    # ── Contract 10: REST allowlist accepts both params ──────────────────
    def test_rest_allowlist_includes_window_params(self):
        from core.views_governance import (
            _GOVERNANCE_ALLOWED_PARAMS__ZOOM_OUT_LEDGER,
        )
        self.assertIn(
            "since_session", _GOVERNANCE_ALLOWED_PARAMS__ZOOM_OUT_LEDGER
        )
        self.assertIn(
            "until_session", _GOVERNANCE_ALLOWED_PARAMS__ZOOM_OUT_LEDGER
        )
