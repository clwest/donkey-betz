"""Tests for `python manage.py build_rag_corpus`.

These tests are DB-free and make no network or LLM calls. They exercise the
local-only Ollama askdocs lane only — production PA/Rigby retrieval (pgvector
via core.rag_integration) is not touched.
"""

from __future__ import annotations

import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase

from core.rag import top_k


def _write(p: Path, body: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")


def _write_index(index_path: Path, paths: list[str]) -> None:
    payload = {"documents": [{"path": p} for p in paths]}
    _write(index_path, json.dumps(payload))


class BuildRagCorpusTests(SimpleTestCase):
    def test_writes_jsonl_with_expected_keys(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _write(base / "docs" / "alpha.md", "alpha body content")
            _write(base / "docs" / "nested" / "beta.md", "beta body content")
            _write(base / "CLAUDE.md", "root body content")
            _write_index(
                base / "docs" / "_index.json",
                ["docs/alpha.md", "docs/nested/beta.md", "CLAUDE.md"],
            )
            output = base / ".rag" / "corpus.jsonl"

            out = io.StringIO()
            call_command(
                "build_rag_corpus",
                f"--index={base / 'docs' / '_index.json'}",
                f"--output={output}",
                "--chunk-size=64",
                stdout=out,
            )

            self.assertTrue(output.is_file())
            rows = [json.loads(l) for l in output.read_text().splitlines() if l.strip()]
            self.assertGreaterEqual(len(rows), 3)
            for row in rows:
                self.assertEqual(set(row.keys()), {"file", "chunk_id", "text"})
                self.assertIsInstance(row["file"], str)
                self.assertIsInstance(row["chunk_id"], int)
                self.assertGreaterEqual(row["chunk_id"], 1)
                self.assertIsInstance(row["text"], str)

            files_seen = {r["file"] for r in rows}
            # docs/ prefix is stripped; root files keep their bare name
            self.assertIn("alpha.md", files_seen)
            self.assertIn("nested/beta.md", files_seen)
            self.assertIn("CLAUDE.md", files_seen)
            self.assertNotIn("docs/alpha.md", files_seen)

    def test_missing_index_raises_clear_error(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            missing = base / "docs" / "_index.json"
            with self.assertRaises(CommandError) as cm:
                call_command(
                    "build_rag_corpus",
                    f"--index={missing}",
                    f"--output={base / '.rag' / 'corpus.jsonl'}",
                )
            msg = str(cm.exception)
            self.assertIn("_index.json", msg)
            self.assertIn("build_docs_index", msg)

    def test_corpus_consumable_by_core_rag_top_k(self):
        """Generated corpus must be readable by `core.rag.top_k()` — the only
        production-dormant consumer of `.rag/corpus.jsonl`."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            doc_body = (
                "Donkey Betz uses pgvector for embeddings and similarity search. "
                "The learning loop creates UserEmbedding rows on successful applications."
            )
            _write(base / "docs" / "audits" / "learning-loop-discovery.md", doc_body)
            _write_index(
                base / "docs" / "_index.json",
                ["docs/audits/learning-loop-discovery.md"],
            )
            output = base / ".rag" / "corpus.jsonl"
            call_command(
                "build_rag_corpus",
                f"--index={base / 'docs' / '_index.json'}",
                f"--output={output}",
                "--chunk-size=200",
                stdout=io.StringIO(),
            )

            from unittest.mock import patch
            import core.rag as core_rag
            with patch.object(core_rag, "CORPUS_PATH", output):
                hits = top_k("learning loop UserEmbedding pgvector", k=3)

            self.assertGreaterEqual(len(hits), 1)
            top = hits[0]
            self.assertIn("file", top)
            self.assertIn("chunk_id", top)
            self.assertIn("text", top)
            self.assertIn("learning-loop-discovery.md", top["file"])

    def test_skips_missing_and_empty_sources_with_warning(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _write(base / "docs" / "real.md", "real content here")
            _write(base / "docs" / "empty.md", "")
            # ghost.md is in the index but not on disk
            _write_index(
                base / "docs" / "_index.json",
                ["docs/real.md", "docs/empty.md", "docs/ghost.md"],
            )
            output = base / ".rag" / "corpus.jsonl"

            out = io.StringIO()
            call_command(
                "build_rag_corpus",
                f"--index={base / 'docs' / '_index.json'}",
                f"--output={output}",
                stdout=out,
            )

            stdout_text = out.getvalue()
            self.assertIn("missing source", stdout_text)
            self.assertIn("empty source", stdout_text)

            rows = [json.loads(l) for l in output.read_text().splitlines() if l.strip()]
            files_seen = {r["file"] for r in rows}
            self.assertEqual(files_seen, {"real.md"})

    def test_dry_run_does_not_write(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _write(base / "docs" / "doc.md", "body")
            _write_index(base / "docs" / "_index.json", ["docs/doc.md"])
            output = base / ".rag" / "corpus.jsonl"

            call_command(
                "build_rag_corpus",
                f"--index={base / 'docs' / '_index.json'}",
                f"--output={output}",
                "--dry-run",
                stdout=io.StringIO(),
            )

            self.assertFalse(output.exists())

    def test_invalid_chunk_size_rejected(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            _write(base / "docs" / "doc.md", "body")
            _write_index(base / "docs" / "_index.json", ["docs/doc.md"])
            with self.assertRaises(CommandError):
                call_command(
                    "build_rag_corpus",
                    f"--index={base / 'docs' / '_index.json'}",
                    f"--output={base / '.rag' / 'corpus.jsonl'}",
                    "--chunk-size=0",
                )
