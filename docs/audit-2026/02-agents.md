# Dossier #2: Agent System

**Audited:** April 6, 2026
**Status:** WORKING (token-conservation mode — scheduled runs disabled, on-demand works)

---

## 1. Purpose

The Agent System is an autonomous multi-agent orchestration platform where 84 code-defined agents + ~139 database-defined persona agents execute specialized tasks (content creation, research, market analysis, code generation, legal drafting, etc.) with personalized context injection, learned knowledge retrieval, and cross-agent knowledge sharing.

## 2. Runtime Evidence

- **84 agents** in AGENT_MAP (`core/agent_router.py:279-425`)
- **~139 DB persona agents** via DynamicPersonaAgent fallback
- **AgentExecution** records in DB track every run with status, tokens, cost
- **AgentMemory** records persist learnings with safety classification
- **AgentKnowledgeSource** records enable cross-agent knowledge sharing
- **ToolCallRecord** audit trail for every tool invocation

## 3. Entry Points

| Trigger | Path | Example |
|---------|------|---------|
| **PA chat** | User message → PA routes to agent | "Research AI trends" → ResearchAgent |
| **Celery Beat** | Scheduled agent rotation tasks | `run_content_research_agents` (disabled for token conservation) |
| **API endpoint** | `POST /api/agents/run/` | Direct agent invocation |
| **Workflow delegation** | WorkflowAgent delegates to specialists | Multi-step tasks |
| **Initiative pipeline** | Stage completion triggers next agent | Initiative stage documents |
| **ConceptForge** | Pipeline stages invoke specific agents | 6-stage analysis |

## 4. Execution Chain

```
AgentRouter.route(agent_name, task, context)
  │
  ├─ 1. Validate context, check AgentControlEntry (blocked?)
  ├─ 2. Lookup agent: AGENT_MAP[name] or DynamicPersonaAgent fallback
  ├─ 3. Parallel context gathering (11 workers, 10s timeout each):
  │     scifi_context, spider_context, learning_context,
  │     advisor_context, feedback_context, knowledge_context,
  │     workspace_context, docs_context, user_context,
  │     risk_context, user_docs_context
  ├─ 4. Instantiate agent, inject workspace_id
  ├─ 5. agent.execute(task, context, scifi_context, spider_context)
  │     │
  │     ├─ _build_prompt() — assembles 7-layer prompt:
  │     │   1. Sharpened system prompt (removes hedging language)
  │     │   2. Relevant knowledge (semantic search + keyword fallback)
  │     │   3. Policy context (up to 3 policies)
  │     │   4. System learnings (from LearningLoopOrchestrator)
  │     │   5. Mood modifiers (behavioral directives)
  │     │   6. Evolution context (authority level affects tone)
  │     │   7. Spider intelligence (real-time data)
  │     │
  │     ├─ _call_openai() — GPT-5-mini, 6000 max_completion_tokens
  │     │   └─ Tool call loop: execute tools until finish_reason != tool_calls
  │     │       ├─ delegate_to_specialist → recursive AgentRouter.route()
  │     │       ├─ web_search → WebSearchTool
  │     │       ├─ spider_query → SpiderIntelligenceService
  │     │       └─ agent-specific tools (subclass override)
  │     │
  │     ├─ Post-execution:
  │     │   ├─ _record_learning_outcome() → AgentLearning + XP
  │     │   ├─ _create_execution_memory() → AgentMemory (safety-classified)
  │     │   └─ _share_knowledge() → AgentKnowledgeSource
  │     │
  │     └─ Return AgentResult(success, message, data, tokens, cost)
  │
  ├─ 6. Record AgentExecution (status, tokens, cost, trace_id)
  ├─ 7. Create Deliverable if scheduled run
  └─ 8. Return result
```

Key files:
- `core/agent_router.py:738-1264` — routing + context gathering
- `core/agents/base_agent.py:317-5154` — 5,154-line base class
- `core/agent_context_middleware.py:18-420` — user context building
- `core/super_platform/prompt_builder.py:40-170` — prompt assembly
- `core/agents/dynamic_persona_agent.py` — DB-backed persona system

## 5. Data Contracts

| Model | Purpose | Key Fields |
|-------|---------|------------|
| Agent | Agent registry | name, agent_type, capabilities, xp, effectiveness_score |
| AgentExecution | Run tracking | agent(FK), status, tokens_used, cost, trace_id |
| AgentMemory | Learned memories | agent(FK), content, memory_type, safety_class, embedding, poison_risk_score |
| AgentKnowledgeSource | Shared knowledge | agent(FK), knowledge_type, title, summary, confidence_score |
| ToolCallRecord | Tool audit trail | agent_name, tool_name, input, output, latency_ms |
| AgentControlEntry | Block/enable agents | agent_name, is_enabled, reason |

## 6. External Dependencies

| Dependency | Purpose | Env Var |
|------------|---------|---------|
| OpenAI GPT-5-mini | Primary LLM for all agents | `OPENAI_API_KEY` |
| OpenAI text-embedding-3-small | Knowledge/memory embeddings | `OPENAI_API_KEY` |
| Stability AI | ImageAgent, ImageEditingAgent | `STABILITY_API_KEY` |
| Runway ML | VideoAgent, VideoEditingAgent | `RUNWAYML_API_KEY` |
| ElevenLabs | AudioAgent, TTS | `ELEVENLABS_API_KEY` |
| Replicate | CharacterTrainingAgent (FLUX LoRA) | `REPLICATE_API_TOKEN` |

## 7. Outputs/Artifacts

What agents produce that users see:
- **Deliverables** — documents, reports, strategies, plans in workspace tabs
- **Images** — generated via Stability AI, stored in ImageHistory
- **Videos** — generated via Runway ML, stored in VideoHistory
- **Audio** — generated via ElevenLabs, stored in AudioHistory
- **Blog posts** — via ContentWriterAgent → SelfBlog model
- **Research briefs** — via ResearchAgent → SelfBlog (category=research_brief)
- **Initiative documents** — stage documents via TechnicalDocumentAgent

## 8. Failure Modes

| Failure | Cause | Impact | Mitigation |
|---------|-------|--------|------------|
| LLM timeout | OpenAI API slow | Agent returns empty result | Per-agent llm_timeout (60-180s) |
| Tool call loop | Agent calls tools indefinitely | Token burn, timeout | Max tool iterations, soft_time_limit |
| Context gathering timeout | One context source hangs | Reduced context quality | 10s per-call timeout, graceful degradation |
| Memory poisoning | Test content enters embeddings | Corrupted knowledge retrieval | safety_class classification (test_only/approved) |
| Blocked agent | AgentControlEntry | Task silently skipped | Logged, returns failure result |
| Duplicate dispatch | Same agent triggered twice | Wasted tokens | Dedup guard (10min cache lock) |

## 9. Current Status: WORKING (On-Demand)

**What works:**
- All 84 AGENT_MAP agents can be invoked on-demand via PA or API
- Context injection (11 sources) gathers in parallel
- Knowledge retrieval (semantic + keyword) operational
- Tool execution (web_search, spider_query, delegation) functional
- Learning loop records outcomes and memories
- Cost tracking per execution

**What's disabled (token conservation):**
- Scheduled agent rotation tasks (content, research, strategy, market, etc.)
- Dormant agent exercise
- Agent conversation triggers
- All category-based scheduled runs

**Blocked agents:**
- CodeGeneratorAgent — permanently blocked (no codebase access on Railway)

## Verified Data (April 6, 2026)

- **Total executions**: 2,384 across 73 unique agents (of 222 registered)
- **Last 30 days**: 0 executions (token conservation mode)
- **Top agents**: CodeGeneratorAgent (991 runs, 99.6% success), ResearchAgent (240, 94.2%), AutonomousContentStudioCoordinator (124, 91.1%), DevOpsAgent (108, 100%), TrendAnalysisAgent (103, 97.1%)
- **Agent effectiveness scores**: Real data — only 4.5% at default 85, distribution ranges 50-85 based on actual performance
- **149 agents have never executed** (registered but dormant)

## 10. Truth Gaps

- **Agent effectiveness scores**: All default to 85 — no real performance data driving these
- **Knowledge retrieval quality**: Semantic search exists but embedding coverage unknown — need to audit what % of AgentKnowledgeSource records have valid embeddings
- **Cross-agent learning impact**: _share_knowledge() writes records but unclear if agents actually retrieve and benefit from other agents' knowledge
- **Persona agent quality**: 139 DB personas use generic DynamicPersonaAgent — quality likely lower than dedicated code agents
- **Tool call success rate**: ToolCallRecord exists but no aggregate analysis done
- **Prompt composition cost**: 7-layer prompt may exceed context window for some agents — no monitoring
- **LLM model routing**: AgentLLMRouter exists (Session 697) but unclear if any agents actually use non-OpenAI models
- **Evolution system**: XP and levels exist but unclear if authority level actually changes agent behavior in practice
