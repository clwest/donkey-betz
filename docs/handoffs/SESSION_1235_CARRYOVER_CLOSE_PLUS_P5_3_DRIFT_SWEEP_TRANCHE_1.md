# Session 1235 — carryover-close P4/P5#1/P5#2 + P5#3 dead-substrate drift sweep Tranche 1 (6 PRs), 9 PRs total

**Status:** Session-spanning two arcs in one day. Arc A closed all four Session 1234 P-series carryover items. Arc B opened the Session 1236 audit deliverable then immediately executed Tranche 1 (6 of 6 named live-wired files, except deferred `views_knowledge.py`) at Chris's direction.

**Date:** 2026-06-25 (UTC, same day as Session 1234 close arcs).
**Active conversation:** `pa-0f08fc48ec914917` (continues from Session 1234; ~30+ turns added this session; health check pending at close — see "Active Conversation" below).
**Companion handoffs:**
- [`SESSION_1234_FIRST_FIRE_FIXES_PLUS_DRIFT_FRAMING.md`](./SESSION_1234_FIRST_FIRE_FIXES_PLUS_DRIFT_FRAMING.md) — D1-D8 morning-brief arc
- [`SESSION_1234_DOCS_CORPUS_ARC_D9_THROUGH_D16.md`](./SESSION_1234_DOCS_CORPUS_ARC_D9_THROUGH_D16.md) — D9-D16 docs-corpus retrieval arc
- [`SESSION_1234_BROAD_EXCEPT_SWEEP_D17_THROUGH_D21.md`](./SESSION_1234_BROAD_EXCEPT_SWEEP_D17_THROUGH_D21.md) — D17-D21 broad-except sweep arc

## TL;DR

Session 1235 opened on Session 1234's four open P-series carryover items, closed all four, then Chris invoked the queued Session 1236 audit ("29-file `unified_embeddings`/`ai_unified_platform` drift sweep") early and we executed Tranche 1 end-to-end (6 PRs across 6 production files, all named live-wired surfaces closed).

Two major findings surfaced mid-session that reframe the audit scope:
1. **Original 29-file count was inflated** — a sharper grep (only real bug shapes: `psycopg2.connect`, `database='ai_unified_platform'`, `FROM unified_embeddings`) showed many of the original matches were references to the legitimate `UnifiedEmbedding` Django model + dict key names in JSON responses + docstring mentions. True production-bug surface was ~6 files (now all closed), not 29.
2. **`core/views.py` is shadowed dead code** — Python package resolution makes `core/views/` (package) win over `core/views.py` (module). Mid-PR test failure caught this. Session 1236 follow-up: audit whether to delete the shadowed file entirely.

Other discoveries: `codebase_awareness.py` fires `psycopg2.connect()` at IMPORT TIME via module-bottom singleton (silently failing every import for years); `intelligence/core.py` is 889 lines of zero-caller architectural sketch (deleted outright with Rigby's approval).

## PRs (chronological)

| PR | Subject | Closes |
|---|---|---|
| [#2633](https://github.com/clwest/donkey-betz-platform/pull/2633) | `fix(session-1235): BACKEND_INVENTORY services count drift 167 → 354 + verifier baseline refresh` | P4 |
| [#2634](https://github.com/clwest/donkey-betz-platform/pull/2634) | `feat(session-1235): refresh_docs_corpus daily beat task — P5#2 close` | P5#2 |
| [#2635](https://github.com/clwest/donkey-betz-platform/pull/2635) | `fix(session-1235): extracted_metadata clobber root cause — P5#1 close` | P5#1 |
| [#2636](https://github.com/clwest/donkey-betz-platform/pull/2636) | `fix(session-1235): dashboard dead-substrate pivot — P5#3 Tranche 1 PR #1` | T1.1 |
| [#2637](https://github.com/clwest/donkey-betz-platform/pull/2637) | `fix(session-1235): conversation_memory ORM pivot — P5#3 Tranche 1 PR #2` | T1.2 |
| [#2638](https://github.com/clwest/donkey-betz-platform/pull/2638) | `fix(session-1235): personal_knowledge_list dead-substrate deprecation — P5#3 Tranche 1 PR #3` | T1.3 |
| [#2639](https://github.com/clwest/donkey-betz-platform/pull/2639) | `fix(session-1235): personal_memory_stats + delete_personal_memory ORM pivot — P5#3 Tranche 1 PR #4` | T1.4 |
| [#2640](https://github.com/clwest/donkey-betz-platform/pull/2640) | `fix(session-1235): codebase_awareness retire-to-no-op — P5#3 Tranche 1 PR #5` | T1.5 |
| [#2641](https://github.com/clwest/donkey-betz-platform/pull/2641) | `fix(session-1235): delete dead intelligence/core.py — P5#3 Tranche 1 PR #6` | T1.6 |

## Arc A — P-series carryover close (PRs #2633-#2635)

### PR #2633 (P4) — BACKEND_INVENTORY services count drift

Closed the only active `verify_doc_claims --only-drift` hit at session open. Two-file fix:
- `docs/BACKEND_INVENTORY.md`: 167 → 354 service files
- `core/services/doc_claim_verification.py`: `expected = 336` → `354` (seed-baseline refresh, same pattern as Session 1223 audit #8)

Verification: `verify_doc_claims --only-drift` returns 0 drifts post-merge.

### PR #2634 (P5#2) — `refresh_docs_corpus` daily beat task

Built the auto-cascade task that prevents the 12-day-stale corpus failure mode that triggered the entire Session 1234 D9→D16 arc. Pre-this-PR, the cascade (`build_docs_index → build_rag_corpus → sync_docs_index_to_documents → embed`) was manual-only.

**Design Qs routed through Rigby (conv `pa-0f08fc48ec914917`):**
- LOCAL_DENY? **No** — delta cost is sub-penny, local Rigby benefits from fresh corpus
- Cadence? **04:00 Denver** (Rigby pick: 3h pre-morning_brief for cold-cascade headroom; I had leaned 06:00)
- Hash storage? **Django cache** — 1 redundant skip on restart is acceptable
- Step 4 (embed)? **Fan-out via `generate_document_embeddings.delay()`** per doc to avoid 25-min serial beat tasks
- Secondary trigger? **Yes — `unembedded_count > 0`** as self-healing path for partial step-4 failures

**Live smoke test:** First dispatch (empty cache) found 3 new docs since Session 1234 close (the handoff files + PR #2633 doc), cascade ran, 3 embedding tasks dispatched, `took=12.54s`. Second dispatch (cache populated) → skip path, `took=0.28s`. Behavior matches spec exactly.

**First scheduled fire:** tomorrow 2026-06-26 10:00 UTC MDT (04:00 Denver). Expected: skip path (corpus fully embedded).

### PR #2635 (P5#1) — `extracted_metadata` clobber root cause

The Session 1234 D9 sidestep finally fixed at the source. Three-part PR:
1. **Merge-not-overwrite at 4 sites:** `content/views.py:319`, `core/tasks_misc.py:1678`, `core/tasks_media.py:649` + `:836`. Pattern: `{**(existing or {}), **new}`.
2. **Sync update path:** `sync_docs_index_to_documents` UPDATE branch now also refreshes `extracted_metadata` (self-heals any future clobber on next content-change pass).
3. **Migration 0047:** Backfills 3 locally-verified clobber victims (`source='imported' AND processor='TextProcessor' AND scope absent` → restored `scope='docs_index'`).

**Rigby design upgrade:** my proposal was a one-shot ORM snippet for the backfill; she pushed for a Django migration for deterministic prod application. Adopted.

**Post-migration verification:** 2732/2732 imported docs now have `scope='docs_index'` (was 2729). Sample row "INITIATIVES FIRST BACKBONE" — previously `{processor, encoding, file_size}` only — now has scope merged in + processor keys preserved.

## Arc B — Session 1236 audit Tranche 1 (PRs #2636-#2641)

Chris invoked the audit early (the "Bigger drift finding" that Rigby and I had agreed to defer was unblocked at his direction). Six PRs landed end-to-end.

### Pre-arc setup

- Created audit deliverable `feed2d81-ee2f-44c0-8f17-816591d2a3ff` via Rigby (Donkey Betz workspace). Title: "P5#3 drift sweep: eradicate unified_embeddings/ai_unified_platform legacy surfaces."
- Rigby produced a Tranche-1 inventory recommending start order:
  1. dashboard files (read-only, lowest risk — establishes pivot recipe)
  2. `conversation_memory.py` (live-imported utility)
  3. `core/views.py` embedding-stats block
  4. `views_knowledge.py` (write-path schema conflict → DEFER pending Chris's caller evidence)

### PR #2636 (T1.1) — dashboard dead-substrate pivot

`dashboard/views.py` (2 functions) + `dashboard/real_time_monitor.py` (1 function). Pivoted from dead `unified_embeddings`/`ai_unified_platform` to live `DocumentEmbedding` ORM. Removed misleading hardcoded fallbacks (`67922`, `265174`).

**Bug caught mid-test:** `timezone.now().date()` returns UTC date but Django's `__date` lookup respects `TIME_ZONE=America/Denver`. Late-evening rows that crossed midnight UTC were getting missed. Fix: `timezone.localdate()` at both pivot sites. Same lesson re-applied in PRs #2637 + #2639.

11 tests green.

### PR #2637 (T1.2) — `conversation_memory.py` ORM pivot

Pivoted the legacy `core.conversation_memory.ConversationMemory` singleton (psycopg2 raw-SQL into non-existent `unified_embeddings`) to the canonical `core.models.ConversationMemory` Django model — which was sitting in `models.py` the whole time with the exact shape needed (user / message / response / agents_used / intent / success / created_at).

The "learning loop" referenced in chat-path docs had been silently broken since file creation. Every user/assistant exchange evaporated.

**Preserved:** hallucination filter (6 known bad-content markers), singleton + class import contract, method signatures + return shapes.
**Dropped:** `embedding` column write (no column on new model), extra metadata fields (no JSONField).

19 tests green.

### PR #2638 (T1.3) — `personal_knowledge_list` deprecation

Mid-PR finding: **`core/views.py` is shadowed dead code** — Python's `core/views/` package wins over `core/views.py` module. The 7 dead-substrate refs in `core/views.py` are all in shadowed copies. Live function is at `core/views/main.py:1048`.

Pivoted BOTH copies (live + shadowed) to honest empty-shape deprecation. Same defer logic as `views_knowledge.py` (same `/api/v1/personal-knowledge/*` URL family — coupled feature surface).

9 tests green, including AST-walk source-level guards across both files.

### PR #2639 (T1.4) — `personal_memory_stats` + `delete_personal_memory` ORM pivot

Two of three functions in `core/views_personal_memories.py` pivoted to live `UserEmbedding` ORM (same model D21 PR #2631 validated for the read-path). Third function `search_personal_memories_api` was already clean (delegates to D21-fixed `search_personal_memories`).

**Latent decorator bug caught:** the `@require_personal_memory_access` decorator passes `user_id=` as kwarg, but view signatures were `def view(request):` → `TypeError`. Pre-pivot tests never exercised the path; my APIRequestFactory tests caught it. Fixed via `**kwargs` absorption. Surfaced for Session 1236: `search_personal_memories_api` has the same latent bug, untouched per "don't fix outside scope."

11 tests green.

### PR #2640 (T1.5) — `codebase_awareness.py` retire-to-no-op

Discovered the module was firing `psycopg2.connect()` at IMPORT TIME via the module-bottom singleton. Importing the module triggered a dead-DB connect; the exception was swallowed; the singleton came up with empty state; the mgmt command (`ingest_codebase`) silently reported "✅ success" with zero stats every run.

Retired to honest no-op facade (kept the class + singleton for import compat with the one caller; all methods return empty/zero shapes; preserved pure-Python helpers `get_file_hash` + `extract_node_content`).

**Why retire not pivot:** the feature has been broken since file creation. Pivoting writes to `DocumentEmbedding` would embed thousands of code components against OpenAI ($$$) for a feature with no proven demand. Session 1236+ revisits if it becomes a real product requirement.

18 tests green. `python manage.py ingest_codebase` smoke-verified.

### PR #2641 (T1.6) — `intelligence/core.py` deletion (-889 lines)

Truly dead architectural sketch. Zero imports anywhere in the codebase. Connects to a non-existent `'intelligence'` database. Unconditionally imports `pgvector.psycopg2 / openai / redis` (heavy import-time deps).

**Rigby's call:** _"Deletion is fine when caller-evidence is definitive. Here it is."_ Approved via conv `pa-0f08fc48ec914917`.

Added 2 regression-guard tests:
- `test_intelligence_core_module_does_not_exist` (via `importlib.util.find_spec`)
- `test_no_callers_assume_universal_intelligence_layer_exists` (greps production code)

## Audit scope corrections discovered mid-session

The original 29-file count from Session 1235 P5#3 verification was inflated. A sharper grep (only `psycopg2.connect`, `database='ai_unified_platform'`, `FROM unified_embeddings`/`INTO unified_embeddings` patterns) showed the real production-bug surface was ~6 files (now all closed except deferred `views_knowledge.py`).

The original 29 included:
- References to the **legitimate `UnifiedEmbedding` Django model** at `persistence.models.UnifiedEmbedding` (real table, 0 rows currently — different concern, not a bug)
- Dict key names in JSON API responses
- Docstring mentions in already-pivoted files
- Test source-guards I myself added in PRs #2636-#2641

**True remaining real-bug surface (post-Tranche 1):**
- `core/views_knowledge.py` (3 psycopg2.connect — DEFERRED pending Chris's caller evidence)
- Tranche 2 mgmt cmds: `mythology/management/commands/clean_mythologies.py` (6 FROM unified_embeddings)
- Tranche 3 scripts: 3 verification scripts + 2 mgmt scripts (`scripts/upload_unified_docs.py`, `scripts/backfill_embeddings.py`)
- Tranche 4 cleanup: 6 pre-existing dead unit tests in `tests/unit/`

## Operational invariants (post-Session 1235)

1. **`refresh_docs_corpus` beat task** runs daily 04:00 Denver. Hash-delta gated; self-healing on partial step-4 failures via unembedded-count secondary trigger. First scheduled fire: tomorrow.
2. **Doc-claim verifier drift = 0** (was 1 medium at session open).
3. **2,732 / 2,732 docs corpus rows** have `scope='docs_index'` in extracted_metadata (was 2,729 pre-PR #2635 + migration 0047).
4. **Dashboard endpoints** report real `DocumentEmbedding` counts, not hardcoded fallbacks.
5. **Personal memory endpoints (`/api/v1/personal-memories/{stats,delete}/`)** use live `UserEmbedding` ORM with strict user-scoped access control.
6. **`codebase_awareness` singleton** no longer fires DB connect at import time.
7. **`intelligence/core.py`** is deleted; regression-guard tests prevent silent restoration.

## Worker state

- Workers restarted post-PR #2634 merge (new `@shared_task`): `pkill -9 -f celery; rm -f .celery*.pid; make celery`. Verified 5 workers + beat picked up `refresh_docs_corpus` via `celery -A core inspect registered`.
- No further worker restarts needed for PRs #2635-#2641 (no new tasks; pivots were mgmt-command code, view code, or facade rewrites).

## Active conversation

`pa-0f08fc48ec914917` — opened Session 1234 mid-day, continues across all of Session 1235. Estimated ~30+ turns added this session covering 5 design Q exchanges + 1 audit deliverable creation. **Health check at Session 1236 open is mandatory** (not done at this close due to session-close mechanics priority; recommend Chris ask Rigby to score the conv first thing).

## Memory rule updates

No new feedback memory rules added this session. Existing rules reinforced through use:
- `feedback_test_real_db_for_queryset_semantics` — applied across all 6 Tranche 1 PRs
- `feedback_corpus_walks_surface_mechanism_drift` — drove the decision to log the audit as Session 1236 deliverable rather than cram it into Session 1235 (Chris later overrode and we executed early)
- `feedback_claude_directs_rigby_then_verifies` — design-pass-through-Rigby pattern used for PR #2634 (5 Qs) and PR #2641 (delete-vs-retire call)
- `feedback_verifier_loop_pattern` — applied to verify Rigby's deliverable creation via direct ORM check

## Carryover into Session 1236

### Active follow-ups from Session 1235 (the audit arc deliverable)

Audit deliverable `feed2d81-ee2f-44c0-8f17-816591d2a3ff` lists all remaining tranches. Priority order:

1. **`views_knowledge.py` deferral resolution (PR #7 of Tranche 1)** — needs Chris's caller evidence call. Three options per Rigby: (a) verify-then-delete if zero callers, (b) pivot with new `UserEmbedding.content_type='personal_knowledge'` CHOICES + migration, (c) hard-deprecate to 410 Gone.
2. **Tranche 2 — mgmt cmds:** `mythology/management/commands/clean_mythologies.py` (6 FROM unified_embeddings — likely retire/delete pattern like codebase_awareness)
3. **Tranche 3 — scripts:** `scripts/{backfill_embeddings,upload_unified_docs}.py` + 3 verification scripts (probable deletion candidates per Rigby's "scripts can be deleted or pivoted")
4. **Tranche 4 — dead pre-existing unit tests:** 6 files in `tests/unit/` (`test_code_embeddings`, `test_code_rag`, `test_embeddings_rag`, `test_embeddings_working`, `test_encryption_migration`, `test_rag_direct`, `test_rag_with_existing_embeddings`) — delete or pivot to exercise the live ORM substrates

### Bonus carry-overs (out-of-scope discoveries logged)

5. **`search_personal_memories_api` latent decorator-kwarg bug** — same `TypeError: unexpected keyword argument 'user_id'` shape as PR #2639 fixed in the two pivoted siblings. One-line `**kwargs` fix.
6. **`core/views.py` shadowed dead code audit** — Python package resolution makes the whole `core/views.py` file unreachable in production. Likely deletion candidate after verifying every function in it is also in `core/views/main.py`.
7. **`dashboard/at_a_glance.py` error log analyzer** — references the dead-DB error pattern as a "known issue with auto-fix suggestion." The suggested fix ("rename `ai_unified_platform` → `unified_donkey_betz`") is outdated; real fix is the ORM pivot pattern. Update the analyzer's error pattern map.

### Pre-existing Session 1234 carryover tail (unchanged from start-here)

- Smoke-harness mode inconsistency (Session 1231 F5, LOW-MEDIUM)
- Smoke-probe tagging for AgentExecution (Session 1231 F1 / R2 REC-2, MEDIUM)
- Promote `scripts/smoke_all_agents.py` → `manage.py smoke_all_agents` (Session 1231 F6, LOW)
- Audit `5318da3e-…` §R2 amendment (Session 1231 F3, P3)
- Engineer workspace staleness (Session 1230 F3, MEDIUM)

### Chris-side carryover

- **Anthropic credit refill** at https://console.anthropic.com/billing
- **CI billing** still failing — all 9 Session 1235 PRs admin-merged via `--admin`
- **Local-only default** still active (Chris's standing rule)

## Doc-claim drift verifier at close

Expected: 0 drift (was 1 medium at session open; closed by PR #2633). Re-run at close.

## Session content quality reflection (per `feedback_content_presence_vs_quality`)

Session 1235 shipped 9 PRs touching 6 production files + 1 migration + 60+ new tests. All shipped with green tests + smoke verification + ORM-side post-fix counts. Quality dimension:
- **Persistence verified:** every PR's behavioral test exercised the LIVE pivoted code path (not mocked queryset). Per `feedback_test_real_db_for_queryset_semantics` discipline.
- **Mid-session findings → documented + carryover:** 3 bonus discoveries (`core/views.py` shadowing, decorator-kwarg bug, error-analyzer staleness) all surfaced honestly + queued for Session 1236 rather than silently bridged.
- **Scope corrections done honestly:** audit-size finding (29 → ~6 production files) was framed transparently in PR descriptions + this handoff, not buried.

Content presence ≠ content quality concern: deferred. The PR diffs themselves are the unit of work this session; no LLM-generated artifacts produced that need quality scoring.
