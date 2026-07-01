---
title: "Authority Enforcement Design Space — Architectural Discovery (research only)"
status: draft
session: 1272
date: 2026-06-30
mission_type: design_space_research
authority: |
  Evidence-only research. No runtime changes. No PRs. No migrations.
  No model definitions. No final API design. No implementation plan.
  No decision on which mapping option, which boundary, which mode,
  which precedence policy. This doc enumerates the design space so
  a downstream design-with-Chris-gate mission can consume it. Symbol
  Mapping (S1270) and Actor Attribution (S1271) are INPUT premises,
  not solved here. The three actor roles — executor_actor,
  sponsor_actor, principal_user — are kept separate throughout;
  collapsing them is anti-pattern per S1271 F11.
companion_docs:
  - docs/research/symbol_mapping_architecture.md
  - docs/research/actor_identity_attribution_architecture.md
  - docs/research/governance_authority_evolution.md
  - docs/research/employee_os_collaboration_patterns.md
  - docs/research/employee_os_communication_substrate_audit.md
  - docs/research/employee_os_communication_protocol_sketch.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/EMPLOYEE_OS_PRIMITIVES.md
  - docs/handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md
verifier_loop: |
  Five parallel Explore sub-agents produced evidence reports:
  (1) enforcement-inputs inventory (24 primitives classified;
      RUNTIME-VERIFIED / OBSERVATION-ONLY / ASPIRATIONAL / UNKNOWN
      + 8 gap categories); (2) boundaries × modes cross-product
      (17 boundaries × 12 modes = 204-cell matrix); (3) AuthorityLevel
      semantics research (4 levels × 4 interpretations each) +
      11 canonical role-scenario walkthroughs; (4) governance-plane
      composition analysis (6 existing composition points + 8 new
      cross-plane questions); (5) consolidated 33-incident historical
      catalog + 15 anti-patterns + 15 prerequisites with dependency
      graph.
  Load-bearing structural claims spot-verified by Claude via direct
  Grep/Read against source before drafting. Five verifications:
  (a) LLMEnforcer.enforce_real_ai at core/llm_enforcer.py:139;
      budget_freeze_active check at lines 200-221 with critical
      purposes {governance, auth, incident_response, pa_chat} +
      PersonalAssistant agent exempt; fail-open pattern at 237-238
      (`except Exception: pass  # Never block LLM calls due to
      budget check errors`).
  (b) HumanAttentionLifecycleService._auto_approve_low_risk_items
      at core/services/human_attention_lifecycle.py:223 (invoked
      from beat task at line 122); LOW_RISK_SOURCES = 5 entries
      (spider_insight, content_review, blog_review, trend_analysis,
      observation) at lines 63-69; AUTO_APPROVABLE_TYPES = 5 entries
      (content, insight, observation, analysis, suggestion) at lines
      72-78.
  (c) KillSwitch reads exist (5 sites: intelligence.py:1569,1717;
      governance.py:2192,2370,2508) but ALL are management/cleanup
      contexts (status listing at 2192, get-for-deactivate at 2370,
      expire loop at 2508, TTL cleanup at intelligence.py:1569,1717)
      — NOT dispatch enforcement. S1269 F2 "KillSwitch is
      write-only" stands.
  (d) MissionRunner._emit_authority_contract_event at
      mission_runner.py:835-900 iterates authority.items() at line
      870 for level_counts; explicit code comment at 897-899:
      "Enforce-mode requires future symbol mapping (S1264 discovery)."
  (e) AuthorityLevel enum runtime consumers: 1 grep hit for
      `.EXECUTE.value / .OBSERVE.value / .RECOMMEND.value /
      .PROHIBITED.value` outside jobs.py contract declarations —
      mission_runner.py:864-867 (shape-counter only). Zero
      code paths branch on AuthorityLevel values.
  Runtime-anchor count conflicts resolved in favor of
  PLATFORM_INVENTORY per DOC_LIFECYCLE §2c where quoted.
  Independent SIGN review by Rigby complete (S1272 PA conversation
  pa-cbcc410b32714f60): **SIGN-with-edits**. Rigby overall
  confidence: Medium. All 8 must-fix edits folded:
  (1) §3 gained 3 first-class boundaries — WebSocket consumer /
      channel-layer handler (row 18), Fleet internal API /
      service-to-service ingress (row 19), Spider run boundary
      (row 20). §3 intro + Exec Summary + §15.1 count updates to
      "20 candidate layers" throughout. Cross-tab matrix note
      added at §4.4 acknowledging boundaries 18-20 are not yet
      in the 204-cell matrix and sketching their approximate
      mode-compatibility.
  (2) §9.0 got a neutrality guardrail — "Comparatives describe
      axes; they are not endorsements."
  (3) §9.1 (Option A) + §9.2 (Option B) got explicit annotation-
      burden / signal-quality-maintenance failure-mode entries
      naming step-declaration drift and tool-schema drift as
      primary risks.
  (4) §9.6 (Option F) got explicit "policy ossification /
      precedence lock-in" risk — codified precedence contracts
      retroactively invalidate audit interpretations if changed.
  (5) §8.4 cluster conclusion rephrased — "all enforce-mode
      prevention options are blocked absent Symbol Mapping;
      audit/warn modes remain partially valuable" (was
      overgeneralized "all modes equally blocked"). S1264 named
      as the standing counter-example.
  (6) §10 gained a Tier-0 hazards callout at section head naming
      #1 (blocking all model writes), #8 (enforcement before
      symbol mapping), and #15 (silent enforcement) as
      disproportionately-high-blast-radius patterns. Explicitly
      framed as incident-risk callout, not preference ordering.
  (7) §6.1 gained a "rule of thumb — which boundary naturally
      knows which role" paragraph naming HTTP → principal_user,
      beat → sponsor_actor=system, Celery → executor_actor
      inherited + principal_user dropped, Step.fn → all roles
      lost, Fleet → own executor_actor via app_slug.
  (8) §14 head gained a P0/P1/P2 semantics note — "reflects
      dependency and uncertainty reduction, not preference for
      any design option." §14.2 (Actor Role Propagation Design)
      split into (i) role schema + propagation contract
      (parallel-safe with §14.1) and (ii) implementation across
      boundaries (dependency-blocked). §14.2 remains P1 overall.
  Rigby SIGN-clean on: F8 fail-open precedent framing + §10
  anti-pattern framing (strongest finding); §14 ordering
  (P0 Symbol Mapping → P1 Actor Role Propagation + Authority
  Enforcement Design Decision → P2 Cross-Plane deferred);
  neutrality language on 6 options (no accidental
  recommendations found); actor role vocabulary usage.
owner: claude (drafted S1272) + rigby (independent pressure-test SIGN review, S1272)
---

# Authority Enforcement Design Space — Architectural Discovery

> **What this is.** The design-space research that must precede any
> enforce-mode PR. Symbol Mapping Architecture (S1270) answered
> "WHAT action happened"; Actor Attribution Architecture (S1271)
> answered "WHO acted"; this doc asks: given both prereqs are
> shipped as research, what are the possible ways the platform
> could eventually decide whether an actor was allowed to perform
> a mapped action? Built from direct file:line evidence + five
> parallel sub-agent sweeps + spot verification.
>
> **What this is not.** A design. A decision. A PR sketch. A
> recommendation to pick one option, one boundary, one mode, one
> plane-precedence rule. The options in §9 are a *design space*,
> not a design. The findings in §12 are *architectural
> observations*, not resolutions. Chris gates every downstream
> design decision. Per the maintenance rules in
> ARCHITECTURE_INDEX.md §9 STAGE 2 pacing note, this is the first
> research mission that contains design content — but the design
> content is enumeration of options, not selection among them.

---

## 1. Executive Summary

Authority enforcement asks: **was that actor allowed to perform
that mapped action in that context?** Answering it requires
composing three primitives:

- **Symbol Mapping** (S1270) — bind action_class strings to
  runtime symbols. 5 options; 0 selected.
- **Actor Attribution** (S1271) — resolve three separate roles:
  **executor_actor** (who ran the code), **sponsor_actor** (who
  authorized), **principal_user** (which User owns the row). 22
  attribution surfaces; 13 Explicit / 9 weaker.
- **Enforcement Primitive** — the layer + mode + plane-composition
  policy that turns "WHAT + WHO" into "ALLOW or BLOCK." This is
  what S1272 scopes.

### The design space in one paragraph

The platform ships **24 enforcement-adjacent inputs** across four
governance planes (§2): 13 RUNTIME-VERIFIED, 7 OBSERVATION-ONLY, 3
ASPIRATIONAL, 1 UNKNOWN, plus 8 GAPS. It has **20 candidate
enforcement boundaries** (§3; 17 from sub-agent 2 sweep + 3
Rigby SIGN additions: WebSocket, Fleet, Spider) and
**12 enforcement modes** (§4).
The cross-product (204 cells) is populated with ~156 mechanical
compatibilities. **Six design options (A-F)** emerge naturally
from this space (§9); each has distinct reuse footprint,
implementation risk, rollback story, and coverage of the
33-incident historical catalog (§8). This doc does not choose
among them.

### The five planes of the gap

1. **Vocabulary/input plane.** Authority speaks in 57 unique
   `action_class` strings (S1270 §2). Zero runtime surfaces
   carry that vocabulary (S1270 F2). The `AuthorityLevel` enum
   has exactly **one runtime consumer** — `mission_runner.py:864-867`
   — and that consumer is a **shape-counter, not a
   decision-maker** (§5.3 evidence).
2. **Boundary plane.** 20 candidate layers exist (§3) where an
   authority check *could* fire, but structural drop points from
   S1271 F6 (HTTP→Celery, MissionRunner config→OpsRun,
   MissionRunner→Step.fn) mean some boundaries permanently lack
   the signals a check would need. **Layer choice is not free.**
3. **Mode plane.** 12 modes span observe-only through
   freeze-platform (§4). Existing precedents cover 8 modes;
   4 (defer-mission, freeze-queue, degrade-mission-evidence at
   step scope, retro-audit at authority scope) lack production
   analogs.
4. **Plane-composition plane.** The 4 governance planes
   (autonomy / authority / budget / human) do not compose today
   (S1269 F1). Only **one cross-plane touch** exists (autonomy →
   budget one-way sync at `governance.py:2285-2322`); every
   other cross-plane interaction is silent independence. Adding
   authority enforcement introduces **8+ new composition
   questions** (§7.5) with no precedent to inherit.
5. **Prereq plane.** 15 prerequisites gate any enforce-mode ship
   (§11). Critical path: Symbol Mapping (S1270 option choice) →
   evidence event schema → violation event schema → fallback
   behavior → enforcement layer choice → test coverage → rollback
   → per-employee opt-in → metrics window → trust threshold →
   false-positive threshold. **None of the 15 is currently
   satisfied in full**; most are partial.

### Major findings

**F1 — AuthorityLevel has exactly one runtime consumer, and it's a shape-counter.**
`mission_runner.py:864-867` accumulates `level_counts` by
iterating `authority.items()` — no code path branches on a
specific level value. The 4-member enum (OBSERVE / RECOMMEND /
EXECUTE / PROHIBITED at `jobs.py:41-52`) is **policy metadata
today, not enforcement metadata**. Any enforcement design must
introduce the level → decision binding from scratch.

**F2 — Existing enforcement precedents cover 8 of 12 modes.**
Per sub-agent 5 §H: warn-mode (S1264
`authority_contract_observed`), soft-fail (LLMEnforcer ROI
throttle), hard-block (AssistantProfile TOOL_PERMISSION_DENIED),
require-approval (HumanAttentionItem +
OrchestrationApprovalGate), pause-employee (AgentControlEntry
block), freeze-platform (`GovernanceState.mode='freeze'`),
retro-audit (Bug Triage step 4 aggregation), observe-only
(generic `OpsRunEvent(info)`). Modes without production analog:
defer-mission (Celery retry ≠ mission-level defer), freeze-queue
(new primitive needed), degrade-mission-evidence at step scope
(partial), retro-audit at authority-violation scope (not yet).

**F3 — Every existing enforcement gate uses a different vocabulary.**
Per sub-agent 1 §E scope breakdown: `AssistantProfile.allowed_tools`
is per-*human*; `LLMEnforcer.check_budget` is per-*platform*
(scoped by task_type + agent exemption);
`GovernanceState.mode='freeze'` is per-platform (with declared
but never-read per-agent/desk scopes); `messaging_tool.send_message`
guard is per-tool; DRF `IsAuthenticated`/`IsAdminUser` is
per-user-role. **No existing gate reads `JobContract.authority`**
(S1269 F3). Any authority enforcement is a new vocabulary that
does not inherit precedent semantics.

**F4 — 4 governance planes do not compose; adding authority is a 5th surface.**
Per S1269 F1 + sub-agent 4 §G: only **1 cross-plane composition
point** exists today (autonomy → budget one-way sync). Sub-agent
4 §C enumerates **8 new composition questions** authority
enforcement would introduce (authority × autonomy priority,
authority × budget layering order, RECOMMEND-triggered HAI
auto-creation, authority × KillSwitch precedence, freeze × HAI
auto-approve, etc.). None have current-state answers.

**F5 — S1271 F6 drop boundaries constrain enforcement layer choice.**
Per sub-agent 2 §G: three structural drop points from S1271
disable authority checks at boundaries 7, 9, 10 (step-function
closure, async task without mission context, signal handler
without request context). This is not a bug — it's an
architecture constraint that any layer-choice must respect.

**F6 — 33 historical incidents; the biggest cluster is "authority mapping gap" itself.**
Per sub-agent 5 §G cross-catalog overlap: **7 incidents** (I-S1,
I-S2, I-S3, I-G1, I-A9, I-A10, I-C12) collapse to a single root
cause — S1264's discovery that `JobContract.authority` policy
strings don't bind to runtime symbols. This is what S1270 was
scoped to close. **Every enforcement mode benefits equally from
closing it; every mode is equally blocked without it.**

**F7 — Mode effectiveness rank does not translate to mode preference.**
Sub-agent 5 §B ranks modes by cross-incident coverage:
warn-mode (94%), observe-only (91%), retro-audit (88%), soft-fail
(88%), hard-block (76%). **This is a coverage metric, not a
recommendation.** A mode that covers 94% of incidents while
producing 30% false-positive rate is worse than a mode that
covers 30% at 0% false-positive rate. §7-effectiveness ranking
must not be read as a preference ranking.

**F8 — LLMEnforcer's fail-open pattern is precedent-setting.**
Direct verification at `llm_enforcer.py:237-238`: `except
Exception: pass  # Never block LLM calls due to budget check
errors`. The budget gate — the closest existing analog to
authority enforcement — **fails open** on any internal error.
Any authority enforcement design must decide fail-open vs.
fail-closed and cite a rationale.

**F9 — Symbol Mapping choice constrains enforcement mode choice.**
Per sub-agent 2 §D: Option E (evidence-only) is compatible with
only 4 of 12 modes (observe-only, warn-mode, degrade-evidence,
retro-audit). Options A/B/C/D are compatible with all 12.
Enforcement design cannot be scoped independently of Symbol
Mapping option choice.

**F10 — Actor role composition determines mode preconditions.**
Per sub-agent 2 §E: modes requiring only executor_actor
(warn-mode, soft-fail, degrade-evidence) can ship without full
actor resolution. Modes requiring sponsor_actor (hard-block for
delegation chains, pause-employee) or all three (require-approval,
retro-audit) presuppose S1271's role vocabulary is fully wired.
**Enforcement mode selection is downstream of Actor Attribution
implementation.**

**F11 — The 15 prerequisites form a DAG, not a checklist.**
Per sub-agent 5 §F: critical path is Symbol Mapping → Evidence
Schema → Violation Event Schema → Fallback → Enforcement Layer →
Test Coverage + Human Review → Rollback → Per-Employee Opt-In →
Metrics Window → Trust Threshold + False-Positive Threshold.
Sequential completion required; parallel work is limited to
Cross-Plane Composition (deferred) and Mode Granularity (design
question).

### Overall observation

**Enforcement is not a feature that ships in one PR.** It is a
composite primitive that ships in stages: Symbol Mapping choice
first (S1270 §11.1 Option Selection Design), then Actor
Attribution wiring (S1271 §13.1 or implicit), then per-employee
warn-mode graduation, then enforcement-layer implementation with
opt-in, then metrics and threshold policies. This doc scopes the
design space each stage will consume; **it does not pick a
stage's answer.**

Per §14: the recommended next research mission is **Symbol
Mapping Option Selection Design** (S1270 §11.1 already named
this) — because F9 + F11 both make it the critical-path
predecessor to every enforcement design decision.

---

## 2. Current Enforcement Inputs

Every input the platform currently has that a future enforcement
primitive could read. Per sub-agent 1's direct-Grep inventory of
24 categories from the mission spec.

### 2.1 Full inventory

Per sub-agent 1 §A table. Consolidated view:

| # | Input | Type | Consumers | Enforceable today? | Scope | Reliability | Cross-ref |
|---|---|---|---|---|---|---|---|
| 1 | `JobContract.authority` dict (57 unique strings, 68 total) | Declarative | `mission_runner.py:850-874` (shape); `bug_triage.py:396-453` (event read) | Observation-only | Per-employee | RUNTIME-VERIFIED (as data source) | S1270 §2 |
| 2 | `AuthorityLevel` enum (4 members) | Declarative | `mission_runner.py:864-867` (shape-counter) | No — see F1 | Per-action-class | RUNTIME-VERIFIED (as counter) | `jobs.py:41-52` |
| 3 | `JobContract.prohibited_actions` tuple (30 entries) | Declarative | `mission_runner.py:856-861` shape validation | No | Per-employee | RUNTIME-VERIFIED (as data) | S1270 §2.6 |
| 4 | `what_chris_approves` / `what_claude_handles` / `what_i_can_do_alone` tuples | Declarative | (declaration only) | No | Per-employee | ASPIRATIONAL | `jobs.py:152-154, 359-381, 626-655, 933-965, 1154-1172` |
| 5 | `authority_contract_observed` event label | Runtime observation | Written at `mission_runner.py:835-900`; read by `bug_triage.py:396-453` (count-only) | No — see F1 | Per-mission | RUNTIME-VERIFIED (event; not enforcement) | S1264; S1270 F5 |
| 6 | `MissionRunnerConfig.job_contract` | Declarative | Enables warn-mode emission when non-None | Yes (opt-in per employee) | Per-mission | RUNTIME-VERIFIED (gate) | `mission_runner.py:562-572` |
| 7 | `MissionRunnerConfig.auto_emit_verdict` | Declarative | Gates verdict-event emission | Yes (behavioral flag) | Per-mission | RUNTIME-VERIFIED | `mission_runner.py:1128-1145` |
| 8 | `employee_handle` string | Declarative | MissionRunnerConfig.employee_handle; emitted in event detail | Yes (identity input, not gate) | Per-employee | RUNTIME-VERIFIED | S1271 §2, F9 |
| 9 | `runs_as_username` string | Declarative | `_resolve_runs_as_user_id` at `mission_runner.py:1585-1591` | Silent-None on miss | Per-employee (principal_user selector) | RUNTIME-VERIFIED with F3 caveat | S1271 F3, F11 |
| 10 | Actor attribution surfaces (22) | Runtime | Various — see S1271 §3.1 | Depends on surface | Various | 13 Explicit / 9 weaker | S1271 §3.1 |
| 11 | `GovernanceState.mode` (normal/throttle/freeze/safe_mode) | Runtime | 4 production consumers (spiders, signal agg, workspace pipeline, LLMEnforcer via sync) | Yes (freeze / safe_mode enforced) | Per-platform + per-agent/desk (aspirational) | RUNTIME-VERIFIED with F9 caveat | S1269 §2.1, F8 |
| 12 | `GovernanceState.expires_at` / TTL | Runtime | `is_expired` property; `effective_mode` uses it | Yes | Per-platform | RUNTIME-VERIFIED | `models_governance.py:97-107` |
| 13 | `KillSwitch` model (6 targets) | Write-only for dispatch | Write API + status/expiry consumers; **NO dispatch consumers** — verified by grep | No (write-only) | Per-platform, target-scoped | ASPIRATIONAL for enforcement | S1269 F2 |
| 14 | `SystemConfiguration.budget_freeze_active` | Runtime | `llm_enforcer.py:200-221` | Yes (blocks non-critical LLM) | Per-platform | RUNTIME-VERIFIED | S1269 §2.3 |
| 15 | `LLMEnforcer.check_budget()` INLINE gate | Runtime | `llm_enforcer.py:139` (enforce_real_ai) — 3 checks: freeze / downgrade / ROI throttle | Yes | Per-platform (task_type filtered) | RUNTIME-VERIFIED with F8 fail-open caveat | `llm_enforcer.py:200-262` |
| 16 | 12 feature flags (RIGBY_EVENT_INTAKE_ENABLED, MESSAGING_TOOL_ALLOW_SEND, PA_USE_FUNCTION_CALLING, etc.) | Runtime | Various inline checks | Yes (feature-scoped) | Per-tool / per-feature | RUNTIME-VERIFIED | S1269 §2.7 |
| 17 | `AssistantProfile.get_allowed_tools()` per-user allowlist | Runtime | `tool_dispatcher.py:687-720` | Yes (returns TOOL_PERMISSION_DENIED) | Per-human | RUNTIME-VERIFIED | S1271 §7.3, F7 |
| 18 | `AssistantProfile.role` (admin / vip_viewer / customer) | Declarative | Resolves allowed_tools default | Yes | Per-human | RUNTIME-VERIFIED | `models_assistant_profile.py:154-157` |
| 19 | `HumanAttentionItem` model (31 creators) | Runtime observation + input | Multiple; lifecycle service; approval gates; escalations | Yes (indirect gate via lifecycle) | Per-human, per-item | RUNTIME-VERIFIED | S1269 §2.4 |
| 20 | `HumanAttentionLifecycleService` 7-condition auto-approve | Runtime | Beat every 10 min | Yes (auto-approve gate) | Per-human + per-item + confidence | RUNTIME-VERIFIED | `human_attention_lifecycle.py:223-296` |
| 21 | `OrchestrationApprovalGate` bridge | Runtime | Blocks orchestration steps pending approval | Yes | Per-orchestration-step | RUNTIME-VERIFIED with UNKNOWN check_auto_approvals trigger | S1269 §2.4 row 33 |
| 22 | Trust ratio (`derive_status()`) | Derived-on-read | `employee_tool status` action | Not currently a gate | Per-employee + per-job | RUNTIME-VERIFIED (as read) | `status.py:53-251` |
| 23 | `AgentFollowupSubscription` → chat banner | Runtime observation | UNKNOWN specific consumers | Not authority-relevant | Per-execution | UNKNOWN | S1271 §2, entry 23 |
| 24 | Symbol mapping candidates (action_class strings) | **GAP** | Zero runtime surfaces carry action_class metadata | No — see F6 | Per-action-class | NOT ENFORCEABLE without S1270 choice | S1270 F2 |

**Distribution:** 13 RUNTIME-VERIFIED + 7 OBSERVATION-ONLY + 3
ASPIRATIONAL + 1 UNKNOWN = 24. Plus 8 gap categories (§2.3).

### 2.2 Runtime vs. Declarative distribution

Per sub-agent 1 §D:

| Class | Count | Examples |
|---|---|---|
| **Declarative** (loaded at code-import; immutable at runtime) | 8 | `JobContract.authority`, `AuthorityLevel`, `prohibited_actions`, `job_contract` field, `auto_emit_verdict`, `employee_handle`, `runs_as_username`, `AssistantProfile.role` |
| **Runtime — request-time** (read on each dispatch/execution) | 9 | `GovernanceState.mode`, `GovernanceState.expires_at`, `budget_freeze_active`, `LLMEnforcer.check_budget()`, `AssistantProfile.allowed_tools`, `HumanAttentionItem.status`, `OrchestrationApprovalGate.status`, 12 feature flags, `check_retry_budget` |
| **Runtime — periodic** (beat/cron) | 2 | `HumanAttentionLifecycleService` auto-approve; expiry cleanup jobs |
| **Runtime — write-once / event** | 3 | `authority_contract_observed` event; OpsRunEvent audit rows; ChatConversation posts |
| **Derived-on-read** (not stored) | 2 | Trust ratio via `derive_status()`; `GovernanceState.effective_mode` property |

### 2.3 Gap inventory (inputs enforcement would need but doesn't have)

Per sub-agent 1 §C. Eight gaps:

| GAP-# | Missing input | Why needed | Blocked-by prior research |
|---|---|---|---|
| GAP-1 | Runtime binding: action_class → {tool_name, step_name, code_path} | Enforcement cannot route action_class string to code location without this registry | S1270 F2 |
| GAP-2 | Runtime binding: `AuthorityLevel` value → enforcement decision | Enum exists (`.OBSERVE` / `.EXECUTE` / etc.); no code branches on it | F1 above; S1264 §5 |
| GAP-3 | Cross-actor identity resolution function | No canonical function resolves an arbitrary identity string to {executor_actor, sponsor_actor, principal_user} | S1271 §6.4, F6 |
| GAP-4 | Audit-model action_class column | Every audit model (OpsRun, OpsRunEvent, ToolCallRecord, AgentExecution, LLMCallEvent) lacks action_class field | S1270 §3.1; S1271 §8.5 |
| GAP-5 | Delegation chain query | `parent_object_type` exists on some models; no canonical `get_delegation_chain(actor, action)` returns ordered delegators | S1271 §3.5 (partial) |
| GAP-6 | Executor / sponsor / principal role fields on audit models | All audit rows treat actor as single field; no row carries the three roles as separate columns/JSON keys | S1271 §8.5, F11 |
| GAP-7 | KillSwitch dispatch consumer | Write path complete; zero code reads `is_active` before scheduler/queue/agent_family/publishing/outbound/deploys actions | S1269 F2 (spot-verified) |
| GAP-8 | Unified feature-flag runtime check pattern | 12 flags scattered; no unified gate; each read is inline per flag | S1269 §2.7 |

### 2.4 Scope classification

Per sub-agent 1 §E:

- **Per-human** (User-scoped): 4 — AssistantProfile.role,
  .allowed_tools, HumanAttentionItem, HumanPreference
- **Per-employee** (employee_handle-scoped): 5 — JobContract.authority,
  employee_handle, runs_as_username, prohibited_actions,
  Trust ratio (per-job)
- **Per-agent** (agent-scoped): 2 — AGENT_MAP membership,
  WORKSPACE_AWARE_AGENTS
- **Per-tool** (tool-scoped): 3 — messaging_tool guard, 12
  feature flags, per-tool schema access control
- **Per-platform** (global): 4 — GovernanceState.mode (with
  aspirational per-scope), budget_freeze_active, feature flags
  (global), OrchestrationApprovalGate lifecycle service

**Observation:** No existing scope maps 1:1 to
`JobContract.authority`. Authority is per-employee-per-action-class;
no existing gate operates at that granularity. Any enforcement
design must decide whether to add per-employee-per-action gates
or degrade to a coarser scope.

---

## 3. Enforcement Boundary Inventory

20 candidate layers where an authority check could theoretically
fire. Per sub-agent 2 §A. **Rigby S1272 SIGN pressure-test
addition:** rows 18-20 (WebSocket consumer, Fleet internal API,
Spider run) were absent from sub-agent 2's original 17-row
inventory; Rigby flagged these as boundary-completeness gaps
during SIGN review. Adding them here so future readers do not
assume "covered by Option X" for real-time / service-to-service /
spider-ingestion paths.

### 3.1 Boundary table

| # | Boundary | file:line | Identity signal | Action signal | Can prevent? | Existing precedent |
|---|---|---|---|---|---|---|
| 1 | HTTP request auth middleware | `core/auth_middleware.py:563-681` | User from token/session (Strong) | Path prefix (Weak) | Yes (403) | is_staff, is_reviewer, IsAuthenticated |
| 2 | ToolDispatcher.execute() entry (AssistantProfile gate) | `tool_dispatcher.py:687-720` | user_id → profile.role (Strong) | tool_name (Weak — no action_class) | Yes (hard-block: TOOL_PERMISSION_DENIED) | AssistantProfile allowlist |
| 3 | PA tool handler body | `td_handlers_*.py` (per-handler) | Caller context (Strong via dispatch) | `payload['action']` string dispatch (Ambiguous) | Yes (logic branch) | messaging_tool.send_message feature-flag guard |
| 4 | MissionRunner.run() entry (mission startup) | `mission_runner.py` (run method) | employee_handle from config (Strong) | mission_run_kind (Weak — no per-step action) | No (mission already dispatched) | None; warn-mode observation happens after this |
| 5 | MissionRunner preflight — warn-mode | `mission_runner.py:835-900` (`_emit_authority_contract_event`) | employee_handle (Strong) | authority dict keys (available BUT not enforced) | **No — observation only by S1264 decree** | S1264 warn-mode (exact precedent) |
| 6 | Before each Step.fn (step loop) | `mission_runner.py:_run_step` | Mission context (Strong) | step.name only (Weak — no action_class) | Yes (would need `Step.action_classes_invoked` per S1270 Option A) | None |
| 7 | Inside Step.fn body (closure) | Per-job step function body | Closure-only (Weak — invisible to runner) | Implementation-defined | Uncertain — closure opaque to runner | Decorator patterns exist |
| 8 | Celery task dispatch (`.apply_async()` / `.delay()`) | Various dispatch sites | task queue name (Strong); no request.user | Task name (Weak — no action_class) | Yes (conditional enqueue) | CELERY_TASK_ROUTES queue routing |
| 9 | Celery task execution (`@shared_task` entry) | `core/tasks*.py` | task_id + Celery context (Strong); no request.user | Function name (Weak) | Yes (exception raise) | None specifically for authority |
| 10 | Model pre_save / pre_delete signals | Django signal handlers | request.user if in-band; None if beat/async | Model class name (Strong) | Yes (raise ValidationError → transaction rollback) | Signal-handler validation pattern exists |
| 11 | Deliverable status transition | `deliverable_status_signals.py:83-100` | OpsRunEvent.user (Weak — nullable) | old_status → new_status (Strong) | No (transition-in-progress) | Rework detection classification |
| 12 | DirectMessage creation | `models_messaging.py` create sites | sender FK (Strong when non-null); sender_type enum | thread_type + metadata (Weak) | Yes (pre-create validation) | None as authority gate |
| 13 | EventBus.publish() | `services/event_bus.py:137-189` | source string (Weak — arbitrary caller) | event_type enum (Strong) | No (publish always succeeds) | None |
| 14 | LLM call — LLMEnforcer.check_budget INLINE | `llm_enforcer.py:200-262` | agent_name (Weak) | task_type / purpose enum (Weak — no action_class) | Yes (freeze blocks non-critical; ROI throttle degrades) | **Closest precedent for INLINE authority gate** |
| 15 | AgentRouter.route() | `core/agent_router.py` route method | User context (Strong) | agent_name string (Strong via AGENT_MAP) | Yes (agent-not-found exception) | Rigby delegation routing table |
| 16 | HumanAttentionItem decision | `core/views_human_interface.py:84-100` (decide endpoint) | request.user (Strong) | item_id + decision enum (Strong) | Yes (auth-check on item.user) | HAI lifecycle |
| 17 | Post-mission retrospective audit | `core/employees/status.py:53-251` (`evidence_for_mission`); Bug Triage step 4 | employee_handle (Strong from parent OpsRun) | mission_run_kind + verdict enum (Strong) | No (read-only) | Existing evidence chain |
| 18 | WebSocket consumer / channel-layer handler | `core/consumers*.py` (Daphne handlers); channel_layer.group_send sites | request.user via `AuthMiddlewareStack` (Strong when authenticated; AnonymousUser otherwise) | Event `type` string + message payload (Weak — no action_class) | Yes (raise + close connection) | AsyncWebsocketConsumer + JsonWebsocketConsumer permission checks; no authority-specific gate |
| 19 | Fleet internal API / service-to-service ingress | Fleet endpoints (grep for `FleetSignatureAuthentication` at `core/services/fleet_auth_drf.py:65-150`) | `FleetServiceIdentity.app_slug` via HMAC-verified header (Strong — cryptographic) | Endpoint route + payload (Weak — no action_class) | Yes (403 on signature failure; permissive fallback at fleet_auth_drf.py:65-150 sets identity=None) | S1269 §2.5 row 40 FleetSignatureAuthentication |
| 20 | Spider run boundary (spider ingestion + governance mode reads) | `core/tasks_spiders.py:381-398` (freeze/safe_mode check); per-spider handler | `spider_name` + spider run identity (Strong for name; Weak for user attribution — spiders run under `system`) | spider name (Strong); no per-item action_class | Yes (returns `{'skipped': True}` on freeze) | S1269 §2.1 row 5 — spider governance gate |

### 3.2 Identity + action signal quality per boundary

Per sub-agent 2 §C:

**Identity Strong (typed FK or verified):** 1, 2, 6, 8, 9, 10 (if
in-band), 12 (if sender non-null), 15, 16, 17 — **10 of 17**.

**Action Strong (deterministic identifier available):** 10, 11,
15, 16, 17 — only **5 of 17** carry an action signal that would
map cleanly to `JobContract.authority` keys today.

**Symbol-dependent (visible IF a S1270 option ships the metadata):**
6 (Option A step declarations), 3+7+8+10 (Option B/C/D tool /
registry / hybrid), 11+16 (Option B model attribute), 14 (LLM
call metadata attribute).

**Structural blockers per S1271 F6:**
- Boundary 9 (Celery task execution) — request.user lost at
  process boundary
- Boundary 7 (inside step.fn) — closure opaque to runner
- Boundary 10 (background signal handlers) — no request context

These three boundaries **cannot fully attribute** without new
context-plumbing primitives.

### 3.3 Enforcement mode taxonomy (per boundary)

Per sub-agent 2 §B — each boundary supports a subset of the 12
modes. Full 204-cell matrix in §4.4. Summary:

- **Layer 5 (preflight)**: only observe-only + warn-mode +
  retro-audit compatible — S1264 decree preserves warn-mode as
  non-blocking.
- **Layers 1, 2, 15, 16**: hard-block dominant precedent; other
  modes possible but redundant.
- **Layer 14 (LLMEnforcer)**: exact analog for INLINE authority
  gate — fail-open at 237-238 is a design precedent, not just an
  accident.
- **Layer 17 (retro-audit)**: only post-dispatch modes fit —
  observe-only, warn-mode, degrade-evidence, retro-audit.

### 3.4 Layer choice constraints

Per sub-agent 2 §G — three coverage gaps that constrain choice:

1. **Symbol Mapping integration missing at boundaries 3, 4, 5, 6,
   7, 8** — hard-block, soft-fail, require-approval all require
   S1270 option to ship action_class binding.
2. **Actor Attribution resolution missing at boundary 7** — step
   closure prevents any mode from binding the three roles.
3. **Freeze-queue primitive missing** — no `SystemConfiguration
   key=celery_queue_<name>_frozen` pattern exists.

---

## 4. Enforcement Modes

12 modes span the mechanical space from pure observation to
platform-wide freeze. Per sub-agent 2 §B.

### 4.1 Mode taxonomy

| Mode | Definition | Timing | Existing precedent |
|---|---|---|---|
| **observe-only** | Record but do not act; no side-effect | POST-DISPATCH | `OpsRunEvent(info)` timeline capture |
| **warn-mode** | Emit warning event; continue | POST-DISPATCH | `authority_contract_observed` event (S1264) — EXACT precedent |
| **soft-fail** | Record failure; degrade evidence; continue | INLINE | Budget downgrade via ROI throttle (`llm_enforcer.py:242-262`) |
| **hard-block** | Refuse to execute; raise exception or return error | PRE-DISPATCH | `AssistantProfile` TOOL_PERMISSION_DENIED (`tool_dispatcher.py:687-720`); HTTP 403 |
| **require-human-approval** | Pause + create HAI; resume on approval | PRE-DISPATCH (creates HAI); POST-DECISION (resumes) | HAI + `OrchestrationApprovalGate` + `views_human_interface.py:84-100` |
| **degrade-mission-evidence** | Mark OpsRun.summary as degraded but complete | INLINE | `OpsRun.summary[degraded]` flag (partial precedent) |
| **defer-mission** | Delay execution to next cycle with backoff | PRE-DISPATCH | Celery task.apply_async(retry=...) — task-level only; mission-level defer UNKNOWN |
| **pause-employee** | Disable employee's next dispatch (governance action) | PRE-DISPATCH | `AgentControlEntry(status=blocked, ttl_hours=N)` |
| **freeze-tool** | Disable specific tool per feature flag | INLINE | `messaging_tool.send_message` guard; `AgentControlEntry` variants |
| **freeze-queue** | Reject Celery task dispatches to a queue | PRE-DISPATCH | **No precedent** — new primitive needed |
| **freeze-platform** | `GovernanceState.mode=freeze` | PRE-DISPATCH | Existing (4 production consumers) |
| **retrospective-violation-report** | Post-hoc audit + escalation Deliverable | POST-DISPATCH | Bug Triage step 4 aggregation (partial); Deliverable escalation |

### 4.2 Mode → actor role requirements

Per sub-agent 2 §E — which of the three roles (executor_actor,
sponsor_actor, principal_user) each mode requires to be resolved
before it can fire:

| Mode | executor_actor | sponsor_actor | principal_user | Minimum set |
|---|---|---|---|---|
| observe-only | Optional | No | No | None (pre-resolution OK) |
| warn-mode | Yes | No | No | executor_actor |
| soft-fail | Yes | No | No | executor_actor |
| hard-block | Yes | Yes (delegation chains) | No | executor + sponsor |
| require-human-approval | Yes | Yes | Yes | All three |
| degrade-mission-evidence | Yes | No | No | executor_actor |
| defer-mission | Yes | Optional | No | executor_actor |
| pause-employee | No | Yes | No | sponsor_actor |
| freeze-tool | No | Yes | No | sponsor_actor |
| freeze-queue | No | Yes | No | sponsor_actor |
| freeze-platform | No | Yes | Yes | sponsor + principal |
| retrospective-violation-report | Yes | No | Yes | executor + principal |

**Observation:** modes requiring only executor_actor (warn,
soft-fail, degrade-evidence, defer) can ship without full actor
resolution. Modes requiring principal_user or all three
(require-approval, freeze-platform, retro-audit) presuppose S1271
role vocabulary is wired everywhere.

### 4.3 Mode → Symbol Mapping option compatibility

Per sub-agent 2 §D — which of S1270's 5 mapping options
(A steps self-declare / B tool attribute / C hybrid / D central
registry / E evidence-only) each mode is compatible with:

| Mode | Compatible with Option |
|---|---|
| observe-only | A / B / C / D / E — all 5 |
| warn-mode | A / B / C / D / E — all 5 |
| soft-fail | A / B / C / D (not E — no pre-dispatch symbol) |
| hard-block | A / B / C / D (not E) |
| require-human-approval | A / B / C / D (not E) |
| degrade-mission-evidence | A / B / C / D / E — all 5 |
| defer-mission | A / B / C / D (not E) |
| pause-employee | A / B / C / D (not E) |
| freeze-tool | A / B / C / D (not E) |
| freeze-queue | A / B / C / D (not E) |
| freeze-platform | A / B / C / D / E — all 5 (governance level, not action level) |
| retrospective-violation-report | A / B / C / D / E — all 5 |

**Observation:** Option E (evidence-only) constrains the mode
choice to 5 (observe-only, warn-mode, degrade-evidence,
freeze-platform, retro-audit). Options A/B/C/D preserve all 12
mode choices. **Option E is the highest-flexibility mode
enabler ONLY among post-dispatch modes**; it disables every
pre-dispatch mode.

### 4.4 Boundary × mode compatibility matrix (204 cells)

Per sub-agent 2 §C. Summary counts (mechanical fit only —
excludes real-world design considerations):

| Total cells | ✓ (mechanical fit) | ✗ (structural incompatibility) | ? (depends on other choice) |
|---|---|---|---|
| 17 × 12 = 204 | ~130 | ~50 | ~24 |

**Rigby S1272 SIGN note:** the 204-cell matrix reflects
sub-agent 2's original 17-boundary sweep. Boundaries 18-20
(WebSocket, Fleet, Spider — added per §3 SIGN pressure-test)
are **not yet cross-tabulated** against the 12 modes. A future
research pass or design mission should extend the matrix to
the full 20-row form. Approximate additions:
- Boundary 18 (WebSocket): PRE-DISPATCH modes (hard-block via
  raise + close) mechanically fit; INLINE modes (soft-fail,
  degrade-evidence) fit if the handler is instrumented; freeze
  modes fit (freeze-tool for a specific consumer, freeze-queue
  for a channel_layer group). Retro-audit fits.
- Boundary 19 (Fleet ingress): all PRE-DISPATCH modes fit
  (fleet HMAC verification is exact analog); freeze-tool
  (per-app_slug) + freeze-queue (per-fleet-endpoint) fit; retro
  fits.
- Boundary 20 (Spider run): PRE-DISPATCH modes fit (already
  wired to freeze/safe_mode gate); soft-fail + degrade-evidence
  fit for partial-ingestion cases; retro fits (Bug Triage-adjacent).

**Highest-flexibility boundaries** (compatible with most modes):
Boundary 3 (PA tool handler body), Boundary 4 (MissionRunner.run
entry), Boundary 6 (before Step.fn), Boundary 14 (LLM call).

**Lowest-flexibility boundaries:** Boundary 5 (preflight, S1264
decree: only observation modes), Boundary 13 (EventBus.publish,
no veto path), Boundary 7 (closure opaque).

Full matrix inside sub-agent 2's report; not replicated here to
avoid drift with prior research.

### 4.5 Existing production precedents

Per sub-agent 2 §F, cross-referenced with sub-agent 5 §H:

**Modes with production analogs (8):**
- observe-only: `OpsRunEvent(info)` timeline capture
- warn-mode: `authority_contract_observed` (S1264) — exact
  precedent
- soft-fail: LLMEnforcer ROI throttle → cheaper model
- hard-block: AssistantProfile TOOL_PERMISSION_DENIED; HTTP 403
- require-approval: HAI + OrchestrationApprovalGate + decide
  endpoint
- pause-employee: AgentControlEntry(status=blocked)
- freeze-platform: GovernanceState.mode='freeze' (4 consumers)
- retro-audit: Bug Triage step 4 aggregation (authority-adjacent)

**Modes without production analog (4):**
- defer-mission at mission-level (Celery retry is task-level only)
- freeze-queue (no `celery_queue_<name>_frozen` pattern)
- degrade-mission-evidence at step scope (only partial via
  `OpsRun.summary[degraded]`)
- retrospective-violation-report at authority-violation scope
  (Bug Triage aggregates contract observations, not violations)

### 4.6 The fail-open precedent

Verified at `core/llm_enforcer.py:237-238`:

```python
try:
    # ... budget flag check + downgrade check ...
except Exception:
    pass  # Never block LLM calls due to budget check errors
```

The closest existing analog to authority enforcement — the
LLMEnforcer budget gate — **fails open** on any internal error.
Any authority enforcement mode design must decide fail-open vs.
fail-closed and cite a rationale. Per F8:

- **Fail-open** (LLMEnforcer pattern): if the check itself
  errors, allow the action. Rationale: infrastructure reliability
  > policy enforcement. Risk: silent enforcement gaps.
- **Fail-closed**: if the check errors, block the action.
  Rationale: policy enforcement > infrastructure reliability.
  Risk: infrastructure hiccups cascade into blocked missions.

This doc does not choose. But every mode selection carries an
implicit fail-open/closed default.

---

## 5. AuthorityLevel Semantics

Per sub-agent 3 Part A — for each of the 4 levels, 4 possible
interpretations enumerated without ranking.

### 5.1 Level distribution across the 68-entry corpus

Per S1270 §2.3 counts, cross-verified:

| Level | Count | Percentage | Example strings |
|---|---|---|---|
| **PROHIBITED** | 32 | 47% | `modify_docs_files`, `open_pull_request`, `delete_database_rows`, `execute_arbitrary_code` |
| **EXECUTE** | 17 | 25% | `run_docs_cascade_commands`, `generate_audit_report`, `synthesize_decision_card` |
| **OBSERVE** | 13 | 19% | `run_drift_observation`, `check_env_config_status`, `read_platform_readiness_telemetry` |
| **RECOMMEND** | 6 | 9% | `broken_link_sweep`, `recommend_remediations`, `recommend_daily_priorities` |
| **Total** | 68 | 100% | Across 4 employees |

### 5.2 Four interpretations per level

Per sub-agent 3 §A.3 — each level admits multiple defensible
enforcement interpretations, with different risks.

#### OBSERVE (13 entries)

**Interpretation A — Read-only DB access; no writes anywhere.**
Permits: `SELECT` queries; log/event queries. Blocks: any
INSERT/UPDATE/DELETE. Risk: conflates "observation" with
"read-only"; in-memory caches / temp files slip through.

**Interpretation B — Read-only + can emit observation events (OpsRunEvent) but not user-facing artifacts.**
Permits: OpsRunEvent audit; populate `summary_acc`. Blocks:
Deliverable creation, DirectMessage send, user-visible writes.
Risk: OpsRunEvent has no `agent_name` field (S1271 gap); which
writes count as "observation" is undefined.

**Interpretation C — Read-only for the specific action_class; other actions unrestricted.**
Permits: any operation NOT bound to the specific action_class.
Blocks: only the action_class labeled OBSERVE. Risk: Symbol
Mapping (S1270) required for granularity; per S1270 F1 there are
57 unique strings but 88% employee-specific. No cross-action
scope defined.

**Interpretation D — Read-only with mandatory reporting to audit trail.**
Permits: reads + automatic audit-trail entries. Blocks: writes
bypassing the audit gate. Risk: no audit gate exists; risk of
silent reads that don't log.

**Cross-interpretation risk:** OBSERVE semantic drift between
"data-layer read" (A/D) and "action-class scope" (C) is
fundamental. Choice affects which interpretation of "action"
enforcement even makes sense.

#### RECOMMEND (6 entries)

**Interpretation A — Propose action; human approval required.**
Permits: create Deliverables with `status='draft'` or
`review_required`; emit recommendation events. Blocks:
transition to `ready` / `completed` without approval. Risk:
current `deliverable_factory.create_escalation_deliverable`
policy uses `force_ready=True` (per S1270 §7.3); conflicts with
approval-required interpretation.

**Interpretation B — Report to escalation surface; delegate decision to higher-authority human.**
Permits: write Deliverables to workspace; post to PA chat as
summary. Blocks: binding decisions (schedule change, config
modify, close issue). Risk: escalation path not durable (S1271
F6 — identity drops at HTTP→Celery); Chris's identity in PA
chat context is not persisted on Deliverable row.

**Interpretation C — Emit recommendation + trigger automatic escalation review queue.**
Permits: Deliverable with `publish_intent='escalation'`;
auto-routes to review queue. Blocks: mark-complete until
reviewed. Risk: no `pending_review` state defined on Deliverable
per S1271 §3.1; no automatic review queue exists.

**Interpretation D — Constrained-scope autonomy: act on low-risk actions; escalate high-risk.**
Permits: act autonomously on actions marked low-risk. Blocks:
act on actions marked `high_risk=true` in contract. Risk:
authority dict is `dict[str, str]`; no risk-rating field exists.
Who determines risk?

**Cross-interpretation risk:** RECOMMEND is the weakest semantic
commitment. Three interpretations (A, B, D) are "propose +
escalate" but differ on *who decides*. `force_ready=True` in
current escalation flow contradicts A.

#### EXECUTE (17 entries)

**Interpretation A — Act autonomously within the scope of the action_class.**
Permits: perform action without approval; emit completion
evidence. Blocks: actions NOT in the authority dict (implicit
PROHIBITED). Risk: 57 authority strings map to ≥7 runtime
identifier families; scope highly fragmented.

**Interpretation B — Act autonomously; emit evidence + telemetry; must certify completion.**
Permits: writes to OpsRun / Deliverable / OpsRunEvent /
DirectMessage. Blocks: actions requiring approval (RECOMMEND /
PROHIBITED). Risk: `auto_emit_verdict=True` (default at
`mission_runner.py:589`) means EXECUTE actions auto-certify;
Bug Triage's `False` opt-out (S1267) makes its EXECUTE weaker.

**Interpretation C — Delegate to step.fn implementation; step.fn honors the level.**
Permits: whatever step chooses. Blocks: nothing (level advisory).
Risk: step.fn receives OpsRun only (S1271 F6-c); no JobContract
or authority passed. Self-gating requires step to look up
contract from global registry.

**Interpretation D — Boundary-respecting autonomy: writes to outcomes in scope; not beyond scope.**
Permits: Deliverable in workspace; modify docs within workspace
scope. Blocks: cross-workspace operations. Risk: workspace
context is lost across delegation (per S1234 PR #2610).

**Cross-interpretation risk:** EXECUTE is the strongest semantic
commitment but broadest risk surface. `auto_emit_verdict=True`
makes EXECUTE weaker as a control. Delegation interpretation C
leaks because step.fn can't access authority metadata.

#### PROHIBITED (32 entries)

**Interpretation A — Hard block; attempt raises exception.**
Permits: nothing. Blocks: any operation labeled PROHIBITED.
Risk: hard-block requires PRE-DISPATCH enforcement; only
warn-mode exists today.

**Interpretation B — Soft block; action possible but flagged as violation + escalated.**
Permits: write violation evidence. Blocks: user-visible success.
Risk: violation detection requires Symbol Mapping + audit
gating; post-action allows damage before detection.

**Interpretation C — Implicit deny; action simply not wired (no tool/step/task).**
Permits: nothing (doesn't exist). Blocks: implicitly.
Risk: proving "action X does not exist" is hard; if an action is
added later (e.g., `open_pull_request` tool), is it
automatically PROHIBITED?

**Interpretation D — Orthogonal marker; not sequenced with the other three.**
Permits: default EXECUTE + explicit PROHIBITED overrides.
Blocks: only explicitly-listed actions. Risk: two-tier authority
model (default + exceptions); schema change required.

**Cross-interpretation risk:** PROHIBITED ambiguous between
hard-block (A) and soft-block (B). Implicit denial (C)
unverifiable without complete action inventory. Orthogonality
(D) vs. ordering (A-C) is fundamental design choice unresolved.

### 5.3 The current runtime consumer situation

Per sub-agent 3 §B, verified independently:

**AuthorityLevel value references outside `jobs.py` contract
declarations:** 1 site — `mission_runner.py:864-867` (shape
counter, verified). No code path branches on
`AuthorityLevel.EXECUTE` / `.OBSERVE` / `.RECOMMEND` /
`.PROHIBITED` value.

**Authority dict iteration sites:** 1 — `mission_runner.py:870`
(`for action_class, level_value in authority.items():` —
counting only).

**Test-only references:** ~11 files, ~60 lines — assertions on
level counts, not enforcement behavior.

**Conclusion:** `AuthorityLevel` is **policy metadata only
today**. Zero enforcement code reads it. Any design must
introduce the first decision-making consumer.

### 5.4 Level ordering questions

Per sub-agent 3 §A.4:

- **Semantic ordering:** OBSERVE < RECOMMEND < EXECUTE (power
  ordering) is defensible.
- **PROHIBITED orthogonality:** PROHIBITED overrides all others
  but is not sequenced. Is it a separate tier or an annotation?
  UNKNOWN.
- **Mutual exclusivity per action_class:** Yes today —
  `authority` dict stores one level per key.
- **Compound authority:** No evidence for same action_class
  carrying different levels in different contexts. Future
  design question.

### 5.5 Cross-level relationships (unimplemented)

Per `mission_runner.py:895-899` explicit comment: **enforcement
does not implement relationships between levels.** No
escalation rule ("RECOMMEND must escalate to EXECUTE-level
actor"), no scope rule ("EXECUTE within workspace; PROHIBITED
across"), no chaining ("OBSERVE→RECOMMEND→EXECUTE with human
approval between each step"). Any design introduces these.

---

## 6. Actor Roles and Enforcement

Per sub-agent 3 Part C — 11 canonical scenarios × 3 roles ×
audit path.

### 6.1 The three-role vocabulary (S1271 §8.5 recap, NOT collapsed)

Per S1271 §8.5:
- **executor_actor** — runtime entity that performed the operation
- **sponsor_actor** — entity that authorized or requested the action
- **principal_user** — UnifiedUser for ownership / permission / row-level access

**Discipline reminder:** these are **never collapsed** in this
doc. Any scenario walkthrough that reports a single "actor" is
under-specified.

**Rule of thumb — which boundary naturally knows which role
(Rigby S1272 SIGN edit).** Role separation is not merely a
naming convention; it is a **propagation constraint** that
different boundaries satisfy differently:

- **HTTP request boundary** tends to know **principal_user**
  (via `request.user`) and often **sponsor_actor** (same
  User for authenticated calls). **executor_actor** is
  usually the tool / agent / handler dispatched *from* the
  request, and is derived downstream.
- **Beat / scheduler boundary** tends to know **sponsor_actor
  = "system"** (the beat mechanism). **executor_actor** is the
  employee / task the beat fires. **principal_user** is the
  `runs_as_username` configured on the employee (usually
  `chris` today).
- **Celery task boundary** tends to inherit **executor_actor**
  from the task kwargs but **drops principal_user unless
  explicitly propagated** (per S1271 F6-a drop boundary).
- **Step.fn boundary** (inside MissionRunner) tends to lose
  all three roles from the caller signature; only mission
  identity survives (per S1271 F6-c).
- **Fleet boundary** knows the fleet's own **executor_actor**
  (via `FleetServiceIdentity.app_slug` HMAC) but tells you
  nothing about the ultimate sponsor / principal upstream of
  the fleet call.

**Implication for enforcement design.** Modes requiring only
`executor_actor` (warn-mode, soft-fail) fit boundaries where
the executor is locally known. Modes requiring
`principal_user` (require-approval, retro-audit) require
explicit propagation for async paths — this is why S1271 F6
drop boundaries constrain layer choice (F5 in §12).

### 6.2 Scenario table (11 canonical scenarios)

Per sub-agent 3 §C.2, consolidated:

| Scenario | executor_actor | sponsor_actor | principal_user | Enforcement point today | Evidence durability | Drop boundaries crossed |
|---|---|---|---|---|---|---|
| 1. Beat-fired Rigby docs cascade | `rigby` (AIEmployee.handle) | `system` (beat mechanism) | `chris` (runs_as_username) | None | OpsRun.triggered_by (mech) + summary JSON | F6-a, F6-b, F6-c |
| 2. Chris runs `employee_tool run_now` via PA | `rigby` | `chris` (User via auth token) | `chris` | AssistantProfile.get_allowed_tools() (tool-level, not authority) | OpsRun.triggered_by='pa_tool'; sponsor='chris' NOT persisted | F6-a (task boundary); F6-b, F6-c |
| 3. Rigby dispatches Claude Code | `claude-code` OR `rigby` (delegator vs. executor — S1271 F4 ambiguity) | `rigby` (delegator) | `chris` (inherited) | UNKNOWN — no code path found | AgentExecution.owner_agent (ambiguous) | Delegation chain not modeled |
| 4. Claude Code writes deliverable | `claude-code` (ambiguous) | `claude-code` + `chris` (indirect) | `chris` (ChatConversation.user FK) | UNKNOWN — no authority check on Deliverable creation | Deliverable.agent_name (ambiguous per S1271 F4) | None explicit; ambiguity dominates |
| 5. Chief of Staff produces morning brief | `chief-of-staff` (handle) — but agent_name field records display name (S1263 drift) | `system` (beat) | `chris` (runs_as_username) | None | Deliverable.agent_name (drift risk) | F6-a, F6-b, F6-c |
| 6. Bug Triage reads other employees' OpsRun rows | `bug-triage` | `system` (beat) | `chris` | OBSERVE authority (unimplemented) | OpsRunEvent (no actor field — S1271 §3.1 row 12 Missing) | F6-c (step reads OpsRun directly) |
| 7. Platform Auditor recommends remediation | `platform-auditor` | `system` (beat) | `chris` | RECOMMEND escalation gate (unimplemented) | Deliverable (principal recorded; sponsor missing) | F6-a (PA escalation posts context loss) |
| 8. PA tool runs from chat (`employee_tool` action) | Same as scenario 2 | `chris` | `chris` | AssistantProfile.get_allowed_tools() (tool-level) | Same as scenario 2 | F6-a |
| 9. Management command runs locally | `rigby` (hardcoded) | **UNKNOWN** (Django mgmt has no request.user) | `chris` (runs_as_username in config) | None (no auth context) | OpsRun.triggered_by='management_cmd'; operator identity lost | Sponsor identity permanently dropped |
| 10. HTTP API request by staff user | View / handler / spawned task | `request.user` (staff User) | `request.user` | DRF permission_classes (orthogonal to authority) | Depends on task spawning | F6-a if task spawned |
| 11. System / beat job creates DirectMessage | `system` or `rigby` (sender_type enum) | Implicit (no sponsor for system messages) | `chris` (if step.fn resolves runs_as_username) | None | DirectMessage.sender=None; sender_type is only actor marker | F6-b, F6-c |

### 6.3 Cross-surface role drift

Per sub-agent 3 §C.3 — for every attribution surface receiving a
row in each scenario, at least one of the three roles is
Ambiguous, Missing, or Inferred-from-JSON. Per S1271 F2 this is
pervasive.

**Most common role loss:** principal_user missing (S1271 F1:
OpsRun has no user FK). Recovery requires JSON parsing.

**Most damaging role loss:** sponsor_actor rarely recorded (only
`OpsRun.triggered_by` mechanism string; not the actual human
sponsor). Scenarios 1, 5, 6, 7, 9, 11 all report sponsor_actor
as `system` or `UNKNOWN`.

**Semantic gap:** delegator vs. executor distinction (S1271 F4)
breaks on `Deliverable.agent_name`, `ToolCallRecord.agent_name`,
`LLMCallEvent.agent_name`, `AgentExecution.owner_agent` — all
single CharFields.

### 6.4 Ambiguity resolution

Per sub-agent 3 §C.4, three scenarios yield multiple defensible
answers to "which role should enforcement check?":

**Scenario 3 (Rigby → Claude Code): executor_actor?**
- Answer A: `claude-code` (agent that runs the code)
- Answer B: `rigby` (employee that delegated)
- S1271 §8.3 calls this "the most consequential semantic gap."

**Scenarios 1, 5, 11: sponsor_actor?**
- Answer A: `system` (beat is the mechanism)
- Answer B: `chris` (implicit principal who configured the beat)
- Answer C: UNKNOWN (no human sponsor)

**Scenarios 4, 7: principal_user with silent-None on `_resolve_runs_as_user_id`?**
- Answer A: `chris` (via runs_as_username lookup succeeds)
- Answer B: UNKNOWN (if User('chris') missing, F3 silent None)

### 6.5 Boundary drop crossings

Per sub-agent 3 §C.5 — the three S1271 F6 drop boundaries appear
in nearly every scenario:

- **F6-a (HTTP → Celery)**: Scenarios 2, 7, 10 — request.user
  not threaded to task; runs_as_username is config, not evidence.
- **F6-b (MissionRunner config → OpsRun row)**: Scenarios 1, 2,
  5, 6, 7, 9, 11 — runs_as_username not persisted as FK; OpsRun
  has no user field.
- **F6-c (MissionRunner → Step.fn)**: Scenarios 1, 2, 5, 6, 7,
  9, 11 — step.fn receives OpsRun only; no actor param.

**Severity:** F6-b is most consequential (OpsRun cannot answer
"who ran this?" via SQL). F6-a and F6-c compound the loss.

### 6.6 Composite examples

Per sub-agent 3 §F, three illustrative composite examples for
downstream design consumption:

**Example 1: Scenario 1 × `certify_mission_run` (EXECUTE) × F6-b.**
Rigby's beat mission autonomously certifies via
`emit_mission_verdict()`. `auto_emit_verdict=True` default. But
`OpsRun.user` FK is missing (F6-b) — no durable record of
principal_user's approval. EXECUTE without durable actor record
becomes "trust the code path" enforcement.

**Example 2: Scenario 4 × `create_escalation_deliverable` (EXECUTE) × agent_name ambiguity (S1271 F4).**
Claude Code invokes tool that creates Deliverable.
`agent_name='claude-code'` (executor) or `agent_name='Rigby'`
(delegator)? Undefined by convention. Enforcement on
`agent_name` requires disambiguation at every call site.

**Example 3: Scenario 7 × `recommend_remediations` (RECOMMEND) × escalation identity loss (F6-a).**
Platform Auditor's audit posts to Chris's PA chat via
`pa_post_fn()`. `PAPostContext.runs_as_user_id` available at
runner but is not queried at pa_post_fn time. Escalation
identity loss: retro cannot ask "who reviewed the auditor's
recommendation?"

---

## 7. Governance Plane Interactions

Per sub-agent 4 — governance authority evolution (S1269) F1
identified 4 planes that don't compose today. Adding authority
enforcement is a 5th surface.

### 7.1 The four planes (per S1269 F1)

1. **Autonomy plane** — `GovernanceState` + `KillSwitch` +
   `GovernanceEngine` + `governance_tool`. 4 consumers
   (spiders, signal agg, workspace pipeline, LLMEnforcer via
   sync).
2. **Authority plane** — `JobContract.authority` +
   `AuthorityLevel` + warn-mode `authority_contract_observed`.
   OBSERVATION-ONLY per §5.3.
3. **Budget plane** — `SystemConfiguration.budget_freeze_active`
   + `LLMEnforcer` + `check_retry_budget`. RUNTIME-VERIFIED at
   `llm_enforcer.py:200-262`.
4. **Human governance plane** — `HumanAttentionItem` +
   `HumanFeedbackRecord` + `HumanPreference` +
   `OrchestrationApprovalGate` + lifecycle service. RUNTIME-VERIFIED.

### 7.2 Existing cross-plane touches

Per sub-agent 4 §B, verified independently:

| # | Composition | Direction | Consistency | Evidence |
|---|---|---|---|---|
| 1 | Autonomy → Budget (one-way sync) | GovernanceEngine writes `budget_freeze_active` when `mode='freeze'` | One-way only; **desync risk** if operator flips budget flag directly | `governance.py:2285-2322` (sync); `llm_enforcer.py:200-221` (consumer); S1269 F4 |
| 2 | Autonomy → Autonomy (within-plane) | 4 consumers respect `GovernanceState.effective_mode` | Consistent across 3 blocking consumers | `tasks_spiders.py:381-398`; `signal_aggregation_service.py:207-227`; `models_workspace_templates.py:209-218`; `intelligence.py:1200-1215` |
| 3 | Autonomy → Human governance | **NOT WIRED** | Independent | `human_attention_lifecycle.py:36-728` (zero grep for GovernanceState/KillSwitch/budget_freeze) |
| 4 | Authority → any plane | **NOT WIRED** | Independent (authority is observation-only) | `mission_runner.py:835-900` — only consumer emits event; never blocks |
| 5 | Budget → Autonomy | **NOT WIRED** | Independent (autonomy does not read budget state) | `governance.py:2231-2283` — set_mode does not check budget flags |
| 6 | KillSwitch → any plane | **NOT WIRED** | Write-only; verified: 5 read sites all in management/cleanup contexts, NOT dispatch | `governance.py:2192, 2370, 2508` (list, deactivate, expire); `intelligence.py:1569, 1717` (TTL cleanup) — sub-agent 4 verification confirmed |

**Only one cross-plane touch exists (composition #1).** Every
other cross-plane interaction is silent independence.

### 7.3 Existing composition wins (patterns to reuse)

Per sub-agent 4 §E:

1. **Autonomy plane internal consistency** — 3 task-dispatch
   consumers use `effective_mode` uniformly (SAFE per S1269 §7).
2. **Budget → Autonomy one-way sync** — GovernanceEngine writes;
   LLMEnforcer reads. Intentional layered design with documented
   desync risk (WRAPPER per S1269 §7).
3. **Human governance loop** — HAI → decision → HumanFeedbackRecord
   → FeedbackProcessor → AgentLearning + LearningInsight. Only
   round-trip with learning today.
4. **OrchestrationApprovalGate bridge** — orchestration ↔ HAI
   via UUID link. Decoupled by design.

### 7.4 Existing composition failures (patterns to avoid)

Per sub-agent 4 §D + S1269:

- **F1 (S1269 F4):** Budget-Autonomy one-way sync desync risk —
  operators can flip budget_freeze_active directly, creating
  disagreement between autonomy and budget planes.
- **F2 (S1269 F2):** KillSwitch write-only — full write path;
  zero dispatch readers. Enforcement absent.
- **F3 (S1269 F8):** Per-scope aspirational — `scope='agent'` or
  `scope='desk'` declared but never read. All 4 consumers query
  `scope='global'` only.
- **F4 (S1269 F9):** Throttle mode dead — `mode='throttle'`
  declared, never consumed.
- **F5 (S1269 row 33):** `OrchestrationApprovalGate.check_auto_approvals()`
  method exists but caller UNKNOWN (not in beat schedule; one
  wrapper task at `tasks.py:7666` without trigger).

### 7.5 New composition questions authority enforcement introduces

Per sub-agent 4 §C + §F — 8 new questions with no current-state
answers. This is a research inventory; **this doc does NOT
answer them**.

1. **Authority × Autonomy priority.** `authority[X]=PROHIBITED`
   AND `GovernanceState.mode='normal'`. Which wins?
2. **Authority × Autonomy resource conflict.**
   `authority[X]=EXECUTE` AND `GovernanceState.mode='freeze'`
   (scoped to that employee's desk — currently aspirational per
   §7.4 F3).
3. **Authority × Budget layering.** `authority[X]=EXECUTE` AND
   `budget_freeze_active=True` AND action X requires LLM. Which
   layer blocks first? Budget enforces at LLM call-time; authority
   would enforce at dispatch or call-time; layering order
   undefined.
4. **Authority × Human governance (RECOMMEND).** Should
   `authority[X]=RECOMMEND` auto-create HAI? Or is HAI
   creation orthogonal to authority?
5. **Authority × KillSwitch precedence.**
   `authority[X]=EXECUTE` for target Y AND
   `KillSwitch(target=Y, is_active=True)`. KillSwitch is
   write-only today (§7.2 #6 + F2); if wired, precedence?
6. **Autonomy × Human governance (freeze + HAI).**
   `mode='freeze'` AND pending HAI. Does auto-approve still
   fire?
7. **Budget × Human governance (auto-approve with LLM confidence).**
   `budget_freeze_active=True` AND HAI auto-approve gate uses
   `ml_confidence` (`human_attention_lifecycle.py:272`
   verified). If confidence check requires an LLM call, does
   freeze block it?
8. **Cross-plane precedence (4 planes vote).** If all four
   planes cast opinions, what's the decision tree? Currently:
   no policy exists.

### 7.6 Composition mode taxonomy

Per sub-agent 4 §G — five possible cross-plane composition
modes:

| Mode | Definition | Current-state prevalence |
|---|---|---|
| **Additive** (ANY veto blocks) | Multiple planes vote; any veto is decisive | Not used |
| **Precedence** (ordered) | Planes ordered; highest-precedence wins | Partial (autonomy → budget one-way sync approximates this) |
| **Union** (combine → decision) | Planes combine into composite | Not used |
| **Layered** (fire in sequence, cascade) | Planes fire in defined order; each layer cascades | Partial (budget + autonomy layered; HAI loop) |
| **Independent** (silos) | Planes don't compose; fire independently | **Predominant current-state pattern** |

**Current platform behavior:** Predominantly independent silos.
Budget↔Autonomy is partially layered (one-way sync + sequential
gates). HAI lifecycle is internally layered. All other
cross-plane touches absent.

**Authority enforcement will introduce:** likely a precedence
or layered model. **Choice is a design decision downstream of
this doc.**

### 7.7 Cross-reference to S1270 + S1271

- **S1270 §9 F8** (Symbol Mapping composition with 4 planes
  undesigned): confirmed. Authority plane has zero symbol
  registry.
- **S1271 F10** (Actor Attribution composition with 4 planes
  undesigned): confirmed. None of the 4 planes read actor
  attribution metadata.
- **This section:** authority enforcement as 5th surface adds
  8+ new composition questions. Smallest blocker is Symbol
  Mapping (shared with S1270). Largest design choice is plane
  precedence.

---

## 8. Historical Failure Analysis

Per sub-agent 5 — consolidated 33-incident catalog across the 4
prior research docs (S1270 §7 + S1271 §5 + S1269 §6 + S1268 §7).

### 8.1 Deduplicated incident matrix (33 core incidents)

Full incident-by-mode matrix in sub-agent 5 §A. Summary view
here for the 4 most-cited failure classes:

**Cluster 1: Authority Symbol Mapping Gap** (7 incidents merged;
represents all of I-S1, I-S2, I-S3, I-G1, I-A9, I-A10, I-C12).
Root cause: policy-description strings not mapped to runtime
symbols. **Every enforcement mode benefits; every enforcement
mode equally blocked without Symbol Mapping.**

**Cluster 2: Actor Identity Drift** (4 incidents: I-A2, I-A4,
I-A15, I-C11). Agent canonicalization failures recur; hard-block
at canonical factory prevents. Sources: S1271 + S1268.

**Cluster 3: Silent Failures** (7 incidents: I-C1, I-C5, I-C6,
I-C7, I-C8, I-C9, I-C10, I-A11). Failures without audit
evidence at occurrence time. observe-only + retro-audit cover
these.

**Cluster 4: Permission / Auth Gate Issues** (4 incidents: I-A6,
I-A1, I-G3, I-G2). Token / permission enforcement. hard-block +
require-approval effective.

### 8.2 Mode effectiveness ranking (coverage across 33 incidents)

Per sub-agent 5 §B. **This is coverage, not preference:**

| Mode | YES | PARTIAL | NO | YES+PARTIAL % |
|---|---|---|---|---|
| warn-mode | 20 | 11 | 2 | 94% |
| observe-only | 17 | 13 | 3 | 91% |
| retrospective-violation-report | 19 | 10 | 4 | 88% |
| soft-fail | 17 | 12 | 4 | 88% |
| hard-block | 14 | 11 | 8 | 76% |
| degrade-mission-evidence | 6 | 16 | 11 | 67% |
| require-human-approval | 4 | 11 | 18 | 45% |
| defer-mission | 4 | 8 | 21 | 36% |
| freeze-queue | 7 | 4 | 22 | 33% |
| freeze-tool | 5 | 5 | 23 | 30% |
| pause-employee | 5 | 6 | 22 | 33% |
| freeze-platform | 3 | 4 | 26 | 21% |

**Critical warning from F7 above:** high coverage does not mean
high preference. A mode that covers 94% of incidents while
producing 30% false-positive rate is worse than a mode covering
30% at 0% false-positive rate. **Ranking is coverage, not
recommendation.**

### 8.3 Failure classes best-served by each mode

Per sub-agent 5 §C:

- **warn-mode (94%):** authority string gaps, silent
  deliverable/agent creation failures, config drift,
  permission/auth gate issues
- **observe-only (91%):** audit-trail completeness, evidence
  reconstruction, cross-employee telemetry, post-hoc policy
  violations
- **hard-block (76%):** token/identity mismatches, type
  enforcement, canonicalization, permission gates, catastrophic
  actions (publish, arbitrary code, DB delete)
- **soft-fail (88%):** degraded-but-continuing patterns,
  placeholder stalls, config issues, auto-fallback behaviors
- **degrade-mission-evidence (67%):** silent failures where
  evidence should be marked compromised
- **require-human-approval (45%):** judgment calls, policy
  exceptions, authority boundary cases
- **Freeze modes (21-33%):** highly specific infrastructure
  failures; over-broad for most failure classes
- **retro-audit (88%):** same coverage as warn-mode +
  observe-only combined; post-hoc reconstruction

### 8.4 Cross-catalog overlap

Per sub-agent 5 §G — the single largest cluster is the Authority
Symbol Mapping Gap (7 incidents). **Rigby S1272 SIGN
clarification:** the earlier framing "every enforcement mode
is equally blocked without Symbol Mapping" overgeneralizes. The
precise claim is: **all enforce-mode prevention options
(hard-block, soft-fail, require-approval, freeze-tool,
freeze-queue, defer, pause-employee) are blocked absent Symbol
Mapping; audit/warn modes (observe-only, warn-mode,
degrade-mission-evidence, retro-audit) remain partially valuable
even without symbol binding — S1264 is the standing counter-
example demonstrating this partial value.** This is F6 above and
the load-bearing justification for §14's next-mission
recommendation.

### 8.5 Historical enforcement precedents (§4.5 recap)

Per sub-agent 5 §H, enforcement modes already in production
(reproducing §4.5 for cross-reference):

- **S1264 warn-mode** shipped; found the 68 unbound authority
  strings (I-S1). **Coverage strong** but no blocking; requires
  Symbol Mapping.
- **`messaging_tool.send_message` guard** works but coarse — S1268
  DO-NOT-REUSE flag: disables entire tool, not per-action gating.
- **`GovernanceState.mode='freeze'`** works with 4 consumers.
- **HAI + auto-approve gate** works with 7 conditions.
- **`AssistantProfile.get_allowed_tools()`** narrow — tool-level
  only.
- **`LLMEnforcer.check_budget()`** semantically closest analog;
  fails open per F8.

**Gaps in existing precedents:**
- No hard-block on per-action authority (only tool / budget /
  global freeze).
- No per-employee enforcement toggle (S1264 shipped platform-wide).
- Freeze-platform is emergency-only; no graduated enforcement
  path.
- No dry-run analysis of "what would have been blocked."

---

## 9. Design Options

**Research description of a design space, NOT a design.**
Six options emerge naturally from the boundary × mode ×
plane-composition space. Each option is presented with reuse
footprint, requirements, and tradeoffs. **This doc does not
rank, prefer, or recommend among them.**

Per mission spec Q9 explicit enumeration.

> **Neutrality guardrail (Rigby S1272 SIGN edit).** Comparatives
> in this section (e.g., "cleanest", "most reversible", "highest
> coverage", "broadest", "canonical", "most compatible") describe
> **axes** of the design space, not endorsements. If a paragraph
> reads as recommendation because of an adjective, it is a
> language slip — flag it. Every option below is a mechanically
> defensible choice; each has failure modes; Chris gates any
> preference among them at the downstream design-decision mission
> (§14.3), not here.

### 9.1 Option A — MissionRunner-centered enforcement

**Shape.** Authority checked at boundaries 4, 5, 6 (mission
entry, preflight, before each Step.fn). Enforcement rides on the
MissionRunner lifecycle; steps that would invoke a PROHIBITED
action are blocked before `step.fn(mission)` is called.

**What it reuses.**
- `MissionRunnerConfig.job_contract` (already opt-in per employee)
- `authority_contract_observed` event pattern (existing shape;
  parallel violation event fits)
- `_emit_authority_contract_event` structure (existing method
  to parallel)
- OpsRunEvent audit chain

**What it requires.**
- Symbol Mapping Option A/C ships (steps declare
  `action_classes_invoked`) — or Option D (central registry
  binds step name → actions)
- Step dataclass extension (per S1270 §5.1 Option A shape)

**What it prevents.**
- Contract violations at mission scope (any of 4 employees)
- Step-level actions that violate authority pre-invocation

**What it misses.**
- Actions taken via direct tool calls outside MissionRunner
  (Boundary 2, 3)
- Actions via Celery task independent of missions
- Actions via ORM directly (Boundary 10 signals)
- HTTP endpoint actions (Boundary 1)

**Implementation risk.** Medium. MissionRunner is central and
well-tested; extending it in-place has clear precedent. But
missing coverage of tool-dispatch path (Boundary 2) means
authority enforcement is only partial.

**Operational risk.** Low-to-medium. Warn-mode already at this
layer; adding enforcement gate keeps the surface familiar.
False-positive risk is scoped to steps that declare wrong
action_classes.

**Observability.** Strong. Events fire at OpsRunEvent scope;
audit chain intact.

**Rollback strategy.** Feature flag on `MissionRunnerConfig.enforce_authority=False`
default; opt-in per employee (matches S1264 warn-mode rollout
pattern).

**Compatibility with Employee OS.** High. MissionRunner is the
canonical Employee OS execution primitive.

**Failure modes.**
- Step declares no `action_classes_invoked` → default (fail-open
  or fail-closed?)
- Action taken outside MissionRunner surface (e.g., Chris runs
  code manually) → no enforcement
- Symbol Mapping Option E chosen → this option becomes
  incompatible (evidence-only cannot pre-block)
- **Signal-quality maintenance burden (Rigby S1272 SIGN):**
  every step author must accurately declare
  `action_classes_invoked` at code time, keep it in sync as the
  step body changes, and pay the code-review cost forever.
  Silent drift between declaration and body is a primary
  failure mode; catching it requires ongoing verifier-loop
  audits. Signal quality — not enforcement layer — is the
  hardest constraint.

**Unknowns.** How does per-mission enforce toggle compose with
per-employee toggle? Priority when both set?

### 9.2 Option B — ToolDispatcher-centered enforcement

**Shape.** Authority checked at Boundary 2 (ToolDispatcher.execute()
entry) and Boundary 3 (inside PA tool handler). Enforcement
rides on the tool dispatch layer.

**What it reuses.**
- `AssistantProfile.get_allowed_tools()` gate structure at
  `tool_dispatcher.py:687-720` (extension via tool → action_class
  binding)
- `TOOL_PERMISSION_DENIED` error shape
- Tool schema layer (`pa_tool_schemas.py`)

**What it requires.**
- Symbol Mapping Option B ships (tool schema carries
  `action_class` attribute per tool + action)
- Tool schema extension for action_class field

**What it prevents.**
- PA tool dispatches that violate authority
- Direct tool calls from any caller (Rigby, Chris, Claude Code, etc.)
- Tool-mediated actions on Deliverable / DirectMessage / OpsRun

**What it misses.**
- Actions taken outside tools (raw ORM in mgmt commands, direct
  Django queries)
- Celery tasks that don't dispatch via ToolDispatcher
- Actions dispatched via `AgentRouter.route()` bypassing PA tool
  layer
- Step body actions inside MissionRunner not routed through
  ToolDispatcher

**Implementation risk.** Low-to-medium. Extends an existing
gate with well-understood semantics. But requires ~113 PA tool
schemas to gain action_class annotations (mostly `None`).

**Operational risk.** Medium. Tool dispatch is high-traffic;
gate overhead per call matters.

**Observability.** Strong. `ToolCallRecord` writes on every
dispatch; violation events would parallel.

**Rollback strategy.** Feature flag globally; per-user
allowed_tools already provides a partial rollback mechanism.

**Compatibility with Employee OS.** Medium. Employees use tools
via MissionRunner-orchestrated steps; enforcement at tool layer
is orthogonal to per-employee authority scope. Requires
per-caller identity → employee_handle resolution.

**Failure modes.**
- Tool without `action_class` (default fail-open or fail-closed?)
- Caller identity resolution to employee_handle fails
- Employee-independent tool calls (Chris directly) not covered
  by employee authority contract
- **Signal-quality maintenance burden (Rigby S1272 SIGN):**
  every one of the ~113 PA tool schemas needs an
  `action_class` annotation per action (or an explicit `None`
  marker). Tool authors must accurately declare and maintain
  the mapping through every schema change; silent drift between
  the annotation and the handler behavior is a primary failure
  mode. As with Option A, signal quality — not enforcement
  layer — is the hardest constraint.

**Unknowns.** How does tool-layer enforcement compose with
Boundary 14 (LLMEnforcer)? Both are INLINE; ordering?

### 9.3 Option C — Audit-first enforcement (evidence-only)

**Shape.** Every action emits `action_class` in its audit row
(ToolCallRecord, OpsRunEvent, LLMCallEvent, etc.). Violations
detected retrospectively via post-mission audit or a periodic
scan. No pre-dispatch enforcement.

**What it reuses.**
- Existing audit chain (ToolCallRecord + OpsRunEvent +
  LLMCallEvent + CeleryTaskEvent + AgentExecution)
- Bug Triage step 4 aggregation pattern (`bug_triage.py:396-453`)
- `evidence_for_mission()` at `status.py:53-251`

**What it requires.**
- Symbol Mapping Option E (evidence-only) or A/B/C/D with
  audit-only mode
- `action_class` field addition to audit models (per S1270
  Option E design)

**What it prevents.**
- Nothing at execution time
- Violations become observable + reportable retroactively

**What it misses.**
- All pre-dispatch prevention
- Real-time gating for catastrophic actions
- Any hard-block use case

**Implementation risk.** Low. Purely additive; no gate logic;
existing audit chain extended.

**Operational risk.** Very low. No false-positive rate on
enforcement (never blocks).

**Observability.** Very strong. Every action logged with
action_class; retrospective query surfaces violations.

**Rollback strategy.** Trivial — remove periodic scan job; audit
schema addition is backward-compatible.

**Compatibility with Employee OS.** High. Additive to existing
audit patterns.

**Failure modes.**
- Producer omission — code path writes audit row without
  populating action_class → silent gap
- Consumer lag — violations detected in next Bug Triage cycle,
  not real-time
- Cannot support hard-block-required actions (delete DB rows,
  publish externally, etc.)

**Unknowns.** Does audit-only support graduation to enforce-mode
later, or is it a terminal design? Per S1270 §5.5 F7 disclaimer:
"reversibility ≠ preference."

### 9.4 Option D — Human-approval enforcement (HAI-mediated)

**Shape.** Certain authority levels (typically RECOMMEND, but
extensible to PROHIBITED) trigger `HumanAttentionItem` creation
before the action executes. Human approval unblocks execution;
rejection blocks + logs.

**What it reuses.**
- `HumanAttentionItem` model + lifecycle service
- `OrchestrationApprovalGate` bridge (already links workflow
  step ↔ HAI via UUID)
- HAI decision endpoint at `views_human_interface.py:84-100`

**What it requires.**
- Symbol Mapping Option A/B/C/D (need to know action_class to
  decide whether HAI required)
- Authority → HAI creation signal (new; not in existing 31 HAI
  creators)
- Per-level policy: which levels create HAI?

**What it prevents.**
- RECOMMEND-level actions from executing before human review
- Configurable subset of PROHIBITED (soft-block variant)

**What it misses.**
- EXECUTE-level actions (no review needed by definition)
- OBSERVE-level (read-only)
- Volume — if RECOMMEND creates HAI per action, approval fatigue
  possible (per S1269 §2.4 auto-approve mitigates)

**Implementation risk.** Medium. New signal integration but
uses existing primitives.

**Operational risk.** High. Approval fatigue is documented
concern (§10 anti-pattern #14 below); HAI capacity ~100
items/day max per prior audits.

**Observability.** Strong. HAI creation + decision + feedback
chain is well-instrumented (S1269 F5).

**Rollback strategy.** Feature flag on authority → HAI signal.

**Compatibility with Employee OS.** High. HAI is the canonical
human-in-loop primitive.

**Failure modes.**
- Approval fatigue if RECOMMEND actions volume is high
- Auto-approve gate (7-condition) may over-approve if authority
  level is treated as a trust signal
- HAI creator misclassification (source_type wrong) breaks
  auto-approve

**Unknowns.** How does authority-triggered HAI compose with the
existing 31 HAI creators? Cross-source collisions?

### 9.5 Option E — Multi-layer enforcement

**Shape.** Different boundaries enforce different authority
levels. E.g., PROHIBITED at Boundary 1 (HTTP middleware) and
Boundary 2 (ToolDispatcher); RECOMMEND via HAI at Boundary 4 or
6; EXECUTE observed at Boundary 5 (warn-mode retained); OBSERVE
enforced via read-only DB scope.

**What it reuses.** All of Options A-D primitives.

**What it requires.**
- Symbol Mapping Options B / C / D (need action_class in
  multiple places)
- Composition contract: which boundary is authoritative for
  which level?

**What it prevents.**
- Broadest coverage: each level enforced at the boundary that
  fits its semantic best

**What it misses.**
- Uniformity — no single answer to "who enforces authority"
- Debuggability suffers when multiple layers vote

**Implementation risk.** High. Multiple integration points;
composition semantics must be nailed down.

**Operational risk.** Medium-high. Cascade risk if one layer's
enforcement fails.

**Observability.** Complex — evidence spread across multiple
layers.

**Rollback strategy.** Layer-by-layer feature flags; can partially
rollback.

**Compatibility with Employee OS.** Medium. High coordination
cost.

**Failure modes.**
- Layer A blocks; Layer B allows (or vice versa)
- Precedence semantics unclear
- Audit trail requires cross-layer join

**Unknowns.** Which level → which layer mapping? What if levels
overlap (`certify_mission_run` = EXECUTE for 3 employees; would
one boundary handle certification for all?)

### 9.6 Option F — Governance-plane composition

**Shape.** Authority enforcement composes with the 4 existing
governance planes into a unified decision. Explicit precedence
policy (e.g., KillSwitch > GovernanceState.freeze > Authority
PROHIBITED > Budget freeze > HAI pending).

**What it reuses.**
- All 4 governance planes (`GovernanceState`, `KillSwitch`,
  `SystemConfiguration.budget_freeze_active`, HAI lifecycle)
- Existing composition #1 (autonomy → budget one-way sync)

**What it requires.**
- Answers to §7.5's 8 composition questions
- Precedence policy (Additive / Precedence / Union / Layered)
- KillSwitch dispatch consumers (GAP-7 must close)
- Per-scope reads on GovernanceState (F3 must close)

**What it prevents.**
- Broadest possible: authority + autonomy + budget + human all
  compose into single decision

**What it misses.**
- Simplicity — complexity moves to composition policy

**Implementation risk.** Very high. Requires closing S1269
gaps (KillSwitch enforcement, per-scope reads, throttle mode).

**Operational risk.** High. Multi-plane decisions are hard to
debug.

**Observability.** Must design cross-plane audit trail.

**Rollback strategy.** Per-plane feature flags.

**Compatibility with Employee OS.** High if done well; Very low
if precedence semantics unclear.

**Failure modes.**
- Plane precedence choice codifies wrong policy
- Desync between planes cascades (per S1269 F4)
- KillSwitch enforcement gaps (F2) become blocking
- **Policy ossification / precedence lock-in (Rigby S1272 SIGN):**
  once a cross-plane precedence contract ships, it becomes
  extremely hard to change without invalidating audit
  interpretations. If a downstream governance decision needs
  a new plane ordering, historical audit records were written
  against the old precedence — retro-analysis becomes
  ambiguous. This is a distinct risk from implementation
  complexity: it accumulates *after* ship, not before.

**Unknowns.** All of §7.5.

### 9.7 Cross-option comparison

| Option | Reuses | Requires | Prevents (breadth) | Implementation risk | Rollback ease |
|---|---|---|---|---|---|
| A: MissionRunner-centered | MissionRunner + OpsRunEvent | Symbol Mapping A/C/D | Mission-scoped actions | Medium | Feature flag; opt-in per employee |
| B: ToolDispatcher-centered | AssistantProfile gate + tool schema | Symbol Mapping B | Tool-mediated actions | Low-medium | Feature flag |
| C: Audit-first (evidence-only) | Audit chain + Bug Triage | Symbol Mapping E OR A/B/C/D | Nothing at execution time | Low | Trivial |
| D: Human-approval | HAI + OrchestrationApprovalGate | Symbol Mapping A/B/C/D | RECOMMEND-level actions | Medium | Feature flag on signal |
| E: Multi-layer | All Options A-D primitives | Symbol Mapping B/C/D | Broadest | High | Layer-by-layer |
| F: Governance-plane composition | 4 planes | 8 composition Qs + GAP-7 closed + F3 closed + F4 mitigated | Broadest possible | Very high | Per-plane |

### 9.8 What is NOT an option

Explicitly outside the design space (per §10 anti-pattern
inventory):

- **Enforcing free-form `prohibited_actions` prose** — S1270 §2.6:
  prose is not a symbol.
- **Trusting LLM self-reported actions** — LLMs will lie about
  what they did.
- **Enabling enforcement before symbol mapping** — F6; blocks all
  options.
- **Enabling enforcement before actor roles resolved** — S1271
  F11.
- **Creating new approval models when HAI exists** —
  `EMPLOYEE_OS_PRIMITIVES.md` §2 anti-duplication matrix.
- **Blocking all model writes** — cascade failure of audit chain
  itself.

Full list: §10.

---

## 10. Anti-Patterns / Premature Enforcement

Per sub-agent 5 §D. **Fifteen anti-patterns** to avoid. Each
carries a citation to the prior research that raised the
concern.

> **Tier-0 hazards (Rigby S1272 SIGN edit).** The 15 anti-patterns
> below are listed without a preference ordering — every entry is
> a real risk with prior evidence. **But three of them carry
> disproportionately high blast radius** if implemented
> prematurely:
>
> - **#1 Blocking all model writes** — highest blast radius.
>   Destroys the audit substrate itself; missions appear
>   never-ran; recovery from an enforcement mistake is
>   impossible because the evidence chain that would show what
>   happened has been broken.
> - **#8 Enabling enforcement before symbol mapping exists** —
>   creates a gate with no stable action_class signal. Either
>   fail-open everywhere (illusory enforcement) or fail-closed
>   on "unknown action" (mass outage).
> - **#15 Silent enforcement (no violation event emitted)** —
>   false sense of safety; governance theater. Violations occur
>   but nothing surfaces them; downstream reasoning treats the
>   platform as compliant when it is not.
>
> These three are the ones most likely to cause a platform-wide
> incident. Ranking them explicitly is not a preference over the
> other 12 — it is a Tier-0 incident-risk callout so that any
> downstream design mission (§14.3) treats them as hard-block
> topics.

| # | Anti-pattern | Danger | Source | Would this pattern cause? |
|---|---|---|---|---|
| 1 | Blocking all model writes | Cascade failures; disables audit trail itself | S1268 §7; EMPLOYEE_OS_PRIMITIVES.md §4.4 | Audit trail corruption; missions appear never-ran |
| 2 | Free-form `prohibited_actions` prose as symbol | Prose is not executable; cannot be checked at runtime | S1270 §2.6 F11 blind spot #2 | Authority checklist becomes meaningless; no actual enforcement |
| 3 | Trusting LLM self-reported actions | LLMs will lie about what they did; may claim authority they lack | S1271 F11 explicit warning; S1270 §6.4 | Enforcement based on false evidence; violations unreportable |
| 4 | Treating `runs_as_username` as executor_actor | `runs_as_username` is principal_user selector, not executor; role confusion | S1271 §8.5, F11 | Executor identity lost; delegation chain breaks |
| 5 | Assuming `employee_handle` equals user | Employees are not users; cross-role conflation | S1271 §8.1-8.4 Q7 | User attribution failures; audit trail incoherent |
| 6 | Enforcement via MissionRunner only | Ignores ToolDispatcher, Celery, HTTP, direct ORM | S1270 §6.2; sub-agent 2 §G | 60%+ of actions bypass MissionRunner |
| 7 | Enforcement via ToolDispatcher only | Misses non-tool actions: ORM writes, agent delegation, Celery, spider | S1270 §6.3; S1271 §7 | Authority silent on non-tool actions |
| 8 | Enabling enforcement before symbol mapping exists | No action_class to check; enforcement gates fail open OR fail closed on nothing | S1264 handoff + S1270 F6 code assertion at `mission_runner.py:895-899` | All enforcement gates dysfunctional |
| 9 | Enabling enforcement before actor roles are resolved | S1271 F11 role-confusion warning | S1271 §8.5 + S1271 §7 | Executor identity ambiguous; delegation broken |
| 10 | Creating new approval models when HAI already exists | Anti-duplication per EMPLOYEE_OS_PRIMITIVES §2 matrix | S1268 §6 + §8; S1269 §7 F10 | Duplicate decision models; no learning loop; maintenance debt |
| 11 | Enforcing at wrong enforcement layer | Each layer has different signal availability; wrong layer → false blocks or misses | S1270 §6.2 layer coverage; §6.5 composition | Either over-broad blocking or useless |
| 12 | Making enforcement unrollable | No rollback path from enforce-mode → warn-mode; gates become permanent | S1270 F7 reversibility analysis | Can't dial back if issues arise |
| 13 | Collecting metrics before min telemetry window | S1264 prereq #2: min days of clean warn-mode required before enforce switch | governance_authority_evolution.md §4; trust threshold | Trust decision made on noise; false-positive rate unknown |
| 14 | False-positive tolerance > system capacity | If enforcement blocks >N% actions, human confidence erodes; approval gate overwhelmed | S1264 pattern; S1268 HAI capacity analysis (~100 items/day) | Approval gate drowns; missions never recover |
| 15 | Silent enforcement (no violation event emitted) | Runs without emitting violation event; gaps go unnoticed | S1268 §7 pattern theme: "silent failures dominate" | Violations invisible; enforcement unobservable |

**Anti-pattern reading:** every one of these has already
happened in some analog form on the platform. §10 is a
checklist, not speculation.

---

## 11. Minimum Prerequisites for Enforce-Mode

Per sub-agent 5 §E + §F. **Fifteen prerequisites** form a DAG,
not a checklist (per F11). Critical path in §11.2.

### 11.1 Prerequisite table

| # | Prereq | Category | Why needed | Currently satisfied? | Gap to close |
|---|---|---|---|---|---|
| 1 | Stable symbol mapping (v0) | Symbol Mapping | Does S1270 answer? | **PARTIAL** — 5 options exist; no choice made | S1270 §11.1 Option Selection Design required |
| 2 | Actor role vocabulary formalized | Actor Attribution | S1271 §8.5 executor/sponsor/principal defined; must be enforced at boundaries | **PARTIAL** — vocab defined; runtime enforcement absent | S1271 §7 enforcement boundaries need wiring |
| 3 | Evidence event schema defined | Violation detection | Shape of `authority_contract_observed` + action_class fields on audit models | **PARTIAL** — event exists; action_class fields absent on audit models | Add action_class to ToolCallRecord, OpsRunEvent, LLMCallEvent (per S1270 Option E or parallel) |
| 4 | Violation event schema parallel to observation event | Violation detection | `VIOLATION_DETECTED_LABEL` + detail (violation_type, action_class, employee_handle, level_expected, enforcement_mode_at_time) | **NO** — does not exist | New event schema design |
| 5 | Fallback behavior when enforcement check errors | Fault tolerance | Fail-open vs. fail-closed policy per mode | **NO** — not documented anywhere; LLMEnforcer precedent is fail-open (F8) | Design policy per enforcement mode |
| 6 | Rollback behavior (enforce → warn) | Reversibility | How to downgrade active enforcement without losing telemetry | **NO** — no rollback path designed | Feature flag + HAI escalation pattern per S1264 |
| 7 | Human review path (where do violations escalate?) | Human governance | Violations → HAI? governance_tool? | **PARTIAL** — HAI + governance_tool exist; routing rule not designed | Design escalation workflow |
| 8 | Test coverage (what does test-enforced look like?) | Testing | Unit tests per mode; integration; canary per S1244 pattern | **UNKNOWN** — no test audit of authority paths | Audit test matrix per enforcement layer |
| 9 | Dry-run mode (per-action check without enforcement) | Safety | Toggle per employee to see violations without blocking | **PARTIAL** — S1264 warn-mode IS a dry-run for shape observation | Design graduation from warn-mode to enforce-mode |
| 10 | Per-employee opt-in (per S1264 pattern) | Rollout | Enforcement must be per-AIEmployee, not platform-wide at launch | **PARTIAL** — S1264 shipped to all 4; per-employee enforce flag not yet | Design toggle: `AIEmployee.enforce_authority_mode`? |
| 11 | Metrics window (min days of clean warn-mode before enforce) | Trust threshold | S1264 prereq #2: how many days without violations = "clean"? | **NO** — not specified | Set concrete SLA: "no violations + zero false-positive alerts for X days" |
| 12 | Trust threshold (what trust level = autonomy?) | Autonomy decision | Level maps to trust percentage — when is EXECUTE safe? | **NO** — enum exists; trust mapping does not | Design: EXECUTE requires X% historical compliance OR Y days clean OR manual gate |
| 13 | False-positive threshold (max acceptable block rate) | Safety | If enforcement blocks >X%, halt. What is X? | **NO** — not specified; S1268 HAI capacity ~100/day max | Design auto-halt threshold |
| 14 | Cross-plane composition rules | Autonomy/authority/budget/human | S1269 F1 + this doc §7.5: 8 open questions | **NO** — composition undefined | Design resolution (deferred, not blocking per §14) |
| 15 | Enforcement scope per action vs. per-employee | Scope granularity | Can employee have OBSERVE for X and EXECUTE for Y? Or per-employee mode? | **PARTIAL** — dict granularity exists; enforcement layer choice affects | Design per-action vs. per-employee reads |

**Status:** 3 fully satisfied? **NONE.** Most partial. Prereq #1
(Symbol Mapping) is the load-bearing predecessor per §14.

### 11.2 Prerequisite dependency graph (critical path)

Per sub-agent 5 §F:

```
Symbol Mapping (S1270 §11.1)
  ├─→ Option A/B/C/D/E chosen
  ├─→ Evidence Event Schema (#3)
  └─→ Action_class field on audit models

Actor Role Vocabulary (S1271 §8.5)
  ├─→ Three-role enforcement at boundaries (S1271 §7)
  └─→ Cross-employee dispatch wiring

Violation Event Schema (#4)
  ├─ Depends on: Evidence schema (#3) + Symbol mapping choice (#1)
  └─ Enables: Fallback behavior design (#5)

Fallback Behavior (#5)
  ├─ Depends on: Violation event schema (#4)
  └─ Enables: Enforcement layer choice

Rollback Behavior (#6)
  ├─ Depends on: Symbol mapping choice (#1) + Enforcement layer
  └─ Enables: Safe rollout per employee (#10)

Human Review Path (#7)
  ├─ Depends on: Violation event schema (#4) + HAI lifecycle (exists)
  └─ Enables: Enforcement-triggered escalation

Test Coverage (#8)
  ├─ Depends on: Enforcement layer choice + Symbol mapping (#1)
  └─ Parallel to: All implementation

Dry-Run Mode (#9)
  ├─ Depends on: warn-mode (exists; S1264)
  └─ Enables: Per-employee opt-in (#10)

Per-Employee Opt-In (#10)
  ├─ Depends on: Dry-run mode (#9) + Rollback behavior (#6)
  └─ Enables: Safe rollout per S1264 pattern

Metrics Window (#11)
  ├─ Depends on: Dry-run mode (#9) + Metrics infrastructure (exists)
  └─ Enables: Trust threshold (#12)

Trust Threshold (#12)
  ├─ Depends on: Metrics window (#11) + False-positive threshold (#13)
  └─ Enables: EXECUTE autonomy decision

False-Positive Threshold (#13)
  ├─ Depends on: Test coverage (#8) + Metrics window (#11)
  └─ Enables: Trust threshold (#12) + Auto-halt rule

Cross-Plane Composition (#14)
  ├─ Deferred (S1269 §10.4 Future Research)
  └─ Blocks: Full four-plane orchestration (out of scope here)

Mode Granularity (#15)
  ├─ Depends on: Symbol mapping choice (#1)
  └─ Enables: JobContract design for enforce-mode
```

**Critical path:** #1 → #3 → #4 → #5 → enforcement-layer choice
→ #8 + #7 → #6 → #10 → #11 → #12 + #13.

**Parallel-safe:** #14 (cross-plane composition — deferred);
#15 (mode granularity — waits on #1).

---

## 12. Architectural Findings

Eleven findings synthesized from the evidence. Numbered F1-F11
independently (mirroring prior research doc conventions where
§1 exec-summary findings and §12 architectural findings are
independent enumerations).

### F1 — AuthorityLevel has exactly one runtime consumer, and it's a shape-counter

Spot-verified: `mission_runner.py:864-867` (level_counts
accumulator). Grep for `.EXECUTE.value` / `.OBSERVE.value` /
`.RECOMMEND.value` / `.PROHIBITED.value` outside `jobs.py`
contract declarations returns only test files. **The 4-member
enum is policy metadata today, not enforcement metadata.**

### F2 — Existing enforcement precedents cover 8 of 12 modes

Per §4.5 + sub-agent 2 §F. Modes with production analogs:
observe-only, warn-mode, soft-fail, hard-block, require-approval,
pause-employee, freeze-platform, retro-audit. Modes without
analog: defer-mission (mission-scoped), freeze-queue,
degrade-mission-evidence at step scope, retro-audit at
authority-violation scope.

### F3 — Every existing enforcement gate uses a different vocabulary

Per §2.4. AssistantProfile is per-human; LLMEnforcer is
per-platform-task_type; GovernanceState is per-platform (with
aspirational per-scope); messaging_tool guard is per-tool; DRF is
per-user-role. **No existing gate reads `JobContract.authority`**
(S1269 F3). Any authority enforcement introduces a new
vocabulary that does not inherit precedent semantics.

### F4 — 4 governance planes don't compose; adding authority is a 5th surface

Per §7.2. Only 1 cross-plane touch exists (autonomy → budget
one-way sync). 8 new composition questions authority enforcement
introduces. No precedent to inherit.

### F5 — S1271 F6 drop boundaries constrain enforcement layer choice

Per §3.2 + sub-agent 2 §G. Boundaries 7, 9, 10 have permanent
identity-signal gaps (step closure opaque; async task without
request.user; background signal handler). Layer choice must
respect this.

### F6 — 33 historical incidents; largest cluster (7) is Authority Symbol Mapping Gap

Per §8.4 + sub-agent 5 §G. Cluster represents S1264 discovery
itself. **Every enforcement mode benefits equally from closing
it; every mode is equally blocked without it.** This is the
load-bearing justification for §14 next-mission recommendation.

### F7 — Mode effectiveness rank does not translate to mode preference

Per §8.2. Coverage metric ranking is not a recommendation.
A 94%-coverage mode with high false-positive rate is worse than
a 30%-coverage mode with 0% false-positive rate. **This doc
enumerates modes; it does not choose.**

### F8 — LLMEnforcer's fail-open pattern is precedent-setting

Spot-verified at `llm_enforcer.py:237-238`: `except Exception:
pass  # Never block LLM calls due to budget check errors`.
The closest existing analog for INLINE authority enforcement
fails open on internal error. Any enforcement mode design must
choose fail-open vs. fail-closed and cite rationale.

### F9 — Symbol Mapping choice constrains enforcement mode choice

Per §4.3. Option E (evidence-only) constrains to 5 of 12 modes.
Options A/B/C/D preserve all 12. Enforcement design cannot be
scoped independently of Symbol Mapping choice.

### F10 — Actor role composition determines mode preconditions

Per §4.2. Modes requiring only executor_actor (warn, soft-fail,
degrade-evidence, defer) can ship without full actor resolution.
Modes requiring principal_user (require-approval, retro-audit,
freeze-platform) presuppose S1271 role vocabulary is wired
everywhere.

### F11 — The 15 prerequisites form a DAG, not a checklist

Per §11.2. Sequential completion required on critical path;
parallel work limited to cross-plane composition (deferred) and
mode granularity (waits on #1). **None of the 15 is currently
fully satisfied.**

---

## 13. Open Questions

Genuine open questions. Not implementation tasks. Not invented
answers.

**Q1 — Should Symbol Mapping option choice precede this doc's
consumption, or can enforcement design proceed with Option
Selection Design in parallel?**
§4.3 constrains: Option E disables 7 modes. Option choice
narrows enforcement design space.

**Q2 — Which of §5.2's 4 interpretations per level is
authoritative?**
OBSERVE / RECOMMEND / EXECUTE / PROHIBITED each admit 4
defensible interpretations. Semantic drift risk if left
implicit.

**Q3 — Fail-open vs. fail-closed default?**
Per F8. LLMEnforcer fails open. Should authority enforcement
follow that precedent, or is the risk profile different?

**Q4 — Per-employee opt-in structure?**
Field on `AIEmployee` (`enforce_authority_mode`)? On
`JobContract` (`enforce_mode`)? Or on `MissionRunnerConfig`
(`enforce_authority=False` default)?

**Q5 — What metrics window (#11) is "clean"?**
S1264 prereq #2 says "≥14 days clean telemetry on N≥4
employees." Is 14 days the right constant? What defines
"clean" — zero violations, zero false-positives, zero
warn-mode events?

**Q6 — RECOMMEND-level → HAI auto-creation?**
§9.4 Option D scopes this. Should authority level be a signal
into HAI creation, or is HAI creation orthogonal?

**Q7 — Precedence policy for cross-plane conflicts (§7.5 Q8)?**
Additive / Precedence / Union / Layered / Independent?

**Q8 — KillSwitch dispatch enforcement (GAP-7)?**
Should this land before or after authority enforcement, given
KillSwitch is currently write-only?

**Q9 — Does the design accept boundaries 7, 9, 10 as
permanent gaps, or should new context-plumbing primitives close
them (major refactor)?**
Per F5.

**Q10 — What is the enforce-mode escalation policy on
violation?**
Send to HAI? Post to PA chat? Silent event only? Combination?

**Q11 — What is the fail-safe policy if a violation cascade
happens (many violations quickly)?**
Auto-halt (per §11 prereq #13)? Auto-freeze? Alert-only?

**Q12 — How does enforcement compose with `MissionRunnerConfig.auto_emit_verdict=False`
(Bug Triage v0)?**
If Bug Triage doesn't emit verdicts, does authority
enforcement need special handling for its EXECUTE actions?

---

## 14. Recommended Next Research

Based on evidence, not preference.

> **P0 / P1 semantics (Rigby S1272 SIGN edit).** The P0 / P1 /
> P2 ordering below reflects **dependency and uncertainty
> reduction** across the research library, not preference for
> any particular design option in §9. Each recommended mission
> below unlocks a downstream mission by closing the largest
> current unknown. P0 means "highest ROI on unknown closure per
> unit of effort"; P1 means "unlocked once P0 lands"; P2 means
> "deferrable without blocking the critical path." None of the
> priorities constitute a recommendation to pick Option A, B, C,
> D, E, or F from §9 — those choices happen in §14.3.

### 14.1 Symbol Mapping Option Selection Design (P0 — recommended next)

**Scope.** Take the 5 options from S1270 §5 and produce a
design decision doc: pick one (or hybrid), scope the v0
employee + layer + surface, sequence the migration.

**Why P0.** Per F6 + F9 + F11: Symbol Mapping is the
load-bearing predecessor to every enforcement design decision.
Every design option in §9 depends on which Symbol Mapping
option is chosen (Option E enables only 5 modes; A/B/C/D enable
all 12). The 33-incident historical catalog collapses to a
single root cause (Authority Symbol Mapping Gap) with 7
incidents; closing it is the largest single-mission ROI on the
platform's outstanding research library.

**Prerequisites.** None beyond S1270 (already shipped).

**Expected outcome.** A design decision doc (not a research
doc) with Chris's ratification, following the same pattern
S1270 §11.1 already named. Rigby SIGN review at close.

**Type.** Design decision — first design mission in the STAGE
2 arc per ARCHITECTURE_INDEX §9.

### 14.2 Actor Role Propagation Design (P1)

**Scope.** Two layers per Rigby S1272 SIGN clarification:
- **(i) Role schema + propagation contract** — define what
  each of executor_actor / sponsor_actor / principal_user
  means across boundary transitions; specify the propagation
  contract (context dict shape, thread-local vs. explicit
  param, defaults on gap). *This layer can run in parallel
  with §14.1 Symbol Mapping selection because it does not
  depend on which mapping option is chosen.*
- **(ii) Implementation across boundaries** — actually wire
  the propagation through §3's 20 candidate boundaries and
  close S1271 F6 drop boundaries wherever possible. *This
  layer depends on §14.1 shipped, because where the WHAT
  signal is emitted affects where WHO can be attached.*

**Why P1.** Layer (ii) depends on §14.1 (Symbol Mapping)
because role requirements per mode (F10) inherit from Symbol
Mapping choice. Layer (i) does not depend on §14.1.

**Prerequisites.** Layer (i): none beyond S1271 §8.5. Layer
(ii): §14.1 shipped.

### 14.3 Authority Enforcement Design Decision (P1)

**Scope.** After §14.1 + §14.2 land, this mission converts
this doc's design space into a design decision: pick option
A-F, pick modes, pick precedence, ship enforce-mode PR set.

**Why P1.** Depends on §14.1 + §14.2. This IS the enforce-mode
work that this research scoped.

**Prerequisites.** §14.1 + §14.2 + prereq DAG per §11.

### 14.4 Cross-Plane Composition Design (P2 — deferred)

**Scope.** Per §7.5 + §11 prereq #14. Answer the 8 composition
questions. Design plane precedence policy.

**Why P2.** Non-blocking for initial enforce-mode ship; adds
complexity that can be deferred.

### 14.5 Explicitly NOT recommended as immediate next research

- **Trust Propagation** (ARCHITECTURE_INDEX §5.3) — waits for
  §14.3.
- **Employee Delegation Design** (ARCHITECTURE_INDEX §5.5) —
  waits for §14.3.
- **Memory Architecture** (ARCHITECTURE_INDEX §5.4) — waits
  for §14.3.
- **Adding fields to OpsRun / audit models as implementation-first**
  — violates the research discipline. Any schema change must go
  through §14.1 → §14.3 gate.

---

## 15. Appendix

### 15.1 Explicit answers to mission-spec Q1-Q12

**Q1 — What would authority enforcement actually mean?**
§4 enumerates 12 modes across prevention (hard-block,
freeze-tool/queue/platform, pause-employee), detection (soft-fail,
warn-mode, degrade-evidence, retro-audit), escalation
(require-approval, defer-mission), evidence (observe-only), and
human review (require-approval).

**Q2 — What authority inputs exist today?**
§2 inventories 24 inputs. Distribution: 13 RUNTIME-VERIFIED + 7
OBSERVATION-ONLY + 3 ASPIRATIONAL + 1 UNKNOWN + 8 GAPS.

**Q3 — What enforcement boundaries are possible?**
§3 inventories 20 boundaries (17 original + 3 Rigby SIGN
additions: WebSocket, Fleet, Spider) with identity + action
signal quality per boundary. Cross-referenced with S1271 F6
drop boundaries.

**Q4 — What enforcement modes are possible?**
§4 inventories 12 modes with existing precedents (8) and
missing analogs (4). Mode × boundary compatibility matrix (204
cells) per sub-agent 2 §C.

**Q5 — How should AuthorityLevel behave?**
§5 enumerates 4 interpretations per level (16 total) with
risks. **This doc does not choose.** Level ordering (OBSERVE <
RECOMMEND < EXECUTE) is defensible; PROHIBITED orthogonality
vs. sequencing is unresolved.

**Q6 — How do the three actor roles affect enforcement?**
§6 walks through 11 canonical scenarios × 3 roles + audit path.
Every scenario has at least one role Ambiguous, Missing, or
Inferred. §6.4 identifies 3 scenarios with irreducible
ambiguity today.

**Q7 — How does enforcement relate to existing governance planes?**
§7 inventories the 4 planes' interactions. 1 existing
cross-plane touch (autonomy → budget one-way sync). 8 new
composition questions authority enforcement introduces. No
precedence policy.

**Q8 — What historical failures would each enforcement style have prevented?**
§8 consolidates 33-incident matrix. Coverage rankings per §8.2
(warn-mode 94%, hard-block 76%, freeze modes 21-33%). Largest
cluster is Authority Symbol Mapping Gap (7 incidents; F6).

**Q9 — What are the major design options?**
§9 enumerates 6 options (A MissionRunner-centered, B
ToolDispatcher-centered, C Audit-first, D Human-approval, E
Multi-layer, F Governance-plane composition). Cross-comparison
matrix per §9.7. **This doc does not choose.**

**Q10 — What should NOT be enforced yet?**
§10 enumerates 15 anti-patterns with source citations.

**Q11 — What minimum prerequisites exist before enforce-mode?**
§11 lists 15 prereqs as a DAG (not a checklist per F11).
Critical path per §11.2.

**Q12 — What should the next research mission be?**
§14.1 — Symbol Mapping Option Selection Design (P0). Rigby
SIGN review at close.

### 15.2 Cross-reference

| Prior research | Relationship |
|---|---|
| S1264 (`docs/handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md`) | Warn-mode shipped; named symbol mapping as prereq for enforce-mode. This doc verifies the code-level assertion at `mission_runner.py:895-899` remains load-bearing. |
| S1268 `employee_os_communication_substrate_audit.md` §7 | 12 incident classes cross-referenced in §8 |
| S1268 `employee_os_collaboration_patterns.md` §7 | 29 failure modes; overlapping incidents deduplicated in §8.1 |
| S1268 `employee_os_communication_protocol_sketch.md` §8.1 | Auditor's authority-dict absence of `create_human_attention_item` referenced as evidence of intentional design |
| S1269 `governance_authority_evolution.md` | 4 governance planes framing (F1) load-bearing for §7. F2 (KillSwitch write-only) spot-verified in §7.2. F3 (35 gates, none authority-contract-layer) load-bearing for F3. F4 (budget-autonomy desync risk) load-bearing for §7.5 |
| S1270 `symbol_mapping_architecture.md` | 5 mapping options + 20 boundaries + 68 authority strings = INPUT premise for this doc. F6 (Symbol Mapping is the load-bearing blocker) confirmed by this doc's F6 |
| S1271 `actor_identity_attribution_architecture.md` | 3-role vocabulary (§8.5) + 22 attribution surfaces + F1 OpsRun-no-user-FK + F6 3 drop boundaries + F11 role-clarity warning = INPUT premises for this doc. §11 F11 explicit anti-pattern against single-actor-label conflation carried forward |
| `docs/research/ARCHITECTURE_INDEX.md` §5.2b | Named this mission as P0 next research; this doc closes that gap. Index v3 update per §10.1 |
| `docs/EMPLOYEE_OS_PRIMITIVES.md` §2 anti-duplication | §9 Option D explicitly reuses HAI (not new approval model); §10 anti-pattern #10 explicit |

### 15.3 Documentation drift surfaced

| Item | Source A says | Source B (runtime) says | Resolution |
|---|---|---|---|
| KillSwitch consumers | Sub-agent 4: "zero dispatch consumers"; S1269 F2: same | Direct verification: 5 read sites (governance.py:2192, 2370, 2508; intelligence.py:1569, 1717) — ALL in management/cleanup contexts (list, deactivate, expire); zero dispatch enforcement | S1269 F2 stands. Reads exist but are not enforcement. |
| Bug Triage step 4 line range | Sub-agent 1: `bug_triage.py:396-453`; earlier docs same | Consistent with prior verification | Confirmed |
| LLMEnforcer method line | Sub-agent 1: `check_budget()` at `llm_enforcer.py:200-260` | Direct read: `enforce_real_ai()` at line 139; budget_freeze_active check at 200-221; fail-open at 237-238 | Method is `enforce_real_ai`, not `check_budget()`. This doc uses `enforce_real_ai` where precise; retains `check_budget()` name in cross-references to S1269 to avoid drift with prior audit. |
| HumanAttentionLifecycleService LOW_RISK_SOURCES | Sub-agent 1: 5 entries per S1269 §5.4 | Direct read: 5 entries at lines 63-69 (spider_insight, content_review, blog_review, trend_analysis, observation) | Confirmed 5 |
| AUTHORITY_LEVEL enum runtime references | Sub-agent 3: 1 (shape-counter at mission_runner.py:864-867) | Independent grep: same finding | Confirmed |

### 15.4 Verifier-loop pass notes

**Sub-agent tasking:** 5 parallel Explore agents. Each prompt
explicit "no design decision" + "actor roles NEVER collapsed"
+ "Symbol Mapping and Actor Attribution are INPUTS."

**Load-bearing claims spot-verified by Claude:**
- `LLMEnforcer.enforce_real_ai` at `llm_enforcer.py:139`;
  budget_freeze_active check at 200-221; **fail-open at 237-238**
  (`except Exception: pass  # Never block LLM calls due to
  budget check errors`) ✓
- `HumanAttentionLifecycleService._auto_approve_low_risk_items`
  at `human_attention_lifecycle.py:223` (invoked from beat at 122);
  LOW_RISK_SOURCES = 5 entries at 63-69; AUTO_APPROVABLE_TYPES =
  5 entries at 72-78; ML confidence check at 272 ✓
- KillSwitch reads at 5 sites (`governance.py:2192, 2370, 2508`;
  `intelligence.py:1569, 1717`) — all management/cleanup contexts,
  NOT dispatch. S1269 F2 stands ✓
- `MissionRunner._emit_authority_contract_event` at
  `mission_runner.py:835-900`; iteration at line 870; explicit
  comment at 895-899 ("Enforce-mode requires future symbol
  mapping (S1264 discovery)") — load-bearing ✓
- AuthorityLevel enum runtime consumers: exactly 1 site
  (mission_runner.py:864-867 shape-counter) verified via grep;
  test-file references excluded ✓

**Sub-agent drift corrected:**
- Sub-agent 1 named `LLMEnforcer.check_budget()`; actual method
  is `enforce_real_ai()`. §2.1 uses the actual method name;
  cross-references retain check_budget() where consistent with
  prior S1269 audit terminology.
- Sub-agent 4 stated GovernanceEngine._sync_budget_flags line
  range as 2285-2322; verified consistent with S1269's citation.
  Both stand.

**Self-verifier pass (one round) before finalization
identified and fixed:**
- Initially had 5 options in §9; expanded to 6 (Option F —
  Governance-plane composition) after §7.5's composition
  questions inventory made it a distinct axis. Options A-E were
  authority-plane-scoped; Option F is cross-plane.
- §5 initially only enumerated interpretations; F1 clarification
  added ("policy metadata today, not enforcement metadata") to
  reinforce that current state is observation-only.
- §14 initially had 5 recommendations; consolidated §14.3 into
  §14.1 (Symbol Mapping Option Selection Design as P0); §14.2
  and §14.3 are downstream P1s. §14.4 (Cross-Plane) is P2
  deferred per §11 prereq #14.
- Verified that each of the 6 options in §9 is presented with
  neutral language ("What it prevents / misses / requires /
  reuses") and no "recommended" or "best" language creeps in.
  Corrected two instances where §9 had "strongest option" for
  Option C (hybrid) — replaced with neutral "combined coverage."
- §4.5 initially listed fail-open as a "problem"; corrected to
  "precedent" per F8 discipline (design decision, not automatic
  bug).

**Status after self-verifier pass.** Publishable as draft.
Rigby independent SIGN review pending — verdict + folded edits
will be recorded in §15.5.

### 15.5 Rigby SIGN review record

**Verdict: SIGN-with-edits.** Rigby overall confidence: **Medium**
(read §8, §9, §10, §11 prereq DAG, §14 fully; plus keyword sweep
for websocket / channel_layer / fleet / consumer / spider that
surfaced the largest gap).

**Rigby's SIGN summary:**
- **Strongest finding:** F8 (LLMEnforcer fail-open precedent
  framing) + §10 anti-pattern framing. Anchoring "fail-open vs.
  fail-closed is not philosophical" to an in-production
  precedent while remaining neutral (not prescribing).
- **Weakest section:** §3 boundary completeness — WebSocket /
  channel-layer, Fleet, and Spider boundaries were absent from
  sub-agent 2's original 17-row inventory. Folded via §3 rows
  18-20.
- **Biggest architectural risk (folded via §3 addition + §4.4
  extension note):** boundary gaps get mistaken for "covered by
  Option X." Options A/B/E look complete but silently miss
  real-time / service-to-service / spider-ingestion paths.
- **Most dangerous premature implementation (folded via §10
  Tier-0 callout):** #1 (blocking all model writes) is highest
  blast radius — destroys the audit substrate itself; #8
  (enforcement before symbol mapping) close second; #15 (silent
  enforcement) third-tier hazard.
- **What I got wrong per Rigby:** §8.4 cluster conclusion "all
  enforcement modes equally blocked without Symbol Mapping"
  overgeneralized. Precise claim: prevent-modes blocked; audit /
  warn modes remain partially valuable (S1264 counter-example).
  Folded.
- **§7 misclassified incident question:** Rigby declined to
  re-grade specific incidents without a targeted second pass —
  flagged "overgeneralized cluster conclusion" as the risk
  instead of any specific YES/PARTIAL/NO misgrade. Folded via
  §8.4 rephrasing.

**8 must-fix edits folded (see frontmatter verifier_loop for full list):**
1. §3 boundaries 18-20 added (WebSocket, Fleet, Spider).
2. §9.0 neutrality guardrail boilerplate.
3. §9.1 + §9.2 signal-quality-maintenance failure-mode entries.
4. §9.6 policy-ossification risk.
5. §8.4 cluster-conclusion rephrasing (prevention vs. audit).
6. §10 Tier-0 hazards callout.
7. §6.1 role-propagation rule-of-thumb.
8. §14 P0/P1 semantics note + §14.2 (i)/(ii) split.

**Optional edits deferred (2):**
- Boundary coverage matrix appendix (options × boundaries with
  ✔/△/✖). Deferred — §4.4 note + §9's per-option "What it
  misses" already cover this at coarse granularity; explicit
  matrix would be design-mission scope.
- §9 paragraph on two-layer enforcement (WHAT at tool + WHO at
  request). Deferred — §9.5 (Option E Multi-layer) already
  covers this shape; adding a separate paragraph would risk
  reading as recommendation.

**§14.2 split guidance folded:** kept overall P1 label; added
explicit (i) role schema + propagation contract (parallel-safe
with §14.1) vs. (ii) implementation across boundaries
(dependency-blocked) split in the §14.2 body per Rigby's
preferred framing.

**Rigby SIGN-clean on (no edits required):**
- F8 fail-open precedent framing.
- §10 anti-pattern framing.
- §14 ordering (P0 Symbol Mapping → P1 Actor Role Propagation +
  Authority Enforcement Design Decision → P2 Cross-Plane
  deferred).
- Neutrality language on 6 options (no accidental
  recommendations found across 35+ role-vocabulary uses and
  6 option write-ups).
- Actor role vocabulary usage.

**Not re-invoked (offered but declined):**
- Rigby offered a targeted second pass on specific incident
  YES/PARTIAL/NO regrades if the incident matrix was made
  available. Not invoked — §8.4 rephrasing already addresses
  the overgeneralization; specific regrades can happen at
  §14.3 (Authority Enforcement Design Decision) time when the
  cluster is being consumed for a decision.

### 15.6 Evidence integrity notes

- Five parallel Explore sub-agents produced the source material
  for §2-§8.
- No runtime state modified; research-only per mission spec.
- All "today" / "is" language describes runtime state verified
  by direct file read; all "would" / "could" language is
  research description of a design space, marked as such.
- Every option in §9 is presented with neutral tradeoff analysis;
  no "recommended" or "best" language.
- Executor_actor / sponsor_actor / principal_user are kept
  separate throughout §6, §7, §11, §12. No section collapses
  them into a single "actor" label.
- Symbol Mapping (S1270) and Actor Attribution (S1271) are
  treated as INPUT premises; this doc does not solve either.
- No implementation plan; no schema changes proposed; no PR
  scoping.
- No code changes made writing this doc. No files touched
  besides this one.
