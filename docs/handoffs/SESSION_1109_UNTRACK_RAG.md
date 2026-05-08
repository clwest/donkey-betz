---
title: "Session 1109 — untrack .rag/ artifacts (Option B, PR 2)"
date: 2026-05-08
status: active
session: 1109
previous_handoff: SESSION_1108_BUILD_RAG_CORPUS.md
---

# Session 1109 — untrack .rag/ artifacts (Option B, PR 2)

## TL;DR

- **Shipped:** removed `.rag/corpus.jsonl` (~6.5 MB) and `.rag/embedding_refs.txt` (~5.6 KB) from the git index. Added `.rag/` to `.gitignore`. Removed the now-redundant `.rag/corpus.jsonl` skip from `.githooks/pre-commit`.
- **Why:** Session 1108 (PR 1) shipped the regenerator (`python manage.py build_rag_corpus`). With a producer in place, the tracked artifact becomes pure clone-size tax. After this PR, `.rag/corpus.jsonl` is the largest tracked file no more.
- **No production behavior changes.** Production PA / Rigby RAG goes through `core.rag_integration` → `unified_embeddings` (PostgreSQL + pgvector). `.rag/` is and was a local-only Ollama askdocs artifact.
- **Local working copies preserved.** `git rm --cached` removed the files from the index only. The on-disk copies remain available; running `python manage.py build_rag_corpus` refreshes them.
- **Carryover:** `stash@{0}` (Docker subnet override) still preserved.

---

## What Shipped

### 1. Untracked the two `.rag/` artifacts

```
git rm --cached .rag/corpus.jsonl
git rm --cached .rag/embedding_refs.txt
```

The on-disk files at `.rag/corpus.jsonl` and `.rag/embedding_refs.txt` were not deleted. Anyone who had a working copy still has a working copy. Anyone cloning fresh after this PR will get an empty `.rag/` and can regenerate via:

```bash
python manage.py build_docs_index --json-only
python manage.py build_rag_corpus
```

### 2. `.gitignore` — added `.rag/`

```diff
 # Documentation
 docs/_build/
 docs/_index.json
+
+# Local-only Ollama askdocs corpus (regenerable via `python manage.py build_rag_corpus`).
+# Production PA RAG uses pgvector via core.rag_integration and is unaffected.
+.rag/
```

Placed adjacent to `docs/_index.json` because the corpus is content-derived from that index by the same kind of management command.

### 3. `.githooks/pre-commit` — fixed deletion-scan + removed redundant skip

The hook used to skip `.rag/corpus.jsonl` from secret scanning to avoid false positives in the chunked doc text. The skip was needed for two reasons: (a) committing the tracked file ever updating it, and (b) **the delete-the-file commit** (i.e. *this* commit) — `git rm --cached` leaves the on-disk copy in place, and the hook would scan it and trip on the same false positives.

Removing the skip line without fixing the deletion-scan semantics would have blocked this very commit. The proper structural fix is one line: scan added/modified files, not deletions.

```diff
-staged_files=$(git diff --cached --name-only)
+staged_files=$(git diff --cached --name-only --diff-filter=d)
```

`--diff-filter=d` (lowercase) excludes deletions. The on-disk content of a delete-only stage is by definition material being removed from the index; scanning it is wrong both semantically (we're not adding it) and practically (false positives like the `.rag/corpus.jsonl` chunked tokens).

With that fix in place, the special-case skip line really is dead and is removed:

```diff
-        # Skip .rag/corpus.jsonl — auto-generated RAG embedding corpus, chunked docs, high false-positive rate
         case "$file" in
             ...
             .githooks/*|.git/hooks/*)
                 continue ;;
-            .rag/corpus.jsonl)
-                continue ;;
         esac
```

### 4. Documentation updates

- **`docs/topics/local-askdocs.md`** — "Tracking note" section flipped from "currently tracked" to "untracked and gitignored as of Session 1109" with the regen recipe surfaced.
- **`00-START-NEXT-SESSION.md`** — `.rag/` paragraph rewritten for the post-untrack reality. Pointer block now links to this handoff and to SESSION_1108 as previous.
- **`docs/handoffs/CURRENT.md`** — re-pointed at SESSION_1109.

---

## Verification

| Check | Result |
|---|---|
| `git ls-files .rag/corpus.jsonl .rag/embedding_refs.txt` | empty — both files no longer in the index |
| Local `.rag/corpus.jsonl`, `.rag/embedding_refs.txt` exist on disk before regen | yes (untrack preserved disk copies) |
| `python manage.py build_rag_corpus` after untrack | regenerates `.rag/corpus.jsonl` as ignored output; `git status` clean afterward |
| `git check-ignore .rag/corpus.jsonl` | reports `.rag/` (ignored) |
| `core/rag.py:top_k()` graceful-empty fallback | unchanged — still returns `[]` if the corpus is missing |
| `python -m pytest core/tests/test_build_rag_corpus.py` | 6/6 pass |
| `python scripts/verify_repo_guardrails.py --inventory-advisory` | PASS — same advisory state as before; no new findings |
| Pre-commit hook | passed on commit (no `.rag/corpus.jsonl` skip needed) |
| Working tree at PR open | clean except for the changes in this PR |
| Production RAG path (`core.rag_integration`, pgvector) | 0 lines touched |
| `stash@{0}` (Docker subnet override) | preserved |

---

## Files Changed

```
D  .rag/corpus.jsonl                            (untracked; on disk preserved)
D  .rag/embedding_refs.txt                      (untracked; on disk preserved)
M  .gitignore                                   +5 lines (`.rag/` block)
M  .githooks/pre-commit                         deletion-scan fix + skip removal
M  docs/topics/local-askdocs.md                 Tracking note rewritten
M  00-START-NEXT-SESSION.md                     `.rag/` paragraph + pointers
M  docs/handoffs/CURRENT.md                     re-pointed at SESSION_1109
A  docs/handoffs/SESSION_1109_UNTRACK_RAG.md    this file
```

No backend, frontend, agent, or runtime code modified.

---

## Why this design (and what it deliberately doesn't do)

### Why now and not in PR 1?

Producer-first kept the transition non-breaking. Untracking before the regenerator existed would have left `python manage.py askdocs` permanently degraded for anyone running on a fresh clone. With PR 1 merged on `main`, this PR is a clean "remove the tracked copy, point users at the regenerator" change.

### Why use `git rm --cached` rather than `git rm`?

`git rm` would also delete the local working copies — needless friction for anyone with the file already present and using the askdocs lane today. `--cached` removes from the index only; on-disk files persist until manually deleted. Combined with the `.gitignore` add, future commits will never re-track them.

### Why is the pre-commit hook change here and not its own PR?

This PR's own commit *is* the trigger: `git rm --cached` stages a deletion of `.rag/corpus.jsonl`, and the hook would scan the (still-on-disk) file and trip on the same false positives the skip line was protecting against. Two ways to fix:

- **Keep the skip line**, ship the untrack, and remove the line in a follow-up PR. Two commits, one round-trip of dead-code-by-design.
- **Fix the deletion-scan semantics now** (`--diff-filter=d`) and remove the skip line in the same PR. Cleaner: the skip really is dead afterwards because deletions never reach the scan loop.

Took the second path. The hook change is structural and one-line; folding it into this PR is appropriate scope rather than expansion.

### Why not rebuild and commit the regenerated corpus once for the snapshot?

Same reasoning that motivated the untrack: a tracked corpus is dead weight when a producer exists. Anyone who wants a snapshot can run `build_rag_corpus` locally; CI doesn't need it; production doesn't read it.

---

## Runtime Behavior Changes

**None.** Repository hygiene only.

- Production PA / Rigby retrieval (pgvector) — unchanged.
- Local Ollama askdocs lane — unchanged in semantics; the only practical difference is that on a fresh clone you must run `python manage.py build_rag_corpus` once before `python manage.py askdocs <q>` returns useful results.
- Pre-commit hook secret scan — unchanged scope (still scans every staged file except the existing skip categories), one structurally-dead skip line removed.

---

## Next Session Picks Up With

The remaining queue from PR #2058 / SESSION_1107:

1. **`PLATFORM_INVENTORY.md` regen** — DB-gated; needs Chris's local DB up. Will clear the only outstanding `verify_repo_guardrails` warning.
2. **`BACKEND_INVENTORY.md` hygiene reassessment** — pure cosmetic now that context-kit upstream picks the right anchor via `verify.yaml`. No urgency.
3. **Branch cleanup** — older `chore/docs-index-*` and `chore/cleanup-*` branches still in the local list; separate hygiene pass.
4. **CI inventory regen (long term)** — would let us drop `--inventory-advisory` from the workflow. Needs Postgres service container + DB credentials in CI; out of scope for now.

---

## Rigby / PA / AI Context

- **Conversation ID:** none for this tooling-only session.
- **State at end of session:** branch `chore/untrack-rag-artifacts`, ready for review. Working tree clean. Local `.rag/corpus.jsonl` and `.rag/embedding_refs.txt` preserved on disk; both ignored by `.gitignore`.
- **How to resume:** `PA_API_URL=http://localhost:8000 PA_API_TOKEN=<local-donkeyking-token> .venv/bin/python tools/pa_chat.py "session 1109 follow-up" --conversation <id>`

---

## Cross-References

- Previous handoff (PR 1): [`SESSION_1108_BUILD_RAG_CORPUS.md`](SESSION_1108_BUILD_RAG_CORPUS.md)
- Original investigation: [`SESSION_1102_PHASE2B_TAXONOMY_AUTOGEN.md`](SESSION_1102_PHASE2B_TAXONOMY_AUTOGEN.md)
- Topic doc: [`docs/topics/local-askdocs.md`](../topics/local-askdocs.md)
- Cleanup plan: [`docs/audit/CLEANUP_PLAN.md`](../audit/CLEANUP_PLAN.md)
- Canonical truth docs: [`docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md), [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md)

---

*Written at end of session 2026-05-08. Do not edit after the next session begins. If the next session finds a bug in this handoff's reasoning, add a note at the bottom rather than rewriting — the original reasoning is history.*
