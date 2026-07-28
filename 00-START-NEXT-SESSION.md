# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3012 CLOSED. **T-ENVELOPE-3 arc is FULLY COMPLETE.** `api_helpers.api_error` retired across all 72 real caller sites (S3011 audit had counted 92 — 20 were false positives from `except Exception as api_error:` variable names + string-literal error-type labels). Four PRs shipped (#3701 / #3702 / #3703 / #3704). `ImportError` at Python import layer confirms retirement (stronger than any lint). ADR-0007 §4.3 close-note appended with all 4 PR SHAs. **S3013 opens with no in-flight envelope arcs** — fresh engineering or one of the queued follow-ups.

**4 feature PRs shipped this session.**

**PR #3701 (`04bc553ea`) — PR 1: views_ab_testing.py 36 sites.** Dead-code discovery: 26 sites in dead A/B testing handlers (URL routes removed at S1103c per `docs/audit-2026/HALF_BUILT_FEATURES_AUDIT.md`) + 10 in wired `/api/goals/*` handlers. Rigby DECIDE Shape A (migrate all 36 to prevent str(e) leaks if re-exposed). 15 exception fallbacks → `internal_error` with `logger.exception` + hint={source, exc_type} (str(e) leaks eliminated). 5/5 tests PASS incl. secret-leak assertion. Live smoke post-recycle: HTTP 401 clean envelope.

**PR #3702 (`3cffe6f0d`) — PR 2: views_learning_loop.py 24 sites.** First scripted migration (15 auth-guards). Script had line-shift bugs (3 source-name mis-attributions + 1 orphaned `insight.is_dismissed = True` line) — self-audit script caught all 4 pre-ship. Rigby Tool Gap Ledger entry logged as workspace deliverable `505dbdc1-9184-478a-b186-1f9e3912807a`. 5/5 tests PASS. 15 auth → not_authenticated / 3 not_found / 3 invalid_json / 2 missing_field / 1 validation_error.

**PR #3703 (`055bd8734`) — PR 3: views_rag_observability.py 12 sites + bundled bug fix.** 10 sites used `status_code=` kwarg that `api_error` REJECTS (TypeError → middleware → generic 500). Migration to `emit_error_envelope` restored intended 401/403/500 semantics. Live smoke verified fix: `curl /api/rag/observability/dashboard/` returned HTTP 401 with `RUR-AUTH-260728-8133`. str(e) leak at L293 eliminated with `logger.exception`. 2/2 tests PASS (dropped one test that hit unreachable code — `@superuser_required` decorator intercepts before in-view checks).

**PR #3704 (`dd2a527ee`) — PR 4: retire api_error() + ADR-0007 §4.3 close-note.** 1-line function deletion + docstring retirement note + ADR execution-record close-notes for both T-ENVELOPE-2-DEPRECATION (S3011) and T-ENVELOPE-3 (S3012) with all PR SHAs cited. `python -c 'from core.api_helpers import api_error'` → ImportError confirms retirement. Rigby-suggested "(Close-note; no policy change)" clarifier adopted per ADR-0001 §3.6 discipline.

**Rigby SIGN quality this session:** 8 substantive SIGN cycles, all tool-grounded, ZERO hallucination triggers (matches S3010 + S3011 pattern — **3 sessions continuous**). ~35 total tool_runs.

**HEAD at close:** `dd2a527ee` + docs cascade PR (this file + handoff + INDEX regen + wrapper pin bump).

Full context:
- `docs/handoffs/SESSION_3012_T_ENVELOPE_3_COMPLETE.md` — 4-PR close, 5 folds (A/B/C/D/E), forward carries, Chris directive transcript.
- `docs/adr/ADR-0007-layered-envelope-policy.md` §4.3 — close-notes appended.
- `core/api_helpers.py` — `api_error()` retired; only `smart_truncate` + `api_success` remain.
- `scripts/lint_no_deprecated_family_b.py` — 8 files lint-locked, 32 grandfathered.

---

## S3013 primary directive candidates

**No in-flight arc.** Chris directive-required to select. Options ranked:

### Option A — Fresh engineering (per bias-engineering rule)

Per `feedback_engineering_bias_over_audit`. Concrete candidates:
- New spider / new agent capability / workspace tab enhancement.
- Signal aggregation rule / body-system monitor / dashboard.
- Chris raises specifics at S3013 open.

**Recommended.** Chris has flagged bias-engineering-over-audit multiple times; 5 consecutive envelope/substrate sessions (S3008 → S3012) is enough substrate work for now.

### Option B — Task #7: Delete dead A/B testing handlers per HALF_BUILT_FEATURES_AUDIT

**~1 session at machine-speed.** Delete ~11 dead handlers in `core/views_ab_testing.py` L82-501 (~600 lines). Follow-up from S3012 PR 1. Needs Chris ratification (scope creep beyond retirement — pure feature-audit cleanup). Rigby offered to SIGN one-paragraph ticket scope (delete-only + URL cleanup + tests).

**Trade-off:** cleans up ~600 lines of confirmed dead code + reduces future reader confusion. Chris flagged HALF_BUILT_FEATURES_AUDIT as a broader theme.

### Option C — Task #8: DRF-decorator refactor for 15 auth guards in views_learning_loop.py

**~1 session.** Replace boilerplate `if not request.user.is_authenticated: return emit_error_envelope(...)` with `@api_view` + `permission_classes([IsAuthenticated])`. Rigby offered SIGN.

**Trade-off:** cleaner code, but 15 sites are already migrated + working. Pure aesthetic cleanup.

### Option D — Fold B PLAYBOOK-7.4.5 amendment (`make restart` for Daphne request path)

**~20-30 min at machine-speed.** Fold B trigger count from S3011 was "5th trigger imminent". This session used `make recycle-all` (broader superset) for all 4 PRs — trigger count unclear whether recycle-all satisfies the same signal. Assess at S3013 open.

### Option E — Sports odds leak drain arc

**~30-60 min at machine-speed.** Drain the 32 grandfathered DRF Response `str(e)` sites in `core/views_odds_sports.py`. Each drained site removes one grandfather entry.

### Option F — Chris's own priority

Chris may have surfaced other work between sessions (email, discord, personal channels not in Claude context). Chris-driven directive supersedes A/B/C/D/E.

**Joint recommendation at close:** Option A (fresh engineering) as default — Chris's bias-engineering rule + 5 consecutive envelope/substrate sessions calls for a change of shape. If Chris wants continuity, Option B (dead-handler deletion) is the natural next step from PR 1 discovery.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3012 handoff (`docs/handoffs/SESSION_3012_T_ENVELOPE_3_COMPLETE.md`).
4. Optional state probes:
   - `git log --oneline -8` — should show docs cascade → `dd2a527ee` (PR #3704 retire api_error) → `055bd8734` (PR #3703 rag_observability) → `3cffe6f0d` (PR #3702 learning_loop) → `04bc553ea` (PR #3701 ab_testing) → `99ed07f34` (S3011 close cascade).
   - `python scripts/lint_no_deprecated_family_b.py` — confirm `✅ 8 files checked, 32 grandfathered str(e) leaks`.
   - `python -c 'from core.api_helpers import api_error'` — should ImportError.
   - `python -c 'from core.api_helpers import smart_truncate, api_success; print("OK")'` — should print OK.

---

## S3013 carry-forward seeds

### New from S3012

- **Task #7 — Delete dead A/B testing handlers** per HALF_BUILT_FEATURES_AUDIT. ~11 handlers, ~600 lines. Needs Chris ratification. Follow-up from PR 1 dead-code discovery.
- **Task #8 — DRF-decorator refactor** for 15 auth guards in views_learning_loop.py. ~1 session.
- **Fold A `1st trigger`** (S3012) — S3011 audit counted grep matches, not real callers (20 false positives out of 92). Watch for 2nd trigger. Mitigation candidate: `grep -c "\bapi_error\s*\("` instead of `\bapi_error\b`.
- **Fold B `1st trigger`** (S3012) — Migration-script text-replacement without line-offset tracking. **Workspace deliverable `505dbdc1-9184-478a-b186-1f9e3912807a` already logged.** Playbook rule candidate: "Any scripted multi-site migration must include an automated post-pass audit that checks (1) per-handler source matches containing def, and (2) envelope emission is in the correct exception/control block."
- **Fold C `informational`** — `@superuser_required` decorator is a Family B → Family E migration candidate (returns `{success: false, error: "..."}` legacy shape). Separate T-slot arc — possibly T-ENVELOPE-4.
- **Fold D `1st trigger`** — Aggressive pipelining safe when audits are read-only. Pattern: during test-wait cycles, forward-scout the next PR's audit + Rigby A1 is safe; code writes still gate on prior PR merge.
- **Fold E `informational`** — Test-writing gotcha: handler branch ordering matters. Read handler top-to-bottom before writing branch-specific tests.

### Carried from S3011 (STATUS PRESERVED)

- **Fold B `5th trigger imminent → assess post-S3012`** — PLAYBOOK-7.4.5 amendment (`make restart` for Daphne request path). This session used `make recycle-all` for all 4 PRs. Whether recycle-all satisfies the Fold B signal or refills the trigger count is unclear — assess at S3013 open.
- **Fold A `1st trigger` (S3009 LLM-hallucination ledger `f4e8481f-...`)** — ZERO hallucinations at S3010 + S3011 + S3012 (**3 sessions continuous**). Watch continues.
- **Fold C `1st trigger` (S3009 Rigby shell-exec ledger `e6e7fd6d-...`)** — still open. Watch for 2nd.
- **Fold B `1st trigger` from S3008** (`repo_tool.search no total_matches`) — still open. Bundle candidate with `e6e7fd6d-...` for repo_tool capability expansion arc.

### Carried from earlier sessions (STILL OPEN — unchanged this session)

- **Sports odds leak drain arc** — 32 DRF Response `str(e)` sites in `views_odds_sports.py` grandfathered.
- **future_str_e_variants** — `repr(e)` / `force_str(e)` / `f"{e!r}"` detection extension for B2 lint (per Rigby A2 STRENGTHEN from S3011, deferred).
- **Fold C `future_trigger` from S3006** — DRF-decorator refactor for inline auth checks. **Superseded by Task #8** (which is the concrete DRF-decorator refactor for views_learning_loop.py's 15 sites).
- **Fold A/B/C `informational` (1st trigger) from S3005** — PLAYBOOK-7.7.1 abort-early clause / ADR-baseline drift / `refines:` frontmatter field. Watch for 2nd triggers.
- **Fold A `2nd trigger` from S3004** — Fold-Drain-Same-Surface pattern. Watch for 3rd.
- **Fold B `informational` (1st trigger) from S3004** — shared-const derived-union frontend pattern. Watch for 2nd.
- **Fold C `same_pr_mitigatable_deferred_to_next_arc` from S3004** — dedicated `/vip/expired` landing page.
- **Fold D `informational` (1st trigger) from S3004** — Rigby repo_tool line-1 read-display truncation false-positive. Watch for 2nd.
- **Fold A `informational` (1st trigger) from S3003** — risk-gate T-slot vs T-ENVELOPE-N scoping.
- **Fold C `informational` (1st trigger) from S3003** — Django reverse-O2O test cache-bust pattern.
- **Fold C `informational` (T-ENVELOPE-0 dev-only) from S3002** — `componentDidCatch` fires twice in dev under StrictMode.
- **Fold D from S3002** — ADR successor discipline VALIDATED PATTERN.
- **Fold B `informational` from S3001** — future ADR-N misread risk.
- **Fold C `informational` (1st trigger) from S3001** — verify target research slot state before accepting scope.
- **Fold A `informational` (1st trigger) from S3000** — reproduce failure at thinnest interface.
- **Fold B `informational` from S3000** — residual APIClient-forcing shapes.
- **Fold B `active watch` from S2999** — metadata accretion governance.
- **Fold C from S2999** — Rigby Tool Gap Ledger, file:line-only scope of consumer verifier.
- **Fold A/B/C `future_trigger` from S2998** — force=true × factory dedupe semantic mismatch / force re-dispatch could emit DeliverableEvent breadcrumb / Rigby Tool Gap Ledger.
- **Fold B `future_trigger` from S2997** — dedupe strictness on stale-ref ACs.
- **Fold F from S2997** — Rigby Tool Gap Ledger (`orm_inspect_tool` JSON-path lookups).
- **Fold C `future_trigger` from S2996** — staleness toast reinforcement.
- **Fold E from S2996** — Rigby Tool Gap Ledger (no in-UI Recheck action).
- **Fold C/D `future_trigger` from S2995** — staleness metadata + periodic staleness beat.
- **Fold E from S2995** — Rigby Tool Gap Ledger (metadata accretion governance).
- **Fold F `future_trigger` from S2995** — WorkspacePageNew param preservation.
- **Fold B/C/D `future_trigger` from S2994** — inline-helper density / Deliverables-tab type badge / Rigby Tool Gap Ledger.
- **Fold B/C ledger candidates from S2993** — dry-run preview for send-to-rigby / executable-prompt tightening.
- **Signal-tweak follow-up for `finding_type` classifier from S2992** (2 acceptable-misses).
- **Data-migration-vs-management-command pattern from S2992** (3rd-trigger check).
- **Dry-run counts pattern from S2991** (3rd-trigger check).
- **Contract-lock-in guardrail from S2991** — updated set.
- **F-D3-tracker-scope wire-up / F-D2-broad LLM-bypass audit / Chris 1805 cap-drift reconciliation / Canonical Briefing v2 scope toggle / _TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT substrate fix / Send-to-Rigby follow-ups from S2988** (S2989-S2990 batch).
- **Chris browser visual checks on S2984 arcs section + S2985 Canonical Briefing tab strip (~5 min each).**
- **Rigby `claude_code_tool` safeguards.** Log to Rigby Tool Gap Ledger.
- **Systemic auth-XHR treatment (S2984 Fold).**
- **Live-dispatch smoke on S2982 stage-doc guardrails (~15 min).**
- **Exercise PLAYBOOK-7.7.4 against a sibling repo.**
- **Browser UX smoke on S2980 Theme Signals UX upgrade (~5 min).**
- **Phase B Theme Signals — "Why now" LLM summarizer (~1 session).**
- **Phase B Theme Signals — who-benefits/who-loses (~1-2 sessions).**
- **Theme Signals sub-tab persistence via localStorage (~30 min).**
- **Rigby Tool Gap Ledger — Fold D from S2982.** DB uniqueness constraint on `AgentExecution.celery_task_id` (~30-60 min).
- **Fold B `future_trigger` from v0.8.0** — fold-authoring evidence-admission helper (3-trigger threshold NOT yet met).
- **Post-close housekeeping (LOW priority).** Fill Playbook front-matter `commit_sha` + `content_hash` PLACEHOLDER fields for v0.9.0 and v0.10.0.
- **Live browser smoke on S3004 VIP-expired modal (~5 min).**
- **ADR-0007 twin-mirror deliverable** — post-close Rigby dispatch to workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c` for ratification-record provenance.
- **Batch 3 400→404 image/video not_found verification** (from S3009 forward-carry) — needs UserPlatformAccount test data setup for chris.
- **`superuser_required` decorator Family B → Family E migration candidate** (Fold C from S3012). Would touch ~N decorated endpoints. Separate T-slot arc — possibly T-ENVELOPE-4.
- **`agents/views_monitoring.py` 7 sites** using `core.api_responses.api_error` (different helper). Separate arc — evaluate whether `core.api_responses.api_error` should also be retired.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session. **Fold B `5th trigger imminent` from S3011** — PLAYBOOK-7.4.5 amendment status unclear post-S3012 (see Fold B carry-forward above).
- **ADR corpus:** ADR-0001 through ADR-0007. **ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION + T-ENVELOPE-3 both CLOSED.** No open ADR successor arcs.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **4× clean Flow B spec→ship this session** (each PR: A1→implement→A2→ship→recycle).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **8× substantive Rigby SIGN cycles this session.** Zero hallucination triggers. 3 sessions continuous.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routings this session were arc-kickoff + pipelining + close-scope-clarification only. All PR-level shape decisions handled Claude ↔ Rigby.
- **Recycle discipline:** `make recycle-all` used for all 4 PRs (Daphne request path — Fold B satisfied via broader superset).

---

## Wrapper pin note

The active PA conversation pin at S3012 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3012 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3012 shipped a clean 4-PR arc close following the S3012 00-START T-ENVELOPE-3 primary directive:** views_ab_testing → views_learning_loop → views_rag_observability (with bundled bug fix) → api_helpers.api_error retirement + ADR close-note. **T-ENVELOPE-3 arc is now FULLY COMPLETE.** ADR-0007 §4.3 both T-slots closed. S3013 opens with no in-flight envelope arcs — fresh engineering recommended (Chris bias-engineering rule + 5 consecutive envelope/substrate sessions).
