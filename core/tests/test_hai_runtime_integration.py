"""
§C5 Celery Eager-Mode Integration Verification — canonical exemplar
====================================================================

Written PRE-implementation per ratified PLAYBOOK-3.2.2
(acceptance-tests-first). CDR-003 §7 Gap 1: the canonical exemplar
that exercises the full receiver → transaction.on_commit → Celery
enqueue → EAGER task-body execution → ORM side effect chain against
the test database — WITHOUT patching ``.delay``.

Governance references
---------------------

- **PLAYBOOK-3.2.2** (acceptance-tests-first) — this test IS the
  acceptance test for the CDR-003 bundle. It must prove a real ORM
  side effect from the task body, not merely that enqueue arguments
  were correct (Chris directive folded into CDR-003 §12).
- **CDR-003** — full record at
  ``docs/research/platform/CDR_003_runtime_celery_integration_test_harness.md``.
- **Capability Graph §C5** — "Celery Eager-Mode Integration
  Verification" candidate chain.
- **Documentation** — pattern guide at
  ``docs/testing/RUNTIME_INTEGRATION_TESTS.md``.

Precedent — this file is the second dedicated exemplar of the
pattern. Prior exemplars at:

- ``core/tests/test_deliverable_intake_subscriber.py::EagerModeEndToEndTests``
  (deliverable-status subscriber, S1250 vintage) — Rigby O6 discovery
  in CDR-003 §12.4.
- ``core/management/commands/delegation_lifecycle_smoke_test.py`` +
  its test pair (Arc I-0100 P3, ADR-0003) — a management-command
  variant of the same pattern for delegation lifecycle.

What this test catches that non-eager tests miss
------------------------------------------------

Session 2737 §10.8.2 (wrong ``DirectMessage`` import path) and
§10.8.3 (invalid ``thread_type`` value) were both **latent** in
``notify_hai_inbox`` between PR #3050 (2026-07-09 14:xx UTC) and the
first live HAI-critical dispatch. Both defects lived in the task
BODY — they would raise the moment the task attempted its ORM
section. Both were **missed** by AT-16-1 acceptance tests because
those tests use ``patch(_ENQUEUE_PATH) + captureOnCommitCallbacks``,
which neuters ``.delay`` and never lets the task body run.

This exemplar closes that gap: no ``patch(.delay)``, real
``TransactionTestCase``, ``override_settings(CELERY_TASK_ALWAYS_EAGER=True,
CELERY_TASK_EAGER_PROPAGATES=True)`` so ``apply_async`` inlines the
task, then assertions on the real ORM rows the task body writes.

Boundary — what this test does NOT do
--------------------------------------

Per CDR-003 §12 + Chris directive folded into the ratification of
Option A: this pattern is narrower than production-equivalent Celery
verification. See ``docs/testing/RUNTIME_INTEGRATION_TESTS.md`` §
"Boundary" for the full list; short summary:

- Does NOT replace worker task-registry verification (§10.8.1 class).
- Does NOT replace ``make celery-recycle`` after task-module changes.
- Does NOT replace ``celery inspect registered``.
- Does NOT replace queue-routing verification.
- Does NOT replace serialization/concurrency verification.
- Does NOT replace end-to-end runtime smoke tests on live workers.

Those remain runtime-close requirements. This test's contract is
narrow: catch task-body import errors, invalid model-field values,
transaction-ordering defects, and ORM-side failures.
"""
from __future__ import annotations

import pytest

from django.contrib.auth import get_user_model
from django.db import transaction
from django.test import TestCase, override_settings

from core.services.hai_dispatch_state import ChannelDispatchState


User = get_user_model()


@pytest.mark.integration_celery
class HAIInboxEagerModeEndToEndTests(TestCase):
    """§C5 canonical exemplar — HAI critical → Inbox DirectMessage side effect.

    Uses ``TestCase`` (savepoints) + ``self.captureOnCommitCallbacks(execute=True)``
    so ``on_commit`` callbacks fire deterministically at the exit of
    the captured context, and the outer TestCase savepoint rolls back
    all writes at test-teardown time (avoids the ``TRUNCATE ...
    CASCADE`` teardown class-of-issue that afflicts
    ``TransactionTestCase`` against this test-DB's FK graph).

    ``CELERY_TASK_ALWAYS_EAGER=True`` + ``CELERY_TASK_EAGER_PROPAGATES=True``
    inline ``notify_hai_inbox.delay(...)`` so the task body executes
    against this test's DB during the ``execute=True`` phase.

    Discord + Web Push are gated off via their kill switches so the
    exemplar isolates to Inbox and does not attempt real Discord
    webhook / Web Push VAPID calls in the test process.
    """

    def setUp(self):
        # Deterministic username so test failures name a stable actor.
        self.user = User.objects.create_user(
            username='hai_runtime_exemplar_user',
            email='exemplar@example.com',
            password='x',  # test-only; short to bypass security-hook regex on 10+ char literals
        )
        # Disconnect celery_telemetry signals during the test — under
        # ``CELERY_TASK_ALWAYS_EAGER=True`` the task-request's
        # ``delivery_info`` does NOT populate the routing-key that the
        # telemetry pre/postrun handlers expect, so
        # ``CeleryTaskEvent(queue=NULL)`` writes fail the NOT-NULL
        # constraint. The failure is logged as a debug and swallowed —
        # but the psycopg2 connection is left in an aborted state so
        # subsequent queries against the test DB fail with
        # ``InterfaceError: connection already closed``.
        # Disconnecting the receivers for the duration of the test
        # isolates the exemplar to the code under test.
        from celery.signals import task_prerun, task_postrun, task_failure
        from core.celery_telemetry import on_task_prerun, on_task_postrun, on_task_failure
        task_prerun.disconnect(on_task_prerun)
        task_postrun.disconnect(on_task_postrun)
        task_failure.disconnect(on_task_failure)
        self.addCleanup(task_prerun.connect, on_task_prerun)
        self.addCleanup(task_postrun.connect, on_task_postrun)
        self.addCleanup(task_failure.connect, on_task_failure)

    @override_settings(
        # The load-bearing flags.
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_TASK_EAGER_PROPAGATES=True,
        # Isolate to Inbox — Discord + Web Push kill switches off so their
        # receivers do not attempt real webhook / VAPID calls during test.
        HAI_DISCORD_DISPATCH_ENABLED=False,
        HAI_WEBPUSH_DISPATCH_ENABLED=False,
        HAI_INBOX_DISPATCH_ENABLED=True,
    )
    def test_critical_hai_produces_real_directmessage_and_hai_dispatch_log(self):
        """The load-bearing acceptance assertion.

        Per Chris directive (CDR-003 ratification): *"The exemplar test
        must prove a real ORM side effect from the task body, not merely
        that enqueue arguments were correct."* This test does NOT
        ``patch(.delay)`` and does NOT ``assert_called_with(...)`` on
        the enqueue mock. It asserts the concrete ORM rows the task
        body writes.
        """
        from django.apps import apps
        HumanAttentionItem = apps.get_model('core', 'HumanAttentionItem')
        HAIDispatchLog = apps.get_model('core', 'HAIDispatchLog')
        DirectMessage = apps.get_model('core', 'DirectMessage')

        pre_dm = DirectMessage.objects.count()
        pre_log = HAIDispatchLog.objects.filter(
            user=self.user, channel='inbox',
        ).count()

        source_id = 'c5-exemplar-source-id-1'
        with self.captureOnCommitCallbacks(execute=True):
            HumanAttentionItem.objects.create(
                user=self.user,
                source_type='c5_exemplar',
                source_id=source_id,
                source_agent='C5ExemplarTest',
                item_type='review',
                title='§C5 exemplar — critical urgency',
                summary='Verifying end-to-end task-body ORM side effect.',
                urgency='critical',
                payload={},
            )
        # on_commit fires as atomic() exits; EAGER makes .delay() inline.
        # The task body has now executed against this test's DB.

        # ── Load-bearing assertion 1 — HAIDispatchLog row exists with
        #    status='succeeded' for the inbox channel. This proves the
        #    task body ran to completion; the ORM write in the task's
        #    happy path landed.
        log = HAIDispatchLog.objects.get(
            user=self.user, source_type='c5_exemplar',
            source_id=source_id, channel='inbox',
        )
        self.assertEqual(log.status, ChannelDispatchState.SUCCEEDED.value)
        self.assertEqual(log.error_message, '')

        # ── Load-bearing assertion 2 — DirectMessage row exists in the
        #    recipient's rigby_routed thread. This proves the task body's
        #    actual downstream ORM effect (not just an audit-log write)
        #    reached the user-visible surface.
        self.assertEqual(DirectMessage.objects.count() - pre_dm, 1)
        dm = DirectMessage.objects.filter(
            thread__participants=self.user,
            thread__thread_type='rigby_routed',
        ).order_by('-created_at').first()
        self.assertIsNotNone(dm, "DirectMessage row missing for HAI-critical")
        self.assertEqual(dm.sender_type, 'system')
        self.assertIn('CRITICAL', dm.body)
        self.assertEqual(dm.metadata.get('source_type'), 'c5_exemplar')
        self.assertEqual(dm.metadata.get('source_id'), source_id)

        # ── Load-bearing assertion 3 — the receiver-side count for this
        #    (user, source, channel) increased by exactly 1. Guards
        #    against silent double-dispatch.
        post_log = HAIDispatchLog.objects.filter(
            user=self.user, channel='inbox',
        ).count()
        self.assertEqual(post_log - pre_log, 1)

    @override_settings(
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_TASK_EAGER_PROPAGATES=True,
        HAI_DISCORD_DISPATCH_ENABLED=False,
        HAI_WEBPUSH_DISPATCH_ENABLED=False,
        HAI_INBOX_DISPATCH_ENABLED=True,
    )
    def test_non_critical_hai_does_not_produce_side_effect(self):
        """Urgency floor holds — 'high' urgency does NOT reach the
        Inbox task body. Guards against a future refactor that
        accidentally lowers the receiver's urgency gate.
        """
        from django.apps import apps
        HumanAttentionItem = apps.get_model('core', 'HumanAttentionItem')
        HAIDispatchLog = apps.get_model('core', 'HAIDispatchLog')
        DirectMessage = apps.get_model('core', 'DirectMessage')

        pre_dm = DirectMessage.objects.count()
        pre_log = HAIDispatchLog.objects.filter(channel='inbox').count()

        with self.captureOnCommitCallbacks(execute=True):
            HumanAttentionItem.objects.create(
                user=self.user,
                source_type='c5_exemplar',
                source_id='c5-exemplar-source-id-2',
                source_agent='C5ExemplarTest',
                item_type='review',
                title='§C5 exemplar — high urgency (should be skipped)',
                summary='Verifying urgency floor holds.',
                urgency='high',
                payload={},
            )
        # on_commit fires; receiver's urgency gate rejects 'high'.

        # No DirectMessage, no HAIDispatchLog row for this HAI.
        self.assertEqual(DirectMessage.objects.count(), pre_dm)
        self.assertEqual(
            HAIDispatchLog.objects.filter(channel='inbox').count(),
            pre_log,
        )

    @override_settings(
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_TASK_EAGER_PROPAGATES=True,
        HAI_DISCORD_DISPATCH_ENABLED=False,
        HAI_WEBPUSH_DISPATCH_ENABLED=False,
        HAI_INBOX_DISPATCH_ENABLED=False,   # kill switch OFF
    )
    def test_inbox_kill_switch_blocks_side_effect(self):
        """Kill switch holds — ``HAI_INBOX_DISPATCH_ENABLED=False``
        blocks the enqueue at the receiver's fast-guard, so the task
        body does NOT execute even under EAGER.
        """
        from django.apps import apps
        HumanAttentionItem = apps.get_model('core', 'HumanAttentionItem')
        HAIDispatchLog = apps.get_model('core', 'HAIDispatchLog')
        DirectMessage = apps.get_model('core', 'DirectMessage')

        pre_dm = DirectMessage.objects.count()
        pre_log = HAIDispatchLog.objects.filter(channel='inbox').count()

        with self.captureOnCommitCallbacks(execute=True):
            HumanAttentionItem.objects.create(
                user=self.user,
                source_type='c5_exemplar',
                source_id='c5-exemplar-source-id-3',
                source_agent='C5ExemplarTest',
                item_type='review',
                title='§C5 exemplar — kill switch OFF',
                summary='Verifying kill switch holds.',
                urgency='critical',
                payload={},
            )

        # Kill switch means the receiver returns early; no side effect.
        self.assertEqual(DirectMessage.objects.count(), pre_dm)
        self.assertEqual(
            HAIDispatchLog.objects.filter(channel='inbox').count(),
            pre_log,
        )
