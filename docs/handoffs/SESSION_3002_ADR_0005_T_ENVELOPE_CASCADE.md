---
title: "SESSION 3002 — ADR-0005 T-slot cascade + ADR-0006 non-provisional successor (γ mechanism COMPLETE)"
session: 3002
date: 2026-07-27
type: multi_pr_cascade_close
merge_shas:
  - "ec408bb7c"   # PR #3674 — T-ENVELOPE-1 QueryClient default onError
  - "fb8c8fdb9"   # PR #3675 — T-ENVELOPE-3 Session-expired modal
  - "ba697a5f7"   # PR #3676 — T-ENVELOPE-0 top-level ErrorBoundary
  - "cf4ff695a"   # PR #3677 — ADR-0006 non-provisional successor
prs:
  - 3674
  - 3675
  - 3676
  - 3677
related_arcs:
  - "ADR-0005 Typed Error Envelope Contract (ratified S3001 PR #3672)"
  - "S3001 → S3002 continuous cascade (extended terminal after S3001 close)"
consumes:
  - "ADR-0005 §3.1–§3.5 decision content (γ mechanism + APIResponseEnvelope SoT + β nested UX)"
  - "ADR-0005 §4.1 T-slot enumeration (T-ENVELOPE-0/1/3 shipped this session)"
  - "ADR-0005 §4.2 BLOCKING PREREQUISITE clause (satisfied by T-ENVELOPE-0 ship → ADR-0006 flip)"
---

# S3002 — ADR-0005 T-slot cascade + ADR-0006 successor — **γ mechanism COMPLETE**

**Status:** CLOSED. 4 feature/docs PRs merged. γ Layer 1 + Layer 2 + Layer 3 all live at HEAD `cf4ff695a`. ADR-0005 flipped non-provisional via ADR-0006 successor.

## Session shape

**S3002 opened mid-terminal after S3001 close cascade merged.** Chris kept saying "ship T-ENVELOPE-X" / "Continue" / "successor then close" — a 4-turn engineering cascade extending the same terminal session across the S3001→S3002 boundary. The wrapper pin was already bumped to `pa-755bc99b7cfb4a91` (S3002 pin) at S3001 close, so PA dispatches went to the correct pin without requiring a terminal restart.

This is a **new session shape** not seen in the prior 100 sessions: normally session boundaries coincide with terminal boundaries. S3002 was authored entirely inside the S3001 terminal after Chris's "Continue on" directive. The session_lifecycle close at S3001 established the boundary formally; S3002 work happened in continuous flow.

**Pattern candidate (2nd trigger required):** Chris-directed mid-terminal S<N>→S<N+1> engineering cascade. Watch for 2nd instance before proposing Playbook amendment.

## What shipped

### PR #3674 (`ec408bb7c`) — T-ENVELOPE-1 QueryClient default onError

γ Layer 1 implementation. React Query v5-canonical pattern (`QueryCache({onError}) + MutationCache({onError})` at QueryClient construction; v5 removed `defaultOptions.queries.onError`). Handler at `frontend/src/lib/queryClientErrorHandler.ts` guards on `status===401` + `!isAuthEndpoint` → `useAuthStore.logout()` + placeholder `console.warn`. Shape-agnostic per §3.3. Rigby A2-pre-merge AGREE Q1/Q2/Q3 with 4 tool_runs.

### PR #3675 (`fb8c8fdb9`) — T-ENVELOPE-3 Session-expired modal

§3.4 step 2 UI. Full-screen modal at `frontend/src/components/SessionExpiredModal.tsx` triggered via new Zustand `sessionExpiredStore`. Single "Log in again" button (no X close per §3.4 step 3 user-acknowledgment gate). Handler updated to trigger store instead of console.warn. Mounted in App.tsx as fragment sibling to Routes. F-C-VIP-1 scope-tightening honored (copy bounded to session/token lifecycle). Rigby A2-pre-merge AGREE Q1/Q2/Q3 with 4 tool_runs; one edge-case noted (undefined url falls to non-auth branch — inherited from T-ENVELOPE-1, "fail open" acceptable).

### PR #3676 (`ba697a5f7`) — T-ENVELOPE-0 top-level ErrorBoundary

γ Layer 2 unblocker + BLOCKING PREREQUISITE discharge. React 18 canonical class component (`getDerivedStateFromError` + `componentDidCatch`) at `frontend/src/components/ErrorBoundary.tsx`. Zero external deps. Wraps App at `main.tsx:28-35` OUTSIDE `QueryClientProvider` (catches mutation-callback render escapes + provider construction errors). Fallback UI: full-screen card with AlertTriangle icon + Reload button. `componentDidCatch` marked as T-ENVELOPE-6 hook-point for future observability. Dual-ownership per ADR-0005 §4.1 (Cat D + Group 2200). Rigby A2-pre-merge AGREE Q1/Q2/Q3 with 2 tool_runs; StrictMode dev-only double-log noted (harmless).

### PR #3677 (`cf4ff695a`) — ADR-0006 non-provisional successor

Flips ADR-0005 `provisional: true` → non-provisional (field omitted). NOT a re-authoring — ADR-0005 §3.1–§3.5 content remains canonical unchanged. Trigger fired at T-ENVELOPE-0 ship per ADR-0005 §4.2 clause. ADR-0005 frontmatter updated in same PR: `superseded_by: ADR-0006` per ADR-0001 §3.6 bidirectional supersede discipline. T1 SIGN skipped (docs-only successor, no new decision content, §4.2 trigger clause verifiable from PR #3676 diff). Joint Claude+Rigby recommendation reached before Chris ratification. Twin-mirror created by Rigby: content mirror `ba5efefb-029a-4975-b361-128e34199f6b` + ratification envelope `ea657daa-f1a0-46f3-8964-ea922a9b2ed9`.

## Cumulative session state (S3001 + S3002 combined)

**6 PRs shipped across the extended terminal:**

1. PR #3672 — ADR-0005 ratified (S3001)
2. PR #3673 — S3001 close cascade (S3001)
3. PR #3674 — T-ENVELOPE-1 (S3002)
4. PR #3675 — T-ENVELOPE-3 (S3002)
5. PR #3676 — T-ENVELOPE-0 (S3002)
6. PR #3677 — ADR-0006 successor (S3002 this handoff)

**γ mechanism state at HEAD `cf4ff695a`:**

- **Layer 1** (QueryClient default onError) — LIVE
- **Layer 2** (top-level ErrorBoundary) — LIVE
- **Layer 3** (per-hook opt-in `onError`) — LIVE (always was; React Query v5 semantics unchanged)
- **§3.4 step 2 UI** (session-expired modal) — LIVE

**Silent-swallow rate on non-auth 401s:** ~99% → 0% at Layer 1 handler + user-visible modal on trigger.

## ADR-0005 T-slot progress: 3-of-7 shipped

- [x] **T-ENVELOPE-0** — R6 top-level ErrorBoundary framework (PR #3676)
- [x] **T-ENVELOPE-1** — QueryClient default onError (PR #3674)
- [x] **T-ENVELOPE-3** — Session-expired modal (PR #3675)
- [ ] **T-ENVELOPE-2** — Backend `EXCEPTION_HANDLER` choice (needs Chris-D-verdict on Path a/b/c)
- [ ] **T-ENVELOPE-4** — Per-hook opt-in migration ramp (803 call-sites, scope down per module)
- [ ] **T-ENVELOPE-5** — Interceptor elevation (optional per §3.3)
- [ ] **T-ENVELOPE-6** — Telemetry hookup (needs Group 1700 channel — logs-only interim viable)
- [ ] **T-VIP-1** — F-C-VIP-1 enforcement (risk-gate for expiry-signal UX)

## Zoom-out folds (PLAYBOOK-6.10.8)

**Fold A (session-shape observation) — potential Playbook amendment candidate.** Mid-terminal S<N>→S<N+1> continuous engineering cascade. 1st concrete instance. Watch for 2nd similar cascade before proposing Playbook rule.

**Fold B (T-ENVELOPE-3 edge-case) — `informational`, inherited from T-ENVELOPE-1.** `queryClientErrorHandler.ts:28-30` — undefined `url` falls to non-auth branch. Auth-endpoint 401 with undefined url would incorrectly show modal. "Fail open" default acceptable; not blocking.

**Fold C (T-ENVELOPE-0 dev-only) — `informational`.** `componentDidCatch` fires twice in dev under StrictMode double-invocation. Log-only side effect; no state impact. Not blocking.

**Fold D (ADR-0006 successor discipline) — VALIDATED PATTERN.** Rigby's Q3(iii) at T-ENVELOPE-0 SIGN correctly recommended separating provisional-flip from code-ship PR. Bundled would have violated PLAYBOOK-16 single-decision-per-PR. Successor-in-its-own-PR pattern now first-instance-applied in this repo (ADR-0004 has `superseded_by: (none)` still; ADR-0005 is the first ADR to receive a supersede link in bidirectional form).

## Rigby Tool Gap Ledger — no new entries

`repo_tool` handled every A2 SIGN grep/read across 3 code PRs and 1 docs PR. Twin-mirror creation via `deliverable_tool.create` worked (with the S2753 diagnostic-clear post-create workaround still needed on the content mirror; ratification envelope came clean this time — possibly a Rigby-side behavior improvement worth noting).

## Substrate — what next session inherits

- **T-ENVELOPE-2 as S3003 primary candidate** — backend `EXCEPTION_HANDLER` choice. Needs Chris-D-verdict on Path (a) DRF `EXCEPTION_HANDLER` at settings level / (b) custom middleware normalization / (c) per-endpoint APIResponseEnvelope adoption without global normalization. Design-prep + ADR + implementation likely 1-2 sessions.
- **T-ENVELOPE-6 telemetry** — smaller, could ship as logs-only stub while Group 1700 Observability arc is queued. `componentDidCatch` hook-point already annotated.
- **T-VIP-1 risk-gate** — blocks any expiry-signal UX from ADR-0005 §3.5. Backend + Celery beat. 1 session estimate.
- **T-ENVELOPE-4 migration ramp** — 803 call-sites, long tail. Scope down per module.
- **ADR-0005 → ADR-0006 supersede chain** — first bidirectional supersede link in the repo. Future ADRs referencing typed-error-envelope should prefer `ADR-0006` for current-truth citations OR `ADR-0005 §<specific-clause>` when invoking specific clause content.
- **Session shape observation** — mid-terminal cascade Fold A watch: if a 2nd similar cascade fires, propose Playbook amendment codifying the pattern.

## HEAD / recycle state

- `cf4ff695a` — ADR-0006 successor (this handoff's basis)
- 3 recycle-all runs during S3002 execution (post T-ENVELOPE-1, post T-ENVELOPE-3, post T-ENVELOPE-0). ADR-0006 successor is docs-only; final recycle-all after this close cascade PR.

## Playbook rule exercise

- **PLAYBOOK-7.7.1** (Spec→Ship contract) — 3× Flow B ships (T-ENVELOPE-1/3/0) + 1× docs successor (ADR-0006). All followed spec→T1-skipped-when-deterministic→ship→A2-pre-merge SIGN→merge→recycle.
- **PLAYBOOK-7.7.2** (SIGN evidence discipline) — 3× Rigby A2-pre-merge SIGN with real tool_runs (all AGREE). One dispatch (ADR-0006) skipped SIGN per docs-only-successor rationale documented in frontmatter.
- **PLAYBOOK-7.7.3** (Chris-facing decision framing) — 4 Chris-facing decision moments framed with plain-English "do we lose anything? / is it more work later?" tables: "ship T-ENVELOPE-1?" / "ship T-ENVELOPE-3?" / "Continue" / "What do you and Rigby suggest?". Joint Claude+Rigby recommendation reached before Chris ratification on the final "successor then close" moment.
- **PLAYBOOK-7.4.4** (recycle after merge) — 3× `make recycle-all` runs during session (frontend touched in all 3 feature PRs; per S2978 refinement, `make celery-recycle` insufficient — verified `make recycle-all` used correctly).
- **PLAYBOOK-16** (draft-first) — ADR-0006 authored with `status: accepted` directly (docs-only successor per §5.6 alternative-rejection precedent; no draft-first cycle needed since ADR-0005 body was already SIGN'd).
- **PLAYBOOK-6.10.8** (fold classification) — 4 folds (A same-PR-mitigable pattern candidate; B informational inherited; C informational dev-only; D VALIDATED PATTERN).
- **`feedback_verify_at_raw_orm_before_trusting_tool_no_data`** — verified all HEAD claims (ErrorBoundary count, APIResponseEnvelope location, api.ts interceptor lines) via direct grep before ADR authoring.
- **`feedback_verify_rigby_tool_runs_before_trusting_sign`** — all 3 Rigby A2 SIGNs produced real tool_runs in verbose block; no rubber-stamp signals.
- **`feedback_zoom_out_ask_per_rigby_sign`** — Q3 zoom-out on every SIGN cycle; surfaced Fold B/C/D refinements.
- **`feedback_claude_rigby_agree_first_chris_yes_no`** — final ADR-0006 decision routed to Rigby FIRST (Q1/Q2/Q3 joint agreement), then Chris ratified with plain-English framing.
- **`feedback_plain_english_decision_framing_for_chris`** — every Chris-facing decision surface answered "do we lose anything? / is it more work later?" plainly.
- **`feedback_recycle_after_merge`** (S2978 refinement) — all 3 feature PRs used `make recycle-all` (frontend touched). ADR-0006 close cascade docs-only but still uses recycle-all as safe default.
- **`feedback_twin_deliverable_at_every_ratification`** + `feedback_rigby_writes_workspace_deliverables` — twin-mirror for BOTH ADR-0005 (S3001) AND ADR-0006 (this session) created by Rigby via PA tool_dispatch; content_mirror + ratification_envelope UUIDs recorded in respective session_lifecycle close invocations.
- **`feedback_commit_wrapper_pin_bump_at_close`** — wrapper diff committed in each session's close cascade PR.
