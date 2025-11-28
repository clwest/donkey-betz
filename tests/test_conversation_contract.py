"""
Tests for Agent Conversation Contract Enforcement
==================================================

Session 261: Tests for the upgraded agent conversation system.

These tests verify that:
1. Tension detection works correctly
2. Grounding detection works correctly
3. DecisionSummary extraction works correctly
4. Contract validation enforces requirements
"""

import pytest
from unittest.mock import patch, MagicMock


class TestTensionDetection:
    """Test tension/disagreement detection in conversation messages."""

    def test_detects_however(self):
        """'However' should indicate tension."""
        from core.conversation_roles import has_tension
        text = "That's interesting, however I think we should consider the data more carefully."
        assert has_tension(text) is True

    def test_detects_but(self):
        """'But' should indicate tension."""
        from core.conversation_roles import has_tension
        text = "I see your point, but the metrics don't support that conclusion."
        assert has_tension(text) is True

    def test_detects_concern(self):
        """'Concern' should indicate tension."""
        from core.conversation_roles import has_tension
        text = "My concern is that the data doesn't support this approach."
        assert has_tension(text) is True

    def test_detects_trade_off(self):
        """'Trade-off' should indicate tension."""
        from core.conversation_roles import has_tension
        text = "There's a trade-off between speed and accuracy here."
        assert has_tension(text) is True

    def test_detects_alternative(self):
        """'Alternative' should indicate tension."""
        from core.conversation_roles import has_tension
        text = "An alternative approach would be to use embeddings for comparison."
        assert has_tension(text) is True

    def test_detects_caveat(self):
        """'Caveat' should indicate tension."""
        from core.conversation_roles import has_tension
        text = "That works with one caveat - we need to validate the assumptions first."
        assert has_tension(text) is True

    def test_detects_what_if(self):
        """'What if' should indicate tension."""
        from core.conversation_roles import has_tension
        text = "What if we approached this from a different angle?"
        assert has_tension(text) is True

    def test_rejects_pure_agreement(self):
        """Pure agreement without nuance should not show tension."""
        from core.conversation_roles import has_tension
        text = "I completely agree with everything you said. That's exactly right!"
        assert has_tension(text) is False

    def test_rejects_empty_praise(self):
        """Empty praise should not show tension."""
        from core.conversation_roles import has_tension
        text = "Great point! Love that idea! Absolutely brilliant!"
        assert has_tension(text) is False

    def test_case_insensitive(self):
        """Tension detection should be case insensitive."""
        from core.conversation_roles import has_tension
        text = "HOWEVER, I think we should reconsider."
        assert has_tension(text) is True


class TestEmptyAgreementDetection:
    """Test detection of empty agreement phrases (to be avoided)."""

    def test_detects_absolutely(self):
        """'Absolutely' should be detected as empty agreement."""
        from core.conversation_roles import has_empty_agreement
        text = "Absolutely! That's a great idea."
        assert has_empty_agreement(text) is True

    def test_detects_great_point(self):
        """'Great point' should be detected as empty agreement."""
        from core.conversation_roles import has_empty_agreement
        text = "Great point! I couldn't agree more."
        assert has_empty_agreement(text) is True

    def test_detects_love_that(self):
        """'Love that' should be detected as empty agreement."""
        from core.conversation_roles import has_empty_agreement
        text = "Love that idea! Let's do it."
        assert has_empty_agreement(text) is True

    def test_accepts_nuanced_agreement(self):
        """Agreement with nuance should NOT be detected as empty."""
        from core.conversation_roles import has_empty_agreement
        text = "I agree with the general direction, though we should consider the trade-offs."
        assert has_empty_agreement(text) is False


class TestGroundingDetection:
    """Test platform grounding detection in conversation messages."""

    def test_detects_embedding_reference(self):
        """Reference to embeddings should be detected."""
        from core.conversation_roles import has_grounding
        text = "We could use embedding similarity to measure this."
        assert has_grounding(text) is True

    def test_detects_rag_reference(self):
        """Reference to RAG should be detected."""
        from core.conversation_roles import has_grounding
        text = "RAG retrieval could power personalized recommendations."
        assert has_grounding(text) is True

    def test_detects_spider_reference(self):
        """Reference to spiders should be detected."""
        from core.conversation_roles import has_grounding
        text = "The spider data from TechCrunch shows increasing interest."
        assert has_grounding(text) is True

    def test_detects_dashboard_reference(self):
        """Reference to dashboards should be detected."""
        from core.conversation_roles import has_grounding
        text = "We could add this as a dashboard widget."
        assert has_grounding(text) is True

    def test_detects_scroll_depth_metric(self):
        """Reference to scroll depth metric should be detected."""
        from core.conversation_roles import has_grounding
        text = "The scroll depth data shows users prefer shorter content."
        assert has_grounding(text) is True

    def test_detects_completion_rate_metric(self):
        """Reference to completion rate metric should be detected."""
        from core.conversation_roles import has_grounding
        text = "We're seeing a 40% completion rate on long-form articles."
        assert has_grounding(text) is True

    def test_detects_reading_time_metric(self):
        """Reference to reading time metric should be detected."""
        from core.conversation_roles import has_grounding
        text = "Articles in the 7-11 minute reading time range perform best."
        assert has_grounding(text) is True

    def test_rejects_generic_content(self):
        """Generic content without platform references should not be grounded."""
        from core.conversation_roles import has_grounding
        text = "We should focus on quality and creativity."
        assert has_grounding(text) is False

    def test_rejects_abstract_discussion(self):
        """Abstract discussion without specifics should not be grounded."""
        from core.conversation_roles import has_grounding
        text = "Users want quality experiences that resonate emotionally."
        assert has_grounding(text) is False


class TestGroundingRefsExtraction:
    """Test extraction of specific grounding references."""

    def test_extracts_multiple_refs(self):
        """Should extract all grounding references from text."""
        from core.conversation_roles import get_grounding_refs
        text = "We should check scroll depth and embedding similarity in the dashboard."
        refs = get_grounding_refs(text)
        assert len(refs) >= 3
        assert any('scroll depth' in r for r in refs)
        assert any('embedding' in r for r in refs)
        assert any('dashboard' in r for r in refs)

    def test_returns_empty_for_ungrounded(self):
        """Should return empty list for ungrounded text."""
        from core.conversation_roles import get_grounding_refs
        text = "This is a generic statement about content."
        refs = get_grounding_refs(text)
        assert refs == []


class TestDecisionSummaryExtraction:
    """Test DecisionSummary parsing from conversation messages."""

    def test_extracts_complete_summary(self):
        """Should extract all parts of a complete DecisionSummary."""
        from core.conversation_roles import extract_decision_summary
        text = '''
Some discussion here about the topic.

=== DecisionSummary ===
Insights:
1. First insight about data patterns and scroll depth metrics
2. Second insight about user behavior and retention
3. Third insight about implementation using RAG

Proposed Feature:
- Name: Content Quality Panel
- Inputs: Article text, metadata, and engagement metrics
- Outputs: Quality scores, pacing analysis, vulnerability index
- Where it plugs into the system: Dashboard widget and content reflection UI

Next Steps:
1. ResearchAgent: Design the scoring algorithm with specific metrics
2. ContentStrategyAgent: Draft UX mockups for the quality panel
'''
        result = extract_decision_summary(text)

        assert result is not None
        assert len(result['insights']) == 3
        assert 'scroll depth' in result['insights'][0].lower() or 'data' in result['insights'][0].lower()
        assert result['proposed_feature']['name'] == 'Content Quality Panel'
        assert 'Article text' in result['proposed_feature']['inputs']
        assert 'Dashboard' in result['proposed_feature']['integration']
        assert len(result['next_steps']) == 2

    def test_returns_none_without_summary(self):
        """Should return None if no DecisionSummary block present."""
        from core.conversation_roles import extract_decision_summary
        text = "Just a regular message without any summary block."
        result = extract_decision_summary(text)
        assert result is None

    def test_handles_partial_summary(self):
        """Should handle partially complete DecisionSummary."""
        from core.conversation_roles import extract_decision_summary
        text = '''
=== DecisionSummary ===
Insights:
1. Single insight here

Proposed Feature:
- Name: Test Feature
'''
        result = extract_decision_summary(text)

        assert result is not None
        assert len(result['insights']) == 1
        assert result['proposed_feature']['name'] == 'Test Feature'


class TestDecisionSummaryValidation:
    """Test validation of DecisionSummary completeness."""

    def test_validates_complete_summary(self):
        """Complete summary should pass validation."""
        from core.conversation_roles import validate_decision_summary
        summary = {
            'insights': ['Insight 1', 'Insight 2', 'Insight 3'],
            'proposed_feature': {'name': 'Test Feature', 'inputs': 'X', 'outputs': 'Y'},
            'next_steps': ['Step 1', 'Step 2']
        }
        result = validate_decision_summary(summary)

        assert result['is_valid'] is True
        assert result['has_insights'] is True
        assert result['has_feature'] is True
        assert result['has_next_steps'] is True

    def test_fails_insufficient_insights(self):
        """Should fail if fewer than 3 insights."""
        from core.conversation_roles import validate_decision_summary
        summary = {
            'insights': ['Insight 1', 'Insight 2'],  # Only 2
            'proposed_feature': {'name': 'Test Feature'},
            'next_steps': ['Step 1', 'Step 2']
        }
        result = validate_decision_summary(summary)

        assert result['is_valid'] is False
        assert result['has_insights'] is False

    def test_fails_missing_feature(self):
        """Should fail if no proposed feature."""
        from core.conversation_roles import validate_decision_summary
        summary = {
            'insights': ['Insight 1', 'Insight 2', 'Insight 3'],
            'proposed_feature': {},  # No name
            'next_steps': ['Step 1', 'Step 2']
        }
        result = validate_decision_summary(summary)

        assert result['is_valid'] is False
        assert result['has_feature'] is False

    def test_fails_insufficient_next_steps(self):
        """Should fail if fewer than 2 next steps."""
        from core.conversation_roles import validate_decision_summary
        summary = {
            'insights': ['Insight 1', 'Insight 2', 'Insight 3'],
            'proposed_feature': {'name': 'Test Feature'},
            'next_steps': ['Step 1']  # Only 1
        }
        result = validate_decision_summary(summary)

        assert result['is_valid'] is False
        assert result['has_next_steps'] is False

    def test_handles_none_summary(self):
        """Should handle None gracefully."""
        from core.conversation_roles import validate_decision_summary
        result = validate_decision_summary(None)

        assert result['is_valid'] is False


class TestConversationRolePrompts:
    """Test role-specific prompt generation."""

    def test_research_agent_role_includes_data_focus(self):
        """ResearchAgent role should emphasize data and patterns."""
        from core.conversation_roles import get_conversation_role
        role = get_conversation_role('ResearchAgent', 'ResearchAgent')

        assert 'data realist' in role.lower()
        assert 'pattern' in role.lower()
        assert 'metric' in role.lower() or 'measure' in role.lower()

    def test_content_strategy_agent_role_includes_storytelling(self):
        """ContentStrategyAgent role should emphasize storytelling."""
        from core.conversation_roles import get_conversation_role
        role = get_conversation_role('ContentStrategyAgent', 'ContentStrategyAgent')

        assert 'storytelling' in role.lower() or 'narrative' in role.lower()
        assert 'framework' in role.lower()
        assert 'psychology' in role.lower() or 'user' in role.lower()

    def test_roles_include_platform_context(self):
        """All roles should include platform context."""
        from core.conversation_roles import get_conversation_role
        role = get_conversation_role('ResearchAgent', 'ResearchAgent')

        assert 'spider' in role.lower()
        assert 'rag' in role.lower() or 'embedding' in role.lower()
        assert 'dashboard' in role.lower()

    def test_default_role_for_unknown_agent(self):
        """Unknown agents should get default role with their info."""
        from core.conversation_roles import get_conversation_role
        role = get_conversation_role('CustomAgent', 'CustomAgent', 'Custom specialty')

        assert 'CustomAgent' in role
        assert 'Custom specialty' in role


class TestConversationOrchestrator:
    """Test the ConversationOrchestrator class."""

    def test_message_classification(self):
        """Test that messages are classified correctly."""
        from core.conversation_orchestrator import ConversationOrchestrator

        orchestrator = ConversationOrchestrator()

        # Question
        assert orchestrator._classify_message("What do you think about this?", 0, 6) == 'question'

        # Challenge
        assert orchestrator._classify_message("However, the data suggests otherwise.", 1, 6) == 'challenge'

        # Proposal
        assert orchestrator._classify_message("I propose we build a dashboard widget.", 2, 6) == 'proposal'

        # Conclusion (final turn)
        assert orchestrator._classify_message("Let's summarize our discussion.", 5, 6) == 'conclusion'

    def test_quality_score_calculation(self):
        """Test quality score calculation."""
        from core.conversation_orchestrator import ConversationOrchestrator, ConversationState

        orchestrator = ConversationOrchestrator()

        # Good conversation state
        state = ConversationState(
            tension_count=3,
            grounding_count=4,
            empty_agreement_count=0
        )
        summary_validation = {
            'has_insights': True,
            'has_feature': True,
            'has_next_steps': True
        }

        score = orchestrator._calculate_quality_score(state, summary_validation)
        assert score >= 80  # Should be high quality

        # Poor conversation state
        poor_state = ConversationState(
            tension_count=0,
            grounding_count=1,
            empty_agreement_count=3
        )
        poor_validation = {
            'has_insights': False,
            'has_feature': False,
            'has_next_steps': False
        }

        poor_score = orchestrator._calculate_quality_score(poor_state, poor_validation)
        assert poor_score < 30  # Should be low quality

    def test_contract_validation(self):
        """Test full contract validation."""
        from core.conversation_orchestrator import ConversationOrchestrator, ConversationState
        from core.conversation_roles import extract_decision_summary

        orchestrator = ConversationOrchestrator()

        # Create compliant messages
        messages = [
            {'content': 'However, the data suggests...', 'contains_tension': True, 'has_grounding': True},
            {'content': 'My concern is the trade-off...', 'contains_tension': True, 'has_grounding': True},
            {'content': 'Looking at scroll depth metrics...', 'contains_tension': False, 'has_grounding': True},
            {'content': '''Final summary.
=== DecisionSummary ===
Insights:
1. First insight
2. Second insight
3. Third insight

Proposed Feature:
- Name: Test Feature
- Inputs: Data
- Outputs: Results
- Where it plugs into the system: Dashboard

Next Steps:
1. Do A
2. Do B''', 'contains_tension': False, 'has_grounding': False},
        ]

        state = ConversationState(
            tension_count=2,
            grounding_count=3
        )

        decision_summary = extract_decision_summary(messages[-1]['content'])
        validation = orchestrator._validate_contract(messages, decision_summary, state)

        assert validation['is_valid'] is True
        assert validation['tension_met'] is True
        assert validation['grounding_met'] is True


# Run tests if executed directly
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
