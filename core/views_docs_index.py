"""
API endpoints for serving the documentation index.

Provides access to docs/_index.json for the frontend DocDetailsPanel
and DocsIndexPage components.
"""
import json
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET


import logging
logger = logging.getLogger(__name__)

def _load_index():
    """Load the documentation index from disk."""
    index_path = Path(settings.BASE_DIR) / 'docs' / '_index.json'
    if not index_path.exists():
        return None

    try:
        with open(index_path, 'r') as f:
            return json.load(f)
    except Exception as _e:
        logger.warning(
            "views_docs_index._load_index: swallowed (%s: %s) — returning default",
            type(_e).__name__, _e,
        )
        return None


@require_GET
def docs_index(request):
    """
    GET /api/docs/index/

    Returns the full documentation index with optional filtering.

    Query params:
        - status: Filter by status (active, superseded, deprecated, draft)
        - type: Filter by document type
        - subsystem: Filter by subsystem
        - search: Search in path and title
        - limit: Limit number of results (default: all)
    """
    index = _load_index()
    if not index:
        return JsonResponse({
            'error': 'Documentation index not found. Run: python manage.py build_docs_index'
        }, status=404)

    documents = index.get('documents', [])

    # Apply filters
    status_filter = request.GET.get('status')
    type_filter = request.GET.get('type')
    subsystem_filter = request.GET.get('subsystem')
    search_query = request.GET.get('search', '').lower()
    limit = request.GET.get('limit')

    if status_filter:
        documents = [d for d in documents if d.get('status') == status_filter]

    if type_filter:
        documents = [d for d in documents if d.get('type') == type_filter]

    if subsystem_filter:
        documents = [d for d in documents if subsystem_filter in d.get('subsystems', [])]

    if search_query:
        documents = [
            d for d in documents
            if search_query in d.get('path', '').lower()
            or search_query in d.get('title', '').lower()
        ]

    if limit:
        try:
            documents = documents[:int(limit)]
        except ValueError:
            pass

    return JsonResponse({
        'generated_at': index.get('generated_at'),
        'version': index.get('version'),
        'total_count': len(index.get('documents', [])),
        'filtered_count': len(documents),
        'documents': documents,
        'graph': index.get('graph', {}),
        'filters': {
            'statuses': list(index.get('by_status', {}).keys()),
            'types': list(index.get('by_type', {}).keys()),
            'subsystems': list(index.get('by_subsystem', {}).keys()),
        }
    })


@require_GET
def docs_detail(request, doc_path):
    """
    GET /api/docs/detail/<path:doc_path>/

    Returns details for a specific document including:
    - Full metadata
    - Outbound links with context
    - Inbound links (documents that reference this one)
    """
    index = _load_index()
    if not index:
        return JsonResponse({
            'error': 'Documentation index not found. Run: python manage.py build_docs_index'
        }, status=404)

    # Find the document
    doc = None
    for d in index.get('documents', []):
        if d.get('path') == doc_path:
            doc = d
            break

    if not doc:
        return JsonResponse({'error': f'Document not found: {doc_path}'}, status=404)

    # Find inbound links (documents that reference this one)
    inbound_links = []
    for d in index.get('documents', []):
        if d.get('path') == doc_path:
            continue
        for link in d.get('outbound_links', []):
            target = link.get('target') if isinstance(link, dict) else link
            if target == doc_path:
                inbound_links.append({
                    'source': d.get('path'),
                    'title': d.get('title'),
                    'occurrences': link.get('occurrences', 1) if isinstance(link, dict) else 1,
                    'snippets': link.get('snippets', []) if isinstance(link, dict) else [],
                })
                break

    # Sort by occurrences
    inbound_links.sort(key=lambda x: x.get('occurrences', 0), reverse=True)

    return JsonResponse({
        'document': doc,
        'inbound_links': inbound_links[:20],  # Top 20
        'inbound_count': len(inbound_links),
        'is_orphan': doc.get('inbound_links_count', 0) == 0 and len(doc.get('outbound_links', [])) == 0,
    })


@require_GET
def docs_graph_summary(request):
    """
    GET /api/docs/graph/

    Returns the cross-reference graph summary.
    """
    index = _load_index()
    if not index:
        return JsonResponse({
            'error': 'Documentation index not found. Run: python manage.py build_docs_index'
        }, status=404)

    graph = index.get('graph', {})

    return JsonResponse({
        'total_links': graph.get('total_links', 0),
        'most_referenced': graph.get('most_referenced', []),
        'orphan_docs': graph.get('orphan_docs', []),
        'broken_links': graph.get('broken_links', []),
        'stats': {
            'total_documents': len(index.get('documents', [])),
            'by_status': {k: len(v) for k, v in index.get('by_status', {}).items()},
            'by_type': {k: len(v) for k, v in index.get('by_type', {}).items()},
        }
    })


@require_GET
def docs_stats(request):
    """
    GET /api/docs/stats/

    Returns documentation statistics for dashboard widgets.
    """
    index = _load_index()
    if not index:
        return JsonResponse({
            'error': 'Documentation index not found'
        }, status=404)

    documents = index.get('documents', [])
    graph = index.get('graph', {})

    # Calculate stats
    total_lines = sum(d.get('lines', 0) for d in documents)
    with_frontmatter = sum(1 for d in documents if d.get('has_frontmatter'))

    return JsonResponse({
        'total_documents': len(documents),
        'total_lines': total_lines,
        'with_frontmatter': with_frontmatter,
        'by_status': {k: len(v) for k, v in index.get('by_status', {}).items()},
        'by_type': {k: len(v) for k, v in index.get('by_type', {}).items()},
        'graph': {
            'total_links': graph.get('total_links', 0),
            'broken_links': len(graph.get('broken_links', [])),
            'orphan_docs': len(graph.get('orphan_docs', [])),
        },
        'generated_at': index.get('generated_at'),
        'version': index.get('version'),
    })
