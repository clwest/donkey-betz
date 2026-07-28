# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3001 CLOSED. **ADR-0005 Typed Error Envelope Contract ratified.** T-ENVELOPE-1 opens for S3002.

**One ADR ratification PR merged this session** (ADR-0005, docs-only, PROVISIONAL, Chris-ratified 2026-07-27).

**PR #3672 (`f87ae95ef`) — ADR-0005 Typed Error Envelope Contract (PROVISIONAL).** Discharges 2503 §19.1 R1 CRITICAL Chris-D-verdict-request for the typed-error-envelope subset. Ratifies Cat D γ mechanism (React Query onError + top-level ErrorBoundary + QueryClient defaults), APIResponseEnvelope (Family B) as SoT emission shape (opt-in, not mandate), SHAPE-BLIND interceptor retention with elevation optionality preserved, Cat C β "explicit re-login" nested as UX policy inside γ default handler, F-C-VIP-1 scope-tightening on expiry-signal UX. **Explicitly does NOT ratify** session-lifecycle α/β/γ, whitelist-replacement γ, backend Path A/B/C, permission-floor registry (each deferred to future ADR-N per §2.4).

**7 T-slots named** (T-ENVELOPE-0..6 + T-VIP-1). T-ENVELOPE-0 (R6 top-level ErrorBoundary) is BLOCKING PREREQUISITE for γ Layer 2 only; Layer 1 + Layer 3 can ship independently per §4.2.

**Rigby T1 SIGN complete** across 2 dispatch turns (arc pin `pa-8e17b50843a34be5`): Q1 AGREE + minor STRENGTHEN (Fold A applied) / Q2 AGREE (7 T-slots aligned with 2499 §8.4 + 2599 §8) / Q3 AGREE (3 HEAD claims tool-verified: zero ErrorBoundary + APIResponseEnvelope location + api.ts interceptor line-drift) / Q4 substantive zoom-out (3 concerns preserved).

**HEAD at close:** `f87ae95ef` + docs cascade PR (this file + handoff + INDEX + wrapper pin bump per `feedback_commit_wrapper_pin_bump_at_close`).

Full context:
- `docs/handoffs/SESSION_3001_ADR_0005_TYPED_ERROR_ENVELOPE.md` — includes scope-recovery post-mortem (2400 Auth slot already-executed discovery)
- `docs/adr/ADR-0005-typed-error-envelope-contract.md` — the ADR itself

---

## S3002 primary directive — T-ENVELOPE-1

**Ship QueryClient default `onError` handler at `frontend/src/main.tsx`.** This is ADR-0005 §3.1 γ Layer 1 implementation — the first post-ratification T-slot PR. Can ship independently of R6 ErrorBoundary (T-ENVELOPE-0), which is a Layer 2 blocker only.

### Scope

- **Location:** `frontend/src/main.tsx` (or QueryClient factory site — verify at S3002 open which pattern this codebase uses)
- **Behavior:** default `onError` fires for every query/mutation error not caught by a hook-scoped handler. On 401 response (any shape family per ADR-0005 §3.4):
  1. Clear client-side auth state (`useAuthStore.getState().logout()`)
  2. Surface user-facing "session expired — please log in" modal/toast (T-ENVELOPE-3 provides concrete UI component; T-ENVELOPE-1 wire to placeholder or `console.warn` if T-ENVELOPE-3 not yet shipped)
  3. Redirect to `/login` on user acknowledgment (NOT immediately, unless request URL matches `/auth/` or `/login`)
- **Anti-pattern gate:** default handler MUST NOT surface `VIPInvite.account_expires_at` copy until T-VIP-1 (F-C-VIP-1 enforcement) ships. Session-expired copy bounded to token/session lifecycle framing.
- **Shape-agnostic:** consume `AxiosError` object directly; do NOT branch on `.response.data.detail` vs `.response.data.error.message` (per ADR-0005 §3.3 SHAPE-BLIND interceptor retention decision).

### Estimated size

~30-60 min. QueryClient factory + `onError` default handler + smoke test. Layer 3 opt-in per-hook overrides remain independent post-ship.

### Follow-on T-slots

- **T-ENVELOPE-0** — R6 top-level ErrorBoundary framework (~1-2 sessions). Dual-owned Cat D + Group 2200. Can run parallel to T-ENVELOPE-1.
- **T-ENVELOPE-3** — "Session expired" modal/toast UI (~30-60 min after T-ENVELOPE-1 lands).
- **T-ENVELOPE-2** — Backend `EXCEPTION_HANDLER` choice (Chris-D-verdict at T-ENVELOPE-2 planning).

### Alternative openers

If S3002 Chris redirects:
- **B — Drain v2 arc fold ledger.** 10+ items still open. Pick 1-2 highest-bang.
- **C — R6 ErrorBoundary framework (T-ENVELOPE-0).** Unblocks γ Layer 2; dual-owned with Group 2200.
- **D — Chris's own priority.** Always higher weight than ADR follow-on if a specific pain point surfaced.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read the S3001 handoff — especially the scope-recovery post-mortem (2400 Auth slot already-executed).
4. Read `docs/adr/ADR-0005-typed-error-envelope-contract.md` §3.1 + §3.4 + §4.1 T-ENVELOPE-1 spec.
5. Optional pre-response state probes:
   - `git log --oneline -6` — should show docs cascade → `f87ae95ef` (PR #3672 ADR-0005) → `c9b09d97d` (S3000 close cascade) → `39a6a9c97` (v2 item #5) → `2c3688817` (S2999 close cascade).
   - `grep -n "QueryClient" frontend/src/main.tsx` — locate current QueryClient factory site.
   - `wc -l frontend/src/main.tsx` — sanity check on file size before edit.

---

## S3002 carry-forward seeds

### New carry-forward from S3001

- **Fold A — CLOSED at merge.** Frontmatter `provisional_reason` wording sharpened to reflect Layer-1 independence.
- **Fold B `informational` — future ADR-N misread risk.** "γ ratified" implying interceptor policy is preserved by §3.3 wording. Watch for Family B mandate ADR-N to potentially need explicit re-anchoring; not a rule candidate yet.
- **Fold C `informational` — potential Playbook rule candidate.** "When Chris quotes a prior-session scoping suggestion, verify the target research slot state before accepting the scope." 1st concrete instance at S3001 (S3000 was spiritual cousin at carry-forward-label scope). Watch for 2nd similar instance before proposing Playbook amendment.
- **ADR-0005 T-slot queue** — 7 T-slots enumerated in §4.1. T-ENVELOPE-1 is next; others queued.

### Carry-forward from S3000 (STILL OPEN)

- **Fold A `informational` — potential Playbook rule candidate.** "Reproduce the failure at the thinnest interface before naming the carry-forward." 1st concrete instance. Watch for 2nd before proposing Playbook amendment.
- **Fold B `informational` — residual APIClient-forcing shapes.** Even with `use_user_auth`: (i) CSRF + session-cookie endpoints; (ii) multipart/form-data uploads; (iii) OAuth redirects; (iv) non-JSON POST bodies. None blocking; log for future arcs.
- **Fold C — Rigby Tool Gap Ledger entry CLOSED by S3000 PR.** Original gap "PA HTTP fetch couldn't hit auth-protected internal endpoints" resolved.

### Carry-forward from S2999 (STILL OPEN)

- **Fold B `active watch` — metadata accretion governance.** 4 detector keys currently. Trigger: 5+ keys OR 2+ independent consumers.
- **Fold C — Rigby Tool Gap Ledger.** File:line-only scope of consumer verifier — expectation-setting.

### Carry-forward from S2998 (STILL OPEN)

- **Fold A `future_trigger` — force=true × factory dedupe semantic mismatch.**
- **Fold B `future_trigger` — force re-dispatch could emit DeliverableEvent breadcrumb.**
- **Fold C — Rigby Tool Gap Ledger.** Semantic mismatch between endpoint override flag and downstream dedupe policy.

### Carry-forward from S2997 (STILL OPEN)

- **Fold B `future_trigger` — dedupe strictness on stale-ref ACs.**
- **Fold F — Rigby Tool Gap Ledger.** `orm_inspect_tool` doesn't support `metadata__<key>=value` JSON-path lookups.

### Carry-forward from S2996 (STILL OPEN)

- **Fold C `future_trigger` — staleness toast reinforcement.**
- **Fold E — Rigby Tool Gap Ledger (sharpened).** No in-UI Recheck action.

### Carry-forward from S2995 (STILL OPEN)

- **Fold C `future_trigger` — staleness metadata → dedicated JSONField.** Watch for 2nd trigger.
- **Fold D `future_trigger` — periodic staleness beat.**
- **Fold E — Rigby Tool Gap Ledger.** Metadata accretion governance (now `active watch` per S2999 Fold B).
- **Fold F `future_trigger` (S2994 hotfix) — WorkspacePageNew param preservation.**

### Carry-forward from S2994 (STILL OPEN)

- **Fold B `future_trigger` — inline-helper density.**
- **Fold C `future_trigger` — Deliverables-tab type badge.**
- **Fold D — Rigby Tool Gap Ledger.** Backend-semantics-shipped → UI-affordance-missing pattern.

### Carry-forward from S2993 (STILL OPEN)

- **Fold B ledger candidate — dry-run preview for send-to-rigby.**
- **Fold C future_trigger — executable-prompt tightening.**

### Carry-forward from S2992 (STILL OPEN)

- **Signal-tweak follow-up for `finding_type` classifier** (2 acceptable-misses).
- **Data-migration-vs-management-command pattern** (3rd-trigger check).

### Carry-forward from S2991 (STILL OPEN)

- **Dry-run counts pattern for future bulk-write migrations** (3rd-trigger check).
- **Contract-lock-in guardrail** — updated set: `close_mode`, `finding_type`, `spec_prompt_shape`, `finding_type_used`, `staleness`, `metadata.staleness_failed_refs`, `metadata.staleness_failed_refs_injected`, `metadata.unverified_consumer_refs`, `reason_code`, `use_user_auth`.
- **Freshness axis 2nd-trigger clause** (still no 2nd trigger).

### Carry-forward from S2989-S2990 (STILL OPEN)

- **F-D3-tracker-scope wire-up** — ~1 session.
- **F-D2-broad LLM-bypass audit spec** — ~1 session.
- **Reconcile Chris's 1805 cap-drift via `memory_hygiene_audit --apply`.** ~30 min.
- **Canonical Briefing v2 scope toggle.** ~1-2 hr.
- **Substrate fix for `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`.** ~1 session.
- **Send-to-Rigby follow-ups from S2988 (STILL OPEN).**

### Older carry-forward (STILL OPEN)

- **Chris browser visual check on S2985 Canonical Briefing tab strip / Refresh behavior.** ~5 min.
- **Rigby `claude_code_tool` safeguards.** Log to Rigby Tool Gap Ledger.
- **Chris browser visual check on S2984 arcs section.** ~5 min.
- **Systemic auth-XHR treatment (STILL OPEN from S2984 as Fold).**
- **Live-dispatch smoke on S2982 stage-doc guardrails.** ~15 min.
- **Exercise PLAYBOOK-7.7.4 against a sibling repo.**
- **Browser UX smoke on S2980 Theme Signals UX upgrade.** ~5 min.
- **Phase B Theme Signals — "Why now" LLM summarizer.** ~1 session.
- **Phase B Theme Signals — who-benefits/who-loses.** ~1-2 sessions.
- **Theme Signals — sub-tab persistence via localStorage.** ~30 min.
- **Rigby Tool Gap Ledger — Fold D from S2982.** DB uniqueness constraint on `AgentExecution.celery_task_id`. ~30-60 min.
- **Fold B `future_trigger` from v0.8.0 — fold-authoring evidence-admission helper.** 3-trigger threshold NOT yet met.
- **Post-close housekeeping (LOW priority).** Fill Playbook front-matter `commit_sha` + `content_hash` PLACEHOLDER fields for both v0.9.0 and v0.10.0.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session. **Candidate seeds:** S3000 Fold A "reproduce at thinnest interface" + S3001 Fold C "verify quoted-scope target-slot state" — both `informational`, both awaiting 2nd trigger.
- **ADR corpus:** ADR-0001 through ADR-0005. ADR-0005 is first PROVISIONAL ADR authored via draft-first + Rigby T1 SIGN pre-Chris-ratification (ADR-0004 precedent). ADR corpus schema unchanged (additive `provisional:` + `provisional_reason:` fields per ADR-0004 §4.4 forward-compat rule).
- **Spec→ship contract:** PLAYBOOK-7.7.1. S3001 was ADR-authoring shape, not feature-shipping shape. No T1 SIGN pre-draft; T1 SIGN happened on drafted body across 2 dispatch turns.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **Exemplar session.** Rigby's Q3 BLOCKED verdict (explicit refusal to rubber-stamp HEAD claims without tool_runs) is the rule working correctly. Turn 2 completion pass produced 9 real tool_runs.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. All 3 Chris-facing decision moments (A/B/C/D pivot / A3 target / Ratify & merge) framed with plain-English "do we lose anything?" + "is it more work later?" tables.
- **Close-ceremony PR discipline:** PLAYBOOK-7.4.1 through 7.4.4.
- **Recycle discipline** (S2978 refinement to PLAYBOOK-7.4.4): docs-only diff for ADR-0005 PR; docs cascade PR also docs-only; `make recycle-all` runs per safe-default rule.
- **Draft-first workflow:** PLAYBOOK-16. ADR-0005 authored with `status: draft`; flipped to `accepted` only after Chris "Ratify and open the PR" verdict.

---

## Wrapper pin note

The active PA conversation pin at S3001 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3001 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3001 is a milestone.** First ADR ratification since ADR-0004 (Arc I-0200 at S2701 on 2026-07-07). ADR-0005 opens the post-v2 arc-authoring cadence: draft-first → Rigby T1 SIGN on drafted body → Chris ratifies → PR → merge → T-slot implementation PRs follow. Whatever S3002 opens, the ADR discipline that shipped this session is the substrate for every future post-arc design-decision ratification.
