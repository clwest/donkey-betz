---
title: "CCL v2 Full-Text Search + Rigby-Follow-up Guardrails Ratification Record (2026-07-11)"
status: active
authority: ratification-record
session_added: 2771
ratification_date: 2026-07-11
ratifier: chris
routing: rigby-pa-chat joint SIGN (design + post-code HTTP shape verify + meta-critique solicited) + Chris N14 selection + Chris D-verdict + Chris directive to include Rigby follow-up in same PR
scope: S2771 — N14: extend close_ceremony_ledger view + S2769 filter row with case-insensitive full-body substring search across handoff bodies. text_match_count per item indicates match density. Applied AFTER cheap filters for perf. Bonus (Rigby-follow-up): applied_filters echo block + skipped_count field surface silent partial results.
serves_arc: platform observability (Ops Console at Workspace → System → Ops); durability + information-retrieval on the 961-handoff corpus
precedent_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger.md (S2763 — v1 ledger view)
  - docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger_v2.md (S2767 — v2 hover-preview + drawer)
  - docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_search_filter.md (S2769 — v2 filters + total_available)
  - docs/research/implementation/RATIFICATION_2026-07-11_health_summary_partial_recycle.md (S2770 — evidence-to-alert loop closure)
ratified_documents:
  - core/views_ops_console.py (amended — close_ceremony_ledger accepts text param; two-phase filter: cheap filters build matched set, then optional text-scan reads full bodies; new applied_filters + skipped_count fields in response)
  - frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx (amended — LedgerFilters extended with text field; 200ms debounced input in the S2769 filter row; text_match_count optional field on CloseCeremonyItem; match-count chip renders next to envelope badge when text search is active)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2771 open freshness (retired-pin dispatch to Rigby) — verdict FRESH · SHA a6c4a47c437b matches HEAD (FIFTH corroboration cycle after PLAYBOOK-7.4.4; recycle log top three all N7-enriched with partial_recycle=false)
  - S2771 design SIGN (Rigby, pin pa-bef24c8c42d3461c) — PASS on all three: Q1 (case-insensitive default), Q2 (handoff bodies only for MVP), Q3 (cheap filters before text scan)
  - S2771 post-code shape verify + meta-critique SIGN (Rigby) — PASS on shape (text_match_count conditional; baseline unchanged); genuine meta-critique raised 4 concerns (unversioned params, silent fail-soft, prod topology, ops surface security drift) with concrete follow-up ask
frozen: true
---

# CCL v2 Full-Text Search + Rigby-Follow-up Guardrails — Ratification Record

Frozen canonical record of Chris's ratification of the S2771 N14 text-search extension on 2026-07-11 plus the same-PR guardrail follow-up Rigby raised in her meta-critique. Turns the 961-handoff corpus into a searchable operator surface. Append-only.

---

## §1. Context

- **Ratification date:** 2026-07-11 (America/Denver operator timezone)
- **Scope:** operator-surface information-retrieval extension of the S2769 filter row (N14 in S2770 candidate menu).
- **Motivation:** the S2769 CCL v2 filter row narrows by session_range / envelope-only / date_range. When Chris (or the AI helper) asks "which sessions talked about PLAYBOOK-7.4.4" or "where was N7 discussed," those filters can't help. N14 adds a text input that filters the ledger to sessions whose handoff BODY contains the substring. Search-as-you-type feel with 200ms debounce.
- **Ratifier:** Chris (candidate selection at S2771 open: "N14 approved, route joint SIGN through Rigby" — plus implicit approval on Rigby-follow-up inclusion when I incorporated `applied_filters` + `skipped_count` after her meta-critique).
- **Fifth cycle after PLAYBOOK-7.4.4 codification:** S2771 open verified FRESH · SHA-match at `a6c4a47c437b` (S2770 close). Recycle log top three (S2770/S2769/S2768) all N7-enriched with `partial_recycle: false`. The rule continues to hold; the N11 override remains dormant (correct — no partials in the wild yet).

---

## §2. Ratified Deliverables

### §2.1 `core/views_ops_console.py::close_ceremony_ledger` — text param + two-phase filter

New optional query param `text` (string). Behavior:

1. **Cheap filters first.** The existing S2769 filters (`session_min`, `session_max`, `envelope_only`, `date_from`, `date_to`) narrow the candidate entries before the text scan runs. This is the Rigby Q3 PASS lean: text scan is 30x more expensive than any cheap filter, so applying it to a pre-narrowed set is the right perf/complexity trade.

2. **Case-insensitive substring scan.** `body.lower().count(text_needle)` per entry — Python string method, no regex, no ReDoS risk. Blank string treated as absent (`text=` in URL means "no text filter").

3. **Per-item `text_match_count` field.** Absent from response when text filter is not set (backward-compat with S2769 clients). Present as an integer > 0 when text filter matched.

4. **Zero-match entries dropped from result.** Only entries with `count > 0` survive. `total_available` reflects the post-text-filter count.

5. **Fail-soft on unopenable files.** OSError during body read → skip entry, increment `skipped_count`.

Performance (empirical):
- Full-corpus scan (~961 handoffs, ~8.8MB) case: 132–411ms depending on term length and hit density.
- Narrowed-set scan (session_min applied first): 6–30ms — the promised perf win.

### §2.2 Rigby-follow-up guardrails: `applied_filters` echo + `skipped_count`

After the initial N14 SIGN + implementation, I asked Rigby "is there anything about the pattern we've been shipping that you would push back on if I asked you fresh today?" She raised 4 substantive concerns (recorded in §4.4). Her concrete follow-up ask: add `applied_filters` (echo of which filters fired) + `skipped_count` (surface silent partial results) as a low-cost guardrail without complicating the MVP UI.

Adopted in the same PR:

- `applied_filters` — a dict-shaped echo of the filter dimensions that actually fired. Empty dict when no filters active. Populated with exact values otherwise. Rigby's rationale: over time ad-hoc query params risk becoming an unversioned API contract; echoing the applied set lets both operators and UI see exactly what fired without re-parsing the query string.

- `skipped_count` — integer count of unopenable files encountered during the text scan. Present in response ONLY when a text scan ran; absent otherwise. Rigby's rationale: silent fail-soft IO masks real regressions; a surfaced counter makes partial results traceable.

Zero UI impact — Rigby explicitly asked "without complicating the MVP UI." Both fields are for operators + future UI + regression detection.

### §2.3 `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — text input + debounce + match-count chip

Three changes:

1. `LedgerFilters` interface gains `text: string`. `hasActiveFilters` + `buildLedgerQueryString` extended. `resetLedgerFilters` clears text.

2. **200ms debounced text state.** The text input updates `ledgerFilters.text` on every keypress (feels live), but a `useEffect` syncs `debouncedText` 200ms after the last keypress, and `ledgerQueryString` uses the debounced value. Keystroke storms don't spam the backend.

3. **Text search input in the filter row.** `<input type="search" placeholder="search text…" />` sits after the date range inputs, flex-1-grow with a min-width. Same amber-focus styling as the other inputs.

4. **`text_match_count` optional field on `CloseCeremonyItem`.** Rendered as a small primary-tinted chip next to the envelope badge when set: "N matches" (or "1 match"). Only appears when text search returned a per-item count.

---

## §3. What Was NOT Changed

- No new URL route. Extended existing `/api/ops/close-ceremony-ledger/` in place.
- No changes to `_HANDOFFS_ROOT` / `_ENVELOPES_ROOT` / `_safe_relpath` safety pattern from S2763.
- No changes to LedgerRow hover-preview or click-to-open drawer (S2767 v2 preserved verbatim).
- No changes to N7 recycle emitter, N11 PARTIAL_RECYCLE verdict, or any other sibling surface.
- No new backend dependency; no new frontend package.
- No text-in-envelope-body search — MVP is handoff bodies only per Rigby Q2 PASS.

---

## §4. Rigby SIGN Summary

Joint SIGN routed via pin `pa-bef24c8c42d3461c` (label `s2771-ccl-v2-full-text-search`); a second round-trip on the same pin covered post-code shape verify + solicited meta-critique.

### §4.1 Q1 — Case sensitivity
- **Rigby verdict:** PASS.
- **Content:** case-insensitive default. "One mental model: 'find the thing,' not 'grep with flags.'"

### §4.2 Q2 — Search corpus
- **Rigby verdict:** PASS.
- **Content:** handoff bodies only for MVP. Keeps semantics clean (one row = one session's handoff); avoids mixing meta/ratification text into narrative search.

### §4.3 Q3 — Filter interaction order
- **Rigby verdict:** PASS.
- **Content:** apply cheap filters first, then text scan on the narrowed set. Right perf/complexity trade for an operator surface.

### §4.4 Post-code shape SIGN + meta-critique
- **Rigby shape verdict:** PASS.
- **Content:** all 4 HTTP smoke variants passed; `text_match_count` conditionally present only when `text` is set; baseline unchanged.
- **Meta-critique (unprompted structure — I asked her to zoom out on the ops-console pattern):**
  1. Ad-hoc query params risk becoming an unversioned API contract surface. Mitigation: `applied_filters` echo. **Adopted in same PR.**
  2. Silent fail-soft file IO can mask real regressions. Mitigation: `skipped_count` field. **Adopted in same PR.**
  3. Local filesystem scanning fine now; prod topology (horizontal scaling + ephemeral FS) could bite later. Mitigation: keep scan as stepping-stone toward SQLite/FTS or Postgres index. **Recorded as §7 forward-carry.**
  4. Ops endpoints accumulating power/visibility — category tends to drift into "debug everything" and leak internal paths/content. Mitigation: periodic `auth_regression` smoke suite + single "ops operator" permission gate for `/api/ops/*`. **Recorded as §7 forward-carry.**

Chris's context question at the same time — "Is Rigby getting to know the system better as well?" — was the correct 4th reason I initially missed for why her recent SIGN cycles had been all-PASS: she's accumulated institutional model from S2761 → S2765 → S2768 → S2770 → S2771 (five substrate decisions in a row on the same surface). The meta-critique proved she still has substantive pushback when asked to zoom out.

---

## §5. Empirical smoke tests

### §5.1 Django shell — 5 text-search combinations
- `text=PLAYBOOK-7.4.4` — 5 sessions (S2766-2770), match counts 2/3/5/5/7 (natural gradient with S2766 ratification highest). 255ms.
- `text=N7` — 4 sessions. 132ms.
- `text=tenant boundary` + `session_min=2755` — 10 sessions, 6ms (cheap-filter-first perf win: 42x faster than full-corpus scan).
- `text=nonsense_zzzzzzz` — 0 sessions, correct empty. 237ms (full-corpus scan even with no matches).
- Baseline no-text — `text_match_count` correctly absent from all items.

### §5.2 Django shell — Rigby follow-up field checks
- `applied_filters` echoes exactly the fired dimensions with their values.
- Empty `applied_filters: {}` when no filters active.
- `skipped_count` present in response only when text scan ran; absent from baseline queries.

### §5.3 Vite production build
- Command: `npm run build`
- Result: passed, no TS errors. Bundle main +~2 KB (text input, debounce effect, match-count chip).

### §5.4 Rigby HTTP smoke via `http_smoke_test`
- 4 variants (PLAYBOOK-7.4.4, N7, tenant boundary + session_min, baseline).
- PASS on all: `text_match_count` conditionally present per contract; baseline shape unchanged.

---

## §6. Post-ratification bindings

- **Head at ratification:** filled at merge.
- **Merged PR:** filled at merge.
- **Workspace mirrors (S2754a twin-canonical rule):**
  - Governance envelope mirror → `RUR-C1 Tenant Boundary Lockdown` workspace `fcd7e683-3bfe-4d35-9704-0e54dd587ea1`.
  - Content mirror → same workspace.
- **PLAYBOOK-7.4.4 dogfood:** `make recycle-all` invoked post-merge — sixth consecutive cycle where the constitutional rule fires; fourth cycle emitting N7-enriched entries.

---

## §7. Forward carry

- **Rigby meta-critique #3: prod topology assumptions.** Filesystem scanning is fine on the current single-node local runtime, but ops-console-on-horizontal-workers or ephemeral-FS deployments would make substring scan flaky (workers seeing partial trees). Not urgent — Donkey Betz single-user pre-prod per `project_single_user_pre_prod_operating_context`. When prod topology changes: build a lightweight index (SQLite FTS or Postgres tsvector table with `session_number` + `handoff_body`). Do NOT proactively build; wait for the topology change or a first "scan is slow" observation.
- **Rigby meta-critique #4: ops-surface security drift.** `/api/ops/*` endpoints accumulate visibility over time (verdicts, staleness warnings, recycle events, close-ceremony ledger, doc paths). Not seeing issues today (login_required on all), but the category drifts if unattended. Mitigation candidates: periodic auth-regression smoke suite (all `/api/ops/*` return 401 without auth) + a distinct "ops operator" permission group. Two-trigger threshold for codification not met.
- **N15 (session-open freshness verdicts persisted to JSONL) still on menu.** N14 shipped alongside evidence-to-alert loop (N11); N15 would give us trend detection on top of that.
- **First observed real partial-recycle event** — still watching. N11 tile-alert path remains dormant.
- **N9 dedicated `/api/ops/doc-preview/` endpoint** — hover-preview bandwidth signal still unmeasured. N14 might drive more traffic; check the doc-content endpoint's request rate at S2775 close.
