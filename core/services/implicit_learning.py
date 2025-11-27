"""
Implicit Learning Service
=========================

Session 210: Learn from user behavior without explicit feedback.

This service tracks various user signals to understand preferences:
- Downloads = user liked the content
- Shares = user really liked it
- Deletes = user didn't like it
- Time spent viewing = interest level
- Regenerations = not satisfied, trying again
- Style choices = explicit preference signal

These signals are aggregated to build a comprehensive user preference profile
that improves recommendations over time.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BehaviorSignal:
    """A single user behavior signal."""
    signal_type: str  # 'download', 'share', 'delete', 'view', 'regenerate', 'style_use'
    content_id: str
    user_id: int
    timestamp: datetime
    metadata: Dict[str, Any]  # style, model, prompt keywords, etc.
    weight: float  # Signal strength (share=1.0, download=0.7, view=0.3, delete=-0.5)


class ImplicitLearningService:
    """
    Learn from user behavior implicitly to improve recommendations.

    Tracks multiple behavioral signals:
    - Downloads: User saved the content (positive signal)
    - Shares: User shared publicly (strong positive signal)
    - Deletes: User removed content (negative signal)
    - View time: Longer viewing = more interest
    - Regenerations: User tried again (mild negative for original)
    - Style usage: Explicit choice of style

    Usage:
        service = ImplicitLearningService()

        # Track a download
        service.track_download(user_id=1, content_id='abc123',
                               style='cyberpunk', model='stable-diffusion')

        # Get user preferences
        prefs = service.calculate_preference_scores(user_id=1)
        # Returns: {'styles': {'cyberpunk': 0.8, 'anime': 0.6}, 'models': {...}}
    """

    # Signal weights (how much each action contributes to preference)
    SIGNAL_WEIGHTS = {
        'share': 1.0,        # Strongest positive signal
        'download': 0.7,     # Strong positive
        'favorite': 0.8,     # Strong positive
        'view_long': 0.4,    # Mild positive (viewed > 10 seconds)
        'view_short': 0.1,   # Weak positive (viewed < 10 seconds)
        'style_use': 0.5,    # Direct style choice
        'regenerate': -0.2,  # Mild negative (wasn't satisfied)
        'delete': -0.5,      # Negative signal
    }

    # Time decay factor (older signals count less)
    DECAY_HALF_LIFE_DAYS = 30  # Signal loses half its weight after 30 days

    def __init__(self):
        """Initialize the implicit learning service."""
        self._behavior_signal_model = None
        self._user_preference_model = None

    @property
    def BehaviorSignalModel(self):
        """Lazy load BehaviorSignal model."""
        if self._behavior_signal_model is None:
            from core.models_unified_system import UserBehaviorSignal
            self._behavior_signal_model = UserBehaviorSignal
        return self._behavior_signal_model

    @property
    def UserPreferenceModel(self):
        """Lazy load UserPreference model."""
        if self._user_preference_model is None:
            from core.models_unified_system import UserPreferenceProfile
            self._user_preference_model = UserPreferenceProfile
        return self._user_preference_model

    # ==================== Tracking Methods ====================

    def track_generation(
        self,
        user_id: int,
        content_id: str,
        prompt: str,
        style: str = None,
        model: str = None,
        metadata: Dict = None
    ) -> None:
        """
        Track a content generation event.

        This is the baseline - just records that generation happened.
        Actual preference signal comes from subsequent actions (download, share, etc.)
        """
        try:
            signal = self.BehaviorSignalModel.objects.create(
                user_id=user_id,
                signal_type='generation',
                content_id=content_id,
                weight=0.0,  # Neutral - just recording
                metadata={
                    'prompt': prompt[:500] if prompt else '',
                    'style': style,
                    'model': model,
                    **(metadata or {})
                }
            )
            logger.debug(f"Tracked generation for user {user_id}: {content_id}")
            return signal
        except Exception as e:
            logger.error(f"Error tracking generation: {e}")

    def track_download(
        self,
        user_id: int,
        content_id: str,
        style: str = None,
        model: str = None
    ) -> None:
        """
        Track when user downloads/saves content.

        Download = user liked it enough to keep it.
        Strong positive signal for the style/model used.
        """
        try:
            signal = self.BehaviorSignalModel.objects.create(
                user_id=user_id,
                signal_type='download',
                content_id=content_id,
                weight=self.SIGNAL_WEIGHTS['download'],
                metadata={'style': style, 'model': model}
            )

            # Update user preference profile
            self._update_preference_score(user_id, style, model, self.SIGNAL_WEIGHTS['download'])

            logger.info(f"Tracked download for user {user_id}: {content_id} (style={style})")
            return signal
        except Exception as e:
            logger.error(f"Error tracking download: {e}")

    def track_share(
        self,
        user_id: int,
        content_id: str,
        style: str = None,
        model: str = None,
        platform: str = None
    ) -> None:
        """
        Track when user shares content publicly.

        Share = user really liked it, willing to show others.
        Strongest positive signal.
        """
        try:
            signal = self.BehaviorSignalModel.objects.create(
                user_id=user_id,
                signal_type='share',
                content_id=content_id,
                weight=self.SIGNAL_WEIGHTS['share'],
                metadata={'style': style, 'model': model, 'platform': platform}
            )

            # Strong preference update
            self._update_preference_score(user_id, style, model, self.SIGNAL_WEIGHTS['share'])

            logger.info(f"Tracked share for user {user_id}: {content_id} (style={style})")
            return signal
        except Exception as e:
            logger.error(f"Error tracking share: {e}")

    def track_delete(
        self,
        user_id: int,
        content_id: str,
        style: str = None,
        model: str = None
    ) -> None:
        """
        Track when user deletes content.

        Delete = user didn't like it.
        Negative signal for the style/model used.
        """
        try:
            signal = self.BehaviorSignalModel.objects.create(
                user_id=user_id,
                signal_type='delete',
                content_id=content_id,
                weight=self.SIGNAL_WEIGHTS['delete'],
                metadata={'style': style, 'model': model}
            )

            # Negative preference update
            self._update_preference_score(user_id, style, model, self.SIGNAL_WEIGHTS['delete'])

            logger.info(f"Tracked delete for user {user_id}: {content_id} (style={style})")
            return signal
        except Exception as e:
            logger.error(f"Error tracking delete: {e}")

    def track_view_time(
        self,
        user_id: int,
        content_id: str,
        seconds: int,
        style: str = None,
        model: str = None
    ) -> None:
        """
        Track how long user viewed content.

        Longer viewing = more interest.
        - < 3 seconds: Ignored (probably just scrolling)
        - 3-10 seconds: Weak positive
        - > 10 seconds: Stronger positive
        """
        try:
            if seconds < 3:
                return  # Ignore very short views

            signal_type = 'view_long' if seconds > 10 else 'view_short'
            weight = self.SIGNAL_WEIGHTS[signal_type]

            # Scale weight by time (up to 30 seconds max)
            time_multiplier = min(seconds / 30.0, 1.0)
            adjusted_weight = weight * (1 + time_multiplier)

            signal = self.BehaviorSignalModel.objects.create(
                user_id=user_id,
                signal_type=signal_type,
                content_id=content_id,
                weight=adjusted_weight,
                metadata={'style': style, 'model': model, 'seconds': seconds}
            )

            self._update_preference_score(user_id, style, model, adjusted_weight)

            logger.debug(f"Tracked view ({seconds}s) for user {user_id}: {content_id}")
            return signal
        except Exception as e:
            logger.error(f"Error tracking view time: {e}")

    def track_regenerate(
        self,
        user_id: int,
        original_content_id: str,
        new_content_id: str,
        style: str = None,
        model: str = None
    ) -> None:
        """
        Track when user regenerates (wasn't satisfied with first result).

        Regeneration = mild negative for original, user wanted something different.
        """
        try:
            signal = self.BehaviorSignalModel.objects.create(
                user_id=user_id,
                signal_type='regenerate',
                content_id=original_content_id,
                weight=self.SIGNAL_WEIGHTS['regenerate'],
                metadata={
                    'style': style,
                    'model': model,
                    'new_content_id': new_content_id
                }
            )

            self._update_preference_score(user_id, style, model, self.SIGNAL_WEIGHTS['regenerate'])

            logger.debug(f"Tracked regenerate for user {user_id}: {original_content_id} -> {new_content_id}")
            return signal
        except Exception as e:
            logger.error(f"Error tracking regenerate: {e}")

    def track_style_selection(
        self,
        user_id: int,
        style: str,
        context: str = None
    ) -> None:
        """
        Track when user explicitly selects a style.

        Direct style choice = explicit preference signal.
        """
        try:
            signal = self.BehaviorSignalModel.objects.create(
                user_id=user_id,
                signal_type='style_use',
                content_id='',  # No specific content
                weight=self.SIGNAL_WEIGHTS['style_use'],
                metadata={'style': style, 'context': context}
            )

            self._update_preference_score(user_id, style, None, self.SIGNAL_WEIGHTS['style_use'])

            logger.debug(f"Tracked style selection for user {user_id}: {style}")
            return signal
        except Exception as e:
            logger.error(f"Error tracking style selection: {e}")

    def track_favorite(
        self,
        user_id: int,
        content_id: str,
        style: str = None,
        model: str = None
    ) -> None:
        """Track when user favorites/likes content."""
        try:
            signal = self.BehaviorSignalModel.objects.create(
                user_id=user_id,
                signal_type='favorite',
                content_id=content_id,
                weight=self.SIGNAL_WEIGHTS['favorite'],
                metadata={'style': style, 'model': model}
            )

            self._update_preference_score(user_id, style, model, self.SIGNAL_WEIGHTS['favorite'])

            logger.info(f"Tracked favorite for user {user_id}: {content_id}")
            return signal
        except Exception as e:
            logger.error(f"Error tracking favorite: {e}")

    # ==================== Analysis Methods ====================

    def calculate_preference_scores(self, user_id: int, days: int = 90) -> Dict[str, Any]:
        """
        Calculate comprehensive preference scores from all behavioral signals.

        Args:
            user_id: User to analyze
            days: Look back period

        Returns:
            Dict with style scores, model scores, and insights
        """
        try:
            from django.utils import timezone
            since = timezone.now() - timedelta(days=days)

            signals = self.BehaviorSignalModel.objects.filter(
                user_id=user_id,
                created_at__gte=since
            ).order_by('-created_at')

            # Aggregate scores by style and model
            style_scores = defaultdict(float)
            model_scores = defaultdict(float)
            signal_counts = defaultdict(int)

            now = timezone.now()

            for signal in signals:
                metadata = signal.metadata or {}
                style = metadata.get('style')
                model = metadata.get('model')

                # Apply time decay
                age_days = (now - signal.created_at).days
                decay_factor = 0.5 ** (age_days / self.DECAY_HALF_LIFE_DAYS)
                weighted_score = signal.weight * decay_factor

                if style:
                    style_scores[style] += weighted_score
                    signal_counts[f'style_{style}'] += 1

                if model:
                    model_scores[model] += weighted_score
                    signal_counts[f'model_{model}'] += 1

            # Normalize scores to 0-1 range
            max_style = max(style_scores.values()) if style_scores else 1
            max_model = max(model_scores.values()) if model_scores else 1

            normalized_styles = {
                k: max(0, min(1, v / max_style))
                for k, v in sorted(style_scores.items(), key=lambda x: -x[1])
            }
            normalized_models = {
                k: max(0, min(1, v / max_model))
                for k, v in sorted(model_scores.items(), key=lambda x: -x[1])
            }

            # Get top preferences
            top_styles = list(normalized_styles.keys())[:5]
            top_models = list(normalized_models.keys())[:3]

            # Calculate confidence based on signal count
            total_signals = len(signals)
            confidence = min(1.0, total_signals / 50)  # Full confidence at 50+ signals

            return {
                'user_id': user_id,
                'period_days': days,
                'total_signals': total_signals,
                'confidence': confidence,
                'styles': normalized_styles,
                'models': normalized_models,
                'top_styles': top_styles,
                'top_models': top_models,
                'signal_breakdown': dict(signal_counts),
            }

        except Exception as e:
            logger.error(f"Error calculating preferences for user {user_id}: {e}")
            return {
                'user_id': user_id,
                'error': str(e),
                'styles': {},
                'models': {},
                'confidence': 0,
            }

    def get_style_affinity(self, user_id: int, style: str) -> float:
        """
        Get user's affinity score for a specific style.

        Returns:
            Float from -1 (strongly dislikes) to 1 (strongly likes)
        """
        prefs = self.calculate_preference_scores(user_id)
        return prefs.get('styles', {}).get(style, 0.0)

    def get_behavior_summary(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get a summary of user's recent behavior for insights.
        """
        try:
            from django.utils import timezone
            from django.db.models import Count, Sum

            since = timezone.now() - timedelta(days=days)

            signals = self.BehaviorSignalModel.objects.filter(
                user_id=user_id,
                created_at__gte=since
            )

            # Aggregate by signal type
            by_type = signals.values('signal_type').annotate(
                count=Count('id'),
                total_weight=Sum('weight')
            )

            type_summary = {
                item['signal_type']: {
                    'count': item['count'],
                    'total_weight': item['total_weight'] or 0
                }
                for item in by_type
            }

            # Calculate activity metrics
            total_generations = type_summary.get('generation', {}).get('count', 0)
            total_downloads = type_summary.get('download', {}).get('count', 0)
            total_shares = type_summary.get('share', {}).get('count', 0)
            total_deletes = type_summary.get('delete', {}).get('count', 0)

            # Satisfaction rate
            positive_actions = total_downloads + total_shares
            negative_actions = total_deletes
            satisfaction_rate = (
                positive_actions / max(1, positive_actions + negative_actions)
            )

            return {
                'user_id': user_id,
                'period_days': days,
                'total_generations': total_generations,
                'total_downloads': total_downloads,
                'total_shares': total_shares,
                'total_deletes': total_deletes,
                'satisfaction_rate': satisfaction_rate,
                'by_signal_type': type_summary,
            }

        except Exception as e:
            logger.error(f"Error getting behavior summary: {e}")
            return {'user_id': user_id, 'error': str(e)}

    # ==================== Private Methods ====================

    def _update_preference_score(
        self,
        user_id: int,
        style: str = None,
        model: str = None,
        score_delta: float = 0.0
    ) -> None:
        """Update the user's preference profile with new signal."""
        try:
            profile, created = self.UserPreferenceModel.objects.get_or_create(
                user_id=user_id,
                defaults={
                    'style_scores': {},
                    'model_scores': {},
                    'total_signals': 0,
                }
            )

            # Update style score
            if style:
                style_scores = profile.style_scores or {}
                current = style_scores.get(style, 0.0)
                style_scores[style] = current + score_delta
                profile.style_scores = style_scores

            # Update model score
            if model:
                model_scores = profile.model_scores or {}
                current = model_scores.get(model, 0.0)
                model_scores[model] = current + score_delta
                profile.model_scores = model_scores

            profile.total_signals = (profile.total_signals or 0) + 1
            profile.save()

        except Exception as e:
            logger.error(f"Error updating preference score: {e}")


    # ==================== Style Evolution Tracking ====================

    def record_daily_evolution(self, user_id: int, domain: str = 'image') -> Optional[Dict]:
        """
        Record a daily snapshot of user's style preferences.

        Should be called once per day (e.g., via Celery task) to track
        how preferences evolve over time.

        Args:
            user_id: User to snapshot
            domain: Content domain (image, video, audio, 3d)

        Returns:
            The created evolution record or None if error
        """
        try:
            from django.utils import timezone
            from core.models_unified_system import StyleEvolution

            today = timezone.now().date()

            # Check if already recorded today
            existing = StyleEvolution.objects.filter(
                user_id=user_id,
                date=today,
                domain=domain
            ).first()

            if existing:
                logger.debug(f"Evolution already recorded for user {user_id} on {today}")
                return {
                    'user_id': user_id,
                    'date': str(today),
                    'already_exists': True,
                    'style_distribution': existing.style_distribution,
                    'top_styles': existing.top_styles,
                }

            # Calculate current preferences
            prefs = self.calculate_preference_scores(user_id, days=30)
            styles = prefs.get('styles', {})

            if not styles:
                logger.debug(f"No style data for user {user_id}")
                return None

            # Normalize to distribution (sum to 1.0)
            total = sum(max(0, v) for v in styles.values()) or 1
            distribution = {k: max(0, v) / total for k, v in styles.items()}

            # Get top 5 styles
            top_styles = sorted(styles.keys(), key=lambda k: styles[k], reverse=True)[:5]

            # Create evolution record
            evolution = StyleEvolution.objects.create(
                user_id=user_id,
                date=today,
                domain=domain,
                style_distribution=distribution,
                top_styles=top_styles,
                total_signals=prefs.get('total_signals', 0),
                confidence_score=prefs.get('confidence', 0),
            )

            logger.info(f"Recorded style evolution for user {user_id}: {top_styles[:3]}")

            return {
                'user_id': user_id,
                'date': str(today),
                'domain': domain,
                'style_distribution': distribution,
                'top_styles': top_styles,
                'total_signals': prefs.get('total_signals', 0),
            }

        except Exception as e:
            logger.error(f"Error recording evolution for user {user_id}: {e}")
            return None

    def get_style_evolution_history(
        self,
        user_id: int,
        days: int = 30,
        domain: str = 'image'
    ) -> Dict[str, Any]:
        """
        Get user's style evolution over time.

        Returns:
            History of style preferences with trend analysis
        """
        try:
            from django.utils import timezone
            from core.models_unified_system import StyleEvolution

            since = timezone.now().date() - timedelta(days=days)

            records = StyleEvolution.objects.filter(
                user_id=user_id,
                domain=domain,
                date__gte=since
            ).order_by('date')

            if not records.exists():
                return {
                    'user_id': user_id,
                    'days': days,
                    'domain': domain,
                    'history': [],
                    'trends': {},
                    'message': 'No evolution data yet'
                }

            # Build history timeline
            history = []
            style_by_date = defaultdict(dict)

            for record in records:
                history.append({
                    'date': str(record.date),
                    'top_styles': record.top_styles,
                    'style_distribution': record.style_distribution,
                    'confidence': record.confidence_score,
                })
                for style, score in record.style_distribution.items():
                    style_by_date[style][str(record.date)] = score

            # Analyze trends - compare first half to second half
            first_records = list(records[:len(records)//2])
            second_records = list(records[len(records)//2:])

            trends = {}
            all_styles = set()
            for record in records:
                all_styles.update(record.style_distribution.keys())

            for style in all_styles:
                first_avg = 0
                second_avg = 0

                if first_records:
                    first_scores = [r.style_distribution.get(style, 0) for r in first_records]
                    first_avg = sum(first_scores) / len(first_scores)

                if second_records:
                    second_scores = [r.style_distribution.get(style, 0) for r in second_records]
                    second_avg = sum(second_scores) / len(second_scores)

                change = second_avg - first_avg
                if abs(change) > 0.05:  # Only report significant changes
                    trends[style] = {
                        'direction': 'rising' if change > 0 else 'falling',
                        'change': round(change, 3),
                        'first_period_avg': round(first_avg, 3),
                        'second_period_avg': round(second_avg, 3),
                    }

            # Find emerging and declining styles
            emerging = [s for s, t in trends.items() if t['direction'] == 'rising']
            declining = [s for s, t in trends.items() if t['direction'] == 'falling']

            return {
                'user_id': user_id,
                'days': days,
                'domain': domain,
                'record_count': len(history),
                'history': history,
                'trends': trends,
                'emerging_styles': emerging,
                'declining_styles': declining,
                'style_timelines': dict(style_by_date),
            }

        except Exception as e:
            logger.error(f"Error getting evolution history: {e}")
            return {'user_id': user_id, 'error': str(e)}

    def detect_style_shifts(self, user_id: int, domain: str = 'image') -> Dict[str, Any]:
        """
        Detect significant shifts in user's style preferences.

        Useful for triggering notifications or adjusting recommendations.

        Returns:
            Dict with shift detection results
        """
        try:
            history = self.get_style_evolution_history(user_id, days=14, domain=domain)

            if history.get('record_count', 0) < 3:
                return {
                    'user_id': user_id,
                    'shifts_detected': False,
                    'message': 'Insufficient data (need at least 3 days)',
                }

            trends = history.get('trends', {})
            emerging = history.get('emerging_styles', [])
            declining = history.get('declining_styles', [])

            # Significant shift = major change in top styles
            recent_history = history.get('history', [])
            if len(recent_history) >= 2:
                recent_top = set(recent_history[-1].get('top_styles', [])[:3])
                older_top = set(recent_history[0].get('top_styles', [])[:3])

                new_favorites = recent_top - older_top
                dropped_favorites = older_top - recent_top
            else:
                new_favorites = set()
                dropped_favorites = set()

            shifts = []

            if new_favorites:
                shifts.append({
                    'type': 'new_favorites',
                    'styles': list(new_favorites),
                    'description': f"New favorite styles: {', '.join(new_favorites)}"
                })

            if dropped_favorites:
                shifts.append({
                    'type': 'dropped_favorites',
                    'styles': list(dropped_favorites),
                    'description': f"Less used now: {', '.join(dropped_favorites)}"
                })

            # Strong emerging trends
            strong_emerging = [s for s in emerging if trends.get(s, {}).get('change', 0) > 0.1]
            if strong_emerging:
                shifts.append({
                    'type': 'strong_trend',
                    'styles': strong_emerging,
                    'description': f"Rapidly growing interest: {', '.join(strong_emerging)}"
                })

            return {
                'user_id': user_id,
                'shifts_detected': len(shifts) > 0,
                'shifts': shifts,
                'emerging_styles': emerging,
                'declining_styles': declining,
                'trends': trends,
            }

        except Exception as e:
            logger.error(f"Error detecting style shifts: {e}")
            return {'user_id': user_id, 'shifts_detected': False, 'error': str(e)}


# Convenience functions
def get_learning_service() -> ImplicitLearningService:
    """Get a singleton instance of the learning service."""
    return ImplicitLearningService()
