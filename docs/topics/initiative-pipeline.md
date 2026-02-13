# Initiative Pipeline

Initiatives are the platform's project management system — ideas flow from dreams through a 5-stage pipeline to deliverables, with signal intelligence providing the "why" behind each initiative.

## Pipeline Flow

```
Dream (user idea or auto-topic)
  → Initiative (created, stage 1)
    → Stage 1: Research Brief
      → Stage 2: Prototype Plan
        → Stage 3: Evaluation Protocol
          → Stage 4: Technical Design
            → Stage 5: Pilot Execution
              → Deliverable (published output)
```

## Two Execution Tracks

**Fast Track (Stages 1-2 only):**
- Default for quick experiments
- Only Stage 2 requires approval
- Stops at Stage 2 awaiting founder decision

**Institutional Track (Full 5-stage):**
- Triggered by content flags: external_data, user_data, public_publishing, legal_compliance, financial, irreversible
- Requires boardroom approval, compliance review, stage approvals (2, 3, 4)
- Content flags auto-detected via keyword matching in initiative name/description

## Signal Intelligence (Session 900)

Full provenance chain tracks WHY initiatives exist:

```
SpiderData (raw, 72h)
  → SignalAggregationService.aggregate_signals()
    → SignalCluster (pattern detected)
      → generate_auto_topics()
        → AutoTopic (with rationale)
          → trigger_signal_driven_conversation()
            → HiveMindSession (with signal_cluster FK + auto_topic FK)
              → Initiative (with full provenance)
```

**Signal Clustering:**
- Extract keywords and topics from SpiderData
- Group by topic (primary) or keywords (secondary)
- Filter clusters below MIN_CLUSTER_SIZE (3)
- Calculate metrics: strength (0-1), confidence (0-1), novelty (0-1)

**7 Pattern Types:** demand_spike, trend_emergence, sentiment_shift, opportunity_window, knowledge_gap, skill_demand, content_gap

**Cluster Metrics:**
- **Strength:** signal count (40%) + source diversity (40%) + relevance (20%)
- **Confidence:** source count / 4 (min 2 sources for > 0.3)
- **Novelty:** Decays over 24h based on average signal age

## Priority Scoring

```
priority_score = impact_score × 0.4 + urgency × 0.2 + confidence × 0.2 + revenue_potential × 0.2
```

All inputs are 0-1 floats. Priority levels: critical (>= 0.8), high (>= 0.6), medium (>= 0.4), low (< 0.4).

## Purpose Categories & Programs

**5 Purposes:** revenue, stability, learning, expansion, maintenance

**10 Programs (portfolio view):** growth_intelligence, platform_health, monetization, content_pipeline, ai_capabilities, user_experience, infrastructure, research, experiments, uncategorized

## Action Item Tracking (Session 902)

Extracted from `=== DecisionSummary ===` sections in HiveMind conversation conclusions.

**InitiativeActionItem fields:**
- Status: pending / in_progress / completed / blocked / cancelled
- Priority: critical / high / medium / low
- Timeline: Parsed from text like "Week 0-1" → due_date
- Assignment: agent name and/or user FK
- Dependencies: ManyToMany to other action items

Methods: `start()`, `complete()`, `block(reason)`. Properties: `is_overdue`, `days_until_due`.

## Initiative Conversations (Session 928)

"Discuss with Agents" button creates HiveMindSession linked to initiative via FK. Injects full context (origin, stages, action items, signals). Auto-selects relevant agents via AgentRouter.

## Key Model Fields

**Initiative:** updated_at, last_activity_at, impact_score, urgency, confidence, revenue_potential, current_stage (1-5), purpose, program, execution_track

**InitiativeActionItem:** status, priority, timeline_text, due_date, assigned_agent, assigned_user, source_conversation (FK to HiveMindSession)

**ResearchResult:** Tracks Stage 1 research with data_sufficient, blocked_reason, retry_count, findings (JSON), confidence_score. Methods: mark_complete(), mark_blocked(), create_research_brief().

## Circuit Breaker (Session 884/994)

Prevents initiative creation when the system is overloaded. Config: `INITIATIVE_BACKLOG_THRESHOLD=50` (env) or `SystemConfiguration` key `initiative_creation_paused`.

**Enforcement points (Session 994):** ALL 5 creation paths check the circuit breaker:
- `InitiativeIntegrationService.get_or_create_initiative()` — raises `InitiativeCreationBlocked`
- `ConversationInitiativePipeline.process()` — quality gate + circuit breaker
- `HiveMindExecutionPipeline` — circuit breaker check
- `DecisionExtractor.auto_link_initiative_for_decision()` — catches `InitiativeCreationBlocked`
- `AgentDream.promote_to_initiative()` — circuit breaker check

**Backlog count:** ACTIVE + TRIAGE initiatives with `last_activity_at IS NULL`. Cached 60s.

## Quality Gate (Session 994)

Pre-creation filter in `ConversationInitiativePipeline._quality_gate()`:
1. Reject exploratory topics (2+ explore patterns like "explore", "trending", "brainstorm")
2. Require action verb in decision summary ("build", "create", "implement", etc.)
3. Require substantive conversation (1000+ chars minimum)
4. Single-pattern explore check on topic prefix

## TRIAGE Status (Session 994)

Auto-created initiatives start as `TRIAGE`, not `ACTIVE`. The PA can promote TRIAGE → ACTIVE via `update_status` action. This prevents auto-generated initiatives from polluting the active pipeline.

## Activity Tracking (Session 994)

`last_activity_at` is updated via `initiative.update_activity()` from:
- `InitiativeStage.approve()` — on every stage approval
- `generate_initiative_stage_document` task — when stage docs are created
- `handle_stage_task_completion()` — when any stage work completes
- `process_initiative_auto_progression` task — when stages auto-progress
- HiveMind session completion (original 2 call sites)

## PA Flow Metrics (Session 994)

`initiative_tool` actions: list, stats, details, action_items, **flow_metrics**, update_status, advance, complete_action_item.

`flow_metrics` returns: creation_rate (24h/7d), backlog (triage/active/no_activity), stage_distribution, circuit_breaker status, completed_last_7d.
