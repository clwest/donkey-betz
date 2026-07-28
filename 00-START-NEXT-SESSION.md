# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3002 CLOSED. **ADR-0005 γ mechanism COMPLETE (Layers 1+2+3 live).** T-ENVELOPE-2 or T-ENVELOPE-6 next.

**4 PRs merged this session** (T-ENVELOPE-1 + T-ENVELOPE-3 + T-ENVELOPE-0 + ADR-0006 successor). S3002 opened mid-terminal after S3001 close as a continuous engineering cascade.

**PR #3674 (`ec408bb7c`) — T-ENVELOPE-1 QueryClient default onError.** γ Layer 1 live. React Query v5-canonical `QueryCache({onError}) + MutationCache({onError})` at construction. Shape-agnostic handler at `frontend/src/lib/queryClientErrorHandler.ts`.

**PR #3675 (`fb8c8fdb9`) — T-ENVELOPE-3 Session-expired modal.** §3.4 step 2 UI live. Full-screen modal at `frontend/src/components/SessionExpiredModal.tsx` + Zustand `sessionExpiredStore` + handler swap.

**PR #3676 (`ba697a5f7`) — T-ENVELOPE-0 top-level ErrorBoundary.** γ Layer 2 unblocked. React 18 canonical class component at `frontend/src/components/ErrorBoundary.tsx` wraps App outside QueryClientProvider.

**PR #3677 (`cf4ff695a`) — ADR-0006 non-provisional successor.** Flipped ADR-0005 provisional posture after T-ENVELOPE-0 satisfied §4.2 trigger. ADR-0005 frontmatter updated with `superseded_by: ADR-0006` (first bidirectional supersede link in repo). Twin-mirror created by Rigby.

**γ mechanism state at HEAD `cf4ff695a`:** Layer 1 + Layer 2 + Layer 3 all LIVE. Silent-swallow rate on non-auth 401s: ~99% → 0%. User-visible modal on trigger.

**HEAD at close:** `cf4ff695a` + docs cascade PR (this file + handoff + INDEX + wrapper pin bump).

Full context:
- `docs/handoffs/SESSION_3002_ADR_0005_T_ENVELOPE_CASCADE.md` — 4-PR cascade + mid-terminal session-shape observation
- `docs/handoffs/SESSION_3001_ADR_0005_TYPED_ERROR_ENVELOPE.md` — ADR-0005 ratification (this session's parent)
- `docs/adr/ADR-0005-typed-error-envelope-contract.md` — decision content (canonical; superseded_by ADR-0006)
- `docs/adr/ADR-0006-typed-error-envelope-contract-non-provisional.md` — current-truth ADR

---

## S3003 primary directive — pick from T-ENVELOPE-2 / T-ENVELOPE-6 / T-VIP-1

ADR-0005 T-slot progress: **3-of-7 shipped**. Remaining candidates:

### Option A — T-ENVELOPE-2 Backend `EXCEPTION_HANDLER` choice (needs Chris-D-verdict)

Ratify Path (a) DRF `EXCEPTION_HANDLER` at settings level / (b) custom middleware normalization / (c) per-endpoint APIResponseEnvelope adoption without global normalization. Design-prep + ADR + implementation. **1-2 sessions estimate.**

- Path (a): custom `EXCEPTION_HANDLER` in `REST_FRAMEWORK` settings that wraps Family A → Family B for all DRF views. Highest coverage, lowest per-endpoint churn.
- Path (b): middleware-level normalization at `core/auth_middleware.py`. Handles non-DRF paths too. More surface to manage.
- Path (c): per-endpoint APIResponseEnvelope adoption ramp. Highest control, most churn.

Chris-D-verdict-question: which path? (recommend routing to Rigby for joint analysis first per `feedback_claude_rigby_agree_first_chris_yes_no`)

### Option B — T-ENVELOPE-6 Telemetry hookup (logs-only interim)

`componentDidCatch` at `frontend/src/components/ErrorBoundary.tsx` is annotated as T-ENVELOPE-6 hook-point. Handler at `queryClientErrorHandler.ts` could emit structured logs. Group 1700 Observability arc not yet shipped so full telemetry channel doesn't exist — but logs-only stub is a valid interim (JSON console.log with structured fields). **30-60 min estimate.**

### Option C — T-VIP-1 F-C-VIP-1 enforcement (risk-gate)

`VIPInvite.account_expires_at` runtime enforcement + periodic cleanup task. Blocks any expiry-signal UX from ADR-0005 §3.5. Backend + Celery beat. **1 session estimate.** Backend-only diff → `make celery-recycle` sufficient (not recycle-all).

### Option D — Different arc entirely

- v2 fold ledger drain (10+ items still open from S2991-S3000)
- Fresh research arc (2100 RAG / 2300 Mobile / 2600 PA — remaining from queue after 2200/2400/2500 done)
- Chris's own priority

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3002 handoff.
4. Read ADR-0006 §3–§4 (current-truth typed-error-envelope contract) if T-ENVELOPE-X work chosen.
5. Optional pre-response state probes:
   - `git log --oneline -8` — should show docs cascade → `cf4ff695a` (PR #3677 ADR-0006) → `ba697a5f7` (PR #3676 T-ENVELOPE-0) → `fb8c8fdb9` (PR #3675 T-ENVELOPE-3) → `ec408bb7c` (PR #3674 T-ENVELOPE-1) → `bec5ac55a` (S3001 close cascade) → `f87ae95ef` (PR #3672 ADR-0005) → `c9b09d97d` (S3000 close cascade).
   - `grep -c "APIResponseEnvelope" core/**/*.py` — sanity check on Family B adoption count for T-ENVELOPE-2 planning.

**Joint recommendation at close:** After 6 PRs in one terminal, S3003 opens with fresh mental model. Preferred order is C (T-VIP-1) > A (T-ENVELOPE-2) > B (T-ENVELOPE-6) > D — reasons: T-VIP-1 is bounded backend work that unblocks §3.5 UX; T-ENVELOPE-2 is bigger and needs design-prep first; T-ENVELOPE-6 is small but low-leverage without Group 1700; D is Chris-priority-dependent. **But route to Rigby first per `feedback_claude_rigby_agree_first_chris_yes_no` before presenting to Chris.**

---

## S3003 carry-forward seeds

### New carry-forward from S3002

- **Fold A (session-shape observation) — potential Playbook amendment candidate.** Mid-terminal S<N>→S<N+1> continuous engineering cascade (S3001→S3002 in one terminal, 6 PRs). 1st concrete instance. Watch for 2nd similar cascade before proposing Playbook rule codifying the pattern.
- **Fold B (T-ENVELOPE-1/3 inherited) — `informational`.** `queryClientErrorHandler.ts:28-30` — undefined `url` falls to non-auth branch. "Fail open" default acceptable. Not blocking.
- **Fold C (T-ENVELOPE-0 dev-only) — `informational`.** `componentDidCatch` fires twice in dev under StrictMode. Log-only side effect. Not blocking.
- **Fold D (ADR successor discipline) — VALIDATED PATTERN.** First bidirectional supersede link in repo (ADR-0005 ↔ ADR-0006). Successor-in-its-own-PR pattern validated per Rigby Q3(iii) at T-ENVELOPE-0 SIGN.
- **ADR-0005 T-slot queue** — 4 remaining T-slots (2/4/5/6) + T-VIP-1 risk-gate.

### Carry-forward from S3001 (STILL OPEN)

- **Fold A — CLOSED at merge.** ADR-0005 frontmatter provisional_reason wording.
- **Fold B `informational` — future ADR-N misread risk.** "γ ratified" implying interceptor policy is preserved by §3.3 wording. Watch for Family B mandate ADR-N to potentially need explicit re-anchoring.
- **Fold C `informational` — potential Playbook rule candidate.** "When Chris quotes a prior-session scoping suggestion, verify the target research slot state before accepting the scope." 1st concrete instance at S3001. Watch for 2nd similar instance.

### Carry-forward from S3000 (STILL OPEN)

- **Fold A `informational` — potential Playbook rule candidate.** "Reproduce the failure at the thinnest interface before naming the carry-forward." 1st concrete instance. Watch for 2nd.
- **Fold B `informational` — residual APIClient-forcing shapes.** Even with `use_user_auth`: CSRF + session-cookie / multipart uploads / OAuth redirects / non-JSON POST bodies. None blocking.
- **Fold C — Rigby Tool Gap Ledger entry CLOSED by S3000 PR.**

### Carry-forward from S2999 (STILL OPEN)

- **Fold B `active watch` — metadata accretion governance.** 4 detector keys currently. Trigger: 5+ keys OR 2+ independent consumers.
- **Fold C — Rigby Tool Gap Ledger.** File:line-only scope of consumer verifier.

### Carry-forward from S2998 (STILL OPEN)

- **Fold A `future_trigger` — force=true × factory dedupe semantic mismatch.**
- **Fold B `future_trigger` — force re-dispatch could emit DeliverableEvent breadcrumb.**
- **Fold C — Rigby Tool Gap Ledger.**

### Carry-forward from S2997 (STILL OPEN)

- **Fold B `future_trigger` — dedupe strictness on stale-ref ACs.**
- **Fold F — Rigby Tool Gap Ledger.** `orm_inspect_tool` doesn't support `metadata__<key>=value` JSON-path lookups.

### Carry-forward from S2996 (STILL OPEN)

- **Fold C `future_trigger` — staleness toast reinforcement.**
- **Fold E — Rigby Tool Gap Ledger (sharpened).** No in-UI Recheck action.

### Carry-forward from S2995 (STILL OPEN)

- **Fold C `future_trigger` — staleness metadata → dedicated JSONField.**
- **Fold D `future_trigger` — periodic staleness beat.**
- **Fold E — Rigby Tool Gap Ledger.** Metadata accretion governance.
- **Fold F `future_trigger` — WorkspacePageNew param preservation.**

### Carry-forward from S2994 (STILL OPEN)

- **Fold B `future_trigger` — inline-helper density.**
- **Fold C `future_trigger` — Deliverables-tab type badge.**
- **Fold D — Rigby Tool Gap Ledger.**

### Carry-forward from S2993 (STILL OPEN)

- **Fold B ledger candidate — dry-run preview for send-to-rigby.**
- **Fold C future_trigger — executable-prompt tightening.**

### Carry-forward from S2992 (STILL OPEN)

- **Signal-tweak follow-up for `finding_type` classifier** (2 acceptable-misses).
- **Data-migration-vs-management-command pattern** (3rd-trigger check).

### Carry-forward from S2991 (STILL OPEN)

- **Dry-run counts pattern for future bulk-write migrations** (3rd-trigger check).
- **Contract-lock-in guardrail** — updated set: `close_mode`, `finding_type`, `spec_prompt_shape`, `finding_type_used`, `staleness`, `metadata.staleness_failed_refs`, `metadata.staleness_failed_refs_injected`, `metadata.unverified_consumer_refs`, `reason_code`, `use_user_auth`.

### Carry-forward from S2989-S2990 (STILL OPEN)

- **F-D3-tracker-scope wire-up** — ~1 session.
- **F-D2-broad LLM-bypass audit spec** — ~1 session.
- **Reconcile Chris's 1805 cap-drift via `memory_hygiene_audit --apply`.** ~30 min.
- **Canonical Briefing v2 scope toggle.** ~1-2 hr.
- **Substrate fix for `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`.** ~1 session.
- **Send-to-Rigby follow-ups from S2988 (STILL OPEN).**

### Older carry-forward (STILL OPEN)

- **Chris browser visual check on S2985 Canonical Briefing tab strip.** ~5 min.
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

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session. **Candidate seeds:** S3000 Fold A (reproduce at thinnest interface) + S3001 Fold C (verify quoted-scope target-slot state) + S3002 Fold A (mid-terminal cascade session-shape) — all `informational`, all awaiting 2nd trigger.
- **ADR corpus:** ADR-0001 through ADR-0006. First bidirectional supersede link in repo (ADR-0005 ↔ ADR-0006). ADR-0006 is current-truth for typed-error-envelope; ADR-0005 remains for §3 clause references.
- **Spec→ship contract:** PLAYBOOK-7.7.1. 3× Flow B ships in S3002 + 1× docs successor. All followed spec→T1-skipped-when-deterministic→ship→A2-pre-merge SIGN→merge→recycle.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. 3× Rigby A2-pre-merge SIGN with real tool_runs (all AGREE). ADR-0006 SIGN skipped per docs-only-successor rationale.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. 4 Chris-facing decision moments framed with plain-English tables. Joint Claude+Rigby recommendation reached before final "successor then close" ratification.
- **Recycle discipline:** S2978 refinement — all 3 feature PRs used `make recycle-all` (frontend touched). ADR-0006 docs-only but final recycle-all uses safe default.
- **Draft-first workflow:** PLAYBOOK-16. ADR-0005 authored draft-first (S3001); ADR-0006 authored `accepted` directly (docs-only successor exception per ADR-0004 §5.6 precedent).
- **`feedback_twin_deliverable_at_every_ratification`** + `feedback_rigby_writes_workspace_deliverables` — twin-mirror for both ADRs created by Rigby via PA tool_dispatch.

---

## Wrapper pin note

The active PA conversation pin at S3002 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3002 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3002 is a milestone.** First mid-terminal continuous S<N>→S<N+1> engineering cascade in the repo (Fold A observation candidate). First bidirectional ADR supersede link (Fold D validated pattern). γ mechanism fully live across all 3 layers with user-visible modal UX. ADR-0005 T-slot progress 3-of-7 — remaining T-slots are polish (T-ENVELOPE-6 telemetry), scale (T-ENVELOPE-4 migration), design-space (T-ENVELOPE-2 backend), or risk-gate (T-VIP-1). Whatever S3003 opens, this session demonstrated: draft-first ADR authoring + T1 SIGN pre-Chris-ratification + A2 pre-merge SIGN + docs-only successor discipline + bidirectional supersede link — a complete post-arc ADR→implementation→successor cycle inside 2 sessions.
