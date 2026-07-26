"""
Tests for Deliverable-as-spec resolution in claude_code_tool dispatcher.

Session 2968 PR-B. Verifies the deliverable_id branch in
`_handle_claude_code` at core/services/td_handlers_codejobs.py:330.

Scope per Rigby T1 SIGN AGREE + F-BLOCKING refinements:
  1. deliverable_id resolves to a spec + pre-injects into task_description
  2. deliverable_id not-found returns error envelope, no dispatch
  3. deliverable_id wins over task when both are passed
  4. deliverable_id alone (without task) satisfies the "task required" gate
     (Rigby T1 SIGN F-BLOCKING #1)
  5. spec_size_exceeds_soft_cap warning fires at >50k chars, but dispatch
     still proceeds (Rigby T1 SIGN F-BLOCKING #2 — warn, don't hard-fail)
  6. engineering_spec deliverable_type is exempt from missing_initiative_id
     diagnostic (unit test on deliverable_factory helper)

Design pattern mirrors core/tests/test_engineer_budget_caps.py — SimpleTestCase
where possible, TransactionTestCase when we need a real Deliverable row.
"""
from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase, TransactionTestCase


class _DispatchProbe:
    """Minimal probe that mirrors CodeJobHandlersMixin's dispatch shape.

    Rather than instantiating the full mixin (which pulls in the whole
    tool_dispatcher import tree), we mixin _handle_claude_code onto a
    stub class so tests can exercise it in isolation.
    """
    _conversation_id = None


def _make_probe():
    from core.services.td_handlers_codejobs import CodeJobHandlersMixin

    class _Probe(CodeJobHandlersMixin, _DispatchProbe):
        pass

    return _Probe()


class TestDeliverableIdResolution(SimpleTestCase):
    """deliverable_id resolves to a spec + pre-injects title/type/content into
    task_description before the Celery dispatch."""

    @patch('core.tasks.claude_code_engineer_task')
    @patch('core.models_skin_layer.ProjectWorkspace')
    def test_deliverable_id_pre_resolves_into_task_description(
        self, mock_ws_cls, mock_task,
    ):
        # Mock Deliverable ORM lookup
        mock_workspace = MagicMock()
        mock_workspace.name = 'Donkey Betz'
        spec = MagicMock()
        spec.id = 'deadbeef-1111-2222-3333-444455556666'
        spec.title = 'Refactor X to use Y'
        spec.deliverable_type = 'engineering_spec'
        spec.content = 'Acceptance criteria:\n1. Do foo\n2. Do bar\nOut of scope: baz.'
        spec.workspace = mock_workspace
        spec.workspace_id = 'ws-uuid'

        # Suppress workspace resolution (irrelevant to this test)
        mock_ws_cls.objects.filter.return_value.first.return_value = None

        with patch('core.models_deliverables.Deliverable') as mock_deliv:
            mock_deliv.objects.select_related.return_value.filter.return_value.first.return_value = spec
            mock_task.delay.return_value = MagicMock(id='task-uuid')

            probe = _make_probe()
            resp = probe._handle_claude_code(
                tool_name='claude_code_tool',
                payload={
                    'deliverable_id': 'deadbeef-1111-2222-3333-444455556666',
                    'workspace_id': 'ws-uuid',
                },
                user_id='chris',
                trace_id='trace-x',
            )

        self.assertEqual(resp['status'], 'dispatched')
        self.assertEqual(
            resp['deliverable_id_resolved'],
            'deadbeef-1111-2222-3333-444455556666',
        )
        self.assertEqual(resp['deliverable_title'], 'Refactor X to use Y')
        self.assertEqual(resp['deliverable_warnings'], [])

        # Task was dispatched with the enriched task_description
        call_kwargs = mock_task.delay.call_args.kwargs
        enriched_task = call_kwargs['task_description']
        self.assertIn('Refactor X to use Y', enriched_task)
        self.assertIn('engineering_spec', enriched_task)
        self.assertIn('Donkey Betz', enriched_task)
        self.assertIn('Acceptance criteria', enriched_task)
        self.assertIn('Do foo', enriched_task)


class TestDeliverableIdNotFound(SimpleTestCase):
    """Deliverable-not-found returns error envelope; no Celery dispatch."""

    @patch('core.tasks.claude_code_engineer_task')
    def test_deliverable_not_found_returns_error_envelope(self, mock_task):
        with patch('core.models_deliverables.Deliverable') as mock_deliv:
            mock_deliv.objects.select_related.return_value.filter.return_value.first.return_value = None
            mock_task.delay.return_value = MagicMock(id='task-uuid')

            probe = _make_probe()
            resp = probe._handle_claude_code(
                tool_name='claude_code_tool',
                payload={'deliverable_id': 'nonexistent-uuid'},
                user_id='chris',
                trace_id='trace-x',
            )

        self.assertEqual(resp['status'], 'error')
        self.assertIn('not found', resp['error'])
        self.assertEqual(resp['deliverable_id_requested'], 'nonexistent-uuid')
        mock_task.delay.assert_not_called()


class TestDeliverableIdWinsOverTask(SimpleTestCase):
    """When both `task` and `deliverable_id` are set, deliverable_id wins."""

    @patch('core.tasks.claude_code_engineer_task')
    @patch('core.models_skin_layer.ProjectWorkspace')
    def test_deliverable_id_supersedes_free_form_task(
        self, mock_ws_cls, mock_task,
    ):
        spec = MagicMock()
        spec.id = 'aaa-bbb'
        spec.title = 'Spec-supplied title'
        spec.deliverable_type = 'engineering_spec'
        spec.content = 'Spec content body.'
        spec.workspace = None
        spec.workspace_id = None

        mock_ws_cls.objects.filter.return_value.first.return_value = None

        with patch('core.models_deliverables.Deliverable') as mock_deliv:
            mock_deliv.objects.select_related.return_value.filter.return_value.first.return_value = spec
            mock_task.delay.return_value = MagicMock(id='task-uuid')

            probe = _make_probe()
            probe._handle_claude_code(
                tool_name='claude_code_tool',
                payload={
                    'task': 'DO SOMETHING ELSE ENTIRELY',
                    'deliverable_id': 'aaa-bbb',
                },
                user_id='chris',
                trace_id='trace-x',
            )

        enriched_task = mock_task.delay.call_args.kwargs['task_description']
        self.assertIn('Spec-supplied title', enriched_task)
        self.assertIn('Spec content body.', enriched_task)
        # Free-form task text should NOT be present — spec wins
        self.assertNotIn('DO SOMETHING ELSE ENTIRELY', enriched_task)


class TestDeliverableIdSatisfiesTaskGate(SimpleTestCase):
    """Rigby T1 SIGN F-BLOCKING #1: `deliverable_id` alone (no `task`) is a
    valid dispatch. Prior gate rejected 'task description is required'."""

    @patch('core.tasks.claude_code_engineer_task')
    @patch('core.models_skin_layer.ProjectWorkspace')
    def test_deliverable_id_alone_satisfies_gate(self, mock_ws_cls, mock_task):
        spec = MagicMock()
        spec.id = 'aaa-bbb'
        spec.title = 'Solo-spec title'
        spec.deliverable_type = 'engineering_spec'
        spec.content = 'Solo body.'
        spec.workspace = None
        spec.workspace_id = None

        mock_ws_cls.objects.filter.return_value.first.return_value = None

        with patch('core.models_deliverables.Deliverable') as mock_deliv:
            mock_deliv.objects.select_related.return_value.filter.return_value.first.return_value = spec
            mock_task.delay.return_value = MagicMock(id='task-uuid')

            probe = _make_probe()
            resp = probe._handle_claude_code(
                tool_name='claude_code_tool',
                payload={'deliverable_id': 'aaa-bbb'},  # no task key at all
                user_id='chris',
                trace_id='trace-x',
            )

        self.assertEqual(resp['status'], 'dispatched')
        mock_task.delay.assert_called_once()

    @patch('core.tasks.claude_code_engineer_task')
    def test_neither_task_nor_deliverable_still_rejected(self, mock_task):
        probe = _make_probe()
        resp = probe._handle_claude_code(
            tool_name='claude_code_tool',
            payload={'workspace_id': 'ws-uuid'},  # no task, no deliverable_id
            user_id='chris',
            trace_id='trace-x',
        )

        self.assertIn('error', resp)
        self.assertIn('deliverable_id', resp['error'])
        mock_task.delay.assert_not_called()


class TestSpecSizeSoftCap(SimpleTestCase):
    """Rigby T1 SIGN F-BLOCKING #2: spec >50k chars logs warning +
    surfaces `spec_size_exceeds_soft_cap` in envelope but STILL dispatches."""

    @patch('core.tasks.claude_code_engineer_task')
    @patch('core.models_skin_layer.ProjectWorkspace')
    def test_oversized_spec_warns_but_dispatches(self, mock_ws_cls, mock_task):
        spec = MagicMock()
        spec.id = 'big-spec'
        spec.title = 'Massive spec'
        spec.deliverable_type = 'engineering_spec'
        # 60k chars > 50k soft cap
        spec.content = 'x' * 60_000
        spec.workspace = None
        spec.workspace_id = None

        mock_ws_cls.objects.filter.return_value.first.return_value = None

        with patch('core.models_deliverables.Deliverable') as mock_deliv:
            mock_deliv.objects.select_related.return_value.filter.return_value.first.return_value = spec
            mock_task.delay.return_value = MagicMock(id='task-uuid')

            probe = _make_probe()
            resp = probe._handle_claude_code(
                tool_name='claude_code_tool',
                payload={'deliverable_id': 'big-spec'},
                user_id='chris',
                trace_id='trace-x',
            )

        self.assertEqual(resp['status'], 'dispatched')  # STILL dispatched
        self.assertIn('spec_size_exceeds_soft_cap', resp['deliverable_warnings'])
        mock_task.delay.assert_called_once()

    @patch('core.tasks.claude_code_engineer_task')
    @patch('core.models_skin_layer.ProjectWorkspace')
    def test_normal_size_spec_no_warning(self, mock_ws_cls, mock_task):
        spec = MagicMock()
        spec.id = 'normal-spec'
        spec.title = 'Normal spec'
        spec.deliverable_type = 'engineering_spec'
        spec.content = 'x' * 1_000  # well under 50k cap
        spec.workspace = None
        spec.workspace_id = None

        mock_ws_cls.objects.filter.return_value.first.return_value = None

        with patch('core.models_deliverables.Deliverable') as mock_deliv:
            mock_deliv.objects.select_related.return_value.filter.return_value.first.return_value = spec
            mock_task.delay.return_value = MagicMock(id='task-uuid')

            probe = _make_probe()
            resp = probe._handle_claude_code(
                tool_name='claude_code_tool',
                payload={'deliverable_id': 'normal-spec'},
                user_id='chris',
                trace_id='trace-x',
            )

        self.assertEqual(resp['deliverable_warnings'], [])


class TestEngineeringSpecTypeIsExempt(SimpleTestCase):
    """`engineering_spec` deliverable_type is exempt from the
    missing_initiative_id diagnostic (per PR-B addition to
    _TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT)."""

    def test_engineering_spec_in_exempt_frozenset(self):
        from core.services.deliverable_factory import (
            _TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT,
        )
        self.assertIn('engineering_spec', _TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT)

    def test_engineering_spec_skips_missing_initiative_diagnostic(self):
        from core.services.deliverable_factory import (
            _evaluate_initiative_alignment,
        )
        # No initiative_id + exempt type → returns None (no diagnostic)
        result = _evaluate_initiative_alignment(
            initiative_id=None,
            workspace_id='ws-uuid',
            deliverable_type='engineering_spec',
        )
        self.assertIsNone(result)

    def test_non_exempt_type_still_flags_missing_initiative(self):
        from core.services.deliverable_factory import (
            _evaluate_initiative_alignment,
        )
        # Sanity: 'document' (non-exempt) still returns diagnostic tuple
        result = _evaluate_initiative_alignment(
            initiative_id=None,
            workspace_id='ws-uuid',
            deliverable_type='document',
        )
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'missing_initiative_id')
