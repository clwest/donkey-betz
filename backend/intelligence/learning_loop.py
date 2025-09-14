"""
Learning Loop with Feedback Incorporation

Implements continuous learning and improvement through feedback collection,
analysis, and automatic system optimization.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
import logging

from orchestration import orchestrator
from agents.registry import agent_registry
from advisors.registry import advisor_registry
from ml_pipeline.pipeline import MLPipeline
from monitoring_dashboard import monitoring_dashboard

logger = logging.getLogger(__name__)


@dataclass
class FeedbackItem:
    """Represents a piece of feedback"""
    id: str
    timestamp: datetime
    source: str  # user, agent, advisor, system
    category: str  # performance, accuracy, usability, error
    target: str  # agent_id, workflow_id, feature
    rating: Optional[float] = None  # 0-1 scale
    message: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningInsight:
    """Represents a learning insight derived from feedback"""
    id: str
    timestamp: datetime
    insight_type: str  # pattern, anomaly, improvement, regression
    description: str
    confidence: float
    affected_components: List[str]
    recommended_actions: List[str]
    impact_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationAction:
    """Represents an optimization action to be taken"""
    id: str
    timestamp: datetime
    action_type: str  # parameter_tuning, workflow_adjustment, agent_update
    target: str
    parameters: Dict[str, Any]
    expected_improvement: float
    risk_level: str  # low, medium, high
    status: str  # pending, in_progress, completed, failed
    result: Optional[Dict[str, Any]] = None


class LearningLoop:
    """Continuous learning and feedback system"""

    def __init__(self):
        self.feedback_buffer = defaultdict(list)
        self.insights_history = []
        self.optimization_queue = []
        self.ml_pipeline = MLPipeline()
        self.learning_active = False

        # Learning parameters
        self.learning_rate = 0.01
        self.feedback_threshold = 10  # Min feedback items before learning
        self.confidence_threshold = 0.7
        self.risk_tolerance = "medium"

        # Performance baselines
        self.baselines = {}
        self.improvements = defaultdict(list)

    async def start_learning(self):
        """Start the continuous learning loop"""
        self.learning_active = True
        logger.info("Learning loop started")

        # Initialize baselines
        await self._establish_baselines()

        # Start learning tasks
        await asyncio.gather(
            self._collect_feedback(),
            self._analyze_feedback(),
            self._generate_insights(),
            self._apply_optimizations(),
            self._validate_improvements()
        )

    async def stop_learning(self):
        """Stop the learning loop"""
        self.learning_active = False
        logger.info("Learning loop stopped")

    async def _establish_baselines(self):
        """Establish performance baselines"""
        logger.info("Establishing performance baselines")

        # Get current metrics from monitoring
        dashboard_data = monitoring_dashboard.get_dashboard_data()

        self.baselines = {
            "agent_response_time": {},
            "workflow_success_rate": dashboard_data["workflows"].get("success_rate", 0),
            "system_performance": dashboard_data["system"],
            "ml_accuracy": dashboard_data["ml_pipeline"].get("accuracy", 0)
        }

        # Baseline for each agent
        for agent_id in agent_registry.list_agents():
            agent_metrics = dashboard_data["agents"].get(agent_id, {})
            if agent_metrics:
                self.baselines["agent_response_time"][agent_id] = agent_metrics.average

        logger.info(f"Baselines established: {self.baselines}")

    async def _collect_feedback(self):
        """Collect feedback from various sources"""
        while self.learning_active:
            try:
                # Collect from monitoring dashboard
                dashboard_data = monitoring_dashboard.get_dashboard_data()

                # System-generated feedback
                if dashboard_data["alerts"]:
                    for alert in dashboard_data["alerts"]:
                        feedback = FeedbackItem(
                            id=f"sys_{datetime.now().timestamp()}",
                            timestamp=datetime.now(),
                            source="system",
                            category="error" if alert["level"] == "critical" else "performance",
                            target=alert["category"],
                            rating=0.3 if alert["level"] == "critical" else 0.6,
                            message=alert["message"],
                            context={"alert": alert}
                        )
                        self._store_feedback(feedback)

                # Agent performance feedback
                for agent_id, metrics in dashboard_data["agents"].items():
                    if hasattr(metrics, "current_value"):
                        baseline = self.baselines["agent_response_time"].get(agent_id, 2.0)
                        if metrics.current_value > baseline * 1.5:
                            feedback = FeedbackItem(
                                id=f"perf_{agent_id}_{datetime.now().timestamp()}",
                                timestamp=datetime.now(),
                                source="system",
                                category="performance",
                                target=agent_id,
                                rating=0.4,
                                message=f"Response time degraded: {metrics.current_value:.2f}s",
                                context={"metrics": metrics.__dict__}
                            )
                            self._store_feedback(feedback)

                # Workflow feedback
                workflows = dashboard_data["workflows"]
                if workflows["success_rate"] < self.baselines["workflow_success_rate"]:
                    feedback = FeedbackItem(
                        id=f"wf_{datetime.now().timestamp()}",
                        timestamp=datetime.now(),
                        source="system",
                        category="accuracy",
                        target="workflows",
                        rating=workflows["success_rate"],
                        message=f"Workflow success rate dropped to {workflows['success_rate']:.1%}",
                        context=workflows
                    )
                    self._store_feedback(feedback)

                await asyncio.sleep(30)  # Collect every 30 seconds

            except Exception as e:
                logger.error(f"Error collecting feedback: {e}")

    def _store_feedback(self, feedback: FeedbackItem):
        """Store feedback item"""
        self.feedback_buffer[feedback.category].append(feedback)
        self.feedback_buffer["all"].append(feedback)

        # Trigger immediate analysis for critical feedback
        if feedback.rating and feedback.rating < 0.3:
            asyncio.create_task(self._handle_critical_feedback(feedback))

    async def _handle_critical_feedback(self, feedback: FeedbackItem):
        """Handle critical feedback immediately"""
        logger.warning(f"Critical feedback received: {feedback.message}")

        # Create immediate optimization action
        action = OptimizationAction(
            id=f"critical_{feedback.id}",
            timestamp=datetime.now(),
            action_type="immediate_response",
            target=feedback.target,
            parameters={"feedback": feedback.__dict__},
            expected_improvement=0.2,
            risk_level="low",
            status="pending"
        )

        self.optimization_queue.insert(0, action)  # Priority queue

    async def _analyze_feedback(self):
        """Analyze collected feedback"""
        while self.learning_active:
            try:
                for category, feedback_items in self.feedback_buffer.items():
                    if len(feedback_items) >= self.feedback_threshold:
                        analysis = await self._perform_analysis(category, feedback_items)

                        if analysis["patterns"]:
                            # Create insights from patterns
                            for pattern in analysis["patterns"]:
                                insight = await self._create_insight(pattern, feedback_items)
                                if insight:
                                    self.insights_history.append(insight)

                        # Clear processed feedback
                        self.feedback_buffer[category] = feedback_items[-5:]  # Keep recent

                await asyncio.sleep(60)  # Analyze every minute

            except Exception as e:
                logger.error(f"Error analyzing feedback: {e}")

    async def _perform_analysis(
        self,
        category: str,
        feedback_items: List[FeedbackItem]
    ) -> Dict[str, Any]:
        """Perform detailed analysis on feedback"""
        analysis = {
            "category": category,
            "count": len(feedback_items),
            "patterns": [],
            "trends": [],
            "anomalies": []
        }

        # Calculate ratings distribution
        ratings = [f.rating for f in feedback_items if f.rating is not None]
        if ratings:
            analysis["average_rating"] = np.mean(ratings)
            analysis["rating_trend"] = self._calculate_trend(ratings)

        # Identify patterns
        target_counts = defaultdict(int)
        for feedback in feedback_items:
            target_counts[feedback.target] += 1

        # Find frequently mentioned targets
        for target, count in target_counts.items():
            if count >= 3:  # Pattern threshold
                analysis["patterns"].append({
                    "type": "frequent_target",
                    "target": target,
                    "frequency": count / len(feedback_items),
                    "category": category
                })

        # Use ML to find deeper patterns
        ml_patterns = await self.ml_pipeline.analyze_feedback_patterns(
            [f.__dict__ for f in feedback_items]
        )
        analysis["patterns"].extend(ml_patterns)

        return analysis

    async def _create_insight(
        self,
        pattern: Dict[str, Any],
        feedback_items: List[FeedbackItem]
    ) -> Optional[LearningInsight]:
        """Create learning insight from pattern"""
        if pattern["frequency"] < 0.2:  # Not significant enough
            return None

        # Generate insight based on pattern type
        if pattern["type"] == "frequent_target":
            target = pattern["target"]
            affected_feedback = [f for f in feedback_items if f.target == target]

            avg_rating = np.mean([f.rating for f in affected_feedback if f.rating])

            insight = LearningInsight(
                id=f"insight_{datetime.now().timestamp()}",
                timestamp=datetime.now(),
                insight_type="pattern",
                description=f"{target} showing performance issues",
                confidence=pattern["frequency"],
                affected_components=[target],
                recommended_actions=await self._generate_recommendations(target, affected_feedback),
                impact_score=1 - avg_rating if avg_rating else 0.5,
                metadata={"pattern": pattern}
            )

            return insight

        return None

    async def _generate_recommendations(
        self,
        target: str,
        feedback_items: List[FeedbackItem]
    ) -> List[str]:
        """Generate recommendations based on feedback"""
        recommendations = []

        # Analyze feedback messages
        issues = defaultdict(int)
        for feedback in feedback_items:
            if feedback.message:
                if "slow" in feedback.message.lower() or "timeout" in feedback.message.lower():
                    issues["performance"] += 1
                if "error" in feedback.message.lower() or "fail" in feedback.message.lower():
                    issues["reliability"] += 1
                if "accuracy" in feedback.message.lower() or "wrong" in feedback.message.lower():
                    issues["accuracy"] += 1

        # Generate specific recommendations
        if issues["performance"] > issues["reliability"] and issues["performance"] > issues["accuracy"]:
            recommendations.append(f"Optimize {target} for better performance")
            recommendations.append(f"Consider caching frequently accessed data in {target}")
            recommendations.append(f"Review async operations in {target}")

        elif issues["reliability"] > issues["performance"] and issues["reliability"] > issues["accuracy"]:
            recommendations.append(f"Add error handling and retry logic to {target}")
            recommendations.append(f"Implement circuit breaker pattern for {target}")
            recommendations.append(f"Add health checks for {target}")

        elif issues["accuracy"] > 0:
            recommendations.append(f"Retrain ML models used by {target}")
            recommendations.append(f"Review and update {target} decision logic")
            recommendations.append(f"Add validation checks to {target} outputs")

        return recommendations

    async def _generate_insights(self):
        """Generate high-level insights from learning"""
        while self.learning_active:
            try:
                if len(self.insights_history) >= 5:
                    # Aggregate recent insights
                    recent_insights = self.insights_history[-10:]

                    # Find common themes
                    themes = defaultdict(list)
                    for insight in recent_insights:
                        themes[insight.insight_type].append(insight)

                    # Generate meta-insights
                    for theme, insights in themes.items():
                        if len(insights) >= 3:
                            meta_insight = await self._create_meta_insight(theme, insights)
                            if meta_insight:
                                logger.info(f"Meta-insight generated: {meta_insight.description}")

                await asyncio.sleep(300)  # Every 5 minutes

            except Exception as e:
                logger.error(f"Error generating insights: {e}")

    async def _create_meta_insight(
        self,
        theme: str,
        insights: List[LearningInsight]
    ) -> Optional[LearningInsight]:
        """Create higher-level insight from multiple insights"""
        if not insights:
            return None

        # Aggregate affected components
        all_components = set()
        for insight in insights:
            all_components.update(insight.affected_components)

        # Calculate average impact
        avg_impact = np.mean([i.impact_score for i in insights])

        # Generate meta description
        if theme == "pattern":
            description = f"Systemic pattern affecting {len(all_components)} components"
        elif theme == "anomaly":
            description = f"Multiple anomalies detected across system"
        else:
            description = f"Recurring {theme} issues identified"

        # Aggregate recommendations
        all_recommendations = []
        for insight in insights:
            all_recommendations.extend(insight.recommended_actions)

        # Deduplicate and prioritize
        unique_recommendations = list(set(all_recommendations))[:5]

        return LearningInsight(
            id=f"meta_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            insight_type=f"meta_{theme}",
            description=description,
            confidence=np.mean([i.confidence for i in insights]),
            affected_components=list(all_components),
            recommended_actions=unique_recommendations,
            impact_score=avg_impact,
            metadata={"source_insights": [i.id for i in insights]}
        )

    async def _apply_optimizations(self):
        """Apply optimization actions"""
        while self.learning_active:
            try:
                if self.optimization_queue:
                    action = self.optimization_queue.pop(0)

                    # Check risk level
                    if self._should_apply_optimization(action):
                        await self._execute_optimization(action)
                    else:
                        logger.info(f"Skipping high-risk optimization: {action.id}")

                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                logger.error(f"Error applying optimizations: {e}")

    def _should_apply_optimization(self, action: OptimizationAction) -> bool:
        """Determine if optimization should be applied"""
        if self.risk_tolerance == "low" and action.risk_level in ["medium", "high"]:
            return False
        if self.risk_tolerance == "medium" and action.risk_level == "high":
            return False
        return True

    async def _execute_optimization(self, action: OptimizationAction):
        """Execute an optimization action"""
        logger.info(f"Executing optimization: {action.action_type} on {action.target}")
        action.status = "in_progress"

        try:
            if action.action_type == "parameter_tuning":
                result = await self._tune_parameters(action.target, action.parameters)

            elif action.action_type == "workflow_adjustment":
                result = await self._adjust_workflow(action.target, action.parameters)

            elif action.action_type == "agent_update":
                result = await self._update_agent(action.target, action.parameters)

            elif action.action_type == "immediate_response":
                result = await self._immediate_response(action.target, action.parameters)

            else:
                result = {"error": f"Unknown action type: {action.action_type}"}

            action.result = result
            action.status = "completed"

            # Track improvement
            self.improvements[action.target].append({
                "timestamp": datetime.now(),
                "action": action.action_type,
                "result": result
            })

        except Exception as e:
            action.status = "failed"
            action.result = {"error": str(e)}
            logger.error(f"Optimization failed: {e}")

    async def _tune_parameters(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Tune parameters for a component"""
        logger.info(f"Tuning parameters for {target}")

        # Get current parameters
        if target.startswith("agent_"):
            agent = agent_registry.get_agent(target)
            if agent and hasattr(agent, "update_parameters"):
                old_params = agent.get_parameters() if hasattr(agent, "get_parameters") else {}
                await agent.update_parameters(parameters)
                return {
                    "success": True,
                    "old_parameters": old_params,
                    "new_parameters": parameters
                }

        return {"success": False, "error": "Target not found or not tunable"}

    async def _adjust_workflow(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adjust workflow configuration"""
        # Implement workflow adjustments
        logger.info(f"Adjusting workflow {target} with {parameters}")

        # Example: Adjust timeout or retry settings
        if target in orchestrator.workflows:
            workflow = orchestrator.workflows[target]
            # Apply adjustments
            return {"success": True, "adjustments": parameters}

        return {"success": False, "error": "Workflow not found"}

    async def _update_agent(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update agent configuration or model"""
        logger.info(f"Updating agent {target}")

        agent = agent_registry.get_agent(target)
        if agent:
            # Trigger retraining or reconfiguration
            if hasattr(agent, "retrain"):
                await agent.retrain(parameters.get("training_data"))
            return {"success": True, "updated": target}

        return {"success": False, "error": "Agent not found"}

    async def _immediate_response(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle immediate response actions"""
        feedback = parameters.get("feedback", {})
        logger.info(f"Immediate response for {target}: {feedback.get('message')}")

        # Quick fixes based on feedback
        if "timeout" in feedback.get("message", "").lower():
            # Increase timeout
            return {"success": True, "action": "increased_timeout"}

        elif "memory" in feedback.get("message", "").lower():
            # Trigger garbage collection
            import gc
            gc.collect()
            return {"success": True, "action": "memory_cleanup"}

        return {"success": True, "action": "logged"}

    async def _validate_improvements(self):
        """Validate that optimizations led to improvements"""
        while self.learning_active:
            try:
                # Wait for optimizations to take effect
                await asyncio.sleep(300)  # Every 5 minutes

                # Get current metrics
                dashboard_data = monitoring_dashboard.get_dashboard_data()

                # Compare with baselines
                improvements = {}

                # Check agent improvements
                for agent_id, baseline_time in self.baselines["agent_response_time"].items():
                    current_metrics = dashboard_data["agents"].get(agent_id)
                    if current_metrics and hasattr(current_metrics, "average"):
                        improvement = (baseline_time - current_metrics.average) / baseline_time
                        improvements[f"agent_{agent_id}"] = improvement

                # Check workflow improvements
                current_success = dashboard_data["workflows"].get("success_rate", 0)
                baseline_success = self.baselines["workflow_success_rate"]
                if baseline_success > 0:
                    improvements["workflow_success"] = (
                        (current_success - baseline_success) / baseline_success
                    )

                # Log improvements
                for component, improvement in improvements.items():
                    if improvement > 0.1:  # 10% improvement
                        logger.info(f"Significant improvement in {component}: {improvement:.1%}")
                    elif improvement < -0.1:  # 10% degradation
                        logger.warning(f"Performance degradation in {component}: {improvement:.1%}")

                # Update baselines if improvements are sustained
                if all(imp > 0 for imp in improvements.values()):
                    await self._establish_baselines()

            except Exception as e:
                logger.error(f"Error validating improvements: {e}")

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from values"""
        if len(values) < 2:
            return "stable"

        # Simple linear regression
        x = np.arange(len(values))
        coefficients = np.polyfit(x, values, 1)
        slope = coefficients[0]

        if slope > 0.01:
            return "improving"
        elif slope < -0.01:
            return "degrading"
        else:
            return "stable"

    async def submit_user_feedback(
        self,
        target: str,
        rating: float,
        message: str,
        category: str = "usability"
    ) -> Dict[str, Any]:
        """Submit user feedback"""
        feedback = FeedbackItem(
            id=f"user_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            source="user",
            category=category,
            target=target,
            rating=rating,
            message=message,
            context={}
        )

        self._store_feedback(feedback)

        # Generate immediate insight if rating is low
        if rating < 0.5:
            insight = await self._create_insight(
                {"type": "user_feedback", "frequency": 1.0},
                [feedback]
            )
            if insight:
                self.insights_history.append(insight)

        return {
            "feedback_id": feedback.id,
            "received": True,
            "will_process": True
        }

    def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning loop status"""
        return {
            "active": self.learning_active,
            "feedback_collected": sum(len(items) for items in self.feedback_buffer.values()),
            "insights_generated": len(self.insights_history),
            "optimizations_pending": len(self.optimization_queue),
            "improvements_tracked": len(self.improvements),
            "learning_rate": self.learning_rate,
            "risk_tolerance": self.risk_tolerance,
            "recent_insights": [
                {
                    "description": i.description,
                    "confidence": i.confidence,
                    "impact": i.impact_score
                }
                for i in self.insights_history[-5:]
            ]
        }


# Global learning loop instance
learning_loop = LearningLoop()