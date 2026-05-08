# Topic Files — Embedding-Optimized

These files describe the **current state** of each subsystem. They are designed for RAG embedding and retrieval — each file is self-contained, uses the correct current terminology, and avoids temporal/historical noise.

**For build history**, see `docs/handoffs/` (600 session handoff documents).

## Files

| File | Subsystem | Key Classes/Files |
|------|-----------|-------------------|
| [personal-assistant.md](personal-assistant.md) | PA routing, tools, enrichment, async | UnifiedPAEntrypoint, ToolDispatcher |
| [content-pipeline.md](content-pipeline.md) | Blog generation, deliberation, quality gating | ContentDeliberationRunner, ClaimsPackBuilder, PublishGate |
| [agent-system.md](agent-system.md) | 83 agents, routing, provenance, voice | AgentRouter, BaseAgent, AutoSpawnerService |
| [initiative-pipeline.md](initiative-pipeline.md) | Dreams, initiatives, stages, signals | Initiative, SignalAggregationService |
| [celery-workers.md](celery-workers.md) | Task queue, workers, observability | CeleryTaskEvent, process_pa_chat_task |
| [body-systems.md](body-systems.md) | 9 health monitoring systems | BodyCoordinator, HeartBeat, ComponentStatus |
| [spider-network.md](spider-network.md) | 80 spiders, data types, signal aggregation | SpiderData, SignalCluster, AutoTopic |
| [stock-intelligence.md](stock-intelligence.md) | Stock dashboard, briefs, alerts, predictions | MarketIntelligenceBrief, StockMarketAlert |
| [frontend.md](frontend.md) | React UI, workspace tabs, PA integration | WorkspacePageNew, GlobalPADock |
| [infrastructure.md](infrastructure.md) | Django, Railway, Redis, PostgreSQL | core.settings, Procfile |
| [active-module-ownership-map.md](active-module-ownership-map.md) | Active-but-underdocumented modules with confusing look-alikes (Session 1114, PR-D from Session 1111) | RevenueRealityVerifier, AdvisorRegistry, llm/ vs agent_llm_router, core.tasks_*.py indirection, urls.py vs urls_unified.py |

## Embedding Strategy

**Embed these topic files** — they describe current state, produce coherent retrieval results.

**Also embed reference docs:** ARCHITECTURE.md, AGENTS.md, SERVICES.md, WIREMAP.md, DATABASE_MODEL_REFERENCE.md, AUTONOMOUS_SYSTEMS.md

**Do NOT embed session handoffs** — they are temporal, overlapping, and contradictory across versions. They confuse retrieval.
