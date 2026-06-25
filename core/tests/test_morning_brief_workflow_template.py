"""Session 1232 Sub-step B + Session 1233 B.1 — morning_brief workflow tests.

Three concentric layers of coverage:

1. **Template shape contract** (locked at Session 1232 PR #2597, updated
   for B.1 internal handler renames). Fails loudly if the template drifts
   from spec.
2. **Internal handler behavior** (new in Session 1233 B.1 PR). Tests the
   three new workflow-internal handlers: ``lane_4_rotating_focus``,
   ``decision_card_synthesis``, ``create_morning_brief_deliverable``.
3. **Plumbing contract**: ``_update_context`` writes ``lane_N_text`` from
   step results so synthesis can read them.

Sub-step B.2 (next PR) ships ``rotation_slot_resolve`` pre-step + override
triggers; tests for those land alongside that PR.

Run::

    python manage.py test core.tests.test_morning_brief_workflow_template -v2
"""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from core.agents.workflow_orchestration_agent import AVAILABLE_WORKFLOWS
from core.services.workflow_orchestration_agent import WorkflowOrchestrationAgent


class MorningBriefWorkflowTemplateTests(SimpleTestCase):
    """Lock the workflow template against the spec.

    Session 1233 B.1 update: lane_4_rotating_focus, decision_card_synthesis,
    and create_deliverable agents flipped to dedicated internal handlers.
    """

    EXPECTED_STEP_NAMES = [
        'lane_1_platform_readiness',
        'lane_2_build_focus',
        'lane_3_competitive_landscape',
        'lane_4_rotating_focus',
        'decision_card_synthesis',
        'strategic_synthesis',
        'create_deliverable',
    ]

    EXPECTED_AGENTS_BY_STEP = {
        'lane_1_platform_readiness': 'system_intelligence_agent',
        'lane_2_build_focus': 'coo_agent',
        'lane_3_competitive_landscape': 'trend_analysis_agent',
        # Session 1233 B.1: was 'research_agent' (v0 placeholder); now internal handler.
        'lane_4_rotating_focus': 'lane_4_rotating_focus',
        # Session 1233 B.1: was 'coo_agent' (v0 placeholder); now internal handler.
        'decision_card_synthesis': 'decision_card_synthesis',
        'strategic_synthesis': 'strategic_synthesis',
        # Session 1233 B.1: was 'create_project_from_research' (v0 placeholder); now internal handler.
        'create_deliverable': 'create_morning_brief_deliverable',
    }

    def test_morning_brief_registered_in_available_workflows(self):
        self.assertIn('morning_brief', AVAILABLE_WORKFLOWS,
                      "morning_brief must be in AVAILABLE_WORKFLOWS so the "
                      "wrapper exposes it to the workflow runner.")

    def test_morning_brief_in_workflows_dict(self):
        self.assertIn('morning_brief', WorkflowOrchestrationAgent.WORKFLOWS,
                      "morning_brief must be defined in the legacy "
                      "WORKFLOWS dict — that's the source of truth for "
                      "step-by-step dispatch.")

    def test_morning_brief_has_no_image_generation_flag(self):
        wf = WorkflowOrchestrationAgent.WORKFLOWS['morning_brief']
        self.assertTrue(
            wf.get('no_image_generation', False),
            "morning_brief is a research/synthesis workflow — must have "
            "no_image_generation=True to skip image steps in the runner."
        )

    def test_morning_brief_has_seven_steps(self):
        wf = WorkflowOrchestrationAgent.WORKFLOWS['morning_brief']
        steps = wf['steps']
        self.assertEqual(
            len(steps), 7,
            f"Spec requires 7 steps in v0 (4 lanes + decision_card_synthesis "
            f"+ strategic_synthesis + create_deliverable). Got {len(steps)}."
        )

    def test_morning_brief_step_names_match_spec(self):
        wf = WorkflowOrchestrationAgent.WORKFLOWS['morning_brief']
        actual_names = [step['name'] for step in wf['steps']]
        self.assertEqual(
            actual_names, self.EXPECTED_STEP_NAMES,
            "Step names must match spec order. If you're reordering, "
            "update docs/MORNING_BRIEF_SPEC.md § 'Workflow template skeleton' "
            "in the same PR."
        )

    def test_morning_brief_step_agents_match_spec(self):
        wf = WorkflowOrchestrationAgent.WORKFLOWS['morning_brief']
        for step in wf['steps']:
            expected = self.EXPECTED_AGENTS_BY_STEP[step['name']]
            self.assertEqual(
                step['agent'], expected,
                f"Step '{step['name']}' agent must be '{expected}' per spec. "
                f"Got '{step['agent']}'. If intentional, update the spec doc "
                f"in the same PR."
            )

    def test_morning_brief_step_numbers_are_sequential(self):
        wf = WorkflowOrchestrationAgent.WORKFLOWS['morning_brief']
        step_numbers = [step['step'] for step in wf['steps']]
        self.assertEqual(
            step_numbers, list(range(1, 8)),
            "Steps must be numbered 1-7 sequentially. Workflow runner "
            "respects step['step'] order."
        )

    def test_morning_brief_uses_strategic_synthesis_handler(self):
        """Session 1231 PR #2592 added workflow-internal handler for
        strategic_synthesis. morning_brief must reference that handler
        by name (not a fake AGENT_MAP entry) for the synthesis step."""
        wf = WorkflowOrchestrationAgent.WORKFLOWS['morning_brief']
        synth_step = next(
            (s for s in wf['steps'] if s['name'] == 'strategic_synthesis'),
            None,
        )
        self.assertIsNotNone(synth_step,
                             "strategic_synthesis step must exist.")
        self.assertEqual(
            synth_step['agent'], 'strategic_synthesis',
            "strategic_synthesis step must dispatch via the "
            "workflow-internal handler from PR #2592 (not a renamed agent)."
        )

    def test_morning_brief_uses_dedicated_deliverable_handler(self):
        """Session 1233 B.1: Step 7 now dispatches to the dedicated
        ``create_morning_brief_deliverable`` internal handler instead of
        the v0 ``create_project_from_research`` placeholder."""
        wf = WorkflowOrchestrationAgent.WORKFLOWS['morning_brief']
        deliv_step = next(
            (s for s in wf['steps'] if s['name'] == 'create_deliverable'),
            None,
        )
        self.assertIsNotNone(deliv_step,
                             "create_deliverable step must exist.")
        self.assertEqual(
            deliv_step['agent'], 'create_morning_brief_deliverable',
            "create_deliverable step must dispatch via the dedicated "
            "create_morning_brief_deliverable internal handler "
            "(Session 1233 B.1). If you're reverting this, update the spec "
            "doc in the same PR."
        )

    def test_morning_brief_content_type_is_morning_brief(self):
        wf = WorkflowOrchestrationAgent.WORKFLOWS['morning_brief']
        self.assertEqual(
            wf.get('content_type'), 'morning_brief',
            "content_type='morning_brief' is the workspace category tag."
        )


class MorningBriefSynthesisModeTests(SimpleTestCase):
    """Session 1233 B.1 — strategic_synthesis branch on _synthesis_mode."""

    def setUp(self):
        self.agent = WorkflowOrchestrationAgent(user=MagicMock(name='user'))

    def test_morning_brief_synthesis_keys_includes_lane_keys(self):
        keys = WorkflowOrchestrationAgent._MORNING_BRIEF_SYNTHESIS_KEYS
        for required in (
            'lane_1_text', 'lane_2_text', 'lane_3_text',
            'lane_4_text', 'decision_card_text',
        ):
            self.assertIn(required, keys,
                          f"_MORNING_BRIEF_SYNTHESIS_KEYS must include "
                          f"{required!r} so strategic_synthesis can read it "
                          f"in morning_brief mode.")

    def test_default_synthesis_keys_unchanged_from_F7(self):
        """B.1 must not regress the Session 1231 F7 default synthesis path
        used by business_research and startup_validation."""
        keys = WorkflowOrchestrationAgent._SYNTHESIS_CONTEXT_KEYS
        for required in (
            'research_summary', 'competitor_insights', 'customer_insights',
        ):
            self.assertIn(required, keys,
                          f"Default synthesis must still include {required!r}")

    def test_empty_morning_brief_context_returns_graceful_no_op(self):
        """Smoke / capability-ping case: morning_brief mode with no lane
        outputs returns success without LLM call."""
        result = self.agent._execute_strategic_synthesis_step({
            '_synthesis_mode': 'morning_brief',
        })
        self.assertTrue(result['success'])
        self.assertEqual(result.get('inputs_used'), [])


class MorningBriefLane4DispatchTests(SimpleTestCase):
    """Session 1233 B.1 — lane_4_rotating_focus slot-driven dispatch."""

    def setUp(self):
        self.agent = WorkflowOrchestrationAgent(user=MagicMock(name='user'))

    def test_lane_4_slot_agent_map_covers_5_spec_slots(self):
        slot_map = WorkflowOrchestrationAgent._MORNING_BRIEF_LANE_4_SLOT_AGENT
        for required in (
            'sports_edge_scan', 'prediction_markets',
            'ticker_catalyst_watch', 'gtm_pipeline_health',
            'ai_infra_deep_dive',
        ):
            self.assertIn(required, slot_map,
                          f"Lane 4 slot map must cover {required!r} per spec "
                          f"§ Lane 4 Rotation Schedule.")

    def test_lane_4_default_slot_is_ai_infra_deep_dive(self):
        self.assertEqual(
            WorkflowOrchestrationAgent._MORNING_BRIEF_LANE_4_DEFAULT_SLOT,
            'ai_infra_deep_dive',
            "B.1 default slot must be 'ai_infra_deep_dive' (Monday slot) "
            "until B.2 ships rotation_slot_resolve pre-step."
        )

    @patch('core.agent_router.AgentRouter')
    def test_lane_4_dispatches_default_slot_when_no_rotation_slot(
        self, mock_router_cls,
    ):
        mock_router = mock_router_cls.return_value
        mock_router.AGENT_MAP = {'ResearchAgent': object()}
        mock_result = MagicMock(
            success=True, message='AI infra brief text', data={'k': 'v'},
        )
        mock_router.route.return_value = mock_result

        result = self.agent._execute_lane_4_rotating_focus_step({})

        self.assertTrue(result['success'])
        self.assertEqual(result['slot_used'], 'ai_infra_deep_dive')
        mock_router.route.assert_called_once()
        args, _ = mock_router.route.call_args
        self.assertEqual(args[0], 'ResearchAgent',
                         "Default slot ai_infra_deep_dive → ResearchAgent")

    @patch('core.agent_router.AgentRouter')
    def test_lane_4_dispatches_sports_slot_when_set(self, mock_router_cls):
        mock_router = mock_router_cls.return_value
        mock_router.AGENT_MAP = {'SharpActionDetector': object()}
        mock_router.route.return_value = MagicMock(
            success=True, message='sports edge text', data={},
        )

        result = self.agent._execute_lane_4_rotating_focus_step({
            'rotation_slot': 'sports_edge_scan',
        })

        self.assertEqual(result['slot_used'], 'sports_edge_scan')
        args, _ = mock_router.route.call_args
        self.assertEqual(args[0], 'SharpActionDetector')

    @patch('core.agent_router.AgentRouter')
    def test_lane_4_falls_back_to_default_on_unknown_slot(
        self, mock_router_cls,
    ):
        mock_router = mock_router_cls.return_value
        mock_router.AGENT_MAP = {'ResearchAgent': object()}
        mock_router.route.return_value = MagicMock(
            success=True, message='fallback', data={},
        )

        result = self.agent._execute_lane_4_rotating_focus_step({
            'rotation_slot': 'made_up_slot_xyz',
        })

        # Falls back to ai_infra_deep_dive default
        self.assertEqual(result['slot_used'], 'ai_infra_deep_dive')


class MorningBriefDecisionCardTests(SimpleTestCase):
    """Session 1233 B.1 — decision_card_synthesis empty-context behavior."""

    def setUp(self):
        self.agent = WorkflowOrchestrationAgent(user=MagicMock(name='user'))

    def test_empty_lanes_returns_sentinel(self):
        """Smoke probe / capability-ping: no lane outputs → sentinel."""
        context = {}
        result = self.agent._execute_decision_card_synthesis_step(context)
        self.assertTrue(result['success'])
        self.assertIn('monitor only', result['decision_card_text'].lower())
        # Verify the handler wrote to context (so _update_context can capture).
        self.assertEqual(context['decision_card_text'],
                         result['decision_card_text'])


class MorningBriefContextPlumbingTests(SimpleTestCase):
    """Session 1233 B.1 — _update_context lane_N_text plumbing."""

    def setUp(self):
        self.agent = WorkflowOrchestrationAgent(user=MagicMock(name='user'))

    def test_lane_1_step_result_captured_to_context(self):
        context = {}
        self.agent._update_context(
            'lane_1_platform_readiness',
            {'success': True, 'output': 'platform healthy', 'data': {'a': 1}},
            context,
        )
        self.assertEqual(context['lane_1_text'], 'platform healthy')
        self.assertEqual(context['lane_1_data'], {'a': 1})

    def test_lane_2_step_result_captured_to_context(self):
        context = {}
        self.agent._update_context(
            'lane_2_build_focus',
            {'success': True, 'output': 'shipped 3 PRs'},
            context,
        )
        self.assertEqual(context['lane_2_text'], 'shipped 3 PRs')

    def test_lane_3_step_result_captured_to_context(self):
        context = {}
        self.agent._update_context(
            'lane_3_competitive_landscape',
            {'success': True, 'output': 'OpenAI shipped operator agent'},
            context,
        )
        self.assertEqual(context['lane_3_text'],
                         'OpenAI shipped operator agent')

    def test_lane_4_step_result_captured_plus_slot_used(self):
        context = {'rotation_slot': 'sports_edge_scan'}
        self.agent._update_context(
            'lane_4_rotating_focus',
            {'success': True, 'output': 'sharp action on NBA',
             'slot_used': 'sports_edge_scan'},
            context,
        )
        self.assertEqual(context['lane_4_text'], 'sharp action on NBA')
        self.assertEqual(context['lane_4_slot_used'], 'sports_edge_scan')

    def test_decision_card_result_captured_to_context(self):
        context = {}
        self.agent._update_context(
            'decision_card_synthesis',
            {'success': True, 'decision_card_text': '### Decision 1: …'},
            context,
        )
        self.assertEqual(context['decision_card_text'],
                         '### Decision 1: …')

    def test_lane_step_with_summary_fallback(self):
        """If result has no 'output' but has 'summary', use that."""
        context = {}
        self.agent._update_context(
            'lane_1_platform_readiness',
            {'success': True, 'summary': 'all systems green'},
            context,
        )
        self.assertEqual(context['lane_1_text'], 'all systems green')
