---
session: 2772
date: 2026-07-12
title: "Ops-endpoint auth-regression smoke suite + staff-gate expansion ratified"
status: complete
outcome: shipped
scope: net-new-engineering-N16
canonical_authority: repo_canonical
ratification_envelope: docs/research/implementation/RATIFICATION_2026-07-12_ops_auth_regression_smoke_suite.md
---

# Session 2772 — Ops-endpoint auth-regression suite + staff gate ratified

## §1. TL;DR

Chris selected N16 from the S2772 candidate menu. Rigby joint SIGN produced Q1 MODIFY (assertion tightened from `!=200` to `{302, 401, 403}`), Q2 PASS (explicit per-endpoint tests), and Q3 (open-ended zoom-out per S2771 rule) → 7 substantive concerns. Two Q3 concerns shipped same-PR (formal ops-endpoint policy docstring; auth-regression inventory guard). One (staff-only gate) escalated to Chris same-turn for D-verdict — approved. Four recorded as forward-carry with explicit trigger criteria.

Also codified: the S2771 workflow rule ("include at least one open-ended zoom-out ask per Rigby SIGN") is validated on first use. The zoom-out produced the largest single SIGN response of the ops-console arc.

**Seventh close-cycle post-PLAYBOOK-7.4.4-codification.** First test-shipping session since the S2755→S2771 operator-surface streak.

## §2. Timeline

| Time (approx) | Event | Reference |
|---|---|---|
| S2772 open | freshness check via retired S2771 pin: FRESH · SHA `aecb4e59b266` | this session |
| N16 selected | Chris: "N16 approved, route joint SIGN through Rigby" | this session |
| Pin minted | `pa-6ca91be75701425f` scoped to `s2772-ops-auth-regression-smoke` | `session_lifecycle open` |
| Verify-before-build | catalogued 6 ops endpoints; Django TestCase convention; codebase uses inline `is_staff` checks rather than decorators | this session |
| Rigby design SIGN | 3-fold + explicit open-ended zoom-out Q3 (S2771 rule applied) | pin above |
| Q1 MODIFY adopted | assertion set tightened to `{302, 401, 403}` | this session |
| Q3 #2 escalated to Chris | staff-gate decision (tighten now vs defer) — Chris approved tighten | this session |
| Code + test | policy docstring + staff gate + 15 tests written | this session |
| Test run | 15/15 PASS in 0.581s | this session |
| Envelope + handoff | this doc + envelope | filesystem |
| Docs cascade + provenance | 4-step + provenance rebuild | (post-merge below) |
| PR merge | filled at merge | GitHub |
| `make recycle-all` | seventh cycle post-codification | Makefile |

## §3. What shipped

**Files touched:**

- `core/views_ops_console.py` — 3 changes: (a) module-level ops-endpoint scope policy docstring block (Rigby Q3 #1); (b) new `_ops_staff_only = user_passes_test(lambda u: u.is_authenticated and u.is_staff)` module decorator; (c) `@_ops_staff_only` added alongside `@login_required` on all 6 endpoints.
- `core/tests/test_ops_auth_regression_2772.py` (new) — 4 TestCase classes, 15 tests:
  - `OpsAuthRegressionAnonymousTest` (6 tests, one per endpoint) — anon → asserts status in `{302, 401, 403}`
  - `OpsAuthRegressionNonStaffTest` (6 tests) — non-staff → same assertion set
  - `OpsAuthStaffAllowedTest` (1 test) — happy-path canary: staff → assert status NOT blocked
  - `OpsRouteInventoryGuardTest` (2 tests) — inventory guard fails loudly if a new endpoint is added without matching tests
- `docs/research/implementation/RATIFICATION_2026-07-12_ops_auth_regression_smoke_suite.md` — new envelope.
- `docs/handoffs/SESSION_2772_OPS_AUTH_REGRESSION_SMOKE_SUITE_RATIFIED.md` — this file.

Net: backend +45 lines, tests +180 lines. Zero frontend edits. Zero new deps.

**Chris's browser session:** confirmed unaffected — `chris: is_staff=True is_superuser=True` verified pre-code.

**Observed status codes at test-time (empirical):**
- Anon → 401 (returned by `core.auth_middleware`, before `@login_required` runs)
- Non-staff → 302 (via `_ops_staff_only` redirect to LOGIN_URL)
- Staff → 200 (happy path, close_ceremony_ledger returns real data)

## §4. Rigby SIGN Summary

Joint SIGN via pin `pa-6ca91be75701425f`.

**Freshness:** verdict FRESH · SHA `aecb4e59b266` matches HEAD (S2771 close). Sixth post-codification cycle held. Recycle log top 3 all N7-enriched.

**Q1 (assertion shape):** MODIFY. `!= 200` lets 500/404 pass — those aren't auth working. `{302, 401, 403}` is the durable contract. Adopted.

**Q2 (test structure):** PASS. Explicit per-endpoint tests. Surgically clear failures + deliberate friction on drift.

**Q3 (open-ended zoom-out — S2771 rule applied):** 7 concerns:
1. Ops scope creep → formal boundary. **Same PR: docstring policy.**
2. Auth is necessary but not sufficient → staff/role gating decision. **Escalated to Chris → approved → same PR: `_ops_staff_only` gate.**
3. Health-summary sub-call composition (HTTP loop vs function). **§7 forward-carry with explicit trigger.**
4. Query-param growth without allowlist. **§7 forward-carry with trigger: 2nd endpoint reaching ≥4 optional params.**
5. Search DoS/injection risk. **§7 forward-carry with trigger: first high-freq operator search OR 2nd search endpoint.**
6. Access logging for powerful endpoints. **§7 forward-carry with trigger: 2nd staff user grant.**
7. Public route registration slip. **Same PR: inventory guard test.**

## §5. Post-merge browser eyeball (Chris)

1. Hard-refresh `localhost:8000/workspace?tab=system&sub=ops`.
2. All ops-console sections should render normally — you're `is_staff=True is_superuser=True`, so the staff gate lets you through.
3. If you happen to be logged out or in a different browser profile, you'll get a login redirect. That's the S2772 change working.
4. No new UI. This session shipped tests + a decorator, not surface.
5. Optional: `curl -s http://localhost:8000/api/ops/health-summary/ -w "\n%{http_code}\n"` from an anon shell to see the 401 (auth_middleware caught it before login_required).

## §6. Twin-Pointer Card

📁 **Repo `/docs/` + `/core/` — S2772 artifacts:**

- **Amended backend view module:** `core/views_ops_console.py` (policy docstring + `_ops_staff_only` + 6 decorated endpoints)
- **New test file:** `core/tests/test_ops_auth_regression_2772.py`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-12_ops_auth_regression_smoke_suite.md`
- **Handoff:** `docs/handoffs/SESSION_2772_OPS_AUTH_REGRESSION_SMOKE_SUITE_RATIFIED.md`
- **Trigger context (S2771 meta-critique #4):** `docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_full_text_search.md`
- **Constitutional context:** `docs/ENGINEERING_PLAYBOOK.md` §7.4.4 (v0.6.0, S2766)

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2772
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surface:** ops-console tab unchanged in appearance for you (staff); non-staff users would now hit login-redirect.

## §7. Current Repository State

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2772 merge) |
| Playbook version | v0.6.0 (RATIFIED S2766) |
| RUR-C1 state | S2755→S2771 diagnostic infra + operator surfaces + governance CLOSED · **S2772 ops-auth regression + staff gate CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-6ca91be75701425f` (retired at S2772 close, force=true) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-6ca91be75701425f` (retired; forces fresh mint at S2773 open) |
| Live infra state | S2755→S2771 diagnostic infra + Playbook v0.6.0 + CCL v2 hover/drawer/filter/search + N7 recycle emitter enriched + N11 PARTIAL_RECYCLE tile + **N16 auth-regression suite + staff gate** operational |
| Next move | Chris selects at S2773 open |

## §8. What This Session Taught About Doing Sessions

- **The S2771 workflow rule ("open-ended zoom-out ask per SIGN") is validated on first use.** Rigby delivered 7 substantive concerns on Q3 alone — the largest single SIGN response of the ops-console arc. Continue the discipline.
- **When Rigby's zoom-out raises multiple substantive concerns, triage cleanly:** ship the small ones same-PR (docstring + inventory guard + Chris-approved gate), record structural ones as forward-carry with EXPLICIT trigger criteria (not "someday"), escalate scope-expansion candidates to Chris same-turn.
- **Trigger criteria are the real forward-carry deliverable.** "§7 forward-carry" without a specific trigger is a graveyard. Each of the 4 recorded concerns names the observable event that would upgrade it from watch-list to actionable ("2nd endpoint reaches ≥4 optional params"; "first high-freq operator search"; "2nd staff user grant"). This lets future sessions know when to act without re-deciding.
- **Test-shipping sessions are legitimate net-new engineering.** After 6 consecutive operator-surface iterations (S2755→S2771), N16 shipped 45 lines of hardening + 180 lines of tests + 15 passing test methods. No new UI. This is exactly what Rigby's "verify-before-build → substrate hardening" discipline produces at maturity.
- **Seventh cycle under PLAYBOOK-7.4.4 continues to hold.** N7-enriched entries continue to accumulate; N11 PARTIAL_RECYCLE branch remains dormant (correct — no partials in the wild yet).
