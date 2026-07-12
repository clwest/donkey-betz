---
title: "Ops-Endpoint Query-Param Allowlist + Helper Refactor + Date-Validation Fix Ratification Record (2026-07-12)"
status: active
authority: ratification-record
session_added: 2773
ratification_date: 2026-07-12
ratifier: chris
routing: rigby-pa-chat joint SIGN (design + zoom-out per S2771 rule + implementation SIGN + concrete follow-up SIGN) + Chris N18 → N18v2 scope-expansion D-verdict
scope: S2773 — N18v2 (expanded per Chris D-verdict on Rigby zoom-out): (a) extract `_call_ops_tool` module helper to replace 4-copy `_Proxy(OpsHandlersMixin)` boilerplate (Rigby Q3 #1); (b) enforce per-endpoint query-param allowlist on all 6 `/api/ops/*` endpoints via `_reject_unknown_query_params` helper + `_OPS_ALLOWED_PARAMS__<NAME>` frozenset constants (Rigby Q3 #2); (c) fix `_parse_date_param` calendar validation using `datetime.date.fromisoformat` (Rigby Q3 #4); (d) new test file with 22 tests locking the contract (Rigby Q2 MODIFY); (e) 400 response body with machine-stable `code='unknown_query_params'` field (Rigby Q1 MODIFY).
serves_arc: substrate hardening → Rigby S2771/S2772 meta-critique #4 addressed at pattern level (not just one endpoint); DRY cleanup of ops-tool dispatch; correctness fix on date filtering
precedent_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-12_ops_auth_regression_smoke_suite.md (S2772 — sibling substrate hardening; auth gate)
  - docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_full_text_search.md (S2771 — meta-critique origin)
  - docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_search_filter.md (S2769 — `close_ceremony_ledger` filter surface being hardened)
ratified_documents:
  - core/views_ops_console.py (amended — `_call_ops_tool` helper + 6 `_OPS_ALLOWED_PARAMS__<NAME>` frozenset constants + `_reject_unknown_query_params` helper + 6 endpoint rewires + module policy docstring §3 refresh + `_parse_date_param` calendar validation)
  - core/tests/test_ops_query_param_allowlist_2773.py (new — 22 tests across 4 TestCase classes: 6 allowlist-accept + 8 allowlist-reject + 1 meta-constant + 7 date-validation)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2773 open freshness (retired-pin dispatch to Rigby) — verdict FRESH · SHA e1e9514ac958 matches HEAD (SEVENTH corroboration cycle after PLAYBOOK-7.4.4)
  - S2773 design SIGN + first zoom-out (Rigby, pin pa-c15a7532e20b4fee) — Q1 MODIFY (add machine-stable `code` field); Q2 MODIFY (new test file, not extending auth-regression file); Q3 zoom-out (S2771 rule applied) → 5 substantive concerns: proxy DRY, allowlist uniformity, URLConf lambda tech debt, date-parse bug, health_summary/ops_tool.overview conceptual overlap
  - Chris D-verdict on scope expansion: Option B approved — fold #1 + #2 + #4 into same PR; forward-carry #3 + #5
  - S2773 concrete implementation SIGN (Rigby, same pin) — Q1 PASS on helper signature (B: payload dict + trace_id); Q2 PASS on allowlist location (A: module constants with `_OPS_ALLOWED_PARAMS__<UPPER>` naming); Q3 MODIFY on date-parse "no behavior change" claim (correctness fix, not invisible); Q4 (open-ended) recommended multi-commit-on-branch + squash-merge for reviewability
frozen: true
---

# Ops-Endpoint Query-Param Allowlist + Helper Refactor + Date Fix — Ratification Record

Frozen canonical record of Chris's ratification of the S2773 N18v2 substrate hardening on 2026-07-12. Second consecutive test-shipping session (after S2772 N16 auth-regression). Continues the ops-console substrate hardening arc that emerged from Rigby's S2771 meta-critique. Append-only.

---

## §1. Context

- **Ratification date:** 2026-07-12 (America/Denver operator timezone)
- **Scope:** cross-endpoint substrate hardening + DRY refactor + correctness fix (N18v2 in S2773 candidate menu, scope-expanded from original N18 per Chris D-verdict on Rigby zoom-out).
- **Motivation:** Rigby's S2772 forward-carry #4 (from her S2771 meta-critique #4 refinement) explicitly flagged: "add explicit_query_params allowlist decorator + 400 response for unknown keys, when a second endpoint reaches ≥4 optional params." Trigger already met — `close_ceremony_ledger` had 7 optional params at S2772 close. N18 was the concrete mitigation for that trigger.
- **Ratifier:** Chris (candidate selection at S2773 open: "N18 approved, route joint SIGN through Rigby"; scope-expansion D-verdict same-turn: "B approved, route joint SIGN through Rigby").
- **Seventh cycle after PLAYBOOK-7.4.4 codification:** S2773 open verified FRESH · SHA-match at `e1e9514ac958` (S2772 close). Recycle log top three all N7-enriched with `partial_recycle=false`. N11 PARTIAL_RECYCLE branch remains dormant (correct — no partials in the wild).

---

## §2. Ratified Deliverables

### §2.1 `core/views_ops_console.py` — `_call_ops_tool` helper (Rigby Q3 #1)

Extracted a module-level shared helper:

```python
def _call_ops_tool(
    request,
    payload: Dict[str, Any],
    trace_id: str = 'ops-console',
) -> Dict[str, Any]:
```

Rewires `slo_status`, `failure_signatures`, `health_summary`, `recent_recycles`. Each previously carried a copy of the `_Proxy(OpsHandlersMixin)` boilerplate — same import, same class, same `_handle_ops` dispatch. Now one helper. Signature per Rigby Q1 PASS on the implementation SIGN: takes full payload dict rather than an action-name mini-DSL that would inevitably accrete special cases.

`blocked_agents` reads from the ORM directly and `close_ceremony_ledger` reads from the filesystem — both untouched.

### §2.2 Per-endpoint query-param allowlist (Rigby Q3 #2)

Every ops endpoint declares an `_OPS_ALLOWED_PARAMS__<NAME>` frozenset constant at module level (naming convention per Rigby implementation SIGN Q2 nudge — the shared prefix lets meta-tests enumerate + validate them in bulk). Constants:

| Endpoint | Allowed params |
|---|---|
| `slo_status` | (empty — accepts none) |
| `failure_signatures` | `{window, limit}` |
| `blocked_agents` | (empty) |
| `health_summary` | (empty) |
| `close_ceremony_ledger` | `{limit, session_min, session_max, envelope_only, date_from, date_to, text}` |
| `recent_recycles` | `{limit}` |

New `_reject_unknown_query_params(request, allowed)` helper returns a 400 `JsonResponse` when `request.GET` contains any key not in the allowlist. Called at the top of every endpoint (endpoints that accept no params reject arbitrary keys too — Rigby's "endpoints with no params: reject if request.GET is non-empty" default posture).

### §2.3 400 response body shape (Rigby Q1 MODIFY)

```json
{
  "error": "Unknown query parameter(s)",
  "code": "unknown_query_params",
  "unknown": ["raw", "include_body"],
  "allowed": ["limit", "session_max", "session_min", ...]
}
```

Machine-stable `code` field means downstream tools (frontend, future tests, ops automation) can key off `code == 'unknown_query_params'` without coupling to the English error string. `unknown` and `allowed` are sorted lists for stable diffing.

### §2.4 Module policy docstring §3 refresh

Rule 3 previously said "reject unknown query parameters or ignore them safely." Now says: "Reject unknown query parameters via `_reject_unknown_query_params` with the endpoint's `_OPS_ALLOWED_PARAMS__<NAME>` frozenset. Every endpoint that accepts query params declares an allowlist constant; endpoints that accept none declare an empty frozenset. Unknown params → 400 with `code='unknown_query_params'` and machine-readable `{unknown, allowed}` body. Never evaluate arbitrary strings."

Policy is no longer "on paper" — the helper + constants make enforcement mechanical.

### §2.5 `_parse_date_param` calendar validation fix (Rigby Q3 #4 correctness)

Replaced the digit-only check with `datetime.date.fromisoformat`. Behavior change (per Rigby implementation SIGN Q3 MODIFY — not invisible, but a correctness improvement):

| Input | Before | After |
|---|---|---|
| `2026-07-12` | `'2026-07-12'` | `'2026-07-12'` (unchanged) |
| `2026-99-99` | `'2026-99-99'` (accepted → downstream string compare on garbage) | `None` (filter dropped correctly) |
| `2026-02-30` | `'2026-02-30'` | `None` |
| `2026-7-12` | `None` (unchanged — length check caught it) | `None` (unchanged — fromisoformat requires zero-pad) |
| empty / None / garbage | `None` | `None` (unchanged) |

No callers relied on the old permissive behavior. Downstream `parsed_date < date_from` string comparisons now compare valid ISO dates only.

### §2.6 `core/tests/test_ops_query_param_allowlist_2773.py` — 22 tests (Rigby Q2 MODIFY: new file)

Four TestCase classes:

- **`OpsQueryParamAllowlistAcceptTest`** (6 tests) — every endpoint accepts its documented allowlisted params without returning 400 unknown_query_params.
- **`OpsQueryParamAllowlistRejectTest`** (8 tests) — every endpoint rejects unknown params with 400 + `code='unknown_query_params'`. Documented params are not spuriously listed as unknown. Multi-unknown params all reported. Response body shape locked to `{error, code, unknown, allowed}`.
- **`OpsAllowlistMetaTest`** (1 test) — enumerates the 6 ops URL names, derives expected `_OPS_ALLOWED_PARAMS__<UPPER>` constant name, asserts each is defined on the views module and is a `frozenset`. Prevents silent drift back to pre-S2773 permissive default.
- **`DateParamValidationTest`** (7 tests) — locks the calendar validation contract (invalid month, invalid day, unpadded, empty, None, garbage all return None; valid passes through).

Combined suite (this file + S2772 auth-regression file): **37/37 tests pass in 0.9s**.

---

## §3. What Was NOT Changed

- No frontend edits. `applied_filters` echo from S2771 already surfaces which recognized filters fired; UI does not need to change to consume `code='unknown_query_params'`.
- No changes to the S2772 auth-regression file (`test_ops_auth_regression_2772.py`) — Rigby Q2 MODIFY explicitly kept its charter focused on auth + route inventory.
- No changes to `blocked_agents`'s ORM query (it doesn't dispatch to `ops_tool`, so no helper wire-up needed there — allowlist only).
- URLConf `lambda r: __import__(...)` pattern (Rigby zoom-out #3) — forward-carry.
- `health_summary` vs `ops_tool.overview` conceptual overlap (Rigby zoom-out #5) — forward-carry.

---

## §4. Rigby SIGN Summary

Joint SIGN routed via pin `pa-c15a7532e20b4fee` (label `s2773-ccl-query-param-allowlist`). Three round-trips:

### §4.1 Round 1: Design + zoom-out
- **Q1 (400 body shape):** MODIFY → add machine-stable `code` field. **Adopted.**
- **Q2 (test file placement):** MODIFY → new file, not extending auth-regression file (charter separation). **Adopted.**
- **Q3 (open-ended zoom-out per S2771 rule):** 5 substantive concerns raised on the ops-console arc:
  1. `_Proxy` boilerplate duplicated 4x → extract helper. **Same PR.**
  2. Allowlist policy stated but not uniformly enforced — 5 other endpoints have the same drift risk. **Same PR (expanded scope).**
  3. URLConf `lambda r: __import__(...)` pattern is tech debt. **Forward-carry.**
  4. `_parse_date_param` accepts invalid calendar dates like `2026-99-99`. **Same PR.**
  5. `health_summary` conceptually duplicates `ops_tool.overview`. **Forward-carry.**

### §4.2 Chris D-verdict on scope expansion
- Chris response to my "Option A tight vs Option B expanded" ask: **"B approved."**
- Justification: #1 sets up #2 to be cheap (allowlist enforcement uses the shared helper indirectly), #4 is a real bug already, doing them together maintains the same close-ceremony overhead.

### §4.3 Round 2: Implementation SIGN (concrete plan)
- **Q1 (helper signature):** PASS → payload dict + trace_id. Implementation nudge: `payload.setdefault('trace_id', ...)` if carrying it.
- **Q2 (allowlist location):** PASS → module constants. Naming nudge: `_OPS_ALLOWED_PARAMS__<UPPER_NAME>` uniform prefix for meta-test enumeration. **Adopted.**
- **Q3 (date-parse "no behavior change"):** MODIFY → my claim of invisibility was wrong. Invalid dates currently do participate in string comparison downstream. Correctly framing this as a correctness fix rather than invisible fix.
- **Q4 (commit sequencing):** freeform → multi-commit on branch, squash-merge per repo convention. **Adopted** — 4 clean commits on the branch: helper → allowlist → date fix → tests.

---

## §5. Empirical smoke tests

### §5.1 `python manage.py test core.tests.test_ops_query_param_allowlist_2773 core.tests.test_ops_auth_regression_2772`
- Result: **37/37 PASS in 0.907s.**
- 22 new N18v2 tests (allowlist accept/reject, meta-constant, date validation).
- 15 S2772 auth-regression tests still green — no regression from helper refactor or allowlist wire-up.

### §5.2 Django shell smoke on `_parse_date_param`
- `'2026-07-12'` → `'2026-07-12'` (valid, unchanged behavior)
- `'2026-99-99'` → `None` (calendar-invalid, previously accepted as valid)
- `'2026-02-30'` → `None` (calendar-invalid, previously accepted)
- `'2026-7-12'` → `None` (unpadded, unchanged behavior)
- `''`, `None`, `'not-a-date'` → `None` (unchanged behavior)

### §5.3 Auth-regression suite still enforces (regression protection)
Rigby's meta-critique from S2771 stays enforced — the S2772 auth-regression tests + route-inventory guard don't touch the N18v2 code but their continued green run confirms no accidental auth downgrade from decorator-order shuffling during the refactor.

---

## §6. Post-ratification bindings

- **Head at ratification:** filled at merge.
- **Merged PR:** filled at merge.
- **Workspace mirrors (S2754a twin-canonical rule):**
  - Governance envelope mirror → `RUR-C1 Tenant Boundary Lockdown` workspace `fcd7e683-3bfe-4d35-9704-0e54dd587ea1`.
  - Content mirror → same workspace.
- **PLAYBOOK-7.4.4 dogfood:** `make recycle-all` invoked post-merge — eighth consecutive cycle where the constitutional rule fires.
- **`session_tool.retire` at close:** fourth consecutive `force=true` required per `feedback_session_tool_retire_needs_force_true` memory rule.

---

## §7. Forward carry

Rigby S2773 zoom-out #3 (URLConf lambda tech debt) and #5 (health_summary vs ops_tool.overview overlap) remain deferred:

- **#3 URLConf lambda `__import__` pattern.** Every ops endpoint in `core/urls.py` registers via `lambda r: __import__('core.views_ops_console', fromlist=[...]).name(r)`. Functional but harder for static tooling. **Trigger for cleanup:** next arc that touches `core/urls.py` for ops registration; refactor to direct import in same PR.
- **#5 `health_summary` overlaps `ops_tool.overview`.** Two paths compose the same base signals. Currently intentional (UI tile shape ≠ overview response shape), but if drift starts between them, consolidate. **Trigger for consolidation:** first bug where the UI tile and `ops_tool.overview` diverge on a factual claim.

Both have explicit triggers, not "someday."

---

## §8. Meta-observation on the SIGN discipline

Third consecutive session applying the S2771 workflow rule (open-ended zoom-out ask per Rigby SIGN):
- **S2771:** rule proposed after Chris observed drift.
- **S2772:** rule applied first time. Rigby produced 7 substantive concerns; 3 shipped same-PR, 4 forward-carry with explicit triggers, 1 escalated to Chris.
- **S2773:** rule applied second time. Rigby produced 5 substantive concerns; 3 shipped same-PR (expanded scope after Chris D-verdict), 2 forward-carry with explicit triggers.

The pattern is stable: zoom-out asks produce 4–7 concerns per session; roughly half ship same-PR (small enough), the rest carry forward with explicit trigger criteria. The rule is doing its job.
