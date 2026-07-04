---
title: "Authority Enforcement Cross-Plane Composition Design"
status: draft
authority: research-design
category: child_audit_design
session: 1903
child_slot: P3_cat_c
domain_slug: authority_enforcement
research_group: 1900
mission_type: cross_plane_composition_design
parent: 1900_authority_enforcement_domain_scoping.md
siblings:
  - 1901_authority_enforcement_cat_a_actor_role_propagation_design.md
  - 1902_authority_enforcement_cat_b_authority_enforcement_design_decision.md
consumes:
  - docs/research/authority_enforcement_design_space.md   # S1272 §7.5 8 composition Qs + §14.4 P3 scope + §7.6 5 composition modes
  - docs/research/governance_authority_evolution.md      # S1269 F1 4 planes don't compose + F2 KillSwitch write-only + F4 desync risk
  - docs/research/domains/authority_enforcement/1901_authority_enforcement_cat_a_actor_role_propagation_design.md  # P1 3-role schema + propagation contract + 20-boundary register
  - docs/research/domains/authority_enforcement/1902_authority_enforcement_cat_b_authority_enforcement_design_decision.md  # P2 D86-D93 + §17 Enforcement Binding Points map
verifier_loop: |
  MC-1 verifier-loop applied pre-Explore + post-Explore per playbook
  §14 REQUIRED discipline. Pre-Explore verified: S1272 §7.5 8 Qs
  authoritative list + S1272 §14.4 P3 scope + S1902 D88 partial
  precedence K>A>F>B>H + S1902 D90 3-value enum + S1902 D91 two-tier
  max-strictness composition + S1269 F1 4-planes-don't-compose + F4
  desync-risk framing. Post-Explore corrections applied: (1) S1902
  §14.2 KillSwitch "4 dispatch-consumer" classification is imprecise
  — direct-verified all 6 sites are management/audit/cleanup, zero
  enforcement dispatch (see §14.1 KNOWN DRIFT); (2) Explore 2 F4
  "REFUTES one-way sync" is a misread — F4 is desync-risk framing,
  not sync-direction refutation; one-way governance→budget sync
  confirmed at `governance.py:2515-2520`; (3) Explore 6 KillSwitch
  classification "2 WRITE + 2 dispatch + 2 audit" corrected against
  direct verification: all reads management/audit/cleanup contexts
  (§14.1). Six parallel Explore probes fired per playbook §13 covering
  autonomy × killswitch × authority (Q1 + Q4), budget × authority
  layering (Q2), HAI creation × RECOMMEND × freeze × ml_confidence
  (Q3 + Q5 + Q6), Employee OS MissionRunner toggle composition (Q7),
  Discord command dispatch × authority (Q8), and cross-plane
  precedent + composition mode inventory (plane precedence policy).
  All 8 S1272 §7.5 composition questions receive designed
  resolutions in §7. KillSwitch enforcement reader design lands as
  §7.4 D94 with deferred-execution rationale (T2 slot per S1902 D88
  R.AUTHORITY.KILLSWITCH-DISPATCH-EXPANSION reference).
owner: claude (drafted S1903; Rigby SIGN cycle 1 pre-commit)
last_updated: 2026-07-04
---

# Authority Enforcement Cross-Plane Composition Design — Group 1900 P3 Cat C

> **THIRD child audit under Group 1900 Authority Enforcement Design
> Space arc.** Executes parent §5.3 P3 scope (S1272 §14.4 Cross-Plane
> Composition Design). Applies playbook §11.2 20-section child audit
> template (standard shape, not design-decision-modified) since P3
> is research + design and is Chris-ratifiable in a single agree-all
> or per-question fold pass — not the multi-verdict D-gate framing
> that P2 required.
>
> **Load-bearing consumption inputs.** (a) S1272 §7.5 8 composition
> questions authoritative list; (b) S1272 §14.4 Cross-Plane
> Composition Design P3 scope; (c) S1902 D86-D93 as authority-side
> input — specifically D88 partial precedence (`KillSwitch > authority
> PROHIBITED > freeze-platform > authority RECOMMEND > HAI
> auto-approve`) + D90 3-value `enforce_authority_mode` enum + D91
> two-tier AIEmployee + MissionRunnerConfig max-strictness
> composition; (d) S1901 §7.3 20-boundary propagation-contract
> table + drop-boundary register (Boundaries 10 + 17 async signal
> register + post-mission retrospective); (e) S1269 F1 4 governance
> planes don't compose framing.
>
> **What this doc delivers.** For each of the 8 S1272 §7.5
> composition questions: a designed resolution with rationale +
> alternatives-rejected + reversibility posture. A plane precedence
> policy that generalizes P2 D88's partial precedence into a full
> cross-plane resolution order. A KillSwitch enforcement reader
> design (D94) with deferred-execution rationale (T2 slot). §17
> Duplicate or Overlapping Systems folded as the plane precedence
> policy P3 first-class deliverable (analogous to P2's §17
> Enforcement Binding Points map).

## 1. Executive Summary

Group 1900 P3 Cat C ships the cross-plane composition contract that
completes the authority enforcement design space started at S1900
parent scoping and advanced at S1901 (Cat A actor role propagation)
+ S1902 (Cat B authority enforcement mode + option pick). Four
governance planes coexist in the platform today per S1269 F1
(Autonomy, Authority, Budget, HAI) plus KillSwitch as an operator
kill vector; they do not compose. P3 answers 8 composition
questions from S1272 §7.5 and designs a canonical plane precedence
policy so P4 Cat F separation-boundary posture audit + post-arc
implementation work have a resolved cross-plane contract to
reference.

**The 8 answers (Q1–Q8) — designed resolutions.**

- **Q1. Authority × Autonomy priority.** Autonomy precedes
  authority. `GovernanceState.mode='freeze'` or `'safe_mode'`
  short-circuits the mission dispatch envelope before any authority
  read fires. Authority enforcement is a per-action-class gate;
  autonomy is a scope-of-work gate. Different granularity, but
  autonomy operates at a larger blast radius, so it evaluates first.
- **Q2. Authority × Budget layering.** Budget precedes authority
  on the LLM sub-path (`LLMEnforcer.enforce_real_ai` at
  `llm_enforcer.py:139` runs before authority is checked); authority
  precedes budget on the pre-dispatch gate (Boundary 6 in Option A
  scaffolding, Boundary 2 in Option B graduation). This is intentional
  asymmetry: budget is an LLM-call-time throttle; authority is a
  mission-time contract. Both fail-open per F8 precedent (`llm_enforcer.py:237-238`,
  `:263-264`; extended by D89 authority fail-open).
- **Q3. RECOMMEND-triggered HAI auto-creation.** Deferred with
  policy. Authority RECOMMEND emits `authority_recommend_observed`
  (post-D-graduation) but does NOT auto-create an HAI. Explicit
  HAI creation is a downstream consumer choice (Option D graduation
  gates it). Rationale: coupling authority-level observation to HAI
  creation would create a hidden 4th plane trigger before D91
  per-employee opt-in landing is stable.
- **Q4. Authority × KillSwitch precedence.** KillSwitch precedes
  authority (K > A per S1272 §7.5 Q4 default answer + S1902 D88
  partial precedence entry). But **precedence is aspirational
  today** — direct verification (§14.1) shows all 6 verified
  KillSwitch reads are management/audit/cleanup contexts, zero
  are enforcement dispatch gates. D94 (§7.4) designs the
  enforcement reader as a deferred T2 slot (R.AUTHORITY.KILLSWITCH-DISPATCH-EXPANSION
  from S1902 §19 T-tier queue).
- **Q5. Freeze × HAI auto-approve.** Freeze does NOT block HAI
  auto-approve today per Explore 3 verification (`human_attention_lifecycle.py:240-296`
  reads only `HumanSystemState.review_mode`, not `GovernanceState.mode`).
  P3 designs that freeze SHOULD block auto-approve under post-arc
  T-tier follow-on but does not require the change in P3 scope. Reason:
  auto-approve is a per-item action; extending it to read
  `GovernanceState.mode` is an additive gate change that follows the
  P2 D90 toggle-shape precedent.
- **Q6. Authority × LOW_RISK_SOURCES × HAI auto-approve.** Deferred
  with policy. LOW_RISK_SOURCES (5 entries at
  `human_attention_lifecycle.py:63-69`) implicit-authority
  classification (each source implies OBSERVE or RECOMMEND) is
  documented as a P3 gap and queued as T3 follow-on. Rationale: the
  5 sources predate the AuthorityLevel enum; retrofitting explicit
  authority tags is Option D graduation-scope work.
- **Q7. Authority × Employee OS MissionRunner enforcement toggle
  composition.** Two-tier composition per S1902 D91 lands at P3
  ship: `AIEmployee.enforce_authority_mode` (default) + effective
  mode resolution happens at MissionRunner init (line 601-638), not
  at event-emission time. Composition rule confirmed: max-strictness
  ordering `"observe"` < `"warn"` < `"enforce"` at
  `mission_runner.py:__init__` per §7.7. All 4 employees land at
  `"warn"` per S1902 D91.
- **Q8. Authority × Discord command dispatch.** Formal deferral
  per Explore 5 evidence: Discord dispatch has zero
  MissionRunner path (0 direct invocations), zero KillSwitch
  reads, and zero `action_class` signaling. Three upstream
  prerequisites block Q8 finalization (Symbol Mapping runtime
  registry, per-Discord-command action_class labeling, principal_user_id
  propagation to Discord actor path). Registered as T2 follow-on
  R.AUTHORITY.DISCORD-DISPATCH-ENFORCEMENT-INSTRUMENTATION.

**Plane Precedence Policy (P3 first-class deliverable — §17).**

The canonical resolution order when planes disagree:

```
KillSwitch > Autonomy > Authority (PROHIBITED) > Freeze > Authority (RECOMMEND) > Budget > HAI auto-approve
```

This generalizes P2 D88's partial precedence into a **full cross-plane
policy**. KillSwitch is the operator-kill vector (highest but
aspirational — see D94 deferred T2 slot). Autonomy operates at
mission-dispatch envelope. Authority PROHIBITED is a hard-block
per D90 `"enforce"` mode. Freeze is compositionally distinct from
Autonomy (Freeze is a specific autonomy `mode` value; here we treat
it as a distinct short-circuit at LLM-call time). Authority RECOMMEND
does NOT auto-block. Budget is an LLM-call-time throttle. HAI
auto-approve is the softest layer (async, out-of-mission).

Per §17.2 sub-precedence rules cover four sub-cases:
- **KillSwitch × Freeze (§17.2.1).** KillSwitch wins (operator kill
  supersedes governance state).
- **Autonomy `safe_mode` × Authority `EXECUTE` (§17.2.2).** Autonomy
  wins (safe_mode is more restrictive than authority EXECUTE).
- **Authority PROHIBITED × Freeze × Budget (§17.2.3).** Authority
  PROHIBITED wins pre-LLM; budget wins at LLM-call-time (per Q2
  asymmetric layering).
- **RECOMMEND × HAI auto-approve × Budget (§17.2.4).** RECOMMEND
  emits observation; auto-approve fires async in beat; budget
  gates any LLM sub-call inside auto-approve. All three fire
  sequentially without veto composition.

**KillSwitch Enforcement Reader Design (D94 — §7.4).**

D94 recommends the reader design (canonical shape + insertion point)
but scopes execution to T2 R.AUTHORITY.KILLSWITCH-DISPATCH-EXPANSION
slot per S1902 §19 T-tier queue. Rationale: shipping the reader
requires simultaneous changes at 4+ dispatch surfaces (Tool
dispatcher, PA tool handler, MissionRunner pre-dispatch, Fleet
dispatch), which exceeds P3 scope (research + design, no
implementation per playbook §14.5 no-implementation rule).

**Chris-gate.** Standard ratification at close (not multi-verdict
D-gate) — each of Q1–Q8 answers + Plane Precedence Policy + D94
receives an "agree-all" or per-question fold pass. If Chris signs
"agree all", 9 designed resolutions ratify simultaneously.

**Non-goals.** No new runtime code. No modification of
MissionRunner (D91 field additions ship at P3 documentation, not
runtime PR). No modification of `_auto_approve_low_risk_items`
per Q5 designed policy (queued as T-tier follow-on).

**Post-arc queue extension.** P3 extends the S1902 §19 T-tier
queue by 3 items (T2 R.AUTHORITY.DISCORD-DISPATCH-ENFORCEMENT-INSTRUMENTATION
+ T3 R.AUTHORITY.LOW-RISK-SOURCES-EXPLICIT-AUTHORITY-TAGS + T3
R.AUTHORITY.AUTO-APPROVE-FREEZE-GATE) + preserves the S1902 T2
R.AUTHORITY.KILLSWITCH-DISPATCH-EXPANSION reference.

## 2. Domain Purpose

Cross-plane composition is the design contract that resolves
disagreements between the 4 platform governance planes (Autonomy,
Authority, Budget, HAI) + KillSwitch when they cast conflicting
opinions on whether a runtime action should proceed. Per S1269 F1
these 4 planes exist independently today; there is exactly one
existing cross-plane touch (`GovernanceEngine._sync_budget_flags` at
`governance.py:2285-2322`, one-way autonomy → budget). Per S1272
§7.5 there are 8 open composition questions (Q1–Q8 in §1
Executive Summary) that authority enforcement graduation cannot
proceed without answering.

P3's domain purpose is threefold:

1. **Answer the 8 composition questions with designed resolutions.**
   S1272 was a research inventory ("this doc does NOT answer them");
   P3 is the design pass that closes the design gap.
2. **Design a plane precedence policy.** Generalize P2 D88's
   partial precedence into a full cross-plane resolution order that
   downstream implementation (P4 Cat F posture audit + post-arc
   T-tier slots) can reference.
3. **Design the KillSwitch enforcement reader (D94).** P2 D88
   recommended precedence-first + scoped the reader expansion to T2
   slot; P3 finalizes the reader shape + insertion point + defers
   execution rationale.

**Explicit non-purposes.**

- Not a runtime PR. No implementation of the composition policy at
  P3 close. All landing artifacts are doc-only.
- Not an ADR for post-arc T-tier items. Each T-slot item is Chris-gated;
  execution PR structure is not P3 scope.
- Not a re-design of the 4 planes. P3 respects the plane boundaries
  established by S1269 (Autonomy = `GovernanceState`, Authority =
  `JobContract.authority`, Budget = `SystemConfiguration.budget_freeze_active`,
  HAI = `HumanAttentionItem`). P3 designs how they compose, not what
  they are.

## 3. Canonical Entry Points

Cross-plane composition is not a single-file entry point today — it
is a distributed contract that would land at the following canonical
insertion sites per P3 designed resolutions:

| Insertion point | Purpose | File:Line | Landing session |
|---|---|---|---|
| `MissionRunner.__init__` effective-mode resolution | Q7 two-tier max-strictness composition | `core/employees/mission_runner.py:601-638` | P3 design; post-arc R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS T1 execution |
| `_emit_authority_contract_event` mode field | Q7 use resolved mode instead of hardcoded `"warn"` | `core/employees/mission_runner.py:894` | Post-arc R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS T1 execution |
| Pre-dispatch authority gate (Boundary 6 under Option A; Boundary 2 under Option B) | Q1 + Q2 + Q4 sequential composition site | `core/employees/mission_runner.py:1030-1054` (Boundary 6) OR `core/services/tool_dispatcher.py:686-751` (Boundary 2) | Post-graduation |
| KillSwitch enforcement reader (D94) | Q4 K > A precedence execution | `core/services/tool_dispatcher.py:686` + Boundary 6 mission_runner insertion + Boundary 3 PA tool handler + Boundary 18 Fleet dispatch | Post-arc T2 R.AUTHORITY.KILLSWITCH-DISPATCH-EXPANSION |
| `LLMEnforcer.enforce_real_ai` fail-open sequencing | Q2 budget × authority asymmetric layering | `core/llm_enforcer.py:139` | Unchanged; documented behavior |
| `_auto_approve_low_risk_items` freeze gate | Q5 freeze × HAI auto-approve composition | `core/services/human_attention_lifecycle.py:240-245` insert `GovernanceState.mode` read | Post-arc T3 R.AUTHORITY.AUTO-APPROVE-FREEZE-GATE |
| `authority_recommend_observed` HAI consumer (Q3 deferred) | Q3 designed no-auto-creation policy | Zero new consumer; explicit non-listener at P3 | N/A — Q3 answer is "do NOT create HAI on RECOMMEND" |
| Discord command dispatch (Q8 deferred) | Q8 formal deferral | `core/services/discord_bot.py` — no new authority gate | Post-arc T2 R.AUTHORITY.DISCORD-DISPATCH-ENFORCEMENT-INSTRUMENTATION |

**Load-bearing observation.** No single "cross-plane resolver"
function exists today, and P3 does NOT propose creating one. The
composition policy lives distributed at the 4 canonical insertion
points above. This is a deliberate design choice: a single-file
resolver would centralize logic that is naturally per-boundary
(each boundary's plane set is different — Boundary 2 sees KillSwitch
+ Authority + Budget; Boundary 6 sees KillSwitch + Autonomy +
Authority; Boundary 16 sees HAI + Freeze + Budget).

## 4. Major Models

Cross-plane composition state lives in six model classes across
five apps. P3 does NOT modify any model schema; it references the
existing shape and designs the composition contract at read-time.

| Model | App / File | Field carrying composition state | Plane |
|---|---|---|---|
| `GovernanceState` | `core/models_governance.py` (lines 22-98) | `mode`: `'normal' \| 'throttle' \| 'freeze' \| 'safe_mode'`; `scope`: `'global' \| 'agent' \| 'desk'`; `scope_target`: str | Autonomy |
| `KillSwitch` | `core/models_governance.py` (lines 101-215) | `is_active`: bool; `target`: `'scheduler' \| 'queue' \| 'agent_family' \| 'publishing' \| 'outbound' \| 'deploys'`; `target_detail`: str; `expires_at`: DateTime | Autonomy (kill sub-vector) |
| `SystemConfiguration` (`key='budget_freeze_active'`, `key='budget_downgrade_active'`, `key='budget_mode'`) | `core/models/system.py` | value flags read by `LLMEnforcer.enforce_real_ai` at `llm_enforcer.py:201-236` | Budget |
| `HumanAttentionItem` | `core/models_human_interface.py` | `status`: 'pending' \| 'viewed' \| 'acted' \| 'expired' \| 'ignored' \| 'deferred'; `urgency`: 'low' \| … ; `source_type`: str; `item_type`: str; `ml_confidence`: float | HAI |
| `HumanSystemState` | `core/models_human_interface.py` (lines 427-471) | `review_mode`: bool (auto-approve short-circuit) | HAI (sub-plane) |
| `JobContract` (frozen dataclass) + `AIEmployee` (frozen dataclass) | `core/employees/jobs.py:73-91` (AIEmployee) + `:94-161` (JobContract) | `authority`: dict[action_class → AuthorityLevel.value]; `enforce_authority_mode` (post-D91) | Authority |
| `MissionRunnerConfig` (frozen dataclass) | `core/employees/mission_runner.py:528-589` | `job_contract`: Optional[JobContract]; `enforce_authority_mode` (post-D91) | Authority (runtime resolution) |
| `OpsRun` + `OpsRunEvent` | `core/models_ops_runs.py:11-88` + `:91-118` | `summary` JSONField (unstructured); `detail` JSONField in OpsRunEvent — captures `schema_version`, `authority_level_counts` per `_emit_authority_contract_event` | Cross-plane audit trail |

**No new cross-plane composition model.** Per EMPLOYEE_OS_PRIMITIVES.md
§4 anti-duplication + playbook §14.5 no-implementation rule, P3
does NOT propose a new `CrossPlaneResolution` or `PlanePrecedenceLog`
model. Composition state lives in the existing 6 models above; audit
trail lives in the existing OpsRunEvent `detail` JSONField.

## 5. Major Services

Six services participate in cross-plane composition today. P3
documents their current-state read-sites + designed composition
contract addition.

| Service | File | Cross-plane read-sites | Composition role |
|---|---|---|---|
| `GovernanceEngine` | `core/services/ops_autopilot/governance.py` | Reads `GovernanceState.mode` (2159, 2177); reads `KillSwitch.is_active` (2192, 2370, 2508, 2545); writes `SystemConfiguration.budget_*` via `_sync_budget_flags` (2285-2322) | Autonomy plane owner; only existing cross-plane writer (autonomy → budget) |
| `OpsIntelligence` | `core/services/ops_autopilot/intelligence.py` | Reads `GovernanceState.mode` (1206-1208); reads `KillSwitch.is_active` (1569, 1717) | Autonomy plane read-only consumer (audit + cleanup contexts) |
| `LLMEnforcer` | `core/llm_enforcer.py` | Reads `SystemConfiguration.budget_freeze_active` (200-221); reads `budget_downgrade_active` (223-236); reads ROI throttle (240-264) | Budget plane enforcement (LLM sub-path); fail-open per F8 (237-238, 263-264) |
| `HumanAttentionLifecycleService` | `core/services/human_attention_lifecycle.py` | Reads `HumanSystemState.review_mode` (240-243); does NOT read `GovernanceState.mode` or budget flags | HAI plane owner; 5-stage internal layering; async beat-driven |
| `MissionRunner` | `core/employees/mission_runner.py` | Reads `JobContract.authority` dict (835-900); emits `authority_contract_observed` events (877); shape-counts AuthorityLevel enum (864-867) | Authority plane observation-only (warn-mode) |
| `ToolDispatcher` | `core/services/tool_dispatcher.py` | Reads `AssistantProfile.get_allowed_tools()` (686-722); does NOT read GovernanceState, KillSwitch, budget flags, or JobContract.authority | Boundary 2 authority-adjacent (tool-level allow-list, not action-class-level) |

**The one existing cross-plane touch — `_sync_budget_flags`.**

`core/services/ops_autopilot/governance.py:2285-2322`. Trigger:
`GovernanceEngine.set_mode()` unconditionally calls
`_sync_budget_flags(mode)` when `scope='global'`. Behavior:

- `mode='normal'` → clear `budget_freeze_active` + `budget_downgrade_active`; set `budget_mode='normal'`
- `mode='throttle'` → set `budget_downgrade_active`; clear `budget_freeze_active`; set `budget_mode='downgrade'`
- `mode='freeze'` or `'safe_mode'` → set both freeze + downgrade; set `budget_mode='freeze'`

Post-expiry sync at line 2515-2520: if global mode expires back to
`'normal'`, re-sync fires.

**Directionality.** Autonomy → Budget one-way. There is NO reverse
sync — flipping `budget_freeze_active` in isolation via
`SystemConfiguration` direct write does NOT update
`GovernanceState.mode`. This is the S1269 F4 desync-risk framing
(operator flipping the budget row by hand can create observation
gap). P3 does NOT propose reverse sync; the asymmetry is
intentional per S1269 honesty note (freeze is a fast-path safety
mechanism that shouldn't wait for governance plumbing).

## 6. Major APIs and Interfaces

Cross-plane composition has no dedicated API surface. Read-sites
listed in §5 are internal Python calls; there is no HTTP or WebSocket
endpoint that exposes "resolve plane precedence for action X."

**Existing surfaces that touch multiple planes (cross-plane
observability, not enforcement):**

| Surface | File:Line | Planes exposed |
|---|---|---|
| `GovernanceEngine.get_status()` | `governance.py:2159-2237` | Autonomy (mode + overrides), KillSwitch (active switches), Budget (budget_flags summary), Throttle counts |
| `governance_tool` PA action `overview` | `core/services/governance_tool.py` (invoked via PA) | Same as get_status() rolled up |
| `platform_config_tool overview` | verified live at S1903 open | Service context + Autonomy + Budget config summary |
| Discord `/status` command | `core/services/discord_bot.py:558` (`StatusCommands`) | Read-only status roll-up (no dispatch gate) |
| Ops autopilot beat tasks | `core/tasks_ops.py` + celery.py schedule | Autonomy expire loop + KillSwitch cleanup loop |

**No new API in P3.** The composition contract lives at internal
call boundaries; exposing a `POST /api/authority/resolve` or
`POST /api/governance/compose` endpoint would violate the
distributed-composition-at-boundary design in §3.

## 7. Runtime Flows — Q1–Q8 Designed Resolutions

Each subsection answers one of the 8 S1272 §7.5 composition
questions with a designed resolution, rationale, alternatives
rejected, and reversibility posture. §7.9 designs D94
(KillSwitch enforcement reader).

### 7.1 Q1 — Authority × Autonomy priority

**Designed resolution.** **Autonomy precedes Authority.**
`GovernanceState.mode='freeze'` or `'safe_mode'` short-circuits at
the mission-dispatch envelope, before any authority read fires.
Under normal-mode operation, autonomy is a no-op and authority
observation runs per S1264 warn-mode.

**Insertion point.** Autonomy short-circuit lives at dispatch-time
in existing consumers:

- `core/services/signal_aggregation_service.py:225` — `if mode in ('freeze', 'safe_mode'): return []` (skip aggregation)
- `core/services/workspace_pipeline_runner.py:44` — `if gov_mode in ('freeze', 'safe_mode'): run.status='cancelled'` (veto execution)
- `core/services/tasks_spiders.py:384` — governance-gated spider dispatch

These sites are pre-mission-runner. Authority observation at
`mission_runner.py:835-900` never fires when autonomy has already
short-circuited the mission dispatch. Result: autonomy precedence is
NATURAL under current runtime code — no new gate required at P3
ship.

**Rationale.**

- Autonomy is a scope-of-work gate (blocks entire operations).
  Authority is a per-action-class gate (blocks specific actions
  within an authorized operation). Different granularity; autonomy
  logically evaluates first because it decides whether the operation
  gets to run at all.
- Existing consumers ALREADY implement autonomy-first behavior
  (three verified sites). P3 designed resolution matches
  observed pattern.
- Autonomy is operator-controlled (via `governance_tool.set_mode`);
  authority is contract-declared (via `JobContract.authority` dict).
  Operator kill takes precedence over declared contract.

**Alternative 1 rejected — Authority precedes Autonomy.** Would
run authority observation first, then autonomy short-circuit. Rejected
because: (a) three existing consumers already sequence autonomy
first at dispatch; (b) fails scope-of-work vs per-action semantic
(authority PROHIBITED shouldn't fire during platform freeze — the
mission shouldn't run at all).

**Alternative 2 rejected — additive veto (either plane blocks).** Would
treat autonomy and authority as parallel vetos. Rejected because:
composition mode taxonomy per S1272 §7.6 recommends precedence for
authority (not additive); precedence enables per-boundary telemetry
distinguishing autonomy blocks vs authority blocks.

**Reversibility.** HIGH. Autonomy-first is the CURRENT behavior at
three verified sites. If future work needs authority-first (e.g., a
new boundary where authority is more restrictive than autonomy), the
policy can be inverted at that specific boundary without breaking
the design.

### 7.2 Q2 — Authority × Budget layering order

**Designed resolution.** **Asymmetric layering.** Budget precedes
authority on the LLM sub-path (`LLMEnforcer.enforce_real_ai` runs
before authority is checked); authority precedes budget on the
pre-dispatch gate (Boundary 6 under Option A scaffolding; Boundary 2
under Option B graduation). Both planes fail-open per F8 precedent.

**Insertion points.**

- **LLM sub-path (budget-first, verified).** `LLMEnforcer.enforce_real_ai`
  at `llm_enforcer.py:139` runs: (1) LUNGS budget hard limit
  (180-192) → (2) `budget_freeze_active` check (200-221) → (3)
  `budget_downgrade_active` check (223-236) → (4) ROI throttle (240-264)
  → (5) LLM call. Authority is NOT checked in this path.
- **Pre-dispatch gate (authority-first, designed post-graduation).** Under
  Option A scaffolding, D90 `"enforce"` mode reads
  `MissionRunnerConfig.enforce_authority_mode` at Boundary 6 pre-step
  execution + gates per level policy binding (D90 §12.5 spec).
  Authority PROHIBITED blocks BEFORE the step's LLM sub-call would
  reach LLMEnforcer's budget check.

**Overlap trace.** For an action X where authority[X]=PROHIBITED AND
`budget_freeze_active=True` AND X requires an LLM call:

- **Pre-graduation (warn-mode today):** LLMEnforcer returns
  `blocked_by_budget=True` at line 212-221 before authority is
  checked. Warn-mode emits `authority_contract_observed` at mission
  start (before LLM call), so authority observation fires but does
  not gate. Result: budget blocks; authority observes.
- **Post-graduation (Option A scaffolding, D90 `"enforce"`):** Pre-dispatch
  gate reads authority; PROHIBITED raises `AuthorityViolationBlocked`
  at gate site BEFORE step invocation. LLM call never fires; budget
  check never evaluates. Result: authority blocks first (correct
  semantic — a prohibited action should never reach LLM regardless
  of budget state).

**Rationale.**

- Budget-first on LLM sub-path is a preserved existing invariant
  (LLMEnforcer has been this shape since S1088 budget-freeze
  landing). Reversing to authority-first inside LLMEnforcer would
  require authority-aware LLMEnforcer (i.e., LLMEnforcer would need
  to know `JobContract.authority`), which violates plane isolation.
- Authority-first at pre-dispatch is the natural graduation shape:
  when D90 `"enforce"` mode lands, authority PROHIBITED is a
  MissionRunner-scoped concept; enforcing it at pre-step gate keeps
  the check at the boundary that has the JobContract handle.
- Fail-open on both planes: F8 established for budget (three
  fail-open sites at `llm_enforcer.py:237-238` + `:263-264` +
  `tool_dispatcher.py:810-814`); D89 extends to authority (see S1902
  §12.4 rationale). Symmetric fail-open bounds blast radius on
  internal errors.

**Alternative 1 rejected — Budget-first everywhere.** Would enforce
budget check at pre-dispatch gate as well. Rejected because: budget
is an LLM-call-time concept; pre-dispatch gate doesn't know if the
step will ultimately call LLM. Would add speculative budget check
that may not correspond to any actual LLM call.

**Alternative 2 rejected — Authority-first everywhere (including
inside LLMEnforcer).** Would make LLMEnforcer read
`JobContract.authority`. Rejected because: violates plane isolation;
requires LLMEnforcer to know Mission context; adds authority read-site
count from 1 (mission_runner) to ~30+ (every enforce_real_ai call
site).

**Reversibility.** MEDIUM. Asymmetric layering is codified as
policy at P3; changing the LLM sub-path to authority-first requires
LLMEnforcer schema change. Changing pre-dispatch gate direction is
a single-file change.

### 7.3 Q3 — RECOMMEND-triggered HAI auto-creation

**Designed resolution.** **Deferred with policy: authority
RECOMMEND does NOT auto-create HAI.** Post-D-graduation, authority
RECOMMEND emits `authority_recommend_observed` event; explicit HAI
creation is a downstream consumer choice gated by Option D
graduation, NOT an automatic coupling.

**Insertion point.** Zero. P3 explicitly designs "no auto-creation
listener" as the answer. `authority_contract_observed` (current
warn-mode) does not emit RECOMMEND-specific events today per Explore
3 verification.

**Rationale.**

- Coupling authority-level observation to HAI creation would
  create a hidden 4th plane trigger before D91 per-employee opt-in
  landing is stable. RECOMMEND authority level is emitted per
  contract shape (D90 3-value enum); it does not carry human-attention
  semantics.
- HAI creation carries recipient assignment (`user`), source
  classification (`source_type`), item type, urgency. RECOMMEND
  authority observation lacks all four (no user context, no
  source_type mapping to LOW_RISK_SOURCES, no urgency). Auto-creation
  would require deriving all four from an abstract authority level,
  which is Option D graduation-scope work.
- The 23 existing HAI creators (per Explore 3 Section A) each set
  `source_agent` explicitly to a system name. Adding a 24th creator
  that fires on authority RECOMMEND observation would inject
  hidden HAI creation from every mission that has RECOMMEND actions
  in its contract, which for 3 of 4 employees (Auditor + Chief +
  Triage) is ≥1 action per mission — flooding the HAI queue.

**Alternative 1 rejected — Auto-create HAI on every RECOMMEND
observation.** Would fire HAI creation from
`_emit_authority_contract_event`. Rejected because: floods HAI queue
per rationale above; couples authority plane to HAI plane before
Option D graduation scoping is Chris-ratified.

**Alternative 2 rejected — Auto-create HAI on RECOMMEND ONLY when
`enforce_authority_mode="enforce"`.** Would gate auto-creation by
D90 toggle. Rejected because: still couples planes; still requires
deriving `source_type` + urgency; runs into same Option D graduation
prerequisite.

**Alternative 3 rejected — Emit `authority_recommend_observed`
event but explicit consumer creates HAI.** Would leave HAI creation
to a bespoke consumer (e.g., `human_interface_service`). Rejected
because: no consumer today; adding one is Option D graduation-scope
implementation work, not P3 research design.

**Reversibility.** HIGH. Adding auto-creation later requires new
consumer of the event. P3 deferred policy does not block future
implementation.

### 7.4 Q4 — Authority × KillSwitch precedence

**Designed resolution.** **KillSwitch precedes Authority (K > A)
per S1272 §7.5 Q4 default answer + S1902 D88 partial precedence
entry.** BUT precedence is ASPIRATIONAL today per direct verification
(see §14.1) — all 6 KillSwitch reads are management/audit/cleanup
contexts, zero are enforcement dispatch gates. Enforcement reader
design lands as D94 (§7.4.1) with T2 slot deferred execution.

**Rationale for precedence direction.**

- Operator kill supersedes any contract-declared authority. If
  Chris/ops activates `KillSwitch(target='outbound', is_active=True)`,
  no employee with `authority['outbound_action']=EXECUTE` should
  proceed. This is the S1269 F1 4-planes context — KillSwitch is
  the operator escape hatch.
- KillSwitch has 6 defined targets (`scheduler`, `queue`,
  `agent_family`, `publishing`, `outbound`, `deploys`) that map to
  broad blast-radius categories. Authority's action-classes are
  narrower per-employee scopes. Broader scope evaluates first.

#### 7.4.1 D94 — KillSwitch Enforcement Reader Design

**Reader shape (canonical).**

```python
def _killswitch_blocks(target: str, target_detail: str | None = None) -> tuple[bool, str | None]:
    """
    Read KillSwitch for the given target + optional target_detail.

    Returns (blocked: bool, reason: str | None).
    Fail-open on internal error per F8 precedent (matches
    LLMEnforcer.enforce_real_ai:237-238 pattern).
    """
    try:
        from core.models_governance import KillSwitch
        qs = KillSwitch.objects.filter(is_active=True, target=target)
        if target_detail:
            qs = qs.filter(target_detail__in=[target_detail, ''])
        active = qs.first()
        if active:
            return True, f"KillSwitch active: {active.reason}"
        return False, None
    except Exception as exc:
        # F8 fail-open precedent — never block dispatch on internal error.
        # Rigby SIGN cycle 1 fold: rate-limited structured log to avoid
        # alert fatigue; severity warning unless invariant breach detected.
        logger.warning(
            "[killswitch_missed_reader:%s] target=%s detail=%s error=%s",
            _boundary_id, target, target_detail, exc,
        )
        return False, None
```

**Insertion points (4 required + 1 optional per S1272 §3.1 map).**

| Boundary | File:Line | Target mapping | Rationale |
|---|---|---|---|
| Boundary 2 (Tool dispatcher) | `core/services/tool_dispatcher.py:686` (before permission check) | `target='queue'` for queued dispatch; `target='outbound'` for tool-triggered external calls | ToolDispatcher is the highest-throughput authority-adjacent boundary per S1902 §17 Row 2 |
| Boundary 6 (Mission runner pre-dispatch) | `core/employees/mission_runner.py:1030-1054` (before `_run_step`) | `target='agent_family'` with `target_detail=employee_handle` | Per-employee kill precedence; matches D91 per-employee opt-in shape |
| Boundary 3 (PA tool handler) | `core/services/tool_dispatcher.py` PA gateway path | `target='queue'` for PA-driven dispatch | PA is the primary end-user surface; kill-switch coverage here is high-signal |
| Boundary 18 (Fleet dispatch) | `core/services/fleet_routing_dispatch.py` | `target='deploys'` mapping | Fleet dispatch is one of the two mentioned expansion surfaces from S1902 §19 T2 slot |
| **Boundary 16 (HAI decide endpoint) — OPTIONAL** (Rigby SIGN fold) | `core/views_human_interface.py:154` decide endpoint | `target` matches whatever execution class the HAI approval would schedule (`queue` / `outbound` / `agent_family` / `deploys`) | ONLY to prevent approving an HAI decision that would schedule execution against an active kill switch; otherwise observation-only. Not required if HAI is downstream-only. |

**Scope of D94 at P3 close.**

- **Included at P3:** reader shape (canonical function with
  rate-limited structured log per Rigby SIGN fold) + 4 required
  insertion points + 1 optional Boundary 16 insertion + fail-open
  policy + target-to-boundary mapping.
- **NOT included at P3:** actual code merge. D94 lands as DESIGN
  ONLY; execution is queued as **T2 R.AUTHORITY.KILLSWITCH-DISPATCH-EXPANSION**
  per S1902 §19 T-tier queue reference. Rationale: 4 required
  insertions + 1 optional × testing at each = ~1-2 sessions of
  implementation work, which exceeds P3 scope (research + design,
  no implementation per playbook §14.5 no-implementation rule).

**Rationale for deferred execution.**

- P3 finalizes the design shape so post-arc T2 slot can execute
  without further design iteration. Chris-gated T-slot execution
  reads P3 §7.4.1 as its ADR-adjacent spec.
- Deferring execution respects arc timebox (1 session per parent
  §5.3 line 707). Landing 4 boundary reads + tests + Rigby SIGN on
  each in one session violates scope.
- The 4 boundaries are independent-enough that T2 execution can
  proceed per-boundary (Boundary 2 first, Boundary 6 second, etc.)
  rather than as an atomic PR. This flexibility is a T2 benefit.

**Alternative 1 rejected — Ship D94 reader implementation at P3.**
Would land 4 boundary reads + tests. Rejected because: exceeds P3
timebox; risks Rigby SIGN drift on runtime code review while P3 is
primarily design.

**Alternative 2 rejected — Defer D94 entirely to xx99 or future arc.**
Would leave KillSwitch dispatch expansion unscoped. Rejected because:
Q4 precedence policy needs a landing reader; without D94, "K > A"
is a policy without an implementation mechanism, which weakens
downstream P4 posture audit.

**Reversibility.** HIGH. Reader function is single-file; insertion
points are additive gate calls that can be removed with a data
migration (removing the read; no schema change).

### 7.5 Q5 — Freeze × HAI auto-approve

**Designed resolution.** **Freeze SHOULD block HAI auto-approve
under post-arc follow-on but does NOT require the change in P3
scope.** Current-state verification: `_auto_approve_low_risk_items`
at `human_attention_lifecycle.py:240-296` reads
`HumanSystemState.review_mode` (line 243), NOT
`GovernanceState.mode`. Freeze does not block auto-approve today.

**Designed insertion (post-arc T3).**

```python
def _auto_approve_low_risk_items(self) -> tuple:
    from core.models_governance import GovernanceState
    from core.models_human_interface import HumanSystemState

    # NEW P3 gate — freeze × HAI auto-approve composition
    global_state = GovernanceState.objects.filter(
        scope='global', scope_target='',
    ).first()
    if global_state and global_state.effective_mode in ('freeze', 'safe_mode'):
        logger.debug("⏸️ [LIFECYCLE] Governance freeze mode; skipping auto-approve")
        return 0, 0

    system_state = HumanSystemState.get_state()
    if system_state.review_mode:
        return 0, 0
    # ... rest unchanged ...
```

**Rationale for "should but not now."**

- Semantic alignment: `mode='freeze'` explicitly means "pause
  autonomous actions." HAI auto-approve is autonomous (no human in
  loop); it fits within the freeze-blocked scope.
- Existing precedent: `signal_aggregation_service.py:225` and
  `workspace_pipeline_runner.py:44` both short-circuit on
  `freeze`/`safe_mode`. Extending to `_auto_approve_low_risk_items`
  maintains the pattern.
- Execution timing: adding a `GovernanceState` read to the auto-approve
  beat task is a single-file, ~5-line change. Simple enough for
  Chris-gated T3 slot; not urgent enough to block P3.
- Existing HAI users are affected: 23 HAI creators would be
  auto-approved during freeze today (Explore 3 Section A). This is
  a real gap, but not a P3 blocker.

**Alternative 1 rejected — Ship the gate at P3.** Would land
runtime PR modifying `human_attention_lifecycle.py`. Rejected
because: playbook §14.5 no-implementation rule for research arcs.

**Alternative 2 rejected — Design policy that freeze does NOT block
auto-approve.** Would preserve current-state as intentional. Rejected
because: violates semantic alignment with `mode='freeze'` scope-of-work
gate; leaves an operational hole where operator kill doesn't stop
autonomous approvals.

**Reversibility.** HIGH. Gate is a 5-line addition; can be removed
with equivalent effort.

**T-slot registration.** T3 R.AUTHORITY.AUTO-APPROVE-FREEZE-GATE.

### 7.6 Q6 — Authority × LOW_RISK_SOURCES × HAI auto-approve

**Designed resolution.** **Deferred with policy: LOW_RISK_SOURCES
implicit-authority classification is queued as T3 follow-on. No
change to `LOW_RISK_SOURCES` (5 entries at
`human_attention_lifecycle.py:63-69`) at P3 close.**

**Current state.** LOW_RISK_SOURCES = `spider_insight`,
`content_review`, `blog_review`, `trend_analysis`, `observation`.
Each source implies an authority level (`spider_insight` ← OBSERVE
authority; `trend_analysis` ← RECOMMEND or OBSERVE). Explore 3
Observation G3 confirmed: no code validates that auto-approve
sources match actual authority grant for a user.

**Rationale for deferral.**

- The 5 sources predate the AuthorityLevel enum (jobs.py:41-51 is
  Session 1264; LOW_RISK_SOURCES is pre-Session 1264).
  Retrofitting explicit authority tags requires:
  1. Adding an authority-level field to the source classification.
  2. Deriving the field for each of the 5 sources (some map cleanly,
     some don't — e.g., `observation` is ambiguous).
  3. Extending `_auto_approve_low_risk_items` to cross-check the
     item's implicit source authority against the recipient user's
     authority grant.
- Step (3) requires per-user authority resolution, which today is
  a JobContract concept (per-employee, not per-user). Users don't
  have JobContracts. This is a bigger design gap that P3 cannot
  close without expanding scope beyond authority × HAI to
  authority × per-user role, which is Group 2000+ Event / Integration
  arc scope per S1900 parent §22 default queue.
- Impact today: minimal. Explore 3 verified 23 HAI creators; the
  auto-approve gate has 8 layers (Section B) that make bypasses
  hard even without explicit authority tags.

**Alternative 1 rejected — Ship explicit authority tags at P3.** Would
add `source_authority: AuthorityLevel` to the LOW_RISK_SOURCES table.
Rejected because: requires per-user authority resolution (see
rationale); exceeds P3 scope.

**Alternative 2 rejected — Remove LOW_RISK_SOURCES auto-approve
entirely.** Would gate all HAI items behind human review. Rejected
because: LOW_RISK_SOURCES has 5 legitimate auto-approve categories
that would otherwise flood the human-review queue; removing the
optimization would degrade user experience without addressing the
authority gap.

**Reversibility.** HIGH. T3 follow-on can add explicit authority
tags additively without breaking the 8-gate composition.

**T-slot registration.** T3 R.AUTHORITY.LOW-RISK-SOURCES-EXPLICIT-AUTHORITY-TAGS.

### 7.7 Q7 — Authority × Employee OS MissionRunner enforcement toggle composition

**Designed resolution.** **Two-tier composition per S1902 D91 lands
at P3 documentation; runtime execution deferred to post-arc T1
R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS slot.** Effective mode
resolution happens at `MissionRunner.__init__` (line 601-638), not
at event-emission time. Composition rule: max-strictness ordering
`"observe"` < `"warn"` < `"enforce"`.

**Composition trace (finalized shape).**

```python
class MissionRunner:
    def __init__(self, config: MissionRunnerConfig, ...):
        ...
        # NEW P3 composition site — Q7 max-strictness resolution
        # Read AIEmployee registry default (via registry lookup, not attr
        # access on config since AIEmployee is registry-scope).
        employee = _EMPLOYEES_BY_HANDLE[config.employee_handle]
        employee_mode = employee.enforce_authority_mode  # D91 6th field
        config_mode = config.enforce_authority_mode  # D91 17th field

        # Max-strictness composition per Q7 designed resolution.
        _ORDER = {"observe": 0, "warn": 1, "enforce": 2}
        if _ORDER[employee_mode] >= _ORDER[config_mode]:
            self.effective_enforce_mode = employee_mode
        else:
            self.effective_enforce_mode = config_mode
        ...

    def _emit_authority_contract_event(self, mission):
        ...
        # UPDATED — use effective mode instead of hardcoded "warn"
        detail = {
            "authority_level_counts": level_counts,
            "prohibited_actions": prohibited_actions,
            "schema_version": AUTHORITY_CONTRACT_SCHEMA_VERSION,
            "contract_version_tag": contract_version_tag,
            "mode": self.effective_enforce_mode,  # was: hardcoded "warn"
        }
```

**4 factory sites to update (post-arc T1 execution).**

Per Explore 4 Section D:

1. `core/employees/mission_runners/docs_cascade.py:713-732` (RIGBY).
2. `core/employees/mission_runners/platform_audit.py:920-936` (PLATFORM_AUDITOR).
3. `core/employees/mission_runners/morning_brief.py:546-562` (CHIEF_OF_STAFF).
4. `core/employees/mission_runners/bug_triage.py:1159-1180` (BUG_TRIAGE_SPECIALIST).

Each factory adds `enforce_authority_mode=<value>` kwarg to
`MissionRunnerConfig(...)` constructor. Default value at P3 ship:
`"warn"` per S1902 D91 rollout pattern.

**Composition semantics verification.**

Test cases per S1902 §12.6 D91 + Explore 4 Section H:

| AIEmployee mode | MissionRunnerConfig mode | Effective mode | Result |
|---|---|---|---|
| `"observe"` | `"warn"` | `"warn"` | Warn-mode fires; observe would have been silent |
| `"warn"` | `"observe"` | `"warn"` | Warn-mode fires; per-mission override rejected as less strict |
| `"warn"` | `"warn"` | `"warn"` | Default S1902 D91 rollout state (all 4 employees at ship) |
| `"warn"` | `"enforce"` | `"enforce"` | Per-mission canary escalation |
| `"enforce"` | `"warn"` | `"enforce"` | Per-employee graduation; per-mission override rejected as less strict |
| `"enforce"` | `"enforce"` | `"enforce"` | Post-graduation steady state |

Composition rule is symmetric and order-independent. Effective mode
is always the STRICTER of the two sources.

**Rationale.**

- Two-tier composition preserves per-employee-registry-default
  discipline (AIEmployee is the immutable registry per
  EMPLOYEE_OS_PRIMITIVES.md §4.1) while allowing per-mission override
  for canary tests (MissionRunnerConfig is per-mission-scope).
- Max-strictness composition is safer than override semantics: a
  registry-level default of `"enforce"` cannot be accidentally
  weakened by a per-mission override to `"warn"`.
- Composition at `__init__` (not at event-emission) means the
  effective mode is stable across mission lifetime — critical for
  telemetry consistency (e.g., audit trail should not have half the
  events at `"warn"` and half at `"enforce"` due to mid-mission mode
  changes).

**Alternative 1 rejected — Override semantics (MissionRunnerConfig
overrides AIEmployee).** Would let a per-mission `"warn"` override a
registry-level `"enforce"`. Rejected because: weakens registry-level
graduation discipline; canary should escalate, not de-escalate.

**Alternative 2 rejected — Ship the composition at P3.** Would land
runtime PR modifying `mission_runner.py` + 4 factory sites. Rejected
because: playbook §14.5 no-implementation rule.

**Alternative 3 rejected — Compose at event-emission time.** Would
resolve effective mode per emission. Rejected because: telemetry
consistency risk. Even though `AIEmployee` and `MissionRunnerConfig`
are frozen dataclasses (Rigby SIGN cycle 1 fold clarification), the
inconsistency vector is NOT dataclass mutation — it's **boundary
rehydration** (a MissionRunner reconstructed mid-mission with a
different config reads a fresh effective mode) OR per-step overrides
that select a different config for later events. Both scenarios
would produce mixed-mode event streams within one mission, breaking
audit trail continuity. Composition at `__init__` is the invariant
that closes both vectors.

**Canonical read discipline (Rigby SIGN cycle 1 fold).** After
composition, only `MissionRunner.resolved_enforce_authority_mode`
(equivalent to `self.effective_enforce_mode` in the sample) is
consulted downstream. Direct reads of
`AIEmployee.enforce_authority_mode` OR
`MissionRunnerConfig.enforce_authority_mode` after composition are
forbidden. This prevents the shadowing/conflict risk where a mid-mission
read picks the wrong source. The T1 R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS
execution PR must audit for direct-read anti-patterns before
merging.

**Reversibility.** HIGH. Composition is a single `__init__` addition;
removable with equivalent effort.

**T-slot registration.** T1 R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS
(inherited from S1902 §19).

### 7.8 Q8 — Authority × Discord command dispatch

**Designed resolution.** **Formal deferral per Explore 5 evidence.
Discord command dispatch remains structurally outside authority
enforcement scope in P3. Registered as T2 follow-on
R.AUTHORITY.DISCORD-DISPATCH-ENFORCEMENT-INSTRUMENTATION.**

**Deferral rationale — 3 blocking prerequisites (per Explore 5 §H).**

1. **No MissionRunner path from Discord.** Explore 5 Section B
   verified zero direct MissionRunner invocations from
   `core/services/discord_bot.py`. Discord commands route via
   `AgentRouter.route()` or `agent.execute()`, which do NOT emit
   `authority_contract_observed` events. Adding authority
   observation to Discord dispatch requires new event emission
   surface — which is Symbol Mapping graduation-scope work
   (S1272 §8.4).
2. **Zero `action_class` signaling on Discord commands.** Explore 5
   Section G verified 6+ Discord commands invoke authority-relevant
   actions (`/ask`, `/create`, `/agent-task`, `/code generate`,
   `/code review`, `/create-content`) but pass only agent name +
   task string. No `action_class` enum in context — required for
   S1270 Symbol Mapping graduation + authority enforcement.
   Retrofitting requires audit of every command + schema change to
   command context.
3. **Discord user identity is nullable principal_user.** Per S1901
   §6.2 (line 553), Discord command is marked "(out-of-table*)" —
   adjacent to the 20-boundary inventory. Discord users lack a
   guaranteed `principal_user_id` (nullable UnifiedUser via
   `discord_id` lookup); authority enforcement requires principal
   propagation which is D91 per-employee-scope, not per-Discord-user-scope.

**Deferral scope (T2 follow-on).**

- Task: R.AUTHORITY.DISCORD-DISPATCH-ENFORCEMENT-INSTRUMENTATION.
- Predecessors: Symbol Mapping runtime registry (S1270 graduation)
  + per-command `action_class` audit + Discord actor path shape from
  S1901 §6.2 finalization.
- Deliverable: authority observation + optional gate on 6+
  authority-relevant Discord commands (`/ask`, `/create`, `/agent-task`,
  `/code generate`, `/code review`, `/create-content`).
- Rigby SIGN needed at T2 execution time.

**Alternative 1 rejected — Design Discord authority gate at P3.**
Would specify the gate shape + insertion point per command. Rejected
because: absence of `action_class` signaling means gate shape depends
on Symbol Mapping runtime registry (S1270 graduation status is
UNKNOWN per S1272 §8.4); designing without the prerequisite would
lock in a shape that graduation could invalidate.

**Alternative 2 rejected — Ban authority-relevant Discord commands
until enforcement lands.** Would remove `/ask`, `/create`, etc.
until D94 lands. Rejected because: user-facing regression; commands
are legitimate use cases; ban would violate S1272 §10 anti-pattern
#12 (never block user-facing surfaces without evidence-based
justification).

**Reversibility.** HIGH. Deferral is documentation-only; T2 execution
is Chris-gated.

**T-slot registration.** T2 R.AUTHORITY.DISCORD-DISPATCH-ENFORCEMENT-INSTRUMENTATION.

### 7.9 D94 KillSwitch Enforcement Reader Design — cross-reference

See §7.4.1 for D94 reader shape + insertion points + fail-open policy
+ target-to-boundary mapping.

## 8. Data Ownership and Lifecycle

Cross-plane composition state ownership follows the 4-plane +
KillSwitch + Authority boundary established in S1269 F1 + S1272
§7.5. P3 does NOT re-scope ownership; it documents the composition
contract that spans owned surfaces.

| Plane | Owner (model + service) | Lifecycle |
|---|---|---|
| Autonomy | `GovernanceState` (models_governance.py) + `GovernanceEngine` (governance.py) | Written by `governance_tool.set_mode` PA action; expires per `expires_at`; auto-reverts to `normal` via TTL cleanup (`governance.py:2495-2505`) |
| KillSwitch (Autonomy sub-vector) | `KillSwitch` (models_governance.py) + `GovernanceEngine` | Written by `governance_tool.activate_kill_switch`; expires per `expires_at`; auto-deactivates via TTL cleanup (`governance.py:2508-2513`) |
| Authority | `JobContract.authority` (frozen dataclass at `jobs.py:94-161`) + `MissionRunner` (mission_runner.py) | Read at mission start (`_emit_authority_contract_event` at line 835-900); observation-only under warn-mode; no runtime write path |
| Budget | `SystemConfiguration` flags (`budget_freeze_active`, `budget_downgrade_active`, `budget_mode`) + `LLMEnforcer` (llm_enforcer.py) | Written via `_sync_budget_flags` (governance.py:2285-2322) OR direct SystemConfiguration write; read at every `enforce_real_ai` call site (30+ per Explore 2) |
| HAI | `HumanAttentionItem` (models_human_interface.py) + `HumanAttentionLifecycleService` (human_attention_lifecycle.py) | Written by 23 creators (Explore 3 §A); lifecycle in 5 stages (created → notified → acknowledged → decided → resolved); async beat-driven |
| MissionRunnerConfig runtime override | `MissionRunnerConfig` (frozen dataclass at `mission_runner.py:528-589`) | Constructed at MissionRunner factory site (4 sites per Explore 4 §D); scope = single mission |
| AIEmployee registry default | `AIEmployee` (frozen dataclass at `jobs.py:73-91`) + `_EMPLOYEES_BY_HANDLE` (line 1327-1332) | Registry-scope; immutable across mission runs per EMPLOYEE_OS_PRIMITIVES.md §4.1 |

**Cross-plane audit trail ownership.**

- `OpsRun` + `OpsRunEvent` (models_ops_runs.py:11-118) captures
  per-mission authority observation via `_emit_authority_contract_event`
  detail field.
- No dedicated "which plane won" field in OpsRun (Explore 6 §H).
  P3 does NOT propose adding one; audit is derived by post-mission
  status querying + event-detail parsing.

## 9. Integrations With Other Domains

Cross-plane composition touches every domain that has a governance
plane surface. P3 documents per-domain integration posture; P4 Cat
F Adjacent / Separation Boundaries CONSOLIDATION audits the seams.

| Domain | Integration surface | Cross-plane touchpoint | Composition role at P3 |
|---|---|---|---|
| Memory (Group 1300) | `AgentLearning` + `LearningInsight` (post-decision learning loop) | HAI plane feeds learning; Authority plane does not (F5 in S1269) | Read-only at P3; T-slot handoff R.AUTHORITY×MEMORY.RECOMMEND-OBSERVATION-LEARNING-BRIDGE deferred to Group 1300 arc if reopened |
| Sports (Group 1500) | Betting dashboard + odds calculator | No authority-plane surface; autonomy-mode-gated dispatch via `signal_aggregation_service.py:225` | Read-only at P3; no P3 handoff |
| Content (Group 1600) | Publishing surfaces (`publishing` KillSwitch target) | KillSwitch dispatch expansion T2 will gate publishing; today write-only per S1269 F3 | Cross-arc handoff to R.CONTENT.KILLSWITCH-PUBLISHING-GATE if scoped by post-arc T-slot |
| HAI (Group 1800) | Boundary 16 decide endpoint + auto-approve gate | Authority-plane read-side at Boundary 16; Q5 + Q6 composition scope | P3 designed policy: freeze SHOULD block auto-approve (T3); LOW_RISK_SOURCES explicit-authority-tags T3 |
| Employee OS | MissionRunner + JobContract | Authority plane owner surface; Q7 two-tier composition + D94 reader Boundary 6 insertion | P3 designed policy: max-strictness at MissionRunner init |
| Frontend | Command Center + Workspace | Read-only status; no authority-plane surface | No P3 integration touchpoint |
| API | REST + WebSocket endpoints | Boundary 2 tool_dispatcher gates | D94 reader Boundary 2 insertion; T2 slot |
| Discord | Discord bot commands | Q8 formal deferral per Explore 5 §H | T2 R.AUTHORITY.DISCORD-DISPATCH-ENFORCEMENT-INSTRUMENTATION |
| Autonomy (S1269 Group) | `GovernanceState` + `KillSwitch` + `governance_tool` | Q1 autonomy-first precedence + Q4 KillSwitch precedence design | P3 designed policy: Autonomy > Authority (Q1); K > A (Q4) |
| Budget | LLMEnforcer + `SystemConfiguration.budget_*` | Q2 asymmetric layering | P3 designed policy: budget-first on LLM sub-path; authority-first on pre-dispatch |

**Cross-arc handoffs from P3.**

- **R.HAI.LEARNING-PLANE-CONTRACT-ADR joint Group 1300+1800.** From
  S1800 close; Group 1900 P3 confirms no direct authority-plane
  contribution to learning loop at P3 scope. Handoff preserved
  unchanged.
- **R.AUTHORITY.DISCORD-DISPATCH-ENFORCEMENT-INSTRUMENTATION T2.** New
  P3 registration. Depends on Symbol Mapping graduation (S1270) +
  per-command action_class audit + Discord actor path shape (S1901 §6.2).
- **R.AUTHORITY.AUTO-APPROVE-FREEZE-GATE T3.** New P3 registration.
  Single-file change; low-priority follow-on.
- **R.AUTHORITY.LOW-RISK-SOURCES-EXPLICIT-AUTHORITY-TAGS T3.** New
  P3 registration. Depends on per-user authority resolution (Group
  2000+ Event / Integration arc).

## 10. Event Flows

Cross-plane composition events are the observable signal for how
planes interact at runtime. P3 documents the event contract; does
not propose new events at P3 scope.

### 10.1 Current-state event inventory

| Event | Emitter | Schema | Consumer |
|---|---|---|---|
| `authority_contract_observed` | `MissionRunner._emit_authority_contract_event` at mission_runner.py:877 | `{schema_version, authority_level_counts, prohibited_actions, contract_version_tag, mode}` | `bug_triage.py` reads via label query filter (accumulates contract shape stats) |
| `run_started` | `MissionRunner._run_all_steps` at line 975-978 | `{trigger}` | Bug triage + docs cascade monitor |
| `step_start` / `step_pass` / `step_fail` | Per-step in `_run_step` | `{step_name, result}` | Post-mission verdict computation |
| KillSwitch activation | `governance_tool.activate_kill_switch` writes model directly; no event emitted | N/A | No consumer today (only management/audit reads per §14.1) |
| GovernanceState mode change | `governance.py:2258-2283` `set_mode` writes model directly; no event emitted | N/A | No consumer today; `_sync_budget_flags` is the sync mechanism |
| HAI auto-approve fires | `_auto_approve_low_risk_items` at line 240-296 logs but does not emit OpsRunEvent | N/A | Log only |

**Post-D-graduation event additions (per S1902 D89 + P3 designed).**

- `authority_contract_violated` (post-D90 `"enforce"` mode) — emitted
  when authority PROHIBITED gate blocks; carries `action_class`,
  `employee_handle`, `mission_id`, `blocked_at_boundary`.
- `authority_recommend_observed` (post-D90 `"warn"` at RECOMMEND
  level — reserved event name; P3 designs Q3 as NO auto-listener).

### 10.2 Cross-plane event ordering

Under P3 designed precedence policy, a single mission dispatch would
emit events in this order:

```
1. run_started (mission_runner.py:975-978)
2. authority_contract_observed (mission_runner.py:877)  ← Authority observation
3. [autonomy short-circuit possible here — no event; dispatch cancelled at signal_aggregation or workspace_pipeline]
4. step_start (per step)
   4a. [pre-dispatch authority gate under Option A — emits authority_contract_violated if PROHIBITED]
   4b. [KillSwitch reader under D94 — no event emitted; blocks silently with log line]
   4c. LLM call (if step requires LLM)
       4c.i. [LLMEnforcer.enforce_real_ai budget check — no event emitted; blocks with return dict]
5. step_pass / step_fail
6. [post-mission retrospective audit — Boundary 17 read-only, no gate emission]
```

**Cross-plane event silence pattern.** KillSwitch, budget, and
autonomy do NOT emit OpsRunEvents today. Authority is the ONE plane
that emits observability events (per S1264 warn-mode). P3 does NOT
propose emitting cross-plane events at other planes; the audit
trail lives at authority-plane events + management-context read
sites for other planes.

## 11. Existing Documentation

**Primary references for cross-plane composition:**

| Doc | Session | Coverage |
|---|---|---|
| `docs/research/authority_enforcement_design_space.md` (S1272) | 1272 | §7.5 8 composition questions + §7.6 5 composition modes + §14.4 P3 scope |
| `docs/research/governance_authority_evolution.md` (S1269) | 1269 | F1 4 planes don't compose + F2 KillSwitch write-only + F3 35 gates none authority-contract + F4 budget-autonomy desync risk |
| `docs/research/symbol_mapping_option_selection_design.md` (S1274) | 1274 | Option E v0 recommended for Symbol Mapping; §10.3.1 4 graduation triggers |
| `docs/research/domains/authority_enforcement/1900_authority_enforcement_domain_scoping.md` (S1900) | 1900 | Parent §5.3 P3 scope + §22 default queue |
| `docs/research/domains/authority_enforcement/1901_authority_enforcement_cat_a_actor_role_propagation_design.md` (S1901) | 1901 | §7.3 20-boundary propagation-contract table; §6.2 Discord actor path shape |
| `docs/research/domains/authority_enforcement/1902_authority_enforcement_cat_b_authority_enforcement_design_decision.md` (S1902) | 1902 | D86-D93; §17 Enforcement Binding Points map |

**Playbook references.**

- Playbook §11.2 20-section child audit template (standard shape,
  not design-decision-modified).
- Playbook §13 6-Explore parallel probes (applied).
- Playbook §14 verifier-loop MC-1 REQUIRED (applied pre-Explore +
  post-Explore).
- Playbook §14.5 no-implementation rule (respected — no runtime PR
  at P3 close).
- Playbook §15 stage table + §16 arc-pin durable-by-sixth-application
  (Group 1900 arc pin `pa-2bd1613ce2bd4a9c` preserved from S1900 open).

**No parked deliverables from S1900 or S1902.** P3 does not
resurrect any parked scope; it executes the parent §5.3 charter
as-scoped.

## 12. Research Coverage

**What P3 answered.**

- Q1–Q8 designed resolutions (§7.1–§7.8).
- Plane precedence policy (§17.1 canonical resolution order).
- D94 KillSwitch enforcement reader design (§7.4.1).
- Cross-plane audit trail confirmation (§10.1 — authority is the
  one plane emitting OpsRunEvents; other planes silent).

**What remains open post-P3.**

- Per-Discord-command `action_class` audit (T2 R.AUTHORITY.DISCORD-DISPATCH-ENFORCEMENT-INSTRUMENTATION
  prerequisite).
- Per-user authority resolution mechanism (T3 R.AUTHORITY.LOW-RISK-SOURCES-EXPLICIT-AUTHORITY-TAGS
  prerequisite; likely Group 2000+ Event / Integration arc scope).
- KillSwitch enforcement reader execution at 4 boundaries (T2
  R.AUTHORITY.KILLSWITCH-DISPATCH-EXPANSION).
- Freeze × auto-approve gate insertion (T3 R.AUTHORITY.AUTO-APPROVE-FREEZE-GATE).
- Enforce mode toggle field additions (T1 R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS —
  inherited from S1902 §19).
- Cross-arc composition contract handoff to Group 2000+ Event /
  Integration arc for authority × Discord × per-user resolution.

**Coverage classification per playbook §9 canonical questions.**

- Q1 (domain purpose) — §2 covered.
- Q2 (canonical entry points) — §3 covered.
- Q3 (major models) — §4 covered.
- Q4–Q9 (services + APIs + flows + ownership) — §5–§8 covered.
- Q14 + Q17 + Q18 + Q21 + Q22 (integrations) — §9 covered.
- Q19 + Q20 (event flows) — §10 covered.
- Q10–Q13 (existing docs + coverage + maturity + drift) — §11–§14
  covered.
- Q23–Q27 (drift + debt + boundary violations + duplicates + ownership) — §14–§18
  covered.
- Q28 (recommended future research) — §19 covered.

## 13. Architecture Maturity

Cross-plane composition maturity is **Pre-Design → Design-Complete**
at P3 close. The 8 composition questions moved from S1272 §7.5
inventory ("this doc does NOT answer them") to §7.1–§7.8 designed
resolutions. The plane precedence policy moved from S1902 D88
partial precedence to §17.1 full cross-plane canonical resolution
order.

**Maturity levels reference (per playbook §14 discipline).**

- **Pre-Design (S1272).** Composition questions inventoried; no
  answers.
- **Partial Design (S1902 D88).** KillSwitch + authority-side
  precedence entries; incomplete.
- **Design-Complete (S1903).** All 8 questions answered; plane
  precedence policy full; D94 reader designed.
- **Implementation-Complete (future).** T-tier follow-on execution
  (T1 + T2 + T3 slots) landed as runtime PRs.
- **Verified-Complete (future).** Post-implementation Rigby SIGN +
  live-runtime verification of composition behavior at each of the
  20 boundaries per S1902 §17 map.

**Load-bearing observation.** P3 respects the playbook §14.5
no-implementation rule; Design-Complete does NOT mean runtime code
lands. Implementation-Complete is post-arc T-tier work, Chris-gated.

## 14. Known Drift

### 14.1 KNOWN DRIFT — S1902 §14.2 KillSwitch "4 dispatch-consumer" classification imprecise

**Drift.** S1902 §14.2 KNOWN DRIFT entry (line 1605-1608) says: "S1272
GAP-7 KillSwitch 'write-only' REFUTED. Explore 3 verified 6 read
sites total: 4 dispatch-consumer reads + 2 audit." S1902 §12.3 D88
rationale (line 1262) says: "KillSwitch (verified 6 read sites per
Explore 3 — 4 dispatch."

**Direct verification at S1903 close** (see §20 verifier-loop
notes): All 6 sites are management / audit / cleanup contexts;
zero are enforcement dispatch gates.

Verified sites per S1903 post-Explore verifier-loop:

| Site | Context | Enforcement classification |
|---|---|---|
| `core/services/ops_autopilot/governance.py:2192` | Loop inside `get_status()` — serializes active switches for status report | AUDIT (status listing) |
| `core/services/ops_autopilot/governance.py:2370` | `deactivate_kill_switch()` — single-switch fetch for manual deactivate | MANAGEMENT (write path) |
| `core/services/ops_autopilot/governance.py:2508` | Auto-expire cleanup loop inside `evaluate()` — TTL-driven deactivate | MANAGEMENT (cleanup) |
| `core/services/ops_autopilot/governance.py:2545` | `get_audit_log()` — recent switch history for audit trail | AUDIT (history) |
| `core/services/ops_autopilot/intelligence.py:1569` | `get_permission_drift_report()` — count of stale-active switches | AUDIT (drift report) |
| `core/services/ops_autopilot/intelligence.py:1717` | `get_containment_plan()` — expire loop with optional dry-run deactivate | MANAGEMENT (cleanup) |

**Correct classification: 4 AUDIT + 2 MANAGEMENT/cleanup + 0 DISPATCH-CONSUMER.**

**Impact on S1902 findings.**

- S1272 GAP-7 "write-only" claim is TECHNICALLY REFUTED (reads
  exist) but the SPIRIT of F2 stands: no enforcement dispatch
  consults `KillSwitch.is_active` before a targeted action fires.
- S1902 D88's "KillSwitch precedes at every boundary per D88 partial
  precedence K>A>F>B>H" — the PRECEDENCE POLICY is intact, but
  the runtime EXECUTION of that precedence is NOT current-state
  today. It becomes current-state after D94 reader lands at T2 slot.

**Recommendation.** Do BOTH per Rigby SIGN cycle 1 fold:

1. **Ship a targeted S1902 correction PR** — narrow scope: §14.2
   wording + D88 rationale citation note. Prevents P4 posture audit
   from consuming stale drift and incorrectly down-ranking KillSwitch
   remediation as "existing enforcement surface."
2. **Batch the correction into xx99 (S1999) §7 anchor-update
   recommendations** — as the "source-of-truth correction + why it
   matters" record.

Downstream doc hygiene: shipping the S1902 patch alongside the P3
merge (or as an immediate follow-on) is preferred over waiting for
xx99 alone.

### 14.2 KNOWN DRIFT — Explore 2 F4 refutation claim

**Drift.** Explore 2 Section D said: "REFUTES S1269 F4 claim of
'one-way sync' — governance→budget flow is bidirectional."

**Correction.** Explore 2 misread S1269 F4. F4 says: "Budget freeze
is on a parallel rail" — specifically that
`SystemConfiguration.budget_freeze_active` can be flipped by hand
without updating `GovernanceState.mode`, creating a desync risk.
F4 does NOT claim governance→budget sync is unidirectional as
"one-way sync"; F4 describes the ASYMMETRY between operator-driven
budget flag write and governance-driven budget flag write.

Direct verification at S1903 close confirms:

- Governance mode change DOES trigger budget flag write via
  `_sync_budget_flags` (`governance.py:2285-2322`).
- Budget flag write in isolation does NOT trigger governance mode
  update (there is no reverse-sync path).
- The direction is governance → budget (one-way from the sync
  perspective) — Explore 2's own trace confirms this.

**Impact.** F4 stands as originally documented in S1269. Explore
2's F4 refutation claim is disregarded. Governance → budget one-way
sync is documented as the one existing cross-plane touch (§5 +
§17.1 rationale).

### 14.3 KNOWN DRIFT — Explore 6 KillSwitch classification

**Drift.** Explore 6 Section C returned KillSwitch classification "2
WRITE + 2 dispatch-consumer + 2 audit" with `intelligence.py:1717`
listed as dispatch-consumer.

**Correction.** Same as §14.1 — all 6 reads are
management/audit/cleanup. `intelligence.py:1717` is a cleanup loop
inside `get_containment_plan()` that optionally deactivates expired
switches; it is NOT a dispatch enforcement gate. Explore 6
classification corrected per §14.1 table.

**Impact.** No downstream design impact — §7.4 D94 designed reader
respects §14.1 verified classification.

### 14.4 KNOWN DRIFT — Inherited from S1902 §14.4 (not re-verified at P3)

The following drifts landed at S1902 §14.4 and remain valid for
S1903:

- Parent §5.2 F8-vs-F9 constraint drift + 4-vs-5 modes count —
  correct to F9 + 5 modes per S1272 §4.3 authoritative table.
- S1272 §3.1 Boundary 16 `views_human_interface.py:84-100` line
  drift — actual decide endpoint at `:154`.
- Option E label collision (S1272 §9.5 Multi-layer vs S1274 Symbol
  Mapping Option E v0 Evidence-only) — recommend rename S1272 §9.5
  → "Option M Multi-layer" or equivalent.
- CLAUDE.md 3-vs-runtime-4 employee_handles drift — reconcile
  CLAUDE.md line 195 claim vs Explore 5 warn-mode 4-handle
  observation.
- HAI auto-approve gate count reconciliation — S1269 §2.4 cited 7;
  Explore 6 verified 8 (7 core + 2 existence) at S1902 close.

**All inherited drifts batched into S1999 xx99 §7 anchor-update
recommendations.**

## 15. Known Technical Debt

Cross-plane composition debt lives in the T-tier queue extension
from P3 to post-arc slots. Debt is Chris-gated per playbook §16
arc-close discipline.

**P3-added T-tier items (extend S1902 §19 queue):**

- **T2 R.AUTHORITY.DISCORD-DISPATCH-ENFORCEMENT-INSTRUMENTATION.** Add
  authority observation + optional gate on 6+ authority-relevant
  Discord commands. Prerequisites: Symbol Mapping runtime registry
  (S1270 graduation status), per-command action_class audit, Discord
  actor path shape (S1901 §6.2 finalization). Estimated effort: 1-2
  sessions.
- **T3 R.AUTHORITY.AUTO-APPROVE-FREEZE-GATE.** Add
  `GovernanceState.mode` short-circuit to `_auto_approve_low_risk_items`
  at `human_attention_lifecycle.py:240-245`. Estimated effort: <0.5
  sessions.
- **T3 R.AUTHORITY.LOW-RISK-SOURCES-EXPLICIT-AUTHORITY-TAGS.** Retrofit
  authority-level tags to the 5 LOW_RISK_SOURCES entries. Prerequisites:
  per-user authority resolution (likely Group 2000+ Event /
  Integration arc). Estimated effort: 1 session (contingent on
  prerequisite).

**Inherited T-tier items (unchanged from S1902 §19 + prior arcs):**

- **T1 R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS** — Add field to
  MissionRunnerConfig + AIEmployee dataclasses; wire max-strictness
  composition per §7.7. Estimated effort: 0.5-1 sessions.
- **T1 R.AUTHORITY.VIOLATION-EVENT-SCHEMA** — Define
  `authority_contract_violated` label + detail dict shape.
- **T1 R.AUTHORITY.RETROSPECTIVE-SCAN-TASK** — Celery beat task
  `authority_violation_retrospective_scan`.
- **T1 R.AUTHORITY.OPTION-E-MIGRATION-TRIGGER** — Beat observing
  S1274 §10.3.1 graduation triggers.
- **T2 R.AUTHORITY.KILLSWITCH-DISPATCH-EXPANSION** — 4-boundary
  reader landing per §7.4.1 D94.
- **T2 R.AUTHORITY.STEP-ACTION-DECLARATION** — Extend Step
  dataclass with `action_classes_invoked` field.
- **T3 R.AUTHORITY.PER-LEVEL-BOUNDARY-BINDING** — Option E multi-layer
  reconsideration post-graduation.
- **T3 R.AUTHORITY.CLAUDE-MD-EMPLOYEE-COUNT-ANCHOR-UPDATE** — Reconcile
  CLAUDE.md 3-employee claim vs runtime 4-employee-handle observation.

**Cross-arc debt.**

- From Group 1800 (S1899): T0/Gate 6-item bundle including
  R.HAI.LEARNING-PLANE-CONTRACT-ADR joint Group 1300+1800 —
  Group 1900 P3 confirms no direct authority-plane contribution
  to learning loop at P3 scope; handoff preserved.
- From Group 1700 (S1799): R.OBSERVABILITY.RETENTION-UNIFIED-ADR +
  R.OBSERVABILITY.D74-SPINE-POSTURE — recommend unified cross-arc
  retention ADR bundle.

## 16. Boundary Violations

Cross-plane composition boundary violations occur when a plane
reads or writes across its owned surface without explicit
composition contract. P3 does NOT propose new violations; it
documents current-state violation posture + how the plane precedence
policy in §17 resolves them.

**Current-state violation surface (inherited from S1269 F1 + S1272 §7):**

- **V1. `_sync_budget_flags` autonomy → budget one-way sync**
  (`governance.py:2285-2322`) — is a controlled cross-plane write.
  Not a violation; it is the ONE codified composition touch.
- **V2. `_auto_approve_low_risk_items` does not read
  `GovernanceState.mode`** (`human_attention_lifecycle.py:240-296`) — is
  a violation of the semantic "freeze pauses autonomous actions"
  (Q5 designed policy). Registered as T3 R.AUTHORITY.AUTO-APPROVE-FREEZE-GATE.
- **V3. KillSwitch has zero enforcement dispatch consumers**
  (§14.1 verified) — is a violation of the D88 partial precedence
  "KillSwitch precedes at every boundary" policy. Registered as T2
  R.AUTHORITY.KILLSWITCH-DISPATCH-EXPANSION.
- **V4. Authority observation is per-mission but not per-step**
  (`mission_runner.py:835-900` emits ONE event per mission at
  start) — is a design choice (per S1264), not a violation. Documented
  in S1902 §12.5.
- **V5. Discord command dispatch has zero authority observation**
  (Explore 5 §H) — is a violation of the Q8 "Discord commands
  invoke authority-relevant actions" semantic. Registered as T2
  R.AUTHORITY.DISCORD-DISPATCH-ENFORCEMENT-INSTRUMENTATION.

**Post-plane-precedence-policy resolution.** After all T-tier items
land, V2-V5 resolve. V1 remains as the intentional codified touch.

## 17. Duplicate or Overlapping Systems — Plane Precedence Policy (P3 First-Class Deliverable)

### 17.1 Canonical resolution order

The plane precedence policy generalizes P2 D88's partial precedence
into a full cross-plane resolution order:

```
KillSwitch > Autonomy > Authority (PROHIBITED) > Freeze > Authority (RECOMMEND) > Budget > HAI auto-approve
```

**Interpretation.**

- Reading left → right = precedence high → low.
- Each plane can VETO the action if it evaluates to a block.
- If no plane vetoes, the action proceeds.
- Multiple planes can be observing simultaneously; observation
  events fire independently of precedence.

**Plane definitions in this policy.**

| Plane | Owned surface | Block condition |
|---|---|---|
| **KillSwitch** | `KillSwitch(is_active=True, target=…)` per §7.4.1 D94 target-to-boundary mapping | Any active kill switch matching the boundary's target |
| **Autonomy** | `GovernanceState.mode` at scope='global' | mode ∈ {`freeze`, `safe_mode`} for full block; `throttle` for degrade-only |
| **Authority (PROHIBITED)** | `JobContract.authority[action_class] == 'prohibited'` | Level equals PROHIBITED for the invoked action_class |
| **Freeze** | Same as Autonomy but scoped to LLM-call-time via `SystemConfiguration.budget_freeze_active` (synced from `GovernanceState.mode`) | budget_freeze_active=True at LLM call site |
| **Authority (RECOMMEND)** | `JobContract.authority[action_class] == 'recommend'` | Never blocks under any current mode; emits observation event |
| **Budget** | `LLMEnforcer.enforce_real_ai` internal checks | LUNGS breach, freeze without whitelist, downgrade, ROI throttle |
| **HAI auto-approve** | `_auto_approve_low_risk_items` at `human_attention_lifecycle.py:240-296` | 8-gate composition (Explore 3 §B); async beat |

**Why Freeze appears twice (as sub-item of Autonomy and separately
in the ordering).** Freeze is a specific autonomy `mode` value that
also propagates to budget flags via `_sync_budget_flags`. It fires
at TWO boundaries: mission-dispatch envelope (part of Autonomy plane)
+ LLM call site (part of Budget plane). Ordering distinguishes the
two firing points.

**Freeze is one plane with two read-sites (Rigby SIGN cycle 1 fold).**

Freeze semantics are precisely:

1. **Freeze is a single policy plane** — one governance state
   (`GovernanceState.mode='freeze'` OR `SystemConfiguration.budget_freeze_active=True`,
   kept in sync by `_sync_budget_flags`).
2. **It has two evaluation sites** — the mission-dispatch envelope
   (dispatch-time short-circuit at signal_aggregation, workspace_pipeline,
   spider_tasks) AND the LLM call site (`LLMEnforcer.enforce_real_ai`
   at `llm_enforcer.py:201-221`).
3. **The same relative order MUST hold at both sites** — Freeze
   evaluates AFTER KillSwitch and Autonomy `safe_mode`, BEFORE
   Authority RECOMMEND and Budget throttle/ROI. Implementers who
   see Freeze at one evaluation site must not re-order it at the
   other.
4. **Autonomy does NOT subsume Freeze** — Autonomy's `safe_mode`
   may TRIGGER Freeze (via `_sync_budget_flags`), but does not
   REDEFINE Freeze's precedence position. Treating "Autonomy
   includes Freeze" as a containment relation would allow reordering
   at implementation time; that is explicitly disallowed here.

### 17.2 Sub-precedence rules

**§17.2.1 KillSwitch × Freeze.** KillSwitch wins.

- Rationale: KillSwitch is the operator-kill vector; Freeze is a
  governance state that can be operator-driven OR TTL-driven. Kill
  is more specific and higher precedence.
- Runtime today: neither has enforcement dispatch, so precedence is
  aspirational at P3 close. Freeze DOES have three enforcement
  dispatch sites (`signal_aggregation`, `workspace_pipeline_runner`,
  `spider_tasks`); KillSwitch has zero. Post-D94 the balance
  inverts.

**§17.2.2 Autonomy `safe_mode` × Authority `EXECUTE`.** Autonomy wins.

- Rationale: `safe_mode` explicitly means "all autonomous actions
  paused, human approval required for everything." Authority
  EXECUTE grants permission for the employee to execute an action;
  under safe_mode the employee shouldn't be autonomously acting
  regardless of authority grant.
- Runtime today: three verified dispatch sites short-circuit on
  `safe_mode` OR `freeze`; authority observation would fire but
  never block (warn-mode); result matches Autonomy-wins semantic.

**§17.2.3 Authority PROHIBITED × Freeze × Budget.** Authority
PROHIBITED wins pre-LLM; Budget wins at LLM-call-time.

- Rationale per Q2: Budget is an LLM-call-time throttle; Authority
  is a mission-time contract. Asymmetric layering per §7.2.
- Runtime today: warn-mode observes authority but does not gate;
  budget blocks at LLM call. Post-D90 `"enforce"` mode, pre-dispatch
  gate blocks PROHIBITED before LLM call is attempted.

**§17.2.4 RECOMMEND × HAI auto-approve × Budget.** All three fire
sequentially without veto composition.

- Rationale per Q3: RECOMMEND does not auto-create HAI (Q3 designed
  policy). Auto-approve fires on async beat schedule, independent
  of mission. Budget affects LLM sub-call if auto-approve requires
  one (per Q6 verified: ml_confidence check is pure comparison, no
  LLM).
- Result: RECOMMEND emits observation; auto-approve fires per
  schedule; budget gates any LLM sub-call inside auto-approve. Three
  independent surfaces, no cross-veto.

### 17.3 Composition mode taxonomy alignment (S1272 §7.6)

Per S1272 §7.6 5 composition modes: Additive, Precedence, Union,
Layered, Independent.

**P3 designed composition adopts PRECEDENCE mode with LAYERED
sub-cases:**

- **Precedence:** §17.1 canonical resolution order defines the
  precedence stack.
- **Layered (sub-case):** Q2 asymmetric layering (budget vs
  authority sequenced differently at LLM sub-path vs pre-dispatch)
  is a LAYERED composition where each layer fires in defined
  order.
- **Independent (residual):** RECOMMEND × HAI × Budget sub-precedence
  in §17.2.4 is Independent (no cross-veto).

**Additive** and **Union** modes are NOT adopted. Additive would
mean any plane veto blocks; that overcouples planes. Union would
combine plane outputs into composite; that requires a resolver
function P3 explicitly avoids per §3 (no single-file cross-plane
resolver).

### 17.4 P3 vs S1902 D88 comparison

| Comparison axis | S1902 D88 (Partial) | S1903 §17.1 (Full) |
|---|---|---|
| Coverage | 5-entry partial (K > A > F > B > H) | Full 7-entry ordering with sub-precedence rules |
| Freeze positioning | Implicit; listed as one item | Distinguished by boundary (mission-dispatch vs LLM-call-time) |
| Sub-precedence rules | None | 4 rules (§17.2.1–§17.2.4) |
| Composition mode declaration | Precedence (implicit) | Precedence primary + Layered sub-case + Independent residual (explicit per §17.3) |
| KillSwitch enforcement | Aspirational (T2 slot referenced) | Same; D94 reader shape designed in §7.4.1 |
| Scope | Authority-side input for P3 | Full cross-plane policy; downstream P4 posture audit reference |

## 18. Ownership Gaps

Cross-plane composition ownership is well-defined per §4 Major
Models + §5 Major Services. P3 does NOT propose new ownership; it
documents the composition contract that spans owned surfaces.

**Gap surface (inherited; documented for xx99).**

- **G1. No single owner for plane precedence policy execution.** Each
  boundary has its own composition read; there is no
  `PlanePrecedenceResolver` service. This is intentional (§3
  distributed-composition-at-boundary design), not a gap requiring
  ownership assignment.
- **G2. No dedicated composition-audit surface.** Audit trail lives
  in OpsRunEvent detail (authority plane) + governance-tool overview
  (autonomy plane) + no dedicated cross-plane composition log. This
  is a POST-implementation gap; P3 does not propose closing it at
  P3 scope (would require §5 new model per V4 taxonomy).
- **G3. Discord command dispatch has no authority owner.** Per Q8
  formal deferral; owner is TBD at T2 R.AUTHORITY.DISCORD-DISPATCH-ENFORCEMENT-INSTRUMENTATION
  execution time.

## 19. Recommended Future Research

P3-recommended future research candidates, ranked by architectural
uncertainty × risk × unblocked flows per playbook §11.2 §19 spec:

**High priority (pre-graduation blockers):**

1. **Symbol Mapping runtime registry status verification.** S1274
   Option E v0 recommended; §10.3.1 4 graduation triggers. P3
   Q8 deferral + Q6 deferral both cite Symbol Mapping graduation
   status as UNKNOWN. Recommend a single-session verification of
   current graduation status + trigger monitoring beat health.
   Registered as future research candidate F.SYMBOL-MAPPING-STATUS-VERIFICATION.
2. **Per-user authority resolution mechanism.** Q6 designed
   deferral depends on per-user authority resolution which is
   currently a JobContract concept (per-employee). Recommend
   design research for per-user authority in Group 2000+ Event /
   Integration arc scope. Registered as F.PER-USER-AUTHORITY-MECHANISM.

**Medium priority (post-graduation enablers):**

3. **Cross-plane composition audit surface.** G2 above; would
   require a `CrossPlaneComposition` model + OpsRunEvent label
   family. Chris-gated design research. Registered as
   F.CROSS-PLANE-AUDIT-SURFACE.
4. **Discord command action_class audit.** Q8 T2 prerequisite;
   requires per-command classification. Registered as
   F.DISCORD-ACTION-CLASS-AUDIT (blocking T2 R.AUTHORITY.DISCORD-DISPATCH-ENFORCEMENT-INSTRUMENTATION).

**Low priority (post-arc future arcs):**

5. **Fleet dispatch authority instrumentation.** D94 §7.4.1 Boundary
   18 insertion; requires understanding Fleet dispatch flow. Registered
   as F.FLEET-DISPATCH-AUTHORITY.
6. **HAI plane learning bridge to authority.** F5 in S1269 notes
   HAI is the only learning loop; extending to authority-plane
   observations is Group 1300+1800 cross-arc scope. Registered as
   F.HAI-LEARNING-TO-AUTHORITY.

## 20. Appendix — Provenance

### 20.1 Files inspected

- `core/services/ops_autopilot/governance.py` (2000+ lines; sections
  read: 2159-2237, 2258-2322, 2370, 2495-2545)
- `core/services/ops_autopilot/intelligence.py` (~2000 lines; sections
  read: 1560-1590, 1710-1740)
- `core/llm_enforcer.py` (~900 lines; sections read: 139-278)
- `core/employees/mission_runner.py` (~1200 lines; sections read:
  528-589 config dataclass, 601-638 __init__, 835-900
  _emit_authority_contract_event, 975-1075 _run_all_steps orchestration)
- `core/employees/jobs.py` (~1400 lines; sections read: 41-51 enum,
  73-91 AIEmployee, 94-161 JobContract, 167-1125 employee entries,
  1327-1347 registries)
- `core/services/human_attention_lifecycle.py` (sections read: 63-90
  constants, 91-133 process_lifecycle, 223-296 _auto_approve_low_risk_items)
- `core/services/tool_dispatcher.py` (sections read: 686-839 dispatch
  path)
- `core/services/discord_bot.py` (Cog inventory; representative
  commands per Explore 5 sample)
- `core/models_governance.py` (GovernanceState + KillSwitch schemas)
- `core/models_human_interface.py` (HumanAttentionItem + HumanSystemState
  schemas)
- `core/models_ops_runs.py` (OpsRun + OpsRunEvent schemas)

### 20.2 Docs inspected

- `docs/research/authority_enforcement_design_space.md` (S1272 —
  §7.5 8 composition Qs + §7.6 5 modes + §14.4 P3 scope + §15
  appendix)
- `docs/research/governance_authority_evolution.md` (S1269 — F1
  4-planes + F2 KillSwitch write-only + F3 35 gates + F4 desync + F5
  learning loop)
- `docs/research/symbol_mapping_option_selection_design.md` (S1274 —
  Option E v0 + §10.3.1 4 graduation triggers)
- `docs/research/domains/authority_enforcement/1900_authority_enforcement_domain_scoping.md`
  (S1900 — parent §5.3 P3 scope + §22 default queue)
- `docs/research/domains/authority_enforcement/1901_authority_enforcement_cat_a_actor_role_propagation_design.md`
  (S1901 — §7.3 20-boundary table + §6.2 Discord actor path shape)
- `docs/research/domains/authority_enforcement/1902_authority_enforcement_cat_b_authority_enforcement_design_decision.md`
  (S1902 — D86-D93 + §17 Enforcement Binding Points map + §19
  T-tier queue)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 20-section
  template + §13 6-Explore + §14 verifier-loop + §14.5
  no-implementation rule + §16 arc-pin durable)

### 20.3 Grep patterns used

- `GovernanceState.mode` + `GovernanceState.effective_mode` — autonomy
  read-site inventory
- `KillSwitch.objects.filter(is_active=True` — KillSwitch read-site
  inventory (6 hits verified in §14.1)
- `budget_freeze_active` + `enforce_real_ai` — budget plane read-site
  inventory
- `HumanAttentionItem.objects.create` + `create_human_attention_item`
  — HAI creator inventory (23 sites per Explore 3)
- `AuthorityLevel` — authority enum reference (1 runtime site at
  mission_runner.py:864-867)
- `_sync_budget_flags` — cross-plane sync touchpoint
- `MissionRunnerConfig` — 4 factory sites (Explore 4 §D)
- `@app_commands.command` + `@commands.command` — Discord command
  inventory (48 slash + 0 prefix per Explore 5 §A)

### 20.4 Unresolved unknowns

- **Symbol Mapping runtime registry status.** S1274 Option E v0 was
  recommended; graduation trigger monitoring status not verified at
  P3 scope. Registered as F.SYMBOL-MAPPING-STATUS-VERIFICATION (§19).
- **Discord command action_class inventory.** Q8 deferral; not
  audited at P3. T2 prerequisite (§15).
- **Per-user authority resolution mechanism.** Q6 deferral;
  requires Group 2000+ arc scope. F.PER-USER-AUTHORITY-MECHANISM (§19).

### 20.5 Conflicts between sources

- **S1902 §14.2 "4 dispatch-consumer" vs direct verification 0
  dispatch-consumer.** Resolved in §14.1 KNOWN DRIFT — direct
  verification supersedes; correction batched to xx99 §7
  anchor-update.
- **Explore 2 "REFUTES S1269 F4" vs direct read of S1269 F4.**
  Resolved in §14.2 KNOWN DRIFT — Explore 2 misread F4; F4 stands.
- **Explore 6 KillSwitch classification vs Explore 1 classification.**
  Resolved in §14.3 KNOWN DRIFT — Explore 1 classification (all
  management/audit/cleanup) matches direct verification.

### 20.6 Verifier-loop corrections

**Pre-Explore verifier-loop applied (playbook §14 MC-1 REQUIRED).**

Verified before firing 6 Explore probes:

- S1272 §7.5 8 composition questions authoritative list (§7.5 lines
  1089-1123) — MATCHES claim; used verbatim in §7.
- S1272 §14.4 Cross-Plane Composition Design P3 scope (§14.4 lines
  2067-2085) — MATCHES claim; used verbatim in §2.
- S1902 D86-D93 verdicts + §17 map + §19 T-tier queue (§12.3–§12.9
  + §17.1 + §19) — MATCHES claim.
- S1901 §7.3 20-boundary table (referenced via §6.2 line 553
  Discord out-of-table marker) — MATCHES claim.
- S1269 F1 4 planes don't compose + F4 desync risk (F1 lines 760-778
  + F4 lines 811-831) — MATCHES claim.

**Post-Explore verifier-loop applied.**

- §14.1 KillSwitch classification correction — 6 sites verified
  against source; classification inverted from Explore 6's
  claim.
- §14.2 Explore 2 F4 refutation correction — F4 re-read against
  source; Explore 2 disregarded.
- §14.3 Explore 6 classification correction — same as §14.1.

**Verifier-loop is MC-1 CODIFICATION-CONFIRMED at P3 close** per
playbook §14 discipline. First pre-Explore + post-Explore both
required; both applied.

### 20.7 Rigby SIGN fold notes

**Rigby SIGN cycle 1 — SIGN-with-edits at High confidence 2026-07-04
on Group 1900 arc pin `pa-2bd1613ce2bd4a9c`.** Single-batch 4-question
SIGN per playbook §15 stage table. **D48 35th arm turn 1 CLEAN →
30-consecutive-fully-clean-arms sub-pattern EXTENDED** per
single-batch-4-question criterion (MC-2 CODIFICATION-CONFIRMED
milestone extended 29 → 30 consecutive).

**4 folds landed pre-commit:**

- **Q1 fold (§17.1) — Freeze double-surface clarification.** Added
  4-point "Freeze is one plane with two read-sites" sub-section:
  (i) Freeze is single policy plane; (ii) two evaluation sites
  (dispatch envelope + LLM call); (iii) same relative order at both
  sites; (iv) Autonomy does NOT subsume Freeze (safe_mode may
  TRIGGER Freeze but does NOT redefine precedence). Rationale:
  prevents implementation-time reordering debates.
- **Q2 fold (§7.4.1) — Boundary 16 optional insertion +
  rate-limited logging.** Added Boundary 16 (HAI decide endpoint at
  `views_human_interface.py:154`) as OPTIONAL 5th insertion — only
  to prevent approving HAI decisions that would schedule execution
  against active kill switches. Changed logging from `logger.error`
  to rate-limited `logger.warning` with structured
  `killswitch_missed_reader:<boundary>` prefix. Rationale: avoids
  alert fatigue while preserving F8 fail-open semantics.
- **Q3 fold (§14.1) — Downstream doc hygiene: do BOTH targeted PR
  + xx99 batch.** Recommendation upgraded from xx99-only to
  targeted S1902 correction PR (narrow: §14.2 wording + D88 rationale
  citation note) + xx99 §7 anchor-update batch. Rationale: prevents
  P4 posture audit from consuming stale drift and incorrectly
  down-ranking KillSwitch remediation.
- **Q4 fold (§7.7) — Canonical read discipline + Alternative 3
  boundary-rehydration clarification.** Added canonical-read
  discipline: after composition, only
  `MissionRunner.resolved_enforce_authority_mode` (equivalent to
  `self.effective_enforce_mode`) is consulted; direct reads of
  either dataclass field after composition are forbidden. Tightened
  Alternative 3 rejection rationale to name the specific inconsistency
  vectors: boundary rehydration (mid-mission MissionRunner reconstruction)
  + per-step config-override (Alternative-3 shape). T1 execution PR
  must audit for direct-read anti-patterns.

**Verdict: SIGN-with-edits at High confidence** with all 4 folds
landed pre-commit. Doc line count post-fold: ≤1750 (target held).
No SIGN cycle 2 required unless Chris identifies additional folds
at ratification.

### 20.8 Session close artifact ledger (at S1903 commit)

To be finalized post-Rigby-SIGN. Anticipated artifacts:

- `docs/research/domains/authority_enforcement/1903_authority_enforcement_cat_c_cross_plane_composition_design.md`
  (this doc)
- `docs/research/ARCHITECTURE_INDEX.md` (v61 → v62 with §1.65
  S1903 registration)
- `docs/research/OPEN_ARCS.md` (Group 1900 row current-child
  S1902 → S1903 + last_updated bump)
- `docs/handoffs/SESSION_1903_AUTHORITY_ENFORCEMENT_CAT_C.md`
  (S1903 handoff)
- `00-START-NEXT-SESSION.md` (overwritten to point at S1904 P4 Cat F)

---

_End of P3 Cross-Plane Composition Design._
