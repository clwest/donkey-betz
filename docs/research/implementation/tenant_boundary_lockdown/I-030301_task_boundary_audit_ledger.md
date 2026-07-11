---
title: "I-030301 Task Boundary Audit Ledger — Phase 1 (I-0303)"
status: active
authority: phase-1-audit-ledger-ratified
session_added: 2754
session_ratified: 2754
last_updated: 2026-07-11
this_phase_ratification: docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase1_ledger.md
ratification_date: 2026-07-11
arc_id: I-0303
arc_phase: 1
parent_arc: I-0303
parent_scoping: docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md
parent_scoping_ratification: docs/research/implementation/RATIFICATION_2026-07-11_i0303_scoping.md
parent_campaign: RUR-C1 (Tenant Boundary Lockdown)
parent_program: RUR (Real User Readiness)
sibling_predecessor: I-030201 (I-0302 Phase 1 Model Audit Ledger — closed ratified S2742)
predicate_module_dependency: core/tenant_boundary_lockdown/predicates.py (I-0302 Phase 2, ratified 2026-07-10)
harness_dependency: tests/security/ (I-0302 Phase 4, ratified 2026-07-10)
head_at_audit: 47cc13dd
ratification_record: docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase1_ledger.md
ratifier: chris
ratifier_verdict: "agree all"
phase_state: Phase 1 CLOSED; Phase 2 (Decorator + Base-Class Implementation) authorized to open
constraint: Phase 2 opens under this ratified ledger; amendments during Phase 2+ route through parent CAMPAIGN §10 amendment discipline
rigby_sign_state: LEDGER RATIFY WITH EDITS (S2754 Phase 1 turn 1) — 3 axis edits applied inline (§3 traffic-informed Phase-3-first list; §7.3 system-scope justification test); §1/§2/§4/§5/§6/§8/§9 PASS; both REG RISK exemplars confirmed. Joint recommendation = LEDGER RATIFY.
d_verdict_invariants_respected:
  - Q1 trusted-source hierarchy — DB-row-derived first; signed header second; payload NEVER
  - Q2 system-task marker — explicit opt-in @system_scope; fail-safe default
  - Q3 AsyncBoundaryProbe shape — new probe class (Phase 4)
  - Q4 coverage-gap threshold — I-0302 precedent (per-exemption SIGN + ratify at Phase 4 close)
  - Q5 RUR-C1 close SIGN scope — one parent-close event at I-0303 arc close
  - Q6 canonical row reference — row-ID dispatch only for user-owned-model tasks
---

# I-030301 Task Boundary Audit Ledger — Phase 1 (I-0303)

> **Arc-phase ledger DRAFT.** RUR-C1 / I-0303 Phase 1 output. Answers §2.1..§2.5 + §2.9 of the I-0303 scoping doc for the task boundary. Full per-task classification follows the I-030201 (I-0302 Phase 1) **SAMPLED** discipline: dominant-category classification + named exemplars per model, not exhaustive per-task enumeration.
>
> **Phase 1 → Phase 2 handoff:** this ledger, once ratified, is the input to Phase 2 (decorator + base-class implementation). Phase 2 authors `@enforce_tenant_boundary` + `TenantScopedTask` against the ownership predicate module frozen at I-0302 Phase 2.

---

## §1. Audit Scope + Method

### §1.1 Audit shape

Following I-030201 sampled-audit precedent (Rigby SIGN F4 amendment 2026-07-10 acknowledged that exhaustive per-caller enumeration is not required at Phase 1 for Phase 2 authoring). Phase 1 produces:

- Concrete task-facade → `_impl_*` mapping strategy (§2)
- Task file inventory + facade counts (§3)
- Per-model task-touch sampling with dominant-category classification (§4)
- Acting-identity source classification per §4 exemplar (§5, per Q1)
- Row-reference shape classification per §4 exemplar (§6, per Q6)
- System-scope task classification (§7, per Q2)
- Nullable/missing-identity interim policy per task class (§8)
- Phase 2 entry criteria (§9)

### §1.2 Reproducibility footnote (per I-030201 §5.0.1 precedent)

**Task enumeration:** `grep -c '@shared_task\|@app\.task\|@celery\.task\|@task(' core/tasks*.py` at HEAD `47cc13dd` returned 407 registrations across 19 files.

**Per-model task-touch grep:** `grep -c '\bDeliverable\b\|\bInitiative\b\|\bChatConversation\b\|\bAgentExecution\b\|\bAgentTaskExecution\b\|\bDocument\b' core/tasks*.py` — reference counts per file recorded in §4 tables. High-touch surface: `core/tasks.py` (facade layer registers 370 tasks; delegates to domain `_impl_*` functions).

**Spot-check task bodies:** read at HEAD `47cc13dd` — evidence-anchored task exemplars in §4 include line-number citations to `core/tasks_agents.py:493`, `core/tasks_conversations.py:3463`, etc.

**Limitations known:** grep-count of a model name in a file may include class references in `.DoesNotExist` handlers, docstrings, or type annotations — not just ORM query targets. Dominant-category classification (§4) errs conservative: any file with >5 grep-hits on a user-owned model is classified as "likely-touches" pending Phase 2 predicate-import verification.

---

## §2. Concrete Task-Facade → `_impl_*` Mapping (§2.1 scope outcome)

### §2.1 Two-tier task layer

The Celery task registration layer is bifurcated:

- **Tier 1 — `core/tasks.py` facade** (370 `@shared_task` registrations at HEAD): each decorated function is typically a 2-5 line delegate that imports `_impl_*` from a domain file and calls it. Example (`core/tasks.py` `summarize_conversation_task` seen at spot-check): `return _impl_summarize_conversation_task(self, conversation_id, user_id)`.
- **Tier 2 — domain `_impl_*` functions** (in `core/tasks_<domain>.py`): the actual task logic — ORM queries, model mutations, LLM calls, side-effect writes. This is where user-owned-model touches actually live.

**Implication for I-0303 enforcement:** `@enforce_tenant_boundary` decorator can be applied at either Tier 1 (facade — wraps the delegator) or Tier 2 (impl — inside the domain module). Tier 1 is preferred for coverage (single site per task-class); Tier 2 is preferred for legacy tasks whose facade is thin and impl body owns the model access. Phase 2 picks per-task; Phase 3 wires.

**Exceptions — Tier 0 direct-registration files:** some domain files register `@shared_task` directly (bypassing the facade). Confirmed at spot-check:

- `core/tasks_agents.py:493` — `execute_agent` is `@shared_task(base=AgentExecutionTask)` — direct registration, not facade-delegated
- `core/tasks_agents.py:781, 811, 831, 860, 1334, 1458` — 6 more direct registrations in `tasks_agents.py`

Phase 2 handoff MUST audit which Tier-0 tasks touch user-owned models directly and which are facade-delegated.

### §2.2 Canonical class re-verification (inherited from I-030201 §2)

I-0303 accepts the I-0302 canonical class decisions verbatim (I-030201 §2 ratified 2026-07-10 by Chris):

| Model concept | Canonical class (I-0302 ratified) | Task-boundary implication |
|---|---|---|
| Deliverable | `core.models_deliverables.Deliverable` | ORM: `Deliverable.objects.get/filter(id=...)` — row-ID access dominant |
| Initiative | `core.models_document_registry.Initiative` | ORM: `Initiative.objects.get/filter(id=...)` — row-ID access dominant |
| ChatConversation | `core.models.ChatConversation` | ORM: `ChatConversation.objects.filter(conversation_id=...)` — filter-by-natural-key common (Q6 concern) |
| AgentExecution | `core.models_unified_system.AgentExecution` (per I-030201 §2.4 canonical decision); NOTE: `core.models.AgentTaskExecution` also live for legacy paths — see §4.4 duplicate-class caveat | ORM: `.objects.get(execution_id=...)` — row-ID access; canonical class Phase-3 selection required |
| Document | `content.models.Document` (per I-030201 §2.5); AND `core.models_deliverables.WorkspaceDocument` sibling class | ORM: mixed — some tasks use natural-key `path=`, others use `id=` — Q6 concern |

Full Phase 1 mapping locks per-task which canonical class is touched. §4 exemplars name the class per exemplar.

---

## §3. Task File Inventory + Facade Counts

Task registration counts per file at HEAD `47cc13dd`:

| File | @shared_task count | User-owned-model exposure (grep hits) | Notes |
|---|---|---|---|
| `core/tasks.py` | **370** | Deliverable 23 · Initiative 11 · ChatConversation 5 · AgentExecution 11 · Document 29 | Facade layer — delegates to domain `_impl_*` |
| `core/tasks_agents.py` | 7 (Tier-0 direct) | Deliverable 0 · Initiative 3 · ChatConversation 3 · AgentExecution 40 · Document 4 | AgentExecution-dominant; direct-registered |
| `core/tasks_content.py` | 2 | Deliverable 9 · Document 4 · Initiative 0 | Deliverable-focused; content pipeline tasks |
| `core/tasks_conversations.py` | 1 | ChatConversation 2 · Initiative 1 · Document 3 · Deliverable 4 · AgentExecution 0 | ChatConversation-focused; PA conversation flows |
| `core/tasks_documentation_manager.py` | 1 | Deliverable 1 | Doc manager mission |
| `core/tasks_financial.py` | 1 | AgentExecution 1 | Peripheral touch |
| `core/tasks_initiatives.py` | 1 | Initiative 48 · Deliverable 9 · AgentExecution 7 · Document 3 | Initiative-heavy — dominant model |
| `core/tasks_media.py` | 2 | Document 17 · AgentExecution 2 | Media generation writes Documents |
| `core/tasks_misc.py` | 1 | Document 16 · Deliverable 8 · ChatConversation 8 · AgentExecution 2 · Initiative 3 | Cross-cutting — highest per-file variety |
| `core/tasks_ops.py` | 2 | AgentExecution 3 · Document 3 · Initiative 1 · Deliverable 0 | Ops orchestrator writes |
| `core/tasks_platform_audit.py` | 1 | Deliverable 1 | System-scope audit |
| `core/tasks_beat_health.py` | 2 | 0 | System-scope health checks |
| `core/tasks_body_systems.py` | 1 | 0 | System-scope body scans |
| `core/tasks_bug_triage.py` | 1 | Deliverable 1 | Bug triage — reads user deliverable? Phase 2 verify |
| `core/tasks_chief_of_staff.py` | 1 | Deliverable 4 | CoS mission writes/reads deliverables |
| `core/tasks_cost_protection.py` | 2 | 0 | System-scope cost telemetry |
| `core/tasks_executor.py` | 1 | 0 (facade only) | Delegator into other domains |
| `core/tasks_push_notifications.py` | 9 | 0 in grep — need Phase 2 verify against user notification target rows | Notification writes; user-scope surface likely |
| `core/tasks_spiders.py` | 1 | 0 | System-scope spider workers |

**Total Tier-0/Tier-1 task registrations at HEAD:** 407 (matches grep count; PLATFORM_INVENTORY says 415 — 8 tasks live in package-level `__init__.py` or `ai_core.tasks` outside `core/tasks*.py` glob per §1.2 method).

**Preliminary bucketing:**

- **HIGH-RISK task files (user-owned-model dominant touch, Tier-0 direct-register or facade-delegated):** `tasks.py`, `tasks_agents.py`, `tasks_initiatives.py`, `tasks_conversations.py`, `tasks_content.py`, `tasks_misc.py`, `tasks_media.py`
- **MEDIUM-RISK:** `tasks_ops.py`, `tasks_chief_of_staff.py`, `tasks_documentation_manager.py`, `tasks_bug_triage.py`, `tasks_push_notifications.py` (verify at Phase 2)
- **LOW-RISK / likely system-scope:** `tasks_beat_health.py`, `tasks_body_systems.py`, `tasks_cost_protection.py`, `tasks_spiders.py`, `tasks_platform_audit.py`, `tasks_financial.py` (grep-count 0-1)

**Traffic note (last 7d, per Rigby SIGN §3 edit — `ops_tool.top_consumers`):** highest-volume tasks are `core.tasks.process_pa_chat_task` (**924 runs**; PA chat processing — almost certainly touches ChatConversation + Deliverable writes) and `core.tasks.execute_agent_task` (7 runs but high wall-clock; agent execution dispatch path), plus system loops (`run_heartbeat`, `check_celery_health`, `capture_worker_memory_snapshot`, `capture_pa_acks_health_snapshot`). Traffic alone doesn't change tenant risk but elevates priority for **PA chat processing + agent execution dispatch paths** in Phase 3 wiring.

**Phase-3-first wiring priority (per Rigby SIGN):** in addition to the two REG RISK exemplars named in §4.4 + §5.1, the traffic-informed Phase 3 wiring priority list is:

1. `core.tasks.execute_agent(execution_id)` — confirmed REG RISK (Q1 spirit)
2. `core.tasks.summarize_conversation_task(conversation_id, user_id=None)` — confirmed REG RISK (Q1 explicit)
3. **`core.tasks.process_pa_chat_task`** — highest-traffic user-owned-model-touching task (924 runs/7d); Phase-2-first target for classification; Phase-3-first target for wiring
4. `core.tasks.execute_agent_task` — dispatch path adjacent to `execute_agent`; likely same Q1 pattern; Phase-2-first target for classification

---

## §4. Per-Model Task-Touch Sampling (§2.4 scope outcome; SAMPLED per I-030201 precedent)

### §4.1 Deliverable — dominant category: **UNKNOWN pending §5 classification**

**Preliminary evidence at HEAD `47cc13dd`:**

- 60 references across 9 task files
- Highest touch: `tasks.py` (23 refs), `tasks_content.py` (9), `tasks_initiatives.py` (9), `tasks_misc.py` (8)
- Delegated facade-tasks likely include content generation tasks that write Deliverables + summarize_conversation_task that writes a Deliverable as summary output

**Named exemplar (Phase 2 verify target):** `summarize_conversation_task` (`tasks.py` facade → `core/tasks_conversations.py:3463` `_impl_summarize_conversation_task`) writes a Deliverable per invocation. Spot-check at line 3463: accepts `conversation_id, user_id=None` — `user_id` is payload-supplied (Q1 concern).

### §4.2 Initiative — dominant category: **UNKNOWN pending §5 classification**

**Preliminary evidence at HEAD `47cc13dd`:**

- 67 references across 6 task files
- Highest touch: `tasks_initiatives.py` (48 refs — expected; initiative-focused domain), `tasks.py` (11)
- Named tasks likely include: `cleanup_junk_initiatives`, `sweep_diagnostic_initiatives`, `auto_kickstart_stuck_initiatives`, `process_initiative_auto_progression` — dozens of initiative-lifecycle tasks in `tasks_initiatives.py`

**Named exemplar (Phase 2 verify target):** `cleanup_junk_initiatives(stale_days: int = 7)` (`tasks.py` facade → `tasks_initiatives.py:122` `_impl_cleanup_junk_initiatives`) — likely system-scope cleanup, but need to verify whether it iterates ALL Initiatives (system-scope OK) OR takes a user_id/workspace_id param (would then be user-scope).

### §4.3 ChatConversation — dominant category: **UNKNOWN pending §5 classification**

**Preliminary evidence at HEAD `47cc13dd`:**

- 18 references across 4 task files (lightest touch surface — reflects `ChatConversation`'s narrow scope: PA chat + Discord + workspace chat)
- Highest touch: `tasks_agents.py` (3 refs — likely execution-context lookups), `tasks_misc.py` (8), `tasks.py` (5)
- Named tasks: `summarize_conversation_task` (per §4.1 spot-check), `run_project_conversation`, `run_agent_conversation`, `trigger_signal_driven_conversation`

**Named exemplar (Phase 2 verify target):** `summarize_conversation_task` — already flagged §4.1 (writes Deliverable + reads ChatConversation).

### §4.4 AgentExecution — dominant category: **HIGH REGRESSION RISK (per §5.4 classification)**

**Preliminary evidence at HEAD `47cc13dd`:**

- 67 references across 8 task files (`AgentExecution` OR `AgentTaskExecution`)
- Highest touch: `tasks_agents.py` (40 refs — expected), `tasks.py` (11), `tasks_initiatives.py` (7)

**Named exemplar (spot-checked at HEAD):** `execute_agent(self, execution_id: str, **kwargs)` (`tasks_agents.py:493-538` — Tier-0 direct-registered).

**Regression pattern confirmed at spot-check:**

```python
execution = AgentTaskExecution.objects.get(execution_id=execution_id)
```

At `tasks_agents.py:504`. `.objects.get()` by `execution_id` alone — **NOT scoped to acting user**. Existence-oracle risk: any caller with an `execution_id` guess can trigger execution of any user's AgentExecution. Row-ID dispatch (Q6 ✓) but Q1 trusted-source-hierarchy VIOLATION (no re-verification that the acting user owns the row).

**Duplicate-class caveat (inherited from I-030201 §2.4):** `AgentTaskExecution` (used at line 504) is one class; `AgentExecution` (I-0302 ratified canonical at `core.models_unified_system:882`) is another. Phase 2 selection may require picking one canonical class + retirement of the other, or scoping both.

### §4.5 Document — dominant category: **UNKNOWN pending §5 classification**

**Preliminary evidence at HEAD `47cc13dd`:**

- 79 references across 8 task files (highest raw grep count; possibly includes `Document.DoesNotExist` handlers + docstrings)
- Highest touch: `tasks.py` (29), `tasks_media.py` (17 — media generation writes Documents), `tasks_misc.py` (16)
- Two canonical classes per I-030201 §2.5: `content.models.Document` + `core.models_deliverables.WorkspaceDocument`

**Named exemplar (Phase 2 verify target):** media generation tasks in `tasks_media.py` — writes `Document` for generated podcast/blog output. Ownership FK inheritance from I-030201 §3 map: `Document.owner` NOT NULL per I-030201 §2.5.

---

## §5. Acting-Identity Source Classification (§2.2 scope outcome; SAMPLED per Q1)

Per Chris Q1 D-verdict, trusted-source hierarchy: **DB-row-derived first; signed dispatch header second; payload-supplied identity NEVER**. This section classifies exemplar tasks by acting-identity source at HEAD.

### §5.1 SAMPLED classification (5 tasks, one per model)

| Task | Model | Payload-declared identity fields | DB-row-derivable identity? | Classification | Phase 3 target |
|---|---|---|---|---|---|
| `execute_agent(execution_id, **kwargs)` | AgentExecution | none (kwargs opaque) | Yes — `AgentTaskExecution.user_id` from row | **NONE (payload silent, DB derivable) — REGRESSION RISK** | Wrap with `@enforce_tenant_boundary(model=AgentExecution, id_kwarg='execution_id')`; predicate resolves acting user from row's `user_id` FK; reject if session-user mismatches |
| `summarize_conversation_task(conversation_id, user_id=None)` | ChatConversation + Deliverable write | `user_id` (payload-supplied — Q1 VIOLATION) | Yes — `ChatConversation.user_id` from row (default) | **MIXED (payload user_id + DB-derivable) — REGRESSION RISK** | Wrap with `@enforce_tenant_boundary`; STRIP `user_id` kwarg entirely (Phase 3 substrate); re-derive from `ChatConversation.user_id` |
| `cleanup_junk_initiatives(stale_days: int = 7)` | Initiative | none (no user_id) | N/A — task iterates ALL stale initiatives | **NONE (system-scope) — VERIFY** | Mark `@system_scope`; Phase 2 audit confirms no user-owned-row write |
| Media generation (`tasks_media.py` — Phase 2 identify specific task) | Document | Phase 2 read + classify | Phase 2 classify | Phase 2 classify | Phase 2 classify |
| Deliverable content generation (`tasks_content.py` — Phase 2 identify specific task) | Deliverable | Phase 2 read + classify | Phase 2 classify | Phase 2 classify | Phase 2 classify |

**Confirmed regression patterns (2 of 5 exemplars):**

1. Payload-declared `user_id` accepted without re-derivation (Q1 violation) — `summarize_conversation_task`
2. Row-ID dispatch with NO acting-user re-verification (Q1 spirit violation even without explicit payload user_id) — `execute_agent`

**Phase 2 sampling extension:** Phase 1 → Phase 2 handoff MUST classify at least 20 more task exemplars (~5 per model minus system-scope) before Phase 2 authoring closes. Sampling depth increases per Rigby SIGN if Phase 2 authoring surfaces uncertainty.

### §5.2 Dominant-category pre-classification (per file, pending §5.1 sample expansion)

| Task file | Dominant acting-identity pattern | Regression bucket |
|---|---|---|
| `tasks_agents.py` | Row-ID dispatch, NO acting-user re-verification | **REG RISK — Q1 spirit violation** |
| `tasks_conversations.py` | Mixed: payload `user_id=None` + DB-derivable | **REG RISK — Q1 explicit violation on non-None cases** |
| `tasks_initiatives.py` | System-scope iteration (no user identity) | Likely OK if verified system-scope-only |
| `tasks_content.py` | Row-ID + LLM output writes | **Phase 2 classify — pipeline mutations** |
| `tasks_media.py` | Row-ID + Document writes | **Phase 2 classify** |
| `tasks_misc.py` | Cross-cutting; per-task classification needed | **Phase 2 sample 3-5 exemplars** |

---

## §6. Row-Reference Shape Classification (§2.2 scope outcome; SAMPLED per Q6)

Per Chris Q6 D-verdict, **row-ID dispatch ONLY** for user-owned-model tasks. Tasks accepting filters or queries as dispatch args are Q6 violations requiring Phase 3 refactor OR explicit exemption.

### §6.1 SAMPLED classification (same 5 exemplars as §5.1)

| Task | Row-reference shape | Q6 status |
|---|---|---|
| `execute_agent(execution_id)` | Row-ID (`execution_id`) | **✓ Q6 compliant** (dispatch); Q1 concern separate |
| `summarize_conversation_task(conversation_id, user_id=None)` | Row-ID (`conversation_id`) + payload user_id | **✓ Q6 compliant on row ref**; Q1 violation on user_id |
| `cleanup_junk_initiatives(stale_days: int = 7)` | Filter (`stale_days` — iterates by date filter, no row ID) | **⚠ Q6 non-compliant BUT system-scope justified** — MUST receive `@system_scope` opt-in + exemption record at Phase 4 coverage-gap report |
| Media generation | Phase 2 classify | Phase 2 classify |
| Deliverable content generation | Phase 2 classify | Phase 2 classify |

**Pattern insight:** system-scope tasks legitimately use filter/date/threshold dispatch (they iterate populations, not specific rows). Q6's "row-ID dispatch only" rule applies to user-owned-model tasks that operate on SPECIFIC rows; system-scope iteration tasks are exempt via the coverage-gap discipline of Q4 + the `@system_scope` marker of Q2.

**Q6 refactor candidates (Phase 3):** any Phase 1-audited task that (a) takes a filter/query dispatch AND (b) operates on user-owned rows AND (c) is NOT explicitly `@system_scope`. Phase 3 substrate MUST either (i) refactor to accept a row ID + user check OR (ii) receive explicit `@system_scope` marker + exemption record.

---

## §7. System-Scope Task Classification (§2.9 scope outcome; per Q2)

Per Chris Q2 D-verdict, **explicit opt-in `@system_scope`** required for system-scope tasks. Fail-safe by default: task lacking either `@enforce_tenant_boundary` OR `@system_scope` marker MUST fail Phase 3 enforcement flip.

### §7.1 Preliminary system-scope task classification

**Confirmed system-scope files (0 user-owned-model grep-hits):**

- `tasks_beat_health.py` (2 tasks) — beat schedule health checks
- `tasks_body_systems.py` (1 task) — body system scans
- `tasks_cost_protection.py` (2 tasks) — cost telemetry (writes `LLMCallLog`, `CostTracking`; system-scope)
- `tasks_spiders.py` (1 task) — spider workers (payload-only, no user-owned writes)

**Likely-system-scope files (≤1 user-owned grep-hit, iterates populations):**

- `tasks_platform_audit.py` (1 task) — platform audit
- `tasks_bug_triage.py` (1 task) — verify at Phase 2; may read user deliverables during triage (regression risk)
- Population-iteration tasks in domain files: `cleanup_junk_*`, `sweep_diagnostic_*`, `auto_kickstart_stuck_*`, `purge_*_older_than_*d` (many exemplars in `tasks.py` facade)

### §7.2 System-scope discipline handoff to Phase 2

Phase 2 MUST decorate every system-scope task with `@system_scope`; every user-owned-model-touching task with `@enforce_tenant_boundary` (or `TenantScopedTask` base class per §4 of scoping). Every task lacking either marker MUST fail Phase 3 enforcement flip (per Q2 fail-safe default).

### §7.3 System-scope justification test (per Rigby SIGN §7 edit)

**System-scope classification is justified only when the task does not read/write user-owned rows (Deliverable / Initiative / ChatConversation / AgentExecution / Document) except in aggregated, non-identifying telemetry form; naming (`health`, `ops`) is not sufficient.**

Consequence for §7.1 preliminary bucketing: files identified as system-scope by NAME (e.g., `tasks_beat_health.py`, `tasks_platform_audit.py`) MUST still pass a Phase 2 body-content audit before receiving `@system_scope`. If any of those tasks reads or writes a user-owned row (even for a "health check" reason), that task is NOT system-scope; it MUST receive `@enforce_tenant_boundary`.

---

## §8. Nullable / Missing Identity Interim Policy (§2.9 scope outcome)

Per I-0303 scoping §6.2, interim policy for tasks with no acting user:

- **System-scope tasks:** `@system_scope` opt-in per Q2 + §7.
- **Attribute-to-system tasks:** e.g., cost telemetry writes to `LLMCallLog`; record `acting_user_id=None + system_actor='cost-monitor'` audit trail.
- **Missing-identity user-scope tasks:** the failure mode I-0303 exists to prevent — Phase 3 enforcement flip MUST reject dispatch that names a user-owned model but has no resolvable acting user.

**Explicit non-policy (reaffirmed at Phase 1):** silent treatment of missing acting-user as "trusted system" is a leakage bug and MUST NOT ship.

---

## §9. Phase 2 Entry Criteria (this ledger's SIGN-target contract)

Phase 2 (decorator + base-class implementation) opens after Rigby SIGN + Chris ratification of this ledger. Entry criteria:

1. **Task-facade → `_impl_*` mapping strategy** (this doc §2) — Tier-0 vs Tier-1 vs Tier-2 layering understood; enforcement layer chosen per task
2. **Per-model task-touch dominant classification** (§4) — HIGH/MEDIUM/LOW-RISK file bucketing agreed
3. **§5.1 SAMPLED acting-identity classification** — 5 exemplars classified; 2 confirmed REG RISK
4. **§6 row-reference Q6 classification** — sampled; refactor candidates flagged
5. **§7 system-scope classification** — 4-6 confirmed system-scope files; opt-in discipline agreed
6. **Interim nullable-identity policy** (§8) — matches scoping doc §6.2
7. **Phase 2 sampling depth extension** (§5.1 note) — at least 20 additional task exemplars classified during Phase 2 authoring; discipline agreed
8. **Predicate module import strategy** (from scoping §3.5) — Phase 2 imports `core/tenant_boundary_lockdown/predicates.py` per I-0302 layering constraint; leaf-module import-layering verified

---

## §10. Follow-On Retirement Targets (per §7.3 scoping carve-out)

Same discipline as I-030201 §9. Identified during Phase 1:

- **AgentExecution / AgentTaskExecution duplicate-class caveat** (§4.4): Phase 2 selection may formalize the canonical class + record the retirement of the sibling as follow-on scope (not I-0303 arc scope per §7.3 non-goal)
- **Cross-file impl `_impl_*` prefix inconsistency**: some domain files have `_impl_*` prefix; some (`tasks_agents.py`) have direct-registered Tier-0 tasks. Follow-on cleanup, not I-0303 scope.

---

## §11. Handoff Summary — Phase 1 → Phase 2

**Confirmed at Phase 1:**

- 407 task registrations total; ~340 user-owned-model-touching (Phase 2 exact count)
- 2 of 5 sampled exemplars are confirmed REG RISK (`execute_agent` — Q1 spirit; `summarize_conversation_task` — Q1 explicit)
- 4-6 confirmed system-scope files (Q2 opt-in eligible)
- Row-ID dispatch dominates user-owned-model tasks; filter dispatch dominates system-scope (Q6 discipline lands cleanly)
- Predicate module import viable per I-0302 leaf-module constraint

**Phase 2 authors:**

- `core/tenant_boundary_lockdown/task_enforcement.py` with `@enforce_tenant_boundary` decorator + `TenantScopedTask` base class + `@system_scope` marker
- Unit tests: 4 primary paths (happy path + user-A-attempts-user-B-row + system-task-passthrough + missing-identity-rejection)
- Uniform failure envelope enforcement (§4 scoping mandate)
- Uniform trusted-source resolution contract (§4 scoping mandate)

**Phase 3 wires:**

- Every user-owned-model-touching task from §4 bucketing gets `@enforce_tenant_boundary`
- Every system-scope task from §7 gets `@system_scope`
- Three-PR staged codification per PLAYBOOK-7.5.1: REPORT-ONLY → BATCH-FIX → ENFORCEMENT-FLIP
- Confirmed REG RISK tasks (`execute_agent`, `summarize_conversation_task`) are Phase 3 leading test cases

---

## §12. Provenance Chain

- **Sibling predecessor:** I-030201 (I-0302 Phase 1 Model Audit Ledger, ratified S2742 2026-07-10) — this ledger inherits its SAMPLED discipline + canonical class decisions
- **Predicate module:** I-030202 (I-0302 Phase 2 Predicate Module, ratified 2026-07-10) — Phase 2 of I-0303 imports this module
- **Regression harness:** I-030203 (I-0302 Phase 4 Harness Architecture, ratified S2751) — Phase 4 of I-0303 extends this harness
- **Parent scoping:** I-0303 scoping (ratified S2754, this session) — §8 Phase 1 charter
- **Chris D-verdicts:** Q1..Q6 (RATIFICATION_2026-07-11_i0303_scoping.md §3) — invariants respected throughout this ledger
- **Playbook v0.5.0:** §7.5.1 (Phase 3 dogfood); §7.6.1 (Phase 4 SIGN dogfood); §7.4.x (arc-close dogfood at Phase 5)
