# Session 1068: Artifact Execution Fan-Out & Observability Fixes

**Date:** 2026-02-23
**PRs:** #1431, #1432, #1433, #1434

## What Was Done

### PA-Driven Failure Research

Used PA via Railway API to diagnose production failures (last 72 hours):
- **14 total errors**, 4 Celery task failures, 10 tool call failures
- **`execute_approved_artifacts`**: 4 consecutive `TimeLimitExceeded(660)` — the only recurring Celery failure
- **Agent timeouts**: 8 of top 10 agent failures were 45-minute cleanup kills
- **ResearchAgent**: 2 failures from `'str' object has no attribute 'get'`
- **WorkflowAgent**: 38.5% failure rate (5/13 in 24h), one failure had blank error message
- **2,299 pending approved artifacts** — all type `insight`, never clearing

### Deep Dive: 7-Day Timeout Breakdown

Queried Railway for full 7-day timeout data:
- **190 total agent timeouts** across 20+ agents
- TrendAnalysisAgent: 36 timeouts (28.1% failure rate)
- ContentWriterAgent: 34 timeouts (12.0%)
- WorkflowAgent: 20 timeouts (41.7%)
- CompetitorAnalysisAgent: 15 (3.2%)
- BearCaseAgent: 8 (21.1%)
- Root cause: open-ended insight artifact prompts causing agents to spiral into 45+ minute research sessions

### Deep Dive: 10 Failed Tool Calls

Queried ToolCallRecord for failure details:
- **4x TOOL_TIMEOUT (60s)**: `workflow_orchestration_agent` x2, `content_writer_agent` x2
- **3x Agent not found**: `universal_agent_tool` passed snake_case names, `strategic_review` mapped to non-existent `StrategyAgent`
- **2x External API**: VideoAgent `generate_video` returning 400
- **1x Redis connection**: `legal_doc_drafter_agent` couldn't connect to Redis

## Fixes

### 1. Fan-Out Artifact Execution — PR #1431

**Root cause:** `execute_approved_artifacts` processed 10 artifacts sequentially, each routing to an agent via `AgentRouter.route()`. Agents can take minutes (some timeout at 45 min), so the 660s hard limit killed the entire batch every single run.

**Fix:** Changed from sequential to fan-out pattern:
- `execute_approved_artifacts` is now a lightweight dispatcher (soft_time_limit=30s) that finds artifacts and dispatches each as its own subtask
- New `execute_single_artifact` subtask with 5min soft / 5.5min hard time limit — one slow agent can't block the batch
- SoftTimeLimitExceeded handler marks the running ArtifactExecution as failed with error message
- Routed new subtask to `long_running` queue

### 2. ResearchAgent `.get()` Guard — PR #1431

**Root cause:** `_execute_tool_call()` could theoretically return a non-dict, and the caller at line 658 called `.get('success')` without checking type.

**Fix:** Added `isinstance(tool_result, dict)` guard before `.get()` calls in both the main tool call loop and the fallback web_search path. Non-dict results are wrapped into `{'success': False, 'data': <original>, 'error': 'non-dict tool result'}`.

### 3. Blank Error Messages — PR #1432

**Root cause:** When `result.error` was empty string and `result.success == False`, the execution record stored `""` as `error_message`. Also `str(e)` on some exceptions can be empty.

**Fix:**
- Agent failures now fall back through `result.error → result.message → 'Agent returned failure with no error details'`, truncated to 2000 chars
- Exception handler records `f'{type(e).__name__}: (no message)'` when `str(e)` is empty

### 4. Tool Dispatch Fixes & Insight Artifact Scope — PR #1433

**Root cause (universal_agent_tool):** GPT passed snake_case tool names (e.g., `content_writer_agent`) as `agent_name` parameter. The handler looked them up verbatim and got "Agent not found".

**Root cause (strategic_review):** Mapped to `StrategyAgent` which doesn't exist in AGENT_MAP.

**Root cause (timeout epidemic):** Insight artifacts got open-ended prompts like "Execute: <title>" causing agents to spiral into research.

**Fixes:**
- `_handle_universal_agent` now resolves snake_case tool names via `_tool_to_agent_name()` before lookup
- `_handle_universal_agent` switched from `registry.execute_agent()` to `AgentRouter.route()` (the proven execution path)
- `strategic_review` remapped to `ContentStrategyAgent`
- Insight artifacts now get concise prompt: "Summarize this insight into 3 concrete next-steps (one sentence each). Do NOT do web research or tool calls."
- Batch limit raised from 10 to 25 (dispatcher is instant now)
- Dedup guard: excludes artifacts with `running` executions to prevent re-dispatch

### 5. Enhanced error_summary_tool — PR #1434

**Problem:** PA's `error_summary_tool` only showed aggregate counts — no detail on which agents timeout, which tool calls fail, or what the actual errors were.

**Fix:** Added 3 new sections to error_summary_tool output:
- **Agent timeout breakdown**: Top 10 agents by timeout count with failure rate percentages
- **Failed tool call details**: Individual ToolCallRecord rows with agent, tool, error type, error message, latency
- **Agent execution failure details**: Failed AgentExecution records with task description, error, timing
- Added `action` parameter to PA schema (default/detailed) — detailed mode always includes individual failure rows
- Hours >= 24 automatically includes detailed output

## Files Changed

| File | Change |
|------|--------|
| `core/services/artifact_execution.py` | Fan-out dispatcher, concise insight prompts, dedup guard for running executions |
| `core/tasks.py` | Reduced parent task time limit (30s), added `execute_single_artifact` subtask (5min), fixed blank error messages |
| `core/settings.py` | Added `execute_single_artifact` → `long_running` queue routing |
| `core/agents/research_agent.py` | Added `isinstance` guards on `_execute_tool_call` results |
| `core/celery.py` | Raised artifact batch limit from 10 to 25 |
| `core/services/tool_dispatcher.py` | Fixed `universal_agent_tool` snake_case resolution, `strategic_review` → `ContentStrategyAgent`, switched to `AgentRouter.route()`, enhanced `error_summary_tool` with timeout/failure detail sections |
| `core/services/pa_tool_schemas.py` | Enhanced `error_summary_tool` schema with `action` parameter |

## Remaining Items

1. **VideoAgent `generate_video` 400 errors** — external API issue, may need payload validation
2. **Redis connection failures** — intermittent, likely Railway Redis restarts
3. **WorkflowAgent 41.7% failure rate** — highest rate of any agent, needs deeper investigation into task types causing failures
4. **PA recommendation**: Governance "Failures" pane in frontend for real-time failure visibility

## Railway Auth

- PA API token for `Donkeyking` user: `<redacted-0cdc1c72-2026-04-20>`
- Endpoint: `POST /api/assistant/chat/` with `Authorization: Token <key>` and `Content-Type: application/json`
- Body: `{"message": "..."}`
