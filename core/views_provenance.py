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
