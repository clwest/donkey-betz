---
originating_session: 1002
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1002C: super() Fallback for 31 Agents

**Date:** February 13, 2026
**Previous:** Session 1002B (Agent Delegation & Shared Tools)

## Problem

Session 1002B centralized `delegate_to_specialist`, `web_search`, and `spider_query` handlers in `BaseAgent._execute_tool_call()`. However, 31 agents override `_execute_tool_call()` and return `{'success': False, 'error': "Unknown tool: ..."}` for unrecognized tools instead of falling through to `super()`. This meant the centralized handlers were unreachable for those agents -- they could never use `web_search` or `spider_query` even if the tools were included in their tool definitions.

## Solution

### Change 1: BaseAgent returns error dict instead of raising

`BaseAgent._execute_tool_call()` previously raised `NotImplementedError` for unrecognized tools. All subclass overrides return error dicts. Adding `super()` calls to those subclasses would cause an exception instead of a dict return, crashing agent execute flows.

Fix: Changed `raise NotImplementedError(...)` to `return {'success': False, 'error': ...}`. The 19 agents that already called `super()` with `try/except NotImplementedError` still work fine (the except just never triggers).

**File:** `core/agents/base_agent.py` (line ~2633)

### Change 2: 31 agents fall through to super()

Replaced each agent's final error return with `return super()._execute_tool_call(tool_name, arguments)`.

## Files Modified (32 total)

### BaseAgent
- `core/agents/base_agent.py` -- NotImplementedError -> error dict return

### Pattern A: 25 agents with standard else/return error
1. `core/agents/analysis/opportunity_scoring_agent.py`
2. `core/agents/analysis/trend_analysis_agent.py`
3. `core/agents/audio_agent.py`
4. `core/agents/business/brand_strategy_agent.py`
5. `core/agents/business/competitor_analysis_agent.py`
6. `core/agents/business/customer_research_agent.py`
7. `core/agents/campaign_orchestrator_agent.py`
8. `core/agents/executive/coo_agent.py`
9. `core/agents/executive/creative_director_agent.py`
10. `core/agents/executive/cto_agent.py`
11. `core/agents/executive/meeting_coordinator_agent.py`
12. `core/agents/image_editing_agent.py`
13. `core/agents/legal/legal_doc_drafter_agent.py`
14. `core/agents/resolve_agent.py`
15. `core/agents/security/content_audit_agent.py`
16. `core/agents/security/memory_isolation_agent.py`
17. `core/agents/strategy/brand_identity_agent.py`
18. `core/agents/strategy/content_strategy_agent.py`
19. `core/agents/strategy/seo_optimizer_agent.py`
20. `core/agents/strategy/social_media_agent.py`
21. `core/agents/three_d_agent.py`
22. `core/agents/training/character_training_agent.py`
23. `core/agents/training/trained_creation_agent.py`
24. `core/agents/video_agent.py`
25. `core/agents/video_editing_agent.py`

### Pattern B: 6 agents with variant endings
26. `core/agents/content_writer_agent.py` -- plain return error (no else keyword)
27. `core/agents/image_agent.py` -- early-return guard `if tool_name != "generate_image"`
28. `core/agents/personal_assistant_agent.py` -- bare return after elif block
29. `core/agents/prompt_engineering_agent.py` -- returned `{"error": ...}` (no success key)
30. `core/agents/research_agent.py` -- standard else with custom message
31. `core/agents/system_intelligence_agent.py` -- returned `{"error": ...}` (no success key)

### Intentionally Skipped (4 agents)
- `core/agents/content_executor_agent.py` -- programmatic, rejects ALL tools by design
- `core/agents/opportunity_pipeline_agent.py` -- programmatic, rejects ALL tools by design
- `core/agents/workflow_orchestration_agent.py` -- programmatic, rejects ALL tools by design
- `core/agents/workflow_agent.py` -- special `delegate_to_agent` tool, not standard delegation

## Verification

1. **Gap check:** `grep -rl "def _execute_tool_call" | wc` (52) minus `grep -rl "super()._execute_tool_call" | wc` (50) = 4 files without super() -- exactly the 4 intentionally skipped agents (content_executor, opportunity_pipeline, workflow_agent, workflow_orchestration).
2. **Import check:** All 31 modified agents import successfully.
3. **BaseAgent behavior:** `BaseAgent._execute_tool_call('nonexistent_tool', {})` returns `{'success': False, 'error': "..."}` (does not raise).
4. **Spot-check:** `ResearchAgent._execute_tool_call('nonexistent_tool', {})` returns error dict via super() chain.

## Change 3: Universal web_search + spider_query tool injection

Only 6 stock agents manually included `WEB_SEARCH_TOOL` in their tool schemas. Zero agents included `SPIDER_QUERY_TOOL`. The LLM can only call tools it sees in the schema, so centralized handlers were unreachable for most agents.

Fix: Added `_get_tools_with_shared()` to BaseAgent that auto-injects `WEB_SEARCH_TOOL` and `SPIDER_QUERY_TOOL` (with dedup) into every agent's tool list. Called by `get_tools_with_delegation()` for delegating agents and directly in `_call_llm_with_tools()` for non-delegating agents.

**File:** `core/agents/base_agent.py`

## Change 4: Fix regression in 4 stock agents with try/except NotImplementedError

Since Change 1 made BaseAgent return a dict instead of raising, the `try: return super()... except NotImplementedError: pass` pattern in 4 stock agents became a bug -- `super()` returned an error dict for the agent's own tools instead of raising, so the agent's own handlers were never reached.

Fix: Removed the `try/except` block and moved `super()` to the end (same pattern as all other agents).

**Files:**
- `core/agents/stocks/bull_case_agent.py`
- `core/agents/stocks/bear_case_agent.py`
- `core/agents/stocks/institutional_watcher_agent.py`
- `core/agents/stocks/stock_analyst_agent.py`

## Change 5: Remove redundant delegate_to_specialist elif blocks

Since BaseAgent now handles `delegate_to_specialist` via the `super()` fallback, all 59 agents with explicit `delegate_to_specialist` elif blocks in their tool handlers had redundant code. Removed all delegate blocks using a programmatic script.

**Files:** 59 agent files (all except `base_agent.py` and `workflow_agent.py`)

## Change 6: Add super() fallback to 14 newly discovered agents

During the delegate block cleanup, discovered 14 agents that had their own tool handler methods (`_execute_tool`, `_handle_tool_call`) but no fallback to BaseAgent. These agents would silently fail on `web_search`, `spider_query`, and `delegate_to_specialist` tool calls.

Fix: Replaced final error returns with `super()._execute_tool_call(tool_name, args)`.

**Files:**
1. `core/agents/analysis/market_intelligence_agent.py` -- `_execute_tool`
2. `core/agents/business/base_business_research_agent.py` -- `handle_custom_tool` default
3. `core/agents/content/contrarian_agent.py` -- `_execute_tool` (inside try/except)
4. `core/agents/content/performance_analyst_agent.py` -- `_execute_tool` (inside try/except)
5. `core/agents/content/topic_miner_agent.py` -- `_execute_tool` (inside try/except)
6. `core/agents/narrative/cultural_impact_agent.py` -- `_handle_tool_call`
7. `core/agents/narrative/narrative_drift_coordinator.py` -- `_handle_tool_call`
8. `core/agents/narrative/narrative_historian_agent.py` -- `_handle_tool_call`
9. `core/agents/narrative/trend_break_detector_agent.py` -- `_handle_tool_call`
10. `core/agents/podcast/debate_advocate_agent.py` -- `_handle_tool_call`
11. `core/agents/podcast/debate_skeptic_agent.py` -- `_handle_tool_call`
12. `core/agents/podcast/moderator_agent.py` -- `_handle_tool_call`
13. `core/agents/stocks/signal_scanner_agent.py` -- `_handle_tool_call`
14. `core/agents/platform_audit_agent.py` -- `_execute_tool`

## Final Verification

**Gap check:** 68 agents with tool handlers, 64 with `super()._execute_tool_call` = 4 gap, exactly the intentionally skipped agents (content_executor, opportunity_pipeline, workflow_agent, workflow_orchestration).

## Change 7: Fix 9 agents bypassing shared tool injection via direct API calls

Nine agents make direct `client.chat.completions.create()` calls with `tools=self.tools`, bypassing `BaseAgent._call_openai()` and its automatic tool injection. Their LLMs never saw `web_search`, `spider_query`, or `delegate_to_specialist`.

Fix: Replaced `tools=self.tools` with `tools=self.get_tools_with_delegation()` at all 9 call sites.

**Files:**
1. `core/agents/analysis/market_intelligence_agent.py` (line 308)
2. `core/agents/business/base_business_research_agent.py` (line 560) -- fixes all child agents
3. `core/agents/narrative/narrative_drift_coordinator.py` (line 1376)
4. `core/agents/platform_audit_agent.py` (line 287)
5. `core/agents/stocks/stock_analyst_agent.py` (line 323)
6. `core/agents/stocks/institutional_watcher_agent.py` (line 223)
7. `core/agents/stocks/market_anomaly_detector_agent.py` (line 283)
8. `core/agents/stocks/market_movement_monitor_agent.py` (line 227)
9. `core/agents/system_intelligence_agent.py` (line 242)

**Verification:** `grep -rn "tools=self\.tools" core/agents/` returns 0 matches (excluding `__pycache__` and `base_agent.py`).

## Result

All agents that go through `_call_llm_with_tools()` now automatically get `web_search` and `spider_query` in their tool schemas (no per-agent imports needed). All 64 agents with tool handlers fall through to BaseAgent for centralized handling. Zero `except NotImplementedError` blocks remain. Zero redundant delegate_to_specialist blocks remain. Zero agents bypass shared tool injection via direct API calls.
