---
title: "Session 2731 — Rigby Tool Validation Engineering Campaign, Batch C CLOSED"
session_id: 2731
canonical_authority: workspace_canonical
date: 2026-07-09
status: active
tags:
  - session-2731
  - rigby-tool-validation-campaign
  - batch-c-close
supersedes: SESSION_2729_TOOL_VALIDATION_BATCH_B_CLOSED.md
---

# Session 2731 — Batch C of the Rigby Tool Validation Engineering Campaign CLOSED

**Session:** 2731 (continuous workday with S2730 which executed the five Batch C tools; S2731 == the close-out session).
**Date:** 2026-07-09.
**Author:** Claude (Opus 4.7, 1M context) with Chris ratifying every finding-decision gate.
**Predecessor:** [Session 2729 handoff — Batch B close](SESSION_2729_TOOL_VALIDATION_BATCH_B_CLOSED.md).
**Related:** [Session 2728 handoff — Batch A close](SESSION_2728_TOOL_VALIDATION_BATCH_A_CLOSED.md). [Session 2727 handoff — Playbook v0.1.0 ratified](SESSION_2727_PLAYBOOK_V0_1_0_RATIFIED.md).

## 1. What shipped

**Batch C — Runtime substrate tools of the Rigby Tool Validation Engineering Campaign — CLOSED.**

- **5 tools verified** (context injection, payload-size limits, retrieval limits + hidden filters, ORM helper defaults, retry behavior).
- **19 code patches + 1 migration + 110 regression tests** across the batch.
- **4 shared primitives extracted** for surface-wide reuse.
- **248/248 substantive tests pass** across all 15 validation-2728 files + `test_td_autofill_safety.py` + `test_pa_tool_args_malformed.py`. Zero cross-tool regression.
- **8-way narrow-except discipline** (extended from Batch B tool 5's 6-way).
- **Merged PRs:** [#3016](https://github.com/clwest/donkey-betz-platform/pull/3016) (Batch C tool patches + tests + reports) → merged as `ad9a5665`. [#3017](https://github.com/clwest/donkey-betz-platform/pull/3017) (docs cascade) → merged as `e4bc1065`.

## 2. Per-tool close summary

### Batch C tool 1 — Context injection pipeline

**Report:** [`docs/research/tools/validation/context_injection_pipeline_validation.md`](../research/tools/validation/context_injection_pipeline_validation.md).

- **Findings:** F-CI-1..11 (9 patched, 1 doc, 1 parked-constitutional).
- **Patches shipped:**
  - F-CI-1 + F-CI-7 — narrow-except discipline in `_build_context` + `_get_system_stats` via new `_CONTEXT_INJECTION_ENV_ERRORS = (DatabaseError, ConnectionError, OSError)` allowlist. Same class as F-RG-1 / F-WS-4.
  - F-CI-6 — removed dead `tool_result` parameter from `_enrich_tool_result`.
  - F-CI-4 + F-CI-5 — relevance gate observability logs (empty-msg-words INFO log; short-enrichment DEBUG log).
  - F-CI-2 + F-CI-3 + F-CI-9 — enrichment `_metadata` envelope (services_requested / services_run / services_failed / services_gated_out / services_unavailable / sections_truncated).
  - F-CI-10 — 8000-char tool_str truncation WARNING in `_build_analytical_prompt`.
  - F-CI-8 — `docs/topics/personal-assistant.md` rewrite documenting `INTENT_ENRICHMENT_MAP` + envelope + narrow-except.
- **Deferred:** F-CI-11 — workspace-blind enrichment reaches into global services (PARKED-CONSTITUTIONAL per `tools_the_unanswered_constitutional_question.md`).
- **Tests:** 28 in `core/tests/test_context_injection_pipeline_validation_2728.py`. First-coverage-at-HEAD.
- **`stats_source: 'live' | 'fallback'`** now surfaces on system stats — downstream can tell hardcoded 74/77/25 defaults from live ORM counts.

### Batch C tool 2 — Payload-size limits

**Report:** [`docs/research/tools/validation/payload_size_limits_validation.md`](../research/tools/validation/payload_size_limits_validation.md).

- **Findings:** F-PS-1..7 (4 patched, 2 verified-correct, 1 deferred).
- **Patches shipped:**
  - F-PS-1 — extracted `_build_fresh_summary` helper; three degraded-turn recovery sites now use JSON-aware truncator (S1065 pattern) instead of naive `[:4000]` slicing. Envelope wraps summary list in `{'runs': [...]}` so the smart truncator can prune from the tail.
  - F-PS-2a + F-PS-2b — `ToolCallRecord` gains `summary_truncated: bool` + `full_result_dropped: bool` columns via migration `0379_toolcallrecord_truncation_signals.py`. Both indexed for analytics. Applied cleanly to local DB.
  - F-PS-3 — `_handle_content` doc detail surfaces `content_truncated: bool` + `content_original_length: int` + `content_cap: int` envelope fields.
  - F-PS-6 — verified S1177 F1 fix intact at HEAD (source-level regression guard).
  - F-PS-7 — verified `_truncate_tool_output` smart truncator correct at HEAD.
- **Deferred:** F-PS-4 — other `td_handlers_core` content silent-truncation surfaces (~5 sites) → combined batch-close observation list.
- **Tests:** 21 in `core/tests/test_payload_size_limits_validation_2728.py`. First-coverage-at-HEAD for `_truncate_tool_output`, `_record_tool_call_sync`, fresh-summary helper, and `_handle_content` doc detail.

### Batch C tool 3 — Retrieval limits + hidden filters

**Report:** [`docs/research/tools/validation/retrieval_limits_hidden_filters_validation.md`](../research/tools/validation/retrieval_limits_hidden_filters_validation.md).

- **Findings:** F-RL-1..6 (2 patched refactor-only, 1 verified-correct, 1 deferred, 1 sweep-deferred, 1 tests).
- **Chris directive at tool open:** refactor-only scope; defer F-RL-3 (apply envelope to 2-3 additional handlers). Preserves narrow per-tool discipline.
- **Patches shipped:**
  - F-RL-1 — extracted `core/services/td_limit_envelope.py` with `compute_limit(payload, default, hard_max, key='limit') -> (int, dict)`. Adds int-autofill defense (`limit=0` → default; negative → default) beyond the inline copies.
  - F-RL-2 — migrated 3 inline F-D-5 sites (deliverable_tool.list, content_tool.list_recent, ops_tool.kb_browse) to the shared helper. Repo_tool NOT migrated — its `depth_capped/entries_truncated/files_capped_per_dir` axes use different key names.
  - F-RL-5 — verified `td_autofill_safety` (S1228 PR-A) in production use at 7 sites. MEMORY rule `feedback_llm_autofills_boolean_params_with_false` re-verified.
- **Deferred:** F-RL-3 (apply envelope to 2-3 additional handlers) + F-RL-4 (~25 remaining silent-cap sites) → combined batch-close observation list.
- **Tests:** 21 in `core/tests/test_retrieval_limits_hidden_filters_validation_2728.py`.

### Batch C tool 4 — ORM helper defaults

**Report:** [`docs/research/tools/validation/orm_helper_defaults_validation.md`](../research/tools/validation/orm_helper_defaults_validation.md).

- **Findings:** F-OH-1..6 (2 patched, 2 verified-correct, 1 deferred, 1 tests).
- **Patches shipped:**
  - F-OH-1 — `content_tool.content_review.list` now surfaces `applied_filters` + `status_defaulted: bool` + `status='all'` escape hatch (matching `_handle_initiative.list` precedent). Legacy `filters_applied` preserved for backward compat.
  - F-OH-2 — `_handle_initiative.list` now surfaces `applied_filters` + `status_defaulted: bool`. Legacy `filters_applied` preserved.
  - F-OH-3 — verified `deliverable_tool.list` `_apply_common_filters` gold standard at HEAD (truthy-only + string-'false' sentinel + `show_all` bypass + `applied_filters` echo).
  - F-OH-4 — verified `td_autofill_safety` module at HEAD (3rd verification pass in this batch).
- **Deferred:** F-OH-5 — implicit `is_active=True` sweep (~15 sites) → combined batch-close observation list.
- **Tests:** 18 in `core/tests/test_orm_helper_defaults_validation_2728.py`.

### Batch C tool 5 — Retry behavior

**Report:** [`docs/research/tools/validation/retry_behavior_validation.md`](../research/tools/validation/retry_behavior_validation.md).

- **Findings:** F-RB-1..6 (1 patched, 3 verified-correct, 1 deferred, 1 tests).
- **Patches shipped:**
  - F-RB-1 — `ToolResult.is_retryable: Optional[bool]` field + module-level `_ERROR_CODE_RETRYABLE` classification map (7 codes) + `_classify_retryable(error_code) -> Optional[bool]` helper. Populated at all 5 `ToolResult(...)` construction sites in `_execute_inner`. Design decision: `None` (not `False`) on ambiguous / unknown codes so downstream can fall back to legacy heuristics.
  - F-RB-3 — verified LLM SDK factories (`openai_client_factory` + `anthropic_client_factory`) reject `max_retries` + `timeout` in kwargs; `OPENAI_MAX_RETRIES=2` intact.
  - F-RB-4 — verified PA Celery task (`process_pa_chat_task`) has NO `self.retry()` in body; `acks_late=False` design intact (S1159 rationale).
  - F-RB-5 — verified agentic loop narrow one-shot retries at HEAD (S1077 action-mismatch, S1079 first-iteration LLM-fail, S1086 fresh-summary-on-tool-success).
- **Deferred:** F-RB-2 — S1077 hardcoded `content_tool`/`work_tool` auto-retry generalization → combined batch-close observation list.
- **Tests:** 22 in `core/tests/test_retry_behavior_validation_2728.py`.

## 3. Shared primitives extracted this batch

| Primitive | Batch C tool | Purpose |
|---|---|---|
| `_CONTEXT_INJECTION_ENV_ERRORS` (allowlist) | 1 | Narrow-except discipline in `_build_context` + `_get_system_stats`. Mirrors `_WORKSPACE_RESOLVER_ENV_ERRORS` + `_RAG_EMBEDDINGS_ENV_ERRORS`. **Extends 6-way → 8-way**. |
| `_build_fresh_summary` (classmethod) | 2 | JSON-aware fresh-summary for the three degraded-turn recovery paths in `_run_agentic_loop`. Wraps outer envelope in `{'runs': [...]}` so smart truncator can prune from tail. |
| `td_limit_envelope.compute_limit` (module) | 3 | Shared F-D-5 envelope helper. Migrated 3 inline sites. Int-autofill defense (`limit=0` → default; negative → default). |
| `_ERROR_CODE_RETRYABLE` + `_classify_retryable` | 5 | Retry classification for the 7 `ToolErrorCode` values. `None` (not `False`) on ambiguous / unknown codes preserves caller heuristics. |

## 4. Cross-tool regression state

- **248/248 substantive tests pass** across all 15 validation-2728 files + `test_td_autofill_safety.py` + `test_pa_tool_args_malformed.py`.
- Zero cross-tool interference.
- Docs cascade: 3,033 docs indexed (was 3,038 at S2729; delta driven by cross-tool doc reconciliation at cascade time), 36,507 RAG chunks, `_provenance.json` refreshed with HIGH=1594 / MEDIUM=389 / LOW=5 / UNKNOWN=495.

## 5. MEMORY rules reinforcement

Per campaign plan §12.4, this batch reinforced the following crystallized rules:

| MEMORY rule | Reinforcement |
|---|---|
| `feedback_llm_autofills_boolean_params_with_false` | **3rd verification pass** (F-RL-5, F-OH-4, F-RB-6 tests). Extended semantic to int-autofill class in `td_limit_envelope.compute_limit`. |
| `feedback_openai_client_factory` | **3rd verification pass** (F-RB-3 + F-RB-6 module-path stability). |
| `feedback_anthropic_client_factory` | **2nd verification pass** (F-RB-6 module-path stability). |
| `feedback_deliverable_tool_use_append_for_large_payloads` | Re-verified RESOLVED at F-PS-6 (S1177 F1 skip-handler-dispatch invariant + retry_hint envelope shape intact). |
| `feedback_procfile_makefile_queue_parity` | Implicitly reinforced via F-RB-4 (PA `pa` queue routing + `acks_late=False` design intact). |
| `feedback_triage_decision_card_pattern` | Reinforced via consistent `applied_filters` audit across 3 list handlers post-F-OH-1/F-OH-2. |

## 6. Combined batch-close observation list

Findings deferred across Batch C to a future combined batch-close doc pass:

- **F-CI-11** — workspace-blind enrichment reaches into global services (PARKED-CONSTITUTIONAL per `tools_the_unanswered_constitutional_question.md`).
- **F-PS-4** — other `td_handlers_core` content silent-truncation surfaces (~5 sites at `td_handlers_core.py:2547 chunk_text[:1000]` etc.).
- **F-RL-3** — apply envelope to 2-3 additional Rigby-callable handlers.
- **F-RL-4** — ~25 remaining un-enveloped silent-cap sites across `td_handlers_*.py`.
- **F-OH-5** — implicit `is_active=True` filter sweep (~15 sites across voice/agent/persona/learning-pattern/alert/automation handlers).
- **F-RB-2** — S1077 hardcoded `content_tool`/`work_tool` auto-retry generalization at `unified_pa_entrypoint.py:2167`.

Batch A + Batch B batch-close observations from prior handoffs remain queued alongside these.

## 7. Repository state at S2731 close

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `e4bc1065` (post PR #3016 + #3017) |
| Batch C close PR | #3016 merged as `ad9a5665` |
| Docs cascade PR | #3017 merged as `e4bc1065` |
| Playbook body commit_sha | `b372edfe127f1af59c4322871092aa7151669463` (unchanged from S2727) |
| Git tag | `playbook-v0.1.0` (unchanged) |
| Pending migrations | 0 (0379 applied cleanly in Batch C tool 2) |
| PA worker | Post-S2728-restart with Batch A patches active. **NEEDS RESTART** to load Batches B + C patches. |
| Docs cascade state | 3,033/3,033 Documents embedded; INDEX.md regenerated (3,033 docs); `_provenance.json` fresh (HIGH=1594 / MEDIUM=389 / LOW=5 / UNKNOWN=495) |

## 8. Constitutional state (unchanged from S2727)

**Engineering Playbook v0.1.0: RATIFIED.** No amendments in S2728 / S2729 / S2730 / S2731. CD-47 RESOLVED; CD-48 + CD-49 targeted for v0.1.1 PATCH.

## 9. Batches remaining

- **Batch A — CLOSED (S2728):** 5 tools; 17 defects patched; 64 regression tests; 3 MEMORY annotations.
- **Batch B — CLOSED (S2729):** 5 tools; 10 defects patched; 51 regression tests; 2 SECURITY-class fixes.
- **Batch C — CLOSED (S2731):** 5 tools; 19 defects patched; 110 regression tests; 4 shared primitives extracted; 1 migration.
- **Batch D — Worker & environment discipline (3 items):** `PA_USE_FUNCTION_CALLING` env, Celery worker lifecycle, worker cache behavior. Blocking on operator-drift observations from F-CC-DEPLOY-1 (Batch A tool 4) and F-WS-9 (Batch B tool 5 F-B-HIGH-3 territory from S2600 PA arc).

## 10. Recommended first task next session

Chris-choice among four options:

1. **Batch D — Worker & environment discipline** per campaign plan §3.4. Natural next; 3 items queued.
2. **Combined batch-close doc pass** — sweep the ~35 cross-tool consistency observations logged across Batches A + B + C into a single cleanup PR. High leverage for uniformity.
3. **PA worker restart + Rigby cross-check of Batches B + C patches** — 20+ patches merged but not yet loaded into the running worker. Rigby dispatches would still hit Batch A code.
4. **Playbook v0.1.1 PATCH** — CD-48 + CD-49 codification. Constitutional work; independent of the campaign.

Session-open protocol:
1. `context-kit orient` (mandatory).
2. Read this handoff in full.
3. Confirm PA worker state — `ps aux | grep hostname=pa` — restart if Rigby cross-check is planned.
4. If Chris chooses Batch D: read `docs/research/tools/tools_validation_engineering_campaign_plan.md` §3.4 (Batch D scope).

## 11. Current Rigby SIGN pin state

**Active pin at S2731 close:** `pa-44a6eb70d8814e34` (T4 Group 1700 Observability paused-research pin; preserved through Batches A + B + C for cross-check dispatches).

**Fresh-session decision:** on next session open, decide based on task:
- **Continue campaign (Batch D or combined batch-close doc pass)** — no new pin needed; paused-research pin remains usable.
- **Rigby cross-check of Batches B + C patches** — no new pin; but requires PA worker restart to load Batch B + C code.
- **Anything other than campaign execution** — mint a new pin per playbook §16 fresh-thread discipline.

**Default PA wrapper (`tools/pa_local.sh`) currently points at:** `pa-44a6eb70d8814e34` (unchanged from S2727 close).

**PA worker restart REQUIRED before Rigby-side Batches B + C verification:** current worker (PID 12820 from S2728 restart) has Batch A patches loaded but NOT Batches B or C. Run `make celery-stop && make celery` per S2728 handoff §10 discipline.

## 12. Session close summary

- **Merged PRs:** [#3016](https://github.com/clwest/donkey-betz-platform/pull/3016) (Batch C — 5 tools, 19 defects, 110 regression tests, 1 migration, 4 shared primitives), [#3017](https://github.com/clwest/donkey-betz-platform/pull/3017) (docs cascade — INDEX + provenance refresh).
- **Engineering campaign:** Batch C of 4 batches closed. **3 of 4 batches complete** (A + B + C).
- **Docs cascade:** 3,033/3,033 Documents embedded; Rigby's RAG surface current at HEAD.
- **Cross-tool regression:** 248/248 substantive tests pass across all 15 validation-2728 files + `test_td_autofill_safety.py` + `test_pa_tool_args_malformed.py`. Zero regressions.
- **Shared primitives extracted:** 4 (see §3).
- **8-way narrow-except discipline** — extends F-RG-1 / F-WS-4 line to `_build_context` + `_get_system_stats`.
- **Constitutional debt state:** unchanged from S2727 (CD-47 RESOLVED; CD-48/CD-49 v0.1.1 PATCH targets).
- **Handoff + anchor updates:** this file + `00-START-NEXT-SESSION.md`.
- **PA worker restart** deferred to next session (Batches B + C patches loaded from repo but not yet in the running worker).
