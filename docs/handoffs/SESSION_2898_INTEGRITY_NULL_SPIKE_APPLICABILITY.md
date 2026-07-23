# Session 2898 — `integrity_null_spike_scan` applicability rule (Ledger Row B) → mitigated

**Date:** 2026-07-22
**PR:** [#3421](https://github.com/clwest/donkey-betz-platform/pull/3421) merged into main at commit `3bed824c4`
**Ship shape:** Engineering-first (Row B pick at S2898 open — Chris ratified after clarifying "B" between "Option B" and "Row B"). Design → Rigby SIGN AGREE (4 dimensions, tool-grounded) → implementation + 8 tests → live post-recycle verification green.
**D6 moratorium status:** IN FORCE (no strategic discovery arcs opened this session).

## What shipped

**PR #3421 — S2898 `integrity_null_spike_scan` applicability rule.** Adds per-field applicability policy to `DataIntegrityEngine.get_null_spike_scan` in `core/services/ops_autopilot/intelligence.py`:

```python
FIELD_APPLICABILITY = {
    'raw_data':       'always',              # primary payload
    'processed_data': 'never',               # dead field, verified 0/72 spiders
    'embedding_text': 'historical_baseline', # async pipeline, keep lag signal
}
```

- `_field_is_applicable(spider, data_type, field, historical_populated_pairs)` returns `(applicable, reason)`. Reason strings are stable identifiers usable in tests and operator UI (`always`, `never`, `historical_populated`, `historical_never_populated`, `unknown_field`).
- `_historical_populated_pairs(field)` runs **once per HISTORICAL_BASELINE field per scan call** — O(1) queries in fields, not O(N) in (spider, data_type) pairs (locked by `assertNumQueries=2`).
- Return dict adds `applicability_skipped` (total), `applicability_skipped_by_field` (per-field breakdown), `baseline_pairs_count` (baseline set sizes). Each emitted spike gains `applicability_reason` field.

## Session shape (three-part plain-English)

1. **What was done.** Chris ratified engineering-first (Row B) at S2898 open — the last remaining open S2895 Ledger row. ORM audit confirmed 96 critical spikes at `null_rate=1.0` split 48/48 across `processed_data` (verified dead field: 0/72 spiders with ≥10 rows ever populated it) and `embedding_text` (populated by 49/72 spiders historically but 0 in last 24h due to async pipeline lag). Designed per-field applicability policy; Rigby SIGN AGREE with 5 concrete edge-case tests absorbed inline; shipped PR + live-verified + post-merge recycled.
2. **Why it matters.** `autopilot_tool.integrity_null_spike_scan` was returning 96 critical spikes, 48 of which were pure noise (`processed_data` field is dead — never populated by any spider ever). Operators triaging the scan output had to mentally filter dead-field spam every time. After this ship: 43 remaining spikes, all legitimately `historical_populated` (real embedding-pipeline-lag signal), and each carries an `applicability_reason` field so operators can filter by reason class. Before/after: `spike_count: 96 → 43`; `applicability_skipped: 0 → 43`.
3. **What's next.** Row B → mitigated (Ledger entry #26 for Row B... actually let Rigby number). All three S2895 Ledger rows now closed (A→S2897, B→S2898, C→S2896). Three deferred zoom-out fold candidates recorded for the ledger. Row 161 substrate-arc gate STILL not decided (three consecutive engineering-first picks now: S2896, S2897, S2898).

## Rigby SIGN cycle summary

**Pre-ship SIGN (design routing):** Rigby ran 6 `repo_tool` grounding calls verifying: intelligence.py line ranges, caller list of `get_null_spike_scan`, that `evaluate()` uses `get_quality_report` (not `get_null_spike_scan`), and confirmed my consumer-safety claim. Verdicts:

- **Q1 (design correctness):** AGREE — per-field + historical baseline is the right shape. Recommended making the classification an explicit inspectable enum (`FIELD_APPLICABILITY = {...}`) at module scope rather than only in code logic. **Absorbed inline.**
- **Q2 (consumer safety):** AGREE — verified via grep no other callers depend on per-spike shape; `evaluate()` reads `get_quality_report()` which only touches `raw_data`. Autopilot enforcement path unaffected.
- **Q3 (test coverage):** DISAGREE with proposed 5-test set — surfaced 5 additional edge cases (A–E: mixed historical population, low-sample-size double-count, data_type migration, empty baseline, query count). **All 5 absorbed inline** (final test file has 8 tests covering all Q3 dimensions).
- **Q4 zoom-out (coupling risk):** AGREE with Phase 1 all-time baseline; recommended Phase 2 lookback cap (30/90d) to prevent "ever true" from becoming permanent sticky bit. Phase 2 deferred to zoom-out ledger — not blocking. Surfaced 3 concrete fold candidates.

**Verification tool_runs (post-recycle live dispatch):** 1 tool_run — `autopilot_tool.integrity_null_spike_scan hours=24`. Result matched design predictions exactly: `spike_count: 43`, `applicability_skipped: 43`, `applicability_skipped_by_field: {processed_data: 43}`, `baseline_pairs_count: {embedding_text: 87}`, all 43 remaining spikes have `field='embedding_text'` + `applicability_reason='historical_populated'`.

## Zoom-out folds this session

**Three fold candidates surfaced in Rigby's Q4 (all deferred to zoom-out ledger — Phase 2 work):**

1. **Applicability metadata is mandatory for heterogeneous integrity scans.** Any integrity detector operating over optional/dead fields will dominate signal-to-noise unless it encodes field applicability (ALWAYS / NEVER / BASELINE-GATED). Pattern applies beyond `null_spike_scan` — likely relevant to `duplicate_report`, `freshness_scan`, per-source reliability scoring.
2. **All-time baselines create "sticky semantics" across regime changes.** "Ever true" becomes permanent coupling; if `embedding_text` is legitimately deprecated for a (spider, data_type) pair, an all-time baseline will keep flagging it forever. Phase 2 lookback cap (30/90d) or dual baseline ("ever" for applicability + "recent" for severity/confidence).
3. **Separate ingest integrity from downstream pipeline freshness.** `raw_data` failures are ingest regressions (should be critical); `embedding_text` all-null over a window is likely async-pipeline-lag (should have separate confidence channel or aggregate as one "pipeline lag" issue rather than N per-spider spikes).

**Trigger for arc:** any of these three would become urgent when the next integrity detector is added or when embedding_text lag becomes chronic (>3 sessions of persistent embedding_text=100%-null spikes).

## Files touched

- `core/services/ops_autopilot/intelligence.py` — +103/-1 lines. Added `FIELD_APPLICABILITY` module-level dict on `DataIntegrityEngine` class (~10 lines); added `_historical_populated_pairs(field)` helper (~25 lines); added `_field_is_applicable(spider, data_type, field, historical_populated_pairs)` helper (~30 lines); rewrote `get_null_spike_scan()` to pre-compute baselines + filter via applicability + expose 3 new return-dict fields (~38 lines).
- `core/tests/test_s2898_null_spike_applicability.py` — new file, 176 lines, 8 tests covering all 4 policy shapes + 5 edge cases (A–E). All passing. 14 pre-existing autofill regression tests (`test_autofill_sweep_session_1228_pr_b`) still pass.

## Live verification (post-recycle)

`autopilot_tool.integrity_null_spike_scan hours=24` default dispatch after `make celery-recycle`:

```json
{
  "action": "integrity_null_spike_scan",
  "period_hours": 24,
  "spike_count": 43,
  "has_spikes": true,
  "applicability_skipped": 43,
  "applicability_skipped_by_field": {"processed_data": 43},
  "baseline_pairs_count": {"embedding_text": 87},
  "spikes": [
    {"spider": "theodds", "data_type": "sports_odds", "field": "embedding_text",
     "null_count": 10, "total": 10, "null_rate": 1.0, "severity": "critical",
     "applicability_reason": "historical_populated"},
    ...42 more, all field=embedding_text, applicability_reason=historical_populated
  ]
}
```

Post-merge recycle done per PLAYBOOK-7.4.4.

## Rigby Tool Gap Ledger status (deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`)

- **Row A (`prospecting_queue` empty titles)** — `mitigated` at PR #3419 (S2897). Unchanged.
- **Row B (`integrity_null_spike_scan` false-positive noise)** — **`MITIGATED` at PR #3421 (S2898)**. All three S2895 Ledger rows now closed.
- **Row C (`autopilot_tool.history` selected_fields silent longer-list wipe)** — `mitigated` at PR #3417 (S2896). Unchanged.
- **Row 27 (deferred, from S2897):** "Batched spider rows collapse N leads into one autopilot Opportunity row." Unchanged.
- **Rows 28/29/30 (deferred, new this session):** three zoom-out fold candidates from S2898 Rigby SIGN Q4 — see "Zoom-out folds" above.

(Rigby will update the workspace ledger deliverable at close per `feedback_rigby_writes_workspace_deliverables`.)

## Row 161 substrate-arc gate — status

**Not decided this session.** Chris picked engineering-first again at S2898 open — third consecutive session (S2896 + S2897 + S2898). Row 161 substrate-arc gate remains open for S2899. Three consecutive engineering-first picks strongly suggests Chris preference for shipping over methodology iteration; watch at S2899 whether Chris continues the pattern (Row 27 arc, or other engineering candidates) or opens the substrate arc.

## Sweep progress tracker (Path B ratified S2892)

**Slice 1 — `td_handlers_ops` (17 registered tools):**
- Batches 1-4 (S2892-S2895): 9 tools ✓
- **S2896:** engineering ship (Row C mitigated).
- **S2897:** engineering ship (Row A mitigated).
- **S2898 (this session):** engineering ship (Row B mitigated).
- **All 3 S2895-surfaced Ledger rows now closed.**
- **Remainder:** Slice 1.5b (`autopilot_tool` mutations, ~1 session) + 4 doc/unknown/partial ops tools (~1-2 sessions).

**Gap-map:** unchanged from S2896 (no sweep batch this session).

## What's next — S2899 open sequence

Per Chris's engineering-bias-over-audit rule + all 3 S2895 Ledger rows now closed + Row 161 gate still open:

1. **FIRST DECISION POINT — Row 161 substrate-arc gate.** Three consecutive Option-C picks (S2896 + S2897 + S2898). All three surfaced Ledger rows closed. Chris may want to re-frame options or continue with engineering candidates from a fresh source (new Ledger rows 28/29/30 from S2898 zoom-out, Row 27 batched-items structural).
2. **If continue engineering:** priority candidates:
   - **S2898 Phase 2** — baseline lookback cap on `embedding_text` applicability (30/90d) — small addition, closes the sticky-semantics risk Rigby surfaced.
   - **DBZ enforcement doc-clarity annotation** — `enforcement_report` hysteresis-oscillation shape (S2895 T2 revised discussion, still queued).
   - **S2894 Ledger rows** — `messaging_tool.send` action or `zoom_out_tool.record_fold` action.
   - **PLAYBOOK-3.2.3/3.2.4 compliance sweep** — carried from S2891.
3. **If continue sweeps:** Slice 1.5b (`autopilot_tool` mutations sweep — 29 actions, needs staged-enforcement session with paired lifecycle scaffolding).
4. **Deferred (D6 moratorium still in force):** No strategic discovery arcs. Docs restructuring arc, W2 #1/#2b/#2c, LLMCallLog field splits, bulk workspace_budget operations, C4/C5/C6 character-os follow-ons all remain queued.

## For fuller sweep context

- **S2897 handoff (prior):** `docs/handoffs/SESSION_2897_PROSPECTING_QUEUE_TITLE_FIX.md`
- **S2896 handoff:** `docs/handoffs/SESSION_2896_AUTOPILOT_HISTORY_WIPE_DIAGNOSTIC.md`
- **S2895 handoff (Row A/B/C surfaced):** `docs/handoffs/SESSION_2895_PA_TOOLS_SWEEP_SLICE_1_5A_AUTOPILOT_READ_ONLY.md`
- **Autopilot tool validation:** `docs/research/tools/validation/autopilot_tool_validation.md`
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)
