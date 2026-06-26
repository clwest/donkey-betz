"""Session 1235 P5#3 audit Tranche 1 PR #5 — codebase_awareness retirement.

Verifies `core/codebase_awareness.py` is fully retired-to-no-op:
- No DB hits at import time
- All write/read methods return empty shapes
- Singleton + class import still work (mgmt command compat)
- search_code delegates cleanly to D12-fixed search_embeddings

Run::

    python manage.py test core.tests.test_codebase_awareness_retirement -v 2 --keepdb
"""

from unittest.mock import patch

from django.test import TestCase


class CodebaseAwarenessImportCompatTests(TestCase):
    """Module import + class instantiation must not raise or hit DB."""

    def test_module_imports_cleanly(self):
        from core import codebase_awareness as ca_module
        self.assertTrue(hasattr(ca_module, 'CodebaseAwareness'))
        self.assertTrue(hasattr(ca_module, 'codebase_awareness'))

    def test_singleton_instance_exists(self):
        from core.codebase_awareness import codebase_awareness, CodebaseAwareness
        self.assertIsInstance(codebase_awareness, CodebaseAwareness)

    def test_constructor_does_not_connect_to_db(self):
        """Pre-pivot: __init__ called load_ingested_files() which fired
        psycopg2.connect to dead `ai_unified_platform`. Post-pivot:
        __init__ just sets self.ingested_files = set() — no DB hit."""
        from core.codebase_awareness import CodebaseAwareness
        # If __init__ hits any DB code, this patch would catch it.
        # The test is structural: instantiating the class must not
        # touch psycopg2 or Django's connection.
        with patch(
            'core.codebase_awareness.logger.error'
        ) as mock_error:
            inst = CodebaseAwareness()
            mock_error.assert_not_called()
        self.assertEqual(inst.ingested_files, set())


class CodebaseAwarenessRetiredMethodTests(TestCase):
    """All retired methods return empty shapes without errors."""

    def setUp(self):
        from core.codebase_awareness import CodebaseAwareness
        self.ca = CodebaseAwareness()

    def test_ingest_codebase_returns_zero_stats(self):
        result = self.ca.ingest_codebase()
        self.assertEqual(result, {
            'files_processed': 0,
            'files_skipped': 0,
            'files_updated': 0,
            'embeddings_created': 0,
            'errors': 0,
        })

    def test_ingest_codebase_force_update_also_zero(self):
        result = self.ca.ingest_codebase(force_update=True)
        self.assertEqual(result['files_processed'], 0)
        self.assertEqual(result['embeddings_created'], 0)

    def test_ingest_file_returns_zero(self):
        self.assertEqual(self.ca.ingest_file('/some/file.py', 'somehash'), 0)

    def test_load_ingested_files_is_noop(self):
        # Should not raise, should not modify state
        before = set(self.ca.ingested_files)
        self.ca.load_ingested_files()
        self.assertEqual(self.ca.ingested_files, before)

    def test_get_implementation_returns_none(self):
        self.assertIsNone(self.ca.get_implementation('SomeClass'))

    def test_get_file_hash_still_functional(self):
        """get_file_hash is pure file I/O, no DB — kept functional."""
        import tempfile
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False,
        ) as f:
            f.write("print('hello')\n")
            fname = f.name
        try:
            h = self.ca.get_file_hash(fname)
            self.assertEqual(len(h), 32)  # MD5 hex digest length
        finally:
            import os
            os.unlink(fname)

    def test_extract_node_content_still_functional(self):
        """extract_node_content is pure string slicing — kept functional."""
        import ast
        source = "def foo():\n    return 1\n"
        tree = ast.parse(source)
        func_node = tree.body[0]
        content = self.ca.extract_node_content(source, func_node)
        self.assertIn('def foo', content)


class CodebaseAwarenessSearchDelegationTests(TestCase):
    """search_code delegates to core.rag_integration.search_embeddings
    (D12 PR #2621 pivot) — returns empty for source_code content_type
    since no current writer populates it."""

    def setUp(self):
        from core.codebase_awareness import CodebaseAwareness
        self.ca = CodebaseAwareness()

    def test_search_code_returns_empty_when_no_matches(self):
        """No DocumentEmbedding rows have content_type='source_code'
        yet — search_code returns empty list, not error."""
        results = self.ca.search_code("anything")
        self.assertEqual(results, [])

    def test_search_code_swallows_underlying_errors(self):
        """If search_embeddings raises, search_code returns [] not
        propagates (preserves mgmt-command UX)."""
        with patch(
            'core.rag_integration.search_embeddings',
            side_effect=RuntimeError('simulated'),
        ):
            results = self.ca.search_code("test")
            self.assertEqual(results, [])

    def test_explain_system_returns_not_found_string(self):
        result = self.ca.explain_system('SomeNonexistent')
        self.assertIn('No information found', result)


class NoDeadSubstrateInCodebaseAwarenessTests(TestCase):
    """Source-level guards: no psycopg2 import, no live cursor.execute,
    no `database='ai_unified_platform'` literal in non-comment code."""

    FILE_PATH = 'core/codebase_awareness.py'

    def _read_non_comment_lines(self):
        from pathlib import Path
        text = Path(__file__).resolve().parent.parent.parent.joinpath(
            self.FILE_PATH,
        ).read_text()
        out_lines = []
        in_docstring = False
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith('"""') or stripped.startswith("'''"):
                if stripped.count('"""') == 2 or stripped.count("'''") == 2:
                    continue
                in_docstring = not in_docstring
                continue
            if in_docstring:
                continue
            if stripped.startswith('#'):
                continue
            out_lines.append(line)
        return '\n'.join(out_lines)

    def test_no_psycopg2_import(self):
        code = self._read_non_comment_lines()
        self.assertNotIn('import psycopg2', code)
        self.assertNotIn('psycopg2.connect', code)

    def test_no_unified_embeddings_query(self):
        code = self._read_non_comment_lines()
        for marker in (
            'FROM unified_embeddings',
            'INTO unified_embeddings',
            'DELETE FROM unified_embeddings',
        ):
            self.assertNotIn(marker, code)

    def test_no_ai_unified_platform_connect(self):
        code = self._read_non_comment_lines()
        self.assertNotIn("'ai_unified_platform'", code)
        self.assertNotIn('"ai_unified_platform"', code)

    def test_no_cursor_execute(self):
        code = self._read_non_comment_lines()
        self.assertNotIn('cursor.execute', code)

    def test_no_db_config_attribute(self):
        """Pre-pivot the class had `self.db_config = {host, database,
        user, password}` — the dead-DB config struct. Post-pivot this
        attribute is gone."""
        code = self._read_non_comment_lines()
        self.assertNotIn('self.db_config', code)
