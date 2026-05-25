---
originating_session: 822
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 822: SKIN Layer Autonomous Remediation Integration

**Date:** January 25, 2026
**Status:** Complete
**PRs:** #176, #177, #178

## Summary

Connected the Autonomous Remediation Orchestrator to the SKIN Layer, enabling agents to write code directly to the project filesystem. This transforms the remediation system from generating proposals to actually deploying fixes autonomously.

## Changes

### 1. Revenue Tracking Signals (PR #176)
Created Django signals to automatically create Revenue records when Opportunities are accepted.

**New Files:**
- `core/signals/revenue_signals.py` - pre_save and post_save handlers

**Modified Files:**
- `core/signals/__init__.py` - Export new signals
- `core/apps.py` - Connect signals on startup

### 2. SKIN Layer Integration (PR #177)
Connected the remediation orchestrator to WorkspaceManager for file operations.

**Modified:** `core/services/autonomous_remediation_orchestrator.py`
- Added `_get_system_workspace()` - Get project workspace
- Added `_get_workspace_manager()` - Get WorkspaceManager instance
- Added `_parse_code_from_result()` - Extract code files from agent output
- Added `_parse_code_blocks()` - Parse markdown code blocks
- Added `_write_and_commit_files()` - Write files and auto-commit
- Added `_auto_commit_changes()` - Create git commits
- Updated `_execute_single_task()` to use SKIN layer

**Modified:** `core/management/commands/auto_remediate.py`
- Added `--no-commit` flag to disable auto-commit

### 3. Enhanced Code Parsing (PR #178)
Improved code parsing to handle more agent output formats.

**Parsing Patterns:**
1. `### path/to/file.py` before code blocks
2. `# filename.py` as first line in code blocks
3. Filenames in docstrings (`"""filename.py`)
4. Extract from class names for substantial code blocks
5. Parse 'message' and 'query' fields for code blocks

**First Agent-Generated Files:**
- `scifi/models.py` - AgentMood with mood_expires_at
- `scifi/management/commands/backfill_mood_expiry.py` - Backfill command
- `scifi/tests/test_models.py` - Tests for mood expiry

## Test Results

```json
{
  "written": true,
  "total_written": 3,
  "files_written": [
    {"path": "scifi/models.py", "size": 2183},
    {"path": "scifi/management/commands/backfill_mood_expiry.py", "size": 3174},
    {"path": "scifi/tests/test_models.py", "size": 3715}
  ],
  "commit": {
    "committed": false,
    "error": "Direct commits to 'main' branch are prohibited"
  }
}
```

## Architecture

```
Autonomous Remediation Pipeline (4 Phases + SKIN)
================================================

Phase 1: Discover
  └─> Scan docs/audits/ for audit files
  └─> Extract findings into AuditFinding records

Phase 2: Assign
  └─> Match findings to appropriate agents
  └─> Create AuditRemediationTask records

Phase 3: Execute
  └─> Run agent with finding context
  └─> Parse code from agent output (4 patterns)
  └─> Write files via WorkspaceManager (SKIN)
  └─> Auto-commit changes (if not on main)

Phase 4: Verify
  └─> Run verification checks
  └─> Update finding status
```

## Usage

```bash
# Full autonomous cycle
python manage.py auto_remediate

# Execute with SKIN layer (writes files)
python manage.py auto_remediate --execute --limit 5

# Execute without auto-commit
python manage.py auto_remediate --execute --no-commit

# Dry run (no changes)
python manage.py auto_remediate --dry-run
```

## Known Limitations

1. **Auto-commit blocked on main**: Pre-commit hook prevents direct commits to main branch (safety feature)
2. **Inconsistent agent output**: Some agents return specifications instead of code
3. **Manual PR required**: Agent-generated code still needs human review before merging

## Files Changed

| File | Change |
|------|--------|
| `core/signals/revenue_signals.py` | NEW - Revenue tracking signals |
| `core/signals/__init__.py` | Export revenue signals |
| `core/apps.py` | Connect revenue signals |
| `core/services/autonomous_remediation_orchestrator.py` | SKIN layer integration |
| `core/management/commands/auto_remediate.py` | --no-commit flag |
| `scifi/models.py` | NEW - Agent-generated |
| `scifi/management/commands/backfill_mood_expiry.py` | NEW - Agent-generated |
| `scifi/tests/test_models.py` | NEW - Agent-generated |

## Next Session

1. Consider creating feature branches for agent-generated code automatically
2. Add PR creation to the auto-commit flow
3. Improve agent prompts to ensure consistent code output format
