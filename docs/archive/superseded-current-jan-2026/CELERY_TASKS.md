<!-- ARCHIVED-DOC-V1 -->
> # ⛔ ARCHIVED — 2026-04-26 (Session 1100)
>
> This doc was retired during the Session 1099 → 1100 doc-drift cleanup
> because its stats diverged materially from runtime reality. **Content
> below is preserved unchanged for historical reference and potential
> future book material** (Chris's "how I learned to work with AI to build
> this platform").
>
> **What this used to be:** Celery task catalog snapshot
>
> **Where to look now:**
> - [docs/topics/celery-workers.md](/docs/topics/celery-workers.md)
>
> **Source of truth for live numbers:** `docs/PLATFORM_INVENTORY.md`
> (regenerable via `python manage.py generate_platform_inventory`).

---

# Celery Tasks Documentation

**Total Tasks:** 127+
**Scheduled Tasks:** 53
**Location:** `core/tasks.py` (18,000+ lines)
**Beat Schedules:** `core/celery.py`
**Last Updated:** January 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Task Categories](#task-categories)
3. [Celery Beat Schedules](#celery-beat-schedules)
4. [Key Tasks Detail](#key-tasks-detail)
5. [Usage](#usage)

---

## Overview

Celery tasks handle all background processing including spider collection, agent conversations, dream generation, autonomous situations, and more.

### Architecture
```
Redis (Broker)
     │
     ▼
Celery Workers (3 queues)
├── default          # Standard tasks
├── long_running     # Extended tasks
└── broadcast        # WebSocket updates
     │
     ▼
Celery Beat (Scheduler)
     │
     ▼
53 Scheduled Tasks
```

### Starting Celery
```bash
make celery           # Start all workers + beat
make celery-status    # Check status
```

---

## Task Categories

### Spider Tasks (10)

| Task | Purpose | Schedule |
|------|---------|----------|
| `run_spider_network` | Run full spider network | Weekly |
| `run_spider_by_category` | Run category spiders | Various |
| `execute_single_spider` | Run one spider | On-demand |
| `collect_spider_data` | Collect from all spiders | Every 30 min |
| `cleanup_old_spider_data` | Clean old data | Daily |
| `generate_spider_embeddings` | Generate embeddings | After collection |
| `sync_spider_to_knowledge` | Sync to knowledge pipeline | After collection |
| `trigger_spider_conversations` | Spider-triggered convos | Hourly |
| `deduplicate_spider_data` | Remove duplicates | Daily |
| `run_priority_spiders` | High-priority only | Every 15 min |

### Agent Conversation Tasks (8)

| Task | Purpose | Schedule |
|------|---------|----------|
| `run_agent_conversation` | Single agent conversation | Every 2 hours |
| `run_multi_agent_conversation` | Multi-agent debate | Every 4 hours |
| `run_project_conversation` | Project-focused convo | On-demand |
| `broadcast_conversation_status` | WebSocket updates | Real-time |
| `trigger_spider_conversations` | Spider data → convos | Hourly |
| `cleanup_stale_conversations` | Clean old convos | Daily |
| `score_conversations` | Quality scoring | After completion |
| `extract_conversation_insights` | Extract learnings | After completion |

### Dream Tasks (8)

| Task | Purpose | Schedule |
|------|---------|----------|
| `generate_agent_dreams` | Generate agent dreams | Every 3 hours |
| `generate_directed_dreams` | Topic-specific dreams | On-demand |
| `score_and_promote_dreams` | Score & promote to boardroom | Every 4 hours |
| `broadcast_dream_journal` | WebSocket updates | After generation |
| `process_approved_dreams` | Execute approved dreams | Hourly |
| `cleanup_stale_dreams` | Clean old dreams | Daily |
| `execute_dream_implementations` | Implement dreams | Every 6 hours |
| `explore_dream_topic` | Deep dream exploration | On-demand |

### Hive Mind Tasks (4)

| Task | Purpose | Schedule |
|------|---------|----------|
| `run_hive_mind_session` | Collective intelligence | On-demand |
| `score_hive_outputs` | Score outputs | After session |
| `promote_hive_decisions` | Promote to boardroom | After scoring |
| `cleanup_hive_sessions` | Clean old sessions | Daily |

### Autonomous Situation Tasks (10)

| Task | Purpose | Schedule |
|------|---------|----------|
| `run_market_intelligence_desk` | Daily market briefs | 6:30 AM weekdays |
| `check_market_events_and_rerun` | Event-triggered rerun | On events |
| `run_autonomous_content_studio` | Content generation | Every 4 hours |
| `generate_content_for_channel` | Per-channel content | On-demand |
| `track_content_performance` | Performance tracking | Daily 8 PM |
| `run_narrative_drift_detection` | Narrative monitoring | Every 6 hours |
| `run_blockchain_audit` | Blockchain monitoring | Every 15 min |
| `run_stock_audit` | Stock monitoring | Market hours |
| `process_situation_triggers` | Trigger processing | Real-time |
| `cleanup_situation_logs` | Clean old logs | Weekly |

### Learning Loop Tasks (8)

| Task | Purpose | Schedule |
|------|---------|----------|
| `record_learning_event` | Record learning | On events |
| `track_prediction_outcomes` | Track predictions | Daily |
| `calculate_agent_accuracy` | Calculate accuracy | Weekly |
| `retrain_ml_model` | Retrain XGBoost | Weekly (if needed) |
| `propagate_new_policies` | Propagate policies | Every 2 hours |
| `auto_resolve_knowledge_gaps` | Fill knowledge gaps | Daily |
| `sync_learning_to_agents` | Sync to agents | After learning |
| `generate_learning_report` | Learning analytics | Weekly |

### Content Pipeline Tasks (8)

| Task | Purpose | Schedule |
|------|---------|----------|
| `generate_content_package` | Generate package | On-demand |
| `generate_ai_series` | Generate series | On-demand |
| `process_distribution` | Distribute content | After generation |
| `track_content_roi` | ROI tracking | Daily |
| `cleanup_old_packages` | Clean old packages | Weekly |
| `generate_thumbnails` | Generate thumbnails | On-demand |
| `watermark_content` | Apply watermarks | On generation |
| `export_content` | Export to platforms | On-demand |

### Workflow Tasks (6)

| Task | Purpose | Schedule |
|------|---------|----------|
| `execute_scheduled_workflow` | Run scheduled workflow | On schedule |
| `process_workflow_step` | Process single step | On-demand |
| `track_workflow_progress` | Progress tracking | Real-time |
| `retry_failed_steps` | Retry failures | Every 15 min |
| `cleanup_completed_workflows` | Clean old workflows | Daily |
| `generate_workflow_report` | Analytics | Weekly |

### Document Processing Tasks (6)

| Task | Purpose | Schedule |
|------|---------|----------|
| `process_document_async` | Process uploaded doc | On upload |
| `process_url_async` | Process URL | On submit |
| `generate_document_embeddings` | Generate embeddings | After processing |
| `isolate_documents_batch` | Batch isolation | Daily |
| `cleanup_old_documents` | Clean old docs | Monthly |
| `ocr_scanned_documents` | OCR processing | On upload |

### Sci-Fi Feature Tasks (15)

| Task | Purpose | Schedule |
|------|---------|----------|
| `update_agent_mood` | Update moods | Every 30 min |
| `check_mood_expirations` | Expire old moods | Hourly |
| `apply_mood_trigger_rules` | Apply triggers | On events |
| `evolve_agent_relationships` | Update relationships | Daily |
| `update_alliance_strengths` | Alliance tracking | Daily |
| `broadcast_relationship_status` | WebSocket updates | On change |
| `process_agent_activity_xp` | XP processing | On activity |
| `check_level_milestones` | Level-up checks | On XP gain |
| `broadcast_evolution_status` | WebSocket updates | On level-up |
| `backfill_memory_embeddings` | Backfill embeddings | Daily |
| `process_time_capsules` | Open time capsules | Daily |
| `generate_personality_insights` | Personality analysis | Weekly |
| `sync_memory_palace` | Memory sync | Hourly |
| `cleanup_old_memories` | Memory cleanup | Monthly |
| `generate_agent_report_card` | Agent analytics | Weekly |

### DaVinci Resolve Tasks (4)

| Task | Purpose | Schedule |
|------|---------|----------|
| `start_resolve_render` | Start render job | On-demand |
| `poll_resolve_job_status` | Poll job status | During render |
| `record_resolve_outcome` | Record for learning | On completion |
| `cleanup_old_resolve_jobs` | Clean old jobs | Weekly |

### Notification Tasks (4)

| Task | Purpose | Schedule |
|------|---------|----------|
| `send_discord_notification` | Discord messages | On events |
| `send_push_notification` | Push notifications | On events |
| `send_email_notification` | Email alerts | On events |
| `broadcast_websocket` | WebSocket updates | Real-time |

### Governance Tasks (6)

| Task | Purpose | Schedule |
|------|---------|----------|
| `auto_promote_decisions` | Auto-promote decisions | Every 4 hours |
| `process_pilot_gates` | Process pilot gates | Hourly |
| `check_pilot_completions` | Check completions | Every 2 hours |
| `generate_governance_report` | Governance analytics | Weekly |
| `cleanup_old_decisions` | Clean old decisions | Monthly |
| `sync_boardroom_to_pilots` | Sync to pilots | On approval |

---

## Celery Beat Schedules

### Every 15 Minutes
- `run_priority_spiders`
- `run_blockchain_audit`
- `retry_failed_steps`

### Every 30 Minutes
- `collect_spider_data`
- `update_agent_mood`

### Hourly
- `trigger_spider_conversations`
- `check_mood_expirations`
- `process_approved_dreams`
- `process_pilot_gates`
- `sync_memory_palace`

### Every 2 Hours
- `run_agent_conversation`
- `propagate_new_policies`
- `check_pilot_completions`

### Every 3 Hours
- `generate_agent_dreams`

### Every 4 Hours
- `run_multi_agent_conversation`
- `run_autonomous_content_studio`
- `score_and_promote_dreams`
- `auto_promote_decisions`

### Every 6 Hours
- `run_narrative_drift_detection`
- `execute_dream_implementations`

### Daily
| Time | Task |
|------|------|
| 1:00 AM | `collect_training_data` |
| 3:00 AM | `cleanup_old_spider_data` |
| 3:30 AM | `retrain_ml_model` (Sunday) |
| 6:30 AM | `run_market_intelligence_desk` |
| 8:00 PM | `track_content_performance` |
| 11:00 PM | `evolve_agent_relationships` |
| 11:30 PM | `auto_resolve_knowledge_gaps` |

### Weekly (Sunday)
- `run_spider_network` (full)
- `calculate_agent_accuracy`
- `generate_learning_report`
- `cleanup_situation_logs`

---

## Key Tasks Detail

### run_spider_network
```python
@shared_task(bind=True)
def run_spider_network(self):
    """Run all spiders in the network"""
    registry = SpiderRegistry()
    for spider_name in registry.get_all_spiders():
        execute_single_spider.delay(spider_name)
```

### generate_agent_dreams
```python
@shared_task(bind=True)
def generate_agent_dreams(self, max_dreamers=5, dreams_per_agent=2):
    """Generate creative dreams from idle agents"""
    # Select agents with low recent activity
    # Generate dreams using GPT
    # Score dreams for quality
    # Broadcast to Discord
```

### run_market_intelligence_desk
```python
@shared_task(name='core.tasks.run_market_intelligence_desk')
def run_market_intelligence_desk():
    """Generate daily market brief with bull/bear debate"""
    # Run BullCaseAgent and BearCaseAgent
    # Synthesize into brief
    # Generate TTS audio
    # Post to Discord
```

### run_autonomous_content_studio
```python
@shared_task(name='autonomous_studio.run_main_loop')
def run_autonomous_content_studio():
    """Run autonomous content generation cycle"""
    # For each active channel:
    #   Run TopicMiner vs Contrarian debate
    #   Select winning topic
    #   Generate content
    #   Track for learning
```

---

## Usage

### Call Task Immediately
```python
from core.tasks import generate_agent_dreams

# Synchronous (testing only)
result = generate_agent_dreams()

# Asynchronous
result = generate_agent_dreams.delay()
task_id = result.id
```

### Call with Arguments
```python
from core.tasks import execute_single_spider

execute_single_spider.delay('hackernews')
```

### Call with Countdown
```python
from core.tasks import send_notification

# Run in 60 seconds
send_notification.apply_async(args=['message'], countdown=60)
```

### Call with ETA
```python
from datetime import datetime, timedelta
from core.tasks import run_report

# Run at specific time
eta = datetime.now() + timedelta(hours=2)
run_report.apply_async(eta=eta)
```

### Check Task Status
```python
from celery.result import AsyncResult

result = AsyncResult(task_id)
print(result.status)  # PENDING, STARTED, SUCCESS, FAILURE
print(result.result)  # Return value if SUCCESS
```

### Revoke Task
```python
from celery.result import AsyncResult

result = AsyncResult(task_id)
result.revoke(terminate=True)
```

---

## Monitoring

### CLI Commands
```bash
# List active tasks
celery -A core inspect active

# List scheduled tasks
celery -A core inspect scheduled

# List reserved tasks
celery -A core inspect reserved

# Purge all tasks
celery -A core purge
```

### Flower (Web UI)
```bash
pip install flower
celery -A core flower
# Open http://localhost:5555
```

---

## Related Documentation

- [AUTONOMOUS_SYSTEMS.md](AUTONOMOUS_SYSTEMS.md) - Autonomous situations using tasks
- [SERVICES.md](SERVICES.md) - Services called by tasks
- [SPIDERS.md](SPIDERS.md) - Spider tasks