# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3004 CLOSED. **§3.5 UX widening shipped. S3002+S3003 Fold-B ledger items drained.** S3005 opens with remaining T-ENVELOPE slots.

**1 PR merged this session** (§3.5 UX widening).

**PR #3681 (`85fffdfc1`) — §3.5 UX widening: X-VIP-Expired header + discriminated authFailureStore + variant modal.** Backend `VIPReadOnlyMiddleware` now emits `X-VIP-Expired: true` header on the 401 deny branch (`core/vip_middleware.py:60-78`). Frontend migrated from single-kind `sessionExpiredStore` to discriminated `authFailureStore` with `AUTH_FAILURE_KIND` shared const (`session_expired` / `vip_expired`). `queryClientErrorHandler.ts` reads the header to select the kind; `SessionExpiredModal.tsx` renders variant-specific title, body, CTA icon+label, and handler (VIP → `/`; Session → `/login`). Closes S3002 Fold B + S3003 Fold B (same-file surface).

**Rigby A2 SIGN quality signal:** 8 real tool_runs across two turns. 4 STRENGTHEN raised — 2 false-positive line-1 truncation, 1 applied (`AUTH_FAILURE_KIND` shared const), 1 rejected+AGREE'd (`/vip/` redirect not a defined route). Substantive per PLAYBOOK-7.7.2, not rubber-stamp.

**HEAD at close:** `85fffdfc1` + docs cascade PR (this file + handoff + INDEX + wrapper pin bump).

Full context:
- `docs/handoffs/SESSION_3004_VIP_EXPIRY_UX_WIDENING.md` — single-PR close, 4 folds, forward carries
- `docs/handoffs/SESSION_3003_T_VIP_1_ACCOUNT_EXPIRY.md` — parent (T-VIP-1 backend that unblocked §3.5 UX)
- `docs/adr/ADR-0006-typed-error-envelope-contract-non-provisional.md` — current-truth typed envelope ADR

---

## S3005 primary directive — pick from remaining T-ENVELOPE slots or Option D

ADR-0005 T-slot progress: **3-of-7 T-ENVELOPE shipped** (T-ENVELOPE-0/1/3), **T-VIP-1 shipped**, **§3.5 UX widening shipped**. Remaining T-ENVELOPE candidates:

### Option A — T-ENVELOPE-2 Backend `EXCEPTION_HANDLER` choice (needs Chris D-verdict)

Ratify Path (a) DRF `EXCEPTION_HANDLER` at settings level / (b) custom middleware normalization / (c) per-endpoint APIResponseEnvelope adoption without global normalization. Design-prep + ADR + implementation. **1-2 sessions estimate.** Blocks T-ENVELOPE-4 migration.

- Path (a): custom `EXCEPTION_HANDLER` in `REST_FRAMEWORK` settings that wraps Family A → Family B for all DRF views. Highest coverage, lowest per-endpoint churn.
- Path (b): middleware-level normalization at `core/auth_middleware.py`. Handles non-DRF paths too. More surface to manage.
- Path (c): per-endpoint APIResponseEnvelope adoption ramp. Highest control, most churn.

Chris-D-verdict-question: which path? (route to Rigby for joint analysis first per `feedback_claude_rigby_agree_first_chris_yes_no`)

### Option B — T-ENVELOPE-6 Telemetry hookup (logs-only interim)

`componentDidCatch` at `frontend/src/components/ErrorBoundary.tsx` is annotated as T-ENVELOPE-6 hook-point. Handler at `queryClientErrorHandler.ts` could emit structured logs. Group 1700 Observability arc not yet shipped so full telemetry channel doesn't exist — but logs-only stub is a valid interim (JSON console.log with structured fields). **30-60 min estimate.**

### Option C — Different arc entirely

- v2 fold ledger drain (10+ items still open from S2991-S3003 + Fold C from S3004: dedicated `/vip/expired` landing page)
- Fresh research arc (2100 RAG / 2300 Mobile / 2600 PA — remaining from queue)
- Chris's own priority

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3004 handoff.
4. Read ADR-0006 §3–§4 (typed-error-envelope contract) if T-ENVELOPE-X work chosen.
5. Optional pre-response state probes:
   - `git log --oneline -8` — should show docs cascade → `85fffdfc1` (PR #3681 §3.5 UX widening) → `b9595c597` (S3003 close cascade) → `3bd3df386` (PR #3679 T-VIP-1) → `276a0e418` (S3002 close cascade) → `cf4ff695a` (PR #3677 ADR-0006) → `ba697a5f7` (PR #3676 T-ENVELOPE-0) → `fb8c8fdb9` (PR #3675 T-ENVELOPE-3).
   - `grep -c "APIResponseEnvelope" core/**/*.py` — sanity check on Family B adoption count for T-ENVELOPE-2 planning.

**Joint recommendation at close:** Preferred order for S3005 is A (T-ENVELOPE-2 — needs Chris D-verdict on path choice) > B (T-ENVELOPE-6 logs-only) > C (Chris priority or Fold-C `/vip/expired` landing). Reason: with §3.5 UX shipped, the frontend substrate is ready to consume Family B envelopes when the backend normalization ships. T-ENVELOPE-2 is the biggest remaining ADR-0005 unblocker. **Route to Rigby first before presenting to Chris.**

---

## S3005 carry-forward seeds

### New carry-forward from S3004

- **Fold A `2nd trigger` — Fold-Drain-Same-Surface pattern.** S3002 Fold B + S3003 Fold B both pointed to `queryClientErrorHandler.ts:28-30` predicate; both closed by S3004 header-based discrimination. **2nd concrete instance.** Watch for 3rd before proposing Playbook rule "when Fold-B ledger items on the same file:line surface accumulate to ≥2, batch-close them in the next arc that reaches that surface."
- **Fold B `informational` — shared-const derived-union frontend pattern.** `AUTH_FAILURE_KIND` const + `(typeof X)[keyof typeof X]` union derivation was Rigby STRENGTHEN 6a during A2 SIGN. **1st concrete instance** in this repo's frontend. Watch for 2nd; if it recurs, propose docs note under `docs/UDB_BEHAVIOR_LAYER.md` `## Frontend conventions`.
- **Fold C `same_pr_mitigatable_deferred_to_next_arc` — dedicated `/vip/expired` landing page.** Rigby STRENGTHEN 6b proposed `/vip/` redirect; rejected because `/vip/` is not a defined route. Genuine gap: expired VIP "log out" lands on marketing DemoHomePage with no context. Ledger for Rigby Tool Gap Ledger + future UX arc.
- **Fold D `informational` — Rigby repo_tool line-1 read-display truncation false-positive.** Initial A2 tool_run reads on TS files displayed content from `2:` onward, causing Rigby to flag line-1 imports as missing. Re-verified via targeted `Read limit=3`. **1st concrete instance.** Watch for 2nd — if recurs, note in Rigby Tool Gap Ledger.

### Carry-forward from S3003 (STILL OPEN)

- **Fold A `informational` — risk-gate T-slot vs T-ENVELOPE-N scoping.** T-VIP-1 shipped parallel to T-ENVELOPE series, not as member. **1st concrete instance** of risk-gate T-slot completing before dependent UX slots. Watch for 2nd before proposing Playbook rule.
- **Fold C `informational` — Django reverse-O2O test cache-bust pattern.** `_make_vip_user` in `tests/test_vip_expiry.py:22-30` documents the pattern with inline comment. **1st concrete instance** in test suite. Watch for 2nd.

### Carry-forward from S3002 (STILL OPEN)

- **Fold A — session-shape observation.** Mid-terminal S<N>→S<N+1> continuous engineering cascade. **2nd concrete instance** now (S3001→S3002 + S3003→S3004). Watch for 3rd similar cascade.
- **Fold C `informational` (T-ENVELOPE-0 dev-only) — `componentDidCatch`** fires twice in dev under StrictMode.
- **Fold D — ADR successor discipline VALIDATED PATTERN.** First bidirectional supersede link in repo (ADR-0005 ↔ ADR-0006).
- **ADR-0005 T-slot queue** — 4 remaining T-slots (T-ENVELOPE-2/4/5/6).

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
- **Live browser smoke on S3004 VIP-expired modal.** When a VIP expiry occurs (or via manual `curl` reproduction). ~5 min.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session. **Candidate seeds:** S3004 Fold A (2nd-trigger Fold-Drain-Same-Surface — watch for 3rd) + S3004 Fold B (shared-const derived-union frontend — watch for 2nd) + S3004 Fold D (Rigby repo_tool line-1 truncation — watch for 2nd). Prior candidates from S3000/S3001/S3002/S3003 all remain open.
- **ADR corpus:** ADR-0001 through ADR-0006. ADR-0006 is current-truth for typed-error-envelope.
- **Spec→ship contract:** PLAYBOOK-7.7.1. 1× Flow B ship (§3.5 UX widening). Clean spec→T1-skipped-when-deterministic→ship→A2-pre-merge SIGN→merge→recycle→close.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. 1× Rigby A2-pre-merge SIGN with 8 real tool_runs across two turns (4 STRENGTHEN — 2 false-positive, 1 applied `AUTH_FAILURE_KIND`, 1 rejected `/vip/` redirect w/ Rigby AGREE'd rationale). Substantive per PLAYBOOK-7.7.2.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. 1 Chris-facing decision moment framed with plain-English "do we lose anything? / is it more work later?" pair. Joint Claude+Rigby recommendation reached before Chris ratification.
- **Recycle discipline:** S2978 refinement — frontend-touched diff → `make recycle-all` (NOT `make celery-recycle`). Correct per Chris's local-truth doctrine + `feedback_recycle_after_merge`.

---

## Wrapper pin note

The active PA conversation pin at S3004 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3004 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3004 is a clean single-focus ship demonstrating the full spec→ship contract at minimum footprint:** one ratified directive → Rigby joint agreement → Chris plain-English ratification → implementation + tests → Rigby A2 SIGN with real tool_runs (substantive: 4 STRENGTHEN, 1 applied) → merge → recycle-all → close cascade. §3.5 UX arc closed. S3002+S3003 Fold-B ledger items drained in same PR.
