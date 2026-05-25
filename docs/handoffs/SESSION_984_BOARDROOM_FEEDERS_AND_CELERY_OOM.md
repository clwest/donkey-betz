---
originating_session: 984
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 984 -- Boardroom Feeder Fix + Celery Worker OOM

**Date:** February 9, 2026
**Previous Session:** 983 (Celery Observability Fix + Skin Health Scoring)
**PRs:** #1043, #1044

---

## Problem 1: Boardroom Attention Items Stale (2/8 or Older)

All Boardroom tabs (All, Review, Alert, Opportunity) showed items from 2/8/26 or older. Only Insights had current-date items.

**Root cause (two-sided):**

1. **Auto-approve too aggressive:** `auto_approve_boardroom_items` ran every 4h and set ALL non-critical pending items to `status='acted'`. UI only queries `status='pending'`, so items disappeared within hours.
2. **Feeders effectively dead:** `generate_human_attention_items` Section 4 filtered `data_type__in=['market_alert', 'security_alert', 'price_alert', 'breaking_news']` -- **none of these match any actual spider data_type**. Real types are: `opportunity`, `market_data`, `news`, `trend_data`, `competitor_info`, etc. Section 2 only monitored 6 hardcoded agent names.

## Solution 1: PR #1043

### Part A: 24h Age Gate on Auto-Approve

**File:** `core/tasks.py` -- `auto_approve_boardroom_items()` (~line 480)

Added `age_cutoff = now - timedelta(hours=24)` and `created_at__lt=age_cutoff` to all 4 auto-approve queries (insights, reviews, opportunities, spider_actions). Items now stay visible in the Boardroom for a full day before auto-clearing.

### Part B: Wider Feeder Filters

**File:** `core/tasks.py` -- `generate_human_attention_items()` (~line 25037)

| Section | Before | After |
|---------|--------|-------|
| 2 (agent failures) | 6 hardcoded agent names, 1h window, 10 limit | All agents, 4h window, 20 limit |
| 4 (spider data) | `data_type__in` with non-existent values | Fixed to real types: `opportunity`, `market_data`, `news`, `trend_data`, `competitor_info` |
| 5 (new) | -- | `StockMarketAlert` objects from last 4h (risk_alert/anomaly = high urgency) |
| 6 (new) | -- | `SelfBlog` with `publish_ready=True` from last 24h (low urgency review items) |

**No dedup issue:** `create_attention_item` in `human_interface_service.py` (line 554) has built-in dedup that skips items with matching `source_type` + `item_type` + `title` when a pending/viewed item already exists.

---

## Problem 2: Celery Worker OOM on Railway (3 Emails Overnight)

Railway's celery-worker service crashing with out-of-memory errors.

**Root cause:** `--pool=threads` makes `CELERY_WORKER_MAX_TASKS_PER_CHILD=100` a no-op. Threads share one process -- memory never recycles. With 261+ tasks, LLM API calls (50-200MB), and spider loads (150-500MB), memory grew linearly until Railway killed the service.

## Solution 2: PR #1044

### Procfile Changes

All Railway workers switched from `--pool=threads` to `--pool=prefork` (safe on Linux):

| Worker | Before | After |
|--------|--------|-------|
| celery-worker | threads, -c 4, 5 queues | prefork, -c 2, 4 queues (dropped `pa`) |
| celery-pa | threads, -c 2 | prefork, -c 2 |
| celery-content | threads, -c 4 | prefork, -c 2 |
| celery-long-running | threads, -c 2 | prefork, -c 1, max-memory 500MB |
| celery-broadcast | threads, -c 2 | prefork, -c 2 |

All workers now have:
- `--max-tasks-per-child=50` (recycle child after 50 tasks)
- `--max-memory-per-child=300000` (300MB hard kill per child, 500MB for long-running)

### Settings Changes (`core/settings.py`)

- `CELERY_WORKER_PREFETCH_MULTIPLIER`: 4 -> 1 (don't pre-load tasks into memory)
- `CELERY_WORKER_MAX_TASKS_PER_CHILD`: 100 -> 50 (aligned with Procfile)
- Added `CELERY_WORKER_MAX_MEMORY_PER_CHILD = 300_000`

### macOS Safety

Local dev unaffected -- `Makefile` uses `--pool=threads` (prefork causes SIGSEGV on macOS due to fork() + Objective-C runtime).

---

## Key Gotchas

- **Spider `data_type` values:** Real types from `base_spider.py` line 354: `opportunity`, `job_posting`, `market_data`, `competitor_info`, `trend_data`, `user_feedback`, `product_info`, `pricing_data`, `content_idea`, `collaboration`, `news`, `research`, `tool_discovery`, `learning_resource`. Default fallback is `'research'`.
- **`--pool=threads` vs `--pool=prefork`:** Threads = shared memory, no recycling. Prefork = child processes, recycled via `max_tasks_per_child` and `max_memory_per_child`. Always use prefork on Linux (Railway), threads on macOS (local).
- **Boardroom dedup:** `create_attention_item` has built-in dedup (line 554 of `human_interface_service.py`). Checks `source_type` + `item_type` + `title` against pending/viewed/deferred items.
- **Auto-approve vs signal handler:** The Django signal `on_agent_execution_complete` in `human_attention_bridge.py` still uses a narrow 5-agent list for real-time alerts. The task feeder uses all agents on a 15-min schedule. This is intentional dual-layer coverage.

---

## Verification

- `py_compile` passes on `core/tasks.py` and `core/settings.py`
- No new Pyright errors (all warnings are pre-existing)
- No migrations needed
