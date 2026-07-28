# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3009 CLOSED. **B1 warm-up + Batch 3 shipped in same session.** `core/auth_middleware.py` now at 0 raw-pattern sites (10/10 use helper); `core/views_auto_distribution.py` fully migrated (25 sites). **4-of-5 T-ENVELOPE-2-DEPRECATION files migrated.** S3010 opens with Batch 4 (`core/views_platform_integrations.py`, 62 sites — largest remaining batch).

**2 PRs merged this session.**

**PR #3691 (`75aa57631`) — B1: 9-site auth_middleware retrofit.** Retrofit remaining raw envelope-emit sites in `core/auth_middleware.py` to `emit_error_envelope()` helper (spec pre-ratified at S3008 Fold A). File now at 0 raw sites. `build_user_facing_envelope` dropped from imports (0 callers). Diff: +41/-59 = -18 net. `JsonResponse` retained (RateLimitingMiddleware inline 429 at L935 = Fold E carry-forward).

**PR #3692 (`546985106`) — Batch 3: 25 sites in views_auto_distribution.py.** All 6 endpoints (create_auto_distribution/batch_distribute/reschedule/cancel/settings/apply_template) migrated. Reason-code taxonomy: 6× not_authenticated / 9× invalid_input / 6× validation_error / 4× not_found. All auto-infer typical_status. Rigby A1 D4 optional enhancements applied (requested_platforms + allowed_statuses). Import cleanup (dropped api_error, kept api_success, added emit_error_envelope). Lint MIGRATED_FILES: **3 → 4 files**. Diff: +167/-26 = +141 net.

**Behavior change flagged:** `create_auto_distribution` Image/Video not_found (L122/L130) shifts from implicit 400 to 404 under `not_found` reason_code. Documented in PR #3692 description. Not directly live-smoke-verified (requires UserPlatformAccount test data for chris) — forward-carry if consumer regresses.

**Rigby SIGN cycle notes:**
- **B1 A2:** AGREE 4/5 (D5 PARTIAL = shell-exec surface gap → Fold C ledger entry).
- **Batch 3 A1:** AGREE 5/5 with 1 D3 behavior-change flag (400→404) + 2 optional D4 enhancements (both applied).
- **Batch 3 A2:** AGREE 4/5 initial, then **DISAGREE D3 was SPURIOUS** — Rigby quoted defensive `.get()` code correctly, then labeled it "not defensive" and hallucinated direct-indexing bytes on re-verify. Resolved via 3-channel Claude verification (Read + Grep + `git show HEAD:...`). Rigby acknowledged mistake was LLM-side, not tool bug. Effective verdict AGREE 5/5. **Fold A new pattern, 1st trigger, ledger entry queued.**

**Live-smoke (post `make restart` both PRs):**
- **B1:** curl unauthed + curl w/ invalid token → both 401 + Family E + `envelope_emit` log source from `error_envelope` module. Invalid-token curl directly verifies L693 B1-converted site.
- **Batch 3:** 4 sites via curl + Django Client. L77 not_authenticated (RUR-AUTH-*), L82 invalid_input json_decode (RUR-INPUT-*), L96 validation_error no_platforms_connected (bonus — RUR-VALIDATE-*), L751 invalid_input unknown_template with `hint={'template': 'nonexistent_template'}` preserved.

**HEAD at close:** `546985106` + docs cascade PR (this file + handoff + INDEX regen + wrapper pin bump).

Full context:
- `docs/handoffs/SESSION_3009_T_ENVELOPE_2_DEPRECATION_BATCH_3.md` — 2-PR close, 5 folds (A/B/C/D/E), forward carries
- `docs/adr/ADR-0007-layered-envelope-policy.md` — parent ADR (ratified S3005)
- `core/security/error_envelope.py:117-154` — helper (shipped S3008)
- `scripts/lint_no_deprecated_family_b.py` — **4 files tracked** (added views_auto_distribution.py this session)

---

## S3010 primary directive — Batch 4 (`core/views_platform_integrations.py`, 62 sites) using the helper

### Option A — Batch 4 direct (recommended)

**Phase 1 — Rigby A1 SIGN on 62-site reason_code mapping (~30-45 min):**
Largest batch yet. Route full mapping table (grouped by endpoint) to Rigby A1 SIGN. Each site: current status_code, proposed reason_code, hint dict, whether typical_status matches. Expect richer variety than Batch 3 — platform integrations may include upstream_provider_error, upstream_provider_timeout, rate_limited from external APIs.

**Phase 2 — Migration (~1-2 sessions, may split across 2 PRs):**
62 sites. If Rigby A1 clusters sites into distinct classes (e.g., 30 auth + 20 upstream + 12 not_found), consider 2 PRs by class rather than 1 monolithic. Chris ratifies split shape at Phase 1 close.

**Phase 3 — Ship + smoke per PR:**
Standard: A2 SIGN → merge `--admin --squash --delete-branch` → `make restart` (view module, Daphne request path per Fold B 3rd trigger) → live-smoke 3-5 representative sites → close cascade.

### Option B — Bundle Fold E RateLimiting 429 with Batch 4 start

**Fold E** (S3007 carry-forward, still open at S3009): `core/auth_middleware.py:935` inline 429 dict in RateLimitingMiddleware.process_request. ~15 min PR with helper: `return emit_error_envelope(reason_code='rate_limited', request=request, retry_after_seconds=N)`. 429-client-parsing behavior surface — worth its own PR ahead of Batch 4 as a small warm-up (mirrors S3009 B1+A shape).

**B1 shape** — separate warm-up PR before Batch 4 (recommended if Chris wants clean batch).
**B2 shape** — absorb into Batch 4 PR (single larger PR).
**B3 shape** — defer indefinitely (still Family E-adjacent, just verbose inline dict).

### Option C — Fold A ledger entry + Fold C ledger entry, then Batch 4

Small doc-only PR to mint 2 Rigby Tool Gap Ledger entries in workspace `b4503364-2573-4401-9e28-61a739e0ce50`:
- **Ledger entry 1 (Fold A):** LLM-side hallucination pattern — verdict text contradicting own tool_run excerpt. Watch-for-2nd-trigger. Mitigation via existing `feedback_verify_rigby_tool_runs_before_trusting_sign` (needs extension text: "AND verify at raw file/git-blob before accepting DISAGREE on file-level code claim").
- **Ledger entry 2 (Fold C):** Rigby shell-exec surface gap — no `run_command` tool for read-only ops. Blocks D5-style "run the actual gate" verification. Substrate arc candidate: whitelist-based `repo_tool.run_command`.

Then Option A. Adds ~20 min upfront but improves Rigby SIGN quality for the 62-site Batch 4 (Fold C fix would let Rigby verify lint pass directly).

### Option D — Fold B Playbook amendment (middleware/view restart discipline)

Fold B hit **3rd trigger** at S3009 (S3007 1st, S3008 2nd, S3009 3rd). Threshold met per amendment discipline. Draft v0.10.1 PATCH or v0.11.0 MINOR extending `feedback_recycle_after_merge` into Playbook Ch 7 §7.4 as a formal [GR] rule. ~1 hour amendment session (spec doc + PLAYBOOK entry + ratification record + CLAUDE.md refresh per amendment pattern).

**Deferral rationale:** the existing memory rule already contains the guidance in its "S2978 refinement" body; a formal Playbook entry is cleanup, not urgent. Chris can ratify or defer at S3010 open.

### Option E — Different arc entirely

- v2 fold ledger drain (12+ items still open from S2991-S3006)
- Fresh research arc (2100 RAG / 2300 Mobile / 2600 PA)
- Batch 3 400→404 verification test-data setup (from S3009 forward-carry)
- Chris's own priority

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3009 handoff (`docs/handoffs/SESSION_3009_T_ENVELOPE_2_DEPRECATION_BATCH_3.md`).
4. Read `core/views_platform_integrations.py` — target file for Batch 4; scan the 62 error-return sites; understand hint shapes + status codes + which endpoints hit external APIs (upstream_provider_error candidates).
5. Optional pre-response state probes:
   - `git log --oneline -8` — should show docs cascade → `546985106` (PR #3692 Batch 3) → `75aa57631` (PR #3691 B1) → `6a85dd26c` (S3008 close cascade) → `efdef79f8` (S3008 helper).
   - `python scripts/lint_no_deprecated_family_b.py --list` — confirm **4 tracked files** (`views_odds_sports.py`, `views_revenue_analytics.py`, `auth_middleware.py`, `views_auto_distribution.py`).
   - `grep -c "api_error\|api_unauthorized\|api_forbidden" core/views_platform_integrations.py` — establish Batch 4 baseline (expect ~62).
   - `grep -c "external\|upstream\|provider" core/views_platform_integrations.py` — get a rough sense of external-API surface (upstream_provider_error candidates).

**Joint recommendation at close:** Preferred order for S3010 is **C+B1+A (ledger entries → Fold E warm-up → Batch 4)** > **B1+A (Fold E warm-up → Batch 4)** > **A (Batch 4 direct)** > **D (Playbook amendment)** > **E (other)**. Reason: Fold C ledger entry improves Rigby's Batch 4 SIGN quality substrate-wise; Fold E warm-up is trivial with helper and clears remaining auth_middleware Family B pattern; Batch 4 is the largest remaining migration and benefits from clean prep. Chris ratifies at S3010 open.

---

## S3010 carry-forward seeds

### New carry-forward from S3009

- **Fold A `1st trigger` — Rigby LLM-side hallucination on file-level code claim.** Ledger candidate in workspace `b4503364-2573-4401-9e28-61a739e0ce50`. Watch for 2nd trigger before Playbook amendment. Consolidates with `feedback_verify_rigby_tool_runs_before_trusting_sign` on extension.
- **Fold B `3rd trigger` — middleware/view restart discipline.** Threshold met. Playbook amendment candidate (Option D at S3010).
- **Fold C `1st trigger` — Rigby shell-exec tool-surface gap.** Ledger candidate in workspace `b4503364-2573-4401-9e28-61a739e0ce50`. Watch for 2nd trigger before capability expansion arc.
- **Fold D `6th continuous cascade`** — observation stays; watch for break.
- **Fold E `future_trigger` (carried through S3007, S3008, S3009)** — RateLimiting 429 in auth_middleware.py:935. Trivial with helper. Option B at S3010.
- **Batch 3 400→404 behavior-change verification** — direct live-smoke skipped for lack of test data (chris has no UserPlatformAccount). Forward-carry: consumer regression check OR management-command probe that seeds test data.

### T-ENVELOPE-2-DEPRECATION queue after S3009

- **S3010 (primary directive candidate):** Batch 4 — `core/views_platform_integrations.py` (62 sites). 2-3 sessions minimum with helper.
- **Batch 5 (post-Batch 4):** `core/api_helpers.py` disposition — separate substrate arc. Currently: Family B helpers with deprecation docstrings. Disposition = retire vs keep-with-warning.

### Carry-forward from S3008 (STILL OPEN)

- **Fold A `future_trigger` — RESOLVED at S3009 as B1.** 
- **Fold B `1st trigger`** — `repo_tool.search` no `total_matches` field. Distinct from S3009 Fold C (shell-exec gap). Ledger workspace `b4503364-2573-4401-9e28-61a739e0ce50`.
- **Fold C `2nd trigger` — SUPERSEDED by S3009 Fold B 3rd trigger.** See S3009 Fold B.
- **Fold D `5th continuous cascade` — SUPERSEDED by S3009 Fold D.**
- **Fold E `future_trigger`** — carried through S3009 as Fold E, still open.

### Carry-forward from S3006 (STILL OPEN)

- **Fold C `future_trigger`** — DRF-decorator refactor for inline auth checks. Deferred.
- **Operator-envelope-from-explicit-emissions** wiring. Not on roadmap.

### Carry-forward from S3005 (STILL OPEN)

- **Fold A `informational` (1st trigger)** — PLAYBOOK-7.7.1 abort-early clause firing at pre-execution probe. Watch for 2nd.
- **Fold B `informational` (1st trigger)** — ADR-baseline post-ratification drift. Watch for 2nd.
- **Fold C `informational` (1st trigger)** — `refines:` frontmatter field for §-scoped amendment. Watch for 2nd.

### Carry-forward from S3004 (STILL OPEN)

- **Fold A `2nd trigger`** — Fold-Drain-Same-Surface pattern. Watch for 3rd.
- **Fold B `informational` (1st trigger)** — shared-const derived-union frontend pattern. Watch for 2nd.
- **Fold C `same_pr_mitigatable_deferred_to_next_arc`** — dedicated `/vip/expired` landing page.
- **Fold D `informational` (1st trigger)** — Rigby repo_tool line-1 read-display truncation false-positive. Watch for 2nd.

### Carry-forward from S3003 (STILL OPEN)

- **Fold A `informational` (1st trigger)** — risk-gate T-slot vs T-ENVELOPE-N scoping. Watch for 2nd.
- **Fold C `informational` (1st trigger)** — Django reverse-O2O test cache-bust pattern. Watch for 2nd.

### Carry-forward from S3002 (STILL OPEN)

- **Fold A** — session-shape observation. **6th concrete continuous-cascade** now with S3008→S3009 (see S3009 Fold D). Watch for cascade-class break.
- **Fold C `informational` (T-ENVELOPE-0 dev-only)** — `componentDidCatch` fires twice in dev under StrictMode.
- **Fold D — ADR successor discipline VALIDATED PATTERN.** ADR-0005 ↔ ADR-0006.

### Carry-forward from S3001 (STILL OPEN)

- **Fold B `informational`** — future ADR-N misread risk. "γ ratified" implying interceptor policy is preserved by §3.3 wording.
- **Fold C `informational` (1st trigger)** — potential Playbook rule candidate: verify target research slot state before accepting scope. Watch for 2nd.

### Carry-forward from S3000 (STILL OPEN)

- **Fold A `informational` (1st trigger)** — potential Playbook rule candidate: reproduce failure at thinnest interface. Watch for 2nd.
- **Fold B `informational`** — residual APIClient-forcing shapes.

### Carry-forward from S2999 (STILL OPEN)

- **Fold B `active watch`** — metadata accretion governance. 4 detector keys currently. Trigger: 5+ keys OR 2+ consumers.
- **Fold C** — Rigby Tool Gap Ledger. File:line-only scope of consumer verifier.

### Carry-forward from S2998 (STILL OPEN)

- **Fold A `future_trigger`** — force=true × factory dedupe semantic mismatch.
- **Fold B `future_trigger`** — force re-dispatch could emit DeliverableEvent breadcrumb.
- **Fold C** — Rigby Tool Gap Ledger.

### Carry-forward from S2997 (STILL OPEN)

- **Fold B `future_trigger`** — dedupe strictness on stale-ref ACs.
- **Fold F** — Rigby Tool Gap Ledger. `orm_inspect_tool` doesn't support `metadata__<key>=value` JSON-path lookups.

### Carry-forward from S2996 (STILL OPEN)

- **Fold C `future_trigger`** — staleness toast reinforcement.
- **Fold E** — Rigby Tool Gap Ledger (sharpened). No in-UI Recheck action.

### Carry-forward from S2995 (STILL OPEN)

- **Fold C `future_trigger`** — staleness metadata → dedicated JSONField.
- **Fold D `future_trigger`** — periodic staleness beat.
- **Fold E** — Rigby Tool Gap Ledger. Metadata accretion governance.
- **Fold F `future_trigger`** — WorkspacePageNew param preservation.

### Carry-forward from S2994 (STILL OPEN)

- **Fold B `future_trigger`** — inline-helper density.
- **Fold C `future_trigger`** — Deliverables-tab type badge.
- **Fold D** — Rigby Tool Gap Ledger.

### Carry-forward from S2993 (STILL OPEN)

- **Fold B ledger candidate** — dry-run preview for send-to-rigby.
- **Fold C future_trigger** — executable-prompt tightening.

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
- **Fold B `future_trigger` from v0.8.0** — fold-authoring evidence-admission helper. 3-trigger threshold NOT yet met.
- **Post-close housekeeping (LOW priority).** Fill Playbook front-matter `commit_sha` + `content_hash` PLACEHOLDER fields for both v0.9.0 and v0.10.0.
- **Live browser smoke on S3004 VIP-expired modal.** ~5 min.
- **ADR-0007 twin-mirror deliverable** — post-close Rigby dispatch to workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c` for ratification-record provenance.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session. Candidate seeds from S3005 Folds A/B/C + S3006 Fold D + S3007 Fold C + S3008 Fold C + S3009 Fold B (3rd trigger, threshold met) still awaiting further Playbook amendment session.
- **ADR corpus:** ADR-0001 through ADR-0007. ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION: **4-of-5 files migrated** (Batches 1+2+3+B1 all shipped). Batch 4 (`views_platform_integrations.py`, 62 sites) + Batch 5 (`api_helpers.py`, disposition arc) remaining.
- **Spec→ship contract:** PLAYBOOK-7.7.1. 2× clean Flow B spec→ship this session (B1 pre-ratified spec, straight to A2 SIGN; Batch 3 full A1→implement→A2 cycle).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. 3× substantive Rigby SIGN cycles + 2× re-verify dispatches on Fold A hallucination. Rigby's third response acknowledged mistake as LLM-side, not tool bug — cleared to merge.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. 1 mid-flight decision surface (Fold E in-S3009 vs S3010) — not answered, default = defer applied.
- **Recycle discipline:** middleware/view diff → `make restart` (NOT `make celery-recycle`) per S3007/S3008/S3009 Fold C/B lineage (now 3rd trigger). Both PRs used correctly from outset.

---

## Wrapper pin note

The active PA conversation pin at S3009 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3009 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3009 shipped a clean two-PR sequential close following the S3008 joint recommendation shape:** B1 warm-up spec pre-ratified at S3008 → Rigby A2 SIGN → merge → `make restart` → live-smoke → Batch 3 full A1→migrate→A2→merge→restart→smoke cycle. `core/auth_middleware.py` now at 0 raw-pattern sites; `core/views_auto_distribution.py` fully migrated. ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION now at 4-of-5 files. Batch 4 (62 sites in views_platform_integrations) remains as the largest single-batch migration; Batch 5 (api_helpers disposition) is a separate substrate arc. **S3009 also surfaced a new Rigby-quality signal (Fold A LLM-side hallucination on file-level code claim, 1st trigger) — Claude's independent 3-channel verification (Read + Grep + git show HEAD) is the mitigation until 2nd trigger.**
