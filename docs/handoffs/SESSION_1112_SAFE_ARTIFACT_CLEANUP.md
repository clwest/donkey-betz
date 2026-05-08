---
title: "Session 1112 — safe artifact cleanup (PR-A from Session 1111 queue)"
date: 2026-05-08
status: active
session: 1112
previous_handoff: SESSION_1111_DEEPER_REVIEW_MAP.md
---

# Session 1112 — safe artifact cleanup

## TL;DR

- **Executed PR-A from the Session 1111 deeper-review queue.** Untracked 23
  verified zero-reader / zero-importer artifact files across five paths.
- **No deletions on disk.** All untracked files preserved locally where
  practical so writers can keep regenerating them.
- `.gitignore` extended with three new rules covering the previously-uncovered
  artifact paths. The other four targeted paths were already matched by
  pre-existing rules (`nohup.out`, `/reports/`).
- **Touched zero forbidden paths.** `agents/urls_deployment.py`, `revenue/`,
  `sports_betting/`, `ai_core/intelligence/*`, `ml_pipeline/`,
  `BACKEND_INVENTORY.md`, `PLATFORM_INVENTORY.md`, and the docker subnet
  stash (`stash@{0}`) are all unchanged.

**HEAD before:** `3f03a147` (clean main).
**Branch:** `chore/untrack-safe-artifacts`.

---

## What changed

### Untracked artifacts (23 files, `git rm --cached` only)

| Path | Files | Reason |
|---|---|---|
| `frontend/components/generated/` | 5 (`.jsx`, `_INTEGRATION.md`, `index.js`) | Generator output for `ai_core/intelligence/proposal_manager.py`. The proposal_manager **writes** into this directory at runtime; no code reads the existing tracked files. `index.js` exports identifiers with hyphens (invalid JS — would syntax-error on import). |
| `reports/*.json` | 13 | 2025-10-02 overnight test outputs. Writers (`scripts/verify_spiders.py`, `scripts/overnight_learning_test.py`, `scripts/one-off/quick_spider_test.py`, `scripts/one-off/activate_spiders.py`, `scripts/websocket_diagnostics_full.py`, `core/management/commands/test_agent_scenarios.py`) overwrite these JSONs but never read them. `/reports/` was already in `.gitignore` (line 311); the existing files predated the rule. |
| `frontend/nohup.out` | 1 | Captured stdout of `nohup npm run dev` or similar. No code reads it. Already covered by `nohup.out` rule (line 82). |
| `templates/frontend_index.html` | 1 | Orphan. `core/settings.py` `TEMPLATES['DIRS']` only loads `frontend/dist`, `ai_core/templates`, `core/templates` — not the root `templates/`. Zero references in any view, template loader, or include (Session 1111 audit confirmed). |
| `templates/{agents,content,invoices}/.gitkeep` | 3 | Placeholders for template subdirs that no view uses. The active `agents` Django app's templates live under `agents/templates/`, not here. |

**Total: 23 files, all blast-radius zero.**

> Note: Session 1111 PR-A recommendation said "21 files" — that was an
> arithmetic error in the recommendation line. The actual table in
> Session 1111 listed 5 + 13 + 1 + 1 + 3 = **23** files, which is what
> shipped here.

### `.gitignore` additions

Three new rules at the bottom of `.gitignore`:

```
# Session 1112: untrack safe generated artifacts
# Generator output dir for ai_core/intelligence/proposal_manager.py — written
# at runtime, not source. Local copies preserved; not tracked in git.
frontend/components/generated/

# Orphan template stubs at repo root. Django TEMPLATES DIRS does not include
# this directory (see core/settings.py: only frontend/dist, ai_core/templates,
# core/templates are loaded). Session 1111 audit confirmed zero references.
/templates/frontend_index.html
/templates/agents/
/templates/content/
/templates/invoices/
```

The `nohup.out` and `/reports/` rules pre-existed and continue to cover
the relevant files; `git check-ignore -v` confirmed every untracked path
is now ignored.

---

## Verification

### Pre-commit baseline (clean main, HEAD `3f03a147`)

```
python scripts/verify_repo_guardrails.py --inventory-advisory
  → 0 blocking, 4 DOC_ONLY (advisory), 2 VERIFIED, exit 0
context-kit verify --json
  → CONFLICT: 0, VERIFIED: 2, DOC_ONLY: 4
```

### Post-change

```
git ls-files frontend/components/generated/   →   (empty)
git ls-files reports/                          →   (empty)
git ls-files frontend/nohup.out                →   (empty)
git ls-files templates/                        →   (empty)

git check-ignore -v <every untracked path>     →   matched (.gitignore line):
  frontend/components/generated/index.js   → .gitignore:384  frontend/components/generated/
  frontend/nohup.out                       → .gitignore:82   nohup.out
  reports/spider_results.json              → .gitignore:311  /reports/
  templates/frontend_index.html            → .gitignore:389  /templates/frontend_index.html
  templates/agents/.gitkeep                → .gitignore:390  /templates/agents/
  templates/content/.gitkeep               → .gitignore:391  /templates/content/
  templates/invoices/.gitkeep              → .gitignore:392  /templates/invoices/
```

Guardrails after the change reported the same envelope: 0 blocking,
4 DOC_ONLY (advisory), 2 VERIFIED, exit 0. No new tracked-generated-paths
findings. `context-kit verify --json` still reports `CONFLICT: 0`.

### Frontend build

`frontend/components/generated/` is **not** under `frontend/src/` and is
not imported by any module in the build graph (`tsconfig`/`vite.config`
roots target `src/`). Untracking it does not affect the Vite build —
local files were preserved, so even direct path references would still
resolve at build time. Build smoke deferred to PR review unless
reviewer requests.

### Stash

`stash@{0}` (docker subnet override 172.20→172.21) untouched. `git stash list`
matches the pre-session output exactly.

---

## What was deliberately not touched

Per session scope:

- `agents/urls_deployment.py` (Session 1111 partial-system, needs Rigby call)
- `revenue/` (active verifier + broken models — needs product call)
- `sports_betting/` (duplicate-app split — needs product call)
- `ai_core/intelligence/*` (`orchestration.py`, `monitoring_dashboard.py`,
  `testing_suite.py` — needs Rigby call on revival vs archive)
- `ml_pipeline/` (the missing `MLPipeline` shim decision)
- `BACKEND_INVENTORY.md` and `docs/PLATFORM_INVENTORY.md`
- Docker subnet stash (`stash@{0}`)

These remain on the deeper-review queue. PR-B (defensive banners for
broken-but-unreachable views) and PR-C (archive-candidate banners) from
the Session 1111 queue are still pending and unaffected by this PR.

---

## Local file preservation

`git rm --cached` was used in every case. All local files remain on
disk:

- `frontend/components/generated/` — 5 files still present
- `reports/` — 13 JSONs plus other writer-produced artifacts still present
- `frontend/nohup.out` — preserved
- `templates/frontend_index.html` — preserved
- `templates/{agents,content,invoices}/.gitkeep` — preserved

Writers (`proposal_manager.py`, the spider/test scripts) continue to work
unchanged; their output now lands in ignored locations instead of being
auto-staged.

---

## Source-of-truth pointers

- Source plan: [`SESSION_1111_DEEPER_REVIEW_MAP.md`](SESSION_1111_DEEPER_REVIEW_MAP.md)
  (PR-A row, "Safe artifact cleanup" table)
- Cleanup workspace: [`docs/audit/CLEANUP_PLAN.md`](../audit/CLEANUP_PLAN.md)
- Runtime inventory: [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md)
- Narrative anchor: [`docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md)
