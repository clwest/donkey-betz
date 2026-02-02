# CLAUDE - AI Session Entry Point

**Last Updated:** February 1, 2026 - Session 903
**Status:** Component Health: 100% | Integration Score: 95% | Data Display: 95% | Django Web App | 9 BODY SYSTEMS | 14/14 SCI-FI UI | 47 Pages | **AI OS Boot Experience** | **Modular Workspace** | Self-Executing | **Celery Health Monitoring: ACTIVE** | **Executive Function: ACTIVE** | **Contracts: 3** | **Auto-Spawning: ACTIVE** | **Prompt Sharpening: ACTIVE** | **Content Feedback Loop: ACTIVE** | **Domain Context Injection: ACTIVE** | **Signal Intelligence: WIRED** | **Initiative Priority: COMPLETE** | **Action Item Tracking: COMPLETE** | **Celery OOM: FIXED**

## System Stats
| Component | Count | Details |
|-----------|-------|---------|
| **Agents** | 76 | All synced + DecisionEnforcerAgent ("Prefrontal Cortex") |
| **Spiders** | 77 | 72 working, 5 need API keys |
| **PA Tools** | 86 | +body tools for all 9 systems |
| **LLM Providers** | 6 | OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini |
| **LLM Models** | 16 | GPT-5 family, Claude 4, Llama, DeepSeek V3, Gemini 2.5/3 |
| **Database Models** | 386+ | Including Deliverable, AuditReport, SignalCluster, AutoTopic, InitiativeActionItem, ToolCallRecord, DecisionRecord, ResearchResult |
| **Celery Tasks** | 260 | ALL body systems active, autonomous remediation, async conversations, ConceptForge, health monitoring, signal aggregation |
| **Services** | 130 | Including AutoSpawnerService, SignalAggregationService, ActionItemParser, DomainContentContextBuilder (9 domains) |
| **Contracts** | 3 | ResearchContract, ExecutionMandate, SynthesisContract |
| **Body Systems** | 9 | HEART, LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR, BRAIN, SKIN |
| **Advisors** | 25 | Famous figures + domain experts |
| **Frontend Bundle** | 1,948 KB | 12 workspace tabs (+Dossiers), collapsible sidebar |

## Key Capabilities
- **Signal Intelligence Wired + Celery OOM Fix (903):** process_pending_auto_topics creates HiveMindSessions with signal_cluster/auto_topic FK links. trigger_signal_driven_conversation dispatches with full provenance chain. run_triggered_conversation accepts hive_session_id and updates status. Celery OOM fixed: task lock on scan_spider_opportunities (Django cache), reduced frequency 15→30 min, proper aiohttp connector cleanup.
- **Action Item Tracking (902):** Extract and track "Next Steps" from conversation conclusions. InitiativeActionItem model with status (pending/in_progress/completed/blocked), priority (critical/high/medium/low), timeline parsing ("Week 0-1" → due date), agent assignments. Parser service extracts items from `=== DecisionSummary ===` sections. 6 API endpoints for CRUD + bulk extraction. UI section in Initiative modal with stats bar, status checkboxes, priority badges, timeline indicators, manual creation input.
- **Initiative Priority & Portfolio (901):** Transform Initiative UI from firehose to strategic project management. Priority scoring: `impact*0.4 + urgency*0.2 + confidence*0.2 + revenue*0.2`. Priority levels: critical (>=0.8), high (>=0.6), medium (>=0.4), low (<0.4). Purpose categories: revenue, stability, learning, expansion, maintenance. Program groupings: 10 programs for portfolio organization. 4-tab UI: Active (working on), Portfolio (grouped by program), Archive (completed/archived), Stats (comprehensive breakdown). Priority badges, purpose icons, collapsible program sections.
- **Signal Intelligence (900):** Full provenance chain tracks WHY conversations happen, not just WHEN. SignalCluster groups spider signals into patterns (source_breakdown, strength, confidence, novelty, keywords). AutoTopic records why topics are chosen with rationale. Signal Aggregation Service clusters SpiderData every 30 min via Celery. API returns origin_signals with full chain. UI displays Origin Signals section in Initiative modal showing source breakdown, pattern metrics, sample signals, and auto topic rationale. Signal-Driven badge in headers. 22 clusters + 10 auto-topics in production.
- **Domain Content Context (891):** Unified system injects domain-specific platform data into ALL content. 9 domains: finance, crypto, sports, betting, ai_tech, legal, career, health, education. Auto-detects topic domain, supports cross-domain content (up to 2 domains). Gives every content type the "builder voice."
- **Podcast Quality System (890):** Anti-cliché detection (50+ phrases), PodcastStyleProfile model, host POV upgrade (takes stances), system war stories tool.
- **Content Feedback Loop (886):** BlogPerformanceContextBuilder injects past performance data into ContentWriterAgent prompts. Agent now "knows" quality scores, top topics, strengths/weaknesses, and active learning rules. Experiment audit: cleaned 81 junk experiments, raised error threshold 25%→35%, 87.5% real success rate.
- **AI OS Boot Experience (884):** Home page at `/` with personalized greeting, "while you were away" activity cards, active projects with progress bars, natural language input routing to PA, quick action buttons (Create, Research, Decide, Review, Build).
- **Executive Function + Contracts (872):** DecisionEnforcerAgent forces decisions after debate. ResearchContract, ExecutionMandate, SynthesisContract prevent vague outputs. AutoSpawnerService triggers data gathering reflexes. Prompt sharpening transforms hedging → decisive language.
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
| `core/services/signal_aggregation_service.py` | Signal clustering & auto-topic generation |
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
| **903** | Signal Intelligence Wired + Celery OOM Fix - HiveMind provenance chain, spider task memory fix | `SESSION_903_SIGNAL_CELERY_FIX.md` |
| **902** | Action Item Tracking - Extract & track next steps from conversation conclusions | `SESSION_902_ACTION_ITEM_TRACKING.md` |
| **901** | Initiative Priority & Portfolio - 4 tabs, priority scoring, purpose/program categorization | `SESSION_901_INITIATIVE_PRIORITY.md` |
| **900** | Signal Intelligence - SignalCluster, AutoTopic models for Origin & Trigger UI provenance | `SESSION_900_SIGNAL_INTELLIGENCE.md` |
| **891** | Domain Content Context - 9 domains (finance, sports, crypto, etc.), unified router, cross-domain support | `SESSION_891_DOMAIN_CONTENT_CONTEXT.md` |
| **890** | Podcast Quality Improvements - Anti-cliché, PodcastStyleProfile, host POV upgrade | `SESSION_890_PODCAST_QUALITY.md` |
| **889** | Podcast Token Auth + SKIN Health Fix + Live Monitor Fix | `SESSION_889_COMPLETE.md` |
| **886** | Content Feedback Loop + Experiment Audit - BlogPerformanceContextBuilder, cleaned 81 junk experiments, 87.5% success rate | `SESSION_886_CONTENT_FEEDBACK_LOOP.md` |
| **885** | Celery Content Pipeline + Operations Tab Fix - dedicated celery-content worker | `SESSION_885_CELERY_CONTENT_PIPELINE.md` |
| **884** | AI OS Boot Experience - Home Page with greeting, while-away stats, projects, NL input | `SESSION_884_HOME_PAGE_BOOT.md` |
| **872** | Executive Function - DecisionEnforcerAgent, 3 Contracts, AutoSpawner, Prompt Sharpening | `SESSION_872_COMPLETE.md` |
| **867** | System-Wide Audit - 231 unscheduled tasks, 40+ stubs, Initiative Pipeline fix | `SESSION_867_SYSTEM_AUDIT.md` |
| **865** | Podcast TTS + Voice Profile Integration + Celery Health Monitoring | `SESSION_865_PODCAST_TTS_VOICE_PROFILES.md` |
| **864** | Content Intelligence Improvements - EditorAgent, operational titles, threshold 0.65→0.55 | `SESSION_864_RUN_MODE_TRACKING.md` |
| **863** | ConceptForge - Autonomous Think Tank Pipeline (Content → Intelligence → Strategy → Product) | `SESSION_863_CONCEPTFORGE.md` |
| **862** | Content Flow Unification - Dream → Initiative → Stages → Deliverable with full FK traceability | `SESSION_862_CONTENT_FLOW_UNIFICATION.md` |
| **861** | Data Persistence Gaps - 6 fixes (ToolCall, Decision, Spider, Learning, Feedback) + Content Tab UI | `SESSION_861_DATA_PERSISTENCE.md` |
| **860** | Initiative Pipeline + API Error Handling - 25 docs linked, console errors fixed | `SESSION_860_API_ERROR_HANDLING.md` |

**Older sessions:** See `docs/handoffs/` directory (Sessions 197-901)

---

## Documentation

| Doc | Purpose |
|-----|---------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture |
| [AGENTS.md](docs/AGENTS.md) | Agent documentation (74 agents) |
| [SPIDERS.md](docs/SPIDERS.md) | Spider network (77 spiders) |
| [SERVICES.md](docs/SERVICES.md) | Services layer (120 services) |
| [DATABASE_MODEL_REFERENCE.md](docs/DATABASE_MODEL_REFERENCE.md) | Which DB table for what |
| [API_PATH_POLICY.md](docs/API_PATH_POLICY.md) | API path conventions (`/api/` vs `/api/v1/`) |
| [DREAM_INITIATIVE_WORKFLOW.md](docs/DREAM_INITIATIVE_WORKFLOW.md) | Dream → Initiative 5-stage pipeline |

**Documentation Index:** Run `python manage.py build_docs_index` to regenerate `docs/INDEX.md`

---

**Always read `00-START-NEXT-SESSION.md` first - it has the current priorities!**
