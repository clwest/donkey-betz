---
originating_session: 1006
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1006 — Systematic Cleanup & Agent Persistence

**Date:** February 13-14, 2026
**PRs:** #1160-#1168 (9 PRs)
**Theme:** Close disconnected dots — agent output persistence, enrichment data loss, legacy route cleanup

---

## Summary

Rapid-fire session knocking out known issues from the disconnected dots audit. 30 agents now persist output to the `Deliverable` model (was 0), enrichment data truncation fixed (was losing 85-95%), and 25 legacy redirect routes removed after updating all internal links.

---

## PR #1160: Profile Async Loading + Temporal Awareness + Opportunity Dedup

- `ExtendedUserProfile` loaded via `asyncio.to_thread()` (was sync blocking in async view)
- Temporal awareness: PA system prompt now includes current date/time
- `collect_real_opportunities`: `get_or_create` prevents reprocessing same jobs

## PR #1161: Initiative Rate Limit + Stage Backfill

- Rate limit raised 40 -> 100 initiatives per auto-progression run
- Stage backfill batch size 50 -> 200, frequency every 15 min

## PR #1162: ImageAgent Persistence + Audit Update

- First agent to get `_save_to_deliverable()` — established the pattern
- Updated disconnected dots audit status in entry point

## PR #1163: Agent Output Persistence Batch 1 (6 agents)

- VideoAgent, AudioAgent, ThreeDAgent, CodeGeneratorAgent, CodeReviewAgent, EditorAgent
- All persist to `Deliverable` model via `BaseAgent._save_to_deliverable()`

## PR #1164: Enrichment Truncation Fix

Three truncation points were causing 85-95% data loss before enrichment reached the LLM:
- `ENRICHMENT_CAPS` per-section: raised from 300-600 -> 1000-2000 chars
- `max_context_chars` overall: raised from 3,000 -> 12,000
- Tool result cap: raised from 3,000 -> 8,000

## PR #1165: Legacy Route Link Updates (21 links in 10 files)

Updated hardcoded legacy paths to new workspace routes:
- `/body-health` -> `/workspace?tab=system`
- `/content-channels` -> `/workspace?tab=content`
- `/spiders` -> `/workspace?tab=dataintel`
- `/blogs` -> `/workspace?tab=content`
- `/llm-routing` removed from nav store

Files: HumanPage, HeartWidget, WorkspacePage, AssistantPage, AdminPage, EntityLink, navigationStore, GlobalAlertBanner, BlogViewerPage, LiveMetricsDashboard

## PR #1166: Agent Output Persistence Batch 2 (4 agents)

- ContentWriterAgent, FullStackDeveloperAgent, ImageEditingAgent, VideoEditingAgent

## PR #1167: Remove Legacy Redirects + Persistence Batch 3 (6 agents)

- Removed 25 `<Navigate>` redirect routes from `App.tsx` (added Feb 8, Session 971b)
- Route count: 37 -> 24 (21 pages + 3 redirects)
- BullCaseAgent, BearCaseAgent, ArbitrageDetector, SportsOddsAnalyst, SEOOptimizerAgent, SocialMediaAgent

## PR #1168: Agent Persistence Final Batch (13 agents)

- BrandIdentityAgent, BrandStrategyAgent, ContentStrategyAgent
- ContrarianAgent, PerformanceAnalystAgent, TopicMinerAgent, VoiceCriticAgent
- TrendBreakDetectorAgent, TransactionMonitorAgent
- MarketMovementMonitorAgent, InstitutionalWatcherAgent
- PredictionMarketAnalyst, GamePredictor, LineMovementAnalyzer, SharpActionDetector

**Total: 30 agents now persist to Deliverable** (was 0 before Session 1006)

---

## Agent Persistence Audit — Final Status

### Agents WITH `_save_to_deliverable()` (30 total)

| PR | Agents |
|----|--------|
| #1162 | ImageAgent |
| #1163 | VideoAgent, AudioAgent, ThreeDAgent, CodeGeneratorAgent, CodeReviewAgent, EditorAgent |
| #1164 | (enrichment fix, not agents) |
| #1166 | ContentWriterAgent, FullStackDeveloperAgent, ImageEditingAgent, VideoEditingAgent |
| #1167 | BullCaseAgent, BearCaseAgent, ArbitrageDetector, SportsOddsAnalyst, SEOOptimizerAgent, SocialMediaAgent |
| #1168 | BrandIdentityAgent, BrandStrategyAgent, ContentStrategyAgent, ContrarianAgent, PerformanceAnalystAgent, TopicMinerAgent, VoiceCriticAgent, TrendBreakDetectorAgent, TransactionMonitorAgent, MarketMovementMonitorAgent, InstitutionalWatcherAgent, PredictionMarketAnalyst, GamePredictor, LineMovementAnalyzer, SharpActionDetector |

### Agents WITHOUT `_save_to_deliverable()` (skipped intentionally)

- **MarketingStrategyAgent, ContentStrategyAgent (business), CustomerResearchAgent** — inherit from `BaseBusinessResearchAgent`, don't override `execute()`. Requires parent class edit.
- **Programmatic agents** (content_executor, opportunity_pipeline, workflow_orchestration, workflow_agent) — no user-facing output to persist.
- **Coordinator agents** (SportsBettingCoordinator, BlockchainAuditCoordinator, etc.) — persist via their own model (SportsBettingBrief, BlockchainAuditBrief).

---

## Disconnected Dots Audit — Updated Status

| Item | Status |
|------|--------|
| Agent output persistence | **CLOSED** — 30/30 applicable agents done |
| Enrichment data truncation | **FIXED** (PR #1164) |
| Legacy route redirects | **REMOVED** (PR #1167) |
| Legacy route links | **UPDATED** (PR #1165) |
| "8 orphaned services" | **RESOLVED** — 7/8 actively used, 1 already deprecated |
| "6 empty model tables" | **RESOLVED** — only PodcastShow + Campaign truly empty |
| 87+ orphan API endpoints | **OPEN** — still needs audit |
| Decision execution wiring | **CLOSED** — fully wired (DecisionEnforcerAgent + ConversationOrchestrator) |

---

## Files Modified

| File | Change |
|------|--------|
| `core/agents/image_agent.py` | `_save_to_deliverable()` |
| `core/agents/video_agent.py` | `_save_to_deliverable()` |
| `core/agents/audio_agent.py` | `_save_to_deliverable()` |
| `core/agents/three_d_agent.py` | `_save_to_deliverable()` |
| `core/agents/code_generator_agent.py` | `_save_to_deliverable()` |
| `core/agents/code_review_agent.py` | `_save_to_deliverable()` |
| `core/agents/editor_agent.py` | `_save_to_deliverable()` |
| `core/agents/content_writer_agent.py` | `_save_to_deliverable()` |
| `core/agents/fullstack_developer_agent.py` | `_save_to_deliverable()` |
| `core/agents/image_editing_agent.py` | `_save_to_deliverable()` |
| `core/agents/video_editing_agent.py` | `_save_to_deliverable()` |
| `core/agents/stocks/bull_case_agent.py` | `_save_to_deliverable()` |
| `core/agents/stocks/bear_case_agent.py` | `_save_to_deliverable()` |
| `core/agents/stocks/market_movement_monitor_agent.py` | `_save_to_deliverable()` |
| `core/agents/stocks/institutional_watcher_agent.py` | `_save_to_deliverable()` |
| `core/agents/markets/arbitrage_detector.py` | `_save_to_deliverable()` |
| `core/agents/markets/sports_odds_analyst.py` | `_save_to_deliverable()` |
| `core/agents/markets/prediction_market_analyst.py` | `_save_to_deliverable()` |
| `core/agents/markets/game_predictor.py` | `_save_to_deliverable()` |
| `core/agents/markets/line_movement_analyzer.py` | `_save_to_deliverable()` |
| `core/agents/markets/sharp_action_detector.py` | `_save_to_deliverable()` |
| `core/agents/strategy/seo_optimizer_agent.py` | `_save_to_deliverable()` |
| `core/agents/strategy/social_media_agent.py` | `_save_to_deliverable()` |
| `core/agents/strategy/brand_identity_agent.py` | `_save_to_deliverable()` |
| `core/agents/strategy/content_strategy_agent.py` | `_save_to_deliverable()` |
| `core/agents/business/brand_strategy_agent.py` | `_save_to_deliverable()` |
| `core/agents/content/contrarian_agent.py` | `_save_to_deliverable()` |
| `core/agents/content/performance_analyst_agent.py` | `_save_to_deliverable()` |
| `core/agents/content/topic_miner_agent.py` | `_save_to_deliverable()` |
| `core/agents/content/voice_critic_agent.py` | `_save_to_deliverable()` |
| `core/agents/narrative/trend_break_detector_agent.py` | `_save_to_deliverable()` |
| `core/agents/blockchain/transaction_monitor_agent.py` | `_save_to_deliverable()` |
| `core/services/unified_pa_entrypoint.py` | Enrichment caps raised |
| `core/services/pa_intelligence_enricher.py` | max_context_chars 3k->12k |
| `frontend/src/App.tsx` | 25 legacy redirects removed |
| 10 frontend files | 21 legacy links updated |
