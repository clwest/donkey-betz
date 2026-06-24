"""Session 1230 P1 sibling-wiring guard tests.

Source-level lint: locks the four sibling callsites that were rewired
from the leaked ``f"<Label>: {task[:N]}"`` pattern to
``build_semantic_research_title(task, prefix='<Label>')`` in
PRs #2580 (COOAgent) + this PR (CTO + TrendAnalysis + TrendBreakDetector).

Mirrors the Session 1228 PR-B (#2571) sweep-guard pattern: instead of
testing behavior at the agent layer (which would require booting full
agent infrastructure), we assert at the source level that the
truncation pattern does not return. Cheap, fast, catches reverts.

The behavior layer is already locked by:
- ``test_deliverable_factory_semantic_research_title.py`` — helper
  semantics (Session 1229 P4)
- ``test_coo_agent_semantic_title.py`` — COO + CTO + Trend prefix
  variants on the diagnostic-prompt shape (Session 1230 P1)

Run::

    python manage.py test core.tests.test_diagnostic_family_semantic_title_wiring -v2
"""
from __future__ import annotations

import re
from pathlib import Path

from django.test import SimpleTestCase


_REPO_ROOT = Path(__file__).resolve().parents[2]

# (file, expected_prefix) — every file in this list must import
# build_semantic_research_title and NOT contain the leak-pattern f-string.
_REWIRED_SITES = (
    ('core/agents/executive/coo_agent.py', 'COO Analysis'),
    ('core/agents/executive/cto_agent.py', 'CTO Analysis'),
    ('core/agents/analysis/trend_analysis_agent.py', 'Trend Analysis'),
    ('core/agents/narrative/trend_break_detector_agent.py', 'Trend Break Detection'),
)

# Matches `title=f"<Label>: {task[:N]}"` — the leaked truncation
# pattern Session 1229 P4 (#2573) and Session 1230 P1 (#2580 + this PR)
# replaced. Scoped to `title=` kwarg position so logging f-strings like
# `f"Received task: {task[:100]}"` (which appear in the COO/CTO/Trend
# `_thinking()` reasoning fields) are not flagged. Allows any prefix
# label, any truncation length.
_LEAK_PATTERN = re.compile(r'title\s*=\s*f["\'][A-Z][\w ]+:\s*\{task\[:\d+\]\}["\']')


class DiagnosticFamilyWiringTests(SimpleTestCase):
    """Each rewired site must import the helper and not regress to the
    f-string truncation pattern."""

    def test_each_site_imports_helper(self):
        for rel_path, _prefix in _REWIRED_SITES:
            with self.subTest(file=rel_path):
                src = (_REPO_ROOT / rel_path).read_text()
                self.assertIn(
                    'from core.services.deliverable_factory import build_semantic_research_title',
                    src,
                    msg=(
                        f'{rel_path} no longer imports build_semantic_research_title '
                        f'— sibling-wiring PR regressed.'
                    ),
                )

    def test_each_site_calls_helper_with_correct_prefix(self):
        for rel_path, prefix in _REWIRED_SITES:
            with self.subTest(file=rel_path, prefix=prefix):
                src = (_REPO_ROOT / rel_path).read_text()
                self.assertIn(
                    f"prefix='{prefix}'",
                    src,
                    msg=(
                        f'{rel_path} no longer calls '
                        f'build_semantic_research_title with prefix={prefix!r}.'
                    ),
                )

    def test_no_site_contains_leak_f_string_pattern(self):
        """The exact `f"<Label>: {task[:N]}"` truncation pattern that the
        ResearchAgent / COOAgent / CTOAgent / Trend* leaks all shared
        must not re-appear in these files."""
        for rel_path, _prefix in _REWIRED_SITES:
            with self.subTest(file=rel_path):
                src = (_REPO_ROOT / rel_path).read_text()
                matches = _LEAK_PATTERN.findall(src)
                self.assertFalse(
                    matches,
                    msg=(
                        f'{rel_path} contains the leak-pattern f-string '
                        f'(matches: {matches!r}). Replace with '
                        f"build_semantic_research_title(task, prefix='<Label>')."
                    ),
                )
