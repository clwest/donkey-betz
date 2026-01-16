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

        try:
            workflows = CustomWorkflow.objects.filter(
                status='active'
            ).select_related('created_by').order_by('-updated_at')

            # Filter by user's workflows or public workflows
            if not request.user.is_staff:
                workflows = workflows.filter(created_by=request.user)

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
                input_data=input_data,
                triggered_by=request.user,
                async_execution=async_mode,
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
                data.append({
                    'id': str(ex.id),
                    'workflow_id': str(ex.workflow_id),
                    'workflow_name': ex.workflow.name if ex.workflow else 'Unknown',
                    'status': ex.status,
                    'current_step': ex.current_step,
                    'total_steps': ex.total_steps,
                    'total_cost': str(ex.total_cost) if ex.total_cost else '0.0000',
                    'total_tokens': ex.total_tokens,
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
                step_data.append({
                    'step_number': step_exec.step_number,
                    'agent_name': step_exec.agent_name,
                    'status': step_exec.status,
                    'started_at': step_exec.started_at.isoformat() if step_exec.started_at else None,
                    'completed_at': step_exec.completed_at.isoformat() if step_exec.completed_at else None,
                    'cost': str(step_exec.cost) if step_exec.cost else '0.0000',
                    'tokens': step_exec.tokens_used,
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
                    'total_tokens': execution.total_tokens,
                    'input_data': execution.input_data,
                    'final_output': execution.final_output,
                    'error_message': execution.error_message,
                    'started_at': execution.started_at.isoformat() if execution.started_at else None,
                    'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                    'triggered_by': execution.triggered_by.username if execution.triggered_by else None,
                },
                'steps': step_data,
                'approval_gates': approval_gates,
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

            # Get the step execution
            step_exec = OrchestrationStepExecution.objects.get(
                orchestration=execution,
                step_number=step_number
            )

            # Build intelligence response
            intelligence = {
                'step_info': {
                    'step_number': step_exec.step_number,
                    'agent_name': step_exec.agent_name,
                    'status': step_exec.status,
                    'cost': str(step_exec.cost) if step_exec.cost else '0.0000',
                    'tokens': step_exec.tokens_used,
                    'duration_seconds': step_exec.duration_seconds,
                    'started_at': step_exec.started_at.isoformat() if step_exec.started_at else None,
                    'completed_at': step_exec.completed_at.isoformat() if step_exec.completed_at else None,
                    'input_data': step_exec.input_data,
                    'output_data': step_exec.output_data,
                    'error_message': step_exec.error_message,
                    'retry_count': step_exec.retry_count,
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
                    input_data = agent_exec.input_data or {}
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
                    context_injected = input_data.get('context_injected', {})
                    intelligence['context_injected'] = context_injected

                    # Extract tool calls from output_data
                    output_data = agent_exec.output_data or {}
                    if 'data' in output_data and isinstance(output_data['data'], dict):
                        tool_calls = output_data['data'].get('tool_calls', [])
                        if tool_calls:
                            intelligence['tool_calls'] = tool_calls

                    # Find memories created by this execution
                    # Look for memories with source_type='execution' and source_id matching
                    try:
                        agent_record = Agent.objects.filter(name=step_exec.agent_name).first()
                        if agent_record:
                            memories = AgentMemory.objects.filter(
                                agent=agent_record,
                                source_type__in=['execution', 'task'],
                                source_id=str(step_exec.execution_id)
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


# URL patterns for this module
def get_urlpatterns():
    """Return URL patterns for orchestration API."""
    from django.urls import path

    return [
        path('workflows/', OrchestrationWorkflowsView.as_view(), name='orchestration-workflows'),
        path('workflows/<uuid:workflow_id>/execute/', OrchestrationExecuteView.as_view(), name='orchestration-execute'),
        path('executions/', OrchestrationExecutionsView.as_view(), name='orchestration-executions'),
        path('executions/<uuid:execution_id>/', OrchestrationExecutionDetailView.as_view(), name='orchestration-execution-detail'),
        path('executions/<uuid:execution_id>/resume/', OrchestrationResumeView.as_view(), name='orchestration-resume'),
        path('executions/<uuid:execution_id>/cancel/', OrchestrationCancelView.as_view(), name='orchestration-cancel'),
        # Session 765: Step intelligence endpoint
        path('executions/<uuid:execution_id>/steps/<int:step_number>/intelligence/',
             OrchestrationStepIntelligenceView.as_view(), name='orchestration-step-intelligence'),
    ]
