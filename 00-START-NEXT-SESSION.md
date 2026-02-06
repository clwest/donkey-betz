# Session 950 - Start Here

**Previous Session:** 949 (Risk-Aware RAG)
**Date:** February 6, 2026
**Status:** 76 Agents | 77 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **166 INITIATIVES** | **Risk-Aware RAG: COMPLETE** | **Dual-Channel Retrieval: ACTIVE** | **Risk Re-Ranking: ACTIVE** | **RESERVED Budget Tier: ACTIVE** | **Unified PA: FULL STACK** | **Voice System: COMPLETE** | **Learning Loop: ACTIVE**

---

## Session 949 Summary (Just Completed)

### Risk-Aware RAG - Dual-Channel Retrieval with Risk Re-Ranking

Implemented complete risk-aware RAG system based on ChatGPT analysis. Critical docs, incident reports, and audit findings are now never missed during retrieval.

**Phase 1 (P0) - PR #920:**
- Added `is_critical`, `risk_level`, `document_class` fields to Document model
- Added `linked_document` FK on AuditFinding
- Created `classify_docs_for_rag` management command
- Added dual-channel retrieval methods to scoped_retrieval

**Phase 2 (P1) - PR #921:**
- Added RESERVED priority tier to context_budget_manager (between CRITICAL and HIGH)
- Reserved budget sections: critical_docs (300), incident_docs (200), audit_findings (150)
- Integrated `_get_risk_aware_context()` into agent_router
- All agents now receive risk context in spider_context

**Phase 3 (P2) - PR #922:**
- Added risk-aware re-ranking with configurable boosts
- risk_level boosts: critical +25%, high +15%
- document_class boosts: postmortem +20%, incident +15%, security +15%
- Added `search_by_document_class()` and convenience methods
- Semantic/keyword search now applies re-ranking

**Files Changed:**
- `content/models.py` - Risk fields on Document
- `core/models_audit_tracking.py` - linked_document FK
- `core/services/scoped_retrieval.py` - Dual-channel + re-ranking
- `core/services/context_budget_manager.py` - RESERVED tier
- `core/agent_router.py` - Risk context injection
- `core/management/commands/classify_docs_for_rag.py` - NEW

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

---

## Recent Session History

| Session | Focus | PRs |
|---------|-------|-----|
| **949** | Risk-Aware RAG - Dual-channel retrieval, RESERVED budget, risk re-ranking | #920, #921, #922 |
| **947** | Spider Context Extension - CreativeOrchestrator (13) + ResearchOrchestrator (5) | - |
| **946** | Learning Loop Backend - LearningLoopOrchestrator, prompt injection, scheduled extraction | #903 |
| **945** | Stale Initiative Cleanup - New junk patterns, activity tracking, last_activity_at field | #901 |
| **944** | Operations Tab Fix + PA Boardroom Listing + ConceptForge Dedupe | #897, #898, #899 |
| **943** | Stage Distribution Fix + Stale Investigation | #876 |
| **942** | Integrity Anomaly Investigation + Halted Experiment Cleanup + Bulk Boardroom Actions | #874, #875 |

---

## Key Files Reference

### Session 949 - Risk-Aware RAG
| File | Purpose |
|------|---------|
| `core/services/scoped_retrieval.py` | Dual-channel search, risk re-ranking, document class filtering |
| `core/services/context_budget_manager.py` | RESERVED priority tier for risk-aware docs |
| `core/agent_router.py` | `_get_risk_aware_context()` + injection |
| `core/management/commands/classify_docs_for_rag.py` | Auto-classify docs by patterns |
| `content/models.py` | Document risk fields (is_critical, risk_level, document_class) |

### Session 947 - Spider Context Extension
| File | Purpose |
|------|---------|
| `core/services/creative_orchestrator.py` | 13 agent calls now get real spider data |
| `core/services/research_orchestrator.py` | 5 agent calls now get real spider data |
| `core/services/spider_context_builder.py` | Central spider context builder service |

### Initiative Pipeline
| File | Purpose |
|------|---------|
| `core/models_document_registry.py` | `Initiative`, `InitiativeStage` models |
| `core/tasks.py` | `cleanup_junk_initiatives` - daily at 4 AM |
| `core/models_unified_system.py` | `HiveMindSession` - conversations linked to initiatives |

---

**Session 950 Focus: Choose priority option above and continue building!**
