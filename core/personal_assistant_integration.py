"""
Personal Assistant Self-Awareness Integration
==============================================

This module integrates the Personal Assistant with the System Reality Self-Awareness Engine,
enabling the assistant to understand the platform's operational state and provide accurate
information about what's real vs simulated.
"""

import logging
from datetime import datetime, timezone as tz
from typing import Dict, Any, List

from core.reality_check import (
    SystemRealityChecker,
    RealityStatus,
    ComponentType,
    ComponentRealityStatus
)
from core.component_pipelines import ComponentDataPipeline

logger = logging.getLogger(__name__)


class PersonalAssistantIntegration:
    """
    Integrates Personal Assistant with the System Self-Awareness Engine
    to provide reality-aware responses and system insights.
    """

    def __init__(self):
        self.reality_checker = SystemRealityChecker()
        self.pipeline_manager = ComponentDataPipeline()
        self.context_cache = {}
        self.last_reality_check = None
        self.reality_check_interval = 60  # seconds
        self._cached_statuses = None

    def enhance_assistant_context(self, message: str, conversation_id: str) -> Dict[str, Any]:
        """
        Enhance the assistant's context with reality awareness and system status.

        Args:
            message: User's message to the assistant
            conversation_id: Current conversation ID

        Returns:
            Enhanced context with system awareness
        """
        context = {
            'message': message,
            'conversation_id': conversation_id,
            'timestamp': datetime.now(tz.utc).isoformat(),
            'system_awareness': self._get_system_awareness(),
            'component_status': self._get_component_status(),
            'data_flow_status': self._get_data_flow_status(),
            'recommendations': self._get_system_recommendations(message)
        }

        # Add intelligent routing based on message content
        context['routing'] = self._determine_routing(message)

        return context

    def _get_system_awareness(self) -> Dict[str, Any]:
        """Get current system awareness status"""
        # Check if we need to refresh reality check
        if self._should_refresh_reality_check():
            self._refresh_reality_status()

        return {
            'platform_reality': self._get_platform_reality_summary(),
            'operational_percentage': self._calculate_operational_percentage(),
            'mock_components': self._identify_mock_components(),
            'real_components': self._identify_real_components(),
            'broken_flows': self._identify_broken_flows()
        }

    def _get_component_status(self) -> Dict[str, Any]:
        """Get detailed status of all components"""
        components = {}

        # Get all component statuses at once
        all_statuses = self.reality_checker.check_all_components()

        for component_type, status in all_statuses.items():
            components[component_type.value] = {
                'status': status.status.value,
                'confidence': status.confidence,
                'is_operational': status.status == RealityStatus.REAL,
                'issues': status.issues_found,
                'last_checked': status.last_checked.isoformat()
            }

        return components

    def _get_data_flow_status(self) -> Dict[str, Any]:
        """Get status of data flows between components"""
        # Note: trace_data_flow not implemented in SystemRealityChecker
        # For now, return basic status based on component checks

        return {
            'spider_to_income': 'unknown',
            'income_to_revenue': 'unknown',
            'decision_to_agents': 'unknown',
            'agents_to_revenue': 'unknown',
            'overall_pipeline': 'partial'
        }

    def _get_system_recommendations(self, message: str) -> List[str]:
        """Generate intelligent recommendations based on system state and user message"""
        recommendations = []

        # Check for keywords in message
        message_lower = message.lower()

        if any(word in message_lower for word in ['revenue', 'money', 'earn', 'income']):
            # Check revenue system status
            revenue_status = self._get_component_status_cached(ComponentType.REVENUE_DASHBOARD)
            if revenue_status.status != RealityStatus.REAL:
                recommendations.append("Revenue tracking is currently simulated. Activate real revenue pipeline for actual earnings.")

            income_status = self._get_component_status_cached(ComponentType.INCOME_BUILDER)
            if income_status.status == RealityStatus.REAL:
                recommendations.append("Income Builder is operational. Try 'analyze opportunities' to find revenue streams.")

        if any(word in message_lower for word in ['agent', 'ai', 'orchestr']):
            # Check agent system status
            orchestra_status = self._get_component_status_cached(ComponentType.NEURAL_ORCHESTRA)
            if orchestra_status.status == RealityStatus.MOCK:
                recommendations.append("Neural Orchestra showing mock data. Deploy agent-execution-engine-builder for real agent activation.")
            else:
                agent_count = self._get_active_agent_count()
                recommendations.append(f"{agent_count} agents are currently active and ready for tasks.")

        if any(word in message_lower for word in ['spider', 'data', 'collect']):
            # Check spider network status
            spider_status = self._get_component_status_cached(ComponentType.SPIDERS)
            if spider_status.status != RealityStatus.REAL:
                recommendations.append("Spider network needs activation. Deploy spider-army-supreme-orchestrator for data collection.")

        if 'status' in message_lower or 'health' in message_lower:
            # Provide overall system health recommendation
            operational_pct = self._calculate_operational_percentage()
            if operational_pct < 50:
                recommendations.append(f"System is {operational_pct}% operational. Priority: Fix broken data flows.")
            elif operational_pct < 80:
                recommendations.append(f"System is {operational_pct}% operational. Consider activating remaining components.")
            else:
                recommendations.append(f"System is {operational_pct}% operational and healthy.")

        return recommendations

    def _determine_routing(self, message: str) -> Dict[str, Any]:
        """Determine intelligent routing based on message content and system state"""
        message_lower = message.lower()
        routing = {
            'primary_component': None,
            'secondary_components': [],
            'suggested_pipeline': None,
            'confidence': 0.0
        }

        # Analyze message for routing hints
        if 'opportunity' in message_lower or 'income' in message_lower:
            routing['primary_component'] = ComponentType.INCOME_BUILDER.value
            routing['suggested_pipeline'] = 'opportunity_flow'
            routing['confidence'] = 0.85

        elif 'revenue' in message_lower or 'earnings' in message_lower:
            routing['primary_component'] = ComponentType.REVENUE_DASHBOARD.value
            routing['suggested_pipeline'] = 'revenue_flow'
            routing['confidence'] = 0.80

        elif 'decision' in message_lower or 'analyze' in message_lower:
            routing['primary_component'] = ComponentType.DECISION_COMMAND.value
            routing['suggested_pipeline'] = 'decision_flow'
            routing['confidence'] = 0.75

        elif 'agent' in message_lower or 'orchestr' in message_lower:
            routing['primary_component'] = ComponentType.NEURAL_ORCHESTRA.value
            routing['suggested_pipeline'] = 'execution_flow'
            routing['confidence'] = 0.78

        # Add secondary components based on primary
        if routing['primary_component']:
            routing['secondary_components'] = self._get_related_components(routing['primary_component'])

        return routing

    def _should_refresh_reality_check(self) -> bool:
        """Determine if reality check needs refresh"""
        if not self.last_reality_check:
            return True

        elapsed = (datetime.now(tz.utc) - self.last_reality_check).total_seconds()
        return elapsed > self.reality_check_interval

    def _refresh_reality_status(self):
        """Refresh the reality check status"""
        try:
            # Trigger comprehensive reality check
            self.reality_checker.check_all_components()
            self.last_reality_check = datetime.now(tz.utc)
            logger.info("Reality status refreshed successfully")
        except Exception as e:
            logger.error(f"Error refreshing reality status: {e}")

    def _get_platform_reality_summary(self) -> str:
        """Get a human-readable summary of platform reality"""
        operational_pct = self._calculate_operational_percentage()

        if operational_pct >= 90:
            return "Platform fully operational with real data flows"
        elif operational_pct >= 70:
            return "Platform mostly operational with some simulated components"
        elif operational_pct >= 50:
            return "Platform partially operational with mixed real/mock components"
        elif operational_pct >= 30:
            return "Platform mostly simulated with some real components"
        else:
            return "Platform largely in simulation mode"

    def _calculate_operational_percentage(self) -> int:
        """Calculate percentage of operational (real) components"""
        all_statuses = self.reality_checker.check_all_components()
        total_components = len(all_statuses)
        real_components = 0

        for component_type, status in all_statuses.items():
            try:
                if status.status == RealityStatus.REAL:
                    real_components += 1
                elif status.status == RealityStatus.PARTIAL:
                    real_components += 0.5
            except Exception as e:
                # Session 1103c: was 'except Exception: pass' which
                # silently undercounted real_components if any status
                # object had an unexpected shape. Reality score is
                # used by ops dashboards to decide system health, so
                # an undercount could trigger false alarms.
                logger.warning(
                    "personal_assistant_integration: reality count "
                    "skipped %s (%s: %s)",
                    component_type, type(e).__name__, e,
                )

        return int((real_components / total_components) * 100) if total_components > 0 else 0

    def _identify_mock_components(self) -> List[str]:
        """Identify components running in mock mode"""
        mock_components = []
        all_statuses = self.reality_checker.check_all_components()

        for component_type, status in all_statuses.items():
            try:
                if status.status == RealityStatus.MOCK:
                    mock_components.append(component_type.value)
            except Exception as e:
                logger.warning(
                    "personal_assistant_integration: mock detection "
                    "skipped %s (%s: %s)",
                    component_type, type(e).__name__, e,
                )

        return mock_components

    def _identify_real_components(self) -> List[str]:
        """Identify components running with real data"""
        real_components = []
        all_statuses = self.reality_checker.check_all_components()

        for component_type, status in all_statuses.items():
            try:
                if status.status == RealityStatus.REAL:
                    real_components.append(component_type.value)
            except Exception as _e:
                logger.warning(
                    "personal_assistant_integration._identify_real_components: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )

        return real_components

    def _identify_broken_flows(self) -> List[str]:
        """Identify broken data flows"""
        # Since trace_data_flow is not implemented, return estimated broken flows
        # based on component status
        broken_flows = []

        all_statuses = self.reality_checker.check_all_components()

        # Check critical component pairs
        if all_statuses.get(ComponentType.SPIDERS, None) and \
           all_statuses[ComponentType.SPIDERS].status != RealityStatus.REAL:
            broken_flows.append('spider_to_income')

        if all_statuses.get(ComponentType.INCOME_BUILDER, None) and \
           all_statuses[ComponentType.INCOME_BUILDER].status != RealityStatus.REAL:
            broken_flows.append('income_to_revenue')

        if all_statuses.get(ComponentType.DECISION_COMMAND, None) and \
           all_statuses[ComponentType.DECISION_COMMAND].status != RealityStatus.REAL:
            broken_flows.append('decision_to_execution')

        return broken_flows

    def _get_active_agent_count(self) -> int:
        """Get count of active agents"""
        try:
            from core.models.agents_registry import UnifiedAgentTemplate
            return UnifiedAgentTemplate.objects.filter(is_active=True).count()
        except Exception:
            return 0

    def _get_related_components(self, primary_component: str) -> List[str]:
        """Get components related to the primary component"""
        relationships = {
            ComponentType.INCOME_BUILDER.value: [
                ComponentType.SPIDERS.value,
                ComponentType.REVENUE_DASHBOARD.value
            ],
            ComponentType.REVENUE_DASHBOARD.value: [
                ComponentType.INCOME_BUILDER.value,
                ComponentType.REVENUE_TRACKING.value
            ],
            ComponentType.NEURAL_ORCHESTRA.value: [
                ComponentType.AGENTS.value,
                ComponentType.DECISION_COMMAND.value
            ],
            ComponentType.DECISION_COMMAND.value: [
                ComponentType.INCOME_BUILDER.value,
                ComponentType.NEURAL_ORCHESTRA.value
            ]
        }

        return relationships.get(primary_component, [])

    def _get_component_status_cached(self, component_type: ComponentType) -> ComponentRealityStatus:
        """Get cached component status or refresh if needed"""
        if self._should_refresh_reality_check() or self._cached_statuses is None:
            self._cached_statuses = self.reality_checker.check_all_components()
            self.last_reality_check = datetime.now(tz.utc)

        return self._cached_statuses.get(component_type, ComponentRealityStatus(
            component=component_type,
            status=RealityStatus.UNKNOWN,
            confidence=0.0,
            details={},
            checks_performed=[],
            issues_found=["Component status unknown"],
            recommendations=[],
            last_checked=datetime.now(tz.utc)
        ))

    async def process_with_awareness(self, message: str, conversation_id: str) -> Dict[str, Any]:
        """
        Process message with full system awareness.

        This is the main entry point for the Personal Assistant to use
        when it needs reality-aware processing.
        """
        # Get enhanced context
        context = self.enhance_assistant_context(message, conversation_id)

        # Determine if we need to route to specific components
        routing = context['routing']

        response = {
            'message': message,
            'conversation_id': conversation_id,
            'system_context': context,
            'suggested_actions': [],
            'reality_insights': []
        }

        # Add reality insights
        if context['system_awareness']['operational_percentage'] < 50:
            response['reality_insights'].append(
                "⚠️ System operating below 50% capacity. Many components are simulated."
            )

        if context['system_awareness']['broken_flows']:
            response['reality_insights'].append(
                f"🔧 Broken data flows detected: {', '.join(context['system_awareness']['broken_flows'])}"
            )

        # Add suggested actions based on routing
        if routing['primary_component']:
            component_status = context['component_status'].get(routing['primary_component'], {})
            if component_status.get('is_operational'):
                response['suggested_actions'].append(
                    f"✅ {routing['primary_component']} is operational and ready"
                )
            else:
                response['suggested_actions'].append(
                    f"❌ {routing['primary_component']} is not operational - needs activation"
                )

        # Add recommendations
        response['recommendations'] = context['recommendations']

        return response

    def get_assistant_system_summary(self) -> str:
        """
        Get a comprehensive system summary for the Personal Assistant.

        Returns:
            Human-readable system summary
        """
        operational_pct = self._calculate_operational_percentage()
        real_components = self._identify_real_components()
        mock_components = self._identify_mock_components()
        broken_flows = self._identify_broken_flows()

        summary = f"""
🤖 **System Self-Awareness Report**

**Overall Status**: {self._get_platform_reality_summary()}
**Operational Level**: {operational_pct}%

**Real Components** ({len(real_components)}):
{chr(10).join(f'  ✅ {comp}' for comp in real_components) if real_components else '  None'}

**Simulated Components** ({len(mock_components)}):
{chr(10).join(f'  ⚠️ {comp}' for comp in mock_components) if mock_components else '  None'}

**Data Flow Issues** ({len(broken_flows)}):
{chr(10).join(f'  🔧 {flow}' for flow in broken_flows) if broken_flows else '  ✅ All flows operational'}

**Recommendations**:
"""

        if operational_pct < 50:
            summary += "1. Priority: Activate core components (Income Builder, Revenue Dashboard)\n"
            summary += "2. Deploy spider-army-supreme-orchestrator for data collection\n"
            summary += "3. Fix broken data flows with platform-unification-orchestrator\n"
        elif operational_pct < 80:
            summary += "1. Complete component activation for full functionality\n"
            summary += "2. Verify all data pipelines are connected\n"
            summary += "3. Test end-to-end revenue generation flow\n"
        else:
            summary += "1. System healthy - optimize performance\n"
            summary += "2. Monitor for any degradation\n"
            summary += "3. Scale successful components\n"

        return summary


# Singleton instance for global access
personal_assistant_integration = PersonalAssistantIntegration()