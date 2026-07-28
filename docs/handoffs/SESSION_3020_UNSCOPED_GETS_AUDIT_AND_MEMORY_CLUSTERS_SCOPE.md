# Session 3020 — Unscoped `.get()` Audit + Memory-Clusters Scope Guards

**Date:** 2026-07-28 · **HEAD at close:** docs cascade → `f5c7823166d0` (PR #3725)

## What shipped

**PR #3725 (`f5c7823166d0` after Rigby REVISE) — `feat(s3020): audit + fold F-1/F-2 memory-clusters scope guards`**

Ratified path: S3019 close 00-START Option A → A.2 pattern generalization audit. Chris ratified same-PR fold on F-1 + F-2 remediation per S3017 F-3 precedent. Rigby T1 REVISE surfaced a third real gap (cluster ownership) — folded same-PR.

**Audit** (`docs/audits/UNSCOPED_GETS_S3020.md`):
- `scripts/audit_unscoped_gets_s3020.py` — grep-based candidate generator across 221 view files.
- 4 candidates → **3 real gaps + 2 false positives** (final classification after Rigby REVISE hand-review resolved F-3).

**Remediation (same-PR):**
- **F-1** `views_memory_clusters.py:464` — `add_memory_to_cluster` gated with `@token_auth_required` + `scope_queryset_agent_memory` on memory fetch.
- **F-1b** `views_memory_clusters.py:451` — (Rigby T1 REVISE Layer 1) cluster fetch also scoped via inline `.filter(agent__user_assignments=request.user).distinct()`, mirroring ADR-0008 shape without a new predicate.
- **F-2** `views_memory_clusters.py:585` — `find_similar_clusters` gated + scoped, same pattern as F-1.
- **F-3** `views_diagnostics.py:4310` — **FALSE POSITIVE** after hand-review. `scope.prospect_profile_id` is server-derived from `VIPInvite.objects.filter(redeemed_by=user)` (not user-influenceable).
- **F-4** `views_preview_api.py:391` — false positive (inline `.filter(owner=)`).
- 8 new tests + snapshot regen (`decorator:token_required` 29 → 31).

Regression: 59/59 pass in 8.494s across S3013-S3020. S3018 route-decorator invariant test correctly caught the snapshot drift.

Live smoke post-recycle:
- Anon POST `/api/memory-clusters/cluster/<id>/add-memory/` → 401 `not_authenticated`.
- Anon POST `/api/memory-clusters/find-similar/` → 401 `not_authenticated`.

## Rigby SIGN cycles this session

1. **T1 SIGN on the audit+remediation PR** — **REVISE** with 3 substantive items:
   - Layer 1: cluster ownership unscoped (real bug I missed). Folded same-PR with inline `.filter(agent__user_assignments=)`.
   - Layer 2 §c: test looseness (`(200, 500)` too broad). Tightened to `assertNotIn(401, 404)` + membership-row assertion.
   - Layer 2 §b: F-3 hand-review now vs S3021 defer. Hand-reviewed same-session; false-positive confirmed.
   - Also §a: script file-level suppression false-negative risk. Noted as S3021 forward-carry (not blocking).
2. **Post-recycle live smoke** — Claude-local curl confirmed anon-401 on both endpoints.

**Rigby SIGN quality:** 1 substantive SIGN cycle with a real bug catch (cluster ownership). Zero rubber-stamp. **Matches S3010-S3019 pattern — 12 sessions continuous.**

## Zoom-out folds

- **Fold A (Rigby T1 §a)** `future arc` — script false-negative from file-level predicate suppression. Refactor to per-hit / per-function suppression.
- **Fold B (Rigby T1 Layer 1 cluster-ownership catch)** `same_pr_actionable → resolved` — cluster fetch also scoped inline. Note that this pattern (agent-owned models with M2M-through-Agent scoping) may warrant its own `scope_queryset_memory_cluster` predicate in a future ADR-0009 if the pattern repeats.
- **Fold C (Rigby T1 §c)** `same_pr_actionable → resolved` — test tightening.
- **Fold D (Rigby T1 §b F-3 hand-review)** `same_session_actionable → resolved` — hand-reviewed + false positive confirmed.

## Forward carries

**New from S3020:**
- **Fold A** — audit script per-hit/per-function suppression refactor.
- **Fold B** — potential `scope_queryset_memory_cluster` predicate (watch for 2nd trigger where the M2M-through-Agent inline pattern is duplicated).
- **Audit multiline chained `.filter(...).get(...)` regex extension.**
- **Predicate universe expansion** — as new predicates land in `object_authz.py`.

**Carried from S3019 (STATUS UPDATED):**
- **S3019 forward-carry: A.2 pattern generalization** — **CLOSED by S3020 PR #3725** (found 2 real gaps + 1 hand-reviewed FP + 1 grep FP; substrate clean).
- **S3019 Fold B (predicate-shape-table comment)** — still open.

**Carried from earlier** — all preserved from S3019 close 00-START.

## Substantive result

The S3020 audit + fixes complete the memory-* auth trajectory:
- **S3016 F-2 audit** — surfaced the bare-prefix bypass class.
- **S3017 A.1 decorator** — closed anon-reach on memory-palace routes.
- **S3018 invariant test** — locked the class at PR review time.
- **S3019 A.2 predicate (ADR-0008)** — closed authenticated cross-user on memory-palace.
- **S3020 audit + fixes** — generalized the pattern to memory-clusters (sibling surface), same-PR-mitigated three real gaps + resolved one hand-review false positive.

Five sessions, five PRs, one full class of vulnerability closed across memory-palace + memory-clusters surfaces with tests + docs + invariant + predicate + audit script. Clean substrate-hardening arc.

Also notable: this is the **fourth consecutive Rigby REVISE-with-substantive-catch** (S3017 F-3 sibling fold, S3018 split-snapshot, S3019 test-helper + wording, S3020 cluster ownership). Rigby's zoom-out is actively catching class-adjacent gaps I miss on first pass. That signal is validated across 4 sessions.
