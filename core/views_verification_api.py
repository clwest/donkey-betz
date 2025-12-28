"""
Verification API Views
======================
Django API endpoints for agent learning verification system
"""

import json
import sys
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Add project root to path
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
from intelligence.learning_verification import verification_system

@csrf_exempt
@require_http_methods(["POST"])
def start_verification_session(request):
    """Start a new learning verification session"""
    try:
        data = json.loads(request.body or b"{}")
        agent_id = data.get('agent_id')
        skill_domain = data.get('skill_domain', 'code_generation')

        if not agent_id:
            return JsonResponse({'error': 'agent_id is required'}, status=400)

        session_id = verification_system.start_verification_session(agent_id, skill_domain)

        response = JsonResponse({
            'success': True,
            'session_id': session_id,
            'agent_id': agent_id,
            'skill_domain': skill_domain
        })
        response["Access-Control-Allow-Origin"] = "*"
        return response

    except Exception as e:
        response = JsonResponse({'error': str(e)}, status=500)
        response["Access-Control-Allow-Origin"] = "*"
        return response

@csrf_exempt
@require_http_methods(["POST"])
def run_baseline_test(request):
    """Run baseline capability test"""
    try:
        data = json.loads(request.body or b"{}")
        session_id = data.get('session_id')

        if not session_id:
            return JsonResponse({'error': 'session_id is required'}, status=400)

        results = verification_system.run_baseline_test(session_id)

        response = JsonResponse({
            'success': True,
            'results': {
                'agent_id': results.agent_id,
                'skill_domain': results.skill_domain,
                'problems_attempted': results.problems_attempted,
                'problems_solved': results.problems_solved,
                'success_rate': results.success_rate,
                'average_time': results.average_time,
                'solution_quality': results.solution_quality,
                'detailed_results': results.detailed_results
            }
        })
        response["Access-Control-Allow-Origin"] = "*"
        return response

    except Exception as e:
        response = JsonResponse({'error': str(e)}, status=500)
        response["Access-Control-Allow-Origin"] = "*"
        return response

@csrf_exempt
@require_http_methods(["POST"])
def expose_learning_material(request):
    """Expose agent to learning material"""
    try:
        data = json.loads(request.body or b"{}")
        session_id = data.get('session_id')
        learning_material = data.get('learning_material', {})

        if not session_id:
            return JsonResponse({'error': 'session_id is required'}, status=400)

        # Default learning material for code generation
        if not learning_material:
            learning_material = {
                'type': 'code_examples',
                'id': 'regex_patterns_advanced',
                'concepts': ['regular_expressions', 'pattern_matching', 'email_extraction', 'advanced_algorithms'],
                'examples': [
                    'import re\nemails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}", text)',
                    'pattern = r"\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"',
                    'def kadane_algorithm(arr):\n    max_sum = current_sum = arr[0]\n    for i in range(1, len(arr)):\n        current_sum = max(arr[i], current_sum + arr[i])\n        max_sum = max(max_sum, current_sum)\n    return max_sum',
                    'def binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1'
                ],
                'explanations': [
                    'Email extraction uses regex patterns to find email addresses in text',
                    'Kadane\'s algorithm efficiently finds maximum subarray sum',
                    'Binary search requires sorted array and uses divide-and-conquer'
                ]
            }

        exposure_record = verification_system.expose_learning_material(session_id, learning_material)

        response = JsonResponse({
            'success': True,
            'exposure_record': exposure_record
        })
        response["Access-Control-Allow-Origin"] = "*"
        return response

    except Exception as e:
        response = JsonResponse({'error': str(e)}, status=500)
        response["Access-Control-Allow-Origin"] = "*"
        return response

@csrf_exempt
@require_http_methods(["POST"])
def run_post_learning_test(request):
    """Run capability test after learning"""
    try:
        data = json.loads(request.body or b"{}")
        session_id = data.get('session_id')

        if not session_id:
            return JsonResponse({'error': 'session_id is required'}, status=400)

        results = verification_system.run_post_learning_test(session_id)

        # Get session for improvement metrics
        session_status = verification_system.get_session_status(session_id)

        response = JsonResponse({
            'success': True,
            'results': {
                'agent_id': results.agent_id,
                'skill_domain': results.skill_domain,
                'problems_attempted': results.problems_attempted,
                'problems_solved': results.problems_solved,
                'success_rate': results.success_rate,
                'average_time': results.average_time,
                'solution_quality': results.solution_quality,
                'detailed_results': results.detailed_results
            },
            'improvement_metrics': session_status.get('improvement_metrics', {}),
            'learning_verified': session_status.get('improvement_metrics', {}).get('success_rate_improvement', 0) > 0.1
        })
        response["Access-Control-Allow-Origin"] = "*"
        return response

    except Exception as e:
        response = JsonResponse({'error': str(e)}, status=500)
        response["Access-Control-Allow-Origin"] = "*"
        return response

@csrf_exempt
@require_http_methods(["GET"])
def get_session_status(request):
    """Get verification session status"""
    try:
        session_id = request.GET.get('session_id')

        if not session_id:
            return JsonResponse({'error': 'session_id is required'}, status=400)

        session_status = verification_system.get_session_status(session_id)

        response = JsonResponse({
            'success': True,
            'session': session_status
        })
        response["Access-Control-Allow-Origin"] = "*"
        return response

    except Exception as e:
        response = JsonResponse({'error': str(e)}, status=500)
        response["Access-Control-Allow-Origin"] = "*"
        return response

@csrf_exempt
@require_http_methods(["GET"])
def list_verification_sessions(request):
    """List all verification sessions"""
    try:
        sessions = verification_system.list_active_sessions()

        response = JsonResponse({
            'success': True,
            'sessions': sessions,
            'total_sessions': len(sessions)
        })
        response["Access-Control-Allow-Origin"] = "*"
        return response

    except Exception as e:
        response = JsonResponse({'error': str(e)}, status=500)
        response["Access-Control-Allow-Origin"] = "*"
        return response

@csrf_exempt
@require_http_methods(["POST"])
def run_quick_verification_demo(request):
    """Run a complete verification demo for testing"""
    try:
        data = json.loads(request.body or b"{}")
        agent_id = data.get('agent_id', 'demo_agent_001')
        skill_domain = data.get('skill_domain', 'code_generation')

        # Run complete verification process
        session_id = verification_system.start_verification_session(agent_id, skill_domain)

        # Baseline test
        baseline_results = verification_system.run_baseline_test(session_id)

        # Learning exposure
        learning_material = {
            'type': 'comprehensive_examples',
            'id': 'advanced_coding_patterns',
            'concepts': ['algorithms', 'data_structures', 'optimization', 'pattern_recognition'],
            'examples': [
                'Regex patterns for email extraction',
                'Dynamic programming solutions',
                'Binary search implementation',
                'Efficient sorting algorithms'
            ]
        }
        exposure_record = verification_system.expose_learning_material(session_id, learning_material)

        # Post-learning test
        post_results = verification_system.run_post_learning_test(session_id)

        # Get final session status
        session_status = verification_system.get_session_status(session_id)

        response = JsonResponse({
            'success': True,
            'demo_completed': True,
            'session_id': session_id,
            'baseline_results': {
                'success_rate': baseline_results.success_rate,
                'average_time': baseline_results.average_time,
                'solution_quality': baseline_results.solution_quality,
                'problems_solved': baseline_results.problems_solved
            },
            'post_learning_results': {
                'success_rate': post_results.success_rate,
                'average_time': post_results.average_time,
                'solution_quality': post_results.solution_quality,
                'problems_solved': post_results.problems_solved
            },
            'improvement_metrics': session_status.get('improvement_metrics', {}),
            'learning_verified': session_status.get('improvement_metrics', {}).get('success_rate_improvement', 0) > 0.1,
            'verification_summary': {
                'agent_learned': session_status.get('improvement_metrics', {}).get('success_rate_improvement', 0) > 0.1,
                'improvement_percentage': session_status.get('improvement_metrics', {}).get('success_rate_improvement', 0) * 100,
                'quality_improvement': session_status.get('improvement_metrics', {}).get('quality_improvement', 0),
                'time_saved': session_status.get('improvement_metrics', {}).get('time_improvement', 0)
            }
        })
        response["Access-Control-Allow-Origin"] = "*"
        return response

    except Exception as e:
        response = JsonResponse({'error': str(e)}, status=500)
        response["Access-Control-Allow-Origin"] = "*"
        return response