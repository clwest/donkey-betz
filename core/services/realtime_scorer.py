"""
Real-time Scoring Service with Redis Priority Queue
Session 470: Market Intelligence Architecture - Phase 2

Provides low-latency scoring with Redis-backed priority queuing
for high-volume scoring requests.
"""

import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class QueuePriority(Enum):
    """Priority levels for Redis queue."""
    HIGH = 'scoring:queue:high'
    NORMAL = 'scoring:queue:normal'
    LOW = 'scoring:queue:low'


@dataclass
class QueuedScoringRequest:
    """A scoring request in the Redis queue."""
    id: str
    spider_data_id: str
    priority: str
    source: str
    user_id: Optional[int]
    created_at: str
    callback_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_json(self) -> str:
        """Serialize to JSON for Redis storage."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, data: str) -> 'QueuedScoringRequest':
        """Deserialize from Redis JSON."""
        return cls(**json.loads(data))


class RealtimeScorer:
    """
    Redis-backed priority queue scorer for low-latency scoring.

    Session 470: Market Intelligence Architecture - Phase 2

    Features:
    - Three-tier priority queue (high/normal/low)
    - Configurable SLA targets
    - Automatic queue draining
    - Dead letter queue for failed items
    """

    # Redis key prefixes
    QUEUE_PREFIX = 'mi:scoring:queue'
    PROCESSING_PREFIX = 'mi:scoring:processing'
    RESULT_PREFIX = 'mi:scoring:result'
    DLQ_PREFIX = 'mi:scoring:dlq'
    METRICS_KEY = 'mi:scoring:metrics'

    # Default settings
    DEFAULT_SLA_MS = 500
    DEFAULT_TIMEOUT_SEC = 30
    MAX_RETRIES = 3

    def __init__(self):
        self._redis = None
        self._sla_target_ms = self.DEFAULT_SLA_MS
        self._processing_timeout = self.DEFAULT_TIMEOUT_SEC
        logger.info("⚡ Realtime Scorer initialized")

    @property
    def redis(self):
        """Lazy-load Redis connection."""
        if self._redis is None:
            import redis
            self._redis = redis.from_url(
                settings.REDIS_URL if hasattr(settings, 'REDIS_URL')
                else 'redis://localhost:6379/0'
            )
        return self._redis

    def enqueue(
        self,
        spider_data_id: str,
        priority: QueuePriority = QueuePriority.NORMAL,
        source: str = 'api',
        user_id: Optional[int] = None,
        callback_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a scoring request to the priority queue.

        Args:
            spider_data_id: ID of SpiderData to score
            priority: Queue priority level
            source: Request source identifier
            user_id: Optional user who requested
            callback_url: Optional webhook for results
            metadata: Additional context

        Returns:
            Request ID for tracking
        """
        import uuid

        request_id = str(uuid.uuid4())
        request = QueuedScoringRequest(
            id=request_id,
            spider_data_id=spider_data_id,
            priority=priority.name,
            source=source,
            user_id=user_id,
            created_at=datetime.utcnow().isoformat(),
            callback_url=callback_url,
            metadata=metadata
        )

        # Add to appropriate queue
        queue_key = f"{self.QUEUE_PREFIX}:{priority.name.lower()}"
        self.redis.lpush(queue_key, request.to_json())

        # Update metrics
        self._increment_metric('enqueued')
        self._increment_metric(f'enqueued:{priority.name.lower()}')

        logger.debug(
            f"⚡ [REALTIME] Enqueued {request_id} to {priority.name} queue"
        )

        return request_id

    def dequeue(self, timeout_sec: int = 1) -> Optional[QueuedScoringRequest]:
        """
        Get next item from queues (priority order).

        Uses Redis BRPOP for blocking wait across multiple queues.

        Args:
            timeout_sec: Max seconds to wait for item

        Returns:
            QueuedScoringRequest or None if queue empty
        """
        # Check queues in priority order
        queues = [
            f"{self.QUEUE_PREFIX}:high",
            f"{self.QUEUE_PREFIX}:normal",
            f"{self.QUEUE_PREFIX}:low"
        ]

        result = self.redis.brpop(queues, timeout=timeout_sec)
        if result is None:
            return None

        queue_name, data = result
        request = QueuedScoringRequest.from_json(data.decode('utf-8'))

        # Mark as processing
        processing_key = f"{self.PROCESSING_PREFIX}:{request.id}"
        self.redis.setex(
            processing_key,
            self._processing_timeout,
            request.to_json()
        )

        self._increment_metric('dequeued')
        return request

    def complete(
        self,
        request_id: str,
        score: float,
        explanation_id: Optional[str] = None,
        latency_ms: Optional[float] = None
    ):
        """
        Mark a scoring request as complete.

        Args:
            request_id: Request ID to complete
            score: Final score result
            explanation_id: Optional explanation record ID
            latency_ms: Processing latency
        """
        # Store result
        result = {
            'request_id': request_id,
            'score': score,
            'explanation_id': explanation_id,
            'latency_ms': latency_ms,
            'completed_at': datetime.utcnow().isoformat()
        }
        result_key = f"{self.RESULT_PREFIX}:{request_id}"
        self.redis.setex(result_key, 3600, json.dumps(result))  # 1 hour TTL

        # Remove from processing
        processing_key = f"{self.PROCESSING_PREFIX}:{request_id}"
        self.redis.delete(processing_key)

        # Update metrics
        self._increment_metric('completed')
        if latency_ms:
            self._track_latency(latency_ms)

        logger.debug(f"⚡ [REALTIME] Completed {request_id} score={score}")

    def fail(
        self,
        request_id: str,
        error: str,
        retry: bool = True
    ):
        """
        Mark a scoring request as failed.

        Args:
            request_id: Request ID that failed
            error: Error message
            retry: Whether to retry (if retries remain)
        """
        processing_key = f"{self.PROCESSING_PREFIX}:{request_id}"
        data = self.redis.get(processing_key)

        if data:
            request = QueuedScoringRequest.from_json(data.decode('utf-8'))

            # Check retry count
            retry_count = (request.metadata or {}).get('retry_count', 0)

            if retry and retry_count < self.MAX_RETRIES:
                # Re-enqueue with incremented retry count
                request.metadata = request.metadata or {}
                request.metadata['retry_count'] = retry_count + 1
                request.metadata['last_error'] = error

                queue_key = f"{self.QUEUE_PREFIX}:{request.priority.lower()}"
                self.redis.lpush(queue_key, request.to_json())
                self._increment_metric('retried')
                logger.warning(
                    f"⚡ [REALTIME] Retrying {request_id} (attempt {retry_count + 1})"
                )
            else:
                # Move to dead letter queue
                dlq_key = f"{self.DLQ_PREFIX}:{request_id}"
                failed_data = {
                    'request': asdict(request),
                    'error': error,
                    'failed_at': datetime.utcnow().isoformat()
                }
                self.redis.setex(dlq_key, 86400 * 7, json.dumps(failed_data))  # 7 days
                self._increment_metric('failed')
                logger.error(f"⚡ [REALTIME] Failed {request_id}: {error}")

        # Clean up processing marker
        self.redis.delete(processing_key)

    def get_result(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get result for a completed request."""
        result_key = f"{self.RESULT_PREFIX}:{request_id}"
        data = self.redis.get(result_key)
        if data:
            return json.loads(data.decode('utf-8'))
        return None

    def get_queue_depths(self) -> Dict[str, int]:
        """Get current depth of each queue."""
        return {
            'high': self.redis.llen(f"{self.QUEUE_PREFIX}:high"),
            'normal': self.redis.llen(f"{self.QUEUE_PREFIX}:normal"),
            'low': self.redis.llen(f"{self.QUEUE_PREFIX}:low"),
            'processing': len(self.redis.keys(f"{self.PROCESSING_PREFIX}:*")),
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get scoring metrics from Redis."""
        metrics = self.redis.hgetall(self.METRICS_KEY)
        return {
            k.decode('utf-8'): float(v.decode('utf-8'))
            for k, v in metrics.items()
        }

    def process_one(self) -> Optional[Dict[str, Any]]:
        """
        Process one item from the queue.

        Dequeues, scores, and completes a single item.

        Returns:
            Result dict or None if queue empty
        """
        request = self.dequeue(timeout_sec=1)
        if not request:
            return None

        start_time = time.time()

        try:
            # Get spider data and score
            from core.models_unified_system import SpiderData
            from core.services.ml_scoring_engine import get_ml_scoring_engine

            spider_data = SpiderData.objects.get(id=request.spider_data_id)
            engine = get_ml_scoring_engine()
            result = engine.score_opportunity(spider_data)

            latency_ms = (time.time() - start_time) * 1000

            if result.success:
                self.complete(
                    request.id,
                    result.hybrid_score,
                    latency_ms=latency_ms
                )
                return {
                    'request_id': request.id,
                    'success': True,
                    'score': result.hybrid_score,
                    'latency_ms': latency_ms
                }
            else:
                self.fail(request.id, result.error or 'Scoring failed')
                return {
                    'request_id': request.id,
                    'success': False,
                    'error': result.error
                }

        except Exception as e:
            self.fail(request.id, str(e))
            return {
                'request_id': request.id,
                'success': False,
                'error': str(e)
            }

    def drain_queue(
        self,
        max_items: int = 100,
        max_time_sec: int = 30
    ) -> Dict[str, Any]:
        """
        Process items until queue empty or limits reached.

        Args:
            max_items: Maximum items to process
            max_time_sec: Maximum seconds to run

        Returns:
            Statistics about processing
        """
        start_time = time.time()
        stats = {
            'processed': 0,
            'success': 0,
            'failed': 0,
            'duration_sec': 0,
            'avg_latency_ms': 0
        }
        total_latency = 0

        while stats['processed'] < max_items:
            # Check time limit
            elapsed = time.time() - start_time
            if elapsed >= max_time_sec:
                break

            result = self.process_one()
            if result is None:
                break  # Queue empty

            stats['processed'] += 1
            if result.get('success'):
                stats['success'] += 1
                total_latency += result.get('latency_ms', 0)
            else:
                stats['failed'] += 1

        stats['duration_sec'] = round(time.time() - start_time, 2)
        if stats['success'] > 0:
            stats['avg_latency_ms'] = round(total_latency / stats['success'], 2)

        logger.info(
            f"⚡ [REALTIME] Drained queue: "
            f"{stats['success']}/{stats['processed']} success in {stats['duration_sec']}s"
        )

        return stats

    def cleanup_stale_processing(self) -> int:
        """
        Clean up requests stuck in processing state.

        Returns:
            Number of items cleaned up
        """
        # Find all processing keys
        processing_keys = self.redis.keys(f"{self.PROCESSING_PREFIX}:*")
        cleaned = 0

        for key in processing_keys:
            ttl = self.redis.ttl(key)
            if ttl <= 0:  # Expired
                data = self.redis.get(key)
                if data:
                    request = QueuedScoringRequest.from_json(data.decode('utf-8'))
                    self.fail(
                        request.id,
                        'Processing timeout',
                        retry=True
                    )
                    cleaned += 1

        if cleaned > 0:
            logger.warning(f"⚡ [REALTIME] Cleaned up {cleaned} stale processing items")

        return cleaned

    def _increment_metric(self, name: str, value: int = 1):
        """Increment a metric in Redis."""
        self.redis.hincrby(self.METRICS_KEY, name, value)

    def _track_latency(self, latency_ms: float):
        """Track latency for SLA monitoring."""
        # Update running average in metrics
        metrics = self.get_metrics()
        current_avg = metrics.get('avg_latency_ms', 0)
        current_count = metrics.get('completed', 1)

        new_avg = ((current_avg * (current_count - 1)) + latency_ms) / current_count
        self.redis.hset(self.METRICS_KEY, 'avg_latency_ms', new_avg)

        # Check SLA
        if latency_ms > self._sla_target_ms:
            self._increment_metric('sla_breaches')
            logger.warning(
                f"⚡ [REALTIME] SLA breach: {latency_ms:.0f}ms > {self._sla_target_ms}ms"
            )


# Singleton instance
_realtime_scorer_instance: Optional[RealtimeScorer] = None


def get_realtime_scorer() -> RealtimeScorer:
    """Get singleton realtime scorer instance."""
    global _realtime_scorer_instance
    if _realtime_scorer_instance is None:
        _realtime_scorer_instance = RealtimeScorer()
    return _realtime_scorer_instance
