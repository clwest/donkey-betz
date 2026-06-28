"""
Tests for PR 5: DeliverableEvent → Rigby Event Intake subscriber.

Covered cases (per PR 5 spec):
1. flag OFF → no enqueue
2. flag ON → exactly one enqueue per status_transition DeliverableEvent
3. transaction rollback → no enqueue
4. non-status_transition DeliverableEvent → no enqueue
5. enqueued event_ref format is stable (``deliverable_event:<uuid>``)
6. dry_run=True is always passed
7. task registration verified (task is in app.tasks registry)
8. eager-mode path produces 1 MissionRun + 3 OpsRunEvents end-to-end

Run::

    python manage.py test core.tests.test_deliverable_intake_subscriber -v2 --keepdb
"""

from __future__ import annotations

import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import transaction
from django.test import TestCase, TransactionTestCase, override_settings

from core.models_deliverables import Deliverable, DeliverableEvent
from core.models_ops_runs import OpsRun, OpsRunEvent
from core.models_skin_layer import ProjectWorkspace


User = get_user_model()


# ---------------------------------------------------------------------------
# Shared fixture builders
# ---------------------------------------------------------------------------


def _make_user(slug):
    return User.objects.create_user(
        username=f"sub-{slug}-{uuid.uuid4().hex[:8]}",
        email=f"sub-{slug}@example.com",
        password="x",
    )


def _make_workspace(user):
    return ProjectWorkspace.objects.create(
        user=user,
        name=f"sub-workspace-{uuid.uuid4().hex[:6]}",
        allow_autonomous_writes=True,
    )


def _make_deliverable(user, workspace, *, status='draft'):
    return Deliverable.objects.create(
        title=f"sub-deliverable-{uuid.uuid4().hex[:6]}",
        slug=f"sub-deliverable-{uuid.uuid4().hex[:10]}",
        agent_name="TestAgent",
        content="placeholder",
        user=user,
        workspace=workspace,
        status=status,
    )


# ---------------------------------------------------------------------------
# Task registration
# ---------------------------------------------------------------------------


class TaskRegistrationTests(TestCase):
    """Verify that the rigby_event_intake task is registered with Celery's
    task registry — this is what PR 5's ``app.conf.imports`` addition
    is supposed to guarantee."""

    def test_task_is_registered_on_celery_app(self):
        from core.celery import app
        # Force importer to load the task module (matches what
        # app.conf.imports does at worker boot).
        import core.services.rigby_event_intake  # noqa: F401

        task_name = "core.services.rigby_event_intake.rigby_event_intake"
        self.assertIn(
            task_name, app.tasks,
            f"task {task_name!r} must be registered on the Celery app",
        )

    def test_task_in_app_conf_imports(self):
        from core.celery import app
        self.assertIn(
            "core.services.rigby_event_intake", app.conf.imports,
            "core.services.rigby_event_intake must be in app.conf.imports "
            "so worker boots register the task",
        )


# ---------------------------------------------------------------------------
# Flag OFF — default behavior, must not enqueue
# ---------------------------------------------------------------------------


class FlagOffNoEnqueueTests(TestCase):
    """Default settings: RIGBY_EVENT_INTAKE_ENABLED = False."""

    @classmethod
    def setUpTestData(cls):
        cls.user = _make_user("flag-off")
        cls.workspace = _make_workspace(cls.user)

    @override_settings(RIGBY_EVENT_INTAKE_ENABLED=False)
    def test_no_enqueue_on_status_transition_when_flag_off(self):
        deliverable = _make_deliverable(self.user, self.workspace, status='draft')
        # Trigger a backward status_transition
        with patch(
            "core.services.rigby_event_intake.rigby_event_intake.apply_async"
        ) as mock_async:
            deliverable.status = 'ready'
            deliverable.save()
            deliverable.status = 'draft'   # backward
            deliverable.save()
        self.assertEqual(
            mock_async.call_count, 0,
            "RIGBY_EVENT_INTAKE_ENABLED=False must suppress all enqueues",
        )

    @override_settings(RIGBY_EVENT_INTAKE_ENABLED=False)
    def test_deliverable_event_still_written_when_flag_off(self):
        """The DeliverableEvent row must still land even when intake is off."""
        deliverable = _make_deliverable(self.user, self.workspace, status='draft')
        before = DeliverableEvent.objects.filter(
            deliverable=deliverable, event_type='status_transition',
        ).count()
        deliverable.status = 'ready'
        deliverable.save()
        deliverable.status = 'draft'   # backward
        deliverable.save()
        after = DeliverableEvent.objects.filter(
            deliverable=deliverable, event_type='status_transition',
        ).count()
        self.assertGreater(after, before)


# ---------------------------------------------------------------------------
# Flag ON — enqueues exactly once per status_transition
# ---------------------------------------------------------------------------


class FlagOnEnqueueTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = _make_user("flag-on")
        cls.workspace = _make_workspace(cls.user)

    @override_settings(RIGBY_EVENT_INTAKE_ENABLED=True)
    def test_one_enqueue_per_status_transition(self):
        # NB: TestCase wraps each test in a transaction that's rolled
        # back at end, so ``transaction.on_commit`` callbacks never
        # fire by default. ``captureOnCommitCallbacks(execute=True)``
        # forces the on_commit callbacks to run at context exit (Django
        # 4.0+).
        deliverable = _make_deliverable(self.user, self.workspace, status='draft')
        with patch(
            "core.services.rigby_event_intake.rigby_event_intake.apply_async"
        ) as mock_async, self.captureOnCommitCallbacks(execute=True):
            deliverable.status = 'ready'
            deliverable.save()
        self.assertEqual(mock_async.call_count, 1)

    @override_settings(RIGBY_EVENT_INTAKE_ENABLED=True)
    def test_enqueued_event_ref_has_stable_format(self):
        deliverable = _make_deliverable(self.user, self.workspace, status='draft')
        with patch(
            "core.services.rigby_event_intake.rigby_event_intake.apply_async"
        ) as mock_async, self.captureOnCommitCallbacks(execute=True):
            deliverable.status = 'ready'
            deliverable.save()

        call = mock_async.call_args
        self.assertIsNotNone(call, "apply_async must have been called")
        # apply_async called as: apply_async(args=[event_ref], kwargs={'dry_run': True})
        args_kwarg = call.kwargs.get('args')
        self.assertIsNotNone(args_kwarg, "apply_async args= kwarg must be present")
        event_ref = args_kwarg[0]
        prefix, _, ref_id = event_ref.partition(":")
        self.assertEqual(prefix, "deliverable_event")
        uuid.UUID(ref_id)  # parses as UUID
        de = DeliverableEvent.objects.get(
            deliverable=deliverable, event_type='status_transition',
        )
        self.assertEqual(ref_id, str(de.id))

    @override_settings(RIGBY_EVENT_INTAKE_ENABLED=True)
    def test_dry_run_true_always_passed(self):
        deliverable = _make_deliverable(self.user, self.workspace, status='draft')
        with patch(
            "core.services.rigby_event_intake.rigby_event_intake.apply_async"
        ) as mock_async, self.captureOnCommitCallbacks(execute=True):
            deliverable.status = 'ready'
            deliverable.save()
        call = mock_async.call_args
        self.assertIsNotNone(call)
        kw = call.kwargs.get('kwargs') or {}
        self.assertEqual(kw.get('dry_run'), True)


# ---------------------------------------------------------------------------
# Non-status_transition writes must NOT enqueue
# ---------------------------------------------------------------------------


class NonStatusTransitionNoEnqueueTests(TestCase):
    """Other DeliverableEvent kinds (synthesis_viewed, shared, etc.) must
    NOT enqueue — only status_transition is subscribed in v0."""

    @classmethod
    def setUpTestData(cls):
        cls.user = _make_user("non-status")
        cls.workspace = _make_workspace(cls.user)
        cls.deliverable = _make_deliverable(cls.user, cls.workspace, status='draft')

    @override_settings(RIGBY_EVENT_INTAKE_ENABLED=True)
    def test_synthesis_viewed_event_does_not_enqueue(self):
        with patch(
            "core.services.rigby_event_intake.rigby_event_intake.apply_async"
        ) as mock_async:
            DeliverableEvent.objects.create(
                deliverable=self.deliverable,
                event_type='synthesis_viewed',
                source='frontend',
            )
        self.assertEqual(mock_async.call_count, 0)

    @override_settings(RIGBY_EVENT_INTAKE_ENABLED=True)
    def test_shared_event_does_not_enqueue(self):
        with patch(
            "core.services.rigby_event_intake.rigby_event_intake.apply_async"
        ) as mock_async:
            DeliverableEvent.objects.create(
                deliverable=self.deliverable,
                event_type='shared',
                source='frontend',
            )
        self.assertEqual(mock_async.call_count, 0)


# ---------------------------------------------------------------------------
# Transaction rollback must not enqueue
# ---------------------------------------------------------------------------


class TransactionRollbackTests(TransactionTestCase):
    """transaction.on_commit must discard the enqueue on rollback.

    This test uses TransactionTestCase (not TestCase) so we can drive
    an explicit ``transaction.atomic()`` block with ``set_rollback(True)``
    and observe that the on_commit callback never fires.
    """

    def setUp(self):
        self.user = _make_user("rollback")
        self.workspace = _make_workspace(self.user)

    @override_settings(RIGBY_EVENT_INTAKE_ENABLED=True)
    def test_rollback_suppresses_enqueue(self):
        with patch(
            "core.services.rigby_event_intake.rigby_event_intake.apply_async"
        ) as mock_async:
            try:
                with transaction.atomic():
                    # Create deliverable + trigger status_transition inside the
                    # block, then force a rollback.
                    deliverable = _make_deliverable(
                        self.user, self.workspace, status='draft',
                    )
                    deliverable.status = 'ready'
                    deliverable.save()
                    # Force rollback.
                    transaction.set_rollback(True)
            except Exception:  # pragma: no cover
                pass
        self.assertEqual(
            mock_async.call_count, 0,
            "transaction.on_commit must discard the enqueue on rollback",
        )

    @override_settings(RIGBY_EVENT_INTAKE_ENABLED=True)
    def test_commit_fires_enqueue(self):
        """Companion to the rollback test — confirms on_commit fires on commit."""
        with patch(
            "core.services.rigby_event_intake.rigby_event_intake.apply_async"
        ) as mock_async:
            with transaction.atomic():
                deliverable = _make_deliverable(
                    self.user, self.workspace, status='draft',
                )
                deliverable.status = 'ready'
                deliverable.save()
            # Outside the atomic block — on_commit callbacks have fired by now.
        self.assertEqual(mock_async.call_count, 1)


# ---------------------------------------------------------------------------
# End-to-end eager-mode integration
# ---------------------------------------------------------------------------


class EagerModeEndToEndTests(TransactionTestCase):
    """With ``CELERY_TASK_ALWAYS_EAGER=True``, apply_async actually executes
    the task body — proves the full chain: signal → enqueue → intake task →
    MissionRun + 3 OpsRunEvents.
    """

    def setUp(self):
        self.user = _make_user("eager")
        self.workspace = _make_workspace(self.user)

    @override_settings(
        RIGBY_EVENT_INTAKE_ENABLED=True,
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_TASK_EAGER_PROPAGATES=True,
    )
    def test_status_transition_produces_one_mission_run_and_three_events(self):
        # Baseline mission counts before.
        mission_before = OpsRun.objects.filter(
            domain='mission', run_kind='intake',
        ).count()

        deliverable = _make_deliverable(self.user, self.workspace, status='draft')
        # Run inside a transaction so on_commit fires once on exit.
        with transaction.atomic():
            deliverable.status = 'ready'
            deliverable.save()

        # Mission run + 3 events created by the eager task.
        mission_runs = OpsRun.objects.filter(
            domain='mission', run_kind='intake',
        )
        self.assertEqual(mission_runs.count() - mission_before, 1)
        run = mission_runs.latest('started_at')
        events = OpsRunEvent.objects.filter(run=run)
        self.assertEqual(events.count(), 3)
        labels = set(events.values_list('label', flat=True))
        self.assertEqual(
            labels,
            {'intake_started', 'impact_assessed', 'decision_made'},
        )
        # forward transition rule fell through to 'ignore'.
        self.assertEqual(run.status, 'passed')
        self.assertEqual(run.summary.get('decision'), 'ignore')

    @override_settings(
        RIGBY_EVENT_INTAKE_ENABLED=True,
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_TASK_EAGER_PROPAGATES=True,
    )
    def test_backward_transition_eager_runs_through_to_monitor_decision(self):
        deliverable = _make_deliverable(self.user, self.workspace, status='ready')
        with transaction.atomic():
            deliverable.status = 'draft'   # backward
            deliverable.save()
        run = OpsRun.objects.filter(
            domain='mission', run_kind='intake',
        ).latest('started_at')
        self.assertEqual(run.summary.get('decision'), 'monitor')
        self.assertEqual(run.summary.get('mission_impact'), 'low')
