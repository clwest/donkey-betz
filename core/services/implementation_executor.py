"""
Implementation Executor Service
Session 690: Execute implementations from completed pilots

This service is the "brain stem" that translates pilot decisions into actual changes.

Execution Flow:
1. Receive implementation from completed pilot
2. Route to appropriate handler based on implementation_type
3. Execute the implementation
4. Record actions and artifacts
5. Update implementation status

Handlers:
- AgentUpdateHandler: Updates agent behavior/prompts
- CodeGenerationHandler: Routes to FullStackDeveloperAgent
- WorkflowUpdateHandler: Creates/modifies workflow templates
- PromptUpdateHandler: Updates central prompt registry
- TaskCreationHandler: Creates human tasks
- ExperimentSetupHandler: Sets up experiments
"""

import logging
from typing import Dict, Any, Optional, List
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)


class ImplementationExecutor:
    """
    Main executor that routes implementations to appropriate handlers.
    """

    def __init__(self):
        self.handlers = {
            'agent_update': AgentUpdateHandler(),
            'code_generation': CodeGenerationHandler(),
            'workflow_update': WorkflowUpdateHandler(),
            'prompt_update': PromptUpdateHandler(),
            'task_creation': TaskCreationHandler(),
            'experiment_setup': ExperimentSetupHandler(),
            'config_update': ConfigUpdateHandler(),
        }

    def execute(self, implementation) -> Dict[str, Any]:
        """
        Execute an implementation.

        Args:
            implementation: PilotImplementation instance

        Returns:
            Dict with execution results
        """
        from core.models_implementation_pipeline import (
            ImplementationAction,
            ImplementationStatus
        )

        logger.info(f"Executing implementation: {implementation.id} ({implementation.implementation_type})")

        # Start the implementation
        implementation.start_implementation()

        handler = self.handlers.get(implementation.implementation_type)
        if not handler:
            implementation.fail_implementation(
                f"No handler for implementation type: {implementation.implementation_type}"
            )
            return {'success': False, 'error': 'No handler found'}

        try:
            # Execute via handler
            result = handler.execute(implementation)

            if result.get('success'):
                implementation.complete_implementation(
                    result=result,
                    artifacts=result.get('artifacts', [])
                )
                implementation.executed_by = result.get('executed_by', handler.__class__.__name__)
                implementation.save()

                # Record actions
                for action in result.get('actions', []):
                    ImplementationAction.objects.create(
                        implementation=implementation,
                        action_type=action.get('type', 'unknown'),
                        description=action.get('description', ''),
                        performed_by=action.get('performed_by', handler.__class__.__name__),
                        success=action.get('success', True),
                        result_data=action.get('result', {}),
                        files_created=action.get('files_created', []),
                        files_modified=action.get('files_modified', [])
                    )

                logger.info(f"Implementation {implementation.id} completed successfully")

            elif result.get('requires_human'):
                implementation.mark_requires_human(result.get('reason', 'Human review required'))

            else:
                implementation.fail_implementation(result.get('error', 'Unknown error'))

            return result

        except Exception as e:
            error_msg = f"Implementation execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            implementation.fail_implementation(error_msg)
            return {'success': False, 'error': error_msg}


class BaseHandler:
    """Base class for implementation handlers."""

    def execute(self, implementation) -> Dict[str, Any]:
        """Execute the implementation. Override in subclasses."""
        raise NotImplementedError


class AgentUpdateHandler(BaseHandler):
    """
    Handle agent behavior updates.

    This can:
    1. Update agent system prompts
    2. Modify agent configurations
    3. Add new capabilities to agents
    """

    def execute(self, implementation) -> Dict[str, Any]:
        from core.agent_router import AgentRouter

        plan = implementation.implementation_plan
        decision = implementation.pilot.gate.decision

        actions = []
        artifacts = []

        # Get target agents
        target_agents = plan.get('target_agents', [])
        if not target_agents:
            return {
                'success': False,
                'error': 'No target agents specified'
            }

        # Build the behavior update
        behavior_update = {
            'key_insights': decision.key_insights or [],
            'recommended_stance': decision.recommended_stance,
            'rationale': decision.rationale,
            'source_pilot': str(implementation.pilot.id),
            'applied_at': timezone.now().isoformat()
        }

        # For each target agent, record the learning
        for agent_name in target_agents:
            try:
                # Store as learning insight (Session 690)
                from core.models.ai_learning.models import LearningInsight

                # Create a learning insight from the pilot decision
                insight, created = LearningInsight.objects.get_or_create(
                    insight_type='pilot_learning',
                    insight_category=decision.impact_area,
                    title=f"Pilot: {decision.topic[:150]}",
                    defaults={
                        'description': decision.suggested_feature or decision.recommended_stance,
                        'solution_approach': '\n'.join(decision.key_insights or []),
                        'confidence_level': 0.82,
                        'applicability_scope': {
                            'agent': agent_name,
                            'decision_type': decision.decision_type,
                            'impact_area': decision.impact_area,
                            'source_pilot': str(implementation.pilot.id),
                            'applied_at': behavior_update['applied_at']
                        }
                    }
                )

                actions.append({
                    'type': 'learning_insight_created',
                    'description': f"Added learning insight for {agent_name}: {decision.topic[:50]}",
                    'performed_by': 'AgentUpdateHandler',
                    'success': True,
                    'result': {
                        'agent': agent_name,
                        'insight_id': str(insight.id),
                        'created': created
                    }
                })

                logger.info(f"Applied learning insight for agent {agent_name}")

            except Exception as e:
                logger.error(f"Failed to update agent {agent_name}: {e}")
                actions.append({
                    'type': 'agent_knowledge_update',
                    'description': f"Failed to update {agent_name}: {str(e)}",
                    'performed_by': 'AgentUpdateHandler',
                    'success': False,
                    'error': str(e)
                })

        # Check if any succeeded
        successful = [a for a in actions if a.get('success')]
        if not successful:
            return {
                'success': False,
                'error': 'All agent updates failed',
                'actions': actions
            }

        return {
            'success': True,
            'executed_by': 'AgentUpdateHandler',
            'actions': actions,
            'artifacts': artifacts,
            'summary': f"Updated {len(successful)} agents with pilot learnings"
        }


class CodeGenerationHandler(BaseHandler):
    """
    Handle code generation requests.

    Routes to FullStackDeveloperAgent for implementation.
    """

    def execute(self, implementation) -> Dict[str, Any]:
        plan = implementation.implementation_plan
        decision = implementation.pilot.gate.decision

        # Build code generation request
        feature_spec = {
            'description': decision.suggested_feature,
            'requirements': decision.key_insights or [],
            'rationale': decision.rationale,
            'impact_area': decision.impact_area
        }

        try:
            # Route to FullStackDeveloperAgent
            from core.agents import FullStackDeveloperAgent

            agent = FullStackDeveloperAgent()
            prompt = f"""
Implement the following feature based on a completed pilot decision:

FEATURE DESCRIPTION:
{decision.suggested_feature}

KEY REQUIREMENTS:
{chr(10).join(f"- {i}" for i in (decision.key_insights or []))}

RATIONALE:
{decision.rationale}

IMPACT AREA: {decision.impact_area}

Please provide:
1. Implementation approach
2. Files to create/modify
3. Code snippets or full implementations
4. Testing recommendations
"""

            # Session 691: Fixed - use correct parameter names for execute()
            result = agent.execute(
                task=prompt,  # Changed from prompt=prompt
                context={
                    'pilot_id': str(implementation.pilot.id),
                    'decision_id': str(decision.id),
                    'feature_spec': feature_spec
                },
                scifi_context={},  # Required parameter
                spider_context={}  # Required parameter
            )

            # Session 691: AgentResult object - access .message for the content
            result_message = result.message if hasattr(result, 'message') else str(result)
            result_success = result.success if hasattr(result, 'success') else True
            result_data = result.data if hasattr(result, 'data') else {}

            return {
                'success': result_success,
                'executed_by': 'CodeGenerationHandler → FullStackDeveloperAgent',
                'actions': [{
                    'type': 'code_generation',
                    'description': f"Generated implementation for: {decision.topic[:50]}",
                    'performed_by': 'FullStackDeveloperAgent',
                    'success': result_success,
                    'result': {
                        'response_preview': result_message[:1000] if result_message else '',
                        'data': result_data
                    }
                }],
                'artifacts': [{
                    'type': 'generated_code',
                    'content_preview': result_message[:500] if result_message else ''
                }],
                'summary': f"Code generated by FullStackDeveloperAgent: {result_message[:100] if result_message else 'No content'}..."
            }

        except Exception as e:
            logger.error(f"Code generation failed: {e}", exc_info=True)
            return {
                'requires_human': True,
                'reason': f"Code generation failed: {str(e)}. Manual implementation required.",
                'feature_spec': feature_spec
            }


class WorkflowUpdateHandler(BaseHandler):
    """
    Handle workflow template updates.
    """

    def execute(self, implementation) -> Dict[str, Any]:
        plan = implementation.implementation_plan
        decision = implementation.pilot.gate.decision

        try:
            # Create or update workflow template
            from core.models_unified_system import WorkflowTemplate

            template_name = f"From Pilot: {decision.topic[:50]}"
            template, created = WorkflowTemplate.objects.get_or_create(
                name=template_name,
                defaults={
                    'description': decision.suggested_feature or decision.recommended_stance,
                    'workflow_type': 'pilot_derived',
                    'steps': self._build_workflow_steps(decision),
                    'is_active': True,
                    'metadata': {
                        'source_pilot': str(implementation.pilot.id),
                        'decision_type': decision.decision_type,
                        'impact_area': decision.impact_area
                    }
                }
            )

            action = 'Created' if created else 'Updated'

            return {
                'success': True,
                'executed_by': 'WorkflowUpdateHandler',
                'actions': [{
                    'type': 'workflow_template_update',
                    'description': f"{action} workflow template: {template_name}",
                    'performed_by': 'WorkflowUpdateHandler',
                    'success': True,
                    'result': {
                        'template_id': str(template.id),
                        'template_name': template_name,
                        'created': created
                    }
                }],
                'artifacts': [{
                    'type': 'workflow_template',
                    'id': str(template.id),
                    'name': template_name
                }],
                'summary': f"{action} workflow template: {template_name}"
            }

        except Exception as e:
            logger.error(f"Workflow update failed: {e}")
            return {
                'requires_human': True,
                'reason': f"Workflow update failed: {str(e)}"
            }

    def _build_workflow_steps(self, decision) -> list:
        """Build workflow steps from decision insights."""
        steps = []
        for i, insight in enumerate(decision.key_insights or [], 1):
            steps.append({
                'step_number': i,
                'name': f"Step {i}",
                'description': insight,
                'agent': None,  # To be assigned
                'required': True
            })
        return steps


class PromptUpdateHandler(BaseHandler):
    """
    Handle prompt registry updates.
    """

    def execute(self, implementation) -> Dict[str, Any]:
        plan = implementation.implementation_plan
        decision = implementation.pilot.gate.decision

        try:
            # Store as a prompt learning in the registry
            from core.prompts import get_prompt_registry

            registry = get_prompt_registry()

            # Add as a learned prompt enhancement
            prompt_key = f"pilot_learning_{implementation.pilot.id}"
            prompt_content = f"""
# Learned from Pilot: {decision.topic}

## Key Insights:
{chr(10).join(f"- {i}" for i in (decision.key_insights or []))}

## Recommended Approach:
{decision.recommended_stance}

## Rationale:
{decision.rationale}
"""

            # Store in database for persistence
            from core.models_unified_system import PromptTemplate
            template, created = PromptTemplate.objects.get_or_create(
                name=prompt_key,
                defaults={
                    'content': prompt_content,
                    'category': 'pilot_learnings',
                    'description': f"Learning from pilot: {decision.topic[:100]}",
                    'is_active': True
                }
            )

            return {
                'success': True,
                'executed_by': 'PromptUpdateHandler',
                'actions': [{
                    'type': 'prompt_update',
                    'description': f"Added prompt learning: {prompt_key}",
                    'performed_by': 'PromptUpdateHandler',
                    'success': True,
                    'result': {
                        'prompt_key': prompt_key,
                        'created': created
                    }
                }],
                'summary': f"Added prompt learning from pilot"
            }

        except Exception as e:
            logger.error(f"Prompt update failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }


class TaskCreationHandler(BaseHandler):
    """
    Create human tasks for implementations that require manual work.
    """

    def execute(self, implementation) -> Dict[str, Any]:
        plan = implementation.implementation_plan
        decision = implementation.pilot.gate.decision

        try:
            from core.models_unified_system import ActionableTask

            # Determine priority based on impact
            priority_map = {
                'security': 'high',
                'infrastructure': 'high',
                'product': 'medium',
                'agents': 'medium',
                'workflow': 'low'
            }
            priority = priority_map.get(decision.impact_area, 'medium')

            task = ActionableTask.objects.create(
                title=f"Implement: {decision.topic[:80]}",
                description=f"""
## Pilot Implementation Required

**Pilot:** {implementation.pilot.name}
**Status:** Completed Successfully
**Decision Type:** {decision.decision_type}
**Impact Area:** {decision.impact_area}

### Recommended Action
{decision.recommended_stance}

### Suggested Feature
{decision.suggested_feature or 'See key insights below'}

### Key Insights
{chr(10).join(f"- {i}" for i in (decision.key_insights or []))}

### Rationale
{decision.rationale}

---
*This task was auto-generated from a completed pilot that requires human implementation.*
""",
                task_type='pilot_implementation',
                priority=priority,
                metadata={
                    'pilot_id': str(implementation.pilot.id),
                    'implementation_id': str(implementation.id),
                    'decision_id': str(decision.id),
                    'auto_generated': True
                }
            )

            return {
                'success': True,
                'executed_by': 'TaskCreationHandler',
                'actions': [{
                    'type': 'task_creation',
                    'description': f"Created human task: {task.title}",
                    'performed_by': 'TaskCreationHandler',
                    'success': True,
                    'result': {
                        'task_id': str(task.id),
                        'priority': priority
                    }
                }],
                'artifacts': [{
                    'type': 'actionable_task',
                    'id': str(task.id),
                    'title': task.title,
                    'priority': priority
                }],
                'summary': f"Created {priority}-priority task for human implementation"
            }

        except Exception as e:
            logger.error(f"Task creation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }


class ExperimentSetupHandler(BaseHandler):
    """
    Set up experiments from pilot decisions.
    """

    def execute(self, implementation) -> Dict[str, Any]:
        plan = implementation.implementation_plan
        decision = implementation.pilot.gate.decision

        try:
            from core.models_pilot_readiness import ExperimentTracking

            # Create experiment from pilot
            experiment = ExperimentTracking.objects.create(
                name=f"Exp: {decision.topic[:80]}",
                hypothesis=decision.suggested_feature or decision.recommended_stance,
                description=f"Experiment derived from pilot: {implementation.pilot.name}",
                status='active',
                source_pilot=implementation.pilot,
                kpis=self._extract_kpis(decision),
                experiment_type='pilot_derived'
            )

            return {
                'success': True,
                'executed_by': 'ExperimentSetupHandler',
                'actions': [{
                    'type': 'experiment_setup',
                    'description': f"Created experiment: {experiment.name}",
                    'performed_by': 'ExperimentSetupHandler',
                    'success': True,
                    'result': {
                        'experiment_id': str(experiment.id),
                        'experiment_name': experiment.name
                    }
                }],
                'artifacts': [{
                    'type': 'experiment',
                    'id': str(experiment.id),
                    'name': experiment.name
                }],
                'summary': f"Created experiment: {experiment.name}"
            }

        except Exception as e:
            logger.error(f"Experiment setup failed: {e}")
            return {
                'requires_human': True,
                'reason': f"Experiment setup failed: {str(e)}"
            }

    def _extract_kpis(self, decision) -> list:
        """Extract KPIs from decision insights."""
        # Default KPIs based on impact area
        kpi_templates = {
            'agents': ['agent_accuracy', 'response_time', 'user_satisfaction'],
            'product': ['user_engagement', 'conversion_rate', 'retention'],
            'workflow': ['completion_rate', 'time_to_complete', 'error_rate'],
            'research': ['relevance_score', 'coverage', 'freshness']
        }
        return kpi_templates.get(decision.impact_area, ['success_rate', 'adoption'])


class ConfigUpdateHandler(BaseHandler):
    """
    Handle system configuration updates.
    """

    def execute(self, implementation) -> Dict[str, Any]:
        # Config updates always require human review for safety
        return {
            'requires_human': True,
            'reason': 'Configuration updates require human review for safety'
        }


# Convenience function
def execute_implementation(implementation) -> Dict[str, Any]:
    """Execute a single implementation."""
    executor = ImplementationExecutor()
    return executor.execute(implementation)
