---
originating_session: 1026
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1026: Remediation System Redesign

**Date:** February 17, 2026
**Status:** Complete

## Problem

The CodeGeneratorAgent remediation pipeline was burning **$9/day** (~88 executions/24h) re-analyzing the same 58+ findings. The agent runs in Railway's ephemeral sandbox with no codebase access — it produces analysis specs but can never write actual fixes. Tasks cycle between `assigned` -> `spec_complete` -> `assigned` indefinitely.

Session 1022 (PR #1257) paused the schedules, but PR #1260 re-enabled them because "findings are valuable for tracking system improvements." The findings ARE real (e.g., duplicate UserProfile definitions, missing service health monitoring), but the execution loop is pure waste.

## Solution: Keep Discovery, Kill Execution

| Schedule | Action | Reason |
|----------|--------|--------|
| `discover-and-import-audits` (daily midnight) | **KEPT** | Discovers real issues from audit reports |
| `assign-open-findings-to-agents` (every 2h) | **KEPT** | Categorizes and assigns findings |
| `execute-remediation-tasks` (every 4h) | **DISABLED** | Agent can't access codebase |
| `verify-completed-fixes` (every 6h) | **DISABLED** | Nothing to verify |
| `run-autonomous-remediation-cycle` (daily 2am) | **DISABLED** | Full cycle includes execution |

### New Flow

Instead of: Finding -> Agent (empty sandbox) -> spec_complete -> re-assign -> repeat ($9/day)

Now: Finding -> `show_remediation_findings` command -> Claude Code session fixes it -> mark fixed

### Management Command

```bash
# All open findings
python manage.py show_remediation_findings

# Critical/High only
python manage.py show_remediation_findings --priority P0 P1

# By category
python manage.py show_remediation_findings --category security

# With full descriptions
python manage.py show_remediation_findings --verbose --limit 5
```

## Changes Made

### 1. `core/celery.py`
- Commented out 3 execution schedules with Session 1026 note
- Kept 2 discovery/assignment schedules active

### 2. `core/management/commands/show_remediation_findings.py` (NEW)
- Surfaces open findings grouped by priority/category
- Shows affected files for each finding
- Designed for Claude Code session start

### 3. Railway DB Changes
- **69 stuck `assigned` tasks** -> `cancelled` with explanation
- **10 `spec_complete` tasks** -> `cancelled`
- **69 findings** reset from `in_progress` -> `open` (now visible in command)
- **3 PeriodicTask entries** disabled in django_celery_beat DB (critical — commenting out Python code alone doesn't disable DB-persisted schedules)

## Current State

- **80 open findings**: 3 P1, 76 P2, 1 P3
- **Categories**: other=62, integration=8, code_quality=5, data_integrity=3, consistency=2
- **Expected cost savings**: ~$9/day (was $9.18/day over last 24h)
- **Discovery still running**: New findings will continue to be discovered and categorized

## Key Learning

**django_celery_beat DB persistence**: Commenting out schedule definitions in `celery.py` does NOT disable schedules that are already persisted in the `django_celery_beat_periodictask` table. You must ALSO disable them in the DB via `PeriodicTask.objects.filter(name='...').update(enabled=False)`. This is why Session 1022's "pause" didn't actually stop execution — the code was re-enabled in PR #1260, but even without that, the DB entries would have kept running.

## Investigation: UserProfile Duplicate Finding

The CodeGeneratorAgent flagged "UserProfile, EnhancedUserProfile defined twice" — this is a **real finding**:

1. **`core/models/users/models.py`** — CANONICAL UserProfile (Django model, OneToOneField to User)
2. **`core/models.py`** (line 561) — DEAD CODE duplicate. Python resolves `core.models` to the package (`core/models/__init__.py`), never this 97KB file.
3. **`core/unified_storage.py`** (line 33) — DIFFERENT model with `CharField user_id`. Causes `RuntimeError: Conflicting 'userprofile' models` at import time.
4. **`core/services/discord_bot.py`** (line 3489) — Broken import: `from core.models_unified_system import EnhancedUserProfile` fails because it doesn't exist there.

The agent correctly identified the issue but its proposed fixes were wrong (editing dead code, treating different models as duplicates). This validates the redesign: discovery is valuable, but execution belongs in Claude Code sessions with actual codebase access.
