# Session 381: Collective Intelligence Architecture - Complete System Documentation

## Overview

This document provides a comprehensive explanation of how the 29 agents, 102 spiders, and learning infrastructure work together to create a self-improving collective intelligence system.

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COLLECTIVE INTELLIGENCE SYSTEM                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐       │
│  │   USER INPUT    │────▶│ AGENT EXECUTION │────▶│ LEARNING HOOKS  │       │
│  │  (AI Studio)    │     │   (29 Agents)   │     │ (_record_*)     │       │
│  └─────────────────┘     └────────┬────────┘     └────────┬────────┘       │
│                                   │                       │                 │
│                                   ▼                       ▼                 │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐       │
│  │  SPIDER NETWORK │────▶│ CoordinatorOut- │◀────│ AgentMemory     │       │
│  │  (102 Spiders)  │     │ come Table      │     │ Table           │       │
│  └─────────────────┘     └────────┬────────┘     └─────────────────┘       │
│                                   │                                         │
│                                   ▼                                         │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐       │
│  │ CELERY TASKS    │────▶│ KNOWLEDGE       │────▶│ AGENT DREAMS &  │       │
│  │ (Scheduled)     │     │ TRANSFERS       │     │ CONVERSATIONS   │       │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component 1: The 29 Agents

### Agent Categories

| Category | Agents | Purpose |
|----------|--------|---------|
| **Generation** | ImageAgent, VideoAgent, AudioAgent, ThreeDAgent | Create content |
| **Strategy** | BrandIdentityAgent, ContentStrategyAgent, SEOOptimizerAgent, SocialMediaAgent | Strategic planning |
| **Executive** | COOAgent, CTOAgent, CreativeDirectorAgent, MeetingCoordinatorAgent | High-level decisions |
| **Analysis** | OpportunityScoringAgent, TrendAnalysisAgent, CompetitorAnalysisAgent, CustomerResearchAgent | Data analysis |
| **Training** | CharacterTrainingAgent, TrainedCreationAgent | Model training |
| **Workflow** | WorkflowAgent, ResearchAgent | Orchestration |
| **Business** | BrandStrategyAgent, MarketingStrategyAgent, BusinessContentStrategyAgent | Business operations |

### Learning Hooks (Added Session 380)

Every agent's `execute()` method now calls two learning hooks:

```python
def execute(self, task, context, scifi_context, spider_context):
    # ... agent logic ...

    result = AgentResult(success=True, message="...", data={...})

    # LEARNING HOOK 1: Record outcome for XP/evolution
    self._record_learning_outcome(
        result=result,
        task=task,
        context=context,
        spider_data_used=bool(spider_context),
        scifi_context_used=bool(scifi_context)
    )

    # LEARNING HOOK 2: Create memory for future retrieval
    self._create_execution_memory(
        result=result,
        task=task,
        memory_type="success",  # or "failure"
        importance=0.7  # 0.6-0.8 depending on outcome
    )

    return result
```

**Files with learning hooks:**
- `core/agents/image_agent.py`
- `core/agents/video_agent.py`
- `core/agents/audio_agent.py`
- `core/agents/three_d_agent.py`
- `core/agents/strategy/brand_identity_agent.py`
- `core/agents/strategy/content_strategy_agent.py`
- `core/agents/strategy/seo_optimizer_agent.py`
- `core/agents/strategy/social_media_agent.py`
- `core/agents/executive/coo_agent.py`
- `core/agents/executive/cto_agent.py`
- `core/agents/executive/creative_director_agent.py`
- `core/agents/executive/meeting_coordinator_agent.py`
- `core/agents/analysis/opportunity_scoring_agent.py`
- `core/agents/analysis/trend_analysis_agent.py`
- `core/agents/training/character_training_agent.py`
- `core/agents/training/trained_creation_agent.py`

---

## Component 2: The 102 Spiders

### Spider Categories

| Category | Count | Example Sources |
|----------|-------|-----------------|
| **Tech News** | 9 | TechCrunch, The Verge, Wired, MIT Tech Review, HackerNews |
| **Financial** | 8 | CoinGecko, Yahoo Finance, Etherscan, SeekingAlpha |
| **Freelance** | 5 | Toptal, Guru, PeoplePerHour, 99Designs, FlexJobs |
| **Creative** | 5 | Dribbble, Behance, Envato, CreativeMarket |
| **AI Tools** | 4 | HuggingFace, Civitai, RunwayML, Replicate |
| **Jobs** | 3 | RemoteOK, WeWorkRemotely, Adzuna |
| **News RSS** | 10+ | CNN, BBC, Reuters, NPR, Ars Technica |
| **Other** | 50+ | Reddit, Unsplash, GitHub, ProductHunt, etc. |

### Spider → Agent Data Flow

```
Spider Crawl → SpiderData Table → Spider Intelligence Service → Agent Context
```

**Key files:**
- `ai_core/spiders/spider_registry.py` - Central registry
- `ai_core/spiders/specialized/` - Individual spider implementations
- `core/services/spider_intelligence.py` - Query service

---

## Component 3: Database Tables

### Learning System Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `CoordinatorOutcome` | Records every agent execution | agents_used, outcome, execution_time_ms, confidence |
| `AgentMemory` | Persistent memories per agent | agent_id, content, importance, embedding |
| `AgentDream` | Creative thoughts during idle time | agent_id, dream_content, vividness_score |
| `AgentConversation` | Agent-to-agent discussions | participants, topic, messages |
| `KnowledgeTransfer` | When agent A teaches agent B | teacher, student, knowledge, useful |
| `LearningConnection` | Which agents learn from which | teacher_id, student_id, strength |
| `SpiderData` | Raw spider crawl results | source, title, content, url, crawled_at |

### Data Flow Example

1. **User asks:** "Create a cyberpunk logo"
2. **ImageAgent executes** with spider context (trending cyberpunk styles)
3. **Learning hook records:**
   - `CoordinatorOutcome`: agents_used="ImageAgent", outcome="success"
   - `AgentMemory`: content="Created cyberpunk logo with neon colors"
4. **Celery task `run_agent_learning_cycle`:**
   - Finds relevant knowledge to transfer
   - Creates `KnowledgeTransfer` from ImageAgent → other agents
5. **Next time:** ContentStrategyAgent sees "cyberpunk logos are trending"

---

## Component 4: Celery Tasks (Scheduled Learning)

### Learning Tasks in `core/tasks.py`

| Task | Schedule | Purpose |
|------|----------|---------|
| `run_agent_learning_cycle` | Every 30 min | Transfer knowledge between connected agents |
| `run_daily_learning_pipeline` | Daily | Comprehensive learning analysis |
| `generate_agent_dreams` | Every 2 hours | Agents dream up creative ideas |
| `run_multi_agent_conversation` | Every hour | Agents discuss topics together |
| `process_agent_activity_xp` | Every 15 min | Award XP for executions |
| `update_agent_effectiveness_from_learning` | Every hour | Update success rates |
| `broadcast_learning_status` | Every 5 min | Push stats to WebSocket |
| `run_spider_network` | Every 30 min | Crawl fresh data |

### Task Execution Flow

```
Celery Beat (Scheduler)
    │
    ├─▶ run_spider_network (crawl data)
    │       └─▶ SpiderData table filled
    │
    ├─▶ run_agent_learning_cycle
    │       ├─▶ Check LearningConnection table
    │       ├─▶ Find teachable knowledge
    │       └─▶ Create KnowledgeTransfer records
    │
    ├─▶ generate_agent_dreams
    │       ├─▶ Select idle agents
    │       ├─▶ GPT generates creative thoughts
    │       └─▶ Save to AgentDream table
    │
    └─▶ run_multi_agent_conversation
            ├─▶ Select topic from recent SpiderData
            ├─▶ 4 agents discuss in rounds
            └─▶ Save to AgentConversation table
```

---

## Component 5: Learning Bridges (Signals)

### Automatic Learning Triggers

Located in `core/apps.py`, these Django signals automatically record learning events:

```python
# Agent Execution Bridge
@receiver(post_save, sender=CoordinatorOutcome)
def on_agent_execution(sender, instance, **kwargs):
    # Record learning event when any agent executes

# Spider Data Bridge
@receiver(post_save, sender=SpiderData)
def on_spider_data(sender, instance, **kwargs):
    # Notify agents of new intelligence

# Revenue Attribution Bridge
@receiver(post_save, sender=Revenue)
def on_revenue(sender, instance, **kwargs):
    # Connect revenue to agent actions
```

### Bridges Status (from logs)
```
✅ Learning Bridges initialized - all signals registered
  - Agent Execution Bridge: ✓
  - Application Outcome Bridge: ✓
  - Revenue Attribution Bridge: ✓
  - Advisor Feedback Bridge: ✓
  - Collaboration Bridge: ✓
  - Personalization Bridge: ✓
  - Sports Betting Bridge: ✓
  - Spider Data Bridge: ✓
```

---

## Component 6: Knowledge Flow Diagram

```
                    ┌──────────────────────────────────────────────────────┐
                    │                KNOWLEDGE SOURCES                      │
                    ├──────────────────────────────────────────────────────┤
                    │  SpiderData (102 sources) │ User Interactions        │
                    │  External APIs            │ Agent Executions         │
                    └─────────────────┬────────┴─────────────┬─────────────┘
                                      │                      │
                                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           KNOWLEDGE PROCESSING                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Agent Execution                    2. Memory Creation                   │
│     ┌──────────────┐                      ┌──────────────┐                 │
│     │ ImageAgent   │──executes────────────▶│ AgentMemory  │                 │
│     │ task: logo   │                      │ importance:  │                 │
│     └──────────────┘                      │ 0.7          │                 │
│                                           └──────────────┘                 │
│                                                                             │
│  3. Outcome Recording                  4. Knowledge Transfer                │
│     ┌──────────────┐                      ┌──────────────┐                 │
│     │ Coordinator  │──────────────────────▶│ ImageAgent   │                 │
│     │ Outcome      │                      │     ↓        │                 │
│     │ success: ✓   │                      │ ContentStrat │                 │
│     └──────────────┘                      └──────────────┘                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           KNOWLEDGE UTILIZATION                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  5. Future Agent Executions           6. Agent Conversations                │
│     ┌──────────────┐                      ┌──────────────┐                 │
│     │ Next request │◀───retrieves────────│ 4 agents     │                 │
│     │ gets context │   memories          │ discuss      │                 │
│     └──────────────┘                      │ market data  │                 │
│                                           └──────────────┘                 │
│                                                                             │
│  7. Agent Dreams                       8. Decision Making                   │
│     ┌──────────────┐                      ┌──────────────┐                 │
│     │ Creative     │                      │ Better       │                 │
│     │ exploration  │──────────────────────▶│ outcomes     │                 │
│     │ during idle  │                      │ over time    │                 │
│     └──────────────┘                      └──────────────┘                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component 7: Current System State

### Session 381 Verification Results

| Metric | Value |
|--------|-------|
| **Total Agents** | 29 |
| **Agents with Learning Hooks** | 21 (code implementations) |
| **Total Spiders** | 102 |
| **Coordinator Outcomes** | 96 |
| **Agent Dreams** | 1,676 |
| **Agent Conversations** | 1,570 |
| **Knowledge Items** | 817 |
| **Learning Connections** | 37 |
| **Knowledge Transfers (24h)** | 66 |

### Top Learning Agents

| Agent | Knowledge Count | Effectiveness | Teaches | Learns From |
|-------|-----------------|---------------|---------|-------------|
| TrendAnalysisAgent | 65 | 100% | 4 | 1 |
| ContentStrategyAgent | 102 | 100% | 4 | 6 |
| ImageAgent | 34 | 100% | 1 | 9 |
| ResearchAgent | 69 | 100% | 3 | 3 |
| COOAgent | 36 | 97% | 1 | 1 |

---

## How to Start the System

```bash
# Start all services
make start          # Daphne web server on :8000
make celery         # Celery worker + beat scheduler

# Or manually:
.venv/bin/daphne -b 0.0.0.0 -p 8000 core.asgi:application &
.venv/bin/celery -A core worker --loglevel=info --pool=solo -E &
.venv/bin/celery -A core beat --loglevel=info &
```

**Note:** On macOS, use `--pool=solo` to avoid SIGSEGV crashes with the prefork pool.

---

## Quick Verification Commands

```bash
# Check learning system stats
.venv/bin/python manage.py shell -c "
from core.models_unified_system import CoordinatorOutcome, AgentDream, AgentConversation
print(f'Outcomes: {CoordinatorOutcome.objects.count()}')
print(f'Dreams: {AgentDream.objects.count()}')
print(f'Conversations: {AgentConversation.objects.count()}')
"

# Force run learning tasks
.venv/bin/python -c "
from core.tasks import run_agent_learning_cycle, broadcast_learning_status
run_agent_learning_cycle.delay()
broadcast_learning_status.delay()
print('Tasks queued!')
"

# Check Celery task status
.venv/bin/celery -A core inspect active
```

---

## Key Files Reference

| Purpose | File Path |
|---------|-----------|
| Base Agent with Learning | `core/agents/base_agent.py` |
| Learning Outcome Recording | `core/tasks.py` → `_record_learning_outcome()` |
| Memory Creation | `core/tasks.py` → `_create_execution_memory()` |
| Learning Cycle Task | `core/tasks.py` → `run_agent_learning_cycle()` |
| Dream Generation | `core/tasks.py` → `generate_agent_dreams()` |
| Multi-Agent Conversations | `core/tasks.py` → `run_multi_agent_conversation()` |
| Spider Registry | `ai_core/spiders/spider_registry.py` |
| Celery Beat Schedule | `core/celery.py` |
| Learning Bridges | `core/apps.py` |
| Database Models | `core/models_unified_system.py` |

---

## Session 381 Summary

1. **Verified Celery worker** runs correctly with `--pool=solo` on macOS
2. **Queued 8 learning tasks** and confirmed execution
3. **Observed multi-agent conversation** with 4 agents discussing market data
4. **Confirmed learning system metrics:**
   - 29 agents registered
   - 817 knowledge items
   - 37 learning connections
   - 66 transfers in 24 hours

The collective intelligence system is fully operational and continuously learning from agent executions, spider data, and inter-agent conversations.
