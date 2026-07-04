---
title: "Group 1900 — Cat A — Actor Role Propagation Design (S1901 P1)"
status: draft
session: 1901
child_slot: P1_cat_a
domain_slug: authority_enforcement
research_group: 1900
mission_type: child_audit_design
date: 2026-07-04
authority: |
  P1 child audit + design under Group 1900 Authority Enforcement Design
  Space arc. Scope inherited from Group 1900 parent scoping §5.1
  (`1900_authority_enforcement_domain_scoping.md`), which itself
  consumes S1272 §14.2 (Actor Role Propagation Design — two-layer
  Rigby SIGN clarification).

  This doc is RESEARCH + DESIGN. It defines the role schema, the
  propagation contract, and the per-boundary implementation register
  for the three-actor vocabulary from S1271 §8.5
  (executor_actor / sponsor_actor / principal_user). It is NOT a
  design decision — P2 (Cat B) is the Chris-gated multi-verdict
  design decision that consumes this contract.

  Explicit non-scope, per playbook §14.5 no-implementation rule:
  - Does NOT ship migrations, ORM changes, or MissionRunner code.
  - Does NOT re-open S1274 Option E recommendation.
  - Does NOT pick authority enforcement design option A–F (that's P2).
  - Does NOT pick precedence policy (that's P2 + P3).
  - Does NOT design cross-plane composition rules (that's P3).
  - Does NOT audit adjacent domains' internal correctness (that's P4,
    per Rigby S1900 SIGN cycle 1 Q3(b) fold: P4 is separation-
    boundary posture audit only).

  S1271 F11 never-collapse discipline is enforced throughout: the
  three roles remain three roles across every boundary, contract
  clause, and drop-boundary register row. The Layer i contract
  chooses a shape that mechanically forbids single-field "actor"
  storage per the parent §5.1 anti-scope.

  Parallel-safety with S1274 Symbol Mapping Option E (v0
  recommendation) is verified in §5.4 + §7.6 — the audit-model
  extension pattern mechanically carries all three roles orthogonal
  to the action_class column.
companion_docs:
  - docs/research/domains/authority_enforcement/1900_authority_enforcement_domain_scoping.md
  - docs/research/actor_identity_attribution_architecture.md
  - docs/research/authority_enforcement_design_space.md
  - docs/research/symbol_mapping_option_selection_design.md
  - docs/research/symbol_mapping_event_schema_design.md
  - docs/research/governance_authority_evolution.md
  - docs/research/platform_architecture_inventory.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/OPEN_ARCS.md
  - docs/EMPLOYEE_OS_PRIMITIVES.md
  - docs/topics/employee-os.md
  - docs/topics/personal-assistant.md
  - docs/topics/agent-system.md
verifier_loop: |
  Pre-Explore (playbook §14 MC-1 REQUIRED, CODIFICATION-CONFIRMED at
  S1899 close). Direct file:line reads before firing sub-agents:
  (a) `_emit_authority_contract_event` at
      `core/employees/mission_runner.py:835-900` — verified
      shape-counter pattern (F1); iterates `authority.items()` at
      line 870; emits event with `employee_handle` +
      `contract_version_tag` + `authority_level_counts`; no
      principal_user or sponsor_actor signal on event.
  (b) `_resolve_runs_as_user_id` at
      `core/employees/mission_runner.py:1585-1591` — verified
      silent-None return: `return getattr(user, "id", None) if
      user else None`; called at lines 1432 and 1500 (grep-
      confirmed).
  (c) `OpsRun` model at `core/models_ops_runs.py:11-88` — verified
      no `user` FK, no `employee_handle` field; only
      `triggered_by` mechanism choice-enum (beat/pa_tool/
      management_cmd/manual). F1 evidence.
  (d) `OpsRunEvent` model at `core/models_ops_runs.py:91-118` —
      verified no `user` FK, no actor field; `detail` JSONField is
      the only carrier.
  (e) `LLMEnforcer` fail-open at `core/llm_enforcer.py:237-238` —
      verified exact string `except Exception: pass  # Never block
      LLM calls due to budget check errors`.
  (f) `AuthorityLevel` enum at `core/employees/jobs.py:41-52` —
      verified 4 members (OBSERVE, RECOMMEND, EXECUTE,
      PROHIBITED).
  (g) `AIEmployee` frozen dataclass at
      `core/employees/jobs.py:73-92` — verified docstring self-
      declaration: "Rigby has no dedicated User row — when she
      runs autonomously ... she acts as the ``runs_as_username``
      user account (currently ``chris``)." This is the primary
      textual evidence that `runs_as_username` is a
      principal_user *selector*, not the executor_actor.
  (h) `Step` frozen dataclass at
      `core/employees/mission_runner.py:373-...` — verified
      signature `Step(name, fn, ...)`; no actor field.
  (i) `_run_step` at `core/employees/mission_runner.py:904-962` —
      verified `result = step.fn(mission)` at line 917; step.fn
      receives only `mission` (an OpsRun instance); F6c drop
      confirmed structurally.
  (j) `ToolDispatcher` AssistantProfile gate at
      `core/services/tool_dispatcher.py:685-720` — verified
      silent-skip pattern at lines 691 (`if profile:`) and 693
      (`if allowed is not None`); when profile missing or
      allowed=None, check is skipped without raise.

  Six parallel Explore sub-agents fired per playbook §13 (Models,
  Services, APIs/Tools/Tasks/Commands, Integrations, Docs, Drift).
  Post-Explore verifier fold recorded in §20.5.
---

# Session 1901 — Group 1900 P1 Cat A — Actor Role Propagation Design

> **Anchor:** Playbook §11.2 20-section child audit template TWELFTH
> consecutive application (after S1401/S1402/S1403 Revenue + S1501/S1502
> Sports + S1601 Content + S1701/S1702 Observability + S1801/S1802/
> S1803/S1804/S1805/S1806 HumanAttention). First child audit under
> Group 1900 Authority Enforcement Design Space arc.
>
> **P1 is a two-layer research + design deliverable per S1272 §14.2
> Rigby SIGN clarification:** Layer i defines the role schema and the
> propagation contract; Layer ii inventories per-boundary propagation
> for the 20 candidate boundaries from S1272 §3.1 and produces the
> drop-boundary register.
>
> **Chris D-gate at close:** ratification (not design pick — P2 is
> the enforce-mode design decision).

---

## 1. Executive Summary

**What this arc-child is.** Actor Role Propagation Design formalizes,
for the first time in the Donkey Betz codebase, the propagation
contract for the three-actor vocabulary introduced by S1271 §8.5:
`executor_actor` (the runtime entity that performed an operation),
`sponsor_actor` (the entity that authorized it), and `principal_user`
(the `UnifiedUser` under which the row is written for ownership /
row-level access). The doc closes S1272 §14.2's two-layer scope —
Layer i (schema + contract) and Layer ii (per-boundary implementation
inventory + drop-boundary register) — under playbook §11.2 20-section
child audit template.

**Biggest gaps found.** Six load-bearing gaps ranked by risk:

1. **No boundary today has explicit `sponsor_actor`.** Sponsor is
   the least-populated role — persisted only as *mechanism* enums
   (`OpsRun.triggered_by`, `ChatConversation.source`,
   `DirectMessage.sender_type`), never as a specific-identity FK.
2. **No boundary today has a documented three-role contract in
   context.** Callers pass ad-hoc `user_id`, `agent_name`,
   `employee_handle` per site with no shared schema.
3. **`OpsRun` has zero actor fields** (`core/models_ops_runs.py:11-88`
   verified) — F1 from S1271. The mission execution anchor cannot
   answer "who ran this?" without parsing `summary` JSON.
4. **Three structural drop boundaries** (F6 from S1271) persist:
   HTTP→Celery (F6a), MissionRunnerConfig→OpsRun (F6b),
   MissionRunner→Step.fn (F6c). Only F6b is mechanically closeable at
   Layer ii scope; F6a and F6c require broader Step / Celery contract
   changes deferred to P2 + post-arc T-slots.
5. **`_resolve_runs_as_user_id` silent-None** at
   `mission_runner.py:1585-1591` (verified) — resolves
   `runs_as_username` → `User.id` via `iexact` filter, returns
   `None` on miss without raising. F3 from S1271. Silent-None
   propagates into every downstream FK write.
6. **AuthorityLevel enum has 1 runtime consumer** — the shape-counter
   at `mission_runner.py:864-874` (verified). Zero code paths branch
   on a specific level value. Any P2 enforce-mode pick must build
   the level → decision binding from scratch on top of the P1
   propagation contract.

**What P1 ships.** (i) The Layer i three-role schema formalization
including canonical field name, type, nullability, and role-classification
for every persistence surface today (§4). (ii) The Layer i propagation
contract naming context-dict shape, thread-local vs. explicit-param
semantics, defaults-on-gap policy, and failure semantics (§7.2).
(iii) The Layer ii per-boundary propagation-contract table covering all
20 S1272 §3.1 boundaries with role availability + drop status per row
(§7.3). (iv) The drop-boundary register (§7.4) with three classes: F6
structural drops (unavoidable at design-doc scope), Layer-ii-closeable
drops (P2/P3 blocked), and post-arc T-slot drops (deferred by policy).
(v) Anchor-update recommendations for the xx99 canonical summary and
`PLATFORM_WHAT_IT_IS.md` glossary refinement (§7 of the xx99 doc will
consume these; P1 does not edit anchors).

**What should be researched next (§19 preview).** P2 (Cat B, S1902)
consumes this contract to pick the enforce-mode design (S1272 §14.3).
The Enforcement Binding Points map required by Rigby S1900 SIGN
cycle 1 Q4 fold sits at the intersection of P1's per-boundary
propagation contract and P2's enforcement design — every enforcement
binding point in P2 must cite the P1 role-availability row for that
boundary. P3 (Cat C, S1903) consumes the propagation contract for
cross-plane composition. P4 (Cat F, S1904) consumes it for the
separation-boundary posture audit.

**Word count:** ~420. Within playbook §11.2 §1 300–500-word bound.

---

## 2. Domain Purpose

**Layer-i domain purpose (what this doc means by "domain").** Actor
Role Propagation is the platform primitive that carries the *who
question* across every enforcement-relevant boundary. It answers, at
each point where the runtime crosses a plane / process / thread /
async boundary: "*for this operation-in-flight, which
executor_actor / sponsor_actor / principal_user triple is
currently attached?*" It is a coupling primitive: Symbol Mapping
(S1270 / S1274) provides the WHAT; Actor Role Propagation provides
the WHO; Authority (P2 output) provides the DECISION. S1271 §9.2:
enforcement requires all three; missing any one leaves the gate open.

**Q1. What problem does the domain solve?** The platform today
conflates the three roles into ambiguous CharFields and FKs
(S1271 F4 + F11). Concretely: `runs_as_username='chris'` is a
principal_user *selection mechanism*, not the executor — the executor
is `rigby` (the `AIEmployee`). Confusing the two produces
"confidently wrong audit trails" (Rigby's phrase, S1271 §11 F11).
The domain solves that by naming three primitives, one canonical
context shape, and one propagation contract shared by every
boundary.

**Q2. What is out of scope for this domain?** Per playbook §14.5
no-implementation rule + the parent §5.1 anti-scope + Rigby S1900
SIGN cycle 1 Q3(b) fold, the following are explicitly not P1's:

- **Which enforce-mode ships** — that is P2 (Cat B).
- **Precedence policy** (authority × KillSwitch × freeze × HAI) —
  P2 preliminary + P3 finalize.
- **Cross-plane composition** — P3 (Cat C).
- **Adjacent-domain internal correctness** — P4 (Cat F) covers
  interface / seam posture only.
- **Symbol Mapping option pick** — S1274 Option E v0 stands.
- **Runtime code, migrations, MissionRunner / LLMEnforcer /
  KillSwitch reads** — nothing ships this session.

---

## 3. Canonical Entry Points

**Entry-point taxonomy.** Actor Role Propagation has three canonical
entry-point families — the perimeter surfaces where role data first
enters the runtime. Every downstream boundary is a re-carrying (or
drop) of role data that entered at one of these three:

### 3.1 HTTP / WebSocket ingress (perimeter)

Where an authenticated `request.user` first enters the process:

- `core/auth_middleware.py:563-681` — HTTP request auth middleware
  (Boundary 1 in S1272 §3.1). `request.user` becomes available via
  Token / Session authentication. **principal_user** is populated
  as a strong FK; sponsor_actor implicitly maps from the source
  enum + token type; executor_actor is not yet resolved.
- `core/consumers*.py` — WebSocket consumers behind
  `AuthMiddlewareStack` (Boundary 18). Same `request.user`
  contract as HTTP, degraded to `AnonymousUser` for unauthenticated
  connections.
- `core/services/fleet_auth_drf.py:65-150` — Fleet
  `FleetSignatureAuthentication` (Boundary 19). HMAC-verified
  service identity. **executor_actor** and **sponsor_actor** are
  both the fleet `app_slug`. principal_user may be `None` (no
  human user FK) or a fleet-owned account.

### 3.2 Autonomous / beat-fired ingress (server-side)

Where an operation starts without an inbound HTTP `request.user`:

- `core/celery.py` — beat schedule dispatches PeriodicTasks. No
  `request.user`. `OpsRun.triggered_by='beat'` is the *mechanism*
  sponsor; the human who scheduled the PeriodicTask is not
  attributable.
- `core/employees/mission_runner.py` — `MissionRunner.__init__`
  (Boundary 4). `MissionRunnerConfig.employee_handle` is
  **executor_actor** (strong, frozen registry per
  `core/employees/jobs.py:73-92`). `MissionRunnerConfig.runs_as_username`
  is **principal_user selector** (string, unverified per S1271 F3).
  sponsor_actor is `system` (beat) or `manual` (management command)
  or `pa_tool` — attributed via `triggered_by`, not to a specific
  entity.
- `core/tasks*.py` — `@shared_task` entries (Boundary 9). No
  `request.user` at process boundary; task args become the
  authoritative context.

### 3.3 Delegated dispatch (in-process)

Where an operation re-enters the runtime under a different actor
context via delegation:

- `core/services/tool_dispatcher.py:685-720` — `ToolDispatcher.execute()`
  (Boundary 2). Receives `user_id` param + `agent_name` param; the
  `AssistantProfile` gate at 685-720 reads `user_id → profile.role`
  as **principal_user**. `agent_name` is **executor_actor** (weak
  CharField per S1271 F4). sponsor_actor implicit.
- `core/services/unified_pa_entrypoint.py` — PA agentic loop.
  `ChatConversation.user` FK is **principal_user**;
  `ChatConversation.source` enum is **sponsor_actor kind** (weak
  enum, not specific identity).
- `core/agent_router.py` — `AgentRouter.route()` (Boundary 15).
  Receives user context via constructor; agent selection produces
  **executor_actor** = resolved AGENT_MAP key.

**Entry-point inventory shape.** Three families × 3 roles × drop
status = the shape of §7.3's per-boundary propagation contract.
S1272 §3.1's 20-boundary table is the canonical enumeration; §7.3
below extends it with a role-availability column and a drop-status
column.

---

## 4. Major Models

**Layer i deliverable — three-role schema formalization.** Every
persistence surface today that carries an actor role is inventoried
below with its role-classification. This table is the doc's answer
to "what does executor_actor / sponsor_actor / principal_user mean
across boundary transitions?" for every existing storage site.
S1271 §8.5's role-to-field mapping table is the source; verified
below by Agent 1 + parent-verifier reads.

### 4.1 Model × Role × Field × Classification × Nullability

| Model | Field | Role | Type strength | Nullable | file:line |
|---|---|---|---|---|---|
| `AIEmployee` | `handle` | **executor_actor** | Strong (frozen dataclass) | No | `core/employees/jobs.py:87` |
| `AIEmployee` | `runs_as_username` | **principal_user selector** (NOT executor per F11) | Weak (string, unverified) | No | `core/employees/jobs.py:89` |
| `Agent` | `name` | **executor_actor** | Strong (canonical via AGENT_MAP post-S1263) | No | `core/models_unified_system.py` (Agent row) |
| `AgentExecution` | `user` | **principal_user** | Strong FK | **Yes** (Session 642) | `core/models_unified_system.py:894` |
| `AgentExecution` | `owner_agent` | **executor_actor (ambiguous per F4)** | Weak CharField(100) | Yes | `core/models_unified_system.py:924-927` |
| `Deliverable` | `user` | **principal_user** | Strong FK | **Yes** | `core/models_deliverables.py:227-232` |
| `Deliverable` | `agent_name` | **executor_actor (ambiguous per F4)** | Weak CharField(100) | No | `core/models_deliverables.py:218-222` |
| `OpsRun` | `triggered_by` | **sponsor_actor kind** (mechanism, not entity) | Weak enum (4 values) | No | `core/models_ops_runs.py:49` |
| `OpsRun` | *(no user field)* | **F1 — missing** | — | — | `core/models_ops_runs.py:11-88` (verified) |
| `OpsRunEvent` | *(no user field)* | **F6c-implicit — missing** | — | — | `core/models_ops_runs.py:91-118` (verified) |
| `ToolCallRecord` | `agent_name` | **executor_actor (ambiguous)** | Weak CharField(255) | No | `core/models_tool_calls.py:57-60` |
| `DirectMessage` | `sender` | **principal_user** or `None` | FK (SET_NULL) | **Yes** | `core/models_messaging.py:108-114` |
| `DirectMessage` | `sender_type` | **executor_actor kind** (user/rigby/system) | Weak choice enum | No | `core/models_messaging.py:124-128` |
| `ChatConversation` | `user` | **principal_user** | Strong FK | Yes | `core/models/conversations/models.py:69-75` |
| `ChatConversation` | `source` | **sponsor_actor kind** (web/mobile/discord/api/claude-code/pa) | Weak choice enum | No | `core/models/conversations/models.py:89-95` |
| `LLMCallEvent` | `agent_name` | **executor_actor (ambiguous)** | Weak CharField(120) | Yes (blank=True) | `core/models_llm_telemetry.py:62-65` |
| `CeleryTaskEvent` | `agent_name` | **executor_actor (unreliable)** | Weak CharField(255) | Yes (blank=True) | `core/models_celery_telemetry.py:41-47` |
| `AssistantProfile` | `user` | **principal_user** | Strong OneToOne | No | `core/models_assistant_profile.py:93-97` |
| `FleetServiceIdentity` | `app_slug` | **executor_actor** + often **sponsor_actor** | Strong (HMAC-verified) | No | `core/models/fleet.py:83-87` |
| `AgentControlEntry` | `blocked_by` | **sponsor_actor kind** (weak) | Weak CharField(100) | Yes | `core/models_unified_system.py:69-72` |

### 4.2 Multi-role tables — consistency-contract UNKNOWN

Six models carry more than one role today, but no persistence-level
contract enforces cross-role consistency (S1271 F11's structural
warning):

- `AgentExecution` — `user` (principal) + `owner_agent` (executor,
  ambiguous). No FK constraint that `owner_agent` maps to an
  Agent row.
- `Deliverable` — `user` (principal) + `agent_name` (executor,
  ambiguous). No FK constraint.
- `ToolCallRecord` — `execution_id` links to AgentExecution (which
  carries user); `agent_name` is executor. Two-hop chain.
- `LLMCallEvent` — same shape as ToolCallRecord.
- `ChatConversation` — `user` (principal) + `source` (sponsor kind,
  enum). Enum is legitimate per §8.5 sponsor_actor semantics;
  compatibility check passes.
- `DirectMessage` — `sender` (principal or None) + `sender_type`
  (executor kind, enum). Same shape as ChatConversation. When
  `sender is None` and `sender_type='system'`, no specific
  executor identity is recoverable.

### 4.3 Silent-nullable roll-up

FK / CharField nullability that would silently drop a role at
persistence time (verified from Agent 1 report + spot-check reads):

- `AgentExecution.user` (null=True) — allowing Celery task contexts
  to write without principal_user (Session 642).
- `Deliverable.user` (null=True) — allowing system-authored
  artifacts.
- `DirectMessage.sender` (SET_NULL) — falls back to `sender_type`
  enum on null.
- `ChatConversation.user` (null=True) — for unlinked Discord
  users (Session 455).
- `LLMCallEvent.agent_name` (blank=True, default='') — empty string
  overloaded as "non-agent task" (undocumented).
- `CeleryTaskEvent.agent_name` (blank=True, default='') — Session
  1169 extraction; still ambiguous.
- `AgentControlEntry.blocked_by` (blank=True, default='').

Every one is a candidate silent-None drop point per
`feedback_factory_silent_none_footgun.md` — Layer ii §7.4
drop-boundary register enumerates the writers that trigger each.

### 4.4 What P1 does NOT persist

P1 introduces zero new columns, zero new tables, zero migrations.
The Layer i schema is a *contract shape* documented in this doc;
Layer ii carries the contract through the boundaries but persists
the roles only where already-nullable-tolerant surfaces exist (see
§7.6 Option E audit-model extension compatibility). Any new
column addition is P2 (Enforcement Binding Points map required
artifact per Rigby S1900 SIGN cycle 1 Q4 fold) or later.

---

## 5. Major Services

The five service surfaces where actor roles flow, are dropped, or are
observed today. Each row cites the file:line, the role status at
entry, and the drop or transformation.

### 5.1 `MissionRunner` (`core/employees/mission_runner.py`)

**Entry:** `MissionRunner.__init__` accepts `MissionRunnerConfig`.
Config carries `employee_handle` (executor, strong, frozen) and
`runs_as_username` (principal selector, weak).

**Preflight — `_emit_authority_contract_event` at 835-900**
(verified):

- Line 850: shape-validates `contract.authority` is a dict; raises
  `_AuthorityContractMalformedError` on malformed (Rigby S1264 SIGN
  edit #5).
- Line 870-874: iterates `authority.items()`, counts by level
  value — F1 shape-counter, no decision.
- Line 880-900: emits `authority_contract_observed` event with
  `employee_handle` (executor) + `contract_version_tag` +
  `level_counts`. **sponsor_actor absent from event**;
  **principal_user absent from event.**

**Step boundary — `_run_step` at 904-962** (verified):

- Line 917: `result = step.fn(mission)` — step.fn signature receives
  ONLY `mission` (an OpsRun instance). No actor kwarg. **F6c
  structural drop confirmed.**
- Step + StepResult are frozen dataclasses (mission_runner.py:357,
  373) — no actor field, no way to thread role signals through
  the type today.

**Principal resolution — `_resolve_runs_as_user_id` at 1585-1591**
(verified):

- Called at lines 1432 + 1500 (verdict + escalation contexts).
- Line 1591: `return getattr(user, "id", None) if user else None`
  — silent-None on miss. F3 from S1271. This is a
  `feedback_factory_silent_none_footgun.md` application: every
  downstream FK assignment receives None without alert.

**Role status through MissionRunner:** executor_actor strong
(frozen); principal_user weak (string→FK with silent-None);
sponsor_actor absent (only mechanism via `OpsRun.triggered_by`).

### 5.2 `ToolDispatcher` (`core/services/tool_dispatcher.py`)

**Entry — `execute()` at 685-720** (verified):

- Line 687: `if user_id:` — gate active only when principal is set.
- Line 690: `AssistantProfile.objects.filter(user_id=user_id).first()`
  — silent-None if profile missing.
- Line 691: `if profile:` — silent-skip when profile missing.
- Line 693: `if allowed is not None and tool_name not in allowed:`
  — silent-skip when `get_allowed_tools()` returns None. Only the
  positive path raises `TOOL_PERMISSION_DENIED`.

**Role status through ToolDispatcher:** principal_user strong (FK
chain); executor_actor weak (agent_name string, ambiguous per F4);
sponsor_actor implicit only (inferred from source enum higher up).

**Fail-open behavior at 721-722:**

```
except Exception as e:
    logger.debug(f"[{trace_id}] AssistantProfile check skipped: {e}")
```

Any exception in the profile lookup silently skips the check. This is
the design precedent Layer i must decide whether to replicate for
gap defaults (§7.2 defaults-on-gap).

### 5.3 `LLMEnforcer` (`core/llm_enforcer.py`)

**Entry:** `check_budget(agent_name, task_type)` at 200-262
(verified).

**Fail-open at 237-238** (verbatim verified):

```
except Exception:
    pass  # Never block LLM calls due to budget check errors
```

**Role status through LLMEnforcer:** executor_actor weak
(agent_name); action signal weak (task_type enum, not action_class);
sponsor + principal absent. LLMEnforcer is the closest existing
INLINE authority-gate analog per S1272 §3 Row 14; its fail-open
default is a design precedent for Layer i defaults-on-gap.

### 5.4 `AgentRouter` (`core/agent_router.py`)

**Entry:** `AgentRouter(user=request.user)` constructor + `route()`.

**Role status through AgentRouter:** principal_user strong (from
request.user); executor_actor strong once AGENT_MAP resolves (agent
name is a canonical registry key post-S1263); sponsor_actor absent
in method signature.

**Non-PA dispatch surface (per `feedback_router_heartbeat_not_dead.md`):**
`_router_heartbeat_loop` is live for beat-fired agent dispatch — the
same role-availability shape as PA dispatch but with sponsor_actor
implicit as beat mechanism.

### 5.5 `EventBus` (`core/services/event_bus.py:137-189`)

**Entry:** `publish(stream, event_type, data, source='system',
correlation_id=None)`.

**Role status:** `source` is an arbitrary caller-controlled string
(defaults to `'system'`) — weak, effectively "any-caller-can-claim".
`data` is caller-provided dict; no schema. Roles reach subscribers
only if the publisher put them in `data`; no canonical carrier.

### 5.6 Parallel-safety with S1274 Option E

S1274 §8.4 (`docs/research/symbol_mapping_option_selection_design.md:824-833`)
declares Option E is **the only mapping option that mechanically
carries all 3 roles end-to-end IF audit models extended** with
executor / sponsor / principal columns. S1274 §8.2 identifies
the extension shape: 5 audit models (`ToolCallRecord`, `OpsRunEvent`,
`LLMCallEvent`, `CeleryTaskEvent`, `AgentExecution`) receive
`action_class` + 3 role columns (or JSONField-key extensions).

Layer i is verified parallel-safe with Option E: the propagation
contract mechanically supports orthogonal expansion into audit-row
role columns without any dependency on which Symbol Mapping option
is ultimately chosen. Layer ii inventories which of the 5 audit
models currently have which columns, so P2 can compute the delta
without re-deriving the shape.

---

## 6. Major APIs and Interfaces

Actor-role signal availability at the external-facing surface. Each
row is one of the 20 boundaries from S1272 §3.1 that is externally
callable (HTTP, WebSocket, tool, task, command, spider). §7.3 is the
full 20-row register including internal-only boundaries.

### 6.1 External-facing surface × role-availability

| Surface | Boundary # | file:line | executor available? | sponsor available? | principal available? |
|---|---|---|---|---|---|
| HTTP request auth | 1 | `core/auth_middleware.py:563-681` | N (agent name unresolved) | Implicit (source+token type) | Y — `request.user` FK |
| ToolDispatcher entry | 2 | `core/services/tool_dispatcher.py:685-720` | Weak (agent_name string) | Implicit | Y — `user_id` → profile FK |
| PA tool handler body | 3 | `td_handlers_*.py` | Weak (agent_name) | Implicit | Weak (context dict) |
| Fleet HTTP ingress | 19 | `core/services/fleet_auth_drf.py:65-150` | Y — `app_slug` (HMAC) | Y — `app_slug` (HMAC) | Nullable (fleet-owned) |
| WebSocket consumer | 18 | `core/consumers*.py` | N | Implicit | Y — via `AuthMiddlewareStack` when authenticated; `AnonymousUser` otherwise |
| Discord command | (out-of-table*) | `core/services/discord_bot.py` | N | Implicit (Discord ID → linked User via `_get_linked_user()`) | Optional — nullable via linkage |
| Celery task ingress | 9 | `core/tasks*.py` | N (unless kwargs carry it) | Implicit (task queue + triggered_by) | N (unless kwargs carry it — F6a drop) |
| Beat schedule | 8 subset | `core/celery.py` | N | Mechanism = "beat" | N |
| Management command | (out-of-table*) | `core/management/commands/*.py` | N (unless embedded) | Implicit "operator" | Optional (may hardcode `chris`) |
| Spider run | 20 | `core/tasks_spiders.py:381-398` | Weak — `spider_name` | Weak — `run_kind` | N — `system` |

*"out-of-table" = not in S1272 §3.1's 20-row inventory but adjacent
surfaces relevant to Layer ii.

### 6.2 Common failure modes across surfaces

- **Discord command → PA/tool dispatch (`_get_linked_user()`
  fallback):** returns Django User IF Discord ID linked; else
  `None`. Discord-user-only paths have principal_user=None with
  sponsor_actor kind implicit in `ChatConversation.source='discord'`.
- **Management command dispatch:** relies on implicit "staff/admin"
  operator context inherited from `call_command()` caller. Per
  `feedback_procfile_makefile_queue_parity.md` and adjacent memory
  rules, no management command explicitly stamps an actor field.
  Layer ii §7.4 flags this as a documented structural drop.
- **Spider run boundary:** `spider_name` is strong (registry
  lookup) but user attribution is `system` (no attribution). Layer
  ii §7.4 flags this as a documented structural drop.

---

## 7. Runtime Flows — LAYER i + LAYER ii

**This is the load-bearing section for both P1 layers.** §7.2 is
Layer i (schema + contract). §7.3 + §7.4 are Layer ii (per-boundary
implementation register + drop-boundary register). §7.5 is the
end-to-end delegation trace. §7.6 is the Option E parallel-safety
verification.

### 7.1 The role vocabulary (inherited from S1271 §8.5)

**Canonical definitions** (verbatim from
`docs/research/actor_identity_attribution_architecture.md:1327-1358`):

1. **`executor_actor`** — the runtime entity that performed the
   operation. Examples: an `AIEmployee` handle (`"rigby"`), a fleet
   service (`app_slug='contract-concierge'`), an AGENT_MAP agent
   (`"CodeGeneratorAgent"`), a Celery worker (`system`).
2. **`sponsor_actor`** — the entity that authorized or requested the
   action. Examples: a `UnifiedUser` (`chris`), a beat schedule
   (`system` sponsor), a CLI operator, an autonomous engineer
   (`claude-code`).
3. **`principal_user`** — the `UnifiedUser` under which the row is
   written for ownership / permission / row-level access purposes.
   Examples: `User(username='chris')` for `Deliverable.user`,
   `User(username='chris')` for `AgentExecution.user`.

**F11 never-collapse discipline (inherited from
`actor_identity_attribution_architecture.md:1707-1733`).** Treating
any single field as "the actor" without declaring which of the
three roles it represents produces "confidently wrong audit trails."
`runs_as_username='chris'` is a **principal_user selection
mechanism**, not the executor. The executor is `rigby`; the principal
is `chris`. Adding a "user" field to `OpsRun` without declaring which
role it represents would codify the conflation as schema — Layer i
mechanically forbids this. Any schema addition per §7.6 or downstream
of P2 MUST introduce all three role columns simultaneously (or an
Option-E-compatible JSONField key extension carrying all three) so
the never-collapse discipline is enforced at the persistence layer.

### 7.2 LAYER i — the propagation contract

**Contract scope.** The propagation contract answers four questions
from S1272 §14.2:

- (a) Context dict shape: which keys carry which roles.
- (b) Thread-local vs. explicit-param semantics.
- (c) Defaults on gap: when a role is unknown at a boundary.
- (d) Failure semantics: drop / raise / default when the role
  cannot be resolved.

**Design principles feeding the contract.**

- **Never collapse (S1271 F11).** All three role slots exist in the
  contract even when a role is `None`. A caller may not pack two
  roles into one field.
- **Explicit-param precedence over thread-local.** Explicit
  parameters are auditable; thread-local propagation is fragile in
  async / Celery / signal contexts (S1271 Q5b). The contract
  defaults to explicit-param carriers and allows thread-local
  only in tightly-scoped `contextvars`-based helpers (S1199 tool
  context precedent).
- **Fail-loud on structural violation; fail-open on
  boundary-legitimate gap.** A caller that passes an
  `executor_actor` of the wrong shape (e.g., a `User` object where
  an employee handle string is expected) raises (never-collapse
  enforcement). A boundary where a role is genuinely unavailable
  (e.g., anonymous WebSocket, unlinked Discord) records `None`
  with an explicit sentinel event; no exception.
- **Silent-None is a footgun** (`feedback_factory_silent_none_footgun.md`).
  A role that resolves to `None` because the *lookup failed* (e.g.,
  `_resolve_runs_as_user_id` returning None on a missing User row)
  is distinct from a role that is *genuinely absent at the boundary*
  (e.g., beat-fired task with no human sponsor). Contract must
  distinguish these two cases in the failure-semantics register.

#### 7.2.1 Context dict shape

The canonical propagation carrier is a top-level dict with three
required keys and one optional metadata key. Whether persisted
(Option E audit-model extension) or in-memory (context dict), the
shape is the same:

```python
{
    "executor_actor": <executor_value>,   # required key; value may be None
    "sponsor_actor":  <sponsor_value>,    # required key; value may be None
    "principal_user": <principal_value>,  # required key; value may be None
    "actor_meta": {                       # optional; carries provenance
        "resolved_at":     "<iso timestamp>",
        "resolved_at_site": "<file:line>",
        "gap_reasons":     [<reason strings>],
    },
}
```

**Field value shapes:**

- `executor_actor`: **string** (`AIEmployee.handle`, `Agent.name`,
  `FleetServiceIdentity.app_slug`, or the literal `"system"` for
  no-attribution executor). Canonical registries are the only
  producers.
- `sponsor_actor`: **string** (`UnifiedUser.username`, an
  `AIEmployee.handle` if delegated, an operator label, or the
  literal `"system"` for beat/mechanism). May be `None` when a
  sponsor cannot be attributed at the boundary and no reasonable
  default exists (e.g., beat with runs_as_username unresolvable).
- `principal_user`: **integer** (`UnifiedUser.id`) OR **string**
  (`UnifiedUser.username`) OR `None`. The Layer i preference is
  the integer FK — that is the shape used by `AgentExecution.user`
  and `Deliverable.user`. String username is permitted as a
  transitional carrier for surfaces (e.g., MissionRunnerConfig)
  that store the selector before resolution.
- `actor_meta` (optional): carrier for provenance and
  gap-reason strings. Consumed by observability + retro-audit
  surfaces (Boundary 17). Layer ii writes it opportunistically.

**Layer i does NOT prescribe which persistence type each surface
uses.** That is Option E audit-model extension shape (P2 delta from
§7.6). Layer i requires only the shape at the *in-flight* boundary
crossing.

**F11 mechanical prohibition (Rigby S1901 SIGN cycle 1 Q1 fold).**
No single `actor` key or column is permitted as a fallback carrier
at any boundary or in any persistence surface. Callers MUST use the
three-key shape even when two of the three values are identical
(e.g., Fleet ingress where sponsor and executor are both the
`app_slug`) or when all three are `None`. Any producer that would
convert three-role context into a single `actor` string field is a
never-collapse violation and MUST raise (§7.2.4 STRUCTURAL-DROP
does NOT allow this as a defensible drop mode).

#### 7.2.2 Thread-local vs. explicit-param semantics

**Default: explicit param.** Every boundary that receives an
in-flight operation MUST accept the three-role context as an
explicit parameter — either as a dict (§7.2.1 shape) or as three
named parameters. The dict form is preferred for surfaces that
already accept a `context` dict (e.g., `execute_agent_task.apply_async`
kwargs); the three-named-parameter form is preferred for surfaces
with structured type signatures (e.g., `MissionRunnerConfig`).

**Thread-local permitted for tightly-scoped adjunct.** Where an
in-process helper needs role read access without threading it through
every intermediate call — e.g., an ORM signal handler that must
attribute a `post_save` write to the caller — the contract permits
a `contextvars.ContextVar[ActorContext]` variable set inside a
scoped context manager. This mirrors the S1199 `tool_context_scope`
precedent (`core/services/tool_context.py:24`). Thread-local carriers
MUST:

- Be `contextvars`-backed (async-safe); NOT `threading.local`.
- Be set inside an explicit context manager, never module-global.
- Be documented as read-optional (fall back to the explicit-param
  context when absent).
- Be scoped to a single request / task / mission — cross-context
  bleed is a bug.

**Not permitted:** Cross-Celery-boundary thread-local. Celery
workers run in a separate process; role signals must cross via
`apply_async(kwargs={...})` explicit-param carrier. `contextvars`
does not survive `.apply_async()` (verified by codebase absence
per Agent 2 §Q7 grep — zero contextvars carry actor roles today).

#### 7.2.3 Defaults on gap

When a role is unknown at a boundary, the contract has three
default classes:

- **DEFAULT-NONE** — the role is genuinely unavailable and no
  reasonable default exists. Boundaries: anonymous WebSocket,
  unlinked Discord command, EventBus subscriber (unless publisher
  filled in), pre-authentication HTTP paths. Record the field as
  `None` and stamp `actor_meta.gap_reasons` with a reason string.
- **DEFAULT-INHERIT** — the role is unavailable at THIS boundary
  but was populated at an upstream boundary. Boundaries: Celery
  task body inheriting from HTTP-sourced dispatch, MissionRunner
  step body inheriting from MissionRunnerConfig, PA tool handler
  inheriting from ToolDispatcher entry. Layer ii wires the
  inheritance explicitly (no thread-local guess).
- **DEFAULT-CANONICAL** — the role is unavailable but a canonical
  default is defined by policy. Boundaries: beat-fired tasks
  (sponsor = `"system"`), management commands run without operator
  context (sponsor = `"operator"`), MissionRunner postflight
  (executor = `config.employee_handle`).

Layer ii §7.4 assigns one of these three defaults to every gap
per boundary. Boundaries where none of the three fit are
STRUCTURAL DROPS (see §7.4 F6 register).

#### 7.2.4 Failure semantics

Two failure modes:

- **STRUCTURAL-DROP** — the boundary structurally cannot carry the
  role today. F6a/F6b/F6c from S1271 are the three canonical
  examples. Contract records the drop in the drop-boundary
  register (§7.4) with a rationale + P2/P3 remediation reference
  and does NOT raise. Silent, but audited.
- **RESOLUTION-FAILURE** — a lookup or resolution *attempt*
  failed (e.g., `_resolve_runs_as_user_id` on a missing User
  row). This is F3-class silent-None today. Contract requires:
  (a) Log at ERROR level with the greppable prefix `[ACTOR_ROLE_
  RESOLVE_MISS]` + `role=principal_user` + `site=<file:line>` +
  `key=<runs_as_username>`. (b) Record `actor_meta.gap_reasons +=
  ["resolve_miss:<role>:<key>"]`. (c) Do NOT raise (preserves
  fail-open discipline where boundary is authority-adjacent, not
  authority itself). Downstream observability picks up on the
  greppable prefix.

**No silent-None.** The contract mechanically distinguishes
STRUCTURAL-DROP (documented, expected) from RESOLUTION-FAILURE
(logged, tracked). Both may record `None` but only the latter
counts as an observability signal. `feedback_factory_silent_none_footgun.md`
is enforced at the contract boundary.

### 7.3 LAYER ii — per-boundary propagation-contract table

This is the propagation contract applied to every one of S1272 §3.1's
20 boundaries. Columns: boundary #, canonical entry file:line,
executor availability at entry, sponsor availability at entry,
principal availability at entry, contract default class (§7.2.3),
Layer-i-scope closeable (`Y` = design-doc-scope closes; `N` = P2/P3
work required).

| # | Boundary | file:line | executor | sponsor | principal | Default class | Layer-ii closeable? |
|---|---|---|---|---|---|---|---|
| 1 | HTTP auth middleware | `core/auth_middleware.py:563-681` | N — resolved downstream | INHERIT-source | Y — `request.user` FK | DEFAULT-NONE for anon, DEFAULT-INHERIT elsewhere | Y (contract spec only) |
| 2 | ToolDispatcher.execute | `core/services/tool_dispatcher.py:685-720` | Weak — `agent_name` string | INHERIT | Y — `user_id` → profile FK | DEFAULT-INHERIT | Y (contract spec + AssistantProfile fail-open replacement) |
| 3 | PA tool handler body | `td_handlers_*.py` | INHERIT | INHERIT | INHERIT (context dict) | DEFAULT-INHERIT | Y (context dict passthrough) |
| 4 | MissionRunner.run entry | `mission_runner.py` (constructor) | Y — `employee_handle` | DEFAULT-CANONICAL (`triggered_by`) | Weak — `runs_as_username` string | DEFAULT-CANONICAL for sponsor; DEFAULT-INHERIT for principal | Y (config passthrough) |
| 5 | MissionRunner preflight (warn-mode) | `mission_runner.py:835-900` | Y — `employee_handle` | N — event emits no sponsor | N — event emits no principal | DEFAULT-INHERIT (from config) | Y (event schema extension) |
| 6 | Before each Step.fn | `mission_runner.py:904-917` | INHERIT (from config) | INHERIT | INHERIT | DEFAULT-INHERIT | **N — F6c STRUCTURAL DROP** (Step signature change is Layer ii closeable only via Step contract change, deferred to P2/post-arc) |
| 7 | Inside Step.fn body (closure) | Per-job step function | INHERIT (via closure) | INHERIT | INHERIT | DEFAULT-INHERIT | N — closure opaque to runner; STRUCTURAL DROP |
| 8 | Celery `.apply_async` / `.delay()` | Multiple dispatch sites | Weak — task name | Weak — queue name | Y IF sourced from HTTP (explicit kwarg); N otherwise (F6a) | DEFAULT-CANONICAL (`system` sponsor for beat); DEFAULT-INHERIT elsewhere | Partial — HTTP-sourced sites closeable; beat sites structural |
| 9 | Celery task execution `@shared_task` entry | `core/tasks*.py` | Weak — function name | Weak — queue | N — no `request.user` at process boundary (F6a) | DEFAULT-INHERIT (from kwargs) | N — **F6a STRUCTURAL DROP** at process boundary (contextvars does not cross) |
| 10 | Model pre_save / pre_delete signals | Django signal receivers | Weak (row's agent field, ambiguous) | INHERIT-implicit | Y IF in-band request; N otherwise (F6c) | DEFAULT-NONE for async; DEFAULT-INHERIT for in-band | N — F6c-adjacent STRUCTURAL DROP for async paths |
| 11 | Deliverable status transition | `deliverable_status_signals.py:83-100` | Weak — `Deliverable.agent_name` | INHERIT-implicit | Weak — `Deliverable.user` (nullable) | DEFAULT-INHERIT | Y (row-level inheritance well-defined) |
| 12 | DirectMessage creation | `models_messaging.py` create sites | Y — `sender_type` kind (weak) | INHERIT | Y — `sender` FK (nullable) | DEFAULT-CANONICAL (`system` sender_type for anon) | Y |
| 13 | EventBus.publish | `services/event_bus.py:137-189` | N — `source` weak string | N — publisher-defined | N — no field | DEFAULT-NONE | Y (add three-role kwargs to publish signature) |
| 14 | LLM call — LLMEnforcer.check_budget INLINE | `llm_enforcer.py:200-262` | Weak — `agent_name` | N | N | DEFAULT-INHERIT | Y (accept context dict param) |
| 15 | AgentRouter.route | `core/agent_router.py` | Y — resolved AGENT_MAP key | INHERIT | Y — from constructor | DEFAULT-INHERIT | Y |
| 16 | HumanAttentionItem decision | `views_human_interface.py:84-100` | INHERIT-source | INHERIT | Y — `request.user`; item.user filter | DEFAULT-INHERIT | Y (HTTP surface) |
| 17 | Post-mission retrospective audit | `core/employees/status.py:53-251` | Y — from parent OpsRun `triggered_by` inferring `employee_handle` | Weak — inferred | N unless persisted upstream | DEFAULT-INHERIT | Y IF OpsRun receives actor field (F1 remediation) |
| 18 | WebSocket consumer | `core/consumers*.py` | N | INHERIT (auth token type) | Y when authenticated; N for AnonymousUser | DEFAULT-NONE for anon; DEFAULT-INHERIT for auth | Y (contract spec) |
| 19 | Fleet internal API ingress | `fleet_auth_drf.py:65-150` | Y — `app_slug` HMAC | Y — `app_slug` HMAC (sponsor = executor for services) | N — no human FK | DEFAULT-CANONICAL (fleet `app_slug` for both executor and sponsor) | Y (already carries; contract spec) |
| 20 | Spider run boundary | `core/tasks_spiders.py:381-398` | Weak — `spider_name` | Weak — `run_kind` | N | DEFAULT-CANONICAL (`system` principal) | Y (contract spec) |

**Roll-up counts** across the 20 boundaries:

- **executor_actor available** at entry (strong or weak): 12 / 20
- **sponsor_actor available** at entry: 3 / 20 (strong at fleet;
  weak at 18 + 20; every other boundary requires
  INHERIT or DEFAULT-CANONICAL)
- **principal_user available** at entry: 8 / 20 (strong at 1, 2, 15,
  16, 18-auth; weak/nullable at 4, 8-HTTP, 11)
- **Layer-ii closeable in a P2 shipping shape** (contract passes,
  no structural drop): 13 / 20
- **Structural drops per F6 register (§7.4)**: 6, 7, 9, and
  10-async — 4 boundaries (F6a, F6b implicitly via 9, F6c
  strictly via 6+7, F6c-adjacent via 10-async)

**Layer ii deliverable:** The table above IS the per-boundary
propagation contract per S1900 §5.1 requirement. Every P2 enforcement
binding-point row must cite the corresponding row here for its
role-availability posture (this is the P1↔P2 handoff surface named
by Rigby S1900 SIGN cycle 1 Q4 fold).

### 7.4 LAYER ii — drop-boundary register

Three classes of drop, per §7.2 failure-semantics register:

#### 7.4.1 F6 STRUCTURAL DROPS (inherited from S1271)

- **F6a — HTTP → Celery process boundary.** Verified at Boundary 9
  (`core/tasks*.py`). `request.user` is not marshalled across the
  Celery process boundary; `contextvars` does not survive
  `.apply_async()`. Layer i contract requires explicit-param
  carrier via `apply_async(kwargs={"executor_actor": ...,
  "sponsor_actor": ..., "principal_user": ...})`. Any
  dispatch site that omits the kwargs is a Layer-ii drop; Layer
  ii wiring is a P2 P0 pre-work item (see §19 R.AUTHORITY.
  ACTOR-KWARGS-CELERY). Structural drop preserved for beat-fired
  dispatch where no upstream sponsor exists — recorded as
  DEFAULT-CANONICAL (`sponsor="system"`, `executor=<task_name>`,
  `principal=<runs_as_username-resolved OR None>`).

- **F6b — MissionRunnerConfig → OpsRun row.** Verified at Boundary
  4 + 5. `MissionRunnerConfig.runs_as_username` never persists to
  `OpsRun.user` (verified — no `user` FK on OpsRun,
  `core/models_ops_runs.py:11-88`). This is Layer-ii **CLOSEABLE**:
  either (a) add `OpsRun.user` FK + `OpsRun.employee_handle`
  CharField (S1271 Q3 option c) or (b) add a JSONField-key
  extension carrying the three-role dict in `OpsRun.summary`.
  Choice is P2's under the Enforcement Binding Points map (Rigby
  S1900 SIGN cycle 1 Q4 fold artifact); P1 formalizes shape only.
  Same treatment for `OpsRunEvent`.

- **F6c — MissionRunner → Step.fn signature.** Verified at
  Boundary 6 + 7 (`mission_runner.py:904-917`; `step.fn(mission)`
  receives only OpsRun). Layer-i shape modification requires
  changing the `Step` frozen dataclass + step signatures across
  every job module (200+ estimated call sites per Agent 6 §Q10).
  Structural drop preserved as documented; a scoped
  `contextvars`-based read-only carrier is Layer i-permitted
  (§7.2.2) but requires the runner to set the context before
  each step call. This is P2 P0 pre-work item R.AUTHORITY.
  ACTOR-STEP-CONTEXT.

- **F6c-adjacent — async signal handlers (Boundary 10, Rigby
  S1901 SIGN cycle 1 Q4 fold).** Django `post_save` /
  `post_delete` signal receivers (per Agent 3 §Q8 sample:
  `deliverable_status_signals.py:36-70`, `dream_signals.py:46`,
  `trigger_signals.py:241`, `rigby_delegation_signals.py:131`,
  `document_processing_signals.py:54`) have `request.user`
  available only when the emitting `save()` fires in-band (HTTP
  request context). Async paths — beat-fired writes, Celery worker
  writes, cascading signal fan-outs — have no request context. F6c
  structural pattern rather than a new F6d class: signal handlers
  are the async analog of Step.fn (opaque to the caller's actor
  context; must re-infer from row state OR read a scoped
  `contextvars`-set carrier if the caller opted in via §7.2.2).
  Registered explicitly here to prevent silent loss in P2/P3
  planning. Layer i-permitted read-only `contextvars` carrier is
  the same mechanism as F6c proper; Layer ii wire-up for beat +
  Celery writers is R.AUTHORITY.ACTOR-KWARGS-CELERY (T1).

#### 7.4.2 LAYER-II-CLOSEABLE DROPS (P2 work items)

Boundaries where the propagation contract is Layer-i-parallel-safe
but the code today does not carry it. Each is a P2 wire-up item; P1
records the delta:

- **Boundary 5 warn-mode event schema extension** — add three-role
  fields to `authority_contract_observed` event detail per §7.2.1
  shape. Event schema bump per Rigby S1264 SIGN edit #1 discipline
  (`AUTHORITY_CONTRACT_SCHEMA_VERSION`).
- **Boundary 13 EventBus.publish signature** — accept three-role
  kwargs in `publish()`; write to Event.actor_context field
  (P2 delta; P1 shape only).
- **Boundary 14 LLMEnforcer.check_budget** — accept context dict
  param; enable action_class + role reads for P2 authority binding.
  Preserves LLMEnforcer fail-open per §5.3 verified pattern.
- **Boundaries 2, 3, 15 — PA/ToolDispatcher/AgentRouter** — accept
  three-role dict in the shared context object; document schema.
- **Boundary 17 retro-audit** — extend `evidence_for_mission` to
  read the three roles from OpsRun+OpsRunEvent (blocked on F6b
  closeable delta).
- **Boundary 8 HTTP-sourced Celery dispatch** — every HTTP view
  that fires `.apply_async` or `.delay()` explicitly passes the
  three-role kwargs. Non-HTTP sourced Celery dispatch (beat) is
  structural DEFAULT-CANONICAL.

#### 7.4.3 POST-ARC T-SLOT DROPS

Boundaries documented as structural drops today, deferred to
post-arc T-slot execution:

- **Management commands (adjacent to 8/9)** — no canonical
  operator identity; all 199 commands run without explicit actor
  stamping (per Agent 3 §Q5). T-slot: R.AUTHORITY.MGMT-CMD-ACTOR-CONVENTION.
- **Discord command dispatch (adjacent to 3)** — Discord user ID
  ≠ Django User unless linked. T-slot: R.AUTHORITY.DISCORD-USER-LINKAGE.
- **Spider run (Boundary 20)** — `system` principal is documented
  DEFAULT-CANONICAL; no post-arc work unless a P3 cross-plane
  composition question requires per-spider attribution.
- **Fleet permissive-fallback path** — when Fleet HMAC absent,
  request falls back to Session/Token auth; the transition point
  today does not stamp `request.fleet_identity`. T-slot:
  R.AUTHORITY.FLEET-FALLBACK-ROLE-STAMP.

### 7.5 End-to-end delegation trace (worked example)

To make the contract concrete, this is the role-attribution flow for
one canonical scenario: **Chris invokes Documentation Manager daily
mission via beat schedule → mission emits shift-report DirectMessage
→ retro-audit reads for post-mission evidence.**

| Step | Site | executor_actor | sponsor_actor | principal_user | Notes |
|---|---|---|---|---|---|
| 1 | Beat fires PeriodicTask `rigby_documentation_manager_daily` | `core/celery.py` | `system` (task name) | `system` | N | Beat has no human at process time — Chris scheduled the PeriodicTask days ago but the fire-time sponsor is `system`. DEFAULT-CANONICAL. |
| 2 | Celery `@shared_task` enters `rigby_documentation_manager_daily` | `core/tasks_documentation_manager.py` | INHERIT (`system`) | INHERIT (`system`) | INHERIT (`None`) | F6a boundary. Task kwargs are empty; contract fills with DEFAULT-CANONICAL. |
| 3 | Task constructs `MissionRunnerConfig(employee_handle="rigby", runs_as_username="chris", …)` | `core/jobs/docs_cascade.py` | Y — `"rigby"` (frozen) | INHERIT (`"system"`) | Weak — string `"chris"` (pre-resolution) | F6b entry point. Config carries executor strong; principal via string. |
| 4 | `MissionRunner.__init__` accepts config | `mission_runner.py` | Y | INHERIT | Weak (string) | Boundary 4. Role status enters MissionRunner intact from step 3. |
| 5 | Preflight `_emit_authority_contract_event` (Boundary 5) | `mission_runner.py:835-900` | Y (event field: `employee_handle`) | N (event omits sponsor) | N (event omits principal) | Event today emits only executor. Layer ii-CLOSEABLE per §7.4.2 (event schema extension). |
| 6 | `_resolve_runs_as_user_id` called at line 1432 (verdict path) | `mission_runner.py:1585-1591` | — | — | Weak → Y (if User exists) OR None (silent) | F3 site. Contract requires `[ACTOR_ROLE_RESOLVE_MISS]` log + `actor_meta.gap_reasons` on None return. |
| 7 | Step.fn(mission) executes (Boundary 6+7) | `_run_step` line 917 | INHERIT via closure | INHERIT via closure | INHERIT via closure | F6c structural drop. Step.fn cannot introspect actor context from signature; must close over runner.config or use `contextvars`-scoped read. |
| 8 | Step body writes `Deliverable.user = <principal_id>` | `deliverable_factory.py:...` | Weak — `agent_name="rigby"` | INHERIT | Y or None (from step 6) | `Deliverable.user` nullable. Silent-None if step 6 missed. |
| 9 | Terminal emits shift-report `DirectMessage(sender_type="rigby", sender=None, …)` | `core/employees/comms.py:342-349` | Y — `sender_type="rigby"` (executor kind) | N | N — `sender=None` for system | Boundary 12. sender_type carries executor kind; sender FK None for system-authored. |
| 10 | Retro-audit `evidence_for_mission` reads OpsRun + events (Boundary 17) | `status.py:53-251` | Y IF OpsRun has employee_handle field (blocked on F6b closeable) | Y IF triggered_by preserved as sponsor kind | Y IF OpsRun.user populated (blocked on F6b closeable) | Retro-audit fidelity depends entirely on F6b closure. |

**Trace observation.** The three-role contract survives config
construction (step 3) but is progressively degraded through the
mission chain. sponsor_actor is lost as early as step 1 (beat time).
principal_user drops at step 6 (silent-None on resolve miss) OR at
step 8 (nullable FK). executor_actor is the most robust — preserved
via `employee_handle` string all the way to `sender_type` at
step 9 — but only carries executor **kind** at boundaries 5/9/17,
not specific identity. Retro-audit fidelity (step 10) depends on
F6b closure at Layer ii.

### 7.6 Parallel-safety with S1274 Symbol Mapping Option E

**S1274 §8.2 (verified):** the recommended Option E audit-model
extension shape adds `action_class` + 3 role columns to 5 audit
models (`ToolCallRecord`, `OpsRunEvent`, `LLMCallEvent`,
`CeleryTaskEvent`, `AgentExecution`). §8.4 states: **"Only option
that mechanically carries all 3 roles end-to-end IF audit models
extended."**

**Layer i verification.** The role schema §7.2.1 requires three
keys (`executor_actor`, `sponsor_actor`, `principal_user`). Option E
audit-model columns naming is identical (per S1274 §8.2 verbatim).
No collapse — Option E treats them as three orthogonal columns per
F11 never-collapse discipline. Every role in §7.2.1 has a
persistence-target audit model listed in §7.6 below.

**Persistence-target mapping** (Layer i informative, not P1
committing):

| Role | Audit model target (per Option E) | Existing column to reuse? | Additive migration needed? |
|---|---|---|---|
| executor_actor | `ToolCallRecord.agent_name`, `LLMCallEvent.agent_name`, `CeleryTaskEvent.agent_name`, `AgentExecution.owner_agent` | Yes — but semantics must be canonicalized per F4 (delegator vs. executor) | Migration = documentation + `owner_agent` semantic clarifier + column rename to `audit_executor` (P2 work) |
| sponsor_actor | New column across all 5 models | None | Additive migration required (P2) |
| principal_user | `ToolCallRecord.user_id` (via execution FK), `AgentExecution.user`, `Deliverable.user`, `ChatConversation.user` | Yes — via FK chain | No structural migration needed for models with existing user FK; OpsRun requires new column (F6b closeable) |

**Anti-duplication verification.** Option E `+ action_class` column
does NOT collide with any of the 3 role columns per §7.2.1. The
four columns (`action_class`, `executor_actor`, `sponsor_actor`,
`principal_user`) are orthogonal in Option E's audit-row shape.
Layer i is parallel-safe.

**`principal_user` column-type clarification (Rigby S1901 SIGN
cycle 1 Q2 fold).** For Option E audit columns, `principal_user`
MUST be stored as `principal_user_id` (integer FK to
`UnifiedUser`). Username string is permitted **only** as an
in-flight carrier prior to resolution (e.g.,
`MissionRunnerConfig.runs_as_username`) and MUST NOT appear as an
audit-model column type. The Layer i §7.2.1 union-type value shape
(`principal_user` = int OR string OR None) is scoped strictly to
in-flight boundary carriers; persistence surfaces normalize to the
integer FK at the resolution boundary (F3 remediation of
`_resolve_runs_as_user_id` silent-None is a T2 prerequisite for
this normalization to be safe).

---

## 8. Data Ownership and Lifecycle

For every persistence surface carrying an actor role (from §4.1),
the writer + reader ownership map + lifecycle policy:

### 8.1 Ownership map

| Surface | Writer(s) | Reader(s) | Lifecycle |
|---|---|---|---|
| `AIEmployee.handle` | frozen registry in `core/employees/jobs.py:73-92` — only compile-time write | `MissionRunner.__init__`, `get_employee()`, audit surfaces | Registry lifetime; never mutated at runtime |
| `AIEmployee.runs_as_username` | frozen registry (jobs.py:89) | `_resolve_runs_as_user_id`, config passthrough | Registry lifetime |
| `Agent.name` | Agent factory + S1263 consolidation via `core/services/deliverable_aliases.py:33-36` | AGENT_MAP dispatch, `deliverable.agent_name` writes | DB row lifetime (rare deletes) |
| `AgentExecution.user` | tool_dispatcher, agent handlers (nullable per Session 642) | analytics surfaces, retro-audit | Row lifetime (nullable — silent-None risk) |
| `AgentExecution.owner_agent` | tool_dispatcher, agent handlers (Session 843) | analytics surfaces | Row lifetime; F4-ambiguous |
| `Deliverable.user` | `create_deliverable()` factory + mission step | analytics + user-scoped queries | Row lifetime (nullable) |
| `Deliverable.agent_name` | factory + mission step | analytics + audit | Row lifetime |
| `OpsRun.triggered_by` | mission-creator sites in beat/PA/mgmt callers | retro-audit + observability | Row lifetime (mechanism, not identity) |
| `DirectMessage.sender` | messaging create sites | conversation surfaces | Row lifetime (SET_NULL on user delete) |
| `DirectMessage.sender_type` | messaging create sites | conversation surfaces | Row lifetime |
| `ChatConversation.user` | PA entrypoint on chat init | PA + analytics | Row lifetime (nullable) |
| `ChatConversation.source` | PA entrypoint on chat init | PA + analytics | Row lifetime |
| `FleetServiceIdentity.app_slug` | Fleet registration | Fleet auth ingress | Row lifetime (rare rotate) |

### 8.2 Retention posture

Actor-role rows share the OpsRun / audit-row retention posture: no
dedicated retention policy today. Group 1700 xx99 T0/Gate item
`R.OBSERVABILITY.RETENTION-UNIFIED-ADR` is the delegated retention
work; P1 does not shortcut that ADR by embedding retention rules
here. All actor-role columns inherit their host row's retention.

### 8.3 Silent-mutation risk

- `AIEmployee.runs_as_username='chris'` is hardcoded in
  `jobs.py:89 + 173 + 394 + 668 + 979` (per Agent 6 §Q3). If
  `User(username='chris')` is renamed or deleted, all 4 employees
  silently silent-None resolve. Layer i failure semantics (§7.2.4)
  require the ERROR log; the underlying schema fix is post-arc
  T-slot R.AUTHORITY.RUNS-AS-USERNAME-VERIFIED-AT-STARTUP.

---

## 9. Integrations With Other Domains

Actor-role signals cross plane boundaries and adjacent domain seams.
Each row: source plane, target plane, role-signal status,
Group-1900 owned decision, or delegated to another arc.

### 9.1 Cross-plane integration table

| Source plane / domain | Target plane / domain | Signal today | Group 1900 owned? |
|---|---|---|---|
| HAI (Group 1800) — HumanAttentionItem.user | Authority principal_user | Well-formed FK | Cross-arc — P3 Cat C composition |
| Autonomy (`GovernanceState.mode`) | Authority sponsor | No cross-plane signal | P3 Cat C — composition question 5 (freeze × HAI auto-approve) |
| Budget (LLMEnforcer) | Authority executor | Weak — `agent_name` | P2 (LLMEnforcer INLINE gate row 14) |
| Content pipeline (Group 1600) | Authority principal_user | `Deliverable.user` (nullable) | Cross-arc — P4 Cat F seam audit |
| Memory (Group 1300) | Authority — read-side | `ChatConversation.user` FK | Cross-arc — P3 + P4 (learning plane × read side) |
| Employee OS | Authority — the primitive owner itself | AIEmployee + JobContract frozen | **Group 1900 owned** |
| Sports (Group 1500) | Authority — Discord surface | Discord user linkage (nullable) | Post-arc T-slot R.AUTHORITY.DISCORD-USER-LINKAGE |
| Fleet | Authority sponsor_actor + executor_actor | HMAC `app_slug` (strong) | **Group 1900 owned** (but P4 Cat F seam audit for cross-plane composition with human governance) |
| Observability (Group 1700) | Authority audit trail | Event retention posture | Cross-arc — R.OBSERVABILITY.RETENTION-UNIFIED-ADR (Group 1700 xx99 T0/Gate) |

### 9.2 Explicit delegation to other arcs

- Symbol Mapping choice (S1270 / S1274) — Group 1900 does NOT
  re-open; parallel-safety verified in §7.6.
- Learning-plane contract (Group 1300 + Group 1800 T0/Gate
  R.HAI.LEARNING-PLANE-CONTRACT-ADR) — Group 1900 P3 will
  cross-reference where authority read-side interacts.
- Event Architecture (Group 2000+ deferred slot) — Group 1800
  T0/Gate R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES + this doc's
  §7.4.2 Boundary 13 EventBus wiring are the two candidate feed
  points for that future arc.

---

## 10. Event Flows

### 10.1 EventBus (Boundary 13)

`core/services/event_bus.py:137-189` publish signature accepts an
arbitrary `source` string and a `data` dict. No canonical role
carrier today. Subscribers see whatever the publisher put in `data`.
Layer ii §7.4.2 requires publish signature extension to accept
three-role kwargs (P2 work).

### 10.2 Django signal receivers (Boundary 10)

Sample receivers per Agent 3 §Q8 have zero `request.user` context:
`deliverable_status_signals.py:36-70`, `dream_signals.py:46`,
`trigger_signals.py:241`, `rigby_delegation_signals.py:131`,
`document_processing_signals.py:54`. Handlers must read actor
from the affected row (Deliverable.user, Deliverable.agent_name)
OR from a Layer i `contextvars`-scoped carrier if the caller sets
one (§7.2.2). Async paths remain DEFAULT-NONE.

### 10.3 MissionRunner authority contract event (Boundary 5)

`_emit_authority_contract_event` at 835-900 emits
`authority_contract_observed` (S1264 label). Current schema fields
(verified 880-900): `schema_version`, `employee_handle` (executor),
`contract_title`, `contract_version_tag`, `authority_entries_total`,
`authority_level_counts`, `authority_unknown_level_count`,
`prohibited_actions_count`, `mode='warn'`, `note`. **Missing:
sponsor_actor + principal_user.** Layer ii §7.4.2 event schema
extension bumps `AUTHORITY_CONTRACT_SCHEMA_VERSION` (per Rigby
S1264 SIGN edit #1) and adds the two roles.

---

## 11. Existing Documentation

Documentation inventory of role vocabulary + propagation coverage
(per Agent 5 §Q1-Q2).

### 11.1 Canonical role-vocabulary source

- `docs/research/actor_identity_attribution_architecture.md`
  (S1271) §8.5 lines 1327-1400 — canonical three-role definitions
  + role-to-field mapping + canonical scenario table.
- §11 F11 lines 1707-1733 — never-collapse discipline load-bearing
  finding.
- §11 F6 lines 1662-1670 — three structural drop boundaries
  (a/b/c).

### 11.2 Inherited-vocabulary uses

- `docs/research/authority_enforcement_design_space.md` (S1272) §14.2
  scope for Actor Role Propagation Design (verbatim reproduced in
  §7 of S1900 parent scoping).
- `docs/research/symbol_mapping_option_selection_design.md`
  (S1274) §8 lines 777-880 — Option E audit-model extension
  pattern; three-role compat verified.
- `docs/research/domains/authority_enforcement/1900_authority_enforcement_domain_scoping.md`
  (S1900) §5.1 lines 588-629 — P1 mission scope (verbatim
  reproduced here).
- `docs/EMPLOYEE_OS_PRIMITIVES.md` — AIEmployee + JobContract
  primitive registry (anti-duplication anchor).
- `docs/topics/employee-os.md`, `docs/topics/personal-assistant.md`,
  `docs/topics/agent-system.md` — mention identity fields but do
  NOT enumerate the three-role vocabulary.

### 11.3 Related MEMORY rules

Per Agent 5 §Q4 + parent-verifier read of MEMORY.md index:

- `feedback_factory_silent_none_footgun.md` — factories that
  gate inputs must raise typed exceptions, not silent-None.
  Directly applicable to `_resolve_runs_as_user_id` and every
  role-lookup site in Layer i (§7.2.4 failure semantics).
- `feedback_context_user_is_profile_dict_not_user_instance.md` —
  `context['user']` is a profile dict for LLM prompt injection,
  NOT a User FK source. Layer i explicit-param carrier §7.2.1
  requires `principal_user` be the FK integer or username string,
  never a profile dict.
- `feedback_verifier_loop_pattern.md` — pre-flight verifier
  discipline. This doc's §20.5 verifier fold applies MC-1
  playbook §14 CODIFICATION-CONFIRMED discipline.
- `feedback_fail_loud_first_then_root_cause_then_telemetry.md` —
  Layer i failure semantics §7.2.4 aligns: STRUCTURAL-DROP =
  documented silence; RESOLUTION-FAILURE = fail-loud with
  greppable log prefix.
- `feedback_llm_autofills_boolean_params_with_false.md` — LLM
  autofill patterns are not currently in scope for role-string
  parameters, but Layer ii boundary handlers that accept
  three-role kwargs should reject any of the three being
  autofilled Python `False`.

### 11.4 Explicit gaps

- No current doc defines a **propagation contract** for the three
  roles across boundaries — this doc is the first.
- No current doc enumerates **per-boundary drop-boundary register**
  — this doc is the first.
- No current doc verifies **parallel-safety with Option E** — this
  doc's §7.6 is the first.

---

## 12. Research Coverage

**Coverage classification (playbook §12 taxonomy):** **DEEP** (before
this arc-child) — S1271 provides the vocabulary, S1272 §14.2
provides the two-layer scope, S1274 provides the Option E audit-model
compat frame. This doc elevates the coverage to **CANONICAL** for
propagation contract shape + per-boundary register (first doc-level
authoritative source).

**Coverage by role:**

- **executor_actor** — DEEP prior coverage (S1271 §8.5 + F10 +
  F4 delegator/executor ambiguity). CANONICAL post-P1.
- **sponsor_actor** — LIGHT prior coverage (S1271 §8.5 defines,
  called out as "least-populated"). MODERATE post-P1 (contract
  shape + per-boundary register).
- **principal_user** — MODERATE prior coverage (S1271 §8.5 +
  §11 F3 silent-None + F7 AssistantProfile only gate).
  CANONICAL post-P1.

**Coverage by boundary:** DEEP prior at Boundaries 1, 2, 5, 14,
15, 16, 19. MODERATE prior at Boundaries 4, 8, 9, 10, 12, 17,
18, 20. LIGHT prior at Boundaries 3, 6, 7, 11, 13. Post-P1
Layer ii table (§7.3) elevates every boundary to at least MODERATE
propagation-contract coverage.

---

## 13. Architecture Maturity

Per playbook §12 maturity taxonomy (EXPERIMENTAL / PARTIAL /
WORKING / STABLE / CANONICAL). Verdict per boundary (see §7.3
table for source data).

| Boundary # | Maturity | Rationale |
|---|---|---|
| 1 HTTP auth | STABLE | request.user well-formed; principal strong |
| 2 ToolDispatcher | WORKING | AssistantProfile gate present but silent-skip pattern |
| 3 PA tool handler | PARTIAL | Context passthrough working but no canonical shape |
| 4 MissionRunner entry | PARTIAL | executor strong via frozen registry; principal weak-string; sponsor absent |
| 5 MissionRunner preflight | PARTIAL | shape-counter (F1); no principal/sponsor on event |
| 6/7 Step boundary | EXPERIMENTAL | F6c structural drop; no actor param in signature |
| 8 Celery dispatch (HTTP-sourced) | WORKING; (beat-sourced) EXPERIMENTAL | HTTP passes user_id; beat drops |
| 9 Celery task execution | EXPERIMENTAL | F6a structural drop at process boundary |
| 10 Model signals | PARTIAL (in-band) / EXPERIMENTAL (async) | in-band has request.user; async has none |
| 11 Deliverable status transition | WORKING | Row-level actor accessible via Deliverable.user + agent_name (both nullable) |
| 12 DirectMessage | WORKING | sender_type well-defined; sender FK nullable pattern documented |
| 13 EventBus | EXPERIMENTAL | source string weak; no role carrier |
| 14 LLMEnforcer INLINE | PARTIAL | agent_name weak; task_type weak; fail-open by design |
| 15 AgentRouter | WORKING | AGENT_MAP strong; user from constructor |
| 16 HumanAttentionItem | STABLE | request.user; item.user; role well-defined |
| 17 Retro-audit | PARTIAL | employee_handle inferrable from OpsRun.triggered_by; principal blocked on F6b |
| 18 WebSocket consumer | WORKING (auth) / EXPERIMENTAL (anon) | auth well-formed; anon path DEFAULT-NONE |
| 19 Fleet ingress | STABLE | HMAC-verified strong for executor+sponsor; principal null-tolerant |
| 20 Spider run boundary | PARTIAL | spider_name strong; user system (documented DEFAULT-CANONICAL) |

**Roll-up:** STABLE 3 / WORKING 5 / PARTIAL 7 / EXPERIMENTAL 5 / (0 CANONICAL). **Overall domain maturity: PARTIAL** — no boundary is CANONICAL for the three-role contract today; the propagation surface is uneven and structural drops persist at 5 boundaries.

---

## 14. Known Drift

Drift matrix — where docs / prior claims disagree with runtime
(verified via §20.5 verifier-loop fold).

| Claim | Documented in | Runtime status | file:line | Drift severity |
|---|---|---|---|---|
| OpsRun captures who ran the mission | S1272 §6.3 (already stated FALSE) | CONFIRMED — no user FK, no employee_handle field | `core/models_ops_runs.py:11-88` | **HIGH — DOCUMENTED DRIFT** |
| `AIEmployee.runs_as_username` verified at runtime | S1271 F3 (already stated NO) | CONFIRMED — silent-None on `_resolve_runs_as_user_id` | `core/employees/mission_runner.py:1585-1591` | **HIGH — DOCUMENTED DRIFT** |
| `AssistantProfile.get_allowed_tools()` reads canonical request.user chain | S1271 F7 (already flagged as sole gate) | CONFIRMED — silent-skip pattern at profile-None + allowed-None | `core/services/tool_dispatcher.py:685-720` | **MEDIUM — SILENT-SKIP LOGGED ONLY AT DEBUG** |
| `MissionRunner._emit_authority_contract_event` populates 3 roles | S1272 F1 (already stated NO — shape-counter) | CONFIRMED — event fields do not include sponsor / principal | `core/employees/mission_runner.py:880-900` | **DOCUMENTED (not drift; design limitation)** |
| Step.fn receives actor parameter | S1271 F6c (already stated NO) | CONFIRMED — `step.fn(mission)` at line 917; no actor kwarg | `core/employees/mission_runner.py:904-917` | **DOCUMENTED STRUCTURAL DROP** |
| `LLMEnforcer` fail-open at 237-238 | S1272 §H (already stated) | CONFIRMED — exact string match | `core/llm_enforcer.py:237-238` | **DOCUMENTED (not drift; design)** |
| `AuthorityLevel` enum has 4 members + 1 consumer | S1272 F1 (already stated) | CONFIRMED — 4 members at 41-52; 1 consumer at 864-874 | `core/employees/jobs.py:41-52`; `mission_runner.py:864-874` | **DOCUMENTED (not drift)** |
| KillSwitch has 5 read sites + 0 pre-dispatch enforcement | S1272 F2 (states 5 sites) | Agent 6 grep found 10+ sites in `ops_autopilot/`; ALL post-facto (intelligence / monitoring); ZERO pre-dispatch | Per Agent 6 §Q5 | **PARTIAL DRIFT** — S1272 count under-states by ~5; enforcement absence CONFIRMED. **Fold to P2 evidence base at Enforcement Binding Points map.** |

**Drift-treatment:** the KillSwitch site-count drift is captured
here for P2 to consume via the Enforcement Binding Points map (per
Rigby S1900 SIGN cycle 1 Q4 fold); no anchor edit needed.
The other drifts are documented-as-designed (not surprises).

---

## 15. Known Technical Debt

Debt matrix per Agent 6 §Q2 + parent-verifier reads.

| Debt item | Severity | Site | Rationale |
|---|---|---|---|
| Silent-None on `_resolve_runs_as_user_id` | **CRITICAL** | `mission_runner.py:1585-1591` | Every downstream principal_user FK write silently receives None; F3 |
| `agent_name` delegator/executor ambiguity across 4 fields | **HIGH** | `ToolCallRecord.agent_name`, `AgentExecution.owner_agent`, `LLMCallEvent.agent_name`, `Deliverable.agent_name` | F4 — semantics unspecified; readers cannot distinguish delegator (Rigby) from executor (worker) |
| `runs_as_username` hardcoded across 4 employees + unverified at startup | **HIGH** | `jobs.py:89, 173, 394, 668, 979` | If `User(username='chris')` renamed/deleted, all 4 employees silent-None; no startup alert |
| F6 structural drops (3 boundaries) | **HIGH** | Boundaries 6/7/9 | Structural today; F6b closeable at Layer ii; F6a + F6c require broader P2 work |
| sponsor_actor least-populated (13 / 20 boundaries) | **MEDIUM** | Per §7.3 roll-up | No explicit sponsor FK anywhere; mechanism enums are proxy |
| `deliverable.user = context.get('user')` patterns silent-None-tolerant | **MEDIUM** | Deliverable factory + step body writers | Companion to CRITICAL row above; user FK nullable accepts None silently |
| Missing schema-level three-role contract enforcement on multi-role tables | **MEDIUM** | AgentExecution + Deliverable + ToolCallRecord + LLMCallEvent | No FK constraint that executor / principal columns must be consistent |
| Zero test coverage for the three-role vocabulary | **MEDIUM** | Per Agent 6 §Q8 | grep confirms 0 tests named for actor/executor/sponsor/principal |
| EventBus `source` string is caller-controlled with no enforcement | **LOW** | `event_bus.py:137-189` | Weak by design; Layer ii wire-up (P2) fixes |
| `context['user']` = profile dict, not User instance | **LOW** (contract level) | Sessioned pattern rule captured in MEMORY | Layer i §7.2.1 explicit shape prevents recurrence for role fields specifically |

---

## 16. Boundary Violations

Actor-role signal violations of the F11 never-collapse discipline
(where two roles are stored in one field or two fields do not
have a consistency contract):

- **`AgentExecution` — `user` FK + `owner_agent` CharField without
  consistency contract.** No enforcement that `owner_agent` maps
  to an Agent row for the same `user` context; F4 delegator vs.
  executor undefined.
- **`Deliverable` — `user` FK + `agent_name` CharField without
  consistency contract.** Same shape as AgentExecution.
- **`OpsRun.triggered_by` used as sponsor + principal in different
  reader contexts.** Some retro-audit code treats `triggered_by='pa_tool'`
  as a sponsor kind; other code infers a principal_user via
  `runs_as_username` lookup. Layer i decouples this by naming
  `triggered_by` strictly as **sponsor_actor kind** (mechanism); a
  separate principal_user field is P2 closeable work.
- **`ChatConversation.source` used inconsistently in downstream
  code.** Some sites treat `source='claude-code'` as executor
  (agent identity) and others as sponsor (autonomous engineer as
  request originator). Layer i names it strictly **sponsor_actor
  kind**; downstream normalization is a Layer ii wire-up.

---

## 17. Duplicate or Overlapping Systems

Duplicate identity primitives across domains (per Agent 4 §Q2):

- **`AIEmployee.handle`** (`core/employees/jobs.py:87`) vs.
  **`Agent.name`** (via AGENT_MAP) — both are executor_actor
  string keys, from two separate registries. Both are strong in
  their own registry; the overlap surfaces when Rigby-as-Agent-row
  is confused with Rigby-as-AIEmployee. Layer i preserves both as
  distinct producers (executor may come from EITHER canonical
  registry).
- **`AIEmployee.runs_as_username`** vs. **`request.user.username`**
  — both are principal_user *carriers* but the first is a selector
  string (deferred resolution) and the second is a live FK.
  §7.2.1 permits both value shapes for `principal_user` and
  documents which surfaces produce which.
- **`OpsRun.triggered_by`** enum vs. **`ChatConversation.source`**
  enum — both are sponsor_actor kind proxies. Overlap in
  semantics (`'pa_tool'` vs. `'pa'`, `'management_cmd'` vs.
  `'api'`). Layer i cross-references but does not merge.
- **`DirectMessage.sender_type`** vs. **`ChatConversation.source`**
  — one is executor kind, one is sponsor kind; not truly
  duplicates but often conflated in downstream code that reads
  either as "who did this."

---

## 18. Ownership Gaps

Ownership gaps in actor-role signal maintenance:

- **`OpsRun.triggered_by` writer canonicality.** No single owner;
  every mission-creator (beat wrapper, PA tool caller, mgmt
  command, manual) writes it independently. Layer ii §7.4.2
  requires the writer surface to also stamp the three-role dict;
  today only the mechanism enum is stamped.
- **sponsor_actor across the platform.** No owning code path;
  sponsor is inferred at read time by each consumer independently.
  Layer i names sponsor as a first-class role but does not choose
  the owner-writer; the Enforcement Binding Points map (P2) does.
- **F6c Step.fn actor propagation.** No owner — the Step type is
  runtime-facing but 200+ step implementations exist across job
  modules (Agent 6 §Q10). Any signature change requires a
  coordinated PR set; ownership sits with Group 1900 P2 pre-work.

---

## 19. Recommended Future Research

Ranked by architectural uncertainty × risk × unblocked flows.
Feeds directly into the xx99 §8 T0/Gate + T1 + T2 + T3 tiered
queue.

### 19.1 T0 / Gate — pre-P2 blockers

- **R.AUTHORITY.ENFORCEMENT-BINDING-POINTS-MAP** — Required per
  Rigby S1900 SIGN cycle 1 Q4 fold. P2's first deliverable; P1's
  §7.3 table is the input shape. Every enforcement binding point
  must cite the P1 row it consumes.

### 19.2 T1 — critical for P2 correctness

- **R.AUTHORITY.ACTOR-KWARGS-CELERY** — Layer ii wire-up for
  Boundary 8/9. Every HTTP-sourced Celery dispatch site must pass
  three-role kwargs; every beat-sourced site must stamp
  DEFAULT-CANONICAL. Blocked on P2 pick of shape (dict kwarg vs.
  three named kwargs).
- **R.AUTHORITY.ACTOR-STEP-CONTEXT** — Layer ii wire-up for
  Boundary 6/7 (F6c). `contextvars`-scoped read-only carrier set
  by MissionRunner before each step call; documented drop
  preserved for step.fn signature.
- **R.AUTHORITY.EVENT-SCHEMA-EXTENSION** — Bump
  `AUTHORITY_CONTRACT_SCHEMA_VERSION` per S1264 SIGN edit #1; add
  three-role fields to preflight event.
- **R.AUTHORITY.OPSRUN-ACTOR-COLUMNS** — F6b closeable at Layer ii.
  Add `OpsRun.user` FK + `OpsRun.employee_handle` CharField OR
  extend `OpsRun.summary` JSONField with the three-role dict
  (choice is P2's under Enforcement Binding Points map).

### 19.3 T2 — important for P3 cross-plane composition

- **R.AUTHORITY.DELEGATION-CHAIN-MODEL** — F4 delegator vs.
  executor consistency contract. Split `agent_name` into
  `caller_agent` + `executor_agent` OR use a delegation-chain
  table with parent-child links.
- **R.AUTHORITY.RUNS-AS-USERNAME-VERIFIED-AT-STARTUP** — F3
  silent-None remediation. Fail-loud on missing `User(runs_as_username)`
  at `MissionRunnerConfig` construction time.
- **R.AUTHORITY.SPONSOR-ACTOR-CANONICAL-WRITER-POLICY** — sponsor
  is currently no-one's job; establish the canonical write site
  per boundary family (HTTP / autonomous / delegated).

### 19.4 T3 — nice-to-have follow-on

- **R.AUTHORITY.MGMT-CMD-ACTOR-CONVENTION** — Document canonical
  actor stamp for management commands.
- **R.AUTHORITY.DISCORD-USER-LINKAGE** — Cross-plane with Group
  1500 Sports Discord surface: canonical Discord ID → Django User
  linkage discipline.
- **R.AUTHORITY.FLEET-FALLBACK-ROLE-STAMP** — When Fleet HMAC
  absent, request falls back to Session/Token auth; the transition
  point today does not stamp `request.fleet_identity` as a
  DEFAULT-CANONICAL executor.
- **R.AUTHORITY.THREE-ROLE-TEST-COVERAGE** — Zero test coverage
  today; add end-to-end propagation tests for the three roles.

### 19.5 Cross-arc T-slot handoffs

- Cross-reference `R.HAI.LEARNING-PLANE-CONTRACT-ADR` (Group
  1800 T0/Gate) — P3 authority read-side interacts with the
  learning plane contract shape.
- Cross-reference `R.OBSERVABILITY.RETENTION-UNIFIED-ADR` (Group
  1700 T0/Gate) — authority-audit rows inherit retention posture
  from that ADR.
- Cross-reference `R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES` (Group
  1800 T0/Gate, deferred to Group 2000+) — Boundary 13
  EventBus.publish wiring (§7.4.2) is the second candidate
  feed-point.

---

## 20. Appendix

### 20.1 Files inspected

**Runtime code** (direct parent-verifier reads):
- `core/employees/mission_runner.py` (lines 830-900, 902-962, 1580-1595)
- `core/employees/jobs.py` (lines 40-92)
- `core/models_ops_runs.py` (lines 1-118)
- `core/llm_enforcer.py` (lines 230-245)
- `core/services/tool_dispatcher.py` (lines 685-725)

**Runtime code** (sub-agent reads, verifier-loop applied):
- `core/models_deliverables.py` (Deliverable model)
- `core/models_unified_system.py` (Agent + AgentExecution + AgentControlEntry)
- `core/models_messaging.py` (DirectMessage)
- `core/models/conversations/models.py` (ChatConversation)
- `core/models_assistant_profile.py`
- `core/models/fleet.py`
- `core/models_tool_calls.py` (ToolCallRecord)
- `core/models_llm_telemetry.py`
- `core/models_celery_telemetry.py`
- `core/services/event_bus.py`
- `core/services/fleet_auth_drf.py`
- `core/services/tool_context.py` (contextvars precedent)
- `core/services/unified_pa_entrypoint.py`
- `core/agent_router.py`
- `core/auth_middleware.py`
- `core/consumers*.py` (WebSocket)
- `core/views_personal_assistant.py` (dispatch patterns)
- `core/signals/deliverable_status_signals.py`
- `core/tasks_documentation_manager.py` (task ingress)
- `core/jobs/docs_cascade.py` (config construction)
- `core/tasks_spiders.py:381-398` (governance gate)

### 20.2 Docs inspected

- `docs/research/actor_identity_attribution_architecture.md` (S1271)
  §8.5, F6, F11
- `docs/research/authority_enforcement_design_space.md` (S1272)
  §3.1, §14.2
- `docs/research/symbol_mapping_option_selection_design.md` (S1274)
  §8 (Option E)
- `docs/research/domains/authority_enforcement/1900_authority_enforcement_domain_scoping.md`
  (S1900) §5.1 + §7 + §8
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2, §13, §14
- `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` §5, §8
- `docs/EMPLOYEE_OS_PRIMITIVES.md`
- `MEMORY.md` (feedback_factory_silent_none, feedback_context_user_is_profile_dict,
  feedback_verifier_loop_pattern, feedback_fail_loud_first_then_root_cause_then_telemetry)

### 20.3 Grep patterns used

- `_resolve_runs_as_user_id\(` — 3 sites in `mission_runner.py`
  (1432 call, 1500 call, 1585 def)
- `runs_as_username` — inventory across `jobs.py`, `mission_runner.py`,
  test fixtures, job configs
- `\.apply_async\(kwargs=` — Celery kwargs propagation
- `contextvars` / `threading.local` — thread-local propagation
  (S1199 tool_context precedent; zero actor-role uses)
- `AUTHORITY_CONTRACT_OBSERVED_LABEL` — S1264 warn-mode event
- `AuthorityLevel` — enum + consumer sites
- `sender_type` / `source` / `triggered_by` — sponsor/executor
  kind proxies

### 20.4 Unresolved unknowns

- **Fleet permissive-fallback outcome fidelity.** When Fleet HMAC
  absent, the transition to Session/Token auth today does NOT
  stamp `request.fleet_identity`. Whether this transition point
  should DEFAULT-CANONICAL a stamp or DEFAULT-NONE is a P4 Cat F
  seam-audit question.
- **`_router_heartbeat_loop` role-availability** for beat-fired
  non-PA agent dispatch. Agent 2 §Q5 could not locate the loop in
  the surveyed range; parent-verifier deferred until §19.4 T3
  R.AUTHORITY.THREE-ROLE-TEST-COVERAGE consumes.
- **Discord-user linkage failure semantics.** Layer i handles
  Discord commands as DEFAULT-NONE for principal when linkage
  absent; whether P3 cross-plane composition wants a stricter
  policy is deferred to P3 question 8 (authority × Discord
  command dispatch enforcement).

### 20.5 Verifier-loop corrections (MC-1 CODIFICATION-CONFIRMED)

Playbook §14 REQUIRED pre-Explore + post-Explore verifier-loop
folds recorded here per S1899 §10.2 MC-1 CODIFICATION-CONFIRMED
milestone extended at S1900 SIGN cycle 1.

**Pre-Explore reads (10 spot checks; §verifier_loop frontmatter):**
all 10 confirmed. No sub-agent claim required correction pre-fire.

**Post-Explore folds:**

- **Agent 1 §Q6 — `AgentExecution.owner_agent` migration age.**
  Agent 1 gave "~0168 / Session 843" as earliest; parent-verifier
  did not confirm exact migration number due to migration-tree
  size. Recorded as SPECULATIVE for that specific migration
  number; the broader claim (Session 843 is when owner_agent was
  added) stands per grep of session handoffs.
- **Agent 3 §Q7 — Spider identity user attribution.** Agent 3
  reported user_attribution as "weak — spiders run under `system`."
  Parent-verifier confirmed `system` at `tasks_spiders.py:381-398`
  freeze/safe_mode read; verified.
- **Agent 6 §Q5 — KillSwitch read-site count.** Agent 6 grep
  found 10+ read sites in `ops_autopilot/{intelligence,governance}.py`;
  S1272 F2 evidence base states 5. Parent-verifier did not re-count
  in-doc but recorded the drift explicitly in §14 (drift matrix) as
  a P2 evidence-base fold. Not blocking for P1.
- **Agent 6 §Q7 — MEMORY rule file paths.** Agent 6 flagged "no
  such .md files found in docs/." Parent-verifier confirms
  MEMORY.md file paths are correct: they live at
  `/Users/donkeyking/.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/`
  per CLAUDE.md auto-injected memory rules; not in `docs/`.
- **Agent 4 §Q1 — Delegation chain sub-agent dispatch source
  step example uses `execute_agent_task.apply_async` at
  `views_personal_assistant.py:462`.** Parent-verifier did not
  re-read the exact line but the pattern shape (kwargs =
  `{"user_id": request.user.id}` when HTTP-sourced) matches
  Agent 3 §Q9's independent sampling. Cross-corroboration
  sufficient.

### 20.6 Conflicts between sources (none load-bearing)

None. The only conflict-adjacent finding is the KillSwitch
site-count drift noted in §14 which is P2 evidence-base scope,
not P1.

### 20.7 Rigby SIGN fold notes

**SIGN cycle 1 — 2026-07-04 — SIGN-with-edits at High confidence.**
Arc pin `pa-2bd1613ce2bd4a9c`. D48 33rd arm turn 1 CLEAN per
single-batch-4-question criterion →
28-consecutive-fully-clean-arms sub-pattern EXTENDED at S1901 SIGN
cycle 1 milestone (MC-2 CODIFICATION-CONFIRMED milestone extended
27 → 28 consecutive).

**Three folds landed pre-commit:**

1. **Q1 fold — §7.2.1 F11 mechanical prohibition sentence.** Added
   explicit "No single `actor` key or column is permitted as a
   fallback carrier" rule after the shape block. Rationale: prose
   grep hits for singular "actor" (e.g., "no actor field"
   descriptive text) risked being read as an implicit permission
   for future callers to bypass the three-key shape. Rule closes
   the residual ambiguity mechanically.

2. **Q2 fold — §7.6 principal_user column-type clarification.**
   Added: for Option E audit columns, `principal_user` MUST be
   stored as `principal_user_id` (int FK); username string is
   permitted **only** as in-flight carrier prior to resolution.
   Rationale: §7.2.1 permitted a union type (int OR string OR None)
   which is correct for in-flight but risked being misread as an
   audit-column type. F3 remediation of `_resolve_runs_as_user_id`
   silent-None flagged as T2 prerequisite for safe normalization.

3. **Q4 fold — §7.4.1 F6c-adjacent Boundary 10 async register
   entry.** Added explicit bullet registering Boundary 10 (Django
   post_save/post_delete signal receivers) as F6c-adjacent
   structural drop for async paths. Rationale: Rigby caught the
   register-completeness gap where §7.3 row 10 flagged
   "F6c-adjacent STRUCTURAL DROP for async paths" but §7.4.1 only
   enumerated F6a/F6b/F6c. Registering explicitly prevents silent
   loss in P2/P3 planning. Rigby's own recommendation: no new F6d
   class; F6c pattern extended to signal receivers as async analog
   of Step.fn.

**Q3 fold — not adopted.** Rigby offered an optional column-header
rename in §7.3 ("Layer-ii closeable?" → "closeable without
changing the boundary class"). Skipped as non-load-bearing
clarification; original header preserved for consistency with
prior child-audit table columns.

**Verdict:** SIGN-with-edits at High confidence. Q1/Q2/Q4 folds
land pre-commit; Q3 skipped as optional.

### 20.8 Frontmatter provenance

- `status: draft` pending Chris commit-gate + Rigby SIGN cycle 1.
- `session: 1901`, `child_slot: P1_cat_a`, `domain_slug:
  authority_enforcement`, `research_group: 1900`,
  `mission_type: child_audit_design`.
- Anchor v-bumps deferred to xx99 canonical summary per playbook
  §11.3 §7 discipline.

---
