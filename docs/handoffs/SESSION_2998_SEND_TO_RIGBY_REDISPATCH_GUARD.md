---
title: "SESSION 2998 — send-to-rigby re-dispatch guard (v2 Fold D from S2997)"
session: 2998
date: 2026-07-27
type: engineering_close
merge_shas:
  - "d3ab2e889"   # PR #3666 — 409 guard + force=true escape hatch
prs:
  - 3666
related_arcs:
  - "findings-surface v2 (S2991 → S2992 → S2993 → S2994 → S2995 → S2996 → S2997 → S2998)"
consumes:
  - "S2997 Fold D (re-dispatch footgun surfaced during A2 SIGN)"
  - "S2995 hotfix (frontend already button-transformed to View deliverable)"
---

# S2998 — send-to-rigby re-dispatch guard (Fold D from S2997)

**Status:** CLOSED. One feature PR merged. Recycle-all clean at `sha=d3ab2e8891c2`.

## What shipped

**PR #3666 (`d3ab2e889`) — v2 Fold D from S2997: send-to-rigby refuses re-dispatch by default; force=true escape hatch.**

Closes the footgun I hit during S2997 A2 SIGN. Endpoint previously proceeded regardless of `finding.deliverable_id`, so a second click / curl / PA-tool call created a duplicate spec and burned tokens.

Contract:
- **409 Conflict** when `finding.deliverable_id` is set AND request body doesn't include `{"force": true}`
- **Strict boolean check** per Rigby T1 SIGN extra — `"true"` / `"yes"` string, integer `1`, etc. all rejected. `force is True` only.
- Response payload includes `existing_deliverable_id` so callers can navigate to what was already produced (matches the S2995 "View deliverable" hotfix pattern)
- `reason_code: "deliverable_already_exists"` for programmatic handling
- **`force=true` re-dispatch** replaces `finding.deliverable_id` with the new one; **old deliverable left as an orphan** (Rigby T1 zoom-out (a) — deletion is irreversible; leave for caller-driven cleanup)
- **WARNING log on force use** for audit trail (token-burn escape hatch)

Frontend (S2995 hotfix) already dispatch-safe via the button-transform pattern; this guard is defense-in-depth for direct API calls, PA-tool dispatches, and bulk ops (Rigby T1 SIGN Ask #2(b)).

**11 new tests** covering: fresh-dispatches (no body / empty body), refuse-when-set (no body / empty / force=false), strict force flag (`"true"` string / integer `1` both rejected), `force=True` boolean overrides + replaces deliverable_id, invalid JSON → 400, non-dict body → 409, WARNING log emitted on force use. **84 pre-existing tests** (S2993 + S2995 + S2997 + canonical-briefing) all green.

## SIGN discipline (PLAYBOOK-7.7.2)

- **T1 SIGN** — Rigby returned substantive rationale on 409 vs 400 (409 semantically right; "resource state prevents action" > "invalid request"; 412 Precondition Failed considered but overkill here). AGREE `force` over `allow_redraft` (terse, common convention, "I know this is unsafe" signal). Zoom-out AGREE (a) leave old deliverable alone (deletion irreversible); (b) backend defense-in-depth still warranted; (c) ledger candidate. Extra tightening: strict boolean check + audit log.

- **A2 SIGN** — Real double-dispatch scenario against fresh finding `00a142f2-...`:
  - Attempt 1 (no body): HTTP 201, deliverable `9f617505-...` created ✓
  - Attempt 2 (no body): HTTP 409, `reason_code=deliverable_already_exists`, `existing_deliverable_id=9f617505-...` ✓
  - Attempt 3 (`{"force": "true"}` — string): HTTP 409 (strict boolean holds) ✓
  - Attempt 4 (`{"force": True}` — boolean): HTTP 201, but returned same deliverable_id `9f617505-...` — surfaced Fold A below

Rigby independently verified via `orm_inspect_tool filter` on both finding and deliverable — both persisted correctly.

## v2 sequence status (post-S2998)

- [x] #1 close_mode taxonomy — S2991
- [x] #2 finding_type classifier + backfill — S2992
- [x] #3 spec-generator prompt branching on finding_type — S2993
- [x] #4 staleness detector at ingest + backfill — S2995
- [x] #4 UI surface (badge + filter + failed-refs) — S2996
- [x] #5 orm_inspect_tool allowlist (ORM half) — S2991
- [x] #6 Rigby-SIGN nudge in UI for decision_evidence — S2994
- [x] #6 hotfix — post-dispatch View-deliverable link — S2995
- [x] #8 wire-through smoke-check AC for half-wired findings — S2997
- [x] Fold D from S2997 — send-to-rigby re-dispatch guard — **S2998 (this handoff)**
- [ ] #5 `web_fetch_tool` session cookies (deferred half) — 3rd trigger surfaced S2997
- [ ] #7 F-A2-equivalent for downstream consumers — carry-forward

**Only #5-cookies and #7 remain from the v2 sequence.** The daily-use pipeline (audit → ingest → FindingsTab → Verify evidence → spec deliverable with staleness call-out → re-dispatch guard) is now defense-in-depth complete.

## Zoom-out folds (PLAYBOOK-6.10.8)

**Fold A (A2 SIGN Attempt 4) — `future_trigger`.** `force=true` bypasses the finding-level guard but `deliverable_factory.create_deliverable` has a 4h title-dedupe + 72h content-hash-dedupe (see `core/services/deliverable_factory.py:935,962`). Within window, force=true → identical spec text → dedupe returns existing deliverable → caller gets old ID back. **Not a bug in shipped code** — dedupe is deliberate cost-control. But there's a semantic mismatch: "force" past the guard vs "force" a genuinely-new deliverable. Two future shapes to consider (Rigby T1 recommendation): split into `force_guard=true` vs `force_new_deliverable=true` flags, OR add a `dedupe_mode=<enum>` param. Doc-first per Rigby A2 zoom-out (a); only ship polish if operator friction surfaces.

**Fold B (Rigby T1 Ask #2(a)) — `future_trigger`.** Force re-dispatch could optionally add a non-destructive metadata breadcrumb (`DeliverableEvent`) marking the OLD deliverable as superseded. Not shipped; leave as caller-driven cleanup.

**Fold C (Rigby T1 zoom-out (c)) — Rigby Tool Gap Ledger.** "Semantic mismatch between endpoint override flag and downstream dedupe policy — classic tool-gap / footgun class." Logging helps avoid future confusion + guides whether we eventually want two flags or an enum.

## HEAD / recycle state

- `d3ab2e889` — feat PR #3666
- Recycle-all clean at `sha=d3ab2e8891c2` post-merge (backend-only, frontend rebuild skipped correctly).

## Files touched

- `core/views_doc_research_findings.py` — `send-to-rigby` view: JSON body parse, 409 refuse path, force check + audit log
- `core/tests/test_s2998_send_to_rigby_redispatch_guard.py` — 11 tests

## Playbook rule exercise

- **PLAYBOOK-7.7.1** (Spec→Ship contract) — Flow B (Option C directive from S2997 close). No phase skipped.
- **PLAYBOOK-7.7.2** (SIGN evidence discipline) — T1 SIGN Rigby returned substantive rationale (not tool_run since spec was deterministic). A2 SIGN used real APIClient double-dispatch producing verifiable HTTP status codes + Rigby independently confirmed persistence via `orm_inspect_tool`. Real gpt-5-mini roundtrip on Attempts 1 and 4.
- **PLAYBOOK-7.7.3** (Chris-facing decision framing) — No new decision required; Option C ratified at S2997 close.
- **PLAYBOOK-6.10.8** (fold classification) — 3 folds (A `future_trigger`; B `future_trigger`; C ledger candidate). Note: Fold A was surfaced by real dispatch (not framing), fits the pattern that A2 SIGN via real ops catches things design-time framing doesn't.
- **PLAYBOOK-7.4.4** (recycle after merge) + S2978 refinement — Backend-only diff; frontend rebuild correctly skipped via HEAD-range path-diff.
- **`feedback_verify_at_raw_orm_before_trusting_tool_no_data`** — Real APIClient double-dispatch verified 409 refuse + force behavior BEFORE Rigby A2 SIGN. Fold A only surfaced BECAUSE I used a real fresh finding (not the S2997 test fixture's fake UUID).
