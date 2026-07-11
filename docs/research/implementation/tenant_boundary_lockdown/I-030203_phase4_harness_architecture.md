---
title: "I-0302 Phase 4 — Regression Harness Architecture"
status: active
authority: phase-4-architecture-signed
session_added: 2748
last_updated: 2026-07-10
arc_id: I-0302
arc_phase: Phase 4 (Regression Harness) — architecture ratified; implementation opening
parent_scoping_doc: docs/research/implementation/tenant_boundary_lockdown/I-0302_scoping.md
parent_scoping_ratification: docs/research/implementation/RATIFICATION_2026-07-10_i0302_scoping.md
phase_1_ledger: docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md
phase_2_design: docs/research/implementation/tenant_boundary_lockdown/I-030202_predicate_module_design.md
phase_2_ratification: docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase2_predicate_module.md
phase_3_wiring_handoff: docs/handoffs/SESSION_2747_I0302_PHASE_3_WIRING_COMPLETE.md
parent_campaign: RUR-C1 (Tenant Boundary Lockdown)
parent_program: RUR (Real User Readiness)
head_at_architecture: 62ee3911
rigby_architecture_sign_state: SIGN-PASS (F1..F4 + F3.1..F3.3 + bonus tightening)
chris_d_verdicts_resolved:
  - F1 runner shape (hybrid matrix + endpoint sentinels) — implicit agree via "agree all"
  - F2 fixture strategy (golden + layered per-test builders) — implicit agree via "agree all"
  - F3 assertion contract ((a)-(e) + UPDATE/PATCH + CREATE parent-binding + ops carve-out policy) — narrow ratification on ops carve-out
  - F3.1 registry mechanism = B (AST scan) — agree
  - F3.2 composition = B (both decorators explicit) — agree
  - F3.3 fail-safe = A (code-only Phase 4) — agree
  - Ledger amendment timing = codify at Phase 4 open (§11 of I-030201) — agree
  - Bonus tightening = single canonical import path enforced by AST — ship
session_pin: pa-59d27abadeed4411 (title `ios-arc-open-I0302-P4`, minted 2026-07-10 S2748 open after retiring `pa-cd35bde16f974843`)
constraint: Phase 4 close awaits shipped harness + Rigby SIGN-PASS + Chris ratification
---

# I-0302 Phase 4 — Regression Harness Architecture

Design contract for the shared cross-tenant regression substrate that satisfies **RUR-C1 parent invariant** for I-0302. Also serves as the reusable substrate that I-0303 (async-boundary enforcement) and I-0301 (already CLOSED) will co-verify against once the parent RUR-C1 shared cross-tenant regression is composed.

**Ratified inputs:**
- Phase 1 ledger §6: Q7 hybrid boundary — 5 canonical models classified per-user vs workspace-scoped
- Phase 1 ledger §11: `@ops_aggregate_allowed` substrate (this arc's canonical carve-out mechanism)
- Phase 2 predicate module (`core/security/object_authz.py`): 11 predicate functions, F-2 hardened
- Phase 3 wiring: 144 enforcement sites across 34+ view files (10 PRs #3100-#3109 merged at HEAD `62ee3911`)
- Session 642 null-user superuser carve-out (AgentExecution-only exception)
- 162/162 security suite baseline (i.e., Phase 3 test discipline extends into Phase 4)

---

## §1. Harness Runner Shape — F1 SIGN

**Verdict: hybrid — matrix-first + targeted endpoint sentinels.** Rejects the full 1864-URL sweep as combinatorially unworkable and flakiness-prone.

### §1.1 Matrix runner (primary)

Iterates `per_model × per_primitive`:

- **Models (5):** `Deliverable`, `Initiative`, `ChatConversation`, `AgentExecution`, `Document`
- **Primitives (7):** LIST, GET, UPDATE, DELETE, EXISTS, aggregate, CREATE-parent-binding

Each cell of the 5×7 matrix runs the same predicate-boundary assertion contract (§3). The matrix is model-invariant and predicate-invariant — this is the ONLY layer that produces regression coverage of the parent RUR-C1 invariant.

Location: `tests/security/test_i0302_p4_matrix_harness.py` (single file — the matrix is small enough that spreading it hurts readability).

### §1.2 Endpoint sentinels (secondary)

10-30 hand-picked view-layer risk endpoints per app area. Categories of "sentinel candidate":

- Custom actions (non-standard REST verbs, `POST /obj/{id}/action/`)
- Nested routes (`/workspace/{ws}/deliverable/{id}/...`)
- Bulk endpoints (batch create/delete)
- `/me/` endpoints
- Export endpoints (CSV/JSON dumps)

Sentinels are smoke tests: hit each URL as `user_a`, `user_b`, `anonymous`, `superuser`. Assertion is minimal — was the boundary held (own = 200, other = 404/403, anon = 401)? — not full semantic behavior.

Location: `tests/security/test_i0302_p4_endpoint_sentinels.py`.

**Endpoint list source:** Rigby to enumerate from Phase 3 view files touched in PRs #3100-#3109. Rigby SIGN target on the specific sentinel list before Task 8 lands.

### §1.3 What is deliberately NOT built

- No full 1864-URL sweep. Combinatorial 1864 × 4 roles × 7 primitives = ~52k assertions. Sentinels + matrix already cover the invariant; the sweep would trade rigor for maintenance debt and flakiness.
- No E2E browser harness. This is a backend predicate-boundary regression, not a UI conformance suite.

---

## §2. Fixture Strategy — F2 SIGN

**Verdict: layered — golden shared "5-model tenant boundary" fixture as baseline + per-test lightweight builders for edge cases.**

### §2.1 Golden fixture

Single pytest module-scoped fixture in `tests/security/conftest.py` (or `tests/security/fixtures/tenant_boundary.py`) that produces:

- `user_a`, `user_b` — two regular users
- `superuser` — one superuser (Session 642 null-user probing lane)
- `workspace_a` — owned by `user_a`
- `workspace_b` — owned by `user_b`
- Per model, N=3 rows owned by `user_a` and N=3 rows owned by `user_b`
  - `Deliverable` × 6 (3 in workspace_a, 3 in workspace_b)
  - `Initiative` × 6 (3 per user)
  - `ChatConversation` × 6 (3 in workspace_a, 3 in workspace_b)
  - `AgentExecution` × 6 (3 per user; 1 additional null-user row for superuser carve-out probing)
  - `Document` × 6 (3 per user)

Rows are **immutable** — tests that mutate must use per-test builders (§2.2). Golden fixture rows persist for LIST/GET/EXISTS/aggregate assertions across the matrix.

### §2.2 Per-test builders

For UPDATE/DELETE/CREATE-parent-binding assertions (which mutate state), each test builds its own row(s) on top of the golden users/workspaces. Never mutates golden rows.

Location: helpers in the same `tests/security/fixtures/` module.

### §2.3 Cost/coupling mitigation

- Golden fixture runs per test-module or per-session (pytest scope choice — start with module, escalate to session if timing shows cost). Django rollback per-test isolates mutations.
- CI collection of golden fixture measures baseline time in `security-conformance.yml` job output; if Phase 4 pushes baseline over 60s, split into two files.

---

## §3. Assertion Contract — F3 SIGN

**Verdict: adopt (a)-(e) universal baseline + add UPDATE/PATCH + CREATE parent-binding + define ops carve-out policy via `@ops_aggregate_allowed`.**

### §3.1 Universal baseline (5 primitives)

For every user-facing endpoint touching any of the 5 canonical models:

| ID | Primitive | Contract |
|---|---|---|
| (a) | **LIST** | Returns only rows the caller owns (per Phase 2 predicate). |
| (b) | **GET** | Other-user row → **404 (not 403)** to avoid existence leak. |
| (c) | **DELETE** | Other-user row → 404 preferred; 403 acceptable only if product requires. |
| (d) | **EXISTS** | Returns `False` for other-user id. |
| (e) | **AGGREGATE** | Excludes other-user rows (unless `@ops_aggregate_allowed` carve-out applies — §3.4). |

### §3.2 UPDATE / PATCH (added per Rigby SIGN F3)

- Other-user row UPDATE → 404 (matches GET posture; do not leak existence).
- Test this primitive explicitly per model in the matrix.

### §3.3 CREATE parent-binding (added per Rigby SIGN F3)

- `user_a` MUST NOT be able to CREATE a row bound to `workspace_b` (parent owned by `user_b`).
- Test this per model that has a workspace/parent FK (`Deliverable`, `ChatConversation`).
- For per-user models (`Initiative`, `AgentExecution`, `Document`) test that `user_a` cannot spoof `owner=user_b` at create-time (POST body owner-injection attack).

### §3.4 Ops carve-out via `@ops_aggregate_allowed`

Cross-tenant aggregate is **forbidden** for regular user role in all cases. For superuser role:

- **Endpoint NOT decorated with `@ops_aggregate_allowed`**: aggregate MUST still be tenant-scoped. Superuser bypass is disallowed unless the endpoint declares intent.
- **Endpoint decorated with `@ops_aggregate_allowed`** AND `@superuser_required` (per I-030201 §11.4): cross-tenant aggregate is permitted for superuser. Matrix's aggregate assertion skips this endpoint with a rationale comment pointing at I-030201 §11.X.

The AST scan (Task 7) enforces the substrate; the matrix runner defers to AST scan output for skip decisions.

### §3.5 Anonymous baseline

For every primitive, anonymous → 401 (not 403, not 200 with empty list). Enforced by F-2 hardening in the predicate module — the harness verifies the boundary held at the request layer.

**AllowAny + predicate-only exception (per Rigby Sub-phase 1 Q4 SIGN 2026-07-10):** `/api/initiatives/` and `/api/deliverables/` are AllowAny with predicate-only boundary — anon → 200 with empty list, NOT 401/403. F-2 hardening in `scope_queryset_*` returns `.none()` for anonymous callers, keeping the payload empty. The harness asserts this "observed surface" — not a policy claim that these endpoints *should* be AllowAny; if a future arc hardens them to `IsAuthenticated`, the assertion flips.

### §3.6 Superuser semantics — permission vs. tenancy (per Rigby Sub-phase 1 Q4 SIGN 2026-07-10)

**Superuser is a permission bypass, not a tenancy bypass, unless explicitly declared via `@ops_aggregate_allowed` (§5.1).**

Concretely:
- `user_can_access_workspace(superuser, workspace_id)` returns True (documented single-object bypass).
- `scope_queryset_deliverable(superuser, qs)` filters by `workspace_id__in=<workspaces superuser OWNS>`. It does NOT ambient-bypass into other users' workspaces. Superuser with zero owned workspaces sees zero deliverables — this is the boundary-correct behavior, not a regression.
- The AGGREGATE primitive (§3.1(e)) inherits the same posture: superuser aggregate is tenant-scoped unless the specific endpoint is decorated with `@ops_aggregate_allowed` + `@superuser_required` (§5.1) AND has a corresponding §11.X F-block ledger amendment justifying the carve-out.

The harness assertion contract MUST NOT interpret "superuser sees fewer rows than user_a" as a regression. That is the invariant holding.

### §3.7 Session 642 null-user carve-out — AgentExecution only (per Rigby Sub-phase 1 Q4 SIGN 2026-07-10)

**`AgentExecution.user = None` rows (system-context Celery executions) are visible to superuser ONLY.** Regular users MUST NEVER see them.

This is a documented legacy carve-out enforced at the predicate layer (`scope_queryset_agent_execution`) as a superuser union with own-owned rows. The harness must:
- Include one null-user row in the golden fixture (via `tb_execution_null_user`) so the invariant is exercised.
- Assert that regular user aggregate/list/get does NOT return the null-user row.
- Assert that superuser aggregate/list DOES include the null-user row.

The carve-out is NOT declared via `@ops_aggregate_allowed` because it predates the substrate. If a similar future carve-out emerges for any other model, use `@ops_aggregate_allowed` with §11.X amendment — do NOT extend the predicate module with implicit unions.

### §3.8 Canonical JSON paths for aggregate endpoints (per Rigby Sub-phase 1 Q4 SIGN 2026-07-10)

Aggregate endpoints ship diverse response shapes. The harness codifies the assertion path per endpoint as a shape-stable contract:

| Endpoint | Canonical assertion path | Model |
|---|---|---|
| `/api/analytics/overview/` | `body["total_executions"]` | AgentExecution |
| `/api/v1/rag/stats/` | `body["embeddings_stats"]["total_documents"]` | Document |
| `/api/deliverables/stats/` | TBD (Sub-phase 2) | Deliverable |

If a future PR reshapes a response body, the harness assertion is the canonical test that catches the drift — reviewers should update this table AND the harness helper in the same PR to keep the contract explicit.

---

## §4. Deferred-Surface Handling — F4 SIGN

**Verdict: hybrid — explicit skip + structured coverage-gap report + cheap posture probe where feasible.**

### §4.1 Skip surfaces

Per Phase 3 ledger amendments, three surface classes are explicitly deferred:

- **§5.3.b (C2, ~126 sites)** — ChatConversation Sub-phase C2 sites deferred per D-verdict at S2747
- **§5.1.a (D non-view sites)** — Deliverable non-view management commands / service-layer sites
- **§5.5.a (Document WebSocket)** — Document real-time channels deferred pending F-A wiring in I-0303

For each surface: matrix skips with `pytest.skip(reason=f"See I-030201 §5.X.a — deferred sub-phase")` OR test decorated `@pytest.mark.skip(reason=...)`.

### §4.2 Coverage-gap report

Skipped tests emit structured rows into a JSON report at `test_reports/i0302_p4_coverage_gaps.json`:

```json
{
  "surface_id": "5.3.b",
  "model": "ChatConversation",
  "sites_deferred": 126,
  "ledger_ref": "docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md#§5.3.b",
  "expected_close": "post-I-0303",
  "posture_probed": false
}
```

Report is a Phase 4 artifact — attached to the Phase 4 close ratification for audit visibility. Skips-without-reporting = invisible debt.

### §4.3 Posture probes (cheap gate)

Where feasible without semantic overhead: emit HEAD/OPTIONS or minimal auth probe against the deferred surface asserting current 401/403 posture. Sets `posture_probed: true` in the coverage-gap row. Do NOT block harness on flaky WebSocket probing — WebSocket surface is probe-exempt.

---

## §5. Substrate References

### §5.1 `@ops_aggregate_allowed` decorator (I-030201 §11)

Codified 2026-07-10 at Phase 4 open. Contract summary:
- Import from `core.security.decorators` ONLY
- Pair with `@superuser_required`
- Per-use §11.X F-block ledger amendment required
- AST harness enforces all three constraints at test-collection

### §5.2 `@superuser_required` decorator (S2747 PR #3104)

Substrate from Phase 3 Sub-phase B2b. Used as the outer/auth gate on any endpoint that adds `@ops_aggregate_allowed`.

### §5.3 Predicate module `core/security/object_authz.py`

11 predicate functions, F-2 anonymous-user hardening. Phase 4 matrix asserts the predicate boundary at the request layer (verifying view wiring calls the predicate correctly), not the predicate function's own logic (which Phase 2's `test_object_authz_predicates.py` already covers with 60 unit tests).

### §5.4 `security-conformance.yml` CI workflow

Existing from I-0301. Phase 4 extends the workflow to run the matrix + sentinel + coverage-gap-report tests on every relevant model/view/predicate file change. Extension lands with the harness in the same PR series.

---

## §6. Implementation Order

Sequential per §7 blockedBy dependency chain. Each step has its own PR (or bounded PR series) with Rigby SIGN gate.

1. **§11 ledger amendment** (I-030201) — DONE Sub-phase 0 (PR #3111)
2. **`@ops_aggregate_allowed` decorator + smoke test** — DONE Sub-phase 0 (PR #3111)
3. **This architecture doc** — DONE Sub-phase 0; extended Sub-phase 1 §3.5-§3.8 per Rigby Q4 SIGN
4. **Golden fixture** — DONE Sub-phase 1 (PR #3112)
5. **Matrix runner** (initial 5 cells) — DONE Sub-phase 1 (PR #3112)
6. **§5.1.b hotfix** — DONE (PR #3113) — 3-site scope: `delete_deliverable`, `link_deliverable_workspace`, `record_deliverable_event`
7. **Fixture cross-membership extension (F1A)** — DONE Sub-phase 2 (this PR) — cross-tenant Deliverable row (user=user_b + workspace=workspace_a) exposes predicate-scoping mistakes
8. **Matrix expansion — hybrid B+C** — DONE Sub-phase 2 (this PR) — Deliverable save/unsave/templateize/GET-item + ChatConversation LIST; Initiative + ChatConversation intentional-immutability per Chris D-verdict at S2748 (no UPDATE/DELETE endpoints exist to test)
9. **§5.1.b extension** — DONE Sub-phase 2 (this PR) — 2 more `except Exception`-swallows-Http404 sites (unsave + templateize) surfaced by harness; fixed inline as trivial extension of §5.1.b guardrail
10. **AST scan module** — Sub-phase 3; independent of matrix, blocks endpoint sentinels (sentinel skip decisions rely on AST output)
11. **Endpoint sentinels** — Sub-phase 3; depends on fixture + AST scan
12. **Coverage-gap report + posture probes** — DONE Sub-phase 3 (S2750) — `tests/security/test_i0302_p4_coverage_gap_report.py` emits `test_reports/i0302_p4_coverage_gaps.json` covering §5.3.b (ChatConversation ~126 sites, live enum 114/36 vs ledger 126/43), §5.1.a (Deliverable 4 hand-picked sites), §5.5.a (Document WebSocket 3 sites). All rows ship `posture_probed: false` — current deferred surfaces are non-HTTP-addressable (services/tasks/agents/Employee-OS) or WebSocket (probe-exempt per §4.3). Probe-machinery structure supports future HTTP-addressable rows without redesign.
13. **Intentional-immutability contract for Initiative + ChatConversation** — Sub-phase 3 — assert unsafe methods (PUT/PATCH/DELETE) return 405/404 as absence-contract per Chris D-verdict at S2748
14. **VIP-scope carve-out coverage on `get_deliverable`** — Sub-phase 3 — extend fixture with VIP membership row; test the VIP-workspace read path currently deferred in Sub-phase 2 GET-item cell
15. **Rigby SIGN on shipped harness + Chris ratification** — Phase 4 close

### §6.a Sub-phase 3 research inputs (per Rigby SIGN F2 2026-07-10)

Before Sub-phase 3 opens, run these research passes (bounded, docs-only outcomes):

- **AgentExecution mutation semantics** — confirm no user-facing UPDATE/DELETE (likely no per S2748 endpoint discovery for Initiative + ChatConversation); if any exist, add absence-contract cells
- **Document mutation semantics** — user vs owner field question (`views_rag_embeddings.py:470/836` use `Document.objects.get(id=..., user=user)` on a model whose FK is named `owner`; investigate whether this is legacy dual-field, misspelling, or a runtime bug)
- **CREATE-parent-binding endpoint map** — inventory which endpoints create rows across the 5 canonical models + identify the parent-binding field per endpoint
- **AGGREGATE endpoint inventory** — enumerate true aggregates vs stats-with-nested-shape endpoints for shape-stable §3.8 table
- **Non-canonical model follow-on** — `LegalDocument`, `LitigationDocument`, `ReviewDocument` unscoped `.objects.get(id=...)` patterns from §5.1.b sweep; scope decision on whether these fall under I-0302 or a separate arc

---

## §7. Phase 4 Close Criteria

Phase 4 closes when ALL of the following hold:

1. Matrix runner (§1.1) exists and passes for all 5 × 7 = 35 cells (minus explicit deferred skips per §4). **Extended at S2749 close** with intentional-immutability contract cells for Initiative + ChatConversation — 48 cells (2 models × 2 endpoints [LIST + DETAIL] × 3 methods [PUT/PATCH/DELETE] × 4 roles) asserting `status in {401, 403, 404, 405}` per S2748 Chris D-verdict "treat as intentional immutability."
2. Endpoint sentinels (§1.2) exist for at least 10 hand-picked risk endpoints and pass across 4 roles. **DONE (S2749):** 28 cockpit ops sentinels shipped in enforcing mode via PRs #3120 → #3121 → #3122. Batch-fix added `@superuser_required` to 23 sites in `views_diagnostics.py`. Report at `test_reports/i0302_p4_endpoint_sentinels.json`.
3. AST scan module (§5.1) is wired into the harness; harness fails collection if `@ops_aggregate_allowed` contract is violated. Zero current uses at Phase 4 close is acceptable (baseline established). **DONE (S2749):** §14 codification substrate for Http404-swallow anti-pattern extended the AST scan approach via PRs #3116 → #3117 → #3118. Batch-fix patched 9 sites across 3 view files. Report at `test_reports/i0302_p4_ast_conformance.json`. Related spec: `I-030204_ast_conformance_rule_spec.md`.
4. Deferred-surface coverage-gap report (§4.2) emits structured JSON on test run; skipped sites are enumerated with ledger refs. **DONE (S2750):** `tests/security/test_i0302_p4_coverage_gap_report.py` emits `test_reports/i0302_p4_coverage_gaps.json`. 4 tests: emit + shape + ledger-refs-resolve + specific-sites-files-exist. Surface classes covered: §5.3.b + §5.1.a + §5.5.a.
5. `security-conformance.yml` runs the Phase 4 harness on every PR touching the relevant surface.
6. Rigby SIGN-PASS on shipped harness.
7. Chris D-verdict ratifying Phase 4 close.
8. Phase 4 close doc appended (either amend this doc §8 "Close statement" OR create `I-030204_phase4_close.md`).

---

## §8. Chain of Custody

| Session | Event | Reference |
|---|---|---|
| S2748 | Phase 4 opened; F1-F4 SIGN | This doc §1-§4 |
| S2748 | F3.1-F3.3 sub-detail SIGN + bonus tightening | I-030201 §11 |
| S2748 | Chris D-verdict "agree all + ship bonus tightening" | This doc frontmatter + I-030201 §11.6 |
| S2748 | `@ops_aggregate_allowed` decorator landed + smoke test | `core/security/decorators.py` + `tests/security/test_i0302_p4_ops_aggregate_decorator.py` |
| S2748+ | Harness implementation | Task list 5-9 |
| S2749 | §14 AST codification substrate (report-only → batch-fix → enforce) | PRs #3116 → #3117 → #3118 |
| S2749 | Endpoint sentinels substrate (report-only → batch-fix → enforce) | PRs #3120 → #3121 → #3122 |
| S2749 | Intentional-immutability contract cells (Initiative + ChatConversation) | `tests/security/test_i0302_p4_matrix_harness.py` §7 |
| S2749 | Rigby gpt-5.2 stall post-mortem fix (provider fallback + response body capture) | PR #3119 |
| S2750 | Deferred-surface coverage-gap report | `tests/security/test_i0302_p4_coverage_gap_report.py` + `test_reports/i0302_p4_coverage_gaps.json` |
| TBD | Rigby SIGN-PASS on shipped harness | Task 10 |
| TBD | Chris ratification + Phase 4 close | Task 10; close statement appended here or in `I-030204_phase4_close.md` |

---

**End of I-0302 Phase 4 Architecture doc. Rigby SIGN + Chris D-verdicts complete for architecture; implementation now proceeds per §6.**
