# Next Session — Start Here

---

## READ THIS FIRST — BATCH A OF THE TOOL VALIDATION CAMPAIGN CLOSED (SESSION 2728)

**Refreshed 2026-07-08 (SESSION 2728 close: Batch A of the Rigby Tool Validation Engineering Campaign shipped 5 tools, 17 defects, 64 regression tests to main).**

Prior anchor context: Engineering Playbook v0.1.0 ratified at Session 2727 close. Session 2728 opened with a constitutional-research directive on "operational contracts between Rigby and platform capabilities" — self-disproved after Chris's pressure-test discipline. Pivoted mid-session to engineering QA. Batch A closed.

The parked constitutional question (single reduced form) is preserved at [`docs/research/tools/tools_the_unanswered_constitutional_question.md`](docs/research/tools/tools_the_unanswered_constitutional_question.md) for future consideration — do NOT reopen without new evidence.

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD (post PR #3010 + PR #3011) | `30e7501e` — will advance again with the S2728 handoff commit |
| Playbook body commit_sha | `b372edfe127f1af59c4322871092aa7151669463` (unchanged from S2727) |
| Git tag | `playbook-v0.1.0` (unchanged) |
| Batch A close PR | #3010 merged as `9f1f1e34` (patches + tests + docs) |
| Docs cascade PR | #3011 merged as `30e7501e` (INDEX + provenance refresh) |
| Pending migrations | 0 |
| PA worker | PID 12820 post-restart with S2728 patches active |
| Docs cascade state | 3,032/3,032 Documents embedded; INDEX.md regenerated; `_provenance.json` fresh |

---

## Current constitutional state (post-Session 2728)

**Engineering Playbook v0.1.0: RATIFIED (unchanged from S2727).**

- 190 rules across 11 chapters. Constitutional debt state unchanged: CD-47 RESOLVED; CD-48 + CD-49 targeted for v0.1.1 PATCH.
- No Playbook amendments in S2728 (campaign work is engineering, not constitutional).

---

## Current tool-validation-campaign state (NEW — post-Session 2728)

**Batch A: CLOSED.** 5 tools verified. 17 defects patched. 64 regression tests + 3 MEMORY rule annotations. Zero regressions across 211-test cross-tool sweep.

| Batch A tool | Report | Defects patched | Commit |
|---|---|---|---|
| `deliverable_tool` | `docs/research/tools/validation/deliverable_tool_validation.md` | 9 (F-D-2/3/4/5/6/7/8/20/21) | `4b83a34f` |
| `session_tool` | `docs/research/tools/validation/session_tool_validation.md` | 2 (F-S-3, F-S-6) | `adcab784` |
| `search_docs` + `kb_tool` | `docs/research/tools/validation/search_docs_kb_tool_validation.md` | 2 (F-SD-1, F-KB-1) | `bb232e9b` |
| `claude_code_tool` | `docs/research/tools/validation/claude_code_tool_validation.md` | 1 (F-CC-3) | `4165856b` |
| `agent_introspection_tool` + `run_agent` | `docs/research/tools/validation/agent_introspection_run_agent_validation.md` | 3 (F-RA-1, F-RA-2/3, F-AI-2) | `39797aba` |

**MEMORY rules annotated at HEAD:**
- `feedback_deliverable_tool_use_append_for_large_payloads` — RESOLVED at S1177 (verified stale at HEAD).
- `feedback_ratification_workflow_gotchas` gotcha #3 — RESOLVED at S2728 (originating_session=0 autofill guard).
- `feedback_procfile_makefile_queue_parity` — VERIFIED-VALID (preventative PR-review discipline).

**Batches remaining:**
- **Batch B — Knowledge-substrate tools** (5 tools): RAG retrieval path, `repo_tool`, `kb_ingest`, provenance/canonical_authority filtering, workspace retrieval. **Chris directed "start Batch B" at S2728 close** — Batch B tool 1 (RAG retrieval path) begins immediately post-handoff.
- **Batch C — Runtime substrate tools** (context injection, payload size limits, retrieval limits + hidden filters, ORM helper defaults, retry behavior). Queued.
- **Batch D — Worker & environment discipline** (`PA_USE_FUNCTION_CALLING`, Celery worker lifecycle, worker cache behavior). Queued.

**Batch-close deferred work (15+ cross-tool consistency observations logged in the Batch A validation reports):** schema-`required` violated by handler defaults across 4 tools; error envelope `ok: false` consistency; multi-alias parameter extraction undocumented; undocumented action aliases; index/corpus freshness signal missing. To be swept at a future Batch A close doc pass.

---

## Current Rigby SIGN pin state

**Active pin at session-2728 close:** `pa-44a6eb70d8814e34` (T4 Group 1700 Observability paused-research pin; preserved through S2728 for Batch A cross-check dispatches).

**Fresh-session decision:** on next session open, decide based on task:
- **Batch B tool 1 (RAG retrieval path) opening** — no new pin needed; Batch B is engineering QA (not research SIGN), so the paused-research pin remains usable for Rigby cross-check dispatches at each tool's close.
- **Anything other than Batch B execution** — mint a new pin per playbook §16 fresh-thread discipline.

**Default PA wrapper (`tools/pa_local.sh`) currently points at:** `pa-44a6eb70d8814e34` (unchanged from S2727 close).

---

## Current recommended first task

**Continue Batch B tool 1: RAG retrieval path.** Chris directed "start Batch B" at S2728 close.

**Batch B scope (per campaign plan §3.2):**

1. **B1 — RAG retrieval path** (`core/rag_integration.py` + `canonical_authority` weighting). Load-bearing for Rigby's grounded reasoning.
2. **B2 — `repo_tool`** (repository-fact retrieval).
3. **B3 — `kb_ingest`** (write side of the KB).
4. **B4 — Provenance / `canonical_authority` filtering** (`content/_canonical_authority_helpers.py`).
5. **B5 — Workspace retrieval** (`workspace_manager.get_active_workspace` + `execute_with_workspace`).

Per-tool sequence per campaign plan §10.1:
1. Read schema + handler + related docs.
2. Author validation report skeleton with 20-question checklist.
3. Execute normal/empty/ambiguous/invalid-parameter/default/high-volume/stale test cases.
4. Classify findings (DEFECT / UNDER-DOCUMENTED / VERIFIED-CORRECT / PARKED-CONSTITUTIONAL / RIGBY-MISUNDERSTANDING).
5. Chris-gate on any patch shape not already ratified (mirror F-D-5 / F-D-6 / F-CC-3 / F-RA-1 pattern class where applicable).
6. Author patches (min diff, one per defect) + regression tests + re-run.
7. Close report.
8. Chris-gate at each batch boundary.

Recommended session-open protocol:
1. `context-kit orient` (mandatory session-open).
2. Read `docs/handoffs/SESSION_2728_TOOL_VALIDATION_BATCH_A_CLOSED.md` in full.
3. Read `docs/research/tools/tools_validation_engineering_campaign_plan.md` §3.2 (Batch B scope).
4. Confirm PA worker is up (`ps aux | grep hostname=pa` — expect PID from post-S2728-restart).
5. Begin Batch B tool 1 (RAG retrieval path) — schema location + handler location + tests in existing coverage.

---

## Reference documents (read order for post-Batch-A sessions)

Session 2728 outputs (post-Batch-A anchors):

1. [`docs/handoffs/SESSION_2728_TOOL_VALIDATION_BATCH_A_CLOSED.md`](docs/handoffs/SESSION_2728_TOOL_VALIDATION_BATCH_A_CLOSED.md) — **Session 2728 handoff + timeline + Batch A close artifacts.**
2. [`docs/research/tools/tools_validation_engineering_campaign_plan.md`](docs/research/tools/tools_validation_engineering_campaign_plan.md) — **the campaign plan Chris ratified.** Batch B scope in §3.2.
3. [`docs/research/tools/validation/`](docs/research/tools/validation/) — 5 validation reports (one per Batch A tool).
4. [`docs/research/tools/tools_the_unanswered_constitutional_question.md`](docs/research/tools/tools_the_unanswered_constitutional_question.md) — **PARKED**. The constitutional question surfaced by the S2728 opening detour; do NOT reopen without new evidence.

Session 2727 anchors (unchanged):

5. [`docs/handoffs/SESSION_2727_PLAYBOOK_V0_1_0_RATIFIED.md`](docs/handoffs/SESSION_2727_PLAYBOOK_V0_1_0_RATIFIED.md) — Playbook v0.1.0 ratification ledger.
6. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified Playbook v0.1.0 body.

Pre-Playbook-arc anchors (unchanged):

7. [`docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md`](docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md) — Cycle 1A ratification ledger.
8. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap.

---

## Session close summary (Session 2728)

- **Merged PRs:** #3010 (Batch A close — 5 tools, 17 defects, 64 regression tests), #3011 (docs cascade — INDEX + provenance refresh).
- **Constitutional-research detour:** self-disproved after Chris pressure-test; parked as single unanswered question at `docs/research/tools/tools_the_unanswered_constitutional_question.md`.
- **Engineering campaign:** Batch A of 4 batches closed. Batch B tool 1 begins immediately post-handoff per Chris directive.
- **Docs cascade:** 3,032/3,032 Documents embedded; Rigby's RAG surface current at HEAD.
- **Rigby cross-check:** her mental model correctly cites every patched pattern across all 5 tools; runtime verified live via both Rigby dispatch and direct Django-shell dispatch.
- **PA worker restart** required post-merge to reload code (documented as part of the session-close protocol per this campaign).
- **Handoff + anchor updates:** this file + `docs/handoffs/SESSION_2728_TOOL_VALIDATION_BATCH_A_CLOSED.md`.
- **Constitutional debt state:** unchanged from S2727 (CD-47 RESOLVED; CD-48/CD-49 v0.1.1 PATCH targets).

---
