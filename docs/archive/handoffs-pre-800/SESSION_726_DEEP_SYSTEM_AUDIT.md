# Session 726: Deep System Audit - Comprehensive Handoff

**Date:** January 7, 2026
**Purpose:** Full system audit to verify everything is connected and used
**Previous Session:** 725 (Body Coordinator Complete)

---

## Executive Summary

The unified-donkey-betz platform has grown to massive scale:
- **39,298 lines** in model files alone
- **123 service files** in core/services/
- **72 agents** in core/agents/
- **77 spiders** in ai_core/spiders/
- **210 Celery tasks** in core/tasks.py
- **39 model files** (core/models*.py)
- **3 separate Django apps** beyond core: `mythology/`, `intelligence/`, `agents/`

**Critical Question:** Is everything connected and actually used?

---

## AUDIT AREAS

### 1. MYTHOLOGY SYSTEM (HIGH PRIORITY)

**Location:** `mythology/` app (separate Django app)

**Files:**
- `mythology/models.py` - 15,105 lines
- `mythology/services.py` - 30,636 lines
- `mythology/views.py` - 40,514 lines
- `mythology/urls.py` - 1,588 lines

**Questions to Answer:**
- [ ] Is mythology/ registered in INSTALLED_APPS?
- [ ] Are mythology URLs included in main urls.py?
- [ ] Is mythology data being created/used?
- [ ] What models exist and do they have data?
- [ ] Is this connected to the main AI Assistant?
- [ ] Is mythology validation active or dormant?

**Related Files:**
- `core/agents/narrative/narrative_mythology_validator.py`
- `ai_core/agents/mythology_validator.py`
- `intelligence/mythology_enhanced_learning.py`
- `docs/handoffs/SESSION_541_MYTHOLOGY_QUARANTINE_SYSTEM.md`
- `docs/handoffs/SESSION_357_MYTHOLOGY_VALIDATION.md`
- `docs/handoffs/SESSION_355_MYTHOLOGY_INTEGRATION.md`

---

### 2. INTELLIGENCE APP (HIGH PRIORITY)

**Location:** `intelligence/` app (separate Django app)

**Key Files (80+ Python files):**
- `intelligence/core.py` - 34,916 lines (main intelligence hub?)
- `intelligence/income_builder.py` - 87,333 lines (massive!)
- `intelligence/tasks.py` - 77,510 lines
- `intelligence/consumers.py` - 53,830 lines
- `intelligence/personal_assistant_interviewer.py` - 79,999 lines
- `intelligence/mythology_enhanced_learning.py` - 19,725 lines

**Questions to Answer:**
- [ ] Is intelligence/ registered in INSTALLED_APPS?
- [ ] What's the relationship between intelligence/ and core/?
- [ ] Is income_builder.py actually being used?
- [ ] What consumers are active? (job_scanner_consumer, interview_consumer, etc.)
- [ ] Is the personal_assistant_interviewer connected to anything?
- [ ] Are intelligence/tasks.py tasks scheduled?

**Sub-directories to audit:**
- `intelligence/api/`
- `intelligence/models/`
- `intelligence/orchestration/`
- `intelligence/services/`
- `intelligence/spiders/`
- `intelligence/reallearning/`

---

### 3. AGENTS APP (MEDIUM PRIORITY)

**Location:** `agents/` app (separate Django app)

**Files:**
- `agents/agent_wiring_system.py`
- `agents/management/commands/migrate_all_discovered_agents.py`

**Questions to Answer:**
- [ ] What is this app's purpose vs core/agents/?
- [ ] Is agent_wiring_system.py being used?
- [ ] Does this duplicate functionality?

---

### 4. INTELLIGENT PROMPTING SYSTEM (HIGH PRIORITY)

**Found in 229 files** across the codebase.

**Key Files:**
- `core/views_assistant_intelligent.py`
- `docs/handoffs/SESSION_529_INTELLIGENT_PROMPTING_COMPLETE.md`

**Questions to Answer:**
- [ ] What is the intelligent prompting system?
- [ ] Is it active in the main AI Assistant flow?
- [ ] How does it interact with core/prompts/registry.py?
- [ ] Is it connected to the tool definitions?

---

### 5. PERSONAL ASSISTANT TOOLS (34 Tools)

**Location:** `core/assistant/tool_definitions.py`

**Current Tool Count:** 34 tools

**Questions to Answer:**
- [ ] Are all 34 tools actually callable?
- [ ] Which tools have handlers in personal_ai_assistant_enhanced.py?
- [ ] Are there orphaned tool definitions (defined but not handled)?
- [ ] Are there duplicate tools across different systems?

**Tool Categories to Verify:**
1. Creation tools (image, video, audio, 3D)
2. Research tools (spider, workflow)
3. Agent tools (universal_agent_tool, specific agents)
4. Intelligence tools (predictions_tool, gates_tool, pilots_tool, opportunity_manager_tool)
5. System tools (memory, project, etc.)

---

### 6. SERVICE LAYER (123 Services)

**Location:** `core/services/`

**Questions to Answer:**
- [ ] Are all 123 services imported/used somewhere?
- [ ] Which services are instantiated as singletons?
- [ ] Are there duplicate services (e.g., system_reality_checker.py vs intelligence/system_reality_checker.py)?
- [ ] What services have no callers?

**Critical Services to Verify Connection:**
- `body_coordinator.py` - Coordinates 10 body systems
- `collective_intelligence.py` - Agent learning
- `llm_provider_registry.py` - Multi-model routing
- `agent_llm_router.py` - Agent to model mapping
- `human_interface_service.py` - HITL system
- `pilot_progress.py` - Pilot tracking
- `intelligence_query.py` - Query intelligence data

---

### 7. CELERY TASKS (210 Tasks)

**Location:** `core/tasks.py` + `intelligence/tasks.py`

**Questions to Answer:**
- [ ] How many tasks are in core/tasks.py vs intelligence/tasks.py?
- [ ] Which tasks are scheduled in celery.py Beat schedule?
- [ ] Are there duplicate task names?
- [ ] Which tasks have never been executed (check logs)?

---

### 8. DATABASE MODELS (39 Model Files)

**Model Files in core/:**
```
core/models.py
core/models_agent_memory.py
core/models_agent_models.py
core/models_ai_series.py
core/models_autonomous_alerts.py
core/models_autonomous_situations.py
core/models_autonomous_studio.py
core/models_bankroll.py
core/models_betting.py
core/models_brain.py
core/models_campaign.py
core/models_circulatory.py
core/models_content_pipeline.py
core/models_conversation_artifacts.py
core/models_digestive.py
core/models_document_registry.py
core/models_engagement_metrics.py
core/models_heart.py
core/models_human_interface.py
core/models_immune.py
core/models_implementation_pipeline.py
core/models_legal.py
core/models_llm_routing.py
core/models_lungs.py
core/models_muscular.py
core/models_narrative_drift.py
core/models_nervous.py
core/models_odds_history.py
core/models_partnership.py
core/models_pilot_readiness.py
core/models_pipeline_feedback.py
core/models_podcast_studio.py
core/models_push_notifications.py
core/models_situation_triggers.py
core/models_skin_layer.py
core/models_skin.py
core/models_spine.py
core/models_unified_system.py
core/models_voice_marketplace.py
```

**Also models in:**
- `mythology/models.py`
- `intelligence/models.py`
- `intelligence/models/` directory

**Questions to Answer:**
- [ ] Which models have 0 records?
- [ ] Are all models registered in admin.py?
- [ ] Are there duplicate model definitions across apps?
- [ ] Which models are never written to?

---

### 9. FRONTEND/REACT INTEGRATION

**Location:** `frontend/` directory

**Questions to Answer:**
- [ ] Which API endpoints are called by frontend?
- [ ] Are there backend APIs with no frontend consumers?
- [ ] Is the frontend up-to-date with backend capabilities?

---

### 10. SCI-FI FEATURES (14 Features)

**Claimed 100% complete, verify:**

| Feature | Backend | Frontend | Actually Used? |
|---------|---------|----------|----------------|
| Agent Learning | core/services/collective_intelligence.py | ? | ? |
| Agent Conversations | ? | Agent Social | ? |
| Agent Dreams | ? | Agent Social | ? |
| Hive Mind | ? | Hive Mind page | ? |
| Memory Palace | ? | Memory Palace page | ? |
| Memory Clusters | ? | ? | ? |
| Mood System | ? | Agent Mood page | ? |
| Rivalries/Alliances | ? | Relationships page | ? |
| Evolution System | ? | Evolution page | ? |
| Time Travel | ? | Time Travel page | ? |
| Personality Profiles | ? | in Mood | ? |
| Time Capsules | ? | Time Capsules page | ? |
| Conversation Contract | ? | Contract page | ? |
| Spider Integration | ? | Spiders page | ? |

---

### 11. BODY HEALTH SYSTEMS (10 Systems)

**All claimed complete, verify data flow:**

| System | Service | API | Celery Task | Frontend |
|--------|---------|-----|-------------|----------|
| HEART | core/services/heart.py | /api/heart/ | check_heart | BodyHealthPage |
| LUNGS | core/services/lungs.py | /api/lungs/ | check_lungs | BodyHealthPage |
| CIRCULATORY | core/services/circulatory.py | /api/circulatory/ | check_circulatory | BodyHealthPage |
| SPINE | core/services/spine.py | /api/spine/ | check_spine | BodyHealthPage |
| IMMUNE | core/services/immune.py | /api/immune/ | check_immune | BodyHealthPage |
| DIGESTIVE | core/services/digestive.py | /api/digestive/ | check_digestive | BodyHealthPage |
| MUSCULAR | core/services/muscular.py | /api/muscular/ | check_muscular | BodyHealthPage |
| BRAIN | core/services/brain.py | /api/brain/ | check_brain | BodyHealthPage |
| SKIN | core/services/skin.py | /api/skin/ | check_skin | BodyHealthPage |
| NERVOUS | core/services/nervous.py | /api/nervous/ | check_nervous | BodyHealthPage |

---

### 12. WEBSOCKET CONSUMERS

**Questions to Answer:**
- [ ] How many WebSocket consumers exist?
- [ ] Which are in core/consumers.py vs intelligence/consumers.py?
- [ ] Are all routed in routing.py?
- [ ] Which consumers are actually used by frontend?

---

### 13. LLM ROUTING SYSTEM (Session 697-700)

**Files:**
- `core/models_llm_routing.py` - 4 models
- `core/services/llm_provider_registry.py` - Provider registry
- `core/services/agent_llm_router.py` - Agent to model routing
- `core/views_llm_routing.py` - 7 API endpoints
- `frontend/src/pages/LLMRoutingPage.tsx` - UI (incomplete)

**Questions to Answer:**
- [ ] Are all 75 agent LLM configs being used?
- [ ] Is the routing actually happening or falling back to default?
- [ ] Is LLMRoutingPage.tsx functional?

---

### 14. DUPLICATE CODE CHECK

**Known potential duplicates:**
- `core/services/system_reality_checker.py` vs `intelligence/system_reality_checker.py`
- `core/agents/` vs `agents/` app
- `core/tasks.py` vs `intelligence/tasks.py`
- Multiple mythology validators

---

## AUDIT COMMANDS

```bash
# Check if apps are installed
grep -E "mythology|intelligence|agents" core/settings.py

# Count records in key tables
.venv/bin/python manage.py shell -c "
from core.models_unified_system import *
from core.models_pilot_readiness import *
from core.models_human_interface import *
print(f'Agents: {Agent.objects.count()}')
print(f'AgentPrediction: {AgentPrediction.objects.count()}')
print(f'PilotReadinessGate: {PilotReadinessGate.objects.count()}')
print(f'PilotExecution: {PilotExecution.objects.count()}')
print(f'Opportunity: {Opportunity.objects.count()}')
"

# Check Celery Beat schedule
grep -E "'task':" core/celery.py | wc -l

# List all WebSocket routes
grep -E "path\(" core/routing.py

# Check which services are imported in tasks.py
grep "from core.services" core/tasks.py | sort | uniq
```

---

## RECOMMENDED AUDIT SEQUENCE

1. **Phase 1: App Discovery**
   - Verify mythology/, intelligence/, agents/ are in INSTALLED_APPS
   - Check URL routing for each app
   - Identify which app owns what functionality

2. **Phase 2: Data Flow Verification**
   - Trace a request from frontend → API → service → model
   - Verify Celery tasks create expected data
   - Check for dead-end data (written but never read)

3. **Phase 3: Integration Points**
   - Map how AI Assistant connects to each subsystem
   - Verify tool definitions have handlers
   - Check WebSocket consumer coverage

4. **Phase 4: Orphan Detection**
   - Find services with no imports
   - Find models with 0 records
   - Find tasks that are never scheduled

5. **Phase 5: Duplicate Resolution**
   - Identify duplicate functionality
   - Recommend consolidation

---

## EXPECTED DELIVERABLES

After the audit:
1. **Reality Score** - % of system that is actually connected and used
2. **Dead Code List** - Services, models, tasks that are orphaned
3. **Missing Connections** - Things that should be connected but aren't
4. **Consolidation Recommendations** - Duplicates to merge
5. **Activation Priorities** - Dormant features to activate

---

## SESSION 726 CONTEXT

This audit was triggered by discovering that:
1. The AI Assistant wasn't using the new `predictions_tool` because system prompt said "don't use tools for information"
2. User asked if we're over-engineering tool routing with too many keywords
3. User wants to verify everything is indeed wired up

**Goal:** Create a true picture of system state before adding more features.

---

**Start the next session by reading this document and running the audit commands.**
