"""Session 1242 Path C — structured decision_card form tests.

Three test classes mirror the implementation surface:

1. ``DecisionCardResponseParserTests`` — ``_parse_decision_card_response``
   splits the LLM's markdown body + ```json``` block, handles every
   parse failure shape (no fence, bad JSON, wrong root type, missing
   key, wrong value type), and recovers gracefully.

2. ``DecisionCardsStructuredValidatorTests`` —
   ``_validate_decision_cards_structured`` enforces the locked Rigby
   contract (6 keys per card, style enum, ISO-8601 offset, null-when-relative
   rule).

3. ``DecisionCardSynthesisStructuredFormIntegrationTests`` — end-to-end
   exercise of ``_execute_decision_card_synthesis_step`` with a mocked
   gpt-5-mini, covering: empty lane inputs sentinel, full success path
   (markdown + structured), JSON parse failure graceful degradation,
   structured-form validation failure, observability log format.

All tests use real DB (per ``feedback_test_real_db_for_queryset_semantics``);
mocks at ``openai_client_factory.get_openai_client`` boundary only.

Run::

    python manage.py test core.tests.test_decision_card_structured_form -v 2 --keepdb
"""

import json
import uuid
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.services.workflow_orchestration_agent import (
    WorkflowOrchestrationAgent,
)

User = get_user_model()


class DecisionCardResponseParserTests(TestCase):

    def test_empty_response_returns_empty_tuple_with_diagnostic(self):
        md, cards, issue = (
            WorkflowOrchestrationAgent._parse_decision_card_response('')
        )
        self.assertEqual(md, '')
        self.assertEqual(cards, [])
        self.assertIn('empty', issue.lower())

    def test_whitespace_only_response_treated_as_empty(self):
        md, cards, issue = (
            WorkflowOrchestrationAgent._parse_decision_card_response('  \n\n  ')
        )
        self.assertEqual(cards, [])
        self.assertIn('empty', issue.lower())

    def test_no_json_fence_returns_full_response_as_markdown(self):
        body = (
            "### Decision 1: Restore agent execution\n"
            "- **Decision:** Restart Celery workers.\n"
            "- **Recommendation:** Do it now.\n"
            "- **Why now:** MUSCULAR warning persists.\n"
            "- **Next step:** DevOps — within 2 hours.\n"
        )
        md, cards, issue = (
            WorkflowOrchestrationAgent._parse_decision_card_response(body)
        )
        self.assertEqual(md, body.strip())
        self.assertEqual(cards, [])
        self.assertIn('no JSON fence', issue)

    def test_malformed_json_returns_markdown_with_decode_diagnostic(self):
        body = (
            "### Decision 1: X\n- **Decision:** Y\n\n"
            "```json\n{ this is not valid json }\n```\n"
        )
        md, cards, issue = (
            WorkflowOrchestrationAgent._parse_decision_card_response(body)
        )
        self.assertIn('Decision 1: X', md)
        self.assertEqual(cards, [])
        self.assertIn('json decode error', issue.lower())

    def test_json_root_not_dict_returns_diagnostic(self):
        body = (
            "### Decision 1: X\n\n"
            "```json\n[1, 2, 3]\n```\n"
        )
        md, cards, issue = (
            WorkflowOrchestrationAgent._parse_decision_card_response(body)
        )
        self.assertEqual(cards, [])
        self.assertIn('not dict', issue)

    def test_missing_decision_cards_key(self):
        body = (
            "### Decision 1: X\n\n"
            '```json\n{"other_key": []}\n```\n'
        )
        md, cards, issue = (
            WorkflowOrchestrationAgent._parse_decision_card_response(body)
        )
        self.assertEqual(cards, [])
        self.assertIn('missing', issue.lower())
        self.assertIn('decision_cards', issue)

    def test_decision_cards_not_list(self):
        body = (
            "### Decision 1: X\n\n"
            '```json\n{"decision_cards": {"oops": true}}\n```\n'
        )
        md, cards, issue = (
            WorkflowOrchestrationAgent._parse_decision_card_response(body)
        )
        self.assertEqual(cards, [])
        self.assertIn('not list', issue)

    def test_successful_parse_splits_markdown_and_cards(self):
        body = (
            "### Decision 1: Restart workers\n"
            "- **Decision:** Restart now.\n"
            "- **Recommendation:** Just do it.\n"
            "- **Why now:** Workers wedged.\n"
            "- **Next step:** DevOps — within 2 hours.\n\n"
            "```json\n"
            '{"decision_cards": [{"decision": "Restart now.", "recommendation": "Just do it.", '
            '"why_now": "Workers wedged.", "next_step_owner": "DevOps", '
            '"next_step_deadline_style": "relative", "next_step_timebox": null}]}\n'
            "```\n"
        )
        md, cards, issue = (
            WorkflowOrchestrationAgent._parse_decision_card_response(body)
        )
        self.assertEqual(issue, '')
        self.assertIn('Decision 1: Restart workers', md)
        self.assertNotIn('```json', md)  # JSON fence stripped from markdown
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0]['next_step_owner'], 'DevOps')

    def test_last_fence_wins_when_markdown_contains_code_block(self):
        """Markdown may contain incidental ``` ``` ``` fences (e.g. code samples in
        a Decision body); only the LAST JSON fence is the structured form."""
        body = (
            "### Decision 1: Fix the tool\n"
            "- **Decision:** Patch this:\n"
            "```python\nfoo = 1\n```\n"
            "- **Next step:** Claude — within 1 hour.\n\n"
            "```json\n"
            '{"decision_cards": [{"decision": "Patch", "recommendation": "Patch the bug.", '
            '"why_now": "Bug present.", "next_step_owner": "Claude", '
            '"next_step_deadline_style": "relative", "next_step_timebox": null}]}\n'
            "```\n"
        )
        md, cards, issue = (
            WorkflowOrchestrationAgent._parse_decision_card_response(body)
        )
        self.assertEqual(issue, '')
        # The python ``` fence stays in the markdown body
        self.assertIn('```python', md)
        # Only 1 structured card came through the JSON parse
        self.assertEqual(len(cards), 1)

    def test_bare_fence_without_json_lang_tag_still_parses(self):
        body = (
            "### Decision 1: X\n\n"
            "```\n"
            '{"decision_cards": []}\n'
            "```\n"
        )
        md, cards, issue = (
            WorkflowOrchestrationAgent._parse_decision_card_response(body)
        )
        self.assertEqual(issue, '')
        self.assertEqual(cards, [])

    def test_sentinel_response_with_empty_array(self):
        body = (
            "No urgent decisions today — monitor only.\n\n"
            "```json\n"
            '{"decision_cards": []}\n'
            "```\n"
        )
        md, cards, issue = (
            WorkflowOrchestrationAgent._parse_decision_card_response(body)
        )
        self.assertEqual(issue, '')
        self.assertIn('No urgent decisions today', md)
        self.assertEqual(cards, [])


class DecisionCardsStructuredValidatorTests(TestCase):

    REQUIRED_KEYS = (
        'decision', 'recommendation', 'why_now',
        'next_step_owner', 'next_step_deadline_style', 'next_step_timebox',
    )

    def _valid_card(self, **overrides):
        base = {
            'decision': 'Restart Celery workers',
            'recommendation': 'Do it now',
            'why_now': 'Workers wedged per Lane 1',
            'next_step_owner': 'DevOps',
            'next_step_deadline_style': 'relative',
            'next_step_timebox': None,
        }
        base.update(overrides)
        return base

    def test_empty_list_valid(self):
        self.assertEqual(
            WorkflowOrchestrationAgent._validate_decision_cards_structured([]),
            [],
        )

    def test_not_a_list_flagged(self):
        issues = WorkflowOrchestrationAgent._validate_decision_cards_structured(
            {'oops': True}
        )
        self.assertEqual(len(issues), 1)
        self.assertIn('not list', issues[0])

    def test_card_not_dict_flagged(self):
        issues = WorkflowOrchestrationAgent._validate_decision_cards_structured(
            ['not a dict']
        )
        self.assertTrue(any('not dict' in i for i in issues))

    def test_missing_required_keys_flagged(self):
        bad = {'decision': 'x'}
        issues = WorkflowOrchestrationAgent._validate_decision_cards_structured(
            [bad]
        )
        self.assertTrue(any('missing keys' in i for i in issues))

    def test_empty_string_field_flagged(self):
        bad = self._valid_card(decision='')
        issues = WorkflowOrchestrationAgent._validate_decision_cards_structured(
            [bad]
        )
        self.assertTrue(any('decision' in i and 'empty' in i for i in issues))

    def test_whitespace_only_field_flagged(self):
        bad = self._valid_card(recommendation='   ')
        issues = WorkflowOrchestrationAgent._validate_decision_cards_structured(
            [bad]
        )
        self.assertTrue(any('recommendation' in i and 'empty' in i for i in issues))

    def test_invalid_style_enum_flagged(self):
        bad = self._valid_card(next_step_deadline_style='asap')
        issues = WorkflowOrchestrationAgent._validate_decision_cards_structured(
            [bad]
        )
        self.assertTrue(any('next_step_deadline_style' in i for i in issues))

    def test_relative_style_with_non_null_timebox_flagged(self):
        bad = self._valid_card(
            next_step_deadline_style='relative',
            next_step_timebox='2026-06-28T11:00:00-06:00',
        )
        issues = WorkflowOrchestrationAgent._validate_decision_cards_structured(
            [bad]
        )
        self.assertTrue(any('must be null' in i for i in issues))

    def test_absolute_style_with_null_timebox_flagged(self):
        bad = self._valid_card(
            next_step_deadline_style='absolute',
            next_step_timebox=None,
        )
        issues = WorkflowOrchestrationAgent._validate_decision_cards_structured(
            [bad]
        )
        self.assertTrue(any('must be ISO-8601' in i for i in issues))

    def test_absolute_style_with_bad_format_flagged(self):
        bad = self._valid_card(
            next_step_deadline_style='absolute',
            next_step_timebox='tomorrow at 11am',
        )
        issues = WorkflowOrchestrationAgent._validate_decision_cards_structured(
            [bad]
        )
        self.assertTrue(any('ISO-8601' in i for i in issues))

    def test_absolute_style_with_valid_iso_offset_passes(self):
        good = self._valid_card(
            next_step_deadline_style='absolute',
            next_step_timebox='2026-06-28T11:00:00-06:00',
        )
        self.assertEqual(
            WorkflowOrchestrationAgent._validate_decision_cards_structured([good]),
            [],
        )

    def test_hybrid_style_with_valid_iso_offset_passes(self):
        good = self._valid_card(
            next_step_deadline_style='hybrid',
            next_step_timebox='2026-06-28T17:00:00-06:00',
        )
        self.assertEqual(
            WorkflowOrchestrationAgent._validate_decision_cards_structured([good]),
            [],
        )

    def test_iso_with_z_suffix_also_valid(self):
        good = self._valid_card(
            next_step_deadline_style='absolute',
            next_step_timebox='2026-06-28T17:00:00Z',
        )
        self.assertEqual(
            WorkflowOrchestrationAgent._validate_decision_cards_structured([good]),
            [],
        )

    def test_iso_with_fractional_seconds_also_valid(self):
        good = self._valid_card(
            next_step_deadline_style='absolute',
            next_step_timebox='2026-06-28T17:00:00.123456-06:00',
        )
        self.assertEqual(
            WorkflowOrchestrationAgent._validate_decision_cards_structured([good]),
            [],
        )

    def test_full_3_card_payload_all_valid(self):
        cards = [
            self._valid_card(),
            self._valid_card(
                decision='Unblock review queue',
                next_step_deadline_style='absolute',
                next_step_timebox='2026-06-28T17:00:00-06:00',
            ),
            self._valid_card(
                decision='Spin up ResearchAgent',
                next_step_deadline_style='hybrid',
                next_step_timebox='2026-06-30T09:00:00-06:00',
            ),
        ]
        self.assertEqual(
            WorkflowOrchestrationAgent._validate_decision_cards_structured(cards),
            [],
        )


class DecisionCardSynthesisStructuredFormIntegrationTests(TestCase):
    """End-to-end tests against ``_execute_decision_card_synthesis_step``
    with a mocked gpt-5-mini. Tests both the success path (structured
    form lands in context) and all known failure modes (JSON parse fail,
    structured validation fail, empty lanes)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=f'test_pathc_{uuid.uuid4().hex[:8]}',
            password='test',
        )

    def _make_agent_with_mocked_llm(self, mocked_content):
        agent = WorkflowOrchestrationAgent(user=self.user)
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = mocked_content
        mock_response.choices[0].finish_reason = 'stop'
        mock_client.chat.completions.create.return_value = mock_response
        return agent, mock_client

    def test_empty_lane_inputs_writes_sentinel_plus_empty_cards(self):
        agent = WorkflowOrchestrationAgent(user=self.user)
        ctx = {}
        result = agent._execute_decision_card_synthesis_step(ctx)
        self.assertTrue(result['success'])
        self.assertEqual(result['decision_cards'], [])
        self.assertIn('No urgent decisions', result['decision_card_text'])
        # Context should also carry both keys
        self.assertEqual(ctx['decision_cards'], [])
        self.assertIn('No urgent decisions', ctx['decision_card_text'])

    def test_success_path_populates_both_markdown_and_structured(self):
        mocked = (
            "### Decision 1: Restart Celery workers\n"
            "- **Decision:** Restart now.\n"
            "- **Recommendation:** Just do it.\n"
            "- **Why now:** Workers wedged per Lane 1.\n"
            "- **Next step:** DevOps — within 2 hours.\n\n"
            "```json\n"
            '{"decision_cards": [{"decision": "Restart now.", '
            '"recommendation": "Just do it.", "why_now": "Workers wedged per Lane 1.", '
            '"next_step_owner": "DevOps", "next_step_deadline_style": "relative", '
            '"next_step_timebox": null}]}\n'
            "```\n"
        )
        agent, mock_client = self._make_agent_with_mocked_llm(mocked)
        ctx = {'lane_1_text': 'lane 1', 'lane_2_text': 'lane 2'}
        with patch(
            'core.services.openai_client_factory.get_openai_client',
            return_value=mock_client,
        ):
            result = agent._execute_decision_card_synthesis_step(ctx)
        self.assertTrue(result['success'])
        # Markdown body present, JSON fence stripped
        self.assertIn('Decision 1: Restart Celery workers', result['decision_card_text'])
        self.assertNotIn('```json', result['decision_card_text'])
        # Structured form populated
        self.assertEqual(len(result['decision_cards']), 1)
        self.assertEqual(result['decision_cards'][0]['next_step_owner'], 'DevOps')
        self.assertEqual(result['decision_cards'][0]['next_step_deadline_style'], 'relative')
        self.assertIsNone(result['decision_cards'][0]['next_step_timebox'])
        # Context also has both
        self.assertEqual(ctx['decision_cards'], result['decision_cards'])

    def test_json_parse_failure_degrades_gracefully(self):
        """If LLM emits malformed JSON, ship markdown with decision_cards=[]."""
        mocked = (
            "### Decision 1: Fix it\n- **Decision:** X\n\n"
            "```json\n{ broken json }\n```\n"
        )
        agent, mock_client = self._make_agent_with_mocked_llm(mocked)
        ctx = {'lane_1_text': 'something'}
        with patch(
            'core.services.openai_client_factory.get_openai_client',
            return_value=mock_client,
        ):
            result = agent._execute_decision_card_synthesis_step(ctx)
        # Workflow does NOT fail
        self.assertTrue(result['success'])
        # Markdown ships
        self.assertIn('Decision 1: Fix it', result['decision_card_text'])
        # Structured form falls back to empty
        self.assertEqual(result['decision_cards'], [])
        # Diagnostic propagated
        self.assertIn('json decode', result['parse_issue'].lower())

    def test_structured_validation_failure_empties_cards_keeps_markdown(self):
        """If structured form parses but fails validation, empty it; markdown intact."""
        mocked = (
            "### Decision 1: X\n- **Decision:** Y\n\n"
            "```json\n"
            '{"decision_cards": [{"decision": "X", "recommendation": "Y", '
            '"why_now": "Z", "next_step_owner": "Someone", '
            '"next_step_deadline_style": "asap", "next_step_timebox": null}]}\n'
            "```\n"
        )
        agent, mock_client = self._make_agent_with_mocked_llm(mocked)
        ctx = {'lane_1_text': 'lane 1'}
        with patch(
            'core.services.openai_client_factory.get_openai_client',
            return_value=mock_client,
        ):
            result = agent._execute_decision_card_synthesis_step(ctx)
        self.assertTrue(result['success'])
        # Markdown kept
        self.assertIn('Decision 1: X', result['decision_card_text'])
        # Structured form emptied because 'asap' is not a valid style
        self.assertEqual(result['decision_cards'], [])
        # Issues surfaced in result for telemetry
        self.assertTrue(len(result['structured_issues']) > 0)

    def test_absolute_timebox_with_denver_offset_round_trip(self):
        """Verify a card with style=absolute + ISO Denver-offset timebox
        passes through cleanly. Tests the round-trip from LLM output →
        parse → validate → context."""
        mocked = (
            "### Decision 1: Wrap up reviews\n"
            "- **Next step:** Chris — by end of day today.\n\n"
            "```json\n"
            '{"decision_cards": [{"decision": "Wrap up reviews.", '
            '"recommendation": "Clear the queue.", "why_now": "Backlog growing.", '
            '"next_step_owner": "Chris", "next_step_deadline_style": "absolute", '
            '"next_step_timebox": "2026-06-27T17:00:00-06:00"}]}\n'
            "```\n"
        )
        agent, mock_client = self._make_agent_with_mocked_llm(mocked)
        ctx = {'lane_1_text': 'lane 1'}
        with patch(
            'core.services.openai_client_factory.get_openai_client',
            return_value=mock_client,
        ):
            result = agent._execute_decision_card_synthesis_step(ctx)
        self.assertTrue(result['success'])
        self.assertEqual(len(result['decision_cards']), 1)
        card = result['decision_cards'][0]
        self.assertEqual(card['next_step_deadline_style'], 'absolute')
        self.assertEqual(card['next_step_timebox'], '2026-06-27T17:00:00-06:00')
        self.assertEqual(result['structured_issues'], [])

    def test_markdown_prompt_no_longer_carries_absolute_clock_example(self):
        """Regression guard: the prompt must NOT seed the LLM with an
        'AM/PM MDT' example for the markdown body. Per Rigby S1242
        verdict, markdown deadlines should be RELATIVE; absolute lives
        in the JSON block only."""
        agent = WorkflowOrchestrationAgent(user=self.user)
        captured = []
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "### Decision 1: X\n```json\n{\"decision_cards\": []}\n```"
        )
        mock_response.choices[0].finish_reason = 'stop'

        def _capture(**kwargs):
            captured.append(kwargs['messages'][0]['content'])
            return mock_response

        mock_client.chat.completions.create.side_effect = _capture
        with patch(
            'core.services.openai_client_factory.get_openai_client',
            return_value=mock_client,
        ):
            agent._execute_decision_card_synthesis_step({'lane_1_text': 'l1'})

        self.assertEqual(len(captured), 1)
        prompt = captured[0]
        # Prompt MUST seed relative-deadline example (the EXAMPLE FORMAT
        # the LLM is instructed to follow for the markdown body).
        self.assertIn('RELATIVE timebox', prompt)
        self.assertIn('within 24 hours', prompt)
        # Prompt MUST instruct LLM to AVOID absolute clock format in
        # the markdown body (the negative-instruction rule). The phrase
        # "by 11:00 AM MDT" intentionally appears as a NEGATIVE example
        # — that's part of the rule text, not the format example.
        self.assertIn('Do NOT use absolute clock times in the markdown', prompt)
        # But the only place an absolute-format example may appear is in
        # the negative-instruction rule (not as the deadline format the
        # LLM should follow). Confirm there are no positive examples of
        # "by HH:MM AM/PM MDT" outside that one negative-instruction line.
        # Count occurrences — should be exactly 1 (the negative example).
        self.assertEqual(
            prompt.count('by 11:00 AM MDT'), 1,
            'Negative-example phrase should appear exactly once (in the rule),'
            ' not as a positive format example',
        )
        # Denver ISO offset IS exposed to LLM for the structured form
        # (typical formats: -06:00 in summer / -07:00 in winter).
        self.assertTrue(
            '-06:00' in prompt or '-07:00' in prompt,
            'Expected Denver ISO offset in prompt; not found',
        )

    def test_humanizer_still_fires_on_lane_1_text(self):
        """PR #2672 wired the humanizer into this step; Path C preserves it.
        Regression guard against accidentally dropping the humanizer call
        when restructuring the function."""
        agent = WorkflowOrchestrationAgent(user=self.user)
        captured = []
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "### Decision 1: X\n```json\n{\"decision_cards\": []}\n```"
        )
        mock_response.choices[0].finish_reason = 'stop'

        def _capture(**kwargs):
            captured.append(kwargs['messages'][0]['content'])
            return mock_response

        mock_client.chat.completions.create.side_effect = _capture
        with patch(
            'core.services.openai_client_factory.get_openai_client',
            return_value=mock_client,
        ):
            agent._execute_decision_card_synthesis_step({
                'lane_1_text': 'MUSCULAR subsystem WARNING: agents stalled',
                'lane_2_text': 'l2',
            })

        self.assertEqual(len(captured), 1)
        prompt = captured[0]
        # Humanized form present
        self.assertIn('agent-activity subsystem [MUSCULAR]', prompt)
        # Bare MUSCULAR not surfaced in lane_1 input section
        self.assertNotIn('MUSCULAR subsystem WARNING', prompt)
