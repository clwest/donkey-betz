"""
Tests for claude_code_engineer context pre-injection (S2968 PR-2).

Verifies:
  1. Default context (context_files=None) injects the standard block:
     repo tree + CLAUDE.md excerpt + PLATFORM_INVENTORY.md excerpt +
     grounding instruction.
  2. Explicit list (context_files=['some/file.md']) injects only that
     file — skips defaults.
  3. Empty list (context_files=[]) explicitly opts out — returns ''
     and the engineer receives the raw task_description with no
     preamble.
"""
import os
import tempfile
import textwrap
from django.test import SimpleTestCase


class TestBuildRepoContext(SimpleTestCase):
    """Direct tests of the _build_repo_context helper."""

    def setUp(self):
        # Build a throwaway repo_root with CLAUDE.md + docs/PLATFORM_INVENTORY.md
        self._tempdir = tempfile.mkdtemp(prefix='pr2_ctx_test_')
        # Top-level files/dirs (tree section verification)
        for entry in ['core', 'docs', 'README.md', '.hidden_file', 'Makefile']:
            path = os.path.join(self._tempdir, entry)
            if entry.endswith('/') or entry in ('core', 'docs'):
                os.makedirs(path, exist_ok=True)
            else:
                open(path, 'w').close()
        # CLAUDE.md — write 500 lines so cap-at-300 truncation visible
        claude_lines = [f'CLAUDE-line-{i}' for i in range(1, 501)]
        with open(os.path.join(self._tempdir, 'CLAUDE.md'), 'w') as f:
            f.write('\n'.join(claude_lines))
        # docs/PLATFORM_INVENTORY.md — write 200 lines so cap-at-100 truncation visible
        os.makedirs(os.path.join(self._tempdir, 'docs'), exist_ok=True)
        inv_lines = [f'INV-line-{i}' for i in range(1, 201)]
        with open(os.path.join(self._tempdir, 'docs', 'PLATFORM_INVENTORY.md'), 'w') as f:
            f.write('\n'.join(inv_lines))
        # An extra file for the explicit-list test
        with open(os.path.join(self._tempdir, 'docs', 'topics.md'), 'w') as f:
            f.write('this is a topic doc')

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tempdir, ignore_errors=True)

    def test_default_injects_standard_block(self):
        """context_files=None → tree + CLAUDE.md excerpt + PLATFORM_INVENTORY excerpt + grounding line."""
        from core.services.claude_code_engineer import _build_repo_context

        context = _build_repo_context(self._tempdir, context_files=None)

        # Framing
        self.assertTrue(context.startswith('<repo_context>'))
        self.assertTrue(context.endswith('</repo_context>'))
        self.assertIn('Use this context as ground truth', context)

        # Repo tree section — visible entries, no dotfiles
        self.assertIn('## Repo tree', context)
        self.assertIn('core/', context)
        self.assertIn('docs/', context)
        self.assertIn('README.md', context)
        self.assertIn('Makefile', context)
        self.assertNotIn('.hidden_file', context)

        # CLAUDE.md excerpt — first 300 lines only
        self.assertIn('CLAUDE.md excerpt', context)
        self.assertIn('CLAUDE-line-1', context)
        self.assertIn('CLAUDE-line-300', context)
        self.assertNotIn('CLAUDE-line-301', context)
        self.assertIn('truncated at 300 lines', context)

        # PLATFORM_INVENTORY excerpt — first 100 lines only
        self.assertIn('PLATFORM_INVENTORY.md excerpt', context)
        self.assertIn('INV-line-1', context)
        self.assertIn('INV-line-100', context)
        self.assertNotIn('INV-line-101', context)
        self.assertIn('truncated at 100 lines', context)

    def test_explicit_list_injects_only_those_files_skips_defaults(self):
        """context_files=[...] → only requested files, no CLAUDE.md / no PLATFORM_INVENTORY."""
        from core.services.claude_code_engineer import _build_repo_context

        context = _build_repo_context(self._tempdir, context_files=['docs/topics.md'])

        self.assertTrue(context.startswith('<repo_context>'))
        self.assertIn('## Explicit Context Files', context)
        self.assertIn('docs/topics.md', context)
        self.assertIn('this is a topic doc', context)

        # Defaults MUST be skipped when caller passes an explicit list
        self.assertNotIn('CLAUDE.md excerpt', context)
        self.assertNotIn('PLATFORM_INVENTORY.md excerpt', context)
        self.assertNotIn('## Repo tree', context)

    def test_empty_list_returns_opt_out(self):
        """context_files=[] → empty string, engineer receives raw task."""
        from core.services.claude_code_engineer import _build_repo_context

        context = _build_repo_context(self._tempdir, context_files=[])

        self.assertEqual(context, '')

    def test_missing_file_in_explicit_list_reports_gracefully(self):
        """Non-existent file in context_files → '(file not found)' marker, no exception."""
        from core.services.claude_code_engineer import _build_repo_context

        context = _build_repo_context(self._tempdir, context_files=['does/not/exist.md'])

        self.assertIn('does/not/exist.md', context)
        self.assertIn('(file not found', context)
