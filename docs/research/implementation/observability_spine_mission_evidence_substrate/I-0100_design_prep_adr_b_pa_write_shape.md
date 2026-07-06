---
title: "Arc I-0100 — ADR-B Design Preparation: PA write shape + PA↔LLMCallEvent correlation contract"
authority: design-preparation
status: active
arc_id: I-0100
arc_slug: observability_spine_mission_evidence_substrate
adr_target: ADR-0002
adr_slug_reserved: pa-write-shape-and-correlation-contract
session_authored: 2700
authored: 2026-07-06
authored_by: claude-code (Arc I-0100 Stage 2)
source_finding_refs:
  - 1799 xx99 §1 point 2 (Cat C PA-path AgentExecution coverage is zero)
  - 1799 xx99 §5 D74 six-axis correlation-spine (options for global correlation posture)
  - 1799 xx99 §8.2 T1 items 2–3 (PA→AgentExecution wire + MISSION_RUNNER staged unlock)
  - Arc I-0100 scoping §8 F5 fold (ADR-B MUST specify PA↔LLMCallEvent correlation contract; no dedup)
  - Arc I-0100 scoping §8 F7 fold (Verification-method interface at Stage 1; concrete at Stage 3)
  - Arc I-0100 scoping §9.1 line 2 (Next-step ADR-B pointer — the trigger for this design-prep)
  - Arc I-0100 scoping §5 P4 row (Planned PR sequence for ADR-B outcome discharge)
sign_cycle_1: (pending — will route on arc pin pa-c5b235f7b15f45be per IOS §7.2 v1.4 implementation ADR SIGN cadence)
sign_cycle_1_pin: pa-c5b235f7b15f45be
companion_docs:
  - docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md
  - docs/adr/ADR-0001-establish-adr-corpus.md
  - docs/adr/ADR-0002-pa-write-shape-and-correlation-contract.md (companion ADR authored from this design-prep)
  - core/models_unified_system.py (AgentExecution:882)
  - core/models_llm_telemetry.py (LLMCallEvent:30)
  - core/models_tool_calls.py (ToolCallRecord)
  - core/services/unified_pa_entrypoint.py (PA agentic loop entry)
verifier_loop: |
  Authored 2026-07-06 by Claude Code at Arc I-0100 Stage 2 opening
  ceremony as canonical design-prep artifact for ADR-B per IOS
  v1.4 §4.3 Stage 2. Assessment surfaced that Arc I-0100 scoping
  doc §9.1 did NOT satisfy IOS v1.4 §4.3 Stage 2 design-prep
  equivalence criteria — specifically consequences-per-option
  articulation was under-specified. Chris ratified the Option (a)
  path (author standalone design-prep doc) 2026-07-06 per directive
  "The Stage 1 scoping document should remain a Stage 1 artifact."
  Investigation of code state (core/models_unified_system.py,
  core/models_llm_telemetry.py, core/models_tool_calls.py,
  core/services/unified_pa_entrypoint.py) informed the analysis
  before any option scoring. Design-prep applies §4.3 Stage 2 v1.4
  criteria (decision question + options + constraints + consequences
  + verification implications) as its structural test. This
  document IS the design-prep artifact; ADR-0002 will cite this
  file (not scoping §9.1) as its canonical design source per
  ADR-0001 §3.4 body-section requirement.
---

# ADR-B Design Preparation — PA write shape + PA↔LLMCallEvent correlation contract

**Purpose.** Author the canonical design-prep artifact for `ADR-0002-pa-write-shape-and-correlation-contract.md`. Per IOS v1.4 §4.3 Stage 2, this file resolves the design-prep equivalence gap Arc I-0100 scoping doc §9.1 could not satisfy alone. ADR-0002 will cite this document as its `design-prep` source.

**Scope.** Two coupled decisions:

1. **Which shape does PA use to persist agentic-loop execution telemetry?** Three candidate options.
2. **What is the PA↔LLMCallEvent correlation contract?** Required keys, join path, verification implications. Per Arc I-0100 Rigby SIGN Cycle 1 F5 fold: the contract is Yes-required in ADR-B; dedup is out-of-scope.

**Non-scope.**

- **D74 six-axis correlation-spine posture** — that's ADR-C (`ADR-0004` reserved slug).
- **`MISSION_RUNNER_ENABLED` / `RIGBY_DELEGATION_ENABLED` staged-enable posture** — that's ADR-A (`ADR-0003` reserved slug).
- **`ToolCallRecord.trace_id` write-side fix** — SPEC_COMPLETE per Arc I-0100 scoping §5 P2 row (F3 fold unconditional ship).
- **Retention posture** — F2 fold binds retention as decision INPUT to ADR-C, not ADR-B.

---

## §1. Context: What PA writes today, and the observability gap

### 1.1 Current PA write path

`core/services/unified_pa_entrypoint.py` (`UnifiedPAEntrypoint` class) runs the PA agentic loop:

- **Line 333 `__init__`:** takes `user: User` + `conversation_id: str | None`. `conversation_id` is a string like `pa-c5b235f7b15f45be` — the arc/session SIGN pin conversation identifier, NOT a UUID.
- **Line 826–834:** dispatches tool calls via `tool_dispatcher.execute(...)` passing `conversation_id`, `agent_name='PersonalAssistant'`, and `pa_trace_id=trace_id` (Session 1172 live-ticker join key).
- **Line 3120, 3474, 6382:** treats `agent_execution` as a distinguished intent that routes into `universal_agent_tool`.
- **Line 1771:** injects `_bound_conversation_id` sentinel into tool arguments (Session 1248) for downstream conversation resolution.

**Critical gap (1799 §1 point 2):** the PA agentic loop DOES NOT persist a top-level `AgentExecution` row for its own turn. It only propagates identifiers to downstream tools. If the dispatched tool is a router-registered agent (intent `agent_execution` → `universal_agent_tool`), THAT downstream path writes its own `AgentExecution` row. But the PA's own conversation-driven turn — the one that included the LLM invocation, the intent classification, the tool selection, and the response composition — leaves no `AgentExecution` row.

**Consequence:** every PA-driven `LLMCallEvent` row has `execution_id: NULL`. The `LLMCallEvent.execution_id` docstring explicitly says "NULL for detached calls (tests, scripts, **PA flows with no execution record**)". This is telemetry design intent for tests, not a design intent for the PA production path.

### 1.2 Correlation surfaces that exist but are unwired

- **`core.AgentExecution.conversation_id` (`CharField(max_length=64)`, indexed).** Added Session 1174 PR-1 for "the agent-follow-up wake design." The column IS the intended PA-conversation correlation key. It is populated ONLY by router-agent path today; the PA agentic loop does not create AgentExecution rows to populate it.
- **`core.LLMCallEvent.execution_id` (`UUIDField`, indexed).** Added Session 1098 PR-1 as "UUID of owning AgentExecution." Points at `core_agentexecution.id`. Bidirectional join axis with `AgentExecution.id` (`UUIDField`, primary key).
- **`core.LLMCallEvent.metadata` (`JSONField`).** Docstring: "caller-supplied context (task_id, parent_trace_id, provider-specific options)."
- **`core.ToolCallRecord.trace_id` (`UUIDField`, indexed).** Cat D concern; F1 fold. Not this ADR's scope but shares correlation-spine semantics.
- **`core.ToolCallRecord.conversation_id` (`UUIDField`, indexed).** ⚠️ **Schema type inconsistency:** ToolCallRecord uses `UUIDField` for `conversation_id`; AgentExecution uses `CharField(64)`. The PA passes `conversation_id` as a string (`pa-c5b235f7b15f45be`), which fails UUID validation. This is a pre-existing schema drift finding; noted here for cross-reference but out of ADR-B scope (Cat D adjacent).

### 1.3 What ADR-B must decide

Given the model surface already exists and is unwired for the PA path, ADR-B answers: **at what granularity does PA create AgentExecution rows, and how does LLMCallEvent join them?**

---

## §2. Decision questions (explicit)

**Q1 — Write granularity.** What is one row of the PA-authored `AgentExecution` (or new-model equivalent)? Options: per PA turn, per PA message, or per PA session (rejected — see §5).

**Q2 — Storage location.** Where does the row live? Options: existing `core.AgentExecution`, existing `core.AgentExecution` with span-granularity extension, or new dedicated model.

**Q3 — Correlation keys.** Which fields form the primary key set for PA↔LLMCallEvent join?

**Q4 — Join path.** Given the keys, what is the concrete ORM traversal for "retrieve LLM calls for a PA turn" (verification-method concrete per F7 fold)?

Q1 and Q2 are jointly resolved by choosing one of the three options in §4. Q3 and Q4 are jointly resolved by the correlation contract in §6.

---

## §3. Constraints (from ratified sources)

Constraints ADR-B MUST respect, sourced from ratified upstream artifacts:

| Constraint | Source | Load-bearing implication |
|-----------|--------|--------------------------|
| **PA↔LLMCallEvent correlation contract is Yes-required** | Arc I-0100 scoping §8 F5 fold (Chris ratified) | ADR-B cannot ratify without specifying keys + join. |
| **No dedup semantics in ADR-B** | Arc I-0100 scoping §8 F5 fold (Chris ratified) | ADR-B declares the correlation shape; dedup (identical-call collapse) is a downstream ADR / follow-on concern. |
| **F4 ordering: ADR-B ratifies FIRST** | Arc I-0100 scoping §8 F4 fold (Chris ratified) | Cannot condition ADR-B decision on ADR-A or ADR-C outcomes. |
| **P2 `ToolCallRecord.trace_id` write-side fix ships unconditional** | Arc I-0100 scoping §8 F3 fold (Chris ratified — SIGN-clean) | `trace_id` is a live correlation axis independent of ADR-B storage choice. |
| **Verification-method as INTERFACE at Stage 1; concrete at Stage 3** | Arc I-0100 scoping §8 F7 fold (Chris ratified) | ADR-B must declare the verification interface but leave the concrete Stage 3 query to Stage 3 pre-flight. |
| **P4 rollout is feature-flagged (`PA_AGENT_EXECUTION_WRITE_ENABLED`)** | Arc I-0100 scoping §5 P4 row | ADR-B write path must be off-by-default at first ship. |
| **P4 migration is backward-compatible (nullable/additive-only)** | Arc I-0100 scoping §5 P4 row | ADR-B cannot require altering non-nullable existing columns. |
| **`AgentExecution.conversation_id` field already exists (`CharField(64)`)** | `core/models_unified_system.py:977` Session 1174 PR-1 | Row-schema for PA conversation correlation is pre-built; use it. |
| **`LLMCallEvent.execution_id` field already exists (`UUIDField`, nullable, indexed)** | `core/models_llm_telemetry.py:54` Session 1098 | Cross-model join key pre-built; use it. |
| **`AgentExecution.agent` FK is REQUIRED (`CASCADE`)** | `core/models_unified_system.py:892` | Cannot write PA-authored `AgentExecution` row without a corresponding `Agent` row OR schema relaxation. |
| **`core.AgentExecution` is the LIVE model (not `agents.AgentExecution`)** | `core/models_unified_system.py:995-1008` Session 1084 comment | ADR-B targets `core.AgentExecution`; `agents.AgentExecution` is not written to. |
| **`intelligence.AgentExecution` is a distinct model** | `intelligence/models.py:587` | Action-plan scoped; not the target of ADR-B. |

---

## §4. Options × 5-field consequence matrix

Options evaluated against 5 fields per IOS v1.4 §4.3 Stage 2 design-prep equivalence rule: schema shape, backward compatibility, migration surface, Rigby tool-surface impact, runtime / storage volume implications.

### Option 1 — Per-turn AgentExecution write (using existing model)

One `core.AgentExecution` row per PA turn (user message → PA agentic loop → response). `agent` FK points at a canonical `PersonalAssistant` Agent row (data-migration prerequisite OR make `agent` FK nullable — see §4.1.C). `input_data['source'] = 'pa'` marker per existing convention. `conversation_id` populated from `UnifiedPAEntrypoint.conversation_id` (string form). `LLMCallEvent.execution_id` populated during the LLM call wrapper by looking up the current PA turn's `AgentExecution.id` via thread-local or explicit dispatch context.

| Field | Consequence |
|-------|-------------|
| **Schema shape** | Uses `core.AgentExecution` as-is. Fields written on each PA turn: `id` (auto UUID), `agent` (FK to canonical PA agent row), `user`, `task` (initial user message text or turn intent), `status`, `input_data['source']='pa'`, `input_data['intent']=<detected>`, `input_data['tool_selected']=<name>`, `output_data['response']=<text>`, `input_data['trace_id']=<pa_trace_id>`, `conversation_id`, `created_at`, `completed_at`, `tokens_used`, `execution_time_ms`. Existing `owner_agent` field (Session 843) hosts `'PersonalAssistant'`. Existing `parent_execution_id` remains NULL for top-of-loop rows; child dispatches populate it. |
| **Backward compatibility** | No changes to existing `AgentExecution` row shape. Router-agent-path writes continue writing exactly as they do. Consumers of `AgentExecution.objects.filter()` see NEW row-type marked by `input_data['source']='pa'`. Downstream tools that filter by `agent__name` see 1 new agent name (`'PersonalAssistant'`) OR (if FK relaxed) rows with NULL agent. **Recommended:** existing tools filter by `input_data__source` when PA-specific queries are wanted; existing "all agents" queries include PA rows naturally. Session 1084 comment confirms `core.AgentExecution` is the live model — no cross-model coordination risk. |
| **Migration surface** | Either (a) **data migration** creating a canonical `PersonalAssistant` `Agent` row (~5 lines RunPython), OR (b) **schema migration** making `AgentExecution.agent` nullable + blank (2-line AlterField). Chris/Rigby choose per §7. Both are backward-compatible (add-only / nullability relaxation). Backfill NOT required — existing rows unchanged. |
| **Rigby tool-surface impact** | `execution_history_tool.recent(user_id=<uid>)` naturally returns PA rows alongside router-agent rows — a strict improvement (currently PA turns are invisible). `ops_tool.execution_summary` includes PA in agent breakdown. `deliverable_provenance_tool.trace` extends by traversing `AgentExecution.parent_execution_id` from a deliverable → creating agent execution → PA row that spawned it. No new tool needed. Filter args on existing tools can add optional `source='pa'` for PA-specific views. |
| **Runtime / storage volume implications** | **~1 row per PA turn.** At current PA cadence (informal estimate — needs measurement at Stage 3): if avg 10 turns per active session per day × 3 active users × 30 days = ~900 rows/month. Compared to current router-agent write volume (58 rows in 2h local per Session 1084 comment = ~7000/day), PA adds ~0.4% write volume. Index cost negligible. `conversation_id` index (Session 1174) already sized for this. `LLMCallEvent.execution_id` index (Session 1098 llm_call_exec_time) benefits — currently 0 rows have execution_id for PA calls; ADR-B populates them. |

### Option 2 — Per-message span (using existing model + new granularity field)

One row per PA "message-level event": user message received, intent classification, tool selected, tool executed, response composed. Requires a new discriminator field (e.g., `AgentExecution.span_type` CharField choices `[turn, message, tool_span]`). One turn = 1 turn-row + N message-rows children (`parent_execution_id` FK).

| Field | Consequence |
|-------|-------------|
| **Schema shape** | Adds `span_type` field to `core.AgentExecution` (`CharField(max_length=20, choices=[('turn','Turn'),('message','Message'),('tool_span','Tool Span')], db_index=True, default='turn')`). Adds `span_sequence` IntegerField for within-turn ordering. Existing `parent_execution_id` becomes load-bearing — every message/tool_span row FKs to its turn row. Fields written per row: same as Option 1 subset + `span_type` + `span_sequence`. |
| **Backward compatibility** | Existing rows implicitly become `span_type='turn'` (via default). Router-agent path also writes span_type=`turn` for its own executions (consistent semantics). Consumers of `AgentExecution.objects.filter(...)` see 3–5× more rows per PA turn — **queries that count executions as "one per user action" break unless they add `.filter(span_type='turn')` OR migrate to a new aggregation.** This is the primary compatibility risk. |
| **Migration surface** | (a) `AddField(span_type, default='turn')` + (b) `AddField(span_sequence, default=0)`. Backfill sets `span_type='turn'` on all existing rows (deterministic). One-shot backfill script over `core_agentexecution` (~62K rows per prod estimate) — reasonable. Additionally requires code sweep to add `.filter(span_type='turn')` to any query that currently counts "one execution per user request" (probability of drift: HIGH given AgentExecution is used across ops_tool / cleanup / dedup / dashboards / router). Blast radius: SUBSYSTEM at minimum. |
| **Rigby tool-surface impact** | `execution_history_tool.recent` returns 3–5× more rows per PA session unless filtered — noisy for a user browsing recent history. Requires `granularity='turn'` (default) vs `granularity='message'` (verbose) argument, which is a tool-schema change. `ops_tool.execution_summary` needs the same filter. `deliverable_provenance_tool.trace` walks a deeper tree per turn — potentially useful for debugging but more expensive. New tool `pa_message_trace_tool` reasonable follow-on. |
| **Runtime / storage volume implications** | **~3–5 rows per PA turn.** Under same estimate: 3000–4500 rows/month for PA (~1.5–2% of current write volume). Still small in absolute terms but 3–5× Option 1. `parent_execution_id` index cost increases proportionally. `conversation_id` index size 3–5×. Query performance for turn-level views degrades unless indexes co-tuned on `(span_type, conversation_id)` OR `(span_type, created_at)`. |

### Option 3 — Dedicated `PAAgentExecution` model

New model `core.PAAgentExecution` (or `pa.PAAgentExecution` in a new app). Field shape mirrors `AgentExecution` but PA-only. `LLMCallEvent` gains a NEW field `pa_execution_id` (UUIDField, nullable, indexed) OR polymorphs `execution_id` semantics via `execution_kind` discriminator.

| Field | Consequence |
|-------|-------------|
| **Schema shape** | New model in `core/models_pa_execution.py`: `id` UUIDField PK, `user` FK, `conversation_id` CharField(64) indexed (SAME as AgentExecution.conversation_id — direct parity), `pa_turn_id` UUIDField indexed, `trace_id` UUIDField indexed, `input_data` JSONField, `output_data` JSONField, `status`, `tokens_used`, `execution_time_ms`, `created_at`, `completed_at`. Deliberately omits `agent` FK (no shim required). `LLMCallEvent.execution_id` semantics EITHER (a) extended to accept both AgentExecution.id and PAAgentExecution.id (breaks type safety; requires `execution_kind` discriminator) OR (b) `LLMCallEvent` gains new `pa_execution_id` field, `execution_id` remains AgentExecution-scoped. |
| **Backward compatibility** | Existing `AgentExecution` writes and consumers unchanged (strict isolation). No router-agent code touches PA model. But `LLMCallEvent` correlation semantics FRAGMENT — dashboards / ops_tool queries that "give me all LLM calls with their execution" must now UNION across two tables OR check `execution_kind`. `execution_history_tool.recent` cannot show PA + router-agent rows in one call without a UNION query. `deliverable_provenance_tool.trace` must decide which table to walk (probability of misroute if a PA turn spawned a downstream router-agent execution: NON-ZERO — cross-model parent chains). |
| **Migration surface** | New migration `NNNN_add_pa_agent_execution.py` — `CreateModel` for `PAAgentExecution` + `AddField(pa_execution_id)` on `LLMCallEvent` OR `AddField(execution_kind, default='router_agent')` on `LLMCallEvent` + backfill. Migration is additive (no altering existing rows' meaning) but adds 1 new table + 1 new column on a hot-write table. Two-migration sequence (create table then modify LLMCallEvent) to blue/green safely. |
| **Rigby tool-surface impact** | `execution_history_tool.recent` needs a NEW code path or UNION-based query rewrite. `ops_tool.execution_summary` similarly. New tool `pa_execution_tool` may be justified. `deliverable_provenance_tool.trace` complexity roughly 2×. Rigby's mental model shifts from "one execution table" to "two". Documentation, agent examples, and existing memory rules referencing `AgentExecution` become partially wrong. |
| **Runtime / storage volume implications** | **~1 row per PA turn (same as Option 1, different table).** `PAAgentExecution` table isolates writes — potentially useful for future PA-specific retention posture. But total DB storage unchanged. Query performance for cross-model views slightly worse (UNION cost). Index parity effort doubles. |

### Option 4 (rejected — noted for completeness): Per-session AgentExecution

One row per PA session (all turns in one row). Rejected because it collapses per-turn correlation entirely — impossible to associate LLMCallEvent with a specific turn within a session. Violates F5 correlation contract requirement.

---

## §5. Pressure test — Which option best satisfies constraints?

Each option scored against the constraint set in §3 + judgment on ADR-B decision quality:

| Test | Option 1 (per-turn AgentExecution) | Option 2 (per-message span) | Option 3 (dedicated PAAgentExecution) |
|------|-----------------------------------|----------------------------|--------------------------------------|
| **Satisfies F5 correlation contract (Yes-required)** | ✅ `LLMCallEvent.execution_id → AgentExecution.id` uses existing keys | ✅ same as Option 1, plus optional finer join on span rows | ⚠️ requires new `pa_execution_id` field OR `execution_kind` polymorphism |
| **Additive-only migration (per P4 rollout constraint)** | ✅ (data migration for canonical PA agent row) OR (nullable FK relaxation) | ⚠️ requires code sweep for `.filter(span_type='turn')` in existing queries — non-trivial | ✅ (new model + new column, both additive) |
| **Backward-compatible for existing consumers** | ✅ (with `input_data['source']='pa'` marker filterable) | ❌ (execution-count queries break silently unless every consumer is patched) | ⚠️ (fragments correlation semantics; existing "join LLMCallEvent to execution" queries need UNION or discriminator) |
| **Uses pre-existing model surface (Session 1174 conversation_id + Session 1098 execution_id)** | ✅ direct fit — Session 1174 PR-1 comment says the field was added precisely for this | ✅ same, plus new span_type field | ❌ duplicates 90%+ of AgentExecution schema |
| **Rigby tool-surface disruption** | LOW — filter args optional | MEDIUM — granularity args + query cost increase | HIGH — cross-model UNIONs + new tools |
| **Storage volume** | ~1 row / turn | 3–5 rows / turn | ~1 row / turn (different table) |
| **Verification-method concrete query at Stage 3 (per F7)** | `AgentExecution.objects.filter(input_data__source='pa', conversation_id=<pin>)` — 1 line | `AgentExecution.objects.filter(input_data__source='pa', span_type='turn', conversation_id=<pin>)` — 1 line, more brittle | `PAAgentExecution.objects.filter(conversation_id=<pin>)` OR UNION — 2+ lines |
| **Post-arc follow-on debt** | LOW (design-prep debt: 0) | MEDIUM (code sweep debt for `.filter(span_type='turn')` across ~25 call sites estimated) | HIGH (dual-model migration debt if we later want to unify) |
| **Blast radius per §5.0 term-definitions** | LOCAL–SUBSYSTEM | SUBSYSTEM–CROSS_DOMAIN | SUBSYSTEM–CROSS_DOMAIN |
| **Reversibility per ADR-0001 §3.5 scale** | 4 (data / nullable migration reversible with modest effort) | 2 (once queries adapt, reverting requires code sweep + backfill of new field to NULL) | 2 (new table cannot be removed without data migration; polymorphism changes to LLMCallEvent are 1) |

**Pressure-test verdict:** Option 1 dominates on 6 of 10 criteria, ties on 1, loses on 0. Option 2's per-message granularity has real observability value but its backward-compatibility cost is severe (silent breakage of "count executions per user action" query semantic across ~25 estimated call sites). Option 3's isolation appeal is real but the correlation-fragment cost violates F5's "PA↔LLMCallEvent join is Yes-required" via a strict reading (the join now goes through a discriminator or two tables, not the single execution_id join current dashboards expect).

**Non-blocking counter-arguments (kept for ADR §5 Alternatives):**

- **Option 2 per-message value.** Finer granularity IS useful for debugging tool-selection heuristics. Recommendation: adopt Option 1 for storage; add a follow-on ADR (post-arc) if per-message telemetry becomes a live operator need. Store per-message events in `AgentExecution.input_data['events']` JSON blob for now (already permitted by schema; low cost; recoverable).
- **Option 3 isolation value.** Retention posture might one day want to prune PA-execution rows more aggressively than router-agent rows (compliance-driven). Option 1 preserves this option — a future retention-tier ADR can target `input_data__source='pa'` filter for differential retention without a schema change.

---

## §6. Correlation contract (PA↔LLMCallEvent)

Per F5 fold: ADR-B MUST specify keys + join path. No dedup semantics.

### 6.1 Required keys

| Field | Model | Type | Purpose |
|-------|-------|------|---------|
| `AgentExecution.id` | `core.AgentExecution` | UUIDField (PK) | Owning-execution identity |
| `LLMCallEvent.execution_id` | `core.LLMCallEvent` | UUIDField, nullable, indexed | FK-shape (no DB FK constraint) pointer to `AgentExecution.id` |
| `AgentExecution.conversation_id` | `core.AgentExecution` | CharField(max_length=64), indexed | PA session pin (`pa-<hex>`) — Session 1174 PR-1 |
| `AgentExecution.input_data['trace_id']` | `core.AgentExecution` | JSONField key | PA trace_id (existing `pa_trace_id` from `UnifiedPAEntrypoint`, Session 1172 live-ticker join key) — carried into `LLMCallEvent.metadata['pa_trace_id']` for cross-join |
| `AgentExecution.input_data['source']` | `core.AgentExecution` | JSONField key | Discriminator: `'pa'` for PA-authored rows |

**Chosen contract:** `LLMCallEvent.execution_id == AgentExecution.id` is the primary correlation join. `conversation_id` and `trace_id` are secondary axes for cross-session / cross-turn aggregation.

### 6.2 Join path (ORM traversals)

- **From a PA turn → its LLM calls:**
  ```python
  AgentExecution.objects.filter(input_data__source='pa', conversation_id=<pin>).values('id').first()
  # then:
  LLMCallEvent.objects.filter(execution_id=<agent_execution_id>)
  ```
- **From an LLM call → its PA turn:**
  ```python
  LLMCallEvent.objects.filter(call_id=<call_uuid>).values('execution_id').first()
  # then:
  AgentExecution.objects.filter(id=<execution_id>)
  ```
- **For a PA session (across turns):**
  ```python
  AgentExecution.objects.filter(input_data__source='pa', conversation_id=<pin>).order_by('created_at')
  ```

### 6.3 Verification implications (per F7 interface)

Stage 3 pre-flight concrete verification queries (deferred implementations):

1. **Rigby-exercisable:** `execution_history_tool.recent(user_id=<uid>, source='pa', limit=10)` returns non-empty for any PA-active user after PR P4 ships and `PA_AGENT_EXECUTION_WRITE_ENABLED=True`.
2. **Claude-verifiable ORM probe:** `AgentExecution.objects.filter(input_data__source='pa', created_at__gte=<T>).count() > 0` post-flag-enable.
3. **Correlation verification:** for a sampled PA-source `AgentExecution`, `LLMCallEvent.objects.filter(execution_id=<id>).exists() == True` when at least one LLM call was made during that turn.
4. **Interface stability:** `deliverable_provenance_tool.trace(deliverable_id=<id>)` returns chain that traverses PA execution → downstream router agent execution → deliverable when applicable.

Stage 5 verify per F7 fold: all four checks Rigby-exercised on real PA traffic ≥24h post-enable.

### 6.4 What is NOT in the contract

- **Dedup logic (identical-call collapse).** Explicit F5 fold: "WITHOUT implementing dedup." Deferred to post-arc follow-on ADR if a live operator need surfaces.
- **Retry-correlation.** `LLMCallEvent.retry_count` field exists; usage is per-call, not per-execution. ADR-B leaves retry semantics to LLMCallEvent internal shape.
- **Nested-dispatch chain.** `AgentExecution.parent_execution_id` + `root_execution_id` (Session 1098 PR #4) already implement cancel/budget lineage. PA turn parent chain uses these existing fields; no new mechanism.
- **Provider-specific tags.** `LLMCallEvent.metadata` free-form; provider tag semantics not ADR-B scope.

---

## §7. Recommendation

**Adopt Option 1 (per-turn AgentExecution write using existing model).**

Rationale:

1. **Uses ratified pre-existing schema.** Session 1174 PR-1 explicitly added `AgentExecution.conversation_id` for PA correlation. Session 1098 added `LLMCallEvent.execution_id` for the join. The pre-work is done; ADR-B activates it.
2. **Minimal blast radius.** LOCAL–SUBSYSTEM. Reversible-4. Backward-compat via `input_data['source']='pa'` marker.
3. **Discharges P4 as intended.** Arc I-0100 scoping §5 P4 row already sketched `core/models_unified_system.py (potential FK addition) OR core/models_pa_execution.py (new model per ADR-B option 3)` — Option 1 selects the "no new model" branch.
4. **F5 correlation contract satisfied cleanly.** `LLMCallEvent.execution_id == AgentExecution.id` — one join, one key, existing indexes.
5. **F7 verification-method interface produces a single concrete Stage 3 query,** simpler than Options 2/3.
6. **Preserves future flexibility.** Option 2 (per-message telemetry) can layer atop Option 1 as JSON events in `input_data['events']` initially; a full per-message row model can be introduced later as a distinct ADR if operator need demands. Option 3's differential-retention argument survives via `input_data__source='pa'` filter in a future retention ADR.

### 7.1 Sub-decision: PA `Agent` FK — data migration OR schema relaxation?

Because `core.AgentExecution.agent` is a non-nullable CASCADE FK, Option 1 requires either:

- **Sub-option (i) Data migration:** create canonical `Agent(name='PersonalAssistant', category='meta', ...)` row via `RunPython`. FK never touches NULL. **~5 lines RunPython + 5 lines reverse_migration.**
- **Sub-option (ii) Schema relaxation:** `AlterField(agent, null=True, blank=True)`. All PA-authored rows have `agent=NULL`; `owner_agent` CharField remains as human-readable marker. **~5 lines AlterField migration; must audit consumers assuming `agent` is non-null (probability of drift: LOW because CASCADE FK semantics historically enforce non-null; but not zero).**

**Recommendation:** Sub-option (i) data migration. Reasons: (a) preserves the FK-non-null invariant that consumers rely on; (b) allows `Agent.category='meta'` to become the discriminator for future meta-agent rows (Rigby-Concierge, mission runners, etc.); (c) `PersonalAssistant` as a canonical `Agent` row is arguably a truth-of-the-platform statement ("PA is an agent") that the schema currently obscures. Sub-option (ii) remains valid — Chris/Rigby may prefer nullable if PA-as-agent is philosophically resisted.

Both sub-options are ADR-B decisions (must ratify one). Both are backward-compat and reversible.

### 7.2 Stage 3 pre-flight follow-ons (out of scope for ADR-B ratification, in scope for Stage 3)

- Bounded consumer sweep for `AgentExecution.objects.filter(...)` sites — verify all handle `input_data__source='pa'` rows correctly.
- Bounded sweep for `AgentExecution.agent` non-null assumptions (if Sub-option (ii) chosen).
- Backfill script decision — populate `AgentExecution.conversation_id` for historical rows OR accept sparse historical data (recommendation: accept sparse; PA turn granularity did not exist pre-flag).
- Concrete verification queries per §6.3, fully filled with production data samples.

---

## §8. Alternatives considered

Full alternative enumeration for ADR-0002 §5 to inherit:

- **Option 1 per-turn AgentExecution (RECOMMENDED)** — §4 Option 1 above.
- **Option 2 per-message span** — §4 Option 2 above. Rejected: silent-breakage cost across ~25 call sites; per-message value achievable via JSON events post-arc.
- **Option 3 dedicated PAAgentExecution model** — §4 Option 3 above. Rejected: fragments correlation semantics; violates F5 clean-join intent.
- **Option 4 per-session AgentExecution** — Rejected in §4: collapses per-turn correlation entirely; violates F5 join granularity.
- **Sub-option 1(i) data migration for PA Agent row (RECOMMENDED)** — §7.1.
- **Sub-option 1(ii) schema relaxation to nullable FK** — §7.1. Valid alternative.

---

## §9. Provenance

- **Design-prep author:** Claude Code, Arc I-0100 Stage 2 opening ceremony session (2026-07-06).
- **Consumed sources:**
  - Arc I-0100 scoping doc §5 P4 + §7 R1/R2/R3 + §8 F5/F6/F7 folds + §9.1 + §9.3
  - 1799 xx99 §1 verdict + §5 D74 correlation-spine + §8.2 T1 items 2–3
  - `core/models_unified_system.py:882-989` (AgentExecution)
  - `core/models_llm_telemetry.py:30-116` (LLMCallEvent)
  - `core/models_tool_calls.py:40-108` (ToolCallRecord)
  - `core/services/unified_pa_entrypoint.py:333, 595, 820-834, 1761-1773, 3120-3474, 6382` (PA agentic loop entry)
  - `core/agent_router.py:102, 464, 595, 2432` (PersonalAssistantAgent removal history)
  - Session 1174 PR-1 comment (conversation_id addition)
  - Session 1098 PR-1 comment (LLMCallEvent + execution_id design)
  - Session 1084 comment (AgentExecution canonical-live-model verdict)
- **Rigby SIGN Cycle 1 target:** pending; will route on arc pin `pa-c5b235f7b15f45be` per IOS §7.2 v1.4 (single-batch × 4-Q on PA-write shape + correlation contract + rollout + risks — see companion ADR-0002 authoring for the SIGN plan).
- **Chris ratification target:** ADR-0002 body (not this design-prep). Design-prep does not need standalone ratification per IOS §4.3 Stage 2 — it is Chris-visible via the ADR-0002 PR body cite + optional standalone review.

---

## §10. What this design-prep taught us about how to do design-prep

Meta-note per §4.3 Stage 2 v1.4 introduction of design-prep equivalence:

- **Consequences-per-option is the hardest field to satisfy from scoping-doc-only pre-scoping.** Scoping doc §9 typically names options and constraints but does not thread each option through 5 fields. This is exactly the gap that necessitated authoring this standalone design-prep — and it is likely a recurring pattern, not a one-off.
- **Reading upstream code before evaluating options materially changed the analysis.** The pre-existing `AgentExecution.conversation_id` field (Session 1174 PR-1) is the single most decisive fact for Option 1's dominance; scoping doc §9 did not surface it because scoping doc is a Stage 1 artifact and Stage 1 does not read code at that level.
- **Sub-decisions inside an option (§7.1 data migration vs schema relaxation) can be as load-bearing as the top-level option choice.** ADR-B ratifies BOTH the top-level (Option 1) AND the sub-decision (1(i) or 1(ii)).

These observations feed into task #39 evaluation of whether design-prep should become a first-class IOS artifact.

---

**END DESIGN-PREP DOCUMENT — canonical design source for `ADR-0002-pa-write-shape-and-correlation-contract.md`.**
