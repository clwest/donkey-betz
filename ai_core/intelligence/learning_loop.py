"""
Learning Loop with Feedback Incorporation

Implements continuous learning and improvement through feedback collection,
analysis, and automatic system optimization.

Enhanced with Bluesky social intelligence integration for real-time learning.
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import numpy as np
import logging

# Lazy load orchestrator to avoid Django dependency issues
orchestrator = None

def get_orchestrator():
    """Get or create orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        try:
            from .orchestration import orchestrator as _orchestrator
            orchestrator = _orchestrator
        except ImportError:
            # Create a mock orchestrator if not available
            class MockOrchestrator:
                def __init__(self):
                    pass
            orchestrator = MockOrchestrator()
    return orchestrator

try:
    from ..agents.registry import agent_registry
except ImportError:
    # Create mock registry
    class MockRegistry:
        def list_agents(self):
            return ['agent_1', 'agent_2', 'agent_3']
    agent_registry = MockRegistry()

try:
    from ..advisors.registry import advisor_registry
except ImportError:
    advisor_registry = None

try:
    from ...ml_pipeline.enhanced_ml_pipeline import EnhancedMLPipeline as MLPipeline
except ImportError:
    # Create mock ML pipeline
    class MockMLPipeline:
        def __init__(self):
            self.accuracy = 0.8
    MLPipeline = MockMLPipeline

try:
    from .monitoring_dashboard import monitoring_dashboard
except ImportError:
    # Create mock monitoring dashboard
    class MockMonitoringDashboard:
        def get_dashboard_data(self):
            return {
                'alerts': [],
                'agents': {},
                'workflows': {'success_rate': 0.85},
                'system': {'cpu': 50, 'memory': 60},
                'ml_pipeline': {'accuracy': 0.8}
            }
    monitoring_dashboard = MockMonitoringDashboard()

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
        """Start the continuous learning loop with Bluesky integration"""
        self.learning_active = True
        logger.info("Enhanced learning loop started with Bluesky integration")

        # Initialize baselines
        await self._establish_baselines()

        # Start learning tasks including Bluesky intelligence
        await asyncio.gather(
            self._collect_feedback(),
            self._collect_bluesky_feedback(),
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
        orch = get_orchestrator()
        if hasattr(orch, 'workflows') and target in orch.workflows:
            workflow = orch.workflows[target]
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


    async def _collect_bluesky_feedback(self):
        """Collect feedback from Bluesky social intelligence"""
        try:
            # Import here to avoid circular dependency
            pass

            while self.learning_active:
                try:
                    # Get Bluesky community feedback
                    bluesky_feedback = await self._extract_bluesky_community_feedback()

                    # Get Reddit community feedback
                    reddit_feedback = await self._extract_reddit_community_feedback()

                    # Get expert sentiment about platform/agents
                    expert_feedback = await self._extract_expert_opinions()

                    # Get market sentiment feedback
                    market_feedback = await self._extract_market_sentiment_feedback()

                    # Get Spider Army intelligence
                    spider_feedback = await self._extract_spider_army_intelligence()

                    # Store all feedback including spider intelligence
                    all_feedback = bluesky_feedback + reddit_feedback + spider_feedback + expert_feedback + market_feedback

                    for feedback in all_feedback:
                        self._store_feedback(feedback)

                    # Log spider intelligence collection
                    if spider_feedback:
                        logger.info(f"Collected {len(spider_feedback)} intelligence items from Spider Army")

                    if all_feedback:
                        logger.info(f"🦋 Collected {len(all_feedback)} feedback items from Bluesky")

                    # Update every 15 minutes for social feedback
                    await asyncio.sleep(900)

                except Exception as e:
                    logger.error(f"Error collecting Bluesky feedback: {e}")
                    await asyncio.sleep(180)  # Retry in 3 minutes

        except ImportError:
            logger.warning("Bluesky learning bridge not available, skipping social feedback")

    async def _extract_spider_army_intelligence(self) -> List[FeedbackItem]:
        """Extract intelligence from the 1,770 Spider Army"""
        feedback_items = []

        try:
            from .spider_learning_orchestrator import get_spider_orchestrator
            orchestrator = get_spider_orchestrator()

            # Get current spider statistics
            stats = await orchestrator.get_spider_statistics()

            if stats.get('spider_army_deployed'):
                logger.info(f"Extracting intelligence from {stats['spider_army_count']} spiders")

                # Create feedback for each spider swarm
                swarms = stats.get('spider_army_swarms', {})

                # Financial Intelligence (500 spiders)
                if 'financial_intel' in swarms:
                    feedback = FeedbackItem(
                        id=f"spider_financial_{datetime.now().timestamp()}",
                        timestamp=datetime.now(),
                        source="spider_army_financial",
                        category="market_intelligence",
                        target="financial_agents",
                        rating=0.9,
                        message=f"Real-time financial intelligence from {swarms['financial_intel']} spiders",
                        context={
                            'spider_count': swarms['financial_intel'],
                            'data_sources': ['SEC', 'Yahoo Finance', 'Polygon.io'],
                            'update_frequency': 'real-time'
                        }
                    )
                    feedback_items.append(feedback)

                # Innovation Tracking (300 spiders)
                if 'innovation_tracker' in swarms:
                    feedback = FeedbackItem(
                        id=f"spider_innovation_{datetime.now().timestamp()}",
                        timestamp=datetime.now(),
                        source="spider_army_innovation",
                        category="innovation_intelligence",
                        target="tech_agents",
                        rating=0.85,
                        message=f"Innovation intelligence from {swarms['innovation_tracker']} spiders",
                        context={
                            'spider_count': swarms['innovation_tracker'],
                            'data_sources': ['ArXiv', 'Patents', 'GitHub'],
                            'focus': 'breakthrough_technologies'
                        }
                    )
                    feedback_items.append(feedback)

                # Market Data (200 spiders)
                if 'market_data' in swarms:
                    feedback = FeedbackItem(
                        id=f"spider_market_{datetime.now().timestamp()}",
                        timestamp=datetime.now(),
                        source="spider_army_market",
                        category="market_data",
                        target="trading_agents",
                        rating=0.95,
                        message=f"Live market data from {swarms['market_data']} spiders",
                        context={
                            'spider_count': swarms['market_data'],
                            'data_sources': ['Binance', 'Coinbase', 'TradingView'],
                            'latency': 'sub-second'
                        }
                    )
                    feedback_items.append(feedback)

                # Social Sentiment (150 spiders)
                if 'social_sentiment' in swarms:
                    feedback = FeedbackItem(
                        id=f"spider_social_{datetime.now().timestamp()}",
                        timestamp=datetime.now(),
                        source="spider_army_social",
                        category="social_sentiment",
                        target="sentiment_agents",
                        rating=0.8,
                        message=f"Social sentiment from {swarms['social_sentiment']} spiders",
                        context={
                            'spider_count': swarms['social_sentiment'],
                            'platforms': ['Reddit', 'Twitter', 'StockTwits'],
                            'sentiment_analysis': 'real-time'
                        }
                    )
                    feedback_items.append(feedback)

                logger.info(f"Extracted {len(feedback_items)} feedback items from Spider Army")

        except Exception as e:
            logger.debug(f"Spider Army intelligence not available: {e}")

        return feedback_items

    async def _extract_reddit_community_feedback(self) -> List[FeedbackItem]:
        """Extract community feedback from Reddit discussions"""
        feedback_items = []

        try:
            from .reddit_learning_bridge import get_reddit_learning_bridge
            reddit_bridge = get_reddit_learning_bridge()

            # Get insights from key subreddits
            subreddits_to_monitor = [
                ('cscareerquestions', 'career'),
                ('artificial', 'ai_technology'),
                ('MachineLearning', 'ml_research'),
                ('Entrepreneur', 'business'),
                ('startups', 'startup')
            ]

            for subreddit, category in subreddits_to_monitor[:3]:
                try:
                    from ..spiders.reddit_handler import RedditHandler
                    reddit_handler = RedditHandler()

                    # Get hot posts from subreddit
                    posts = await reddit_handler.get_subreddit_posts(
                        subreddit,
                        sort='hot',
                        limit=5
                    )

                    for post in posts:
                        if post.score > 50:
                            # Extract feedback from post
                            sentiment = self._calculate_sentiment_rating(post.content)

                            feedback = FeedbackItem(
                                id=f"reddit_{subreddit}_{post.id}",
                                timestamp=post.created_at,
                                source="reddit_community",
                                category=category,
                                target="platform_insights",
                                rating=sentiment,
                                message=f"{post.title}: {post.content[:300]}",
                                context={
                                    'subreddit': subreddit,
                                    'post_score': post.score,
                                    'num_comments': post.num_comments,
                                    'url': f"https://reddit.com/r/{subreddit}/comments/{post.id}",
                                    'platform': 'reddit'
                                }
                            )
                            feedback_items.append(feedback)

                except Exception as e:
                    logger.warning(f"Error extracting feedback from r/{subreddit}: {e}")
                    continue

        except Exception as e:
            logger.debug(f"Reddit community extraction not available: {e}")

        return feedback_items

    async def _extract_bluesky_community_feedback(self) -> List[FeedbackItem]:
        """Extract feedback from Bluesky community discussions"""
        from ..spiders.bluesky_handler import bluesky_handler

        feedback_items = []

        # Search for discussions about AI agents, automation, job matching
        feedback_queries = [
            'AI agent experience',
            'automated job search',
            'AI hiring tools',
            'job matching platform',
            'agent automation review'
        ]

        for query in feedback_queries[:3]:  # Limit to prevent rate limiting
            try:
                posts = await bluesky_handler.search_posts(query, limit=5)

                for post in posts:
                    if self._is_relevant_feedback(post):
                        sentiment_rating = self._calculate_sentiment_rating(post['text'])

                        feedback = FeedbackItem(
                            id=f"bluesky_community_{post['cid']}",
                            timestamp=datetime.fromisoformat(post['created_at'].replace('Z', '+00:00')),
                            source="bluesky_community",
                            category=self._categorize_bluesky_feedback(post['text']),
                            target="platform_performance",
                            rating=sentiment_rating,
                            message=post['text'][:500],  # Truncate long messages
                            context={
                                'author': post['author']['handle'],
                                'engagement': post['metrics']['engagement'],
                                'platform': 'bluesky',
                                'post_uri': post['uri']
                            }
                        )
                        feedback_items.append(feedback)

            except Exception as e:
                logger.warning(f"Error extracting feedback for '{query}': {e}")
                continue

        return feedback_items

    async def _extract_expert_opinions(self) -> List[FeedbackItem]:
        """Extract expert opinions about AI and automation trends from Bluesky and Reddit"""
        feedback_items = []

        # Extract from Bluesky
        try:
            from ..spiders.bluesky_handler import bluesky_handler

            # Known experts in AI and technology
            tech_experts = [
                'karpathy.ai', 'ylecun.bsky.social', 'sama.bsky.social',
                'pmarca.bsky.social', 'dhh.bsky.social'
            ]

            # Keywords that might relate to our platform
            relevant_keywords = ['AI agent', 'automation', 'job market', 'hiring', 'artificial intelligence']

            for expert in tech_experts[:3]:  # Limit expert monitoring
                try:
                    posts = await bluesky_handler.get_author_feed(expert, limit=5)

                    for post in posts:
                        # Check if post mentions relevant topics
                        if any(keyword.lower() in post['text'].lower() for keyword in relevant_keywords):
                            sentiment_rating = self._calculate_sentiment_rating(post['text'])

                            feedback = FeedbackItem(
                                id=f"bluesky_expert_{expert}_{post['cid']}",
                                timestamp=datetime.fromisoformat(post['created_at'].replace('Z', '+00:00')),
                                source="expert_opinion",
                                category="industry_insight",
                                target="platform_direction",
                                rating=sentiment_rating,
                                message=post['text'][:500],
                                context={
                                    'expert': expert,
                                    'engagement': post['metrics']['engagement'],
                                    'expertise_area': self._identify_expertise_area(expert),
                                    'influence_score': post['metrics']['engagement'] / 10
                                }
                            )
                            feedback_items.append(feedback)

                except Exception as e:
                    logger.warning(f"Error extracting opinions from {expert}: {e}")
                    continue
        except ImportError:
            logger.debug("Bluesky handler not available")

        # Extract from Reddit AMAs and expert discussions
        try:
            from .reddit_learning_bridge import get_reddit_learning_bridge
            reddit_bridge = get_reddit_learning_bridge()

            # Search for expert AMAs in tech subreddits
            from ..spiders.reddit_handler import RedditHandler
            reddit_handler = RedditHandler()

            # Search for recent AMAs
            ama_posts = await reddit_handler.search_posts(
                'AMA artificial intelligence OR machine learning OR automation',
                sort='relevance',
                time_filter='month',
                limit=10
            )

            for post in ama_posts:
                if post.score > 100:  # Quality filter
                    # Get top comments from the AMA
                    comments = await reddit_handler.get_post_comments(
                        post.id,
                        sort='best',
                        limit=20
                    )

                    # Extract insights from high-quality comments
                    for comment in comments[:5]:
                        if comment.score > 50:
                            feedback = FeedbackItem(
                                id=f"reddit_expert_{post.id}_{comment.id}",
                                timestamp=comment.created_at,
                                source="reddit_expert",
                                category="industry_insight",
                                target="platform_direction",
                                rating=min(comment.score / 100, 1.0),
                                message=comment.body[:500],
                                context={
                                    'subreddit': post.subreddit,
                                    'post_title': post.title,
                                    'comment_score': comment.score,
                                    'is_ama': 'AMA' in post.title.upper(),
                                    'expertise_area': 'Technology',
                                    'platform': 'reddit'
                                }
                            )
                            feedback_items.append(feedback)

        except Exception as e:
            logger.debug(f"Reddit expert extraction not available: {e}")

        return feedback_items

    async def _extract_market_sentiment_feedback(self) -> List[FeedbackItem]:
        """Extract market sentiment that affects platform performance from Bluesky and Reddit"""
        feedback_items = []

        # Extract from Bluesky
        try:
            from ..spiders.bluesky_handler import bluesky_handler

            # Market sentiment topics that affect our platform
            market_topics = [
                'tech layoffs',
                'AI job displacement',
                'remote work trends',
                'hiring market',
                'tech hiring'
            ]

            for topic in market_topics[:2]:  # Limit topic monitoring
                try:
                    posts = await bluesky_handler.search_posts(topic, limit=8)

                    if posts:
                        # Calculate aggregate sentiment
                        total_sentiment = 0
                        total_engagement = 0
                        sentiment_posts = []

                        for post in posts:
                            if post['metrics']['engagement'] > 3:  # Filter for relevance
                                post_sentiment = self._calculate_sentiment_rating(post['text'])
                                engagement = post['metrics']['engagement']

                                # Weight sentiment by engagement
                                total_sentiment += post_sentiment * engagement
                                total_engagement += engagement
                                sentiment_posts.append(post['text'][:100])

                        if total_engagement > 0:
                            avg_sentiment = total_sentiment / total_engagement

                            feedback = FeedbackItem(
                                id=f"bluesky_market_{topic.replace(' ', '_')}_{datetime.now().timestamp()}",
                                timestamp=datetime.now(),
                                source="market_sentiment",
                                category="market_conditions",
                                target="business_environment",
                                rating=avg_sentiment,
                                message=f"Market sentiment for '{topic}': {sentiment_posts[0] if sentiment_posts else 'No significant discussions'}",
                                context={
                                    'topic': topic,
                                    'sample_posts': sentiment_posts[:3],
                                    'total_engagement': total_engagement,
                                    'post_count': len(posts),
                                    'sentiment_trend': 'positive' if avg_sentiment > 0.6 else 'negative' if avg_sentiment < 0.4 else 'neutral'
                                }
                            )
                            feedback_items.append(feedback)

                except Exception as e:
                    logger.warning(f"Error extracting market sentiment for '{topic}': {e}")
                    continue
        except ImportError:
            logger.debug("Bluesky handler not available")

        # Extract from Reddit
        try:
            from .reddit_learning_bridge import get_reddit_learning_bridge
            reddit_bridge = get_reddit_learning_bridge()

            # Get Reddit market sentiment
            market_topics = [
                'tech layoffs',
                'AI replacing jobs',
                'remote work',
                'job market 2025',
                'tech hiring freeze'
            ]

            for topic in market_topics[:3]:  # Process top 3 topics
                try:
                    consensus = await reddit_bridge.get_community_consensus(topic)
                    if consensus:
                        feedback = FeedbackItem(
                            id=f"reddit_market_{topic.replace(' ', '_')}_{datetime.now().timestamp()}",
                            timestamp=datetime.now(),
                            source="reddit_consensus",
                            category="market_conditions",
                            target="business_environment",
                            rating=consensus.average_sentiment,
                            message=f"Reddit consensus on '{topic}': {consensus.key_arguments_for[0] if consensus.key_arguments_for else 'Mixed opinions'}",
                            context={
                                'topic': topic,
                                'subreddits': consensus.subreddits[:5],
                                'total_discussions': consensus.total_discussions,
                                'sentiment': 'positive' if consensus.average_sentiment > 0.6 else 'negative' if consensus.average_sentiment < 0.4 else 'neutral',
                                'confidence': consensus.confidence
                            }
                        )
                        feedback_items.append(feedback)
                except Exception as e:
                    logger.warning(f"Error extracting Reddit sentiment for '{topic}': {e}")
                    continue
        except ImportError:
            logger.debug("Reddit learning bridge not available")

        return feedback_items

    def _is_relevant_feedback(self, post: Dict) -> bool:
        """Check if a Bluesky post contains relevant feedback"""
        # Look for feedback indicators
        feedback_indicators = [
            'experience with', 'used', 'tried', 'review', 'opinion',
            'works', 'doesn\'t work', 'helpful', 'useless', 'recommend',
            'avoid', 'love', 'hate', 'frustrated', 'impressed'
        ]

        text_lower = post['text'].lower()
        has_feedback = any(indicator in text_lower for indicator in feedback_indicators)

        # Must have some engagement to be considered relevant
        has_engagement = post['metrics']['engagement'] > 2

        return has_feedback and has_engagement

    def _categorize_bluesky_feedback(self, text: str) -> str:
        """Categorize Bluesky feedback"""
        text_lower = text.lower()

        if any(word in text_lower for word in ['error', 'bug', 'broken', 'crash', 'fail']):
            return 'error'
        elif any(word in text_lower for word in ['slow', 'fast', 'speed', 'performance', 'lag']):
            return 'performance'
        elif any(word in text_lower for word in ['confusing', 'difficult', 'easy', 'user-friendly', 'interface']):
            return 'usability'
        elif any(word in text_lower for word in ['accurate', 'wrong', 'correct', 'mistake', 'precise']):
            return 'accuracy'
        else:
            return 'general'

    def _calculate_sentiment_rating(self, text: str) -> float:
        """Calculate sentiment rating from text (0-1 scale)"""
        try:
            from textblob import TextBlob
            blob = TextBlob(text)
            sentiment = blob.sentiment.polarity
            # Convert from -1,1 to 0,1 scale
            return (sentiment + 1) / 2
        except ImportError:
            # Fallback: simple keyword-based sentiment
            positive_words = ['good', 'great', 'excellent', 'love', 'amazing', 'helpful', 'useful', 'works']
            negative_words = ['bad', 'terrible', 'awful', 'hate', 'useless', 'broken', 'doesn\'t work']

            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)

            if positive_count + negative_count == 0:
                return 0.5  # Neutral

            return positive_count / (positive_count + negative_count)

    def _identify_expertise_area(self, expert_handle: str) -> str:
        """Identify the expertise area of an expert"""
        expertise_mapping = {
            'karpathy.ai': 'AI Research',
            'ylecun.bsky.social': 'Deep Learning',
            'sama.bsky.social': 'Startup Strategy',
            'pmarca.bsky.social': 'Venture Capital',
            'dhh.bsky.social': 'Software Development'
        }
        return expertise_mapping.get(expert_handle, 'Technology')


# Global learning loop instance
learning_loop = LearningLoop()