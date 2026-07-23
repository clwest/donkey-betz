# Session 2899 — `integrity_null_spike_scan` baseline lookback cap (Ledger Row #29) → mitigated

**Date:** 2026-07-22
**PR:** [#3423](https://github.com/clwest/donkey-betz-platform/pull/3423) merged into main at commit `1fd68a49b`
**Ship shape:** Engineering-first (Row #29 pick — fourth consecutive engineering-first ship). Chris ratified Option C with an explicit trigger that S2900 opens with Row 161 as the FIRST action regardless of queued candidates (avoids engineering-bias silently supplanting the sweep-pace substrate-arc gate).
**D6 moratorium status:** IN FORCE (no strategic discovery arcs opened this session).

## What shipped

**PR #3423 — S2899 `integrity_null_spike_scan` baseline lookback cap.** Layers an optional per-field lookback cap on top of the S2898 Phase 1 `HISTORICAL_BASELINE` applicability policy in `DataIntegrityEngine.get_null_spike_scan`:

```python
HISTORICAL_BASELINE_LOOKBACK_DAYS = {
    'embedding_text': None,   # None = all-time (S2898 Phase 1 default)
                              # int N = last N days rolling window
}
```

- `_historical_populated_pairs(field, lookback_days=None)` — chained `.filter(created_at__gte=cutoff)` before `.values(...).distinct()` when lookback is set. Preserves the **O(1)-queries-per-field invariant** from S2898 (locked by `test_query_count_is_bounded` via `assertNumQueries=2`).
- `get_null_spike_scan()` reads the class dict and passes lookback per HISTORICAL_BASELINE field.
- Return dict adds `baseline_lookback_days` **scoped to HISTORICAL_BASELINE fields only** (per Rigby Q2 — cleaner than dumping None for always/never entries).

## Session shape (three-part plain-English)

1. **What was done.** Chris ratified engineering-first at S2899 open (Option C — S2898 Phase 2, embedding_text baseline lookback cap). Design: added `HISTORICAL_BASELINE_LOOKBACK_DAYS` class dict; extended `_historical_populated_pairs` to accept `lookback_days` kwarg; wired call site in `get_null_spike_scan`; extended return dict with `baseline_lookback_days`. Wrote 3 new tests (default None preserves S2898 semantics; 30d cap excludes 100d-old populate; 30d cap preserves 10d-old populate). All 11 tests pass (8 Phase 1 + 3 new). Rigby SIGN AGREE with two zoom-out concerns (knob proliferation, decay-vs-truth semantics — both already mitigated by design). Shipped PR + recycled + live-verified via Django shell (wrapper truncated PA-tool output, so verified at ORM layer).
2. **Why it matters.** The S2898 Phase 1 `HISTORICAL_BASELINE` baseline is "ever populated in DB history" — this creates sticky semantics: a pair that populated `embedding_text` long ago but has legitimately stopped (retired data_type, replaced pipeline) would keep emitting spikes on every scan. With the cap available, operators can now decay stale populates out of the baseline once a pipeline lag becomes chronic. **Default None = zero behavior change at ship** — this is substrate work, not an automatic policy change.
3. **What's next.** Row #29 → mitigated. Row 161 substrate-arc gate remains open (fourth consecutive engineering-first pick). **Explicit trigger recorded:** S2900 opens with Row 161 as the FIRST decision regardless of what candidates are queued. This is not a "queue-drainage" continuation — Chris wants the gate resolved before the fifth engineering-first pick.

## Rigby SIGN cycle summary

**Pre-ship SIGN (design routing):** One turn, envelope-format, single verdict + Q1–Q4. Verdicts:

- **Q1 (correctness / O(1) query invariant):** AGREE — chained `.filter()` before `.values(...).distinct()` preserves single-query-per-field. Called out sanity checks: filter applied inside same queryset, no per-row `.exists()`/`.first()` loops, skip counter computed from materialized results not extra `.count()`. Code matches — no per-pair queries introduced.
- **Q2 (semantic-lock / return payload scope):** AGREE — scoping `baseline_lookback_days` to HISTORICAL_BASELINE fields only is correct. Nit-level rename suggestion (`historical_baseline_lookback_days` for explicit tie to policy name) — explicitly not blocking, kept current name for parity with FIELD_APPLICABILITY convention.
- **Q3 (test lock / query count):** AGREE with not extending `test_query_count_is_bounded` — 3 semantic tests are the right ROI; would only add if we had a history of accidental N+1 regressions in this code path.
- **Q4 zoom-out (coupling risks):** AGREE with two concerns worth naming:
  1. **Knob proliferation / governance clarity** — every new knob increases operator mental-model burden. Mitigated by default None + return-dict-explains-active-semantics. Watch: ensure single canonical place for operator to flip; don't let it become "set in three places" drift.
  2. **Baseline semantics: "decay" vs "truth"** — a lookback cap changes meaning from "has ever been populated" to "has been populated recently." Totally fine (it's the point), but alters severity interpretation. Mitigated: field-scoped (not global default), operator tuning knob only.

**Verification tool_runs (post-recycle live dispatch):** PA-tool dispatch of `autopilot_tool.integrity_null_spike_scan hours=24` completed and returned full spike detail, but the wrapper output truncates at ~76 lines and the summary fields were pushed off the top by the ~44-row spikes array. Verified at Django shell (raw ORM path per `feedback_verify_at_raw_orm_before_trusting_tool_no_data`):

```json
{
  "period_hours": 24,
  "spike_count": 44,
  "has_spikes": true,
  "applicability_skipped": 44,
  "applicability_skipped_by_field": {"processed_data": 44},
  "baseline_pairs_count": {"embedding_text": 87},
  "baseline_lookback_days": {"embedding_text": null}
}
```

`baseline_lookback_days` field IS PRESENT and default `null` value confirms zero behavior change at ship. Baseline pairs count `87` matches S2898 exactly. Spike count `44` (was `43` at S2898 close — one new pair since yesterday, expected drift).

## Zoom-out folds this session

None new. Rigby's Q4 concerns (knob proliferation, decay-vs-truth semantics) are already mitigated in the shipped design — no new fold candidates added to the ledger.

## Files touched

- `core/services/ops_autopilot/intelligence.py` — +45/-5 lines. Added `HISTORICAL_BASELINE_LOOKBACK_DAYS` class dict (~10 lines); extended `_historical_populated_pairs` signature + docstring + optional filter (~15 lines); wired call site in `get_null_spike_scan` (~5 lines); extended return dict with `baseline_lookback_days` scoped comprehension (~5 lines).
- `core/tests/test_s2898_null_spike_applicability.py` — +93 lines. New `BaselineLookbackCapTests` class with 3 tests + `_mk` + `_backdate` helpers.

## Live verification (post-recycle)

Django shell dispatch after `make recycle-all` completed cleanly at HEAD `1fd68a49b`:

- `baseline_lookback_days: {"embedding_text": null}` — Phase 2 field present, default preserved.
- `baseline_pairs_count: {"embedding_text": 87}` — unchanged from S2898.
- Spike count 44 (was 43 at S2898 close; one new pair drift, expected).
- All 44 skipped are `processed_data` (dead field, correctly suppressed).

Local test result: **11 passed in 196.72s (0:03:16)**. All 8 Phase 1 tests continue to pass unchanged (default-None substitutes cleanly for the old unconditional all-time query).

Post-merge recycle done per PLAYBOOK-7.4.4.

## Rigby Tool Gap Ledger status (deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`)

- **Row A / B / C (S2895-surfaced):** all `mitigated` (Row A at PR #3419 S2897, Row B at PR #3421 S2898, Row C at PR #3417 S2896). Unchanged.
- **Row 27 (deferred, from S2897):** batched spider rows collapse N leads into one autopilot Opportunity row. Unchanged.
- **Row 28 (deferred, from S2898 Q4):** applicability metadata mandatory for heterogeneous integrity scans. Unchanged.
- **Row 29 (deferred, from S2898 Q4):** all-time baselines create sticky semantics — **`MITIGATED` at PR #3423 (S2899)**. Default-None substrate + operator tuning knob available.
- **Row 30 (deferred, from S2898 Q4):** separate ingest integrity from downstream pipeline freshness. Unchanged.

(Rigby will update the workspace ledger deliverable at close per `feedback_rigby_writes_workspace_deliverables`.)

## Row 161 substrate-arc gate — status

**Not decided this session.** Fourth consecutive engineering-first pick (S2896 + S2897 + S2898 + S2899). **Chris ratified the S2899 Option-C pick with an explicit trigger:** at S2900 open, Row 161 is the FIRST decision regardless of what engineering candidates are queued. This preserves the engineering-bias benefits of the recent streak while preventing the pattern from silently supplanting the sweep-pace substrate-arc gate.

## Sweep progress tracker (Path B ratified S2892)

**Slice 1 — `td_handlers_ops` (17 registered tools):**
- Batches 1-4 (S2892-S2895): 9 tools ✓
- **S2896:** engineering ship (Row C mitigated).
- **S2897:** engineering ship (Row A mitigated).
- **S2898:** engineering ship (Row B mitigated).
- **S2899 (this session):** engineering ship (Row #29 mitigated — Phase 2 lookback cap).
- **All 3 S2895-surfaced Ledger rows + one deferred zoom-out row now closed.**
- **Remainder:** Slice 1.5b (`autopilot_tool` mutations, ~1 session) + 4 doc/unknown/partial ops tools (~1-2 sessions).

**Gap-map:** unchanged from S2896 (no sweep batch this session).

## What's next — S2900 open sequence

**Per Chris's explicit S2899 ratification trigger:**

1. **FIRST ACTION — Row 161 substrate-arc gate DECISION.** Not a menu item, not deferred behind other candidates. Chris's directive: resolve this before any fifth engineering-first pick. Options remain A/B/C from the S2896–S2899 arc:
   - **Option A (Rigby lean, S2895 close):** Open a dedicated substrate arc (auto-harness build + family-doc template extraction + low-signal tool audit). Slows sweep pace short-term; expected to close remaining Slice 1-5 scope in ~10-15 sessions instead of ~50.
   - **Option B:** Push through Slice 1 close-out (~4-5 more current-shape sessions), THEN re-evaluate. Closes Slice 1.5b + 4 doc/unknown/partial ops tools.
   - **Option C:** Another engineering session. Priority candidates listed in step 2 below (do NOT open Option C without explicit re-ratification given the four-consecutive-C-picks pattern).
2. **If Option C re-ratified after Row 161 decision:** priority candidates:
   - **DBZ enforcement doc-clarity annotation** — `enforcement_report` hysteresis-oscillation shape (S2895 T2 revised discussion, still queued).
   - **S2894 Ledger rows** — `messaging_tool.send` action or `zoom_out_tool.record_fold` action.
   - **PLAYBOOK-3.2.3/3.2.4 compliance sweep** — carried from S2891.
   - **Rows 27/28/30 arc trigger watch** — batched-items structural (Row 27), applicability metadata pattern (Row 28), ingest-vs-pipeline separation (Row 30) all remain deferred with unchanged trigger criteria.
3. **Deferred (D6 moratorium still in force):** No strategic discovery arcs. Docs restructuring arc, W2 #1/#2b/#2c, LLMCallLog field splits, bulk workspace_budget operations, C4/C5/C6 character-os follow-ons all remain queued.

## For fuller sweep context

- **S2898 handoff (prior):** `docs/handoffs/SESSION_2898_INTEGRITY_NULL_SPIKE_APPLICABILITY.md`
- **S2897 handoff:** `docs/handoffs/SESSION_2897_PROSPECTING_QUEUE_TITLE_FIX.md`
- **S2896 handoff:** `docs/handoffs/SESSION_2896_AUTOPILOT_HISTORY_WIPE_DIAGNOSTIC.md`
- **S2895 handoff (Row A/B/C surfaced):** `docs/handoffs/SESSION_2895_PA_TOOLS_SWEEP_SLICE_1_5A_AUTOPILOT_READ_ONLY.md`
- **Autopilot tool validation:** `docs/research/tools/validation/autopilot_tool_validation.md`
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)
