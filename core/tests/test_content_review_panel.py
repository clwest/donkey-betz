"""
Tests for ContentReviewPanel - Session 961
==========================================

Tests the multi-agent content review panel with mocked LLM/conversation calls.
"""

import pytest
from unittest.mock import MagicMock, patch

from core.services.content_review_panel import (
    ContentReviewPanel,
    ReviewResult,
    DOMAIN_REVIEW_AGENTS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def panel():
    """Return a ContentReviewPanel with all dependencies mocked out."""
    p = ContentReviewPanel()
    # Pre-set lazy instances to avoid real imports during tests
    p._domain_builder_instance = MagicMock()
    p._spider_builder_instance = MagicMock()
    p._orchestrator_instance = MagicMock()
    return p


@pytest.fixture
def sample_content():
    return {
        'title': 'AI Startup Trends in 2026',
        'intro': 'The AI landscape is evolving rapidly.',
        'sections': [
            {'header': 'Section 1', 'content': 'Machine learning advances...'},
            {'header': 'Section 2', 'content': 'Enterprise adoption...'},
        ],
        'conclusion': 'The future is bright for AI startups.',
        'full_text': 'The AI landscape is evolving rapidly. Machine learning advances. Enterprise adoption. The future is bright for AI startups.',
        'meta_description': 'AI startup trends analysis',
        'keywords': ['AI', 'startups', 'trends'],
    }


def _make_conversation(chosen_path='PUBLISH this content', decision_text='PUBLISH', messages=None):
    """Build a fake conversation result dict."""
    if messages is None:
        messages = [
            {'agent': 'EditorAgent', 'content': 'The structure is solid.'},
            {'agent': 'TrendAnalysisAgent', 'content': 'Claims are backed by data.'},
            {'agent': 'EditorAgent', 'content': 'Weaknesses: needs stronger hook.'},
            {'agent': 'TrendAnalysisAgent', 'content': f'Recommendation: {decision_text}.'},
        ]
    return {
        'messages': messages,
        'decision_summary': {'decision': decision_text, 'insights': [], 'next_steps': []},
        'execution_mandate': {
            'chosen_path': chosen_path,
            'reason': 'Content meets quality bar',
            'decision_owner': 'EditorAgent',
        },
        'validation': {},
        'state': {},
    }


# ---------------------------------------------------------------------------
# 1. ReviewResult dataclass
# ---------------------------------------------------------------------------

class TestReviewResultDataclass:
    def test_review_result_dataclass(self):
        """All fields populated correctly."""
        result = ReviewResult(
            decision='publish',
            enhanced_content={'title': 'Better Title'},
            review_notes='Looks great',
            confidence=0.85,
            panel_composition=['EditorAgent', 'TrendAnalysisAgent'],
            spider_data_used=True,
            mandate={'chosen_path': 'PUBLISH'},
            execution_time_ms=1234,
        )
        assert result.decision == 'publish'
        assert result.enhanced_content == {'title': 'Better Title'}
        assert result.review_notes == 'Looks great'
        assert result.confidence == 0.85
        assert result.panel_composition == ['EditorAgent', 'TrendAnalysisAgent']
        assert result.spider_data_used is True
        assert result.mandate == {'chosen_path': 'PUBLISH'}
        assert result.execution_time_ms == 1234


# ---------------------------------------------------------------------------
# 2-4. Domain detection
# ---------------------------------------------------------------------------

class TestDomainDetection:
    def test_domain_detection_finance(self, panel, sample_content):
        """Finance topic -> domain='finance'."""
        panel._domain_builder_instance.detect_domain.return_value = ('finance', 0.9)
        domain = panel._detect_domain(sample_content, 'stock market investment strategies')
        assert domain == 'finance'

    def test_domain_detection_crypto(self, panel, sample_content):
        """Crypto topic -> domain='crypto'."""
        panel._domain_builder_instance.detect_domain.return_value = ('crypto', 0.85)
        domain = panel._detect_domain(sample_content, 'bitcoin ethereum blockchain')
        assert domain == 'crypto'

    def test_domain_detection_general(self, panel, sample_content):
        """Generic topic -> domain='general'."""
        panel._domain_builder_instance.detect_domain.return_value = ('general', 0.0)
        domain = panel._detect_domain(sample_content, 'random thoughts on life')
        assert domain == 'general'


# ---------------------------------------------------------------------------
# 5-6. Panel assembly
# ---------------------------------------------------------------------------

class TestPanelAssembly:
    def test_panel_assembly_finance(self, panel):
        """Finance -> EditorAgent + TrendAnalysisAgent."""
        result = panel._assemble_panel('finance')
        assert len(result) == 2
        assert result[0]['name'] == 'EditorAgent'
        assert result[1]['name'] == 'TrendAnalysisAgent'

    def test_panel_assembly_general(self, panel):
        """General -> EditorAgent + ContentStrategyAgent."""
        result = panel._assemble_panel('general')
        assert len(result) == 2
        assert result[0]['name'] == 'EditorAgent'
        assert result[1]['name'] == 'ContentStrategyAgent'


# ---------------------------------------------------------------------------
# 7-9. Decision extraction via full review()
# ---------------------------------------------------------------------------

class TestReviewDecisions:
    def test_review_publish_decision(self, panel, sample_content):
        """Mock conversation with PUBLISH mandate -> decision='publish'."""
        panel._domain_builder_instance.detect_domain.return_value = ('ai_tech', 0.8)
        panel._spider_builder_instance.build_context_for_agent.return_value = {
            'summary': 'AI adoption is growing 40% YoY',
        }
        panel._orchestrator_instance.generate_conversation.return_value = _make_conversation(
            chosen_path='PUBLISH this content immediately',
            decision_text='PUBLISH',
        )

        result = panel.review(sample_content, topic='AI trends')

        assert result.decision == 'publish'
        assert result.confidence >= 0.7
        assert 'EditorAgent' in result.panel_composition
        assert result.spider_data_used is True
        assert result.mandate is not None
        assert result.execution_time_ms >= 0

    def test_review_revise_decision(self, panel, sample_content):
        """Mock conversation with REVISE mandate -> decision='revise'."""
        panel._domain_builder_instance.detect_domain.return_value = ('finance', 0.9)
        panel._spider_builder_instance.build_context_for_agent.return_value = {'summary': ''}
        panel._orchestrator_instance.generate_conversation.return_value = _make_conversation(
            chosen_path='REVISE with stronger data citations',
            decision_text='REVISE',
        )

        result = panel.review(sample_content, topic='investment strategies')

        assert result.decision == 'revise'
        assert result.confidence >= 0.5

    def test_review_kill_decision(self, panel, sample_content):
        """Mock conversation with KILL mandate -> decision='kill'."""
        panel._domain_builder_instance.detect_domain.return_value = ('general', 0.3)
        panel._spider_builder_instance.build_context_for_agent.return_value = {'summary': ''}
        panel._orchestrator_instance.generate_conversation.return_value = _make_conversation(
            chosen_path='KILL this content - too generic',
            decision_text='KILL',
        )

        result = panel.review(sample_content, topic='random topic')

        assert result.decision == 'kill'
        assert result.confidence >= 0.5


# ---------------------------------------------------------------------------
# 10. Graceful degradation
# ---------------------------------------------------------------------------

class TestGracefulDegradation:
    def test_graceful_degradation(self, panel, sample_content):
        """Orchestrator raises exception -> returns ReviewResult(decision='draft')."""
        panel._domain_builder_instance.detect_domain.return_value = ('general', 0.5)
        panel._spider_builder_instance.build_context_for_agent.return_value = {'summary': ''}
        panel._orchestrator_instance.generate_conversation.side_effect = RuntimeError(
            "LLM provider unavailable"
        )

        result = panel.review(sample_content, topic='test topic')

        assert result.decision == 'draft'
        assert result.confidence == 0.0
        assert 'unavailable' in result.review_notes.lower()
        assert result.execution_time_ms >= 0
