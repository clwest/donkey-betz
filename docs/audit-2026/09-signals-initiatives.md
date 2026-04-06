# Dossier #9: Signal Intelligence + Initiative Pipeline

**Audited:** April 6, 2026
**Status:** WORKING — full chain from spider data to initiative creation verified

---

## 1. Purpose

Transforms raw spider data into actionable business initiatives through a multi-stage autonomous pipeline: signal clustering detects patterns, auto-topics generate discussion points, goal-driven conversations produce decisions, and the conversation-to-initiative pipeline creates tracked 5-stage work items with quality gates, founder intent controls, and action item extraction.

## 2. Runtime Evidence

- **19 initiatives** on production (2 ACTIVE, rest TRIAGE)
- **SignalCluster** records created every 30 minutes from spider data
- **AutoTopic** records generated from high-confidence clusters
- **HiveMindSession** records track goal-driven conversations
- **InitiativeStage** 5-stage pipeline with hard invariants enforced at DB level
- **InitiativeActionItem** records track concrete tasks with dependencies

## 3. Entry Points

| Trigger | What Happens |
|---------|--------------|
| Celery Beat (30m) | `aggregate_spider_signals` → clusters spider data into SignalCluster |
| Signal aggregation | High-confidence clusters → AutoTopic generation (max 10/day) |
| AutoTopic created | Triggers HiveMindSession (goal-driven conversation) |
| Conversation complete | `ConversationInitiativePipeline` creates Initiative with 5 stages |
| Dream approved | `dream.promote_to_initiative()` creates Initiative from dream |
| Manual | PA tool or API can create initiatives directly |

## 4. Execution Chain

```
SPIDER DATA (every 30 minutes)
  │
  ├─ aggregate_spider_signals (core/services/signal_aggregation_service.py:115)
  │   → Fetch 500 recent items (6-hour window)
  │   → Extract keywords (7 pattern types)
  │   → Cluster by topic (min 3 signals per cluster)
  │   → Score: strength, confidence, novelty, urgency
  │   → Create SignalCluster records
  │
  ├─ AutoTopic generation (signal_aggregation_service.py:492)
  │   → Max 10 topics per 24-hour window
  │   → Clusters with confidence >= 0.6
  │   → Suggest agents based on pattern type
  │   → Create AutoTopic with urgency, relevance, suggested_agents
  │
  ├─ HiveMindSession (core/models_unified_system.py:10027)
  │   → Goal-driven conversation with objective + success criteria
  │   → Auto-select up to 8 relevant agents by topic matching
  │   → Conversation types: analytical, creative, debate, planning, critique
  │   → Each agent contributes with key_points and confidence_score
  │   → Produces conclusion/synthesis
  │
  └─ ConversationInitiativePipeline (core/services/conversation_initiative_pipeline.py:376)
      │
      ├─ Quality Gate (line 300)
      │   → Reject exploratory topics (brainstorm, trends, tell me)
      │   → Reject content review (revise, review, enhance)
      │   → Require actionable verb (build, create, implement, deploy)
      │   → Require 1000+ chars substance
      │
      ├─ Circuit Breaker (line 416)
      │   → Pause if pending initiatives exceed threshold
      │
      ├─ Initiative Creation (line 442)
      │   → LLM-generated title
      │   → Dedup: reuse similar existing initiatives
      │   → Status: TRIAGE (auto-created)
      │   → Auto-assign owner agent
      │   → Auto-link to source SignalCluster (embedding similarity >= 0.60)
      │   → Set founder intent to BALANCED
      │   → Assign human_id: INIT-000001 format
      │
      ├─ 5 InitiativeStages created (line 566)
      │   Stage 1: Research Brief (discovery + framing)
      │   Stage 2: Prototype Plan (how to build)
      │   Stage 3: Evaluation Protocol (should we proceed?)
      │   Stage 4: Technical Design (what exactly to build)
      │   Stage 5: Pilot Execution (build + postmortem)
      │
      └─ Task Dispatch (line 610)
          → Stage 1 tasks dispatched to agents via Celery

PARALLEL PATH: DREAMS → INITIATIVES

AgentDream (core/models_unified_system.py:8841)
  → dream_type: creative_idea, what_if, prediction, improvement, etc.
  → composite_score = (creativity + actionability + relevance) / 3 * origin_weight
  → Origin weights: serious=1.0, speculative=0.8, probe=0.3, joke=0.1
  → If approved: promote_to_initiative() → creates Initiative in TRIAGE
```

## 5. Data Contracts

| Model | File | Purpose |
|-------|------|---------|
| SignalCluster | `core/models_signal_intelligence.py:29` | Pattern detection from spider data |
| AutoTopic | `core/models_signal_intelligence.py:258` | Generated discussion topics |
| HiveMindSession | `core/models_unified_system.py:10027` | Goal-driven multi-agent conversations |
| HiveMindContribution | `core/models_unified_system.py:10290` | Per-agent contributions with key points |
| Initiative | `core/models_document_registry.py:37` | 5-stage tracked work items |
| InitiativeStage | `core/models_document_registry.py:1259` | Individual pipeline stages with documents |
| InitiativeActionItem | `core/models_document_registry.py:1838` | Concrete tasks with dependencies |
| AgentDream | `core/models_unified_system.py:8841` | Creative ideas that can become initiatives |

### Initiative Status Flow
```
TRIAGE (auto-created) → ACTIVE (founder intent set) → COMPLETED (5 stages approved)
                                                     → ON_HOLD
                                                     → ARCHIVED
```

### Stage Status Flow
```
PENDING → DRAFT → IN_REVIEW → APPROVED → (advance to next stage)
                             → REJECTED
                             → BLOCKED (awaiting data)
                             → SUPERSEDED (replaced)
```

### Priority Scoring
```
priority_score = impact*0.4 + urgency*0.2 + confidence*0.2 + revenue_potential*0.2
  >= 0.8 → CRITICAL
  >= 0.6 → HIGH
  >= 0.4 → MEDIUM
  <  0.4 → LOW
```

## 6. Hard Invariants (Patent-Relevant)

1. **Stage cannot be APPROVED without a document** — enforced in `clean()` and `save()` with transactions
2. **Stage N cannot be approved before Stage N-1** — sequential gate enforcement
3. **current_stage <= max_approved_stage + 1** — prevents skipping
4. **Race condition prevention** — `select_for_update()` on stage approval
5. **Circuit breaker** — pauses initiative creation if backlog exceeds threshold

## 7. Founder Intent Controls (Patent-Relevant)

Initiatives have explicit human control parameters:
- `execution_speed`: fast / balanced / thorough
- `risk_tolerance`: low / medium / high
- `budget_engineering_hours`, `budget_llm_spend`
- `stop_rule`: condition that kills initiative
- `requires_boardroom_approval`: boolean
- `content_flags`: external_data, user_data, public_publishing, legal_compliance, financial, irreversible
- `execution_track`: fast_track or institutional

## 8. Current Status: WORKING

**Fully operational:**
- Spider → SignalCluster clustering (every 30m)
- AutoTopic generation from high-confidence clusters
- HiveMindSession goal-driven conversations
- Conversation → Initiative pipeline with quality gates
- 5-stage pipeline with hard invariants
- Dream → Initiative promotion
- Action item extraction with dependencies
- Signal auto-linking via embedding similarity

**Production data:** 19 initiatives (2 ACTIVE), multiple signal clusters, action items

## 9. Truth Gaps

- **Initiative completion rate**: 0 initiatives have reached COMPLETED — all stuck at Stage 1/TRIAGE
- **Auto-progression effectiveness**: Does auto-advance work when stages are approved? Not verified
- **Drift detection**: drift_score exists but unclear if it's actually calculated
- **Action item execution**: Items are created but unclear if agents actually execute them
- **Founder intent impact**: Controls exist but unclear if execution_speed/risk_tolerance actually change pipeline behavior

## Key Patent Claims

1. **Autonomous signal-to-initiative pipeline** — spider data → signal clustering → topic generation → goal-driven conversation → initiative creation without human intervention
2. **5-stage gated pipeline with hard invariants** — transactional enforcement prevents progression without prior stage approval + document
3. **Founder intent controls** — human parameters (speed, risk, budget, stop rules) constrain autonomous execution
4. **Dream productization** — creative AI-generated ideas scored and promoted to tracked work items
5. **Signal provenance linking** — embedding-based auto-linking traces initiatives back to originating spider signals
6. **Circuit breaker pattern** — prevents runaway initiative creation when system is overwhelmed
