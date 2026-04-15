"""
Session 706: DIGESTIVE SYSTEM - Data Ingestion & Processing Service

The DIGESTIVE SYSTEM monitors how raw spider data is transformed into
actionable intelligence through the 4-stage pipeline:

1. INTAKE: Spider data collection (SpiderData, SpiderExecutionLog)
2. PROCESSING: Normalization, deduplication
3. ENRICHMENT: Embedding generation, relevance scoring
4. ROUTING: Data delivery to agents and services

Key Features:
- Stage-by-stage health monitoring
- Throughput and latency metrics
- Bottleneck detection
- Integration with HEART and CIRCULATORY systems

Usage:
    from core.services.digestive import get_digestive_system

    digestive = get_digestive_system()

    # Run full digestion check
    result = digestive.digest()

    # Quick health check
    is_ok = digestive.is_digesting()

    # Get cached vitals
    vitals = digestive.get_vitals()

    # Get metabolism rate
    metabolism = digestive.get_metabolism_rate()
"""

import logging
import uuid
from datetime import timedelta
from typing import Optional, List, Dict, Any

from django.db import transaction
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone

logger = logging.getLogger(__name__)


# Singleton instance
_digestive_instance: Optional['DigestiveSystemService'] = None


def get_digestive_system() -> 'DigestiveSystemService':
    """Get the singleton DigestiveSystemService instance."""
    global _digestive_instance
    if _digestive_instance is None:
        _digestive_instance = DigestiveSystemService()
    return _digestive_instance


class DigestiveSystemService:
    """
    Data Ingestion & Processing - the digestive system of the AI body.

    Monitors spider data intake, processing, enrichment, and routing
    to ensure smooth data flow through the system.
    """

    # Health thresholds
    HEALTHY_THRESHOLD = 80.0      # 80%+ = healthy
    SLUGGISH_THRESHOLD = 60.0     # 60-80% = sluggish
    BLOATED_THRESHOLD = 40.0      # 40-60% = bloated
    BLOCKED_THRESHOLD = 20.0      # 20-40% = blocked
    # Below 20% = starving

    # Cache duration
    CACHE_DURATION_SECONDS = 30

    # Status UUID for singleton record
    STATUS_UUID = uuid.UUID('00000000-0000-0000-0000-000000000006')

    def __init__(self):
        self._cached_pulse = None
        self._cache_time = None

    def digest(self, force: bool = False) -> dict:
        """
        Run full digestion check - the main health check method.

        Returns:
            dict: Comprehensive digestion status including:
                - overall_status: healthy/sluggish/bloated/blocked/starving
                - digestion_score: 0-100%
                - stage-specific metrics
                - bottlenecks detected
        """
        from core.models_digestive import IngestionRoute, DigestivePulse, DigestionStatus

        start_time = timezone.now()
        cutoff_24h = timezone.now() - timedelta(hours=24)
        cutoff_1h = timezone.now() - timedelta(hours=1)

        # Check each stage
        intake_result = self.check_intake()
        processing_result = self.check_processing()
        enrichment_result = self.check_enrichment()
        routing_result = self.check_routing()

        # Calculate overall score (weighted average of stages)
        stage_scores = [
            (intake_result.get('score', 100), 0.35),      # Intake: 35%
            (processing_result.get('score', 100), 0.30),  # Processing: 30%
            (enrichment_result.get('score', 100), 0.20),  # Enrichment: 20%
            (routing_result.get('score', 100), 0.15),     # Routing: 15%
        ]
        digestion_score = sum(score * weight for score, weight in stage_scores)

        # Determine overall status
        overall_status = self._determine_status(digestion_score)
        is_digesting = overall_status in ('healthy', 'sluggish')

        # Detect bottlenecks
        bottlenecks = self.detect_bottlenecks(
            intake_result, processing_result, enrichment_result, routing_result
        )

        # Get route statuses
        routes = IngestionRoute.objects.filter(is_active=True)
        routes_checked = routes.count()
        routes_healthy = 0
        routes_warning = 0
        routes_critical = 0

        for route in routes:
            try:
                status = route.status
                if status.is_healthy:
                    routes_healthy += 1
                elif status.status in ('sluggish', 'bloated'):
                    routes_warning += 1
                else:
                    routes_critical += 1
            except DigestionStatus.DoesNotExist:
                pass

        # Calculate metabolism rates (items per minute over last hour)
        metabolism = self.get_metabolism_rate()

        # Check integrations
        heart_connected = self._check_heart_connection()
        circulatory_connected = self._check_circulatory_connection()

        end_time = timezone.now()
        check_duration_ms = (end_time - start_time).total_seconds() * 1000

        # Create pulse record
        pulse = DigestivePulse.objects.create(
            overall_status=overall_status,
            digestion_score=digestion_score,
            is_digesting=is_digesting,

            # Intake metrics
            items_ingested_24h=intake_result.get('items_24h', 0),
            spiders_executed_24h=intake_result.get('spiders_executed', 0),
            spider_success_rate=intake_result.get('success_rate', 100.0),
            intake_errors_24h=intake_result.get('errors', 0),
            duplicates_filtered_24h=intake_result.get('duplicates_filtered', 0),

            # Processing metrics
            items_processed_24h=processing_result.get('items_24h', 0),
            items_pending=processing_result.get('queue_depth', 0),
            processing_throughput=processing_result.get('throughput', 0),
            avg_processing_time_ms=processing_result.get('avg_latency_ms', 0),
            processing_errors_24h=processing_result.get('errors', 0),

            # Enrichment metrics
            embeddings_generated_24h=enrichment_result.get('embeddings_24h', 0),
            embedding_coverage_pct=enrichment_result.get('coverage', 0),
            relevance_scores_calculated_24h=enrichment_result.get('scores_24h', 0),
            enrichment_errors_24h=enrichment_result.get('errors', 0),

            # Routing metrics
            items_routed_24h=routing_result.get('items_24h', 0),
            items_filtered_24h=routing_result.get('filtered', 0),
            items_actionable_24h=routing_result.get('actionable', 0),
            routing_errors_24h=routing_result.get('errors', 0),

            # Metabolism rates
            intake_rate=metabolism.get('intake_rate', 0),
            processing_rate=metabolism.get('processing_rate', 0),
            output_rate=metabolism.get('output_rate', 0),

            # Stage statuses
            intake_status=intake_result.get('status', 'healthy'),
            processing_status=processing_result.get('status', 'healthy'),
            enrichment_status=enrichment_result.get('status', 'healthy'),
            routing_status=routing_result.get('status', 'healthy'),

            # Bottlenecks
            bottlenecks=bottlenecks,

            # Routes
            routes_checked=routes_checked,
            routes_healthy=routes_healthy,
            routes_warning=routes_warning,
            routes_critical=routes_critical,

            # Integrations
            heart_connected=heart_connected,
            circulatory_connected=circulatory_connected,

            # Metadata
            check_duration_ms=int(check_duration_ms),
        )

        # Cache result
        self._cached_pulse = pulse
        self._cache_time = timezone.now()

        result = {
            'timestamp': timezone.now().isoformat(),
            'overall_status': overall_status,
            'digestion_score': round(digestion_score, 1),
            'is_digesting': is_digesting,
            'check_duration_ms': round(check_duration_ms, 2),

            # Stages
            'stages': {
                'intake': {
                    'status': intake_result.get('status', 'healthy'),
                    'score': round(intake_result.get('score', 100), 1),
                    'items_24h': intake_result.get('items_24h', 0),
                    'spiders_executed': intake_result.get('spiders_executed', 0),
                    'success_rate': round(intake_result.get('success_rate', 100), 1),
                },
                'processing': {
                    'status': processing_result.get('status', 'healthy'),
                    'score': round(processing_result.get('score', 100), 1),
                    'queue_depth': processing_result.get('queue_depth', 0),
                    'throughput': round(processing_result.get('throughput', 0), 2),
                    'avg_latency_ms': round(processing_result.get('avg_latency_ms', 0), 0),
                },
                'enrichment': {
                    'status': enrichment_result.get('status', 'healthy'),
                    'score': round(enrichment_result.get('score', 100), 1),
                    'embeddings_24h': enrichment_result.get('embeddings_24h', 0),
                    'coverage': round(enrichment_result.get('coverage', 0), 1),
                },
                'routing': {
                    'status': routing_result.get('status', 'healthy'),
                    'score': round(routing_result.get('score', 100), 1),
                    'items_routed': routing_result.get('items_24h', 0),
                    'items_filtered': routing_result.get('filtered', 0),
                },
            },

            # Metabolism
            'metabolism': {
                'intake_rate': round(metabolism.get('intake_rate', 0), 2),
                'processing_rate': round(metabolism.get('processing_rate', 0), 2),
                'output_rate': round(metabolism.get('output_rate', 0), 2),
            },

            # Bottlenecks
            'bottlenecks': bottlenecks,

            # Routes summary
            'routes': {
                'checked': routes_checked,
                'healthy': routes_healthy,
                'warning': routes_warning,
                'critical': routes_critical,
            },

            # Integrations
            'integrations': {
                'heart': heart_connected,
                'circulatory': circulatory_connected,
            },
        }

        logger.info(f"DIGESTIVE check: {overall_status} ({digestion_score:.1f}%) - "
                   f"Intake: {intake_result.get('items_24h', 0)} items, "
                   f"Bottlenecks: {len(bottlenecks)}")

        return result

    def is_digesting(self) -> bool:
        """Quick check - is data being processed normally?"""
        pulse = self._get_cached_pulse()
        return pulse.is_digesting if pulse else True

    def get_vitals(self) -> dict:
        """Get current digestion vitals (cached)."""
        pulse = self._get_cached_pulse()
        if not pulse:
            try:
                return self.digest()
            except Exception as e:
                logger.warning(f"DIGESTIVE full check failed, returning defaults: {e}")
                return {
                    'overall_status': 'unknown',
                    'digestion_score': 50,
                    'is_digesting': True,
                    'stages': {},
                    'metabolism': {},
                    'items_pending': 0,
                    'bottlenecks': [],
                    'error': str(e),
                }

        return {
            'timestamp': pulse.recorded_at.isoformat(),
            'overall_status': pulse.overall_status,
            'digestion_score': pulse.digestion_score,
            'is_digesting': pulse.is_digesting,
            'stages': {
                'intake': pulse.intake_status,
                'processing': pulse.processing_status,
                'enrichment': pulse.enrichment_status,
                'routing': pulse.routing_status,
            },
            'metabolism': {
                'intake_rate': pulse.intake_rate,
                'processing_rate': pulse.processing_rate,
                'output_rate': pulse.output_rate,
            },
            'items_pending': pulse.items_pending,
            'bottlenecks': pulse.bottlenecks,
        }

    def get_status(self) -> dict:
        """Get current status for body coordinator integration."""
        return self.get_vitals()

    def get_history(self, hours: int = 24, limit: int = 100) -> List[dict]:
        """Get digestion pulse history."""
        from core.models_digestive import DigestivePulse

        cutoff = timezone.now() - timedelta(hours=hours)
        pulses = DigestivePulse.objects.filter(recorded_at__gte=cutoff)[:limit]

        return [
            {
                'id': str(p.id),
                'timestamp': p.recorded_at.isoformat(),
                'status': p.overall_status,
                'score': p.digestion_score,
                'is_digesting': p.is_digesting,
                'intake_status': p.intake_status,
                'processing_status': p.processing_status,
                'enrichment_status': p.enrichment_status,
                'routing_status': p.routing_status,
                'items_pending': p.items_pending,
                'check_duration_ms': p.check_duration_ms,
            }
            for p in pulses
        ]

    def check_intake(self) -> dict:
        """Check spider data intake health."""
        from core.models_unified_system import SpiderData, SpiderExecutionLog, SpiderItemHash

        cutoff_24h = timezone.now() - timedelta(hours=24)

        # Count SpiderData created in last 24h
        items_24h = SpiderData.objects.filter(created_at__gte=cutoff_24h).count()

        # Spider execution stats
        executions = SpiderExecutionLog.objects.filter(started_at__gte=cutoff_24h)
        spiders_executed = executions.count()

        # Count both 'success' and 'partial' as successful executions
        # 'partial' means spider ran but found no NEW items (deduplication working)
        successful = executions.filter(status__in=['success', 'partial']).count()
        success_rate = (successful / spiders_executed * 100) if spiders_executed > 0 else 100.0

        errors = executions.filter(status__in=['error', 'timeout']).count()

        # Deduplication stats
        duplicates_filtered = SpiderItemHash.objects.filter(created_at__gte=cutoff_24h).count()

        # Calculate score
        # Base 100, deduct for low intake or errors
        score = 100.0

        # Deduct for low intake (if less than expected)
        expected_hourly = 50  # Expected items per hour
        expected_24h = expected_hourly * 24
        if items_24h < expected_24h * 0.5:  # Less than 50% of expected
            score -= 30
        elif items_24h < expected_24h * 0.75:  # Less than 75% of expected
            score -= 15

        # Deduct for errors
        if spiders_executed > 0:
            error_rate = errors / spiders_executed
            score -= min(30, error_rate * 100)

        # Deduct for low success rate
        if success_rate < 90:
            score -= (90 - success_rate)

        score = max(0, min(100, score))
        status = self._determine_status(score)

        # Check for starvation (no intake in last hour)
        recent_intake = SpiderData.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=1)
        ).count()
        if recent_intake == 0 and items_24h > 0:
            status = 'starving'
            score = min(score, 19)

        return {
            'status': status,
            'score': score,
            'items_24h': items_24h,
            'spiders_executed': spiders_executed,
            'success_rate': success_rate,
            'errors': errors,
            'duplicates_filtered': duplicates_filtered,
        }

    def check_processing(self) -> dict:
        """Check data processing queue and throughput."""
        from core.models_unified_system import SpiderData

        cutoff_24h = timezone.now() - timedelta(hours=24)
        cutoff_1h = timezone.now() - timedelta(hours=1)

        # Count unprocessed items (queue depth)
        # Using is_processed field if available, otherwise estimate
        try:
            queue_depth = SpiderData.objects.filter(is_processed=False).count()
        except Exception:
            # If is_processed field doesn't exist, estimate from recent untagged items
            queue_depth = SpiderData.objects.filter(
                created_at__gte=cutoff_24h,
                relevance_score__isnull=True
            ).count()

        # Processed items (24h)
        try:
            items_24h = SpiderData.objects.filter(
                is_processed=True,
                created_at__gte=cutoff_24h
            ).count()
        except Exception:
            items_24h = SpiderData.objects.filter(
                created_at__gte=cutoff_24h,
                relevance_score__isnull=False
            ).count()

        # Calculate throughput (items per minute over last hour)
        # Use processed_at timestamp to count items actually processed recently
        try:
            recent_processed = SpiderData.objects.filter(
                is_processed=True,
                processed_at__gte=cutoff_1h
            ).count()
        except Exception:
            # Fallback: count items created recently that are processed
            recent_processed = SpiderData.objects.filter(
                is_processed=True,
                created_at__gte=cutoff_1h
            ).count()

        throughput = recent_processed / 60.0  # items per minute

        # Estimate average latency (time from creation to processing)
        # This is a rough estimate - actual latency tracking would need timestamps
        avg_latency_ms = 0
        if throughput > 0:
            avg_latency_ms = queue_depth / throughput * 60000 if queue_depth > 0 else 500

        # Calculate score
        score = 100.0

        # Deduct for high queue depth
        if queue_depth > 1000:
            score -= 40
        elif queue_depth > 500:
            score -= 25
        elif queue_depth > 200:
            score -= 10

        # Deduct for low throughput (if there's a queue)
        if queue_depth > 100 and throughput < 5:
            score -= 20
        elif queue_depth > 50 and throughput < 2:
            score -= 30

        # Deduct for high latency
        if avg_latency_ms > 10000:
            score -= 20
        elif avg_latency_ms > 5000:
            score -= 10

        score = max(0, min(100, score))
        status = self._determine_status(score)

        # Check for blocked (queue growing, no processing)
        if queue_depth > 500 and throughput < 1:
            status = 'blocked'
            score = min(score, 19)

        return {
            'status': status,
            'score': score,
            'queue_depth': queue_depth,
            'items_24h': items_24h,
            'throughput': throughput,
            'avg_latency_ms': avg_latency_ms,
            'errors': 0,  # Would need error tracking
        }

    def check_enrichment(self) -> dict:
        """Check embedding/scoring pipeline health."""
        from core.models_unified_system import SpiderData

        cutoff_24h = timezone.now() - timedelta(hours=24)

        # Count items with embeddings
        total_items = SpiderData.objects.filter(created_at__gte=cutoff_24h).count()

        # Check for embedding field
        try:
            items_with_embeddings = SpiderData.objects.filter(
                created_at__gte=cutoff_24h,
                embedding__isnull=False
            ).count()
        except Exception:
            # If embedding field doesn't exist, assume no embeddings
            items_with_embeddings = 0

        coverage = (items_with_embeddings / total_items * 100) if total_items > 0 else 0

        # Count items with relevance scores
        items_with_scores = SpiderData.objects.filter(
            created_at__gte=cutoff_24h,
            relevance_score__isnull=False
        ).count()

        # Calculate score
        score = 100.0

        # Deduct for low embedding coverage
        if coverage < 30:
            score -= 40
        elif coverage < 50:
            score -= 25
        elif coverage < 70:
            score -= 10

        # Deduct for low relevance scoring coverage
        score_coverage = (items_with_scores / total_items * 100) if total_items > 0 else 0
        if score_coverage < 50:
            score -= 15
        elif score_coverage < 75:
            score -= 5

        score = max(0, min(100, score))
        status = self._determine_status(score)

        return {
            'status': status,
            'score': score,
            'embeddings_24h': items_with_embeddings,
            'coverage': coverage,
            'scores_24h': items_with_scores,
            'total_items': total_items,
            'errors': 0,
        }

    def check_routing(self) -> dict:
        """Check data routing to consumers."""
        from core.models_unified_system import SpiderData

        cutoff_24h = timezone.now() - timedelta(hours=24)

        total_items = SpiderData.objects.filter(created_at__gte=cutoff_24h).count()

        # Items marked as actionable (routed to agents)
        try:
            items_actionable = SpiderData.objects.filter(
                created_at__gte=cutoff_24h,
                is_actionable=True
            ).count()
        except Exception:
            # If is_actionable doesn't exist, estimate from relevance scores
            items_actionable = SpiderData.objects.filter(
                created_at__gte=cutoff_24h,
                relevance_score__gte=70  # High relevance = likely actionable
            ).count()

        # Items filtered out (low relevance)
        items_filtered = SpiderData.objects.filter(
            created_at__gte=cutoff_24h,
            relevance_score__lt=50
        ).count() if total_items > 0 else 0

        # Items routed (actionable or high relevance)
        items_routed = SpiderData.objects.filter(
            created_at__gte=cutoff_24h,
            relevance_score__gte=50
        ).count() if total_items > 0 else 0

        # Calculate score
        score = 100.0

        # Routing score based on throughput vs items available
        if total_items > 0:
            routing_rate = items_routed / total_items
            if routing_rate < 0.3:
                score -= 30
            elif routing_rate < 0.5:
                score -= 15

            # Check for actionable rate
            actionable_rate = items_actionable / total_items
            if actionable_rate < 0.1:
                score -= 20
            elif actionable_rate < 0.2:
                score -= 10

        score = max(0, min(100, score))
        status = self._determine_status(score)

        return {
            'status': status,
            'score': score,
            'items_24h': items_routed,
            'actionable': items_actionable,
            'filtered': items_filtered,
            'total_items': total_items,
            'errors': 0,
        }

    def detect_bottlenecks(self, intake: dict, processing: dict,
                          enrichment: dict, routing: dict) -> List[dict]:
        """Identify slowdowns in data processing pipeline."""
        bottlenecks = []

        # Check intake bottlenecks
        if intake.get('status') == 'starving':
            bottlenecks.append({
                'stage': 'intake',
                'issue': 'No data intake in the last hour',
                'severity': 'critical',
            })
        elif intake.get('success_rate', 100) < 70:
            bottlenecks.append({
                'stage': 'intake',
                'issue': f"Low spider success rate ({intake.get('success_rate', 0):.1f}%)",
                'severity': 'warning',
            })

        # Check processing bottlenecks
        queue_depth = processing.get('queue_depth', 0)
        if queue_depth > 500:
            bottlenecks.append({
                'stage': 'processing',
                'issue': f'High queue depth ({queue_depth} items pending)',
                'severity': 'critical' if queue_depth > 1000 else 'warning',
            })

        throughput = processing.get('throughput', 0)
        if queue_depth > 100 and throughput < 2:
            bottlenecks.append({
                'stage': 'processing',
                'issue': f'Low processing throughput ({throughput:.1f} items/min)',
                'severity': 'warning',
            })

        # Check enrichment bottlenecks
        coverage = enrichment.get('coverage', 0)
        if coverage < 30:
            bottlenecks.append({
                'stage': 'enrichment',
                'issue': f'Low embedding coverage ({coverage:.1f}%)',
                'severity': 'critical' if coverage < 10 else 'warning',
            })
        elif coverage < 50:
            bottlenecks.append({
                'stage': 'enrichment',
                'issue': f'Moderate embedding coverage ({coverage:.1f}%)',
                'severity': 'info',
            })

        # Check routing bottlenecks
        if routing.get('items_24h', 0) == 0 and intake.get('items_24h', 0) > 0:
            bottlenecks.append({
                'stage': 'routing',
                'issue': 'No items routed despite intake',
                'severity': 'warning',
            })

        return bottlenecks

    def get_metabolism_rate(self) -> dict:
        """Calculate current throughput metrics (items per minute)."""
        from core.models_unified_system import SpiderData

        cutoff_1h = timezone.now() - timedelta(hours=1)

        # Intake rate (items created per minute in last hour)
        items_ingested_1h = SpiderData.objects.filter(created_at__gte=cutoff_1h).count()
        intake_rate = items_ingested_1h / 60.0

        # Processing rate (items processed per minute) - use processed_at timestamp
        try:
            items_processed_1h = SpiderData.objects.filter(
                processed_at__gte=cutoff_1h,
                is_processed=True
            ).count()
        except Exception:
            # Fallback to created_at
            items_processed_1h = SpiderData.objects.filter(
                created_at__gte=cutoff_1h,
                is_processed=True
            ).count()
        processing_rate = items_processed_1h / 60.0

        # Output rate (actionable items per minute)
        try:
            items_output_1h = SpiderData.objects.filter(
                created_at__gte=cutoff_1h,
                is_actionable=True
            ).count()
        except Exception:
            items_output_1h = SpiderData.objects.filter(
                created_at__gte=cutoff_1h,
                relevance_score__gte=70
            ).count()
        output_rate = items_output_1h / 60.0

        return {
            'intake_rate': intake_rate,
            'processing_rate': processing_rate,
            'output_rate': output_rate,
        }

    def get_routes(self, route_type: str = None, stage: str = None,
                  active_only: bool = True) -> List[dict]:
        """Get monitored ingestion routes."""
        from core.models_digestive import IngestionRoute

        queryset = IngestionRoute.objects.all()

        if active_only:
            queryset = queryset.filter(is_active=True)
        if route_type:
            queryset = queryset.filter(route_type=route_type)
        if stage:
            queryset = queryset.filter(stage=stage)

        return [
            {
                'id': str(r.id),
                'name': r.name,
                'display_name': r.display_name,
                'route_type': r.route_type,
                'stage': r.stage,
                'identifier': r.identifier,
                'is_critical': r.is_critical,
                'is_active': r.is_active,
                'max_queue_depth': r.max_queue_depth,
                'target_throughput': r.target_throughput,
                'total_items_processed': r.total_items_processed,
            }
            for r in queryset
        ]

    def get_status_emoji(self) -> str:
        """Get emoji for current status."""
        pulse = self._get_cached_pulse()
        if not pulse:
            return '❓'

        return {
            'healthy': '🍽️',     # Plate - digesting well
            'sluggish': '🐌',    # Snail - slow
            'bloated': '🎈',     # Balloon - full/backed up
            'blocked': '🚫',     # No entry - stuck
            'starving': '💀',    # Skull - no input
        }.get(pulse.overall_status, '❓')

    # Private methods

    def _determine_status(self, score: float) -> str:
        """Determine status based on score."""
        if score >= self.HEALTHY_THRESHOLD:
            return 'healthy'
        elif score >= self.SLUGGISH_THRESHOLD:
            return 'sluggish'
        elif score >= self.BLOATED_THRESHOLD:
            return 'bloated'
        elif score >= self.BLOCKED_THRESHOLD:
            return 'blocked'
        else:
            return 'starving'

    def _get_cached_pulse(self) -> Optional['DigestivePulse']:
        """Get cached pulse or fetch most recent from DB."""
        from core.models_digestive import DigestivePulse

        if (self._cached_pulse and self._cache_time and
            (timezone.now() - self._cache_time).total_seconds() < self.CACHE_DURATION_SECONDS):
            return self._cached_pulse

        try:
            pulse = DigestivePulse.objects.order_by('-recorded_at').first()
            self._cached_pulse = pulse
            self._cache_time = timezone.now()
            return pulse
        except Exception as _e:
            logger.warning(
                "digestive._get_cached_pulse: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return None

    def _check_heart_connection(self) -> bool:
        """Check if HEART service is accessible."""
        try:
            from core.services.heart import get_heart_monitor
            heart = get_heart_monitor()
            return heart.is_alive()
        except Exception as _e:
            logger.warning(
                "digestive._check_heart_connection: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return False

    def _check_circulatory_connection(self) -> bool:
        """Check if CIRCULATORY service is accessible."""
        try:
            from core.services.circulatory import get_circulatory_system
            circulatory = get_circulatory_system()
            return circulatory.is_flowing()
        except Exception as _e:
            logger.warning(
                "digestive._check_circulatory_connection: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return False
