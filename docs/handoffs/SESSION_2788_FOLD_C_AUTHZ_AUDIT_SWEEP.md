# Session 2788 — Fold C Follow-up: authZ Audit Sweep (3 platform endpoints)

**Ship SHA:** `10110f492` · **PR:** [#3189](https://github.com/clwest/donkey-betz-platform/pull/3189) · **Date:** 2026-07-14

---

## §1 What shipped

Closed the S2787 Fold C `future_trigger` (row 39) + Rigby's T1 same-PR tightening. 3 platform endpoints in `core/views_platform_command.py` gated staff-only with 2 middleware PUBLIC_PATHS entries removed.

**Backend (2 files):**

- `core/auth_middleware.py` — removed 2 PUBLIC_PATHS entries (`/api/platform/celery-debug/` at line 453 + `/api/platform/cleanup-stale-executions/` at line 454). Replaced with S2788 Fold C explanatory comment.
- `core/views_platform_command.py` — added `@login_required + @_platform_staff_only` decorator stack on 3 views:
  - `celery_debug_view` (line 2481, GET) — previously anon-reachable, leaked redis + celery beat + periodic-task state
  - `cleanup_stale_executions_view` (line 2630, POST) — previously anon-reachable POST mutation; also removed `@csrf_exempt`
  - `delete_failed_executions_view` (line 2696, POST/DELETE) — previously any-authed-user reachable; also removed `@csrf_exempt`

**Tests (1 new file):**

- `core/tests/test_platform_authz_sweep_2788.py` — 4 test classes × 3 endpoints = 12 tests:
  - `PlatformAuthzSweepAnonymousTest` — anon → blocked
  - `PlatformAuthzSweepNonStaffTest` — non-staff → 403
  - `PlatformAuthzSweepStaffReachableTest` — staff → not blocked
  - `PlatformAuthzSweepTokenAuthS887PreservationTest` — Token-auth → not blocked

---

## §2 Novel-precedent moments

### 2.1 First "future_trigger fold → next-session ship" cadence proven

Fold C was persisted at S2787 close as `future_trigger`. S2788 opened with it selected as the P0 engineering candidate. Ship shape came in as expected (~45 min actual vs ~1-2h estimated) because the preceding S2787 substrate work (middleware understanding, S887 preservation mechanism, staff-only sentinel pattern) was already load-bearing.

**Signal:** the `future_trigger` classification correctly identified real-but-not-blocking work. The persistence-before-D-verdict discipline (PLAYBOOK-6.10.8) means future sessions can enumerate their next-arc candidates directly from the ledger.

### 2.2 Rigby SIGN response NOT truncated this time

S2786 T2 partial + S2787 T1 severe truncation. S2788 T1: full response landed clean (~230 lines including tool_runs). Suggests truncation is size-dependent — S2788 T1's tool_runs were fewer (5 tool calls vs S2787 T1's 10). Not a reliable pattern yet; watching for third trigger before promoting to substrate concern.

### 2.3 Same-PR tightening cleanly integrated

Rigby's T1 tightening (add `celery_debug_view`) expanded scope by 1 endpoint mid-agreement. Rather than defer to S2789, adopted same-PR because (a) same file, (b) same pattern, (c) same test infrastructure, (d) same coherence-gap that S2787 Fold A was reasoning about. Chris ratified the tightened scope in one yes.

---

## §3 T1 SIGN cycle summary

| Turn | Author | Content | Tool_runs | Outcome |
|---|---|---|---|---|
| T1 | Claude → Rigby | Scope proposal for 2 sites + PLAYBOOK-6.10.9 evidence admission + 2 F-BLOCKING + 3 zoom-out asks | Rigby: 5 (git_info, 4× repo_tool reads on auth_middleware / urls / views_platform_command / object_authz) | Rigby AGREE with same-PR tightening (add celery-debug); both F-BLOCKING cleared with tool_ground evidence |

**Anti-rubber-stamp check:** Rigby's tool_runs non-empty; her T1 verified my claims independently (didn't just echo them) AND added a substantive tightening (celery-debug) I hadn't included in scope. Anti-rubber-stamp discipline confirmed.

---

## §4 Ledger delta

- **At S2788 open:** 39 rows (16/15/8)
- **After T1 fold persistence (pre-D-verdict):** 41 rows (17/15/9)
  - Row 40 (S2788, Rigby tightening, `same_pr_actionable`): "celery_debug_view is @require_GET but in PUBLIC_PATHS…"
  - Row 41 (S2788, broader-audit deferral, `future_trigger`): "Broader PUBLIC_PATHS categorical audit needed…"

---

## §5 Twin-pointer card

📁 **Repo `/` + `/docs/` — S2788 artifacts:**

- **Ship code:** `core/auth_middleware.py`, `core/views_platform_command.py`, `core/tests/test_platform_authz_sweep_2788.py`, `tools/pa_local.sh` (+2/-1 pin refresh)
- **Handoff:** `docs/handoffs/SESSION_2788_FOLD_C_AUTHZ_AUDIT_SWEEP.md` (this file)
- **Predecessors:** S2787 (CSRF cross-file cleanup + Fold C discovery), S2786 (Playbook v0.8.0)

🖥️ **Workspace UI — `/workspaces` surface:**

- **System / Sign Ledger sub-tab** (`?tab=system&sub=sign-ledger`) — 41 rows, including S2788 rows 40+41
- **Live surfaces:**
  - `logs/zoom_out_classifications.jsonl` — 41 rows at S2788 close
  - `logs/session_freshness.jsonl` — grew by 1 at S2788 open
  - `logs/recycle_events.jsonl` — +1 new event from S2788 close (`sha=10110f492284`)

---

## §6 Open items forward-carry

1. **Broader PUBLIC_PATHS categorical audit** — Fold B row 41 as `future_trigger`. Trigger: 4th public+unsafe-method site OR 4th public+sensitive-GET site surfacing in future audits. Not urgent.
2. **N24 anti-rubber-stamp SIGN codification** — still at 4 F-BLOCKING triggers (S2778/S2780/S2786/S2787). S2788 T1 was AGREE (not F-BLOCKING) with tightening; doesn't advance the trigger count. Promotion candidate awaiting 5th F-BLOCKING trigger or Chris directive.
3. **Rigby SIGN response truncation pattern** — 2 observations (S2786 T2 + S2787 T1); S2788 T1 was fine. Not yet 3-trigger. Watching.
4. **CSRF interceptor E2E eyeball follow-up** — verified in S2787 close conversation via DevTools; item retired.
5. **Auth-gate consolidation** — 4 sentinels now (`_platform_staff_only`, `_governance_staff_only`, `_human_staff_only`, `_require_boardroom_staff`). No new sentinel added in S2788. Wait for 5th before promoting to `core/auth_gates.py`.
6. All prior S2787 open runtime items forward-carry unchanged unless S2788 changed them:
   - #2 Fold C follow-up → **CLOSED** in this session (2 sites + celery-debug tightening = 3 sites)
   - #4 CSRF interceptor E2E → CLOSED at S2787 close
   - Others unchanged.

---

## §7 Rebindings post-merge

- **Ledger:** 41 rows (17 actionable / 15 mitigatable / 9 future_trigger)
- **Rule count:** 205 (unchanged; no Playbook amendment)
- **Playbook version:** v0.8.0 (unchanged)
- **Session pin:** `pa-9840f56652674967` (S2788) — retire at close per S2770+ pattern with `force=true`
- **Wrapper default pin:** to be updated with fresh mint at S2789 open (forcing function preserved)
