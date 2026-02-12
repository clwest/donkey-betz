# Agent System

76 agents organized by category, routed deterministically via dictionary lookup, with automatic tool call recording and provenance tracking.

## Agent Categories (76 Total)

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
| Markets | 3 | PredictionMarketAnalyst, SportsOddsAnalyst, ArbitrageDetector |
| Development | 5 | CodeGeneratorAgent, FullStackDeveloperAgent, CodeReviewAgent, DevOpsAgent, PromptEngineeringAgent |
| Legal | 1 | LegalDocDrafterAgent |
| Training | 2 | CharacterTrainingAgent, TrainedCreationAgent |
| Security | 2 | MemoryIsolationAgent, ContentAuditAgent |
| Business Research | 4 | CompetitorAnalysisAgent, CustomerResearchAgent, BrandStrategyAgent, MarketingStrategyAgent |
| System | 2 | SystemIntelligenceAgent, PersonalAssistantAgent |
| Utility | 5 | OpportunityPipelineAgent, ContentExecutorAgent, WorkflowOrchestrationAgent, ThinkingAgent, TechnicalDocumentAgent |

**49 routable** (can be invoked directly) | **25 non-routable** (sub-agents/coordinators) | **26 provenance-tracked**

## Routing (core/agent_router.py)

Deterministic dictionary lookup — no LLM involved in routing:
1. `AGENT_MAP` maps agent name strings to classes
2. Router receives `agent_name` + `task` + `context`
3. Validates agent exists, instantiates fresh per request
4. Injects context layers (10 types), executes, returns `AgentResult`

**Optional semantic routing:** Embeddings-based for natural language queries (cosine similarity threshold 0.35, falls back to keyword matching).

## Context Injection (10 Layers)

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

`feedback_context` now includes `pa_review_feedback` (last 5 PA publish/archive/revise decisions) and `pa_review_summary`, extracted into `spider_context['pa_content_feedback']` and `spider_context['pa_review_summary']` by `gather_context()` (Session 990).

Context can be pre-gathered before timeout starts via `gather_context()` + `pre_gathered_context` param.

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
