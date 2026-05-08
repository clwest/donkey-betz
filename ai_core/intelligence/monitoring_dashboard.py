"""
Real-Time Performance Monitoring Dashboard

Provides comprehensive monitoring of the intelligence platform including
agent performance, workflow execution, system health, and learning metrics.
"""

# BROKEN-BUT-UNREACHABLE — Session 1113 review (Session 1111 PR-C queue).
# Classification: import-broken module, no active runtime caller.
# Why: top-of-file `from orchestration import orchestrator` resolves at
# import time as a bare top-level package — no such top-level package
# exists in the repo (the actual module is `ai_core.intelligence.orchestration`),
# so any import of this module raises ModuleNotFoundError immediately.
# It also imports `from ml_pipeline.pipeline import MLPipeline`, but
# `ml_pipeline.pipeline` doesn't exist either — see `ml_pipeline/__init__.py`
# note. Both failures are pre-Django; smoke import never reaches the body.
# No active importer found in the repo (the only reference is the
# Session 1111 audit + this banner).
# Decision pending: archive once the deeper-review queue confirms no
# revival path. Sits in the same family as `orchestration.py` and
# `testing_suite.py` — treat consistently.
# See: docs/handoffs/SESSION_1111_DEEPER_REVIEW_MAP.md

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import logging

from orchestration import orchestrator
from core.agents.registry import agent_registry
from advisors.registry import advisor_registry
from ml_pipeline.pipeline import MLPipeline

logger = logging.getLogger(__name__)


@dataclass
class MetricSnapshot:
    """Point-in-time metric snapshot"""
    timestamp: datetime
    metric_type: str
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetric:
    """Performance metric with history"""
    name: str
    current_value: float
    average: float
    min_value: float
    max_value: float
    trend: str  # rising, falling, stable
    history: deque = field(default_factory=lambda: deque(maxlen=100))


class MonitoringDashboard:
    """Real-time monitoring and analytics dashboard"""

    def __init__(self):
        self.metrics = defaultdict(lambda: deque(maxlen=1000))
        self.alerts = deque(maxlen=100)
        self.ml_pipeline = MLPipeline()
        self.monitoring_active = False
        self.update_interval = 5  # seconds

        # Performance thresholds
        self.thresholds = {
            "response_time": {"warning": 2.0, "critical": 5.0},
            "error_rate": {"warning": 0.05, "critical": 0.1},
            "memory_usage": {"warning": 80, "critical": 90},
            "cpu_usage": {"warning": 70, "critical": 85},
            "workflow_success_rate": {"warning": 0.8, "critical": 0.6}
        }

    async def start_monitoring(self):
        """Start real-time monitoring"""
        self.monitoring_active = True
        logger.info("Performance monitoring started")

        # Start monitoring tasks
        await asyncio.gather(
            self._monitor_agents(),
            self._monitor_workflows(),
            self._monitor_system_health(),
            self._monitor_ml_performance(),
            self._process_alerts()
        )

    async def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        logger.info("Performance monitoring stopped")

    async def _monitor_agents(self):
        """Monitor agent performance"""
        while self.monitoring_active:
            try:
                for agent_id in agent_registry.list_agents():
                    agent = agent_registry.get_agent(agent_id)
                    if agent:
                        metrics = await self._collect_agent_metrics(agent_id, agent)
                        self._store_metrics(f"agent_{agent_id}", metrics)

                await asyncio.sleep(self.update_interval)

            except Exception as e:
                logger.error(f"Error monitoring agents: {e}")

    async def _monitor_workflows(self):
        """Monitor workflow execution"""
        while self.monitoring_active:
            try:
                workflow_metrics = await self._collect_workflow_metrics()
                self._store_metrics("workflows", workflow_metrics)

                await asyncio.sleep(self.update_interval)

            except Exception as e:
                logger.error(f"Error monitoring workflows: {e}")

    async def _monitor_system_health(self):
        """Monitor system health metrics"""
        import psutil

        while self.monitoring_active:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self._store_metrics("system_cpu", {"usage": cpu_percent})

                # Memory usage
                memory = psutil.virtual_memory()
                self._store_metrics("system_memory", {
                    "usage": memory.percent,
                    "available": memory.available / (1024 ** 3),  # GB
                    "used": memory.used / (1024 ** 3)  # GB
                })

                # Disk usage
                disk = psutil.disk_usage('/')
                self._store_metrics("system_disk", {
                    "usage": disk.percent,
                    "free": disk.free / (1024 ** 3)  # GB
                })

                # Network I/O
                net_io = psutil.net_io_counters()
                self._store_metrics("system_network", {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv
                })

                await asyncio.sleep(self.update_interval)

            except Exception as e:
                logger.error(f"Error monitoring system health: {e}")

    async def _monitor_ml_performance(self):
        """Monitor ML pipeline performance"""
        while self.monitoring_active:
            try:
                ml_metrics = await self.ml_pipeline.get_performance_metrics()
                self._store_metrics("ml_pipeline", ml_metrics)

                # Check for ML insights
                insights = await self.ml_pipeline.get_recent_insights()
                if insights:
                    self._store_metrics("ml_insights", insights)

                await asyncio.sleep(self.update_interval * 2)  # Less frequent

            except Exception as e:
                logger.error(f"Error monitoring ML pipeline: {e}")

    async def _collect_agent_metrics(
        self,
        agent_id: str,
        agent: Any
    ) -> Dict[str, Any]:
        """Collect metrics for a specific agent"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id
        }

        # Get agent-specific metrics if available
        if hasattr(agent, "get_metrics"):
            agent_metrics = await agent.get_metrics()
            metrics.update(agent_metrics)
        else:
            # Default metrics
            metrics.update({
                "status": "active",
                "requests_processed": 0,
                "average_response_time": 0,
                "error_rate": 0
            })

        return metrics

    async def _collect_workflow_metrics(self) -> Dict[str, Any]:
        """Collect workflow execution metrics"""
        active_workflows = len(orchestrator.active_contexts)
        completed_workflows = sum(
            1 for w in orchestrator.workflows.values()
            if w["status"].value == "completed"
        )
        failed_workflows = sum(
            1 for w in orchestrator.workflows.values()
            if w["status"].value == "failed"
        )

        total = completed_workflows + failed_workflows
        success_rate = completed_workflows / total if total > 0 else 1.0

        return {
            "timestamp": datetime.now().isoformat(),
            "active": active_workflows,
            "completed": completed_workflows,
            "failed": failed_workflows,
            "success_rate": success_rate,
            "total": len(orchestrator.workflows)
        }

    def _store_metrics(self, category: str, metrics: Dict[str, Any]):
        """Store metrics with timestamp"""
        snapshot = MetricSnapshot(
            timestamp=datetime.now(),
            metric_type=category,
            value=metrics.get("value", 0),
            metadata=metrics
        )
        self.metrics[category].append(snapshot)

        # Check thresholds and generate alerts if needed
        self._check_thresholds(category, metrics)

    def _check_thresholds(self, category: str, metrics: Dict[str, Any]):
        """Check metrics against thresholds and generate alerts"""
        for metric_name, value in metrics.items():
            if metric_name in self.thresholds:
                thresholds = self.thresholds[metric_name]

                if isinstance(value, (int, float)):
                    if value >= thresholds["critical"]:
                        self._create_alert(
                            level="critical",
                            category=category,
                            message=f"{metric_name} is critical: {value}"
                        )
                    elif value >= thresholds["warning"]:
                        self._create_alert(
                            level="warning",
                            category=category,
                            message=f"{metric_name} warning: {value}"
                        )

    def _create_alert(
        self,
        level: str,
        category: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Create an alert"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "category": category,
            "message": message,
            "metadata": metadata or {}
        }
        self.alerts.append(alert)
        logger.warning(f"Alert created: {alert}")

    async def _process_alerts(self):
        """Process and handle alerts"""
        while self.monitoring_active:
            try:
                # Process recent alerts
                recent_alerts = [
                    alert for alert in self.alerts
                    if datetime.fromisoformat(alert["timestamp"]) >
                    datetime.now() - timedelta(minutes=5)
                ]

                if recent_alerts:
                    # Group alerts by category
                    by_category = defaultdict(list)
                    for alert in recent_alerts:
                        by_category[alert["category"]].append(alert)

                    # Take action based on alert patterns
                    for category, alerts in by_category.items():
                        critical_count = sum(
                            1 for a in alerts if a["level"] == "critical"
                        )

                        if critical_count >= 3:
                            await self._handle_critical_situation(category, alerts)

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Error processing alerts: {e}")

    async def _handle_critical_situation(
        self,
        category: str,
        alerts: List[Dict[str, Any]]
    ):
        """Handle critical alert situations"""
        logger.critical(f"Critical situation detected in {category}")

        # Implement auto-remediation strategies
        if "workflow" in category:
            # Slow down workflow creation
            orchestrator.update_interval *= 2
            logger.info("Slowing down workflow creation due to high load")

        elif "system_memory" in category:
            # Trigger garbage collection
            import gc
            gc.collect()
            logger.info("Triggered garbage collection due to high memory usage")

        elif "agent" in category:
            # Restart problematic agents
            agent_id = category.replace("agent_", "")
            await agent_registry.restart_agent(agent_id)
            logger.info(f"Restarted agent {agent_id} due to errors")

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data"""
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": self._get_summary_metrics(),
            "agents": self._get_agent_metrics(),
            "workflows": self._get_workflow_metrics(),
            "system": self._get_system_metrics(),
            "ml_pipeline": self._get_ml_metrics(),
            "alerts": list(self.alerts)[-10:],  # Last 10 alerts
            "trends": self._calculate_trends()
        }

    def _get_summary_metrics(self) -> Dict[str, Any]:
        """Get summary metrics"""
        return {
            "total_agents": len(agent_registry.list_agents()),
            "total_advisors": len(advisor_registry.list_advisors()),
            "active_workflows": len(orchestrator.active_contexts),
            "total_alerts": len(self.alerts),
            "critical_alerts": sum(
                1 for a in self.alerts if a["level"] == "critical"
            )
        }

    def _get_agent_metrics(self) -> Dict[str, PerformanceMetric]:
        """Get agent performance metrics"""
        agent_metrics = {}

        for agent_id in agent_registry.list_agents():
            category = f"agent_{agent_id}"
            if category in self.metrics:
                snapshots = list(self.metrics[category])
                if snapshots:
                    values = [s.metadata.get("average_response_time", 0)
                              for s in snapshots[-20:]]
                    if values:
                        agent_metrics[agent_id] = PerformanceMetric(
                            name=agent_id,
                            current_value=values[-1],
                            average=statistics.mean(values),
                            min_value=min(values),
                            max_value=max(values),
                            trend=self._calculate_trend(values),
                            history=deque(values, maxlen=100)
                        )

        return agent_metrics

    def _get_workflow_metrics(self) -> Dict[str, Any]:
        """Get workflow metrics"""
        if "workflows" in self.metrics:
            snapshots = list(self.metrics["workflows"])[-20:]
            if snapshots:
                return {
                    "active": snapshots[-1].metadata.get("active", 0),
                    "completed": snapshots[-1].metadata.get("completed", 0),
                    "failed": snapshots[-1].metadata.get("failed", 0),
                    "success_rate": snapshots[-1].metadata.get("success_rate", 0),
                    "trend": self._calculate_trend(
                        [s.metadata.get("success_rate", 0) for s in snapshots]
                    )
                }

        return {"active": 0, "completed": 0, "failed": 0, "success_rate": 0}

    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system health metrics"""
        system_metrics = {}

        for category in ["system_cpu", "system_memory", "system_disk"]:
            if category in self.metrics:
                snapshots = list(self.metrics[category])[-20:]
                if snapshots:
                    metric_name = category.replace("system_", "")
                    values = [s.metadata.get("usage", 0) for s in snapshots]
                    system_metrics[metric_name] = {
                        "current": values[-1] if values else 0,
                        "average": statistics.mean(values) if values else 0,
                        "trend": self._calculate_trend(values)
                    }

        return system_metrics

    def _get_ml_metrics(self) -> Dict[str, Any]:
        """Get ML pipeline metrics"""
        if "ml_pipeline" in self.metrics:
            snapshots = list(self.metrics["ml_pipeline"])[-10:]
            if snapshots:
                latest = snapshots[-1].metadata
                return {
                    "patterns_identified": latest.get("patterns_identified", 0),
                    "predictions_made": latest.get("predictions_made", 0),
                    "accuracy": latest.get("accuracy", 0),
                    "learning_rate": latest.get("learning_rate", 0),
                    "insights_generated": latest.get("insights_generated", 0)
                }

        return {
            "patterns_identified": 0,
            "predictions_made": 0,
            "accuracy": 0,
            "learning_rate": 0,
            "insights_generated": 0
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from values"""
        if len(values) < 2:
            return "stable"

        # Simple linear regression
        n = len(values)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return "stable"

        slope = numerator / denominator

        if slope > 0.1:
            return "rising"
        elif slope < -0.1:
            return "falling"
        else:
            return "stable"

    def _calculate_trends(self) -> Dict[str, str]:
        """Calculate overall trends"""
        trends = {}

        # Agent performance trend
        agent_values = []
        for agent_id in agent_registry.list_agents():
            category = f"agent_{agent_id}"
            if category in self.metrics:
                snapshots = list(self.metrics[category])[-10:]
                values = [s.metadata.get("average_response_time", 0) for s in snapshots]
                if values:
                    agent_values.extend(values)

        if agent_values:
            trends["agent_performance"] = self._calculate_trend(agent_values)

        # Workflow success trend
        if "workflows" in self.metrics:
            snapshots = list(self.metrics["workflows"])[-20:]
            values = [s.metadata.get("success_rate", 0) for s in snapshots]
            if values:
                trends["workflow_success"] = self._calculate_trend(values)

        # System health trend
        if "system_cpu" in self.metrics:
            snapshots = list(self.metrics["system_cpu"])[-20:]
            values = [s.metadata.get("usage", 0) for s in snapshots]
            if values:
                trends["system_health"] = self._calculate_trend([-v for v in values])

        return trends

    async def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        dashboard_data = self.get_dashboard_data()

        report = {
            "generated_at": datetime.now().isoformat(),
            "monitoring_period": {
                "start": (datetime.now() - timedelta(hours=24)).isoformat(),
                "end": datetime.now().isoformat()
            },
            "executive_summary": self._generate_executive_summary(dashboard_data),
            "performance_metrics": dashboard_data,
            "recommendations": await self._generate_recommendations(dashboard_data),
            "ml_insights": await self.ml_pipeline.generate_insights_report()
        }

        return report

    def _generate_executive_summary(
        self,
        dashboard_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate executive summary"""
        summary = dashboard_data["summary"]
        trends = dashboard_data["trends"]

        health_score = 100
        issues = []

        # Calculate health score
        if summary["critical_alerts"] > 0:
            health_score -= summary["critical_alerts"] * 10
            issues.append(f"{summary['critical_alerts']} critical alerts")

        workflows = dashboard_data["workflows"]
        if workflows["success_rate"] < 0.8:
            health_score -= 20
            issues.append(f"Low workflow success rate: {workflows['success_rate']:.1%}")

        system = dashboard_data["system"]
        if "cpu" in system and system["cpu"]["current"] > 80:
            health_score -= 15
            issues.append(f"High CPU usage: {system['cpu']['current']:.1f}%")

        return {
            "health_score": max(0, health_score),
            "status": "healthy" if health_score > 70 else "degraded" if health_score > 40 else "critical",
            "issues": issues,
            "trends": trends,
            "highlights": [
                f"{summary['total_agents']} agents active",
                f"{summary['active_workflows']} workflows running",
                f"{workflows['completed']} workflows completed"
            ]
        }

    async def _generate_recommendations(
        self,
        dashboard_data: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on metrics"""
        recommendations = []

        # Check workflow success rate
        workflows = dashboard_data["workflows"]
        if workflows["success_rate"] < 0.8:
            recommendations.append(
                "Consider reviewing failing workflows and adjusting timeout settings"
            )

        # Check system resources
        system = dashboard_data["system"]
        if "memory" in system and system["memory"]["current"] > 80:
            recommendations.append(
                "Memory usage is high. Consider scaling resources or optimizing agents"
            )

        # Check alert patterns
        if dashboard_data["summary"]["critical_alerts"] > 5:
            recommendations.append(
                "Multiple critical alerts detected. Review system configuration"
            )

        # Get ML recommendations
        ml_recommendations = await self.ml_pipeline.get_optimization_recommendations()
        recommendations.extend(ml_recommendations)

        return recommendations


# Global dashboard instance
monitoring_dashboard = MonitoringDashboard()