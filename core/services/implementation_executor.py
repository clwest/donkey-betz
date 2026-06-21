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

    Stores workflow as a Deliverable (type=document, category=Workflow)
    so it's visible in the deliverables library and can be executed later.
    """

    def execute(self, implementation) -> Dict[str, Any]:
        plan = implementation.implementation_plan
        decision = implementation.pilot.gate.decision

        template_name = f"Workflow: {decision.topic[:80]}"
        workflow_steps = self._build_workflow_steps(decision)

        # Build structured content
        content = f"# {template_name}\n\n"
        content += f"**Source:** Pilot {implementation.pilot.name}\n"
        content += f"**Impact Area:** {decision.impact_area}\n\n"
        content += f"## Description\n{decision.suggested_feature or decision.recommended_stance}\n\n"
        content += "## Steps\n"
        for step in workflow_steps:
            content += f"{step['step_number']}. {step['description']}\n"
        content += f"\n## Rationale\n{decision.rationale}\n"

        try:
            from core.models_deliverables import Deliverable
            from core.services.deliverable_workspace_resolver import resolve_workspace
            ws, ws_saved = resolve_workspace()

            from core.services.deliverable_factory import create_deliverable
            deliverable = create_deliverable(
                title=template_name,
                content=content,
                agent_name='WorkflowUpdateHandler',
                category='Workflow',
                deliverable_type='document',
                agent_task=f"Pilot implementation: {decision.topic[:100]}",
                quality_score=0.75,
                is_saved=ws_saved,
                metadata={
                    'source_pilot': str(implementation.pilot.id),
                    'decision_type': decision.decision_type,
                    'impact_area': decision.impact_area,
                    'workflow_steps': workflow_steps,
                    'trigger_source': 'direct',
                },
                preview_content=content[:500],
                status='completed',
                workspace=ws,
            )

            return {
                'success': True,
                'executed_by': 'WorkflowUpdateHandler',
                'actions': [{
                    'type': 'workflow_created',
                    'description': f"Created workflow deliverable: {template_name}",
                    'performed_by': 'WorkflowUpdateHandler',
                    'success': True,
                    'result': {'deliverable_id': str(deliverable.id)},
                }],
                'artifacts': [{'type': 'deliverable', 'id': str(deliverable.id), 'name': template_name}],
                'summary': f"Workflow created as deliverable: {template_name}",
            }
        except Exception as e:
            logger.error(f"WorkflowUpdateHandler failed: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _build_workflow_steps(self, decision) -> list:
        steps = []
        for i, insight in enumerate(decision.key_insights or [], 1):
            steps.append({
                'step_number': i,
                'name': f"Step {i}",
                'description': insight,
                'required': True,
            })
        return steps


class PromptUpdateHandler(BaseHandler):
    """
    Handle prompt registry updates.

    Stores pilot learnings as AgentKnowledgeSource entries so they're
    automatically injected into agent prompts via the knowledge pipeline.
    """

    def execute(self, implementation) -> Dict[str, Any]:
        plan = implementation.implementation_plan
        decision = implementation.pilot.gate.decision

        prompt_content = (
            f"Pilot Learning: {decision.topic}\n\n"
            f"Key Insights:\n"
            + '\n'.join(f"- {i}" for i in (decision.key_insights or []))
            + f"\n\nRecommended Approach: {decision.recommended_stance}"
            + f"\n\nRationale: {decision.rationale}"
        )

        try:
            from core.models_unified_system import AgentKnowledgeSource

            # Store as knowledge accessible to all relevant agents
            target_agents = plan.get('target_agents', [])
            created_items = []

            if not target_agents:
                # Create a general knowledge entry
                knowledge, created = AgentKnowledgeSource.objects.get_or_create(
                    knowledge_type='pilot_learning',
                    title=f"Pilot: {decision.topic[:150]}",
                    defaults={
                        'knowledge_value': prompt_content,
                        'source': f'pilot:{implementation.pilot.id}',
                    },
                )
                created_items.append({'id': str(knowledge.id), 'agent': 'general', 'created': created})
            else:
                from core.models_unified_system import Agent as AgentModel
                for agent_name in target_agents:
                    agent_obj = AgentModel.objects.filter(name=agent_name).first()
                    if not agent_obj:
                        continue
                    knowledge, created = AgentKnowledgeSource.objects.get_or_create(
                        agent=agent_obj,
                        knowledge_type='pilot_learning',
                        title=f"Pilot: {decision.topic[:150]}",
                        defaults={
                            'knowledge_value': prompt_content,
                            'source': f'pilot:{implementation.pilot.id}',
                        },
                    )
                    created_items.append({'id': str(knowledge.id), 'agent': agent_name, 'created': created})

            return {
                'success': True,
                'executed_by': 'PromptUpdateHandler',
                'actions': [{
                    'type': 'knowledge_created',
                    'description': f"Stored pilot learning as agent knowledge ({len(created_items)} entries)",
                    'performed_by': 'PromptUpdateHandler',
                    'success': True,
                    'result': {'entries': created_items},
                }],
                'artifacts': [{'type': 'agent_knowledge', 'entries': created_items}],
                'summary': f"Stored pilot learning as {len(created_items)} AgentKnowledgeSource entries",
            }
        except Exception as e:
            logger.error(f"PromptUpdateHandler failed: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}


class TaskCreationHandler(BaseHandler):
    """
    Create human tasks for implementations that require manual work.

    Creates HumanAttentionItems (for urgent/human review) and/or
    InitiativeActionItems (for tracked work items).
    """

    def execute(self, implementation) -> Dict[str, Any]:
        plan = implementation.implementation_plan
        decision = implementation.pilot.gate.decision

        priority_map = {
            'security': 'critical',
            'infrastructure': 'high',
            'product': 'medium',
            'agents': 'medium',
            'workflow': 'low',
        }
        priority = priority_map.get(decision.impact_area, 'medium')

        task_title = f"Implement: {decision.topic[:80]}"
        task_description = (
            f"Pilot: {implementation.pilot.name}\n"
            f"Decision: {decision.recommended_stance}\n"
            f"Feature: {decision.suggested_feature or 'See insights'}\n\n"
            f"Insights:\n"
            + '\n'.join(f"- {i}" for i in (decision.key_insights or []))
            + f"\n\nRationale: {decision.rationale}"
        )

        actions = []

        # Create a HumanAttentionItem so it shows up in the boardroom
        try:
            from core.models_human_interface import HumanAttentionItem
            from django.contrib.auth import get_user_model

            User = get_user_model()
            user = User.objects.filter(is_superuser=True).first()
            if user:
                item = HumanAttentionItem.objects.create(
                    user=user,
                    item_type='pilot_implementation',
                    title=task_title,
                    description=task_description[:2000],
                    priority=priority,
                    source_type='pilot',
                    source_id=str(implementation.pilot.id),
                    metadata={
                        'pilot_id': str(implementation.pilot.id),
                        'implementation_id': str(implementation.id),
                        'decision_type': decision.decision_type,
                        'impact_area': decision.impact_area,
                    },
                )
                actions.append({
                    'type': 'attention_item_created',
                    'description': f"Created attention item: {task_title}",
                    'performed_by': 'TaskCreationHandler',
                    'success': True,
                    'result': {'attention_item_id': str(item.id), 'priority': priority},
                })
        except Exception as e:
            logger.error(f"TaskCreationHandler attention item failed: {e}")
            actions.append({
                'type': 'attention_item_failed',
                'description': str(e),
                'performed_by': 'TaskCreationHandler',
                'success': False,
            })

        return {
            'success': len([a for a in actions if a.get('success')]) > 0,
            'executed_by': 'TaskCreationHandler',
            'actions': actions,
            'artifacts': [{'type': 'task', 'title': task_title, 'priority': priority}],
            'summary': f"Created task ({priority}): {task_title}",
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

    Creates a HumanAttentionItem with the proposed config change
    so it can be reviewed and applied manually. Config changes are
    too sensitive for auto-execution.
    """

    def execute(self, implementation) -> Dict[str, Any]:
        decision = implementation.pilot.gate.decision

        # Store the proposed change as a deliverable for reference
        try:
            from core.models_deliverables import Deliverable
            from core.services.deliverable_workspace_resolver import resolve_workspace
            ws, ws_saved = resolve_workspace()

            content = (
                f"# Config Change Proposal\n\n"
                f"**Source:** Pilot {implementation.pilot.name}\n"
                f"**Impact Area:** {decision.impact_area}\n\n"
                f"## Proposed Change\n{decision.suggested_feature or decision.recommended_stance}\n\n"
                f"## Rationale\n{decision.rationale}\n\n"
                f"## Key Insights\n"
                + '\n'.join(f"- {i}" for i in (decision.key_insights or []))
                + "\n\n---\n*Requires human review before applying.*"
            )

            from core.services.deliverable_factory import create_deliverable
            create_deliverable(
                title=f"Config Proposal: {decision.topic[:80]}",
                content=content,
                agent_name='ConfigUpdateHandler',
                category='Config Proposals',
                deliverable_type='document',
                is_saved=ws_saved,
                metadata={
                    'source_pilot': str(implementation.pilot.id),
                    'requires_human': True,
                    'trigger_source': 'direct',
                },
                preview_content=content[:500],
                status='completed',
                workspace=ws,
            )
        except Exception as e:
            logger.debug(f"ConfigUpdateHandler deliverable save failed: {e}")

        return {
            'requires_human': True,
            'reason': (
                f'Config change for {decision.impact_area}: '
                f'{(decision.suggested_feature or decision.recommended_stance)[:200]}. '
                f'Saved as deliverable for review.'
            ),
        }


# Convenience function
def execute_implementation(implementation) -> Dict[str, Any]:
    """Execute a single implementation."""
    executor = ImplementationExecutor()
    return executor.execute(implementation)
