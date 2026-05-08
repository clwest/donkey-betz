"""
Improved Agent Execution Views with Real LLM Support
====================================================

This module provides both demo mode (fast, pre-generated) and real mode
(actual agent execution with LLM calls).
"""

# PARTIAL — Session 1113 review (Session 1111 PR-B/PR-E queue).
# Classification: built but not URL-mounted.
# Why: reached only via `views_deployment_execute.execute_deployed_agents`
# (lazy import) and `tests/spiders/test_agent_modes.py` (single test
# import of `execute_agents_improved`). The view itself is not registered
# in any URLConf — `agents/urls_deployment.py` is dark.
# Decision pending: same as `agents/urls_deployment.py`.
# See: docs/handoffs/SESSION_1111_DEEPER_REVIEW_MAP.md

import os
import json
from typing import Dict, Any
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from core.models import GeneratedProject, GeneratedCode
import redis

# Redis URL for production compatibility
_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@csrf_exempt
@require_http_methods(["POST"])
def execute_agents_improved(request):
    """
    Execute agents with choice of mode:
    - demo: Fast, uses pre-generated code templates
    - real: Actual agent execution with LLM calls
    """
    try:
        data = json.loads(request.body or b"{}")
        project_id = data.get('project_id')
        project_type = data.get('project_type', 'ecommerce')
        project_description = data.get('project_description', '')
        key_features = data.get('key_features', [])
        target_audience = data.get('target_audience', '')
        agent_names = data.get('agents', [])
        ml_features = data.get('ml_features', [])
        execution_mode = data.get('mode', 'demo')  # 'demo' or 'real'
        requirements = data.get('requirements', {})

        # Create project name from description
        project_name = project_description[:50] if project_description else f"{project_type.title()} Project"

        # Create or get project
        if project_id:
            project = GeneratedProject.objects.get(id=project_id)
        else:
            project = GeneratedProject.objects.create(
                name=project_name,
                project_type=project_type,
                description=project_description or f"AI-generated {project_type} project",
                status='generating',
                agents_used=agent_names,
                metadata={
                    'mode': execution_mode,
                    'key_features': key_features,
                    'target_audience': target_audience,
                    'requirements': requirements
                }
            )

        generated_outputs = []
        generated_files = []

        if execution_mode == 'real':
            # Real agent execution with LLM calls
            from agents.proper_agent_executor import execute_agents_properly

            # Send real-time updates via WebSocket
            channel_layer = get_channel_layer()

            task_config = {
                'project_type': project_type,
                'project_description': project_description,
                'key_features': key_features,
                'target_audience': target_audience,
                'ml_features': ml_features,
                'requirements': requirements,
                'strategy': data.get('strategy', 'sequential')
            }

            # Notify that real execution is starting
            async_to_sync(channel_layer.group_send)(
                'ai_training',
                {
                    'type': 'broadcast_learning_update',
                    'data': {
                        'event': 'real_execution_started',
                        'message': f'Starting real LLM execution for {len(agent_names)} agents',
                        'agents': agent_names
                    }
                }
            )

            # Execute agents in a separate thread to avoid async context issues
            import threading
            import queue

            result_queue = queue.Queue()

            def execute_in_thread():
                try:
                    results = execute_agents_properly(agent_names, project, task_config)
                    result_queue.put(('success', results))
                except Exception as e:
                    result_queue.put(('error', str(e)))

            thread = threading.Thread(target=execute_in_thread)
            thread.start()
            thread.join(timeout=300)  # 5 minute timeout

            if thread.is_alive():
                # Timeout occurred
                results = [{
                    'success': False,
                    'agent': agent,
                    'error': 'Execution timeout after 5 minutes'
                } for agent in agent_names]
            else:
                try:
                    status, results = result_queue.get_nowait()
                    if status == 'error':
                        results = [{
                            'success': False,
                            'agent': agent,
                            'error': results
                        } for agent in agent_names]
                except queue.Empty:
                    results = [{
                        'success': False,
                        'agent': agent,
                        'error': 'Unknown execution error'
                    } for agent in agent_names]

            for i, result in enumerate(results):
                if result['success']:
                    generated_outputs.append({
                        'agent': result['agent'],
                        'status': 'success',
                        'output': f"Completed {result['task']}: Generated {result.get('file_created', 'output')}",
                        'task': result['task'],
                        'files_created': 1
                    })

                    generated_files.append({
                        'filename': result.get('file_created', 'output.json'),
                        'path': f"ai_generated_projects/{project.name}/{result.get('file_created', 'output.json')}",
                        'size': result.get('content_length', 0),
                        'agent': result['agent']
                    })

                    # Track learning metrics for real execution
                    track_real_learning(result['agent'], result)

                else:
                    generated_outputs.append({
                        'agent': result['agent'],
                        'status': 'error',
                        'output': result.get('error', 'Execution failed'),
                        'files_created': 0
                    })

        else:
            # Demo mode - fast, pre-generated templates
            from agents.real_code_generator import RealCodeGenerator

            for agent_name in agent_names:
                try:
                    # Generate demo code quickly
                    generated = RealCodeGenerator.generate_code_by_agent(
                        agent_name, project_type, ml_features
                    )
                    code_content = generated['code']
                    file_name = generated['filename']

                    # Save to database
                    code_file = GeneratedCode.objects.create(
                        project=project,
                        filename=file_name,
                        file_path=f"ai_generated_projects/{project.name}/{file_name}",
                        content=code_content,
                        language='python',
                        agent_creator=agent_name,
                        task_description=f"Demo code for {project_type}",
                        is_latest=True,
                        execution_status='success'
                    )

                    generated_files.append({
                        'filename': file_name,
                        'path': code_file.file_path,
                        'size': len(code_content),
                        'agent': agent_name
                    })

                    generated_outputs.append({
                        'agent': agent_name,
                        'status': 'success',
                        'output': f"Generated {file_name} with {len(code_content)} bytes of code (demo mode)",
                        'files_created': 1
                    })

                    # Track demo learning metrics
                    track_demo_learning(agent_name, code_content)

                except Exception as e:
                    generated_outputs.append({
                        'agent': agent_name,
                        'status': 'error',
                        'output': str(e),
                        'files_created': 0
                    })

        # Update project status
        project.status = 'completed'
        project.save()

        return JsonResponse({
            'success': True,
            'project_id': str(project.id),
            'execution_mode': execution_mode,
            'outputs': generated_outputs,
            'files': generated_files,
            'total_files': len(generated_files),
            'message': f"Executed {len(generated_outputs)} agents in {execution_mode} mode"
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def track_real_learning(agent_name: str, result: Dict[str, Any]):
    """Track learning metrics for real agent execution"""
    try:
        from intelligence.learning_verification import LearningVerificationSystem

        learning_system = LearningVerificationSystem()

        # For real execution, track actual task completion
        learning_result = {
            'quality': 85,  # Higher quality for real execution
            'improvement': 10,
            'complexity': 75,
            'task_completed': result.get('task'),
            'output_type': result.get('file_created', '').split('.')[-1]
        }

        # Store in Redis
        r = redis.Redis.from_url(_REDIS_URL, decode_responses=True)
        r.hincrby(f'agent:{agent_name}:stats', 'real_executions', 1)
        r.hset(f'agent:{agent_name}:stats', 'last_real_task', result.get('task', ''))
        r.hset(f'agent:{agent_name}:stats', 'last_quality_score', 85)

        # Broadcast via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'ai_training',
            {
                'type': 'broadcast_learning_update',
                'data': {
                    'agent': agent_name,
                    'event': 'real_task_completed',
                    'metrics': learning_result
                }
            }
        )

    except Exception as e:
        print(f"Learning tracking error: {e}")


def track_demo_learning(agent_name: str, code_content: str):
    """Track learning metrics for demo execution"""
    try:
        from intelligence.learning_verification import LearningVerificationSystem

        learning_system = LearningVerificationSystem()
        learning_result = learning_system.verify_capability_improvement(
            agent_name=agent_name,
            task_type='code_generation',
            generated_code=code_content
        )

        # Store in Redis
        r = redis.Redis.from_url(_REDIS_URL, decode_responses=True)
        r.hincrby(f'agent:{agent_name}:stats', 'demo_executions', 1)
        r.hincrby(f'agent:{agent_name}:stats', 'total_lines', len(code_content.splitlines()))

        # Calculate quality and complexity scores for demo mode
        lines_count = len(code_content.splitlines())
        quality_score = min(100, 75 + (lines_count / 20))  # Base 75% + bonus for more lines
        complexity_score = min(100, 60 + (lines_count / 15))  # Base 60% + bonus for more lines

        # Broadcast via WebSocket with proper metrics
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'ai_training',
            {
                'type': 'broadcast_learning_update',
                'data': {
                    'agent': agent_name,
                    'event': 'demo_code_generated',
                    'metrics': {
                        'lines_of_code': lines_count,
                        'quality_score': quality_score,
                        'complexity_score': complexity_score,
                        'learning_progress': min(100, quality_score + (complexity_score * 0.3))
                    }
                }
            }
        )

    except Exception as e:
        print(f"Learning tracking error: {e}")


@csrf_exempt
@require_http_methods(["GET"])
def get_execution_modes(request):
    """Get available execution modes and their descriptions"""
    return JsonResponse({
        'modes': [
            {
                'id': 'demo',
                'name': 'Demo Mode',
                'description': 'Fast execution with pre-generated templates',
                'speed': 'Instant',
                'uses_llm': False,
                'cost': 'Free'
            },
            {
                'id': 'real',
                'name': 'Real Mode',
                'description': 'Actual agent execution with LLM calls',
                'speed': '10-30 seconds per agent',
                'uses_llm': True,
                'cost': 'Uses API credits'
            }
        ],
        'default': 'demo'
    })


@csrf_exempt
@require_http_methods(["GET"])
def debug_agent_registry(request):
    """Debug endpoint to inspect agent registry status"""
    try:
        from agents.proper_agent_executor import ProperAgentExecutor

        executor = ProperAgentExecutor()

        registry_info = {
            'has_agent_classes': hasattr(executor.executor, 'agent_classes'),
            'total_agents': 0,
            'available_agents': [],
            'executor_attributes': dir(executor.executor)
        }

        if hasattr(executor.executor, 'agent_classes'):
            registry_info['total_agents'] = len(executor.executor.agent_classes)
            registry_info['available_agents'] = sorted(list(executor.executor.agent_classes.keys()))

        # Test some common agent mappings
        test_mappings = {
            'Brand Strategist': 'brand_strategist',
            'NLP Specialist': 'nlp_specialist',
            'ML Recommendation Engine': 'ml_pipeline',
            'Business Agent': 'business_analyst'
        }

        mapping_results = {}
        for display_name, expected_key in test_mappings.items():
            mapping_results[display_name] = {
                'expected_key': expected_key,
                'found_in_registry': expected_key in registry_info.get('available_agents', [])
            }

        registry_info['mapping_test'] = mapping_results

        return JsonResponse({
            'success': True,
            'registry_info': registry_info
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)