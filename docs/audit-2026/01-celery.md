# Dossier #1: Celery Orchestration + Runtime Truth

**Audited:** April 6, 2026
**Status:** WORKING (token-conservation mode)

---

## 1. Purpose

Celery is the execution backbone — every autonomous action on the platform (spider crawls, agent execution, content generation, signal analysis, learning loops) flows through it. Without Celery running, the platform is a static website.

## 2. Runtime Evidence

- **413 registered tasks** across 25 modules
- **48 active Beat-scheduled tasks** (health + cleanup + spiders + signals)
- **~1,200+ task instances/day** from Beat alone
- **9 queues** routing by resource profile
- **CeleryTaskEvent** telemetry records every task start/finish/failure
- Local worker logs confirm tasks executing every 5-30 minutes

## 3. Entry Points

| Trigger | Example | How |
|---------|---------|-----|
| **Beat scheduler** | `run_spider_network` every 30m | `core/celery.py` line 166 |
| **Django signals** | ConceptForge on SelfBlog publish | `core/signals/conceptforge_signals.py` |
| **API endpoints** | PA chat → `process_pa_chat_task` | `core/views_pa.py` → Celery `.delay()` |
| **Agent router** | Heavy tools dispatch async | `core/services/tool_dispatcher.py` |
| **Manual** | Django admin, management commands | `task.delay()` or `task.apply_async()` |

## 4. Execution Chain

Example: Spider Network (the most critical scheduled task)

```
Beat (every 30m)
  → core.tasks.run_spider_network [queue: long_running]
    → core/tasks_spiders.py:_impl_run_spider_network
      → GovernanceState check (freeze/safe_mode → skip)
      → SpiderRegistry.list_spiders() → 77 spiders
      → Per-spider: collect_spider_data_sync() → REAL web fetch
      → Store as SpiderData records
      → Record SpiderExecutionLog
  
  Parallel (triggered by Beat on same cadence):
    → process_core_spider_data (every 5m) → dedup, embed, quality
    → backfill_spider_embeddings (every 15m) → batch embed via OpenAI
    → aggregate_spider_signals (every 30m) → cluster into signals
    → scan_spider_opportunities (every 30m) → find opportunities
    → process_spider_actions (every 30m) → create action items
```

Key files:
- `core/celery.py:24-227` — Beat schedule
- `core/tasks.py` — 345 tasks, main router
- `core/tasks_spiders.py:315-400` — Spider execution
- `core/tasks_agents.py:4509-4750` — Agent workspace output
- `core/settings.py:956-1200` — Queue routing

## 5. Data Contracts

| Model | Table | Purpose | Key Fields |
|-------|-------|---------|------------|
| CeleryTaskEvent | core_celerytaskevent | Per-task telemetry | task_name, status, started_at, finished_at, rss_mb_start/end |
| SpiderData | core_spiderdata | Raw spider output | spider_name, source_url, data_type, raw_data, embedding |
| SpiderExecutionLog | core_spiderexecutionlog | Spider run metrics | spider_name, duration, items_collected, celery_task_id |
| AgentExecution | core_agentexecution | Agent run records | agent, status, input_data, created_at |
| WorkspaceOperation | core_workspaceoperation | Skin layer output | workspace, agent_name, success, run_mode |

## 6. External Dependencies

| Dependency | Used By | Env Var |
|------------|---------|---------|
| Redis (broker) | All tasks | `CELERY_BROKER_URL` (redis://localhost:6379/2) |
| Redis (results) | Task results | `CELERY_RESULT_BACKEND` (redis://localhost:6379/3) |
| OpenAI API | Embedding backfill, agent execution | `OPENAI_API_KEY` |
| Various web sources | 77 spiders | URLs hardcoded in spider classes |

## 7. Outputs/Artifacts

What the user actually sees from Celery activity:
- **Deliverables** — agent-produced documents in workspace tabs
- **Blogs** — auto-generated content in Content Studio
- **Spider data** — feeds Intelligence tab, signal clusters
- **Initiatives** — auto-created from conversation → initiative pipeline
- **Attention items** — surfaced in Home tab
- **System health** — Body Systems vitals (HEART, BRAIN, LUNGS, etc.)

## 8. Failure Modes

| Failure | Cause | Impact | Mitigation |
|---------|-------|--------|------------|
| OOM crash | Large embedding batch or heavy LLM call | Worker dies, task requeued | max-memory-per-child=300MB, max-tasks=50 |
| Task timeout | LLM API slow (>25min) | Soft kill, logged | soft_time_limit=25m, hard=30m |
| Redis disconnect | Redis restart/OOM | All workers lose connection | broker_heartbeat=120s, acks_late=True |
| Duplicate dispatch | Beat fires before previous completes | Same task runs twice | Dedup guard added (Session 1085, 10min cache lock) |
| Agent blocked | AgentControlEntry DB | Task skips silently | Logged, returns early |

## 9. Current Status: WORKING (Token-Conservation Mode)

**What's running (48 tasks):**
- Health checks (heartbeat, celery health) — every 10-30m
- 25 cleanup tasks — daily/weekly
- Spider network + processing — every 5-30m
- Signal aggregation + opportunity scanning — every 30m
- Dream surfacing — daily 9am

**What's DISABLED (to save API tokens):**
- Agent exercise rotations (content, research, strategy, market, etc.)
- Content generation (blog auto-gen, podcast, deliberation)
- Initiative orchestration
- Intelligence loops
- Dream generation cycles
- Learning loop cycles
- All agent conversation triggers

**To re-enable:** Uncomment disabled schedules in `core/celery.py:24-227` or trigger tasks manually via `task.delay()`.

## 10. Truth Gaps

- **Actual token cost per cycle**: Unknown — need to trace LLM calls per task and sum costs
- **Task success rate**: CeleryTaskEvent exists but hasn't been queried for aggregate rates
- **Queue backlog depth**: No monitoring dashboard for Redis queue lengths
- **Which spiders actually return useful data**: 77 registered but "5 need API keys" — need per-spider audit
- **Task dependency chain**: No explicit chaining (all Beat-triggered in parallel) — some tasks assume prior task completed but don't verify
