---
title: "I-0302 Scoping — Object-Level Authorization on 5 User-Owned Models"
status: active
authority: arc-scoping-ratified
session_added: 2742
last_updated: 2026-07-10
arc_id: I-0302
parent_campaign: RUR-C1 (Tenant Boundary Lockdown)
parent_program: RUR (Real User Readiness)
parent_program_doc: docs/research/implementation/real_user_readiness/CAMPAIGN.md
parent_program_ratification: docs/research/implementation/RATIFICATION_2026-07-10_real_user_readiness.md
parent_workspace: "Real User Readiness Campaign"
parent_workspace_id: 638e9e90-47b4-4bd4-a872-bf16181cf3b5
sibling_arcs:
  - I-0301 (HTTP + AllowAny Surface Remediation + Failure-Data Safety Contract) — CLOSED 2026-07-10; safety contract ratified; sibling
  - I-0303 (Async Tenant-Boundary Enforcement) — NOT YET OPENED; sibling
head_at_scoping: 8150d9cd
head_at_ratification: 8150d9cd
current_phase: Phase 1 (Model Audit Ledger) — authorized to open
ratification_record: docs/research/implementation/RATIFICATION_2026-07-10_i0302_scoping.md
ratification_date: 2026-07-10
ratifier: chris
rigby_sign_state: SIGN-CLEAN (post-edit after F1..F6 SIGN-WITH-EDITS applied)
depends_on_ratified_artifacts:
  - Failure-Data Safety Contract (frozen, ratified 2026-07-10)
  - I-0301 arc close (ratified 2026-07-10)
parent_close_gate: RUR-C1 parent closes only when I-0301 + I-0302 + I-0303 all pass shared cross-tenant regression per Chris Q2 D-verdict
chris_d_verdicts:
  - Q7 tenant boundary — APPROVED hybrid per-model: workspace-scoped (Deliverable, ChatConversation); per-user (Initiative, AgentExecution, Document)
  - Q2 AgentExecution triple-class — APPROVED lean (arc picks canonical; duplicate retirement is follow-on)
  - Q3 nullable-owner policy — APPROVED lean (defer to Phase 1; escalate if volumes large)
  - Q6 reuse not_found reason_code — APPROVED lean (existence-oracle avoidance per I-0301 precedent)
constraint: Phase 1 opens under this scoping; amendments during Phase 1+ route through parent CAMPAIGN §10 amendment discipline
---

# I-0302 Scoping — Object-Level Authorization on 5 User-Owned Models

> **Arc-scoping document.** RUR-C1 second child arc. Answers the scope-outcome template for I-0302. Implementation begins only after Rigby scope SIGN + Chris ratification. Wave 1 authorization is permission to scope this arc, NOT permission to begin remediation.
>
> Parent invariant: **RUR-C1 closes only when I-0301 + I-0302 + I-0303 all pass shared cross-tenant regression.** I-0302 close does NOT close RUR-C1.

---

## §1. Arc Objective

Prove — and enforce — object-level ownership on the 5 user-owned models named in the parent CAMPAIGN §4:

1. `Deliverable`
2. `Initiative`
3. `ChatConversation`
4. `AgentExecution` (name is conceptual; multiple concrete models exist — see §3)
5. `Document`

**Ownership enforcement** means: for every code path that returns or mutates rows of these models, the enforced invariant is `row.owner == request.user` (or the equivalent tenant-scope predicate). Any code path that returns a row not owned by the requesting user is a bug.

### Two acceptable enforcement mechanisms (per parent CAMPAIGN §4)

- **`Meta.permissions` custom class exercised by the regression suite** — Django's built-in object-level permissions framework, extended with a custom `has_object_permission` on a DRF permission class.
- **Verified view-level queryset/service-layer scoping** — the queryset is filtered by `user=request.user` (or the tenant predicate) before object lookup can succeed, and the scoping is verified by an integration test firing user-A → user-B negative probes.

Per-endpoint choice at implementation time; the model-level regression test must accept either.

### Deliverable of the arc

**Per-model leakage tests** (5 tests, one per model — plus a shared harness) that:

- Iterate every code path that returns or accepts an ID of the model
- As user-A: attempt to read/write/delete a row owned by user-B
- Assert the response is 404 (per Rigby S2742 Stage 2b SIGN Q6 existence-oracle avoidance) — NOT 403 (which reveals existence)
- CI-blocking

---

## §2. Required Scope Outcomes (Chris S2742 §8)

Per the ratified parent CAMPAIGN, this scoping must produce implementation-driving answers to:

- **§2.1** — Which concrete model is authoritative for each of the 5 named model concepts?
- **§2.2** — For each concrete model: what are the ownership FKs (`user`, `workspace`, `owner`, `created_by`) and their nullability?
- **§2.3** — Which existing views/services touch each model with ownership scoping already in place?
- **§2.4** — Which existing views/services touch each model WITHOUT ownership scoping (regression risk)?
- **§2.5** — Which endpoints route to each model?
- **§2.6** — Per model, does `Meta.permissions` or view-level scoping fit better?
- **§2.7** — What is the shared cross-tenant regression harness shape (the same suite RUR-C1 close depends on)?
- **§2.8** — How do async task boundaries (I-0303 scope) interact with model-level enforcement (I-0302 scope)?
- **§2.9** — Which changes are strictly I-0302 vs deferred to I-0303 vs the follow-on programs recorded at I-0301 close?
- **§2.10** — Failure-envelope conformance: every 403/404 response from the new ownership checks conforms to the ratified safety contract.

---

## §3. Current-HEAD Model Audit (preliminary; full audit is Phase 1)

Preliminary evidence gathered during scoping-time verify-before-build. Full per-model audit ledger opens at Phase 1.

### §3.1 — Concrete-model map (§2.1)

| CAMPAIGN §4 concept | Concrete model path | Notes |
|---|---|---|
| `Deliverable` | `core.models_deliverables.Deliverable` | Single canonical class |
| `Initiative` | `core.models_document_registry.Initiative` | Single canonical class |
| `ChatConversation` | `core.models.conversations.ChatConversation` | Single canonical class |
| `AgentExecution` | **3 candidates — must resolve at Phase 1**: `intelligence.models.AgentExecution` (line 587), `intelligence.models.agent_execution.AgentExecution` (line 11), `core.models_unified_system.AgentExecution` (line 882, self-labeled DEPRECATED). Also relevant: `AgentTaskExecution` (used by the `AgentExecutionViewSet` in `core/views/agents.py`). Per I-0301 Stage 2b/Stage 3 audits the ViewSet is not URL-routed; **do not assume `AgentTaskExecution` is user-facing without Phase 1 proof of live callers.** | Phase 1 must produce a canonical-model decision + retire duplicates as a follow-on if they diverge |
| `Document` | `content.models.Document` (extends `UnifiedBaseModel`) | Single canonical class. `Document.owner` is defined directly on `content.models.Document` (FK to User, **NOT NULL**); `UnifiedBaseModel` does NOT provide `owner`. |

### §3.2 — Ownership FK map (§2.2 — preliminary)

| Model | FK column | Type | Nullable? | Notes |
|---|---|---|---|---|
| Deliverable | `user` | ForeignKey → AUTH_USER_MODEL | **Yes** (CASCADE) | Also has nullable `workspace` FK; existing user-less rows possible |
| Deliverable | `workspace` | ForeignKey → `core.ProjectWorkspace` | Yes (SET_NULL) | Composite ownership predicate candidate |
| Initiative | `owner` | ForeignKey → `core.UnifiedUser` | **Yes** (SET_NULL) | Per Rigby SIGN F1 verification 2026-07-10. `created_by` is a CharField default 'system'; not FK; not a real ownership predicate |
| ChatConversation | `user` | ForeignKey → AUTH_USER_MODEL | (confirmed populated during S2746 session_lifecycle work) | Session-track model |
| ChatConversation | `workspace` | ForeignKey → `core.ProjectWorkspace` | Yes | Composite ownership predicate candidate |
| AgentExecution | Per-class; unresolved | Per-class | Per-class | Phase 1 must resolve which class + which FK is authoritative |
| Document | `owner` | ForeignKey → User | **NOT NULL** (CASCADE) | Verified per Rigby SIGN F1 2026-07-10. Defined directly on `content.models.Document`; NOT inherited from `UnifiedBaseModel`. |

**Nullable FKs are a real risk class:** existing rows with `user=NULL` cannot be attributed to a user; a leakage test that queries by `user=None` might match them for user-A too. Phase 1 must:
- Count `user=NULL` rows per model
- Decide policy: purge / attribute-to-system / preserve-with-explicit-scope
- Consider migrating to `NOT NULL` after the policy applies

### §3.3 — Existing view-level scoping (§2.3, §2.4 — preliminary)

Stage 2b PR A added `IsAuthenticated` + user-scoping to 7 `intelligence/views.py` endpoints (Phase 1 will complete the audit; here's what's already known):

| Model | Scoped existing views | Unscoped existing views |
|---|---|---|
| Deliverable | Some via `deliverable_tool` PA path (workspace-scoped) | Need Phase 1 grep — many callers likely bypass ownership scoping via ORM helpers |
| Initiative | Need Phase 1 audit | Need Phase 1 audit |
| ChatConversation | `session_tool.retire` / `session_tool.set_active` / `session_tool.seed` filter by `user_id=request user` (I-0301 lineage) | Some list/detail views may bypass |
| AgentExecution | `AgentExecutionViewSet.get_queryset()` filters by user IF game_id not present (game_id path now removed per Stage 3 PR B) | Multiple ORM callers likely bypass; `cleanup_stuck_executions` command — needs review |
| Document | `sync_docs_index_to_documents` filters by status — not per-user | Need Phase 1 audit |

---

## §4. Enforcement Mechanism Decision Framework (§2.6)

Per-model, pick between `Meta.permissions` (DRF custom permission class + `has_object_permission`) OR view-level queryset scoping. Rubric:

**Choose `Meta.permissions` + custom permission class when:**
- The model is accessed via multiple DRF viewsets / views
- You need **one canonical predicate** that both DRF and non-DRF callers can share; the DRF permission class calls it, and commands/Celery tasks/services must call the same predicate explicitly. (Note: `Meta.permissions` alone does NOT enforce at ORM callers — it protects only DRF request-time surfaces. Non-DRF enforcement is via explicit predicate call.)
- Object detail lookups need per-object checks (not just queryset filtering)

**Choose view-level queryset scoping when:**
- The model is accessed by very few views (1-3)
- All views use standard `filter(user=request.user)` shape
- Non-DRF access is already scoped at the service layer

**Both mechanisms MUST:**
- Emit safety-contract-conformant 404 responses on ownership failures (per Rigby SIGN Q6)
- Be exercised by the regression harness in §5

Preliminary lean (subject to Phase 1 verification):
- **Deliverable** — view-level scoping (many callers; PA tool + DRF views + admin; view-level is simpler)
- **Initiative** — view-level scoping (single-view surface)
- **ChatConversation** — view-level scoping (session_tool substrate already in place from I-0301)
- **AgentExecution** — `Meta.permissions` (multiple viewsets, ORM callers, cleanup commands)
- **Document** — view-level scoping (main callers are RAG sync + admin)

---

## §5. Shared Cross-Tenant Regression Harness (§2.7)

**Same suite as RUR-C1 close depends on.** New file: `tests/security/test_cross_tenant_object_authz.py`.

### §5.1 — Harness shape (per Rigby SIGN F3 material amendment 2026-07-10)

Parametrized over the 5 models. For each model:

1. **Authentication precondition:** harness always authenticates as two real users (user-A, user-B), each with distinct workspaces. 401/403 are NOT acceptable outcomes for ownership probes — those are separate test axes.
2. Create N owned rows for each user (N ≥ 3 to catch off-by-one).
3. **Two distinct negative-probe types** (must not be conflated in test naming):
   - **Ownership probe:** row exists and is owned by user-B; user-A requests by ID → **expect 404 not_found envelope.** 403 on this probe is a FAIL (existence-oracle leak per Rigby S2742 Stage 2b SIGN Q6).
   - **Nonexistent probe:** user-A requests a random UUID → also expect 404, but different test setup + name.
4. For each read/write/delete detail endpoint touching the model:
   - As user-A read user-B's row by ID → ownership probe assertions
   - As user-A update user-B's row → ownership probe assertions
   - As user-A delete user-B's row → ownership probe assertions
5. **List endpoint semantics** (distinct from detail probes; list endpoints correctly return 200 with filtered results):
   - status == 200
   - user-B row IDs absent from user-A response
   - no cross-tenant counts / aggregates leak (if the endpoint returns aggregates)
6. **Response-body safety-contract probes** (applied on all ownership 404 responses):
   - If response is JSON, run prohibited-content probes (UUIDs / paths / providers / tracebacks / exception values), same battery as `test_bucket_b_remediation.py`.
   - If response is non-JSON (e.g., Django default 404 HTML), FAIL with "envelope missing / non-contract response shape" — this indicates the endpoint fell outside the ratified safety-contract substrate.
   - `support_code` and `reason_code` values are permitted (they're the contract's identifiers).

### §5.2 — CI-blocking

Suite added to `.github/workflows/security-conformance.yml` triggers on model-file changes + view-file changes.

### §5.3 — Shared with I-0303

I-0303 (Async Tenant-Boundary Enforcement) will EXTEND this harness with async-task-boundary probes (not add its own separate suite). RUR-C1 parent close condition: **all three arcs' probes pass in this single suite**.

---

## §6. Async Boundary Interaction (§2.8)

**I-0302 owns:** synchronous request-time object-level authz (DRF view + ORM caller boundaries).

**I-0303 owns:** async task-boundary re-verification. Every Celery task payload carrying an object ID must re-verify ownership against DB before mutation, since the payload was accepted at request-time but the task executes later with elevated privileges.

**Interaction contract:** the ownership predicate defined here (e.g., `Deliverable.objects.filter(user=request.user)`) becomes the same predicate I-0303's task-boundary re-verification calls. I-0302 exports the predicate as a reusable function per-model so I-0303 doesn't have to re-derive it.

Concretely: `core/security/object_authz.py` module ships in I-0302 with per-model functions like `deliverable_visible_to(user, deliverable_id)`. I-0303 imports and calls at task-dispatch verification.

### §6.1 — Import-layering constraint (per Rigby SIGN F4 minor amendment 2026-07-10)

`core/security/object_authz.py` is a **leaf module**:
- MAY import: Django models, settings, `core/security/*` siblings, stdlib
- MUST NOT import: DRF, Celery, `core/views/*`, `core/tasks*`, any module that imports the above

Rationale: predicates are called from BOTH sync request paths AND async task boundaries. Cycles / side-effects at import time would break Celery worker boot or cause request-time DRF cascades.

### §6.2 — Predicate signatures (frozen at Phase 2)

Standard shape per model:
- `can_read_<model>(user, obj) -> bool` — object-level read predicate
- `scope_queryset_<model>(user, qs) -> QuerySet` — queryset filter for list endpoints
- Optionally: `can_write_<model>(user, obj) -> bool` if write authz diverges from read

**Predicates MUST be pure + deterministic:** no request context, no network, no filesystem. Async task boundaries won't have `request` objects; predicates that require them can't be reused.

---

## §7. Scope Boundaries — What Belongs to I-0302 vs I-0303 vs Follow-on

### §7.1 In-scope for I-0302

- Per-model ownership FK audit + policy on nullable FKs
- Per-model `Meta.permissions` custom class OR view-level scoping proof (per §4 rubric)
- New `core/security/object_authz.py` module with per-model predicates
- Failure responses conforming to the ratified safety contract (404 not 403 per Rigby SIGN Q6)
- Cross-tenant regression harness (`tests/security/test_cross_tenant_object_authz.py`)
- CI-blocking wiring for the harness
- Migration of user-NULL rows per Phase 1 policy decision (if migration is required)

### §7.2 Deferred to I-0303 (Async Tenant-Boundary Enforcement)

- Celery task payload workspace-scope re-verification
- Reject async dispatches without trusted user/workspace identity
- User-A → user-B negative tests on task boundaries (uses same harness, adds probes)

### §7.3 Deferred to follow-on programs

- Legacy `AgentExecution` duplicate-class consolidation (I-0302 chooses one canonical class; retirement of the others is orphan-cleanup follow-on scope)
- Bulk backfill of user-NULL rows if the policy is "attribute-to-system" and volumes are large
- Any object-level authz for the other ~50 models not in the parent CAMPAIGN §4 list

### §7.4 Explicit non-goals

- Does NOT touch DRF's existing view-level `permission_classes` — that's I-0301 scope, already closed
- Does NOT modify the ratified safety contract — that's a constitutional artifact
- Does NOT modify the RUR-C1 parent close condition (needs all three arcs)
- **Does NOT change Celery task payloads, trace-ID propagation, or task-routing** — those are I-0303 + RUR-C2 scope (per Rigby SIGN F5 minor amendment 2026-07-10)

### §7.5 Nullable-owner interim policy (per Rigby SIGN F5 minor amendment 2026-07-10)

Phase 1 MUST define interim policy for `user=NULL` / `owner=NULL` rows per model. Options:
- **Deny-by-default** (safe fallback until backfill decided)
- **Migrate to `NOT NULL`** (surgical if row counts are low)
- **Explicit-scope** (some rows are legitimately unowned — e.g., system-generated — and get a named handler)

**Explicit non-policy:** silent treatment of NULL as "publicly visible" is a leakage bug and MUST NOT ship, even as an interim state.

---

## §8. Implementation Approach + Phases (draft; subject to Rigby SIGN)

### Phase 1 — Model Audit Ledger (target: 1 session)

- Materialize the 5-model audit ledger as a workspace deliverable under `fcd7e683` (RUR-C1 Tenant Boundary Lockdown workspace)
- Per-model: resolve `AgentExecution` canonical class; enumerate ownership FKs; count nullable-owner rows; catalogue all views/services/tasks/management-commands touching the model; classify each as scoped / unscoped / ambiguous
- Nullable-owner policy decision per model (purge / attribute-to-system / preserve-with-explicit-scope)
- Rigby SIGN on the ledger before Phase 2 opens

### Phase 2 — Ownership Predicate Module (target: 1 session)

- `core/security/object_authz.py` with 5 per-model predicate functions (one per model)
- Test suite: `tests/security/test_object_authz_predicates.py` proving each predicate correctly scopes to owner
- Rigby SIGN on the module before Phase 3 opens

### Phase 3 — Per-Model Enforcement Application (target: 1-2 sessions)

- Per-model application of predicates: DRF permission class OR view-level scoping (per §4 rubric outcome)
- Failure responses conform to safety contract (404 not 403 per SIGN Q6)
- Migration for user-NULL row policy if required by Phase 1 decision
- Endpoint-drift snapshot regen if new routes / permissions changed

### Phase 4 — Cross-Tenant Regression Harness (target: 1 session)

- `tests/security/test_cross_tenant_object_authz.py` parametrized over 5 models
- CI-blocking via `security-conformance.yml`
- I-0303 gains the async probes on top of this harness at its own Phase 3

### Phase 5 — I-0302 Arc Close

- All 5 models proven scoped via harness green
- No user-NULL row leakage per Phase 1 policy
- Follow-on `AgentExecution` duplicate-class consolidation recorded
- `I-030299_object_level_authorization_implementation_close.md` written + Chris-ratified

---

## §9. Open Scope Questions Requiring SIGN + Chris Ratification

1. Preliminary Bucket-A/B/C model-classification lean (§4 lean list) — Rigby's operational memory may flip AgentExecution to view-level scoping if the canonical class settles favorably.
2. `AgentExecution` triple-class situation — which is canonical, and is that decision within I-0302 scope or is it a separate orphan-cleanup follow-on?
3. Nullable-user-FK policy per model — purge vs system-attribute vs preserve. Chris D-verdict may be needed if volumes are large.
4. `core/security/object_authz.py` module location — is that the right home, or should it live under `core/models/` as a sibling to the models? My lean: `core/security/object_authz.py` to keep security substrate co-located.
5. Regression harness in `tests/security/` follows I-0301 precedent — confirm.
6. Do 404-not-403 responses on ownership failures conform to the safety contract enough, or should we add a new `object_authz_denied` reason_code to the enum? My lean: reuse `not_found` (per Rigby SIGN Q6 existence-oracle avoidance).
7. **[Rigby SIGN F6 add — governance-critical, requires Chris D-verdict BEFORE Phase 1 opens]** Tenant boundary definition: is the enforced boundary strictly **per-User** (`row.owner == request.user`) OR **per-Workspace/Tenant** (`row.workspace ∈ user.workspaces` for workspace-scoped resources)? Chris's D-verdict shapes the predicate signatures + the harness setup. **Do not open Phase 1 without this D-verdict** — reversing it later means rewriting predicates + harness.

---

## §10. Sibling Arc Cross-References + Dependency Ordering

I-0302 depends on:
- Ratified safety contract (I-0301 Phase 2 close) ✅ MET
- `core/security/error_envelope.py` substrate (I-0301 Phase 3 Stage 1) ✅ MET
- Phase 4 endpoint drift machinery (I-0301 Phase 4) ✅ MET — Phase 2 of this arc will regen the snapshot when endpoint permissions land

I-0302 unblocks (via shared harness):
- I-0303 async task-boundary enforcement uses the same predicates + extends the harness
- RUR-C1 parent close condition (needs I-0301 + I-0302 + I-0303 to all pass shared regression)

---

## §11. Rigby SIGN Cycle + Chris Ratification Contract

This scoping doc is `authority: arc-scoping` until Rigby signs + Chris ratifies. Ratification signals:

- Rigby scope SIGN with any material amendment applied (per S2742 §4 escalation rule)
- Chris D-verdict on the §9 open questions (at minimum the ones affecting scope shape)
- Frontmatter transitions to `status: active` + adds ratification metadata
- Phase 1 (Model Audit Ledger) opens

Post-ratification, this doc is the constitutional reference against which every Phase 1-5 sub-artifact is measured. Amendments discovered during Phase 1+ route through the parent CAMPAIGN §10 amendment discipline.

### §11.1 — Rigby scope SIGN outcome (2026-07-10)

**Verdict: SIGN-WITH-EDITS → SIGN-PASS post-edit.**

Six focus areas SIGN'd (F1..F6):
- **F1 material** — model audit corrections (§3.1 AgentTaskExecution assumption softened, §3.2 Initiative + Document ownership FK types locked): APPLIED
- **F2 minor** — §4 Meta.permissions rubric reframed to "one canonical predicate" contract: APPLIED
- **F3 material** — §5 harness distinguishes ownership vs nonexistent probes, list vs detail semantics, response-body safety-contract probes on 404 bodies: APPLIED
- **F4 minor** — §6 `object_authz.py` leaf-module constraint + predicate signatures + purity rule: APPLIED (§6.1, §6.2)
- **F5 minor** — §7 "do not creep" line + NULL-owned interim policy explicit non-policy: APPLIED (§7.4 bullet, §7.5)
- **F6 informational + governance-critical add** — §9 Q7 tenant-boundary definition (user vs workspace/tenant), pre-Phase-1 D-verdict gate: APPLIED (§9.7)

**Post-edit state:** SIGN-CLEAN pending Chris D-verdict on §9 open questions.

### §11.2 — Chris D-verdict target list (routed post-Rigby-SIGN)

Chris must D-verdict at least:
- **§9 Q7 tenant boundary** (per Rigby F6 pre-Phase-1 gate) — REQUIRED before Phase 1 opens
- §9 Q3 nullable-owner policy — if volumes are large enough to warrant D-verdict (Phase 1 audit will surface this)
- §9 Q6 reuse `not_found` vs add `object_authz_denied` reason_code
- §9 Q2 `AgentExecution` triple-class in-scope vs follow-on

Any Q9 question Chris defers back to Rigby / to Phase 1 is documented in the ratification record.

---

**End of I-0302 Scoping. Wave 1 authorization is permission to scope this arc, not permission to implement.**
