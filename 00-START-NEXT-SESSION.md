# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3011 CLOSED. **ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION arc is now FULLY COMPLETE.** All 5 MIGRATED_FILES clean of raw JsonResponse error envelopes (`views_platform_integrations.py` gumroad_webhook 3 sites closed as B1; extended AST-based str(e) body-leak lint ships as B2 with 32 grandfathered DRF Response debt sites cataloged). **T-ENVELOPE-3 opens as the primary S3012 arc** — retire `api_helpers.api_error` across ~90 caller sites in 4 primary files + 6 minor sites.

**2 feature PRs shipped this session.**

**PR #3698 (`96326c20e`) — B1: gumroad_webhook 3 error sites migrated.** L1382 (JSON decode fail) + L1393 (missing product_id) → `invalid_input` (400→400). L1447 (unhandled exception) → `internal_error` (500→500). **Safety upgrade:** str(e) leak at L1447 removed. Success paths L1418/L1428 preserved as raw JsonResponse per ADR §4.3 error-only scope. Rigby A1 (3 STRENGTHEN + 2 AGREE, 5 tool_runs); A2 (4 AGREE + 1 STRENGTHEN, 2 tool_runs). Live curl smoke post-`make restart` — 3 sites × PASS with fresh support codes (74d2/7905/a08c). str(e) confirmed in operator log ONLY, not user body.

**PR #3699 (`6a1d8645a`) — B2: AST-based str(e) body-leak lint + grandfather list.** Extended `scripts/lint_no_deprecated_family_b.py` with AST detector for `return JsonResponse/Response({...str(e) or f-string {e}...})` patterns. 32 pre-existing DRF Response leaks in `core/views_odds_sports.py` grandfathered as `STR_E_LEAK_GRANDFATHER` frozenset. `--regenerate-grandfather` flag for churn recovery. Stale grandfather detection at exit 0. Rigby A1 (DECIDE Shape 4 + 3 STRENGTHENs, 4 tool_runs); A2 (3 AGREE + 1 STRENGTHEN P1-minor, 2 tool_runs). Test evidence: 6/6 PASS (baseline / list / regenerate / new-leak-fail / stale-warn / syntax).

**B3 audit + rescope.** Grep-tool-grounded audit surfaced api_helpers.py `api_error` has ~90 caller sites across 4 primary files (`views_ab_testing.py` 37 / `views_learning_loop.py` 25 / `views_rag_observability.py` 13 / `tasks_conversations.py` 11) + 6 minor sites. Plus existing bug: 7 sites in `views_rag_observability.py` use `status_code=` kwarg api_error doesn't accept (would `TypeError`). Chris ratified Option F (defer to T-ENVELOPE-3 successor arc) after workflow correction on wall-clock time inflation (Fold C).

**Rigby SIGN quality this session:** 5 substantive SIGN cycles, all tool-grounded, ZERO hallucination triggers (matches S3010 zero-hallucination pattern — 2 sessions continuous).

**HEAD at close:** `6a1d8645a` + docs cascade PR (this file + handoff + INDEX regen + wrapper pin bump).

Full context:
- `docs/handoffs/SESSION_3011_ENVELOPE_CLOSEOUT_B1_B2.md` — 2-PR close, 5 folds (A/B/C/D/E), forward carries, T-ENVELOPE-3 arc open
- `docs/adr/ADR-0007-layered-envelope-policy.md` — parent ADR (T-ENVELOPE-2 CLOSED at S3011)
- `core/security/error_envelope.py:117-154` — helper (shipped S3008)
- `scripts/lint_no_deprecated_family_b.py` — expanded S3011 (Family B helpers + AST str(e) body-leak detection + grandfather set)

---

## S3012 primary directive — T-ENVELOPE-3 retire api_error()

**Primary arc:** Retire `core.api_helpers.api_error` across ~90 caller sites. Migrate to `emit_error_envelope(reason_code=..., request=request, hint=...)` per Family E contract (ADR-0007 §3.1).

### Scope

4 primary files (by site count):
- `core/views_ab_testing.py` — **37 sites**
- `core/views_learning_loop.py` — **25 sites**
- `core/views_rag_observability.py` — **13 sites** (bundle bug fix: `s/status_code=/status=/g` for 7 sites)
- `core/tasks_conversations.py` — **11 sites**

6 minor files (1-2 sites each):
- `core/tests/test_llm_call_wrapper.py`
- `core/tests/test_pilot_gates_authz_sweep_2789.py`
- `core/services/llm_call_wrapper.py`
- `core/services/agent_llm_router.py`
- `core/models_llm_telemetry.py`
- `core/models_deliberation.py`

### Recommended shape (per bias-toward-machine-speed post-Fold-C)

**4 sequential mini-PRs, one per primary file.** Each PR:
1. Read the file, identify all api_error sites + their status codes.
2. Route A1 to Rigby with proposed migration table (site → reason_code mapping + hint dict shape).
3. Implement (batch mechanical migration).
4. Route A2 to Rigby with diff + smoke evidence.
5. Ship. If Daphne-request-path file → `make restart` (Fold B). Otherwise `make celery-recycle`.
6. Add file to `MIGRATED_FILES` tuple in `scripts/lint_no_deprecated_family_b.py`.

**Bundle minor files (6 sites total) into a 5th PR** at the end. Or fold into the last primary-file PR if scope allows.

**Total estimate at Claude+Rigby machine-speed cadence:** ~45-90 min for full retirement.

### Reason code mapping guide

| api_error usage pattern | Recommended reason_code | typical_status |
|--|--|--|
| `api_error("Authentication required", ...)` | `not_authenticated` | 401 |
| `api_error("Test not found", status=404)` | `not_found` | 404 |
| `api_error("Missing required field: X")` | `invalid_input` | 400 |
| `api_error("Invalid JSON data")` | `invalid_input` | 400 |
| `api_error("Cannot start test in {status} status")` | `validation_error` | 400 |
| `api_error(str(e), status=500)` (exception fallback) | `internal_error` | 500 (drop str(e) leak → hint={exc_type}) |
| `api_error("Staff access required", ...)` | `permission_denied` | 403 |

### Bundled bug fix (per Chris ratification)

In the `views_rag_observability.py` migration PR:
- Fix `status_code=` kwarg (~7 sites at L43/L68/L98/L127/L155/L182/L210/L239/L293) — either `s/status_code=/status=/g` before migration OR just drop the kwarg entirely when migrating to `emit_error_envelope` (which uses `reason_code` inference for status).

### api_success disposition (deferred)

`api_error` is Family B (error surface). `api_success` (L63-70) is success surface — per ADR-0007 §3.3, `api_success` + `api_paginated` may stay canonical. T-ENVELOPE-3 focuses on `api_error` retirement. `api_success` disposition deferred to a follow-up (possibly T-ENVELOPE-4).

### After T-ENVELOPE-3 complete

- Retire `api_error` from `core/api_helpers.py` (breaking change; safe once all callers migrated).
- `core/api_helpers.py` reduces to `smart_truncate` + optionally `api_success`.
- ADR-0007 close (§4.3 T-ENVELOPE-2 + §4.4 T-ENVELOPE-3 both complete).

---

## S3012 alternative directive candidates

### Option A — Fold B Playbook amendment (5th trigger imminent)

**~20-30 min at machine-speed.** Fold B has hit 4 triggers (S3007/S3008/S3009/S3010→S3011). Extend `feedback_recycle_after_merge` into formal PLAYBOOK-7.4.5 rule (or v0.10.1 PATCH). Rule text ready in S3011 handoff Fold B section. Bundle candidate with T-ENVELOPE-3 close cascade.

### Option B — Sports odds leak drain arc (bundled with T-ENVELOPE-3 or standalone)

**~30-60 min at machine-speed.** Drain the 32 grandfathered DRF Response `str(e)` sites in `core/views_odds_sports.py`. Each drained site removes one grandfather entry from `STR_E_LEAK_GRANDFATHER`. When set is empty, drop the grandfather mechanism entirely.

Could bundle into T-ENVELOPE-3 if views_odds_sports.py is added to that arc's scope. But those sites are DRF Response (not api_error callers) — arguably a separate class of migration.

### Option C — Fresh engineering (Chris bias-engineering rule)

Per `feedback_engineering_bias_over_audit`. Concrete candidates:
- New spider / new agent capability / workspace tab enhancement.
- Signal aggregation rule / body-system monitor / dashboard.
- Chris raises specifics at S3012 open.

### Option D — Docs restructuring arc (queued at S2801)

Chris directive S2800 close (2026-07-16): open a parent-scoped research arc auditing `/docs/` using the `/docs/research/` pattern itself. Complementary to Chris's ebook idea (recorded S3010 in `project_ebook_from_docs_folder`).

### Option E — Chris's own priority

Chris may have surfaced other work between sessions (email, discord, personal channels not in Claude context). Chris-driven directive supersedes A/B/C/D.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3011 handoff (`docs/handoffs/SESSION_3011_ENVELOPE_CLOSEOUT_B1_B2.md`).
4. Optional state probes:
   - `git log --oneline -8` — should show docs cascade → `6a1d8645a` (PR #3699 B2 str(e) lint) → `96326c20e` (PR #3698 B1 gumroad_webhook) → `383f53949` (S3010 close cascade).
   - `python scripts/lint_no_deprecated_family_b.py` — confirm `✅ ADR-0007 Family B deprecation lint OK (5 files checked, 32 grandfathered str(e) leaks)`.
   - `grep -c "\bapi_error\b" core/views_ab_testing.py core/views_learning_loop.py core/views_rag_observability.py core/tasks_conversations.py` — confirm caller counts still match audit (37/25/13/11).

**Joint recommendation at close:** T-ENVELOPE-3 as primary S3012 arc (most-continuous close-out for the ADR-0007 envelope story). Bundle Fold B PLAYBOOK-7.4.5 amendment (Option A, ~20-30 min) into T-ENVELOPE-3 close cascade as a natural pairing. Sports odds leak drain (Option B) as follow-up after T-ENVELOPE-3 closes if session appetite remains.

---

## S3012 carry-forward seeds

### New from S3011

- **T-ENVELOPE-3 primary arc** — retire `api_helpers.api_error` across ~90 sites in 4 primary files + 6 minor sites. Bundle bug fix in `views_rag_observability.py` (`status_code`→`status`). See S3012 primary directive section above.
- **Fold B `5th trigger` in-flight** — v0.10.1 PATCH amendment for PLAYBOOK-7.4.5 (`make restart` requirement for Daphne request path). Bundle with T-ENVELOPE-3 close cascade.
- **Fold A `1st trigger` (S3011)** — 00-START line-number drift. Watch for 2nd. Do line-number lookups fresh at session open, don't trust doc-stored linenos.
- **Fold C `1st trigger` (S3011)** — Wall-clock time inflation in Claude scope estimates. Watch for 2nd. Use machine-speed framing (Claude+Rigby cadence ≈ 1/5 to 1/10 of human wall-clock).
- **Fold D `1st trigger` (S3011)** — Close-cascade scope estimates without caller audits. Watch for 2nd. Cross-session forward-carry arc estimates must include caller-count or file-count audit result.
- **Fold E `1st trigger` (S3011)** — MIGRATED_FILES lint scope-drift (helper-call vs raw-construction leak classes). Watch for 2nd.
- **Sports odds leak drain arc** — 32 DRF Response `str(e)` sites in `views_odds_sports.py` grandfathered by B2 lint. Follow-up arc; each drained site removes one grandfather entry.
- **future_str_e_variants** — `repr(e)` / `force_str(e)` / `f"{e!r}"` detection extension for B2 lint (per Rigby A2 STRENGTHEN, deferred beyond promised scope).

### Carried from S3010 (STATUS PRESERVED)

- **Fold B `4th → 5th trigger imminent`** — PLAYBOOK-7.4.5 amendment ready.
- **Fold A `1st trigger` (S3009 LLM-hallucination ledger `f4e8481f-...`)** — ZERO hallucinations at S3010 + S3011 (2 sessions continuous). Watch continues.
- **Fold C `1st trigger` (S3009 Rigby shell-exec ledger `e6e7fd6d-...`)** — still open. Watch for 2nd.
- **Fold B `1st trigger` from S3008** (`repo_tool.search no total_matches`) — still open. Bundle candidate with `e6e7fd6d-...` for repo_tool capability expansion arc.

### Carried from earlier sessions (STILL OPEN — unchanged this session)

- **Fold C `future_trigger` from S3006** — DRF-decorator refactor for inline auth checks. Deferred.
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

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session. **Fold B (5th trigger imminent)** — PLAYBOOK-7.4.5 amendment ready for v0.10.1 PATCH. Priority Option A for S3012 bundle with T-ENVELOPE-3 close cascade.
- **ADR corpus:** ADR-0001 through ADR-0007. **ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION FULLY COMPLETE.** T-ENVELOPE-3 (`api_helpers.py` retirement) opens as successor arc for S3012.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **2× clean Flow B spec→ship this session** (B1 A1→implement→A2→ship→restart→live-curl; B2 A1→implement→A2→ship). Plus 1 audit-driven decision cycle (B3 A1 rescope, no ship).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **5× substantive Rigby SIGN cycles this session** (B1 A1 + B1 A2 + B2 A1 + B2 A2 + B3 A1). Zero hallucination triggers. Matches S3010 pattern (2 sessions continuous).
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. 3 mid-flight decision surfaces (B1 shape, B2 sequential-vs-bundled, B3 audit rescope). All routed with plain-English framing.
- **Recycle discipline:** B1 (view diff) → `make restart` used correctly. **Fold B 4th trigger** (5th if T-ENVELOPE-3 primary-file PRs are Daphne request-path). B2 (lint-only) → no restart. Cascade PR (docs-only) → no restart.

---

## Wrapper pin note

The active PA conversation pin at S3011 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3011 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3011 shipped a clean 2-PR close following the S3011 00-START Option B recommendation:** gumroad_webhook migration (B1, PR #3698) → str(e) body-leak lint expansion (B2, PR #3699) → B3 audit-driven Chris rescope (Option F, T-ENVELOPE-3 opened for S3012). **ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION arc is now FULLY COMPLETE.** S3012 opens with T-ENVELOPE-3 as the primary directive (retire `api_helpers.api_error` across ~90 caller sites; machine-speed estimate ~45-90 min via 4 sequential mini-PRs). Rigby SIGN quality stayed clean this session (zero hallucination triggers — 2 sessions continuous).
