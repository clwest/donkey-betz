---
title: "Session 1108 — build_rag_corpus producer (Option B, PR 1)"
date: 2026-05-08
status: active
session: 1108
previous_handoff: SESSION_1107_CI_GUARDRAIL_WIRING.md
---

# Session 1108 — build_rag_corpus producer (Option B, PR 1)

## TL;DR

- **Shipped:** new management command `python manage.py build_rag_corpus`. Walks `docs/_index.json` (produced by `build_docs_index`), chunks each doc, and emits `.rag/corpus.jsonl` in the JSONL shape `core/rag.py:top_k()` reads.
- **Why:** `.rag/corpus.jsonl` was an orphan — tracked artifact (6.5 MB), no in-repo producer, no path to regenerate. Per Session 1102 investigation it is **production-dormant** (production PA RAG goes through `core.rag_integration` + pgvector). Adding a producer is PR 1 of the Option B plan; PR 2 will untrack `.rag/` once this lands.
- **No production behavior changes.** `core.rag_integration`, `EmbeddingService`, `unified_embeddings`, `Document` model, and the entire PA / Rigby retrieval path are untouched. Only the local-only Ollama `askdocs` lane is affected.
- **Tests:** 6 new tests in `core/tests/test_build_rag_corpus.py`, all passing. DB-free, no network/LLM calls.
- **Carryover:** `stash@{0}` (Docker subnet override) still preserved.

---

## What Shipped

### 1. `core/management/commands/build_rag_corpus.py` — new command (~170 lines)

Reads `docs/_index.json`, iterates `documents[].path`, chunks each doc, writes JSONL. Output row shape:

```json
{"file": "audits/learning-loop-discovery.md", "chunk_id": 1, "text": "..."}
```

- Paths under `docs/` are stripped of the `docs/` prefix to match the existing artifact convention and the `core.rag.PREF_FILE_BONUS` regexes (e.g., `audits/.*learning[-_ ]loop`). Root-level docs (e.g., `CLAUDE.md`) keep their bare name.
- `chunk_id` is 1-indexed, matching the existing on-disk artifact.
- Chunk size defaults to 1200 chars with no overlap (matches existing artifact).
- Missing index file → `CommandError` with message pointing the user at `python manage.py build_docs_index`.
- Malformed JSON → `CommandError` with the underlying parse error.
- Source files listed in the index but missing/unreadable/empty on disk → skipped with a `warn:` line on stdout.
- `--dry-run` reports counts and exits without writing.
- `--index PATH`, `--output PATH`, `--chunk-size N` flags for non-default invocations.

When `--index` is overridden, source files resolve relative to the index's parent of parent (the repo containing `docs/_index.json`), not `settings.BASE_DIR`. This makes the command directly testable in a tempdir without needing Django settings to point at a fake project root.

### 2. `core/tests/test_build_rag_corpus.py` — 6 tests

DB-free `SimpleTestCase`. No network, no LLM calls. Coverage:

- **`test_writes_jsonl_with_expected_keys`** — invoking the command writes a valid JSONL file; every row has exactly `{"file", "chunk_id", "text"}`; `docs/` prefix is stripped; root files keep their bare name.
- **`test_missing_index_raises_clear_error`** — missing `_index.json` raises `CommandError` whose message names `_index.json` and `build_docs_index`.
- **`test_corpus_consumable_by_core_rag_top_k`** — the only direct compatibility check: generate a corpus, point `core.rag.CORPUS_PATH` at it, run `top_k()`, assert it returns at least one hit with the expected keys and the matching file. This proves the producer's output is round-trip compatible with the (production-dormant) consumer.
- **`test_skips_missing_and_empty_sources_with_warning`** — sources listed in the index but absent or empty on disk are skipped, and a `warn:` line is written to stdout.
- **`test_dry_run_does_not_write`** — `--dry-run` reports counts without creating the output file.
- **`test_invalid_chunk_size_rejected`** — `--chunk-size=0` is rejected with `CommandError`.

### 3. `docs/topics/local-askdocs.md` — new topic doc

One-page reference for the local Ollama askdocs lane:

- Side-by-side comparison of production PA RAG (pgvector) vs. local askdocs (`.rag/corpus.jsonl`).
- File map (`core/rag.py`, `ask_with_docs.py`, `askdocs.py`, `build_rag_corpus.py`).
- Regen recipe and output shape.
- "When this lane is useful / when not to use it."
- Note that PR 2 will untrack `.rag/`.

### 4. Pointer updates

- `00-START-NEXT-SESSION.md` — `.rag/` paragraph updated to reflect that the producer landed (PR 1) and untrack is the next pending step (PR 2).
- `docs/handoffs/CURRENT.md` — re-pointed at this handoff.

---

## Verification

| Check | Result |
|---|---|
| `.venv/bin/python -m pytest core/tests/test_build_rag_corpus.py -v` | 6/6 pass |
| `.venv/bin/python -m pytest core/tests/test_build_rag_corpus.py core/tests/test_celery_sync_commands.py -v` | 8/8 pass (new + nearby management-command tests) |
| `python manage.py build_docs_index --json-only` | OK — wrote `docs/_index.json` (1,917 documents). Gitignored, not committed. |
| `python manage.py build_rag_corpus --dry-run` | OK — `18006 chunk(s) across 1917 file(s) (chunk_size=1200)` |
| `python manage.py build_rag_corpus` | OK — wrote `.rag/corpus.jsonl`. Inspected first row: shape matches existing on-disk convention. Tracked file restored via `git checkout` after verification (not modified in this PR). |
| `python scripts/verify_repo_guardrails.py --inventory-advisory` | PASS — same advisory state as `main` (4 DOC_ONLY + inventory drift, both pre-existing); no new findings. |
| Working tree at PR open | clean except for the new files |
| Runtime app code modified | 0 |
| Production RAG path (`core.rag_integration`, pgvector) modified | 0 |
| `stash@{0}` (Docker subnet override) | preserved |

---

## Files Changed

```
A  core/management/commands/build_rag_corpus.py     ~170 lines
A  core/tests/test_build_rag_corpus.py              ~155 lines
A  docs/topics/local-askdocs.md                     new topic doc
M  00-START-NEXT-SESSION.md                         .rag/ paragraph
M  docs/handoffs/CURRENT.md                         re-pointed at SESSION_1108
A  docs/handoffs/SESSION_1108_BUILD_RAG_CORPUS.md   this file
```

`.rag/corpus.jsonl` is **not** modified by this PR. The pre-commit hook's existing skip for `.rag/corpus.jsonl` is unchanged.

---

## Why this design (and what it deliberately doesn't do)

### Why ship the producer before the untrack?

If the file were untracked first, `python manage.py askdocs <q>` would silently degrade (returns `No matching /docs context found.` via the empty-list fallback in `top_k`), with no recovery path inside the repo. Producer-first means the untrack is a non-breaking transition — anyone running `askdocs` after the untrack just runs `build_rag_corpus` once.

### Why match the existing on-disk shape exactly?

So the output of `build_rag_corpus` is a drop-in replacement for the tracked `.rag/corpus.jsonl`. After the untrack PR, regenerating the corpus locally produces a file that behaves identically to the one that used to be in git. Any divergence (different chunking, different path format, different chunk_id base) would change `top_k()` results in subtle ways.

### Why not also untrack `.rag/embedding_refs.txt` here?

Same scope-discipline reason: PR 1 is producer-only. `embedding_refs.txt` has zero in-repo consumers, so untracking it is uncontroversial — but it can ride with PR 2 (the untrack PR) where it belongs logically.

### Why no DB / no OpenAI in the tests?

The producer reads `_index.json` and chunks file bodies. It doesn't generate embeddings, doesn't talk to OpenAI, and doesn't touch the database. Adding fake DB or API mocks just to follow a pattern would add weight without raising confidence.

---

## Runtime Behavior Changes

**None.** New management command + new tests + new topic doc + pointer updates. No production code path touched.

---

## Next Session Picks Up With

The follow-up PR for the same Option B plan, plus the queue from PR #2058:

1. **PR 2 — untrack `.rag/`.** `git rm --cached .rag/corpus.jsonl .rag/embedding_refs.txt`, add `.rag/` to `.gitignore`, drop the now-unneeded `.rag/corpus.jsonl` skip from `.githooks/pre-commit`, update handoffs/00-START. Now safe because PR 1 (this) shipped the regenerator.
2. **`PLATFORM_INVENTORY.md` regen** — DB-gated; needs Chris's local DB up. Will clear the only outstanding `verify_repo_guardrails` warning.
3. **`BACKEND_INVENTORY.md` hygiene reassessment** — pure cosmetic now that context-kit upstream picks the right anchor via `verify.yaml`. No urgency.
4. **Branch cleanup** — older `chore/docs-index-*` and `chore/cleanup-*` branches still in the local list; separate hygiene pass.
5. **CI inventory regen (long term)** — would let us drop `--inventory-advisory` from the workflow. Needs Postgres service container + DB credentials in CI; out of scope for now.

---

## Rigby / PA / AI Context

- **Conversation ID:** none for this tooling-only session.
- **State at end of session:** branch `chore/add-rag-corpus-builder`, ready for review. Working tree clean except for the new files in this PR. `.rag/corpus.jsonl` left untouched (regen during verification reverted via `git checkout`).
- **How to resume:** `PA_API_URL=http://localhost:8000 PA_API_TOKEN=<local-donkeyking-token> .venv/bin/python tools/pa_chat.py "session 1108 follow-up" --conversation <id>`

---

## Cross-References

- Previous handoff: [`SESSION_1107_CI_GUARDRAIL_WIRING.md`](SESSION_1107_CI_GUARDRAIL_WIRING.md)
- Original investigation: [`SESSION_1102_PHASE2B_TAXONOMY_AUTOGEN.md`](SESSION_1102_PHASE2B_TAXONOMY_AUTOGEN.md) (deferred-queue entry, dormancy proof)
- Topic doc: [`docs/topics/local-askdocs.md`](../topics/local-askdocs.md)
- Cleanup plan: [`docs/audit/CLEANUP_PLAN.md`](../audit/CLEANUP_PLAN.md)
- Canonical truth docs: [`docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md), [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md)

---

*Written at end of session 2026-05-08. Do not edit after the next session begins. If the next session finds a bug in this handoff's reasoning, add a note at the bottom rather than rewriting — the original reasoning is history.*
