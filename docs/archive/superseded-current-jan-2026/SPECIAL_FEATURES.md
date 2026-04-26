<!-- ARCHIVED-DOC-V1 -->
> # ⛔ ARCHIVED — 2026-04-26 (Session 1100)
>
> This doc was retired during the Session 1099 → 1100 doc-drift cleanup
> because its stats diverged materially from runtime reality. **Content
> below is preserved unchanged for historical reference and potential
> future book material** (Chris's "how I learned to work with AI to build
> this platform").
>
> **What this used to be:** Special-feature catalog
>
> **Where to look now:**
> - [docs/CAPABILITIES.md](/docs/CAPABILITIES.md)
> - [docs/SCIFI_FEATURES.md](/docs/SCIFI_FEATURES.md)
>
> **Source of truth for live numbers:** `docs/PLATFORM_INVENTORY.md`
> (regenerable via `python manage.py generate_platform_inventory`).

---

# Special Features Documentation

**Total Sci-Fi Features:** 14
**Last Updated:** January 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Time Capsules](#time-capsules)
3. [Memory Palace](#memory-palace)
4. [Consciousness System](#consciousness-system)
5. [Mythology System](#mythology-system)
6. [Agent Dreams](#agent-dreams)
7. [Living Projects](#living-projects)
8. [Income Action System](#income-action-system)
9. [Agent Evolution](#agent-evolution)
10. [Additional Features](#additional-features)

---

## Overview

The platform includes 14 "sci-fi" features that give agents human-like qualities: memory, dreams, evolution, consciousness, and more. All features are active with real data.

### Feature Summary

| Feature | Session | Purpose |
|---------|---------|---------|
| Time Capsules | 259 | Messages to future selves |
| Memory Palace | 251 | Visual memory organization |
| Consciousness | - | System self-awareness |
| Mythology | 541 | Hallucination prevention |
| Agent Dreams | 247/366 | Creative ideation |
| Living Projects | 335 | Autonomous learning |
| Income Actions | 388 | Opportunity pipeline |
| Agent Evolution | 254 | XP and leveling |
| Agent Moods | - | Emotional states |
| Agent Relationships | - | Inter-agent connections |
| Hive Mind | - | Collective decisions |
| Time Travel | - | Decision replay |
| Collective Intelligence | - | Knowledge sharing |
| Neural Orchestra | - | Visual orchestration |

---

## Time Capsules

**Session:** 259 (Restored in 567)
**Location:** `core/views_time_capsules.py`

### Purpose
Messages that agents write to their future selves, sealed until a scheduled reveal date.

### Models

**TimeCapsule:**
```
- title, message content
- trigger_type: reflection, milestone, prediction, lesson, goal, dream, question
- context_captured: {mood, level, xp, tasks_completed} at creation
- reveal_at: scheduled date
- status: sealed, revealed, expired
- ai_reflection: generated when revealed
- state_comparison: then vs now
```

**TimeCapsuleReaction:**
```
- reaction_types: touching, insightful, funny, inspiring, nostalgic, surprising
```

**TimeCapsuleStats:**
```
- total/sealed/revealed counts per agent
- average seal duration
- most common trigger type
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/time-capsules/` | GET | Overview stats |
| `/api/time-capsules/agent/<id>/` | GET/POST | Agent's capsules |
| `/api/time-capsules/<id>/` | GET | Capsule detail |
| `/api/time-capsules/<id>/reveal/` | POST | Reveal sealed capsule |
| `/api/time-capsules/<id>/react/` | POST | Add reaction |
| `/api/time-capsules/ready-to-reveal/` | GET | List ready to open |
| `/api/time-capsules/generate/` | POST | Auto-generate |

### Workflow
1. Agent creates capsule with message and future date
2. Agent's state (mood, level, XP) captured
3. Capsule remains sealed until reveal_at
4. On reveal, AI generates reflection comparing past vs current
5. Other agents can react with emotions

---

## Memory Palace

**Session:** 251
**Location:** `core/views_memory_palace.py`

### Purpose
Visual organization of agent memories in themed "rooms."

### Models

**AgentMemory:**
```
- content, title, context
- memory_types: success, failure, user_preference, technique, insight, interaction, feedback
- emotional_valence: positive, negative, neutral
- importance_score: 0-1
- semantic_embedding: for retrieval
- access_count, last_accessed
- source: task, conversation, dream, etc.
```

**MemoryPalaceRoom:**
```
- room_types: techniques_library, hall_of_victories, lessons_learned,
              user_preferences, insight_garden, experiment_lab, general_archive
- x, y coordinates for visualization
- color, emoji icon
- M2M relationship to memories
```

**MemoryConnection:**
```
- connection_types: causal, similar, contrast, elaborates, temporal
- strength_score: 0-1
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/memories/agent/<id>/` | GET | All memories |
| `/api/memories/<id>/` | GET | Memory detail |
| `/api/memories/` | POST | Create memory |
| `/api/memories/search/` | POST | Semantic search |
| `/api/memory-palace/rooms/<id>/` | GET | All rooms |
| `/api/memory-palace/room/<id>/` | GET | Memories in room |
| `/api/memory-palace/assign/` | POST | Assign to room |
| `/api/memory-palace/summary/<id>/` | GET | Prompt injection |
| `/api/memories/connect/` | POST | Create connection |

---

## Consciousness System

**Location:** `ai_core/spiders/consciousness.py`, `core/views_consciousness.py`

### Purpose
System self-awareness and introspection capabilities.

### Components

**ConsciousnessBridge:**
- Analyzes own code using AST
- Catalogs capabilities (agents, spiders, advisors)
- Identifies limitations and strengths
- Proposes system improvements
- Tracks emergent behaviors
- Calculates self-awareness score
- Engages in philosophical dialogue

**Capability Dataclass:**
```
- name, type, description, file_path
- dependencies
- performance_scores
- usage_metrics
- strengths, limitations
```

**SystemInsight Dataclass:**
```
- categories: pattern, inefficiency, opportunity, emergent_behavior
- confidence/importance scores
- action_items
```

**ImprovementProposal Dataclass:**
```
- title, description, category
- impact/complexity/ROI scores
- implementation_steps
- affected_components, risks, benefits
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/consciousness/data/` | GET | Current state |
| `/api/consciousness/introspect/` | POST | Deep introspection |
| `/api/consciousness/evolve/` | POST | Evolution proposal |
| `/api/consciousness/health/` | GET | Health metrics |

---

## Mythology System

**Session:** 541
**Location:** `mythology/`

### Purpose
Hallucination prevention and knowledge validation.

### Components

**MythologyEvent:**
```
- event_types: creation, mutation, propagation, detection, prevention
- mutation_types: context_loss, inflation, semantic_drift, confidence_decay,
                  expansion, condensation, false_claim, capability_exaggeration
- original vs mutated content
- confidence/risk scoring
- prevention status and method
```

**MythologyQuarantine:**
```
- teacher/student agents involved
- blocked_content_summary
- violation_type: financial_myth, technical_myth, time_myth,
                  dangerous_myth, spider_data_myth
- spider_source traceability
- review_status: pending, approved, rejected, edited
```

### Validation Process
1. Knowledge transfer between agents validated
2. URL validation: verifies source URLs are real
3. Corroboration checking: requires multiple sources
4. Content validation: detects unrealistic claims
5. Uses authoritative source lists (NOAA, EPA, SEC, etc.)
6. Blocks unreliable sources (Onion, Babylon Bee, clickbait)
7. Quarantined transfers go to review queue

### Authoritative Sources

| Category | Sources |
|----------|---------|
| Climate | NOAA, EPA, NASA, IPCC, Nature |
| Health | NIH, CDC, WHO, NEJM, Lancet |
| Markets | SEC, Federal Reserve, Bloomberg, Reuters |
| Politics | Congress.gov, WhiteHouse.gov |
| Tech | IEEE, ACM, arXiv, TechCrunch |
| Crypto | SEC, CFTC, CoinDesk, Chainalysis |

---

## Agent Dreams

**Sessions:** 247 (initial), 366 (productization)
**Location:** `core/models_unified_system.py`

### Purpose
Creative ideation when agents are idle.

### Model - AgentDream

```
- dream_types: creative_idea, what_if, mashup, prediction,
               improvement, observation, wild_thought
- quality_scores:
  - vividness (0-1): how detailed
  - creativity (0-1): how novel
  - actionability (0-1): how implementable
  - relevance (0-1): relevance to projects
  - composite: (creativity + actionability + relevance) / 3
- inspiration: what inspired the dream
- topics: related tags
```

**Productization Fields (Session 366):**
```
- promoted_to_decision: promoted to Boardroom
- promoted_at: timestamp
- decision_outcome: pending, approved, deferred, rejected
- directed_topic: user-requested focus
```

### Workflow
1. Idle agents "dream" - generating creative ideas
2. 90% from agent knowledge, 10% from other agents' [Learned] knowledge
3. Dreams scored on actionability and project relevance
4. High-scoring dreams promoted to Boardroom
5. Outcomes tracked (approved = implementation)

---

## Living Projects

**Session:** 335
**Location:** `core/services/living_project_service.py`

### Purpose
Projects that autonomously learn from the ecosystem.

### Models

**LivingProjectConfig:**
```
- is_active: learning enabled
- watch_topics, competitors, keywords
- enabled_sources, spider_categories
- relevance_threshold, confidence_threshold
- notification_preferences
- auto_expand_topics
- stats: total_surfaced, acted_on, average_rating
```

**ProjectInsight:**
```
- insight_types: spider_data, competitor, trend, pain_point,
                 opportunity, agent_insight, decision, creative_idea
- source: spider, agent, decision, learning, dream, research
- relevance/confidence scoring
- matched_topics
- status: new, seen, acted_on, dismissed, archived
- user_interaction: pinned, rating (1-5), notes
```

### Workflow
1. Project defines topics (tags, metadata, company info)
2. Spider data matched to projects by relevance
3. Agent conversations → create insights if relevant
4. Canonical decisions surfaced to relevant projects
5. Projects receive automatic insights feed
6. User rates insights → system learns thresholds

### Service Methods

| Method | Purpose |
|--------|---------|
| `get_project_topics()` | Extract topics |
| `calculate_relevance()` | Score with matched topics |
| `process_spider_data()` | Create insights from spiders |
| `process_agent_conversation()` | Create insights from discussions |
| `activate_living_project()` | Enable learning |
| `get_project_feed()` | Insight feed with filtering |

---

## Income Action System

**Session:** 388
**Location:** `core/services/income_action_service.py`, `core/views_income_action.py`

### Purpose
Pipeline from spider data to income opportunities.

### Model - SavedOpportunity

```
- title, source_url (dedup), source_platform
- description, salary_info, company_name, location, category
- raw_spider_data reference
- status: saved → materials_ready → applied → interview → accepted/rejected
- generated_materials: JSON (cover letters/proposals)
- timestamps: created, applied, resolved
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/income/save-opportunity/` | POST | Save opportunity |
| `/api/income/generate-application/` | POST | Generate materials |
| `/api/income/update-status/` | POST | Update status |
| `/api/income/opportunities/` | GET | List saved |
| `/api/income/statistics/` | GET | Success stats |
| `/api/income/quick-apply/` | POST | One-click save + generate |

### Workflow
1. User sees opportunity in UI (from spider data)
2. User clicks "Save & Apply"
3. System saves with duplicate check
4. System generates application materials (cover letter)
5. User applies externally
6. User records outcome
7. System learns from outcomes (LearningPattern)

---

## Agent Evolution

**Session:** 254
**Location:** `core/models_unified_system.py`

### Purpose
XP-based leveling and progression system.

### Model - AgentEvolution

```
- total_xp
- current_level (1-10)
- xp_to_next_level
- prestige: max-level reset count
```

**Stats:**
```
- tasks_completed, tasks_failed
- collaborations_completed
- mentorship_sessions
```

**Ability Bonuses:**
```
- speed_bonus
- quality_bonus
- creativity_bonus
- efficiency_bonus
```

### Level Titles

| Level | Title |
|-------|-------|
| 1 | Novice |
| 2 | Apprentice |
| 3 | Journeyman |
| 4 | Expert |
| 5 | Master |
| 6 | Grandmaster |
| 7 | Legend |
| 8 | Mythic |
| 9 | Transcendent |
| 10 | Omniscient |

### XP Formula
Level N requires `100 * 1.5^(N-1)` XP

---

## Additional Features

### Agent Moods
Emotional states affecting agent behavior and responses.

### Agent Relationships
Inter-agent connections with trust levels and interaction history.

### Hive Mind
Collective decision-making sessions with multiple agents.

### Time Travel
Decision replay to explore alternative paths.

### Collective Intelligence
Knowledge sharing and transfer between agents.

### Neural Orchestra
Visual orchestration of agent activities.

---

## Summary Table

| Feature | Session | Status | Key Files |
|---------|---------|--------|-----------|
| Time Capsules | 259 | Active | `views_time_capsules.py` |
| Memory Palace | 251 | Active | `views_memory_palace.py` |
| Consciousness | - | Active | `consciousness.py` |
| Mythology | 541 | Active | `mythology/` |
| Agent Dreams | 247/366 | Productized | models line 8374 |
| Living Projects | 335 | Active | `living_project_service.py` |
| Income Actions | 388 | Active | `income_action_service.py` |
| Agent Evolution | 254 | Active | models line 11054 |

---

## Related Documentation

- [AGENTS.md](AGENTS.md) - Agent details
- [AUTONOMOUS_SYSTEMS.md](AUTONOMOUS_SYSTEMS.md) - Autonomous situations
- [MODELS.md](MODELS.md) - Database models
