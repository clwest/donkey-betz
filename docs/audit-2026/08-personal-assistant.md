# Dossier #8: Personal Assistant (Rigby)

**Audited:** April 6, 2026
**Status:** WORKING — 103 tool schemas, 162 handlers, GPT-5.2 function calling live

---

## 1. Purpose

Rigby is the platform's primary user interface — a GPT-5.2-powered personal assistant with 103 tool schemas and 162 tool handlers that can execute any platform action. She detects intent from natural language, selects and executes tools, enriches responses with real-time intelligence, and maintains conversation context across sessions.

## 2. Runtime Evidence

- **6,993 lines** in unified_pa_entrypoint.py (core orchestration)
- **103 tool schemas** in pa_tool_schemas.py (OpenAI function calling format)
- **162 tool handlers** across 8 mixin categories in tool_dispatcher.py
- **7 enrichment services** fire per intent
- **ChatConversation** records persist history (20-turn window)
- **Celery PA queue** dedicated worker for non-blocking execution
- Verified working locally and on production

## 3. Entry Points

| Trigger | Endpoint | Flow |
|---------|----------|------|
| Web chat | `POST /api/pa/chat/` | → Celery PA task → poll `/api/pa/chat/status/<task_id>/` |
| Claude Code | `python tools/pa_chat.py "message"` | → Same API with `source='claude-code'` |
| Discord | Discord bot command | → Same pipeline, different source |
| API direct | Token auth + POST | → Same pipeline |

## 4. Execution Chain

```
User message arrives
  │
  ├─ 1. INTENT DETECTION (deterministic, no LLM)
  │     unified_pa_entrypoint.py:2169
  │     40+ keyword patterns with priorities:
  │       media creation → ownership → initiatives → dreams →
  │       boardroom → content review → decisions → activity → health
  │     155 intent aliases normalize to canonical forms
  │
  ├─ 2. ENRICHMENT PIPELINE (per intent)
  │     unified_pa_entrypoint.py:121-152
  │     Based on detected intent, fire 1-5 enrichers:
  │       PAIntelligenceEnricher → platform knowledge, trends
  │       BlogPerformanceContext → content metrics
  │       DomainContentContext → domain expertise (9 domains)
  │       SpiderContext → real-time spider data
  │       AdvisorContext → legendary advisor principles
  │       ProactiveIntelligence → anticipatory context
  │       PlatformBriefing → full system awareness
  │     Each capped at 1000-2000 chars
  │
  ├─ 3. TOOL SCHEMA SELECTION
  │     unified_pa_entrypoint.py:1105
  │     From 103 schemas, filter by:
  │       Message intent relevance
  │       User role/permissions (AssistantProfile)
  │       Schema version (live-reload)
  │
  ├─ 4. GPT-5.2 FUNCTION CALLING LOOP
  │     unified_pa_entrypoint.py:1100
  │     Max 8 iterations:
  │       Iteration 0-6: LLM with tools → execute tool calls → append results
  │       Iteration 7: LLM WITHOUT tools → force text summary
  │     Tool loop detection prevents infinite cycles
  │     Uses OpenAI Responses API previous_response_id for continuity
  │
  ├─ 5. TOOL EXECUTION
  │     tool_dispatcher.py:506
  │     For each tool call:
  │       Permission check → handler lookup → async execute →
  │       PII scrubbing → metrics recording → audit trail
  │     Returns ToolResult(ok, tool, latency_ms, error_code, result)
  │
  ├─ 6. RESULT FORMATTING
  │     unified_pa_entrypoint.py:3822
  │     Intent-specific formatting:
  │       Item numbering (#1, #2) instead of UUIDs
  │       Urgency levels, status badges inline
  │       Actionable hints ("Say 'approve this' to act")
  │
  └─ 7. ANALYTICAL RESPONSE
        unified_pa_entrypoint.py:3611
        Second LLM call with:
          Tool results + enrichment + intent directives
          16 intent-specific analysis rules
          "Provide 2-4 sentences of insight, not lists"
        Returns conversational response to user
```

## 5. Tool Categories (162 Handlers)

| Category | Handler Count | Examples |
|----------|--------------|---------|
| Creation Agents | 8 | image, video, audio, 3D, character training |
| Research & Analysis | 13 | web search, competitor, market intelligence |
| Strategy & Content | 8 | SEO, social media, content audit, editor |
| Executive & Orchestration | 7 | CTO, COO, campaigns, workflows |
| Stock & Markets | 9 | analyst, signal scanner, anomaly detector |
| Sports & Betting | 5 | game predictor, line movement, arbitrage |
| Blockchain | 5 | smart contract auditor, whale watcher |
| Content Studio | 7 | topic miner, contrarian, distribution |
| Gateway Tools | 11 | ops, work, content, deliverable, governance |
| Self-Awareness | 10+ | agent introspection, platform status |
| Body Systems | 4 | vitals, budget, alerts, cost telemetry |
| Intelligence | 3 | gates, pilots, reasoning engine |
| Memory | 2 | conversation, remember |
| Data Access | 5 | repo, analytics, discord, mobile |

## 6. Data Contracts

| Model | Purpose | Key Fields |
|-------|---------|------------|
| ChatConversation | Conversation history | user, conversation_id, messages(JSON), platform |
| AssistantProfile | Per-user PA config | user, allowed_tools, preferences |
| PAResponse | Execution result | trace_id, tool_runs, latency_ms, intent |
| ToolResult | Per-tool result | ok, tool, latency_ms, error_code, result |
| LLMCallLog | API call tracking | model, tokens, cost, agent_name |

## 7. External Dependencies

| Dependency | Purpose | Cost |
|------------|---------|------|
| OpenAI GPT-5.2 | Function calling + response generation | ~$0.003/1K input, $0.012/1K output |
| OpenAI Responses API | Conversation continuity via previous_response_id | Included |
| Redis | Tool metrics, rate limiting | Included |
| Celery PA queue | Async execution (non-blocking) | Included |

## 8. Failure Modes

| Failure | Cause | Impact | Mitigation |
|---------|-------|--------|------------|
| Tool loop | LLM calls same tool repeatedly | Token burn, timeout | Loop detection (signature tracking), max 8 iterations |
| PA queue blocked | Heavy task on PA worker | User waits indefinitely | Dedicated PA queue with 2 threads |
| Tool handler crash | Bad payload or DB error | Single tool fails | Structured error in ToolResult, other tools continue |
| Enrichment timeout | Slow enricher service | Degraded context | Per-enricher timeout, graceful skip |
| LLM timeout | OpenAI API slow | No response | Retry logic on first iteration, fallback summarization |
| History overflow | Long conversation | Token budget exceeded | 20-turn cap, 8000 char per assistant message |

## 9. Current Status: WORKING

**Fully operational:**
- 103 tool schemas registered and selectable
- 162 tool handlers dispatching across 8 mixin categories
- GPT-5.2 function calling loop (max 8 iterations)
- 7 enrichment services firing per intent
- Conversation history persisted (20-turn window)
- Dedicated Celery PA queue
- PII/secrets scrubbing on all results
- Tool metrics and audit trail

**Known limitations:**
- Some tool actions have mismatched enums between schemas and handlers (e.g., `publish` not valid for content_tool)
- Enrichment character caps may truncate important context
- Intent detection is keyword-based (no semantic understanding of ambiguous requests)

## 10. Truth Gaps

- **Tool coverage**: 103 schemas but 162 handlers — some handlers not exposed via schemas, some schemas may not have handlers
- **Tool success rates**: Metrics recorded in Redis but no dashboard or aggregate analysis
- **Enrichment effectiveness**: 7 enrichers fire but unclear if the added context improves response quality
- **Conversation memory quality**: 20-turn window may lose important context from earlier in long sessions
- **Schema-handler sync**: Schema enum values and handler action enums may drift — no automated validation
- **Cost per conversation**: LLMCallLog tracks per-call but no aggregate cost per conversation session
- **User satisfaction**: No feedback mechanism for PA response quality (no thumbs up/down)

## Key Patent Claims (Personal Assistant)

1. **Intent-driven tool orchestration** — deterministic intent detection selects from 103 tool schemas without LLM overhead
2. **Multi-iteration function calling loop** — up to 8 LLM iterations with tool execution, loop detection, and forced text summary on final iteration
3. **Per-intent enrichment pipeline** — 7 intelligence services selectively fire based on detected intent, enriching tool results with real-time spider data, advisor principles, and domain expertise
4. **162-handler tool dispatch** — single PA interface can execute any platform action (creation, analysis, governance, code execution, deployment)
5. **3-way collaborative chat** — user + PA + Claude Code developer in same conversation with role-aware response rules
6. **Analytical response synthesis** — second LLM pass with 16 intent-specific directives transforms raw tool results into conversational insights
