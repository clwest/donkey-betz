"""
Tests for SystemIntelligenceAgent escalation logic.

Covers:
1. _classify_severity — reclassifies aggregator items correctly
2. Dedup update — create_attention_item refreshes urgency/summary/payload
3. Auto-resolve vs deferred — warning auto-resolves, critical gets deferred
4. Output consistency — counts reflect reclassified severity
"""

from dataclasses import dataclass

from django.test import TestCase
from django.contrib.auth import get_user_model

from core.agents.system_intelligence_agent import SystemIntelligenceAgent

User = get_user_model()

# Direct reference to the static method — avoids self-injection issues
_classify = SystemIntelligenceAgent._classify_severity


@dataclass
class FakeAttentionItem:
    """Mimics core.services.system_state_aggregator.AttentionItem."""
    id: str
    section: str
    category: str
    priority: int
    title: str
    summary: str
    action_url: str = ''
    explanation: str = ''
    recommended_action: str = ''
    severity: str = 'info'
    location: str = ''


class ClassifySeverityTest(TestCase):
    """Test SIA's _classify_severity overrides."""

    def test_stale_key_spider_is_critical(self):
        """Key spiders (coingecko, theodds, etc.) → critical."""
        item = FakeAttentionItem(
            id='spider_stale', section='research',
            category='stale_concern', priority=50,
            title='Stale Spiders (1)',
            summary='No data in 24h: coingecko',
            severity='info',
        )
        self.assertEqual(_classify(item), 'critical')

    def test_stale_nonkey_spider_is_warning(self):
        """Non-key spiders → warning."""
        item = FakeAttentionItem(
            id='spider_stale', section='research',
            category='stale_concern', priority=50,
            title='Stale Spiders (2)',
            summary='No data in 24h: reddit_scraper, wikipedia_spider',
            severity='info',
        )
        self.assertEqual(_classify(item), 'warning')

    def test_stale_signal_clusters_high_count_is_critical(self):
        """50+ stale signal clusters → critical."""
        item = FakeAttentionItem(
            id='signal_stale', section='research',
            category='stale_concern', priority=50,
            title='Stale Signal Clusters: 80',
            summary='80 active cluster(s) not detected in 48h',
            severity='info',
        )
        self.assertEqual(_classify(item), 'critical')

    def test_stale_signal_clusters_medium_count_is_warning(self):
        """10-49 stale signal clusters → warning."""
        item = FakeAttentionItem(
            id='signal_stale', section='research',
            category='stale_concern', priority=50,
            title='Stale Signal Clusters: 15',
            summary='15 active cluster(s) not detected in 48h',
            severity='info',
        )
        self.assertEqual(_classify(item), 'warning')

    def test_stale_signal_clusters_low_count_stays_info(self):
        """<10 stale signal clusters → stays info."""
        item = FakeAttentionItem(
            id='signal_stale', section='research',
            category='stale_concern', priority=50,
            title='Stale Signal Clusters: 5',
            summary='5 active cluster(s) not detected in 48h',
            severity='info',
        )
        self.assertEqual(_classify(item), 'info')

    def test_smoke_failure_is_warning(self):
        item = FakeAttentionItem(
            id='smoke', section='command_center',
            category='health', priority=80,
            title='Smoke Suite Failing: 3 checks',
            summary='3 smoke checks failing',
            severity='info',
        )
        self.assertEqual(_classify(item), 'warning')

    def test_deploy_drift_is_critical(self):
        item = FakeAttentionItem(
            id='drift', section='command_center',
            category='alert', priority=90,
            title='Deploy Drift Detected',
            summary='Code differs from deployed version',
            severity='info',
        )
        self.assertEqual(_classify(item), 'critical')

    def test_overdue_content_stays_info(self):
        """Regular items keep original severity."""
        item = FakeAttentionItem(
            id='overdue_1', section='autonomous',
            category='overdue_task', priority=60,
            title='Overdue: Market Intelligence',
            summary='Content due 325h ago',
            severity='info',
        )
        self.assertEqual(_classify(item), 'info')

    def test_key_spider_in_summary_not_title(self):
        """Spider name in summary (not title) still matches."""
        for spider in ('theodds', 'polygon_finance', 'newsapi', 'etherscan_api'):
            item = FakeAttentionItem(
                id='spider_stale', section='research',
                category='stale_concern', priority=50,
                title='Stale Spiders (1)',
                summary=f'No data in 24h: {spider}',
                severity='info',
            )
            self.assertEqual(
                _classify(item), 'critical',
                f'{spider} should be critical',
            )


class DedupUpdateTest(TestCase):
    """Test that create_attention_item updates existing items on dedup."""

    def setUp(self):
        self.user, _ = User.objects.get_or_create(
            username='sia_test_user',
            defaults={'password': 'test123'},
        )

    def tearDown(self):
        from core.models_human_interface import HumanAttentionItem
        HumanAttentionItem.objects.filter(user=self.user).delete()

    def test_dedup_updates_urgency(self):
        """Second call with higher urgency updates the existing item."""
        from core.services.human_interface_service import get_human_interface_service
        service = get_human_interface_service(self.user)

        # Create initial item at medium urgency
        result1 = service.create_attention_item(
            source_type='test_sia',
            source_id='test:spider_stale',
            source_agent='TestAgent',
            item_type='alert',
            title='[SIA] Test Spider',
            summary='Spider is stale',
            urgency='medium',
            deduplicate=True,
        )
        self.assertFalse(result1.get('deduplicated'))
        item_id = result1['item_id']

        # Second call with critical urgency
        result2 = service.create_attention_item(
            source_type='test_sia',
            source_id='test:spider_stale',
            source_agent='TestAgent',
            item_type='alert',
            title='[SIA] Test Spider',
            summary='Spider is still stale — critical now',
            urgency='critical',
            deduplicate=True,
        )
        self.assertTrue(result2.get('deduplicated'))
        self.assertIn('urgency', result2.get('fields_updated', []))

        # Verify DB state
        from core.models_human_interface import HumanAttentionItem
        item = HumanAttentionItem.objects.get(id=item_id)
        self.assertEqual(item.urgency, 'critical')
        self.assertEqual(item.summary, 'Spider is still stale — critical now')
        self.assertEqual(item.priority_score, 10.0)

    def test_dedup_no_update_when_same(self):
        """Dedup returns empty fields_updated when nothing changed."""
        from core.services.human_interface_service import get_human_interface_service
        service = get_human_interface_service(self.user)

        service.create_attention_item(
            source_type='test_sia',
            source_id='test:same',
            source_agent='TestAgent',
            item_type='alert',
            title='[SIA] Same Item',
            summary='Nothing changes',
            urgency='medium',
            deduplicate=True,
        )

        result2 = service.create_attention_item(
            source_type='test_sia',
            source_id='test:same',
            source_agent='TestAgent',
            item_type='alert',
            title='[SIA] Same Item',
            summary='Nothing changes',
            urgency='medium',
            deduplicate=True,
        )
        self.assertTrue(result2.get('deduplicated'))
        self.assertEqual(result2.get('fields_updated', []), [])


class AutoResolvePolicyTest(TestCase):
    """Test that warning items auto-resolve and critical items get deferred."""

    def setUp(self):
        self.user, _ = User.objects.get_or_create(
            username='sia_policy_user',
            defaults={'password': 'test123'},
        )

    def tearDown(self):
        from core.models_human_interface import HumanAttentionItem
        HumanAttentionItem.objects.filter(user=self.user).delete()

    def test_warning_auto_resolves(self):
        """Warning item not in current findings → status='acted'."""
        from core.models_human_interface import HumanAttentionItem

        item = HumanAttentionItem.objects.create(
            user=self.user,
            source_type='system_intelligence',
            source_id='sia:old_warning',
            source_agent='SystemIntelligenceAgent',
            item_type='alert',
            title='[SIA] Old Warning',
            summary='This warning should auto-resolve',
            urgency='medium',
            status='pending',
        )

        agent = SystemIntelligenceAgent(user=self.user)
        stats = agent._escalate_to_attention_items([])

        item.refresh_from_db()
        self.assertEqual(item.status, 'acted')
        self.assertEqual(item.decision, 'approve')
        self.assertIn('Auto-resolved', item.decision_feedback)
        self.assertEqual(stats['resolved'], 1)

    def test_critical_gets_deferred(self):
        """Critical item not in current findings → status='deferred'."""
        from core.models_human_interface import HumanAttentionItem

        item = HumanAttentionItem.objects.create(
            user=self.user,
            source_type='system_intelligence',
            source_id='sia:old_critical',
            source_agent='SystemIntelligenceAgent',
            item_type='alert',
            title='[SIA] Old Critical',
            summary='This critical needs human sign-off',
            urgency='critical',
            status='pending',
        )

        agent = SystemIntelligenceAgent(user=self.user)
        stats = agent._escalate_to_attention_items([])

        item.refresh_from_db()
        self.assertEqual(item.status, 'deferred')
        self.assertIsNone(item.decision)
        self.assertIn('human confirmation', item.decision_feedback)
        self.assertEqual(stats['deferred_for_review'], 1)
        self.assertEqual(stats['resolved'], 0)


class SeverityCountConsistencyTest(TestCase):
    """Test that SIA output counts use reclassified severity."""

    def test_classify_severity_used_for_counts(self):
        """If _classify_severity promotes items, counts should reflect it."""
        items = [
            FakeAttentionItem(
                id='spider_stale', section='research',
                category='stale_concern', priority=50,
                title='Stale Spiders (1)',
                summary='No data in 24h: coingecko',
                severity='info',
            ),
            FakeAttentionItem(
                id='signal_stale', section='research',
                category='stale_concern', priority=50,
                title='Stale Signal Clusters: 80',
                summary='80 active cluster(s) not detected in 48h',
                severity='info',
            ),
            FakeAttentionItem(
                id='overdue_1', section='autonomous',
                category='overdue_task', priority=60,
                title='Overdue: Market Intelligence',
                summary='Content due 325h ago',
                severity='info',
            ),
        ]

        sia_severities = [_classify(i) for i in items]
        critical_count = sia_severities.count('critical')
        warning_count = sia_severities.count('warning')
        info_count = sia_severities.count('info')

        self.assertEqual(critical_count, 2, 'coingecko + 80 clusters should be critical')
        self.assertEqual(warning_count, 0)
        self.assertEqual(info_count, 1, 'overdue task stays info')
