---
title: "S2824 — Phase-0.5 B2 router build execution log"
session: 2824
date: 2026-07-19
predecessor_envelope: RATIFICATION_2026-07-18_s2823_phase0_5_constitutional_package_b1_b2_b3.md
scope:
  Records the S2824 implementation of the Phase-0.5 B2 router per Chris R7
  build authorization in the S2823 frozen envelope §7. This log is a
  separate artifact — it does NOT edit or amend the S2823 envelope
  (which is FROZEN per PLAYBOOK-6.10.9 at its own merge).
authority: implementation-log
---

# Implementation Log — S2824 Phase-0.5 B2 build

## §1 Constitutional anchoring

Executes S2823 D-verdict §15.7 R7 "Build authorization: RATIFIED — B1, B2,
B3 now form a coherent constitutional package. Build authorization is
granted only within the documented advisory-only constraints."

R1-R7 constraints from S2823 §15.1-15.7 are unchanged. This log DOES NOT
modify the frozen envelope.

## §2 Files shipped

Per B2 §13 build-gate spec:

| Path | Purpose | Novel |
|---|---|---|
| `core/services/phase_0_5_router.py` | Router module (Phase0_5Router class + RouterDecision dataclass + get_router singleton + window lifecycle + integrity events + Class B triggers) | Yes |
| `core/services/phase_0_5_classifier_a.py` | Mirror of `docs/research/discovery_layer/PHASE_0/classifier_a.py` (Python import compatibility; drift-guarded via contract test) | Yes |
| `core/settings.py` | `PHASE_0_5_ROUTER_ENABLED` bool + `PHASE_0_5_MEASUREMENT_WINDOW` enum + `PHASE_0_5_MEASUREMENT_WINDOW_N` int | Additive |
| `core/services/td_handlers_ops.py` | Flag-guarded diff at `:5905` (kb_tool.semantic_search) | Byte-identical when flag off |
| `persistence/models.py` | `Phase0_5RouterEvent` mirror model | New model |
| `persistence/migrations/0009_phase0_5routerevent.py` | Auto-generated migration | Applied to local DB S2824 |
| `docs/research/discovery_layer/PHASE_0_5/analyze_router_log.py` | Committed extraction script (JSONL SoT + optional model verification) | Yes |
| `core/tests/test_phase_0_5_router.py` | 18 contract tests locking R1-R7 + Rigby cycle-2 refinements | Yes (all pass) |
| `logs/phase_0_5_router.jsonl` | JSONL SoT — created at runtime by the router (`logs/` is in `.gitignore` so not tracked) | Yes |
| `logs/phase_0_5_integrity_events.jsonl` | Separate integrity-events log (Q5 non-recursion) — created at runtime | Yes |

## §3 R1-R7 → implementation mapping

| Constraint | Implementation |
|---|---|
| **R1 advisory-only** | Handler diff never modifies `search_embeddings` args; `_parallel_both` field is always `null` in Phase-0.5 (envelope shape `parallel_both_substrates: null`); contract test `test_parallel_both_field_is_null_on_ambiguous_decision` locks the invariant. |
| **R2 measurement window canonical unit** | `start_measurement_window` mints a `window_id` bound to the active window; every event carries `measurement_window_id`; window_start / window_end boundary events persist to durable log. |
| **R3 single instrumentation surface** | Only `td_handlers_ops.py:5905` (kb_tool.semantic_search) is modified; adjacent handlers untouched. |
| **R4 durable evidence** | JSONL is SoT (`logs/phase_0_5_router.jsonl`); `Phase0_5RouterEvent` model is mirror; `event_id` idempotency across both; mirror save failure raises `MIRROR_DIVERGENCE` integrity event (never silent reconciliation). Contract test `test_mirror_save_failure_raises_integrity_event` locks the invariant. |
| **R5 additive-non-breaking** | `_router_advisory` v1 field only appears when flag on; flag-off envelope is byte-identical (contract test + live Rigby validation confirmed). Envelope matches live `chunks` key per td_handlers_ops.py:5967+. Categorical confidence only (no numeric field anywhere in schema). |
| **R6 epistemic integrity** | Class B triggers (T2/T3) gate on `routed_count >= 20` before firing; Class C (T4/T5) inactive in Phase-0.5 (verified by static test `test_t4_never_appears_as_runtime_trigger_id`); Class D downgrade is inherent to the min-N gate. |
| **R7 downstream discipline** | Rigby cycle-2 F-BLOCKING (Q4 log-on-error) caught and resolved same-turn; all 6 questions cleared. Any weakening of these constraints post-merge routes back through SIGN + new D-verdict per S2823 §15.7. |

## §4 Rigby cycle-2 refinements → implementation mapping

| Refinement | Implementation |
|---|---|
| **Q1 mirror drift guard** | `core/services/phase_0_5_classifier_a.py` header banner + `test_mirror_classifier_matches_source_on_fixture_corpus` runs both source (via importlib) and mirror on 20 fixture queries; fails loud on drift. |
| **Q3 byte-identical safe pattern** | Existing envelope block preserved verbatim inside `if not PHASE_0_5_ROUTER_ENABLED:` early-return; flag-on branch is the only place `_router_advisory` is constructed. |
| **Q4 log-on-error (F-BLOCKING resolution)** | `search_embeddings` wrapped in `try/except/finally`; `log_decision()` fires in `finally` regardless of exception; `retrieval_error` (max 500 chars) + `retrieval_exception_type` fields added to JSONL schema + Django model. Contract test `test_log_row_includes_retrieval_error_when_populated` locks the invariant. |
| **Q5 non-recursion** | Integrity events written to `logs/phase_0_5_integrity_events.jsonl` (separate file). `_raise_integrity_event` never calls `log_decision`. Contract tests `test_integrity_event_write_does_not_touch_router_log` + `test_integrity_event_write_does_not_call_log_decision` lock the invariant. |
| **Q6-A window boundary events** | `start_measurement_window` / `end_measurement_window` write `WSTART-<uuid>` / `WEND-<uuid>` events with counter snapshots (routed_count, ambiguous_count, unclassifiable_count, context_needed_count, clarify_count, operator_override_count). Contract test `test_start_and_end_events_written_with_counter_snapshot`. |
| **Q6-B integrity-stop markdown writer** | `_raise_integrity_event` also writes `docs/research/discovery_layer/PHASE_0_5/integrity_stops/evidence_integrity_stop_<trigger>_<ts>.md`. Next classify after abort returns a `RouterDecision` with `integrity_stop_trigger` populated → envelope surfaces `_router_advisory.integrity_stop`. Window boundary re-enables the router. Contract tests `test_abort_writes_evidence_markdown_file_and_disables_window` + `test_classify_after_abort_returns_integrity_stop_decision` + `test_new_window_re_enables_router_after_abort`. |

## §5 Test contract

```
core.tests.test_phase_0_5_router
  ClassAT1NumericThresholdStructuralGuardTests
    test_router_decision_confidence_field_type_is_str ......... ok
    test_router_decision_dataclass_has_no_numeric_confidence_field .... ok
  ClassBMinNGatingTests
    test_high_abstain_rate_below_min_n_does_not_abort ......... ok
    test_high_operator_override_rate_below_min_n_does_not_abort ... ok
  ClassCT4InactiveInPhase05Tests
    test_no_parallel_execution_counter_in_router .............. ok
    test_t4_never_appears_as_runtime_trigger_id ............... ok
  MirrorDivergenceIntegrityTests
    test_mirror_save_failure_raises_integrity_event ........... ok
  Q1MirrorDriftGuardTests
    test_mirror_classifier_matches_source_on_fixture_corpus ... ok
  Q4LogOnErrorTests
    test_log_row_includes_retrieval_error_when_populated ...... ok
  Q5NonRecursionTests
    test_integrity_event_write_does_not_call_log_decision ..... ok
    test_integrity_event_write_does_not_touch_router_log ...... ok
  Q6AWindowBoundaryTests
    test_start_and_end_events_written_with_counter_snapshot ... ok
  Q6BIntegrityStopMarkdownTests
    test_abort_writes_evidence_markdown_file_and_disables_window ... ok
    test_classify_after_abort_returns_integrity_stop_decision . ok
    test_new_window_re_enables_router_after_abort ............. ok
  R1AdvisoryOnlyTests
    test_parallel_both_field_is_null_on_ambiguous_decision .... ok
  R4EventIdIdempotencyTests
    test_log_decision_writes_one_row_per_event_id ............. ok
    test_two_classifies_produce_distinct_event_ids ............ ok

Ran 18 tests in 0.101s — OK
```

## §6 Live validation

**Flag OFF (default, via Rigby PA chat):** kb_tool.semantic_search returned
envelope with keys `action`, `count`, `applied_filters`, `chunks` only. No
`_router_advisory`. Byte-identical to pre-flag.

**Flag ON (local Django shell):** 3 classifies with 3 distinct family shapes:

- "How many agents do we have" → COUNT / HIGH / no abstain
- "PLATFORM_INVENTORY" → IDENTITY / MEDIUM / no abstain
- "spider" → LOW / AMBIGUOUS / (c)

JSONL had 1 window_start + 3 router_decision rows. Django mirror had 3
matching rows with identical `event_id`s and families. Test rows cleared
before commit — shipped JSONL files are empty.

## §7 Recycle discipline

`make recycle-all` executed at S2824 close per PLAYBOOK-7.4.4 (constitutional
as of Playbook v0.6.0). Clean recycle recorded — sha=`0c77f80862b2`,
surviving=none.

## §8 Rollback

If Chris flags any post-merge R1-R7 revision:

- Fastest path: set `PHASE_0_5_ROUTER_ENABLED=false` (default). Handler
  early-returns byte-identical to pre-flag. No code revert required.
- If code revert needed: single-PR revert removes 8 files + settings diff +
  handler diff. Migration `0009_phase0_5routerevent.py` can remain applied
  or be reverted (no data dependency).

## §9 S2825 arc direction

**Recommended default:** balanced P1 harvest execution per B1 §6 — now
unblocked. Instrumentation dispatches run harvest against the flag-on
endpoint under a fresh measurement window; router advisories persist to
JSONL SoT + Django mirror.

**Available if Chris pivots:** Playbook v0.9 amendment (10/10 triggers);
Playbook v0.10 R1 provenance discipline candidate (2/2 triggers as of
S2823 + potentially 3/3 now with S2824 build execution provenance);
Colorado Phase 4; BettingPage first-user trace; Stock Intelligence
end-to-end verify.
