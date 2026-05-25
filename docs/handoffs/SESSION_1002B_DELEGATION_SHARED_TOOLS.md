---
originating_session: 1002
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1002B: Agent Delegation System Fix & Shared Tool Sets

**Date:** February 13, 2026
**Focus:** Fix under-utilization of 82-agent system through delegation and spider_query improvements

---

## Problem

Audit of all 82 agents revealed systemic under-utilization:

1. **AVAILABLE_SPECIALISTS** was a static list of only 13 agents -- the LLM's delegation tool description only mentioned 4 examples, so it couldn't discover the other 69 agents
2. **spider_query had no handler in BaseAgent** -- only 5 business agents handled it, and those called `service.search_intelligence()` which doesn't exist (should be `search_spider_data()`), meaning spider_query was silently failing for all business research agents
3. **No SPIDER_QUERY_TOOL at module level** -- `WEB_SEARCH_TOOL` existed as a shared constant but spider_query had to be manually defined per agent

## Changes

### 1. SPIDER_QUERY_TOOL constant (base_agent.py)

Added module-level constant matching existing `WEB_SEARCH_TOOL` pattern. Any agent can now include `SPIDER_QUERY_TOOL` in its tools list and get automatic handling from BaseAgent.

### 2. Dynamic AVAILABLE_SPECIALISTS (base_agent.py)

Replaced static 13-agent list with a `@property` that reads from `AgentRouter.AGENT_MAP` (cached 5 minutes). Now returns 81 agents (all except PersonalAssistantAgent). Falls back to the original 13-agent list if AgentRouter import fails.

### 3. Enhanced delegation tool description (base_agent.py)

Expanded description from a vague 4-example hint to a categorized overview of 82 agents across 8 categories (Research, Content, Media, Finance, Development, Business, Blockchain, Markets). This gives the LLM enough context to choose the right specialist.

### 4. spider_query handler in BaseAgent._execute_tool_call() (base_agent.py)

Added centralized spider_query handler matching the existing web_search pattern. Uses `SpiderIntelligenceService.search_spider_data()`. Any agent that includes SPIDER_QUERY_TOOL now gets working spider queries without custom handler code.

### 5. Fixed broken spider_query in BaseBusinessResearchAgent (base_business_research_agent.py)

Changed `service.search_intelligence()` (doesn't exist) to `service.search_spider_data()`. Fixed result extraction: was `results.get('results', [])` on a list return, now correctly handles the list return type.

## Files Changed

| File | Lines Changed | What |
|------|--------------|------|
| `core/agents/base_agent.py` | ~50 | SPIDER_QUERY_TOOL constant, dynamic AVAILABLE_SPECIALISTS, enhanced delegation description, spider_query handler |
| `core/agents/business/base_business_research_agent.py` | ~6 | Fixed broken search_intelligence() -> search_spider_data() |

## Verification

- Import check: `SPIDER_QUERY_TOOL` and `WEB_SEARCH_TOOL` both import cleanly
- Dynamic specialists: Returns 81 agents from AgentRouter.AGENT_MAP
- Delegation description: 666 chars with categories and "82-agent" reference

## Not Done (Deferred)

- Adding SPIDER_QUERY_TOOL to specific agents' tool lists (infrastructure first, then selective rollout)
- ContentWriterAgent delegation (uses direct OpenAI calls, not `_call_openai()`)
- Cost optimization / model routing
