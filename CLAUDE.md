# CLAUDE - AI Session Entry Point

**Last Updated:** January 29, 2026 - Session 865
**Status:** Component Health: 100% | Integration Score: 95% | Data Display: 95% | Django Web App | 9 BODY SYSTEMS | 14/14 SCI-FI UI | 46 Pages | **Modular Workspace** | Self-Executing | **Celery Health Monitoring: ACTIVE** | **Podcast TTS: RECONNECTED** | **Content Intelligence: IMPROVED** | **ConceptForge: ACTIVE** | **Content Flow: COMPLETE** | **Data Persistence: COMPLETE** | **Initiative Pipeline: ACTIVE** | **Citation Gate: ACTIVE** | **Diagnostic Pipeline: ACTIVE** | **User Context: ACTIVE** | **Workspace Inline: ACTIVE**

## System Stats
| Component | Count | Details |
|-----------|-------|---------|
| **Agents** | 75 | All synced to database + workspace integration (+1 EditorAgent) |
| **Spiders** | 77 | 72 working, 5 need API keys |
| **PA Tools** | 86 | +body tools for all 9 systems |
| **LLM Providers** | 6 | OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini |
| **LLM Models** | 16 | GPT-5 family, Claude 4, Llama, DeepSeek V3, Gemini 2.5/3 |
| **Database Models** | 378+ | Including Deliverable, AuditReport, AgentMemory, ToolCallRecord, DecisionRecord, ResearchResult |
| **Celery Tasks** | 241 | ALL body systems active, autonomous remediation, async conversations, ConceptForge, health monitoring |
| **Services** | 124 | Including diagnostic pipeline, context optimization, self-healing orchestrator |
| **Body Systems** | 9 | HEART, LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR, BRAIN, SKIN |
| **Advisors** | 25 | Famous figures + domain experts |
| **Frontend Bundle** | 1,948 KB | 12 workspace tabs (+Dossiers), collapsible sidebar |

## Key Capabilities
- **Podcast TTS + Voice Profiles + ConceptForge UI (865):** Reconnected ElevenLabs TTS pipeline, VoiceProfileModal fetches real voices, custom voice selection. Added Dossiers tab with full 6-stage pipeline visualization. Celery health monitoring sends Discord alerts every 30 min.
- **Content Intelligence Improvements (864):** EditorAgent for auto-enhancement, operational title detection (auto-internal), lowered structure threshold 0.65→0.55. Expected: 2%→15%+ publish ready.
- **ConceptForge Pipeline (863):** Content → Intelligence → Strategy → Product. 6-stage autonomous think tank with 139 persona agents and 25 legendary advisors. Gate: quality >= 0.80 + strategic_tag.
- **Content Flow Unification (862):** Dream → Initiative → 5 Stages → Deliverable with full FK traceability. New ResearchResult model for Stage 1 tracking.
- **Data Persistence Complete (861):** Fixed 6 data persistence gaps - ToolCallRecord, DecisionRecord, SpiderAggregation, LearningBackup models + Content Tab modals with full content viewing
- **Initiative Pipeline + API Error Handling (860):** Documents now link to initiatives (25 backfilled) + fixed all console 404/401 errors and v.filter crashes
- **Workspace Inline Refactor (857):** 181 external links removed - all content displays inline, publish action creates Deliverables
- **User Context Injection (858):** All agents receive personalized user data (skills, goals, preferences) via context dict with category-based injection policy
- **Diagnostic Pipeline (856):** Detection → Diagnosis → Prescription system for failure analysis with evidence gathering
- **Experiment Learning Loop (836):** 251 learnings, 29 decision patterns, 89% success rate - Celery Beat fix + 3 production API fixes
- **Agent Output Rendering (835):** 10 output categories, 4 specialized renderers (Trends, Advisors, Investment, Security)
- **Async Conversations (827):** Production 502 fix - conversations run via Celery, instant response with task_id
- **Goal-Driven Conversations (826):** Objectives, success criteria, structured turn flows, topic-matched agents
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
| **865** | Podcast TTS + Voice Profile Integration + Celery Health Monitoring | `SESSION_865_PODCAST_TTS_VOICE_PROFILES.md` |
| **864** | Content Intelligence Improvements - EditorAgent, operational titles, threshold 0.65→0.55 | `SESSION_864_RUN_MODE_TRACKING.md` |
| **863** | ConceptForge - Autonomous Think Tank Pipeline (Content → Intelligence → Strategy → Product) | `SESSION_863_CONCEPTFORGE.md` |
| **862** | Content Flow Unification - Dream → Initiative → Stages → Deliverable with full FK traceability | `SESSION_862_CONTENT_FLOW_UNIFICATION.md` |
| **861** | Data Persistence Gaps - 6 fixes (ToolCall, Decision, Spider, Learning, Feedback) + Content Tab UI | `SESSION_861_DATA_PERSISTENCE.md` |
| **860** | Initiative Pipeline + API Error Handling - 25 docs linked, console errors fixed | `SESSION_860_API_ERROR_HANDLING.md` |
| **858** | User Context Injection - Agents receive personalized user data | `SESSION_858_USER_CONTEXT_INJECTION.md` |
| **857** | Workspace Inline Refactor - 181 external links removed, publish fix | `SESSION_857_WORKSPACE_INLINE_REFACTOR.md` |
| **856** | Diagnostic Pipeline + Agent Content Review Fixes (12 agents) | `SESSION_856_DIAGNOSTIC_PIPELINE.md` |
| **847** | Initiative Pipeline - ThinkingAgent → Initiative → Stages → Documents | `SESSION_847_INITIATIVE_PIPELINE.md` |
| **846** | Citation Gate + Serper News API + Stuck Conversations Fix + Dream Cleanup | `SESSION_846_CITATION_GATE.md` |
| **842** | Agent Learning Tab + Production Cleanup (242 stuck) + Celery Beat Investigation | `SESSION_842_AGENT_LEARNING_TAB_FIXES.md` |
| **841** | Experiment Monitoring Fixes - Stop global halts, provider health tracking | `SESSION_841_EXPERIMENT_MONITORING_FIXES.md` |
| **836** | Experiment System Diagnosis - Celery Beat fix, 251 learnings created | `SESSION_836_EXPERIMENT_SYSTEM_DIAGNOSIS.md` |
| **835** | Agent Output Audit (80+ agents) + 4 New Renderers + Deep Linking Fix | `SESSION_835_AGENT_OUTPUT_AUDIT.md` |
| **834** | Sidebar Cleanup (44→15) + Advisors Panel + Grouped Operations + Detail Modals | `SESSION_834_UI_CONSOLIDATION.md` |
| **833** | Workspace Improvements + Blog Approval + 50 Agent Fixes | `SESSION_833_WORKSPACE_IMPROVEMENTS.md` |
| **832** | Recent Activity Enhancement - New fields, system activity | `SESSION_832_RECENT_ACTIVITY_ENHANCEMENT.md` |

**Older sessions:** See `docs/handoffs/` directory (Sessions 197-865)

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
