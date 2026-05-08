---
title: "Session 1114 — active module ownership map (PR-D from Session 1111 queue)"
date: 2026-05-08
status: active
session: 1114
previous_handoff: SESSION_1113_DORMANT_PARTIAL_LABELS.md
---

# Session 1114 — active module ownership map

## TL;DR

- **Docs-only.** No code changes. Closes PR-D from the
  [Session 1111 deeper-review queue](SESSION_1111_DEEPER_REVIEW_MAP.md).
- New topic file
  [`docs/topics/active-module-ownership-map.md`](../topics/active-module-ownership-map.md)
  documents the five active-but-underdocumented runtime modules
  Session 1111 flagged as needing a `docs/topics/*.md` entry.
- Two Session 1111 claims **corrected** by this pass:
  1. `advisors/` is **not** a namespace package — `advisors/__init__.py`
     exists (5 LOC docstring).
  2. `core/urls.py` is the 4,750-line monolith **and** the entrypoint;
     `core/urls_unified.py` is the 118-line redirect helper. Session
     1111's PR-D row had these swapped.
- `docs/topics/README.md` updated with a new row pointing at the file
  so the embedding pipeline picks it up.

**HEAD before:** `ed297242` (clean main, post-Session 1113 squash).
**Branch:** `docs/active-module-ownership-map`.

---

## What the new topic doc covers

[`docs/topics/active-module-ownership-map.md`](../topics/active-module-ownership-map.md)
runs through five subsystems where the file layout makes it hard to
tell active code apart from dormant or duplicate code by inspection
alone. Each section names the active path, where it actually runs,
and the most-confused look-alike.

### §1 — `revenue/revenue_verifier.py`

- Active 456-LOC class `RevenueRealityVerifier`.
- Imported and **instantiated at module load** by `ai_platform/views.py:15-22`.
- `ai_platform.urls` is included at the root from
  `core/urls.py:3179` (`path('', include('ai_platform.urls'))`), so
  the verifier runs on every web boot.
- Talks to Redis on **DB 3** (dedicated, not the default DB 0); reads
  `REDIS_HOST` / `REDIS_PORT` from settings.
- **Failure semantics:** every Redis op is wrapped in
  `try/except Exception` that logs and returns `False` (or proceeds).
  Closer to *fail-silent* than fail-open in the strict sense — caller
  decides what to do with `False`.
- **Companion:** `revenue/models.py` is `ACTIVE-COMPANION-PARTIAL`
  (Session 1113). The persistence layer was drafted but never wired —
  no migrations, missing `app_label`, app not in `INSTALLED_APPS`.
  The verifier is Redis-only by design today.

### §2 — `advisors/`

- 1,641 LOC across `__init__.py` (5), `registry.py` (935),
  `llm_advisor_system.py` (701).
- **Real package**, not a namespace package — corrects the Session 1111
  audit row.
- `advisor_registry = get_advisor_registry()` module-level singleton
  at `advisors/registry.py:936`.
- 16+ active importers enumerated: PA modules, opportunity analyzer,
  audit coordinators, action plan tools, `core/services/advisor_context_builder.py`,
  agent wiring, integration tests.
- Doc warns: don't fold under `core/services/` — too many absolute
  imports would break without a shim.

### §3 — Top-level `llm/`

- ~52 LOC across `base.py` (14), `ollama_provider.py` (26),
  `router.py` (12); empty `__init__.py`.
- Imported by exactly two view modules: `core/views/main.py:1438-1439`
  and `core/views.py:1607-1608`.
- This is a **direct-Ollama chat helper**, not the production routing
  layer. Doc enumerates the four `core/services/*` modules that
  comprise the production layer:
  - `core/services/agent_llm_router.py` (697 LOC routing)
  - `core/services/llm_provider_registry.py` (`LLMProviderRegistry`)
  - `core/services/llm_call_wrapper.py` (`llm_call_span()`)
  - `core/services/universal_llm_executor.py`
- Rule of thumb captured: views can use `llm/` for one-shot direct
  chats; agents and Celery tasks must go through `core/services/`
  routers so telemetry + provider failover work.

### §4 — `core/tasks_*.py`

- 12 implementation modules totaling ~31,766 LOC behind
  `core/tasks.py` (12,575 LOC). Full LOC table in the doc.
- **Only `core.tasks_agents` is explicitly in `app.conf.imports`**
  (`core/celery.py:317`). The other 11 modules are loaded lazily via
  `_impl_*` imports inside wrapper Celery tasks defined in
  `core/tasks.py`.
- Pattern documented with a real example: a `@shared_task` wrapper in
  `core/tasks.py` does `from core.tasks_<X> import _impl_<name>` and
  delegates. This keeps the Celery autodiscover surface narrow
  (`tasks.py` only) while the heavy code is paged in lazily.
- Reading guide: don't assume a `tasks_<X>.py` module is dormant just
  because it's not in `app.conf.imports`. Search `core/tasks.py` for
  `_impl_<name>` to find the wrapper that loads it.

### §5 — `core/urls.py` vs `core/urls_unified.py`

- **Corrects Session 1111's PR-D row, which had the relationship
  inverted.** Actual line counts and roles:
  - `core/urls.py` = 4,750 LOC, 1,759 path()/include() — entrypoint
    AND the big monolith. `ROOT_URLCONF = 'core.urls'`.
  - `core/urls_unified.py` = 118 LOC, 44 path() — small redirect
    helper that maps legacy Django URL names to React routes.
    Included from `core/urls.py:1559` via
    `path('', include('core.urls_unified'))`.
- Doc captures the inclusion chain at lines 1559 (urls_unified),
  1745 (urls_provenance), 1751 (urls_real_data).
- Calls out that the split is **historical, not architectural** — it
  was carved out during Session 688's React migration for
  redirect-helper reasons. The 60+ legacy redirects Session 1111
  describes correctly live in `urls_unified.py`.

---

## What was deliberately not changed

- No code edits anywhere.
- No file deletions, archival moves, or untrack operations.
- No banners added (Session 1113 already labelled the *dormant*
  siblings; this doc is for the *active* counterparts).
- Forbidden / out-of-scope paths from the Session 1111 review remain
  untouched: `ai_core/intelligence/learning_loop.py`,
  `ml_pipeline/enhanced_ml_pipeline.py`, `BACKEND_INVENTORY.md`,
  `docs/PLATFORM_INVENTORY.md`, docker subnet stash.

---

## Verification

| Check | Result |
|---|---|
| `python scripts/verify_repo_guardrails.py --inventory-advisory` | 0 blocking, 4 DOC_ONLY (advisory), 2 VERIFIED, exit 0 (same envelope as clean-main baseline) ✓ |
| `context-kit verify --json` | CONFLICT 0 (unchanged) ✓ |
| `python manage.py build_docs_index` | regenerates `docs/INDEX.md` with the new topic file picked up alongside the rest |
| Pre-commit hook | passed ✓ |

`build_docs_index` regenerates `docs/INDEX.md` from the docs tree.
Since the new topic file lives under `docs/topics/`, the indexer picks
it up automatically; the only manual update required was the
`docs/topics/README.md` table row.

---

## Files changed

- `docs/topics/active-module-ownership-map.md` — **new**, ~310 lines
  of documentation across the five subsystems.
- `docs/topics/README.md` — added the new row to the topics table.
- `docs/audit/CLEANUP_PLAN.md` — new **Phase 7** section marks PR-D
  complete with a per-subsystem map.
- `docs/INDEX.md` — regenerated by `build_docs_index` (DOC-AUTOGEN file).
- `00-START-NEXT-SESSION.md` — pointer to Session 1114 handoff;
  PR-D status updated.
- `docs/handoffs/CURRENT.md` — latest = 1114, previous = 1113.
- `docs/handoffs/SESSION_1114_ACTIVE_MODULE_OWNERSHIP_MAP.md` —
  this handoff.

---

## What's next

PR-E remains the only unfinished item from the Session 1111 queue
and is **Rigby-gated** — three connected decisions:

1. Revive `ml_pipeline.pipeline` by adding
   `MLPipeline = EnhancedMLPipeline` (one-line shim) so the partial
   `ai_core/intelligence/orchestration.py` runs against real code,
   OR mark the orchestrator dormant alongside `monitoring_dashboard.py`
   and `testing_suite.py`.
2. Wire `agents/urls_deployment.py` into `core/urls.py` (the
   "deploy a stack of agents to a project" feature is ~80% done) OR
   archive the bundle.
3. Rehome `revenue/models.py` into a real installed app and run
   migrations OR delete and accept the verifier as Redis-only.

Each needs a product call before code. The decisions are explicitly
**not** required to get value from PR-D — anyone reading the new
topic doc gets the active-module map regardless of how PR-E lands.

---

## Source-of-truth pointers

- Source plan: [`SESSION_1111_DEEPER_REVIEW_MAP.md`](SESSION_1111_DEEPER_REVIEW_MAP.md)
- New doc: [`docs/topics/active-module-ownership-map.md`](../topics/active-module-ownership-map.md)
- Cleanup workspace: [`docs/audit/CLEANUP_PLAN.md`](../audit/CLEANUP_PLAN.md)
- Runtime inventory: [`PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md)
- Narrative anchor: [`PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md)
