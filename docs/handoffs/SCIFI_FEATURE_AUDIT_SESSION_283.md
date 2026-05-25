---
originating_session: 293
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Sci-Fi Feature Audit & Deprecation - Sessions 283-284

**Date:** November 29, 2025
**Purpose:** Comprehensive audit and deprecation of Sci-Fi features for HANDOFF_03
**Status:** PHASE 1 COMPLETE - Deprecations Applied

---

## Executive Summary

After thorough analysis of codebase references, database usage, and integration patterns, here are the key findings:

### Database Usage Summary

| Feature | Model(s) | Records | Status |
|---------|----------|---------|--------|
| **Agent Dreams** | AgentDream, DreamFeedbackPreference, DreamExploration | 534 | ACTIVE |
| **Agent Conversations** | AgentConversation, ConversationMessage | 2,919 | HEAVILY USED |
| **Hive Mind** | HiveMindSession, HiveMindContribution | 15 | LIGHT USE |
| **Memory Palace** | AgentMemory, MemoryPalaceRoom | 17 | LIGHT USE |
| **Memory Clusters** | MemoryCluster, MemoryClusterMembership, ClusterEvolution | 0 | EMPTY |
| **Mood System** | AgentMood, MoodHistory, MoodTriggerRule | 22 | LIGHT USE |
| **Rivalries/Alliances** | AgentRelationship, Alliance, Rivalry | 380 | ACTIVE |
| **Evolution System** | AgentEvolution, AgentAbility, XPHistory, LevelMilestone | 22 | LIGHT USE |
| **Time Travel Debug** | AgentSession, DecisionPoint, ThoughtBubble, etc. | 52 | LIGHT USE |
| **Personality** | AgentPersonality | 20 | ACTIVE |
| **Predictions/Prophecies** | AgentPrediction, PredictionStats, etc. | 0 | EMPTY |
| **Time Capsules** | TimeCapsule, TimeCapsuleReaction | 7 | MINIMAL |

**TOTAL: 3,988 records across all sci-fi models**

---

## Codebase Reference Analysis

| Feature | References | Key Files | Status |
|---------|------------|-----------|--------|
| **Agent Dreams** | 315 | `views_agent_learning.py`, `views_predictions.py`, `tasks.py` | Widely integrated |
| **Prophecies** | 1 | `intelligence/connect_all_agents.py` | Nearly unused |
| **Time Capsules** | 16 | `views_time_capsules.py`, `models_unified_system.py` | Minimal |
| **Memory Clusters** | 42 | `views_memory_clusters.py`, `context_aggregator.py` | Integrated but empty |
| **Rivalries** | 141 | `views_agent_relationships.py`, `scifi_integration.py`, `tasks.py` | Active |
| **Agent Conversations** | 53 | `agent_conversation_consumer.py`, `routing.py`, `consumers.py` | WebSocket-based, active |
| **Hive Mind** | 66 | `views_hive_mind.py`, `hive_mind_consumer.py`, `coordinator.py` | Core feature |
| **Memory Palace** | 28 | `views_memory_palace.py`, `context_aggregator.py` | Integrated |
| **Mood System** | 327 | `views_agent_mood.py`, `scifi_integration.py` | Heavily integrated |
| **Evolution** | 65 | `views_agent_evolution.py`, `scifi_integration.py` | Integrated |
| **Time Travel** | 41 | `views_time_travel.py`, `base_agent.py`, `time_travel_mixin.py` | Core infrastructure |
| **SuperPlatform** | 38 | `coordinator.py`, `views_super_platform.py` | Core brain |
| **Spider Integration** | 77 | `spider_intelligence.py`, `spider_intelligence_bridge.py` | Core data source |
| **Personality Profiles** | 0 | (Merged with AgentMood/Evolution) | Part of other systems |
| **Agent Learning** | 76 | `agent_learning_service.py`, `views_agent_learning.py` | Active |

---

## Dependency Map

```
SuperPlatformCoordinator (THE BRAIN)
├── QueryClassifier
├── ContextAggregator
│   ├── SpiderIntelligenceService (real data)
│   ├── Memory Palace (AgentMemory, MemoryPalaceRoom)
│   ├── Memory Clusters (EMPTY - candidate for removal)
│   └── Mood System (AgentMood)
├── PromptBuilder
├── SciFiIntegrationService
│   ├── Mood System → MoodInfluence
│   ├── Evolution System → EvolutionInfluence
│   ├── Relationships → RelationshipInfluence (includes Rivalries)
│   ├── Memory → MemoryInfluence
│   └── Dreams → Recent creative thoughts
└── AgentRouter (Clean Architecture)
    └── All 22 Clean Agents use TimeTravelMixin

Time Travel Debugging
├── TimeTravelMixin (base_agent.py)
├── DecisionPoint model
├── ThoughtBubble model
├── AgentSession model
└── Independent of other sci-fi features

Hive Mind Mode
├── HiveMindSession model
├── HiveMindContribution model
├── WebSocket consumer (hive_mind_consumer.py)
└── Uses SciFiIntegrationService for agent context

Agent Conversations
├── AgentConversation model
├── ConversationMessage model
├── ConversationArtifact model (EMPTY)
├── WebSocket consumer (agent_conversation_consumer.py)
└── Could be merged into Hive Mind

Rivalries/Alliances
├── AgentRelationship model (380 records)
├── Alliance model (EMPTY)
├── Rivalry model (EMPTY)
├── Used by SciFiIntegrationService.get_collaboration_bonus()
└── Could be simplified to static synergy map

Agent Dreams
├── AgentDream model (510 records)
├── DreamFeedbackPreference (20 records)
├── DreamExploration (4 records)
├── Used by SciFiIntegrationService._get_recent_dreams()
└── Questionable value - adds creative suggestions to prompts

Predictions/Prophecies
├── AgentPrediction model (EMPTY)
├── PredictionStats model (EMPTY)
├── views_predictions.py exists but model is empty
└── CANDIDATE FOR DEPRECATION

Time Capsules
├── TimeCapsule model (7 records)
├── TimeCapsuleReaction model (EMPTY)
└── CANDIDATE FOR DEPRECATION
```

---

## Feature Status Decisions

### TIER 1: KEEP & STRENGTHEN (Core Infrastructure)

| Feature | Records | Reason | Action |
|---------|---------|--------|--------|
| SuperPlatformCoordinator | N/A | Central brain | KEEP |
| Time Travel Debugging | 52 | Essential for debugging | KEEP |
| Spider Integration | N/A | Real data source | KEEP |
| Memory Palace | 17 | Context persistence | KEEP |
| Hive Mind Mode | 15 | Multi-agent collaboration | KEEP |

### TIER 2: KEEP & SIMPLIFY (Useful but complex)

| Feature | Records | Reason | Action |
|---------|---------|--------|--------|
| Mood System | 22 | Affects agent behavior | SIMPLIFY to 3 states |
| Evolution System | 22 | Progress tracking | SIMPLIFY to stats |
| Agent Relationships | 380 | Collaboration bonuses | SIMPLIFY to synergy map |

### TIER 3: MERGE (Overlap with other features)

| Feature | Records | Merge Into | Action |
|---------|---------|------------|--------|
| Memory Clusters | 0 | Memory Palace (add tags field) | MERGE |
| Agent Conversations | 2,919 | Hive Mind (conversation mode) | MERGE |
| Agent Learning | 76 refs | Evolution System (success tracking) | MERGE |

### TIER 4: DEPRECATE (Low or no value)

| Feature | Records | Reason | Action |
|---------|---------|--------|--------|
| Agent Dreams | 534 | Unclear user value | DEPRECATE |
| Predictions/Prophecies | 0 | Empty, novelty feature | DEPRECATE |
| Time Capsules | 7 | Minimal use, novelty | DEPRECATE |

---

## Views & API Endpoints

| Feature | View File | Lines | Status |
|---------|-----------|-------|--------|
| Mood System | `views_agent_mood.py` | 209+ | Active |
| Evolution | `views_agent_evolution.py` | exists | Active |
| Memory Palace | `views_memory_palace.py` | exists | Active |
| Memory Clusters | `views_memory_clusters.py` | 18 refs | Could remove |
| Hive Mind | `views_hive_mind.py` | 13 refs | Active |
| Time Travel | `views_time_travel.py` | exists | Active |
| Predictions | `views_predictions.py` | 30+ refs | Empty model |
| Time Capsules | `views_time_capsules.py` | exists | Minimal use |
| Relationships | `views_agent_relationships.py` | 85 refs | Active |
| Super Platform | `views_super_platform.py` | 12 refs | Active |

---

## Integration Points to Preserve

1. **SciFiIntegrationService** (`scifi_integration.py`)
   - `get_scifi_context()` - Used by SuperPlatformCoordinator
   - `get_collaboration_bonus()` - Used for team synergy
   - `get_prompt_injection()` - Enhances agent prompts

2. **ContextAggregator** (`context_aggregator.py`)
   - `_get_memory_context()` - Uses AgentMemory, MemoryCluster
   - `_get_mood_context()` - Uses AgentMood, MoodHistory
   - `_get_agent_relationships()` - Uses AgentRelationship

3. **TimeTravelMixin** (`agents/time_travel_mixin.py`)
   - Used by all 22 clean agents in `core/agents/`
   - Records DecisionPoint, ThoughtBubble

4. **WebSocket Consumers**
   - `hive_mind_consumer.py` - Hive Mind sessions
   - `agent_conversation_consumer.py` - Could merge into Hive Mind

---

## Session 284 Implementation - PHASE 1 COMPLETE

### Phase 1: Deprecate Low-Value Features - DONE

1. **Agent Dreams** - DEPRECATED
   - Added deprecation warning to `AgentDream.save()` with DeprecationWarning
   - Updated `SciFiIntegrationService._get_recent_dreams()` to return empty list
   - Kept model for data preservation (534 records)
   - Updated docstring with deprecation notice

2. **Predictions/Prophecies** - DEPRECATED
   - Added deprecation warning to `AgentPrediction.save()` with DeprecationWarning
   - Updated docstring with deprecation notice
   - Model preserved but will reject new records

3. **Time Capsules** - DEPRECATED
   - Added deprecation warning to `TimeCapsule.save()` with DeprecationWarning
   - Updated docstring with deprecation notice
   - 7 existing records preserved

4. **Empty Models Also Deprecated:**
   - `MemoryCluster` - Added deprecation warning, zero records
   - `Alliance` - Added deprecation warning, zero records
   - `Rivalry` - Added deprecation warning, zero records

### Verified Working:
- SciFiIntegrationService still functions correctly
- SuperPlatformCoordinator still works
- Dreams now return empty (as intended)
- Mood, Evolution, Relationships still work

### Phase 2: Merge Features - DONE

1. **Memory Clusters → Memory Palace** - DONE
   - Added `tags = JSONField(default=list)` to `AgentMemory`
   - Added helper methods: `add_tag()`, `remove_tag()`, `has_tag()`, `get_by_tag()`, `get_all_tags()`
   - Updated `ContextAggregator` to use tags instead of MemoryCluster
   - Created migration `0054_add_tags_to_agentmemory`
   - MemoryCluster already deprecated in Phase 1

2. **Agent Conversations → Hive Mind** - DONE
   - Added `session_mode` field to `HiveMindSession`: 'hive_mind' or 'conversation'
   - Added `conversation_topic` field for conversation mode
   - Added 'active' status for ongoing conversations
   - Deprecated `AgentConversation` with save() warning
   - Created migration `0055_add_session_mode_to_hivemindsession`
   - Existing 2,919 AgentConversation records preserved

### Phase 3: Simplify Features

1. **Mood System → 3 States**
   ```python
   class SimpleMood:
       FOCUSED = 'focused'    # Default
       CREATIVE = 'creative'  # More experimental
       CAUTIOUS = 'cautious'  # More conservative
   ```

2. **Evolution → Stats Only**
   ```python
   class AgentStats:
       total_executions: int
       successful_executions: int
       average_execution_time_ms: float
       last_execution: datetime

       @property
       def level(self) -> int:
           # Simple: 1-99 → L1, 100-499 → L2, 500+ → L3
   ```

3. **Relationships → Synergy Map**
   ```python
   AGENT_SYNERGY = {
       ('ImageAgent', 'ContentStrategyAgent'): 1.2,
       ('ResearchAgent', 'TrendAnalysisAgent'): 1.3,
   }
   ```

---

## Success Metrics

| Metric | Before | Target |
|--------|--------|--------|
| Active sci-fi features | 15 | 7 core |
| Model classes for sci-fi | 37 | ~20 (rest deprecated) |
| SciFiIntegrationService complexity | High | Medium |
| Empty database models | 7 | 0 (deprecate all) |

---

## Risks

1. **Data Loss**: Mitigated by keeping models, just deprecating
2. **Feature Regression**: Verify SuperPlatformCoordinator after changes
3. **WebSocket Breakage**: Test Hive Mind consumer carefully
4. **Agent Behavior Change**: Mood simplification may affect responses

---

## Next Steps

Session 283 complete. Session 284 should:

1. Start with Phase 1 (deprecate Agent Dreams, Predictions, Time Capsules)
2. Continue with Phase 2 (merge Memory Clusters, Agent Conversations)
3. Finish with Phase 3 (simplify Mood, Evolution, Relationships)
4. Update SciFiIntegrationService
5. Run validation tests
