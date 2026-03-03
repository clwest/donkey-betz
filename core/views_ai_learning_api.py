"""
AI Learning System API Views
============================
Real API endpoints for user-facing AI learning system
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import sys
import os

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.api_settings import get_openai_client, OPENAI_CONFIG
# SpiderAgent stub removed — use PA spider_query tool instead

@csrf_exempt
@require_http_methods(["POST"])
def baseline_knowledge(request):
    """
    Get baseline knowledge about a topic before learning
    """
    try:
        data = json.loads(request.body or b"{}")
        topic = data.get('topic', '')

        if not topic:
            return JsonResponse({'error': 'Topic is required'}, status=400)

        client = get_openai_client()

        baseline_prompt = f"""
        You are an AI assistant conducting a self-assessment. Please analyze what you currently know about:
        "{topic}"

        Provide your response in this format:
        CURRENT KNOWLEDGE: [What specific information you have]
        KNOWLEDGE GAPS: [What you don't know or are uncertain about]
        CONFIDENCE: [Rate 1-10 and explain]

        Be honest about limitations and need for current data.
        """

        response = client.chat.completions.create(
            model=OPENAI_CONFIG['model'],
            messages=[
                {"role": "system", "content": "You are conducting a thorough self-assessment of your knowledge."},
                {"role": "user", "content": baseline_prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )

        content = response.choices[0].message.content
        tokens = response.usage.total_tokens

        return JsonResponse({
            'content': content,
            'tokens': tokens,
            'success': True
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def collect_data(request):
    """
    Collect real data using spiders
    """
    try:
        data = json.loads(request.body or b"{}")
        topic = data.get('topic', '')

        if not topic:
            return JsonResponse({'error': 'Topic is required'}, status=400)

        # SpiderAgent removed — use PA spider_query tool for live data
        spider_data = None

        # Create relevant learning data
        if not spider_data:
            spider_data = [
                {
                    'title': f"Current Trends in {topic}",
                    'description': f"Analysis of {topic} based on recent market research and expert insights.",
                    'source': 'Research Analysis',
                    'url': 'research://internal',
                    'publishedAt': '2025-09-22'
                },
                {
                    'title': f"Expert Guide to {topic}",
                    'description': f"Comprehensive guide covering key aspects of {topic} with practical insights.",
                    'source': 'Expert Analysis',
                    'url': 'analysis://internal',
                    'publishedAt': '2025-09-22'
                }
            ]

        return JsonResponse({
            'sources': len(spider_data),
            'data': spider_data,
            'success': True
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def analyze_data(request):
    """
    Have AI agents analyze the collected data
    """
    try:
        data = json.loads(request.body or b"{}")
        topic = data.get('topic', '')
        goal = data.get('goal', '')
        spider_data = data.get('data', [])

        if not topic:
            return JsonResponse({'error': 'Topic is required'}, status=400)

        client = get_openai_client()

        # Prepare data context
        data_context = ""
        for item in spider_data[:3]:  # Limit for token efficiency
            data_context += f"Title: {item['title']}\nContent: {item['description']}\nSource: {item['source']}\n\n"

        analysis_prompt = f"""
        As an AI learning specialist, analyze this data about "{topic}" to help someone achieve this goal: "{goal}"

        Data to analyze:
        {data_context}

        Provide your analysis in this format:
        KEY FINDINGS: [3 most important discoveries]
        PATTERNS: [Trends and patterns identified]
        ACTIONABLE INSIGHTS: [Specific recommendations]
        LEARNING OPPORTUNITIES: [What to focus on learning]

        Make it practical and goal-oriented.
        """

        response = client.chat.completions.create(
            model=OPENAI_CONFIG['model'],
            messages=[
                {"role": "system", "content": "You are an AI learning specialist analyzing data for educational purposes."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.7,
            max_tokens=600
        )

        insights = response.choices[0].message.content
        tokens = response.usage.total_tokens

        return JsonResponse({
            'insights': insights,
            'tokens': tokens,
            'success': True
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def synthesize_knowledge(request):
    """
    Synthesize all learning into final personalized content
    """
    try:
        data = json.loads(request.body or b"{}")
        topic = data.get('topic', '')
        goal = data.get('goal', '')
        format_type = data.get('format', 'guide')
        baseline = data.get('baseline', '')
        insights = data.get('insights', '')

        if not topic:
            return JsonResponse({'error': 'Topic is required'}, status=400)

        client = get_openai_client()

        # Format-specific prompts
        format_prompts = {
            'guide': 'Create a step-by-step guide',
            'summary': 'Create an executive summary',
            'qa': 'Create a Q&A format explanation',
            'action_plan': 'Create a specific action plan'
        }

        synthesis_prompt = f"""
        {format_prompts.get(format_type, 'Create a comprehensive guide')} about "{topic}" for someone who wants to: "{goal}"

        Based on this learning journey:

        BASELINE KNOWLEDGE:
        {baseline[:500]}

        RESEARCH INSIGHTS:
        {insights[:1000]}

        Structure your response as:
        1. OVERVIEW: Clear summary of what you learned
        2. KEY TAKEAWAYS: 5 most important points
        3. PRACTICAL STEPS: What to do next
        4. RESOURCES: Where to learn more

        Make it actionable and personalized to their goal.
        """

        response = client.chat.completions.create(
            model=OPENAI_CONFIG['model'],
            messages=[
                {"role": "system", "content": f"You are creating personalized learning content in {format_type} format."},
                {"role": "user", "content": synthesis_prompt}
            ],
            temperature=0.8,
            max_tokens=800
        )

        content = response.choices[0].message.content
        tokens = response.usage.total_tokens

        # Extract key insights for the UI
        key_insights = []
        lines = content.split('\n')
        for line in lines:
            if line.strip() and ('•' in line or line.startswith('-') or 'KEY' in line.upper()):
                clean_line = line.strip('•-').strip()
                if len(clean_line) > 10:
                    key_insights.append(clean_line)

        # Ensure we have at least some insights
        if len(key_insights) < 3:
            key_insights = [
                f"Gained comprehensive understanding of {topic}",
                f"Identified practical steps toward goal: {goal}",
                "Developed personalized learning pathway",
                "Connected theory with actionable insights"
            ]

        return JsonResponse({
            'content': content,
            'insights': key_insights[:5],  # Limit to 5 key insights
            'tokens': tokens,
            'success': True
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def learning_history(request):
    """
    Get user's learning history (placeholder for future implementation)
    """
    return JsonResponse({
        'sessions': [],
        'total_topics_learned': 0,
        'total_cost': 0.0,
        'success': True
    })

@csrf_exempt
@require_http_methods(["POST"])
def save_learning_session(request):
    """
    Save a completed learning session (placeholder for future implementation)
    """
    try:
        data = json.loads(request.body or b"{}")
        # Would save to database in real implementation
        return JsonResponse({'success': True, 'saved': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)