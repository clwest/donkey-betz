# Unscoped `Model.objects.get(id=...)` Audit — S3020 (Fold A generalization)

**Session:** 3020 · **Date:** 2026-07-28 · **HEAD at audit:** `95158a509`

## What this audit is (and isn't)

Ratified as S3020 Option A at S3019 close: the memory-palace 4-session arc (S3016 F-2 audit → S3017 A.1 decorator → S3018 invariant → S3019 A.2 predicate) closed ONE class of vulnerability. This audit checks whether the same "unscoped `.get()` where a predicate exists" shape repeats elsewhere.

**Candidate generator only.** For each of the 6 canonical scope predicates (S3019 baseline: `deliverable`, `chat_conversation`, `initiative`, `agent_execution`, `document`, `agent_memory`), grep `core/views_*.py` for `<Model>.objects...get(id=...)` patterns where the same file does NOT reference the corresponding predicate.

**Distinct from `PUBLIC_PATHS_BARE_PREFIX_AUDIT_S3016.md`:** that audit was about silent-empty reads under a bare-prefix bypass. This one is about predicate-exists-but-not-called. The two intersect but aren't identical.

## Method

1. Enumerate the 6 predicates + their target models.
2. Grep `core/views*.py`, `core/views/*.py`, `core/agents/views_*.py` for `<Model>.objects.[chain].get(...)` patterns.
3. Suppress hits where the same file contains a call to `scope_queryset_<model>` (signal that the view already uses the scope path — hand-review can still catch same-file mis-usage).
4. Emit per-hit rows with file:line + snippet for hand-review.

**Scope caveats:**
- Multiline chained `.filter(...)\n.get(...)` split across newlines is missed by regex — hand-review of any grepped file catches these.
- Views that scope via a shared helper called from multiple sites are false-negative-tolerant (the source in the current file doesn't need to name the predicate).
- Views that inline-scope via `.filter(owner=request.user).get(...)` are FALSE POSITIVES — the intent matches the predicate even without calling it.

## Baseline scan (script `scripts/audit_unscoped_gets_s3020.py`)

**View files scanned:** 221
**Candidate hits:** 4 across 4 rows

| Hit | File:Line | Model | Predicate | Classification |
|-----|-----------|-------|-----------|----------------|
| F-1 | `core/views_memory_clusters.py:464` | `AgentMemory` | `scope_queryset_agent_memory` | **REAL GAP** — F-3-shape |
| F-2 | `core/views_memory_clusters.py:585` | `AgentMemory` | `scope_queryset_agent_memory` | **REAL GAP** — F-3-shape |
| F-3 | `core/views_diagnostics.py:4310` | `Deliverable` | `scope_queryset_deliverable` | **NEEDS AUTH TRIAGE** |
| F-4 | `core/views_preview_api.py:391` | `Initiative` | `scope_queryset_initiative` | **FALSE POSITIVE** — inline-scoping |

## Findings

### F-1 — `views_memory_clusters.py:464` (add-memory-to-cluster) — REAL GAP

- **Endpoint:** POST body with `memory_id`; unscoped `AgentMemory.objects.get(id=memory_id)` at line 464.
- **Enclosing decorator:** `@require_http_methods(["POST"])` at line 442. **No auth gate.**
- **URL prefix:** `/api/memory-clusters/` in `PUBLIC_PATHS` at `core/auth_middleware.py:433` (bare prefix).
- **Failure mode:** anonymous caller with any valid memory UUID can add that memory (including another user's) into a cluster they specify. Cross-user memory write + potential cross-user cluster mutation.
- **Severity:** direct sibling of S3017 F-3 (memory-palace delete). Same class, different endpoint.
- **Remediation candidate:** wire `@token_auth_required` + `scope_queryset_agent_memory(request.user, ...).get(id=...)`. Parallels S3017 + S3019 shape exactly.

### F-2 — `views_memory_clusters.py:585` (find-similar / query embedding) — REAL GAP

- **Endpoint:** POST body with `memory_id`; unscoped `AgentMemory.objects.get(id=memory_id)` at line 585 to fetch embedding vector.
- **Enclosing decorator:** `@require_http_methods(["POST"])` at line 561. **No auth gate.**
- **URL prefix:** same as F-1 — `/api/memory-clusters/` PUBLIC_PATHS bare-prefix.
- **Failure mode:** anonymous caller can supply any memory UUID, retrieve the embedding + trigger similarity search. Vector-space cross-user read + potential index enumeration.
- **Severity:** F-2-shape read leak; also an embedding-vector leak (embeddings can encode text semantics).
- **Remediation candidate:** same as F-1 — decorator + predicate.

### F-3 — `views_diagnostics.py:4310` (cockpit VIP context) — NEEDS AUTH TRIAGE

- **Endpoint:** `cockpit_vip_context` at line 4276; unscoped `Deliverable.objects.get(id=scope.prospect_profile_id)` at line 4310 (inside the `if scope.prospect_profile_id:` branch).
- **Enclosing decorator:** `@csrf_exempt` + `@require_http_methods(["GET"])`. **No auth gate.**
- **URL prefix:** `/api/cockpit/vip-context/` — **NOT** in `PUBLIC_PATHS` (verified by grep). Goes through `UnifiedTokenAuthenticationMiddleware` full path, so anon is rejected at middleware.
- **Failure mode:** authenticated caller can pass a `scope.prospect_profile_id` that references another user's Deliverable and retrieve its title + preview. But `scope` is derived from `request.user` earlier in the view (see line 4276 context) — needs deeper hand-review to determine whether an authenticated user can influence `scope.prospect_profile_id` cross-user.
- **Severity:** low if `scope.prospect_profile_id` is server-derived from `request.user` (no user-controlled input); medium if the user can influence it via query params.
- **Remediation candidate:** defer to S3021+ hand-review; if server-derived, no action; else wire `scope_queryset_deliverable`.

### F-4 — `views_preview_api.py:391` (initiative auto-populate) — FALSE POSITIVE

- **Code:** `Initiative.objects.filter(owner=request.user).get(id=initiative_id)` at line 391.
- **Why FP:** the `.filter(owner=request.user)` inline already enforces the same invariant as `scope_queryset_initiative`. The regex's "predicate not in file" heuristic missed this pattern.
- **Comment at line 387-388:** "I-0302 Phase 3 Sub-phase A2: query-time owner scoping — surfaces as `Initiative not found` (existing 400) if the caller doesn't own it."
- **Severity:** none. Correctly scoped.

## Substantive result

The audit surfaced **2 real gaps** in the same file (`views_memory_clusters.py`) — direct siblings of the S3016 F-2 / S3017 F-3 class. The `/api/memory-clusters/` bare-prefix in `PUBLIC_PATHS` combined with unscoped `AgentMemory.objects.get(id=…)` produces the exact F-2/F-3 shape S3017 closed on `/api/memory-palace/memory/`. Same class, different surface.

**Remediation shape:** the fix is mechanically identical to S3017 PR #3719 + S3019 PR #3723 combined — add `@token_auth_required` decorator AND route the `.get()` through `scope_queryset_agent_memory`. ~30 minutes for both sites.

**F-3 requires deeper hand-review** but the failure mode is bounded (no anon reach; authenticated-cross-user only if `scope.prospect_profile_id` is user-influenceable).

**F-4 is a false positive** — inline-scoping via `.filter(owner=…)` is equivalent to the predicate.

## Forward carries

- **F-1 + F-2 remediation** — apply S3017/S3019 pattern to `views_memory_clusters.py:464` and `:585`. Chris ratifies at S3020 close (or S3021).
- **F-3 hand-review** — determine whether `scope.prospect_profile_id` is user-influenceable in `cockpit_vip_context`. If yes, add predicate. If no, mark as false positive.
- **Audit pattern generalization** — this candidate generator missed multiline chained `.filter(...).get(...)` patterns and helper-function-scoped predicates. Extension for future arcs.
- **Predicate universe expansion** — as new predicates are added to `object_authz.py`, add them to `PREDICATES` in `scripts/audit_unscoped_gets_s3020.py`.

## Machine-readable output

`docs/audits/unscoped_gets_s3020.json` — raw per-hit rows before hand-review + false-positive filtering.
