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
                    # Session 916: Create stage with audit logging
                    from core.models_document_registry import StageTransitionLog
                    new_stage = InitiativeStage.objects.create(
                        initiative=initiative,
                        stage=stage_num,
                        status='APPROVED',
                        approved_at=timezone.now(),
                        approved_by='backfill_api',
                        notes=f'Backfilled via API at {timezone.now().isoformat()}',
                    )
                    StageTransitionLog.log_transition(
                        stage=new_stage,
                        from_status='CREATED',
                        to_status='APPROVED',
                        triggered_by='backfill_api',
                        trigger_type='api',
                        notes='Created via kickstart backfill API'
                    )
                elif fix['action'] == 'approve':
                    # Session 916: Use approve() method with invariant enforcement
                    stage = existing_stages[stage_num]

                    # Only approve if stage has a document (invariant enforcement)
                    if not stage.document:
                        fix_record['stages_fixed'].append({
                            'stage': stage_num,
                            'action': 'skipped',
                            'reason': 'Cannot approve without document'
                        })
                        continue

                    stage.approve(
                        approved_by='backfill_api',
                        notes=f'Approved via kickstart backfill API at {timezone.now().isoformat()}',
                        checks_passed={
                            'has_document': True,
                            'backfill_action': True,
                        }
                    )

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


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def backfill_stage_documents(request):
    """
    Session 915: Trigger backfill of missing stage documents.

    Since `railway run` executes locally (can't reach Redis internal network),
    this API endpoint triggers the Celery task from within Railway's container.

    POST/GET params:
        stage: int - Stage number to backfill (default: 1)
        limit: int - Max initiatives to process (default: 50)
        dry_run: bool - Preview without triggering (default: False)

    Example:
        # Dry run
        curl -X POST https://your-app.railway.app/api/initiatives/backfill-documents/ \
             -H "Authorization: Token YOUR_TOKEN" \
             -d '{"dry_run": true}'

        # Backfill Stage 1 documents
        curl -X POST https://your-app.railway.app/api/initiatives/backfill-documents/ \
             -H "Authorization: Token YOUR_TOKEN" \
             -d '{"stage": 1, "limit": 50}'
    """
    from core.models_document_registry import Initiative, InitiativeStage
    from core.tasks import backfill_stage_documents as backfill_task

    # Parse params
    if request.method == 'POST':
        data = request.data
    else:
        data = request.query_params

    stage_num = int(data.get('stage', 1))
    limit = int(data.get('limit', 50))

    dry_run = data.get('dry_run', False)
    if isinstance(dry_run, str):
        dry_run = dry_run.lower() in ('true', '1', 'yes')

    result = {
        'stage': stage_num,
        'limit': limit,
        'dry_run': dry_run,
        'initiatives_found': 0,
        'task_id': None,
        'preview': [],
    }

    # Find initiatives missing documents for this stage
    all_initiatives = Initiative.objects.filter(
        current_stage__gte=stage_num
    ).order_by('-created_at')[:limit * 2]

    initiatives_needing_docs = []
    for initiative in all_initiatives:
        stage = InitiativeStage.objects.filter(
            initiative=initiative,
            stage=stage_num
        ).first()

        if stage and not stage.document:
            initiatives_needing_docs.append(initiative)

        if len(initiatives_needing_docs) >= limit:
            break

    result['initiatives_found'] = len(initiatives_needing_docs)

    if dry_run:
        result['message'] = f"[DRY RUN] Would backfill Stage {stage_num} documents for {len(initiatives_needing_docs)} initiatives"
        result['preview'] = [
            {
                'id': str(i.id),
                'name': i.name[:80],
                'stage': i.current_stage,
            }
            for i in initiatives_needing_docs[:20]
        ]
        if len(initiatives_needing_docs) > 20:
            result['preview_note'] = f"Showing 20 of {len(initiatives_needing_docs)} initiatives"
        return Response(result)

    if not initiatives_needing_docs:
        result['message'] = f"No initiatives need Stage {stage_num} document backfill"
        return Response(result)

    # Trigger the Celery task
    try:
        async_result = backfill_task.delay(stage_num=stage_num, limit=limit)
        result['task_id'] = async_result.id
        result['message'] = (
            f"Triggered backfill task for {len(initiatives_needing_docs)} initiatives "
            f"(task_id: {async_result.id})"
        )
        logger.info(
            f"[backfill_api] {result['message']}"
        )
    except Exception as e:
        result['error'] = str(e)
        result['message'] = f"Failed to trigger backfill task: {e}"
        logger.error(f"[backfill_api] {result['message']}")

    return Response(result)


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def fix_initiative_titles(request):
    """
    Session 916: Fix messy initiative titles using smart title generation.

    POST/GET params:
        limit: int - Max initiatives to process (default: 50)
        dry_run: bool - Preview without making changes (default: True)

    Example:
        # Dry run
        curl -X GET "https://your-app.railway.app/api/initiatives/fix-titles/?limit=20"

        # Actually fix titles
        curl -X POST "https://your-app.railway.app/api/initiatives/fix-titles/" \\
             -H "Authorization: Token YOUR_TOKEN" \\
             -d '{"dry_run": false, "limit": 50}'
    """
    from core.models_document_registry import Initiative
    from core.services.initiative_title_generator import generate_initiative_title, _is_valid_title
    from django.db import transaction

    # Parse params
    if request.method == 'POST':
        data = request.data
    else:
        data = request.query_params

    limit = int(data.get('limit', 50))
    dry_run = data.get('dry_run', True)
    if isinstance(dry_run, str):
        dry_run = dry_run.lower() not in ('false', '0', 'no')

    result = {
        'limit': limit,
        'dry_run': dry_run,
        'total_analyzed': 0,
        'bad_titles_found': 0,
        'fixed': 0,
        'errors': 0,
        'preview': [],
    }

    try:
        # Find initiatives with bad titles
        initiatives = Initiative.objects.all().order_by('-created_at')[:limit]

        bad_titles = []
        for init in initiatives:
            result['total_analyzed'] += 1
            if not _is_valid_title(init.name, max_length=80):
                bad_titles.append(init)

        result['bad_titles_found'] = len(bad_titles)

        # Generate new titles
        for init in bad_titles[:20]:  # Preview max 20
            content = init.description or ""
            topic_hint = init.parent_topic or ""

            new_title = generate_initiative_title(
                content=content,
                topic_hint=topic_hint,
                max_length=80,
                use_llm=True
            )

            preview_item = {
                'id': str(init.id),
                'old_title': init.name[:60] + '...' if len(init.name) > 60 else init.name,
                'new_title': new_title,
            }
            result['preview'].append(preview_item)

            if not dry_run:
                try:
                    with transaction.atomic():
                        init.name = new_title
                        init.save(update_fields=['name'])
                        result['fixed'] += 1
                except Exception as e:
                    result['errors'] += 1
                    logger.error(f"[fix_titles_api] Error fixing {init.id}: {e}")

        if dry_run:
            result['message'] = f"[DRY RUN] Would fix {result['bad_titles_found']} titles"
        else:
            result['message'] = f"Fixed {result['fixed']} titles ({result['errors']} errors)"

        logger.info(f"[fix_titles_api] {result['message']}")

    except Exception as e:
        result['error'] = str(e)
        result['message'] = f"Failed to fix titles: {e}"
        logger.error(f"[fix_titles_api] {result['message']}")

    return Response(result)


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def reset_premature_completed(request):
    """
    Session 920: Reset prematurely-completed initiatives back to ACTIVE.

    Finds initiatives marked as COMPLETED but with < 100% approved stages
    and resets them to ACTIVE status.

    Usage:
        # Preview (GET or dry_run=true)
        curl -X GET "https://donkey-betz-platform-production.up.railway.app/api/initiatives/reset-premature-completed/"

        # Execute reset
        curl -X POST "https://donkey-betz-platform-production.up.railway.app/api/initiatives/reset-premature-completed/" \\
             -H "Content-Type: application/json" \\
             -d '{"dry_run": false}'

        # Reset with minimum threshold (only reset if < 60% approved)
        curl -X POST "https://donkey-betz-platform-production.up.railway.app/api/initiatives/reset-premature-completed/" \\
             -H "Content-Type: application/json" \\
             -d '{"dry_run": false, "threshold": 60}'

    POST/GET params:
        dry_run: bool - Preview without resetting (default: True for safety)
        threshold: int - Only reset if approved_percentage < threshold (default: 100)

    Returns:
        JSON with reset results
    """
    from core.models_document_registry import Initiative
    from django.db import transaction

    # Parse parameters
    if request.method == 'GET':
        dry_run = True
        threshold = int(request.GET.get('threshold', 100))
    else:
        data = request.data if hasattr(request, 'data') else {}
        dry_run = data.get('dry_run', True)
        threshold = int(data.get('threshold', 100))

    result = {
        'dry_run': dry_run,
        'threshold': threshold,
        'premature_completed_found': 0,
        'reset_count': 0,
        'errors': 0,
        'initiatives': [],
        'message': '',
    }

    try:
        # Find COMPLETED initiatives
        completed_initiatives = Initiative.objects.filter(status='COMPLETED')
        result['total_completed'] = completed_initiatives.count()

        # Check each one for premature completion
        premature = []
        for init in completed_initiatives:
            # Calculate approved percentage
            stages = list(init.stages.all())
            approved_count = sum(1 for s in stages if s.status == 'APPROVED')
            approved_pct = int((approved_count / 5) * 100) if stages else 0

            if approved_pct < threshold:
                premature.append({
                    'initiative': init,
                    'approved_pct': approved_pct,
                    'approved_count': approved_count,
                    'stages_with_work': sum(1 for s in stages if s.status != 'PENDING'),
                })

        result['premature_completed_found'] = len(premature)

        # Reset them
        for item in premature:
            init = item['initiative']
            preview = {
                'id': str(init.id),
                'name': init.name[:60] + '...' if len(init.name) > 60 else init.name,
                'approved_pct': item['approved_pct'],
                'stages_with_work': item['stages_with_work'],
                'status': 'will_reset' if not dry_run else 'would_reset',
            }

            if not dry_run:
                try:
                    with transaction.atomic():
                        init.status = 'ACTIVE'
                        init.save(update_fields=['status', 'updated_at'])
                        result['reset_count'] += 1
                        preview['status'] = 'reset_to_active'
                except Exception as e:
                    result['errors'] += 1
                    preview['status'] = f'error: {str(e)}'
                    logger.error(f"[reset_premature] Error resetting {init.id}: {e}")

            result['initiatives'].append(preview)

        if dry_run:
            result['message'] = f"[DRY RUN] Found {len(premature)} prematurely-completed initiatives (< {threshold}% approved). POST with dry_run=false to reset."
        else:
            result['message'] = f"Reset {result['reset_count']} initiatives to ACTIVE ({result['errors']} errors)"

        logger.info(f"[reset_premature] {result['message']}")

    except Exception as e:
        result['error'] = str(e)
        result['message'] = f"Failed to reset initiatives: {e}"
        logger.error(f"[reset_premature] {result['message']}")

    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pipeline_health(request):
    """
    Session 921: Real-time pipeline health monitoring.

    Shows whether initiatives are actually making progress through the pipeline,
    with recent activity, stale detection, and stage distribution.

    GET params:
        stale_hours: int - Hours without activity to consider stale (default: 48)
        transition_limit: int - Max recent transitions to return (default: 50)

    Returns:
        JSON with pipeline health metrics
    """
    from core.models_document_registry import Initiative, InitiativeStage, StageTransitionLog
    from django.db.models import Count, Max, Q, F
    from django.db.models.functions import Now
    from datetime import timedelta

    stale_hours = int(request.GET.get('stale_hours', 168))
    transition_limit = int(request.GET.get('transition_limit', 50))

    now = timezone.now()
    stale_threshold = now - timedelta(hours=stale_hours)
    last_24h = now - timedelta(hours=24)
    last_1h = now - timedelta(hours=1)

    result = {
        'generated_at': now.isoformat(),
        'stale_threshold_hours': stale_hours,
        'summary': {},
        'recent_transitions': [],
        'stale_initiatives': [],
        'stage_distribution': {},
        'hourly_activity': [],
        'health_status': 'unknown',
    }

    try:
        # === SUMMARY STATS ===
        active_initiatives = Initiative.objects.filter(status='ACTIVE')
        active_count = active_initiatives.count()

        # Count initiatives that had transitions in last 24h
        initiatives_with_recent_activity = StageTransitionLog.objects.filter(
            timestamp__gte=last_24h,
            stage__initiative__status='ACTIVE'
        ).values('stage__initiative').distinct().count()

        # Count transitions in last 24h and 1h
        transitions_24h = StageTransitionLog.objects.filter(timestamp__gte=last_24h).count()
        transitions_1h = StageTransitionLog.objects.filter(timestamp__gte=last_1h).count()

        # Count approvals (actual progress) in last 24h
        approvals_24h = StageTransitionLog.objects.filter(
            timestamp__gte=last_24h,
            to_status='APPROVED'
        ).count()

        result['summary'] = {
            'active_count': active_count,
            'moved_last_24h': initiatives_with_recent_activity,
            'transitions_last_24h': transitions_24h,
            'transitions_last_1h': transitions_1h,
            'approvals_last_24h': approvals_24h,
            'stale_count': 0,  # Will be calculated below
            'blocked_count': InitiativeStage.objects.filter(
                initiative__status='ACTIVE',
                status='BLOCKED'
            ).values('initiative').distinct().count(),
        }

        # === RECENT TRANSITIONS (the activity feed) ===
        recent_logs = StageTransitionLog.objects.select_related(
            'stage', 'stage__initiative'
        ).order_by('-timestamp')[:transition_limit]

        for log in recent_logs:
            result['recent_transitions'].append({
                'id': str(log.id),
                'initiative_id': str(log.stage.initiative.id),
                'initiative_name': log.stage.initiative.name[:60] + ('...' if len(log.stage.initiative.name) > 60 else ''),
                'stage_number': log.stage.stage,
                'from_status': log.from_status,
                'to_status': log.to_status,
                'timestamp': log.timestamp.isoformat(),
                'time_ago': _format_time_ago(log.timestamp, now),
                'triggered_by': log.triggered_by,
                'trigger_type': log.trigger_type,
                'quality_score': log.quality_score,
                'had_error': log.had_error,
            })

        # === STALE INITIATIVES ===
        # Find active initiatives with no recent transitions
        # Get last activity time for each active initiative
        initiative_last_activity = {}

        # First, get all transition timestamps for active initiatives
        active_ids = list(active_initiatives.values_list('id', flat=True)[:500])

        for init_id in active_ids:
            last_log = StageTransitionLog.objects.filter(
                stage__initiative_id=init_id
            ).order_by('-timestamp').first()

            if last_log:
                initiative_last_activity[init_id] = last_log.timestamp
            else:
                # No transitions logged - use initiative updated_at
                init = Initiative.objects.get(id=init_id)
                initiative_last_activity[init_id] = init.updated_at

        # Find stale ones
        stale_initiatives = []
        for init_id, last_activity in initiative_last_activity.items():
            if last_activity < stale_threshold:
                init = Initiative.objects.get(id=init_id)
                days_stale = (now - last_activity).total_seconds() / 86400
                stale_initiatives.append({
                    'id': str(init_id),
                    'name': init.name[:60] + ('...' if len(init.name) > 60 else ''),
                    'current_stage': init.current_stage,
                    'last_activity': last_activity.isoformat(),
                    'days_stale': round(days_stale, 1),
                    'completion_pct': init.completion_percentage,
                })

        # Sort by most stale first
        stale_initiatives.sort(key=lambda x: x['days_stale'], reverse=True)
        result['stale_initiatives'] = stale_initiatives[:100]
        result['summary']['stale_count'] = len(stale_initiatives)

        # === STAGE DISTRIBUTION ===
        # Session 943: Fix to show initiatives AT each stage (by current_stage),
        # not just the stage entry status. Previous bug showed 436 for all stages
        # because every initiative has 5 stage entries.
        stage_dist = {}
        for stage_num in range(1, 6):
            # Count initiatives WHERE current_stage == stage_num
            initiatives_at_stage = Initiative.objects.filter(
                status='ACTIVE',
                current_stage=stage_num
            )
            count_at_stage = initiatives_at_stage.count()

            # Get the status breakdown of stage entries for those initiatives
            stage_counts = InitiativeStage.objects.filter(
                initiative__in=initiatives_at_stage,
                stage=stage_num
            ).values('status').annotate(count=Count('id'))

            stage_dist[f'stage_{stage_num}'] = {
                'count': count_at_stage,  # Main number: how many ARE at this stage
                **{
                    item['status'].lower(): item['count']
                    for item in stage_counts
                }
            }

        result['stage_distribution'] = stage_dist

        # === HOURLY ACTIVITY (last 24 hours) ===
        hourly = []
        for hours_ago in range(24):
            start = now - timedelta(hours=hours_ago + 1)
            end = now - timedelta(hours=hours_ago)
            count = StageTransitionLog.objects.filter(
                timestamp__gte=start,
                timestamp__lt=end
            ).count()
            hourly.append({
                'hour': hours_ago,
                'label': f'{hours_ago}h ago',
                'transitions': count,
            })
        result['hourly_activity'] = hourly

        # === HEALTH STATUS ===
        # Determine overall pipeline health
        if transitions_1h >= 3:
            result['health_status'] = 'healthy'
            result['health_message'] = f'Pipeline is active: {transitions_1h} transitions in last hour'
        elif transitions_24h >= 10:
            result['health_status'] = 'moderate'
            result['health_message'] = f'Pipeline is moving: {transitions_24h} transitions in last 24h'
        elif transitions_24h > 0:
            result['health_status'] = 'slow'
            result['health_message'] = f'Pipeline is slow: only {transitions_24h} transitions in last 24h'
        else:
            result['health_status'] = 'stalled'
            result['health_message'] = 'Pipeline appears stalled: no transitions in 24h'

        # Add stale warning — only critical if stale AND blocked or zero week activity
        stale_pct = (len(stale_initiatives) / active_count * 100) if active_count > 0 else 0
        blocked_count = result['summary'].get('blocked_count', 0)
        week_transitions = StageTransitionLog.objects.filter(
            timestamp__gte=now - timedelta(days=7)
        ).count()
        if stale_pct > 50 and (blocked_count > 0 or week_transitions == 0):
            result['health_status'] = 'critical'
            result['health_message'] = f'CRITICAL: {len(stale_initiatives)} initiatives ({stale_pct:.0f}%) stale, {blocked_count} blocked, {week_transitions} transitions in 7d'
        elif stale_pct > 50:
            result['health_status'] = 'attention'
            result['health_message'] = f'{len(stale_initiatives)} initiatives ({stale_pct:.0f}%) have no activity in {stale_hours}+ hours'

    except Exception as e:
        result['error'] = str(e)
        result['health_status'] = 'error'
        result['health_message'] = f'Error fetching pipeline health: {e}'
        logger.error(f"[pipeline_health] Error: {e}")

    return Response(result)


def _format_time_ago(timestamp, now):
    """Format a timestamp as human-readable time ago."""
    delta = now - timestamp
    seconds = delta.total_seconds()

    if seconds < 60:
        return 'just now'
    elif seconds < 3600:
        mins = int(seconds / 60)
        return f'{mins}m ago'
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f'{hours}h ago'
    else:
        days = int(seconds / 86400)
        return f'{days}d ago'


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def diagnose_stuck_initiatives(request):
    """
    Session 921: Diagnose why initiatives are stuck and not auto-progressing.

    Checks each DRAFT stage to identify exactly what's blocking progression:
    - Missing document
    - Document too short
    - Missing required sections
    - Founder intent not set
    - Quality check failure

    GET params:
        limit: int - Max initiatives to check (default: 50)
        stage: int - Only check specific stage (default: all)

    Returns:
        JSON with diagnostic breakdown
    """
    from core.models_document_registry import Initiative, InitiativeStage
    from core.services.initiative_auto_progression import (
        evaluate_stage_quality,
        STAGE_QUALITY_THRESHOLDS,
        get_daily_progression_stats
    )

    limit = int(request.GET.get('limit', 50))
    stage_filter = request.GET.get('stage')

    result = {
        'generated_at': timezone.now().isoformat(),
        'rate_limit_stats': get_daily_progression_stats(),
        'summary': {
            'total_checked': 0,
            'no_document': 0,
            'quality_failed': 0,
            'founder_intent_missing': 0,
            'ready_to_progress': 0,
        },
        'blocking_reasons': {},
        'initiatives': [],
    }

    try:
        # Get DRAFT stages
        draft_filter = {'status': 'DRAFT', 'initiative__status': 'ACTIVE'}
        if stage_filter:
            draft_filter['stage'] = int(stage_filter)

        draft_stages = InitiativeStage.objects.filter(
            **draft_filter
        ).select_related('initiative', 'document').order_by('initiative__name')[:limit]

        for stage in draft_stages:
            result['summary']['total_checked'] += 1
            initiative = stage.initiative

            diagnosis = {
                'id': str(initiative.id),
                'name': initiative.name[:60] + ('...' if len(initiative.name) > 60 else ''),
                'stage': stage.stage,
                'blockers': [],
                'can_progress': True,
            }

            # Check 1: Founder intent
            if not initiative.founder_intent_set:
                diagnosis['blockers'].append('founder_intent_not_set')
                diagnosis['can_progress'] = False
                result['summary']['founder_intent_missing'] += 1

            # Check 2: Document exists
            if not stage.document:
                diagnosis['blockers'].append('no_document')
                diagnosis['can_progress'] = False
                result['summary']['no_document'] += 1
            else:
                # Check 3: Quality evaluation
                passes, confidence, reason = evaluate_stage_quality(stage)
                diagnosis['quality_check'] = {
                    'passes': passes,
                    'confidence': f'{confidence:.0%}',
                    'reason': reason,
                }

                if not passes or confidence < 0.6:
                    diagnosis['blockers'].append(f'quality_check: {reason}')
                    diagnosis['can_progress'] = False
                    result['summary']['quality_failed'] += 1

            # Track blocking reasons
            for blocker in diagnosis['blockers']:
                key = blocker.split(':')[0].strip()
                result['blocking_reasons'][key] = result['blocking_reasons'].get(key, 0) + 1

            if diagnosis['can_progress']:
                result['summary']['ready_to_progress'] += 1

            result['initiatives'].append(diagnosis)

        # Sort by most common blocker
        result['blocking_reasons'] = dict(
            sorted(result['blocking_reasons'].items(), key=lambda x: x[1], reverse=True)
        )

    except Exception as e:
        result['error'] = str(e)
        logger.error(f"[diagnose_stuck] Error: {e}")

    return Response(result)


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def trigger_stage_backfill(request):
    """
    Session 921: Trigger Stage 1 document generation for initiatives missing them.

    POST params:
        limit: int - Max initiatives to process (default: 20)
        dry_run: bool - Preview without triggering (default: True)

    Returns:
        JSON with triggered tasks
    """
    from core.models_document_registry import Initiative, InitiativeStage
    from core.tasks import generate_initiative_stage_document

    if request.method == 'GET':
        dry_run = True
        limit = int(request.GET.get('limit', 20))
    else:
        data = request.data if hasattr(request, 'data') else {}
        dry_run = data.get('dry_run', True)
        limit = int(data.get('limit', 20))

    result = {
        'dry_run': dry_run,
        'limit': limit,
        'triggered': 0,
        'errors': 0,
        'initiatives': [],
    }

    try:
        # Find DRAFT Stage 1 initiatives without documents
        stages_without_docs = InitiativeStage.objects.filter(
            status='DRAFT',
            stage=1,
            initiative__status='ACTIVE',
            document__isnull=True
        ).select_related('initiative')[:limit]

        result['found'] = stages_without_docs.count()

        for stage in stages_without_docs:
            init = stage.initiative
            item = {
                'id': str(init.id),
                'name': init.name[:50] + ('...' if len(init.name) > 50 else ''),
            }

            if dry_run:
                item['status'] = 'would_trigger'
                result['triggered'] += 1
            else:
                try:
                    task = generate_initiative_stage_document.delay(str(init.id), 1)
                    item['status'] = 'triggered'
                    item['task_id'] = str(task.id)
                    result['triggered'] += 1
                except Exception as e:
                    item['status'] = f'error: {str(e)}'
                    result['errors'] += 1

            result['initiatives'].append(item)

        if dry_run:
            result['message'] = f"[DRY RUN] Would trigger {result['triggered']} Stage 1 document generations. POST with dry_run=false to execute."
        else:
            result['message'] = f"Triggered {result['triggered']} Stage 1 document generations ({result['errors']} errors)"

    except Exception as e:
        result['error'] = str(e)
        result['message'] = f"Error: {e}"
        logger.error(f"[trigger_backfill] Error: {e}")

    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_initiative_conversation(request, initiative_id):
    """
    Session 928: Start a conversation about an initiative.

    Creates a HiveMindSession linked to the initiative, with full context
    injected so agents can discuss the initiative intelligently.

    POST /api/initiatives/{initiative_id}/start-conversation/
    {
        "topic": "optional custom topic - defaults to initiative name",
        "objective": "optional objective - defaults to discussing next steps",
        "conversation_type": "analytical" | "creative" | "debate" | "planning" | "critique" | "general",
        "auto_select_agents": true | false (default: true)
    }

    Returns:
        {
            "success": true,
            "session_id": "uuid",
            "session_url": "/workspace?tab=hivemind&session=uuid",
            "message": "Started conversation about initiative"
        }
    """
    from core.models_document_registry import Initiative, InitiativeStage
    from core.models_unified_system import HiveMindSession, Agent
    from core.agent_router import AgentRouter
    import uuid as uuid_module

    try:
        # Get the initiative
        try:
            initiative_uuid = uuid_module.UUID(str(initiative_id))
            initiative = Initiative.objects.get(id=initiative_uuid)
        except (ValueError, Initiative.DoesNotExist):
            return Response({
                'success': False,
                'error': f'Initiative not found: {initiative_id}'
            }, status=404)

        # Parse request data
        data = request.data if hasattr(request, 'data') else {}
        topic = data.get('topic') or f"Discuss: {initiative.name}"
        objective = data.get('objective') or f"Discuss next steps and strategy for the initiative: {initiative.name}"
        conversation_type = data.get('conversation_type', 'analytical')
        auto_select_agents = data.get('auto_select_agents', True)

        # Build rich context about the initiative
        context_parts = [
            f"## Initiative: {initiative.name}",
            f"**Status:** {initiative.status}",
            f"**Current Stage:** {initiative.current_stage}/5",
            f"**Description:** {initiative.description[:1000] if initiative.description else 'No description'}",
            "",
        ]

        # Add stage information
        stages = InitiativeStage.objects.filter(initiative=initiative).order_by('stage')
        if stages.exists():
            context_parts.append("## Pipeline Stages:")
            for stage in stages:
                stage_names = {
                    1: 'Research Brief',
                    2: 'Prototype Plan',
                    3: 'Evaluation Protocol',
                    4: 'Technical Design',
                    5: 'Pilot Execution'
                }
                stage_name = stage_names.get(stage.stage, f'Stage {stage.stage}')
                has_doc = "with document" if stage.document else "no document"
                context_parts.append(f"  - **Stage {stage.stage} ({stage_name}):** {stage.status} ({has_doc})")

        context_parts.append("")
        context_parts.append("## Discussion Focus:")
        context_parts.append("Please discuss this initiative, considering:")
        context_parts.append("1. What should happen next?")
        context_parts.append("2. What blockers or risks exist?")
        context_parts.append("3. What resources or agents are needed?")
        context_parts.append("4. What is the strategic value of this initiative?")

        context = "\n".join(context_parts)

        # Select agents based on initiative or use defaults
        participant_ids = []
        if auto_select_agents:
            # Use AgentRouter to find relevant agents
            try:
                router = AgentRouter()
                # Get agents relevant to the topic
                routing_result = router.route_by_query(
                    query=f"{initiative.name} {initiative.description[:200] if initiative.description else ''}"
                )
                if routing_result and routing_result.get('agents'):
                    relevant_agents = routing_result['agents'][:5]
                    participant_ids = [str(a.id) for a in relevant_agents]
            except Exception as e:
                logger.warning(f"Agent routing failed: {e}")

        # Fallback: use default strategic agents
        if not participant_ids:
            default_agent_names = [
                'ResearchAgent',
                'StrategyAgent',
                'CTOAgent',
                'SystemIntelligenceAgent',
                'ThinkingAgent'
            ]
            default_agents = Agent.objects.filter(name__in=default_agent_names)[:5]
            participant_ids = [str(a.id) for a in default_agents]

        # Create the HiveMindSession
        session = HiveMindSession.objects.create(
            session_mode='conversation',
            question=topic,
            context=context,
            conversation_topic=topic[:200],
            conversation_type=conversation_type,
            objective=objective,
            success_criteria=[
                "Clear next steps identified",
                "Blockers and risks discussed",
                "Strategic alignment confirmed"
            ],
            auto_selected_agents=auto_select_agents,
            rich_context_injected=True,
            status='initializing',
            participant_ids=participant_ids,
            initiative=initiative,  # Link to initiative
        )

        # Trigger conversation processing via Celery
        try:
            from core.tasks import run_triggered_conversation
            run_triggered_conversation.delay(str(session.id))
            session.status = 'gathering'
            session.started_at = timezone.now()
            session.save(update_fields=['status', 'started_at'])
        except Exception as e:
            logger.warning(f"Failed to trigger conversation task: {e}")
            # Session is created, will be picked up by periodic task

        return Response({
            'success': True,
            'session_id': str(session.id),
            'session_url': f'/workspace?tab=hivemind&session={session.id}',
            'message': f'Started conversation about: {initiative.name}',
            'participants': len(participant_ids),
            'conversation_type': conversation_type,
        })

    except Exception as e:
        logger.error(f"[start_initiative_conversation] Error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
