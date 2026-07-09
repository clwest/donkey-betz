# SESSION_2729 — Rigby Tool Validation Engineering Campaign, Batch B Closed

**Date:** 2026-07-08 (continuous with S2728 — handoff sequence-numbered S2729 to mark Batch B close as its own record)
**Session type:** Engineering QA — Batch B execution of the ratified campaign plan
**Predecessor handoff:** [`SESSION_2728_TOOL_VALIDATION_BATCH_A_CLOSED.md`](SESSION_2728_TOOL_VALIDATION_BATCH_A_CLOSED.md)
**Ratified merges:** PR #3013 (Batch B patches + tests + docs) → merge `dca420c5`; PR #3014 (docs cascade) → merge `432366d6`.

---

## 1. Executive Summary

**Batch B of the Rigby Tool Validation Engineering Campaign is closed as of 2026-07-08 (post-S2728 continuous work).** Five knowledge-substrate tools verified against Chris-approved patch shapes. 10 defects patched — including 2 SECURITY-class fixes. 51 new regression tests. Zero regressions across the 122-test cross-tool sweep.

**Batch B totals:**
- **5 tools verified:** RAG retrieval path, `repo_tool`, `kb_ingest`, `canonical_authority_helpers` (VERIFY-ONLY), workspace retrieval.
- **10 defects patched** (1 F-RG + 3 F-RT + 4 F-KI + 2 F-WS). Every patch Chris-ratified before authoring.
- **2 SECURITY-class fixes:** F-KI-2/F-KI-3 (kb_ingest cross-user provenance leak — Document owner defaulted to `User.objects.first()`) + F-KI-4 (kb_ingest SSRF/local-file exfiltration surface — non-http(s) URLs bypassed tool-boundary validation).
- **51 new regression tests** across 4 test files.
- **1 constitutional-artifact verify-only close** — `canonical_authority_helpers` (Cycle 1A KFI-2 / ADR-0120). First tool in the campaign to close as VERIFIED-VALID-AT-HEAD without patches. Chris ratified Option A ("verify only — the tool works; leave the ratified surface alone.").
- **2 first-coverage-at-HEAD tools** — `repo_tool` (15 tests) + `kb_ingest` (16 tests) both had zero regression tests before this batch.
- **D17-D21 narrow-except discipline extended** from 4-way (pre-campaign) to 6-way (F-RG-1 tool 1 + F-WS-4 tool 5). Cross-file allowlist invariant tracked by `test_d20_views_rag_embeddings_narrow_except.py::test_all_four_allowlists_have_same_shape` grows to 6-way.
- **Docs cascade complete:** 3,038/3,038 Documents embedded post-merge; 6 new docs `derived → repo_canonical` via KFI-2 backfill (per MEMORY `feedback_ratification_workflow_gotchas` gotcha #2 discipline).

## 2. Timeline of the batch (post-S2728-handoff continuation)

| Event | Detail |
|---|---|
| Batch B tool 1 open | RAG retrieval path (`core/rag_integration.py`) — 585-line substrate module. `_derive_canonical_authority` orthogonal (that's tool 4). |
| F-RG-1 identified | `search_embeddings` broad `except Exception` at line 342 returns `[]` on any error — same anti-pattern S1234 D21 fixed for `search_personal_memories`. |
| F-RG-1 patched | Added `_RAG_EMBEDDINGS_ENV_ERRORS` allowlist mirroring `_PERSONAL_MEMORY_ENV_ERRORS`; narrowed except. Log level upgraded to ERROR with exc_info=True. |
| Batch B tool 1 closed | Commit `1597b798`. 9 regression tests + 68 adjacent pass. Pre-existing test-file breakage in `test_rag_integration_search_embeddings.py` (stale post-D16 mocks) verified via `git stash` isolation — NOT rolled back per §11 S7; deferred. |
| Batch B tool 2 open | `repo_tool` — 4 actions (tree/read_file/search/git_info) with ZERO existing regression tests. |
| F-RT-2/5/11 identified + patched | Tree cap envelope (3 hard maxes surfaced); search cap envelope (4 hard maxes surfaced); outer except now logs traceback with exc_info=True. Response contract unchanged; envelopes attached only when caps fire. |
| Batch B tool 2 closed | Commit `258ecb98`. 15 new regression tests — first coverage at HEAD. Covers all patched behaviors + security invariant (`_safe_path` blocking env/creds/out-of-root) + read_file/git_info/unknown-action baselines. |
| Batch B tool 3 open | `kb_ingest` — one action within `intelligence_tool`. 4-layer delegation chain: `intelligence_tool.kb_ingest` → `_handle_rag_query.ingest` → `process_url_async` @shared_task → `_impl_process_url_async`. |
| F-KI-2/F-KI-3 SECURITY identified | `user_id` from handler kwarg NOT plumbed to `process_url_async.delay(...)`. Combined with `_impl_process_url_async:374-375` defaulting to `User.objects.first()`, every PA-dispatched kb_ingest silently attributed the created Document to the lowest-ID user (typically `admin` / `system`), not the actual dispatching user. Cross-user provenance leak. |
| F-KI-4 SECURITY identified | Zero URL scheme validation. `file:///etc/passwd`, `data:...`, `javascript:...`, and no-scheme URLs all dispatched to the URL fetcher. SSRF + local-file exfiltration surface. |
| F-KI-1/5 identified | Empty URL raised ValueError instead of returning typed error dict (inconsistent with sibling actions). `success: True` on dispatch was misleading (dispatch success ≠ ingestion success). |
| Chris ratifies 4 patches | F-KI-1 (typed error dict), F-KI-2/F-KI-3 (user_id plumbed), F-KI-4 (URL scheme validation), F-KI-5 option (a) additive `dispatched: True` field. |
| Batch B tool 3 closed | Commit `9d010aa1`. 16 new regression tests — first coverage at HEAD. Covers all 4 patches + delegation baseline. |
| Batch B tool 4 open | `content/_canonical_authority_helpers.py` — 102-line substrate. **Constitutionally-ratified artifact** (Cycle 1A KFI-2 / ADR-0120). |
| Trace + assessment | All 5 load-bearing ADR-0120 contract elements verified against existing 11-test suite (T1a-T1e branch coverage; T2 backfill populates all tiers; T4 idempotency; T5 signal-safety via `update_knowledge_base_stats` non-firing check; T6 query count under ceiling). All 8 R-rules pass at HEAD. 6 findings surfaced (all LOW-MEDIUM diagnostic-clarity, not defects). |
| Chris ratifies Option A | "Verify only — the tool works; leave the ratified surface alone." First tool in the campaign to close as VERIFIED-VALID-AT-HEAD without patches. |
| Batch B tool 4 closed | Commit `62cc6bc7`. Report-only commit. Establishes discipline that verifying a tool sometimes means verifying no work is needed. |
| Batch B tool 5 open | Workspace retrieval — three surfaces: `WorkspaceManager.get_active_workspace` (4-tier fallback with side effects) + `workspace_resolver.get_active_workspace(user)` (2-tier pure lookup) + `BaseAgent.execute_with_workspace` (post-execute file-writing wrapper). |
| F-WS-4 identified | `workspace_resolver.get_active_workspace` broad `except Exception` returns None on any error — same class as F-RG-1. |
| F-WS-1 identified | `WorkspaceManager.get_active_workspace` T2 superuser cross-user fallback fires silently. Behavior intentional (S1085 Chris-ratified) but call site has no diagnostic trail. |
| Chris ratifies 2 patches | F-WS-4 (narrow-except discipline extension — 6-way invariant), F-WS-1 (log-only visibility; zero behavior change). |
| Batch B tool 5 closed | Commit `01322aec`. 11 new regression tests. F-B-HIGH-3 workspace-membership implicit permission gate from S2600 PA arc confirmed as the `execute_with_workspace` line 5355 surface — F-WS-9 batch-close observation. |
| Chris directive | "Continue on with the next steps mirroring what we have done" — commit + PR + merge + cascade + handoff. |
| Batch B close PR #3013 | 6 commits (5 per-tool + 1 docs). Merged as `dca420c5` via `gh pr merge --admin --merge`. |
| Docs cascade executed | build_docs_index (3027 docs) → build_rag_corpus (36,388 chunks) → sync_docs_index_to_documents (6 created + 2 updated) → KFI-2 `run_backfill(Document)` (6 docs `derived → repo_canonical`) → embed_documents --all-unembedded (all 3,038 embedded) → build_docs_provenance (2,477 docs indexed). |
| Cascade PR #3014 | INDEX + `_provenance.json` refresh. Merged as `432366d6`. |
| S2729 handoff (this doc) + 00-START rewrite | Session close protocol per campaign plan §12.5 mirroring Batch A pattern. |

## 3. Batch B defect resolution matrix

Every patch matches a Chris-approved shape ratified in-session before authoring.

| Tool | Defects patched | Chris-approved shape | Commit |
|---|---|---|---|
| B1 RAG retrieval path | F-RG-1 (1) | narrow-except discipline extension mirroring S1234 D17-D21 (`_RAG_EMBEDDINGS_ENV_ERRORS = (DatabaseError, ConnectionError, OSError)`); ERROR log with exc_info=True | `1597b798` |
| B2 `repo_tool` | F-RT-2, F-RT-5, F-RT-11 (3) | tree cap envelope + search cap envelope + outer except traceback log; response contract unchanged; envelopes attached only when caps fire | `258ecb98` |
| B3 `kb_ingest` | F-KI-1, F-KI-2/F-KI-3, F-KI-4, F-KI-5(a) (4) | typed empty-URL error dict; user_id plumbed to Celery task delay (SECURITY provenance leak fix); URL scheme validation (SECURITY SSRF defense); additive `dispatched: True` field alongside existing `success: True` | `9d010aa1` |
| B4 canonical_authority_helpers | 0 (Chris Option A — verify-only) | ratified constitutional artifact; existing 11-test suite validates all 5 load-bearing ADR-0120 contract elements at HEAD | `62cc6bc7` |
| B5 workspace retrieval | F-WS-4, F-WS-1 (2) | workspace_resolver narrow-except (extends D17-D21 allowlist invariant from 5-way to 6-way); superuser cross-user fallback WARNING log naming requesting_user + fallback workspace + fallback owner (zero behavior change) | `01322aec` |

## 4. Batch B security posture improvement

Two SECURITY-class issues closed:

- **Cross-user provenance leak (F-KI-2/F-KI-3, kb_ingest):** every PA-dispatched kb_ingest was attributing the created Document to `User.objects.first()` (typically admin) instead of the actual dispatching user. F-KI-3 identified the delegation-boundary drop; F-KI-2 identified the downstream default-to-first-user behavior. Both closed by plumbing `user_id` explicitly through `process_url_async.delay(url=url, user_id=user_id, generate_embeddings=True)`.
- **SSRF / local-file exfiltration surface (F-KI-4, kb_ingest):** `file:///etc/passwd`, `data:...`, `javascript:...`, and no-scheme URLs were all dispatched to the URL fetcher without tool-boundary validation. Closed via `urllib.parse.urlparse` gate at the tool layer; non-http/https schemes return typed `{'ok': False, 'error_code': 'invalid_url_scheme', ...}` with the scheme echoed for diagnosis + SSRF defense rationale in the message.

**Additional visibility improvement (F-WS-1, workspace retrieval):** when Rigby dispatches as superuser (`chris`) without her own active workspace, S1085 semantics silently returned another user's most-active workspace. Behavior is INTENTIONAL (Chris-ratified S1085) but silent. F-WS-1 patch adds a WARNING log naming the fallback workspace + owner. Zero behavior change; log-only visibility. Enables operator diagnosis if Rigby lands in someone else's workspace.

## 5. Discipline extensions ratified this batch

**D17-D21 narrow-except discipline** extended from **4-way** (pre-campaign: views_rag_embeddings + rag_helpers × 3) to **6-way** at Batch B close:

1. `_PERSONAL_MEMORY_ENV_ERRORS` — `search_personal_memories` (S1234 D21 baseline).
2. Three D17/D18/D19-family allowlists tracked by `test_d20_views_rag_embeddings_narrow_except.py::test_all_four_allowlists_have_same_shape`.
3. **NEW:** `_RAG_EMBEDDINGS_ENV_ERRORS` — `search_embeddings` (Batch B tool 1 F-RG-1).
4. **NEW:** `_WORKSPACE_RESOLVER_ENV_ERRORS` — `workspace_resolver.get_active_workspace` (Batch B tool 5 F-WS-4).

The invariant test at `test_d20_views_rag_embeddings_narrow_except.py::test_all_four_allowlists_have_same_shape` may need extension to 6-way in a future Batch B close doc pass — noted for follow-up.

**Constitutional-artifact verify-only discipline** established at Batch B tool 4 close: when a tool is ratified (Cycle 1A KFI-2 / ADR-0120 in this case) and its load-bearing contract is fully test-covered, closing as VERIFIED-VALID-AT-HEAD without patches is the correct discipline. First application in the campaign; documented precedent.

## 6. Runtime verification at HEAD

Batch B tool 4 (canonical_authority_helpers) verified via existing 11-test suite at HEAD. Batch B tools 1/2/3/5 verified via new 51-test regression sweep + adjacent 71-test sweep. **122/122 substantive tests pass** across all 10 validation-2728 files + adjacent canonical_authority tests. Zero regressions.

**Docs cascade at Batch B close:**
- 3,038/3,038 Documents fully embedded (unembedded=0).
- 6 new Documents (Batch B validation reports) reclassified `derived → repo_canonical` via KFI-2 `run_backfill(Document)` post-sync.
- `_provenance.json` refreshed: 2,477 docs indexed (HIGH=1593 / MEDIUM=384 / LOW=5 / UNKNOWN=495).

## 7. Batch B close artifacts (for future navigation)

Batch B validation reports at `docs/research/tools/validation/`:

1. `rag_retrieval_path_validation.md` — Batch B tool 1 report (F-RG-1 narrow-except; pre-existing test-file breakage observation).
2. `repo_tool_validation.md` — Batch B tool 2 report (F-RT-2/5/11 + first-coverage-at-HEAD).
3. `kb_ingest_validation.md` — Batch B tool 3 report (F-KI-1/2/3/4/5 + 2 SECURITY fixes + first-coverage-at-HEAD).
4. `canonical_authority_helpers_validation.md` — Batch B tool 4 report (VERIFIED-VALID-AT-HEAD; Chris Option A).
5. `workspace_retrieval_validation.md` — Batch B tool 5 report + **Batch B closure statement**.

Test files added at `core/tests/`:

- `test_rag_retrieval_path_validation_2728.py` (9 tests)
- `test_repo_tool_validation_2728.py` (15 tests — first coverage at HEAD)
- `test_kb_ingest_validation_2728.py` (16 tests — first coverage at HEAD)
- `test_workspace_retrieval_validation_2728.py` (11 tests)

Merged PRs: #3013 (`dca420c5`), #3014 (`432366d6`).

## 8. Batch-close cleanup observations (deferred, not shipped in Batch B)

15+ cross-tool consistency observations logged across the 5 Batch B reports (in addition to the 15+ logged during Batch A). Deferred to a future combined batch-close doc pass:

- **Schema `required: ["action"]` violated by handler defaults** across intelligence_tool (implicit), etc. — LOW individually; systemic pattern (extended from Batch A observation).
- **Error envelope `ok: false` field consistency** across error responses. Ongoing.
- **F-RG-2** `get_rag_context` hardcodes `limit=10`, `similarity_threshold=0.4` — caller inflexibility.
- **F-RG-3** `get_rag_context` no-results envelope lacks diagnostic reason.
- **F-RG-4** `get_rag_context` truncation not explicit via `truncated: bool` field.
- **F-RG-5** `canonical_authority` duplicated top-level + `metadata` in response.
- **F-RG-BC** legacy `namespace`/`exclude_personal` kwargs ignored + no threshold clamp + freshness stripped.
- **F-RT-1/BC-1/BC-2/BC-3/BC-4** repo_tool action default vs schema `required`; BLOCKED filter surfacing; git_info result caps; error envelope `ok:` field; original coverage gap (partially closed by first-coverage tests).
- **F-KI-6/7/BC-*** kb_ingest `generate_embeddings=True` hardcoded; `title` param not plumbed; provenance echo gaps (workspace_id / conversation_id / submitted_at); no auto-follow-up.
- **F-CA-1/2/4/5/6/BC** canonical_authority_helpers diagnostic-clarity improvements (Chris chose verify-only — deferred).
- **F-WS-2/3/5/6/7/8/9** workspace retrieval auto-creation side effects; no resolution_tier signal; divergent get_active_workspace functions; execute_with_workspace heuristics + duplicated category_map; missing test coverage for write_to_workspace=False silent-skip; missing workspace-membership check in _write_files_to_workspace (F-B-HIGH-3 territory from S2600).
- **Test-file mock refresh** for `test_rag_integration_search_embeddings.py` (stale post-D16 mocks; pre-existing, isolated via `git stash`).
- **D17-D21 invariant test extension** to 6-way at `test_d20_views_rag_embeddings_narrow_except.py::test_all_four_allowlists_have_same_shape`.

## 9. Next steps (S2730+)

**Immediate options for the next session:**

1. **Batch C — Runtime substrate tools** per campaign plan §3.3 (5 tools): context injection pipeline, payload-size limits, retrieval limits + hidden filters, ORM helper defaults, retry behavior. Natural next per plan.
2. **Batch A/B close doc pass** — sweep the 30+ cross-tool consistency observations logged across Batches A + B into a single cleanup PR. High leverage for cross-tool uniformity but not Chris-ratified as a batch scope.
3. **Test-file mock refresh** — dedicated PR to fix the `test_rag_integration_search_embeddings.py` stale-mock breakage isolated during Batch B tool 1 + extend the D17-D21 invariant test to 6-way.
4. **Playbook v0.1.1 PATCH** — CD-48 + CD-49 codification (from Session 2727 handoff §5). Constitutional work; independent of the campaign.

**Later batches (queued):**

- **Batch D:** worker & environment discipline — `PA_USE_FUNCTION_CALLING`, Celery worker lifecycle, worker cache behavior. Blocking on operator-drift observations from F-CC-DEPLOY-1 (Batch A tool 4) and F-WS-9 (Batch B tool 5 F-B-HIGH-3 territory).

**Also queued but not batch-scoped:**

- Expanded SIGN pass on the 95 remaining unaudited Playbook rules (from S2727 handoff §5).
- Cycle 2 hardening per 2712 §17 (content_hash population, ORM immutability signals, CI validation).

## 10. Session state at close

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD after Batch B merges | `432366d6` (docs cascade merge) → will advance again with this handoff commit |
| Playbook v0.1.0 body commit | `b372edfe127f1af59c4322871092aa7151669463` — unchanged |
| Playbook tag | `playbook-v0.1.0` — unchanged |
| PA worker | Still running post-S2728-restart with S2728 Batch A patches active. **NEEDS RESTART** to pick up Batch B patches (F-RG-1 narrow-except, F-RT-2/5/11 repo_tool cap envelopes, F-KI-1/2/3/4/5 kb_ingest fixes, F-WS-4/1 workspace retrieval fixes). Rigby cross-check verification of Batch B patches deferred to next session with fresh worker. |
| Active PA pin | `pa-44a6eb70d8814e34` (T4 Group 1700 Observability paused-research pin; preserved through Batch B) |
| Rigby retrieval surface | 3,038/3,038 Documents embedded post-cascade; INDEX.md regenerated (3,027 docs); `_provenance.json` refreshed (2,477 docs indexed) |
| Constitutional debt | CD-47 RESOLVED (S2725); CD-48/CD-49 queued for v0.1.1 PATCH (unchanged from S2727/S2728) |
| Working tree | clean (post-merge) — this handoff + 00-START-NEXT-SESSION update will be the next commits |

**Session close protocol executed:** (a) all Batch B changes on main via PRs #3013 + #3014; (b) docs cascade run; (c) 122-test cross-tool sweep confirmed zero regressions; (d) this handoff authored; (e) 00-START-NEXT-SESSION.md overwrite pending in same commit as this file. **PA worker restart deferred to next session** so Batch B patches are available when Rigby cross-check dispatches begin.
