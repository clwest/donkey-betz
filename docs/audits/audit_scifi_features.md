# Agent 2.2: Sci-Fi Features Audit

**Date:** December 21, 2025
**Status:** Complete
**Priority:** P1 - High
**Auditor:** Claude (Session 526)

---

## Executive Summary

The Sci-Fi Features system has **7 active features** with significant data, but there's a critical gap: **moods are not being refreshed** (all 50 have null expiry dates), and **only 2 agents actually use mood/evolution** in their prompts.

### Key Findings

| Feature | Records | Status |
|---------|---------|--------|
| AgentMood | **50** | All have null expiry (not refreshing) |
| AgentEvolution | **49** | Active (Level 1-4) |
| AgentMemory | **292** | Active |
| AgentRelationship | **552** | Active |
| scifi_context usage | **87 files** | Reference exists but consumption limited |

---

## Sci-Fi Features Architecture

### Active Features (7)

From `core/super_platform/scifi_integration.py`:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SCI-FI FEATURES OVERVIEW                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. MOOD SYSTEM                                                  │
│     ├── 50 AgentMood records exist                              │
│     ├── 10 mood types: inspired, focused, curious, confident... │
│     ├── Has intensity, creativity_level, precision_level fields │
│     ├── GAP: mood_expires_at is NULL for all agents             │
│     └── Celery task `check-mood-expirations` runs but no effect │
│                                                                  │
│  2. MEMORY PALACE                                                │
│     ├── 292 AgentMemory records                                 │
│     ├── Types: execution, context, preference                   │
│     └── Used in BaseAgent._build_prompt() for context          │
│                                                                  │
│  3. EVOLUTION SYSTEM                                             │
│     ├── 49 AgentEvolution records                               │
│     ├── Levels 1-4 achieved (ResearchAgent leads at Level 4)   │
│     ├── XP range: 50-960                                        │
│     └── Used in prompt building for authority context           │
│                                                                  │
│  4. SYNERGY/RELATIONSHIPS                                        │
│     ├── 552 AgentRelationship records                           │
│     ├── Relationship types: collaboration, mentorship, rivalry  │
│     └── Strength scores tracked                                 │
│                                                                  │
│  5. TIME TRAVEL (Limited)                                        │
│     └── TimeTravelMixin inherited by all BaseAgent subclasses   │
│                                                                  │
│  6. HIVE MIND                                                    │
│     └── Cross-agent knowledge sharing (see Learning System)     │
│                                                                  │
│  7. SPIDER INTEGRATION                                           │
│     └── Spider data injected into prompts (72 spiders)          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Deprecated Features (4)

From scifi_integration.py comments:
- Agent Dreams → Moved to AgentDream model (separate system)
- Agent Conversations → Moved to AgentConversation model
- Prophecies → Deprecated
- Time Capsules → Deprecated

---

## Detailed Analysis

### 1. Mood System Issues

**Problem:** All 50 agent moods have `mood_expires_at = NULL`

| Agent | Mood | Expiry |
|-------|------|--------|
| MeetingCoordinatorAgent | calm | NULL |
| PromptEngineeringAgent | focused | NULL |
| VideoEditingAgent | calm | NULL |
| TrainedCreationAgent | focused | NULL |
| CodeReviewAgent | focused | NULL |

**Celery Tasks Exist But Ineffective:**

```python
# core/celery.py
'check-mood-expirations': {
    'task': 'core.tasks.check_mood_expirations',
    'schedule': crontab(minute='*/5'),  # Every 5 minutes
}
'apply-mood-rules': {
    'task': 'core.tasks.apply_mood_trigger_rules',
    'schedule': crontab(minute='*/10'),  # Every 10 minutes
}
```

These tasks run, but since no moods have expiry dates set, nothing gets refreshed.

**Root Cause:** When moods are created, `mood_expires_at` is not being set.

### 2. Evolution System (Working)

**Top 10 Evolved Agents:**

| Agent | Level | XP |
|-------|-------|-----|
| ResearchAgent | 4 | 960 |
| ContentWriterAgent | 3 | 555 |
| ImageAgent | 3 | 380 |
| AudioAgent | 2 | 270 |
| AISeriesWorkflowAgent | 2 | 260 |
| PersonalAssistantAgent | 2 | 260 |
| CustomerResearchAgent | 2 | 240 |
| CompetitorAnalysisAgent | 2 | 240 |
| BrandStrategyAgent | 2 | 225 |
| MarketIntelligenceCoordinator | 2 | 165 |

Evolution IS being used in prompts - see `content_writer_agent.py:223-226`.

### 3. Agent Mood/Evolution Consumption

**Files that actually USE mood in prompts:**

| File | Lines | Usage |
|------|-------|-------|
| `content_writer_agent.py` | 210-212 | Reads mood from scifi_context |
| `base_agent.py` | 613, 731 | Uses mood in _build_response methods |

**Files that USE evolution in prompts:**

| File | Lines | Usage |
|------|-------|-------|
| `content_writer_agent.py` | 223-226 | Adds evolution level to prompt |
| `base_agent.py` | 636-638, 755-757 | Uses evolution for authority context |

**Result:** Only 2 files actually consume mood/evolution - same gap as prompting system.

### 4. scifi_context Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    SCIFI_CONTEXT DATA FLOW                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SciFiIntegrationService.get_context(agent_id)                  │
│      │                                                           │
│      ├── Fetches AgentMood → returns mood dict                  │
│      ├── Fetches AgentEvolution → returns evolution dict        │
│      ├── Fetches AgentMemory → returns memories list            │
│      └── Returns combined scifi_context dict                    │
│                                                                  │
│  PersonalAssistantAgent._handle_content_writer_agent()          │
│      │                                                           │
│      └── Calls scifi_service.get_context() ← Fixed Session 523  │
│                                                                  │
│  ContentWriterAgent.execute()                                    │
│      │                                                           │
│      └── Uses scifi_context in _build_intelligent_system_prompt │
│                                                                  │
│  BUT: 41 other agents don't use scifi_context effectively!      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Gap Analysis

### What's Working

1. **Evolution System** - 49 agents have XP/levels, actively accumulating
2. **Relationship Data** - 552 relationships tracked
3. **Memory Storage** - 292 memories persisted
4. **Infrastructure** - Celery tasks scheduled, services defined

### What Needs Improvement

| Issue | Impact | Priority |
|-------|--------|----------|
| All 50 moods have NULL expiry | Moods never refresh | P0 |
| Only 2 agents use mood/evolution | 40 agents ignore context | P0 |
| Mood creation doesn't set expiry | System design gap | P1 |
| scifi_context passed but not used | Wasted data | P1 |

---

## Recommendations

### P0 - Critical

1. **Fix Mood Expiration Setting**
   - When creating/updating AgentMood, set `mood_expires_at` to `now + 4 hours`
   - This allows `check-mood-expirations` to actually refresh moods

2. **Apply Mood/Evolution to All Agents**
   - Modify `BaseAgent._build_prompt()` to always include mood/evolution
   - Same fix as prompting system (Agent 2.1)

### P1 - High Priority

3. **Verify Mood Refresh Task Works**
   ```bash
   .venv/bin/python manage.py shell -c "
   from core.tasks import check_mood_expirations
   check_mood_expirations()
   "
   ```

4. **Set Initial Expiry for Existing Moods**
   ```python
   from django.utils import timezone
   from datetime import timedelta
   AgentMood.objects.update(mood_expires_at=timezone.now() + timedelta(hours=4))
   ```

---

## Integration with Other Systems

| System | Integration Point |
|--------|-------------------|
| Prompting System (2.1) | scifi_context should feed into PLATFORM_CONTEXT |
| Learning System (2.5) | Evolution XP comes from learning outcomes |
| Autonomous Systems (2.6) | Agent dreams/conversations are separate now |

---

## Files Referenced

| File | Purpose |
|------|---------|
| `core/super_platform/scifi_integration.py` | SciFiIntegrationService |
| `core/models_unified_system.py:10161` | AgentMood model |
| `core/models_unified_system.py` | AgentEvolution, AgentMemory models |
| `core/agents/content_writer_agent.py` | Only agent using mood/evolution |
| `core/agents/base_agent.py` | Has mood/evolution methods but not enforced |
| `core/celery.py:443-456` | Mood-related Celery tasks |
| `core/tasks.py` | check_mood_expirations, apply_mood_trigger_rules |

---

*Generated by Agent 2.2: Sci-Fi Features Audit - December 21, 2025*
