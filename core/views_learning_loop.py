"""
Session 232: Learning Loop API Views
Phase 5 - Creative Intelligence Empire

Provides endpoints for:
- Success pattern analysis
- Content performance prediction
- Pricing optimization
- User learning profile
- Performance comparisons
- Distribution insights
"""

import json
import uuid
from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, Sum, Count, Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models_unified_system import (
    SuccessPattern,
    ContentPerformancePrediction,
    PricingOptimization,
    DistributionInsight,
    UserLearningProfile,
    PerformanceComparison,
    ContentDistribution,
    DistributionPlatform,
)
from .api_helpers import api_success, api_error


# ============================================================
# Success Pattern API
# ============================================================

@csrf_exempt
@require_http_methods(["GET"])
def list_success_patterns(request):
    """
    GET /api/learning/patterns/
    List discovered success patterns for the user.
    """
    if not request.user.is_authenticated:
        return api_success({"patterns": [], "count": 0})

    try:
        pattern_type = request.GET.get('type')  # Filter by pattern type
        min_confidence = float(request.GET.get('min_confidence', 50))
        include_global = request.GET.get('include_global', 'true').lower() == 'true'

        # Build query
        query = Q(user=request.user)
        if include_global:
            query |= Q(is_global=True)

        patterns = SuccessPattern.objects.filter(query, is_active=True)

        if pattern_type:
            patterns = patterns.filter(pattern_type=pattern_type)

        patterns = patterns.filter(confidence_score__gte=min_confidence)
        patterns = patterns.order_by('-success_rate', '-confidence_score')[:50]

        return api_success({
            'patterns': [{
                'id': str(p.id),
                'type': p.pattern_type,
                'name': p.pattern_name,
                'description': p.pattern_description,
                'attributes': p.pattern_attributes,
                'success_rate': float(p.success_rate),
                'avg_revenue': float(p.avg_revenue_per_success),
                'total_revenue': float(p.total_revenue_attributed),
                'confidence': float(p.confidence_score),
                'sample_size': p.sample_size,
                'statistically_significant': p.statistical_significance,
                'best_platforms': p.best_platforms,
                'best_upload_times': p.best_upload_times,
                'is_global': p.is_global,
            } for p in patterns],
            'count': len(patterns),
            'pattern_types': dict(SuccessPattern._meta.get_field('pattern_type').choices),
        })
    except Exception:
        return api_success({'patterns': [], 'count': 0, 'pattern_types': {}})


@csrf_exempt
@require_http_methods(["GET"])
def pattern_detail(request, pattern_id):
    """
    GET /api/learning/patterns/<id>/
    Get detailed information about a success pattern.
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status=401)

    try:
        pattern = SuccessPattern.objects.get(
            Q(id=pattern_id),
            Q(user=request.user) | Q(is_global=True)
        )
    except SuccessPattern.DoesNotExist:
        return api_error("Pattern not found", status=404)

    return api_success({
        'pattern': {
            'id': str(pattern.id),
            'type': pattern.pattern_type,
            'name': pattern.pattern_name,
            'description': pattern.pattern_description,
            'attributes': pattern.pattern_attributes,
            'success_count': pattern.success_count,
            'failure_count': pattern.failure_count,
            'success_rate': float(pattern.success_rate),
            'avg_revenue': float(pattern.avg_revenue_per_success),
            'total_revenue': float(pattern.total_revenue_attributed),
            'confidence': float(pattern.confidence_score),
            'sample_size': pattern.sample_size,
            'statistically_significant': pattern.statistical_significance,
            'best_platforms': pattern.best_platforms,
            'best_upload_times': pattern.best_upload_times,
            'best_seasons': pattern.best_seasons,
            'example_content_ids': pattern.example_content_ids,
            'is_global': pattern.is_global,
            'created_at': pattern.created_at.isoformat(),
            'last_validated': pattern.last_validated.isoformat() if pattern.last_validated else None,
        }
    })


@csrf_exempt
@require_http_methods(["POST"])
def analyze_patterns(request):
    """
    POST /api/learning/patterns/analyze/
    Trigger pattern analysis for the user's distribution history.
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status=401)

    # Get user's successful distributions
    distributions = ContentDistribution.objects.filter(
        user=request.user,
        status='completed'
    ).select_related('platform')

    if distributions.count() < 5:
        return api_success({
            'message': 'Need at least 5 successful distributions to analyze patterns',
            'current_count': distributions.count(),
            'patterns_discovered': 0,
        })

    patterns_discovered = []

    # Analyze content style patterns
    style_counts = {}
    for dist in distributions:
        style = dist.metadata.get('style', 'unknown')
        if style not in style_counts:
            style_counts[style] = {'success': 0, 'revenue': Decimal('0')}
        style_counts[style]['success'] += 1
        style_counts[style]['revenue'] += dist.revenue_generated or Decimal('0')

    for style, data in style_counts.items():
        if data['success'] >= 3:  # Minimum threshold
            pattern, created = SuccessPattern.objects.get_or_create(
                user=request.user,
                pattern_type='content_style',
                pattern_name=f"Style: {style.title()}",
                defaults={
                    'pattern_description': f"Content with {style} style performs well",
                    'pattern_attributes': {'style': style},
                }
            )
            pattern.success_count = data['success']
            pattern.total_revenue_attributed = data['revenue']
            pattern.sample_size = data['success']
            if data['success'] > 0:
                pattern.avg_revenue_per_success = data['revenue'] / data['success']
                pattern.success_rate = min(100, data['success'] * 10)  # Simplified
            pattern.save()
            patterns_discovered.append(pattern.pattern_name)

    # Analyze platform patterns
    platform_counts = {}
    for dist in distributions:
        platform_name = dist.platform.name if dist.platform else 'unknown'
        if platform_name not in platform_counts:
            platform_counts[platform_name] = {'success': 0, 'revenue': Decimal('0')}
        platform_counts[platform_name]['success'] += 1
        platform_counts[platform_name]['revenue'] += dist.revenue_generated or Decimal('0')

    for platform, data in platform_counts.items():
        if data['success'] >= 3:
            pattern, created = SuccessPattern.objects.get_or_create(
                user=request.user,
                pattern_type='platform_match',
                pattern_name=f"Platform: {platform.title()}",
                defaults={
                    'pattern_description': f"Content performs well on {platform}",
                    'pattern_attributes': {'platform': platform},
                }
            )
            pattern.success_count = data['success']
            pattern.total_revenue_attributed = data['revenue']
            pattern.sample_size = data['success']
            if data['success'] > 0:
                pattern.avg_revenue_per_success = data['revenue'] / data['success']
                pattern.success_rate = min(100, data['success'] * 10)
            pattern.save()
            patterns_discovered.append(pattern.pattern_name)

    # Analyze pricing patterns
    price_ranges = {'low': (0, 15), 'medium': (15, 35), 'high': (35, 100), 'premium': (100, 1000)}
    price_counts = {k: {'success': 0, 'revenue': Decimal('0')} for k in price_ranges}

    for dist in distributions:
        price = float(dist.price_listed or 0)
        for range_name, (low, high) in price_ranges.items():
            if low <= price < high:
                price_counts[range_name]['success'] += 1
                price_counts[range_name]['revenue'] += dist.revenue_generated or Decimal('0')
                break

    for range_name, data in price_counts.items():
        if data['success'] >= 3:
            pattern, created = SuccessPattern.objects.get_or_create(
                user=request.user,
                pattern_type='pricing_strategy',
                pattern_name=f"Pricing: {range_name.title()} Range",
                defaults={
                    'pattern_description': f"Content priced in {range_name} range sells well",
                    'pattern_attributes': {'price_range': range_name, 'bounds': price_ranges[range_name]},
                }
            )
            pattern.success_count = data['success']
            pattern.total_revenue_attributed = data['revenue']
            pattern.sample_size = data['success']
            if data['success'] > 0:
                pattern.avg_revenue_per_success = data['revenue'] / data['success']
                pattern.success_rate = min(100, data['success'] * 10)
            pattern.save()
            patterns_discovered.append(pattern.pattern_name)

    return api_success({
        'patterns_discovered': len(set(patterns_discovered)),
        'pattern_names': list(set(patterns_discovered)),
        'distributions_analyzed': distributions.count(),
    })


# ============================================================
# Content Performance Prediction API
# ============================================================

@csrf_exempt
@require_http_methods(["POST"])
def predict_performance(request):
    """
    POST /api/learning/predict/
    Predict performance for content before distribution.
    Uses ContentScoringEngine from learning_engine.py
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return api_error("Invalid JSON")

    content_type = data.get('content_type', 'image')
    content_id = data.get('content_id')
    attributes = data.get('attributes', {})
    target_platforms = data.get('platforms', [])
    tags = data.get('tags', attributes.get('tags', []))
    price = data.get('price', attributes.get('price', 19.99))
    title = data.get('title', '')
    description = data.get('description', '')

    # Use the ML-based ContentScoringEngine
    from .learning_engine import ContentScoringEngine

    engine = ContentScoringEngine(user=request.user)
    scores = engine.score_content(
        content_type=content_type,
        platforms=target_platforms or ['etsy', 'gumroad', 'shutterstock'],
        tags=tags if isinstance(tags, list) else [t.strip() for t in str(tags).split(',')],
        price=float(price),
        title=title,
        description=description,
    )

    # Use scores from the ML engine
    overall_probability = scores['overall'] / 100  # Convert to decimal
    platform_predictions = {}

    for platform_name, platform_scores in scores['platform_fit'].items():
        platform_predictions[platform_name] = {
            'success_probability': round(platform_scores['score'] / 100, 4),
            'expected_revenue': round(platform_scores.get('avg_revenue', 25) * (platform_scores['score'] / 100), 2),
            'confidence': round(platform_scores['confidence'] / 100, 4),
        }

    # Get pricing optimization for recommended price
    from .learning_engine import PricingEngine
    pricing_engine = PricingEngine(user=request.user)

    # Get optimal price for primary platform
    primary_platform = (target_platforms or ['etsy'])[0]
    pricing_result = pricing_engine.get_optimal_price(
        content_type=content_type,
        platform=primary_platform,
        current_price=float(price) if price else None
    )

    recommended_price = {
        'min': pricing_result['min_price'],
        'max': pricing_result['max_price'],
        'optimal': pricing_result['optimal_price'],
    }

    # Build matching patterns list from recommendations
    matching_patterns = []
    for rec in scores.get('recommendations', []):
        matching_patterns.append({
            'pattern_type': rec['type'],
            'message': rec['message'],
            'priority': rec['priority'],
        })

    # Sort platforms by score for recommendations
    sorted_platforms = sorted(
        scores['platform_fit'].items(),
        key=lambda x: x[1]['score'],
        reverse=True
    )
    recommended_platforms = [p[0] for p in sorted_platforms]

    # Calculate expected total revenue
    expected_total_revenue = sum(p['expected_revenue'] for p in platform_predictions.values())

    # Average confidence across platforms
    avg_confidence = sum(p['confidence'] for p in platform_predictions.values()) / max(len(platform_predictions), 1)

    # Create prediction record
    prediction = ContentPerformancePrediction.objects.create(
        user=request.user,
        content_type=content_type,
        content_id=uuid.UUID(content_id) if content_id else None,
        analyzed_attributes={**attributes, 'tags': tags, 'price': price, 'title': title},
        platform_predictions=platform_predictions,
        overall_success_probability=Decimal(str(overall_probability)),
        expected_total_revenue=Decimal(str(expected_total_revenue)),
        prediction_confidence=Decimal(str(avg_confidence)),
        recommended_platforms=recommended_platforms,
        recommended_price_range=recommended_price,
        recommended_tags=tags if isinstance(tags, list) else [t.strip() for t in str(tags).split(',')],
        matching_success_patterns=[],
    )

    return api_success({
        'prediction_id': str(prediction.id),
        'overall_score': round(scores['overall'], 1),
        'overall_success_probability': round(overall_probability, 4),
        'expected_total_revenue': round(expected_total_revenue, 2),
        'prediction_confidence': round(avg_confidence, 4),
        'score_breakdown': {
            'content_type': round(scores['content_type_score'], 1),
            'price': round(scores['price_score'], 1),
            'tags': round(scores['tag_score'], 1),
            'timing': round(scores['timing_score'], 1),
        },
        'platform_predictions': platform_predictions,
        'recommended_price_range': recommended_price,
        'pricing_rationale': pricing_result.get('rationale', ''),
        'recommendations': scores.get('recommendations', []),
        'recommended_platforms': recommended_platforms,
    })


@csrf_exempt
@require_http_methods(["GET"])
def list_predictions(request):
    """
    GET /api/learning/predictions/
    List recent performance predictions.
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status=401)

    limit = int(request.GET.get('limit', 20))
    predictions = ContentPerformancePrediction.objects.filter(
        user=request.user
    ).order_by('-prediction_timestamp')[:limit]

    return api_success({
        'predictions': [{
            'id': str(p.id),
            'content_type': p.content_type,
            'content_id': str(p.content_id) if p.content_id else None,
            'success_probability': float(p.overall_success_probability),
            'expected_revenue': float(p.expected_total_revenue),
            'confidence': float(p.prediction_confidence),
            'recommended_platforms': p.recommended_platforms,
            'actual_success': p.actual_success,
            'actual_revenue': float(p.actual_revenue) if p.actual_revenue else None,
            'prediction_accuracy': float(p.prediction_accuracy) if p.prediction_accuracy else None,
            'timestamp': p.prediction_timestamp.isoformat(),
        } for p in predictions],
        'count': len(predictions),
    })


# ============================================================
# Pricing Optimization API
# ============================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_pricing_optimization(request):
    """
    GET /api/learning/pricing/
    Get pricing optimization recommendations using PricingEngine.
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status=401)

    platform = request.GET.get('platform', 'etsy')
    content_type = request.GET.get('content_type', 'image')
    current_price = request.GET.get('current_price')

    # Use the ML-based PricingEngine
    from .learning_engine import PricingEngine

    engine = PricingEngine(user=request.user)
    result = engine.get_optimal_price(
        content_type=content_type,
        platform=platform,
        current_price=float(current_price) if current_price else None
    )

    # Also save to PricingOptimization model for tracking
    try:
        platform_obj = DistributionPlatform.objects.filter(name__icontains=platform).first()
    except Exception:
        platform_obj = None

    pricing, created = PricingOptimization.objects.update_or_create(
        user=request.user,
        content_category=content_type,
        platform=platform_obj,
        defaults={
            'optimal_price': Decimal(str(result['optimal_price'])),
            'optimal_price_confidence': Decimal(str(result['confidence'])),
            'price_range_suggestion': {
                'min': result['min_price'],
                'max': result['max_price'],
                'optimal': result['optimal_price'],
            },
        }
    )

    return api_success({
        'optimization': {
            'optimal_price': result['optimal_price'],
            'min_price': result['min_price'],
            'max_price': result['max_price'],
            'confidence': result['confidence'],
            'market_position': result.get('market_position', 'average'),
            'rationale': result['rationale'],
        },
        'platform': platform,
        'content_type': content_type,
    })


# ============================================================
# User Learning Profile API
# ============================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_learning_profile(request):
    """
    GET /api/learning/profile/
    Get user's learning profile with insights.
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status=401)

    # Get or create profile
    profile, created = UserLearningProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'preferred_styles': [],
            'preferred_platforms': [],
        }
    )

    # Update with latest data
    distributions = ContentDistribution.objects.filter(user=request.user)

    if distributions.exists():
        # Calculate success rate
        total = distributions.count()
        successful = distributions.filter(revenue_generated__gt=0).count()
        profile.overall_success_rate = (successful / total * 100) if total > 0 else 0
        profile.total_successful_distributions = successful

        # Total revenue
        total_rev = distributions.aggregate(total=Sum('revenue_generated'))['total']
        profile.total_lifetime_revenue = total_rev or Decimal('0')

        # Find strongest platforms
        platform_perf = distributions.values('platform__name').annotate(
            revenue=Sum('revenue_generated'),
            count=Count('id')
        ).order_by('-revenue')[:3]
        profile.strongest_categories = [p['platform__name'] for p in platform_perf if p['platform__name']]

        # Patterns discovered
        profile.patterns_discovered = SuccessPattern.objects.filter(user=request.user).count()

        # Insights generated
        profile.insights_generated = DistributionInsight.objects.filter(user=request.user).count()

        profile.save()

    return api_success({
        'profile': {
            'preferred_styles': profile.preferred_styles,
            'preferred_platforms': profile.preferred_platforms,
            'preferred_content_types': profile.preferred_content_types,
            'preferred_price_ranges': profile.preferred_price_ranges,
            'typical_upload_times': profile.typical_upload_times,
            'productivity_patterns': profile.productivity_patterns,
            'avg_content_per_week': float(profile.avg_content_per_week),
            'overall_success_rate': float(profile.overall_success_rate),
            'strongest_categories': profile.strongest_categories,
            'weakest_categories': profile.weakest_categories,
            'total_successful_distributions': profile.total_successful_distributions,
            'total_lifetime_revenue': float(profile.total_lifetime_revenue),
            'patterns_discovered': profile.patterns_discovered,
            'insights_generated': profile.insights_generated,
            'insights_acted_upon': profile.insights_acted_upon,
            'prediction_accuracy_avg': float(profile.prediction_accuracy_avg),
            'revenue_goals': profile.revenue_goals,
            'profile_completeness': profile.profile_completeness,
        },
        'last_activity': profile.last_activity.isoformat(),
    })


@csrf_exempt
@require_http_methods(["POST"])
def update_learning_profile(request):
    """
    POST /api/learning/profile/
    Update user's learning preferences.
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return api_error("Invalid JSON")

    profile, _ = UserLearningProfile.objects.get_or_create(user=request.user)

    # Update fields if provided
    if 'preferred_styles' in data:
        profile.preferred_styles = data['preferred_styles']
    if 'preferred_platforms' in data:
        profile.preferred_platforms = data['preferred_platforms']
    if 'revenue_goals' in data:
        profile.revenue_goals = data['revenue_goals']
    if 'notification_preferences' in data:
        profile.notification_preferences = data['notification_preferences']

    profile.save()

    return api_success({
        'message': 'Profile updated successfully',
        'profile_completeness': profile.profile_completeness,
    })


# ============================================================
# Distribution Insights API
# ============================================================

@csrf_exempt
@require_http_methods(["GET"])
def list_insights(request):
    """
    GET /api/learning/insights/
    List AI-generated insights for the user.
    """
    if not request.user.is_authenticated:
        return api_success({"insights": [], "count": 0})

    try:
        insight_type = request.GET.get('type')
        priority = request.GET.get('priority')
        unread_only = request.GET.get('unread_only', 'false').lower() == 'true'

        insights = DistributionInsight.objects.filter(
            user=request.user,
            is_still_relevant=True,
            is_dismissed=False
        )

        if insight_type:
            insights = insights.filter(insight_type=insight_type)
        if priority:
            insights = insights.filter(priority=priority)
        if unread_only:
            insights = insights.filter(is_read=False)

        insights = insights.order_by('-created_at')[:50]

        return api_success({
            'insights': [{
                'id': str(i.id),
                'type': i.insight_type,
                'priority': i.priority,
                'title': i.title,
                'message': i.message,
                'recommended_actions': i.recommended_actions,
                'potential_impact': float(i.potential_revenue_impact) if i.potential_revenue_impact else None,
                'confidence': float(i.confidence_level),
                'is_read': i.is_read,
                'is_acted_upon': i.is_acted_upon,
                'created_at': i.created_at.isoformat(),
            } for i in insights],
            'unread_count': DistributionInsight.objects.filter(
                user=request.user, is_read=False, is_still_relevant=True
            ).count(),
        })
    except Exception:
        return api_success({'insights': [], 'unread_count': 0})


@csrf_exempt
@require_http_methods(["POST"])
def generate_insights(request):
    """
    POST /api/learning/insights/generate/
    Generate new insights based on recent activity.
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status=401)

    insights_created = []

    # Get recent distributions
    recent_dist = ContentDistribution.objects.filter(
        user=request.user,
        created_at__gte=timezone.now() - timedelta(days=30)
    )

    # Revenue milestone insight
    total_revenue = recent_dist.aggregate(total=Sum('revenue_generated'))['total'] or Decimal('0')
    milestones = [100, 500, 1000, 5000, 10000]
    for milestone in milestones:
        if float(total_revenue) >= milestone:
            existing = DistributionInsight.objects.filter(
                user=request.user,
                insight_type='milestone',
                title__icontains=f"${milestone}"
            ).exists()

            if not existing:
                insight = DistributionInsight.objects.create(
                    user=request.user,
                    insight_type='milestone',
                    priority='high',
                    title=f"Revenue Milestone: ${milestone}!",
                    message=f"Congratulations! You've earned ${total_revenue:.2f} in the last 30 days!",
                    supporting_data={'revenue': float(total_revenue), 'milestone': milestone},
                    potential_revenue_impact=Decimal(str(milestone * 0.2)),
                    confidence_level=Decimal('95'),
                )
                insights_created.append(insight.title)

    # Low activity warning
    if recent_dist.count() < 3:
        existing = DistributionInsight.objects.filter(
            user=request.user,
            insight_type='warning',
            title__icontains='Low Activity',
            created_at__gte=timezone.now() - timedelta(days=7)
        ).exists()

        if not existing:
            insight = DistributionInsight.objects.create(
                user=request.user,
                insight_type='warning',
                priority='medium',
                title="Low Distribution Activity",
                message="You've only distributed {0} items in the last 30 days. Consider increasing your output.".format(
                    recent_dist.count()
                ),
                recommended_actions=[
                    {'action': 'Create more content', 'expected_impact': '+50% potential revenue'},
                    {'action': 'Use batch upload', 'expected_impact': 'Save 2+ hours'},
                ],
                confidence_level=Decimal('80'),
            )
            insights_created.append(insight.title)

    # Best performing content insight
    top_performer = recent_dist.filter(revenue_generated__gt=0).order_by('-revenue_generated').first()
    if top_performer:
        existing = DistributionInsight.objects.filter(
            user=request.user,
            insight_type='trend',
            created_at__gte=timezone.now() - timedelta(days=7)
        ).exists()

        if not existing:
            insight = DistributionInsight.objects.create(
                user=request.user,
                insight_type='trend',
                priority='medium',
                title="Top Performer Identified",
                message=f"'{top_performer.title}' generated ${top_performer.revenue_generated:.2f}. Consider creating similar content!",
                supporting_data={
                    'content_id': str(top_performer.id),
                    'revenue': float(top_performer.revenue_generated),
                    'platform': top_performer.platform.name if top_performer.platform else None,
                },
                recommended_actions=[
                    {'action': 'Create similar content', 'expected_impact': '+30% potential revenue'},
                ],
                potential_revenue_impact=top_performer.revenue_generated * Decimal('0.3'),
                confidence_level=Decimal('70'),
            )
            insights_created.append(insight.title)

    return api_success({
        'insights_generated': len(insights_created),
        'insight_titles': insights_created,
    })


@csrf_exempt
@require_http_methods(["POST"])
def mark_insight_read(request, insight_id):
    """
    POST /api/learning/insights/<id>/read/
    Mark an insight as read.
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status=401)

    try:
        insight = DistributionInsight.objects.get(id=insight_id, user=request.user)
        insight.is_read = True
        insight.save()
        return api_success({'message': 'Insight marked as read'})
    except DistributionInsight.DoesNotExist:
        return api_error("Insight not found", status=404)


@csrf_exempt
@require_http_methods(["POST"])
def dismiss_insight(request, insight_id):
    """
    POST /api/learning/insights/<id>/dismiss/
    Dismiss an insight.
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status=401)

    try:
        insight = DistributionInsight.objects.get(id=insight_id, user=request.user)
        insight.is_dismissed = True
        insight.save()
        return api_success({'message': 'Insight dismissed'})
    except DistributionInsight.DoesNotExist:
        return api_error("Insight not found", status=404)


# ============================================================
# Performance Comparison API
# ============================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_performance_comparison(request):
    """
    GET /api/learning/compare/
    Get user's performance compared to benchmarks.
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status=401)

    comparison_type = request.GET.get('type', 'platform')
    scope_value = request.GET.get('scope', 'all')
    days = int(request.GET.get('days', 30))

    period_end = timezone.now().date()
    period_start = period_end - timedelta(days=days)

    # Get user metrics
    user_distributions = ContentDistribution.objects.filter(
        user=request.user,
        created_at__gte=period_start,
        status='completed'
    )

    user_revenue = user_distributions.aggregate(total=Sum('revenue_generated'))['total'] or Decimal('0')
    user_sales = user_distributions.filter(revenue_generated__gt=0).count()
    user_items = user_distributions.count()

    user_metrics = {
        'revenue': float(user_revenue),
        'items_sold': user_sales,
        'items_listed': user_items,
        'conversion_rate': (user_sales / user_items * 100) if user_items > 0 else 0,
        'avg_price': float(user_distributions.aggregate(avg=Avg('price_listed'))['avg'] or 0),
    }

    # Mock benchmark data (in real app, this would come from aggregated user data)
    benchmark_metrics = {
        'revenue': {'p25': 100, 'p50': 300, 'p75': 800, 'p90': 2000},
        'items_sold': {'p25': 2, 'p50': 8, 'p75': 20, 'p90': 50},
        'conversion_rate': {'p25': 1.0, 'p50': 3.0, 'p75': 5.0, 'p90': 10.0},
    }

    # Calculate percentile rankings
    percentile_rankings = {}
    for metric, benchmarks in benchmark_metrics.items():
        value = user_metrics.get(metric, 0)
        if value <= benchmarks['p25']:
            percentile = 25 * (value / benchmarks['p25']) if benchmarks['p25'] > 0 else 0
        elif value <= benchmarks['p50']:
            percentile = 25 + 25 * ((value - benchmarks['p25']) / (benchmarks['p50'] - benchmarks['p25']))
        elif value <= benchmarks['p75']:
            percentile = 50 + 25 * ((value - benchmarks['p50']) / (benchmarks['p75'] - benchmarks['p50']))
        elif value <= benchmarks['p90']:
            percentile = 75 + 15 * ((value - benchmarks['p75']) / (benchmarks['p90'] - benchmarks['p75']))
        else:
            percentile = 90 + 10 * min(1, (value - benchmarks['p90']) / benchmarks['p90'])

        percentile_rankings[metric] = round(min(99, percentile), 1)

    # Generate insights
    strengths = []
    weaknesses = []
    opportunities = []

    if percentile_rankings.get('revenue', 0) >= 75:
        strengths.append("Top 25% in revenue generation")
    elif percentile_rankings.get('revenue', 0) <= 25:
        weaknesses.append("Revenue is below average")
        opportunities.append("Increase pricing or volume to improve revenue")

    if percentile_rankings.get('conversion_rate', 0) >= 75:
        strengths.append("Excellent conversion rate")
    elif percentile_rankings.get('conversion_rate', 0) <= 25:
        weaknesses.append("Low conversion rate")
        opportunities.append("Improve content quality or pricing to boost conversions")

    # Create or update comparison record
    comparison, _ = PerformanceComparison.objects.update_or_create(
        user=request.user,
        comparison_type=comparison_type,
        scope_value=scope_value,
        period_start=period_start,
        period_end=period_end,
        defaults={
            'user_metrics': user_metrics,
            'benchmark_metrics': benchmark_metrics,
            'percentile_rankings': percentile_rankings,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'improvement_opportunities': opportunities,
            'sample_size': 1000,  # Mock
        }
    )

    return api_success({
        'comparison': {
            'type': comparison_type,
            'scope': scope_value,
            'period': {'start': str(period_start), 'end': str(period_end), 'days': days},
            'user_metrics': user_metrics,
            'benchmark_metrics': benchmark_metrics,
            'percentile_rankings': percentile_rankings,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'opportunities': opportunities,
            'sample_size': comparison.sample_size,
        }
    })


# ============================================================
# Learning Dashboard API
# ============================================================

@csrf_exempt
@require_http_methods(["GET"])
def learning_dashboard(request):
    """
    GET /api/learning/dashboard/
    Get comprehensive learning dashboard data.
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status=401)

    # Get profile
    profile, _ = UserLearningProfile.objects.get_or_create(user=request.user)

    # Get recent patterns
    patterns = SuccessPattern.objects.filter(
        Q(user=request.user) | Q(is_global=True),
        is_active=True
    ).order_by('-success_rate')[:5]

    # Get recent insights
    insights = DistributionInsight.objects.filter(
        user=request.user,
        is_still_relevant=True,
        is_dismissed=False
    ).order_by('-created_at')[:5]

    # Get recent predictions
    predictions = ContentPerformancePrediction.objects.filter(
        user=request.user
    ).order_by('-prediction_timestamp')[:5]

    # Calculate prediction accuracy
    verified_predictions = predictions.filter(actual_success__isnull=False)
    if verified_predictions.exists():
        accuracy = verified_predictions.aggregate(avg=Avg('prediction_accuracy'))['avg']
    else:
        accuracy = None

    return api_success({
        'dashboard': {
            'profile_summary': {
                'success_rate': float(profile.overall_success_rate),
                'lifetime_revenue': float(profile.total_lifetime_revenue),
                'patterns_discovered': profile.patterns_discovered,
                'profile_completeness': profile.profile_completeness,
            },
            'top_patterns': [{
                'name': p.pattern_name,
                'success_rate': float(p.success_rate),
                'revenue': float(p.total_revenue_attributed),
            } for p in patterns],
            'recent_insights': [{
                'title': i.title,
                'type': i.insight_type,
                'priority': i.priority,
                'is_read': i.is_read,
            } for i in insights],
            'unread_insights_count': DistributionInsight.objects.filter(
                user=request.user, is_read=False, is_still_relevant=True
            ).count(),
            'prediction_accuracy': float(accuracy) if accuracy else None,
            'recent_predictions_count': predictions.count(),
        }
    })


# ============================================================
# Session 954: Learning Loop Effectiveness API
# ============================================================

@csrf_exempt
@require_http_methods(["GET"])
def learning_loop_stats(request):
    """
    GET /api/learning/loop/stats/
    Get comprehensive learning loop effectiveness statistics.

    Returns stats on active learnings, effectiveness rates, and recent patterns.
    """
    try:
        from .services.learning_loop_orchestrator import get_learning_loop_orchestrator

        orchestrator = get_learning_loop_orchestrator()
        stats = orchestrator.get_learning_effectiveness_stats()

        return api_success({
            'learning_loop': stats,
        })
    except Exception:
        return api_success({
            'learning_loop': {
                'total_active_learnings': 0,
                'total_applied': 0,
                'total_successful': 0,
                'overall_effectiveness': 0,
                'applied_patterns_count': 0,
                'most_effective': [],
                'least_effective': [],
                'recent_learnings': [],
                'by_pattern_type': [],
            },
        })


@csrf_exempt
@require_http_methods(["POST"])
def track_learning_outcome(request):
    """
    POST /api/learning/loop/track/
    Track when a learning pattern is applied and its outcome.

    Body:
        pattern_id: UUID of the learning pattern
        was_successful: boolean indicating outcome
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return api_error("Invalid JSON")

    pattern_id = data.get('pattern_id')
    was_successful = data.get('was_successful', False)

    if not pattern_id:
        return api_error("pattern_id is required")

    from .services.learning_loop_orchestrator import get_learning_loop_orchestrator

    orchestrator = get_learning_loop_orchestrator()
    success = orchestrator.track_learning_application(pattern_id, was_successful)

    if success:
        return api_success({
            'message': 'Learning outcome tracked successfully',
            'pattern_id': pattern_id,
            'was_successful': was_successful,
        })
    else:
        return api_error("Failed to track learning outcome", status=400)


@csrf_exempt
@require_http_methods(["POST"])
def run_learning_cycle(request):
    """
    POST /api/learning/loop/run/
    Trigger a learning cycle to extract and persist learnings.

    This analyzes tool outcomes, decision records, and user feedback
    to extract actionable learning patterns.
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status=401)

    from .services.learning_loop_orchestrator import get_learning_loop_orchestrator

    orchestrator = get_learning_loop_orchestrator()
    result = orchestrator.run_learning_cycle()

    return api_success({
        'cycle_result': result,
    })


@csrf_exempt
@require_http_methods(["GET"])
def get_agent_learnings(request):
    """
    GET /api/learning/loop/agent/<agent_name>/
    Get learnings formatted for a specific agent.

    Query params:
        agent_name: Name of the agent (required)
        max_learnings: Maximum number of learnings (default 5)
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status=401)

    agent_name = request.GET.get('agent_name')
    if not agent_name:
        return api_error("agent_name query parameter is required")

    max_learnings = int(request.GET.get('max_learnings', 5))

    from .services.learning_loop_orchestrator import get_learning_loop_orchestrator

    orchestrator = get_learning_loop_orchestrator()
    learnings = orchestrator.get_learnings_for_agent(agent_name, max_learnings)
    formatted = orchestrator.format_learnings_for_prompt(agent_name, max_learnings)

    return api_success({
        'agent_name': agent_name,
        'learnings': learnings,
        'formatted_for_prompt': formatted,
    })
