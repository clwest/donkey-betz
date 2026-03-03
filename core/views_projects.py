"""
Project building and code execution views
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from pathlib import Path
import subprocess
import json
import sys
import os
import logging
from datetime import datetime

# Initialize logger
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Project configuration
PROJECTS_BASE_DIR = Path("/Users/donkeyking/development/unified-donkey-betz/ai_generated_projects")

def find_project_directory(base_dir, project_name):
    """
    Intelligent project directory finder with fuzzy matching
    Handles dynamic project names created by agents with versions, underscores, hyphens, dots, etc.
    """
    if not project_name:
        return None

    # Clean project name for comparison
    project_lower = project_name.lower()
    project_clean = project_lower.replace(" ", "_").replace("-", "_")

    # Exact match attempts first
    exact_candidates = [
        project_name,
        project_clean,
        project_lower,
        project_name.replace(" ", "_"),
        project_name.replace(" ", "-"),
        project_name.replace("_", "-"),
        project_clean.replace("_", "-"),
        project_name.replace(".", "_"),  # Handle version dots
        project_name.replace("_", "."),  # Handle version dots reverse
    ]

    # Check exact matches first
    for candidate in exact_candidates:
        test_path = base_dir / candidate
        if test_path.exists() and test_path.is_dir():
            return test_path

    # If no exact match, do fuzzy matching on existing directories
    try:
        existing_dirs = [d for d in base_dir.iterdir() if d.is_dir()]
    except Exception:
        return None

    # Fuzzy matching - find directories that contain the project name or vice versa
    project_base = project_clean.replace("_", "").replace("-", "").replace(".", "")

    best_match = None
    best_score = 0

    for dir_path in existing_dirs:
        dir_name = dir_path.name.lower()
        dir_base = dir_name.replace("_", "").replace("-", "").replace(".", "")

        # Calculate similarity score
        score = 0

        # Exact substring match
        if project_base in dir_base or dir_base in project_base:
            score += 10

        # Common prefix match
        common_prefix = 0
        for i in range(min(len(project_base), len(dir_base))):
            if project_base[i] == dir_base[i]:
                common_prefix += 1
            else:
                break

        if common_prefix > 0:
            score += common_prefix

        # Version number handling (e.g., content_factory matches content_factory_3_0)
        if "_" in dir_name or "." in dir_name:
            # Remove version numbers and check again
            dir_base_no_version = dir_base.split("_")[0].split(".")[0]
            project_base_no_version = project_base.split("_")[0].split(".")[0]

            if dir_base_no_version == project_base_no_version:
                score += 15  # Higher score for version match

        # Update best match if this is better
        if score > best_score and score >= 5:  # Minimum threshold
            best_score = score
            best_match = dir_path

    return best_match

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
        data = json.loads(request.body or b"{}")
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
        data = json.loads(request.body or b"{}")
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
        data = json.loads(request.body or b"{}")
        project = data.get('project', request.session.get('active_project', 'ecommerce'))
        specific_file = data.get('file', None)  # Allow executing a specific file

        # Get the project directory - handle Orchestra-generated projects with intelligent matching
        project_dir = find_project_directory(PROJECTS_BASE_DIR, project)

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

        # Check if this is server code that needs test mode
        with open(latest_file, 'r') as f:
            file_content = f.read()

        is_server_code = 'serve_forever()' in file_content or 'HTTPServer' in file_content

        # Execute the code with appropriate timeout and flags
        if is_server_code:
            # Run server code in test mode with longer timeout
            result = subprocess.run(
                ['python', str(latest_file), '--test'],
                capture_output=True,
                text=True,
                cwd=str(project_dir),
                timeout=10  # Longer timeout for server tests
            )
        else:
            # Regular code execution
            result = subprocess.run(
                ['python', str(latest_file)],
                capture_output=True,
                text=True,
                cwd=str(project_dir),
                timeout=5
            )

        # If there's an error, report it (auto-fix via PA tools)
        if result.returncode != 0 and result.stderr:
            fix_success = False
            fix_message = result.stderr[:500]

            if False:  # Auto-fix removed — use PA auto_fix_code tool instead
                # Check if the fixed code is server code
                with open(latest_file, 'r') as f:
                    fixed_content = f.read()

                is_fixed_server_code = 'serve_forever()' in fixed_content or 'HTTPServer' in fixed_content

                # Try running the fixed code
                if is_fixed_server_code:
                    retry_result = subprocess.run(
                        ['python', str(latest_file), '--test'],
                        capture_output=True,
                        text=True,
                        cwd=str(project_dir),
                        timeout=10
                    )
                else:
                    retry_result = subprocess.run(
                        ['python', str(latest_file)],
                        capture_output=True,
                        text=True,
                        cwd=str(project_dir),
                        timeout=5
                    )

                # Update execution status in database after auto-fix
                retry_output = retry_result.stdout if retry_result.stdout else retry_result.stderr
                try:
                    from core.models import GeneratedProject, GeneratedCode
                    project_obj = GeneratedProject.objects.get(name=project)
                    code_obj = GeneratedCode.objects.filter(
                        project=project_obj,
                        filename=latest_file.name,
                        is_latest=True
                    ).first()

                    if code_obj:
                        code_obj.execution_status = 'fixed' if retry_result.returncode == 0 else 'error'
                        code_obj.execution_output = retry_output
                        code_obj.save()
                except Exception as e:
                    logger.warning(f"Could not update execution status after auto-fix: {e}")

                return JsonResponse({
                    'success': retry_result.returncode == 0,
                    'file': latest_file.name,
                    'output': retry_output,
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

        # Update execution status in database if available
        try:
            from core.models import GeneratedProject, GeneratedCode
            project_obj = GeneratedProject.objects.get(name=project)
            code_obj = GeneratedCode.objects.filter(
                project=project_obj,
                filename=latest_file.name,
                is_latest=True
            ).first()

            if code_obj:
                code_obj.execution_status = 'success' if result.returncode == 0 else 'error'
                code_obj.execution_output = output
                code_obj.save()
        except Exception as e:
            logger.warning(f"Could not update execution status in database: {e}")

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
            'output': 'Code execution exceeded time limit (5s for scripts, 10s for servers)'
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
    from core.models import GeneratedProject, GeneratedCode

    try:
        project = request.GET.get('project', request.session.get('active_project', 'ecommerce'))

        # First, try to get code from database
        try:
            project_obj = GeneratedProject.objects.get(name=project)
            latest_code = GeneratedCode.objects.filter(
                project=project_obj,
                is_latest=True
            ).order_by('-created_at').first()

            if latest_code:
                return JsonResponse({
                    'success': True,
                    'project': project,
                    'file': latest_code.filename,
                    'code': latest_code.content,
                    'timestamp': latest_code.created_at.isoformat(),
                    'agent_creator': latest_code.agent_creator,
                    'task_description': latest_code.task_description,
                    'language': latest_code.language,
                    'execution_status': latest_code.execution_status,
                    'source': 'database'
                })
        except GeneratedProject.DoesNotExist:
            pass  # Fall back to file system

        # Fallback: Get from file system (for backward compatibility)
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
                'timestamp': datetime.fromtimestamp(latest_file.stat().st_mtime).isoformat(),
                'source': 'filesystem'
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
        data = json.loads(request.body or b"{}")
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

        # Project advisor removed — use PA agent routing instead
        analysis = {
            'suggestions': [],
            'message': 'Use PA agent routing for project advice',
        }

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
        data = json.loads(request.body or b"{}")
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
        data = json.loads(request.body or b"{}")
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

        # RealAgentOrchestra removed — use PA run_agent tool for orchestrated builds
        return JsonResponse({
            'success': False,
            'error': 'Real agent orchestra deprecated — use PA run_agent tool',
            'project': project_type,
        })

    except Exception as e:
        logger.error(f"Orchestration error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        })

@csrf_exempt
@require_http_methods(["GET"])
def get_real_agents(request):
    """Get list of all real agents available in the system"""
    try:
        from core.models_unified_system import Agent

        agent_qs = Agent.objects.filter(
            is_active=True
        ).exclude(agent_type='advisor').values_list('name', flat=True).order_by('name')

        agents = [
            {'id': name, 'name': name.replace('_', ' ').replace('-', ' ').title(), 'available': True}
            for name in agent_qs
        ]

        advisors_qs = Agent.objects.filter(
            agent_type='advisor', is_active=True
        ).values_list('name', flat=True)[:25]

        advisors = [{'id': name, 'name': name, 'available': True} for name in advisors_qs]

        return JsonResponse({
            'success': True,
            'agents': agents[:20],
            'total_agents': len(agents),
            'advisors': advisors,
            'total_advisors': len(advisors),
        })

    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
