---
session: 2769
date: 2026-07-11
title: "Close-Ceremony Ledger v2 search + filter ratified"
status: complete
outcome: shipped
scope: net-new-engineering-N8
canonical_authority: repo_canonical
ratification_envelope: docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_search_filter.md
---

# Session 2769 — Close-Ceremony Ledger v2 search + filter ratified

## §1. TL;DR

Chris selected N8 from the S2769 candidate menu with "N8 approved, route joint SIGN through Rigby." Rigby PASSed all three design questions (separate min/max params; strict AND across filters; keep limit=10 default with explicit "Show up to 50"). Shipped server-side filters + `total_available` field on the S2763 `close_ceremony_ledger` view and a compact filter row + expand button in the S2767 v2 render.

**Opportunistic fix included:** the S2763 date-line regex only recognized older `**Date:**` markdown handoffs. Newer S2767+ handoffs use YAML `date:` frontmatter and were silently invisible to date filters (returned `date: null`). Broadened `_DATE_LINE_RE` to accept both. Date-filter smoke widened 14 → 17 sessions covered.

**Fourth close-cycle under PLAYBOOK-7.4.4.** Second post-N7 cycle producing an enriched JSONL entry.

## §2. Timeline

| Time (approx) | Event | Reference |
|---|---|---|
| S2769 open | `context-kit orient` + START-NEXT read + freshness via retired S2768 pin | this session log |
| N8 selected | Chris: "N8 approved, route joint SIGN through Rigby" | this session |
| Pin minted | `pa-465ff14a830f49f9` scoped to `s2769-ccl-v2-search-filter` | `session_lifecycle open` |
| Verify-before-build | S2763 view internals traced (`_HANDOFFS_ROOT`, `_index_envelopes_by_session`, regex constants) | this session |
| Rigby design SIGN | one round-trip, Q1/Q2/Q3 asks batched; PASS on all three | pin above |
| Code + smoke | view edit → shell smoke (6 combos) → date regex extension → build → Rigby HTTP smoke (5 variants) | this session |
| Envelope + handoff | this doc + envelope | filesystem |
| Docs cascade + provenance | 4-step + provenance rebuild | (post-merge below) |
| PR merge | filled at merge | GitHub |
| `make recycle-all` | dogfoods PLAYBOOK-7.4.4 (fourth cycle) | Makefile |

## §3. What shipped

**Files touched:**

- `core/views_ops_console.py` — `close_ceremony_ledger` view extended with `session_min / session_max / envelope_only / date_from / date_to` optional query params; returns new `total_available` field. Two helpers added: `_parse_int_param`, `_parse_date_param`. `_DATE_LINE_RE` broadened to accept both `**Date:** YYYY-MM-DD` markdown and `date: YYYY-MM-DD` YAML frontmatter.
- `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — new `LedgerFilters` interface + `hasActiveFilters` / `buildLedgerQueryString` helpers; `ledgerFilters` + `ledgerLimit` state; ledgerQuery keyed by filter-query-string; compact filter row above the Recent Close-Ceremonies section (session range + envelope-only checkbox + date range + clear button); "showing X of Y matches" header; "Show up to 50" expand button; empty-state card.
- `docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_search_filter.md` — new envelope.
- `docs/handoffs/SESSION_2769_CCL_V2_SEARCH_FILTER_RATIFIED.md` — this file.

Net: backend +65 lines, frontend +110 lines. No new routes; no schema; no new deps.

**Backward compat:** clients ignoring `total_available` still work (S2763 shape preserved). Older backends returning without `total_available` render fine on the new frontend (the header falls back to the "last N" text).

## §4. Rigby SIGN Summary

Joint SIGN routed via pin `pa-465ff14a830f49f9`; post-code verify was a second round-trip on the same pin using `http_smoke_test` to exercise five GET variants.

**Freshness:** verdict FRESH · SHA `c46d19ef6d6f` matches HEAD (S2768 close). Third post-codification cycle held. Recycle log carries mix of N7-enriched + legacy rows — backward-compat verified in production.

**Design SIGN — Q1 (query param shape):** PASS on separate `session_min` + `session_max` (URL-safe, no parsing, clean cache keys).

**Design SIGN — Q2 (filter interaction):** PASS on strict AND. `envelope_only` + session range compose as intersection, not re-rank.

**Design SIGN — Q3 (limit interaction):** PASS on keep-default-10 + explicit "Show up to 50" button. Preserves initial-page performance; avoids surprise loads.

**Post-code verify SIGN (HTTP smoke, 5 variants):** PASS.
- baseline (`?limit=10`) → count=10, total=961
- session_min=2765 → count=4, total=4 (sessions [2768,2767,2766,2765])
- envelope_only=true → count=10, total=21
- date_from=2026-07-11 → count=10, total=14 (before frontmatter regex fix; post-fix widened to 17)
- session_min=2765 & envelope_only=true → count=4, total=4
- `total_available` field present on all 5 responses.

## §5. Frontmatter date regex fix (opportunistic)

The S2763 `_DATE_LINE_RE` regex only matched `**Date:** YYYY-MM-DD` bold markdown. That format lived on until roughly S2760; from S2767 forward, handoffs use `date: YYYY-MM-DD` in YAML frontmatter (following the ratification envelope convention). The view was silently returning `date: null` for those, making them invisible to any date filter.

Fix: broadened the regex to `^(?:\*\*Date:\*\*\s+|date:\s+)(\d{4}-\d{2}-\d{2})`. Zero edge cases — both patterns are anchored to line-start with `MULTILINE` and the capture group is identical. Post-fix, S2764–S2768 all pick up `date: 2026-07-11` correctly.

Not a regression from N8; a pre-existing data-quality gap that N8 exposed. Fixed in the same PR because leaving it would have made the new date filter appear broken to any operator who tried it on recent sessions.

## §6. Post-merge browser eyeball (Chris)

1. Hard-refresh `localhost:8000/workspace?tab=system&sub=ops`.
2. Verify all existing sections still render (Ops Health tile, SLO, Signatures, Blocked, Recent Recycles).
3. **NEW — filter row above Recent Close-Ceremonies:** session range inputs, envelope-only checkbox, date range inputs.
4. Type `2765` in the min input → header should update to "showing X of Y matches"; rows filter to S2765+.
5. Tick "envelope only" → results intersect (only envelope-having rows visible).
6. Clear filters (click "clear") → returns to "last 10" default.
7. Load handoff paths for older sessions by widening date range or lowering session_min; if >10 match, "Show up to 50" button appears.
8. Regression check: LedgerRow hover-preview + click-to-open drawer still work exactly as before.

## §7. Twin-Pointer Card

📁 **Repo `/docs/` + `/core/` + `/frontend/` — S2769 artifacts:**

- **Amended backend view:** `core/views_ops_console.py::close_ceremony_ledger`
- **Amended frontend surface:** `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_search_filter.md`
- **Handoff:** `docs/handoffs/SESSION_2769_CCL_V2_SEARCH_FILTER_RATIFIED.md` (this file)
- **Predecessor envelopes:** S2763 (v1 ledger) + S2767 (v2 hover-preview + drawer) in the same folder.
- **Constitutional context:** `docs/ENGINEERING_PLAYBOOK.md` §7.4.4 (v0.6.0, S2766)

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2769 (created at close via ORM-direct per S2754a twin-canonical rule)
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surface:** `localhost:8000/workspace?tab=system&sub=ops` — Recent Close-Ceremonies section now has a compact filter row and a "showing X of Y" header + expand button when filters narrow results.

## §8. Current Repository State

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2769 merge) |
| Playbook version | v0.6.0 (RATIFIED S2766) |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · I-0303 Phase 3 stage 2 first pass CLOSED · S2755→S2768 diagnostic infra + operator surfaces + governance CLOSED · **S2769 CCL v2 search+filter CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-465ff14a830f49f9` (retired at S2769 close) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-465ff14a830f49f9` (retired; forces fresh mint at S2770 open) |
| Live infra state | S2755→S2768 diagnostic infra + operator surfaces + Playbook v0.6.0 + CCL v2 + recycle emitter enriched + **CCL v2 search+filter** operational |
| Next move | Chris selects at S2770 open |

## §9. What This Session Taught About Doing Sessions

- **Backend-first shell smoke saves a Rigby round-trip.** Testing all 6 filter combos via Django shell before touching frontend gave me the correct expected counts to hand Rigby for HTTP verify (the 5-variant `http_smoke_test` had exact expected values, not "check if it works"). Cheap; catches misspecifications before they leave my machine.
- **Opportunistic fixes belong in the same PR when they'd make the new feature appear broken.** The frontmatter date regex gap wasn't caused by N8, but leaving it unfixed would have made an operator's first `date_from` filter attempt on recent sessions return zero results. Fixing it in the same PR is the right call — one round-trip through review, not two.
- **`total_available` is the durable UX handle for capped surfaces.** Any ledger with a limit should return both the count and the pre-limit-matched size. Without it, the UI can't tell "you hit the exact matching set" from "there are more you can't see." Worth codifying as a pattern for future capped-list ops surfaces.
- **Fourth close-cycle under PLAYBOOK-7.4.4 still holds.** Recycle rule remains machine-observable; N7 enrichment continues to flow into the log.
