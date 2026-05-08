"""
Build the local-only RAG corpus consumed by `python manage.py askdocs`.

This command regenerates `.rag/corpus.jsonl` by walking every document listed in
`docs/_index.json` (produced by `build_docs_index`) and emitting fixed-size
chunks in the JSONL shape `core/rag.py:top_k()` reads:

    {"file": "<path-relative-to-docs>", "chunk_id": <1-indexed>, "text": "<chunk>"}

Production note (do not change without coordination):
    The production PA / Rigby retrieval path uses `core.rag_integration` against
    the `unified_embeddings` PostgreSQL table (pgvector). It does NOT read
    `.rag/corpus.jsonl`. This command, `core/rag.py`, `core/ask_with_docs.py`,
    and `core/management/commands/askdocs.py` form a separate, local-only
    Ollama-backed Q&A lane.

Usage:
    python manage.py build_rag_corpus
    python manage.py build_rag_corpus --index PATH       # alt _index.json
    python manage.py build_rag_corpus --output PATH      # alt output corpus
    python manage.py build_rag_corpus --chunk-size 1500  # override (default 1200)
    python manage.py build_rag_corpus --dry-run          # report only

Run `python manage.py build_docs_index` first if `docs/_index.json` is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


DEFAULT_CHUNK_SIZE = 1200
DEFAULT_OUTPUT = Path(".rag/corpus.jsonl")
DEFAULT_INDEX = Path("docs/_index.json")


def _to_corpus_path(repo_relative_path: str) -> str:
    """Match the convention used by the existing corpus and `core/rag.py`
    PREF_FILE_BONUS regexes: paths are relative to docs/ when applicable."""
    if repo_relative_path.startswith("docs/"):
        return repo_relative_path[len("docs/"):]
    return repo_relative_path


def chunk_text(text: str, size: int) -> list[str]:
    if size <= 0:
        raise ValueError("chunk size must be positive")
    if not text:
        return []
    return [text[i:i + size] for i in range(0, len(text), size)]


def iter_corpus_rows(
    index_data: dict,
    base_dir: Path,
    chunk_size: int,
    on_warning=None,
):
    """Yield (file, chunk_id, text) triples in deterministic order."""
    documents = index_data.get("documents") or []
    for doc in documents:
        repo_rel = doc.get("path")
        if not repo_rel:
            continue
        abs_path = base_dir / repo_rel
        if not abs_path.is_file():
            if on_warning:
                on_warning(f"missing source: {repo_rel} (listed in index, not on disk)")
            continue
        try:
            body = abs_path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            if on_warning:
                on_warning(f"unreadable source: {repo_rel} ({exc})")
            continue
        if not body.strip():
            if on_warning:
                on_warning(f"empty source: {repo_rel}")
            continue
        corpus_file = _to_corpus_path(repo_rel)
        for i, chunk in enumerate(chunk_text(body, chunk_size), start=1):
            yield corpus_file, i, chunk


class Command(BaseCommand):
    help = (
        "Regenerate .rag/corpus.jsonl from docs/_index.json for the local-only "
        "askdocs / Ollama RAG lane. Production PA RAG uses pgvector and is "
        "untouched by this command."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--index",
            type=str,
            default=None,
            help=f"Path to docs index JSON (default: {DEFAULT_INDEX}).",
        )
        parser.add_argument(
            "--output",
            type=str,
            default=None,
            help=f"Output corpus path (default: {DEFAULT_OUTPUT}).",
        )
        parser.add_argument(
            "--chunk-size",
            type=int,
            default=DEFAULT_CHUNK_SIZE,
            help=f"Chunk size in characters (default: {DEFAULT_CHUNK_SIZE}).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report counts without writing the corpus file.",
        )

    def handle(self, *args, **options):
        settings_base = Path(getattr(settings, "BASE_DIR", Path.cwd()))
        if options.get("index"):
            index_path = Path(options["index"]).resolve()
            # When --index is overridden, resolve source files relative to the
            # index's parent of parent (the repo containing docs/_index.json).
            base_dir = index_path.parent.parent
        else:
            index_path = settings_base / DEFAULT_INDEX
            base_dir = settings_base
        output_path = Path(options["output"]) if options.get("output") else settings_base / DEFAULT_OUTPUT
        chunk_size = options["chunk_size"]
        dry_run = options["dry_run"]

        if chunk_size <= 0:
            raise CommandError("--chunk-size must be a positive integer")

        if not index_path.is_file():
            raise CommandError(
                f"docs index not found at {index_path}. "
                "Run `python manage.py build_docs_index` first."
            )

        try:
            with index_path.open("r", encoding="utf-8") as f:
                index_data = json.load(f)
        except json.JSONDecodeError as exc:
            raise CommandError(f"invalid JSON in {index_path}: {exc}") from exc

        warnings: list[str] = []
        rows = list(
            iter_corpus_rows(
                index_data,
                base_dir=base_dir,
                chunk_size=chunk_size,
                on_warning=warnings.append,
            )
        )

        for w in warnings:
            self.stdout.write(self.style.WARNING(f"warn: {w}"))

        files_seen = {file for file, _, _ in rows}
        self.stdout.write(
            f"{len(rows)} chunk(s) across {len(files_seen)} file(s) "
            f"(chunk_size={chunk_size})"
        )

        if dry_run:
            self.stdout.write(self.style.WARNING("dry-run: no file written"))
            return

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as out:
            for file, chunk_id, text in rows:
                out.write(json.dumps({"file": file, "chunk_id": chunk_id, "text": text}) + "\n")

        self.stdout.write(self.style.SUCCESS(f"wrote {output_path}"))
