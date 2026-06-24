"""Session 1230 P1 — COOAgent semantic title regression tests.

Locks the behavior of ``build_semantic_research_title(prefix='COO Analysis')``
at the COOAgent ``_save_to_deliverable`` callsite. Mirrors the P4 fix
shipped in Session 1229 PR #2573 for ``ResearchAgent`` and
``CustomerResearchAgent`` — same recursion class, different agent.

Background: Rigby's ``deliverable_tool action=duplicates`` surfaced a
6-row cluster (5 in the prior 7 days) with title
``"COO Analysis: You are running the daily COO operations diagnostic.
The threshold gate has trip"`` — the same ``f"COO Analysis: {task[:80]}"``
truncation pattern the ResearchAgent fix replaced.

This test file is intentionally narrow: it verifies that the helper, when
called with ``prefix='COO Analysis'``, applies all the same defenses
(prompt-body extraction, ``[User Context: …]`` strip, word-boundary
truncation, date suffix) to COO inputs.

Run::

    python manage.py test core.tests.test_coo_agent_semantic_title -v2
"""
from __future__ import annotations

from datetime import date

from django.test import SimpleTestCase

from core.services.deliverable_factory import (
    TEMPLATE_LEAK_TITLE_TOKENS,
    build_semantic_research_title,
)


T = date(2026, 6, 24)


class COOAgentSemanticTitleHappyPathTests(SimpleTestCase):
    """Clean COO tasks should pass through with the COO Analysis prefix."""

    def test_short_clean_task_passes_through(self):
        title = build_semantic_research_title(
            'Plan the next sprint', prefix='COO Analysis', today=T,
        )
        self.assertEqual(
            title,
            'COO Analysis: Plan the next sprint — 2026-06-24',
        )

    def test_assess_risks_task(self):
        title = build_semantic_research_title(
            'Assess risks for the Q3 release', prefix='COO Analysis', today=T,
        )
        self.assertEqual(
            title,
            'COO Analysis: Assess risks for the Q3 release — 2026-06-24',
        )

    def test_long_clean_task_truncates_at_word_boundary(self):
        task = (
            'Identify the top operational risks for the upcoming product '
            'launch covering release timing, infrastructure capacity, '
            'on-call rotation, and customer-support staffing'
        )
        title = build_semantic_research_title(
            task, prefix='COO Analysis', today=T,
        )
        self.assertTrue(title.startswith('COO Analysis: '))
        self.assertTrue(title.endswith(' — 2026-06-24'))
        body = title[len('COO Analysis: '):-len(' — 2026-06-24')]
        self.assertLessEqual(len(body), 80)
        self.assertFalse(body.endswith(' '))


class COOAgentSemanticTitlePromptBodyLeakTests(SimpleTestCase):
    """The audit cluster: COO daily diagnostic prompt must NOT leak."""

    def test_exact_audit_cluster_prompt_is_neutralized(self):
        """Regression for the exact leaked-cluster shape Rigby surfaced.

        Title was ``COO Analysis: You are running the daily COO operations
        diagnostic. The threshold gate has trip`` (6 rows). With the new
        ``You are running the daily`` / ``The threshold gate has tripped``
        markers in ``_PROMPT_BODY_MARKERS``, the helper recognizes this as
        a prompt body and falls through to step-4 default ``'brief'``.
        Neutral title, no leak. The same fall-through applies to CTOAgent
        and TrendAnalysisAgent sibling sites.
        """
        task = (
            'You are running the daily COO operations diagnostic. The '
            'threshold gate has tripped. Review recent metrics, identify '
            'the root cause, and recommend remediation steps.'
        )
        title = build_semantic_research_title(
            task, prefix='COO Analysis', today=T,
        )
        self.assertEqual(title, 'COO Analysis: brief — 2026-06-24')
        # The leaked phrasing must NOT appear in the title.
        self.assertNotIn('You are running', title)
        self.assertNotIn('threshold gate', title)
        # And none of the gate's leak tokens should appear either.
        title_lower = title.lower()
        for token in TEMPLATE_LEAK_TITLE_TOKENS:
            self.assertNotIn(token, title_lower)

    def test_cto_sibling_prompt_shape_is_neutralized(self):
        """CTOAgent shares the same diagnostic prompt template
        (``cto_daily.py``). The helper neutralizes its prompt body too —
        even though CTOAgent isn't wired to the helper in this PR, the
        marker addition shields callers that opt in later."""
        task = (
            'You are running the daily CTO platform reliability '
            'diagnostic. The threshold gate has tripped — produce a '
            'structured incident report.'
        )
        title = build_semantic_research_title(
            task, prefix='CTO Analysis', today=T,
        )
        self.assertEqual(title, 'CTO Analysis: brief — 2026-06-24')

    def test_trend_sibling_prompt_shape_is_neutralized(self):
        """TrendAnalysisAgent shares the same prompt template
        (``trend_analysis_daily.py``). Same marker coverage."""
        task = (
            'You are running the daily TrendAnalysis spider-intelligence '
            'anomaly diagnostic. The threshold gate has tripped — produce '
            'a structured anomaly report.'
        )
        title = build_semantic_research_title(
            task, prefix='Trend Analysis', today=T,
        )
        self.assertEqual(title, 'Trend Analysis: brief — 2026-06-24')

    def test_research_topic_section_is_extracted(self):
        """If a COO dispatch ever arrives with the Stage-1 dispatch shape
        (`## Research Topic` section), the helper extracts the topic and
        prefixes it with ``COO Analysis:`` rather than the research label."""
        task = (
            'Run the daily COO operations diagnostic.\n\n'
            'BINDING DIRECTIVE: Your output must directly advance THIS task.\n\n'
            '## Research Topic\n'
            'Q3 release risk assessment\n\n'
            '## Background Context\n'
            'Release scheduled 2026-07-15.\n'
        )
        title = build_semantic_research_title(
            task, prefix='COO Analysis', today=T,
        )
        self.assertEqual(
            title,
            'COO Analysis: Q3 release risk assessment — 2026-06-24',
        )


class COOAgentSemanticTitleEdgeCaseTests(SimpleTestCase):
    """Edge cases that mirror the ResearchAgent test surface."""

    def test_empty_task_uses_brief_default_with_coo_prefix(self):
        title = build_semantic_research_title(
            '', prefix='COO Analysis', today=T,
        )
        self.assertEqual(title, 'COO Analysis: brief — 2026-06-24')

    def test_user_context_tail_is_stripped(self):
        task = (
            'Plan the next sprint\n\n'
            "[User Context: Researching for: Chris; "
            "User's research interests: trading, AI, ops]"
        )
        title = build_semantic_research_title(
            task, prefix='COO Analysis', today=T,
        )
        self.assertEqual(
            title,
            'COO Analysis: Plan the next sprint — 2026-06-24',
        )

    def test_multiline_task_collapses_to_single_line(self):
        task = 'Plan\n\nthe\n\nnext\n\nsprint'
        title = build_semantic_research_title(
            task, prefix='COO Analysis', today=T,
        )
        self.assertEqual(
            title,
            'COO Analysis: Plan the next sprint — 2026-06-24',
        )
