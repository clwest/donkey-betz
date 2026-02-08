"""
Session 962 Phase 2: Strategic Memory API Endpoints

Provides read-only API access to the strategic memory layer:
- Precedent search across all memory sources
- Failure signature aggregation
- Strategy recommendations
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from core.services.strategic_memory_service import get_strategic_memory_service

logger = logging.getLogger(__name__)


@require_GET
def memory_precedents(request):
    """GET /api/memory/precedents/?q=...&top_k=10 - Search for precedents."""
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'error': 'q parameter is required'}, status=400)

    top_k = min(int(request.GET.get('top_k', 10)), 50)
    full = request.GET.get('full', '0') == '1'
    include_embeddings = request.GET.get('include_embeddings', '0') == '1'

    svc = get_strategic_memory_service()
    result = svc.query_precedents(query=query, top_k=top_k, include_embeddings=include_embeddings)

    # Truncate summaries unless full=1
    if not full:
        for r in result.get('results', []):
            r['summary'] = (r.get('summary') or '')[:200]

    return JsonResponse(result)


@require_GET
def memory_failures(request):
    """GET /api/memory/failures/?domain=...&top_k=10 - Failure signatures."""
    domain = request.GET.get('domain', '') or None
    top_k = min(int(request.GET.get('top_k', 10)), 50)

    svc = get_strategic_memory_service()
    result = svc.get_failure_signatures(domain=domain, top_k=top_k)

    return JsonResponse(result)


@require_GET
def memory_strategy(request):
    """GET /api/memory/strategy/?objective=...&top_k=5 - Strategy recommendations."""
    objective = request.GET.get('objective', '')
    if not objective:
        return JsonResponse({'error': 'objective parameter is required'}, status=400)

    top_k = min(int(request.GET.get('top_k', 5)), 20)
    include_embeddings = request.GET.get('include_embeddings', '0') == '1'

    svc = get_strategic_memory_service()
    result = svc.recommend_strategy(objective=objective, top_k=top_k, include_embeddings=include_embeddings)

    # Truncate precedent summaries in strategy response
    for r in result.get('precedents', []):
        r['summary'] = (r.get('summary') or '')[:200]

    return JsonResponse(result)
