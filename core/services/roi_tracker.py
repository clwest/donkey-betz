"""
ROI Tracker Service - Phase 6 Market Intelligence Architecture

Tracks ROI metrics, conversion events, attribution paths, and generates
weekly intelligence briefs.

Session 472: December 17, 2025
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from django.db import transaction
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone

logger = logging.getLogger(__name__)


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ConversionResult:
    """Result of recording a conversion event."""
    event_id: str
    event_type: str
    value: Optional[Decimal]
    success: bool
    attribution_source: Optional[str] = None
    path_length: int = 1
    error: Optional[str] = None


@dataclass
class ROISummary:
    """Summary of ROI metrics."""
    period: str
    total_revenue: Decimal
    total_cost: Decimal
    roi_percentage: Optional[Decimal]
    conversions: int
    views: int
    clicks: int
    conversion_rate: Optional[Decimal]
    ctr: Optional[Decimal]
    top_sources: List[Dict]


@dataclass
class AttributionResult:
    """Result of attribution calculation."""
    path_id: str
    model: str
    credits: Dict[str, Decimal]
    primary_source: str
    primary_credit: Decimal
    success: bool
    error: Optional[str] = None


# ============================================================================
# ROI Tracker Class
# ============================================================================

class ROITracker:
    """
    Tracks ROI metrics, conversion events, and attribution paths.

    Provides:
    - Conversion funnel tracking (view → click → apply → convert → revenue)
    - Multi-touch attribution (first, last, linear, time-decay, position-based)
    - ROI metric aggregation by period and dimension
    - Weekly intelligence brief generation
    """

    # Event type ordering for funnel tracking
    EVENT_FUNNEL = [
        'view', 'click', 'apply', 'submit',
        'interview', 'offer', 'convert', 'revenue'
    ]

    # Attribution model implementations
    ATTRIBUTION_MODELS = [
        'first_touch', 'last_touch', 'linear',
        'time_decay', 'position_based', 'data_driven'
    ]

    def __init__(self):
        """Initialize ROI tracker."""
        self._model_cache = {}
        logger.info("ROITracker initialized")

    # ========================================================================
    # Conversion Event Tracking
    # ========================================================================

    def record_conversion_event(
        self,
        event_type: str,
        opportunity_id: Optional[str] = None,
        spider_data_id: Optional[str] = None,
        user_id: Optional[int] = None,
        value: Optional[Decimal] = None,
        currency: str = 'USD',
        session_id: Optional[str] = None,
        attribution_source: Optional[str] = None,
        attribution_medium: Optional[str] = None,
        attribution_campaign: Optional[str] = None,
        metadata: Optional[Dict] = None,
        previous_event_id: Optional[str] = None
    ) -> ConversionResult:
        """
        Record a conversion event in the funnel.

        Args:
            event_type: Type of event (view, click, apply, etc.)
            opportunity_id: Related opportunity UUID
            spider_data_id: Original spider data UUID
            user_id: User who triggered the event
            value: Monetary value if applicable
            currency: Currency code (default USD)
            session_id: Browser/app session ID
            attribution_source: Source attribution (spider name, campaign)
            attribution_medium: Medium (organic, paid, email)
            attribution_campaign: Campaign identifier
            metadata: Additional event metadata
            previous_event_id: Previous event in conversion path

        Returns:
            ConversionResult with event details
        """
        try:
            from core.models_unified_system import (
                ConversionEvent, Opportunity, LegacySpiderData
            )
            from django.contrib.auth import get_user_model
            User = get_user_model()

            # Validate event type
            event_type_field = ConversionEvent._meta.get_field('event_type')
            valid_types = [c[0] for c in event_type_field.choices]
            if event_type not in valid_types:
                return ConversionResult(
                    event_id='',
                    event_type=event_type,
                    value=value,
                    success=False,
                    error=f"Invalid event type: {event_type}"
                )

            # Get related objects
            opportunity = None
            spider_data = None
            user = None
            previous_event = None

            if opportunity_id:
                try:
                    opportunity = Opportunity.objects.get(id=opportunity_id)
                except Opportunity.DoesNotExist:
                    logger.warning(f"Opportunity not found: {opportunity_id}")

            if spider_data_id:
                try:
                    spider_data = LegacySpiderData.objects.get(id=spider_data_id)
                except LegacySpiderData.DoesNotExist:
                    logger.warning(f"LegacySpiderData not found: {spider_data_id}")

            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    logger.warning(f"User not found: {user_id}")

            if previous_event_id:
                try:
                    previous_event = ConversionEvent.objects.get(id=previous_event_id)
                except ConversionEvent.DoesNotExist:
                    logger.warning(f"Previous event not found: {previous_event_id}")

            # Auto-detect attribution source from spider data
            if not attribution_source and spider_data:
                attribution_source = spider_data.source_url

            if not attribution_source and opportunity:
                # Try to get from opportunity's first spider data
                first_spider = opportunity.spider_data.first()
                if first_spider:
                    attribution_source = first_spider.source_url

            # Create the conversion event
            with transaction.atomic():
                event = ConversionEvent.objects.create(
                    event_type=event_type,
                    opportunity=opportunity,
                    spider_data=spider_data,
                    user=user,
                    session_id=session_id or '',
                    value=value,
                    currency=currency,
                    attribution_source=attribution_source or '',
                    attribution_medium=attribution_medium or '',
                    attribution_campaign=attribution_campaign or '',
                    metadata=metadata or {},
                    previous_event=previous_event
                )

                # Calculate path length
                path_length = 1
                current = previous_event
                while current:
                    path_length += 1
                    current = current.previous_event

                logger.info(f"Recorded {event_type} event: {event.id} (path length: {path_length})")

                # If this is a revenue event, create attribution path
                if event_type == 'revenue' and value:
                    self._create_attribution_path(event)

                return ConversionResult(
                    event_id=str(event.id),
                    event_type=event_type,
                    value=value,
                    success=True,
                    attribution_source=attribution_source,
                    path_length=path_length
                )

        except Exception as e:
            logger.error(f"Error recording conversion event: {e}")
            return ConversionResult(
                event_id='',
                event_type=event_type,
                value=value,
                success=False,
                error=str(e)
            )

    def get_conversion_path(
        self,
        event_id: str,
        include_metadata: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get the full conversion path leading to an event.

        Args:
            event_id: UUID of the target event
            include_metadata: Include event metadata in results

        Returns:
            List of events in chronological order
        """
        try:
            from core.models_unified_system import ConversionEvent

            event = ConversionEvent.objects.get(id=event_id)

            # Build path backwards
            path = []
            current = event
            while current:
                event_data = {
                    'id': str(current.id),
                    'event_type': current.event_type,
                    'event_type_display': current.get_event_type_display(),
                    'value': str(current.value) if current.value else None,
                    'attribution_source': current.attribution_source,
                    'timestamp': current.event_timestamp.isoformat()
                }
                if include_metadata:
                    event_data['metadata'] = current.metadata
                path.append(event_data)
                current = current.previous_event

            # Reverse to chronological order
            path.reverse()
            return path

        except Exception as e:
            logger.error(f"Error getting conversion path: {e}")
            return []

    def get_funnel_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get funnel metrics showing conversion rates between stages.

        Args:
            start_date: Filter events after this date
            end_date: Filter events before this date
            source: Filter by attribution source

        Returns:
            Dict with funnel metrics
        """
        try:
            from core.models_unified_system import ConversionEvent

            # Build query
            filters = Q()
            if start_date:
                filters &= Q(event_timestamp__gte=start_date)
            if end_date:
                filters &= Q(event_timestamp__lte=end_date)
            if source:
                filters &= Q(attribution_source=source)

            # Count events by type
            events = ConversionEvent.objects.filter(filters)
            counts = events.values('event_type').annotate(
                count=Count('id')
            ).order_by('event_type')

            # Build funnel
            count_map = {item['event_type']: item['count'] for item in counts}

            funnel = []
            prev_count = None
            for event_type in self.EVENT_FUNNEL:
                count = count_map.get(event_type, 0)

                stage = {
                    'stage': event_type,
                    'count': count,
                    'conversion_rate': None,
                    'drop_off': None
                }

                if prev_count is not None and prev_count > 0:
                    stage['conversion_rate'] = round(count / prev_count * 100, 2)
                    stage['drop_off'] = prev_count - count

                funnel.append(stage)
                prev_count = count

            # Calculate overall conversion
            total_views = count_map.get('view', 0)
            total_revenue = count_map.get('revenue', 0)
            overall_rate = None
            if total_views > 0:
                overall_rate = round(total_revenue / total_views * 100, 4)

            return {
                'funnel': funnel,
                'total_events': sum(count_map.values()),
                'overall_conversion_rate': overall_rate,
                'period': {
                    'start': start_date.isoformat() if start_date else None,
                    'end': end_date.isoformat() if end_date else None
                }
            }

        except Exception as e:
            logger.error(f"Error getting funnel metrics: {e}")
            return {'funnel': [], 'error': str(e)}

    # ========================================================================
    # Attribution
    # ========================================================================

    def _create_attribution_path(
        self,
        revenue_event: Any,
        model: str = 'last_touch'
    ) -> AttributionResult:
        """
        Create attribution path for a revenue event.

        Args:
            revenue_event: The revenue ConversionEvent
            model: Attribution model to use

        Returns:
            AttributionResult with attribution details
        """
        try:
            from core.models_unified_system import AttributionPath

            # Get full path
            path_data = self.get_conversion_path(str(revenue_event.id))
            if not path_data:
                return AttributionResult(
                    path_id='',
                    model=model,
                    credits={},
                    primary_source='',
                    primary_credit=Decimal('0'),
                    success=False,
                    error="No path data found"
                )

            # Extract unique sources from path
            sources = []
            for event in path_data:
                source = event.get('attribution_source')
                if source and source not in sources:
                    sources.append(source)

            if not sources:
                sources = ['unknown']

            # Calculate credits based on model
            credits = self._calculate_attribution_credits(sources, model)

            # Get primary source (highest credit)
            primary_source = max(credits.keys(), key=lambda k: credits[k])
            primary_credit = credits[primary_source]

            # Calculate time to conversion
            first_ts = datetime.fromisoformat(path_data[0]['timestamp'].replace('Z', '+00:00'))
            last_ts = datetime.fromisoformat(path_data[-1]['timestamp'].replace('Z', '+00:00'))
            hours = (last_ts - first_ts).total_seconds() / 3600

            # Create attribution path record
            with transaction.atomic():
                path = AttributionPath.objects.create(
                    conversion_event=revenue_event,
                    attribution_model=model,
                    path_data=path_data,
                    path_length=len(path_data),
                    time_to_conversion_hours=Decimal(str(round(hours, 2))),
                    attribution_credits=credits,
                    primary_source=primary_source,
                    primary_source_credit=primary_credit,
                    attributed_value=revenue_event.value
                )

                logger.info(f"Created attribution path: {path.id} ({model})")

                return AttributionResult(
                    path_id=str(path.id),
                    model=model,
                    credits=credits,
                    primary_source=primary_source,
                    primary_credit=primary_credit,
                    success=True
                )

        except Exception as e:
            logger.error(f"Error creating attribution path: {e}")
            return AttributionResult(
                path_id='',
                model=model,
                credits={},
                primary_source='',
                primary_credit=Decimal('0'),
                success=False,
                error=str(e)
            )

    def _calculate_attribution_credits(
        self,
        sources: List[str],
        model: str
    ) -> Dict[str, Decimal]:
        """
        Calculate attribution credits based on model.

        Args:
            sources: List of sources in order of touchpoints
            model: Attribution model to use

        Returns:
            Dict mapping source to credit (0-1)
        """
        n = len(sources)
        if n == 0:
            return {}

        credits = {}

        if model == 'first_touch':
            # All credit to first touchpoint
            credits[sources[0]] = Decimal('1.0')
            for source in sources[1:]:
                if source not in credits:
                    credits[source] = Decimal('0.0')

        elif model == 'last_touch':
            # All credit to last touchpoint
            for source in sources[:-1]:
                if source not in credits:
                    credits[source] = Decimal('0.0')
            credits[sources[-1]] = Decimal('1.0')

        elif model == 'linear':
            # Equal credit to all touchpoints
            credit_per = Decimal('1.0') / Decimal(str(n))
            for source in sources:
                if source not in credits:
                    credits[source] = Decimal('0.0')
                credits[source] += credit_per

        elif model == 'time_decay':
            # More credit to recent touchpoints (decay factor 0.5)
            total_weight = Decimal('0')
            weights = []
            for i in range(n):
                weight = Decimal('2') ** Decimal(str(i))
                weights.append(weight)
                total_weight += weight

            for i, source in enumerate(sources):
                if source not in credits:
                    credits[source] = Decimal('0.0')
                credits[source] += weights[i] / total_weight

        elif model == 'position_based':
            # 40% first, 40% last, 20% split among middle
            if n == 1:
                credits[sources[0]] = Decimal('1.0')
            elif n == 2:
                credits[sources[0]] = Decimal('0.5')
                credits[sources[1]] = Decimal('0.5')
            else:
                middle_credit = Decimal('0.2') / Decimal(str(n - 2))
                credits[sources[0]] = Decimal('0.4')
                for source in sources[1:-1]:
                    if source not in credits:
                        credits[source] = Decimal('0.0')
                    credits[source] += middle_credit
                if sources[-1] not in credits:
                    credits[sources[-1]] = Decimal('0.0')
                credits[sources[-1]] += Decimal('0.4')

        else:  # data_driven - default to linear
            credit_per = Decimal('1.0') / Decimal(str(n))
            for source in sources:
                if source not in credits:
                    credits[source] = Decimal('0.0')
                credits[source] += credit_per

        # Round credits
        return {k: round(v, 4) for k, v in credits.items()}

    def get_attribution_by_source(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        model: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get attribution summary grouped by source.

        Args:
            start_date: Filter after this date
            end_date: Filter before this date
            model: Filter by attribution model

        Returns:
            List of source attribution summaries
        """
        try:
            from core.models_unified_system import AttributionPath

            filters = Q()
            if start_date:
                filters &= Q(created_at__gte=start_date)
            if end_date:
                filters &= Q(created_at__lte=end_date)
            if model:
                filters &= Q(attribution_model=model)

            paths = AttributionPath.objects.filter(filters)

            # Aggregate by primary source
            results = paths.values('primary_source').annotate(
                total_attributed=Sum('attributed_value'),
                path_count=Count('id'),
                avg_path_length=Avg('path_length'),
                avg_time_to_conversion=Avg('time_to_conversion_hours'),
                avg_credit=Avg('primary_source_credit')
            ).order_by('-total_attributed')

            return [
                {
                    'source': r['primary_source'],
                    'total_revenue': str(r['total_attributed'] or 0),
                    'conversions': r['path_count'],
                    'avg_path_length': round(r['avg_path_length'] or 0, 1),
                    'avg_hours_to_convert': round(r['avg_time_to_conversion'] or 0, 1),
                    'avg_credit': round(float(r['avg_credit'] or 0), 3)
                }
                for r in results
            ]

        except Exception as e:
            logger.error(f"Error getting attribution by source: {e}")
            return []

    # ========================================================================
    # ROI Metrics Aggregation
    # ========================================================================

    def aggregate_roi_metrics(
        self,
        period_type: str = 'daily',
        dimension: str = 'overall',
        target_date: Optional[datetime] = None
    ) -> bool:
        """
        Aggregate ROI metrics for a given period.

        Args:
            period_type: hourly, daily, weekly, monthly, quarterly, yearly
            dimension: overall, spider_source, opportunity_category, user_segment, agent, campaign
            target_date: Date to aggregate (defaults to now)

        Returns:
            True if successful
        """
        try:
            from core.models_unified_system import (
                ConversionEvent
            )

            if target_date is None:
                target_date = timezone.now()

            # Calculate period boundaries
            period_start, period_end = self._get_period_boundaries(
                period_type, target_date
            )

            # Get events in period
            events = ConversionEvent.objects.filter(
                event_timestamp__gte=period_start,
                event_timestamp__lt=period_end
            )

            if dimension == 'overall':
                # Single aggregation for entire period
                self._aggregate_dimension(
                    events=events,
                    period_type=period_type,
                    period_start=period_start,
                    period_end=period_end,
                    dimension='overall',
                    dimension_value='platform'
                )
            elif dimension == 'spider_source':
                # Group by attribution source
                sources = events.values_list(
                    'attribution_source', flat=True
                ).distinct()
                for source in sources:
                    if source:
                        self._aggregate_dimension(
                            events=events.filter(attribution_source=source),
                            period_type=period_type,
                            period_start=period_start,
                            period_end=period_end,
                            dimension='spider_source',
                            dimension_value=source
                        )
            # Additional dimensions can be added here

            logger.info(
                f"Aggregated {period_type} ROI metrics for {dimension} "
                f"({period_start.date()} to {period_end.date()})"
            )
            return True

        except Exception as e:
            logger.error(f"Error aggregating ROI metrics: {e}")
            return False

    def _aggregate_dimension(
        self,
        events,
        period_type: str,
        period_start: datetime,
        period_end: datetime,
        dimension: str,
        dimension_value: str
    ) -> None:
        """Aggregate metrics for a specific dimension."""
        from core.models_unified_system import ROIMetric

        # Count events by type
        views = events.filter(event_type='view').count()
        clicks = events.filter(event_type='click').count()
        applications = events.filter(
            event_type__in=['apply', 'submit']
        ).count()
        conversions = events.filter(event_type='convert').count()

        # Sum revenue
        revenue_events = events.filter(event_type='revenue')
        total_revenue = revenue_events.aggregate(
            total=Sum('value')
        )['total'] or Decimal('0')

        # Count unique users and opportunities
        unique_users = events.values('user').distinct().count()
        unique_opportunities = events.values('opportunity').distinct().count()

        # Calculate derived metrics
        ctr = None
        if views > 0:
            ctr = Decimal(str(clicks / views))

        conversion_rate = None
        if applications > 0:
            conversion_rate = Decimal(str(conversions / applications))

        # For now, assume cost is 0 (can be tracked separately)
        total_cost = Decimal('0')
        roi = None
        cpa = None
        arpu = None

        if total_cost > 0:
            roi = (total_revenue - total_cost) / total_cost

        if conversions > 0 and total_cost > 0:
            cpa = total_cost / Decimal(str(conversions))

        if unique_users > 0:
            arpu = total_revenue / Decimal(str(unique_users))

        # Create or update metric
        with transaction.atomic():
            metric, created = ROIMetric.objects.update_or_create(
                period_type=period_type,
                period_start=period_start,
                dimension=dimension,
                dimension_value=dimension_value,
                defaults={
                    'period_end': period_end,
                    'views': views,
                    'clicks': clicks,
                    'applications': applications,
                    'conversions': conversions,
                    'total_revenue': total_revenue,
                    'total_cost': total_cost,
                    'click_through_rate': ctr,
                    'conversion_rate': conversion_rate,
                    'cost_per_acquisition': cpa,
                    'return_on_investment': roi,
                    'average_revenue_per_user': arpu,
                    'unique_users': unique_users,
                    'unique_opportunities': unique_opportunities
                }
            )

    def _get_period_boundaries(
        self,
        period_type: str,
        target_date: datetime
    ) -> tuple:
        """Get start and end boundaries for a period."""
        if period_type == 'hourly':
            start = target_date.replace(minute=0, second=0, microsecond=0)
            end = start + timedelta(hours=1)
        elif period_type == 'daily':
            start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif period_type == 'weekly':
            start = target_date - timedelta(days=target_date.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)
        elif period_type == 'monthly':
            start = target_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if target_date.month == 12:
                end = start.replace(year=start.year + 1, month=1)
            else:
                end = start.replace(month=start.month + 1)
        elif period_type == 'quarterly':
            quarter = (target_date.month - 1) // 3
            start = target_date.replace(
                month=quarter * 3 + 1, day=1,
                hour=0, minute=0, second=0, microsecond=0
            )
            if quarter == 3:
                end = start.replace(year=start.year + 1, month=1)
            else:
                end = start.replace(month=(quarter + 1) * 3 + 1)
        else:  # yearly
            start = target_date.replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0
            )
            end = start.replace(year=start.year + 1)

        return start, end

    def get_roi_summary(
        self,
        period_type: str = 'daily',
        dimension: str = 'overall',
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get ROI summary for recent periods.

        Args:
            period_type: hourly, daily, weekly, monthly
            dimension: overall, spider_source, etc.
            limit: Number of periods to return

        Returns:
            List of ROI summaries
        """
        try:
            from core.models_unified_system import ROIMetric

            metrics = ROIMetric.objects.filter(
                period_type=period_type,
                dimension=dimension
            ).order_by('-period_start')[:limit]

            return [
                {
                    'period_start': m.period_start.isoformat(),
                    'period_end': m.period_end.isoformat(),
                    'dimension_value': m.dimension_value,
                    'views': m.views,
                    'clicks': m.clicks,
                    'conversions': m.conversions,
                    'total_revenue': str(m.total_revenue),
                    'ctr': str(m.click_through_rate) if m.click_through_rate else None,
                    'conversion_rate': str(m.conversion_rate) if m.conversion_rate else None,
                    'roi': str(m.return_on_investment) if m.return_on_investment else None,
                    'unique_users': m.unique_users
                }
                for m in metrics
            ]

        except Exception as e:
            logger.error(f"Error getting ROI summary: {e}")
            return []

    # ========================================================================
    # Weekly Intelligence Brief
    # ========================================================================

    def generate_weekly_brief(
        self,
        week_start: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate weekly intelligence brief.

        Args:
            week_start: Start of week (defaults to most recent Monday)

        Returns:
            Dict with brief data
        """
        try:
            from core.models_unified_system import (
                WeeklyIntelligenceBrief, ConversionEvent
            )

            # Calculate week boundaries
            if week_start is None:
                now = timezone.now()
                week_start = now - timedelta(days=now.weekday())
            week_start = week_start.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            week_end = week_start + timedelta(days=7)

            # Check if brief already exists
            existing = WeeklyIntelligenceBrief.objects.filter(
                week_start=week_start.date()
            ).first()

            if existing and existing.status == 'complete':
                return {
                    'id': str(existing.id),
                    'status': 'exists',
                    'week_start': existing.week_start.isoformat(),
                    'week_end': existing.week_end.isoformat(),
                    'total_revenue': str(existing.total_revenue),
                    'total_conversions': existing.total_conversions,
                    'executive_summary': existing.executive_summary
                }

            # Create or update brief
            brief, _ = WeeklyIntelligenceBrief.objects.update_or_create(
                week_start=week_start.date(),
                defaults={
                    'week_end': week_end.date(),
                    'status': 'generating'
                }
            )

            # Get conversion events for the week
            events = ConversionEvent.objects.filter(
                event_timestamp__gte=week_start,
                event_timestamp__lt=week_end
            )

            # Calculate totals
            revenue_total = events.filter(event_type='revenue').aggregate(
                total=Sum('value')
            )['total'] or Decimal('0')

            conversions = events.filter(event_type='convert').count()

            # Get unique opportunities
            opportunities = events.values('opportunity').distinct().count()

            # Get spider data count (from spider_data relation)
            spider_records = events.values('spider_data').distinct().count()

            # Top spider sources
            top_sources = events.exclude(
                attribution_source=''
            ).values('attribution_source').annotate(
                revenue=Sum('value', filter=Q(event_type='revenue')),
                count=Count('id')
            ).order_by('-revenue')[:10]

            top_spider_sources = [
                {
                    'source': s['attribution_source'],
                    'revenue': str(s['revenue'] or 0),
                    'events': s['count']
                }
                for s in top_sources
            ]

            # Compare to previous week
            prev_week_start = week_start - timedelta(days=7)
            prev_events = ConversionEvent.objects.filter(
                event_timestamp__gte=prev_week_start,
                event_timestamp__lt=week_start
            )

            prev_revenue = prev_events.filter(event_type='revenue').aggregate(
                total=Sum('value')
            )['total'] or Decimal('0')

            prev_conversions = prev_events.filter(event_type='convert').count()

            revenue_change = None
            if prev_revenue > 0:
                revenue_change = (
                    (revenue_total - prev_revenue) / prev_revenue * 100
                )

            conversions_change = None
            if prev_conversions > 0:
                conversions_change = (
                    (conversions - prev_conversions) / prev_conversions * 100
                )

            # Generate insights
            key_insights = []

            if revenue_change is not None:
                if revenue_change > 10:
                    key_insights.append(
                        f"Revenue increased {revenue_change:.1f}% week-over-week"
                    )
                elif revenue_change < -10:
                    key_insights.append(
                        f"Revenue decreased {abs(revenue_change):.1f}% week-over-week"
                    )

            if top_spider_sources:
                key_insights.append(
                    f"Top performer: {top_spider_sources[0]['source']} "
                    f"with ${top_spider_sources[0]['revenue']} revenue"
                )

            # Generate recommendations
            recommendations = []

            if conversions_change is not None and conversions_change < 0:
                recommendations.append(
                    "Review conversion funnel - conversions down this week"
                )

            if len(top_spider_sources) > 1:
                recommendations.append(
                    f"Consider increasing investment in {top_spider_sources[0]['source']}"
                )

            # Executive summary
            executive_summary = (
                f"Week of {week_start.strftime('%b %d, %Y')}: "
                f"${revenue_total:,.2f} revenue from {conversions} conversions. "
            )

            if revenue_change is not None:
                direction = "up" if revenue_change > 0 else "down"
                executive_summary += f"Revenue {direction} {abs(revenue_change):.1f}% vs prior week."

            # Update brief
            brief.total_revenue = revenue_total
            brief.total_conversions = conversions
            brief.total_opportunities = opportunities
            brief.total_spider_records = spider_records
            brief.revenue_change_pct = revenue_change
            brief.conversions_change_pct = conversions_change
            brief.top_spider_sources = top_spider_sources
            brief.key_insights = key_insights
            brief.recommendations = recommendations
            brief.executive_summary = executive_summary
            brief.status = 'complete'
            brief.generated_at = timezone.now()
            brief.save()

            logger.info(f"Generated weekly brief for {week_start.date()}")

            return {
                'id': str(brief.id),
                'status': 'generated',
                'week_start': brief.week_start.isoformat(),
                'week_end': brief.week_end.isoformat(),
                'total_revenue': str(brief.total_revenue),
                'total_conversions': brief.total_conversions,
                'total_opportunities': brief.total_opportunities,
                'revenue_change_pct': str(brief.revenue_change_pct) if brief.revenue_change_pct else None,
                'top_spider_sources': brief.top_spider_sources,
                'key_insights': brief.key_insights,
                'recommendations': brief.recommendations,
                'executive_summary': brief.executive_summary
            }

        except Exception as e:
            logger.error(f"Error generating weekly brief: {e}")
            return {'status': 'error', 'error': str(e)}

    def get_weekly_briefs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent weekly briefs."""
        try:
            from core.models_unified_system import WeeklyIntelligenceBrief

            briefs = WeeklyIntelligenceBrief.objects.filter(
                status='complete'
            ).order_by('-week_start')[:limit]

            return [
                {
                    'id': str(b.id),
                    'week_start': b.week_start.isoformat(),
                    'week_end': b.week_end.isoformat(),
                    'total_revenue': str(b.total_revenue),
                    'total_conversions': b.total_conversions,
                    'revenue_change_pct': str(b.revenue_change_pct) if b.revenue_change_pct else None,
                    'executive_summary': b.executive_summary,
                    'generated_at': b.generated_at.isoformat() if b.generated_at else None
                }
                for b in briefs
            ]

        except Exception as e:
            logger.error(f"Error getting weekly briefs: {e}")
            return []


# ============================================================================
# Singleton and Convenience Functions
# ============================================================================

_roi_tracker_instance: Optional[ROITracker] = None


def get_roi_tracker() -> ROITracker:
    """Get singleton ROI tracker instance."""
    global _roi_tracker_instance
    if _roi_tracker_instance is None:
        _roi_tracker_instance = ROITracker()
    return _roi_tracker_instance


def record_view(
    opportunity_id: str,
    user_id: Optional[int] = None,
    source: Optional[str] = None,
    **kwargs
) -> ConversionResult:
    """Record an opportunity view event."""
    tracker = get_roi_tracker()
    return tracker.record_conversion_event(
        event_type='view',
        opportunity_id=opportunity_id,
        user_id=user_id,
        attribution_source=source,
        **kwargs
    )


def record_click(
    opportunity_id: str,
    user_id: Optional[int] = None,
    source: Optional[str] = None,
    previous_event_id: Optional[str] = None,
    **kwargs
) -> ConversionResult:
    """Record a click event."""
    tracker = get_roi_tracker()
    return tracker.record_conversion_event(
        event_type='click',
        opportunity_id=opportunity_id,
        user_id=user_id,
        attribution_source=source,
        previous_event_id=previous_event_id,
        **kwargs
    )


def record_application(
    opportunity_id: str,
    user_id: Optional[int] = None,
    source: Optional[str] = None,
    previous_event_id: Optional[str] = None,
    **kwargs
) -> ConversionResult:
    """Record an application event."""
    tracker = get_roi_tracker()
    return tracker.record_conversion_event(
        event_type='apply',
        opportunity_id=opportunity_id,
        user_id=user_id,
        attribution_source=source,
        previous_event_id=previous_event_id,
        **kwargs
    )


def record_conversion(
    opportunity_id: str,
    user_id: Optional[int] = None,
    value: Optional[Decimal] = None,
    source: Optional[str] = None,
    previous_event_id: Optional[str] = None,
    **kwargs
) -> ConversionResult:
    """Record a conversion event."""
    tracker = get_roi_tracker()
    return tracker.record_conversion_event(
        event_type='convert',
        opportunity_id=opportunity_id,
        user_id=user_id,
        value=value,
        attribution_source=source,
        previous_event_id=previous_event_id,
        **kwargs
    )


def record_revenue(
    opportunity_id: str,
    value: Decimal,
    user_id: Optional[int] = None,
    source: Optional[str] = None,
    previous_event_id: Optional[str] = None,
    **kwargs
) -> ConversionResult:
    """Record a revenue event (triggers attribution)."""
    tracker = get_roi_tracker()
    return tracker.record_conversion_event(
        event_type='revenue',
        opportunity_id=opportunity_id,
        user_id=user_id,
        value=value,
        attribution_source=source,
        previous_event_id=previous_event_id,
        **kwargs
    )
