---
title: "I-0303 Scoping — Async Tenant-Boundary Enforcement"
status: active
authority: arc-scoping-ratified
session_added: 2754
session_ratified: 2754
last_updated: 2026-07-11
arc_id: I-0303
parent_campaign: RUR-C1 (Tenant Boundary Lockdown)
parent_program: RUR (Real User Readiness)
parent_program_doc: docs/research/implementation/real_user_readiness/CAMPAIGN.md
parent_program_ratification: docs/research/implementation/RATIFICATION_2026-07-10_real_user_readiness.md
parent_workspace: "Real User Readiness Campaign"
parent_workspace_id: 638e9e90-47b4-4bd4-a872-bf16181cf3b5
sibling_arcs:
  - I-0301 (HTTP + AllowAny Surface Remediation + Failure-Data Safety Contract) — CLOSED 2026-07-10; safety contract ratified; sibling
  - I-0302 (Object-Level Authorization on 5 User-Owned Models) — CLOSED 2026-07-10; sibling; predicate module + regression harness produced here are directly reused
head_at_scoping: f7e40ddb
head_at_ratification: TBD (filled at ratification)
current_phase: Phase 1 (Task Boundary Audit Ledger) — authorized to open
ratification_record: docs/research/implementation/RATIFICATION_2026-07-11_i0303_scoping.md
ratification_date: 2026-07-11
ratifier: chris
ratifier_verdict: "agree all"
rigby_sign_state: SCOPING RATIFY WITH EDITS (S2754 turn 1) — 4 axis edits + Q6 addition applied inline; Q1..Q6 leans converged Claude+Rigby; joint recommendation SCOPING RATIFY; Chris "agree all" S2754
chris_d_verdicts:
  - Q1 trusted-source hierarchy — APPROVED MANDATE (DB-row first; signed header second; payload NEVER)
  - Q2 system-task marker — APPROVED EXPLICIT OPT-IN @system_scope (fail-safe by default)
  - Q3 AsyncBoundaryProbe shape — APPROVED NEW PROBE CLASS (task-dispatch semantics distinct from HTTP)
  - Q4 coverage-gap threshold — APPROVED I-0302 PRECEDENT (per-exemption SIGN + Chris ratification)
  - Q5 RUR-C1 close SIGN scope — APPROVED ONE PARENT-CLOSE EVENT (single D-verdict ratifying all three arcs)
  - Q6 canonical row reference — APPROVED ROW-ID DISPATCH ONLY for user-owned-model tasks
depends_on_ratified_artifacts:
  - Failure-Data Safety Contract (frozen, ratified 2026-07-10)
  - I-0301 arc close (ratified 2026-07-10)
  - I-0302 arc close (ratified 2026-07-10) — predicate module + cross-tenant regression harness
  - Engineering Playbook v0.5.0 (ratified 2026-07-11 S2753) — close-ceremony discipline §7.4, staged codification §7.5.1, watchpoint SIGN §7.6.1
parent_close_gate: RUR-C1 parent closes only when I-0301 + I-0302 + I-0303 all pass shared cross-tenant regression per Chris Q2 D-verdict
constraint: Phase 1 opens under this scoping once ratified; amendments during Phase 1+ route through parent CAMPAIGN §10 amendment discipline
---

# I-0303 Scoping — Async Tenant-Boundary Enforcement

> **Arc-scoping document (DRAFT).** RUR-C1 third and final child arc. Answers the scope-outcome template for I-0303. Implementation begins only after Rigby scope SIGN + Chris ratification. RUR-C1 parent invariant close-gate: **RUR-C1 closes only when I-0301 + I-0302 + I-0303 all pass shared cross-tenant regression**. I-0303 close does NOT alone close RUR-C1; RUR-C1 close is a separate ratification event.

---

## §1. Arc Objective

Prove — and enforce — trusted user/workspace identity at **async task boundaries** (Celery task dispatch + execution). Concretely: for every Celery task that **reads/returns OR mutates** rows of user-owned models, re-verify at execution time that the acting user and workspace match the committed DB row — NOT the LLM- or caller-supplied payload. Read-only tasks that return user-owned rows are equally in scope; existence-oracle risk on read is the same class as mutation risk on write.

**Boundary enforcement** means: at task-execution start, the task MUST (a) resolve `acting_user_id` + `acting_workspace_id` from a trusted source (default: **DB-row-derived identity** — resolve from the committed row referenced by dispatch; secondary: signed dispatch header only when DB-row-derived identity is not resolvable; NEVER payload-supplied strings that could be forged by a compromised LLM prompt-injection or a stale dispatch), (b) re-verify ownership using the ownership predicates ratified at I-0302 Phase 2, and (c) reject the dispatch fail-loud per the I-0301 safety contract if verification fails.

**Scope clamp (Rigby S2754 SIGN edit).** In-scope models are the 5 named in the parent CAMPAIGN §4 (Deliverable, Initiative, ChatConversation, AgentExecution, Document). Any additional user-owned model discovered during Phase 1 audit that touches Celery tasks WILL be added to the arc scope with a Phase 1 audit amendment; models not surfaced by Phase 1 are explicitly OUT-of-scope for I-0303.

### Two acceptable enforcement mechanisms (informative, per parent CAMPAIGN §4)

- **Decorator-based re-verification** — a task-scope `@enforce_tenant_boundary` decorator that wraps task bodies, resolves acting identity, calls the I-0302 predicate module, and rejects mismatches. Applied at task-definition time.
- **Base-class re-verification** — a `TenantScopedTask` Celery base task class that runs the same check in `before_start` / dispatch hook. Applied at task-registration time.

Per-task choice at implementation time; the task-boundary regression test must accept either.

### Deliverable of the arc

**Per-task cross-tenant leakage tests** (one per each task class touching the 5 user-owned models — plus the shared harness reused from I-0302) that:

- Enumerate every Celery task that reads or writes rows of `Deliverable`, `Initiative`, `ChatConversation`, `AgentExecution`, or `Document`
- Dispatch as user-A with a payload naming a row owned by user-B
- Assert the task rejects fail-loud per the I-0301 safety contract (task returns FAILED with `reason_code='tenant_boundary_violation'`; NO mutation of the target row; NO existence-oracle leak in `human_message`)
- CI-blocking, uses the same harness as I-0302 (extended with async-boundary probes)

---

## §2. Required Scope Outcomes

Per the ratified parent CAMPAIGN and the I-0302 §7.2 deferral list, this scoping must produce implementation-driving answers to:

- **§2.1** — Which Celery task classes touch the 5 user-owned models? Full task-boundary inventory.
- **§2.2** — For each task class: what is the **acting-identity payload shape** at dispatch time (user_id, workspace_id, both, neither)?
- **§2.3** — What is the **trusted source of acting identity** at execution time — session lookup, signed dispatch header, DB row cross-check, or a combination?
- **§2.4** — Which existing tasks already re-verify workspace/ownership at execution start (baseline)?
- **§2.5** — Which existing tasks accept payload-supplied identity blindly (regression risk)?
- **§2.6** — Per task, does the decorator approach or the base-class approach fit better?
- **§2.7** — What is the shape of the **async-boundary probe extension** to the shared cross-tenant regression harness (built at I-0302 Phase 4)?
- **§2.8** — How does the I-0302 predicate module get imported into task-scope code without violating the import-layering constraint recorded at I-0302 §6.1?
- **§2.9** — What is the interim policy for tasks whose payload legitimately has no acting user (system tasks, spider workers, ops-orchestrator dispatch)?
- **§2.10** — Failure-envelope conformance: every task rejection conforms to the ratified safety contract (`reason_code` + `human_message` + `trace_id`; no existence-oracle in the failure surface).

---

## §3. Current-HEAD Async Boundary Audit (preliminary; full audit is Phase 1)

Preliminary evidence gathered during scoping-time verify-before-build. Full per-task audit ledger opens at Phase 1.

### §3.1 — Task file inventory (§2.1 preliminary)

At HEAD `f7e40ddb`: **19 `core/tasks*.py` files**, PLATFORM_INVENTORY reports **415 user-defined Celery tasks** total. Subset touching the 5 user-owned models is Phase 1's audit scope.

Files highest-signal for tenant-boundary risk (from grep + prior audit context):

- `core/tasks_agents.py` — agent-execution dispatch, likely `AgentExecution` writes
- `core/tasks_content.py` — deliverable / document mutations
- `core/tasks_conversations.py` — `ChatConversation` writes
- `core/tasks_initiatives.py` — `Initiative` mutations
- `core/tasks.py` (root) — mixed; needs classification
- `core/tasks_executor.py` — cross-cutting executor path

Not in-scope for I-0303 (no user-owned-model touch expected but Phase 1 confirms):

- `core/tasks_beat_health.py` (system beat health)
- `core/tasks_body_systems.py` (system-scope body scans)
- `core/tasks_spiders.py` (spider workers — payload-only, no user-model writes)
- `core/tasks_platform_audit.py` (system audit)

### §3.2 — Existing workspace-scope patterns (§2.4 preliminary)

`grep -c 'workspace_id\|workspace_scope\|verify_workspace\|workspace_owner' core/tasks.py` returned **4** — implying most tasks in the root file do NOT touch workspace scope. Preliminary; Phase 1 completes the full-repo grep across all 19 task files + associated services.

### §3.3 — Acting-identity payload shape (§2.2 preliminary)

Preliminary — I-0302 Phase 1 audit ledger recorded that many tasks receive `user_id` and/or `workspace_id` as payload kwargs. Whether those are trusted (session-derived) or forgeable (payload-supplied via LLM tool call) is Phase 1's binary classification task.

### §3.4 — Trusted-source options (§2.3 preliminary)

Candidate mechanisms at HEAD:

- **Session-lookup**: task reads `AgentExecution.user_id` / `ChatConversation.user_id` from the row referenced by dispatch. Trusted because DB row is the committed source of truth.
- **Signed dispatch header**: a HMAC-signed `X-Tenant-Scope` header on task headers, validated at execution start. Requires new dispatch middleware.
- **Django session sync**: not applicable at task boundary (no request context).

Phase 1 records per-task classification; Phase 2 chooses the canonical mechanism.

### §3.5 — Predicate module reuse (§2.8 preliminary)

I-0302 Phase 2 predicate module lives at `core/tenant_boundary_lockdown/predicates.py` (11 predicate functions + 60 unit tests, ratified 2026-07-10). Import from task-scope code is subject to the same import-layering constraint recorded at I-0302 §6.1 — task modules cannot import Django views, but the predicate module is service-layer and importable from tasks per the layering spec.

Phase 2 of I-0303 will confirm import graph is clean (no circular dependency introduced).

---

## §4. Enforcement Mechanism Decision Framework (§2.6)

The choice between decorator and base-class approach is not one-size-fits-all. Framework:

**Decorator-based re-verification** (`@enforce_tenant_boundary(model=X, id_kwarg='deliverable_id')`) — best for:
- Existing tasks that can be annotated incrementally
- Task-by-task rollout without changing task registration
- Tasks whose acting-identity source varies (e.g., some resolve from `AgentExecution.user_id`, some from payload)

**Base-class re-verification** (`class DeliverableMutationTask(TenantScopedTask)`) — best for:
- New task classes authored during Phase 3
- Tasks with a uniform acting-identity source across a domain
- Tasks that need a consistent lifecycle hook (`before_start` + `after_return`)

**Decision authority:** per-task, chosen at Phase 3 wiring time. Phase 2 predicate module signatures accommodate both patterns.

**Uniform contract (Rigby S2754 SIGN edit).** Regardless of decorator vs base-class choice, both mechanisms MUST enforce a **uniform failure envelope** (identical `reason_code='tenant_boundary_violation'`, identical `human_message` shape per the I-0301 safety contract) AND a **uniform trusted-source resolution contract** (identical hierarchy: DB-row-derived identity first, signed dispatch header second, payload-supplied identity NEVER). Per-task choice is about ergonomics + lifecycle hook fit; it is NOT about acceptable failure semantics or acceptable trust sources.

---

## §5. Shared Cross-Tenant Regression Harness — Async-Boundary Extension (§2.7)

### §5.1 — Reuse of I-0302 harness

I-0302 Phase 4 produced 6 test modules under `tests/security/` covering HTTP + view-layer regressions (ratified S2751). Per I-0302 §5.3, that harness was designed to be shared with I-0303. The extension adds:

- **Probe class: `AsyncBoundaryProbe`** — dispatches Celery task as user-A with a payload naming user-B's row; asserts task returns FAILED with `reason_code='tenant_boundary_violation'`.
- **Coverage matrix cell**: one row per (task class, model) pair. Same shape as the I-0302 endpoint matrix.
- **Sentinel test**: at least one canonical per-model async boundary sentinel that fails CI if the task ships without the decorator/base-class applied.

### §5.2 — CI-blocking

Async-boundary tests are added to the same `security-conformance.yml` workflow that runs I-0302 tests. Any regression on the async-boundary suite reopens Phase 4 close per the deferred behavioral-verify recovery gate recorded at RUR-C1 arc-close ratification.

### §5.3 — Coverage-gap tolerance

Following I-0302 precedent (arc-close close doc §7 recorded matrix coverage gap tolerance), a limited number of tasks MAY be exempted from the async-boundary probe if:

- The task is system-scope (no user-owned model touch)
- The exemption is documented in a coverage-gap report at Phase 4 close
- The exemption receives Rigby SIGN

---

## §6. HTTP-vs-Async Boundary Interaction (§2.8, §2.9)

### §6.1 — HTTP-layer scoping is I-0301 + I-0302 scope

I-0303 does NOT modify HTTP-layer permissions, view-level queryset scoping, or DRF `permission_classes`. Those are I-0301 (permissions) + I-0302 (object-level queryset scoping) scope, both closed. I-0303 assumes HTTP layer is correctly scoped at all task dispatch entry points; task-boundary enforcement is a defense-in-depth layer.

### §6.2 — System / unowned tasks (§2.9)

Interim policy for tasks whose payload legitimately has NO acting user:

- **System-scope tasks** (spider workers, ops audit, beat health): explicit `SystemBoundaryTask` base class (or explicit `@system_scope` decorator marker) that documents "this task does NOT enforce tenant boundary because it acts as the platform, not as a user." Must NOT touch user-owned models.
- **Attribute-to-system** (e.g., cost telemetry writes to `LLMCallLog`): task records `acting_user_id=None + system_actor='cost-monitor'` audit trail. Row remains system-scoped.
- **Spider-worker writes** (`SpiderItemHash`, etc.): system-scope, no user-owned-model touch expected; Phase 1 confirms.

**Explicit non-policy:** silent treatment of missing acting-user as "trusted system" is a leakage bug and MUST NOT ship, even as an interim state.

---

## §7. Scope Boundaries — What Belongs to I-0303 vs Follow-on

### §7.1 In-scope for I-0303

- Celery task boundary re-verification of acting user/workspace against committed DB state
- Rejection of dispatches with untrusted or missing acting identity for user-owned-model mutations
- Async-boundary probe extension to the shared cross-tenant regression harness
- System-task classification (which tasks are legitimately system-scope)
- Coverage-gap report for exempted tasks

### §7.2 Deferred to RUR-C2 (Async State + Fail-Loud + Traceability)

- Canonical `OpsRunEvent` state machine (PENDING → RUNNING → SUCCEEDED | FAILED | CANCELLED) — I-0303 uses the CURRENT state machine and hardens tenant boundary within it
- `support_code + reason_code + trace_id` propagation surface — I-0303 emits the `tenant_boundary_violation` reason_code but the full trace-ID propagation lands at RUR-C2
- Semantic-quality "SUCCEEDED with empty output" detection — RUR-C2 postcondition verification

### §7.3 Deferred to follow-on programs

- Full task-registration audit for the ~415 tasks not touching user-owned models (I-0303 focuses on model-touching subset)
- Legacy task-class consolidation (any duplicate `AgentExecution` handler classes surface as I-0302 follow-on, not I-0303)
- Async retry idempotency — RUR-C4 scope

### §7.4 Explicit non-goals

- Does NOT modify the I-0302 predicate module (frozen; consumed as-is)
- Does NOT modify the ratified failure-data safety contract
- Does NOT modify HTTP-layer permission enforcement (I-0301 + I-0302 scope)
- Does NOT introduce a new canonical state machine (RUR-C2 scope)
- Does NOT modify the RUR-C1 parent close condition

---

## §8. Implementation Approach + Phases (draft; subject to Rigby SIGN)

### Phase 1 — Task Boundary Audit Ledger (target: 1 session)

- Materialize the per-task boundary audit ledger as a workspace deliverable under `fcd7e683` (RUR-C1 Tenant Boundary Lockdown workspace)
- Per task-touching-user-model: classify acting-identity source (session-derived / payload-supplied / mixed / none); classify existing verification (present / absent / partial)
- System-task classification: which tasks are legitimately system-scope and do not need tenant-boundary enforcement
- Rigby SIGN on the ledger before Phase 2 opens

### Phase 2 — Decorator + Base-Class Implementation (target: 1 session)

- Author `@enforce_tenant_boundary` decorator + `TenantScopedTask` base class in `core/tenant_boundary_lockdown/task_enforcement.py`
- Import the I-0302 predicate module (import-layering verified)
- Unit tests: happy path + user-A-attempts-user-B-row + system-task-passthrough + missing-identity-rejection
- Rigby SIGN on the enforcement module before Phase 3 opens

### Phase 3 — Per-Task Enforcement Application (target: 1-2 sessions; may extend to 2-3 sessions per Rigby S2754 SIGN edit if Phase 1 audit surfaces many mixed/none identity tasks)

- Apply decorator or base-class to every task from Phase 1's audit that touches user-owned models
- Follow PLAYBOOK-7.5.1 staged codification: **REPORT-ONLY** substrate PR (warn-only enforcement) → **BATCH-FIX** PR (close all report-only findings) → **ENFORCEMENT-FLIP** PR (hard gate)
- Track per-task application in ledger; incrementally close rows
- **Session-count elasticity (Rigby S2754 SIGN edit):** if Phase 1 audit ledger classifies more than ~10 tasks as "mixed identity" (payload for some fields + session-derived for others) or "no identity" (system-adjacent tasks that touch user-owned models), Phase 3 MAY expand to 2-3 sessions rather than 1-2 without triggering a scoping amendment; the expansion is anticipated by this SIGN edit

### Phase 4 — Async-Boundary Regression Harness (target: 1 session)

- Extend I-0302's `tests/security/` harness with `AsyncBoundaryProbe` + per-(task, model) matrix cells
- **Sentinel coverage requirement (Rigby S2754 SIGN edit):** Phase 4 MUST ship at least (a) one sentinel test per user-owned model (5 sentinels minimum) AND (b) one sentinel test per task-domain cluster (`agents`, `content`, `conversations`, `initiatives`, and any additional cluster identified at Phase 1) so coverage isn't accidentally model-only. Task-domain clusters map to `core/tasks_<domain>.py` file groupings.
- CI-block on regression via `security-conformance.yml`
- Coverage-gap report for any exempted task (per §5.3)
- Rigby SIGN on the harness before Phase 5 opens
- SIGN uses PLAYBOOK-7.6.1 watchpoint-attestation shape (dogfooding v0.5.0)

### Phase 5 — I-0303 Arc Close

- Close doc: `I-030399_i0303_arc_close.md`
- Ratification record: `RATIFICATION_<date>_i0303_arc_close.md`
- Close ceremony under PLAYBOOK-7.4.1 (single-PR bundle) + PLAYBOOK-7.4.3 (COMBINED or SPLIT cascade)
- Triggers **RUR-C1 parent close ratification** — Chris D-verdict on whether all three arcs (I-0301 + I-0302 + I-0303) pass the shared cross-tenant regression suite

---

## §9. Open Scope Questions Requiring SIGN + Chris Ratification

**Joint Claude+Rigby leans applied (S2754 SIGN turn 1).** Claude and Rigby converged on all six questions; the leans below reflect the joint recommendation. Chris ratifies yes/no on the joint shape per the new agree-first workflow rule.

- **Q1 — Trusted-source hierarchy.** Should Phase 2 mandate a canonical hierarchy or allow per-task choice?
  - **Joint lean: MANDATE canonical hierarchy** — DB-row-derived identity first; signed dispatch header second (only when DB-row identity is not resolvable); payload-supplied identity NEVER. Auditability + fail-safe both argue for mandate. Rigby lean matches Claude lean.

- **Q2 — System-task marker discipline.** Explicit `@system_scope` decorator (opt-in) vs implicit-by-absence?
  - **Joint lean: EXPLICIT OPT-IN** `@system_scope` — fail-safe by default. Task lacking any marker MUST fail CI at Phase 3 enforcement flip (either annotated with tenant boundary or with system scope). No silent passthrough. Rigby lean matches Claude lean.

- **Q3 — `AsyncBoundaryProbe` shape.** Reuse I-0302's endpoint probes verbatim, OR new probe class tailored to task-boundary semantics?
  - **Joint lean: NEW PROBE CLASS** — task-dispatch semantics differ enough from HTTP endpoint semantics that reuse would obscure test intent. Shared matrix + shared coverage-gap tolerance stay; probe class is distinct. Rigby lean matches Claude lean.

- **Q4 — Coverage-gap threshold.** How many exempted tasks trigger re-ratification of the coverage-gap tolerance policy?
  - **Joint lean: MATCH I-0302 PRECEDENT** — tolerance exists (per I-0302 arc-close doc §7); any exemption MUST be enumerated in the coverage-gap report AND receive Rigby SIGN + Chris ratification at Phase 4 close. No numerical threshold; discipline is per-exemption sign-off, not aggregate count. Rigby lean matches Claude lean.

- **Q5 — RUR-C1 close SIGN scope.** After I-0303 closes, is RUR-C1 parent close ONE additional ratification event or two (regression suite pass + parent-close)?
  - **Joint lean: ONE EVENT** — ratifying "all three arcs pass the shared harness" as a single Chris D-verdict at RUR-C1 parent close. Splitting would add ceremony without evidence benefit. Rigby lean matches Claude lean.

- **Q6 — Canonical row reference at task dispatch (added by Rigby S2754 SIGN turn 1).** Should tasks accept row IDs (re-resolved from DB at execution start) OR filters/queries (higher oracle risk)?
  - **Joint lean: ROW-ID DISPATCH ONLY for user-owned-model tasks** — tenant enforcement is easiest and least leaky when tasks accept row IDs and re-resolve in DB. Tasks that currently accept filters/queries against user-owned models are higher existence-oracle risk and MUST either (a) refactor to accept IDs (Phase 3 substrate) or (b) receive an explicit exemption enumerated in the coverage-gap report (per Q4). Row-ID discipline is the trusted-source-hierarchy Q1 mechanism made concrete. Joint recommendation.

---

## §10. Sibling Arc Cross-References + Dependency Ordering

**Sibling arc state at S2754 open:**

- **I-0301 (CLOSED 2026-07-10):** HTTP + AllowAny + failure-data safety contract ratified. I-0303 CONSUMES the safety contract for failure-envelope conformance.
- **I-0302 (CLOSED 2026-07-10):** Object-level authorization + predicate module + shared regression harness. I-0303 CONSUMES the predicate module (§3.5, §4, Phase 2) and the harness (§5).
- **I-0303 (this arc, OPENING S2754):** Async tenant-boundary enforcement. Third and final RUR-C1 child.

**RUR-C1 parent close-gate:** RUR-C1 parent close is blocked until I-0303 closes AND all three arcs jointly pass the shared cross-tenant regression suite (Chris Q2 D-verdict).

**Cross-arc close-ceremony discipline (new at v0.5.0):**

I-0303 close ceremony follows PLAYBOOK-7.4.1/7.4.2/7.4.3 (close-ceremony delivery); Phase 3 substrate follows PLAYBOOK-7.5.1 (three-PR staged codification); every phase-close + arc-close SIGN follows PLAYBOOK-7.6.1 (watchpoint-attestation shape). I-0303 is the first arc opened under v0.5.0.

**Downstream unlock at I-0303 close:**

- RUR-C1 parent close ratification (single event per Q5 lean above)
- RUR-C2 remains eligible-to-open per Wave 1 staged-overlap (was eligible during I-0303 too)
- RUR-C3 unblocks once RUR-C2 lands the canonical state machine

---

## §11. Provenance Chain

- **Scoping precedent:** `docs/research/implementation/tenant_boundary_lockdown/I-0302_scoping.md` (ratified S2742)
- **I-0302 §7.2 deferral:** identifies exactly what I-0303 must cover (Celery task workspace-scope re-verification + reject unsafe dispatches + user-A → user-B negative tests)
- **CAMPAIGN.md §4 arc slot:** I-0303 Async Tenant-Boundary Enforcement, effort M, prereq I-0301 safety contract signed
- **CAMPAIGN.md §5 dependency:** RUR-C1 parent close requires all three arcs pass shared regression
- **Predicate module:** `core/tenant_boundary_lockdown/predicates.py` (ratified I-0302 Phase 2)
- **Regression harness:** `tests/security/` (ratified I-0302 Phase 4)
- **Failure-data safety contract:** `docs/research/implementation/tenant_boundary_lockdown/failure_data_safety_contract.md` (ratified I-0301)
- **Close-ceremony discipline (new):** PLAYBOOK-7.4.1/7.4.2/7.4.3/7.5.1/7.6.1 (ratified v0.5.0 S2753)
