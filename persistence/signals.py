"""
Django signals for the Data Persistence system.
"""

from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.core.cache import cache
import logging

from .models import (
    UnifiedEmbedding, AgentKnowledge, SpiderData,
    DataPersistenceMetrics
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=UnifiedEmbedding)
def update_embedding_cache(sender, instance, created, **kwargs):
    """
    Update cache when embeddings are created or modified.
    """
    if created:
        # Record embedding creation metric
        DataPersistenceMetrics.record_metric(
            name='embeddings_created_total',
            value=1,
            metric_type='counter',
            subsystem='embeddings',
            metadata={
                'content_type': instance.content_type,
                'source_system': instance.source_system
            }
        )

        # Update cache statistics
        cache_key = f"embedding_count_{instance.content_type}"
        current_count = cache.get(cache_key, 0)
        cache.set(cache_key, current_count + 1, 3600)  # Cache for 1 hour

        logger.info(f"Created embedding for {instance.content_type}:{instance.content_id}")

    # Clear related search cache when embeddings change
    cache.delete_pattern(f"search_results_*")


@receiver(post_save, sender=AgentKnowledge)
def track_knowledge_creation(sender, instance, created, **kwargs):
    """
    Track agent knowledge creation and updates.
    """
    if created:
        # Record knowledge creation metric
        DataPersistenceMetrics.record_metric(
            name='agent_knowledge_created_total',
            value=1,
            metric_type='counter',
            subsystem='agent_knowledge',
            metadata={
                'agent_name': instance.agent_name,
                'knowledge_type': instance.knowledge_type
            }
        )

        # Update agent knowledge cache
        cache_key = f"agent_knowledge_count_{instance.agent_name}"
        current_count = cache.get(cache_key, 0)
        cache.set(cache_key, current_count + 1, 3600)

        logger.info(f"Created knowledge '{instance.title}' for agent {instance.agent_name}")

    else:
        # Track knowledge updates
        if instance.usage_count > 0:
            DataPersistenceMetrics.record_metric(
                name='knowledge_usage_events',
                value=1,
                metric_type='counter',
                subsystem='agent_knowledge',
                metadata={
                    'agent_name': instance.agent_name,
                    'knowledge_type': instance.knowledge_type,
                    'success_rate': instance.success_rate
                }
            )


@receiver(post_save, sender=SpiderData)
def track_spider_discoveries(sender, instance, created, **kwargs):
    """
    Track spider data discoveries and processing.
    """
    if created:
        # Record discovery metric
        DataPersistenceMetrics.record_metric(
            name='spider_discoveries_total',
            value=1,
            metric_type='counter',
            subsystem='spider_data',
            metadata={
                'spider_name': instance.spider_name,
                'source_platform': instance.source_platform,
                'data_type': instance.data_type,
                'opportunity_score': instance.opportunity_score
            }
        )

        # Update platform discovery cache
        cache_key = f"spider_discoveries_{instance.source_platform}"
        current_count = cache.get(cache_key, 0)
        cache.set(cache_key, current_count + 1, 3600)

        # Track high-value opportunities
        if instance.opportunity_score > 0.8:
            DataPersistenceMetrics.record_metric(
                name='high_value_opportunities',
                value=1,
                metric_type='counter',
                subsystem='spider_data',
                metadata={
                    'spider_name': instance.spider_name,
                    'platform': instance.source_platform,
                    'score': instance.opportunity_score
                }
            )

        logger.info(f"Spider {instance.spider_name} discovered: {instance.title[:50]}")

    else:
        # Track conversion updates
        if instance.conversion_status == 'converted' and instance.revenue_generated > 0:
            DataPersistenceMetrics.record_metric(
                name='spider_data_revenue',
                value=float(instance.revenue_generated),
                metric_type='gauge',
                subsystem='spider_data',
                metadata={
                    'spider_name': instance.spider_name,
                    'platform': instance.source_platform,
                    'data_type': instance.data_type
                }
            )


@receiver(pre_delete, sender=UnifiedEmbedding)
def track_embedding_deletion(sender, instance, **kwargs):
    """
    Track embedding deletions for monitoring.
    """
    DataPersistenceMetrics.record_metric(
        name='embeddings_deleted_total',
        value=1,
        metric_type='counter',
        subsystem='embeddings',
        metadata={
            'content_type': instance.content_type,
            'source_system': instance.source_system,
            'reason': 'manual_deletion'
        }
    )

    logger.warning(f"Deleted embedding for {instance.content_type}:{instance.content_id}")


@receiver(post_delete, sender=UnifiedEmbedding)
def cleanup_embedding_cache(sender, instance, **kwargs):
    """
    Clean up cache when embeddings are deleted.
    """
    # Update cache counts
    cache_key = f"embedding_count_{instance.content_type}"
    current_count = cache.get(cache_key, 1)
    cache.set(cache_key, max(0, current_count - 1), 3600)

    # Clear search cache
    cache.delete_pattern(f"search_results_*")


# Custom signal for tracking system performance
class PerformanceTracker:
    """
    Track system performance metrics.
    """

    @staticmethod
    def track_search_performance(query_time_ms, result_count, search_type):
        """Track search performance metrics"""
        DataPersistenceMetrics.record_metric(
            name='search_performance_ms',
            value=query_time_ms,
            metric_type='timer',
            subsystem='search',
            metadata={
                'result_count': result_count,
                'search_type': search_type
            }
        )

    @staticmethod
    def track_embedding_generation_performance(generation_time_ms, model, success=True):
        """Track embedding generation performance"""
        metric_name = 'embedding_generation_success' if success else 'embedding_generation_failures'
        DataPersistenceMetrics.record_metric(
            name=metric_name,
            value=generation_time_ms,
            metric_type='timer',
            subsystem='embeddings',
            metadata={'model': model}
        )

    @staticmethod
    def track_agent_collaboration(session_duration_minutes, agent_count, knowledge_generated):
        """Track agent collaboration effectiveness"""
        DataPersistenceMetrics.record_metric(
            name='collaboration_session_duration',
            value=session_duration_minutes,
            metric_type='timer',
            subsystem='collaboration',
            metadata={
                'agent_count': agent_count,
                'knowledge_generated': knowledge_generated
            }
        )


# Export the performance tracker for use in services
performance_tracker = PerformanceTracker()