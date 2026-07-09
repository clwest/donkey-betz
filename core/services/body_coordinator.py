"""
Session 711: Body Coordinator Service

Central coordination service that makes body systems communicate with each other.
Monitors all body systems, detects when intervention is needed, and coordinates
responses across the entire body.

Human Body Metaphor:
- This is the AUTONOMIC NERVOUS SYSTEM - automatic responses without conscious thought
- Like how your body automatically adjusts heart rate, breathing, digestion
- Detects issues and triggers coordinated responses
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Singleton instance
_coordinator_instance: Optional['BodyCoordinator'] = None


def get_body_coordinator() -> 'BodyCoordinator':
    """Get the singleton BodyCoordinator instance."""
    global _coordinator_instance
    if _coordinator_instance is None:
        _coordinator_instance = BodyCoordinator()
    return _coordinator_instance


class CoordinationEventType(Enum):
    """Types of coordination events that can trigger responses."""
    # LUNGS events
    LUNGS_EXHAUSTED = 'lungs_exhausted'          # Budget < 10%
    LUNGS_LOW = 'lungs_low'                      # Budget < 20%
    LUNGS_RECOVERED = 'lungs_recovered'          # Budget > 50%

    # HEART events
    HEART_CRITICAL = 'heart_critical'            # Core component down
    HEART_DEGRADED = 'heart_degraded'            # Component unhealthy
    HEART_RECOVERED = 'heart_recovered'          # All components healthy

    # IMMUNE events
    IMMUNE_THREAT_HIGH = 'immune_threat_high'    # High threat level
    IMMUNE_THREAT_SEVERE = 'immune_threat_severe' # Severe threat level
    IMMUNE_CLEAR = 'immune_clear'                # Threats resolved

    # DIGESTIVE events
    DIGESTIVE_BLOCKED = 'digestive_blocked'      # Pipeline blocked
    DIGESTIVE_BLOATED = 'digestive_bloated'      # Queue backlog
    DIGESTIVE_HEALTHY = 'digestive_healthy'      # Pipeline flowing

    # MUSCULAR events
    MUSCULAR_PARALYZED = 'muscular_paralyzed'    # No agent activity
    MUSCULAR_STRAINED = 'muscular_strained'      # High failure rate
    MUSCULAR_RECOVERED = 'muscular_recovered'    # Agents performing well

    # CIRCULATORY events
    CIRCULATORY_BLOCKED = 'circulatory_blocked'  # Data flow blocked
    CIRCULATORY_SLOW = 'circulatory_slow'        # Data flow slow
    CIRCULATORY_FLOWING = 'circulatory_flowing'  # Normal flow

    # SPINE events
    SPINE_INJURED = 'spine_injured'              # Routing failures
    SPINE_STRAINED = 'spine_strained'            # High latency
    SPINE_ALIGNED = 'spine_aligned'              # Normal routing

    # BRAIN events (Session 725)
    BRAIN_OVERLOADED = 'brain_overloaded'        # Too many inferences
    BRAIN_CONFUSED = 'brain_confused'            # Model errors
    BRAIN_FOCUSED = 'brain_focused'              # Operating normally

    # SKIN events (Session 725)
    SKIN_IRRITATED = 'skin_irritated'            # Write failures
    SKIN_DAMAGED = 'skin_damaged'                # Critical workspace issues
    SKIN_HEALTHY = 'skin_healthy'                # Normal operations

    # NERVOUS events (Session 725)
    NERVOUS_DAMAGED = 'nervous_damaged'          # WebSocket infrastructure down
    NERVOUS_OVERLOADED = 'nervous_overloaded'    # Too many connections
    NERVOUS_RESPONSIVE = 'nervous_responsive'    # Normal operations


@dataclass
class CoordinationEvent:
    """An event that requires coordination."""
    event_type: CoordinationEventType
    source_system: str
    severity: str  # 'info', 'warning', 'critical'
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=timezone.now)


@dataclass
class CoordinationResponse:
    """Record of a coordination response."""
    event: CoordinationEvent
    actions_taken: List[str]
    success: bool
    response_time_ms: int
    timestamp: datetime = field(default_factory=timezone.now)


class BodyCoordinator:
    """
    Coordinates responses across body systems.

    The autonomic nervous system of the AI body - monitors all systems
    and triggers automatic responses when issues are detected.
    """

    # Cache keys
    THROTTLE_CACHE_KEY = 'body_coordinator:throttle_mode'
    LAST_CHECK_CACHE_KEY = 'body_coordinator:last_check'
    RESPONSE_LOG_CACHE_KEY = 'body_coordinator:responses'

    # Thresholds
    LUNGS_EXHAUSTED_THRESHOLD = 10.0    # %
    LUNGS_LOW_THRESHOLD = 20.0          # %
    LUNGS_RECOVERED_THRESHOLD = 50.0    # %
    DIGESTIVE_BLOATED_THRESHOLD = 1000  # items in queue
    MUSCULAR_STRAINED_THRESHOLD = 70.0  # % success rate

    def __init__(self):
        self.handlers: Dict[CoordinationEventType, Callable] = {
            # LUNGS handlers
            CoordinationEventType.LUNGS_EXHAUSTED: self._handle_lungs_exhausted,
            CoordinationEventType.LUNGS_LOW: self._handle_lungs_low,
            CoordinationEventType.LUNGS_RECOVERED: self._handle_lungs_recovered,

            # HEART handlers
            CoordinationEventType.HEART_CRITICAL: self._handle_heart_critical,
            CoordinationEventType.HEART_DEGRADED: self._handle_heart_degraded,
            CoordinationEventType.HEART_RECOVERED: self._handle_heart_recovered,

            # IMMUNE handlers
            CoordinationEventType.IMMUNE_THREAT_HIGH: self._handle_immune_threat,
            CoordinationEventType.IMMUNE_THREAT_SEVERE: self._handle_immune_threat,
            CoordinationEventType.IMMUNE_CLEAR: self._handle_immune_clear,

            # DIGESTIVE handlers
            CoordinationEventType.DIGESTIVE_BLOCKED: self._handle_digestive_blocked,
            CoordinationEventType.DIGESTIVE_BLOATED: self._handle_digestive_bloated,
            CoordinationEventType.DIGESTIVE_HEALTHY: self._handle_digestive_healthy,

            # MUSCULAR handlers
            CoordinationEventType.MUSCULAR_PARALYZED: self._handle_muscular_issue,
            CoordinationEventType.MUSCULAR_STRAINED: self._handle_muscular_issue,
            CoordinationEventType.MUSCULAR_RECOVERED: self._handle_muscular_recovered,

            # CIRCULATORY handlers
            CoordinationEventType.CIRCULATORY_BLOCKED: self._handle_circulatory_issue,
            CoordinationEventType.CIRCULATORY_SLOW: self._handle_circulatory_issue,
            CoordinationEventType.CIRCULATORY_FLOWING: self._handle_circulatory_recovered,

            # SPINE handlers
            CoordinationEventType.SPINE_INJURED: self._handle_spine_issue,
            CoordinationEventType.SPINE_STRAINED: self._handle_spine_issue,
            CoordinationEventType.SPINE_ALIGNED: self._handle_spine_recovered,

            # BRAIN handlers (Session 725)
            CoordinationEventType.BRAIN_OVERLOADED: self._handle_brain_issue,
            CoordinationEventType.BRAIN_CONFUSED: self._handle_brain_issue,
            CoordinationEventType.BRAIN_FOCUSED: self._handle_brain_recovered,

            # SKIN handlers (Session 725)
            CoordinationEventType.SKIN_IRRITATED: self._handle_skin_issue,
            CoordinationEventType.SKIN_DAMAGED: self._handle_skin_issue,
            CoordinationEventType.SKIN_HEALTHY: self._handle_skin_recovered,

            # NERVOUS handlers (Session 725)
            CoordinationEventType.NERVOUS_DAMAGED: self._handle_nervous_issue,
            CoordinationEventType.NERVOUS_OVERLOADED: self._handle_nervous_issue,
            CoordinationEventType.NERVOUS_RESPONSIVE: self._handle_nervous_recovered,
        }

        self._response_log: List[CoordinationResponse] = []
        logger.info("🧠 BodyCoordinator initialized - Autonomic Nervous System active")

    # =========================================================================
    # Main Coordination Loop
    # =========================================================================

    def coordinate(self, force: bool = False) -> Dict[str, Any]:
        """
        Run the main coordination loop.

        Checks all body systems, detects events, and triggers responses.
        This is the "heartbeat" of the autonomic nervous system.

        Args:
            force: Force check even if recently checked

        Returns:
            Coordination report with events detected and actions taken
        """
        start = timezone.now()

        # Check if we recently coordinated (avoid over-checking)
        last_check = cache.get(self.LAST_CHECK_CACHE_KEY)
        if not force and last_check:
            last_check_time = datetime.fromisoformat(last_check)
            if (timezone.now() - last_check_time).total_seconds() < 30:
                return {
                    'skipped': True,
                    'reason': 'Recently checked',
                    'last_check': last_check
                }

        events_detected: List[CoordinationEvent] = []
        responses: List[CoordinationResponse] = []

        # Detect events from each body system
        try:
            events_detected.extend(self._detect_lungs_events())
        except Exception as e:
            logger.error(f"Error detecting LUNGS events: {e}")

        try:
            events_detected.extend(self._detect_heart_events())
        except Exception as e:
            logger.error(f"Error detecting HEART events: {e}")

        try:
            events_detected.extend(self._detect_immune_events())
        except Exception as e:
            logger.error(f"Error detecting IMMUNE events: {e}")

        try:
            events_detected.extend(self._detect_digestive_events())
        except Exception as e:
            logger.error(f"Error detecting DIGESTIVE events: {e}")

        try:
            events_detected.extend(self._detect_muscular_events())
        except Exception as e:
            logger.error(f"Error detecting MUSCULAR events: {e}")

        try:
            events_detected.extend(self._detect_circulatory_events())
        except Exception as e:
            logger.error(f"Error detecting CIRCULATORY events: {e}")

        try:
            events_detected.extend(self._detect_spine_events())
        except Exception as e:
            logger.error(f"Error detecting SPINE events: {e}")

        # Session 725: Added BRAIN, SKIN, NERVOUS detection
        try:
            events_detected.extend(self._detect_brain_events())
        except Exception as e:
            logger.error(f"Error detecting BRAIN events: {e}")

        try:
            events_detected.extend(self._detect_skin_events())
        except Exception as e:
            logger.error(f"Error detecting SKIN events: {e}")

        try:
            events_detected.extend(self._detect_nervous_events())
        except Exception as e:
            logger.error(f"Error detecting NERVOUS events: {e}")

        # Handle each detected event
        for event in events_detected:
            response = self._handle_event(event)
            if response:
                responses.append(response)

        # Update last check time
        cache.set(self.LAST_CHECK_CACHE_KEY, timezone.now().isoformat(), timeout=3600)

        # Store response log
        self._response_log.extend(responses)
        # Keep only last 100 responses in memory
        self._response_log = self._response_log[-100:]

        duration_ms = int((timezone.now() - start).total_seconds() * 1000)

        return {
            'success': True,
            'timestamp': timezone.now().isoformat(),
            'duration_ms': duration_ms,
            'events_detected': len(events_detected),
            'responses_triggered': len(responses),
            'is_throttled': self.is_throttled(),
            'events': [
                {
                    'type': e.event_type.value,
                    'source': e.source_system,
                    'severity': e.severity,
                    'message': e.message
                }
                for e in events_detected
            ],
            'responses': [
                {
                    'event_type': r.event.event_type.value,
                    'actions': r.actions_taken,
                    'success': r.success
                }
                for r in responses
            ]
        }

    def _handle_event(self, event: CoordinationEvent) -> Optional[CoordinationResponse]:
        """Handle a single coordination event."""
        start = timezone.now()

        handler = self.handlers.get(event.event_type)
        if not handler:
            logger.warning(f"No handler for event type: {event.event_type}")
            return None

        try:
            actions = handler(event)
            duration_ms = int((timezone.now() - start).total_seconds() * 1000)

            response = CoordinationResponse(
                event=event,
                actions_taken=actions,
                success=True,
                response_time_ms=duration_ms
            )

            logger.info(
                f"🧠 Coordination: {event.event_type.value} -> {len(actions)} actions "
                f"({duration_ms}ms)"
            )
            return response

        except Exception as e:
            logger.error(f"Error handling event {event.event_type}: {e}")
            return CoordinationResponse(
                event=event,
                actions_taken=[f"ERROR: {str(e)}"],
                success=False,
                response_time_ms=int((timezone.now() - start).total_seconds() * 1000)
            )

    # =========================================================================
    # Event Detection Methods
    # =========================================================================

    def _detect_lungs_events(self) -> List[CoordinationEvent]:
        """Detect LUNGS (budget) related events."""
        events = []
        try:
            from core.services.lungs import get_lungs_monitor
            lungs = get_lungs_monitor()
            vitals = lungs.get_vitals()

            oxygen_level = vitals.get('oxygen_level', 100)

            if oxygen_level <= self.LUNGS_EXHAUSTED_THRESHOLD:
                events.append(CoordinationEvent(
                    event_type=CoordinationEventType.LUNGS_EXHAUSTED,
                    source_system='lungs',
                    severity='critical',
                    message=f'Budget exhausted: {oxygen_level:.1f}% remaining',
                    data={'oxygen_level': oxygen_level}
                ))
            elif oxygen_level <= self.LUNGS_LOW_THRESHOLD:
                events.append(CoordinationEvent(
                    event_type=CoordinationEventType.LUNGS_LOW,
                    source_system='lungs',
                    severity='warning',
                    message=f'Budget low: {oxygen_level:.1f}% remaining',
                    data={'oxygen_level': oxygen_level}
                ))
            elif oxygen_level >= self.LUNGS_RECOVERED_THRESHOLD and self.is_throttled():
                events.append(CoordinationEvent(
                    event_type=CoordinationEventType.LUNGS_RECOVERED,
                    source_system='lungs',
                    severity='info',
                    message=f'Budget recovered: {oxygen_level:.1f}%',
                    data={'oxygen_level': oxygen_level}
                ))

        except Exception as e:
            logger.error(f"Error detecting LUNGS events: {e}")

        return events

    def _detect_heart_events(self) -> List[CoordinationEvent]:
        """Detect HEART (core platform health) events."""
        events = []
        try:
            from core.services.heart import get_heart_monitor
            heart = get_heart_monitor()
            vitals = heart.get_vitals()

            status = vitals.get('overall_status', 'unknown')
            health_score = vitals.get('health_score', 0)

            if status in ['critical', 'offline', 'flat']:
                events.append(CoordinationEvent(
                    event_type=CoordinationEventType.HEART_CRITICAL,
                    source_system='heart',
                    severity='critical',
                    message=f'Core platform critical: {status}',
                    data={'status': status, 'health_score': health_score}
                ))
            elif status in ['degraded', 'irregular']:
                events.append(CoordinationEvent(
                    event_type=CoordinationEventType.HEART_DEGRADED,
                    source_system='heart',
                    severity='warning',
                    message=f'Core platform degraded: {status}',
                    data={'status': status, 'health_score': health_score}
                ))

        except Exception as e:
            logger.error(f"Error detecting HEART events: {e}")

        return events

    def _detect_immune_events(self) -> List[CoordinationEvent]:
        """Detect IMMUNE (security) events."""
        events = []
        try:
            from core.services.immune import get_immune_system
            immune = get_immune_system()
            status = immune.get_status()

            threat_level = status.get('overall_status', 'healthy')

            if threat_level in ['severe', 'overwhelmed', 'compromised']:
                events.append(CoordinationEvent(
                    event_type=CoordinationEventType.IMMUNE_THREAT_SEVERE,
                    source_system='immune',
                    severity='critical',
                    message=f'Security threat: {threat_level}',
                    data={'threat_level': threat_level, 'threats': status.get('threats_detected_24h', 0)}
                ))
            elif threat_level in ['high', 'alert', 'fighting']:
                events.append(CoordinationEvent(
                    event_type=CoordinationEventType.IMMUNE_THREAT_HIGH,
                    source_system='immune',
                    severity='warning',
                    message=f'Elevated security threat: {threat_level}',
                    data={'threat_level': threat_level}
                ))

        except Exception as e:
            logger.error(f"Error detecting IMMUNE events: {e}")

        return events

    def _detect_digestive_events(self) -> List[CoordinationEvent]:
        """Detect DIGESTIVE (data pipeline) events."""
        events = []
        try:
            from core.services.digestive import get_digestive_system
            digestive = get_digestive_system()
            status = digestive.get_status()

            overall_status = status.get('overall_status', 'healthy')
            items_pending = status.get('items_pending', 0)

            if overall_status in ['blocked', 'starving']:
                events.append(CoordinationEvent(
                    event_type=CoordinationEventType.DIGESTIVE_BLOCKED,
                    source_system='digestive',
                    severity='critical',
                    message=f'Data pipeline {overall_status}',
                    data={'status': overall_status, 'items_pending': items_pending}
                ))
            elif overall_status == 'bloated' or items_pending > self.DIGESTIVE_BLOATED_THRESHOLD:
                events.append(CoordinationEvent(
                    event_type=CoordinationEventType.DIGESTIVE_BLOATED,
                    source_system='digestive',
                    severity='warning',
                    message=f'Data pipeline backlog: {items_pending} items',
                    data={'status': overall_status, 'items_pending': items_pending}
                ))

        except Exception as e:
            logger.error(f"Error detecting DIGESTIVE events: {e}")

        return events

    def _detect_muscular_events(self) -> List[CoordinationEvent]:
        """Detect MUSCULAR (agent execution) events."""
        events = []
        try:
            from core.services.muscular import get_muscular_system
            muscular = get_muscular_system()
            status = muscular.get_status()

            overall_status = status.get('overall_status', 'fit')
            success_rate = status.get('success_rate_24h', 100)

            if overall_status == 'paralyzed':
                events.append(CoordinationEvent(
                    event_type=CoordinationEventType.MUSCULAR_PARALYZED,
                    source_system='muscular',
                    severity='critical',
                    message='Agent execution paralyzed',
                    data={'status': overall_status, 'success_rate': success_rate}
                ))
            elif overall_status == 'strained' or success_rate < self.MUSCULAR_STRAINED_THRESHOLD:
                events.append(CoordinationEvent(
                    event_type=CoordinationEventType.MUSCULAR_STRAINED,
                    source_system='muscular',
                    severity='warning',
                    message=f'Agent execution strained: {success_rate:.1f}% success',
                    data={'status': overall_status, 'success_rate': success_rate}
                ))

        except Exception as e:
            logger.error(f"Error detecting MUSCULAR events: {e}")

        return events

    def _detect_circulatory_events(self) -> List[CoordinationEvent]:
        """Detect CIRCULATORY (data flow) events."""
        events = []
        try:
            from core.services.circulatory import get_circulatory_system
            circulatory = get_circulatory_system()
            status = circulatory.get_status()

            overall_status = status.get('overall_status', 'flowing')

            if overall_status == 'blocked':
                events.append(CoordinationEvent(
                    event_type=CoordinationEventType.CIRCULATORY_BLOCKED,
                    source_system='circulatory',
                    severity='critical',
                    message='Data flow blocked',
                    data={'status': overall_status}
                ))
            elif overall_status in ['slow', 'congested']:
                events.append(CoordinationEvent(
                    event_type=CoordinationEventType.CIRCULATORY_SLOW,
                    source_system='circulatory',
                    severity='warning',
                    message=f'Data flow {overall_status}',
                    data={'status': overall_status}
                ))

        except Exception as e:
            logger.error(f"Error detecting CIRCULATORY events: {e}")

        return events

    def _detect_spine_events(self) -> List[CoordinationEvent]:
        """Detect SPINE (API routing) events."""
        events = []
        try:
            from core.services.spine import get_spine_router
            spine = get_spine_router()
            status = spine.get_status()

            overall_status = status.get('overall_status', 'aligned')

            if overall_status == 'injured':
                events.append(CoordinationEvent(
                    event_type=CoordinationEventType.SPINE_INJURED,
                    source_system='spine',
                    severity='critical',
                    message='API routing injured',
                    data={'status': overall_status}
                ))
            elif overall_status in ['strained', 'compressed']:
                events.append(CoordinationEvent(
                    event_type=CoordinationEventType.SPINE_STRAINED,
                    source_system='spine',
                    severity='warning',
                    message=f'API routing {overall_status}',
                    data={'status': overall_status}
                ))

        except Exception as e:
            logger.error(f"Error detecting SPINE events: {e}")

        return events

    # Session 725: BRAIN, SKIN, NERVOUS detection methods

    def _detect_brain_events(self) -> List[CoordinationEvent]:
        """Detect BRAIN (cognitive/ML processing) events."""
        events = []
        try:
            from core.services.brain import get_brain_service
            brain = get_brain_service()
            vitals = brain.get_vitals()

            status = vitals.get('status', 'unknown')
            health_score = vitals.get('health_score', 100)

            if status == 'overloaded' or health_score < 30:
                events.append(CoordinationEvent(
                    event_type=CoordinationEventType.BRAIN_OVERLOADED,
                    source_system='brain',
                    severity='critical',
                    message=f'Cognitive processing overloaded: {health_score:.0f}% health',
                    data={'status': status, 'health_score': health_score}
                ))
            elif status in ['confused', 'error'] or health_score < 50:
                events.append(CoordinationEvent(
                    event_type=CoordinationEventType.BRAIN_CONFUSED,
                    source_system='brain',
                    severity='warning',
                    message=f'Cognitive processing issues: {status}',
                    data={'status': status, 'health_score': health_score}
                ))

        except Exception as e:
            logger.error(f"Error detecting BRAIN events: {e}")

        return events

    def _detect_skin_events(self) -> List[CoordinationEvent]:
        """Detect SKIN (workspace output) events."""
        events = []
        try:
            from core.services.skin import get_skin_service
            skin = get_skin_service()
            vitals = skin.get_vitals()

            status = vitals.get('status', 'unknown')
            health_score = vitals.get('health_score', 100)
            failed_writes = vitals.get('failed_writes_24h', 0)

            if status == 'damaged' or health_score < 30:
                events.append(CoordinationEvent(
                    event_type=CoordinationEventType.SKIN_DAMAGED,
                    source_system='skin',
                    severity='critical',
                    message=f'Workspace operations damaged: {failed_writes} failed writes',
                    data={'status': status, 'health_score': health_score, 'failed_writes': failed_writes}
                ))
            elif status == 'irritated' or failed_writes > 10:
                events.append(CoordinationEvent(
                    event_type=CoordinationEventType.SKIN_IRRITATED,
                    source_system='skin',
                    severity='warning',
                    message=f'Workspace write issues: {failed_writes} failures',
                    data={'status': status, 'health_score': health_score, 'failed_writes': failed_writes}
                ))

        except Exception as e:
            logger.error(f"Error detecting SKIN events: {e}")

        return events

    def _detect_nervous_events(self) -> List[CoordinationEvent]:
        """Detect NERVOUS (WebSocket communication) events."""
        events = []
        try:
            from core.services.nervous import get_nervous_service
            nervous = get_nervous_service()
            vitals = nervous.get_vitals()

            status = vitals.get('status', 'unknown')
            health_score = vitals.get('health_score', 100)

            # Only alert on actual infrastructure issues, not normal idle behavior
            if status == 'damaged' or health_score < 20:
                events.append(CoordinationEvent(
                    event_type=CoordinationEventType.NERVOUS_DAMAGED,
                    source_system='nervous',
                    severity='critical',
                    message='WebSocket infrastructure damaged - check Redis and Daphne',
                    data={'status': status, 'health_score': health_score}
                ))
            elif status == 'overloaded':
                events.append(CoordinationEvent(
                    event_type=CoordinationEventType.NERVOUS_OVERLOADED,
                    source_system='nervous',
                    severity='warning',
                    message='WebSocket system overloaded - too many connections',
                    data={'status': status, 'health_score': health_score}
                ))
            # Note: 'dormant', 'sluggish', 'numb' are normal states - no events

        except Exception as e:
            logger.error(f"Error detecting NERVOUS events: {e}")

        return events

    # =========================================================================
    # Event Handlers - Automated Responses
    # =========================================================================

    def _handle_lungs_exhausted(self, event: CoordinationEvent) -> List[str]:
        """Handle LUNGS exhausted - enable throttle mode."""
        actions = []

        # 1. Enable throttle mode
        self.set_throttle_mode(True)
        actions.append("Enabled throttle mode")

        # 2. Send Discord alert
        try:
            from core.services.discord_notifications import send_status_notification
            send_status_notification(
                "🫁 LUNGS EXHAUSTED",
                f"Budget at {event.data.get('oxygen_level', 0):.1f}% - Throttle mode enabled",
                "critical"
            )
            actions.append("Sent Discord alert")
        except Exception as e:
            logger.error(f"Failed to send Discord alert: {e}")

        # 3. Create attention item
        actions.append("Created attention item for budget exhaustion")

        return actions

    def _handle_lungs_low(self, event: CoordinationEvent) -> List[str]:
        """Handle LUNGS low - warn but don't throttle."""
        actions = []

        # Send warning notification
        try:
            from core.services.discord_notifications import send_status_notification
            send_status_notification(
                "🫁 LUNGS Low",
                f"Budget at {event.data.get('oxygen_level', 0):.1f}% - Consider reducing operations",
                "warning"
            )
            actions.append("Sent Discord warning")
        except Exception as e:
            logger.error(f"Failed to send Discord warning: {e}")

        return actions

    def _handle_lungs_recovered(self, event: CoordinationEvent) -> List[str]:
        """Handle LUNGS recovered - disable throttle mode."""
        actions = []

        # Disable throttle mode
        self.set_throttle_mode(False)
        actions.append("Disabled throttle mode")

        # Send recovery notification
        try:
            from core.services.discord_notifications import send_status_notification
            send_status_notification(
                "🫁 LUNGS Recovered",
                f"Budget at {event.data.get('oxygen_level', 0):.1f}% - Normal operations resumed",
                "info"
            )
            actions.append("Sent recovery notification")
        except Exception as e:
            logger.error(f"Failed to send recovery notification: {e}")

        return actions

    def _handle_heart_critical(self, event: CoordinationEvent) -> List[str]:
        """Handle HEART critical - major alert."""
        actions = []

        # Send critical Discord alert
        try:
            from core.services.discord_notifications import send_status_notification
            send_status_notification(
                "❤️ HEART CRITICAL",
                f"Core platform health critical: {event.message}",
                "critical"
            )
            actions.append("Sent critical Discord alert")
        except Exception as e:
            logger.error(f"Failed to send Discord alert: {e}")

        # Enable throttle mode to reduce load
        self.set_throttle_mode(True)
        actions.append("Enabled throttle mode to reduce load")

        return actions

    def _handle_heart_degraded(self, event: CoordinationEvent) -> List[str]:
        """Handle HEART degraded - warning."""
        actions = []

        try:
            from core.services.discord_notifications import send_status_notification
            send_status_notification(
                "❤️ HEART Degraded",
                f"Core platform health degraded: {event.message}",
                "warning"
            )
            actions.append("Sent degraded warning")
        except Exception as e:
            logger.error(f"Failed to send Discord warning: {e}")

        return actions

    def _handle_heart_recovered(self, event: CoordinationEvent) -> List[str]:
        """Handle HEART recovered."""
        actions = []
        actions.append("Heart recovered - monitoring continues")
        return actions

    def _handle_immune_threat(self, event: CoordinationEvent) -> List[str]:
        """Handle IMMUNE threat - security response."""
        actions = []

        # Send security alert
        try:
            from core.services.discord_notifications import send_status_notification
            send_status_notification(
                "🛡️ IMMUNE Threat Detected",
                f"Security threat level: {event.data.get('threat_level', 'unknown')}",
                "critical" if event.severity == 'critical' else "warning"
            )
            actions.append("Sent security alert")
        except Exception as e:
            logger.error(f"Failed to send security alert: {e}")

        # Notify SPINE to increase scrutiny
        actions.append("Notified SPINE to increase request scrutiny")

        return actions

    def _handle_immune_clear(self, event: CoordinationEvent) -> List[str]:
        """Handle IMMUNE clear - threats resolved."""
        actions = []
        actions.append("Immune system clear - normal security level")
        return actions

    def _handle_digestive_blocked(self, event: CoordinationEvent) -> List[str]:
        """Handle DIGESTIVE blocked - pause spider execution + inbox HAI.

        Session 2735 addition: alongside the pre-existing Discord alert,
        also create a ``HumanAttentionItem(source_type='data_pipeline_stall',
        urgency='critical')`` via ``HumanAttentionBridge`` so the silent-
        outage 24h invisibility window (per Capability Graph §5 Item 9)
        closes at the same 10-min cadence as this autonomic tick.

        Dedup: skip if any open (undecided) ``data_pipeline_stall`` HAI
        was created within the last hour. Matches the §14 body-system
        cadence policy — the tick fires every 10 min, so an unguarded
        dispatch would create 6 duplicate HAI per persistent-critical
        hour.

        Kill switch: ``settings.DATA_PIPELINE_STALL_HAI_ENABLED``
        (default True). Discord alert path is unaffected by the
        switch.
        """
        actions = []

        # Send alert (pre-existing)
        try:
            from core.services.discord_notifications import send_status_notification
            send_status_notification(
                "🍽️ DIGESTIVE Blocked",
                f"Data pipeline blocked - pausing spider execution",
                "critical"
            )
            actions.append("Sent pipeline blocked alert")
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")

        # Session 2735 — inbox HAI production (Capability Chain §5 Item 14).
        from django.conf import settings as _dj_settings
        if getattr(_dj_settings, 'DATA_PIPELINE_STALL_HAI_ENABLED', True):
            try:
                if self._data_pipeline_stall_dedup_open():
                    actions.append(
                        "Skipped HAI dispatch — open data_pipeline_stall "
                        "attention already present within 1h dedup window"
                    )
                else:
                    self._dispatch_data_pipeline_stall_hai(event)
                    actions.append("Created data_pipeline_stall HumanAttentionItem")
            except Exception as e:  # pragma: no cover — defensive
                logger.warning(
                    "[BodyCoordinator] data_pipeline_stall HAI dispatch "
                    "failed (%s: %s); Discord alert path unaffected",
                    type(e).__name__, e,
                )

        # Signal spider coordinator to pause
        actions.append("Signaled spider coordinator to pause execution")

        return actions

    def _data_pipeline_stall_dedup_open(self) -> bool:
        """True if an undecided ``data_pipeline_stall`` HAI was created
        in the last hour. Fails safe to ``False`` on any error so a
        broken lookup does NOT swallow a genuine escalation.
        """
        try:
            from datetime import timedelta as _td
            from core.models_human_interface import HumanAttentionItem
            cutoff = timezone.now() - _td(hours=1)
            return HumanAttentionItem.objects.filter(
                source_type='data_pipeline_stall',
                decided_at__isnull=True,
                created_at__gte=cutoff,
            ).exists()
        except Exception as e:  # pragma: no cover — defensive
            logger.warning(
                "[BodyCoordinator] data_pipeline_stall dedup lookup "
                "failed (%s: %s); allowing escalation",
                type(e).__name__, e,
            )
            return False

    def _dispatch_data_pipeline_stall_hai(self, event: CoordinationEvent):
        """Dispatch to the HumanAttentionBridge with the current
        digestive snapshot embedded in the event payload.
        """
        from core.services.human_attention_bridge import attention_bridge
        data = event.data or {}
        digestive_status = str(data.get('status') or 'starving')
        items_pending = int(data.get('items_pending', 0) or 0)
        items_24h = int(data.get('items_24h', 0) or 0)
        recent_intake = int(data.get('recent_intake', 0) or 0)
        # Bucket rounds the coordination event's minute-precision
        # timestamp down to the hour so retries within the same tick
        # window produce the same idempotency_key.
        ts = event.timestamp or timezone.now()
        window_bucket = ts.strftime('%Y-%m-%d:%H')
        attention_bridge.create_data_pipeline_stall_attention(
            digestive_status=digestive_status,
            items_pending=items_pending,
            items_24h=items_24h,
            recent_intake=recent_intake,
            window_bucket=window_bucket,
        )

    def _handle_digestive_bloated(self, event: CoordinationEvent) -> List[str]:
        """Handle DIGESTIVE bloated - reduce intake rate."""
        actions = []

        try:
            from core.services.discord_notifications import send_status_notification
            send_status_notification(
                "🍽️ DIGESTIVE Backlog",
                f"Queue backlog: {event.data.get('items_pending', 0)} items pending",
                "warning"
            )
            actions.append("Sent backlog warning")
        except Exception as e:
            logger.error(f"Failed to send warning: {e}")

        actions.append("Recommended reducing spider fetch rate")

        return actions

    def _handle_digestive_healthy(self, event: CoordinationEvent) -> List[str]:
        """Handle DIGESTIVE healthy."""
        actions = []
        actions.append("Digestive system healthy - normal processing")
        return actions

    def _handle_muscular_issue(self, event: CoordinationEvent) -> List[str]:
        """Handle MUSCULAR issues - reduce agent routing."""
        actions = []

        # Send alert
        try:
            from core.services.discord_notifications import send_status_notification
            status = "paralyzed" if event.event_type == CoordinationEventType.MUSCULAR_PARALYZED else "strained"
            send_status_notification(
                f"💪 MUSCULAR {status.title()}",
                f"Agent execution {status}: {event.data.get('success_rate', 0):.1f}% success rate",
                "critical" if status == "paralyzed" else "warning"
            )
            actions.append(f"Sent muscular {status} alert")
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")

        # Recommend reducing agent workload
        actions.append("Recommended reducing agent workload")

        return actions

    def _handle_muscular_recovered(self, event: CoordinationEvent) -> List[str]:
        """Handle MUSCULAR recovered."""
        actions = []
        actions.append("Muscular system recovered - agents performing well")
        return actions

    def _handle_circulatory_issue(self, event: CoordinationEvent) -> List[str]:
        """Handle CIRCULATORY issues."""
        actions = []

        try:
            from core.services.discord_notifications import send_status_notification
            send_status_notification(
                "🩸 CIRCULATORY Issue",
                f"Data flow {event.data.get('status', 'unknown')}",
                "critical" if event.event_type == CoordinationEventType.CIRCULATORY_BLOCKED else "warning"
            )
            actions.append("Sent circulatory alert")
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")

        return actions

    def _handle_circulatory_recovered(self, event: CoordinationEvent) -> List[str]:
        """Handle CIRCULATORY recovered."""
        actions = []
        actions.append("Circulatory system flowing normally")
        return actions

    def _handle_spine_issue(self, event: CoordinationEvent) -> List[str]:
        """Handle SPINE issues."""
        actions = []

        try:
            from core.services.discord_notifications import send_status_notification
            send_status_notification(
                "🦴 SPINE Issue",
                f"API routing {event.data.get('status', 'unknown')}",
                "critical" if event.event_type == CoordinationEventType.SPINE_INJURED else "warning"
            )
            actions.append("Sent spine alert")
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")

        return actions

    def _handle_spine_recovered(self, event: CoordinationEvent) -> List[str]:
        """Handle SPINE recovered."""
        actions = []
        actions.append("Spine aligned - routing normal")
        return actions

    # Session 725: BRAIN, SKIN, NERVOUS handlers

    def _handle_brain_issue(self, event: CoordinationEvent) -> List[str]:
        """Handle BRAIN issues - cognitive/ML problems."""
        actions = []

        try:
            from core.services.discord_notifications import send_status_notification
            is_overloaded = event.event_type == CoordinationEventType.BRAIN_OVERLOADED
            send_status_notification(
                f"🧠 BRAIN {'Overloaded' if is_overloaded else 'Confused'}",
                f"Cognitive processing issue: {event.message}",
                "critical" if is_overloaded else "warning"
            )
            actions.append("Sent brain alert")
        except Exception as e:
            logger.error(f"Failed to send brain alert: {e}")

        # If overloaded, recommend reducing ML workload
        if event.event_type == CoordinationEventType.BRAIN_OVERLOADED:
            self.set_throttle_mode(True)
            actions.append("Enabled throttle mode to reduce ML load")

        return actions

    def _handle_brain_recovered(self, event: CoordinationEvent) -> List[str]:
        """Handle BRAIN recovered."""
        actions = []
        actions.append("Brain focused - cognitive processing normal")
        return actions

    def _handle_skin_issue(self, event: CoordinationEvent) -> List[str]:
        """Handle SKIN issues - workspace write problems."""
        actions = []

        try:
            from core.services.discord_notifications import send_status_notification
            is_damaged = event.event_type == CoordinationEventType.SKIN_DAMAGED
            send_status_notification(
                f"🖐️ SKIN {'Damaged' if is_damaged else 'Irritated'}",
                f"Workspace issue: {event.message}",
                "critical" if is_damaged else "warning"
            )
            actions.append("Sent skin alert")
        except Exception as e:
            logger.error(f"Failed to send skin alert: {e}")

        # Recommend checking workspace permissions
        actions.append("Check workspace file permissions and disk space")

        return actions

    def _handle_skin_recovered(self, event: CoordinationEvent) -> List[str]:
        """Handle SKIN recovered."""
        actions = []
        actions.append("Skin healthy - workspace operations normal")
        return actions

    def _handle_nervous_issue(self, event: CoordinationEvent) -> List[str]:
        """Handle NERVOUS issues - WebSocket infrastructure problems."""
        actions = []

        try:
            from core.services.discord_notifications import send_status_notification
            is_damaged = event.event_type == CoordinationEventType.NERVOUS_DAMAGED
            send_status_notification(
                f"⚡ NERVOUS {'Damaged' if is_damaged else 'Overloaded'}",
                f"WebSocket issue: {event.message}",
                "critical" if is_damaged else "warning"
            )
            actions.append("Sent nervous alert")
        except Exception as e:
            logger.error(f"Failed to send nervous alert: {e}")

        # If damaged, recommend checking Redis and Daphne
        if event.event_type == CoordinationEventType.NERVOUS_DAMAGED:
            actions.append("Check Redis connection and Daphne WebSocket server")
        else:
            actions.append("Consider scaling WebSocket infrastructure")

        return actions

    def _handle_nervous_recovered(self, event: CoordinationEvent) -> List[str]:
        """Handle NERVOUS recovered."""
        actions = []
        actions.append("Nervous system responsive - WebSocket communication normal")
        return actions

    # =========================================================================
    # Throttle Mode Management
    # =========================================================================

    def is_throttled(self) -> bool:
        """Check if the system is in throttle mode."""
        return cache.get(self.THROTTLE_CACHE_KEY, False)

    def set_throttle_mode(self, enabled: bool) -> None:
        """Enable or disable throttle mode."""
        cache.set(self.THROTTLE_CACHE_KEY, enabled, timeout=3600 * 24)  # 24 hour timeout
        logger.info(f"🧠 Throttle mode {'enabled' if enabled else 'disabled'}")

    def get_throttle_factor(self) -> float:
        """
        Get the throttle factor (0.0-1.0).

        Returns:
            1.0 = normal operations
            0.5 = half speed
            0.1 = emergency only
        """
        if not self.is_throttled():
            return 1.0

        # Check current LUNGS status for more granular throttling
        try:
            from core.services.lungs import get_lungs_monitor
            lungs = get_lungs_monitor()
            vitals = lungs.get_vitals()
            oxygen = vitals.get('oxygen_level', 0)

            if oxygen <= 5:
                return 0.1  # Emergency only
            elif oxygen <= 10:
                return 0.3  # Heavily throttled
            elif oxygen <= 20:
                return 0.5  # Moderately throttled
            else:
                return 0.7  # Lightly throttled
        except Exception:
            return 0.5  # Default moderate throttle

    # =========================================================================
    # Status and Reporting
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get current coordination status."""
        return {
            'is_throttled': self.is_throttled(),
            'throttle_factor': self.get_throttle_factor(),
            'last_check': cache.get(self.LAST_CHECK_CACHE_KEY),
            'recent_responses': len(self._response_log),
            'handlers_registered': len(self.handlers)
        }

    def get_response_log(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent coordination responses."""
        return [
            {
                'event_type': r.event.event_type.value,
                'source_system': r.event.source_system,
                'severity': r.event.severity,
                'message': r.event.message,
                'actions': r.actions_taken,
                'success': r.success,
                'response_time_ms': r.response_time_ms,
                'timestamp': r.timestamp.isoformat()
            }
            for r in self._response_log[-limit:]
        ]
