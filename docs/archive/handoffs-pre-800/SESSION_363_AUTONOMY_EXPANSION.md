# Session 363: Autonomy Expansion - Three New Reactive Pipelines

**Date:** December 5, 2025
**Focus:** Expand autonomous behaviors with reactive data-driven pipelines
**Status:** COMPLETE - All 3 autonomy features implemented and tested

---

## Summary

Session 363 builds on Session 362's autonomy pipeline fix by adding **three new reactive pipelines** that create truly autonomous, self-improving system behavior:

| Pipeline | Trigger | Action | Schedule |
|----------|---------|--------|----------|
| **Spider-Triggered Conversations** | New high-relevance spider data | Creates agent discussions about the data | Every 15 min |
| **Project-Triggered Research** | Project with research needs | Prioritizes relevant spiders | Every 20 min |
| **Decision-Triggered Propagation** | New canonical policy | Creates implementation conversations | Every 10 min |

---

## Complete Autonomous Flow (Now Fully Connected!)

```
[Spider Network] ─── 30 min ───────────────────────────────────────────────────┐
       │                                                                        │
       v                                                                        │
[SpiderData] ───────────────────────┐                                           │
       │                            │                                           │
       │ (15 min)                   │                                           │
       v                            │                                           │
[trigger_spider_conversations]      │                                           │
       │                            │                                           │
       v                            v                                           │
[Agent Conversations] ──> [Conclusions] ──> [DecisionExtractor]                 │
       │ (5 min)                                   │                            │
       │                                           v                            │
       │                           [AgentDecisionSummary]                       │
       │                                           │ (30 min)                   │
       │                                           v                            │
       │                           [auto_promote_decisions]                     │
       │                                           │                            │
       │                                           v                            │
       │                           [Canonical Policies]                         │
       │                                           │ (10 min)                   │
       │                                           v                            │
       │                           [propagate_new_policies]                     │
       │                                           │                            │
       │                                           v                            │
       │                           [Implementation Conversations] ──────────────┤
       │                                                                        │
       v                                                                        │
[LivingProjectService]                                                          │
       │                                                                        │
       v                                                                        │
[LivingProjectConfig] ←─────────────────────────────────────────────────────────┤
       │                                                                        │
       │ (20 min)                                                               │
       v                                                                        │
[trigger_project_research]                                                      │
       │                                                                        │
       v                                                                        │
[SpiderPriority boost] ─────────────────────────────────────────────────────────┘

                        FULLY CONNECTED AUTONOMOUS LOOP
```

---

## Implementation Details

### 1. Spider-Triggered Conversations (`trigger_spider_conversations`)

**Location:** `core/tasks.py:4654-4838`

**What it does:**
- Finds spider data from last 2 hours with `relevance_score >= 70`
- Maps data types to relevant agent specializations
- Creates `critical_review` conversations about new intelligence
- Deduplicates to avoid discussing the same data twice

**Data type to agent mapping:**
```python
data_type_to_agents = {
    'tech': ['ResearchAgent', 'CTOAgent', 'InnovationScoutAgent'],
    'financial': ['ResearchAgent', 'COOAgent', 'OpportunityScannerAgent'],
    'jobs': ['ResearchAgent', 'ContentStrategyAgent'],
    'creative': ['DesignAssistantAgent', 'BrandIdentityAgent', 'ContentStrategyAgent'],
    'market': ['ResearchAgent', 'TrendAnalysisAgent', 'OpportunityScannerAgent'],
    'news': ['ResearchAgent', 'CTOAgent', 'InnovationScoutAgent'],
}
```

**New trigger type:** Added `'spider_data'` to AgentConversation.trigger_type choices

---

### 2. Project-Triggered Research (`trigger_project_research`)

**Location:** `core/tasks.py:4845-5020`

**What it does:**
- Finds active LivingProjectConfig records
- Checks if projects need fresh data (< 3 insights in last 4 hours)
- Maps watch_topics to relevant spider categories
- Boosts spider priorities via `SpiderPriority` model
- Creates `brainstorm` conversations about research needs (30% chance)

**Topic to spider mapping:**
```python
topic_to_spiders = {
    'ai': ['techcrunch', 'theverge', 'hackernews', 'huggingface', 'devto'],
    'ml': ['techcrunch', 'huggingface', 'hackernews', 'kaggle'],
    'tech': ['techcrunch', 'theverge', 'wired', 'mit_tech_review', 'hackernews'],
    'finance': ['yahoo_finance', 'coingecko', 'seekingalpha', 'business_news'],
    # ... and 10 more categories
}
```

**New trigger type:** Added `'project_need'` to AgentConversation.trigger_type choices

---

### 3. Decision-Triggered Propagation (`propagate_new_policies`)

**Location:** `core/tasks.py:5027-5200`

**What it does:**
- Finds canonical policies from last 2 hours not yet propagated
- Maps policy `impact_area` to affected agents via `PolicyContextService.AGENT_IMPACT_AREAS`
- Creates `implementation_planning` conversations
- Marks policies as propagated to avoid re-processing

**New field:** Added `propagated_at` to `AgentDecisionSummary` model

---

## Celery Beat Schedule (Now 16 Autonomous Tasks)

| Task | Frequency | Purpose |
|------|-----------|---------|
| `run-spider-network` | 30 min | Collect external data |
| `run-agent-learning-cycle` | 10 min | Knowledge propagation |
| `agent-conversation-cycle` | 5 min | 2-agent discussions |
| `multi-agent-panel-cycle` | 20 min | 3-5 agent panel discussions |
| `auto-promote-decisions` | 30 min | Promote to canonical policies |
| **`trigger-spider-conversations`** | **15 min** | **NEW: Data → Discussion** |
| **`trigger-project-research`** | **20 min** | **NEW: Project → Spider** |
| **`propagate-new-policies`** | **10 min** | **NEW: Policy → Agents** |
| `agent-dream-cycle` | 15 min | Creative thinking |
| `broadcast-learning-status` | 1 min | WebSocket updates |
| `broadcast-conversation-status` | 2 min | WebSocket updates |
| `broadcast-dream-journal` | 3 min | WebSocket updates |
| `sync-workflow-schedules` | 5 min | Workflow sync |
| `check-workflow-schedules` | 1 min | Execute due workflows |
| `poll-pending-trainings` | 30s | Character training |
| `cleanup-stale-trainings` | 60 min | Cleanup |

---

## Files Modified

| File | Changes |
|------|---------|
| `core/tasks.py` | Added 3 new tasks (~370 lines total) |
| `core/settings.py` | Added 3 tasks to CELERY_BEAT_SCHEDULE |
| `core/models_unified_system.py` | Added `propagated_at` field, new trigger_type choices |
| `core/migrations/0070_*` | Migration for propagated_at + trigger_type |

---

## Commits

1. `f3d2d57` - feat(Session 363): Add spider-triggered autonomous conversations
2. `8557ad6` - feat(Session 363): Add project-triggered research autonomy
3. `5f1b7b4` - feat(Session 363): Add decision-triggered policy propagation

---

## Testing Results

### Spider-Triggered Conversations
```
Result: {'status': 'success', 'message': 'No new data', 'stats':
  {'spider_data_checked': 0, 'conversations_triggered': 0}}
```
(No high-relevance data in last 2 hours - working as expected)

### Project-Triggered Research
```
Result: {'status': 'success', 'stats':
  {'projects_checked': 6, 'research_triggered': 0, 'spiders_prioritized': []}}
```
(All projects have sufficient recent insights - working as expected)

### Decision-Triggered Propagation
```
Result: {'status': 'success', 'stats':
  {'policies_checked': 2, 'actions_triggered': 1,
   'agents_notified': ['ContentStrategyAgent', 'ImageAgent'],
   'conversations_created': 1}}
```
(Found unpropagated policies, created implementation conversation - working!)

---

## What's Next (Session 364+)

### Option A: More Diversity
- Mood variety (23/24 agents are "calm")
- Relationship evolution (more rivalries/alliances)
- Specialized conversation topics

### Option B: Pipeline Monitoring
- Dashboard for autonomous activity
- Real-time view of which tasks are firing
- Success/failure metrics

### Option C: Cross-Agent Learning
- Agents share knowledge from conversations
- Transfer learning between specialists
- Collective memory improvements

---

## Quick Start

```bash
make start
make celery  # For full autonomous operation
open http://localhost:8000/ai-studio/
```

The system now runs autonomously with 16 scheduled tasks creating a fully connected learning loop!
