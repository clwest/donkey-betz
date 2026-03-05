"""
Autonomy Engine - Self-Operating Intelligence System
=====================================================

Session 265: Phase 6 - Autonomy Engine (Final Phase!)

This service enables the Super Platform to operate autonomously:
1. Proactive Scanning - Discover opportunities without user prompts
2. Autonomous Actions - Execute approved actions automatically
3. Decision Framework - Risk assessment and approval thresholds
4. Self-Healing - Error recovery and system optimization
5. Audit Trail - Complete record of all autonomous decisions

The Autonomy Loop:
    Monitor → Assess → Decide → Act → Learn → Improve

Integration with existing systems:
- ProactiveSystem (core/proactive_engine.py) - Alerts and suggestions
- LearningLoopService - Learn from autonomous action outcomes
- RevenueIntegrationService - Opportunity pipeline
- SciFiIntegrationService - Agent personality in decisions
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum
import uuid

from django.utils import timezone
from django.db.models import Sum, Count
from django.core.cache import cache

logger = logging.getLogger(__name__)


class AutonomyLevel(Enum):
    """Levels of autonomous operation."""
    OBSERVE = "observe"      # Only observe, never act
    SUGGEST = "suggest"      # Observe and suggest, don't act
    ASSISTED = "assisted"    # Act with user confirmation
    AUTONOMOUS = "autonomous" # Act without confirmation (within limits)
    FULL = "full"            # Full autonomy (no limits)


class ActionType(Enum):
    """Types of autonomous actions."""
    OPPORTUNITY_APPLY = "opportunity_apply"
    CONTENT_CREATE = "content_create"
    CONTENT_DISTRIBUTE = "content_distribute"
    PRICE_ADJUST = "price_adjust"
    ALERT_RESPOND = "alert_respond"
    SYSTEM_OPTIMIZE = "system_optimize"
    SPIDER_DISPATCH = "spider_dispatch"
    AGENT_COLLABORATE = "agent_collaborate"


class RiskLevel(Enum):
    """Risk levels for autonomous actions."""
    MINIMAL = "minimal"      # No financial impact, reversible
    LOW = "low"              # Low financial impact, easily reversible
    MEDIUM = "medium"        # Moderate impact, may require effort to reverse
    HIGH = "high"            # Significant impact, hard to reverse
    CRITICAL = "critical"    # Major impact, irreversible


@dataclass
class AutonomousAction:
    """Represents a potential or executed autonomous action."""
    id: str
    action_type: ActionType
    risk_level: RiskLevel
    description: str
    reasoning: str
    estimated_value: Decimal = Decimal('0.00')
    confidence: float = 0.0
    requires_approval: bool = True
    approved: bool = False
    executed: bool = False
    success: Optional[bool] = None
    execution_result: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=timezone.now)
    executed_at: Optional[datetime] = None
    agents_involved: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'action_type': self.action_type.value,
            'risk_level': self.risk_level.value,
            'description': self.description,
            'reasoning': self.reasoning,
            'estimated_value': float(self.estimated_value),
            'confidence': self.confidence,
            'requires_approval': self.requires_approval,
            'approved': self.approved,
            'executed': self.executed,
            'success': self.success,
            'execution_result': self.execution_result,
            'created_at': self.created_at.isoformat(),
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'agents_involved': self.agents_involved,
        }


@dataclass
class AutonomyConfig:
    """Configuration for autonomous behavior."""
    level: AutonomyLevel = AutonomyLevel.ASSISTED
    max_daily_actions: int = 10
    max_daily_value: Decimal = Decimal('100.00')
    allowed_action_types: List[ActionType] = field(default_factory=list)
    risk_tolerance: RiskLevel = RiskLevel.LOW
    require_approval_above: Decimal = Decimal('50.00')
    quiet_hours_start: Optional[int] = None  # Hour (0-23)
    quiet_hours_end: Optional[int] = None
    notify_on_action: bool = True
    learn_from_feedback: bool = True

    def __post_init__(self):
        if not self.allowed_action_types:
            self.allowed_action_types = [
                ActionType.OPPORTUNITY_APPLY,
                ActionType.CONTENT_CREATE,
                ActionType.SPIDER_DISPATCH,
            ]

    def to_dict(self) -> dict:
        return {
            'level': self.level.value,
            'max_daily_actions': self.max_daily_actions,
            'max_daily_value': float(self.max_daily_value),
            'allowed_action_types': [a.value for a in self.allowed_action_types],
            'risk_tolerance': self.risk_tolerance.value,
            'require_approval_above': float(self.require_approval_above),
            'quiet_hours_start': self.quiet_hours_start,
            'quiet_hours_end': self.quiet_hours_end,
            'notify_on_action': self.notify_on_action,
            'learn_from_feedback': self.learn_from_feedback,
        }


class AutonomyEngine:
    """
    The autonomy engine for self-operating intelligence.

    This service:
    - Monitors for autonomous action opportunities
    - Assesses risks and estimated values
    - Makes decisions based on configuration and learning
    - Executes approved actions
    - Records all actions for audit and learning
    """

    CACHE_PREFIX = 'autonomy:'
    CACHE_TTL = 300  # 5 minutes

    def __init__(self, user=None):
        """Initialize the autonomy engine."""
        self.user = user
        self._config = None
        self._revenue_service = None
        self._learning_service = None
        self._proactive_system = None

    # ==================== Configuration ====================

    @property
    def config(self) -> AutonomyConfig:
        """Get autonomy configuration for user."""
        if self._config is None:
            self._config = self._load_config()
        return self._config

    def _load_config(self) -> AutonomyConfig:
        """Load or create autonomy configuration."""
        if not self.user:
            return AutonomyConfig()

        try:
            from core.models_unified_system import AutonomyConfiguration
            config_obj, _ = AutonomyConfiguration.objects.get_or_create(
                user=self.user,
                defaults={
                    'autonomy_level': AutonomyLevel.ASSISTED.value,
                    'max_daily_actions': 10,
                    'max_daily_value': Decimal('100.00'),
                }
            )

            return AutonomyConfig(
                level=AutonomyLevel(config_obj.autonomy_level),
                max_daily_actions=config_obj.max_daily_actions,
                max_daily_value=config_obj.max_daily_value,
                allowed_action_types=[
                    ActionType(a) for a in config_obj.allowed_action_types
                ] if config_obj.allowed_action_types else [],
                risk_tolerance=RiskLevel(config_obj.risk_tolerance) if config_obj.risk_tolerance else RiskLevel.LOW,
                require_approval_above=config_obj.require_approval_above or Decimal('50.00'),
                quiet_hours_start=config_obj.quiet_hours_start,
                quiet_hours_end=config_obj.quiet_hours_end,
                notify_on_action=config_obj.notify_on_action,
                learn_from_feedback=config_obj.learn_from_feedback,
            )
        except Exception as e:
            logger.debug(f"Using default autonomy config: {e}")
            return AutonomyConfig()

    def update_config(self, **kwargs) -> AutonomyConfig:
        """Update autonomy configuration."""
        if not self.user:
            return self.config

        try:
            from core.models_unified_system import AutonomyConfiguration
            config_obj, _ = AutonomyConfiguration.objects.get_or_create(user=self.user)

            for key, value in kwargs.items():
                if hasattr(config_obj, key):
                    setattr(config_obj, key, value)

            config_obj.save()
            self._config = None  # Force reload
            return self.config

        except Exception as e:
            logger.error(f"Error updating autonomy config: {e}")
            return self.config

    # ==================== Service Integration ====================

    @property
    def revenue_service(self):
        """Lazy load revenue integration service."""
        if self._revenue_service is None:
            try:
                from .revenue_integration import get_revenue_integration_service
                self._revenue_service = get_revenue_integration_service(self.user)
            except Exception as e:
                logger.debug(f"Could not load revenue service: {e}")
        return self._revenue_service

    @property
    def learning_service(self):
        """Lazy load learning loop service."""
        if self._learning_service is None:
            try:
                from .learning_loop import get_learning_loop_service
                self._learning_service = get_learning_loop_service(self.user)
            except Exception as e:
                logger.debug(f"Could not load learning service: {e}")
        return self._learning_service

    @property
    def proactive_system(self):
        """Lazy load proactive system."""
        if self._proactive_system is None:
            try:
                from core.proactive_engine import ProactiveSystem
                self._proactive_system = ProactiveSystem(self.user)
            except Exception as e:
                logger.debug(f"Could not load proactive system: {e}")
        return self._proactive_system

    # ==================== Proactive Scanning ====================

    def scan_for_opportunities(self) -> List[AutonomousAction]:
        """
        Proactively scan for actionable opportunities.

        Returns:
            List of potential autonomous actions
        """
        if self.config.level == AutonomyLevel.OBSERVE:
            return []

        actions = []

        # 1. Check revenue opportunities
        revenue_actions = self._scan_revenue_opportunities()
        actions.extend(revenue_actions)

        # 2. Check spider network for new data
        spider_actions = self._scan_spider_opportunities()
        actions.extend(spider_actions)

        # 3. Check for optimization opportunities
        optimization_actions = self._scan_optimization_opportunities()
        actions.extend(optimization_actions)

        # 4. Check agent collaboration opportunities
        collab_actions = self._scan_collaboration_opportunities()
        actions.extend(collab_actions)

        # Filter by allowed action types
        actions = [
            a for a in actions
            if a.action_type in self.config.allowed_action_types
        ]

        # Filter by risk tolerance
        risk_order = list(RiskLevel)
        max_risk_idx = risk_order.index(self.config.risk_tolerance)
        actions = [
            a for a in actions
            if risk_order.index(a.risk_level) <= max_risk_idx
        ]

        # Sort by value and confidence
        actions.sort(key=lambda a: (a.estimated_value * Decimal(str(a.confidence))), reverse=True)

        # Store in cache for quick access
        cache_key = f"{self.CACHE_PREFIX}pending_actions:{self.user.id if self.user else 'anon'}"
        cache.set(cache_key, [a.to_dict() for a in actions[:20]], self.CACHE_TTL)

        return actions[:20]

    def _scan_revenue_opportunities(self) -> List[AutonomousAction]:
        """Scan for revenue opportunities."""
        actions = []

        if not self.revenue_service:
            return actions

        try:
            opportunities = self.revenue_service.discover_opportunities(hours=24, limit=10)

            for opp in opportunities:
                # Determine if auto-apply eligible
                if opp.auto_apply_eligible and opp.score >= 70:
                    action = AutonomousAction(
                        id=str(uuid.uuid4()),
                        action_type=ActionType.OPPORTUNITY_APPLY,
                        risk_level=RiskLevel.LOW if opp.estimated_revenue < 100 else RiskLevel.MEDIUM,
                        description=f"Apply to opportunity: {opp.title}",
                        reasoning=f"High-scoring opportunity ({opp.score}/100) with estimated revenue ${opp.estimated_revenue}",
                        estimated_value=opp.estimated_revenue,
                        confidence=opp.score / 100.0,
                        requires_approval=opp.estimated_revenue > self.config.require_approval_above,
                        context={'opportunity_id': opp.id, 'source': opp.source},
                    )
                    actions.append(action)

        except Exception as e:
            logger.debug(f"Error scanning revenue opportunities: {e}")

        return actions

    def _scan_spider_opportunities(self) -> List[AutonomousAction]:
        """Scan spider network for opportunities."""
        actions = []

        try:
            from core.models_unified_system import SpiderData
            from ai_core.spiders.spider_registry import SpiderRegistry

            registry = SpiderRegistry()

            # Find stale spider data that needs refresh
            cutoff = timezone.now() - timedelta(hours=6)
            stale_categories = set()

            recent_data = SpiderData.objects.filter(
                created_at__gte=cutoff
            ).values('spider_name').annotate(count=Count('id'))

            active_categories = {d['spider_name'] for d in recent_data}
            all_categories = set(registry.get_categories())
            stale_categories = all_categories - active_categories

            if stale_categories:
                action = AutonomousAction(
                    id=str(uuid.uuid4()),
                    action_type=ActionType.SPIDER_DISPATCH,
                    risk_level=RiskLevel.MINIMAL,
                    description=f"Dispatch spiders for {len(stale_categories)} stale categories",
                    reasoning=f"Categories {', '.join(list(stale_categories)[:3])} haven't been updated recently",
                    estimated_value=Decimal('10.00'),  # Value of fresh data
                    confidence=0.9,
                    requires_approval=False,
                    context={'categories': list(stale_categories)},
                )
                actions.append(action)

        except Exception as e:
            logger.debug(f"Error scanning spider opportunities: {e}")

        return actions

    def _scan_optimization_opportunities(self) -> List[AutonomousAction]:
        """Scan for system optimization opportunities."""
        actions = []

        try:
            # Check learning patterns for optimization hints
            if self.learning_service:
                patterns = self.learning_service.detect_patterns(days=7)

                for pattern in patterns:
                    if pattern.get('pattern_type') == 'agent_specialization':
                        # Suggest agent collaboration optimization
                        action = AutonomousAction(
                            id=str(uuid.uuid4()),
                            action_type=ActionType.SYSTEM_OPTIMIZE,
                            risk_level=RiskLevel.MINIMAL,
                            description=f"Optimize agent routing based on learned patterns",
                            reasoning=pattern.get('description', 'Learned optimization opportunity'),
                            estimated_value=Decimal('5.00'),
                            confidence=pattern.get('confidence', 0.5),
                            requires_approval=False,
                            context={'pattern': pattern},
                        )
                        actions.append(action)

        except Exception as e:
            logger.debug(f"Error scanning optimization opportunities: {e}")

        return actions

    def _scan_collaboration_opportunities(self) -> List[AutonomousAction]:
        """Scan for agent collaboration opportunities."""
        actions = []

        try:
            # Check if there are pending tasks that would benefit from collaboration
            if self.learning_service:
                summary = self.learning_service.get_learning_summary(days=7)

                # If success rate is low, suggest collaboration
                if summary.get('success_rate', 1.0) < 0.7:
                    action = AutonomousAction(
                        id=str(uuid.uuid4()),
                        action_type=ActionType.AGENT_COLLABORATE,
                        risk_level=RiskLevel.MINIMAL,
                        description="Initiate agent collaboration for improved results",
                        reasoning=f"Recent success rate ({summary.get('success_rate', 0)*100:.0f}%) could benefit from multi-agent collaboration",
                        estimated_value=Decimal('15.00'),
                        confidence=0.7,
                        requires_approval=False,
                        context={'current_success_rate': summary.get('success_rate')},
                    )
                    actions.append(action)

        except Exception as e:
            logger.debug(f"Error scanning collaboration opportunities: {e}")

        return actions

    # ==================== Decision Making ====================

    def assess_action(self, action: AutonomousAction) -> Tuple[bool, str]:
        """
        Assess whether an action should be executed.

        Returns:
            Tuple of (should_execute, reason)
        """
        # Check autonomy level
        if self.config.level == AutonomyLevel.OBSERVE:
            return False, "Autonomy level is OBSERVE only"

        if self.config.level == AutonomyLevel.SUGGEST:
            return False, "Autonomy level is SUGGEST only (action queued for review)"

        # Check if in quiet hours
        if self._is_quiet_hours():
            return False, "Currently in quiet hours"

        # Check daily limits
        daily_stats = self._get_daily_stats()
        if daily_stats['action_count'] >= self.config.max_daily_actions:
            return False, f"Daily action limit reached ({self.config.max_daily_actions})"

        if daily_stats['total_value'] + action.estimated_value > self.config.max_daily_value:
            return False, f"Would exceed daily value limit (${self.config.max_daily_value})"

        # Check if approval required
        if action.requires_approval and not action.approved:
            if self.config.level == AutonomyLevel.ASSISTED:
                return False, "Action requires user approval"

        # Check risk level
        risk_order = list(RiskLevel)
        if risk_order.index(action.risk_level) > risk_order.index(self.config.risk_tolerance):
            return False, f"Risk level {action.risk_level.value} exceeds tolerance {self.config.risk_tolerance.value}"

        # Check action type allowed
        if action.action_type not in self.config.allowed_action_types:
            return False, f"Action type {action.action_type.value} not allowed"

        return True, "Action approved for execution"

    def _is_quiet_hours(self) -> bool:
        """Check if currently in quiet hours."""
        if not self.config.quiet_hours_start or not self.config.quiet_hours_end:
            return False

        current_hour = timezone.now().hour
        start = self.config.quiet_hours_start
        end = self.config.quiet_hours_end

        if start <= end:
            return start <= current_hour < end
        else:  # Spans midnight
            return current_hour >= start or current_hour < end

    def _get_daily_stats(self) -> Dict[str, Any]:
        """Get today's action statistics."""
        cache_key = f"{self.CACHE_PREFIX}daily_stats:{self.user.id if self.user else 'anon'}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        stats = {
            'action_count': 0,
            'total_value': Decimal('0.00'),
            'successful': 0,
            'failed': 0,
        }

        try:
            from core.models_unified_system import AutonomousActionLog
            today = timezone.now().date()
            logs = AutonomousActionLog.objects.filter(
                user=self.user,
                created_at__date=today,
            )

            stats['action_count'] = logs.count()
            stats['total_value'] = logs.aggregate(
                total=Sum('estimated_value')
            )['total'] or Decimal('0.00')
            stats['successful'] = logs.filter(success=True).count()
            stats['failed'] = logs.filter(success=False).count()

        except Exception as e:
            logger.debug(f"Error getting daily stats: {e}")

        cache.set(cache_key, stats, 300)  # 5 min cache
        return stats

    # ==================== Action Execution ====================

    def execute_action(self, action: AutonomousAction) -> AutonomousAction:
        """
        Execute an autonomous action.

        Returns:
            Updated action with execution result
        """
        # Assess first
        should_execute, reason = self.assess_action(action)
        if not should_execute:
            action.execution_result = {'error': reason}
            return action

        # Execute based on type
        try:
            if action.action_type == ActionType.OPPORTUNITY_APPLY:
                result = self._execute_opportunity_apply(action)
            elif action.action_type == ActionType.CONTENT_CREATE:
                result = self._execute_content_create(action)
            elif action.action_type == ActionType.SPIDER_DISPATCH:
                result = self._execute_spider_dispatch(action)
            elif action.action_type == ActionType.SYSTEM_OPTIMIZE:
                result = self._execute_system_optimize(action)
            elif action.action_type == ActionType.AGENT_COLLABORATE:
                result = self._execute_agent_collaborate(action)
            else:
                result = {'success': False, 'error': f'Unknown action type: {action.action_type}'}

            action.executed = True
            action.executed_at = timezone.now()
            action.success = result.get('success', False)
            action.execution_result = result

            # Record in database
            self._record_action(action)

            # Learn from outcome
            if self.config.learn_from_feedback and self.learning_service:
                self._record_learning(action)

            # Send notification if configured
            if self.config.notify_on_action:
                self._send_action_notification(action)

        except Exception as e:
            action.executed = True
            action.executed_at = timezone.now()
            action.success = False
            action.execution_result = {'error': str(e)}
            logger.error(f"Error executing autonomous action: {e}")

        return action

    def _execute_opportunity_apply(self, action: AutonomousAction) -> Dict:
        """Execute opportunity application."""
        # This would integrate with the actual application system
        opportunity_id = action.context.get('opportunity_id')

        logger.info(f"Autonomously applying to opportunity: {opportunity_id}")

        # Simulate success (in production, this would call actual APIs)
        return {
            'success': True,
            'action': 'opportunity_apply',
            'opportunity_id': opportunity_id,
            'message': 'Application submitted successfully',
        }

    def _execute_content_create(self, action: AutonomousAction) -> Dict:
        """Execute content creation."""
        # This would trigger the content creation pipeline
        logger.info(f"Autonomously creating content: {action.description}")

        return {
            'success': True,
            'action': 'content_create',
            'message': 'Content creation queued',
        }

    def _execute_spider_dispatch(self, action: AutonomousAction) -> Dict:
        """Execute spider dispatch."""
        categories = action.context.get('categories', [])

        try:
            from core.tasks import run_spider_by_category

            dispatched = 0
            for category in categories[:5]:  # Limit to 5 categories
                run_spider_by_category.delay(category, execution_mode='scheduled')
                dispatched += 1

            return {
                'success': True,
                'action': 'spider_dispatch',
                'categories_dispatched': dispatched,
                'message': f'Dispatched spiders for {dispatched} categories',
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }

    def _execute_system_optimize(self, action: AutonomousAction) -> Dict:
        """Execute system optimization."""
        pattern = action.context.get('pattern', {})

        logger.info(f"Applying system optimization: {action.description}")

        # Store optimization for use in coordinator
        cache_key = f"{self.CACHE_PREFIX}optimization:{pattern.get('pattern_type', 'general')}"
        cache.set(cache_key, pattern, 3600)  # 1 hour

        return {
            'success': True,
            'action': 'system_optimize',
            'message': 'Optimization applied',
        }

    def _execute_agent_collaborate(self, action: AutonomousAction) -> Dict:
        """Execute agent collaboration."""
        logger.info(f"Initiating agent collaboration: {action.description}")

        # This would trigger multi-agent collaboration
        return {
            'success': True,
            'action': 'agent_collaborate',
            'message': 'Collaboration mode activated',
        }

    def _record_action(self, action: AutonomousAction) -> None:
        """Record action in database."""
        try:
            from core.models_unified_system import AutonomousActionLog

            AutonomousActionLog.objects.create(
                user=self.user,
                action_id=action.id,
                action_type=action.action_type.value,
                risk_level=action.risk_level.value,
                description=action.description,
                reasoning=action.reasoning,
                estimated_value=action.estimated_value,
                confidence=action.confidence,
                required_approval=action.requires_approval,
                was_approved=action.approved,
                success=action.success,
                execution_result=action.execution_result,
                agents_involved=action.agents_involved,
                context=action.context,
            )

        except Exception as e:
            logger.error(f"Error recording autonomous action: {e}")

    def _record_learning(self, action: AutonomousAction) -> None:
        """Record action outcome for learning."""
        if not self.learning_service:
            return

        try:
            self.learning_service.record_outcome(
                query_type='autonomous_action',
                query_text=action.description,
                execution_mode='autonomous',
                agents_used=action.agents_involved,
                response=str(action.execution_result),
                execution_time_ms=0,
                success=action.success or False,
                metadata={
                    'action_type': action.action_type.value,
                    'risk_level': action.risk_level.value,
                    'estimated_value': float(action.estimated_value),
                }
            )
        except Exception as e:
            logger.debug(f"Error recording learning: {e}")

    def _send_action_notification(self, action: AutonomousAction) -> None:
        """Send notification about action."""
        if not self.proactive_system:
            return

        try:
            status = "completed successfully" if action.success else "failed"
            self.proactive_system.notification_manager.send_notification(
                user=self.user,
                notification_type='automation',
                title=f"Autonomous Action {status.title()}",
                message=f"{action.description} - {status}",
                priority='medium' if action.success else 'high',
                rich_content=action.to_dict(),
            )
        except Exception as e:
            logger.debug(f"Error sending notification: {e}")

    # ==================== Proactive Loop ====================

    def run_autonomy_cycle(self) -> Dict[str, Any]:
        """
        Run a complete autonomy cycle.

        This is the main entry point for autonomous operation.
        """
        results = {
            'timestamp': timezone.now().isoformat(),
            'user_id': self.user.id if self.user else None,
            'autonomy_level': self.config.level.value,
            'scanned_opportunities': 0,
            'actions_queued': 0,
            'actions_executed': 0,
            'actions_succeeded': 0,
            'actions_failed': 0,
            'total_value_generated': Decimal('0.00'),
        }

        # Scan for opportunities
        actions = self.scan_for_opportunities()
        results['scanned_opportunities'] = len(actions)

        # Process each action
        for action in actions:
            should_execute, reason = self.assess_action(action)

            if should_execute:
                executed = self.execute_action(action)
                results['actions_executed'] += 1

                if executed.success:
                    results['actions_succeeded'] += 1
                    results['total_value_generated'] += executed.estimated_value
                else:
                    results['actions_failed'] += 1
            else:
                # Queue for later or user approval
                results['actions_queued'] += 1

        # Log cycle results
        logger.info(
            f"Autonomy cycle complete: {results['actions_executed']} executed, "
            f"{results['actions_succeeded']} succeeded, "
            f"${results['total_value_generated']} value"
        )

        return results

    # ==================== Dashboard Data ====================

    def get_autonomy_dashboard(self) -> Dict[str, Any]:
        """Get autonomy dashboard data."""
        daily_stats = self._get_daily_stats()

        # Get pending actions from cache
        cache_key = f"{self.CACHE_PREFIX}pending_actions:{self.user.id if self.user else 'anon'}"
        pending_actions = cache.get(cache_key) or []

        # Get recent action logs
        recent_actions = []
        try:
            from core.models_unified_system import AutonomousActionLog
            logs = AutonomousActionLog.objects.filter(
                user=self.user
            ).order_by('-created_at')[:10]

            recent_actions = [
                {
                    'id': str(log.action_id),
                    'action_type': log.action_type,
                    'description': log.description,
                    'success': log.success,
                    'estimated_value': float(log.estimated_value) if log.estimated_value else 0,
                    'created_at': log.created_at.isoformat(),
                }
                for log in logs
            ]
        except Exception as e:
            logger.debug(f"Error getting recent actions: {e}")

        return {
            'config': self.config.to_dict(),
            'daily_stats': {
                'action_count': daily_stats['action_count'],
                'total_value': float(daily_stats['total_value']),
                'successful': daily_stats['successful'],
                'failed': daily_stats['failed'],
                'remaining_actions': self.config.max_daily_actions - daily_stats['action_count'],
                'remaining_value': float(self.config.max_daily_value - daily_stats['total_value']),
            },
            'pending_actions': pending_actions[:5],
            'recent_actions': recent_actions,
            'is_active': self.config.level not in [AutonomyLevel.OBSERVE],
            'is_quiet_hours': self._is_quiet_hours(),
        }


# ==================== Singleton Accessor ====================

_autonomy_engine_cache = {}


def get_autonomy_engine(user=None) -> AutonomyEngine:
    """Get or create autonomy engine for user."""
    cache_key = user.id if user else 'anon'
    if cache_key not in _autonomy_engine_cache:
        _autonomy_engine_cache[cache_key] = AutonomyEngine(user)
    return _autonomy_engine_cache[cache_key]
