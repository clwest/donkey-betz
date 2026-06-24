"""Session 1224 P1 — Deliverables Hygiene initiative d8d6c0b2-… tests.

Locks the new factory gates:
  - gate_4_template_leak  — title contains BINDING DIRECTIVE / "research this
                            topic to advance the initiative" / similar prompt
                            leak tokens.
  - gate_5_no_relevance   — ResearchAgent with metadata.sources_count == 0
                            (no-evidence synthesis shouldn't land in main).

Companion to test_deliverable_factory_gated_exception.py.

Run::

    python manage.py test core.tests.test_deliverable_factory_template_leak_gate -v2
"""
from __future__ import annotations

from django.test import TestCase

from core.services.deliverable_factory import (
    DeliverableGatedError,
    _should_create_deliverable,
    create_deliverable,
)


class TemplateLeakGateTests(TestCase):
    """Gate 4: titles containing prompt-leak tokens are rejected."""

    def test_binding_directive_in_title_is_blocked(self):
        title = (
            'Research: This topic to advance the initiative.\n\n'
            'BINDING DIRECTIVE: Your output must directly advance'
        )
        should, reason, code = _should_create_deliverable(
            title=title,
            content='x' * 400,
            agent_name='ResearchAgent',
            metadata={'trigger_source': 'pa_tool', 'sources_count': 5},
        )
        self.assertFalse(should)
        self.assertEqual(code, 'gate_4_template_leak')
        self.assertIn('binding directive', reason.lower())

    def test_research_this_topic_phrase_is_blocked(self):
        title = (
            'Research this topic to advance the initiative — '
            'placeholder title because Stage 1 fallback misfired'
        )
        should, reason, code = _should_create_deliverable(
            title=title,
            content='x' * 400,
            agent_name='ResearchAgent',
            metadata={'trigger_source': 'pa_tool', 'sources_count': 5},
        )
        self.assertFalse(should)
        self.assertEqual(code, 'gate_4_template_leak')

    def test_external_sources_prompt_leak_is_blocked(self):
        """Session 1226 P3 — Rigby+Claude verifier-loop audit caught this
        in-the-wild leak pattern from ResearchAgent (32-row cluster, 28
        created in last 7 days at time of audit). Title is the exact
        101-char-truncated form as stored in core_deliverables (the
        truncation happens at core/agents/research_agent.py:1103 via
        title=f'Research: {task[:100]}').
        """
        # Exact title as stored in the duplicate cluster surfaced by
        # deliverable e2964e4a-… §3.1 row #1.
        title = (
            'Research: This topic using EXTERNAL sources (web_search, spider_query).\n'
            'DO NOT use query_internal_dat'
        )
        should, reason, code = _should_create_deliverable(
            title=title,
            content='x' * 400,
            agent_name='ResearchAgent',
            metadata={'trigger_source': 'pa_tool', 'sources_count': 5},
        )
        self.assertFalse(should)
        self.assertEqual(code, 'gate_4_template_leak')
        self.assertIn('this topic using external sources', reason.lower())

    def test_case_insensitive_match(self):
        title = 'BiNdInG dIrEcTiVe: leaked title casing'
        should, reason, code = _should_create_deliverable(
            title=title,
            content='x' * 400,
            agent_name='ResearchAgent',
            metadata={'trigger_source': 'pa_tool', 'sources_count': 3},
        )
        self.assertFalse(should)
        self.assertEqual(code, 'gate_4_template_leak')

    def test_legitimate_research_title_passes(self):
        """A normal research title isn't accidentally swept."""
        should, reason, code = _should_create_deliverable(
            title='Research: AI-driven workflow automation for SMB ops teams',
            content='x' * 400,
            agent_name='ResearchAgent',
            metadata={'trigger_source': 'pa_tool', 'sources_count': 5},
        )
        self.assertTrue(should)
        self.assertEqual(code, 'passed')

    def test_template_leak_in_content_only_passes(self):
        """Content can quote the directive — only title matters for this gate."""
        should, reason, code = _should_create_deliverable(
            title='Stage 1 research — workflow automation',
            content=(
                'The original prompt included a BINDING DIRECTIVE clause '
                'that we are quoting here for traceability. ' + 'x' * 400
            ),
            agent_name='ResearchAgent',
            metadata={'trigger_source': 'pa_tool', 'sources_count': 4},
        )
        self.assertTrue(should)
        self.assertEqual(code, 'passed')


class RelevanceGateTests(TestCase):
    """Gate 5: ResearchAgent with zero sources is rejected."""

    def test_research_agent_with_zero_sources_blocked(self):
        should, reason, code = _should_create_deliverable(
            title='Research: SMB ops automation',
            content='x' * 400,
            agent_name='ResearchAgent',
            metadata={'trigger_source': 'pa_tool', 'sources_count': 0},
        )
        self.assertFalse(should)
        self.assertEqual(code, 'gate_5_no_relevance')

    def test_research_agent_with_positive_sources_passes(self):
        should, reason, code = _should_create_deliverable(
            title='Research: SMB ops automation',
            content='x' * 400,
            agent_name='ResearchAgent',
            metadata={'trigger_source': 'pa_tool', 'sources_count': 3},
        )
        self.assertTrue(should)
        self.assertEqual(code, 'passed')

    def test_research_agent_without_sources_metadata_passes(self):
        """Backwards-compat: legacy callers that omit sources_count aren't blocked."""
        should, reason, code = _should_create_deliverable(
            title='Research: SMB ops automation',
            content='x' * 400,
            agent_name='ResearchAgent',
            metadata={'trigger_source': 'pa_tool'},
        )
        self.assertTrue(should)
        self.assertEqual(code, 'passed')

    def test_non_research_agent_zero_sources_ignored(self):
        """Relevance gate only fires for RELEVANCE_GATED_AGENTS."""
        should, reason, code = _should_create_deliverable(
            title='Analysis: market shift',
            content='x' * 400,
            agent_name='SomeOtherAgent',
            metadata={'trigger_source': 'pa_tool', 'sources_count': 0},
        )
        self.assertTrue(should)
        self.assertEqual(code, 'passed')


class TypedExceptionContractTests(TestCase):
    """raise_on_gated=True exposes the new reason codes via DeliverableGatedError."""

    def test_template_leak_raises_with_code(self):
        title = 'Research: BINDING DIRECTIVE: leaked'
        with self.assertRaises(DeliverableGatedError) as ctx:
            create_deliverable(
                title=title,
                content='x' * 400,
                agent_name='ResearchAgent',
                metadata={'trigger_source': 'pa_tool', 'sources_count': 3},
                raise_on_gated=True,
            )
        self.assertEqual(ctx.exception.reason_code, 'gate_4_template_leak')
        self.assertEqual(ctx.exception.agent_name, 'ResearchAgent')
        self.assertIn('BINDING DIRECTIVE', ctx.exception.title)

    def test_no_relevance_raises_with_code(self):
        with self.assertRaises(DeliverableGatedError) as ctx:
            create_deliverable(
                title='Research: market shift',
                content='x' * 400,
                agent_name='ResearchAgent',
                metadata={'trigger_source': 'pa_tool', 'sources_count': 0},
                raise_on_gated=True,
            )
        self.assertEqual(ctx.exception.reason_code, 'gate_5_no_relevance')

    def test_default_contract_returns_none_for_template_leak(self):
        """Legacy callers (raise_on_gated=False) still get None on gate-4 reject."""
        result = create_deliverable(
            title='Research: BINDING DIRECTIVE: leaked',
            content='x' * 400,
            agent_name='ResearchAgent',
            metadata={'trigger_source': 'pa_tool', 'sources_count': 3},
        )
        self.assertIsNone(result)
