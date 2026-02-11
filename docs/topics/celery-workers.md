# Celery & Workers

261 Celery tasks across 7 worker types with queue-based routing, memory management, and observability via CeleryTaskEvent signals.

## Worker Types (7)

| Worker | Queue(s) | Pool | Memory Limit | Task Recycling | Purpose |
|--------|----------|------|-------------|----------------|---------|
| celery-worker | default, agents, sports, ml | prefork (Railway) / threads (macOS) | 200MB | 50 tasks | General tasks |
| celery-pa | pa | prefork | 200MB | 50 tasks | PA chat queries (dedicated to prevent queue starvation) |
| celery-content | content | prefork | 200MB | 30 tasks | Blog generation, podcasts, initiative stages |
| celery-long-running | long_running | prefork | 300MB | 10 tasks | Spider network, agent conversations, dreams |
| celery-broadcast | broadcast | prefork | 200MB | 50 tasks | High-frequency status updates (60-180s) |
| celery-beat | (scheduler) | — | — | — | DatabaseScheduler, dispatches scheduled tasks |

## Pool Configuration

**Railway (Linux):** `--pool=prefork -c 1` enables child process recycling via `max_tasks_per_child`. Memory caps enforced via `--max-memory-per-child`.

**macOS Local:** MUST use `--pool=threads` (prefork causes SIGSEGV on Darwin). `max_tasks_per_child` is a NO-OP with threads. Set `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES`.

**Memory budget:** Parent ~200MB + 1 child at 200MB = ~400MB (safe for Railway). Previously with `-c 2` + 300MB children = 800MB (OOM).

## Task Routing (settings.py)

Tasks routed by module and explicit name:
- `core.tasks.process_pa_chat_task` → `pa` queue
- `agents.*` → `agents` queue
- `sports.*` → `sports` queue
- Content/blog tasks → `content` queue
- Spider/conversation tasks → `long_running` queue
- Status update tasks → `broadcast` queue
- Default: `default` queue

## Key Task Categories

**Body Systems (10-30 min intervals):** run_spine_health_check, run_circulatory_check, run_digestive_check, run_immune_scan, run_muscular_check

**Data Ingestion:** collect_real_opportunities (15m), run_spider_network (15m), process_core_spider_data (2m), scan_spider_opportunities (30m)

**Learning & Intelligence:** run_learning_loop_cycle (6h), mine_learning_patterns (12h), discover_success_patterns (6h)

**Content Generation:** generate_self_blog_task (6h), generate_self_blog_deliberation_task (on-demand), generate_podcast_task (on-demand)

**Attention & Orchestration:** generate_human_attention_items (15m), process_human_attention_lifecycle (10m), enrich_boardroom_ml_predictions (15m), process_spider_actions (30m), process_gate_progression (15m)

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
