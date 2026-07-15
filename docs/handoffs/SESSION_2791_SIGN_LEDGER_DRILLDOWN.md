# Session 2791 — Sign Ledger drill-down (aggregations + per-row modal)

**Ship SHA:** `e5be876fe` · **PR:** [#3195](https://github.com/clwest/donkey-betz-platform/pull/3195) · **Date:** 2026-07-15

---

## §1 What shipped

Extended the Chris-facing Sign Ledger UI (`?tab=system&sub=sign-ledger`)
from a flat list into a drill-down surface — clickable arc chips filter
the list, future-trigger rule-target chips summarize PLAYBOOK amendment
pressure, and per-row click opens a modal exposing full concern text,
click-to-copy evidence, and sister rows (other folds sharing the same
arc). Advisory posture repeated three times inside the modal (header
subtitle, footer strip, aggregations block markers) to defend against
the "dashboard gravity" risk Rigby raised in T1 SIGN.

**Backend (2 files):**

- `core/services/td_handlers_governance.py` — added `re` import + module-
  level `_PLAYBOOK_RULE_RE` (matches `PLAYBOOK-\d+\.\d+(\.\d+)?`,
  case-insensitive). `_zoom_out_list` now parses an opt-in `include`
  payload param (accepts comma-separated string or list; unknown tokens
  are no-ops). When `aggregations` is requested, appends an
  `aggregations` block to the response with `top_arcs_by_count` (top
  20, descending), `future_trigger_rule_targets` (regex-parsed rule IDs
  from `concern_text` of `future_trigger` rows only), `sessions_covered`
  (sorted distinct sessions), and redundant `is_gate: false` +
  `semantics: "advisory_pattern_evidence"` markers.
- `core/views_governance.py` — added `'include'` to
  `_GOVERNANCE_ALLOWED_PARAMS__ZOOM_OUT_LEDGER` frozenset + one-line
  payload passthrough. Without the allowlist add, the endpoint would
  400 before payload build (Row 48 same_pr_actionable).

**Frontend (1 file):**

- `frontend/src/pages/workspace/tabs/ZoomOutLedgerSection.tsx` — grows
  from ~325 lines to ~610 lines (net +286):
  - `ZoomOutAggregations` type + `aggregations?` field on response type
  - `buildQueryString` now always requests `include=aggregations` (so
    chips stay populated even after filtering — aggregations are
    computed over the full ledger server-side)
  - Two chip strips below the existing counts row: top-arc chips
    (clickable, toggles `arc` filter, active state highlighted) +
    future-trigger rule-target chips (informational, amber palette)
  - Each row is now a `<button>` with `line-clamp-2` on `concern_text`;
    click opens `ZoomOutRowDetailModal`
  - New `ZoomOutRowDetailModal` component reusing the
    `ConversationDetailModal` overlay pattern
    (`fixed inset-0 z-50 flex items-center justify-center p-4
    bg-black/70 backdrop-blur-sm` container + `bg-dark-card` panel;
    S2791 T1 SIGN Row 49 same_pr_mitigatable fold adopted — no shadcn
    Dialog primitive exists in the tree)
  - Modal exposes full `concern_text` (whitespace-preserved), meta
    strip (session/classification/timestamp/backfilled/entered_by),
    arc, click-to-copy `evidence_ref` (green check flashes on success;
    silent no-op on clipboard rejection), sister-rows list (rows
    sharing this row's arc, click to pivot the modal). Esc key +
    backdrop click close.

**Tests (1 new file):**

- `core/tests/test_zoom_out_aggregations_2791.py` — 14 tests, 4 classes:
  - `ZoomOutAggregationsShapeTest` — Contract 1: aggregations shape,
    arc descending, rule-target future-trigger-scoping (mentions in
    same_pr_actionable rows explicitly excluded), sessions sorted
    distinct, aggregations computed over full ledger even with arc
    filter applied.
  - `ZoomOutAggregationsAdvisoryPreservationTest` — Contract 2: outer
    `is_gate:false` + `semantics` preserved with aggregations;
    aggregations block ALSO carries the markers (belt-and-suspenders
    per S2780 V5 fold); missing log branch still returns advisory
    markers.
  - `ZoomOutAggregationsBackwardCompatTest` — Contract 3: no `include`
    → no `aggregations` key (byte-for-byte S2780 shape); unknown token
    no-ops; list form and comma-separated string both parsed.
  - `ZoomOutAggregationsViewAllowlistTest` — Contract 4: `include`
    accepted at the view layer; genuinely-unknown params still return
    400 with `code=unknown_query_params`.

**Full 13-suite regression: 249 tests OK** (235 prior + 14 new).

---

## §2 Novel-precedent moments

### 2.1 First Rigby-modified spec adopted whole-cloth

Prior T1 SIGN cycles produced same-PR mitigations layered onto Claude-
drafted specs. S2791 T1 was the first cycle where both non-trivial
modifications Rigby proposed (Row 48 backend allowlist reality-check
+ Row 49 modal-pattern reuse) were adopted as-shipped — the modal
implementation section of the spec was rewritten from "shadcn Dialog /
native `<dialog>`" to "reuse `ConversationDetailModal` overlay" between
draft and code. Evidence-admission per PLAYBOOK-6.10.9 supplied all
three folds inline with file+line pointers.

### 2.2 First aggregation-drift regression pattern

The `future_trigger` fold Rigby surfaced (Row 50) was novel: not
"defer this shape decision to a future arc" but "encode a guardrail
that will fire IF a future consumer treats aggregation output as gate
input." Row 50 is the first `future_trigger` classification whose
trigger condition is expressed as a same-PR regression test rather
than an external observation. The test
`test_aggregations_block_repeats_advisory_markers` explicitly asserts
`is_gate:false` inside the aggregations dict — if a future PR removes
that marker (whether by accident or as an intentional gate-i-fication),
the regression fails loud.

### 2.3 Chip strip informational-only pattern

The `future_trigger_rule_targets` chip strip renders as amber
non-clickable spans — the first UI element in the Sign Ledger that
exists purely to summarize accumulation pressure toward specific
PLAYBOOK amendments (e.g. `PLAYBOOK-6.10.11: 2` indicates two future-
trigger folds have referenced that rule ID). It does not filter, does
not gate, does not link to an amendment envelope. Tooltip repeats
"Advisory evidence — codification requires ratification." to preempt
the read as an approval mechanism.

---

## §3 T1 SIGN cycle

- **Pin:** `pa-24fcf1b32a314838` (fresh mint at S2791 open, label
  `s2791-sign-ledger-drilldown`).
- **Turn 1 dispatch:** Draft spec + 4 tool-grounded verify requests
  (repo tree, search, 2× read_file) + fold classification directive +
  zoom-out ask. Response body truncated by shell tail; re-dispatch
  returned verbatim §1..§5.
- **Turn 2 dispatch:** ledger persist attempt via
  `zoom_out_tool.record` — Rigby correctly refused (read-only tool
  surface). Fell back to direct `python manage.py
  record_zoom_out_concern` × 3.
- **Tool_runs:** 5 non-empty on Turn 1 (repo_tool tree, search,
  read_file × 3) — anti-rubber-stamp check per
  `feedback_verify_rigby_tool_runs_before_trusting_sign` passes.
- **Response length:** ~55 lines, no truncation — S2790 tightened-
  prompt pattern held (sample size 2 post-Row 44).
- **Folds classified + persisted BEFORE D-verdict per PLAYBOOK-6.10.8/9:**
  - Row 48 `same_pr_actionable` — backend allowlist add (adopted)
  - Row 49 `same_pr_mitigatable` — modal pattern reuse (adopted)
  - Row 50 `future_trigger` — aggregation drift guardrail (encoded as
    regression test)
- **Chris D-verdict:** "yes build it"

---

## §4 Ledger delta

- **Rows at S2790 close:** 47 (20 / 16 / 11)
- **Rows at S2791 close:** 50 (21 / 17 / 12)
- **Delta:** +3 rows, all arc `sign_ledger_drilldown_s2791`, all
  `entered_by=claude`, all live capture (not backfilled)

---

## §5 Twin-pointer card

📁 **Repo `/` + `/docs/` — S2791 artifacts:**

- **Ship backend:** `core/services/td_handlers_governance.py` (~50 lines added)
- **Ship view:** `core/views_governance.py` (+3 lines: allowlist + passthrough)
- **Ship frontend:** `frontend/src/pages/workspace/tabs/ZoomOutLedgerSection.tsx` (+286 net)
- **Tests:** `core/tests/test_zoom_out_aggregations_2791.py` (344 lines, 14 tests)
- **Handoff:** `docs/handoffs/SESSION_2791_SIGN_LEDGER_DRILLDOWN.md` (this file)
- **Predecessors:** S2790 (time-travel), S2789 (pilot-gates), S2780 (Sign Ledger UI shipped)

🖥️ **Workspace UI — `/workspaces` surface:**

- **System / Sign Ledger sub-tab** (`?tab=system&sub=sign-ledger`) —
  now has:
  - Top-arc chips row (top 8 arcs, click to filter)
  - Future-trigger rule-target chips row (informational, amber)
  - Per-row click → detail modal (full concern, sister rows,
    click-to-copy evidence)
- **Live surfaces at close:**
  - `logs/zoom_out_classifications.jsonl` — 50 rows (21 / 17 / 12)
  - `logs/session_freshness.jsonl` — grew by 1 at S2791 open
  - `logs/recycle_events.jsonl` — +1 new event (`sha=e5be876fe814`)

---

## §6 Forward-carry

**Immediate follow-ups (S2792+):**

- **Chris browser eyeball** at
  `http://localhost:8000/workspace?tab=system&sub=sign-ledger` — click
  a row, click a top-arc chip, verify future-trigger rule-target
  chips render. Local Django serves `frontend/dist/` post-`npm run
  build` (already built at ship SHA `e5be876fe`).
- **PA-tool surface parity** — `zoom_out_tool.list` (Rigby's read
  path) does NOT yet emit the `aggregations` block. If Rigby ever
  needs arc-count or rule-target summaries for her own SIGN reasoning,
  extend `_zoom_out_list` payload plumbing to accept `include` from
  the PA tool schema too (currently governance REST endpoint only).

**Deferred (unchanged from S2790 forward-carry, plus one new):**

- Row 50 (`future_trigger`) — aggregation-drift guardrail is now
  encoded in `test_aggregations_block_repeats_advisory_markers`. If
  the assertion ever needs to change, that is the amendment trigger.
- Every other item in `00-START-NEXT-SESSION.md` §"Deferred (waiting
  on triggers, not calendar)" carries forward.

---

## §7 Rebindings

- **Wrapper pin:** `pa-24fcf1b32a314838` (retired at S2791 close,
  `force=true`, twenty-second consecutive per S2770+ pattern).
- **HEAD:** `e5be876fe` post-merge; cascade PR advances to next SHA.

---

## §8 Post-merge cascade

- `make recycle-all` executed post-merge per PLAYBOOK-7.4.4 —
  **thirtieth close-cycle** at `sha=e5be876fe814`, all workers
  restarted clean.
- Docs cascade (this PR): `build_docs_index` + `build_docs_provenance`
  regenerate `docs/INDEX.md` + `docs/_provenance.json`; refresh
  `00-START-NEXT-SESSION.md` with S2791 CLOSED banner + S2792
  candidate menu.
