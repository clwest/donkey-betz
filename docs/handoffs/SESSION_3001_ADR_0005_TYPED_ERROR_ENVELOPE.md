---
title: "SESSION 3001 — ADR-0005 Typed Error Envelope Contract (PROVISIONAL) — Chris-ratified"
session: 3001
date: 2026-07-27
type: adr_ratification_close
merge_shas:
  - "f87ae95ef"   # PR #3672 — ADR-0005 typed error envelope contract
prs:
  - 3672
related_arcs:
  - "Group 2400 Auth (S2400-S2499 closed 2026-07-05) — parent verification arc"
  - "Group 2500 API (S2500-S2599 closed 2026-07-06) — design-prep source arc"
  - "S3001 opened on pivot decision after v2 findings-surface arc close (S2991-S3000)"
consumes:
  - "2503 §19.1 R1 CRITICAL Chris-D-verdict-request for typed-error-envelope subset"
  - "2404 §19.1 Cat D PROPOSED PRIMARY γ mechanism"
  - "2499 §8.4 T-slot cross-arc handoff bundles + 2599 §8 T-slot follow-on queue"
---

# S3001 — ADR-0005 Typed Error Envelope Contract (PROVISIONAL) — **first post-arc ADR post-v2**

**Status:** CLOSED. One ADR ratification PR merged. HEAD `f87ae95ef` on main. First ADR ratified since ADR-0004 (2026-07-07, Arc I-0200).

## Session shape

Chris opened with "Please begin" — S3001 arrived with no directive because v2 findings-surface arc drained at S3000. Presented Chris a pivot menu (A: fresh research arc / B: drain fold ledger / C: Playbook amendment / D: your priority). Chris selected **A → 2400 Auth**, citing a prior-session scoping suggestion.

**Verification broke the label.** Grep of `docs/research/domains/auth/` returned a full arc already executed 2026-07-05 — parent scoping + 4 children (Cat A/B/C/D) + canonical summary. Chris's quoted suggestion predated that arc (drafted ~S2099 queue proposal). Same pattern for Group 2500 API (closed 2026-07-06). This is the second consecutive session where verifying a carry-forward at raw code corrected a mis-scoped intent (S3000 was the first — `feedback_verify_at_raw_orm_before_trusting_tool_no_data` cousin).

Pivoted to **A3 → typed-error-envelope specifically** after discovering `docs/research/domains/api/2503_api_error_envelope_refresh_logout_contracts_design_prep_audit.md` already existed — the design-prep phase was banked. Natural next artifact = ADR ratification, not more research.

## What shipped

**PR #3672 (`f87ae95ef`) — ADR-0005 Typed Error Envelope Contract (PROVISIONAL) — Chris-ratified 2026-07-27.**

327 lines, docs-only, reversibility 4. Ratifies the following typed-error-envelope contract:

- **§3.1 Mechanism** — Cat D **γ** (React Query onError + top-level ErrorBoundary + QueryClient default `onError`) as platform-canonical mechanism. Three layers: Layer 1 (QueryClient default), Layer 2 (top-level ErrorBoundary), Layer 3 (per-hook opt-in).
- **§3.2 SoT emission shape** — `APIResponseEnvelope` (Family B at `core/api_responses.py:15-234`) as backend target shape. **Opt-in, not mandate** — Family A `{"detail":...}` remains DRF default, tolerated at consumer via shape-agnostic Layer 1 handler.
- **§3.3 SHAPE-BLIND interceptor** — retained unchanged at `api.ts:63-82` (drifted from 2503's `43-62`; structure IDENTICAL). Elevation optionality preserved for future ADR-N (if Chris later ratifies Family A → Family B mandate).
- **§3.4 Nested UX policy** — Cat C **β "explicit re-login"** as default UX policy nested inside γ Layer 1 `onError` handler (per 2503 §9.1 Rigby Q6 fold reconciliation: γ mechanism ⊃ β UX policy). Session-expired copy bounded to token/session lifecycle framing.
- **§3.5 F-C-VIP-1 scope-tightening** — γ Layer 1 default handler MUST NOT surface account-expiry copy until `VIPInvite.account_expires_at` is enforced.

**§2.4 explicit non-decisions:** does NOT ratify Cat C session-lifecycle α/β/γ, Cat D whitelist-replacement γ, Cat A Path A/B/C backend contract SoT, Cat D permission-floor registry, REST↔WS T7 message-contract, F-C-VIP-1 enforcement mechanism, or backend `EXCEPTION_HANDLER` implementation choice. Each deferred to a future ADR-N per §8 Follow-on ADRs.

**§4.1 Post-arc T-slot enumeration** — 7 T-slots named as post-arc requirements:

- **T-ENVELOPE-0** (BLOCKING PREREQUISITE) — R6 top-level ErrorBoundary framework. Blocks γ **Layer 2 only**; Layer 1 + Layer 3 can ship independently.
- **T-ENVELOPE-1** — QueryClient default `onError` at `frontend/src/main.tsx`. Layer 1 implementation. **Next session's primary directive.**
- **T-ENVELOPE-2** — Backend `EXCEPTION_HANDLER` choice + per-endpoint Family B adoption ramp.
- **T-ENVELOPE-3** — "Session expired" modal/toast UI component.
- **T-ENVELOPE-4** — Per-hook opt-in `onError` migration ramp for 803 consumer call-sites.
- **T-ENVELOPE-5** — Interceptor elevation to shape-normalizer (optional per §3.3).
- **T-ENVELOPE-6** — Telemetry hookup (Cat C CF-C3 handoff to Group 1700 Observability).
- **T-VIP-1** — F-C-VIP-1 `VIPInvite.account_expires_at` runtime enforcement + periodic cleanup (referenced as risk-gate, not owned).

## The Rigby T1 SIGN — 2 dispatch turns

**Turn 1 (arc pin pa-8e17b50843a34be5):**
- **Q1 AGREE + minor STRENGTHEN** — content fidelity to 2503 §19.1 + §9.1 + §14.7 verified with citations. One tension flagged: `provisional_reason` frontmatter said "BLOCKING PREREQUISITE for γ mechanism" but body §4.2 argued Layer 1 can ship without R6. Fold A applied pre-ratification.
- **Q2 STRENGTHEN** — Rigby honestly declined to enumerate T-slots without reading §4.1 (her tool_run truncated ADR excerpt at line 220). Required re-issue.
- **Q3 BLOCKED** — Rigby explicitly refused to rubber-stamp HEAD empirical claims (zero ErrorBoundary / APIResponseEnvelope location / api.ts interceptor line) without tool_runs. **Per `feedback_verify_rigby_tool_runs_before_trusting_sign` — this is the SIGN discipline working correctly**, not a failure. Required re-issue with explicit tool-run instructions.
- **Q4 substantive zoom-out** — (i) narrow ADR scope is right (vs omnibus bundling Cat C + Cat D); (ii) provisional_reason wording should reflect Layer-1 independence (aligned with Q1 STRENGTHEN); (iii) coupling risk of "γ ratified" implying interceptor policy is preserved by §3.3 optionality wording.

**Turn 2 completion pass:**
- **Q2 AGREE** — 7 T-slots verified aligned with 2499 §8.4 + 2599 §8 evidence chain; T-ENVELOPE-1 → T-ENVELOPE-0 dependency edge confirmed via tool_runs.
- **Q3 AGREE** — all 3 HEAD empirical claims tool-verified: (a) zero ErrorBoundary/componentDidCatch/getDerivedStateFromError in `frontend/src/`; (b) APIResponseEnvelope class at `core/api_responses.py:15`; (c) response interceptor at `api.ts:63-82` SHAPE-BLIND structure identical to 2503 baseline.

**Fold A** landed pre-Chris-ratification. Cycle 2 NOT scheduled.

## Zoom-out folds (PLAYBOOK-6.10.8)

**Fold A (Rigby Q1 STRENGTHEN + Q4 (ii)) — same-PR mitigable.** Frontmatter `provisional_reason` wording sharpened to reflect γ Layer 1 + Layer 3 can ship independently of R6 ErrorBoundary; only Layer 2 is blocked. Applied via Edit pre-ratification.

**Fold B (Rigby Q4 (iii)) — `informational`.** Downstream misread risk that "γ ratified" implies interceptor policy is preserved by §3.3 wording. Watch for future ADR-N (Family B mandate) to potentially need explicit re-anchoring; not a rule candidate yet.

**Fold C (scope-recovery — S3001-specific) — potential Playbook rule candidate.** Pattern: **"When Chris quotes a prior-session scoping suggestion, verify the target research slot state before accepting the scope."** At S3001 open, prior-session Claude's "2400 Auth arc scoping" suggestion referenced a slot that was already fully executed 22 days prior. `git log` + `ls docs/research/domains/<slug>/` before ratifying a quoted scope would have caught it in 30 seconds. 1st concrete instance this session (S3000 had the spiritual cousin at carry-forward-label scope; this is at cross-session-quote scope). Rule-worthy IF a 2nd similar instance surfaces — for now, `informational` with active-watch trigger.

## v2 arc post-close observation

The findings-surface v2 arc (S2991–S3000, 12-of-12 shipped) is COMPLETE. S3001 is the first post-v2 session and it followed a fundamentally different session shape:

- v2 sessions: 1 feature PR per session, `PLAYBOOK-7.7.1` Flow A/B with T1 → A2 SIGN cycles
- S3001: 1 ADR ratification PR, `PLAYBOOK-16` draft-first workflow, Rigby T1 SIGN across 2 dispatch turns without an A2 SIGN (there's no runtime behavior to verify at A2 for a docs-first ADR)

This is the second post-v2 workflow shape observed (ADR-0004 at S2701 was first). Both used draft-first + Rigby SIGN pre-Chris-ratification. Not a codification candidate — this shape is already documented in ADR-0001 §3.6 lifecycle + playbook §16 draft-first.

## HEAD / recycle state

- `f87ae95ef` — PR #3672 (ADR-0005) merged post-`c9b09d97d` (S3000 close cascade)
- Recycle target: post-docs-cascade-merge — see close-cascade section below

## Files touched

- `docs/adr/ADR-0005-typed-error-envelope-contract.md` — CREATED (327 lines)
- `docs/INDEX.md` — regenerated via `build_docs_index` (adds ADR-0005 entry)
- `00-START-NEXT-SESSION.md` — refreshed for S3002 primary directive = T-ENVELOPE-1
- `docs/handoffs/SESSION_3001_ADR_0005_TYPED_ERROR_ENVELOPE.md` — this file
- `tools/pa_local.sh` — wrapper pin bump at close via `session_lifecycle close`

## Playbook rule exercise

- **PLAYBOOK-7.7.1** (Spec→Ship contract) — ADR-authoring shape, NOT feature-shipping shape. Investigation → design-prep (already banked at 2503) → ADR draft → Rigby T1 SIGN → Chris ratification → PR → merge. No T1 SIGN pre-draft because the ADR body IS the design synthesis; T1 SIGN happens on the drafted body.
- **PLAYBOOK-7.7.2** (SIGN evidence discipline) — **exemplar session for this rule.** Rigby's Q3 BLOCKED verdict — explicitly declining to rubber-stamp HEAD empirical claims without tool_runs — is the rule working as designed. Turn 2 completion pass produced 9 real tool_runs (ADR reads + 2499/2599 reads + 3 grep verifications + api.ts read + APIResponseEnvelope grep). Empty tool_runs = re-issue signal held.
- **PLAYBOOK-7.7.3** (Chris-facing decision framing) — S3001 open menu was A/B/C/D with plain-English "do we lose anything? / is it more work later?" per `feedback_plain_english_decision_framing_for_chris`. Chris's redirect at the 2400-slot-verified moment ("A3 typed-error-envelope, check today's api files first") was itself a plain-English decision route.
- **PLAYBOOK-7.4.4** (recycle after merge) — docs-only diff; recycle-all still runs per S2978 refinement safe-default rule.
- **PLAYBOOK-16** (draft-first) — ADR-0005 authored with `status: draft` + `provisional: true`; flipped to `accepted` only after Chris "Ratify and open the PR" verdict.
- **`feedback_verify_at_raw_orm_before_trusting_tool_no_data`** — S3001 verified 2400 slot state at raw filesystem before accepting Chris's quoted scope, caught the 22-day-stale scoping suggestion.
- **`feedback_verify_rigby_tool_runs_before_trusting_sign`** — Rigby's Q3 BLOCKED was the rule enforcing itself; re-issue with tool-forcing directives produced substantive verification.
- **`feedback_zoom_out_ask_per_rigby_sign`** — Q4 zoom-out surfaced Fold A (frontmatter wording) which would have been invisible from a Q1/Q2/Q3-only routing.
- **`feedback_claude_rigby_agree_first_chris_yes_no`** — Joint Rigby+Claude AGREE achieved across 2 SIGN turns before routing to Chris for yes/no.
- **`feedback_plain_english_decision_framing_for_chris`** — All 3 Chris-facing decision moments (A/B/C/D pivot / A3 target / Ratify & merge) framed with "do we lose anything?" + "is it more work later?" tables.
- **`feedback_per_pr_summary_signals_close_readiness`** — Post-merge summary included explicit "still open before close" checklist.

## Rigby Tool Gap Ledger — no new entries

No new PA tool-surface limitations surfaced this session. `repo_tool` (Rigby's read/grep tool) worked correctly for all Q3 empirical verifications. No fallback to Django shell or APIClient needed.

## Substrate — what next session inherits

- **T-ENVELOPE-1 as S3002 primary directive** — QueryClient default `onError` wire-up at `frontend/src/main.tsx`. Can ship independently of R6 ErrorBoundary. First implementation PR discharging ADR-0005 §3.1 Layer 1.
- **T-ENVELOPE-0 as parallel candidate** — R6 top-level ErrorBoundary framework establishment. Dual-owned Cat D + Group 2200 post-arc T-slot. Blocks γ Layer 2 shipment; can run parallel to T-ENVELOPE-1.
- **Fold C watch** — 2nd instance of prior-session-scoping-quote-vs-slot-state mismatch would trigger Playbook amendment consideration.
- **v2 arc carry-forwards** — 10+ fold ledger items from S2991-S3000 still open (see 00-START); paper-cuts, ranked by unblocking-imminent-arc criterion per `feedback_engineering_bias_over_audit`.
