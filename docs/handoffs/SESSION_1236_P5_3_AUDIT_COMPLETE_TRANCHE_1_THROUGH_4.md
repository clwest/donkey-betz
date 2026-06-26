# Session 1236 — P5#3 drift-sweep audit COMPLETE across Tranche 1-4, 7 PRs total

**Status:** Closes the P5#3 drift-sweep audit deliverable in full. All 4 tranches landed end-to-end. Audit deliverable `feed2d81-ee2f-44c0-8f17-816591d2a3ff` marked `completed` at session close.

**Date:** 2026-06-26 (UTC, same UTC day as Session 1235 close — three sessions ran continuously across the 06-25/06-26 UTC boundary).
**Active conversation:** Started Session 1236 with `pa-0f08fc48ec914917` (continuation from Session 1235), rotated mid-session to `pa-a2443db2e43a42dc` per Rigby's own health-check recommendation. See "Rotation" below.
**Companion handoffs:**
- [`SESSION_1235_CARRYOVER_CLOSE_PLUS_P5_3_DRIFT_SWEEP_TRANCHE_1.md`](./SESSION_1235_CARRYOVER_CLOSE_PLUS_P5_3_DRIFT_SWEEP_TRANCHE_1.md) — preceded this, opened Tranche 1 (6 of 7 named files)

## TL;DR

Session 1236 opened with a Rigby health check (75/100 continue with explicit "rotate before Tranche 2/3/4 execution" trigger) + a Rigby+Claude verification pass against the Session 1235 close state (10 PRs grounded against git/ORM). Both passes clean.

Chris then made the views_knowledge.py decision (builder-remembers-but-forgot-using) → delete the orphan personal-knowledge feature (Tranche 1 PR #7, -489 lines). After that, Tranches 2/3/4 executed end-to-end in 4 more PRs (one per tranche, 5 of the 7 files in T3/T4 were bulk-deleted in single PRs since they're pattern-identical orphans).

Mid-session conv rotation per Rigby's recommendation — fresh thread `pa-a2443db2e43a42dc` titled "Session 1236 — P5#3 Drift Sweep (Tranche 2/3/4 execution)" carried the Tranche 2/3/4 work.

## PRs (chronological)

| PR | Subject | Tranche |
|---|---|---|
| [#2643](https://github.com/clwest/donkey-betz-platform/pull/2643) | `delete orphan personal-knowledge feature` (-489 lines) | T1 PR #7 (final) |
| [#2644](https://github.com/clwest/donkey-betz-platform/pull/2644) | `chore: rotate pa_local.sh pin to pa-a2443db2e43a42dc` | infra |
| [#2645](https://github.com/clwest/donkey-betz-platform/pull/2645) | `clean_mythologies retire cleanup step` (-85 + retired) | T2 PR #1 |
| [#2646](https://github.com/clwest/donkey-betz-platform/pull/2646) | `delete 5 dead one-shot scripts` (-1,624 lines) | T3 (bulk) |
| [#2647](https://github.com/clwest/donkey-betz-platform/pull/2647) | `delete 6 dead zombie unit tests` (-1,110 lines) | T4 (bulk) |

(Session 1235 PRs #2636-#2641 closed Tranche 1 PRs #1-#6; this session opened with #2643 to close T1 PR #7.)

## Pre-execution discipline (P0 + P1)

### P0 — Rigby conversation health check

`tools/pa_local.sh "session_tool action=health_check"` returned:
- **Score: 75/100** (down from 100/100 at Session 1234 close — meaningful drop after ~30+ turns in Session 1235)
- **Recommendation: continue** with rotation trigger _"Rotate when we start implementing Tranche 2/3/4 so the new thread can be audit execution rather than audit discovery + design."_
- Topic count 6/6 boundary; hallucination risk self-rated 7/10 (Rigby flagged she couldn't independently verify "6/6 Tranche 1 shipped" from in-conv memory alone)

### P1 — verification pass against ground truth

Rigby ran 5 tool checks (`repo_tool`, `scheduled_tasks_tool`, `db_health_tool`, `deliverable_tool detail`). Claude cross-checked 2 gaps she didn't cover (git log + Document scope=docs_index count). All PASS with 0 drift from Session 1235 close summary. State grounded; Tranche 2-4 execution proceeded on verified facts.

## Tranche 1 final PR — orphan personal-knowledge feature deletion (PR #2643)

Chris's evidence: _"I do remember when we started that, but I honestly forgot all about doing it lol"_ — strongest possible deletion signal (builder-remembers-but-forgot-using).

**Scope:** 4 endpoints (`upload`/`delete`/`list`/`stats`) + `core/views_knowledge.py` (235 lines) + `personal_knowledge_list` shadowed copies in `core/views.py` + `core/views/main.py` + URL wiring + the PR #2638 deprecation tests (now obsolete).

**Net:** -489 lines.

**Why no 410-Gone preserve:** Chris pushed back on my over-engineered "deprecation logging + monitor" framing with _"theres a lot of things we haven't used in 30 days lol"_ — 30-day-non-use is too common a state to justify deprecation infrastructure. Honest deletion is right when the feature is functionally redundant with 4 existing surfaces (Document corpus, ConversationMemory, UserEmbedding, workspace deliverables).

**Tests:** 5 new regression-guard tests (file absence, no importable function from either copy, no leftover URL patterns).

## Rotation (PR #2644)

After PR #2643 merged, rotated Rigby per her own recommendation:
- **Retired:** `pa-0f08fc48ec914917` — Sessions 1234-1235 + Session 1236 open. ~50 turns covering audit-discovery + Tranche 1 execution.
- **New:** `pa-a2443db2e43a42dc` — title "Session 1236 — P5#3 Drift Sweep (Tranche 2/3/4 execution)". Carry-forward seeded with audit deliverable scope, Tranche 1 close summary, Tranche 2/3/4 todo, worker state, refresh_docs_corpus first-fire timing.
- **Ownership verified:** `session_tool action=whoami` returned `conversation_owner_username: chris`, `conversation_owner_match: true`.
- `tools/pa_local.sh` updated with new pin + retirement note appended to the prior-pin history.

## Tranche 2 — `clean_mythologies` retire (PR #2645)

`mythology/management/commands/clean_mythologies.py` had 6 `FROM unified_embeddings` queries in its `clean_embeddings()` method (4 ILIKE filters for known hallucinations: Dart/Flutter, Fitness Dashboard, "350 deployments", capability exaggerations + 1 count + per-batch DELETE).

**Zero callers** outside the file itself. **The surrounding mythology ecosystem IS live** elsewhere (`core/consumers_hallucination.py`, `core/tasks.py`, `core/signals/mythology_alert_signals.py`, separate `seed_mythology` mgmt cmd) — so retired-to-no-op is right (preserves `setup_guards` / `setup_patterns` / `generate_summary` which use real Django models).

**Why retire not pivot:** hallucination prevention now happens at WRITE time via `core/conversation_memory.py:HALLUCINATION_INDICATORS` (Session 1235 PR #2637 preserved that filter). Post-hoc cleanup is redundant.

**Tests:** 8 new (5 behavior, 3 source-level guards).

## Tranche 3 — 5 dead one-shot scripts deleted in bulk (PR #2646)

| Script | Lines | Intent |
|---|---|---|
| `scripts/backfill_embeddings.py` | 444 | Vector backfill for AgentKnowledge/SpiderData/UnifiedEmbedding (mixed real + dead targets) |
| `scripts/upload_unified_docs.py` | 363 | Docs upload (superseded by live cascade) |
| `scripts/verification/check_embeddings_integration.py` | 194 | Verify migrated embeddings |
| `scripts/verification/verify_and_enable_embeddings.py` | 272 | Setup script |
| `scripts/verification/verify_complete_isolation.py` | 347 | Memory isolation acceptance test |

**Net: -1,624 lines.**

**Caller evidence:** Zero real callers (the 36 raw grep hits for `backfill_embeddings` resolved to 2 audit-doc refs + 4 refs to a DIFFERENT file in `external-project-docs/ai-content-studio/` + 1 self-docstring usage example). The 3 verification scripts had literal zero refs anywhere.

**Why batch as one PR:** pattern-identical orphans, no semantic groupings, same evidence threshold as `intelligence/core.py` deletion.

**Tests:** 1 parametric `subTest`-based regression guard covering all 5 file paths.

## Tranche 4 — 6 dead zombie unit tests deleted in bulk (PR #2647)

All 6 had identical `pytestmark = [pytest.mark.django_db, pytest.mark.skip(reason="Requires unified_embeddings table from production DB")]` since Session 452:

| File | Lines |
|---|---|
| `tests/unit/test_code_embeddings.py` | 243 |
| `tests/unit/test_code_rag.py` | 131 |
| `tests/unit/test_embeddings_rag.py` | 150 |
| `tests/unit/test_encryption_migration.py` | 126 |
| `tests/unit/test_rag_direct.py` | 228 |
| `tests/unit/test_rag_with_existing_embeddings.py` | 232 |

**Net: -1,110 lines.**

Zero CI signal (skipped = no assertions exercised), pure collection overhead.

**Tests:** 1 parametric regression guard covering all 6 paths.

## Final audit verification

Final sharper grep for real bug patterns (`psycopg2.connect` / `database='ai_unified_platform'` / `FROM unified_embeddings` / `INTO unified_embeddings`) across entire repo (non-archive, non-doc, non-.venv):

```
8 files have hits:
  - core/codebase_awareness.py            ← docstring/comment only (S1235 PR #2640 retired)
  - 7 test files                          ← intentional source-guard assertNotIn() text
```

**0 real bug patterns in production code.** Audit DoD met.

## Audit deliverable status

`feed2d81-ee2f-44c0-8f17-816591d2a3ff` marked `completed` via `content_tool action=content_complete` (per memory `feedback_deliverable_status_via_content_complete` — `deliverable_tool action=update` silently ignores the status field). ORM verified: `status='completed'`, `updated_at: 2026-06-26 02:56 UTC`.

## Operational invariants (post-Session 1236)

All Session 1235 invariants still hold + these additions:
1. `clean_mythologies` mgmt cmd runs cleanly with `[RETIRED]` notice + zero counts.
2. Zero `psycopg2.connect` calls remain in production code (all retired/deleted).
3. Zero `FROM unified_embeddings` / `INTO unified_embeddings` queries remain in production code.
4. Audit deliverable `feed2d81-…` marked `completed`.

## Carryover for Session 1237+

Bonus discoveries surfaced during the audit but NOT part of its DoD:

1. **`search_personal_memories_api` latent decorator-kwarg bug** — `@require_personal_memory_access` passes `user_id=` as kwarg, function signature is `def view(request):`. One-line `**kwargs` fix (same pattern Session 1235 PR #2639 applied to two sibling functions). Surfaced during PR #2639 testing.
2. **`core/views.py` shadowed dead code audit** — Python package resolution makes `core/views/` (package) win over `core/views.py` (module). Likely deletion candidate (potentially -thousands of lines) after verifying every function is also in `core/views/main.py`. Surfaced during PR #2638 + #2643 work.
3. **`dashboard/at_a_glance.py` error log analyzer** — references the dead-DB error pattern with an outdated suggested fix ("rename `ai_unified_platform` → `unified_donkey_betz`"). Real fix is the ORM pivot pattern. Update the analyzer's error pattern map. Surfaced during PR #2636 dashboard work.

Plus pre-existing Session 1235 carryover (unchanged):
- morning_brief 2nd-fire verify (TIME-BOUND, 2026-06-26 13:00 UTC = 07:00 MDT) — first scheduled fire with D3/D4/D5/D6 live
- `refresh_docs_corpus` first scheduled fire verify (TIME-BOUND, 2026-06-26 10:00 UTC MDT = 04:00 Denver) — Session 1235 PR #2634's first ever scheduled run
- Operator Edge Friday-1 dry-run check (2026-06-26 12:00 UTC)
- Brief read → Sub-step D (if morning_brief 2nd fire produced real content)
- Pre-1234 tail (smoke-harness mode, smoke-probe tagging, etc.)

## Active conversation at close

`pa-a2443db2e43a42dc` — Session 1236 Tranche 2/3/4 execution thread. Should carry forward to Session 1237 with whatever new work is queued. Health re-check recommended at S1237 open.

## Worker state

No new `@shared_task` added this session. No worker restart needed.

## Doc-claim drift verifier at close

Expected 0 drift. Run at close.

## Memory rule updates

No new feedback memory rules added this session. Existing rules reinforced through use:
- `feedback_session_open_with_orient` — session opens with P0 health check (used)
- `feedback_claude_directs_rigby_then_verifies` — verification pass + deliverable creation pattern used throughout
- `feedback_corpus_walks_surface_mechanism_drift` — original audit motivation
- `feedback_test_real_db_for_queryset_semantics` — all behavior tests written against real DB
- `feedback_deliverable_status_via_content_complete` — used at close to mark deliverable completed

## Session content quality reflection (per `feedback_content_presence_vs_quality`)

Session 1236 shipped 5 PRs (PR #2643 close-T1, #2644 rotation infra, #2645 T2, #2646 T3, #2647 T4) totaling **-3,308 net production lines** and ~30+ regression-guard tests. The session was almost entirely deletion + retirement work — high signal/noise ratio. No LLM-generated artifacts produced that need quality scoring.

The audit itself was the deliverable. Closed cleanly.
