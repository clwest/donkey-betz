# Session 3019 — AgentMemory Scope Predicate (ADR-0008 A.2)

**Date:** 2026-07-28 · **HEAD at close:** docs cascade → `d516743c5` (PR #3723 fix)

## What shipped

**PR #3723 (`d516743c5`) — `feat(s3019): AgentMemory scope predicate (ADR-0008 A.2 cross-user isolation)`**

Ratified path from S3018 close 00-START Option A → ADR-0008 draft → Rigby T0 SIGN AGREE Layer 1 + REVISE Layer 2 (3 changes applied pre-ratification) → Chris ratified 2026-07-28 → implementation shipped → Rigby T1 SIGN AGREE Layer 1 + AGREE Layer 2 → merge → recycle → live smoke passed.

Changes:
- **NEW** `docs/adr/ADR-0008-agent-memory-scope-predicate.md` — accepted 2026-07-28. Sixth predicate on the `object_authz.py` surface.
- **MODIFIED** `core/security/object_authz.py`:
  - `can_read_agent_memory(user, memory)` — True iff user is assigned to `memory.agent`, OR (superuser AND agent has no user_assignments).
  - `scope_queryset_agent_memory(user, qs)` — filters via M2M traversal; `.distinct()` guards duplication.
- **MODIFIED** `core/views_memory_palace.py` — 3 views wired to scope predicate: `get_memory_detail`, `get_memory_connections`, `delete_memory`.
- **NEW** `core/tests/helpers/agent_assignment.py` — `assign_agent_to_user()` factory (ADR-0008 §3.4 per Rigby T0 §a).
- **NEW** `core/tests/test_s3019_agent_memory_scope_predicate.py` — 12 tests (5 predicate + 7 view-wiring).
- **MODIFIED** `core/tests/test_s3017_memory_detail_auth_gate.py` — updated to `assign_agent_to_user()` the test user (S3017 predated A.2 scoping).

Regression: 52/52 pass in 7.177s (40 prior S3013-S3018 + 12 new S3019).

Live smoke post-recycle:
- Anon GET `/api/memory-palace/memory/<real-uuid>/` → 401 `not_authenticated` (S3017 decorator still enforcing anon-reach).
- Superuser (Chris) GET → 200 + memory content (S3019 predicate returns row via null-assignment carve-out; `AgentAssignment` table is empty at HEAD).

## Rigby SIGN cycles this session

1. **T0 SIGN (before coding, on the ADR draft)** — Layer 1 **AGREE-with-shape**, Layer 2 **REVISE-with-3-changes**:
   - §2.2 data-state numbers (984 AgentMemory local ORM vs. 981 verify_table lag; 97 Agents; 0 AgentAssignment — Rigby couldn't verify AgentAssignment via allowlist).
   - §3.1 docstring warning wording tightened.
   - §3.4 `assign_agent_to_user()` test helper added.
2. **T1 SIGN (before merge)** — Layer 1 **AGREE** + Layer 2 **AGREE**. Substantive tool_runs across 3 file reads + edge-case walk-through. Confirmed the earlier predicate bug (initial `can_read_agent_memory` had superuser fall-through that returned True on any memory; caught by test-run and patched pre-SIGN) was fixed. Zoom-out §a-d all clean.
3. **Post-merge live smoke** — Claude-local curl (per S3017 tool-gap ledger) confirmed anon-401 + superuser-200 on real UUID.

**Rigby SIGN quality this session:** 2 substantive SIGN cycles, both tool-grounded, zero rubber-stamp. **Matches S3010–S3018 pattern — 11 sessions continuous.**

## Zoom-out folds

- **Fold A (Rigby T0 §a) — `same_pr_actionable → resolved`**: `assign_agent_to_user()` test helper shipped ADR §3.4 pre-ratification.
- **Fold B (Rigby T1 §c) — `informational`**: predicate-shape-table comment in `object_authz.py` as a readability improvement. Not blocking; future arc.
- **Fold C (implementation bug caught in-flight) — `informational`**: initial `can_read_agent_memory` had a superuser fall-through that returned True on any memory. Caught by the first test run at `test_can_read_agent_memory_predicate` and patched before commit. Test-first discipline paid off.
- **Fold D (S3017 test migration) — `same_pr_actionable → resolved`**: S3017 tests updated to `assign_agent_to_user()`; the alternative (leave S3017 tests exercising pre-A.2 behavior) would have encoded the bug as expected behavior per Rigby T1 §b.

## Forward carries

**New from S3019:**
- **Fold B (Rigby T1 §c)** — predicate-shape-table comment in `object_authz.py`.
- **Method-decorator detection extension** (from S3018 Fold) — catch `@method_decorator(superuser_required)` on CBV methods.
- **A.2 pattern generalization** — S3016 F-2 → S3017 A.1 decorator → S3018 invariant test → S3019 A.2 predicate. This arc closes the memory-palace class. Same pattern likely applies to `AgentExecution` detail endpoints, `MemoryConnection` endpoints, and cluster/room subroutes. **Recommend audit + rollout.**

**Carried from S3018 (STATUS UPDATED):**
- **S3018 Fold C (A.2 cross-user isolation)** — **CLOSED by S3019 PR #3723**.
- **S3018 Fold B (test-time advisory for decorator-chain-break)** — still open, future arc.
- **S3018 Fold D (Rigby response truncation 1st trigger)** — still open. This session Rigby T1 SIGN was NOT truncated; Fold D remains at 1st trigger.

**Carried from S3017 (STATUS UPDATED):**
- **S3017 Fold A (route-decorator invariant)** — CLOSED by S3018.
- **S3017 Fold C (A.2 cross-user isolation)** — **CLOSED by S3019 PR #3723**.
- **S3017 Fold D (Rigby Tool Gap Ledger — web_fetch_tool DELETE + http_smoke_test middleware-bypass)** — still open; this session used Claude-local curl again for the DELETE + superuser smoke.

**Carried from S3016 / older** — all preserved from S3018 close 00-START.

## Substantive result

The four-part memory-palace auth trajectory is now closed:
1. **S3016 F-2 audit** — surfaced the bare-prefix bypass class + specifically flagged `/api/memory-palace/memory/<uuid>/` as unscoped-and-anon-readable.
2. **S3017 A.1 decorator gate** — closed anon reach on all three memory-palace sibling routes (detail read, connections read, DELETE mutation).
3. **S3018 route-decorator invariant** — locked the class so no future bare-prefix child ships ungated.
4. **S3019 A.2 predicate** — closed the authenticated cross-user gap. Row-level scoping via M2M traversal; null-assignment superuser carve-out for system agents; behavior-neutral under current single-user data state (Chris keeps full visibility via carve-out).

Four sessions, four PRs, one full class of vulnerability closed with tests + docs + invariant + predicate. Clean substrate-hardening arc.
