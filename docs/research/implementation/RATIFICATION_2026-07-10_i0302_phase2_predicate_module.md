---
title: "I-0302 Phase 2 Predicate Module Ratification Record (2026-07-10)"
status: active
authority: ratification-record
session_added: 2742
ratification_date: 2026-07-10
ratifier: chris
routing: rigby-pa-chat SIGN (design + implementation) + Chris direct in-session ratification
program_id: RUR
parent_arc: I-0302
parent_arc_phase: Phase 2 (Predicate Module)
parent_arc_workspace: fcd7e683-3bfe-4d35-9704-0e54dd587ea1
parent_arc_workspace_name: "RUR-C1 Tenant Boundary Lockdown"
parent_campaign: RUR-C1 (Tenant Boundary Lockdown)
parent_campaign_workspace: 638e9e90-47b4-4bd4-a872-bf16181cf3b5
parent_campaign_workspace_name: "Real User Readiness Campaign"
parent_program_doc: docs/research/implementation/real_user_readiness/CAMPAIGN.md
parent_program_ratification: docs/research/implementation/RATIFICATION_2026-07-10_real_user_readiness.md
sibling_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-10_i0301_arc_close.md
  - docs/research/implementation/RATIFICATION_2026-07-10_i0302_scoping.md
  - docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase1_ledger.md
ratified_documents:
  - docs/research/implementation/tenant_boundary_lockdown/I-030202_predicate_module_design.md
  - core/security/object_authz.py
  - core/security/__init__.py (extended re-exports)
  - tests/security/test_object_authz_predicates.py (60 tests)
  - .github/workflows/security-conformance.yml (extended triggers + workflow_dispatch)
ratified_head: 1790d672
merged_pr: https://github.com/clwest/donkey-betz-platform/pull/3097
sign_sessions:
  - S2742 — Rigby design SIGN initial: SIGN-WITH-EDITS (F1..F6 mixed severity); all edits applied
  - S2742 — Rigby design SIGN post-edit: SIGN-PASS
  - S2742 — Rigby implementation SIGN initial: SIGN-WITH-EDITS (F3.2 AgentExecution superuser exactness test add); applied
  - S2742 — Rigby implementation SIGN post-edit: SIGN-PASS
supersedes: none (first I-0302 Phase 2 ratification)
superseded_by: (open; not expected — Phase 2 ratifications are frozen historical records)
frozen: true
arc_state:
  phase_1_model_audit_ledger: closed
  phase_2_predicate_module: closed (this record)
  phase_3_enforcement_application: authorized_to_open
  phase_4_regression_harness: pending
  phase_5_arc_close: pending
  arc_status: OPEN (Phase 2 CLOSED; Phase 3 authorized to open)
test_results:
  local_test_count: 60
  local_test_pass_rate: "60/60"
  local_test_runtime_seconds: 196
parent_campaign_close_gate:
  - RUR-C1 parent close requires I-0301 + I-0302 + I-0303 all pass shared cross-tenant regression suite per Chris Q2 D-verdict at parent CAMPAIGN ratification
  - I-0301 CLOSED 2026-07-10; I-0302 Phase 2 CLOSED (this record); I-0303 NOT YET OPENED; RUR-C1 remains OPEN
---

# I-0302 Phase 2 Predicate Module Ratification Record

This file is the **frozen** canonical record of Chris's ratification of the I-0302 Phase 2 Predicate Module on 2026-07-10. It captures the ratified design brief, the shipped module + tests + CI extension, the Rigby double-SIGN cycle (design SIGN → implementation SIGN), Chris's ratification, and Phase 3 opening authorization. It is append-only history; do NOT edit after commit.

---

## §1. Context

- **Ratification date:** 2026-07-10 (America/Denver operator timezone)
- **Arc phase:** I-0302 Phase 2 (Predicate Module)
- **Merged PR:** https://github.com/clwest/donkey-betz-platform/pull/3097
- **Merge SHA:** `1790d672` (squash-merged to main via `--admin` due to CI billing block on prior PRs)
- **Ratifier:** Chris ("ratify Phase 2")
- **Sibling status:** I-0301 CLOSED 2026-07-10; I-0302 scoping ratified 2026-07-10; I-0302 Phase 1 ratified 2026-07-10; Phase 2 ratified via this record; I-0303 NOT YET OPENED.

---

## §2. Ratified Deliverables

### §2.1 `core/security/object_authz.py` — leaf predicate module

11 public functions (per scoping §6.2 signature contract):

**Canonical primitive:**
- `user_can_access_workspace(user, workspace_id) -> bool` — single-owner semantics + superuser bypass. Under single-user pre-prod, access = `ProjectWorkspace.user == user`. Multi-tenant Phase 0 expands to membership tables.

**5 per-model object predicates:**
- `can_read_deliverable(user, deliverable) -> bool` — workspace-scoped + staff carve-out for null-workspace cleanup path
- `can_read_chat_conversation(user, conv) -> bool` — workspace-scoped + transitional user-fallback (workspace wins invariant)
- `can_read_initiative(user, initiative) -> bool` — per-user; null-owner deny-by-default (Phase 3 migration eliminates)
- `can_read_agent_execution(user, execution) -> bool` — per-user + **superuser-only** carve-out for null-user Celery runs (F4: not `is_staff`, avoids overreach when staff role expands)
- `can_read_document(user, doc) -> bool` — per-user; Document.owner NOT NULL so no fallback

**5 per-model queryset filters:**
- `scope_queryset_deliverable(user, qs)` — non-staff: own-workspace rows; staff: own + null-workspace rows
- `scope_queryset_chat_conversation(user, qs)` — union of workspace-scoped + user-direct
- `scope_queryset_initiative(user, qs)` — `owner=user` filter
- `scope_queryset_agent_execution(user, qs)` — non-superuser: `user=user`; superuser: **exactly** `Q(user=user) | Q(user__isnull=True)` (never broadened)
- `scope_queryset_document(user, qs)` — `owner=user` filter

### §2.2 `core/security/__init__.py` — extended re-exports

11 new symbols added to the public `core.security` API surface alongside the existing I-0301 safety-contract exports.

### §2.3 `tests/security/test_object_authz_predicates.py` — 60 tests

Coverage per predicate:
- Owner+access path (allow)
- Wrong-owner+deny path (deny)
- Null-owner rule per model
- Unauthenticated user (user is None) → False / `.none()`
- Null obj → False
- Empty queryset invariant
- Mixed-ownership queryset returns only user's rows
- **Idempotence / monotonicity:** `scope(scope(qs)) == scope(qs)`

Model-specific invariants:
- **ChatConversation workspace-wins** — 2-direction tests (allow when workspace-owner requests despite conv.user disagreement; deny when conv.user matches but workspace-owner differs)
- **AgentExecution superuser exactness** — dedicated `test_superuser_exactness_own_plus_null_only` verifies superuser scope = `Q(user=user) | Q(user__isnull=True)` exactly, never broadening to foreign-user rows (F4 invariant)
- **Deliverable staff carve-out** — null-workspace non-staff denied; null-workspace staff allowed for cleanup

**Local test run:** 60/60 pass in ~196s.

### §2.4 `.github/workflows/security-conformance.yml` — CI extended

6 new trigger paths (5 canonical model files + `core/models_skin_layer.py` for ProjectWorkspace) + `workflow_dispatch` enabled for manual runs during refactors. Existing `tests/security/` glob trigger picks up the new test file automatically.

### §2.5 `docs/research/implementation/tenant_boundary_lockdown/I-030202_predicate_module_design.md` — Phase 2 design brief

Design contract ratified after Rigby SIGN-PASS (design) + Rigby SIGN-PASS (implementation). Frontmatter records SIGN state + implementation files touched + circular-import override documentation.

---

## §3. Rigby Double-SIGN Cycle

### §3.1 Design SIGN (initial: SIGN-WITH-EDITS → post-edit: SIGN-PASS)

Routed via `tools/pa_local.sh` on conversation `pa-73f0e2e210574d6d` with 6-area SIGN prompt on module structure, workspace primitive, per-model predicates, staff carve-out shape, test coverage, CI wiring.

| Finding | Severity | Disposition |
|---|---|---|
| **F1** — hybrid import strategy (top-level for safe, local for cycle-avoidance) + explicit leaf-module comment | minor | APPLIED (design); **overridden at implementation** — see §4 |
| **F2** — superuser override on `user_can_access_workspace`; skip `is_active` (verified ProjectWorkspace has no such field) | minor | APPLIED |
| **F3** — Deliverable staff carve-out for null-workspace; ChatConversation dual-fallback transitional + workspace-wins invariant | minor | APPLIED |
| **F4** — AgentExecution carve-out changed from `is_staff` to `is_superuser` (avoids overreach when staff role expands to non-admin operators) | minor | APPLIED |
| **F5** — idempotence + mixed-null + ChatConversation disagreement + user_c superuser-invariant tests | minor | APPLIED |
| **F6** — CI triggers expanded to `core/security/**` + all relevant model modules + `workflow_dispatch` enabled | informational | APPLIED |

### §3.2 Implementation SIGN (initial: SIGN-WITH-EDITS → post-edit: SIGN-PASS)

| Finding | Severity | Disposition |
|---|---|---|
| **F1 (impl)** — local-import perf guidance ("prefer queryset scoping over Python loops") | minor | DEFERRED to Phase 3 per Rigby concurrence (add comment adjacent to Phase 3 caller wiring, not here) |
| **F2 (impl)** — ChatConversation workspace-wins + AgentExecution superuser exactness code correctness | minor | VERIFIED — matches design |
| **F3 (impl)** — explicit `test_superuser_exactness_own_plus_null_only` for AgentExecution 3-row invariant | minor | APPLIED |
| **F4 (impl)** — do NOT trigger CI on design-doc edits (avoid noise) | informational | APPLIED (design-doc excluded from CI triggers) |

Both SIGN cycles concluded SIGN-PASS.

---

## §4. Circular-Import Override (F1 exception)

Rigby SIGN F1 hybrid-import guidance was overridden for THIS module:
- `core/settings.py` imports from `core.security`
- `core.security.__init__.py` re-exports from `object_authz.py`
- `models_skin_layer.py` calls `get_user_model()` at module load time
- Chain triggers `AppRegistryNotReady` at Django startup

**Fix:** all model imports moved back inside function bodies with explicit `# local import: avoid settings cycle` comments. Documented in module-head docstring as an intentional exception. Rigby explicitly ACK'd this override at implementation SIGN.

**Impact:** minor per-call overhead of local imports; negligible in current usage. Guidance to "prefer queryset scoping over Python per-row loops" deferred to Phase 3 when callers get wired.

---

## §5. Test Results

- **Local test count:** 60 (up from ~50 target due to F5 amendment adding idempotence + F3.2 impl amendment adding superuser exactness)
- **Local test pass rate:** 60/60
- **Local runtime:** ~196s (Django app boot + Postgres DB creation dominates; individual test time is sub-second)
- **CI status on merged PR #3097:** admin-merged bypassing CI billing block; workflow will run on next PR that touches trigger paths

---

## §6. Downstream Unlocks

Ratification of Phase 2 authorizes:

- **Phase 3 (Per-Model Enforcement Application)** to open under I-0302.
- Phase 3 concrete moves:
  1. **Initiative Option C pre-flight migration:** backfill all 62 null-owner rows to canonical primary user (first superuser); migrate `owner` to NOT NULL. Uses `User.objects.filter(is_superuser=True).order_by('pk').first()`, NOT hardcoded string (per Chris D-verdict guardrail at Phase 1 close).
  2. **Deliverable Option-C-analog migration** (per §7 informational): backfill 45 null-user rows (if migration deemed applicable under single-user pre-prod) + workspace-null handling per staff carve-out.
  3. Apply predicates to the ~50 caller hotspots identified in Phase 1 §5 (~20 Initiative DRF callers, 3 AgentExecution dashboard view files, ChatConversation views, Deliverable detail lookups, Document consumer paths).
  4. Endpoint drift snapshot regen (per I-0301 Phase 4 mechanism) if any new routes / permissions landed.
- Phase 3 ships one or more surgical PRs per model or view-cluster. Each gets Rigby SIGN before merge.

Ratification does NOT authorize:
- Any Phase 4 (regression harness) work without Phase 3 close.
- Any Phase 5 (arc close) work without full arc completion.
- Any I-0303 (async boundary) work — I-0303 remains OPEN authorization pending until Chris signals.
- Any modification to the ratified failure-data safety contract, I-0302 scoping, or Phase 1 ledger.

---

## §7. Constitutional Anchors

This ratification is anchored under:

- **Engineering Playbook v0.4.1** (ratified S2742) — Phase 2 design-SIGN + implementation-SIGN cadence per §4.3.
- **Real User Readiness CAMPAIGN** (parent program, ratified S2742) — RUR-C1 close-gate invariant per §4.
- **I-0302 Scoping** (ratified S2742) — Chris Q7 hybrid boundary D-verdict + Rigby scope SIGN.
- **I-0302 Phase 1 Ledger** (ratified S2742) — Chris Option C D-verdict on Initiative null-owner policy + single-user pre-prod operating context.
- **I-0301 Arc Close** (ratified S2742) — sibling arc precedent for Phase-by-Phase ratification cadence.
- **Failure-Data Safety Contract** (ratified S2742 as I-0301 Phase 2 constitutional artifact) — Phase 4 regression harness safety-contract probes will reuse.

---

## §8. Handoff to Phase 3

Phase 3 (Per-Model Enforcement Application) is authorized to open. Concrete Phase 3 opening moves per §6:

1. Phase 3 pre-flight — Initiative null-owner backfill migration (Chris Option C) + NOT NULL flip.
2. Phase 3 pre-flight — Deliverable null-user backfill (if applicable) + null-workspace staff-only visibility already covered by predicate.
3. Rigby SIGN on Phase 3 pre-flight migration plan before code lands.
4. Apply predicates to caller hotspots per Phase 1 §5 regression-risk rank (highest first): Initiative → AgentExecution → ChatConversation → Deliverable → Document.
5. Regenerate endpoint snapshot per I-0301 Phase 4 mechanism if new routes/permissions changed.
6. Rigby SIGN on Phase 3 implementation before ratification.

Phase 3 may split into multiple sub-phases (per-model or per-view-cluster) at Rigby's SIGN recommendation.

---

**End of I-0302 Phase 2 Predicate Module Ratification Record. Frozen 2026-07-10.**
