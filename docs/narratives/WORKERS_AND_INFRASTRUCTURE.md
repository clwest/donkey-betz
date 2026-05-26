---
title: "Workers + Infrastructure — narrative (batch E)"
status: draft (batch E of Session 1158 corpus-narrative program)
last_updated: 2026-05-25
session: 1158
audience: future-operator (future-Claude / future-hire / future-Chris) — cannot access UI
template_version: v1-LOCKED (Rigby, Session 1158)
companion_docs:
  - docs/topics/celery-workers.md
  - docs/topics/infrastructure.md
  - docs/narratives/AGENTS_AND_AUTONOMY.md
  - docs/narratives/CONTENT_PIPELINE.md
  - docs/PLATFORM_INVENTORY.md
provenance_confidence: HIGH (anchored to topic docs + named handoff files + memory feedback entries)
provenance_note: Operator-critical narrative — what the platform runs on, how work is queued, why workers fail, and how to bring them back. Counts anchored to PLATFORM_INVENTORY 2026-05-25 (git HEAD d513cd7f). Uncertainty labelled inline.
---

# Workers + Infrastructure

> The doc you reach for when things break. Covers the Celery
> worker fleet (7+ processes + beat + code-worker), the queue
> routing, the OOM history, the Django/Railway/Redis/Postgres
> stack, and the macOS local-stall playbook. Every other
> subsystem in this corpus runs on this layer; if this layer is
> wrong, nothing else works.

---

## 1. What this is

The platform is a Django application served by Daphne (ASGI),
backed by PostgreSQL with pgvector for embeddings, Redis for
cache + broker + result-backend, and a fleet of Celery workers
that do every piece of background work — agent executions,
spider crawls, content generation, signal aggregation, embedding
backfills, body-system health checks, blog publishing, sports
prediction settlement. Production deployment is on Railway with
a $1,500/month cost budget. Local development runs natively on
macOS with a documented SIGSEGV workaround (`OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES`).

The Celery side has gone through ~4 sessions of OOM remediation
between Sessions 1029 and 1064. The core mistake — letting
heavy tasks fall through to a 200 MB `default` worker — was made
once but recurred whenever new tasks shipped without explicit
routing. The remediation arc culminates in `sync_task_queues`,
a release-time management command that asserts every
`PeriodicTask.queue` matches `CELERY_TASK_ROUTES` so the next
class of "task X fell through to default and OOMed the worker"
bug is structurally prevented.

This narrative is operator-grade: it should let someone debug
a stuck queue, identify why a worker keeps OOMing, restore from
a macOS hang, or read the cost story.

---

## 2. Core objects & vocabulary

| Term | Meaning |
|---|---|
| **`Procfile`** | The Railway entrypoint listing 11 process types (release + web + 7 celery workers + beat + code-worker + resolve-node). The web process is Daphne ASGI; release runs migrations + beat sync + queue sync. |
| **Worker processes (7+1+1)** | `celery-worker` (default, agents, sports), `celery-pa` (pa), `celery-content` (content), `celery-long-running` + `celery-long-running-2` (long_running, ml), `celery-broadcast` (broadcast), `celery-beat` (scheduler), `code-worker` (code_jobs). Each has its own memory cap and task-recycling policy. |
| **Pool: prefork vs threads** | Railway (Linux) uses `--pool=prefork -c 1` with `max_tasks_per_child` recycling. macOS local uses `--pool=threads` because prefork triggers SIGSEGV on Darwin. With threads, `max_tasks_per_child` is a no-op. |
| **`max_tasks_per_child`** | Memory-leak mitigation. Worker child process is killed and restarted after N tasks. Values: default=5, pa=10, content=2, long_running=2, broadcast=50, code-worker=1. Prefork only. |
| **`--max-memory-per-child`** | Hard memory cap enforced by Celery. Worker is killed if RSS exceeds. Tier sizes: default 150 MB, pa 200 MB, content 250 MB, long_running 150 MB, broadcast 200 MB, code-worker 400 MB. |
| **`CELERY_TASK_ROUTES`** | The static routing map in `core.settings`. Maps task names (or glob patterns) to queues. The model is "task → queue → worker." Misrouting = OOM. |
| **`PeriodicTask`** | The DB row owned by `django-celery-beat` for scheduled tasks. Materialized from `core/celery.py:app.conf.beat_schedule` via `sync_celery_beat` at release time. **Important:** `PeriodicTask.queue` overrides `CELERY_TASK_ROUTES` when set — the source of half the OOM history. |
| **`sync_celery_beat`** | Release-time command that creates / disables `PeriodicTask` rows from `core/celery.py` definitions. Critical: does **not** set the `queue` field — that's why `sync_task_queues` exists. |
| **`sync_task_queues`** (Session 1064) | The fix for "PeriodicTask.queue doesn't match CELERY_TASK_ROUTES." Reads routes, resolves intended queue per task (explicit first, then glob), updates mismatches. Runs on every release. |
| **`QueuePreservingScheduler`** (Session 1064) | The fix for "celery-beat restarts reset PeriodicTask.queue to NULL." A custom scheduler in `core/schedulers.py` that preserves existing DB queue values when the schedule entry doesn't specify one. Configured via `CELERY_BEAT_SCHEDULER` in `core.settings`. |
| **`CeleryTaskEvent`** (Session 983) | Custom telemetry model in `core/models_celery_telemetry.py`. Populated by signal handlers (`task_prerun`, `task_postrun`, `task_failure`) in `core/celery_telemetry.py`. The platform's authoritative record of what ran, when, and how it ended. `django_celery_results.TaskResult` is empty with the Redis backend, so this exists as a replacement. |
| **`task_breakdown_tool`** (Session 1048) | PA tool with `summary` and `drilldown` actions. Reads `CeleryTaskEvent` for one-click load analysis. p50/p95 percentiles computed Python-side. Windows: 15m / 60m / 2h / 6h / 24h. REST endpoints: `GET /api/celery/breakdown/`, `GET /api/celery/breakdown/task/`. |
| **`add_critical_celery_tasks`** (refactored Session 1157) | The bootstrap command that materializes `PeriodicTask` rows from `core/celery.py:app.conf.beat_schedule`. Previously carried its own ~100-entry `CRITICAL_TASKS` dict that contradicted minimal-mode and risked re-enabling conserve-mode-disabled tasks. Session 1157 (PR #2243) refactored it to be a thin wrapper over the canonical source. |
| **macOS SIGSEGV workaround** | `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` env var + `--pool=solo` or `--pool=threads`. Prefork on Darwin triggers Objective-C's fork-safety crash. The workaround disables the check; works in practice but is officially unsafe per Apple's docs. |
| **macOS Celery stall** | The "worker alive to `ps` but not responding to `inspect ping`" pattern. Memory entry `feedback_local_celery_stall_playbook.md` lists the 6-step diagnostic (CeleryTaskEvent → queue depths → inspect ping → log grep for mutex.cc → purge stale queues → restart without beat). The remedy is `pkill -9 -f celery; rm -f .celery*.pid; make celery`. |
| **`.celery*.pid` cache** | Stale PID files prevent `make celery` from restarting workers. Per memory `feedback_celery_pid_cache_blocks_restart.md`: `make celery` will refuse if PID files exist. After tool registration or PA code changes, `pkill -9 -f celery; rm -f .celery*.pid; make celery` is mandatory. |
| **Redis databases** | DB1 = cache, DB2 = broker, DB3 = results. Channel layer uses default DB. Three distinct DBs in `settings.py`. |
| **Workspace path self-healing** (Session 1034) | `_get_workspace_for_skin_layer()` auto-detects stale local macOS paths stored in DB, recomputes from `__file__`, and updates the DB record. Handles Railway-vs-local path mismatch when a developer's local DB gets synced/restored from prod. |
| **ML import lazy-loading** | Heavy ML imports (torch, sklearn, transformers) MUST be lazy — inside methods or behind `try/except ImportError`. Module-level imports loaded ~800 MB into the Celery parent process. `ml_engine.py` uses `_detect_device()` helper for lazy torch. |

---

## 3. Milestone timeline

| When | Change shipped | Why | Outcome | Status | Pointers |
|---|---|---|---|---|---|
| **Foundation — Django + Daphne + Postgres + Redis + Celery** *(early sessions, Inferred)* | Django 4.2+ with Daphne ASGI; PostgreSQL with pgvector extension; Redis split across DB1 (cache) / DB2 (broker) / DB3 (results); ~7 celery worker processes in Procfile; LLM providers wired (OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini). Railway as the deploy target with healthcheck timeout 600 s. | The platform needed a production-grade stack from day one — async web (Daphne), vector search (pgvector), background work (Celery), multi-LLM provider abstraction. Each piece was a deliberate choice; none has been replaced. | Stack stabilized; new subsystems plug into existing primitives (PA queue, content queue, ml queue) rather than introducing new infra. | **Active** — entire stack is current. 6 LLM providers registered. | `docs/topics/infrastructure.md`; `core.settings`; `Procfile` |
| **Session 983 — CeleryTaskEvent observability** | `django_celery_results.TaskResult` is empty when `CELERY_RESULT_BACKEND=redis` (results land in Redis, not Postgres). Added `CeleryTaskEvent` model in `core/models_celery_telemetry.py`, populated by signal handlers (`task_prerun`, `task_postrun`, `task_failure`). Fields: task_id, task_name, queue, status, worker, started_at, finished_at, duration_seconds, error_type, error_message. | The platform had no visible record of what was running, what failed, or how long things took. Worker death was invisible until a user complained. This was the gap that turned every prod issue into "guess what crashed." | Every task execution is now persisted with timing + status + error info. Becomes the data source for `status_snapshot_tool`, `system_health_tool`, `task_breakdown_tool`, and the nervous-system message stats. | **Active** — the canonical telemetry source. Used everywhere downstream. | `docs/topics/celery-workers.md` §"Observability (Session 983)"; `core/models_celery_telemetry.py`; `core/celery_telemetry.py` |
| **Sessions 1029, 1043, 1063, 1064 — the OOM arc** | Across four sessions, ~130 tasks moved off the 200 MB `default` queue onto appropriate larger queues. (1029) 5 tasks moved — `run_multi_agent_conversation`, `run_autonomous_thinking_cycle`, `process_hivemind_sessions`, `execute_approved_dreams_via_orchestration`, `warm_up_spider_network`. (1043) 9 more — `execute_agent_task`, `run_spider_by_category`, `execute_single_spider`, `produce_content_package`, etc. (1063) 46 unrouted — body checks → broadcast (11), heavy LLM/agents → long_running (19), embeddings → ml (5), content tasks → content (7). (1064) ~70 more after discovering that the `agents.*` glob in routes only matched `agents.update_agent_performance` — `core.tasks_agents.*` (with 6 heavy tasks including `execute_agent`, `execute_orchestration`) was uncovered and falling through. Also introduced `sync_task_queues` management command + `QueuePreservingScheduler` to prevent the bug class from recurring. | The 200 MB `default` worker was OOMing 3 times in 18 minutes (Session 1029). Heavy tasks — agent loaders, spider executors, LLM-calling orchestrators, embedding generators — were falling through to it because either no explicit route existed, the glob didn't match, or `PeriodicTask.queue` had been set to `'default'` or NULL by `sync_celery_beat` (which doesn't set `queue` field). Body-system checks alone were generating ~150 task runs/hour on the wrong worker. | `default` queue is now light DB-query tasks only (~28). Heavy work routes to `long_running` (52 tasks), `content` (19), `broadcast` (4), `ml` (12), `agents` (18), `sports` (11). OOM frequency dropped to near-zero. `sync_task_queues` runs on every release; `QueuePreservingScheduler` survives beat restarts. | **Active** — the routing model is the standard. `sync_task_queues` is part of the release command. | `docs/topics/celery-workers.md` §"OOM Fix" sections (1029, 1043, 1063) + §"OOM Fix — ~70 More Unrouted Tasks (Session 1064)" + §"PeriodicTask Queue Sync (Session 1064)" |
| **Session 1034 — schedule throttling + workspace self-healing + cost budget** | (Throttling) Spider warm-up 4h → 6h, clean stale data 24h → 48h, refresh AI opportunities 30m → 2h, dream execution 2h → 4h. ~40 % fewer runs for these four schedules. (Workspace) `_get_workspace_for_skin_layer()` auto-detects stale local macOS paths stored in DB (when a developer's local DB was synced/restored from prod or vice versa), recomputes from `__file__`, and updates the DB. (Cost) Budget raised from $1,200 to $1,500/month with the throttling tax already factored in. Media task guard: `_MEDIA_AGENTS` frozenset + `_MEDIA_GENERATION_PATTERN` regex blocks non-generative dispatches like "List recent images" at two layers (`ConversationActionDispatcher` pre-dispatch + `execute_agent_task` fallback). | The platform was paying for redundant LLM calls (spider warm-ups running 4× /day when 6h was sufficient) and was crashing on workspace path mismatches when DBs moved between environments. Cost was running over budget; workspace failures were visible to users. | Cost stabilized within budget. Workspace path errors became self-correcting. Media task guard closed the "agent uses generation budget for a listing operation" class of waste. | **Active** — all three mechanisms still in production. | `docs/topics/celery-workers.md` §"Session 1034 Schedule Throttling" and §"Media Task Guard"; `docs/topics/infrastructure.md` §"Workspace path self-healing" |
| **Session 1048 — task volume breakdown** | Two REST endpoints — `GET /api/celery/breakdown/?window=60m&limit=25` (aggregated totals + by-task with p50/p95 + by-agent) and `GET /api/celery/breakdown/task/?task_name=...` (single-task drilldown). PA tool `task_breakdown_tool` with `summary` and `drilldown` actions. Triggered by "what's driving load?", "top failing tasks", "task volume" prompts. Windows: 15m / 60m / 2h / 6h / 24h. P50/p95 computed Python-side from sorted duration lists. | After the OOM arc, the platform had telemetry (`CeleryTaskEvent`) but no easy way to ask "what's loading the workers right now?". The previous answer was to read logs. The breakdown tool made the question one PA call. | Load analysis is now a chat-time operation. The PA can answer "show me the top 25 tasks by volume in the last hour, with failure rates and p95 duration" without anyone touching a terminal. | **Active** — `task_breakdown_tool` is part of the standard PA tool set. | `docs/topics/celery-workers.md` §"Task Volume Breakdown (Session 1048)" |
| **Sessions 1027, 1029 — three agent dispatch systems** | Discovered that disabling one agent dispatch path did NOT stop the others. Three primary systems coexist: (A) `run_*_agents()` in `core/tasks.py` — 19 group schedules via `_run_agent_group()`; (B) `AGENT_WORKSPACE_REGISTRY` iterated by `agent_category_rotation()`; (C) `MetricsActionTrigger` (`core/services/metrics_action_trigger.py`) — condition-based triggers from live metrics. Plus three secondary paths: `workspace_autopilot_tick()` CATEGORY_AGENTS / TYPE_AGENTS maps, Dream pipeline `DREAM_TO_WORKFLOW`, podcast `auto_generate_podcast_episode()`. Beat schedules persist in DB even after commenting out code — to disable, must run `PeriodicTask.objects.filter(name='...').update(enabled=False)` as well. PRs #1271, #1283, #1284 disabled 3 remediation execution schedules + 3 metric trigger rules. | The team was disabling agent paths thinking they had killed dispatches, then finding the same agents still running. The "3 systems" reality wasn't documented, and DB-persisted beat schedules weren't reset when the code that scheduled them was commented out. Both were silent footguns. | The three-path model is now a documented warning. Disabling an agent requires checking all six paths, not just one. `PeriodicTask.objects.filter(...).update(enabled=False)` is the standard pattern. | **Active warning** — the six-path topology is unchanged; the discipline of checking all of them on disable is. | `docs/topics/celery-workers.md` §"Disabled Schedules" + §"Three Agent Dispatch Systems (Session 1029)" |
| **Session 1033 — content + deliverable scoring tasks added** | `auto_enhance_blogs` (every 4h at :45 on `content` queue, EditorAgent w/ `save=True`, limit 5) — wired the content-pipeline finishing loop. `score_unscored_deliverables` (every 6h at :15 on `default` queue) — heuristic scoring over the 4,380 deliverables that had hardcoded `quality_score=0.7`. First-run results: 6 blogs enhanced (status moved `needs_enhancement → pending_review`), 884 deliverables scored (distribution 0.30–0.75). | The content pipeline (covered in narrative B) had structure but couldn't complete on its own. Blogs hit `needs_enhancement` and stayed there; deliverables had no quality differentiation. Both were silent failures from the user's perspective — the UI showed "things exist" but operationally nothing was moving. | The finishing loop completes end-to-end without manual intervention. `enhancement_count` cap (3 rounds) prevents infinite loops. EditorAgent's broken LLM import was fixed in PR #1308 as part of this arc. | **Active** — both tasks are scheduled and running. | Cross-ref: `docs/narratives/CONTENT_PIPELINE.md` milestone 7; `docs/topics/celery-workers.md` Session 1033 references |
| **Session 1157 — celery-beat-schedule canonical-source refactor** | `add_critical_celery_tasks` mgmt command refactored to materialize `PeriodicTask` rows from `core/celery.py:app.conf.beat_schedule` (the canonical static source). Removed the ~100-entry `CRITICAL_TASKS` dict that contradicted "minimal token-conservation mode" — different entries AND different cadences (e.g., `heart-service-heartbeat` every 60s vs every 600s). Smoke-test on main: 77/77 entries translate, 0 DB churn, idempotent. Footgun closed: running the mgmt command no longer re-enables conserve-mode-disabled tasks. | Two sources of truth had drifted. `core/celery.py` was in intentional "MINIMAL mode" since Session 1077 to conserve LLM tokens. The mgmt command had its own list claiming "MUST be running" that pre-dated the minimal mode and would have wiped it out if invoked. Code-vs-code contradiction. | One canonical schedule source; the mgmt command is a thin wrapper. `context-kit` still flags a CONFLICT signal because the detector heuristic spans ~36 files broader than this pair; queued for Session 1158+. | **Active** — code-level footgun closed. Detector signal still flagged (deferred follow-up). | `docs/handoffs/SESSION_1157_CELERY_BEAT_SCHEDULE_CLEANUP.md`; PR #2243 |

---

## 4. What came of it

### Wins

- **Heavy work no longer crashes the lightweight queue.** The
  OOM arc moved ~130 tasks off `default` onto appropriate
  larger queues over four sessions. The release-time
  `sync_task_queues` command structurally prevents the bug
  class from recurring.
- **Every task is observable.** `CeleryTaskEvent` (Session
  983) captures every run. Load analysis is a PA call away
  (`task_breakdown_tool`). The previous "guess what crashed"
  mode is over.
- **Cost is bounded.** Schedule throttling (Session 1034)
  reduced spider warm-up, stale-data clean, AI opportunity
  refresh, and dream execution by ~40 %. Budget raised to
  $1,500/month with the new cadences absorbed.
- **Workspace path self-healing.** Sessions where a developer
  syncs DB from prod or vice versa no longer crash on stale
  macOS-style paths. Auto-recompute from `__file__`.
- **One canonical schedule source.** Session 1157 closed the
  code-vs-code contradiction between `core/celery.py` and
  `add_critical_celery_tasks`. The mgmt command is now a thin
  wrapper.
- **macOS local dev has a documented playbook.** The hang
  pattern (worker alive to `ps`, not responding to `inspect
  ping`) and its remedy (`pkill -9 -f celery; rm -f
  .celery*.pid; make celery`) are written down in memory. New
  developers don't have to rediscover.

### Tradeoffs

- **`default` worker is still 150–200 MB.** Anything new that
  ships without an explicit route falls through to it. The
  release-time `sync_task_queues` catches the
  `PeriodicTask.queue` drift but not the original miss in
  `CELERY_TASK_ROUTES`. New tasks need route entries on day
  one.
- **macOS `--pool=threads` disables `max_tasks_per_child`.**
  Memory leaks accumulate per-worker forever on local dev. The
  remedy is to restart workers periodically; there's no
  automated mitigation locally.
- **`OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` is officially
  unsafe per Apple.** Works in practice but the workaround is
  documented as undefined behavior. If Apple removes the
  override, local dev breaks.
- **Three agent dispatch systems + three secondary paths
  remain.** No consolidation. Disabling an agent requires
  checking all six. The complexity is documented but not
  reduced.
- **`PeriodicTask.queue` overrides `CELERY_TASK_ROUTES`.** The
  override semantic is the cause of half the OOM history. The
  fix (`sync_task_queues` + `QueuePreservingScheduler`) is
  belt-and-suspenders; the underlying override behavior
  remains.
- **`celery-beat-schedule` detector still flags CONFLICT.** The
  underlying code-vs-code contradiction is closed (Session
  1157); the context-kit heuristic spans ~36 files broader
  than the closed pair and still emits a CONFLICT signal.
  Deferred follow-up.
- **`add_critical_celery_tasks` can still re-write a beat
  schedule if invoked without thinking.** It's now a thin
  wrapper, but it's still a thing you can run. The minimal
  mode is intentional and not enforced at the command level —
  only by convention.
- **Redis DB choice is hardcoded.** DB1/DB2/DB3 are split in
  settings; switching to another Redis instance requires
  understanding the split. Not parameterized.

### Follow-on systems enabled

- **PA telemetry tools** (Session 1048 task_breakdown_tool,
  cockpit_tool from Session 1100, status_snapshot_tool) all
  consume `CeleryTaskEvent`. The Personal Assistant narrative
  (D) covers their dispatch; this narrative covers the data
  source.
- **The Content Pipeline finishing loop** (narrative B) is the
  consumer of `auto_enhance_blogs` + `score_unscored_deliverables`
  added in Session 1033.
- **The Signal Intelligence pipeline** (narrative C) depends on
  `scan_spider_opportunities` (every 30 min, `default`),
  `backfill_spider_embeddings` (every 10 min, `ml`),
  `advance_initiative_pipeline` (long_running). The narrative
  C wins all run on this worker fleet.
- **Body system health monitoring** runs on the `broadcast`
  queue (covered in narrative F when it ships).

---

## 5. Current state snapshot

> Source for counts: `PLATFORM_INVENTORY.md` snapshot 2026-05-25
> (git HEAD `d513cd7f`). Celery task count: 401 user-defined.
> Beat schedule: 80 enabled / 0 disabled = 80 `PeriodicTask`
> rows.

**Procfile entries (11 total).** release + web + 7 celery workers
+ beat + code-worker + resolve-node.

**Worker processes (Railway).** `celery-worker` (default,
agents, sports — 150 MB, 5/child), `celery-pa` (pa — 200 MB,
10/child), `celery-content` (content — 250 MB, 2/child),
`celery-long-running` ×2 (long_running, ml — 150 MB ea,
2/child), `celery-broadcast` (broadcast — 200 MB, 50/child,
threads), `celery-beat` (scheduler), `code-worker` (code_jobs —
400 MB, 1/child).

**Queue routing (`CELERY_TASK_ROUTES`).**
- `default` — ~20 tasks. Light DB queries, narrative drift,
  attention lifecycle, triggers, roi_metrics, cleanup.
- `long_running` — ~120 tasks. Agent exercises, autonomous
  situations, pipeline execution, spider network, intelligence
  desks, multi-agent conversations, hivemind, dreams, content,
  LLM pipelines.
- `content` — ~35 tasks. Blog generation, podcasts, initiative
  stages, content deliberation, blog re-eval, auto-publish,
  auto-enhance, voice scoring.
- `sports` — ~11 tasks. Odds collection, predictions, scores,
  evaluation, verification, settlement, accuracy reports.
- `broadcast` — ~25 tasks. Status snapshots, heartbeat,
  nervous system, body checks (9), orchestration timeouts,
  stuck/cleanup, learning loop, KPI alerts, celery health.
- `ml` — ~12 tasks. Embedding backfills, ML training/scoring,
  agent activity embeddings, doc/memory embeddings.
- `pa` — 2 tasks. `process_pa_chat_task`,
  `draft_legal_document_task`.
- `agents` — ~18 tasks. Agent exercise groups, autonomous
  situations, market desk, alert checks.

**Schedule source of truth.** `core/celery.py:app.conf.beat_schedule`
is canonical. `django-celery-beat` owns runtime
`PeriodicTask` rows. Sync commands bridge: `sync_celery_beat`
creates/disables rows; `sync_task_queues` aligns queue fields;
`add_critical_celery_tasks` is a thin wrapper (Session 1157).

**Release command (Procfile).**
```
release: python manage.py migrate --noinput
      && python manage.py sync_celery_beat --apply --create-only --disable-missing
      && python manage.py sync_task_queues --apply
      && python manage.py setup_codebase_workspace
```

**Beat scheduler.** `CELERY_BEAT_SCHEDULER =
'core.schedulers:QueuePreservingScheduler'` — preserves
existing `PeriodicTask.queue` when the schedule entry doesn't
specify one. Session 1064 fix for "celery-beat reset queue to
NULL."

**Telemetry.** `CeleryTaskEvent` rows on every `task_prerun /
task_postrun / task_failure` signal. Used by
`status_snapshot_tool`, `system_health_tool`,
`task_breakdown_tool`, `cockpit_tool`, nervous-system stats.

**Telemetry REST endpoints.**
- `GET /api/celery/breakdown/?window={15m|60m|2h|6h|24h}&limit=25`
- `GET /api/celery/breakdown/task/?task_name=...&window=...`

**Cost budget.** $1,500/month (raised from $1,200 in Session
1034 with throttling tax factored in).

**LLM providers (6).** OpenAI, Anthropic, Together AI, Ollama,
DeepSeek, Gemini.

**Database (PostgreSQL + pgvector).** 585 concrete models
across 23 apps. `core/models/` package shadows `core/models.py`
— Django uses the package. New model imports go in
`core/models/__init__.py`. `core/models.py` is dead code; do
not add imports there.

**Redis DBs.** DB1 cache, DB2 broker, DB3 results. Channel
layer uses default DB.

**Where to look when something stops working.**
- Task stuck in queue → `celery -A core inspect active` to
  see if a worker is processing; `redis-cli LLEN <queue>` for
  queue depth.
- Worker keeps OOMing → check task routing
  (`CELERY_TASK_ROUTES`); check `PeriodicTask.queue` for the
  task in question (it overrides routes); add explicit route
  and run `sync_task_queues --apply`.
- `inspect ping` shows fewer nodes than expected → worker is
  alive-but-hung. macOS pattern. Remedy: `pkill -9 -f celery;
  rm -f .celery*.pid; make celery`.
- New tool/PA capability not visible after deploy → daphne +
  ALL celery workers need restart, not just daphne. Per memory
  `feedback_celery_pid_cache_blocks_restart.md`: `make celery`
  alone won't restart if PID files exist.
- Beat task running on wrong worker → check `PeriodicTask.queue`
  for the row; if it's wrong, `sync_task_queues --apply`. If
  it keeps reverting, `QueuePreservingScheduler` isn't loading
  — check `CELERY_BEAT_SCHEDULER` setting.
- macOS local SIGSEGV on Celery start → missing
  `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` env or trying to
  use `--pool=prefork`. Use `--pool=solo` or `--pool=threads`.
- "Task X completed but never marked complete in Redis" → the
  PA-style stall where the task ran but `result_backend` write
  failed. Check Redis `celery-task-meta-<id>` key. Often a
  symptom of the worker hanging mid-cleanup.
- "Migrations hang on lock during deploy" → blue-green deploy
  contention. Temporarily remove `migrate` from release
  command, deploy, run migrate manually, restore.

---

## 6. Open questions / unknown outcomes

- **What % of recent OOMs trace to misrouted PeriodicTasks vs
  newly-added unrouted code?** *Known:* `sync_task_queues`
  catches `PeriodicTask.queue` drift. *Unknown:* whether
  recent OOMs (if any) are from new code shipping without
  routes vs DB-side drift. A `CeleryTaskEvent` query joined
  with worker-death timestamps would surface this.
- **The 68 tasks with "no route" at Session 1064 resolution —
  what are they?** *Known:* Session 1064 fixed 179, left 36
  already correct, and "68 no route (left as-is)." *Unknown:*
  whether those 68 are intentionally unrouted (light enough
  to live on default) or were skipped because the routing
  intent wasn't clear. A routing audit would close.
- **Is the macOS-`-pool=threads` memory leak meaningful in
  practice?** *Known:* `max_tasks_per_child` is a no-op with
  threads, so leaks accumulate per-worker forever. *Unknown:*
  the actual RSS growth rate on a long-lived local worker.
  Most local sessions are short enough that the leak doesn't
  matter, but no measurement is in the corpus.
- **`celery-beat-schedule` context-kit CONFLICT detector
  scope.** *Known:* Session 1157 closed the code-level
  footgun (PR #2243). *Unknown:* exactly which ~36 files
  trigger context-kit's "ownership claim" heuristic. Two
  paths: detector tuning (preferred — read-only investigation
  of the detector source) or targeted 36-file phrasing sweep.
  Queued for Session 1158 carryover.
- **Should the 3-system agent dispatch topology be
  consolidated?** *Known:* three primary + three secondary
  paths. *Inferred:* the complexity has caused real bugs (the
  "I disabled X but it's still running" class). *Unknown:*
  whether a consolidation has been scoped or whether the
  documentation alone is considered sufficient.
- **Pre-existing 3-row PeriodicTask drift.** *Known:* 80 DB
  rows vs 77 entries in `core/celery.py:app.conf.beat_schedule`
  (per start-here doc). *Unknown:* what the three orphan rows
  are. Folds into the celery-beat-schedule detector follow-up.
- **Redis pooling sweep.** *Known:* per Session 1144+
  carryover (`feedback_openai_client_factory.md` +
  `feedback_anthropic_client_factory.md` patterns), ~40
  inline `redis.Redis.from_url(...)` sites would benefit from
  a factory similar to the OpenAI/Anthropic client factories.
  *Unknown:* whether the sweep has started.
- **`exists_on_disk: false` flag in `_provenance.json`.**
  *Known:* 326 dead paths in `_provenance.json` since Session
  1145. Schema bump v1→v2 deferred. *Unknown:* whether the
  schema bump is in flight.

---

## 7. Source index

### Primary doc sources

- `docs/topics/celery-workers.md` — current-state topic doc;
  the closest companion. Most session citations originate
  there.
- `docs/topics/infrastructure.md` — Django/Railway/Redis/Postgres
  stack overview.
- `docs/PLATFORM_INVENTORY.md` — runtime-derived inventory;
  authoritative for task counts (401 Celery, 80 PeriodicTask,
  6 LLM providers, 585 models, 23 apps).

### Named session handoffs cited above

- `docs/handoffs/SESSION_1157_CELERY_BEAT_SCHEDULE_CLEANUP.md`
  — canonical-source refactor.
- Sessions 983 / 1027 / 1029 / 1033 / 1034 / 1043 / 1048 /
  1063 / 1064 — telemetry, OOM arc, throttling, breakdown
  endpoints, route consolidation. Handoff filenames in
  `docs/handoffs/`.
- MEMORY.md feedback entries:
  - `feedback_local_celery_stall_playbook.md`
  - `feedback_celery_pid_cache_blocks_restart.md`
  - `feedback_openai_client_factory.md`
  - `feedback_anthropic_client_factory.md`

### Code anchors

- `core/celery.py` — `app.conf.beat_schedule` (canonical
  static source).
- `core.settings` — `CELERY_TASK_ROUTES`,
  `CELERY_BEAT_SCHEDULER`, Redis DB split.
- `core/celery_telemetry.py` — `task_prerun / task_postrun /
  task_failure` signal handlers.
- `core/models_celery_telemetry.py` — `CeleryTaskEvent` model.
- `core/schedulers.py` — `QueuePreservingScheduler`.
- `core/management/commands/sync_celery_beat.py` — schedule
  sync.
- `core/management/commands/sync_task_queues.py` — Session
  1064 queue alignment.
- `core/management/commands/add_critical_celery_tasks.py` —
  thin wrapper post Session 1157.
- `Procfile` — process declarations.

### Verification commands

- `python manage.py generate_platform_inventory` — regenerate
  inventory.
- `python manage.py sync_task_queues --apply` — fix queue
  drift.
- `python manage.py sync_celery_beat --apply --create-only --disable-missing` —
  rebuild PeriodicTask rows from `core/celery.py`.
- `celery -A core inspect ping` — verify all workers respond.
- `celery -A core inspect active` — see what's running.
- `redis-cli -u redis://localhost:6379/0 LLEN <queue>` —
  queue depth.
- `pkill -9 -f celery; rm -f .celery*.pid; make celery` — full
  worker restart (the macOS playbook).
