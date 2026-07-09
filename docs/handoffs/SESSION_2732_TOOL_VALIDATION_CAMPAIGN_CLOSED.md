---
title: "Session 2732 — Rigby Tool Validation Engineering Campaign CLOSED (Batch D + 18-tool scope)"
session_id: 2732
canonical_authority: workspace_canonical
date: 2026-07-09
status: active
tags:
  - session-2732
  - rigby-tool-validation-campaign
  - batch-d-close
  - campaign-close
supersedes: SESSION_2731_TOOL_VALIDATION_BATCH_C_CLOSED.md
---

# Session 2732 — Batch D CLOSED — Rigby Tool Validation Engineering Campaign CLOSED

**Session:** 2732 (close-out session for Batch D + the campaign's original 4-batch / 18-tool scope).
**Date:** 2026-07-09.
**Author:** Claude (Opus 4.7, 1M context) with Chris ratifying every finding-decision gate.
**Predecessor:** [Session 2731 handoff — Batch C close](SESSION_2731_TOOL_VALIDATION_BATCH_C_CLOSED.md).
**Related:** [Session 2729 handoff — Batch B close](SESSION_2729_TOOL_VALIDATION_BATCH_B_CLOSED.md), [Session 2728 handoff — Batch A close](SESSION_2728_TOOL_VALIDATION_BATCH_A_CLOSED.md), [Session 2727 handoff — Playbook v0.1.0 ratified](SESSION_2727_PLAYBOOK_V0_1_0_RATIFIED.md).

## 1. What shipped

**Batch D — Worker & environment discipline of the Rigby Tool Validation Engineering Campaign — CLOSED.** With this close, the campaign's original 4-batch / 18-tool scope is complete.

- **3 tools verified** (PA_USE_FUNCTION_CALLING env flag, Celery worker lifecycle, worker cache behavior).
- **11 code/config patches + 45 regression tests** across the batch.
- **3 observability additions** (`[PA_ROUTING_INIT]`, `[CELERY_WORKER_INIT]`/`[CELERY_WORKER_SHUTDOWN]`, `[DJANGO_CACHE_INIT]`) — every substrate layer now emits a startup log declaring its state.
- **2 bounded LRU refactors** (`_aggregator_cache`, `_service_cache`) using the `platform_config` gold-standard pattern.
- **1 new Makefile target** (`make celery-recycle`) closing the operator-discipline gap Batch D tool 2 documented.
- **293/293 substantive tests pass** across all 18 validation-2728 files + adjacent legacy tests. Zero cross-tool regression.
- **Merged PRs:** [#3019](https://github.com/clwest/donkey-betz-platform/pull/3019) (Batch D tool patches + tests + reports), [#3020](https://github.com/clwest/donkey-betz-platform/pull/3020) (docs cascade).

## 2. Per-tool close summary

### Batch D tool 1 — `PA_USE_FUNCTION_CALLING` env flag

**Report:** [`docs/research/tools/validation/pa_use_function_calling_env_validation.md`](../research/tools/validation/pa_use_function_calling_env_validation.md).

- **Findings:** F-WF-1..6 (4 patched, 1 verified, 1 tests).
- **Patches shipped:**
  - F-WF-1 — code default flipped `'false'` → `'true'` in `settings.py:1662`; narrative doc rewrite naming F-WF-1 explicitly. S1036 architectural intent honored; keyword router is the intentional fallback, not the intentional default.
  - F-WF-2 — `PA_USE_FUNCTION_CALLING=true` on every `celery-*` line in Procfile. Belt-and-suspenders against Railway env drift.
  - F-WF-3 — `[PA_ROUTING_INIT]` startup log at `UnifiedPAEntrypoint` module scope. Fires once per worker at import time.
  - F-WF-4 — `routing_path=fc|keyword` field on `[PA_TASK_SUMMARY]` log line. S1184-class incident recurrence detectable in ≤30 seconds via log grep.
- **Verified:** F-WF-6 — MEMORY `feedback_pa_worker_function_calling_env` accurate at HEAD; 3-test source-level guard pins Makefile + settings.py + unified_pa_entrypoint shape claims.
- **Tests:** 10 in `core/tests/test_pa_use_function_calling_env_validation_2728.py`.

### Batch D tool 2 — Celery worker lifecycle

**Report:** [`docs/research/tools/validation/celery_worker_lifecycle_validation.md`](../research/tools/validation/celery_worker_lifecycle_validation.md).

- **Findings:** F-CW-1..5 (3 patched, 1 verified, 1 tests).
- **Patches shipped:**
  - F-CW-1 — `make celery-recycle` target + Makefile solo-pool implication header comment. Documents that local `--pool=solo` silently ignores `CELERY_WORKER_MAX_TASKS_PER_CHILD=50` from settings.py; gives operators a one-command recycle discipline.
  - F-CW-2 — `worker_process_init` + `worker_process_shutdown` signal handlers in `core/celery.py` emitting `[CELERY_WORKER_INIT]` (pid/ppid/hostname/app) + `[CELERY_WORKER_SHUTDOWN]` (pid/exitcode/hostname) logs. Railway prefork recycle events now grep-visible in ≤1 second.
  - F-CW-3 — `make celery-status` extended to check all 5 workers (added `pa` + `code_jobs` with tail-log failure hints).
- **Verified:** F-CW-4 — MEMORY `feedback_local_celery_stall_playbook` 6-step diagnostic sequence still valid at HEAD (underlying substrate CeleryTaskEvent + Redis broker at db 2 + prefork recycle config intact).
- **Tests:** 14 in `core/tests/test_celery_worker_lifecycle_validation_2728.py`.

### Batch D tool 3 — Worker cache behavior

**Report:** [`docs/research/tools/validation/worker_cache_behavior_validation.md`](../research/tools/validation/worker_cache_behavior_validation.md).

- **Findings:** F-WC-1..6 (2 patched, 3 verified, 1 tests).
- **Patches shipped:**
  - F-WC-1a — `[DJANGO_CACHE_INIT]` INFO log at Django settings-import time declaring effective cache backend + `REDIS_HEALTHY` value + `REDIS_URL`. Silent Redis→LocMemCache fallback (previously signalled only by one WARNING on failure) now grep-visible in first ~100 lines of every worker/web log.
  - F-WC-2a — `@lru_cache(maxsize=64)` refactor on `attention_aggregator._aggregator_cache` + `human_interface_service._service_cache`. Both were unbounded per-user dict caches keyed on `user_id` with no eviction; grew indefinitely under solo-pool local workers (Batch D tool 2 F-CW-1). Mirrors `platform_config` gold standard. Backward-compat `_AggregatorCacheView` / `_ServiceCacheView` preserves any existing observability caller that read `len(_aggregator_cache)` pre-S2731.
- **Verified:**
  - F-WC-3 — LLM client factory caches (`_CLIENT_CACHE`, `_ASYNC_CLIENT_CACHE`) verified bounded at HEAD (O(providers) via (api_key, base_url) tuple keys).
  - F-WC-4 — `platform_config._cached_primary_workspace_id` + `_cached_primary_user_id` `@lru_cache(maxsize=1)` gold standard verified.
  - F-WC-5 — `_backlog_cache` 60-second TTL discipline verified.
- **Tests:** 21 in `core/tests/test_worker_cache_behavior_validation_2728.py`, including 3 Redis DB topology structural guards (db 1 = Django cache, db 2 = Celery broker, db 3 = result backend).

## 3. Substrate observability additions this batch

The three tools together added a startup-log surface across every substrate layer PA/Rigby depends on. An operator can now diagnose a misconfigured worker in ≤30 seconds via three grep queries:

| Log line | Emitted by | Fires at | Reveals |
|---|---|---|---|
| `[PA_ROUTING_INIT]` | `UnifiedPAEntrypoint` module scope | once per worker at import | env=`true`/`false`/`<unset>`, effective bool, routing_path |
| `[CELERY_WORKER_INIT]` | `worker_process_init` signal in `core/celery.py` | per prefork child + once per solo worker at startup | pid, ppid, hostname, app name |
| `[CELERY_WORKER_SHUTDOWN]` | `worker_process_shutdown` signal | per prefork child at recycle + at worker exit | pid, exitcode (0=clean recycle; non-zero=kill) |
| `[DJANGO_CACHE_INIT]` | `settings.py` at import | once per Django process | cache backend (RedisCache vs LocMemCache), REDIS_HEALTHY, REDIS_URL |
| `[PA_TASK_SUMMARY]` (extended) | `_process_message` per turn | per PA request | routing_path=fc\|keyword field (added F-WF-4) |

## 4. Campaign scope closure

The Rigby Tool Validation Engineering Campaign's original 4-batch / 18-tool scope is now complete:

| Batch | Tools | Sessions | Defects | Tests | Notable |
|---|---|---|---|---|---|
| **A** | 5 | S2728 | 17 | 64 | 3 MEMORY annotations |
| **B** | 5 | S2729 | 10 | 51 | **2 SECURITY-class fixes** (kb_ingest cross-user provenance leak + SSRF surface) |
| **C** | 5 | S2731 | 19 | 110 | **4 shared primitives extracted** (`_CONTEXT_INJECTION_ENV_ERRORS`, `_build_fresh_summary`, `td_limit_envelope.compute_limit`, `_classify_retryable` / `_ERROR_CODE_RETRYABLE`); 1 migration |
| **D** | 3 | S2731 → S2732 | 11 | 45 | 3 observability additions, 2 bounded LRU refactors, 1 mgmt command target |
| **Total** | **18** | 4 sessions | **57** | **270** | 4 primitives, 1 migration, ~35 combined-batch-close observations |

**All 18 tools verified at DEFECT-PATCHED-VERIFIED.**

## 5. Campaign-wide MEMORY rules reinforcement

MEMORY rules verified or reinforced across the campaign:

| MEMORY rule | Verification passes | Comment |
|---|---|---|
| `feedback_llm_autofills_boolean_params_with_false` | **3** (Batch C tool 3 F-RL-5, Batch C tool 4 F-OH-4, Batch C tool 5 F-RB-6) | Semantic extended to int-autofill class in `td_limit_envelope.compute_limit` |
| `feedback_openai_client_factory` | **3** (Batch C tool 3 F-RL-5, Batch C tool 5 F-RB-3/F-RB-6, Batch D tool 3 F-WC-3) | Factory + `_FORBIDDEN_KWARGS` invariant intact |
| `feedback_pa_worker_function_calling_env` | **1** (Batch D tool 1 F-WF-6) | 3-test source-level guard added |
| `feedback_deliverable_tool_use_append_for_large_payloads` | 2 (Batch A tool 1 F-D-9, Batch C tool 2 F-PS-6) | S1177 F1 skip-handler invariant + retry_hint envelope pinned |
| `feedback_local_celery_stall_playbook` | **2** (Batch D tool 2 F-CW-4, Batch D tool 3 Redis DB topology) | Substrate + diagnostic sequence pinned |
| `feedback_procfile_makefile_queue_parity` | reinforced across Batch B tool 3, Batch C tool 5, Batch D tool 1 | Procfile PA_USE_FUNCTION_CALLING declaration + Makefile parity intact |
| `feedback_triage_decision_card_pattern` | reinforced Batch C tool 4 | `applied_filters` echo now consistent across 3 list handlers |
| `feedback_anthropic_client_factory` | 2 (Batch C tool 5 F-RB-6, Batch D tool 3 F-WC-3) | Factory + `get_anthropic_client` export stable |

## 6. Repository state at S2732 close

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `8906904a` (post PR #3019 + #3020) |
| Batch D close PR | #3019 merged as `47b40d5b` |
| Docs cascade PR | #3020 merged as `8906904a` |
| Playbook body commit_sha | `b372edfe127f1af59c4322871092aa7151669463` (unchanged from S2727) |
| Git tag | `playbook-v0.1.0` (unchanged) |
| Pending migrations | 0 (0379 was Batch C tool 2's; no Batch D migrations) |
| PA worker | Post-S2728-restart with Batch A patches active. **NEEDS RESTART** to load Batches B + C + D patches when Rigby cross-check begins. |
| Docs cascade state | 3,037/3,037 Documents embedded; INDEX.md regenerated (3,037 docs); `_provenance.json` fresh (HIGH=1595 / MEDIUM=392 / LOW=5 / UNKNOWN=495) |

## 7. Constitutional state (unchanged from S2727)

**Engineering Playbook v0.1.0: RATIFIED.** No amendments in S2728 / S2729 / S2730 / S2731 / S2732. CD-47 RESOLVED; CD-48 + CD-49 targeted for v0.1.1 PATCH.

## 8. Combined batch-close observation list (cross-campaign)

~35 cross-tool consistency observations logged across Batches A + B + C + D for a future combined-doc-pass sweep:

**From Batch A + B (from S2729 handoff):** schema-`required` violated by handler defaults, error envelope `ok: false` consistency, multi-alias parameter extraction undocumented, undocumented action aliases, index/corpus freshness signal missing, test-file mock refresh for `test_rag_integration_search_embeddings.py`, D17-D21 invariant test extension to 8-way.

**From Batch C (from S2731 handoff):**
- F-CI-11 — workspace-blind enrichment (PARKED-CONSTITUTIONAL).
- F-PS-4 — other `td_handlers_core` content silent-truncation surfaces (~5 sites).
- F-RL-3 — apply envelope to 2-3 additional Rigby-callable handlers.
- F-RL-4 — ~25 remaining un-enveloped silent-cap sites.
- F-OH-5 — implicit `is_active=True` filter sweep (~15 sites).
- F-RB-2 — S1077 hardcoded `content_tool`/`work_tool` auto-retry generalization.

**From Batch D (this batch):**
- F-CW-5 companion — worker_recycled `CeleryTaskEvent` marker (extending F-CW-2 into the audit substrate).
- 43 `django.core.cache` users not individually audited — KEY_PREFIX='udb' tenant isolation closes the immediate coherence risk.

## 9. Recommended first task next session

Chris-choice among five options:

1. **Combined batch-close doc pass** — sweep the ~35 cross-tool consistency observations logged across A + B + C + D into a single cleanup PR. High leverage for uniformity.
2. **PA worker restart + Rigby cross-check of Batches B + C + D patches** — ~57 defects patched but not yet loaded into the running worker. Rigby dispatches would still hit Batch A code.
3. **Playbook v0.1.1 PATCH** — CD-48 + CD-49 codification (from S2727 handoff §5). Constitutional work; independent of the campaign.
4. **Post-campaign retrospective** — write a `SESSION_2733_CAMPAIGN_RETROSPECTIVE.md` capturing what worked / what to codify into the Playbook v0.1.1 methodology chapters / what patterns to reuse.
5. **Something else** — the campaign is closed; the queue is open.

Session-open protocol:
1. `context-kit orient` (mandatory).
2. Read this handoff in full.
3. Confirm PA worker state — `ps aux | grep hostname=pa` — restart if any cross-check dispatch is planned.
4. If Chris chooses (1) or (4): read the batch-close observation lists in the 18 validation reports OR the 4 batch-close handoffs (S2728, S2729, S2731, S2732).

## 10. Current Rigby SIGN pin state

**Active pin at S2732 close:** `pa-44a6eb70d8814e34` (T4 Group 1700 Observability paused-research pin; preserved through the entire campaign for cross-check dispatches).

**Fresh-session decision:** on next session open, decide based on task:
- **Combined batch-close doc pass / retrospective** — no new pin needed; paused-research pin remains usable.
- **Rigby cross-check** — no new pin; but requires PA worker restart to load Batches B + C + D code.
- **Anything else** — mint a new pin per playbook §16 fresh-thread discipline.

**Default PA wrapper (`tools/pa_local.sh`) currently points at:** `pa-44a6eb70d8814e34` (unchanged from S2727 close).

**PA worker restart REQUIRED before Rigby-side Batches B + C + D verification:** current worker (PID 12820 from S2728 restart) has Batch A patches loaded but NOT Batches B, C, or D. Run `make celery-stop && make celery` — or, using the F-CW-1 helper shipped in this batch, `make celery-recycle`.

## 11. Session close summary

- **Merged PRs:** [#3019](https://github.com/clwest/donkey-betz-platform/pull/3019) (Batch D — 3 tools, 11 defects, 45 tests, 3 observability additions, 2 bounded LRU refactors, 1 mgmt target), [#3020](https://github.com/clwest/donkey-betz-platform/pull/3020) (docs cascade).
- **Engineering campaign:** Batch D closed; **CAMPAIGN COMPLETE** (4 of 4 batches, 18 of 18 tools).
- **Docs cascade:** 3,037/3,037 Documents embedded; Rigby's RAG surface current at HEAD.
- **Cross-tool regression:** 293/293 substantive tests pass across all 18 validation-2728 files + adjacent legacy tests.
- **Total campaign delivery:** 57 defects patched, 270 regression tests added, 4 shared primitives extracted, 1 migration, ~35 observations deferred for combined-doc-pass sweep.
- **Constitutional debt state:** unchanged from S2727 (CD-47 RESOLVED; CD-48/CD-49 v0.1.1 PATCH targets).
- **Handoff + anchor updates:** this file + `00-START-NEXT-SESSION.md`.
- **PA worker restart** deferred to next session (Batches B + C + D patches loaded from repo but not yet in the running worker).
