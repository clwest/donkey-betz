"""
Session 233: Learning Engine - ML Training Pipeline
Phase 5 - Creative Intelligence Empire

This module provides the core ML algorithms for:
- Pattern discovery from distribution data
- Content performance scoring
- Price optimization calculations
- User behavior learning
- Real-time insight generation
"""

import logging
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from django.db.models import Avg, Sum, Count, Q
from django.utils import timezone

logger = logging.getLogger(__name__)


class PatternDiscoveryEngine:
    """
    Discovers success patterns from distribution and sales data.
    Uses statistical analysis to identify what works.
    """

    def __init__(self, user=None):
        self.user = user

    def discover_patterns(self, days: int = 90) -> List[Dict]:
        """
        Analyze historical data to discover success patterns.
        Returns list of discovered patterns with confidence scores.
        """
        from .models_unified_system import (
            ContentDistribution, DistributionAnalytics
        )

        cutoff = timezone.now() - timedelta(days=days)
        patterns = []

        # Get user's distribution data
        query = Q(created_at__gte=cutoff)
        if self.user:
            query &= Q(user=self.user)

        distributions = ContentDistribution.objects.filter(query)
        analytics = DistributionAnalytics.objects.filter(
            distribution__in=distributions
        )

        if distributions.count() < 5:
            return patterns  # Not enough data

        # 1. Content Style Patterns
        style_patterns = self._analyze_content_styles(distributions, analytics)
        patterns.extend(style_patterns)

        # 2. Pricing Patterns
        pricing_patterns = self._analyze_pricing(distributions, analytics)
        patterns.extend(pricing_patterns)

        # 3. Timing Patterns
        timing_patterns = self._analyze_timing(distributions, analytics)
        patterns.extend(timing_patterns)

        # 4. Platform Match Patterns
        platform_patterns = self._analyze_platforms(distributions, analytics)
        patterns.extend(platform_patterns)

        # 5. Tag Patterns
        tag_patterns = self._analyze_tags(distributions, analytics)
        patterns.extend(tag_patterns)

        return patterns

    def _analyze_content_styles(self, distributions, analytics) -> List[Dict]:
        """Analyze which content styles perform best."""
        patterns = []

        # Group by content type
        content_types = distributions.values('content_type').annotate(
            count=Count('id'),
            total_revenue=Sum('analytics__revenue_generated'),
            avg_views=Avg('analytics__views'),
            avg_sales=Avg('analytics__sales'),
        ).filter(count__gte=3)

        for ct in content_types:
            if ct['total_revenue'] and ct['total_revenue'] > 0:
                success_rate = min(100, (ct['avg_sales'] or 0) / max(ct['count'], 1) * 100)
                patterns.append({
                    'type': 'content_style',
                    'name': f"{ct['content_type'].title()} Content",
                    'description': f"Your {ct['content_type']} content generates ${ct['total_revenue']:.2f} avg revenue",
                    'attributes': {'content_type': ct['content_type']},
                    'success_rate': success_rate,
                    'confidence': min(95, 50 + ct['count'] * 5),
                    'sample_size': ct['count'],
                    'avg_revenue': float(ct['total_revenue'] / ct['count']) if ct['count'] > 0 else 0,
                })

        return patterns

    def _analyze_pricing(self, distributions, analytics) -> List[Dict]:
        """Analyze pricing patterns that lead to sales."""
        patterns = []

        # Group by price ranges
        price_ranges = [
            (0, 10, 'Budget ($0-$10)'),
            (10, 25, 'Mid-range ($10-$25)'),
            (25, 50, 'Premium ($25-$50)'),
            (50, 100, 'High-end ($50-$100)'),
            (100, 10000, 'Luxury ($100+)'),
        ]

        for min_price, max_price, label in price_ranges:
            range_dist = distributions.filter(
                price__gte=min_price,
                price__lt=max_price
            )
            if range_dist.count() >= 2:
                range_analytics = analytics.filter(distribution__in=range_dist)
                total_sales = range_analytics.aggregate(s=Sum('sales'))['s'] or 0
                total_revenue = range_analytics.aggregate(r=Sum('revenue_generated'))['r'] or 0

                if total_sales > 0:
                    patterns.append({
                        'type': 'pricing_strategy',
                        'name': f"{label} Pricing",
                        'description': f"Items priced {label} generated {total_sales} sales",
                        'attributes': {'min_price': min_price, 'max_price': max_price},
                        'success_rate': min(100, total_sales / range_dist.count() * 50),
                        'confidence': min(90, 40 + range_dist.count() * 5),
                        'sample_size': range_dist.count(),
                        'avg_revenue': float(total_revenue / max(total_sales, 1)),
                    })

        return patterns

    def _analyze_timing(self, distributions, analytics) -> List[Dict]:
        """Analyze upload timing patterns."""
        patterns = []

        # Analyze by day of week
        day_performance = defaultdict(lambda: {'count': 0, 'sales': 0, 'revenue': 0})

        for dist in distributions:
            day = dist.created_at.strftime('%A')
            day_performance[day]['count'] += 1

            dist_analytics = analytics.filter(distribution=dist).first()
            if dist_analytics:
                day_performance[day]['sales'] += dist_analytics.sales or 0
                day_performance[day]['revenue'] += float(dist_analytics.revenue_generated or 0)

        best_day = max(day_performance.items(), key=lambda x: x[1]['sales'], default=(None, None))
        if best_day[0] and best_day[1]['sales'] > 0:
            patterns.append({
                'type': 'timing',
                'name': f"Upload on {best_day[0]}",
                'description': f"{best_day[0]} uploads get {best_day[1]['sales']} avg sales",
                'attributes': {'best_day': best_day[0]},
                'success_rate': min(100, best_day[1]['sales'] / max(best_day[1]['count'], 1) * 100),
                'confidence': min(85, 40 + best_day[1]['count'] * 5),
                'sample_size': best_day[1]['count'],
                'avg_revenue': best_day[1]['revenue'] / max(best_day[1]['count'], 1),
            })

        # Analyze by hour
        hour_performance = defaultdict(lambda: {'count': 0, 'sales': 0})
        for dist in distributions:
            hour = dist.created_at.hour
            hour_performance[hour]['count'] += 1
            dist_analytics = analytics.filter(distribution=dist).first()
            if dist_analytics:
                hour_performance[hour]['sales'] += dist_analytics.sales or 0

        if hour_performance:
            best_hour = max(hour_performance.items(), key=lambda x: x[1]['sales'])
            if best_hour[1]['sales'] > 0:
                hour_label = f"{best_hour[0]}:00" if best_hour[0] >= 10 else f"0{best_hour[0]}:00"
                patterns.append({
                    'type': 'timing',
                    'name': f"Upload around {hour_label}",
                    'description': f"Uploads at {hour_label} perform best",
                    'attributes': {'best_hour': best_hour[0]},
                    'success_rate': min(100, best_hour[1]['sales'] / max(best_hour[1]['count'], 1) * 100),
                    'confidence': min(75, 35 + best_hour[1]['count'] * 3),
                    'sample_size': best_hour[1]['count'],
                })

        return patterns

    def _analyze_platforms(self, distributions, analytics) -> List[Dict]:
        """Analyze which platforms work best."""
        patterns = []

        platform_stats = distributions.values('platform__name').annotate(
            count=Count('id'),
            total_sales=Sum('analytics__sales'),
            total_revenue=Sum('analytics__revenue_generated'),
            avg_views=Avg('analytics__views'),
        ).filter(count__gte=2)

        for ps in platform_stats:
            if ps['total_sales'] and ps['total_sales'] > 0:
                patterns.append({
                    'type': 'platform_match',
                    'name': f"{ps['platform__name']} Success",
                    'description': f"Your content performs well on {ps['platform__name']}",
                    'attributes': {'platform': ps['platform__name']},
                    'success_rate': min(100, ps['total_sales'] / ps['count'] * 50),
                    'confidence': min(90, 45 + ps['count'] * 5),
                    'sample_size': ps['count'],
                    'avg_revenue': float(ps['total_revenue'] / ps['count']) if ps['count'] > 0 else 0,
                })

        return patterns

    def _analyze_tags(self, distributions, analytics) -> List[Dict]:
        """Analyze which tag combinations work best."""
        patterns = []
        tag_performance = defaultdict(lambda: {'count': 0, 'sales': 0, 'revenue': 0})

        for dist in distributions:
            tags = dist.tags or []
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(',')]

            dist_analytics = analytics.filter(distribution=dist).first()
            sales = dist_analytics.sales if dist_analytics else 0
            revenue = float(dist_analytics.revenue_generated) if dist_analytics else 0

            for tag in tags[:10]:  # Limit to first 10 tags
                tag_lower = tag.lower().strip()
                if tag_lower:
                    tag_performance[tag_lower]['count'] += 1
                    tag_performance[tag_lower]['sales'] += sales or 0
                    tag_performance[tag_lower]['revenue'] += revenue

        # Find best performing tags
        top_tags = sorted(
            tag_performance.items(),
            key=lambda x: x[1]['sales'],
            reverse=True
        )[:5]

        for tag, stats in top_tags:
            if stats['sales'] > 0 and stats['count'] >= 2:
                patterns.append({
                    'type': 'tag_combination',
                    'name': f"Tag: {tag}",
                    'description': f"Content tagged '{tag}' generated {stats['sales']} sales",
                    'attributes': {'tag': tag},
                    'success_rate': min(100, stats['sales'] / stats['count'] * 50),
                    'confidence': min(80, 35 + stats['count'] * 3),
                    'sample_size': stats['count'],
                    'avg_revenue': stats['revenue'] / max(stats['count'], 1),
                })

        return patterns

    def save_patterns(self, patterns: List[Dict]) -> int:
        """Save discovered patterns to database."""
        from .models_unified_system import SuccessPattern

        saved = 0
        for p in patterns:
            pattern, created = SuccessPattern.objects.update_or_create(
                user=self.user,
                pattern_type=p['type'],
                pattern_name=p['name'],
                defaults={
                    'pattern_description': p.get('description', ''),
                    'pattern_attributes': p.get('attributes', {}),
                    'success_rate': Decimal(str(p.get('success_rate', 0))),
                    'confidence_score': Decimal(str(p.get('confidence', 50))),
                    'sample_size': p.get('sample_size', 0),
                    'avg_revenue_per_success': Decimal(str(p.get('avg_revenue', 0))),
                    'is_active': True,
                }
            )
            saved += 1

        return saved


class ContentScoringEngine:
    """
    Scores content performance potential before distribution.
    Uses discovered patterns to predict success.
    """

    def __init__(self, user=None):
        self.user = user

    def score_content(
        self,
        content_type: str,
        platforms: List[str],
        tags: List[str],
        price: float,
        title: str = "",
        description: str = "",
    ) -> Dict:
        """
        Score content based on discovered patterns and historical data.
        Returns a comprehensive score with breakdown.
        """
        from .models_unified_system import SuccessPattern

        scores = {
            'overall': 0,
            'platform_fit': {},
            'price_score': 0,
            'timing_score': 0,
            'tag_score': 0,
            'content_type_score': 0,
            'recommendations': [],
        }

        # Get user's patterns
        query = Q(is_active=True)
        if self.user:
            query &= (Q(user=self.user) | Q(is_global=True))
        else:
            query &= Q(is_global=True)

        patterns = SuccessPattern.objects.filter(query)

        # Score content type
        content_patterns = patterns.filter(
            pattern_type='content_style',
            pattern_attributes__content_type=content_type
        )
        if content_patterns.exists():
            best = content_patterns.order_by('-success_rate').first()
            scores['content_type_score'] = float(best.success_rate)
        else:
            scores['content_type_score'] = 50  # Default

        # Score each platform
        for platform in platforms:
            platform_patterns = patterns.filter(
                pattern_type='platform_match',
                pattern_attributes__platform__icontains=platform
            )
            if platform_patterns.exists():
                best = platform_patterns.order_by('-success_rate').first()
                scores['platform_fit'][platform] = {
                    'score': float(best.success_rate),
                    'confidence': float(best.confidence_score),
                    'avg_revenue': float(best.avg_revenue_per_success),
                }
            else:
                scores['platform_fit'][platform] = {
                    'score': 50,
                    'confidence': 30,
                    'avg_revenue': 0,
                }

        # Score pricing
        pricing_patterns = patterns.filter(pattern_type='pricing_strategy')
        for pp in pricing_patterns:
            attrs = pp.pattern_attributes or {}
            min_p = attrs.get('min_price', 0)
            max_p = attrs.get('max_price', 10000)
            if min_p <= price < max_p:
                scores['price_score'] = float(pp.success_rate)
                break
        if scores['price_score'] == 0:
            scores['price_score'] = 50

        # Score tags
        tag_scores = []
        for tag in tags:
            tag_patterns = patterns.filter(
                pattern_type='tag_combination',
                pattern_attributes__tag__iexact=tag.strip()
            )
            if tag_patterns.exists():
                best = tag_patterns.order_by('-success_rate').first()
                tag_scores.append(float(best.success_rate))
        scores['tag_score'] = sum(tag_scores) / len(tag_scores) if tag_scores else 50

        # Score timing (current time)
        now = timezone.now()
        timing_patterns = patterns.filter(
            pattern_type='timing',
            pattern_attributes__best_hour=now.hour
        )
        if timing_patterns.exists():
            best = timing_patterns.order_by('-success_rate').first()
            scores['timing_score'] = float(best.success_rate)
        else:
            scores['timing_score'] = 50

        # Calculate overall score
        platform_avg = sum(p['score'] for p in scores['platform_fit'].values()) / max(len(scores['platform_fit']), 1)
        scores['overall'] = (
            scores['content_type_score'] * 0.25 +
            platform_avg * 0.25 +
            scores['price_score'] * 0.20 +
            scores['tag_score'] * 0.20 +
            scores['timing_score'] * 0.10
        )

        # Generate recommendations
        if scores['price_score'] < 60:
            scores['recommendations'].append({
                'type': 'pricing',
                'message': 'Consider adjusting your price based on top-performing ranges',
                'priority': 'high' if scores['price_score'] < 40 else 'medium',
            })

        if scores['tag_score'] < 60:
            scores['recommendations'].append({
                'type': 'tags',
                'message': 'Add more high-performing tags to increase visibility',
                'priority': 'medium',
            })

        if scores['timing_score'] < 60:
            best_timing = patterns.filter(pattern_type='timing').order_by('-success_rate').first()
            if best_timing:
                attrs = best_timing.pattern_attributes or {}
                if 'best_day' in attrs:
                    scores['recommendations'].append({
                        'type': 'timing',
                        'message': f"Consider uploading on {attrs['best_day']} for better results",
                        'priority': 'low',
                    })

        return scores


class PricingEngine:
    """
    Optimizes pricing based on market data and user history.
    """

    def __init__(self, user=None):
        self.user = user

    def get_optimal_price(
        self,
        content_type: str,
        platform: str,
        current_price: Optional[float] = None,
    ) -> Dict:
        """
        Calculate optimal pricing for content.
        """
        from .models_unified_system import (
            ContentDistribution, DistributionAnalytics
        )

        result = {
            'optimal_price': 0,
            'min_price': 0,
            'max_price': 0,
            'confidence': 0,
            'rationale': '',
            'market_position': 'average',
            'price_elasticity': 0,
        }

        # Get historical pricing data
        query = Q(content_type=content_type)
        if self.user:
            query &= Q(user=self.user)

        distributions = ContentDistribution.objects.filter(query)

        if distributions.count() < 3:
            # Use default pricing based on content type and platform
            defaults = self._get_default_pricing(content_type, platform)
            result.update(defaults)
            result['rationale'] = 'Based on market averages (limited personal data)'
            return result

        # Analyze price performance
        price_performance = []
        for dist in distributions:
            analytics = DistributionAnalytics.objects.filter(distribution=dist).first()
            if analytics and dist.price:
                conversion = (analytics.sales or 0) / max(analytics.views or 1, 1)
                revenue = float(analytics.revenue_generated or 0)
                price_performance.append({
                    'price': float(dist.price),
                    'conversion': conversion,
                    'revenue': revenue,
                    'sales': analytics.sales or 0,
                })

        if not price_performance:
            defaults = self._get_default_pricing(content_type, platform)
            result.update(defaults)
            return result

        # Find optimal price point
        # Strategy: Maximize revenue while maintaining reasonable conversion
        best_price = max(price_performance, key=lambda x: x['revenue'])
        avg_price = sum(p['price'] for p in price_performance) / len(price_performance)

        result['optimal_price'] = round(best_price['price'], 2)
        result['min_price'] = round(min(p['price'] for p in price_performance) * 0.8, 2)
        result['max_price'] = round(max(p['price'] for p in price_performance) * 1.2, 2)
        result['confidence'] = min(90, 40 + len(price_performance) * 5)

        # Determine market position
        if best_price['price'] > avg_price * 1.2:
            result['market_position'] = 'premium'
        elif best_price['price'] < avg_price * 0.8:
            result['market_position'] = 'budget'
        else:
            result['market_position'] = 'competitive'

        # Build rationale
        result['rationale'] = (
            f"Based on {len(price_performance)} similar items. "
            f"Your best-performing price was ${best_price['price']:.2f} "
            f"with {best_price['sales']} sales generating ${best_price['revenue']:.2f}."
        )

        return result

    def _get_default_pricing(self, content_type: str, platform: str) -> Dict:
        """Default pricing based on content type and platform."""
        defaults = {
            'image': {
                'etsy': {'optimal': 14.99, 'min': 4.99, 'max': 49.99},
                'gumroad': {'optimal': 9.99, 'min': 2.99, 'max': 29.99},
                'shutterstock': {'optimal': 0.25, 'min': 0.10, 'max': 2.00},
                'redbubble': {'optimal': 19.99, 'min': 9.99, 'max': 39.99},
                'default': {'optimal': 12.99, 'min': 4.99, 'max': 39.99},
            },
            'video': {
                'etsy': {'optimal': 29.99, 'min': 9.99, 'max': 99.99},
                'gumroad': {'optimal': 19.99, 'min': 4.99, 'max': 79.99},
                'default': {'optimal': 24.99, 'min': 9.99, 'max': 79.99},
            },
            'audio': {
                'gumroad': {'optimal': 9.99, 'min': 2.99, 'max': 29.99},
                'default': {'optimal': 9.99, 'min': 2.99, 'max': 29.99},
            },
            '3d': {
                'gumroad': {'optimal': 24.99, 'min': 9.99, 'max': 99.99},
                'etsy': {'optimal': 19.99, 'min': 7.99, 'max': 79.99},
                'default': {'optimal': 24.99, 'min': 9.99, 'max': 79.99},
            },
            'template': {
                'etsy': {'optimal': 9.99, 'min': 2.99, 'max': 29.99},
                'gumroad': {'optimal': 14.99, 'min': 4.99, 'max': 49.99},
                'creative_market': {'optimal': 19.99, 'min': 9.99, 'max': 59.99},
                'default': {'optimal': 14.99, 'min': 4.99, 'max': 49.99},
            },
        }

        content_defaults = defaults.get(content_type, defaults.get('image'))
        platform_pricing = content_defaults.get(platform, content_defaults.get('default'))

        return {
            'optimal_price': platform_pricing['optimal'],
            'min_price': platform_pricing['min'],
            'max_price': platform_pricing['max'],
            'confidence': 60,
        }


class InsightGenerator:
    """
    Generates AI-powered insights from learning data.
    """

    def __init__(self, user=None):
        self.user = user

    def generate_insights(self, max_insights: int = 10) -> List[Dict]:
        """Generate actionable insights from user's data."""

        insights = []

        # 1. Revenue trend insights
        revenue_insight = self._analyze_revenue_trend()
        if revenue_insight:
            insights.append(revenue_insight)

        # 2. Best performing content insight
        best_content = self._find_best_content()
        if best_content:
            insights.append(best_content)

        # 3. Underperforming content warning
        underperforming = self._find_underperforming()
        if underperforming:
            insights.append(underperforming)

        # 4. Pricing opportunity
        pricing_insight = self._analyze_pricing_opportunities()
        if pricing_insight:
            insights.append(pricing_insight)

        # 5. Platform recommendation
        platform_insight = self._recommend_platforms()
        if platform_insight:
            insights.append(platform_insight)

        # 6. Timing suggestion
        timing_insight = self._suggest_timing()
        if timing_insight:
            insights.append(timing_insight)

        # 7. Tag optimization
        tag_insight = self._optimize_tags()
        if tag_insight:
            insights.append(tag_insight)

        # 8. Success celebration
        success = self._celebrate_success()
        if success:
            insights.append(success)

        return insights[:max_insights]

    def _analyze_revenue_trend(self) -> Optional[Dict]:
        """Analyze revenue trend and generate insight."""
        from .models_unified_system import DistributionAnalytics

        now = timezone.now()
        last_30 = now - timedelta(days=30)
        prev_30 = last_30 - timedelta(days=30)

        query = Q()
        if self.user:
            query &= Q(distribution__user=self.user)

        recent = DistributionAnalytics.objects.filter(
            query, distribution__created_at__gte=last_30
        ).aggregate(total=Sum('revenue_generated'))['total'] or 0

        previous = DistributionAnalytics.objects.filter(
            query,
            distribution__created_at__gte=prev_30,
            distribution__created_at__lt=last_30
        ).aggregate(total=Sum('revenue_generated'))['total'] or 0

        if previous > 0:
            change = ((recent - previous) / previous) * 100
            if change > 20:
                return {
                    'type': 'success_celebration',
                    'title': 'Revenue Growing!',
                    'message': f'Your revenue is up {change:.1f}% compared to last month!',
                    'priority': 'high',
                    'action_items': ['Keep doing what works', 'Consider scaling successful content'],
                }
            elif change < -20:
                return {
                    'type': 'performance_warning',
                    'title': 'Revenue Declining',
                    'message': f'Revenue is down {abs(change):.1f}% from last month.',
                    'priority': 'high',
                    'action_items': ['Review recent content performance', 'Check pricing strategy', 'Consider new platforms'],
                }

        return None

    def _find_best_content(self) -> Optional[Dict]:
        """Find and highlight best performing content."""
        from .models_unified_system import ContentDistribution

        query = Q()
        if self.user:
            query &= Q(user=self.user)

        best = ContentDistribution.objects.filter(query).annotate(
            revenue=Sum('analytics__revenue_generated'),
            sales=Sum('analytics__sales')
        ).order_by('-revenue').first()

        if best and best.revenue and best.revenue > 0:
            return {
                'type': 'success_celebration',
                'title': 'Top Performer Found!',
                'message': f'"{best.title}" has earned ${best.revenue:.2f} with {best.sales} sales!',
                'priority': 'medium',
                'action_items': [
                    'Create similar content',
                    'Use same tags and pricing strategy',
                    f'Distribute more to {best.platform.name if best.platform else "this platform"}'
                ],
            }

        return None

    def _find_underperforming(self) -> Optional[Dict]:
        """Find underperforming content that needs attention."""
        from .models_unified_system import ContentDistribution

        query = Q()
        if self.user:
            query &= Q(user=self.user)

        # Find items with views but no sales (older than 7 days)
        week_ago = timezone.now() - timedelta(days=7)

        underperforming = ContentDistribution.objects.filter(
            query,
            created_at__lt=week_ago,
            analytics__views__gt=10,
            analytics__sales=0
        ).first()

        if underperforming:
            return {
                'type': 'performance_warning',
                'title': 'Content Needs Attention',
                'message': f'"{underperforming.title}" has views but no sales yet.',
                'priority': 'medium',
                'action_items': [
                    'Review and update title/description',
                    'Consider lowering price temporarily',
                    'Add more relevant tags'
                ],
            }

        return None

    def _analyze_pricing_opportunities(self) -> Optional[Dict]:
        """Find pricing optimization opportunities."""
        from .models_unified_system import SuccessPattern

        query = Q(pattern_type='pricing_strategy', is_active=True)
        if self.user:
            query &= (Q(user=self.user) | Q(is_global=True))

        best_pricing = SuccessPattern.objects.filter(query).order_by('-success_rate').first()

        if best_pricing and best_pricing.success_rate > 60:
            attrs = best_pricing.pattern_attributes or {}
            return {
                'type': 'pricing_opportunity',
                'title': 'Optimal Price Range Found',
                'message': f'Items priced ${attrs.get("min_price", 0)}-${attrs.get("max_price", 100)} perform {best_pricing.success_rate:.0f}% better.',
                'priority': 'medium',
                'action_items': [
                    'Adjust new listings to this range',
                    'Test price changes on existing items'
                ],
            }

        return None

    def _recommend_platforms(self) -> Optional[Dict]:
        """Recommend platforms based on success patterns."""
        from .models_unified_system import SuccessPattern

        query = Q(pattern_type='platform_match', is_active=True)
        if self.user:
            query &= (Q(user=self.user) | Q(is_global=True))

        best_platform = SuccessPattern.objects.filter(query).order_by('-success_rate').first()

        if best_platform and best_platform.avg_revenue_per_success > 0:
            attrs = best_platform.pattern_attributes or {}
            return {
                'type': 'platform_recommendation',
                'title': f'Focus on {attrs.get("platform", "Top Platform")}',
                'message': f'You earn ${best_platform.avg_revenue_per_success:.2f} avg on this platform.',
                'priority': 'medium',
                'action_items': [
                    'Prioritize new uploads here',
                    'Optimize existing listings'
                ],
            }

        return None

    def _suggest_timing(self) -> Optional[Dict]:
        """Suggest optimal upload timing."""
        from .models_unified_system import SuccessPattern

        query = Q(pattern_type='timing', is_active=True)
        if self.user:
            query &= (Q(user=self.user) | Q(is_global=True))

        best_timing = SuccessPattern.objects.filter(query).order_by('-success_rate').first()

        if best_timing:
            attrs = best_timing.pattern_attributes or {}
            if 'best_day' in attrs:
                return {
                    'type': 'timing_suggestion',
                    'title': f'Best Upload Day: {attrs["best_day"]}',
                    'message': f'Content uploaded on {attrs["best_day"]} performs {best_timing.success_rate:.0f}% better.',
                    'priority': 'low',
                    'action_items': [
                        f'Schedule uploads for {attrs["best_day"]}',
                        'Use the scheduling feature'
                    ],
                }

        return None

    def _optimize_tags(self) -> Optional[Dict]:
        """Suggest tag optimizations."""
        from .models_unified_system import SuccessPattern

        query = Q(pattern_type='tag_combination', is_active=True)
        if self.user:
            query &= (Q(user=self.user) | Q(is_global=True))

        top_tags = SuccessPattern.objects.filter(query).order_by('-success_rate')[:3]

        if top_tags:
            tags = [p.pattern_attributes.get('tag', '') for p in top_tags if p.pattern_attributes]
            tags = [t for t in tags if t]
            if tags:
                return {
                    'type': 'tag_optimization',
                    'title': 'Top Performing Tags',
                    'message': f'Tags that work well: {", ".join(tags)}',
                    'priority': 'low',
                    'action_items': [
                        'Include these tags in new content',
                        'Update existing listings'
                    ],
                }

        return None

    def _celebrate_success(self) -> Optional[Dict]:
        """Celebrate user achievements."""
        from .models_unified_system import DistributionAnalytics

        query = Q()
        if self.user:
            query &= Q(distribution__user=self.user)

        total_revenue = DistributionAnalytics.objects.filter(query).aggregate(
            total=Sum('revenue_generated')
        )['total'] or 0

        total_sales = DistributionAnalytics.objects.filter(query).aggregate(
            total=Sum('sales')
        )['total'] or 0

        milestones = [
            (10000, 'You\'ve earned over $10,000! Amazing!'),
            (5000, 'You\'ve crossed the $5,000 mark!'),
            (1000, 'You\'ve earned over $1,000!'),
            (500, 'You\'ve made your first $500!'),
            (100, 'You\'ve earned your first $100!'),
        ]

        for amount, message in milestones:
            if total_revenue >= amount:
                return {
                    'type': 'success_celebration',
                    'title': 'Milestone Reached!',
                    'message': f'{message} Total: ${total_revenue:.2f} from {total_sales} sales.',
                    'priority': 'high',
                    'action_items': ['Keep up the great work!', 'Share your success'],
                }

        return None

    def save_insights(self, insights: List[Dict]) -> int:
        """Save generated insights to database."""
        from .models_unified_system import DistributionInsight

        saved = 0
        for i in insights:
            # Check if similar insight exists recently
            recent = timezone.now() - timedelta(days=1)
            exists = DistributionInsight.objects.filter(
                user=self.user,
                insight_type=i['type'],
                title=i['title'],
                created_at__gte=recent
            ).exists()

            if not exists:
                DistributionInsight.objects.create(
                    user=self.user,
                    insight_type=i['type'],
                    title=i['title'],
                    message=i['message'],
                    priority=i.get('priority', 'medium'),
                    action_items=i.get('action_items', []),
                )
                saved += 1

        return saved


class RealTimeLearner:
    """
    Learns from user actions in real-time.
    Updates patterns and preferences as user interacts.
    """

    def __init__(self, user=None):
        self.user = user

    def record_distribution(self, distribution_data: Dict) -> None:
        """Record a new distribution for learning."""
        # Update user learning profile
        self._update_profile('distribution_count', 1)
        self._update_content_preferences(distribution_data.get('content_type'))
        self._update_platform_preferences(distribution_data.get('platform'))
        self._update_pricing_preferences(distribution_data.get('price'))

    def record_sale(self, sale_data: Dict) -> None:
        """Record a sale for pattern learning."""

        # Update success patterns
        content_type = sale_data.get('content_type')
        platform = sale_data.get('platform')
        price = sale_data.get('price', 0)
        tags = sale_data.get('tags', [])

        # Increment pattern sample sizes and update success rates
        if content_type:
            self._reinforce_pattern('content_style', {'content_type': content_type})

        if platform:
            self._reinforce_pattern('platform_match', {'platform': platform})

        if price:
            price_range = self._get_price_range(price)
            self._reinforce_pattern('pricing_strategy', price_range)

        for tag in tags[:5]:
            self._reinforce_pattern('tag_combination', {'tag': tag.lower().strip()})

    def record_view(self, view_data: Dict) -> None:
        """Record content view for engagement tracking."""
        self._update_profile('total_views', 1)

    def _update_profile(self, field: str, increment: int) -> None:
        """Update user learning profile."""
        from .models_unified_system import UserLearningProfile

        if not self.user:
            return

        profile, _ = UserLearningProfile.objects.get_or_create(user=self.user)

        if hasattr(profile, field):
            current = getattr(profile, field) or 0
            setattr(profile, field, current + increment)
            profile.save()

    def _update_content_preferences(self, content_type: str) -> None:
        """Update content type preferences."""
        from .models_unified_system import UserLearningProfile

        if not self.user or not content_type:
            return

        profile, _ = UserLearningProfile.objects.get_or_create(user=self.user)
        prefs = profile.content_preferences or {}
        prefs[content_type] = prefs.get(content_type, 0) + 1
        profile.content_preferences = prefs
        profile.save()

    def _update_platform_preferences(self, platform: str) -> None:
        """Update platform preferences."""
        from .models_unified_system import UserLearningProfile

        if not self.user or not platform:
            return

        profile, _ = UserLearningProfile.objects.get_or_create(user=self.user)
        prefs = profile.platform_preferences or {}
        prefs[platform] = prefs.get(platform, 0) + 1
        profile.platform_preferences = prefs
        profile.save()

    def _update_pricing_preferences(self, price: float) -> None:
        """Update pricing preferences."""
        from .models_unified_system import UserLearningProfile

        if not self.user or not price:
            return

        profile, _ = UserLearningProfile.objects.get_or_create(user=self.user)
        price_range = self._get_price_range_label(price)
        prefs = profile.pricing_preferences or {}
        prefs[price_range] = prefs.get(price_range, 0) + 1
        profile.pricing_preferences = prefs
        profile.save()

    def _reinforce_pattern(self, pattern_type: str, attributes: Dict) -> None:
        """Reinforce a success pattern after a sale."""
        from .models_unified_system import SuccessPattern

        if not self.user:
            return

        patterns = SuccessPattern.objects.filter(
            user=self.user,
            pattern_type=pattern_type,
            is_active=True
        )

        for pattern in patterns:
            pattern_attrs = pattern.pattern_attributes or {}
            if all(pattern_attrs.get(k) == v for k, v in attributes.items()):
                pattern.sample_size += 1
                pattern.success_rate = min(100, pattern.success_rate + Decimal('0.5'))
                pattern.confidence_score = min(100, pattern.confidence_score + Decimal('0.25'))
                pattern.save()
                return

    def _get_price_range(self, price: float) -> Dict:
        """Get price range attributes for a price."""
        if price < 10:
            return {'min_price': 0, 'max_price': 10}
        elif price < 25:
            return {'min_price': 10, 'max_price': 25}
        elif price < 50:
            return {'min_price': 25, 'max_price': 50}
        elif price < 100:
            return {'min_price': 50, 'max_price': 100}
        else:
            return {'min_price': 100, 'max_price': 10000}

    def _get_price_range_label(self, price: float) -> str:
        """Get price range label for a price."""
        if price < 10:
            return 'budget'
        elif price < 25:
            return 'mid-range'
        elif price < 50:
            return 'premium'
        elif price < 100:
            return 'high-end'
        else:
            return 'luxury'
