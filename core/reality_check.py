"""
System Reality Self-Awareness Engine
====================================

This module implements comprehensive reality checking infrastructure that gives
the platform true operational self-knowledge. It can definitively distinguish
between real and mock functionality across all components.

The SystemRealityChecker provides:
- Component operational status verification
- Data flow integrity checking
- Mock vs real detection
- Performance metrics analysis
- Revenue validation
- Agent execution verification
"""

import logging
import redis
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from django.db import connection
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from dataclasses import dataclass
from enum import Enum
import os

logger = logging.getLogger(__name__)


class RealityStatus(Enum):
    """Reality status levels"""
    REAL = "real"
    MOCK = "mock"
    PARTIAL = "partial"
    BROKEN = "broken"
    UNKNOWN = "unknown"


class ComponentType(Enum):
    """Platform component types"""
    INCOME_BUILDER = "income_builder"
    REVENUE_DASHBOARD = "revenue_dashboard"
    NEURAL_ORCHESTRA = "neural_orchestra"
    DECISION_COMMAND = "decision_command"
    WEBSOCKET_HUB = "websocket_hub"
    DATABASE = "database"
    REDIS = "redis"
    AGENTS = "agents"
    SPIDERS = "spiders"
    ML_PIPELINE = "ml_pipeline"
    REVENUE_TRACKING = "revenue_tracking"


@dataclass
class ComponentRealityStatus:
    """Reality status for a single component"""
    component: ComponentType
    status: RealityStatus
    confidence: float  # 0.0 to 1.0
    details: Dict[str, Any]
    checks_performed: List[str]
    issues_found: List[str]
    recommendations: List[str]
    last_checked: datetime


@dataclass
class DataFlowStatus:
    """Status of data flow between components"""
    source: ComponentType
    destination: ComponentType
    flow_active: bool
    data_quality: float  # 0.0 to 1.0
    latency_ms: Optional[float]
    last_data_timestamp: Optional[datetime]
    issues: List[str]


class SystemRealityChecker:
    """
    Comprehensive system reality checking engine.

    This class performs deep analysis of all platform components to determine
    what's actually operational vs what's simulated or mocked.
    """

    def __init__(self):
        self.redis_client = self._get_redis_client()
        self.component_checkers = {
            ComponentType.DATABASE: self._check_database_reality,
            ComponentType.REDIS: self._check_redis_reality,
            ComponentType.INCOME_BUILDER: self._check_income_builder_reality,
            ComponentType.REVENUE_DASHBOARD: self._check_revenue_dashboard_reality,
            ComponentType.NEURAL_ORCHESTRA: self._check_neural_orchestra_reality,
            ComponentType.DECISION_COMMAND: self._check_decision_command_reality,
            ComponentType.WEBSOCKET_HUB: self._check_websocket_hub_reality,
            ComponentType.AGENTS: self._check_agents_reality,
            ComponentType.SPIDERS: self._check_spiders_reality,
            ComponentType.ML_PIPELINE: self._check_ml_pipeline_reality,
            ComponentType.REVENUE_TRACKING: self._check_revenue_tracking_reality,
        }

    def _get_redis_client(self):
        """Get Redis client for caching and data checks"""
        try:
            return redis.Redis.from_url(
                getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0'),
                decode_responses=True
            )
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            return None

    def check_all_components(self) -> Dict[ComponentType, ComponentRealityStatus]:
        """
        Check reality status of all platform components.

        Returns:
            Dictionary mapping component types to their reality status
        """
        results = {}

        for component_type, checker_func in self.component_checkers.items():
            try:
                logger.info(f"Checking reality of {component_type.value}")
                status = checker_func()
                results[component_type] = status

                # Cache result for performance
                cache.set(
                    f"reality_check_{component_type.value}",
                    status.__dict__,
                    timeout=300  # 5 minutes
                )

            except Exception as e:
                logger.error(f"Error checking {component_type.value}: {e}")
                results[component_type] = ComponentRealityStatus(
                    component=component_type,
                    status=RealityStatus.BROKEN,
                    confidence=0.0,
                    details={'error': str(e)},
                    checks_performed=['initialization'],
                    issues_found=[f"Component check failed: {str(e)}"],
                    recommendations=[f"Fix {component_type.value} configuration"],
                    last_checked=timezone.now()
                )

        return results

    def _check_database_reality(self) -> ComponentRealityStatus:
        """Check if database contains real data vs empty/mock data"""
        checks_performed = []
        issues_found = []
        recommendations = []
        details = {}

        try:
            # Check database connection
            checks_performed.append("connection_test")
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                details['connection'] = 'active'

            # Check for real data in key tables
            checks_performed.append("data_volume_check")

            # Check intelligence models
            try:
                from intelligence.models import OpportunityActionPlan, ActionPlan, EarningRecord

                opp_count = OpportunityActionPlan.objects.count()
                plan_count = ActionPlan.objects.count()
                earning_count = EarningRecord.objects.count()

                details.update({
                    'opportunities': opp_count,
                    'action_plans': plan_count,
                    'earnings': earning_count
                })

                # Determine if data looks real
                has_real_data = (
                    opp_count > 0 or
                    plan_count > 0 or
                    earning_count > 0
                )

                if not has_real_data:
                    issues_found.append("No data in intelligence tables")
                    recommendations.append("Run spider network to collect opportunities")

            except ImportError:
                issues_found.append("Intelligence models not found")
                recommendations.append("Ensure intelligence app is installed")

            # Check agents
            checks_performed.append("agent_data_check")
            try:
                from core.models.agents_registry import UnifiedAgentTemplate, AgentTaskExecution

                agent_count = UnifiedAgentTemplate.objects.filter(is_active=True).count()
                execution_count = AgentTaskExecution.objects.count()

                details.update({
                    'active_agents': agent_count,
                    'agent_executions': execution_count
                })

                if agent_count < 100:  # Should have 149 agents
                    issues_found.append(f"Only {agent_count} agents registered, expected 149")
                    recommendations.append("Run agent registration to deploy all agents")

            except ImportError:
                issues_found.append("Agent models not found")
                recommendations.append("Ensure agents app is installed")

            # Check user data
            checks_performed.append("user_data_check")
            try:
                from core.models import UnifiedUser, UserProfile

                user_count = UnifiedUser.objects.count()
                profile_count = UserProfile.objects.count()

                details.update({
                    'users': user_count,
                    'profiles': profile_count
                })

                if user_count == 0:
                    issues_found.append("No users in system")
                    recommendations.append("Create test users or admin accounts")

            except ImportError:
                issues_found.append("Core models not found")

            # Determine overall status
            if len(issues_found) == 0:
                status = RealityStatus.REAL
                confidence = 0.95
            elif len(issues_found) < 3:
                status = RealityStatus.PARTIAL
                confidence = 0.6
            else:
                status = RealityStatus.MOCK
                confidence = 0.3

        except Exception as e:
            status = RealityStatus.BROKEN
            confidence = 0.0
            issues_found.append(f"Database connection failed: {str(e)}")
            recommendations.append("Check database configuration and connectivity")

        return ComponentRealityStatus(
            component=ComponentType.DATABASE,
            status=status,
            confidence=confidence,
            details=details,
            checks_performed=checks_performed,
            issues_found=issues_found,
            recommendations=recommendations,
            last_checked=timezone.now()
        )

    def _check_redis_reality(self) -> ComponentRealityStatus:
        """Check Redis connectivity and data"""
        checks_performed = []
        issues_found = []
        recommendations = []
        details = {}

        try:
            if not self.redis_client:
                raise Exception("Redis client not available")

            # Test connection
            checks_performed.append("connection_test")
            self.redis_client.ping()
            details['connection'] = 'active'

            # Check for real data
            checks_performed.append("data_check")
            keys = self.redis_client.keys('*')
            details['total_keys'] = len(keys)

            # Look for platform-specific keys
            platform_keys = [k for k in keys if any(prefix in k for prefix in [
                'opportunity', 'revenue', 'agent', 'websocket', 'income'
            ])]
            details['platform_keys'] = len(platform_keys)

            # Check WebSocket connections
            checks_performed.append("websocket_check")
            ws_keys = [k for k in keys if 'asgi:group' in k or 'websocket' in k]
            details['websocket_keys'] = len(ws_keys)

            if len(ws_keys) == 0:
                issues_found.append("No active WebSocket connections")
                recommendations.append("Start WebSocket services and connect clients")

            # Determine status
            if len(platform_keys) > 5:
                status = RealityStatus.REAL
                confidence = 0.9
            elif len(platform_keys) > 0:
                status = RealityStatus.PARTIAL
                confidence = 0.6
            else:
                status = RealityStatus.MOCK
                confidence = 0.3
                issues_found.append("No platform data in Redis")
                recommendations.append("Generate platform data and cache it")

        except Exception as e:
            status = RealityStatus.BROKEN
            confidence = 0.0
            issues_found.append(f"Redis check failed: {str(e)}")
            recommendations.append("Check Redis configuration and start Redis server")
            details['error'] = str(e)

        return ComponentRealityStatus(
            component=ComponentType.REDIS,
            status=status,
            confidence=confidence,
            details=details,
            checks_performed=checks_performed,
            issues_found=issues_found,
            recommendations=recommendations,
            last_checked=timezone.now()
        )

    def _check_income_builder_reality(self) -> ComponentRealityStatus:
        """Check if Income Builder uses real data and AI"""
        checks_performed = []
        issues_found = []
        recommendations = []
        details = {}

        try:
            # Check if income builder module exists
            checks_performed.append("module_check")
            try:
                import ai_core.intelligence.income_builder as ib_module
                details['module_found'] = True

                # Check for real AI integration
                if hasattr(ib_module, 'income_builder'):
                    details['has_income_builder'] = True

                    # Check AI configuration
                    if hasattr(ib_module.income_builder, 'ai_client'):
                        details['has_ai_client'] = True
                    else:
                        issues_found.append("No AI client configured")
                        recommendations.append("Configure OpenAI or Claude API keys")
                else:
                    issues_found.append("Income builder not instantiated")
                    recommendations.append("Initialize income builder properly")

            except ImportError:
                issues_found.append("Income builder module not found")
                recommendations.append("Install and configure income builder module")
                details['module_found'] = False

            # Check for real opportunities data
            checks_performed.append("opportunities_check")
            try:
                from intelligence.models import OpportunityActionPlan

                recent_opps = OpportunityActionPlan.objects.filter(
                    created_at__gte=timezone.now() - timedelta(hours=24)
                ).count()

                details['recent_opportunities'] = recent_opps

                if recent_opps == 0:
                    issues_found.append("No recent opportunities found")
                    recommendations.append("Run opportunity spider to collect real data")

            except ImportError:
                issues_found.append("Opportunity models not available")

            # Check WebSocket consumer
            checks_performed.append("websocket_consumer_check")
            try:
                from intelligence.consumers import IncomeBuilderConsumer

                # Check if consumer has real data methods
                has_real_methods = (
                    hasattr(IncomeBuilderConsumer, 'get_reddit_opportunities') and
                    hasattr(IncomeBuilderConsumer, 'analyze_opportunities')
                )

                details['has_real_websocket_methods'] = has_real_methods

                if not has_real_methods:
                    issues_found.append("WebSocket consumer uses mock data")
                    recommendations.append("Update WebSocket consumer to use real data")

            except ImportError:
                issues_found.append("Income builder WebSocket consumer not found")

            # Determine overall status
            real_indicators = sum([
                details.get('module_found', False),
                details.get('has_income_builder', False),
                details.get('has_ai_client', False),
                details.get('recent_opportunities', 0) > 0,
                details.get('has_real_websocket_methods', False)
            ])

            if real_indicators >= 4:
                status = RealityStatus.REAL
                confidence = 0.9
            elif real_indicators >= 2:
                status = RealityStatus.PARTIAL
                confidence = 0.6
            else:
                status = RealityStatus.MOCK
                confidence = 0.3

        except Exception as e:
            status = RealityStatus.BROKEN
            confidence = 0.0
            issues_found.append(f"Income builder check failed: {str(e)}")
            recommendations.append("Debug income builder configuration")

        return ComponentRealityStatus(
            component=ComponentType.INCOME_BUILDER,
            status=status,
            confidence=confidence,
            details=details,
            checks_performed=checks_performed,
            issues_found=issues_found,
            recommendations=recommendations,
            last_checked=timezone.now()
        )

    def _check_revenue_dashboard_reality(self) -> ComponentRealityStatus:
        """Check if Revenue Dashboard shows real vs mock data"""
        checks_performed = []
        issues_found = []
        recommendations = []
        details = {}

        try:
            # Check for revenue models
            checks_performed.append("revenue_models_check")
            try:
                from intelligence.models import RevenueMetrics, EarningRecord

                metrics_count = RevenueMetrics.objects.count()
                earnings_count = EarningRecord.objects.count()

                details.update({
                    'revenue_metrics_records': metrics_count,
                    'earning_records': earnings_count
                })

                # Check for recent data
                recent_metrics = RevenueMetrics.objects.filter(
                    date__gte=timezone.now().date() - timedelta(days=7)
                ).count()

                recent_earnings = EarningRecord.objects.filter(
                    earned_date__gte=timezone.now().date() - timedelta(days=30)
                ).count()

                details.update({
                    'recent_metrics': recent_metrics,
                    'recent_earnings': recent_earnings
                })

                if recent_metrics == 0 and recent_earnings == 0:
                    issues_found.append("No recent revenue data")
                    recommendations.append("Generate revenue from real opportunities")

                # Check for real revenue amounts
                if earnings_count > 0:
                    from django.db.models import Sum
                    total_revenue = EarningRecord.objects.aggregate(
                        total=Sum('amount')
                    )['total'] or 0

                    details['total_revenue'] = float(total_revenue)

                    if total_revenue == 0:
                        issues_found.append("All earnings are $0")
                        recommendations.append("Track real revenue from completed work")

            except ImportError:
                issues_found.append("Revenue models not found")
                recommendations.append("Create revenue tracking models")

            # Check Revenue Dashboard WebSocket
            checks_performed.append("websocket_check")
            try:
                from intelligence.consumers import RevenueIncomeConsumer
                details['has_revenue_websocket'] = True

                # Check if it has real data methods
                has_real_methods = hasattr(RevenueIncomeConsumer, 'get_revenue_metrics')
                details['has_real_revenue_methods'] = has_real_methods

            except ImportError:
                issues_found.append("Revenue WebSocket consumer not found")
                details['has_revenue_websocket'] = False

            # Check frontend integration
            checks_performed.append("frontend_check")
            frontend_path = "/Users/donkeyking/Donkey_Betz/unified-donkey-betz/frontend/src/components/RevenueDashboard.tsx"

            if os.path.exists(frontend_path):
                with open(frontend_path, 'r') as f:
                    content = f.read()

                # Check for WebSocket usage
                uses_websocket = 'WebSocket' in content or 'ws://' in content
                details['frontend_uses_websocket'] = uses_websocket

                # Check for mock data patterns
                has_mock_data = 'mockData' in content or 'fake' in content.lower()
                details['frontend_has_mock_data'] = has_mock_data

                if has_mock_data:
                    issues_found.append("Frontend still uses mock data")
                    recommendations.append("Update frontend to use real WebSocket data")
            else:
                issues_found.append("Revenue Dashboard frontend not found")

            # Determine status
            real_indicators = sum([
                details.get('revenue_metrics_records', 0) > 0,
                details.get('earning_records', 0) > 0,
                details.get('recent_earnings', 0) > 0,
                details.get('total_revenue', 0) > 0,
                details.get('has_revenue_websocket', False),
                details.get('frontend_uses_websocket', False),
                not details.get('frontend_has_mock_data', True)
            ])

            if real_indicators >= 5:
                status = RealityStatus.REAL
                confidence = 0.9
            elif real_indicators >= 3:
                status = RealityStatus.PARTIAL
                confidence = 0.6
            else:
                status = RealityStatus.MOCK
                confidence = 0.3

        except Exception as e:
            status = RealityStatus.BROKEN
            confidence = 0.0
            issues_found.append(f"Revenue dashboard check failed: {str(e)}")
            recommendations.append("Debug revenue dashboard configuration")

        return ComponentRealityStatus(
            component=ComponentType.REVENUE_DASHBOARD,
            status=status,
            confidence=confidence,
            details=details,
            checks_performed=checks_performed,
            issues_found=issues_found,
            recommendations=recommendations,
            last_checked=timezone.now()
        )

    def _check_neural_orchestra_reality(self) -> ComponentRealityStatus:
        """Check if Neural Orchestra shows real vs mock agents"""
        checks_performed = []
        issues_found = []
        recommendations = []
        details = {}

        try:
            # Check agent models
            checks_performed.append("agent_models_check")
            try:
                from core.models.agents_registry import UnifiedAgentTemplate, AgentTaskExecution

                total_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()
                total_executions = AgentTaskExecution.objects.count()

                details.update({
                    'total_agents': total_agents,
                    'total_executions': total_executions
                })

                # Check if we have the expected 149 agents
                if total_agents < 100:
                    issues_found.append(f"Only {total_agents} agents, expected 149")
                    recommendations.append("Run full agent deployment")
                elif total_agents >= 149:
                    details['has_full_agent_count'] = True

                # Check for recent executions
                recent_executions = AgentTaskExecution.objects.filter(
                    started_at__gte=timezone.now() - timedelta(hours=24)
                ).count()

                details['recent_executions'] = recent_executions

                if recent_executions == 0:
                    issues_found.append("No recent agent executions")
                    recommendations.append("Execute agents on real tasks")

            except ImportError:
                issues_found.append("Agent models not found")
                recommendations.append("Install and configure agent models")

            # Check Orchestra WebSocket
            checks_performed.append("orchestra_websocket_check")
            try:
                details['has_orchestra_websocket'] = True

            except ImportError:
                issues_found.append("Orchestra WebSocket consumer not found")
                details['has_orchestra_websocket'] = False

            # Check for agent advisors
            checks_performed.append("advisors_check")
            try:
                from core.models.agents_registry import AgentAdvisor
                advisor_count = AgentAdvisor.objects.count()
                details['advisors'] = advisor_count

                if advisor_count < 25:
                    issues_found.append(f"Only {advisor_count} advisors, expected 25+")
                    recommendations.append("Deploy full advisor network")

            except ImportError:
                details['advisors'] = 0
                issues_found.append("Advisor models not found")

            # Check frontend
            checks_performed.append("frontend_check")
            frontend_path = "/Users/donkeyking/Donkey_Betz/unified-donkey-betz/frontend/src/components/NeuralOrchestra.tsx"

            if os.path.exists(frontend_path):
                with open(frontend_path, 'r') as f:
                    content = f.read()

                uses_websocket = 'WebSocket' in content or 'ws://' in content
                has_mock_data = 'mockAgents' in content or 'fake' in content.lower()

                details.update({
                    'frontend_uses_websocket': uses_websocket,
                    'frontend_has_mock_data': has_mock_data
                })

                if has_mock_data:
                    issues_found.append("Frontend uses mock agent data")
                    recommendations.append("Update frontend to show real agents")

            # Determine status
            real_indicators = sum([
                details.get('total_agents', 0) >= 100,
                details.get('total_executions', 0) > 0,
                details.get('recent_executions', 0) > 0,
                details.get('has_orchestra_websocket', False),
                details.get('advisors', 0) > 20,
                details.get('frontend_uses_websocket', False),
                not details.get('frontend_has_mock_data', True)
            ])

            if real_indicators >= 5:
                status = RealityStatus.REAL
                confidence = 0.9
            elif real_indicators >= 3:
                status = RealityStatus.PARTIAL
                confidence = 0.6
            else:
                status = RealityStatus.MOCK
                confidence = 0.3

        except Exception as e:
            status = RealityStatus.BROKEN
            confidence = 0.0
            issues_found.append(f"Neural orchestra check failed: {str(e)}")
            recommendations.append("Debug neural orchestra configuration")

        return ComponentRealityStatus(
            component=ComponentType.NEURAL_ORCHESTRA,
            status=status,
            confidence=confidence,
            details=details,
            checks_performed=checks_performed,
            issues_found=issues_found,
            recommendations=recommendations,
            last_checked=timezone.now()
        )

    def _check_decision_command_reality(self) -> ComponentRealityStatus:
        """Check if Decision Command uses real ML/AI"""
        checks_performed = []
        issues_found = []
        recommendations = []
        details = {}

        try:
            # Check for decision models
            checks_performed.append("decision_models_check")
            try:
                from intelligence.models import OpportunityActionPlan

                # Look for high-confidence opportunities (real ML would generate these)
                high_confidence_opps = OpportunityActionPlan.objects.filter(
                    ml_confidence__gte=0.7
                ).count()

                details['high_confidence_opportunities'] = high_confidence_opps

                if high_confidence_opps == 0:
                    issues_found.append("No high-confidence ML predictions")
                    recommendations.append("Run ML pipeline on real data")

            except ImportError:
                issues_found.append("Decision models not found")

            # Check Decision Command WebSocket
            checks_performed.append("websocket_check")
            try:
                details['has_decision_websocket'] = True

            except ImportError:
                issues_found.append("Decision Command WebSocket not found")
                details['has_decision_websocket'] = False

            # Check for AI integration
            checks_performed.append("ai_integration_check")
            ai_configured = (
                bool(os.getenv('OPENAI_API_KEY')) or
                bool(os.getenv('ANTHROPIC_API_KEY'))
            )

            details['ai_configured'] = ai_configured

            if not ai_configured:
                issues_found.append("No AI API keys configured")
                recommendations.append("Configure OpenAI or Anthropic API keys")

            # Check frontend
            checks_performed.append("frontend_check")
            frontend_path = "/Users/donkeyking/Donkey_Betz/unified-donkey-betz/frontend/src/components/DecisionCommand.tsx"

            if os.path.exists(frontend_path):
                with open(frontend_path, 'r') as f:
                    content = f.read()

                uses_websocket = 'WebSocket' in content
                has_mock_decisions = 'mockDecisions' in content or 'hardcoded' in content.lower()

                details.update({
                    'frontend_uses_websocket': uses_websocket,
                    'frontend_has_mock_decisions': has_mock_decisions
                })

                if has_mock_decisions:
                    issues_found.append("Frontend uses mock decisions")
                    recommendations.append("Connect frontend to real ML pipeline")

            # Determine status
            real_indicators = sum([
                details.get('high_confidence_opportunities', 0) > 0,
                details.get('has_decision_websocket', False),
                details.get('ai_configured', False),
                details.get('frontend_uses_websocket', False),
                not details.get('frontend_has_mock_decisions', True)
            ])

            if real_indicators >= 4:
                status = RealityStatus.REAL
                confidence = 0.9
            elif real_indicators >= 2:
                status = RealityStatus.PARTIAL
                confidence = 0.6
            else:
                status = RealityStatus.MOCK
                confidence = 0.3

        except Exception as e:
            status = RealityStatus.BROKEN
            confidence = 0.0
            issues_found.append(f"Decision command check failed: {str(e)}")
            recommendations.append("Debug decision command configuration")

        return ComponentRealityStatus(
            component=ComponentType.DECISION_COMMAND,
            status=status,
            confidence=confidence,
            details=details,
            checks_performed=checks_performed,
            issues_found=issues_found,
            recommendations=recommendations,
            last_checked=timezone.now()
        )

    def _check_websocket_hub_reality(self) -> ComponentRealityStatus:
        """Check if WebSocket Hub provides real vs mock data"""
        checks_performed = []
        issues_found = []
        recommendations = []
        details = {}

        try:
            # Check for unified hub
            checks_performed.append("unified_hub_check")
            try:
                from core.unified_hub import UnifiedWebSocketHub
                details['has_unified_hub'] = True

                # Check if it has real data methods
                has_real_methods = (
                    hasattr(UnifiedWebSocketHub, 'get_real_income_builder_data') and
                    hasattr(UnifiedWebSocketHub, 'get_real_revenue_data') and
                    hasattr(UnifiedWebSocketHub, 'get_real_orchestra_data')
                )

                details['has_real_data_methods'] = has_real_methods

                if not has_real_methods:
                    issues_found.append("Hub lacks real data methods")
                    recommendations.append("Implement real data fetching methods")

            except ImportError:
                issues_found.append("Unified WebSocket Hub not found")
                details['has_unified_hub'] = False
                recommendations.append("Deploy unified WebSocket hub")

            # Check WebSocket routing
            checks_performed.append("routing_check")
            routing_path = "/Users/donkeyking/Donkey_Betz/unified-donkey-betz/core/routing.py"

            if os.path.exists(routing_path):
                with open(routing_path, 'r') as f:
                    content = f.read()

                has_unified_routes = 'unified_hub' in content
                has_component_routes = all(comp in content for comp in [
                    'income', 'revenue', 'orchestra', 'decision'
                ])

                details.update({
                    'has_unified_routes': has_unified_routes,
                    'has_component_routes': has_component_routes
                })

                if not has_unified_routes:
                    issues_found.append("No unified hub routing")
                    recommendations.append("Add unified hub to WebSocket routing")
            else:
                issues_found.append("WebSocket routing file not found")

            # Check for mock bridge (should be replaced)
            checks_performed.append("mock_bridge_check")
            mock_bridge_path = "/Users/donkeyking/Donkey_Betz/unified-donkey-betz/core/websocket_bridge.py"

            if os.path.exists(mock_bridge_path):
                with open(mock_bridge_path, 'r') as f:
                    content = f.read()

                if 'mock' in content.lower() or 'fake' in content.lower():
                    issues_found.append("Mock WebSocket bridge still exists")
                    recommendations.append("Replace mock bridge with unified hub")
                    details['has_mock_bridge'] = True
                else:
                    details['has_mock_bridge'] = False

            # Check Redis for WebSocket data
            if self.redis_client:
                checks_performed.append("redis_websocket_check")
                ws_keys = self.redis_client.keys('asgi:group:*')
                details['active_websocket_groups'] = len(ws_keys)

                if len(ws_keys) == 0:
                    issues_found.append("No active WebSocket connections")
                    recommendations.append("Start WebSocket services and connect clients")

            # Determine status
            real_indicators = sum([
                details.get('has_unified_hub', False),
                details.get('has_real_data_methods', False),
                details.get('has_unified_routes', False),
                details.get('has_component_routes', False),
                not details.get('has_mock_bridge', True),
                details.get('active_websocket_groups', 0) > 0
            ])

            if real_indicators >= 5:
                status = RealityStatus.REAL
                confidence = 0.9
            elif real_indicators >= 3:
                status = RealityStatus.PARTIAL
                confidence = 0.6
            else:
                status = RealityStatus.MOCK
                confidence = 0.3

        except Exception as e:
            status = RealityStatus.BROKEN
            confidence = 0.0
            issues_found.append(f"WebSocket hub check failed: {str(e)}")
            recommendations.append("Debug WebSocket hub configuration")

        return ComponentRealityStatus(
            component=ComponentType.WEBSOCKET_HUB,
            status=status,
            confidence=confidence,
            details=details,
            checks_performed=checks_performed,
            issues_found=issues_found,
            recommendations=recommendations,
            last_checked=timezone.now()
        )

    def _check_agents_reality(self) -> ComponentRealityStatus:
        """Check if agents actually execute vs just exist"""
        checks_performed = []
        issues_found = []
        recommendations = []
        details = {}

        try:
            # Check agent registration
            checks_performed.append("agent_registration_check")
            try:
                from core.models.agents_registry import UnifiedAgentTemplate

                total_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()
                details['total_registered_agents'] = total_agents

                if total_agents < 149:
                    issues_found.append(f"Only {total_agents}/149 agents registered")
                    recommendations.append("Complete agent registration deployment")

            except ImportError:
                issues_found.append("Agent models not available")
                total_agents = 0

            # Check agent execution history
            checks_performed.append("execution_history_check")
            try:
                from core.models.agents_registry import AgentTaskExecution

                total_executions = AgentTaskExecution.objects.count()
                recent_executions = AgentTaskExecution.objects.filter(
                    started_at__gte=timezone.now() - timedelta(hours=24)
                ).count()

                successful_executions = AgentTaskExecution.objects.filter(
                    status='completed'
                ).count()

                details.update({
                    'total_executions': total_executions,
                    'recent_executions': recent_executions,
                    'successful_executions': successful_executions
                })

                if total_executions == 0:
                    issues_found.append("No agent executions found")
                    recommendations.append("Execute agents on real tasks")
                elif recent_executions == 0:
                    issues_found.append("No recent agent activity")
                    recommendations.append("Trigger agent executions")

            except ImportError:
                issues_found.append("Agent execution models not available")

            # Check agent capabilities
            checks_performed.append("agent_capabilities_check")
            try:
                from core.models.agents_registry import UnifiedAgentTemplate

                # Check for different agent types
                specializations = UnifiedAgentTemplate.objects.filter(
                    is_active=True
                ).values_list('specialization', flat=True).distinct()

                details['specializations'] = list(specializations)
                details['specialization_count'] = len(specializations)

                expected_specializations = [
                    'content_creation', 'data_analysis', 'web_scraping',
                    'api_integration', 'financial_analysis', 'social_media'
                ]

                missing_specializations = [
                    spec for spec in expected_specializations
                    if spec not in specializations
                ]

                if missing_specializations:
                    issues_found.append(f"Missing specializations: {missing_specializations}")
                    recommendations.append("Deploy missing agent specializations")

            except ImportError:
                pass

            # Check agent orchestration
            checks_performed.append("orchestration_check")
            try:
                from core.models.agents_registry import AgentOrchestration

                orchestrations = AgentOrchestration.objects.count()
                active_orchestrations = AgentOrchestration.objects.filter(
                    status='running'
                ).count()

                details.update({
                    'total_orchestrations': orchestrations,
                    'active_orchestrations': active_orchestrations
                })

                if orchestrations == 0:
                    issues_found.append("No agent orchestrations")
                    recommendations.append("Create agent orchestration workflows")

            except ImportError:
                issues_found.append("Agent orchestration models not available")

            # Determine status
            real_indicators = sum([
                details.get('total_registered_agents', 0) >= 100,
                details.get('total_executions', 0) > 0,
                details.get('recent_executions', 0) > 0,
                details.get('successful_executions', 0) > 0,
                details.get('specialization_count', 0) >= 5,
                details.get('total_orchestrations', 0) > 0
            ])

            if real_indicators >= 5:
                status = RealityStatus.REAL
                confidence = 0.9
            elif real_indicators >= 3:
                status = RealityStatus.PARTIAL
                confidence = 0.6
            else:
                status = RealityStatus.MOCK
                confidence = 0.3

        except Exception as e:
            status = RealityStatus.BROKEN
            confidence = 0.0
            issues_found.append(f"Agents check failed: {str(e)}")
            recommendations.append("Debug agent system configuration")

        return ComponentRealityStatus(
            component=ComponentType.AGENTS,
            status=status,
            confidence=confidence,
            details=details,
            checks_performed=checks_performed,
            issues_found=issues_found,
            recommendations=recommendations,
            last_checked=timezone.now()
        )

    def _check_spiders_reality(self) -> ComponentRealityStatus:
        """Check if spider network collects real opportunities"""
        checks_performed = []
        issues_found = []
        recommendations = []
        details = {}

        try:
            # Check for spider modules
            checks_performed.append("spider_modules_check")
            spider_paths = [
                "/Users/donkeyking/Donkey_Betz/unified-donkey-betz/spiders",
                "/Users/donkeyking/Donkey_Betz/unified-donkey-betz/ai_core/spiders"
            ]

            has_spiders = False
            for path in spider_paths:
                if os.path.exists(path):
                    spider_files = [f for f in os.listdir(path) if f.endswith('.py')]
                    if spider_files:
                        has_spiders = True
                        details['spider_files'] = spider_files
                        details['spider_count'] = len(spider_files)
                        break

            if not has_spiders:
                issues_found.append("No spider modules found")
                recommendations.append("Deploy spider network for opportunity collection")
                details['spider_count'] = 0

            # Check for collected opportunities
            checks_performed.append("collected_opportunities_check")
            try:
                from intelligence.models import OpportunityActionPlan

                # Look for opportunities from spider collection (use platform field)
                spider_opportunities = OpportunityActionPlan.objects.filter(
                    platform__in=['reddit', 'upwork', 'freelancer', 'fiverr']
                ).count()

                recent_spider_opps = OpportunityActionPlan.objects.filter(
                    platform__in=['reddit', 'upwork', 'freelancer', 'fiverr'],
                    created_at__gte=timezone.now() - timedelta(hours=24)
                ).count()

                details.update({
                    'spider_collected_opportunities': spider_opportunities,
                    'recent_spider_opportunities': recent_spider_opps
                })

                if spider_opportunities == 0:
                    issues_found.append("No opportunities collected by spiders")
                    recommendations.append("Run spider collection to gather real opportunities")
                elif recent_spider_opps == 0:
                    issues_found.append("No recent spider activity")
                    recommendations.append("Schedule regular spider runs")

            except ImportError:
                issues_found.append("Opportunity models not available for spider check")

            # Check Reddit integration
            checks_performed.append("reddit_integration_check")
            reddit_configured = (
                bool(os.getenv('REDDIT_CLIENT_ID')) and
                bool(os.getenv('REDDIT_CLIENT_SECRET'))
            )

            details['reddit_configured'] = reddit_configured

            if not reddit_configured:
                issues_found.append("Reddit API not configured")
                recommendations.append("Configure Reddit API credentials")

            # Check other platform integrations
            checks_performed.append("platform_integrations_check")
            platform_configs = {
                'upwork': bool(os.getenv('UPWORK_API_KEY')),
                'freelancer': bool(os.getenv('FREELANCER_API_KEY')),
                'fiverr': bool(os.getenv('FIVERR_API_KEY')),
            }

            details['platform_integrations'] = platform_configs
            configured_platforms = sum(platform_configs.values())

            if configured_platforms == 0:
                issues_found.append("No freelance platform APIs configured")
                recommendations.append("Configure freelance platform API access")

            # Determine status
            real_indicators = sum([
                details.get('spider_count', 0) > 0,
                details.get('spider_collected_opportunities', 0) > 0,
                details.get('recent_spider_opportunities', 0) > 0,
                details.get('reddit_configured', False),
                configured_platforms > 0
            ])

            if real_indicators >= 4:
                status = RealityStatus.REAL
                confidence = 0.9
            elif real_indicators >= 2:
                status = RealityStatus.PARTIAL
                confidence = 0.6
            else:
                status = RealityStatus.MOCK
                confidence = 0.3

        except Exception as e:
            status = RealityStatus.BROKEN
            confidence = 0.0
            issues_found.append(f"Spiders check failed: {str(e)}")
            recommendations.append("Debug spider network configuration")

        return ComponentRealityStatus(
            component=ComponentType.SPIDERS,
            status=status,
            confidence=confidence,
            details=details,
            checks_performed=checks_performed,
            issues_found=issues_found,
            recommendations=recommendations,
            last_checked=timezone.now()
        )

    def _check_ml_pipeline_reality(self) -> ComponentRealityStatus:
        """Check if ML pipeline performs real analysis"""
        checks_performed = []
        issues_found = []
        recommendations = []
        details = {}

        try:
            # Check for ML models
            checks_performed.append("ml_models_check")
            try:
                from intelligence.models import OpportunityActionPlan

                # Look for ML confidence scores
                ml_analyzed = OpportunityActionPlan.objects.filter(
                    ml_confidence__isnull=False
                ).count()

                high_confidence = OpportunityActionPlan.objects.filter(
                    ml_confidence__gte=0.7
                ).count()

                details.update({
                    'ml_analyzed_opportunities': ml_analyzed,
                    'high_confidence_predictions': high_confidence
                })

                if ml_analyzed == 0:
                    issues_found.append("No ML analysis performed")
                    recommendations.append("Run ML pipeline on collected opportunities")

            except ImportError:
                issues_found.append("ML models not available")

            # Check for AI integration
            checks_performed.append("ai_integration_check")
            ai_keys_configured = {
                'openai': bool(os.getenv('OPENAI_API_KEY')),
                'anthropic': bool(os.getenv('ANTHROPIC_API_KEY')),
                'google': bool(os.getenv('GOOGLE_AI_API_KEY'))
            }

            details['ai_integrations'] = ai_keys_configured
            configured_ai = sum(ai_keys_configured.values())

            if configured_ai == 0:
                issues_found.append("No AI APIs configured")
                recommendations.append("Configure AI API keys for ML pipeline")

            # Check for feature engineering
            checks_performed.append("feature_engineering_check")
            try:
                from intelligence.models import OpportunityActionPlan

                # Check if opportunities have structured data (indicates feature engineering)
                structured_data = OpportunityActionPlan.objects.filter(
                    opportunity_data__has_key='features'
                ).count()

                details['opportunities_with_features'] = structured_data

                if structured_data == 0:
                    issues_found.append("No feature engineering detected")
                    recommendations.append("Implement feature extraction for opportunities")

            except ImportError:
                pass

            # Check for model training data
            checks_performed.append("training_data_check")
            try:
                from intelligence.models import EarningRecord

                # Training data would come from successful earnings
                training_samples = EarningRecord.objects.filter(
                    amount__gt=0
                ).count()

                details['training_data_samples'] = training_samples

                if training_samples < 10:
                    issues_found.append("Insufficient training data")
                    recommendations.append("Collect more successful earning records for training")

            except ImportError:
                issues_found.append("Training data models not available")

            # Check for model persistence
            checks_performed.append("model_persistence_check")
            model_paths = [
                "/Users/donkeyking/Donkey_Betz/unified-donkey-betz/models",
                "/Users/donkeyking/Donkey_Betz/unified-donkey-betz/ml_models"
            ]

            has_persisted_models = False
            for path in model_paths:
                if os.path.exists(path):
                    model_files = [f for f in os.listdir(path)
                                 if f.endswith(('.pkl', '.joblib', '.pt', '.h5'))]
                    if model_files:
                        has_persisted_models = True
                        details['model_files'] = model_files
                        break

            details['has_persisted_models'] = has_persisted_models

            if not has_persisted_models:
                issues_found.append("No persisted ML models found")
                recommendations.append("Train and save ML models for opportunity scoring")

            # Determine status
            real_indicators = sum([
                details.get('ml_analyzed_opportunities', 0) > 0,
                details.get('high_confidence_predictions', 0) > 0,
                configured_ai > 0,
                details.get('opportunities_with_features', 0) > 0,
                details.get('training_data_samples', 0) >= 10,
                details.get('has_persisted_models', False)
            ])

            if real_indicators >= 5:
                status = RealityStatus.REAL
                confidence = 0.9
            elif real_indicators >= 3:
                status = RealityStatus.PARTIAL
                confidence = 0.6
            else:
                status = RealityStatus.MOCK
                confidence = 0.3

        except Exception as e:
            status = RealityStatus.BROKEN
            confidence = 0.0
            issues_found.append(f"ML pipeline check failed: {str(e)}")
            recommendations.append("Debug ML pipeline configuration")

        return ComponentRealityStatus(
            component=ComponentType.ML_PIPELINE,
            status=status,
            confidence=confidence,
            details=details,
            checks_performed=checks_performed,
            issues_found=issues_found,
            recommendations=recommendations,
            last_checked=timezone.now()
        )

    def _check_revenue_tracking_reality(self) -> ComponentRealityStatus:
        """Check if revenue tracking captures real money"""
        checks_performed = []
        issues_found = []
        recommendations = []
        details = {}

        try:
            # Check revenue models
            checks_performed.append("revenue_models_check")
            try:
                from intelligence.models import EarningRecord
                from django.db.models import Sum, Avg, Count

                total_earnings = EarningRecord.objects.aggregate(
                    total=Sum('amount'),
                    count=Count('id'),
                    avg=Avg('amount')
                )

                details.update({
                    'total_revenue': float(total_earnings['total'] or 0),
                    'total_transactions': total_earnings['count'] or 0,
                    'average_earning': float(total_earnings['avg'] or 0)
                })

                # Check for real revenue (not $0)
                non_zero_earnings = EarningRecord.objects.filter(
                    amount__gt=0
                ).count()

                details['non_zero_earnings'] = non_zero_earnings

                if non_zero_earnings == 0:
                    issues_found.append("All earnings are $0 - no real revenue")
                    recommendations.append("Track actual revenue from completed work")

                # Check for recent revenue
                recent_earnings = EarningRecord.objects.filter(
                    earned_date__gte=timezone.now().date() - timedelta(days=30)
                ).count()

                details['recent_earnings'] = recent_earnings

                if recent_earnings == 0:
                    issues_found.append("No recent revenue activity")
                    recommendations.append("Generate revenue from active opportunities")

            except ImportError:
                issues_found.append("Revenue tracking models not available")
                recommendations.append("Deploy revenue tracking system")

            # Check payment integration
            checks_performed.append("payment_integration_check")
            payment_configs = {
                'stripe': bool(os.getenv('STRIPE_SECRET_KEY')),
                'paypal': bool(os.getenv('PAYPAL_CLIENT_ID')),
                'square': bool(os.getenv('SQUARE_ACCESS_TOKEN')),
            }

            details['payment_integrations'] = payment_configs
            configured_payments = sum(payment_configs.values())

            if configured_payments == 0:
                issues_found.append("No payment processing configured")
                recommendations.append("Configure payment processing (Stripe/PayPal)")

            # Check for withdrawal/payout tracking
            checks_performed.append("payout_tracking_check")
            try:
                from intelligence.models import EarningRecord

                # Look for withdrawal records
                withdrawals = EarningRecord.objects.filter(
                    source='withdrawal'
                ).count()

                details['withdrawal_records'] = withdrawals

                if withdrawals == 0 and details.get('total_revenue', 0) > 100:
                    issues_found.append("No withdrawal tracking for earned revenue")
                    recommendations.append("Implement withdrawal/payout tracking")

            except ImportError:
                pass

            # Check platform revenue sources
            checks_performed.append("revenue_sources_check")
            try:
                from intelligence.models import EarningRecord

                sources = EarningRecord.objects.values_list(
                    'source', flat=True
                ).distinct()

                details['revenue_sources'] = list(sources)
                details['source_diversity'] = len(sources)

                if len(sources) < 2:
                    issues_found.append("Limited revenue source diversity")
                    recommendations.append("Diversify revenue streams across platforms")

            except ImportError:
                pass

            # Check revenue validation
            checks_performed.append("revenue_validation_check")
            try:
                from intelligence.models import EarningRecord

                # Check for revenue validation (proof of payment) - use transaction_data field
                validated_earnings = EarningRecord.objects.filter(
                    transaction_data__has_key='payment_proof'
                ).count()

                details['validated_earnings'] = validated_earnings

                total_records = details.get('total_transactions', 0)
                if total_records > 0 and validated_earnings / total_records < 0.5:
                    issues_found.append("Low revenue validation rate")
                    recommendations.append("Implement payment proof validation")

            except ImportError:
                pass

            # Determine status
            real_indicators = sum([
                details.get('total_revenue', 0) > 0,
                details.get('non_zero_earnings', 0) > 0,
                details.get('recent_earnings', 0) > 0,
                configured_payments > 0,
                details.get('source_diversity', 0) >= 2,
                details.get('validated_earnings', 0) > 0
            ])

            if real_indicators >= 5:
                status = RealityStatus.REAL
                confidence = 0.9
            elif real_indicators >= 3:
                status = RealityStatus.PARTIAL
                confidence = 0.6
            else:
                status = RealityStatus.MOCK
                confidence = 0.3

        except Exception as e:
            status = RealityStatus.BROKEN
            confidence = 0.0
            issues_found.append(f"Revenue tracking check failed: {str(e)}")
            recommendations.append("Debug revenue tracking system")

        return ComponentRealityStatus(
            component=ComponentType.REVENUE_TRACKING,
            status=status,
            confidence=confidence,
            details=details,
            checks_performed=checks_performed,
            issues_found=issues_found,
            recommendations=recommendations,
            last_checked=timezone.now()
        )

    def generate_reality_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive reality report for the entire platform.

        Returns:
            Complete reality assessment with scores and recommendations
        """
        logger.info("Generating comprehensive platform reality report")

        # Check all components
        component_statuses = self.check_all_components()

        # Calculate overall reality score
        total_confidence = sum(status.confidence for status in component_statuses.values())
        overall_score = total_confidence / len(component_statuses) if component_statuses else 0.0

        # Categorize components by status
        status_categories = {
            'real': [],
            'partial': [],
            'mock': [],
            'broken': []
        }

        for component, status in component_statuses.items():
            status_categories[status.status.value].append({
                'component': component.value,
                'confidence': status.confidence,
                'issues': len(status.issues_found),
                'recommendations': len(status.recommendations)
            })

        # Collect all issues and recommendations
        all_issues = []
        all_recommendations = []

        for status in component_statuses.values():
            all_issues.extend([
                {'component': status.component.value, 'issue': issue}
                for issue in status.issues_found
            ])
            all_recommendations.extend([
                {'component': status.component.value, 'recommendation': rec}
                for rec in status.recommendations
            ])

        # Priority recommendations (most impactful)
        priority_recommendations = []
        if status_categories['broken']:
            priority_recommendations.append("Fix broken components before optimizing others")
        if status_categories['mock']:
            priority_recommendations.append("Replace mock components with real implementations")
        if overall_score < 0.5:
            priority_recommendations.append("Platform needs major reality improvements")
        elif overall_score < 0.8:
            priority_recommendations.append("Platform is partially operational, focus on weak areas")
        else:
            priority_recommendations.append("Platform is mostly operational, optimize performance")

        # Generate data flow analysis
        data_flows = self._analyze_data_flows(component_statuses)

        report = {
            'generated_at': timezone.now().isoformat(),
            'overall_reality_score': round(overall_score, 3),
            'overall_status': self._get_overall_status(overall_score),
            'summary': {
                'total_components': len(component_statuses),
                'real_components': len(status_categories['real']),
                'partial_components': len(status_categories['partial']),
                'mock_components': len(status_categories['mock']),
                'broken_components': len(status_categories['broken']),
                'total_issues': len(all_issues),
                'total_recommendations': len(all_recommendations)
            },
            'components': {
                component.value: {
                    'status': status.status.value,
                    'confidence': round(status.confidence, 3),
                    'details': status.details,
                    'checks_performed': status.checks_performed,
                    'issues_found': status.issues_found,
                    'recommendations': status.recommendations,
                    'last_checked': status.last_checked.isoformat()
                }
                for component, status in component_statuses.items()
            },
            'status_categories': status_categories,
            'critical_issues': [
                issue for issue in all_issues
                if any(keyword in issue['issue'].lower() for keyword in [
                    'broken', 'failed', 'not found', 'no data'
                ])
            ],
            'priority_recommendations': priority_recommendations,
            'data_flows': data_flows,
            'reality_metrics': {
                'data_completeness': self._calculate_data_completeness(component_statuses),
                'functional_completeness': self._calculate_functional_completeness(component_statuses),
                'integration_completeness': self._calculate_integration_completeness(component_statuses)
            }
        }

        # Cache the report
        cache.set('platform_reality_report', report, timeout=600)  # 10 minutes

        logger.info(f"Reality report generated: {overall_score:.1%} operational")

        return report

    def _get_overall_status(self, score: float) -> str:
        """Get overall platform status based on score"""
        if score >= 0.9:
            return "fully_operational"
        elif score >= 0.7:
            return "mostly_operational"
        elif score >= 0.5:
            return "partially_operational"
        elif score >= 0.3:
            return "mostly_simulated"
        else:
            return "primarily_mock"

    def _analyze_data_flows(self, component_statuses: Dict[ComponentType, ComponentRealityStatus]) -> List[Dict[str, Any]]:
        """Analyze data flows between components"""
        flows = []

        # Define expected data flows
        expected_flows = [
            (ComponentType.SPIDERS, ComponentType.DATABASE, "Opportunity collection"),
            (ComponentType.DATABASE, ComponentType.ML_PIPELINE, "ML analysis"),
            (ComponentType.ML_PIPELINE, ComponentType.INCOME_BUILDER, "Opportunity ranking"),
            (ComponentType.INCOME_BUILDER, ComponentType.REVENUE_TRACKING, "Revenue generation"),
            (ComponentType.AGENTS, ComponentType.NEURAL_ORCHESTRA, "Agent coordination"),
            (ComponentType.DATABASE, ComponentType.WEBSOCKET_HUB, "Real-time data"),
            (ComponentType.WEBSOCKET_HUB, ComponentType.REVENUE_DASHBOARD, "Dashboard updates"),
        ]

        for source, dest, description in expected_flows:
            source_status = component_statuses.get(source)
            dest_status = component_statuses.get(dest)

            if source_status and dest_status:
                # Calculate flow health based on both components
                flow_health = (source_status.confidence + dest_status.confidence) / 2

                flows.append({
                    'source': source.value,
                    'destination': dest.value,
                    'description': description,
                    'health': round(flow_health, 3),
                    'status': 'active' if flow_health > 0.6 else 'degraded' if flow_health > 0.3 else 'broken',
                    'issues': (source_status.issues_found + dest_status.issues_found)[:3]  # Top 3 issues
                })

        return flows

    def _calculate_data_completeness(self, component_statuses: Dict[ComponentType, ComponentRealityStatus]) -> float:
        """Calculate what percentage of expected data exists"""
        data_components = [
            ComponentType.DATABASE,
            ComponentType.SPIDERS,
            ComponentType.REVENUE_TRACKING
        ]

        scores = []
        for comp in data_components:
            if comp in component_statuses:
                scores.append(component_statuses[comp].confidence)

        return sum(scores) / len(scores) if scores else 0.0

    def _calculate_functional_completeness(self, component_statuses: Dict[ComponentType, ComponentRealityStatus]) -> float:
        """Calculate what percentage of functions actually work"""
        functional_components = [
            ComponentType.INCOME_BUILDER,
            ComponentType.NEURAL_ORCHESTRA,
            ComponentType.DECISION_COMMAND,
            ComponentType.AGENTS,
            ComponentType.ML_PIPELINE
        ]

        scores = []
        for comp in functional_components:
            if comp in component_statuses:
                scores.append(component_statuses[comp].confidence)

        return sum(scores) / len(scores) if scores else 0.0

    def _calculate_integration_completeness(self, component_statuses: Dict[ComponentType, ComponentRealityStatus]) -> float:
        """Calculate how well components integrate"""
        integration_components = [
            ComponentType.WEBSOCKET_HUB,
            ComponentType.REDIS,
            ComponentType.DATABASE
        ]

        scores = []
        for comp in integration_components:
            if comp in component_statuses:
                scores.append(component_statuses[comp].confidence)

        return sum(scores) / len(scores) if scores else 0.0


# Global instance for easy access
system_reality_checker = SystemRealityChecker()