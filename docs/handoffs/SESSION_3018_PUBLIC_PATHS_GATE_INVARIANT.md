# Session 3018 — Route-Decorator Invariant Test (Fold A close)

**Date:** 2026-07-28 · **HEAD at close:** docs cascade → `f81d84951` (PR #3721)

## What shipped

**PR #3721 (`f81d84951`) — `test(s3018): route-decorator invariant test for PUBLIC_PATHS bare-prefixes (Fold A)`**

Ratified path from S3017 Fold A `1st trigger`. Chris ratified Option A ("proceed with the invariant test") at S3017 close. Generalizes the ad-hoc S3016 Fold G / S3017 F-2+F-3 audit + fix into a permanent guard.

Changes:
- **NEW** `tests/security/public_paths_gate_snapshot_builder.py` — enumeration + gate detection (marker + `__wrapped__` unwrap traversal + DRF `permission_classes` fallback) + split-file read/write helpers.
- **NEW** `tests/security/public_paths_gate_snapshot_gated.json` — 127 gated rows (1027 lines). High-signal diff surface.
- **NEW** `tests/security/public_paths_gate_snapshot_ungated.json` — 606 ungated rows (4859 lines). Noise bucket.
- **NEW** `tests/security/test_public_paths_gate_invariant_s3018.py` — 2 tests: (1) snapshot ↔ live-state equality with special "NEW ungated route" fail-path fired BEFORE generic drift, (2) sanity check on the S3017 `get_memory_detail` gated view.
- **NEW** `core/management/commands/refresh_public_paths_gate_snapshot.py` — regen command with `--dry-run`.
- **MODIFIED** `core/auth_middleware.py` — `_auth_gate = 'token_required'` marker on `token_auth_required`.
- **MODIFIED** `core/security/decorators.py` — `_auth_gate = 'superuser_required'` marker on `superuser_required`.

Baseline: 733 in-scope routes across 255 bare-prefixes (excluding `/admin/`, `/api-auth/`, and `OPTIONAL_AUTH_PATHS`).
- 29 `decorator:token_required` (includes the 3 S3017 fixes)
- 98 `drf:IsAuthenticated`
- 606 `gate: none` (mixed — many legitimately public; snapshot locks state)

Regression: 40/40 pass (38 prior S3013-S3017 + 2 new S3018) in 4.454s. Negative-path sanity: both failure branches (gated-route drift + new-ungated-route special message) fire correctly.

## Rigby SIGN cycles this session

1. **T0 SIGN (before coding)** — AGREE-with-shape + 3 refinements:
   - §1: Variant B (snapshot-lock, not strict-must-gate) — applied.
   - §1: Special failure message for new ungated routes — applied.
   - §2: Marker + `__wrapped__` unwrap traversal (both) — applied.
   - §3: Include `PUBLIC_PATHS_EXACT`, exclude `OPTIONAL_AUTH_PATHS` — applied.
   - 4 Layer-2 risk callouts (path normalization, view identity stability, DRF ambiguity, snapshot-theater) — all addressed in the implementation.
2. **T1 SIGN (before merge)** — Re-issued after Rigby misread first prompt; second turn was substantive with tool_runs. REVISE-1 (split snapshot into gated + ungated files for diff hygiene) — Chris ratified same-PR fold. REVISE-2 (test-time advisory for decorator-chain-break) — deferred to future arc.
3. **Post-merge live verification** — `python manage.py refresh_public_paths_gate_snapshot --dry-run` returns clean counts (733 routes / 255 prefixes / 29 token / 98 DRF / 606 none) matching the shipped snapshot.

**Rigby SIGN quality this session:** 2 substantive SIGN cycles + 1 truncation-recovery re-issue, all tool-grounded, zero hallucination triggers. **Matches S3010–S3017 pattern — 10 sessions continuous.**

## Zoom-out folds

- **Fold A (Rigby T1 REVISE-1) — `same_pr_actionable → resolved`**: snapshot split into gated + ungated files.
- **Fold B (Rigby T1 REVISE-2) — `future arc`**: test-time advisory telemetry for decorator-chain-break (marker defeated by non-wraps outer decorator).
- **Fold C (Rigby T1 zoom-out §3) — `informational`**: optional `@public_intentional` decorator marker to shrink the ambiguous `gate: none` bucket over time without a sweep.
- **Fold D (Rigby SIGN infra) — `1st trigger`**: Rigby first-turn response was truncated (only 1 of intended tool_runs surfaced). Root cause unclear — possibly tool_runs section overflow or context-window truncation on her end. Second turn (with explicit "run these tools" prompt) succeeded. Watch for 2nd trigger.

## Known limitations of gate detection (documented — not fixed in MVP)

- `@method_decorator(superuser_required)` on class methods is not caught by the marker traversal (marker lives on the method, not `.as_view()` output). Such views appear as `gate: none` even though they're properly gated. Fold-in candidate.
- Inline `request.user.is_authenticated` checks inside view bodies are not detected. `gate: none` for those too.
- Custom auth decorators outside `token_auth_required` / `superuser_required` are unrecognized. Add markers to them + regen the snapshot.

## Forward carries

**New from S3018:**
- **Fold B (Rigby REVISE-2)** — test-time advisory telemetry for decorator-chain-break.
- **Fold C** — optional `@public_intentional` marker to shrink the `gate: none` bucket.
- **Fold D** — Rigby response-truncation trigger (1st).
- **Method-decorator detection extension** — catch `@method_decorator(superuser_required)` on CBV methods.
- **Inline `.is_authenticated` detection extension** — grep-based advisory for views that gate inline.

**Carried from S3017 (STATUS UPDATED):**
- **S3017 Fold A** — **CLOSED by S3018 PR #3721**.
- **S3017 Fold C (A.2 cross-user isolation)** — still open, future arc.
- **S3017 Fold D (Rigby Tool Gap Ledger tool gaps)** — still open.

**Carried from S3016 / older** — all preserved from S3017 close 00-START.

## Substantive result

Class of leak that produced F-2 (S3016) and F-3 (S3017) is now protected by a hard-fail invariant:
- Any new URL pattern under a `PUBLIC_PATHS` (or `PUBLIC_PATHS_EXACT`) bare-prefix that lacks an `_auth_gate` marker OR a non-`AllowAny` DRF `permission_classes` will fail the invariant test.
- The test surfaces the specific new routes and their gate status in the failure message.
- To ship a legitimately-public new endpoint under a bare-prefix, the reviewer must consciously regenerate the snapshot — the regen appears as a diff in the ungated file, visible to any subsequent audit.

The 606 currently-ungated routes form an implicit audit backlog. Migration to gated-per-view or Variant A (strict-must-gate) remains a future arc.
