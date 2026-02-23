"""
Boardroom ML Recommendation Service
====================================

Session 954: Content-aware ML predictions for boardroom items.

Improvements over simple type-based learning:
1. Content similarity using embeddings
2. Bayesian confidence scoring (proper uncertainty)
3. Predictions based on similar past decisions
4. Auto-populates ml_prediction fields on HumanAttentionItem

Usage:
    from core.services.boardroom_ml_service import get_boardroom_ml_service

    service = get_boardroom_ml_service()
    prediction = service.predict_decision(attention_item)
    service.enrich_item_with_prediction(attention_item)
"""

import logging
import math
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Q

logger = logging.getLogger(__name__)


class BoardroomMLService:
    """
    Content-aware ML predictions for boardroom attention items.
    """

    # Weights for different signals
    WEIGHT_CONTENT_SIMILARITY = 0.5
    WEIGHT_TYPE_HISTORY = 0.2
    WEIGHT_SOURCE_HISTORY = 0.2
    WEIGHT_URGENCY_HISTORY = 0.1

    # Minimum samples for reliable predictions
    MIN_SAMPLES_FOR_PREDICTION = 3
    MIN_SAMPLES_FOR_HIGH_CONFIDENCE = 10

    # Similarity thresholds
    SIMILARITY_THRESHOLD = 0.65

    def __init__(self):
        self._embedding_service = None

    @property
    def embedding_service(self):
        """Lazy load embedding service."""
        if self._embedding_service is None:
            try:
                from core.services.embedding_service import get_embedding_service
                self._embedding_service = get_embedding_service()
            except Exception as e:
                logger.warning(f"Failed to load embedding service: {e}")
        return self._embedding_service

    def predict_decision(self, item) -> Dict[str, Any]:
        """
        Predict user decision on an attention item.

        Returns:
            Dict with:
                - prediction: 'approve', 'ignore', or 'uncertain'
                - confidence: 0.0-1.0
                - reasoning: explanation of prediction
                - similar_items: list of similar past decisions
        """
        from core.models_human_interface import HumanAttentionItem

        user = item.user

        # Get historical decisions
        past_decisions = HumanAttentionItem.objects.filter(
            user=user,
            decision__isnull=False,
            decided_at__isnull=False
        ).exclude(pk=item.pk).order_by('-decided_at')[:500]

        if past_decisions.count() < self.MIN_SAMPLES_FOR_PREDICTION:
            return {
                'prediction': 'uncertain',
                'confidence': 0.0,
                'reasoning': f'Insufficient decision history ({past_decisions.count()} < {self.MIN_SAMPLES_FOR_PREDICTION})',
                'similar_items': [],
            }

        # Collect prediction signals
        signals = []
        reasoning_parts = []

        # Signal 1: Content similarity
        content_signal = self._get_content_similarity_signal(item, past_decisions)
        if content_signal:
            signals.append((content_signal['approval_rate'], content_signal['confidence'], self.WEIGHT_CONTENT_SIMILARITY))
            reasoning_parts.append(content_signal['reasoning'])

        # Signal 2: Type history
        type_signal = self._get_type_history_signal(user, item.item_type)
        if type_signal:
            signals.append((type_signal['approval_rate'], type_signal['confidence'], self.WEIGHT_TYPE_HISTORY))
            reasoning_parts.append(type_signal['reasoning'])

        # Signal 3: Source history
        source_signal = self._get_source_history_signal(user, item.source_agent)
        if source_signal:
            signals.append((source_signal['approval_rate'], source_signal['confidence'], self.WEIGHT_SOURCE_HISTORY))
            reasoning_parts.append(source_signal['reasoning'])

        # Signal 4: Urgency history
        urgency_signal = self._get_urgency_history_signal(user, item.urgency)
        if urgency_signal:
            signals.append((urgency_signal['approval_rate'], urgency_signal['confidence'], self.WEIGHT_URGENCY_HISTORY))
            reasoning_parts.append(urgency_signal['reasoning'])

        if not signals:
            return {
                'prediction': 'uncertain',
                'confidence': 0.0,
                'reasoning': 'No usable signals found',
                'similar_items': [],
            }

        # Combine signals using weighted average
        combined_rate, combined_confidence = self._combine_signals(signals)

        # Determine prediction
        if combined_rate >= 0.6:
            prediction = 'approve'
        elif combined_rate <= 0.4:
            prediction = 'ignore'
        else:
            prediction = 'uncertain'

        return {
            'prediction': prediction,
            'confidence': combined_confidence,
            'approval_probability': combined_rate,
            'reasoning': ' | '.join(reasoning_parts),
            'similar_items': content_signal.get('similar_items', []) if content_signal else [],
        }

    def _get_content_similarity_signal(
        self,
        item,
        past_decisions
    ) -> Optional[Dict[str, Any]]:
        """Find similar past items by content and calculate approval rate."""

        if not self.embedding_service:
            return None

        # Create content string for the new item
        item_content = f"{item.title} {item.summary}"

        try:
            # Collect all texts for a single batch embedding call
            past_items_list = list(past_decisions[:100])
            all_texts = [item_content] + [
                f"{pi.title} {pi.summary}" for pi in past_items_list
            ]

            # One API call instead of N individual calls — fixes 3GB memory spike
            all_embeddings = self.embedding_service.get_embeddings_sync(all_texts)

            if not all_embeddings or all_embeddings[0] is None:
                return None

            item_embedding = all_embeddings[0]

            # Find similar past items
            similar_items = []

            for i, past_item in enumerate(past_items_list):
                past_embedding = all_embeddings[i + 1] if (i + 1) < len(all_embeddings) else None

                if past_embedding is not None:
                    similarity = self._cosine_similarity(item_embedding, past_embedding)

                    if similarity >= self.SIMILARITY_THRESHOLD:
                        similar_items.append({
                            'id': str(past_item.pk),
                            'title': past_item.title,
                            'decision': past_item.decision,
                            'similarity': similarity,
                        })

            if len(similar_items) < 2:
                return None

            # Sort by similarity
            similar_items.sort(key=lambda x: x['similarity'], reverse=True)
            similar_items = similar_items[:10]  # Top 10

            # Calculate weighted approval rate
            approvals = sum(
                s['similarity'] for s in similar_items
                if s['decision'] in ['approve', 'promote']
            )
            total_weight = sum(s['similarity'] for s in similar_items)

            approval_rate = approvals / total_weight if total_weight > 0 else 0.5

            # Confidence based on number of similar items
            confidence = self._wilson_score_confidence(
                successes=len([s for s in similar_items if s['decision'] in ['approve', 'promote']]),
                trials=len(similar_items)
            )

            return {
                'approval_rate': approval_rate,
                'confidence': confidence,
                'reasoning': f"Similar content: {len(similar_items)} matches, {approval_rate:.0%} approved",
                'similar_items': similar_items[:5],
            }

        except Exception as e:
            logger.warning(f"Content similarity failed: {e}")
            return None

    def _get_type_history_signal(self, user, item_type: str) -> Optional[Dict[str, Any]]:
        """Get approval rate for this item type."""
        from core.models_human_interface import HumanAttentionItem

        type_decisions = HumanAttentionItem.objects.filter(
            user=user,
            item_type=item_type,
            decision__isnull=False
        ).values('decision').annotate(count=Count('decision'))

        stats = {d['decision']: d['count'] for d in type_decisions}
        approvals = stats.get('approve', 0) + stats.get('promote', 0)
        total = sum(stats.values())

        if total < 2:
            return None

        approval_rate = approvals / total
        confidence = self._wilson_score_confidence(approvals, total)

        return {
            'approval_rate': approval_rate,
            'confidence': confidence,
            'reasoning': f"Type '{item_type}': {approval_rate:.0%} of {total}",
        }

    def _get_source_history_signal(self, user, source_agent: str) -> Optional[Dict[str, Any]]:
        """Get approval rate for this source agent."""
        from core.models_human_interface import HumanAttentionItem

        if not source_agent:
            return None

        source_decisions = HumanAttentionItem.objects.filter(
            user=user,
            source_agent=source_agent,
            decision__isnull=False
        ).values('decision').annotate(count=Count('decision'))

        stats = {d['decision']: d['count'] for d in source_decisions}
        approvals = stats.get('approve', 0) + stats.get('promote', 0)
        total = sum(stats.values())

        if total < 2:
            return None

        approval_rate = approvals / total
        confidence = self._wilson_score_confidence(approvals, total)

        return {
            'approval_rate': approval_rate,
            'confidence': confidence,
            'reasoning': f"Source '{source_agent}': {approval_rate:.0%} of {total}",
        }

    def _get_urgency_history_signal(self, user, urgency: str) -> Optional[Dict[str, Any]]:
        """Get approval rate for this urgency level."""
        from core.models_human_interface import HumanAttentionItem

        urgency_decisions = HumanAttentionItem.objects.filter(
            user=user,
            urgency=urgency,
            decision__isnull=False
        ).values('decision').annotate(count=Count('decision'))

        stats = {d['decision']: d['count'] for d in urgency_decisions}
        approvals = stats.get('approve', 0) + stats.get('promote', 0)
        total = sum(stats.values())

        if total < 3:
            return None

        approval_rate = approvals / total
        confidence = self._wilson_score_confidence(approvals, total)

        return {
            'approval_rate': approval_rate,
            'confidence': confidence,
            'reasoning': f"Urgency '{urgency}': {approval_rate:.0%} of {total}",
        }

    def _combine_signals(
        self,
        signals: List[Tuple[float, float, float]]
    ) -> Tuple[float, float]:
        """
        Combine multiple prediction signals.

        Args:
            signals: List of (rate, confidence, weight) tuples

        Returns:
            (combined_rate, combined_confidence)
        """
        if not signals:
            return 0.5, 0.0

        # Weight by both the configured weight AND the confidence
        total_weight = 0.0
        weighted_rate = 0.0
        confidence_product = 1.0

        for rate, confidence, weight in signals:
            effective_weight = weight * confidence
            weighted_rate += rate * effective_weight
            total_weight += effective_weight
            # Combine confidences (product gives lower bound)
            confidence_product *= (1 - confidence * weight)

        combined_rate = weighted_rate / total_weight if total_weight > 0 else 0.5
        combined_confidence = 1 - confidence_product

        # Reduce confidence if prediction is uncertain (near 0.5)
        uncertainty_penalty = 1 - abs(combined_rate - 0.5) * 2
        combined_confidence *= (1 - uncertainty_penalty * 0.3)

        return combined_rate, min(0.95, combined_confidence)

    def _wilson_score_confidence(
        self,
        successes: int,
        trials: int,
        z: float = 1.96
    ) -> float:
        """
        Wilson score confidence interval - proper statistical confidence.

        Returns a confidence score 0-1 based on sample size and variance.
        With more samples, confidence approaches true rate.
        With few samples, confidence stays low even with 100% success.
        """
        if trials == 0:
            return 0.0

        p = successes / trials

        # Wilson score lower bound
        denominator = 1 + z * z / trials
        center = p + z * z / (2 * trials)
        spread = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials))

        lower_bound = (center - spread) / denominator
        upper_bound = (center + spread) / denominator

        # Confidence is inversely related to interval width
        interval_width = upper_bound - lower_bound

        # Map to 0-1 confidence (narrower interval = higher confidence)
        # At 10 samples, interval is ~0.3, at 100 samples ~0.1
        confidence = max(0, 1 - interval_width * 2)

        # Boost for more samples
        sample_boost = min(1.0, trials / 20)

        return confidence * sample_boost

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def enrich_item_with_prediction(self, item, save: bool = True) -> bool:
        """
        Populate ml_prediction, ml_confidence, ml_recommendation on an item.

        Returns True if enriched successfully.
        """
        try:
            prediction = self.predict_decision(item)

            item.ml_prediction = {
                'prediction': prediction['prediction'],
                'approval_probability': prediction.get('approval_probability', 0.5),
                'reasoning': prediction['reasoning'],
                'similar_items': prediction.get('similar_items', []),
                'predicted_at': timezone.now().isoformat(),
            }
            item.ml_confidence = prediction['confidence']
            item.ml_recommendation = prediction['prediction']

            if save:
                item.save(update_fields=['ml_prediction', 'ml_confidence', 'ml_recommendation'])

            logger.info(
                f"🤖 ML prediction for {item.title[:50]}: {prediction['prediction']} "
                f"({prediction['confidence']:.0%} confidence)"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to enrich item with prediction: {e}")
            return False

    def batch_enrich_pending_items(self, user, limit: int = 50) -> Dict[str, int]:
        """
        Enrich all pending items without ML predictions for a user.

        Returns stats dict.
        """
        from core.models_human_interface import HumanAttentionItem

        pending_items = HumanAttentionItem.objects.filter(
            user=user,
            status__in=['pending', 'viewed'],
            ml_prediction__isnull=True
        )[:limit]

        stats = {'enriched': 0, 'failed': 0, 'skipped': 0}

        for item in pending_items:
            if self.enrich_item_with_prediction(item):
                stats['enriched'] += 1
            else:
                stats['failed'] += 1

        logger.info(f"📊 Batch enrichment complete: {stats}")
        return stats

    def get_recommendation_summary(self, user) -> Dict[str, Any]:
        """
        Get a summary of ML recommendations for the user.

        Returns insights about prediction accuracy and patterns.
        """
        from core.models_human_interface import HumanAttentionItem

        # Get items with predictions that have been decided
        decided_items = HumanAttentionItem.objects.filter(
            user=user,
            ml_prediction__isnull=False,
            decision__isnull=False
        ).order_by('-decided_at')[:100]

        if decided_items.count() < 5:
            return {
                'accuracy': None,
                'total_predictions': decided_items.count(),
                'message': 'Insufficient data for accuracy analysis',
            }

        correct = 0
        total = 0

        for item in decided_items:
            prediction = item.ml_prediction.get('prediction') if item.ml_prediction else None
            actual = item.decision

            if prediction and actual:
                total += 1
                # Check if prediction matched
                if prediction == 'approve' and actual in ['approve', 'promote']:
                    correct += 1
                elif prediction == 'ignore' and actual in ['ignore', 'reject']:
                    correct += 1
                elif prediction == 'uncertain':
                    # Don't count uncertain predictions against accuracy
                    total -= 1

        accuracy = correct / total if total > 0 else None

        return {
            'accuracy': accuracy,
            'correct_predictions': correct,
            'total_predictions': total,
            'message': f"ML accuracy: {accuracy:.0%}" if accuracy else 'No predictions to evaluate',
        }


# Singleton instance
_boardroom_ml_service: Optional[BoardroomMLService] = None


def get_boardroom_ml_service() -> BoardroomMLService:
    """Get the singleton BoardroomMLService instance."""
    global _boardroom_ml_service
    if _boardroom_ml_service is None:
        _boardroom_ml_service = BoardroomMLService()
    return _boardroom_ml_service
