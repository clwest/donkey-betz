"""
Content Scoring Service - Session 1025

Rule-based scoring engine for SignalClusters. Computes reach, intent,
replicability, source_confidence, and assigns a pipeline track
(attention vs intent) to each cluster.

No LLM calls -- pure keyword/heuristic scoring for speed and cost.
"""

import logging

logger = logging.getLogger(__name__)


class ContentScoringService:
    """Scores SignalClusters on reach, intent, replicability, and source confidence."""

    # Source tiers for confidence scoring
    SOURCE_TIERS = {
        'tier1': frozenset({
            'reuters', 'bbc', 'techcrunch', 'nature', 'arxiv', 'espn',
            'associated_press', 'bloomberg', 'wsj', 'nyt', 'guardian',
            'coindesk', 'cointelegraph',
        }),
        'tier2': frozenset({
            'hackernews', 'devto', 'reddit', 'venturebeat', 'medium',
            'producthunt', 'ycombinator', 'substack', 'bluesky',
            'mastodon', 'github_trending',
        }),
        'tier3': frozenset({
            'giphy', 'spotify', 'noaa_weather', 'unsplash',
            'random_user', 'cat_facts', 'dad_jokes',
        }),
    }

    TIER_WEIGHTS = {'tier1': 1.0, 'tier2': 0.6, 'tier3': 0.2}
    DEFAULT_TIER_WEIGHT = 0.3

    INTENT_KEYWORDS = frozenset({
        'how to', 'tutorial', 'course', 'guide', 'step by step',
        'pricing', 'cost', 'salary', 'earn', 'revenue', 'freelance',
        'job', 'hiring', 'remote work', 'opportunity', 'certification',
        'template', 'checklist', 'tool', 'software', 'platform',
    })

    REACH_KEYWORDS = frozenset({
        'trending', 'viral', 'breaking', 'controversy', 'debate',
        'million', 'billion', 'record', 'first ever', 'unprecedented',
        'surge', 'crash', 'scandal', 'launch', 'announce',
    })

    EVERGREEN_KEYWORDS = frozenset({
        'tutorial', 'guide', 'how to', 'step by step', 'course',
        'certification', 'reference', 'documentation', 'framework',
        'best practices', 'checklist', 'template',
    })

    # Pattern types that indicate commercial/actionable intent
    INTENT_PATTERN_TYPES = {'opportunity_window', 'skill_demand'}
    PARTIAL_INTENT_PATTERN_TYPES = {'demand_spike'}

    def score_cluster(self, cluster) -> dict:
        """
        Compute all 4 scores + track assignment for a SignalCluster.

        Returns dict of field names -> values ready for setattr/update.
        """
        keywords = cluster.keywords or []
        sources = cluster.source_breakdown or {}
        keyword_text = ' '.join(keywords).lower()

        reach = self._compute_reach(keyword_text, sources, cluster)
        intent = self._compute_intent(keyword_text, cluster)
        replicability = self._compute_replicability(keyword_text, sources)
        confidence = self._compute_source_confidence(sources)
        track = self._assign_track(reach, intent)

        return {
            'reach_score': round(reach, 3),
            'intent_score': round(intent, 3),
            'replicability_score': round(replicability, 3),
            'source_confidence': round(confidence, 3),
            'track': track,
        }

    # ------------------------------------------------------------------
    # Individual score computations
    # ------------------------------------------------------------------

    def _compute_reach(self, keyword_text: str, sources: dict, cluster) -> float:
        """0-1: viral/audience potential."""
        source_diversity = min(len(sources) / 5, 1.0)
        keyword_reach = self._keyword_hit_ratio(keyword_text, self.REACH_KEYWORDS)
        strength = getattr(cluster, 'strength', 0.0) or 0.0
        return min(1.0, 0.4 * source_diversity + 0.3 * keyword_reach + 0.3 * strength)

    def _compute_intent(self, keyword_text: str, cluster) -> float:
        """0-1: commercial/actionable potential."""
        keyword_intent = self._keyword_hit_ratio(keyword_text, self.INTENT_KEYWORDS)

        pattern_type = getattr(cluster, 'pattern_type', '') or ''
        if pattern_type in self.INTENT_PATTERN_TYPES:
            data_type_intent = 1.0
        elif pattern_type in self.PARTIAL_INTENT_PATTERN_TYPES:
            data_type_intent = 0.5
        else:
            data_type_intent = 0.0

        urgency = getattr(cluster, 'urgency', 0.0) or 0.0
        return min(1.0, 0.5 * keyword_intent + 0.3 * data_type_intent + 0.2 * urgency)

    def _compute_replicability(self, keyword_text: str, sources: dict) -> float:
        """0-1: can we act on this repeatedly."""
        is_evergreen = 1.0 if any(kw in keyword_text for kw in self.EVERGREEN_KEYWORDS) else 0.0
        has_multiple_sources = min(len(sources) / 3, 1.0)
        is_recurring = 0.5  # placeholder -- needs historical comparison
        return min(1.0, 0.5 * is_evergreen + 0.3 * has_multiple_sources + 0.2 * is_recurring)

    def _compute_source_confidence(self, sources: dict) -> float:
        """0-1: trustworthiness of contributing sources."""
        if not sources:
            return 0.0

        total_weight = 0.0
        total_count = 0
        for source_name, count in sources.items():
            tier_weight = self._get_tier_weight(source_name.lower())
            total_weight += tier_weight * count
            total_count += count

        if total_count == 0:
            return 0.0

        return min(1.0, total_weight / total_count)

    def _assign_track(self, reach: float, intent: float) -> str:
        """Assign pipeline track based on reach vs intent dominance."""
        if intent >= 0.6:
            return 'intent'
        if reach >= 0.6:
            return 'attention'
        if intent >= 0.4 and intent > reach:
            return 'intent'
        if reach >= 0.4 and reach > intent:
            return 'attention'
        return 'unclassified'

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _keyword_hit_ratio(self, text: str, keyword_set: frozenset) -> float:
        """Proportion of keywords from the set found in text (0-1)."""
        if not text:
            return 0.0
        hits = sum(1 for kw in keyword_set if kw in text)
        return min(1.0, hits / max(len(keyword_set), 1))

    def _get_tier_weight(self, source_name: str) -> float:
        """Look up tier weight for a source name (partial match)."""
        for tier, names in self.SOURCE_TIERS.items():
            for name in names:
                if name in source_name or source_name in name:
                    return self.TIER_WEIGHTS[tier]
        return self.DEFAULT_TIER_WEIGHT
