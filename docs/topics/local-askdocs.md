---
title: "Local-only Ollama askdocs lane"
status: active
session: 1108
---

# Local-only Ollama askdocs lane

A small, **local-only** Q&A pipeline for the `docs/` corpus, backed by Ollama.
This is **not** the production RAG path. It is a developer convenience that
runs entirely against a local model with no network calls to OpenAI/Anthropic.

## What this is and isn't

| | Production PA / Rigby retrieval | Local Ollama askdocs |
|---|---|---|
| Module | `core.rag_integration` | `core.rag` |
| Storage | PostgreSQL `unified_embeddings` table (pgvector) | `.rag/corpus.jsonl` (flat file) |
| Embeddings | `EmbeddingService` (OpenAI `text-embedding-3-small`, Redis-cached) | None — keyword scoring only |
| Inference | Whatever provider the PA is configured to use | Local Ollama (`http://127.0.0.1:11434`) |
| Source ingest | `python manage.py sync_docs_index_to_documents [--embed]` → `Document` model | `python manage.py build_rag_corpus` → `.rag/corpus.jsonl` |
| Used by | PA enrichment, agent retrieval, knowledge views, ~13 production files | `python manage.py askdocs <q>` and `core/ask_with_docs.py` only |
| Touches OpenAI | yes | no |

The two paths are **completely independent**. `core.rag` and
`core.rag_integration` are distinct modules with non-overlapping consumers.
Changes to the local lane have no effect on production retrieval.

## Files involved

- `core/rag.py` — `top_k()` and `build_docs_context()`. Reads
  `.rag/corpus.jsonl` from the working directory; gracefully returns an empty
  list if the file is missing.
- `core/ask_with_docs.py` — wraps `build_docs_context` + a local Ollama chat
  client (`core.llm_ollama`).
- `core/management/commands/askdocs.py` — Django management command:
  `python manage.py askdocs "<question>"`. Uses Ollama at
  `http://127.0.0.1:11434/v1/chat/completions` with model
  `qwen2.5:14b-instruct` by default.
- `core/management/commands/build_rag_corpus.py` — regenerator (this PR).

## Regenerating the corpus

```bash
# 1) (Re)build the docs index — produces docs/_index.json (gitignored).
python manage.py build_docs_index --json-only

# 2) (Re)build the local RAG corpus.
python manage.py build_rag_corpus
# Optional flags:
#   --index PATH        alternative _index.json
#   --output PATH       alternative output file (default: .rag/corpus.jsonl)
#   --chunk-size N      override chunk size (default: 1200 chars)
#   --dry-run           report counts without writing
```

Output shape (one JSON object per line):

```json
{"file": "audits/learning-loop-discovery.md", "chunk_id": 1, "text": "..."}
```

- `file` is relative to `docs/` for files under `docs/`, or the bare name for
  root-level docs (e.g., `CLAUDE.md`).
- `chunk_id` is 1-indexed.
- Chunks are fixed-size character windows with no overlap, matching the
  on-disk artifact convention.

## Asking a question

```bash
# Requires a local Ollama daemon listening on 127.0.0.1:11434.
python manage.py askdocs "what does the learning loop do?"
```

If `.rag/corpus.jsonl` is absent or empty, the command will return
`No matching /docs context found.` Regenerate the corpus and try again.

## When this lane is useful

- Offline doc Q&A when the OpenAI quota is exhausted.
- Quick local sanity checks against the doc corpus without round-tripping
  through the PA / production path.
- Iterating on local Ollama models (`LLM_MODEL`, `EMBED_MODEL` env vars; see
  `ragtest.py` for a related local-only RAG test).

## When **not** to use this

- Anything user-facing.
- Anything an agent will consume.
- Any retrieval from inside production code.

For all of those, use `core.rag_integration` and the pgvector pipeline.

## Tracking note

`.rag/corpus.jsonl` is currently tracked in git (~6.5 MB). Now that there is
an in-repo producer, a follow-up PR can untrack it and add `.rag/` to
`.gitignore`. That step is intentionally **not** included in this PR — the
producer ships first so the untrack is non-breaking.
