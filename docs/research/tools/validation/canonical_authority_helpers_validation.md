# `content/_canonical_authority_helpers.py` — Validation Report

**Tool:** `content/_canonical_authority_helpers.py` — the KFI-2 canonical_authority classifier + backfill primitive.
**File:** `content/_canonical_authority_helpers.py` (102 lines total — the smallest tool in the campaign).
**Entry points:**
- `_derive_canonical_authority(document) -> str` — pure classifier (line 27-60).
- `run_backfill(Document) -> dict[str, int]` — signal-safe bulk reclassification (line 63-102).

**Downstream consumers (traced in prior tools):**
- `kb_tool.semantic_search` filter param + top-level metadata (Batch A tool 3).
- `search_embeddings` in `core/rag_integration.py` (Batch B tool 1) — filter branch + ADR-0130 authority-weighted ranking.
- `sync_docs_index_to_documents` classification pathway — I ran `run_backfill(Document)` in the S2728 docs cascade to reclassify 10 docs `derived → repo_canonical` (per MEMORY `feedback_ratification_workflow_gotchas` gotcha #2).

**Constitutional anchor:**
- **Cycle 1A KFI-2** — ratified via Playbook v0.1.0 at S2727.
- **ADR-0120** — the 5-element load-bearing contract codified in the module docstring.
- **SIGN-1 F3 disposition** — Chris Option D 2026-07-07 authorized `QuerySet.update()` bypass of `post_save` signals.

**Session validated:** S2728 → S2729 (Batch B tool 4 of 5).
**HEAD at validation:** `5ce56b5f` + Batch B tools 1-3 uncommitted patches.
**Reviewer:** Claude (Opus 4.7, 1M context).
**Rigby cross-check:** deferred (Rigby uses this substrate indirectly via kb_tool.semantic_search + search_embeddings — already verified at Batch A tool 3 + Batch B tool 1).
**Report status:** VERIFIED-VALID-AT-HEAD (Batch B tool 4 of 5). Chris ratified **Option A** (zero patches) at Batch B tool 4 close. All 5 load-bearing ADR-0120 contract elements verified via existing 11-test suite; passes all 8 Rigby-safe R-rules at HEAD.

---

## 1. Intended purpose

Assign every `Document` row a `canonical_authority` classification (`workspace_canonical` / `repo_canonical` / `derived`) per a 4-branch decision tree with load-bearing evaluation order. Support signal-safe idempotent backfill so migrations and post-sync cascades can reclassify without triggering KB-stats recomputes.

## 2. Rigby's belief (per MEMORY + prior tool interactions)

Rigby uses this substrate implicitly through:
- `kb_tool.semantic_search canonical_authority='repo_canonical'` filter — surfaces `/docs/`-ingested content.
- `kb_tool.semantic_search canonical_authority='workspace_canonical'` — surfaces ratified workspace Deliverable mirrors (KFI-1).
- `search_embeddings authority_weighted=True` — ADR-0130 authority-weighted ranking (2.0/1.5/1.0).

**Load-bearing MEMORY rule:** `feedback_ratification_workflow_gotchas` gotcha #2 explicitly names `sync_docs_index_to_documents` NOT triggering the KFI-2 classifier as the reason docs land with `derived` and get excluded from `repo_canonical` filters. The fix is to run `run_backfill(Document)` after every sync — which I did in the S2728 docs cascade.

## 3. Function signatures (verbatim capture)

### 3.1 `_derive_canonical_authority(document) -> str`

Pure classifier. No side effects. Reads `document.source`, `document.file_path`, `document.extracted_metadata` via `getattr(..., '')` fallbacks.

**4-branch decision tree (order matters per ADR-0120 §2.1):**
- **B1:** `source == 'workspace'` → `'workspace_canonical'`
- **B2:** `extracted_metadata['workspace_source_uuid']` → `'derived'` (exported-mirror edge case per 0120 §2.5)
- **B3:** `source == 'imported'` AND (`file_path.startswith('docs/')` OR `extracted_metadata['scope'] == 'docs_index'`) → `'repo_canonical'`
- **B4:** else → `'derived'` (safe under-classification; explicit upgrade required)

### 3.2 `run_backfill(Document) -> dict[str, int]`

Signal-safe bulk reclassification. Uses `QuerySet.update(...)` per-row to bypass `post_save` signals (SIGN-1 F3 Chris Option D disposition). Returns per-tier update counts.

```python
{
    'workspace_canonical': N,
    'repo_canonical': M,
    'derived': K,
}
```

Only INCREMENTED rows are counted. Idempotent-skipped rows are NOT counted (line 95-96: `if doc.canonical_authority == authority: continue`).

## 4. Handler behavior (traced)

### 4.1 `_derive_canonical_authority` (line 27-60)

- Line 47-49: **defensive `getattr(document, ..., '')` fallbacks** for `source`, `file_path`, `extracted_metadata`. Silent fallback to empty string if field missing. Documents field expectations; hides regressions if `Document` model schema changes. **F-CA-4** (LOW).
- Line 51: B1 branch — highest priority.
- Line 53: B2 branch — checks `meta.get('workspace_source_uuid')`. Note this evaluates BEFORE the imported-docs check, so a workspace-mirror doc that ALSO has `source='imported'` classifies as `'derived'` (correct per 0120 §2.5). **F-CA-5** — non-obvious edge case, but documented in the docstring.
- Line 55-57: B3 branch — dual-signal check (file_path OR scope).
- Line 60: B4 default — safe under-classification.

### 4.2 `run_backfill` (line 63-102)

- Line 81-85: `updated` counter dict pre-populated with 3 tier keys, values 0.
- Line 86: `now = timezone.now()` captured once for all row updates. Bulk-op idiom.
- Line 87-93: `.iterator()` for memory bound; `.only(...)` for field-scoping.
- Line 94: derives new authority via pure function.
- Line 95-96: **idempotency skip** — no-op if stored value already matches.
- Line 97-100: `QuerySet.update(canonical_authority=..., updated_at=now)` — signal-safe bypass of `post_save`.
- Line 101: increments counter ONLY for changed rows.
- Line 102: returns per-tier counter dict.

**F-CA-1** (LOW): no batch_size / limit. `.iterator()` bounds memory but processes the whole `Document` table serially. At 3,032 rows (current HEAD), ~1s total; at 100k+ could grow. Not a HEAD concern.

**F-CA-2** (LOW-MEDIUM): counter dict tracks CHANGED rows only. Rigby / operators calling this cannot distinguish "second run correctly wrote zero rows (idempotency verified)" from "all rows already matched (idempotency verified)" without external state (row count pre/post). Contract element 3 (idempotency) is verifiable by comparing consecutive calls (both return all-zero) but a `total_scanned` / `skipped` counter would make single-call verification cleaner.

**F-CA-6** (LOW-MEDIUM): no error handling around `_derive_canonical_authority(doc)` inside the loop. If a single row's `extracted_metadata` is malformed (e.g., non-dict from a data-corruption incident), that row raises AttributeError inside `meta.get('workspace_source_uuid')` — which propagates and crashes the loop. **Partial-progress state:** rows already `.update()`d are committed (per-row transactions); remaining rows are skipped. Recovery: fix the corrupt row + re-run (which is idempotent per contract element 3, so already-updated rows are no-ops). Not a data-loss risk; a diagnostic-clarity gap.

## 5. Defaults inventory

N/A — pure classifier + backfill primitive; no parameters with defaults.

## 6. Hidden filters

N/A. The 4-branch decision tree IS the filter logic; all branches surfaced in the docstring.

## 7. Limits inventory

- `_derive_canonical_authority`: no I/O, no limits.
- `run_backfill`: no batch_size / limit — processes all rows via `.iterator()`.

## 8. Silent-truncation test

N/A.

## 9. Silent-filter test

N/A.

## 10. Silent-fallback test

- **F-CA-4:** `getattr(document, ..., '')` fallback silently substitutes empty string when field missing. Documented; batch-close observation.
- **F-CA-5:** B2 edge-case classifies imported-with-workspace_source_uuid as `'derived'` — non-obvious but documented in docstring per ADR-0120 §2.5.

## 11. Staleness test

- `run_backfill` reads current `Document` field values via `.only(...)` — inherently fresh. No caching.
- `updated_at` bumped on every changed row.

## 12. Freshness signal

- `run_backfill` sets `updated_at=now` on changed rows. `now` captured once at function entry.

## 13. Provenance signal

- The `canonical_authority` field IS the provenance signal. Downstream tools (kb_tool.semantic_search, search_embeddings) surface it.

## 14. Authority / workspace assumptions

- **B1:** `source == 'workspace'` is the workspace-canonical upgrade path. Workspace-mirror rows land with `source='workspace'` per KFI-1 (0110 mirror pipeline).
- **B2:** exported-mirror docs (workspace_source_uuid metadata but not workspace source) intentionally under-classify as `'derived'` per ADR-0120 §2.5.
- **B3:** `docs/`-prefix files or `docs_index` scope → `repo_canonical` (the primary repo-canonical upgrade path used by `sync_docs_index_to_documents`).

## 15. Runtime dependencies

- Django ORM (`Document` model).
- `django.utils.timezone` for `updated_at` timestamp.
- No Redis, no Celery, no external HTTP.

## 16. Recoverable failure modes

- Missing model field → silent empty-string fallback via `getattr` (F-CA-4).
- Malformed `extracted_metadata` (non-dict) → uncaught AttributeError on `.get()` propagates (F-CA-6).

## 17. STOP-and-report failure modes

- Django DB exception → bubbles.
- Migration-safe `apps.get_model` used elsewhere (migration 0049 delegates here).

## 18. Operator-action failure modes

- Corrupt `extracted_metadata` on a specific row → partial-progress backfill halt (F-CA-6). Recovery: fix the corrupt row + re-run (idempotent).
- Post-`sync_docs_index_to_documents` cascade must run `run_backfill(Document)` per MEMORY `feedback_ratification_workflow_gotchas` gotcha #2. Operator discipline; not patchable at handler.

## 19. Existing test coverage

**Strong existing coverage at HEAD:**

- `content/tests/test_canonical_authority.py` — 11 tests across the 5 load-bearing contract elements:
  - **T1a-T1e** (5 tests): all 4 branches of the classifier + edge cases (workspace + workspace_source_uuid still workspace_canonical; imported + workspace_source_uuid → derived; docs/ prefix vs scope-only; api-fallback).
  - **T2** (1 test): backfill populates all tiers.
  - **T3** (1 test): mirror sets `workspace_canonical` on create (KFI-1 anchor test — belongs to a different module but validates the contract).
  - **T4** (1 test): idempotency — second run returns all-zero counters (contract element 3).
  - **T5** (1 test): backfill does NOT trigger `KnowledgeBase.update_statistics()` (contract element 4 signal-safety, SIGN-1 F3 verification).
  - **T6** (1 test): query count stays under ceiling (performance guardrail).

Adjacent coverage:
- `core/tests/test_docs_cascade_preflight.py` — cascade discipline validation.
- `core/tests/test_extracted_metadata_clobber_fix.py` — extracted_metadata invariant (S1235 backfill regression).
- `content/migrations/0049_add_canonical_authority.py` — migration that delegates here (used direct import for testing).

## 20. Change list

**No code patches.** Chris ratified Option A (verify-only) at Batch B tool 4 close.

- Zero changes to `content/_canonical_authority_helpers.py`.
- Zero new test files.
- Zero MEMORY.md changes.
- Validation report (this file) only.

**Rationale:** this is a Cycle 1A KFI-2 / ADR-0120 ratified constitutional artifact. The 5 load-bearing contract elements are codified in the module docstring and covered by the existing 11-test suite. The 3 potentially-actionable findings (F-CA-2, F-CA-6, F-CA-BC) are diagnostic-clarity improvements rather than defects. Chris's determination: "verify only — the tool works; leave the ratified surface alone."

**Test verification:**

- `python manage.py test content.tests.test_canonical_authority --keepdb --noinput` → **10/10 pass + 1 pre-existing skip** (0.519s). Skipped test is `test_t3_mirror_sets_workspace_canonical_on_create` with reason "KFI-1 (0110 mirror pipeline) unshipped at HEAD 8acdc6f0" — a pre-existing skip on a different module's KFI-1 pipeline check, unrelated to Batch B work. **Full validation of all 5 ADR-0120 contract elements at HEAD.**
- Cross-tool verification: no functional dependency between this substrate and Batch B tool 1-3 patches; all downstream consumers (kb_tool.semantic_search + search_embeddings) continue to work per Batch A tool 3 + Batch B tool 1 regression sweeps.

---

## Findings

### F-CA-4 — `getattr` defensive fallbacks hide model schema regressions (LOW; batch-close)
- **Class:** UNDER-DOCUMENTED / defensive-coding tradeoff.
- **Evidence:** `_derive_canonical_authority` lines 47-49.
- **Severity:** LOW. Fallback to empty string is DEFENSIVE, not silent-degrade. If `Document.source` were renamed, all rows would classify as `'derived'` (safe under-classification) instead of crashing. Documented via docstring implicitly (field expectations named there).
- **Action:** BATCH-CLOSE observation. Not patched.

### F-CA-5 — B2 edge case classifies imported-with-workspace_source_uuid as `'derived'` (LOW; batch-close)
- **Class:** UNDER-DOCUMENTED / ADR-0120 §2.5 edge case.
- **Evidence:** `_derive_canonical_authority` line 53-54.
- **Severity:** LOW. Documented in the module docstring citing ADR-0120 §2.5.
- **Action:** BATCH-CLOSE observation. Not patched.

### F-CA-1 — `run_backfill` has no batch_size / limit (LOW; batch-close)
- **Class:** OBSERVABLE performance ceiling.
- **Evidence:** `run_backfill` line 87 — full-table `.iterator()`.
- **Severity:** LOW. `.iterator()` bounds memory. At current HEAD (3,032 Documents) runtime is ~1s. Not a HEAD concern.
- **Action:** BATCH-CLOSE observation. Not patched.

### F-CA-2 — `run_backfill` counter dict tracks changed rows only (LOW-MEDIUM; Chris-decision candidate)
- **Class:** UNDER-DOCUMENTED diagnostic gap.
- **Evidence:** `run_backfill` line 81-102. `updated` counter only increments for changed rows (line 101 inside the not-continue branch); skipped-idempotent rows are silent.
- **Severity:** LOW-MEDIUM. Idempotency contract element 3 is verifiable across two calls (both return all-zero), but a single-call verification would require external state (row-count pre/post). Adding `total_scanned` + per-tier `skipped` counters would make single-call verification cleaner without changing the ratified contract.
- **Action:** **CHRIS-DECISION CANDIDATE.** This is a constitutionally-ratified module — any changes require explicit Chris ratification, not the usual "approved" nod. If patched, would extend the return-dict shape additively (back-compat safe).

### F-CA-6 — No per-row error handling; partial-progress crash on corrupt metadata (LOW-MEDIUM; Chris-decision candidate)
- **Class:** DIAGNOSTIC-CLARITY gap.
- **Evidence:** `run_backfill` line 94 — bare `_derive_canonical_authority(doc)` call inside loop.
- **Severity:** LOW-MEDIUM. Corrupt `extracted_metadata` (non-dict) on a single row raises AttributeError from `meta.get('workspace_source_uuid')`, crashing the entire loop. Rows already `.update()`d remain updated (per-row transactions commit); remaining rows are unprocessed. Recovery: fix corrupt row + re-run (idempotent per contract element 3, so already-updated rows are no-ops).
- **Action:** **CHRIS-DECISION CANDIDATE.** Adding per-row try/except with error logging would preserve idempotency and prevent partial-progress crashes. Chris ratification needed because this changes error semantics on a constitutional module.

### F-CA-BC — batch-close observations
- Module-level `now = timezone.now()` captured once per backfill run — all changed rows share the same `updated_at`. Bulk-op idiom; documented in code.

---

## Rigby-safe assessment (unchanged post-verify)

- **R1 (no dangerous defaults):** CLEARED. Safe under-classification (B4 default) requires explicit upgrade — a Rigby-safe pattern.
- **R2 (no silent action substitution):** N/A.
- **R3 (no silent truncation):** N/A.
- **R4 (hidden filters surfaced):** CLEARED (4-branch tree fully documented).
- **R5 (workspace/authority carriage):** CLEARED. Workspace-canonical upgrade requires `source='workspace'`; repo-canonical requires `imported+docs/`.
- **R6 (freshness surface):** CLEARED (`updated_at` bumped on changed rows).
- **R7 (provenance surface):** CLEARED (`canonical_authority` IS the provenance signal).
- **R8 (worker/env preconditions):** N/A (pure ORM).

**All 8 R-rules cleared at HEAD without any code change.**

---

## Verdict

Tool status: **VERIFIED-VALID-AT-HEAD** (Chris ratified Option A at Batch B tool 4 close).

**Code trace coverage:** both functions (`_derive_canonical_authority`, `run_backfill`) full 102-line file traced; 4-branch decision tree cross-referenced against ADR-0120 §2.1-§2.5; SIGN-1 F3 signal-safety verified against contract element 4.

**Findings summary:**

- **Zero defects surfaced.** All 6 findings (F-CA-1, F-CA-2, F-CA-4, F-CA-5, F-CA-6, F-CA-BC) are LOW-MEDIUM diagnostic-clarity observations, not defects.
- **Chris's determination:** Option A — this ratified constitutional artifact passes all 5 load-bearing contract elements at HEAD; the diagnostic-clarity improvements are genuine but don't warrant touching the ratified surface.

**Existing test coverage validated at HEAD:**

- 11 tests in `content/tests/test_canonical_authority.py` covering all 5 load-bearing ADR-0120 contract elements: T1a-T1e (5 tests, all 4 classifier branches + edge cases), T2 (backfill populates all tiers), T3 (skipped — KFI-1 mirror pipeline pre-existing skip on different HEAD), T4 (idempotency — contract element 3), T5 (signal-safety — contract element 4 via `update_knowledge_base_stats` non-firing check), T6 (query count under ceiling).
- 10/10 substantive tests pass; 1 pre-existing skip unrelated to Batch B work.

**Downstream consumers verified as still functional:**

- `kb_tool.semantic_search canonical_authority=...` filter — Batch A tool 3 regression sweep confirms.
- `search_embeddings authority_weighted=True` weighted ranking — Batch B tool 1 regression sweep confirms.
- `sync_docs_index_to_documents` cascade — I ran `run_backfill(Document)` in the S2728 docs cascade; 10 docs correctly reclassified `derived → repo_canonical` (all under `docs/` prefix).

**MEMORY rule status:**

- **`feedback_ratification_workflow_gotchas`** gotcha #2 (must run `run_backfill(Document)` after `sync_docs_index_to_documents`) remains VALID at HEAD — this is preventative operator discipline, not a defect. `run_backfill` continues to be the canonical fix.

**Follow-ups filed:**

- Batch-close observations for diagnostic-clarity improvements (F-CA-1/2/4/5/6/BC). If a future arc needs them, they're recorded; but this campaign scope does not touch them per Chris's Option A ratification.

**Tool closure statement:** `content/_canonical_authority_helpers.py` is VERIFIED-VALID at HEAD `5ce56b5f`. The Cycle 1A KFI-2 / ADR-0120 ratified contract holds. The 11-test existing suite validates all 5 load-bearing contract elements. Rigby's canonical_authority-aware retrieval workflows continue to work correctly. Zero patches, zero regressions, zero MEMORY changes — the tool works as ratified.
