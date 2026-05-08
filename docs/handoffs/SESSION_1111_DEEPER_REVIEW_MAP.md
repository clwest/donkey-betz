---
title: "Session 1111 — deeper repo review map (docs-only continuity)"
date: 2026-05-08
status: active
session: 1111
previous_handoff: SESSION_1110_MOUNTED_ROUTE_FALLBACKS.md
---

# Session 1111 — deeper repo review map

## TL;DR

- **Docs-only session.** No code changes, no artifact untracking, no
  archive banners.
- Records the structured map of remaining cleanup / deeper-review
  findings that Sessions 1108–1110 deliberately did not touch, so the
  next session can pick from a single ranked queue instead of re-running
  the audit.
- The canonical cleanup workspace remains
  [`docs/audit/CLEANUP_PLAN.md`](../audit/CLEANUP_PLAN.md). This handoff
  is the **deeper-review companion** to that plan, not a duplicate.

**HEAD at investigation time:** `f8ab330d` on `main`.
Guardrails: 0 CONFLICT, 4 DOC_ONLY (advisory), 2 VERIFIED.

---

## Already fixed (reference only)

| Item | Where | Status |
|---|---|---|
| 5 mounted-but-broken routes (`/visualization/`, `/ai-building-products/`, `/share/<token>/`, `/nexus/`, `/intelligence/`) | PR #2062 / commit `f8ab330d` | Redirects or SPA-shell delegation. Smoke tests in `core/tests/test_mounted_route_fallbacks.py`. |
| `core/views_visualization.py` `ai_agents_visualization`, `activity_monitor`, `ai_building_products` | PR #2062 | Were dormant template-render bodies; now redirects. |
| `core/views_ecosystem.py` `ai_building_products` | PR #2062 | Same. |
| `core/views_share.py` 5 share-state renders | PR #2062 | Inline HTML fallbacks; status semantics preserved. |
| `core/views_unified_intelligence.py` `unified_intelligence_dashboard` | PR #2062 | Now `react_app(request)`. |
| `.rag/` artifact tracking | Sessions 1108–1109 | Producer + untrack done. Production RAG still pgvector. |
| Repo guardrails CI | Session 1107 | Wired to PR-time CI; strict mode on with named carve-out for inventory freshness. |
| context-kit upstream fixes + orient/inspect/verify | Sessions 1101–1106 | Live. |

---

## Still active / document, don't clean

These show up in the "underdocumented active" bucket. They are **not**
dead — they need a `docs/topics/*.md` entry, not removal.

| Path | Classification | Evidence | Risk | Recommended next action |
|---|---|---|---|---|
| `revenue/revenue_verifier.py` (`RevenueRealityVerifier`) | ACTIVE, undocumented | `ai_platform/views.py:15` imports + instantiates at module load. `ai_platform.urls` mounted at root. | Medium — runs on every web boot, talks to Redis | Document in `docs/topics/`. Confirm Redis fail-open semantics before any refactor. Do **not** archive. |
| `advisors/registry.py` + `advisors/llm_advisor_system.py` | ACTIVE, undocumented | 16+ active importers (PA, agents, opportunity analyzer, audit coordinators). `advisors/` is a namespace package (no `__init__.py`). | Low | Document as a first-class module. Note the registry pattern + 25 advisor seed list. |
| `llm/{base,ollama_provider,router}.py` (top-level) | ACTIVE, undocumented | Imported by `core/views.py` and `core/views/main.py` for `ChatMessage`. ~50 lines total across 3 files. | Low (easy to confuse with `core.services.agent_llm_router` and `LLMProviderRegistry`) | Document the relationship, or fold into `core/services/` to remove the top-level surface. |
| `core/tasks_*.py` (12 modules, `_impl_*` indirection) | ACTIVE, undocumented | `core/tasks.py` re-imports `_impl_*` functions. Only `tasks_agents` is in `app.conf.imports`; the others are loaded transitively. | Low — works, but easy to misread as dead | Document the pattern in `docs/topics/celery-workers.md` (or a new `core/tasks-layout.md`). |
| `core/urls_unified.py` (4,750-line monolith via `core/urls.py:1559`) | ACTIVE, undocumented | Most of the app's URL surface lives here. Entry is `core/urls.py`, but most paths are in `urls_unified.py`. | Low — works | Document the urls.py vs urls_unified.py relationship; flag as "split is historical, not architectural." |

---

## Partial / needs product decision (do not auto-archive)

These are "started but unfinished, may be strategically important." Each
needs a Rigby/Chris call before any cleanup PR.

| Path | Classification | Evidence | Strategic? | Recommended next action |
|---|---|---|---|---|
| `agents/urls_deployment.py` + `agents/views_deployment*.py` + `agents/views_all_agents*.py` | PARTIAL — fully built, never wired | 14 view functions across 5 modules. URL conf not included. Only one external test ref (`tests/spiders/test_agent_modes.py` imports `execute_agents_improved`). All modules import OK. | Possibly — looks like a complete agent-deploy-to-project feature | Document the option. Keep in place. Ask Rigby: deliberate hold, or oversight? If "hold," add a `# DEFERRED: not yet wired (Session 1111 review)` banner. |
| `revenue/models.py` (4 models, one missing `app_label`, app not in INSTALLED_APPS) | PARTIAL — broken on import | Smoke `import revenue.models` raises `RuntimeError: ... doesn't declare an explicit app_label`. Zero importers. Models would never have migrated. | Possibly — could be persistence layer for the active `RevenueRealityVerifier` | Document the gap. Either rehome models in a real app (e.g., `core/models_revenue.py`), or delete `models.py` and keep the verifier Redis-only. Needs product call. |
| `ai_core/intelligence/orchestration.py` | PARTIAL — defensive mock fallback | `try: from ml_pipeline.pipeline import MLPipeline except ImportError: MLPipeline = MockMLPipeline`. Smoke import OK, but degrades silently to no-op. Only active importer: `archive/scripts/verify_llm_integration.py`. | Yes — sits in the same family as `learning_loop.py` (which falls back to the **real** `EnhancedMLPipeline`) | Document the layer. Decision: (a) alias `MLPipeline = EnhancedMLPipeline` in `ml_pipeline/__init__.py` so the layer runs on real code, or (b) treat the layer as DORMANT and add archive banners. |
| `ai_core/intelligence/monitoring_dashboard.py` | BROKEN — no active importer | `from orchestration import orchestrator` (bare top-level) → `ModuleNotFoundError`. Plus unguarded `from ml_pipeline.pipeline import MLPipeline`. | No — listed because it sits in the same module family | Document as broken-but-unreachable. Add archive-candidate banner in PR-C below. |
| `ai_core/intelligence/testing_suite.py` | BROKEN — no active importer | Same `from orchestration import orchestrator` failure | No | Same as above. |
| `sports_betting/` (whole app) | PARTIAL — planned app, never wired | `apps.py` exists, real `SportsBettingConsumer` with mock data, hardcoded mock `views.py`, empty `models.py`. Not in INSTALLED_APPS. Only ref: `ai_core/routing.py` (which itself is never imported — `core/routing.py` is the active one). | Possibly — "Donkey Betz" branding implies sports-betting is core. Active app is `sports/`; `sports_betting/` looks like an earlier WS UI experiment that lost the wire-up race. | Document the duplicate-app split (sports/ vs sports_betting/) before any archival. Confirm with Rigby whether dormant-planned or archivable. |
| `intelligence/urls_ai_jobs.py` | BROKEN — references missing view fns | Smoke import: `AttributeError: module 'intelligence.views' has no attribute 'get_spiders'`. The 5 named views don't exist anywhere; `intelligence/views.py` uses CBVs. URL not included anywhere. | No — looks like a pre-CBV migration relic | Document, then archive. Lowest-risk archival candidate of the bunch. |
| `ml_pipeline/pipeline` (the missing module) | BROKEN GHOST | File doesn't exist. Imports in 3 files: `monitoring_dashboard.py`, `orchestration.py` (try/except), `testing_suite.py` (bare). `class MLPipeline` only in `archive/docs/*.md`. The two real classes — `EnhancedMLPipeline` and an inline `class MLPipeline` in `ai_core/intelligence/income_builder.py` — are unrelated. | Yes — `EnhancedMLPipeline` is **active** (used by `intelligent_job_matcher.py`, `learning_loop.py` fallback, `intelligence/income_builder.py`, scripts). The ghost is the **shim** that should bridge them. | Decision needed: add `MLPipeline = EnhancedMLPipeline` alias to `ml_pipeline/__init__.py` (one line) to revive the partial layer, OR mark dormant. Either way, document. |

---

## Broken but unreachable (low priority, mark before delete)

| Path | Why broken | Why low risk | Recommended next action |
|---|---|---|---|
| `core/views_neural_orchestra.py` `neural_orchestra_view` (lines 29-37) | renders missing `neural_orchestra.html` | URL was unmounted Session 871. No external importer. | Add `# DORMANT: unmounted Session 871` banner OR convert body to redirect. Low priority. |
| `core/views_content.py` `ai_image_studio` (lines 1324-1338) | renders missing `ai_image_studio.html` | Same — unmounted Session 871. No importer. | Same. |
| `core/views_diagnostics.py` `diagnostic_dashboard` (lines 546-548) | renders missing `diagnostic_dashboard.html` | Same — 70+ other handlers in this file are live. | Same. |
| `core/views_unified.py` `EditProfileView`, `SignupView` (~250-340) | render missing `unified/edit_profile.html`, `unified/signup.html` | TemplateView CBVs explicitly marked DEPRECATED in module docstring. Not imported. | Same — defensive banner. |
| `core/views_unified.py` `opportunity_detail` (line 820) | renders missing `unified/opportunity_detail.html`; signature mismatch (no `opportunity_id` kwarg) | **Not** the routed `opportunity_detail` — that one is `core.views_opportunity.opportunity_detail` (line 145, signature `(request, opportunity_id)`). The unified-module version is a name shadow with zero callers. | Same — defensive banner. Confirmed by grep: 0 importers. |

---

## Safe artifact cleanup (no runtime risk)

All verified zero-reader, zero-importer. Each is a clean untrack candidate.

| Path | Reason | Notes |
|---|---|---|
| `frontend/components/generated/{*.jsx, *.md, index.js}` (5 files) | Generated 2025-09-26. `index.js` exports identifiers with hyphens (invalid JS — would syntax-error on import). Not under `frontend/src/`. Zero importers. | Add `.gitignore` glob `frontend/components/generated/`. |
| `reports/*.json` (13 files) | All 2025-10-02 overnight test outputs. Zero readers in active code. Two writers (`verify_spiders.py`, `overnight_learning_test.py`) overwrite, never read. | `.gitignore` already has `/reports/` (Session 976) but these files were tracked before that rule. Just `git rm --cached`. |
| `frontend/nohup.out` | Captured stdout of `nohup npm run dev` or similar. No code reads it. | Untrack; matches root-level `*.log` policy intent. |
| `templates/frontend_index.html` | Orphan — zero references in any view, template loader, or include. | Untrack. |
| `templates/{agents,content,invoices}/.gitkeep` | Placeholders for template subdirs that no view uses (`agents/templates/agent_selection.html` is a different path under the `agents` Django app). | Untrack. |

---

## Needs verification before action

| Item | What to verify | How |
|---|---|---|
| `revenue/models.py` migration history | Whether the 4 models were ever in any migration anywhere | `git log -p -- revenue/`; grep migrations dirs for the model names. If they were ever migrated, dropping the file is risky. |
| `sports_betting/` migration history | Confirm `sports_betting` was never an INSTALLED_APP that produced migrations | Migration data refs (`sports_betting_nfl/nba/mlb/nhl`) in `core/migrations/0019_*` and `core/migrations/0254_*` are learning-domain enum strings — NOT Django app references. They stay regardless. |
| `agents/views_deployment*` | Whether Rigby intends to wire these up later | PA conversation. |
| `ai_core/intelligence/orchestration.py` | Whether the partial layer is being revived | Rigby. |
| Each "dormant template render" function (5 files) | Whether removing the function body breaks imports anywhere | Grep + smoke `import` test. (Already done: zero importers.) Still needs runtime smoke before archive. |
| `frontend/dist/` build hygiene | Whether build is reproducible from a clean clone | `cd frontend && rm -rf node_modules dist && npm ci && npm run build` |
| `.rag_cache.pkl` (~16 MB at root, untracked locally) | Whether anyone produces or reads it | `grep -r .rag_cache` across the repo. |
| Platform inventory freshness | After any code change | `python manage.py generate_platform_inventory` (needs DB) |

---

## Half-built but strategically important — flag for product call

These four are the ones to put in front of Rigby/Chris before any cleanup:

1. **`agents/views_deployment*` bundle** — a complete agent-deploy-to-project feature, fully implemented, just not URL-mounted. If "deploy a stack of agents to a project" is on the roadmap, this is 80% done. Verify intent before archiving.
2. **`ai_core/intelligence/orchestration.py` + the missing `ml_pipeline.pipeline` shim** — partial intelligence orchestration layer with a defensive mock fallback. One-line alias (`MLPipeline = EnhancedMLPipeline`) would revive it against real code. Worth a yes/no on revival.
3. **`revenue/revenue_verifier.py` + `revenue/models.py`** — verifier is active and security-relevant; models are broken. The pair was clearly designed together. Decide whether to complete the persistence layer or keep the verifier Redis-only.
4. **`sports_betting/` vs `sports/` duplicate-app split** — sports-betting is the brand. Knowing whether the dormant app is "future surface" or "abandoned experiment" changes the archival decision. Confirm with Rigby.

---

## Modules that look dead but may preserve compatibility

Worth checking before removal — each could be load-bearing for a
back-compat path that's not obvious from grep:

| Module | Compat-preservation hypothesis |
|---|---|
| `run_stock_financial_agents` (in `core/tasks.py`) | Already documented as a wrapper for `run_stock_audit_cycle`. Stays. |
| `revenue/models.py` 4 models | Could be referenced in old PeriodicTask names or migration string-refs. Verify before delete. |
| `sports_betting` learning-domain enum strings | Enum strings in `core/migrations/0019_*` and `core/migrations/0254_*` are independent of the `sports_betting/` directory. Removing the dir does NOT touch migration data. Safe — but still worth verifying. |
| `core.views_unified.opportunity_detail` (the shadow) | Unused, but the name collision with `core.views_opportunity.opportunity_detail` could mask future imports. Worth a comment if not removed. |
| `core/templates/index.html` | The ONLY rendered template in active routes. Do not touch. |
| `core/urls_unified.py` redirect_view bag (60+ legacy redirects) | Each preserves an old Django URL → React route redirect. Removing them breaks bookmarks and external links. Stays. |

---

## Recommended next 5 PRs (in order)

1. **PR-A — Untrack pure artifacts (lowest risk, fastest win).**
   `git rm --cached` on the 21 files in "Safe artifact cleanup" above;
   add corresponding `.gitignore` entries. Smokes: guardrails,
   `npm run build`. **Blast radius: zero.** Depends on nothing.

2. **PR-B — Defensive banners for "broken but unreachable" code (annotation-only).**
   Add a one-line `# DORMANT: unmounted Session 871, retained for archival; renders missing template`
   banner to `neural_orchestra_view`, `ai_image_studio`,
   `diagnostic_dashboard`, `EditProfileView`, `SignupView`,
   `core.views_unified.opportunity_detail`. No body changes.
   Smokes: `python manage.py check`, guardrails. **Blast radius: zero.**

3. **PR-C — Archive-candidate banners for the unambiguously dead.**
   Add a single-line `# ARCHIVE-CANDIDATE: not mounted, not installed (Session 1111 review)`
   to `intelligence/urls_ai_jobs.py`,
   `ai_core/intelligence/{monitoring_dashboard,testing_suite}.py`.
   Update `docs/audit/CLEANUP_PLAN.md` Phase 2 with these specific paths.
   **Blast radius: zero.**

4. **PR-D — Document the active-but-undocumented modules.**
   New `docs/topics/` entries (or appendices in existing topic docs)
   for: `revenue/revenue_verifier.py`, `advisors/`, top-level `llm/`,
   `core/tasks_*.py` indirection pattern, `core/urls.py` vs
   `urls_unified.py` split. Regenerate `docs/INDEX.md` via
   `build_docs_index`. Smokes: guardrails,
   `verify_doc_claims --only-drift`. **Blast radius: docs only.**

5. **PR-E — Decision PRs (one of three; needs Rigby first).**
   Pick one of: (a) revive `ml_pipeline.pipeline` shim with
   `MLPipeline = EnhancedMLPipeline` alias, (b) wire
   `agents/urls_deployment.py` into `core/urls.py`, (c) rehome
   `revenue/models.py`. Each needs product input before code.
   **Blast radius: medium — first time the partial systems get a verdict.**

PR-A and PR-B are independent and can ship in either order. PR-C
depends on the partial-system Rigby calls being deferred (i.e., we
accept these three are dormant). PR-D depends on nothing. PR-E is
gated by Rigby.

---

## Source-of-truth pointers

- Canonical cleanup plan: [`docs/audit/CLEANUP_PLAN.md`](../audit/CLEANUP_PLAN.md)
- Audit workspace index: [`docs/AUDIT_INDEX.md`](../AUDIT_INDEX.md)
- Runtime inventory: [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md)
- Narrative anchor: [`docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md)

This handoff is a **deeper-review companion** to those docs, not a
duplicate audit plan. When PR-A through PR-E land, they should update
`docs/audit/CLEANUP_PLAN.md` rather than this file.
