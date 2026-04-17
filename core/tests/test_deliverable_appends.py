"""
Session 1098 Fix B-full — DeliverableAppend service tests.
=========================================================

Covers the 7 test cases from
``docs/plans/SESSION_1098_FIX_B_FULL_TICKET.md``:

    1. append_is_idempotent
    2. append_chunks_streaming
    3. initiative_promotion_race_detects_mismatch
    4. missing_target_deliverable_raises
    5. concurrent_appends_serialize
    6. superseded_emits_metric (Session 1098: verified via fallback row)
    7. empty_content_is_noop

Plus feature-flag off test and idempotency-race-loser test for
completeness.

Run::

    python manage.py test core.tests.test_deliverable_appends -v2
"""

import threading
import uuid
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase, TransactionTestCase, override_settings

from core.models import Deliverable, Initiative
from core.models_deliverable_appends import DeliverableAppend
from core.models_skin_layer import ProjectWorkspace
from core.services.deliverable_append_service import (
    AppendResult,
    FeatureDisabledError,
    append_to_deliverable,
)


User = get_user_model()


# =========================================================================
# Shared fixtures
# =========================================================================


def _make_test_data(cls):
    """Create user + workspace + initiative + deliverable."""
    cls.user = User.objects.create_user(
        username=f'b-full-test-{uuid.uuid4().hex[:8]}',
        email='bfull@example.com',
        password='x',
        is_superuser=True,
    )
    cls.workspace = ProjectWorkspace.objects.create(
        user=cls.user, name='B-full Test Workspace',
        allow_autonomous_writes=True,
    )
    cls.initiative = Initiative.objects.create(
        name='B-full Test Initiative', status='ACTIVE', current_stage=1,
    )
    cls.deliverable = Deliverable.objects.create(
        title='B-full Target Deliverable',
        content='original content — ',
        agent_name='TestAgent',
        category='Test',
        deliverable_type='document',
        user=cls.user,
        workspace_id=str(cls.workspace.id),
        initiative_id=str(cls.initiative.id),
    )


# =========================================================================
# Feature flag OFF — caller must fall back
# =========================================================================


class FeatureFlagOffTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        _make_test_data(cls)

    @override_settings(DELIVERABLE_APPEND_ENABLED=False)
    def test_feature_flag_off_raises(self):
        with self.assertRaises(FeatureDisabledError):
            append_to_deliverable(
                deliverable_id=str(self.deliverable.id),
                call_id=str(uuid.uuid4()),
                content='should not write',
                agent_name='TestAgent',
            )


# =========================================================================
# Happy-path + idempotency — the 7 ticket cases
# =========================================================================


@override_settings(DELIVERABLE_APPEND_ENABLED=True)
class DeliverableAppendHappyPathTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        _make_test_data(cls)

    def test_append_applies_content(self):
        call_id = str(uuid.uuid4())
        result = append_to_deliverable(
            deliverable_id=str(self.deliverable.id),
            call_id=call_id,
            content='appended text',
            agent_name='TestAgent',
        )
        self.assertEqual(result.status, 'committed')
        self.assertIsInstance(result.append_offset, int)
        self.deliverable.refresh_from_db()
        self.assertIn('appended text', self.deliverable.content)

    def test_append_is_idempotent(self):
        """Ticket case #1. Repeat call with same call_id is a no-op;
        Deliverable.content unchanged after second call."""
        call_id = str(uuid.uuid4())
        first = append_to_deliverable(
            deliverable_id=str(self.deliverable.id),
            call_id=call_id,
            content='ONCE',
            agent_name='TestAgent',
        )
        self.deliverable.refresh_from_db()
        after_first = self.deliverable.content

        second = append_to_deliverable(
            deliverable_id=str(self.deliverable.id),
            call_id=call_id,
            content='SHOULD NOT APPEND',
            agent_name='TestAgent',
        )
        self.deliverable.refresh_from_db()
        self.assertEqual(after_first, self.deliverable.content,
                         'repeat call_id must not double-append')
        self.assertEqual(first.call_id, second.call_id)
        self.assertEqual(first.append_offset, second.append_offset)
        self.assertEqual(second.status, 'committed')

    def test_append_chunks_streaming(self):
        """Ticket case #2. Three chunks with same call_id + chunk_index
        0/1/2 commit in order; content is chunk0+chunk1+chunk2."""
        call_id = str(uuid.uuid4())
        for i, chunk in enumerate(['A', 'B', 'C']):
            append_to_deliverable(
                deliverable_id=str(self.deliverable.id),
                call_id=call_id,
                chunk_index=i,
                content=chunk,
                agent_name='TestAgent',
            )
        self.deliverable.refresh_from_db()
        # Appends happen in offset order (each after the previous).
        self.assertIn('ABC', self.deliverable.content)
        rows = DeliverableAppend.objects.filter(
            deliverable_id=self.deliverable.id, call_id=call_id,
        ).order_by('chunk_index')
        self.assertEqual([r.chunk_index for r in rows], [0, 1, 2])
        self.assertTrue(all(r.status == 'committed' for r in rows))

    def test_missing_target_deliverable_raises(self):
        """Ticket case #4. Unknown deliverable_id → structured error
        (not silent no-op)."""
        with self.assertRaises(Deliverable.DoesNotExist):
            append_to_deliverable(
                deliverable_id=str(uuid.uuid4()),
                call_id=str(uuid.uuid4()),
                content='nope',
                agent_name='TestAgent',
            )

    def test_empty_content_is_noop_but_commits(self):
        """Ticket case #7. Empty string appends a zero-length record
        that still commits (offset = current length)."""
        call_id = str(uuid.uuid4())
        before = self.deliverable.content
        result = append_to_deliverable(
            deliverable_id=str(self.deliverable.id),
            call_id=call_id,
            content='',
            agent_name='TestAgent',
        )
        self.deliverable.refresh_from_db()
        self.assertEqual(self.deliverable.content, before,
                         'empty append must not change content')
        self.assertEqual(result.status, 'committed')


# =========================================================================
# Race protection — initiative promotion
# =========================================================================


@override_settings(DELIVERABLE_APPEND_ENABLED=True)
class InitiativePromotionRaceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        _make_test_data(cls)

    def test_initiative_promotion_race_detects_mismatch(self):
        """Ticket case #3. Caller expects initiative A; deliverable now
        links initiative B. Append lands as 'superseded' with fallback
        id set; original deliverable is UNTOUCHED."""
        # Caller resolved expected_initiative_id=initiative.id.
        expected_initiative = self.initiative

        # While the caller was working, the deliverable was promoted to
        # a different initiative.
        other_initiative = Initiative.objects.create(
            name='Promoted Elsewhere', status='ACTIVE', current_stage=2,
        )
        Deliverable.objects.filter(id=self.deliverable.id).update(
            initiative_id=str(other_initiative.id),
        )

        before = Deliverable.objects.get(id=self.deliverable.id).content

        result = append_to_deliverable(
            deliverable_id=str(self.deliverable.id),
            call_id=str(uuid.uuid4()),
            content='SHOULD NOT LAND ON TARGET',
            agent_name='TestAgent',
            expected_initiative_id=str(expected_initiative.id),
        )

        self.assertEqual(result.status, 'superseded')
        self.assertIsNotNone(result.fallback_deliverable_id)
        self.assertIn('initiative mismatch', result.failure_reason)

        # Original deliverable is unchanged — content must NOT include
        # the superseded append.
        after = Deliverable.objects.get(id=self.deliverable.id).content
        self.assertEqual(before, after)
        self.assertNotIn('SHOULD NOT LAND ON TARGET', after)

        # Fallback deliverable carries the rescued content.
        fallback = Deliverable.objects.get(id=result.fallback_deliverable_id)
        self.assertIn('SHOULD NOT LAND ON TARGET', fallback.content)
        # deliverable_factory auto-prepends agent_name to the title,
        # so our "[SUPERSEDED INITIATIVE]" marker ends up mid-string.
        self.assertIn('[SUPERSEDED INITIATIVE]', fallback.title)

        # A superseded DeliverableAppend row was recorded for metrics.
        sup_row = DeliverableAppend.objects.get(call_id=result.call_id)
        self.assertEqual(sup_row.status, 'superseded')

    def test_matching_initiative_id_commits_normally(self):
        """When expected matches actual, append goes through as committed."""
        result = append_to_deliverable(
            deliverable_id=str(self.deliverable.id),
            call_id=str(uuid.uuid4()),
            content='matches initiative',
            agent_name='TestAgent',
            expected_initiative_id=str(self.initiative.id),
        )
        self.assertEqual(result.status, 'committed')


# =========================================================================
# Concurrent writers — unique constraint serializes
# =========================================================================


@override_settings(DELIVERABLE_APPEND_ENABLED=True)
class ConcurrentAppendTests(TransactionTestCase):
    """Ticket case #5. TransactionTestCase so each test starts with a
    clean DB — concurrent writers need real commits to observe each
    other's state."""

    def setUp(self):
        _make_test_data(self)

    def test_concurrent_appends_serialize(self):
        """Two threads append with different call_ids. Both commit, both
        offsets are correct, content contains both substrings."""
        call_id_a = str(uuid.uuid4())
        call_id_b = str(uuid.uuid4())
        barrier = threading.Barrier(2)
        results = {}

        def _writer(name, cid, body):
            barrier.wait(timeout=5)
            try:
                results[name] = append_to_deliverable(
                    deliverable_id=str(self.deliverable.id),
                    call_id=cid,
                    content=body,
                    agent_name=f'Worker-{name}',
                )
            except Exception as exc:
                results[name] = exc

        t1 = threading.Thread(target=_writer, args=('A', call_id_a, 'AAAAA'))
        t2 = threading.Thread(target=_writer, args=('B', call_id_b, 'BBBBB'))
        t1.start(); t2.start()
        t1.join(timeout=10); t2.join(timeout=10)

        # Both results are AppendResult (no exceptions).
        a_result = results.get('A')
        b_result = results.get('B')
        self.assertIsInstance(a_result, AppendResult, f'A result: {a_result!r}')
        self.assertIsInstance(b_result, AppendResult, f'B result: {b_result!r}')

        self.assertEqual(results['A'].status, 'committed')
        self.assertEqual(results['B'].status, 'committed')
        # Different offsets — SELECT FOR UPDATE serialized them.
        self.assertNotEqual(
            results['A'].append_offset,
            results['B'].append_offset,
            'concurrent appends must get distinct offsets',
        )

        self.deliverable.refresh_from_db()
        self.assertIn('AAAAA', self.deliverable.content)
        self.assertIn('BBBBB', self.deliverable.content)

    def test_idempotency_under_race(self):
        """Two threads with the SAME call_id + chunk_index — both must
        return the same committed row; Deliverable.content includes the
        payload exactly once."""
        call_id = str(uuid.uuid4())
        barrier = threading.Barrier(2)
        results = {}

        def _writer(name):
            barrier.wait(timeout=5)
            try:
                results[name] = append_to_deliverable(
                    deliverable_id=str(self.deliverable.id),
                    call_id=call_id,
                    content='ONCE_ONLY',
                    agent_name='IdempotentWorker',
                )
            except Exception as exc:
                results[name] = exc

        t1 = threading.Thread(target=_writer, args=('A',))
        t2 = threading.Thread(target=_writer, args=('B',))
        t1.start(); t2.start()
        t1.join(timeout=10); t2.join(timeout=10)

        a, b = results['A'], results['B']
        self.assertEqual(a.call_id, b.call_id)
        self.assertEqual(a.append_offset, b.append_offset,
                         'both callers see the same committed offset')

        self.deliverable.refresh_from_db()
        # Content should contain ONCE_ONLY exactly once.
        self.assertEqual(self.deliverable.content.count('ONCE_ONLY'), 1)
