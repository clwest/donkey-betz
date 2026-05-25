<!-- DOC-POINTER-V1 (Session 1147) -->
> **Topic-folder entry point — refresh-in-place; do not move.**
> The topic files in this directory describe the *current state* of each subsystem (embedding-optimized, no temporal noise). Hardcoded counts in this folder may drift from runtime — for verified numbers always check [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) (sole counts source per `DOC_LIFECYCLE.md` §2c) and [`docs/canon/INDEX.md`](../canon/INDEX.md) (canon registry incl. the Runtime Evidence family added Session 1146).
> **Last reviewed for drift labeling:** Session 1147 (2026-05-25)

# Topic Files — Embedding-Optimized

These files describe the **current state** of each subsystem. They are designed for RAG embedding and retrieval — each file is self-contained, uses the correct current terminology, and avoids temporal/historical noise.

**For build history**, see `docs/handoffs/` (handoff documents).

**Where current truth lives** (per `DOC_LIFECYCLE.md` §2c): platform counts come from `docs/PLATFORM_INVENTORY.md`; doc-corpus counts from `docs/INDEX.md`; per-subsystem runtime evidence from the 8 `docs/*_AUDIT.md` autogen files (canon-registered Session 1146). Use those when verifying anything count-shaped; this folder's prose is for understanding *what the subsystems do*, not *how many of them there are right now*.

## Files

| File | Subsystem | Key Classes/Files |
|------|-----------|-------------------|
| [personal-assistant.md](personal-assistant.md) | PA routing, tools, enrichment, async | UnifiedPAEntrypoint, ToolDispatcher |
| [content-pipeline.md](content-pipeline.md) | Blog generation, deliberation, quality gating | ContentDeliberationRunner, ClaimsPackBuilder, PublishGate |
| [agent-system.md](agent-system.md) | Agents, routing, provenance, voice (count: see PLATFORM_INVENTORY) | AgentRouter, BaseAgent, AutoSpawnerService |
| [initiative-pipeline.md](initiative-pipeline.md) | Dreams, initiatives, stages, signals | Initiative, SignalAggregationService |
| [celery-workers.md](celery-workers.md) | Task queue, workers, observability | CeleryTaskEvent, process_pa_chat_task |
| [body-systems.md](body-systems.md) | Health monitoring systems (count: see PLATFORM_INVENTORY) | BodyCoordinator, HeartBeat, ComponentStatus |
| [spider-network.md](spider-network.md) | Spiders, data types, signal aggregation (count: see PLATFORM_INVENTORY) | SpiderData, SignalCluster, AutoTopic |
| [stock-intelligence.md](stock-intelligence.md) | Stock dashboard, briefs, alerts, predictions | MarketIntelligenceBrief, StockMarketAlert |
| [frontend.md](frontend.md) | React UI, workspace tabs, PA integration | WorkspacePageNew, GlobalPADock |
| [infrastructure.md](infrastructure.md) | Django, Railway, Redis, PostgreSQL | core.settings, Procfile |
| [active-module-ownership-map.md](active-module-ownership-map.md) | Active-but-underdocumented modules with confusing look-alikes (Session 1114, PR-D from Session 1111) | RevenueRealityVerifier, AdvisorRegistry, llm/ vs agent_llm_router, core.tasks_*.py indirection, urls.py vs urls_unified.py |

## Embedding Strategy

**Embed these topic files** — they describe current state, produce coherent retrieval results.

**Also embed reference docs:** ARCHITECTURE.md, AGENTS.md, SERVICES.md, WIREMAP.md, DATABASE_MODEL_REFERENCE.md, AUTONOMOUS_SYSTEMS.md

**Do NOT embed session handoffs** — they are temporal, overlapping, and contradictory across versions. They confuse retrieval.
