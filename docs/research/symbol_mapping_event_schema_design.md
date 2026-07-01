---
title: Symbol Mapping v0 — Event Schema Design (authority_action_observed)
session: 1275
date: 2026-07-01
status: draft (Rigby SIGN-with-edits folded; awaiting Chris canonical sign-off)
authors: Claude Code (Chris directed); Rigby SIGN review folded
supersedes: none
related:
  - docs/research/symbol_mapping_option_selection_design.md (S1274 — Option E selection)
  - docs/research/symbol_mapping_architecture.md (S1270 — architectural framing)
  - docs/research/actor_identity_attribution_architecture.md (S1271 — 3-role actor vocabulary)
  - docs/research/authority_enforcement_design_space.md (S1272 — enforcement design space)
  - docs/research/governance_authority_evolution.md (S1269 — governance evolution)
  - docs/AUDIT_FINDINGS.md §12 (S1115 Celery deferred-by-policy list)
  - core/management/commands/audit_celery_zero_fire.py (S1245 zero-fire detector)
  - core/services/doc_claim_verification.py (S1099 claim-verification framework)
scope: v0 event schema — field-by-field, producer cohort, drift detection
non_goals:
  - implementation PRs (this is a design doc)
  - authority enforcement policy (S1272 covers that)
  - actor identity redesign (S1271 covers that)
  - selection of Option A/B/C/D/E vs alternatives (S1274 already decided — E)
---

# Symbol Mapping v0 — Event Schema Design

**Status:** draft — Rigby SIGN-with-edits folded (8 must-fixes + bonus #9); awaiting Chris canonical sign-off
**Session:** 1275
**Author:** Claude Code (Chris directed) · Rigby SIGN review folded
**Predecessor:** S1274 Option Selection Design (Option E: evidence-only)
**Successor:** implementation PRs (out of scope — this doc is design-only)

---

## 1. Executive Summary

### 1.1 The problem this doc solves

S1274 recommended **Option E (evidence-only mapping)** as the v0 approach to Symbol Mapping: enrich existing audit rows with a small set of new fields so the platform can answer *"which authority-scoped action did this runtime event represent?"* without inventing a new authoritative registry. S1274 stopped one step short of the concrete schema.

This doc defines that schema:

- **The canonical event name**
- **The exact field set (what's required, what's optional, what stays NULL)**
- **Which of the platform's existing audit surfaces hosts it**
- **Which 3–5 runtime producers emit it first**
- **How each producer populates `action_class`**
- **How the platform detects wrong-but-non-NULL mappings before they corrupt downstream reasoning** (S1274 Rigby must-fix #3 §12.1)
- **What is *explicitly* out-of-scope for v0**

### 1.2 The one-sentence recommendation

Emit a new logical event `authority_action_observed` as **a two-surface stream** — mission-scoped emissions extend `OpsRunEvent` (new `label` + JSONField key namespace), non-mission tool-call emissions extend `ToolCallRecord.parameters` under the same namespaced key, and downstream consumers read a unified `authority_action_observed_stream` view that `UNION ALL`s both surfaces — populated by **four v0 emitters plus one first consumer** (MissionRunner authority warn-mode preflight, MissionRunner step lifecycle, ToolDispatcher `execute()`, `employee_tool` `run_now`; first consumer = Bug Triage step 4), with **`action_class` populated only where confidence is DEFINITE or DECLARED and DECLARED is treated as non-authoritative** (coverage dashboards only, never enforcement), `mapping_confidence` explicitly declared per row, and drift detection reusing the S1245 zero-fire detector pattern plus the S1099 claim-verification framework plus a new sampled-truthing loop that catches wrong-but-non-NULL mappings without triggering false-positive storms.

### 1.3 The single most dangerous failure mode

Per S1274 Rigby must-fix #3 (§12.1): a **wrong-but-non-NULL `action_class`** is more dangerous than NULL. NULL shows up in dashboards; a wrong non-NULL looks correct and silently corrupts every downstream consumer. Section 12 of this doc treats drift detection as a first-class deliverable, not an afterthought.

### 1.4 What this doc is not

- Not an implementation plan. No PRs are proposed. No file diffs are given.
- Not a re-litigation of S1274 Option E vs alternatives. That decision is settled.
- Not a policy design. Authority enforcement (fail-open vs. fail-closed, grace periods, exemptions) belongs to S1272.
- Not an actor identity redesign. The 3-role vocabulary (`executor_actor` / `sponsor_actor` / `principal_user`) is settled in S1271 and honored here without re-derivation.

---

## 2. Scope and Non-Goals

### 2.1 In scope

| # | Deliverable |
|---|---|
| S1 | Canonical event name for the new observation |
| S2 | Minimum viable schema — every field, every type, every nullability rule |
| S3 | Choice of host audit surface (which existing model, with rationale) |
| S4 | First producer cohort (3–5 concrete emitters) |
| S5 | `action_class` population strategy per producer |
| S6 | `mapping_confidence` operational semantics |
| S7 | Actor role population strategy per producer (3 roles, kept separate) |
| S8 | Drift / data-quality detection strategy (NULL rate, wrong non-NULL, stale producer, cross-source conflict) |
| S9 | First golden flows (concrete test cases) |
| S10 | v0 dashboard / query API shape |
| S11 | Migration + rollout plan (no code — sequencing only) |
| S12 | Explicit out-of-scope list |
| S13 | Open questions for Rigby |

### 2.2 Out of scope

| # | Non-goal | Where it lives instead |
|---|---|---|
| N1 | Enforcement policy (fail-open vs. fail-closed) | S1272 authority_enforcement_design_space.md |
| N2 | Authority level graduation policy (warn → soft-block → hard-block) | S1272 + Chief of Staff future work |
| N3 | Actor vocabulary changes | S1271 actor_identity_attribution_architecture.md — locked |
| N4 | New event surface (creating a new model instead of reusing OpsRunEvent) | Section 5 explicitly rejects this |
| N5 | Fleet-side event emission | Fleet apps out of scope — v0 is unified-donkey-betz only |
| N6 | WebSocket / Spider producers | S1274 §8.8: NOT covered at v0 (generalization is end-state) |
| N7 | Real-time drift dashboard | v0 ships batch-mode drift audit; real-time is v1 |
| N8 | Cross-repo `symbol_registry` catalog | Explicitly the Option A/B/C/D approach — rejected in S1274 |
| N9 | LLM-based action_class inference | v0 producers populate action_class from structured sources only |
| N10 | Backfill of historical rows | v0 is forward-looking; historical `OpsRunEvent` rows keep NULL action_class |

### 2.3 Assumptions inherited from prior sessions

The following are treated as **settled facts** and are not re-derived here:

- **S1271 F11:** `executor_actor`, `sponsor_actor`, `principal_user` are three separate fields — never collapsed. Enforced by this schema.
- **S1272 §11:** Symbol Mapping is at the critical-path root of a 15-prereq DAG. Nothing else in the enforcement stack can proceed until v0 ships.
- **S1274 §8.8 (Rigby must-fix #1):** Coverage at v0 is narrow — 2 MissionRunner emissions, 4 lifecycle hooks, ~14 authority strings. **Not** Fleet, **not** WebSocket, **not** Spider. Generalization is end-state, not v0.
- **S1274 §10.3.1 (Rigby must-fix #2):** Catastrophic-action graduation guardrail — 4 telemetry triggers force Chris-decision within 30 days. Not this doc's problem; enforced downstream.
- **S1274 §11 (Rigby must-fix #4):** `employee_handle` is Employee OS identity (NULL for non-mission actions); `executor_actor` is generalized runtime executor. **This doc treats them as distinct fields.**
- **S1264 warn-mode precedent:** `authority_contract_observed` event already exists (MissionRunner preflight). v0 does *not* rename it; the new `authority_action_observed` complements it.
- **CELERY_TASK_EVENT_RETENTION_DAYS = 30** — the retention model reused for the new event.

---

## 3. Design Questions

The 11 primary design questions this doc must answer (per S1275 mission spec):

| # | Question | Answered in § |
|---|---|---|
| Q1 | What is the canonical event name? | §6 |
| Q2 | What is the minimum viable schema? | §7 |
| Q3 | Which existing audit surface hosts it? | §5 |
| Q4 | Which 3–5 emitters (+ first consumer) go first? | §8 |
| Q5 | How is `action_class` populated per producer? | §10 |
| Q6 | How does `mapping_confidence` work? | §11 |
| Q7 | How are the 3 actor roles populated? | §9 |
| Q8 | How does the design prevent wrong-but-non-NULL false confidence? | §12 |
| Q9 | What are the first golden flows? | §13 |
| Q10 | What does the v0 dashboard / query API look like? | §14 |
| Q11 | What is explicitly out of scope for v0? | §2.2 + §16 |

---

## 4. Prior Art on the Platform

Evidence gathered by five parallel Explore sub-agents. Full evidence bundles in Appendix C.

### 4.1 Audit surface inventory (Sub-Agent 1)

Seven audit-capable models were inventoried:

| Model | Actor fields | JSONField | Retention | v0 fit |
|---|---|---|---|---|
| `OpsRunEvent` | via parent `OpsRun` (weak) | `data` ✓ | none documented | **primary** |
| `ToolCallRecord` | `agent_name` CharField + `user` FK | `parameters` ✓ | none documented | secondary |
| `LLMCallEvent` | `execution_id` link to AgentExecution | `metadata` ✓ | 30 days | secondary |
| `CeleryTaskEvent` | none | **NO JSONField** (migration required) | 30 days | reject |
| `AgentExecution` | `user` FK + `owner_agent` CharField | `input_data`/`output_data` ✓ | none | reject (deprecated per Session 287) |
| `DeliverableEvent` | `user` FK | `metadata` ✓ | none | tertiary |
| `DirectMessage` | `sender` FK + `sender_type` enum | `metadata` ✓ | none | reject (comms surface, not audit) |

**Key finding:** `OpsRunEvent` alone lacks a `user` FK. Its `OpsRun` parent has `job_contract` FK but no `user`. This is the largest structural gap — mitigated in §7 by adding a nullable `principal_user_id` field to the event payload.

### 4.2 Producer candidates (Sub-Agent 2)

Ranked 5 v0 candidates by coverage-per-emit:

| # | Producer | Site | Rationale |
|---|---|---|---|
| 1 | MissionRunner authority warn-mode preflight | `core/employees/mission_runner.py:835-900` | Highest-value single site — reads `JobContract.authority` dict directly, so `action_class` is DEFINITE |
| 2 | MissionRunner step lifecycle | `core/employees/mission_runner.py:904-962` | 4 hooks per step (start/success/error/timeout); high volume, populates executor via step.fn |
| 3 | ToolDispatcher `execute()` | `core/services/tool_dispatcher.py:585-720` | Universal tool-call site — all 3 actor roles available at emission |
| 4 | `employee_tool` `run_now` | `core/services/td_handlers_employee.py:212-300` | HTTP→Celery drop boundary (S1271 F6-a); sponsor+executor known, principal from request |
| 5 | Bug Triage step 4 aggregation | `core/jobs/bug_triage.py:396-453` | *Consumer*, not producer; demonstrates event usefulness for downstream reasoning |

Estimated v0 coverage per Sub-Agent 2: 35–44% of authority strings, 33–42% of modes, 25–30% of boundaries. Aligned with S1274 §8.8 narrow-coverage caveat.

### 4.3 Actor role availability (Sub-Agent 3)

Per producer × per role:

| Producer | executor_actor | sponsor_actor | principal_user | Notes |
|---|---|---|---|---|
| MissionRunner preflight | knowable (`employee_handle`) | NULL (system-initiated) | knowable via `OpsRun.principal_user` (needs add) | S1271 F4 delegator/executor ambiguity applies |
| MissionRunner step lifecycle | `step.fn.__qualname__` | inherited from mission | inherited from mission | S1271 F6-c: step boundary drops user context |
| ToolDispatcher | `agent_name` (CharField) | `owner_agent` (from calling AgentExecution) | `user` FK | **All 3 roles present** — cleanest producer |
| employee_tool run_now | Employee handle | HTTP requester | HTTP requester | Sponsor + principal usually same at HTTP entry |
| Bug Triage (consumer) | — | — | — | reads events, doesn't emit |

**S1271 F4 warning:** `agent_name` CharField at ToolDispatcher may be either delegator or executor — depends on caller. This doc requires the field to hold **executor** at emission, with delegator (if any) carried in the JSONField payload.

### 4.4 action_class population (Sub-Agent 4)

Ranked by population confidence:

| Producer | action_class source | Confidence |
|---|---|---|
| MissionRunner authority preflight | `JobContract.authority[action_key]` | **DEFINITE** — direct read |
| MissionRunner step lifecycle | needs new `Step.action_class` declaration | UNKNOWN pre-declaration |
| ToolDispatcher | needs new tool-schema `action_class` field | DECLARED (require tool schema extension) |
| LLM/Deliverable/DirectMessage | not populated | NULL at v0 |

**Critical finding (Sub-Agent 4):** it is unknown which `action_class` corresponds to *the mission itself* (mission-trigger action). Sub-Agent 4 proposes a new `JobContract.mission_trigger_action_class` field. This doc adopts that proposal (§10.1).

### 4.5 Drift / data-quality detection (Sub-Agent 5)

Prior-art scan of 10 detection categories:

| # | Category | Precedent | Strength |
|---|---|---|---|
| 1 | NULL rate monitoring | none dedicated | needs bespoke build |
| 2 | Wrong-but-non-NULL detection | none | **highest gap — bespoke design required** |
| 3 | Golden-flow regression tests | event *counts* yes; event *content* no | partial |
| 4 | Cross-emitter conflict detection | policy conflicts only (`td_handlers_ops.py:2609`) | weak |
| 5 | Stale producer detection | **`audit_celery_zero_fire.py:1-413`** | **strong — direct reuse** |
| 6 | Impossible actor-role combos | `models_document_registry.py:724` `validate_stage_invariant()` | partial (pattern, not universal hook) |
| 7 | Retention policies | `CELERY_TASK_EVENT_RETENTION_DAYS = 30` | reused |
| 8 | JSONField query patterns | extensive queries; NO GIN indexes | partial |
| 9 | `verify_doc_claims` framework | `doc_claim_verification.py` | **strong — direct reuse** |
| 10 | Telemetry-drift dashboards | ad-hoc view components only | needs bespoke build |

**High-impact reuse opportunities:**
1. Fork `audit_celery_zero_fire.py` for "which action_class producers have zero fire in window?"
2. Use `@register_claim` framework immediately for `verify_authority_action_observed_claims` command
3. Adopt `validate_stage_invariant()` pattern on the event model for impossible-actor-combo detection

---

## 5. Recommended v0 Event Surface

### 5.1 The decision — a two-surface stream, not a synthetic single surface

**v0 emits `authority_action_observed` on two existing surfaces:**

- **Mission-scoped emissions** (MissionRunner preflight, MissionRunner step lifecycle, `employee_tool run_now`) extend `OpsRunEvent` — new `LABEL_AUTHORITY_ACTION_OBSERVED` constant + `data['authority_action_observed']` JSONField key namespace.
- **Non-mission tool-call emissions** (ToolDispatcher `execute()` outside a mission) extend `ToolCallRecord.parameters` — same `parameters['authority_action_observed']` JSONField key namespace.

Downstream consumers read the unified logical stream via a new **`authority_action_observed_stream` database view** that `UNION ALL`s the two surfaces. Producers never see the view; consumers never see the split.

**Why this replaces an earlier draft's "ambient OpsRun" idea:** synthetic runs create ambiguous grouping ("why is this tool call in yesterday's ambient run?"), poison analytics joins, and force downstream consumers to remember to filter by `domain='ambient'` (which they will forget). The two-surface + UNION-view pattern is honest about where each event actually lives while presenting a single stream to readers.

### 5.2 Rationale (why the two-surface pattern beats alternatives)

| Consideration | Two-surface + UNION view | Ambient OpsRun (rejected) | New `AuthorityActionEvent` model |
|---|---|---|---|
| **Coupling to mission context (for mission scope)** | ✅ Direct FK to `OpsRun` on the mission side | ✅ Same | ❌ Would need FK to OpsRun |
| **Precedent for mission side** | ✅ S1264 `authority_contract_observed` already emitted as `OpsRunEvent` (`_emit_authority_contract_event` at mission_runner.py:835-900) | ✅ Same | ❌ Diverges from established pattern |
| **Precedent for tool-call side** | ✅ `ToolCallRecord.parameters` is the tool-call-scoped audit surface (`models_tool_calls.py:19-217`) | ⚠️ Synthetic run wraps something that isn't a run | ❌ New model + admin + indexes |
| **Honest grouping semantics** | ✅ Each event lives where it belongs | ❌ Ambient runs group by an arbitrary calendar bucket | ✅ |
| **Anti-duplication** | ✅ Reuses two existing tables; no new model | ✅ Reuses OpsRun/Event | ❌ Violates EMPLOYEE_OS_PRIMITIVES.md §2 |
| **Consumer effort** | ⚠️ Consumers query the UNION view (one-time cost) | ✅ Single physical table | ⚠️ Parallel consumer path |
| **Filter-forgetting failure mode** | ✅ UNION view exposes only authority_action_observed rows | ❌ Consumers forget to filter `domain='ambient'` and treat ambient as mission | N/A |

### 5.3 The UNION view sketch

Concept (not a migration — this is design intent):

```sql
CREATE OR REPLACE VIEW authority_action_observed_stream AS
SELECT
  'ops_run_event' AS source_surface,
  ope.id AS source_row_id,
  ope.run_id AS mission_ops_run_id,
  ope.created_at AS emitted_at_persist,
  ope.data->'authority_action_observed' AS payload
FROM core_opsrunevent ope
WHERE ope.label = 'authority_action_observed'
UNION ALL
SELECT
  'tool_call_record' AS source_surface,
  tcr.id AS source_row_id,
  NULL AS mission_ops_run_id,
  tcr.created_at AS emitted_at_persist,
  tcr.parameters->'authority_action_observed' AS payload
FROM core_toolcallrecord tcr
WHERE tcr.parameters ? 'authority_action_observed';
```

Consumers query the view. Producers write to whichever surface fits their execution context. Neither side needs to know about the other.

### 5.4 The one operational cost

The two-surface pattern requires **schema-parallel drift detection**: every drift audit (§12) must query the UNION view, not either surface directly. This is a discipline requirement, not an architectural cost — the drift stack (§12) is written against the view.

### 5.5 Alternatives explicitly rejected

| Surface | Why rejected |
|---|---|
| **Ambient OpsRun** (single surface via synthetic run) | Synthetic run semantics poison downstream joins; consumers forget to filter `domain='ambient'`; introduces "who owns this run?" question that has no honest answer for non-mission tool calls |
| `LLMCallEvent.metadata` | LLM-scoped only; misses non-LLM actions (deliverable transitions, DirectMessage sends); coupling to LLM provider unclear |
| `CeleryTaskEvent` | No JSONField; would require full migration; tightly coupled to Celery task boundary |
| `AgentExecution.output_data` | Deprecated per Session 287 |
| New dedicated `AuthorityActionEvent` model | Violates anti-duplication (EMPLOYEE_OS_PRIMITIVES.md §2) |
| Django signal-only (no persistent event) | Loses drift-detection capability; no historical query surface |
| Emitter-side single surface (force everything into `OpsRunEvent`) | See "Ambient OpsRun" — same problem in a different wrapper |

---

## 6. Canonical Event Name

### 6.1 The recommendation

**`authority_action_observed`**

Chosen for symmetry with the existing S1264 `authority_contract_observed` event: both are *observations* (warn-mode, non-enforcing), both are authority-scoped. The distinction:

- `authority_contract_observed` — a mission's declared authority contract was inspected at preflight (S1264 baseline)
- `authority_action_observed` — a specific runtime action mapped to an authority-scoped `action_class` was observed

### 6.2 Alternatives considered

| Candidate | Reason rejected |
|---|---|
| `symbol_mapping_observed` | Emphasizes the *design mechanism*, not the *observable fact* |
| `action_class_observed` | Redundant with the field name |
| `authority_use_observed` | "Use" implies enforcement (permission granted); v0 is warn-mode only |
| `runtime_action_observed` | Too broad — not all runtime actions are authority-scoped |
| `authorized_action_observed` | Presumes enforcement outcome |

### 6.3 Naming stability commitment

The v0 event name is **frozen for the life of Option E**. Renaming after producers ship would fragment historical data. If v1 introduces enforcement (fail-open → fail-closed), a **new** event `authority_action_enforced` is emitted alongside — never renamed.

---

## 7. Minimum Viable Schema

The event lives inside `OpsRunEvent.data['authority_action_observed']`. Every field below is a key inside that nested dict, not a column on the model.

### 7.1 Required fields

| Field | Type | Nullable | Description |
|---|---|---|---|
| `schema_version` | `str` (semver) | **no** | Frozen at `"1.0.0"` for v0. Consumers must fail-open on unknown versions. |
| `emitted_at` | ISO-8601 str | **no** | Wall-clock at emission (not persistence). Kept required because it discriminates emit-vs-persist skew, but persistence timestamp on the host row is the authoritative fallback if this is missing. |
| `producer` | `str` enum | **no** | One of: `mission_runner.preflight`, `mission_runner.step`, `tool_dispatcher.execute`, `employee_tool.run_now` (v0 emitter set — extended in v1). Bug Triage step 4 is a consumer, not a producer; it does not populate this field. |
| `mapping_confidence` | `str` enum | **no** | One of: `DEFINITE`, `DECLARED`, `HEURISTIC`, `UNKNOWN`. See §11. |
| `mapping_source` | `str` enum | **no** | One of: `job_contract`, `step_declaration`, `tool_schema`, `heuristic`, `absent`. See §11.2. |

**Note on `event_id`:** an earlier draft required a client-generated UUID `event_id` for dedup. Rigby SIGN review (S1275 must-fix #2) removed it: `OpsRunEvent.id` and `ToolCallRecord.id` on the host row are sufficient identity. Async emitters that risk duplicates use the optional `idempotency_key` field in §7.3 instead.

**Note on `producer_version`:** an earlier draft required per-emit git SHA. Rigby SIGN review (must-fix #3) demoted it to optional (§7.3) because per-emit SHA bloats payload, appears identically on every event from a given deploy, and is more usefully expressed as a separate producer-heartbeat event surface (deferred to v1).

### 7.2 Semi-required fields (nullable but must be *deliberately* NULL)

| Field | Type | Nullable | Description |
|---|---|---|---|
| `action_class` | `str` | ✅ | The mapped action class (e.g., `deliverable.publish`, `content.commit`). NULL means "producer could not determine." A NULL value is **valid**; a wrong non-NULL is a bug. See §10 + §12. |
| `executor_actor` | `str` | ✅ | Runtime executor identity (agent name, step function qualname, tool handler name). Follows S1271 F11. NULL only when producer legitimately cannot determine. |
| `sponsor_actor` | `str` | ✅ | Who authorized/initiated. NULL for system-initiated actions. Follows S1271 F11. |
| `principal_user_id` | `int` (FK to `UnifiedUser`) | ✅ | End-user attribution. NULL for autonomous system actions. Follows S1271 F11. |
| `employee_handle` | `str` | ✅ | Employee OS handle if mission-scoped, else NULL. **Distinct from `executor_actor`** per S1274 Rigby must-fix #4. |

### 7.3 Optional fields (may be absent)

| Field | Type | Description |
|---|---|---|
| `idempotency_key` | `str` | Client-generated dedup key. Required ONLY for async emitters that can duplicate on retry (e.g., Celery task with retry-on-failure). Not needed for synchronous ToolDispatcher or MissionRunner emissions where host row ID is sufficient. |
| `caller_actor` | `str` | **Immediate upstream caller in a call chain, when different from sponsor.** Example: Chris → ChiefOfStaffAgent → DocumentationManager → tool → caller_actor="chief_of_staff", executor_actor="documentation_manager", sponsor_actor="chris" (top-level authorizer), principal_user_id=chris.id. See §9.4 for full semantics. Absent = no upstream caller distinct from sponsor. **This is not a 4th actor role** — the 3-role vocabulary (executor / sponsor / principal_user) is preserved; caller_actor is a runtime-graph position. |
| `producer_version` | `str` | Git SHA prefix of the emitter code. **Emitted only when non-default** (canary builds, CI runs); production emitters MAY omit. Also acceptable to omit entirely and rely on a separate producer-heartbeat event surface (deferred to v1). |
| `mission_id` | `str` (UUID) | Redundant with `OpsRunEvent.run.id` when mission-scoped; carried explicitly on tool-call-side emissions so the UNION view (§5.3) preserves mission attribution when a tool call happens inside a mission context. |
| `boundary_crossed` | `str` enum | One of: `http_to_celery`, `mission_config_to_ops_run`, `mission_to_step_fn`, `none`. Per S1271 F6. Absent = `none`. |
| `authority_key` | `str` | The `JobContract.authority` dict key the action was matched against, when confidence=DEFINITE. |
| `authority_level` | `str` | Value read from `JobContract.authority[authority_key]`. Not enforced; observation only. |
| `debug_context` | `dict` | Namespaced dict for emitter-side debugging only. Hard size cap: 128 bytes serialized. **Consumers MUST NOT parse.** Fires an invariant warning if size exceeded. Replaces the earlier draft's free-text `notes` field (removed per Rigby must-fix #3 — free text became a junk drawer). |

### 7.4 Reserved fields (defined but unused at v0)

| Field | Reserved for | v0 behavior |
|---|---|---|
| `enforcement_verdict` | v1 fail-closed events | Producers MUST NOT populate; presence is a v1 signal |
| `override_reason` | v1 exemption flow | MUST NOT populate |
| `graduation_tier` | v1 catastrophic-action guardrail | MUST NOT populate |

### 7.5 Schema versioning rule

`schema_version` bumps **major** on any of:
- Adding a new *required* field
- Removing any field
- Changing enum values in a way that invalidates existing rows
- Changing nullability of any field

**Minor** bumps for adding optional fields. **Patch** bumps for docstring/enum-comment clarifications only.

### 7.6 Payload size budget + reserved-keys policy

**Total payload size cap: 1024 bytes serialized JSON.** Larger payloads indicate producer over-population (a common drift source per S1274 §12.1). The claim-verification suite (§14) enforces this.

**Per-field caps (v0):**
- `debug_context` dict: 128 bytes serialized
- Any string field: 256 bytes
- Any array field (none at v0): reject if present

**Reserved-keys policy (per Rigby SIGN bonus must-fix 9):**

Adding a new *required* field to `data['authority_action_observed']` (or `parameters['authority_action_observed']`) requires **all** of:
1. `schema_version` major bump
2. Design doc revision (this doc)
3. Coordinated producer + consumer rollout

Adding a new *optional* field requires:
1. `schema_version` minor bump
2. Entry in §7.3 with rationale
3. Consumer default: treat missing field as legitimately absent

Removing any field or narrowing an enum → `schema_version` major bump + migration plan for stored rows.

Producers MAY NOT invent ad-hoc keys inside the payload dict. Any key not defined in §7.1, §7.3, or §7.4 fires an invariant warning at read time and is dropped from downstream projections. This prevents schema creep — one of the most common drift sources per S1274 §12.1.

### 7.7 Example payloads

**Example 7.7.1 — MissionRunner preflight, DEFINITE confidence** (on `OpsRunEvent.data['authority_action_observed']`):
```json
{
  "schema_version": "1.0.0",
  "emitted_at": "2026-07-01T14:23:11.104Z",
  "producer": "mission_runner.preflight",
  "mapping_confidence": "DEFINITE",
  "mapping_source": "job_contract",
  "action_class": "documentation.commit",
  "executor_actor": "documentation_manager",
  "sponsor_actor": null,
  "principal_user_id": 1,
  "employee_handle": "documentation_manager",
  "mission_id": "b7…",
  "authority_key": "documentation.commit",
  "authority_level": "AUTONOMOUS"
}
```

**Example 7.7.2 — ToolDispatcher inside a mission with delegation chain, DECLARED confidence** (on `OpsRunEvent.data['authority_action_observed']` because mission-scoped):
```json
{
  "schema_version": "1.0.0",
  "emitted_at": "2026-07-01T14:24:02.518Z",
  "producer": "tool_dispatcher.execute",
  "mapping_confidence": "DECLARED",
  "mapping_source": "tool_schema",
  "action_class": "deliverable.list",
  "executor_actor": "deliverable_tool",
  "caller_actor": "chief_of_staff",
  "sponsor_actor": "chris",
  "principal_user_id": 1,
  "employee_handle": null,
  "boundary_crossed": "none",
  "mission_id": "b7…"
}
```

**Example 7.7.3 — Non-mission ToolDispatcher with UNKNOWN confidence** (on `ToolCallRecord.parameters['authority_action_observed']` — no mission context):
```json
{
  "schema_version": "1.0.0",
  "emitted_at": "2026-07-01T14:25:11.001Z",
  "producer": "tool_dispatcher.execute",
  "mapping_confidence": "UNKNOWN",
  "mapping_source": "absent",
  "action_class": null,
  "executor_actor": "unknown_tool",
  "sponsor_actor": null,
  "principal_user_id": 3,
  "employee_handle": null
}
```

---

## 8. First Emitter Cohort + First Consumer

Per Rigby SIGN must-fix #5: an event system's cohort is *emitters* and *consumers*, not "producers." Blurring the two makes the payload `producer` enum incorrect and causes the wave-plan to conflate "code writes events" with "code reads events." This section separates them.

### 8.1 The four v0 emitters

Ranked by "coverage-per-emit × ease-of-instrumentation × downstream utility":

| # | Emitter | Site | Est. daily emits | Payload `producer` value | Coverage type |
|---|---|---|---|---|---|
| 1 | MissionRunner authority preflight | `mission_runner.py:835-900` | 3× per mission run | `mission_runner.preflight` | authority strings, employee identity |
| 2 | MissionRunner step lifecycle | `mission_runner.py:904-962` | 4× per step × N steps per mission | `mission_runner.step` | step executors, boundary crossings |
| 3 | ToolDispatcher `execute()` | `tool_dispatcher.py:585-720` | O(1000/day) | `tool_dispatcher.execute` | tool-scoped actions, PA-invoked |
| 4 | `employee_tool` `run_now` | `td_handlers_employee.py:212-300` | O(10/day) | `employee_tool.run_now` | HTTP→Celery boundary events |

### 8.2 The first v0 consumer

| # | Consumer | Site | Consumption pattern |
|---|---|---|---|
| C1 | Bug Triage step 4 | `bug_triage.py:396-453` | Reads events from the UNION view (§5.3); aggregates by authority string; produces a triage report |

**Bug Triage step 4 does NOT populate the payload `producer` field.** It never emits `authority_action_observed` events. If it needs to emit a *different* event type (e.g., "I detected a mislabel"), that goes on a separate event label — `authority_mapping_correction` per §12.3 — not this one.

**Why include a consumer in the v0 cohort at all?**
- **Forces the schema to be useful to a real consumer** — if C1 can't answer its questions from the v0 fields, the schema is wrong
- **Provides a natural golden-flow anchor** — see §13 GF-3
- **Surfaces wrong-non-NULL drift early** — if C1's aggregate counts diverge from ground truth (via §12.3 truthing loop), the mismatch fires

### 8.3 Why this cohort (not others)

**Explicitly excluded from v0:**

| Emitter | Why deferred |
|---|---|
| ContentDeliberationRunner | v2 content pipeline is complex; needs its own action_class declarations (out of v0 scope) |
| Deliverable transitions | Multiple emitters (PA tools, agents, admin) — hard to converge on schema in one PR |
| WebSocket message handlers | S1274 §8.8 explicit non-goal |
| Spider execution | S1274 §8.8 explicit non-goal |
| Fleet-app RPC handlers | Cross-repo boundary; out of unified-donkey-betz |
| LLM call emissions | LLMCallEvent already exists; folding authority observation adds LLM-provider coupling with no v0 payoff |
| Discord bot commands | 96 commands across 25 Cogs — coverage explosion; deferred to v1 |
| ChiefOfStaffAgent direct dispatch | Once ToolDispatcher (Emitter #3) is instrumented, CoS-dispatched tool calls are already captured — no separate emitter needed at v0 |

### 8.4 Rollout order

| Wave | Wired code | Duration | Exit criterion |
|---|---|---|---|
| A | Emitter #1 (MissionRunner preflight) | 3 days observation | ≥50 events with DEFINITE confidence + zero schema violations |
| B | Emitter #2 (MissionRunner step lifecycle) | 3 days | ≥200 events + Step.action_class declaration coverage ≥60% |
| C | Emitter #3 (ToolDispatcher) — mission side first, then non-mission (ToolCallRecord surface) | 7 days | ≥5000 events + tool-schema action_class coverage ≥70% |
| D | Emitter #4 (employee_tool run_now) | 3 days | HTTP boundary events show sponsor+principal identity |
| E | Consumer C1 (Bug Triage step 4) + UNION view (§5.3) | 7 days | consumer's report matches ground truth on golden flows |

Total minimum observation window before v1 planning: **≥14 days per S1264 prereq #2** ("clean telemetry on N≥4 employees") — Waves A+B+C+D+E cover this.

---

## 9. Actor Role Population Strategy

### 9.1 The invariant that never bends — 3 roles + 1 graph position + 1 identity marker

Per S1271 F11 and S1274 Rigby must-fix #4 + S1275 Rigby must-fix #4: the schema carries **exactly three actor *roles*** (from S1271's vocabulary — never expanded), plus **one runtime-graph position** (`caller_actor`), plus **one identity marker** (`employee_handle`). These are all separate fields, but they answer different questions:

| Field | Question it answers | Kind |
|---|---|---|
| `sponsor_actor` | "Who is the top-level authorizer at the human/system boundary?" | ROLE — top of stack |
| `executor_actor` | "Which runtime component actually executed?" | ROLE — bottom of stack |
| `principal_user_id` | "Whose artifact is this? Whose permissions apply?" | ROLE — ownership |
| `caller_actor` | "Who was the immediate upstream caller in a call chain?" | GRAPH POSITION — not a role |
| `employee_handle` | "Is this an Employee OS mission executor, and if so which one?" | IDENTITY MARKER — orthogonal to role |

**Why caller_actor is not a 4th role:** in the chain `Chris → ChiefOfStaffAgent → DocumentationManager → tool`:
- Sponsor = **Chris** (the top-level authorizer)
- Executor = **DocumentationManager** (the runtime executor)
- Principal = **chris.id** (the ownership context)
- **Caller = ChiefOfStaffAgent** — the *immediate* upstream, distinct from the top-level sponsor

Without `caller_actor`, the schema would either (a) collapse sponsor+caller into one field (losing "who authorized" vs "who invoked"), or (b) introduce a genuine 4th role and break the S1271 3-role vocabulary. The graph-position framing preserves both.

**When to populate caller_actor:** only when the immediate upstream is distinct from the sponsor. In the flat case (`Chris → tool`), sponsor = caller = "chris" — do not populate `caller_actor` redundantly. Leave it absent. Presence signals a real call chain.

**Concrete rule for `employee_handle`:** `employee_handle == executor_actor` is *permitted* (Employee OS mission executor case) but MUST be populated as two independent fields, not as a single field with two meanings. The distinction: `employee_handle` says "this executor is an Employee OS employee named X"; `executor_actor` says "the runtime execution was performed by X." A non-Employee-OS executor (e.g., a raw tool handler) leaves `employee_handle = NULL`.

### 9.2 Per-emitter × per-field population matrix

| Emitter | executor_actor | caller_actor (optional) | sponsor_actor | principal_user_id | employee_handle |
|---|---|---|---|---|---|
| MissionRunner preflight | `mission.employee.handle` | NULL | NULL (system-initiated) | payload-scoped from mission invocation context (§9.3) | `mission.employee.handle` |
| MissionRunner step start/success/error/timeout | `step.fn.__qualname__` | NULL unless step is a delegation | `mission.employee.handle` | inherited from mission context | `mission.employee.handle` |
| ToolDispatcher `execute()` | `agent_name` param (see §9.4) — the executor | populated when caller ≠ sponsor (delegation chain) | top-level authorizer resolved from caller's context | `user_id` param | NULL unless the executor is an Employee OS mission executor |
| employee_tool `run_now` | `mission.employee.handle` (post-dispatch) | NULL | HTTP requester `user.username` | HTTP requester `user_id` | `mission.employee.handle` |

### 9.3 The `OpsRun.principal_user_id` gap

Per Sub-Agent 1's inventory: `OpsRun` has `job_contract` FK but **no `user` FK**. The `principal_user_id` field is unavailable via the parent, so the event payload MUST include `principal_user_id` explicitly.

The v0 schema treats this as **the payload's responsibility**, not the model's. An earlier draft proposed adding `OpsRun.principal_user` as a nullable FK. Rejected because:

- Non-mission tool calls live on `ToolCallRecord`, not OpsRun (§5.1 two-surface pattern), so an OpsRun column doesn't help
- Migration risk on a load-bearing model
- Payload field is sufficient for v0 querying (partial GIN index in §14.4)

**v1 may promote `principal_user_id` to an OpsRun column** once mission-side query patterns stabilize.

### 9.4 The S1271 F4 ambiguity — `agent_name` as caller or executor

At `ToolDispatcher.execute()` (`tool_dispatcher.py:585-720`), the `agent_name` param is populated by the caller and its semantic (caller vs executor) depends on the call site.

**v0 rule:** `agent_name` at ToolDispatcher emission MUST be the **executor** (the actual runtime executor of the tool). The immediate caller — when distinct from sponsor — goes in `caller_actor`.

Worked example (delegation chain `Chris → ChiefOfStaffAgent → DocumentationManager (via employee mission) → deliverable_tool`):
- `executor_actor = "deliverable_tool"` — the runtime executor of this specific event
- `caller_actor = "documentation_manager"` — the immediate upstream
- `sponsor_actor = "chris"` — the top-level authorizer at the human/system boundary
- `principal_user_id = <chris.id>` — the ownership principal
- `employee_handle = null` — deliverable_tool is not an Employee OS mission executor

Worked example (flat direct-invoke `Chris → deliverable_tool`):
- `executor_actor = "deliverable_tool"`
- `caller_actor = null` — no distinct upstream; sponsor is also the caller
- `sponsor_actor = "chris"`
- `principal_user_id = <chris.id>`
- `employee_handle = null`

**Instrumentation cost:** ToolDispatcher must be modified to accept `caller_actor` at emission (v0 PR scope) — but callers that don't know it emit with `caller_actor = null` and no invariant fires.

### 9.5 Impossible-combination invariants

Per Sub-Agent 5's `validate_stage_invariant` precedent (`models_document_registry.py:724`), the event MUST enforce these invariants at emit time (fail-loud in tests; log-and-continue in production):

| # | Rule | Rationale |
|---|---|---|
| I1 | At least one of `executor_actor`, `sponsor_actor`, `principal_user_id` MUST be non-NULL | An event with no attribution is meaningless |
| I2 | If `mapping_confidence == DEFINITE`, `mapping_source` MUST be `job_contract` or `step_declaration` | DEFINITE without a structured source is a bug |
| I3 | If `mapping_source == absent`, `action_class` MUST be NULL | Can't have a mapped action_class from no source |
| I4 | If `employee_handle` is non-NULL, `producer` MUST be one of: `mission_runner.*`, `employee_tool.*` | Non-mission emitters cannot have Employee OS handles |
| I5 | If `boundary_crossed != "none"`, event MAY carry pre-boundary actor state in `debug_context` (subject to 128-byte cap in §7.6) | Preserves drop-boundary forensics per S1271 F6 |
| I6 | `caller_actor` MUST NOT equal `sponsor_actor`. If they would be equal, emit with `caller_actor = null` | Prevents redundant population and keeps caller_actor as a "distinct upstream" signal |
| I7 | Payload MUST NOT contain keys outside the sets defined in §7.1, §7.3, §7.4 | Enforces reserved-keys policy (§7.6) — prevents schema creep |

Invariants I1–I4, I6, I7 raise `AuthorityEventInvariantViolation` in tests; log a `[AUTHORITY_EVENT_INVARIANT_VIOLATED]` warning in production and persist the row anyway (fail-open to avoid dropping observations). Invariant I5 is advisory — presence of pre-boundary state is a "nice to have," not a requirement.

### 9.6 The caller-only case

If an emitter knows only the immediate caller (not the executor — rare but possible at HTTP entry points where dispatch decision is pending), it emits with `caller_actor` populated and `executor_actor = NULL`. This is a legitimate NULL. The drift dashboard (§14) tracks caller-only rate as a first-class metric — high rates indicate an instrumentation gap at that emitter.

---

## 10. `action_class` Population Strategy

### 10.1 The four confidence tiers

`mapping_confidence` takes exactly four values. Populating `action_class` at each tier follows different rules.

| Tier | When to use | `action_class` behavior | `mapping_source` |
|---|---|---|---|
| **DEFINITE** | Producer reads action_class from a structured, versioned declaration (JobContract.authority key, Step.action_class attribute). | REQUIRED — must be non-NULL | `job_contract` or `step_declaration` |
| **DECLARED** | Producer reads action_class from a structured secondary source (tool schema field). May be wrong if the schema drifts from ground truth. | REQUIRED — must be non-NULL | `tool_schema` |
| **HEURISTIC** | Producer applies a rule (regex, prefix match, hardcoded map). **Not permitted in v0.** Reserved for v1 experimentation. | must be NULL at v0 | `heuristic` |
| **UNKNOWN** | Producer has no basis to guess. | MUST be NULL | `absent` |

**v0 producers are restricted to DEFINITE, DECLARED, and UNKNOWN.** Any producer that emits HEURISTIC is a bug in v0 — the invariant checker (§9.5) will not enforce this in production (fail-open), but the claim-verification suite (§14) fires an alert if any HEURISTIC events are observed.

### 10.2 Population source per producer

| Producer | Source | Confidence tier |
|---|---|---|
| MissionRunner preflight | `JobContract.authority` dict — the *key* matched against action being observed | DEFINITE |
| MissionRunner step lifecycle | New `Step.action_class` attribute on the Step dataclass (added by Wave B rollout) | DEFINITE when declared; UNKNOWN when Step has no declaration |
| ToolDispatcher | New `tool_schema.action_class` field in `pa_tool_schemas.py` per-tool-schema entry | DECLARED (schema may drift from actual behavior) |
| employee_tool run_now | Inherits mission's action_class from JobContract | DEFINITE |
| Bug Triage step 4 (consumer) | reads action_class from events; does not emit | N/A |

### 10.3 The mission-trigger action_class problem (Sub-Agent 4)

Sub-Agent 4 identified: **it is unknown which action_class corresponds to the mission itself.** A mission executes many actions; the mission trigger is one of them (e.g., "run the daily documentation audit"). Without a mission-level declaration, MissionRunner preflight has no basis to populate `action_class` for the preflight event.

**Proposal (from Sub-Agent 4, adopted here):** Add a `mission_trigger_action_class` string field to `JobContract`. MissionRunner preflight reads this field to populate `action_class` for the preflight event.

**Naming convention (v0):**
- `mission_trigger_action_class = "documentation.audit.run"` for the Documentation Manager's audit mission
- `mission_trigger_action_class = "auditor.mission.run"` for the Platform Auditor's mission
- `mission_trigger_action_class = "chief_of_staff.mission.run"` for the Chief of Staff's mission

**Fallback rule:** If `mission_trigger_action_class` is unset on a JobContract, MissionRunner preflight emits with `action_class = NULL, mapping_confidence = UNKNOWN, mapping_source = absent`. The invariant is respected (no wrong non-NULL); the coverage gap is visible on the dashboard.

### 10.4 The step-level declaration format

Step objects (currently `Step` in `core/employees/steps.py` or equivalent) gain an optional `action_class: str | None = None` attribute. Steps declare it in the step-factory:

```python
Step(fn=documentation_manager_audit_step, action_class="documentation.audit.execute")
```

Steps that do not declare `action_class` emit with `mapping_confidence = UNKNOWN`. This is intentional — the drift dashboard's coverage metric measures declaration completeness. Chris can see which steps have not yet been annotated.

### 10.5 The tool-schema declaration format

Each entry in `pa_tool_schemas.py` gains an optional `action_class` string field:

```python
{
  "name": "deliverable_tool",
  "description": "…",
  "action_class": "deliverable.manage",
  "parameters": {…}
}
```

ToolDispatcher reads this at emission. Missing `action_class` on a tool schema → `UNKNOWN` confidence at emission.

**Design intent:** tool schema is the natural declaration site — it's where the tool is registered, versioned, and reviewed. It also enables the schema-drift detection in §12.3.

### 10.6 What NEVER populates `action_class` at v0

- LLM inference on the action being observed (reserved for v1 experimentation with sandboxed truthing)
- Regex or substring match on `agent_name`
- Historical join against past events (temporal inference)
- Cross-emitter reconciliation ("this looks like the event that Producer #1 saw 3ms ago")

These are all deferred to v1 because each is a wrong-non-NULL risk per §12.

---

## 11. `mapping_confidence` Semantics

### 11.1 The four values, in operational terms

| Value | Operational meaning | Downstream consumer treatment |
|---|---|---|
| `DEFINITE` | Emitter read from a versioned declaration in a code-controlled file (JobContract, Step). If wrong, the *declaration* is wrong — fix source, not payload. **DEFINITE indicates emitter-local certainty, not canonical truth** (per Rigby SIGN must-fix #8). | Trust for coverage counts. Do NOT treat as global ground-truth in cross-source reconciliation (§12.3). Enforcement decisions in v1 require an additional adjudication step. |
| `DECLARED` | Emitter read from a structured secondary source (tool schema field). May be wrong if the schema drifts from the tool's actual behavior. Renamed from an earlier draft's `INFERRED` per Rigby SIGN must-fix #6 — "declared" is truthful (the schema declares it), "inferred" implied a runtime inference that doesn't happen. | **Coverage dashboards only.** Never used for enforcement decisions. Never trusted for cross-source truthing. Until §12.3 sampled-truthing loop shows a producer's DECLARED correction rate is <2%, treat every DECLARED as advisory. |
| `HEURISTIC` | *Reserved.* v0 emitters do not emit this. | Ignore for coverage; count as a drift signal (any HEURISTIC in v0 is an emitter bug). |
| `UNKNOWN` | Emitter had no structured basis to populate `action_class`. This is the honest NULL. | Count as coverage gap. Never a bug — it's the expected outcome for unannotated code paths. |

**The bright line (per Rigby SIGN must-fix #6):** DECLARED is non-authoritative by construction. It exists to expand v0 coverage learning without pretending the tool schema is behavioral ground truth. A future v1 upgrade may promote a specific producer's DECLARED tier to DEFINITE-equivalent trust after sustained low correction rates — but that upgrade is per-producer, per-action_class, and requires a documented adjudication.

### 11.2 The `mapping_source` companion field

`mapping_source` is a compact provenance label for the source of the mapping. Values:

| `mapping_source` | Meaning | Compatible with `mapping_confidence` |
|---|---|---|
| `job_contract` | `JobContract.authority` dict lookup | DEFINITE only |
| `step_declaration` | `Step.action_class` attribute | DEFINITE only |
| `tool_schema` | `pa_tool_schemas.py` entry field | DECLARED only |
| `heuristic` | Producer's own rule (banned in v0) | HEURISTIC only |
| `absent` | No source available | UNKNOWN only |

Invariant I2 (§9.5) enforces the confidence↔source pairing.

### 11.3 Why not a single "confidence float 0.0–1.0"

Rejected explicitly. Reasons:

- **False precision.** A float invites downstream code to threshold on 0.7, 0.8, 0.95 — arbitrary cutoffs that hide semantic distinctions.
- **Wrong-non-NULL amplifier.** A "0.6 confidence, action_class=X" row is exactly the case §12 warns against. Discrete tiers make wrong non-NULL harder to hide.
- **Provenance loss.** A float doesn't distinguish "read from JobContract" from "regex-matched agent_name" — but the operational treatment of those two is very different.

### 11.4 Confidence downgrade at read time (v1 hook)

At v0, confidence is *emitted* by producers and *read* by consumers as-is. v1 may introduce a **downgrade layer**: if drift detection (§12) finds that a producer's DEFINITE events disagree with ground truth 10% of the time, the read layer downgrades that producer's DEFINITE → DECLARED at query time.

This is a **v1 hook only** — the v0 schema reserves the semantic space by not introducing anything that would prevent it (e.g., not caching confidence in downstream tables).

### 11.5 The "silent DEFINITE" trap

The most dangerous drift pattern per S1274 §12.1: a producer emits DEFINITE with the wrong `action_class`, and no consumer notices. Section 12 addresses this. **The confidence tier is not a get-out-of-drift-free card.** DEFINITE just says "the producer thinks it's certain" — it does not say "the mapping is correct."

---

## 12. Preventing False Confidence (Drift Detection)

**This section is a first-class deliverable, not a v0 nice-to-have.** Rigby's S1274 must-fix #3 (§12.1 of that doc) elevated it: wrong-but-non-NULL is more dangerous than NULL, so drift detection must ship with the first producer.

### 12.1 The six drift patterns to detect

| # | Pattern | Failure mode | Detection strategy | Precedent |
|---|---|---|---|---|
| D1 | High NULL rate | Emitter stops populating action_class | NULL rate per emitter per day > threshold | §12.2 |
| D2 | Wrong non-NULL (including stable wrong non-NULL) | Emitter populates plausible-but-incorrect action_class, possibly consistently over long periods | Sampled-truthing loop + cross-source disagreement (weighted, not adjudicated) + golden flows + suspect-event flagging | §12.3 (bespoke — largest gap; sampled-truthing added per Rigby SIGN must-fix #7) |
| D3 | Zero-fire emitter | Emitter stops emitting entirely | S1245 zero-fire audit pattern | §12.4 |
| D4 | Cross-emitter conflict | Two emitters emit conflicting action_class for same mission_id | Cross-emitter disagreement query (emits `suspected_mislabel`, never "wrong producer" verdict — per must-fix #8) | §12.5 |
| D5 | Impossible actor combos + payload key creep | Invariants I1–I7 (§9.5) violated | Invariant validator at emit + read | §12.6 |
| D6 | Schema drift | Tool schema or Step declaration changed without emitter update | Schema signature check (v0) + behavioral truthing (v1) | §12.7 |

### 12.2 D1 — NULL rate monitoring

**Approach:** New Celery beat task `audit_authority_action_null_rate` (daily), builds on the `check_initiative_drift.py` per-producer aggregation pattern. Outputs to a new `AuthorityEventDriftReport` row (see §14.3).

**Thresholds (v0, tunable):**
- Producer NULL rate for `action_class` > 40% on a rolling 7-day window → warning
- Producer NULL rate > 70% → alert
- **BUT:** for producers legitimately observing non-mission-scoped actions (e.g., ToolDispatcher), UNKNOWN is expected. The threshold is on **unexpected NULL** — measured by comparing to the producer's own 30-day baseline.

**Reused pattern:** `pa_acks_health.py` (`.filter(field__isnull=True)` + `.count()` pattern).

### 12.3 D2 — Wrong-but-non-NULL detection (the hardest problem)

Sub-Agent 5 found **no precedent** for cross-source truthing on the platform. This is the largest gap. Per Rigby SIGN must-fix #7 + #8, v0 addresses it with **four complementary techniques**, none of which treat any single emitter as canonical truth:

**Foundational premise (per must-fix #8):** DEFINITE indicates emitter-local certainty, not global truth. Cross-source consistency does not emit "Producer X is wrong"; it emits `suspected_mislabel` on disagreement, and any "wrong producer" verdict requires a separate adjudication step. This prevents the drift system from becoming a false-positive alert cannon when a single upstream emitter has a wrong DEFINITE.

**D2.1 — Cross-source disagreement detection (weighted, not adjudicated)**

Invariant: if two or more emitters observe the same `(mission_id, action_class_slot)` and emit different `action_class` values, this is a **suspected mislabel** — not a producer-X-is-wrong verdict.

Implementation shape (v0 scope — new beat task `audit_authority_action_consistency`):
- Query all events from the UNION view (§5.3) for a given `mission_id` in the last N hours
- Read `JobContract.authority` for that mission
- Compute per-mission agreement scores:
  - Multiple emitters agree on `action_class` → **agreement point** (confidence up)
  - Emitters disagree → emit a `suspected_mislabel` row into `AuthorityEventDriftReport` with severity=warning
  - Any `action_class` value not in the mission's `JobContract.authority` dict → **suspected mislabel** (does not mark producer as wrong; flags for adjudication)
- Never marks a specific producer as "wrong" without an adjudication step (§12.3.4)

**D2.2 — Golden-flow regression assertions**

Define **golden flows** (§13) — deterministic scenarios where the expected event sequence and action_class values are known ahead of time. Run these in CI and periodically in production. Any drift from expected → CI fail; production drift → high-severity `AuthorityEventDriftReport`. Golden flows are the only place a specific producer's specific action_class value is treated as "must equal Y" — because the ground truth for a golden flow is code-controlled and reviewed.

**D2.3 — Sampled truthing loop (per Rigby SIGN must-fix #7)**

The one technique that catches "stable, wrong, non-NULL" mappings (the smallest producer bug the rest of the stack won't catch — per Rigby's §12.3 analysis).

Weekly beat task `audit_authority_action_sampled_truthing`:
- Sample N events per emitter × confidence tier (v0: N=25) where `mapping_confidence ∈ {DEFINITE, DECLARED}`
- Manual or LLM-assisted reviewer compares each event's `action_class` vs the observed runtime behavior at the time of emission (using host row context: for `OpsRunEvent`, the parent `OpsRun` + surrounding events; for `ToolCallRecord`, the tool name + parameters + result)
- Reviewer emits a new event type `authority_mapping_correction` on the UNION view when a mismatch is found, with fields:
  - `original_event_ref`: pointer to the source row (source_surface + source_row_id)
  - `corrected_action_class`: what the reviewer believes is correct
  - `correction_reason`: freeform, capped at 256 bytes
  - `reviewer_actor`: who performed the truthing
  - `correction_confidence`: DEFINITE (code-reviewed golden flow) or DECLARED (LLM-assisted, human-approved)
- Track **`correction_rate`** per emitter × action_class as a first-class KPI
- Until an emitter × action_class's rolling-30-day correction_rate stabilizes below 2%, DECLARED tier for that pair remains non-authoritative

**v0 constraint:** the sampled-truthing loop's *mechanism* (event type, storage, KPI) ships in v0. The *review cadence* starts at weekly and may drop to monthly as correction rates stabilize. LLM-assisted review is scoped but the LLM adjudication is deferred to v1 — v0 sampled truthing is manual (Chris + Rigby collaboration).

**D2.4 — Chris-visible suspect-event flagging**

The v0 dashboard (§14) surfaces a "recent 100 events per emitter" view where Chris (or Rigby via PA tool) can flag rows as wrong-non-NULL directly. Flagged rows land in a `SuspectAuthorityEvent` table. When an emitter × action_class pair accumulates ≥3 flagged events in 7 days, an alert fires and the pair's DECLARED tier is downgraded to "quarantined" (v1 downgrade hook per §11.4).

**Explicit acknowledgment (unchanged from earlier draft, refined):** D2 remains the weakest defense at v0. The sampled-truthing loop (D2.3) mitigates the "stable wrong non-NULL" hole that Rigby SIGN must-fix #7 identified. But the loop's power is bounded by review throughput. Full behavioral truthing (comparing declared `action_class` against actual side-effect observation) is deferred to v1.

### 12.4 D3 — Zero-fire producer detection

**Direct reuse of `audit_celery_zero_fire.py`** (`core/management/commands/audit_celery_zero_fire.py:1-413`, S1245).

New management command `audit_authority_action_zero_fire`:
- Query distinct `producer` values from the UNION view (§5.3) in the last N days
- Compare against the known v0 emitter set (§8.1: the 4 emitters — `mission_runner.preflight`, `mission_runner.step`, `tool_dispatcher.execute`, `employee_tool.run_now`)
- Report emitters with zero events as candidate silent failures

**Retention constraint:** Per S1245 pattern + `CELERY_TASK_EVENT_RETENTION_DAYS`, the zero-fire lookback is bounded by the event surface's retention. Neither `OpsRunEvent` nor `ToolCallRecord` currently has documented retention (Sub-Agent 1 finding); v0 sets `AUTHORITY_ACTION_EVENT_RETENTION_DAYS = 90` matching `AUDIT_LOG_RETENTION_DAYS`, applied uniformly across both host surfaces.

**Trigger:** Beat schedule, daily at 08:00 UTC. Fires alert if any expected emitter has zero events in the trailing 3 days.

### 12.5 D4 — Cross-emitter conflict detection

**Approach:** Reuse the `td_handlers_ops.py:2603-2615` policy-conflict-report pattern (see §4.5).

New beat task `audit_authority_action_cross_emitter`:
- Group events from the UNION view (§5.3) by `mission_id` (for mission-scoped) or by `(principal_user_id, calendar_day)` for non-mission tool calls on `ToolCallRecord`
- Within each group, check that `action_class` values are compatible (either same, or both in JobContract.authority dict when a mission_id is present)
- Any incompatibility → **suspected_mislabel** row in `AuthorityEventDriftReport` (severity=warning; never marks a specific producer as wrong without adjudication per §12.3)

### 12.6 D5 — Invariant validator

The invariants I1–I7 in §9.5 are enforced at three layers:

| Layer | Behavior |
|---|---|
| Emit-time (fail-open in prod, fail-loud in tests) | Log `[AUTHORITY_EVENT_INVARIANT_VIOLATED]` + persist row (except I7 which strips unknown keys before persistence) |
| Read-time (dashboard, drift audit) | Filter out invariant-violating rows from confidence metrics; count them separately |
| CI (test suite) | Raise `AuthorityEventInvariantViolation` on any violation of I1–I4, I6, I7 |

### 12.7 D6 — Schema drift detection

The problem: tool schema author adds `action_class = "deliverable.publish"` to a tool, but the tool actually does `deliverable.list`. The producer emits DECLARED with the *declared* action_class; no consumer notices for weeks.

**Detection:** New management command `audit_authority_action_schema_drift`:
- For each tool schema entry with `action_class`, compare against the **actual tool handler behavior** using a smoke-test harness
- The smoke test runs the handler in a sandboxed context and inspects side effects (e.g., what DB rows changed, what external calls were made)
- Any mismatch → schema drift alert

**Reality check:** This is expensive and imperfect. v0 ships a **schema-signature check** only: hash the tool handler's function body + signature + declared `action_class`. Store the hash. Any change to hash without action_class update → warning. Full behavioral truthing is v1.

### 12.8 The claim-verification integration

Direct reuse of `core/services/doc_claim_verification.py` (Session 1099).

Register the following claims at v0:

```python
@register_claim(doc="authority_action_observed.v0", claim_id="producer_coverage")
def verify_producer_coverage() -> ClaimResult: ...

@register_claim(doc="authority_action_observed.v0", claim_id="invariant_violation_rate")
def verify_invariant_violation_rate() -> ClaimResult: ...

@register_claim(doc="authority_action_observed.v0", claim_id="null_action_class_rate_per_producer")
def verify_null_action_class_rate_per_producer() -> ClaimResult: ...

@register_claim(doc="authority_action_observed.v0", claim_id="schema_version_stability")
def verify_schema_version_stability() -> ClaimResult: ...

@register_claim(doc="authority_action_observed.v0", claim_id="golden_flow_pass_rate")
def verify_golden_flow_pass_rate() -> ClaimResult: ...
```

`python manage.py verify_doc_claims --doc authority_action_observed.v0 --only-drift --format json` becomes the single-command drift report.

### 12.9 The drift-detection stack summary

| Layer | Mechanism | Cadence | Precedent |
|---|---|---|---|
| Emit | Invariant validator (§9.5 — I1–I7) + reserved-keys enforcement | Every emission | `models_document_registry.py:724` |
| Persist | Payload size guard (§7.6) | Every emission | new |
| Batch — NULL rate | `audit_authority_action_null_rate` | Daily | `pa_acks_health.py` |
| Batch — zero-fire | `audit_authority_action_zero_fire` | Daily | `audit_celery_zero_fire.py` (S1245) |
| Batch — cross-emitter disagreement (weighted, not adjudicated) | `audit_authority_action_consistency` | Daily | new (bespoke — per Rigby SIGN must-fix #8) |
| Batch — cross-emitter conflict | `audit_authority_action_cross_emitter` | Daily | `td_handlers_ops.py:2603-2615` |
| **Weekly sampled truthing** | `audit_authority_action_sampled_truthing` | Weekly (v0 cadence) | new (bespoke — per Rigby SIGN must-fix #7) |
| Batch — schema drift | `audit_authority_action_schema_drift` | Weekly | new |
| Query — claim registry | `verify_doc_claims --doc authority_action_observed.v0` | On demand | `doc_claim_verification.py` (S1099) |
| CI — golden flows | pytest suite (§13) | Every PR | `test_rigby_mission_delegation.py:395-398` |
| Chris/Rigby flagging | `authority_drift_tool flag_suspect_event` (§14.5) | On demand | new |

---

## 13. Golden Flows

### 13.1 What a golden flow is

A **golden flow** is a deterministic test scenario where the expected event sequence and field values are known ahead of time. Golden flows serve two purposes:

1. **CI regression protection** — catch producer changes that break the schema before they merge
2. **Production drift anchor** — periodic executions in production compared against the CI baseline detect drift

### 13.2 The first three golden flows (v0)

Chosen for maximum information per test:

**GF-1: Documentation Manager audit run**

Trigger: `MissionRunner.run(mission=documentation_manager.audit)`

Expected event sequence (partial):
1. `producer=mission_runner.preflight`, `mapping_confidence=DEFINITE`, `action_class="documentation.audit.run"`, `employee_handle="documentation_manager"`, `executor_actor="documentation_manager"`
2. `producer=mission_runner.step`, `mapping_confidence=DEFINITE`, `action_class="documentation.audit.step.<step_name>"`, per step
3. Zero events with `mapping_confidence=HEURISTIC`
4. Zero invariant violations

Golden invariant: exactly one `producer=mission_runner.preflight` event per mission.

**GF-2: PA-invoked `deliverable_tool.list`**

Trigger: PA chat message "list my open deliverables" → `tool_dispatcher.execute("deliverable_tool", action="list")`.

Expected:
1. `producer=tool_dispatcher.execute`, `mapping_confidence=DECLARED`, `mapping_source=tool_schema`, `action_class="deliverable.list"`, `executor_actor="deliverable_tool"`, `sponsor_actor="pa"`, `principal_user_id=<chris.id>`
2. Payload ≤ 1024 bytes
3. Zero invariant violations

**GF-3: `employee_tool run_now` for Bug Triage, plus consumer read**

Trigger: HTTP POST `/api/pa/chat/` "run bug triage" → `employee_tool run_now handle=bug_triage`.

Expected emit sequence:
1. `producer=employee_tool.run_now`, `mapping_confidence=DEFINITE`, `mapping_source=job_contract`, `action_class="bug_triage.mission.run"`, `employee_handle="bug_triage"`
2. `producer=mission_runner.preflight` (immediately after HTTP→Celery boundary), `boundary_crossed=http_to_celery`
3. `producer=mission_runner.step` events (per bug triage step)
4. Cross-source disagreement check: all `mission_runner.step` action_classes are compatible with `bug_triage.job_contract.authority` (zero `suspected_mislabel` rows generated)

Expected consumer behavior (Consumer C1 = Bug Triage step 4):
5. Bug Triage step 4 reads events from the UNION view (§5.3) and produces its triage report
6. The consumer's aggregate counts (events per authority string) match the ground-truth counts injected by the golden-flow fixture
7. If the consumer's aggregate diverges from ground truth, GF-3 fails — this is the golden-flow test that catches consumer-side schema misinterpretation

### 13.3 Anti-golden flows (drift-injection tests)

CI includes **anti-golden** tests that deliberately inject drift and verify the drift-detection layer catches it. Examples:

- Producer emits `mapping_confidence=DEFINITE` with `action_class` not in `JobContract.authority` → `audit_authority_action_consistency` must flag
- Producer emits `mapping_confidence=HEURISTIC` (banned in v0) → `verify_authority_action_observed_claims` must fail
- Two producers emit conflicting `action_class` for same `mission_id` → `audit_authority_action_cross_emitter` must flag
- Producer stops emitting for 5 days → `audit_authority_action_zero_fire` must flag

### 13.4 Golden flow versioning

Golden flow expected sequences are checked into `tests/authority/golden_flows/<flow_name>.json`. Producer changes that alter the sequence require a PR that also updates the golden flow file with a clear commit note. This makes producer-behavior changes visible in code review.

### 13.5 Anti-pattern: mocked golden flows

Per S1234 D9–D15 lessons (memory: `feedback_test_real_db_for_queryset_semantics`), golden flows MUST run against a real DB and real Celery pool. Mocked `OpsRunEvent.objects.filter(...)` in golden-flow tests **is a bug** — it defeats the purpose of the test. Enforced by test-review checklist.

---

## 14. v0 Dashboard / Query API

### 14.1 What ships at v0

**Batch-mode drift audit + on-demand claim report.** No real-time streaming dashboard at v0.

| Surface | Path | Cadence | Purpose |
|---|---|---|---|
| DB view | `authority_action_observed_stream` (UNION of `OpsRunEvent` + `ToolCallRecord` rows with the label/key) | On demand | Single logical stream — the source for all drift audits and consumers |
| Beat task | `audit_authority_action_null_rate` | Daily | populate `AuthorityEventDriftReport` |
| Beat task | `audit_authority_action_zero_fire` | Daily | " |
| Beat task | `audit_authority_action_consistency` | Daily | " |
| Beat task | `audit_authority_action_cross_emitter` | Daily | " |
| Beat task | `audit_authority_action_sampled_truthing` | Weekly | " (per Rigby SIGN must-fix #7) |
| Mgmt command | `audit_authority_action_schema_drift` | Weekly | " |
| Mgmt command | `verify_doc_claims --doc authority_action_observed.v0` | On demand | claim-registry report |
| Django admin | `AuthorityEventDriftReport` ModelAdmin | On demand | Chris eyeball view |
| Django admin | `SuspectAuthorityEvent` ModelAdmin | On demand | Chris/Rigby flag wrong-non-NULL events |
| DRF endpoint (single) | `GET /api/authority/drift/latest/` | On demand | Rigby PA tool consumer |

### 14.2 What does NOT ship at v0

- Real-time WebSocket streaming of events
- React-based drift dashboard component
- Grafana / Prometheus integration
- Historical trend charts

These are deferred to v1 because they carry meaningful complexity that would delay the primary v0 goal (get events flowing, detect drift, don't break enforcement plans).

### 14.3 `AuthorityEventDriftReport` model shape (sketch)

```
AuthorityEventDriftReport
├── generated_at: datetime
├── window_start: datetime
├── window_end: datetime
├── report_type: str  # 'null_rate' | 'zero_fire' | 'consistency' | 'cross_emitter' | 'schema_drift' | 'sampled_truthing' | 'suspect_flagged'
├── data: JSONField  # structured report content
├── severity: str  # 'ok' | 'warning' | 'alert'
└── summary: str  # 1-line human-readable
```

Rows retained per `AUDIT_LOG_RETENTION_DAYS = 90`.

### 14.4 JSONField query indexes — two surfaces

Per Sub-Agent 5's finding of no GIN indexes on JSONFields platform-wide, v0 makes an explicit two-surface decision:

- **Partial GIN index on `OpsRunEvent.data`** filtered to `label='authority_action_observed'`
- **Partial GIN index on `ToolCallRecord.parameters`** filtered to rows where the payload key is present
- Migration cost is modest (event volume is tractable at v0 emitter scope)
- Enables efficient drift queries via the UNION view on `payload->>'producer'` and `payload->>'action_class'`

This is one of the few v0 decisions that adds infrastructure — justified because drift queries are the primary consumer, and the UNION view is unusable without indexes on both underlying surfaces.

### 14.5 The Rigby PA tool consumer

Add a new PA tool `authority_drift_tool` (or extend an existing ops tool) with actions:
- `latest_report` → returns latest `AuthorityEventDriftReport` per type
- `emitter_health` → returns per-emitter health (NULL rate, zero-fire status, last-emit time, correction_rate)
- `flag_suspect_event` → Chris/Rigby mark a row as wrong-non-NULL, lands in `SuspectAuthorityEvent`
- `submit_truthing_correction` → reviewer submits an `authority_mapping_correction` event per §12.3.3 sampled-truthing loop

This tool is the primary Chris-visibility surface for v0. Aligns with memory rule `feedback_chris_discoverability_visibility` (deliverables + PA-surface visibility).

### 14.6 The single quantitative KPI

**v0 primary KPI:** "Fraction of executed authority-scoped actions covered by an `authority_action_observed` event with `mapping_confidence != UNKNOWN`."

Target for v0 exit (i.e., before v1 planning starts):
- ≥60% on mission-scoped actions
- ≥30% on tool-dispatched actions
- Zero invariant-violation rate (I1–I4, I6, I7)
- Zero HEURISTIC events (emitter bug indicator)
- Cross-emitter disagreement rate <2% of DEFINITE emissions on the same `mission_id`
- Sampled-truthing correction rate <2% per DEFINITE emitter × action_class pair (per §12.3.3)
- Zero producers with sustained zero-fire status ≥3 days

If any target misses, v1 planning is deferred until the miss is understood — no clock-based forcing function.

---

## 15. Migration + Rollout Plan (Sequencing Only, No Code)

### 15.1 The five phases

| Phase | Duration | Goal | Exit criterion |
|---|---|---|---|
| P0 | 1 sprint | Schema + invariant validator + emit-time infra | `OpsRunEvent` accepts new `label`; invariants raise in tests |
| P1 | 1 sprint | Producer #1 wired (MissionRunner preflight) | ≥50 DEFINITE events; drift beat tasks running (empty reports OK) |
| P2 | 1 sprint | Producer #2 (MissionRunner step lifecycle) + Step.action_class attribute | ≥60% step-declaration coverage on ≥1 employee's steps |
| P3 | 2 sprints | Producer #3 (ToolDispatcher) + tool-schema action_class field | Tool-schema declaration coverage ≥70% on PA tools |
| P4 | 1 sprint | Producer #4 (employee_tool run_now) + Producer #5 (Bug Triage consumer) | Golden Flow GF-3 passes end-to-end |
| P5 | 2 weeks observation | Meet exit KPI (§14.6) | v1 planning approved |

Total: **~10 weeks P0→observation exit.** Longer than a single-quarter push; deliberate slow pace to catch drift patterns before they become entrenched.

### 15.2 Anti-patterns to prevent (from prior sessions)

Per memory review, these behaviors are explicit **anti-patterns** and must not appear in rollout:

- **P0.a:** Do not skip the invariant validator to accelerate P1. The validator's presence is what makes emit-time bugs visible.
- **P0.b:** Do not use MagicMock in event-emitting tests (memory `feedback_test_real_db_for_queryset_semantics`). Real DB, real Celery pool.
- **P1.a:** Producer #1 wave A is 3-day observation minimum before P2 starts, regardless of apparent stability. The 3-day window catches drift patterns that a 24-hour window misses.
- **P2.a:** Steps without `action_class` annotation emit `mapping_confidence=UNKNOWN` — do NOT retro-fit a HEURISTIC or LLM inference to boost declaration coverage.
- **P3.a:** Tool schema `action_class` values are code-reviewed on each PR — the PR-review checklist gains a new item ("did you set action_class if the tool has authority implications?").
- **P4.a:** The Bug Triage consumer (producer #5) is not "done" until it produces a drift report that Chris can act on. Consumer-side integration is where v0 usefulness is proven.

### 15.3 Rollback conditions

Rollback the whole v0 event surface if any of:
- Any producer causes measurable prod latency regression (>50ms p99 on the emitting code path)
- Invariant violation rate >5% of emissions in first week
- Chris directs rollback for any reason

Rollback shape: disable all producers via a settings flag `AUTHORITY_ACTION_OBSERVED_PRODUCERS_ENABLED = False`. The persisted event surface is preserved (no destructive rollback).

### 15.4 The v1 door

v0 explicitly does NOT commit to v1 timing. Once §14.6 KPIs are met and ≥14 days observation is clean, v1 planning starts as a **separate** research session. v1 is where:
- LLM-based action_class inference is scoped
- Enforcement (fail-closed) is designed per S1272
- Real-time dashboard is scoped
- WebSocket / Spider / Fleet producers are added
- Confidence downgrade at read-time (§11.4) is designed

---

## 16. Out of Scope for v0

Consolidated list of explicit non-goals. Cross-referenced with §2.2 and other sections.

| # | Item | Why | Where it lives |
|---|---|---|---|
| O1 | LLM-based action_class inference | Wrong-non-NULL risk unacceptable at v0 | v1 planning session |
| O2 | Real-time streaming dashboard | Complexity delays v0 exit; batch reports are sufficient | v1 |
| O3 | React frontend drift dashboard component | Same as O2 | v1 |
| O4 | Grafana / Prometheus integration | External infra; not required for drift detection at v0 volume | v1 or DevOps track |
| O5 | Enforcement (fail-closed) | Warn-mode only at v0 per S1264 precedent | S1272 authority_enforcement_design_space.md → v1 |
| O6 | Confidence downgrade at read time | Hook reserved (§11.4); implementation deferred | v1 |
| O7 | WebSocket / Spider / Fleet producers | S1274 §8.8 explicit non-goal at v0 | v1+ |
| O8 | Discord bot command producers | Coverage explosion (96 commands) | v1+ |
| O9 | Backfill of historical `OpsRunEvent` rows | Historical rows keep NULL action_class; v0 is forward-looking | never (out of scope permanently) |
| O10 | Cross-repo symbol_registry catalog | This is the Option A/B/C/D approach rejected in S1274 | never |
| O11 | Renaming the S1264 `authority_contract_observed` event | Would fragment historical data | never |
| O12 | Adding `OpsRun.principal_user` column | Migration risk on load-bearing model | v1 if ambient-run patterns require |
| O13 | Full behavioral truthing of tool schemas | v0 ships schema-signature check only (§12.7) | v1 |
| O14 | Automatic HEURISTIC-tier emission | Banned in v0 per §10.1 | v1 experimentation |
| O15 | Automatic drift-triggered producer disable | Chris-in-the-loop only at v0 | v1 |

---

## 17. Rigby SIGN Review Log (folded)

The pre-SIGN draft posed 10 open questions. Rigby returned SIGN-with-edits and 8 must-fixes (plus 1 bonus). This section preserves the audit trail: each question, Rigby's answer, and where in the doc the fold lives.

### 17.1 Q1 — Is the recommended event surface right? → **Must-fix #1 folded**

Original draft: extend `OpsRunEvent` only, with an "ambient OpsRun" for non-mission ToolDispatcher events.

**Rigby verdict:** ambient OpsRun is wrong — synthetic run semantics poison joins and consumers will forget to filter `domain='ambient'`.

**Fold:** §5 rewritten to a two-surface pattern (`OpsRunEvent` for mission scope, `ToolCallRecord.parameters` for non-mission tool calls) + unified UNION view `authority_action_observed_stream` for consumers.

### 17.2 Q2 — Is the schema too big? → **Must-fix #3 folded + partial #4 folded**

Original: 21 fields including `notes` (free text) and required `producer_version`.

**Rigby verdict:** `notes` becomes a junk drawer; `producer_version` bloats payload without proportional value.

**Fold:** §7.3 replaces `notes` with 128-byte-capped `debug_context`; `producer_version` demoted from required to optional-canary-only per §7.1 note.

### 17.3 Q3 — Wrongly required fields? → **Must-fix #2 folded**

Original: `event_id` was required.

**Rigby verdict:** host row IDs on `OpsRunEvent` / `ToolCallRecord` are sufficient identity.

**Fold:** `event_id` removed from §7.1 required list; optional `idempotency_key` added to §7.3 for async emitters that risk retry duplication.

### 17.4 Q4 — Actor roles kept separate? → **Must-fix #4 folded**

Original: 5-field split treated `delegator_actor` as a "4th role."

**Rigby verdict:** don't inflate the 3-role vocabulary. Rename `delegator_actor` → `caller_actor` and frame it as a runtime-graph position, not a new role.

**Fold:** §9.1 rewritten to define 3 roles + 1 graph position + 1 identity marker. §9.4 gives worked examples for delegation-chain and flat-invoke cases.

### 17.5 Q5 — First producer choices? → **Must-fix #5 folded**

Original: "5 v0 producers" — including Bug Triage step 4 (which is actually a consumer).

**Rigby verdict:** Bug Triage is a consumer, not a producer. Reframe as "4 emitters + 1 consumer" and remove Bug Triage from the payload `producer` enum.

**Fold:** §8 restructured with separate §8.1 (4 emitters) and §8.2 (1 consumer). Payload `producer` enum in §7.1 dropped from 5 values to 4. ChiefOfStaffAgent explicitly noted as covered-by-ToolDispatcher-instrumentation rather than needing a separate emitter.

### 17.6 Q6 — DECLARED tier too speculative? → **Must-fix #6 folded**

Original: `INFERRED` tier; schema-signature check treated as sufficient.

**Rigby verdict:** the word "INFERRED" is misleading — nothing is inferred; the tool schema *declares* the action_class. Rename + make explicitly non-authoritative.

**Fold:** `INFERRED` renamed to `DECLARED` throughout. §11.1 adds the bright line: DECLARED never used for enforcement or cross-source truthing; only for coverage until §12.3 sampled-truthing loop shows the emitter's correction rate stabilizes.

### 17.7 Q7 — Drift stack: smallest bug it cannot catch? → **Must-fix #7 folded**

Rigby verdict: the stable-wrong-non-NULL case (tool schema and emitter code agree, but the label is semantically wrong from day 1) will slip through NULL-rate, zero-fire, schema-signature, and even golden-flow checks.

**Fold:** §12.3 gains D2.3 — a new `audit_authority_action_sampled_truthing` weekly beat task that samples N=25 events per emitter × tier, reviewer emits `authority_mapping_correction` on the UNION view for mismatches, `correction_rate` becomes a first-class KPI. §14.6 KPI updated.

### 17.8 Q8 — Most dangerous data-quality failure? → **Must-fix #8 folded**

Original draft: "wrong DEFINITE from Producer #1 causes false-positive storm downstream."

**Rigby verdict:** the analysis is right about the bug being severe, but the reconciliation design that treats Producer #1 as canonical truth is what creates the storm. Fix the reconciliation semantics, not just the risk narrative.

**Fold:** §12.3 D2.1 rewritten to weighted disagreement detection (`suspected_mislabel` on divergence, never "producer X is wrong" without an adjudication step). §11.1 adds "DEFINITE indicates emitter-local certainty, not canonical truth."

### 17.9 Q9 — v0 vs v1? warn-mode-only OK? → **No must-fix; ratified**

Rigby verdict: warn-mode-only at v0 is the correct choice. The event's purpose is to create a reliable evidence substrate; enforcing before mappings are trusted violates S1272/S1274 anti-patterns. Recommendation: tie warn-mode-only to a graduation condition even if not implemented.

**Fold:** §16 O5 unchanged (warn-mode confirmed as v0-only). §15.4 v1 door language reused unchanged.

### 17.10 Q10 — Must-fix ranking + bonus → **Bonus #9 folded**

Rigby returned 8 must-fixes ranked by risk (folded in §17.1–§17.8) plus bonus #9 (bound payload + reserved-keys policy).

**Fold:** §7.6 rewritten to include per-field caps, hard total cap 1024 bytes, and reserved-keys policy: producers may not invent ad-hoc keys; unknown keys stripped at read time with invariant warning. §9.5 gains invariants I6 (`caller_actor` ≠ `sponsor_actor`) and I7 (no unknown payload keys).

### 17.11 Post-fold verdict

All 8 must-fixes + bonus 9 folded. Doc is ready for Chris review + a second Rigby pass at Chris's request. Not yet marked canonical — awaiting Chris sign-off.

---

## 18. Appendices

### 18.A — Field reference table (consolidated, post-Rigby-SIGN-fold)

Complete list of all payload keys (under `OpsRunEvent.data['authority_action_observed']` or `ToolCallRecord.parameters['authority_action_observed']`), deduplicated across sections.

| Field | Required | Type | Introduced in § | Notes |
|---|---|---|---|---|
| `schema_version` | yes | str semver | §7.1 | Frozen `"1.0.0"` for v0 |
| `emitted_at` | yes | ISO-8601 str | §7.1 | Wall-clock at emit; host row persists timestamp separately |
| `producer` | yes | enum str | §7.1 + §8.1 | **4 v0 values** — Bug Triage removed per Rigby SIGN must-fix #5 |
| `mapping_confidence` | yes | enum | §7.1 + §11 | DEFINITE/DECLARED/HEURISTIC/UNKNOWN — INFERRED renamed per Rigby SIGN must-fix #6 |
| `mapping_source` | yes | enum | §7.1 + §11.2 | job_contract/step_declaration/tool_schema/heuristic/absent |
| `action_class` | nullable | str | §7.2 + §10 | Wrong-non-NULL = highest-risk bug; sampled-truthing loop in §12.3 D2.3 |
| `executor_actor` | nullable | str | §7.2 + §9 | S1271 F11 role |
| `sponsor_actor` | nullable | str | §7.2 + §9 | S1271 F11 role — top-level authorizer |
| `principal_user_id` | nullable | int FK | §7.2 + §9.3 | S1271 F11 role — payload-scoped due to OpsRun gap |
| `employee_handle` | nullable | str | §7.2 + §9 | Identity marker; distinct from executor_actor per S1274 must-fix #4 |
| `idempotency_key` | optional | str | §7.3 | Only for async emitters that risk retry duplication; added per Rigby SIGN must-fix #2 |
| `caller_actor` | optional | str | §7.3 + §9.4 | **Graph position, not a 4th role.** Populated only when caller ≠ sponsor (S1275 must-fix #4) |
| `producer_version` | optional | str | §7.3 | Canary/CI only per Rigby SIGN must-fix #3; production emitters may omit |
| `mission_id` | optional | UUID str | §7.3 + §9.3 | Carried explicitly on `ToolCallRecord`-side emissions to preserve mission attribution across UNION view |
| `boundary_crossed` | optional | enum | §7.3 + §9.5 | Per S1271 F6 |
| `authority_key` | optional | str | §7.3 + §10.2 | JobContract.authority key when DEFINITE from job_contract |
| `authority_level` | optional | str | §7.3 | Read from JobContract; not enforced |
| `debug_context` | optional | dict (128B cap) | §7.3 + §7.6 | Replaces earlier draft's free-text `notes` per Rigby SIGN must-fix #3 |
| `enforcement_verdict` | reserved | — | §7.4 | v1 fail-closed hook |
| `override_reason` | reserved | — | §7.4 | v1 exemption hook |
| `graduation_tier` | reserved | — | §7.4 | v1 catastrophic-action hook |

Removed between draft and canonical: `event_id` (must-fix #2), `notes` (must-fix #3), `delegator_actor` (renamed to `caller_actor`, must-fix #4).

### 18.B — Emitter + consumer inventory (consolidated)

| Role | # | Component | Site | Confidence tier | Actor roles available |
|---|---|---|---|---|---|
| Emitter | 1 | MissionRunner preflight | `mission_runner.py:835-900` | DEFINITE | executor, principal, employee_handle |
| Emitter | 2 | MissionRunner step lifecycle | `mission_runner.py:904-962` | DEFINITE (when declared) / UNKNOWN | executor (step.fn.__qualname__), sponsor (inherited), employee_handle |
| Emitter | 3 | ToolDispatcher execute | `tool_dispatcher.py:585-720` | DECLARED (via tool schema) | all 3 roles + caller_actor when delegation chain applies |
| Emitter | 4 | employee_tool run_now | `td_handlers_employee.py:212-300` | DEFINITE | employee_handle, sponsor (HTTP requester), principal |
| Consumer | C1 | Bug Triage step 4 | `bug_triage.py:396-453` | N/A — reads events via UNION view | N/A |

### 18.C — Sub-agent evidence references

Full reports live in Session 1275 conversation history. Key file references cited across the design:

- **Sub-Agent 1 (audit surfaces):** `models_ops_runs.py:11-118`, `models_tool_calls.py:19-217`, `models_llm_telemetry.py:30-115`, `models_celery_telemetry.py:17-102`, `models_unified_system.py:882-980`, `models_deliverables.py:561-614`, `models_messaging.py:99-141`
- **Sub-Agent 2 (producers):** `core/employees/mission_runner.py:835-900,904-962`, `core/services/tool_dispatcher.py:585-720`, `core/services/td_handlers_employee.py:212-300`, `core/jobs/bug_triage.py:396-453`
- **Sub-Agent 3 (actor roles):** same producer sites; S1271 F4/F6/F11 cross-refs
- **Sub-Agent 4 (action_class):** `core/employees/jobs.py` (JobContract.authority dict), proposed `JobContract.mission_trigger_action_class` new field, proposed `Step.action_class` new attribute, proposed `pa_tool_schemas.py` per-tool `action_class` field
- **Sub-Agent 5 (drift detection):** `core/management/commands/audit_celery_zero_fire.py:1-413`, `core/services/doc_claim_verification.py`, `core/services/td_handlers_ops.py:2603-2615`, `core/models_document_registry.py:724,1471`, `core/settings.py:102-103,1090,1131`, `core/tasks.py:11484`

### 18.D — Cross-references to prior research

| Prior doc | What this doc inherits |
|---|---|
| S1270 `symbol_mapping_architecture.md` | Framing of the mapping problem |
| S1271 `actor_identity_attribution_architecture.md` | F4 delegator/executor, F6 drop boundaries, F11 3-role separation |
| S1272 `authority_enforcement_design_space.md` | Placement in the 15-prereq DAG |
| S1269 `governance_authority_evolution.md` | 4 governance planes; authority as 5th surface |
| S1274 `symbol_mapping_option_selection_design.md` | Option E selection; must-fixes #1 (narrow coverage), #2 (graduation guardrail is downstream), #3 (drift detection first-class), #4 (employee_handle ≠ executor_actor) |
| S1264 `authority_contract_observed` event | Warn-mode precedent, prereq #2 (14-day observation window) |
| `EMPLOYEE_OS_PRIMITIVES.md` §2 | Anti-duplication mandate (why OpsRunEvent, not new model) |
| `AUDIT_FINDINGS.md` §12 | Deferred-by-policy pattern for celery task orphans (informs zero-fire audit) |

### 18.E — Frozen decisions (do not re-derive without doc revision)

The following are locked for v0 after the Rigby SIGN fold:

- Event name: `authority_action_observed` (§6.1)
- Host surfaces: **two** — `OpsRunEvent.data['authority_action_observed']` (mission-scoped) + `ToolCallRecord.parameters['authority_action_observed']` (non-mission tool calls) unified via `authority_action_observed_stream` view (§5.1, per Rigby SIGN must-fix #1)
- Schema version: `"1.0.0"` (§7.1)
- Confidence tiers: {DEFINITE (emitter-local certainty, not global truth), DECLARED (non-authoritative, coverage-only), HEURISTIC (reserved, banned in v0), UNKNOWN} (§10.1 + §11.1 per must-fixes #6 + #8)
- Actor roles: **3 roles + 1 graph position + 1 identity marker** — executor_actor / sponsor_actor / principal_user_id / (caller_actor optional) / (employee_handle optional) (§9.1 per must-fix #4)
- First cohort: **4 emitters + 1 consumer** per §8 (per must-fix #5) — never 5 producers
- Wrong-non-NULL is the primary drift risk (§12.1); sampled-truthing loop is the v0 mitigation (§12.3 D2.3 per must-fix #7)
- Warn-mode only at v0 (§2.2 N1, §16 O5); §17.9 ratified
- Golden flow suite: GF-1, GF-2, GF-3 (§13.2)
- Payload size cap: 1024 bytes total, 128B for debug_context, 256B per string field (§7.6 per bonus must-fix #9)
- Reserved-keys policy: emitters may not add ad-hoc keys; unknown keys stripped at read time with invariant warning (§7.6 + §9.5 I7)
- Removed pre-canonical: ambient OpsRun, `event_id` required, `notes` free-text field, `INFERRED` tier name, "5 producers" framing

### 18.F — Change log

| Date | Change | Author |
|---|---|---|
| 2026-07-01 | Draft created (v0.1) | Claude Code (session 1275) |
| 2026-07-01 | Rigby SIGN-with-edits — 8 must-fixes + bonus #9 folded (v0.2) | Claude Code fold; Rigby SIGN |
| pending | Chris canonical sign-off | — |
