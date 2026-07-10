---
title: "I-0301 Scoping — HTTP + AllowAny Surface Remediation + Failure-Data Safety Contract"
status: active
authority: arc-scoping
session_added: 2742
session_scoping_ratified: 2742
scoping_ratification_date: 2026-07-10
scoping_ratifier: chris
last_updated: 2026-07-10
arc_id: I-0301
parent_campaign: RUR-C1 (Tenant Boundary Lockdown)
parent_program: RUR (Real User Readiness)
parent_program_doc: docs/research/implementation/real_user_readiness/CAMPAIGN.md
parent_program_ratification: docs/research/implementation/RATIFICATION_2026-07-10_real_user_readiness.md
parent_workspace: "Real User Readiness Campaign"
parent_workspace_id: 638e9e90-47b4-4bd4-a872-bf16181cf3b5
arc_workspace: "RUR-C1 Tenant Boundary Lockdown"
arc_workspace_id: fcd7e683-3bfe-4d35-9704-0e54dd587ea1
sibling_arcs:
  - I-0302 (Object-Level Authorization) — waits for I-0301 safety contract SIGN
  - I-0303 (Async Tenant-Boundary Enforcement) — waits for I-0301 safety contract SIGN
head_at_scoping: 0825df46
current_phase: Phase 3 (HTTP Remediation) — UNBLOCKED by Phase 2 close 2026-07-10 (Chris ratified frozen safety contract); pending Chris authorization to open. First code-touching phase.
phase_1_audit_ledger_deliverable: 1ca36f84-ae40-415c-b482-768415d13fd9  # workspace fcd7e683
phase_1_closed: 2026-07-10 (Rigby SIGN-PASS on audit ledger; no material amendments)
phase_2_closed: 2026-07-10 (Chris ratified frozen safety contract; downstream unlocks per §13)
phase_2_safety_contract: docs/research/implementation/tenant_boundary_lockdown/failure_data_safety_contract.md
phase_2_ratification_record: docs/research/implementation/RATIFICATION_2026-07-10_i0301_safety_contract.md
sign_history:
  - session: 2742
    reviewer: rigby
    verdict: SIGN-with-amendments (10 focus areas; ~10 non-material applied directly; 3 material amendments applied post-SIGN and escalated to Chris per §12 escalation rule)
scoping_ratification_note: Chris approved all 3 material amendments in the S2742 return. I-0301 scoping is ratified as amended. Phase 1 (Audit Ledger) is unblocked. Implementation code (Phase 3) still requires Phase 2 safety-contract SIGN + Chris ratification of the frozen contract.
---

# I-0301 Scoping — HTTP + AllowAny Surface Remediation + Failure-Data Safety Contract

> **Arc-scoping document.** Answers Chris S2742 §8 required scope outcomes. Implementation begins only after Rigby scope SIGN + Chris ratification of this scoping. Wave 1 authorization is permission to scope this arc, NOT permission to begin remediation.
>
> Parent invariant: **RUR-C1 closes only when I-0301 + I-0302 + I-0303 pass the shared cross-tenant regression suite.** Closure of I-0301 alone is NOT closure of RUR-C1.

---

## §1. Arc Objective

Two objectives, both mandatory for I-0301 close:

### Objective A — Remediate the HTTP + AllowAny surface

Audit and remediate every HTTP endpoint that presents a cross-tenant data exposure risk at current HEAD. This is the entry point for external users touching the platform.

### Objective B — Establish the Failure-Data Safety Contract

Publish the durable contract that governs what user-facing error surfaces may expose. Rigby SIGN-confirms the contract. Once signed, this contract is the opening precondition for RUR-C2 (Async State + Fail-Loud + Traceability) — I-0302 and I-0303 also gate on it.

**Objective B is the higher-leverage of the two.** It unblocks three downstream arcs and defines the substrate every failure surface will conform to.

---

## §2. Required Scope Outcomes (Chris S2742 §8)

Per the ratified CAMPAIGN, this scoping must produce implementation-driving answers to:

- **§2.1** What is the current production default permission class?
- **§2.2** How many endpoints are explicitly `AllowAny` at current HEAD?
- **§2.3** Which endpoints inherit permissions implicitly?
- **§2.4** Which public endpoints are intentionally public?
- **§2.5** Which public endpoints expose user-owned / workspace-owned / filesystem-derived / operational / mutation-capable data?
- **§2.6** Which endpoints are mocks / dormant / dead / debug-only / future-dangerous?
- **§2.7** Which endpoints require authentication but not object authorization?
- **§2.8** Which endpoint patterns share a common fix?
- **§2.9** Which fixes risk breaking legitimate public functionality?
- **§2.10** What HTTP error schema will satisfy the failure-data safety contract?
- **§2.11** Which fields are safe for users?
- **§2.12** Which fields are operator-only?
- **§2.13** How will support codes map to protected diagnostic context?
- **§2.14** What regression test snapshot covers the HTTP surface?
- **§2.15** How will new endpoints automatically enter the future test denominator?
- **§2.16** What changes are strictly I-0301 vs deferred to I-0302 or I-0303?

Each subsection below answers one or more of these. Where evidence is preliminary (scoping-phase snapshot), that is noted; full remediation occurs at implementation.

---

## §3. Current-HEAD Evidence Pass

### §3.1 — DRF Default Permission Class (§2.1)

Evidence: `core/settings.py:712-714`

```python
'DEFAULT_PERMISSION_CLASSES': [
    'rest_framework.permissions.IsAuthenticated',  # Require authentication by default
],
```

**Verdict:** DRF default is secure. Views without explicit `permission_classes` inherit `IsAuthenticated`. This is the correct baseline. `core/security_validator.py:169-171` also flags any drift to `AllowAny` in the default at settings-validation time.

**Implication:** the risk surface is exclusively views that OVERRIDE the default with `AllowAny`, not views that omit the field.

### §3.2 — AllowAny Endpoint Denominator at HEAD (§2.2)

HEAD: `0825df46` (main branch after ratification + cascade merges).

Snapshot at scoping time:

```
Total STATIC AllowAny occurrences: 26
Files: 8
```

**Denominator qualifier (Rigby SIGN §1 material amendment):** the 26 count is a **lower bound**. It captures static `permission_classes = [AllowAny]` declarations found by grep. It does NOT capture:

- DRF viewsets with `get_permissions()` returning `AllowAny` dynamically
- Action-level overrides using indirection (e.g., `PUBLIC_PERMS = [AllowAny]` referenced elsewhere)
- Non-DRF Django views that are effectively public without touching `AllowAny` at all

**Required audit-phase task (Phase 1 addition):** dynamic-permission audit — grep for `get_permissions`, `permission_classes_by_action`, and any indirect `AllowAny` references. Any endpoints surfaced by that audit enter the denominator and are classified per §4.

| File | Count | Notes |
|---|---|---|
| `ai_core/api/autonomous_system_api.py` | 4 | Autonomous revenue system; currently mock/stub responses |
| `intelligence/views.py` | 7 | Includes ActionPlanPersistenceView (line 179) which reads user action plans from filesystem globs |
| `sports/views.py` | 2 | Both self-labeled "Allow public read access" |
| `core/views_public_intelligence.py` | 1 | Filename implies public intent |
| `core/views_nervous.py` | 6 | Nervous-system diagnostic views |
| `core/views_content_learning.py` | 4 | Self-labeled inline: "Public for debugging, change to IsAuthenticated in production" |
| `core/views_public_changelog.py` | 1 | Filename implies public intent |
| `core/views/agents.py` | 1 | Single `@action(permission_classes=[permissions.AllowAny])` decorator |

**Verdict:** count matches the S2740 snapshot of 26. Chris's §8 directive to "confirm the actual endpoint denominator rather than trusting the old count of 26" — confirmed unchanged at HEAD.

**Recompute at implementation open** (per §5 regression test denominator design): the snapshot list will be re-derived immediately before the audit ledger opens, so any drift between now and remediation open is caught.

### §3.3 — Implicit Inheritance Risk (§2.3)

There are ~74 view classes with explicit `permission_classes`. All remaining DRF view classes inherit `IsAuthenticated` from the default. Given the secure default, implicit inheritance is a positive — views that omit the field are safe by construction.

**Sub-risk:** function-based views using `@api_view` decorators. They also inherit the default, so same reasoning applies. Confirmed no `@api_view` with `AllowAny` unless explicitly decorated (which would show up in the grep above).

**No further audit action required for implicit inheritance** — Objective A remediation focuses on explicit `AllowAny` overrides only.

---

## §4. Endpoint Classification Framework (§2.4 – §2.7)

Every one of the 26 `AllowAny` occurrences will be classified into exactly one of four buckets during the audit ledger phase:

### Bucket A — Intentionally Public

The endpoint should remain `AllowAny` because it exposes only genuinely public data (public changelog, health check, marketing page) or is a documentation / debug tool with no data exposure.

**Remediation action:** none. Add an in-code justification comment linking to this scoping.

**Preliminary candidates for Bucket A** (subject to per-endpoint review at implementation):
- `core/views_public_changelog.py:104` (filename implies public intent)

### Bucket A2 — Public-but-Authenticated-by-Other-Means (Rigby SIGN §2)

Separate named sub-bucket to prevent reviewers from accidentally approving truly-open endpoints. Endpoint is:
- Protected by HMAC signature check
- Protected by IP allowlist
- Protected by fleet-internal shared secret
- Protected by another out-of-band mechanism that DRF permission_classes doesn't see

**Remediation action:** verify the alternate auth mechanism is active + tested. Add in-code justification comment naming the alternate auth. If the alternate is broken or missing, this endpoint drops into Bucket B.

**Preliminary candidates for Bucket A2:** unknown at scoping time; identified during Phase 1 audit.

### Bucket B — Temporarily Public (Remediation Required)

The endpoint was labeled public for legitimate short-term reasons (debugging, mock stub, pending integration) but exposes data or actions that should be authenticated.

**Remediation action:** replace `AllowAny` with `IsAuthenticated` + appropriate object-level check (the object-level check work moves to I-0302 if scope-material).

**Preliminary candidates for Bucket B** (subject to per-endpoint review at implementation):
- `core/views_content_learning.py:30, 82, 110, 156` (self-labeled "Public for debugging, change to IsAuthenticated in production")
- `intelligence/views.py:179` (`ActionPlanPersistenceView` reading filesystem globs — data exposure)

### Bucket C — Obsolete / Dead / Debug-Only

The endpoint is:
- No longer wired to any active caller
- A dev-only demonstration route
- A future-dangerous mock/stub for something not yet built

**Remediation action:** delete the route, or gate behind `DEBUG=True` settings check, or move to a separate debug-only URL include.

**Evidence requirement for Bucket C classification (Rigby SIGN §5):** classification into C requires **proof of no prod callers** OR a documented debug-gate fallback. Preliminary suspicion is not sufficient — a caller-graph check is mandatory before deletion. If evidence is unavailable, the endpoint drops into Bucket D (Ambiguous).

**Preliminary candidates for Bucket C** (subject to caller-graph evidence at implementation):
- `ai_core/api/autonomous_system_api.py:13, 45, 106, 124` (currently mock; may be dead code — requires caller-graph proof before deletion)
- `core/views_nervous.py` (6 occurrences; diagnostic views — Rigby SIGN §4 flags these as risk of migrating from Bucket C to Bucket B if they leak workspace IDs, task IDs, queue depths, environment, or paths)

### Bucket D — Ambiguous, Requires Evidence

The endpoint's intent is unclear from code alone. Requires:
- Caller-graph analysis
- Rigby operational-memory query
- Cross-check against handoff / campaign closeout documents

**Remediation action:** produce an evidence bundle per-endpoint before reclassifying into A / A2 / B / C.

**Preliminary Bucket D candidates (Rigby SIGN §3 flag):**
- `core/views_public_intelligence.py:102` — filename suggests public intent BUT "intelligence" often aggregates spider / KB / ops signals that are tenant-derived. Requires evidence bundle showing content is static + non-tenant-derived before it can move to Bucket A.

---

## §5. Regression Test Denominator + Verification Approach (§2.14, §2.15)

### §5.1 — Test Denominator Snapshot

At implementation open, `tests/security/endpoints_covered.txt` is created with a pinned snapshot of user-facing HTTP endpoints:

- All routes in `core/urls*.py` and per-app `urls.py` files, resolved to their view class / function
- Every route deriving from a `ViewSet` / `APIView` with either `IsAuthenticated`, `IsAuthenticatedOrReadOnly`, or a stricter permission class
- Every route with `AllowAny` that lands in Bucket A (Intentionally Public) — these are tested to VERIFY they leak nothing tenant-specific

The snapshot is committed. At CI time, a route-list generator re-derives the current denominator; if new routes are added and not present in the snapshot, CI fails until the snapshot is updated + reviewed.

### §5.2 — Regression Suite Shape

`tests/security/test_cross_tenant_regression.py` exercises the pinned snapshot:

- For each authenticated endpoint: user-A logs in, requests user-B's resources (by ID probe or list-endpoint sweep). Expected: `403` / `404` / empty result. Any success = fail.
- For each Bucket A public endpoint: response must not vary by session cookie / auth header. Response must not include user_id, workspace_id, or session-specific data.
- For each Bucket A2 endpoint: the alternate auth mechanism (HMAC/IP/etc.) must fire; requests with invalid signatures must fail.
- For each error path: response conforms to the failure-data safety contract (see §6). No stack traces, no `Exception: <tenant-name>` strings, no raw ORM error messages leaking foreign-workspace names.

**Additional attack modes (Rigby SIGN §7):**
- **List vs detail probing.** user-A calls `GET /api/foo/` (list) then `GET /api/foo/<user-B-uuid>/` (detail). Both must reject.
- **Mutation methods.** user-A `POST` / `PATCH` / `DELETE` against user-B rows. All must reject.
- **Pagination + count leakage.** user-A calls list endpoint with pagination — response `count`, `next`, `previous` must reflect user-A's scope only, not global counts.
- **Cross-tenant create-then-fetch.** user-A creates row → user-B tries to fetch by UUID. Must reject.
- **IDOR via URL manipulation.** replace path segments with foreign UUIDs; must reject.
- **Field-projection probing.** attempt to specify foreign fields in query params / graph-like filters; must not expose.

CI-blocking: any failure blocks the PR that introduced it.

### §5.3 — Common-Fix Patterns (§2.8, §2.9)

Preliminary common-fix patterns identified during scoping:

- **Pattern 1:** views with `AllowAny` + comment "Public for debugging" → straight replace with `IsAuthenticated`. Ownership of returned data must be verified separately (moves to I-0302 if the view returns user-owned data).
- **Pattern 2:** mock/stub views (Bucket C) → gate behind `DEBUG=True` or delete outright. If any prod call site depends on the mock returning static data, that's a bug and gets its own ticket.
- **Pattern 3:** DRF `@action` decorators with `permission_classes=[permissions.AllowAny]` → inspect per-action whether the action returns owned data; if yes, remove the override.

**Legitimate public functionality NOT to break:** health checks, public changelog, marketing routes, docs endpoints, HMAC-authenticated fleet endpoints. Bucket A audit catches these.

---

## §6. Failure-Data Safety Contract (§2.10, §2.11, §2.12, §2.13)

**This is the load-bearing deliverable of I-0301.** Once Rigby SIGN-confirms this contract, RUR-C2 may open in parallel with I-0302 + I-0303 remediation.

### §6.1 — Contract Statement (draft; subject to Rigby SIGN)

**User-facing HTTP error responses SHALL emit ONLY the following fields:**

```json
{
  "support_code": "<opaque short string, e.g. RUR-XXXX-YYYY>",
  "reason_code": "<enumerated, safe-by-design, e.g. 'workspace_not_found'>",
  "human_message": "<user-appropriate copy, e.g. 'That workspace isn\\'t accessible'>",
  "retryable": true | false,
  "terminal_state": "FAILED" | "CANCELLED" | "DENIED" | ...,
  "timestamp": "<ISO 8601 UTC, optional>"
}
```

**User-facing HTTP error responses SHALL NOT expose:**

- Foreign-workspace data (any field derived from another workspace's row)
- Raw model payloads (LLM prompt, LLM response, tool call args, tool call output)
- User prompts or conversation contents unless explicitly classified as safe
- Filesystem paths (absolute or relative — `core/tasks.py` leaks, `workspaces/*` leaks, etc.)
- Secrets or credentials (API keys, session tokens, HMAC secrets, hashed values)
- Internal stack traces (Python traceback, Django ORM error paths)
- Raw exception values containing tenant data (`Exception: workspace_id=<foreign-uuid> denied`)
- **Free-form `exception_message` in any user-facing surface, even sanitized** (Rigby SIGN §6). If the underlying exception was raised inside our code, the reason_code enum + safe human_message replaces it. Sanitization is a footgun class we don't attempt.
- Unrestricted serialized objects (`repr(obj)`, `str(model_instance)`)
- Internal provider request bodies (OpenAI / Anthropic request payloads)
- **Correlation identifiers that could enable cross-tenant inference if globally visible** (Rigby SIGN §6). `trace_id` in particular MUST NOT be surfaced to the user if the ID is globally visible across tenants. Users receive `support_code` only; operators trace via `support_code → trace_id` in the tenant-scoped operator envelope.

### §6.2 — Operator-Only Diagnostic Envelope

Alongside the user-facing envelope, the system produces an **operator-only diagnostic envelope** at the same failure event:

```
OpsRunEvent (tenant-scoped write):
- support_code: <same as user-facing>
- trace_id: <propagated end-to-end>
- reason_code: <enumerated>
- exception_class, exception_message: <internal, full detail>
- request_context: {user_id, workspace_id, endpoint, http_method, ...}
- provider_context: {model, tokens, cost, ...} — where applicable
```

**Access control on operator diagnostics (Rigby SIGN §6 material amendment — expanded):**

- `trace_lookup` (see RUR-C2 exit criterion E9) is **operator-only AND tenant-scoped**: operators can only retrieve traces for tenants / workspaces they are authorized to support.
- No workspace-B operator can see workspace-A trace details, even by support_code.
- `trace_lookup` **must never return raw foreign identifiers** in a form that an operator could paste back to a user to enable exfiltration (e.g., returning a foreign workspace UUID to an alpha user who then queries it).
- If a "support role" concept exists in the auth model, name it as the guard. If it does not exist at implementation time, the tenant-scope requirement is enforced **procedurally** at the alpha level (documented ops runbook + operator agreement) with a code enforcement plan tracked as a follow-on.
- Operator dashboards similarly read `OpsRunEvent` rows filtered by the operator's tenant access.
- The `support_code → trace_id → full context` chain respects the tenant boundary at every hop.

**Escalation flag:** this access-control specification is material and refines the ratified CAMPAIGN E9 exit criterion. It does NOT contradict E9; it defines E9's tenant-scope contract explicitly. Recorded in §12 (post-SIGN material amendments) for Chris review before scoping ratification.

### §6.3 — `support_code` Format + Mapping (§2.13)

Draft format: `RUR-<component>-<yyMMdd>-<opaque-hex>`, e.g. `RUR-AUTH-260710-a4f2`.

`support_code` is stable across the failure event (same code returned to user and stored in `OpsRunEvent`). Operator uses `python manage.py trace_lookup <support_code>` (see RUR-C2 exit criterion E9) to retrieve the operator-diagnostic envelope subject to their tenant access.

**Uniqueness:** collision probability is negligible for the alpha cohort scale. If we ever need stronger guarantees, prefix bytes can be widened.

**Format privacy assessment (Rigby SIGN §6):** the `<yyMMdd>` date component reveals rough incident timing to any recipient of the code. This is acceptable for gated alpha because it does NOT expose cross-tenant data — only internal taxonomy + rough day. Optional future hardening: drop the date component or replace with week-of-year, deferred to post-alpha.

### §6.4 — Component Coverage

The contract applies to:

- Every DRF view returning a non-2xx response
- **Every non-DRF Django view returning a non-2xx response** (Rigby SIGN §6 — the contract must not over-claim DRF-only coverage; middleware / template / streaming responses are equally in-scope for the safety contract even if enforcement uses a different mechanism)
- **Every Django middleware 403 / 404 / 500 template response** — Django's default templates ARE generic, but our custom middleware overrides must conform to the same permitted/prohibited field list
- **Every streaming response (SSE, chunked)** where a per-chunk error can surface to the user
- **Every async status endpoint** that surfaces task failure reason back to the user (see RUR-C2 for the async task path itself)
- Every WebSocket close code >= 4000 (also see RUR-C5 for consumer coverage)
- Every async task failure surfaced to the user (see RUR-C2 for the async path)
- Every permission denial (401 / 403)

**Explicit scope EXCLUSION:** static 500 pages generated by Django's own default error middleware (those are already generic and safe by design — but we verify they leak nothing at test time).

**Success-path leakage note (Rigby SIGN §6):** the safety contract governs ERROR envelopes. However, list/count endpoints in the SUCCESS path can still leak cross-tenant data via counts, next-page links, or aggregate stats. Those leaks are caught by the §5.2 regression suite ("succeeded-but-wrong" attack modes), NOT by the safety contract enforcement layer. The distinction matters — do NOT try to make the safety contract cover success responses.

### §6.5 — Enforcement Approach (Rigby SIGN §6 material amendment — corrected)

**Multi-layer enforcement (corrected — the previous single-layer DRF-only claim over-scoped):**

1. **DRF-level:** `REST_FRAMEWORK.EXCEPTION_HANDLER` catches DRF-raised exceptions and produces the user-facing envelope. Covers DRF view code paths only.
2. **Django middleware-level:** a custom exception middleware catches non-DRF Django view exceptions (plain function views, streaming responses, non-DRF error paths) and applies the same envelope shape.
3. **Template-level:** custom `403.html` / `404.html` / `500.html` templates (if any) conform to the permitted/prohibited field list — verified at test time. Django defaults are already generic.
4. **Test-level:** `test_cross_tenant_regression.py` fires deliberately-broken requests + verifies response shape via schema assertion. Any response carrying a prohibited field fails the test.

The multi-layer approach means the safety contract IS actually enforceable across the platform's HTTP surface, not just DRF views. The previous single-layer draft over-claimed coverage.

---

## §7. Scope Boundaries — What Belongs to I-0301 vs I-0302 vs I-0303 (§2.16)

Per Chris Q2 D-verdict, RUR-C1 has three distinct child arcs. Scope discipline matters — implementation drift across arcs is a known failure mode.

### §7.1 — In-scope for I-0301

- **HTTP** endpoint audit + classification for the AllowAny surface
- **HTTP** remediation of Buckets B / C endpoints (replace `AllowAny` with `IsAuthenticated`, delete/gate obsolete routes)
- Failure-data safety contract definition + Rigby SIGN
- Base DRF exception handler + response envelope
- `support_code` format + generation
- Regression test scaffolding (`endpoints_covered.txt` snapshot + `test_cross_tenant_regression.py` skeleton)
- Coverage denominator machinery (new-route detection at CI time)
- **Minimal safe queryset scoping (Rigby SIGN §7):** for endpoints in Bucket B where the response obviously returns user-owned rows, I-0301 remediation MAY include the queryset scoping to filter by workspace/user context (e.g., `.filter(workspace_id=request.user.workspace)`). This prevents the boundary-leak class where flipping `AllowAny → IsAuthenticated` leaves the response returning all users' data to any authenticated caller. Full object-level authorization policy (Meta.permissions, per-model leakage tests) stays in I-0302.

### §7.2 — Deferred to I-0302 (Object-Level Authorization)

- Adding `Meta.permissions` custom classes to Deliverable / Initiative / ChatConversation / AgentExecution / Document
- Per-model queryset scoping proofs (`filter(workspace_id=request.user.workspace)` audits)
- Per-model leakage tests (user-A queries user-B's model by ID)
- Serializer-level ownership checks

I-0302 opens after §6 safety contract is Rigby-SIGN-confirmed.

### §7.3 — Deferred to I-0303 (Async Tenant-Boundary Enforcement)

- Task-payload workspace scope re-verification against DB row ownership
- Rejecting task dispatches without trusted user/workspace identity
- User-A → user-B negative tests on Celery task boundaries

I-0303 opens after §6 safety contract is Rigby-SIGN-confirmed.

### §7.4 — Deferred to RUR-C5 (Channels Auth Hardening)

- WebSocket consumer `connect()` authentication audit (all 17 consumers)
- Group name workspace scoping

RUR-C5 opens after I-0301 audit output feeds consumer classification (Wave 2).

### §7.5 — Explicit Non-Goals for I-0301

- Do NOT rewrite view-inheritance hierarchies
- Do NOT change DRF version or auth backend
- Do NOT introduce a new permission framework
- Do NOT refactor URL routing globally
- Do NOT touch existing `IsAuthenticated`-guarded endpoints (unless a specific defect surfaces)
- Do NOT change frontend behavior (frontend safe-envelope consumption is C2 scope for the async path; for HTTP path, frontend already handles standard DRF error responses)

---

## §8. Implementation Approach + Milestones (draft; subject to Rigby SIGN)

Not implementation authorization. This is scoping-level shape of what implementation would look like when authorized.

### Phase 1 — Audit Ledger (target: 1 session)

- Materialize the endpoint audit ledger as a workspace deliverable under `fcd7e683`
- Per-endpoint: file / line / current permission_class / preliminary bucket / notes
- Bucket A entries get an in-code justification comment drafted (not yet applied)
- Bucket B / C / D entries flagged for Phase 2

### Phase 2 — Safety Contract Draft + Rigby SIGN (target: 1 session)

- Publish the failure-data safety contract as a durable doc (probably `docs/research/implementation/tenant_boundary_lockdown/failure_data_safety_contract.md`, frozen post-SIGN)
- Rigby SIGN pass on the contract itself
- **On Rigby SIGN + Chris ratification of the contract, RUR-C2 / I-0302 / I-0303 unblock (per §9.1 of the parent CAMPAIGN)**

### Phase 3 — HTTP Remediation (Bucket B + C) (target: 2–3 sessions)

- Replace `AllowAny` with `IsAuthenticated` for Bucket B endpoints
- Delete or `DEBUG`-gate Bucket C endpoints
- Regression test scaffolding lands + first tests pass
- Base DRF exception handler + response envelope lands
- Every PR includes the new probe against `test_cross_tenant_regression.py`

### Phase 4 — Coverage Denominator Machinery (target: 1 session)

- CI-time route-list generator
- Snapshot drift detection
- New-route-added → CI fail unless snapshot updated

### Phase 5 — I-0301 Close

- All 26 `AllowAny` remediated per bucket
- Regression suite green + CI-blocking
- Coverage machinery live
- I-030199 close doc written + ratified

RUR-C1 parent continues to wait on I-0302 + I-0303. Close of I-0301 is NOT close of RUR-C1.

---

## §9. Cross-References

- Parent campaign: [`../real_user_readiness/CAMPAIGN.md`](../real_user_readiness/CAMPAIGN.md)
- Parent ratification: [`../RATIFICATION_2026-07-10_real_user_readiness.md`](../RATIFICATION_2026-07-10_real_user_readiness.md)
- Sibling arcs: `I-0302_scoping.md` (not yet opened), `I-0303_scoping.md` (not yet opened)
- Downstream unlock: RUR-C2 (Async State + Fail-Loud + Traceability) opens after §6 safety contract SIGN
- Parent workspace: `638e9e90-47b4-4bd4-a872-bf16181cf3b5` (`Real User Readiness Campaign`)
- Arc workspace: `fcd7e683-3bfe-4d35-9704-0e54dd587ea1` (`RUR-C1 Tenant Boundary Lockdown`)

---

## §10. Open Scope Questions Requiring SIGN + Chris Ratification

1. **§6.3 support_code format** — is `RUR-<component>-<yyMMdd>-<opaque-hex>` OK, or a different shape preferred?
2. **Bucket A preliminary candidates** — Rigby has cross-session operational memory; would she flip any of the preliminary Bucket A candidates?
3. **`ai_core/api/autonomous_system_api.py`** — currently mock; delete outright vs debug-gate vs replace with `IsAuthenticated`? The 4 endpoints there are the strongest Bucket C candidates.
4. **Contract publication location** — `docs/research/implementation/tenant_boundary_lockdown/failure_data_safety_contract.md` as a separately-ratified frozen doc, or a section inside `I-030199_close.md` when the arc closes? My lean: separate doc, ratified at Phase 2 close.
5. **Coverage denominator machinery** — build as part of I-0301 (Phase 4) or defer to a follow-on ops arc? My lean: build here, because without it the regression suite has no way to catch future drift.

---

## §11. What This Scoping Does + Does Not Authorize

**This scoping is a proposal to Chris + Rigby. It DOES NOT:**

- Authorize remediation of any endpoint
- Authorize the failure-data safety contract (that requires Rigby SIGN at Phase 2 open)
- Open I-0302 or I-0303 (those wait for §6 contract SIGN)
- Open RUR-C2 (same wait)
- Close any part of RUR-C1
- Modify code

**This scoping DOES:**

- Confirm the endpoint denominator at HEAD (26; unchanged from S2740 snapshot)
- Confirm the DRF default is secure (`IsAuthenticated`)
- Define the four-bucket classification framework
- Define the failure-data safety contract shape (subject to SIGN)
- Define the regression test denominator + verification approach
- Define the scope boundary between I-0301 / I-0302 / I-0303
- List open questions requiring SIGN + ratification

**Next step:** Rigby scope SIGN on this document. Any material amendment goes back to Chris. On SIGN + ratification, Phase 1 (Audit Ledger) opens.

---

## §12. Rigby Scope SIGN Outcome + Post-SIGN Amendments Applied

### Rigby SIGN cycle (S2742)

Ten-focus-area pressure-test conducted 2026-07-10. Verdict summary:

| Focus | Rigby verdict | Fold-back applied? |
|---|---|---|
| §3.2 denominator | WEAK — 26 is lower bound | Yes — labeled "static AllowAny occurrences"; dynamic-permission audit added to Phase 1 |
| §4 four-bucket framework | PASS + missing distinction | Yes — Bucket A2 added |
| §4 Bucket A candidates | WEAK on `public_intelligence` | Yes — moved to Bucket D pending evidence |
| §4 Bucket B candidates | PASS but likely incomplete | Documented; expect nervous views to migrate B/C after evidence |
| §4 Bucket C stubs | WEAK — needs evidence-driven req | Yes — evidence requirement added; caller-graph check mandatory |
| §6 Failure-Data Safety Contract | WEAK — several tightenings | Yes — prohibit free-form exception_message; prohibit cross-tenant-inferable trace_id; support_code date OK for alpha; component coverage expanded; success-path leakage distinction added |
| §5.2 regression suite | Add attack modes | Yes — list/detail, mutation, pagination, IDOR, field projection added |
| §7 scope boundaries | PASS + minimal safe queryset scoping | Yes — I-0301 authorized to do minimal queryset scoping where obviously required |
| §8 phase plan | WEAK — timeboxing | Documented; Phase 2 may split into 2 sessions if contract needs more iteration |
| §10 open questions | 2 need-now, 3 can-defer | Documented in this §12 (material amendments) |

### Material amendments applied post-SIGN (require Chris review before scoping ratification)

Per Chris S2742 §4 escalation rule, the three items below refine hard gates / Wave 1 authorization contract boundaries. They are applied in-doc but flagged for Chris D-verdict:

1. **Enforcement layering correction (§6.5):** the earlier single-layer DRF-only claim over-scoped the safety contract's actual coverage. Corrected to multi-layer (DRF handler + Django middleware + template + test) so that the contract IS actually enforceable across the full HTTP surface, not just DRF views.
2. **trace_lookup tenant-scoped access rule (§6.2):** operator access to `trace_lookup` is not only "operator-only" — it must also be tenant-scoped. Refines E9 exit criterion in the ratified CAMPAIGN without contradicting it. At alpha level, procedural enforcement is acceptable if code-level RBAC isn't yet in place.
3. **Denominator lower-bound qualifier (§3.2):** 26 is a lower bound. Phase 1 must include a dynamic-permission audit step (get_permissions, action-level overrides, etc.).

**None of the three material amendments change a D-verdict, campaign scope (RUR-C1–C7), dependency graph, hard gate (G1–G8), or Wave 1 authorization (permission to scope I-0301 only, not to implement).** They refine implementation shape within the ratified constitutional envelope.

**Chris scoping-ratification decision required:** approve as amended vs amend further.

**Chris D-verdict (2026-07-10, S2742 return):** **APPROVE ALL 3 MATERIAL AMENDMENTS.** I-0301 scoping is ratified as-amended. Phase 1 (Audit Ledger) is unblocked. Implementation code (Phase 3) still requires Phase 2 safety-contract SIGN + Chris ratification of the frozen contract before it opens.

### Non-material amendments applied directly

Per Rigby's allowance, applied without Chris escalation:
- Bucket A2 named sub-bucket
- Bucket D `public_intelligence` demotion
- Bucket C caller-graph evidence requirement
- support_code privacy conclusion (§6.3)
- Component coverage additions (§6.4 middleware, streaming, async status)
- Success-path leakage distinction (§6.4)
- Prohibit free-form exception_message
- Prohibit cross-tenant-inferable trace_id
- §5.2 additional attack modes
- Minimal safe queryset scoping allowance in I-0301 scope (§7.1)

---

## §13. Phase State Ledger

Live tracker of I-0301 phase progress. Updated as each phase opens / closes.

| Phase | Status | Opens on | Closes on |
|---|---|---|---|
| **Phase 1 — Audit Ledger** | **CLOSED 2026-07-10** — Rigby SIGN-PASS on ledger deliverable `1ca36f84-ae40-415c-b482-768415d13fd9`; no material amendments; denominator 27 (26 static + 1 dynamic); bucket tally A=2 / A2=2 / B=12 / C=4 (preliminary) / D=7 | Chris scoping ratification ✅ | Audit ledger materialized + Rigby ledger SIGN ✅ |
| **Phase 2 — Safety Contract Draft + Rigby SIGN + Chris Ratification** | **CLOSED 2026-07-10** — Rigby SIGN-WITH-EDITS (11/12 PASS, 1 material amendment TIGHTENING §3.2 applied); Chris ratified frozen contract. Contract lives at `failure_data_safety_contract.md`, `frozen: true`. Ratification record `RATIFICATION_2026-07-10_i0301_safety_contract.md`. | Phase 1 close ✅ | Contract frozen + ratified ✅; downstream unlocks in effect |
| **Phase 3 — HTTP Remediation** | **OPEN 2026-07-10** — Stage 1 SHIPPED (PR #3085 substrate + CI); Stage 2a SHIPPED (4 content_learning endpoints remediated); Stage 2b PENDING (7 intelligence + 1 agents; needs Rigby SIGN on filesystem-vs-DB architecture); Stage 2c NEW FOLLOW-ON (envelope-shape unification — `APIResponseEnvelope` migration to safety-contract shape; cross-platform blast radius; separate arc scope candidate); Stage 3 (Bucket C caller-graph + Bucket D evidence) blocked on 2b close. | Phase 2 close ✅ | All 27+ endpoints remediated per bucket; base DRF exception handler + Django middleware + template overrides + regression suite scaffolded conforming to safety contract §8; envelope unification landed OR documented cross-substrate acceptance; first tests pass; CI-blocking |
| **Phase 4 — Coverage Denominator Machinery** | BLOCKED on Phase 3 close | Phase 3 close | CI route-list generator live; snapshot drift detection blocks unreviewed new routes |
| **Phase 5 — I-0301 Close** | BLOCKED on Phase 4 close | Phase 4 close | All buckets remediated; regression suite green + CI-blocking; coverage machinery live; `I-030199_close.md` written + Chris-ratified |

**Downstream unlocks activated by Phase 2 close (each requires separate Chris authorization to open):**
- **Phase 3** (this arc) — HTTP Remediation (first code-touching phase)
- **RUR-C2** — Async State + Fail-Loud + Traceability (I-0400 slot)
- **I-0302** — Object-Level Authorization (RUR-C1 second child)
- **I-0303** — Async Tenant-Boundary Enforcement (RUR-C1 third child)

**Downstream unlocks:**
- Phase 2 close (safety contract Chris-ratified) unblocks: RUR-C2 opening + I-0302 opening + I-0303 opening
- I-0301 close does NOT close RUR-C1 (parent needs I-0302 + I-0303 close too, per Chris Q2 D-verdict)

---

**End of I-0301 Scoping. Wave 1 authorization is permission to scope this arc, not permission to implement.**
