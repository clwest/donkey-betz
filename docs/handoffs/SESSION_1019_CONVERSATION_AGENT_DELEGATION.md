---
originating_session: 1019
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1019 - Conversation Agent Delegation

**Date:** February 16, 2026
**PRs:** #1244, #1245

## Problem

Agent conversations (`run_agent_conversation` and `run_multi_agent_conversation` in `core/tasks.py`) generate messages via direct LLM calls **without tools**. When a topic references another agent (e.g. "Scan competitor activity using ResearchAgent"), the participating agents spent all their turns saying "we can't do this without data" because they literally could not invoke the referenced agent. This was observed 3 times for the same topic, producing zero-value conversations each time.

## Solution: Hybrid Pre-gather + Mid-conversation Delegation

### Part A: Pre-flight Agent Data Gathering (PR #1244)

Added `_preflight_gather_agent_data(topic, participant_names)` utility function:

1. **Detection**: Scans topic string for agent name references using `AgentRouter.AGENT_MAP.keys()`. Checks both full names (e.g. "ResearchAgent") and base names (e.g. "research" if len > 3).
2. **Filtering**: Skips agents that are already conversation participants. Caps at 2 invocations max.
3. **Invocation**: Gets `system_autonomous` user, creates `AgentRouter`, calls `router.route(agent_name, topic)` directly.
4. **Injection**: Formats results as `== PRE-GATHERED DATA from {name} ==` blocks (max 2000 chars each). Injects into system prompts alongside existing spider/mood/policy context.
5. **Failure handling**: Failed/empty agents get a `=== NO UPSTREAM DATA AVAILABLE ===` block to prevent hallucination.

Called in both `run_agent_conversation` (after template selection) and `run_multi_agent_conversation` (same location).

### Part B: Mid-conversation Delegation (PR #1244)

Added `CONVERSATION_DELEGATION_TOOL` constant and `_handle_conversation_delegation()` handler:

1. **Tool schema**: Minimal `delegate_to_specialist` tool with `specialist_agent` and `task` parameters.
2. **Conditional offering**: Tool offered only when:
   - No delegation has been used yet this conversation
   - First 1-2 turns (msg_num < 2 for 2-agent, round_num == 0 for multi-agent)
   - Pre-flight didn't already invoke agents (avoids double-invocation)
   - `delegation_user` (system_autonomous) exists
3. **Handling**: On tool call, executes via `AgentRouter.route()`, then re-prompts same speaker with delegation results appended to system prompt (NO tools on re-prompt).
4. **Claude fallback**: NOT modified -- too fragile during rate-limit recovery. Preflight context is still available.

### ThreadPoolExecutor Fix (PR #1245)

Initial implementation used `ThreadPoolExecutor` for timeout isolation. This broke Django DB connections in child threads -- `router.route()` completed successfully but results were lost. Fixed by switching to direct calls. Timeout is already handled by AgentRouter/OpenAI API internally (120s).

## Files Modified

| File | Changes |
|------|---------|
| `core/tasks.py` | +307 lines: `_preflight_gather_agent_data()`, `CONVERSATION_DELEGATION_TOOL`, `_handle_conversation_delegation()`, modified both conversation functions |

## Verification on Railway

```
=== PREFLIGHT TEST ===
Invoked agents: ['ResearchAgent']
Failed agents: []
Context length: 2073 chars
```

ResearchAgent successfully invoked and returned substantive data when topic referenced it.

## Cost / Latency Budget

- **Part A**: Max 2 agent invocations per conversation. Only triggers when agent names detected in topic (most conversations skip). ~15-20s per invocation.
- **Part B**: 1 delegation + 1 re-prompt LLM call. Only triggers when LLM chooses to delegate on first turn.
- **Total additional cost**: ~$0.02-0.10 per conversation that triggers. Most conversations cost $0 extra.

## Key Gotcha

**Do NOT use ThreadPoolExecutor for Django ORM operations.** Child threads get separate DB connections that don't share state. Use direct calls or Celery subtasks instead.
