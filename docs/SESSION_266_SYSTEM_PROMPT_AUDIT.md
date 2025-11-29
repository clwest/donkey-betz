# Session 266: Complete System Prompt Audit

## Overview

This document catalogs EVERY system prompt and role definition across the platform.
The goal is to understand what exists so we can rewrite everything with unified Super Platform awareness.

---

## CRITICAL FINDING: Prompt Fragmentation

We have **40+ different prompt locations** across the codebase, many outdated or conflicting.
Most were written incrementally over 266 sessions without a unified vision.

---

## 1. MAIN PERSONAL ASSISTANT

### Location: `core/personal_ai_assistant_enhanced.py`
**Lines: 4910-5070** (just rewritten in Session 266)

**Purpose:** Main user-facing AI assistant system prompt

**Current State:** JUST REWRITTEN with Super Platform awareness
- Now includes Spider Network (70 spiders)
- Agent Ecosystem (22 agents)
- Clear consultative vs. creation distinction
- Style variety reminders

**Status:** ✅ UPDATED (Session 266)

---

## 2. SUPER PLATFORM PROMPT BUILDER

### Location: `core/super_platform/prompt_builder.py`
**Lines: 44-51** (BASE_IDENTITY) + **54-135** (PROMPT_SECTIONS)

**Purpose:** Dynamic context-aware prompt building for Super Platform

**Current State:** Good foundation from Session 264
- Has BASE_IDENTITY with platform overview
- Context-specific sections for spider data, creation tools, memory, mood
- Query type-specific intros

**Status:** ✅ GOOD (Session 264) - but needs integration

---

## 3. CONVERSATION ROLES (Agent-to-Agent)

### Location: `core/conversation_roles.py`
**Lines: 82-259** (AGENT_CONVERSATION_ROLES)

**Purpose:** Role definitions for agent conversations (Hive Mind, etc.)

**Defined Roles:**
- ResearchAgent (DATA REALIST, PATTERN ENFORCER)
- ContentStrategyAgent (STORYTELLING, PSYCHOLOGY SPECIALIST)
- ImageAgent (VISUAL INTELLIGENCE)
- VideoAgent (VIDEO PRODUCTION)
- CreativeDirectorAgent (CREATIVE VISION)
- SEOOptimizerAgent (DISCOVERABILITY)
- TrendAnalysisAgent (TREND INTELLIGENCE)
- default (generic template)

**Status:** ⚠️ OUTDATED
- References "67 spiders" (now 70)
- Doesn't mention Super Platform integration
- Missing many newer agents

---

## 4. AI CONTENT AGENTS (Registry)

### Location: `core/services/ai_content_agents.py`
**Lines: 129-350** (prompt_template for each agent)

**Agents with prompts:**
1. image_generation_agent - "expert image generation assistant"
2. video_generation_agent - "expert video creation assistant"
3. style_discovery_agent - "visual style analyst and trend forecaster"
4. prompt_engineering_agent - "expert prompt engineer"
5. model_recommender_agent - "AI model specialist"
6. product_idea_agent - "digital product strategist"
7. content_strategy_agent - "content strategist"
8. design_assistant_agent - "design assistant"
9. trend_analysis_agent - "trend analyst"
10. research_agent - "research specialist"
11. template_curator_agent - "template specialist"
12. opportunity_scanner_agent - "opportunity scout"
13. brand_identity_agent - "brand identity specialist"
14. innovation_scout_agent - "innovation scout"

**Status:** ❌ VERY OUTDATED
- Generic prompts with no platform context
- No mention of spiders, Super Platform, or unified vision
- Written early in development

---

## 5. EXECUTIVE AGENTS

### Location: `agents/cto_agent.py`
**Lines: 140+** (system_prompt)

**Purpose:** CTO Agent for technical decisions

**Status:** ⚠️ NEEDS REVIEW

---

### Location: `agents/coo_agent.py`
**Lines: 408+** (system prompt)

**Purpose:** COO Agent for operations

**Status:** ⚠️ NEEDS REVIEW

---

### Location: `agents/meeting_coordinator_agent.py`
**Lines: 310+** (system prompt)

**Purpose:** Meeting coordination for boardroom sessions

**Status:** ⚠️ NEEDS REVIEW

---

## 6. CREATION AGENTS

### Location: `agents/audio_agent.py`
**Lines: 159+** (system_prompt)

**Purpose:** Audio generation with ElevenLabs

**Status:** ⚠️ NEEDS REVIEW

---

### Location: `agents/video_agent.py`
**Lines: 149+** (system_prompt)

**Purpose:** Video generation with Runway ML

**Status:** ⚠️ NEEDS REVIEW

---

## 7. LLM ENFORCER (Task-Type Prompts)

### Location: `core/llm_enforcer.py`
**Lines: 222-242** (TASK_TYPE_PROMPTS)

**Purpose:** Task-specific system prompts for different content types

**Defined prompts:**
- cover_letter: "expert cover letter writer"
- content: "professional content creator"
- analysis: "expert analyst"
- code: "expert programmer"
- general: "helpful AI assistant"

**Status:** ❌ OUTDATED - Generic, no platform context

---

## 8. CELERY TASKS (Agent Conversations)

### Location: `core/tasks.py`
**Lines: 3595, 4001, 4213, 4410, 4529**

**Purpose:** System prompts for agent conversations, dreams, hive mind

**Status:** ⚠️ DYNAMIC but needs review

---

## 9. COMMAND CENTER AI

### Location: `core/command_center_ai.py`
**Lines: 461-527**

**Purpose:** AI Command Center system prompts

**Status:** ⚠️ NEEDS REVIEW

---

## 10. ADVISOR API

### Location: `core/views_advisor_api.py`
**Lines: 68-86**

**Purpose:** Legendary advisor prompts (Warren Buffett, etc.)

**Status:** ⚠️ NEEDS REVIEW

---

## 11. TIME CAPSULES / PROPHECIES

### Location: `core/views_time_capsules.py`
**Lines: 479, 643**

**Purpose:** Agent time capsule and prophecy prompts

**Status:** ⚠️ NEEDS REVIEW

---

## 12. RAG ASSISTANT

### Location: `core/views_assistant_rag_enhanced.py`
**Lines: 335-396**

**Purpose:** RAG-enhanced assistant prompts

**Status:** ⚠️ NEEDS REVIEW - may conflict with main assistant

---

## 13. AGENT INTEGRATION

### Location: `core/agent_integration.py`
**Lines: 383-408**

**Purpose:** Dynamic agent execution prompts

**Status:** ⚠️ NEEDS REVIEW

---

## 14. UNIVERSAL LLM EXECUTOR

### Location: `agents/universal_llm_executor.py`
**Lines: 126+**

**Purpose:** Generic agent execution prompt template

**Status:** ⚠️ NEEDS REVIEW

---

## 15. ENHANCED TASKS

### Location: `agents/tasks_enhanced.py`
**Lines: 233-265**

**Purpose:** Enhanced agent task prompts

**Status:** ⚠️ NEEDS REVIEW

---

## SUMMARY TABLE

| Category | Location | Status | Priority |
|----------|----------|--------|----------|
| Main Assistant | personal_ai_assistant_enhanced.py | ✅ UPDATED | HIGH |
| Super Platform Builder | prompt_builder.py | ✅ GOOD | HIGH |
| Conversation Roles | conversation_roles.py | ⚠️ OUTDATED | HIGH |
| AI Content Agents | ai_content_agents.py | ❌ OUTDATED | HIGH |
| Executive Agents | cto/coo/meeting agents | ⚠️ NEEDS REVIEW | MEDIUM |
| Creation Agents | audio/video agents | ⚠️ NEEDS REVIEW | MEDIUM |
| LLM Enforcer | llm_enforcer.py | ❌ OUTDATED | MEDIUM |
| Celery Tasks | tasks.py | ⚠️ DYNAMIC | MEDIUM |
| Command Center | command_center_ai.py | ⚠️ NEEDS REVIEW | LOW |
| Advisor API | views_advisor_api.py | ⚠️ NEEDS REVIEW | LOW |
| Time Capsules | views_time_capsules.py | ⚠️ NEEDS REVIEW | LOW |
| RAG Assistant | views_assistant_rag_enhanced.py | ⚠️ NEEDS REVIEW | MEDIUM |
| Agent Integration | agent_integration.py | ⚠️ NEEDS REVIEW | MEDIUM |
| Universal Executor | universal_llm_executor.py | ⚠️ NEEDS REVIEW | MEDIUM |

---

## RECOMMENDED ARCHITECTURE

### Tier 1: Central Prompt Registry
Create a single source of truth: `core/prompts/registry.py`

```python
class PromptRegistry:
    """Central registry for all system prompts."""

    # Shared platform context - used by ALL prompts
    PLATFORM_CONTEXT = """..."""

    # Main assistant prompt
    PERSONAL_ASSISTANT = """..."""

    # Agent-specific prompts
    AGENTS = {
        'ResearchAgent': """...""",
        'ImageAgent': """...""",
        ...
    }

    # Advisor prompts
    ADVISORS = {
        'Warren Buffett': """...""",
        ...
    }
```

### Tier 2: Dynamic Prompt Builder
Keep `prompt_builder.py` but have it pull from the registry.

### Tier 3: Context Injection
Each prompt gets:
1. Platform context (spiders, agents, capabilities)
2. User context (preferences, history)
3. Task context (what they're trying to do)

---

## NEXT STEPS

1. **Create prompt registry** - Single source of truth
2. **Rewrite all agent prompts** - Super Platform aware
3. **Update conversation roles** - Current system info
4. **Deprecate old prompts** - Remove scattered definitions
5. **Test thoroughly** - Ensure no regressions

---

## SESSION 266 STATUS

- [x] Audit complete
- [ ] Registry created
- [ ] Prompts rewritten
- [ ] Testing complete
