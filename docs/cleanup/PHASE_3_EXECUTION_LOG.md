---
title: "Root Cleanup — Phase 3 Execution Log"
status: complete
date: 2026-04-20
related_plan: ROOT_CLEANUP_PLAN.md
previous_log: PHASE_2_EXECUTION_LOG.md
---

# Phase 3 Execution Log — One-Off Maintenance Scripts

Phase 3 of `ROOT_CLEANUP_PLAN.md`. Moved 59 one-off scripts from the repo root into scoped `scripts/` sub-directories. Also handled two Phase-4-flagged scripts (`run_discord_bot.py`, `audit_system.py`, `rag_docs.py`) after quick pre-flight investigations confirmed they were safe. Also resolved investigation I5 (`spreadspoke.R`).

**Date:** 2026-04-20
**Branch:** `chore/cleanup-phase-3-oneoff-scripts`
**Scope:** Phases 3.1–3.8 + bonus + I5

## Summary

| Sub-phase | Category | Files | Source | Destination |
|---|---|---|---|---|
| 3.1 | Backfill scripts | 4 | root `backfill_*.py` | `scripts/backfills/` |
| 3.2 | Fix scripts | 13 | root `fix_*.{py,sh}` | `scripts/fixes/` |
| 3.3 | Check scripts | 6 | root `check_*.py` | `scripts/checks/` |
| 3.4 | Verify scripts | 6 | root `verify_*.py` | `scripts/verify/` |
| 3.5 | Diagnose scripts | 4 | root `diagnose_*.py` | `scripts/diagnose/` |
| 3.6 | Cleanup scripts | 4 | root `cleanup_*.py` + `clean_workspace.py` | `scripts/cleanup/` |
| 3.7 | Registration scripts | 3 | root `register_*.py` | `scripts/registrations/` |
| 3.8 | Misc one-offs | 19 | various | `scripts/one-off/` |
| bonus | Backup file (gitignored) | 1 | `00-START-NEXT-SESSION.md.backup` | `docs/archive/session_notes/` (local mv only) |
| I5 | Orphan R script | 1 | `spreadspoke.R` | `archive/early_experiments/` |

**Total moves:** 60 tracked files via `git mv` + 1 untracked local `mv`.

**Root file count progression:**

| Checkpoint | Root files |
|---|---|
| Pre-cleanup | 338 entries |
| After Phase 1 | 172 files |
| After Phase 2 | 80 files |
| **After Phase 3** | **19 files** |
| Plan target | ~15 files |

Plan target was ~15. Actual is 19 because:
- 3 gitignored runtime files (`db.sqlite3`, `dump.rdb`, `django_debug.log`) — must stay at root for local dev
- 4 docker-compose variants (`docker-compose.yml` + `.ci.yml` + `.monitoring.yml` + `.prod.yml`) — all legit
- 12 other legit config/entry files (CLAUDE.md, README.md, 00-START-NEXT-SESSION.md, Dockerfile, entrypoint.sh, Makefile, manage.py, Procfile, pyrightconfig.json, pytest.ini, railway.toml, requirements.txt)

Every remaining file at root belongs there. The 4-file "overshoot" vs the ~15 estimate is docker-compose variants + runtime files — neither can be moved.

## Pre-flight findings

### Critical reference check (run once, applied per-sub-phase)

Grep'd every Phase 3 script name against:
- `Makefile`
- `Procfile`
- `docker-compose*.yml`
- `entrypoint.sh`

**Only hit:** `run_discord_bot` — 4 refs in `Makefile`. Investigation below.

All other ~55 scripts: **zero references** in build/deploy files. Safe to move.

### Phase 4-flagged scripts — resolved and included in Phase 3.8

The plan deferred these 3 scripts to Phase 4 pending investigation. Each was inspected during this session; all turned out to be one-off scripts safely archivable.

#### I1 resolution: `run_discord_bot.py` — confirmed stale duplicate

**Finding:** 14-line thin shim at root:
```python
#!/usr/bin/env python
"""Run the Discord bot."""
import os
import asyncio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from core.services.discord_bot import run_bot
if __name__ == '__main__':
    asyncio.run(run_bot())
```

**Canonical version:** `core/management/commands/run_discord_bot.py` (57 lines, proper Django Command class).

**Makefile usage:**
```makefile
nohup $(DJANGO_MANAGE) run_discord_bot > $(DISCORD_BOT_LOG) 2>&1 &
```

The Makefile calls `python manage.py run_discord_bot` (the mgmt command), NOT the root-level script. The `pgrep -f "run_discord_bot"` check matches either (the string appears in both the mgmt command invocation and the file path) but functionally nothing uses the root version.

**Verdict:** stale duplicate. Moved to `scripts/one-off/` in Phase 3.8 with a note in the commit message.

#### `audit_system.py` — Session 127 audit script, no refs
279 lines, written for "Session 127 Part 2" system audit. Zero references anywhere. Moved to `scripts/one-off/`.

#### `rag_docs.py` — Local Ollama RAG embedder, no refs
51 lines, uses local Ollama (`http://127.0.0.1:11434`) to embed local docs. Zero references. Moved to `scripts/one-off/`.

### I5 resolution: `spreadspoke.R` — orphan

**Finding:** 1 R script committed in Session 33 (commit `9614b7b2` — "Implement User Profile + Agent Learning Integration"). Contains early NFL-spread regression analysis. References a local path (`~/Documents/R/nfl regression/spreadspoke`) and a CSV (`spreadspoke_scores.csv`) that isn't in the repo. Unrelated to the current platform.

**Action:** moved to `archive/early_experiments/spreadspoke.R`. Preserved per DO 11 for historical/retrospective value.

## Verification

| Check | Result |
|---|---|
| `pytest --collect-only` test count | **766** ✅ (same as pre-Phase-3) |
| `pytest --collect-only` errors | 1 ✅ (same pre-existing unrelated error) |
| Root `backfill_*.py` / `fix_*.py` / etc. | 0 for all 8 patterns ✅ |
| Root `test_*.py` (from Phase 2) | 0 ✅ (unchanged) |
| Root file count | 80 → 19 (-61) ✅ |
| `git log --follow scripts/backfills/<any>.py` | history traverses rename ✅ |
| `Makefile` still references `$(DJANGO_MANAGE) run_discord_bot` | ✅ (mgmt command unchanged) |
| All existing `scripts/` subdirs intact | ✅ |

## Commit structure

One commit per sub-phase (for `git bisect` cleanliness):

1. `chore(cleanup): Phase 3.1 — move backfill_*.py → scripts/backfills/ (4 files)`
2. `chore(cleanup): Phase 3.2 — move fix_*.{py,sh} → scripts/fixes/ (13 files)`
3. `chore(cleanup): Phase 3.3 — move check_*.py → scripts/checks/ (6 files)`
4. `chore(cleanup): Phase 3.4 — move verify_*.py → scripts/verify/ (6 files)`
5. `chore(cleanup): Phase 3.5 — move diagnose_*.py → scripts/diagnose/ (4 files)`
6. `chore(cleanup): Phase 3.6 — move cleanup_*.py + clean_workspace.py → scripts/cleanup/ (4 files)`
7. `chore(cleanup): Phase 3.7 — move register_*.py → scripts/registrations/ (3 files)`
8. `chore(cleanup): Phase 3.8 — move remaining one-off scripts → scripts/one-off/ (19 files)`
9. `chore(cleanup): Phase 3 — archive orphan R script (I5 resolution)`

Plus a later "Phase 3 execution log" commit (this file).

## What's NOT in Phase 3

- **docker-compose variants** — there are 4 at root. They're all legit and shouldn't be consolidated without a real reason.
- **Directory audit (Phase 4)** — the ~69 top-level dirs (some orphan from early exploration) still need a separate audit per the plan's Phase 4.2. Deferred.
- **Token rotation** — the hardcoded prod token flagged in Phase 2 still needs Chris's rotation. Outside cleanup scope.
- **`.gitignore` hardening for scripts dir** — not added since scripts/ subdirs don't need enforcement like `/*.log` did; one-off scripts at root are obviously misplaced by naming convention alone.

## Deferred: Phase 4

Per `ROOT_CLEANUP_PLAN.md` Phase 4, the remaining work is:
- Directory-level audit of ~69 top-level dirs (identify orphans, empty dirs, duplicates like `archive/` vs `_archived/`)
- Any other per-directory investigations that surface

Phase 4 does NOT block the "polished parked state" goal — the root is clean, imports work, pytest runs. Phase 4 is discretionary cleanup for later.

## Rollback

Any single sub-phase: `git revert <sub-phase-commit-sha>`.
All of Phase 3: `git revert <PR-merge-sha>`.

All moves via `git mv` — history preserved, `git log --follow` works across renames.

## Related

- Plan: [`ROOT_CLEANUP_PLAN.md`](ROOT_CLEANUP_PLAN.md)
- Phase 1 log: [`PHASE_1_EXECUTION_LOG.md`](PHASE_1_EXECUTION_LOG.md)
- Phase 2 log: [`PHASE_2_EXECUTION_LOG.md`](PHASE_2_EXECUTION_LOG.md)
- Framework: [`../docs-pattern/06_dos_and_donts.md`](../docs-pattern/06_dos_and_donts.md) (DO 11)
