"""
Project building and code execution views
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from pathlib import Path
import subprocess
import json
import random
import time
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_error_handler import AgentErrorHandler
from enhanced_agent_orchestrator import EnhancedAgentOrchestrator
from agent_project_advisor import AgentProjectAdvisor
from real_agent_orchestra import RealAgentOrchestra
import asyncio

# Project configuration
PROJECTS_BASE_DIR = Path("/Users/donkeyking/development/unified-donkey-betz/ai_generated_projects")

PROJECTS = {
    "ecommerce": {
        "name": "E-Commerce Revenue Engine",
        "modules": ["cart_recovery", "payment_processor", "inventory_manager", "customer_analytics"],
        "icon": "🛒"
    },
    "content_factory": {
        "name": "Content Factory 3.0",
        "modules": ["content_generator", "seo_optimizer", "social_scheduler", "analytics_tracker"],
        "icon": "✍️"
    },
    "trading_bot": {
        "name": "Crypto Trading Bot",
        "modules": ["market_analyzer", "trade_executor", "risk_manager", "portfolio_tracker"],
        "icon": "📈"
    },
    "predictive_analytics": {
        "name": "Predictive Analytics Engine",
        "modules": ["data_preprocessor", "model_trainer", "prediction_engine", "visualization_suite"],
        "icon": "🔮"
    }
}

@csrf_exempt
@require_http_methods(["POST"])
def switch_project(request):
    """Switch the active project"""
    try:
        data = json.loads(request.body)
        project = data.get('project', 'ecommerce')

        if project not in PROJECTS:
            return JsonResponse({
                'success': False,
                'error': 'Invalid project'
            })

        # Store active project in session
        request.session['active_project'] = project

        return JsonResponse({
            'success': True,
            'project': project,
            'name': PROJECTS[project]['name'],
            'modules': PROJECTS[project]['modules']
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def build_project_module(request):
    """Build a new module for the active project"""
    try:
        data = json.loads(request.body)
        project = data.get('project', request.session.get('active_project', 'ecommerce'))

        # Run the dynamic project builder
        result = subprocess.run(
            ['python', 'dynamic_project_builder.py', 'switch', project],
            capture_output=True,
            text=True,
            cwd='/Users/donkeyking/development/unified-donkey-betz',
            timeout=10
        )

        # Get the latest generated file
        project_dir = PROJECTS_BASE_DIR / project
        py_files = sorted(project_dir.glob("*.py"), key=lambda x: x.stat().st_mtime, reverse=True)

        if py_files:
            latest_file = py_files[0]
            with open(latest_file, 'r') as f:
                code = f.read()

            return JsonResponse({
                'success': True,
                'project': project,
                'file': latest_file.name,
                'code': code,
                'output': result.stdout if result.stdout else "Module built successfully"
            })

        return JsonResponse({
            'success': False,
            'error': 'No files generated'
        })

    except subprocess.TimeoutExpired:
        return JsonResponse({
            'success': False,
            'error': 'Build timeout'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def execute_latest_code(request):
    """Execute the latest generated code for a project with automatic error fixing"""
    try:
        data = json.loads(request.body)
        project = data.get('project', request.session.get('active_project', 'ecommerce'))
        specific_file = data.get('file', None)  # Allow executing a specific file

        # Get the project directory - handle Orchestra-generated projects
        project_clean = project.lower().replace(" ", "_").replace("-", "_")
        possible_dirs = [
            PROJECTS_BASE_DIR / project,
            PROJECTS_BASE_DIR / project_clean,
            PROJECTS_BASE_DIR / project.lower(),
            PROJECTS_BASE_DIR / project.replace(" ", "_"),
            PROJECTS_BASE_DIR / project.replace(" ", "-")
        ]

        project_dir = None
        for test_dir in possible_dirs:
            if test_dir.exists():
                project_dir = test_dir
                break

        if not project_dir:
            return JsonResponse({
                'success': False,
                'error': f'Project directory not found for: {project}'
            })

        # Get the file to execute
        if specific_file:
            # Execute a specific file
            target_file = project_dir / specific_file
            if not target_file.exists():
                return JsonResponse({
                    'success': False,
                    'error': f'File {specific_file} not found in project'
                })
        else:
            # Get the latest Python file
            py_files = sorted(project_dir.glob("*.py"), key=lambda x: x.stat().st_mtime, reverse=True)
            if not py_files:
                return JsonResponse({
                    'success': False,
                    'error': 'No code files found'
                })
            target_file = py_files[0]

        latest_file = target_file

        # Execute the code
        result = subprocess.run(
            ['python', str(latest_file)],
            capture_output=True,
            text=True,
            cwd=str(project_dir),
            timeout=5
        )

        # If there's an error, try to fix it automatically
        if result.returncode != 0 and result.stderr:
            error_handler = AgentErrorHandler()
            fix_success, fix_message = error_handler.attempt_fix(str(latest_file), result.stderr)

            if fix_success:
                # Try running the fixed code
                retry_result = subprocess.run(
                    ['python', str(latest_file)],
                    capture_output=True,
                    text=True,
                    cwd=str(project_dir),
                    timeout=5
                )

                return JsonResponse({
                    'success': retry_result.returncode == 0,
                    'file': latest_file.name,
                    'output': retry_result.stdout if retry_result.stdout else retry_result.stderr,
                    'project': project,
                    'auto_fixed': True,
                    'fix_message': fix_message
                })
            else:
                # Couldn't fix automatically, return the original error
                return JsonResponse({
                    'success': False,
                    'file': latest_file.name,
                    'output': result.stderr,
                    'project': project,
                    'fix_attempted': True,
                    'fix_message': fix_message
                })

        output = result.stdout if result.stdout else result.stderr

        return JsonResponse({
            'success': result.returncode == 0,
            'file': latest_file.name,
            'output': output,
            'project': project
        })

    except subprocess.TimeoutExpired:
        return JsonResponse({
            'success': False,
            'error': 'Execution timeout',
            'output': 'Code execution exceeded 5 seconds'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["GET"])
def get_latest_code(request):
    """Get the latest generated code for a project"""
    try:
        project = request.GET.get('project', request.session.get('active_project', 'ecommerce'))

        # Get the latest Python file
        project_dir = PROJECTS_BASE_DIR / project

        if not project_dir.exists():
            project_dir.mkdir(parents=True, exist_ok=True)

        py_files = sorted(project_dir.glob("*.py"), key=lambda x: x.stat().st_mtime, reverse=True)

        if py_files:
            latest_file = py_files[0]
            with open(latest_file, 'r') as f:
                code = f.read()

            return JsonResponse({
                'success': True,
                'project': project,
                'file': latest_file.name,
                'code': code,
                'timestamp': datetime.fromtimestamp(latest_file.stat().st_mtime).isoformat()
            })

        # Return sample code if no files exist yet
        return JsonResponse({
            'success': True,
            'project': project,
            'file': 'sample.py',
            'code': f'''#!/usr/bin/env python3
"""
{PROJECTS[project]['name']}
Waiting for code generation...
"""

print("Click 'Build New Module' to generate real code!")
print("Project: {PROJECTS[project]['name']}")
print("Modules available: {', '.join(PROJECTS[project]['modules'][:2])}")
''',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["GET"])
def get_project_stats(request):
    """Get statistics for all projects"""
    try:
        stats = {}

        for project_key, project_info in PROJECTS.items():
            project_dir = PROJECTS_BASE_DIR / project_key

            if project_dir.exists():
                py_files = list(project_dir.glob("*.py"))
                total_size = sum(f.stat().st_size for f in py_files)

                # Calculate progress based on file count
                progress = min(100, len(py_files) * 25)  # Each file adds 25%

                stats[project_key] = {
                    'name': project_info['name'],
                    'icon': project_info['icon'],
                    'file_count': len(py_files),
                    'total_size': total_size,
                    'progress': progress,
                    'modules': [f.stem for f in py_files]
                }
            else:
                stats[project_key] = {
                    'name': project_info['name'],
                    'icon': project_info['icon'],
                    'file_count': 0,
                    'total_size': 0,
                    'progress': 0,
                    'modules': []
                }

        return JsonResponse({
            'success': True,
            'stats': stats,
            'total_files': sum(s['file_count'] for s in stats.values())
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def get_agent_suggestions(request):
    """Get AI agent suggestions for the current project"""
    try:
        data = json.loads(request.body)
        project = data.get('project', request.session.get('active_project', 'ecommerce'))
        requested_agents = data.get('agents', None)  # Optional: specific agents to consult

        # Get the latest code for analysis
        project_dir = PROJECTS_BASE_DIR / project
        py_files = sorted(project_dir.glob("*.py"), key=lambda x: x.stat().st_mtime, reverse=True)

        if py_files:
            latest_file = py_files[0]
            with open(latest_file, 'r') as f:
                code = f.read()
        else:
            code = ""

        # Initialize advisor and get suggestions
        advisor = AgentProjectAdvisor()
        analysis = advisor.analyze_project(project, code, requested_agents)

        # Store suggestions in session for later application
        request.session['latest_suggestions'] = analysis

        return JsonResponse({
            'success': True,
            'project': project,
            'suggestions': analysis['suggestions'],
            'priority_actions': analysis['priority_actions'],
            'estimated_impact': analysis['estimated_impact'],
            'timestamp': analysis['timestamp'],
            'file': py_files[0].name if py_files else None
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def apply_suggestion(request):
    """Apply a specific agent suggestion to the project code"""
    try:
        data = json.loads(request.body)
        project = data.get('project', request.session.get('active_project', 'ecommerce'))
        agent_id = data.get('agent_id')
        suggestion_index = data.get('suggestion_index', 0)

        # Get the latest code file
        project_dir = PROJECTS_BASE_DIR / project
        py_files = sorted(project_dir.glob("*.py"), key=lambda x: x.stat().st_mtime, reverse=True)

        if not py_files:
            return JsonResponse({
                'success': False,
                'error': 'No code files found'
            })

        latest_file = py_files[0]

        # Get stored suggestions
        suggestions = request.session.get('latest_suggestions', {})

        # Find the specific suggestion
        for agent_suggestion in suggestions.get('suggestions', []):
            if agent_suggestion.get('agent_id') == agent_id:
                code_improvements = agent_suggestion.get('code_improvements', [])

                if suggestion_index < len(code_improvements):
                    improvement = code_improvements[suggestion_index]

                    # Read current file
                    with open(latest_file, 'r') as f:
                        current_code = f.read()

                    # Apply the improvement (add the new code)
                    lines = current_code.split('\n')

                    # Find a good insertion point (after imports, before main)
                    insert_index = 0
                    for i, line in enumerate(lines):
                        if line.startswith('import ') or line.startswith('from '):
                            insert_index = i + 1
                        elif line.strip().startswith('class ') and insert_index > 0:
                            break

                    # Insert the improvement code
                    improvement_code = improvement.get('code', '')
                    lines.insert(insert_index + 1, '')
                    lines.insert(insert_index + 2, '# Added by ' + agent_suggestion.get('agent', 'Agent'))
                    lines.insert(insert_index + 3, improvement_code)

                    # Write back to file
                    updated_code = '\n'.join(lines)
                    with open(latest_file, 'w') as f:
                        f.write(updated_code)

                    return JsonResponse({
                        'success': True,
                        'message': f"Applied {improvement.get('description', 'improvement')}",
                        'file': latest_file.name,
                        'code': updated_code
                    })

        return JsonResponse({
            'success': False,
            'error': 'Suggestion not found'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
@csrf_exempt
@require_http_methods(["POST"])
def orchestrate_real_build(request):
    """Trigger REAL agent orchestration to build a project"""
    import logging
    logger = logging.getLogger(__name__)

    try:
        data = json.loads(request.body)
        project_type = data.get('project', 'ecommerce')
        raw_project_name = data.get('name', PROJECTS.get(project_type, {}).get('name', 'AI Project'))

        # Clean project name to remove emojis and ensure ASCII-safe
        import re
        project_name = re.sub(r'[^\x00-\x7F]+', '', raw_project_name).strip()
        if not project_name:
            project_name = 'AI Project'

        logger.info(f"Starting orchestration for: {project_type} - {project_name}")

        # Use the enhanced orchestrator with real LLM capabilities
        use_enhanced = request.GET.get('enhanced', 'true').lower() == 'true'

        if use_enhanced:
            logger.info("Using Enhanced Agent Orchestrator with LLM")

            try:
                from enhanced_agent_orchestrator import EnhancedAgentOrchestrator

                # Create enhanced orchestrator
                orchestrator = EnhancedAgentOrchestrator()

                # Run orchestration with advisors and real execution
                result = orchestrator.orchestrate_with_advisors(project_type, project_name)

                logger.info(f"Enhanced orchestration completed: {result.get('status')}")

                # Get execution stats
                stats = orchestrator.get_stats()

                # Extract agent and advisor names from the result
                agent_executions = result.get('phases', {}).get('agent_execution', [])
                agents_used = [exec_result.get('agent', 'unknown') for exec_result in agent_executions if exec_result.get('success')]

                advisor_consultations = result.get('phases', {}).get('advisor_consultation', [])
                advisors = [consultation.get('advisor', 'unknown') for consultation in advisor_consultations]

                # Clean the result for JSON response
                clean_result = {
                    'project': result.get('project', project_name),
                    'type': result.get('type', project_type),
                    'status': result.get('status', 'Completed'),
                    'agents_used': agents_used,  # Array of agent names
                    'advisors': advisors,  # Array of advisor names
                    'phases': {
                        'advisors': len(advisor_consultations),
                        'agents': len(agent_executions)
                    },
                    'components_built': result.get('components_built', []),
                    'statistics': stats,
                    'enhanced': True,
                    'next_steps': 'Review generated code and deploy components'
                }

                return JsonResponse({
                    'success': True,
                    'project': project_type,
                    'result': clean_result,
                    'message': f'Enhanced orchestration: {stats["successes"]}/{stats["executions"]} successful!'
                }, json_dumps_params={'ensure_ascii': True})

            except ImportError:
                logger.warning("Enhanced orchestrator not available, falling back to simple")
                use_enhanced = False
            except Exception as e:
                logger.error(f"Error in enhanced orchestration: {e}")
                use_enhanced = False

        if not use_enhanced:
            logger.info("Using Simple Agent Orchestrator")

            try:
                from simple_agent_orchestrator import SimpleAgentOrchestrator

                # Create orchestrator instance
                orchestrator = SimpleAgentOrchestrator()

                # Run the orchestration
                result = orchestrator.orchestrate_project(project_type, project_name)

                logger.info(f"Orchestration completed: {result.get('status')}")

                # Clean the result for JSON response
                clean_result = {
                    'project': result.get('project', project_name),
                    'type': result.get('type', project_type),
                    'status': result.get('status', 'Completed'),
                    'agents_used': result.get('agents_used', []),
                    'advisors': result.get('advisors', []),
                    'components_built': result.get('components_built', []),
                    'next_steps': result.get('next_steps', 'Review and integrate')
                }

                return JsonResponse({
                    'success': True,
                    'project': project_type,
                    'result': clean_result,
                    'message': f'Successfully orchestrated with {len(clean_result["agents_used"])} agents!'
                }, json_dumps_params={'ensure_ascii': True})

            except Exception as e:
                logger.error(f"Error in simple orchestration: {e}")
                import traceback
                logger.error(traceback.format_exc())

                # Fallback response
                return JsonResponse({
                    'success': False,
                    'project': project_type,
                    'error': str(e),
                    'message': 'Orchestration failed - check server logs'
                }, json_dumps_params={'ensure_ascii': True})

        # Initialize the Real Agent Orchestra
        orchestra = RealAgentOrchestra()

        # Run the async build process
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Build the project with real agents and advisors
            # Add timeout to prevent hanging
            import asyncio
            raw_result = loop.run_until_complete(
                asyncio.wait_for(
                    orchestra.build_project(project_type, project_name),
                    timeout=30.0  # 30 second timeout
                )
            )

            # Ensure result is clean
            if raw_result:
                result = raw_result
            else:
                result = {}

            # Update build status
            status_file = PROJECTS_BASE_DIR / "build_status.json"

            if status_file.exists():
                with open(status_file, 'r') as f:
                    status = json.load(f)
            else:
                status = {"projects": {}}

            status['projects'][project_type] = {
                'name': project_name,
                'agents_used': result.get('agents_used', []),
                'advisors': result.get('advisors', []),
                'components_built': result.get('components_built', []),
                'status': result.get('status', 'Building'),
                'timestamp': datetime.now().isoformat()
            }

            with open(status_file, 'w') as f:
                json.dump(status, f, indent=2)

            # Clean result to avoid encoding issues
            def ensure_ascii_safe(obj):
                """Ensure all strings are ASCII safe"""
                if isinstance(obj, dict):
                    return {k: ensure_ascii_safe(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [ensure_ascii_safe(item) for item in obj]
                elif isinstance(obj, str):
                    # Remove any non-ASCII characters including broken surrogates
                    try:
                        obj.encode('utf-8')
                        # Remove emojis and non-ASCII characters
                        import re
                        return re.sub(r'[^\x00-\x7F]+', '', obj)
                    except UnicodeEncodeError:
                        # If encoding fails, remove problematic characters
                        return obj.encode('utf-8', 'ignore').decode('utf-8')
                else:
                    return obj

            clean_result = ensure_ascii_safe({
                'project': result.get('project', project_type),
                'type': result.get('type', project_type),
                'status': result.get('status', 'Building'),
                'agents_used': result.get('agents_used', []),
                'advisors': result.get('advisors', []),
                'components_built': result.get('components_built', []),
                'next_steps': result.get('next_steps', 'Continue building')
            })

            return JsonResponse({
                'success': True,
                'project': project_type,
                'result': clean_result,
                'message': ensure_ascii_safe(f'Real agents and advisors are building {project_name}!')
            }, json_dumps_params={'ensure_ascii': True, 'allow_nan': False})

        finally:
            loop.close()

    except Exception as e:
        import traceback
        # Try to extract clean error message
        error_msg = str(e)
        try:
            # Remove any problematic characters from error message
            error_msg = error_msg.encode('ascii', 'ignore').decode('ascii')
        except:
            error_msg = 'An error occurred during orchestration'

        return JsonResponse({
            'success': False,
            'error': error_msg,
            'details': 'Check server logs for full details'
        }, json_dumps_params={'ensure_ascii': True})

@csrf_exempt
@require_http_methods(["GET"])
def get_real_agents(request):
    """Get list of all real agents available in the system"""
    try:
        orchestra = RealAgentOrchestra()

        agents = []
        for agent_name, agent_class in orchestra.executor.agent_classes.items():
            agents.append({
                'id': agent_name,
                'name': agent_name.replace('_', ' ').title(),
                'available': True,
                'description': agent_class.__doc__ if hasattr(agent_class, '__doc__') else 'AI Agent'
            })

        advisors = []
        for advisor_id, advisor in orchestra.advisor_registry.advisors.items():
            advisors.append({
                'id': advisor_id,
                'name': advisor.name if hasattr(advisor, 'name') else advisor_id,
                'domain': str(advisor.domain) if hasattr(advisor, 'domain') else 'General',
                'available': True
            })

        return JsonResponse({
            'success': True,
            'agents': agents[:20],  # First 20 agents
            'total_agents': len(agents),
            'advisors': advisors[:10],  # First 10 advisors
            'total_advisors': len(advisors)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
