# Session 1237 — P5#3 audit bonus carryovers close, 3 PRs (-1,558 net lines)

**Status:** Closes all 3 bonus carryovers surfaced during the Session 1235-1236 P5#3 drift-sweep audit. No new audit deliverable — these were already-queued follow-ups from the parent audit's discovery work.

**Date:** 2026-06-26 (UTC, ~22:00-22:30 CDT / 03:00-03:30 UTC).
**Active conversation:** `pa-a2443db2e43a42dc` — fresh thread continued from Session 1236. Health 100/100 at S1237 open, no rotation needed during this session.
**Companion handoffs:**
- [`SESSION_1236_P5_3_AUDIT_COMPLETE_TRANCHE_1_THROUGH_4.md`](./SESSION_1236_P5_3_AUDIT_COMPLETE_TRANCHE_1_THROUGH_4.md) — preceded this; closed the formal audit + surfaced these carryovers

## TL;DR

Session 1237 opened with a Rigby health check (100/100 continue, fresh) at 22:05 CDT — confirmed all 06-26 calendar P1 fires were still 7-10h away. Chose to use the session window for the 3 queued P2 bonus carryovers from the closed P5#3 audit instead of stopping.

Three PRs landed in execution order:

| PR | Subject | Lines |
|---|---|---|
| [#2649](https://github.com/clwest/donkey-betz-platform/pull/2649) | P2.a — `search_personal_memories_api` decorator-kwarg fix | +140 / -3 |
| [#2650](https://github.com/clwest/donkey-betz-platform/pull/2650) | P2.c — `dashboard/at_a_glance.py` delete | +75 / -415 |
| [#2651](https://github.com/clwest/donkey-betz-platform/pull/2651) | P2.b — `core/views.py` shadowed delete | +105 / -1,460 |

**Net Session 1237: ~-1,558 lines.** Mostly the massive shadowed `core/views.py` deletion.

## PR #2649 — `search_personal_memories_api` decorator-kwarg bug fix (P2.a)

One-line `**kwargs` fix to absorb the `user_id` passthrough that `@require_personal_memory_access` injects. Pre-fix the view signature was `def view(request):` → DRF dispatch raised `TypeError: unexpected keyword argument 'user_id'`.

Same shape Session 1235 PR #2639 fixed in the two sibling functions (`personal_memory_stats`, `delete_personal_memory`). At PR #2639 time `search_personal_memories_api` was left untouched per "don't fix outside scope" and queued as a bonus carryover. This PR resolves it.

**Why the bug went silent:** zero observed callers — frontend uses the workspace memory surface directly. Pre-fix dispatches would have raised TypeError → 500. No clients = no error reports.

**Tests (5):** 4 behavioral + 1 parametric guard over all 3 views in the file via `inspect.signature` (prevents regression on any to a bare `def view(request):` shape).

## PR #2650 — `dashboard/at_a_glance.py` delete (P2.c — scope-corrected mid-execution)

**Original framing:** "update the error-pattern map" (assumed live tooling that operators read for auto-fix suggestions).

**Triple-grep at execution:** zero importers in `.py`, zero refs in `.sh`/`.md`/`.yml`/`.toml`. Only "caller" is the file's own `def main()` example block.

**Pivot:** Routed framing change through Chris ("delete it" — confirmed). Same orphan-deletion pattern as `intelligence/core.py` (PR #2641) and the Tranche 3 scripts (PR #2646).

**Bonus value:** the deleted error-pattern map's suggested fix for `database "ai_unified_platform" does not exist` was wrong even when written — it suggested `sed -i "" "s/ai_unified_platform/unified_donkey_betz/g" ai_core/settings.py`, but `ai_core/settings.py` doesn't actually contain the string `ai_unified_platform` (the connection strings were in app-level `psycopg2.connect` calls, which Session 1235-1236 audit retired/deleted). If any operator had run the sed command it would have been a no-op. Bad data + zero readers = deletion-was-right.

**Tests (2):** file absence guard via `importlib.util.find_spec` + repo-wide grep guard for residual imports.

## PR #2651 — `core/views.py` shadowed dead-code delete (P2.b — the BIG one, -1,457 lines)

Discovered during Session 1235 PR #2638 work: Python package resolution makes `core/views/` (package) win over `core/views.py` (module file). The 7 dead-substrate refs in `core/views.py` at that time were all in shadowed copies; live was at `core/views/main.py`.

**This session's audit:** systematic set-diff of function names between the two files.

```
core/views.py:    30 functions
core/views/main.py: 30 functions
ONLY in core/views.py: ∅ (empty)
ONLY in core/views/main.py: ∅ (empty)
```

**100% duplication.** Confirmed via `find_spec('core.views').origin` → `core/views/__init__.py` (package wins, NOT the module file).

**Origin per `__init__.py` comment:** the conversion dated back to Session 728 — _"Original platform views (from core/views.py, now in main.py)"_. The conversion moved everything to `main.py`. `core/views.py` was kept around as dead artifact for unknown reasons. Exactly the kind of dead-code-archeology debt the P5#3 audit was created to eliminate.

**Bypass check:** zero `importlib.import_module` / `runpy` / direct module loaders anywhere in the codebase. All `from core.views import X` imports resolve to the package via `__init__.py` re-exports.

**Bonus cleanup:** updated 2 string references (`setup_codebase_workspace.py` + `system_reality_checker.py`) that pointed at the deleted path to point at `core/views/main.py` (the live file with the same content).

**Tests (4):** file absence guard, namespace still resolves to package, sample 7-function import via package, URL resolver still loads cleanly (1797 patterns unchanged).

**Verification post-deletion:**
- Django boots cleanly
- URL resolver loads 1797 top-level patterns (unchanged)
- All `from core.views import X` imports work
- 21 related-test regression-check across PR #2649 + PR #2639 + PR #2643 + my own deletion guards: all green

## Operational invariants (post-Session 1237)

All Session 1235-1236 invariants still hold + these additions:
1. `search_personal_memories_api` accepts decorator `user_id=` kwarg cleanly (no TypeError on dispatch).
2. `dashboard/at_a_glance.py` deleted; zero refs anywhere.
3. `core/views.py` deleted; 100% of its content was duplicated in `core/views/main.py` and the package re-export chain preserves all import paths.
4. Set-diff parity (`comm -23 / -13`) is the canonical evidence pattern for any future "is this duplicate file a shadow?" audit work.

## Carryover for Session 1238+

**Unchanged from Session 1236-1237 close — calendar P1 fires happen tomorrow morning:**

- `refresh_docs_corpus` first scheduled fire (2026-06-26 10:00 UTC MDT = 04:00 Denver) — Session 1235 PR #2634's first-ever scheduled run. Expected: skip path.
- morning_brief 2nd-fire verify (2026-06-26 13:00 UTC = 07:00 MDT) — Session 1234 D3/D4/D5/D6 first scheduled fire.
- Operator Edge newsletter Friday-1 dry-run (2026-06-26 12:00 UTC) — Session 1228 carryover.
- Brief read → Sub-step D (if morning_brief 2nd fire produced real content)

**Pre-existing tail (unchanged):** smoke-harness mode inconsistency, smoke-probe tagging, promote scripts/smoke_all_agents.py → mgmt cmd, Audit `5318da3e-…` §R2 amendment, engineer workspace staleness, meeting-context leak watch, fleet-smoke wall-clock timeouts.

**Chris-side:** Anthropic credit refill, CI billing (still admin-merging).

## Audit grand-total stats (Sessions 1235 → 1237 combined)

| | Count |
|---|---|
| Formal audit PRs (Tranches 1-4) | 14 |
| Bonus-carryover PRs (Session 1237) | 3 |
| Total PRs | **17** |
| Lines of dead code removed | **~5,000+** |
| Regression-guard tests written | **~100+** |
| Real bug patterns in production code | **0** (verified by final sharper-grep) |
| Audit deliverable status | `completed` (`feed2d81-…`) |

## Active conversation at close

`pa-a2443db2e43a42dc` — health was 100/100 at S1237 open. Added ~6 turns through the 3 PRs + this close. Should still be 95-100. Recommended health re-check at S1238 open.

## Worker state

No new `@shared_task` added this session. No worker restart needed.

## Doc-claim drift verifier at close

Expected 0 drift. Run at close.

## Memory rule updates

No new feedback memory rules added this session. Existing rules reinforced:
- `feedback_session_open_with_orient` — P0 conv health check pattern (used)
- `feedback_claude_directs_rigby_then_verifies` — N/A this session (no Rigby tool calls; pure code work)
- `feedback_test_real_db_for_queryset_semantics` — all behavior tests against real DB
- `feedback_corpus_walks_surface_mechanism_drift` — Session 1235 finding (shadowing) executed in this session

## Session content quality reflection (per `feedback_content_presence_vs_quality`)

Session 1237 shipped 3 PRs totaling -1,558 net production lines. Pure execution work — no design debate, no new audit scope, all 3 picks were already queued from the parent audit's discovery phase. ~10 regression-guard tests written. High signal/noise.

The session's purpose was bonus cleanup — same orphan-deletion + decorator-fix patterns as the parent audit, just at scale. Closed cleanly.
