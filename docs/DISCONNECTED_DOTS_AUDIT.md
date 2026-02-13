# Disconnected Dots Audit

**Session 972 | February 8, 2026**
**Method:** 5 parallel code-analysis agents swept the entire codebase

This document catalogs every significant case where something was built but not fully connected — dead wires, dropped context, orphan endpoints, and missing integrations. Use it as a work queue.

---

## Table of Contents

1. [PA Pipeline Dead Wires](#1-pa-pipeline-dead-wires)
2. [Enrichment Data Loss (85-95%)](#2-enrichment-data-loss)
3. [Frontend-API Disconnects](#3-frontend-api-disconnects)
4. [Orphan API Endpoints (~200+)](#4-orphan-api-endpoints)
5. [Agent Output Persistence Gap](#5-agent-output-persistence-gap)
6. [Models With No API Exposure](#6-models-with-no-api-exposure)
7. [Celery Task Gaps](#7-celery-task-gaps)
8. [Feedback Loop Breaks](#8-feedback-loop-breaks)
9. [Priority Matrix](#9-priority-matrix)

---

## 1. PA Pipeline Dead Wires

These are places in the PA where data is collected but the last wire is never connected.

### 1A. Blog Quality Metrics Never Displayed

| What | Where |
|------|-------|
| **Fetched** | `tool_dispatcher.py:1786-1838` — `avg_quality`, `avg_novelty`, `avg_structure`, `publish_ready_count` |
| **Dropped at** | `unified_pa_entrypoint.py:1616-1632` — stats formatter only shows `ready_for_review`, `drafts`, `published` counts |
| **Impact** | PA tells user to "compare novelty vs structure scores" but never shows those scores |
| **Fix** | Add `avg_quality`, `avg_novelty`, `avg_structure` to stats response formatter |

### 1B. Blog Detail Fields Never Shown

| What | Where |
|------|-------|
| **Fetched** | `tool_dispatcher.py:1859-1874` — `gate_notes`, `tone`, `word_count`, `publish_ready` |
| **Dropped at** | `unified_pa_entrypoint.py:1634-1652` — details formatter ignores these fields |
| **Impact** | Editorial feedback (`gate_notes`) and tone never reach the user |
| **Fix** | Add `gate_notes`, `tone`, `word_count` to the details response formatter |

### 1C. Knowledge Injector Only Works for Direct Responses

| What | Where |
|------|-------|
| **Built at** | `unified_pa_entrypoint.py:505-511` — `context['system_knowledge']` populated |
| **Used at** | `unified_pa_entrypoint.py:2382-2387` — only in `_generate_direct_response()` |
| **Dropped for** | All tool-based responses (the majority of PA interactions) |
| **Impact** | When PA uses a tool, workspace/health/agent knowledge is invisible to the LLM |
| **Fix** | Also inject `format_for_prompt()` output in tool-based analytical prompts |

### 1D. Strategic Memory Only Fires for 'reasoning' Intent

| What | Where |
|------|-------|
| **Defined** | `unified_pa_entrypoint.py:1150-1161` — strategic memory enrichment |
| **Mapped to** | Only `'reasoning'` in `INTENT_ENRICHMENT_MAP` (line 93) |
| **Impact** | Content review, initiatives, boardroom, opportunities never get strategic memory |
| **Fix** | Add `'strategic_memory'` to more intents in `INTENT_ENRICHMENT_MAP` |

### 1E. Learning Insights Mislabeled as System Brief

| What | Where |
|------|-------|
| **Built** | `pa_learning_insights.py:379-439` — rich learning summary with pilots and predictions |
| **Stored as** | `sections['system_brief']` in `_enrich_tool_result()` (line 1110) |
| **Impact** | Learning data gets mixed with system status instead of being clearly labeled |
| **Fix** | Store as `sections['learning_insights']` with its own section header |

---

## 2. Enrichment Data Loss

Every enrichment service builds rich structured data, but consumers only extract a single text field. This is the biggest systemic issue.

### Data Loss Summary

| Service | Keys Produced | Keys Consumed | Loss |
|---------|--------------|---------------|------|
| PA Intelligence Enricher | 8 keys (knowledge, experts, dreams, policies, spider_trends, system_state, platform_briefing, learning_insights) | 1 (`context_text`) | ~88% |
| Spider Context Builder | 11 keys (relevant_trends, discussions, articles, market_data, creative_trends, job_data, data_sources, freshness, summary, has_data, categories_queried) | 1 (`summary`) | ~91% |
| Advisor Context Builder | 7 keys (relevant_advisors, advisor_insights, decision_frameworks, key_principles, recommended_approach, summary, has_advice) | 1 partial (`key_principles[:3]`) | ~86% |
| Domain Content Context | Multi-domain structured data | 1 formatted string | ~95% |
| Blog Performance Context | 10+ metric fields + learning rules + engagement data | 1 formatted string | ~90% |
| Signal Aggregation | 15-field cluster objects (strength, confidence, novelty, urgency, keywords, sample_signals) | 3-4 fields (keywords[:3], pattern_type, first sample) | ~75% |

### Root Cause

The pattern is always the same:
1. Service builds `result = { 'structured_data': [...], 'metadata': {...}, 'summary': '...' }`
2. Consumer does `text = result.get('summary', '')` or `text = result.get('context_text', '')`
3. Everything else is discarded

### What's Lost

- **Spider market_data** — crypto prices, stock changes with percentages
- **Spider job_data** — job categories, top companies, salary ranges
- **Advisor decision_frameworks** — named strategic frameworks
- **Advisor recommended_approach** — synthesized multi-advisor recommendation
- **Intelligence enricher metadata** — source counts, intent classification, urgency flags
- **Signal cluster scores** — strength, confidence, novelty (0-1 floats, calculated but never used downstream)
- **Blog performance per-topic breakdowns** — top/weak topics with avg scores

---

## 3. Frontend-API Disconnects

### Pages That Permanently Show Empty States

| Page | Fetches | Shows | Reason |
|------|---------|-------|--------|
| **BillingPage** | 6 Stripe endpoints (plans, status, payment methods, invoices, usage, upcoming) | "No plans available", "No payment methods on file", "No invoices yet" | No seeded data / no real Stripe integration |
| **DistributionPage** | 8 distribution endpoints (stats, platforms, accounts, content, revenue, recommendations, compare, scheduled) | "No distributions yet", "No platforms connected" | All endpoints return empty arrays |
| **PortfolioPage** | 5 portfolio endpoints (recommendations, comparisons, integrations, analytics, content) | "No recommendations yet", "No comparison data yet" | No data providers |

### Workspace Tabs with Shallow Integration

These tabs exist in the workspace but have minimal actual API integration:
- **CareerTab** — shell exists but limited data flow
- **VoiceMarketplaceTab** — UI present but backend integration thin
- **TriggersTab** — trigger management UI with limited real triggers

---

## 4. Orphan API Endpoints

These backend endpoints exist in `core/urls.py` but have **no frontend consumer**.

### Project Intelligence (7 endpoints)
```
api/projects/<id>/intelligence/
api/projects/<id>/intelligence/learning/
api/projects/<id>/intelligence/conversations/
api/projects/<id>/intelligence/dreams/
api/projects/<id>/intelligence/boardroom/
api/projects/<id>/intelligence/spiders/
api/projects/<id>/intelligence/slack/
```

### User Learning System (8 endpoints, Session 930)
```
api/user-learning/feedback/
api/user-learning/effectiveness/<agent_id>/
api/user-learning/goals/
api/user-learning/goals/<id>/progress/
api/user-learning/skills/
api/user-learning/skills/growth/
api/user-learning/profile-completeness/
api/user-learning/profile-next-question/
```

### ATS / Resume System (6 endpoints, Session 866)
```
api/ats/analyze/
api/ats/extract-keywords/
api/ats/optimize/
api/ats/templates/
api/ats/generate-summary/
api/ats/stats/
```

### Opportunity Engine (6 endpoints, Sessions 223-224)
```
api/opportunities/
api/opportunities/top/
api/opportunities/stats/
api/opportunities/<id>/
api/opportunities/<id>/act/
api/opportunities/<id>/rescore/
```

### Business Ideas Pipeline (5 endpoints, Session 338)
```
api/business-ideas/
api/business-ideas/list/
api/business-ideas/stats/
api/business-ideas/<id>/
api/business-ideas/<id>/generate-assets/
```

### Team & Workflow APIs (8+ endpoints, Sessions 227-228)
```
api/teams/ (CRUD)
api/teams/messages/
api/teams/workflows/
```

### Proactive System (8+ endpoints, Session 234)
```
api/proactive/alerts/
api/proactive/notifications/
api/proactive/suggestions/
api/proactive/automations/
```

### Memory & Strategic APIs (Session 962)
```
api/memory/precedents/
api/memory/failures/
api/memory/strategy/
```

### Content Calendar (5+ endpoints, Sessions 628-632)
```
api/content-calendar/
api/content-calendar/upcoming/
api/content-calendar/history/
api/content-calendar/reschedule/
api/content-calendar/generate/
```

### Learning Loop Endpoints (Sessions 232, 954)
```
api/learning/dashboard/
api/learning/patterns/
api/learning/insights/
api/learning/loop/stats/
api/learning/loop/track/
api/rag/observability/ (multiple)
```

**Total: ~200+ orphan endpoints**

---

## 5. Agent Output Persistence Gap

### Finding: 76 agents exist, but only ~3 persist their outputs

| Category | Persists Output | Details |
|----------|----------------|---------|
| **ContentWriterAgent** | Yes | Saves to `Deliverable` via `_wrap_output_as_deliverable()` |
| **CampaignOrchestratorAgent** | Yes | Saves to `CampaignDeliverable` |
| **BaseAgent** | Optional | Has `_wrap_output_as_deliverable()` but most subclasses don't call it |
| **73 other agents** | No | `execute()` returns `AgentResult`, caller discards it |

### Agents Whose Output Vanishes

- **ResearchAgent** — research data discarded after display
- **ImageAgent, VideoAgent, AudioAgent, ThreeDAgent** — creation outputs lost
- **TrendAnalysisAgent** — market analysis gone after response
- **CompetitorAnalysisAgent** — competitive intelligence not captured
- **DecisionEnforcerAgent** — has `DecisionRecord` model but wiring incomplete
- **StockAuditCoordinator, BlockchainAuditCoordinator** — audit reports discarded
- **PodcastCoordinatorAgent** — production records lost (Session 994: user context now passed, attribution fixed)
- **CodeGeneratorAgent, FullStackDeveloperAgent** — code generation not saved

### Impact

- No persistent audit trail of agent work products
- Learning loops can't reference past outputs
- No way to build a portfolio of agent work
- Cannot replay or debug agent decisions

---

## 6. Models With No API Exposure

These Django models exist and contain data, but have no serializers or ViewSets to read them through the API.

| Model | Purpose | API Status |
|-------|---------|------------|
| `DecisionRecord` | Agent decisions | No read API |
| `ToolCallRecord` | Tool call audit trail | Auto-recorded, not queryable |
| `SignalCluster` | Signal intelligence patterns | No direct query API |
| `AutoTopic` | Auto-generated conversation topics | No read endpoint |
| `ReportProvenance` | Data source tracking | Not exposed |
| `LearningBackup` | Learning data persistence | Not accessible |
| `HumanFeedbackRecord` | User feedback on outputs | Recorded but feedback loop broken |
| `AgentDecisionSummary` | Decision summaries | Not queryable by agents |

---

## 7. Celery Task Gaps

- **319** `@shared_task` definitions in `core/tasks.py`
- **270** tasks in `beat_schedule`
- **~49** tasks defined but never scheduled or called via `.delay()`

Notable: Some tasks reference services that have been renamed or restructured.

---

## 8. Feedback Loop Breaks

### FeedbackProcessor (Session 861)

`core/services/feedback_processing.py` contains a `FeedbackProcessor` class that:
- Processes `HumanFeedbackRecord` via Django signal handlers
- Converts positive feedback (4-5 stars) to reinforcement learning records
- Converts negative feedback (1-2 stars) to improvement triggers

**Status:** Signal handler is registered but feedback records are sparse because the UI thumbs-up/thumbs-down buttons don't consistently create `HumanFeedbackRecord` entries.

### Blog Quality Feedback Loop (Session 886)

`BlogPerformanceContextBuilder` injects past quality scores into `ContentWriterAgent` prompts so the agent "knows" its strengths/weaknesses. **This works**, but the quality scores themselves aren't surfaced to users (see Section 1A).

### Experiment Learning Loop

`ExperimentLearningLoop` tracks A/B test outcomes with 251 learnings and 29 decision patterns. **This works** autonomously. However, the results feed into agent prompts but are **not visible in the UI** — users can't see what the system has learned.

---

## 9. Priority Matrix

### Tier 1 — High Impact, Low Effort (wire existing code)

| # | Fix | Files | Est. Lines |
|---|-----|-------|-----------|
| 1 | Wire blog quality metrics into PA stats response | `unified_pa_entrypoint.py` | ~15 |
| 2 | Wire blog gate_notes/tone into PA details response | `unified_pa_entrypoint.py` | ~10 |
| 3 | Inject knowledge context into tool-based responses (not just direct) | `unified_pa_entrypoint.py` | ~10 |
| 4 | Label learning insights separately from system_brief | `unified_pa_entrypoint.py` | ~5 |
| 5 | Add strategic_memory to more intents in INTENT_ENRICHMENT_MAP | `unified_pa_entrypoint.py` | ~5 |

### Tier 2 — Medium Impact, Medium Effort (connect existing systems)

| # | Fix | Scope |
|---|-----|-------|
| 6 | Have BaseAgent always save output to Deliverable (opt-out, not opt-in) | `core/agents/base_agent.py` + test |
| 7 | Add API ViewSets for DecisionRecord, ToolCallRecord, SignalCluster | New serializers + views |
| 8 | Surface experiment learning results in UI (Data & Intel tab) | Frontend component + API hook |
| 9 | Wire HumanFeedbackRecord creation consistently from UI buttons | Frontend + API |
| 10 | Expose enrichment structured data (not just summary strings) to PA prompts | Multiple enrichment services |

### Tier 3 — Strategic Cleanup (reduce dead weight)

| # | Fix | Scope |
|---|-----|-------|
| 11 | Audit 200+ orphan API endpoints — remove or wire to UI | `core/urls.py` + frontend |
| 12 | Remove or connect BillingPage / DistributionPage / PortfolioPage empty states | Frontend pages |
| 13 | Clean up ~49 unscheduled Celery tasks | `core/tasks.py` |
| 14 | Remove deprecated `_deprecated/decision_executor.py` | File deletion |

---

*Generated by 5 parallel code-analysis agents scanning the full codebase. To update, re-run the audit.*
