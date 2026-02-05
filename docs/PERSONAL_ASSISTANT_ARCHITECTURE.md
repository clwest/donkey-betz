# Personal Assistant (PA) Architecture

**Last Updated:** Session 931
**Status:** Gap Analysis Complete | Refactor Planned

## Overview

The Personal Assistant is the "brain" of the platform - the central interface that routes user requests to 74 agents, 77 spiders, 25 advisors, and 9 body systems.

## Current State: Fragmented Architecture

### The Problem: 3-4 Overlapping PA Implementations

| File | Lines | Purpose | Used By |
|------|-------|---------|---------|
| `personal_assistant_agent.py` | 592KB | Traffic cop routing | Agent ecosystem |
| `personal_ai_assistant.py` | ~400 | User learning + personalization | Some views |
| `personal_ai_assistant_enhanced.py` | 13,479+ | Full features + DB access | Enhanced endpoints |
| `unified_personal_assistant.py` | Large | Neural + orchestration | Unified endpoint |
| `consumers_unified_v2.py` | 360 | WebSocket real-time | Frontend WebSocket |

**Impact:**
- Behavior inconsistent between endpoints
- Numbers drift (e.g., 609 attention items vs 17)
- "Tool exists" ≠ "tool works"
- Failures disappear silently

---

## Tool Inventory (47 Tools)

### Creation Tools (8)
| Tool | Handler | Status |
|------|---------|--------|
| `image_generation_agent` | ImageAgent | ✅ Works |
| `image_editing_agent` | ImageEditingAgent | ✅ Works |
| `video_generation_agent` | VideoAgent | ✅ Works |
| `video_editing_agent` | VideoEditingAgent | ✅ Works |
| `audio_generation_agent` | AudioAgent | ✅ Works |
| `three_d_generation_agent` | ThreeDAgent | ✅ Works |
| `character_training_agent` | CharacterTrainingAgent | ✅ Works |
| `talking_character_agent` | TalkingCharacterAgent | ✅ Works |

### Research Tools (7)
| Tool | Handler | Status |
|------|---------|--------|
| `web_search` | ResearchAgent | ✅ Works |
| `competitor_analysis_agent` | CompetitorAnalysisAgent | ✅ Works |
| `customer_research_agent` | CustomerResearchAgent | ✅ Works |
| `brand_strategy_agent` | BrandStrategyAgent | ✅ Works |
| `content_strategy_agent` | ContentStrategyAgent | ✅ Works |
| `marketing_strategy_agent` | MarketingStrategyAgent | ✅ Works |
| `content_writer_agent` | ContentWriterAgent | ✅ Works |

### ML Pipeline Tools (5)
| Tool | Handler | Status |
|------|---------|--------|
| `opportunity_manager_tool` | OpportunityManager | ⚠️ Needs audit |
| `task_manager_tool` | TaskManager | ⚠️ Needs audit |
| `pipeline_orchestrator_tool` | PipelineOrchestrator | ⚠️ Needs audit |
| `revenue_tracker_tool` | RevenueTracker | ⚠️ Needs audit |
| `ml_analysis` | MLEngine | ⚠️ Needs audit |

### Universal Access Tools (2)
| Tool | Handler | Status |
|------|---------|--------|
| `universal_agent_tool` | AgentRegistry | ✅ Works |
| `workspace_tool` | WorkspaceManager | ✅ Works |

### Body System Tools (3)
| Tool | Handler | Status |
|------|---------|--------|
| `get_body_vitals` | BodyVitalsService | ✅ Works |
| `check_resource_budget` | LungsSystem | ✅ Works |
| `get_system_alerts` | AlertsService | ✅ Works |

### Intelligence Tools (5)
| Tool | Handler | Status |
|------|---------|--------|
| `predictions_tool` | PredictionsService | ⚠️ Needs audit |
| `gates_tool` | GatesService | ⚠️ Needs audit |
| `pilots_tool` | PilotsService | ⚠️ Needs audit |
| `human_decisions_tool` | HumanDecisionsService | ⚠️ Needs audit |
| `reasoning_engine_tool` | ThinkingAgent | ⚠️ Needs audit |

### Workflow Tools (5)
| Tool | Handler | Status |
|------|---------|--------|
| `workflow_orchestration_agent` | WorkflowAgent | ✅ Works |
| `create_brand_video` | BrandVideoWorkflow | ✅ Works |
| `create_project_from_research` | ProjectCreator | ✅ Works |
| `strategic_review` | StrategyReviewer | ✅ Works |
| `coleadership_agent` | CoLeadershipAgent | ✅ Works |

### Legal Tools (1)
| Tool | Handler | Status |
|------|---------|--------|
| `legal_doc_drafter_agent` | LegalDocDrafterAgent | ✅ Works |

---

## Gap Analysis Summary

### Critical Issues

| Issue | Current State | Fix |
|-------|---------------|-----|
| **Fragmented PA** | 3-4 implementations | Single canonical entrypoint |
| **Silent Failures** | Tools fail without trace | ToolDispatcher with structured results |
| **No TTS Output** | Voice input only | ElevenLabs TTS on responses |

### High Priority (Defer Until Above Fixed)

| Issue | Current State | Why Defer |
|-------|---------------|-----------|
| Learning Loop | Data collected, not used | Needs success signals defined first |
| Persistent Memory | Multiple memory systems | Don't create another until consolidated |
| Proactive Intelligence | Optional, silent | Fix failures first or it becomes noisy |

### Attention Item Mismatch (609 vs 17)

**Root Cause:** Different endpoints return different counts
- `Human Interface attention items` → 609 (all critical/high/etc)
- `get_system_attention` → 17 (curated)

**Fix:** Single "Attention Aggregator" that returns both with labels:
```json
{
  "system_attention": {"count": 17, "source": "curated"},
  "human_attention": {"count": 609, "source": "all_items"}
}
```

---

## Target Architecture

```
┌─────────────────────────────────────────────────────────┐
│              UnifiedPA (Single Entrypoint)              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Build Context                                       │
│     ├── User Profile                                    │
│     ├── Last N conversation turns                       │
│     └── System vitals (when relevant)                   │
│                                                         │
│  2. Route Request                                       │
│     ├── Semantic routing (embeddings)                   │
│     └── Keyword fallback                                │
│                                                         │
│  3. Execute via ToolDispatcher                          │
│     ├── Wrap ALL tool calls                             │
│     ├── Return structured result                        │
│     └── Never fail silently                             │
│                                                         │
│  4. Log Outcome                                         │
│     ├── Success/failure                                 │
│     ├── Latency                                         │
│     └── Trace ID for debugging                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## ToolDispatcher Contract

Every tool call returns:
```json
{
  "ok": true,
  "tool": "human_decisions_tool",
  "latency_ms": 1234,
  "error_code": null,
  "error_message": null,
  "trace_id": "abc123",
  "result": {...}
}
```

On failure:
```json
{
  "ok": false,
  "tool": "human_decisions_tool",
  "latency_ms": 5000,
  "error_code": "TOOL_TIMEOUT",
  "error_message": "Tool execution exceeded 5s timeout",
  "trace_id": "abc123",
  "result": null
}
```

---

## TTS Integration

### Response Schema (Extended)
```json
{
  "type": "message",
  "content": "Here are your pending decisions...",
  "audio_url": "/media/audio_cache/2026/02/abc123.mp3",
  "trace_id": "abc123",
  "tool_runs": [
    {"tool": "human_decisions_tool", "ok": true, "latency_ms": 234}
  ]
}
```

### Narration Feature
- "Listen" button on any PA message
- "Narrate Conversation" button on HiveMind sessions
- Stitches messages into podcast-style audio

---

## Implementation Plan

### Phase 1: Single Entrypoint + ToolDispatcher (Session 931)
1. Create `UnifiedPAEntrypoint` class - single front door
2. Create `ToolDispatcher` with structured results
3. Route all UI requests through entrypoint
4. Surface `trace_id` in responses

### Phase 2: TTS Output (Session 931)
1. Add ElevenLabs TTS wrapper tool
2. Extend response schema with `audio_url`
3. Add "Listen" button to frontend
4. Add "Narrate" feature for conversations

### Phase 3: Attention Aggregator (Session 932)
1. Create unified attention endpoint
2. Label sources (system vs human)
3. Update frontend to show labeled counts

### Phase 4: Learning Loop (Future)
1. Define success signals
2. Implement feedback collection
3. Weight recent performance
4. Inject into prompts

---

## Files to Modify

| File | Change |
|------|--------|
| `core/services/unified_pa_entrypoint.py` | NEW - Single front door |
| `core/services/tool_dispatcher.py` | NEW - Centralized tool execution |
| `core/services/pa_tts_service.py` | NEW - TTS wrapper |
| `core/consumers_unified_v2.py` | Route through entrypoint |
| `core/views_personal_assistant.py` | Route through entrypoint |
| `frontend/src/components/ListenButton.tsx` | NEW - Play button |
| `frontend/src/api.ts` | Add TTS endpoint |

---

## Related Documentation

- [AGENTS.md](AGENTS.md) - Agent documentation (74 agents)
- [SERVICES.md](SERVICES.md) - Services layer (120 services)
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
