"""
Event Bus Service - Redis Streams
Session 470: Market Intelligence Architecture - Phase 4

Centralized event bus using Redis Streams for pub/sub messaging
across the Market Intelligence Platform.
"""

import logging
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
from enum import Enum
import redis
from django.conf import settings

logger = logging.getLogger(__name__)


class EventStream(str, Enum):
    """Available event streams in the Market Intelligence Platform."""
    SPIDER_DATA = "mi:spider_data"           # New spider data collected
    OPPORTUNITY_CREATED = "mi:opportunity_created"  # New opportunity created
    OPPORTUNITY_SCORED = "mi:opportunity_scored"    # Opportunity scored
    VALIDATION_REQUIRED = "mi:validation_required"  # Needs human review
    VALIDATION_DECIDED = "mi:validation_decided"    # Human decision made
    OUTCOME_RECORDED = "mi:outcome_recorded"        # Actual outcome tracked
    MODEL_TRAINED = "mi:model_trained"              # ML model retrained
    SYSTEM_ALERT = "mi:system_alert"                # System alerts


class EventPriority(str, Enum):
    """Event priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Event:
    """Represents an event in the system."""
    event_type: str
    stream: EventStream
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_id: Optional[str] = None
    priority: EventPriority = EventPriority.NORMAL
    source: str = "unknown"
    correlation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for Redis."""
        return {
            'event_type': self.event_type,
            'stream': self.stream.value,
            'data': json.dumps(self.data),
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority.value,
            'source': self.source,
            'correlation_id': self.correlation_id or '',
        }

    @classmethod
    def from_dict(cls, event_id: str, data: Dict[str, Any]) -> 'Event':
        """Create event from Redis stream entry."""
        return cls(
            event_id=event_id,
            event_type=data.get('event_type', 'unknown'),
            stream=EventStream(data.get('stream', 'mi:system_alert')),
            data=json.loads(data.get('data', '{}')),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.utcnow().isoformat())),
            priority=EventPriority(data.get('priority', 'normal')),
            source=data.get('source', 'unknown'),
            correlation_id=data.get('correlation_id') or None,
        )


@dataclass
class ConsumerInfo:
    """Information about an event consumer."""
    name: str
    group: str
    handler: Callable[[Event], None]
    streams: List[EventStream]
    active: bool = True


class EventBus:
    """
    Centralized Event Bus using Redis Streams.

    Session 470: Market Intelligence Architecture - Phase 4

    Features:
    - Publish events to streams
    - Subscribe to streams with consumer groups
    - Event replay for debugging
    - Dead letter queue for failed events
    - Event metrics and monitoring
    """

    STREAM_MAX_LEN = 10000  # Max events per stream
    CONSUMER_BLOCK_MS = 5000  # Block time for consumers
    DEAD_LETTER_STREAM = "mi:dead_letter"

    def __init__(self):
        self.redis_client = self._get_redis_client()
        self.consumers: Dict[str, ConsumerInfo] = {}
        self._ensure_consumer_groups()
        logger.info("📡 Event Bus initialized")

    def _get_redis_client(self) -> redis.Redis:
        """Get Redis client from settings."""
        redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
        return redis.from_url(redis_url, decode_responses=True)

    def _ensure_consumer_groups(self):
        """Ensure consumer groups exist for all streams."""
        default_groups = ['scoring_workers', 'validation_workers', 'analytics_workers']

        for stream in EventStream:
            for group in default_groups:
                try:
                    self.redis_client.xgroup_create(
                        stream.value,
                        group,
                        id='0',
                        mkstream=True
                    )
                    logger.debug(f"Created consumer group {group} for {stream.value}")
                except redis.ResponseError as e:
                    if "BUSYGROUP" not in str(e):
                        logger.warning(f"Error creating group {group}: {e}")

    def publish(
        self,
        stream: EventStream,
        event_type: str,
        data: Dict[str, Any],
        priority: EventPriority = EventPriority.NORMAL,
        source: str = "system",
        correlation_id: Optional[str] = None
    ) -> str:
        """
        Publish an event to a stream.

        Args:
            stream: The event stream to publish to
            event_type: Type of event (e.g., 'spider_crawl_complete')
            data: Event payload
            priority: Event priority level
            source: Source of the event
            correlation_id: Optional ID to correlate related events

        Returns:
            Event ID from Redis
        """
        event = Event(
            event_type=event_type,
            stream=stream,
            data=data,
            priority=priority,
            source=source,
            correlation_id=correlation_id
        )

        try:
            event_id = self.redis_client.xadd(
                stream.value,
                event.to_dict(),
                maxlen=self.STREAM_MAX_LEN,
                approximate=True
            )

            logger.debug(
                f"📡 [EventBus] Published {event_type} to {stream.value} "
                f"(id={event_id}, priority={priority.value})"
            )

            # Update metrics
            self._increment_metric(f"events_published:{stream.value}")

            return event_id

        except Exception as e:
            logger.error(f"📡 [EventBus] Failed to publish event: {e}")
            raise

    def subscribe(
        self,
        consumer_name: str,
        consumer_group: str,
        streams: List[EventStream],
        handler: Callable[[Event], None]
    ) -> str:
        """
        Subscribe to streams with a consumer.

        Args:
            consumer_name: Unique name for this consumer
            consumer_group: Consumer group name
            streams: List of streams to subscribe to
            handler: Callback function to handle events

        Returns:
            Consumer ID
        """
        consumer_id = f"{consumer_group}:{consumer_name}"

        self.consumers[consumer_id] = ConsumerInfo(
            name=consumer_name,
            group=consumer_group,
            handler=handler,
            streams=streams
        )

        logger.info(
            f"📡 [EventBus] Subscribed {consumer_id} to "
            f"{[s.value for s in streams]}"
        )

        return consumer_id

    def unsubscribe(self, consumer_id: str):
        """Unsubscribe a consumer."""
        if consumer_id in self.consumers:
            self.consumers[consumer_id].active = False
            del self.consumers[consumer_id]
            logger.info(f"📡 [EventBus] Unsubscribed {consumer_id}")

    def consume(
        self,
        consumer_group: str,
        consumer_name: str,
        streams: List[EventStream],
        count: int = 10,
        block_ms: int = None
    ) -> List[Event]:
        """
        Consume events from streams.

        Args:
            consumer_group: Consumer group name
            consumer_name: Consumer name within group
            streams: Streams to read from
            count: Max events to read
            block_ms: Block time in milliseconds

        Returns:
            List of events
        """
        block_ms = block_ms or self.CONSUMER_BLOCK_MS
        stream_dict = {s.value: '>' for s in streams}

        try:
            results = self.redis_client.xreadgroup(
                consumer_group,
                consumer_name,
                stream_dict,
                count=count,
                block=block_ms
            )

            events = []
            if results:
                for stream_name, messages in results:
                    for msg_id, msg_data in messages:
                        try:
                            event = Event.from_dict(msg_id, msg_data)
                            events.append(event)
                        except Exception as e:
                            logger.error(f"Error parsing event {msg_id}: {e}")
                            self._move_to_dead_letter(stream_name, msg_id, msg_data, str(e))

            return events

        except Exception as e:
            logger.error(f"📡 [EventBus] Error consuming events: {e}")
            return []

    def acknowledge(
        self,
        stream: EventStream,
        consumer_group: str,
        event_ids: List[str]
    ) -> int:
        """
        Acknowledge processed events.

        Args:
            stream: The stream the events came from
            consumer_group: Consumer group name
            event_ids: List of event IDs to acknowledge

        Returns:
            Number of events acknowledged
        """
        if not event_ids:
            return 0

        try:
            count = self.redis_client.xack(stream.value, consumer_group, *event_ids)
            logger.debug(f"📡 [EventBus] Acknowledged {count} events in {stream.value}")
            return count
        except Exception as e:
            logger.error(f"Error acknowledging events: {e}")
            return 0

    def replay(
        self,
        stream: EventStream,
        start_id: str = '0',
        end_id: str = '+',
        count: int = 100
    ) -> List[Event]:
        """
        Replay events from a stream (for debugging).

        Args:
            stream: Stream to replay from
            start_id: Start event ID (default: beginning)
            end_id: End event ID (default: end)
            count: Max events to return

        Returns:
            List of events
        """
        try:
            results = self.redis_client.xrange(
                stream.value,
                min=start_id,
                max=end_id,
                count=count
            )

            events = []
            for msg_id, msg_data in results:
                try:
                    event = Event.from_dict(msg_id, msg_data)
                    events.append(event)
                except Exception as e:
                    logger.warning(f"Error parsing event {msg_id}: {e}")

            logger.info(f"📡 [EventBus] Replayed {len(events)} events from {stream.value}")
            return events

        except Exception as e:
            logger.error(f"Error replaying events: {e}")
            return []

    def get_pending(
        self,
        stream: EventStream,
        consumer_group: str,
        count: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get pending (unacknowledged) events.

        Args:
            stream: Stream to check
            consumer_group: Consumer group
            count: Max items to return

        Returns:
            List of pending event info
        """
        try:
            pending = self.redis_client.xpending_range(
                stream.value,
                consumer_group,
                min='-',
                max='+',
                count=count
            )

            return [
                {
                    'event_id': p['message_id'],
                    'consumer': p['consumer'],
                    'idle_time_ms': p['time_since_delivered'],
                    'delivery_count': p['times_delivered']
                }
                for p in pending
            ]

        except Exception as e:
            logger.error(f"Error getting pending events: {e}")
            return []

    def claim_stale(
        self,
        stream: EventStream,
        consumer_group: str,
        consumer_name: str,
        min_idle_ms: int = 60000,
        count: int = 10
    ) -> List[Event]:
        """
        Claim stale events from other consumers.

        Args:
            stream: Stream to claim from
            consumer_group: Consumer group
            consumer_name: New consumer to assign events to
            min_idle_ms: Minimum idle time before claiming
            count: Max events to claim

        Returns:
            List of claimed events
        """
        try:
            # Get pending events older than min_idle_ms
            pending = self.get_pending(stream, consumer_group, count)
            stale_ids = [
                p['event_id'] for p in pending
                if p['idle_time_ms'] >= min_idle_ms
            ][:count]

            if not stale_ids:
                return []

            # Claim the events
            claimed = self.redis_client.xclaim(
                stream.value,
                consumer_group,
                consumer_name,
                min_idle_ms,
                stale_ids
            )

            events = []
            for msg_id, msg_data in claimed:
                try:
                    event = Event.from_dict(msg_id, msg_data)
                    events.append(event)
                except Exception as e:
                    logger.warning(f"Error parsing claimed event {msg_id}: {e}")

            if events:
                logger.info(f"📡 [EventBus] Claimed {len(events)} stale events")

            return events

        except Exception as e:
            logger.error(f"Error claiming stale events: {e}")
            return []

    def _move_to_dead_letter(
        self,
        stream: str,
        event_id: str,
        event_data: Dict,
        error: str
    ):
        """Move failed event to dead letter queue."""
        try:
            dead_letter_data = {
                'original_stream': stream,
                'original_id': event_id,
                'error': error,
                'timestamp': datetime.utcnow().isoformat(),
                **event_data
            }

            self.redis_client.xadd(
                self.DEAD_LETTER_STREAM,
                dead_letter_data,
                maxlen=1000
            )

            logger.warning(f"📡 [EventBus] Moved event {event_id} to dead letter queue")

        except Exception as e:
            logger.error(f"Error moving to dead letter: {e}")

    def _increment_metric(self, metric_name: str):
        """Increment a metric counter."""
        try:
            self.redis_client.incr(f"mi:metrics:{metric_name}")
        except Exception:
            pass  # Don't fail on metrics

    def get_stream_info(self, stream: EventStream) -> Dict[str, Any]:
        """Get information about a stream."""
        try:
            info = self.redis_client.xinfo_stream(stream.value)
            groups = self.redis_client.xinfo_groups(stream.value)

            return {
                'stream': stream.value,
                'length': info['length'],
                'first_entry': info.get('first-entry'),
                'last_entry': info.get('last-entry'),
                'groups': [
                    {
                        'name': g['name'],
                        'consumers': g['consumers'],
                        'pending': g['pending'],
                        'last_delivered_id': g['last-delivered-id']
                    }
                    for g in groups
                ]
            }
        except Exception as e:
            logger.error(f"Error getting stream info: {e}")
            return {'stream': stream.value, 'error': str(e)}

    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        stats = {
            'streams': {},
            'total_events': 0,
            'dead_letter_count': 0
        }

        for stream in EventStream:
            try:
                length = self.redis_client.xlen(stream.value)
                stats['streams'][stream.value] = length
                stats['total_events'] += length
            except Exception:
                stats['streams'][stream.value] = 0

        try:
            stats['dead_letter_count'] = self.redis_client.xlen(self.DEAD_LETTER_STREAM)
        except Exception:
            pass

        return stats


# =============================================================================
# Convenience Functions for Publishing Events
# =============================================================================

def publish_spider_data_event(
    spider_name: str,
    spider_data_id: str,
    record_count: int,
    source: str = "spider_network"
) -> str:
    """Publish a spider data collection event."""
    bus = get_event_bus()
    return bus.publish(
        stream=EventStream.SPIDER_DATA,
        event_type="spider_crawl_complete",
        data={
            'spider_name': spider_name,
            'spider_data_id': spider_data_id,
            'record_count': record_count
        },
        source=source
    )


def publish_opportunity_scored_event(
    opportunity_id: Optional[str],
    spider_data_id: Optional[str],
    ml_score: Optional[float],
    rule_score: Optional[float],
    hybrid_score: Optional[float],
    confidence: Optional[float],
    source: str = "scoring_engine"
) -> str:
    """Publish an opportunity scored event."""
    bus = get_event_bus()

    # Determine priority based on confidence
    conf = confidence or 0
    if conf >= 85:
        priority = EventPriority.HIGH
    elif conf < 50:
        priority = EventPriority.LOW
    else:
        priority = EventPriority.NORMAL

    return bus.publish(
        stream=EventStream.OPPORTUNITY_SCORED,
        event_type="opportunity_scored",
        data={
            'opportunity_id': opportunity_id,
            'spider_data_id': spider_data_id,
            'hybrid_score': hybrid_score,
            'ml_score': ml_score,
            'rule_score': rule_score,
            'confidence': confidence
        },
        priority=priority,
        source=source
    )


def publish_validation_required_event(
    validation_request_id: str,
    opportunity_id: str,
    confidence: float,
    priority: int,
    source: str = "hitl_service"
) -> str:
    """Publish a validation required event."""
    bus = get_event_bus()
    return bus.publish(
        stream=EventStream.VALIDATION_REQUIRED,
        event_type="validation_queued",
        data={
            'validation_request_id': validation_request_id,
            'opportunity_id': opportunity_id,
            'confidence': confidence,
            'priority': priority
        },
        priority=EventPriority.HIGH,
        source=source
    )


def publish_validation_decided_event(
    validation_request_id: str,
    opportunity_id: str,
    decision: str,
    decided_by: str,
    override_score: Optional[float] = None,
    source: str = "hitl_service"
) -> str:
    """Publish a validation decision event."""
    bus = get_event_bus()
    return bus.publish(
        stream=EventStream.VALIDATION_DECIDED,
        event_type="validation_decided",
        data={
            'validation_request_id': validation_request_id,
            'opportunity_id': opportunity_id,
            'decision': decision,
            'decided_by': decided_by,
            'override_score': override_score
        },
        source=source
    )


def publish_outcome_recorded_event(
    opportunity_id: str,
    outcome_type: str,
    outcome_value: float,
    actual_revenue: Optional[float] = None,
    source: str = "outcome_tracker"
) -> str:
    """Publish an outcome recorded event."""
    bus = get_event_bus()
    return bus.publish(
        stream=EventStream.OUTCOME_RECORDED,
        event_type="outcome_recorded",
        data={
            'opportunity_id': opportunity_id,
            'outcome_type': outcome_type,
            'outcome_value': outcome_value,
            'actual_revenue': actual_revenue
        },
        source=source
    )


def publish_model_trained_event(
    model_version: str,
    training_samples: int,
    metrics: Dict[str, float],
    source: str = "ml_training"
) -> str:
    """Publish a model trained event."""
    bus = get_event_bus()
    return bus.publish(
        stream=EventStream.MODEL_TRAINED,
        event_type="model_trained",
        data={
            'model_version': model_version,
            'training_samples': training_samples,
            'metrics': metrics
        },
        priority=EventPriority.HIGH,
        source=source
    )


def publish_system_alert_event(
    alert_type: str,
    message: str,
    severity: str = "warning",
    details: Optional[Dict] = None,
    source: str = "system"
) -> str:
    """Publish a system alert event."""
    bus = get_event_bus()

    priority = {
        'info': EventPriority.LOW,
        'warning': EventPriority.NORMAL,
        'error': EventPriority.HIGH,
        'critical': EventPriority.CRITICAL
    }.get(severity, EventPriority.NORMAL)

    return bus.publish(
        stream=EventStream.SYSTEM_ALERT,
        event_type=f"alert_{alert_type}",
        data={
            'message': message,
            'severity': severity,
            'details': details or {}
        },
        priority=priority,
        source=source
    )


# =============================================================================
# Singleton Instance
# =============================================================================

_event_bus_instance: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get singleton event bus instance."""
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus()
    return _event_bus_instance
