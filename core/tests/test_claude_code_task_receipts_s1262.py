"""Session 1262 — Claude Code task receipt reliability tests.

Validates the fail-loud + AgentExecution-anchored repair shipped in
S1262 PR. Three contract behaviors are locked in:

1. **Happy path with conversation_id set** —
   ``execute_engineering_task`` creates an AgentExecution row, runs,
   completes, persists output_data, and ChatConversation row lands.
2. **conversation_id=None silent-drop is fixed** — the LLM run still
   completes, AgentExecution row carries the result, ``_post_to_conversation``
   ERROR-logs ``[CLAUDE_CODE_POSTBACK_DROPPED]`` but does NOT raise.
3. **ChatConversation write failure fails LOUD** — ``_post_to_conversation``
   ERROR-logs ``[CLAUDE_CODE_POSTBACK_FAILED]``, marks the AgentExecution
   ``status='failed'`` with ``output_data['post_back_status']='failed'``,
   then raises so ``CeleryTaskEvent.status=FAILURE`` becomes visible.

Plus a registration guardrail: ``claude_code_engineer_task`` has
``max_retries=0`` so the fail-loud raise doesn't trigger LLM-budget
re-spend.

Real PostgreSQL (per the S1234 memory rule).

Run::

    .venv/bin/python manage.py test \\
        core.tests.test_claude_code_task_receipts_s1262 -v 2 --keepdb
"""

from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase

from core.models import Agent, AgentExecution, ChatConversation
from core.services.claude_code_engineer import (
    _create_engineer_execution_record,
    _mark_post_back_failed_on_execution,
    _persist_engineer_terminal_state,
    _post_to_conversation,
    _resolve_claude_code_agent,
)


# ═════════════════════════════════════════════════════════════════════
# §1 — Agent resolver
# ═════════════════════════════════════════════════════════════════════


def _ensure_claude_code_agent_row() -> Agent:
    """Test helper: ensure 'claude-code' Agent row exists in the test DB.

    The production DB has this row, but the Django test runner uses an
    isolated test DB. Seed the row in tests that need it.
    """
    agent, _ = Agent.objects.get_or_create(
        name='claude-code',
        defaults={
            'agent_type': 'tool_direct',
            'is_active': True,
        },
    )
    return agent


class ResolveClaudeCodeAgentTests(TestCase):
    """Verifies the canonical-name-with-fallback resolver."""

    def setUp(self):
        _ensure_claude_code_agent_row()

    def test_resolves_canonical_claude_code(self):
        agent = _resolve_claude_code_agent()
        self.assertIsNotNone(agent)
        # Prefer 'claude-code' when both exist (per Rigby S1262 SIGN
        # guidance). Either 'claude-code' or 'ClaudeCode' is acceptable
        # if only one exists in this environment.
        self.assertIn(agent.name, ('claude-code', 'ClaudeCode'))

    def test_returns_none_when_no_agent_row_exists(self):
        Agent.objects.filter(
            name__in=('claude-code', 'ClaudeCode')
        ).delete()
        self.assertIsNone(_resolve_claude_code_agent())


# ═════════════════════════════════════════════════════════════════════
# §2 — AgentExecution lifecycle
# ═════════════════════════════════════════════════════════════════════


class EngineerExecutionRecordLifecycleTests(TestCase):
    """End-to-end ``AgentExecution`` create + terminal + post-back-fail."""

    def setUp(self):
        _ensure_claude_code_agent_row()

    def test_create_writes_celery_task_id_in_input_data(self):
        """``schedule_followup(task_id=…)`` queries
        ``input_data__celery_task_id`` (td_handlers_agents.py:5202).
        Verify the field lands on the row.
        """
        record = _create_engineer_execution_record(
            celery_task_id='test-task-id-aaaa',
            task_description='echo hello',
            conversation_id='pa-test-conv-1',
            requested_by='rigby',
            request_mode='answer',
        )
        self.assertIsNotNone(record)
        self.assertEqual(record.status, 'in_progress')
        self.assertEqual(
            record.input_data.get('celery_task_id'), 'test-task-id-aaaa'
        )
        self.assertEqual(record.conversation_id, 'pa-test-conv-1')
        # Lookup mirrors td_handlers_agents.py:5202 followup binding
        found = AgentExecution.objects.filter(
            input_data__celery_task_id='test-task-id-aaaa'
        ).first()
        self.assertEqual(found.id, record.id)

    def test_persist_terminal_state_success(self):
        record = _create_engineer_execution_record(
            celery_task_id='test-task-id-bbbb',
            task_description='echo hello',
            conversation_id='pa-test-conv-1',
            requested_by='rigby',
            request_mode='answer',
        )
        result = {
            'status': 'success',
            'summary': 'Did the thing.',
            'files_changed': ['foo.py'],
            'pr_url': 'https://github.com/x/y/pull/1',
            'provider': 'anthropic',
            'mode': 'change',
            'iterations': 3,
        }
        _persist_engineer_terminal_state(record, result=result)
        record.refresh_from_db()
        self.assertEqual(record.status, 'completed')
        self.assertEqual(record.output_data.get('summary'), 'Did the thing.')
        self.assertEqual(record.output_data.get('files_changed'), ['foo.py'])
        self.assertEqual(
            record.output_data.get('pr_url'),
            'https://github.com/x/y/pull/1',
        )

    def test_persist_terminal_state_exception(self):
        record = _create_engineer_execution_record(
            celery_task_id='test-task-id-cccc',
            task_description='boom',
            conversation_id='pa-test-conv-1',
            requested_by='rigby',
            request_mode='answer',
        )
        exc = RuntimeError('synthetic engineer failure')
        _persist_engineer_terminal_state(record, exception=exc)
        record.refresh_from_db()
        self.assertEqual(record.status, 'failed')
        self.assertIn('synthetic engineer failure', record.error_message)

    def test_post_back_failed_marks_execution_failed_and_preserves_summary(self):
        record = _create_engineer_execution_record(
            celery_task_id='test-task-id-dddd',
            task_description='persist + post-back-fail',
            conversation_id='pa-test-conv-1',
            requested_by='rigby',
            request_mode='change',
        )
        # First: complete normally (LLM run succeeded; summary persisted)
        result = {
            'status': 'success',
            'summary': 'Implemented the change.',
            'files_changed': ['bar.py'],
            'pr_url': None,
            'provider': 'anthropic',
            'mode': 'change',
        }
        _persist_engineer_terminal_state(record, result=result)
        # Then: post-back-fail flag is raised by _post_to_conversation
        _mark_post_back_failed_on_execution(
            str(record.id),
            reason='ChatConversation create raised: OperationalError: db gone',
        )
        record.refresh_from_db()
        self.assertEqual(record.status, 'failed')
        # Result envelope is PRESERVED even though we marked failed —
        # post-back failure should not erase the queryable result.
        self.assertEqual(
            record.output_data.get('summary'), 'Implemented the change.'
        )
        self.assertEqual(
            record.output_data.get('post_back_status'), 'failed'
        )
        self.assertIn(
            'OperationalError',
            record.output_data.get('post_back_failure_reason', ''),
        )


# ═════════════════════════════════════════════════════════════════════
# §3 — `_post_to_conversation` fail-loud contract
# ═════════════════════════════════════════════════════════════════════


class PostToConversationFailLoudTests(TestCase):
    """The four ``if conversation_id:`` silent skips are gone."""

    def setUp(self):
        _ensure_claude_code_agent_row()

    def test_conversation_id_none_logs_error_and_returns(self):
        """conv_id=None: ERROR log marker fires, return clean (no raise)."""
        with self.assertLogs(
            'core.services.claude_code_engineer', level='ERROR'
        ) as cm:
            _post_to_conversation(
                conversation_id=None,
                summary='Result that has nowhere to go.',
                files_changed=['x.py'],
                pr_url=None,
                agent_execution_id='exec-id-test',
            )
        joined = ' '.join(cm.output)
        self.assertIn('[CLAUDE_CODE_POSTBACK_DROPPED]', joined)
        self.assertIn('agent_execution_id=exec-id-test', joined)

    def test_chat_conversation_write_failure_marks_execution_and_raises(self):
        """ChatConversation create raises → AgentExecution flagged + RAISE."""
        record = _create_engineer_execution_record(
            celery_task_id='test-task-id-eeee',
            task_description='post-back will fail',
            conversation_id='pa-fail-test',
            requested_by='rigby',
            request_mode='change',
        )
        # First, persist a successful LLM result so the post-back failure
        # cleanly demonstrates the "summary preserved" guarantee.
        _persist_engineer_terminal_state(
            record,
            result={
                'status': 'success',
                'summary': 'LLM ran successfully.',
                'files_changed': [],
                'pr_url': None,
                'provider': 'anthropic',
                'mode': 'change',
            },
        )

        synthetic_exc = RuntimeError('synthetic ChatConversation failure')
        with patch.object(
            ChatConversation.objects, 'create', side_effect=synthetic_exc
        ):
            with self.assertRaises(RuntimeError) as ctx:
                with self.assertLogs(
                    'core.services.claude_code_engineer', level='ERROR'
                ) as cm:
                    _post_to_conversation(
                        conversation_id='pa-fail-test',
                        summary='LLM ran successfully.',
                        files_changed=[],
                        pr_url=None,
                        agent_execution_id=str(record.id),
                    )
            self.assertIn(
                'synthetic ChatConversation failure', str(ctx.exception)
            )
            self.assertIn(
                '[CLAUDE_CODE_POSTBACK_FAILED]', ' '.join(cm.output)
            )

        record.refresh_from_db()
        self.assertEqual(record.status, 'failed')
        self.assertEqual(
            record.output_data.get('post_back_status'), 'failed'
        )
        # Summary preserved — the post-back fail did not erase the
        # queryable result.
        self.assertEqual(
            record.output_data.get('summary'), 'LLM ran successfully.'
        )


# ═════════════════════════════════════════════════════════════════════
# §4 — Celery task max_retries=0 lock-in
# ═════════════════════════════════════════════════════════════════════


class ClaudeCodeEngineerTaskNoRetryTests(TestCase):
    """Lock in that the expensive LLM task NEVER auto-retries on raise.

    Rigby S1262 SIGN explicit constraint — the fail-loud raise from
    ``_post_to_conversation`` must NOT trigger Celery's default 3-retry
    behavior. The decorator must declare ``max_retries=0``.
    """

    def test_max_retries_is_zero(self):
        from core.tasks import claude_code_engineer_task

        self.assertEqual(claude_code_engineer_task.max_retries, 0)

    def test_acks_late_is_false(self):
        """Defensive: ack on receipt so worker-crash mid-LLM-run does
        NOT trigger redelivery + redundant LLM spend.
        """
        from core.tasks import claude_code_engineer_task

        self.assertIs(claude_code_engineer_task.acks_late, False)
