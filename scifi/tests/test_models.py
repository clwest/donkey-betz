# scifi/tests/test_models.py
"""
Tests for AgentMood model expiry logic and backfill management command.
"""

from datetime import timedelta

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from scifi.models import AgentMood


@override_settings(SCIFI_MOOD_TTL_DAYS=7)
class AgentMoodModelTests(TestCase):
    def test_creation_without_mood_expires_sets_expiry(self):
        """
        Creating an AgentMood without mood_expires_at should set it to
        created_at + TTL days.
        """
        before = timezone.now()
        mood = AgentMood.objects.create(mood="happy", mood_expires_at=None)
        after = timezone.now()

        # Reload from DB to ensure persisted values are read.
        mood = AgentMood.objects.get(pk=mood.pk)
        self.assertIsNotNone(mood.mood_expires_at)

        expected = mood.created_at + timedelta(days=settings.SCIFI_MOOD_TTL_DAYS)

        # Ensure created_at was set between before and after.
        self.assertGreaterEqual(mood.created_at, before - timedelta(seconds=1))
        self.assertLessEqual(mood.created_at, after + timedelta(seconds=1))

        # expiry should equal created_at + TTL (allow small drift)
        diff = abs((mood.mood_expires_at - expected).total_seconds())
        self.assertLess(diff, 1.0, f"Expiry differs by {diff} seconds")

    def test_creation_with_explicit_mood_expires_preserved(self):
        """
        If mood_expires_at is explicitly provided, it should be preserved.
        """
        explicit = timezone.now() + timedelta(days=2)
        mood = AgentMood.objects.create(mood="sad", mood_expires_at=explicit)
        mood = AgentMood.objects.get(pk=mood.pk)
        self.assertEqual(mood.mood_expires_at.replace(microsecond=0), explicit.replace(microsecond=0))


@override_settings(SCIFI_MOOD_TTL_DAYS=10)
class BackfillCommandTests(TestCase):
    def test_backfill_command_fills_null_expiries(self):
        """
        Rows with NULL mood_expires_at should be updated to created_at + TTL.
        """
        now = timezone.now()

        # Create rows: some with null expiry, some with explicit expiry.
        m1 = AgentMood.objects.create(mood="m1", created_at=now - timedelta(days=1), mood_expires_at=None)
        m2 = AgentMood.objects.create(mood="m2", created_at=now - timedelta(days=2), mood_expires_at=None)
        explicit = now + timedelta(days=5)
        m3 = AgentMood.objects.create(mood="m3", created_at=now - timedelta(days=3), mood_expires_at=explicit)

        # Ensure initial DB state has two nulls.
        null_count_before = AgentMood.objects.filter(mood_expires_at__isnull=True).count()
        self.assertEqual(null_count_before, 2)

        # Run command (default batch size is fine)
        call_command("backfill_mood_expiry")

        # After backfill: no rows should have null expiry
        null_count_after = AgentMood.objects.filter(mood_expires_at__isnull=True).count()
        self.assertEqual(null_count_after, 0)

        # Verify explicit was preserved
        m3.refresh_from_db()
        self.assertEqual(m3.mood_expires_at.replace(microsecond=0), explicit.replace(microsecond=0))

        # Verify computed expiries equal created_at + TTL
        ttl = settings.SCIFI_MOOD_TTL_DAYS
        m1.refresh_from_db()
        m2.refresh_from_db()
        expected_m1 = m1.created_at + timedelta(days=ttl)
        expected_m2 = m2.created_at + timedelta(days=ttl)
        self.assertAlmostEqual(m1.mood_expires_at.timestamp(), expected_m1.timestamp(), delta=1.0)
        self.assertAlmostEqual(m2.mood_expires_at.timestamp(), expected_m2.timestamp(), delta=1.0)