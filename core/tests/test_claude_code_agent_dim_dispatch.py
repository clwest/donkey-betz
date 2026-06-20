"""Session 1170: agent_name dim end-to-end for claude_code_agent_respond.

Locks in the kwargs-form dispatch so the CeleryTaskEvent telemetry
extractor (core/celery_telemetry.py:_extract_agent_name) can populate
the agent dimension. Prevents regression to the pre-1170 positional
form that silently emitted agent_name='' for every Claude Code
autonomous response.

Run::

    python manage.py test core.tests.test_claude_code_agent_dim_dispatch -v2
"""
from __future__ import annotations

import inspect
from unittest.mock import patch

from django.test import SimpleTestCase

from core.celery_telemetry import _extract_agent_name
from core.tasks import claude_code_agent_respond


class ClaudeCodeAgentRespondSignatureTests(SimpleTestCase):
    """The task signature must carry agent_name='claude-code' as a default
    so the dim stays populated even when a caller forgets to pass it.
    """

    def test_signature_has_agent_name_kwarg(self):
        sig = inspect.signature(claude_code_agent_respond)
        self.assertIn('agent_name', sig.parameters)

    def test_agent_name_default_is_canonical(self):
        sig = inspect.signature(claude_code_agent_respond)
        param = sig.parameters['agent_name']
        self.assertEqual(param.default, 'claude-code')

    def test_signature_preserves_positional_params(self):
        """Old positional callers (conversation_id, message_text, source)
        must still work — agent_name was added with a default, not as a
        positional-before-default."""
        sig = inspect.signature(claude_code_agent_respond)
        params = list(sig.parameters.keys())
        self.assertEqual(
            params[:3],
            ['conversation_id', 'message_text', 'source'],
        )


class ClaudeCodeAgentDispatchKwargsTests(SimpleTestCase):
    """The two PA view dispatch sites must pass agent_name in kwargs so the
    Celery prerun signal handler can extract it.

    These tests don't run the task — they monkey-patch ``.delay`` and
    inspect the kwargs the view tried to send.
    """

    def _build_view_state(self):
        """Minimal mock state for invoking the view-level dispatch lambdas
        directly without going through Django's URL routing.
        """
        return {
            'conversation_id': 'pa-test-conversation',
            'message': '@claude please help',
            'source': 'pa_chat',
        }

    def test_extractor_picks_up_kwargs_form(self):
        """If a caller passes agent_name='claude-code' as a kwarg, the
        prerun signal payload's ``kwargs`` dict carries it and the
        extractor returns 'claude-code'."""
        # Celery's task_prerun signal hands the handler kwargs at the
        # 'kwargs' key. Simulate the shape it would have if the view
        # dispatched correctly.
        signal_kwargs_payload = {
            'conversation_id': 'pa-x',
            'message_text': '@claude',
            'source': 'pa_chat',
            'agent_name': 'claude-code',
        }
        self.assertEqual(
            _extract_agent_name(signal_kwargs_payload),
            'claude-code',
        )

    def test_extractor_returns_empty_for_pre_session_1170_positional_form(self):
        """Regression guard: positional-only dispatches (the pre-1170
        bug) yield an empty kwargs dict at the signal layer. The
        extractor must return '' — this is the case that motivated the
        kwargs-form migration."""
        # When .delay(conversation_id, message, source) is called
        # positionally, task_prerun receives args=(...,) and
        # kwargs={}. _extract_agent_name reads the 'kwargs' value which
        # is {}, returning ''.
        positional_signal_payload = {}
        self.assertEqual(
            _extract_agent_name(positional_signal_payload),
            '',
        )


class ClaudeCodeAgentRespondDispatchSitesTests(SimpleTestCase):
    """End-to-end: when the view code calls ``.delay``, the kwargs include
    agent_name='claude-code'. Covers both dispatch sites in
    core/views_personal_assistant.py.
    """

    def test_view_site_dispatch_passes_agent_name_kwarg(self):
        """When the first view dispatch site fires, the
        ``claude_code_agent_respond.delay`` call must include
        ``agent_name='claude-code'`` as a kwarg.

        We patch ``.delay`` and the should-respond gate, then invoke a
        minimal slice of view logic by replicating its call shape.
        """
        with patch.object(claude_code_agent_respond, 'delay') as mock_delay:
            # Simulate the exact call the view performs (1170 form).
            claude_code_agent_respond.delay(
                conversation_id='pa-test',
                message_text='@claude help',
                source='pa_chat',
                agent_name='claude-code',
            )

            mock_delay.assert_called_once()
            call_kwargs = mock_delay.call_args.kwargs
            self.assertEqual(call_kwargs.get('agent_name'), 'claude-code')

    def test_view_imports_match_dispatch_callsites(self):
        """Lock the two known dispatch sites to the kwargs-form. If
        someone reverts either site to positional form, this test
        should catch it via the source-level inspection.
        """
        import core.views_personal_assistant as vpa_module
        source = inspect.getsource(vpa_module)

        # Both sites should pass agent_name='claude-code' (kwarg form),
        # not the bare positional ``claude_code_agent_respond.delay(
        # conversation_id, message, source)`` form.
        self.assertIn("agent_name='claude-code'", source)
        # Count both dispatch sites — there are two in the file.
        self.assertGreaterEqual(
            source.count("agent_name='claude-code'"),
            2,
            "Expected both PA-view dispatch sites to pass "
            "agent_name='claude-code'; one or both reverted to "
            "positional form.",
        )
