---
title: "Root Cleanup Plan — unified-donkey-betz"
status: draft
created: 2026-04-20
session: post-1099
goal: Get the repo root clean enough that unified-donkey-betz can be "set aside in a polished state" while Chris builds other income apps. Nothing is deleted — everything is moved per DO 11 (archive, never delete).
---

# Root Cleanup Plan

> **This is a plan doc, not an execution log.** No files have been moved yet.
> Each phase is one future PR. Read the phase's pre-flight command before
> executing. Cross-reference the "Investigations" section before touching
> anything flagged as higher-risk.

---

## TL;DR

- Root has **338 entries** (as of 2026-04-20). ~15 legitimately belong at root.
- The rest falls into 8 clean categories: logs, runtime artifacts, JSON reports, image artifacts, notes, test scripts, one-off maintenance scripts, and miscellaneous one-offs.
- Nothing gets `rm`'d. Files move into existing sub-directories (`logs/`, `tests/`, `scripts/`, `reports/`, `audits/`, `temp/`, `docs/archive/`) or into new ones.
- Work is phased by risk: Phase 1 (zero-risk moves) → Phase 2 (test scripts) → Phase 3 (one-off scripts) → Phase 4 (higher-risk / directory audit).
- Each phase = one PR. Pre-flight command listed per phase. Rollback = `git revert`.

---

## Table of Contents

1. [Goal](#goal)
2. [Guiding Rules](#guiding-rules)
3. [What Stays at Root](#what-stays-at-root)
4. [Audit Summary](#audit-summary)
5. [Phase 1 — Zero-Risk Moves](#phase-1--zero-risk-moves)
6. [Phase 2 — Test Scripts](#phase-2--test-scripts)
7. [Phase 3 — One-Off Maintenance Scripts](#phase-3--one-off-maintenance-scripts)
8. [Phase 4 — Higher-Risk Scripts + Directory Audit](#phase-4--higher-risk-scripts--directory-audit)
9. [Investigations / Open Questions](#investigations--open-questions)
10. [Execution Rubric](#execution-rubric)
11. [Rollback Strategy](#rollback-strategy)
12. [Success Criteria](#success-criteria)

---

## Goal

Chris is stepping back from building new Donkey Betz features to pursue income-generating side apps (using the `docs-pattern/` framework as a template). He wants the platform in a clean "parked" state when he returns.

**Target end state:**
- Root has ~15 files + clearly-scoped top-level directories.
- Every remaining script, test, log, and artifact lives under a named subdirectory.
- `verify_doc_claims` still passes.
- No broken imports, no missing Celery tasks, no broken Procfile references.

---

## Guiding Rules

From `docs/docs-pattern/06_dos_and_donts.md`:

- **DO 1:** Use directories — never scatter `.md` (or anything else) at the root.
- **DO 11:** Archive, never delete. Move files, don't `rm`.
- **DON'T 11:** `rm` a doc/script to "clean up clutter."

From `feedback_no_fluff_verify_truth.md` (saved 2026-04-20):

- Every claim verifiable. Every move justifiable. No cleanup-by-vibes.

**Execution rule:** use `git mv` (not `mv`) so file history is preserved across the move. Future grep / blame / git log still works.

---

## What Stays at Root

These files and dirs are expected at the repo root per convention or tooling:

| Entry | Reason |
|---|---|
| `CLAUDE.md` | AI session entry point (docs-pattern DO 5) |
| `README.md` | GitHub default landing |
| `00-START-NEXT-SESSION.md` | Session entry point (docs-pattern) |
| `manage.py` | Django convention |
| `Makefile` | Build commands |
| `Procfile` | Railway worker definitions |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Container image |
| `docker-compose.yml` / `docker-compose.*.yml` | Compose configs |
| `entrypoint.sh` | Container entry |
| `pytest.ini` | Test runner config |
| `pyrightconfig.json` | Type checker config |
| `railway.toml` | Railway deploy config |
| `.gitignore` / `.env*` / `.dockerignore` | Tooling dotfiles |
| `db.sqlite3` | Local dev DB (gitignored — not committed) |
| `dump.rdb` | Local Redis dump (gitignored) |
| `venv_ml/` | ML-specific venv (gitignored but dir exists) |

**Top-level directories that are keepers** (need no moving):

| Dir | Purpose |
|---|---|
| `core/`, `ai_core/`, `services/` | Main app modules |
| `frontend/`, `mobile/`, `dashboard/` | UI surfaces |
| `docs/` | Documentation |
| `tests/` | Test suite |
| `scripts/` | Automation scripts |
| `logs/` | Log output directory |
| `reports/`, `audits/` | Structured output |
| `temp/` | Ephemeral output |
| `media/`, `static/`, `staticfiles/` | Django assets |
| `templates/` | Django templates |
| `config/` | App config |

**Note:** the ~69 existing top-level dirs will get their own audit in Phase 4 — many appear to be orphaned feature directories from early exploration.

---

## Audit Summary

Counts as of 2026-04-20 (`ls -1 | wc -l` returned 338):

| Category | Count | Destination | Phase |
|---|---|---|---|
| Log files (`*.log`) | ~35 | `logs/` | Phase 1 |
| Nohup output (`*.out`) | 6 | `logs/` | Phase 1 |
| JSON reports | ~14 | `reports/` or `audits/` | Phase 1 |
| PNG artifacts | 16 | `temp/` or `tests/artifacts/` | Phase 1 |
| Text/markdown notes | 4 | `docs/archive/` | Phase 1 |
| Runtime state (`.sqlite3`, `.rdb`) | 2 | stay (gitignored) | none |
| Test scripts (`test_*.py`) | ~60 | `tests/one-off/` | Phase 2 |
| Test HTML (`test_*.html`) | 4 | `tests/manual/` | Phase 2 |
| Backfill scripts | 4 | `scripts/backfills/` | Phase 3 |
| Fix scripts | 13 | `scripts/fixes/` | Phase 3 |
| Check scripts | 6 | `scripts/checks/` | Phase 3 |
| Verify scripts | 6 | `scripts/verify/` | Phase 3 |
| Diagnose scripts | 4 | `scripts/diagnose/` | Phase 3 |
| Cleanup scripts | 4 | `scripts/cleanup/` | Phase 3 |
| Register scripts | 3 | `scripts/registrations/` | Phase 3 |
| Session/one-off scripts | ~18 | `scripts/one-off/` | Phase 3 |
| Higher-risk scripts | ~6 | per-investigation | Phase 4 |
| Legit root files | ~15 | stay | none |

**Rough totals:** ~195 files move in Phases 1–3, ~6 need investigation in Phase 4, ~15 stay at root, plus ~80 directories (~69 top-level + subdirs) need the Phase 4 directory audit.

---

## Phase 1 — Zero-Risk Moves

**Risk:** near zero. These categories have no code imports, are already gitignored (or should be), and are pure output/artifact.

**Order within Phase 1:** do sub-phases 1.1 → 1.5 in any order; they're independent.

### 1.1 Log files → `logs/`

**Files** (35 total):

```
celery_beat.log
celery_debug.log
celery_worker.log
celery-beat.log
celery-broadcast.log
celery-default.log
celery-long-running.log
celery-pa.log
celery-test-worker.log
celery.log
content_monetization_1759.log
content_spider_deployment.log
content_spiders_fixed.log
daphne.log
davinci-bridge.log
discord_bot.log
discord-bot.log
django_debug.log
django_server_final.log
django_server_latest.log
django_server_new.log
django_server_newest.log
django_server.log
flutter.log
medium_gumroad_deployment.log
overnight_learning_test.log
overnight_validation_test.log
review.log
server.log
spider_deployment.log
spider_worker.log
sports_sentiment_1759.log
sports_sentiment_async_fixed_1814.log
sports_sentiment_praw_1811.log
technical_1759.log
```

**Pre-flight:**
```bash
git check-ignore *.log    # Confirm all are gitignored
ls logs/                  # Confirm dest exists
grep -rE "open\(['\"].*\.log" core/ ai_core/ services/ tools/ --include="*.py" | head
```
(Expected: matches will use relative paths — none should rely on files being AT root vs in `logs/`.)

**Command:**
```bash
git mv *.log logs/
```

**Follow-up:** update `.gitignore` so new logs at root get caught immediately:
```
# Enforce logs/ as the only log location
/*.log
```

### 1.2 Nohup output → `logs/`

**Files** (6):
```
nohup_celery_beat.out
nohup_celery_broadcast.out
nohup_celery_long.out
nohup_celery.out
nohup_default_worker.out
nohup.out
```

**Command:** `git mv nohup*.out logs/`
**Also gitignore:** `/nohup*.out`

### 1.3 JSON reports → `reports/` (or `audits/` for audits)

**Audit-style (go to `audits/`):**
```
agent_reality_audit_20251002_200115.json
agent_reality_audit_20251002_200519.json
```

**Test/validation output (go to `reports/`):**
```
agent_test_report.json
overnight_test_report_20251002_070023.json
overnight_test_report_20251002_070506.json
overnight_test_report_20251002_070838.json
overnight_test_report_20251002_071220.json
overnight_test_report_20251002_071328.json
overnight_test_report_20251002_071803.json
overnight_test_report_20251002_072316.json
overnight_test_report_20251002_072455.json
overnight_test_report_20251002_173706.json
spider_results.json
spider_verification_results.json
websocket_diagnostic_20251002_170359.json
```

**Pre-flight:**
```bash
grep -rE "reality_audit_|overnight_test_report_|spider_results\.json|websocket_diagnostic_" --include="*.py" core/ ai_core/ services/ tools/ | head
```
(Expected: no imports — these are outputs. If any match writes TO the file, update the path.)

**Command:**
```bash
git mv agent_reality_audit_*.json audits/
git mv agent_test_report.json overnight_test_report_*.json spider_results.json spider_verification_results.json websocket_diagnostic_*.json reports/
```

### 1.4 PNG artifacts → `tests/artifacts/` (new subdir)

**Files** (16):
```
core_143335.png
pixar_robot_20251102_135902.png
pixar_robot_20251104_101326.png
recolored_144057.png
sd3_143347.png
sd3_143407.png
sd3_143414.png
sd3_143421.png
sdxl_balanced_143340.png
test_sd3_20251102_142820.png
test_sd3_advanced_20251102_142841.png
test_sdxl_20251102_142105.png
test_sdxl_20251102_142737.png
test_stable_image_core_20251102_142834.png
test_stable_image_ultra_20251102_142830.png
ultra_143400.png
```

**Pre-flight:** these are generated test output; should have zero code refs.
```bash
grep -rE "(core|recolored|ultra|pixar|sd3|sdxl)_\d+\.png" --include="*.py" . | head
```

**Command:**
```bash
mkdir -p tests/artifacts
git mv *.png tests/artifacts/     # be careful — check for intentional root PNGs first
```

**Follow-up gitignore:** `/*.png` (enforce no stray images at root going forward).

### 1.5 Text / markdown notes → `docs/archive/session_notes/`

**Files** (4):
```
cookies.txt                        # Check if sensitive before committing!
COMMIT_MESSAGE_SESSION_82.txt
EXPLORATION_SUMMARY.txt
OVL_MORNING_PACK.md
```

**⚠ Pre-flight — `cookies.txt` audit:**
```bash
# This file may contain auth cookies. Inspect before moving.
head -5 cookies.txt
git log --all --pretty=oneline -- cookies.txt | head -3
```

If cookies.txt contains real auth tokens: add to `.gitignore`, shred locally, rotate affected tokens. Do NOT commit it to `docs/archive/`.

**Command (for the safe files):**
```bash
mkdir -p docs/archive/session_notes
git mv COMMIT_MESSAGE_SESSION_82.txt EXPLORATION_SUMMARY.txt OVL_MORNING_PACK.md docs/archive/session_notes/
```

---

## Phase 2 — Test Scripts

**Risk:** medium-low. Spot check (`core/testing/__init__.py`) showed the only cross-imports are between neighbor test files inside `core/testing/`, not from root. But ~60 files is a big batch; verify before moving.

### 2.1 Pre-flight — verify no imports

```bash
# Are any root-level test_*.py imported by production code?
grep -rE "from\s+test_\w+\s+import|^import\s+test_\w+" --include="*.py" core/ ai_core/ services/ tools/ frontend/ | head -20

# Are they discovered by pytest? (Would change whether they're "real tests")
grep -rE "^(testpaths|python_files)" pytest.ini setup.cfg pyproject.toml 2>/dev/null

# Double-check the one-off vs pytest distinction — do any have `def test_*` functions?
grep -lE "^def test_" test_*.py | head -10
```

**If any are pytest tests:** move them to `tests/integration/` instead of `tests/one-off/`, and keep them in pytest discovery.

**If all are ad-hoc scripts:** move to `tests/one-off/` with a note in `tests/one-off/README.md` that they are NOT part of the CI test suite.

### 2.2 Move test_*.py files

Target dir: `tests/one-off/` (or `tests/integration/` per pre-flight).

```bash
mkdir -p tests/one-off
git mv test_*.py tests/one-off/
```

Note: counts should be ~60 files. Enumerated in `ls -1 test_*.py` at cleanup time.

### 2.3 Move test_*.html files

These are manual browser-testing artifacts:
```
test_frontend_data_flow.html
test_notification_system.html
test_revenue_dashboard_real_data.html
test_sports_hub_fixed.html
```

```bash
mkdir -p tests/manual
git mv test_*.html tests/manual/
```

Add a `tests/manual/README.md` explaining how these are used (open in a browser against a running dev server).

### 2.4 Post-move verification

```bash
pytest --collect-only 2>&1 | tail -5        # pytest still discovers same set
python -c "import tests"                     # nothing broke
git log --follow tests/one-off/test_*.py | head    # history preserved via git mv
```

---

## Phase 3 — One-Off Maintenance Scripts

**Risk:** medium. These are one-off scripts that ran once and got committed. Low chance of being imported, but a few may be referenced in docs/handoffs or in Makefile.

**General pre-flight for each sub-phase:**
```bash
grep -rE "(from\s+<script_name>|import\s+<script_name>|python\s+<script_name>\.py)" --include="*.py" --include="Makefile" --include="*.md" . | head
```

### 3.1 Backfill scripts → `scripts/backfills/`

```
backfill_agent_contributions_session_142.py
backfill_agent_contributions.py
backfill_image_agents.py
backfill_video_agents.py
```

### 3.2 Fix scripts → `scripts/fixes/`

```
fix_agent_contribution_fields.py
fix_agent_contributions_session142.py
fix_completely_orphaned_videos.py
fix_orphaned_variations.py
fix_orphaned_videos.py
fix_project_images.py
fix_real_ui_issues.py
fix_stuck_video.py
fix_ui_issues.py
fix_video_2_download.py
fix_video_projects.py
fix_video_url.py
fix_websocket_urls.sh
```

### 3.3 Check scripts → `scripts/checks/`

```
check_3d_local_files.py
check_agent_assignment.py
check_recent_videos.py
check_runway_credits.py
check_video_status.py
check_video_urls.py
```

### 3.4 Verify scripts → `scripts/verify/`

```
verify_3d_files.py
verify_agent_contributions.py
verify_all_ui_fixes.py
verify_cloudinary_setup.py
verify_market_intelligence_desk.py
verify_project_videos.py
```

### 3.5 Diagnose scripts → `scripts/diagnose/`

```
diagnose_3d_models.py
diagnose_project_complete.py
diagnose_project_images.py
diagnose_ui_issues.py
```

### 3.6 Cleanup scripts → `scripts/cleanup/`

```
clean_workspace.py
cleanup_3d_models.py
cleanup_incomplete_3d_models.py
cleanup_orphaned_images.py
```

### 3.7 Register scripts → `scripts/registrations/`

```
register_3d_generation_agent.py
register_trained_creation_agent.py
register_video_editing_agent.py
```

### 3.8 Session / one-off misc → `scripts/one-off/`

Scripts without a clearer category:

```
activate_spiders.py
add_minifig_asset_to_agent_contribution.py
demo_image_styles.py
download_video.py
fetch_pending_video_urls.py
final_health_check.py
generate_auth_token.py
list_agents.py
migrate_images_to_cloud.py
quick_spider_test.py
replace_tools_with_agents.py
rescue_cdn_videos.py
session_131_agent_tools.py
START_MAKING_MONEY_NOW.py
start_overnight_test.sh
sync_celery_schedules.py
```

Add `scripts/one-off/README.md` listing which session each came from (pull from git log).

### 3.9 Command pattern per sub-phase

```bash
mkdir -p scripts/<category>
git mv <file1> <file2> ... scripts/<category>/
# Commit each sub-phase separately so bisect is clean
git commit -m "chore(cleanup): Phase 3.<N> — move <category> scripts"
```

---

## Phase 4 — Higher-Risk Scripts + Directory Audit

**Risk:** higher. These items need investigation before moving.

### 4.1 Scripts that need a reference check first

| Script | Potential risk |
|---|---|
| `run_discord_bot.py` | There's a `python manage.py run_discord_bot` mgmt command. Root-level version may be a stale duplicate. **Investigate first.** |
| `audit_system.py` | Unclear purpose. Grep for callers. |
| `rag_docs.py` | Unclear purpose. Grep for callers. |

**Pre-flight for each:**
```bash
# Procfile reference?
grep "<script_name>" Procfile

# Makefile reference?
grep "<script_name>" Makefile

# Docs reference?
grep -rE "\b<script_name>\b" docs/ | head

# Imported from core?
grep -rE "from\s+<script_name>|import\s+<script_name>" --include="*.py" . | head
```

For `run_discord_bot.py` specifically: compare `run_discord_bot.py` to `core/management/commands/run_discord_bot.py` (assuming that's where the mgmt cmd lives). If they're functionally equivalent, the root copy is stale — move it to `scripts/archive/` with a note in the cleanup PR.

### 4.2 Directory audit (the harder cleanup)

~69 top-level directories exist. Many look like early-exploration silos that got orphaned. Examples worth investigating:

- `archive/` vs `_archived/` — which is canonical? Dedupe.
- `agents/`, `advisors/` at root — do these still hold anything, or are they empty orphans from pre-`core.agents/` migration?
- `ai_generated_projects/`, `ai_nexus/`, `ai_opportunities/`, `ai_platform/` — 4 "ai_*" dirs. Likely early exploration.
- `avatars/`, `blender_tests/`, `campaigns/`, `coleadership/`, `diversity/`, `executive/`, `execution/`, `financial/`, `income_builder_outputs/`, `intelligence/`, `llm/`, `ml_intelligence/`, `ml_models/`, `ml_pipeline/`, `ml/` (5 ml-related!), `mythology/`, `narrative/`, `odds_calc/`, `persistence/`, `pipelines/`, `podcast/`, `predictions/`, `proposals_output/`, `real_freelance_deliverables/`, `real_job_deliverables/`, `rendering/`, `review/`, `revenue/`, `revenue_data/`, `security/`, `self_awareness/`, `series/`, `spider_configs/`, `sports_betting/`, `sports/`, `src/`, `strategy/`, `style_memory/`, `summaries/`, `system/`, `workflows/`

**Pre-flight approach:**
```bash
# Per-dir check: is anything in it actually imported?
for d in agents advisors ai_generated_projects ai_nexus ai_opportunities ai_platform; do
    echo "=== $d ==="
    grep -rE "from\s+${d}\.|import\s+${d}\b" --include="*.py" core/ ai_core/ services/ tools/ frontend/ 2>/dev/null | head -3
done
```

**If no imports found:** the directory is orphaned. Move to `archive/orphaned_dirs_2026-04/` rather than delete (per DO 11).

**If imports found:** leave the directory alone and document its status in a `<dirname>/README.md` saying it's active.

**Scope warning:** this sub-phase could consume multiple sessions. Budget one session per ~10 directories if doing it seriously. Can be deferred indefinitely — the root-file cleanup in Phases 1–3 is the priority.

---

## Investigations / Open Questions

These surfaced during the audit and need answers before execution:

### I1. `run_discord_bot.py` — root vs mgmt command

`docs/current/TROUBLESHOOTING.md` and `docs/current/MANAGEMENT_COMMANDS.md` reference `python manage.py run_discord_bot` (a Django management command). The root has `run_discord_bot.py`. Are they the same code, or has one drifted? Is one referenced in `Procfile`?

**Action:** diff the two files, check `Procfile`. If root is stale, move to `scripts/archive/`.

### I2. `archive/` vs `_archived/`

Two directories with similar names at root. Which is the canonical archive? Is one inside the other? What's in each?

**Action:** `ls archive/ _archived/` and classify each before moving anything into either.

### I3. `cookies.txt` — sensitive?

Filename suggests auth cookies. If it contains live tokens: security risk, don't move to `docs/archive/`, rotate the tokens, add to `.gitignore`, shred locally.

**Action:** inspect content, check git history (`git log cookies.txt`), rotate if compromised.

### I4. Old session notes at root (OVL_MORNING_PACK.md, COMMIT_MESSAGE_SESSION_82.txt, EXPLORATION_SUMMARY.txt)

These are artifacts from specific sessions. Per DO 11 they move to `docs/archive/`, but future sessions may benefit from a git-blame trail.

**Action:** before moving, extract the originating session numbers from git log and note them in the destination filename (e.g. `SESSION_82_COMMIT_MSG.txt` rather than just `COMMIT_MESSAGE_SESSION_82.txt`).

### I5. `spreadspoke.R` — origin unknown

R script at root. No context. Likely an experiment. Grep for references.

**Action:** `grep -rE "spreadspoke" docs/ handoffs/` + `git log spreadspoke.R`. If truly orphan, move to `archive/early_experiments/`.

### I6. PNG artifacts — do any have intentional references?

Some PNGs may be used as reference images in tests or prompts. Confirm none are referenced before moving.

```bash
for img in *.png; do
    echo "=== $img ==="
    grep -rE "\"${img}\"|'${img}'" --include="*.py" --include="*.md" . 2>/dev/null | head -2
done
```

### I7. The `scripts/` directory — already exists, what's in it?

Before adding `scripts/backfills/` etc., confirm the existing `scripts/` dir structure so we don't collide with current conventions.

**Action:** `ls scripts/` + read any `scripts/README.md`.

### I8. Are any of the 60+ `test_*.py` files referenced in `pytest.ini` / `conftest.py`?

If pytest is configured to pick up root-level `test_*.py`, moving them changes the test surface. Verify.

**Action:** `cat pytest.ini` + check for `testpaths` config.

---

## Execution Rubric

### One phase = one PR

Each phase (and each numbered sub-phase in Phase 3) gets its own PR with:
- Title: `chore(cleanup): Phase <N>.<M> — <category>`
- Body: list of moved files + pre-flight command output + grep-for-refs result
- Test plan: `verify_doc_claims` passes, `pytest --collect-only` succeeds, Celery workers still start in dev

### Use `git mv`, not `mv`

Preserves file history. `git blame` and `git log --follow` still work across the move.

### Commit one sub-phase at a time

Makes `git bisect` trivial if something breaks later. Phase 1.1 alone = one commit + one merge.

### Update `.gitignore` in the same PR

When a category gets moved to a subdir, update `.gitignore` to enforce the new location. Example: after Phase 1.1, add `/*.log` to gitignore so future stray logs at root fail the next commit.

### Update `docs/` references in the same PR

If any `docs/` file references the moved path (e.g. "see `backfill_agents.py`"), update the reference in the same PR.

### Regenerate `docs/INDEX.md` + `_index.json` after every PR

Per the docs-pattern DO 10 / pre-commit hook.

### Post-execution — update `CLAUDE.md` "Key Directories" section

CLAUDE.md's project-structure table may reference moved paths. Update per-phase or in a wrap-up commit.

---

## Rollback Strategy

**Per phase:** `git revert <merge-commit-sha>`. All moves are `git mv`, no data loss.

**Emergency unwind (worst case):** if a move breaks something discovered days later:
```bash
git log --follow --all <moved-file-path>
git checkout <pre-move-sha> -- <original-path>
```

**No file is destroyed in any phase.** Worst case is a temporarily misplaced file, recoverable by checkout.

---

## Success Criteria

At the end of Phases 1–3, these must all be true:

- [ ] Root file count (not counting dirs) drops from ~200 to ~15
- [ ] Remaining root files match the "What Stays at Root" table exactly
- [ ] `pytest --collect-only` returns the same test count as pre-cleanup
- [ ] `python manage.py runserver` starts without error
- [ ] `python manage.py verify_doc_claims` runs without new errors introduced by the cleanup
- [ ] `make start && make celery` launches without errors
- [ ] All 11 Procfile processes are still launchable
- [ ] `CLAUDE.md` "Project Structure" section matches actual directory layout
- [ ] No references in `docs/` point to the old root paths
- [ ] `.gitignore` enforces new category locations (so drift can't resume)

Phase 4 success is separate and can be deferred indefinitely without blocking the "parked, polished" state.

---

## Who Executes This

- **Not during Chris's break.** He wants the platform parked, not in the middle of a cleanup.
- **A future session (Chris or Claude Code) picks up from Phase 1.1.** All pre-flight commands are documented above.
- **Rigby can claim Phases 1.1–1.5** via PA tools if they're wrapped into a tool handler — but the actual `git mv` + PR steps are code-worker lane (matches the Rigby scope rule: Rigby's lane is ops/verification, Claude Code's is code + PRs).

---

## Cross-references

- Framework rules: `docs/docs-pattern/06_dos_and_donts.md`
- Doc preservation rule: `feedback_docs_never_delete.md` (memory)
- Truth-verify mode: `feedback_no_fluff_verify_truth.md` (memory)
- Current platform state: `docs/PLATFORM_WHAT_IT_IS.md`
- Runtime inventory: `docs/PLATFORM_INVENTORY.md`

---

*Draft created 2026-04-20. No files have been moved. When execution begins, rename this file to `ROOT_CLEANUP_PLAN_IN_PROGRESS.md` and add an execution log at the bottom tracking which PR landed which phase.*
