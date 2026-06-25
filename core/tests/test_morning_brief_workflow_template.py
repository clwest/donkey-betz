"""Session 1232 Sub-step B — `WORKFLOWS['morning_brief']` v0 template shape.

Contract tests that lock the v0 draft template against the spec at
``docs/MORNING_BRIEF_SPEC.md`` § "Workflow template skeleton —
`WORKFLOWS['morning_brief']`".

v0 is a **shape stub**: it parses, registers in `AVAILABLE_WORKFLOWS`, and
dispatches each step name. Full per-step input plumbing
(`rotation_slot_resolve` pre-step, slot-resolved Lane 4 agent,
override-trigger inputs) lands in Sub-step B follow-on.

These tests fail loudly if the v0 template drifts from the spec — they're
the contract that lets Sub-step B safely modify Lane 4 dispatch + add the
pre-step without losing the rest.

Run::

    python manage.py test core.tests.test_morning_brief_workflow_template -v2
"""

from django.test import SimpleTestCase

from core.agents.workflow_orchestration_agent import AVAILABLE_WORKFLOWS
from core.services.workflow_orchestration_agent import WorkflowOrchestrationAgent


class MorningBriefWorkflowTemplateTests(SimpleTestCase):
    """Lock the v0 workflow template against the spec."""

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
        'lane_4_rotating_focus': 'research_agent',
        'decision_card_synthesis': 'coo_agent',
        'strategic_synthesis': 'strategic_synthesis',
        'create_deliverable': 'create_project_from_research',
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

    def test_morning_brief_uses_create_project_from_research_for_deliverable(self):
        """`create_project_from_research` is the existing internal handler
        for persisting workflow output as a project/deliverable."""
        wf = WorkflowOrchestrationAgent.WORKFLOWS['morning_brief']
        deliv_step = next(
            (s for s in wf['steps'] if s['name'] == 'create_deliverable'),
            None,
        )
        self.assertIsNotNone(deliv_step,
                             "create_deliverable step must exist.")
        self.assertEqual(
            deliv_step['agent'], 'create_project_from_research',
            "create_deliverable must dispatch via the existing "
            "create_project_from_research internal handler."
        )

    def test_morning_brief_content_type_is_morning_brief(self):
        wf = WorkflowOrchestrationAgent.WORKFLOWS['morning_brief']
        self.assertEqual(
            wf.get('content_type'), 'morning_brief',
            "content_type='morning_brief' is the workspace category tag."
        )
