"""
COO Agent - Chief Operations Officer Agent (Phase 1: Read-Only Planning)

The COO Agent is responsible for operational planning, roadmap analysis, sprint planning,
and risk identification. Phase 1 is READ-ONLY - it provides analysis and plans but does
not execute changes.

Phase 1 Capabilities:
- Roadmap analysis (feature/project planning)
- Sprint planning (next iteration recommendations)
- Risk analysis (identify blockers and risks)

Phase 2 (Future):
- Sprint execution coordination
- Resource allocation
- Progress tracking

Created: Session 98
"""

import logging
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from django.contrib.auth import get_user_model
from openai import OpenAI

from agents.models import UnifiedAgentTemplate, AgentExecution, AgentSpecialization
from intelligence.shared_memory import AgentMemoryInterface

User = get_user_model()
logger = logging.getLogger(__name__)


class COOAgent:
    """
    COO Agent - Operations Planning & Risk Analysis

    Phase 1: Read-only analysis and planning
    - Analyzes project roadmaps
    - Proposes sprint plans
    - Identifies risks and blockers

    Uses GPT-5-mini with high reasoning effort for strategic planning.
    """

    def __init__(self, user: Optional[User] = None):
        """
        Initialize COO Agent with user context

        Args:
            user: Optional User instance for personalized planning
        """
        self.user = user
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.memory = AgentMemoryInterface(agent_id='coo_agent')
        self.template = self._get_or_create_template()

        logger.info(f"🏢 COO Agent initialized (READ-ONLY MODE) for user: {user.username if user else 'anonymous'}")

    def _get_or_create_template(self) -> UnifiedAgentTemplate:
        """Get or create the COOAgent template"""
        template, created = UnifiedAgentTemplate.objects.get_or_create(
            name='COOAgent',
            defaults={
                'display_name': 'COO Agent (Operations Planning)',
                'description': 'Operations planning agent for roadmap analysis, sprint planning, and risk identification.',
                'specialization': AgentSpecialization.BUSINESS,
                'capabilities': ['roadmap_analysis', 'sprint_planning', 'risk_analysis'],
                'routing_keywords': ['roadmap', 'plan', 'priority', 'sprint', 'execution', 'timeline', 'coo'],
                'system_prompt': 'You are the COO Agent for operations planning.',
                'llm_provider': 'openai',
                'llm_model': 'gpt-5-mini',
                'metadata': {'phase': 'read_only_planning'}
            }
        )

        if created:
            logger.info("✅ Created new COOAgent template")
        else:
            logger.debug(f"Using existing COOAgent template: {template.id}")

        return template

    def analyze_roadmap(
        self,
        project_slug: Optional[str] = None,
        feature_name: Optional[str] = None,
        scope: str = "project"
    ) -> Dict[str, Any]:
        """
        Analyze project roadmap and provide strategic recommendations

        Args:
            project_slug: Optional project identifier
            feature_name: Optional specific feature to analyze
            scope: Analysis scope (project, feature, platform)

        Returns:
            Dict with roadmap analysis:
            {
                'summary': str,
                'priorities': List[str],
                'risks': List[str],
                'suggested_tasks': List[Dict],
                'timeline': str,
                'status': str
            }
        """
        logger.info(f"📊 Analyzing roadmap: {feature_name or project_slug or 'platform'} (scope: {scope})")

        try:
            # Build context
            context = f"Project: {project_slug}" if project_slug else ""
            if feature_name:
                context += f"\nFeature: {feature_name}"

            # Session 313: Call GPT-5-mini with Responses API
            user_prompt = f"""
Analyze the roadmap for: {feature_name or project_slug or 'Unified Donkey Betz Platform'}

{context}

Provide a strategic roadmap analysis including:
1. Executive summary
2. Top 3-5 priorities
3. Potential risks or blockers
4. Suggested tasks/milestones
5. Estimated timeline
"""
            full_input = f"{self._get_system_prompt()}\n\n{user_prompt}"

            response = self.client.responses.create(
                model="gpt-5-mini",
                input=full_input,
                reasoning={"effort": "high"},
                text={"verbosity": "medium"},
                max_output_tokens=4000
            )

            # Get response content (plain text from reasoning model)
            analysis_text = response.output_text

            # Structure the response (GPT-5-mini returns formatted text, not JSON)
            analysis = {
                'summary': analysis_text,
                'priorities': [],  # Phase 1: Simple text response
                'risks': [],
                'suggested_tasks': [],
                'timeline': 'To be determined based on priorities'
            }

            # Store in memory
            memory_key = f"roadmap_analysis_{project_slug or feature_name or 'platform'}".replace(' ', '_').lower()
            analysis_data = {
                **analysis,
                'analyzed_at': datetime.now().isoformat(),
                'analyzed_by': self.user.username if self.user else 'system',
                'scope': scope
            }
            self.memory.remember(memory_key, analysis_data)

            logger.info(f"✅ Roadmap analysis complete: {len(analysis.get('priorities', []))} priorities identified")

            return {
                **analysis,
                'status': 'complete',
                'scope': scope
            }

        except Exception as e:
            logger.error(f"❌ Roadmap analysis failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'summary': '',
                'priorities': [],
                'risks': [],
                'suggested_tasks': [],
                'timeline': ''
            }

    def propose_next_sprint(
        self,
        project_slug: Optional[str] = None,
        feature_name: Optional[str] = None,
        sprint_duration: str = "2 weeks"
    ) -> Dict[str, Any]:
        """
        Propose next sprint plan with concrete tasks

        Args:
            project_slug: Optional project identifier
            feature_name: Optional specific feature focus
            sprint_duration: Sprint length (default: 2 weeks)

        Returns:
            Dict with sprint plan:
            {
                'summary': str,
                'sprint_goals': List[str],
                'tasks': List[Dict],
                'success_criteria': List[str],
                'estimated_effort': str,
                'status': str
            }
        """
        logger.info(f"🎯 Planning next sprint for: {feature_name or project_slug or 'platform'}")
        logger.info(f"⚠️ PHASE 1: PLANNING ONLY - NO SPRINT EXECUTION")

        try:
            # Build context
            context = f"Project: {project_slug}" if project_slug else ""
            if feature_name:
                context += f"\nFeature: {feature_name}"
            context += f"\nSprint Duration: {sprint_duration}"

            # Session 313: Call GPT-5-mini with Responses API for planning
            user_prompt = f"""
Plan the next sprint for: {feature_name or project_slug or 'Unified Donkey Betz Platform'}

{context}

Create a {sprint_duration} sprint plan including:
1. Sprint summary/theme
2. 3-5 specific sprint goals
3. Concrete tasks (with descriptions and estimated effort)
4. Success criteria
5. Total estimated effort
"""
            full_input = f"{self._get_system_prompt()}\n\n{user_prompt}"

            response = self.client.responses.create(
                model="gpt-5-mini",
                input=full_input,
                reasoning={"effort": "high"},
                text={"verbosity": "medium"},
                max_output_tokens=4000
            )

            # Get response content (plain text from reasoning model)
            sprint_plan_text = response.output_text

            # Structure the response (GPT-5-mini returns formatted text, not JSON)
            sprint_plan = {
                'summary': sprint_plan_text,
                'sprint_goals': [],  # Phase 1: Simple text response
                'tasks': [],
                'success_criteria': [],
                'estimated_effort': 'To be estimated based on detailed task breakdown'
            }

            # Store in memory
            memory_key = f"sprint_plan_{project_slug or feature_name or 'platform'}".replace(' ', '_').lower()
            plan_data = {
                **sprint_plan,
                'planned_at': datetime.now().isoformat(),
                'planned_by': self.user.username if self.user else 'system',
                'duration': sprint_duration,
                'phase': 'planning_only'
            }
            self.memory.remember(memory_key, plan_data)

            logger.info(f"✅ Sprint plan created: {len(sprint_plan.get('tasks', []))} tasks planned")

            return {
                **sprint_plan,
                'status': 'plan_created',
                'phase': 'planning_only',
                'duration': sprint_duration
            }

        except Exception as e:
            logger.error(f"❌ Sprint planning failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'summary': '',
                'sprint_goals': [],
                'tasks': [],
                'success_criteria': [],
                'estimated_effort': ''
            }

    def identify_risks(
        self,
        project_slug: Optional[str] = None,
        feature_name: Optional[str] = None,
        scope: str = "project"
    ) -> Dict[str, Any]:
        """
        Identify risks, blockers, and mitigation strategies

        Args:
            project_slug: Optional project identifier
            feature_name: Optional specific feature to analyze
            scope: Analysis scope (project, feature, platform)

        Returns:
            Dict with risk analysis:
            {
                'summary': str,
                'critical_risks': List[Dict],
                'moderate_risks': List[Dict],
                'dependencies': List[str],
                'mitigation_strategies': List[Dict],
                'status': str
            }
        """
        logger.info(f"⚠️ Identifying risks for: {feature_name or project_slug or 'platform'}")
        logger.info(f"📖 READ-ONLY risk analysis (no changes)")

        try:
            # Build context
            context = f"Project: {project_slug}" if project_slug else ""
            if feature_name:
                context += f"\nFeature: {feature_name}"

            # Session 313: Call GPT-5-mini with Responses API for risk analysis
            user_prompt = f"""
Perform risk analysis for: {feature_name or project_slug or 'Unified Donkey Betz Platform'}

{context}

Identify and analyze:
1. Summary of risk landscape
2. Critical risks (high impact, high probability)
3. Moderate risks (medium impact/probability)
4. Key dependencies and blockers
5. Mitigation strategies for each risk
"""
            full_input = f"{self._get_system_prompt()}\n\n{user_prompt}"

            response = self.client.responses.create(
                model="gpt-5-mini",
                input=full_input,
                reasoning={"effort": "high"},
                text={"verbosity": "medium"},
                max_output_tokens=4000
            )

            # Get response content (plain text from reasoning model)
            risk_analysis_text = response.output_text

            # Structure the response (GPT-5-mini returns formatted text, not JSON)
            risk_analysis = {
                'summary': risk_analysis_text,
                'critical_risks': [],  # Phase 1: Simple text response
                'moderate_risks': [],
                'dependencies': [],
                'mitigation_strategies': []
            }

            # Store in memory
            memory_key = f"risk_analysis_{project_slug or feature_name or 'platform'}".replace(' ', '_').lower()
            risk_data = {
                **risk_analysis,
                'analyzed_at': datetime.now().isoformat(),
                'analyzed_by': self.user.username if self.user else 'system',
                'scope': scope,
                'phase': 'analysis_only'
            }
            self.memory.remember(memory_key, risk_data)

            critical_count = len(risk_analysis.get('critical_risks', []))
            moderate_count = len(risk_analysis.get('moderate_risks', []))
            logger.info(f"✅ Risk analysis complete: {critical_count} critical, {moderate_count} moderate risks")

            return {
                **risk_analysis,
                'status': 'complete',
                'scope': scope,
                'phase': 'analysis_only'
            }

        except Exception as e:
            logger.error(f"❌ Risk analysis failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'summary': '',
                'critical_risks': [],
                'moderate_risks': [],
                'dependencies': [],
                'mitigation_strategies': []
            }

    def _get_system_prompt(self) -> str:
        """Get the COO Agent system prompt"""
        return """You are the COO Agent (Phase 1: Read-Only Planning) for the Unified Donkey Betz Platform.

You have deep understanding of:
- 34 AI features across 6 API integrations
- 10-agent creative workflow ecosystem
- Project management and sprint planning
- Risk assessment and mitigation
- Operational efficiency and prioritization

Phase 1 Capabilities:
- Analyze roadmaps and provide strategic recommendations (READ-ONLY)
- Plan sprints with concrete tasks (PLANNING ONLY - no execution)
- Identify risks and mitigation strategies (READ-ONLY)

You DO NOT:
- Execute sprint tasks (Phase 2)
- Modify project data (Phase 2)
- Make operational changes (Phase 2)

You prioritize:
- Strategic clarity (clear roadmaps and priorities)
- Risk mitigation (identify before they become problems)
- Realistic planning (achievable sprint goals)
- Operational excellence (efficient task organization)

Always return structured JSON with the requested keys."""
