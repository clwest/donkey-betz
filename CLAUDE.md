# CLAUDE - AI Session Entry Point

**Last Updated:** April 3, 2026

## Working with Rigby (PA)

Claude Code MUST coordinate with Rigby (the Personal Assistant) for all decision-making, questions, and status updates. **Do not ask yes/no or approval questions in the terminal** — route them through Rigby via `python tools/pa_chat.py "message" --tools --conversation <conversation_id>`. The user (Chris) will respond via the Chat UI. Only use the terminal for questions if explicitly told to do so for a specific reason.

- **Active conversation:** Set per session (check with Chris or Rigby)
- **Tool:** `python tools/pa_chat.py "message" --tools --conversation <id>`
- **Rigby knows:** current priorities, context, errors, and Chris's preferences

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
| **Agents** | 218 | 84 AGENT_MAP (74 enabled, 8 rerouted, 2 blocked) + ~139 DB persona agents (via DynamicPersonaAgent), 26 provenance-tracked |
| **Spiders** | 79 | 74 working, 5 need API keys |
| **PA Tools** | 130+ | GPT-5.2 function calling, 130+ tool handlers, 85+ schemas, 8 enrichment services |
| **LLM Providers** | 6 | OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini |
| **Database Models** | 397+ | PostgreSQL + pgvector |
| **Celery Tasks** | 269 | 9 worker processes (7 Celery + code-worker + web), dedicated PA queue |
| **Services** | 135 | Signal aggregation, content scoring, content deliberation, auto-spawning |
| **Body Systems** | 9 | HEART, LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR, BRAIN, SKIN |
| **Advisors** | 25 | Famous figures + domain experts |
| **Frontend** | ~2,500 KB | 9 workspace tabs, 69 routes, 12-tab betting dashboard |

## Project Structure

### Key Directories
- `core/agents/` - 84 AGENT_MAP agents with learning hooks
- `core/services/` - 134 service classes
- `ai_core/spiders/` - 77 spiders
- `docs/topics/` - Embedding-optimized subsystem docs (current state)
- `docs/handoffs/` - 641 session handoff documents (build history)

### Key Files
| File | Purpose |
|------|---------|
| `00-START-NEXT-SESSION.md` | Current session priorities |
| `core/agent_router.py` | Deterministic agent routing |
| `core/tasks.py` | Celery background tasks |
| `core/conversation_orchestrator.py` | Multi-agent conversations |
| `core/services/unified_pa_entrypoint.py` | PA: GPT-5.2 function calling agentic loop, enrichment pipeline |
| `core/services/tool_dispatcher.py` | PA: 53 tool handlers |
| `core/services/pa_tool_schemas.py` | PA: 50+ OpenAI function-calling tool schemas |
| `core/services/signal_aggregation_service.py` | Signal clustering & auto-topic generation |
| `core/services/content_scoring_service.py` | Rule-based reach/intent/replicability scoring |
| `core/services/content_deliberation_runner.py` | v2 content pipeline |
| `frontend/src/pages/WorkspacePageNew.tsx` | 9-tab modular workspace |
| `frontend/src/pages/CommandCenterPage.tsx` | Command Center with PA chat |

## Subsystem Documentation

Detailed current-state docs for each subsystem (designed for embedding):

| Topic File | Covers |
|------------|--------|
| [docs/topics/personal-assistant.md](docs/topics/personal-assistant.md) | PA GPT-5.2 function calling, 53 tools, enrichment, async flow |
| [docs/topics/content-pipeline.md](docs/topics/content-pipeline.md) | ClaimsPack, deliberation, reviewers, PublishGate |
| [docs/topics/agent-system.md](docs/topics/agent-system.md) | 84 AGENT_MAP agents, routing, ToolCallRecord, provenance |
| [docs/topics/initiative-pipeline.md](docs/topics/initiative-pipeline.md) | Dreams, 5-stage pipeline, signals, action items |
| [docs/topics/celery-workers.md](docs/topics/celery-workers.md) | 9 worker processes, queues, memory management, observability |
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
| [demo_mode.md](docs/demo_mode.md) | Resolve demo mode guardrails, demo clip generation |
| [governance_redesign.md](docs/governance_redesign.md) | Governance UX redesign spec, 7 implementation tickets |

**Documentation Index:** Run `python manage.py build_docs_index` to regenerate `docs/INDEX.md`

---

**Always read `00-START-NEXT-SESSION.md` first - it has the current priorities!**
