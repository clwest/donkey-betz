# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3003 CLOSED. **T-VIP-1 shipped. ADR-0005 §3.5 F-C-VIP-1 risk-gate DISCHARGED.** S3004 opens with remaining T-ENVELOPE slots.

**1 PR merged this session** (T-VIP-1).

**PR #3679 (`3bd3df386`) — T-VIP-1 VIPInvite account expiry enforcement.** `VIPReadOnlyMiddleware` now denies 401 on requests from VIP users whose most-recent redeeming invite is missing, revoked, or past `account_expires_at`. New backstop `@shared_task cleanup_expired_vip_users` at `core/tasks_vip.py` runs nightly at 2:55 AM MST via new beat entry `cleanup-expired-vip-users`. 9 test cases at `tests/test_vip_expiry.py` all passing. Preserved HIGH-severity F-C-VIP-1 risk-gate (declared-but-not-enforced across S2403 + S2503) discharged.

**Rigby A2 SIGN quality signal:** 7 real tool_runs verifying each file:line claim; one STRENGTHEN applied (enriched missing-invite log line with user_id + username). Substantive per PLAYBOOK-7.7.2, not rubber-stamp.

**HEAD at close:** `3bd3df386` + docs cascade PR (this file + handoff + INDEX + wrapper pin bump).

Full context:
- `docs/handoffs/SESSION_3003_T_VIP_1_ACCOUNT_EXPIRY.md` — single-PR close, 3 folds, forward carries
- `docs/handoffs/SESSION_3002_ADR_0005_T_ENVELOPE_CASCADE.md` — γ mechanism cascade (S3003's parent)
- `docs/adr/ADR-0006-typed-error-envelope-contract-non-provisional.md` — current-truth typed envelope ADR

---

## S3004 primary directive — pick from remaining T-ENVELOPE slots or Option D

ADR-0005 T-slot progress: **3-of-7 T-ENVELOPE shipped** (T-ENVELOPE-0/1/3), **T-VIP-1 shipped**. Remaining T-ENVELOPE candidates:

### Option A — T-ENVELOPE-2 Backend `EXCEPTION_HANDLER` choice (needs Chris-D-verdict)

Ratify Path (a) DRF `EXCEPTION_HANDLER` at settings level / (b) custom middleware normalization / (c) per-endpoint APIResponseEnvelope adoption without global normalization. Design-prep + ADR + implementation. **1-2 sessions estimate.** Blocks T-ENVELOPE-4 migration.

- Path (a): custom `EXCEPTION_HANDLER` in `REST_FRAMEWORK` settings that wraps Family A → Family B for all DRF views. Highest coverage, lowest per-endpoint churn.
- Path (b): middleware-level normalization at `core/auth_middleware.py`. Handles non-DRF paths too. More surface to manage.
- Path (c): per-endpoint APIResponseEnvelope adoption ramp. Highest control, most churn.

Chris-D-verdict-question: which path? (route to Rigby for joint analysis first per `feedback_claude_rigby_agree_first_chris_yes_no`)

### Option B — T-ENVELOPE-6 Telemetry hookup (logs-only interim)

`componentDidCatch` at `frontend/src/components/ErrorBoundary.tsx` is annotated as T-ENVELOPE-6 hook-point. Handler at `queryClientErrorHandler.ts` could emit structured logs. Group 1700 Observability arc not yet shipped so full telemetry channel doesn't exist — but logs-only stub is a valid interim (JSON console.log with structured fields). **30-60 min estimate.**

### Option C — §3.5 UX widening (unblocks VIP-expiry UX)

Now that T-VIP-1 backend lands, VIP users hit a 401 that the T-ENVELOPE-1 `queryClientErrorHandler` treats as "fail open" because the auth-branch predicate is url-based and VIP-expiry 401s arrive on non-auth URLs (e.g. `/api/deliverables/`). Two candidate paths:

- Path (a): widen auth-branch predicate at `frontend/src/lib/queryClientErrorHandler.ts:28-30` to include VIP-expiry responses (detect via body error string OR add a response header like `X-VIP-Expired`).
- Path (b): route VIP-expiry 401s through a dedicated modal component (siblings T-ENVELOPE-3 SessionExpiredModal).

**~30-60 min estimate.** Route options through Rigby first for design agreement.

### Option D — Different arc entirely

- v2 fold ledger drain (10+ items still open from S2991-S3002 + Fold B from S3003)
- Fresh research arc (2100 RAG / 2300 Mobile / 2600 PA — remaining from queue)
- Chris's own priority

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3003 handoff.
4. Read ADR-0006 §3–§4 (typed-error-envelope contract) if T-ENVELOPE-X work chosen.
5. Optional pre-response state probes:
   - `git log --oneline -8` — should show docs cascade → `3bd3df386` (PR #3679 T-VIP-1) → `276a0e418` (S3002 close cascade) → `cf4ff695a` (PR #3677 ADR-0006) → `ba697a5f7` (PR #3676 T-ENVELOPE-0) → `fb8c8fdb9` (PR #3675 T-ENVELOPE-3) → `ec408bb7c` (PR #3674 T-ENVELOPE-1) → `bec5ac55a` (S3001 close cascade).
   - `grep -c "APIResponseEnvelope" core/**/*.py` — sanity check on Family B adoption count for T-ENVELOPE-2 planning.

**Joint recommendation at close:** Preferred order for S3004 is C (§3.5 UX widening) > A (T-ENVELOPE-2) > B (T-ENVELOPE-6) > D. Reasons: C is short and immediately-visible (users now hit real 401s; without it they get silent failures instead of a modal). A is bigger and needs Chris D-verdict on path choice. B is low-leverage without Group 1700. D is Chris-priority-dependent. **Route to Rigby first before presenting to Chris.**

---

## S3004 carry-forward seeds

### New carry-forward from S3003

- **Fold A `informational` — risk-gate T-slot vs T-ENVELOPE-N scoping.** T-VIP-1 shipped parallel to T-ENVELOPE series, not as member. **1st concrete instance** of risk-gate T-slot completing before dependent UX slots. Watch for 2nd before proposing Playbook rule.
- **Fold B `same_pr_mitigatable_deferred_to_next_arc` — frontend §3.5 UX widening.** `queryClientErrorHandler.ts:28-30` non-auth 401 fail-open path swallows VIP-expiry 401s. Belongs to §3.5 UX arc (Option C above). See S3003 handoff §Folds.
- **Fold C `informational` — Django reverse-O2O test cache-bust pattern.** `_make_vip_user` in `tests/test_vip_expiry.py:22-30` documents the pattern with inline comment. **1st concrete instance** in test suite. Watch for 2nd.

### Carry-forward from S3002 (STILL OPEN)

- **Fold A — session-shape observation.** Mid-terminal S<N>→S<N+1> continuous engineering cascade. 1st concrete instance (S3001→S3002). Watch for 2nd similar cascade.
- **Fold B `informational` (T-ENVELOPE-1/3 inherited) — `queryClientErrorHandler.ts:28-30`** undefined-url falls to non-auth branch. "Fail open" default acceptable. Not blocking. **NOTE:** This is the same-file location as S3003 Fold B; §3.5 UX arc will likely close both together.
- **Fold C `informational` (T-ENVELOPE-0 dev-only) — `componentDidCatch`** fires twice in dev under StrictMode.
- **Fold D — ADR successor discipline VALIDATED PATTERN.** First bidirectional supersede link in repo (ADR-0005 ↔ ADR-0006).
- **ADR-0005 T-slot queue** — 4 remaining T-slots (T-ENVELOPE-2/4/5/6). **T-VIP-1 now ✅ shipped.**

### Carry-forward from S3001 (STILL OPEN)

- **Fold B `informational` — future ADR-N misread risk.** "γ ratified" implying interceptor policy is preserved by §3.3 wording.
- **Fold C `informational` — potential Playbook rule candidate.** "When Chris quotes a prior-session scoping suggestion, verify the target research slot state before accepting the scope." 1st concrete instance. Watch for 2nd.

### Carry-forward from S3000 (STILL OPEN)

- **Fold A `informational` — potential Playbook rule candidate.** "Reproduce the failure at the thinnest interface before naming the carry-forward." 1st concrete instance. Watch for 2nd.
- **Fold B `informational` — residual APIClient-forcing shapes.** Even with `use_user_auth`: CSRF + session-cookie / multipart uploads / OAuth redirects / non-JSON POST bodies.

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
- **Contract-lock-in guardrail** — updated set as of S2991.

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

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session. **Candidate seeds:** S3003 Fold A (risk-gate T-slot vs T-ENVELOPE scoping) + S3003 Fold C (Django reverse-O2O test cache-bust) — both `informational`, both awaiting 2nd trigger. Prior candidates from S3000/S3001/S3002 all remain open.
- **ADR corpus:** ADR-0001 through ADR-0006. ADR-0006 is current-truth for typed-error-envelope.
- **Spec→ship contract:** PLAYBOOK-7.7.1. 1× Flow B ship (T-VIP-1). Clean spec→T1-skipped-when-deterministic→ship→A2-pre-merge SIGN→merge→recycle→close.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. 1× Rigby A2-pre-merge SIGN with 7 real tool_runs (AGREE + 1 STRENGTHEN applied). Substantive per PLAYBOOK-7.7.2, not rubber-stamp.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. 1 Chris-facing decision moment framed with plain-English "do we lose anything? / is it more work later?" pair. Joint Claude+Rigby recommendation reached before Chris ratification.
- **Recycle discipline:** S2978 refinement — backend-only diff, `make celery-recycle` used (not recycle-all). Correct per Chris's local-truth doctrine + `feedback_local_truth_no_production`.

---

## Wrapper pin note

The active PA conversation pin at S3003 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3003 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3003 is a clean single-focus ship demonstrating the full spec→ship contract at minimum footprint:** one ratified directive → Rigby joint agreement → Chris plain-English ratification → implementation + tests → Rigby A2 SIGN with real tool_runs → merge → recycle → close cascade. F-C-VIP-1 discharged after multi-session preservation across S2403+S2503. §3.5 UX arc now unblocked.
