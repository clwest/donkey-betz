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


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def fix_initiative_stages(request):
    """
    Session 884: Fix initiatives with inconsistent stage completion.

    Finds initiatives where current_stage > 1 but prior stages are still
    PENDING, and backfills them as APPROVED.

    POST/GET params:
        dry_run: bool - Preview without making changes (default: False)
        id: str - Fix a specific initiative by ID

    Returns:
        JSON with fix results
    """
    from core.models_document_registry import Initiative, InitiativeStage

    # Parse params
    if request.method == 'POST':
        data = request.data
    else:
        data = request.query_params

    dry_run = data.get('dry_run', False)
    if isinstance(dry_run, str):
        dry_run = dry_run.lower() in ('true', '1', 'yes')

    specific_id = data.get('id')

    result = {
        'dry_run': dry_run,
        'initiatives_checked': 0,
        'initiatives_fixed': 0,
        'stages_backfilled': 0,
        'fixes': [],
        'errors': [],
    }

    # Find initiatives with inconsistent stages
    if specific_id:
        initiatives = Initiative.objects.filter(id=specific_id).prefetch_related('stages')
    else:
        initiatives = Initiative.objects.filter(
            current_stage__gt=1,
            status='ACTIVE'
        ).prefetch_related('stages')

    result['initiatives_checked'] = initiatives.count()

    for initiative in initiatives:
        current_stage = initiative.current_stage
        existing_stages = {s.stage: s for s in initiative.stages.all()}

        fixes_needed = []

        # Check all stages before current_stage
        for stage_num in range(1, current_stage):
            stage = existing_stages.get(stage_num)

            if not stage:
                fixes_needed.append({
                    'stage': stage_num,
                    'action': 'create',
                    'reason': 'Stage missing',
                })
            elif stage.status in ['PENDING', 'DRAFT', 'IN_REVIEW']:
                fixes_needed.append({
                    'stage': stage_num,
                    'action': 'approve',
                    'reason': f'Stage was {stage.status}',
                })

        if not fixes_needed:
            continue

        fix_record = {
            'initiative_id': str(initiative.id),
            'initiative_name': initiative.name[:80],
            'current_stage': current_stage,
            'stages_fixed': [],
        }

        if dry_run:
            fix_record['status'] = 'would_fix'
            fix_record['stages_fixed'] = fixes_needed
            result['initiatives_fixed'] += 1
            result['stages_backfilled'] += len(fixes_needed)
            result['fixes'].append(fix_record)
            continue

        # Apply fixes
        try:
            for fix in fixes_needed:
                stage_num = fix['stage']

                if fix['action'] == 'create':
                    InitiativeStage.objects.create(
                        initiative=initiative,
                        stage=stage_num,
                        status='APPROVED',
                        approved_at=timezone.now(),
                        notes=f'Backfilled via API at {timezone.now().isoformat()}',
                    )
                elif fix['action'] == 'approve':
                    stage = existing_stages[stage_num]
                    stage.status = 'APPROVED'
                    stage.approved_at = timezone.now()
                    stage.notes = f"{stage.notes}\n\n[Backfilled via API at {timezone.now().isoformat()}]"
                    stage.save()

                fix_record['stages_fixed'].append(fix)
                result['stages_backfilled'] += 1

            fix_record['status'] = 'fixed'
            result['initiatives_fixed'] += 1

        except Exception as e:
            fix_record['status'] = 'error'
            fix_record['error'] = str(e)
            result['errors'].append(f"{initiative.name[:30]}: {e}")

        result['fixes'].append(fix_record)

    result['message'] = (
        f"{'[DRY RUN] Would fix' if dry_run else 'Fixed'} "
        f"{result['initiatives_fixed']} initiatives with "
        f"{result['stages_backfilled']} stages backfilled"
    )

    logger.info(
        f"[fix_stages_api] {result['message']} - "
        f"checked={result['initiatives_checked']}, errors={len(result['errors'])}"
    )

    return Response(result)


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def retry_stuck_initiatives(request):
    """
    Session 884: Retry stuck initiatives where Stage 1 was started but never completed.

    These are initiatives with:
    - current_stage = 1
    - stages_with_work >= 1 (Stage 1 is DRAFT)
    - But completion is still at 12% (Stage 1 never finished)

    The timeout/event loop bug (PR #591) caused tasks to fail silently.
    This endpoint re-dispatches Stage 1 tasks to retry them.

    POST/GET params:
        dry_run: bool - Preview without dispatching (default: False)
        limit: int - Max initiatives to process (default: 50)
    """
    from core.models_document_registry import Initiative, InitiativeStage
    from core.services.conversation_initiative_pipeline import CONTENT_TYPE_STAGES
    from core.tasks import execute_initiative_stage_task

    # Parse params
    if request.method == 'POST':
        data = request.data
    else:
        data = request.query_params

    dry_run = data.get('dry_run', False)
    if isinstance(dry_run, str):
        dry_run = dry_run.lower() in ('true', '1', 'yes')

    limit = int(data.get('limit', 50))

    result = {
        'dry_run': dry_run,
        'limit': limit,
        'initiatives_found': 0,
        'initiatives_retried': 0,
        'tasks_dispatched': 0,
        'initiatives': [],
        'errors': [],
    }

    # Find stuck initiatives: Stage 1 started (DRAFT) but not progressing
    stuck_initiatives = []
    for initiative in Initiative.objects.filter(status='ACTIVE', current_stage=1):
        # Check if Stage 1 exists and is in DRAFT or IN_REVIEW (started but not approved)
        stage_1 = InitiativeStage.objects.filter(initiative=initiative, stage=1).first()
        if stage_1 and stage_1.status in ['DRAFT', 'IN_REVIEW']:
            stuck_initiatives.append(initiative)

    stuck_initiatives = stuck_initiatives[:limit]
    result['initiatives_found'] = len(stuck_initiatives)

    if not stuck_initiatives:
        result['message'] = 'No stuck initiatives found (Stage 1 started but not completing)'
        return Response(result)

    for initiative in stuck_initiatives:
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
                    'status': 'would_retry',
                })
            initiative_info['status'] = 'dry_run'
            result['initiatives'].append(initiative_info)
            continue

        # Re-dispatch Stage 1 tasks
        try:
            # Reset Stage 1 to DRAFT (allow re-processing)
            stage_1 = InitiativeStage.objects.get(initiative=initiative, stage=1)
            stage_1.status = 'DRAFT'
            stage_1.notes = f"{stage_1.notes}\n\n[Retried via API at {timezone.now().isoformat()}]"
            stage_1.save()

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
                            'source': 'retry_stuck_api',
                            'topic': topic,
                            'user_id': request.user.id,
                            'retry': True,
                        }
                    )

                    initiative_info['tasks'].append({
                        'agent': agent_name,
                        'task': task_description[:100],
                        'status': 'retried',
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

            initiative_info['status'] = 'retried'
            result['initiatives_retried'] += 1

        except Exception as e:
            initiative_info['status'] = 'error'
            initiative_info['error'] = str(e)
            result['errors'].append(f"{initiative.name[:30]}: {e}")

        result['initiatives'].append(initiative_info)

    result['message'] = (
        f"{'[DRY RUN] Would retry' if dry_run else 'Retried'} "
        f"{result['initiatives_retried'] if not dry_run else result['initiatives_found']} stuck initiatives "
        f"with {result['tasks_dispatched']} tasks dispatched"
    )

    logger.info(
        f"[retry_stuck_api] {result['message']} - "
        f"found={result['initiatives_found']}, errors={len(result['errors'])}"
    )

    return Response(result)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def initiative_circuit_breaker(request):
    """
    Session 884: Circuit breaker API for initiative creation.

    GET: Returns current circuit breaker status
    POST: Pause or resume initiative creation

    POST params:
        action: 'pause' or 'resume'
        reason: Optional reason for pausing

    Example:
        # Check status
        curl -X GET https://your-app.railway.app/api/initiatives/circuit-breaker/ \
             -H "Authorization: Token YOUR_TOKEN"

        # Pause creation
        curl -X POST https://your-app.railway.app/api/initiatives/circuit-breaker/ \
             -H "Authorization: Token YOUR_TOKEN" \
             -H "Content-Type: application/json" \
             -d '{"action": "pause", "reason": "Clearing backlog"}'

        # Resume creation
        curl -X POST https://your-app.railway.app/api/initiatives/circuit-breaker/ \
             -H "Authorization: Token YOUR_TOKEN" \
             -H "Content-Type: application/json" \
             -d '{"action": "resume"}'
    """
    from core.services.initiative_circuit_breaker import (
        get_backlog_status,
        pause_initiative_creation,
        resume_initiative_creation,
    )

    if request.method == 'GET':
        status = get_backlog_status()
        return Response({
            'status': 'paused' if not status['can_create'] else 'active',
            **status,
        })

    # POST - pause or resume
    data = request.data
    action = data.get('action', '').lower()

    if action == 'pause':
        reason = data.get('reason', f'Paused via API by user {request.user.id}')
        success = pause_initiative_creation(reason)
        if success:
            return Response({
                'success': True,
                'message': 'Initiative creation PAUSED',
                'reason': reason,
                **get_backlog_status(),
            })
        else:
            return Response({
                'success': False,
                'error': 'Failed to pause - check logs',
            }, status=500)

    elif action == 'resume':
        success = resume_initiative_creation()
        if success:
            return Response({
                'success': True,
                'message': 'Initiative creation RESUMED',
                **get_backlog_status(),
            })
        else:
            return Response({
                'success': False,
                'error': 'Failed to resume - check logs',
            }, status=500)

    else:
        return Response({
            'error': f"Invalid action: '{action}'. Use 'pause' or 'resume'.",
            'current_status': get_backlog_status(),
        }, status=400)


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def cleanup_initiatives(request):
    """
    Session 884: Cleanup stuck initiatives by archiving or deleting them.

    GET: Preview what would be cleaned up
    POST: Execute cleanup

    POST params:
        action: 'archive' or 'delete' (default: archive)
        max_completion: Archive/delete initiatives at or below this % (default: 12)
        status_filter: Only affect initiatives with this status (default: ACTIVE)
        dry_run: Preview without making changes (default: False)

    Example:
        # Preview cleanup
        curl -X GET https://your-app.railway.app/api/initiatives/cleanup/ \
             -H "Authorization: Token YOUR_TOKEN"

        # Archive all stuck initiatives (<=12% completion)
        curl -X POST https://your-app.railway.app/api/initiatives/cleanup/ \
             -H "Authorization: Token YOUR_TOKEN" \
             -H "Content-Type: application/json" \
             -d '{"action": "archive"}'

        # Delete all stuck initiatives
        curl -X POST https://your-app.railway.app/api/initiatives/cleanup/ \
             -H "Authorization: Token YOUR_TOKEN" \
             -H "Content-Type: application/json" \
             -d '{"action": "delete", "max_completion": 12}'
    """
    from core.models_document_registry import Initiative, InitiativeStage

    # Parse params
    if request.method == 'POST':
        data = request.data
    else:
        data = request.query_params

    action = data.get('action', 'archive').lower()
    max_completion = int(data.get('max_completion', 12))
    status_filter = data.get('status_filter', 'ACTIVE')
    dry_run = data.get('dry_run', request.method == 'GET')
    if isinstance(dry_run, str):
        dry_run = dry_run.lower() in ('true', '1', 'yes')

    result = {
        'action': action,
        'max_completion': max_completion,
        'status_filter': status_filter,
        'dry_run': dry_run,
        'initiatives_found': 0,
        'initiatives_affected': 0,
        'stages_deleted': 0,
        'errors': [],
    }

    if action not in ('archive', 'delete'):
        return Response({
            'error': f"Invalid action: '{action}'. Use 'archive' or 'delete'.",
        }, status=400)

    # Find initiatives to clean up
    initiatives = Initiative.objects.filter(status=status_filter)

    # Filter by completion percentage
    to_cleanup = []
    for initiative in initiatives:
        if initiative.completion_percentage <= max_completion:
            to_cleanup.append(initiative)

    result['initiatives_found'] = len(to_cleanup)

    if dry_run:
        # Preview mode - show what would be affected
        result['message'] = f"[DRY RUN] Would {action} {len(to_cleanup)} initiatives"
        result['preview'] = [
            {
                'id': str(i.id),
                'name': i.name[:80],
                'completion': i.completion_percentage,
                'stage': i.current_stage,
            }
            for i in to_cleanup[:20]  # Limit preview to 20
        ]
        if len(to_cleanup) > 20:
            result['preview_note'] = f"Showing 20 of {len(to_cleanup)} initiatives"
        return Response(result)

    # Execute cleanup
    for initiative in to_cleanup:
        try:
            if action == 'archive':
                initiative.status = 'ARCHIVED'
                initiative.save(update_fields=['status', 'updated_at'])
                result['initiatives_affected'] += 1
            elif action == 'delete':
                # Delete related stages first
                stages_count = InitiativeStage.objects.filter(initiative=initiative).count()
                InitiativeStage.objects.filter(initiative=initiative).delete()
                result['stages_deleted'] += stages_count
                # Delete initiative
                initiative.delete()
                result['initiatives_affected'] += 1
        except Exception as e:
            result['errors'].append(f"{initiative.name[:30]}: {str(e)}")

    result['message'] = (
        f"{'Archived' if action == 'archive' else 'Deleted'} "
        f"{result['initiatives_affected']} initiatives"
    )

    if action == 'delete':
        result['message'] += f" and {result['stages_deleted']} stages"

    logger.info(
        f"[cleanup_api] {result['message']} - "
        f"found={result['initiatives_found']}, errors={len(result['errors'])}"
    )

    return Response(result)
