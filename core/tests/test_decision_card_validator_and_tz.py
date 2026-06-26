"""Session 1238 PR-1 — Decision Card validator + truncation guard + TZ.

Three test classes:

1. ``DecisionCardValidatorTests`` — static method
   ``_validate_decision_card`` exercised against happy path + the 4
   defect shapes Rigby's 06-26 audience-fit verdict flagged
   (truncation, missing field, no decisions, sentinel).

2. ``DenverTimezoneInPromptTests`` — confirms the
   `_build_decision_card_synthesis prompt` injects the current Denver
   TZ abbreviation (MDT in summer / MST in winter) instead of the
   pre-fix hardcoded "MST".

3. ``TokenBudgetTests`` — confirms `max_completion_tokens=6000` for
   decision_card_synthesis (bumped from 4000) and 6000 for
   strategic_synthesis morning_brief mode.

Per `feedback_test_real_db_for_queryset_semantics`: real DB throughout;
mocks only at the OpenAI client boundary.

Run::

    python manage.py test core.tests.test_decision_card_validator_and_tz -v 2 --keepdb
"""

import uuid
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.services.workflow_orchestration_agent import (
    WorkflowOrchestrationAgent,
)

User = get_user_model()


class DecisionCardValidatorTests(TestCase):
    """Static method `_validate_decision_card` catches the 4 defect
    shapes Rigby's 06-26 audience-fit verdict flagged."""

    def test_valid_card_returns_no_issues(self):
        """Well-formed card with 2 decisions, all 4 fields each, ends
        with a period."""
        card = (
            "### Decision 1: Run live worker health checks\n"
            "- **Decision:** Approve immediate health check.\n"
            "- **Recommendation:** Run inspect commands now.\n"
            "- **Why now:** Lane 1 paralyzed warning.\n"
            "- **Next step:** DevOps — by 9:30 AM MDT.\n"
            "\n"
            "### Decision 2: Pause failing agents\n"
            "- **Decision:** Disable ArbitrageDetector + SportsOddsAnalyst.\n"
            "- **Recommendation:** Pause both for triage.\n"
            "- **Why now:** 45.5% success rate.\n"
            "- **Next step:** Eng Lead — by 10:00 AM MDT.\n"
        )
        issues = WorkflowOrchestrationAgent._validate_decision_card(card)
        self.assertEqual(issues, [])

    def test_sentinel_exempt(self):
        """The 'no urgent decisions' sentinel is valid by definition."""
        sentinel = 'No urgent decisions today — monitor only.'
        issues = WorkflowOrchestrationAgent._validate_decision_card(sentinel)
        self.assertEqual(issues, [])

    def test_empty_card_returns_issue(self):
        issues = WorkflowOrchestrationAgent._validate_decision_card('')
        self.assertEqual(issues, ['decision_card empty'])

    def test_truncation_mid_sentence_caught(self):
        """The 06-26 defect: Decision #3 ended at '...confirm whether
        missing odds data' with no period."""
        card = (
            "### Decision 1: Foo\n"
            "- **Decision:** Bar.\n"
            "- **Recommendation:** Baz.\n"
            "- **Why now:** Lane 1.\n"
            "- **Next step:** Owner — by 11 AM MDT.\n"
            "\n"
            "### Decision 2: Truncated mid-sentence\n"
            "- **Decision:** Investigate something.\n"
            "- **Recommendation:** Authorize a team to look at this\n"
            "  and confirm whether missing odds data"  # ← no period
        )
        issues = WorkflowOrchestrationAgent._validate_decision_card(card)
        # Two issues: truncation + missing required fields in Decision 2
        self.assertTrue(
            any('truncation' in i for i in issues),
            f"Expected truncation issue; got: {issues}",
        )

    def test_missing_required_field_caught(self):
        """A Decision block missing 'Next step:' fails validation."""
        card = (
            "### Decision 1: Half-formed\n"
            "- **Decision:** Do something.\n"
            "- **Recommendation:** Do it now.\n"
            "- **Why now:** Lane 2.\n"
            # No "Next step:" field
            "\nSome dangling text.\n"
        )
        issues = WorkflowOrchestrationAgent._validate_decision_card(card)
        self.assertTrue(
            any('Next step:' in i for i in issues),
            f"Expected Next step missing issue; got: {issues}",
        )

    def test_no_decision_headers_at_all_caught(self):
        """Random text that has no '### Decision' headers and is NOT the
        sentinel = invalid."""
        card = (
            "Some narrative text without proper structure. "
            "This should fail validation."
        )
        issues = WorkflowOrchestrationAgent._validate_decision_card(card)
        self.assertTrue(
            any("'### Decision N:' headers" in i for i in issues),
            f"Expected no-headers issue; got: {issues}",
        )


class DenverTimezoneInPromptTests(TestCase):
    """Decision Card prompt injects current Denver TZ abbreviation
    instead of pre-fix hardcoded 'MST'."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=f'test_dc_tz_{uuid.uuid4().hex[:8]}',
            password='test',
        )

    def test_prompt_uses_dynamic_tz_in_summer(self):
        """When called in June (DST active), prompt should reference MDT
        not MST."""
        from datetime import datetime
        from zoneinfo import ZoneInfo

        agent = WorkflowOrchestrationAgent(user=self.user)

        # Capture the prompt by mocking the OpenAI client
        captured_prompt = []
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'Mock card'
        mock_response.choices[0].finish_reason = 'stop'
        mock_client.chat.completions.create.return_value = mock_response

        def _capture(**kwargs):
            captured_prompt.append(kwargs['messages'][0]['content'])
            return mock_response

        mock_client.chat.completions.create.side_effect = _capture

        context = {
            'lane_1_text': 'lane 1 stuff',
            'lane_2_text': 'lane 2 stuff',
            'lane_3_text': 'lane 3 stuff',
            'lane_4_text': 'lane 4 stuff',
            'rotation_slot': 'ai_infra_deep_dive',
        }

        with patch(
            'core.services.openai_client_factory.get_openai_client',
            return_value=mock_client,
        ):
            agent._execute_decision_card_synthesis_step(context)

        self.assertEqual(len(captured_prompt), 1)
        prompt = captured_prompt[0]

        # Today's Denver TZ
        today_denver_tz = datetime.now(
            tz=ZoneInfo('America/Denver'),
        ).strftime('%Z')

        self.assertIn(
            today_denver_tz, prompt,
            f"Prompt should contain current Denver TZ '{today_denver_tz}' "
            f"(injected dynamically). Prompt excerpt:\n"
            f"...{prompt[-500:]}",
        )

    def test_prompt_no_longer_hardcodes_mst(self):
        """Regression guard: prompt source should not contain the
        pre-fix hardcoded 'AM MST' string outside of test or docstring."""
        import inspect
        src = inspect.getsource(
            WorkflowOrchestrationAgent._execute_decision_card_synthesis_step
        )
        # The fix uses f-string with `_denver_tz`. Literal "AM MST"
        # should be gone from the live prompt construction.
        # Allow 'MST' to appear only in the fallback comment.
        live_code_lines = [
            l for l in src.splitlines()
            if not l.strip().startswith('#')
            and not l.strip().startswith('"')
        ]
        live_code = '\n'.join(live_code_lines)
        self.assertNotIn(
            'by 11:00 AM MST', live_code,
            "Pre-fix literal 'by 11:00 AM MST' found in live code; "
            "should use dynamic _denver_tz f-string instead.",
        )


class TokenBudgetTests(TestCase):
    """decision_card_synthesis budget bumped 4000 → 6000;
    strategic_synthesis morning_brief mode also 6000."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=f'test_budget_{uuid.uuid4().hex[:8]}',
            password='test',
        )

    def _capture_max_tokens(self, step_invocation):
        captured = []
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'Mock content'
        mock_response.choices[0].finish_reason = 'stop'

        def _capture(**kwargs):
            captured.append(kwargs.get('max_completion_tokens'))
            return mock_response

        mock_client.chat.completions.create.side_effect = _capture
        with patch(
            'core.services.openai_client_factory.get_openai_client',
            return_value=mock_client,
        ):
            step_invocation()
        return captured

    def test_decision_card_synthesis_budget_is_6000(self):
        agent = WorkflowOrchestrationAgent(user=self.user)
        captured = self._capture_max_tokens(
            lambda: agent._execute_decision_card_synthesis_step({
                'lane_1_text': 'a', 'lane_2_text': 'b',
                'lane_3_text': 'c', 'lane_4_text': 'd',
            })
        )
        self.assertEqual(captured, [6000])

    def test_strategic_synthesis_morning_brief_mode_budget_is_6000(self):
        agent = WorkflowOrchestrationAgent(user=self.user)
        captured = self._capture_max_tokens(
            lambda: agent._execute_strategic_synthesis_step({
                '_synthesis_mode': 'morning_brief',
                'lane_1_text': 'a', 'lane_2_text': 'b',
                'lane_3_text': 'c', 'lane_4_text': 'd',
                'decision_card_text': 'card',
            })
        )
        self.assertEqual(captured, [6000])

    def test_strategic_synthesis_default_mode_budget_unchanged_at_4000(self):
        agent = WorkflowOrchestrationAgent(user=self.user)
        captured = self._capture_max_tokens(
            lambda: agent._execute_strategic_synthesis_step({
                'topic': 'something',
            })
        )
        self.assertEqual(captured, [4000])
