"""
publish_intent enum — model field + resolver + COO filter integration.
========================================================================

Session 1095: Rigby's architectural refinement. Shipped as a three-part
vertical slice:

1. `Deliverable.publish_intent` CharField choice with 3 values
   (internal_only / publish_candidate / publish_required)
2. `deliverable_factory.resolve_publish_intent(agent, explicit)` — default
   resolver that defers to explicit caller override first, then a per-agent
   table, then falls back to internal_only (safest default per Rigby)
3. COO diagnostic filter `COO_DIAG_PUBLISH_INTENTS` CSV that scopes the
   velocity + publishing_jam + review_age gates to intent-to-publish
   deliverables. Replaces the Session 1094 `PUBLISHABLE_TYPES` CSV bridge.

Run:
    python manage.py test core.tests.test_publish_intent_enum -v2
"""
from datetime import timedelta
from unittest.mock import patch

from django.test import SimpleTestCase, TransactionTestCase
from django.utils import timezone

from core.services.deliverable_factory import resolve_publish_intent


# =============================================================================
# resolve_publish_intent — pure-logic unit tests
# =============================================================================

class ResolvePublishIntentTests(SimpleTestCase):

    def test_default_internal_only_for_unknown_agent(self):
        self.assertEqual(resolve_publish_intent('SomeNewAgent'), 'internal_only')

    def test_initiative_pipeline_is_publish_candidate(self):
        self.assertEqual(
            resolve_publish_intent('InitiativePipeline'),
            'publish_candidate',
        )

    def test_content_writer_agent_is_publish_candidate(self):
        self.assertEqual(
            resolve_publish_intent('ContentWriterAgent'),
            'publish_candidate',
        )

    def test_explicit_override_wins_over_lookup(self):
        """Caller-provided value takes precedence over the per-agent table."""
        # InitiativePipeline defaults to publish_candidate, but caller
        # can explicitly flag this instance as required
        self.assertEqual(
            resolve_publish_intent('InitiativePipeline', 'publish_required'),
            'publish_required',
        )
        # Explicit internal_only beats the lookup default
        self.assertEqual(
            resolve_publish_intent('InitiativePipeline', 'internal_only'),
            'internal_only',
        )

    def test_empty_explicit_ignored(self):
        """Empty-string explicit falls through to lookup table."""
        self.assertEqual(
            resolve_publish_intent('InitiativePipeline', ''),
            'publish_candidate',
        )

    def test_empty_agent_name_defaults_to_internal_only(self):
        self.assertEqual(resolve_publish_intent(''), 'internal_only')
        self.assertEqual(resolve_publish_intent(None), 'internal_only')  # type: ignore[arg-type]


# =============================================================================
# Factory integration — Deliverable created via create_deliverable gets
# the right publish_intent
# =============================================================================

class DeliverableFactoryPublishIntentTests(TransactionTestCase):

    def test_known_publisher_gets_publish_candidate(self):
        from core.services.deliverable_factory import create_deliverable
        d = create_deliverable(
            title='My Initiative Brief',
            content='some content long enough to pass quality gate ' * 10,
            agent_name='InitiativePipeline',
            deliverable_type='document',
        )
        self.assertIsNotNone(d, 'Factory should have created the deliverable')
        self.assertEqual(d.publish_intent, 'publish_candidate')

    def test_unknown_agent_gets_internal_only(self):
        from core.services.deliverable_factory import create_deliverable
        d = create_deliverable(
            title='Stock Analyst Daily Report',
            content='analysis content long enough to pass the quality gate ' * 10,
            agent_name='StockAnalystAgent',
            deliverable_type='analysis',
        )
        self.assertIsNotNone(d)
        self.assertEqual(d.publish_intent, 'internal_only')

    def test_explicit_kwarg_overrides_default(self):
        from core.services.deliverable_factory import create_deliverable
        d = create_deliverable(
            title='Critical Communique',
            content='time-sensitive content long enough to pass quality gate ' * 10,
            agent_name='StockAnalystAgent',  # default would be internal_only
            deliverable_type='document',
            publish_intent='publish_required',
        )
        self.assertIsNotNone(d)
        self.assertEqual(d.publish_intent, 'publish_required')


# =============================================================================
# COO gate filter integration — publish_intent scopes metrics
# =============================================================================

class CooPublishIntentFilterTests(TransactionTestCase):
    """With `COO_DIAG_PUBLISH_INTENTS` set, velocity + review_backlog gates
    scope to only deliverables matching the specified intents."""

    def setUp(self):
        from core.models_deliverables import Deliverable
        Deliverable.objects.all().delete()

        # 10 internal_only "analyses" (default intent)
        for i in range(10):
            Deliverable.objects.create(
                title=f'analysis-{i}',
                content='content',
                agent_name='StockAnalystAgent',
                deliverable_type='analysis',
                status='ready',
                publish_intent='internal_only',
            )
        # 3 publish_candidate documents
        for i in range(3):
            Deliverable.objects.create(
                title=f'candidate-{i}',
                content='content',
                agent_name='ContentWriterAgent',
                deliverable_type='document',
                status='ready',
                publish_intent='publish_candidate',
            )
        # 2 published publish_candidates (already shipped)
        for i in range(2):
            Deliverable.objects.create(
                title=f'pub-{i}',
                content='content',
                agent_name='InitiativePipeline',
                deliverable_type='document',
                status='published',
                publish_intent='publish_candidate',
            )
        # 1 publish_required (critical flow)
        Deliverable.objects.create(
            title='required-a',
            content='content',
            agent_name='ContentWriterAgent',
            deliverable_type='document',
            status='ready',
            publish_intent='publish_required',
        )

    def _metrics(self, env_overrides=None):
        from core.services.diagnostics.coo_daily import collect_metrics
        now = timezone.now()
        cutoff_24h = now - timedelta(hours=24)
        cutoff_7d = now - timedelta(days=7)
        with patch.dict('os.environ', env_overrides or {}, clear=False):
            return collect_metrics(now, cutoff_24h, cutoff_7d)

    def test_no_filter_counts_all(self):
        """Default = no env var = all 16 deliverables counted."""
        m = self._metrics()
        self.assertEqual(m['velocity']['created_24h'], 16)  # 10 + 3 + 2 + 1
        self.assertEqual(m['velocity']['published_24h'], 2)
        self.assertIsNone(m['velocity']['publish_intents_filter'])
        self.assertEqual(m['review_backlog']['ready_count'], 14)  # 10 + 3 + 1

    def test_publish_candidate_and_required_scopes_to_publishable_pipeline(self):
        """Rigby's recommended filter: skip internal_only noise."""
        m = self._metrics({'COO_DIAG_PUBLISH_INTENTS': 'publish_candidate,publish_required'})
        self.assertEqual(m['velocity']['created_24h'], 6)  # 3 + 2 + 1
        self.assertEqual(m['velocity']['published_24h'], 2)
        self.assertEqual(
            m['velocity']['publish_intents_filter'],
            ['publish_candidate', 'publish_required'],
        )
        self.assertEqual(m['review_backlog']['ready_count'], 4)  # 3 + 1

    def test_publish_required_only_narrowest_scope(self):
        m = self._metrics({'COO_DIAG_PUBLISH_INTENTS': 'publish_required'})
        self.assertEqual(m['velocity']['created_24h'], 1)
        self.assertEqual(m['review_backlog']['ready_count'], 1)

    def test_internal_only_shows_analysis_pile(self):
        """Filtering to internal_only reveals the noisy scheduled-agent analyses."""
        m = self._metrics({'COO_DIAG_PUBLISH_INTENTS': 'internal_only'})
        self.assertEqual(m['velocity']['created_24h'], 10)
        self.assertEqual(m['review_backlog']['ready_count'], 10)

    def test_intent_and_types_filter_and(self):
        """Both env vars set = AND semantics (narrow to rows matching both)."""
        m = self._metrics({
            'COO_DIAG_PUBLISH_INTENTS': 'publish_candidate,publish_required',
            'COO_DIAG_PUBLISHABLE_TYPES': 'document',
        })
        # Still 6 — both filters already selected same rows
        self.assertEqual(m['velocity']['created_24h'], 6)

        # Narrow to intent=required AND type=analysis (no such rows)
        m2 = self._metrics({
            'COO_DIAG_PUBLISH_INTENTS': 'publish_required',
            'COO_DIAG_PUBLISHABLE_TYPES': 'analysis',
        })
        self.assertEqual(m2['velocity']['created_24h'], 0)


# =============================================================================
# Enum sanity
# =============================================================================

class PublishIntentEnumTests(SimpleTestCase):

    def test_three_values(self):
        from core.models_deliverables import PublishIntent
        self.assertEqual(
            set(PublishIntent.values),
            {'internal_only', 'publish_candidate', 'publish_required'},
        )

    def test_field_has_default_internal_only(self):
        from core.models_deliverables import Deliverable
        field = Deliverable._meta.get_field('publish_intent')
        self.assertEqual(field.default, 'internal_only')
        self.assertTrue(field.db_index)
