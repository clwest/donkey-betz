# Next Session — Start Here

---

## READ THIS FIRST — BATCH B OF THE TOOL VALIDATION CAMPAIGN CLOSED (SESSION 2729)

**Refreshed 2026-07-08 (SESSION 2729 close: Batch B of the Rigby Tool Validation Engineering Campaign shipped 5 tools, 10 defects, 51 regression tests, and 2 SECURITY-class fixes to main).**

Prior anchor context: Engineering Playbook v0.1.0 ratified at Session 2727 close. Session 2728 opened with a constitutional-research directive that self-disproved and pivoted to engineering QA. Batch A closed at S2728. Session 2729 = Batch B execution (continuous with S2728 workday).

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD (post PR #3013 + PR #3014) | `432366d6` — will advance again with the S2729 handoff commit |
| Playbook body commit_sha | `b372edfe127f1af59c4322871092aa7151669463` (unchanged from S2727) |
| Git tag | `playbook-v0.1.0` (unchanged) |
| Batch B close PR | #3013 merged as `dca420c5` (patches + tests + reports) |
| Docs cascade PR | #3014 merged as `432366d6` (INDEX + provenance refresh) |
| Pending migrations | 0 |
| PA worker | Post-S2728-restart with Batch A patches active. **NEEDS RESTART** to load Batch B patches when Rigby cross-check dispatches begin. |
| Docs cascade state | 3,038/3,038 Documents embedded; INDEX.md regenerated (3,027 docs); `_provenance.json` fresh |

---

## Current constitutional state (unchanged from S2727)

**Engineering Playbook v0.1.0: RATIFIED.** No amendments in S2728/S2729. CD-47 RESOLVED; CD-48 + CD-49 targeted for v0.1.1 PATCH.

---

## Current tool-validation-campaign state (post-Session 2729)

**Batch A: CLOSED (S2728).** 5 tools verified; 17 defects patched; 64 regression tests; 3 MEMORY rule annotations.

**Batch B: CLOSED (S2729).** 5 tools verified; 10 defects patched; 51 regression tests; **2 SECURITY-class fixes** (F-KI-2/F-KI-3 kb_ingest cross-user provenance leak + F-KI-4 kb_ingest SSRF surface).

| Batch B tool | Report | Defects patched | Commit |
|---|---|---|---|
| B1 RAG retrieval path | `docs/research/tools/validation/rag_retrieval_path_validation.md` | 1 (F-RG-1) | `1597b798` |
| B2 `repo_tool` | `docs/research/tools/validation/repo_tool_validation.md` | 3 (F-RT-2, F-RT-5, F-RT-11) | `258ecb98` |
| B3 `kb_ingest` | `docs/research/tools/validation/kb_ingest_validation.md` | 4 (F-KI-1, F-KI-2/F-KI-3, F-KI-4, F-KI-5(a)) | `9d010aa1` |
| B4 canonical_authority_helpers | `docs/research/tools/validation/canonical_authority_helpers_validation.md` | **0 (VERIFY-ONLY; Chris Option A)** | `62cc6bc7` |
| B5 workspace retrieval | `docs/research/tools/validation/workspace_retrieval_validation.md` | 2 (F-WS-4, F-WS-1) | `01322aec` |

**Batch B highlights:**
- **2 SECURITY-class fixes:** F-KI-2/F-KI-3 (cross-user provenance leak) + F-KI-4 (SSRF surface).
- **1 constitutional-artifact verify-only close** — canonical_authority_helpers (Cycle 1A KFI-2 / ADR-0120). First tool in campaign to close as VERIFIED-VALID-AT-HEAD without patches.
- **2 first-coverage-at-HEAD tools** — repo_tool (15 tests) + kb_ingest (16 tests) had zero regression tests before this batch.
- **D17-D21 narrow-except discipline extended** from 4-way to 6-way (F-RG-1 tool 1 + F-WS-4 tool 5).
- **122/122 substantive tests pass** across all 10 validation-2728 files + adjacent canonical_authority tests. Zero cross-tool interference.

**MEMORY rules status (unchanged from Batch A + reinforcements):**
- 3 annotated at Batch A: `feedback_deliverable_tool_use_append_for_large_payloads` (RESOLVED), `feedback_ratification_workflow_gotchas` gotcha #3 (RESOLVED), `feedback_procfile_makefile_queue_parity` (VERIFIED-VALID).
- Batch B reinforcements: `feedback_procfile_makefile_queue_parity` (implicit via tool 3 default queue verification), `feedback_pa_local_verify_ownership` (workspace ownership discipline reinforced at tool 5), `feedback_ratification_workflow_gotchas` gotcha #2 (KFI-2 backfill discipline exercised in cascade).

**Batches remaining:**

- **Batch C — Runtime substrate tools** (5 tools): context injection pipeline, payload-size limits, retrieval limits + hidden filters, ORM helper defaults, retry behavior. Queued per campaign plan §3.3.
- **Batch D — Worker & environment discipline** (`PA_USE_FUNCTION_CALLING`, Celery worker lifecycle, worker cache behavior). Queued. Blocking on operator-drift observations from F-CC-DEPLOY-1 (Batch A tool 4) and F-WS-9 (Batch B tool 5 F-B-HIGH-3 territory from S2600 PA arc).

**Combined batch-close deferred work (30+ cross-tool consistency observations logged across Batches A + B):** schema-`required` violated by handler defaults; error envelope `ok: false` consistency; multi-alias parameter extraction undocumented; undocumented action aliases; index/corpus freshness signal missing; test-file mock refresh for `test_rag_integration_search_embeddings.py`; D17-D21 invariant test extension to 6-way at `test_d20_views_rag_embeddings_narrow_except.py::test_all_four_allowlists_have_same_shape`. To be swept at a future combined batch-close doc pass.

---

## Current Rigby SIGN pin state

**Active pin at session-2729 close:** `pa-44a6eb70d8814e34` (T4 Group 1700 Observability paused-research pin; preserved through Batches A + B for cross-check dispatches).

**Fresh-session decision:** on next session open, decide based on task:
- **Continue campaign (Batch C or A/B close doc pass)** — no new pin needed; paused-research pin remains usable.
- **Rigby cross-check of Batch B patches** — no new pin; but requires PA worker restart to load Batch B code (see below).
- **Anything other than campaign execution** — mint a new pin per playbook §16 fresh-thread discipline.

**Default PA wrapper (`tools/pa_local.sh`) currently points at:** `pa-44a6eb70d8814e34` (unchanged from S2727 close).

**PA worker restart REQUIRED before Rigby-side Batch B verification:** current worker (PID 12820 from S2728 restart) has Batch A patches loaded but NOT Batch B. To verify F-RG-1, F-RT-2/5/11, F-KI-1/2/3/4/5, F-WS-4/1 via Rigby dispatch, run `make celery-stop && make celery` per S2728 handoff §10 discipline.

---

## Current recommended first task

**Chris-choice among four options** (per S2729 handoff §9):

1. **Batch C — Runtime substrate tools** per campaign plan §3.3. Natural next; 5 tools queued.
2. **Batch A/B close doc pass** — sweep the 30+ cross-tool consistency observations logged across A + B into a single cleanup PR. High leverage for uniformity.
3. **Test-file mock refresh** — dedicated PR to fix `test_rag_integration_search_embeddings.py` stale-mock breakage + extend D17-D21 invariant test to 6-way.
4. **Playbook v0.1.1 PATCH** — CD-48 + CD-49 codification (from S2727 handoff §5). Constitutional work; independent of the campaign.

Recommended session-open protocol:
1. `context-kit orient` (mandatory session-open).
2. Read `docs/handoffs/SESSION_2729_TOOL_VALIDATION_BATCH_B_CLOSED.md` in full.
3. Confirm PA worker state — `ps aux | grep hostname=pa` — restart if Batch B verification via Rigby is planned.
4. If Chris chooses Batch C: read `docs/research/tools/tools_validation_engineering_campaign_plan.md` §3.3 (Batch C scope). Begin Batch C tool 1 (context injection pipeline).
5. If Chris chooses doc-pass or mock refresh: read the batch-close observation lists in the 10 Batch A + B validation reports.

---

## Reference documents (read order for post-Batch-B sessions)

Session 2729 outputs (post-Batch-B anchors):

1. [`docs/handoffs/SESSION_2729_TOOL_VALIDATION_BATCH_B_CLOSED.md`](docs/handoffs/SESSION_2729_TOOL_VALIDATION_BATCH_B_CLOSED.md) — **Session 2729 handoff + Batch B close artifacts.**
2. [`docs/research/tools/tools_validation_engineering_campaign_plan.md`](docs/research/tools/tools_validation_engineering_campaign_plan.md) — **the campaign plan Chris ratified.** Batch C scope in §3.3.
3. [`docs/research/tools/validation/`](docs/research/tools/validation/) — **10 validation reports** (5 Batch A + 5 Batch B).

Session 2728 anchors:

4. [`docs/handoffs/SESSION_2728_TOOL_VALIDATION_BATCH_A_CLOSED.md`](docs/handoffs/SESSION_2728_TOOL_VALIDATION_BATCH_A_CLOSED.md) — Session 2728 handoff + Batch A close.

Session 2727 anchors (unchanged):

5. [`docs/handoffs/SESSION_2727_PLAYBOOK_V0_1_0_RATIFIED.md`](docs/handoffs/SESSION_2727_PLAYBOOK_V0_1_0_RATIFIED.md) — Playbook v0.1.0 ratification ledger.
6. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified Playbook v0.1.0 body.

Pre-Playbook-arc anchors (unchanged):

7. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap.

---

## Session close summary (Session 2729)

- **Merged PRs:** #3013 (Batch B close — 5 tools, 10 defects, 51 regression tests, 2 SECURITY fixes), #3014 (docs cascade — INDEX + provenance refresh).
- **Engineering campaign:** Batch B of 4 batches closed. 2 of 4 batches complete (A + B).
- **Docs cascade:** 3,038/3,038 Documents embedded; Rigby's RAG surface current at HEAD.
- **Cross-tool regression:** 122/122 substantive tests pass across all validation-2728 files + adjacent canonical_authority. Zero regressions.
- **Constitutional debt state:** unchanged from S2727 (CD-47 RESOLVED; CD-48/CD-49 v0.1.1 PATCH targets).
- **Handoff + anchor updates:** this file + `docs/handoffs/SESSION_2729_TOOL_VALIDATION_BATCH_B_CLOSED.md`.
- **PA worker restart** deferred to next session (Batch B patches are loaded from repo but not yet in the running worker).

---
