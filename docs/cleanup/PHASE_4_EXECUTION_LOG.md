---
title: "Root Cleanup — Phase 4 Execution Log"
status: complete
date: 2026-04-20
related_plan: ROOT_CLEANUP_PLAN.md
previous_log: PHASE_3_EXECUTION_LOG.md
---

# Phase 4 Execution Log — Directory Audit

Phase 4.2 of `ROOT_CLEANUP_PLAN.md`. Audited all ~90 top-level directories, identified 21 orphans (tracked content with zero imports from production code), and archived them to `archive/orphaned_dirs_2026-04-20/`. Caught and fixed three Django URL `include()` dependencies my initial grep missed.

**Date:** 2026-04-20
**Branch:** `chore/cleanup-phase-4-dir-audit`
**Scope:** Phase 4.2 (the dir audit). Phase 4.1 (higher-risk scripts) was resolved in Phase 3.8.

## Summary

**Before Phase 4:** 90 top-level directories.
**After Phase 4:** 69 top-level directories (21 archived, 40 have tracked content from a fresh-clone perspective).

## Methodology

For each of 90 top-level dirs:

1. **Tracked file count** via `git ls-files <dir>`
2. **Import scan** — `grep -rE "(from\s+${d}\.|from\s+${d}\s+import|^import\s+${d}\b)"` across `core/`, `ai_core/`, `services/`, `tools/`, `frontend/`
3. **Frontend refs** — `grep -rE "['\"]\./${d}/|from\s+['\"]${d}"` across `frontend/`
4. **Django config** — check `core/settings.py` `INSTALLED_APPS`
5. **Build config** — check `Makefile`, `Procfile`, `docker-compose*.yml`, `entrypoint.sh`
6. **⚠ GAP in initial scan:** Did NOT check Django URL `include()` patterns. This caught 3 false-orphan classifications (ai_platform, backend, revenue). See "Lessons learned" below.

## Dirs KEPT at root (all verified active)

### Django INSTALLED_APPS (17 apps)

`core, agents, coleadership, rendering, pipelines, ai_core, intelligence, ml, sports, content, persistence, self_awareness, style_memory, dashboard, workflows, mythology, ai_opportunities`

Plus sub-apps referenced via dotted paths: `ai_core.spiders`, `ai_core.intelligence`, `core.learning_bridges`.

### Actively imported (not in INSTALLED_APPS but used)

| Dir | Usage |
|---|---|
| `advisors` | 27 Python imports from production code |
| `ai_nexus` | `from ai_nexus.memory import AIMemorySystem`, `from ai_nexus.revenue_detector` |
| `llm` | `from llm.base import ChatMessage`, `from llm import router` |
| `ml_pipeline` | `from ml_pipeline.pipeline import MLPipeline` |
| `sports_betting` | `ai_core/routing.py` WebSocket consumer |
| `ai_platform` | `core/urls.py:3179` via `include('ai_platform.urls')` — **caught after initial archive attempt** |
| `backend` | `core/urls.py:3616, 4046` via `include('backend.auto_endpoints.urls')` — **caught after initial archive attempt** |
| `revenue` | `ai_platform/views.py:1` — `from revenue.revenue_verifier import RevenueRealityVerifier` — **caught transitively** |

### Infrastructure / runtime

`docs, scripts, tests, frontend, mobile, resolve_node, archive, external-project-docs, venv_ml, config, templates, tools, logs, reports, audits, temp, static, staticfiles, media, backups, secrets, cache`

### Gitignored-only (exist locally, not in repo)

`_archived, analysis, assistant, blockchain, campaigns, development, diversity, execution, executive, financial, generated_content, income_builder_outputs, ml_models, models, narrative, norman-handyman-mvp, podcast, predictions, security, series, strategy, summaries`

These have 0 tracked files each; their local contents are .gitignored. They don't affect a fresh clone and don't need repo-level action. Listed here for completeness.

## Dirs ARCHIVED → `archive/orphaned_dirs_2026-04-20/`

### Batch A — Small orphans (14 dirs, ≤3 tracked files each)

`ai_platform`, `avatars`, `blender_tests`, `executor_repos`, `generated_docs`, `ml_intelligence`, `odds_calc`, `pgvector_local_repo`, `research`, `revenue`, `revenue_data`, `review`, `src`, `system`

⚠ `ai_platform` and `revenue` subsequently restored (see "Restored" section below).

### Batch B — Medium orphans (5 dirs, 9–17 tracked files)

| Dir | Files | Notes |
|---|---|---|
| `real_freelance_deliverables` | 9 | Old output artifacts |
| `services` (root) | 9 | Contains `obs_bridge/`. Real services live in `core/services/`. |
| `proposals_output` | 10 | Old proposal output artifacts |
| `backend` | 10 | Pre-Django experimental backend — **subsequently restored** |
| `real_job_deliverables` | 17 | Output dir; agent self-creates via `os.makedirs(exist_ok=True)` |

### Batch C — Larger orphans (5 dirs, 7–93 tracked files)

| Dir | Files | Notes |
|---|---|---|
| `_future_projects` | 15 | Roadmap stubs, nothing live |
| `spider_configs` | 16 | Orphan config set, not loaded by current spider registry |
| `davinci_bridge` | 7 | Old impl; now replaced by `resolve_node/`. Makefile's `davinci-bridge` target is a make target NAME (not a dir ref) |
| `generated_projects` | 93 | Historical AI-generated projects. `related_name='generated_projects'` in Django models = query hint, no filesystem dependency |
| `ai_generated_projects` | 83 | Historical. `core/views_ecosystem.py` has hardcoded absolute paths — already broken for anyone not on Chris's machine. `core/services/proper_agent_executor.py` writes to `ai_generated_projects/{name}/` — will self-create if run |

### Restored (false orphans — caught by pytest regression)

Three dirs were initially archived then restored after `pytest --collect-only` surfaced a `ModuleNotFoundError`.

| Dir | Reason for restore |
|---|---|
| `ai_platform` | `core/urls.py` does `include('ai_platform.urls')` — string-based Django include, not a `from X import` |
| `backend` | `core/urls.py` does `include('backend.auto_endpoints.urls')` — same pattern |
| `revenue` | `ai_platform/views.py` does `from revenue.revenue_verifier import ...` — transitively needed once `ai_platform` was restored |

**Net archived: 21 dirs** (24 moved − 3 restored).

## Lessons learned

1. **Django `include()` is a string-based dep** that doesn't show up in `from X import` grep. Any dir audit must also grep `include(['"]<dirname>`.
2. **Transitive dependencies cascade** — restoring `ai_platform` exposed its dependency on `revenue`. Run pytest after each batch of moves to catch these iteratively.
3. **Gitignored "empty" dirs are harmless** — ~22 dirs showed 0 tracked files. These are local-only runtime dirs (generated_content, backups, etc.). They don't appear in a fresh clone, so no repo action needed.

## Verification

| Check | Pre-Phase-4 | Post-Phase-4 |
|---|---|---|
| `pytest --collect-only` tests | 766 | 766 ✅ |
| `pytest --collect-only` errors | 1 (pre-existing `test_verbosity_fix.py`) | 1 (same pre-existing) ✅ |
| Top-level dir count | 90 | 69 |
| Dirs with tracked content (fresh-clone view) | ~60 | 40 ✅ |
| `git log --follow <moved-file>` works across rename | — | ✅ |

## Root state after Phase 4

A fresh `git clone` now sees 40 top-level directories with clear purposes:

- **App code (17 Django apps + 5 helpers):** core, agents, coleadership, rendering, pipelines, ai_core, intelligence, ml, sports, content, persistence, self_awareness, style_memory, dashboard, workflows, mythology, ai_opportunities, advisors, ai_nexus, llm, ml_pipeline, sports_betting, ai_platform, backend, revenue
- **Infrastructure:** docs, scripts, tests, config, templates, tools, resolve_node, frontend, mobile
- **Archives/outputs/external:** archive, external-project-docs, audits, reports

That's it. No mystery dirs. Anyone cloning can match each top-level dir to a purpose in ~5 minutes.

## Rollback

`git revert <merge-sha>`. All archived dirs are preserved at `archive/orphaned_dirs_2026-04-20/<dir>` — if any turns out to still be needed, `git mv archive/orphaned_dirs_2026-04-20/<dir> ./<dir>` restores it with history intact.

## What's NOT done in Phase 4

- **Local gitignored dir cleanup** — the 22 "empty" dirs that exist only locally. Purely cosmetic; doesn't affect repo state or collaborators.
- **Documentation sweep** — CLAUDE.md and docs/topics/ may reference old dir names in prose (not imports). Left as-is; future docs sessions can update.
- **Docker-compose consolidation** — 4 compose variants at root. All legit, per Phase 3 analysis.

## Related

- Plan: [`ROOT_CLEANUP_PLAN.md`](ROOT_CLEANUP_PLAN.md)
- Phase 1: [`PHASE_1_EXECUTION_LOG.md`](PHASE_1_EXECUTION_LOG.md)
- Phase 2: [`PHASE_2_EXECUTION_LOG.md`](PHASE_2_EXECUTION_LOG.md)
- Phase 3: [`PHASE_3_EXECUTION_LOG.md`](PHASE_3_EXECUTION_LOG.md)
- Token cleanup: [`TOKEN_ROTATION_PLAYBOOK.md`](TOKEN_ROTATION_PLAYBOOK.md)
