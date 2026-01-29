"""
Session 861: Spider Aggregation Caching System

Provides database caching for expensive spider aggregation computations.
This addresses the MEDIUM RISK data persistence gap where:
- Same expensive aggregations were re-computed repeatedly
- Slow response times for dashboards
- No historical aggregation comparisons

The caching layer stores pre-computed aggregations at various levels:
- Category-level summaries
- Cross-spider trends
- Opportunity aggregations
- Relevance distributions

Pre-computation is done via Celery Beat scheduled tasks.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class SpiderAggregation(models.Model):
    """
    Cached aggregation results for spider data.

    Unlike SpiderAnalytics (per-spider daily metrics), this model stores
    higher-level aggregations that span multiple spiders and time periods.

    Example:
        SpiderAggregation.objects.create(
            aggregation_type='category_summary',
            category='financial',
            date_range_start=today - timedelta(days=7),
            date_range_end=today,
            aggregation_data={
                'total_items': 1523,
                'avg_relevance': 72.5,
                'top_topics': ['crypto', 'stocks', 'earnings'],
                'spider_contributions': {'yahoo_finance': 450, 'coingecko': 380, ...}
            }
        )
    """

    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Aggregation type
    AGGREGATION_TYPES = [
        ('category_summary', 'Category Summary'),
        ('cross_spider_trend', 'Cross-Spider Trend'),
        ('opportunity_summary', 'Opportunity Summary'),
        ('relevance_distribution', 'Relevance Distribution'),
        ('topic_analysis', 'Topic Analysis'),
        ('hourly_activity', 'Hourly Activity'),
        ('daily_summary', 'Daily Summary'),
        ('weekly_summary', 'Weekly Summary'),
    ]
    aggregation_type = models.CharField(
        max_length=50, choices=AGGREGATION_TYPES, db_index=True,
        help_text="Type of aggregation"
    )

    # Scope
    category = models.CharField(
        max_length=100, blank=True, db_index=True,
        help_text="Spider category (financial, tech, news, etc.)"
    )
    spider_name = models.CharField(
        max_length=100, blank=True, db_index=True,
        help_text="Specific spider name (if single-spider aggregation)"
    )

    # Time range
    date_range_start = models.DateTimeField(
        db_index=True,
        help_text="Start of the aggregation period"
    )
    date_range_end = models.DateTimeField(
        db_index=True,
        help_text="End of the aggregation period"
    )

    # Aggregated data
    aggregation_data = models.JSONField(
        default=dict,
        help_text="The computed aggregation data"
    )

    # Metadata
    items_analyzed = models.IntegerField(
        default=0,
        help_text="Number of SpiderData items included in aggregation"
    )
    computation_time_ms = models.IntegerField(
        default=0,
        help_text="Time taken to compute this aggregation"
    )

    # Timestamps
    computed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    expires_at = models.DateTimeField(
        null=True, blank=True, db_index=True,
        help_text="When this cached aggregation should be recomputed"
    )

    class Meta:
        db_table = 'core_spider_aggregation'
        ordering = ['-computed_at']
        indexes = [
            models.Index(fields=['aggregation_type', 'category', 'computed_at']),
            models.Index(fields=['aggregation_type', 'date_range_start']),
            models.Index(fields=['expires_at']),
        ]
        # Allow duplicate aggregation types for different time ranges
        unique_together = ['aggregation_type', 'category', 'spider_name', 'date_range_start', 'date_range_end']

    def __str__(self):
        scope = self.category or self.spider_name or 'all'
        return f"{self.aggregation_type} ({scope}): {self.date_range_start.date()} to {self.date_range_end.date()}"

    @property
    def is_expired(self) -> bool:
        """Check if this aggregation has expired and needs recomputation."""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    @classmethod
    def get_cached_or_compute(
        cls,
        aggregation_type: str,
        category: str = '',
        spider_name: str = '',
        date_range_start=None,
        date_range_end=None,
        compute_fn=None,
        ttl_hours: int = 1,
    ):
        """
        Get a cached aggregation or compute it if not available.

        Args:
            aggregation_type: Type of aggregation
            category: Spider category filter
            spider_name: Specific spider filter
            date_range_start: Start of time range
            date_range_end: End of time range
            compute_fn: Function to call to compute the aggregation
            ttl_hours: Hours before expiration

        Returns:
            Tuple of (aggregation_data, from_cache)
        """
        now = timezone.now()
        if date_range_end is None:
            date_range_end = now
        if date_range_start is None:
            date_range_start = now - timedelta(days=1)

        # Try to get cached version
        cached = cls.objects.filter(
            aggregation_type=aggregation_type,
            category=category,
            spider_name=spider_name,
            date_range_start=date_range_start,
            date_range_end=date_range_end,
            expires_at__gt=now,
        ).first()

        if cached:
            return cached.aggregation_data, True

        # Compute if no cache or compute_fn provided
        if compute_fn:
            import time
            start_time = time.time()
            data = compute_fn()
            computation_time_ms = int((time.time() - start_time) * 1000)

            # Cache the result
            aggregation = cls.objects.create(
                aggregation_type=aggregation_type,
                category=category,
                spider_name=spider_name,
                date_range_start=date_range_start,
                date_range_end=date_range_end,
                aggregation_data=data,
                computation_time_ms=computation_time_ms,
                expires_at=now + timedelta(hours=ttl_hours),
            )
            return aggregation.aggregation_data, False

        return None, False

    @classmethod
    def invalidate(cls, category: str = None, spider_name: str = None):
        """
        Invalidate cached aggregations for a category or spider.

        Called when new spider data arrives to trigger recomputation.
        """
        qs = cls.objects.all()
        if category:
            qs = qs.filter(category=category)
        if spider_name:
            qs = qs.filter(spider_name=spider_name)
        # Set expires_at to now to mark as expired
        qs.update(expires_at=timezone.now())


class TrendDataPoint(models.Model):
    """
    Time-series data points for spider trends.

    Stores hourly/daily data points for trend visualization
    without needing to recompute from raw SpiderData.
    """

    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Trend identification
    TREND_TYPES = [
        ('item_count', 'Item Count'),
        ('relevance_avg', 'Average Relevance'),
        ('topic_frequency', 'Topic Frequency'),
        ('source_activity', 'Source Activity'),
        ('opportunity_count', 'Opportunity Count'),
    ]
    trend_type = models.CharField(
        max_length=50, choices=TREND_TYPES, db_index=True,
        help_text="Type of trend being tracked"
    )

    # Scope
    category = models.CharField(
        max_length=100, blank=True, db_index=True,
        help_text="Spider category"
    )
    spider_name = models.CharField(
        max_length=100, blank=True, db_index=True,
        help_text="Specific spider"
    )
    topic = models.CharField(
        max_length=100, blank=True, db_index=True,
        help_text="Specific topic (for topic_frequency trends)"
    )

    # Time granularity
    GRANULARITIES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]
    granularity = models.CharField(
        max_length=20, choices=GRANULARITIES, db_index=True,
        help_text="Time granularity of this data point"
    )

    # Data point
    timestamp = models.DateTimeField(db_index=True, help_text="Time bucket")
    value = models.FloatField(help_text="The trend value")
    metadata = models.JSONField(
        default=dict,
        help_text="Additional context for this data point"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_trend_data_point'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['trend_type', 'granularity', 'timestamp']),
            models.Index(fields=['category', 'trend_type', 'timestamp']),
            models.Index(fields=['spider_name', 'trend_type', 'timestamp']),
        ]
        unique_together = ['trend_type', 'category', 'spider_name', 'topic', 'granularity', 'timestamp']

    def __str__(self):
        scope = self.category or self.spider_name or self.topic or 'all'
        return f"{self.trend_type} ({scope}): {self.value} @ {self.timestamp}"


# Helper functions for pre-computation via Celery tasks

def compute_category_summary(category: str, hours: int = 24) -> dict:
    """
    Compute summary statistics for a spider category.

    Returns:
        Dict with total_items, avg_relevance, top_topics, spider_contributions
    """
    from core.models_unified_system import SpiderData, SpiderCategory
    from django.db.models import Avg, Count

    now = timezone.now()
    start = now - timedelta(hours=hours)

    # Get spiders in this category
    spider_cat = SpiderCategory.objects.filter(name__iexact=category).first()
    if not spider_cat:
        return {'error': f'Category {category} not found'}

    spider_names = list(spider_cat.spiders.values_list('name', flat=True))

    # Query SpiderData
    qs = SpiderData.objects.filter(
        spider_name__in=spider_names,
        created_at__gte=start,
    )

    # Aggregate
    total_items = qs.count()
    avg_relevance = qs.aggregate(avg=Avg('relevance_score'))['avg'] or 0

    # Spider contributions
    contributions = dict(qs.values('spider_name').annotate(count=Count('id')).values_list('spider_name', 'count'))

    # Top topics (from insights)
    topics = {}
    for item in qs.only('insights')[:500]:
        for insight in (item.insights or []):
            topic = insight.get('topic', '')
            if topic:
                topics[topic] = topics.get(topic, 0) + 1
    top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        'total_items': total_items,
        'avg_relevance': round(avg_relevance, 2),
        'top_topics': [t[0] for t in top_topics],
        'spider_contributions': contributions,
        'time_range_hours': hours,
    }


def compute_daily_summary() -> dict:
    """
    Compute platform-wide daily summary.

    Returns:
        Dict with overall stats across all spiders.
    """
    from core.models_unified_system import SpiderData, SpiderCategory
    from django.db.models import Avg, Count

    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    qs = SpiderData.objects.filter(created_at__gte=today_start)

    total_items = qs.count()
    avg_relevance = qs.aggregate(avg=Avg('relevance_score'))['avg'] or 0
    actionable = qs.filter(is_actionable=True).count()
    processed = qs.filter(is_processed=True).count()

    # Per-category breakdown
    categories = {}
    for cat in SpiderCategory.objects.all():
        spider_names = list(cat.spiders.values_list('name', flat=True))
        cat_count = qs.filter(spider_name__in=spider_names).count()
        if cat_count > 0:
            categories[cat.name] = cat_count

    return {
        'date': now.date().isoformat(),
        'total_items': total_items,
        'avg_relevance': round(avg_relevance, 2),
        'actionable_items': actionable,
        'processed_items': processed,
        'categories': categories,
    }


def record_trend_data_point(
    trend_type: str,
    value: float,
    category: str = '',
    spider_name: str = '',
    topic: str = '',
    granularity: str = 'hourly',
    metadata: dict = None,
):
    """
    Record a trend data point.

    Called by Celery tasks to build time-series data.
    """
    now = timezone.now()

    # Round timestamp to granularity
    if granularity == 'hourly':
        timestamp = now.replace(minute=0, second=0, microsecond=0)
    elif granularity == 'daily':
        timestamp = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif granularity == 'weekly':
        # Start of week (Monday)
        timestamp = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        timestamp = now

    TrendDataPoint.objects.update_or_create(
        trend_type=trend_type,
        category=category,
        spider_name=spider_name,
        topic=topic,
        granularity=granularity,
        timestamp=timestamp,
        defaults={
            'value': value,
            'metadata': metadata or {},
        }
    )
