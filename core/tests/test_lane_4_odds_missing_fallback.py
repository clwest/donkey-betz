"""Session 1238 PR-3 — Lane 4 odds-missing fallback.

Three test classes:

1. ``LaneFourThinDetectorTests`` — `_lane_4_output_is_thin` heuristic
   correctly classifies thin vs substantive outputs.

2. ``LaneFourSportsEdgeFallbackContentTests`` — the static fallback
   template includes Rigby's 3 required blocks (Data status / What we
   can still do today / Action).

3. ``LaneFourAugmentationIntegrationTests`` — `_execute_lane_4_
   rotating_focus_step` augments thin sports_edge_scan outputs and
   leaves other slots / substantive outputs unchanged.

Per `feedback_test_real_db_for_queryset_semantics`: real DB; mocks
only at the `core.agent_router.AgentRouter` boundary (the agent
dispatch surface — agents themselves are out of test scope).

Run::

    python manage.py test core.tests.test_lane_4_odds_missing_fallback -v 2 --keepdb
"""

import uuid
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.services.workflow_orchestration_agent import (
    WorkflowOrchestrationAgent,
)

User = get_user_model()


class LaneFourThinDetectorTests(TestCase):
    """`_lane_4_output_is_thin` correctly classifies outputs."""

    def test_empty_string_is_thin(self):
        self.assertTrue(WorkflowOrchestrationAgent._lane_4_output_is_thin(''))

    def test_short_string_is_thin(self):
        self.assertTrue(WorkflowOrchestrationAgent._lane_4_output_is_thin('Hi.'))

    def test_no_multi_bookmaker_marker_is_thin(self):
        """The exact 06-26 case: agent reported success with
        'No multi-bookmaker odds data available.'"""
        text = "No multi-bookmaker odds data available."
        self.assertTrue(WorkflowOrchestrationAgent._lane_4_output_is_thin(text))

    def test_substantial_content_is_not_thin(self):
        text = (
            "Sharp action detected on Lakers/Warriors total. Line moved "
            "from 220.5 to 222 on 65% reverse line move from Pinnacle and "
            "Circa. Limit increase on Pinnacle suggests sharp interest in "
            "the over. Watch for additional movement into 7pm cutoff. "
            "Action: consider a moderate position on the over at 222 or "
            "better; closing-line value likely positive."
        )
        self.assertFalse(WorkflowOrchestrationAgent._lane_4_output_is_thin(text))

    def test_substantial_with_caveat_is_not_thin(self):
        text = (
            "Three qualifying edges found this morning across NFL preseason. "
            "Cowboys -3 vs Browns has reverse line movement of 1.5 points "
            "on 38% public bet share — classic sharp money signal. "
            "Recommendation: lay -3 at currently available -110 books. "
            "Detail: this is a 200+ character substantive output that "
            "should NOT be flagged as thin even though it covers fewer markets."
        )
        self.assertFalse(WorkflowOrchestrationAgent._lane_4_output_is_thin(text))


class LaneFourSportsEdgeFallbackContentTests(TestCase):
    """Static fallback template includes Rigby's 3 required blocks."""

    def test_fallback_includes_data_status_block(self):
        text = WorkflowOrchestrationAgent._lane_4_sports_edge_scan_fallback()
        self.assertIn('Data status', text)
        self.assertIn('Multi-bookmaker odds', text)

    def test_fallback_includes_what_we_can_still_do_block(self):
        text = WorkflowOrchestrationAgent._lane_4_sports_edge_scan_fallback()
        self.assertIn('What we can still do today', text)

    def test_fallback_includes_action_block(self):
        text = WorkflowOrchestrationAgent._lane_4_sports_edge_scan_fallback()
        self.assertIn('Action', text)
        # At least one concrete action suggestion
        self.assertTrue(
            any(verb in text.lower() for verb in (
                'verify', 'trigger', 'restart', 'file',
            )),
            'Fallback should include a concrete action verb',
        )

    def test_fallback_is_substantive_length(self):
        """Fallback itself should be >> the thin threshold so brief
        ships with real content."""
        text = WorkflowOrchestrationAgent._lane_4_sports_edge_scan_fallback()
        self.assertGreater(len(text), 600)


class LaneFourAugmentationIntegrationTests(TestCase):
    """`_execute_lane_4_rotating_focus_step` augments thin
    sports_edge_scan outputs; leaves other paths untouched."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=f'test_l4_aug_{uuid.uuid4().hex[:8]}',
            password='test',
        )

    def _dispatch_with_mock_result(self, slot, mock_message, mock_success=True):
        """Helper: dispatch the Lane 4 step with a mocked AgentRouter
        that returns the given (success, message). Returns the step's
        return dict."""
        agent = WorkflowOrchestrationAgent(user=self.user)

        mock_result = MagicMock()
        mock_result.success = mock_success
        mock_result.message = mock_message
        mock_result.data = {}
        mock_result.error = None

        mock_router = MagicMock()
        # Include all slot agents so test can dispatch any slot
        mock_router.AGENT_MAP = {
            'SharpActionDetector': 'fake',
            'PredictionMarketAnalyst': 'fake',
            'StockAnalystAgent': 'fake',
            'COOAgent': 'fake',
            'ResearchAgent': 'fake',
        }
        mock_router.route.return_value = mock_result

        with patch(
            'core.agent_router.AgentRouter',
            return_value=mock_router,
        ):
            return agent._execute_lane_4_rotating_focus_step({
                'rotation_slot': slot,
                'topic': 'test',
            })

    def test_thin_sports_edge_scan_output_is_augmented(self):
        """The exact 06-26 case: agent returned success with thin output.
        Augmented output should include the fallback template."""
        result = self._dispatch_with_mock_result(
            slot='sports_edge_scan',
            mock_message='No multi-bookmaker odds data available.',
        )
        self.assertTrue(result['success'])
        self.assertIn('Session 1238 PR-3', result['output'])
        self.assertIn('Data status', result['output'])
        self.assertIn('What we can still do today', result['output'])
        self.assertIn('Action', result['output'])

    def test_substantive_sports_edge_output_not_augmented(self):
        """When the agent returns real content, no augmentation."""
        substantive = (
            "Three sharp-action edges found this morning. Lakers/Warriors "
            "total moved from 220.5 to 222 on reverse line movement. "
            "Cowboys -3 has 65% sharp money signal. Recommendation: "
            "moderate position on each. Detail: comprehensive analysis "
            "of cross-bookmaker line moves shows consistent sharp interest."
        )
        result = self._dispatch_with_mock_result(
            slot='sports_edge_scan',
            mock_message=substantive,
        )
        self.assertTrue(result['success'])
        self.assertNotIn('Session 1238 PR-3', result['output'])
        self.assertNotIn('What we can still do today', result['output'])
        self.assertEqual(result['output'], substantive)

    def test_thin_non_sports_slot_not_augmented(self):
        """Other slots (e.g., ai_infra_deep_dive) don't get the
        sports_edge_scan fallback even if their output is thin."""
        result = self._dispatch_with_mock_result(
            slot='ai_infra_deep_dive',
            mock_message='Nothing notable today.',
        )
        self.assertTrue(result['success'])
        self.assertNotIn('Session 1238 PR-3', result['output'])
        self.assertNotIn('Data status', result['output'])
        # Output unchanged
        self.assertEqual(result['output'], 'Nothing notable today.')

    def test_failure_path_unchanged(self):
        """When the agent returns success=False, the existing fail-loud
        + sentinel path runs — augmentation does NOT fire."""
        result = self._dispatch_with_mock_result(
            slot='sports_edge_scan',
            mock_message='No multi-bookmaker odds data available.',
            mock_success=False,
        )
        self.assertFalse(result['success'])
        # The failure-path sentinel kicks in, no Session 1238 PR-3
        # augmentation header in output
        self.assertNotIn('Session 1238 PR-3', result['output'])
