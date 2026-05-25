<!-- DOC-POINTER-V2 (Session 1143) -->
> **Status:** Superseded
> **Last verified:** Session 1143 (2026-05-25)
> **Current canon:** [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) (runtime-derived, autogen) + [`docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md) (narrative) + [`docs/topics/*`](../topics/) (subsystem deep-dives).
> **Change reason:** Early visual system map. Superseded by current architecture docs + topics/*.
> **Preserved because:** historical "reality score" / system-overview snapshot. Useful as build-history record; do NOT cite for current state.

# SYSTEM ARCHITECTURE MAP
## Visual Guide to Unified Donkey Betz Platform

---

## HIGH-LEVEL SYSTEM OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│                    UNIFIED DONKEY BETZ PLATFORM                 │
│                  18-Month AI-Human Collaboration                │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  INTELLIGENCE │    │   EXECUTION   │    │  PRESENTATION │
│    LAYER      │───▶│     LAYER     │───▶│     LAYER     │
│  (Spiders)    │    │   (Agents)    │    │  (Frontend)   │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        │                     ▼                     │
        │            ┌───────────────┐              │
        └───────────▶│   LEARNING    │◀─────────────┘
                     │     LAYER     │
                     │  (Bridges)    │
                     └───────────────┘
                              │
                              ▼
                     ┌───────────────┐
                     │  PERSISTENCE  │
                     │    LAYER      │
                     │  (Database)   │
                     └───────────────┘
```

---

## INTELLIGENCE LAYER (Data Collection)

### Spider Army Architecture

```
┌────────────────────────────────────────────────────────┐
│          SPIDER ARMY ORCHESTRATOR                      │
│    /ai_core/spiders/spider_army_orchestrator.py        │
└────────────────────────────────────────────────────────┘
                      │
                      │ coordinates
                      ▼
┌────────────────────────────────────────────────────────┐
│              SPIDER REGISTRY                           │
│       /ai_core/spiders/spider_registry.py              │
│                                                        │
│  Registered Spiders: 48                                │
│  ✅ Implemented: 23    ⚠️ Placeholder: 25              │
│  ❌ Unregistered: 2 (CoinGecko, Yahoo Finance)         │
└────────────────────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐
│  FINANCIAL   │ │FREELANCE │ │ CONTENT  │
│   SPIDERS    │ │ SPIDERS  │ │ SPIDERS  │
│              │ │          │ │          │
│ • Financial  │ │• Toptal  │ │• Medium  │
│ • Innovation │ │• Guru    │ │• Gumroad │
│ • Market     │ │• PPH     │ │• Substack│
│ • News       │ │• FlexJob │ │• Patreon │
│ • Social     │ │• RemoteOK│ │• Ko-fi   │
│ ❌CoinGecko  │ │• 99Design│ │• ProdHunt│
│ ❌YahooFin   │ │          │ │          │
└──────────────┘ └──────────┘ └──────────┘
        │             │             │
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐
│   SPORTS     │ │  LEGAL   │ │   TECH   │
│   SPIDERS    │ │ SPIDERS  │ │ SPIDERS  │
│              │ │          │ │          │
│ • Horse Race │ │• CourtLis│ │• HuggFace│
│ • Combat     │ │• Justia  │ │• Kaggle  │
│              │ │• FindLaw │ │• GitHub  │
│              │ │• LII     │ │• StackOvr│
└──────────────┘ └──────────┘ └──────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
                      ▼
              ┌───────────────┐
              │ SPIDER DATA   │
              │   STORAGE     │
              │  (Database)   │
              └───────────────┘
```

### Missing Connections ❌
- CoinGecko spider exists but not registered
- Yahoo Finance spider exists but not registered

---

## EXECUTION LAYER (AI Agents)

### Agent System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  AGENT DATABASE                         │
│            /agents/models.py                            │
│        UnifiedAgentTemplate Model                       │
│                                                         │
│        Stores: 196 agent configurations                 │
└─────────────────────────────────────────────────────────┘
                      │
                      │ loads from DB
                      ▼
┌─────────────────────────────────────────────────────────┐
│            UNIVERSAL AGENT LOADER                       │
│    /ai_core/agents/universal_agent_loader.py            │
│                                                         │
│  Dynamically creates agent classes from DB templates    │
│  + Hardcoded specialized agents                         │
│                                                         │
│  ✅ Loaded: ~165 agents                                 │
│  ❌ Orphaned: 11 specialized agents not imported        │
└─────────────────────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐
│ AI ENFORCED  │ │   LLM    │ │ CONCRETE │
│    BASE      │→│INTEGRATION│→│ EXECUTOR │
│              │ │          │ │          │
│ • Base class │ │• OpenAI  │ │• Async   │
│ • Common API │ │• Anthropic│ │  exec    │
│ • Learning   │ │• Mock    │ │• Sync    │
│   context    │ │          │ │  exec    │
└──────────────┘ └──────────┘ └──────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              AGENT CATEGORIES (207 total)               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  DATABASE-GENERATED AGENTS (196):                       │
│  • Financial advisors                                   │
│  • Content creators                                     │
│  • Job matchers                                         │
│  • Market analysts                                      │
│  • Sports predictors                                    │
│  • And 190 more specialized agents                      │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  HARDCODED SPECIALIZED AGENTS (11 loaded + 11 orphaned):│
│                                                         │
│  ✅ LOADED (working):                                   │
│  • RealContentCreatorAgent                              │
│  • ZeroCapitalIncomeGenerator                           │
│  • ContentMarketplaceAgent                              │
│                                                         │
│  ❌ ORPHANED (exist but not loaded):                    │
│  • UltimateMoneyMachine                                 │
│  • AffiliateMarketingEmpire                             │
│  • RealClientAcquisition                                │
│  • RealPaymentProcessor                                 │
│  • RealWorkDeliveryEngine                               │
│  • RealJobExecutor                                      │
│  • RealTaskExecutor                                     │
│  • AutomatedJobBot                                      │
│  • IntelligentJobMatcher                                │
│  • FreelancePipeline                                    │
│  • JobApplicationAgent                                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Agent Orchestration (Multiple Implementations ⚠️)

```
┌────────────────────────────────────────────────┐
│         AGENT ORCHESTRATION SYSTEMS            │
│        (NEEDS CONSOLIDATION)                   │
├────────────────────────────────────────────────┤
│                                                │
│  Implementation #1:                            │
│  /ai_core/agents/agent_orchestration_layer.py  │
│  Status: ⚠️ Unclear if used                    │
│                                                │
│  Implementation #2:                            │
│  /intelligence/agent_execution_pipeline.py     │
│  Status: ⚠️ Seems production-ready             │
│                                                │
│  Implementation #3:                            │
│  /core/views_agent_orchestration.py            │
│  Status: ⚠️ Handles web requests               │
│                                                │
│  RECOMMENDATION: Consolidate to single system  │
│                                                │
└────────────────────────────────────────────────┘
```

---

## LEARNING LAYER (Continuous Improvement)

### Learning Bridge Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  BASE LEARNING BRIDGE                   │
│        /core/learning_bridges/base.py                   │
│                                                         │
│  Abstract base class for all learning bridges           │
└─────────────────────────────────────────────────────────┘
                      │
                      │ inherited by
                      ▼
┌─────────────────────────────────────────────────────────┐
│           11 SPECIALIZED LEARNING BRIDGES               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ✅ agent_execution_bridge.py                           │
│     • Learns from agent task completions                │
│     • Tracks success/failure patterns                   │
│     • Status: INTEGRATED ✅                              │
│                                                         │
│  ✅ spider_data_bridge.py                               │
│     • Learns from spider data quality                   │
│     • Identifies high-value data sources                │
│     • Status: INTEGRATED ✅                              │
│                                                         │
│  ✅ revenue_attribution_bridge.py                       │
│     • Tracks which systems generate revenue             │
│     • Learns ROI of different agents/spiders            │
│     • Status: INTEGRATED (needs more data sources) ⚠️   │
│                                                         │
│  ✅ sports_betting_bridge.py                            │
│     • Learns from betting outcomes                      │
│     • Improves prediction accuracy                      │
│     • Status: INTEGRATED ✅                              │
│                                                         │
│  ⚠️ application_outcome_bridge.py                       │
│     • Learns from job application results               │
│     • Status: INTEGRATION UNCLEAR                       │
│                                                         │
│  ⚠️ advisor_feedback_bridge.py                          │
│     • Learns from user feedback on advice               │
│     • Status: INTEGRATION UNCLEAR                       │
│                                                         │
│  ⚠️ collaboration_bridge.py                             │
│     • Learns from agent-agent collaboration             │
│     • Status: INTEGRATION UNCLEAR                       │
│                                                         │
│  ⚠️ personalization_bridge.py                           │
│     • Learns user preferences                           │
│     • Status: INTEGRATION UNCLEAR                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
                      │
                      │ writes to
                      ▼
┌─────────────────────────────────────────────────────────┐
│              LEARNING ENTRY MODEL                       │
│          /intelligence/models.py                        │
│                                                         │
│  Stores all learning data for agent improvement         │
└─────────────────────────────────────────────────────────┘
```

---

## PRESENTATION LAYER (Frontend)

### WebSocket Real-Time Communication

```
┌─────────────────────────────────────────────────────────┐
│                 WEBSOCKET ROUTING                       │
│              /core/routing.py                           │
│                                                         │
│         60+ registered WebSocket routes                 │
└─────────────────────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐
│   REVENUE    │ │  INCOME  │ │  SPORTS  │
│  DASHBOARD   │ │ BUILDER  │ │   HUB    │
│              │ │          │ │          │
│ • Live $     │ │• Opps    │ │• Odds    │
│ • Tracking   │ │• Agents  │ │• Predict │
│ • History    │ │• Spider  │ │• Results │
│              │ │  data    │ │          │
└──────────────┘ └──────────┘ └──────────┘
        │             │             │
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐
│   NEURAL     │ │ PERSONAL │ │ COMMAND  │
│  ORCHESTRA   │ │ASSISTANT │ │  CENTER  │
│              │ │          │ │          │
│ • Agent      │ │• Chat    │ │• Control │
│   status     │ │• Context │ │• Monitor │
│ • Tasks      │ │• Learn   │ │• Manage  │
│              │ │          │ │          │
└──────────────┘ └──────────┘ └──────────┘
```

### View Layer (72 View Files)

```
┌─────────────────────────────────────────────────────────┐
│                    VIEW CATEGORIES                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  CORE UNIFIED VIEWS (Production):                       │
│  • views_unified.py                                     │
│  • views_unified_backend.py                             │
│  • views_unified_intelligence.py                        │
│  • views_real_income_builder.py                         │
│  • views_odds_sports.py                                 │
│                                                         │
│  REVENUE VIEWS:                                         │
│  • views_revenue.py                                     │
│  • views_revenue_tracking.py                            │
│                                                         │
│  AGENT VIEWS:                                           │
│  • views_agent_orchestration.py                         │
│  • views_agent_work_platform.py                         │
│  • views_agent_dashboard.py                             │
│                                                         │
│  CONTENT VIEWS:                                         │
│  • views_content.py                                     │
│  • views_image.py                                       │
│  • views_video.py                                       │
│                                                         │
│  LEARNING VIEWS:                                        │
│  • views_learning_dashboard.py                          │
│  • views_learning_path.py                               │
│  • views_ai_learning_api.py                             │
│                                                         │
│  ASSISTANT VIEWS (Multiple implementations ⚠️):         │
│  • views_personal_assistant.py                          │
│  • views_assistant_intelligent.py                       │
│  • views_assistant_rag_enhanced.py                      │
│  • views_assistant_minimal.py                           │
│  • views_assistant_bypass.py                            │
│  → NEEDS CONSOLIDATION                                  │
│                                                         │
│  And 50+ more specialized view files...                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## PERSISTENCE LAYER (Database)

### Core Models

```
┌─────────────────────────────────────────────────────────┐
│                   DATABASE MODELS                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  CORE:                                                  │
│  • UnifiedBaseModel (abstract base)                     │
│  • UnifiedUser (extended auth)                          │
│                                                         │
│  AGENTS:                                                │
│  • UnifiedAgentTemplate (196 agents stored here)        │
│                                                         │
│  INTELLIGENCE:                                          │
│  • Opportunity (income opportunities)                   │
│  • Revenue ($ tracking)                                 │
│  • ActionPlan (strategic planning)                      │
│  • LearningEntry (learning data)                        │
│                                                         │
│  SPORTS:                                                │
│  • Prediction models                                    │
│  • Odds tracking                                        │
│  • Results history                                      │
│                                                         │
│  CONTENT:                                               │
│  • Document (knowledge base)                            │
│  • DocumentEmbedding (RAG/semantic search)              │
│                                                         │
│  SELF-AWARENESS (⚠️ unclear integration):               │
│  • Self-awareness system models                         │
│                                                         │
│  MYTHOLOGY (⚠️ unclear integration):                    │
│  • Content validation models                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## BACKGROUND PROCESSING (Celery)

### Current State ⚠️ UNDERUTILIZED

```
┌─────────────────────────────────────────────────────────┐
│                  CELERY TASKS                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ✅ REGISTERED:                                         │
│  • isolate_documents_batch()                            │
│    (Document namespace isolation)                       │
│                                                         │
│  ❌ SHOULD BE CELERY BUT AREN'T:                        │
│  • Spider data collection (sync)                        │
│  • Agent execution (mostly sync)                        │
│  • LLM API calls (blocking)                             │
│  • Revenue opportunity scanning                         │
│  • Learning system updates                              │
│  • Email/notification sending                           │
│  • Report generation                                    │
│  • Data aggregation                                     │
│                                                         │
│  RECOMMENDATION: Convert 15+ operations to background   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## DATA FLOW EXAMPLE: Spider → Agent → Revenue

### Complete Pipeline

```
1. SPIDER COLLECTS DATA
   ↓
   Medium Spider finds viral article opportunity
   {
     title: "AI Tools That Made Me $10k",
     engagement: 95,000 views,
     estimated_earnings: $850
   }
   ↓

2. SPIDER DATA BRIDGE (Learning)
   ↓
   Learns: "Medium articles about AI tools = high value"
   Stores in LearningEntry model
   ↓

3. OPPORTUNITY CREATED
   ↓
   Intelligence.Opportunity model stores opportunity
   ↓

4. AGENT EXECUTOR TRIGGERED
   ↓
   ContentCreatorAgent loads learned context
   Sees: "AI tool articles perform well on Medium"
   ↓

5. AGENT GENERATES CONTENT
   ↓
   Uses LLM (OpenAI/Anthropic) with learned context
   Creates AI productivity article
   ↓

6. AGENT EXECUTION BRIDGE (Learning)
   ↓
   Learns: "ContentCreator + Medium = successful execution"
   ↓

7. REVENUE TRACKED (⚠️ INCOMPLETE)
   ↓
   Revenue model SHOULD record:
   {
     source: "medium_partner_program",
     amount: $850,
     agent: "ContentCreatorAgent",
     opportunity_id: <opportunity_id>
   }
   ↓

8. REVENUE ATTRIBUTION BRIDGE (Learning)
   ↓
   Learns: "ContentCreator → Medium → $850 revenue"
   Future agents prioritize high-revenue sources
   ↓

9. FRONTEND DISPLAY
   ↓
   WebSocket pushes update to Revenue Dashboard
   User sees real-time $ earned
   ↓

10. FUTURE OPTIMIZATION
    ↓
    System learns to prioritize:
    • High-engagement topics (AI tools)
    • High-revenue platforms (Medium)
    • Successful agent-platform combinations
```

### Current Status of This Pipeline

```
✅ Steps 1-6: WORKING
⚠️ Step 7: INCOMPLETE (revenue tracking not connected to all spiders)
⚠️ Step 8: UNCLEAR (revenue attribution bridge needs verification)
✅ Step 9: WORKING (WebSocket displays revenue)
⚠️ Step 10: PARTIAL (learning works but needs complete data)
```

---

## KEY INTEGRATION GAPS

### 1. Spider Registration Gaps

```
ISSUE: 2 spiders built but not registered

┌──────────────────┐         ┌──────────────────┐
│  CoinGecko       │    ❌   │ Spider Registry  │
│  Spider          │────X────│                  │
│  (exists)        │  not    │ spider_registry  │
└──────────────────┘  added  │     .py          │
                              └──────────────────┘
┌──────────────────┐
│  Yahoo Finance   │    ❌
│  Spider          │────X────
│  (exists)        │  not
└──────────────────┘  added

FIX: Add 6 lines to spider_registry.py
```

### 2. Agent Loading Gaps

```
ISSUE: 11 specialized agents exist but not loaded

┌──────────────────┐         ┌──────────────────┐
│  Ultimate        │    ❌   │ Universal Agent  │
│  Money Machine   │────X────│     Loader       │
│  (exists)        │  not    │                  │
└──────────────────┘  loaded └──────────────────┘

┌──────────────────┐
│  Affiliate       │    ❌
│  Marketing       │────X────
│  Empire          │  not
└──────────────────┘  loaded

... and 9 more

FIX: Add imports to universal_agent_loader.py
```

### 3. Revenue Attribution Gaps

```
ISSUE: Spiders → Revenue tracking incomplete

┌──────────────┐         ┌──────────────┐
│ Medium       │    ⚠️   │   Revenue    │
│ Spider       │────?────│   Model      │
│ (finds $)    │  maybe  │              │
└──────────────┘         └──────────────┘

┌──────────────┐
│ Gumroad      │    ⚠️
│ Spider       │────?────
│ (finds $)    │  maybe
└──────────────┘

FIX: Add Revenue.objects.create() calls in spiders
```

---

## SUMMARY DIAGRAM: INTEGRATION STATUS

```
┌─────────────────────────────────────────────────────────┐
│           UNIFIED DONKEY BETZ PLATFORM                  │
│                INTEGRATION STATUS                       │
└─────────────────────────────────────────────────────────┘

INTELLIGENCE LAYER (Spiders):     ████████████████░░░░ 80%
├─ Registered: 48                 ✅
├─ Implemented: 23                ✅
├─- Unregistered: 2               ❌ QUICK FIX
└─ Placeholder: 25                ⚠️ FUTURE WORK

EXECUTION LAYER (Agents):         ██████████████████░░ 85%
├─ DB Agents: 196                 ✅
├─ Loaded Hardcoded: 3            ✅
├─ Orphaned: 11                   ❌ QUICK FIX
├─ LLM Integration: Working       ✅
└─ Orchestration: Duplicated      ⚠️ NEEDS CONSOLIDATION

LEARNING LAYER (Bridges):         ██████████████░░░░░░ 70%
├─ Bridges Created: 11            ✅
├─ Confirmed Active: 4            ✅
├─ Unclear Status: 4              ⚠️ NEEDS VERIFICATION
└─ Integration Points: Partial    ⚠️ NEEDS LOGGING

PERSISTENCE LAYER (Database):     ██████████████████░░ 90%
├─ Core Models: Complete          ✅
├─ Agent Storage: Working         ✅
├─ Revenue Model: Exists          ✅
└─ Revenue Data: Incomplete       ⚠️ NEEDS CONNECTION

PRESENTATION LAYER (Frontend):    ████████████████░░░░ 80%
├─ WebSocket Routes: 60+          ✅
├─ View Files: 72                 ✅
├─ Templates: Multiple locations  ⚠️ NEEDS CONSOLIDATION
└─ Real-time Updates: Working     ✅

BACKGROUND TASKS (Celery):        ██████░░░░░░░░░░░░░░ 35%
├─ Registered Tasks: 1            ⚠️
├─ Should Be Tasks: 15+           ❌ UNDERUTILIZED
└─ Performance Impact: HIGH       ⚠️ OPTIMIZATION NEEDED

════════════════════════════════════════════════════════

OVERALL INTEGRATION:              ████████████████░░░░ 75%

ASSESSMENT: Production-ready core with disconnected advanced features
RECOMMENDATION: 6 hours of quick fixes → 90% integration
```

---

## NAVIGATION GUIDE

**For Developers:**
- Agent system: `/ai_core/agents/`
- Spider system: `/ai_core/spiders/`
- Learning bridges: `/core/learning_bridges/`
- Views: `/core/views_*.py`
- Models: `/*/models.py`

**For Understanding Flow:**
- Start: This document (architecture overview)
- Details: `COMPREHENSIVE_SYSTEM_AUDIT_2025_10_02.md`
- Quick wins: `QUICK_FIX_GUIDE.md`
- Summary: `AUDIT_EXECUTIVE_SUMMARY.md`

---

**Created:** October 2, 2025
**Purpose:** Visual understanding of 18-month platform architecture
**Status:** 75% integrated, clear path to 100%
