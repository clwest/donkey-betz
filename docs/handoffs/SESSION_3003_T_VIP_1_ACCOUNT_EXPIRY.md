---
title: "SESSION 3003 — T-VIP-1 VIPInvite.account_expires_at runtime enforcement + backstop"
session: 3003
date: 2026-07-27
type: single_pr_close
merge_shas:
  - "3bd3df386"   # PR #3679 — T-VIP-1 middleware enforcement + cleanup beat task
prs:
  - 3679
related_arcs:
  - "ADR-0005 Typed Error Envelope Contract (ratified S3001, superseded by ADR-0006 S3002)"
  - "F-C-VIP-1 declared-but-not-enforced risk-gate (preserved HIGH severity across S2403, S2503)"
consumes:
  - "ADR-0005 §3.5 UX prerequisite clause (expiry-signal UX blocked on F-C-VIP-1 enforcement)"
  - "S3002 close-cascade joint recommendation ranking C > A > B > D"
---

# S3003 — T-VIP-1 — VIPInvite account expiry enforcement

**Status:** CLOSED. 1 feature PR merged. ADR-0005 §3.5 F-C-VIP-1 risk-gate discharged. HEAD `3bd3df386`.

## Session shape

Single-focus, single-PR, one-session close. Chris ratified T-VIP-1 as S3003 primary directive after Claude+Rigby joint recommendation reached agreement (C > A > B > D ranking preserved from S3002 close cascade). Full Flow B: primary-directive routing → Rigby joint agreement → Chris plain-English ratification → implementation → tests → A2 pre-merge SIGN → merge → recycle → close cascade. No spec-invalidation, no T1 DISAGREE, no Chris D-verdict revision — clean spec→ship walk.

## PR #3679 (`3bd3df386`) — T-VIP-1 middleware enforcement + backstop task

**Scope:**
1. `core/vip_middleware.py:60-70,118-146` — `VIPReadOnlyMiddleware.__call__` extended: after `_is_vip_user()` short-circuit, calls new `_invite_is_still_active(user)` helper. Denies 401 `{'error': 'Your VIP demo access has expired.'}` when the user's most-recent `VIPInvite(redeemed_by=user)` is missing, `revoked_at != None`, or `account_expires_at <= now`. Fail-closed on lookup exceptions. Missing-invite log line enriched with `user_id + username` per Rigby STRENGTHEN.
2. `core/tasks_vip.py` (new, 61 LOC) — `@shared_task(name='core.tasks_vip.cleanup_expired_vip_users')` filters `VIPInvite.objects.filter(account_expires_at__lt=now, redeemed_by__isnull=False, redeemed_by__is_active=True)`, sets `user.is_active=False`, returns `{'checked', 'deactivated', 'ran_at'}`. Idempotent.
3. `core/celery.py:229-238,1069-1075,1122-1127` — three additions:
   - Beat entry `cleanup-expired-vip-users` at `crontab(hour=2, minute=55)` queue=broadcast expires=3600 (slotted between existing 2:40 / 4:50 daily cleanups).
   - `'core.tasks_vip'` in `app.conf.imports` tuple (worker dispatch resolution).
   - `'core.tasks_vip'` in `_eager_import_session1115_modules` eager_modules (audit-time resolution — same S1115+S1253+S1257 non-standard-module precedent as `tasks_platform_audit` / `tasks_bug_triage` / `tasks_documentation_manager`).
4. `tests/test_vip_expiry.py` (new, 182 LOC) — 9 test cases:
   - **Middleware:** unexpired VIP passes / expired 401 / revoked 401 / no invite row 401 / non-VIP untouched / most-recent invite wins.
   - **Cleanup task:** deactivates expired active user / skips unexpired / idempotent on already-inactive.
   - **Test-writing gotcha discovered:** `_is_vip_user` reads `request.user.enhanced_profile` (Django reverse OneToOne descriptor that caches on User instance). A `post_save` signal on User auto-creates `EnhancedUserProfile` with `primary_role=''` and caches the reverse. Fix: re-fetch `User.objects.get(pk=user.pk)` after mutating `primary_role` to bust the cache. Not a production concern (session-auth flow gets a fresh user); worth noting for future `RequestFactory`-based middleware tests.

**Design decisions ratified by Rigby A2 SIGN:**
1. **401 (not 403).** Auth-lifecycle semantics — "access expired" ≠ "permission denied". Aligns with T-ENVELOPE-3 `SessionExpiredModal` semantics shipped S3002.
2. **Response body `{'error': 'string'}`.** Consistent within `vip_middleware.py`; envelope B migration is T-ENVELOPE-2/4 scope.
3. **Missing invite row = deny.** Data-inconsistency safe posture. Enriched log for debuggability per Rigby STRENGTHEN.
4. **Middleware-first + cleanup task backstop.** Immediate enforcement + eventual deactivation defense-in-depth.
5. **Beat cadence 2:55 AM MST.** Postgres-hit-cluster spacing.

**Rigby A2 SIGN quality signal:** 7 real tool_runs, each verifying a specific file:line claim I made in the routing. Per PLAYBOOK-7.7.2 SIGN evidence discipline this is substantive, not rubber-stamp. Zoom-out surfaced three concerns — two informational (invite-selection criterion depends on `redeemed_at` invariant; revocation endpoint already deactivates so cleanup task doesn't double-work), one same-PR-mitigatable-but-actually-forward-carry: frontend `queryClientErrorHandler` treats non-auth 401s as fail-open, so the T-ENVELOPE-3 modal won't fire for VIP expiry 401s. Ledger'd for §3.5 UX arc.

## Verifications performed at HEAD `3bd3df386`

- `pytest tests/test_vip_expiry.py -x -v` → 9 passed in 201s
- Django-shell wiring probe:
  - `app.conf.beat_schedule['cleanup-expired-vip-users']` present with correct crontab + options
  - `app.tasks['core.tasks_vip.cleanup_expired_vip_users']` resolves
  - direct import + `.name` attribute check OK
- `make celery-recycle` post-merge — all 3 workers + beat restarted cleanly

## γ mechanism state (unchanged from S3002 close)

Layer 1 + Layer 2 + Layer 3 still all LIVE at HEAD `3bd3df386`. This session did not touch typed-error-envelope work; ADR-0005 T-slot progress remains **3-of-7 shipped** (T-ENVELOPE-0/1/3). Remaining T-slots: T-ENVELOPE-2 (backend EXCEPTION_HANDLER, needs Chris D-verdict), T-ENVELOPE-4 (migration), T-ENVELOPE-5 (nested), T-ENVELOPE-6 (telemetry polish).

## Folds

- **Fold A — `informational` T-slot-vs-risk-gate scoping.** T-VIP-1 was scoped as a risk-gate PARALLEL to the T-ENVELOPE-N series, not a member. The 7-slot count for T-ENVELOPE remains authoritative. **1st concrete instance** of a risk-gate T-slot completing before its dependent ENVELOPE-N slots. Watch for second before proposing Playbook rule codifying "risk-gate T-slots ship before dependent UX ENVELOPE-N slots."
- **Fold B — `same_pr_mitigatable_deferred_to_next_arc`. Frontend 401 predicate widening.** Per Rigby zoom-out §3: `queryClientErrorHandler.ts:28-30` treats undefined-url as non-auth "fail open"; VIP expiry 401 arrives with url set to `/api/deliverables/` etc., which is non-auth branch, so T-ENVELOPE-3 modal will NOT trigger for VIP expiry today. Not blocking T-VIP-1 (backend enforcement lands regardless of frontend UX). Belongs to §3.5 UX arc. Ledger.
- **Fold C — `informational` test-cache-bust pattern.** Django reverse OneToOne cached-descriptor bit anyone writing `RequestFactory`-based middleware tests. Documented in `_make_vip_user` helper comment. **1st concrete instance** in this repo's test suite. Watch for second; if pattern proliferates, propose test-helper utility.

## Carry-forward

All S3002 carry-forwards remain OPEN (see S3002 handoff §"S3003 carry-forward seeds"). This session did not close any of them. New carries:

- **Frontend §3.5 UX** (Fold B above) — widen T-ENVELOPE-1 handler auth-branch predicate OR route VIP-expiry 401s through a dedicated modal path.
- **ADR-0005 T-slot queue** — 4 remaining T-slots (T-ENVELOPE-2/4/5/6). T-VIP-1 now ✅ shipped.

## Governance

No Playbook amendments this session. No ADRs authored or updated. Fold A + Fold C are `informational` (1st-trigger candidates awaiting 2nd instance). Fold B is same-PR-mitigatable-but-deferred to §3.5 UX arc — recorded here so future §3.5 work has the pointer.

Rigby A2 pre-merge SIGN cycle followed PLAYBOOK-7.7.2 (tool_runs + line citations mandatory) — 7 real tool_runs, zero rubber-stamp. Chris-facing decision framing followed PLAYBOOK-7.7.3 (plain-English "do we lose anything?" + "is it more work later?" + ≤1 decision).

## HEAD at close

`3bd3df386` (PR #3679 merged) + docs cascade PR (this file + 00-START refresh + INDEX regen + wrapper pin bump).
