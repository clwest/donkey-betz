# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3015 CLOSED. **U3 Bulk-promote SignalClusters shipped** (PR #3710, `c388f006a`) + **4 post-ship browser-layer hotfixes** (PR #3712 `a01bb6740` active-workspace routing / PR #3713 `756f7a6f` TRIAGE visibility + dedupe UX polish / PR #3714 `47c1cbd57` Token-auth on `/api/initiatives/`). Third consecutive user-facing session (S3013 U1 → S3014 U2 → S3015 U3). Backend U3: refactored U2's core creation logic into shared helper + new bulk endpoint `POST /api/platform/signal-cluster/bulk-create-initiative/` + Cluster Explorer table gets checkboxes + sticky action bar + confirm modal + dismissible result summary card + 10 new tests (all PASS, S3014's 8 also still PASS = 18/18). Rigby A2 zoom-out mitigation: 100-item batch cap. Zero new model fields. **Chris browser-verified end-to-end** — U2 single-cluster promotion + U3 bulk promotion both write to the active workspace, land in TRIAGE, visible in Initiatives tab.

**1 feature PR shipped this session.**

**PR #3710 (`c388f006a`) — U3: Bulk-promote SignalClusters to Initiatives (+ optional briefs).**

- **Backend refactor:** extracted `_resolve_target_workspace()` + `_create_initiative_from_cluster_core()` helpers. S3014 single-cluster view refactored to thin wrapper (8/8 S3014 tests still PASS post-refactor).
- **New endpoint:** `POST /api/platform/signal-cluster/bulk-create-initiative/`. Body `{cluster_ids: [...], generate_brief?: bool, workspace_id?: str}`. Returns 200 with per-row results. Partial-failure semantics: initiative-level failure ≠ brief-level failure. 100-item batch cap. De-dupes within request + preserves order.
- **Frontend:** checkbox column on Cluster Explorer → sticky "Create N initiatives" bar when ≥1 selected → `BulkPromoteModal` (shows first 10 cluster names + generate-briefs toggle) → post-run `BulkPromoteResultCard` (dismissible, expandable failures panel with deep links to `existing_initiative` pointers).
- **Tests:** new `core/tests/test_s3015_bulk_create_initiatives_from_clusters.py` (10 tests, all PASS in ~1s). Includes Rigby A2 zoom-out regression (100-cap 400).

**Rigby SIGN quality this session:** 3 substantive SIGN cycles, all tool-grounded, ZERO hallucination triggers (matches S3010 → S3014 pattern — **6 sessions continuous**).

**HEAD at close:** `47c1cbd57` (Token-auth hotfix) after the ship trail: `c388f006a` (U3) → `b8f9b889f` (docs cascade) → `a01bb6740` (active-workspace) → `756f7a6f` (TRIAGE visibility + dedupe polish) → `47c1cbd57` (Token-auth fix) + this docs cascade PR (handoff post-ship section + 00-START refresh + INDEX regen).

Full context:
- `docs/handoffs/SESSION_3015_U3_BULK_CLUSTER_PROMOTION.md` — full session close, 4 folds (A/B/C/D), forward carries.
- `core/views_platform_command.py` — `_create_initiative_from_cluster_core` helper + `bulk_create_initiatives_from_clusters_view` + refactored single view.
- `core/tests/test_s3015_bulk_create_initiatives_from_clusters.py` — 10 tests.
- `frontend/src/pages/workspace/tabs/signals/SignalsClustersView.tsx` — checkbox column + BulkPromoteModal + BulkPromoteResultCard.
- `frontend/src/lib/api.ts` — `signalsApi.bulkCreateInitiativesFromClusters()`.

---

## S3016 primary directive candidates

**No in-flight arc.** Chris directive-required to select. Options ranked:

### Option A — Fresh engineering (per bias-engineering rule)

- **U4 candidate:** AgentDecisionSummary bulk-decide. `pending_decisions` currently mixes HumanAttentionItem (which U1 handles) + AgentDecisionSummary (which nothing bulk-handles). ~1 session.
- **U5 candidate:** Post-create auto-link cluster ↔ initiative via embeddings. Use existing `initiative_signal_linker.auto_link_initiative_signals()` after cluster→initiative create. ~30 min.
- **U6 candidate:** Bulk cluster → initiative UX polish — inline per-row name editing in the confirm modal (currently all-defaults). Requires expanded modal + per-row state. ~1 session.
- Chris raises specifics at S3016 open.

**Recommended.** U5 (auto-link) is the fastest — leverages existing service. Or U4 (parallel bulk pattern for AgentDecisionSummary — matches U1 shape).

### Option B — Fold A codification: bulk endpoint scope-limit-cap standard

**~30 min.** Retrofit `MAX_BATCH_SIZE` to S3013 `BulkAttentionDecideView` (currently uncapped) + document as bulk-endpoint invariant. Small ADR or Playbook amendment candidate. Needs Chris ratification.

### Option C — Fold A codification (S3014): "diagnostic on create" invariant

**~1 session.** Broader Playbook rule that all user-triggered create endpoints resolve non-null required-for-integrity FKs before create. Would touch multiple existing views (audit + amend). Needs Chris ratification.

### Option D — 9th test coupling (S3013 non-blocking carry)

**~15 min.** Test asserting `governance_view.pending_decisions[].id` → `HumanAttentionItem.id`.

### Option E — Task #7: Delete dead A/B testing handlers (S3012 carry)

**~1 session.** ~11 dead handlers, ~600 lines. Needs Chris ratification.

### Option F — Chris's own priority

Chris-driven directive supersedes A/B/C/D/E.

**Joint recommendation at close:** Option A — U5 (fastest, uses existing service). If Chris wants continuation of the bulk-shape pattern, U4 (AgentDecisionSummary bulk-decide) parallels S3013 U1.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3015 handoff (`docs/handoffs/SESSION_3015_U3_BULK_CLUSTER_PROMOTION.md`).
4. Optional state probes:
   - `git log --oneline -5` — should show docs cascade → `c388f006a` (PR #3710 U3) → `9a5cef211` (S3014 close cascade) → `e00e5880f` (PR #3708 U2).
   - `python manage.py test core.tests.test_s3015_bulk_create_initiatives_from_clusters core.tests.test_s3014_create_initiative_from_cluster --keepdb` — should return 18/18 OK in ~1s.
   - Browser smoke: Workspace → Intelligence tab → Signals sub-tab → Cluster Explorer → check 2-3 rows → confirm sticky "Create N initiatives" bar appears.

---

## S3016 carry-forward seeds

### New from S3015

- **Fold E `1st trigger`** — Browser-layer defects invisible to shell tests + Rigby SIGN. 4 hotfixes shipped this session broke immediately in Chris's real browser despite passing all backend tests + Rigby A2 SIGN + shell probes. Missing coverage class: browser-session + Token-auth path testing. Every test in this session used session auth; frontend uses Token auth exclusively. Watch for 2nd trigger.
- **Fold F `1st trigger`** — "Empty state" symptom has multiple silent-degradation causes (browser cache / auth session/token / middleware auth path / queryset scope / frontend filter). Formalize the diagnostic tree so future triage compresses.
- **Fold G `informational`** — `UnifiedTokenAuthenticationMiddleware.PUBLIC_PATHS` uses `startswith` matching. Audit for other bare-prefix entries that might be broader than their comment suggests (the `/api/initiatives/` entry was meant for `/api/initiatives/<uuid>/action-items/` sub-path but caught the list endpoint).
- **U4 candidate:** AgentDecisionSummary bulk-decide.
- **U5 candidate:** Post-create auto-link via `initiative_signal_linker`.
- **U6 candidate:** Per-row name editing in bulk cluster confirm modal.
- **Fold A `1st trigger`** — Bulk-endpoint scope-limit-cap standard. Retrofit BulkAttentionDecideView (uncapped) + codify as invariant.
- **Fold B `informational`** — Refactor-first for U-N when U-(N-1) shipped shared logic.
- **Fold C `informational`** — Bulk-endpoint invariants (order preserved + de-dupe within request).
- **Fold D `3rd trigger`** — Cycle 1A verify-before-build. 3 consecutive triggers.
- **UI candidate:** progress bar during bulk create (currently single mutation call; could show optimistic per-item progress).

### Carried from S3014 (STATUS PRESERVED)

- **Rigby non-blocking A2 suggestion (S3013):** 9th test coupling.
- **Batch Defer for Governance (S3013):** needs new bulk endpoint.
- **Fold A `1st trigger` (S3014)** — "Diagnostic on create" invariant codification. Watch for 2nd.
- **Fold B `informational` (S3014)** — `create_deliverable` factory `trigger_source` bypass documentation.
- **Fold C `informational` (S3014)** — Session 843 `parent_object_type/id` audit opportunity.
- **Fold D `2nd trigger` (rolled)** — Rigby web_fetch_tool auth clarification (Rigby Tool Gap Ledger candidate).

### Carried from S3013 (STATUS PRESERVED)

- **Fold A `3rd trigger` this session** — Cycle 1A verify-before-build (pattern reinforcement).
- **Fold B `1st trigger` (S3013)** — S2785 auth-regression mutation-path blind spot.
- **Fold D `future_trigger` (S3013)** — `BulkAttentionDecideView` uses Family B envelope shape.
- **Fold E `informational` (S3013)** — Bulk endpoint decision enum inconsistency.

### Carried from S3012 (STATUS PRESERVED)

- **Task #7 — Delete dead A/B testing handlers** per HALF_BUILT_FEATURES_AUDIT. Needs Chris ratification.
- **Task #8 — DRF-decorator refactor** for 15 auth guards in views_learning_loop.py.
- **Fold C `informational`** — `@superuser_required` decorator Family B → Family E migration candidate.

### Carried from S3011 (STATUS PRESERVED)

- **Fold B `5th trigger imminent → assess post-S3015`** — PLAYBOOK-7.4.5 amendment (`make restart` for Daphne). All 3 recent sessions used `make recycle-all`.
- **Fold A `1st trigger` (S3009 LLM-hallucination ledger)** — ZERO hallucinations at S3010-S3015 (**6 sessions continuous**).
- **Fold C `1st trigger` (S3009 Rigby shell-exec ledger)** — still open.
- **Fold B `1st trigger` from S3008** (`repo_tool.search no total_matches`) — bundle candidate for repo_tool capability expansion arc.

### Carried from earlier sessions (STILL OPEN — unchanged this session)

- **Sports odds leak drain arc** — 32 DRF Response `str(e)` sites in `views_odds_sports.py` grandfathered.
- **future_str_e_variants** — `repr(e)` / `force_str(e)` / `f"{e!r}"` detection extension for B2 lint.
- **Fold C `future_trigger` from S3006** — DRF-decorator refactor for inline auth checks (superseded by Task #8).
- **Fold A/B/C `informational` (1st trigger) from S3005** — PLAYBOOK-7.7.1 abort-early clause / ADR-baseline drift / `refines:` frontmatter field.
- **Fold A `2nd trigger` from S3004** — Fold-Drain-Same-Surface pattern.
- **Fold B `informational` (1st trigger) from S3004** — shared-const derived-union frontend pattern.
- **Fold C `same_pr_mitigatable_deferred_to_next_arc` from S3004** — dedicated `/vip/expired` landing page.
- **Fold D `informational` (1st trigger) from S3004** — Rigby repo_tool line-1 read-display truncation false-positive.
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
- **Fold A/B/C `future_trigger` from S2998** — force=true × factory dedupe / DeliverableEvent breadcrumb / Rigby Tool Gap Ledger.
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
- **Chris browser visual checks on S2984 arcs section + S2985 Canonical Briefing tab strip.**
- **Rigby `claude_code_tool` safeguards.** Log to Rigby Tool Gap Ledger.
- **Systemic auth-XHR treatment (S2984 Fold).**
- **Live-dispatch smoke on S2982 stage-doc guardrails.**
- **Exercise PLAYBOOK-7.7.4 against a sibling repo.**
- **Browser UX smoke on S2980 Theme Signals UX upgrade.**
- **Phase B Theme Signals — "Why now" LLM summarizer.**
- **Phase B Theme Signals — who-benefits/who-loses.**
- **Theme Signals sub-tab persistence via localStorage.**
- **Rigby Tool Gap Ledger — Fold D from S2982.** DB uniqueness constraint on `AgentExecution.celery_task_id`.
- **Fold B `future_trigger` from v0.8.0** — fold-authoring evidence-admission helper.
- **Post-close housekeeping (LOW priority).** Fill Playbook front-matter `commit_sha` + `content_hash` PLACEHOLDER fields for v0.9.0 and v0.10.0.
- **Live browser smoke on S3004 VIP-expired modal.**
- **ADR-0007 twin-mirror deliverable.**
- **Batch 3 400→404 image/video not_found verification** (from S3009 forward-carry).
- **`superuser_required` decorator Family B → Family E migration candidate** (Fold C from S3012).
- **`agents/views_monitoring.py` 7 sites** using `core.api_responses.api_error`.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session.
- **ADR corpus:** ADR-0001 through ADR-0007. No open ADR successor arcs.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship this session.**
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **3× substantive Rigby SIGN cycles. Zero hallucination triggers. 6 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing this session: "continue with U3" (ratifying joint recommendation) + "Internet blip continue" (resume after blip).
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` used pre-merge (smoke) and post-merge (constitutional).
- **Verify-before-build (Cycle 1A):** **3rd consecutive trigger** — extracted + reused U2 core helpers for U3 bulk endpoint.
- **Fold classification (PLAYBOOK-6.10.8):** Rigby A2 zoom-out concern classified `same_pr_actionable` (100-cap adopted in same PR).

---

## Wrapper pin note

The active PA conversation pin at S3015 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3015 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3015 shipped a clean 1-PR arc following the S3015 00-START Option A (fresh engineering / U3 bulk-promote clusters) primary directive. Third consecutive user-facing session (U1 → U2 → U3). S3016 opens with no in-flight arc.**
