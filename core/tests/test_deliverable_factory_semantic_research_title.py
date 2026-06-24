"""Session 1229 P4 — semantic research title builder tests.

Locks behavior of ``build_semantic_research_title``, which is the upstream
side of the ``TEMPLATE_LEAK_TITLE_TOKENS`` reactive gate. The gate (tested
in ``test_deliverable_factory_template_leak_gate.py``) blocks rows whose
titles contain prompt-body markers; this helper stops the leak at the
source so the gate stays a safety net rather than the primary defense.

Companion to:
  - ``test_deliverable_factory_template_leak_gate.py`` (the gate)
  - ``test_deliverable_factory_gated_exception.py``    (the exception)

Run::

    python manage.py test core.tests.test_deliverable_factory_semantic_research_title -v2
"""
from __future__ import annotations

from datetime import date

from django.test import SimpleTestCase

from core.services.deliverable_factory import (
    TEMPLATE_LEAK_TITLE_TOKENS,
    build_semantic_research_title,
)


# Frozen "today" used across tests so the date suffix is deterministic.
T = date(2026, 6, 24)


class SemanticResearchTitleHappyPathTests(SimpleTestCase):
    """Clean queries should pass through with the expected prefix + suffix."""

    def test_short_clean_query_passes_through(self):
        title = build_semantic_research_title(
            'What does decentralization mean for HFT?', today=T,
        )
        self.assertEqual(
            title,
            'Research: What does decentralization mean for HFT? — 2026-06-24',
        )

    def test_custom_prefix_for_customer_research(self):
        title = build_semantic_research_title(
            'Why do users abandon onboarding at step 3?',
            prefix='Customer Research',
            today=T,
        )
        self.assertEqual(
            title,
            'Customer Research: Why do users abandon onboarding at step 3? — 2026-06-24',
        )

    def test_long_clean_query_truncates_at_word_boundary(self):
        query = (
            'How do large language model providers price function-calling '
            'with reasoning models versus completion-only models in 2026 '
            'and what is the cost per million tokens'
        )
        title = build_semantic_research_title(query, today=T)
        self.assertTrue(title.startswith('Research: '))
        self.assertTrue(title.endswith(' — 2026-06-24'))
        # Topic body bounded by max_topic_chars (default 80).
        body = title[len('Research: '):-len(' — 2026-06-24')]
        self.assertLessEqual(len(body), 80)
        # Truncation lands on a word boundary, not mid-word.
        self.assertNotIn('  ', body)
        self.assertFalse(body.endswith(' '))


class SemanticResearchTitlePromptBodyLeakTests(SimpleTestCase):
    """The whole point: prompt bodies in `task` must NOT leak into titles."""

    def test_research_topic_section_is_extracted(self):
        """Current `tasks_initiatives.py:2735` Stage-1 prompt shape."""
        task = (
            'Research this topic to advance the initiative.\n\n'
            'BINDING DIRECTIVE: Your output must directly advance THIS initiative.\n\n'
            '## Research Topic\n'
            'Low-latency arbitrage on Solana\n\n'
            '## Background Context\n'
            'No description provided\n\n'
            '## Instructions\n'
            '1. Use web_search to find current external information about this topic.\n'
        )
        title = build_semantic_research_title(task, today=T)
        self.assertEqual(
            title,
            'Research: Low-latency arbitrage on Solana — 2026-06-24',
        )

    def test_old_external_sources_prompt_falls_back_to_topics(self):
        """Older Session-923 prompt shape — no `## Research Topic` section
        but has `EXTERNAL sources` + `DO NOT use query_internal_data` body
        that produced the 32-row audit cluster."""
        task = (
            'Research this topic using EXTERNAL sources (web_search, spider_query).\n'
            'DO NOT use query_internal_data - this is NOT about internal system analysis.\n'
        )
        title = build_semantic_research_title(
            task,
            topics_detected=['decentralized HFT', 'low-latency networks', 'arbitrage'],
            today=T,
        )
        self.assertEqual(
            title,
            'Research: decentralized HFT · low-latency networks · arbitrage — 2026-06-24',
        )

    def test_old_prompt_with_no_topics_uses_default(self):
        """Last-resort fallback — topics empty AND prompt body unparseable."""
        task = (
            'Research this topic using EXTERNAL sources (web_search, spider_query).\n'
            'DO NOT use query_internal_data\n'
        )
        title = build_semantic_research_title(task, today=T)
        self.assertEqual(title, 'Research: brief — 2026-06-24')

    def test_exact_audit_cluster_title_does_not_repeat(self):
        """Regression: the exact `task` body that the audit found persisting
        as title=`Research: This topic using EXTERNAL sources (web_search, ...
        spider_query).\\nDO NOT use query_internal_dat` must not be the
        title we emit. Verify both that the leaked phrasing is absent and
        that none of the gate's leak tokens appear in our output."""
        task = (
            'This topic using EXTERNAL sources (web_search, spider_query).\n'
            'DO NOT use query_internal_data - this is NOT about internal system analysis.\n\n'
            '## Research Topic\n'
            'AI agent orchestration patterns\n\n'
            '## Background Context\n'
            'How modern AI platforms wire multi-agent pipelines together\n'
        )
        title = build_semantic_research_title(task, today=T)
        self.assertEqual(
            title,
            'Research: AI agent orchestration patterns — 2026-06-24',
        )
        # None of the gate's leak tokens should appear in the emitted title.
        title_lower = title.lower()
        for token in TEMPLATE_LEAK_TITLE_TOKENS:
            self.assertNotIn(token, title_lower)

    def test_binding_directive_alone_falls_back_cleanly(self):
        task = (
            'Research this topic to advance the initiative.\n\n'
            'BINDING DIRECTIVE: Your output must directly advance THIS initiative.\n'
        )
        title = build_semantic_research_title(task, today=T)
        self.assertEqual(title, 'Research: brief — 2026-06-24')
        for token in TEMPLATE_LEAK_TITLE_TOKENS:
            self.assertNotIn(token, title.lower())


class SemanticResearchTitleEdgeCaseTests(SimpleTestCase):
    """Edge cases: empty input, augmentation tails, junk topics."""

    def test_empty_task_uses_brief_default(self):
        title = build_semantic_research_title('', today=T)
        self.assertEqual(title, 'Research: brief — 2026-06-24')

    def test_none_task_uses_brief_default(self):
        # Defensive: callers shouldn't pass None, but the helper must not
        # raise if they do.
        title = build_semantic_research_title(None, today=T)  # type: ignore[arg-type]
        self.assertEqual(title, 'Research: brief — 2026-06-24')

    def test_user_context_tail_is_stripped(self):
        """research_agent.py:780 augments `task` with `[User Context: ...]`
        when user profile is available. That suffix should NOT leak into
        the title."""
        task = (
            "What's the deal with high-frequency trading?\n\n"
            "[User Context: Researching for: Chris; "
            "User's research interests: trading, AI, ops]"
        )
        title = build_semantic_research_title(task, today=T)
        self.assertEqual(
            title,
            "Research: What's the deal with high-frequency trading? — 2026-06-24",
        )

    def test_empty_topics_are_skipped(self):
        task = (
            'Research this topic using EXTERNAL sources (web_search, spider_query).\n'
        )
        title = build_semantic_research_title(
            task,
            topics_detected=['', None, 'arbitrage', '', 'HFT'],  # type: ignore[list-item]
            today=T,
        )
        self.assertEqual(title, 'Research: arbitrage · HFT — 2026-06-24')

    def test_multiline_query_collapses_to_single_line(self):
        task = 'What is\n\nthis\n\nabout?'
        title = build_semantic_research_title(task, today=T)
        self.assertEqual(title, 'Research: What is this about? — 2026-06-24')

    def test_date_suffix_uses_today_when_not_injected(self):
        """Smoke: no `today` arg → suffix matches today's date format."""
        title = build_semantic_research_title('quick query')
        # Just check the shape; the exact date is wall-clock dependent.
        self.assertTrue(title.startswith('Research: quick query — '))
        suffix = title[len('Research: quick query — '):]
        self.assertRegex(suffix, r'^\d{4}-\d{2}-\d{2}$')
