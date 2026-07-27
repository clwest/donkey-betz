---
title: "SESSION 2996 — Findings-surface v2 Option A: FindingsTab staleness surface"
session: 2996
date: 2026-07-27
type: engineering_close
merge_shas:
  - "12e5400a2"   # PR #3661 — Option A: staleness badge + filter + failed-refs
prs:
  - 3661
related_arcs:
  - "findings-surface v2 (S2991 → S2992 → S2993 → S2994 → S2995 → S2996)"
consumes:
  - "S2995 staleness axis + metadata['staleness_failed_refs']"
  - "S2994 FindingsTab hidden-for-default badge pattern"
---

# S2996 — FindingsTab staleness surface (Option A)

**Status:** CLOSED. One feature PR merged. Recycle-all clean at `sha=12e5400a222a`.

## What shipped

**PR #3661 (`12e5400a2`) — Option A: FindingsTab surfaces staleness (badge + filter + failed-refs).**

Extends the S2994 FindingsTab treatment to the S2995 staleness axis. Chris can now visually spot the 4 currently-suspected findings without needing the `?staleness=suspected` API param.

- **TS types** — `Staleness = 'fresh' | 'suspected'` added to Finding; `metadata.staleness_failed_refs?: string[]` implicitly consumed.
- **`StalenessBadge` component** — orange `Clock` icon + "Stale" text on every suspected row; hidden for `fresh` (matches the S2994 hidden-for-default pattern). Shows regardless of `finding_type` per Rigby T1 SIGN Ask #3(a) — staleness is an orthogonal truth signal, so a future `decision_evidence + suspected` combination stays visible.
- **Filter dropdown** — "Staleness: Any / Fresh / Suspected stale" joins the existing status/source/type/confidence filter bar and wires the S2995 `?staleness=` backend param.
- **Expanded row detail** — when `metadata.staleness_failed_refs` is present, renders the failing refs as orange monospace `<code>` chips. Plain list, no clickable-URL coupling (Rigby Ask #3(b) — GitHub-blob URLs would require repo-remote-shape config and multi-repo disambiguation).

## SIGN discipline (PLAYBOOK-7.7.2)

- **T1 SIGN** — Rigby returned real `orm_inspect_tool` result on Ask #1: confirmed all 4 currently-suspected rows are `finding_type=executable`, so the Stale badge sits inline with existing Executable badge (no visual collision). This informed the color choice — orange-500 stays distinguishable from amber (Evidence) and blue (Executable). Ask #2 (color): AGREE orange-500 (attention without alarm). Ask #3: (a) AGREE show on every suspected row regardless of type; (b) AGREE plain list; (c) DEFER recheck-button (workflow scope creep, ledger candidate); (d) AGREE ledger candidate.

- **A2 SIGN** — Post-merge, Rigby verified substrate via `orm_inspect_tool filter(staleness='suspected')` — all 4 rows still present with `metadata.staleness_failed_refs` populated (the exact data the expanded-row chips render). Ask #2 (endpoint HTTP verify) DISAGREE for auth reason (`web_fetch_tool` hit 401 — expected; that IS the deferred half of v2 item #5). Backend was E2E-tested in S2995 already so this is a known tool-gap, not a substrate failure.

## v2 sequence status (post-S2996)

- [x] #1 close_mode taxonomy — S2991
- [x] #2 finding_type classifier + backfill — S2992
- [x] #3 spec-generator prompt branching on finding_type — S2993
- [x] #4 staleness detector at ingest + backfill — S2995
- [x] #4 UI surface (badge + filter + failed-refs) — **S2996 (this handoff)**
- [x] #5 orm_inspect_tool allowlist (ORM half) — S2991
- [x] #6 Rigby-SIGN nudge in UI for `finding_type=decision_evidence` — S2994
- [x] #6 hotfix — post-dispatch View-deliverable link — S2995
- [ ] #5 `web_fetch_tool` session cookies (deferred half) — **live-verified as a real gap this session (Rigby A2 hit 401)**
- [ ] #7 F-A2-equivalent for downstream consumers — carry-forward
- [ ] #8 wire-through smoke-check AC for half-wired findings — carry-forward

**The findings-surface v2 arc's UI-side is now closed.** Backend has status/close_mode/finding_type/staleness axes, all four surfaced in FindingsTab (badges hidden-for-default, filters, targeted CTAs). Remaining v2 items (#5-cookies, #7, #8) are ~30-60 min each with different substrate priorities.

## Zoom-out folds (PLAYBOOK-6.10.8)

**Fold A (Rigby A2 Ask #2 DISAGREE) — direct evidence of an existing carry-forward.** `web_fetch_tool` hit 401 on `?staleness=suspected` — that IS the deferred half of v2 item #5 (session cookies for `web_fetch_tool`). Not new. Live-verified this session as a real ops gap: Rigby's HTTP-shape verification of backend endpoints is blocked by auth. Bumps the priority of that carry-forward item slightly (2nd trigger).

**Fold B (Rigby A2 zoom-out (a)) — `future_trigger`, condition = daily Chris triage.** Recheck-this-finding button still deferred. Rigby: "promote to next PR IF Chris is actively triaging daily; otherwise keep in ledger." Current signal is 4 suspected rows total — not daily-triage volume yet. Ledger stays.

**Fold C (Rigby A2 zoom-out (b)) — `future_trigger`.** Toast copy for suspected findings could read "Evidence-capture created (staleness suspected)" to reinforce the axis at dispatch time. Optional polish; watch for 2nd trigger or Chris signal.

**Fold D (Rigby A2 zoom-out (c)) — `informational`, low risk.** Badge crowding on `Evidence + Stale` (future) or `Executable + Stale` (current) is manageable; hidden-for-default axis pattern prevents badge spam. If it grows crowded, future step is a badge-stack wrap layout, not axis suppression.

**Fold E (Rigby A2 zoom-out (d)) — Rigby Tool Gap Ledger entry.** No in-UI action to re-run staleness verification for a single finding (or selection) from FindingsTab. Would consume the S2995 `--recheck-staleness --apply` mode behind an authenticated endpoint. Sharpened from S2996 T1 Fold — clear next-increment shape.

## HEAD / recycle state

- `12e5400a2` — feat(s2996) PR #3661
- Recycle-all clean at `sha=12e5400a222a` post-merge (frontend rebuild included per `feedback_recycle_after_merge` — 2303 modules transformed, Daphne restarted, dist synced).

## Files touched

- `frontend/src/pages/workspace/tabs/FindingsTab.tsx` — Staleness type, StalenessBadge, filter dropdown, expanded-row failed_refs chips
- `core/templates/index.html` — Vite manifest sync

## Playbook rule exercise

- **PLAYBOOK-7.7.1** (Spec→Ship contract) — Flow B (Option A ratified at S2995 close). No phase skipped: framing → T1 SIGN → code → build check → PR → A2 SIGN → merge → recycle.
- **PLAYBOOK-7.7.2** (SIGN evidence discipline) — Both SIGN cycles returned real `orm_inspect_tool` results. A2 additionally exercised `web_fetch_tool` (which surfaced the deferred v2 item #5 gap concretely).
- **PLAYBOOK-7.7.3** (Chris-facing decision framing) — No new decision required; Option A was Chris's directive at S2995 close.
- **PLAYBOOK-6.10.8** (fold classification) — 5 folds classified (A `informational` = 2nd trigger on existing carry-forward; B `future_trigger`; C `future_trigger`; D `informational` low risk; E ledger candidate).
- **PLAYBOOK-7.4.4** (recycle after merge) + S2978 refinement — Frontend diff → `make recycle-all` triggered frontend rebuild + Daphne restart. `feedback_recycle_after_merge` compliance.
- **`feedback_verify_at_raw_orm_before_trusting_tool_no_data`** — Rigby A2 Ask #1 used raw ORM to confirm the 4 rows have `staleness_failed_refs` populated (the exact data the UI chips render).
- **`feedback_zoom_out_ask_per_rigby_sign`** — Both SIGN cycles included a zoom-out ask; A2 zoom-out surfaced 3 folds worth ledger + future_trigger tracking.
