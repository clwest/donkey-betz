"""
Session 705: IMMUNE SYSTEM - Security & Threat Detection Service

The IMMUNE SYSTEM is the defense layer of the AI body - detecting and responding
to threats, suspicious patterns, and malicious activity.

Key Features:
- Threat pattern detection (signature, threshold, anomaly)
- Automatic response to detected threats
- Quarantine management for blocked entities
- Integration with SPINE for request analysis
- Integration with HEART for health reporting

Usage:
    from core.services.immune import get_immune_system

    immune = get_immune_system()

    # Run full immune scan
    result = immune.scan()

    # Check if request is allowed
    allowed, reason = immune.check_request(ip='1.2.3.4', path='/api/agents/')

    # Detect threats in a request
    threats = immune.detect_threats(request_data)

    # Quarantine an IP
    immune.quarantine_ip('1.2.3.4', reason='rate_abuse', duration_minutes=60)
"""

import logging
import re
import uuid
from datetime import timedelta
from typing import Optional, Tuple, List, Dict, Any

from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

logger = logging.getLogger(__name__)


# Singleton instance
_immune_instance: Optional['ImmuneSystemService'] = None


def get_immune_system() -> 'ImmuneSystemService':
    """Get the singleton ImmuneSystemService instance."""
    global _immune_instance
    if _immune_instance is None:
        _immune_instance = ImmuneSystemService()
    return _immune_instance


class ImmuneSystemService:
    """
    Security & Threat Detection - the immune system of the AI body.

    Detects threats, responds to attacks, and maintains quarantine lists.
    Integrates with SPINE (request routing) and HEART (health monitoring).
    """

    # Health thresholds
    HEALTHY_THRESHOLD = 90.0      # 90%+ = healthy
    ALERT_THRESHOLD = 70.0        # 70-90% = alert
    FIGHTING_THRESHOLD = 50.0     # 50-70% = fighting
    OVERWHELMED_THRESHOLD = 30.0  # 30-50% = overwhelmed
    # Below 30% = compromised

    # Threat level thresholds
    THREAT_LEVEL_LOW = 5          # 5+ threats = low
    THREAT_LEVEL_ELEVATED = 15    # 15+ threats = elevated
    THREAT_LEVEL_HIGH = 30        # 30+ threats = high
    THREAT_LEVEL_SEVERE = 50      # 50+ threats = severe

    # Cache duration
    CACHE_DURATION_SECONDS = 30

    def __init__(self):
        self._cached_status = None
        self._cache_time = None
        self._pattern_cache = {}
        self._quarantine_cache = {}
        self._quarantine_cache_time = None

    def scan(self, force: bool = False) -> dict:
        """
        Run full immune system scan - the main health check method.

        Returns:
            dict: Comprehensive immune status including:
                - overall_status: healthy/alert/fighting/overwhelmed/compromised
                - health_score: 0-100%
                - threat_level: none/low/elevated/high/severe
                - active threats and quarantine status
        """
        from core.models_immune import (
            ThreatPattern, ThreatEvent, ImmuneResponse, Quarantine, ImmuneStatus
        )

        start_time = timezone.now()
        cutoff_24h = timezone.now() - timedelta(hours=24)

        # Get or create immune status record
        status, created = ImmuneStatus.objects.get_or_create(
            pk=uuid.UUID('00000000-0000-0000-0000-000000000002'),
            defaults={
                'status': 'healthy',
                'health_score': 100.0,
            }
        )

        # Count active patterns
        active_patterns = ThreatPattern.objects.filter(is_active=True).count()

        # Count threats in last 24 hours
        threats_24h = ThreatEvent.objects.filter(detected_at__gte=cutoff_24h)
        threats_detected_24h = threats_24h.count()

        # Active threats (not resolved)
        active_threats = ThreatEvent.objects.filter(
            status__in=['detected', 'analyzing', 'responded', 'escalated']
        ).count()

        # Threats blocked
        threats_blocked_24h = threats_24h.filter(
            response_taken__in=['block_temp', 'block_perm', 'quarantine']
        ).count()

        # False positives
        false_positives_24h = threats_24h.filter(status='false_positive').count()

        # Count quarantined entities
        active_quarantine = Quarantine.objects.filter(
            is_active=True
        ).filter(
            Q(is_permanent=True) | Q(expires_at__gt=timezone.now())
        )
        quarantined_ips = active_quarantine.filter(entity_type='ip').count()
        quarantined_users = active_quarantine.filter(entity_type='user').count()
        total_quarantined = active_quarantine.count()

        # Count responses
        responses_24h = ImmuneResponse.objects.filter(responded_at__gte=cutoff_24h)
        auto_responses_24h = responses_24h.filter(is_automatic=True).count()
        manual_responses_24h = responses_24h.filter(is_automatic=False).count()

        # Threats by category
        threats_by_category = dict(
            threats_24h.values('category').annotate(count=Count('id')).values_list('category', 'count')
        )

        # Threats by severity
        threats_by_severity = dict(
            threats_24h.values('severity').annotate(count=Count('id')).values_list('severity', 'count')
        )

        # Patterns triggered
        patterns_triggered_24h = threats_24h.values('pattern').distinct().count()

        # Calculate health score
        health_score = self._calculate_health_score(
            active_threats=active_threats,
            threats_detected_24h=threats_detected_24h,
            threats_blocked_24h=threats_blocked_24h,
            false_positives_24h=false_positives_24h,
            threats_by_severity=threats_by_severity,
        )

        # Determine threat level
        threat_level = self._calculate_threat_level(active_threats, threats_by_severity)

        # Determine status
        if health_score >= self.HEALTHY_THRESHOLD:
            overall_status = 'healthy'
        elif health_score >= self.ALERT_THRESHOLD:
            overall_status = 'alert'
        elif health_score >= self.FIGHTING_THRESHOLD:
            overall_status = 'fighting'
        elif health_score >= self.OVERWHELMED_THRESHOLD:
            overall_status = 'overwhelmed'
        else:
            overall_status = 'compromised'

        # Check integrations
        spine_connected = self._check_spine_connection()
        heart_connected = self._check_heart_connection()

        end_time = timezone.now()
        scan_duration_ms = (end_time - start_time).total_seconds() * 1000

        # Update status record
        status.update_status(overall_status, health_score, threat_level)
        status.active_threats = active_threats
        status.threats_detected_24h = threats_detected_24h
        status.threats_blocked_24h = threats_blocked_24h
        status.false_positives_24h = false_positives_24h
        status.quarantined_ips = quarantined_ips
        status.quarantined_users = quarantined_users
        status.total_quarantined = total_quarantined
        status.active_patterns = active_patterns
        status.patterns_triggered_24h = patterns_triggered_24h
        status.auto_responses_24h = auto_responses_24h
        status.manual_responses_24h = manual_responses_24h
        status.threats_by_category = threats_by_category
        status.threats_by_severity = threats_by_severity
        status.spine_connected = spine_connected
        status.heart_connected = heart_connected
        if active_threats > 0:
            status.last_threat = timezone.now()
        status.save()

        # Cache result
        self._cached_status = status
        self._cache_time = timezone.now()

        result = {
            'timestamp': timezone.now().isoformat(),
            'overall_status': overall_status,
            'health_score': round(health_score, 1),
            'is_healthy': overall_status in ('healthy', 'alert'),
            'threat_level': threat_level,
            'scan_duration_ms': round(scan_duration_ms, 2),

            # Threat counts
            'threats': {
                'active': active_threats,
                'detected_24h': threats_detected_24h,
                'blocked_24h': threats_blocked_24h,
                'false_positives_24h': false_positives_24h,
            },

            # Quarantine status
            'quarantine': {
                'total': total_quarantined,
                'ips': quarantined_ips,
                'users': quarantined_users,
            },

            # Pattern activity
            'patterns': {
                'active': active_patterns,
                'triggered_24h': patterns_triggered_24h,
            },

            # Response metrics
            'responses': {
                'auto_24h': auto_responses_24h,
                'manual_24h': manual_responses_24h,
            },

            # Breakdown
            'threats_by_category': threats_by_category,
            'threats_by_severity': threats_by_severity,

            # Integration status
            'integrations': {
                'spine': spine_connected,
                'heart': heart_connected,
            },
        }

        logger.info(f"IMMUNE scan: {overall_status} ({health_score:.1f}%) - "
                   f"Threat Level: {threat_level}, Active: {active_threats}")

        return result

    def is_healthy(self) -> bool:
        """Quick check - is the immune system healthy?"""
        status = self._get_cached_status()
        return status.is_healthy if status else True

    def get_vitals(self) -> dict:
        """Get current immune vitals (cached)."""
        status = self._get_cached_status()
        if not status:
            try:
                return self.scan()
            except Exception as e:
                logger.warning(f"IMMUNE full check failed, returning defaults: {e}")
                return {
                    'overall_status': 'unknown',
                    'health_score': 50,
                    'is_healthy': True,
                    'threat_level': 'unknown',
                    'active_threats': 0,
                    'threats_detected_24h': 0,
                    'quarantine': {'total': 0, 'ips': [], 'users': []},
                    'patterns': {'active': 0, 'triggered_24h': 0},
                    'threats_by_category': {},
                    'threats_by_severity': {},
                    'error': str(e),
                }

        return {
            'timestamp': status.last_scan.isoformat(),
            'overall_status': status.status,
            'health_score': status.health_score,
            'is_healthy': status.is_healthy,
            'threat_level': status.threat_level,
            'active_threats': status.active_threats,
            'threats_detected_24h': status.threats_detected_24h,
            'quarantine': {
                'total': status.total_quarantined,
                'ips': status.quarantined_ips,
                'users': status.quarantined_users,
            },
            'patterns': {
                'active': status.active_patterns,
                'triggered_24h': status.patterns_triggered_24h,
            },
            'threats_by_category': status.threats_by_category,
            'threats_by_severity': status.threats_by_severity,
        }

    def get_status(self) -> dict:
        """Get current status for body coordinator integration."""
        return self.get_vitals()

    def check_request(self, ip: str = None, user_id: int = None,
                     path: str = None, user_agent: str = None) -> Tuple[bool, str]:
        """
        Check if a request should be allowed.

        Returns:
            Tuple[bool, str]: (allowed, reason)
        """
        # Check quarantine
        if ip:
            quarantined = self._is_quarantined('ip', ip)
            if quarantined:
                self._record_blocked_request('ip', ip)
                return False, f"IP {ip} is quarantined"

        if user_id:
            quarantined = self._is_quarantined('user', str(user_id))
            if quarantined:
                self._record_blocked_request('user', str(user_id))
                return False, f"User {user_id} is quarantined"

        if user_agent:
            quarantined = self._is_quarantined('user_agent', user_agent)
            if quarantined:
                return False, "User agent is blocked"

        return True, "Request allowed"

    def detect_threats(self, request_data: dict) -> List[dict]:
        """
        Detect threats in request data.

        Args:
            request_data: Dict containing ip, path, method, user_id, user_agent, params, body

        Returns:
            List of detected threat patterns
        """
        from core.models_immune import ThreatPattern

        detected = []

        # Get all active patterns
        patterns = self._get_active_patterns()

        for pattern in patterns:
            if pattern.detection_type == 'signature':
                # Signature-based detection
                match = self._check_signature(pattern, request_data)
                if match:
                    detected.append({
                        'pattern': pattern,
                        'match': match,
                        'confidence': 1.0,
                    })

            elif pattern.detection_type == 'threshold':
                # Threshold-based detection (rate limiting)
                exceeded = self._check_threshold(pattern, request_data)
                if exceeded:
                    detected.append({
                        'pattern': pattern,
                        'match': exceeded,
                        'confidence': 1.0,
                    })

        return detected

    def record_threat(self, pattern_id: uuid.UUID, request_data: dict,
                     details: dict = None, confidence: float = 1.0) -> 'ThreatEvent':
        """Record a detected threat event."""
        from core.models_immune import ThreatPattern, ThreatEvent

        try:
            pattern = ThreatPattern.objects.get(pk=pattern_id)
        except ThreatPattern.DoesNotExist:
            logger.warning(f"Threat pattern not found: {pattern_id}")
            return None

        # Create threat event
        event = ThreatEvent.objects.create(
            pattern=pattern,
            severity=pattern.severity,
            category=pattern.category,
            source_ip=request_data.get('ip'),
            source_user_id=request_data.get('user_id'),
            source_user_agent=request_data.get('user_agent', ''),
            source_path=request_data.get('path', ''),
            source_method=request_data.get('method', ''),
            detection_details=details or {},
            confidence_score=confidence,
        )

        # Update pattern statistics
        pattern.total_detections += 1
        pattern.last_detection = timezone.now()
        pattern.save(update_fields=['total_detections', 'last_detection'])

        # Auto-respond if configured
        if pattern.auto_respond:
            self._auto_respond(event, pattern)

        logger.warning(f"IMMUNE: Threat detected - {pattern.display_name} "
                      f"(severity: {pattern.severity}) from {request_data.get('ip')}")

        return event

    def respond_to_threat(self, event_id: uuid.UUID, action: str,
                         target_type: str, target_value: str,
                         duration_minutes: int = None,
                         is_automatic: bool = False) -> 'ImmuneResponse':
        """Record and execute a response to a threat."""
        from core.models_immune import ThreatEvent, ImmuneResponse

        try:
            event = ThreatEvent.objects.get(pk=event_id)
        except ThreatEvent.DoesNotExist:
            logger.warning(f"Threat event not found: {event_id}")
            return None

        # Calculate expiration
        expires_at = None
        if duration_minutes and action in ('rate_limit', 'block_temp'):
            expires_at = timezone.now() + timedelta(minutes=duration_minutes)

        # Create response record
        response = ImmuneResponse.objects.create(
            event=event,
            action=action,
            is_automatic=is_automatic,
            target_type=target_type,
            target_value=target_value,
            duration_minutes=duration_minutes,
            expires_at=expires_at,
        )

        # Execute the response
        if action in ('block_temp', 'block_perm', 'quarantine'):
            self._quarantine_entity(
                entity_type=target_type,
                entity_value=target_value,
                reason=event.category,
                is_permanent=(action == 'block_perm'),
                duration_minutes=duration_minutes,
                event=event,
            )

        # Update event status
        event.status = 'responded'
        event.response_taken = action
        event.response_at = timezone.now()
        event.save()

        logger.info(f"IMMUNE: Response taken - {action} on {target_type}:{target_value}")

        return response

    def quarantine_ip(self, ip: str, reason: str, duration_minutes: int = None,
                     is_permanent: bool = False, notes: str = '') -> 'Quarantine':
        """Quarantine an IP address."""
        return self._quarantine_entity(
            entity_type='ip',
            entity_value=ip,
            reason=reason,
            is_permanent=is_permanent,
            duration_minutes=duration_minutes,
            notes=notes,
        )

    def quarantine_user(self, user_id: int, reason: str, duration_minutes: int = None,
                       is_permanent: bool = False, notes: str = '') -> 'Quarantine':
        """Quarantine a user account."""
        return self._quarantine_entity(
            entity_type='user',
            entity_value=str(user_id),
            reason=reason,
            is_permanent=is_permanent,
            duration_minutes=duration_minutes,
            notes=notes,
        )

    def release_from_quarantine(self, entity_type: str, entity_value: str) -> bool:
        """Release an entity from quarantine."""
        from core.models_immune import Quarantine

        try:
            quarantine = Quarantine.objects.get(
                entity_type=entity_type,
                entity_value=entity_value,
                is_active=True,
            )
            quarantine.is_active = False
            quarantine.save()

            # Clear cache
            cache_key = f"{entity_type}:{entity_value}"
            if cache_key in self._quarantine_cache:
                del self._quarantine_cache[cache_key]

            logger.info(f"IMMUNE: Released {entity_type}:{entity_value} from quarantine")
            return True
        except Quarantine.DoesNotExist:
            return False

    def get_quarantine_list(self, entity_type: str = None,
                           active_only: bool = True) -> List[dict]:
        """Get list of quarantined entities."""
        from core.models_immune import Quarantine

        queryset = Quarantine.objects.all()

        if active_only:
            queryset = queryset.filter(is_active=True).filter(
                Q(is_permanent=True) | Q(expires_at__gt=timezone.now())
            )

        if entity_type:
            queryset = queryset.filter(entity_type=entity_type)

        return [
            {
                'id': str(q.id),
                'entity_type': q.entity_type,
                'entity_value': q.entity_value,
                'reason': q.reason,
                'is_permanent': q.is_permanent,
                'expires_at': q.expires_at.isoformat() if q.expires_at else None,
                'blocked_requests': q.blocked_requests,
                'created_at': q.created_at.isoformat(),
            }
            for q in queryset
        ]

    def get_recent_threats(self, hours: int = 24, limit: int = 100,
                          severity: str = None, category: str = None) -> List[dict]:
        """Get recent threat events."""
        from core.models_immune import ThreatEvent

        cutoff = timezone.now() - timedelta(hours=hours)

        queryset = ThreatEvent.objects.filter(detected_at__gte=cutoff)

        if severity:
            queryset = queryset.filter(severity=severity)
        if category:
            queryset = queryset.filter(category=category)

        return [
            {
                'id': str(t.id),
                'pattern': t.pattern.display_name if t.pattern else 'Unknown',
                'severity': t.severity,
                'category': t.category,
                'status': t.status,
                'source_ip': t.source_ip,
                'source_path': t.source_path,
                'detected_at': t.detected_at.isoformat(),
                'response_taken': t.response_taken,
            }
            for t in queryset[:limit]
        ]

    def get_patterns(self, category: str = None, active_only: bool = True) -> List[dict]:
        """Get threat patterns."""
        from core.models_immune import ThreatPattern

        queryset = ThreatPattern.objects.all()

        if active_only:
            queryset = queryset.filter(is_active=True)
        if category:
            queryset = queryset.filter(category=category)

        return [
            {
                'id': str(p.id),
                'name': p.name,
                'display_name': p.display_name,
                'category': p.category,
                'severity': p.severity,
                'detection_type': p.detection_type,
                'auto_respond': p.auto_respond,
                'response_action': p.response_action,
                'is_active': p.is_active,
                'is_builtin': p.is_builtin,
                'total_detections': p.total_detections,
                'last_detection': p.last_detection.isoformat() if p.last_detection else None,
            }
            for p in queryset
        ]

    def get_status_emoji(self) -> str:
        """Get emoji for current status."""
        status = self._get_cached_status()
        if not status:
            return '❓'

        return {
            'healthy': '🛡️',
            'alert': '⚠️',
            'fighting': '⚔️',
            'overwhelmed': '🔥',
            'compromised': '💀',
        }.get(status.status, '❓')

    # Private methods

    def _get_cached_status(self) -> Optional['ImmuneStatus']:
        """Get cached status or fetch from DB."""
        from core.models_immune import ImmuneStatus

        if (self._cached_status and self._cache_time and
            (timezone.now() - self._cache_time).total_seconds() < self.CACHE_DURATION_SECONDS):
            return self._cached_status

        try:
            status = ImmuneStatus.objects.get(
                pk=uuid.UUID('00000000-0000-0000-0000-000000000002')
            )
            self._cached_status = status
            self._cache_time = timezone.now()
            return status
        except ImmuneStatus.DoesNotExist:
            return None

    def _get_active_patterns(self) -> List['ThreatPattern']:
        """Get active threat patterns with caching."""
        from core.models_immune import ThreatPattern

        # Simple cache - refresh every minute
        cache_key = 'all_active'
        if cache_key not in self._pattern_cache:
            self._pattern_cache[cache_key] = list(
                ThreatPattern.objects.filter(is_active=True)
            )
        return self._pattern_cache[cache_key]

    def _is_quarantined(self, entity_type: str, entity_value: str) -> bool:
        """Check if entity is quarantined."""
        from core.models_immune import Quarantine

        cache_key = f"{entity_type}:{entity_value}"

        # Check cache
        if self._quarantine_cache_time:
            cache_age = (timezone.now() - self._quarantine_cache_time).total_seconds()
            if cache_age < 60 and cache_key in self._quarantine_cache:
                return self._quarantine_cache[cache_key]

        # Query database
        is_quarantined = Quarantine.objects.filter(
            entity_type=entity_type,
            entity_value=entity_value,
            is_active=True,
        ).filter(
            Q(is_permanent=True) | Q(expires_at__gt=timezone.now())
        ).exists()

        # Update cache
        self._quarantine_cache[cache_key] = is_quarantined
        self._quarantine_cache_time = timezone.now()

        return is_quarantined

    def _record_blocked_request(self, entity_type: str, entity_value: str):
        """Record a blocked request for quarantine statistics."""
        from core.models_immune import Quarantine

        try:
            quarantine = Quarantine.objects.get(
                entity_type=entity_type,
                entity_value=entity_value,
                is_active=True,
            )
            quarantine.record_block()
        except Quarantine.DoesNotExist:
            pass

    def _check_signature(self, pattern: 'ThreatPattern', request_data: dict) -> Optional[dict]:
        """Check signature-based detection."""
        try:
            regex = re.compile(pattern.pattern, re.IGNORECASE)

            # Check various parts of the request
            check_fields = ['path', 'user_agent']
            params = request_data.get('params', {})
            body = request_data.get('body', '')

            for field in check_fields:
                value = request_data.get(field, '')
                if value and regex.search(value):
                    return {'field': field, 'value': value[:100]}

            # Check params
            for key, value in params.items():
                if isinstance(value, str) and regex.search(value):
                    return {'field': f'param:{key}', 'value': value[:100]}

            # Check body
            if body and isinstance(body, str) and regex.search(body):
                return {'field': 'body', 'value': body[:100]}

        except re.error as e:
            logger.warning(f"Invalid regex in pattern {pattern.name}: {e}")

        return None

    def _check_threshold(self, pattern: 'ThreatPattern', request_data: dict) -> Optional[dict]:
        """Check threshold-based detection."""
        from core.models_immune import ThreatEvent

        ip = request_data.get('ip')
        if not ip:
            return None

        cutoff = timezone.now() - timedelta(seconds=pattern.threshold_window_seconds)

        # Count recent events from this IP
        count = ThreatEvent.objects.filter(
            pattern=pattern,
            source_ip=ip,
            detected_at__gte=cutoff,
        ).count()

        if count >= pattern.threshold_count:
            return {
                'count': count,
                'threshold': pattern.threshold_count,
                'window': pattern.threshold_window_seconds,
            }

        return None

    def _auto_respond(self, event: 'ThreatEvent', pattern: 'ThreatPattern'):
        """Automatically respond to a threat based on pattern configuration."""
        if pattern.response_action == 'log':
            return  # Just logging, no action needed

        target_type = 'ip'
        target_value = event.source_ip

        if not target_value:
            target_type = 'user'
            target_value = str(event.source_user_id) if event.source_user_id else None

        if not target_value:
            return

        self.respond_to_threat(
            event_id=event.id,
            action=pattern.response_action,
            target_type=target_type,
            target_value=target_value,
            duration_minutes=pattern.block_duration_minutes,
            is_automatic=True,
        )

    def _quarantine_entity(self, entity_type: str, entity_value: str,
                          reason: str, is_permanent: bool = False,
                          duration_minutes: int = None, event: 'ThreatEvent' = None,
                          notes: str = '') -> 'Quarantine':
        """Add an entity to quarantine."""
        from core.models_immune import Quarantine

        expires_at = None
        if not is_permanent and duration_minutes:
            expires_at = timezone.now() + timedelta(minutes=duration_minutes)

        quarantine, created = Quarantine.objects.update_or_create(
            entity_type=entity_type,
            entity_value=entity_value,
            defaults={
                'reason': reason,
                'is_permanent': is_permanent,
                'expires_at': expires_at,
                'is_active': True,
                'notes': notes,
            }
        )

        if event:
            quarantine.related_events.add(event)
            quarantine.total_events = quarantine.related_events.count()
            quarantine.save(update_fields=['total_events'])

        # Clear cache
        cache_key = f"{entity_type}:{entity_value}"
        self._quarantine_cache[cache_key] = True
        self._quarantine_cache_time = timezone.now()

        logger.info(f"IMMUNE: Quarantined {entity_type}:{entity_value} "
                   f"({'permanent' if is_permanent else f'{duration_minutes}min'})")

        return quarantine

    def _calculate_health_score(self, active_threats: int, threats_detected_24h: int,
                                threats_blocked_24h: int, false_positives_24h: int,
                                threats_by_severity: dict) -> float:
        """Calculate overall immune health score."""
        score = 100.0

        # Deduct for active threats (up to 30 points)
        score -= min(30, active_threats * 5)

        # Deduct for critical threats (up to 20 points)
        critical_count = threats_by_severity.get('critical', 0)
        score -= min(20, critical_count * 10)

        # Deduct for high severity threats (up to 15 points)
        high_count = threats_by_severity.get('high', 0)
        score -= min(15, high_count * 3)

        # Deduct for volume of threats (up to 20 points)
        if threats_detected_24h > 100:
            score -= min(20, (threats_detected_24h - 100) / 10)

        # Add back for successful blocks (up to 10 points)
        if threats_detected_24h > 0:
            block_rate = threats_blocked_24h / threats_detected_24h
            score += block_rate * 10

        # Deduct for false positives (up to 5 points)
        if threats_detected_24h > 0:
            fp_rate = false_positives_24h / threats_detected_24h
            score -= fp_rate * 5

        return max(0, min(100, score))

    def _calculate_threat_level(self, active_threats: int,
                               threats_by_severity: dict) -> str:
        """Calculate current threat level."""
        # Weight by severity
        weighted_count = (
            threats_by_severity.get('critical', 0) * 10 +
            threats_by_severity.get('high', 0) * 5 +
            threats_by_severity.get('medium', 0) * 2 +
            threats_by_severity.get('low', 0) * 1
        )

        # Add active threats
        total_weight = weighted_count + (active_threats * 3)

        if total_weight >= self.THREAT_LEVEL_SEVERE:
            return 'severe'
        elif total_weight >= self.THREAT_LEVEL_HIGH:
            return 'high'
        elif total_weight >= self.THREAT_LEVEL_ELEVATED:
            return 'elevated'
        elif total_weight >= self.THREAT_LEVEL_LOW:
            return 'low'
        else:
            return 'none'

    def _check_spine_connection(self) -> bool:
        """Check if SPINE service is accessible."""
        try:
            from core.services.spine import get_spine_router
            spine = get_spine_router()
            return spine.is_aligned()
        except Exception as _e:
            logger.warning(
                "immune._check_spine_connection: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return False

    def _check_heart_connection(self) -> bool:
        """Check if HEART service is accessible.

        Session 1083 (Rigby audit): was calling `heart.is_healthy()` but
        HeartMonitorService doesn't have an is_healthy method —
        real method is `is_alive()`. Fired as AttributeError every
        minute via the immune cycle until round 22's swallow-tightening
        surfaced the warning; now fixed.
        """
        try:
            from core.services.heart import get_heart_monitor
            heart = get_heart_monitor()
            return heart.is_alive()
        except Exception as _e:
            logger.warning(
                "immune._check_heart_connection: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return False
