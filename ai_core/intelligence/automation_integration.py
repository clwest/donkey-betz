"""
Revenue Opportunity + Automation Integration
Connects Income Builder plans to revenue tracking and automatic execution
"""

from typing import Dict, Any, List
from datetime import datetime
from decimal import Decimal
from django.db import models
from core.agents import OpportunityPipelineAgent

class RevenueAutomationIntegration:
    """
    Bridges Income Builder automation with Revenue Opportunities tracking
    """

    def __init__(self):
        self.opportunity_orchestrator = OpportunityPipelineAgent()
        self.active_automations = {}
        self.revenue_tracking = {}

    def link_plan_to_revenue(self, plan_id: str, opportunity_id: str, automation_id: str) -> Dict[str, Any]:
        """
        Link an Income Builder plan to revenue tracking
        """
        link = {
            "plan_id": plan_id,
            "opportunity_id": opportunity_id,
            "automation_id": automation_id,
            "created_at": datetime.now().isoformat(),
            "status": "linked",
            "revenue_potential": self._calculate_revenue_potential(opportunity_id),
            "tracking_metrics": {
                "tasks_completed": 0,
                "revenue_generated": 0,
                "time_invested": 0,
                "roi": 0
            }
        }

        self.revenue_tracking[automation_id] = link
        return link

    def track_task_revenue(self, automation_id: str, task_id: str, task_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track revenue impact of completed tasks
        """
        if automation_id not in self.revenue_tracking:
            return {"error": "Automation not found"}

        tracking = self.revenue_tracking[automation_id]

        # Extract revenue signals from task results
        revenue_impact = self._extract_revenue_impact(task_result)

        # Update tracking metrics
        tracking["tracking_metrics"]["tasks_completed"] += 1
        tracking["tracking_metrics"]["revenue_generated"] += revenue_impact.get("revenue", 0)
        tracking["tracking_metrics"]["time_invested"] += revenue_impact.get("time_hours", 0)

        # Calculate ROI
        if tracking["tracking_metrics"]["time_invested"] > 0:
            tracking["tracking_metrics"]["roi"] = (
                tracking["tracking_metrics"]["revenue_generated"] /
                (tracking["tracking_metrics"]["time_invested"] * 50)  # Assuming $50/hour value
            )

        # Log task completion
        if "task_completions" not in tracking:
            tracking["task_completions"] = []

        tracking["task_completions"].append({
            "task_id": task_id,
            "completed_at": datetime.now().isoformat(),
            "revenue_impact": revenue_impact
        })

        return tracking

    def _extract_revenue_impact(self, task_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract revenue signals from task execution results
        """
        impact = {
            "revenue": 0,
            "time_hours": 0.5,  # Default time investment
            "deliverables": [],
            "opportunities_created": 0
        }

        # Check for revenue indicators
        if "proposals_generated" in task_result.get("results", {}):
            proposals = task_result["results"]["proposals_generated"]
            impact["opportunities_created"] = proposals
            impact["revenue"] = proposals * 500  # Estimated value per proposal

        if "estimated_value" in task_result.get("results", {}):
            value_str = task_result["results"]["estimated_value"]
            try:
                impact["revenue"] = float(value_str.replace("$", "").replace(",", ""))
            except:
                pass

        if "content_pieces" in task_result.get("results", {}):
            pieces = task_result["results"]["content_pieces"]
            impact["deliverables"].append(f"{pieces} content pieces")
            impact["revenue"] += pieces * 100  # Estimated value per piece

        if "campaigns_launched" in task_result.get("results", {}):
            campaigns = task_result["results"]["campaigns_launched"]
            impact["opportunities_created"] += campaigns
            impact["revenue"] += campaigns * 1000  # Estimated campaign value

        return impact

    def _calculate_revenue_potential(self, opportunity_id: str) -> float:
        """
        Calculate revenue potential for an opportunity
        """
        # Default potentials by opportunity type
        opportunity_potentials = {
            "ai-content-writing": 3000,
            "no-code-automation": 5000,
            "digital-products": 4000,
            "freelancing": 2500,
            "trading": 10000
        }

        return opportunity_potentials.get(opportunity_id, 2000)

    def generate_revenue_report(self, automation_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive revenue report for an automation
        """
        if automation_id not in self.revenue_tracking:
            return {"error": "Automation not found"}

        tracking = self.revenue_tracking[automation_id]

        report = {
            "automation_id": automation_id,
            "opportunity_id": tracking["opportunity_id"],
            "status": tracking["status"],
            "metrics": tracking["tracking_metrics"],
            "revenue_potential": tracking["revenue_potential"],
            "achievement_rate": (
                tracking["tracking_metrics"]["revenue_generated"] /
                tracking["revenue_potential"] * 100
                if tracking["revenue_potential"] > 0 else 0
            ),
            "task_completions": len(tracking.get("task_completions", [])),
            "total_revenue": tracking["tracking_metrics"]["revenue_generated"],
            "roi": tracking["tracking_metrics"]["roi"],
            "recommendations": self._generate_recommendations(tracking)
        }

        return report

    def _generate_recommendations(self, tracking: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on performance
        """
        recommendations = []

        achievement = (
            tracking["tracking_metrics"]["revenue_generated"] /
            tracking["revenue_potential"] * 100
            if tracking["revenue_potential"] > 0 else 0
        )

        if achievement < 30:
            recommendations.append("Focus on high-value tasks first")
            recommendations.append("Consider adjusting your pricing strategy")

        if tracking["tracking_metrics"]["roi"] < 1:
            recommendations.append("Optimize time investment per task")
            recommendations.append("Automate repetitive activities")

        if tracking["tracking_metrics"]["tasks_completed"] < 5:
            recommendations.append("Increase task completion rate")
            recommendations.append("Break down complex tasks into smaller steps")

        if achievement > 70:
            recommendations.append("Scale successful strategies")
            recommendations.append("Explore similar opportunities")

        return recommendations

    def get_active_automations(self) -> List[Dict[str, Any]]:
        """
        Get all active automation-revenue links
        """
        active = []
        for automation_id, tracking in self.revenue_tracking.items():
            if tracking["status"] == "linked":
                active.append({
                    "automation_id": automation_id,
                    "opportunity_id": tracking["opportunity_id"],
                    "revenue_generated": tracking["tracking_metrics"]["revenue_generated"],
                    "tasks_completed": tracking["tracking_metrics"]["tasks_completed"],
                    "roi": tracking["tracking_metrics"]["roi"]
                })
        return active

    def project_revenue(self, automation_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Project future revenue based on current performance
        """
        if automation_id not in self.revenue_tracking:
            return {"error": "Automation not found"}

        tracking = self.revenue_tracking[automation_id]
        metrics = tracking["tracking_metrics"]

        # Calculate daily rate
        days_active = 1  # Simplified for demo
        daily_revenue = metrics["revenue_generated"] / days_active if days_active > 0 else 0

        projection = {
            "automation_id": automation_id,
            "current_daily_rate": daily_revenue,
            "projected_revenue": {
                "7_days": daily_revenue * 7,
                "30_days": daily_revenue * 30,
                "90_days": daily_revenue * 90
            },
            "confidence": self._calculate_confidence(tracking),
            "growth_potential": self._assess_growth_potential(tracking)
        }

        return projection

    def _calculate_confidence(self, tracking: Dict[str, Any]) -> str:
        """
        Calculate confidence level in projections
        """
        tasks = tracking["tracking_metrics"]["tasks_completed"]

        if tasks < 5:
            return "Low - Limited data"
        elif tasks < 20:
            return "Medium - Building track record"
        else:
            return "High - Proven performance"

    def _assess_growth_potential(self, tracking: Dict[str, Any]) -> str:
        """
        Assess growth potential
        """
        roi = tracking["tracking_metrics"]["roi"]

        if roi > 3:
            return "Excellent - High ROI indicates strong scaling potential"
        elif roi > 1.5:
            return "Good - Positive returns support growth"
        elif roi > 0.8:
            return "Moderate - Optimize before scaling"
        else:
            return "Limited - Focus on improving efficiency"


# Django Model for persistence
class AutomationRevenueLink(models.Model):
    """
    Database model for automation-revenue tracking
    """
    automation_id = models.CharField(max_length=100, unique=True)
    opportunity_id = models.CharField(max_length=100)
    plan_id = models.CharField(max_length=100)

    revenue_generated = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    revenue_potential = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tasks_completed = models.IntegerField(default=0)
    time_invested_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    roi = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'automation_revenue_links'
        ordering = ['-created_at']