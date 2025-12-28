"""
Session 228: Team Workflow Execution Engine

Makes teams of agents actually collaborate on complex tasks.
Handles step-by-step execution, agent handoffs, and progress tracking.
"""

import logging
from typing import Dict, List, Optional
from django.utils import timezone
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


# Workflow Templates - Define how teams collaborate
WORKFLOW_TEMPLATES = {
    'logo_creation': {
        'name': 'Logo Creation Workflow',
        'description': 'Research, design, and review a professional logo',
        'steps': [
            {
                'name': 'Research Phase',
                'action': 'research_brand',
                'role_type': 'researcher',
                'description': 'Research brand identity, competitors, and style trends',
                'estimated_duration': 300,  # seconds
                'tools': ['web_search', 'spider_data'],
            },
            {
                'name': 'Strategy Development',
                'action': 'develop_strategy',
                'role_type': 'strategist',
                'description': 'Develop creative direction based on research',
                'estimated_duration': 180,
                'depends_on': [0],
            },
            {
                'name': 'Design Creation',
                'action': 'create_design',
                'role_type': 'designer',
                'description': 'Create logo designs using AI generation',
                'estimated_duration': 600,
                'tools': ['stability_ai', 'image_generation'],
                'depends_on': [1],
            },
            {
                'name': 'Quality Review',
                'action': 'review_design',
                'role_type': 'reviewer',
                'description': 'Review and critique the logo designs',
                'estimated_duration': 180,
                'depends_on': [2],
            },
            {
                'name': 'Optimization',
                'action': 'optimize_design',
                'role_type': 'optimizer',
                'description': 'Refine based on feedback',
                'estimated_duration': 300,
                'tools': ['image_editing'],
                'depends_on': [3],
            },
        ]
    },
    'content_writing': {
        'name': 'Content Writing Workflow',
        'description': 'Research, write, and review content',
        'steps': [
            {
                'name': 'Topic Research',
                'action': 'research_topic',
                'role_type': 'researcher',
                'description': 'Research the topic thoroughly',
                'estimated_duration': 300,
                'tools': ['web_search', 'spider_data'],
            },
            {
                'name': 'Content Strategy',
                'action': 'plan_content',
                'role_type': 'strategist',
                'description': 'Plan content structure and key points',
                'estimated_duration': 180,
                'depends_on': [0],
            },
            {
                'name': 'Writing',
                'action': 'write_content',
                'role_type': 'writer',
                'description': 'Write the content based on research and strategy',
                'estimated_duration': 600,
                'tools': ['text_generation'],
                'depends_on': [1],
            },
            {
                'name': 'Review & Edit',
                'action': 'review_content',
                'role_type': 'reviewer',
                'description': 'Review and suggest improvements',
                'estimated_duration': 180,
                'depends_on': [2],
            },
            {
                'name': 'Final Polish',
                'action': 'polish_content',
                'role_type': 'optimizer',
                'description': 'Apply final improvements',
                'estimated_duration': 180,
                'depends_on': [3],
            },
        ]
    },
    'brand_package': {
        'name': 'Brand Package Workflow',
        'description': 'Complete brand identity package',
        'steps': [
            {
                'name': 'Brand Research',
                'action': 'research_brand',
                'role_type': 'researcher',
                'description': 'Research brand positioning and competitors',
                'estimated_duration': 400,
                'tools': ['web_search', 'spider_data'],
            },
            {
                'name': 'Brand Strategy',
                'action': 'develop_brand_strategy',
                'role_type': 'strategist',
                'description': 'Define brand voice, values, and visual direction',
                'estimated_duration': 300,
                'depends_on': [0],
            },
            {
                'name': 'Logo Design',
                'action': 'design_logo',
                'role_type': 'designer',
                'description': 'Create primary logo',
                'estimated_duration': 600,
                'tools': ['stability_ai'],
                'depends_on': [1],
            },
            {
                'name': 'Color Palette',
                'action': 'create_colors',
                'role_type': 'designer',
                'description': 'Define brand color palette',
                'estimated_duration': 300,
                'depends_on': [1],
            },
            {
                'name': 'Brand Copy',
                'action': 'write_brand_copy',
                'role_type': 'writer',
                'description': 'Write tagline and brand messaging',
                'estimated_duration': 400,
                'depends_on': [1],
            },
            {
                'name': 'Review All',
                'action': 'review_brand',
                'role_type': 'reviewer',
                'description': 'Review complete brand package',
                'estimated_duration': 300,
                'depends_on': [2, 3, 4],
            },
            {
                'name': 'Final Refinement',
                'action': 'refine_brand',
                'role_type': 'optimizer',
                'description': 'Apply final refinements',
                'estimated_duration': 300,
                'depends_on': [5],
            },
        ]
    },
    'creative_content': {
        'name': 'Creative Content Workflow',
        'description': 'General creative content production',
        'steps': [
            {
                'name': 'Research',
                'action': 'research',
                'role_type': 'researcher',
                'description': 'Research the topic or subject',
                'estimated_duration': 300,
            },
            {
                'name': 'Planning',
                'action': 'plan',
                'role_type': 'strategist',
                'description': 'Plan the creative approach',
                'estimated_duration': 180,
                'depends_on': [0],
            },
            {
                'name': 'Creation',
                'action': 'create',
                'role_type': 'designer',
                'description': 'Create the content',
                'estimated_duration': 600,
                'depends_on': [1],
            },
            {
                'name': 'Review',
                'action': 'review',
                'role_type': 'reviewer',
                'description': 'Review and provide feedback',
                'estimated_duration': 180,
                'depends_on': [2],
            },
        ]
    },
    'social_media_campaign': {
        'name': 'Social Media Campaign',
        'description': 'Create a complete social media campaign',
        'steps': [
            {
                'name': 'Audience Research',
                'action': 'research_audience',
                'role_type': 'researcher',
                'description': 'Research target audience and trends',
                'estimated_duration': 300,
                'tools': ['web_search', 'spider_data'],
            },
            {
                'name': 'Campaign Strategy',
                'action': 'plan_campaign',
                'role_type': 'strategist',
                'description': 'Plan campaign messaging and schedule',
                'estimated_duration': 300,
                'depends_on': [0],
            },
            {
                'name': 'Visual Content',
                'action': 'create_visuals',
                'role_type': 'designer',
                'description': 'Create images and graphics',
                'estimated_duration': 600,
                'tools': ['stability_ai'],
                'depends_on': [1],
            },
            {
                'name': 'Copy Writing',
                'action': 'write_copy',
                'role_type': 'writer',
                'description': 'Write captions and copy',
                'estimated_duration': 400,
                'depends_on': [1],
            },
            {
                'name': 'Content Review',
                'action': 'review_campaign',
                'role_type': 'reviewer',
                'description': 'Review all campaign content',
                'estimated_duration': 180,
                'depends_on': [2, 3],
            },
            {
                'name': 'Final Optimization',
                'action': 'optimize_campaign',
                'role_type': 'optimizer',
                'description': 'Optimize for engagement',
                'estimated_duration': 180,
                'depends_on': [4],
            },
        ]
    },
}


class TeamWorkflowEngine:
    """
    Engine for executing team workflows with agent collaboration.
    """

    def __init__(self):
        self.channel_layer = get_channel_layer()

    def get_template(self, template_name: str) -> Optional[Dict]:
        """Get a workflow template by name."""
        return WORKFLOW_TEMPLATES.get(template_name)

    def list_templates(self) -> List[Dict]:
        """List all available workflow templates."""
        return [
            {
                'id': key,
                'name': template['name'],
                'description': template['description'],
                'steps_count': len(template['steps']),
                'roles_needed': list(set(s['role_type'] for s in template['steps']))
            }
            for key, template in WORKFLOW_TEMPLATES.items()
        ]

    @transaction.atomic
    def initialize_workflow(self, workflow) -> bool:
        """
        Initialize a workflow with steps from template.
        Creates TeamWorkflowStep records for each step.
        """
        from core.models_unified_system import TeamWorkflowStep, AgentRole

        template_name = workflow.workflow_template
        template = self.get_template(template_name)

        if not template:
            # Use generic creative_content template
            template = WORKFLOW_TEMPLATES['creative_content']

        # Store template steps in workflow
        workflow.steps = template['steps']
        workflow.save()

        # Create step execution records
        step_objects = []
        for i, step_def in enumerate(template['steps']):
            # Find role for this step
            role = AgentRole.objects.filter(role_type=step_def['role_type']).first()

            step = TeamWorkflowStep.objects.create(
                workflow=workflow,
                step_number=i,
                step_name=step_def['name'],
                action=step_def['action'],
                status='pending',
                required_role=role,
                input_data={
                    'description': step_def.get('description', ''),
                    'tools': step_def.get('tools', []),
                    'estimated_duration': step_def.get('estimated_duration', 300),
                }
            )
            step_objects.append(step)

        # Set up dependencies
        for i, step_def in enumerate(template['steps']):
            if 'depends_on' in step_def:
                step = step_objects[i]
                for dep_idx in step_def['depends_on']:
                    step.depends_on.add(step_objects[dep_idx])

        logger.info(f"Initialized workflow {workflow.id} with {len(step_objects)} steps")
        return True

    @transaction.atomic
    def start_workflow(self, workflow) -> Dict:
        """
        Start executing a workflow.
        Assigns first available steps to agents.
        """

        if workflow.status == 'active':
            return {'success': False, 'error': 'Workflow already active'}

        # Initialize if not done
        if not workflow.step_executions.exists():
            self.initialize_workflow(workflow)

        # Mark workflow as active
        workflow.status = 'active'
        workflow.started_at = timezone.now()
        workflow.save()

        # Find steps that can start (no dependencies or all deps complete)
        ready_steps = self._get_ready_steps(workflow)

        assigned_count = 0
        for step in ready_steps:
            if self._assign_step_to_agent(workflow, step):
                assigned_count += 1

        # Broadcast workflow started
        self._broadcast_workflow_update(workflow, 'workflow_started', {
            'steps_assigned': assigned_count,
            'total_steps': workflow.step_executions.count(),
        })

        return {
            'success': True,
            'message': f'Workflow started with {assigned_count} steps assigned',
            'steps_assigned': assigned_count,
        }

    def _get_ready_steps(self, workflow) -> List:
        """Get steps that are ready to execute (dependencies satisfied)."""

        ready = []
        pending_steps = workflow.step_executions.filter(status='pending')

        for step in pending_steps:
            dependencies = step.depends_on.all()
            if not dependencies.exists():
                ready.append(step)
            elif all(dep.status == 'completed' for dep in dependencies):
                ready.append(step)

        return ready

    def _assign_step_to_agent(self, workflow, step) -> bool:
        """Assign a workflow step to an appropriate agent."""
        from core.models_unified_system import AgentTeamMembership, AgentMessage

        # Find agent with required role in this team
        membership = AgentTeamMembership.objects.filter(
            team=workflow.team,
            role=step.required_role
        ).first()

        if not membership:
            # Fallback: find any agent with matching role type
            membership = AgentTeamMembership.objects.filter(
                team=workflow.team,
                role__role_type=step.required_role.role_type if step.required_role else None
            ).first()

        if not membership:
            # Fallback: assign to team lead
            membership = AgentTeamMembership.objects.filter(
                team=workflow.team,
                is_lead=True
            ).first()

        if not membership:
            logger.warning(f"No agent found for step {step.id}")
            return False

        # Assign step
        step.assigned_agent = membership.agent
        step.status = 'assigned'
        step.save()

        # Create task request message
        if workflow.team.lead_agent and membership.agent:
            AgentMessage.objects.create(
                sender_agent=workflow.team.lead_agent,
                receiver_agent=membership.agent,
                message_type='request',
                subject=f'Task Assignment: {step.step_name}',
                content=f"You have been assigned to: {step.step_name}\n\n{step.input_data.get('description', '')}",
                task_context={
                    'workflow_id': str(workflow.id),
                    'step_id': str(step.id),
                    'action': step.action,
                    'tools': step.input_data.get('tools', []),
                },
                priority=7,
            )

        # Broadcast step assigned
        self._broadcast_workflow_update(workflow, 'step_assigned', {
            'step_id': str(step.id),
            'step_name': step.step_name,
            'agent_id': str(membership.agent.id),
            'agent_name': membership.agent.name,
        })

        logger.info(f"Assigned step {step.step_name} to agent {membership.agent.name}")
        return True

    @transaction.atomic
    def execute_step(self, step, input_data: Dict = None) -> Dict:
        """
        Execute a workflow step.
        This is where the actual AI work happens.
        """

        if step.status not in ['assigned', 'pending']:
            return {'success': False, 'error': f'Step not ready: {step.status}'}

        # Mark as in progress
        step.status = 'in_progress'
        step.started_at = timezone.now()
        if input_data:
            step.input_data.update(input_data)
        step.save()

        workflow = step.workflow

        # Broadcast step started
        self._broadcast_workflow_update(workflow, 'step_started', {
            'step_id': str(step.id),
            'step_name': step.step_name,
            'agent_name': step.assigned_agent.name if step.assigned_agent else 'Unknown',
        })

        # Execute the actual work based on action type
        try:
            result = self._perform_step_action(step)

            # Mark as completed or send for review
            step.output_data = result
            step.status = 'completed'
            step.completed_at = timezone.now()
            step.save()

            # Update workflow progress
            self._update_workflow_progress(workflow)

            # Check for next steps
            self._advance_workflow(workflow)

            # Broadcast step completed
            self._broadcast_workflow_update(workflow, 'step_completed', {
                'step_id': str(step.id),
                'step_name': step.step_name,
                'result_preview': str(result)[:200] if result else None,
            })

            return {'success': True, 'result': result}

        except Exception as e:
            logger.error(f"Error executing step {step.id}: {e}")
            step.status = 'failed'
            step.output_data = {'error': str(e)}
            step.save()

            self._broadcast_workflow_update(workflow, 'step_failed', {
                'step_id': str(step.id),
                'step_name': step.step_name,
                'error': str(e),
            })

            return {'success': False, 'error': str(e)}

    def _perform_step_action(self, step) -> Dict:
        """
        Perform the actual action for a step.
        This integrates with the AI agents and tools.
        """
        action = step.action
        tools = step.input_data.get('tools', [])
        workflow = step.workflow

        # Get context from previous steps
        context = self._gather_step_context(step)

        # Build result based on action type
        result = {
            'action': action,
            'agent': step.assigned_agent.name if step.assigned_agent else 'System',
            'completed_at': timezone.now().isoformat(),
            'context_used': list(context.keys()),
        }

        # Simulate different action types (in production, these would call real AI)
        if action in ['research', 'research_brand', 'research_topic', 'research_audience']:
            result['findings'] = [
                f"Research finding 1 for {workflow.name}",
                f"Research finding 2 for {workflow.name}",
                f"Key insight: Market trends show opportunity",
            ]
            result['sources'] = ['web_search', 'spider_data']

        elif action in ['develop_strategy', 'plan_content', 'develop_brand_strategy', 'plan_campaign', 'plan']:
            result['strategy'] = {
                'direction': f"Creative direction for {workflow.name}",
                'key_points': ['Point 1', 'Point 2', 'Point 3'],
                'recommendations': ['Use bold colors', 'Modern typography'],
            }

        elif action in ['create_design', 'design_logo', 'create_colors', 'create_visuals', 'create']:
            result['designs'] = {
                'primary': f"Design created for {workflow.name}",
                'variations': 3,
                'style': 'modern',
            }
            # In production: would call stability_ai here

        elif action in ['write_content', 'write_brand_copy', 'write_copy']:
            result['content'] = {
                'headline': f"Headline for {workflow.name}",
                'body': "Professional content created by AI writer agent.",
                'word_count': 500,
            }

        elif action in ['review', 'review_design', 'review_content', 'review_brand', 'review_campaign']:
            result['review'] = {
                'score': 8.5,
                'feedback': ['Great work', 'Minor refinements suggested'],
                'approved': True,
            }

        elif action in ['optimize', 'optimize_design', 'polish_content', 'refine_brand', 'optimize_campaign']:
            result['optimizations'] = {
                'changes_made': ['Enhanced contrast', 'Improved readability'],
                'final_score': 9.2,
            }

        return result

    def _gather_step_context(self, step) -> Dict:
        """Gather context from previous completed steps."""
        context = {}

        # Get output from dependency steps
        for dep in step.depends_on.all():
            if dep.status == 'completed' and dep.output_data:
                context[dep.action] = dep.output_data

        # Also include workflow-level context
        context['workflow_name'] = step.workflow.name
        context['workflow_description'] = step.workflow.description

        return context

    def _update_workflow_progress(self, workflow):
        """Update workflow progress percentage."""
        total = workflow.step_executions.count()
        completed = workflow.step_executions.filter(status='completed').count()

        if total > 0:
            workflow.progress = int((completed / total) * 100)
            workflow.current_step = completed
            workflow.save()

    def _advance_workflow(self, workflow):
        """Check if workflow can advance to next steps."""
        # Get newly ready steps
        ready_steps = self._get_ready_steps(workflow)

        for step in ready_steps:
            if step.status == 'pending':
                self._assign_step_to_agent(workflow, step)

        # Check if workflow is complete
        all_complete = not workflow.step_executions.exclude(
            status__in=['completed', 'skipped']
        ).exists()

        if all_complete:
            self._complete_workflow(workflow)

    def _complete_workflow(self, workflow):
        """Mark workflow as complete and gather results."""
        from core.models_unified_system import AgentMessage

        workflow.status = 'completed'
        workflow.completed_at = timezone.now()

        # Gather all results
        results = {}
        for step in workflow.step_executions.filter(status='completed'):
            results[step.action] = step.output_data

        workflow.results = results
        workflow.progress = 100
        workflow.save()

        # Send completion message to team lead
        if workflow.team.lead_agent:
            AgentMessage.objects.create(
                sender_agent=workflow.team.lead_agent,
                receiver_agent=workflow.team.lead_agent,
                message_type='notification',
                subject=f'Workflow Complete: {workflow.name}',
                content=f"The workflow '{workflow.name}' has been completed successfully!",
                task_context={
                    'workflow_id': str(workflow.id),
                    'results_summary': list(results.keys()),
                },
                priority=9,
            )

        # Broadcast completion
        self._broadcast_workflow_update(workflow, 'workflow_completed', {
            'workflow_id': str(workflow.id),
            'workflow_name': workflow.name,
            'total_steps': workflow.step_executions.count(),
            'results_count': len(results),
        })

        logger.info(f"Workflow {workflow.id} completed successfully!")

    def _broadcast_workflow_update(self, workflow, event_type: str, data: Dict):
        """Broadcast workflow updates via WebSocket."""
        if not self.channel_layer:
            return

        try:
            message = {
                'type': 'workflow_update',
                'event': event_type,
                'workflow_id': str(workflow.id),
                'workflow_name': workflow.name,
                'team_id': str(workflow.team.id),
                'progress': workflow.progress,
                'status': workflow.status,
                'data': data,
                'timestamp': timezone.now().isoformat(),
            }

            # Broadcast to team channel
            async_to_sync(self.channel_layer.group_send)(
                f'team_{workflow.team.id}',
                message
            )

            # Also broadcast to general workflow channel
            async_to_sync(self.channel_layer.group_send)(
                'workflow_updates',
                message
            )

        except Exception as e:
            logger.error(f"Error broadcasting workflow update: {e}")

    def get_workflow_status(self, workflow) -> Dict:
        """Get detailed workflow status."""
        steps_data = []
        for step in workflow.step_executions.order_by('step_number'):
            steps_data.append({
                'id': str(step.id),
                'step_number': step.step_number,
                'name': step.step_name,
                'action': step.action,
                'status': step.status,
                'assigned_agent': step.assigned_agent.name if step.assigned_agent else None,
                'started_at': step.started_at.isoformat() if step.started_at else None,
                'completed_at': step.completed_at.isoformat() if step.completed_at else None,
                'has_output': bool(step.output_data),
            })

        return {
            'workflow_id': str(workflow.id),
            'name': workflow.name,
            'status': workflow.status,
            'progress': workflow.progress,
            'current_step': workflow.current_step,
            'total_steps': len(steps_data),
            'steps': steps_data,
            'started_at': workflow.started_at.isoformat() if workflow.started_at else None,
            'completed_at': workflow.completed_at.isoformat() if workflow.completed_at else None,
            'team_name': workflow.team.name,
        }


# Global engine instance
workflow_engine = TeamWorkflowEngine()
