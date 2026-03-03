"""
Deliverables API Views - Session 819: Deliverables Marketplace

API endpoints for the Deliverables Marketplace feature:
- List deliverables with filtering
- Get deliverable detail
- Save/unsave to library
- Clone deliverable
- Convert to template
- Export to PDF/DOCX/HTML
- Jobs tracking
"""

import logging
from datetime import timedelta
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from core.auth_middleware import token_auth_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.shortcuts import get_object_or_404

from core.models_deliverables import (
    Deliverable,
    DeliverableEvent,
    DeliverableExport,
    DeliverableCollection,
    DeliverableType,
)

logger = logging.getLogger(__name__)


def _emit_event(deliverable, event_type, user, source='frontend', metadata=None):
    """Emit a DeliverableEvent. Fire-and-forget — never raises."""
    try:
        resolved_user = user if (user and user.is_authenticated) else None
        DeliverableEvent.objects.create(
            deliverable=deliverable,
            event_type=event_type,
            user=resolved_user,
            source=source,
            metadata=metadata or {},
        )
    except Exception as exc:
        logger.debug("DeliverableEvent emit failed: %s", exc)


@require_GET
def list_deliverables(request):
    """
    List deliverables with filtering and pagination.

    Query parameters:
        - type: Filter by deliverable type (document, image, code, etc.)
        - category: Filter by category
        - agent: Filter by agent name
        - saved: Filter by is_saved (true/false)
        - template: Filter by is_template (true/false)
        - source: Filter by source (user/system)
        - search: Search in title and content
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20, max: 100)
    """
    try:
        # Base queryset
        queryset = Deliverable.objects.all()

        # Filter by user if authenticated
        if request.user.is_authenticated:
            # Show user's own deliverables plus public ones
            queryset = queryset.filter(
                Q(user=request.user) | Q(user__isnull=True)
            )

        # Apply filters
        deliverable_type = request.GET.get('type')
        if deliverable_type:
            queryset = queryset.filter(deliverable_type=deliverable_type)

        category = request.GET.get('category')
        if category:
            queryset = queryset.filter(category__iexact=category)

        agent = request.GET.get('agent')
        if agent:
            queryset = queryset.filter(agent_name__iexact=agent)

        saved = request.GET.get('saved')
        if saved is not None:
            queryset = queryset.filter(is_saved=saved.lower() == 'true')

        template = request.GET.get('template')
        if template is not None:
            queryset = queryset.filter(is_template=template.lower() == 'true')

        source = request.GET.get('source')
        if source == 'user':
            queryset = queryset.filter(user__isnull=False)
        elif source == 'system':
            queryset = queryset.filter(user__isnull=True)

        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(preview_content__icontains=search) |
                Q(tags__contains=[search])
            )

        # Order by most recent
        queryset = queryset.order_by('-created_at')

        # Pagination
        page = int(request.GET.get('page', 1))
        per_page = min(int(request.GET.get('per_page', 20)), 100)

        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)

        # Serialize results
        deliverables = [
            _serialize_deliverable(d, include_content=False)
            for d in page_obj
        ]

        return JsonResponse({
            'success': True,
            'deliverables': deliverables,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })

    except Exception as e:
        logger.error(f"Error listing deliverables: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def get_deliverable(request, deliverable_id):
    """Get a single deliverable with full content."""
    try:
        deliverable = get_object_or_404(Deliverable, id=deliverable_id)

        # Check access permissions
        if deliverable.user and request.user.is_authenticated:
            if deliverable.user != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'Access denied'
                }, status=403)

        # Auto-emit view event
        _emit_event(deliverable, 'synthesis_viewed', request.user, 'frontend')

        return JsonResponse({
            'success': True,
            'deliverable': _serialize_deliverable(deliverable, include_content=True)
        })

    except Exception as e:
        logger.error(f"Error getting deliverable {deliverable_id}: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_POST
@token_auth_required
def save_deliverable(request, deliverable_id):
    """Save a deliverable to the user's library."""
    try:
        deliverable = get_object_or_404(Deliverable, id=deliverable_id)

        # Check ownership
        if deliverable.user and deliverable.user != request.user:
            return JsonResponse({
                'success': False,
                'error': 'Access denied'
            }, status=403)

        # Set user if not set
        if not deliverable.user:
            deliverable.user = request.user

        deliverable.is_saved = True
        deliverable.save(update_fields=['is_saved', 'user', 'updated_at'])
        _emit_event(deliverable, 'deliverable_saved', request.user, 'frontend')

        return JsonResponse({
            'success': True,
            'message': 'Deliverable saved to library',
            'deliverable': _serialize_deliverable(deliverable, include_content=False)
        })

    except Exception as e:
        logger.error(f"Error saving deliverable {deliverable_id}: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_POST
@token_auth_required
def unsave_deliverable(request, deliverable_id):
    """Remove a deliverable from the user's library."""
    try:
        deliverable = get_object_or_404(
            Deliverable,
            id=deliverable_id,
            user=request.user
        )

        deliverable.is_saved = False
        deliverable.save(update_fields=['is_saved', 'updated_at'])

        return JsonResponse({
            'success': True,
            'message': 'Deliverable removed from library',
            'deliverable': _serialize_deliverable(deliverable, include_content=False)
        })

    except Exception as e:
        logger.error(f"Error unsaving deliverable {deliverable_id}: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_POST
@token_auth_required
def clone_deliverable(request, deliverable_id):
    """Create a copy of a deliverable."""
    try:
        original = get_object_or_404(Deliverable, id=deliverable_id)

        # Create clone
        clone = Deliverable.objects.create(
            title=f"Copy of {original.title}"[:255],
            deliverable_type=original.deliverable_type,
            category=original.category,
            tags=original.tags.copy() if original.tags else [],
            agent_name=original.agent_name,
            agent_task=original.agent_task,
            user=request.user,
            content=original.content,
            content_format=original.content_format,
            preview_content=original.preview_content,
            thumbnail_url=original.thumbnail_url,
            quality_score=original.quality_score,
            confidence_score=original.confidence_score,
            cloned_from=original,
            execution_time_ms=original.execution_time_ms,
            llm_cost=original.llm_cost,
            tool_calls=original.tool_calls.copy() if original.tool_calls else [],
            raw_output=original.raw_output.copy() if original.raw_output else {},
            metadata={'cloned_at': timezone.now().isoformat()},
            status='draft',
        )

        # Update clone count on original
        original.clone_count += 1
        original.save(update_fields=['clone_count', 'updated_at'])

        return JsonResponse({
            'success': True,
            'message': 'Deliverable cloned',
            'deliverable': _serialize_deliverable(clone, include_content=True)
        })

    except Exception as e:
        logger.error(f"Error cloning deliverable {deliverable_id}: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_POST
@token_auth_required
def templateize_deliverable(request, deliverable_id):
    """Convert a deliverable into a reusable template."""
    try:
        deliverable = get_object_or_404(
            Deliverable,
            id=deliverable_id,
            user=request.user
        )

        deliverable.is_template = True
        deliverable.save(update_fields=['is_template', 'updated_at'])

        return JsonResponse({
            'success': True,
            'message': 'Deliverable converted to template',
            'deliverable': _serialize_deliverable(deliverable, include_content=False)
        })

    except Exception as e:
        logger.error(f"Error templateizing deliverable {deliverable_id}: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_POST
@token_auth_required
def export_deliverable(request, deliverable_id):
    """Export a deliverable to PDF, DOCX, or HTML."""
    import json

    try:
        deliverable = get_object_or_404(Deliverable, id=deliverable_id)

        # Check access
        if deliverable.user and deliverable.user != request.user:
            return JsonResponse({
                'success': False,
                'error': 'Access denied'
            }, status=403)

        # Parse request body
        try:
            body = json.loads(request.body)
            export_format = body.get('format', 'html')
        except json.JSONDecodeError:
            export_format = request.POST.get('format', 'html')

        if export_format not in ['pdf', 'docx', 'html', 'markdown', 'json']:
            return JsonResponse({
                'success': False,
                'error': f'Unsupported export format: {export_format}'
            }, status=400)

        # Generate export content
        if export_format == 'html':
            content = _export_to_html(deliverable)
            content_type = 'text/html'
            filename = f"{deliverable.slug}.html"

        elif export_format == 'markdown':
            content = _export_to_markdown(deliverable)
            content_type = 'text/markdown'
            filename = f"{deliverable.slug}.md"

        elif export_format == 'json':
            content = json.dumps(
                _serialize_deliverable(deliverable, include_content=True),
                indent=2
            )
            content_type = 'application/json'
            filename = f"{deliverable.slug}.json"

        else:
            # PDF and DOCX require additional libraries
            # For now, return error
            return JsonResponse({
                'success': False,
                'error': f'{export_format.upper()} export not yet implemented'
            }, status=501)

        # Record export
        DeliverableExport.objects.create(
            deliverable=deliverable,
            user=request.user,
            export_format=export_format,
            file_size_bytes=len(content.encode('utf-8')),
        )
        _emit_event(deliverable, 'deliverable_exported', request.user, 'frontend',
                     {'format': export_format})

        # Return file download
        response = HttpResponse(content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        logger.error(f"Error exporting deliverable {deliverable_id}: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def get_deliverable_stats(request):
    """Get statistics about deliverables."""
    try:
        # Base queryset
        queryset = Deliverable.objects.all()

        if request.user.is_authenticated:
            queryset = queryset.filter(
                Q(user=request.user) | Q(user__isnull=True)
            )

        # Aggregate stats
        total = queryset.count()
        saved = queryset.filter(is_saved=True).count()
        templates = queryset.filter(is_template=True).count()
        user_count = queryset.filter(user__isnull=False).count()
        system_count = queryset.filter(user__isnull=True).count()

        # By type
        by_type = list(
            queryset.values('deliverable_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # By category
        by_category = list(
            queryset.exclude(category='')
            .values('category')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        # By agent
        by_agent = list(
            queryset.values('agent_name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        # Recent activity
        recent_count = queryset.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()

        return JsonResponse({
            'success': True,
            'stats': {
                'total': total,
                'saved': saved,
                'templates': templates,
                'recent_7d': recent_count,
                'user_count': user_count,
                'system_count': system_count,
                'by_type': by_type,
                'by_category': by_category,
                'by_agent': by_agent,
            }
        })

    except Exception as e:
        logger.error(f"Error getting deliverable stats: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def get_deliverable_types(request):
    """Get available deliverable types."""
    return JsonResponse({
        'success': True,
        'types': [
            {'value': choice[0], 'label': choice[1]}
            for choice in DeliverableType.choices
        ]
    })


# =============================================================================
# Helper Functions
# =============================================================================

def _serialize_deliverable(deliverable: Deliverable, include_content: bool = False) -> dict:
    """Serialize a deliverable to a JSON-compatible dict."""
    # Determine source: user-initiated (PA chat) vs system (autonomous agents)
    source = 'user' if deliverable.user is not None else 'system'

    data = {
        'id': str(deliverable.id),
        'title': deliverable.title,
        'slug': deliverable.slug,
        'deliverable_type': deliverable.deliverable_type,
        'category': deliverable.category,
        'tags': deliverable.tags or [],
        'agent_name': deliverable.agent_name,
        'agent_task': deliverable.agent_task,
        'preview_content': deliverable.preview_content,
        'thumbnail_url': deliverable.thumbnail_url,
        'quality_score': deliverable.quality_score,
        'confidence_score': deliverable.confidence_score,
        'is_saved': deliverable.is_saved,
        'is_template': deliverable.is_template,
        'is_starred': deliverable.is_starred,
        'clone_count': deliverable.clone_count,
        'is_cloned': deliverable.is_cloned,
        'execution_time_ms': deliverable.execution_time_ms,
        'llm_cost': str(deliverable.llm_cost),
        'word_count': deliverable.word_count,
        'line_count': deliverable.line_count,
        'status': deliverable.status,
        'source': source,
        'created_at': deliverable.created_at.isoformat(),
        'updated_at': deliverable.updated_at.isoformat(),
    }

    if include_content:
        data['content'] = deliverable.content
        data['content_format'] = deliverable.content_format
        data['tool_calls'] = deliverable.tool_calls or []
        data['raw_output'] = deliverable.raw_output or {}
        data['metadata'] = deliverable.metadata or {}

        # Include source operation info if available
        if deliverable.source_operation:
            data['source_operation'] = {
                'id': str(deliverable.source_operation.id),
                'operation_type': deliverable.source_operation.operation_type,
                'file_path': deliverable.source_operation.file_path,
            }

    return data


def _export_to_html(deliverable: Deliverable) -> str:
    """Export deliverable content to HTML."""
    import markdown

    # Convert markdown to HTML if needed
    if deliverable.content_format == 'markdown':
        content_html = markdown.markdown(
            deliverable.content,
            extensions=['fenced_code', 'tables', 'toc']
        )
    elif deliverable.content_format == 'html':
        content_html = deliverable.content
    else:
        # Wrap plain text in pre tag
        content_html = f"<pre>{deliverable.content}</pre>"

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{deliverable.title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
        h1 {{ color: #333; }}
        .meta {{ color: #666; font-size: 0.9em; margin-bottom: 20px; }}
        pre {{ background: #f4f4f4; padding: 15px; overflow-x: auto; }}
        code {{ background: #f4f4f4; padding: 2px 5px; }}
    </style>
</head>
<body>
    <h1>{deliverable.title}</h1>
    <div class="meta">
        <p>Agent: {deliverable.agent_name} | Type: {deliverable.deliverable_type} | Category: {deliverable.category}</p>
        <p>Created: {deliverable.created_at.strftime('%Y-%m-%d %H:%M')}</p>
    </div>
    <div class="content">
        {content_html}
    </div>
</body>
</html>"""


def _export_to_markdown(deliverable: Deliverable) -> str:
    """Export deliverable content to Markdown."""
    return f"""# {deliverable.title}

**Agent:** {deliverable.agent_name}
**Type:** {deliverable.deliverable_type}
**Category:** {deliverable.category}
**Created:** {deliverable.created_at.strftime('%Y-%m-%d %H:%M')}

---

{deliverable.content}
"""


@require_POST
def record_deliverable_event(request, deliverable_id):
    """
    Record a user interaction event on a deliverable.

    POST body (JSON):
        event_type: one of synthesis_viewed, deliverable_saved,
                    deliverable_exported, shared, task_created,
                    followup_created, action_taken
        metadata: optional dict of extra context
    """
    import json

    valid_types = {c[0] for c in DeliverableEvent.EVENT_TYPES}

    try:
        deliverable = get_object_or_404(Deliverable, id=deliverable_id)

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        event_type = body.get('event_type', '')
        if event_type not in valid_types:
            return JsonResponse({
                'success': False,
                'error': f'Invalid event_type. Must be one of: {sorted(valid_types)}'
            }, status=400)

        meta = body.get('metadata', {})
        if not isinstance(meta, dict):
            meta = {}

        _emit_event(deliverable, event_type, request.user, 'api', meta)

        return JsonResponse({'success': True, 'event_type': event_type})

    except Exception as e:
        logger.error(f"Error recording event for {deliverable_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
