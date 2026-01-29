"""
ConceptForge API Views
======================

Session 865: REST API endpoints for ConceptForge dossier pipeline.

Endpoints:
- GET /api/conceptforge/runs/ - List all runs with filtering
- GET /api/conceptforge/runs/<id>/ - Get run details with stages
- POST /api/conceptforge/runs/<id>/retry/ - Retry a failed run
- GET /api/conceptforge/stats/ - Get pipeline statistics
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from core.models_conceptforge import ConceptForgeRun, ConceptForgeStageRun, ConceptForgeArtifact

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET"])
def list_runs(request):
    """
    List ConceptForge runs with optional filtering.

    Query params:
    - status: Filter by status (pending, running, completed, failed)
    - domain: Filter by domain (legal, market, tech, etc.)
    - limit: Max results (default 50)
    - offset: Pagination offset
    """
    try:
        # Get filter params
        status = request.GET.get('status')
        domain = request.GET.get('domain')
        limit = min(int(request.GET.get('limit', 50)), 100)
        offset = int(request.GET.get('offset', 0))

        # Build query
        queryset = ConceptForgeRun.objects.select_related('user').prefetch_related('stages')

        if status:
            queryset = queryset.filter(status=status)
        if domain:
            queryset = queryset.filter(domain=domain)

        # Order by most recent
        queryset = queryset.order_by('-created_at')

        # Get total count before pagination
        total = queryset.count()

        # Apply pagination
        runs = queryset[offset:offset + limit]

        # Serialize
        results = []
        for run in runs:
            stages_data = {}
            for stage in run.stages.all():
                stages_data[stage.stage_name] = {
                    'id': str(stage.id),
                    'status': stage.status,
                    'duration_ms': stage.duration_ms,
                    'has_output': bool(stage.output_text),
                    'agent_used': stage.agent_used,
                    'advisors_used': stage.advisors_used,
                    'legendary_advisors_used': stage.legendary_advisors_used,
                }

            results.append({
                'id': str(run.id),
                'source_type': run.source_type,
                'source_id': str(run.source_id),
                'source_title': run.source_title,
                'domain': run.domain,
                'status': run.status,
                'current_stage': run.current_stage,
                'progress_percentage': run.progress_percentage,
                'quality_score': run.quality_score,
                'triggered_by': run.triggered_by,
                'duration_ms': run.duration_ms,
                'error': run.error if run.status == 'failed' else None,
                'stages': stages_data,
                'created_at': run.created_at.isoformat(),
                'started_at': run.started_at.isoformat() if run.started_at else None,
                'completed_at': run.completed_at.isoformat() if run.completed_at else None,
            })

        return JsonResponse({
            'runs': results,
            'total': total,
            'limit': limit,
            'offset': offset,
        })

    except Exception as e:
        logger.exception("Error listing ConceptForge runs")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_run_detail(request, run_id):
    """
    Get detailed information about a specific run including all stage outputs.
    """
    try:
        run = ConceptForgeRun.objects.prefetch_related(
            'stages', 'artifacts'
        ).get(id=run_id)

        # Build stage details with full output
        stages = []
        for stage in run.stages.order_by('stage_order'):
            stages.append({
                'id': str(stage.id),
                'stage_name': stage.stage_name,
                'stage_order': stage.stage_order,
                'status': stage.status,
                'agent_used': stage.agent_used,
                'advisors_used': stage.advisors_used,
                'legendary_advisors_used': stage.legendary_advisors_used,
                'output_text': stage.output_text,
                'output_metadata': stage.output_metadata,
                'error': stage.error if stage.status == 'failed' else None,
                'duration_ms': stage.duration_ms,
                'started_at': stage.started_at.isoformat() if stage.started_at else None,
                'completed_at': stage.completed_at.isoformat() if stage.completed_at else None,
            })

        # Build artifacts list
        artifacts = []
        for artifact in run.artifacts.all():
            artifacts.append({
                'id': str(artifact.id),
                'name': artifact.name,
                'kind': artifact.kind,
                'version': artifact.version,
                'is_primary': artifact.is_primary,
                'content': artifact.content[:500] + '...' if len(artifact.content) > 500 else artifact.content,
                'full_content_length': len(artifact.content),
                'created_at': artifact.created_at.isoformat(),
            })

        return JsonResponse({
            'id': str(run.id),
            'source_type': run.source_type,
            'source_id': str(run.source_id),
            'source_title': run.source_title,
            'domain': run.domain,
            'status': run.status,
            'current_stage': run.current_stage,
            'progress_percentage': run.progress_percentage,
            'quality_score': run.quality_score,
            'triggered_by': run.triggered_by,
            'duration_ms': run.duration_ms,
            'error': run.error,
            'advisor_panel_snapshot': run.advisor_panel_snapshot,
            'stages': stages,
            'artifacts': artifacts,
            'created_at': run.created_at.isoformat(),
            'started_at': run.started_at.isoformat() if run.started_at else None,
            'completed_at': run.completed_at.isoformat() if run.completed_at else None,
        })

    except ConceptForgeRun.DoesNotExist:
        return JsonResponse({'error': 'Run not found'}, status=404)
    except Exception as e:
        logger.exception("Error getting ConceptForge run detail")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_stage_content(request, run_id, stage_name):
    """
    Get full content for a specific stage.
    """
    try:
        stage = ConceptForgeStageRun.objects.get(
            run_id=run_id,
            stage_name=stage_name
        )

        return JsonResponse({
            'id': str(stage.id),
            'stage_name': stage.stage_name,
            'status': stage.status,
            'agent_used': stage.agent_used,
            'advisors_used': stage.advisors_used,
            'legendary_advisors_used': stage.legendary_advisors_used,
            'inputs_snapshot': stage.inputs_snapshot,
            'output_text': stage.output_text,
            'output_metadata': stage.output_metadata,
            'error': stage.error,
            'duration_ms': stage.duration_ms,
        })

    except ConceptForgeStageRun.DoesNotExist:
        return JsonResponse({'error': 'Stage not found'}, status=404)
    except Exception as e:
        logger.exception("Error getting stage content")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_artifact_content(request, artifact_id):
    """
    Get full content for an artifact.
    """
    try:
        artifact = ConceptForgeArtifact.objects.get(id=artifact_id)

        return JsonResponse({
            'id': str(artifact.id),
            'name': artifact.name,
            'kind': artifact.kind,
            'version': artifact.version,
            'is_primary': artifact.is_primary,
            'content': artifact.content,
            'file_path': artifact.file_path,
            'metadata': artifact.metadata,
            'created_at': artifact.created_at.isoformat(),
        })

    except ConceptForgeArtifact.DoesNotExist:
        return JsonResponse({'error': 'Artifact not found'}, status=404)
    except Exception as e:
        logger.exception("Error getting artifact content")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def retry_run(request, run_id):
    """
    Retry a failed ConceptForge run from the failed stage.
    """
    try:
        run = ConceptForgeRun.objects.get(id=run_id)

        if run.status != 'failed':
            return JsonResponse({
                'error': 'Can only retry failed runs'
            }, status=400)

        # Import here to avoid circular imports
        from core.tasks import run_conceptforge_pipeline

        # Reset run status
        run.status = 'pending'
        run.error = ''
        run.save(update_fields=['status', 'error', 'updated_at'])

        # Trigger async execution
        task = run_conceptforge_pipeline.delay(
            source_type=run.source_type,
            source_id=str(run.source_id),
            source_title=run.source_title,
            domain=run.domain,
            quality_score=run.quality_score,
            triggered_by='manual_retry',
            user_id=request.user.id if request.user.is_authenticated else None,
            existing_run_id=str(run.id),  # Continue existing run
        )

        return JsonResponse({
            'success': True,
            'run_id': str(run.id),
            'task_id': task.id,
            'message': 'Run queued for retry'
        })

    except ConceptForgeRun.DoesNotExist:
        return JsonResponse({'error': 'Run not found'}, status=404)
    except Exception as e:
        logger.exception("Error retrying ConceptForge run")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_stats(request):
    """
    Get ConceptForge pipeline statistics.
    """
    try:
        now = timezone.now()
        last_7_days = now - timedelta(days=7)
        last_30_days = now - timedelta(days=30)

        # Overall stats
        total_runs = ConceptForgeRun.objects.count()
        completed_runs = ConceptForgeRun.objects.filter(status='completed').count()
        failed_runs = ConceptForgeRun.objects.filter(status='failed').count()
        running_runs = ConceptForgeRun.objects.filter(status='running').count()
        pending_runs = ConceptForgeRun.objects.filter(status='pending').count()

        # Recent activity
        runs_last_7_days = ConceptForgeRun.objects.filter(created_at__gte=last_7_days).count()
        runs_last_30_days = ConceptForgeRun.objects.filter(created_at__gte=last_30_days).count()

        # Average duration for completed runs
        avg_duration = ConceptForgeRun.objects.filter(
            status='completed',
            duration_ms__gt=0
        ).aggregate(avg=Avg('duration_ms'))['avg'] or 0

        # Runs by domain
        by_domain = list(
            ConceptForgeRun.objects.values('domain')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # Runs by status
        by_status = {
            'completed': completed_runs,
            'failed': failed_runs,
            'running': running_runs,
            'pending': pending_runs,
        }

        # Success rate
        success_rate = (completed_runs / total_runs * 100) if total_runs > 0 else 0

        # Recent runs (last 5)
        recent_runs = []
        for run in ConceptForgeRun.objects.order_by('-created_at')[:5]:
            recent_runs.append({
                'id': str(run.id),
                'source_title': run.source_title[:50],
                'domain': run.domain,
                'status': run.status,
                'progress_percentage': run.progress_percentage,
                'created_at': run.created_at.isoformat(),
            })

        return JsonResponse({
            'total_runs': total_runs,
            'completed_runs': completed_runs,
            'failed_runs': failed_runs,
            'running_runs': running_runs,
            'pending_runs': pending_runs,
            'runs_last_7_days': runs_last_7_days,
            'runs_last_30_days': runs_last_30_days,
            'avg_duration_ms': int(avg_duration),
            'success_rate': round(success_rate, 1),
            'by_domain': by_domain,
            'by_status': by_status,
            'recent_runs': recent_runs,
        })

    except Exception as e:
        logger.exception("Error getting ConceptForge stats")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_domain_labs(request):
    """
    Get available domain labs configuration.
    """
    try:
        from core.conceptforge.labs import DOMAIN_LABS

        labs = []
        for domain, config in DOMAIN_LABS.items():
            labs.append({
                'domain': domain,
                'name': config.name,
                'description': config.description,
                'icon': config.icon,
                'routing_tags': config.routing_tags,
            })

        return JsonResponse({'labs': labs})

    except Exception as e:
        logger.exception("Error getting domain labs")
        return JsonResponse({'error': str(e)}, status=500)
