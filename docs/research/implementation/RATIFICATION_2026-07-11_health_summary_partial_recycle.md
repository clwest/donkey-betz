---
title: "health_summary PARTIAL_RECYCLE verdict Ratification Record (2026-07-11)"
status: active
authority: ratification-record
session_added: 2770
ratification_date: 2026-07-11
ratifier: chris
routing: rigby-pa-chat joint SIGN (design + post-code shape verify) + Chris N11 selection + Chris D-verdict ("if you lean that way" — implicit approval on Rigby-PASSed leans)
scope: S2770 — N11: extend the S2761 Ops Health tile's health_summary composition with a fifth backend action call (recent_recycles limit=1) and a verdict override — when the base version verdict is STALE_* AND the newest recycle event has partial_recycle=true (S2768 N7 evidence), verdict becomes PARTIAL_RECYCLE and a new partial_recycle_details field carries the surviving_processes list plus recycle_sha_short.
serves_arc: PLAYBOOK-7.4.4 evidence-to-alert loop closure (N7 recorded per-role recycle diff; N11 makes partial recycles operator-visible on the Ops Health tile itself)
precedent_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile.md (S2761 — Ops Health tile composition)
  - docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_recent_recycles.md (S2765 — JSONL emitter + read handler)
  - docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_6_0.md (S2766 — codified PLAYBOOK-7.4.4)
  - docs/research/implementation/RATIFICATION_2026-07-11_recycle_emitter_worker_pids.md (S2768 — N7 emitter enrichment)
  - docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_search_filter.md (S2769 — CCL v2 filters)
ratified_documents:
  - core/views_ops_console.py (amended — health_summary calls recent_recycles limit=1; adds PARTIAL_RECYCLE verdict override; conditionally adds partial_recycle_details field; typing imports)
  - frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx (amended — OpsHealthSummary.verdict enum gains 'PARTIAL_RECYCLE'; new optional partial_recycle_details field; amber color mapping in tile dot + text; new surviving-processes warning row below tile header)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2770 open freshness (retired-pin dispatch to Rigby) — verdict FRESH · SHA 7013f9893878 matches HEAD (FOURTH corroboration cycle after PLAYBOOK-7.4.4; recycle log top three all N7-enriched)
  - S2770 design SIGN (Rigby, pin pa-fa4fcfa52f91490e) — PASS on all three: Q1 (strict AND on trigger), Q2 (newest recycle only), Q3 (legacy → treat as false)
  - S2770 post-code shape SIGN (Rigby, same pin) — PASS: baseline shape unchanged; verdict enum extended additively; partial_recycle_details correctly absent when not PARTIAL_RECYCLE
frozen: true
---

# health_summary PARTIAL_RECYCLE verdict — Ratification Record

Frozen canonical record of Chris's ratification of the S2770 N11 health_summary override on 2026-07-11. Closes the evidence-to-alert loop that S2768 N7 opened — the JSONL log now RECORDS partial-recycles, and as of N11, the Ops Health tile SURFACES them the moment a partial coincides with stale processes. Append-only.

---

## §1. Context

- **Ratification date:** 2026-07-11 (America/Denver operator timezone)
- **Scope:** operator surface — extends the S2761 health_summary composition (N11 in S2770 candidate menu).
- **Motivation:** S2768 N7 gave the recycle log a `partial_recycle` boolean per event. Nothing surfaced it. On the first real partial recycle (kernel panic mid-restart, `brew upgrade` mid-recycle, macOS SIGKILL of a hung worker, network hiccup during Celery worker init), the operator sees a red STALE_DAPHNE / STALE_CELERY / STALE_BOTH tile and has to spelunk `logs/recycle_events.jsonl` to notice the recycle itself was partial. N11 makes the tile speak directly: "PARTIAL_RECYCLE — celery_beat, daphne survived; run `make recycle-all` again."
- **Ratifier:** Chris (candidate selection at S2770 open: "Lets go with N11 if you lean that way" — implicit D-verdict conditional on Rigby joint SIGN, which PASSed all three asks with my leans intact).
- **Fourth cycle after PLAYBOOK-7.4.4 codification:** S2770 open verified FRESH · SHA-match at `7013f9893878` (S2769 close). Recycle log top three (S2769/S2768/S2767-smoke) all N7-enriched — the substrate is producing evidence continuously.

---

## §2. Ratified Deliverables

### §2.1 `core/views_ops_console.py::health_summary` — fifth call + verdict override + details field

Backend extension. Adds a fifth `_safe_call` to `recent_recycles` (limit=1) alongside the existing four (`version`, `tenant_boundary_violations`, `staleness_warnings`, `slo_status`). Verdict resolution logic:

```python
base_verdict = version.get('staleness_verdict') or 'UNKNOWN'
verdict = base_verdict
partial_details = None
if base_verdict in ('STALE_DAPHNE', 'STALE_CELERY', 'STALE_BOTH') and isinstance(recycles, dict):
    items = recycles.get('items') or []
    newest = items[0] if items else None
    if isinstance(newest, dict) and newest.get('partial_recycle') is True:
        verdict = 'PARTIAL_RECYCLE'
        partial_details = {
            'surviving_processes': newest.get('surviving_processes') or [],
            'recycle_sha_short': newest.get('sha_short') or '',
        }
```

Override fires ONLY when both conditions hold: base verdict is stale AND newest recycle event has `partial_recycle=true`. Legacy pre-N7 rows lack the field; `.get('partial_recycle')` returns None, does not equal True, override doesn't fire. Safest default — no false alarms for pre-N7 history.

`partial_recycle_details` field is conditionally added to the JSON response only when the override fires. Clients ignoring it are unaffected; clients that check for it (S2770 frontend) render the warning row.

Also added `from typing import Any, Dict` to the imports (previously not needed by this file).

### §2.2 Verdict enum extension

Before N11: `FRESH / STALE_DAPHNE / STALE_CELERY / STALE_BOTH / UNKNOWN` (5 states).
After N11: `FRESH / STALE_DAPHNE / STALE_CELERY / STALE_BOTH / PARTIAL_RECYCLE / UNKNOWN` (6 states).

The new state is not a base verdict; it's an override that fires strictly downstream of a stale base verdict. This means:
- `FRESH` cannot become `PARTIAL_RECYCLE` (correct — if processes are all fresh, whatever the last recycle did is irrelevant).
- `UNKNOWN` cannot become `PARTIAL_RECYCLE` (correct — we can't diagnose partial without a diagnosable base).
- Any `STALE_*` + newest `partial_recycle=false` (or legacy row) keeps its base verdict (correct — a subsequent clean recycle should un-alarm).

### §2.3 `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — verdict interface + amber tile + warning row

Frontend surfaces the override:

- `OpsHealthSummary.verdict` union type extended with `'PARTIAL_RECYCLE'`.
- New optional `partial_recycle_details?: { surviving_processes: string[]; recycle_sha_short: string }` field.
- Tile dot color: amber (`bg-amber-400`) for PARTIAL_RECYCLE, distinct from green FRESH and red STALE.
- Tile text color: amber (`text-amber-400`) for PARTIAL_RECYCLE.
- New warning row rendered below the tile header when `verdict === 'PARTIAL_RECYCLE' && partial_recycle_details`: "Partial recycle detected · surviving: `<role list>` · recycle sha `<sha7>` · run `make recycle-all` to fix."
- Warning row is amber-bordered / amber-tinted (subtle 30/5 opacity split), doesn't compete with the tile itself.

Zero regression risk to the existing FRESH / STALE_* rendering — new mappings are additive; existing conditions retain their exact prior semantics via the `verdict !== 'PARTIAL_RECYCLE'` guard in the fallback STALE branch.

---

## §3. What Was NOT Changed

- No new endpoint. Extended the existing `/api/ops/health-summary/` view in place.
- No changes to `_ops_version`, `_ops_recent_recycles`, `_ops_tenant_boundary_violations`, `_ops_staleness_warnings`, or `_ops_slo_status` handlers.
- No change to the S2768 N7 emitter or JSONL schema. This ship reads what N7 already writes.
- No change to CCL v2 filter code (S2769) despite touching the same file — additive.
- No changes to LedgerRow, hover-preview, or DocumentViewer wiring.

---

## §4. Rigby SIGN Summary

Joint SIGN routed via pin `pa-fa4fcfa52f91490e` (label `s2770-health-summary-partial-recycle`); post-code shape verify was a second round-trip on the same pin using `http_smoke_test`.

### §4.1 Q1 — Trigger semantics
- **Rigby verdict:** PASS.
- **Content:** `base_verdict in STALE_* AND newest.partial_recycle == true` correctly surfaces operator pain (staleness + you thought you recycled) while auto-suppressing historical partials that were later cleaned up by a subsequent successful recycle.

### §4.2 Q2 — Lookback scope
- **Rigby verdict:** PASS.
- **Content:** newest recycle only (`recent_recycles limit=1`). Keeps signal tight and non-noisy; a later clean recycle means the system probably recovered.

### §4.3 Q3 — Legacy row handling
- **Rigby verdict:** PASS.
- **Content:** missing `partial_recycle` ⇒ treat as `false`. Safest default; "unknown" would pollute the tile for all pre-N7 history without actionable value.

### §4.4 Post-code shape SIGN (HTTP smoke via `http_smoke_test`)
- **Rigby verdict:** PASS.
- **Content:** verdict = "FRESH" (still in enum); `partial_recycle_details` correctly absent (not FRESH ⇒ no override); all four existing summary fields present unchanged (`tenant_boundary_violations`, `staleness_warnings`, `slo_status`, `head_commit_sha_short`). Backward-compat verified.

---

## §5. Empirical smoke tests

### §5.1 Django shell — baseline
- Command: call `health_summary` directly against the live process.
- Result: verdict `FRESH`, `partial_recycle_details` absent, TBV total 7, STW total 1, SLO total 8 (0 breach). Matches the S2769-close operator state (all workers fresh; PLAYBOOK-7.4.4 hold).

### §5.2 Django shell — simulated STALE_BOTH + partial=true
- Setup: `unittest.mock.patch` on `OpsHandlersMixin._handle_ops` returning `{staleness_verdict: 'STALE_BOTH'}` for version and `{items: [{partial_recycle: true, surviving_processes: ['celery_beat', 'daphne'], sha_short: 'abcdef123456'}]}` for recent_recycles.
- Result: verdict `PARTIAL_RECYCLE`, `partial_recycle_details = {surviving_processes: ['celery_beat', 'daphne'], recycle_sha_short: 'abcdef123456'}`. **Override fires correctly.**

### §5.3 Django shell — simulated STALE_DAPHNE + partial=false (subsequent clean recycle)
- Setup: version returns STALE_DAPHNE; recent_recycles returns `partial_recycle: false`.
- Result: verdict stays `STALE_DAPHNE`, `partial_recycle_details` absent. **Override correctly does NOT fire.**

### §5.4 Django shell — simulated STALE_CELERY + legacy pre-N7 row
- Setup: version returns STALE_CELERY; recent_recycles returns a row with no `partial_recycle` field (pre-N7 shape).
- Result: verdict stays `STALE_CELERY`, `partial_recycle_details` absent. **Legacy fallback correct.**

### §5.5 Vite production build
- Command: `npm run build`
- Result: passed 3.25s, no TS errors. Bundle unchanged (main +~1 KB for new verdict cases and warning row).

### §5.6 Rigby HTTP shape smoke
- Command: `http_smoke_test` GET `/api/ops/health-summary/`
- Result: PASS. Response verdict `FRESH`, `partial_recycle_details` absent, all four legacy summary fields present.

---

## §6. Post-ratification bindings

- **Head at ratification:** filled at merge.
- **Merged PR:** filled at merge.
- **Workspace mirrors (S2754a twin-canonical rule):**
  - Governance envelope mirror → `RUR-C1 Tenant Boundary Lockdown` workspace `fcd7e683-3bfe-4d35-9704-0e54dd587ea1`.
  - Content mirror → same workspace.
- **PLAYBOOK-7.4.4 dogfood:** `make recycle-all` invoked post-merge — fifth consecutive cycle where the constitutional rule fires; third cycle to produce N7-enriched entry.

---

## §7. Forward carry

- **First observed real partial-recycle event** — still not observed. N11 makes the alerting path exist; the empirical trigger for the UI badge (N10, still deferred) is the same event. When it lands, both N10 and N11 alert on the same signal from different angles (N11 in the tile itself; N10 in the recent-recycles list row). Watch during S2770→S2780 arc.
- **`recycle_events.jsonl` retention policy** — the log grows unbounded (one line per recycle). At 5 close-cycles / day that's ~40/week / ~2k/year. Reader is fine (tail read); size not a concern yet. If it becomes one, tail-truncate to last 500 entries as a preventative maintenance step. Not urgent.
- **Verdict enum documentation** — Ops Health tile now supports 6 verdicts. Not codified as a Playbook rule; the enum grows organically. If a third override state gets proposed, document the base-vs-override distinction in Playbook Chapter 8 (currently STUB).
