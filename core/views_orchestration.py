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
                is_active=True
            ).select_related('user').order_by('-updated_at')

            # Filter by user's workflows or public workflows
            if not request.user.is_staff:
                workflows = workflows.filter(user=request.user)

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
            workflow = CustomWorkflow.objects.get(id=workflow_id, is_active=True)

            # Check permissions
            if not request.user.is_staff and workflow.user != request.user:
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
                    'output_preview': str(step_exec.output_data)[:200] if step_exec.output_data else None,
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
    ]
