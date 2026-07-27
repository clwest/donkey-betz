---
title: "SESSION 2993 — Findings-surface v2 item #3: spec-generator prompt branching on finding_type"
session: 2993
date: 2026-07-27
type: engineering_close
merge_shas:
  - "f533cacf8"
prs:
  - 3653
related_arcs:
  - "findings-surface v2 (S2991 → S2992 → S2993)"
consumes:
  - "S2992 finding_type axis (decision_evidence / executable / unknown)"
---

# S2993 — Spec-generator prompt branches on finding_type

**Status:** CLOSED. One feature PR merged. Recycle-all clean at `sha=f533cacf8be0`.

## What shipped

**PR #3653 (`f533cacf8`) — v2 item #3: spec-generator prompt branching on `finding_type`.**

`core/services/briefing_spec_generator.generate_spec_body` now accepts an optional `finding_type: Optional[str]` kwarg. When `decision_evidence`, the internal router selects `_build_spec_prompt_evidence` (evidence-capture prompt — goal captures a boundary/verdict, acceptance criteria become verification/re-audit steps). Everything else (`executable`, `unknown`, `None`, unrecognized) falls through to the existing `_build_spec_prompt_engineering` (the pre-S2993 prompt).

Design shape (Rigby T1 SIGN AGREE-all with real tool_runs on 3 real decision_evidence corpus samples):

- **Same JSON schema** (`goal / context / open_question / files_implicated / acceptance_criteria`) — no renderer or list-endpoint changes needed.
- **Same markdown section headers** — Deliverable body renderers stay identical.
- **New extras** — `spec_prompt_shape` (`engineering` | `evidence_capture`) + `finding_type_used` (the finding_type string that drove selection, or `None`) land in Deliverable metadata for downstream audit.
- **Fail-open placeholder copy diverges per shape** — `_placeholder_spec` takes a `prompt_shape` argument. Evidence-shape failures say "evidence capture failed — author manually" / "Author verification steps manually." instead of the engineering copy. Same-PR mitigation of a Rigby zoom-out fold.
- **Send-to-rigby view forwards `finding.finding_type`.** The canonical-briefing view keeps default `None` (no per-bullet finding_type there yet).
- **Executable / unknown behavior unchanged.** Rigby T1 SIGN Ask #3(b) verdict: don't tighten `executable` in the same PR — that's a second axis of change that would confound evaluation.

**Tests:** 19 new tests in `core/tests/test_s2993_briefing_spec_prompt_branching.py` covering:

- `_resolve_prompt_shape` mapping (case-tolerant, total, fall-through)
- `_build_spec_prompt` routing to the correct sub-builder
- `generate_spec_body` extras metadata per finding_type
- Fail-open placeholder copy divergence per shape
- Send-to-rigby view forwards `finding.finding_type` through to Deliverable metadata (3 tests — one per class)

Pre-existing S2992 classifier + canonical-briefing suites re-run (44 tests, all green).

## SIGN discipline (PLAYBOOK-7.7.2)

- **T1 SIGN** — Rigby returned real `orm_inspect_tool` results on Ask #1: sampled 3 real `decision_evidence` rows from the 900-row corpus (`fb90b82f-…` "Zero visibility into 9.8% of frontend HTTP surface." / `fa569deb-…` "No token attach on bypass path." / `f8a6e40c-…` `AgentLearningService` writes to Redis DB 5 directly). All three read as boundary/contract evidence statements; framing verified against real data before code. Ask #2 (downstream semantic assumptions) grep-verified — Deliverable renderers + list endpoints operate on schema + headers, not on the SEMANTIC intent of `acceptance_criteria` (`test_canonical_briefing.py` asserts presence + shape, not "must be engineering AC"). Ask #3 zoom-out: AGREE / AGREE / DISAGREE (low risk) / AGREE.

- **A2 SIGN** — Post-merge, I POSTed real `send-to-rigby` dispatches (real gpt-5-mini roundtrip) against 3 open findings (one per class) via APIClient with `SERVER_NAME='localhost'`. All 3 returned 201. Rigby independently ran `orm_inspect_tool action=filter model=Deliverable filters={"metadata__has_key":"spec_prompt_shape"} order_by=-created_at limit=5` and verified the shape mapping: decision_evidence → `evidence_capture`, executable → `engineering`, unknown → `engineering`. She also used `deliverable_tool detail` to eyeball the actual LLM output of the decision_evidence deliverable (`e51207dc-…`) — goal reads "Record that F-VIP-1 (Cat A baseline) and F-C-VIP-1 (Cat C) are the same issue lineage…" (capture, not implement); all 4 acceptance criteria are verification steps ("Open …", "Confirm …", "Locate …"). The reframe took.

## v2 sequence status (post-S2993)

- [x] #1 close_mode taxonomy — S2991
- [x] #2 finding_type classifier + backfill — S2992
- [x] #3 spec-generator prompt branching on finding_type — **S2993 (this handoff)**
- [x] #5 orm_inspect_tool allowlist (ORM half) — S2991 (`web_fetch_tool` cookies deferred)
- [ ] #4 staleness detector at ingest — carry-forward
- [ ] #6 Rigby-SIGN nudge in UI for `finding_type=decision_evidence` — carry-forward (now unblocked)
- [ ] #7 F-A2-equivalent for downstream consumers — carry-forward
- [ ] #8 wire-through smoke-check AC for half-wired findings — carry-forward

**#3 was the smallest remaining piece.** With prompt-branching shipped, the natural next opener is likely #6 (Rigby-SIGN UI nudge; now unblocked) or #4 (staleness detector).

## Zoom-out folds (PLAYBOOK-6.10.8)

**Fold A (Rigby A2 zoom-out (b)) — `informational`, already mitigated.** Concern: adding `spec_prompt_shape` + `finding_type_used` to Deliverable.metadata creates an observable field downstream tooling might rely on. Mitigation already in place: values are stable (`engineering`, `evidence_capture`), `spec_prompt_version` already versions the prompt schema. If we rename shapes later, do it with a compatibility alias. No follow-up PR needed.

**Fold B (Rigby A2 zoom-out (c)) — `future_trigger` for Rigby Tool Gap Ledger.** Rigby A2 dispatch workflow only learns "which shape ran" after LLM tokens are spent. A cheap dry-run preview surface (`would_use_shape / finding_type_used / spec_prompt_version` without calling the LLM) would let Rigby preview a dispatch before burning tokens. Logging to Rigby Tool Gap Ledger as next-slate candidate. Not blocking this PR.

**Fold C (T1 SIGN Ask #3(b) — executable tightening) — `future_trigger`.** Rigby correctly gated: don't tighten `executable` prompt in the same PR as evidence-branching. Open as a distinct follow-on once we've seen quality stats on evidence_capture output.

## Signal-tweak carry-forward from S2992 (still open)

- `boundary drift` phrasing lands in `unknown` (regex expects `boundary (observation|violation)`)
- `VERIFIED at HEAD` evidence records land in `executable` because they cite `file:line`

No 2nd independent trigger surfaced this session. Combine into a signal-tweak PR when a 2nd trigger lands.

## Carry-forward (also open)

- **`web_fetch_tool` session cookies (deferred half of v2 item #5)** — bigger design change, security review needed.
- All older S2989-S2992 seeds (see 00-START).

## HEAD / recycle state

- `f533cacf8` — feat(s2993) PR #3653 (this session's feature PR)
- Recycle-all clean at `sha=f533cacf8be0` post-merge.
- 3 real send-to-rigby A2 deliverables persisted:
  - `6c43078e-…` (unknown → engineering)
  - `3f42fefa-…` (executable → engineering)
  - `e51207dc-…` (decision_evidence → evidence_capture)

## Files touched

- `core/services/briefing_spec_generator.py` — router, evidence prompt, placeholder-per-shape, extras
- `core/views_doc_research_findings.py` — forward `finding.finding_type`
- `core/tests/test_s2993_briefing_spec_prompt_branching.py` — new test file (19 tests)

## Playbook rule exercise

- **PLAYBOOK-7.7.1** (Spec→Ship contract) — Flow B (spec-originated from S2991's v2 list; 00-START directive). Framing → Rigby T1 SIGN → code → tests → PR → Rigby A2 SIGN → merge → recycle.
- **PLAYBOOK-7.7.2** (SIGN evidence discipline) — T1 SIGN Ask #1 sampled 3 real corpus rows via `orm_inspect_tool`. A2 SIGN independently ran `orm_inspect_tool filter` + `deliverable_tool detail` to verify shape mapping + LLM output. Zero rubber-stamping.
- **PLAYBOOK-7.7.3** (Chris-facing decision framing) — No Chris-facing decision required this session; 00-START directive was already ratified at S2992 close.
- **PLAYBOOK-6.10.8** (fold classification) — 3 folds classified (A `informational`, B `future_trigger`, C `future_trigger`).
- **PLAYBOOK-7.4.4** (recycle after merge) — `make recycle-all` post-PR-#3653 (backend-only diff, HEAD-range path-diff correctly skipped frontend rebuild).
- **`feedback_verify_at_raw_orm_before_trusting_tool_no_data`** — Rigby T1 SIGN Ask #1 verified corpus rows exist before framing the prompt reframe; if the sample had returned engineering-ish content the whole design would have needed a rethink.
- **`feedback_zoom_out_ask_per_rigby_sign`** — Both SIGN cycles included a zoom-out ask; A2 surfaced Fold B (ledger candidate) and Fold A (already mitigated).
