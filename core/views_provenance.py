"""
Provenance API Views - Content Ownership & Attribution
=======================================================

Session 295: API endpoints for provenance, audit, originality, and marketplace.

Endpoints:
    # Provenance
    POST /api/provenance/create/          - Create provenance for content
    GET  /api/provenance/<id>/            - Get provenance details
    GET  /api/provenance/<id>/certificate/ - Get certificate JSON
    GET  /api/provenance/<id>/certificate/download/ - Download PDF
    GET  /api/provenance/verify/          - Verify content by hash
    GET  /api/provenance/similar/         - Find similar images

    # Audit
    POST /api/audit/prompt/               - Audit a prompt before generation
    GET  /api/audit/<provenance_id>/      - Get audit for content
    GET  /api/audit/<id>/transparency/    - Get transparency card

    # Originality
    POST /api/originality/analyze/        - Analyze prompt originality
    GET  /api/originality/<provenance_id>/ - Get originality score
    POST /api/originality/alternatives/   - Get alternative prompts

    # Marketplace
    GET  /api/marketplace/fit/<provenance_id>/ - Market fit analysis
    GET  /api/marketplace/platforms/<provenance_id>/ - Platform suggestions
    GET  /api/marketplace/opportunities/  - Trending opportunities
    POST /api/marketplace/hashtags/       - Generate hashtags
"""

import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)


# =============================================================================
# Provenance Endpoints
# =============================================================================

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_provenance(request):
    """Create provenance record for content."""
    try:
        from core.services.provenance_service import ProvenanceService

        data = json.loads(request.body)
        image_history_id = data.get('image_history_id')
        generation_params = data.get('generation_params', {})

        if not image_history_id:
            return JsonResponse({
                'success': False,
                'error': 'image_history_id is required'
            }, status=400)

        # Get image history
        from content.models import ImageHistory
        image_history = ImageHistory.objects.get(id=image_history_id)

        # Get image bytes
        if image_history.image:
            image_bytes = image_history.image.read()
            image_history.image.seek(0)
        else:
            return JsonResponse({
                'success': False,
                'error': 'No image data available'
            }, status=400)

        service = ProvenanceService()
        result = service.create_provenance(
            image_history=image_history,
            user=request.user,
            image_bytes=image_bytes,
            generation_params=generation_params
        )

        return JsonResponse({
            'success': result.success,
            'provenance_id': str(result.provenance.id) if result.provenance else None,
            'content_hash': result.content_hash,
            'perceptual_hash': result.perceptual_hash,
            'error': result.error
        })

    except ImageHistory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Image not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error creating provenance: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_provenance(request, provenance_id):
    """Get provenance details."""
    try:
        from core.models_unified_system import ContentProvenance

        provenance = ContentProvenance.objects.get(id=provenance_id)

        # Check ownership
        if provenance.creator != request.user:
            return JsonResponse({
                'success': False,
                'error': 'Not authorized to view this provenance record'
            }, status=403)

        return JsonResponse({
            'success': True,
            'provenance': {
                'id': str(provenance.id),
                'content_type': provenance.content_type,
                'content_hash': provenance.content_hash,
                'perceptual_hash': provenance.perceptual_hash,
                'created_at': provenance.created_at.isoformat(),
                'generation_params': provenance.generation_params,
                'derivative_type': provenance.derivative_type,
                'is_verified': provenance.is_verified,
                'certificate_issued': provenance.certificate_issued,
            }
        })

    except ContentProvenance.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Provenance record not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting provenance: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_certificate(request, provenance_id):
    """Get certificate JSON."""
    try:
        from core.models_unified_system import ContentProvenance

        provenance = ContentProvenance.objects.get(id=provenance_id)

        if provenance.creator != request.user:
            return JsonResponse({
                'success': False,
                'error': 'Not authorized'
            }, status=403)

        certificate = provenance.generate_certificate()

        return JsonResponse({
            'success': True,
            'certificate': certificate
        })

    except ContentProvenance.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Provenance record not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting certificate: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def download_certificate(request, provenance_id):
    """Download PDF certificate."""
    try:
        from core.services.certificate_service import CertificateService
        from core.models_unified_system import ContentProvenance

        provenance = ContentProvenance.objects.get(id=provenance_id)

        if provenance.creator != request.user:
            return JsonResponse({
                'success': False,
                'error': 'Not authorized'
            }, status=403)

        service = CertificateService()
        result = service.generate_pdf_certificate(str(provenance_id))

        if result.success and result.pdf_bytes:
            response = HttpResponse(
                result.pdf_bytes,
                content_type='application/pdf'
            )
            response['Content-Disposition'] = (
                f'attachment; filename="certificate_{provenance_id}.pdf"'
            )
            return response
        else:
            return JsonResponse({
                'success': False,
                'error': result.error or 'Failed to generate certificate'
            }, status=500)

    except ContentProvenance.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Provenance record not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error downloading certificate: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def verify_provenance(request):
    """Verify content by hash (public endpoint for QR codes)."""
    try:
        from core.models_unified_system import ContentProvenance

        content_hash = request.GET.get('hash')
        provenance_id = request.GET.get('id')

        if provenance_id:
            try:
                provenance = ContentProvenance.objects.get(id=provenance_id)
                return JsonResponse({
                    'valid': True,
                    'provenance_id': str(provenance.id),
                    'content_type': provenance.content_type,
                    'creator': provenance.creator.username,
                    'created_at': provenance.created_at.isoformat(),
                    'is_verified': provenance.is_verified,
                })
            except ContentProvenance.DoesNotExist:
                return JsonResponse({
                    'valid': False,
                    'error': 'Provenance not found'
                })

        if content_hash:
            try:
                provenance = ContentProvenance.objects.get(content_hash=content_hash)
                return JsonResponse({
                    'valid': True,
                    'provenance_id': str(provenance.id),
                    'content_type': provenance.content_type,
                    'creator': provenance.creator.username,
                    'created_at': provenance.created_at.isoformat(),
                })
            except ContentProvenance.DoesNotExist:
                return JsonResponse({
                    'valid': False,
                    'error': 'No matching provenance record'
                })

        return JsonResponse({
            'valid': False,
            'error': 'Provide hash or id parameter'
        }, status=400)

    except Exception as e:
        logger.error(f"Error verifying provenance: {e}")
        return JsonResponse({
            'valid': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def find_similar(request):
    """Find similar images by perceptual hash."""
    try:
        from core.services.provenance_service import ProvenanceService

        perceptual_hash = request.GET.get('phash')
        threshold = int(request.GET.get('threshold', 10))

        if not perceptual_hash:
            return JsonResponse({
                'success': False,
                'error': 'phash parameter required'
            }, status=400)

        service = ProvenanceService()
        similar = service.find_similar_images(perceptual_hash, threshold)

        return JsonResponse({
            'success': True,
            'similar': [
                {
                    'provenance_id': str(p[0]),
                    'distance': p[1]
                }
                for p in similar[:10]
            ]
        })

    except Exception as e:
        logger.error(f"Error finding similar: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Audit Endpoints
# =============================================================================

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def audit_prompt(request):
    """Audit a prompt before generation."""
    try:
        from core.services.provenance_service import ContentAuditService

        data = json.loads(request.body)
        prompt = data.get('prompt', '')
        model = data.get('model')

        if not prompt:
            return JsonResponse({
                'success': False,
                'error': 'prompt is required'
            }, status=400)

        service = ContentAuditService()
        result = service.audit_prompt(prompt)

        return JsonResponse({
            'success': result.success,
            'safety_score': result.safety_score,
            'bias_detected': result.bias_detected,
            'bias_categories': result.bias_categories,
            'ethics_flags': result.ethics_flags,
            'prompt_suggestions': result.prompt_suggestions,
            'recommendations': result.recommendations,
            'error': result.error
        })

    except Exception as e:
        logger.error(f"Error auditing prompt: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_audit(request, provenance_id):
    """Get audit for content."""
    try:
        from core.models_unified_system import ContentAuditResult

        audits = ContentAuditResult.objects.filter(
            provenance_id=provenance_id
        ).order_by('-audited_at')

        if not audits.exists():
            return JsonResponse({
                'success': False,
                'error': 'No audit found'
            }, status=404)

        audit = audits.first()

        return JsonResponse({
            'success': True,
            'audit': {
                'id': str(audit.id),
                'overall_safety_score': audit.overall_safety_score,
                'bias_detected': audit.bias_detected,
                'bias_categories': audit.bias_categories,
                'ethics_flags': audit.ethics_flags,
                'prompt_suggestions': audit.prompt_suggestions,
                'recommendations': audit.recommendations,
                'audited_at': audit.audited_at.isoformat(),
            }
        })

    except Exception as e:
        logger.error(f"Error getting audit: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_transparency_card(request, audit_id):
    """Get transparency card for an audit."""
    try:
        from core.models_unified_system import ContentAuditResult

        audit = ContentAuditResult.objects.get(id=audit_id)
        card = audit.generate_transparency_card()

        return JsonResponse({
            'success': True,
            'transparency_card': card
        })

    except ContentAuditResult.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Audit not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting transparency card: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Originality Endpoints
# =============================================================================

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def analyze_originality(request):
    """Analyze prompt originality."""
    try:
        from core.services.provenance_service import OriginalityService

        data = json.loads(request.body)
        prompt = data.get('prompt', '')

        if not prompt:
            return JsonResponse({
                'success': False,
                'error': 'prompt is required'
            }, status=400)

        service = OriginalityService()
        result = service.analyze_prompt_originality(prompt)

        return JsonResponse({
            'success': result.success,
            'overall_score': result.overall_score,
            'verdict': result.verdict,
            'generic_patterns': result.generic_patterns,
            'differentiation_suggestions': result.differentiation_suggestions,
            'alternative_prompts': result.alternative_prompts,
            'error': result.error
        })

    except Exception as e:
        logger.error(f"Error analyzing originality: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_originality_score(request, provenance_id):
    """Get originality score for content."""
    try:
        from core.models_unified_system import OriginalityScore

        scores = OriginalityScore.objects.filter(
            provenance_id=provenance_id
        ).order_by('-scored_at')

        if not scores.exists():
            return JsonResponse({
                'success': False,
                'error': 'No originality score found'
            }, status=404)

        score = scores.first()

        return JsonResponse({
            'success': True,
            'originality': {
                'overall_originality': score.overall_originality,
                'prompt_originality': score.prompt_originality,
                'style_originality': score.style_originality,
                'composition_originality': score.composition_originality,
                'trend_similarity': score.trend_similarity,
                'uniqueness_percentile': score.uniqueness_percentile,
                'generic_patterns_detected': score.generic_patterns_detected,
                'differentiation_suggestions': score.differentiation_suggestions,
                'scored_at': score.scored_at.isoformat(),
            }
        })

    except Exception as e:
        logger.error(f"Error getting originality score: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def get_alternative_prompts(request):
    """Get alternative prompts for more originality."""
    try:
        from core.services.provenance_service import OriginalityService

        data = json.loads(request.body)
        prompt = data.get('prompt', '')
        count = data.get('count', 3)

        if not prompt:
            return JsonResponse({
                'success': False,
                'error': 'prompt is required'
            }, status=400)

        service = OriginalityService()
        alternatives = service.get_alternative_prompts(prompt, count)

        return JsonResponse({
            'success': True,
            'original_prompt': prompt,
            'alternatives': alternatives
        })

    except Exception as e:
        logger.error(f"Error getting alternatives: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Marketplace Endpoints
# =============================================================================

@login_required
@require_http_methods(["GET"])
def get_market_fit(request, provenance_id):
    """Analyze market fit for content."""
    try:
        from core.services.marketplace_discovery_service import MarketplaceDiscoveryService

        service = MarketplaceDiscoveryService()
        result = service.analyze_content_market_fit(provenance_id)

        return JsonResponse(result.to_dict())

    except Exception as e:
        logger.error(f"Error analyzing market fit: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_platform_suggestions(request, provenance_id):
    """Get platform suggestions for content."""
    try:
        from core.services.marketplace_discovery_service import MarketplaceDiscoveryService

        service = MarketplaceDiscoveryService()
        suggestions = service.suggest_platforms(provenance_id)

        return JsonResponse({
            'success': True,
            'platforms': [s.to_dict() for s in suggestions]
        })

    except Exception as e:
        logger.error(f"Error getting platform suggestions: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_trending_opportunities(request):
    """Get trending opportunities matching creator's style."""
    try:
        from core.services.marketplace_discovery_service import MarketplaceDiscoveryService

        style = request.GET.get('style')
        category = request.GET.get('category')
        limit = int(request.GET.get('limit', 10))

        service = MarketplaceDiscoveryService()
        opportunities = service.find_trending_opportunities(
            style=style,
            category=category,
            limit=limit
        )

        return JsonResponse({
            'success': True,
            'opportunities': opportunities
        })

    except Exception as e:
        logger.error(f"Error getting opportunities: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def generate_hashtags(request):
    """Generate hashtags for content."""
    try:
        from core.services.marketplace_discovery_service import MarketplaceDiscoveryService

        data = json.loads(request.body)
        provenance_id = data.get('provenance_id')
        platform = data.get('platform', 'instagram')

        if not provenance_id:
            return JsonResponse({
                'success': False,
                'error': 'provenance_id is required'
            }, status=400)

        service = MarketplaceDiscoveryService()
        hashtags = service.generate_hashtags(provenance_id, platform)

        return JsonResponse({
            'success': True,
            'platform': platform,
            'hashtags': hashtags,
            'formatted': ' '.join(f'#{h}' for h in hashtags)
        })

    except Exception as e:
        logger.error(f"Error generating hashtags: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Watermark Endpoints
# =============================================================================

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def verify_watermark(request):
    """Verify watermark ownership claim."""
    try:
        from core.services.watermark_service import WatermarkService

        # Get image from request
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Image file required'
            }, status=400)

        image_file = request.FILES['image']
        image_bytes = image_file.read()

        claimed_creator_id = request.POST.get('creator_id', str(request.user.id))

        service = WatermarkService()
        is_owner, watermark_data = service.verify_ownership(
            image_bytes,
            claimed_creator_id
        )

        return JsonResponse({
            'success': True,
            'is_owner': is_owner,
            'watermark_data': watermark_data
        })

    except Exception as e:
        logger.error(f"Error verifying watermark: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def extract_watermark(request):
    """Extract watermark from image."""
    try:
        from core.services.watermark_service import WatermarkService

        # Get image from request
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Image file required'
            }, status=400)

        image_file = request.FILES['image']
        image_bytes = image_file.read()

        service = WatermarkService()
        result = service.extract_watermark(image_bytes)

        return JsonResponse({
            'success': result.success,
            'watermark_data': result.watermark_data,
            'error': result.error
        })

    except Exception as e:
        logger.error(f"Error extracting watermark: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# MARKET INTELLIGENCE DATA LINEAGE ENDPOINTS (Phase 5 - Session 472)
# =============================================================================
# These endpoints track data provenance through the Market Intelligence pipeline:
# Spider Data → Opportunity → Scoring → Validation → Decision → Outcome

from django.utils import timezone
from datetime import timedelta


@csrf_exempt
@require_http_methods(["GET"])
def get_mi_lineage(request, entity_type, entity_id):
    """
    Get the complete lineage chain for a Market Intelligence entity.

    GET /api/mi/lineage/<entity_type>/<entity_id>/

    Entity types: spider_data, opportunity, scoring_result, validation_request,
                  validation_decision, opportunity_outcome

    Query params:
        include_metadata: bool (default True) - Include metadata in response
        include_compliance: bool (default True) - Include compliance status

    Returns:
        {
            "success": true,
            "lineage": [...],
            "total_depth": 4,
            "integrity_verified": true
        }
    """
    try:
        from .services.provenance_tracker import get_provenance_tracker

        tracker = get_provenance_tracker()
        include_metadata = request.GET.get('include_metadata', 'true').lower() == 'true'
        include_compliance = request.GET.get('include_compliance', 'true').lower() == 'true'

        result = tracker.get_lineage(entity_type, entity_id)

        if not result.success:
            return JsonResponse({
                'success': False,
                'error': result.error
            }, status=404)

        # Build response
        lineage_data = []
        for item in result.lineage:
            item_data = {
                'id': str(item.id),
                'entity_type': item.entity_type,
                'entity_id': item.entity_id,
                'depth': item.depth,
                'source_type': item.source_type,
                'source_name': item.source_name,
                'created_at': item.created_at.isoformat(),
                'compliance_status': item.compliance_status,
            }

            if include_metadata:
                item_data['metadata'] = item.metadata

            if include_compliance:
                item_data['compliance_checks'] = list(
                    item.compliance_checks.values(
                        'check_type', 'passed', 'severity', 'details'
                    )
                )

            lineage_data.append(item_data)

        return JsonResponse({
            'success': True,
            'lineage': lineage_data,
            'total_depth': len(lineage_data),
            'integrity_verified': result.integrity_verified
        })

    except Exception as e:
        logger.error(f"Error getting MI lineage: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_mi_descendants(request, provenance_id):
    """
    Get all descendants of a provenance record.

    GET /api/mi/provenance/<provenance_id>/descendants/

    Query params:
        max_depth: int (default None) - Maximum depth to traverse

    Returns:
        {
            "success": true,
            "root_id": "...",
            "descendants": [...],
            "total_count": 15
        }
    """
    try:
        from .models_unified_system import DataProvenance
        from .services.provenance_tracker import get_provenance_tracker

        tracker = get_provenance_tracker()
        max_depth = request.GET.get('max_depth')
        if max_depth:
            max_depth = int(max_depth)

        descendants = tracker.get_descendants(provenance_id, max_depth)

        return JsonResponse({
            'success': True,
            'root_id': provenance_id,
            'descendants': descendants,
            'total_count': len(descendants)
        })

    except DataProvenance.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Provenance record {provenance_id} not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting MI descendants: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def verify_mi_integrity(request, provenance_id):
    """
    Verify the cryptographic integrity of a provenance chain.

    GET /api/mi/provenance/<provenance_id>/verify/

    Returns:
        {
            "success": true,
            "verified": true,
            "chain_length": 4,
            "verification_details": [...],
            "errors": []
        }
    """
    try:
        from .models_unified_system import DataProvenance
        from .services.provenance_tracker import get_provenance_tracker

        tracker = get_provenance_tracker()
        result = tracker.verify_integrity(provenance_id)

        return JsonResponse({
            'success': True,
            **result
        })

    except DataProvenance.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Provenance record {provenance_id} not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error verifying MI integrity: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_mi_provenance_detail(request, provenance_id):
    """
    Get detailed information about a single provenance record.

    GET /api/mi/provenance/<provenance_id>/

    Returns detailed provenance information including hash chain and compliance.
    """
    try:
        from .models_unified_system import DataProvenance

        provenance = DataProvenance.objects.get(id=provenance_id)

        return JsonResponse({
            'success': True,
            'provenance': {
                'id': str(provenance.id),
                'entity_type': provenance.entity_type,
                'entity_id': provenance.entity_id,
                'parent_id': str(provenance.parent_id) if provenance.parent_id else None,
                'root_id': str(provenance.root_id) if provenance.root_id else None,
                'depth': provenance.depth,
                'source_type': provenance.source_type,
                'source_name': provenance.source_name,
                'content_hash': provenance.content_hash,
                'previous_hash': provenance.previous_hash,
                'compliance_status': provenance.compliance_status,
                'metadata': provenance.metadata,
                'created_at': provenance.created_at.isoformat(),
                'compliance_checks': list(
                    provenance.compliance_checks.values(
                        'id', 'check_type', 'passed', 'severity',
                        'details', 'remediation_required', 'remediated_at'
                    )
                )
            }
        })

    except DataProvenance.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Provenance record {provenance_id} not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting MI provenance detail: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# AUDIT TRAIL ENDPOINTS (Phase 5 - Session 472)
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_mi_audit_trail(request):
    """
    Get audit trail with filtering options.

    GET /api/mi/audit/trail/

    Query params:
        entity_type: str - Filter by entity type
        entity_id: str - Filter by entity ID
        action_type: str - Filter by action type
        actor_type: str - Filter by actor type (user, agent, system)
        actor_id: str - Filter by actor ID
        start_date: str (ISO format) - Start of date range
        end_date: str (ISO format) - End of date range
        limit: int (default 100) - Maximum results
        offset: int (default 0) - Pagination offset

    Returns:
        {
            "success": true,
            "audit_trail": [...],
            "total_count": 500,
            "limit": 100,
            "offset": 0
        }
    """
    try:
        from .services.provenance_tracker import get_provenance_tracker

        tracker = get_provenance_tracker()

        # Parse query params
        filters = {}
        for key in ['entity_type', 'entity_id', 'action_type', 'actor_type',
                    'actor_id', 'start_date', 'end_date']:
            value = request.GET.get(key)
            if value:
                filters[key] = value

        limit = int(request.GET.get('limit', 100))
        offset = int(request.GET.get('offset', 0))

        audit_entries = tracker.get_audit_trail(**filters)

        # Count total before pagination
        total_count = len(audit_entries)

        # Apply pagination
        paginated = audit_entries[offset:offset + limit]

        return JsonResponse({
            'success': True,
            'audit_trail': paginated,
            'total_count': total_count,
            'limit': limit,
            'offset': offset
        })

    except Exception as e:
        logger.error(f"Error getting MI audit trail: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# COMPLIANCE ENDPOINTS (Phase 5 - Session 472)
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_mi_compliance_summary(request):
    """
    Get compliance statistics and summary.

    GET /api/mi/compliance/summary/

    Query params:
        entity_type: str - Filter by entity type
        start_date: str - Start of date range
        end_date: str - End of date range

    Returns compliance summary with pass rates and failure breakdown.
    """
    try:
        from .services.provenance_tracker import get_provenance_tracker

        tracker = get_provenance_tracker()

        entity_type = request.GET.get('entity_type')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        summary = tracker.get_compliance_summary(
            entity_type=entity_type,
            start_date=start_date,
            end_date=end_date
        )

        return JsonResponse({
            'success': True,
            'summary': summary
        })

    except Exception as e:
        logger.error(f"Error getting MI compliance summary: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_mi_compliance_rules(request):
    """
    Get all active compliance rules.

    GET /api/mi/compliance/rules/

    Returns list of active compliance rules and their configurations.
    """
    try:
        from .models_unified_system import ComplianceRule

        rules = ComplianceRule.objects.filter(is_active=True).values(
            'id', 'name', 'check_type', 'entity_types',
            'severity', 'blocking', 'config', 'description'
        )

        return JsonResponse({
            'success': True,
            'rules': list(rules)
        })

    except Exception as e:
        logger.error(f"Error getting MI compliance rules: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_mi_compliance_issues(request):
    """
    Get outstanding compliance issues requiring remediation.

    GET /api/mi/compliance/issues/

    Query params:
        severity: str - Filter by severity (critical, high, medium, low)
        entity_type: str - Filter by entity type
        unremediated_only: bool (default True) - Only show unremediated issues
        limit: int (default 100)

    Returns list of compliance issues with details.
    """
    try:
        from .models_unified_system import ComplianceCheck

        severity = request.GET.get('severity')
        entity_type = request.GET.get('entity_type')
        unremediated_only = request.GET.get('unremediated_only', 'true').lower() == 'true'
        limit = int(request.GET.get('limit', 100))

        # Build query
        queryset = ComplianceCheck.objects.filter(
            passed=False,
            remediation_required=True
        )

        if unremediated_only:
            queryset = queryset.filter(remediated_at__isnull=True)

        if severity:
            queryset = queryset.filter(severity=severity)

        if entity_type:
            queryset = queryset.filter(provenance__entity_type=entity_type)

        queryset = queryset.order_by('severity', '-created_at')

        total_count = queryset.count()
        critical_count = queryset.filter(severity='critical').count()

        issues = []
        for check in queryset[:limit]:
            issues.append({
                'id': check.id,
                'check_type': check.check_type,
                'severity': check.severity,
                'details': check.details,
                'created_at': check.created_at.isoformat(),
                'entity_type': check.provenance.entity_type,
                'entity_id': check.provenance.entity_id,
                'provenance_id': str(check.provenance_id),
                'remediated_at': check.remediated_at.isoformat() if check.remediated_at else None
            })

        return JsonResponse({
            'success': True,
            'issues': issues,
            'total_count': total_count,
            'critical_count': critical_count
        })

    except Exception as e:
        logger.error(f"Error getting MI compliance issues: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def remediate_mi_compliance_issue(request, check_id):
    """
    Mark a compliance issue as remediated.

    POST /api/mi/compliance/<check_id>/remediate/

    Body:
        {
            "remediation_notes": "Fixed data freshness by re-crawling source"
        }

    Returns confirmation of remediation.
    """
    try:
        from .models_unified_system import ComplianceCheck
        from .services.provenance_tracker import get_provenance_tracker

        check = ComplianceCheck.objects.get(id=check_id)

        if check.remediated_at:
            return JsonResponse({
                'success': False,
                'error': 'Issue already remediated'
            }, status=400)

        # Parse body
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            body = {}

        remediation_notes = body.get('remediation_notes', '')

        # Update check
        check.remediated_at = timezone.now()
        check.remediated_by = request.user
        check.details['remediation_notes'] = remediation_notes
        check.save()

        # Log the remediation
        tracker = get_provenance_tracker()
        tracker._create_audit_log(
            action_type='compliance_remediated',
            actor_type='user',
            actor_id=str(request.user.id),
            entity_type=check.provenance.entity_type,
            entity_id=check.provenance.entity_id,
            before_state={'remediated_at': None},
            after_state={
                'remediated_at': check.remediated_at.isoformat(),
                'remediation_notes': remediation_notes
            },
            metadata={
                'check_id': check.id,
                'check_type': check.check_type
            }
        )

        return JsonResponse({
            'success': True,
            'check_id': check.id,
            'remediated_at': check.remediated_at.isoformat()
        })

    except ComplianceCheck.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Compliance check {check_id} not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error remediating MI compliance issue: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# STATISTICS ENDPOINTS (Phase 5 - Session 472)
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_mi_provenance_stats(request):
    """
    Get overall provenance and audit statistics.

    GET /api/mi/provenance/stats/

    Returns comprehensive statistics about the provenance system.
    """
    try:
        from django.db.models import Count, Avg
        from .models_unified_system import DataProvenance, AuditLog, ComplianceCheck

        # Basic counts
        total_provenance = DataProvenance.objects.count()
        total_audit_logs = AuditLog.objects.count()

        # By entity type
        by_entity_type = dict(
            DataProvenance.objects.values('entity_type')
            .annotate(count=Count('id'))
            .values_list('entity_type', 'count')
        )

        # By source type
        by_source_type = dict(
            DataProvenance.objects.values('source_type')
            .annotate(count=Count('id'))
            .values_list('source_type', 'count')
        )

        # Average chain depth
        avg_depth = DataProvenance.objects.aggregate(avg=Avg('depth'))['avg'] or 0

        # Compliance stats
        total_checks = ComplianceCheck.objects.count()
        passed_checks = ComplianceCheck.objects.filter(passed=True).count()
        pass_rate = passed_checks / total_checks if total_checks > 0 else 1.0
        open_issues = ComplianceCheck.objects.filter(
            passed=False,
            remediation_required=True,
            remediated_at__isnull=True
        ).count()

        # Recent activity
        now = timezone.now()
        last_24h = DataProvenance.objects.filter(
            created_at__gte=now - timedelta(hours=24)
        ).count()
        last_7d = DataProvenance.objects.filter(
            created_at__gte=now - timedelta(days=7)
        ).count()

        audit_24h = AuditLog.objects.filter(
            created_at__gte=now - timedelta(hours=24)
        ).count()
        audit_7d = AuditLog.objects.filter(
            created_at__gte=now - timedelta(days=7)
        ).count()

        return JsonResponse({
            'success': True,
            'stats': {
                'total_provenance_records': total_provenance,
                'by_entity_type': by_entity_type,
                'by_source_type': by_source_type,
                'avg_chain_depth': round(avg_depth, 2),
                'total_audit_logs': total_audit_logs,
                'compliance': {
                    'total_checks': total_checks,
                    'pass_rate': round(pass_rate, 3),
                    'open_issues': open_issues
                },
                'recent_activity': {
                    'provenance_24h': last_24h,
                    'provenance_7d': last_7d,
                    'audit_24h': audit_24h,
                    'audit_7d': audit_7d
                }
            }
        })

    except Exception as e:
        logger.error(f"Error getting MI provenance stats: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
