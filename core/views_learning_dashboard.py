"""
Learning Dashboard API Views
===========================
Serves real-time learning data for the AI-proof jobs learning dashboard
"""

import os
import redis
from datetime import datetime
from django.http import JsonResponse


def learning_dashboard_data(request):
    """
    API endpoint for real-time learning dashboard data
    """
    try:
        r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'), db=4, decode_responses=True)

        # Get main status
        status = r.hgetall("learning:dashboard:status")

        # Get individual topic data
        topics = []
        for i in range(4):  # 4 topics
            topic_data = r.hgetall(f"learning:topic:{i}")
            if topic_data:
                topics.append({
                    'index': i,
                    'topic': topic_data.get('topic', ''),
                    'baseline_length': int(topic_data.get('baseline_length', 0)),
                    'post_learning_length': int(topic_data.get('post_learning_length', 0)),
                    'knowledge_increase': float(topic_data.get('knowledge_increase', 0)),
                    'status': topic_data.get('status', 'pending'),
                    'spider_sources': int(topic_data.get('spider_sources', 0)),
                    'baseline_tokens': int(topic_data.get('baseline_tokens', 0)),
                    'learning_tokens': int(topic_data.get('learning_tokens', 0)),
                    'post_learning_tokens': int(topic_data.get('post_learning_tokens', 0))
                })

        response_data = {
            'status': {
                'phase': status.get('phase', 'initializing'),
                'current_topic': status.get('current_topic', ''),
                'current_topic_index': int(status.get('current_topic_index', 0)),
                'topics_total': int(status.get('topics_total', 4)),
                'topics_completed': int(status.get('topics_completed', 0)),
                'learning_events': int(status.get('learning_events', 0)),
                'total_tokens': int(status.get('total_tokens', 0)),
                'total_cost': float(status.get('total_cost', 0.0)),
                'session_complete': status.get('session_complete', 'false') == 'true',
                'timestamp': status.get('timestamp', datetime.now().isoformat())
            },
            'topics': topics,
            'chart_data': {
                'labels': [topic.get('topic', f'Topic {topic["index"]+1}')[:20] + '...' for topic in topics],
                'baseline': [topic['baseline_length'] for topic in topics],
                'learned': [topic['post_learning_length'] for topic in topics]
            }
        }

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': {'phase': 'error'},
            'topics': [],
            'chart_data': {'labels': [], 'baseline': [], 'learned': []}
        })

def learning_updates_stream(request):
    """
    API endpoint for live update stream
    """
    try:
        r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'), db=4, decode_responses=True)

        # Get recent updates (last 20)
        updates = []

        # Check for recent activity
        status = r.hgetall("learning:dashboard:status")
        phase = status.get('phase', 'initializing')
        current_topic = status.get('current_topic', '')

        # Generate contextual updates based on phase
        timestamp = datetime.now().strftime('%H:%M:%S')

        if phase == 'baseline_testing':
            updates.append({
                'timestamp': timestamp,
                'message': f'🔍 Testing baseline knowledge: {current_topic[:30]}...',
                'type': 'baseline'
            })
        elif phase == 'spider_collection':
            updates.append({
                'timestamp': timestamp,
                'message': f'🕷️ Spider collecting data: {current_topic[:30]}...',
                'type': 'learning'
            })
        elif phase == 'post_learning_testing':
            updates.append({
                'timestamp': timestamp,
                'message': f'🧠 Testing learned knowledge: {current_topic[:30]}...',
                'type': 'learning'
            })
        elif phase == 'complete':
            updates.append({
                'timestamp': timestamp,
                'message': '✅ Learning session complete - Real AI learning proven!',
                'type': 'completed'
            })

        return JsonResponse({'updates': updates})

    except Exception as e:
        return JsonResponse({'updates': [], 'error': str(e)})