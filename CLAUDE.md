# CLAUDE - AI Session Entry Point

**Last Updated:** February 12, 2026 - Session 996

## Quick Start

```bash
# 1. Read current context (MANDATORY)
cat 00-START-NEXT-SESSION.md

# 2. Start platform
make start && make celery

# 3. Access AI Studio
open http://localhost:8000/ai-studio/
```

## System Stats

| Component | Count | Details |
|-----------|-------|---------|
| **Agents** | 79 | 52 routable, 25 non-routable, 26 provenance-tracked |
| **Spiders** | 79 | 74 working, 5 need API keys |
| **PA Tools** | 97 | 38 intents, 53 tool handlers, 8 enrichment services |
| **LLM Providers** | 6 | OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini |
| **Database Models** | 386+ | PostgreSQL + pgvector |
| **Celery Tasks** | 264 | 7 workers, dedicated PA queue |
| **Services** | 134 | Signal aggregation, content deliberation, auto-spawning |
| **Body Systems** | 9 | HEART, LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR, BRAIN, SKIN |
| **Advisors** | 25 | Famous figures + domain experts |
| **Frontend** | 2,253 KB | 9 workspace tabs, 36 routes |

## Project Structure

### Key Directories
- `core/agents/` - 76 agents with learning hooks
- `core/services/` - 134 service classes
- `ai_core/spiders/` - 77 spiders
- `docs/topics/` - Embedding-optimized subsystem docs (current state)
- `docs/handoffs/` - 600 session handoff documents (build history)

### Key Files
| File | Purpose |
|------|---------|
| `00-START-NEXT-SESSION.md` | Current session priorities |
| `core/agent_router.py` | Deterministic agent routing |
| `core/tasks.py` | Celery background tasks |
| `core/conversation_orchestrator.py` | Multi-agent conversations |
| `core/services/unified_pa_entrypoint.py` | PA: 35 intents, enrichment pipeline |
| `core/services/tool_dispatcher.py` | PA: 50 tool handlers |
| `core/services/signal_aggregation_service.py` | Signal clustering & auto-topic generation |
| `core/services/content_deliberation_runner.py` | v2 content pipeline |
| `frontend/src/pages/WorkspacePageNew.tsx` | 9-tab modular workspace |
| `frontend/src/pages/CommandCenterPage.tsx` | Command Center with PA chat |

## Subsystem Documentation

Detailed current-state docs for each subsystem (designed for embedding):

| Topic File | Covers |
|------------|--------|
| [docs/topics/personal-assistant.md](docs/topics/personal-assistant.md) | PA intent routing, 50 tools, enrichment, async flow |
| [docs/topics/content-pipeline.md](docs/topics/content-pipeline.md) | ClaimsPack, deliberation, reviewers, PublishGate |
| [docs/topics/agent-system.md](docs/topics/agent-system.md) | 76 agents, routing, ToolCallRecord, provenance |
| [docs/topics/initiative-pipeline.md](docs/topics/initiative-pipeline.md) | Dreams, 5-stage pipeline, signals, action items |
| [docs/topics/celery-workers.md](docs/topics/celery-workers.md) | 7 workers, queues, memory management, observability |
| [docs/topics/body-systems.md](docs/topics/body-systems.md) | 9 health systems, coordinator, scoring |
| [docs/topics/spider-network.md](docs/topics/spider-network.md) | 77 spiders, data types, signal aggregation |
| [docs/topics/stock-intelligence.md](docs/topics/stock-intelligence.md) | Dashboard, briefs, alerts, predictions |
| [docs/topics/frontend.md](docs/topics/frontend.md) | 9 workspace tabs, PA integration, telemetry |
| [docs/topics/infrastructure.md](docs/topics/infrastructure.md) | Django, Railway, Redis, PostgreSQL |

## GPT-5-mini Configuration

```python
# CORRECT - Reasoning model has different parameters
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=messages,
    max_completion_tokens=6000  # NOT max_tokens, NO temperature
)
```

## Troubleshooting

```bash
# Full restart
pkill -f daphne; pkill -f redis; pkill -f celery
rm -f .daphne.pid .celery.pid .celery-beat.pid
make start && make celery

# macOS Celery SIGSEGV fix
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES celery -A core worker -l INFO --pool=solo
```

## Reference Documentation

| Doc | Purpose |
|-----|---------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture |
| [AGENTS.md](docs/AGENTS.md) | Agent documentation |
| [SPIDERS.md](docs/SPIDERS.md) | Spider network |
| [SERVICES.md](docs/SERVICES.md) | Services layer |
| [DATABASE_MODEL_REFERENCE.md](docs/DATABASE_MODEL_REFERENCE.md) | Which DB table for what |
| [API_PATH_POLICY.md](docs/API_PATH_POLICY.md) | API path conventions |
| [DREAM_INITIATIVE_WORKFLOW.md](docs/DREAM_INITIATIVE_WORKFLOW.md) | Initiative 5-stage pipeline |
| [DISCORD_INTEGRATION.md](docs/DISCORD_INTEGRATION.md) | Discord bot: 112 commands |

**Documentation Index:** Run `python manage.py build_docs_index` to regenerate `docs/INDEX.md`

---

**Always read `00-START-NEXT-SESSION.md` first - it has the current priorities!**
