# PUBLIC_PATHS Audit — S2789 (Fold B row 41)

**Session:** 2789 · **Date:** 2026-07-15 · **Scope:** proactive; row 41 `future_trigger` had not fired the 4th-site threshold

## Executive summary

- `core/auth_middleware.py::UnifiedTokenAuthenticationMiddleware.PUBLIC_PATHS` has 263 prefix entries + 2 exact entries
- Total /api routes matched by PUBLIC_PATHS: 1369 (of which 611 = /admin/ has own auth)
- **UNGATED + true mutation evidence: 76** ← BUCKET B
- UNGATED + no mutation evidence (simulation / mock / noop — safe): 38
- GATED mutating (has auth marker in view or CBV MRO): 143
- Unknown-methods routes (need manual check): 63

## S2789 ship (closed this session)

**Prefix:** `/api/pilot-gates/` — 7 mutation endpoints gated with `@token_auth_required` (Rigby S2789 T1 SIGN fold rows 42+43 corrected `@login_required` recommendation).

- `update_gate_status` (POST /api/pilot-gates/<uuid>/status/)
- `update_checklist_item` (POST /api/pilot-gates/<uuid>/items/<uuid>/)
- `create_pilot_gate` (POST /api/pilot-gates/create/<uuid:decision_id>/) — classifier missed (custom factory call, not `.objects.create()`)
- `start_pilot_execution` (POST /api/pilot-gates/<uuid>/pilot/)
- `complete_pilot_execution` (POST /api/pilot-gates/<uuid>/pilot/<uuid>/complete/)
- `regenerate_checklist_content` (POST /api/pilot-gates/<uuid>/regenerate/)
- `approve_all_checklist_items` (POST /api/pilot-gates/<uuid>/approve-all/)

Regression: `core/tests/test_pilot_gates_authz_sweep_2789.py` (21 tests, all pass).

## Deferred to S2790+ (mechanical continuation)

**S2790 UPDATE:** `/api/time-travel/` prefix CLOSED (PR pending — 11 endpoints gated with `@token_auth_required`, `@csrf_exempt` removed per S2787 pattern, regression `core/tests/test_time_travel_authz_sweep_2790.py` = 44 tests). Ungated remaining: 65 (was 76).


The remaining ungated-true-mutating candidates by prefix (each a per-prefix ship candidate for future sessions):

| Prefix | Endpoints | Ship priority | Notes |
|---|---|---|---|
| `/api/time-travel/` | 11 | HIGH | — |
| `/api/teams/` | 6 | HIGH | — |
| `/api/distribution/` | 6 | HIGH | — |
| `/api/v1/research/self-blog/` | 6 | MEDIUM | — |
| `/api/legal/cases/` | 6 | HIGH | — |
| `/api/agent-evolution/` | 5 | LOW | — |
| `/api/memory-clusters/` | 4 | LOW | — |
| `/api/agent-dreams/` | 3 | LOW | — |
| `/api/experiments/` | 3 | MEDIUM | — |
| `/api/agent-relationships/` | 3 | LOW | — |
| `/api/initiatives/` | 2 | MEDIUM | — |
| `/api/action-items/` | 2 | LOW | — |
| `/api/spider-health/` | 2 | LOW | — |
| `/api/memory-palace/` | 2 | LOW | — |
| `/api/neural-orchestra/` | 1 | LOW | — |
| `/api/spider-dashboard/` | 1 | LOW | — |
| `/api/spider-intelligence/` | 1 | LOW | — |
| `/api/spider-feed/` | 1 | LOW | — |
| `/api/hive-mind/` | 1 | LOW | — |
| `/api/autonomous/` | 1 | LOW | — |
| `/api/audit-tracking/findings/` | 1 | LOW | — |
| `/api/v1/telemetry/` | 1 | LOW | — |
| `/api/newsletter/` | 1 | LOW | — |

## Full endpoint list (JSON)

See `docs/audits/public_paths_audit_s2789.json` for the machine-readable inventory. Each entry:
```
{path, prefix, methods, view_file, view_line, mutation_hits}
```

## Classifier method

1. Enumerate all Django URL patterns via `get_resolver().url_patterns`.
2. For each pattern, match against `PUBLIC_PATHS` prefixes.
3. Deep-unwrap `__wrapped__` chain + `view_class` to find the real view.
4. Extract HTTP methods from CBV `http_method_names`, DRF `actions`, or decorator source (`@require_http_methods`, `@api_view`, `@require_POST`).
5. Check for auth markers in view source + CBV MRO + `permission_classes` class attr (excluding django/rest_framework framework classes).
6. Filter mutating-but-ungated routes by real mutation evidence (`.objects.create(`, `.save()`, `.delete()`, celery dispatch, cache mutations, redis publish, transactions).

**Known limitations (per Rigby S2789 T1 SIGN Concern 1):**
- Classifier misses custom factory methods (e.g., `PilotReadinessGate.create_for_decision()`).
- Classifier flags simulation/mock endpoints (like `/api/agents/execute/` which returns `random.uniform()` values) as mutating — filtered to `ungated_no_mutation_evidence` bucket.
- CBVs whose auth lives in a base class outside the standard MRO scan may false-positive as ungated.

## Zoom-out folds persisted at S2789 (rows 42-44)

- Row 42 (`same_pr_actionable`) — Classifier POST-vs-mutation false-positive heuristic (adopted this PR: added mutation-evidence filter).
- Row 43 (`same_pr_actionable`) — `@login_required` breaks S887 on PUBLIC_PATHS (adopted this PR: gated with `@token_auth_required` instead).
- Row 44 (`future_trigger`) — 3rd Rigby SIGN response truncation observation; substrate-promotion trigger now met (deferred to S2790+ as pa_chat.py/PA worker size cap investigation).

## Zoom-out fold candidate (S2789 substrate; not persisted yet, future ADR)

263 PUBLIC_PATHS prefix entries + 76 unresolved-Bucket-B candidates suggests the middleware+prefix-allow-list pattern is fundamentally the wrong shape. Alternative: explicit `@public_endpoint` opt-in decorator (Flask/FastAPI-style). Recorded as zoom-out for future ADR sketch.