# Session 2748 — I-0302 Phase 4 Sub-phases 0/1/2 COMPLETE + §5.1.b Hotfix (5 sites)

**Session:** 2748
**Date:** 2026-07-10
**Session type:** Engineering-execution arc — I-0302 Phase 4 Sub-phases 0/1/2 harness build + §5.1.b security hotfix
**System Owner directive at open:** Confirm Phase 4 primary + open with Sub-phase 0 opening move via Rigby SIGN F1-F4
**System Owner directive at close:** Merge PR #3114, route §14 codification design SIGN through Rigby, write handoff
**PA conversation pin (arc):** `pa-59d27abadeed4411` (S2748 pin — minted at session open after retiring `pa-cd35bde16f974843`; label `ios-arc-open-I0302-P4`; still active at close for Sub-phase 3 continuation)
**Preceding arc:** SESSION_2747 handoff (I-0302 Phase 3 wiring COMPLETE — 10 PRs, 144 sites, 162/162 pass)

---

## §1 Delivery ledger

**4 PRs merged to main.** Session shipped one sub-phase per D-verdict cycle, with Rigby SIGN gates and Chris ratification at every step. Two of the four PRs were expanded post-open in response to harness-surfaced security findings, with Chris D-verdict authorization each time.

| # | PR | Sub-phase / Class | HEAD after merge |
|---|---|---|---|
| 1 | [#3111](https://github.com/clwest/donkey-betz-platform/pull/3111) | Sub-phase 0 — `@ops_aggregate_allowed` decorator + I-030201 §11 ledger amendment + I-030203 harness architecture doc + 8 smoke tests | `0edc85cc` |
| 2 | [#3112](https://github.com/clwest/donkey-betz-platform/pull/3112) | Sub-phase 1 — golden 5-model tenant boundary fixture + matrix runner (5 cells, 20 tests) + I-030203 §3.5-§3.8 clarifications per Rigby Q4 SIGN | `df4e94e6` |
| 3 | [#3113](https://github.com/clwest/donkey-betz-platform/pull/3113) | **§5.1.b hotfix** — 3 destructive-mutation sites scoped (delete_deliverable + link_deliverable_workspace + record_deliverable_event) + ledger §5.1.b restructured as 3-site table + grep methodology guardrail | `41c8d458` |
| 4 | [#3114](https://github.com/clwest/donkey-betz-platform/pull/3114) | Sub-phase 2 — hybrid B+C matrix expansion (5 cells, 21 tests) + F1A cross-tenant fixture + §5.1.b **extended to 5th site** (get_deliverable anonymous content leak caught by Rigby Q2 Edit 2 content-leak invariant) + Rigby Q2 SIGN edits + §14 threshold documented | `5637dcd6` |

**Cumulative test surface added this session:**
- `tests/security/test_i0302_p4_ops_aggregate_decorator.py` — 8 smoke tests
- `tests/security/test_i0302_p4_matrix_harness.py` — 40 tests (5 Sub-phase 1 cells + 5 Sub-phase 2 cells)
- `tests/security/test_i0302_d1_deliverable_wiring.py` — 9 new tests across 3 hotfix regression classes
- `tests/security/fixtures/tenant_boundary.py` — golden fixture module (333 lines + F1A cross-tenant row extension)
- `tests/security/conftest.py` — pytest auto-discovery re-export
- `tests/security/fixtures/__init__.py` — package init

**Total new test coverage: 57 tests, all pass locally.**

---

## §2 Architecture + substrate shipped

### §2.1 `@ops_aggregate_allowed` decorator substrate (Sub-phase 0)

Codified before first use per Rigby "codify at Phase 4 open" SIGN (0.70 confidence). Zero uses at codification — baseline established.

- **File:** `core/security/decorators.py` — extends the module built at Phase 3 Sub-phase B2b for `superuser_required` (PR #3104)
- **Semantics:** request-time no-op marker. Belt-and-suspenders runtime attribute `_ops_aggregate_allowed = True`. Primary detection is AST tree, not runtime attribute.
- **Contract (I-030201 §11):**
  - Canonical import path: `core.security.decorators` (single canonical source enforced by AST harness — Rigby bonus tightening)
  - Required pairing with `@superuser_required` (both explicit; not auto-stacked)
  - Every use requires §11.X F-block ledger amendment
  - AST harness recognition rule: fail at test-collection on missing pair, wrong import path, or missing ledger amendment
- **Fail-safe posture:** code-only key for Phase 4 (Rigby SIGN F3.3 = A). DB-backed second key deferred to follow-on if decorator spreads to >20 sites.

### §2.2 Golden 5-model tenant boundary fixture (Sub-phase 1)

Layered fixture per Rigby SIGN F2 (0.75 confidence):

- **Users:** `tb_user_a`, `tb_user_b`, `tb_superuser`
- **Workspaces:** `tb_workspace_a` (owned by user_a), `tb_workspace_b` (owned by user_b)
- **Per model, N=3 rows per user:**
  - Deliverable × 6 (3 per workspace)
  - Initiative × 6 (3 per user)
  - ChatConversation × 6 (3 per user)
  - AgentExecution × 6 + 1 null-user (Session 642 superuser carve-out probe)
  - Document × 6 (3 per user)
- **F1A cross-tenant Deliverable** (Sub-phase 2 extension per Rigby Sub-phase 1 Q1): adversarial row with `user=user_b + workspace=workspace_a` — closest analog to a "shared workspace" edge under ProjectWorkspace's single-owner constraint. Visible to user_a (workspace_id match), invisible to user_b (predicate uses workspace_id not user_id). Documented in docstring as "NOT a valid business state."
- **Auto-discovery** via `tests/security/conftest.py` — every `tests/security/*.py` picks up `tb_*` fixtures without import.
- **`tb_` prefix** prevents collision with existing per-file fixtures in Phase 3 sub-phase wiring tests.

### §2.3 Matrix runner (Sub-phases 1 + 2)

10 cells total. Read-only primitives via immutable golden fixture; mutations use golden rows with per-test rollback (per-test builders deferred to Sub-phase 3 for CREATE-parent-binding).

**Sub-phase 1 (Rigby SIGN F1 = hybrid matrix + endpoint sentinels, 0.80):**
| Model | Primitive | Endpoint |
|---|---|---|
| Initiative | LIST | `/api/initiatives/` |
| AgentExecution | AGGREGATE | `/api/analytics/overview/` (Session 642 carve-out probe) |
| ChatConversation | GET | `/api/pa/conversations/<id>/` |
| Deliverable | LIST | `/api/deliverables/` |
| Document | AGGREGATE | `/api/v1/rag/stats/` |

**Sub-phase 2 (hybrid B+C after endpoint discovery falsified F2 assumption):**
| Model | Primitive | Endpoint | Notes |
|---|---|---|---|
| Deliverable | SAVE | `/api/deliverables/<uuid>/save/` | Existence-leak-tolerant (403/404) |
| Deliverable | UNSAVE | `/api/deliverables/<uuid>/unsave/` | Predicate-in-filter, strict 404 |
| Deliverable | TEMPLATEIZE | `/api/deliverables/<uuid>/templateize/` | Predicate-in-filter, strict 404 |
| Deliverable | GET-item | `/api/deliverables/<uuid>/` | Anonymous 401 post §5.1.b 5th-site fix |
| ChatConversation | LIST | `/api/pa/conversations/` | C1 predicate boundary probe |

Roles per §3.5: `anon`, `user_a`, `user_b`, `superuser` (4 tests per cell → 40 total).

### §2.4 Architecture doc I-030203

Extended in-session with:
- §3.5 — AllowAny + predicate-only exception (Initiative + Deliverable observed surface)
- §3.6 — Superuser semantics: **permission bypass, not tenancy bypass** unless explicitly declared via `@ops_aggregate_allowed`. Prevents future reviewers from misclassifying "superuser sees fewer rows than user_a" as a regression.
- §3.7 — Session 642 null-user carve-out contract (AgentExecution only)
- §3.8 — Canonical JSON assertion paths per aggregate endpoint (`/api/analytics/overview/` → `body["total_executions"]`; `/api/v1/rag/stats/` → `body["embeddings_stats"]["total_documents"]`)
- §6 — Implementation Order updated with Sub-phase 0/1/2 done markers + Sub-phase 3 pipeline
- §6.a — Sub-phase 3 research inputs (AgentExecution mutation semantics, Document `user` vs `owner` field question, CREATE-parent-binding endpoint map, AGGREGATE endpoint inventory, non-canonical model follow-on)

---

## §3 §5.1.b hotfix — 5 sites scoped this session

Ledger §5.1.b amendment restructured as a 5-site table capturing D1 sweep-gap discovery. All 5 sites in `core/views_deliverables.py`; all discovered via Phase 4 harness endpoint discovery + subsequent Rigby SIGN-driven test tightening.

| # | Site | Op | Pre-hotfix gap | Fix | PR |
|---|---|---|---|---|---|
| 1 | `delete_deliverable:243` | DELETE | Unscoped `get_object_or_404` — any authenticated caller could delete | `scope_queryset_deliverable` wrap + `except Http404: raise` | #3113 |
| 2 | `link_deliverable_workspace:528` | MUTATE (workspace FK rewrite) | (a) source-fetch unscoped; (b) target workspace fetch unscoped | (a) predicate wrap; (b) `user_can_access_workspace` gate; (c) Http404 propagation | #3113 |
| 3 | `record_deliverable_event:1044` | MUTATE (audit event) | (a) NO auth gate; (b) NO ownership check | (a) `@token_auth_required`; (b) predicate wrap; (c) Http404 propagation | #3113 |
| 4 | `unsave_deliverable:295` | MUTATE (is_saved toggle) | `except Exception` swallowed Http404 → 500 not 404 | `except Http404: raise` (2 lines) | #3114 |
| 5 | `templateize_deliverable:390` | MUTATE (is_template toggle) | Same Http404-swallow | Same 2-line fix | #3114 |
| 5b | `get_deliverable:161` | READ (5th distinct site, same class) | (a) NO auth gate + `is_authenticated` guard skipped access check for anon → 200 + full content leak; (b) same Http404-swallow | (a) `@token_auth_required`; (b) `except Http404: raise` | #3114 |

**Discovery mechanism per site:**
- Site 1 surfaced by Sub-phase 2 endpoint discovery (running grep for `get_object_or_404(<Model>, id=...)` per Rigby SIGN Q3 guardrail)
- Sites 2 + 3 surfaced by Chris-ratified codebase-wide grep sweep
- Sites 4 + 5 surfaced by harness matrix test failures during Sub-phase 2 cell writing
- Site 5b (get_deliverable) surfaced by **Rigby Q2 Edit 2 content-leak invariant assertion** during Sub-phase 2 SIGN cycle — the harness surfaced the bug via its own tightening

**§14 two-triggers threshold MET decisively** (5 instances of same anti-pattern in single view file). Ledger §5.1.b tail documents the tally and specifies Sub-phase 3 codification as mandatory.

**Chain of custody per site is preserved in the ledger.** Both Chris D-verdicts ("B — hotfix PR first, then Sub-phase 2" and "A — expand this PR" applied twice) are named in §5.1.b provenance. Rigby SIGN pin `pa-59d27abadeed4411` is the arc-scoped SIGN authority.

**Non-canonical model findings from §5.1.b grep sweep** (noted for follow-on I-0302 scope carve-out review — not fixed this session):
- `core/views_legal.py:962/1281` — `LitigationDocument.objects.get(id=document_id)` unscoped
- `core/views_artifacts.py:639/673/706/742` — `ReviewDocument.objects.get(id=review_id)` unscoped
- `core/views_rag_embeddings.py:470/836` — `Document.objects.get(id=..., user=user)` uses `user=` filter on model whose FK is named `owner` (dual-field or bug — needs investigation)

---

## §4 System Owner directives resolved

Explicit Chris D-verdicts this session:

| Directive | Context | Outcome |
|---|---|---|
| "route through Rigby" (Phase 4 open) | Sub-phase 0 harness architecture design SIGN | Rigby F1-F4 + F3.1-F3.3 SIGN completed |
| "I think we allow them with ii what do you and Rigby think?" | F3 ops carve-out policy | (ii) `@ops_aggregate_allowed` per-view decorator chosen |
| "agree all ship the bonus tightening" | Rigby F3.1-F3.3 sub-detail SIGN | (B) AST scan, (B) both decorators explicit, (A) code-only fail-safe, + single canonical import path bonus |
| "incremental PRs, light SIGN per PR" | PR granularity strategy | 4 PRs shipped with per-PR Rigby SIGN gates |
| "merge it and open sub-phase 1" | Sub-phase 0 close | PR #3111 merged, Sub-phase 1 opened |
| "merge it and open sub-phase 2" | Sub-phase 1 close | PR #3112 merged, Sub-phase 2 opened (endpoint discovery pivot) |
| "B — hotfix PR first, then Sub-phase 2" | §5.1.b delete_deliverable discovery | PR #3113 opened as separate hotfix |
| "A — expand this PR" (first occurrence) | 2 more §5.1.b sites (link + record) surfaced by grep | PR #3113 extended to 3-site scope |
| "merge it and continue with sub-phase 2" | §5.1.b hotfix close | PR #3113 merged, Sub-phase 2 continued |
| "proceed with hybrid B+C, treat as intentional immutability" | Sub-phase 2 re-scoping | Initiative + ChatConversation CRUD DELETE/UPDATE = intentional; Sub-phase 3 formalizes as absence-contract |
| "A — expand this PR" (second occurrence) | 5th §5.1.b site (get_deliverable) surfaced by Rigby Q2 Edit 2 | PR #3114 extended with 5th-site fix |
| "merge it and route final SIGN through Rigby" | Sub-phase 2 close | PR #3114 merged, §14 codification design SIGN routed |

---

## §5 What's next (Sub-phase 3 opening protocol)

Per I-030203 §6 + §6.a and Rigby final SIGN, Sub-phase 3 opens with:

### §5.1 §14 codification (Rigby final SIGN 2026-07-10)

Per Rigby F1/F2/F3 (confidence 0.74-0.80), all leans matched, no Chris ratification needed for the design:

- **F1 Mechanism:** C — extend the Phase 4 harness AST scan module (built for `@ops_aggregate_allowed`) to also flag `except Exception` around `get_object_or_404` without `except Http404: raise` first. One canonical "security conformance AST" surface. Ship as `tests/security/test_i0302_p4_ast_conformance.py`.
- **F2 Scope:** B — all Django view files (`core/views*.py` + `apps/*/views*.py` + DRF viewsets). Path-based allowlist heuristics.
- **F3 Retroactive sweep:** A — sweep + fix within F2 scope BEFORE enforcement lands. Workflow: report-only mode → patched batch PR → flip to enforcing mode.
- **Rigby offered** to propose the exact AST rule definition (what constitutes a violation) — captured as Sub-phase 3 opening move.

### §5.2 Other Sub-phase 3 substrate (per I-030203 §6 steps 10-15)

- Formalize intentional-immutability contract for Initiative + ChatConversation (assert unsafe methods return 405/404 as absence-contract)
- Build AST scan module for `@ops_aggregate_allowed` enforcement (Task #7)
- Build endpoint sentinels layer (10-30 view-layer risk endpoints per Rigby SIGN F1) (Task #8)
- Build deferred-surface coverage-gap report + posture probes for §5.3.b/§5.1.a/§5.5.a skipped surfaces (Task #9)
- VIP-scope carve-out coverage extension on `get_deliverable` matrix cell

### §5.3 Sub-phase 3 research inputs (per I-030203 §6.a)

Bounded, docs-only research passes required before code lands:

- AgentExecution mutation semantics — confirm no user-facing UPDATE/DELETE (likely no per S2748 Initiative + ChatConversation finding)
- Document `user` vs `owner` field question (`views_rag_embeddings.py:470/836` uses `user=user` on a model whose canonical FK is `owner` — dual-field, legacy alias, or runtime bug?)
- CREATE-parent-binding endpoint map across the 5 canonical models
- AGGREGATE endpoint inventory (extends §3.8 canonical JSON path table)
- Non-canonical model follow-on scope decision (`LegalDocument`, `LitigationDocument`, `ReviewDocument` — in I-0302 or separate arc?)

---

## §6 Governance provenance

### §6.1 Substrate / ledger amendments landed this session

- I-030201 §11 — `@ops_aggregate_allowed` decorator substrate (Sub-phase 0)
- I-030201 §5.1.b — 5-site hotfix + §14 threshold codification (Sub-phase 2 close)
- I-030203 §3.5-§3.8 — assertion contract clarifications (Sub-phase 1)
- I-030203 §6 — Sub-phase 3 pipeline (Sub-phase 2 close)
- I-030203 §6.a — Sub-phase 3 research inputs (Sub-phase 2 close)

### §6.2 Rigby SIGN cadence

Per Chris "light SIGN per PR" directive at S2748 open. Every PR received a shipped-code SIGN cycle from Rigby via `pa-59d27abadeed4411`:

- PR #3111 (Sub-phase 0): Q1-Q4 SIGN-PASS on 3 folds, SIGN-WITH-EDITS on Q3 smoke test coverage → 2 test additions applied
- PR #3112 (Sub-phase 1): Q1-Q4 SIGN-PASS on 2 folds, SIGN-WITH-EDITS on Q1 (Sub-phase 2 deferred) + Q4 (I-030203 §3.5-§3.8 clarifications applied)
- PR #3113 (§5.1.b hotfix): Q1-Q3 all SIGN-PASS after re-routing with explicit repo_tool instructions
- PR #3114 (Sub-phase 2): Q1 SIGN-PASS, Q2 SIGN-WITH-EDITS (2 test tightenings → surfaced 5th-site security bug), Q3 SIGN-WITH-EDITS (ledger §14 tally clarification applied)
- §14 codification design SIGN (session close): F1 (0.80) + F2 (0.74) + F3 (0.76) all matched Claude's leans

### §6.3 Session pin lifecycle

- **Retired at session open:** `pa-cd35bde16f974843` (S2747 arc pin)
- **Minted at session open:** `pa-59d27abadeed4411` (label `ios-arc-open-I0302-P4`)
- **Active at session close:** `pa-59d27abadeed4411` — carry-forward to S2749 Sub-phase 3 opening. Do NOT retire at S2749 open unless Chris explicitly changes arc scope.

### §6.4 Playbook rule alignment

- PLAYBOOK-6.10.6 (verify-substrate-before-implement) — applied: harness design SIGN preceded code (Sub-phase 0 architecture doc + §11 substrate landed before matrix runner Sub-phase 1)
- PLAYBOOK-6.6.14 (design-prep discipline) — applied: harness architecture doc `I-030203_phase4_harness_architecture.md` codified F1-F4 SIGN outcomes before implementation
- §14 two-triggers-plus rule — MET decisively via 5-instance count in `views_deliverables.py`; Sub-phase 3 opening MUST codify Http404-swallow AST check per Rigby F1 SIGN

---

## §7 Memory candidates (for future codification)

Session surfaced patterns that may become memory rules with more corroboration:

- **Harness caught 3 real security bugs during Sub-phase 2** (§5.1.b sites 1, 5, 5b + Rigby Q2 Edit 2 as amplifier). The Sub-phase 2 shipped-code SIGN loop is a real bug-finder, not just a design-check. **Pattern to watch:** "Rigby SIGN-WITH-EDITS assertion tightening surfaced production bug." If this repeats in Sub-phase 3, worth codifying as a workflow pattern.
- **Chris scope-expansion pattern:** "A — expand this PR" applied twice this session (both times same-class bugs from same discovery). If the pattern surfaces a 3rd time with same rationale, worth codifying as a playbook §14 candidate rule (e.g., "same-class bugs from same discovery ship in same PR when trivial-to-fix").
- **Endpoint discovery falsifying design SIGN:** Sub-phase 2 F2 SIGN assumed UPDATE/DELETE existed for 3 models; endpoint discovery falsified it. Discovery-before-design vs design-before-discovery is a real methodology tension worth memory tracking.

---

## §8 Repository state at close

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `5637dcd6` (PR #3114 merged; Sub-phase 2 complete + §5.1.b extended to 5 sites) |
| Playbook version | v0.4.1 (unchanged) |
| Playbook rule count | 196 (unchanged) |
| Constitutional Debt | Zero outstanding |
| Session pin | `pa-59d27abadeed4411` (active — carry-forward to S2749) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-59d27abadeed4411` (rotated at S2748 open) |
| Live infra state | `SystemConfiguration cost_threshold_month = 500`, mode = `monitor` (observation period accumulating since 2026-07-10 07:35 MDT — check-in actionable 2026-07-11+) |
| RUR arc state | I-0301 CLOSED · I-0302 Phases 1-3 CLOSED · Phase 4 Sub-phases 0/1/2 CLOSED · Phase 4 Sub-phase 3 AUTHORIZED · Phase 4 close pending · Phase 5 (arc close) not yet opened · I-0303 not yet opened · RUR-C1 parent OPEN |

**End of Session 2748 handoff. S2749 opens on Sub-phase 3 opening protocol per I-030203 §6 + §6.a + Rigby final §14 codification design SIGN.**
