"""
MythologyAlert → HumanAttentionItem bridge tests — Session 1095 Tier 1b.
=========================================================================

Session 1095 audit found 312 critical MythologyAlerts sitting silent
because nobody looked at /mythology-lab directly. This bridge closes
the operator-visibility gap — when a new critical/high MythologyAlert
is saved, a HumanAttentionItem with item_type='mythology_alert' gets
created for every admin user so the alert surfaces in the governance
inbox Chris already watches.

Tests cover:
- Critical + high severities DO bridge
- Low + medium severities DON'T bridge (too noisy)
- Updates to existing alerts don't re-fire (only `created=True`)
- Bridge failure never breaks the MythologyAlert save
- Payload carries alert_id for operator traceback

Run:
    python manage.py test mythology.tests.test_alert_hai_bridge -v2
"""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from mythology.models import MythologyAlert

User = get_user_model()


class MythologyAlertHAIBridgeTests(TransactionTestCase):

    def setUp(self):
        # Clean slate for every test
        from core.models_human_interface import HumanAttentionItem
        HumanAttentionItem.objects.all().delete()
        MythologyAlert.objects.all().delete()
        self.admin = User.objects.create_user(
            username='myth_admin', password='x', is_staff=True,
        )

    def _count_hais(self, **filters):
        from core.models_human_interface import HumanAttentionItem
        return HumanAttentionItem.objects.filter(**filters).count()

    # ── Bridged severities ─────────────────────────────────────────────

    def test_critical_alert_creates_hai(self):
        MythologyAlert.objects.create(
            alert_type='new_myth',
            severity='critical',
            title='Test critical myth',
            description='desc',
        )
        self.assertGreaterEqual(self._count_hais(item_type='mythology_alert'), 1)

    def test_high_alert_creates_hai(self):
        MythologyAlert.objects.create(
            alert_type='wide_propagation',
            severity='high',
            title='Test high myth',
            description='desc',
        )
        self.assertGreaterEqual(self._count_hais(item_type='mythology_alert'), 1)

    # ── Unbridged severities ────────────────────────────────────────────

    def test_medium_alert_does_not_create_hai(self):
        """Medium alerts stay in mythology DB only — too noisy for inbox."""
        MythologyAlert.objects.create(
            alert_type='pattern_detected',
            severity='medium',
            title='Test medium myth',
            description='desc',
        )
        self.assertEqual(self._count_hais(item_type='mythology_alert'), 0)

    def test_low_alert_does_not_create_hai(self):
        MythologyAlert.objects.create(
            alert_type='pattern_detected',
            severity='low',
            title='Test low myth',
            description='desc',
        )
        self.assertEqual(self._count_hais(item_type='mythology_alert'), 0)

    # ── Update/re-save semantics ────────────────────────────────────────

    def test_acknowledgement_save_does_not_re_fire(self):
        """Editing an existing alert (e.g. acknowledgement) must NOT create
        a second HAI. Only the initial creation fires the bridge."""
        alert = MythologyAlert.objects.create(
            alert_type='new_myth',
            severity='critical',
            title='Test myth',
            description='desc',
        )
        count_after_create = self._count_hais(item_type='mythology_alert')
        self.assertGreaterEqual(count_after_create, 1)

        # Acknowledge + save again
        alert.acknowledged = True
        alert.acknowledged_by = self.admin
        alert.save()

        count_after_update = self._count_hais(item_type='mythology_alert')
        self.assertEqual(count_after_update, count_after_create)

    # ── Payload + provenance ────────────────────────────────────────────

    def test_hai_payload_includes_mythology_alert_id(self):
        """Operator must be able to jump back from HAI → MythologyAlert."""
        from core.models_human_interface import HumanAttentionItem
        alert = MythologyAlert.objects.create(
            alert_type='new_myth',
            severity='critical',
            title='Traceable alert',
            description='must be jumpable',
        )
        hai = HumanAttentionItem.objects.filter(
            item_type='mythology_alert'
        ).first()
        self.assertIsNotNone(hai)
        self.assertEqual(hai.source_id, str(alert.pk))
        self.assertEqual(hai.payload.get('mythology_alert_id'), str(alert.pk))
        self.assertEqual(hai.payload.get('alert_type'), 'new_myth')
        self.assertEqual(hai.payload.get('severity'), 'critical')

    def test_hai_urgency_matches_alert_severity(self):
        from core.models_human_interface import HumanAttentionItem
        MythologyAlert.objects.create(
            alert_type='new_myth', severity='critical',
            title='c', description='d',
        )
        hai = HumanAttentionItem.objects.filter(
            item_type='mythology_alert'
        ).order_by('-created_at').first()
        self.assertEqual(hai.urgency, 'critical')

    def test_hai_source_type_namespaced(self):
        """source_type must include the alert_type for filtering."""
        from core.models_human_interface import HumanAttentionItem
        MythologyAlert.objects.create(
            alert_type='rapid_inflation', severity='high',
            title='r', description='d',
        )
        hai = HumanAttentionItem.objects.filter(
            item_type='mythology_alert'
        ).order_by('-created_at').first()
        self.assertIn('mythology:rapid_inflation', hai.source_type)

    # ── Fail-safe: bridge errors never break the mythology save ─────────

    def test_alert_save_succeeds_if_bridge_raises(self):
        """Bridge failure must not prevent the MythologyAlert from
        persisting. The alert is more important than the governance ping."""
        with patch(
            'core.services.human_attention_bridge.attention_bridge.'
            'create_mythology_alert',
            side_effect=RuntimeError('simulated bridge failure'),
        ):
            alert = MythologyAlert.objects.create(
                alert_type='new_myth', severity='critical',
                title='Must-persist alert', description='d',
            )
        # Alert row is saved despite bridge failure
        self.assertTrue(
            MythologyAlert.objects.filter(pk=alert.pk).exists(),
            'MythologyAlert must persist even when bridge raises',
        )
