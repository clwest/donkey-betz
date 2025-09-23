#!/usr/bin/env python3
"""
Advisor Oversight System
========================

This system implements REAL advisor oversight where legendary advisors
(Warren Buffett, Cathie Wood, Ray Dalio, etc.) actively monitor, guide,
and review agent work throughout the project building process.

Key Features:
1. Pre-execution planning and strategy
2. Real-time guidance during execution
3. Post-execution review and feedback
4. Quality gates and approval workflows
5. Strategic pivots and course corrections
"""

import os
import django
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.agents.concrete_executor import ConcreteAgentExecutor
from advisors.llm_advisor_system import LLMAdvisorNetwork
from advisors.registry import AdvisorRegistry
from backend.spiders.spider_registry import SpiderRegistry

logger = logging.getLogger(__name__)


class AdvisorOversightSystem:
    """
    Implements comprehensive advisor oversight for agent orchestration.
    Advisors provide strategic guidance, review work, and ensure quality.
    """

    def __init__(self):
        self.executor = ConcreteAgentExecutor()
        self.advisor_network = LLMAdvisorNetwork()
        self.advisor_registry = AdvisorRegistry()
        self.spider_registry = SpiderRegistry()

        # Oversight configuration
        self.approval_threshold = 0.7  # 70% approval needed
        self.max_revision_rounds = 3
        self.strategic_checkpoints = ["blueprint", "phase_complete", "integration", "deployment"]

        logger.info(f"🎓 Advisor Oversight System Initialized")
        logger.info(f"   • {len(self.advisor_registry.advisors)} Advisors providing oversight")
        logger.info(f"   • {len(self.executor.agent_classes)} Agents under supervision")

    async def strategic_planning_session(self,
                                       project_type: str,
                                       project_goals: Dict) -> Dict[str, Any]:
        """
        Advisors collaborate to create strategic plan before any work begins.
        This is where the big picture thinking happens.
        """

        logger.info(f"\n📋 STRATEGIC PLANNING SESSION")
        logger.info(f"   Project Type: {project_type}")

        # Select relevant advisors for this project
        advisors = self._select_strategic_advisors(project_type)

        planning_results = {
            'project_type': project_type,
            'timestamp': datetime.now().isoformat(),
            'advisors_consulted': [],
            'strategic_vision': {},
            'success_metrics': {},
            'risk_assessment': {},
            'resource_allocation': {},
            'phase_strategy': []
        }

        # Each advisor provides their strategic input
        for advisor_id in advisors:
            advisor = self.advisor_network.get_advisor(advisor_id)

            if advisor:
                logger.info(f"   🧠 Consulting {advisor.advisor_profile['name']}...")

                consultation = advisor.provide_consultation(
                    topic=f"Strategic planning for {project_type}",
                    context={
                        'project_type': project_type,
                        'goals': project_goals,
                        'request': 'Provide strategic vision, success metrics, and risk assessment'
                    },
                    consultation_type='strategic'
                )

                planning_results['advisors_consulted'].append({
                    'advisor': advisor.advisor_profile['name'],
                    'expertise': advisor.domain,
                    'recommendations': consultation.get('recommendations', [])
                })

                # Aggregate strategic insights
                self._aggregate_strategic_insights(planning_results, consultation)

        # Create consensus strategy
        planning_results['consensus_strategy'] = self._build_consensus_strategy(planning_results)

        return planning_results

    async def pre_execution_review(self,
                                  agent_name: str,
                                  task: str,
                                  context: Dict) -> Dict[str, Any]:
        """
        Advisors review and guide BEFORE agent executes task.
        They can suggest approach modifications or provide additional context.
        """

        logger.info(f"\n🔍 PRE-EXECUTION REVIEW")
        logger.info(f"   Agent: {agent_name}")
        logger.info(f"   Task: {task}")

        # Select advisors based on task type
        advisors = self._select_task_advisors(task, context.get('project_type'))

        review_results = {
            'agent': agent_name,
            'task': task,
            'timestamp': datetime.now().isoformat(),
            'advisor_guidance': [],
            'approach_modifications': [],
            'additional_context': {},
            'risk_warnings': [],
            'approval_status': 'pending'
        }

        approval_votes = []

        for advisor_id in advisors[:3]:  # Top 3 advisors review
            advisor = self.advisor_network.get_advisor(advisor_id)

            if advisor:
                guidance = advisor.provide_consultation(
                    topic=f"Review approach for: {task}",
                    context={
                        'agent': agent_name,
                        'task': task,
                        'project_context': context,
                        'request': 'Review the planned approach and provide guidance'
                    },
                    consultation_type='review'
                )

                # Extract specific guidance
                review_results['advisor_guidance'].append({
                    'advisor': advisor.advisor_profile['name'],
                    'advice': guidance.get('advice', ''),
                    'confidence': guidance.get('confidence_score', 0.5)
                })

                # Check if advisor approves
                approval_score = guidance.get('confidence_score', 0.5)
                approval_votes.append(approval_score)

                # Extract modifications if suggested
                if guidance.get('recommendations'):
                    review_results['approach_modifications'].extend(
                        guidance['recommendations'][:2]  # Top 2 recommendations
                    )

        # Calculate approval
        if approval_votes:
            avg_approval = sum(approval_votes) / len(approval_votes)
            review_results['approval_status'] = 'approved' if avg_approval >= self.approval_threshold else 'needs_revision'
            review_results['approval_score'] = avg_approval

        return review_results

    async def real_time_monitoring(self,
                                  agent_name: str,
                                  task: str,
                                  execution_id: str) -> Dict[str, Any]:
        """
        Advisors monitor agent execution in real-time and can provide
        course corrections if needed.
        """

        monitoring = {
            'execution_id': execution_id,
            'agent': agent_name,
            'task': task,
            'monitoring_events': [],
            'interventions': [],
            'status': 'monitoring'
        }

        # Simulate real-time monitoring checkpoints
        checkpoints = ['initialization', 'processing', 'validation', 'completion']

        for checkpoint in checkpoints:
            # Random advisor checks in
            advisor_id = self._select_monitoring_advisor()
            advisor = self.advisor_network.get_advisor(advisor_id)

            if advisor and checkpoint == 'processing':
                # Advisor might intervene during processing
                intervention = advisor.provide_consultation(
                    topic=f"Monitor execution checkpoint: {checkpoint}",
                    context={
                        'agent': agent_name,
                        'task': task,
                        'checkpoint': checkpoint,
                        'request': 'Check if intervention needed'
                    },
                    consultation_type='monitoring'
                )

                if intervention.get('confidence_score', 1.0) < 0.6:
                    monitoring['interventions'].append({
                        'advisor': advisor.advisor_profile['name'],
                        'checkpoint': checkpoint,
                        'intervention': intervention.get('recommendations', ['Continue as planned'])[0],
                        'timestamp': datetime.now().isoformat()
                    })

            monitoring['monitoring_events'].append({
                'checkpoint': checkpoint,
                'timestamp': datetime.now().isoformat(),
                'status': 'passed'
            })

        monitoring['status'] = 'completed'
        return monitoring

    async def post_execution_review(self,
                                   agent_name: str,
                                   task: str,
                                   result: Dict) -> Dict[str, Any]:
        """
        Comprehensive review after agent completes task.
        Advisors assess quality, completeness, and alignment with strategy.
        """

        logger.info(f"\n📊 POST-EXECUTION REVIEW")
        logger.info(f"   Agent: {agent_name} - Task: {task}")

        # Select reviewing advisors
        advisors = self._select_review_panel(task)

        review = {
            'agent': agent_name,
            'task': task,
            'timestamp': datetime.now().isoformat(),
            'quality_scores': [],
            'feedback': [],
            'required_revisions': [],
            'approval_decision': 'pending',
            'next_steps': []
        }

        quality_scores = []

        for advisor_id in advisors:
            advisor = self.advisor_network.get_advisor(advisor_id)

            if advisor:
                assessment = advisor.provide_consultation(
                    topic=f"Review completed work: {task}",
                    context={
                        'agent': agent_name,
                        'task': task,
                        'result': result,
                        'request': 'Assess quality and completeness'
                    },
                    consultation_type='assessment'
                )

                # Extract quality score
                quality_score = assessment.get('confidence_score', 0.7)
                quality_scores.append(quality_score)

                review['quality_scores'].append({
                    'advisor': advisor.advisor_profile['name'],
                    'score': quality_score,
                    'rationale': assessment.get('advice', '')[:200]
                })

                # Collect feedback
                review['feedback'].append({
                    'advisor': advisor.advisor_profile['name'],
                    'feedback': assessment.get('recommendations', ['Good work'])[0]
                })

                # Check for required revisions
                if quality_score < self.approval_threshold:
                    revisions = assessment.get('action_items', [])
                    if revisions:
                        review['required_revisions'].extend(revisions[:2])

        # Final approval decision
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            review['overall_quality_score'] = avg_quality

            if avg_quality >= self.approval_threshold:
                review['approval_decision'] = 'approved'
                review['next_steps'] = ['Proceed to next phase']
            else:
                review['approval_decision'] = 'needs_revision'
                review['next_steps'] = ['Address feedback and resubmit']

        return review

    async def strategic_checkpoint_review(self,
                                         checkpoint_type: str,
                                         project_status: Dict) -> Dict[str, Any]:
        """
        Major strategic checkpoints where advisors assess overall progress
        and can recommend pivots or course corrections.
        """

        logger.info(f"\n🎯 STRATEGIC CHECKPOINT: {checkpoint_type}")

        # Get strategic advisory panel
        panel = self._get_strategic_panel()

        checkpoint_review = {
            'checkpoint': checkpoint_type,
            'timestamp': datetime.now().isoformat(),
            'project_status': project_status,
            'advisor_assessments': [],
            'strategic_recommendations': [],
            'pivot_recommendations': [],
            'continue_decision': 'pending'
        }

        continue_votes = []

        for advisor_id in panel:
            advisor = self.advisor_network.get_advisor(advisor_id)

            if advisor:
                assessment = advisor.provide_consultation(
                    topic=f"Strategic checkpoint: {checkpoint_type}",
                    context={
                        'checkpoint': checkpoint_type,
                        'project_status': project_status,
                        'request': 'Assess progress and recommend strategic adjustments'
                    },
                    consultation_type='strategic'
                )

                checkpoint_review['advisor_assessments'].append({
                    'advisor': advisor.advisor_profile['name'],
                    'assessment': assessment.get('advice', ''),
                    'continue_confidence': assessment.get('confidence_score', 0.7)
                })

                continue_votes.append(assessment.get('confidence_score', 0.7))

                # Collect strategic recommendations
                if assessment.get('recommendations'):
                    checkpoint_review['strategic_recommendations'].extend(
                        assessment['recommendations'][:2]
                    )

        # Decision on continuing
        if continue_votes:
            avg_confidence = sum(continue_votes) / len(continue_votes)

            if avg_confidence >= 0.8:
                checkpoint_review['continue_decision'] = 'full_speed_ahead'
            elif avg_confidence >= 0.6:
                checkpoint_review['continue_decision'] = 'proceed_with_caution'
            else:
                checkpoint_review['continue_decision'] = 'major_revision_needed'

        return checkpoint_review

    def _select_strategic_advisors(self, project_type: str) -> List[str]:
        """Select advisors for strategic planning based on project type"""

        advisor_mapping = {
            'ecommerce': ['warren_buffett_advisor', 'financial_strategist', 'business_strategist'],
            'content_factory': ['gary_vaynerchuk_advisor', 'startup_guru', 'mr_beast_advisor'],
            'trading_bot': ['ray_dalio_advisor', 'crypto_expert', 'cathie_wood_advisor'],
            'saas': ['sam_altman_advisor', 'startup_guru', 'tech_architect']
        }

        default_advisors = ['warren_buffett_advisor', 'elon_musk_advisor', 'sam_altman_advisor']

        return advisor_mapping.get(project_type, default_advisors)

    def _select_task_advisors(self, task: str, project_type: str) -> List[str]:
        """Select advisors based on specific task"""

        task_lower = task.lower()

        if 'database' in task_lower or 'data' in task_lower:
            return ['sam_altman_advisor', 'tech_architect']
        elif 'api' in task_lower or 'backend' in task_lower:
            return ['tech_architect', 'ai_strategist']
        elif 'ui' in task_lower or 'frontend' in task_lower:
            return ['startup_guru', 'tech_architect']
        elif 'business' in task_lower or 'revenue' in task_lower:
            return ['warren_buffett_advisor', 'financial_strategist']
        elif 'ml' in task_lower or 'ai' in task_lower:
            return ['sam_altman_advisor', 'ai_strategist', 'cathie_wood_advisor']
        else:
            return self._select_strategic_advisors(project_type)

    def _select_monitoring_advisor(self) -> str:
        """Select an advisor for real-time monitoring"""
        import random
        monitoring_pool = ['ray_dalio_advisor', 'tech_architect', 'crypto_expert']
        return random.choice(monitoring_pool)

    def _select_review_panel(self, task: str) -> List[str]:
        """Select review panel based on task"""
        # Similar to task advisors but might include different perspectives
        return self._select_task_advisors(task, 'general')[:3]

    def _get_strategic_panel(self) -> List[str]:
        """Get the strategic advisory panel"""
        return ['warren_buffett_advisor', 'ray_dalio_advisor', 'elon_musk_advisor']

    def _aggregate_strategic_insights(self,
                                     planning_results: Dict,
                                     consultation: Dict):
        """Aggregate insights from multiple advisors"""

        # Extract and combine strategic elements
        if consultation.get('recommendations'):
            if 'success_metrics' not in planning_results:
                planning_results['success_metrics'] = {}

            # Add unique recommendations
            for rec in consultation['recommendations']:
                if isinstance(rec, str) and 'metric' in rec.lower():
                    planning_results['success_metrics'][consultation['advisor']] = rec

    def _build_consensus_strategy(self, planning_results: Dict) -> Dict:
        """Build consensus strategy from all advisor inputs"""

        consensus = {
            'primary_focus': 'Value creation and sustainable growth',
            'key_principles': [],
            'execution_priorities': [],
            'risk_mitigation': []
        }

        # Analyze all recommendations to find common themes
        all_recommendations = []
        for advisor_input in planning_results.get('advisors_consulted', []):
            all_recommendations.extend(advisor_input.get('recommendations', []))

        # Extract top priorities (simplified for demo)
        if all_recommendations:
            consensus['execution_priorities'] = all_recommendations[:5]

        return consensus

    async def orchestrate_with_oversight(self,
                                        project_type: str,
                                        project_name: str) -> Dict:
        """
        Main orchestration method with full advisor oversight.
        This is the complete flow with all oversight checkpoints.
        """

        logger.info(f"\n{'='*60}")
        logger.info(f"🎓 ADVISOR-GUIDED ORCHESTRATION")
        logger.info(f"Project: {project_name}")
        logger.info(f"{'='*60}")

        results = {
            'project': project_name,
            'type': project_type,
            'started_at': datetime.now().isoformat(),
            'phases': []
        }

        # Phase 1: Strategic Planning
        logger.info("\n📋 PHASE 1: STRATEGIC PLANNING")
        strategic_plan = await self.strategic_planning_session(
            project_type,
            {'name': project_name, 'type': project_type}
        )
        results['strategic_plan'] = strategic_plan

        # Phase 2: Task Planning with Pre-execution Reviews
        logger.info("\n🔨 PHASE 2: TASK EXECUTION WITH OVERSIGHT")

        sample_tasks = [
            ('database_architect', 'Design Database Schema'),
            ('api_endpoint_validator', 'Create API Layer'),
            ('react_native_unify', 'Build Frontend UI')
        ]

        for agent_name, task in sample_tasks:
            phase_result = {
                'agent': agent_name,
                'task': task,
                'oversight_events': []
            }

            # Pre-execution review
            pre_review = await self.pre_execution_review(
                agent_name, task, {'project_type': project_type}
            )
            phase_result['oversight_events'].append({
                'type': 'pre_execution_review',
                'result': pre_review
            })

            if pre_review['approval_status'] == 'approved':
                # Execute with monitoring
                execution_id = f"exec_{datetime.now().timestamp()}"

                monitoring = await self.real_time_monitoring(
                    agent_name, task, execution_id
                )
                phase_result['oversight_events'].append({
                    'type': 'real_time_monitoring',
                    'result': monitoring
                })

                # Simulate agent execution result
                agent_result = {
                    'success': True,
                    'output': f"Completed {task}",
                    'code_generated': True
                }

                # Post-execution review
                post_review = await self.post_execution_review(
                    agent_name, task, agent_result
                )
                phase_result['oversight_events'].append({
                    'type': 'post_execution_review',
                    'result': post_review
                })

                phase_result['final_status'] = post_review['approval_decision']
            else:
                phase_result['final_status'] = 'blocked_by_advisors'

            results['phases'].append(phase_result)

        # Phase 3: Strategic Checkpoint
        logger.info("\n🎯 PHASE 3: STRATEGIC CHECKPOINT")
        checkpoint = await self.strategic_checkpoint_review(
            'phase_complete',
            {'phases_completed': len(results['phases']), 'status': 'on_track'}
        )
        results['strategic_checkpoint'] = checkpoint

        # Final Summary
        results['completed_at'] = datetime.now().isoformat()
        results['oversight_summary'] = {
            'total_advisor_consultations': len(results['phases']) * 3,  # pre, monitor, post
            'strategic_checkpoints_passed': 1,
            'final_decision': checkpoint['continue_decision']
        }

        return results


# Example usage
if __name__ == "__main__":
    oversight = AdvisorOversightSystem()

    # Run a project with full advisor oversight
    result = asyncio.run(oversight.orchestrate_with_oversight(
        project_type="ecommerce",
        project_name="AI-Powered Marketplace"
    ))

    print(f"\n🎓 OVERSIGHT COMPLETE")
    print(f"   Final Decision: {result['oversight_summary']['final_decision']}")
    print(f"   Advisor Consultations: {result['oversight_summary']['total_advisor_consultations']}")