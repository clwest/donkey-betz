---
title: "Root Cleanup — Phase 2 Execution Log"
status: complete
date: 2026-04-20
related_plan: ROOT_CLEANUP_PLAN.md
previous_log: PHASE_1_EXECUTION_LOG.md
---

# Phase 2 Execution Log — Test Scripts

Phase 2 of `ROOT_CLEANUP_PLAN.md`. Moved 93 test-looking files (89 `.py` + 4 `.html`) out of the repo root into scoped `tests/` sub-directories. Nothing deleted (DO 11). History preserved via `git mv`.

**Date:** 2026-04-20
**Branch:** `chore/cleanup-phase-2-test-scripts`
**Scope:** root `test_*.py` + root `test_*.html`

## Summary

| Category | Files | Source | Destination |
|---|---|---|---|
| Python ad-hoc test scripts | 89 | root `test_*.py` | `tests/one-off/` |
| HTML manual-test harnesses | 4 | root `test_*.html` | `tests/manual/` |

**Root file count:** 172 → 80 (92 files relocated; 93 moves total with READMEs/conftest.py stripped from count).

## Pre-flight findings

### pytest discovery config

`pytest.ini` has `testpaths = tests` — meaning only `tests/` is scanned. Root `test_*.py` was NEVER discovered by pytest (confirmed by `pytest --collect-only -q` showing 0 matches from root-level files and 766 from the `tests/` suite).

**Implication:** the 89 root files were ad-hoc scripts, not real tests. Moving them into `tests/one-off/` would cause pytest to start collecting them — which would fail because most call `django.setup()` at module level and have other non-pytest patterns.

**Mitigation:** `tests/one-off/conftest.py` sets `collect_ignore_glob = ["test_*.py"]` to explicitly exclude this directory from pytest collection. Verified post-move: pytest still collects exactly 766 tests (same count as pre-move, with same pre-existing 1 error in `tests/unit/test_verbosity_fix.py` — unrelated to this cleanup).

### Import-risk grep

Spot-checked for `from test_<name>` / `import test_<name>` patterns across `core/`, `ai_core/`, `services/`, `tools/`. No root-level test imports from production code. Move is safe.

### ⚠ Security finding — hardcoded prod tokens in 2 files

**This surfaced during pre-flight inspection and needs attention beyond the cleanup:**

Two files embed a Railway production auth token:
- `tests/one-off/test_pa_readonly_tools.py` line 11
- `tests/one-off/test_pa_mutation_tools.py` line 14

Both contain: `TOKEN = '43d46129f9d92d5f454c4f8fced36b744a53d248'`

**Context:** these are PA tool testing scripts from Session 1062 that hit `https://donkey-betz-platform-production.up.railway.app` with this token in the `Authorization: Token ...` header.

**Risk assessment:**
- Token has been in git history since the files were committed (pre-Session 1062).
- Moving the files to `tests/one-off/` does NOT reduce exposure — git history is the authoritative record.
- If this token is still valid, anyone with read access to this repo history has authenticated access to the production API.

**Recommended action (outside Phase 2 scope):**
1. **Rotate the token** — regenerate in the Django admin, update `.env` files, update Railway deploy env vars.
2. **Replace the hardcoded literal** in the two files with `os.environ.get('PA_API_TOKEN_TEST')` or similar.
3. **Audit git history** for other hardcoded tokens: `git log -p | grep -E "[0-9a-f]{40}"`.

The move itself is not a security fix — it's organizational cleanup. The rotation step is Chris's call and must happen separately.

## What moved (file lists)

### Python ad-hoc scripts (89) → `tests/one-off/`

Full `ls tests/one-off/*.py` lists them. Notable patterns:
- `test_session_*.py` — session-specific tests (127, 128 × 3, 143 × 3, etc.)
- `test_animation_*.py`, `test_animate_*.py` — video/animation pipeline tests
- `test_runway_*.py`, `test_replicate_*.py`, `test_stability_*.py` — external API tests
- `test_agent_*.py`, `test_learning_*.py`, `test_character_training_*.py` — agent system tests
- `test_image_*.py`, `test_video_*.py`, `test_3d_*.py`, `test_audio_*.py` — media pipeline tests
- `test_pa_mutation_tools.py`, `test_pa_readonly_tools.py` — PA tool testing (**see security note above**)
- `test_spider_*.py`, `test_market_intel_desk.py` — spider / intelligence desk tests
- `test_project_*.py`, `test_projects_api.py`, `test_frontend_integration.py` — project integration
- Plus ~40 others.

All 89 are committed to the new location via `git mv`, so `git log --follow` tracks each file through the rename.

### HTML manual-test harnesses (4) → `tests/manual/`

- `test_frontend_data_flow.html`
- `test_notification_system.html`
- `test_revenue_dashboard_real_data.html`
- `test_sports_hub_fixed.html`

Each is a standalone browser page that hits local Django endpoints. `tests/manual/README.md` documents how to use them.

## New files (3)

- `tests/one-off/conftest.py` — pytest collection guard (`collect_ignore_glob = ["test_*.py"]`)
- `tests/one-off/README.md` — explains the directory, the pytest guard, and the security finding
- `tests/manual/README.md` — explains the HTML harnesses

## Verification

Post-move:

| Check | Result |
|---|---|
| `pytest --collect-only` test count | 766 ✅ (same as pre-move) |
| `pytest --collect-only` errors | 1 ✅ (same pre-existing error in `tests/unit/test_verbosity_fix.py` — unrelated) |
| Root `test_*.py` count | 0 ✅ |
| Root `test_*.html` count | 0 ✅ |
| `git log --follow tests/one-off/<any file>` | history traverses the rename ✅ |
| Pre-existing `tests/` structure untouched | ✅ (agents_tests/, api/, e2e/, etc. all intact) |

## Root count progression

| Checkpoint | Root files | Change |
|---|---|---|
| Pre-cleanup (before Phase 1) | 338 entries | — |
| After Phase 1 | 172 files | -166 (Phase 1 included dir counts) |
| **After Phase 2** | **80 files** | **-92** |
| Target end state (end of Phase 3) | ~15 | -65 more |

## What was NOT done

- **Phase 3** — one-off maintenance scripts (`backfill_*.py`, `fix_*.py`, `check_*.py`, etc.) still at root.
- **Token rotation** — flagged in the security section above; requires Chris's call + production access.
- **Dedup check** — didn't verify if any of the 89 moved files duplicate existing `tests/` fixtures or functions. If Phase 3 or a later cleanup session wants to consolidate, manual review is needed.

## Rollback

Single PR revert: `git revert <merge-commit-sha>`. All moves are reversible via `git mv`. New files (conftest.py, READMEs) get reverted with the rest.

## Next phase

Phase 3 = ~60 one-off maintenance scripts across 8 categories (backfills, fixes, checks, verify, diagnose, cleanup, registrations, one-off misc) → `scripts/<category>/` per plan section 3.

Per-sub-phase pre-flight (per plan):
```bash
grep -rE "(from\s+<script_name>|import\s+<script_name>|python\s+<script_name>\.py)" \
     --include="*.py" --include="Makefile" --include="*.md" . | head
```

## Related

- Plan: [`ROOT_CLEANUP_PLAN.md`](ROOT_CLEANUP_PLAN.md)
- Phase 1 log: [`PHASE_1_EXECUTION_LOG.md`](PHASE_1_EXECUTION_LOG.md)
- Framework: [`../docs-pattern/06_dos_and_donts.md`](../docs-pattern/06_dos_and_donts.md) (DO 11)
