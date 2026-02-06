"""
Session 954: RAG Observability API Views

Provides dashboard endpoints for monitoring the risk-aware RAG system:
- Document inventory stats (classifications, risk levels)
- Retrieval channel effectiveness
- Context budget utilization
- Risk boost impact analysis

Built on Session 949's risk-aware RAG infrastructure.
"""

import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .api_helpers import api_success, api_error


@csrf_exempt
@require_http_methods(["GET"])
def rag_observability_dashboard(request):
    """
    GET /api/rag/observability/dashboard/

    Get comprehensive RAG observability dashboard data.

    Returns:
        - document_inventory: Counts by risk level, document class, critical status
        - retrieval_channels: Channel usage and distribution
        - risk_boost: Boost effectiveness metrics
        - context_budget: Token utilization by tier
        - health_indicators: System health checks
        - summary: Key metrics for quick view
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status_code=401)

    from .services.rag_observability_service import get_rag_observability_service

    service = get_rag_observability_service()
    dashboard = service.get_dashboard_summary()

    return api_success(dashboard)


@csrf_exempt
@require_http_methods(["GET"])
def rag_document_inventory(request):
    """
    GET /api/rag/observability/inventory/

    Get detailed document inventory statistics.

    Returns breakdown by:
        - risk_level: critical, high, medium, low
        - document_class: postmortem, incident_report, security, etc.
        - critical status: is_critical=True docs
        - freshness: age metrics for documents
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status_code=401)

    from .services.rag_observability_service import get_rag_observability_service
    from dataclasses import asdict

    service = get_rag_observability_service()
    stats = service.get_document_inventory_stats()

    return api_success({
        'inventory': asdict(stats),
    })


@csrf_exempt
@require_http_methods(["GET"])
def rag_context_budget(request):
    """
    GET /api/rag/observability/budget/

    Get context budget utilization statistics.

    Returns:
        - total_budget: Max tokens (default 4000)
        - total_used: Allocated tokens
        - utilization_pct: Usage percentage
        - By priority tier: CRITICAL, RESERVED, HIGH, MEDIUM, LOW
        - Reserved tier breakdown: critical_docs, incident_docs, audit_findings
        - section_usage: Per-section allocation details
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status_code=401)

    from .services.rag_observability_service import get_rag_observability_service
    from dataclasses import asdict

    service = get_rag_observability_service()
    stats = service.get_context_budget_stats()

    return api_success({
        'budget': asdict(stats),
    })


@csrf_exempt
@require_http_methods(["GET"])
def rag_risk_boost_stats(request):
    """
    GET /api/rag/observability/boost/

    Get risk-aware re-ranking boost statistics.

    Returns:
        - total_results_boosted: Count of docs receiving boosts
        - avg_boost_applied: Average boost magnitude
        - max_boost_applied: Maximum boost (is_critical = +0.30)
        - boost_by_risk_level: Breakdown by risk level
        - boost_by_document_class: Breakdown by classification
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status_code=401)

    from .services.rag_observability_service import get_rag_observability_service
    from dataclasses import asdict

    service = get_rag_observability_service()
    stats = service.get_risk_boost_stats()

    return api_success({
        'boost_stats': asdict(stats),
    })


@csrf_exempt
@require_http_methods(["GET"])
def rag_critical_docs(request):
    """
    GET /api/rag/observability/critical-docs/

    Get detailed report of all critical documents.

    Returns list of critical docs with:
        - id, title, path
        - document_class, risk_level
        - updated_at, age_days
        - retrieval_boost multiplier
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status_code=401)

    from .services.rag_observability_service import get_rag_observability_service

    service = get_rag_observability_service()
    docs = service.get_critical_docs_report()

    return api_success({
        'critical_docs': docs,
        'count': len(docs),
    })


@csrf_exempt
@require_http_methods(["GET"])
def rag_risk_distribution(request):
    """
    GET /api/rag/observability/risk-distribution/

    Get risk distribution matrix and coverage analysis.

    Returns:
        - risk_matrix: risk_level x document_class counts
        - coverage_gaps: Identified gaps in coverage
        - recommendations: Actions to improve coverage
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status_code=401)

    from .services.rag_observability_service import get_rag_observability_service

    service = get_rag_observability_service()
    report = service.get_risk_distribution_report()

    return api_success({
        'distribution': report,
    })


@csrf_exempt
@require_http_methods(["GET"])
def rag_retrieval_channels(request):
    """
    GET /api/rag/observability/channels/

    Get retrieval channel usage statistics.

    Returns:
        - semantic_channel_count: Docs available for semantic search
        - critical_channel_count: Critical docs (always included)
        - incident_channel_count: Postmortems + incident reports
        - constraint_channel_count: Security + constraint docs
        - Distribution percentages
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status_code=401)

    from .services.rag_observability_service import get_rag_observability_service
    from dataclasses import asdict

    service = get_rag_observability_service()
    stats = service.get_retrieval_channel_stats()

    return api_success({
        'channels': asdict(stats),
    })


@csrf_exempt
@require_http_methods(["POST"])
def rag_run_classification(request):
    """
    POST /api/rag/observability/classify/

    Trigger document classification for RAG.

    This runs the classify_docs_for_rag logic on unclassified documents.

    Body (optional):
        - limit: Max documents to classify (default 100)
        - force: Re-classify already classified docs (default false)
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status_code=401)

    # Check for staff/admin permission
    if not request.user.is_staff:
        return api_error("Staff access required", status_code=403)

    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = {}

    limit = data.get('limit', 100)
    force = data.get('force', False)

    try:
        from content.models import Document
        from django.db.models import Q

        # Get unclassified docs
        query = Document.objects.filter(status='active')
        if not force:
            query = query.filter(
                Q(document_class__isnull=True) | Q(document_class='')
            )
        query = query[:limit]

        classified_count = 0
        results = {
            'by_class': {},
            'by_risk': {},
        }

        # Simple keyword-based classification
        for doc in query:
            doc_class, risk_level = _classify_document(doc)

            if doc_class:
                doc.document_class = doc_class
                results['by_class'][doc_class] = results['by_class'].get(doc_class, 0) + 1

            if risk_level:
                doc.risk_level = risk_level
                results['by_risk'][risk_level] = results['by_risk'].get(risk_level, 0) + 1

            if doc_class or risk_level:
                doc.save(update_fields=['document_class', 'risk_level', 'updated_at'])
                classified_count += 1

        return api_success({
            'classified_count': classified_count,
            'results': results,
        })

    except Exception as e:
        return api_error(f"Classification failed: {str(e)}", status_code=500)


def _classify_document(doc) -> tuple:
    """
    Classify a document based on content and path.

    Returns (document_class, risk_level) tuple.
    """
    title = (doc.title or '').lower()
    path = (doc.path or '').lower()
    content = (doc.raw_content or doc.content or '')[:2000].lower()

    doc_class = None
    risk_level = 'medium'

    # Postmortem detection
    if any(kw in title or kw in path for kw in ['postmortem', 'post-mortem', 'post_mortem', 'incident-review']):
        doc_class = 'postmortem'
        risk_level = 'high'

    # Incident report detection
    elif any(kw in title or kw in path for kw in ['incident', 'outage', 'failure', 'crash']):
        doc_class = 'incident_report'
        risk_level = 'high'

    # Security detection
    elif any(kw in title or kw in path for kw in ['security', 'vulnerability', 'cve', 'exploit', 'auth']):
        doc_class = 'security'
        risk_level = 'critical'

    # Constraint detection
    elif any(kw in title or kw in path for kw in ['constraint', 'rule', 'policy', 'requirement', 'must', 'never']):
        doc_class = 'constraint'
        risk_level = 'high'

    # Architecture detection
    elif any(kw in title or kw in path for kw in ['architecture', 'design', 'system', 'overview']):
        doc_class = 'architecture'
        risk_level = 'medium'

    # Runbook detection
    elif any(kw in title or kw in path for kw in ['runbook', 'playbook', 'procedure', 'how-to', 'howto']):
        doc_class = 'runbook'
        risk_level = 'medium'

    # Changelog detection
    elif any(kw in title or kw in path for kw in ['changelog', 'release', 'version', 'update']):
        doc_class = 'changelog'
        risk_level = 'low'

    # Default to reference
    else:
        doc_class = 'reference'
        risk_level = 'low'

    return doc_class, risk_level
