"""
Session 555 - Artifact API Endpoints

Phase A: Extraction & Decision
- List artifacts (with filtering)
- Get artifact details
- Decide on artifact (approve/reject/defer)
- Get artifacts by conversation

Phase B: Execution Pipeline
- Execute approved artifacts
- View execution history
- Get execution status
"""

import logging
from datetime import timedelta
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

from core.models_conversation_artifacts import ExtractedArtifact, ArtifactExecution

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def list_artifacts(request):
    """
    List artifacts with optional filtering.

    Query params:
    - status: pending|approved|rejected|deferred|implemented
    - type: proposal|experiment|risk|data_spec|question|action_item|insight
    - limit: max results (default 50)
    - offset: pagination offset
    """
    try:
        status = request.GET.get('status')
        artifact_type = request.GET.get('type')
        limit = min(int(request.GET.get('limit', 50)), 100)
        offset = int(request.GET.get('offset', 0))

        queryset = ExtractedArtifact.objects.select_related(
            'conversation', 'source_agent', 'decided_by'
        ).order_by('-composite_score', '-extracted_at')

        if status:
            queryset = queryset.filter(status=status)
        if artifact_type:
            queryset = queryset.filter(artifact_type=artifact_type)

        total = queryset.count()
        artifacts = queryset[offset:offset + limit]

        # Get counts by status
        counts = {
            'pending': ExtractedArtifact.objects.filter(status='pending').count(),
            'approved': ExtractedArtifact.objects.filter(status='approved').count(),
            'rejected': ExtractedArtifact.objects.filter(status='rejected').count(),
            'deferred': ExtractedArtifact.objects.filter(status='deferred').count(),
            'implemented': ExtractedArtifact.objects.filter(status='implemented').count(),
        }

        # Get counts by type (for pending only)
        type_counts = {}
        for t, _ in ExtractedArtifact.ARTIFACT_TYPES:
            type_counts[t] = ExtractedArtifact.objects.filter(
                status='pending', artifact_type=t
            ).count()

        return JsonResponse({
            'success': True,
            'artifacts': [_serialize_artifact(a) for a in artifacts],
            'total': total,
            'limit': limit,
            'offset': offset,
            'counts': counts,
            'type_counts': type_counts,
        })

    except Exception as e:
        logger.error(f"Error listing artifacts: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_artifact(request, artifact_id):
    """Get detailed artifact info."""
    try:
        artifact = ExtractedArtifact.objects.select_related(
            'conversation', 'source_agent', 'decided_by'
        ).get(id=artifact_id)

        return JsonResponse({
            'success': True,
            'artifact': _serialize_artifact(artifact, full=True)
        })

    except ExtractedArtifact.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Artifact not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting artifact {artifact_id}: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def decide_artifact(request, artifact_id):
    """
    Make a decision on an artifact.

    POST body:
    - decision: approved|rejected|deferred
    - notes: optional decision notes
    """
    try:
        artifact = ExtractedArtifact.objects.get(id=artifact_id)

        data = json.loads(request.body) if request.body else {}
        decision = data.get('decision')
        notes = data.get('notes', '')

        if decision not in ['approved', 'rejected', 'deferred', 'implemented']:
            return JsonResponse({
                'success': False,
                'error': 'Invalid decision. Must be: approved, rejected, deferred, or implemented'
            }, status=400)

        # Get user if authenticated
        user = request.user if request.user.is_authenticated else None

        if decision == 'approved':
            artifact.approve(user=user, notes=notes)
        elif decision == 'rejected':
            artifact.reject(user=user, notes=notes)
        elif decision == 'deferred':
            artifact.defer(user=user, notes=notes)
        else:
            artifact.status = 'implemented'
            artifact.decided_at = timezone.now()
            artifact.decided_by = user
            artifact.decision_notes = notes
            artifact.save()

        logger.info(f"Artifact {artifact_id} marked as {decision}")

        return JsonResponse({
            'success': True,
            'artifact': _serialize_artifact(artifact),
            'message': f'Artifact {decision}'
        })

    except ExtractedArtifact.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Artifact not found'}, status=404)
    except Exception as e:
        logger.error(f"Error deciding artifact {artifact_id}: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def conversation_artifacts(request, conversation_id):
    """Get all artifacts from a specific conversation."""
    try:
        artifacts = ExtractedArtifact.objects.filter(
            conversation_id=conversation_id
        ).select_related('source_agent').order_by('-composite_score')

        return JsonResponse({
            'success': True,
            'conversation_id': str(conversation_id),
            'artifacts': [_serialize_artifact(a) for a in artifacts],
            'count': artifacts.count()
        })

    except Exception as e:
        logger.error(f"Error getting conversation artifacts: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def extract_conversation(request, conversation_id):
    """
    Manually trigger artifact extraction for a conversation.
    Useful for re-extraction or debugging.
    """
    try:
        from core.services.artifact_extraction import extraction_service

        # Delete existing artifacts
        existing_count = ExtractedArtifact.objects.filter(
            conversation_id=conversation_id
        ).delete()[0]

        # Extract new artifacts
        artifacts = extraction_service.extract_from_conversation(str(conversation_id))

        return JsonResponse({
            'success': True,
            'conversation_id': str(conversation_id),
            'previous_artifacts_deleted': existing_count,
            'artifacts_extracted': len(artifacts),
            'artifacts': [_serialize_artifact(a) for a in artifacts]
        })

    except Exception as e:
        logger.error(f"Error extracting artifacts: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def pending_artifacts_summary(request):
    """
    Get summary of pending artifacts for dashboard display.
    Used in Boardroom for "Proposals Awaiting Decision" section.
    """
    try:
        pending = ExtractedArtifact.objects.filter(
            status='pending'
        ).select_related(
            'conversation', 'source_agent'
        ).order_by('-composite_score')[:10]

        # Group by type
        by_type = {}
        for artifact in pending:
            t = artifact.artifact_type
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(_serialize_artifact(artifact))

        # Get total counts
        total_pending = ExtractedArtifact.objects.filter(status='pending').count()
        type_counts = {}
        for t, _ in ExtractedArtifact.ARTIFACT_TYPES:
            type_counts[t] = ExtractedArtifact.objects.filter(
                status='pending', artifact_type=t
            ).count()

        return JsonResponse({
            'success': True,
            'total_pending': total_pending,
            'top_artifacts': [_serialize_artifact(a) for a in pending],
            'by_type': by_type,
            'type_counts': type_counts
        })

    except Exception as e:
        logger.error(f"Error getting pending summary: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def _serialize_artifact(artifact, full=False):
    """Serialize artifact for JSON response."""
    data = {
        'id': str(artifact.id),
        'type': artifact.artifact_type,
        'type_display': artifact.get_artifact_type_display(),
        'title': artifact.title,
        'description': artifact.description[:300] if not full else artifact.description,
        'source_agent': artifact.source_agent.name if artifact.source_agent else None,
        'conversation_id': str(artifact.conversation_id),
        'conversation_topic': artifact.conversation.topic if artifact.conversation else None,
        'status': artifact.status,
        'status_display': artifact.get_status_display(),
        'importance_score': artifact.importance_score,
        'urgency_score': artifact.urgency_score,
        'composite_score': artifact.composite_score,
        'extracted_at': artifact.extracted_at.isoformat() if artifact.extracted_at else None,
    }

    if full:
        data.update({
            'details': artifact.details,
            'source_message_index': artifact.source_message_index,
            'confidence_score': artifact.confidence_score,
            'decided_at': artifact.decided_at.isoformat() if artifact.decided_at else None,
            'decided_by': artifact.decided_by.username if artifact.decided_by else None,
            'decision_notes': artifact.decision_notes,
        })

    return data


# ============================================================================
# Phase B: Execution Pipeline Endpoints
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def execute_artifact(request, artifact_id):
    """
    Manually trigger execution for an approved artifact.

    POST /api/artifacts/<uuid>/execute/

    Returns execution ID and initial status.
    """
    try:
        from core.services.artifact_execution import execution_service

        artifact = ExtractedArtifact.objects.get(id=artifact_id)

        if artifact.status != 'approved':
            return JsonResponse({
                'success': False,
                'error': f'Artifact must be approved first (current status: {artifact.status})'
            }, status=400)

        # Check if already has a running or completed execution
        existing = artifact.executions.filter(status__in=['running', 'completed']).first()
        if existing:
            return JsonResponse({
                'success': False,
                'error': f'Artifact already has a {existing.status} execution',
                'execution_id': str(existing.id)
            }, status=400)

        execution = execution_service.execute_artifact(artifact)

        logger.info(f"Manual execution triggered for artifact {artifact_id}")

        return JsonResponse({
            'success': True,
            'execution_id': str(execution.id),
            'agent_name': execution.agent_name,
            'status': execution.status,
            'message': f'Execution {execution.status}'
        })

    except ExtractedArtifact.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Artifact not found'}, status=404)
    except Exception as e:
        logger.error(f"Error executing artifact {artifact_id}: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def list_executions(request, artifact_id):
    """
    Get execution history for an artifact.

    GET /api/artifacts/<uuid>/executions/
    """
    try:
        executions = ArtifactExecution.objects.filter(
            artifact_id=artifact_id
        ).order_by('-queued_at')

        return JsonResponse({
            'success': True,
            'artifact_id': str(artifact_id),
            'executions': [_serialize_execution(e) for e in executions],
            'count': executions.count()
        })

    except Exception as e:
        logger.error(f"Error listing executions for {artifact_id}: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def execution_status(request):
    """
    Get overall execution pipeline status.

    GET /api/artifacts/execution-status/

    Returns counts and recent executions.
    """
    try:
        cutoff_24h = timezone.now() - timedelta(hours=24)

        # Get counts
        stats = {
            'queued': ArtifactExecution.objects.filter(status='queued').count(),
            'running': ArtifactExecution.objects.filter(status='running').count(),
            'completed_24h': ArtifactExecution.objects.filter(
                status='completed',
                completed_at__gte=cutoff_24h
            ).count(),
            'failed_24h': ArtifactExecution.objects.filter(
                status='failed',
                completed_at__gte=cutoff_24h
            ).count(),
        }

        # Calculate success rate
        total_finished = stats['completed_24h'] + stats['failed_24h']
        stats['success_rate'] = (
            stats['completed_24h'] / total_finished if total_finished > 0 else 0.0
        )

        # Get recent executions
        recent = ArtifactExecution.objects.select_related('artifact').order_by('-queued_at')[:10]

        return JsonResponse({
            'success': True,
            'stats': stats,
            'recent_executions': [_serialize_execution(e) for e in recent]
        })

    except Exception as e:
        logger.error(f"Error getting execution status: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_execution(request, execution_id):
    """
    Get details of a specific execution.

    GET /api/artifacts/executions/<uuid>/
    """
    try:
        execution = ArtifactExecution.objects.select_related('artifact').get(id=execution_id)

        return JsonResponse({
            'success': True,
            'execution': _serialize_execution(execution, full=True)
        })

    except ArtifactExecution.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Execution not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting execution {execution_id}: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def _serialize_execution(execution, full=False):
    """Serialize execution for JSON response."""
    data = {
        'id': str(execution.id),
        'artifact_id': str(execution.artifact_id),
        'artifact_title': execution.artifact.title[:50] if execution.artifact else None,
        'agent_name': execution.agent_name,
        'status': execution.status,
        'queued_at': execution.queued_at.isoformat() if execution.queued_at else None,
        'started_at': execution.started_at.isoformat() if execution.started_at else None,
        'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
        'execution_time_ms': execution.execution_time_ms,
    }

    if full:
        data.update({
            'task_description': execution.task_description,
            'context': execution.context,
            'result': execution.result,
            'error_message': execution.error_message,
            'tokens_used': execution.tokens_used,
        })

    return data


# ============================================================================
# Phase D: Review Documents with Side Chats
# ============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def list_review_documents(request):
    """
    List review documents awaiting decision.

    GET /api/reviews/

    Query params:
    - status: filter by status (default: awaiting_human)
    - limit: max results (default 20)
    """
    from core.models_conversation_artifacts import ReviewDocument

    try:
        status = request.GET.get('status', 'awaiting_human')
        limit = min(int(request.GET.get('limit', 20)), 50)

        reviews = ReviewDocument.objects.filter(
            status=status
        ).order_by('-created_at')[:limit]

        # Get counts by status
        counts = {}
        for s, _ in ReviewDocument.STATUS_CHOICES:
            counts[s] = ReviewDocument.objects.filter(status=s).count()

        return JsonResponse({
            'success': True,
            'reviews': [_serialize_review(r) for r in reviews],
            'count': len(reviews),
            'total_awaiting': counts.get('awaiting_human', 0),
            'counts': counts,
        })
    except Exception as e:
        logger.error(f"Error listing reviews: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_review_document(request, review_id):
    """
    Get detailed review document with side chat histories.

    GET /api/reviews/<uuid>/
    """
    from core.models_conversation_artifacts import ReviewDocument

    try:
        review = ReviewDocument.objects.get(id=review_id)

        # Get side chat histories
        pro_chat = review.side_chats.filter(side='pro').first()
        con_chat = review.side_chats.filter(side='con').first()

        data = _serialize_review(review, full=True)
        data['pro_chat_history'] = pro_chat.messages if pro_chat else []
        data['con_chat_history'] = con_chat.messages if con_chat else []

        return JsonResponse({
            'success': True,
            'review': data,
        })
    except ReviewDocument.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Review not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting review {review_id}: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def ask_pro_side(request, review_id):
    """
    Ask a question to the Pro side.

    POST /api/reviews/<uuid>/ask-pro/
    Body: {"question": "..."}
    """
    from core.models_conversation_artifacts import ReviewDocument
    from core.services.side_chat import side_chat_service

    try:
        review = ReviewDocument.objects.get(id=review_id)
        data = json.loads(request.body) if request.body else {}
        question = data.get('question', '').strip()

        if not question:
            return JsonResponse({'success': False, 'error': 'Question required'}, status=400)

        result = side_chat_service.ask_side(review, 'pro', question)

        return JsonResponse({
            'success': True,
            **result
        })
    except ReviewDocument.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Review not found'}, status=404)
    except Exception as e:
        logger.error(f"Error asking pro side: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def ask_con_side(request, review_id):
    """
    Ask a question to the Con side.

    POST /api/reviews/<uuid>/ask-con/
    Body: {"question": "..."}
    """
    from core.models_conversation_artifacts import ReviewDocument
    from core.services.side_chat import side_chat_service

    try:
        review = ReviewDocument.objects.get(id=review_id)
        data = json.loads(request.body) if request.body else {}
        question = data.get('question', '').strip()

        if not question:
            return JsonResponse({'success': False, 'error': 'Question required'}, status=400)

        result = side_chat_service.ask_side(review, 'con', question)

        return JsonResponse({
            'success': True,
            **result
        })
    except ReviewDocument.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Review not found'}, status=404)
    except Exception as e:
        logger.error(f"Error asking con side: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def decide_review(request, review_id):
    """
    Make a decision on a review document.

    POST /api/reviews/<uuid>/decide/
    Body: {
        "decision": "approved|approved_with_conditions|declined|deferred",
        "conditions": "...",  # If approved_with_conditions
        "reasoning": "..."    # Optional reasoning
    }
    """
    from core.models_conversation_artifacts import ReviewDocument

    try:
        review = ReviewDocument.objects.get(id=review_id)
        data = json.loads(request.body) if request.body else {}

        decision = data.get('decision')
        conditions = data.get('conditions', '')
        reasoning = data.get('reasoning', '')

        valid_decisions = ['approved', 'approved_with_conditions', 'declined', 'deferred']
        if decision not in valid_decisions:
            return JsonResponse({
                'success': False,
                'error': f'Invalid decision. Must be one of: {valid_decisions}'
            }, status=400)

        # Update review document
        review.status = decision
        review.decision_conditions = conditions
        review.decision_reasoning = reasoning
        review.decided_at = timezone.now()
        review.decided_by = request.user if request.user.is_authenticated else None
        review.save()

        # Also update the underlying artifact if applicable
        if review.target_type == 'artifact':
            try:
                artifact = ExtractedArtifact.objects.get(id=review.target_id)
                if decision in ['approved', 'approved_with_conditions']:
                    artifact.approve(
                        user=review.decided_by,
                        notes=f"Approved via review. {conditions}".strip()
                    )
                elif decision == 'declined':
                    artifact.reject(
                        user=review.decided_by,
                        notes=reasoning or "Declined via review"
                    )
                elif decision == 'deferred':
                    artifact.defer(
                        user=review.decided_by,
                        notes=reasoning or "Deferred via review"
                    )
            except ExtractedArtifact.DoesNotExist:
                pass

        logger.info(f"Review {review_id} decided: {decision}")

        return JsonResponse({
            'success': True,
            'review': _serialize_review(review),
            'message': f'Decision recorded: {decision}'
        })
    except ReviewDocument.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Review not found'}, status=404)
    except Exception as e:
        logger.error(f"Error deciding review {review_id}: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def generate_review_for_artifact(request, artifact_id):
    """
    Generate a review document for a pending artifact.

    POST /api/artifacts/<uuid>/generate-review/
    """
    from core.services.review_document import review_service

    try:
        review = review_service.get_or_create_for_artifact(str(artifact_id))

        return JsonResponse({
            'success': True,
            'review': _serialize_review(review, full=True),
            'message': 'Review document generated'
        })
    except ExtractedArtifact.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Artifact not found'}, status=404)
    except Exception as e:
        logger.error(f"Error generating review for {artifact_id}: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def _serialize_review(review, full: bool = False):
    """Serialize review document for JSON response."""
    from core.models_conversation_artifacts import ReviewDocument

    data = {
        'id': str(review.id),
        'target_type': review.target_type,
        'target_id': str(review.target_id),
        'neutral_summary': review.neutral_summary[:300] if not full else review.neutral_summary,
        'ai_lean': review.ai_lean,
        'ai_confidence': review.ai_confidence,
        'status': review.status,
        'questions_asked_pro': review.questions_asked_pro,
        'questions_asked_con': review.questions_asked_con,
        'created_at': review.created_at.isoformat(),
    }

    if full:
        data.update({
            'pro_case': review.pro_case,
            'con_case': review.con_case,
            'open_questions': review.open_questions,
            'key_evidence': review.key_evidence,
            'ai_recommendation': review.ai_recommendation,
            'decision_conditions': review.decision_conditions,
            'decision_reasoning': review.decision_reasoning,
            'decided_at': review.decided_at.isoformat() if review.decided_at else None,
            'decided_by': review.decided_by.username if review.decided_by else None,
        })

    return data


# ============================================================================
# Session 556: Option C - Auto-Review Generation Trigger
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def trigger_auto_reviews(request):
    """
    Manually trigger auto-review generation for pending artifacts.

    POST /api/artifacts/trigger-auto-reviews/

    Triggers the Celery task that scans for:
    - High-priority artifacts (composite_score >= 0.7)
    - Artifacts pending > 24 hours
    - Urgent artifacts (urgency_score >= 0.8)

    Returns:
        JSON with task_id for tracking
    """
    try:
        from core.tasks import generate_pending_reviews

        # Trigger the Celery task
        result = generate_pending_reviews.delay()

        logger.info(f"Auto-review generation triggered: task_id={result.id}")

        return JsonResponse({
            'success': True,
            'task_id': str(result.id),
            'message': 'Auto-review generation triggered. Reviews will be generated for qualifying artifacts.'
        })
    except Exception as e:
        logger.error(f"Error triggering auto-reviews: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_auto_review_stats(request):
    """
    Get statistics about auto-review generation.

    GET /api/artifacts/auto-review-stats/

    Returns:
        JSON with counts of pending artifacts by trigger condition
    """
    from django.utils import timezone
    from datetime import timedelta
    from core.models_conversation_artifacts import ExtractedArtifact, ReviewDocument

    try:
        now = timezone.now()

        # Find artifacts that don't have reviews yet
        existing_review_targets = ReviewDocument.objects.filter(
            target_type='artifact'
        ).values_list('target_id', flat=True)

        pending_artifacts = ExtractedArtifact.objects.filter(
            status='pending'
        ).exclude(
            id__in=existing_review_targets
        )

        # Count by trigger condition
        stats = {
            'total_pending_without_review': pending_artifacts.count(),
            'high_priority': pending_artifacts.filter(composite_score__gte=0.7).count(),
            'pending_over_24h': pending_artifacts.filter(
                extracted_at__lt=now - timedelta(hours=24)
            ).count(),
            'urgent': pending_artifacts.filter(urgency_score__gte=0.8).count(),
            'total_reviews': ReviewDocument.objects.count(),
            'reviews_awaiting_human': ReviewDocument.objects.filter(
                status='awaiting_human'
            ).count(),
        }

        # Would-be-generated count (union of all conditions)
        would_generate = pending_artifacts.filter(
            models.Q(composite_score__gte=0.7) |
            models.Q(extracted_at__lt=now - timedelta(hours=24)) |
            models.Q(urgency_score__gte=0.8)
        ).count()
        stats['would_generate'] = would_generate

        return JsonResponse({
            'success': True,
            'stats': stats,
        })
    except Exception as e:
        logger.error(f"Error getting auto-review stats: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================================================
# Session 556: Option D - Dream Reviews
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def generate_review_for_dream(request, dream_id):
    """
    Generate a review document for an AgentDream.

    POST /api/dreams/<uuid>/generate-review/

    Creates a pro/con review document for a dream to help with
    investment decisions. Uses the same Ask Pro/Ask Con workflow
    as artifact reviews.

    Returns:
        JSON with the generated review document
    """
    from core.models_unified_system import AgentDream
    from core.services.review_document import review_service
    from core.models_conversation_artifacts import ReviewDocument

    try:
        # Check for existing review
        try:
            existing = ReviewDocument.objects.get(
                target_type='dream',
                target_id=dream_id
            )
            logger.info(f"Found existing dream review: {existing.id}")
            return JsonResponse({
                'success': True,
                'review': _serialize_review(existing, full=True),
                'message': 'Existing review found',
                'existing': True,
            })
        except ReviewDocument.DoesNotExist:
            pass

        # Generate new review
        dream = AgentDream.objects.get(id=dream_id)
        review = review_service.generate_dream_review(dream)

        logger.info(f"Generated dream review: {review.id} for dream: {dream_id}")

        return JsonResponse({
            'success': True,
            'review': _serialize_review(review, full=True),
            'message': 'Dream review document generated',
            'existing': False,
        })
    except AgentDream.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Dream not found'}, status=404)
    except Exception as e:
        logger.error(f"Error generating dream review for {dream_id}: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def list_dream_reviews(request):
    """
    List review documents for dreams.

    GET /api/dreams/reviews/

    Query params:
    - status: filter by status (default: all)
    - limit: max results (default: 20)
    """
    from core.models_conversation_artifacts import ReviewDocument

    try:
        status = request.GET.get('status')
        limit = min(int(request.GET.get('limit', 20)), 50)

        queryset = ReviewDocument.objects.filter(target_type='dream')

        if status:
            queryset = queryset.filter(status=status)

        reviews = queryset.order_by('-created_at')[:limit]

        return JsonResponse({
            'success': True,
            'reviews': [_serialize_review(r) for r in reviews],
            'count': len(reviews),
        })
    except Exception as e:
        logger.error(f"Error listing dream reviews: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
