"""
PDF Export API Views
====================

Session 918: API endpoints for downloading reports as PDFs.

Endpoints:
- GET /api/reports/pdf/<operation_id>/ - Download workspace operation as PDF
- POST /api/reports/pdf/generate/ - Generate PDF from content
"""

import logging
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_operation_pdf(request, operation_id):
    """
    Download a WorkspaceOperation as PDF.

    GET /api/reports/pdf/<operation_id>/

    Returns:
        PDF file download
    """
    try:
        from core.services.pdf_export_service import get_pdf_export_service
        from core.models_skin_layer import WorkspaceOperation

        # Verify operation exists and user has access
        try:
            operation = WorkspaceOperation.objects.get(id=operation_id)
        except WorkspaceOperation.DoesNotExist:
            return JsonResponse({'error': 'Operation not found'}, status=404)

        # Generate PDF
        service = get_pdf_export_service()
        pdf_bytes = service.generate_from_operation(operation_id)

        # Build filename
        agent_name = operation.agent_name or 'report'
        safe_name = agent_name.replace(' ', '_').lower()
        filename = f"{safe_name}_{operation_id[:8]}.pdf"

        # Return PDF response
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(pdf_bytes)

        logger.info(f"PDF download: {filename} ({len(pdf_bytes)} bytes)")
        return response

    except ImportError as e:
        logger.error(f"PDF generation unavailable: {e}")
        return JsonResponse({
            'error': 'PDF generation not available',
            'detail': 'WeasyPrint is not installed'
        }, status=503)
    except Exception as e:
        logger.error(f"PDF generation failed: {e}", exc_info=True)
        return JsonResponse({
            'error': 'PDF generation failed',
            'detail': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_pdf(request):
    """
    Generate PDF from provided content.

    POST /api/reports/pdf/generate/

    Body:
        {
            "title": "Report Title",
            "content": "Markdown content...",
            "category": "sports|financial|blockchain|narrative|strategy|research",
            "agent_name": "AgentName",
            "provenance": {...},  // Optional
        }

    Returns:
        PDF file download
    """
    try:
        from core.services.pdf_export_service import generate_pdf as gen_pdf

        data = request.data

        title = data.get('title', 'Report')
        content = data.get('content', '')
        category = data.get('category', 'default')
        agent_name = data.get('agent_name', '')
        provenance = data.get('provenance')

        if not content:
            return JsonResponse({'error': 'Content is required'}, status=400)

        # Generate PDF
        pdf_bytes = gen_pdf(
            title=title,
            content=content,
            category=category,
            agent_name=agent_name,
            provenance=provenance,
        )

        # Build filename
        safe_title = title.replace(' ', '_').lower()[:30]
        filename = f"{safe_title}.pdf"

        # Return PDF response
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(pdf_bytes)

        logger.info(f"PDF generated: {filename} ({len(pdf_bytes)} bytes)")
        return response

    except ImportError as e:
        logger.error(f"PDF generation unavailable: {e}")
        return JsonResponse({
            'error': 'PDF generation not available',
            'detail': 'WeasyPrint is not installed'
        }, status=503)
    except Exception as e:
        logger.error(f"PDF generation failed: {e}", exc_info=True)
        return JsonResponse({
            'error': 'PDF generation failed',
            'detail': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_exportable_operations(request):
    """
    List recent WorkspaceOperations that can be exported as PDF.

    GET /api/reports/pdf/list/

    Query params:
        - category: Filter by category (sports, financial, blockchain, etc.)
        - limit: Number of results (default 20, max 100)

    Returns:
        List of operations with PDF download URLs
    """
    try:
        from core.models_skin_layer import WorkspaceOperation
        from django.utils import timezone
        from datetime import timedelta

        category = request.query_params.get('category')
        limit = min(int(request.query_params.get('limit', 20)), 100)

        # Get recent operations
        cutoff = timezone.now() - timedelta(days=7)
        operations = WorkspaceOperation.objects.filter(
            created_at__gte=cutoff,
            success=True,
        ).order_by('-created_at')

        # Filter by category if specified
        if category:
            category_paths = {
                'sports': ['sports/'],
                'financial': ['financial/', 'stocks/'],
                'blockchain': ['blockchain/'],
                'narrative': ['narrative/'],
                'strategy': ['strategy/'],
                'research': ['research/', 'analysis/'],
            }
            paths = category_paths.get(category, [])
            if paths:
                from django.db.models import Q
                path_filters = Q()
                for path in paths:
                    path_filters |= Q(file_path__contains=path)
                operations = operations.filter(path_filters)

        operations = operations[:limit]

        results = []
        for op in operations:
            # Determine category from file path
            file_path = op.file_path or ''
            op_category = 'default'
            if 'financial' in file_path or 'stocks' in file_path:
                op_category = 'financial'
            elif 'sports' in file_path:
                op_category = 'sports'
            elif 'blockchain' in file_path:
                op_category = 'blockchain'
            elif 'narrative' in file_path:
                op_category = 'narrative'
            elif 'strategy' in file_path:
                op_category = 'strategy'
            elif 'research' in file_path:
                op_category = 'research'

            results.append({
                'id': str(op.id),
                'title': op.agent_task or f"Report from {op.agent_name}",
                'agent_name': op.agent_name,
                'category': op_category,
                'created_at': op.created_at.isoformat(),
                'file_path': op.file_path,
                'pdf_url': f"/api/reports/pdf/{op.id}/",
            })

        return JsonResponse({
            'count': len(results),
            'results': results,
        })

    except Exception as e:
        logger.error(f"Failed to list operations: {e}", exc_info=True)
        return JsonResponse({
            'error': 'Failed to list operations',
            'detail': str(e)
        }, status=500)
