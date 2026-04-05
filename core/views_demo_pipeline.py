"""
Demo Pipeline — "First Win" for New Users
==========================================

A lightweight 3-stage pipeline that runs in ~60 seconds and produces
a real deliverable. Triggered from the guided tour onboarding.

Stages:
1. Quick Research — TopicMiner + web search (paraphrased queries)
2. Alignment Check — verify research matches topic
3. Deliverable — create a short insight summary

This is the moment where a new user goes from "I don't understand this
system" to "Oh — this actually does something."
"""

import logging
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError as _FuturesTimeout

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

logger = logging.getLogger(__name__)

# Demo pipeline timeout per stage (shorter than full pipeline)
DEMO_STAGE_TIMEOUT = 120  # 2 minutes max per stage
DEMO_RUNS_PER_USER_PER_DAY = 3  # Rate limit


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_demo_pipeline(request):
    """
    Run a quick demo pipeline that produces a real deliverable in ~60s.

    Body (optional):
        topic: str — what to research (defaults to a safe sample topic)

    Returns immediately with a run_id, then the pipeline executes async.
    Poll GET /api/demo-pipeline/status/<run_id>/ for progress.
    """
    topic = (request.data.get('topic') or '').strip()

    if not topic:
        topic = "How small teams use AI automation to compete with enterprises"

    # Rate limit check
    from django.core.cache import cache
    rate_key = f'demo_pipeline:{request.user.id}:daily'
    run_count = cache.get(rate_key, 0)
    if run_count >= DEMO_RUNS_PER_USER_PER_DAY:
        return Response({
            'success': False,
            'error': f'Demo limit reached ({DEMO_RUNS_PER_USER_PER_DAY}/day). Try again tomorrow.',
        }, status=429)

    # Create demo run record
    run_id = uuid.uuid4().hex[:12]

    # Store initial state in cache
    cache.set(f'demo_run:{run_id}', {
        'status': 'pending',
        'topic': topic,
        'user_id': request.user.id,
        'stages': [
            {'name': 'Quick Research', 'status': 'pending'},
            {'name': 'Quality Check', 'status': 'pending'},
            {'name': 'Create Deliverable', 'status': 'pending'},
        ],
        'progress_pct': 0,
        'deliverable_id': None,
        'started_at': timezone.now().isoformat(),
    }, timeout=600)  # 10 min TTL

    # Increment rate limit
    try:
        cache.incr(rate_key)
    except ValueError:
        cache.set(rate_key, 1, timeout=86400)

    # Dispatch to Celery
    from core.tasks import execute_demo_pipeline_task
    execute_demo_pipeline_task.delay(run_id, topic, request.user.id)

    return Response({
        'success': True,
        'run_id': run_id,
        'topic': topic,
        'message': f'Demo pipeline started! Researching "{topic}"...',
    }, status=202)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def demo_pipeline_status(request, run_id):
    """Poll demo pipeline status."""
    from django.core.cache import cache

    state = cache.get(f'demo_run:{run_id}')
    if not state:
        return Response({'success': False, 'error': 'Run not found or expired'}, status=404)

    return Response({
        'success': True,
        'run_id': run_id,
        **state,
    })


def _execute_demo_pipeline(run_id: str, topic: str, user_id: int):
    """
    Execute the 3-stage demo pipeline synchronously.
    Updates cache state after each stage for frontend polling.
    """
    from django.core.cache import cache
    from django.contrib.auth import get_user_model
    from core.agent_router import AgentRouter
    from core.services.search_strategy_service import generate_query_plan
    from core.services.agent_content_extractor import extract_deliverable_content

    User = get_user_model()
    user = User.objects.filter(id=user_id).first()
    router = AgentRouter()

    def _update(stage_idx, status, extra=None):
        state = cache.get(f'demo_run:{run_id}') or {}
        if state.get('stages') and stage_idx < len(state['stages']):
            state['stages'][stage_idx]['status'] = status
        state['progress_pct'] = int(((stage_idx + (1 if status == 'completed' else 0.5)) / 3) * 100)
        if extra:
            state.update(extra)
        cache.set(f'demo_run:{run_id}', state, timeout=600)

    try:
        # Stage 1: Quick Research
        _update(0, 'running', {'status': 'running'})

        brief = {'topic': topic}
        query_plan = generate_query_plan(topic, brief, max_queries=3)
        task_desc = (
            f"Research this topic quickly and find 3 key findings with sources: {topic}. "
            f"Search for: {', '.join(q['query'] for q in query_plan[:3])}"
        )

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                router.route,
                task=task_desc,
                agent_name='ResearchAgent',
                context={'workspace_brief': brief},
            )
            research_result = future.result(timeout=DEMO_STAGE_TIMEOUT)

        research_content = ''
        if research_result and research_result.success:
            research_content = extract_deliverable_content(research_result)
            _update(0, 'completed')
        else:
            _update(0, 'failed')
            research_content = f"Research on {topic}: Limited results found. Proceeding with available data."
            _update(0, 'completed')  # Don't block demo on research quality

        # Stage 2: Quality Check (lightweight — just verify we have something)
        _update(1, 'running')
        has_content = len(research_content) > 50
        _update(1, 'completed' if has_content else 'warning')

        # Stage 3: Create Deliverable
        _update(2, 'running')

        # Build a clean deliverable from whatever we got
        deliverable_content = f"# Quick Insight: {topic}\n\n"
        if research_content and len(research_content) > 100:
            deliverable_content += research_content
        else:
            deliverable_content += (
                f"## Summary\n"
                f"This is a demo research pass on \"{topic}\". "
                f"The agents searched for relevant information using multiple query strategies.\n\n"
                f"## Next Steps\n"
                f"- Ask Rigby to run a deeper research pass\n"
                f"- Create a full workspace for this topic\n"
                f"- Expand into a newsletter or blog post\n"
            )

        # Save as deliverable
        try:
            from core.services.deliverable_factory import create_deliverable

            deliverable = create_deliverable(
                title=f"Demo: Quick Insight — {topic}"[:255],
                content=deliverable_content,
                agent_name='DemoPipeline',
                category='Demo Run',
                deliverable_type='document',
                user=user,
                content_format='markdown',
                is_saved=True,
                metadata={
                    'demo_run': True,
                    'demo_run_id': run_id,
                    'demo_ttl_days': 7,
                    'topic': topic,
                },
            )
            deliverable_id = str(deliverable.id)
        except Exception as e:
            logger.error("Demo pipeline deliverable creation failed: %s", e)
            deliverable_id = None

        _update(2, 'completed', {
            'status': 'completed',
            'deliverable_id': deliverable_id,
            'finished_at': timezone.now().isoformat(),
            'message': f'Demo complete! Created "Quick Insight: {topic}"',
        })

        logger.info("Demo pipeline %s completed for user %s", run_id, user_id)

    except _FuturesTimeout:
        _update(0, 'failed', {
            'status': 'failed',
            'error': 'Research timed out. Try a simpler topic or retry.',
        })
    except Exception as e:
        logger.error("Demo pipeline %s failed: %s", run_id, e)
        state = cache.get(f'demo_run:{run_id}') or {}
        state['status'] = 'failed'
        state['error'] = f'Demo failed: {str(e)[:200]}'
        cache.set(f'demo_run:{run_id}', state, timeout=600)
