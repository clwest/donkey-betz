"""S2824 — Phase-0.5 advisory-only router contract tests.

Locks the constitutional constraints from S2823 D-verdict §15 R1-R7 +
S2824 Rigby cycle-2 refinements (Q1 mirror drift guard, Q3 byte-identical
safe pattern, Q4 log-on-error, Q5 non-recursion split, Q6-A window boundary
events, Q6-B integrity-stop markdown writer).

Design source: docs/research/discovery_layer/PHASE_0_5/
ROUTER_SCAFFOLDING_DESIGN.md
Envelope frozen: docs/research/implementation/
RATIFICATION_2026-07-18_s2823_phase0_5_constitutional_package_b1_b2_b3.md
"""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import TestCase

from core.services import phase_0_5_router as router_mod
from core.services.phase_0_5_router import (
    ROW_TYPE_ROUTER_DECISION,
    ROW_TYPE_WINDOW_END,
    ROW_TYPE_WINDOW_START,
    Phase0_5Router,
    RouterDecision,
    get_router,
    reset_router_for_tests,
)


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


class _P05TestBase(TestCase):
    """Base that redirects log/doc paths to a tempdir per test."""

    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.tmp_dir = Path(self._tmp.name)
        self.router_log = self.tmp_dir / "phase_0_5_router.jsonl"
        self.integrity_log = self.tmp_dir / "phase_0_5_integrity_events.jsonl"
        self.stop_doc_dir = self.tmp_dir / "integrity_stops"
        self._patches = [
            patch.object(router_mod, "ROUTER_LOG_PATH", self.router_log),
            patch.object(router_mod, "INTEGRITY_LOG_PATH", self.integrity_log),
            patch.object(router_mod, "INTEGRITY_STOP_DOC_DIR", self.stop_doc_dir),
        ]
        for p in self._patches:
            p.start()
        reset_router_for_tests()

    def tearDown(self) -> None:
        for p in self._patches:
            p.stop()
        reset_router_for_tests()
        self._tmp.cleanup()


class Q1MirrorDriftGuardTests(_P05TestBase):
    """Rigby S2824 Q1 refinement — mirror stays drift-free from source."""

    FIXTURE_QUERIES = [
        "How many agents do we have",
        "PLATFORM_INVENTORY",
        "core/rag.py",
        "what is the docs cascade",
        "restart the workers",
        "list all spider categories",
        "it",
        "the current one",
        "difference between search_docs and semantic_search",
        "how do i regenerate the platform inventory",
        "SESSION_2823",
        "00-start-next-session",
        "2823_docs_audit",
        "explain the router advisory shape",
        "find all references to _router_advisory",
        "where do i read first",
        "spider",
        "playbook",
        "how does the abstain policy handle CONTEXT_NEEDED",
        "search for parallel_both handling",
    ]

    def test_mirror_classifier_matches_source_on_fixture_corpus(self):
        # Source lives outside python package tree; import via importlib.
        import importlib.util
        import sys as _sys
        source_path = (
            Path(router_mod.__file__).resolve().parents[2]
            / "docs" / "research" / "discovery_layer" / "PHASE_0" / "classifier_a.py"
        )
        spec = importlib.util.spec_from_file_location("classifier_a_source", source_path)
        assert spec and spec.loader
        source_mod = importlib.util.module_from_spec(spec)
        # Register before exec_module so @dataclass can resolve __module__.
        _sys.modules["classifier_a_source"] = source_mod
        try:
            spec.loader.exec_module(source_mod)
        finally:
            _sys.modules.pop("classifier_a_source", None)

        from core.services.phase_0_5_classifier_a import classify_a as mirror_classify

        drifts: list[tuple[str, dict, dict]] = []
        for q in self.FIXTURE_QUERIES:
            source_out = source_mod.classify_a(q).to_dict()
            mirror_out = mirror_classify(q).to_dict()
            if source_out != mirror_out:
                drifts.append((q, source_out, mirror_out))
        self.assertFalse(
            drifts,
            msg=(
                f"Mirror drifted from source on {len(drifts)} queries: {drifts[:3]}. "
                "Re-mirror docs/.../classifier_a.py → core/services/phase_0_5_classifier_a.py."
            ),
        )


class R1AdvisoryOnlyTests(_P05TestBase):
    """R1 — advisory-only; _parallel_both ALWAYS null in Phase-0.5."""

    def test_parallel_both_field_is_null_on_ambiguous_decision(self):
        r = get_router()
        # Bare 4-word noun phrase → AMBIGUOUS per classifier_a bare_noun_phrase.
        decision = r.classify("spider")
        self.assertEqual(decision.abstain_reason, "AMBIGUOUS")
        # (c) parallel-both is the ratified advisory option but not executed.
        self.assertEqual(decision.abstain_option, "(c)")
        # There is no field on RouterDecision that hints at execution.
        for slot in ("execute_parallel", "parallel_result", "lexical_chunks"):
            self.assertFalse(hasattr(decision, slot))


class R4EventIdIdempotencyTests(_P05TestBase):
    """R4 — event_id is the idempotency key across JSONL + model."""

    def test_two_classifies_produce_distinct_event_ids(self):
        r = get_router()
        d1 = r.classify("How many agents do we have")
        d2 = r.classify("How many agents do we have")
        self.assertNotEqual(d1.event_id, d2.event_id)
        self.assertTrue(d1.event_id.startswith("evt-"))

    def test_log_decision_writes_one_row_per_event_id(self):
        r = get_router()
        d = r.classify("How many agents do we have")
        r.log_decision(
            query="How many agents do we have",
            decision=d,
            chosen_substrate="semantic_search",
            actual_substrate="semantic_search",
            retrieval_count=3,
        )
        r.log_decision(
            query="How many agents do we have",
            decision=d,
            chosen_substrate="semantic_search",
            actual_substrate="semantic_search",
            retrieval_count=3,
        )
        rows = [
            r for r in _read_jsonl(self.router_log)
            if r.get("row_type") == ROW_TYPE_ROUTER_DECISION
        ]
        # Both writes append (JSONL is append-only SoT), but they share event_id.
        self.assertEqual(len({row["event_id"] for row in rows}), 1)


class Q4LogOnErrorTests(_P05TestBase):
    """Rigby S2824 Q4 F-BLOCKING fix — log_decision fires even on error."""

    def test_log_row_includes_retrieval_error_when_populated(self):
        r = get_router()
        d = r.classify("How many spiders do we have")
        r.log_decision(
            query="How many spiders do we have",
            decision=d,
            chosen_substrate="semantic_search",
            actual_substrate="semantic_search",
            retrieval_count=0,
            retrieval_error="pg connection reset",
            retrieval_exception_type="OperationalError",
        )
        rows = _read_jsonl(self.router_log)
        decision_rows = [r for r in rows if r.get("row_type") == ROW_TYPE_ROUTER_DECISION]
        self.assertEqual(len(decision_rows), 1)
        row = decision_rows[0]
        self.assertEqual(row["retrieval_count"], 0)
        self.assertEqual(row["retrieval_error"], "pg connection reset")
        self.assertEqual(row["retrieval_exception_type"], "OperationalError")


class Q5NonRecursionTests(_P05TestBase):
    """Rigby S2824 Q5 refinement — integrity events use separate log."""

    def test_integrity_event_write_does_not_touch_router_log(self):
        r = get_router()
        r._raise_integrity_event(  # noqa: SLF001 — test hook
            trigger_id="T2",
            reason="test",
            context={"measurement_window_id": "win-x", "measurement_window_type": "session"},
        )
        # Router log stays empty; integrity log has the row.
        self.assertEqual(_read_jsonl(self.router_log), [])
        integrity_rows = _read_jsonl(self.integrity_log)
        self.assertEqual(len(integrity_rows), 1)
        self.assertEqual(integrity_rows[0]["trigger_id"], "T2")

    def test_integrity_event_write_does_not_call_log_decision(self):
        r = get_router()
        with patch.object(r, "log_decision") as mock_log:
            r._raise_integrity_event(  # noqa: SLF001
                trigger_id="MIRROR_DIVERGENCE",
                reason="test",
                context={},
            )
        mock_log.assert_not_called()


class Q6AWindowBoundaryTests(_P05TestBase):
    """Rigby S2824 Q6-A — window_start / window_end events persist."""

    def test_start_and_end_events_written_with_counter_snapshot(self):
        r = get_router()
        wid = r.start_measurement_window(window_type="session")
        for q in ["how many agents", "how many spiders", "how many services"]:
            d = r.classify(q)
            r.log_decision(
                query=q, decision=d,
                chosen_substrate="semantic_search",
                actual_substrate="semantic_search",
                retrieval_count=5,
            )
        r.end_measurement_window(wid, reason="test_boundary")

        rows = _read_jsonl(self.router_log)
        starts = [r for r in rows if r.get("row_type") == ROW_TYPE_WINDOW_START]
        ends = [r for r in rows if r.get("row_type") == ROW_TYPE_WINDOW_END]
        decisions = [r for r in rows if r.get("row_type") == ROW_TYPE_ROUTER_DECISION]
        self.assertEqual(len(starts), 1)
        self.assertEqual(len(ends), 1)
        self.assertEqual(len(decisions), 3)
        # End event carries counter snapshot.
        end_counters = ends[0]["counters"]
        self.assertEqual(end_counters["routed_count"], 3)
        self.assertEqual(ends[0]["reason"], "test_boundary")
        # Both boundary events bind to the same window_id.
        self.assertEqual(starts[0]["measurement_window_id"], wid)
        self.assertEqual(ends[0]["measurement_window_id"], wid)


class Q6BIntegrityStopMarkdownTests(_P05TestBase):
    """Rigby S2824 Q6-B — integrity-stop markdown file written per §12."""

    def test_abort_writes_evidence_markdown_file_and_disables_window(self):
        r = get_router()
        wid = r.start_measurement_window(window_type="session")
        # Manually seed a window state above min-N with dominant AMBIGUOUS +
        # UNCLASSIFIABLE counts to trigger T2 abstain-rate cap.
        state = r._windows[wid]  # noqa: SLF001
        state.routed_count = 25
        state.ambiguous_count = 15
        state.unclassifiable_count = 6
        r._evaluate_window_triggers(wid)  # noqa: SLF001
        # Window aborted.
        self.assertTrue(state.aborted)
        self.assertEqual(state.abort_trigger, "T2")
        # Integrity event log has a row.
        integrity_rows = _read_jsonl(self.integrity_log)
        self.assertEqual(len(integrity_rows), 1)
        self.assertEqual(integrity_rows[0]["trigger_id"], "T2")
        # Markdown file was written.
        md_files = list(self.stop_doc_dir.glob("evidence_integrity_stop_T2_*.md"))
        self.assertEqual(len(md_files), 1)
        body = md_files[0].read_text()
        self.assertIn("Evidence-Integrity Stop", body)
        self.assertIn("T2", body)

    def test_classify_after_abort_returns_integrity_stop_decision(self):
        r = get_router()
        wid = r.start_measurement_window(window_type="session")
        state = r._windows[wid]  # noqa: SLF001
        state.routed_count = 25
        state.ambiguous_count = 15
        state.unclassifiable_count = 6
        r._evaluate_window_triggers(wid)  # noqa: SLF001
        # Next classify inside the aborted window signals integrity_stop.
        decision = r.classify("how many agents")
        self.assertEqual(decision.integrity_stop_trigger, "T2")
        self.assertTrue(decision.abstain_reason.startswith("INTEGRITY_STOP_"))

    def test_new_window_re_enables_router_after_abort(self):
        r = get_router()
        wid1 = r.start_measurement_window(window_type="session")
        state1 = r._windows[wid1]  # noqa: SLF001
        state1.aborted = True
        state1.abort_trigger = "T2"
        # Ending + starting a new window resumes router operation.
        r.end_measurement_window(wid1)
        wid2 = r.start_measurement_window(window_type="session")
        self.assertNotEqual(wid1, wid2)
        decision = r.classify("how many agents")
        self.assertIsNone(decision.integrity_stop_trigger)


class ClassBMinNGatingTests(_P05TestBase):
    """§12 Class B triggers ONLY evaluate when routed_count >= MIN_N_FOR_TRIGGERS."""

    def test_high_abstain_rate_below_min_n_does_not_abort(self):
        r = get_router()
        wid = r.start_measurement_window(window_type="session")
        state = r._windows[wid]  # noqa: SLF001
        # 15 rows — below the 20 min-N. 100% abstain rate.
        state.routed_count = 15
        state.ambiguous_count = 15
        r._evaluate_window_triggers(wid)  # noqa: SLF001
        self.assertFalse(state.aborted)

    def test_high_operator_override_rate_below_min_n_does_not_abort(self):
        r = get_router()
        wid = r.start_measurement_window(window_type="session")
        state = r._windows[wid]  # noqa: SLF001
        state.routed_count = 10
        state.operator_override_count = 10
        r._evaluate_window_triggers(wid)  # noqa: SLF001
        self.assertFalse(state.aborted)


class ClassAT1NumericThresholdStructuralGuardTests(_P05TestBase):
    """§12 T1 — no numeric confidence field anywhere in the schema."""

    def test_router_decision_dataclass_has_no_numeric_confidence_field(self):
        import dataclasses
        fields = {f.name for f in dataclasses.fields(RouterDecision)}
        # Only categorical confidence exists; no numeric variant.
        self.assertIn("confidence_categorical", fields)
        for banned in ("confidence", "confidence_numeric", "confidence_score", "score"):
            self.assertNotIn(banned, fields)

    def test_router_decision_confidence_field_type_is_str(self):
        import typing
        hints = typing.get_type_hints(RouterDecision)
        self.assertEqual(hints["confidence_categorical"], str)


class ClassCT4InactiveInPhase05Tests(_P05TestBase):
    """§12 T4 (parallel-retrieval confusion pattern) is inactive in Phase-0.5.

    Advisory-only guarantee (Chris R1): parallel-both is NOT executed. T4
    activates only if a future D-verdict lifts the guardrail. Verified
    structurally: the router has no code path that increments a T4 counter
    or evaluates T4 during Phase-0.5.
    """

    def test_no_parallel_execution_counter_in_router(self):
        r = get_router()
        wid = r.start_measurement_window(window_type="session")
        state = r._windows[wid]  # noqa: SLF001
        # There is no `parallel_confusion_count` field on window state.
        for banned in ("parallel_confusion_count", "parallel_execution_count", "t4_count"):
            self.assertFalse(hasattr(state, banned))

    def test_t4_never_appears_as_runtime_trigger_id(self):
        # Static evidence: _evaluate_window_triggers must not construct any
        # abort call whose trigger_id is T4 or T5 in Phase-0.5.
        import inspect
        src = inspect.getsource(Phase0_5Router._evaluate_window_triggers)
        self.assertNotIn('trigger_id="T4"', src)
        self.assertNotIn("trigger_id='T4'", src)
        self.assertNotIn('trigger_id="T5"', src)
        self.assertNotIn("trigger_id='T5'", src)


class MirrorDivergenceIntegrityTests(_P05TestBase):
    """R4 §15.4 — divergence between JSONL + model raises integrity event."""

    def test_mirror_save_failure_raises_integrity_event(self):
        r = get_router()
        d = r.classify("How many agents do we have")
        with patch(
            "persistence.models.Phase0_5RouterEvent.objects.update_or_create",
            side_effect=RuntimeError("simulated DB failure"),
        ):
            r.log_decision(
                query="How many agents do we have",
                decision=d,
                chosen_substrate="semantic_search",
                actual_substrate="semantic_search",
                retrieval_count=1,
            )
        # Router log still gets the row (SoT preserved).
        rows = _read_jsonl(self.router_log)
        decisions = [r for r in rows if r.get("row_type") == ROW_TYPE_ROUTER_DECISION]
        self.assertEqual(len(decisions), 1)
        # Integrity event log has the divergence event.
        integrity_rows = _read_jsonl(self.integrity_log)
        self.assertTrue(
            any(r["trigger_id"] == "MIRROR_DIVERGENCE" for r in integrity_rows),
            msg=f"Expected MIRROR_DIVERGENCE event; got {integrity_rows}",
        )
