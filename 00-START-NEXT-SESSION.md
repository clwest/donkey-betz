# Session 947 - Start Here

**Previous Session:** 946 (Learning Loop Backend)
**Date:** February 5, 2026
**Status:** 76 Agents | 77 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **166 INITIATIVES** | **Unified PA: FULL STACK** | **Voice System: COMPLETE** | **User Learning UI: COMPLETE** | **Spider Context: EXTENDED** | **Boardroom Tab: LIVE** | **PA Boardroom: ENHANCED** | **Boardroom Learning: ACTIVE** | **Auto-Approve: SCHEDULED** | **Experiment Cleanup: SCHEDULED** | **Bulk Actions: COMPLETE** | **Stage Distribution: FIXED** | **Operations Tab: FIXED** | **ConceptForge Plan: COMPLETE** | **Stale Cleanup: ENHANCED** | **Learning Loop: ACTIVE**

---

## Session 946 Summary (Just Completed)

### Learning Loop Backend - Full Implementation

Implemented the unified learning feedback loop that connects execution outcomes to agent prompts.

**Components Built:**

1. **LearningLoopOrchestrator** (`core/services/learning_loop_orchestrator.py`)
   - Central service unifying scattered learning infrastructure
   - Analyzes ToolCallRecord outcomes (success rates, latency, problem combinations)
   - Analyzes DecisionRecord outcomes (confidence calibration, type success rates)
   - Extracts actionable learnings with confidence scores
   - Persists learnings to LearningPattern model

2. **Success Signals** defined for common tools:
   - `web_search`: 10s latency threshold, success indicators
   - `analyze_filing`: 30s threshold, parsing error detection
   - `get_stock_data`: 5s threshold, data validation

3. **Learning Extraction Patterns:**
   - `tool_reliability`: Tools with <70% or >95% success rates
   - `agent_performance`: Agents struggling with tool usage
   - `agent_tool_mismatch`: Specific agent-tool combinations failing
   - `confidence_calibration`: When high-confidence decisions fail

4. **Prompt Injection:**
   - `_get_system_learnings_section()` method added to BaseAgent
   - Integrated into all 3 prompt builders:
     - `_build_prompt_with_attribution`
     - `_build_prompt`
     - `_build_intelligent_prompt` (preferred method)
   - Learnings appear as "## System Learnings" section in prompts

5. **Celery Scheduled Task:**
   - `run_learning_loop_cycle` runs every 6 hours
   - Analyzes last 7 days of execution data
   - Extracts and persists learnings automatically

**Files Changed:**
- `core/services/learning_loop_orchestrator.py` - **NEW** - Central orchestrator
- `core/agent_context_middleware.py` - Added `get_system_learnings_for_agent()` function
- `core/agents/base_agent.py` - Added `_get_system_learnings_section()` + injection in 3 builders
- `core/tasks.py` - Added `run_learning_loop_cycle` Celery task
- `core/celery.py` - Scheduled learning loop every 6 hours

**How It Works:**
```
ToolCallRecord / DecisionRecord
         ↓
  LearningLoopOrchestrator.extract_learnings()
         ↓
  LearningPattern (persisted)
         ↓
  BaseAgent._get_system_learnings_section()
         ↓
  Agent prompts include "## System Learnings"
```

---

## PRIORITY OPTIONS FOR NEXT SESSION

### Option B: Spider Context for Remaining Paths
Extend SpiderContextBuilder to:
- `creative_orchestrator.py` (13 locations)
- `research_orchestrator.py` (5 locations)
- Other content generation tasks

### Option C: Boardroom ML Improvements
Improve ML recommendations for boardroom items:
- Train on actual user decisions
- Better confidence scoring
- Recommendations based on item content, not just type

### Option D: Initiative Source Cleanup
Investigate why so many junk initiatives are being created:
- Find where "Auto-created From Conversation Decision" comes from
- Add validation before initiative creation
- Consider gating initiative creation on founder intent

### Option E: Typography/UI Polish
Continue modernizing markdown rendering:
- Verify ChatMarkdown and Prose components work across all pages
- Test prose-dark theme in production
- Address any remaining hard-to-read text

### Option F: Learning Loop Refinement
Build on the learning loop with:
- More success signals for other tools
- User feedback integration
- Learning effectiveness tracking
- Dashboard for viewing active learnings

---

## Recent Session History

| Session | Focus | PRs |
|---------|-------|-----|
| **946** | Learning Loop Backend - LearningLoopOrchestrator, prompt injection, scheduled extraction | - |
| **945** | Stale Initiative Cleanup - New junk patterns, activity tracking, last_activity_at field | #901 |
| **944** | Operations Tab Fix + PA Boardroom Listing + ConceptForge Dedupe | #897, #898, #899 |
| **943** | Stage Distribution Fix + Stale Investigation | #876 |
| **942** | Integrity Anomaly Investigation + Halted Experiment Cleanup + Bulk Boardroom Actions | #874, #875 |
| **941** | Boardroom Auto-Approve Scheduled | #871 |
| **940** | PA Boardroom Complete (Awareness + Tools + Triage + Learning) | #866-#869 |

---

## Key Files Reference

### Session 946 - Learning Loop
| File | Purpose |
|------|---------|
| `core/services/learning_loop_orchestrator.py` | Central orchestrator - analyze, extract, persist learnings |
| `core/agent_context_middleware.py` | `get_system_learnings_for_agent()` helper |
| `core/agents/base_agent.py` | `_get_system_learnings_section()` + prompt injection |
| `core/tasks.py` | `run_learning_loop_cycle` - scheduled every 6 hours |
| `core/celery.py` | Beat schedule for learning loop |

### Initiative Pipeline
| File | Purpose |
|------|---------|
| `core/models_document_registry.py` | `Initiative`, `InitiativeStage` models |
| `core/tasks.py` | `cleanup_junk_initiatives` - daily at 4 AM |
| `core/models_unified_system.py` | `HiveMindSession` - conversations linked to initiatives |

### SKIN Layer / Operations Tab
| File | Purpose |
|------|---------|
| `core/tasks.py` | `universal_agent_workspace_output()` - creates WorkspaceOperations |
| `core/models_skin_layer.py` | `WorkspaceOperation` model |
| `frontend/src/pages/workspace/tabs/OperationsTab.tsx` | Operations Tab UI |

### Boardroom System
| File | Purpose |
|------|---------|
| `core/models_unified_system.py` | `AgentDecisionSummary` - boardroom decisions |
| `core/services/deduplication_service.py` | `dedupe_decision_summary_blocks()` |
| `core/conceptforge/orchestrator.py` | Provenance headers + placeholder validation |
| `core/services/experiment_collision_service.py` | Experiment collision detection |

---

**Session 947 Focus: Choose priority option above and continue building!**
