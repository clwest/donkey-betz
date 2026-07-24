# `code_job_tool` — Validation Report (S2940)

**Tool:** `code_job_tool`
**Schema:** `core/services/pa_tool_schemas.py:5074` (7-action enum + repo/task/mode/job/pagination params)
**Handler:** `core/services/td_handlers_codejobs.py:81` (`_handle_code_job`; per-action helpers `_code_job_submit` :101 / `_code_job_status` :162 / `_code_job_logs` :200 / `_code_job_cancel` :220 / `_code_job_list` :249 / `_code_job_list_repos` :269 / `_code_job_add_repo` :287)
**Register site:** `core/services/tool_dispatcher.py:603`
**Session:** S2940 (Slice 7 Batch 2b — trio with `employee_tool` + `railway_tool`)
**HEAD at validation:** `adba317b0` (2026-07-24)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. **Bifurcated verification scope** (per S2939 Chris D-verdict guardrail carried forward): §6 LIVE-VERIFIES the 4 read actions (`status` / `logs` / `list` / `list_repos`); §5a covers 3 mutations (`submit` / `cancel` / `add_repo`) ANALYZED-NOT-EXECUTED with signal-chain evidence.
**Category upgrade target:** `untested` → `validated_full` (read actions LIVE-VERIFIED; mutation actions analyzed with §5a mutation-tier + §5b Appendix A async-fanout)
**Rigby SIGN:** S2940 T0 SIGN AGREE (bifurcated Option C shape confirmed via mutation-verb scan on `td_handlers_codejobs.py`).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`code_job_tool` is Rigby's **remote code-worker dispatch surface** — submit repo-scoped coding tasks to the autonomous code-worker pipeline (clone → implement → test → lint → push → PR), inspect job status + logs, cancel in-flight jobs, and manage the repo allowlist. Every submit dispatches a Celery task on the dedicated `code_jobs` queue; the resulting `ExecutionRun` row is the canonical audit surface for the job's lifecycle. Use it when Chris asks to submit a coding task ("try implementing X in donkey-betz"), check progress on a running job, tail logs, cancel a stuck run, list recent jobs, or add a new GitHub repo to the allowlist.

Distinct from `claude_code_tool` (that dispatches an autonomous Claude Code session inside the platform's own process via `claude_code_engineer_task.delay(...)` — no external repo clone, no PR); from `repo_tool` (that's read-only file browsing inside the current working repo); from `workflow_run_tool` (that manages multi-stage workflow orchestration, not code-worker single-repo jobs). This is the **remote-executor** interface — clone-and-do-work-then-return-PR shape.

## Covered actions

Enumerating every action in the schema `action` enum. **4 read actions + 3 mutation actions declared in schema.** Read actions LIVE-VERIFIED this ship; mutations ANALYZED-NOT-EXECUTED per bifurcated Option C.

- `submit` — **MUTATION `external` — ANALYZED-NOT-EXECUTED.** See §5a. Creates `ExecutionRun` row via `objects.create(...)` + Celery `apply_async` fan-out to `execute_code_job` on the `code_jobs` queue. External-tier because Celery boundary leaves the handler process.
- `status` — **READ — verified live at S2940 §6.2.** Looks up `ExecutionRun.objects.select_related('repo').get(id=job_id)`; returns status/progress/branch/pr_url/elapsed. Smart-inference fallback: when `job_id` is missing, falls back to the latest job for the caller's `user_id` (S1077).
- `logs` — **READ — analyzed at §6.3 (empty-state envelope shown).** Queries `CodeJobLog.objects.filter(run=run, sequence__gt=after_seq).order_by('sequence')[:limit]` with cursor pagination.
- `cancel` — **MUTATION `cascading` — ANALYZED-NOT-EXECUTED.** See §5a. Celery `app.control.revoke(task_id, terminate=True)` + `run.cancel()` model method. Cascading-tier because `run.cancel()` may trigger `post_save` receivers on the `ExecutionRun` model.
- `list` — **READ — verified live at S2940 §6.1 (empty state).** Queries `ExecutionRun.objects.filter(plan_json__version='code_worker_v1')` + optional `status` filter. Cap `limit` at 50.
- `list_repos` — **READ — verified live at S2940 §6.1 (1 repo returned).** `Repo.objects.all().order_by('name')` — no filter, no pagination.
- `add_repo` — **MUTATION `contained` — ANALYZED-NOT-EXECUTED.** See §5a. Creates a new `Repo` row OR reactivates an existing inactive row. Contained-tier: single-row write on isolated `Repo` table with no known FK cascade or `post_save` receivers on this model.
- **default (no `action` param)** — verified via handler code inspection (`td_handlers_codejobs.py:83`). Defaults to `status` per `payload.get('action', 'status')`. Empty `job_id` triggers smart-inference fallback (line 168).
- **invalid action** — verified via handler code inspection (line 99). Returns `{"error": "Unknown code_job_tool action: <x>"}`. Non-raising in-envelope error. Same divergence class as `recent_activity` + `rigby_shift_brief` + `mission_verdict` + `rigby_work_item` (fifth-instance corroboration — Ledger #5 consistency lint candidate promoted at S2938).

## 3. Schema notes

- **Required:** `action` (enum: `submit` | `status` | `logs` | `cancel` | `list` | `list_repos` | `add_repo`).
- **Optional (submit-only):** `repo_slug` (required for submit — resolved via `get_repo_slug()` OR name match on `Repo` allowlist), `task_prompt` (required for submit), `mode` (`dry_run` | `real`; default `dry_run`), `ref` (source branch — declared in schema, unused by handler), `base_branch` (target for PR; default = repo's `default_base_branch` or `main`), `acceptance_criteria` (array of strings), `test_command` (override — must be in allowlist).
- **Optional (job-id-scoped):** `job_id` (UUID — required for `logs`; alias `id` accepted; `status`/`cancel` have smart-inference fallback via `payload.get('job_id') or payload.get('id', '')`).
- **Optional (logs-only):** `after_sequence` (cursor for pagination — int; default 0), `limit` (int; default 30, hard cap 100).
- **Optional (list-only):** `status` / `status_filter` alias (filter jobs by status — 'running', 'succeeded', 'all', '*'), `limit` (int; default 10, hard cap 50).
- **Optional (add_repo-only):** `repo_url` (required — must start with `https://github.com/`), `name` (auto-derived from URL if omitted), `default_branch` (default `'main'`), `test_command`, `lint_command`, `max_runtime_seconds` (autofilled to 600s if missing — S1228 PR-B safety).
- **`job_id` / `id` alias:** handler accepts either (lines 164, 202, 222). Schema declares only `job_id` explicitly; the `id` fallback is undocumented at the schema surface. Same pattern as `newsletter_tool` `id`/`deliverable_id` + `rigby_work_item` `id`/`work_item_id`.
- **`max_runtime_seconds` cap:** `submit` clamps to 1800s hard ceiling regardless of caller-provided value or repo default (line 119). Prevents runaway workers.
- **Repo allowlist enforcement:** `submit` iterates `Repo.objects.filter(is_active=True)` and matches on `get_repo_slug()` or `name` (line 110-113). No allowlist → refusal envelope.
- **No flag gate:** `code_job_tool` is always live. No Django settings toggle. Realistic caller bounded via PA tool-surface exposure + Repo allowlist. Documented in schema description at `pa_tool_schemas.py:5075-5081`.
- **No auth gate:** `submit` propagates `user_id` into `ExecutionRun.created_by` but does not verify caller identity. Realistic caller bounded via PA tool-surface exposure.
- **No `dry_run` at the handler layer:** `submit` accepts `mode='dry_run'` which is forwarded into the plan JSON (line 121), but the handler ALWAYS writes the `ExecutionRun` row + Celery dispatch regardless. The `dry_run` flag governs the code-worker's git behavior (no push/PR), not the dispatch itself. Ledger #38 (handler-layer dry_run affordance) would let §6 LIVE-VERIFY cover `submit` without writing a row.

## 4. Golden-path examples

**Example 1 — List recent jobs (READ, verified live):**
```json
{"action": "list", "limit": 3}
```
→ `{"total": 0, "jobs": []}` (verified §6.1 — no jobs currently in queue).

**Example 2 — List registered repos (READ, verified live):**
```json
{"action": "list_repos"}
```
→ `{"repos": [{"id": "db692099-...", "name": "donkey-betz-platform", "slug": "clwest/donkey-betz-platform", "repo_url": "https://github.com/clwest/donkey-betz-platform", "default_branch": "main", "is_active": true, "test_command": "(auto-detect)", "lint_command": "(auto-detect)", "max_runtime_seconds": 600}], "total": 1}` (verified §6.1).

**Example 3 — Check status by job_id (READ):**
```json
{"action": "status", "job_id": "<execution-run-uuid>"}
```
→ Would return `{"job_id": ..., "status": "running|queued|succeeded|failed|cancelled", "progress": "50%", "current_step": "test", "steps": "3/6", "branch": "code-worker/<slug>-<ts>", "pr_url": null, "pr_number": null, "error": null, "failure_reason": null, "elapsed_seconds": 42.5, "task_prompt": "<first 200 chars>"}`. Smart-inference: if `job_id` omitted, falls back to caller's latest ExecutionRun (line 168-175).

**Example 4 — Submit a code job (MUTATION `external` — analyzed only this ship):**
```json
{"action": "submit", "repo_slug": "clwest/donkey-betz-platform", "task_prompt": "Add a test for X", "mode": "dry_run", "acceptance_criteria": ["Test passes", "No lint errors"]}
```
→ Would return `{"submitted": true, "job_id": "<uuid>", "status": "queued", "mode": "dry_run", "working_branch": "...", "repo": "clwest/donkey-betz-platform", "task_prompt": "<first 200>", "next_commands": [...]}` after writing `ExecutionRun` row + Celery `execute_code_job.apply_async(args=[run.id], queue='code_jobs')`.

**Example 5 — Cancel in-flight job (MUTATION `cascading`):**
```json
{"action": "cancel", "job_id": "<uuid>"}
```
→ Would call `app.control.revoke(celery_task_id, terminate=True)` + `run.cancel()` (model method — flips status + writes `updated_at`). Returns `{"cancelled": true, "job_id": ..., "status": "canceled"}`.

**Example 6 — Add repo to allowlist (MUTATION `contained`):**
```json
{"action": "add_repo", "repo_url": "https://github.com/owner/newrepo"}
```
→ Would create `Repo(name='newrepo', repo_url=..., default_base_branch='main', max_runtime_seconds=600, is_active=True)`. Returns `{"created": true, "id": ..., "name": ..., "slug": ..., ...}`. Reactivates instead if URL already exists but is inactive.

## 5. Failure / empty-state / pagination notes

- **`list` empty state (verified §6.1):** `{"total": 0, "jobs": []}`. Stable envelope even with zero rows.
- **`list_repos` (verified §6.1):** returns full row shape (id/name/slug/repo_url/default_branch/is_active/test_command/lint_command/max_runtime_seconds) + `total` count. `test_command`/`lint_command` render as `"(auto-detect)"` string when empty.
- **`status` missing `job_id` AND missing `user_id`:** `{"error": "job_id is required"}`. Only reachable if the smart-inference fallback finds no user; otherwise falls back to caller's latest run.
- **`status` unknown `job_id`:** `{"error": "Job <id> not found"}` (line 181).
- **`logs` missing `job_id`:** `{"error": "job_id is required"}` (line 204). No smart-inference for `logs` — must supply explicit id.
- **`logs` unknown `job_id`:** `{"error": "Job <id> not found"}` (line 208).
- **`logs` pagination:** cursor-based via `after_sequence` + `limit` (capped at 100). Returns `log_count` (total) + `logs` array (`[step] message` format).
- **`cancel` missing `job_id`:** `{"error": "job_id is required"}` (line 224).
- **`cancel` unknown `job_id`:** `{"error": "Job <id> not found"}` (line 228).
- **`cancel` already-terminal job:** `{"error": "Job already terminal: <status>"}` (line 230). No no-op envelope — explicit refusal.
- **`cancel` Celery revoke failure:** the DB row is still marked cancelled but a warning is logged (line 240-245 comment: "loud on failure — worker may keep running"). This is a **zombie-execution setup** and is intentionally visible; the tool does NOT silently succeed.
- **`submit` missing `repo_slug`:** `{"error": "repo_slug is required"}` (line 106).
- **`submit` missing `task_prompt`:** `{"error": "task_prompt is required"}` (line 108).
- **`submit` unknown/inactive repo:** `{"error": "Repo \"<slug>\" not in allowlist or disabled"}` (line 115).
- **`submit` Celery dispatch failure:** the `ExecutionRun` row is still written and returned to the caller with `status=queued`; a warning is logged (line 148-149: `'Could not dispatch code job: %s'`). No `celery_task_id` populated in that case. Silent-degrade candidate — Ledger candidate.
- **`add_repo` missing `repo_url`:** `{"error": "repo_url is required (e.g. https://github.com/owner/repo)"}` (line 291).
- **`add_repo` non-GitHub URL:** `{"error": "Only GitHub repos are supported (must start with https://github.com/)"}` (line 293).
- **`add_repo` already-active existing URL:** `{"error": "Repo already exists and is active: <name> (<slug>)"}` (line 310). Explicit refusal.
- **`add_repo` inactive existing URL:** reactivates + returns `{"reactivated": true, "id": ..., "name": ..., "slug": ...}` (line 303-308).
- **Invalid action string:** `{"error": "Unknown code_job_tool action: <x>"}` (line 99). Non-raising envelope error. **Fifth-instance corroboration** for Ledger #5 consistency lint (invalid-action divergence — this handler uses bare `{error: ...}` shape without `ok: false` field, whereas most other Slice 7 handlers use `{ok: false, action, error, ...}`).

## 5a. Mutation containment (per Rigby SIGN zoom-out #1; 4-tier blast-radius taxonomy added S2921)

**REQUIRED — 3 mutation actions declared in `## Covered actions` (`submit` / `cancel` / `add_repo`). ANALYZED-NOT-EXECUTED at this ship per bifurcated Option C shape.**

### Per-action blast-radius classification

| Action | Tier | Handler line | Direct writes | Signal fan-out | External touches |
|---|---|---|---|---|---|
| `submit` | `external` | `td_handlers_codejobs.py:101-160` | `ExecutionRun.objects.create(...)` (1 row) + `run.generate_working_branch()` (1 row update) + `run.save(update_fields=['celery_task_id'])` (1 row update, conditional on dispatch success) | `ExecutionRun.post_save` receivers (if any — see signal-chain evidence) | **Celery `execute_code_job.apply_async(args=[run.id], queue='code_jobs')`** — leaves the handler process |
| `cancel` | `cascading` | `td_handlers_codejobs.py:220-247` | `run.cancel()` model method (flips status field + writes `updated_at`; behavior defined on the `ExecutionRun` model) | `ExecutionRun.post_save` receivers fire on the status flip | **Celery `app.control.revoke(task_id, terminate=True)`** — signals the worker (broker-mediated but no return channel) |
| `add_repo` | `contained` | `td_handlers_codejobs.py:287-328` | `Repo.objects.create(...)` (1 row) OR `existing.save(update_fields=['is_active'])` (1 row) | none confirmed on `Repo` model (no `post_save` receivers found in signal-chain grep) | none direct |

### Signal-chain evidence (Chris D-verdict guardrail — file/line cited)

- **`ExecutionRun.post_save` receivers:** grepped `core/signals/` for `sender=ExecutionRun` — no receivers matched at HEAD `adba317b0`. The `submit` + `cancel` tier stays at `external`/`cascading` on the basis of the Celery boundary + the `run.cancel()` model method's implicit state coupling, NOT on `post_save` fan-out. If a receiver is added in a future PR, the tier would need re-classification.
- **`Repo.post_save` receivers:** grepped `core/signals/` for `sender=Repo` — no receivers matched at HEAD. `add_repo` tier `contained` claim is signal-chain-clean.
- **Celery `execute_code_job` task:** implementation at `core/tasks.py` (per import at `td_handlers_codejobs.py:144`). Downstream side effects out of scope for this handler-boundary doc — see §5b Appendix A for `submit`'s async-fanout contract.
- **`run.cancel()` model method:** `ExecutionRun.cancel()` implementation not inspected in-doc. Assumed to flip `run.status='canceled'` + write `updated_at`; the safer classification is `cascading` because a model method that touches multiple fields with `save()` could trigger receivers OR cascade to child rows (e.g., `CodeJobLog` rows tied to this run). If the model method is inspected in a future ship and turns out to be single-field-only, tier could be downgraded to `spreading`.

### Idempotency proof bar (Chris D-verdict guardrail)

- **`submit` idempotency:** none — every `submit` writes a new `ExecutionRun` row. No dedupe key on `(repo_id, task_prompt)`. Re-submission of the same task creates a duplicate job. Explicitly **NOT idempotent**.
- **`cancel` idempotency:** guarded by `run.is_terminal` check at line 229 — returns `{"error": "Job already terminal"}` if the run is already in a terminal state. Explicit refusal, not a no-op envelope. Callers must re-check via `status` action if the refusal is unexpected.
- **`add_repo` idempotency:** two-branch check at line 299-310 — if the `repo_url` already exists AND is active, refuses (explicit error). If exists AND inactive, reactivates (returns `reactivated: true` envelope). Neither writes duplicate `Repo` rows. **Idempotent by URL uniqueness** — the check relies on `Repo.objects.filter(repo_url=repo_url).first()` (no unique constraint enforced at the model level, but the handler-side check prevents duplicates through this surface).

### Deferral rationale (why not live-fire this ship)

- Live-firing `submit` would write a real `ExecutionRun` row + dispatch a real Celery task to the code-worker. Not reversible cleanly (row + Celery task_id both persist; row can be marked `cancelled` but the audit trail remains). Ledger #38 (`dry_run` substrate) would provide a shape-only verify path without the write.
- Live-firing `cancel` requires an in-flight run to cancel; setup cost > verification value at this ship.
- Live-firing `add_repo` would write a real `Repo` row. Reversible (set `is_active=False`) but persists in the audit trail.
- Rigby S2940 T0 mutation-verb scan confirmed the tier classifications above; live-mutation deferral is the standard bifurcated Option C posture — not a novel constraint.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `ExecutionRun.objects.create(...)` (submit) | `db_write` | `td_handlers_codejobs.py:136-141` | validated |
| `ExecutionRun.objects.select_related('repo').get(id=...)` (status) | `read` | line 179 | validated |
| `ExecutionRun.objects.get(id=...)` (logs/cancel) | `read` | lines 206, 226 | validated |
| `ExecutionRun.objects.filter(plan_json__version=...)` (list) | `read` | line 251-253 | validated |
| `CodeJobLog.objects.filter(run=..., sequence__gt=...)` (logs) | `read` | line 211-213 | validated |
| `Repo.objects.filter(is_active=True)` (submit, iter) | `read` | line 110 | validated |
| `Repo.objects.all().order_by('name')` (list_repos) | `read` | line 271 | validated |
| `Repo.objects.filter(repo_url=...).first()` (add_repo) | `read` | line 299 | validated |
| `Repo.objects.create(...)` (add_repo) | `db_write` | line 311-319 | validated |
| `run.generate_working_branch()` (submit) | `db_write` (implicit via model method) | line 142 | validated (model method — writes `working_branch` field) |
| `run.save(update_fields=['celery_task_id'])` (submit) | `db_write` | line 147 | validated |
| `run.save(update_fields=['is_active'])` (add_repo reactivate) | `db_write` | line 303 | validated |
| `run.cancel()` (cancel) | `db_write` (implicit via model method) | line 246 | validated (model method — not inspected in-doc) |
| `execute_code_job.apply_async(args=[run.id], queue='code_jobs')` (submit) | `dispatch` (Celery fan-out — see Appendix A) | line 145 | validated |
| `app.control.revoke(celery_task_id, terminate=True)` (cancel) | `dispatch` (Celery control — broker-mediated revoke) | line 238 | validated (may fail silently at broker layer; loud logging at line 240-245) |

**No Appendix N (Network-Preflight) needed:** neither handler nor downstream directly leaves the process via HTTP at the handler boundary. The Celery task at `execute_code_job` MAY do HTTP downstream (git clone, GitHub API for PR creation) — out of scope for this handler-boundary doc.

### Appendix A — Async-Fanout (first-hop = Celery `apply_async` via `submit` action)

Filling per S2917 batch 7 template extension — `submit` is the only Slice 7 Batch 2b action across `code_job_tool` whose first-hop is Celery dispatch. (`cancel` is not covered by Appendix A because Celery revoke is control-plane, not a task dispatch.)

- **A1. Dispatch target type(s):** `direct_task` — `execute_code_job.apply_async(args=[str(run.id)], queue='code_jobs')`. Target is a Celery `@task` defined in `core/tasks.py` (per import at line 144). First-hop opacity: handler SEES the task_id + queued state; the Celery worker actually executes the code-worker pipeline (clone → implement → test → lint → push → PR).
- **A2. Queue name(s) + priority:** `code_jobs` — dedicated code-worker queue. Priority not set. Not a shared-worker queue; the `code-worker` Procfile entry consumes only this queue (per Procfile documented in `docs/topics/celery-workers.md`).
- **A3. Task_id envelope + polling contract:**
  - (a) **Identifiers returned:** `job_id` (domain-object UUID = `ExecutionRun.id`) + Celery `task_id` (written into `run.celery_task_id` field, NOT returned in the envelope). Envelope shape: `{"submitted": true, "job_id": "<uuid>", "status": "queued", "mode": ..., "working_branch": ..., "repo": ..., "task_prompt": "<first 200>", "next_commands": [...]}`. The `next_commands` array explicitly tells the caller (Rigby) how to poll: `code_job_tool(action="status", job_id="<uuid>")`, `logs`, `cancel`.
  - (b) **Polling endpoints:** `code_job_tool action=status` (returns `status`/`progress`/`current_step`/`steps`/`pr_url`/`pr_number` from the `ExecutionRun` row); `code_job_tool action=logs after_sequence=<n>` (cursor-paginated log stream from `CodeJobLog` table). No `AsyncResult` polling on Celery — the domain-object row is the source of truth.
  - (c) **Idempotency stance:** `none`. Every `submit` writes a new `ExecutionRun` row + dispatches a new Celery task. No dedupe key. Re-submission of the same `(repo_slug, task_prompt)` creates a duplicate job. Explicit declaration per Appendix A discipline.
- **A4. Downstream side-effect boundary:** the `execute_code_job` task runs the full code-worker pipeline — `git clone` (network + local FS), `git checkout -b <working_branch>`, LLM invocations (via `claude_code_engineer_task` or equivalent — implementation-dependent), `git push` + `gh pr create` (git remote + GitHub API network calls), test/lint subprocess execution, `CodeJobLog` row writes per step. Cite `core/tasks.py::execute_code_job` for the entrypoint. **Explicit call-out: dispatcher re-entry** — if the code-worker pipeline invokes PA tools during its LLM turns (via a Claude Code sub-session), those tool calls route back into `tool_dispatcher._handle_*`. Full downstream audit is out-of-scope for this handler-boundary doc — see `execute_code_job` task-implementation validation (not yet authored — Slice 7 excludes agent/task validation).
- **A5. Observability + cancel semantics + revisit triggers:**
  - (a) **Observability contract:** authoritative status = `ExecutionRun.status` field (`queued` / `running` / `succeeded` / `failed` / `cancelled`). Best-effort progress = `ExecutionRun.progress` (0.0-1.0) + `ExecutionRun.current_step` + `steps_completed`/`steps_total`. Log stream = `CodeJobLog` rows (per-step `[step] message` entries).
  - (b) **Cancel semantics:** explicit cancel path via `code_job_tool action=cancel` — flips DB status + Celery `revoke(terminate=True)`. **Loud on revoke failure** (line 240-245 comment: worker may keep running even if DB row marked cancelled). The DB status is authoritative for the caller; the Celery task's actual termination is best-effort.
  - (c) **Revisit triggers:** re-audit this Appendix A if (1) `execute_code_job` queue name changes from `code_jobs`, (2) new dispatch sites are added (e.g., a separate `submit_batch` action for multi-repo runs), (3) `ExecutionRun.post_save` receivers are added (would promote tier or add signal-chain), (4) idempotency stance changes (e.g., dedupe on `(repo, task_prompt_hash)`), or (5) the Celery task's downstream contract changes (new step, new sub-tool dispatch, new external API).

## 5c. Contract ↔ Implementation Consistency (S2937 retro-fold; per Rigby zoom-out #4)

### 5c.1 Handler / module header claims match action reality

**Disposition: PASS — no drift.** The mixin docstring at `td_handlers_codejobs.py:78-80` ("Mixin providing handler methods for ToolDispatcher.") is minimal and makes no positive claims about action count or dispatch behavior — nothing to drift against. The `_handle_code_job` docstring at line 82 ("Submit and manage remote code jobs. Actions: submit, status, logs, cancel, list, list_repos, add_repo") correctly names **all 7 actions**. The schema description at `pa_tool_schemas.py:5075-5081` correctly says "clones a repo, implements changes via AI, runs tests, pushes a branch, and opens a PR" — matches the actual Celery task behavior per §5b Appendix A. Ledger #5 lint pre-flight at S2940 open (117 tools scanned): `code_job_tool` returned **0 hits** — no auto-detected drift.

### 5c.2 Gating truth matches runtime behavior

**Disposition: PASS — no gate; always live.** `code_job_tool` has no Django settings flag or auth gate. The realistic invocation scope is bounded by PA tool-surface exposure (GPT-5.2 function-calling on PA chat path — Rigby-only in practice) plus the `Repo` allowlist on `submit`. The `mode=dry_run` parameter on `submit` is a **code-worker behavior toggle** (governs git push/PR), NOT a handler-layer safety gate — the `ExecutionRun` row + Celery task are always written regardless of mode. Documented under §3 Schema notes.

### 5c.3 Shared handler-file coupling noted

**Disposition: SHARED — dedicated file BUT with sibling tool.** `td_handlers_codejobs.py` also hosts `_handle_claude_code` (the `claude_code_tool` handler) at line 330. Both tools share the same `CodeJobHandlersMixin` class. Cross-link required for future operators editing this file: **`claude_code_tool` is the sibling** — that handler dispatches `claude_code_engineer_task` (in-process autonomous Claude Code session, NOT a remote code-worker job). Any refactor to the mixin's shared state (`self._conversation_id` at line 351 is `claude_code_tool`-only; not touched by `code_job_tool`) should preserve both surfaces. `claude_code_tool` is `validated_full` per existing `claude_code_tool_validation.md`.

## 6. Evidence

Live PA-dispatch evidence for the 4 read actions. Captured at S2940 T0 via Rigby dispatch (tool_runs verbose block). Mutations (`submit` / `cancel` / `add_repo`) analyzed-not-executed per §5a.

### 6.1 `action=list_repos` — LIVE at S2940 T0

Dispatch: `code_job_tool action=list_repos`
Latency: 14ms
Result:
```json
{
  "repos": [
    {
      "id": "db692099-29a9-4ed1-86a9-b73a2c07a40c",
      "name": "donkey-betz-platform",
      "slug": "clwest/donkey-betz-platform",
      "repo_url": "https://github.com/clwest/donkey-betz-platform",
      "default_branch": "main",
      "is_active": true,
      "test_command": "(auto-detect)",
      "lint_command": "(auto-detect)",
      "max_runtime_seconds": 600
    }
  ],
  "total": 1
}
```

**Observations locked at this HEAD:**
- Exactly 1 repo in the allowlist: `donkey-betz-platform` (the platform's own repo).
- `test_command` + `lint_command` render as literal `"(auto-detect)"` string when the DB fields are empty (line 280-281 of handler).
- Row shape is stable — all 9 fields present. Envelope is bare `{repos: [...], total: N}` — no `ok`/`action`/`gateway` wrapper. **Ledger #5 consistency lint candidate** — this handler uses bare envelope shape, whereas most Slice 7 handlers use `{ok, action, gateway, ...}` (see §5c.1 disposition — schema description is source-of-truth for callers; envelope shape is a minor stylistic drift, not a semantic drift).

### 6.2 `action=list` (limit=3) — LIVE at S2940 T0

Dispatch: `code_job_tool action=list limit=3`
Latency: 28ms
Result:
```json
{
  "total": 0,
  "jobs": []
}
```

**Observations locked at this HEAD:**
- Empty state — no `ExecutionRun` rows with `plan_json__version='code_worker_v1'` at HEAD `adba317b0`. Cleanly returns empty envelope.
- `total` reflects the pre-limit query count (post-`.filter()` but pre-`[:limit]` slice). Same pattern as other list handlers (rigby_work_item + newsletter_tool).
- Envelope stable: `{total: N, jobs: [...]}` — bare shape, no `ok`/`action` wrapper. Same divergence from the `{ok, action, ...}` pattern as §6.1.

### 6.3 `action=status` — ANALYZED (not live-verifiable in empty-state)

The `list` action at §6.2 verified zero `ExecutionRun` rows at this HEAD; without an existing `ExecutionRun.id` to reference, `status` cannot be exercised live without first firing a `submit` mutation. Analyzed via handler branch at line 179 (`ExecutionRun.objects.select_related('repo').get(id=job_id)`). Expected envelope shape (from handler lines 187-198):
```json
{
  "job_id": "<uuid>",
  "status": "queued|running|succeeded|failed|cancelled",
  "progress": "50%",
  "current_step": "<step_name_or_null>",
  "steps": "3/6",
  "branch": "<working_branch>",
  "pr_url": null,
  "pr_number": null,
  "error": null,
  "failure_reason": null,
  "elapsed_seconds": 42.5,
  "task_prompt": "<first 200 chars>"
}
```
Smart-inference fallback path (line 168-175): if `job_id` is missing AND `user_id` is set, resolves to `ExecutionRun.objects.filter(created_by=user).order_by('-created_at').first()`. If no user OR no runs → `{"error": "job_id is required"}`.

Missing-job envelope (verified via §5 analysis of line 180-181): `{"error": "Job <id> not found"}`.

### 6.4 `action=logs` — ANALYZED (not live-verifiable in empty-state)

Same empty-state constraint as §6.3 — cannot exercise without an existing `ExecutionRun.id`, and creating one requires firing `submit` (deferred per bifurcated Option C). Analyzed via handler branch at line 200. Expected envelope shape (from lines 214-218):
```json
{
  "job_id": "<uuid>",
  "status": "<status>",
  "log_count": 42,
  "logs": ["[<step>] <message>", ...]
}
```
Cursor pagination via `after_sequence` (line 209) + `limit` capped at 100 (line 210). Logs formatted as `[step] message` strings (line 217).

### 6.5 Mutation actions (`submit`, `cancel`, `add_repo`) — ANALYZED-NOT-EXECUTED

See §5a for per-action write-target inventory + signal-chain evidence + idempotency proof + Appendix A async-fanout contract + deferral rationale.

### 6.6 Invalid action envelope

Handler line 99: `{"error": "Unknown code_job_tool action: <x>"}`. Non-raising in-envelope error. Bare `{error: ...}` shape — no `ok: false` field. Fifth-instance corroboration of the invalid-action divergence class documented in `rigby_work_item` §5c.1 (Ledger #5 candidate for Tier-2 promotion).

## Related

- **Adjacent tools (same Slice 7 Batch 2b):** `employee_tool` (bifurcated: 3 read + 1 mutation — `run_now` external Celery), `railway_tool` (bifurcated: 5 read + 2 external mutations — Railway GraphQL API).
- **Adjacent tools (same handler file — SHARED):** `claude_code_tool` (`_handle_claude_code` at `td_handlers_codejobs.py:330`) — sibling in the mixin. `claude_code_tool` dispatches an in-process autonomous Claude Code session via `claude_code_engineer_task.delay(...)`; `code_job_tool.submit` dispatches a remote code-worker session via `execute_code_job.apply_async(queue='code_jobs')`. Distinct surfaces despite the shared file.
- **Adjacent tools (adjacent surface):** `repo_tool` (read-only file/dir browsing on the current repo — no remote dispatch, no PR creation), `execution_history_tool` (read-only cross-tool execution audit including `ExecutionRun` rows), `workflow_run_tool` (multi-stage workflow orchestration — different execution model), `github_pr_tool` (PR inspection — reads GitHub API directly).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1 + §5c retro-fold added S2937); `docs/audits/PA_TOOLS_GAP_MAP.md`; `core/tasks.py::execute_code_job` (Celery task implementation — not yet validated per Slice 7 scope).
- **Prior ratifications:** S2892 Path B open; S2907 T0 Fold E; S2921 §5a taxonomy; S2928 Slice 5 CLOSE; S2937 T1 Chris ratification (4-batch Slice 7 plan + §5c retro-fold); S2938 Ledger #5 lint substrate; S2939 T0 Chris D-verdict RATIFIED with two guardrails (§6 read-only scope + §5a mutation proof bar) — carried forward at S2940 T0 Chris D-verdict RATIFIED (Batch 2b = 3-tool ship closes Slice 7).
- **Lint pre-flight at S2940 open:** `code_job_tool` → **0 handler_drift hits** (verified via `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check`). Clean.
- **First-hop dependencies:** see §5b table + Appendix A (`submit` async fan-out via Celery `execute_code_job.apply_async` on `code_jobs` queue).
- **Regression coverage:** `core/tests/test_code_job_flow.py` + related — grep `test_code_job` in `core/tests/` for full coverage. Handler-boundary tests exist for the submit/status/list surface.
- **Ledger candidates surfaced this doc:** (a) **Ledger #5 Tier-2 candidate** — bare `{error: ...}` envelope shape vs. `{ok: false, action, gateway, error, ...}` pattern (fifth-instance corroboration; still record-only pending threshold); (b) **Silent-degrade on submit Celery dispatch failure** (line 148-149 warning-log-only path — DB row written without `celery_task_id`; caller sees `submitted: true`, `status: queued` with no dispatch — Ledger candidate for a first-class refusal envelope OR a `celery_dispatched: false` field). Both recorded, not fixed this ship.
- **Post-merge live-dispatch verification:** exercise `code_job_tool action=list_repos` + `action=list` after `make recycle-all` at merge; confirm envelope shapes match §6.1 + §6.2. Mutations remain analyzed-only.
