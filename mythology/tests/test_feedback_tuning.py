"""
Mythology feedback-tuning + bulk-review tests — Session 1095 Tier 1.
=====================================================================

Tests the human-review → pattern-quality loop that closes the Mythology
Lab activation plan's first tier.

Run:
    python manage.py test mythology.tests.test_feedback_tuning -v2
"""
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient

from mythology.feedback_tuning import (
    AUTO_DISABLE_FP_THRESHOLD,
    MIN_REVIEWS_FOR_DISABLE,
    bulk_review_by_pattern,
    tune_patterns_from_review,
)
from mythology.models import FlaggedHallucination, MythPattern

User = get_user_model()


def _make_pattern(pattern_type: str, severity: float = 0.5) -> MythPattern:
    pattern, _ = MythPattern.objects.update_or_create(
        pattern_type=pattern_type,
        defaults={
            'description': f'Test pattern for {pattern_type}',
            'severity_weight': severity,
            'is_active': True,
            'frequency_count': 0,
            'times_prevented': 0,
            'prevention_success_rate': 0.0,
        },
    )
    return pattern


def _make_flag(patterns_detected: list[str], priority: str = 'medium') -> FlaggedHallucination:
    return FlaggedHallucination.objects.create(
        flagged_content='some test content',
        flagged_type='auto_detected',
        priority=priority,
        verification_status='pending',
        patterns_detected=patterns_detected,
    )


class TunePatternsFromReviewTests(TransactionTestCase):

    def setUp(self):
        MythPattern.objects.all().delete()
        FlaggedHallucination.objects.all().delete()
        self.user = User.objects.create_user(
            username='tuner_test', password='x'
        )

    # ── Correct-catch path ─────────────────────────────────────────────

    def test_correct_catch_increments_times_prevented(self):
        p = _make_pattern('dangerous_myth', severity=0.5)
        f = _make_flag(['dangerous_myth'])
        result = tune_patterns_from_review(f, review_action='remove')
        p.refresh_from_db()
        self.assertEqual(p.times_prevented, 1)
        self.assertEqual(result['action_class'], 'correct_catch')
        self.assertEqual(result['patterns_updated'], 1)

    def test_correct_catch_nudges_severity_upward(self):
        p = _make_pattern('dangerous_myth', severity=0.5)
        f = _make_flag(['dangerous_myth'])
        tune_patterns_from_review(f, 'verified_hallucination')
        p.refresh_from_db()
        self.assertGreater(p.severity_weight, 0.5)

    def test_severity_capped_at_1(self):
        p = _make_pattern('dangerous_myth', severity=0.98)
        f = _make_flag(['dangerous_myth'])
        tune_patterns_from_review(f, 'remove')
        p.refresh_from_db()
        self.assertLessEqual(p.severity_weight, 1.0)

    # ── False-positive path ─────────────────────────────────────────────

    def test_false_positive_nudges_severity_down(self):
        p = _make_pattern('dangerous_myth', severity=0.5)
        f = _make_flag(['dangerous_myth'])
        tune_patterns_from_review(f, 'flag_false_positive')
        p.refresh_from_db()
        self.assertLess(p.severity_weight, 0.5)

    def test_false_positive_does_not_auto_disable_with_small_sample(self):
        """Auto-disable requires at least MIN_REVIEWS_FOR_DISABLE reviews."""
        p = _make_pattern('dangerous_myth', severity=0.5)
        # Only 3 false positives — below threshold of 25
        for _ in range(3):
            f = _make_flag(['dangerous_myth'])
            tune_patterns_from_review(f, 'flag_false_positive')
        p.refresh_from_db()
        self.assertTrue(p.is_active)

    def test_extreme_fp_rate_auto_disables_pattern(self):
        """Past MIN_REVIEWS_FOR_DISABLE with FP ratio >= threshold → disabled."""
        p = _make_pattern('dangerous_myth', severity=0.5)
        # 30 false positives, 2 correct catches → FP ratio 93.75%, above 80%
        for _ in range(30):
            f = _make_flag(['dangerous_myth'])
            tune_patterns_from_review(f, 'flag_false_positive')
        for _ in range(2):
            f = _make_flag(['dangerous_myth'])
            tune_patterns_from_review(f, 'remove')
        p.refresh_from_db()
        self.assertFalse(p.is_active)
        tuning = (p.prevention_strategies or {}).get('tuning', {})
        self.assertIsNotNone(tuning.get('auto_disabled_at'))
        self.assertIn('auto_disable_reason', tuning)

    def test_balanced_reviews_keep_pattern_active(self):
        """50/50 fp/correct is NOT enough to auto-disable.

        Must interleave reviews so FP ratio never exceeds the 80%
        threshold while crossing MIN_REVIEWS_FOR_DISABLE. Doing all
        FPs first would hit 100% FP ratio at review 25 and trip
        auto-disable before any correct catches arrive.
        """
        p = _make_pattern('dangerous_myth', severity=0.5)
        for _ in range(20):
            # Alternate correct and FP — always 50/50, never crosses threshold
            f = _make_flag(['dangerous_myth'])
            tune_patterns_from_review(f, 'remove')
            f = _make_flag(['dangerous_myth'])
            tune_patterns_from_review(f, 'flag_false_positive')
        p.refresh_from_db()
        self.assertTrue(p.is_active)

    def test_prevention_success_rate_updated(self):
        p = _make_pattern('dangerous_myth')
        # 3 correct + 1 FP = 75% success rate
        for _ in range(3):
            f = _make_flag(['dangerous_myth'])
            tune_patterns_from_review(f, 'remove')
        f = _make_flag(['dangerous_myth'])
        tune_patterns_from_review(f, 'flag_false_positive')
        p.refresh_from_db()
        self.assertEqual(p.prevention_success_rate, 0.75)

    # ── Edge cases ──────────────────────────────────────────────────────

    def test_unknown_action_is_noop(self):
        p = _make_pattern('dangerous_myth', severity=0.5)
        f = _make_flag(['dangerous_myth'])
        result = tune_patterns_from_review(f, 'some_unknown_action')
        p.refresh_from_db()
        self.assertEqual(p.times_prevented, 0)
        self.assertEqual(p.severity_weight, 0.5)
        self.assertEqual(result['action_class'], 'unknown')
        self.assertEqual(result['patterns_updated'], 0)

    def test_no_patterns_detected_noop(self):
        f = _make_flag([])
        result = tune_patterns_from_review(f, 'remove')
        self.assertEqual(result['patterns_updated'], 0)

    def test_unknown_pattern_type_auto_creates_row(self):
        """Session 1095 audit: flags can reference pattern types that don't
        yet have a MythPattern DB row (two validator systems produce
        non-overlapping type sets). The tuner auto-creates on first
        review so the loop closes for both systems, rather than silently
        skipping.
        """
        f = _make_flag(['dangerous_myth'])  # Not in DB initially
        self.assertFalse(MythPattern.objects.filter(pattern_type='dangerous_myth').exists())

        result = tune_patterns_from_review(f, 'remove')
        self.assertEqual(result['patterns_updated'], 1)
        self.assertEqual(result['action_class'], 'correct_catch')

        # Pattern now exists with review applied
        p = MythPattern.objects.get(pattern_type='dangerous_myth')
        self.assertEqual(p.times_prevented, 1)
        self.assertGreater(p.severity_weight, 0.3)  # Nudged up from neutral default

    def test_multiple_patterns_all_updated(self):
        p1 = _make_pattern('dangerous_myth')
        p2 = _make_pattern('time_myth')
        f = _make_flag(['dangerous_myth', 'time_myth'])
        result = tune_patterns_from_review(f, 'remove')
        self.assertEqual(result['patterns_updated'], 2)
        p1.refresh_from_db()
        p2.refresh_from_db()
        self.assertEqual(p1.times_prevented, 1)
        self.assertEqual(p2.times_prevented, 1)


class BulkReviewTests(TransactionTestCase):
    """Bulk-review endpoint + helper — unblocks the FP backlog."""

    def setUp(self):
        MythPattern.objects.all().delete()
        FlaggedHallucination.objects.all().delete()
        self.user = User.objects.create_user(username='bulk_test', password='x')

    def test_bulk_marks_all_matching_pattern(self):
        _make_pattern('dangerous_myth')
        for _ in range(5):
            _make_flag(['dangerous_myth'])
        # Flag with a different pattern — should NOT be affected
        _make_flag(['time_myth'])

        result = bulk_review_by_pattern(
            pattern_type='dangerous_myth',
            review_action='flag_false_positive',
            reviewer=self.user,
        )
        self.assertEqual(result['reviewed_count'], 5)
        self.assertEqual(result['new_status'], 'false_positive')

        # Unrelated flag still pending
        unrelated = FlaggedHallucination.objects.filter(
            patterns_detected__contains=['time_myth']
        )
        self.assertEqual(unrelated.count(), 1)
        self.assertEqual(unrelated.first().verification_status, 'pending')

    def test_bulk_tunes_pattern_only_once_per_batch(self):
        """Bulk reviewing 100 FPs shouldn't nudge severity 100 times."""
        p = _make_pattern('dangerous_myth', severity=0.5)
        for _ in range(100):
            _make_flag(['dangerous_myth'])
        bulk_review_by_pattern(
            pattern_type='dangerous_myth',
            review_action='flag_false_positive',
            reviewer=self.user,
        )
        p.refresh_from_db()
        # Severity nudged ONCE — clamped to MIN_SEVERITY_WEIGHT at worst
        # but should equal roughly initial - SEVERITY_NUDGE_FALSE_POSITIVE
        self.assertGreater(p.severity_weight, 0.1)
        self.assertLess(p.severity_weight, 0.5)
        # Pattern NOT auto-disabled even though 100 FPs (because we only
        # recorded ONE review)
        self.assertTrue(p.is_active)

    def test_bulk_with_priority_filter(self):
        _make_pattern('dangerous_myth')
        for _ in range(3):
            _make_flag(['dangerous_myth'], priority='critical')
        for _ in range(2):
            _make_flag(['dangerous_myth'], priority='medium')

        result = bulk_review_by_pattern(
            pattern_type='dangerous_myth',
            review_action='flag_false_positive',
            reviewer=self.user,
            priority_filter='critical',
        )
        self.assertEqual(result['reviewed_count'], 3)
        # Medium-priority flags untouched
        medium_pending = FlaggedHallucination.objects.filter(
            priority='medium', verification_status='pending'
        ).count()
        self.assertEqual(medium_pending, 2)

    def test_bulk_skips_already_reviewed(self):
        """Bulk operates only on pending rows — already-reviewed stays."""
        _make_pattern('dangerous_myth')
        f_pending = _make_flag(['dangerous_myth'])
        f_done = _make_flag(['dangerous_myth'])
        f_done.verification_status = 'verified_safe'
        f_done.save(update_fields=['verification_status'])

        result = bulk_review_by_pattern(
            pattern_type='dangerous_myth',
            review_action='flag_false_positive',
            reviewer=self.user,
        )
        self.assertEqual(result['reviewed_count'], 1)
        f_done.refresh_from_db()
        self.assertEqual(f_done.verification_status, 'verified_safe')


class BulkReviewEndpointTests(TransactionTestCase):
    """End-to-end: authenticate + POST to the endpoint."""

    def setUp(self):
        MythPattern.objects.all().delete()
        FlaggedHallucination.objects.all().delete()
        self.user = User.objects.create_user(username='endpoint_test', password='x', is_staff=True)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_post_bulk_review_returns_count(self):
        _make_pattern('dangerous_myth')
        for _ in range(4):
            _make_flag(['dangerous_myth'])
        resp = self.client.post(
            reverse('mythology:bulk_review'),
            data={
                'pattern_type': 'dangerous_myth',
                'action': 'flag_false_positive',
                'notes': 'Regex too broad — research content',
            },
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body['success'])
        self.assertEqual(body['reviewed_count'], 4)
        self.assertIn('pattern_tuning', body)

    def test_post_missing_fields_returns_400(self):
        resp = self.client.post(
            reverse('mythology:bulk_review'),
            data={'action': 'flag_false_positive'},  # missing pattern_type
            format='json',
        )
        self.assertEqual(resp.status_code, 400)

    def test_post_invalid_action_returns_400(self):
        resp = self.client.post(
            reverse('mythology:bulk_review'),
            data={
                'pattern_type': 'dangerous_myth',
                'action': 'not_a_real_action',
            },
            format='json',
        )
        self.assertEqual(resp.status_code, 400)

    def test_post_unauthenticated_returns_401_or_403(self):
        self.client.force_authenticate(user=None)
        resp = self.client.post(
            reverse('mythology:bulk_review'),
            data={'pattern_type': 'x', 'action': 'approve'},
            format='json',
        )
        self.assertIn(resp.status_code, (401, 403))
