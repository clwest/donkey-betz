"""
Session 1185 F1: ContentWriterAgent diagnostic_mode bypass tests.
==================================================================

Surfaced by Session 1184 Section 6 forensic validation on conversation
pa-10df024c0bd8: dispatching content_writer_agent with explicit
diagnostic instructions ('include nonce PV-...', 'state X exactly',
'<= 200 words') produced a generic 561-word publishable article that
honored ZERO of the requested elements. Root cause: ContentWriterAgent's
content production pipeline (build_content_prompt → flagship injection →
LLM → quality scoring → provenance) treats instruction words as topic
words.

Fix: when `context['diagnostic_mode']=True`, bypass the full pipeline
and render the task spec verbatim as the deliverable body. No LLM call.
Deterministic by construction.

Acceptance criteria from deliverable c511e6e4-0b00-4ee0-bd19-9ee64c5a8e60:
    AC1: content matches the task spec verbatim (no LLM rewrite of
         explicit-content blocks)
    AC2: word-cap directives ('Keep to <= 200 words') are honored
    AC3: explicit-include directives ('Include this nonce: PV-...')
         land verbatim
    AC4: forensic flow can deterministically re-test the provenance
         chain with a fixed nonce

Run:
    USE_PGBOUNCER=0 python manage.py test core.tests.test_content_writer_diagnostic_mode -v2 --keepdb
"""

from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.agents.content_writer_agent import ContentWriterAgent
from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace


User = get_user_model()


FORENSIC_TASK = (
    "Create a VERY short internal diagnostic deliverable for provenance "
    "validation. Title: PROVENANCE-VALIDATION — Post-fix forensic test "
    "— 2026-06-21. Nonce: PV-20260621-002. Requirements: Include a line "
    "with the nonce exactly as above. Include a single line with the "
    "current time in Mountain Time (MDT/MST). State 'No web browsing "
    "used.' Keep to <= 200 words. This is an internal diagnostic (not "
    "for publishing)."
)


class DiagnosticModeTests(TestCase):
    """F1 — diagnostic_mode flag bypasses the full content production pipeline."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='diag-mode', email='dm@example.com', password='x',
            is_superuser=True,
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name='Diagnostic Mode Test Workspace',
            allow_autonomous_writes=True,
        )

    def setUp(self):
        self.agent = ContentWriterAgent(user=self.user)
        # mimic agent_router._run_agent_execute setup so _save_to_deliverable
        # has the workspace + execution context it needs
        self.agent._workspace_id = str(self.workspace.id)

    def _dispatch(self, task, extra_context=None):
        context = {'diagnostic_mode': True}
        if extra_context:
            context.update(extra_context)
        return self.agent.execute(
            task=task,
            context=context,
            scifi_context={},
            spider_context={},
        )

    # ── AC1 ────────────────────────────────────────────────────────────────
    def test_diagnostic_mode_renders_task_verbatim(self):
        """The deliverable body must equal the task spec verbatim — no LLM
        rewrite, no editorial restructuring, no added headers."""
        result = self._dispatch(FORENSIC_TASK)

        self.assertTrue(result.success, f"dispatch must succeed: {result.error}")
        self.assertEqual(result.data['content']['full_text'], FORENSIC_TASK,
                         'AC1: full_text must equal the task spec verbatim')
        self.assertTrue(result.data['diagnostic_mode'])

    # ── AC2 ────────────────────────────────────────────────────────────────
    def test_diagnostic_mode_honors_word_cap_by_preserving_caller_spec(self):
        """Word-cap directives are honored by NOT inflating the content. A
        spec under the requested cap stays under the cap."""
        short_task = "Diagnostic ping. Nonce: PV-TEST-123. <= 25 words."
        result = self._dispatch(short_task)

        body = result.data['content']['full_text']
        self.assertLessEqual(
            len(body.split()), 25,
            'AC2: caller said <=25 words; render must not inflate beyond that',
        )

    # ── AC3 ────────────────────────────────────────────────────────────────
    def test_diagnostic_mode_includes_explicit_nonce_verbatim(self):
        """The exact nonce string from the task must appear in the saved
        deliverable body."""
        result = self._dispatch(FORENSIC_TASK)
        body = result.data['content']['full_text']

        self.assertIn('PV-20260621-002', body,
                      'AC3: explicit nonce must land verbatim in content')
        self.assertIn("No web browsing used.", body,
                      'AC3: explicit-state directive must land verbatim')

    # ── AC4 ────────────────────────────────────────────────────────────────
    def test_diagnostic_mode_is_deterministic_across_runs(self):
        """Same task → same content body. No LLM in the loop means forensic
        flows can re-dispatch and assert identical output."""
        r1 = self._dispatch(FORENSIC_TASK)
        # Fresh agent instance, second dispatch
        agent2 = ContentWriterAgent(user=self.user)
        agent2._workspace_id = str(self.workspace.id)
        r2 = agent2.execute(
            task=FORENSIC_TASK,
            context={'diagnostic_mode': True},
            scifi_context={}, spider_context={},
        )

        self.assertEqual(
            r1.data['content']['full_text'],
            r2.data['content']['full_text'],
            'AC4: dispatches with identical task must produce identical content',
        )

    # ── Pipeline-bypass proof ─────────────────────────────────────────────
    def test_diagnostic_mode_does_not_call_llm(self):
        """Bypass proof: no openai client / generate_content call fires.
        If diagnostic_mode somehow re-entered the full pipeline, the LLM
        call would happen and this test would observe it."""
        with mock.patch.object(
            ContentWriterAgent, '_generate_content',
            side_effect=AssertionError('LLM path must not execute in diagnostic_mode'),
        ):
            result = self._dispatch(FORENSIC_TASK)
        self.assertTrue(result.success)

    # ── Deliverable side-effect ───────────────────────────────────────────
    def test_diagnostic_mode_persists_deliverable_with_marker(self):
        """The deliverable must land in the DB with the diagnostic_mode
        metadata marker so downstream forensic flows can find it.

        Note: factory's `_clean_deliverable_title` always prepends
        `<agent_name>: ` to clean titles — so the saved title is
        `'ContentWriterAgent: Diagnostic Dispatch'`, not the raw value
        we passed in. That's existing factory behavior, not a diagnostic-
        mode contract.
        """
        before = Deliverable.objects.filter(
            user=self.user, agent_name='ContentWriterAgent',
        ).count()
        result = self._dispatch(FORENSIC_TASK)
        after = Deliverable.objects.filter(
            user=self.user, agent_name='ContentWriterAgent',
        ).count()

        self.assertEqual(after - before, 1, 'one deliverable per dispatch')
        d = Deliverable.objects.filter(
            user=self.user, agent_name='ContentWriterAgent',
        ).order_by('-created_at').first()
        self.assertEqual(d.content, FORENSIC_TASK, 'persisted body == task verbatim')
        self.assertTrue(d.metadata.get('diagnostic_mode'),
                        'metadata.diagnostic_mode must mark forensic dispatches')
        self.assertIn('Diagnostic Dispatch', d.title,
                      'default title shows through factory prefix-cleaning')
        # silence unused result on this path
        self.assertTrue(result.success)

    # ── Optional context overrides ────────────────────────────────────────
    def test_diagnostic_mode_honors_title_override(self):
        """diagnostic_title in context should override the default title.
        AgentResult carries the raw title; persisted Deliverable carries
        the factory-prefixed version."""
        result = self._dispatch(
            FORENSIC_TASK,
            extra_context={'diagnostic_title': 'PROVENANCE-VALIDATION'},
        )
        self.assertEqual(result.data['title'], 'PROVENANCE-VALIDATION',
                         'AgentResult.data.title is the un-prefixed override')

        d = Deliverable.objects.filter(
            user=self.user, agent_name='ContentWriterAgent',
            title__icontains='PROVENANCE-VALIDATION',
        ).first()
        self.assertIsNotNone(d, 'persisted deliverable must surface override title')
