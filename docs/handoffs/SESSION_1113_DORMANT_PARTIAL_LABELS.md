---
title: "Session 1113 — dormant / partial / broken-but-unreachable labels"
date: 2026-05-08
status: active
session: 1113
previous_handoff: SESSION_1112_SAFE_ARTIFACT_CLEANUP.md
---

# Session 1113 — dormant / partial / broken-but-unreachable labels

## TL;DR

- **Annotation-only.** Labels added to 13 files, comment-only in every
  case. No runtime behavior change, no deletions, no archival moves,
  no untracking, no route wiring, no model migrations.
- Implements PR-B (defensive banners) and PR-C (archive-candidate
  banners) of the Session 1111 deeper-review queue, plus the documenting
  half of PR-E (the partial-system decision PRs that still need a Rigby
  call). The decisions themselves remain pending — banners simply make
  the classification durable so the next contributor doesn't re-run the
  audit.
- Smoke imports for every banner-touched module match the classifications
  exactly: PARTIAL / note / archive-candidate modules import cleanly,
  BROKEN-BUT-UNREACHABLE modules fail with the exact errors documented
  in the banner text, ACTIVE-COMPANION-PARTIAL raises the documented
  `RuntimeError`.

**HEAD before:** `9a6950f0` (clean main, post-PR #2064 squash).
**Branch:** `docs/label-dormant-partial-systems`.

---

## Classification language

| Label | Meaning |
|---|---|
| **PARTIAL** | Built but not mounted; needs a product decision before wiring or archiving. |
| **ARCHIVE-CANDIDATE** | Not mounted / not installed; preserve until product decision. |
| **BROKEN-BUT-UNREACHABLE** | Import or template path broken, but no active runtime caller found. |
| **ACTIVE-COMPANION-PARTIAL** | Paired with an active runtime helper, but the persistence / model layer is not wired. |

---

## Files touched (13)

### PARTIAL — agent-deploy bundle (6 files)

These six form a complete "deploy a stack of agents to a project"
feature. The URLConf is fully populated and every view is implemented,
but `agents/urls_deployment.py` is never `include()`-d from any active
URLConf — so all routes are dark.

- `agents/urls_deployment.py`
- `agents/views_deployment.py`
- `agents/views_deployment_execute.py`
- `agents/views_deployment_execute_improved.py` *(also referenced by
  `tests/spiders/test_agent_modes.py` — only external consumer)*
- `agents/views_all_agents.py`
- `agents/views_all_agents_simple.py`

**Decision pending:** wire into `core/urls.py` or treat as dormant
(PR-E in the Session 1111 queue).

### ARCHIVE-CANDIDATE — sports_betting/ app

`sports_betting/__init__.py` (previously empty) now carries a banner
explaining:

- App is **not** in `core.settings.INSTALLED_APPS`.
- The only external importer is `ai_core/routing.py:8`, which is itself
  inactive — `core/asgi.py` uses `core.routing.websocket_urlpatterns`,
  not `ai_core.routing`.
- `models.py` is empty stub, `views.py` returns hardcoded mock data, no
  migrations exist.
- `sports_betting_*` strings in `core/migrations/0019_*` and
  `core/migrations/0254_*` are learning-domain enum values, **not**
  Django app references — independent of this directory.

**Decision pending:** future surface to revive, or abandoned experiment
to archive.

### BROKEN-BUT-UNREACHABLE (3 files)

Each fails at import time, but no active code imports them. Smoke
imports confirm the documented failure modes.

| File | Failure mode |
|---|---|
| `intelligence/urls_ai_jobs.py` | `AttributeError: module 'intelligence.views' has no attribute 'get_spiders'` (5 view fns missing — pre-CBV migration relic) |
| `ai_core/intelligence/monitoring_dashboard.py` | `ModuleNotFoundError: No module named 'orchestration'` (bare top-level import) |
| `ai_core/intelligence/testing_suite.py` | Same `ModuleNotFoundError: orchestration` |

**Decision pending:** archive once the deeper-review queue confirms no
revival path.

### ACTIVE-COMPANION-PARTIAL — revenue/models.py

Pairs with the active `revenue/revenue_verifier.py:RevenueRealityVerifier`,
but the persistence layer was never wired:

- `revenue` is **not** in `core.settings.INSTALLED_APPS`.
- Models lack `app_label` in Meta and the app has no `apps.py`, so
  importing the module raises:
  ```
  RuntimeError: Model class revenue.models.<X> doesn't declare an
  explicit app_label and isn't in an application in INSTALLED_APPS.
  ```
- No migrations were ever produced; zero importers.

**Decision pending:** rehome the 4 models in a real installed app
(`core/models_revenue.py` is one option) and run migrations, OR delete
the file and accept the verifier as Redis-only. The verifier itself is
security-relevant, so the companion stays preserved until that call.

### PARTIAL — ai_core/intelligence/orchestration.py

Has a `try/except ImportError` defensive fallback to `MockMLPipeline`
because the real `ml_pipeline.pipeline.MLPipeline` import always fails
(the submodule doesn't exist). The only importer in the entire repo is
`archive/scripts/verify_llm_integration.py`, and the active learning
loop bypasses this orchestrator.

**Decision pending:** revive with a one-line shim
(`MLPipeline = EnhancedMLPipeline` in `ml_pipeline/__init__.py`) or
mark dormant alongside `monitoring_dashboard.py` and `testing_suite.py`.

### Note — ml_pipeline/__init__.py

Pure documentation. The package only exports `EnhancedMLPipeline`; there
is no `ml_pipeline.pipeline` submodule. Three `ai_core/intelligence/*`
modules expect `MLPipeline` to live there. The banner names them and
documents the one-line shim that would unblock revival.

---

## What was deliberately not changed

- No imports added or removed.
- No view function bodies altered.
- No URLs included or removed.
- No `apps.py` / `INSTALLED_APPS` entries added.
- No model migrations produced.
- `frontend/`, `core/services/`, `core/urls*.py`, and every active
  runtime module are untouched.
- Forbidden paths from the session brief (
  `revenue/revenue_verifier.py`, `ai_core/intelligence/learning_loop.py`,
  `ml_pipeline/enhanced_ml_pipeline.py`, `BACKEND_INVENTORY.md`,
  `PLATFORM_INVENTORY.md`, docker subnet stash) are all unchanged.

---

## Verification

| Check | Result |
|---|---|
| `python manage.py check` | `System check identified no issues (0 silenced)` ✓ |
| Smoke import — `agents.urls_deployment` | OK ✓ |
| Smoke import — `agents.views_deployment` | OK ✓ |
| Smoke import — `agents.views_deployment_execute` | OK ✓ |
| Smoke import — `agents.views_deployment_execute_improved` | OK ✓ |
| Smoke import — `agents.views_all_agents` | OK ✓ |
| Smoke import — `agents.views_all_agents_simple` | OK ✓ |
| Smoke import — `intelligence.urls_ai_jobs` | FAIL `AttributeError: ... 'get_spiders'` (matches banner) ✓ |
| Smoke import — `ai_core.intelligence.monitoring_dashboard` | FAIL `ModuleNotFoundError: orchestration` (matches banner) ✓ |
| Smoke import — `ai_core.intelligence.testing_suite` | FAIL `ModuleNotFoundError: orchestration` (matches banner) ✓ |
| Smoke import — `ai_core.intelligence.orchestration` | OK ✓ |
| Smoke import — `revenue.models` | FAIL `RuntimeError: ... doesn't declare an explicit app_label` (matches banner) ✓ |
| Smoke import — `ml_pipeline` | OK ✓ |
| Smoke import — `sports_betting` | OK ✓ |
| `python scripts/verify_repo_guardrails.py --inventory-advisory` | 0 blocking, 4 DOC_ONLY (advisory), 2 VERIFIED ✓ |
| `context-kit verify --json` | CONFLICT 0 (unchanged) ✓ |
| Pre-commit hook | passed ✓ |

---

## What's next

PR-D from the Session 1111 queue (documenting the active-but-undocumented
modules — `revenue/revenue_verifier.py`, `advisors/`, top-level `llm/`,
`core/tasks_*.py` indirection, `core/urls.py` vs `urls_unified.py`) is
unblocked and independent of any of the partial-system Rigby calls.

PR-E (the actual decisions: revive `ml_pipeline.pipeline` shim, wire
`agents/urls_deployment.py`, rehome `revenue/models.py`) remains gated
on Rigby.

---

## Source-of-truth pointers

- Source plan: [`SESSION_1111_DEEPER_REVIEW_MAP.md`](SESSION_1111_DEEPER_REVIEW_MAP.md)
- Cleanup plan: [`docs/audit/CLEANUP_PLAN.md`](../audit/CLEANUP_PLAN.md)
  (Phase 6 added in this session)
- Runtime inventory: [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md)
- Narrative anchor: [`docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md)
