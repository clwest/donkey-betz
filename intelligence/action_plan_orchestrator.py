"""
Action Plan Orchestrator - Complete Flow Management

Manages the entire lifecycle from Action Plan creation through Advisor review
to Team formation and execution.

This is the main orchestration point that:
1. Receives completed Action Plans from Income Builder
2. Hands them off to appropriate Advisors
3. Forms execution teams based on Advisor recommendations
4. Initiates and tracks execution
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import all required components
from intelligence.action_plan_formatter import action_plan_formatter
from intelligence.action_plan_advisor_handoff import action_plan_advisor_handoff
from intelligence.income_builder import AIIncomeBuilder
from core.agents.registry import agent_registry
from advisors.registry import advisor_registry

logger = logging.getLogger(__name__)


class ActionPlanOrchestrator:
    """
    Main orchestrator for the complete Action Plan lifecycle
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.formatter = action_plan_formatter
        self.handoff = action_plan_advisor_handoff
        self.income_builder = AIIncomeBuilder()

        # Track active plans and their status
        self.active_plans: Dict[str, Dict[str, Any]] = {}
        self.execution_status: Dict[str, Dict[str, Any]] = {}

    async def process_action_plan_completion(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a completed action plan through the entire flow:
        1. Format the plan
        2. Hand off to advisor
        3. Get advisor review
        4. Form execution team
        5. Begin execution

        Args:
            plan_data: The completed action plan data from Income Builder

        Returns:
            Complete processing result with advisor review and team formation
        """
        plan_id = plan_data.get('id', f'plan_{datetime.now().strftime("%Y%m%d%H%M%S")}')

        result = {
            "plan_id": plan_id,
            "status": "processing",
            "stages": {},
            "timestamp": datetime.now().isoformat()
        }

        try:
            # Stage 1: Format the action plan
            self.logger.info(f"Stage 1: Formatting action plan {plan_id}")
            formatted_plan = self.formatter.format_complete_plan(plan_data)
            result["stages"]["formatting"] = {
                "status": "completed",
                "output_size": len(formatted_plan),
                "timestamp": datetime.now().isoformat()
            }

            # Stage 2: Hand off to advisor
            self.logger.info(f"Stage 2: Handing off plan {plan_id} to advisor")
            advisor_id, advisor_review = await self.handoff.handoff_to_advisor(plan_data)

            result["stages"]["advisor_handoff"] = {
                "status": "completed",
                "advisor_id": advisor_id,
                "advisor_name": advisor_review.advisor_name,
                "success_probability": advisor_review.success_probability,
                "timestamp": datetime.now().isoformat()
            }

            # Stage 3: Form execution team based on advisor review
            self.logger.info(f"Stage 3: Forming execution team for plan {plan_id}")
            team = await self.handoff.form_execution_team(plan_id, advisor_review)

            result["stages"]["team_formation"] = {
                "status": "completed",
                "team_id": team.team_id,
                "lead_agent": team.lead_agent,
                "team_size": len(team.core_agents) + len(team.specialist_agents),
                "timestamp": datetime.now().isoformat()
            }

            # Stage 4: Begin execution
            self.logger.info(f"Stage 4: Beginning execution of plan {plan_id}")
            execution_status = await self.handoff.execute_with_team(team, plan_data)

            result["stages"]["execution_initiation"] = {
                "status": "completed",
                "execution_status": execution_status["status"],
                "agents_activated": execution_status["agents_activated"],
                "initial_tasks": len(execution_status["initial_tasks"]),
                "timestamp": datetime.now().isoformat()
            }

            # Store complete result
            self.active_plans[plan_id] = plan_data
            self.execution_status[plan_id] = execution_status

            # Update overall status
            result["status"] = "ready_for_execution"
            result["advisor_review"] = {
                "advisor": advisor_review.advisor_name,
                "strengths": advisor_review.strengths[:3],  # Top 3
                "immediate_actions": advisor_review.immediate_actions[:5],  # Top 5
                "success_metrics": advisor_review.success_metrics[:3],  # Top 3
                "budget_estimate": advisor_review.budget_estimate,
                "timeline_adjustment": advisor_review.timeline_adjustment
            }
            result["team"] = {
                "id": team.team_id,
                "lead": team.lead_agent,
                "core_agents": team.core_agents,
                "specialists": team.specialist_agents,
                "coordination_model": team.coordination_model,
                "phases": len(team.execution_phases)
            }

            self.logger.info(f"Successfully processed action plan {plan_id} through complete flow")

        except Exception as e:
            self.logger.error(f"Error processing action plan {plan_id}: {str(e)}")
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def begin_execution(self, plan_id: str, team: Dict[str, Any], advisor_id: str = None) -> Dict[str, Any]:
        """
        Begin execution of an action plan with the assigned team

        Args:
            plan_id: The ID of the plan to execute
            team: The team configuration
            advisor_id: The advisor who reviewed the plan

        Returns:
            Execution status and progress information
        """
        try:
            self.logger.info(f"🚀 Beginning execution for plan {plan_id}")

            # Store execution status
            self.execution_status[plan_id] = {
                "status": "running",
                "started_at": datetime.now().isoformat(),
                "team": team,
                "advisor_id": advisor_id,
                "progress": 0.1,
                "agents_active": []
            }

            # Activate team agents
            lead_agent = team.get('lead_agent', 'orchestrator')
            core_agents = team.get('core_agents', [])
            specialist_agents = team.get('specialist_agents', [])

            all_agents = [lead_agent] + core_agents + specialist_agents
            self.execution_status[plan_id]["agents_active"] = all_agents[:5]  # Start with first 5

            # Connect to spider network for data gathering
            from ai_core.spiders.spider_army_orchestrator import SpiderArmyOrchestrator
            spider_orchestrator = SpiderArmyOrchestrator()

            # Activate relevant spiders based on plan requirements
            spider_types = self._determine_spider_types(plan_id)
            spider_orchestrator.activate_spiders(spider_types)

            self.logger.info(f"✅ Activated {len(all_agents)} agents and {len(spider_types)} spider types")

            # Create execution tasks
            execution_tasks = self._create_execution_tasks(plan_id, team)
            self.execution_status[plan_id]["total_tasks"] = len(execution_tasks)
            self.execution_status[plan_id]["completed_tasks"] = 0

            # Update progress
            self.execution_status[plan_id]["progress"] = 0.25

            return {
                "status": "success",
                "plan_id": plan_id,
                "execution_status": "running",
                "agents_active": self.execution_status[plan_id]["agents_active"],
                "progress": self.execution_status[plan_id]["progress"],
                "message": f"Execution started with {len(all_agents)} agents"
            }

        except Exception as e:
            self.logger.error(f"❌ Failed to begin execution for plan {plan_id}: {str(e)}")
            return {
                "status": "error",
                "plan_id": plan_id,
                "error": str(e)
            }

    def _determine_spider_types(self, plan_id: str) -> list:
        """Determine which spider types to activate based on plan"""
        # For now, activate a default set of spiders
        return ['job_spider', 'freelance_spider', 'content_spider', 'market_spider']

    def _create_execution_tasks(self, plan_id: str, team: Dict[str, Any]) -> list:
        """Create execution tasks for the team"""
        tasks = []

        # Create tasks based on team configuration
        if team.get('lead_agent'):
            tasks.append({"agent": team['lead_agent'], "task": "Coordinate team", "status": "pending"})

        for agent in team.get('core_agents', [])[:3]:
            tasks.append({"agent": agent, "task": f"Execute core function", "status": "pending"})

        return tasks

    async def get_plan_status(self, plan_id: str) -> Dict[str, Any]:
        """
        Get the current status of a plan

        Args:
            plan_id: The plan ID to check

        Returns:
            Current status information
        """
        if plan_id not in self.active_plans:
            return {
                "plan_id": plan_id,
                "status": "not_found",
                "message": f"Plan {plan_id} not found in active plans"
            }

        execution = self.execution_status.get(plan_id, {})

        return {
            "plan_id": plan_id,
            "status": "active",
            "execution_status": execution.get("status", "unknown"),
            "team_id": execution.get("team_id"),
            "current_phase": execution.get("current_phase", 0),
            "agents_activated": execution.get("agents_activated", []),
            "tasks_assigned": len(execution.get("initial_tasks", [])),
            "last_update": execution.get("start_time")
        }

    async def simulate_complete_flow(self, opportunity_title: str) -> Dict[str, Any]:
        """
        Simulate the complete flow from opportunity to execution

        This is useful for testing and demonstration

        Args:
            opportunity_title: The opportunity to build a plan for

        Returns:
            Complete flow results
        """
        self.logger.info(f"Simulating complete flow for: {opportunity_title}")

        # Create a sample action plan
        sample_plan = {
            "id": f"demo_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "opportunity_title": opportunity_title,
            "timeline": "4 weeks",
            "steps": [
                "Research and market analysis",
                "Create initial product/service",
                "Setup sales infrastructure",
                "Launch and acquire first customers",
                "Scale and optimize"
            ],
            "step_1_data": {
                "ai_content": f"Comprehensive research plan for {opportunity_title}...",
                "real_data": {
                    "search_results": {
                        "results": [
                            {"title": f"Guide to {opportunity_title}", "url": "https://example.com/guide"},
                            {"title": f"Market analysis for {opportunity_title}", "snippet": "Growing 25% annually"}
                        ]
                    }
                }
            }
        }

        # Process through complete flow
        result = await self.process_action_plan_completion(sample_plan)

        return result

    async def get_advisor_recommendation_for_opportunity(self, opportunity: str) -> Dict[str, Any]:
        """
        Get advisor recommendation for a specific opportunity type

        Args:
            opportunity: The opportunity description

        Returns:
            Recommended advisor and reasoning
        """
        # Create minimal plan data for domain identification
        plan_data = {"opportunity_title": opportunity}

        # Identify domain
        plan_domain = self.handoff._identify_plan_domain(plan_data)

        # Get best advisor
        advisor_id = await self.handoff._select_best_advisor(plan_domain, plan_data)

        # Get advisor details
        advisor = advisor_registry.advisors.get(advisor_id)

        if advisor:
            return {
                "opportunity": opportunity,
                "domain": plan_domain.value,
                "recommended_advisor": {
                    "id": advisor_id,
                    "name": advisor.name,
                    "title": advisor.title,
                    "expertise_level": advisor.expertise_level.value,
                    "specializations": advisor.specializations[:3],
                    "years_experience": advisor.years_experience,
                    "success_rate": advisor.success_rate
                },
                "reasoning": f"{advisor.name} is recommended due to expertise in {plan_domain.value} "
                           f"with {advisor.years_experience} years of experience and "
                           f"{advisor.success_rate:.0%} success rate"
            }

        return {
            "opportunity": opportunity,
            "domain": plan_domain.value,
            "recommended_advisor": None,
            "reasoning": "No suitable advisor found"
        }

    def get_active_teams(self) -> List[Dict[str, Any]]:
        """
        Get all currently active teams

        Returns:
            List of active team summaries
        """
        teams = []
        for plan_id, execution in self.execution_status.items():
            if "team_id" in execution:
                team = self.handoff.active_teams.get(execution["team_id"])
                if team:
                    teams.append({
                        "team_id": team.team_id,
                        "plan_id": team.plan_id,
                        "advisor_id": team.advisor_id,
                        "lead_agent": team.lead_agent,
                        "team_size": len(team.core_agents) + len(team.specialist_agents),
                        "current_phase": execution.get("current_phase", 1),
                        "status": execution.get("status", "active")
                    })

        return teams

    def get_advisor_workload(self) -> Dict[str, int]:
        """
        Get current workload for each advisor

        Returns:
            Dictionary of advisor_id -> number of active reviews
        """
        workload = {}
        for review in self.handoff.active_reviews.values():
            advisor_id = review.advisor_id
            workload[advisor_id] = workload.get(advisor_id, 0) + 1

        return workload


# Create singleton instance
action_plan_orchestrator = ActionPlanOrchestrator()