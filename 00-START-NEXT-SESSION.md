# Start Next Session Here

**Last Session:** 350 - Domain-Aware Spider Targeting + Agent Learning Cleanup
**Date:** December 4, 2025
**Status:** 102 spiders | 36 categories | 79 agents | Domain-Targeted Business Research

---

## What Happened in Session 350

### 1. Domain-Aware Spider Targeting (Major Feature)
- Created `DomainExtractionService` with 13 business domains
- Business research agents now extract domain from project descriptions
- Spider queries are domain-specific (fitness → fitness keywords, fintech → finance keywords)
- Honest data reporting when domain-specific data is limited

### 2. Business Viability Check ("Idiot Protector")
- GPT-4o-mini scores business ideas 0-100
- Detects jokes/absurd ideas (e.g., "Onion Bar - restaurant serving only raw onions")
- Shows warning for low-scoring ideas before research begins

### 3. Trend Analysis UI Fix
- Fixed "1 data point" display → now shows actual count (21 data points)
- Fixed summary showing task text → now shows actual trend topics with relevance scores

### 4. Agent Learning [Learned] Prefix Cleanup
- Fixed accumulation: `[Learned] [Learned] [Learned]...` → `[Learned]`
- Cleaned 20 existing database entries
- UI now strips prefixes for clean display

---

## Session 351 Priority: Agent Knowledge → Research Integration

**Big Question:** Are agents actually using their shared knowledge and conversations in business research?

### Key Investigation Areas

1. **Agent Knowledge Sharing**
   - Agents share knowledge via `KnowledgeTransfer` records
   - Are these insights being injected into research prompts?
   - Location: `core/tasks.py` (agent_learning_cycle)

2. **Agent Conversations**
   - Agents have real-time conversations via WebSocket
   - These discussions contain valuable insights
   - Location: `core/agent_conversation_consumer.py`

3. **The Boardroom**
   - Executive agents (CTO, COO, etc.) discuss strategy
   - These decisions should influence business research
   - Location: Check for boardroom-related code

4. **Research Pipeline Integration Points**
   - `ResearchOrchestrator` chains agents together
   - Where can we inject agent knowledge/conversations?
   - Location: `core/services/research_orchestrator.py`

### Files to Investigate

```
core/tasks.py                              # agent_learning_cycle, knowledge transfers
core/services/research_orchestrator.py     # Research pipeline
core/agent_conversation_consumer.py        # Agent chat WebSocket
core/services/collective_intelligence.py   # Collective knowledge API
core/models_unified_system.py              # KnowledgeTransfer, SharedKnowledge models
```

### Goal for Session 351

Connect the dots:
```
Agent Conversations → Shared Insights → Research Pipeline → Better Business Plans
         ↓
   Boardroom Decisions → Research Context
```

---

## Current System State

| Component | Count |
|-----------|-------|
| **Spiders** | **102** |
| **Categories** | **36** |
| **Agents** | **79** (69 legacy + 10 clean) |
| **Data Points** | **9,983+** |
| **Business Domains** | **13** |
| **Knowledge Transfers** | Check DB |
| **Agent Conversations** | Real-time WebSocket |

---

## Quick Start

```bash
make start
make celery  # For background tasks
open http://localhost:8000/ai-studio/
```

---

## Key Documentation

- **Session 350 Details:** `docs/handoffs/SESSION_350_DOMAIN_AWARE_SPIDER_TARGETING.md`
- **Architecture:** `docs/ARCHITECTURE.md`
- **Agents:** `docs/AGENTS.md`

---

## Commits from Session 350

1. `16e547d` - feat: Domain-aware spider targeting + business viability check
2. `a1735cf` - fix: Trend Analysis display showing "1 data point"
3. `97c3fbf` - fix: Clean up [Learned] prefix accumulation in agent learning

---

**Next: Investigate if agent knowledge/conversations flow into research!**
