<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`../PLATFORM_WHAT_IT_IS.md`](/docs/PLATFORM_WHAT_IT_IS.md). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality (Session 1099 verifier).

# Celery & Workers

271 Celery tasks across 9 worker processes with queue-based routing, memory management, and observability via CeleryTaskEvent signals. Session 1000C: Routed 60+ heavy tasks off default queue to prevent OOM. Session 1029: Rerouted 5 additional heavy tasks from default to long_running to fix recurring OOM crashes. Session 1033: Added auto_enhance_blogs + score_unscored_deliverables. Session 1034: Throttled 4 beat schedules (~40% fewer runs), media task guard, workspace path self-healing. Session 1063: Routed 46 more unrouted tasks (body checks → broadcast, LLM tasks → long_running, embeddings → ml). Session 1064: Created `sync_task_queues` management command to sync PeriodicTask.queue fields to CELERY_TASK_ROUTES — fixed 179 misrouted beat tasks.

## Worker Processes (9 in Procfile)

| Worker | Queue(s) | Pool | Concurrency | Memory Limit | Task Recycling | Purpose |
|--------|----------|------|-------------|-------------|----------------|---------|
| celery-worker | default, agents, sports | prefork (Railway) / threads (macOS) | 1 | 150MB | 5 tasks | Lightweight DB-query tasks only (~28 tasks) |
| celery-pa | pa | prefork | 1 | 200MB | 10 tasks | PA chat queries (dedicated to prevent queue starvation) |
| celery-content | content | prefork | 1 | 250MB | 2 tasks | Blog generation, podcasts, initiative stages (~19 tasks) |
| celery-long-running | long_running, ml | prefork | 2 | 150MB | 2 tasks | Agent exercises, LLM calls, embeddings, spiders (~52 tasks) |
| celery-long-running-2 | long_running, ml | prefork | 2 | 150MB | 2 tasks | Second long-running worker for capacity |
| celery-broadcast | broadcast | threads | 3 | 200MB | 50 tasks | High-frequency status updates (60-180s, ~4 tasks) |
| celery-beat | (scheduler) | — | — | — | — | Drives beat schedule entries |
| code-worker | code_jobs | prefork | 1 | 400MB | 1 task | Code generation tasks |

## Pool Configuration

**Railway (Linux):** `--pool=prefork -c 1` enables child process recycling via `max_tasks_per_child`. Memory caps enforced via `--max-memory-per-child`.

**macOS Local:** MUST use `--pool=threads` (prefork causes SIGSEGV on Darwin). `max_tasks_per_child` is a NO-OP with threads. Set `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES`.

**Memory budget:** Parent ~200MB + 1 child at 200MB = ~400MB (safe for Railway 512MB limit).

## Task Routing (settings.py CELERY_TASK_ROUTES)

108 beat schedule entries in `CELERY_BEAT_SCHEDULE` (settings.py) have NO explicit `options.queue` — routing is entirely driven by `CELERY_TASK_ROUTES`:

| Queue | # Tasks | Categories |
|-------|---------|------------|
| default | ~20 | Light DB queries, narrative drift, attention lifecycle, triggers, roi_metrics, cleanup |
| long_running | ~120 | Agent exercises (18), autonomous situations (14), pipeline execution, spider network, intelligence desks, multi-agent conversations, hivemind sessions, dream execution, core.tasks_agents.execute_*, ai_core.spiders.tasks.*, content generation, LLM pipelines |
| content | ~35 | Blog generation, podcasts, initiative stages, content deliberation, blog re-evaluation, auto-publish, auto-enhance blogs, dream triage, pilot completion, voice scoring |
| sports | ~11 | Odds collection, prediction generation, score fetching, evaluation, verification, settlement, accuracy reports, betting digests |
| broadcast | ~25 | Status snapshots, heartbeat, nervous system, body system checks (9), orchestration timeouts, stuck/cleanup checks, learning loop tracking, KPI alerts, celery health |
| ml | ~12 | Embedding backfills, ML model training/scoring, agent activity embeddings, document/memory embeddings, signal score backfills, training data collection |
| pa | 2 | process_pa_chat_task, draft_legal_document_task |
| agents | ~18 | Agent exercise groups, autonomous situations, market desk, alert checks |

**Important:** `CELERY_BEAT_SCHEDULE` in settings.py overrides `app.conf.beat_schedule` in celery.py (lazy `config_from_object`). The celery.py beat schedule is effectively dead code — all beat entries live in settings.py.

### OOM Fix — Heavy Tasks Rerouted (Session 1029, PR #1282)

celery-worker (512MB container, ~200MB parent) was OOMing 3 times in 18 minutes. 5 tasks moved from `default` to `long_running`:

| Task | Est. Memory | Why Heavy |
|------|-------------|-----------|
| `run_multi_agent_conversation` | 150-300MB | Loads up to 30 agents |
| `run_autonomous_thinking_cycle` | 100-250MB | Gathers 24h system context |
| `process_hivemind_sessions` | 100-250MB | 3 sessions x orchestration |
| `execute_approved_dreams_via_orchestration` | 250-500MB | Up to 10 dreams |
| `warm_up_spider_network` | 200-400MB | Initializes all 77 spiders |

### OOM Fix — 9 More Heavy Tasks Rerouted (Session 1043)

9 additional unrouted heavy tasks found falling through to `default` queue (200MB limit):

| Task | Est. Memory | Why Heavy | New Queue |
|------|-------------|-----------|-----------|
| `execute_agent_task` | 300-500MB | AgentRouter loads all 84 AGENT_MAP agents | long_running |
| `run_spider_by_category` | 400-800MB | SpiderRegistry + spider execution | long_running |
| `execute_single_spider` | 400-800MB | Full spider execution, data collection | long_running |
| `execute_single_spider_lightweight` | 200-400MB | Spider instantiation + fetch | long_running |
| `produce_content_package` | 400-800MB | ContentProductionOrchestrator + multi-agent | long_running |
| `run_hive_mind_session` | 300-600MB | OpenAI API calls for 10+ agents | long_running |
| `explore_dream_topic` | 300-500MB | LLM API calls | long_running |
| `evaluate_pilots_with_thinking_agent` | 200-400MB | ThinkingAgent LLM calls | long_running |
| `run_learning_loop_cycle` | 300-500MB | LearningLoopOrchestrator | long_running |

### OOM Fix — 46 Unrouted Tasks Rerouted (Session 1063)

46 tasks had no explicit route and were falling to `default` queue (200MB celery-worker). Key categories:

| Category | Count | New Queue | Examples |
|----------|-------|-----------|----------|
| Body system checks | 11 | broadcast | `coordinate_body` (60s), `check_circulation` (2m), `immune_scan` (3m), 7 more at 5-15m |
| Heavy LLM/agent tasks | 19 | long_running | `process_spider_data_automatic`, `run_autonomy_cycle`, `market_intelligence_scan`, `run_stock_market_intelligence`, `workspace_autopilot_tick` |
| Embedding tasks | 5 | ml | `embed_agent_activity`, `embed_daily_agent_learning`, `generate_document_embeddings` |
| Content/pipeline tasks | 7 | content | `auto_enhance_blogs`, `auto_triage_dreams`, `auto_promote_decisions`, `auto_complete_pilots` |
| PA-triggered | 1 | pa | `draft_legal_document_task` |
| Alert checks | 1 | agents | `check_all_alerts` |

Body checks alone were generating ~150+ task runs/hour on the 200MB default worker.

### OOM Fix — ~70 More Unrouted Tasks (Session 1064)

Critical discovery: `core.tasks_agents.*` (6 tasks including `execute_agent`, `execute_orchestration`) were NOT covered by the `agents.*` glob — that glob only matches `agents.update_agent_performance`. These ~300-500MB tasks were all landing on the 200MB default worker.

| Category | Count | New Queue | Examples |
|----------|-------|-----------|----------|
| core.tasks_agents.* | 4 | long_running | `execute_agent`, `execute_agent_async`, `execute_orchestration` |
| core.tasks_agents.* | 2 | broadcast | `check_stuck_executions`, `cleanup_old_executions` |
| ai_core.spiders.tasks.* | 5 | long_running | `deploy_full_army`, `collect_spider_data`, `activate_spider_wave` |
| ai_core.spiders.tasks.* | 2 | broadcast | `spider_heartbeat`, `clean_inactive_spiders` |
| Standalone module tasks | 6 | long_running | `trigger_signal_driven_conversation`, `workspace.autopilot_tick`, `pipelines.tasks.run_pipeline_task` |
| Standalone module tasks | 14 | various | `roi_metrics.*`, `triggers.*`, `learning_loop.*`, etc. |
| core.tasks.* heavy | ~30 | long_running | `execute_orchestration_async`, `run_conceptforge_pipeline`, `generate_content_package`, `collect_spider_data` |
| core.tasks.* content | ~5 | content/sports | `generate_podcast_episode`, `enhance_blog`, `collect_sports_odds` |
| core.tasks.* monitoring | ~3 | broadcast | `monitor_celery_health`, `check_kpi_alerts`, `get_event_bus_stats` |

### PeriodicTask Queue Sync (Session 1064)

**Problem:** 179 `PeriodicTask` records had wrong or missing `queue` values (`'default'` or NULL). `sync_celery_beat` never sets the `queue` field when creating tasks. When `PeriodicTask.queue` is set, it **overrides** `CELERY_TASK_ROUTES`, causing heavy tasks to land on the 200MB celery-worker.

**Solution:** New management command `sync_task_queues` reads `CELERY_TASK_ROUTES`, resolves intended queue per task (explicit routes first, then glob patterns), and updates mismatches.

```bash
python manage.py sync_task_queues           # Dry run
python manage.py sync_task_queues --apply   # Apply changes
python manage.py sync_task_queues --verbose # Show all tasks
```

Added to Procfile release command (runs after `sync_celery_beat` on every deploy):
```
release: ... && python manage.py sync_celery_beat ... && python manage.py sync_task_queues --apply && ...
```

Result: 179 fixed, 36 already correct, 68 no route (left as-is).

**Critical gotcha:** `django_celery_beat`'s `DatabaseScheduler.update_from_dict()` resets `PeriodicTask.queue` to NULL on every celery-beat restart (for entries without explicit `options.queue`). Fix: `QueuePreservingScheduler` in `core/schedulers.py` — subclasses `ModelEntry` to omit `queue` from `update_or_create` defaults when not explicitly set. Configured via `CELERY_BEAT_SCHEDULER = 'core.schedulers:QueuePreservingScheduler'` in settings.py.

### Disabled Schedules (Sessions 1027, 1029)

3 remediation execution schedules disabled (PR #1271) + 3 metric trigger rules disabled (PRs #1283, #1284). Discovery + assignment still run. Beat schedules persisted in DB — commenting out code alone does NOT disable them; must also `PeriodicTask.objects.filter(name='...').update(enabled=False)`.

### Three Agent Dispatch Systems (Session 1029)

Agents are dispatched from 3 independent paths (plus 3 secondary paths). Disabling one does NOT stop the others:

| System | File | Mechanism |
|--------|------|-----------|
| A: `run_*_agents()` | `core/tasks.py` | 19 group schedules via `_run_agent_group()` |
| B: `AGENT_WORKSPACE_REGISTRY` | `core/tasks.py` | `agent_category_rotation()` iterates registry |
| C: `MetricsActionTrigger` | `core/services/metrics_action_trigger.py` | Condition-based triggers from live metrics |
| +: `workspace_autopilot_tick()` | `core/tasks.py` | CATEGORY_AGENTS / TYPE_AGENTS maps |
| +: Dream pipeline | `core/services/dream_execution_pipeline.py` | DREAM_TO_WORKFLOW agent lists |
| +: Podcast generation | `core/tasks.py` | `auto_generate_podcast_episode()` |

## Key Task Categories

**Body Systems (10-30 min intervals):** run_spine_health_check, run_circulatory_check, run_digestive_check, run_immune_scan, run_muscular_check

**Data Ingestion:** collect_real_opportunities (15m), run_spider_network (15m), process_core_spider_data (2m), scan_spider_opportunities (30m)

**Session 1034 Schedule Throttling:** spider warm-up 4h→6h, clean stale data 24h→48h, refresh AI opportunities 30m→2h, dream execution 2h→4h. Reduces Railway costs ~40% for these 4 tasks.

**Session 1034 Media Task Guard:** `_MEDIA_AGENTS` frozenset (ImageAgent, VideoAgent, AudioAgent, ThreeDAgent) + `_MEDIA_GENERATION_PATTERN` regex. Two-layer defense: pre-dispatch filter in `ConversationActionDispatcher` + fallback in `execute_agent_task`. Blocks non-generative tasks like "List recent images".

**Learning & Intelligence:** run_learning_loop_cycle (6h), mine_learning_patterns (12h), discover_success_patterns (6h)

**Content Generation:** generate_self_blog_task (6h), generate_self_blog_deliberation_task (on-demand), generate_podcast_task (on-demand), auto_enhance_blogs (4h, Session 1033), enhance_all_blogs_needing_enhancement (6h), reevaluate_enhanced_blogs (6h), auto_publish_approved_blogs (daily 6AM)

**Quality Scoring:** score_unscored_deliverables (6h, Session 1033)

**Attention & Orchestration:** generate_human_attention_items (15m), process_human_attention_lifecycle (10m), enrich_boardroom_ml_predictions (15m), process_spider_actions (30m), process_gate_progression (15m)

**Sports Pipeline (Sessions 1010-1011, 8 scheduled tasks — fully automated):**

| Task | Schedule | Purpose |
|------|----------|---------|
| `collect_sports_odds` | Every 20 min | Ingest odds from TheOddsSpider |
| `generate_game_predictions` | Every 2h | Run GamePredictor → MLPrediction rows |
| `update_game_scores` | Every 30 min | Fetch final scores from TheOddsSpider, mark Games FINAL |
| `evaluate_completed_predictions` | Hourly | Compare predictions to outcomes, set was_correct |
| `verify_betting_outcomes` | Every 30 min | Settle PlacedWager legs, verify arb items |
| `settle_user_bets` | Every 15 min | Update wager statuses |
| `generate_accuracy_report` | Daily 9 AM | Model performance summary |
| `cleanup_old_predictions` | Weekly Mon 3 AM | Remove stale data |

## Observability (Session 983)

**Problem:** `django_celery_results.TaskResult` is empty when `CELERY_RESULT_BACKEND=redis`.

**Solution:** `CeleryTaskEvent` model in `core/models_celery_telemetry.py`, populated by signal handlers in `core/celery_telemetry.py`:
- Signals: `task_prerun`, `task_postrun`, `task_failure`
- Fields: task_id, task_name, queue, status, worker, started_at, finished_at, duration_seconds, error_type, error_message
- Used by: status_snapshot_tool (PA), system_health_tool, nervous system message stats, task_breakdown_tool (PA)

### Task Volume Breakdown (Session 1048)

Two REST endpoints + PA tool for one-click task load analysis, querying `CeleryTaskEvent` directly:

| Endpoint | Purpose |
|----------|---------|
| `GET /api/celery/breakdown/?window=60m&limit=25` | Aggregated totals, by-task (with p50/p95 percentiles), by-agent breakdown |
| `GET /api/celery/breakdown/task/?task_name=core.tasks.xyz&window=60m` | Drill-down into a specific task name |

**PA tool:** `task_breakdown_tool` with `summary` and `drilldown` actions. Triggered by "what's driving load?", "top failing tasks", "task volume", etc.

**Window options:** 15m, 60m, 2h, 6h, 24h. **Percentile calculation:** Python-side from sorted duration lists (manageable data volume).

## ML Import Chain

ALL heavy ML imports (torch, sklearn, transformers) MUST be lazy — inside methods or wrapped in `try/except ImportError`. Module-level imports loaded ~800MB into Celery parent process. `ml_engine.py` uses `_detect_device()` helper for lazy torch.

## PA Async Flow

1. `POST /api/pa/chat/` dispatches `process_pa_chat_task.delay()` → returns `{task_id}` immediately
2. Task runs on dedicated `pa` queue with `time_limit=300s`
3. Frontend polls `GET /api/pa/chat/status/<task_id>/` every 2s
4. Uses `new_event_loop()` + `run_until_complete()` (not `async_to_sync`, which deadlocks)

Production latency: 3-64s (previously 280s+ timeout).
