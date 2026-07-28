# PUBLIC_PATHS Bare-Prefix Audit — S3016 (Fold G)

**Session:** 3016 · **Date:** 2026-07-28 · **HEAD at audit:** `ad84a847b` (Fold E merged)

## What this audit is (and isn't)

PR #3714 (S3015 hotfix) exposed a failure mode where a bare prefix in
`UnifiedTokenAuthenticationMiddleware.PUBLIC_PATHS` matched broader than its
comment intended: `/api/initiatives/` was meant for `/api/initiatives/<uuid>/action-items/`
(Session 912) but `startswith` matching caught the list endpoint too. The
middleware short-circuited before token parsing, dropped Token-authenticated
callers to `AnonymousUser`, and `scope_queryset_initiative(AnonymousUser)`
returned `.none()` — count=0 in the browser even though the same user via
session auth returned 22 rows.

Rigby T0 REVISE 2 narrowed the audit scope: **flag only PUBLIC_PATHS
prefixes that resolve to endpoints whose anonymous behavior is "empty 200"
due to queryset scoping** (silent degradation), not endpoints that 401/403
loudly. This is distinct from `PUBLIC_PATHS_AUDIT_S2789.md` — that audit
was about *mutation gating* (76 ungated writes; 22 shipped fixes across
S2789+S2790; 65 remaining). This one is about *silent-empty reads*.

## Method

**`scripts/audit_public_paths_scoped_reads_s3016.py` is a candidate
generator only — it does not classify anon behavior as empty-200 vs
loud-401/403.** The grep yields candidates; hand-review of each candidate
determines whether an earlier decorator (e.g. `@superuser_required`) makes
anon 401 loudly, or the scope predicate silently returns `.none()`.

1. Enumerate every URL pattern via `get_resolver().url_patterns`.
2. For each `PUBLIC_PATHS` prefix, find matching URL patterns via
   `startswith` (mirrors the middleware short-circuit at
   `core/auth_middleware.py:591-594`).
3. Deep-unwrap `__wrapped__` and `view_class` chains to reach the real view.
4. Grep view source for calls to any of the 5 scope predicates in
   `core/security/object_authz.py`:
   - `scope_queryset_deliverable`
   - `scope_queryset_chat_conversation`
   - `scope_queryset_initiative`
   - `scope_queryset_agent_execution`
   - `scope_queryset_document`
5. Emit a per-prefix candidate list + JSON at
   `docs/audits/public_paths_bare_prefix_audit_s3016.json`.
6. Hand-review each candidate: read the view source for gating decorators,
   classify anon behavior (401/403 loud vs empty 200 silent), and write
   findings below.

## Findings

**2 raw matches. After hand-review: 0 critical, 1 partial degradation, 1 false positive.**

### F-1 (false positive) — `/api/celery/` → `/api/celery/breakdown/` (`TaskBreakdownView`)

- **File:** `core/views_celery_api.py:256` (`TaskBreakdownView`)
- **Scope predicate:** `scope_queryset_agent_execution`
- **Anonymous behavior:** **401 loud rejection**, not empty 200.
- **Why:** The `.get()` method is decorated with `@method_decorator(superuser_required)`
  (`core/views_celery_api.py:264`). Docstring at line 261 confirms:
  "Anonymous → 401, non-superuser → 403." The scope predicate is present
  for defense-in-depth but the decorator gate runs first and rejects anon
  loudly.
- **Action:** none required. Reclassify out.

### F-2 (unscoped detail endpoint in PUBLIC_PATHS) — `/api/memory-palace/` (and narrower `/api/memory-palace/memory/`) → `/api/memory-palace/memory/<uuid:memory_id>/` (`get_memory_detail`)

> **CLOSED S3017 (PR #3719, merge `09f6e91e7`).** Option A.1 shipped —
> `@token_auth_required` gate on `get_memory_detail`. Rigby T1 SIGN
> zoom-out 5b surfaced **F-3** (sibling routes under the same bare-prefix
> bypass): `get_memory_connections` (same-class read leak) and
> `delete_memory` (anon-DELETE-any-row mutation leak — strictly worse
> than F-2). Both folded into the same PR per PLAYBOOK-6.10.8
> `same_pr_actionable`. Cross-user isolation (A.2 alternative — new
> `scope_queryset_agent_memory` predicate) remains a forward-carry.
> Live smoke: GET detail / GET connections / DELETE all return 401 +
> `not_authenticated` envelope against real memory UUIDs.


- **File:** `core/views_memory_palace.py:98` (`get_memory_detail`).
- **Primary issue:** the memory detail row itself is **unscoped and public**.
  The top-level `AgentMemory.objects.defer('embedding').get(id=memory_id)`
  at line 107 has no scope predicate, no `user=` filter, and no permission
  decorator (`@csrf_exempt + @require_http_methods(["GET"])` at line 98-99).
  Any anonymous caller with a valid `memory_id` UUID sees the memory row —
  including the access_count auto-increment side effect at line 112-114.
- **Secondary issue (silent enrichment drop):** the optional `execution_data`
  enrichment at line 128-142 uses `scope_queryset_agent_execution(request.user,
  …).get(id=memory.source_id)`, which raises `AgentExecution.DoesNotExist`
  for anon; the `except` clause `pass`es and the response returns
  `execution_data=None` with no indication of whether the enrichment was
  absent or withheld.
- **Severity:** low for the S3015 class (list-endpoint-empty), but the
  unscoped-detail-row issue is a distinct authz gap that predates this
  audit's scope. Not remediating in this doc-only PR — Chris ratifies
  remediation shape.
- **Remediation candidates (deferred, not this session):**
  1. Gate the whole view with `@token_auth_required` (simplest — matches
     S2789 pattern for endpoints in PUBLIC_PATHS that need auth).
  2. **Scope the memory lookup itself** via a new `scope_queryset_agent_memory`
     predicate in `core/security/object_authz.py`, then use
     `scope_queryset_agent_memory(request.user, AgentMemory.objects.defer('embedding')).get(id=memory_id)`.
     No such predicate exists today; introducing one is a small design
     addition to the object_authz surface.
  3. Add an `execution_data_available` payload flag so consumers can
     distinguish "no execution linked" from "auth-denied enrichment".
     Addresses the secondary issue only; does not fix the unscoped memory
     row leak.
  Chris ratifies which shape at S3016 close or forward-carry. Options 1 or
  2 solve the primary issue; option 3 alone would not.

### Housekeeping — duplicate `/api/celery/` entry in `PUBLIC_PATHS`

`/api/celery/` appears twice in the list:

- `core/auth_middleware.py:148` — Session 660 comment "Celery Task Monitor"
- `core/auth_middleware.py:225` — Session 642 comment "Celery Monitoring"

Same prefix, harmless in runtime (idempotent `startswith` match), but noisy
in this audit. Dedupe candidate for a low-priority follow-up PR.

## Substantive result

The S3015 list-endpoint-empty class **does not repeat elsewhere in the
current PUBLIC_PATHS surface for the 5 tracked scope predicates.** The
Fold E hotfix + parity tests are correctly scoped to the actual failure;
no other `/api/…/` endpoint list-view is currently at risk of the same
silent-empty divergence via a bare-prefix PUBLIC_PATHS entry.

**Caveat:** the candidate generator only catches views that reference the
5 tracked predicate names in source. Views that do inline scoping via
`.filter(user=request.user)` or `get_object_or_404(Model, user=request.user, …)`
are invisible to this scan. If a future silent-empty regression surfaces
on an endpoint that doesn't use the tracked predicates, expand the
classifier to grep for those inline patterns as well.

## Scope caveats

1. **Predicate coverage is 5 predicates.** If a view uses a different
   `.filter(user=request.user)` pattern inline (not routed through the
   canonical scope predicates), it would not be flagged here.
2. **Read-only heuristic.** POST/PUT/PATCH endpoints are covered by
   `PUBLIC_PATHS_AUDIT_S2789.md` (mutation gating). This audit is READ-only.
3. **`startswith` normalization.** URL patterns are stripped of leading
   `^` and forced to a `/` prefix before matching. Edge cases (regex
   patterns with anchors deep in the pattern) are not modeled.
4. **Middleware ordering.** All findings assume `UnifiedTokenAuthenticationMiddleware`
   runs in the standard position. Middleware-ordering drift is a separate
   S3016 Fold E zoom-out carry (not addressed here).

## Forward carries

- **F-2 remediation** (either `@token_auth_required` gate or an
  `execution_data_available` payload flag) — Chris ratifies shape.
- **Dupe `/api/celery/` entry** — low-priority housekeeping PR.
- **Extend audit to inline `.filter(user=…)` patterns** — if a future
  silent-empty regression surfaces on an endpoint that doesn't use the
  5 tracked predicates, expand the classifier.
- **Track the S3016 zoom-out carries** in the session handoff: middleware-
  ordering drift, HTTP_HOST / proxy-header edge cases, `Bearer` vs `Token`
  header variants.

## Machine-readable output

`docs/audits/public_paths_bare_prefix_audit_s3016.json` — raw findings
before hand-review + false-positive filtering. Each entry:
```
{prefix, matched_scoped_endpoints: [{url, view_name, file, line, scope_predicates_called}]}
```
