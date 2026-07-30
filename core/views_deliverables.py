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

import json
import logging
from datetime import timedelta
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from core.auth_middleware import token_auth_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Min
from django.utils import timezone
from django.shortcuts import get_object_or_404

from core.security import scope_queryset_deliverable, can_read_deliverable
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
        - owner: 'me' → filter to request.user's rows; '<user_id>' → filter to
          that user (staff/superuser only — non-staff passing a non-self id is
          coerced to self). Wires the existing Deliverable.user FK. PR 4 of
          the RaaS UI arc will formalize the operator-vs-customer role guard
          around the arbitrary-user-id branch.
        - search: Search in title and content
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20, max: 100)
    """
    try:
        # Base queryset — exclude archived by default (Session 1077).
        # I-0302 Phase 3 Sub-phase D1 (2026-07-10): Option A staff-tightening —
        # replace the legacy `is_staff sees ALL deliverables` bypass with the
        # ratified predicate. Non-staff still sees only their own workspaces;
        # staff sees their own workspaces + workspace-null rows (Phase 2 §6.1
        # F3 amendment — staff carve-out is workspace-null only, NOT
        # cross-user). Anonymous callers receive `.none()` via `_authed()`.
        show_archived = request.GET.get('include_archived', '').lower() == 'true'
        queryset = scope_queryset_deliverable(
            request.user,
            Deliverable.objects.all(),
        )
        if not show_archived:
            queryset = queryset.exclude(status='archived')

        # Additional optional filter — restrict to a specific workspace.
        workspace_id = request.GET.get('workspace')
        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)

        # S3050 PR 1 (RaaS UI arc Phase 2, Gap 4 / Gap 2 backend / Gap 7):
        # per-user ownership filter layered ON TOP of workspace-scoping.
        # Coercion rule: non-staff callers passing an arbitrary user id are
        # coerced to self (defense against a customer-role user hand-crafting
        # `owner=<other-id>` before PR 4 lands the DRF role guard).
        owner = request.GET.get('owner')
        if owner and getattr(request.user, 'is_authenticated', False):
            if owner == 'me':
                queryset = queryset.filter(user=request.user)
            elif getattr(request.user, 'is_staff', False) or getattr(request.user, 'is_superuser', False):
                queryset = queryset.filter(user_id=owner)
            else:
                queryset = queryset.filter(user=request.user)

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
@token_auth_required
def get_deliverable(request, deliverable_id):
    """Get a single deliverable with full content."""
    try:
        # I-0302 §5.1.b hotfix extension (2026-07-10, S2748 Sub-phase 2):
        # added @token_auth_required. Pre-hotfix, the endpoint had NO
        # auth gate and the access-check guard `if deliverable.user and
        # request.user.is_authenticated:` skipped the ENTIRE access check
        # for anonymous callers — any anonymous caller with knowledge of
        # a deliverable id received 200 + full content. Surfaced by
        # Phase 4 harness `TestMatrixDeliverableGetItem.
        # test_anonymous_blocked_or_scoped` with Rigby Q2 Edit 2 content-
        # leak assertion. Ledger amendment: I-030201 §5.1.b (5th site).
        #
        # NOT changed in this hotfix (preserved carve-outs):
        # - VIP scope carve-out: authenticated non-owner non-staff with
        #   `scope.is_vip and scope.workspace_id == deliverable.workspace_id`
        #   still gets access. VIP substrate is a real product feature,
        #   not scope-creepable in this hotfix.
        # - Staff bypass: authenticated staff (non-superuser) still gets
        #   access. §5.1.a Option A tightening applied to LIST + stats
        #   only; get_deliverable was outside D1 scope. Sub-phase 3 can
        #   evaluate whether to extend Option A tightening here.
        deliverable = get_object_or_404(Deliverable, id=deliverable_id)

        # Check access permissions (now that request.user.is_authenticated
        # is guaranteed True by @token_auth_required).
        if deliverable.user:
            if deliverable.user != request.user and not request.user.is_staff:
                # Allow VIP users to view deliverables in their assigned workspace
                vip_allowed = False
                if deliverable.workspace_id:
                    try:
                        from core.vip_scope import get_vip_scope
                        scope = get_vip_scope(request)
                        if scope.is_vip and scope.workspace_id == str(deliverable.workspace_id):
                            vip_allowed = True
                    except Exception as _e:
                        logger.warning(
                            "views_deliverables.get_deliverable: swallowed (%s: %s) — degraded",
                            type(_e).__name__, _e,
                        )
                if not vip_allowed:
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

    except Http404:
        # Let 404 propagate — bare `except Exception` below would convert
        # get_object_or_404's 404 into a 500 (5th site of the pattern
        # documented in §5.1.b tail).
        raise
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

    except Http404:
        # I-0302 §14 batch-fix (S2749): let 404 propagate — bare `except Exception`
        # would convert get_object_or_404's Http404 into 500. Detected by
        # tests/security/test_i0302_p4_ast_conformance.py.
        raise
    except Exception as e:
        logger.error(f"Error saving deliverable {deliverable_id}: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_POST
@token_auth_required
def delete_deliverable(request, deliverable_id):
    """Permanently delete a deliverable."""
    try:
        # I-0302 Phase 3 Sub-phase D1 hotfix (2026-07-10, S2748): scope
        # the source fetch — prior code used `get_object_or_404(Deliverable,
        # id=deliverable_id)` with no ownership filter, which let any
        # authenticated caller DELETE any deliverable whose id they knew.
        # Missed by the original D1 12-site sweep; surfaced during Phase 4
        # harness endpoint discovery. Mirrors the clone_deliverable
        # source-fetch pattern from D1 (line 306 in this file).
        # Ledger amendment: I-030201 §5.1.b.
        deliverable = get_object_or_404(
            scope_queryset_deliverable(request.user, Deliverable.objects.all()),
            id=deliverable_id,
        )
        title = deliverable.title
        deliverable.delete()
        return JsonResponse({
            'success': True,
            'message': f'Deleted: {title}',
        })
    except Http404:
        # Let 404 propagate — bare `except Exception` below would convert
        # the scoped-source-fetch's 404 into a 500 (mirrors clone_deliverable
        # D1 pattern; regression discovered by S2748 harness endpoint
        # discovery, see §5.1.b).
        raise
    except Exception as e:
        logger.error(f"Error deleting deliverable {deliverable_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


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

    except Http404:
        # I-0302 §5.1.b extension (S2748 Sub-phase 2): let 404 propagate.
        # Broader `except Exception` below would convert the filter's 404
        # into a 500, breaking existence-oracle semantics. Same class as
        # the delete_deliverable fix from §5.1.b hotfix PR #3113.
        raise
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
        # I-0302 Phase 3 Sub-phase D1 (2026-07-10): scope the source
        # fetch — a caller must be authorized to read the deliverable
        # before they can clone it. Prior code fetched by id alone,
        # which let a caller clone any deliverable whose id they knew.
        original = get_object_or_404(
            scope_queryset_deliverable(request.user, Deliverable.objects.all()),
            id=deliverable_id,
        )

        # Create clone
        # Session 1091 — explicitly inherit workspace + initiative from the
        # original. Previously these were both omitted, so every clone became
        # an orphan (workspace=NULL) regardless of where the original lived.
        # Surfaced during the Workspace/Deliverable Flow Verification Sprint.
        clone = Deliverable.objects.create(
            title=f"Copy of {original.title}"[:255],
            deliverable_type=original.deliverable_type,
            category=original.category,
            tags=original.tags.copy() if original.tags else [],
            agent_name=original.agent_name,
            agent_task=original.agent_task,
            user=request.user,
            workspace=original.workspace,
            initiative=original.initiative,
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

    except Http404:
        # Let 404 propagate — bare `except Exception` would convert the
        # scoped-source-fetch's 404 into a 500 (regression discovered by
        # I-0302 Phase 3 Sub-phase D1 test suite).
        raise
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

    except Http404:
        # I-0302 §5.1.b extension (S2748 Sub-phase 2): let 404 propagate.
        # Same class as delete_deliverable/unsave_deliverable fix.
        raise
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

        elif export_format == 'pdf':
            try:
                from core.services.pdf_export_service import generate_deliverable_pdf_bytes
                pdf_bytes = generate_deliverable_pdf_bytes(
                    title=deliverable.title,
                    content=deliverable.content or '',
                    content_format=deliverable.content_format or 'markdown',
                )

                # Upload to Cloudinary for shareable URL if requested
                share_url = None
                upload_param = body.get('upload', '') if isinstance(body, dict) else ''
                if upload_param == 'cloudinary':
                    try:
                        from django.core.files.storage import default_storage
                        from django.core.files.base import ContentFile
                        import hashlib
                        content_hash = hashlib.md5(pdf_bytes).hexdigest()[:8]
                        cloud_path = f'exports/pdf/{deliverable.slug}-{content_hash}.pdf'
                        saved_path = default_storage.save(cloud_path, ContentFile(pdf_bytes))
                        share_url = default_storage.url(saved_path)
                    except Exception as upload_err:
                        logger.warning("Cloudinary upload failed for PDF: %s", upload_err)

                export_record = DeliverableExport.objects.create(
                    deliverable=deliverable,
                    user=request.user,
                    export_format='pdf',
                    file_size_bytes=len(pdf_bytes),
                    file_url=share_url or '',
                )
                _emit_event(deliverable, 'deliverable_exported', request.user, 'frontend',
                             {'format': 'pdf', 'share_url': share_url})

                if share_url:
                    return JsonResponse({
                        'success': True,
                        'format': 'pdf',
                        'share_url': share_url,
                        'export_id': str(export_record.id),
                        'file_size': len(pdf_bytes),
                    })

                response = HttpResponse(pdf_bytes, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{deliverable.slug}.pdf"'
                return response
            except Exception:
                logger.exception("PDF export failed for deliverable_id=%s", deliverable_id)
                return JsonResponse(
                    {'success': False, 'error': 'PDF export failed', 'format': 'pdf'},
                    status=500,
                )

        else:
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

    except Http404:
        # I-0302 §14 batch-fix (S2749): let 404 propagate — bare `except Exception`
        # would convert get_object_or_404's Http404 into 500. Detected by
        # tests/security/test_i0302_p4_ast_conformance.py.
        raise
    except Exception as e:
        logger.error(f"Error exporting deliverable {deliverable_id}: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_POST
@token_auth_required
def link_deliverable_workspace(request, deliverable_id):
    """Link a deliverable to a workspace (set workspace FK)."""
    import json

    try:
        # I-0302 §5.1.b hotfix (2026-07-10, S2748): scope BOTH the source
        # deliverable fetch AND the target workspace fetch. Pre-hotfix, an
        # authenticated caller could rewrite the workspace FK of any
        # deliverable whose id they knew AND link it to any workspace by
        # id — hijacking unclaimed deliverables into their own workspace
        # OR dumping their own deliverable into another user's workspace.
        # Source-fetch: predicate scoping. Target workspace: authoritative
        # `user_can_access_workspace` primitive.
        deliverable = get_object_or_404(
            scope_queryset_deliverable(request.user, Deliverable.objects.all()),
            id=deliverable_id,
        )

        body = json.loads(request.body) if request.body else {}
        workspace_id = body.get('workspace_id', '')
        if not workspace_id:
            return JsonResponse({'success': False, 'error': 'workspace_id is required'}, status=400)

        from core.security import user_can_access_workspace
        from core.models_skin_layer import ProjectWorkspace
        if not user_can_access_workspace(request.user, workspace_id):
            return JsonResponse(
                {'success': False, 'error': 'Access denied to target workspace'},
                status=404,
            )
        workspace = get_object_or_404(ProjectWorkspace, id=workspace_id)

        # Don't overwrite if already linked to a different workspace
        if deliverable.workspace_id and str(deliverable.workspace_id) != str(workspace_id):
            return JsonResponse({
                'success': False,
                'error': f'Already linked to workspace {deliverable.workspace_id}',
            }, status=409)

        deliverable.workspace = workspace
        deliverable.save(update_fields=['workspace', 'updated_at'])

        return JsonResponse({
            'success': True,
            'deliverable_id': str(deliverable.id),
            'workspace_id': str(workspace.id),
            'workspace_name': workspace.name,
        })

    except Http404:
        # Let 404 propagate for both the predicate-scoped source-fetch
        # AND target workspace access denial. See delete_deliverable §5.1.b.
        raise
    except Exception as e:
        logger.error(f"Error linking deliverable {deliverable_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_GET
def get_deliverable_stats(request):
    """Get statistics about deliverables."""
    try:
        # Base queryset — exclude archived by default (Session 1077).
        # I-0302 Phase 3 Sub-phase D1 (2026-07-10): Option A staff-tightening.
        queryset = scope_queryset_deliverable(
            request.user, Deliverable.objects.exclude(status='archived'),
        )

        # Session 1077: Scope stats to workspace when specified
        workspace_id = request.GET.get('workspace')
        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)

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

        # By category — return all for dropdown filter (Session 1077)
        by_category = list(
            queryset.exclude(category='')
            .values('category')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # By agent
        by_agent = list(
            queryset.values('agent_name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        # Session 1091 Sprint B — workspace breakdown.
        # `orphan` (workspace_id IS NULL) and `unassigned` (lives in the
        # per-user "Unassigned" sentinel bucket) are tracked separately —
        # they are different failure modes:
        # - orphan_count > 0 means the factory's Unassigned-bucket fallback
        #   leaked (regression of PR #1965).
        # - unassigned_count > 0 just means agents are creating deliverables
        #   without explicit workspace assignment, which is the current
        #   designed-correct behavior; it surfaces volume worth triaging.
        by_workspace_rows = list(
            queryset.values('workspace_id', 'workspace__name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        by_workspace = [
            {
                'workspace_id': str(r['workspace_id']) if r['workspace_id'] else None,
                'workspace_name': r['workspace__name'] or 'Orphan (no workspace)',
                'count': r['count'],
                'is_orphan': r['workspace_id'] is None,
                'is_unassigned': r['workspace__name'] == 'Unassigned',
            }
            for r in by_workspace_rows
        ]
        orphan_count = queryset.filter(workspace_id__isnull=True).count()
        unassigned_count = queryset.filter(workspace__name='Unassigned').count()

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
                'by_workspace': by_workspace,
                'orphan_count': orphan_count,
                'unassigned_count': unassigned_count,
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
        # Session 1091 — surface workspace assignment for UI rendering.
        # The PA tool (deliverable_tool.list) already returns these via
        # td_handlers_agents._LIST_FIELDS; the REST endpoint that the
        # React DeliverablesTab actually consumes was still missing them,
        # so the workspace badge / orphan indicator had nothing to render.
        'workspace_id': str(deliverable.workspace_id) if deliverable.workspace_id else None,
        'workspace_name': deliverable.workspace.name if deliverable.workspace_id and deliverable.workspace else None,
        'is_orphan': deliverable.workspace_id is None,
    }

    # Session 1077: Include initiative context if linked
    if deliverable.initiative_id:
        data['initiative'] = {
            'id': str(deliverable.initiative_id),
            'name': deliverable.initiative.name if deliverable.initiative else None,
        }
    else:
        data['initiative'] = None

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


@require_GET
def stage3_dashboard(request):
    """
    Stage 3 Evaluation Dashboard — ATR-24h metrics for the
    Capitalize Opportunity initiative pilot.

    Returns headline KPIs, funnel, role breakdown, and top producers.
    """
    try:
        ACTION_TYPES = [
            'action_taken', 'task_created', 'followup_created',
            'deliverable_exported', 'shared', 'deliverable_saved',
        ]
        VIEW_TYPES = ['synthesis_viewed']

        # ── Syntheses queryset ──────────────────────────────────────
        # I-0302 Phase 3 Sub-phase D1 (2026-07-10): scope via predicate
        # so this dashboard aggregate doesn't leak cross-workspace counts.
        syntheses = scope_queryset_deliverable(
            request.user,
            Deliverable.objects.filter(
                category='Initiatives',
                tags__contains=['initiative:capitalize-opportunity'],
            ),
        ).filter(
            Q(title__istartswith='Synthesis') | Q(deliverable_type__icontains='synthesis')
        )

        total_syntheses = syntheses.count()

        if total_syntheses == 0:
            return JsonResponse({'success': True, 'dashboard': {
                'headline': {
                    'total_syntheses': 0, 'atr_24h': 0,
                    'median_hours_to_action': None, 'viewed_rate': 0,
                },
                'funnel': [],
                'by_role': [],
                'top_agents': [],
                'gate': {'status': 'NO_DATA', 'details': {}},
            }})

        synth_ids = set(syntheses.values_list('id', flat=True))
        synth_created = {
            str(s['id']): s['created_at']
            for s in syntheses.values('id', 'created_at')
        }

        # ── Events queryset ─────────────────────────────────────────
        all_events = DeliverableEvent.objects.filter(deliverable_id__in=synth_ids)

        # Actions: first action per deliverable
        action_events = (
            all_events.filter(event_type__in=ACTION_TYPES)
            .values('deliverable_id')
            .annotate(first_action=Min('created_at'))
        )
        first_actions = {
            str(row['deliverable_id']): row['first_action']
            for row in action_events
        }

        # Views: unique deliverables viewed
        viewed_ids = set(
            str(x) for x in
            all_events.filter(event_type__in=VIEW_TYPES)
            .values_list('deliverable_id', flat=True).distinct()
        )

        # Saved/exported/shared
        save_export_share_ids = set(
            str(x) for x in
            all_events.filter(event_type__in=['deliverable_saved', 'deliverable_exported', 'shared'])
            .values_list('deliverable_id', flat=True).distinct()
        )

        # ── Compute ATR-24h overall ────────────────────────────────
        acted_24h = 0
        hours_to_action_list = []
        for sid_str, created_at in synth_created.items():
            fa = first_actions.get(sid_str)
            if fa and fa <= created_at + timedelta(hours=24):
                acted_24h += 1
                delta_hours = (fa - created_at).total_seconds() / 3600.0
                hours_to_action_list.append(delta_hours)

        atr_24h = round(acted_24h / total_syntheses, 4) if total_syntheses else 0

        # Median hours
        median_hours = None
        if hours_to_action_list:
            sorted_h = sorted(hours_to_action_list)
            mid = len(sorted_h) // 2
            if len(sorted_h) % 2 == 0:
                median_hours = round((sorted_h[mid - 1] + sorted_h[mid]) / 2, 2)
            else:
                median_hours = round(sorted_h[mid], 2)

        viewed_count = len(viewed_ids & {str(s) for s in synth_ids})
        saved_exported_shared_count = len(save_export_share_ids & {str(s) for s in synth_ids})

        # ── Headline KPIs ───────────────────────────────────────────
        headline = {
            'total_syntheses': total_syntheses,
            'atr_24h': round(atr_24h * 100, 1),
            'median_hours_to_action': median_hours,
            'viewed_rate': round(viewed_count / total_syntheses * 100, 1) if total_syntheses else 0,
        }

        # ── Funnel ──────────────────────────────────────────────────
        funnel = [
            {'step': 'Syntheses generated', 'count': total_syntheses, 'pct': 100.0},
            {'step': 'Viewed/opened', 'count': viewed_count,
             'pct': round(viewed_count / total_syntheses * 100, 1) if total_syntheses else 0},
            {'step': 'Saved/exported/shared', 'count': saved_exported_shared_count,
             'pct': round(saved_exported_shared_count / total_syntheses * 100, 1) if total_syntheses else 0},
            {'step': 'Action taken (<=24h)', 'count': acted_24h,
             'pct': round(acted_24h / total_syntheses * 100, 1) if total_syntheses else 0},
        ]

        # ── Role breakdown ──────────────────────────────────────────
        def _get_role(d):
            tags = d.tags or []
            for t in tags:
                if t.startswith('role:'):
                    return t.split(':', 1)[1]
            title_lower = (d.title or '').lower()
            if 'manager' in title_lower:
                return 'manager'
            if 'recruiter' in title_lower:
                return 'recruiter'
            if 'developer' in title_lower:
                return 'developer'
            return 'unknown'

        role_data = {}
        for d in syntheses.only('id', 'title', 'tags', 'created_at'):
            role = _get_role(d)
            if role not in role_data:
                role_data[role] = {'total': 0, 'viewed': 0, 'saved': 0, 'acted': 0, 'hours': []}
            role_data[role]['total'] += 1
            sid_str = str(d.id)
            if sid_str in viewed_ids:
                role_data[role]['viewed'] += 1
            if sid_str in save_export_share_ids:
                role_data[role]['saved'] += 1
            fa = first_actions.get(sid_str)
            if fa and fa <= d.created_at + timedelta(hours=24):
                role_data[role]['acted'] += 1
                role_data[role]['hours'].append((fa - d.created_at).total_seconds() / 3600.0)

        by_role = []
        for role, rd in sorted(role_data.items()):
            total_r = rd['total']
            atr_r = round(rd['acted'] / total_r * 100, 1) if total_r else 0
            med_h = None
            if rd['hours']:
                sh = sorted(rd['hours'])
                m = len(sh) // 2
                med_h = round((sh[m - 1] + sh[m]) / 2, 2) if len(sh) % 2 == 0 else round(sh[m], 2)
            by_role.append({
                'role': role,
                'syntheses': total_r,
                'viewed': rd['viewed'],
                'saved_exported_shared': rd['saved'],
                'acted_24h': rd['acted'],
                'atr_24h': atr_r,
                'median_hours': med_h,
            })

        # ── Top agents ──────────────────────────────────────────────
        agent_map = {}
        for d in syntheses.only('id', 'agent_name', 'created_at'):
            aname = d.agent_name or 'Unknown'
            if aname not in agent_map:
                agent_map[aname] = {'total': 0, 'acted': 0}
            agent_map[aname]['total'] += 1
            fa = first_actions.get(str(d.id))
            if fa and fa <= d.created_at + timedelta(hours=24):
                agent_map[aname]['acted'] += 1

        top_agents = sorted(
            [
                {'agent': name, 'syntheses': v['total'], 'acted_24h': v['acted'],
                 'atr_24h': round(v['acted'] / v['total'] * 100, 1) if v['total'] else 0}
                for name, v in agent_map.items()
            ],
            key=lambda x: (-x['atr_24h'], -x['syntheses']),
        )[:10]

        # ── Stage gate assessment ───────────────────────────────────
        overall_pct = headline['atr_24h']
        real_roles = [r for r in by_role if r['role'] != 'unknown']
        roles_below_min_n = [r['role'] for r in real_roles if r['syntheses'] < 10]
        roles_below_15 = [r['role'] for r in real_roles if r['syntheses'] >= 10 and r['atr_24h'] < 15]

        # Insufficient data: need >= 40 overall and >= 10 per role to evaluate
        if total_syntheses < 40 or roles_below_min_n:
            gate_status = 'INSUFFICIENT_DATA'
        elif overall_pct >= 25 and not roles_below_15:
            gate_status = 'APPROVED'
        elif overall_pct >= 25 and len(roles_below_15) <= 1:
            gate_status = 'CONDITIONAL'
        elif overall_pct < 20 or len(roles_below_15) >= 2:
            gate_status = 'FAILED'
        else:
            gate_status = 'IN_PROGRESS'

        gate = {
            'status': gate_status,
            'details': {
                'atr_overall': overall_pct,
                'atr_target': 25,
                'roles_below_15': roles_below_15,
                'roles_insufficient_data': roles_below_min_n,
                'total_syntheses': total_syntheses,
                'min_overall': 40,
                'min_per_role': 10,
            }
        }

        return JsonResponse({'success': True, 'dashboard': {
            'headline': headline,
            'funnel': funnel,
            'by_role': by_role,
            'top_agents': top_agents,
            'gate': gate,
        }})

    except Exception as e:
        logger.error("Stage 3 dashboard error: %s", e, exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
@token_auth_required
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
        # I-0302 §5.1.b hotfix (2026-07-10, S2748): (a) added
        # @token_auth_required decorator — previously anonymous callers
        # could emit audit events on any deliverable, poisoning the
        # DeliverableEvent audit log; (b) scoped source-fetch via
        # scope_queryset_deliverable so authenticated non-owners can't
        # attribute events (e.g., fake "shared") to another user's row.
        deliverable = get_object_or_404(
            scope_queryset_deliverable(request.user, Deliverable.objects.all()),
            id=deliverable_id,
        )

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

    except Http404:
        # Let 404 propagate — bare `except Exception` below would convert
        # the scoped-source-fetch's 404 into a 500 (mirrors delete_deliverable
        # §5.1.b pattern).
        raise
    except Exception as e:
        logger.error(f"Error recording event for {deliverable_id}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
