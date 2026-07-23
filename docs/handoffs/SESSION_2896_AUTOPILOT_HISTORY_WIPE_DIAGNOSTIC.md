# Session 2896 — `autopilot_tool.history` wipe-diagnostic (Ledger Row C)

**Date:** 2026-07-22
**PR:** [#3417](https://github.com/clwest/donkey-betz-platform/pull/3417) merged into main at commit `dfbb4e194`
**Ship shape:** Engineering-first (Option C at S2896 open — Chris ratified). Response-contract additive change; two new echo fields; all 19 unit tests pass; Rigby T1 + T2 SIGN AGREE live.
**D6 moratorium status:** IN FORCE (no strategic discovery arcs opened this session).

## What shipped

**PR #3417 — S2896 `autopilot_tool.history` wipe-diagnostic.** Response now echoes two additive fields alongside `selected_fields`:

- `selected_fields_dropped` — paths per-item validation rejected (invalid prefix / no dot).
- `selected_fields_received_count` — list length as the handler saw it pre-truncation (NOT end-to-end proof of what the caller sent).

Four operator cases become unambiguous:

| kept                          | dropped     | count      | interpretation                                                       |
|-------------------------------|-------------|------------|----------------------------------------------------------------------|
| `[N paths]`                   | `[]`        | `N`        | normal, all valid                                                    |
| `[]`                          | `[M paths]` | `M`        | per-item validation rejected M (handler-side silent-ignore)          |
| `[]`                          | `[]`        | `N (N>0)`  | **upstream wipe** — list arrived at handler as `[]` despite caller sending N. This is the S2895 T2 shape. |
| `[20 paths]`                  | `[]`        | `25`       | silent truncation at cap                                             |

Existing `selected_fields` echo contract unchanged.

## Session shape (three-part plain-English)

1. **What was done.** Fixed the diagnostic gap that let Rigby's S2895 T2 silent-wipe observation escape without a location. Instead of chasing an upstream root cause that didn't reproduce, added additive echo fields so the wipe surfaces the next time it happens.
2. **Why it matters.** Any operator (Rigby, Chris, downstream LLMs) who sees `selected_fields: []` after sending a non-empty list can now tell — from the response alone — whether the wipe happened in the handler (validation dropped all) or upstream (schema/JSON-parse/LLM-arg-emission). Before this change, that was a "drop to Django shell" investigation.
3. **What's next.** Ledger Row C flips from `open` to `mitigated`. Row A (`prospecting_queue` empty titles) and Row B (`integrity_null_spike_scan` false-positive noise) remain open engineering candidates for S2897. Row 161 substrate-arc gate still not decided — Chris deferred by picking Option C this session.

## Rigby SIGN cycle summary

**T1 SIGN (4 tool_runs):** `repo_tool.read_file` × 2 (verified diff + tests), `autopilot_tool.history` × 2 (live 8-path + 4-path dispatches). Verdicts:
- **Q1 (diff shape):** AGREE — additive, backward-compatible, echo semantics correct.
- **Q2 (8-path live attempt):** NOT REPRODUCED — response coherent; new fields would surface a wipe if it occurred.
- **Q3 (4-path control):** PASS.
- **Q4 (tests):** AGREE — 7 new tests discriminate the four operator cases plus edge cases.
- **Q5 ZOOM-OUT:** Fold row 162 (`same_pr_mitigatable`) — response-level introspection field creep risks over-interpretation as general transport-audit probe. Same-PR mitigation shipped: schema description narrowed to explicit "NOT end-to-end proof" language + "Narrow use:" prefix.

**T2 SIGN (1 tool_run):** `autopilot_tool.history` post-merge live dispatch. Verdicts:
- **Live shape:** AGREE — new fields present, values correct, existing echo unchanged.
- **Deploy SHA check:** DISAGREE — but this was my sloppy verification framing. The `deploy_sha` field is per-`AutopilotAction`-row-created-at, not per-tool-executed-at. New handler code IS live (proven by new echo fields being present).

## Rigby Tool Gap Ledger status (deliverable `5c84e75a-…`)

- **Row A (`prospecting_queue` empty titles)** — open. S2895 candidate.
- **Row B (`integrity_null_spike_scan` false-positive noise)** — open. S2895 candidate.
- **Row C (`autopilot_tool.history` selected_fields silent longer-list wipe)** — **`mitigated` at PR #3417 (S2896)**. Diagnostic surface shipped; root cause not fixed (not reproducible), but any recurrence will now be locatable from response fields alone.

## Zoom-out folds persisted to `logs/zoom_out_classifications.jsonl`

- **Row 162 (`same_pr_mitigatable`) — response-level introspection field creep.** Adding two new echo fields (`selected_fields_dropped` + `selected_fields_received_count`) risks operators/LLMs over-interpreting the `_count` field as end-to-end proof of what the caller sent. Same-PR mitigation: schema description narrowed to explicit "NOT end-to-end proof" phrasing + "Narrow use:" prefix on the four-case recipe. Rigby T1 AGREE on classification.

## Files touched

- `core/services/td_handlers_ops.py` — +12 lines around 2521-2564 (added `selected_fields_dropped` tracking + `selected_fields_received_count`; both surfaced in response return dict).
- `core/services/pa_tool_schemas.py` — schema description updated to document new echo fields + narrowed scope claim ("NOT end-to-end proof").
- `core/tests/test_s2861_autopilot_selected_fields.py` — +90 lines, 7 new tests (`test_dropped_paths_surfaced_in_echo`, `test_upstream_wipe_signature`, `test_all_paths_dropped_distinguishable_from_wipe`, `test_received_count_reflects_pre_truncation_length`, `test_non_list_received_count_is_zero`, `test_include_evidence_false_still_surfaces_received_count`, plus preserved existing `test_nested_value_returned_whole`). All 19 tests pass under `--keepdb`.
- `logs/zoom_out_classifications.jsonl` — appended row 162 (local-only; gitignored).

## Row 161 substrate-arc gate — status

**Not decided this session.** Chris picked Option C (engineering-first Ledger row) at S2896 open. Row 161 substrate-arc gate remains open for S2897. Options unchanged from S2895 close:

- **Option A (Rigby lean):** open dedicated substrate arc — auto-harness build + family-doc template extraction + low-signal tool audit. Cuts remaining sweep from ~50 sessions to ~10-15.
- **Option B:** push through Slice 1 close-out (~4-5 more current-shape sessions) then re-evaluate with hard data.
- **Option C:** another Ledger-row-fix engineering session (Row A or Row B).

## Sweep progress tracker (Path B ratified S2892)

**Slice 1 — `td_handlers_ops` (17 registered tools):**
- Batches 1-4 (S2892-S2895): 9 tools ✓ (`agent_control_tool`, `agent_memory_tool`, `heartbeat_history_tool`, `infra_health_tool`, `governor_tool`, `ops_digest_tool`, `scheduled_tasks_tool`, `spider_status_tool`, `workspace_budget_tool`, `autopilot_tool` read-only)
- **S2896 (this session):** engineering ship (no sweep batch). Row C mitigated.
- **Remainder:** Slice 1.5b (autopilot_tool mutations, ~1 session) + 4 doc/unknown/partial ops tools (`agent_introspection_tool`, `kb_tool`, `search_docs`, `ops_tool`, ~1-2 sessions).

**Gap-map:** unchanged from S2895 close (no sweep batch this session).

## What's next — S2897 open sequence

Per Chris's decision this session (Option C) and Row 161 gate remaining open:

1. **Row 161 substrate-arc gate STILL OPEN** — decide among Option A / B / C (S2895 shape) OR C-continue (fix Row A or Row B).
2. **Ledger candidates surfaced at S2895 still open:**
   - Row A: `prospecting_queue` empty-titles investigation
   - Row B: `integrity_null_spike_scan` applicability-rule or allowlist
   - Also: DBZ enforcement doc-clarity annotation (from S2895 T2 revised discussion).
3. **Or continue Slice 1 sweep:** Slice 1.5b autopilot mutations OR next doc/unknown/partial ops tool.
4. **PLAYBOOK-3.2.3/3.2.4 compliance sweep** — carried from S2891.

**D6 MORATORIUM still in force** — no strategic discovery arcs, no R1a proposals, no docs restructuring, no W2 items, no LLMCallLog field splits, no bulk workspace_budget operations, no C4/C5/C6 character-os follow-ons.

## For fuller sweep context

See:
- **S2896 handoff (this doc)**
- **S2895 handoff:** `docs/handoffs/SESSION_2895_PA_TOOLS_SWEEP_SLICE_1_5A_AUTOPILOT_READ_ONLY.md`
- **S2894 handoff:** `docs/handoffs/SESSION_2894_PA_TOOLS_SWEEP_SLICE_1_BATCH_3.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md`
- **Autopilot tool validation doc:** `docs/research/tools/validation/autopilot_tool_validation.md` (§3, §5, §7.1 reference the Row C shape)
- **Zoom-out ledger:** `logs/zoom_out_classifications.jsonl` (local-only; row 162 appended this session)
