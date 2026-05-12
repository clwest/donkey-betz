<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`../PLATFORM_WHAT_IT_IS.md`](/docs/PLATFORM_WHAT_IT_IS.md). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality (Session 1099 verifier).

# Agent System

83 agents in AGENT_MAP, with DB persona rows available via DynamicPersonaAgent fallback, routed deterministically via dictionary lookup with automatic tool call recording and provenance tracking. Session 1000: 4 Intelligence Desks defined; Session 1115 confirmed **all 4 desks are on-demand only** via `POST /api/home/trigger-desks/` (the previously-claimed daily `run_market_intelligence_desk` PeriodicTask was removed in commit `a88fb8e7` "minimal beat schedule" cleanup, but this doc lagged until Session 1115). Session 1029: Agent health audit — 35 thriving, 6 bounded, 3 waste paths closed. Session 1034: RAG user documents wired into all AGENT_MAP agents, media task guard blocks non-generative tasks.

## Agent Categories (83 in AGENT_MAP)

| Category | Count | Agents |
|----------|-------|--------|
| Creation | 4 | ImageAgent, VideoAgent, AudioAgent, ThreeDAgent |
| Editing | 2 | ImageEditingAgent, VideoEditingAgent |
| Research | 2 | ResearchAgent, PlatformAuditAgent |
| Strategy | 4 | ContentStrategyAgent, BrandIdentityAgent, SEOOptimizerAgent, SocialMediaAgent |
| Executive | 4 | CTOAgent, COOAgent, CreativeDirectorAgent, MeetingCoordinatorAgent |
| Analysis | 3 | TrendAnalysisAgent, OpportunityScoringAgent, MarketIntelligenceAgent |
| Stock | 9 | StockAuditCoordinator, BullCaseAgent, BearCaseAgent, MarketMovementMonitor, InstitutionalWatcher, MarketAnomalyDetector, SignalScanner, MarketIntelligenceCoordinator, StockAnalystAgent |
| Blockchain | 5 | BlockchainAuditCoordinator, SmartContractAuditor, TransactionMonitor, WhaleWatcher, ExploitDetector |
| Content | 6 | ContentWriterAgent, EditorAgent, TopicMinerAgent, ContrarianAgent, PerformanceAnalystAgent, VoiceCriticAgent |
| Orchestration | 6 | AISeriesWorkflowAgent, AutonomousContentStudioCoordinator, ContentDiversityOrchestrator, ResolveAgent, WorkflowAgent, CampaignOrchestrator |
| Podcast | 4 | PodcastCoordinatorAgent, DebateAdvocateAgent, DebateSkepticAgent, ModeratorAgent |
| Narrative | 4 | NarrativeDriftCoordinator, NarrativeHistorianAgent, TrendBreakDetector, CulturalImpactAgent |
| Markets | 7 | PredictionMarketAnalyst, SportsOddsAnalyst, ArbitrageDetector, GamePredictor, LineMovementAnalyzer, SharpActionDetector (Session 1012: structured recs), BookmakerAgent |
| Development | 5 | CodeGeneratorAgent, FullStackDeveloperAgent, CodeReviewAgent, DevOpsAgent, PromptEngineeringAgent |
| Legal | 1 | LegalDocDrafterAgent |
| Training | 2 | CharacterTrainingAgent, TrainedCreationAgent |
| Security | 2 | MemoryIsolationAgent, ContentAuditAgent |
| Business Research | 4 | CompetitorAnalysisAgent, CustomerResearchAgent, BrandStrategyAgent, MarketingStrategyAgent |
| System | 3 | SystemIntelligenceAgent, DecisionEnforcerAgent (Session 1000), PersonalAssistantAgent |
| Utility | 5 | OpportunityPipelineAgent, ContentExecutorAgent, WorkflowOrchestrationAgent, ThinkingAgent, TechnicalDocumentAgent |

**54 routable** (can be invoked directly) | **25 non-routable** (sub-agents/coordinators) | **26 provenance-tracked**

## Intelligence Desks (Session 1000 — on-demand only, refreshed Session 1115)

4 desk coordinators are **defined**. All four are **on-demand only** — none are scheduled.

| Desk | Coordinator | Agents Activated | Schedule (verified Session 1115) |
|------|------------|-----------------|---|
| Stocks | MarketIntelligenceCoordinator | 9 agents (bull/bear/audit/monitor/anomaly/scanner) | **On-demand only** (no PeriodicTask — `run_market_intelligence_desk` task fn at `core/tasks.py:4356` still exists; can be re-scheduled if needed) |
| Sports | SportsBettingCoordinator | 5 agents (predictor/odds/arbitrage/line/sharp) | **On-demand only** (no PeriodicTask) |
| Blockchain | BlockchainAuditCoordinator | 5 agents (contract/transaction/whale/exploit) | **On-demand only** (no PeriodicTask) |
| Narrative | NarrativeDriftCoordinator | 4 agents (historian/trend/cultural) | **On-demand only** (no PeriodicTask) |

> Both the individual-desk tasks (`run_market_intelligence_desk`,
> `run_sports_intelligence_desk`, etc.) and the wrapper
> `run_all_desks_intelligence` exist as Celery task functions but **none
> are registered as a beat schedule** (verified Session 1115 audit, after
> the Session 1000-era `run_market_intelligence_desk` daily schedule was
> removed in commit `a88fb8e7`). "Run All Desks" in the UI invokes the
> wrapper on-demand via `POST /api/home/trigger-desks/`. To resume
> automated runs, add a PeriodicTask for the desk(s) of interest in
> `core/celery.py`.

API: `GET /api/home/intelligence-desks/`, `POST /api/home/trigger-desks/`
Cache keys: `desk:{stocks|sports|blockchain|narrative}:latest`

## Routing (core/agent_router.py)

Deterministic dictionary lookup — no LLM involved in routing:
1. `AGENT_MAP` maps agent name strings to classes
2. Router receives `agent_name` + `task` + `context`
3. Validates agent exists, instantiates fresh per request
4. Injects context layers (12 types), executes, returns `AgentResult`

**Optional semantic routing:** Embeddings-based for natural language queries (cosine similarity threshold 0.35, falls back to keyword matching).

## Context Injection (12 Layers)

Every agent receives contextual data before execution:
1. **scifi_context** — Platform state
2. **spider_context** — Real-time spider data
3. **learning_context** — Past learning patterns
4. **advisor_context** — 25 legendary advisor wisdom
5. **feedback_context** — Performance metrics + PA content review history
6. **knowledge_context** — Existing knowledge (check before external queries)
7. **workspace_context** — File operations awareness
8. **docs_context** — Documentation/session awareness
9. **user_context** — Personalized user data (skills, goals, preferences)
10. **risk_context** — Critical docs, incidents, audit findings
11. **platform_tools_directive** — "Use internal tools, not external services" prompt from `PlatformIntegration` (Session 992)
12. **user_docs_context** — User-uploaded documents via RAG (Session 1034): pgvector cosine search on `DocumentEmbedding`, threshold 0.45, top 5 chunks. Only runs when `self.user` is set. Injected into `_build_intelligent_prompt()` as "YOUR UPLOADED DOCUMENTS".

`feedback_context` now includes `pa_review_feedback` (last 5 PA publish/archive/revise decisions) and `pa_review_summary`, extracted into `spider_context['pa_content_feedback']` and `spider_context['pa_review_summary']` by `gather_context()` (Session 990).

`AgentLearningService` (`core/services/agent_learning_service.py`) records every `route()` execution via `record_interaction()` and builds per-user, per-agent preference models in Redis. `_get_user_context()` injects the adaptive context string into `user_context['agent_learned_preferences']`, which `gather_context()` surfaces into `spider_context['agent_learned_preferences']` (Session 991).

Context can be pre-gathered before timeout starts via `gather_context()` + `pre_gathered_context` param.

## Shared Tools & Delegation (Sessions 1002B-1002C)

Every agent automatically receives 3 shared tools in its LLM tool schema via `BaseAgent`:

| Tool | Handler | Purpose |
|------|---------|---------|
| `web_search` | `BaseAgent._execute_tool_call()` | Real-time web search via Tavily |
| `spider_query` | `BaseAgent._execute_tool_call()` | Query SpiderData via `SpiderIntelligenceService` |
| `delegate_to_specialist` | `BaseAgent._execute_tool_call()` | Route sub-tasks to discoverable agents |

**Injection paths:**
- `_call_openai()` / `_call_llm_with_tools()` — automatic via `_get_tools_with_shared()`
- Direct `client.chat.completions.create()` calls — use `self.get_tools_with_delegation()`

**Tool handler chain:** Agent's `_execute_tool_call()` handles own tools, then `super()._execute_tool_call()` handles shared tools. 64 agents wired. 4 programmatic agents intentionally skipped (content_executor, opportunity_pipeline, workflow_orchestration, workflow_agent).

## ToolCallRecord (Session 970)

Automatic audit trail for all agents via `__init_subclass__()` in `BaseAgent`:
- Wraps `_execute_tool_call()` in every subclass automatically
- Records: tool_name, arguments, result, latency_ms, success, error_message
- Zero agent files changed — the wrapper is inherited
- Never breaks agent execution (wrapped in try/except)

## Provenance Tracking (Session 953)

26 data-driven agents include `provenance`, `publishable`, and `validation_status` in output:

| Group | Agents | Staleness Window |
|-------|--------|------------------|
| Stock (8) | BullCase, BearCase, MarketIntelligenceCoordinator, StockAuditCoordinator, MarketAnomalyDetector, SignalScanner, InstitutionalWatcher, MarketMovementMonitor | 24h |
| Blockchain (5) | BlockchainAuditCoordinator, WhaleWatcher, TransactionMonitor, ExploitDetector, SmartContractAuditor | 4h |
| Analysis (3) | TrendAnalysis, MarketIntelligence, OpportunityScoring | 24h |
| Standalone (2) | BookmakerAgent (2h), CreationAgent (24h) | varies |

Provenance fields: `generated_at`, `inputs_used`, `freshness_window`, `publishable`, `validation_status`.

## Agent Health Classification (Sessions 1029, 1032-1033)

Every agent is classified by its ability to fulfill its mission:

| Classification | Count | Criteria |
|---------------|-------|----------|
| Thriving | 35 | >80% success rate, producing deliverables |
| Struggling | 6 | 30-80% success, need bounded tasks or data |
| Wasting | 3 | Running with no useful output (paths now closed) |

### 79-Agent Stress Test (Session 1032)

Comprehensive end-to-end test of all routable agents: **73 PASS, 6 FAIL (92.4% pass rate)**. Each agent tested with realistic task + context. Failures were all pre-existing issues (missing API keys, external service quotas), not code bugs.

### EditorAgent LLM Fix (Session 1033, PR #1308)

EditorAgent's `_enhance_with_llm()` referenced nonexistent `core.services.llm_service`. Fixed to use `LLMProviderRegistry` + `LLMRequest` from `core.services.llm_provider_registry`. Now successfully enhances blogs via OpenAI gpt-4o-mini (~18s per blog).

### Waste Agents Removed (Sessions 1027, 1029)

| Agent | Issue | Fix |
|-------|-------|-----|
| CodeGeneratorAgent | No codebase access on Railway, sandbox-only output | Removed from ALL 6 dispatch paths (PRs #1273, #1283, #1285) |
| AudioAgent | ElevenLabs quota exceeded, 0% success | Removed from ALL dispatch paths + podcast TTS disabled (PRs #1273, #1283, #1285) |
| OpportunityScoringAgent | No revenue loop, `zero_revenue_7d` trigger spawned 62+ runs/day | Trigger disabled (PR #1284) |

### Bounded Task Pattern (Session 1029)

Unbounded tasks cause 45-min timeouts and LLM reinterpretation. Bounded tasks complete in seconds:

| Pattern | Example | Result |
|---------|---------|--------|
| Unbounded | "Analyze current market trends" | 45-min timeout, 0% success |
| Bounded | "Top 3 trends, 500 words, do NOT delegate" | Completes in seconds, ~80% success |

Rules for bounded tasks:
- Specify scope (top N items)
- Set length limit (under X words)
- Add "do NOT delegate/spawn sub-tasks"
- Add "if no data exists, report 'no data available'"

### Data-Starved Agents

CompetitorAnalysisAgent and CustomerResearchAgent evidence gates correctly block hallucination, but no competitive intelligence or customer data exists in the spider network. Need spiders configured to collect competitor and customer signals.

## AutoSpawnerService

"Missing reflex" — auto-spawns agents/spiders when data is insufficient:
- Checks data count against configurable thresholds (e.g., job_listings: 100 min, 1000 optimal)
- Staleness detection (e.g., 48h for job data)
- Spawns spiders via `run_spider_with_priority.delay()` and agents via `queue_agent_task.delay()`
- Decorator: `@ensure_sufficient_data('job_listings', extractor_fn, threshold)`

## Agent Voice (Session 926)

12 ElevenLabs voices mapped to agent categories:
- Rachel (Research/Analysis), Antoni (Financial), Bella (Content/Creative), Daniel (Development), George (Executive), Domi (Blockchain), Sam (Sports), Charlotte (Legal), Emily (Marketing), Callum (Strategy), Matilda (Health), Elli (Support)

Assignment: explicit voice_id → keyword matching → category matching → default Rachel.

## CodeArtifact Capture (Session 1012)

When `CodeGeneratorAgent._write_file()` or `_edit_file()` fails due to workspace unavailability (no manager, no workspace, no write permission, or write operation failure), the code output is captured as a `CodeArtifact` record instead of being silently lost. This is critical on Railway where no writable workspace exists.

- **Model:** `CodeArtifact` (`core.models_code_artifacts`) — kind (file_create/file_edit/patch), status (pending/approved/rejected/applied/stale), target_path, content, content_before
- **API:** `GET /api/code-artifacts/` (list, filterable by status/agent_name/initiative/kind), `POST .../approve/`, `POST .../reject/`
- **NOT captured:** File-not-found and old_text-not-found errors (logic errors, not workspace issues)
- **Return dict:** Failed writes include `artifact_id` and `artifact_captured: True` so the agent's tool loop knows the code was saved

## Executive Function (Session 872)

- **DecisionEnforcerAgent** ("Prefrontal Cortex"): Forces decisions after debate, forbids hedging
- **Contracts:** ResearchContract, ExecutionMandate, SynthesisContract prevent vague outputs
- **Prompt sharpening:** Transforms hedging language → decisive language

## Agent Knowledge & Conversations (Session 988)

**Knowledge freshness:** `_get_agent_knowledge()` in `ConversationOrchestrator` filters `AgentKnowledgeSource` and `AgentMemory` to 14-day window. Prevents agents grounding on stale records (e.g., "Oct 2023 Notion articles").

**DATA GROUNDING REQUIREMENT:** Turn prompts inject current month/year and explicitly ban:
- "Notion spider", "Notion data", data collection dates, dataset sizes
- Citing dates older than 30 days as evidence
- Any reference to 2023 or 2024 data

**Conversation records:** Multi-agent conversations write to `DeliberationSession` (not `AgentExecution`). The PA execution_history tool queries both sources.

**Dynamic team selection:** `_select_agents_for_topic()` in `ConversationOrchestrator` tries `DynamicTeamBuilder` first (embedding similarity + synergy scoring), falling back to `AgentRegistry` text matching on failure (Session 992).
