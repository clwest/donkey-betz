---
title: "Ops-Endpoint Auth-Regression Smoke Suite + Staff Gate Ratification Record (2026-07-12)"
status: active
authority: ratification-record
session_added: 2772
ratification_date: 2026-07-12
ratifier: chris
routing: rigby-pa-chat joint SIGN (design + open-ended zoom-out per Chris S2771 workflow rule) + Chris N16 selection + Chris D-verdict on same-PR staff-gate expansion
scope: S2772 — N16: (a) lock the security property that every /api/ops/* endpoint refuses anonymous + non-staff access via a Django TestCase suite with route-inventory guard; (b) tighten auth from @login_required-only to @login_required + @user_passes_test(is_staff) on all 6 endpoints; (c) add a formal ops-endpoint scope policy docstring at the top of `views_ops_console.py`.
serves_arc: Rigby S2771 meta-critique #4 (ops-surface security drift mitigation); substrate hardening before non-admin users arrive
precedent_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_full_text_search.md (S2771 — meta-critique that raised the concern)
  - docs/research/implementation/RATIFICATION_2026-07-11_health_summary_partial_recycle.md (S2770 — sibling operator surface)
ratified_documents:
  - core/views_ops_console.py (amended — module-level ops-endpoint scope policy docstring block; `_ops_staff_only` decorator; @_ops_staff_only added alongside @login_required on all 6 endpoints)
  - core/tests/test_ops_auth_regression_2772.py (new — 4 TestCase classes, 15 tests: 6 anon-blocks + 6 non-staff-blocks + 1 staff-reachable-happy-path + 2 route-inventory guards)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2772 open freshness (retired-pin dispatch to Rigby) — verdict FRESH · SHA aecb4e59b266 matches HEAD (SIXTH corroboration cycle after PLAYBOOK-7.4.4; recycle log top three N7-enriched)
  - S2772 design SIGN (Rigby, pin pa-6ca91be75701425f) — Q1 MODIFY (assertion set tightened from `!=200` to `{302, 401, 403}` to reject 500/404 as false positives); Q2 PASS (explicit per-endpoint tests); Q3 open-ended zoom-out per Chris S2771 rule produced 7 substantive concerns
frozen: true
---

# Ops-Endpoint Auth-Regression Smoke Suite + Staff Gate — Ratification Record

Frozen canonical record of Chris's ratification of the S2772 N16 auth-regression suite + staff-gate expansion on 2026-07-12. First session to explicitly ship tests (rather than product surface) since S2755→S2771's operator-surface streak. Ships the concrete mitigation for Rigby's S2771 meta-critique #4 (ops surfaces drift into "debug everything" without vigilance).

Also codifies the meta-lesson from S2771: the quality of Rigby SIGN pushback is a function of the question asked. S2772 SIGN was the first to include an explicit open-ended zoom-out ask (Q3). Result: 7 substantive concerns raised; 2 addressed in same PR; 4 recorded as forward-carry with explicit trigger criteria; 1 (staff gate) escalated to Chris same-turn for D-verdict. Chris approved the same-PR staff-gate expansion.

Append-only.

---

## §1. Context

- **Ratification date:** 2026-07-12 (America/Denver operator timezone; crossed midnight during work)
- **Scope:** substrate hardening + test coverage (N16 in S2772 candidate menu).
- **Motivation:** Rigby's S2771 meta-critique #4 flagged that `/api/ops/*` endpoints accumulate visibility over time and the category tends to drift into "debug everything" if unattended. Ops endpoints today expose SLO status, failure signatures, blocked agents, health summary, close-ceremony ledger, and recycle timeline — all safe for the current single-user pre-prod context but a real risk vector when non-admin users arrive.
- **Ratifier:** Chris (candidate selection at S2772 open: "N16 approved, route joint SIGN through Rigby"; same-turn D-verdict on the same-PR staff-gate expansion: "approved").
- **Sixth cycle after PLAYBOOK-7.4.4 codification:** S2772 open verified FRESH · SHA-match at `aecb4e59b266` (S2771 close). Recycle log top three all N7-enriched. N11 PARTIAL_RECYCLE branch dormant (correct — no partials in the wild).

---

## §2. Ratified Deliverables

### §2.1 `core/views_ops_console.py` — module-level scope policy docstring

A 20-line policy block at the top of the module names six rules for every ops endpoint:

1. Aggregate / read-only. No mutation endpoints; no side effects.
2. No raw DB dumps, secrets, user content.
3. Reject or safely ignore unknown query parameters.
4. Require both `@login_required` AND `@user_passes_test(is_staff)`. Anon → 302; non-staff → 302; staff → 200. Auth-regression tests lock the contract.
5. Fail soft on downstream error — degrade, do not 500.
6. Compose sub-calls at the FUNCTION level, not HTTP loops.

Adding a new `/api/ops/*` endpoint MUST include matching auth tests in the auth-regression suite — the inventory guard fails loudly if you forget.

### §2.2 `core/views_ops_console.py` — `_ops_staff_only` decorator

New module-level decorator:

```python
_ops_staff_only = user_passes_test(
    lambda u: u.is_authenticated and u.is_staff,
)
```

Added to all 6 endpoints alongside `@login_required`. Decorator chain order (top-to-bottom):

```python
@require_GET
@login_required   # anon → 302 to LOGIN_URL (short-circuits here)
@_ops_staff_only  # authenticated-non-staff → 302 to LOGIN_URL
def endpoint(...): ...
```

Anon never reaches `_ops_staff_only` because `@login_required` catches them first. Non-staff authenticated users reach `_ops_staff_only`, fail the `is_staff` test, and get redirected. Staff users pass both and hit the view.

### §2.3 `core/tests/test_ops_auth_regression_2772.py` — 15 tests

Four TestCase classes:

- **`OpsAuthRegressionAnonymousTest`** — 6 tests, one per endpoint. Anon GET → assert `status_code in {302, 401, 403}`.
- **`OpsAuthRegressionNonStaffTest`** — 6 tests, one per endpoint. Logged-in-non-staff GET → assert `status_code in {302, 401, 403}`.
- **`OpsAuthStaffAllowedTest`** — 1 test (happy-path canary). Staff GET on close_ceremony_ledger → assert `status_code NOT in {302, 401, 403}`. Without this test, an over-eager gate that returned 403 for everyone would still pass the two suites above.
- **`OpsRouteInventoryGuardTest`** — 2 tests:
  - `test_all_ops_endpoints_have_auth_tests` — enforces that every URL name in `_OPS_ENDPOINTS` inventory has both `test_<name>_blocks_anonymous` and `test_<name>_blocks_non_staff` method defined. Prevents test-rot.
  - `test_ops_url_space_matches_inventory` — walks the Django URL resolver, collects every URL name starting with `ops-`, and asserts symmetric difference with `_OPS_ENDPOINTS` is empty. Prevents new endpoints from being added without matching inventory + tests.

Total: 15 tests. Ran in 0.581s. All pass.

### §2.4 Rigby Q1 MODIFY: assertion set tightened

Original lean: assert `status != 200` (block payload delivery).
Rigby MODIFY: `!= 200` lets 500 and 404 pass, which is not the intent of an auth-regression suite. A broken endpoint (500) or a stale URL (404) should NOT be evidence that auth works.
Adopted: `assertIn(response.status_code, {302, 401, 403})`. Only redirect-to-login and forbidden statuses count as blocking evidence.

Observed status codes from the empirical run:
- Anon → 401 (returned by `core.auth_middleware`, before `@login_required` runs)
- Non-staff → 302 (`@user_passes_test` redirects to LOGIN_URL)
- Staff → 200 (happy path)

Both anon (401) and non-staff (302) fall within `{302, 401, 403}` — assertion set correctly covers observed behavior.

---

## §3. What Was NOT Changed

- No changes to any handler bodies. Only decorators + docstring on the view side.
- No frontend edits. Chris is `is_staff=True is_superuser=True` — his browser session continues to work.
- No changes to auth_middleware.py (source of the anon → 401 behavior). Left as-is.
- No mutations to ops_tool PA handlers — the tests hit the REST endpoints, not the PA gateway.
- Rigby's meta-critique concerns #3 (health-summary function-vs-HTTP composition), #4 refinement (broader access logging), #5 (search DoS limits), #6 (query-param allowlist per endpoint) — all recorded as forward-carry per §7.

---

## §4. Rigby SIGN Summary

Joint SIGN via pin `pa-6ca91be75701425f` (label `s2772-ops-auth-regression-smoke`).

### §4.1 Q1 — Assertion shape
- **Rigby verdict:** MODIFY.
- **Content:** primary assertion should reject 500/404 as false positives; specific `{302, 401, 403}` set is the durable contract. **Adopted.**

### §4.2 Q2 — Test structure
- **Rigby verdict:** PASS.
- **Content:** one test method per endpoint is right — surgically clear failures ("which endpoint drifted") + deliberate friction when a new endpoint is added without tests.

### §4.3 Q3 — Open-ended zoom-out on the ops-console pattern
- **Rigby verdict:** freeform substantive critique.
- **Content:** 7 concerns raised, ordered by "small now, expensive later":
  1. Ops surface scope creep needs a formal boundary. **→ Q3 #1 addressed in same PR (§2.1 docstring).**
  2. Auth is necessary but not sufficient: staff/role gating decision. **→ Q3 #2 escalated to Chris; approved; addressed in same PR (§2.2 gate).**
  3. Health-summary composing 5 sub-calls: HTTP loops vs function calls. **→ §7 forward-carry.**
  4. Query-param growth → accidental data exposure without allowlist. **→ §7 forward-carry.**
  5. Search introduces injection/DoS risk if not constrained. **→ §7 forward-carry.**
  6. Observability: access logging for powerful endpoints. **→ §7 forward-carry.**
  7. Test coverage should catch accidental public route registration. **→ Q3 #7 addressed in same PR (§2.3 inventory guard test).**

**Meta-observation on the SIGN cycle itself:** the S2771 lesson ("include at least one open-ended zoom-out ask per session") produced its intended effect on the first application. Rigby delivered 7 concerns; my proposals shipped Q3 #1, #2, and #7 in same PR; #3, #4, #5, #6 recorded with explicit trigger criteria in §7.

---

## §5. Empirical smoke tests

### §5.1 `python manage.py test core.tests.test_ops_auth_regression_2772 -v 2`
- Result: **15/15 PASS in 0.581s.**
- Anon returns 401 (auth_middleware short-circuit).
- Non-staff returns 302 (user_passes_test redirect).
- Staff happy-path returns 200.
- Inventory guard PASSes: URL space matches `_OPS_ENDPOINTS` list exactly (6 names, no drift).

### §5.2 No frontend edit, no bundle impact
- Skipped Vite build — no frontend files touched.

### §5.3 No Rigby HTTP smoke — tests are the smoke
- Django's `TestCase` uses transaction-isolated fixtures, not a live server. `http_smoke_test` would hit the running dev daphne but only prove "the current running instance has the staff gate" — which is already proven by the test suite running against the freshly-compiled code path.

---

## §6. Post-ratification bindings

- **Head at ratification:** filled at merge.
- **Merged PR:** filled at merge.
- **Workspace mirrors (S2754a twin-canonical rule):**
  - Governance envelope mirror → `RUR-C1 Tenant Boundary Lockdown` workspace `fcd7e683-3bfe-4d35-9704-0e54dd587ea1`.
  - Content mirror → same workspace.
- **PLAYBOOK-7.4.4 dogfood:** `make recycle-all` invoked post-merge — seventh consecutive cycle where the constitutional rule fires; fifth cycle emitting N7-enriched entries.
- **`session_tool.retire` at close:** third consecutive `force=true` required per `feedback_session_tool_retire_needs_force_true` memory rule.

---

## §7. Forward carry

Four Rigby S2772 Q3 concerns recorded with explicit trigger criteria:

- **Q3 #3 (Health-summary sub-call composition).** Currently `health_summary` calls `_handle_ops` directly via `OpsHandlersMixin` (function-level composition, not HTTP loops). Verified in §5 pre-merge review — no HTTP round-trips in the composition path. Codified as rule #6 in §2.1 docstring policy. **Trigger for revisit:** any future ops endpoint that composes another ops endpoint's REST route rather than its handler function.
- **Q3 #4 (Query-param allowlist).** `close_ceremony_ledger` now accepts 6 optional params (`limit`, `session_min`, `session_max`, `envelope_only`, `date_from`, `date_to`, `text`). Unknown params silently ignored — Rigby's concern is that "silent ignore" makes it too easy to add an unsafe param like `?raw=1`. **Trigger for codification:** propose an `explicit_query_params` allowlist decorator + 400 response for unknown keys, when a second endpoint reaches ≥4 optional params.
- **Q3 #5 (Search DoS/injection limits).** N14 full-text search on `text` param has no length cap, no ReDoS surface (Python `str.count()`, not regex), no rate limit. Cheap-filters-first mitigates full-corpus scan cost. **Trigger for codification:** first observed high-frequency operator search or first search-endpoint added elsewhere.
- **Q3 #6 (Access logging).** Ops endpoints run inside `auth_middleware` which already logs API requests/responses. Sample from the test run: `API Response: GET /api/ops/blocked-agents/ -> 302`. Verified sufficient for current single-user context. **Trigger for extension:** when a second user is granted staff role, add structured audit logging that captures user_id + query params separately from the request log.

---

## §8. Meta-observation on SIGN discipline (recorded per S2771 workflow rule)

S2771 close observation: Rigby SIGN cycles had drifted to all-PASS across 3 consecutive sessions. Chris named the pattern; I identified 4 causes (sharper proposals, known groove, Rigby institutional model, some rubber-stamp creep) and codified a fix: include at least one open-ended zoom-out ask per Rigby SIGN.

S2772 was the first application of the rule. Result: 7 substantive concerns raised on Q3 alone — the largest single SIGN response of the ops-console arc. Two directly shipped same-PR; five recorded with trigger criteria; one escalated to Chris same-turn.

**Codified conclusion:** the S2771 workflow rule is validated on first use. Continue the discipline. Save as feedback memory.
