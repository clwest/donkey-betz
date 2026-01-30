"""
Initiative Kickstart API
========================

Session 884: API endpoint to kickstart stuck initiatives from within Railway.

Since `railway run` executes locally (not inside Railway's container),
the Redis internal hostname doesn't resolve. This API endpoint runs
inside the deployed app where Redis is accessible.

Usage:
    # Preview (dry run)
    curl -X POST https://your-app.railway.app/api/initiatives/kickstart/ \
         -H "Authorization: Token YOUR_TOKEN" \
         -H "Content-Type: application/json" \
         -d '{"dry_run": true}'

    # Kickstart 10 initiatives
    curl -X POST https://your-app.railway.app/api/initiatives/kickstart/ \
         -H "Authorization: Token YOUR_TOKEN" \
         -H "Content-Type: application/json" \
         -d '{"limit": 10}'

    # Kickstart all
    curl -X POST https://your-app.railway.app/api/initiatives/kickstart/ \
         -H "Authorization: Token YOUR_TOKEN"
"""

import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.utils import timezone

logger = logging.getLogger(__name__)


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def kickstart_initiatives(request):
    """
    Kickstart stuck initiatives by dispatching Stage 1 tasks.

    POST/GET params:
        dry_run: bool - Preview without dispatching (default: False)
        limit: int - Max initiatives to process (default: all)
        id: str - Specific initiative ID to kickstart

    Returns:
        JSON with kickstart results
    """
    from core.models_document_registry import Initiative, InitiativeStage
    from core.services.conversation_initiative_pipeline import CONTENT_TYPE_STAGES
    from core.tasks import execute_initiative_stage_task

    # Parse params from POST body or query params
    if request.method == 'POST':
        data = request.data
    else:
        data = request.query_params

    dry_run = data.get('dry_run', False)
    if isinstance(dry_run, str):
        dry_run = dry_run.lower() in ('true', '1', 'yes')

    limit = data.get('limit')
    if limit:
        try:
            limit = int(limit)
        except (ValueError, TypeError):
            limit = None

    specific_id = data.get('id')

    result = {
        'dry_run': dry_run,
        'limit': limit,
        'initiatives_found': 0,
        'initiatives_kickstarted': 0,
        'tasks_dispatched': 0,
        'initiatives': [],
        'errors': [],
    }

    # Find stuck initiatives
    if specific_id:
        initiatives = list(Initiative.objects.filter(id=specific_id))
    else:
        initiatives = [
            i for i in Initiative.objects.filter(status='ACTIVE', current_stage=1)
            if i.stages_with_work == 0
        ]

    if limit:
        initiatives = initiatives[:limit]

    result['initiatives_found'] = len(initiatives)

    if not initiatives:
        result['message'] = 'No stuck initiatives found'
        return Response(result)

    for initiative in initiatives:
        topic = initiative.parent_topic or initiative.name
        content_type = _detect_content_type(topic)

        initiative_info = {
            'id': str(initiative.id),
            'name': initiative.name[:100],
            'content_type': content_type,
            'tasks': [],
            'status': 'pending',
        }

        # Get stage 1 tasks
        stage_config = CONTENT_TYPE_STAGES.get(content_type, CONTENT_TYPE_STAGES['document'])
        stage_1_info = stage_config.get(1, {'tasks': []})
        tasks = stage_1_info.get('tasks', []) if isinstance(stage_1_info, dict) else []

        if dry_run:
            for task_config in tasks:
                task_desc = task_config['task_template'].format(topic=topic[:50])
                initiative_info['tasks'].append({
                    'agent': task_config['agent'],
                    'task': task_desc[:100],
                    'status': 'would_dispatch',
                })
            initiative_info['status'] = 'dry_run'
            result['initiatives'].append(initiative_info)
            continue

        # Actually dispatch tasks
        try:
            # Ensure Stage 1 exists
            stage_1, created = InitiativeStage.objects.get_or_create(
                initiative=initiative,
                stage=1,
                defaults={
                    'status': 'DRAFT',
                    'notes': f'Kickstarted via API at {timezone.now().isoformat()}',
                }
            )

            if stage_1.status == 'PENDING':
                stage_1.status = 'DRAFT'
                stage_1.save()

            # Dispatch tasks
            for task_config in tasks:
                agent_name = task_config['agent']
                task_template = task_config['task_template']
                task_description = task_template.format(topic=topic)

                try:
                    async_result = execute_initiative_stage_task.delay(
                        initiative_id=str(initiative.id),
                        stage_num=1,
                        agent_name=agent_name,
                        task=task_description,
                        context={
                            'source': 'kickstart_api',
                            'topic': topic,
                            'user_id': request.user.id,
                        }
                    )

                    initiative_info['tasks'].append({
                        'agent': agent_name,
                        'task': task_description[:100],
                        'status': 'dispatched',
                        'task_id': async_result.id,
                    })
                    result['tasks_dispatched'] += 1

                except Exception as e:
                    initiative_info['tasks'].append({
                        'agent': agent_name,
                        'task': task_description[:100],
                        'status': 'failed',
                        'error': str(e),
                    })
                    result['errors'].append(f"{initiative.name[:30]}: {agent_name} - {e}")

            initiative_info['status'] = 'kickstarted'
            result['initiatives_kickstarted'] += 1

        except Exception as e:
            initiative_info['status'] = 'error'
            initiative_info['error'] = str(e)
            result['errors'].append(f"{initiative.name[:30]}: {e}")

        result['initiatives'].append(initiative_info)

    result['message'] = (
        f"{'[DRY RUN] Would kickstart' if dry_run else 'Kickstarted'} "
        f"{result['initiatives_kickstarted'] if not dry_run else result['initiatives_found']} initiatives"
    )

    logger.info(
        f"[kickstart_api] {result['message']} - "
        f"tasks={result['tasks_dispatched']}, errors={len(result['errors'])}"
    )

    return Response(result)


def _detect_content_type(topic: str) -> str:
    """Detect content type from topic text."""
    topic_lower = topic.lower()

    if any(kw in topic_lower for kw in ['persona', 'customer', 'user', 'buyer']):
        return 'strategy'
    elif any(kw in topic_lower for kw in ['plan', 'roadmap', 'timeline', 'milestone']):
        return 'plan'
    elif any(kw in topic_lower for kw in ['research', 'study', 'analysis', 'audit']):
        return 'research'
    elif any(kw in topic_lower for kw in ['content', 'blog', 'article', 'post']):
        return 'document'
    else:
        return 'strategy'  # Default
