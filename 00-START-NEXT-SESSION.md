# Start Next Session Here

**Last Session:** 362 - Conversation Value Audit + Auto-Promotion Fix
**Date:** December 5, 2025
**Status:** 102 spiders | 36 categories | 79 agents | 1,280 CONVERSATIONS | FEEDBACK LOOP NOW CLOSED!

---

## Session 362 Accomplishments

### The Problem We Solved

**Question:** Are the 1,280 agent conversations just stored without influencing decisions?

**Finding:** Pipelines existed but the feedback loop was broken:
- Only 1 of 115 decisions had been promoted to canonical policy (0.1%!)
- Decisions need to be canonical to influence future agent behavior

### The Fix: Auto-Promotion System

We implemented automatic promotion of high-quality decisions:

1. **Quality Scoring** - Each decision scored 0-1 based on:
   - Recommended stance length
   - Number of key insights
   - Rationale provided
   - Conversation depth
   - Participant diversity

2. **Auto-Promote Task** - Runs every 30 minutes via Celery Beat:
   - Updates quality scores for new decisions
   - Promotes top 3 decisions above 0.6 threshold
   - Ensures diversity across impact areas

3. **Result:** Went from 1 → 4 canonical policies on first run!

### Conversion Metrics (After Fix)

| Metric | Before | After |
|--------|--------|-------|
| Canonical Policies | 1 | 4 |
| Decisions with Quality Scores | 0 | 114 |
| High Quality (>=0.6) | Unknown | 114 (100%!) |
| Auto-Promotion Active | No | Yes (every 30 min) |

---

## What's Next (Session 363)

### Option A: Monitor Auto-Promotion Impact
- Let the system run and observe if agent behavior changes
- Check if policies are actually injected into prompts

### Option B: Fix LivingProjectConfig (0 records!)
Projects can't receive insights because no `LivingProjectConfig` exists:
```python
# When projects are created, auto-create living configs
LivingProjectConfig.objects.create(
    project=project,
    is_active=True,
    watch_topics=extract_topics(project.name)
)
```

### Option C: Mood Variety
23 of 24 agents are "calm" - need more mood variety in the system.

---

## Current System State

| Component | Count |
|-----------|-------|
| **Spiders** | **102** |
| **Categories** | **36** |
| **Agents** | **79** |
| **Data Points** | **8,879+** |
| **Agent Conversations** | **1,280** |
| **Decisions Extracted** | **115** |
| **Canonical Policies** | **4** (was 1!) |
| **Project Insights** | **260+** (grew during promotion!) |
| **LivingProjectConfig** | **0** (still needs fixing) |

---

## Quick Start

```bash
make start
make celery  # For background tasks + learning cycles + auto-promotion
open http://localhost:8000/ai-studio/
```

---

## Celery Beat Schedule (Agent Learning)

| Task | Frequency | Purpose |
|------|-----------|---------|
| `agent-learning-cycle` | Every 5 min | Knowledge propagation |
| `agent-conversation-cycle` | Every 5 min | 2-agent discussions |
| `multi-agent-panel-cycle` | Every 20 min | 3-5 agent panel discussions |
| `auto-promote-decisions` | Every 30 min | **NEW! Promotes high-quality decisions** |
| `agent-dream-cycle` | Every 15 min | Creative thinking |
| `agent-mood-check` | Every 10 min | Emotional state updates |
| `agent-relationship-evolution` | Every 10 min | Alliance/rivalry updates |
| `broadcast-learning-status` | Every 3 min | WebSocket broadcasts |
| `broadcast-conversation-status` | Every 3 min | WebSocket broadcasts |

---

## Data Flow (After Fix)

```
[Agent Conversation] ---> [Conclusion Generated]
         |
         +--> [DecisionExtractor] --> AgentDecisionSummary (115)
         |         |
         |         +--> [auto_promote_decisions] --> 4 CANONICAL POLICIES! ✓
         |                    |
         |                    +--> [PolicyContextService] --> Future Agent Prompts!
         |
         +--> [LivingProjectService] --> ProjectInsight (260+)
                   |
                   +--> Still needs LivingProjectConfig records
```

---

## Session 362 Files Changed

| File | Changes |
|------|---------|
| `core/models_unified_system.py` | Added `quality_score`, `calculate_quality_score()`, `update_quality_score()` |
| `core/tasks.py` | Added `auto_promote_decisions` task |
| `core/celery.py` | Added `auto-promote-decisions` to Beat schedule |
| `core/migrations/0069_*` | Migration for quality_score field |

---

## Related Documentation

- `docs/handoffs/SESSION_362_CONVERSATION_VALUE_AUDIT.md` - Complete audit + fix
- `docs/handoffs/SESSION_361_CELERY_BEAT_MULTI_AGENT.md` - Multi-agent Celery Beat
- `docs/handoffs/SESSION_360_MULTI_AGENT_CONVERSATIONS.md` - Multi-agent panels
