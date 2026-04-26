<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`../PLATFORM_WHAT_IT_IS.md`](/docs/PLATFORM_WHAT_IT_IS.md). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality (Session 1099 verifier).

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
- **Known behavior:** `can_auto_progress` returns `False` when `execution_speed == 'fast' AND current_stage >= 2`. Since all initiatives default to `fast`, auto-progression stalls at Stage 2 until a human promotes or changes execution_speed. This causes apparent "gaps" in the Activity Feed where Celery tasks run every 10 min but find nothing eligible to progress.

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

**10 Pattern Types** (PATTERN_TYPE_CHOICES): demand_spike, trend_emergence, sentiment_shift, opportunity_window, knowledge_gap, competitive_signal, market_movement, skill_demand, content_gap, user_need

**Topic Quality Gate (Session 1010):**
- `_generate_topic_name()` filters stopwords (new, now, before, how to, want, need, etc.) from cluster keywords
- Clusters with ALL stopword keywords are skipped entirely (no AutoTopic created)
- Uses comma separator instead of "and" for multi-keyword topics
- Falls back to cluster name when no meaningful keywords remain

**Circuit Breaker (Session 1010):**
- Counts ALL active + triage initiatives (not just those with no activity)
- Default threshold: 20 (env var: `INITIATIVE_BACKLOG_THRESHOLD`)
- Dedup check includes TRIAGE status (was only ACTIVE)
- Blocks new initiative creation when backlog >= threshold

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

**Initiative:** updated_at, last_activity_at, impact_score, urgency, confidence, revenue_potential, current_stage (1-5), purpose, program, execution_track, owner (FK to User), owner_agent (CharField)

**InitiativeActionItem:** status, priority, timeline_text, due_date, assigned_agent, assigned_user, source_conversation (FK to HiveMindSession)

**ResearchResult:** Tracks Stage 1 research with data_sufficient, blocked_reason, retry_count, findings (JSON), confidence_score. Methods: mark_complete(), mark_blocked(), create_research_brief().

## Circuit Breaker (Session 884/994)

Prevents initiative creation when the system is overloaded. Config: `INITIATIVE_BACKLOG_THRESHOLD=50` (env) or `SystemConfiguration` key `initiative_creation_paused`.

**Enforcement points (Session 994, updated Session 1020):** ALL 6 creation paths check the circuit breaker + similarity dedup:
- `InitiativeIntegrationService.get_or_create_initiative()` — similarity dedup + circuit breaker
- `ConversationInitiativePipeline.process()` — quality gate + circuit breaker (Session 1020)
- `HiveMindExecutionPipeline` — circuit breaker (Session 1020)
- `DecisionExtractor.auto_link_initiative_for_decision()` — catches `InitiativeCreationBlocked`
- `AgentDream.promote_to_initiative()` — similarity dedup + circuit breaker (Session 1020)
- `create_initiative_from_deliverables()` — circuit breaker

**Similarity dedup (Session 1020):** `find_similar_initiative()` in `initiative_circuit_breaker.py` uses Jaccard keyword similarity at 0.6 threshold.

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

## Ownership (Session 996)

Each initiative can have an **owner** (human FK) or **owner_agent** (agent name string). The PA can filter by owner, show ownership in list/details, and assign/transfer ownership.

**Auto-assignment rules** (via `_auto_assign_owner()` in `initiative_integration_service.py`):
1. If `program` matches `PROGRAM_OWNER_MAP` → assign that agent (e.g., content_pipeline → ContentStrategyAgent)
2. Else if `created_by` looks like an agent name → use created_by
3. Otherwise leave unowned

**PROGRAM_OWNER_MAP:** content_pipeline → ContentStrategyAgent, growth_intelligence → MarketIntelligenceAgent, monetization → OpportunityScoringAgent, platform_health → SystemIntelligenceAgent, ai_capabilities → ThinkingAgent, infrastructure → DevOpsAgent, research/experiments → ResearchAgent

**PA commands:** "show my initiatives", "unowned initiatives", "who owns [X]?", "assign [X] to [Agent]", "take ownership of [X]"

## Stage Pipeline Integrity (Session 1021)

Three systemic bugs found and fixed in `advance_initiative_pipeline`:

**DRAFT stages silently skipped (PR #1250):** Pipeline only matched `PENDING` stages without docs. After Session 1020 created docs for Stage 2+, stages with `DRAFT` status + existing document were never approved. Fixed by adding DRAFT+document detection path.

**Future stage document generation (PR #1251):** The `range(1, 6)` loop generated documents for ANY pending stage regardless of whether prior stages were approved. This caused "rubber-stamping" — 4 stages approved in 10 minutes with zero work when Stage 2 was unblocked. Fixed by anchoring to `init.current_stage` with prior stage approval check.

**Garbage document content (PR #1252):** ALL Stage 1 and Stage 2 documents contained garbage — parroted prompt instructions or random blog summaries. Root cause: `TechnicalDocumentAgent` called without `topic` or `research_context`, and has no tools to do research. Fixed by adding `_gather_initiative_research()` that queries SpiderData, SignalClusters, AgentConversations, and Deliverables for real data before calling the agent.

**Current pipeline behavior (post Session 1021):**
1. Only processes `init.current_stage` (never scans ahead)
2. Verifies prior stage is `APPROVED` before proceeding
3. Gathers real system data (spider intelligence, signal clusters, conversations, deliverables) via keyword search
4. Injects real data into task prompt with anti-hallucination instructions
5. Passes `topic` and `research_context` to agent context

## Dead State Fix & First Completions (Session 1033)

### The Problem

All 3 ACTIVE initiatives were permanently stuck at Stage 2 with `status=IN_REVIEW` but **no document**. The pipeline only processed `PENDING`/`DRAFT` stages — `IN_REVIEW` without a document was an unrecoverable dead state.

### Fix 1: IN_REVIEW Dead State (PR #1307)

`advance_initiative_pipeline` now includes `IN_REVIEW` stages with no document:
```python
if not stage or (stage.status in ('PENDING', 'DRAFT', 'IN_REVIEW') and not stage.document_id):
```

Previously only `PENDING`/`DRAFT` were handled, so `IN_REVIEW` stages without documents were permanently skipped.

### Fix 2: `_get_next_task_for_agent()` Rewrite (PR #1307)

The function was completely broken — referenced nonexistent fields:
- `InitiativeStage.assigned_agent` (doesn't exist)
- `InitiativeStage.description` (doesn't exist)
- `Initiative.title` (should be `name`)
- `status='pending'` (should be uppercase `'PENDING'`)
- Wrong import path (`core.models` instead of `core.models_document_registry`)

Rewritten to query `PENDING` stages with no document, plus PublishGate backlog as fallback.

### Production Results — First Initiatives EVER Completed

Data fix: Reset 3 stuck Stage 2 `IN_REVIEW` records to `PENDING` on Railway. Then manually triggered `advance_initiative_pipeline`:

| Initiative | Stages Completed | Time |
|-----------|-----------------|------|
| "Developing role, job, position skills" | 2→3→4→5→COMPLETED | ~3 min |
| "Revise Android 17 Beta Review for Credibility and Clarity" | 2→3→4→5→COMPLETED | ~3 min |
| "Capitalizing on deadline, position opportunity" | 2→3→4→5→COMPLETED | ~3 min |

Each stage generated a real document via TechnicalDocumentAgent (~45s each), using spider data and embeddings. **These were the first initiatives EVER to complete the full 5-stage pipeline.**

Post-Session 1033 status: 3 COMPLETED, 0 ACTIVE, 17 TRIAGE.

## PA Flow Metrics (Session 994)

`initiative_tool` actions: list, stats, details, action_items, **flow_metrics**, update_status, advance, complete_action_item, **assign_owner**.

`flow_metrics` returns: creation_rate (24h/7d), backlog (triage/active/no_activity), stage_distribution, circuit_breaker status, completed_last_7d.
