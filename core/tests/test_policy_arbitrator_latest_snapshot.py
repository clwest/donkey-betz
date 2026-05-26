"""
Tests for PolicyArbitrator.get_latest_snapshot() and the
`latest_overrides_snapshot` PA tool action.

Session 1163 B-style storage: per-cycle append-only rows in the
`FinalAppliedOverrides` model. Replaces the prior Session 1163 C-style
single-row-overwrite in `SystemConfiguration(key='policy_arbitrator_snapshot')`.
See Disclosure L §14.7 + narrative `SELF_TUNING_AND_EXPERIMENTATION.md`
§6.4 for the lineage. Tests pin both the latest-only and time-travel
read paths; the writer is exercised via `record_overrides_snapshot`.
"""
import uuid
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from core.models import FinalAppliedOverrides
from core.services.ops_autopilot.governance import PolicyArbitrator


def _create_snapshot(cycle_ts, knobs=None, knob_count=None, cycle_id=None):
    """Test factory — insert one FinalAppliedOverrides row."""
    knobs = knobs or {}
    return FinalAppliedOverrides.objects.create(
        cycle_id=cycle_id or uuid.uuid4(),
        cycle_ts=cycle_ts,
        knob_count=knob_count if knob_count is not None else len(knobs),
        applied_values=knobs,
    )


class GetLatestSnapshotTests(TestCase):
    """Direct unit tests for PolicyArbitrator.get_latest_snapshot()."""

    def test_returns_friendly_null_when_table_is_empty(self):
        """No rows → found=False with explainer note."""
        result = PolicyArbitrator().get_latest_snapshot()

        self.assertFalse(result['found'])
        self.assertIsNone(result['cycle_id'])
        self.assertIsNone(result['cycle_ts'])
        self.assertIsNone(result['row_created_at'])
        self.assertIsNone(result['queried_at'])
        self.assertEqual(result['knob_count'], 0)
        self.assertEqual(result['knobs'], {})
        self.assertEqual(result['storage']['model'], 'FinalAppliedOverrides')
        self.assertIn(
            'append-only per-cycle row',
            result['storage']['mechanism'],
        )
        self.assertIn(
            'No arbitrator snapshot matches the query',
            result['note'],
        )

    def test_returns_latest_when_at_is_unset(self):
        """Multiple rows → unset `at` returns the most recent by cycle_ts."""
        now = timezone.now()
        _create_snapshot(now - timedelta(minutes=30), knobs={'a': {'value': '1'}})
        _create_snapshot(now - timedelta(minutes=20), knobs={'b': {'value': '2'}})
        latest = _create_snapshot(
            now - timedelta(minutes=10),
            knobs={'c': {'value': '3'}},
        )

        result = PolicyArbitrator().get_latest_snapshot()

        self.assertTrue(result['found'])
        self.assertEqual(result['cycle_id'], str(latest.cycle_id))
        self.assertEqual(result['knob_count'], 1)
        self.assertIn('c', result['knobs'])
        self.assertIsNone(result['queried_at'])
        self.assertIsNotNone(result['row_created_at'])

    def test_time_travel_returns_snapshot_active_at_given_time(self):
        """`at=<between two rows>` returns the row with the largest cycle_ts <= at."""
        now = timezone.now()
        t30 = now - timedelta(minutes=30)
        t20 = now - timedelta(minutes=20)
        t10 = now - timedelta(minutes=10)

        r30 = _create_snapshot(t30, knobs={'k': {'value': '30'}})
        r20 = _create_snapshot(t20, knobs={'k': {'value': '20'}})
        _create_snapshot(t10, knobs={'k': {'value': '10'}})

        # Query at T-15 → should return r20 (most recent <= T-15)
        at = now - timedelta(minutes=15)
        result = PolicyArbitrator().get_latest_snapshot(at=at)

        self.assertTrue(result['found'])
        self.assertEqual(result['cycle_id'], str(r20.cycle_id))
        self.assertEqual(result['knobs']['k']['value'], '20')
        self.assertEqual(result['queried_at'], at.isoformat())

        # Query at T-25 → should return r30
        at_25 = now - timedelta(minutes=25)
        result_25 = PolicyArbitrator().get_latest_snapshot(at=at_25)
        self.assertTrue(result_25['found'])
        self.assertEqual(result_25['cycle_id'], str(r30.cycle_id))

    def test_time_travel_returns_friendly_null_when_no_row_before_at(self):
        """`at=<before first row>` → found=False, note explains the gap."""
        now = timezone.now()
        _create_snapshot(now, knobs={'k': {'value': '1'}})

        before = now - timedelta(hours=1)
        result = PolicyArbitrator().get_latest_snapshot(at=before)

        self.assertFalse(result['found'])
        self.assertEqual(result['queried_at'], before.isoformat())
        self.assertIn(
            'no cycle completed before that time',
            result['note'],
        )

    def test_accepts_iso_string_for_at(self):
        """`at` accepts an ISO 8601 string in addition to a datetime."""
        now = timezone.now()
        row = _create_snapshot(now - timedelta(hours=1), knobs={'x': {'value': 'v'}})

        result = PolicyArbitrator().get_latest_snapshot(at=now.isoformat())

        self.assertTrue(result['found'])
        self.assertEqual(result['cycle_id'], str(row.cycle_id))
        self.assertEqual(result['queried_at'], now.isoformat())

    def test_unparseable_at_string_fails_loud(self):
        """Bad `at` string → found=False with parse error explainer, no crash."""
        _create_snapshot(timezone.now(), knobs={'k': {'value': '1'}})

        result = PolicyArbitrator().get_latest_snapshot(at='not-a-datetime')

        self.assertFalse(result['found'])
        self.assertEqual(result['queried_at'], 'not-a-datetime')
        self.assertIn(
            "Could not parse `at` argument",
            result['note'],
        )

    def test_storage_context_documents_new_mechanism(self):
        """The storage block names the as-built append-only mechanism."""
        result = PolicyArbitrator().get_latest_snapshot()

        self.assertEqual(result['storage']['model'], 'FinalAppliedOverrides')
        self.assertEqual(
            result['storage']['table'],
            'core_final_applied_overrides',
        )
        self.assertIn('90-day retention', result['storage']['mechanism'])


class RecordOverridesSnapshotTests(TestCase):
    """Tests for the writer half of the cycle — record_overrides_snapshot."""

    def test_writer_creates_new_row_per_call(self):
        """Each invocation appends a row — no overwrite."""
        arb = PolicyArbitrator()
        now = timezone.now()

        result_a = arb.record_overrides_snapshot(now, uuid.uuid4())
        result_b = arb.record_overrides_snapshot(
            now + timedelta(minutes=10), uuid.uuid4(),
        )

        self.assertEqual(FinalAppliedOverrides.objects.count(), 2)
        self.assertIn('cycle_id', result_a)
        self.assertIn('cycle_id', result_b)
        self.assertNotEqual(result_a['cycle_id'], result_b['cycle_id'])


class LatestOverridesSnapshotHandlerTests(TestCase):
    """Smoke test for the `latest_overrides_snapshot` autopilot_tool action."""

    def test_handler_returns_action_label_and_snapshot_fields(self):
        """The dispatcher handler echoes the action label + snapshot dict."""
        from core.services.td_handlers_ops import OpsHandlersMixin

        _create_snapshot(
            timezone.now(),
            knobs={'handler_test': {'value': 'v', 'owner': 'test', 'priority': 99}},
        )

        handler = OpsHandlersMixin()
        result = handler._handle_autopilot(
            tool_name='autopilot_tool',
            payload={'action': 'latest_overrides_snapshot'},
            user_id=None,
            trace_id='test-trace',
        )

        self.assertEqual(result['action'], 'latest_overrides_snapshot')
        self.assertTrue(result['found'])
        self.assertEqual(
            result['storage']['table'],
            'core_final_applied_overrides',
        )

    def test_handler_passes_at_argument_through(self):
        """payload['at'] reaches PolicyArbitrator.get_latest_snapshot."""
        from core.services.td_handlers_ops import OpsHandlersMixin

        now = timezone.now()
        old = _create_snapshot(
            now - timedelta(hours=2),
            knobs={'k': {'value': 'old'}},
        )
        _create_snapshot(now, knobs={'k': {'value': 'new'}})

        handler = OpsHandlersMixin()
        at = (now - timedelta(hours=1)).isoformat()
        result = handler._handle_autopilot(
            tool_name='autopilot_tool',
            payload={'action': 'latest_overrides_snapshot', 'at': at},
            user_id=None,
            trace_id='test-trace',
        )

        self.assertEqual(result['action'], 'latest_overrides_snapshot')
        self.assertTrue(result['found'])
        self.assertEqual(result['cycle_id'], str(old.cycle_id))
        self.assertEqual(result['queried_at'], at)


class PurgeRetentionTests(TestCase):
    """Tests for the 90-day retention purge."""

    def test_purge_removes_rows_older_than_window(self):
        """Rows with cycle_ts older than 90 days are deleted; newer rows survive."""
        from core.tasks import purge_finaloverrides_older_than_90d

        now = timezone.now()
        old = _create_snapshot(
            now - timedelta(days=120),
            knobs={'a': {'value': '1'}},
        )
        edge = _create_snapshot(
            now - timedelta(days=89),
            knobs={'b': {'value': '2'}},
        )
        recent = _create_snapshot(
            now - timedelta(hours=1),
            knobs={'c': {'value': '3'}},
        )

        result = purge_finaloverrides_older_than_90d()

        surviving = set(FinalAppliedOverrides.objects.values_list('id', flat=True))
        self.assertIn(edge.id, surviving)
        self.assertIn(recent.id, surviving)
        self.assertNotIn(old.id, surviving)
        self.assertEqual(result['deleted'], 1)
        self.assertEqual(result['retention_days'], 90)
