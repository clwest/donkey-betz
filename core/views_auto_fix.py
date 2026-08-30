"""
Auto-fix views for AI agent-powered debugging
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Stubs removed — auto-fix uses LLM directly

# Project configuration
PROJECTS_BASE_DIR = Path("/Users/donkeyking/Donkey_Betz/unified-donkey-betz/ai_generated_projects")


@csrf_exempt
@require_http_methods(["POST"])
def auto_fix_code(request):
    """Auto-fix failed code using AI agents"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
    try:
        data = json.loads(request.body or b"{}")
        project = data.get('project', '')
        file_name = os.path.basename(data.get('file', ''))  # sanitize path traversal
        error_message = data.get('error', '')

        if not all([project, file_name, error_message]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameters: project, file, error'
            })

        # Find the project directory using intelligent matching
        from .views_projects import find_project_directory
        project_dir = find_project_directory(PROJECTS_BASE_DIR, project)

        if not project_dir:
            return JsonResponse({
                'success': False,
                'error': f'Project directory not found for: {project}'
            })

        file_path = project_dir / file_name
        if not file_path.exists():
            return JsonResponse({
                'success': False,
                'error': f'File {file_name} not found in project'
            })

        # Attempt LLM-based fix directly (stubs removed)
        fix_success = False
        fix_message = ''

        if False:  # legacy error_handler path removed
            # Test the fixed code automatically
            try:
                test_result = subprocess.run(
                    ['python', str(file_path)],
                    capture_output=True,
                    text=True,
                    cwd=str(project_dir),
                    timeout=5
                )

                auto_test_success = test_result.returncode == 0
                auto_test_output = test_result.stdout if auto_test_success else test_result.stderr

                return JsonResponse({
                    'success': True,
                    'fix_description': fix_message,
                    'agent_used': 'Code Debug Agent',
                    'auto_test_success': auto_test_success,
                    'auto_test_result': auto_test_output[:500] if auto_test_output else 'No output',
                    'fix_method': 'agent_error_handler'
                })

            except subprocess.TimeoutExpired:
                return JsonResponse({
                    'success': True,
                    'fix_description': fix_message,
                    'agent_used': 'Code Debug Agent',
                    'auto_test_success': False,
                    'auto_test_result': 'Test timed out after 5 seconds',
                    'fix_method': 'agent_error_handler'
                })

        else:
            # If the built-in error handler failed, try using LLM agents for more advanced fixing
            try:
                # Read the current file content
                with open(file_path, 'r') as f:
                    current_code = f.read()

                # Create a fix prompt for the LLM
                fix_prompt = f"""Fix this Python code that has an error:

ERROR:
{error_message}

CURRENT CODE:
{current_code}

Please provide a corrected version of the code that fixes the error. Return only the corrected Python code without explanations."""

                # Use OpenAI directly for the fix
                from config.api_settings import get_openai_client
                client = get_openai_client()
                response = client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[{"role": "user", "content": fix_prompt}],
                    max_completion_tokens=6000,
                )
                fixed_code = response.choices[0].message.content or ''

                # Clean the response to extract just the code
                if "```python" in fixed_code:
                    fixed_code = fixed_code.split("```python")[1].split("```")[0].strip()
                elif "```" in fixed_code:
                    fixed_code = fixed_code.split("```")[1].split("```")[0].strip()

                # Write the fixed code back to the file
                with open(file_path, 'w') as f:
                    f.write(fixed_code)

                # Test the LLM-fixed code
                try:
                    test_result = subprocess.run(
                        ['python', str(file_path)],
                        capture_output=True,
                        text=True,
                        cwd=str(project_dir),
                        timeout=5
                    )

                    auto_test_success = test_result.returncode == 0
                    auto_test_output = test_result.stdout if auto_test_success else test_result.stderr

                    return JsonResponse({
                        'success': True,
                        'fix_description': 'LLM agent rewrote the code to fix the error',
                        'agent_used': 'GPT-4o-mini Code Fixer',
                        'auto_test_success': auto_test_success,
                        'auto_test_result': auto_test_output[:500] if auto_test_output else 'No output',
                        'fix_method': 'llm_rewrite'
                    })

                except subprocess.TimeoutExpired:
                    return JsonResponse({
                        'success': True,
                        'fix_description': 'LLM agent rewrote the code to fix the error',
                        'agent_used': 'GPT-4o-mini Code Fixer',
                        'auto_test_success': False,
                        'auto_test_result': 'Test timed out after 5 seconds',
                        'fix_method': 'llm_rewrite'
                    })

            except Exception as llm_error:
                return JsonResponse({
                    'success': False,
                    'error': f'Both built-in and LLM fixing failed. LLM error: {str(llm_error)}'
                })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Auto-fix service error: {str(e)}'
        })