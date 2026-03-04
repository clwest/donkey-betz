# Code Runner (Beta) — v0

**Status:** Implemented (v0)
**Operation:** VIP Launchpad (OVL)
**Security:** Admin-only, VIP-denied, workspace-restricted

## Overview

The Code Runner allows admin users to dispatch code-agent tasks against the
`mobile/` workspace from the mobile app. v0 supports dry-run analysis and
intent-logged apply mode. A future release will wire up a real code execution
engine for apply mode.

## Architecture

```
Mobile Screen  →  POST /api/v1/code/run/
                     ↓
               CodeRun model (PostgreSQL)
                     ↓
              Background thread spawns:
              python manage.py run_code_agent
                     ↓
              stdout captured → log_lines (JSONField)
                     ↓
Mobile polls  ←  GET /api/v1/code/status/<id>/
              ←  GET /api/v1/code/logs/<id>/
```

## Backend

### Model: `CodeRun`

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | UnifiedBaseModel PK |
| created_by | FK(User) | Admin who initiated |
| mode | CharField | `dry_run` or `apply` |
| task | TextField | The task prompt |
| status | CharField | `queued`/`running`/`completed`/`failed` |
| workspace | CharField | Always `mobile` (v0) |
| started_at | DateTimeField | Set when thread starts |
| finished_at | DateTimeField | Set on completion/failure |
| exit_code | IntegerField | Process exit code |
| log_lines | JSONField | List of stdout/stderr lines |
| created_at | DateTimeField | Auto from UnifiedBaseModel |

File: `core/models_code_runner.py`
Migration: `core/migrations/0297_code_runner_model.py`

### API Endpoints

All endpoints require `IsAdminUser` permission (`is_staff=True`).

#### POST `/api/v1/code/run/`

Start a new code run.

**Request:**
```json
{
  "task": "Add error boundary to SettingsScreen",
  "mode": "dry_run"
}
```

**Response (201):**
```json
{
  "run_id": "uuid-here",
  "status": "queued",
  "mode": "dry_run"
}
```

**Error (409):** Another run is already active.

#### GET `/api/v1/code/status/<run_id>/`

**Response:**
```json
{
  "run_id": "uuid",
  "status": "completed",
  "mode": "dry_run",
  "workspace": "mobile",
  "started_at": "2026-03-03T...",
  "finished_at": "2026-03-03T...",
  "exit_code": 0,
  "created_at": "2026-03-03T..."
}
```

#### GET `/api/v1/code/logs/<run_id>/`

**Response:**
```json
{
  "run_id": "uuid",
  "lines": ["line1", "line2", "..."],
  "total_lines": 42,
  "truncated": false,
  "status": "completed"
}
```

Returns last 200 lines. `truncated: true` if total exceeds 200.

### Management Command

```bash
python manage.py run_code_agent \
  --workspace ./mobile \
  --mode dry_run \
  --task "Add error boundary" \
  --run-id <uuid>
```

Workspace allowlist: `mobile/`, `./mobile` only.

### Security

| Layer | Protection |
|-------|-----------|
| DRF permission | `IsAdminUser` (requires `is_staff=True`) |
| VIP deny | Defensive check for `platform_role == 'vip_demo'` |
| Workspace | Allowlist enforced in management command |
| Apply mode | v0 logs intent only, no code execution |
| Secrets | Regex redaction of API keys, tokens, AWS keys in log output |
| Concurrency | One active run at a time (409 on conflict) |
| Runtime cap | 600 seconds max, killed with SIGKILL on timeout |

## Mobile

### Files

- `mobile/src/api/codeRunner.ts` — API client with Zod validation
- `mobile/src/screens/CodeRunnerScreen.tsx` — Full screen UI
- `mobile/src/navigation/screenRegistry.ts` — Registered as `/code-runner`

### Screen Features

- Admin gate: blocks non-admin users
- VIP gate: blocks demo mode users
- Task input with mode selector (dry_run default)
- Apply confirmation: must type "APPLY" to confirm
- Status chip with color coding (queued/running/completed/failed)
- Log viewer with 1-second polling and auto-scroll
- Copy logs to clipboard
- Error handling for 403/409 responses

### Navigation

Route registered in app manifest (`core/views_app_manifest.py`):
```python
{'path': '/code-runner', 'label': 'Code Runner', 'authRequired': True, 'roles': ['admin'], 'category': 'admin'}
```

Only visible to admin users (filtered by RBAC in manifest endpoint).

## v0 Limitations

1. **Apply mode** logs intent only — no real code modifications
2. **Workspace** locked to `mobile/` — no other directories
3. **Execution** uses background thread, not Celery
4. **No WebSocket** — polling-based log updates (1s interval)

## Future Work

- Wire real code execution engine for apply mode
- Move to Celery task for better lifecycle management
- Add WebSocket for real-time log streaming
- Support additional workspaces (with governance approval)
- Add run history and diff viewer
