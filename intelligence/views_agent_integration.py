"""
Agent Integration Views for Income Builder
Connects UI controls to real agent execution system
"""

import asyncio
import logging
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .agent_execution_pipeline import AgentExecutionPipeline
from .agent_instruction_parser import AgentInstructionParser
from .models import ActionPlan, ActionPlanExecution
from core.agents.registry import get_agent_registry

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def analyze_plan_for_automation(request):
    """
    Analyze an Income Builder plan to extract agent tasks
    """
    try:
        plan_content = request.data.get('plan_content', '')

        if not plan_content:
            return Response({
                'success': False,
                'error': 'Plan content is required'
            }, status=400)

        # Use the agent instruction parser to extract tasks
        parser = AgentInstructionParser()
        instructions = parser.parse_plan(plan_content)

        # Get execution order
        execution_groups = parser.get_execution_order()

        # Get available agents
        agent_registry = get_agent_registry()
        agent_stats = agent_registry.get_registry_stats()

        # Create analysis
        analysis = {
            'total_instructions': len(instructions),
            'execution_groups': len(execution_groups),
            'estimated_duration': len(instructions) * 30,  # 30 seconds per task estimate
            'agents_required': list(set([inst.agent_type for inst in instructions])),
            'active_agents_available': agent_stats.active_agents,
            'instructions_preview': [
                {
                    'agent_type': inst.agent_type,
                    'action': inst.action[:100] + '...' if len(inst.action) > 100 else inst.action,
                    'step_number': inst.step_number,
                    'week': inst.week
                }
                for inst in instructions[:5]  # Show first 5
            ],
            'automation_readiness': 'ready' if len(instructions) > 0 else 'needs_analysis'
        }

        return Response({
            'success': True,
            'analysis': analysis,
            'instructions_json': parser.to_json()
        })

    except Exception as e:
        logger.error(f"Error analyzing plan: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def execute_plan_automation(request):
    """
    Execute an Income Builder plan through the real agent system
    """
    try:
        plan_id = request.data.get('plan_id')
        plan_file = request.data.get('plan_file')
        auto_execute = request.data.get('auto_execute', True)

        if plan_id:
            # Use existing plan ID
            try:
                plan = ActionPlan.objects.get(id=plan_id)
                logger.info(f"Executing plan by ID: {plan.opportunity_title}")
            except ActionPlan.DoesNotExist:
                return Response({
                    'success': False,
                    'error': f'Plan with ID {plan_id} not found'
                }, status=404)

        elif plan_file:
            # Load plan from file
            import os
            try:
                # Handle both full paths and relative paths
                if plan_file.startswith('/'):
                    file_path = plan_file
                else:
                    file_path = os.path.join('/', plan_file)

                with open(file_path, 'r') as f:
                    plan_content = f.read()

                # Create a temporary plan object
                plan = type('TempPlan', (), {
                    'id': f"temp_{datetime.now().timestamp()}",
                    'opportunity_title': 'File-based Plan',
                    'generated_content': plan_content,
                    'status': 'ready'
                })()

                logger.info(f"Executing plan from file: {plan_file}")

            except FileNotFoundError:
                return Response({
                    'success': False,
                    'error': f'Plan file not found: {plan_file}'
                }, status=404)
        else:
            return Response({
                'success': False,
                'error': 'Either plan_id or plan_file is required'
            }, status=400)

        if auto_execute:
            # Execute the plan through our real agent system
            pipeline = AgentExecutionPipeline()

            # Run the execution in a new event loop (Django-safe)
            def run_execution():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(pipeline.execute_plan(str(plan.id)))
                    return result
                finally:
                    loop.close()

            execution_result = run_execution()

            if execution_result.get('success'):
                logger.info(f"Plan execution completed: {execution_result['executed']} tasks")

                return Response({
                    'success': True,
                    'execution_id': str(datetime.now().timestamp()),
                    'plan_id': str(plan.id),
                    'total_instructions': execution_result['total_instructions'],
                    'executed_tasks': execution_result['executed'],
                    'results': execution_result['results'][:3],  # Show first 3 results
                    'status': 'completed',
                    'message': f'Successfully executed {execution_result["executed"]} tasks through real agents!'
                })
            else:
                return Response({
                    'success': False,
                    'error': execution_result.get('error', 'Unknown execution error')
                }, status=500)

        else:
            # Just analyze without executing
            return Response({
                'success': True,
                'message': 'Plan analysis completed. Ready for execution.',
                'status': 'analyzed'
            })

    except Exception as e:
        logger.error(f"Error executing plan automation: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_available_agents(request):
    """
    Get list of available agents for UI selection
    """
    try:
        agent_registry = get_agent_registry()

        # Get all agents
        agents = agent_registry.list_agents()

        # Group by specialization
        agents_by_type = {}
        for agent in agents:
            specialization = agent.get('specialization', 'general')
            if specialization not in agents_by_type:
                agents_by_type[specialization] = []

            agents_by_type[specialization].append({
                'name': agent['name'],
                'display_name': agent.get('display_name', agent['name']),
                'capabilities': agent.get('capabilities', []),
                'is_active': agent.get('is_active', False),
                'is_verified': agent.get('is_verified', False)
            })

        # Get registry stats
        stats = agent_registry.get_registry_stats()

        return Response({
            'success': True,
            'agents_by_type': agents_by_type,
            'stats': {
                'total_agents': stats.total_agents,
                'active_agents': stats.active_agents,
                'total_executions': stats.total_executions,
                'avg_success_rate': stats.avg_success_rate
            }
        })

    except Exception as e:
        logger.error(f"Error getting available agents: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def execute_specific_agent(request):
    """
    Execute a specific agent with custom parameters
    """
    try:
        agent_name = request.data.get('agent_name')
        action = request.data.get('action')
        parameters = request.data.get('parameters', {})

        if not agent_name or not action:
            return Response({
                'success': False,
                'error': 'agent_name and action are required'
            }, status=400)

        # Create pipeline and execute single agent
        pipeline = AgentExecutionPipeline()

        # Create instruction
        from .agent_instruction_parser import AgentInstruction
        instruction = AgentInstruction(
            agent_type=agent_name,
            agent_name=agent_name,
            action=action,
            tool=agent_name,
            expected_outcome='Agent execution result',
            parameters=parameters,
            step_number=1,
            week='Immediate',
            original_text=action
        )

        # Execute the agent
        def run_single_execution():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    pipeline._execute_single_instruction(instruction, 'manual_execution')
                )
                return result
            finally:
                loop.close()

        result = run_single_execution()

        if result.get('success'):
            return Response({
                'success': True,
                'agent': result['agent'],
                'result': result['result'],
                'execution_time': result.get('timestamp'),
                'message': f'Agent {agent_name} executed successfully!'
            })
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Agent execution failed')
            }, status=500)

    except Exception as e:
        logger.error(f"Error executing specific agent: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_execution_status(request, execution_id):
    """
    Get status of an agent execution
    """
    try:
        # Try to get execution from database
        try:
            execution = ActionPlanExecution.objects.get(id=execution_id)
            return Response({
                'success': True,
                'status': execution.status,
                'result': execution.result,
                'started_at': execution.started_at,
                'completed_at': execution.completed_at,
                'error_message': execution.error_message
            })
        except ActionPlanExecution.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Execution not found'
            }, status=404)

    except Exception as e:
        logger.error(f"Error getting execution status: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)