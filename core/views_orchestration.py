"""
Orchestration API Endpoints
===========================

Session 764: REST API for multi-agent workflow execution.

Endpoints:
- GET  /api/orchestration/workflows/              - List workflows
- POST /api/orchestration/workflows/{id}/execute/ - Execute workflow
- GET  /api/orchestration/executions/             - List executions
- GET  /api/orchestration/executions/{id}/        - Get execution status
- POST /api/orchestration/executions/{id}/resume/ - Resume paused execution
- POST /api/orchestration/executions/{id}/cancel/ - Cancel execution
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
import json

logger = logging.getLogger(__name__)


class OrchestrationWorkflowsView(View):
    """List and manage orchestration workflows."""

    @method_decorator(login_required)
    def get(self, request):
        """List all workflows available for orchestration."""
        from core.models_unified_system import CustomWorkflow
        from django.contrib.auth import get_user_model
        from django.db.models import Q

        try:
            workflows = CustomWorkflow.objects.filter(
                status='active'
            ).select_related('created_by').order_by('-updated_at')

            # Filter by user's workflows OR system templates (created by 'system' user)
            # Staff can see all workflows
            if not request.user.is_staff:
                User = get_user_model()
                system_user = User.objects.filter(username='system').first()
                workflows = workflows.filter(
                    Q(created_by=request.user) | Q(created_by=system_user)
                )

            data = []
            for wf in workflows[:50]:  # Limit to 50 workflows
                data.append({
                    'id': str(wf.id),
                    'name': wf.name,
                    'description': wf.description or '',
                    'execution_mode': wf.execution_mode,
                    'max_retries': wf.max_retries,
                    'timeout_seconds': wf.timeout_seconds,
                    'cost_budget': str(wf.cost_budget) if wf.cost_budget else None,
                    'step_count': wf.steps.count(),
                    'created_at': wf.created_at.isoformat() if wf.created_at else None,
                    'updated_at': wf.updated_at.isoformat() if wf.updated_at else None,
                })

            return JsonResponse({
                'success': True,
                'workflows': data,
                'count': len(data),
            })

        except Exception as e:
            logger.error(f"Error listing workflows: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e),
            }, status=500)


class OrchestrationWorkflowDetailView(View):
    """Get detailed workflow information including all steps."""

    @method_decorator(login_required)
    def get(self, request, workflow_id):
        """Get workflow with all steps, agents, and input parameters."""
        from core.models_unified_system import CustomWorkflow
        from django.contrib.auth import get_user_model
        import re

        try:
            workflow = CustomWorkflow.objects.select_related('created_by').get(
                id=workflow_id, status='active'
            )

            # Check permissions - allow access to system templates
            User = get_user_model()
            system_user = User.objects.filter(username='system').first()
            if not request.user.is_staff:
                if workflow.created_by != request.user and workflow.created_by != system_user:
                    return JsonResponse({
                        'success': False,
                        'error': 'Permission denied',
                    }, status=403)

            # Get all steps with full details
            steps = []
            all_input_params = set()

            for step in workflow.steps.all().order_by('order'):
                config = step.config or {}
                prompt_template = config.get('prompt_template', '')

                # Extract input parameters from prompt template (e.g., {topic}, {style})
                # Exclude step references like {step_1}, {step_2}
                params = re.findall(r'\{(\w+)\}', prompt_template)
                step_params = [p for p in params if not p.startswith('step_')]
                all_input_params.update(step_params)

                steps.append({
                    'id': str(step.id),
                    'order': step.order,
                    'name': step.name,
                    'description': step.description or '',
                    'agent': step.agent,
                    'prompt_template': prompt_template,
                    'input_params': step_params,
                    'config': config,
                    'timeout_seconds': step.timeout_seconds,
                    'requires_approval': step.requires_approval,
                    'approval_config': step.approval_config,
                    'depends_on_steps': step.depends_on_steps or [],
                    'rollback_step': step.rollback_step,
                    'cost_limit': str(step.cost_limit) if step.cost_limit else None,
                    'retry_count': step.retry_count,
                    'is_required': step.is_required,
                })

            return JsonResponse({
                'success': True,
                'workflow': {
                    'id': str(workflow.id),
                    'name': workflow.name,
                    'description': workflow.description or '',
                    'execution_mode': workflow.execution_mode,
                    'max_retries': workflow.max_retries,
                    'timeout_seconds': workflow.timeout_seconds,
                    'cost_budget': str(workflow.cost_budget) if workflow.cost_budget else None,
                    'require_approval_on_error': workflow.require_approval_on_error,
                    'created_by': workflow.created_by.username if workflow.created_by else None,
                    'is_template': workflow.created_by == system_user if system_user else False,
                    'created_at': workflow.created_at.isoformat() if workflow.created_at else None,
                    'updated_at': workflow.updated_at.isoformat() if workflow.updated_at else None,
                },
                'steps': steps,
                'input_parameters': list(all_input_params),
            })

        except CustomWorkflow.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Workflow not found',
            }, status=404)

        except Exception as e:
            logger.error(f"Error getting workflow details: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e),
            }, status=500)


class OrchestrationAgentsView(View):
    """Get available agents for workflow configuration."""

    @method_decorator(login_required)
    def get(self, request):
        """List all agents available for orchestration steps."""
        from core.agent_router import AgentRouter

        try:
            router = AgentRouter()
            agents = []

            # Session 768: Use get_available_agents() method
            available_agents = router.get_available_agents()

            # Also get agent categories from AGENT_MAP if available
            agent_categories = {}
            if hasattr(router, 'AGENT_MAP'):
                for agent_name, agent_class in router.AGENT_MAP.items():
                    # Try to extract category from agent class
                    category = 'general'
                    if hasattr(agent_class, 'category'):
                        category = agent_class.category
                    elif 'Stock' in agent_name or 'Market' in agent_name:
                        category = 'stocks'
                    elif 'Image' in agent_name or 'Video' in agent_name or 'Audio' in agent_name:
                        category = 'creative'
                    elif 'Content' in agent_name or 'Blog' in agent_name or 'Writer' in agent_name:
                        category = 'content'
                    elif 'Research' in agent_name or 'Analysis' in agent_name:
                        category = 'research'
                    elif 'Code' in agent_name or 'Dev' in agent_name:
                        category = 'development'
                    elif 'CTO' in agent_name or 'COO' in agent_name or 'Director' in agent_name:
                        category = 'executive'
                    elif 'Blockchain' in agent_name or 'Smart' in agent_name:
                        category = 'blockchain'
                    elif 'Podcast' in agent_name or 'Debate' in agent_name or 'Moderator' in agent_name:
                        category = 'podcast'
                    agent_categories[agent_name] = category

            for agent_info in available_agents:
                agent_name = agent_info.get('name', '')
                description = agent_info.get('description', '')
                # Truncate description to first sentence
                if description:
                    first_sentence = description.split('\n')[0][:200]
                    description = first_sentence

                agents.append({
                    'key': agent_name,
                    'name': agent_name,
                    'description': description,
                    'category': agent_categories.get(agent_name, 'general'),
                    'capabilities': [],
                })

            # Sort by category then name
            agents.sort(key=lambda x: (x['category'], x['name']))

            return JsonResponse({
                'success': True,
                'agents': agents,
                'count': len(agents),
            })

        except Exception as e:
            logger.error(f"Error listing agents: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e),
            }, status=500)


class OrchestrationCreateWorkflowView(View):
    """Create or update a workflow."""

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def post(self, request):
        """Create a new workflow with steps."""
        from core.models_unified_system import CustomWorkflow, CustomWorkflowStep

        try:
            body = json.loads(request.body) if request.body else {}

            name = body.get('name')
            if not name:
                return JsonResponse({
                    'success': False,
                    'error': 'Workflow name is required',
                }, status=400)

            # Create workflow
            workflow = CustomWorkflow.objects.create(
                name=name,
                description=body.get('description', ''),
                execution_mode=body.get('execution_mode', 'sequential'),
                max_retries=body.get('max_retries', 3),
                timeout_seconds=body.get('timeout_seconds', 3600),
                cost_budget=body.get('cost_budget'),
                require_approval_on_error=body.get('require_approval_on_error', True),
                created_by=request.user,
                status='active',
            )

            # Create steps
            steps_data = body.get('steps', [])
            for idx, step_data in enumerate(steps_data):
                CustomWorkflowStep.objects.create(
                    workflow=workflow,
                    order=step_data.get('order', idx + 1),
                    name=step_data.get('name', f'Step {idx + 1}'),
                    description=step_data.get('description', ''),
                    agent=step_data.get('agent', 'ThinkingAgent'),
                    config={
                        'prompt_template': step_data.get('prompt_template', ''),
                        **step_data.get('config', {}),
                    },
                    timeout_seconds=step_data.get('timeout_seconds', 300),
                    requires_approval=step_data.get('requires_approval', False),
                    approval_config=step_data.get('approval_config', {}),
                    depends_on_steps=step_data.get('depends_on_steps', []),
                    rollback_step=step_data.get('rollback_step'),
                    cost_limit=step_data.get('cost_limit'),
                    retry_count=step_data.get('retry_count', 3),
                    is_required=step_data.get('is_required', True),
                )

            return JsonResponse({
                'success': True,
                'workflow_id': str(workflow.id),
                'message': f'Workflow "{name}" created with {len(steps_data)} steps',
            })

        except Exception as e:
            logger.error(f"Error creating workflow: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e),
            }, status=500)


class OrchestrationExecuteView(View):
    """Execute a workflow."""

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def post(self, request, workflow_id):
        """Execute a workflow with optional input parameters."""
        from core.models_unified_system import CustomWorkflow
        from core.services.orchestration_engine import orchestration_engine

        try:
            # Parse request body
            try:
                body = json.loads(request.body) if request.body else {}
            except json.JSONDecodeError:
                body = {}

            input_data = body.get('input', {})
            async_mode = body.get('async', True)

            # Get workflow
            workflow = CustomWorkflow.objects.get(id=workflow_id, status='active')

            # Check permissions
            if not request.user.is_staff and workflow.created_by != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'Permission denied',
                }, status=403)

            # Execute workflow
            execution = orchestration_engine.execute_workflow(
                workflow=workflow,
                user=request.user,
                input_data=input_data,
                async_mode=async_mode,
            )

            return JsonResponse({
                'success': True,
                'execution_id': str(execution.id),
                'status': execution.status,
                'message': f'Workflow execution started' if async_mode else f'Workflow completed with status: {execution.status}',
            })

        except CustomWorkflow.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Workflow not found',
            }, status=404)

        except Exception as e:
            logger.error(f"Error executing workflow: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e),
            }, status=500)


class OrchestrationExecutionsView(View):
    """List workflow executions."""

    @method_decorator(login_required)
    def get(self, request):
        """List all executions for the current user."""
        from core.models_orchestration import OrchestrationExecution

        try:
            # Get query parameters
            status_filter = request.GET.get('status')
            workflow_id = request.GET.get('workflow_id')
            limit = min(int(request.GET.get('limit', 50)), 100)

            # Build query
            executions = OrchestrationExecution.objects.filter(
                triggered_by=request.user
            ).select_related('workflow').order_by('-started_at')

            if status_filter:
                executions = executions.filter(status=status_filter)

            if workflow_id:
                executions = executions.filter(workflow_id=workflow_id)

            # Staff can see all
            if request.user.is_staff and request.GET.get('all') == 'true':
                executions = OrchestrationExecution.objects.all().select_related(
                    'workflow', 'triggered_by'
                ).order_by('-started_at')

            data = []
            for ex in executions[:limit]:
                # Session 769: Calculate combined cost (LLM + external)
                llm_cost = float(ex.total_cost) if ex.total_cost else 0
                external_cost = float(ex.total_external_cost) if ex.total_external_cost else 0
                combined_cost = llm_cost + external_cost

                data.append({
                    'id': str(ex.id),
                    'workflow_id': str(ex.workflow_id),
                    'workflow_name': ex.workflow.name if ex.workflow else 'Unknown',
                    'status': ex.status,
                    'current_step': ex.current_step,
                    'total_steps': ex.total_steps,
                    'total_cost': str(ex.total_cost) if ex.total_cost else '0.0000',
                    'total_tokens': ex.total_tokens,
                    # Session 769: Include external costs
                    'total_external_cost': str(ex.total_external_cost) if ex.total_external_cost else '0.0000',
                    'total_combined_cost': f'{combined_cost:.4f}',
                    'started_at': ex.started_at.isoformat() if ex.started_at else None,
                    'completed_at': ex.completed_at.isoformat() if ex.completed_at else None,
                    'error_message': ex.error_message,
                    'triggered_by': ex.triggered_by.username if ex.triggered_by else None,
                })

            return JsonResponse({
                'success': True,
                'executions': data,
                'count': len(data),
            })

        except Exception as e:
            logger.error(f"Error listing executions: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e),
            }, status=500)


class OrchestrationExecutionDetailView(View):
    """Get execution details."""

    @method_decorator(login_required)
    def get(self, request, execution_id):
        """Get detailed status of an execution."""
        from core.models_orchestration import OrchestrationExecution

        try:
            execution = OrchestrationExecution.objects.select_related(
                'workflow', 'triggered_by'
            ).get(id=execution_id)

            # Check permissions
            if not request.user.is_staff and execution.triggered_by != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'Permission denied',
                }, status=403)

            # Get step executions
            step_data = []
            for step_exec in execution.step_executions.all().order_by('step_number'):
                # Session 769: Get tokens from model field or fallback to output_data
                tokens = step_exec.tokens_used
                if not tokens and step_exec.output_data:
                    tokens = step_exec.output_data.get('tokens_used') or 0

                # Session 769: Calculate step combined cost
                step_llm_cost = float(step_exec.cost) if step_exec.cost else 0
                step_external_cost = float(step_exec.external_cost) if step_exec.external_cost else 0
                step_combined = step_llm_cost + step_external_cost

                step_data.append({
                    'step_number': step_exec.step_number,
                    'agent_name': step_exec.agent_name,
                    'status': step_exec.status,
                    'started_at': step_exec.started_at.isoformat() if step_exec.started_at else None,
                    'completed_at': step_exec.completed_at.isoformat() if step_exec.completed_at else None,
                    'cost': str(step_exec.cost) if step_exec.cost else '0.0000',
                    'tokens': tokens,
                    # Session 769: Include external costs per step
                    'external_cost': str(step_exec.external_cost) if step_exec.external_cost else '0.0000',
                    'external_cost_breakdown': step_exec.external_cost_breakdown or {},
                    'combined_cost': f'{step_combined:.4f}',
                    'retry_count': step_exec.retry_count,
                    'error_message': step_exec.error_message,
                    'output_preview': self._extract_output_preview(step_exec.output_data),
                })

            # Get pending approval gates
            approval_gates = []
            for gate in execution.approval_gates.filter(status='pending'):
                approval_gates.append({
                    'id': str(gate.id),
                    'step_number': gate.step_execution.step_number if gate.step_execution else None,
                    'status': gate.status,
                    'created_at': gate.created_at.isoformat() if gate.created_at else None,
                    'expires_at': gate.expires_at.isoformat() if gate.expires_at else None,
                })

            # Session 769: Get total_tokens from model field, final_output, or calculate from steps
            total_tokens = execution.total_tokens
            if not total_tokens and execution.final_output:
                total_tokens = execution.final_output.get('total_tokens') or 0
            if not total_tokens:
                # Calculate from step data as last fallback
                for step in step_data:
                    total_tokens += step.get('tokens') or 0

            # Session 769: Calculate combined cost
            llm_cost = float(execution.total_cost) if execution.total_cost else 0
            external_cost = float(execution.total_external_cost) if execution.total_external_cost else 0
            combined_cost = llm_cost + external_cost

            # Session 770: Check for linked podcast episode and fetch TTS cost
            podcast_info = None
            try:
                # Look for episode_id in step outputs (PodcastCoordinatorAgent returns it)
                episode_id = None
                for step_exec in execution.step_executions.all():
                    if step_exec.output_data:
                        # Check in output_data.data.episode_id
                        data_section = step_exec.output_data.get('data', {})
                        if isinstance(data_section, dict):
                            episode_id = data_section.get('episode_id')
                            if episode_id:
                                break

                if episode_id:
                    from core.models_podcast_studio import PodcastEpisode
                    try:
                        episode = PodcastEpisode.objects.get(id=episode_id)
                        podcast_info = {
                            'episode_id': str(episode.id),
                            'title': episode.title,
                            'topic': episode.topic,
                            'status': episode.status,
                            'tts_cost': str(episode.tts_cost) if episode.tts_cost else '0.0000',
                            'tts_cost_breakdown': episode.tts_cost_breakdown or {},
                            'audio_url': episode.audio_url,
                            'audio_duration_seconds': episode.audio_duration_seconds,
                        }
                    except PodcastEpisode.DoesNotExist:
                        pass
            except Exception as e:
                logger.warning(f"Error fetching podcast info: {e}")

            return JsonResponse({
                'success': True,
                'execution': {
                    'id': str(execution.id),
                    'workflow_id': str(execution.workflow_id),
                    'workflow_name': execution.workflow.name if execution.workflow else 'Unknown',
                    'status': execution.status,
                    'current_step': execution.current_step,
                    'total_steps': execution.total_steps,
                    'total_cost': str(execution.total_cost) if execution.total_cost else '0.0000',
                    'total_tokens': total_tokens,
                    # Session 769: Include external cost breakdown
                    'total_external_cost': str(execution.total_external_cost) if execution.total_external_cost else '0.0000',
                    'external_cost_breakdown': execution.external_cost_breakdown or {},
                    'total_combined_cost': f'{combined_cost:.4f}',
                    'input_data': execution.input_data,
                    'final_output': execution.final_output,
                    'error_message': execution.error_message,
                    'started_at': execution.started_at.isoformat() if execution.started_at else None,
                    'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                    'triggered_by': execution.triggered_by.username if execution.triggered_by else None,
                },
                'steps': step_data,
                'approval_gates': approval_gates,
                # Session 770: Include podcast info if this is a podcast workflow
                'podcast_info': podcast_info,
            })

        except OrchestrationExecution.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Execution not found',
            }, status=404)

        except Exception as e:
            logger.error(f"Error getting execution details: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e),
            }, status=500)

    def _extract_output_preview(self, output_data: dict) -> str | None:
        """
        Session 767: Extract meaningful preview text from step output data.

        Looks for common keys that contain human-readable content rather than
        returning raw JSON string representation.
        """
        if not output_data:
            return None

        # Priority order for extracting preview text
        preview_keys = [
            # ContentWriterAgent outputs
            ('data', 'content', 'intro'),
            ('data', 'content', 'summary'),
            ('data', 'content', 'conclusion'),
            # Research outputs
            ('data', 'query'),
            ('data', 'synthesis'),
            ('data', 'summary'),
            # Generic outputs
            ('message',),
            ('result',),
            ('summary',),
            ('content',),
        ]

        for key_path in preview_keys:
            value = output_data
            try:
                for key in key_path:
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        value = None
                        break
                if value and isinstance(value, str):
                    # Return first 200 chars with ellipsis if truncated
                    if len(value) > 200:
                        return value[:197] + "..."
                    return value
            except (KeyError, TypeError):
                continue

        # Fallback: Try to get any string value from data dict
        if isinstance(output_data.get('data'), dict):
            data = output_data['data']
            # Check for tags, topics, or other list-based content
            if data.get('tags'):
                tags = data['tags'][:5] if isinstance(data['tags'], list) else []
                return f"Tags: {', '.join(str(t) for t in tags)}"
            if data.get('topics_detected'):
                topics = data['topics_detected'][:5] if isinstance(data['topics_detected'], list) else []
                return f"Topics: {', '.join(str(t) for t in topics)}"

        # Last resort: Return message if exists
        if output_data.get('message'):
            msg = output_data['message']
            if len(msg) > 200:
                return msg[:197] + "..."
            return msg

        return "Output generated (see details for full data)"


class OrchestrationResumeView(View):
    """Resume a paused or waiting execution."""

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def post(self, request, execution_id):
        """Resume execution from current checkpoint."""
        from core.models_orchestration import OrchestrationExecution
        from core.services.orchestration_engine import orchestration_engine

        try:
            # Parse request body
            try:
                body = json.loads(request.body) if request.body else {}
            except json.JSONDecodeError:
                body = {}

            modifications = body.get('modifications', {})

            # Get execution
            execution = OrchestrationExecution.objects.get(id=execution_id)

            # Check permissions
            if not request.user.is_staff and execution.triggered_by != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'Permission denied',
                }, status=403)

            # Check if resumable
            if execution.status not in ['waiting_approval', 'failed', 'paused']:
                return JsonResponse({
                    'success': False,
                    'error': f'Cannot resume execution with status: {execution.status}',
                }, status=400)

            # Resume execution
            orchestration_engine.resume_execution(
                execution_id=str(execution_id),
                modifications=modifications
            )

            # Refresh execution
            execution.refresh_from_db()

            return JsonResponse({
                'success': True,
                'execution_id': str(execution.id),
                'status': execution.status,
                'message': 'Execution resumed',
            })

        except OrchestrationExecution.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Execution not found',
            }, status=404)

        except Exception as e:
            logger.error(f"Error resuming execution: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e),
            }, status=500)


class OrchestrationCancelView(View):
    """Cancel a running or waiting execution."""

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def post(self, request, execution_id):
        """Cancel the execution."""
        from core.models_orchestration import OrchestrationExecution
        from core.services.orchestration_engine import orchestration_engine

        try:
            # Parse request body
            try:
                body = json.loads(request.body) if request.body else {}
            except json.JSONDecodeError:
                body = {}

            reason = body.get('reason', 'Cancelled by user')

            # Get execution
            execution = OrchestrationExecution.objects.get(id=execution_id)

            # Check permissions
            if not request.user.is_staff and execution.triggered_by != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'Permission denied',
                }, status=403)

            # Check if cancellable
            if execution.status in ['completed', 'failed', 'cancelled']:
                return JsonResponse({
                    'success': False,
                    'error': f'Cannot cancel execution with status: {execution.status}',
                }, status=400)

            # Cancel execution
            orchestration_engine.cancel_execution(
                execution_id=str(execution_id),
                reason=reason
            )

            # Refresh execution
            execution.refresh_from_db()

            return JsonResponse({
                'success': True,
                'execution_id': str(execution.id),
                'status': execution.status,
                'message': 'Execution cancelled',
            })

        except OrchestrationExecution.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Execution not found',
            }, status=404)

        except Exception as e:
            logger.error(f"Error cancelling execution: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e),
            }, status=500)


class OrchestrationStepIntelligenceView(View):
    """
    Session 765: Fetch intelligence data for an orchestration step.

    Returns the underlying AgentExecution data, memories created,
    learning patterns applied, tool calls, and injected context.
    """

    @method_decorator(login_required)
    def get(self, request, execution_id, step_number):
        """Get intelligence data for a specific step."""
        from core.models_orchestration import OrchestrationExecution, OrchestrationStepExecution
        from core.models_unified_system import AgentExecution, AgentMemory, Agent

        try:
            # Get the orchestration execution
            execution = OrchestrationExecution.objects.get(id=execution_id)

            # Check permissions
            if not request.user.is_staff and execution.triggered_by != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'Permission denied',
                }, status=403)

            # Get the step execution (use latest if there are retries with same step_number)
            step_exec = OrchestrationStepExecution.objects.filter(
                orchestration=execution,
                step_number=step_number
            ).order_by('-id').first()

            if not step_exec:
                return JsonResponse({
                    'success': False,
                    'error': f'Step {step_number} not found',
                }, status=404)

            # Session 767: Get full context from workflow step config (stored data may be truncated)
            full_context = {}
            if step_exec.workflow_step:
                workflow_step = step_exec.workflow_step
                config = workflow_step.config or {}
                if 'dream_context' in config:
                    full_context['dream_context'] = config['dream_context']
                if 'hivemind_context' in config:
                    full_context['hivemind_context'] = config['hivemind_context']

            # Session 769: Get tokens from model field or fallback to output_data
            step_tokens = step_exec.tokens_used
            if not step_tokens and step_exec.output_data:
                step_tokens = step_exec.output_data.get('tokens_used') or 0

            # Build intelligence response
            intelligence = {
                'step_info': {
                    'step_number': step_exec.step_number,
                    'agent_name': step_exec.agent_name,
                    'status': step_exec.status,
                    'cost': str(step_exec.cost) if step_exec.cost else '0.0000',
                    'tokens': step_tokens,
                    'duration_seconds': step_exec.duration_seconds,
                    'started_at': step_exec.started_at.isoformat() if step_exec.started_at else None,
                    'completed_at': step_exec.completed_at.isoformat() if step_exec.completed_at else None,
                    'input_data': step_exec.input_data,
                    'output_data': step_exec.output_data,
                    'error_message': step_exec.error_message,
                    'retry_count': step_exec.retry_count,
                    'full_context': full_context,  # Session 767: Full context from workflow step config
                },
                'agent_execution': None,
                'memories_created': [],
                'context_injected': {},
                'tool_calls': [],
            }

            # If we have an execution_id, fetch the underlying execution data
            if step_exec.execution_id:
                try:
                    agent_exec = AgentExecution.objects.get(id=step_exec.execution_id)

                    # Session 767: Get full task from input_data (task field is truncated to 500 chars)
                    # Session 881: Defensive check - input_data might be a list in some edge cases
                    input_data = agent_exec.input_data or {}
                    if not isinstance(input_data, dict):
                        input_data = {}
                    full_task = input_data.get('task') or agent_exec.task

                    intelligence['agent_execution'] = {
                        'id': str(agent_exec.id),
                        'task': full_task,
                        'status': agent_exec.status,
                        'execution_time_ms': agent_exec.execution_time_ms,
                        'tokens_used': agent_exec.tokens_used,
                        'cost': str(agent_exec.cost) if agent_exec.cost else '0.0000',
                        'output_data': agent_exec.output_data,
                        'error_message': agent_exec.error_message,
                        'created_at': agent_exec.created_at.isoformat() if agent_exec.created_at else None,
                    }

                    # Extract context that was injected
                    # Session 881: input_data already validated as dict above
                    context_injected = input_data.get('context_injected', {})
                    intelligence['context_injected'] = context_injected

                    # Extract tool calls from output_data
                    # Session 769: tool_calls are stored in step_exec.output_data (from orchestration),
                    # NOT in agent_exec.output_data (which doesn't include tool_calls)
                    step_output = step_exec.output_data or {}
                    tool_calls = step_output.get('tool_calls', [])
                    # Also check agent_exec as fallback
                    if not tool_calls:
                        agent_output = agent_exec.output_data or {}
                        tool_calls = agent_output.get('tool_calls', [])
                        # Also check inside data for legacy format
                        if not tool_calls and 'data' in agent_output and isinstance(agent_output['data'], dict):
                            tool_calls = agent_output['data'].get('tool_calls', [])
                    if tool_calls:
                        intelligence['tool_calls'] = tool_calls

                    # Find memories created by this execution
                    # Session 769: BaseAgent creates memories with source_type='agent_execution'
                    # and source_id=agent_name. Since source_id matches ALL executions of this agent,
                    # we MUST filter by time window to get memories from THIS specific execution.
                    try:
                        agent_record = Agent.objects.filter(name=step_exec.agent_name).first()
                        if agent_record and step_exec.started_at and step_exec.completed_at:
                            from datetime import timedelta
                            # Primary: Find memories created during this step's execution window
                            # Session 810: Defer embedding fields to reduce egress costs
                            memories = AgentMemory.objects.defer('embedding').filter(
                                agent=agent_record,
                                created_at__gte=step_exec.started_at - timedelta(seconds=10),
                                created_at__lte=step_exec.completed_at + timedelta(seconds=10)
                            ).order_by('-created_at')[:10]

                            for mem in memories:
                                intelligence['memories_created'].append({
                                    'id': str(mem.id),
                                    'title': mem.title,
                                    'content': mem.content[:500] if mem.content else '',
                                    'memory_type': mem.memory_type,
                                    'valence': mem.valence,
                                    'importance_score': mem.importance_score,
                                    'created_at': mem.created_at.isoformat() if mem.created_at else None,
                                })
                    except Exception as mem_err:
                        logger.warning(f"Error fetching memories: {mem_err}")

                except AgentExecution.DoesNotExist:
                    logger.warning(f"AgentExecution {step_exec.execution_id} not found")

            return JsonResponse({
                'success': True,
                'intelligence': intelligence,
            })

        except OrchestrationExecution.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Execution not found',
            }, status=404)

        except OrchestrationStepExecution.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Step {step_number} not found',
            }, status=404)

        except Exception as e:
            logger.error(f"Error fetching step intelligence: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e),
            }, status=500)


@method_decorator([csrf_exempt, login_required], name='dispatch')
class ActiveWorkView(View):
    """
    Session 1000C: Combined "Active Work" view for Command Center NowHub.

    Returns active initiatives, recent agent executions, and running
    orchestration workflows in a single lightweight response.
    """

    def get(self, request):
        try:
            from core.models_document_registry import Initiative
            from core.models import AgentExecution
            from django.utils.timezone import now
            from datetime import timedelta
            from django.db.models import Count

            cutoff = now() - timedelta(hours=24)

            # Active initiatives summary
            active_initiatives = Initiative.objects.filter(status='ACTIVE')
            initiative_count = active_initiatives.count()
            by_stage = dict(
                active_initiatives.values_list('current_stage')
                .annotate(c=Count('id'))
                .values_list('current_stage', 'c')
            )

            # Top 5 most recent active initiatives
            # completion_percentage is a @property, not a DB field — compute in Python
            top_initiatives = []
            for init in active_initiatives.order_by('-updated_at')[:5]:
                top_initiatives.append({
                    'id': str(init.id),
                    'name': (init.name or '')[:80],
                    'current_stage': init.current_stage,
                    'completion_percentage': init.completion_percentage,
                })

            # Agent executions in last 24h
            recent_execs = AgentExecution.objects.filter(created_at__gte=cutoff)
            exec_total = recent_execs.count()
            exec_completed = recent_execs.filter(status='completed').count()
            exec_failed = recent_execs.filter(status='failed').count()

            # Top 5 most active agents in last 24h
            top_agents = list(
                recent_execs.values('agent__name')
                .annotate(c=Count('id'))
                .order_by('-c')[:5]
            )

            # Running orchestration executions (original Active Work source)
            from core.models_orchestration import OrchestrationExecution
            running_workflows = OrchestrationExecution.objects.filter(
                status='running'
            ).count()

            return JsonResponse({
                'success': True,
                'initiatives': {
                    'active_count': initiative_count,
                    'by_stage': {str(k): v for k, v in by_stage.items()},
                    'recent': top_initiatives,
                },
                'agent_executions': {
                    'last_24h': exec_total,
                    'completed': exec_completed,
                    'failed': exec_failed,
                    'top_agents': [{'name': a['agent__name'] or 'Unknown', 'count': a['c']} for a in top_agents],
                },
                'workflows': {
                    'running': running_workflows,
                },
            })

        except Exception as e:
            logger.error(f"Error fetching active work: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e),
            }, status=500)


# URL patterns for this module
def get_urlpatterns():
    """Return URL patterns for orchestration API."""
    from django.urls import path

    return [
        path('workflows/', OrchestrationWorkflowsView.as_view(), name='orchestration-workflows'),
        path('workflows/create/', OrchestrationCreateWorkflowView.as_view(), name='orchestration-create-workflow'),
        path('workflows/<uuid:workflow_id>/', OrchestrationWorkflowDetailView.as_view(), name='orchestration-workflow-detail'),
        path('workflows/<uuid:workflow_id>/execute/', OrchestrationExecuteView.as_view(), name='orchestration-execute'),
        path('agents/', OrchestrationAgentsView.as_view(), name='orchestration-agents'),
        path('executions/', OrchestrationExecutionsView.as_view(), name='orchestration-executions'),
        path('executions/<uuid:execution_id>/', OrchestrationExecutionDetailView.as_view(), name='orchestration-execution-detail'),
        path('executions/<uuid:execution_id>/resume/', OrchestrationResumeView.as_view(), name='orchestration-resume'),
        path('executions/<uuid:execution_id>/cancel/', OrchestrationCancelView.as_view(), name='orchestration-cancel'),
        # Session 765: Step intelligence endpoint
        path('executions/<uuid:execution_id>/steps/<int:step_number>/intelligence/',
             OrchestrationStepIntelligenceView.as_view(), name='orchestration-step-intelligence'),
        # Session 1000C: Combined active work for Command Center NowHub
        path('active-work/', ActiveWorkView.as_view(), name='orchestration-active-work'),
    ]
