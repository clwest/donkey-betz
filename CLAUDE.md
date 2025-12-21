# CLAUDE - AI Session Entry Point

**Last Updated:** December 21, 2025 - Session 521
**Status:** 100% Reality Score | Django Web App | ALL 6 PHASES COMPLETE + 15 Sci-Fi Features
**Spider Network:** 72 spiders | 20,712 data records | 88.1% embeddings
**Agent Ecosystem:** 42 routable agents | Autonomous Content Generation | 3-Agent Debates
**LLM Model:** GPT-5-mini (reasoning model - uses `max_completion_tokens`, no `temperature`)

---

## Quick Start

```bash
# 1. Read current context (MANDATORY)
cat 00-START-NEXT-SESSION.md

# 2. Start platform
make start
make celery

# 3. Access AI Studio
open http://localhost:8000/ai-studio/
```

---

## Project Structure

### Key Directories
- `core/agents/` - **Canonical agent location** (42 agents with learning hooks)
- `core/services/` - Business logic services
- `core/prompts/` - Central prompt registry
- `ai_core/spiders/` - Spider network (72 spiders)
- `ai_core/templates/` - Frontend (ai_image_studio.html)
- `docs/handoffs/` - Session handoff documents

### Key Files
| File | Purpose |
|------|---------|
| `00-START-NEXT-SESSION.md` | Current session priorities |
| `core/agent_router.py` | Deterministic agent routing |
| `core/tasks.py` | Celery background tasks |
| `core/celery.py` | Celery Beat schedules |
| `core/assistant/tool_definitions.py` | GPT tool schemas |

---

## Agent Ecosystem (42 Agents)

All agents in `core/agents/` with learning hooks connected to collective intelligence.

| Category | Agents |
|----------|--------|
| **Creation** | ImageAgent, VideoAgent, AudioAgent, ThreeDAgent |
| **Editing** | ImageEditingAgent, VideoEditingAgent |
| **Research** | ResearchAgent, TrendAnalysisAgent, OpportunityScoringAgent |
| **Strategy** | ContentStrategyAgent, BrandIdentityAgent, SEOOptimizerAgent, SocialMediaAgent |
| **Business** | CompetitorAnalysisAgent, CustomerResearchAgent, BrandStrategyAgent, MarketingStrategyAgent, BusinessContentStrategyAgent |
| **Executive** | CTOAgent, COOAgent, CreativeDirectorAgent, MeetingCoordinatorAgent |
| **Development** | CodeGeneratorAgent, FullStackDeveloperAgent, CodeReviewAgent, DevOpsAgent |
| **Content Studio** | AutonomousContentStudioCoordinator, TopicMinerAgent, ContrarianAgent, PerformanceAnalystAgent |
| **Specialized** | LegalDocDrafterAgent, ResolveAgent, PodcastCoordinatorAgent, AISeriesWorkflowAgent |
| **Training** | CharacterTrainingAgent, TrainedCreationAgent |
| **Orchestration** | WorkflowAgent, CampaignOrchestratorAgent |
| **Entry Point** | PersonalAssistantAgent |

### Agent Architecture
- **BaseAgent** - All agents inherit TimeTravelMixin, learning hooks, memory creation
- **Router** - `core/agent_router.py` - Deterministic routing (no LLM)
- **Learning** - All agents connected to collective intelligence system

---

## Spider Network (72 Spiders)

Real data sources across 20 categories:
- **Tech:** TechCrunch, The Verge, Wired, MIT Tech Review, HackerNews API
- **Jobs:** RemoteOK, WeWorkRemotely, Adzuna API
- **Financial:** CoinGecko API, Yahoo Finance API, Etherscan
- **Creative:** Dribbble, Behance, Unsplash API
- **Community:** Reddit (20+ subreddits)

---

## GPT-5-mini Configuration

**Critical:** GPT-5-mini is a reasoning model with different parameters!

```python
# CORRECT
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=messages,
    max_completion_tokens=6000  # NOT max_tokens
    # NO temperature parameter!
)
```

---

## Troubleshooting

```bash
# Full restart
pkill -f daphne; pkill -f redis; pkill -f celery
rm -f .daphne.pid .celery.pid .celery-beat.pid
make start && make celery

# Health check
curl http://localhost:8000/health/ping/

# Database check
.venv/bin/python manage.py shell -c "from core.models_unified_system import Agent; print(f'Agents: {Agent.objects.count()}')"
```

---

## Recent Sessions

| Session | Focus | Handoff |
|---------|-------|---------|
| 520 | Projects Tab Unification - Fixed CreativeProject vs PartnershipProject disconnect | `SESSION_520_PROJECTS_TAB_AUDIT.md` |
| 519 | Auto-Project Creation & Content Display | `SESSION_519_AUTO_PROJECT_CREATION_AND_CONTENT_DISPLAY.md` |
| 513 | Campaign Orchestrator Agent - Marketing hub | `SESSION_513_CAMPAIGN_ORCHESTRATOR.md` |
| 511 | ML Scoring Sub-Tab Enhancement | `SESSION_511_ML_SCORING_SUBTAB_ENHANCEMENT.md` |
| 503 | Spider API Fixes (Etherscan + Kaggle) | `SESSION_503_SPIDER_FIXES.md` |
| 499 | Full Agent Routing (42 Agents) | `SESSION_499_FULL_AGENT_ROUTING.md` |
| 497 | Platform Integration Gap Analysis | `SESSION_497_INTEGRATION_GAP_ANALYSIS.md` |
| 496 | AI Podcast Studio | `SESSION_496_AI_PODCAST_STUDIO.md` |
| 495 | SmartTrendingService & New Spiders | `SESSION_495_SMART_TRENDING_SERVICE.md` |
| 478 | DaVinci Resolve Integration | `SESSION_478_DAVINCI_RESOLVE_FULL_UTILIZATION.md` |

For older sessions, see `docs/handoffs/` directory.

---

## Documentation

| Doc | Purpose |
|-----|---------|
| `docs/ARCHITECTURE.md` | System architecture |
| `docs/CAPABILITIES.md` | Full feature list |
| `docs/AGENTS.md` | Agent documentation |
| `docs/SPIDERS.md` | Spider network details |
| `docs/SCIFI_FEATURES.md` | 15 advanced AI features |

---

## Platform Phases (All Complete)

| Phase | Focus | Status |
|-------|-------|--------|
| 1-6 | Creative Intelligence Empire | DONE |
| 7-15 | Sci-Fi Features (Dreams, Memory, Evolution, etc.) | DONE |
| Super Platform | Unified intelligence coordinator | DONE |

---

**Always read `00-START-NEXT-SESSION.md` first - it has the current priorities!**
