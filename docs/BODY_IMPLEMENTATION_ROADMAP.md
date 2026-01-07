# Body Implementation Roadmap - Phased Implementation Plan

**Created:** Session 708 (January 7, 2026)
**Purpose:** Step-by-step implementation guide to complete the body architecture
**Current Status:** 55% Complete → Target: 95%

---

## Overview

This roadmap outlines the phased implementation to complete the body architecture integration. Each phase builds on the previous, with clear deliverables and success criteria.

```
Phase 1: Brain ↔ Body Connection     [Session 709]    ~4 hours
Phase 2: Attention System Integration [Session 709]    ~2 hours
Phase 3: User Dashboard               [Session 710]    ~6 hours
Phase 4: Body Coordination            [Session 711]    ~4 hours
Phase 5: Feedback Loops               [Session 712]    ~4 hours
Phase 6: Polish & Testing             [Session 712]    ~2 hours
```

---

## Phase 1: Connect Brain to Body (P0 - CRITICAL)

**Goal:** Give the Personal Assistant awareness of body health

### Step 1.1: Create Body Vitals Service

**File:** `core/services/body_vitals.py`

```python
"""
Body Vitals Service - Unified query for all body systems
Session 709: Connect Brain to Body
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Singleton instance
_body_vitals_instance = None


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
    """

    SYSTEM_GETTERS = {
        'heart': '_get_heart_vitals',
        'lungs': '_get_lungs_vitals',
        'circulatory': '_get_circulatory_vitals',
        'spine': '_get_spine_vitals',
        'immune': '_get_immune_vitals',
        'digestive': '_get_digestive_vitals',
        'muscular': '_get_muscular_vitals',
    }

    STATUS_WEIGHTS = {
        'heart': 1.5,      # Critical - affects everything
        'lungs': 1.3,      # Important - budget
        'circulatory': 1.0,
        'spine': 1.2,      # Important - routing
        'immune': 1.2,     # Important - security
        'digestive': 1.0,
        'muscular': 1.0,
    }

    def get_all_vitals(self, include_details: bool = False) -> Dict[str, Any]:
        """
        Get health status from all 7 body systems.

        Args:
            include_details: Include detailed metrics per system

        Returns:
            Unified health report
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
                total_weighted_score += vitals['score'] * weight
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
                    'error': str(e)
                }

        # Calculate overall health
        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0
        overall_status = self._score_to_status(overall_score)

        duration_ms = (datetime.now() - start).total_seconds() * 1000

        return {
            'timestamp': datetime.now().isoformat(),
            'overall_health': overall_status,
            'health_score': round(overall_score, 1),
            'systems': systems,
            'alerts': sorted(alerts, key=lambda x: x.get('severity_score', 0), reverse=True),
            'check_duration_ms': round(duration_ms, 2),
            'recommendation': self._generate_recommendation(systems, alerts)
        }

    def check_budget(self, estimated_tokens: int = 0, estimated_cost: float = 0) -> Dict[str, Any]:
        """
        Check if budget allows for an operation.

        Args:
            estimated_tokens: Estimated token usage
            estimated_cost: Estimated cost in USD

        Returns:
            Budget check result with recommendation
        """
        lungs_vitals = self._get_lungs_vitals(include_details=True)

        oxygen_level = lungs_vitals.get('oxygen_level', 100)
        can_proceed = oxygen_level > 10  # Always allow if > 10%

        # Check if this operation would exhaust budget
        if estimated_tokens > 0 or estimated_cost > 0:
            remaining_tokens = lungs_vitals.get('details', {}).get('remaining_tokens', float('inf'))
            remaining_cost = lungs_vitals.get('details', {}).get('remaining_cost', float('inf'))

            would_exhaust = (
                estimated_tokens > remaining_tokens * 0.9 or
                estimated_cost > remaining_cost * 0.9
            )
            if would_exhaust:
                can_proceed = False

        return {
            'can_proceed': can_proceed,
            'oxygen_level': oxygen_level,
            'status': lungs_vitals['status'],
            'warning': None if can_proceed else 'Budget too low for this operation',
            'recommendation': self._get_budget_recommendation(oxygen_level)
        }

    def get_alerts(self, severity_threshold: str = 'warning') -> List[Dict[str, Any]]:
        """
        Get all alerts above severity threshold.

        Args:
            severity_threshold: 'info', 'warning', or 'critical'

        Returns:
            List of alerts sorted by severity
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

    def _get_heart_vitals(self, include_details: bool = False) -> Dict[str, Any]:
        """Get HEART system vitals."""
        try:
            from core.services.heart import get_heart_monitor
            heart = get_heart_monitor()
            vitals = heart.get_vitals()

            result = {
                'status': vitals.get('overall_status', 'unknown'),
                'score': vitals.get('health_score', 0),
                'emoji': self._status_to_emoji('heart', vitals.get('overall_status')),
                'alerts': []
            }

            if vitals.get('overall_status') in ['critical', 'offline']:
                result['alerts'].append({
                    'system': 'heart',
                    'message': f"System health: {vitals.get('overall_status')}",
                    'severity': 'critical',
                    'severity_score': 3
                })

            if include_details:
                result['details'] = {
                    'components': vitals.get('components', {}),
                    'last_check': vitals.get('timestamp')
                }

            return result
        except Exception as e:
            return {'status': 'error', 'score': 0, 'emoji': '❓', 'error': str(e), 'alerts': []}

    def _get_lungs_vitals(self, include_details: bool = False) -> Dict[str, Any]:
        """Get LUNGS system vitals."""
        try:
            from core.services.lungs import get_lungs_capacity
            lungs = get_lungs_capacity()
            vitals = lungs.get_vitals()

            oxygen_level = vitals.get('oxygen_level', 100)
            status = vitals.get('overall_status', 'unknown')

            result = {
                'status': status,
                'score': oxygen_level,
                'emoji': self._status_to_emoji('lungs', status),
                'oxygen_level': oxygen_level,
                'alerts': []
            }

            if oxygen_level < 20:
                result['alerts'].append({
                    'system': 'lungs',
                    'message': f"Budget at {oxygen_level}%",
                    'severity': 'critical' if oxygen_level < 10 else 'warning',
                    'severity_score': 3 if oxygen_level < 10 else 2
                })

            if include_details:
                result['details'] = {
                    'respiratory_rate': vitals.get('respiratory_rate', 0),
                    'budgets': vitals.get('budgets', []),
                    'remaining_tokens': vitals.get('remaining_tokens', 0),
                    'remaining_cost': vitals.get('remaining_cost', 0)
                }

            return result
        except Exception as e:
            return {'status': 'error', 'score': 0, 'emoji': '❓', 'error': str(e), 'alerts': []}

    def _get_circulatory_vitals(self, include_details: bool = False) -> Dict[str, Any]:
        """Get CIRCULATORY system vitals."""
        try:
            from core.services.circulatory import get_circulatory_system
            circ = get_circulatory_system()
            vitals = circ.get_vitals()

            result = {
                'status': vitals.get('overall_status', 'unknown'),
                'score': vitals.get('flow_score', 0),
                'emoji': self._status_to_emoji('circulatory', vitals.get('overall_status')),
                'alerts': []
            }

            if vitals.get('overall_status') in ['congested', 'blocked']:
                result['alerts'].append({
                    'system': 'circulatory',
                    'message': f"Data flow: {vitals.get('overall_status')}",
                    'severity': 'warning',
                    'severity_score': 2
                })

            if include_details:
                result['details'] = {
                    'throughput': vitals.get('total_throughput', 0),
                    'bottlenecks': vitals.get('bottlenecks', [])
                }

            return result
        except Exception as e:
            return {'status': 'error', 'score': 0, 'emoji': '❓', 'error': str(e), 'alerts': []}

    def _get_spine_vitals(self, include_details: bool = False) -> Dict[str, Any]:
        """Get SPINE system vitals."""
        try:
            from core.services.spine import get_spine_router
            spine = get_spine_router()
            vitals = spine.get_vitals()

            result = {
                'status': vitals.get('overall_status', 'unknown'),
                'score': vitals.get('alignment_score', 0),
                'emoji': self._status_to_emoji('spine', vitals.get('overall_status')),
                'alerts': []
            }

            if vitals.get('overall_status') in ['compressed', 'injured']:
                result['alerts'].append({
                    'system': 'spine',
                    'message': f"API routing: {vitals.get('overall_status')}",
                    'severity': 'warning',
                    'severity_score': 2
                })

            if include_details:
                result['details'] = {
                    'healthy_patterns': vitals.get('healthy_patterns', 0),
                    'degraded_patterns': vitals.get('degraded_patterns', 0),
                    'failed_patterns': vitals.get('failed_patterns', 0)
                }

            return result
        except Exception as e:
            return {'status': 'error', 'score': 0, 'emoji': '❓', 'error': str(e), 'alerts': []}

    def _get_immune_vitals(self, include_details: bool = False) -> Dict[str, Any]:
        """Get IMMUNE system vitals."""
        try:
            from core.services.immune import get_immune_system
            immune = get_immune_system()
            vitals = immune.get_vitals()

            result = {
                'status': vitals.get('overall_status', 'unknown'),
                'score': vitals.get('immune_score', 0),
                'emoji': self._status_to_emoji('immune', vitals.get('overall_status')),
                'threat_level': vitals.get('threat_level', 'none'),
                'alerts': []
            }

            if vitals.get('threat_level') in ['high', 'severe']:
                result['alerts'].append({
                    'system': 'immune',
                    'message': f"Threat level: {vitals.get('threat_level')}",
                    'severity': 'critical',
                    'severity_score': 3
                })

            if include_details:
                result['details'] = {
                    'threats_detected_24h': vitals.get('threats_detected_24h', 0),
                    'threats_blocked_24h': vitals.get('threats_blocked_24h', 0),
                    'active_quarantines': vitals.get('active_quarantines', 0)
                }

            return result
        except Exception as e:
            return {'status': 'error', 'score': 0, 'emoji': '❓', 'error': str(e), 'alerts': []}

    def _get_digestive_vitals(self, include_details: bool = False) -> Dict[str, Any]:
        """Get DIGESTIVE system vitals."""
        try:
            from core.services.digestive import get_digestive_system
            digestive = get_digestive_system()
            vitals = digestive.get_vitals()

            result = {
                'status': vitals.get('overall_status', 'unknown'),
                'score': vitals.get('digestion_score', 0),
                'emoji': self._status_to_emoji('digestive', vitals.get('overall_status')),
                'alerts': []
            }

            if vitals.get('overall_status') in ['blocked', 'starving']:
                result['alerts'].append({
                    'system': 'digestive',
                    'message': f"Data pipeline: {vitals.get('overall_status')}",
                    'severity': 'critical',
                    'severity_score': 3
                })
            elif vitals.get('overall_status') == 'bloated':
                result['alerts'].append({
                    'system': 'digestive',
                    'message': f"Queue backlog: {vitals.get('items_pending', 0)} items",
                    'severity': 'warning',
                    'severity_score': 2
                })

            if include_details:
                result['details'] = {
                    'items_pending': vitals.get('items_pending', 0),
                    'throughput': vitals.get('processing_rate', 0),
                    'bottlenecks': vitals.get('bottlenecks', [])
                }

            return result
        except Exception as e:
            return {'status': 'error', 'score': 0, 'emoji': '❓', 'error': str(e), 'alerts': []}

    def _get_muscular_vitals(self, include_details: bool = False) -> Dict[str, Any]:
        """Get MUSCULAR system vitals."""
        try:
            from core.services.muscular import get_muscular_system
            muscular = get_muscular_system()
            vitals = muscular.get_vitals()

            result = {
                'status': vitals.get('overall_status', 'unknown'),
                'score': vitals.get('strength_score', 0),
                'emoji': self._status_to_emoji('muscular', vitals.get('overall_status')),
                'alerts': []
            }

            if vitals.get('overall_status') in ['strained', 'paralyzed']:
                result['alerts'].append({
                    'system': 'muscular',
                    'message': f"Agent execution: {vitals.get('overall_status')}",
                    'severity': 'warning',
                    'severity_score': 2
                })

            if include_details:
                result['details'] = {
                    'success_rate_24h': vitals.get('success_rate_24h', 0),
                    'active_agents': vitals.get('active_agents', 0),
                    'weak_muscles': vitals.get('weak_muscles', []),
                    'overworked_muscles': vitals.get('overworked_muscles', [])
                }

            return result
        except Exception as e:
            return {'status': 'error', 'score': 0, 'emoji': '❓', 'error': str(e), 'alerts': []}

    def _status_to_emoji(self, system: str, status: str) -> str:
        """Get emoji for system status."""
        emoji_map = {
            'heart': {'healthy': '❤️', 'degraded': '💛', 'critical': '🧡', 'offline': '🖤'},
            'lungs': {'normal': '🫁', 'elevated': '😤', 'hyperventilating': '🥵', 'holding': '🚫'},
            'circulatory': {'flowing': '🩸', 'slow': '🐌', 'congested': '⚠️', 'blocked': '🚫'},
            'spine': {'aligned': '🦴', 'strained': '⚡', 'compressed': '🔧', 'injured': '🚨'},
            'immune': {'healthy': '🛡️', 'alert': '⚠️', 'fighting': '⚔️', 'overwhelmed': '🔥', 'compromised': '💀'},
            'digestive': {'healthy': '🍽️', 'sluggish': '🐌', 'bloated': '🎈', 'blocked': '🚫', 'starving': '💀'},
            'muscular': {'strong': '💪', 'fit': '🏃', 'fatigued': '😓', 'strained': '🥵', 'paralyzed': '🦽'},
        }
        return emoji_map.get(system, {}).get(status, '❓')

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
        """Generate actionable recommendation based on status."""
        critical_systems = [s for s, v in systems.items() if v.get('score', 100) < 40]

        if not critical_systems:
            return "All systems operating normally"

        if 'lungs' in critical_systems:
            return "Budget is low - consider reducing LLM usage or increasing limits"
        if 'immune' in critical_systems:
            return "Security threats detected - review quarantine and threat logs"
        if 'digestive' in critical_systems:
            return "Data pipeline blocked - check Celery workers and spider health"
        if 'muscular' in critical_systems:
            return "Agent execution issues - run some agent tasks to warm up the system"
        if 'heart' in critical_systems:
            return "Core components unhealthy - check service status and logs"

        return f"Attention needed: {', '.join(critical_systems)}"

    def _get_budget_recommendation(self, oxygen_level: float) -> str:
        """Get recommendation based on budget level."""
        if oxygen_level >= 80:
            return "Budget healthy - proceed with operations"
        elif oxygen_level >= 50:
            return "Budget moderate - avoid very expensive operations"
        elif oxygen_level >= 20:
            return "Budget low - use efficient models (Haiku, GPT-4o-mini)"
        elif oxygen_level >= 10:
            return "Budget critical - only essential operations"
        else:
            return "Budget exhausted - operations blocked"
```

### Step 1.2: Add Tool Definitions

**File:** `core/assistant/tool_definitions.py` (add to end)

```python
def _get_body_vitals_tool_definition() -> Dict:
    """Tool for PA to query body system health."""
    return {
        "type": "function",
        "name": "get_body_vitals",
        "description": get_tool_description("get_body_vitals"),
        "parameters": {
            "type": "object",
            "properties": {
                "systems": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["heart", "lungs", "circulatory", "spine", "immune", "digestive", "muscular", "all"]
                    },
                    "description": "Which body systems to query. Use 'all' for complete health check."
                },
                "include_details": {
                    "type": "boolean",
                    "description": "Include detailed metrics per system"
                }
            },
            "required": []
        }
    }


def _get_check_budget_tool_definition() -> Dict:
    """Tool for PA to check budget before expensive operations."""
    return {
        "type": "function",
        "name": "check_resource_budget",
        "description": get_tool_description("check_resource_budget"),
        "parameters": {
            "type": "object",
            "properties": {
                "estimated_tokens": {
                    "type": "integer",
                    "description": "Estimated token usage for the operation"
                },
                "estimated_cost": {
                    "type": "number",
                    "description": "Estimated cost in USD for the operation"
                }
            },
            "required": []
        }
    }


def _get_system_alerts_tool_definition() -> Dict:
    """Tool for PA to get critical system alerts."""
    return {
        "type": "function",
        "name": "get_system_alerts",
        "description": get_tool_description("get_system_alerts"),
        "parameters": {
            "type": "object",
            "properties": {
                "severity_threshold": {
                    "type": "string",
                    "enum": ["info", "warning", "critical"],
                    "description": "Minimum severity level to include"
                }
            },
            "required": []
        }
    }
```

### Step 1.3: Add Tool Descriptions

**File:** `core/prompts/tool_descriptions.py` (add entries)

```python
TOOL_DESCRIPTIONS = {
    # ... existing descriptions ...

    "get_body_vitals": """Query the health status of body systems (HEART, LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR).

Use this tool when:
- User asks about system health or status
- Before executing expensive operations (check LUNGS budget)
- When troubleshooting issues (check relevant systems)
- For proactive health awareness

The response includes:
- Overall health score (0-100%)
- Per-system status with emoji indicators
- Active alerts and their severity
- Actionable recommendations""",

    "check_resource_budget": """Check if the current budget allows for an operation.

Use this tool BEFORE:
- Large image/video generation requests
- Complex multi-step workflows
- Operations requiring expensive models (GPT-5, Claude Opus)

The response tells you:
- Whether to proceed (can_proceed: true/false)
- Current oxygen level (budget %)
- Warning message if budget is low
- Recommendation for model selection""",

    "get_system_alerts": """Get active alerts from all body systems.

Use this tool when:
- User asks "what needs attention?"
- Starting a new session (quick health check)
- Something seems wrong with the system

Returns alerts sorted by severity with:
- Which system raised the alert
- What the issue is
- Severity (info/warning/critical)""",
}
```

### Step 1.4: Register Tools in get_tool_definitions()

**File:** `core/assistant/tool_definitions.py` (modify function)

```python
def get_tool_definitions() -> List[Dict]:
    return [
        # ... existing tools ...
        _get_body_vitals_tool_definition(),         # Session 709: Body awareness
        _get_check_budget_tool_definition(),        # Session 709: Budget checking
        _get_system_alerts_tool_definition(),       # Session 709: Alert awareness
        _get_workflow_orchestration_agent_definition(),  # Keep last
    ]
```

### Step 1.5: Implement Tool Handlers

**File:** `core/personal_ai_assistant_enhanced.py` (add handlers)

```python
def _handle_get_body_vitals(self, args: dict) -> dict:
    """Handle get_body_vitals tool call."""
    from core.services.body_vitals import get_body_vitals_service
    service = get_body_vitals_service()

    systems = args.get('systems', ['all'])
    include_details = args.get('include_details', False)

    if 'all' in systems:
        return service.get_all_vitals(include_details=include_details)
    else:
        # Query specific systems
        result = {'systems': {}, 'alerts': []}
        for system in systems:
            getter = getattr(service, f'_get_{system}_vitals', None)
            if getter:
                result['systems'][system] = getter(include_details)
        return result


def _handle_check_resource_budget(self, args: dict) -> dict:
    """Handle check_resource_budget tool call."""
    from core.services.body_vitals import get_body_vitals_service
    service = get_body_vitals_service()

    return service.check_budget(
        estimated_tokens=args.get('estimated_tokens', 0),
        estimated_cost=args.get('estimated_cost', 0)
    )


def _handle_get_system_alerts(self, args: dict) -> dict:
    """Handle get_system_alerts tool call."""
    from core.services.body_vitals import get_body_vitals_service
    service = get_body_vitals_service()

    return {
        'alerts': service.get_alerts(
            severity_threshold=args.get('severity_threshold', 'warning')
        )
    }
```

### Success Criteria - Phase 1

- [ ] `core/services/body_vitals.py` created
- [ ] 3 new tools added to tool_definitions.py
- [ ] Tool descriptions added to prompts
- [ ] Tool handlers implemented in PA
- [ ] PA can successfully call `get_body_vitals`
- [ ] PA can check budget before expensive operations
- [ ] PA can get system alerts

---

## Phase 2: Attention System Integration (P0)

**Goal:** Make body alerts visible in SystemStateAggregator

### Step 2.1: Add Body Items to Aggregator

**File:** `core/services/system_state_aggregator.py` (add method)

```python
def _get_body_system_items(self) -> List[AttentionItem]:
    """Get attention items from body systems (Session 709)."""
    items = []

    try:
        from core.services.body_vitals import get_body_vitals_service
        vitals_service = get_body_vitals_service()
        all_vitals = vitals_service.get_all_vitals()

        for alert in all_vitals.get('alerts', []):
            severity = alert.get('severity', 'info')
            system = alert.get('system', 'unknown')

            # Map severity to priority
            priority = {
                'critical': PRIORITY_SCORES['critical_alert'],
                'warning': PRIORITY_SCORES['health_failure'],
                'info': PRIORITY_SCORES['informational']
            }.get(severity, PRIORITY_SCORES['informational'])

            items.append(AttentionItem(
                id=f"body_{system}_{hash(alert.get('message', ''))}",
                section='body_systems',
                category='health_failure' if severity == 'critical' else 'health',
                priority=priority,
                title=f"{system.upper()}: {alert.get('message', 'Issue detected')}",
                summary=alert.get('message', ''),
                explanation=f"Body system {system} reported an issue",
                recommended_action=f"Check Body Health Dashboard > {system.upper()}",
                severity=severity,
                location=f"Body Health > {system.upper()}"
            ))
    except Exception as e:
        self.logger.error(f"Error getting body system items: {e}")

    return items
```

### Step 2.2: Call Method in get_attention_items

**File:** `core/services/system_state_aggregator.py` (modify)

```python
def get_attention_items(self, max_per_section: int = 5, force_refresh: bool = False):
    # ... existing code ...

    try:
        items.extend(self._get_body_system_items())  # Session 709
    except Exception as e:
        self.logger.error(f"Error getting Body System items: {e}")

    # ... rest of code ...
```

### Success Criteria - Phase 2

- [ ] `_get_body_system_items` method added
- [ ] Method called in `get_attention_items`
- [ ] Body alerts appear in attention items
- [ ] SystemIntelligenceAgent can see body health

---

## Phase 3: User Dashboard (P1)

**Goal:** Create frontend Body Health Dashboard

### Files to Create

| File | Purpose |
|------|---------|
| `frontend/src/pages/BodyHealthPage.tsx` | Main dashboard page |
| `frontend/src/components/body/BodySystemCard.tsx` | Individual system card |
| `frontend/src/components/body/BodyStatusSummary.tsx` | Header summary |
| `frontend/src/hooks/useBodyHealth.ts` | Data fetching hook |
| `frontend/src/api/body.ts` | API client functions |

### API Endpoint

**File:** `core/views_body.py` (create)

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.services.body_vitals import get_body_vitals_service


@api_view(['GET'])
def body_status(request):
    """Get unified body health status."""
    service = get_body_vitals_service()
    include_details = request.GET.get('details', 'false').lower() == 'true'
    return Response(service.get_all_vitals(include_details=include_details))
```

### Add Route

**File:** `core/urls.py` (add)

```python
path('api/body/status/', views_body.body_status, name='body_status'),
```

### Success Criteria - Phase 3

- [ ] `/api/body/status/` endpoint working
- [ ] BodyHealthPage component created
- [ ] 7 BodySystemCard components render
- [ ] Real-time updates via polling (5s)
- [ ] Click system card → detailed view
- [ ] Route added to React router

---

## Phase 4: Body Coordination (P1)

**Goal:** Enable cross-system coordination

### Create Body Coordinator

**File:** `core/services/body_coordinator.py`

```python
"""
Body Coordinator - Orchestrates responses across body systems
Session 711: Body ↔ Body coordination
"""

class BodyCoordinator:
    """Coordinates responses across body systems."""

    def __init__(self):
        self.intervention_log = []

    def check_all_and_respond(self) -> dict:
        """Run all checks and take coordinated action."""
        from core.services.body_vitals import get_body_vitals_service
        vitals = get_body_vitals_service().get_all_vitals()

        responses = []

        # Check LUNGS → Throttle if needed
        lungs = vitals['systems'].get('lungs', {})
        if lungs.get('score', 100) < 10:
            responses.append(self._throttle_operations())

        # Check IMMUNE → Alert if threats
        immune = vitals['systems'].get('immune', {})
        if immune.get('threat_level') in ['high', 'severe']:
            responses.append(self._alert_security_threat(immune))

        # Check DIGESTIVE → Pause spiders if blocked
        digestive = vitals['systems'].get('digestive', {})
        if digestive.get('status') == 'blocked':
            responses.append(self._pause_spider_execution())

        return {
            'vitals': vitals,
            'responses': responses,
            'intervention_count': len(responses)
        }

    def _throttle_operations(self) -> dict:
        """Enable throttle mode when budget exhausted."""
        # Implementation
        return {'action': 'throttle', 'status': 'enabled'}

    def _alert_security_threat(self, immune_status: dict) -> dict:
        """Send alert for security threats."""
        # Implementation - Discord notification
        return {'action': 'security_alert', 'status': 'sent'}

    def _pause_spider_execution(self) -> dict:
        """Pause spider execution when pipeline blocked."""
        # Implementation
        return {'action': 'pause_spiders', 'status': 'paused'}
```

### Add Celery Task

**File:** `core/tasks.py` (add)

```python
@shared_task(name='core.tasks.coordinate_body_systems')
def coordinate_body_systems():
    """Session 711: Run body coordination check."""
    from core.services.body_coordinator import BodyCoordinator
    coordinator = BodyCoordinator()
    return coordinator.check_all_and_respond()
```

### Add Beat Schedule

**File:** `core/celery.py` (add)

```python
'body-coordination': {
    'task': 'core.tasks.coordinate_body_systems',
    'schedule': 120.0,  # Every 2 minutes
},
```

### Success Criteria - Phase 4

- [ ] BodyCoordinator service created
- [ ] Celery task registered
- [ ] Beat schedule added
- [ ] Throttle works when LUNGS < 10%
- [ ] Security alerts sent when IMMUNE high

---

## Phase 5: Feedback Loops (P2)

**Goal:** Implement automatic responses

### Implementation Details

See [BODY_INTEGRATION_GAPS.md](./BODY_INTEGRATION_GAPS.md) Gap 5 for full specification.

Key feedback loops:
1. LUNGS exhausted → Throttle PA
2. HEART critical → User notification
3. IMMUNE threat → SPINE reroute
4. DIGESTIVE blocked → Pause spiders
5. MUSCULAR strained → Reduce agent routing

---

## Phase 6: Polish & Testing (P2)

### Tasks

1. Add unit tests for BodyVitalsService
2. Add integration tests for tool handlers
3. Add frontend component tests
4. Performance optimization (caching)
5. Documentation updates
6. Error handling improvements

---

## Timeline Summary

| Phase | Sessions | Duration | Dependencies |
|-------|----------|----------|--------------|
| 1 | 709 | ~4 hours | None |
| 2 | 709 | ~2 hours | Phase 1 |
| 3 | 710 | ~6 hours | Phase 1, 2 |
| 4 | 711 | ~4 hours | Phase 1 |
| 5 | 712 | ~4 hours | Phase 4 |
| 6 | 712 | ~2 hours | All |

**Total: ~22 hours across 4 sessions**

---

## Quick Reference Commands

```bash
# Test body vitals service
python manage.py shell -c "
from core.services.body_vitals import get_body_vitals_service
service = get_body_vitals_service()
print(service.get_all_vitals())
"

# Test unified endpoint
curl http://localhost:8000/api/body/status/

# Run body coordination
python manage.py shell -c "
from core.tasks import coordinate_body_systems
result = coordinate_body_systems()
print(result)
"
```

---

## Related Documentation

- [BODY_ARCHITECTURE.md](./BODY_ARCHITECTURE.md) - System overview
- [BODY_SYSTEMS_REFERENCE.md](./BODY_SYSTEMS_REFERENCE.md) - Technical reference
- [BODY_INTEGRATION_GAPS.md](./BODY_INTEGRATION_GAPS.md) - Complete gap analysis
