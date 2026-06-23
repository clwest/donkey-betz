"""
Session 1211 — Phase B receipt_only pattern adoption across 3 new agents:

  - VideoEditingAgent (core/agents/video_editing_agent.py)
  - ImageEditingAgent (core/agents/image_editing_agent.py)
  - MeetingCoordinatorAgent (core/agents/executive/meeting_coordinator_agent.py)

Each agent now mirrors the CodeReviewAgent Phase B contract (Session 1210):
  - Static _is_receipt_only_mode(context) helper covers both signals
  - execute() short-circuits to a minimal v0 receipt when receipt_only
  - Receipt data shape lights up the URC Q1 predicate at
    core/services/urc_envelope.py:_is_skipped

Run:
    python manage.py test core.tests.test_phase_b_receipt_only_adopters -v2
"""

from contextlib import contextmanager
from unittest.mock import Mock

from django.test import SimpleTestCase

from core.agents.video_editing_agent import VideoEditingAgent
from core.agents.image_editing_agent import ImageEditingAgent
from core.agents.executive.meeting_coordinator_agent import MeetingCoordinatorAgent
from core.services.urc_envelope import compute_run_status, _is_skipped


# Per-agent: (agent_class, expected_message_fragment, expected_mode_key)
_ADOPTERS = [
    (VideoEditingAgent, 'video editing', 'VideoEditingAgent'),
    (ImageEditingAgent, 'image editing', 'ImageEditingAgent'),
    (MeetingCoordinatorAgent, 'meeting coordination', 'MeetingCoordinatorAgent'),
]


class _BaseReceiptOnlyAdoptionTests:
    """Shared assertions every Phase B adopter must satisfy.

    Subclasses bind ``agent_cls``, ``msg_fragment``, ``expected_name``.
    """

    agent_cls = None
    msg_fragment = ""
    expected_name = ""

    def _make_agent(self):
        """Build a bare agent instance with the side-effect methods mocked.

        The receipt_only path must not touch any of the mocked attrs — that's
        what AC-1 verifies. The normal-mode tests exercise the legacy path
        via the existing per-agent test files; here we only confirm that
        normal mode reaches the post-branch flow.
        """
        agent = self.agent_cls.__new__(self.agent_cls)
        agent.name = self.expected_name
        agent.agent_name = self.expected_name
        agent.user = None
        agent._tt_decision_count = 0
        agent._tt_decision_outcomes_marked = 0  # legacy guard

        agent._validate_task = Mock(return_value=True)
        agent._extract_spider_intelligence = Mock(return_value={'has_data': False})
        agent._build_intelligent_prompt = Mock(return_value="prompt")
        agent._call_openai = Mock(return_value={"tool_calls": []})
        agent._execute_tool_call = Mock()
        agent.record_decision = Mock()
        agent.mark_decision_outcome = Mock()
        agent._record_learning_outcome = Mock()
        agent._save_to_deliverable = Mock()
        agent._render_agent_output_markdown = Mock(return_value="rendered")

        self._tt_entered = False
        outer = self

        @contextmanager
        def _tt_session(*args, **kwargs):
            outer._tt_entered = True
            yield None

        agent.time_travel_session = _tt_session
        return agent

    # ── Detector helper ────────────────────────────────────────────

    def test_detector_mode_signal_triggers(self):
        self.assertTrue(
            self.agent_cls._is_receipt_only_mode({'mode': 'receipt_only'})
        )

    def test_detector_flag_signal_triggers(self):
        self.assertTrue(
            self.agent_cls._is_receipt_only_mode({'receipt_only': True})
        )

    def test_detector_truthy_but_not_true_does_not_trigger(self):
        self.assertFalse(
            self.agent_cls._is_receipt_only_mode({'receipt_only': 1})
        )
        self.assertFalse(
            self.agent_cls._is_receipt_only_mode({'receipt_only': 'yes'})
        )

    def test_detector_empty_or_none_does_not_trigger(self):
        self.assertFalse(self.agent_cls._is_receipt_only_mode({}))
        self.assertFalse(self.agent_cls._is_receipt_only_mode(None))

    def test_detector_other_mode_value_does_not_trigger(self):
        self.assertFalse(
            self.agent_cls._is_receipt_only_mode({'mode': 'something_else'})
        )

    # ── execute() AC-1: receipt_only short-circuits ────────────────

    def test_receipt_only_returns_skipped_receipt(self):
        agent = self._make_agent()
        result = agent.execute(
            task="capability ping",
            context={'mode': 'receipt_only'},
            scifi_context={},
            spider_context={},
        )
        self.assertTrue(result.success)
        self.assertIn(self.msg_fragment, result.message)
        self.assertTrue(result.data['skipped'])
        self.assertEqual(result.data['status'], 'skipped')
        self.assertEqual(result.data['mode'], 'receipt_only')
        self.assertEqual(result.tool_calls, [])
        self.assertEqual(result.decisions_made, 0)
        self.assertEqual(result.agent_name, self.expected_name)

    def test_receipt_only_skips_side_effects(self):
        """No LLM call, no spider extraction, no deliverable save, no
        time_travel_session entry — pure early return."""
        agent = self._make_agent()
        agent.execute(
            task="capability ping",
            context={'mode': 'receipt_only'},
            scifi_context={},
            spider_context={},
        )
        agent._call_openai.assert_not_called()
        agent._extract_spider_intelligence.assert_not_called()
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

    # ── execute() AC-3: normal mode still enters the existing flow ─

    def test_normal_mode_reaches_post_branch_flow(self):
        """Without receipt_only signals, execute() must continue past the
        early-return — proven by entering time_travel_session (or the
        spider intel call for MeetingCoordinatorAgent)."""
        agent = self._make_agent()
        try:
            agent.execute(
                task="real task",
                context={},
                scifi_context={},
                spider_context={},
            )
        except Exception:
            # The mocked agent might bail out further in (e.g., the real
            # _validate_task or LLM mock can produce weird flows); we only
            # care that the early-return did NOT fire — i.e., we reached
            # at least one post-branch side effect.
            pass
        # MeetingCoordinatorAgent extracts spider intel BEFORE
        # time_travel_session; the other two go straight into the session.
        # Either side effect is proof we passed the early-return.
        self.assertTrue(
            self._tt_entered or agent._extract_spider_intelligence.called,
            "normal mode did not reach any post-branch side effect — "
            "early-return is leaking into normal flow",
        )

    # ── URC Q1 predicate integration ───────────────────────────────

    def test_receipt_output_lights_up_q1_predicate(self):
        agent = self._make_agent()
        result = agent.execute(
            task="capability ping",
            context={'mode': 'receipt_only'},
            scifi_context={},
            spider_context={},
        )
        self.assertTrue(_is_skipped(result.success, result.data))

    def test_receipt_output_maps_to_run_status_skipped(self):
        agent = self._make_agent()
        result = agent.execute(
            task="capability ping",
            context={'mode': 'receipt_only'},
            scifi_context={},
            spider_context={},
        )
        status, reason = compute_run_status(
            result.success,
            result.error,
            result.data,
            {'mode': 'receipt_only'},
        )
        self.assertEqual(status, 'skipped')
        self.assertIsNone(reason)


class VideoEditingAgentReceiptOnlyTests(_BaseReceiptOnlyAdoptionTests, SimpleTestCase):
    agent_cls = VideoEditingAgent
    msg_fragment = 'video editing'
    expected_name = 'VideoEditingAgent'


class ImageEditingAgentReceiptOnlyTests(_BaseReceiptOnlyAdoptionTests, SimpleTestCase):
    agent_cls = ImageEditingAgent
    msg_fragment = 'image editing'
    expected_name = 'ImageEditingAgent'


class MeetingCoordinatorAgentReceiptOnlyTests(_BaseReceiptOnlyAdoptionTests, SimpleTestCase):
    agent_cls = MeetingCoordinatorAgent
    msg_fragment = 'meeting coordination'
    expected_name = 'MeetingCoordinatorAgent'
