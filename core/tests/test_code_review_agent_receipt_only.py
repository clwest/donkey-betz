"""
CodeReviewAgent receipt_only mode (URC v0.1 Phase B) — Session 1210.

Covers:
- AC-1: receipt_only mode returns success=True with data.skipped=True and
  no code inspection (no _call_openai, no time_travel_session entry).
- AC-3: Normal mode (no receipt_only signal) hits the existing code path
  — _call_openai IS invoked.
- Detection rule (Rigby sign-off): both context['mode']=='receipt_only'
  AND context.get('receipt_only') is True must trigger; other shapes
  must not.
- URC predicate integration: the receipt shape lights up the Q1
  predicate at core.services.urc_envelope._is_skipped, producing
  run_status='skipped' through compute_run_status.

Run:
    python manage.py test core.tests.test_code_review_agent_receipt_only -v2
"""

from contextlib import contextmanager
from unittest.mock import Mock

from django.test import SimpleTestCase

from core.agents.code_review_agent import CodeReviewAgent
from core.services.urc_envelope import compute_run_status, _is_skipped


class ReceiptOnlyModeDetectorTests(SimpleTestCase):
    """Helper detects the two signed-off signals; ignores everything else."""

    def test_mode_receipt_only_triggers(self):
        self.assertTrue(CodeReviewAgent._is_receipt_only_mode({'mode': 'receipt_only'}))

    def test_receipt_only_flag_true_triggers(self):
        self.assertTrue(CodeReviewAgent._is_receipt_only_mode({'receipt_only': True}))

    def test_both_signals_set_still_triggers(self):
        self.assertTrue(
            CodeReviewAgent._is_receipt_only_mode(
                {'mode': 'receipt_only', 'receipt_only': True}
            )
        )

    def test_mode_other_value_does_not_trigger(self):
        self.assertFalse(CodeReviewAgent._is_receipt_only_mode({'mode': 'normal'}))
        self.assertFalse(CodeReviewAgent._is_receipt_only_mode({'mode': 'outbound_pack'}))

    def test_receipt_only_truthy_but_not_true_does_not_trigger(self):
        # ``is True`` is intentional — strings/ints don't count.
        self.assertFalse(CodeReviewAgent._is_receipt_only_mode({'receipt_only': 1}))
        self.assertFalse(CodeReviewAgent._is_receipt_only_mode({'receipt_only': 'yes'}))

    def test_empty_context_does_not_trigger(self):
        self.assertFalse(CodeReviewAgent._is_receipt_only_mode({}))

    def test_none_context_does_not_trigger(self):
        self.assertFalse(CodeReviewAgent._is_receipt_only_mode(None))


class CodeReviewAgentReceiptOnlyExecuteTests(SimpleTestCase):
    """AC-1 + AC-3: execute() under receipt_only vs. normal mode."""

    def _make_agent(self):
        agent = CodeReviewAgent.__new__(CodeReviewAgent)
        agent.name = "CodeReviewAgent"
        agent.agent_name = "CodeReviewAgent"
        agent.user = None
        agent._tt_decision_count = 0

        # Mocks for the normal-mode path. The receipt_only path must
        # NOT touch these.
        agent._build_intelligent_prompt = Mock(return_value="prompt")
        agent._call_openai = Mock(return_value={"tool_calls": []})
        agent._execute_tool_call = Mock()
        agent.record_decision = Mock()
        agent.mark_decision_outcome = Mock()
        agent._record_learning_outcome = Mock()
        agent._save_to_deliverable = Mock()
        agent._render_agent_output_markdown = Mock(return_value="rendered")

        # time_travel_session sentinel — receipt_only returns BEFORE
        # this context manager opens, so the entered flag stays False.
        self._tt_entered = False
        outer = self

        @contextmanager
        def _tt_session(*args, **kwargs):
            outer._tt_entered = True
            yield None

        agent.time_travel_session = _tt_session
        return agent

    # ── AC-1: receipt_only mode short-circuits ─────────────────────

    def test_receipt_only_mode_returns_skipped_receipt(self):
        agent = self._make_agent()
        result = agent.execute(
            task="capability ping",
            context={'mode': 'receipt_only'},
            scifi_context={},
            spider_context={},
        )
        self.assertTrue(result.success)
        self.assertEqual(
            result.message,
            'receipt_only mode — no code inspection performed',
        )
        self.assertTrue(result.data['skipped'])
        self.assertEqual(result.data['status'], 'skipped')
        self.assertEqual(result.data['mode'], 'receipt_only')
        self.assertEqual(result.tool_calls, [])
        self.assertEqual(result.decisions_made, 0)
        self.assertEqual(result.agent_name, 'CodeReviewAgent')

    def test_receipt_only_mode_skips_openai_and_time_travel(self):
        """No LLM call, no time_travel_session entry — pure early return."""
        agent = self._make_agent()
        agent.execute(
            task="capability ping",
            context={'mode': 'receipt_only'},
            scifi_context={},
            spider_context={},
        )
        agent._call_openai.assert_not_called()
        agent._build_intelligent_prompt.assert_not_called()
        agent._save_to_deliverable.assert_not_called()
        agent._record_learning_outcome.assert_not_called()
        self.assertFalse(self._tt_entered)

    def test_receipt_only_flag_signal_also_works(self):
        agent = self._make_agent()
        result = agent.execute(
            task="capability ping",
            context={'receipt_only': True},
            scifi_context={},
            spider_context={},
        )
        self.assertTrue(result.success)
        self.assertTrue(result.data['skipped'])
        agent._call_openai.assert_not_called()

    # ── AC-3: Normal mode is untouched ─────────────────────────────

    def test_normal_mode_still_enters_inspection_path(self):
        """Without receipt_only signals, execute() must reach _call_openai
        and enter time_travel_session — i.e., no regression from Phase B."""
        agent = self._make_agent()
        agent.execute(
            task="Review core/example.py",
            context={},
            scifi_context={},
            spider_context={},
        )
        agent._call_openai.assert_called_once()
        self.assertTrue(self._tt_entered)

    def test_normal_mode_with_other_mode_value_still_enters_inspection(self):
        agent = self._make_agent()
        agent.execute(
            task="Review core/example.py",
            context={'mode': 'something_else'},
            scifi_context={},
            spider_context={},
        )
        agent._call_openai.assert_called_once()


class ReceiptOnlyOutputMapsToUrcSkippedTests(SimpleTestCase):
    """The receipt shape must light up the URC Q1 predicate end-to-end.

    Without this guarantee, AC-2 (post-fix smoke flips run_status from
    'error' to 'skipped') silently fails — the agent's output_data lands
    in AgentExecution but the URC envelope writes 'success' instead.
    """

    def _build_agent_output_data(self):
        agent = CodeReviewAgent.__new__(CodeReviewAgent)
        agent.name = "CodeReviewAgent"
        agent.agent_name = "CodeReviewAgent"
        agent.user = None
        agent._tt_decision_count = 0
        agent._build_intelligent_prompt = Mock()
        agent._call_openai = Mock()
        agent.time_travel_session = lambda *a, **kw: _NoopCM()

        result = agent.execute(
            task="capability ping",
            context={'mode': 'receipt_only'},
            scifi_context={},
            spider_context={},
        )
        return result

    def test_is_skipped_predicate_fires_on_agent_receipt(self):
        result = self._build_agent_output_data()
        self.assertTrue(_is_skipped(result.success, result.data))

    def test_compute_run_status_returns_skipped(self):
        result = self._build_agent_output_data()
        status, reason = compute_run_status(
            result.success,
            result.error,
            result.data,
            {'mode': 'receipt_only'},
        )
        self.assertEqual(status, 'skipped')
        self.assertIsNone(reason)


class _NoopCM:
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        return False
