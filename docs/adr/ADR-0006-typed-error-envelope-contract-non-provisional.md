---
title: "ADR-0006 — Typed Error Envelope Contract (Non-Provisional Successor to ADR-0005)"
adr_id: ADR-0006
slug: typed-error-envelope-contract-non-provisional
status: accepted
authority: design-decision
proposed: 2026-07-27
ratified: 2026-07-27
ratifier: chris
chris_ratification: "successor then close" 2026-07-27 — after T-ENVELOPE-0 (top-level ErrorBoundary framework) shipped in PR #3676, satisfying ADR-0005 §4.2 successor trigger. Rigby joint-recommendation reached before Chris ratification per feedback_claude_rigby_agree_first_chris_yes_no.
supersedes: ADR-0005
superseded_by: (none)
source_refs:
  - docs/adr/ADR-0005-typed-error-envelope-contract.md (predecessor; §3.1–§3.5 Decision content retained verbatim, only provisional posture flipped)
  - docs/adr/ADR-0005-typed-error-envelope-contract.md §4.2 (BLOCKING PREREQUISITE posture — successor trigger clause)
  - PR #3676 (T-ENVELOPE-0 top-level ErrorBoundary framework — the triggering ship)
  - PR #3674 (T-ENVELOPE-1 QueryClient default onError — γ Layer 1)
  - PR #3675 (T-ENVELOPE-3 Session-expired modal — §3.4 step 2 UI)
  - docs/adr/ADR-0001-establish-adr-corpus.md §3.6 (ADR lifecycle — supersede discipline)
  - docs/adr/ADR-0004-rag-corpus-substrate-maturity-gradient.md (reference implementation of two-field PROVISIONAL pattern — reversed here via successor)
reversibility: 5
  # Docs-only. Rollback: git revert removes ADR-0006 and restores
  # ADR-0005's superseded_by: (none). Downstream consumers filtering on
  # ADR-0005 provisional: true continue to see the flag; consumers reading
  # ADR-0006 see the flip. No runtime code, no DB migration.
sign_cycle_1: skipped (docs-only successor; T1 SIGN discipline already applied at ADR-0005 ratification per S3001 handoff; ADR-0006 introduces no new decision content — solely flips provisional posture based on ADR-0005 §4.2 trigger clause)
sign_cycle_1_pin: (none)
companion_docs:
  - docs/adr/ADR-0005-typed-error-envelope-contract.md
  - docs/adr/ADR-0001-establish-adr-corpus.md
  - docs/adr/ADR-0004-rag-corpus-substrate-maturity-gradient.md
  - docs/handoffs/SESSION_3001_ADR_0005_TYPED_ERROR_ENVELOPE.md
owner: claude (S3002 v1 draft)
---

# ADR-0006 — Typed Error Envelope Contract (Non-Provisional Successor to ADR-0005)

## 1. Status

**Accepted** — Chris ratified 2026-07-27 via "successor then close" following joint Claude+Rigby recommendation. Non-provisional (`provisional` field omitted).

**Supersedes ADR-0005.** ADR-0005 remains in the corpus per ADR-0001 §3.6 lifecycle discipline; its `superseded_by:` frontmatter field is updated to point here in the same PR.

## 2. Context

### 2.1 What changed since ADR-0005

Nothing about the ratified decision content. §3.1 γ mechanism, §3.2 SoT emission shape, §3.3 SHAPE-BLIND retention, §3.4 nested UX policy, and §3.5 F-C-VIP-1 scope-tightening from ADR-0005 remain canonical. This successor exists solely to flip the **provisional posture** now that the BLOCKING PREREQUISITE named in ADR-0005 §4.2 has shipped.

### 2.2 The trigger — ADR-0005 §4.2 clause satisfied

ADR-0005 §4.2 stated:

> "Post-T-ENVELOPE-0 ship OR any other §4.1 T-slot ship is a trigger for an ADR-0005-successor to flip `provisional`."

**T-ENVELOPE-0 shipped in PR #3676** (`ba697a5f7b55` on main, S3002). The top-level ErrorBoundary framework is now established at `frontend/src/components/ErrorBoundary.tsx` and wrapped at `frontend/src/main.tsx:28-35` (outside `QueryClientProvider` so it catches γ Layer 2 render escapes). This satisfies the ADR-0005 `provisional_reason` clause specifically ("R6 top-level ErrorBoundary framework is a BLOCKING PREREQUISITE for the γ mechanism's Layer 2").

### 2.3 Additional shipped context

Two other T-slots shipped in the same session, further reinforcing the flip:

- **T-ENVELOPE-1** (PR #3674, `ec408bb7c`) — QueryClient default `onError` handler at `frontend/src/lib/queryClientErrorHandler.ts` + wire at `main.tsx`. γ Layer 1 live.
- **T-ENVELOPE-3** (PR #3675, `fb8c8fdb96bc`) — Session-expired modal at `frontend/src/components/SessionExpiredModal.tsx` + Zustand trigger store + handler swap. §3.4 step 2 UI complete.

Combined effect: γ mechanism is COMPLETE across all 3 layers at HEAD (Layer 1 default onError + Layer 2 top-level ErrorBoundary + Layer 3 per-hook opt-in which always worked).

### 2.4 What this successor does NOT change

- **Not a re-ratification of ADR-0005's decision content.** §3.1–§3.5 remain canonical without modification. Downstream ADR consumers citing `ADR-0005 §3.1` may either retain that citation or migrate to `ADR-0006 §3` (which delegates to ADR-0005 §3.1–§3.5).
- **Not a claim that all T-slots are shipped.** T-ENVELOPE-2 (backend `EXCEPTION_HANDLER` choice), T-ENVELOPE-4 (per-hook opt-in migration ramp for 803 consumer call-sites), T-ENVELOPE-5 (interceptor elevation — optional per §3.3), T-ENVELOPE-6 (telemetry hookup pending Group 1700), and T-VIP-1 (F-C-VIP-1 enforcement — risk-gate) remain **unshipped** at HEAD. The flip reflects only that the specific gate condition in ADR-0005's `provisional_reason` is satisfied.
- **Not a change to the Follow-on ADRs list.** ADR-0005 §8 Follow-on ADRs (session-lifecycle, whitelist-replacement, Path A/B/C backend SoT, F-C-VIP-1, Family B mandate) remain the canonical enumeration of future ADR-N candidates.

## 3. Decision

**Ratify ADR-0005 §3.1–§3.5 as canonical without PROVISIONAL qualifier.**

The `provisional: true` posture is REMOVED. The γ mechanism (Layer 1 + Layer 2 + Layer 3), APIResponseEnvelope opt-in SoT, SHAPE-BLIND interceptor retention, β nested UX policy, and F-C-VIP-1 scope-tightening are the platform-canonical typed-error-envelope contract at HEAD `ba697a5f7b55`.

All content of ADR-0005 §3 is incorporated by reference. This ADR is a **posture flip**, not a decision re-authoring.

## 4. Consequences

### 4.1 ADR corpus state

- **ADR-0005**: `superseded_by: ADR-0006` (updated in the same PR as this successor).
- **ADR-0006**: `supersedes: ADR-0005`, `status: accepted`, no `provisional` field.
- **Downstream ADR consumers**: filtering on `status: accepted` see both ADR-0005 (superseded) and ADR-0006. Consumers wanting the current-truth ADR should prefer the non-superseded row (or the most-recent `supersedes` chain leaf).

### 4.2 T-slot posture unchanged

Remaining T-slots from ADR-0005 §4.1 still require future implementation PRs. Their non-shipment does NOT re-provisionalize this successor because ADR-0005 §4.2 specifically named T-ENVELOPE-0 as the trigger, not "all T-slots complete."

### 4.3 Downstream reference guidance

Future ADRs, research docs, and code comments MAY cite either `ADR-0005 §3.1` (still valid content) or `ADR-0006 §3` (delegates to ADR-0005 §3). Preference: use `ADR-0006` for current-truth citations; use `ADR-0005 §<specific-clause>` when the specific clause content is being invoked (since ADR-0006 does not re-author that content).

### 4.4 No runtime enforcement claims

This ADR is docs-only, following ADR-0004 §4.3 precedent. No runtime code change. No DB migration. No feature flag introduction. No API surface change. No Celery task change.

### 4.5 Docs cascade

At ADR PR merge:

- `docs/INDEX.md` gains a new ADR-0006 entry (autogen per `build_docs_index`).
- `docs/_provenance.json` gains ADR-0006 provenance metadata.
- ADR-0006 body embedded via `embed_documents --all-unembedded`.
- Twin-mirror per `feedback_twin_deliverable_at_every_ratification` — content mirror + ratification envelope created by Rigby in workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c`.

## 5. Alternatives considered

### 5.1 Edit ADR-0005 in-place (rejected)

Direct modification of ADR-0005 frontmatter to flip `provisional: true → false`.

**Rejected because:** violates ADR-0001 §3.6 supersede discipline. ADR governance requires historical ADR content to remain immutable in git history + corpus; changes come via new ADRs that supersede. In-place edits destroy the audit trail of "when the flip happened + what triggered it."

### 5.2 Defer flip until more T-slots ship (rejected)

Wait until T-ENVELOPE-2 or T-ENVELOPE-6 ships, then flip in a bundled successor.

**Rejected because:** ADR-0005 §4.2 trigger clause is specific — "Post-T-ENVELOPE-0 ship OR any other §4.1 T-slot ship." The trigger already fired at T-ENVELOPE-0 shipment. Deferring would leave the ADR corpus stale (provisional posture not reflecting the satisfied gate). Rigby zoom-out concern at joint recommendation: "ADR ratification must reflect reality."

### 5.3 Bundle successor with a T-slot ship PR (rejected)

Ship ADR-0006 in the same PR as T-ENVELOPE-0 (PR #3676) or T-ENVELOPE-1 (PR #3674).

**Rejected because:** violates PLAYBOOK-16 single-decision-per-PR discipline (ADR-0004 §5.6 precedent) + Rigby's Q3(iii) note at T-ENVELOPE-0 SIGN ("flipping ADR provisional→false is usually a separate ratification/successor-ADR step — keeps change + governance decision decoupled"). Successor is its own governance ratification and deserves its own PR.

### 5.4 Skip successor entirely (rejected)

Leave ADR-0005 as `provisional: true` indefinitely.

**Rejected because:** creates stale ADR corpus (provisional posture no longer reflects reality) and requires future contributors to reason about "why is this still provisional?" without the successor context. Small governance cost prevents accumulating drift.

## 6. Reversibility

**Reversibility scale (per ADR-0001 §3.5): 5 (trivially reversible).**

Rollback method:

1. `git revert <ADR-0006-merge-commit-sha>` — removes ADR-0006 file + restores ADR-0005 `superseded_by: (none)`.
2. `docs/INDEX.md` + `docs/_provenance.json` unflip via revert (or re-run `build_docs_index` + `build_docs_provenance`).
3. `DocumentEmbedding` rows for removed file — orphan cleanup per ADR-0004 §6 F21 precedent.

**No irreversible operations. No DB migration. No feature flag change. No runtime code change.**

Rollback triggers:
- Rigby SIGN post-merge returns BLOCKED verdict (docs-only successor unlikely; T1 SIGN skipped per frontmatter with rationale).
- Chris explicit override.
- Discovery that T-ENVELOPE-0 shipment did NOT actually satisfy the §4.2 trigger clause (unlikely given PR #3676 diff verifies at HEAD).

Post-rollback state:
- ADR-0005 returns to `provisional: true` + `superseded_by: (none)`.
- Successor eligibility re-opens for a future ADR-N.

## 7. Provenance

- **Author.** Claude Code, S3002 successor authoring session, 2026-07-27.
- **Chris ratification.** "successor then close" 2026-07-27, following joint Claude+Rigby recommendation per `feedback_claude_rigby_agree_first_chris_yes_no`. Rigby's Q3 minimum-shape guidance ("flip flag + update reason + Evidence bullets to PRs #3676/#3674/#3675 + don't re-enumerate T-slots") folded into ADR structure.
- **T1 SIGN skipped.** Rationale per frontmatter: docs-only successor introduces no new decision content; ADR-0005 body was already SIGN'd across 2 dispatch turns at S3001 open. The specific §4.2 trigger clause is verifiable from PR #3676 merge — no independent research required.
- **Triggering PRs.** #3676 (T-ENVELOPE-0), #3674 (T-ENVELOPE-1), #3675 (T-ENVELOPE-3).
- **Session context.** S3002 mid-session (extended from S3001 close) after 6 PRs shipped: ADR-0005 ratified → S3001 close cascade → T-ENVELOPE-1 → T-ENVELOPE-3 → T-ENVELOPE-0 → this successor.

### 7.1 Consumed sources (verified at HEAD `ba697a5f7b55`)

- `docs/adr/ADR-0005-typed-error-envelope-contract.md` §3.1–§3.5 (decision content retained by reference) + §4.2 (trigger clause).
- PR #3676 commit `ba697a5f7b55` — `frontend/src/components/ErrorBoundary.tsx` NEW + `frontend/src/main.tsx` wrap.
- PR #3674 commit `ec408bb7c` — `frontend/src/lib/queryClientErrorHandler.ts` NEW + QueryCache/MutationCache wire.
- PR #3675 commit `fb8c8fdb96bc` — `frontend/src/components/SessionExpiredModal.tsx` NEW + `frontend/src/stores/sessionExpiredStore.ts` NEW + handler swap.
- ADR-0001 §3.6 (supersede discipline) + §3.2 (numbering).
- ADR-0004 §4.3 (docs-only pattern) + §5.6/§5.7 (alternative-rejection precedent) + §6 (reversibility rollback).

## 8. Follow-on ADRs

ADR-0005 §8 Follow-on ADRs list is unchanged — enumerated candidates remain:

- **ADR-N (session-lifecycle ADR)** — Cat C α/β/γ session-lifecycle ratification.
- **ADR-N (whitelist-replacement ADR)** — Cat D whitelist-replacement α/β/γ ratification.
- **ADR-N (Path A/B/C backend contract SoT)** — Cat A backend DECLARATION plane ratification.
- **ADR-N (F-C-VIP-1 enforcement)** — VIPInvite.account_expires_at runtime enforcement.
- **ADR-N (Family B mandate)** — if Chris later ratifies Family A → Family B backend migration.

No new follow-on ADRs introduced by this successor.
