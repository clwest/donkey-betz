"""
Event Handlers - Consumer Handlers for Event Bus
Session 470: Market Intelligence Architecture - Phase 4

Handles processing of events from the Event Bus Redis Streams.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from core.services.event_bus import (
    Event, EventStream, get_event_bus
)

logger = logging.getLogger(__name__)


@dataclass
class HandlerResult:
    """Result of handling an event."""
    success: bool
    event_id: str
    handler: str
    message: Optional[str] = None
    error: Optional[str] = None
    processing_time_ms: float = 0.0


class EventHandlerRegistry:
    """
    Registry for event handlers.

    Maps event types to their handlers for automatic dispatch.
    """

    def __init__(self):
        self.handlers: Dict[str, List[callable]] = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default handlers for common events."""
        # Spider data handlers
        self.register('spider_crawl_complete', handle_spider_data_event)

        # Scoring handlers
        self.register('opportunity_scored', handle_opportunity_scored_event)

        # Validation handlers
        self.register('validation_queued', handle_validation_queued_event)
        self.register('validation_decided', handle_validation_decided_event)

        # Outcome handlers
        self.register('outcome_recorded', handle_outcome_recorded_event)

        # Model handlers
        self.register('model_trained', handle_model_trained_event)

        # Alert handlers
        self.register('alert_error', handle_system_alert_event)
        self.register('alert_critical', handle_system_alert_event)

    def register(self, event_type: str, handler: callable):
        """Register a handler for an event type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        logger.debug(f"Registered handler {handler.__name__} for {event_type}")

    def unregister(self, event_type: str, handler: callable):
        """Unregister a handler."""
        if event_type in self.handlers:
            self.handlers[event_type] = [
                h for h in self.handlers[event_type]
                if h != handler
            ]

    def get_handlers(self, event_type: str) -> List[callable]:
        """Get handlers for an event type."""
        return self.handlers.get(event_type, [])

    def dispatch(self, event: Event) -> List[HandlerResult]:
        """Dispatch an event to its handlers."""
        handlers = self.get_handlers(event.event_type)

        if not handlers:
            logger.debug(f"No handlers for event type: {event.event_type}")
            return []

        results = []
        for handler in handlers:
            start_time = datetime.utcnow()
            try:
                handler(event)
                processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

                results.append(HandlerResult(
                    success=True,
                    event_id=event.event_id,
                    handler=handler.__name__,
                    processing_time_ms=processing_time
                ))

            except Exception as e:
                processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                logger.error(f"Handler {handler.__name__} failed for {event.event_id}: {e}")

                results.append(HandlerResult(
                    success=False,
                    event_id=event.event_id,
                    handler=handler.__name__,
                    error=str(e),
                    processing_time_ms=processing_time
                ))

        return results


# =============================================================================
# Default Event Handlers
# =============================================================================


def handle_spider_data_event(event: Event):
    """
    Handle spider data collection events.

    Triggers:
    - Opportunity creation from spider data
    - Scoring of new opportunities
    """
    logger.info(f"📡 [Handler] Processing spider data event: {event.event_id}")

    data = event.data
    spider_name = data.get('spider_name')
    spider_data_id = data.get('spider_data_id')
    record_count = data.get('record_count', 0)

    if not spider_data_id:
        logger.warning("Spider data event missing spider_data_id")
        return

    logger.info(
        f"📡 [Handler] Spider '{spider_name}' collected {record_count} records "
        f"(data_id={spider_data_id})"
    )

    # Trigger opportunity creation and scoring
    # This would typically queue a Celery task
    try:
        from core.tasks import score_spider_data_async

        # Queue scoring for the new spider data
        score_spider_data_async.delay(spider_data_id)
        logger.debug(f"Queued scoring for spider data {spider_data_id}")

    except ImportError:
        logger.debug("score_spider_data_async task not available")
    except Exception as e:
        logger.error(f"Error queuing scoring task: {e}")


def handle_opportunity_scored_event(event: Event):
    """
    Handle opportunity scored events.

    Triggers:
    - HITL validation routing based on confidence
    - Analytics updates
    """
    logger.info(f"📡 [Handler] Processing opportunity scored event: {event.event_id}")

    data = event.data
    opportunity_id = data.get('opportunity_id')
    confidence = data.get('confidence', 0)
    hybrid_score = data.get('hybrid_score', 0)

    logger.info(
        f"📡 [Handler] Opportunity {opportunity_id} scored: "
        f"score={hybrid_score:.1f}, confidence={confidence:.1f}%"
    )

    # Check if HITL validation is needed (50-85% confidence)
    if 50 <= confidence < 85:
        logger.info(f"📡 [Handler] Opportunity {opportunity_id} needs human validation")
        # The HITL service will have already created the validation request
        # This handler is for analytics and notifications


def handle_validation_queued_event(event: Event):
    """
    Handle validation queued events.

    Triggers:
    - Notifications to reviewers
    - Dashboard updates
    """
    logger.info(f"📡 [Handler] Processing validation queued event: {event.event_id}")

    data = event.data
    validation_request_id = data.get('validation_request_id')
    opportunity_id = data.get('opportunity_id')
    confidence = data.get('confidence', 0)
    priority = data.get('priority', 3)

    logger.info(
        f"📡 [Handler] Validation queued: request={validation_request_id}, "
        f"opportunity={opportunity_id}, confidence={confidence:.1f}%, priority={priority}"
    )

    # Could trigger notifications here
    # For example, Discord notification for high-priority items
    if priority <= 2:  # High priority
        try:
            from core.services.discord_notifications import send_to_channel
            send_to_channel(
                channel_name='system-status',
                message=f"High priority validation needed for opportunity (confidence: {confidence:.1f}%)"
            )
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"Could not send Discord notification: {e}")


def handle_validation_decided_event(event: Event):
    """
    Handle validation decision events.

    Triggers:
    - ML feedback loop updates
    - Analytics tracking
    """
    logger.info(f"📡 [Handler] Processing validation decided event: {event.event_id}")

    data = event.data
    validation_request_id = data.get('validation_request_id')
    opportunity_id = data.get('opportunity_id')
    decision = data.get('decision')
    decided_by = data.get('decided_by')
    override_score = data.get('override_score')

    logger.info(
        f"📡 [Handler] Validation decided: request={validation_request_id}, "
        f"decision={decision}, by={decided_by}"
    )

    # If there was a score override, this is valuable training signal
    if override_score is not None:
        logger.info(
            f"📡 [Handler] Score override detected: {override_score} - "
            f"valuable training signal for ML model"
        )


def handle_outcome_recorded_event(event: Event):
    """
    Handle outcome recorded events.

    Triggers:
    - ML training data updates
    - ROI calculations
    - Performance tracking
    """
    logger.info(f"📡 [Handler] Processing outcome recorded event: {event.event_id}")

    data = event.data
    opportunity_id = data.get('opportunity_id')
    outcome_type = data.get('outcome_type')
    outcome_value = data.get('outcome_value')
    actual_revenue = data.get('actual_revenue')

    logger.info(
        f"📡 [Handler] Outcome recorded: opportunity={opportunity_id}, "
        f"type={outcome_type}, value={outcome_value}, revenue={actual_revenue}"
    )

    # This is critical training data for the ML model
    # Check if we have enough outcomes to trigger retraining
    try:
        from core.models_unified_system import OpportunityOutcome
        outcome_count = OpportunityOutcome.objects.filter(
            actual_outcome__isnull=False
        ).count()

        if outcome_count >= 100 and outcome_count % 50 == 0:
            # Every 50 outcomes after 100, consider retraining
            logger.info(
                f"📡 [Handler] {outcome_count} outcomes recorded - "
                f"consider triggering ML model retraining"
            )
    except Exception as e:
        logger.warning(f"Could not check outcome count: {e}")


def handle_model_trained_event(event: Event):
    """
    Handle model trained events.

    Triggers:
    - System notifications
    - Performance comparison
    """
    logger.info(f"📡 [Handler] Processing model trained event: {event.event_id}")

    data = event.data
    model_version = data.get('model_version')
    training_samples = data.get('training_samples')
    metrics = data.get('metrics', {})

    logger.info(
        f"📡 [Handler] ML model trained: version={model_version}, "
        f"samples={training_samples}, metrics={metrics}"
    )

    # Notify about new model
    try:
        from core.services.discord_notifications import send_to_channel
        send_to_channel(
            channel_name='system-status',
            message=f"ML Scoring Model v{model_version} trained on {training_samples} samples. "
                    f"Test R2: {metrics.get('test_r2', 'N/A')}"
        )
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"Could not send Discord notification: {e}")


def handle_system_alert_event(event: Event):
    """
    Handle system alert events.

    Triggers:
    - Notifications based on severity
    - Incident logging
    """
    logger.info(f"📡 [Handler] Processing system alert event: {event.event_id}")

    data = event.data
    message = data.get('message')
    severity = data.get('severity', 'warning')
    details = data.get('details', {})

    if severity == 'critical':
        logger.critical(f"📡 [ALERT] CRITICAL: {message}")
    elif severity == 'error':
        logger.error(f"📡 [ALERT] ERROR: {message}")
    else:
        logger.warning(f"📡 [ALERT] {severity.upper()}: {message}")

    # Send notification for errors and critical
    if severity in ('error', 'critical'):
        try:
            from core.services.discord_notifications import send_to_channel
            send_to_channel(
                channel_name='system-status',
                message=f"[{severity.upper()}] {message}"
            )
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"Could not send Discord notification: {e}")


# =============================================================================
# Event Consumer Workers
# =============================================================================


class EventConsumerWorker:
    """
    Worker that consumes and processes events from streams.

    Can be run as a Celery task or standalone process.
    """

    def __init__(
        self,
        consumer_group: str,
        consumer_name: str,
        streams: List[EventStream],
        batch_size: int = 10,
        block_ms: int = 5000
    ):
        self.consumer_group = consumer_group
        self.consumer_name = consumer_name
        self.streams = streams
        self.batch_size = batch_size
        self.block_ms = block_ms
        self.event_bus = get_event_bus()
        self.handler_registry = EventHandlerRegistry()
        self.running = False

    def process_batch(self) -> Dict[str, Any]:
        """
        Process a batch of events.

        Returns:
            Dict with processing results
        """
        results = {
            'events_processed': 0,
            'events_succeeded': 0,
            'events_failed': 0,
            'errors': []
        }

        # Consume events
        events = self.event_bus.consume(
            consumer_group=self.consumer_group,
            consumer_name=self.consumer_name,
            streams=self.streams,
            count=self.batch_size,
            block_ms=self.block_ms
        )

        if not events:
            return results

        # Process each event
        for event in events:
            results['events_processed'] += 1

            handler_results = self.handler_registry.dispatch(event)

            if handler_results:
                all_succeeded = all(r.success for r in handler_results)
                if all_succeeded:
                    results['events_succeeded'] += 1
                    # Acknowledge the event
                    self.event_bus.acknowledge(
                        event.stream,
                        self.consumer_group,
                        [event.event_id]
                    )
                else:
                    results['events_failed'] += 1
                    for r in handler_results:
                        if not r.success:
                            results['errors'].append({
                                'event_id': event.event_id,
                                'handler': r.handler,
                                'error': r.error
                            })
            else:
                # No handlers, still acknowledge
                results['events_succeeded'] += 1
                self.event_bus.acknowledge(
                    event.stream,
                    self.consumer_group,
                    [event.event_id]
                )

        return results

    def claim_stale_events(self, min_idle_ms: int = 60000) -> int:
        """Claim and process stale events from other consumers."""
        total_claimed = 0

        for stream in self.streams:
            events = self.event_bus.claim_stale(
                stream=stream,
                consumer_group=self.consumer_group,
                consumer_name=self.consumer_name,
                min_idle_ms=min_idle_ms,
                count=self.batch_size
            )

            for event in events:
                handler_results = self.handler_registry.dispatch(event)

                if handler_results:
                    all_succeeded = all(r.success for r in handler_results)
                    if all_succeeded:
                        self.event_bus.acknowledge(
                            event.stream,
                            self.consumer_group,
                            [event.event_id]
                        )
                        total_claimed += 1

        return total_claimed


# =============================================================================
# Singleton Instances
# =============================================================================

_handler_registry_instance: Optional[EventHandlerRegistry] = None


def get_handler_registry() -> EventHandlerRegistry:
    """Get singleton handler registry instance."""
    global _handler_registry_instance
    if _handler_registry_instance is None:
        _handler_registry_instance = EventHandlerRegistry()
    return _handler_registry_instance


def create_scoring_worker(consumer_name: str = "scoring_worker_1") -> EventConsumerWorker:
    """Create a worker for scoring events."""
    return EventConsumerWorker(
        consumer_group="scoring_workers",
        consumer_name=consumer_name,
        streams=[EventStream.SPIDER_DATA, EventStream.OPPORTUNITY_CREATED],
        block_ms=0,  # Session 1075: non-blocking — Celery Beat handles scheduling
    )


def create_validation_worker(consumer_name: str = "validation_worker_1") -> EventConsumerWorker:
    """Create a worker for validation events."""
    return EventConsumerWorker(
        consumer_group="validation_workers",
        consumer_name=consumer_name,
        streams=[EventStream.OPPORTUNITY_SCORED, EventStream.VALIDATION_REQUIRED],
        block_ms=0,  # Session 1075: non-blocking — Celery Beat handles scheduling
    )


def create_analytics_worker(consumer_name: str = "analytics_worker_1") -> EventConsumerWorker:
    """Create a worker for analytics events."""
    return EventConsumerWorker(
        consumer_group="analytics_workers",
        consumer_name=consumer_name,
        streams=[
            EventStream.VALIDATION_DECIDED,
            EventStream.OUTCOME_RECORDED,
            EventStream.MODEL_TRAINED
        ],
        block_ms=0,  # Session 1075: non-blocking — Celery Beat handles scheduling
    )
