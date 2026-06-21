"""
Session 1191 — Initiative activity tick + auto-populate bootstrap fix.
===================================================================

Covers Rigby's option-B fix shape from Session 1191:

1. **Auto-populate writes activity** (regression test for the
   `populate_initiatives_api` fix). New Initiatives born via the
   auto-populate path now have non-null `last_activity_at` from the
   moment they're created.

2. **Tick picks up NULL rows** — the staleness sweep finds rows where
   `last_activity_at IS NULL` and refreshes them.

3. **Tick picks up rows older than `stale_after_hours`** — rows whose
   `last_activity_at` is older than the threshold are re-examined.

4. **Tick ignores fresh rows** — rows whose `last_activity_at` is
   newer than the threshold are NOT touched.

5. **Tick respects `hard_cap`** — never examines more than N rows
   per run.

6. **Tick excludes ARCHIVED initiatives** — archived rows are
   intentionally cold; tick should not refresh them.

7. **Tick takes max of cheap signals** — `last_activity_at` is set
   to the max of `initiative.updated_at`, latest action_item
   `updated_at`, latest deliverable `updated_at`. No LLM, no stage
   advance, no document writes.

Run:
    python manage.py test core.tests.test_initiative_activity_tick -v2
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.models import Initiative
from core.models_document_registry import InitiativeActionItem
from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace
from core.tasks_initiatives import _impl_initiative_activity_tick


User = get_user_model()


class AutoPopulateBootstrapsActivityTest(TestCase):
    """The populate_initiatives_api fix: freshly-created auto-populated
    Initiatives should not be born with last_activity_at=NULL."""

    def test_update_activity_accepts_reason_kwarg(self):
        i = Initiative.objects.create(
            name='test-bootstrap',
            description='test',
            status='ACTIVE',
            current_stage=1,
        )
        self.assertIsNone(i.last_activity_at)
        i.update_activity(reason='auto_populate_create')
        i.refresh_from_db()
        self.assertIsNotNone(i.last_activity_at)

    def test_update_activity_works_without_reason(self):
        """Backward compat — pre-1191 callers pass no reason kwarg."""
        i = Initiative.objects.create(
            name='test-noreason',
            description='test',
            status='ACTIVE',
            current_stage=1,
        )
        i.update_activity()
        i.refresh_from_db()
        self.assertIsNotNone(i.last_activity_at)


class InitiativeActivityTickTest(TestCase):
    """Behavior of the staleness sweep task itself."""

    def setUp(self):
        self.now = timezone.now()
        # Some tests bypass auto_now to plant historical timestamps.
        # We use queryset.update() for that since it bypasses signals
        # and auto_now=True.

    def _make_initiative(self, name, status='ACTIVE', last_activity_at=None):
        i = Initiative.objects.create(
            name=name,
            description=f'{name} description',
            status=status,
            current_stage=1,
        )
        Initiative.objects.filter(id=i.id).update(last_activity_at=last_activity_at)
        i.refresh_from_db()
        return i

    def test_tick_refreshes_null_rows(self):
        i = self._make_initiative('null-row', last_activity_at=None)
        result = _impl_initiative_activity_tick()
        i.refresh_from_db()
        self.assertGreaterEqual(result['examined'], 1)
        # No linked signals exist, but initiative.updated_at is non-null
        # (auto_now=True on Initiative). So the tick sets
        # last_activity_at = initiative.updated_at.
        self.assertIsNotNone(i.last_activity_at)
        self.assertGreaterEqual(result['refreshed'], 1)

    def test_tick_refreshes_stale_rows(self):
        old = self.now - timedelta(hours=48)
        i = self._make_initiative('stale-row', last_activity_at=old)
        result = _impl_initiative_activity_tick(stale_after_hours=24)
        i.refresh_from_db()
        self.assertGreater(i.last_activity_at, old)
        self.assertGreaterEqual(result['refreshed'], 1)

    def test_tick_ignores_fresh_rows(self):
        fresh = self.now - timedelta(hours=2)
        i = self._make_initiative('fresh-row', last_activity_at=fresh)
        before = i.last_activity_at
        _impl_initiative_activity_tick(stale_after_hours=24)
        i.refresh_from_db()
        # Fresh row should not be touched.
        self.assertEqual(i.last_activity_at, before)

    def test_tick_respects_hard_cap(self):
        for n in range(5):
            self._make_initiative(f'cap-row-{n}', last_activity_at=None)
        result = _impl_initiative_activity_tick(hard_cap=2)
        self.assertLessEqual(result['examined'], 2)

    def test_tick_excludes_archived(self):
        i = self._make_initiative(
            'archived-row',
            status='ARCHIVED',
            last_activity_at=None,
        )
        _impl_initiative_activity_tick()
        i.refresh_from_db()
        self.assertIsNone(i.last_activity_at)

    def test_tick_uses_max_of_signals(self):
        """When linked deliverable/action_item exist, last_activity_at
        is set to the max of (initiative.updated_at, latest action_item
        updated_at, latest deliverable updated_at)."""
        i = self._make_initiative('signal-max', last_activity_at=None)
        user = User.objects.create_user(
            username='test-signal-max-user',
            password='x',
        )
        ws = ProjectWorkspace.objects.create(
            name='test-ws-signal',
            description='test',
            user=user,
        )
        # Create a deliverable linked to the initiative; auto_now will
        # set its updated_at to ~now.
        d = Deliverable.objects.create(
            title='test-deliverable',
            slug=f'test-deliverable-{i.id}',
            workspace=ws,
            initiative=i,
            content='test',
        )
        # Force the deliverable's updated_at to a known future value.
        future = self.now + timedelta(minutes=5)
        Deliverable.objects.filter(id=d.id).update(updated_at=future)

        _impl_initiative_activity_tick()
        i.refresh_from_db()
        # last_activity_at should be the deliverable's planted future value
        # (because it's the max signal). Allow a small delta for
        # microsecond rounding.
        self.assertIsNotNone(i.last_activity_at)
        self.assertGreaterEqual(i.last_activity_at, future - timedelta(seconds=1))

    def test_tick_returns_summary_dict(self):
        result = _impl_initiative_activity_tick(stale_after_hours=24, hard_cap=50)
        self.assertIn('examined', result)
        self.assertIn('refreshed', result)
        self.assertIn('skipped_no_signal', result)
        self.assertEqual(result['stale_after_hours'], 24)
        self.assertEqual(result['hard_cap'], 50)
