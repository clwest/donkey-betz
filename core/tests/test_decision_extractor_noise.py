"""Session 1092: Tests for decision_extractor noise filter + pending quota.

Targets the gaps that produced the 296 product-type draft backlog:
truncated topics ("Discussion: competitor activity and"), thin topics
("Panel: AI"), and unbounded inbox accumulation.
"""

from django.test import TestCase

from core.services.decision_extractor import (
    PENDING_CAP_PER_TYPE,
    _pending_quota_exceeded,
    is_noise_topic,
)


class TestNoiseFilter(TestCase):
    """is_noise_topic() — Session 1092 strengthening."""

    def test_dangling_trailing_word_rejected(self):
        cases = [
            "Discussion: competitor activity and",
            "Panel: marketing strategy for",
            "[Synthesis] launch plan with",
            "Discussion: revenue and the",
            "Panel: feature analysis or",
        ]
        for topic in cases:
            with self.subTest(topic=topic):
                self.assertTrue(
                    is_noise_topic(topic),
                    f"Expected truncated topic to be filtered: '{topic}'",
                )

    def test_thin_topic_rejected(self):
        # "Panel: AI" → 1 substantive word, "Panel: AI work" → 2 words
        # Both should fail the >=3 substantive-word rule.
        cases = [
            "Discussion: ai work",
            "Panel: marketing demo",
            "Discussion: revenue",
        ]
        for topic in cases:
            with self.subTest(topic=topic):
                self.assertTrue(
                    is_noise_topic(topic),
                    f"Expected thin topic to be filtered: '{topic}'",
                )

    def test_substantive_topic_passes(self):
        cases = [
            "Discussion: AI agent collaboration patterns",
            "Panel: competitor coverage gap analysis",
            "[Synthesis] customer onboarding flow improvements",
            "Q4 monetization strategy review",
        ]
        for topic in cases:
            with self.subTest(topic=topic):
                self.assertFalse(
                    is_noise_topic(topic),
                    f"Expected substantive topic to pass: '{topic}'",
                )

    def test_existing_noise_words_still_blocked(self):
        # Regression: pre-Session-1092 checks must still fire.
        for topic in ('discussion', 'panel', 'ai', 'test', ''):
            with self.subTest(topic=topic):
                self.assertTrue(is_noise_topic(topic))


class TestPendingQuota(TestCase):
    """_pending_quota_exceeded() — Session 1092 inbox cap."""

    def _make_draft(self, decision_type='product'):
        from core.models_unified_system import AgentDecisionSummary

        return AgentDecisionSummary.objects.create(
            conversation=None,
            hive_session=None,
            topic=f'Test draft #{decision_type}',
            decision_type=decision_type,
            impact_area='agents',
            status='draft',
        )

    def test_quota_not_exceeded_under_cap(self):
        for _ in range(3):
            self._make_draft('product')
        self.assertFalse(_pending_quota_exceeded('product'))

    def test_quota_exceeded_at_cap(self):
        for _ in range(PENDING_CAP_PER_TYPE):
            self._make_draft('product')
        self.assertTrue(_pending_quota_exceeded('product'))

    def test_quota_isolated_per_type(self):
        # Filling 'product' should not block 'experiment' creation.
        for _ in range(PENDING_CAP_PER_TYPE):
            self._make_draft('product')
        self.assertTrue(_pending_quota_exceeded('product'))
        self.assertFalse(_pending_quota_exceeded('experiment'))

    def test_quota_ignores_promoted_decisions(self):
        from core.models_unified_system import AgentDecisionSummary

        for _ in range(PENDING_CAP_PER_TYPE + 5):
            self._make_draft('product')
        # Promote enough to drop pending below cap. Slice → ID list → bulk update,
        # since Django won't update a sliced queryset directly.
        ids_to_promote = list(
            AgentDecisionSummary.objects.filter(
                decision_type='product', status='draft'
            ).values_list('id', flat=True)[:PENDING_CAP_PER_TYPE]
        )
        AgentDecisionSummary.objects.filter(id__in=ids_to_promote).update(
            status='canonical'
        )

        self.assertFalse(
            _pending_quota_exceeded('product'),
            "Quota should only count draft-status rows",
        )

    def test_empty_decision_type_does_not_block(self):
        self.assertFalse(_pending_quota_exceeded(''))
        self.assertFalse(_pending_quota_exceeded(None))  # type: ignore[arg-type]
