# Session 3017 — Memory-Palace Auth Gate (F-2 close + F-3 sibling fold)

**Date:** 2026-07-28 · **HEAD at close:** docs cascade → `09f6e91e7` (PR #3719 fix) → `95980649b` (S3016 close cascade)

## What shipped

**PR #3719 (`09f6e91e7`) — `fix(s3017): @token_auth_required on memory-palace detail + siblings (F-2 + F-3)`**

Ratified path from S3016 close-out joint recommendation: Option A.1 (`@token_auth_required` gate) on the F-2-identified endpoint. Rigby T1 SIGN zoom-out expanded scope to include the two sibling routes under the same bare-prefix bypass.

Changes:
- `core/views_memory_palace.py`:
  - Imported `token_auth_required` from `core.auth_middleware`.
  - Gated `get_memory_detail` (F-2 — anon-readable memory row + `access_count` bump).
  - Gated `get_memory_connections` (F-3 — same-class anon-readable connection graph).
  - Gated `delete_memory` (F-3 — worse-than-F-2: anon-DELETE-any-row mutation).
- `core/tests/test_s3017_memory_detail_auth_gate.py` — 6 tests:
  1. anon → 401 with `not_authenticated` envelope
  2. anon does NOT bump `access_count`
  3. session-auth → 200 + success
  4. Token-auth → 200 + success (Fold E parity)
  5. anon connections → 401
  6. anon DELETE → 401 + row survives
- `docs/audits/PUBLIC_PATHS_BARE_PREFIX_AUDIT_S3016.md` §F-2 — CLOSED block + F-3 reference.

Regression: 38/38 pass (32 existing S3013-S3016 + 6 new S3017) in 4.647s.

## Rigby SIGN cycles this session

1. **T1 SIGN (before merge)** — AGREE with substantive tool_runs (repo_tool.read + repo_tool.search across `views_memory_palace.py`, `auth_middleware.py`, and the new test file). Zoom-out 5b surfaced F-3; folded same-PR.
2. **Close-out SIGN (post-recycle live smoke)** — REVISE (Layer 2): live GET-401 verified on detail + connections, but tool gaps blocked live DELETE-401 verification (see Rigby Tool Gap Ledger).
3. **REVISE-1 closed by Claude local curl** — DELETE against real memory UUID `d64fd7f9-…` → 401 + `not_authenticated` envelope, row survives. Definitive Layer 2 proof of F-3 gate.

**Rigby SIGN quality this session:** 2 substantive SIGN cycles, both tool-grounded, zero hallucination triggers. **Matches S3010–S3016 pattern — 9 sessions continuous.**

## Zoom-out folds

- **Fold A (Rigby T1 5a) — `1st trigger`**: route-decorator invariant test (enumerate URL patterns under `/api/memory-palace/` and assert decorator coverage). Reduces "human memory tax" of per-view gating. Not addressed in this PR — forward carry.
- **Fold B (Rigby T1 5b) — `same_pr_actionable → resolved`**: sibling routes folded (F-3 above).
- **Fold C (Rigby T1 5c) — `future arc`**: A.1 → A.2 migration path documented. `scope_queryset_agent_memory` predicate for cross-user isolation is a separate ADR candidate.
- **Fold D (Rigby close-out) — `1st trigger`**: `web_fetch_tool` DELETE support gap + `http_smoke_test` middleware-bypass gap. Logged to Rigby Tool Gap Ledger.

## Forward carries

**New from S3017:**
- **Route-decorator invariant test** (Fold A) — extend to all bare-prefix children under `/api/memory-palace/` + audit other bare-prefix entries in PUBLIC_PATHS for the same shape.
- **A.2 cross-user isolation** (Fold C) — new `scope_queryset_agent_memory` predicate + migration from A.1 (keep decorator, add row-scoping). Requires ADR since `AgentMemory` has no direct user FK today.
- **Rigby Tool Gap Ledger — `web_fetch_tool` DELETE support** (Fold D) — verify against real UUIDs remained a Claude-local-shell fallback.
- **Rigby Tool Gap Ledger — `http_smoke_test` middleware-bypass** (Fold D) — `http_smoke_test` appears to skip `UnifiedTokenAuthenticationMiddleware` for anon requests (hit view body directly, returning 404 instead of 401). Confirms live smoke should route through `web_fetch_tool` or Claude curl for auth-gate verification.

**Carried from S3016 (STATUS UPDATED):**
- **S3016 Fold G F-2 remediation** — **CLOSED by S3017 PR #3719**.
- **S3016 dupe `/api/celery/` PUBLIC_PATHS entry** — still open (housekeeping).
- All other S3016 zoom-out carries preserved (middleware-order snapshot test, DRF ViewSet parallel audit, WebSocket auth parity, `Bearer <token>` helper extension).

**Carried from S3015/S3014/S3013/older** — all preserved from 00-START-NEXT-SESSION at S3016 close.

## Substantive result

Class of leak closed for `/api/memory-palace/memory/<uuid>/**`:
- Anon-read of detail row + silent side effect (`access_count` bump) — closed.
- Anon-read of connection graph — closed.
- Anon-DELETE of any memory row — closed (was the highest-severity gap; not in the original F-2 audit finding).

The audit-driven F-2 remediation caught F-3 as a same-PR fold via Rigby zoom-out. Without the zoom-out ask (per `feedback_zoom_out_ask_per_rigby_sign`), F-3 would have shipped as a follow-up PR within a day — the anon-DELETE hole would have stayed open in between.
