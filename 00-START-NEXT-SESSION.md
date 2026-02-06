# Session 954 - Start Here

**Previous Session:** 953 (Agent Provenance Expansion)
**Date:** February 6, 2026
**Status:** 76 Agents | 77 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **166 INITIATIVES** | **Risk-Aware RAG: COMPLETE** | **Dual-Channel Retrieval: ACTIVE** | **Risk Re-Ranking: ACTIVE** | **RESERVED Budget Tier: ACTIVE** | **Unified PA: FULL STACK** | **Voice System: COMPLETE** | **Learning Loop: ACTIVE** | **PA Platform Query: ACTIVE** | **Agent Provenance: 18 AGENTS**

---

## Session 953 Summary (Just Completed)

### Agent Provenance Expansion - Extends Session 918

Added provenance tracking to 18 additional data-driven agents, building on the Session 918 foundation.

**Stock Agents (24h stale threshold):**
- BullCaseAgent, BearCaseAgent
- MarketIntelligenceCoordinator, StockAuditCoordinator
- MarketAnomalyDetectorAgent, SignalScannerAgent
- InstitutionalWatcherAgent, MarketMovementMonitorAgent

**Blockchain Agents (4h stale threshold):**
- BlockchainAuditCoordinator, WhaleWatcherAgent
- TransactionMonitorAgent, ExploitDetectorAgent
- SmartContractAuditorAgent

**Analysis Agents (24h stale threshold):**
- TrendAnalysisAgent, MarketIntelligenceAgent, OpportunityScoringAgent

**Standalone Agents (LearningMixin pattern):**
- BookmakerAgent (2h - sports data)
- CreationAgent (24h - generated content)

**Pattern Applied:**
```python
from core.agents.report_schemas import build_provenance, format_disclaimer

# Build provenance from tool calls
provenance = build_provenance(
    report_type='stock_analysis',  # category-specific
    agent_name=self.name,
    sources=sources,
    stale_threshold_hours=24.0,  # varies by category
)

# Add to result
result.data['provenance'] = provenance.to_dict()
result.data['publishable'] = provenance.publishable
result.data['validation_status'] = provenance.validation_status
```

**Files Changed:** 18 agent files in `core/agents/`

---

## PRIORITY OPTIONS FOR NEXT SESSION

### Option A: Run Document Classification
Run the new classification command to tag existing documents:
```bash
python manage.py classify_docs_for_rag --dry-run  # Preview
python manage.py classify_docs_for_rag            # Execute
```

### Option B: Boardroom ML Improvements
Improve ML recommendations for boardroom items:
- Train on actual user decisions
- Better confidence scoring
- Recommendations based on item content, not just type

### Option C: Initiative Source Cleanup
Investigate why so many junk initiatives are being created:
- Find where "Auto-created From Conversation Decision" comes from
- Add validation before initiative creation
- Consider gating initiative creation on founder intent

### Option D: Learning Loop Refinement
Build on the learning loop with:
- More success signals for other tools
- User feedback integration
- Learning effectiveness tracking
- Dashboard for viewing active learnings

### Option E: RAG Observability Dashboard
Create visibility into the new risk-aware RAG system:
- Show which critical docs are being retrieved
- Track risk re-ranking effectiveness
- Monitor dual-channel usage stats

### Option F: Extend Provenance to Remaining Agents
Add provenance to additional agent categories:
- Content agents (ContentWriterAgent, PodcastCoordinatorAgent)
- Executive agents (CTOAgent, COOAgent)
- Development agents (FullStackDeveloperAgent)

---

## Recent Session History

| Session | Focus | PRs |
|---------|-------|-----|
| **953** | Agent Provenance Expansion - 18 agents with provenance tracking | - |
| **952** | Narrative Injection Enhancement - Topic filtering, diversity, fallbacks | #929, #930 |
| **951** | PA Platform Query Tool - Query deliverables, reports, initiatives | #929 |
| **950** | Kalshi Sports Categorization + Workspace Scroll + Stock Analysis Fix | #924, #926, #927 |
| **949** | Risk-Aware RAG - Dual-channel retrieval, RESERVED budget, risk re-ranking | #920, #921, #922 |
| **947** | Spider Context Extension - CreativeOrchestrator (13) + ResearchOrchestrator (5) | - |
| **946** | Learning Loop Backend - LearningLoopOrchestrator, prompt injection, scheduled extraction | #903 |
| **945** | Stale Initiative Cleanup - New junk patterns, activity tracking, last_activity_at field | #901 |

---

## Key Files Reference

### Session 953 - Agent Provenance Expansion
| File | Purpose |
|------|---------|
| `core/agents/report_schemas.py` | `build_provenance()`, `format_disclaimer()` |
| `core/agents/stocks/*.py` | 8 stock agents with provenance |
| `core/agents/blockchain/*.py` | 5 blockchain agents with provenance |
| `core/agents/analysis/*.py` | 3 analysis agents with provenance |
| `core/agents/bookmaker_agent.py` | Standalone with provenance |
| `core/agents/creation_agent.py` | Standalone with provenance |

### Session 952 - Narrative Injection Enhancement
| File | Purpose |
|------|---------|
| `core/services/content_voice_system.py` | DOMAIN_KEYWORDS, FALLBACK_INCIDENTS, topic filtering, diversity constraints |

### Session 949 - Risk-Aware RAG
| File | Purpose |
|------|---------|
| `core/services/scoped_retrieval.py` | Dual-channel search, risk re-ranking, document class filtering |
| `core/services/context_budget_manager.py` | RESERVED priority tier for risk-aware docs |
| `core/agent_router.py` | `_get_risk_aware_context()` + injection |

### Initiative Pipeline
| File | Purpose |
|------|---------|
| `core/models_document_registry.py` | `Initiative`, `InitiativeStage` models |
| `core/tasks.py` | `cleanup_junk_initiatives` - daily at 4 AM |
| `core/models_unified_system.py` | `HiveMindSession` - conversations linked to initiatives |

---

**Session 954 Focus: Choose priority option above and continue building!**
