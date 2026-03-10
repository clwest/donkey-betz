# Remote Code Worker — Contract Specification

**Version:** 0.2 (Reviewed)
**Date:** 2026-03-08
**Authors:** Claude Code + Rigby (PA)
**Conversation:** pa-d6e219f40a1b

---

## 1. Overview

The Remote Code Worker is an ephemeral Railway service that executes code tasks (implement feature, fix bug, run tests) against a GitHub repo and produces a PR with results. ChatUI is the sole HITL surface.

---

## 2. CodeJob — Input Schema

```json
{
  "repo_slug": "clwest/donkey-betz-platform",
  "ref": "dev",
  "task_prompt": "Add endpoint /api/v1/health/extended returning version + db connectivity",
  "acceptance_criteria": [
    "Endpoint returns JSON with version and db_ok fields",
    "Tests pass"
  ],
  "test_command": null,
  "lint_command": null,
  "conversation_id": "pa-d6e219f40a1b",
  "priority": "normal",
  "max_runtime_seconds": 600
}
```

### Field Definitions

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `repo_slug` | string | yes | — | GitHub `owner/repo`. Must be in DB allowlist. |
| `ref` | string | no | repo default branch | Branch/tag/SHA to checkout |
| `base_branch` | string | no | repo default branch | PR target branch (may differ from `ref` for hotfixes) |
| `task_prompt` | string | yes | — | Natural language task description |
| `acceptance_criteria` | string[] | no | [] | Machine-checkable success conditions |
| `test_command` | string | no | auto-detect | Override test command |
| `lint_command` | string | no | auto-detect | Override lint command |
| `conversation_id` | string | no | null | PA conversation to post results to |
| `priority` | enum | no | "normal" | "low" / "normal" / "high" |
| `max_runtime_seconds` | int | no | 600 | Wall-clock timeout (max 1800) |

---

## 3. CodeJob — Output Schema (Artifacts)

```json
{
  "job_id": "uuid",
  "status": "succeeded",
  "branch": "ccw/abc123-health-extended",
  "pr_url": "https://github.com/clwest/donkey-betz-platform/pull/1450",
  "pr_number": 1450,
  "diff_stats": {
    "files_changed": 3,
    "insertions": 47,
    "deletions": 2
  },
  "test_result": {
    "command": "python manage.py test core.tests.test_health_extended",
    "exit_code": 0,
    "passed": 5,
    "failed": 0,
    "skipped": 0,
    "duration_seconds": 12.3,
    "output_tail": "... last 50 lines ..."
  },
  "lint_result": {
    "command": "ruff check .",
    "exit_code": 0,
    "issues": 0
  },
  "handoff_summary": "## What Changed\n- Added /api/v1/health/extended ...",
  "execution": {
    "started_at": "2026-03-08T21:15:00Z",
    "completed_at": "2026-03-08T21:18:42Z",
    "duration_seconds": 222,
    "steps_completed": ["clone", "branch", "implement", "test", "lint", "push", "pr"]
  },
  "error": null
}
```

### Status Values

| Status | Description |
|--------|-------------|
| `queued` | Job accepted, waiting for worker |
| `cloning` | Shallow-cloning repo |
| `implementing` | LLM generating changes |
| `testing` | Running test suite |
| `linting` | Running lint/format |
| `pushing` | Pushing branch + opening PR |
| `succeeded` | PR opened, tests passed |
| `failed` | Pipeline ran but job outcome failed (tests failed, lint failed, PR rejected) |
| `error` | Infrastructure/runner failure (clone auth, network, OOM, timeout, internal exception) |
| `cancelled` | Cancelled by user |

---

## 4. API Endpoints

### Create Job
```
POST /api/code-jobs/
Authorization: Token <pa_token>
Content-Type: application/json

{
  "repo_slug": "clwest/donkey-betz-platform",
  "task_prompt": "Add health/extended endpoint",
  ...
}

Response 201:
{
  "job_id": "uuid",
  "status": "queued",
  "created_at": "2026-03-08T21:15:00Z"
}
```

### Get Job Status
```
GET /api/code-jobs/{job_id}/
Authorization: Token <pa_token>

Response 200:
{
  "job_id": "uuid",
  "status": "testing",
  "progress": 0.6,
  "current_step": "testing",
  "steps_completed": ["clone", "branch", "implement"],
  "started_at": "...",
  "elapsed_seconds": 45
}
```

### Get Job Logs (streaming-ready)
```
GET /api/code-jobs/{job_id}/logs/?offset=0
Authorization: Token <pa_token>

Response 200:
{
  "job_id": "uuid",
  "log_lines": [
    {"ts": "...", "level": "info", "step": "clone", "msg": "Cloning clwest/donkey-betz-platform@dev..."},
    {"ts": "...", "level": "info", "step": "clone", "msg": "Clone complete (shallow, 2.1s)"},
    ...
  ],
  "has_more": true,
  "next_offset": 25
}
```

### Cancel Job
```
POST /api/code-jobs/{job_id}/cancel/
Authorization: Token <pa_token>

Response 200:
{"job_id": "uuid", "status": "cancelled"}
```

### List Jobs
```
GET /api/code-jobs/?status=succeeded&limit=10
Authorization: Token <pa_token>
```

---

## 5. Test Command Auto-Detection

Priority order (first match wins):

| Signal | Test Command | Notes |
|--------|-------------|-------|
| `pytest.ini` or `pyproject.toml [tool.pytest]` | `pytest` | Most Django projects |
| `manage.py` exists | `python manage.py test` | Django fallback |
| `pnpm-lock.yaml` | `pnpm test` | Node/pnpm |
| `yarn.lock` | `yarn test` | Node/yarn |
| `package-lock.json` | `npm test` | Node/npm |
| `Cargo.toml` | `cargo test` | Rust |
| `go.mod` | `go test ./...` | Go |
| `.dbz/code_worker.yml` | value of `test_command` | Repo-local override |
| DB `CodeRepoConfig.test_command` | stored value | DB override (highest priority) |

### Config Precedence (highest wins)

1. **DB `CodeRepoConfig`** — authoritative allowlist + command overrides
2. **Repo-local `.dbz/code_worker.yml`** — optional, only read if repo is allowlisted in DB
3. **Auto-detect** — file-presence heuristics from table above

### Command Allowlist (hardcoded safe set)

Only these commands are permitted for test/lint execution:
`pytest`, `python manage.py test`, `pnpm test`, `npm test`, `yarn test`, `cargo test`, `go test ./...`, `ruff check`, `ruff format --check`, `eslint`, `prettier --check`

No arbitrary `custom_command` field is exposed via API. DB overrides are restricted to this allowlist.

---

## 6. DB Models

### CodeJob

```python
class CodeJobStatus(models.TextChoices):
    QUEUED = 'queued'
    CLONING = 'cloning'
    IMPLEMENTING = 'implementing'
    TESTING = 'testing'
    LINTING = 'linting'
    PUSHING = 'pushing'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    ERROR = 'error'
    CANCELLED = 'cancelled'

class CodeJob(UnifiedBaseModel):
    # Ownership
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='code_jobs')
    conversation_id = models.CharField(max_length=100, blank=True, db_index=True)

    # Input
    repo_slug = models.CharField(max_length=200, db_index=True)
    ref = models.CharField(max_length=200, default='main')
    base_branch = models.CharField(max_length=200, blank=True, help_text="PR target branch; defaults to repo default")
    task_prompt = models.TextField()
    acceptance_criteria = models.JSONField(default=list, blank=True)
    test_command = models.CharField(max_length=500, blank=True)
    lint_command = models.CharField(max_length=500, blank=True)
    priority = models.CharField(max_length=10, default='normal')
    max_runtime_seconds = models.IntegerField(default=600)

    # Execution
    status = models.CharField(max_length=20, choices=CodeJobStatus.choices, default=CodeJobStatus.QUEUED, db_index=True)
    progress = models.FloatField(default=0.0)
    current_step = models.CharField(max_length=30, blank=True)
    branch_name = models.CharField(max_length=200, blank=True)
    commit_sha = models.CharField(max_length=40, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)

    # Output
    pr_url = models.URLField(blank=True)
    pr_number = models.IntegerField(null=True, blank=True)
    diff_stats = models.JSONField(default=dict, blank=True)
    test_result = models.JSONField(default=dict, blank=True)
    lint_result = models.JSONField(default=dict, blank=True)
    handoff_summary = models.TextField(blank=True)

    # Error
    error_message = models.TextField(blank=True)
    error_type = models.CharField(max_length=100, blank=True)
    failure_reason_code = models.CharField(max_length=50, blank=True, help_text="TESTS_FAILED, LINT_FAILED, CLONE_AUTH, TIMEOUT, OOM, etc.")

    # Celery
    celery_task_id = models.CharField(max_length=100, blank=True, db_index=True)

    # Learning
    user_rating = models.IntegerField(null=True, blank=True)
    user_feedback = models.TextField(blank=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['repo_slug', 'status']),
        ]

    @property
    def is_terminal(self):
        return self.status in (CodeJobStatus.SUCCEEDED, CodeJobStatus.FAILED,
                               CodeJobStatus.ERROR, CodeJobStatus.CANCELLED)
```

### CodeRepoConfig (Allowlist)

```python
class CodeRepoConfig(UnifiedBaseModel):
    repo_slug = models.CharField(max_length=200, unique=True)
    default_branch = models.CharField(max_length=100, default='main')
    allowed = models.BooleanField(default=True)
    test_command = models.CharField(max_length=500, blank=True)
    lint_command = models.CharField(max_length=500, blank=True)
    install_command = models.CharField(max_length=500, blank=True)
    max_runtime_seconds = models.IntegerField(default=600)
    max_patch_files = models.IntegerField(default=50)
    github_installation_id = models.CharField(max_length=100, blank=True)
    path_filters = models.JSONField(default=list, blank=True, help_text="Allowed subdirs for monorepo")

    class Meta:
        app_label = 'core'
```

### CodeJobLog (Chunked Logs)

```python
class CodeJobLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    job = models.ForeignKey(CodeJob, on_delete=models.CASCADE, related_name='logs')
    sequence = models.IntegerField(db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10, default='info')
    step = models.CharField(max_length=30)
    message = models.TextField()

    class Meta:
        app_label = 'core'
        ordering = ['sequence']
        indexes = [
            models.Index(fields=['job', 'sequence']),
        ]
```

---

## 7. Celery Task Routing

```python
# In CELERY_TASK_ROUTES (core/settings.py)
'core.tasks.execute_code_job': {'queue': 'code_jobs'},

# Procfile addition
code-worker: celery -A core worker -l info --pool=prefork -c 1 --max-tasks-per-child=1 --max-memory-per-child=400000 -Q code_jobs
```

- `max-tasks-per-child=1`: Each job gets a fresh process (no state leakage between repos)
- `max-memory-per-child=400000`: 400MB cap (repo clone + test runner)
- Concurrency 1: One job at a time per instance

---

## 8. Worker Execution Pipeline

```
1. QUEUED     → Validate repo_slug against CodeRepoConfig allowlist
2. CLONING    → git clone --depth=1 --branch={ref} {repo_url} /tmp/{job_id}/
3. BRANCHING  → git checkout -b ccw/{job_id_short}-{slug}
4. IMPLEMENTING → [LLM generates patch / Claude Code executes task]
5. TESTING    → Run auto-detected or configured test command
6. LINTING    → Run lint/format (optional, non-blocking for MVP)
7. PUSHING    → git push origin ccw/{job_id_short}-{slug}
8. PR         → GitHub API: create PR targeting {ref}
9. SUCCEEDED  → Store artifacts, post to conversation_id
```

Each step updates `status`, `progress`, `current_step` and appends to `CodeJobLog`.

---

## 9. Security Boundaries

| Boundary | Enforcement |
|----------|-------------|
| Repo allowlist | `CodeRepoConfig.allowed=True` checked before clone |
| No arbitrary commands | Only auto-detected or DB-configured commands run |
| GitHub auth | GitHub App installation tokens (short-lived, scoped) |
| No prod DB access | Worker env has NO `DATABASE_URL` for prod — only its own job tracking DB or API callbacks |
| Timeout | Wall-clock `max_runtime_seconds` enforced via `signal.alarm` or ThreadPoolExecutor |
| Resource cap | Railway service memory limit + `max-memory-per-child` |
| No deploy capability | Worker can only push branches + create PRs, never merge or deploy |
| Secret isolation | Worker Railway service has only: `GITHUB_APP_*`, `REDIS_URL`, `DATABASE_URL` (job DB) |

---

## 10. PA Tool Integration

```python
# New PA tool schema
{
    "name": "code_job_tool",
    "description": "Submit and manage remote code jobs",
    "parameters": {
        "action": {"type": "string", "enum": ["submit", "status", "logs", "cancel", "list"]},
        "repo_slug": {"type": "string"},
        "task_prompt": {"type": "string"},
        "job_id": {"type": "string"},
        ...
    }
}
```

This allows Rigby to submit, monitor, and retrieve code job results directly from ChatUI.

---

## 11. Implementation Order

1. **Models**: `CodeJob`, `CodeRepoConfig`, `CodeJobLog` → migration
2. **API Views**: `views_code_jobs.py` → 5 endpoints
3. **Celery Task**: `execute_code_job` in `tasks.py` → route to `code_jobs` queue
4. **Worker Pipeline**: Clone → branch → implement → test → push → PR
5. **PA Tool**: `code_job_tool` schema + handler in `tool_dispatcher.py`
6. **Procfile**: Add `code-worker` service
7. **GitHub App**: Create + install + store secrets on Railway
8. **Acceptance Test**: End-to-end from ChatUI
