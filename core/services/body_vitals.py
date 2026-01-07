"""
Session 709: Body Vitals Service - Unified Query for All Body Systems
Session 722: Added BRAIN system - cognitive processing monitoring

This service bridges the BRAIN (Personal Assistant) to all BODY SYSTEMS,
enabling the PA to query health status and make informed decisions.

The body systems are:
- HEART: Component health monitoring (brain, organs, sensory, memory)
- LUNGS: Budget/resource management (token limits, costs)
- CIRCULATORY: Data flow (Redis, Celery, WebSockets)
- SPINE: API routing health (latency, errors)
- IMMUNE: Security/threat detection (attacks, quarantine)
- DIGESTIVE: Data ingestion pipeline (spiders, processing)
- MUSCULAR: Agent work execution (success rates, fatigue)
- BRAIN: Cognitive processing (LLM calls, conversations, reasoning)

Usage:
    from core.services.body_vitals import get_body_vitals_service
    service = get_body_vitals_service()
    vitals = service.get_all_vitals()
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


# Singleton instance
_body_vitals_instance: Optional['BodyVitalsService'] = None


def get_body_vitals_service() -> 'BodyVitalsService':
    """Get the singleton BodyVitalsService instance."""
    global _body_vitals_instance
    if _body_vitals_instance is None:
        _body_vitals_instance = BodyVitalsService()
    return _body_vitals_instance


class BodyVitalsService:
    """
    Unified service for querying all body system health.

    This is the bridge between the Brain (PA) and the Body Systems.
    Provides:
    - get_all_vitals(): Query all 9 systems at once
    - check_budget(): Check LUNGS before expensive operations
    - get_alerts(): Get critical alerts from all systems
    """

    SYSTEM_GETTERS = {
        'heart': '_get_heart_vitals',
        'lungs': '_get_lungs_vitals',
        'circulatory': '_get_circulatory_vitals',
        'spine': '_get_spine_vitals',
        'immune': '_get_immune_vitals',
        'digestive': '_get_digestive_vitals',
        'muscular': '_get_muscular_vitals',
        'brain': '_get_brain_vitals',
        'skin': '_get_skin_vitals',
        'nervous': '_get_nervous_vitals',
    }

    # Weights for calculating overall health score
    # Higher weight = more important to overall health
    STATUS_WEIGHTS = {
        'heart': 1.5,       # Critical - affects everything
        'lungs': 1.3,       # Important - budget constraints
        'circulatory': 1.0,
        'spine': 1.2,       # Important - API routing
        'immune': 1.2,      # Important - security
        'digestive': 1.0,
        'muscular': 1.0,
        'brain': 1.4,       # Important - cognitive processing
        'skin': 1.1,        # Important - workspace operations
        'nervous': 1.3,     # Important - real-time communication
    }

    # Status emoji mappings per system
    EMOJI_MAP = {
        'heart': {
            'healthy': '❤️', 'degraded': '💛', 'critical': '🧡', 'offline': '🖤',
            'unknown': '❓', 'error': '❓'
        },
        'lungs': {
            'normal': '🫁', 'elevated': '😤', 'hyperventilating': '🥵', 'holding': '🚫',
            'unknown': '❓', 'error': '❓'
        },
        'circulatory': {
            'flowing': '🩸', 'slow': '🐌', 'congested': '⚠️', 'blocked': '🚫',
            'unknown': '❓', 'error': '❓'
        },
        'spine': {
            'aligned': '🦴', 'strained': '⚡', 'compressed': '🔧', 'injured': '🚨',
            'unknown': '❓', 'error': '❓'
        },
        'immune': {
            'healthy': '🛡️', 'alert': '⚠️', 'fighting': '⚔️', 'overwhelmed': '🔥', 'compromised': '💀',
            'unknown': '❓', 'error': '❓'
        },
        'digestive': {
            'healthy': '🍽️', 'sluggish': '🐌', 'bloated': '🎈', 'blocked': '🚫', 'starving': '💀',
            'unknown': '❓', 'error': '❓'
        },
        'muscular': {
            'strong': '💪', 'fit': '🏃', 'fatigued': '😓', 'strained': '🥵', 'paralyzed': '🦽',
            'unknown': '❓', 'error': '❓'
        },
        'brain': {
            'focused': '🧠', 'thinking': '💭', 'overloaded': '🤯', 'foggy': '🌫️', 'resting': '😴', 'offline': '💀',
            'unknown': '❓', 'error': '❓'
        },
        'skin': {
            'healthy': '🧴', 'active': '✋', 'sweating': '💦', 'irritated': '🔴', 'damaged': '🩹', 'healing': '💊', 'dormant': '😴',
            'unknown': '❓', 'error': '❓'
        },
        'nervous': {
            'responsive': '⚡', 'active': '🔌', 'sluggish': '🐌', 'numb': '😶', 'overloaded': '🔥', 'damaged': '💀', 'dormant': '😴',
            'unknown': '❓', 'error': '❓'
        },
    }

    def get_all_vitals(self, include_details: bool = False) -> Dict[str, Any]:
        """
        Get health status from all 10 body systems.

        Args:
            include_details: Include detailed metrics per system

        Returns:
            Unified health report with:
            - overall_health: Overall status string
            - health_score: 0-100 weighted score
            - systems: Per-system status
            - alerts: All active alerts sorted by severity
            - recommendation: Actionable recommendation
        """
        start = datetime.now()
        systems = {}
        alerts = []
        total_weighted_score = 0
        total_weight = 0

        for system_name, getter_name in self.SYSTEM_GETTERS.items():
            try:
                getter = getattr(self, getter_name)
                vitals = getter(include_details)
                systems[system_name] = vitals

                # Calculate weighted score
                weight = self.STATUS_WEIGHTS.get(system_name, 1.0)
                score = vitals.get('score', 0)
                total_weighted_score += score * weight
                total_weight += weight

                # Collect alerts
                if vitals.get('alerts'):
                    alerts.extend(vitals['alerts'])

            except Exception as e:
                logger.error(f"Error getting {system_name} vitals: {e}")
                systems[system_name] = {
                    'status': 'error',
                    'score': 0,
                    'emoji': '❓',
                    'error': str(e),
                    'alerts': []
                }

        # Calculate overall health
        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0
        overall_status = self._score_to_status(overall_score)

        duration_ms = (datetime.now() - start).total_seconds() * 1000

        return {
            'timestamp': datetime.now().isoformat(),
            'overall_health': overall_status,
            'health_score': round(overall_score, 1),
            'is_healthy': overall_score >= 60,
            'systems': systems,
            'alerts': sorted(alerts, key=lambda x: x.get('severity_score', 0), reverse=True),
            'alert_count': len(alerts),
            'check_duration_ms': round(duration_ms, 2),
            'recommendation': self._generate_recommendation(systems, alerts)
        }

    def get_system_vitals(self, system_name: str, include_details: bool = False) -> Dict[str, Any]:
        """
        Get vitals for a specific body system.

        Args:
            system_name: One of: heart, lungs, circulatory, spine, immune, digestive, muscular
            include_details: Include detailed metrics

        Returns:
            System vitals dict or error
        """
        getter_name = self.SYSTEM_GETTERS.get(system_name)
        if not getter_name:
            return {'error': f"Unknown system: {system_name}", 'valid_systems': list(self.SYSTEM_GETTERS.keys())}

        try:
            getter = getattr(self, getter_name)
            return getter(include_details)
        except Exception as e:
            logger.error(f"Error getting {system_name} vitals: {e}")
            return {'status': 'error', 'score': 0, 'error': str(e)}

    def check_budget(self, estimated_tokens: int = 0, estimated_cost: float = 0) -> Dict[str, Any]:
        """
        Check if budget allows for an operation.

        Use this BEFORE expensive operations to avoid budget overruns.

        Args:
            estimated_tokens: Estimated token usage
            estimated_cost: Estimated cost in USD

        Returns:
            Budget check result with:
            - can_proceed: Whether operation should proceed
            - oxygen_level: Current budget % remaining
            - warning: Warning message if any
            - recommendation: Model selection advice
        """
        # Ensure type safety (tool arguments may come as strings)
        try:
            estimated_tokens = int(estimated_tokens) if estimated_tokens else 0
        except (ValueError, TypeError):
            estimated_tokens = 0
        try:
            estimated_cost = float(estimated_cost) if estimated_cost else 0.0
        except (ValueError, TypeError):
            estimated_cost = 0.0

        lungs_vitals = self._get_lungs_vitals(include_details=True)

        oxygen_level = lungs_vitals.get('oxygen_level', 100)
        can_proceed = oxygen_level > 10  # Always allow if > 10%

        # Check if this operation would exhaust budget
        details = lungs_vitals.get('details', {})
        if estimated_tokens > 0 or estimated_cost > 0:
            remaining_tokens = details.get('remaining_tokens', float('inf'))
            remaining_cost = details.get('remaining_cost', float('inf'))

            # Treat 0 as "no tracking" not "exhausted" (use oxygen_level for that)
            # Only block if we have real budget limits configured
            has_token_budget = remaining_tokens not in (0, float('inf'))
            has_cost_budget = remaining_cost not in (0, float('inf'))

            # Would this exhaust 90%+ of remaining budget?
            would_exhaust = (
                (has_token_budget and estimated_tokens > remaining_tokens * 0.9) or
                (has_cost_budget and estimated_cost > remaining_cost * 0.9)
            )
            if would_exhaust:
                can_proceed = False

        warning = None
        if not can_proceed:
            if oxygen_level <= 10:
                warning = 'Budget exhausted - operations blocked'
            else:
                warning = 'This operation would exhaust remaining budget'
        elif oxygen_level < 20:
            warning = 'Budget low - consider using efficient models'

        return {
            'can_proceed': can_proceed,
            'oxygen_level': oxygen_level,
            'status': lungs_vitals.get('status', 'unknown'),
            'warning': warning,
            'recommendation': self._get_budget_recommendation(oxygen_level),
            'estimated_tokens': estimated_tokens,
            'estimated_cost': estimated_cost
        }

    def get_alerts(self, severity_threshold: str = 'warning') -> List[Dict[str, Any]]:
        """
        Get all alerts above severity threshold.

        Args:
            severity_threshold: 'info', 'warning', or 'critical'

        Returns:
            List of alerts sorted by severity (highest first)
        """
        severity_scores = {'info': 1, 'warning': 2, 'critical': 3}
        threshold_score = severity_scores.get(severity_threshold, 2)

        all_vitals = self.get_all_vitals()
        alerts = all_vitals.get('alerts', [])

        filtered = [
            a for a in alerts
            if severity_scores.get(a.get('severity', 'info'), 1) >= threshold_score
        ]

        return filtered

    def get_quick_status(self) -> Dict[str, Any]:
        """
        Get a quick status summary (faster than full vitals).

        Returns minimal info for status bar display.
        """
        systems_summary = {}
        total_score = 0
        count = 0

        for system_name in self.SYSTEM_GETTERS.keys():
            try:
                vitals = self.get_system_vitals(system_name, include_details=False)
                systems_summary[system_name] = {
                    'emoji': vitals.get('emoji', '❓'),
                    'status': vitals.get('status', 'unknown'),
                    'score': vitals.get('score', 0)
                }
                total_score += vitals.get('score', 0)
                count += 1
            except Exception:
                systems_summary[system_name] = {'emoji': '❓', 'status': 'error', 'score': 0}

        avg_score = total_score / count if count > 0 else 0

        return {
            'overall_score': round(avg_score, 1),
            'overall_status': self._score_to_status(avg_score),
            'systems': systems_summary,
            'emoji_summary': ' '.join(s['emoji'] for s in systems_summary.values())
        }

    # ========== Individual System Getters ==========

    def _get_heart_vitals(self, include_details: bool = False) -> Dict[str, Any]:
        """Get HEART system vitals."""
        try:
            from core.services.heart import get_heart_monitor
            heart = get_heart_monitor()
            vitals = heart.get_vitals()

            status = vitals.get('overall_status', 'unknown')
            score = vitals.get('health_score', 0)

            result = {
                'status': status,
                'score': score,
                'emoji': self._get_emoji('heart', status),
                'alerts': []
            }

            # Generate alerts for degraded/critical status
            if status in ['critical', 'offline']:
                result['alerts'].append({
                    'system': 'heart',
                    'message': f"System health: {status}",
                    'severity': 'critical',
                    'severity_score': 3
                })
            elif status == 'degraded':
                result['alerts'].append({
                    'system': 'heart',
                    'message': f"System health degraded ({score}%)",
                    'severity': 'warning',
                    'severity_score': 2
                })

            if include_details:
                result['details'] = {
                    'components': vitals.get('components', {}),
                    'components_healthy': vitals.get('components_healthy', 0),
                    'components_degraded': vitals.get('components_degraded', 0),
                    'last_check': vitals.get('timestamp')
                }

            return result
        except Exception as e:
            logger.error(f"HEART vitals error: {e}")
            return {'status': 'error', 'score': 0, 'emoji': '❓', 'error': str(e), 'alerts': []}

    def _get_lungs_vitals(self, include_details: bool = False) -> Dict[str, Any]:
        """Get LUNGS system vitals."""
        try:
            from core.services.lungs import get_lungs_monitor
            lungs = get_lungs_monitor()
            vitals = lungs.get_vitals()

            oxygen_level = vitals.get('oxygen_level', 100)
            status = vitals.get('overall_status', 'unknown')

            result = {
                'status': status,
                'score': oxygen_level,
                'emoji': self._get_emoji('lungs', status),
                'oxygen_level': oxygen_level,
                'alerts': []
            }

            # Generate alerts for low budget
            if oxygen_level < 10:
                result['alerts'].append({
                    'system': 'lungs',
                    'message': f"Budget exhausted ({oxygen_level}% remaining)",
                    'severity': 'critical',
                    'severity_score': 3
                })
            elif oxygen_level < 20:
                result['alerts'].append({
                    'system': 'lungs',
                    'message': f"Budget low ({oxygen_level}% remaining)",
                    'severity': 'warning',
                    'severity_score': 2
                })

            if include_details:
                result['details'] = {
                    'respiratory_rate': vitals.get('respiratory_rate', 0),
                    'budgets': vitals.get('budgets', []),
                    'remaining_tokens': vitals.get('remaining_tokens', 0),
                    'remaining_cost': vitals.get('remaining_cost', 0),
                    'is_breathing': vitals.get('is_breathing', True)
                }

            return result
        except Exception as e:
            logger.error(f"LUNGS vitals error: {e}")
            return {'status': 'error', 'score': 0, 'emoji': '❓', 'error': str(e), 'alerts': []}

    def _get_circulatory_vitals(self, include_details: bool = False) -> Dict[str, Any]:
        """Get CIRCULATORY system vitals."""
        try:
            from core.services.circulatory import get_circulatory_system
            circ = get_circulatory_system()
            vitals = circ.get_vitals()

            status = vitals.get('overall_status', 'unknown')
            score = vitals.get('flow_score', 0)

            result = {
                'status': status,
                'score': score,
                'emoji': self._get_emoji('circulatory', status),
                'alerts': []
            }

            if status in ['congested', 'blocked']:
                result['alerts'].append({
                    'system': 'circulatory',
                    'message': f"Data flow: {status}",
                    'severity': 'critical' if status == 'blocked' else 'warning',
                    'severity_score': 3 if status == 'blocked' else 2
                })

            if include_details:
                result['details'] = {
                    'throughput': vitals.get('total_throughput', 0),
                    'items_in_transit': vitals.get('total_items_in_transit', 0),
                    'bottlenecks': vitals.get('bottlenecks', [])
                }

            return result
        except Exception as e:
            logger.error(f"CIRCULATORY vitals error: {e}")
            return {'status': 'error', 'score': 0, 'emoji': '❓', 'error': str(e), 'alerts': []}

    def _get_spine_vitals(self, include_details: bool = False) -> Dict[str, Any]:
        """Get SPINE system vitals."""
        try:
            from core.services.spine import get_spine_router
            spine = get_spine_router()
            vitals = spine.get_vitals()

            status = vitals.get('overall_status', 'unknown')
            score = vitals.get('health_score', 0)  # Session 712: Fixed field name

            result = {
                'status': status,
                'score': score,
                'emoji': self._get_emoji('spine', status),
                'alerts': []
            }

            if status in ['compressed', 'injured']:
                result['alerts'].append({
                    'system': 'spine',
                    'message': f"API routing: {status}",
                    'severity': 'critical' if status == 'injured' else 'warning',
                    'severity_score': 3 if status == 'injured' else 2
                })

            if include_details:
                result['details'] = {
                    'healthy_patterns': vitals.get('healthy_patterns', 0),
                    'degraded_patterns': vitals.get('degraded_patterns', 0),
                    'failed_patterns': vitals.get('failed_patterns', 0),
                    'heart_status': vitals.get('heart_status'),
                    'lungs_status': vitals.get('lungs_status'),
                    'circulatory_status': vitals.get('circulatory_status')
                }

            return result
        except Exception as e:
            logger.error(f"SPINE vitals error: {e}")
            return {'status': 'error', 'score': 0, 'emoji': '❓', 'error': str(e), 'alerts': []}

    def _get_immune_vitals(self, include_details: bool = False) -> Dict[str, Any]:
        """Get IMMUNE system vitals."""
        try:
            from core.services.immune import get_immune_system
            immune = get_immune_system()
            vitals = immune.get_vitals()

            status = vitals.get('overall_status', 'unknown')
            score = vitals.get('health_score', 0)  # Session 712: Fixed field name
            threat_level = vitals.get('threat_level', 'none')

            result = {
                'status': status,
                'score': score,
                'emoji': self._get_emoji('immune', status),
                'threat_level': threat_level,
                'alerts': []
            }

            if threat_level in ['high', 'severe']:
                result['alerts'].append({
                    'system': 'immune',
                    'message': f"Threat level: {threat_level}",
                    'severity': 'critical',
                    'severity_score': 3
                })
            elif threat_level == 'elevated':
                result['alerts'].append({
                    'system': 'immune',
                    'message': f"Threat level elevated",
                    'severity': 'warning',
                    'severity_score': 2
                })

            if include_details:
                result['details'] = {
                    'threats_detected_24h': vitals.get('threats_detected_24h', 0),
                    'threats_blocked_24h': vitals.get('threats_blocked_24h', 0),
                    'active_quarantines': vitals.get('active_quarantines', 0),
                    'false_positives_24h': vitals.get('false_positives_24h', 0)
                }

            return result
        except Exception as e:
            logger.error(f"IMMUNE vitals error: {e}")
            return {'status': 'error', 'score': 0, 'emoji': '❓', 'error': str(e), 'alerts': []}

    def _get_digestive_vitals(self, include_details: bool = False) -> Dict[str, Any]:
        """Get DIGESTIVE system vitals."""
        try:
            from core.services.digestive import get_digestive_system
            digestive = get_digestive_system()
            vitals = digestive.get_vitals()

            status = vitals.get('overall_status', 'unknown')
            score = vitals.get('digestion_score', 0)

            result = {
                'status': status,
                'score': score,
                'emoji': self._get_emoji('digestive', status),
                'alerts': []
            }

            if status in ['blocked', 'starving']:
                result['alerts'].append({
                    'system': 'digestive',
                    'message': f"Data pipeline: {status}",
                    'severity': 'critical',
                    'severity_score': 3
                })
            elif status == 'bloated':
                items_pending = vitals.get('items_pending', 0)
                result['alerts'].append({
                    'system': 'digestive',
                    'message': f"Queue backlog: {items_pending} items pending",
                    'severity': 'warning',
                    'severity_score': 2
                })

            if include_details:
                result['details'] = {
                    'items_pending': vitals.get('items_pending', 0),
                    'throughput': vitals.get('metabolism', {}).get('processing_rate', 0),
                    'intake_rate': vitals.get('metabolism', {}).get('intake_rate', 0),
                    'bottlenecks': vitals.get('bottlenecks', []),
                    'stages': vitals.get('stages', {})
                }

            return result
        except Exception as e:
            logger.error(f"DIGESTIVE vitals error: {e}")
            return {'status': 'error', 'score': 0, 'emoji': '❓', 'error': str(e), 'alerts': []}

    def _get_muscular_vitals(self, include_details: bool = False) -> Dict[str, Any]:
        """Get MUSCULAR system vitals."""
        try:
            from core.services.muscular import get_muscular_system
            muscular = get_muscular_system()
            vitals = muscular.get_vitals()

            status = vitals.get('overall_status', 'unknown')
            score = vitals.get('strength_score', 0)

            result = {
                'status': status,
                'score': score,
                'emoji': self._get_emoji('muscular', status),
                'alerts': []
            }

            if status in ['strained', 'paralyzed']:
                result['alerts'].append({
                    'system': 'muscular',
                    'message': f"Agent execution: {status}",
                    'severity': 'warning',
                    'severity_score': 2
                })

            if include_details:
                result['details'] = {
                    'success_rate_24h': vitals.get('success_rate_24h', 0),
                    'total_executions_24h': vitals.get('total_executions_24h', 0),
                    'active_agents': vitals.get('active_agents', 0),
                    'idle_agents': vitals.get('idle_agents', 0),
                    'weak_muscles': vitals.get('weak_muscles', []),
                    'overworked_muscles': vitals.get('overworked_muscles', [])
                }

            return result
        except Exception as e:
            logger.error(f"MUSCULAR vitals error: {e}")
            return {'status': 'error', 'score': 0, 'emoji': '❓', 'error': str(e), 'alerts': []}

    def _get_brain_vitals(self, include_details: bool = False) -> Dict[str, Any]:
        """Get BRAIN system vitals."""
        try:
            from core.services.brain import get_brain_service
            brain = get_brain_service()
            vitals = brain.get_vitals()

            # get_vitals() returns 'status', not 'overall_status'
            status = vitals.get('status', 'unknown')
            score = vitals.get('cognitive_score', 0)

            result = {
                'status': status,
                'score': score,
                'emoji': self._get_emoji('brain', status),
                'alerts': []
            }

            # Generate alerts based on cognitive status
            if status in ['overloaded', 'offline']:
                result['alerts'].append({
                    'system': 'brain',
                    'message': f"Cognitive processing: {status}",
                    'severity': 'critical',
                    'severity_score': 3
                })
            elif status == 'foggy':
                result['alerts'].append({
                    'system': 'brain',
                    'message': f"Cognitive clarity degraded ({score}%)",
                    'severity': 'warning',
                    'severity_score': 2
                })

            if include_details:
                result['details'] = {
                    'llm_calls_24h': vitals.get('llm_calls_24h', 0),
                    'tokens_total_24h': vitals.get('tokens_total_24h', 0),
                    'active_conversations': vitals.get('active_conversations', 0),
                    'agent_executions_24h': vitals.get('agent_executions_24h', 0),
                    'avg_response_time_ms': vitals.get('avg_response_time_ms', 0),
                    'cognitive_channels': vitals.get('cognitive_channels', {}),
                    'is_thinking': vitals.get('is_thinking', False)
                }

            return result
        except Exception as e:
            logger.error(f"BRAIN vitals error: {e}")
            return {'status': 'error', 'score': 0, 'emoji': '❓', 'error': str(e), 'alerts': []}

    def _get_skin_vitals(self, include_details: bool = False) -> Dict[str, Any]:
        """Get SKIN system vitals - project workspace health."""
        try:
            from core.services.skin import get_skin_service
            skin = get_skin_service()
            vitals = skin.get_vitals()

            status = vitals.get('status', 'unknown')
            score = vitals.get('health_score', 0)

            result = {
                'status': status,
                'score': score,
                'emoji': self._get_emoji('skin', status),
                'alerts': []
            }

            # Generate alerts based on skin status
            if status in ['damaged', 'irritated']:
                result['alerts'].append({
                    'system': 'skin',
                    'message': f"Workspace health: {status}",
                    'severity': 'critical' if status == 'damaged' else 'warning',
                    'severity_score': 3 if status == 'damaged' else 2
                })
            elif status == 'healing':
                result['alerts'].append({
                    'system': 'skin',
                    'message': "Rollback operations in progress",
                    'severity': 'info',
                    'severity_score': 1
                })

            if include_details:
                result['details'] = {
                    'total_workspaces': vitals.get('total_workspaces', 0),
                    'active_workspaces': vitals.get('active_workspaces', 0),
                    'operations_24h': vitals.get('operations_24h', 0),
                    'success_rate_24h': vitals.get('success_rate_24h', 100),
                    'activity_level': vitals.get('activity_level', 'unknown'),
                    'ops_per_hour': vitals.get('ops_per_hour', 0),
                    'last_operation': vitals.get('last_operation')
                }

            return result
        except Exception as e:
            logger.error(f"SKIN vitals error: {e}")
            return {'status': 'error', 'score': 0, 'emoji': '❓', 'error': str(e), 'alerts': []}

    def _get_nervous_vitals(self, include_details: bool = False) -> Dict[str, Any]:
        """Get NERVOUS system vitals - WebSocket communication health."""
        try:
            from core.services.nervous import get_nervous_service
            nervous = get_nervous_service()
            vitals = nervous.get_vitals()

            status = vitals.get('status', 'unknown')
            score = vitals.get('health_score', 0)

            result = {
                'status': status,
                'score': score,
                'emoji': self._get_emoji('nervous', status),
                'alerts': []
            }

            # Generate alerts based on nervous status
            if status in ['damaged', 'numb', 'overloaded']:
                result['alerts'].append({
                    'system': 'nervous',
                    'message': f"WebSocket communication: {status}",
                    'severity': 'critical' if status == 'damaged' else 'warning',
                    'severity_score': 3 if status == 'damaged' else 2
                })
            elif status == 'sluggish':
                result['alerts'].append({
                    'system': 'nervous',
                    'message': "WebSocket communication is sluggish",
                    'severity': 'warning',
                    'severity_score': 2
                })

            # Alert if channel layer is disconnected
            if not vitals.get('channel_layer_healthy', True):
                result['alerts'].append({
                    'system': 'nervous',
                    'message': "Redis channel layer disconnected - WebSockets not working",
                    'severity': 'critical',
                    'severity_score': 3
                })

            if include_details:
                result['details'] = {
                    'active_connections': vitals.get('active_connections', 0),
                    'messages_per_second': vitals.get('messages_per_second', 0),
                    'channel_layer_healthy': vitals.get('channel_layer_healthy', False),
                }

            return result
        except Exception as e:
            logger.error(f"NERVOUS vitals error: {e}")
            return {'status': 'error', 'score': 0, 'emoji': '❓', 'error': str(e), 'alerts': []}

    # ========== Helper Methods ==========

    def _get_emoji(self, system: str, status: str) -> str:
        """Get emoji for system status."""
        system_emojis = self.EMOJI_MAP.get(system, {})
        return system_emojis.get(status, system_emojis.get('unknown', '❓'))

    def _score_to_status(self, score: float) -> str:
        """Convert score to overall status."""
        if score >= 80:
            return 'healthy'
        elif score >= 60:
            return 'degraded'
        elif score >= 40:
            return 'impaired'
        elif score >= 20:
            return 'critical'
        else:
            return 'failing'

    def _generate_recommendation(self, systems: Dict, alerts: List) -> str:
        """Generate actionable recommendation based on current status."""
        critical_systems = [
            s for s, v in systems.items()
            if v.get('score', 100) < 40 and v.get('status') != 'error'
        ]

        if not critical_systems and not alerts:
            return "All systems operating normally"

        if not critical_systems:
            return f"{len(alerts)} alerts detected - review body health dashboard"

        # Prioritized recommendations
        if 'brain' in critical_systems:
            return "Cognitive processing overloaded - reduce LLM calls or check conversation queue"
        if 'lungs' in critical_systems:
            return "Budget is critically low - reduce LLM usage or increase budget limits"
        if 'immune' in critical_systems:
            return "Security threats detected - review quarantine and threat logs immediately"
        if 'heart' in critical_systems:
            return "Core components unhealthy - check service status and restart failing services"
        if 'digestive' in critical_systems:
            return "Data pipeline blocked - check Celery workers and spider health"
        if 'spine' in critical_systems:
            return "API routing degraded - review error rates and latency metrics"
        if 'muscular' in critical_systems:
            return "Agent execution issues - run some agent tasks to warm up the system"
        if 'circulatory' in critical_systems:
            return "Data flow issues - check Redis and Celery queue depths"

        return f"Attention needed: {', '.join(critical_systems)}"

    def _get_budget_recommendation(self, oxygen_level: float) -> str:
        """Get recommendation based on budget level."""
        if oxygen_level >= 80:
            return "Budget healthy - proceed with any operations"
        elif oxygen_level >= 50:
            return "Budget moderate - avoid very expensive operations (video generation, large batches)"
        elif oxygen_level >= 20:
            return "Budget low - use efficient models (GPT-4o-mini, Haiku, DeepSeek)"
        elif oxygen_level >= 10:
            return "Budget critical - only essential operations, use cheapest models"
        else:
            return "Budget exhausted - operations should be blocked until budget reset"
