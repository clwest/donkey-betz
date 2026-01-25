# CLAUDE - AI Session Entry Point

**Last Updated:** January 25, 2026 - Session 825
**Status:** Component Health: 100% | Integration Score: 95% | Data Display: 90% | Django Web App | 9 BODY SYSTEMS | 14/14 SCI-FI UI | 46 Pages | **Modular Workspace** | Self-Executing

## System Stats
| Component | Count | Details |
|-----------|-------|---------|
| **Agents** | 74 | All synced to database + workspace integration |
| **Spiders** | 77 | 72 working, 5 need API keys |
| **PA Tools** | 86 | +body tools for all 9 systems |
| **LLM Providers** | 6 | OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini |
| **LLM Models** | 16 | GPT-5 family, Claude 4, Llama, DeepSeek V3, Gemini 2.5/3 |
| **Database Models** | 367+ | Including Deliverable, AuditReport, AgentMemory |
| **Celery Tasks** | 234 | ALL body systems active, autonomous remediation |
| **Services** | 120 | Including context optimization, self-healing orchestrator |
| **Body Systems** | 9 | HEART, LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR, BRAIN, SKIN |
| **Advisors** | 25 | Famous figures + domain experts |
| **Frontend Bundle** | 1,948 KB | 11 workspace tabs, collapsible sidebar |

## Key Capabilities
- **Self-Healing System (820-823):** Auto-discovers audits → assigns to agents → executes fixes → verifies
- **SKIN Layer (695, 778):** All 74 agents write to real workspaces with rollback
- **UI Consolidation (825):** 29 pages → 6 workspace tabs, collapsible sidebar
- **Context Optimization (806):** 70% token reduction via ToolCategoryRouter + LazyContextLoader
- **Memory Safety (768):** Classification prevents test content from polluting learning
- **Integration Complete (744):** All 5 phases done - spider data, learning, advisors flow to agents

---

## Quick Start

```bash
# 1. Read current context (MANDATORY)
cat 00-START-NEXT-SESSION.md

# 2. Start platform
make start && make celery

# 3. Access AI Studio
open http://localhost:8000/ai-studio/
```

---

## Project Structure

### Key Directories
- `core/agents/` - 74 agents with learning hooks
- `core/services/` - 120 service classes
- `ai_core/spiders/` - 77 spiders
- `docs/handoffs/` - Session handoff documents

### Key Files
| File | Purpose |
|------|---------|
| `00-START-NEXT-SESSION.md` | Current session priorities |
| `core/agent_router.py` | Deterministic agent routing |
| `core/tasks.py` | Celery background tasks |
| `core/conversation_orchestrator.py` | Multi-agent conversations |
| `core/services/autonomous_remediation_orchestrator.py` | Self-healing system |
| `frontend/src/pages/WorkspacePageNew.tsx` | Modular command center |

---

## Agent Ecosystem (74 Agents)

**49 routable** | **25 non-routable** (sub-agents/coordinators)

| Category | Count | Examples |
|----------|-------|----------|
| Creation | 4 | ImageAgent, VideoAgent, AudioAgent, ThreeDAgent |
| Development | 5 | FullStackDeveloperAgent, CodeReviewAgent, DevOpsAgent |
| Executive | 4 | CTOAgent, COOAgent, CreativeDirectorAgent |
| Stocks | 9 | StockAuditCoordinator, BullCaseAgent, BearCaseAgent |
| Blockchain | 5 | SmartContractAuditorAgent, WhaleWatcherAgent |
| Content | 8 | ContentWriterAgent, PodcastCoordinatorAgent |
| Analysis | 6 | TrendAnalysisAgent, MarketIntelligenceAgent |
| Special | 3 | ThinkingAgent, SystemIntelligenceAgent |

Full list: See `docs/AGENTS.md`

---

## Spider Network (77 Spiders)

| Category | Count | Examples |
|----------|-------|----------|
| News/Media | 10 | TechCrunch, BBC, Reuters, NewsAPI |
| Financial | 9 | CoinGecko, YahooFinance, Polygon, Kalshi |
| Tech | 8 | HackerNews, DevTo, GitHub |
| Legal | 6 | CourtListener, FindLaw, Justia |

Full list: See `docs/SPIDERS.md`

---

## GPT-5-mini Configuration

```python
# CORRECT - Reasoning model has different parameters
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=messages,
    max_completion_tokens=6000  # NOT max_tokens, NO temperature
)
```

---

## Troubleshooting

```bash
# Full restart
pkill -f daphne; pkill -f redis; pkill -f celery
rm -f .daphne.pid .celery.pid .celery-beat.pid
make start && make celery

# macOS Celery SIGSEGV fix
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES celery -A core worker -l INFO --pool=solo
```

---

## Recent Sessions (Last 15)

| Session | Focus | Handoff |
|---------|-------|---------|
| **825** | UI Consolidation - 29 pages → 6 tabs, collapsible sidebar | `SESSION_825_UI_CONSOLIDATION_PLAN.md` |
| **824** | UI Integration Sprint - Live Metrics, Triggers, Actions | `SESSION_824_UI_INTEGRATION_SPRINT.md` |
| **823** | Self-Execution Engine - System monitors + triggers actions | `SESSION_823_SELF_EXECUTION_ENGINE.md` |
| **822** | SKIN Layer Autonomous Remediation | `SESSION_822_SKIN_REMEDIATION.md` |
| **821** | Staleness Validation - Filters old audit findings | `SESSION_821_STALENESS_VALIDATION.md` |
| **820** | Self-Healing Orchestration + Tiered Docs Injection | `SESSION_820_SELF_HEALING_ORCHESTRATION.md` |
| **819** | Deliverables Marketplace + Audit Tracking | `SESSION_819_DELIVERABLES_MARKETPLACE.md` |
| **817** | Autonomous Agent Behavior + Smart Tool Renderer | `SESSION_817_AUTONOMOUS_AGENTS_TOOL_RENDERER.md` |
| **816** | Operations Panel + Playbooks + Audits Browser | `SESSION_816_OPERATIONS_PLAYBOOKS_AUDITS.md` |
| **815** | Platform Command Center | `SESSION_815_PLATFORM_COMMAND_CENTER.md` |
| **814** | Spider Search Fix + Blogs Page + Docs Injection | See handoffs |
| **810** | MASSIVE Celery Beat Fix - 60 tasks restored | See handoffs |
| **806** | Personal Assistant Context Optimization | `SESSION_806_CONTEXT_OPTIMIZATION.md` |
| **781** | Agent Conversation Voice Fixes | `SESSION_781_AGENT_VOICE_FIXES.md` |
| **768** | Memory Safety Classification | `SESSION_768_MEMORY_SAFETY_CLASSIFICATION.md` |

**Older sessions:** See `docs/handoffs/` directory (Sessions 197-825)

---

## Documentation

| Doc | Purpose |
|-----|---------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture |
| [AGENTS.md](docs/AGENTS.md) | Agent documentation (74 agents) |
| [SPIDERS.md](docs/SPIDERS.md) | Spider network (77 spiders) |
| [SERVICES.md](docs/SERVICES.md) | Services layer (120 services) |
| [DATABASE_MODEL_REFERENCE.md](docs/DATABASE_MODEL_REFERENCE.md) | Which DB table for what |

**Documentation Index:** Run `python manage.py build_docs_index` to regenerate `docs/INDEX.md`

---

**Always read `00-START-NEXT-SESSION.md` first - it has the current priorities!**
