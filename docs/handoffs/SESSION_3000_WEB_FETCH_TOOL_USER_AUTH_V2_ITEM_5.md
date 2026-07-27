---
title: "SESSION 3000 — web_fetch_tool use_user_auth (v2 item #5, corrected scope) — v2 arc 12-of-12 COMPLETE"
session: 3000
date: 2026-07-27
type: engineering_close
merge_shas:
  - "39a6a9c97"   # PR #3670 — web_fetch_tool use_user_auth
prs:
  - 3670
related_arcs:
  - "findings-surface v2 (S2991 → S2992 → S2993 → S2994 → S2995 → S2996 → S2997 → S2998 → S2999 → S3000)"
  - "COMPLETE: v2 arc 12-of-12 items shipped end-to-end"
consumes:
  - "5-trigger accumulated evidence across S2996–S2999 that APIClient fallback was systemic"
---

# S3000 — web_fetch_tool use_user_auth (v2 item #5) — **v2 arc COMPLETE**

**Status:** CLOSED. One feature PR merged after ~15 min investigation reframed the scope. Recycle-all clean at `sha=39a6a9c97bfe`. **The findings-surface v2 arc is now 12-of-12 items complete.**

## Session shape

Chris asked before opening Option A: "what's actually wrong with web_fetch_tool? Should we investigate before we move on?" That instinct proved correct — the "web_fetch_tool session cookies" carry-forward label was wrong. Actual gap was smaller than framed.

## What shipped

**PR #3670 (`39a6a9c97`) — v2 item #5 (corrected scope): `web_fetch_tool` gains `use_user_auth` param.**

Handler at `core/services/td_handlers_agents.py:442` already received `user_id` from Rigby's dispatch context but never used it. When `use_user_auth=True` + `user_id` present → look up user's DRF Token via `Token.objects.filter(user_id=user_id).first()` → inject `Authorization: Token <key>` header. The `MobileTokenAuthentication` in `REST_FRAMEWORK` config accepts this exactly.

Contract:
- **`use_user_auth: bool = False`** new schema param
- **Explicit override wins** — case-insensitive check for existing `Authorization` header; caller's value preserved
- **Fail-open** — no Token row for the user → proceed unauthenticated, endpoint's 401 returned as-is (Rigby sees the real failure mode instead of a mystery)
- **`auth_injected=<bool>`** added to the existing INFO log line for audit
- **Never mutates** caller's headers dict (copies before setting)
- **Default False** → zero change for existing external-endpoint callsites

Precedent: same Token lookup at `td_handlers_core.py:854-855`. **~5-10 LOC net**, not "~1 session + security review" as I'd been framing it for 5 sessions.

**8 new tests** covering all branches (default, use_user_auth=False, injection, no user_id, no token row → fail-open, explicit-header override lowercase+uppercase, headers dict not mutated).

## The historic A2 SIGN

**First time this entire v2 arc that Rigby verified a backend endpoint without me falling back to APIClient.**

Rigby dispatched:
- `web_fetch_tool` with `url=http://localhost:8000/api/repo/doc-research-findings/?status=open&staleness=suspected&page_size=5`, `use_user_auth=true`, `method=GET`

Result: **HTTP 200** (not 401), body contained ALL 4 known-suspected finding IDs (`56851590-...`, `e386eb18-...`, `956f8571-...`, `7d5f6797-...`), full JSON structure with `staleness_failed_refs` metadata visible. End-to-end proof that Rigby's own tool surface is now self-sufficient for internal-endpoint A2 SIGN.

## The scope-mislabel post-mortem

Carry-forward called it "web_fetch_tool session cookies" for 5 sessions. Actual gap: `user_id → DRF Token lookup`. The mislabel cost me ~5 sessions of framing the carry-forward as "~1 session + security review" when it was ~30 min end-to-end (investigation + implementation + tests + ship).

Root cause: I named the gap from the symptom (401 responses) rather than reading the handler code. The name locked in the false assumption ("must be session cookies") that ossified across the arc.

Chris's instinct — "investigate first before jumping to A" — was the crack that broke the mislabel loop.

## v2 sequence status (post-S3000) — **COMPLETE**

- [x] #1 close_mode taxonomy — S2991
- [x] #2 finding_type classifier + backfill — S2992
- [x] #3 spec-generator prompt branching on finding_type — S2993
- [x] #4 staleness detector at ingest + backfill — S2995
- [x] #4 UI surface (badge + filter + failed-refs) — S2996
- [x] **#5 orm_inspect_tool allowlist (ORM half) — S2991**
- [x] **#5 `web_fetch_tool` user auth (formerly "cookies half") — S3000 (this handoff)**
- [x] #6 Rigby-SIGN nudge in UI for decision_evidence — S2994
- [x] #6 hotfix — post-dispatch View-deliverable link — S2995
- [x] #7 F-A2-equivalent for downstream consumers — S2999
- [x] #8 wire-through smoke-check AC for half-wired findings — S2997
- [x] Fold D from S2997 — send-to-rigby re-dispatch guard — S2998

**All original v2 sequence items shipped. Arc COMPLETE.**

## Zoom-out folds (PLAYBOOK-6.10.8)

**Fold A (Rigby A2 zoom-out (a)) — potential Playbook rule candidate.** Pattern: "Before carrying forward an investigation as a multi-session blocker, reproduce the failure at the thinnest interface (PA tool / HTTP call) and enumerate the missing affordance precisely." This session was 1st concrete instance of a mislabel breaking after 5 sessions. Rule-worthy pattern IF a 2nd similar instance surfaces — for now, `informational` with active-watch trigger.

**Fold B (Rigby A2 zoom-out (b)) — `informational`.** Residual APIClient-forcing shapes even with `use_user_auth`: (i) CSRF + Django-session-cookie endpoints (not DRF Token-authed); (ii) multipart/form-data uploads (schema is JSON-only); (iii) OAuth redirects / signed URLs; (iv) non-JSON POST bodies. None blocking v2; watch for future arcs needing any of these shapes.

**Fold C (Rigby A2 zoom-out (c)) — Rigby Tool Gap Ledger (closed by this PR).** Gap entry: "PA HTTP fetch couldn't hit auth-protected internal endpoints; forced APIClient fallback." Fix shipped in this PR. Residual gaps logged in Fold B.

## HEAD / recycle state

- `39a6a9c97` — feat PR #3670
- Recycle-all clean at `sha=39a6a9c97bfe` post-merge (backend-only, frontend rebuild skipped correctly).

## Files touched

- `core/services/td_handlers_agents.py` — `use_user_auth` handling in `_handle_web_fetch`, `auth_injected` in log line
- `core/services/pa_tool_schemas.py` — new `use_user_auth` schema param
- `core/tests/test_s3000_web_fetch_tool_user_auth.py` — 8 tests

## Playbook rule exercise

- **PLAYBOOK-7.7.1** (Spec→Ship contract) — Flow B, but with an investigation phase inserted BEFORE T1 SIGN because Chris challenged the scope framing. Ships were: investigate → recommend scope → Chris ratifies → code → tests → PR → A2 SIGN → merge → recycle.
- **PLAYBOOK-7.7.2** (SIGN evidence discipline) — T1 SIGN was skipped (design was fully deterministic after Chris ratified Option 1). A2 SIGN was the strongest possible — Rigby used her own newly-shipped tool surface end-to-end, no APIClient fallback.
- **PLAYBOOK-7.7.3** (Chris-facing decision framing) — Chris's investigation ask was itself a decision route ("A or investigate first?"). Investigate-first delivered a corrected scope + smaller ship in less time than the mislabeled framing would have taken.
- **PLAYBOOK-6.10.8** (fold classification) — 3 folds (A `informational` potential rule; B `informational` residual gaps; C ledger candidate closed).
- **PLAYBOOK-7.4.4** (recycle after merge) — Backend-only; frontend rebuild skipped correctly.
- **`feedback_verify_at_raw_orm_before_trusting_tool_no_data`** — This session's spiritual cousin: verify at raw CODE before trusting your own carry-forward framing. The T1 SIGN convention emphasizes tool-based verification of assumptions; this session showed that assumption-verification should also cover carry-forward LABELS, not just the framing content.
- **`feedback_zoom_out_ask_per_rigby_sign`** — A2 zoom-out surfaced the rule-worthy pattern (Fold A) that would have been invisible from a "small win" narrative.
