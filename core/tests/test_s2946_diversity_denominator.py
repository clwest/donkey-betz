"""S2946 A6 — SignalCluster promotion diversity denominator (5 → 3).

Chris ratified Option 1 after Rigby AGREE. Change: line 855 of
`signal_aggregation_service.py`,
`diversity_factor = min(1.0, source_count / 5)` → `/ 3`.

Rationale (from A6 investigation):
- Pre-change: 838/870 (96%) of clusters decayed or archived; only 9 active
  (~1%). Root cause: no decayed cluster ever hit >=4 sources. Naturally-narrow
  signal types (skill_demand from job spiders) capped at ~3 sources, so
  diversity_factor stuck at 0.6 and strength never cleared the 0.5 bar.
- Post-change: 3 sources -> diversity_factor 1.0. 145 previously-decayed
  3-source clusters would now clear strength>=0.5. Confidence floor
  (requires 2+ sources) still blocks single-source noise.

These tests lock the new formula and the invariants that make it safe.
"""
from __future__ import annotations

from django.test import TestCase

from core.services.signal_aggregation_service import SignalAggregationService


class DiversityDenominatorTests(TestCase):
    """Lock the /3 denominator and the strength weights."""

    def setUp(self):
        self.svc = SignalAggregationService()

    def _signals(self, source_counts: dict[str, int], relevance: float = 50.0):
        """Build the signals list shape `_calculate_strength` expects."""
        out = []
        for source, n in source_counts.items():
            for _ in range(n):
                out.append({
                    'spider_name': source,
                    'relevance_score': relevance,
                })
        return out

    def test_three_sources_hits_full_diversity_factor(self):
        """S2946 core: 3 sources -> diversity_factor 1.0 (was 0.6)."""
        breakdown = {'a': 2, 'b': 2, 'c': 2}
        signals = self._signals(breakdown)
        strength = self.svc._calculate_strength(signals, breakdown)
        # signal_factor = 6/20 = 0.30; diversity = 3/3 = 1.0; relevance = 0.50
        # = 0.30*0.4 + 1.0*0.4 + 0.50*0.2 = 0.12 + 0.40 + 0.10 = 0.62
        self.assertGreaterEqual(strength, 0.5,
            "3-source cluster must clear the 0.5 promotion bar post-S2946")
        self.assertAlmostEqual(strength, 0.62, places=2)

    def test_two_sources_still_below_bar_at_low_signal_count(self):
        """Precision guardrail: 2 sources with few signals stays sub-threshold."""
        breakdown = {'a': 2, 'b': 2}
        signals = self._signals(breakdown, relevance=30.0)
        strength = self.svc._calculate_strength(signals, breakdown)
        # signal_factor = 4/20 = 0.20; diversity = 2/3 = 0.67; relevance = 0.30
        # = 0.20*0.4 + 0.67*0.4 + 0.30*0.2 = 0.08 + 0.267 + 0.06 = 0.407
        self.assertLess(strength, 0.5,
            "2-source thin clusters must remain unpromoted")

    def test_single_source_diversity_factor_matches_third(self):
        """1 source -> diversity_factor 0.33 (was 0.20)."""
        breakdown = {'a': 5}
        signals = self._signals(breakdown)
        strength = self.svc._calculate_strength(signals, breakdown)
        # signal_factor = 5/20 = 0.25; diversity = 1/3 = 0.333; relevance = 0.50
        # = 0.25*0.4 + 0.333*0.4 + 0.50*0.2 = 0.10 + 0.133 + 0.10 = 0.333
        # NOTE: single-source still blocked by confidence floor (0.3),
        # so strength lift here doesn't translate into false promotion.
        self.assertLess(strength, 0.5,
            "1-source clusters still below strength bar; confidence blocks anyway")

    def test_diversity_factor_caps_at_1(self):
        """4+ sources doesn't exceed 1.0 diversity (min-clamp preserved)."""
        breakdown = {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1}
        signals = self._signals(breakdown)
        strength = self.svc._calculate_strength(signals, breakdown)
        # signal_factor = 5/20 = 0.25; diversity = min(1, 5/3) = 1.0
        # = 0.25*0.4 + 1.0*0.4 + 0.50*0.2 = 0.10 + 0.40 + 0.10 = 0.60
        self.assertAlmostEqual(strength, 0.60, places=2)

    def test_confidence_floor_still_blocks_single_source(self):
        """Confidence formula unchanged — precision guardrail intact."""
        breakdown = {'only_source': 10}
        conf = self.svc._calculate_confidence(breakdown)
        # source_count < MIN_SOURCES_FOR_CONFIDENCE (2) -> 0.3 hard floor
        self.assertLess(conf, 0.5,
            "Single-source clusters must not clear confidence bar")

    def test_promotion_gate_requires_both_strength_and_confidence(self):
        """End-to-end: strength lift alone doesn't promote 1-source clusters."""
        breakdown = {'lone_spider': 15}
        signals = self._signals(breakdown, relevance=80.0)
        strength = self.svc._calculate_strength(signals, breakdown)
        confidence = self.svc._calculate_confidence(breakdown)
        # Even with post-S2946 formula, single-source stays unpromoted
        # because confidence gate is independent.
        promotes = strength >= 0.5 and confidence >= 0.5
        self.assertFalse(promotes,
            "Single-source noise stays unpromoted post-S2946")

    def test_three_source_low_relevance_still_promotes(self):
        """The target cohort: 3-source clusters with mediocre relevance."""
        # This is the shape of the 145 clusters that used to decay.
        breakdown = {'a': 3, 'b': 3, 'c': 4}  # 10 signals, 3 sources
        signals = self._signals(breakdown, relevance=30.0)
        strength = self.svc._calculate_strength(signals, breakdown)
        confidence = self.svc._calculate_confidence(breakdown)
        # signal_factor = 10/20 = 0.5; diversity = 3/3 = 1.0; relevance = 0.30
        # = 0.5*0.4 + 1.0*0.4 + 0.30*0.2 = 0.20 + 0.40 + 0.06 = 0.66
        # confidence: source_count=3 -> min(1, 3/4) = 0.75
        self.assertGreaterEqual(strength, 0.5)
        self.assertGreaterEqual(confidence, 0.5)
        self.assertTrue(strength >= 0.5 and confidence >= 0.5,
            "3-source mediocre-relevance clusters MUST promote (the S2946 target cohort)")
