"""
Session 823: Metrics Action Trigger Service

This service enables self-execution by automatically triggering corrective
actions when live system metrics indicate problems.

The system is now:
- Self-Aware: Can query its own state via _gather_live_system_metrics()
- Self-Executing: Automatically acts on problems via this trigger service

Trigger conditions map metrics to actions:
- spider_entries_24h == 0 → Run spider collection
- open_findings > 100 → Trigger remediation cycle
- body system unhealthy → Trigger health recovery
- high error rates → Trigger investigation
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional
from enum import Enum

from django.utils import timezone

logger = logging.getLogger(__name__)


class ActionPriority(Enum):
    """Priority levels for triggered actions."""
    CRITICAL = 0  # Execute immediately
    HIGH = 1      # Execute within the hour
    MEDIUM = 2    # Execute within the day
    LOW = 3       # Execute when convenient


class ActionType(Enum):
    """Types of actions that can be triggered."""
    CELERY_TASK = "celery_task"
    AGENT_EXECUTION = "agent_execution"
    MANAGEMENT_COMMAND = "management_command"
    ALERT = "alert"
    LOG_ONLY = "log_only"


@dataclass
class TriggerCondition:
    """Defines a condition that triggers an action."""
    name: str
    description: str
    metric_path: str  # e.g., "activity.spider_entries_24h"
    operator: str     # "==", "<", ">", "<=", ">="
    threshold: Any
    priority: ActionPriority
    cooldown_hours: int = 4  # Don't re-trigger within this window


@dataclass
class TriggerAction:
    """Defines an action to take when a condition is met."""
    name: str
    action_type: ActionType
    target: str  # Task name, agent name, or command
    description: str = ""
    kwargs: Optional[Dict[str, Any]] = None


@dataclass
class TriggerRule:
    """A complete rule combining condition and action."""
    condition: TriggerCondition
    action: TriggerAction
    enabled: bool = True


class MetricsActionTrigger:
    """
    Session 823: Self-Execution Engine

    Evaluates live metrics against trigger conditions and executes
    corrective actions automatically.
    """

    def __init__(self):
        self.rules = self._build_default_rules()
        self.last_triggered: Dict[str, datetime] = {}

    def _build_default_rules(self) -> List[TriggerRule]:
        """Build the default set of trigger rules."""
        return [
            # =================================================================
            # SPIDER DATA COLLECTION
            # =================================================================
            TriggerRule(
                condition=TriggerCondition(
                    name="no_spider_data_24h",
                    description="No spider data collected in 24 hours",
                    metric_path="activity.spider_entries_24h",
                    operator="==",
                    threshold=0,
                    priority=ActionPriority.HIGH,
                    cooldown_hours=2,
                ),
                action=TriggerAction(
                    name="run_spider_collection",
                    action_type=ActionType.CELERY_TASK,
                    target="core.tasks.run_spider_network",
                    description="Trigger spider data collection cycle",
                ),
            ),

            TriggerRule(
                condition=TriggerCondition(
                    name="low_spider_data_24h",
                    description="Less than 100 spider entries in 24 hours",
                    metric_path="activity.spider_entries_24h",
                    operator="<",
                    threshold=100,
                    priority=ActionPriority.MEDIUM,
                    cooldown_hours=6,
                ),
                action=TriggerAction(
                    name="boost_spider_collection",
                    action_type=ActionType.CELERY_TASK,
                    target="core.tasks.run_spider_by_category",
                    kwargs={"category": "news"},
                    description="Run news category spiders",
                ),
            ),

            # =================================================================
            # AUTONOMOUS REMEDIATION
            # Session 1028: Disabled — execution schedules were disabled in Session 1027
            # (PR #1271) to save ~$9/day. These metric triggers were bypassing that
            # by re-triggering remediation via the hourly metrics check. Discovery
            # and assignment remain active; execution is manual via Claude Code.
            # =================================================================

            # =================================================================
            # BODY SYSTEM HEALTH
            # =================================================================
            TriggerRule(
                condition=TriggerCondition(
                    name="heart_unhealthy",
                    description="HEART system reporting unhealthy status",
                    metric_path="health.heart.status",
                    operator="==",
                    threshold="error",
                    priority=ActionPriority.CRITICAL,
                    cooldown_hours=1,
                ),
                action=TriggerAction(
                    name="heart_health_check",
                    action_type=ActionType.MANAGEMENT_COMMAND,
                    target="heart_check",
                    description="Run comprehensive heart health check",
                ),
            ),

            TriggerRule(
                condition=TriggerCondition(
                    name="skin_dormant_too_long",
                    description="SKIN system dormant (no workspace activity)",
                    metric_path="health.skin.status",
                    operator="==",
                    threshold="dormant",
                    priority=ActionPriority.LOW,
                    cooldown_hours=24,
                ),
                action=TriggerAction(
                    name="log_skin_dormancy",
                    action_type=ActionType.LOG_ONLY,
                    target="",
                    description="Log that SKIN layer has no recent activity",
                ),
            ),

            # =================================================================
            # AGENT ACTIVITY
            # =================================================================
            TriggerRule(
                condition=TriggerCondition(
                    name="no_agent_executions_24h",
                    description="No agent executions in 24 hours",
                    metric_path="activity.agent_executions_24h",
                    operator="==",
                    threshold=0,
                    priority=ActionPriority.HIGH,
                    cooldown_hours=4,
                ),
                action=TriggerAction(
                    name="trigger_agent_health_check",
                    action_type=ActionType.CELERY_TASK,
                    target="core.tasks.run_agent_health_rotation",
                    description="Run agent health check rotation",
                ),
            ),

            TriggerRule(
                condition=TriggerCondition(
                    name="high_agent_failure_rate",
                    description="More than 10 failed agent executions in 24h",
                    metric_path="activity.failed_executions_24h",
                    operator=">",
                    threshold=10,
                    priority=ActionPriority.HIGH,
                    cooldown_hours=6,
                ),
                action=TriggerAction(
                    name="investigate_agent_failures",
                    action_type=ActionType.AGENT_EXECUTION,
                    target="SystemIntelligenceAgent",
                    kwargs={"task": "Investigate recent agent failures and recommend fixes"},
                    description="Use SystemIntelligenceAgent to investigate failures",
                ),
            ),

            # =================================================================
            # REVENUE TRACKING
            # =================================================================
            TriggerRule(
                condition=TriggerCondition(
                    name="zero_revenue_7d",
                    description="No revenue recorded in 7 days",
                    metric_path="revenue.last_7_days",
                    operator="==",
                    threshold=0.0,
                    priority=ActionPriority.MEDIUM,
                    cooldown_hours=24,
                ),
                action=TriggerAction(
                    name="check_revenue_pipeline",
                    action_type=ActionType.AGENT_EXECUTION,
                    target="OpportunityScoringAgent",
                    kwargs={"task": "Analyze why no revenue has been recorded and identify opportunities"},
                    description="Use OpportunityScoringAgent to find revenue opportunities",
                ),
            ),

            # =================================================================
            # LLM COST MANAGEMENT
            # =================================================================
            TriggerRule(
                condition=TriggerCondition(
                    name="high_llm_cost_24h",
                    description="LLM costs exceed $10 in 24 hours",
                    metric_path="activity.llm_cost_24h",
                    operator=">",
                    threshold=10.0,
                    priority=ActionPriority.MEDIUM,
                    cooldown_hours=12,
                ),
                action=TriggerAction(
                    name="alert_high_llm_cost",
                    action_type=ActionType.ALERT,
                    target="high_cost_alert",
                    description="Alert about high LLM costs",
                ),
            ),
        ]

    def _get_metric_value(self, metrics: Dict, path: str) -> Any:
        """
        Get a value from nested metrics dict using dot notation.
        e.g., "activity.spider_entries_24h" → metrics['activity']['spider_entries_24h']
        """
        parts = path.split(".")
        value = metrics
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
                if value is None:
                    return None
            else:
                return None
        return value

    def _evaluate_condition(self, condition: TriggerCondition, metrics: Dict) -> bool:
        """Evaluate if a condition is met based on current metrics."""
        value = self._get_metric_value(metrics, condition.metric_path)

        if value is None:
            logger.debug(f"Metric {condition.metric_path} not found in metrics")
            return False

        threshold = condition.threshold

        try:
            if condition.operator == "==":
                return value == threshold
            elif condition.operator == "!=":
                return value != threshold
            elif condition.operator == "<":
                return float(value) < float(threshold)
            elif condition.operator == ">":
                return float(value) > float(threshold)
            elif condition.operator == "<=":
                return float(value) <= float(threshold)
            elif condition.operator == ">=":
                return float(value) >= float(threshold)
            else:
                logger.warning(f"Unknown operator: {condition.operator}")
                return False
        except (ValueError, TypeError) as e:
            logger.warning(f"Error evaluating condition {condition.name}: {e}")
            return False

    def _is_in_cooldown(self, rule_name: str, cooldown_hours: int) -> bool:
        """Check if a rule is still in cooldown period."""
        if rule_name not in self.last_triggered:
            return False

        last_time = self.last_triggered[rule_name]
        cooldown_end = last_time + timedelta(hours=cooldown_hours)
        return timezone.now() < cooldown_end

    def _execute_action(self, action: TriggerAction) -> Dict[str, Any]:
        """Execute a triggered action."""
        result = {
            "action": action.name,
            "type": action.action_type.value,
            "target": action.target,
            "success": False,
            "message": "",
        }

        try:
            if action.action_type == ActionType.CELERY_TASK:
                # Import and call the Celery task dynamically
                import importlib
                module_path, task_name = action.target.rsplit(".", 1)
                module = importlib.import_module(module_path)
                task_func = getattr(module, task_name, None)
                if task_func and hasattr(task_func, 'delay'):
                    kwargs = action.kwargs or {}
                    task_func.delay(**kwargs)
                    result["success"] = True
                    result["message"] = f"Triggered Celery task: {action.target}"
                else:
                    result["message"] = f"Celery task not found: {action.target}"

            elif action.action_type == ActionType.AGENT_EXECUTION:
                # Execute via agent - queue for async execution
                kwargs = action.kwargs or {}
                task = kwargs.get("task", "Perform automated check")
                # Queue for async execution via Celery
                from core.tasks import execute_agent_task
                execute_agent_task.delay(action.target, task)
                result["success"] = True
                result["message"] = f"Queued agent execution: {action.target}"

            elif action.action_type == ActionType.MANAGEMENT_COMMAND:
                # Run Django management command
                from django.core.management import call_command
                from io import StringIO
                out = StringIO()
                call_command(action.target, stdout=out)
                result["success"] = True
                result["message"] = f"Ran command: {action.target}"
                result["output"] = out.getvalue()[:500]

            elif action.action_type == ActionType.ALERT:
                # Create an alert/notification
                logger.warning(f"[ALERT] {action.description}: {action.target}")
                result["success"] = True
                result["message"] = f"Alert logged: {action.target}"

            elif action.action_type == ActionType.LOG_ONLY:
                logger.info(f"[METRICS] {action.description}")
                result["success"] = True
                result["message"] = "Logged observation"

            else:
                result["message"] = f"Unknown action type: {action.action_type}"

        except Exception as e:
            result["message"] = f"Error executing action: {str(e)}"
            logger.exception(f"Error executing action {action.name}")

        return result

    def evaluate_and_trigger(self, metrics: Dict) -> Dict[str, Any]:
        """
        Main entry point: evaluate all rules against metrics and trigger actions.

        Returns a summary of what was triggered.
        """
        results = {
            "timestamp": timezone.now().isoformat(),
            "rules_evaluated": 0,
            "conditions_met": 0,
            "actions_triggered": 0,
            "actions_skipped_cooldown": 0,
            "actions": [],
            "errors": [],
        }

        for rule in self.rules:
            if not rule.enabled:
                continue

            results["rules_evaluated"] += 1

            try:
                if self._evaluate_condition(rule.condition, metrics):
                    results["conditions_met"] += 1

                    # Check cooldown
                    if self._is_in_cooldown(rule.condition.name, rule.condition.cooldown_hours):
                        results["actions_skipped_cooldown"] += 1
                        logger.debug(f"Rule {rule.condition.name} in cooldown, skipping")
                        continue

                    # Execute action
                    logger.info(f"🎯 Trigger condition met: {rule.condition.name}")
                    logger.info(f"   → Executing action: {rule.action.name}")

                    action_result = self._execute_action(rule.action)
                    results["actions"].append({
                        "rule": rule.condition.name,
                        "priority": rule.condition.priority.name,
                        **action_result,
                    })

                    if action_result["success"]:
                        results["actions_triggered"] += 1
                        self.last_triggered[rule.condition.name] = timezone.now()

            except Exception as e:
                results["errors"].append({
                    "rule": rule.condition.name,
                    "error": str(e),
                })
                logger.exception(f"Error evaluating rule {rule.condition.name}")

        return results

    def get_rules_summary(self) -> List[Dict]:
        """Get a summary of all configured rules."""
        return [
            {
                "name": rule.condition.name,
                "description": rule.condition.description,
                "metric": rule.condition.metric_path,
                "threshold": f"{rule.condition.operator} {rule.condition.threshold}",
                "priority": rule.condition.priority.name,
                "action": rule.action.name,
                "action_type": rule.action.action_type.value,
                "enabled": rule.enabled,
                "in_cooldown": self._is_in_cooldown(
                    rule.condition.name, rule.condition.cooldown_hours
                ),
            }
            for rule in self.rules
        ]
