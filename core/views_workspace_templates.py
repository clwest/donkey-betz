"""
Workspace Templates & Business-Unit APIs
==========================================

Endpoints for workspace template browsing, provisioning, and
per-workspace business dashboards.

- GET  /api/workspace-templates/              — list available templates
- GET  /api/workspace-templates/<slug>/       — template detail
- POST /api/workspaces/create-from-template/  — provision workspace from template
- GET  /api/workspaces/<id>/dashboard/        — per-workspace business dashboard
- GET  /api/workspaces/<id>/config/           — workspace business config
- PATCH /api/workspaces/<id>/config/          — update workspace config
"""

import logging

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models_workspace_templates import WorkspaceTemplate, WorkspaceConfig, PipelineRun

logger = logging.getLogger(__name__)


# ── Template Browsing ────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_templates(request):
    """List available workspace templates."""
    templates = WorkspaceTemplate.objects.filter(is_active=True).order_by('sort_order')

    return Response({
        'success': True,
        'templates': [{
            'id': str(t.id),
            'name': t.name,
            'slug': t.slug,
            'description': t.description,
            'icon': t.icon,
            'category': t.category,
            'is_featured': t.is_featured,
            'pipeline_stage_count': len(t.pipeline_stages),
            'agent_count': len(t.agent_pool),
            'spider_count': len(t.spider_subscriptions),
            'pipeline_stages': t.pipeline_stages,
            'agent_pool': t.agent_pool,
            'deliverable_categories': t.deliverable_categories,
            'default_settings': t.default_settings,
        } for t in templates],
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def template_detail(request, slug):
    """Get full detail for a specific template."""
    try:
        t = WorkspaceTemplate.objects.get(slug=slug, is_active=True)
    except WorkspaceTemplate.DoesNotExist:
        return Response({'success': False, 'error': 'Template not found'}, status=404)

    return Response({
        'success': True,
        'template': {
            'id': str(t.id),
            'name': t.name,
            'slug': t.slug,
            'description': t.description,
            'icon': t.icon,
            'category': t.category,
            'is_featured': t.is_featured,
            'pipeline_stages': t.pipeline_stages,
            'agent_pool': t.agent_pool,
            'spider_subscriptions': t.spider_subscriptions,
            'deliverable_categories': t.deliverable_categories,
            'default_settings': t.default_settings,
            'default_quotas': t.default_quotas,
            'instances_count': t.instances.count(),
        },
    })


# ── Workspace Provisioning ───────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_from_template(request):
    """
    Create a new workspace from a template.

    Body:
        template_slug: str (required)
        name: str (required)
        description: str (optional)
        settings_overrides: dict (optional) — merged over template defaults
    """
    template_slug = request.data.get('template_slug', '').strip()
    name = request.data.get('name', '').strip()
    description = request.data.get('description', '')
    settings_overrides = request.data.get('settings_overrides', {})

    if not template_slug:
        return Response({'success': False, 'error': 'template_slug is required'}, status=400)
    if not name:
        return Response({'success': False, 'error': 'name is required'}, status=400)

    try:
        template = WorkspaceTemplate.objects.get(slug=template_slug, is_active=True)
    except WorkspaceTemplate.DoesNotExist:
        return Response({'success': False, 'error': f'Template "{template_slug}" not found'}, status=404)

    # Provision workspace
    workspace = template.provision(
        user=request.user,
        name=name,
        description=description,
    )

    # Apply settings overrides if provided
    if settings_overrides and hasattr(workspace, 'config'):
        config = workspace.config
        merged = {**config.settings, **settings_overrides}
        config.settings = merged
        config.save(update_fields=['settings'])

    return Response({
        'success': True,
        'workspace': {
            'id': str(workspace.id),
            'name': workspace.name,
            'description': workspace.description,
            'template': template.name,
            'template_slug': template.slug,
            'status': workspace.config.status,
            'pipeline_stages': workspace.config.pipeline_config,
            'agent_pool': workspace.config.agent_pool,
            'settings': workspace.config.settings,
        },
        'message': f'Workspace "{name}" created from {template.name} template.',
    }, status=201)


# ── Workspace Dashboard ──────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def workspace_dashboard(request, workspace_id):
    """
    Per-workspace business dashboard with metrics.

    Returns deliverable counts, pipeline stage summary, recent activity,
    and workspace health indicators.
    """
    from core.models_skin_layer import ProjectWorkspace
    from core.models_deliverables import Deliverable

    try:
        workspace = ProjectWorkspace.objects.get(id=workspace_id, user=request.user)
    except ProjectWorkspace.DoesNotExist:
        return Response({'success': False, 'error': 'Workspace not found'}, status=404)

    # Get or create config
    config = getattr(workspace, 'config', None)
    template_name = config.template.name if config and config.template else 'Custom'

    # Deliverable metrics
    deliverables = Deliverable.objects.filter(workspace=workspace)
    total = deliverables.count()
    saved = deliverables.filter(is_saved=True).count()
    by_category = dict(
        deliverables.values('category')
        .annotate(count=Count('id'))
        .order_by('-count')
        .values_list('category', 'count')[:10]
    )
    by_type = dict(
        deliverables.values('deliverable_type')
        .annotate(count=Count('id'))
        .values_list('deliverable_type', 'count')
    )

    # Recent deliverables
    recent = deliverables.order_by('-created_at')[:5]
    recent_list = [{
        'id': str(d.id),
        'title': d.title,
        'category': d.category,
        'agent_name': d.agent_name,
        'quality_score': d.quality_score,
        'created_at': d.created_at.isoformat(),
    } for d in recent]

    # Pipeline stage summary (if config exists)
    pipeline_summary = []
    if config and config.pipeline_config:
        for stage in config.pipeline_config:
            stage_name = stage.get('name', '')
            # Count deliverables tagged with this stage
            stage_count = deliverables.filter(
                Q(tags__contains=[stage_name.lower()]) |
                Q(category__icontains=stage_name)
            ).count()
            pipeline_summary.append({
                'name': stage_name,
                'agent': stage.get('agent'),
                'auto': stage.get('auto', False),
                'requires_approval': stage.get('requires_approval', False),
                'deliverable_count': stage_count,
                'description': stage.get('description', ''),
            })

    # Initiative count for this workspace
    from core.models_document_registry import Initiative
    initiative_count = Initiative.objects.filter(target_workspace=workspace).count()

    return Response({
        'success': True,
        'workspace': {
            'id': str(workspace.id),
            'name': workspace.name,
            'description': workspace.description,
            'template': template_name,
            'status': config.status if config else 'unconfigured',
            'governance_mode': config.effective_governance_mode if config else 'normal',
            'created_at': workspace.created_at.isoformat(),
        },
        'metrics': {
            'deliverables_total': total,
            'deliverables_saved': saved,
            'by_category': by_category,
            'by_type': by_type,
            'initiative_count': initiative_count,
        },
        'pipeline': pipeline_summary,
        'recent_deliverables': recent_list,
        'settings': config.settings if config else {},
        'quotas': config.quotas if config else {},
    })


# ── Workspace Config Management ──────────────────────────────────────────────

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def workspace_config(request, workspace_id):
    """Get or update workspace business config."""
    from core.models_skin_layer import ProjectWorkspace

    try:
        workspace = ProjectWorkspace.objects.get(id=workspace_id, user=request.user)
    except ProjectWorkspace.DoesNotExist:
        return Response({'success': False, 'error': 'Workspace not found'}, status=404)

    config = getattr(workspace, 'config', None)
    if not config:
        return Response({'success': False, 'error': 'No business config for this workspace. Create from a template first.'}, status=404)

    if request.method == 'PATCH':
        # Update allowed fields
        updatable = ['settings', 'quotas', 'status', 'governance_mode',
                     'pipeline_config', 'agent_pool', 'spider_subscriptions',
                     'deliverable_categories']
        updated = []
        for field in updatable:
            if field in request.data:
                if field in ('settings', 'quotas'):
                    # Merge instead of replace
                    current = getattr(config, field) or {}
                    merged = {**current, **request.data[field]}
                    setattr(config, field, merged)
                else:
                    setattr(config, field, request.data[field])
                updated.append(field)

        if updated:
            config.save(update_fields=updated + ['updated_at'])

        return Response({
            'success': True,
            'updated_fields': updated,
            'message': f'Updated workspace config: {", ".join(updated)}',
        })

    # GET
    return Response({
        'success': True,
        'config': {
            'id': str(config.id),
            'workspace_id': str(workspace.id),
            'workspace_name': workspace.name,
            'template': config.template.name if config.template else None,
            'template_slug': config.template.slug if config.template else None,
            'status': config.status,
            'governance_mode': config.effective_governance_mode,
            'pipeline_config': config.pipeline_config,
            'agent_pool': config.agent_pool,
            'spider_subscriptions': config.spider_subscriptions,
            'deliverable_categories': config.deliverable_categories,
            'settings': config.settings,
            'quotas': config.quotas,
            'created_at': config.created_at.isoformat(),
            'updated_at': config.updated_at.isoformat(),
        },
    })


# ── Pipeline Execution ───────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_pipeline(request, workspace_id):
    """
    Trigger a pipeline run for a workspace.

    Dispatches to Celery so the request returns immediately.
    Returns the run_id for status polling.
    """
    from core.models_skin_layer import ProjectWorkspace

    try:
        workspace = ProjectWorkspace.objects.get(id=workspace_id, user=request.user)
    except ProjectWorkspace.DoesNotExist:
        return Response({'success': False, 'error': 'Workspace not found'}, status=404)

    config = getattr(workspace, 'config', None)
    if not config or not config.pipeline_config:
        return Response({'success': False, 'error': 'No pipeline configured'}, status=400)

    # Check for already-running pipeline
    active = PipelineRun.objects.filter(
        workspace=workspace, status='running'
    ).first()
    if active:
        return Response({
            'success': False,
            'error': 'Pipeline already running',
            'run_id': str(active.id),
        }, status=409)

    # Create the run record immediately so we can return run_id
    run = PipelineRun.objects.create(
        workspace=workspace,
        triggered_by=request.user,
        status='pending',
        pipeline_snapshot=config.pipeline_config,
        stage_results=[
            {
                'stage_index': i,
                'name': stage.get('name', f'Stage {i+1}'),
                'agent': stage.get('agent'),
                'auto': stage.get('auto', False),
                'requires_approval': stage.get('requires_approval', False),
                'status': 'pending',
                'started_at': None,
                'finished_at': None,
                'output': None,
                'error': None,
            }
            for i, stage in enumerate(config.pipeline_config)
        ],
    )

    # Dispatch to Celery
    from core.tasks import execute_workspace_pipeline
    execute_workspace_pipeline.delay(str(run.id))

    return Response({
        'success': True,
        'run_id': str(run.id),
        'status': 'pending',
        'stages': run.stage_results,
        'message': f'Pipeline started for "{workspace.name}" ({len(config.pipeline_config)} stages)',
    }, status=202)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pipeline_status(request, workspace_id):
    """
    Get pipeline run status for a workspace.

    Query params:
        run_id: specific run (optional — defaults to most recent)
    """
    from core.models_skin_layer import ProjectWorkspace

    try:
        workspace = ProjectWorkspace.objects.get(id=workspace_id, user=request.user)
    except ProjectWorkspace.DoesNotExist:
        return Response({'success': False, 'error': 'Workspace not found'}, status=404)

    run_id = request.GET.get('run_id')
    if run_id:
        try:
            run = PipelineRun.objects.get(id=run_id, workspace=workspace)
        except PipelineRun.DoesNotExist:
            return Response({'success': False, 'error': 'Run not found'}, status=404)
    else:
        run = PipelineRun.objects.filter(workspace=workspace).first()
        if not run:
            return Response({'success': True, 'run': None, 'message': 'No pipeline runs yet'})

    return Response({
        'success': True,
        'run': {
            'id': str(run.id),
            'status': run.status,
            'progress_pct': run.progress_pct,
            'current_stage_index': run.current_stage_index,
            'stages': run.stage_results,
            'started_at': run.started_at.isoformat() if run.started_at else None,
            'finished_at': run.finished_at.isoformat() if run.finished_at else None,
            'duration_seconds': run.duration_seconds,
            'error_message': run.error_message,
            'created_at': run.created_at.isoformat(),
        },
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pipeline_history(request, workspace_id):
    """List recent pipeline runs for a workspace."""
    from core.models_skin_layer import ProjectWorkspace

    try:
        workspace = ProjectWorkspace.objects.get(id=workspace_id, user=request.user)
    except ProjectWorkspace.DoesNotExist:
        return Response({'success': False, 'error': 'Workspace not found'}, status=404)

    runs = PipelineRun.objects.filter(workspace=workspace)[:10]

    return Response({
        'success': True,
        'runs': [{
            'id': str(r.id),
            'status': r.status,
            'progress_pct': r.progress_pct,
            'stage_count': len(r.pipeline_snapshot),
            'started_at': r.started_at.isoformat() if r.started_at else None,
            'finished_at': r.finished_at.isoformat() if r.finished_at else None,
            'duration_seconds': r.duration_seconds,
            'created_at': r.created_at.isoformat(),
        } for r in runs],
    })
