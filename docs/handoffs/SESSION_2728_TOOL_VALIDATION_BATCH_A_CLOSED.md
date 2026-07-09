# SESSION_2728 — Rigby Tool Validation Engineering Campaign, Batch A Closed

**Date:** 2026-07-08
**Session type:** Engineering QA — pivoted from constitutional-research abstraction detour
**Predecessor handoff:** [`SESSION_2727_PLAYBOOK_V0_1_0_RATIFIED.md`](SESSION_2727_PLAYBOOK_V0_1_0_RATIFIED.md)
**Ratified merges:** PR #3010 (Batch A patches + tests + docs) → merge `9f1f1e34`; PR #3011 (docs cascade) → merge `30e7501e`.

---

## 1. Executive Summary

**Batch A of the Rigby Tool Validation Engineering Campaign is closed as of 2026-07-08.** Five high-priority Rigby tools verified against Chris-approved patch shapes. 17 defects patched. 64 new regression tests + 3 MEMORY rule annotations. 211/211 tests pass across all 5 tools + adjacent suites. Zero cross-tool interference.

**The session began as constitutional research** ("What operational contracts actually exist between Rigby and every platform capability?") but self-disproved that framing after Chris's pressure-test discipline surfaced 65% terminology drift and revealed the domain either (a) has no independent constitutional character (reduces to existing chapters) or (b) has independent character but no vocabulary yet exists to describe it. That single unanswered constitutional question is parked at `docs/research/tools/tools_the_unanswered_constitutional_question.md` for future consideration. Chris then pivoted the session from theory to **engineering QA — actually validate the tools Rigby depends on.**

**Batch A totals at close:**
- **5 tools verified:** `deliverable_tool`, `session_tool`, `search_docs` + `kb_tool`, `claude_code_tool`, `agent_introspection_tool` + `run_agent`.
- **17 defects patched.** Every patch Chris-ratified before authoring.
- **64 new regression tests** across 5 test files.
- **3 MEMORY rules annotated at HEAD:** 2 RESOLVED (`feedback_deliverable_tool_use_append_for_large_payloads`, `feedback_ratification_workflow_gotchas` gotcha #3), 1 VERIFIED-VALID (`feedback_procfile_makefile_queue_parity`). Rule bodies retained per campaign plan §12.4.
- **Docs cascade complete:** 3,032/3,032 Documents embedded post-merge; Rigby's RAG surface current at HEAD.
- **Rigby cross-check VERIFIED live:** her mental model correctly cites every patched pattern; runtime behavior at HEAD confirmed via both live Rigby dispatch (F-D-5 limit cap, F-D-20 updated_at) and direct Django-shell dispatch (F-D-6/F-D-7/F-SD-1/F-CC-3).

## 2. Timeline of the session

| UTC | Event |
|---|---|
| Session open | `context-kit orient` executed; source-of-truth chain absorbed. Chris opened with constitutional research directive |
| Phase 0 domain-definition draft | `docs/research/tools/tools_operational_contract_domain_definition.md` (588 lines). Proposed 5-child research arc (P1 AUTHORITY-CARRIAGE / P2 CAPABILITY-CONTRACT / P3 KNOWLEDGE-SUBSTRATE / P4 FAILURE-AND-RECOVERY / P5 VERIFIER-LOOP) under new `docs/research/tools/` directory parallel to `docs/research/platform/` |
| Chris directive: pressure-test | "Attempt to falsify. Do not defend. Determine whether terminology shifts are architectural discovery or conceptual drift." |
| Architecture pressure test | `docs/research/tools/tools_operational_contract_architecture_pressure_test.md` (495 lines). Verdict: **DECOMPOSITION DISPROVED.** Terminology shift audit 35% discovery / 65% drift. Only 1 of 5 proposed children survived (P2 narrowed to tool-call discipline). 3 reframes surfaced (narrow to tool surface / audit-only / different arc at platform/) |
| Chris directive: reduce to one question | "What single constitutional question remains that if answered would eliminate the uncertainty?" |
| Unanswered constitutional question distillation | `docs/research/tools/tools_the_unanswered_constitutional_question.md` (94 lines). Reduced to: *"Do platform-internal runtime reaches constitute a scope of constitutional authority independent of the scopes that already exist, or does every rule about such a reach reduce without residue to a rule already owned by an existing Playbook chapter?"* Parked pending Chris ratification |
| Chris directive: pivot to engineering QA | "Open a Rigby Tool Validation Engineering Campaign. Do NOT continue the constitutional runtime-reach research right now. Do NOT open a broad Tool Constitution arc." |
| Campaign plan authored | `docs/research/tools/tools_validation_engineering_campaign_plan.md` (406 lines). 4 batches / 18 tools total; per-tool 20-question checklist; evidence logging format; defect / verified / Rigby-safe definitions; Chris-gate discipline. Chris approved before execution |
| Batch A tool 1: `deliverable_tool` | Full code trace + 22 candidate findings + Chris ratified 9 patches → shipped in commit `4b83a34f`. 17 regression tests / 67 adjacent tests pass. MEMORY rule `feedback_deliverable_tool_use_append_for_large_payloads` annotated RESOLVED at S1177 |
| Batch A tool 2: `session_tool` | Full code trace + 8 findings + Chris ratified 2 patches (F-S-3 list cap; F-S-6 retire not_found vs already_retired) → shipped in commit `adcab784`. 7 new + 33 existing tests pass |
| Batch A tool 3: `search_docs` + `kb_tool` | Full code trace + 5 findings + Chris ratified 2 patches (F-SD-1 originating_session=0 autofill guard; F-KB-1 kb_tool cap envelope) + 1 opportunistic stale-test cleanup → shipped in commit `bb232e9b`. 21 new + 40 existing tests pass. MEMORY `feedback_ratification_workflow_gotchas` gotcha #3 annotated RESOLVED |
| Batch A tool 4: `claude_code_tool` | Full code trace + 6 findings + Chris ratified F-CC-3 patch (conversation_id echo + follow_up_will_fire) → shipped in commit `4165856b`. 6 new + 69 existing tests pass. MEMORY `feedback_procfile_makefile_queue_parity` annotated VERIFIED-VALID |
| Batch A tool 5: `agent_introspection_tool` + `run_agent` | Full code trace + 6 findings + Chris ratified 3 patches (F-RA-1 auto_followup echo on both dispatch paths; F-RA-2/F-RA-3 agent substitution envelope; F-AI-2 introspection list cap) → shipped in commit `39797aba`. 13 new + 23 existing tests pass |
| Chris directive: commit + open Batch A close PR + merge --admin + cascade docs | Single PR bundling all 5 tools per Chris scope-override (campaign §12.2 default is per-tool) |
| PR #3010 opened | Title: "tools(validation): Batch A — 5 tools, 17 defects patched, 64 regression tests" |
| PR #3010 merged | `gh pr merge 3010 --admin --merge` → merge commit `9f1f1e34` |
| Docs cascade executed | build_docs_index (3021 docs) → build_rag_corpus (36,283 chunks) → sync_docs_index_to_documents (10 created + 3 updated) → KFI-2 `run_backfill(Document)` (10 docs `derived → repo_canonical`) → embed_documents --all-unembedded (all 3,032 embedded) → build_docs_provenance (2,471 docs indexed) → verify_doc_claims (1 pre-existing unrelated drift on BACKEND_INVENTORY.md) |
| PR #3011 opened + merged | Docs cascade artifacts (INDEX + `_provenance.json` refresh). Merge commit `30e7501e` |
| Rigby cross-check phase | Verified identity via `session_tool.whoami` (`chris`, staff+superuser, pin `pa-44a6eb70d8814e34`). Requested Rigby demonstrate model of all 5 tools (when-to-use + safe-value patterns). She correctly cited every patched pattern; 1 minor imprecision on claude_code_tool default (immediately corrected) |
| PA worker restart | Old workers stopped; `make celery` restarted with `PA_USE_FUNCTION_CALLING=true` env preserved. New PA worker PID 12820 loaded post-merge code |
| Live verification (Rigby dispatch) | F-D-5 limit-cap fields absent because Rigby was passing `limit ≤ 50`; F-D-20 `updated_at` present in all list items. Direct Django-shell dispatch with explicit `limit=200` confirmed F-D-5 fires: `limit_capped=True, requested_limit=200, effective_limit=50, hard_max=50` |
| Direct dispatch verification | F-D-6 (create → status='ready'), F-D-7 (update status='completed' → typed error naming completion path), F-SD-1 (originating_session=0 → no filter block), F-CC-3 (with/without conversation_id → follow_up_will_fire True/False). All 4 patches verified live |
| Session close | S2728 handoff (this doc) + 00-START-NEXT-SESSION.md overwrite |

## 3. Constitutional-research detour: parked but honest

The session opened with a constitutional-research directive that self-disproved after two pressure-test rounds. The research artifacts remain in the repository at `docs/research/tools/` as **honest record of the abstraction detour**, not as active mission:

- `tools_operational_contract_domain_definition.md` — Phase 0 domain definition (climbed into constitutional abstraction).
- `tools_operational_contract_architecture_pressure_test.md` — Chris-directed falsification pass; disproved the Phase 0 architecture (65% drift / 35% discovery on terminology).
- `tools_the_unanswered_constitutional_question.md` — reduced to a single unanswered question, parked for future consideration.

The parked question is preserved verbatim below in case a future arc surfaces the evidence to answer it:

> *"Do platform-internal runtime reaches — the moments where one part of the platform reaches for another part of the platform — constitute a scope of constitutional authority independent of the scopes that already exist, or does every rule about such a reach reduce without residue to a rule already owned by an existing Playbook chapter?"*

## 4. Batch A defect resolution matrix

Every patch matches a Chris-approved shape ratified in-session before authoring.

| Tool | Defects patched | Chris-approved shape | Commit |
|---|---|---|---|
| `deliverable_tool` | F-D-2/3/4/5/6/7/8/20/21 (9) | typed errors on `status='completed'` for both create + update; whitelist default `'ready'`; inference envelope at layer 1; unknown-action typed error; limit-cap envelope; `updated_at` in list; `status` in update response; `source` in provenance block | `4b83a34f` |
| `session_tool` | F-S-3, F-S-6 (2) | `list_recent` cap envelope + unbounded `total` when > 25; `retire` distinguishes `not_found` vs `already_retired` via existence-query + typed `reason` | `adcab784` |
| `search_docs` + `kb_tool` | F-SD-1, F-KB-1 (2) | new `_resolve_originating_session` positive-only guard (mirrors `_d14_resolve_min_session`); kb_tool cap envelope on 4 list-shaped actions | `bb232e9b` |
| `claude_code_tool` | F-CC-3 (1) | `conversation_id` echo (value or `null`) + `follow_up_will_fire: bool` in dispatch response; message-string hint when no banner will fire | `4165856b` |
| `agent_introspection_tool` + `run_agent` | F-RA-1 (both paths), F-RA-2/F-RA-3, F-AI-2 (3) | `auto_followup` + `follow_up_will_fire` echo on both `_handle_agent_tool` + `_handle_universal_agent`; `agent_name_requested/effective/substituted/reason` envelope; introspection list cap envelope | `39797aba` |

## 5. MEMORY rule status at HEAD

Three MEMORY rules annotated during Batch A. Rule bodies retained per campaign plan §12.4 (do not delete; annotate).

- **`feedback_deliverable_tool_use_append_for_large_payloads`** — annotated **RESOLVED at S1177**. Verified stale at HEAD: `unified_pa_entrypoint.py:2020-2063` typed `TOOL_ARGS_JSON_MALFORMED` envelope replaces the silent action=list fallback. The workaround "use append for content > 6 kB" remains hint-worthy but the surface is now loud, not silent.
- **`feedback_ratification_workflow_gotchas`** gotcha #3 — annotated **RESOLVED at S2728**. `search_docs originating_session=0` LLM autofill is now guarded via `_resolve_originating_session` (positive-only). Workaround "use kb_tool instead" is obsolete; both surfaces are safe.
- **`feedback_procfile_makefile_queue_parity`** — annotated **VERIFIED-VALID at S2728**. Preventative PR-review discipline; historical `claude_code_tool` silent-queue-forever defect from S1226 remains RESOLVED at HEAD (Procfile:32 + Makefile:322 both consume `code_jobs`).

## 6. Runtime verification at HEAD

Post-merge + PA-worker-restart verification confirms all 17 patches active:

- **F-D-5** `limit_capped=True, requested_limit=200, effective_limit=50, hard_max=50` on `deliverable_tool.list limit=200` (direct dispatch).
- **F-D-6** `create` returns `status='ready'` by default (direct dispatch).
- **F-D-7** `update status='completed'` returns `ok=False, error_code='status_completed_not_allowed_on_update'` with message naming `content_tool.content_complete` (direct dispatch).
- **F-D-20** `updated_at` in every `list` item (live Rigby dispatch).
- **F-SD-1** `search_docs originating_session=0` returns no `filter` block (autofill guard fired; direct dispatch).
- **F-CC-3** `claude_code_tool` dispatch with `conversation_id='pa-test'` → `follow_up_will_fire=True`; without → `False` with `conversation_id=None` (direct dispatch).

Rigby cross-check: her mental model correctly cites every patched pattern (deliverable_tool default status='ready' + `has_initiative='false'` string sentinel + `dry_run + confirm` two-factor gate; session_tool `retire` reason field; search_docs positive-only originating_session; claude_code_tool `follow_up_will_fire`; run_agent auto_followup echo; universal_agent substitution envelope; introspection list cap). One minor imprecision on `claude_code_tool` default behavior when `conversation_id` is omitted — she corrected on my prompt.

## 7. Batch A close artifacts (for future navigation)

Research + validation record at `docs/research/tools/`:

1. `tools_operational_contract_domain_definition.md` — Phase 0 detour (record of what was tried).
2. `tools_operational_contract_architecture_pressure_test.md` — pressure test that disproved Phase 0.
3. `tools_the_unanswered_constitutional_question.md` — parked question.
4. `tools_validation_engineering_campaign_plan.md` — the ratified engineering QA campaign plan (4 batches; 18 tools).
5. `validation/deliverable_tool_validation.md` — Batch A tool 1 report.
6. `validation/session_tool_validation.md` — Batch A tool 2 report.
7. `validation/search_docs_kb_tool_validation.md` — Batch A tool 3 report.
8. `validation/claude_code_tool_validation.md` — Batch A tool 4 report.
9. `validation/agent_introspection_run_agent_validation.md` — Batch A tool 5 report.

Test files added at `core/tests/`:

- `test_deliverable_tool_validation_2728.py` (17 tests)
- `test_session_tool_validation_2728.py` (7 tests)
- `test_search_docs_kb_tool_validation_2728.py` (21 tests)
- `test_claude_code_tool_validation_2728.py` (6 tests)
- `test_agent_introspection_run_agent_validation_2728.py` (13 tests)

Merged PRs: #3010 (`9f1f1e34`), #3011 (`30e7501e`).

## 8. Batch-close cleanup observations (deferred, not shipped in Batch A)

15+ cross-tool consistency observations logged in the individual validation reports but NOT included in the Batch A patches. Deferred to a future Batch A close doc pass or cross-tool consistency work:

- **Schema `required: ["action"]` violated by handler defaults** across `session_tool` (`'health_check'`), `kb_tool` (`'stats'`), `deliverable_tool` (`'list'`), `agent_introspection_tool` (`'inspect'`). LOW individually; systemic pattern.
- **Error envelope `ok: false` field consistency** across all 5 tools. Some error responses have `ok: false`; some just have `error` string. LOW individually; systemic.
- **Multi-alias parameter extraction undocumented** (F-CC-1: `claude_code_tool` accepts task/task_description/description/prompt/message; F-RA-BC-1: `_handle_agent_tool` accepts task/prompt/query).
- **Undocumented action aliases** (F-AI-BC-1: `agent_introspection_tool` accepts `detail`/`inspect` folded to `details`).
- **Index/corpus freshness signal missing** on `kb_tool` (no last-built timestamp in response — batch-close doc-only observation).

## 9. Next steps (S2729+)

**Immediate:** Batch B — Knowledge-substrate tools per campaign plan §3.2. Five tools:

- **B1: RAG retrieval path** (`core/rag_integration.py` + `canonical_authority` weighting).
- **B2: `repo_tool`** (repository-fact retrieval).
- **B3: `kb_ingest`** (write side of the KB).
- **B4: Provenance / `canonical_authority` filtering** (`content/_canonical_authority_helpers.py`).
- **B5: Workspace retrieval** (`workspace_manager.get_active_workspace` + `execute_with_workspace`).

Per campaign plan §10.2 "Between batches: Chris review gate." Batch B opens at Chris's explicit continue directive (given in the same S2728 message that closed Batch A + wrote this handoff — Chris directed "start Batch B" alongside handoff authoring; Batch B tool 1 begins immediately post-handoff-write).

**Later batches (queued):**

- **Batch C:** runtime substrate tools — context injection pipeline, payload-size limits, retrieval limits + hidden filters, ORM helper defaults, retry behavior.
- **Batch D:** worker & environment discipline — `PA_USE_FUNCTION_CALLING`, Celery worker lifecycle, worker cache behavior.

**Also queued but not batch-scoped:**

- Batch A close doc pass — sweep the 15+ cross-tool consistency observations logged in §8.
- Playbook v0.1.1 PATCH — CD-48 + CD-49 codification (from Session 2727 handoff §5).
- Expanded SIGN pass on the 95 remaining unaudited Playbook rules (from Session 2727 handoff §5).
- Cycle 2 hardening per 2712 §17 (content_hash population, ORM immutability signals, CI validation).

## 10. Session state at close

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD after merges | `30e7501e` (docs cascade merge) → will advance again with this handoff commit |
| Playbook v0.1.0 body commit | `b372edfe127f1af59c4322871092aa7151669463` — unchanged |
| Playbook tag | `playbook-v0.1.0` — unchanged |
| PA worker | PID 12820 (post-restart with S2728 patches active); `PA_USE_FUNCTION_CALLING=true` preserved |
| Active PA pin | `pa-44a6eb70d8814e34` (T4 Group 1700 Observability paused-research pin; preserved through S2728 for Batch A cross-check dispatches) |
| Rigby retrieval surface | 3,032/3,032 Documents embedded post-cascade; INDEX.md regenerated (3,021 docs); `_provenance.json` refreshed (2,471 docs indexed) |
| Constitutional debt | CD-47 RESOLVED (S2725); CD-48/CD-49 queued for v0.1.1 PATCH (unchanged from S2727) |
| Working tree | clean (post-merge) — this handoff + 00-START-NEXT-SESSION update will be the next commits |

**Session close protocol executed:** (a) all changes on main via PRs #3010 + #3011; (b) docs cascade run; (c) MEMORY annotations applied; (d) Rigby cross-check verified; (e) this handoff authored; (f) 00-START-NEXT-SESSION.md overwrite pending in same commit as this file.
