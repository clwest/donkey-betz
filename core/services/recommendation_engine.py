"""
Recommendation Engine
=====================

Session 210: Personalized style and content recommendations.
Session 211: A/B Testing Integration - Experimental recommendation strategies.

This engine uses implicit learning signals to recommend:
- Styles that match user preferences
- Time-based suggestions (what works at different times)
- Trending styles across the platform
- Complementary styles based on usage patterns

Architecture:
- ImplicitLearningService provides user preference data
- StyleEvolution provides temporal patterns
- StyleTrend provides platform-wide popularity
- ABTestingService allows experimental recommendation strategies
- This engine combines all signals into actionable recommendations
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class StyleRecommendation:
    """A style recommendation with context."""
    style: str
    score: float  # 0-1 relevance score
    reason: str   # Why we're recommending this
    source: str   # 'personal', 'trending', 'collaborative', 'temporal'
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'style': self.style,
            'score': round(self.score, 3),
            'reason': self.reason,
            'source': self.source,
            'metadata': self.metadata or {}
        }


class RecommendationEngine:
    """
    Generate personalized recommendations based on implicit learning.

    Combines multiple signals:
    1. Personal preferences (from ImplicitLearningService)
    2. Temporal patterns (what works at different times)
    3. Trending styles (platform-wide popularity)
    4. Collaborative filtering (users like you also liked...)
    5. Style complementarity (if you like X, you might like Y)

    Usage:
        engine = RecommendationEngine()

        # Get style recommendations
        recs = engine.get_style_recommendations(user_id=1, limit=5)

        # Get "because you liked X" recommendations
        similar = engine.get_similar_style_recommendations(user_id=1, style='cyberpunk')
    """

    # Style relationships for complementarity recommendations
    STYLE_FAMILIES = {
        'animation': ['pixar', 'disney', 'dreamworks', 'ghibli', 'anime', 'manga', 'cartoon', 'chibi'],
        'tv_animation': ['south_park', 'simpsons', 'family_guy', 'rick_and_morty', 'archer',
                        'adventure_time', 'gravity_falls', 'bojack', 'looney_tunes'],
        'traditional_art': ['watercolor', 'oil_painting', 'pencil', 'charcoal', 'pastel', 'sketch'],
        'fine_art': ['impressionist', 'surreal', 'cubist', 'pop_art', 'art_deco', 'baroque', 'renaissance'],
        'genre': ['cyberpunk', 'steampunk', 'fantasy', 'scifi', 'gothic', 'horror', 'noir'],
        'photographic': ['cinematic', 'portrait', 'landscape', 'macro', 'street', 'documentary'],
        'modern_digital': ['minimalist', 'geometric', 'abstract', 'gradient', 'neon', 'vaporwave'],
    }

    # Time-based style suggestions (styles that work well at certain times)
    TIME_STYLE_AFFINITY = {
        'morning': ['watercolor', 'pastel', 'impressionist', 'landscape', 'minimalist'],
        'afternoon': ['pixar', 'disney', 'cartoon', 'pop_art', 'vibrant'],
        'evening': ['cyberpunk', 'neon', 'noir', 'cinematic', 'dramatic'],
        'night': ['gothic', 'horror', 'dark', 'mystery', 'ethereal'],
    }

    def __init__(self):
        """Initialize the recommendation engine."""
        self._learning_service = None
        self._style_evolution_model = None
        self._style_trend_model = None
        self._behavior_signal_model = None
        self._ab_testing_service = None

    @property
    def learning_service(self):
        """Lazy load the implicit learning service."""
        if self._learning_service is None:
            from core.services.implicit_learning import get_learning_service
            self._learning_service = get_learning_service()
        return self._learning_service

    @property
    def StyleEvolutionModel(self):
        """Lazy load StyleEvolution model."""
        if self._style_evolution_model is None:
            from core.models_unified_system import StyleEvolution
            self._style_evolution_model = StyleEvolution
        return self._style_evolution_model

    @property
    def StyleTrendModel(self):
        """Lazy load StyleTrend model."""
        if self._style_trend_model is None:
            from core.models_unified_system import StyleTrend
            self._style_trend_model = StyleTrend
        return self._style_trend_model

    @property
    def BehaviorSignalModel(self):
        """Lazy load BehaviorSignal model."""
        if self._behavior_signal_model is None:
            from core.models_unified_system import UserBehaviorSignal
            self._behavior_signal_model = UserBehaviorSignal
        return self._behavior_signal_model

    @property
    def ab_testing_service(self):
        """Lazy load A/B testing service."""
        if self._ab_testing_service is None:
            from core.services.ab_testing import get_ab_testing_service
            self._ab_testing_service = get_ab_testing_service()
        return self._ab_testing_service

    # ==================== A/B Testing Integration ====================

    def get_experiment_variant(
        self,
        user_id: int,
        session_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the user's variant assignment for any active recommendation experiments.

        Returns:
            Dict with experiment_id, variant_name, and variant_config if in experiment,
            None otherwise.
        """
        try:
            # Look for active recommendation experiments
            experiments = self.ab_testing_service.get_active_experiments(
                domain='style_recommendations'
            )

            if not experiments:
                return None

            # Get first active experiment (typically only one runs at a time)
            experiment = experiments[0]
            variant = self.ab_testing_service.get_variant_for_user(
                experiment_id=experiment['id'],
                user_id=user_id,
                session_id=session_id
            )

            if variant:
                return {
                    'experiment_id': str(experiment['id']),
                    'experiment_name': experiment['name'],
                    'variant_name': variant.name,
                    'variant_config': variant.config,
                    'is_control': variant.is_control
                }

            return None

        except Exception as e:
            logger.error(f"Error getting experiment variant: {e}")
            return None

    def _apply_experiment_weights(
        self,
        weights: Dict[str, float],
        variant_config: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Apply experimental weights from A/B test variant config.

        Args:
            weights: Default weights for recommendation sources
            variant_config: Configuration from the assigned variant

        Returns:
            Modified weights dictionary
        """
        modified_weights = weights.copy()

        # Allow variant to override weights
        if 'weights' in variant_config:
            for source, weight in variant_config['weights'].items():
                if source in modified_weights:
                    modified_weights[source] = weight

        return modified_weights

    def track_recommendation_click(
        self,
        user_id: int,
        style: str,
        recommendation_source: str,
        session_id: Optional[str] = None
    ) -> bool:
        """
        Track when a user clicks on a recommendation (for A/B testing).

        Args:
            user_id: User who clicked
            style: Style that was clicked
            recommendation_source: Source of recommendation (personal, trending, etc.)
            session_id: Session ID for anonymous tracking

        Returns:
            True if conversion was tracked, False otherwise
        """
        try:
            # Find active recommendation experiments
            experiments = self.ab_testing_service.get_active_experiments(
                domain='style_recommendations'
            )

            tracked = False
            for experiment in experiments:
                success = self.ab_testing_service.track_conversion(
                    experiment_id=experiment['id'],
                    conversion_type='click',
                    user_id=user_id,
                    session_id=session_id,
                    value=1.0,
                    metadata={
                        'style': style,
                        'recommendation_source': recommendation_source
                    }
                )
                if success:
                    tracked = True

            return tracked

        except Exception as e:
            logger.error(f"Error tracking recommendation click: {e}")
            return False

    def track_recommendation_apply(
        self,
        user_id: int,
        style: str,
        recommendation_source: str,
        session_id: Optional[str] = None
    ) -> bool:
        """
        Track when a user applies a recommended style (higher value conversion).

        Args:
            user_id: User who applied
            style: Style that was applied
            recommendation_source: Source of recommendation
            session_id: Session ID for anonymous tracking

        Returns:
            True if conversion was tracked, False otherwise
        """
        try:
            experiments = self.ab_testing_service.get_active_experiments(
                domain='style_recommendations'
            )

            tracked = False
            for experiment in experiments:
                success = self.ab_testing_service.track_conversion(
                    experiment_id=experiment['id'],
                    conversion_type='apply',
                    user_id=user_id,
                    session_id=session_id,
                    value=5.0,  # Higher value for applying vs clicking
                    metadata={
                        'style': style,
                        'recommendation_source': recommendation_source
                    }
                )
                if success:
                    tracked = True

            return tracked

        except Exception as e:
            logger.error(f"Error tracking recommendation apply: {e}")
            return False

    # ==================== Main Recommendation Methods ====================

    def get_style_recommendations(
        self,
        user_id: int,
        limit: int = 10,
        exclude_recent: bool = True,
        include_trending: bool = True,
        include_temporal: bool = True,
        session_id: Optional[str] = None
    ) -> List[StyleRecommendation]:
        """
        Get personalized style recommendations for a user.

        Args:
            user_id: User to get recommendations for
            limit: Maximum number of recommendations
            exclude_recent: Don't recommend recently used styles
            include_trending: Include trending styles
            include_temporal: Include time-of-day appropriate styles
            session_id: Session ID for A/B testing (anonymous users)

        Returns:
            List of StyleRecommendation objects sorted by relevance
        """
        try:
            recommendations: List[StyleRecommendation] = []

            # Check for A/B experiment variant
            experiment_variant = self.get_experiment_variant(user_id, session_id)

            # Default weights for each recommendation source
            source_weights = {
                'personal': 1.0,
                'collaborative': 0.9,
                'complementary': 0.8,
                'trending': 0.6,
                'temporal': 0.5
            }

            # Apply experimental weights if in an experiment
            if experiment_variant and not experiment_variant['is_control']:
                source_weights = self._apply_experiment_weights(
                    source_weights,
                    experiment_variant['variant_config']
                )
                logger.info(f"User {user_id} in experiment: {experiment_variant['experiment_name']}, "
                          f"variant: {experiment_variant['variant_name']}")

            # 1. Personal preferences (highest weight)
            personal_recs = self._get_personal_recommendations(user_id)
            for rec in personal_recs:
                rec.score *= source_weights['personal']
            recommendations.extend(personal_recs)

            # 2. "Users like you" collaborative filtering
            collaborative_recs = self._get_collaborative_recommendations(user_id)
            for rec in collaborative_recs:
                rec.score *= source_weights['collaborative']
            recommendations.extend(collaborative_recs)

            # 3. Complementary styles ("because you like X")
            complementary_recs = self._get_complementary_recommendations(user_id)
            for rec in complementary_recs:
                rec.score *= source_weights['complementary']
            recommendations.extend(complementary_recs)

            # 4. Trending styles (if enabled)
            if include_trending:
                trending_recs = self._get_trending_recommendations()
                for rec in trending_recs:
                    rec.score *= source_weights['trending']
                recommendations.extend(trending_recs)

            # 5. Time-appropriate styles (if enabled)
            if include_temporal:
                temporal_recs = self._get_temporal_recommendations()
                for rec in temporal_recs:
                    rec.score *= source_weights['temporal']
                recommendations.extend(temporal_recs)

            # Deduplicate and merge scores
            merged = self._merge_recommendations(recommendations)

            # Exclude recently used if requested
            if exclude_recent:
                recent_styles = self._get_recent_styles(user_id, days=7)
                merged = [r for r in merged if r.style not in recent_styles]

            # Sort by score and limit
            merged.sort(key=lambda x: x.score, reverse=True)

            # Add experiment info to metadata if in experiment
            if experiment_variant:
                for rec in merged[:limit]:
                    if rec.metadata is None:
                        rec.metadata = {}
                    rec.metadata['experiment'] = {
                        'id': experiment_variant['experiment_id'],
                        'variant': experiment_variant['variant_name']
                    }

            return merged[:limit]

        except Exception as e:
            logger.error(f"Error generating recommendations for user {user_id}: {e}")
            return self._get_fallback_recommendations(limit)

    def get_similar_style_recommendations(
        self,
        user_id: int,
        base_style: str,
        limit: int = 5
    ) -> List[StyleRecommendation]:
        """
        Get styles similar to a given style.

        "Because you liked {base_style}, you might also like..."

        Args:
            user_id: User ID
            base_style: Style to find similar styles for
            limit: Maximum recommendations

        Returns:
            List of similar style recommendations
        """
        try:
            recommendations = []
            base_style_lower = base_style.lower()

            # Find which family this style belongs to
            style_family = None
            for family, styles in self.STYLE_FAMILIES.items():
                if base_style_lower in styles:
                    style_family = family
                    break

            if style_family:
                # Recommend other styles from the same family
                family_styles = self.STYLE_FAMILIES[style_family]
                for style in family_styles:
                    if style != base_style_lower:
                        recommendations.append(StyleRecommendation(
                            style=style,
                            score=0.7,
                            reason=f"Similar to {base_style} ({style_family} style)",
                            source='similar',
                            metadata={'base_style': base_style, 'family': style_family}
                        ))

            # Also check what other users who liked base_style also liked
            similar_from_users = self._get_styles_users_also_liked(base_style_lower)
            for style, count in similar_from_users[:5]:
                if style != base_style_lower:
                    recommendations.append(StyleRecommendation(
                        style=style,
                        score=min(0.9, 0.5 + (count * 0.1)),
                        reason=f"Users who liked {base_style} also liked this",
                        source='collaborative',
                        metadata={'base_style': base_style, 'user_count': count}
                    ))

            # Deduplicate and sort
            merged = self._merge_recommendations(recommendations)
            merged.sort(key=lambda x: x.score, reverse=True)
            return merged[:limit]

        except Exception as e:
            logger.error(f"Error getting similar styles for {base_style}: {e}")
            return []

    def get_discovery_recommendations(
        self,
        user_id: int,
        limit: int = 5
    ) -> List[StyleRecommendation]:
        """
        Get styles the user hasn't tried but might like.

        Focuses on exploration and discovery of new styles.

        Args:
            user_id: User ID
            limit: Maximum recommendations

        Returns:
            List of discovery recommendations
        """
        try:
            # Get user's known preferences
            prefs = self.learning_service.calculate_preference_scores(user_id)
            known_styles = set(prefs.get('styles', {}).keys())

            # Get user's top style families
            top_families = self._get_user_style_families(known_styles)

            recommendations = []

            # Recommend unexplored styles from preferred families
            for family in top_families[:3]:
                family_styles = self.STYLE_FAMILIES.get(family, [])
                for style in family_styles:
                    if style not in known_styles:
                        recommendations.append(StyleRecommendation(
                            style=style,
                            score=0.65,
                            reason=f"Explore more {family} styles",
                            source='discovery',
                            metadata={'family': family, 'reason': 'family_exploration'}
                        ))

            # Add some trending styles the user hasn't tried
            trending = self._get_trending_styles(days=7)
            for style, trend_score in trending[:10]:
                if style not in known_styles:
                    recommendations.append(StyleRecommendation(
                        style=style,
                        score=0.5 * trend_score,
                        reason="Trending style you haven't tried",
                        source='discovery',
                        metadata={'trend_score': trend_score, 'reason': 'trending_unexplored'}
                    ))

            # Deduplicate and sort
            merged = self._merge_recommendations(recommendations)
            merged.sort(key=lambda x: x.score, reverse=True)
            return merged[:limit]

        except Exception as e:
            logger.error(f"Error getting discovery recommendations: {e}")
            return []

    # ==================== Private Recommendation Methods ====================

    def _get_personal_recommendations(self, user_id: int) -> List[StyleRecommendation]:
        """Get recommendations based on user's personal preferences."""
        try:
            prefs = self.learning_service.calculate_preference_scores(user_id)
            style_scores = prefs.get('styles', {})
            confidence = prefs.get('confidence', 0)

            recommendations = []
            for style, score in style_scores.items():
                if score > 0.3:  # Only recommend styles with positive affinity
                    recommendations.append(StyleRecommendation(
                        style=style,
                        score=score * confidence,  # Weight by confidence
                        reason="Based on your preferences",
                        source='personal',
                        metadata={'raw_score': score, 'confidence': confidence}
                    ))

            return recommendations
        except Exception as e:
            logger.error(f"Error getting personal recommendations: {e}")
            return []

    def _get_collaborative_recommendations(self, user_id: int) -> List[StyleRecommendation]:
        """Get recommendations based on similar users' preferences."""
        try:
            # Find users with similar preferences
            similar_users = self._find_similar_users(user_id, limit=10)

            if not similar_users:
                return []

            # Aggregate their preferences
            style_votes = defaultdict(float)
            for similar_user_id, similarity in similar_users:
                prefs = self.learning_service.calculate_preference_scores(similar_user_id)
                for style, score in prefs.get('styles', {}).items():
                    if score > 0:
                        style_votes[style] += score * similarity

            # Get user's own styles to exclude
            user_prefs = self.learning_service.calculate_preference_scores(user_id)
            user_styles = set(user_prefs.get('styles', {}).keys())

            recommendations = []
            for style, vote_score in sorted(style_votes.items(), key=lambda x: -x[1])[:10]:
                if style not in user_styles:
                    recommendations.append(StyleRecommendation(
                        style=style,
                        score=min(0.8, vote_score / 10),  # Normalize
                        reason="Users with similar taste enjoyed this",
                        source='collaborative',
                        metadata={'vote_score': vote_score}
                    ))

            return recommendations
        except Exception as e:
            logger.error(f"Error getting collaborative recommendations: {e}")
            return []

    def _get_complementary_recommendations(self, user_id: int) -> List[StyleRecommendation]:
        """Get recommendations based on style complementarity."""
        try:
            prefs = self.learning_service.calculate_preference_scores(user_id)
            top_styles = prefs.get('top_styles', [])[:3]

            recommendations = []
            for liked_style in top_styles:
                # Find the family and recommend related styles
                for family, styles in self.STYLE_FAMILIES.items():
                    if liked_style in styles:
                        for related_style in styles[:5]:
                            if related_style != liked_style:
                                recommendations.append(StyleRecommendation(
                                    style=related_style,
                                    score=0.6,
                                    reason=f"Because you like {liked_style}",
                                    source='complementary',
                                    metadata={'based_on': liked_style, 'family': family}
                                ))
                        break

            return recommendations
        except Exception as e:
            logger.error(f"Error getting complementary recommendations: {e}")
            return []

    def _get_trending_recommendations(self) -> List[StyleRecommendation]:
        """Get currently trending styles."""
        try:
            trending = self._get_trending_styles(days=7)

            recommendations = []
            for style, trend_score in trending[:5]:
                recommendations.append(StyleRecommendation(
                    style=style,
                    score=0.4 * trend_score,  # Lower weight for trending
                    reason="Trending right now",
                    source='trending',
                    metadata={'trend_score': trend_score}
                ))

            return recommendations
        except Exception as e:
            logger.error(f"Error getting trending recommendations: {e}")
            return []

    def _get_temporal_recommendations(self) -> List[StyleRecommendation]:
        """Get time-of-day appropriate style recommendations."""
        try:
            # Use Django's timezone settings (configured for America/Denver = MST)
            from django.utils import timezone
            from django.conf import settings
            import pytz

            # Get local time in configured timezone
            try:
                local_tz = pytz.timezone(settings.TIME_ZONE)
                local_time = timezone.now().astimezone(local_tz)
                hour = local_time.hour
            except Exception:
                # Fallback to UTC
                hour = datetime.now().hour

            # Determine time period
            if 5 <= hour < 12:
                period = 'morning'
            elif 12 <= hour < 17:
                period = 'afternoon'
            elif 17 <= hour < 21:
                period = 'evening'
            else:
                period = 'night'

            styles = self.TIME_STYLE_AFFINITY.get(period, [])

            recommendations = []
            for style in styles[:3]:
                recommendations.append(StyleRecommendation(
                    style=style,
                    score=0.3,  # Lower weight for temporal
                    reason=f"Great for {period} creativity",
                    source='temporal',
                    metadata={'time_period': period, 'hour': hour}
                ))

            return recommendations
        except Exception as e:
            logger.error(f"Error getting temporal recommendations: {e}")
            return []

    def _get_fallback_recommendations(self, limit: int) -> List[StyleRecommendation]:
        """Get fallback recommendations when no data is available."""
        fallback_styles = ['cyberpunk', 'pixar', 'watercolor', 'anime', 'cinematic']
        return [
            StyleRecommendation(
                style=style,
                score=0.5,
                reason="Popular style",
                source='fallback',
                metadata={}
            )
            for style in fallback_styles[:limit]
        ]

    # ==================== Helper Methods ====================

    def _merge_recommendations(
        self,
        recommendations: List[StyleRecommendation]
    ) -> List[StyleRecommendation]:
        """Merge duplicate style recommendations, combining scores."""
        merged = {}

        for rec in recommendations:
            style = rec.style.lower()
            if style in merged:
                # Combine scores (weighted average, favor higher)
                existing = merged[style]
                combined_score = max(existing.score, rec.score) * 0.7 + \
                               min(existing.score, rec.score) * 0.3
                # Keep the higher-scored recommendation but update score
                if rec.score > existing.score:
                    rec.score = combined_score
                    merged[style] = rec
                else:
                    existing.score = combined_score
            else:
                merged[style] = rec

        return list(merged.values())

    def _get_recent_styles(self, user_id: int, days: int = 7) -> set:
        """Get styles the user has used recently."""
        try:
            from django.utils import timezone
            since = timezone.now() - timedelta(days=days)

            signals = self.BehaviorSignalModel.objects.filter(
                user_id=user_id,
                created_at__gte=since
            ).values_list('metadata', flat=True)

            recent_styles = set()
            for metadata in signals:
                if metadata and 'style' in metadata:
                    recent_styles.add(metadata['style'])

            return recent_styles
        except Exception as e:
            logger.error(f"Error getting recent styles: {e}")
            return set()

    def _get_trending_styles(self, days: int = 7) -> List[Tuple[str, float]]:
        """Get currently trending styles platform-wide."""
        try:
            from django.utils import timezone
            since = timezone.now() - timedelta(days=days)

            # Query behavior signals
            signals = self.BehaviorSignalModel.objects.filter(
                created_at__gte=since,
                signal_type__in=['download', 'share', 'favorite']
            )

            # Count positive signals per style
            style_counts = defaultdict(int)
            for signal in signals:
                metadata = signal.metadata or {}
                style = metadata.get('style')
                if style:
                    # Weight by signal strength
                    weight = abs(signal.weight)
                    style_counts[style] += weight

            # Normalize to 0-1
            max_count = max(style_counts.values()) if style_counts else 1
            normalized = [
                (style, count / max_count)
                for style, count in sorted(style_counts.items(), key=lambda x: -x[1])
            ]

            return normalized
        except Exception as e:
            logger.error(f"Error getting trending styles: {e}")
            return []

    def _find_similar_users(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[Tuple[int, float]]:
        """Find users with similar preferences (for collaborative filtering)."""
        try:
            from core.models_unified_system import UserPreferenceProfile

            # Get target user's preferences
            try:
                target_profile = UserPreferenceProfile.objects.get(user_id=user_id)
                target_styles = target_profile.style_scores or {}
            except UserPreferenceProfile.DoesNotExist:
                return []

            if not target_styles:
                return []

            # Find other users and calculate similarity
            other_profiles = UserPreferenceProfile.objects.exclude(user_id=user_id)

            similar_users = []
            for profile in other_profiles:
                other_styles = profile.style_scores or {}
                if other_styles:
                    similarity = self._calculate_style_similarity(target_styles, other_styles)
                    if similarity > 0.3:  # Only include reasonably similar users
                        similar_users.append((profile.user_id, similarity))

            # Sort by similarity
            similar_users.sort(key=lambda x: -x[1])
            return similar_users[:limit]

        except Exception as e:
            logger.error(f"Error finding similar users: {e}")
            return []

    def _calculate_style_similarity(
        self,
        styles_a: Dict[str, float],
        styles_b: Dict[str, float]
    ) -> float:
        """Calculate cosine similarity between two style preference dictionaries."""
        # Get common styles
        all_styles = set(styles_a.keys()) | set(styles_b.keys())

        if not all_styles:
            return 0.0

        # Calculate dot product and magnitudes
        dot_product = 0.0
        mag_a = 0.0
        mag_b = 0.0

        for style in all_styles:
            a = styles_a.get(style, 0.0)
            b = styles_b.get(style, 0.0)
            dot_product += a * b
            mag_a += a * a
            mag_b += b * b

        if mag_a == 0 or mag_b == 0:
            return 0.0

        return dot_product / (mag_a ** 0.5 * mag_b ** 0.5)

    def _get_styles_users_also_liked(
        self,
        base_style: str,
        limit: int = 10
    ) -> List[Tuple[str, int]]:
        """Get styles that users who liked base_style also liked."""
        try:
            # Find users who liked base_style
            users_who_liked = self.BehaviorSignalModel.objects.filter(
                signal_type__in=['download', 'share', 'favorite'],
                metadata__style=base_style
            ).values_list('user_id', flat=True).distinct()

            if not users_who_liked:
                return []

            # Find what else these users liked
            other_styles = self.BehaviorSignalModel.objects.filter(
                user_id__in=users_who_liked,
                signal_type__in=['download', 'share', 'favorite']
            ).exclude(
                metadata__style=base_style
            )

            # Count styles
            style_counts = defaultdict(int)
            for signal in other_styles:
                style = (signal.metadata or {}).get('style')
                if style:
                    style_counts[style] += 1

            # Sort by count
            sorted_styles = sorted(style_counts.items(), key=lambda x: -x[1])
            return sorted_styles[:limit]

        except Exception as e:
            logger.error(f"Error getting related styles: {e}")
            return []

    def _get_user_style_families(self, known_styles: set) -> List[str]:
        """Determine which style families the user prefers based on known styles."""
        family_counts = defaultdict(int)

        for family, styles in self.STYLE_FAMILIES.items():
            for style in styles:
                if style in known_styles:
                    family_counts[family] += 1

        # Sort by count
        sorted_families = sorted(family_counts.items(), key=lambda x: -x[1])
        return [family for family, count in sorted_families if count > 0]


# Convenience function
def get_recommendation_engine() -> RecommendationEngine:
    """Get a singleton instance of the recommendation engine."""
    return RecommendationEngine()
