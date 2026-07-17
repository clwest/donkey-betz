"""S2803 Phase 3.0 — legal drafting dispatch + status endpoint tests.

Covers the two new endpoints + the shared dispatch helper + the
_handle_legal_agent PA path + the draft_legal_document_task terminal-state
update logic:

  T1  POST /api/legal/draft/ with disclaimer_acknowledged=False → 400 error_code=disclaimer_required
  T2  POST /api/legal/draft/ with disclaimer_acknowledged=True + task_description → 200 +
      LegalDocumentDispatchLog row shape (user / task_id / ip / user_agent / disclaimer_acknowledged / status='dispatched')
  T3  GET /api/legal/draft-status/<task_id>/ cross-user → 404 (no info leak)
  T4  POST /api/legal/draft/ unauthenticated → 401
  T5a draft_legal_document_task completion path — patch AgentRouter to return success
      + verify DispatchLog gets status='completed' + completed_at + resulting_document
  T5b draft_legal_document_task failure path — patch AgentRouter to raise
      + verify DispatchLog gets status='failed' + error_message + completed_at
  T6  _handle_legal_agent (Rigby PA path) with disclaimer_acknowledged=False →
      returns error_code='disclaimer_required' (no task dispatch)
  T6b _handle_legal_agent with disclaimer_acknowledged=True → dispatches +
      records LegalDocumentDispatchLog with client_session_pin set

Run: python manage.py test core.tests.test_legal_draft_endpoint -v2 --noinput
"""

from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.agents.base_agent import AgentResult
from core.models_legal_audit import LegalDocumentDispatchLog
from core.models_unified_system import LegalDocument
from core.services.legal_dispatch import DisclaimerRequired, dispatch_legal_draft

User = get_user_model()


class LegalDraftEndpointTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='legal_draft_owner_s2803', password='x')
        cls.intruder = User.objects.create_user(username='legal_draft_intruder_s2803', password='x')

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)

    # -------------------------------------------------------------- T1
    def test_t1_dispatch_rejects_missing_disclaimer(self):
        resp = self.client.post(
            '/api/legal/draft/',
            {'task_description': 'Draft a motion', 'disclaimer_acknowledged': False},
            format='json',
        )
        self.assertEqual(resp.status_code, 400, resp.content)
        body = resp.json()
        self.assertFalse(body.get('success'))
        self.assertEqual(body.get('error_code'), 'disclaimer_required')
        self.assertEqual(LegalDocumentDispatchLog.objects.count(), 0,
                         'no DispatchLog row should be written when disclaimer missing')

    # -------------------------------------------------------------- T2
    @patch('core.tasks.draft_legal_document_task')
    def test_t2_dispatch_success_writes_dispatch_log(self, mock_task):
        mock_task.delay.return_value = MagicMock(id='fake-task-id-t2')
        resp = self.client.post(
            '/api/legal/draft/',
            {
                'task_description': 'Draft Motion to Modify Parenting Time',
                'disclaimer_acknowledged': True,
            },
            format='json',
            HTTP_USER_AGENT='TestBrowser/1.0',
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        body = resp.json()
        self.assertTrue(body['success'])
        self.assertEqual(body['task_id'], 'fake-task-id-t2')
        self.assertIn('dispatch_log_id', body)

        row = LegalDocumentDispatchLog.objects.get(task_id='fake-task-id-t2')
        self.assertEqual(row.user, self.owner)
        self.assertEqual(row.task_description, 'Draft Motion to Modify Parenting Time')
        self.assertTrue(row.disclaimer_acknowledged)
        self.assertEqual(row.status, 'dispatched')
        self.assertEqual(row.user_agent, 'TestBrowser/1.0')
        # ip_address is set from _client_ip_from_request; in test client it's typically 127.0.0.1
        self.assertIsNone(row.completed_at)

    # -------------------------------------------------------------- T3
    def test_t3_status_cross_user_returns_404(self):
        # Owner creates a dispatch log
        LegalDocumentDispatchLog.objects.create(
            user=self.owner,
            task_id='owner-only-task',
            task_description='owner task',
            disclaimer_acknowledged=True,
            status='dispatched',
        )
        # Intruder polls owner's task_id → 404
        self.client.force_authenticate(user=self.intruder)
        resp = self.client.get('/api/legal/draft-status/owner-only-task/')
        self.assertEqual(resp.status_code, 404, resp.content)

    # -------------------------------------------------------------- T4
    def test_t4_unauthenticated_rejected(self):
        anon = APIClient()
        resp = anon.post(
            '/api/legal/draft/',
            {'task_description': 'x', 'disclaimer_acknowledged': True},
            format='json',
        )
        self.assertEqual(resp.status_code, 401, resp.content)


class DraftLegalDocumentTaskTerminalStateTests(TestCase):
    """T5a/T5b: draft_legal_document_task updates DispatchLog on completion + failure."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='legal_task_test_s2803', password='x')

    def setUp(self):
        # celery_telemetry.on_task_postrun calls close_old_connections() which
        # breaks the surrounding TestCase transaction on eager task.apply().
        # Disconnect just the postrun/failure handlers for these two tests;
        # our terminal-state update logic lives inline in the task, not in
        # the signal handler, so we lose nothing test-relevant.
        from celery.signals import task_postrun, task_failure
        from core.celery_telemetry import on_task_postrun, on_task_failure

        task_postrun.disconnect(on_task_postrun)
        task_failure.disconnect(on_task_failure)
        self.addCleanup(task_postrun.connect, on_task_postrun)
        self.addCleanup(task_failure.connect, on_task_failure)

    def _make_dispatch_log(self, task_id='task-under-test'):
        return LegalDocumentDispatchLog.objects.create(
            user=self.user,
            task_id=task_id,
            task_description='Draft a motion',
            disclaimer_acknowledged=True,
            status='dispatched',
        )

    def test_t5a_completion_path_updates_dispatch_log(self):
        log = self._make_dispatch_log(task_id='task-t5a')
        legal_doc = LegalDocument.objects.create(
            user=self.user,
            document_type='motion',
            title='Test',
            content='body',
        )

        fake_result = AgentResult(
            success=True,
            message='drafted',
            data={'saved_document_ids': [str(legal_doc.id)]},
            agent_name='LegalDocDrafterAgent',
        )

        with patch('core.agent_router.AgentRouter') as MockRouter:
            MockRouter.return_value.route.return_value = fake_result

            from core.tasks import draft_legal_document_task
            # .apply() runs the task synchronously in-process; task_id sets self.request.id.
            draft_legal_document_task.apply(
                kwargs={
                    'task_description': 'Draft a motion',
                    'context': {},
                    'user_id': self.user.id,
                },
                task_id='task-t5a',
            )

        log.refresh_from_db()
        self.assertEqual(log.status, 'completed')
        self.assertIsNotNone(log.completed_at)
        self.assertEqual(log.resulting_document, legal_doc)

    def test_t5b_failure_path_updates_dispatch_log(self):
        log = self._make_dispatch_log(task_id='task-t5b')

        with patch('core.agent_router.AgentRouter') as MockRouter:
            MockRouter.return_value.route.side_effect = RuntimeError('agent boom')

            from core.tasks import draft_legal_document_task
            # .apply() surfaces the exception in `.result` / .traceback rather than raising;
            # our task raises after updating the log, so .successful() will be False.
            eager_result = draft_legal_document_task.apply(
                kwargs={
                    'task_description': 'Draft a motion',
                    'context': {},
                    'user_id': self.user.id,
                },
                task_id='task-t5b',
            )
            self.assertFalse(eager_result.successful())

        log.refresh_from_db()
        self.assertEqual(log.status, 'failed')
        self.assertIsNotNone(log.completed_at)
        self.assertIn('agent boom', log.error_message)


class LegalDispatchHelperTests(TestCase):
    """Direct helper tests — enforcement is unit-testable without HTTP layer."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='legal_helper_test_s2803', password='x')

    def test_disclaimer_required_raises_when_false(self):
        with self.assertRaises(DisclaimerRequired):
            dispatch_legal_draft(
                user=self.user,
                task_description='x',
                disclaimer_acknowledged=False,
            )
        self.assertEqual(LegalDocumentDispatchLog.objects.count(), 0)


class HandleLegalAgentDisclaimerTests(TestCase):
    """T6: Rigby PA path (_handle_legal_agent) shares the disclaimer gate."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='legal_pa_test_s2803', password='x')

    def _get_handler(self):
        # ToolDispatcher inheritance is deep; instantiate via inspection.
        from core.services.tool_dispatcher import get_tool_dispatcher
        return get_tool_dispatcher()

    def test_t6_pa_path_rejects_missing_disclaimer(self):
        handler = self._get_handler()
        result = handler._handle_legal_agent(
            tool_name='legal_doc_drafter_agent',
            payload={'task': 'Draft a motion'},  # no disclaimer_acknowledged
            user_id=self.user.id,
            trace_id='test-trace',
        )
        self.assertFalse(result['success'])
        self.assertEqual(result.get('error_code'), 'disclaimer_required')
        self.assertEqual(LegalDocumentDispatchLog.objects.count(), 0,
                         'PA path without disclaimer must not create dispatch log')

    @patch('core.tasks.draft_legal_document_task')
    def test_t6b_pa_path_success_writes_client_session_pin(self, mock_task):
        mock_task.delay.return_value = MagicMock(id='pa-task-id-t6b')
        handler = self._get_handler()
        result = handler._handle_legal_agent(
            tool_name='legal_doc_drafter_agent',
            payload={
                'task': 'Draft motion via PA',
                'disclaimer_acknowledged': True,
                'conversation_id': 'pa-test-pin-t6b',
            },
            user_id=self.user.id,
            trace_id='test-trace',
        )
        self.assertEqual(result['action'], 'draft_legal_document')
        self.assertEqual(result['task_id'], 'pa-task-id-t6b')

        row = LegalDocumentDispatchLog.objects.get(task_id='pa-task-id-t6b')
        self.assertTrue(row.disclaimer_acknowledged)
        self.assertEqual(row.client_session_pin, 'pa-test-pin-t6b')
        self.assertEqual(row.user, self.user)
