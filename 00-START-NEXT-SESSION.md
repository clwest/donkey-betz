# Session 951 - Start Here

**Previous Session:** 950 (Kalshi Sports Categorization + Workspace Scroll Fix)
**Date:** February 6, 2026
**Status:** 76 Agents | 77 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **166 INITIATIVES** | **Risk-Aware RAG: COMPLETE** | **Dual-Channel Retrieval: ACTIVE** | **Risk Re-Ranking: ACTIVE** | **RESERVED Budget Tier: ACTIVE** | **Unified PA: FULL STACK** | **Voice System: COMPLETE** | **Learning Loop: ACTIVE**

---

## Session 950 Summary (Just Completed)

### Kalshi Sports Betting Market Categorization Fix - PR #926

Fixed sports betting markets being miscategorized as "tech" or "general" in Market Intelligence reports.

**Changes:**
- Added dedicated 'sports' category to Kalshi spider with comprehensive patterns:
  - Major leagues: NBA, NFL, MLB, NHL, MLS, WNBA, NCAA, PGA, UFC, MMA
  - Esports: League of Legends, Valorant, Counter-Strike, Dota, Overwatch
  - Betting terms: parlay, spread, over/under, moneyline, prop bet
  - Player stats: points, assists, rebounds, touchdowns, yards, goals
  - Team names: Lakers, Celtics, Cowboys, Patriots, Yankees, etc.
  - Player names: LeBron, Curry, Mahomes, etc.
- Added `_clean_title()` for multi-leg parlay bets:
  - Detects concatenated "yes X: value, yes Y: value" patterns
  - Creates readable titles like "Player + 9 others Parlay (10 legs)"
- Improved volume/probability handling:
  - Use `last_price` as fallback for probability calculation
  - Check multiple volume field names (volume, volume_24h, dollar_volume)
- Updated MarketIntelligenceCoordinator to include 'sports' in categories

### Workspace Scroll Fix - PR #924

Fixed workspace pages not scrolling after PA dock was added in Session 948.

### Empty Stock Analysis Fix - PR #927

Fixed BullCaseAgent and BearCaseAgent returning empty results in Market Intelligence reports.

**Root Cause:** Session 761 refactored the agents to use LLM tool calling, but changed the return structure from a list of cases to a single dict. The coordinator expected `{'bull_cases': [...]}` but got `{'analysis': ..., 'ticker': 'AAPL'}`.

**Fix:** Updated both agents to iterate over all tickers and return the expected list format.

**Files Changed:**
- `ai_core/spiders/specialized/kalshi_spider.py` - Sports category + title cleanup
- `core/agents/stocks/market_intelligence_coordinator.py` - Sports signals
- `core/agents/stocks/bull_case_agent.py` - Return bull_cases list
- `core/agents/stocks/bear_case_agent.py` - Return bear_cases list
- `frontend/src/components/layout/Layout.tsx` - Fixed overflow-hidden to overflow-auto

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
| **950** | Kalshi Sports Categorization + Workspace Scroll + Stock Analysis Fix | #924, #926, #927 |
| **949** | Risk-Aware RAG - Dual-channel retrieval, RESERVED budget, risk re-ranking | #920, #921, #922 |
| **947** | Spider Context Extension - CreativeOrchestrator (13) + ResearchOrchestrator (5) | - |
| **946** | Learning Loop Backend - LearningLoopOrchestrator, prompt injection, scheduled extraction | #903 |
| **945** | Stale Initiative Cleanup - New junk patterns, activity tracking, last_activity_at field | #901 |
| **944** | Operations Tab Fix + PA Boardroom Listing + ConceptForge Dedupe | #897, #898, #899 |
| **943** | Stage Distribution Fix + Stale Investigation | #876 |

---

## Key Files Reference

### Session 950 - Kalshi Sports + Stock Analysis Fix
| File | Purpose |
|------|---------|
| `ai_core/spiders/specialized/kalshi_spider.py` | Sports category, _clean_title(), volume fallbacks |
| `core/agents/stocks/market_intelligence_coordinator.py` | Sports signals integration |
| `core/agents/stocks/bull_case_agent.py` | Returns bull_cases list for all tickers |
| `core/agents/stocks/bear_case_agent.py` | Returns bear_cases list for all tickers |
| `frontend/src/components/layout/Layout.tsx` | Workspace scroll fix |

### Session 949 - Risk-Aware RAG
| File | Purpose |
|------|---------|
| `core/services/scoped_retrieval.py` | Dual-channel search, risk re-ranking, document class filtering |
| `core/services/context_budget_manager.py` | RESERVED priority tier for risk-aware docs |
| `core/agent_router.py` | `_get_risk_aware_context()` + injection |
| `core/management/commands/classify_docs_for_rag.py` | Auto-classify docs by patterns |
| `content/models.py` | Document risk fields (is_critical, risk_level, document_class) |

### Initiative Pipeline
| File | Purpose |
|------|---------|
| `core/models_document_registry.py` | `Initiative`, `InitiativeStage` models |
| `core/tasks.py` | `cleanup_junk_initiatives` - daily at 4 AM |
| `core/models_unified_system.py` | `HiveMindSession` - conversations linked to initiatives |

---

**Session 951 Focus: Choose priority option above and continue building!**
