---
title: "Close-Ceremony Ledger v2 Search + Filter Ratification Record (2026-07-11)"
status: active
authority: ratification-record
session_added: 2769
ratification_date: 2026-07-11
ratifier: chris
routing: rigby-pa-chat joint SIGN (design + post-code 5-variant verify) + Chris N8 selection + Chris D-verdict
scope: S2769 — N8: extend the S2763 close-ceremony ledger view + S2767 v2 render with server-side filters (session_min, session_max, envelope_only, date_from, date_to) and a total_available field so the operator surface stays useful past the 10-entry tail
serves_arc: platform observability (Ops Console at Workspace → System → Ops); durability of the close-ceremony ledger as sessions accumulate
precedent_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger.md (S2763 — v1 filesystem-backed ledger, fixed-root safety pattern)
  - docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger_v2.md (S2767 — v2 hover-preview + click-to-open)
  - docs/research/implementation/RATIFICATION_2026-07-11_recycle_emitter_worker_pids.md (S2768 — sibling ops surface extension)
ratified_documents:
  - core/views_ops_console.py (amended — close_ceremony_ledger view accepts 5 new filter params + returns total_available; _DATE_LINE_RE regex broadened to accept both markdown and YAML frontmatter date shapes)
  - frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx (amended — LedgerFilters state + compact filter row above the Recent Close-Ceremonies section + "showing X of Y" header + "Show up to 50" expand button + empty-state card)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2769 open freshness (retired-pin dispatch to Rigby) — verdict FRESH · SHA c46d19ef6d6f matches HEAD (THIRD corroboration cycle after PLAYBOOK-7.4.4; log carries mix of N7-enriched + legacy rows; backward-compat verified in the wild)
  - S2769 design SIGN (Rigby, pin pa-465ff14a830f49f9) — PASS on all three asks: Q1 (separate min/max params), Q2 (strict AND across filters), Q3 (keep limit=10 default, explicit "Show up to 50")
  - S2769 post-code verify SIGN (Rigby) — PASS on all 5 variants: baseline (count=10,total=961), session_min=2765 (4/4), envelope_only (10/21), date_from=2026-07-11 (10/14), session_min+envelope_only (4/4); total_available present on all responses
frozen: true
---

# Close-Ceremony Ledger v2 Search + Filter — Ratification Record

Frozen canonical record of Chris's ratification of the S2769 N8 filter extension on 2026-07-11. Extends the S2763 v1 ledger view + S2767 v2 render with server-side filters (session range, envelope-only, date range) plus a `total_available` field so the ledger stays useful once sessions accumulate past the 10-entry default tail. Append-only.

---

## §1. Context

- **Ratification date:** 2026-07-11 (America/Denver operator timezone)
- **Scope:** operator surface durability (N8 in S2768 candidate menu). At S2769 open the handoffs directory held 961 total handoffs; the S2763 v1 + S2767 v2 render capped at 10 meant every session past S2758 was invisible without a URL hand-edit. N8 makes the surface durable.
- **Motivation:** the S2767 CCL v2 hover-preview + click-to-open surface is only useful for sessions visible in the tail. Once a session falls off, the operator has to remember its number and paste the path manually — defeating the "fast context re-load" purpose of the S2763 build.
- **Ratifier:** Chris (candidate selection at S2769 open: "N8 approved, route joint SIGN through Rigby"; joint SIGN PASSed all three questions; no D-verdict re-check required).
- **Third cycle after PLAYBOOK-7.4.4 codification:** S2769 open verified FRESH · SHA-match at `c46d19ef6d6f` (S2768 close). Recycle log now carries a mix of N7-enriched + legacy rows — backward-compat verified in production.

---

## §2. Ratified Deliverables

### §2.1 `core/views_ops_console.py::close_ceremony_ledger` — 5 new filter params + `total_available`

Extended the S2763 view signature. All new params optional; strict AND semantics; filters applied BEFORE the limit slice:

| Param | Type | Meaning |
|---|---|---|
| `session_min` | int | include only sessions with number >= this |
| `session_max` | int | include only sessions with number <= this |
| `envelope_only` | bool | include only entries whose envelope exists |
| `date_from` | YYYY-MM-DD | include only entries whose parsed date >= this |
| `date_to` | YYYY-MM-DD | include only entries whose parsed date <= this |

Undated entries are excluded when either date filter is set (fail-safe: an operator asking for a date range wants dated entries).

Return shape adds `total_available: int` — the pre-limit matching count. UI uses it to render "showing X of Y matches" and to gate the "Show up to 50" expand button.

Two helpers extracted for testability: `_parse_int_param` (returns None on blank/invalid) and `_parse_date_param` (returns raw string if it matches `YYYY-MM-DD`, else None). Zero third-party deps.

### §2.2 `_DATE_LINE_RE` broadened to accept both handoff date shapes

The S2763 regex `^\*\*Date:\*\*\s+(\d{4}-\d{2}-\d{2})` only matched older handoffs that wrote the date as bold markdown. Newer handoffs (from S2767+) write the date in YAML frontmatter as `date: 2026-07-11`. Both formats are now accepted:

```python
_DATE_LINE_RE = re.compile(
    r'^(?:\*\*Date:\*\*\s+|date:\s+)(\d{4}-\d{2}-\d{2})',
    re.MULTILINE,
)
```

Before the fix: S2764–S2768 returned `date: null` (invisible to date filters). After: all 5 pick up `date: 2026-07-11` correctly. Date-filter smoke `date_from=2026-07-11` widened from 14 → 17 sessions.

### §2.3 `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — compact filter row + total_available surfacing + expand button

Above the Recent Close-Ceremonies row list, a single-line filter card:

- Two number inputs for session range (min – max), width 16 columns each
- Envelope-only checkbox with label
- Two date inputs (from – to)
- `clear` button appears when any filter is active

State managed via a new `LedgerFilters` interface and a `ledgerLimit` counter. `ledgerQuery` keyed by the filter query string so react-query cache respects filter identity.

Header behavior:
- No filters active: `Recent Close-Ceremonies (last N)`
- Any filter active: `Recent Close-Ceremonies (showing X of Y matches)`

Expand button:
- Renders when `total_available > count` AND `ledgerLimit < 50`
- Clicking sets `ledgerLimit = 50` — triggers react-query refetch under the new key

Empty-state card:
- Renders when `items.length === 0` — "No close-ceremonies match the current filters."

---

## §3. What Was NOT Changed

- No new URL route. Extended the existing `/api/ops/close-ceremony-ledger/` in place.
- No changes to the sibling `_HANDOFFS_ROOT` / `_ENVELOPES_ROOT` safety pattern from S2763.
- No changes to LedgerRow behavior (hover-preview + click-to-open drawer preserved verbatim).
- No changes to the S2765 recent-recycles view or S2768 N7 emitter.
- No frontend routing / component-tree changes outside the Ops Console tab.

---

## §4. Rigby SIGN Summary

Joint SIGN routed via pin `pa-465ff14a830f49f9` (label `s2769-ccl-v2-search-filter`).

### §4.1 Q1 — Query param shape
- **Rigby verdict:** PASS.
- **Content:** separate `session_min` + `session_max`. Simplest to validate server-side, cleanest react-query cache keys, composes with other filters.

### §4.2 Q2 — envelope_only + session filter interaction
- **Rigby verdict:** PASS.
- **Content:** strict AND across all active filters. Operator intent is unambiguous — ticking "envelope only" means "hide handoff-only rows," not "re-rank."

### §4.3 Q3 — Limit interaction with filters
- **Rigby verdict:** PASS.
- **Content:** keep default `limit=10`; expose an explicit "Show up to 50" re-fetch when `total_available > count`. Preserves initial-page performance; explicit expand is cleaner than surprise-load.

### §4.4 Post-code verify SIGN (5-variant HTTP smoke via `http_smoke_test`)
- **Rigby verdict:** PASS.
- **Content:**
  - `?limit=10` → count=10, total=961
  - `?session_min=2765` → count=4, total=4 (sessions [2768,2767,2766,2765])
  - `?envelope_only=true` → count=10, total=21
  - `?date_from=2026-07-11` → count=10, total=14 (before the frontmatter regex fix — post-fix 17)
  - `?session_min=2765&envelope_only=true` → count=4, total=4
  - `total_available` field present on all 5 responses.

---

## §5. Empirical smoke tests

### §5.1 Vite production build
- Command: `npm run build`
- Result: passed 3.25s, no TS errors. Main bundle grew ~3 KB (filter state + inputs + expand button).

### §5.2 Django shell smoke (6 combos + regex fix follow-up)
- Baseline / session_min / envelope_only / date_from / combined / narrow-range-with-limit-expand — all returned the expected count + total_available. Full log in envelope §4.4.

### §5.3 Rigby HTTP smoke
- 5 GET variants via `http_smoke_test`; all PASS; `total_available` present on every response. Full log in envelope §4.4.

### §5.4 Frontmatter date regex fix
- Baseline (before): S2764–S2768 returned `date: null`.
- Post-fix: all 5 pick up `date: 2026-07-11`. `date_from=2026-07-11` widened 14 → 17.
- Not a regression from N8; the underlying data-quality gap already existed; N8 exposed it. Fixed opportunistically in the same PR.

---

## §6. Post-ratification bindings

- **Head at ratification:** filled at merge.
- **Merged PR:** filled at merge.
- **Workspace mirrors (S2754a twin-canonical rule):**
  - Governance envelope mirror → `RUR-C1 Tenant Boundary Lockdown` workspace `fcd7e683-3bfe-4d35-9704-0e54dd587ea1` (deliverable_type `ratification_record`, category `governance`).
  - Content mirror → same workspace (deliverable_type `initiative_phase_doc`, category `implementation`).
- **PLAYBOOK-7.4.4 dogfood:** `make recycle-all` invoked post-merge — fourth consecutive cycle where the constitutional rule fires; second cycle to emit N7-enriched entry into the log.

---

## §7. Forward carry

- **N9 (dedicated `/api/ops/doc-preview/`).** Still deferred; no bandwidth signal yet from CCL v2 hover-preview. Re-evaluate once the search UI drives more traffic.
- **N10 (partial-recycle UI badge).** Still gated on observing at least one partial-recycle event in the JSONL log. The N7 machinery is now producing enriched rows in production; two-trigger threshold still unmet.
- **Filter presets (deferred N-lane).** If the "clear" button gets clicked immediately after a "Show up to 50" expand often enough to be noticeable, a small preset dropdown ("last 20", "this arc", "envelope-having only") might be worth it. Two-trigger threshold not met; wait for real operator patterns.
- **Frontmatter date normalization elsewhere.** The `_DATE_LINE_RE` broadening solves the ledger's date filter but the underlying handoff-date drift (some `**Date:**`, some YAML `date:`) is a broader repo hygiene item. Not codifying as a Playbook rule until a second surface trips on the same drift.
