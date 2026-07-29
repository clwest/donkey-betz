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

    # Session 1233 B.2: rotation_slot_resolve added as Step 1 pre-step;
    # all subsequent steps shifted from 1-7 to 2-8.
    EXPECTED_STEP_NAMES = [
        'rotation_slot_resolve',
        'lane_1_platform_readiness',
        'lane_2_build_focus',
        'lane_3_competitive_landscape',
        'lane_4_rotating_focus',
        'decision_card_synthesis',
        'strategic_synthesis',
        'create_deliverable',
    ]

    EXPECTED_AGENTS_BY_STEP = {
        # Session 1233 B.2: internal pure-logic handler.
        'rotation_slot_resolve': 'rotation_slot_resolve',
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

    def test_morning_brief_has_eight_steps(self):
        wf = WorkflowOrchestrationAgent.WORKFLOWS['morning_brief']
        steps = wf['steps']
        self.assertEqual(
            len(steps), 8,
            f"Session 1233 B.2: spec requires 8 steps "
            f"(rotation_slot_resolve pre-step + 4 lanes + "
            f"decision_card_synthesis + strategic_synthesis + "
            f"create_deliverable). Got {len(steps)}."
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
            step_numbers, list(range(1, 9)),
            "Session 1233 B.2: steps must be numbered 1-8 sequentially "
            "(rotation_slot_resolve added as Step 1). Workflow runner "
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
    def test_lane_4_dispatches_monday_default_when_no_rotation_slot(
        self, mock_router_cls,
    ):
        """Session 1233 B.2: when neither rotation_slot nor override is
        set, Lane 4 falls back through _resolve_rotation_slot which
        uses the current weekday. Forcing Monday via _get_now_utc mock
        verifies Lane 4's fallback chain chains through to the weekday
        resolver instead of using a static default."""
        mock_router = mock_router_cls.return_value
        mock_router.AGENT_MAP = {'ResearchAgent': object()}
        mock_router.route.return_value = MagicMock(
            success=True, message='AI infra brief text', data={'k': 'v'},
        )

        # Force Monday via the test seam.
        mock_now = MagicMock()
        mock_now.weekday.return_value = 0
        mock_now.isocalendar.return_value = (2026, 1, 1)
        with patch.object(self.agent, '_get_now_utc', return_value=mock_now):
            result = self.agent._execute_lane_4_rotating_focus_step({})

        self.assertTrue(result['success'])
        self.assertEqual(result['slot_used'], 'ai_infra_deep_dive')
        mock_router.route.assert_called_once()
        args, _ = mock_router.route.call_args
        self.assertEqual(args[0], 'ResearchAgent',
                         "Monday default ai_infra_deep_dive → ResearchAgent")

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


class MorningBriefLane4FailLoudTests(SimpleTestCase):
    """Session 1234 D1 — lane_4 fail-loud regression guard.

    The 2026-06-25 first-fire postmortem (task 9d00907a-…) showed
    ``_execute_lane_4_rotating_focus_step`` returning ``{'success': False}``
    with no ``error`` field when ``OpportunityPipelineAgent`` reported
    falsy success. The orchestrator at workflow_orchestration_agent.py:1271
    then logged a generic "Unknown error". These tests lock in the fix:
    on falsy success, the return dict ALWAYS includes a populated ``error``
    field and an ``agent_name`` field for downstream log context.
    """

    def setUp(self):
        self.agent = WorkflowOrchestrationAgent(user=MagicMock(name='user'))

    @patch('core.agent_router.AgentRouter')
    def test_falsy_success_with_result_error_captures_error_string(
        self, mock_router_cls,
    ):
        mock_router = mock_router_cls.return_value
        mock_router.AGENT_MAP = {'COOAgent': object()}
        mock_router.route.return_value = MagicMock(
            success=False, message='', data={},
            error='upstream agent timed out',
        )

        result = self.agent._execute_lane_4_rotating_focus_step({
            'rotation_slot': 'gtm_pipeline_health',
        })

        self.assertFalse(result['success'])
        self.assertIn('error', result,
                      "Falsy-success path MUST populate 'error' field.")
        self.assertIn('upstream agent timed out', result['error'])
        self.assertIn('COOAgent', result['error'])
        self.assertIn("'gtm_pipeline_health'", result['error'])
        self.assertEqual(result['agent_name'], 'COOAgent')
        self.assertEqual(result['slot_used'], 'gtm_pipeline_health')

    @patch('core.agent_router.AgentRouter')
    def test_falsy_success_falls_through_to_message(self, mock_router_cls):
        mock_router = mock_router_cls.return_value
        mock_router.AGENT_MAP = {'COOAgent': object()}
        # No .error attribute on the mock result — must fall through to message
        mock_result = MagicMock(spec=['success', 'message', 'data'])
        mock_result.success = False
        mock_result.message = 'partial output before failure'
        mock_result.data = {}
        mock_router.route.return_value = mock_result

        result = self.agent._execute_lane_4_rotating_focus_step({
            'rotation_slot': 'gtm_pipeline_health',
        })

        self.assertFalse(result['success'])
        self.assertIn('partial output before failure', result['error'])

    @patch('core.agent_router.AgentRouter')
    def test_falsy_success_with_no_diagnostics_uses_structured_fallback(
        self, mock_router_cls,
    ):
        """The exact 2026-06-25 first-fire shape: agent returned an object
        with success=False and no error/message/output. Before D1 this
        produced 'Unknown error' at the orchestrator. After D1 the handler
        must produce a diagnostic string identifying the agent + result type.
        """
        mock_router = mock_router_cls.return_value
        mock_router.AGENT_MAP = {'COOAgent': object()}
        mock_result = MagicMock(spec=['success', 'message', 'data'])
        mock_result.success = False
        mock_result.message = ''
        mock_result.data = {}
        mock_router.route.return_value = mock_result

        result = self.agent._execute_lane_4_rotating_focus_step({
            'rotation_slot': 'gtm_pipeline_health',
        })

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('COOAgent', result['error'])
        self.assertIn('no error/message/output', result['error'])
        # MUST NOT be the generic orchestrator-level "Unknown error"
        self.assertNotIn('Unknown error', result['error'])

    @patch('core.agent_router.AgentRouter')
    def test_router_route_exception_captures_exception_type(
        self, mock_router_cls,
    ):
        mock_router = mock_router_cls.return_value
        mock_router.AGENT_MAP = {'COOAgent': object()}
        mock_router.route.side_effect = ValueError('contextual oops')

        result = self.agent._execute_lane_4_rotating_focus_step({
            'rotation_slot': 'gtm_pipeline_health',
        })

        self.assertFalse(result['success'])
        self.assertIn('ValueError', result['error'])
        self.assertIn('contextual oops', result['error'])
        self.assertEqual(result['agent_name'], 'COOAgent')
        self.assertEqual(result['slot_used'], 'gtm_pipeline_health')

    @patch('core.agent_router.AgentRouter')
    def test_agent_not_in_agent_map_includes_agent_name_in_return(
        self, mock_router_cls,
    ):
        mock_router = mock_router_cls.return_value
        # Empty AGENT_MAP — slot resolves to an agent that doesn't exist.
        mock_router.AGENT_MAP = {}

        result = self.agent._execute_lane_4_rotating_focus_step({
            'rotation_slot': 'gtm_pipeline_health',
        })

        self.assertFalse(result['success'])
        self.assertIn('not in AGENT_MAP', result['error'])
        self.assertEqual(result['agent_name'], 'COOAgent')

    @patch('core.agent_router.AgentRouter')
    def test_successful_dispatch_still_includes_agent_name(
        self, mock_router_cls,
    ):
        """Regression guard: agent_name field must be present on success too."""
        mock_router = mock_router_cls.return_value
        mock_router.AGENT_MAP = {'COOAgent': object()}
        mock_router.route.return_value = MagicMock(
            success=True, message='gtm signal text', data={'k': 'v'},
        )

        result = self.agent._execute_lane_4_rotating_focus_step({
            'rotation_slot': 'gtm_pipeline_health',
        })

        self.assertTrue(result['success'])
        self.assertEqual(result['agent_name'], 'COOAgent')
        self.assertEqual(result['slot_used'], 'gtm_pipeline_health')


class MorningBriefLane4D2SlotReassignmentTests(SimpleTestCase):
    """Session 1234 D2 — Lane 4 slot→agent reassignment + per-slot prompts.

    D2 P1.A (Rigby-ratified): ``gtm_pipeline_health`` remapped from
    ``OpportunityPipelineAgent`` (which required ``context['opportunity']``,
    incompatible with Lane 4's daily-summary contract) to ``COOAgent``
    (no required context keys). Persona duplication with Lane 2 mitigated
    via ``_MORNING_BRIEF_LANE_4_SLOT_FOCUS`` per-slot focus phrases.
    """

    def setUp(self):
        self.agent = WorkflowOrchestrationAgent(user=MagicMock(name='user'))

    def test_gtm_pipeline_health_routes_to_coo_agent(self):
        """Regression guard against re-introducing OpportunityPipelineAgent."""
        slot_map = WorkflowOrchestrationAgent._MORNING_BRIEF_LANE_4_SLOT_AGENT
        self.assertEqual(slot_map['gtm_pipeline_health'], 'COOAgent',
                         "D2 P1.A: gtm_pipeline_health MUST route to COOAgent. "
                         "Was OpportunityPipelineAgent pre-D2 — that agent "
                         "requires context['opportunity'] which Lane 4 cannot "
                         "supply. Reverting will break the workflow.")

    def test_slot_focus_map_covers_all_5_slots(self):
        focus_map = WorkflowOrchestrationAgent._MORNING_BRIEF_LANE_4_SLOT_FOCUS
        for required in (
            'sports_edge_scan', 'prediction_markets',
            'ticker_catalyst_watch', 'gtm_pipeline_health',
            'ai_infra_deep_dive',
        ):
            self.assertIn(required, focus_map,
                          f"Per-slot focus map missing entry for {required!r}. "
                          f"Without it, Lane 4 uses a generic prompt that "
                          f"may collide with other lanes' content.")

    def test_gtm_focus_phrase_differentiates_from_lane_2(self):
        """The gtm focus phrase MUST explicitly exclude Lane 2's territory
        so COOAgent (shared by Lane 2 + Lane 4) produces distinct output."""
        focus = WorkflowOrchestrationAgent._MORNING_BRIEF_LANE_4_SLOT_FOCUS[
            'gtm_pipeline_health']
        self.assertIn('Lane 2', focus,
                      "GTM focus phrase MUST reference Lane 2 to make the "
                      "boundary explicit (Rigby's D2 design contract).")
        self.assertIn('pipeline', focus.lower())

    @patch('core.agent_router.AgentRouter')
    def test_lane_4_step_task_includes_gtm_focus_for_gtm_slot(
        self, mock_router_cls,
    ):
        mock_router = mock_router_cls.return_value
        mock_router.AGENT_MAP = {'COOAgent': object()}
        mock_router.route.return_value = MagicMock(
            success=True, message='gtm bullets', data={},
        )

        self.agent._execute_lane_4_rotating_focus_step({
            'rotation_slot': 'gtm_pipeline_health',
        })

        args, _ = mock_router.route.call_args
        dispatched_task = args[1]
        self.assertIn('gtm_pipeline_health', dispatched_task)
        # Verify the gtm-specific focus phrase made it into the dispatch
        self.assertIn('KPI', dispatched_task)


class MorningBriefLane4SentinelTests(SimpleTestCase):
    """Session 1234 D2 P2.C — Lane 4 fail-soft sentinel.

    When Lane 4 fails (no upstream data, agent contract mismatch, ambient
    dispatch error), the workflow continues and the brief ships with a
    sentinel as the Lane 4 section. ``_update_context`` reads ``result['output']``
    into ``context['lane_4_text']``; synthesis renders it as the Lane 4
    paragraph. Loud-but-non-blocking: orchestrator emits
    ``[MORNING_BRIEF_LANE_4_NONCRITICAL_FAIL]`` log line, doesn't halt.
    """

    def setUp(self):
        self.agent = WorkflowOrchestrationAgent(user=MagicMock(name='user'))

    def test_sentinel_helper_renders_short_paragraph(self):
        sentinel = WorkflowOrchestrationAgent._lane_4_sentinel(
            'gtm_pipeline_health', 'Kalshi spider returned no data',
        )
        self.assertIn('gtm pipeline health', sentinel)
        self.assertIn('No signal today', sentinel)
        self.assertIn('Kalshi spider returned no data', sentinel)

    def test_sentinel_truncates_long_error_excerpts(self):
        long_error = 'x' * 1000
        sentinel = WorkflowOrchestrationAgent._lane_4_sentinel(
            'sports_edge_scan', long_error,
        )
        # Sentinel total bounded; 240-char excerpt limit guards against
        # multi-page error dumps polluting the brief.
        self.assertLess(len(sentinel), 400)
        self.assertIn('...', sentinel)

    def test_sentinel_handles_empty_error_gracefully(self):
        sentinel = WorkflowOrchestrationAgent._lane_4_sentinel(
            'prediction_markets', '',
        )
        self.assertIn('no detail captured', sentinel)
        self.assertIn('prediction markets', sentinel)

    @patch('core.agent_router.AgentRouter')
    def test_falsy_success_populates_output_with_sentinel(
        self, mock_router_cls,
    ):
        """On falsy success with no agent output, the handler's return
        dict MUST have an 'output' field containing the sentinel — so
        ``_update_context`` writes it to ``context['lane_4_text']``."""
        mock_router = mock_router_cls.return_value
        mock_router.AGENT_MAP = {'COOAgent': object()}
        mock_result = MagicMock(spec=['success', 'message', 'data'])
        mock_result.success = False
        mock_result.message = ''  # No output from agent
        mock_result.data = {}
        mock_router.route.return_value = mock_result

        result = self.agent._execute_lane_4_rotating_focus_step({
            'rotation_slot': 'gtm_pipeline_health',
        })

        self.assertFalse(result['success'])
        # output MUST contain sentinel — synthesis will pick it up
        self.assertIn('output', result)
        self.assertIn('No signal today', result['output'])
        self.assertIn('gtm pipeline health', result['output'])

    @patch('core.agent_router.AgentRouter')
    def test_router_route_exception_also_populates_sentinel_output(
        self, mock_router_cls,
    ):
        mock_router = mock_router_cls.return_value
        mock_router.AGENT_MAP = {'COOAgent': object()}
        mock_router.route.side_effect = ValueError('upstream pipeline timeout')

        result = self.agent._execute_lane_4_rotating_focus_step({
            'rotation_slot': 'gtm_pipeline_health',
        })

        self.assertFalse(result['success'])
        self.assertIn('No signal today', result['output'])
        self.assertIn('ValueError', result['output'])

    def test_successful_dispatch_uses_agent_output_not_sentinel(self):
        """Regression guard: success path MUST use the agent's actual
        message as output, NOT the sentinel."""
        with patch('core.agent_router.AgentRouter') as mock_router_cls:
            mock_router = mock_router_cls.return_value
            mock_router.AGENT_MAP = {'COOAgent': object()}
            mock_router.route.return_value = MagicMock(
                success=True,
                message='- KPI 1 moved +12%\n- Risk: vendor delays',
                data={'kpi_count': 1},
            )

            result = self.agent._execute_lane_4_rotating_focus_step({
                'rotation_slot': 'gtm_pipeline_health',
            })

        self.assertTrue(result['success'])
        self.assertIn('KPI 1', result['output'])
        self.assertNotIn('No signal today', result['output'])


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


class MorningBriefRotationSlotResolveTests(SimpleTestCase):
    """Session 1233 B.2 — rotation_slot_resolve pre-step.

    Coverage shape:
    - Each weekday Mon-Thu + Sat-Sun → expected default slot
    - Fri alternation by ISO week parity (sports ↔ markets)
    - Override priority chain: incident → revenue → signal → calendar
    - Caller-forced ``rotation_slot`` wins over all overrides
    - Handler writes ``context['rotation_slot']`` for Lane 4 to read
    - Handler returns ``reason`` diagnostic for runner step_result
    """

    def setUp(self):
        self.agent = WorkflowOrchestrationAgent(user=MagicMock(name='user'))

    def _mock_now(self, weekday, iso_week=1):
        """Build a now-mock returning the given weekday + iso_week.

        Patch ``self.agent._get_now_utc`` to return this so
        ``_resolve_rotation_slot`` reads our fixed value.
        """
        mock_now = MagicMock()
        mock_now.weekday.return_value = weekday
        mock_now.isocalendar.return_value = (2026, iso_week, weekday + 1)
        return mock_now

    def _resolve_at(self, weekday, iso_week=1, context=None):
        with patch.object(
            self.agent, '_get_now_utc',
            return_value=self._mock_now(weekday, iso_week=iso_week),
        ):
            return self.agent._resolve_rotation_slot(context or {})

    # ── default weekday assignments ──

    def test_monday_resolves_to_ai_infra_deep_dive(self):
        self.assertEqual(self._resolve_at(0), 'ai_infra_deep_dive')

    def test_tuesday_resolves_to_ai_infra_deep_dive(self):
        """Spec calls Tue 'competitor_wedge' but that's a Lane-3-deepen
        concept, not a Lane 4 slot. B.2 falls back to ai_infra default;
        a future Sub-step can add a dedicated competitor_wedge slot."""
        self.assertEqual(self._resolve_at(1), 'ai_infra_deep_dive')

    def test_wednesday_resolves_to_ticker_catalyst_watch(self):
        self.assertEqual(self._resolve_at(2), 'ticker_catalyst_watch')

    def test_thursday_resolves_to_gtm_pipeline_health(self):
        self.assertEqual(self._resolve_at(3), 'gtm_pipeline_health')

    def test_saturday_falls_back_to_ai_infra(self):
        self.assertEqual(self._resolve_at(5), 'ai_infra_deep_dive')

    def test_sunday_falls_back_to_ai_infra(self):
        self.assertEqual(self._resolve_at(6), 'ai_infra_deep_dive')

    # ── Friday alternation ──

    def test_friday_even_iso_week_picks_sports(self):
        self.assertEqual(
            self._resolve_at(4, iso_week=2), 'sports_edge_scan',
            "Friday on an even ISO week → sports edge scan.",
        )

    def test_friday_odd_iso_week_picks_prediction_markets(self):
        self.assertEqual(
            self._resolve_at(4, iso_week=1), 'prediction_markets',
            "Friday on an odd ISO week → prediction markets.",
        )

    # ── caller-forced wins ──

    def test_caller_forced_slot_wins_over_weekday_default(self):
        slot = self.agent._resolve_rotation_slot(
            {'rotation_slot': 'sports_edge_scan'},
        )
        self.assertEqual(slot, 'sports_edge_scan')

    def test_caller_forced_slot_wins_over_overrides(self):
        slot = self.agent._resolve_rotation_slot({
            'rotation_slot': 'sports_edge_scan',
            'rotation_override': {'incident': True, 'revenue': True},
        })
        self.assertEqual(slot, 'sports_edge_scan',
                         "Caller-forced rotation_slot wins over override flags.")

    # ── override priority chain ──

    def test_incident_override_routes_to_ai_infra(self):
        """B.2 doesn't have a dedicated incident_focus slot yet; until
        that lands, incident override deepens Lane 1's coverage by
        re-running ai_infra_deep_dive."""
        slot = self.agent._resolve_rotation_slot({
            'rotation_override': {'incident': True},
        })
        self.assertEqual(slot, 'ai_infra_deep_dive')

    def test_revenue_override_routes_to_gtm(self):
        slot = self.agent._resolve_rotation_slot({
            'rotation_override': {'revenue': True},
        })
        self.assertEqual(slot, 'gtm_pipeline_health')

    def test_signal_shorthand_routes_to_slot(self):
        for shorthand, expected in [
            ('sports', 'sports_edge_scan'),
            ('markets', 'prediction_markets'),
            ('tickers', 'ticker_catalyst_watch'),
            ('gtm', 'gtm_pipeline_health'),
            ('ai_infra', 'ai_infra_deep_dive'),
        ]:
            slot = self.agent._resolve_rotation_slot({
                'rotation_override': {'signal_slot': shorthand},
            })
            self.assertEqual(slot, expected,
                             f"signal_slot={shorthand!r} → {expected!r}")

    def test_calendar_shorthand_routes_to_slot(self):
        slot = self.agent._resolve_rotation_slot({
            'rotation_override': {'calendar_slot': 'tickers'},
        })
        self.assertEqual(slot, 'ticker_catalyst_watch')

    def test_incident_beats_revenue(self):
        slot = self.agent._resolve_rotation_slot({
            'rotation_override': {'incident': True, 'revenue': True},
        })
        self.assertEqual(slot, 'ai_infra_deep_dive',
                         "Incident is higher priority than revenue.")

    def test_revenue_beats_signal(self):
        slot = self.agent._resolve_rotation_slot({
            'rotation_override': {
                'revenue': True,
                'signal_slot': 'sports',
            },
        })
        self.assertEqual(slot, 'gtm_pipeline_health',
                         "Revenue is higher priority than signal.")

    def test_signal_beats_calendar(self):
        slot = self.agent._resolve_rotation_slot({
            'rotation_override': {
                'signal_slot': 'tickers',
                'calendar_slot': 'sports',
            },
        })
        self.assertEqual(slot, 'ticker_catalyst_watch',
                         "Signal is higher priority than calendar.")

    def test_unknown_signal_shorthand_falls_back_to_default(self):
        slot = self.agent._resolve_rotation_slot({
            'rotation_override': {'signal_slot': 'made_up_xyz'},
        })
        self.assertEqual(slot, 'ai_infra_deep_dive',
                         "Unknown shorthand → default slot fallback.")

    # ── handler step behavior ──

    def test_handler_writes_rotation_slot_to_context(self):
        context = {}
        with patch.object(
            self.agent, '_get_now_utc',
            return_value=self._mock_now(2),
        ):
            result = self.agent._execute_rotation_slot_resolve_step(context)
        self.assertTrue(result['success'])
        self.assertEqual(context['rotation_slot'], 'ticker_catalyst_watch')
        self.assertEqual(result['rotation_slot'], 'ticker_catalyst_watch')
        self.assertIn('weekday_default:2', result['reason'])

    def test_handler_reason_distinguishes_caller_forced(self):
        context = {'rotation_slot': 'sports_edge_scan'}
        result = self.agent._execute_rotation_slot_resolve_step(context)
        self.assertEqual(result['reason'], 'caller_forced')
        self.assertEqual(result['rotation_slot'], 'sports_edge_scan')

    def test_handler_reason_captures_override_type(self):
        for override, expected_prefix in [
            ({'incident': True}, 'override_incident'),
            ({'revenue': True}, 'override_revenue'),
            ({'signal_slot': 'sports'}, 'override_signal:sports'),
            ({'calendar_slot': 'tickers'}, 'override_calendar:tickers'),
        ]:
            result = self.agent._execute_rotation_slot_resolve_step({
                'rotation_override': override,
            })
            self.assertEqual(result['reason'], expected_prefix)

    def test_handler_registered_in_dispatcher(self):
        """Smoke-level check: rotation_slot_resolve as agent name in a
        step_def routes to the dedicated internal handler, not the
        AGENT_MAP fallback."""
        with patch.object(
            self.agent, '_execute_rotation_slot_resolve_step',
            return_value={'success': True, 'rotation_slot': 'sentinel'},
        ) as spy:
            result = self.agent._execute_step(
                {'step': 1, 'name': 'rotation_slot_resolve',
                 'agent': 'rotation_slot_resolve', 'description': 'test'},
                context={},
            )
            spy.assert_called_once()


class AgentMapFallbackFailLoudTests(SimpleTestCase):
    """S3037 A6 — AGENT_MAP fallback fail-loud regression guard.

    Discharges the S3037 Reliability Audit v0 Step 3 finding: the
    ``_execute_step`` AGENT_MAP fallback (used by ``lane_1_platform_readiness``
    → ``system_intelligence_agent`` and every other snake_case-agent step
    that has no dedicated internal handler) returned ``{'success': False,
    'output': '', 'data': ...}`` with no ``'error'`` field on falsy
    router.route success. Orchestrator at line 1315/1342 then substituted
    the generic "Unknown error" fallback, producing the deterministic
    ``error_signature: 1cfc0fcf97dd26ce`` on 5+ morning_brief failures
    across 12 days (2026-07-17 → 2026-07-29).

    These tests lock in the fix: on falsy router.route success, the
    return dict ALWAYS populates ``'error'`` (with priority
    result.error → result.message/output → structured fallback),
    ``'agent_name'``, and ``'duration_ms'``. Mirrors the S1234 D1
    pattern applied to lane_4_rotating_focus.
    """

    def setUp(self):
        self.agent = WorkflowOrchestrationAgent(user=MagicMock(name='user'))
        # step_def shape matches morning_brief lane_1_platform_readiness
        self.step_def = {
            'step': 2,
            'name': 'lane_1_platform_readiness',
            'agent': 'system_intelligence_agent',
            'description': 'Overnight platform health',
        }

    @patch('core.agent_router.AgentRouter')
    def test_falsy_success_with_result_error_captures_error_string(
        self, mock_router_cls,
    ):
        mock_router = mock_router_cls.return_value
        mock_router.AGENT_MAP = {'SystemIntelligenceAgent': object()}
        mock_router.route.return_value = MagicMock(
            success=False, message='', data={},
            error='ORM query timeout during platform health check',
        )

        result = self.agent._execute_step(self.step_def, context={})

        self.assertFalse(result['success'])
        self.assertIn('error', result,
                      "Falsy-success path MUST populate 'error' field.")
        self.assertIn('ORM query timeout', result['error'])
        self.assertIn('SystemIntelligenceAgent', result['error'])
        self.assertIn("'lane_1_platform_readiness'", result['error'])
        self.assertEqual(result['agent_name'], 'SystemIntelligenceAgent')
        self.assertIn('duration_ms', result)
        self.assertIsInstance(result['duration_ms'], int)
        # MUST NOT be the generic orchestrator-level "Unknown error"
        self.assertNotIn('Unknown error', result['error'])

    @patch('core.agent_router.AgentRouter')
    def test_falsy_success_falls_through_to_message(self, mock_router_cls):
        mock_router = mock_router_cls.return_value
        mock_router.AGENT_MAP = {'SystemIntelligenceAgent': object()}
        # No .error attribute on the mock result — must fall through to message
        mock_result = MagicMock(spec=['success', 'message', 'data'])
        mock_result.success = False
        mock_result.message = 'partial diagnostic before failure'
        mock_result.data = {}
        mock_router.route.return_value = mock_result

        result = self.agent._execute_step(self.step_def, context={})

        self.assertFalse(result['success'])
        self.assertIn('partial diagnostic before failure', result['error'])
        self.assertIn('SystemIntelligenceAgent', result['error'])
        self.assertNotIn('Unknown error', result['error'])

    @patch('core.agent_router.AgentRouter')
    def test_falsy_success_with_no_diagnostics_uses_structured_fallback(
        self, mock_router_cls,
    ):
        """The 2026-07-17 → 2026-07-29 morning_brief failure shape: agent
        returned an object with success=False and no error/message/output.
        Before S3037 A6 this produced 'Unknown error' at the orchestrator.
        After A6 the handler must produce a diagnostic string identifying
        the agent + result type.
        """
        mock_router = mock_router_cls.return_value
        mock_router.AGENT_MAP = {'SystemIntelligenceAgent': object()}
        mock_result = MagicMock(spec=['success', 'message', 'data'])
        mock_result.success = False
        mock_result.message = ''
        mock_result.data = {}
        mock_router.route.return_value = mock_result

        result = self.agent._execute_step(self.step_def, context={})

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('SystemIntelligenceAgent', result['error'])
        self.assertIn('no error/message/output', result['error'])
        # MUST NOT be the generic orchestrator-level "Unknown error"
        self.assertNotIn('Unknown error', result['error'])

    @patch('core.agent_router.AgentRouter')
    def test_router_route_exception_captures_exception_type(
        self, mock_router_cls,
    ):
        mock_router = mock_router_cls.return_value
        mock_router.AGENT_MAP = {'SystemIntelligenceAgent': object()}
        mock_router.route.side_effect = ValueError('deterministic platform check bug')

        result = self.agent._execute_step(self.step_def, context={})

        self.assertFalse(result['success'])
        self.assertIn('ValueError', result['error'])
        self.assertIn('deterministic platform check bug', result['error'])
        self.assertIn("'lane_1_platform_readiness'", result['error'])
        self.assertEqual(result['agent_name'], 'SystemIntelligenceAgent')
        self.assertNotIn('Unknown error', result['error'])

    @patch('core.agent_router.AgentRouter')
    def test_success_case_shape_unchanged(self, mock_router_cls):
        """Regression guard: happy path returns the same {success, output,
        data} shape as before A6. No new keys should appear on success."""
        mock_router = mock_router_cls.return_value
        mock_router.AGENT_MAP = {'SystemIntelligenceAgent': object()}
        mock_router.route.return_value = MagicMock(
            success=True, message='all systems green', data={'checks': 5},
        )

        result = self.agent._execute_step(self.step_def, context={})

        self.assertTrue(result['success'])
        self.assertEqual(result['output'], 'all systems green')
        self.assertEqual(result['data'], {'checks': 5})
        # Success path stays minimal — no agent_name / duration_ms /
        # error keys leak on the happy path (they only appear on failure).
        self.assertNotIn('error', result)
        self.assertNotIn('agent_name', result)
        self.assertNotIn('duration_ms', result)

    @patch('core.agent_router.AgentRouter')
    def test_duration_ms_captured_on_slow_failure(self, mock_router_cls):
        """A6 fast/slow-fail timing signature: duration_ms must be
        populated on the failure path so the audit can distinguish
        network-suspect (fast fail <1s) from logic-suspect (slow fail
        several seconds+)."""
        import time
        mock_router = mock_router_cls.return_value
        mock_router.AGENT_MAP = {'SystemIntelligenceAgent': object()}

        def slow_failure(*args, **kwargs):
            time.sleep(0.05)  # 50ms
            return MagicMock(success=False, message='', data={}, error='slow bug')
        mock_router.route.side_effect = slow_failure

        result = self.agent._execute_step(self.step_def, context={})

        self.assertFalse(result['success'])
        self.assertIn('duration_ms', result)
        self.assertGreaterEqual(result['duration_ms'], 45,
                                "duration_ms should reflect actual call latency")
