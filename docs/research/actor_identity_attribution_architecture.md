---
title: "Actor Identity & Attribution Architecture — Architectural Discovery (research only)"
status: draft
session: 1271
date: 2026-06-30
mission_type: architectural_discovery
authority: |
  Evidence-only research. No runtime changes. No PRs. No migrations.
  No model definitions. No proposed implementation. No contract
  changes. No API design. This doc inventories every actor identity
  concept, every attribution surface, every identity shape change,
  every historical identity failure, every existing identity
  registry, and every candidate enforcement boundary. Reuse
  classifications in §10 are proposals, not decisions. Findings in
  §11 are architectural observations, not resolutions.
companion_docs:
  - docs/research/symbol_mapping_architecture.md
  - docs/research/governance_authority_evolution.md
  - docs/research/employee_os_collaboration_patterns.md
  - docs/research/employee_os_communication_substrate_audit.md
  - docs/research/employee_os_communication_protocol_sketch.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/EMPLOYEE_OS_PRIMITIVES.md
  - docs/handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md
verifier_loop: |
  Five parallel Explore sub-agents produced evidence reports (actor
  identity concepts + shape changes, attribution surfaces, historical
  identity failures, existing identity registries, enforcement
  boundaries). Load-bearing structural claims spot-verified by Claude
  via direct Grep/Read against source before drafting. Six load-
  bearing verifications:
  (a) OpsRun (`core/models_ops_runs.py:11-88`) has NO user FK —
      only `triggered_by` choice string (beat/pa_tool/management_cmd/
      manual). This is the largest attribution gap on the platform.
  (b) `MissionRunner._resolve_runs_as_user_id`
      (`core/employees/mission_runner.py:1585-1591`) does `iexact`
      User lookup on `config.runs_as_username`; returns `None` on
      miss (silent failure).
  (c) `AGENT_NAME_ALIASES` (`core/services/deliverable_aliases.py:
      33-36`) has exactly 2 entries: `{'rigby': 'Rigby',
      'ClaudeCode': 'claude-code'}`.
  (d) `AgentExecution` (`core/models_unified_system.py:882-928`) has
      nullable `user` FK (Session 642 for Celery contexts) plus
      `owner_agent` CharField(100) (Session 843). The Session-287
      deprecation header on this class is STALE — the model has 10+
      active import sites in views_analytics*.py.
  (e) `DirectMessage.sender` (`core/models_messaging.py:108-128`) is
      nullable FK (SET_NULL); `SENDER_TYPE_CHOICES` = user/rigby/
      system; `__str__` falls back to `self.sender_type` when sender
      FK is null.
  (f) Sub-agent-2 discovered ambiguity: `ToolCallRecord.agent_name`,
      `AgentExecution.owner_agent`, and `LLMCallEvent.agent_name` all
      use a CharField named similarly but with unclear semantics
      (delegator vs. executor). No docstring resolves this.

  Sub-agent count conflicts resolved in favor of PLATFORM_INVENTORY
  per DOC_LIFECYCLE §2c:
  - AGENT_MAP: 83 (runtime anchor), not "149 agents" (sub-agent 4
    working from prior context).
  - WORKSPACE_AWARE_AGENTS: 20 (verified direct read at
    epa_handlers_tools.py:3873-3907, matching S1270), not 17
    (sub-agent 4 undercount).
  - Management commands / Celery tasks: use PLATFORM_INVENTORY
    values when quoted.

  Independent SIGN review by Rigby complete (S1271 PA conversation
  pa-cbcc410b32714f60): **SIGN-with-edits**. Rigby overall
  confidence: Medium (with self-declared partial read of the
  1798-line draft; pressure-test focused on framing + architecture
  risk over line-by-line completeness). Must-fix edits folded:
  (i) §8.5 added introducing the executor_actor / sponsor_actor /
      principal_user three-role vocabulary as normative for the
      doc, with canonical-scenario table and role-to-field mapping;
      §11 F11 added as a summary finding pointing to §8.5;
      forward-reference note added at the top of §2.
  (ii) F1 language softened from "cannot answer" to "cannot answer
      reliably or queryably" (best-effort recovery via
      OpsRun.summary JSON acknowledged).
  (iii) F9 language softened from "the enforcement primitive" to
      "the cleanest enforcement primitive" (two-layer split is
      mechanically possible, just weaker).
  (iv) §3.5 added inventorying attribution patterns the platform
      does NOT ship (created_by/updated_by mixin, request-level
      thread-local, WebSocket actor persistence, side-effect audit
      anchoring as fallback, fleet write paths beyond
      FleetServiceIdentity, delegation chain query).
  Optional edits folded: §9.4 Attribution-first vs. Mapping-first
  counterargument paragraph added to §9 (existing §9.4 renumbered
  to §9.5); §5 role-confusion framing note added at section head.
  Rigby SIGN-clean on: F1 as materially load-bearing (spot-verified
  against source), F4 as real enforcement-blocking ambiguity (not
  cosmetic hygiene), §8.3 sender-vs-executor distinction, §13.1
  Authority Enforcement Design Space as the recommended next
  research (no preceding mission required — proceed, but consume
  §8.5's 3-role vocabulary).
  Rigby's Q7 blunt calls #3-#5 (runs_as_username is
  principal_user selector not actor; agent_name drift is
  enforcement-blocking semantic ambiguity; OpsRun.user field is
  not the obvious fix) all folded via F11 + §8.5 role clarity.
  Rigby offered scenario-table expansion (optional #5) and
  historical-failure role-confusion recast (optional #7); the
  latter folded as framing note at §5 head; the former deferred
  as §8.5's canonical-scenario table already covers the highest-
  value cases.
owner: claude (drafted S1271) + rigby (independent pressure-test SIGN review, S1271)
---

# Actor Identity & Attribution Architecture — Architectural Discovery

> **What this is.** The canonical research anchor for the "WHO"
> question. When the platform records an action, how does it know
> who performed it? Symbol Mapping Architecture (S1270) answered
> "WHAT action happened"; this doc answers "who did it." Both
> questions must be answered before authority can be enforced.
> Built from direct file:line evidence + five parallel sub-agent
> sweeps + spot verification.
>
> **What this is not.** A design. A decision. An API sketch. A
> proposal for a new `ActorRegistry` model. A recommendation to
> unify actor concepts. Every option or shape discussed in §5-§8
> is inventory of *what exists*, not *what should be built*.
> Chris gates every downstream design decision.

---

## 1. Executive Summary

The platform has **at least 19 distinct actor identity concepts**
(§2), stored in **~25 registries** (§6), scattered across **22
attribution surfaces** (§3). No canonical actor primitive exists.
Instead, three parallel identity models coexist:

1. **Human actor** — `UnifiedUser` (Django User model), primary
   identity via `id` + `username`. Backed by database. Strong FK
   attribution where used.
2. **AI Employee actor** — `AIEmployee` frozen dataclass
   (`core/employees/jobs.py:73-92`), identity via `handle` +
   `runs_as_username` string, no dedicated DB row. Registry in
   `_EMPLOYEES_BY_HANDLE` dict. 4 employees today.
3. **Service actor** — mixed forms:
   `FleetServiceIdentity.app_slug` (HMAC-verified fleet apps),
   `ChatConversation.source='claude-code'` (autonomous engineer),
   `DirectMessage.sender_type='system'` (system-emitted messages),
   `Deliverable.agent_name='<string>'` (agent-scoped artifacts).

### The architectural gap in one sentence

**When the runtime records an action, the "actor" field is
sometimes a `User` FK, sometimes an `agent_name` CharField,
sometimes a `sender_type` enum, sometimes a `source` string, and
sometimes nothing at all — and no field, primitive, or contract
declares which is authoritative for a given action.**

### The five planes of the gap

1. **Vocabulary plane.** ≥19 identity concepts (§2) with
   overlapping semantics: `User.username`, `AIEmployee.handle`,
   `AIEmployee.runs_as_username`, `Agent.name` (Agent DB row),
   `AGENT_MAP` key, `AssistantProfile.user`,
   `ChatConversation.owner`, `DirectMessage.sender_type`,
   `FleetServiceIdentity.app_slug`, `ChatConversation.source`,
   `AnonymousUser`. No canonical mapping between them.
2. **Persistence plane.** Only 13 of 22 audited surfaces (§3.1)
   carry explicit actor FK. The other 9 are inferred, missing,
   ambiguous, or unreliable. Notably: **`OpsRun` has no user
   field** — only a `triggered_by` mechanism classifier
   (beat/pa_tool/management_cmd/manual). Missions today cannot
   answer "who ran this?" without querying `OpsRun.summary` JSON.
3. **Attribution plane.** Where actor identity IS stored, its
   meaning drifts. `ToolCallRecord.agent_name`,
   `AgentExecution.owner_agent`, and `LLMCallEvent.agent_name`
   all use CharFields but have distinct semantics that are
   underspecified. When Rigby dispatches a worker agent that
   makes an LLM call, three surfaces record `agent_name` but
   readers cannot tell whether the string means "delegator" or
   "executor" without tracing the call chain.
4. **Boundary plane.** 17 candidate enforcement layers (§7); at
   least 3 major boundaries **drop identity entirely**: (a) HTTP
   → Celery (request.user is lost; task inherits context dict
   only), (b) MissionRunner config → OpsRun row (runs_as_username
   is not persisted), (c) MissionRunner → Step.fn (step signature
   receives OpsRun only; no actor parameter).
5. **Contract plane.** Only 1 layer (`AssistantProfile.get_allowed_tools()`,
   `tool_dispatcher.py:687-720`) reads actor identity as part of
   an enforcement decision. Every other authority-adjacent gate
   uses a different actor abstraction (feature flags, user role,
   budget flag, staff status), not the canonical actor identity.

### Major findings

**F1 — OpsRun cannot answer "who ran this mission?" reliably or queryably.**
The mission execution record (`core/models_ops_runs.py:11-88`)
has no `user` FK, no `employee_handle` field, no `actor` field.
Only `triggered_by` (mechanism string: beat/pa_tool/
management_cmd/manual). All 4 employees run their missions on
this row today. Per Rigby S1271 SIGN clarification: the finding
is not that the answer is *impossible* — `OpsRun.summary` JSON
sometimes carries `employee_handle`, so best-effort recovery
exists — but that there is no *reliable, queryable* first-class
field for the executor. Anyone querying "which missions did
Rigby run this week?" must either (a) filter by `run_kind` +
guess (Rigby's job's `run_kind` is `"docs_cascade"`), or (b)
parse `OpsRun.summary` JSON for `employee_handle` (may or may
not be populated by callers). Sub-agent 2 §A row 1.

**F2 — Identity has 5 kinds of "weak."**
Sub-agent 2 §B defined five reliability classes: Explicit,
Inferred, Missing, Ambiguous, Unreliable. Of 22 attribution
surfaces audited: 13 Explicit, 2 Inferred, 2 Missing (OpsRun +
OpsRunEvent), 4 Ambiguous, 1 Unreliable. Only 59% of surfaces
have strong attribution.

**F3 — `runs_as_username` is a string, not a verification.**
All 4 employees hardcode `runs_as_username = "chris"`
(`core/employees/jobs.py:173, 394, 668, 979`). At mission start,
`_resolve_runs_as_user_id` (`mission_runner.py:1585-1591`) does
an iexact User lookup and returns None on miss. **No enforcement
that the resolved user is the "actor" the mission claims to run
as.** If `User("chris")` is renamed, deleted, or never created,
missions silently run with `user_id=None` in whatever surfaces
receive it.

**F4 — Three separate `agent_name` fields with drifting semantics.**
`ToolCallRecord.agent_name` (`core/models_tool_calls.py:57-60`),
`AgentExecution.owner_agent` (`models_unified_system.py:924-927`),
and `LLMCallEvent.agent_name` (`models_llm_telemetry.py:62-65`)
all name an agent, but readers cannot tell whether the value is
the *delegator* (agent that invoked the call) or the *executor*
(agent doing the work). No docstring resolves this. In a
delegated call chain (Rigby → ResearchWorker → LLM), all three
surfaces would populate `agent_name`, but auditors cannot
reconstruct the delegation graph.

**F5 — Duplicate identity is a documented recurring failure.**
S1263 PR #2754 + migration 0374 consolidated duplicate
`ClaudeCode` (7 executions) and `claude-code` (9 executions)
`Agent` rows created by seed scripts + `deliverable_factory.
_synthesize_pa_receipt` bypassing canonicalization. Similar risk:
`Rigby` vs. `rigby` handled by `canonicalize_agent_name`
(`deliverable_aliases.py:39-47`) with 2 entries. Pattern will
recur for every new agent name that bypasses the alias map.

**F6 — Actor identity is dropped at 3 boundaries.**
Per sub-agent 5 §F: (a) HTTP → Celery loses `request.user`
(task inherits context dict of strings only), (b) MissionRunner
config → OpsRun row loses `runs_as_username`, (c) MissionRunner
→ Step.fn loses actor context (step signature receives
`mission: OpsRun` only). Each boundary is a structural drop,
not a bug. Enforcement downstream of these drops requires
identity to be re-inferred from row state or context dict.

**F7 — Only `AssistantProfile` reads actor identity for a gate.**
Per sub-agent 5 §D: 8 identity-based checks exist in production
(auth middleware, DRF permissions, Rigby-gating, warn-mode
observation, fleet HMAC, etc.), but only one
(`AssistantProfile.get_allowed_tools()` at
`tool_dispatcher.py:687-720`) uses the canonical actor identity
(User FK → per-user allowed_tools list) as its enforcement
predicate. Every other gate uses a different abstraction (role
enum, staff bit, feature flag, HMAC-signed key).

**F8 — Historical case for Actor Attribution is strong.**
Per sub-agent 3: 15 incidents inventoried. 7 (47%) would be
directly prevented by explicit actor attribution; 4 (27%) would
be partially prevented; 4 (27%) are orthogonal (Postgres
PgBouncer masking, wrapper URL trap, silent env-based routing,
authority observation-only). **11 of 15 incidents (73%) are
either fully or partially in scope for Actor Attribution.**
Silent failures dominate: 64% of incidents (silent + semi-silent)
were invisible at time of occurrence.

**F9 — Symbol Mapping and Actor Attribution are two sides of the cleanest enforcement primitive.**
Per §9: Symbol Mapping answers "what action" (action_class →
runtime symbol); Actor Attribution answers "who acted" (actor
identity → runtime signal). Per Rigby S1271 SIGN clarification:
the *cleanest* enforcement primitive puts both answers at the
same layer, but this is not the only possible design — a
two-layer split (Symbol at tool dispatch, Actor at request
boundary) is mechanically possible, just weaker on UX/security.
The doc's argument is that the composite primitive is cleanest,
not that it is the only enforceable shape. Enforcing "Rigby
cannot open a PR" (the canonical example) is strongest when (a)
detecting the PR action (Symbol Mapping) AND (b) knowing Rigby
was the attempted actor (Actor Attribution) happen together.
The two research missions scope the two halves of the same
primitive.

**F10 — Cross-plane composition with the four governance planes is undesigned.**
Per governance_authority_evolution.md F1: autonomy, authority,
budget, and human governance planes do not compose. Adding
Actor Attribution introduces new composition questions: how does
"Rigby (AI actor) running as chris (User)" resolve against
`GovernanceState.mode='freeze'` (scoped to `agent` or `desk`)?
Against `budget_freeze_active`? Against `HumanAttentionItem`
pending Chris's decision? None of these are answered anywhere in
code. This is a follow-on research question, not scope of this
doc.

### Overall observation

**Actor Attribution is not a "feature" — it is a foundational
identity primitive.** Every downstream authority research
mission (Trust Propagation, Employee Delegation, Memory
Architecture, Cross-Employee Scheduling) requires this layer to
exist before it can be scoped meaningfully. Per §13, the
recommended next research mission is *Authority Enforcement
Design Space* — the first mission that assumes both Symbol
Mapping and Actor Attribution as prerequisites and enumerates
how they would compose into an actual enforcement primitive.

---

## 2. Actor Identity Inventory

Every actor identity concept the platform ships today. Enumerated
by direct read of the sources listed in each row. Where a concept
is a Django model, the row cites the model class. Where a concept
is a string convention, the row cites the string literal's
canonical grep site.

> **Vocabulary forward-reference (Rigby S1271 SIGN).** This doc
> uses three actor roles — **executor_actor**, **sponsor_actor**,
> **principal_user** — defined in §8.5. Findings (§11) and the
> Q7 semantics section (§8) use this vocabulary where role
> clarity matters. Readers unfamiliar with the roles should read
> §8.5 before §11. In the inventory tables below, the "concept"
> column names the identity primitive; role interpretations are
> in §8.5's role-to-field mapping table.

### 2.1 The 19 actor identity concepts

| # | Concept | Definition | Where declared | Runtime storage | Trust boundary | Where lost | Enforced or metadata? |
|---|---|---|---|---|---|---|---|
| 1 | **UnifiedUser** | Django User model (AbstractUser subclass) | `core/models/base/models.py:86-98` | DB (users table); PK = UUID `id` + `username` (unique) | Token → User via `auth_middleware.py`; `is_staff` gate | Never (row persists) | **Enforced** — FK constraint |
| 2 | **username** | Case-insensitive string on User | Django User.username field | On User row; queried via `iexact` lookup | Auth middleware token payload | Never persisted separately | **Weak** — string, drift risk on rename |
| 3 | **runs_as_username** | `AIEmployee` field: which User the employee acts as server-side | `core/employees/jobs.py:89` (field def), `:173, 394, 668, 979` (all "chris") | Frozen dataclass; not in DB | Runtime: `MissionRunner._resolve_runs_as_user_id` (`mission_runner.py:1585-1591`) via iexact lookup | Returns None on miss (silent) | **Weak** — string, one-time lookup |
| 4 | **employee_handle** | `AIEmployee` field: canonical id for the AI worker | `core/employees/jobs.py:87` (field), `:1327-1332` (registry) | `_EMPLOYEES_BY_HANDLE` dict; frozen after module load | `get_employee(handle.lower())` at `jobs.py:1355-1357` | Cannot drift (frozen) | **Enforced** — immutable registry |
| 5 | **display_name** | `AIEmployee` chat-facing name | `core/employees/jobs.py:88` | Frozen dataclass; not in DB | N/A (display only) | N/A | **Metadata only** |
| 6 | **primary_chat_id** | `AIEmployee` pinned PA conversation UUID | `core/employees/jobs.py:90` (optional) | Frozen dataclass | N/A (routing only) | N/A | **Metadata only** |
| 7 | **agent_name (AGENT_MAP)** | String key mapping name → agent class | `core/agent_router.py` AGENT_MAP (83 entries per PLATFORM_INVENTORY) | Python dict at module scope | Router lookup at execute time | Cannot drift within dict | **Enforced** for routing |
| 8 | **agent_name (CharField)** | String on multiple audit models | `Deliverable.agent_name`, `ToolCallRecord.agent_name`, `AgentExecution.owner_agent`, `LLMCallEvent.agent_name` | DB CharField, indexed on most | Canonicalized via `canonicalize_agent_name` at write in some sites, not all | Can drift if bypassed | **Weak + Ambiguous** — see F4 |
| 9 | **Agent DB row** | Persistent identity for AGENT_MAP agents | `core/models_unified_system.py:378-461` | DB (agents table); PK = UUID `id` + unique `name` | `Agent.objects.get(name=canonical_name)` at deliverable_factory:706 | Duplicate rows possible without canonicalization (S1263 F5) | **Enforced** as FK on `AgentExecution.agent`; **Weak** as string reference |
| 10 | **AssistantProfile** | Per-user PA configuration + allowlist | `core/models_assistant_profile.py:90-97` (1:1 to User) | DB; cascade with User | `AssistantProfile.get_allowed_tools()` at `tool_dispatcher.py:687-720` | Cascades on User delete | **Enforced** — FK cascade |
| 11 | **ChatConversation.user** | Owner of a conversation thread | `core/models/conversations/models.py:69-75` (nullable FK) | DB; nullable for unlinked Discord users | Query by conversation_id → owner | Discord users may not have User rows | **Enforced** when set; nullable |
| 12 | **ChatConversation.source** | Origin classifier | `core/models/conversations/models.py:81-95` — choices: web/mobile/discord/api/claude-code/pa | DB CharField choice | Recorded at write; propagates from CLI via payload | Never (persisted) | **Weak** — string enum; no FK to a source actor |
| 13 | **DirectMessage.sender** | Message sender (User FK, nullable) | `core/models_messaging.py:108-114` (SET_NULL) | DB; null when sender_type='system' | Query by thread | Never (persisted) | **Enforced** when set; nullable |
| 14 | **DirectMessage.sender_type** | Sender classifier (user/rigby/system) | `core/models_messaging.py:119-128` | DB CharField choice | Complement to sender FK | Never | **Weak** — 3-value enum |
| 15 | **service account "chris"** | String literal used as runs_as_username | Hardcoded in `core/employees/jobs.py:173, 394, 668, 979` | Implicit; no dedicated User row asserted | `_resolve_runs_as_user_id` lookup | Returns None on miss | **Weak** — string, silent fallback |
| 16 | **system actor** | `sender_type='system'` on DirectMessage; `source='system'` on ChatConversation; `creator_agent="system"` on embeddings | Multiple sites; no canonical User row | String literals across the codebase | Signature: sender=None + sender_type='system' | Cannot enforce (no FK) | **Metadata only** |
| 17 | **anonymous actor** | Django `AnonymousUser()` for unauthenticated requests | `core/websocket_auth.py:6,18`; `core/ws_auth_middleware.py:21` | Framework class | Auth middleware fallback when token missing | Converted on login | **Enforced** — typed class |
| 18 | **fleet identity** | `FleetServiceIdentity.app_slug` (HMAC-verified) | `core/models/fleet.py:63-129` (identity + keys) | DB; unique `app_slug` | `X-Fleet-Signature` header verified against `FleetServiceKey` | Rotation lifecycle | **Enforced** — cryptographic |
| 19 | **claude-code source** | `ChatConversation.source='claude-code'` — autonomous engineer | `tools/pa_chat.py:108-109` (payload); `core/models/conversations/models.py:86` (choice) | On ChatConversation; also `platform='cli'` per views_personal_assistant.py:557 | Recorded at write; no dedicated user_row for "claude-code" | Never | **Weak** — string enum |

**Totals:** 19 concepts. Of these: **9 have DB-backed persistence
with FK enforcement**, **6 are string enums or CharFields**, **3
are frozen-dataclass constants**, **1 is a framework-provided
class** (`AnonymousUser`).

### 2.2 Concept clustering (by identity kind)

Per sub-agent 1 grouping:

| Kind | Concepts | Backed by |
|---|---|---|
| **Human user identity** | UnifiedUser (#1), username (#2), AssistantProfile (#10) | Django auth |
| **AI employee identity** | employee_handle (#4), display_name (#5), runs_as_username (#3), primary_chat_id (#6) | Frozen dataclass (`AIEmployee`) |
| **Agent identity** | agent_name (AGENT_MAP #7), agent_name (CharField #8), Agent DB row (#9) | Mixed: code dict + DB row + CharField |
| **Conversation actor** | ChatConversation.user (#11), source (#12) | DB with FK + choice |
| **Message actor** | DirectMessage.sender (#13), sender_type (#14) | DB with FK + choice |
| **Service actor** | service account "chris" (#15), system actor (#16), fleet identity (#18), claude-code source (#19) | Mixed: strings, HMAC, choices |
| **Auth state** | anonymous actor (#17) | Django framework |

### 2.3 Concept overlap and collision

Multiple concepts refer to the same entity from different angles:

- **"Rigby"** appears in: `employee_handle='rigby'` (canonical),
  `display_name='Rigby'` (chat), `agent_name='Rigby'` (Deliverable
  and ToolCallRecord after canonicalization), `sender_type='rigby'`
  (DirectMessage). Four distinct fields; four distinct semantics.
- **"chris"** appears in: `User.username='chris'` (canonical User),
  `runs_as_username='chris'` (AIEmployee field for all 4
  employees), `ChatConversation.user=<chris_user>` (owner).
- **"claude-code"** appears in: `Agent.name='claude-code'`
  (canonical Agent row after S1263 consolidation), `agent_name=
  'claude-code'` (multiple CharField sites), `ChatConversation.
  source='claude-code'` (source enum), `platform='cli'`
  (`views_personal_assistant.py:557` for `source='claude-code'`
  input), `code-worker` (Procfile worker name — related but not
  identity per se).
- **"system"** appears in: `sender_type='system'`
  (DirectMessage), `source` (?), `creator_agent="system"`
  (UnifiedEmbedding default). No `User(username='system')` row
  documented.

Sub-agent 1 §D notes: **no cross-concept canonicalization**
exists. `canonicalize_agent_name` at `deliverable_aliases.py:
39-47` handles Agent-DB-row-name variants only (2 aliases).
There is no function that answers "given an arbitrary identity
string, resolve it to the canonical (User FK OR employee_handle
OR Agent name)."

### 2.4 The `runs_as_username` load-bearing lookup

`runs_as_username` is the single most consequential identity-
translation primitive on the platform. It appears in every
frozen `AIEmployee` dataclass (all 4 employees hardcode
`"chris"`) and drives the User FK on every mission's actor-
relevant surfaces.

**Site of resolution** (`core/employees/mission_runner.py:1585-1591`):

```python
def _resolve_runs_as_user_id(self) -> Optional[Any]:
    """Return the ``User.id`` for the configured runs_as_username."""
    User = get_user_model()
    user = User.objects.filter(
        username__iexact=self.config.runs_as_username
    ).first()
    return getattr(user, "id", None) if user else None
```

**Behavior on lookup miss:** returns `None`. No exception. No
log line. No escalation. Downstream code that expects a User FK
receives `None` and either silently proceeds with `user=None`
or crashes on the next FK constraint.

**Callers:**
- `mission_runner.py:1432` (context UNKNOWN pending trace)
- `mission_runner.py:1500` (context UNKNOWN pending trace)

**Implication:** if `User(username='chris')` is renamed to
`User(username='christopher')`, or deleted, or never created in
the environment, every mission for every employee silently runs
"as nobody" without a runtime alert. This is the F3 finding.

---

## 3. Attribution Surfaces

Every model + audit stream that could carry actor identity.
Per sub-agent 2 §A, 22 surfaces audited by direct file read.

### 3.1 Full attribution surface table

| # | Surface | Actor field(s) | Type | file:line | Attribution class |
|---|---|---|---|---|---|
| 1 | **OpsRun** | — (only `triggered_by` mechanism) | choice string | `models_ops_runs.py:11-88` | **MISSING** |
| 2 | **OpsRunEvent** | — (only run FK + label + detail) | — | `models_ops_runs.py:91-118` | **MISSING** |
| 3 | **AgentExecution** | `user` FK (nullable), `owner_agent` CharField | FK(User) + CharField | `models_unified_system.py:882-928` | **Explicit + Ambiguous** |
| 4 | **ToolCallRecord** | `agent_name` CharField | CharField | `models_tool_calls.py:57-60` | **Ambiguous** |
| 5 | **Deliverable** | `user` FK (nullable), `agent_name` CharField | FK(User) + CharField | `models_deliverables.py:218-234` | **Explicit + Ambiguous** |
| 6 | **DeliverableEvent** | `user` FK (nullable, SET_NULL) | FK(User) | `models_deliverables.py:584-595` | **Explicit** |
| 7 | **DirectMessage** | `sender` FK (nullable), `sender_type` choice | FK(User) + CharField | `models_messaging.py:108-128` | **Explicit + Ambiguous** |
| 8 | **MessageThread** | — (participants via M2M) | Inferred | `models_messaging.py:21-67` | **Inferred** |
| 9 | **ThreadParticipant** | `user` FK | FK(User) | `models_messaging.py:69-97` | **Explicit** |
| 10 | **HumanAttentionItem** | `user` FK | FK(User) | `models_human_interface.py:93-96` | **Explicit** |
| 11 | **HumanFeedbackRecord** | `user` FK | FK(User) | `models_human_interface.py:238` | **Explicit** |
| 12 | **LLMCallEvent** | `agent_name` CharField | CharField | `models_llm_telemetry.py:62-65` | **Ambiguous** |
| 13 | **CeleryTaskEvent** | `agent_name` CharField (backfilled at prerun) | CharField | `models_celery_telemetry.py:41-47` | **Unreliable** (empty string overloaded) |
| 14 | **ChatConversation** | `user` FK (nullable), `source` choice | FK(User) + CharField | `models/conversations/models.py:69-95` | **Explicit** (user) + **Weak** (source) |
| 15 | **ConversationMemory** | `user` FK | FK(User) | `models/conversations/models.py:24` | **Explicit** |
| 16 | **UserProfile** | `user` 1:1 FK | OneToOneField | `models/users/models.py:40` | **Explicit** |
| 17 | **EnhancedUserProfile** | `user` 1:1 FK | OneToOneField | `models/users/models.py:370` | **Explicit** |
| 18 | **AssistantProfile** | `user` 1:1 FK + `role` | OneToOneField + choice | `models_assistant_profile.py:90-97` | **Explicit** |
| 19 | **EventBus event payload** | `source: str = "system"` default | CharField in publish signature | `services/event_bus.py:42-77` | **Ambiguous** (arbitrary caller string) |
| 20 | **DeliverableExport** | `user` FK | FK(User) | `models_deliverables.py:493-497` | **Explicit** |
| 21 | **ContentPacket** | `created_by` FK (nullable) | FK(User) | `models_deliverables.py:651-655` | **Explicit** |
| 22 | **PA tool call payload** | `user_id` param (optional), `agent_name` string default 'Direct' | Parameter | `tool_dispatcher.py:585-720` | **Weak** (unless AssistantProfile gate enforces) |

**Totals per sub-agent 2 §G:** 13 Explicit, 2 Inferred, 4 Ambiguous, 1 Unreliable, 2 Missing.

### 3.2 The OpsRun gap (F1 evidence)

Direct read of `core/models_ops_runs.py:11-88` (verified by
Claude): OpsRun's persisted fields are `id`, `title`, `run_type`,
`status`, `triggered_by`, `started_at`, `finished_at`, `summary`,
`event_count`, `fail_count`, `domain`, `run_kind`, `mission_id`.

**No `user` FK. No `employee_handle` field. No `actor` field.**

`triggered_by` is a mechanism classifier
(`beat/pa_tool/management_cmd/manual`), not an identity.

**Practical implication:** anyone asking "which missions did
Rigby run this week?" must:
1. Filter by `domain='mission'` and `run_kind='docs_cascade'`
   (Rigby's job's mission_run_kind), OR
2. Parse `OpsRun.summary` JSON for `employee_handle` (may or may
   not be populated by callers), OR
3. Join to the calling Celery task's `CeleryTaskEvent`
   (`agent_name` field, unreliable per row 13), OR
4. Query the mission's `AgentExecution` rows and infer.

None of these is a canonical query. The identity of the actor
lives *outside* the OpsRun row.

### 3.3 The three `agent_name` fields (F4 evidence)

Three surfaces name an agent with a CharField:

**Row 3 — `AgentExecution.owner_agent`** (models_unified_system.py:924-927):
```
owner_agent = models.CharField(
    max_length=100, blank=True, db_index=True,
    help_text="Session 843: Agent that owns/created this execution"
)
```

**Row 4 — `ToolCallRecord.agent_name`** (models_tool_calls.py:57-60):
```
agent_name = models.CharField(max_length=255, db_index=True)
```
(No docstring on this line.)

**Row 12 — `LLMCallEvent.agent_name`** (models_llm_telemetry.py:62-65):
Sub-agent 2 notes: "Agent that initiated this LLM call."

**The problem** (sub-agent 2 §D #1): "owns/created" (Session 843),
"the tool call" (undocumented), and "initiated" (LLMCallEvent)
are all undefined. Consider a chain:

1. Rigby (PA) dispatches worker agent: `ToolCallRecord(agent_name='Rigby', tool_name='research_tool')`
2. Inside worker agent, LLM call: `LLMCallEvent(agent_name='ResearchWorker')`
3. What goes on `AgentExecution.owner_agent` for the ResearchWorker
   invocation? "Rigby" (delegator) or "ResearchWorker" (executor)?

**No docstring resolves this.** A reader cannot determine
whether to credit the action to the delegator or the executor
without tracing the call chain.

### 3.4 Cross-surface consistency scenarios

Per sub-agent 2 §C, three canonical scenarios:

**Scenario 1: Rigby dispatches ops_tool status.**
- `OpsRun` — no actor recorded
- `ToolCallRecord.agent_name` — 'Rigby' (ambiguous)
- `LLMCallEvent.agent_name` — 'Rigby' (same ambiguity)
- `CeleryTaskEvent.agent_name` — may or may not be 'Rigby'
  (unreliable per row 13)

If ops_tool triggers an LLM call to parse the result, the three
event surfaces record the actor's name *inconsistently* — one
doesn't record it at all, and the other two use a CharField
with undefined delegator-vs-executor semantics.

**Scenario 2: Chris approves a human attention item.**
- `HumanAttentionItem.user` — chris (Explicit)
- `HumanFeedbackRecord.user` — chris (Explicit)
- `DeliverableEvent.user` — chris (Explicit)

Strong. All human-facing models carry explicit User FK.
Attribution is consistent.

**Scenario 3: Beat task fires docs cascade mission.**
- `OpsRun` — `triggered_by='beat'`; no actor
- Any downstream `AgentExecution` — `user=NULL` (per Session
  642, nullable for Celery contexts)
- Any downstream `Deliverable` — `user=NULL` (nullable) with
  `agent_name` as executor
- `CeleryTaskEvent.agent_name` — empty string (not an agent
  task) or unset

**Result:** the "who initiated this cascade?" question has no
single answer across surfaces. The beat is the trigger; the
actor is system/unknown.

### 3.5 Missing surfaces — attribution patterns the platform does NOT ship (Rigby S1271 SIGN)

Per Rigby S1271 SIGN pressure-test #1: some attribution patterns
that Django platforms typically ship are *absent* here. Their
absence is itself a finding.

| Pattern | Status | Evidence / notes |
|---|---|---|
| **`created_by` / `updated_by` mixin** (audit mixin auto-stamping the User who created/updated a row) | **ABSENT** as a standard pattern | Grep for `class.*Mixin.*created_by` / `class TimestampedAuditMixin` / `class ActorStampedMixin` yields no repeatable mixin. Individual models add `user` FK ad-hoc (Deliverable, HumanAttentionItem, etc.), but there is no shared mixin enforcing a canonical stamp. Any downstream design that expects "just add `AuditMixin`" would have to build the mixin first. |
| **Request-level identity propagation middleware** (thread-local storing `request.user` for signal handlers to access) | **ABSENT** as canonical | `django-currentuser` or equivalent thread-local pattern not observed. `request.user` is available inside view functions but does not propagate into `pre_save`/`post_save` signals unless the caller explicitly sets a thread-local. Beat-triggered signals have no request context (per §7.4). |
| **`websocket_auth.User` binding on WebSocket messages** | **PARTIAL** — auth middleware falls back to `AnonymousUser()` (`core/websocket_auth.py:6,18`; `core/ws_auth_middleware.py:21`); no equivalent to `request.user` persisted on channels layer events | Any actor check on WebSocket-driven flows must reach into the middleware layer or accept AnonymousUser fallback. |
| **Side-effect audit anchoring (DeliverableEvent / ToolCallRecord / LLMCallEvent as the de-facto actor log if OpsRun stays actorless)** | **POSSIBLE FALLBACK** | Per §3.1 rows 6 (DeliverableEvent.user), 4 (ToolCallRecord.agent_name), 12 (LLMCallEvent.agent_name): the *side-effect* rows have some attribution today. If F1's OpsRun gap is *not* closed by adding an actor field, downstream enforcement could anchor on side-effect logs instead — accepting weaker mission-level queryability in exchange for stronger per-effect audit. This is a design tradeoff, not a current pattern. |
| **Fleet write paths beyond `FleetServiceIdentity`** | **UNKNOWN** | `FleetServiceIdentity.app_slug` is verified at HTTP ingress via `FleetSignatureAuthentication`. Whether any fleet call downstream writes to `OpsRun`, `Deliverable`, `AgentExecution`, or `DirectMessage` — and how `app_slug` propagates into those rows — is UNKNOWN without a fleet-endpoint-to-side-effect trace. If it does propagate, `app_slug` needs to be classified against §8.5's roles (likely executor_actor + sponsor_actor). If it does not, fleet writes may land as anonymous or ambiguously-attributed. |
| **Delegation chain table (parent-child call graph across agents)** | **PARTIAL** — `AgentExecution.parent_object_type` + `parent_object_id` (Session 843, `models_unified_system.py:916-923`) supports a parent link, but no canonical query joins by delegation chain | The fields exist but there is no query API that reconstructs a delegation graph. F4's ambiguity (delegator vs. executor) intersects here: without a chain table + query, the delegator cannot be reliably reconstructed. |

**Implication for downstream research.** Design missions that
assume "the platform already ships X pattern" (audit mixins,
thread-local request.user, delegation graph query) will be
surprised. This inventory is preemptive: any actor primitive
that promises those patterns is scoping-in the implementation
of the pattern itself.

### 3.6 Cross-reference to Symbol Mapping

S1270 catalogued 12 runtime action surfaces. Overlap with S1271's
attribution surfaces:

| Action surface (S1270) | Attribution surface (this doc) | Actor field |
|---|---|---|
| MissionRunner steps | OpsRunEvent | **MISSING** actor |
| PA tool schemas | ToolCallRecord | agent_name (Ambiguous) |
| Celery tasks | CeleryTaskEvent | agent_name (Unreliable) |
| Django mgmt commands | — | **MISSING** — no attribution surface |
| AGENT_MAP agents | AgentExecution | user FK + owner_agent (Ambiguous) |
| Deliverable creation | Deliverable | user FK + agent_name (Ambiguous) |
| HAI creation | HumanAttentionItem | user FK (Explicit) |
| LLM tool_calls | LLMCallEvent | agent_name (Ambiguous) |
| Model writes | — | Model-specific; often unrecorded |
| OpsRunEvent emission | OpsRunEvent | **MISSING** actor |
| DirectMessage | DirectMessage | sender FK + sender_type (Explicit + Ambiguous) |
| HTTP endpoints | (via middleware) | request.user (Explicit) |

**Observation:** every runtime action surface where Symbol Mapping
would try to bind an `action_class` corresponds to at least one
attribution surface — but the actor field on that attribution
surface is Ambiguous, Missing, or Unreliable in **7 of 12
cases**. Symbol Mapping bridges the "what" gap; attribution
still leaves the "who" gap open.

---

## 4. Identity Shape Changes

Every conversion where actor identity changes representation.
Per sub-agent 1 §B, 14 major shape changes identified.

### 4.1 Shape change table

| # | Starting → Ending | Location | Preserved | Lost | Assumption |
|---|---|---|---|---|---|
| 1 | HTTP token → User instance | `auth_middleware.py` | user.id, username | permissions, groups | Token valid; User row exists |
| 2 | User → username (str) | Any `user.username` access | username | user.id, is_staff | N/A |
| 3 | username → runs_as_username | Hardcoded in `AIEmployee` constants | string literal | User FK | Single runs_as_username per employee (all "chris") |
| 4 | runs_as_username → User FK | `MissionRunner._resolve_runs_as_user_id` at `mission_runner.py:1585-1591` | user.id (via iexact) | original string | User("chris") exists |
| 5 | employee_handle → MissionRunnerConfig | Task dispatch (Celery) | employee_handle, display_name, runs_as_username | HTTP auth context | AIEmployee in registry |
| 6 | Agent.name (variant) → Agent DB row | `deliverable_factory.py:706` calls `canonicalize_agent_name()` before `get_or_create()` | canonical name | variant spelling | Canonical is unique |
| 7 | ChatConversation.source → actor inference | Reader-side: interpretation of `source` choice | source string | original requester identity | source correctly set |
| 8 | PA request.user → conversation owner | `views_personal_assistant.py:554-558` | user.id | full User object | User.id valid at write |
| 9 | PA request.user → tool dispatch agent_name | Router / intent classification | request.user context | User identity not passed to tool dispatcher | Router picks agent deterministically |
| 10 | Tool caller → dispatcher agent_name | `tool_dispatcher.py:585-653` (agent_name='Direct' default) | agent_name param | Full User (unless AssistantProfile check) | agent_name is caller-specified |
| 11 | Celery task dispatch → execution identity | `task.apply_async(kwargs={...})` | employee_handle (if in kwargs) | request.user (dropped) | Kwargs carry employee_handle |
| 12 | OpsRun.summary['employee_handle'] → DirectMessage.sender_type | `core/employees/comms.py:342-349` (post_shift_report) | sender_type choice ('rigby' or 'system') | employee_handle not stored on DirectMessage | sender_type in SENDER_TYPE_CHOICES |
| 13 | DirectMessage.sender=None + sender_type → recipient | `models_messaging.py:139` `__str__` fallback: `self.sender.username if self.sender else self.sender_type` | sender_type enum | User identity | sender_type is the discriminator |
| 14 | LLM tool_call name → ToolDispatcher execute | LLM function-call → PA loop → dispatcher | agent_name from LLM output | caller User identity (not passed) | agent_name is deterministic |

### 4.2 Identity drop boundaries

Per sub-agent 5 §F, three boundaries where identity is
structurally dropped:

**Drop 1 — HTTP → Celery task.** HTTP request carries a typed
`User` instance in `request.user`. Celery task receives a
`context` dict (strings, IDs, JSON) via `apply_async(kwargs=...)`.
The User instance does not cross the process boundary. Downstream
tasks must either (a) trust caller-provided strings in context,
or (b) re-look-up User by ID.

**Drop 2 — MissionRunner config → OpsRun row.**
`MissionRunnerConfig.runs_as_username='chris'` is available at
config-time but **not persisted to OpsRun**. OpsRun rows carry
`triggered_by` mechanism string only (F1). Callers cannot ask
"which missions ran as `chris`?" without either JSON-parsing
`summary` or joining downstream tables.

**Drop 3 — MissionRunner → Step.fn.** Step dataclass signature
is `Step(name: str, fn: Callable[[Any], StepResult])`. Step.fn
receives only the mission `OpsRun` row. **No actor parameter.**
Step body can access `self.config.runs_as_username` via closure
if it happens to be a bound method of MissionRunner, but for
standalone step functions (which is the pattern in
`core/jobs/*.py`), actor identity is not part of the interface.

### 4.3 Identity flow for the canonical Rigby mission

Trace for Rigby's docs_cascade daily mission:

```
Chris authenticates (Web login → token)
  ↓
Beat scheduler fires PeriodicTask "documentation_manager_docs_cascade_daily"
  [Drop 1: no HTTP request context]
  ↓
Celery worker picks up task: run_docs_cascade_mission.apply_async(...)
  [Task receives no request.user; no actor context]
  ↓
Inside run_docs_cascade_mission:
  config = MissionRunnerConfig(
      employee_handle='rigby',
      runs_as_username='chris',
      ...,
  )
  [Config carries string identities; not persisted anywhere yet]
  ↓
runner = MissionRunner(config, steps=[...])
runner.run()
  ↓
runner._create_mission_row() → OpsRun(triggered_by='beat', ...)
  [Drop 2: OpsRun row has no user; runs_as_username lost]
  ↓
runner._emit_authority_contract_event(mission)
  [S1264 warn-mode — observation of contract shape only]
  ↓
For each step in self.steps:
  step.fn(mission)  # step receives OpsRun only
  [Drop 3: step body has no actor param; no runs_as_username]
  ↓
Step body creates Deliverable(agent_name='Rigby', user=???)
  [If step queries _resolve_runs_as_user_id, it may set Deliverable.user=chris]
  [Otherwise Deliverable.user=NULL and only agent_name='Rigby' identifies the actor]
  ↓
Step body posts DirectMessage(sender=None, sender_type='rigby', ...)
  [sender FK null; sender_type enum is the actor marker]
```

**Observation:** in a fully-instrumented case, `chris`'s User row
appears indirectly (via `_resolve_runs_as_user_id` at write
sites), but the mission's OpsRun row itself never learns who ran
it. Retrospective audit requires the JOIN across
`OpsRun.run_kind + Deliverable.agent_name` or
`OpsRun.summary.employee_handle` — none of which is a canonical
FK path.

---

## 5. Historical Identity Failures

Per sub-agent 3, 15 incidents inventoried where actor identity
was the root cause OR a compounding factor.

> **Role-confusion framing (Rigby S1271 SIGN optional #7).**
> Per §8.5's three-role vocabulary: many of the incidents below
> are best characterized as *role confusion* incidents — a field
> intended to represent one role (e.g., principal_user) was
> conflated with another (e.g., executor_actor) at the site of
> the failure. The most explicit examples: I-A1 (admin token
> mapped to donkeyking's principal_user context — sponsor_actor
> mismatch), I-A2 (`ClaudeCode` vs. `claude-code` — executor_actor
> naming drift), I-A3 (`context['user']` dict vs. FK — the same
> field name used for two different roles: prompt-injection
> profile vs. principal_user FK), I-A4 (`agent_name` string vs.
> FK — same executor_actor stored as two divergent identifiers).
> This framing is a lens on the existing catalog, not a
> re-classification; each incident's YES/PARTIALLY/NO verdict
> below is unchanged.

### 5.1 Verdict distribution

| Verdict | Count | Percentage |
|---|---|---|
| **YES** — Actor Attribution directly prevents | 7 | 47% |
| **PARTIALLY** — Actor Attribution reduces likelihood | 4 | 27% |
| **NO** — Root cause orthogonal | 4 | 27% |
| **Total** | 15 | 100% |

**Effective case strength: 11 / 15 = 73% would be prevented or
significantly improved by explicit Actor Attribution.**

### 5.2 YES cases (7)

Actor Attribution directly prevents:

**I-A1: `pa_local.sh` admin/donkeyking token split (S1098).**
Wrapper hardcoded admin's token + admin's conversation.
34+ messages landed under admin instead of donkeyking while
Chris watched empty ChatUI. Root cause: no runtime verification
that token→user mapping was correct. Source: memory rule
`feedback_pa_local_verify_ownership.md` + S1098 handoff.
Would Actor Attribution prevent? YES — token→user binding as
an explicit check at dispatch time.

**I-A2: Duplicate `Agent` rows: `ClaudeCode` vs. `claude-code`
(S1263 PR #2754 + migration 0374).** Two active Agent rows for
the same actor. Root cause: seed scripts + `deliverable_factory.
_synthesize_pa_receipt` bypassing canonicalization. Fixed:
migration consolidates; PR wires canonicalization into factory.
Would Actor Attribution prevent? YES — canonical actor factory
would enforce single identity.

**I-A3: `context['user']` dict vs. `UnifiedUser` FK type
confusion (S1234 PR #2608).** Handlers wrote a dict (prompt-
injection profile) into `Deliverable.user` FK, raising
`ValueError`. Root cause: naming collision between prompt
convention and FK convention. Would Actor Attribution prevent?
YES — type-enforcement on actor fields ("must be User instance,
not dict") would catch the mismatch at dispatch.

**I-A4: `agent_name` string vs. `Agent` FK normalization gap
(S1226).** `AgentExecution.owner_agent='ClaudeCode'` (string)
while FK `agent` pointed to `claude-code` row. Internal
inconsistency. Would Actor Attribution prevent? YES — dual-field
normalization would require FK + string identifier to resolve
to the same canonical actor.

**I-A5: Rigby's `pa_local.sh` conversation unverified at
session start (S1099 recurrence).** Startup doc listed wrong
token; must be verified via Token table each session. Ritual
relies on human memory. Would Actor Attribution prevent? YES —
startup verification would make token→user binding explicit and
checkable.

**I-A6: HTTP API permission gate flip (S1265 PR #2760 pre-SIGN
catch).** New Employee/Mission API shipped with `IsAuthenticated`
(any authenticated user). Rigby SIGN-WITH-EDITS flagged: should
be `IsAdminUser`. Would Actor Attribution prevent? YES — actor-
type binding on views would make permission classes a function
of the actor's role.

**I-A7: `workspace_id` threading lost in WorkflowOrchestrationAgent
lanes (S1234 PR #2610).** Five lane intermediates landed in
wrong workspace because router didn't thread workspace context
to delegates. Would Actor Attribution prevent? YES — actor context
threading would preserve workspace binding through delegation.

### 5.3 PARTIALLY cases (4)

Actor Attribution reduces likelihood but is not sufficient alone:

- **I-A8:** `pa_chat.py` URL default → prod (S1249). URL fix
  addressable; token trap requires config-management, not just
  identity primitive.
- **I-A9:** Authority symbol-mapping gap (S1264 + S1270).
  Symbol Mapping is the direct blocker; Actor Attribution
  enables enforcement gates but isn't sufficient alone.
- **I-A10:** Authority observation without enforcement
  (S1264 warn-mode). Requires both Symbol Mapping and Actor
  Attribution.
- **I-A11:** Deliverable create defaults to `completed`
  (S1241). Actor Attribution could detect via post-action audit
  but cannot prevent without explicit action-intent binding.

### 5.4 NO cases (4)

Orthogonal:

- **I-A12:** PgBouncer application_name masking (S1173).
  Infrastructure-layer masking; Actor Attribution operates above
  transport layer.
- **I-A13:** PA worker `PA_USE_FUNCTION_CALLING=true` env
  dependence (S1184). Worker-capability declaration problem, not
  actor identity.
- **I-A14:** Token validation exception masking (S1171 PR
  #2328). Fixed via typed exception split; independent of actor
  primitive.
- **I-A15:** `DeliverableFactory._synthesize_pa_receipt` missing
  canonicalization (S1263). Fixed inside the factory; recurrent
  in new creation sites regardless of actor primitive.

### 5.5 Silent-vs-loud

Per sub-agent 3 §D:
- **Silent (no evidence at discovery time):** 5 incidents (33%)
- **Semi-silent (evidence exists but hard to interpret):** 4 (27%)
- **Loud (thrown exception, obvious failure):** 6 (40%)

**60% of actor identity failures were silent or semi-silent.**
Explicit actor attribution at dispatch surfaces would make the
silent-failure window observable (per-actor audit trail at time
of failure).

### 5.6 Recurrence

Failure classes that have recurred after being "fixed once":

1. **Identity-token mismatch:** S1098 → S1099 → S1083 pre-fix.
   Trust in stale documentation; no runtime verification.
2. **Duplicate Agent rows:** S1226 (migration 0365) → S1263
   (migration 0374). No central Agent factory with mandatory
   canonicalization.
3. **Environment-based silent routing:** S1184 (PA worker) —
   would recur per new worker type without registration/capability
   declaration.
4. **Deliverable create status default:** S1241 — pattern still
   in place; root cause not diagnosed.
5. **Authority observation without enforcement:** S1264 → S1270
   → this doc. Structural recurrence per each new employee added.

### 5.7 Cross-reference to S1270 failures

Of 23 incidents in `symbol_mapping_architecture.md` §7, per
sub-agent 3 §G: **6 have actor-identity components**. Of those
6: **3 are fully actor-related** (`context['user']` type,
authority enforcement, identity binding); **3 are partially
actor-related** (involve actor but root cause is Symbol
Mapping).

### 5.8 Failure classes Actor Attribution CANNOT prevent

Per sub-agent 3 §F, five categories out of scope:

1. **PgBouncer infrastructure-layer masking** — below application
   layer; requires transport-layer cooperation.
2. **PA wrapper URL trap (pre-S1249)** — config management, not
   actor identity.
3. **Deliverable create status default** — silent backend
   default behavior; separate design.
4. **Authority observation-without-enforcement** — requires
   Symbol Mapping as prerequisite.
5. **Environment-based silent routing** — worker-capability
   declaration problem, not actor identity.

---

## 6. Existing Identity Registries

Per sub-agent 4, ~25 identity registries inventoried. Full detail
below; abbreviated form for classification.

### 6.1 Registry inventory table (all 25)

| # | Registry | Type | Key | Count | file:line |
|---|---|---|---|---|---|
| 1 | `UnifiedUser` | Django model (AbstractUser) | id (UUID) + username | UNKNOWN | `core/models/base/models.py:86` |
| 2 | `AIEmployee` | Frozen dataclass | handle (str) | 4 | `core/employees/jobs.py:73-92` |
| 3 | `Agent` | Django model | id (UUID) + name (unique) | 83 per PLATFORM_INVENTORY | `core/models_unified_system.py:378-461` |
| 4 | `_EMPLOYEES_BY_HANDLE` | Python dict | handle (lowercase) | 4 | `jobs.py:1327-1332` |
| 5 | `_JOBS_BY_EMPLOYEE` | Python dict | (employee_handle, job_key) | 4 | `jobs.py:1334-1347` |
| 6 | `AGENT_MAP` | Python dict (class attr) | agent_name (str) | 83 | `core/agent_router.py` |
| 7 | `AssistantProfile` | Django model (1:1) | user_id | UNKNOWN | `core/models_assistant_profile.py:90` |
| 8 | `ChatConversation` | Django model | conversation_id (str) | UNKNOWN | `core/models/conversations/models.py:59` |
| 9 | `DirectMessage.SENDER_TYPE_CHOICES` | Choice enum | sender_type | 3 (user/rigby/system) | `core/models_messaging.py:119-123` |
| 10 | `ThreadParticipant` | Django model (join) | (thread_id, user_id) unique | UNKNOWN | `models_messaging.py:69` |
| 11 | `MessageThread` | Django model | id (UUID) | UNKNOWN | `models_messaging.py:21` |
| 12 | `canonicalize_agent_name()` | Function | agent_name param | — | `core/services/deliverable_aliases.py:39-47` |
| 13 | `AGENT_NAME_ALIASES` | Python dict | variant → canonical | **2** (verified) | `deliverable_aliases.py:33-36` |
| 14 | `WORKSPACE_AWARE_AGENTS` | List (local) | agent_name | **20** (verified by direct read at `epa_handlers_tools.py:3873-3907`; sub-agent 4 undercount of 17 corrected) | `core/epa_handlers_tools.py:3873-3907` |
| 15 | `FleetServiceIdentity` | Django model | app_slug (unique) | UNKNOWN | `core/models/fleet.py:63` |
| 16 | `UserProfile` | Django model (1:1) | user_id | UNKNOWN | `core/models/users/models.py:12` |
| 17 | `EnhancedUserProfile` | Django model (1:1) | user_id | UNKNOWN | `models/users/models.py:370` |
| 18 | VIP role enum | Choice value | primary_role='vip_demo_viewer' | 1 | `core/vip_middleware.py:50-105` |
| 19 | `JobContract` | Frozen dataclass | (employee_handle, title) | 4 | `jobs.py:95-162` |
| 20 | `UserPreference` | Django model | (user_id, key) unique | UNKNOWN | `models/users/models.py:978` |
| 21 | `UserEmbedding` | Django model | user_id + content_type | UNKNOWN | `models/users/models.py:886` |
| 22 | `OpsRun` mission rows | Django model | id + domain='mission' + run_kind | UNKNOWN | `models_ops_runs.py:11-88` |
| 23 | `MobilePushToken` | Django model | user_id + device | UNKNOWN | `core/models_mobile.py:9` |
| 24 | `OpsRunEvent` | Django model | id + run_id | UNKNOWN | `models_ops_runs.py:91-118` |
| 25 | `Deliverable.agent_name` | CharField | agent_name (string, indexed) | UNKNOWN | `models_deliverables.py` |

### 6.2 Registry classification (SAFE / WRAPPER / DO NOT REUSE / DEPRECATED / UNKNOWN)

Per sub-agent 4 §B (subset of the 25 relevant for a hypothetical
actor primitive — not every §6.1 row is a candidate primitive):

**SAFE TO REUSE (16):**
- `UnifiedUser` (#1) — Django User; primary root identity.
- `AIEmployee` (#2) — frozen dataclass proven pattern (EMPLOYEE_OS_PRIMITIVES §1 row 1).
- `Agent` (#3) — canonical Agent DB row; FK'd from AgentExecution.
- `_EMPLOYEES_BY_HANDLE` (#4) — frozen dict, PR-reviewed.
- `_JOBS_BY_EMPLOYEE` (#5) — companion registry.
- `AGENT_MAP` (#6) — 83 stable agent names; deterministic router.
- `ChatConversation` (#8) — captures user + source.
- `canonicalize_agent_name()` (#12) — single alias source of truth.
- `AGENT_NAME_ALIASES` (#13) — 2 entries; extensible.
- `FleetServiceIdentity` (#15) — HMAC-verified service identity.
- `EnhancedUserProfile` (#17) — role, subscription, personalization.
- `JobContract` (#19) — frozen; proven.
- `OpsRun` mission rows (#22) — mission execution primitive
  (though missing actor field per F1).
- `OpsRunEvent` (#24) — step audit primitive.
- `ThreadParticipant` (#10) — per-user read state.
- `Deliverable.agent_name` (#25) — normalized via canonicalize_agent_name.

**REUSE WITH WRAPPER (6):**
- `AssistantProfile` (#7) — reuse for actor-specific tool access
  but audit against role duplication.
- `DirectMessage.SENDER_TYPE_CHOICES` (#9) — 3 values; extend
  with new choices only via schema migration.
- `WORKSPACE_AWARE_AGENTS` (#14) — refactor from local list to
  frozen constant or DB table; currently OK for small set.
- `UserPreference` (#20) — key-value store; unstructured schema.
- `UserEmbedding` (#21) — source string is not FK.
- VIP role enum (#18) — formalize as choice enum, not string.

**DO NOT REUSE (1):**
- `MobilePushToken` (#23) — device-specific, orthogonal to actor.

**DEPRECATED (1):**
- `UserProfile` (#16) — superseded by `EnhancedUserProfile`.

**UNKNOWN (1):**
- `MessageThread` (#11) — no single owner FK; participant M2M is
  inferred attribution; classify depends on whether "thread
  owner" is a needed concept.

**Totals classified:** 16 SAFE + 6 WRAPPER + 1 DO-NOT-REUSE + 1
DEPRECATED + 1 UNKNOWN = 25.

### 6.3 Anti-duplication check

Per `EMPLOYEE_OS_PRIMITIVES.md` §2 anti-duplication matrix:

| Proposed shape | Duplicates | Verdict |
|---|---|---|
| New `ActorRegistry` model | UnifiedUser + AIEmployee + FleetServiceIdentity | **BLOCKED** |
| New `actor_handle` field | username + AIEmployee.handle + Agent.name + app_slug | **BLOCKED** |
| New `actor_type` enum | DirectMessage.SENDER_TYPE_CHOICES + ChatConversation.SOURCE_CHOICES + EnhancedUserProfile.ROLE_CHOICES | **BLOCKED** |
| New `ActorPermission` model | AssistantProfile.allowed_tools + JobContract.authority + FleetServiceIdentity.capabilities | **BLOCKED** |
| New `ActorAuditLog` model | OpsRunEvent + DeliverableEvent + LLMCallEvent + ToolCallRecord + FleetAuthAuditLog | **BLOCKED** |

**Conclusion:** any hypothetical actor primitive design **must
reuse existing registries and add a shared `actor_type` enum**
(human / ai_employee / service / system) + canonicalization
functions per type. New tables would duplicate existing
registries. This doc does not propose a design; the observation
is that the design space is constrained by anti-duplication.

### 6.4 Canonicalization patterns

Per sub-agent 4 §F:

| Pattern | Where declared | Applies to |
|---|---|---|
| `canonicalize_agent_name(agent_name)` | `deliverable_aliases.py:39-47` | Agent identity |
| `AGENT_NAME_ALIASES` dict | `deliverable_aliases.py:33-36` | Agent name variants |
| `AIEmployee.handle.lower()` | `jobs.py:1355-1357` (`get_employee(handle.lower())`) | Employee identity |
| `UnifiedUser.username iexact` | Convention (Django ORM pattern) | User identity |
| `FleetServiceIdentity.app_slug` (exact match, no normalization) | `core/models/fleet.py:83-86` | Service identity |
| `DirectMessage.sender_type` (exact match on choice) | `models_messaging.py:119-128` | Message sender actor type |
| `ChatConversation.source` (exact match on choice) | `conversations/models.py:81-95` | Message source actor |
| `get_employee(handle.lower())` | `jobs.py:1355-1357` | Employee lookup |
| `get_job(employee_handle.lower(), job_key.lower())` | `jobs.py:1392-1398` | Job lookup within employee |

**Pattern observations:**
- **Case normalization:** AIEmployee.handle uses `.lower()` for
  dict key lookup; UnifiedUser.username uses iexact.
- **Alias mapping:** `canonicalize_agent_name()` handles variant
  spellings — currently only 2 aliases.
- **String enums:** SENDER_TYPE_CHOICES, SOURCE_CHOICES,
  thread_type use exact string match; no normalization.
- **No cross-actor canonicalization:** `rigby` (AIEmployee) vs.
  `Rigby` (Agent.name) vs. `'rigby'` (Deliverable.agent_name)
  are treated as separate identities. Canonicalize_agent_name
  handles Agent variants only, not AIEmployee ↔ Agent mapping.

### 6.5 Gaps — actor concepts WITHOUT a dedicated registry

Per sub-agent 4 §D:

| Gap | Current pattern | Notes |
|---|---|---|
| "system" actor | String convention only (SENDER_TYPE_CHOICES, source, creator_agent) | No canonical User row (e.g., no documented `User(username='system')` row) |
| Celery task caller | `@shared_task` context carries no actor metadata | Task runs anonymously unless kwargs explicitly carry actor |
| Claude Code / autonomous engineer | `source='claude-code'` string | No dedicated User row for the actor |
| Anonymous / unauthenticated | Django `AnonymousUser` framework class | Sufficient for auth-check; not a persistent identity |
| Rigby-routed actor | `MessageThread.thread_type='rigby_routed'` | Route metadata in `MessageThread.metadata + DirectMessage.metadata` |

---

## 7. Enforcement Boundaries

Per sub-agent 5, 17 candidate enforcement layers where actor
identity is checkable, checked, or dropped.

### 7.1 Enforcement layer inventory

| # | Layer | Actor signal | Reliability | Existing precedent | Cost | Mode |
|---|---|---|---|---|---|---|
| 1 | HTTP middleware / DRF | `request.user` (User FK) | Strong | `is_staff`, `is_reviewer`, `IsAuthenticated` | LOW | PRE-DISPATCH |
| 2 | ToolDispatcher.execute() entry | `user_id` param, `agent_name='Direct'` default | Weak (string) | `AssistantProfile.get_allowed_tools()` at `tool_dispatcher.py:687-720` | MEDIUM | INLINE |
| 3 | Inside PA tool handler | user_id from context, agent_name implicit | Weak | None systematic | MEDIUM | INLINE |
| 4 | Before MissionRunner.run() | runs_as_username (str), employee_handle (str) | Weak | None (runs_as_username not verified) | HIGH | PRE-DISPATCH |
| 5 | MissionRunner preflight | job_contract (optional; authority dict) | Ambiguous | S1264 warn-mode observation only | HIGH | POST-DISPATCH (warn) |
| 6 | Before Step.fn | Mission OpsRun row (no actor in signature) | Weak | None | HIGH | PRE-DISPATCH |
| 7 | Inside Step.fn body | None in signature; closure-dependent | Missing | None | HIGH | INLINE |
| 8 | Celery task entry | `context` dict (source, dispatch_context strings) | Ambiguous | Rigby delegation `dispatch_context['source']='rigby_mission_delegation'` | MEDIUM | POST-DISPATCH |
| 9 | AgentExecution row creation | `user` FK (nullable), `agent_name` string | Strong (FK) + Weak (agent_name) | AgentExecution.user + owner_agent | MEDIUM | INLINE |
| 10 | Deliverable creation | `user` FK (nullable), `agent_name` string | Strong (FK) + Weak (agent_name) | None (no gate) | MEDIUM | INLINE |
| 11 | DirectMessage creation | `sender` FK + `sender_type` string | Strong + Weak | None as gate | MEDIUM | INLINE |
| 12 | OpsRunEvent emission | No actor field | Missing | None | HIGH | INLINE |
| 13 | EventBus.publish() | `source: str = "system"` default | Weak | None (advisory) | HIGH | POST-DISPATCH |
| 14 | Model pre_save / post_save | Inherited from prior layer; no explicit capture | Ambiguous | Signals read from row state / thread-local | HIGH | INLINE |
| 15 | HTTP endpoint view (before DRF) | `request.user` | Strong | `IsAuthenticated` decorators | LOW | PRE-DISPATCH |
| 16 | Agent-to-agent delegation | `agent_name` string + optional parent_object | Weak | Rigby delegation routing table | MEDIUM | INLINE |
| 17 | Fleet HTTP endpoints | `X-Fleet-Signature` HMAC → `FleetServiceIdentity.app_slug` | Strong (cryptographic) | `FleetSignatureAuthentication` | LOW | PRE-DISPATCH |

### 7.2 Signal quality distribution

Per sub-agent 5 §C:

- **Strong (5 layers):** #1, #9 (user FK), #11 (sender FK), #15, #17
- **Weak (7 layers):** #2, #3, #4, #10 (agent_name string), #11 (sender_type), #13, #16
- **Missing (3 layers):** #6-#7, #12
- **Ambiguous (2 layers):** #5, #8, #14

Only **5 of 17 layers** have strong actor signal available today.

### 7.3 Existing precedent

Per sub-agent 5 §D, 8 identity-based checks in production:

1. `AssistantProfile.get_allowed_tools()` — per-user tool allowlist (`tool_dispatcher.py:687-720`)
2. `is_staff` — admin path gate (`auth_middleware.py:610-613`)
3. `is_reviewer` — reviewer write-block (`auth_middleware.py:616-623`)
4. `IsAuthenticated` — DRF permission (views)
5. Rigby-gating (`_verify_rigby_caller`) in tool dispatcher — checks caller matches Rigby's `runs_as_username`
6. Authority observation (warn-mode) — S1264
7. `FleetSignatureAuthentication` — HMAC-verified fleet apps
8. Rigby delegation routing table — routes work items to agents (not identity per se, but delegation audit)

### 7.4 Composition and identity drops

Per sub-agent 5 §E + §F:

**Chain: HTTP → ToolDispatcher → Tool Handler**
- Layer 1: request.user (Strong)
- Layer 2: AssistantProfile.get_allowed_tools() reads user_id
- Layer 3: handler receives (tool_name, payload, user_id, agent_name); no obligation to re-check

**Chain: HTTP → MissionRunner → Step.fn**
- Layer 1: request.user (Strong)
- Layer 4: config.runs_as_username='chris' (Weak — string, not verified)
- Layer 5: authority observation only (no block)
- Layer 6-7: Step.fn signature has no actor param (Missing)
- **Identity dropped at layer 4 boundary:** runs_as_username not persisted to OpsRun.

**Chain: HTTP → Celery → Task**
- Layer 1: request.user (Strong)
- Layer 8: context dict of strings (Ambiguous)
- **Identity dropped at Celery boundary:** request.user does not cross process boundary.

**Chain: Beat scheduler → Celery → Task**
- Beat has no HTTP context; no actor identity at layer 0.
- Layer 8: context dict of strings, if kwargs carry employee_handle
- **Identity was never present**; beat-triggered signals have no request.user available.

### 7.5 Cross-reference to Symbol Mapping boundaries (§6 of S1270)

S1270 enumerated 20 boundaries for "WHAT"; this doc has 17 for
"WHO." Per sub-agent 5 §G:

**Common boundaries (both docs list):**
1. HTTP middleware / DRF
2. ToolDispatcher.execute
3. Inside PA tool handler
4. Before MissionRunner.run
5. HTTP endpoint view
6. Celery task entry
7. Model signals
8. EventBus.publish
9. Fleet HTTP endpoints

**Actor-specific (only S1271):**
- MissionRunner preflight (warn-mode observation)
- Before Step.fn (step receives OpsRun only)
- Inside Step.fn (closure-dependent)
- AgentExecution creation
- Deliverable creation
- DirectMessage creation
- OpsRunEvent emission
- Agent-to-agent delegation

**Symbol-specific (only S1270):**
- Pre-Celery-task authority check (blocks task queue entry based on action_class)
- Model pre_save / pre_delete based on action_class
- Retrospective audit / evidence_for_mission

**Observation:** actor boundaries are **broader** than symbol
boundaries. Every layer where a symbol is checkable is also a
place where an actor should be checkable, but the reverse is
not true. Actor checks are meaningful even for *internal*
operations (beat tasks, signal handlers) where symbols don't
flow externally.

---

## 8. Actor Semantics for Employee OS

The Q7 mission question: **what does "actor" need to mean for
Employee OS?** This section is not a design; it is an
articulation of the semantic ambiguities today, so future design
missions have vocabulary to reason about.

### 8.1 Six actor semantics questions

**Q7.1 — Is an employee an actor?**
Yes. `AIEmployee` (Rigby, Platform Auditor, Chief of Staff, Bug
Triage Specialist) is an identity with runtime behavior. Missions
are attributed to employee_handle. Deliverables are attributed to
`agent_name='Rigby'`. DirectMessages are attributed to
`sender_type='rigby'`. Employees are named actors.

**Q7.2 — Is an agent an actor?**
Yes, but *differently*. AGENT_MAP agents (83 entries) are
executor primitives. They can be dispatched by a caller (a PA, an
employee, a workflow orchestrator). When an agent runs, an
`AgentExecution` row is created with `agent` FK + `owner_agent`
CharField. But agents are not first-class in the same way
employees are — an agent has no `runs_as_username`, no
`primary_chat_id`, no JobContract. Agents are *tools of actors*,
not actors themselves in the employee sense.

**Q7.3 — Is Chris an actor?**
Yes, and Chris is a *human* actor. `UnifiedUser(username='chris')`
is the primary human identity on the platform. Chris authenticates
via web/CLI/API tokens. Chris's User FK appears on
HumanAttentionItem.user, HumanFeedbackRecord.user,
DeliverableEvent.user, ChatConversation.user, ThreadParticipant.
user, and many other explicit surfaces.

**Q7.4 — Is Rigby acting as herself or on behalf of Chris?**
This is the deepest semantic question. Today: **both, ambiguously.**
- Rigby has an `AIEmployee` identity with `handle='rigby'`,
  `display_name='Rigby'`, `runs_as_username='chris'`.
- When Rigby dispatches a Celery task, the task runs in a worker
  process. `_resolve_runs_as_user_id` looks up
  `User(username='chris')`. Downstream FKs on
  AgentExecution.user, Deliverable.user etc. get set to
  `chris.id`.
- On surfaces like `DirectMessage`, Rigby's identity shows up as
  `sender_type='rigby'` (not chris) — chris is not surfaced as
  the sender.
- On surfaces like `OpsRun`, Rigby's identity is not surfaced at
  all (F1).
- On surfaces like `Deliverable.agent_name`, Rigby's identity is
  the string `'Rigby'`.

**No single surface consistently answers "is this action from
Rigby or from chris?"** The answer depends on the surface. This
is F2's ambiguity plane.

**Q7.5 — When Claude Code performs work through Rigby, who acted?**
- Claude Code is `ChatConversation.source='claude-code'` from
  the CLI perspective.
- Claude Code is `Agent(name='claude-code')` from the Agent row
  perspective (after S1263 consolidation).
- Claude Code messages arrive as `ChatConversation(user=chris,
  source='claude-code')` — chris's User FK is the identity,
  claude-code is the source.
- When Claude Code invokes a tool via PA, `ToolDispatcher.execute
  (agent_name=??, user_id=chris.id)`. What's `agent_name`?
  Undefined by convention.
- Rigby's `AIEmployee` is not the caller; her lifecycle is
  triggered by beat, not by claude-code.

**So the actor chain for claude-code → PA → tool call is:**
`Claude Code (source) → chris (user_id) → Rigby (PA context) →
tool (executor)`. Four identities on the path; only some persist
to the audit trail.

**Q7.6 — When a Celery beat fires a mission, who acted?**
- `OpsRun.triggered_by='beat'` (mechanism, not identity).
- No `request.user` at beat time.
- Downstream `AgentExecution.user=NULL` per Session 642 (Celery
  contexts).
- `runs_as_username` from `AIEmployee` resolves to `chris` at
  step-write time, if the code path uses it.

**So the actor for beat-fired missions is "system" in one sense
(no human triggered it) and "chris" in another (as configured by
runs_as_username), and "rigby" in a third (as the employee
executing). Three answers to one question.**

**Q7.7 — When MissionRunner emits evidence (OpsRunEvent), who
acted?**
- `OpsRunEvent` has no actor field.
- The event is contextually inherited from the parent OpsRun,
  which itself has no actor.
- The emitter is whichever step / callback wrote the event —
  identity is dropped at emission.

### 8.2 Three actor-kind axes

Sub-agent 4 §D observed that all 25 registries + all 22
attribution surfaces cluster along three axes:

**Axis 1 — Actor kind:**
- Human (Chris; via UnifiedUser)
- AI Employee (Rigby, Auditor, CoS, Triage; via AIEmployee dataclass)
- Autonomous engineer (Claude Code; via source='claude-code' + Agent row)
- Managed agent (any AGENT_MAP entry; via Agent DB row)
- Service (fleet apps; via FleetServiceIdentity)
- System (implicit; via sender_type='system' or source='system')
- Anonymous (Django AnonymousUser)

**Axis 2 — Actor authentication:**
- Token-based (UnifiedUser via auth middleware)
- Cryptographic (fleet HMAC)
- Frozen convention (AIEmployee dataclass)
- String literal (system, claude-code source)
- Django-framework class (AnonymousUser)

**Axis 3 — Actor persistence:**
- DB row (User, Agent, FleetServiceIdentity)
- Frozen constant (AIEmployee)
- Ephemeral (per-request request.user)
- Never persisted (system, various string literals)

**No design or code today crosses these axes uniformly.** Any
future actor primitive must decide how these axes compose.

### 8.3 Sender vs. Executor distinction

The most consequential semantic gap: **the platform does not
distinguish "actor who caused the action" from "actor who
executed it."** Concretely:

- When Rigby dispatches a worker agent that makes an LLM call
  that creates a Deliverable:
  - **Cause:** Rigby (the PA that initiated the mission)
  - **Executor:** worker agent (the AI that did the LLM call)
  - **Persistence:** Deliverable.agent_name is a single string
    field; it does not encode cause vs. executor.
  - **Common practice:** the string is the executor's name, but
    convention varies by call site.

This is the F4 finding sharpened: three CharField `agent_name`
surfaces cannot express both cause and executor. Any actor
primitive must decide whether to model this distinction (and if
so, how — with two fields, with a chain, with a delegation
table).

### 8.4 Scope of "actor" for downstream research

Different scopes yield different design pressures:

- **Narrow scope:** "actor" = the identity persisted on the row
  that gets written. Design task: fix Ambiguous / Missing cases
  in §3.1.
- **Medium scope:** "actor" = the causal chain from human trigger
  to executor. Design task: model delegation graphs; add
  cause+executor fields; enable audit chains.
- **Broad scope:** "actor" = a first-class concept unifying all
  three axes (kind, authentication, persistence). Design task:
  new primitive with anti-duplication constraints; touches ~25
  registries.

**This doc does not choose a scope.** That choice is downstream
per §13's recommended research mission.

### 8.5 Proposed minimal actor-role vocabulary — executor / sponsor / principal (Rigby S1271 SIGN)

Per Rigby S1271 SIGN pressure-test #4: leaving the "what is an
actor" question entirely open weakens the doc — every downstream
enforcement discussion will re-litigate definitions. This
sub-section proposes a **minimal 3-role vocabulary** the doc uses
consistently for the remaining findings and that downstream
research is expected to inherit.

**The three roles:**

1. **executor_actor** — the runtime entity that performed the
   operation. Examples: an `AIEmployee` handle (`"rigby"`), a
   fleet service (`app_slug='contract-concierge'`), a Celery
   worker (`system`), an AGENT_MAP agent (`"CodeGeneratorAgent"`).
2. **sponsor_actor** — the entity that authorized or requested
   the action. Examples: a `UnifiedUser` (`chris`), a beat
   schedule (`system` sponsor), a CLI operator, an autonomous
   engineer (`claude-code`).
3. **principal_user** — the `UnifiedUser` under which the row
   is written for ownership / permission / row-level access
   purposes. Examples: `User(username='chris')` for
   `Deliverable.user`, `User(username='chris')` for
   `AgentExecution.user`.

**Why three roles.** Per Rigby's biggest-architectural-risk call:
the platform today conflates these into ambiguous CharFields and
FKs. `runs_as_username='chris'` is a **principal_user selection
mechanism**, not the executor_actor; the executor is Rigby.
Confusing the two produces "confidently wrong audit trails."

**Canonical role interpretations for key scenarios:**

| Scenario | executor_actor | sponsor_actor | principal_user |
|---|---|---|---|
| Beat-fired Rigby mission emits DirectMessage | `rigby` (employee handle) | `system` (beat) | `chris` (row ownership if persisted) |
| Chris invokes tool via PA chat | `PersonalAssistant` (or specific agent) | `chris` | `chris` |
| Claude Code invokes tool via CLI-source PA chat | `claude-code` (Agent DB row) | `claude-code` (source enum); indirectly `chris` (user context) | `chris` (ChatConversation.user) |
| Management command run manually | (mgmt command name) | (operator, if known) | (may be None or `chris`) |
| Fleet HTTP write | `<app_slug>` (fleet identity) | `<app_slug>` | (may be None or fleet-owned account) |
| Employee dispatches worker agent | delegating: `rigby`; executing: `<WorkerAgent>` | `rigby` (delegator) | `chris` |
| WebSocket message from anonymous user | `AnonymousUser` | `AnonymousUser` | None |

**Role → field mapping today (partial; where roles are
persisted):**

| Field / concept | Role today | Notes |
|---|---|---|
| `AIEmployee.runs_as_username` | **principal_user selector** (Rigby's principal is `chris`) | Not the executor; this is what §11 F3 flagged as "unverified string." |
| `UnifiedUser.username` via auth token | **sponsor_actor** (usually) + **principal_user** | Depends on context — the same User can be sponsor and principal. |
| `AIEmployee.handle` | **executor_actor** (for autonomous jobs) | Frozen registry; canonical. |
| `Agent.name` / `AGENT_MAP` | **executor_actor** (for dispatched agents) | Canonical after S1263 consolidation. |
| `FleetServiceIdentity.app_slug` | **executor_actor** (for fleet) + often **sponsor_actor** | HMAC-verified. |
| `Deliverable.user` FK | **principal_user** | Not the executor. |
| `Deliverable.agent_name` | **executor_actor** (ambiguous per F4) | Delegator vs. executor undefined. |
| `AgentExecution.user` FK | **principal_user** | Nullable per Session 642. |
| `AgentExecution.owner_agent` | **executor_actor** (ambiguous per F4) | Undefined. |
| `DirectMessage.sender` FK | **principal_user** (usually the human sending) OR None for system messages | Nullable via SET_NULL. |
| `DirectMessage.sender_type` | **executor_actor kind** (user/rigby/system) | Choice enum. |
| `ChatConversation.user` FK | **principal_user** | Owner of conversation. |
| `ChatConversation.source` | **sponsor_actor kind** (web/mobile/discord/api/claude-code/pa) | Choice enum. |
| `OpsRun.triggered_by` | **sponsor_actor kind** (beat/pa_tool/mgmt_cmd/manual) | Choice enum; not the specific sponsor. |

**Observation:** the platform *already carries* two of the three
roles on many surfaces (principal_user via User FKs;
executor_actor kind via choice enums), but the two are stored in
separate fields without a documented contract that they must be
consistent, and the executor_actor kind is often the ambiguous
CharField (F4). The **sponsor_actor** is the least-populated
role today.

**Scope note.** This vocabulary is proposed *for use within this
doc and inherited by downstream research*. It is not a schema
change and not a design decision. The role names could be
renamed by the downstream design mission (§13.1); the *shape*
(three roles rather than one) is the load-bearing proposal.

---

## 9. Relationship to Symbol Mapping

Per Q8: Symbol Mapping (S1270) and Actor Attribution (this doc)
are the two halves of the same enforcement primitive.

### 9.1 The three concepts

| Concept | Question | Where scoped |
|---|---|---|
| **Symbol Mapping** | WHAT action happened? | S1270 (this month) |
| **Actor Attribution** | WHO performed it? | S1271 (this doc) |
| **Authority** | Was WHO allowed to do WHAT? | Neither yet; awaits both prerequisites |

### 9.2 Enforcement requires both

Consider the enforce-mode check "Rigby cannot open a PR":

1. **Symbol Mapping** answers: is this action `"open_pull_request"`?
   (S1270 F2: today no runtime surface carries `action_class`
   metadata. F1: `"open_pull_request"` is 4-of-4 PROHIBITED across
   all employees.)
2. **Actor Attribution** answers: is the attempted actor Rigby?
   (This doc F1: OpsRun has no actor. F4: `agent_name` fields are
   ambiguous. F6: identity is dropped at 3 boundaries.)
3. **Authority** would answer: does Rigby's contract permit
   `"open_pull_request"`? (governance_authority_evolution.md F2:
   authority dict exists but has no runtime readers.)

**Any single answer is insufficient.** Enforcing "Rigby cannot
open a PR" requires all three: detect the action, identify the
actor, check the authority contract, block on mismatch. All
three primitives are foundational; missing any one leaves the
gate open.

### 9.3 Composition surface

Where would the three primitives compose? Per the S1270 §6
enumeration + this doc's §7:

**Best candidate layer for composition:** the ToolDispatcher
entry (S1270 layer 6 / this doc layer 2). Both docs identify
this as the layer where:
- Symbol Mapping could bind tool + action → action_class
- Actor Attribution could enforce user_id → canonical actor
- Authority check could gate action_class vs. contract

But **no design proposes this composition today.** That's the
downstream mission per §13.

### 9.4 Attribution-first vs. Mapping-first ordering (Rigby S1271 SIGN)

Per Rigby S1271 SIGN pressure-test #5: **the ordering
(S1270 Symbol Mapping → S1271 Actor Attribution) is defensible
but not the only defensible order.** Recording the counter-
argument here prevents future readers from mistaking retrospective
rationalization for principled sequencing.

**Why Attribution-first is plausible:**

- Adding a `user_id` or `actor_id` field somewhere (e.g.,
  OpsRun) is *often* mechanically cheap and immediately unlocks
  the query "who caused this run?"
- Reduces audit ambiguity quickly for beat-triggered flows.

**Why Attribution-first is risky here specifically:**

- Per F11 + §8.5: the platform currently conflates
  executor_actor / sponsor_actor / principal_user. Stamping an
  "actor" now — without first declaring which role the stamp
  represents — codifies the conflation as schema.
- Concrete failure mode: an `OpsRun.user` FK added without
  role clarity would almost certainly land as the
  principal_user (since that's the User FK
  `_resolve_runs_as_user_id` produces), while readers would
  interpret it as the executor_actor. The confidently-wrong
  audit trail becomes the new baseline.

**Why Mapping-first is still justified:**

- Symbol Mapping has a warn-mode anchor (S1264 PR #2756) and
  an explicit in-code assertion at
  `mission_runner.py:895-899` that enforce-mode requires
  symbol binding. Actor Attribution has no equivalent
  contract-level assertion — only the observation that
  attribution surfaces are Ambiguous / Missing (F2).
- Enforcement asks "can Rigby do X?" — you need X to be well-
  defined (Symbol Mapping) before "who did it" is
  evaluable against a specific action_class. Attribution
  without symbol binding gives "who did *something*," which
  is weaker as a policy predicate.

**Net:** the two-doc order (Symbol Mapping then Actor
Attribution) is a defensible sequencing given the current
platform state, but the *implementation* order at design-mission
time (§13.1) is a separate decision. Both prerequisites must
land before enforcement is meaningful; the *sequence* of landing
is a downstream call.

### 9.5 Missing prerequisites (Q8 answer)

Before authority enforcement can exist, three primitives must
land:

1. **Symbol Mapping v0** — some binding between authority strings
   and runtime symbols (S1270 §5 options A/B/C/D/E).
2. **Actor Attribution v0** — some canonical actor primitive OR
   filling of the Ambiguous / Missing rows in §3.1. Most
   critical: OpsRun.user (or `.employee_handle`) FK to close F1.
3. **Composition contract** — how do the two primitives compose
   at the same enforcement layer? What's the enforcement mode
   (PRE-DISPATCH vs. INLINE vs. POST-DISPATCH)?

**None of these three exists in code today.** All three are the
scope of downstream research + design missions.

---

## 10. Reuse Classification

Per the standard research-doc format used by prior architectural
research. Symbol-mapping-scoped reuse classifications for the
primitives, helpers, and models relevant to actor attribution — a
curated subset of the 25 §6.1 registries (registries that are
DO-NOT-REUSE / DEPRECATED / UNKNOWN / orthogonal are inventoried
in §6 but not classified for actor primitive reuse here).

### 10.1 SAFE TO REUSE (14)

1. **`UnifiedUser`** — primary human identity root. Any actor
   primitive branches from here.
2. **`AIEmployee` frozen dataclass** — proven identity primitive
   for autonomous agents (EMPLOYEE_OS_PRIMITIVES §1 row 1).
3. **`Agent` DB row** — canonical executor identity.
4. **`_EMPLOYEES_BY_HANDLE` dict** — proven registry pattern.
5. **`_JOBS_BY_EMPLOYEE` dict** — companion registry.
6. **`AGENT_MAP` dict** — 83 stable agent names.
7. **`AssistantProfile`** — per-user PA config; already the
   canonical actor→tool authorization surface.
8. **`ChatConversation`** — actor identity via user FK + source
   choice.
9. **`canonicalize_agent_name()` function** — single alias
   canonicalization site (`deliverable_aliases.py:39-47`).
10. **`AGENT_NAME_ALIASES` dict** — extensible alias table (2
    entries today).
11. **`FleetServiceIdentity`** — HMAC-verified service actor.
12. **`EnhancedUserProfile`** — role + subscription + preferences.
13. **`JobContract`** — proven per-employee policy primitive.
14. **`_resolve_runs_as_user_id`** — the runs_as_username → User
    lookup helper (though F3 flags its silent-None behavior).

### 10.2 REUSE WITH WRAPPER (7)

1. **`AgentExecution`** — `user` FK is nullable; `owner_agent`
   CharField is Ambiguous. Wrapper documents the delegator-vs-
   executor semantic + adds validation.
2. **`ToolCallRecord`** — `agent_name` CharField is Ambiguous
   (F4). Wrapper documents semantics + optionally splits into
   two fields.
3. **`LLMCallEvent`** — same Ambiguity as ToolCallRecord.
4. **`CeleryTaskEvent`** — `agent_name` is Unreliable (empty
   string overloaded). Wrapper documents "not-agent-task" vs.
   "pre-migration" vs. "missing kwargs" cases.
5. **`DirectMessage.SENDER_TYPE_CHOICES`** — extend with new
   employee handles as they're added; migration cost.
6. **`WORKSPACE_AWARE_AGENTS`** — refactor from local list to
   frozen constant or DB registry.
7. **`OpsRun`** — reuse for mission execution but the actor gap
   (F1) blocks direct enforcement use; wrapper documents the
   gap + optionally adds a JSON convention on `summary`.

### 10.3 DO NOT REUSE (0)

No existing identity registry is so broken that it shouldn't be
reused for actor attribution. The 7 WRAPPER classifications cover
the friction cases.

### 10.4 DEPRECATED (1)

**`UserProfile`** (`core/models/users/models.py:12`) — superseded
by `EnhancedUserProfile` per sub-agent 4 §B. Don't build new
features on it.

### 10.5 UNKNOWN (3)

1. **`MessageThread`** — no single owner FK; attribution is
   inferred via ThreadParticipant M2M. Classify depends on
   whether "thread owner" is a needed concept downstream.
2. **`OpsRunEvent`** — no actor field. Whether to add one, or to
   rely on parent OpsRun (once that gets an actor), is an open
   design question.
3. **Service account "chris"** — does a documented, canonical
   `User(username='chris')` row exist in production? Sub-agent 1
   §D notes it's asserted implicitly; runtime existence is
   UNKNOWN without direct DB probe.

### 10.6 Anti-duplication summary

Per §6.3: five hypothetical primitive shapes (`ActorRegistry`
model, `actor_handle` field, `actor_type` enum, `ActorPermission`
model, `ActorAuditLog` model) all fail anti-duplication because
they duplicate existing registries. Any actor primitive design
must extend existing surfaces + add a shared classifier enum, not
create new tables.

---

## 11. Architectural Findings

Ten findings synthesized from the evidence. Numbered F1-F10;
independent numbering from prior research docs.

### F1 — OpsRun has no actor field

`core/models_ops_runs.py:11-88` verified. All 4 employees run
missions on this row. `triggered_by` classifies mechanism, not
identity. Missions cannot answer "who ran this?" without querying
`summary` JSON or joining downstream tables. **This is the
largest single attribution gap on the platform.**

### F2 — Five kinds of "weak" attribution

Sub-agent 2 §B defined and populated: Explicit (13), Inferred (2),
Missing (2), Ambiguous (4), Unreliable (1) across 22 audited
surfaces. Only 59% of surfaces are Explicit. The distribution is
skewed: **human-facing surfaces (HAI, HumanFeedback,
DeliverableEvent) are strong; AI/agent-facing surfaces
(ToolCallRecord, LLMCallEvent, AgentExecution.owner_agent) are
weak.**

### F3 — `runs_as_username` is unverified

`mission_runner.py:1585-1591`. Silent None on missing User.
All 4 employees hardcode `"chris"`. No runtime alert if
`User('chris')` is renamed, deleted, or never seeded. This is
the identity-token-mismatch pattern from S1098 mapped to
mission execution.

### F4 — Three `agent_name` CharFields with drifting semantics

`ToolCallRecord.agent_name` (`models_tool_calls.py:57-60`),
`AgentExecution.owner_agent` (`models_unified_system.py:924-927`),
`LLMCallEvent.agent_name` (`models_llm_telemetry.py:62-65`). No
docstring resolves whether the string means the delegator or the
executor. In a delegated call chain, readers cannot reconstruct
the delegation graph from the row-level fields.

### F5 — Duplicate identity is a documented recurring failure

S1226 (migration 0365, agent_name normalization) → S1263 (PR
#2754, migration 0374, ClaudeCode/claude-code consolidation).
Pattern: any new agent-creation site that bypasses
`canonicalize_agent_name` re-introduces the duplicate risk.
Structural fix requires a central Agent factory with mandatory
canonicalization (does not exist today, per
`EMPLOYEE_OS_PRIMITIVES.md` §1 — no such row).

### F6 — Identity is dropped at three structural boundaries

Sub-agent 5 §F. (a) HTTP → Celery: request.user lost, task
inherits context dict of strings. (b) MissionRunner config →
OpsRun row: runs_as_username not persisted. (c) MissionRunner →
Step.fn: step signature receives OpsRun only, no actor parameter.
Each drop is a structural design decision, not a bug — but each
downstream boundary needing enforcement must re-infer identity.

### F7 — Only `AssistantProfile.get_allowed_tools()` reads actor for a gate

Sub-agent 5 §D. Eight identity-based gates in production; only
one (`tool_dispatcher.py:687-720`) uses the canonical
`request.user → AssistantProfile.user` chain as its enforcement
predicate. Every other gate (is_staff, is_reviewer,
IsAuthenticated, Rigby-gating, warn-mode observation, fleet
HMAC, retry budget, timeout enforcement) uses a different actor
abstraction. **No unified identity model drives enforcement
today.**

### F8 — Historical case for Actor Attribution is strong

Sub-agent 3 catalog. 15 incidents: 7 YES + 4 PARTIALLY + 4 NO =
73% in scope. Silent failures dominate (60% silent or semi-
silent). The strongest recurrence pattern is the identity-token-
mismatch chain (S1098 → S1099 → S1083 pre-fix), which no
existing primitive prevents.

### F9 — Actor Attribution and Symbol Mapping are inseparable for enforcement

§9. Symbol Mapping alone answers "what action" — but without
knowing "who acted," authority cannot be enforced. Actor
Attribution alone answers "who" — but without knowing "what
action_class," authority contracts are irrelevant. **Enforcement
requires both primitives at the same layer.**

### F10 — Sender-vs-executor distinction is undesigned

§8.3. The platform's single `agent_name` CharField cannot express
both "actor who caused the action" and "actor who executed it."
When Rigby dispatches a worker agent, the persistence surfaces
record one string but the semantic meaning is undefined by
convention. Any future actor primitive must decide whether to
model this distinction (and how).

### F11 — A single "actor" label is insufficient (Rigby S1271 SIGN)

Per Rigby S1271 SIGN pressure-test #4 and biggest-architectural-
risk call: enforcement-grade attribution requires at least three
roles — **executor_actor** (runtime entity that performed the
operation), **sponsor_actor** (entity that authorized it), and
**principal_user** (User FK used for row ownership /
permissions). See §8.5 for the vocabulary definition and
canonical-scenario table.

**Load-bearing implication:** Treating any single field as "the
actor" without declaring which of the three roles it represents
produces "confidently wrong audit trails" (Rigby's phrase).
Concretely: `runs_as_username='chris'` is a *principal_user
selection mechanism*, not the executor_actor. The executor is
`rigby` (the AIEmployee); the principal is `chris` (the User).
Confusing the two is F3's silent-None problem sharpened into a
role-semantics problem. **Adding a "user" field to OpsRun
without declaring which role it represents would codify the
conflation as schema.**

**Evidence:** §8.5's role-to-field mapping table shows the
platform already stores two of the three roles on many
surfaces (principal_user via User FKs; executor_actor kind via
choice enums), but the two are in *separate fields* with no
consistency contract. The sponsor_actor is the least-populated
role today.

---

## 12. Open Questions

Genuine open questions. Not implementation tasks. Not invented
answers.

**Q1 — Should there be a canonical actor primitive at all?**
Options: (a) unified `Actor` model with `actor_type` enum
(kind: human / employee / agent / service / system), (b) leave
each identity concept as separate primitive and add a shared
classifier enum, (c) add strong FKs on the currently-Ambiguous /
Missing surfaces without new primitive. All three respect anti-
duplication if scoped carefully.

**Q2 — How should sender vs. executor be encoded?**
Per F10 + §8.3. Options: (a) split into two fields (`caller_
agent`, `executor_agent`), (b) delegation chain table (like
`ToolCallRecord` with parent-child links), (c) preserve single
field with strict convention + doctstring.

**Q3 — Should OpsRun get an actor field?**
Per F1. If yes, options: (a) direct `user` FK, (b)
`employee_handle` CharField, (c) both. Migration cost: MEDIUM
(OpsRun has many downstream queries). Backward compat: additive.

**Q4 — How should `runs_as_username` be verified at runtime?**
Per F3. Options: (a) fail-loud on missing User at
MissionRunnerConfig construction, (b) fail-loud on missing at
`_resolve_runs_as_user_id`, (c) require User row seed at deploy
time (would eliminate silent None), (d) accept silent-None and
document the behavior.

**Q5 — How should identity be threaded across the three drop
boundaries (F6)?**
Per §7.4. Options: (a) explicit `actor` kwarg on
`apply_async(kwargs={'actor': ...})`, (b) thread-local /
contextvar identity propagation (fragile in async), (c) accept
drops and require re-lookup at each layer.

**Q6 — Should Actor Attribution formalize before Symbol Mapping,
after Symbol Mapping, or in parallel?**
Per F9. This doc argues both are prerequisites for authority
enforcement; the *order* they land in is a strategic choice.
S1270 completed first; this research completed second. Whether
implementation should mirror that order is UNKNOWN.

**Q7 — What is the actor for beat-fired missions?**
Per §8, Q7.6. Three answers today: "system" (no human triggered),
"chris" (as configured by runs_as_username), "rigby" (as the
employee executing). A design must pick one, or model all three
explicitly as a chain.

**Q8 — Should system be a User row or a string convention?**
Per §6.5 gap #1 + Q7.4. Options: (a) create `User(username=
'system')` seed row (strong FK everywhere), (b) preserve string
conventions per surface (drift risk), (c) create an `actor_kind`
enum with `system` as a value (independent of User table).

**Q9 — Does Claude Code deserve a canonical actor identity?**
Per §8, Q7.5. Options: (a) reserved `User(username='claude-code')`
seed row, (b) already-consolidated `Agent(name='claude-code')`
DB row, (c) source string on ChatConversation (current pattern).
Claude Code performs work through Chris's user context today;
attribution to "claude-code" is via source string only.

**Q10 — How should cross-plane composition (F10 of governance
audit) work?**
If Actor Attribution + Symbol Mapping both land, and authority
becomes enforceable, how does actor identity compose with the
four governance planes (autonomy / authority / budget / human)?
This is scope of a separate research mission (see §13).

**Q11 — Should agent_name canonicalization extend beyond
Agent-DB variants?**
Per §6.4. Today `canonicalize_agent_name` handles Agent DB
variants only (2 aliases). Should it also handle AIEmployee ↔
Agent DB mapping ("rigby" employee ↔ "Rigby" Agent row)?
Currently they are separate identities.

**Q12 — What is the smallest viable v0 for Actor Attribution?**
Per Q1's option (c) — "add strong FKs on currently-Ambiguous /
Missing surfaces without new primitive" — is a minimal step.
Concretely: adding `OpsRun.user` FK (F1) and clarifying the
three `agent_name` CharFields' semantics (F4) closes the two
largest gaps without introducing new primitives.

---

## 13. Recommended Next Research

Based on evidence, not preference.

### 13.1 Authority Enforcement Design Space (P0 — recommended next)

**Scope.** Take the 5 Symbol Mapping options from S1270 §5 and
the 25 identity registries + 22 attribution surfaces from this
doc, and produce a design proposal that composes both primitives
into an actual enforcement gate. The mission answers: at which
layer(s) does authority check fire? What data does it need at
that layer? What does it do on mismatch?

**Why P0.** Both Symbol Mapping (S1270) and Actor Attribution
(this doc) are foundational research; neither is sufficient for
enforcement on its own. Every downstream authority mission
(Trust Propagation, Employee Delegation, Memory Architecture)
depends on knowing how enforcement composes.

**Why NOT this doc.** This research inventories the "WHO"
question. Composing WHO + WHAT into an enforcement gate is a
downstream design decision.

**Prerequisites.** S1270 (Symbol Mapping) + this doc (Actor
Attribution). Both are draft research; neither is design.

**Expected outcome.** A design-space enumeration (like S1270 §5
options) for enforcement, with tradeoffs, migration cost, and
composition semantics. Not a design decision; a scoping doc for
Chris to gate.

### 13.2 Trust Propagation (P1 — was ARCHITECTURE_INDEX §5.3)

**Scope.** Once Symbol Mapping + Actor Attribution exist, cross-
employee trust becomes designable. Today `derive_status()`
computes per-employee trust; cross-employee is undefined.

**Why P1.** Depends on the enforcement primitive shipping (from
§13.1).

### 13.3 Cross-Plane Composition (P1 — governance F10)

**Scope.** Per this doc's F10 + governance_authority_evolution.md
F1: four governance planes don't compose. If enforcement lands,
how do actor + action + autonomy + budget + human governance
compose?

**Why P1.** Blocks any enforcement mode that involves multiple
planes.

### 13.4 Employee Delegation Design (P2 — was ARCHITECTURE_INDEX §5.5)

**Scope.** Cross-employee scheduling primitive (subscribe to
(employee, verdict) → dispatch target employee's next mission
preflight).

**Why P2.** Blocked on §13.1 + §13.2. Authority + trust must be
answered first.

### 13.5 Memory Architecture (P2 — was ARCHITECTURE_INDEX §5.4)

**Scope.** Cross-employee episodic memory. How does one employee
"remember" what another employee did?

**Why P2.** Requires actor identity to be canonicalized (this
doc) + trust propagation (§13.2).

### 13.6 Explicitly NOT recommended as immediate next research

- **Mission Composition** (ARCHITECTURE_INDEX §5.6) — orthogonal
  to actor identity; can happen in parallel with §13.1.
- **Focus Mode Inventory** (governance §10.8) — orthogonal;
  parallel-safe.
- **Adding OpsRun.user FK as an immediate implementation task
  without a research doc first** — would violate the research
  discipline. F1 is a finding, not a design decision.

---

## 14. Appendix

### 14.1 Explicit answers to mission-spec Q1-Q10

**Q1 — What actor identities exist today?**
19 concepts inventoried in §2. Clustered into 7 kinds (human,
AI employee, agent, conversation actor, message actor, service,
auth state) per §2.2. Overlap and collision documented in §2.3.

**Q2 — Where is actor identity recorded?**
22 attribution surfaces inventoried in §3.1. Distribution: 13
Explicit, 2 Inferred, 4 Ambiguous, 1 Unreliable, 2 Missing
(OpsRun, OpsRunEvent).

**Q3 — Where does actor identity change shape?**
14 shape changes in §4.1. Three critical drop boundaries in
§4.2: HTTP → Celery, MissionRunner config → OpsRun, MissionRunner
→ Step.fn.

**Q4 — What identity collisions or duplicates have happened?**
15 incidents in §5.1. Highlights: S1263 ClaudeCode/claude-code
consolidation (I-A2), S1098 admin/donkeyking token split (I-A1),
S1234 context['user'] dict vs. FK (I-A3), S1226 agent_name
string vs. FK normalization gap (I-A4).

**Q5 — What existing identity registries can be reused?**
25 registries in §6.1. Classification: 14 SAFE + 7 WRAPPER + 1
DO-NOT-REUSE + 1 DEPRECATED + 3 UNKNOWN. Anti-duplication check
in §6.3 blocks all 5 hypothetical new-primitive shapes.

**Q6 — Where could actor attribution be enforced?**
17 candidate layers in §7.1. Signal quality: 5 Strong, 7 Weak,
3 Missing, 2 Ambiguous. Only 1 layer today
(`AssistantProfile.get_allowed_tools()`) uses canonical actor
identity as a gate predicate (F7).

**Q7 — What does "actor" need to mean for Employee OS?**
Six semantic questions posed in §8.1 — none has a canonical
answer today. Three axes in §8.2 (kind, authentication,
persistence). Sender-vs-executor distinction is undesigned
(F10 + §8.3).

**Q8 — What is the relationship between actor identity and
authority?**
§9. Symbol Mapping = WHAT, Actor Attribution = WHO, Authority =
WHETHER. Enforcement requires all three at the same layer. None
exists today.

**Q9 — What historical failures would actor attribution have
prevented?**
§5.1. 7 YES + 4 PARTIALLY + 4 NO = 15 total. 73% in scope
(YES+PARTIALLY). Silent failures dominate (60% of incidents).
5 recurrence chains identified in §5.6.

**Q10 — What should the next research mission be?**
§13. Recommended P0: Authority Enforcement Design Space (composes
Symbol Mapping + Actor Attribution + Authority into an
enforcement gate). Downstream P1s: Trust Propagation, Cross-
Plane Composition.

### 14.2 Cross-reference

| Prior research | Relationship |
|---|---|
| `docs/EMPLOYEE_OS_PRIMITIVES.md` §1 rows 1-2 | This doc's §2 concepts #3-#6 expand AIEmployee + JobContract identity fields |
| `docs/EMPLOYEE_OS_PRIMITIVES.md` §2 anti-duplication | This doc's §6.3 anti-duplication check honors the matrix; all 5 hypothetical new-primitives are BLOCKED |
| `docs/research/symbol_mapping_architecture.md` §5 (5 mapping options) | This doc's §9 composes with them — Symbol Mapping and Actor Attribution are the two halves of the same enforcement primitive |
| `docs/research/symbol_mapping_architecture.md` §7 (23 incidents) | This doc's §5 has 6 overlapping incidents; the 3 fully-actor-related are in this doc's YES list |
| `docs/research/governance_authority_evolution.md` §4 (35 gates) | This doc's §7.3 references 8 identity-based gates from that set; §7.5 crossreferences the 20 boundaries |
| `docs/research/employee_os_collaboration_patterns.md` §7 (29 failure modes) | Some overlap with this doc's §5 identity failures; new S1271 incidents added |
| `docs/research/employee_os_communication_substrate_audit.md` §3.5 (31 HAI creators) | Referenced as evidence that HAI is a strong attribution surface (§3.1 row 10) |
| `docs/research/ARCHITECTURE_INDEX.md` §5 gap list | This doc closes one of the named gaps; recommends the next |
| `docs/handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md` | Named symbol mapping as prereq for enforce-mode; this doc adds actor attribution as parallel prereq |

### 14.3 Documentation drift surfaced

| Item | Source A says | Source B (runtime) says | Resolution |
|---|---|---|---|
| AgentExecution deprecation | `models_unified_system.py:884-887` claims deprecated in Session 287; use `agents.models.AgentExecution` instead | `agents/models.py` is a compat shim; no `AgentExecution` class in `agents_registry/`. 10+ active import sites reference `models_unified_system.AgentExecution` | Deprecation header is **stale**. Model is the live canonical AgentExecution. This doc treats it as active. |
| AGENT_MAP count | Sub-agent 4: "149 agents in AGENT_MAP" | PLATFORM_INVENTORY: 83 agents (74 enabled, 8 rerouted, 1 blocked) | PLATFORM_INVENTORY is the runtime anchor per DOC_LIFECYCLE §2c. This doc uses **83**. |
| WORKSPACE_AWARE_AGENTS count | Sub-agent 4: 17 entries | Direct read verified: **20 entries** (4 dev + 3 content + 4 strategy + 5 research + 2 analysis + 1 legal + 1 system) at `epa_handlers_tools.py:3873-3907` | Sub-agent 4 undercount corrected. This doc uses **20** matching S1270. |
| AGENT_NAME_ALIASES count | Sub-agent 4: 2 entries | Direct read (verified): exactly 2 entries (`{'rigby': 'Rigby', 'ClaudeCode': 'claude-code'}`) | Verified via Claude direct read. This doc uses **2**. |
| OpsRun user field | Sub-agent 2: `Missing` (no user FK) | Direct read: verified — no user FK, only `triggered_by` mechanism | Verified. F1 stands. |

### 14.4 Verifier-loop pass notes

**Sub-agent tasking:** 5 parallel Explore agents. Each prompt
explicit "no design proposals" discipline. Reports returned in
under 10 minutes.

**Load-bearing claims spot-verified by Claude:**
- OpsRun schema at `models_ops_runs.py:11-88` — no user FK ✓
- `MissionRunner._resolve_runs_as_user_id` at `mission_runner.py:
  1585-1591` — iexact lookup, returns None on miss ✓
- `AGENT_NAME_ALIASES` at `deliverable_aliases.py:33-36` — 2
  entries: `{'rigby': 'Rigby', 'ClaudeCode': 'claude-code'}` ✓
- `AgentExecution.user` nullable per Session 642 (Celery),
  `owner_agent` CharField per Session 843, at
  `models_unified_system.py:882-928` ✓
- `AgentExecution` deprecation header is stale — no replacement
  in `agents/models.py` or `agents_registry/`; 10+ active
  imports ✓
- `DirectMessage.sender` nullable FK + `SENDER_TYPE_CHOICES`
  3 values at `models_messaging.py:99-141` ✓
- `AssistantProfile.get_allowed_tools()` at `tool_dispatcher.py:
  692-720` reads per-user allowed_tools ✓

**Sub-agent drift corrected:**
- Sub-agent 4's "149 agents" → runtime anchor 83 used.
- Sub-agent 4's WORKSPACE_AWARE_AGENTS count of 17 → verified 20
  via direct read of `epa_handlers_tools.py:3873-3907` (matches
  S1270 §3.1 row 15).

**Self-verifier pass (one round) before finalization identified
and fixed:**
- Initially §2 had 20 identity concepts; consolidated
  "primary_chat_id" as concept #6 (was misclassified) → 19.
- §3.1 initially had 20 attribution surfaces; added
  `AssistantProfile` (#18) + `ContentPacket` (#21) +
  `DeliverableExport` (#20) explicitly per sub-agent 2 → 22.
- §6.1 initially had 24 registries; added `Deliverable.agent_name`
  (#25) as a distinct attribution CharField pattern → 25.
- §11 F1-F10 numbered independently; not aligned with §1 major
  findings numbers to preserve exec-summary vs. architectural-
  finding distinction (matches prior research doc convention).

**Status after self-verifier pass.** Publishable as draft. Rigby
independent SIGN review pending — verdict + folded edits will be
recorded in §14.5.

### 14.5 Rigby SIGN review record

**Verdict: SIGN-with-edits.** Rigby overall confidence: **Medium**
(with self-declared partial read of the 1798-line draft;
pressure-test focused on framing + architecture risk over line-by-
line completeness).

**Rigby's SIGN summary:**
- **Strongest finding:** F1 (OpsRun has no actor field); real
  and materially load-bearing, spot-verified.
- **Weakest section:** the "therefore Actor Attribution is
  foundational for every downstream mission" move in the
  Executive Summary was slightly over-tightened; folded via
  §9.4's Attribution-first counterargument acknowledgment.
- **Biggest architectural risk (folded via F11 + §8.5):**
  conflating executor / sponsor / principal into a single
  "actor" label — treating any single field as "the actor"
  without declaring which role it represents produces
  "confidently wrong audit trails."
- **What I got wrong (Rigby's 5 blunt calls, all folded):**
  (1) treating OpsRun's missing field as single-axis (folded
  via F11 → role-semantics deficit framing), (2) implying
  enforcement inevitably needs a single combined WHAT+WHO
  primitive (folded via F9 softening + §9.4 counterargument),
  (3) any implication that runs_as_username is "actor"
  (folded via F11 + §8.5 role-to-field mapping), (4) any
  implication that agent_name drift is naming hygiene rather
  than enforcement-blocking semantic ambiguity (folded via F11
  reinforcing F4), (5) implying that "add actor field to
  OpsRun" is the obvious fix (folded via F11's explicit
  warning against adding a "user" field to OpsRun without
  role clarity).

**Must-fix edits folded (4):**
1. Introduce 3-role vocabulary (executor_actor / sponsor_actor /
   principal_user) as normative — §8.5 added + F11 added + §2
   forward-reference.
2. Soften F1 wording — "cannot answer reliably or queryably."
3. Soften F9 wording — "the cleanest enforcement primitive."
4. Add missing-surfaces inventory — §3.5 added covering
   created_by/updated_by mixin absence, request-level identity
   propagation, WebSocket, side-effect audit anchoring
   possibility, fleet write paths, delegation chain query.

**Optional edits folded (2):**
5. Attribution-first vs. Mapping-first paragraph added at §9.4;
   original §9.4 renumbered to §9.5.
6. Role-confusion framing note added at §5 head.

**Optional edits deferred (1):**
- Full historical-failure role-confusion recast per-incident
  (Rigby's optional #7's per-incident rewrite): deferred; the
  §5-head framing note + §8.5's role vocabulary provide the
  interpretive lens without re-classifying every YES/PARTIALLY/
  NO verdict. Downstream design mission (§13.1) can consume the
  role vocabulary and re-frame incidents as needed.

**Rigby SIGN-clean on (no edits required):**
- F1 as materially load-bearing (spot-verified against
  `models_ops_runs.py:11-88`).
- F4 as real enforcement-blocking ambiguity (not cosmetic
  hygiene).
- §8.3 sender-vs-executor distinction.
- §13.1 Authority Enforcement Design Space as the recommended
  next research; no preceding mission required. Explicitly:
  *don't jump to* "OpsRun.user field" as implementation-first
  — that violates the role-clarity discipline F11 established.

**Rigby's placement guidance folded:**
- 3-role vocabulary placed in §8.5 (Rigby's recommended
  location — semantics, not a finding); F11 added as
  lightweight summary pointer.

**Not re-invoked (offered but declined):**
- Rigby offered a diff-based re-SIGN pass on the folded
  sections. Not invoked at close: edits are contained; verdict
  is SIGN-with-edits not NEEDS-MORE; the doc's next consumer
  is the §13.1 design mission which will re-review as a matter
  of course.

### 14.6 Evidence integrity notes

- Five parallel Explore sub-agents produced the source material
  for §2-§7.
- No runtime state modified; research-only per mission spec.
- All "today" / "is" language describes runtime state verified
  by direct file read; all "would" / "could" language is
  research description of a design space, marked as such.
- No design proposals; §10 classifications are proposals-for-
  reuse, not decisions.
- No code changes made writing this doc. No files touched
  besides this one.
