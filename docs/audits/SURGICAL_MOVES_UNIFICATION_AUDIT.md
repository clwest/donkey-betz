# Surgical Moves Unification Audit

**Session:** 960
**Date:** February 7, 2026
**Auditor:** Claude Code (Senior Systems Architect & Integration Auditor)
**Scope:** Three surgical moves across the full unified-donkey-betz codebase

---

## A) Executive Summary

This platform has **~70% of the infrastructure** needed for all three surgical moves already built and working in production. The gap is not missing technology -- it is **missing connectors** between existing systems. The three moves share a single unifying theme: every agent action should produce a traceable, citable, replayable, learnable artifact.

### What Exists (Strong Foundation)

| Move | Readiness | Key Infrastructure |
|------|-----------|-------------------|
| **Move 1: Docs as Cognitive Organ** | ~60% | ReportProvenance, Claim dataclass, PublishGate, BaseAgent doc methods (_read_doc, _write_doc, _create_session_handoff), SelfBlog pipeline, build_docs_index |
| **Move 2: Deliberation Sessions** | ~75% | HiveMindSession, ConceptForge 6-stage pipeline, 3 Contracts (Research/Synthesis/Execution), DecisionEnforcerAgent, ConversationOrchestrator with debate types, DecisionRecord/ToolCallRecord audit trail |
| **Move 3: Strategic Memory** | ~70% | AgentMemory (pgvector embeddings), LearningPattern (14K+ records), MemoryPalaceRoom, MemoryCluster, MythologyDetectionService, memory decay weighting, LearningLoopOrchestrator |

### What's Missing (Critical Gaps)

1. **No citation tracking in agent outputs** -- ReportProvenance exists but agents don't emit `internal_doc_refs` linking to the docs they consumed
2. **No unified deliberation session model** -- ConceptForge, HiveMind, and ConversationOrchestrator are three separate systems with no shared session abstraction
3. **No meta-query service** -- Memory is recorded but nothing answers "Have we tried this before?" or "What patterns recur across failures?"
4. **Contracts are ephemeral** -- ResearchContract/SynthesisContract/ExecutionMandate are dataclasses created in-memory but never persisted to the database
5. **No doc versioning** -- BaseAgent can write docs but there's no version history, diff tracking, or "Git-for-thinking" audit trail

### Strategic Recommendation

Implement in 4 phases over ~4 sessions. Phase 0 (connectors-only, no new models) delivers 80% of value. The remaining phases add persistence, UI, and meta-intelligence. Total blast radius is moderate: ~15 files modified, 3-4 new models, 2 new services.

---

## B) Current State Map

### Move 1: Docs as First-Class Cognitive Organ

#### What's Built

```
BaseAgent (core/agents/base_agent.py)
  |-- _read_doc(path)           # Session 798 - reads from docs/
  |-- _write_doc(path, content) # Session 798 - writes to docs/
  |-- _create_session_handoff() # Session 798 - generates handoff markdown
  |-- _update_start_next_session()
  |-- _regenerate_docs_index()  # Calls build_docs_index management command

ReportProvenance (core/agents/report_schemas.py:68)
  |-- report_type: str
  |-- generated_at_utc: str
  |-- sources: List[SourceInfo]     # name, endpoint, retrieved_at, record_count, freshness_hours
  |-- validation_status: str        # verified | partially_verified | unverified | stale
  |-- publishable: bool
  |-- publish_blockers: List[str]
  |-- disclaimer: str
  |-- to_markdown_block()           # Human-readable provenance header
  |-- to_dict()                     # Serializable dict

Claim (core/agents/report_schemas.py)
  |-- claim: str
  |-- confidence: float
  |-- evidence_source: str
  |-- claim_type: str               # factual | analytical | speculative

PublishGate (core/services/publish_gate.py)
  |-- evaluate(blog) -> GateResult
  |-- Thresholds: quality>=0.75, novelty>=0.60, structure>=0.55
  |-- Auto-classifies operational titles as internal

SelfBlog Pipeline
  |-- SelfBlog model: quality_score, novelty_score, structure_score, publish_ready, gate_notes, tone, word_count
  |-- ContentWriterAgent -> PublishGate -> SelfBlog

docs/ Directory Infrastructure
  |-- 562 classified documents (risk_level: critical=18, high=332, medium=212)
  |-- build_docs_index management command regenerates docs/INDEX.md
  |-- docs/handoffs/ for session-to-session continuity
  |-- RAG retrieval with risk-aware dual-channel (Session 949)
```

#### What's NOT Built

- **Citation injection**: Agents don't record which internal docs they read during execution
- **Doc versioning**: No version history when docs are updated (just overwrites)
- **Reflection triggers**: No automatic re-evaluation when a doc's source data changes
- **Doc-to-doc linking**: No bidirectional references between related documents
- **Quality scoring for non-blog docs**: PublishGate only covers SelfBlog, not general docs/

### Move 2: Replace Pipelines with Deliberation Sessions

#### What's Built

```
HiveMindSession (core/models_unified_system.py:9862)
  |-- session_type: hive_mind | conversation | autonomous
  |-- conversation_type: analytical | creative | debate | planning | critique
  |-- objective: TextField
  |-- success_criteria: JSONField
  |-- participants: JSONField (agent names)
  |-- signal_cluster: FK -> SignalCluster    # WHY this session started
  |-- auto_topic: FK -> AutoTopic            # What triggered it
  |-- initiative: FK -> Initiative           # What it produces
  |-- status: pending | active | completed | failed

ConceptForge Pipeline (core/models_conceptforge.py)
  |-- ConceptForgeRun: 6-stage pipeline (research -> debate -> feasibility -> risk -> market -> synthesis)
  |-- ConceptForgeStageRun: per-stage tracking with input_snapshot, output_snapshot, advisor_panel_snapshot
  |-- ConceptForgeArtifact: versioned outputs with artifact_type + content + metadata

Contracts System (core/contracts/)
  |-- ResearchContract: status tracking (BLOCKED/IN_PROGRESS/COMPLETE/FAILED), sources_used, auto-deliverables
  |-- SynthesisContract: validated/rejected binary, open_risks, dissents, consensus_level, owner_assignments
  |-- ExecutionMandate: chosen_path, rejected_paths, kill_criteria, experiments, spawned_tasks

ConversationOrchestrator (core/conversation_orchestrator.py)
  |-- Structured turn flows per conversation type
  |-- Contract enforcement (tension_check, grounding_check)
  |-- Synthesis contract triggered at final turn
  |-- Decision enforcer flag for debate-type conversations

DecisionEnforcerAgent (core/agents/decision_enforcer_agent.py:59)
  |-- BANNED_PHRASES: 15+ weasel words ("it depends", "further research needed", etc.)
  |-- Forces APPROVE/REJECT/MODIFY decisions
  |-- Spawns ExecutionMandate tasks

Audit Trail
  |-- DecisionRecord: trace_id, agent_name, reasoning, alternatives, confidence, outcome
  |-- ToolCallRecord: trace_id, tool_name, parameters, result_hash (SHA256), latency_ms
  |-- AgentDecisionSummary: trace_id, key_insights, recommended_actions, dissenting_views

Signal Intelligence Chain
  |-- SpiderData -> SignalCluster -> AutoTopic -> HiveMindSession -> Initiative
  |-- Full provenance: source_breakdown, strength, confidence, novelty, keywords

TimeTravelMixin (core/agents/time_travel_mixin.py:38)
  |-- AgentSession: captures full agent execution context
  |-- DecisionPoint: records individual decision moments within a session
  |-- Replay capability via session reconstruction
```

#### What's NOT Built

- **Unified session abstraction**: HiveMindSession, ConceptForgeRun, and ConversationOrchestrator sessions are three separate, disconnected models with no shared interface
- **Contract persistence**: ResearchContract/SynthesisContract/ExecutionMandate are in-memory dataclasses -- never saved to DB
- **Debate transcript preservation**: ConversationOrchestrator runs debates but only saves the final AgentDecisionSummary, not the full turn-by-turn transcript
- **Automatic decision enforcer**: DecisionEnforcerAgent exists but must be manually invoked -- not auto-triggered at conversation end
- **Session replay UI**: TimeTravelMixin records data but no frontend can replay a session
- **Cross-session linking**: No way to link a ConceptForge run to the HiveMindSession that inspired it

### Move 3: Promote Memory to a Strategic Layer

#### What's Built

```
AgentMemory (core/models_unified_system.py:10187)
  |-- content: TextField
  |-- embedding: VectorField (pgvector, 1536 dimensions)
  |-- memory_type: episodic | semantic | procedural | working
  |-- importance_score: FloatField
  |-- safety_class: safe | sensitive | restricted
  |-- poison_risk: FloatField
  |-- decay_rate: FloatField
  |-- access_count: IntegerField
  |-- last_accessed: DateTimeField

MemoryPalaceRoom (core/models_unified_system.py)
  |-- Spatial metaphor for memory organization
  |-- room_type, capacity, items linked

MemoryCluster (core/models_unified_system.py)
  |-- Groups related memories by semantic similarity
  |-- cluster_label, centroid_embedding, member_count

LearningPattern (core/models_unified_system.py:14068)
  |-- pattern_type: tool_success | tool_failure | quality_improvement | user_preference | boardroom_ml_accuracy
  |-- source_tool / source_agent
  |-- confidence: FloatField
  |-- times_applied / success_when_applied
  |-- metadata: JSONField (flexible signal storage)

LearningPatternEngine (core/services/learning_pattern_engine.py:28)
  |-- mine_patterns_from_decisions()
  |-- maintain_knowledge_freshness()
  |-- promote_shared_knowledge()

LearningLoopOrchestrator (core/services/learning_loop_orchestrator.py:47)
  |-- 15+ success signal definitions
  |-- analyze_user_feedback() from boardroom decisions
  |-- track_learning_application()
  |-- get_learning_effectiveness_stats()

MythologyDetectionService (mythology/services.py)
  |-- Pattern-based hallucination detection
  |-- MythologyQuarantine model for flagged content
  |-- Prevents poisoned memories from propagating

Memory Retrieval
  |-- MemoryEmbeddingService: semantic search via pgvector cosine similarity
  |-- MemoryContextService: cross-session memory with exponential decay weighting
  |-- UserMemoryContext: per-user memory summaries
```

#### What's NOT Built

- **Meta-query service**: No API answers "Have we tried X before?" or "What failed when we attempted Y?"
- **Failure pattern consolidation**: LearningPattern records failures individually but doesn't aggregate them into strategic "failure signatures"
- **Decision similarity search**: No embedding-based search across DecisionRecord/AgentDecisionSummary to find analogous past decisions
- **Strategic recommendation engine**: Memory is passive (retrieved on demand) -- nothing proactively surfaces "Based on 47 past decisions, this approach has a 23% success rate"
- **Memory health dashboard**: No visibility into memory decay, poison risk distribution, or cluster coherence
- **Cross-agent memory sharing**: AgentMemory is per-agent; no mechanism for one agent's learnings to inform another's decisions (except via LearningPattern promotion, which is limited)
- **Temporal pattern detection**: No service identifies recurring patterns across time (e.g., "Every Q1, crypto spiders produce low-quality data")

---

## C) Gap Analysis + Connector Plan

### Gap 1: Citation Tracking in Agent Outputs

**Current state:** ReportProvenance tracks external data sources. Agents can read docs via `_read_doc()`. But the provenance `sources` list never includes internal doc references.

**Connector:** Extend `SourceInfo` to support `source_type: 'internal_doc' | 'external_api' | 'spider_data' | 'memory'`. When `_read_doc()` is called, auto-append to a thread-local `_docs_consumed` list. At provenance build time, merge `_docs_consumed` into `sources`.

**Implementation steps:**
1. Add `source_type` field to `SourceInfo` dataclass in `report_schemas.py`
2. Add `_docs_consumed: List[SourceInfo]` accumulator to `BaseAgent`
3. Modify `_read_doc()` to append to `_docs_consumed` with timestamp and path
4. Modify `build_provenance()` to accept `internal_sources` parameter
5. Update the 26 agents with provenance to pass `internal_sources`

**Risk:** Low. Additive change to existing dataclass. No schema migrations.
**Test:** Run any provenance-enabled agent, verify `sources` includes internal doc refs with `source_type: 'internal_doc'`.

---

### Gap 2: Contract Persistence

**Current state:** ResearchContract, SynthesisContract, ExecutionMandate are Python dataclasses created in ConversationOrchestrator, used during conversation, then garbage collected.

**Connector:** Create a `ContractRecord` model that serializes any contract to JSON and links it to the HiveMindSession/conversation that produced it.

**Implementation steps:**
1. Create `ContractRecord` model: `session_id (FK HiveMindSession)`, `contract_type (research|synthesis|execution)`, `contract_data (JSONField)`, `created_at`, `trace_id`
2. Add `.to_dict()` methods to all three contract classes (SynthesisContract already has partial serialization)
3. In ConversationOrchestrator, after contract creation, save `ContractRecord`
4. Add API endpoint `GET /api/sessions/<id>/contracts/` to retrieve contracts for a session

**Risk:** Low-medium. New model requires migration. Contract serialization must handle all field types.
**Test:** Run a debate conversation, verify ContractRecord saved. Query API, verify contract data matches in-memory version.

---

### Gap 3: Unified Session Abstraction

**Current state:** Three separate session systems:
- `HiveMindSession` (multi-agent conversations)
- `ConceptForgeRun` (6-stage think tank)
- `AgentSession` (single-agent time travel)

Each tracks different metadata, has different statuses, and stores outputs differently.

**Connector:** Create a `DeliberationSession` model that acts as a parent envelope. Existing models gain an optional FK to `DeliberationSession`. This is NOT a replacement -- it's a unifying wrapper.

**Implementation steps:**
1. Create `DeliberationSession` model: `session_id (UUID)`, `session_type (hivemind|conceptforge|agent|composite)`, `objective`, `participants (JSONField)`, `status`, `created_at`, `completed_at`, `parent_session (self-FK for nesting)`, `evidence_pack (JSONField)`, `trace (JSONField)`
2. Add optional `deliberation_session` FK to HiveMindSession, ConceptForgeRun, AgentSession
3. When any session starts, auto-create a DeliberationSession envelope
4. Populate `evidence_pack` and `trace` fields as session progresses (see Sections D & E)

**Risk:** Medium. Three migrations (one per model getting the FK). Must be backward-compatible (nullable FK).
**Test:** Create a HiveMindSession, verify parent DeliberationSession auto-created. Query DeliberationSession, verify it links to child.

---

### Gap 4: Debate Transcript Preservation

**Current state:** ConversationOrchestrator runs multi-turn debates. Only the final `AgentDecisionSummary` is saved. Individual agent responses during the conversation are not persisted in structured form.

**Connector:** Record each turn as a `DeliberationTurn` linked to the session.

**Implementation steps:**
1. Create `DeliberationTurn` model: `session (FK DeliberationSession)`, `turn_number`, `agent_name`, `role (advocate|critic|synthesizer|enforcer)`, `content`, `contract_state (JSONField, nullable)`, `created_at`
2. In ConversationOrchestrator `_execute_turn()`, after each agent response, create `DeliberationTurn`
3. Link final `AgentDecisionSummary` to the `DeliberationSession` via FK

**Risk:** Medium. Write volume proportional to conversation length (typically 4-8 turns). Index on session FK.
**Test:** Run a debate, verify turn count matches expected. Replay from DB matches original flow.

---

### Gap 5: Meta-Query Service ("Have We Tried This?")

**Current state:** Memory is stored (AgentMemory, LearningPattern, DecisionRecord) but no service performs cross-model semantic search to answer meta-questions.

**Connector:** Create `StrategicMemoryService` that queries across AgentMemory, LearningPattern, DecisionRecord, and AgentDecisionSummary using embedding similarity.

**Implementation steps:**
1. Create `core/services/strategic_memory_service.py`
2. Implement `query_precedents(question: str, top_k: int = 10)`:
   - Embed the question
   - Search AgentMemory (pgvector cosine similarity)
   - Search LearningPattern (text match on pattern_data + metadata)
   - Search DecisionRecord (text match on reasoning + alternatives)
   - Search AgentDecisionSummary (text match on key_insights)
   - Rank by relevance, return unified results with source attribution
3. Implement `get_failure_signatures(domain: str)`:
   - Query LearningPattern where `pattern_type='tool_failure'` grouped by source_tool
   - Aggregate failure rates, common error patterns, time distribution
4. Implement `recommend_strategy(objective: str)`:
   - Find similar past objectives (Initiative.description embedding search)
   - Return success/failure rates, common blockers, recommended approaches
5. Wire into PA enrichment pipeline as a new enrichment source for `reasoning` and `initiatives` intents

**Risk:** Medium. Performance depends on embedding index quality. Pgvector already indexed on AgentMemory. DecisionRecord/AgentDecisionSummary would need text-based search (no embeddings yet).
**Test:** Ask "Have we tried automated content publishing?" -- verify results include PublishGate history, content experiment learnings, and relevant AgentDecisionSummaries.

---

### Gap 6: Doc Versioning

**Current state:** `_write_doc()` overwrites files. `_regenerate_docs_index()` rebuilds the index. No version history.

**Connector:** Create a `DocVersion` model that snapshots content before overwrites.

**Implementation steps:**
1. Create `DocVersion` model: `doc_path`, `version_number`, `content_hash (SHA256)`, `content_snapshot (TextField)`, `author_agent`, `session_id`, `change_reason`, `created_at`
2. Modify `BaseAgent._write_doc()` to: read current content, if changed, create DocVersion, then write
3. Add `GET /api/docs/<path>/versions/` endpoint
4. Add `GET /api/docs/<path>/diff/<v1>/<v2>/` endpoint for diffs

**Risk:** Low-medium. Storage grows with doc update frequency. Most docs update rarely (session handoffs are write-once).
**Test:** Update a doc twice via agent, verify two DocVersion records. Diff endpoint returns meaningful changes.

---

### Gap 7: Automatic Decision Enforcer Triggering

**Current state:** DecisionEnforcerAgent exists but is only invoked when explicitly included in conversation participants. Most conversations end without forced decisions.

**Connector:** In ConversationOrchestrator, auto-invoke DecisionEnforcerAgent as the final turn for `debate` and `planning` conversation types.

**Implementation steps:**
1. In `ConversationOrchestrator._should_enforce_decision()`, return True for debate/planning types
2. After the synthesis turn, if `_should_enforce_decision()`, inject DecisionEnforcerAgent as final participant
3. Store the resulting ExecutionMandate as a ContractRecord (Gap 2)

**Risk:** Low. DecisionEnforcerAgent is already production-tested. Only changes turn flow for 2 conversation types.
**Test:** Start a debate conversation without explicitly adding DecisionEnforcer. Verify it auto-appears as final turn and produces a mandate.

---

## D) Evidence Pack Spec

Every `DeliberationSession` accumulates an Evidence Pack -- a structured record of all inputs, sources, and claims that informed the deliberation.

```json
{
  "$schema": "evidence-pack-v1",
  "session_id": "uuid",
  "assembled_at": "ISO-8601",
  "sources": [
    {
      "source_id": "uuid",
      "source_type": "spider_data | internal_doc | external_api | agent_memory | learning_pattern | user_input",
      "name": "string",
      "endpoint_or_path": "string",
      "retrieved_at": "ISO-8601",
      "freshness_hours": "float",
      "record_count": "int",
      "content_hash": "sha256",
      "reliability_score": "float (0-1, optional)"
    }
  ],
  "claims": [
    {
      "claim_id": "uuid",
      "claim_text": "string",
      "claim_type": "factual | analytical | speculative",
      "confidence": "float (0-1)",
      "source_ids": ["uuid (refs sources[].source_id)"],
      "supporting_evidence": "string (excerpt or summary)",
      "challenged_by": ["uuid (refs claims[].claim_id, optional)"],
      "status": "uncontested | challenged | refuted | verified"
    }
  ],
  "contradictions": [
    {
      "contradiction_id": "uuid",
      "claim_a_id": "uuid",
      "claim_b_id": "uuid",
      "nature": "string (description of the contradiction)",
      "resolution": "claim_a_wins | claim_b_wins | unresolved | synthesized",
      "resolution_reasoning": "string",
      "resolved_by": "string (agent_name or 'consensus')"
    }
  ],
  "internal_refs": [
    {
      "doc_path": "string (relative to project root)",
      "doc_title": "string",
      "relevance": "primary | supporting | background",
      "sections_cited": ["string (section headers or line ranges)"],
      "accessed_at": "ISO-8601",
      "version_hash": "sha256 (optional, links to DocVersion)"
    }
  ],
  "memory_retrievals": [
    {
      "memory_id": "int (AgentMemory PK)",
      "memory_type": "episodic | semantic | procedural",
      "similarity_score": "float",
      "content_preview": "string (first 200 chars)",
      "retrieved_for": "string (query that triggered retrieval)"
    }
  ]
}
```

### Mapping to Existing Infrastructure

| Evidence Pack Field | Existing Model/Service | Gap |
|--------------------|-----------------------|-----|
| `sources` | `ReportProvenance.sources` (SourceInfo) | Add `source_type` and `content_hash` fields |
| `claims` | `Claim` dataclass in report_schemas.py | Add `claim_id`, `source_ids`, `challenged_by`, `status` |
| `contradictions` | ConversationOrchestrator `tension_check` | Currently checks tension but doesn't persist contradiction records |
| `internal_refs` | BaseAgent `_docs_consumed` (proposed) | Not yet built -- Gap 1 |
| `memory_retrievals` | MemoryEmbeddingService queries | Currently returns results but doesn't log which memories were retrieved |

### Population Strategy

The Evidence Pack is **incrementally assembled** during a deliberation session:

1. **Session start**: Initialize with `sources` from signal intelligence chain (SignalCluster, AutoTopic)
2. **Each agent turn**: Append agent's tool calls to `sources`, extract claims from structured output, log memory retrievals
3. **Debate turns**: When agents challenge claims, create `contradictions` entries
4. **Synthesis turn**: Update claim statuses based on SynthesisContract (validated/rejected)
5. **Session end**: Finalize with resolution data and internal_refs from doc accesses

---

## E) Session Trace Spec

Every `DeliberationSession` maintains a Session Trace -- the complete execution record enabling replay, audit, and learning.

```json
{
  "$schema": "session-trace-v1",
  "session_id": "uuid (matches DeliberationSession PK)",
  "trace_version": "1.0",
  "session_type": "hivemind | conceptforge | agent | composite",
  "initiated_by": "string (user | celery_task | signal_cluster | agent_name)",
  "trigger": {
    "trigger_type": "user_request | scheduled | signal_driven | agent_spawned",
    "signal_cluster_id": "uuid (optional)",
    "auto_topic_id": "uuid (optional)",
    "parent_session_id": "uuid (optional, for nested sessions)",
    "trigger_context": "string (why this session was created)"
  },
  "participants": [
    {
      "agent_name": "string",
      "role": "advocate | critic | synthesizer | enforcer | researcher | observer",
      "joined_at": "ISO-8601",
      "contribution_count": "int"
    }
  ],
  "inputs": {
    "objective": "string",
    "success_criteria": ["string"],
    "context_provided": {
      "enrichment_sources": ["string (enrichment service names)"],
      "token_budget": "int",
      "constraints": ["string"]
    }
  },
  "deliberation": [
    {
      "turn_number": "int",
      "agent_name": "string",
      "role": "string",
      "timestamp": "ISO-8601",
      "action_type": "research | argue | challenge | synthesize | decide | enforce",
      "content_summary": "string (first 500 chars)",
      "content_hash": "sha256 (full content)",
      "tool_calls": [
        {
          "tool_name": "string",
          "parameters_hash": "sha256",
          "result_hash": "sha256",
          "latency_ms": "int",
          "tool_call_record_id": "int (FK to ToolCallRecord)"
        }
      ],
      "claims_made": ["uuid (refs evidence_pack.claims[])"],
      "claims_challenged": ["uuid"],
      "contract_snapshot": {
        "contract_type": "research | synthesis | execution | null",
        "status": "string",
        "key_fields": {}
      }
    }
  ],
  "decisions": [
    {
      "decision_id": "uuid",
      "decision_type": "approve | reject | modify | defer | kill",
      "made_by": "string (agent_name)",
      "reasoning": "string",
      "alternatives_considered": ["string"],
      "confidence": "float (0-1)",
      "mandate": {
        "chosen_path": "string",
        "rejected_paths": ["string"],
        "kill_criteria": ["string"],
        "experiments": ["string"]
      },
      "decision_record_id": "int (FK to DecisionRecord)"
    }
  ],
  "outputs": {
    "deliverables": [
      {
        "type": "report | blog | initiative | action_items | dossier",
        "title": "string",
        "model_ref": "string (e.g., 'SelfBlog:42', 'Initiative:uuid')",
        "quality_score": "float (optional)",
        "publish_status": "draft | published | killed"
      }
    ],
    "contracts_produced": [
      {
        "contract_type": "research | synthesis | execution",
        "contract_record_id": "int (FK to ContractRecord)",
        "summary": "string"
      }
    ]
  },
  "memory_writes": [
    {
      "memory_id": "int (AgentMemory PK)",
      "memory_type": "episodic | semantic | procedural",
      "content_preview": "string",
      "importance_score": "float",
      "agent_name": "string",
      "write_reason": "string (e.g., 'debate outcome', 'failure pattern', 'new capability discovered')"
    }
  ],
  "learning_extractions": [
    {
      "pattern_id": "int (LearningPattern PK)",
      "pattern_type": "string",
      "confidence": "float",
      "description": "string"
    }
  ],
  "performance": {
    "total_duration_ms": "int",
    "total_turns": "int",
    "total_tool_calls": "int",
    "total_tokens_consumed": "int (estimated)",
    "enrichment_sources_used": "int"
  }
}
```

### Mapping to Existing Infrastructure

| Trace Field | Existing Model | Linkage |
|-------------|---------------|---------|
| `session_id` | HiveMindSession.id / ConceptForgeRun.id | Via DeliberationSession FK |
| `trigger` | SignalCluster, AutoTopic FKs on HiveMindSession | Direct mapping |
| `participants` | HiveMindSession.participants (JSONField) | Add role tracking |
| `deliberation[].tool_calls` | ToolCallRecord (trace_id linkage) | Filter by trace_id |
| `decisions` | DecisionRecord + AgentDecisionSummary | Filter by conversation_id/trace_id |
| `outputs.deliverables` | Initiative, SelfBlog, Deliverable models | Link via session FK |
| `memory_writes` | AgentMemory (created_at filtering) | Add session_id field to AgentMemory |
| `learning_extractions` | LearningPattern | Add session_id field to LearningPattern |
| `performance` | Computed from ToolCallRecord latency aggregation | New computation |

### Replay Protocol

To replay a session from its trace:

1. Load `DeliberationSession` by `session_id`
2. Reconstruct evidence pack from `evidence_pack` JSON field
3. Iterate `deliberation` turns in order
4. For each turn, verify `content_hash` matches stored `DeliberationTurn.content`
5. Verify `tool_calls[].result_hash` matches `ToolCallRecord.result_hash`
6. Display decisions with full context (alternatives, mandate, confidence)
7. Show memory writes and learning extractions as session outcomes

---

## F) Implementation Phases

### Phase 0: Connectors Only (1 session, ~3 hours)

**Goal:** Wire existing systems together. No new models. No migrations. Maximum value with minimum risk.

| Step | File(s) | Change | Blast Radius |
|------|---------|--------|-------------|
| 1 | `core/agents/report_schemas.py` | Add `source_type` field to `SourceInfo`. Add `claim_id`, `source_ids`, `challenged_by`, `status` to `Claim`. | Low -- additive fields with defaults |
| 2 | `core/agents/base_agent.py` | Add `_docs_consumed` list. Modify `_read_doc()` to track reads. Add `get_docs_consumed()` method. | Low -- new attribute, no behavior change |
| 3 | `core/conversation_orchestrator.py` | Auto-invoke DecisionEnforcerAgent for debate/planning conversations. Record contradiction when tension_check fires. | Medium -- changes debate flow for 2 types |
| 4 | `core/contracts/research_contract.py` | Add `to_dict()` serialization method | Low -- additive |
| 5 | `core/contracts/synthesis_contract.py` | Add `to_dict()` serialization method (extend existing) | Low -- additive |
| 6 | `core/contracts/execution_mandate.py` | Add `to_dict()` serialization method | Low -- additive |
| 7 | `core/services/unified_pa_entrypoint.py` | Add `strategic_memory` enrichment type. Wire basic precedent search using existing embedding service for `reasoning` intent. | Low -- new enrichment source, follows existing pattern |

**Deliverables:**
- Agents track which docs they read
- Contracts are serializable
- Debates auto-enforce decisions
- PA can answer basic "what do we know about X?" queries

**Acceptance criteria:**
- [ ] `_read_doc()` populates `_docs_consumed`
- [ ] All 3 contracts serialize to dict and back without data loss
- [ ] Debate conversation auto-triggers DecisionEnforcer as final turn
- [ ] PA `reasoning` intent includes memory/learning pattern context

---

### Phase 1: Persistence Layer (1 session, ~4 hours)

**Goal:** Create the database models that make sessions, contracts, and doc versions permanent.

| Step | File(s) | Change | Blast Radius |
|------|---------|--------|-------------|
| 1 | `core/models_deliberation.py` (NEW) | Create `DeliberationSession` model (UUID PK, session_type, objective, participants, status, evidence_pack JSONField, trace JSONField, parent FK) | New file -- no existing code affected |
| 2 | `core/models_deliberation.py` | Create `DeliberationTurn` model (FK to session, turn_number, agent_name, role, content, contract_state, created_at) | New model |
| 3 | `core/models_deliberation.py` | Create `ContractRecord` model (FK to session, contract_type, contract_data JSONField, trace_id, created_at) | New model |
| 4 | `core/models_deliberation.py` | Create `DocVersion` model (doc_path, version_number, content_hash, content_snapshot, author_agent, change_reason, created_at) | New model |
| 5 | `core/models_unified_system.py` | Add nullable `deliberation_session` FK to `HiveMindSession` | Migration -- nullable FK, backward compatible |
| 6 | `core/models_conceptforge.py` | Add nullable `deliberation_session` FK to `ConceptForgeRun` | Migration -- nullable FK, backward compatible |
| 7 | `core/conversation_orchestrator.py` | On session start, create `DeliberationSession`. On each turn, create `DeliberationTurn`. On contract creation, create `ContractRecord`. | Medium -- adds DB writes to conversation flow |
| 8 | `core/agents/base_agent.py` | Modify `_write_doc()` to create `DocVersion` before overwrite | Low -- additive pre-write step |

**Deliverables:**
- 4 new models with migrations
- Conversations produce persistent session records with full turn history
- Contracts survive garbage collection
- Doc updates create version history

**Acceptance criteria:**
- [ ] `DeliberationSession` created for every HiveMindSession
- [ ] `DeliberationTurn` count matches conversation turn count
- [ ] `ContractRecord` persists ResearchContract/SynthesisContract/ExecutionMandate
- [ ] `DocVersion` created on every `_write_doc()` call with content diff

---

### Phase 2: Strategic Memory Service (1 session, ~3 hours)

**Goal:** Build the meta-query service that makes memory strategic, not just archival.

| Step | File(s) | Change | Blast Radius |
|------|---------|--------|-------------|
| 1 | `core/services/strategic_memory_service.py` (NEW) | Create `StrategicMemoryService` with `query_precedents()`, `get_failure_signatures()`, `recommend_strategy()` | New file |
| 2 | `core/services/strategic_memory_service.py` | `query_precedents()`: Embed query, search AgentMemory (pgvector), search LearningPattern (text), search DecisionRecord (text), rank and return | New service using existing pgvector index |
| 3 | `core/services/strategic_memory_service.py` | `get_failure_signatures()`: Aggregate LearningPattern failures by tool/agent, compute failure rates, identify recurring patterns | New computation on existing data |
| 4 | `core/services/strategic_memory_service.py` | `recommend_strategy()`: Find similar Initiative descriptions via embedding, return success/failure stats and common approaches | Depends on Initiative embeddings (may need to compute) |
| 5 | `core/services/unified_pa_entrypoint.py` | Replace Phase 0 basic memory search with full `StrategicMemoryService` integration | Upgrade existing enrichment |
| 6 | `core/views_deliberation.py` (NEW) | API endpoints: `GET /api/memory/precedents/`, `GET /api/memory/failures/`, `GET /api/memory/strategy/` | New endpoints |
| 7 | `core/urls.py` | Register new URL patterns | Low -- additive |

**Deliverables:**
- "Have we tried this before?" answerable via API
- Failure patterns aggregated and queryable
- Strategic recommendations based on historical outcomes
- PA can proactively surface precedents during conversations

**Acceptance criteria:**
- [ ] `query_precedents("automated content publishing")` returns relevant AgentMemory + LearningPattern + DecisionRecord hits
- [ ] `get_failure_signatures("content")` returns aggregated failure rates by tool
- [ ] `recommend_strategy("Launch crypto trading bot")` returns similar past initiatives with outcomes
- [ ] PA enrichment for `reasoning` intent includes strategic context

---

### Phase 3: Evidence Pack Assembly + Replay UI (1 session, ~4 hours)

**Goal:** Assemble evidence packs during deliberations, build session replay.

| Step | File(s) | Change | Blast Radius |
|------|---------|--------|-------------|
| 1 | `core/services/evidence_pack_builder.py` (NEW) | Create `EvidencePackBuilder` that incrementally assembles evidence packs during sessions | New file |
| 2 | `core/conversation_orchestrator.py` | Wire EvidencePackBuilder: on each turn, extract claims from agent output, track contradictions from tension checks, log memory retrievals | Medium -- adds structured extraction to turn processing |
| 3 | `core/services/session_trace_builder.py` (NEW) | Create `SessionTraceBuilder` that assembles trace JSON from DeliberationTurn + ToolCallRecord + DecisionRecord data | New file |
| 4 | `core/views_deliberation.py` | Add endpoints: `GET /api/sessions/<id>/evidence/`, `GET /api/sessions/<id>/trace/`, `GET /api/sessions/<id>/replay/` | New endpoints |
| 5 | `frontend/src/pages/workspace/tabs/` | New `SessionReplayTab` or sub-tab showing turn-by-turn replay with evidence, claims, decisions | New frontend component |
| 6 | `core/tasks.py` | Celery task `extract_session_learnings` -- post-session, extract LearningPatterns from session outcomes and write to strategic memory | New task |

**Deliverables:**
- Evidence packs assembled automatically during every deliberation
- Full session traces queryable via API
- Frontend replay of any past deliberation session
- Automatic learning extraction from completed sessions

**Acceptance criteria:**
- [ ] Evidence pack JSON validates against schema (Section D)
- [ ] Session trace JSON validates against schema (Section E)
- [ ] Replay endpoint returns ordered turns with evidence context
- [ ] Frontend renders session timeline with expandable turns
- [ ] `extract_session_learnings` creates LearningPatterns from session outcomes

---

### File Touchpoint Summary (All Phases)

| File | Phase | Nature of Change |
|------|-------|-----------------|
| `core/agents/report_schemas.py` | 0 | Extend SourceInfo, Claim dataclasses |
| `core/agents/base_agent.py` | 0, 1 | Track doc reads, version doc writes |
| `core/conversation_orchestrator.py` | 0, 1, 3 | Auto-enforce decisions, create session/turn/contract records, wire evidence builder |
| `core/contracts/research_contract.py` | 0 | Add to_dict() |
| `core/contracts/synthesis_contract.py` | 0 | Add to_dict() |
| `core/contracts/execution_mandate.py` | 0 | Add to_dict() |
| `core/services/unified_pa_entrypoint.py` | 0, 2 | Wire strategic memory enrichment |
| `core/models_deliberation.py` | 1 | **NEW** -- 4 models |
| `core/models_unified_system.py` | 1 | Add FK to HiveMindSession |
| `core/models_conceptforge.py` | 1 | Add FK to ConceptForgeRun |
| `core/services/strategic_memory_service.py` | 2 | **NEW** -- meta-query service |
| `core/views_deliberation.py` | 2, 3 | **NEW** -- API endpoints |
| `core/urls.py` | 2, 3 | Register new URL patterns |
| `core/services/evidence_pack_builder.py` | 3 | **NEW** -- evidence assembly |
| `core/services/session_trace_builder.py` | 3 | **NEW** -- trace assembly |
| `core/tasks.py` | 3 | Add learning extraction task |
| `frontend/src/pages/workspace/tabs/` | 3 | Session replay component |

### Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Migration conflicts with pending branches | Low | Medium | Run migrations in isolation, nullable FKs only |
| Evidence pack assembly slows conversations | Medium | Low | Async extraction, don't block turn processing |
| Memory query performance with large datasets | Medium | Medium | Leverage existing pgvector index, add DB indexes on trace_id/session_id |
| Contract serialization loses type fidelity | Low | Low | Round-trip tests (serialize -> deserialize -> compare) |
| Doc versioning storage growth | Low | Low | Most docs are write-once (handoffs); add retention policy if needed |
| DecisionEnforcer auto-trigger produces unwanted mandates | Low | Medium | Only trigger for debate/planning types; add `auto_enforce=True` flag for opt-out |

---

## Appendix: Cross-Cutting Themes

### Theme 1: trace_id as Universal Connector

The `trace_id` field already appears in:
- `ToolCallRecord.trace_id`
- `DecisionRecord.trace_id`
- `AgentDecisionSummary.trace_id`

Extending trace_id to `DeliberationSession`, `ContractRecord`, and `DeliberationTurn` creates a single thread that connects every artifact produced during a deliberation. Query pattern: `WHERE trace_id = X` across all tables returns the complete audit trail.

### Theme 2: JSONField as Schema Evolution Strategy

The Evidence Pack and Session Trace specs use JSON. Storing them as `JSONField` on `DeliberationSession` allows schema evolution without migrations. Validate against the spec in application code, not at the DB level. Version the spec (`$schema: "evidence-pack-v1"`) so old records remain readable as the spec evolves.

### Theme 3: Incremental Assembly, Not Batch Construction

Both the Evidence Pack and Session Trace are built incrementally during the session, not assembled after the fact. This ensures:
- No data loss if session crashes mid-way
- Real-time visibility into ongoing deliberations
- Lower memory pressure (append-only, not reconstruct-from-scratch)
