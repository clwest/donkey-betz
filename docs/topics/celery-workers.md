# Celery & Workers

271 Celery tasks across 7 worker types with queue-based routing, memory management, and observability via CeleryTaskEvent signals. Session 1000C: Routed 60+ heavy tasks off default queue to prevent OOM. Session 1029: Rerouted 5 additional heavy tasks from default to long_running to fix recurring OOM crashes. Session 1033: Added auto_enhance_blogs + score_unscored_deliverables. Session 1034: Throttled 4 beat schedules (~40% fewer runs), media task guard, workspace path self-healing.

## Worker Types (7)

| Worker | Queue(s) | Pool | Memory Limit | Task Recycling | Purpose |
|--------|----------|------|-------------|----------------|---------|
| celery-worker | default, agents, sports | prefork (Railway) / threads (macOS) | 200MB | 10 tasks | Lightweight DB-query tasks only (~28 tasks) |
| celery-pa | pa | prefork | 200MB | 50 tasks | PA chat queries (dedicated to prevent queue starvation) |
| celery-content | content | prefork | 150MB | 10 tasks | Blog generation, podcasts, initiative stages (~19 tasks) |
| celery-long-running | long_running, ml | prefork | 300MB | 10 tasks | Agent exercises, LLM calls, embeddings, spiders (~52 tasks) |
| celery-broadcast | broadcast | threads | 200MB | 50 tasks | High-frequency status updates (60-180s, ~4 tasks) |
| celery-beat | (scheduler) | — | — | — | Drives 108 beat schedule entries from settings.py |

## Pool Configuration

**Railway (Linux):** `--pool=prefork -c 1` enables child process recycling via `max_tasks_per_child`. Memory caps enforced via `--max-memory-per-child`.

**macOS Local:** MUST use `--pool=threads` (prefork causes SIGSEGV on Darwin). `max_tasks_per_child` is a NO-OP with threads. Set `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES`.

**Memory budget:** Parent ~200MB + 1 child at 200MB = ~400MB (safe for Railway 512MB limit).

## Task Routing (settings.py CELERY_TASK_ROUTES)

108 beat schedule entries in `CELERY_BEAT_SCHEDULE` (settings.py) have NO explicit `options.queue` — routing is entirely driven by `CELERY_TASK_ROUTES`:

| Queue | # Tasks | Categories |
|-------|---------|------------|
| default | ~24 | Light DB queries, body system checks, attention lifecycle, deliverable scoring |
| long_running | ~55 | Agent exercises (18), autonomous situations (14), pipeline execution, spider network, intelligence desks, blog enhancement, multi-agent conversations, hivemind sessions, dream execution |
| content | ~22 | Blog generation, podcasts, initiative stages, content deliberation, blog re-evaluation, auto-publish, auto-enhance blogs |
| sports | ~8 | Odds collection, prediction generation, score fetching, evaluation, verification, settlement, accuracy reports |
| broadcast | ~4 | Status snapshots, heartbeat, nervous system |
| ml | ~3 | Embedding backfills, ML model training/scoring |
| pa | 1 | process_pa_chat_task |

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
| `execute_agent_task` | 300-500MB | AgentRouter loads all 92 agents | long_running |
| `run_spider_by_category` | 400-800MB | SpiderRegistry + spider execution | long_running |
| `execute_single_spider` | 400-800MB | Full spider execution, data collection | long_running |
| `execute_single_spider_lightweight` | 200-400MB | Spider instantiation + fetch | long_running |
| `produce_content_package` | 400-800MB | ContentProductionOrchestrator + multi-agent | long_running |
| `run_hive_mind_session` | 300-600MB | OpenAI API calls for 10+ agents | long_running |
| `explore_dream_topic` | 300-500MB | LLM API calls | long_running |
| `evaluate_pilots_with_thinking_agent` | 200-400MB | ThinkingAgent LLM calls | long_running |
| `run_learning_loop_cycle` | 300-500MB | LearningLoopOrchestrator | long_running |

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
- Used by: status_snapshot_tool (PA), system_health_tool, nervous system message stats

## ML Import Chain

ALL heavy ML imports (torch, sklearn, transformers) MUST be lazy — inside methods or wrapped in `try/except ImportError`. Module-level imports loaded ~800MB into Celery parent process. `ml_engine.py` uses `_detect_device()` helper for lazy torch.

## PA Async Flow

1. `POST /api/pa/chat/` dispatches `process_pa_chat_task.delay()` → returns `{task_id}` immediately
2. Task runs on dedicated `pa` queue with `time_limit=300s`
3. Frontend polls `GET /api/pa/chat/status/<task_id>/` every 2s
4. Uses `new_event_loop()` + `run_until_complete()` (not `async_to_sync`, which deadlocks)

Production latency: 3-64s (previously 280s+ timeout).
