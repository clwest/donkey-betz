"""
Scoring Dispatcher Service
Session 470: Market Intelligence Architecture - Phase 2

Routes scoring requests to either real-time or batch processing
based on configuration, SLA thresholds, and current load.

Updated Session 472: Integrated with Event Bus for centralized event publishing.
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any, List
from django.utils import timezone

logger = logging.getLogger(__name__)


def _publish_scoring_event(spider_data, result, mode: str, latency_ms: float):
    """Helper to publish scoring events to the event bus."""
    try:
        from core.services.event_bus import publish_opportunity_scored_event

        # Try to get opportunity ID if it exists
        opportunity_id = None
        try:
            from core.models_unified_system import Opportunity
            opportunity = Opportunity.objects.filter(
                source_data=spider_data
            ).first()
            if opportunity:
                opportunity_id = str(opportunity.id)
        except Exception as _e:
            logger.warning(
                "scoring_dispatcher._publish_scoring_event: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

        publish_opportunity_scored_event(
            opportunity_id=opportunity_id,
            spider_data_id=str(spider_data.id),
            ml_score=result.ml_score if hasattr(result, 'ml_score') else None,
            rule_score=result.rule_score if hasattr(result, 'rule_score') else None,
            hybrid_score=result.hybrid_score if hasattr(result, 'hybrid_score') else None,
            confidence=result.confidence if hasattr(result, 'confidence') else None,
            source=f'scoring_dispatcher_{mode}'
        )

        logger.debug(f"📡 Published opportunity_scored event to event bus")

    except ImportError:
        logger.debug("Event bus not available, skipping event publish")
    except Exception as e:
        logger.warning(f"Failed to publish scoring event: {e}")


def _create_scoring_provenance(spider_data, result, explanation_id: str = None):
    """Helper to create provenance for scoring results."""
    try:
        from core.services.provenance_tracker import create_scoring_provenance

        # Use explanation_id as scoring_id if available, otherwise generate one
        scoring_id = explanation_id or f"score_{spider_data.id}_{timezone.now().timestamp()}"

        # For now, we don't have a parent provenance from opportunity
        # In full integration, this would come from the opportunity's provenance
        create_scoring_provenance(
            scoring_id=scoring_id,
            opportunity_provenance_id=None,  # Would be linked in full integration
            ml_score=result.ml_score if hasattr(result, 'ml_score') else 0.0,
            rule_score=result.rule_score if hasattr(result, 'rule_score') else 0.0,
            hybrid_score=result.hybrid_score if hasattr(result, 'hybrid_score') else 0.0,
            confidence=result.confidence if hasattr(result, 'confidence') else 0.0,
            model_version='ml_scoring_v1',
            metadata={
                'spider_data_id': str(spider_data.id),
                'spider_source': spider_data.source if hasattr(spider_data, 'source') else '',
                'scoring_time_ms': result.scoring_time_ms if hasattr(result, 'scoring_time_ms') else None,
            }
        )

        logger.debug(f"📜 Created provenance for scoring {scoring_id}")

    except ImportError:
        logger.debug("Provenance tracker not available, skipping provenance creation")
    except Exception as e:
        logger.warning(f"Failed to create scoring provenance: {e}")


class ScoringPriority(Enum):
    """Priority levels for scoring requests."""
    HIGH = 1      # User-triggered, immediate processing
    NORMAL = 2    # Background scoring
    LOW = 3       # Backfill/reprocessing


class ScoringMode(Enum):
    """How scoring should be processed."""
    REALTIME = 'realtime'   # Immediate scoring, synchronous response
    BATCH = 'batch'         # Queue for async processing
    AUTO = 'auto'           # System decides based on load/SLA


@dataclass
class ScoringRequest:
    """A request to score spider data."""
    spider_data_id: str
    priority: ScoringPriority = ScoringPriority.NORMAL
    source: str = 'system'
    user_id: Optional[int] = None
    callback_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ScoringResponse:
    """Response from a scoring request."""
    success: bool
    mode: str  # 'realtime' or 'batch'
    score: Optional[float] = None
    explanation_id: Optional[str] = None
    queue_position: Optional[int] = None
    estimated_wait_ms: Optional[int] = None
    latency_ms: Optional[float] = None
    error: Optional[str] = None


class ScoringDispatcher:
    """
    Routes scoring requests based on configuration and load.

    Session 470: Market Intelligence Architecture - Phase 2

    Features:
    - Real-time vs batch routing
    - SLA-based automatic mode switching
    - Priority queue management
    - Latency tracking and metrics
    """

    # Latency tracking window
    LATENCY_WINDOW_SIZE = 100

    # Auto-switch thresholds
    QUEUE_DEPTH_THRESHOLD = 50  # Switch to batch if queue > this
    CPU_THRESHOLD = 80  # Switch to batch if CPU > this %

    def __init__(self):
        self._recent_latencies: List[float] = []
        self._mode_switches = 0
        self._last_sla_breach = None
        logger.info("🚦 Scoring Dispatcher initialized")

    def dispatch(
        self,
        spider_data,
        priority: ScoringPriority = ScoringPriority.NORMAL,
        source: str = 'system',
        user=None,
        force_mode: Optional[ScoringMode] = None
    ) -> ScoringResponse:
        """
        Dispatch a scoring request.

        Args:
            spider_data: SpiderData model instance to score
            priority: Processing priority
            source: Where the request came from
            user: User who requested the scoring
            force_mode: Override auto-detection and use this mode

        Returns:
            ScoringResponse with results or queue position
        """
        start_time = time.time()

        try:
            # Get configuration
            from core.models_unified_system import ScoringConfiguration
            config = ScoringConfiguration.get_config(user)

            # Determine scoring mode
            if force_mode:
                mode = force_mode
            else:
                mode = self._determine_mode(config, priority)

            logger.info(
                f"🚦 [DISPATCHER] Routing {spider_data.id} via {mode.value} "
                f"(priority={priority.name}, source={source})"
            )

            # Route to appropriate handler
            if mode == ScoringMode.REALTIME:
                response = self._score_realtime(spider_data, config)
            else:
                response = self._queue_for_batch(spider_data, priority, source, user)

            # Track metrics
            latency_ms = (time.time() - start_time) * 1000
            response.latency_ms = latency_ms
            self._track_latency(latency_ms)
            config.record_request(latency_ms, mode.value)

            return response

        except Exception as e:
            logger.error(f"❌ [DISPATCHER] Error dispatching: {e}")
            return ScoringResponse(
                success=False,
                mode='error',
                error=str(e),
                latency_ms=(time.time() - start_time) * 1000
            )

    def _determine_mode(
        self,
        config,
        priority: ScoringPriority
    ) -> ScoringMode:
        """Determine whether to use realtime or batch scoring."""
        # Check explicit configuration
        if config.scoring_mode == 'realtime':
            return ScoringMode.REALTIME
        elif config.scoring_mode == 'batch':
            return ScoringMode.BATCH

        # Auto mode - use heuristics
        # High priority always gets realtime
        if priority == ScoringPriority.HIGH:
            return ScoringMode.REALTIME

        # Low priority always goes to batch
        if priority == ScoringPriority.LOW:
            return ScoringMode.BATCH

        # Check recent latency
        avg_latency = self._get_average_latency()
        if avg_latency > config.auto_switch_threshold_ms:
            logger.warning(
                f"🚦 [DISPATCHER] Switching to batch mode: "
                f"avg latency {avg_latency:.0f}ms > {config.auto_switch_threshold_ms}ms"
            )
            self._mode_switches += 1
            return ScoringMode.BATCH

        # Check queue depth
        queue_depth = self._get_queue_depth()
        if queue_depth > self.QUEUE_DEPTH_THRESHOLD:
            logger.warning(
                f"🚦 [DISPATCHER] Switching to batch mode: "
                f"queue depth {queue_depth} > {self.QUEUE_DEPTH_THRESHOLD}"
            )
            self._mode_switches += 1
            return ScoringMode.BATCH

        # Default to realtime for normal priority
        return ScoringMode.REALTIME

    def _score_realtime(self, spider_data, config) -> ScoringResponse:
        """Score immediately and return result."""
        from core.services.ml_scoring_engine import get_ml_scoring_engine

        engine = get_ml_scoring_engine()
        result = engine.score_opportunity(spider_data)

        if not result.success:
            return ScoringResponse(
                success=False,
                mode='realtime',
                error=result.error or 'Scoring failed'
            )

        # Store explanation if configured
        explanation_id = None
        if config.store_explanations and result.shap_explanation:
            explanation_id = self._store_explanation(spider_data, result, config)

        # Publish scoring event to event bus
        _publish_scoring_event(spider_data, result, 'realtime', result.scoring_time_ms or 0)

        # Create provenance record for scoring
        _create_scoring_provenance(spider_data, result, str(explanation_id) if explanation_id else None)

        return ScoringResponse(
            success=True,
            mode='realtime',
            score=result.hybrid_score,
            explanation_id=str(explanation_id) if explanation_id else None
        )

    def _queue_for_batch(
        self,
        spider_data,
        priority: ScoringPriority,
        source: str,
        user
    ) -> ScoringResponse:
        """Add to batch queue for async processing."""
        from core.models_unified_system import ScoringQueueItem
        from datetime import timedelta

        # Create queue item
        queue_item = ScoringQueueItem.objects.create(
            spider_data=spider_data,
            priority=priority.value,
            request_source=source,
            requested_by=user,
            expires_at=timezone.now() + timedelta(hours=24)
        )

        # Get queue position
        position = ScoringQueueItem.objects.filter(
            status='pending',
            priority__lte=priority.value,
            created_at__lte=queue_item.created_at
        ).count()

        # Estimate wait time based on historical processing rate
        estimated_wait = self._estimate_wait_time(position)

        logger.info(
            f"🚦 [DISPATCHER] Queued {spider_data.id} at position {position}, "
            f"estimated wait: {estimated_wait}ms"
        )

        return ScoringResponse(
            success=True,
            mode='batch',
            queue_position=position,
            estimated_wait_ms=estimated_wait
        )

    def _store_explanation(self, spider_data, result, config) -> Optional[str]:
        """Store SHAP explanation in database."""
        try:
            from core.models_unified_system import ScoringExplanation, Opportunity

            # Find or create opportunity for this spider data
            opportunity = Opportunity.objects.filter(
                source_data=spider_data
            ).first()

            if not opportunity:
                # No opportunity yet - explanation will be stored when opportunity is created
                return None

            # Check if explanation already exists
            if hasattr(opportunity, 'ml_explanation'):
                # Update existing
                explanation = opportunity.ml_explanation
            else:
                explanation = ScoringExplanation(opportunity=opportunity)

            # Populate fields
            explanation.ml_score = result.ml_score
            explanation.rule_score = result.rule_score
            explanation.hybrid_score = result.hybrid_score
            explanation.confidence = result.confidence

            if result.shap_explanation:
                explanation.shap_base_value = result.shap_explanation.base_value
                explanation.shap_values = result.shap_explanation.shap_values
                explanation.feature_names = result.shap_explanation.feature_names
                explanation.feature_values = result.shap_explanation.feature_values
                explanation.top_positive_features = result.shap_explanation.top_positive
                explanation.top_negative_features = result.shap_explanation.top_negative

            explanation.scoring_time_ms = result.scoring_time_ms
            explanation.save()

            return str(explanation.id)

        except Exception as e:
            logger.warning(f"⚠️ [DISPATCHER] Failed to store explanation: {e}")
            return None

    def _track_latency(self, latency_ms: float):
        """Track latency for SLA monitoring."""
        self._recent_latencies.append(latency_ms)
        if len(self._recent_latencies) > self.LATENCY_WINDOW_SIZE:
            self._recent_latencies.pop(0)

    def _get_average_latency(self) -> float:
        """Get average latency from recent requests."""
        if not self._recent_latencies:
            return 0.0
        return sum(self._recent_latencies) / len(self._recent_latencies)

    def _get_queue_depth(self) -> int:
        """Get current queue depth."""
        try:
            from core.models_unified_system import ScoringQueueItem
            return ScoringQueueItem.objects.filter(status='pending').count()
        except Exception:
            return 0

    def _estimate_wait_time(self, position: int) -> int:
        """Estimate wait time based on position and processing rate."""
        # Estimate based on average processing time per item
        avg_processing_time_ms = 100  # Default estimate
        if self._recent_latencies:
            avg_processing_time_ms = self._get_average_latency()

        return int(position * avg_processing_time_ms)

    def get_metrics(self) -> Dict[str, Any]:
        """Get dispatcher metrics."""
        return {
            'average_latency_ms': round(self._get_average_latency(), 2),
            'recent_requests': len(self._recent_latencies),
            'queue_depth': self._get_queue_depth(),
            'mode_switches': self._mode_switches,
            'last_sla_breach': self._last_sla_breach
        }

    def process_batch_queue(self, batch_size: int = 100) -> Dict[str, Any]:
        """
        Process pending items in the batch queue.

        Args:
            batch_size: Maximum items to process

        Returns:
            Dict with processing statistics
        """
        from core.models_unified_system import ScoringQueueItem, ScoringConfiguration
        from core.services.ml_scoring_engine import get_ml_scoring_engine

        logger.info(f"🚦 [DISPATCHER] Processing batch queue (max {batch_size} items)")

        # Get pending items by priority
        pending = ScoringQueueItem.objects.filter(
            status='pending'
        ).select_related('spider_data').order_by('priority', 'created_at')[:batch_size]

        if not pending:
            logger.info("🚦 [DISPATCHER] No pending items in queue")
            return {'processed': 0, 'success': 0, 'failed': 0}

        engine = get_ml_scoring_engine()
        config = ScoringConfiguration.get_config()

        stats = {
            'processed': 0,
            'success': 0,
            'failed': 0,
            'total_latency_ms': 0
        }

        for item in pending:
            try:
                # Mark as processing
                item.status = 'processing'
                item.started_at = timezone.now()
                item.save(update_fields=['status', 'started_at'])

                # Score
                result = engine.score_opportunity(item.spider_data)

                # Update item
                item.completed_at = timezone.now()
                if result.success:
                    item.status = 'completed'
                    item.result_score = result.hybrid_score

                    # Store explanation
                    if config.store_explanations:
                        exp_id = self._store_explanation(item.spider_data, result, config)
                        if exp_id:
                            item.result_explanation_id = exp_id

                    # Publish scoring event to event bus
                    _publish_scoring_event(
                        item.spider_data, result, 'batch',
                        result.scoring_time_ms or 0
                    )

                    # Create provenance record for scoring
                    _create_scoring_provenance(item.spider_data, result, exp_id)

                    stats['success'] += 1
                else:
                    item.status = 'failed'
                    item.error_message = result.error or 'Unknown error'
                    stats['failed'] += 1

                item.save()
                stats['processed'] += 1

                if item.latency_ms:
                    stats['total_latency_ms'] += item.latency_ms

            except Exception as e:
                logger.error(f"❌ [DISPATCHER] Failed to process {item.id}: {e}")
                item.status = 'failed'
                item.error_message = str(e)
                item.completed_at = timezone.now()
                item.save()
                stats['failed'] += 1
                stats['processed'] += 1

        avg_latency = (
            stats['total_latency_ms'] / stats['processed']
            if stats['processed'] > 0 else 0
        )
        stats['avg_latency_ms'] = round(avg_latency, 2)

        logger.info(
            f"🚦 [DISPATCHER] Batch complete: "
            f"{stats['success']}/{stats['processed']} success, "
            f"avg latency: {stats['avg_latency_ms']}ms"
        )

        return stats

    def cleanup_expired(self) -> int:
        """Remove expired queue items."""
        from core.models_unified_system import ScoringQueueItem

        expired = ScoringQueueItem.objects.filter(
            status='pending',
            expires_at__lt=timezone.now()
        )
        count = expired.count()
        expired.update(status='expired')

        if count > 0:
            logger.info(f"🚦 [DISPATCHER] Expired {count} queue items")

        return count


# Singleton instance
_dispatcher_instance: Optional[ScoringDispatcher] = None


def get_scoring_dispatcher() -> ScoringDispatcher:
    """Get singleton scoring dispatcher instance."""
    global _dispatcher_instance
    if _dispatcher_instance is None:
        _dispatcher_instance = ScoringDispatcher()
    return _dispatcher_instance
