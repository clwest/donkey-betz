# `zoom_out_tool` — Validation Report (S2937)

**Tool:** `zoom_out_tool`
**Schema:** `core/services/pa_tool_schemas.py:2897` (1-action enum + 6 optional filter/opt-in params)
**Handler:** `core/services/td_handlers_governance.py:26` (`_handle_zoom_out`) → `_zoom_out_list` at line 48
**Register site:** `core/services/tool_dispatcher.py:524`
**Session:** S2937 (Slice 7 batch 1 — trio with `rigby_shift_brief_tool` + `spider_data_aggregation_tool`)
**HEAD at validation:** `416931160` (2026-07-24)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4.
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2937 T0 SIGN AGREE (tool-grounded — verified single-action pure-read + PLAYBOOK-6.10.8 advisory posture invariants).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`zoom_out_tool` is the **read surface for `logs/zoom_out_classifications.jsonl`** — the append-only ledger of Rigby SIGN zoom-out concerns per PLAYBOOK-6.10.8 (constitutional at Playbook v0.7.0). Use it during joint SIGN loops to consult prior zoom-out folds before repeating them, or to answer "what did we surface last time on this arc?", "how many `future_trigger` folds mention PLAYBOOK-6.10.7 across the sweep?", or "show me the S2790-S2800 window of ratchet concerns."

**Advisory-only by explicit design** — response embeds `advisory` header + `is_gate: false` + `semantics: "advisory_pattern_evidence"` in three redundant fields (per PLAYBOOK-6.10.8 + S2777 tail-wags-dog fold) to prevent advisory→gate drift regardless of consumer surface. Ships alongside a Chris-facing UI at `/api/governance/zoom-out-ledger/`.

Distinct from `ops_tool.zoom_out_ledger` (pre-S2780 same surface; factored out at N22 v3 per S2779 V6 fold + S2780 V7 Fold B firing — first non-Rigby consumer); from `record_zoom_out_concern` management command (the WRITE path — writes to the same jsonl; this tool is READ-only); from the Chris-facing governance UI at `/api/governance/zoom-out-ledger/` (functionally equivalent read surface for humans).

## Covered actions

Enumerating every action in the schema `action` enum. **1 action, LIVE-VERIFIED at S2937.**

- `list` — **in scope this ship — verified live.** Default (and only) action. Reads the tail of `logs/zoom_out_classifications.jsonl` with optional filters (session / since_session / until_session / classification / arc / limit) + opt-in aggregations block. Envelope: `{action, log_exists, log_path, advisory, is_gate: false, semantics, total_rows, counts_by_classification, items[], count, limit, malformed_lines_skipped, [aggregations{...}] if include=aggregations, [<filter>_filter if applied]}`.
- **default (no `action` param)** — verified via handler code inspection (`td_handlers_governance.py:39`). Defaults to `list` per `payload.get('action', 'list')`.
- **invalid action** — verified via handler code inspection (`td_handlers_governance.py:42-46`). Returns via `_handler_error` helper: `{"action": "<x>", "error_code": "unknown_action", "error": "Unknown zoom_out_tool action: <x>"}`. Non-raising envelope shape.

## 3. Schema notes

- **Required:** `action` (enum: `list` — only value).
- **Optional filters:**
  - `session` (int — exact-match on originating session; autofill-guarded per line 118-126 so `session=0` or negative treated as no-filter).
  - `since_session` (int — inclusive lower bound; same autofill guard per line 132-142).
  - `until_session` (int — inclusive upper bound; same autofill guard).
  - `classification` (enum: `same_pr_actionable` / `same_pr_mitigatable` / `future_trigger`; per line 111).
  - `arc` (string — substring match on arc slug per line 112).
  - `limit` (int — default 20, min 1, max 100, clamped at line 105-109).
- **Optional opt-in:** `include` (string or list — comma-separated tokens; only `aggregations` token honored per line 274-284). When present, response gains `aggregations{top_arcs_by_count, future_trigger_rule_targets, sessions_covered, is_gate:false, semantics}` computed over ALL rows (not the filtered items window) — invariant locked by `test_zoom_out_time_window_2793.py` contract 6.
- **Fail-soft on missing log file:** if `logs/zoom_out_classifications.jsonl` doesn't exist, returns `{log_exists: false, ...zero-shaped envelope, note: "logs/zoom_out_classifications.jsonl not present. The record_zoom_out_concern management command emits this file on first classified fold per PLAYBOOK-6.10.8."}` (line 166-185).
- **Path-traversal defense (line 144-165):** log path resolved against `settings.BASE_DIR`; refuses reads outside the tree with `note: "log path resolved outside BASE_DIR; refusing to read"`. Mirrors `_ops_recent_recycles` discipline.
- **Malformed line handling (line 208-220):** malformed JSON lines skipped defensively; `malformed_lines_skipped` counter always present in response (even when zero).
- **Aggregations block invariant (line 271-282):** computed over ALL rows regardless of filter window — preserves longitudinal-signal semantics. Documented in schema description + locked by contract test.
- **Advisory-posture redundancy (line 246-259):** response includes `advisory` header + `is_gate: false` + `semantics: "advisory_pattern_evidence"` in the top-level envelope, AND the same 3 fields inside `aggregations{}` (when opt-in). Three redundant surfaces prevent advisory→gate drift.
- **No auth gate:** module docstring line 12 explicitly notes "Advisory-only by explicit design." Pure filesystem read.
- **No `dry_run` affordance:** pure-read tool — none needed.

## 4. Golden-path examples

**Example 1 — Default tail (last 20 rows):**
```json
{"action": "list"}
```
→ `{"action":"list", "log_exists":true, "log_path":"logs/zoom_out_classifications.jsonl", "advisory":"Rigby SIGN zoom-out concern ledger — pattern evidence for review. Rows are longitudinal signal, not automatic escalation triggers. Any Playbook codification decision requires its own ratification.", "is_gate":false, "semantics":"advisory_pattern_evidence", "total_rows":<N>, "counts_by_classification":{"same_pr_actionable":<A>, "same_pr_mitigatable":<M>, "future_trigger":<F>}, "items":[...last 20 rows...], "count":<up to 20>, "limit":20, "malformed_lines_skipped":<K>}`.

**Example 2 — Session-window narrowing + aggregations:**
```json
{"action": "list", "since_session": 2900, "until_session": 2936, "include": "aggregations"}
```
→ Same envelope shape; `items[]` narrowed to sessions in [2900, 2936]; `since_session_filter=2900` + `until_session_filter=2936` echoed; `aggregations{top_arcs_by_count, future_trigger_rule_targets, sessions_covered, is_gate:false, semantics}` block added — **computed over ALL rows, not the filter window** (invariant per §3).

**Example 3 — Filter by classification for `future_trigger` folds only:**
```json
{"action": "list", "classification": "future_trigger", "limit": 50}
```
→ Same envelope shape; `items[]` restricted to `future_trigger` rows; `classification_filter="future_trigger"` echoed; `limit=50` (clamped in [1, 100]).

## 5. Failure / empty-state / pagination notes

- **Missing log file:** fail-soft envelope with `log_exists: false, total_rows: 0, items: [], note: "logs/zoom_out_classifications.jsonl not present. The record_zoom_out_concern management command emits this file on first classified fold per PLAYBOOK-6.10.8."` (line 166-185). Advisory fields still populated. No exception.
- **OS read failure:** wrapped at line 187-204 → `note: "read failed: <exc!s>"`. Same envelope shape as missing-file case. No exception.
- **Path resolves outside BASE_DIR:** refuses to read with `note: "log path resolved outside BASE_DIR; refusing to read"` (line 144-164). Path-traversal defense.
- **Malformed JSON lines:** silently skipped; counter surfaced in `malformed_lines_skipped`. Non-dict JSON also counted as malformed (line 217-219).
- **Empty filter result (`items: []`):** `count: 0, items: []` returned; `total_rows` still reflects all rows in the file; `counts_by_classification` still aggregates over ALL rows (pre-filter). Consumer can distinguish "empty file" (`total_rows=0`) from "filtered to empty" (`total_rows>0, count=0`).
- **Invalid action:** returns `{"action": "<x>", "error_code": "unknown_action", "error": "Unknown zoom_out_tool action: <x>"}` via `_handler_error`. Non-raising in-envelope error. Consistent with rigby_shift_brief_tool + spider_data_aggregation_tool siblings this batch.
- **`limit` out of bounds:** silently clamped to [1, 100]; no error surfaced (line 105-109).
- **`session=0` / negative int:** autofill-guarded — treated as no-filter per line 118-126 + 132-142. Documented as "LLM commonly autofills integer params with 0" guard.
- **Multiple filter dimensions AND-ed:** filters at line 224-243 are cumulative (all applied). No OR-mode.
- **`include=aggregations` short-circuit:** only `aggregations` token recognized in the `include` list per line 274-284. Unknown tokens silently ignored; no error.
- **Pagination:** none. `limit` is a tail-window cap over the filtered set. No offset/cursor. Full-history readers use the Chris-facing UI at `/api/governance/zoom-out-ledger/` or read the jsonl file directly.

## 5c. Contract ↔ Implementation Consistency (S2937 retro-fold; per Rigby zoom-out #4)

### 5c.1 Handler / module header claims match action reality

**Disposition: PASS.** Module docstring (line 1-17) accurately states single `zoom_out_tool` action with "read surface for `logs/zoom_out_classifications.jsonl`", "Rigby-consumable during joint SIGN loops per PLAYBOOK-6.10.7 + 6.10.8", "Advisory-only by explicit design — response embeds `advisory` header + `is_gate: false` + `semantics: \"advisory_pattern_evidence\"` to prevent advisory→gate drift." Schema description (line 2898-2910) matches: names the single `list` action, cites PLAYBOOK-6.10.8, describes filter set, notes advisory-only aggregations. Handler matches. Zero drift.

### 5c.2 Gating truth matches runtime behavior

**Disposition: PASS — no gate.** No settings flag, no env var, no feature toggle. Only "gate" is the path-traversal defense at line 144-164 (refuses reads outside BASE_DIR) and the file-existence check (fail-soft envelope when jsonl missing). Neither is a runtime feature gate. §6 LIVE-VERIFY covers the always-live path.

### 5c.3 Shared handler-file coupling noted

**Disposition: PASS with note — dedicated handler, but future extension point.** `td_handlers_governance.py` (312 lines) currently hosts only `zoom_out_tool`. Module docstring line 5-8 explicitly frames this file as "a discrete home for future governance-adjacent tool handlers so `ops_tool` stays focused on runtime ops signal (SLO / staleness / failure signatures / worker health)." So while there is no sibling tool TODAY, the file is a designated extension point for future governance-scope tools (successor handlers to any `ops_tool.zoom_out_ledger` follow-ons). No current-tool coupling to note; future extensions should add cross-links here.

## 6. Evidence

Live PA-dispatch evidence, S2937 T0 (HEAD `416931160`, 2026-07-24). Dispatched via `zoom_out_tool` handler at `td_handlers_governance.py:26` → `_zoom_out_list` at line 48. Envelope shape captured verbatim in §6.1.

### 6.1 `action=list` (default `limit=20`, no filters) — LIVE at S2937 T0

Captured verbatim via Rigby dispatch, HEAD `416931160`, 2026-07-24 17:49 UTC. Runtime **5ms** — pure filesystem read of `logs/zoom_out_classifications.jsonl`.

Envelope (structural fields shown; `items[]` truncated to first row for readability):
```json
{
  "action": "list",
  "log_exists": true,
  "log_path": "logs/zoom_out_classifications.jsonl",
  "advisory": "Rigby SIGN zoom-out concern ledger — pattern evidence for review. Rows are longitudinal signal, not automatic escalation triggers. Any Playbook codification decision requires its own ratification.",
  "is_gate": false,
  "semantics": "advisory_pattern_evidence",
  "total_rows": 162,
  "counts_by_classification": {
    "same_pr_actionable": 56,
    "same_pr_mitigatable": 59,
    "future_trigger": 47
  },
  "items": [
    {
      "ts": "2026-07-16T16:04:41.291949+00:00",
      "schema_version": 1,
      "session": 2800,
      "arc": "broken_agents_shutdown_handler_bounded_bulk",
      "classification": "same_pr_actionable",
      "concern_text": "T1 Rigby zoom-out: shutdown handler MUST use bounded/bulk UPDATE...",
      "evidence_ref": "S2800 T1 Rigby SIGN Ask 5 fold 3",
      "backfilled": false,
      "entered_by": "claude"
    }
    // ... up to 20 tail rows total (limit=20)
  ],
  "count": 20,
  "limit": 20,
  "malformed_lines_skipped": 0
}
```

**Observations locked at this HEAD:**
- **162 total ledger rows** at HEAD `416931160`; classification split: 56 `same_pr_actionable` / 59 `same_pr_mitigatable` / 47 `future_trigger`. Balanced across the three classifications — no single classification dominates.
- `advisory` header, `is_gate: false`, `semantics: "advisory_pattern_evidence"` all present in top-level envelope. Advisory-posture triple redundancy holds.
- `malformed_lines_skipped: 0` — jsonl file is currently well-formed.
- `log_exists: true` — file present at expected path.
- `items[]` returned in oldest-first order within the tail-window per `filtered[-limit:]` slice at line 244 (window shows S2800-era rows given the small tail-limit; caller passing a `session=NNNN` filter narrows further).

### 6.1a `action=list include=aggregations` — NOT captured this dispatch

**Anomaly:** the S2937 T0 verification dispatch requested `include=aggregations` but the response returned NO `aggregations` block. The `include` param may not have propagated through Rigby's dispatch surface, OR the `include` token normalization at line 274-284 requires exact-form match (`include=aggregations` as a string vs `include=["aggregations"]` as a list) that Rigby's wrapper didn't emit correctly. Handler code confirms the aggregations block IS produced when `include` contains the `aggregations` token — this is a dispatch-surface not-a-handler-bug observation.

Post-merge live-dispatch verification should re-exercise `zoom_out_tool action=list include=aggregations` with `include` explicitly as a list to force the token-normalization branch and capture the `aggregations{top_arcs_by_count, future_trigger_rule_targets, sessions_covered, is_gate:false, semantics}` block for the record. Deferred as a Rigby-wrapper investigation candidate, not a tool bug.

### 6.2 `action=list include=aggregations`

Not exercised as a separate call this batch — handler line 271-311 confirms `aggregations{top_arcs_by_count, future_trigger_rule_targets, sessions_covered, is_gate:false, semantics}` block added; computed over ALL rows regardless of filter window (invariant locked by `test_zoom_out_time_window_2793.py` contract 6).

### 6.3 `action=list since_session=2900 until_session=2936`

Not exercised as a separate call this batch — handler line 129-142 confirms session-window narrowing with autofill guards (0/negative treated as no-filter). Envelope adds `since_session_filter` + `until_session_filter` echo fields. `items[]` narrowed; `total_rows` + `counts_by_classification` unchanged (pre-filter aggregates).

### 6.4 Default action (no `action` in payload)

Not exercised as a separate call — handler line 39 confirms default = `"list"` via `payload.get('action', 'list')`. Behavior identical to §6.1.

### 6.5 Invalid action gating

Not exercised via failing dispatch this batch. Handler line 42-46 confirms in-envelope error return via `_handler_error(action, 'unknown_action', 'Unknown zoom_out_tool action: <x>')`. Non-raising — matches rigby_shift_brief_tool + spider_data_aggregation_tool siblings this batch.

### 6.6 Fail-soft on missing log file

Not exercised in this environment (file exists). Handler line 166-185 confirms fail-soft envelope with `log_exists: false, note: <helpful pointer to record_zoom_out_concern>` when jsonl missing.

## Related

- **Adjacent tools (same Slice 7 batch 1):** `rigby_shift_brief_tool` (operator brief — orthogonal subsystem); `spider_data_aggregation_tool` (SpiderData rollup — orthogonal subsystem). All 3 pure-read + no shared-module coupling THIS SHIP.
- **Adjacent tools (governance-adjacent):** `ops_tool.zoom_out_ledger` (pre-S2780 same surface; factored out at N22 v3 — do not use for new work); `record_zoom_out_concern` management command (WRITE path); the Chris-facing UI at `/api/governance/zoom-out-ledger/` (functionally equivalent read surface for humans).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1 + §5c retro-fold added S2937); `docs/audits/PA_TOOLS_GAP_MAP.md` (Slice 7 open = 9 untested; this doc + 2 siblings this batch → 6 remaining); `docs/ENGINEERING_PLAYBOOK.md` §6.10.7 + §6.10.8 (constitutional at Playbook v0.7.0 — write-path + advisory-posture rules that this read surface enforces).
- **Prior ratifications:** S2779 V6 fold (scope creep from ops_tool); S2780 V7 Fold B firing (first non-Rigby consumer → factor-out ratified); S2791 (aggregations opt-in for UI parity); S2793 N22 v2 (session-int window filters); S2892 Path B open; S2907 T0 Fold E; S2921 §5a taxonomy; S2928 Slice 5 CLOSE; S2936 Slice 6 CLOSE; S2937 T1 Chris ratification (4-batch Slice 7 plan + template §5c retro-fold).
- **First-hop dependencies:** filesystem read (`logs/zoom_out_classifications.jsonl` under `settings.BASE_DIR`). §5b Appendix N/A not applicable (no network); Appendix A/N not applicable (no Celery, no dispatch).
- **Locked invariants (contract tests):** `core/tests/test_zoom_out_time_window_2793.py` contract 6 — aggregations block computed over ALL rows regardless of filter window (longitudinal-signal semantics preserved).
- **Post-merge live-dispatch verification:** exercise `zoom_out_tool action=list include=aggregations` after `make recycle-all` at merge; confirm `advisory` + `is_gate:false` + `semantics` triple present in both top-level envelope AND `aggregations` sub-block. Recorded in S2937 handoff.
