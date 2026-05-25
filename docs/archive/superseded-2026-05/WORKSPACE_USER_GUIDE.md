# Workspace (SKIN Layer) User Guide

**Session 780 | January 19, 2026**

The **Workspace** page is the SKIN Layer of the AI Studio platform - the boundary where AI agents interface with real project filesystems. This is how agents "touch the real world."

---

## Table of Contents

1. [What is the SKIN Layer?](#what-is-the-skin-layer)
2. [Getting Started](#getting-started)
3. [Overview Tab](#overview-tab)
4. [Files Tab](#files-tab)
5. [Git Tab](#git-tab)
6. [Operations Tab](#operations-tab)
7. [Reviews Tab](#reviews-tab)
8. [Project Understanding (Context)](#project-understanding-context)
9. [Body Health Integration](#body-health-integration)
10. [Security & Permissions](#security--permissions)
11. [API Reference](#api-reference)
12. [Troubleshooting](#troubleshooting)

---

## What is the SKIN Layer?

In the AI Body metaphor used throughout the platform:

| Body Part | System Component |
|-----------|------------------|
| **Consciousness** | Human Operator |
| **Eyes/Ears** | Human Interface Layer |
| **Brain** | ThinkingAgent |
| **Nervous System** | Agent-Model Router |
| **Organs** | 72 Specialized Agents |
| **Sensory** | 77 Spiders (data collection) |
| **Hands/SKIN** | **Workspace Layer** - touches the real world |

The Workspace is where AI-generated code becomes real, working software. Every file write, git commit, and code modification goes through this layer with full audit trails and rollback capabilities.

---

## Getting Started

### Registering a Workspace

1. Navigate to **Workspace** in the sidebar
2. Click **Select Workspace** button
3. Click **Register New Workspace**
4. Enter:
   - **Project Path**: Absolute path to your project (e.g., `/Users/dev/my-project`)
   - **Name** (optional): Display name (auto-detected from folder if not provided)
   - **Description** (optional): Notes about the project
5. Click **Register**

The system will automatically:
- Detect the tech stack (React, Django, etc.)
- Scan the file structure
- Identify key files and patterns
- Extract dependencies

### Scanning a Workspace

After registration or when the project changes:

1. Click the **Scan** button in the header
2. Wait for scanning to complete
3. View updated statistics and context in the Overview tab

---

## Overview Tab

The Overview tab provides a comprehensive dashboard of your workspace.

### Statistics Cards (Row 1 - Project Stats)

| Card | Description |
|------|-------------|
| **Total Files** | Number of files in the workspace |
| **Directories** | Number of directories |
| **Lines of Code** | Approximate total lines of code |
| **Pending Reviews** | Operations awaiting human approval |

### Statistics Cards (Row 2 - Operations Stats)

| Card | Description |
|------|-------------|
| **Total Operations** | All-time operations performed |
| **Files Written** | Total files created/modified |
| **Git Commits** | Total commits made by agents |
| **Rollbacks Available** | Operations that can be undone |

### 24-Hour Activity

Shows operations, successes, and failures in the last 24 hours with visual progress bars.

### 7-Day Trends

Two cards showing:
- **By Type**: Operations grouped by type (file_create, file_modify, git_commit, etc.)
- **By Agent**: Operations grouped by agent name (top 10 agents shown)

### File Types

Visual breakdown of file extensions in the project (e.g., `.py: 234`, `.tsx: 89`).

### Tech Stack

Detected or configured technology stack:
- Frontend framework
- Backend framework
- Database
- Styling
- Testing framework
- etc.

### Key Files (Session 780)

Important files that agents reference when generating code:

| Role | Example |
|------|---------|
| **main_entry** | `frontend/src/App.tsx` |
| **routes** | `frontend/src/routes.tsx` |
| **api_client** | `frontend/src/api/client.ts` |
| **models** | `core/models.py` |
| **urls** | `core/urls.py` |
| **settings** | `core/settings.py` |

### Coding Patterns (Session 780)

Detected conventions in the codebase:

| Pattern | Example Description |
|---------|---------------------|
| **component_pattern** | PascalCase.tsx in components/ |
| **hook_pattern** | use*.ts in hooks/ |
| **api_pattern** | REST with axios, base URL from env |
| **test_pattern** | test_*.py in tests/ |

### Dependencies (Session 780)

Project dependencies grouped by category:

```
Frontend:
  react@18.2.0  tailwindcss@3.3.0  axios@1.6.0  ...

Backend:
  django@5.0  djangorestframework@3.14  celery@5.3  ...
```

### Import Aliases (Session 780)

Path shortcuts configured in the project:

```
@/components  →  src/components
@/utils       →  src/utils
@/api         →  src/api
```

### Directory Map (Session 780)

What each directory is for:

| Directory | Purpose |
|-----------|---------|
| `frontend/src/components` | Reusable UI components |
| `frontend/src/pages` | Route page components |
| `frontend/src/hooks` | Custom React hooks |
| `core/agents` | AI agent implementations |
| `core/services` | Business logic services |

### Body Health

Real-time connection to the AI Body health system showing:
- Overall health score (0-100%)
- Status (healthy/degraded/critical)
- 9 body system indicators (Heart, Lungs, Circulatory, Spine, Immune, Digestive, Muscular, Brain, Skin)

---

## Files Tab

Browse and view files in the workspace.

### File Tree

- Hierarchical view of directories and files
- Click directories to expand/collapse
- Click files to view content

### File Content

- Syntax-highlighted code display
- File size indicator
- Truncation warning for files >100KB
- **View History** button to see all operations on the file

### File History Modal

Shows all operations performed on the selected file with:
- Operation type (create/modify/delete)
- Agent that performed it
- Timestamp
- Success/failure status
- Diff view capability

---

## Git Tab

Manage git operations with body governance integration.

### Git Status

| Metric | Description |
|--------|-------------|
| **Branch** | Current git branch |
| **Modified Files** | Files changed but not staged |
| **Staged Files** | Files ready to commit |
| **Deleted Files** | Files marked for deletion |
| **Untracked Files** | New files not in git |

### Changed Files List

Visual list with status indicators:
- **A** (green): Added/staged
- **M** (amber): Modified
- **D** (red): Deleted
- **?** (gray): Untracked

### Actions

- **Refresh Status**: Update git status
- **New Commit**: Create a commit (with body governance check)
- **New Branch**: Create a new branch from current HEAD

### Body Governance

If body systems are compromised:
- Warning banner displayed
- Operations may be blocked
- Heart icon animates to indicate restricted state

---

## Operations Tab

Complete audit trail of all workspace operations.

### Filtering

Search by file path or agent name.

### Operation Cards

Each operation shows:
- **Type icon**: Create (green +), Modify (amber code), Delete (red trash), Commit (purple branch)
- **File path**: The affected file
- **Agent**: Link to the agent that performed the operation
- **Timestamp**: When it was performed
- **Execution time**: How long it took (e.g., `45ms`)
- **Status badge**: Success (green) or Failed (red)
- **Review status**: Approved/Rejected/Pending

### Actions per Operation

- **View Content**: View the file content after the operation
- **Show Diff**: Toggle unified diff view
- **Rollback**: Restore to previous state (if available)

### Rolled Back Operations

Rolled-back operations appear dimmed with a "Rolled Back" badge.

---

## Reviews Tab

Human-in-the-loop approval for critical operations.

### When Reviews Are Required

Reviews are required when:
- Workspace has `require_human_review` enabled
- Operation affects protected paths
- Body governance flags the operation

### Review Actions

- **Approve**: Apply the operation
- **Reject**: Discard the operation

### Review Workflow

1. Agent proposes a file change
2. Operation is stored with `pending_review=True`
3. Appears in Reviews tab with badge count
4. Human reviews the diff
5. Human approves or rejects
6. If approved, changes are applied

---

## Project Understanding (Context)

The workspace context is a cached understanding of the project structure that agents use to make intelligent decisions about where to place code.

### How It Works

1. **Scanning**: When you scan a workspace, the system analyzes:
   - Directory structure
   - File types and counts
   - Dependencies (package.json, requirements.txt, etc.)
   - Import aliases (tsconfig.json paths)
   - Naming patterns

2. **Storage**: Context is cached in `WorkspaceContext` model

3. **Agent Usage**: When an agent needs to write code, it receives:
   - The file tree
   - Key files for reference
   - Coding patterns to follow
   - Directory purposes to know where to put files

### Context Fields

| Field | Description | Example |
|-------|-------------|---------|
| `file_tree` | Directory → file mapping | `{"src/components": ["Button.tsx", "Modal.tsx"]}` |
| `key_files` | Important reference files | `{"main_entry": "App.tsx"}` |
| `coding_patterns` | Detected conventions | `{"hook_pattern": "use*.ts in hooks/"}` |
| `dependencies` | Package versions | `{"frontend": {"react": "18.2.0"}}` |
| `import_aliases` | Path shortcuts | `{"@/components": "src/components"}` |
| `directory_purposes` | Folder descriptions | `{"src/pages": "Route page components"}` |

---

## Body Health Integration

The Workspace is the SKIN of the AI Body. It's connected to the health monitoring system.

### Health-Aware Operations

- Operations check body health before executing
- If systems are degraded, operations may be warned or blocked
- Visual indicators show current health status

### Body Systems Shown

| Emoji | System | Healthy State |
|-------|--------|---------------|
| ❤️ | Heart | healthy |
| 🫁 | Lungs | healthy |
| 🩸 | Circulatory | flowing |
| 🦴 | Spine | aligned |
| 🛡️ | Immune | protected |
| 🍽️ | Digestive | healthy |
| 💪 | Muscular | strong/fit |

### Governance Rules

The `useBodyGovernance()` hook checks:
- `canWriteFile`: Can the agent write to files?
- If body health is critically low, file writes are blocked
- Warnings are shown for degraded states

---

## Security & Permissions

### Workspace Permissions

| Permission | Default | Description |
|------------|---------|-------------|
| `allow_file_write` | true | Create/modify files |
| `allow_file_delete` | false | Delete files (dangerous) |
| `allow_command_execution` | true | Run shell commands |
| `allow_git_operations` | true | Perform git operations |

### Protected Paths

Certain paths can be protected from agent modification:
- `.env` files
- `secrets/` directories
- Credential files

Configure via the workspace settings.

### Human Review

Enable `require_human_review` to force all operations through the Reviews tab.

---

## API Reference

### Workspace Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/workspaces/` | List all workspaces |
| POST | `/api/workspaces/` | Register new workspace |
| GET | `/api/workspaces/{id}/` | Get workspace details |
| PATCH | `/api/workspaces/{id}/` | Update workspace settings |
| DELETE | `/api/workspaces/{id}/` | Delete workspace |
| POST | `/api/workspaces/{id}/activate/` | Set as active |
| POST | `/api/workspaces/{id}/scan/` | Rescan workspace |
| GET | `/api/workspaces/{id}/files/` | Browse files |
| GET | `/api/workspaces/{id}/file/?path=...` | Read file content |
| POST | `/api/workspaces/{id}/write/` | Write file |
| GET | `/api/workspaces/{id}/git-status/` | Get git status |
| POST | `/api/workspaces/{id}/git-commit/` | Create commit |
| POST | `/api/workspaces/{id}/git-branch/` | Create branch |
| GET | `/api/workspaces/{id}/operations/` | List operations |
| GET | `/api/workspaces/{id}/stats/` | Get statistics |
| GET | `/api/workspaces/active/` | Get active workspace |
| GET | `/api/workspaces/dashboard/` | Dashboard overview |

### Operation Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/workspace-operations/` | List all operations |
| GET | `/api/workspace-operations/{id}/` | Get operation details with diff |
| POST | `/api/workspace-operations/{id}/rollback/` | Rollback operation |
| POST | `/api/workspace-operations/{id}/review/` | Approve/reject operation |
| GET | `/api/workspace-operations/pending-reviews/` | Get all pending reviews |

### Stats Response Structure

```json
{
  "workspace_id": "uuid",
  "workspace_name": "my-project",
  "totals": {
    "operations": 156,
    "files_written": 89,
    "commits": 23
  },
  "last_24h": {
    "operations": 12,
    "successful": 11,
    "failed": 1
  },
  "last_7d": {
    "operations": 45,
    "by_type": {"file_create": 20, "file_modify": 15, "git_commit": 10},
    "by_agent": {"ContentWriterAgent": 15, "CodeGeneratorAgent": 12, ...}
  },
  "pending_reviews": 2,
  "rollback_available": 34,
  "project": {
    "total_files": 1234,
    "total_directories": 89,
    "total_lines_of_code": 45678,
    "file_types": {".py": 234, ".tsx": 89, ...},
    "last_scanned": "2026-01-19T..."
  }
}
```

---

## Troubleshooting

### "No Active Workspace"

**Cause**: No workspace is selected or registered.

**Solution**:
1. Click "Select Workspace"
2. Choose an existing workspace or register a new one

### "Authentication Required"

**Cause**: Session expired or not logged in.

**Solution**: Log in at `/login`

### "File Writing Disabled"

**Cause**: Workspace has `allow_file_write=False`.

**Solution**: Update workspace settings to enable file writing.

### "Operation Blocked" (Body Governance)

**Cause**: Body health is critically low.

**Solution**:
1. Check Body Health page
2. Resolve system issues
3. Retry the operation

### Empty Context Sections

**Cause**: Workspace hasn't been scanned yet.

**Solution**: Click the "Scan" button to analyze the workspace.

### Git Operations Failing

**Cause**: Not a git repository or git not installed.

**Solution**:
1. Initialize git: `git init` in project directory
2. Ensure git is installed and in PATH

### Rollback Unavailable

**Cause**: Operation doesn't support rollback (e.g., command execution).

**Solution**: Only file operations can be rolled back. For other operations, manually revert.

---

## Related Documentation

- [SKIN Layer Architecture](/docs/designs/SKIN_LAYER_ARCHITECTURE.md)
- [Body Systems Reference](/docs/body/BODY_SYSTEMS_REFERENCE.md)
- [Database Model Reference](/docs/DATABASE_MODEL_REFERENCE.md)
- [Agent Documentation](/docs/AGENTS.md)

---

**Last Updated**: Session 780 | January 19, 2026
