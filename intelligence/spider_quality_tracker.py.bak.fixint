"""
Spider Quality Metrics & Learning System
Tracks spider source quality and optimizes fetch priorities
"""

from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
import math

logger = logging.getLogger(__name__)


class SpiderQualityMetrics(models.Model):
    """
    Tracks quality metrics for each spider source
    Enables data-driven spider prioritization
    """

    spider_name = models.CharField(max_length=100, db_index=True)
    source_platform = models.CharField(max_length=100, db_index=True)

    # Fetch metrics
    opportunities_fetched = models.IntegerField(default=0)
    fetch_success_rate = models.FloatField(default=1.0)
    avg_fetch_time_ms = models.IntegerField(default=0)

    # Engagement metrics
    opportunities_viewed = models.IntegerField(default=0)
    opportunities_clicked = models.IntegerField(default=0)
    opportunities_applied = models.IntegerField(default=0)
    opportunities_accepted = models.IntegerField(default=0)

    # Quality scores (0-1)
    view_rate = models.FloatField(default=0.0)
    click_rate = models.FloatField(default=0.0)
    application_rate = models.FloatField(default=0.0)
    acceptance_rate = models.FloatField(default=0.0)

    # Composite quality score (0-100)
    quality_score = models.FloatField(default=50.0)

    # Learning metadata
    confidence_level = models.FloatField(default=0.5)
    last_updated = models.DateTimeField(auto_now=True)
    sample_size = models.IntegerField(default=0)

    # Priority adjustment
    fetch_priority = models.CharField(
        max_length=20,
        choices=[
            ('very_high', 'Very High'),
            ('high', 'High'),
            ('normal', 'Normal'),
            ('low', 'Low'),
            ('very_low', 'Very Low'),
        ],
        default='normal'
    )

    class Meta:
        app_label = 'intelligence_rt'
        unique_together = ['spider_name', 'source_platform']
        indexes = [
            models.Index(fields=['-quality_score']),
            models.Index(fields=['fetch_priority']),
        ]

    def update_metrics(self):
        """Recalculate all quality metrics"""
        if self.opportunities_fetched > 0:
            self.view_rate = self.opportunities_viewed / self.opportunities_fetched

        if self.opportunities_viewed > 0:
            self.click_rate = self.opportunities_clicked / self.opportunities_viewed

        if self.opportunities_clicked > 0:
            self.application_rate = self.opportunities_applied / self.opportunities_clicked

        if self.opportunities_applied > 0:
            self.acceptance_rate = self.opportunities_accepted / self.opportunities_applied

        # Calculate composite quality score (weighted)
        self.quality_score = (
            self.view_rate * 20 +  # 20 points for views
            self.click_rate * 30 +  # 30 points for clicks
            self.application_rate * 30 +  # 30 points for applications
            self.acceptance_rate * 20  # 20 points for acceptances
        ) * 100

        # Update confidence based on sample size
        self.sample_size = (
            self.opportunities_viewed +
            self.opportunities_clicked +
            self.opportunities_applied
        )

        # Confidence increases logarithmically with sample size
        if self.sample_size > 0:
            self.confidence_level = min(1.0, math.log10(self.sample_size + 1) / 2)

        # Adjust fetch priority based on quality score
        self.fetch_priority = self._calculate_priority()

        self.save()

    def _calculate_priority(self) -> str:
        """Calculate fetch priority based on quality score and confidence"""
        # Only adjust priority if we have enough confidence
        if self.confidence_level < 0.3:
            return 'normal'  # Not enough data yet

        score = self.quality_score

        if score >= 75:
            return 'very_high'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'normal'
        elif score >= 25:
            return 'low'
        else:
            return 'very_low'

    def record_fetch(self, count: int, success: bool, fetch_time_ms: int):
        """Record spider fetch event"""
        self.opportunities_fetched += count

        # Update fetch success rate (exponential moving average)
        success_value = 1.0 if success else 0.0
        self.fetch_success_rate = self.fetch_success_rate * 0.9 + success_value * 0.1

        # Update avg fetch time (exponential moving average)
        self.avg_fetch_time_ms = int(self.avg_fetch_time_ms * 0.9 + fetch_time_ms * 0.1)

        self.update_metrics()

    def record_interaction(self, interaction_type: str):
        """
        Record user interaction with opportunity from this source

        Args:
            interaction_type: 'view', 'click', 'apply', 'accept'
        """
        if interaction_type == 'view':
            self.opportunities_viewed += 1
        elif interaction_type == 'click':
            self.opportunities_clicked += 1
        elif interaction_type == 'apply':
            self.opportunities_applied += 1
        elif interaction_type == 'accept':
            self.opportunities_accepted += 1

        self.update_metrics()

    @classmethod
    def get_top_sources(cls, limit=10):
        """Get top performing sources by quality score"""
        return cls.objects.order_by('-quality_score', '-confidence_level')[:limit]

    @classmethod
    def get_sources_by_priority(cls, priority: str):
        """Get all sources with specific priority"""
        return cls.objects.filter(fetch_priority=priority)


class SpiderLearningLoop:
    """
    Learning loop that connects user interactions back to spider optimization
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def on_opportunity_fetched(self, spider_name: str, source_platform: str,
                               count: int, success: bool, fetch_time_ms: int):
        """
        Called when spider fetches opportunities
        """
        metrics, created = SpiderQualityMetrics.objects.get_or_create(
            spider_name=spider_name,
            source_platform=source_platform
        )

        metrics.record_fetch(count, success, fetch_time_ms)

        self.logger.info(
            f"🕷️ Spider fetch recorded: {source_platform} - "
            f"{count} opps, quality={metrics.quality_score:.1f}"
        )

    def on_opportunity_interaction(self, opportunity, interaction_type: str):
        """
        Called when user interacts with opportunity
        """
        # Extract source platform from opportunity
        source_platform = opportunity.source if hasattr(opportunity, 'source') else 'unknown'
        if hasattr(opportunity, 'metadata') and isinstance(opportunity.metadata, dict):
            source_platform = opportunity.metadata.get('platform', source_platform)

        spider_name = 'FreelanceOpportunitySpider'
        if hasattr(opportunity, 'metadata') and isinstance(opportunity.metadata, dict):
            spider_name = opportunity.metadata.get('spider_name', spider_name)

        # Update metrics
        metrics, created = SpiderQualityMetrics.objects.get_or_create(
            spider_name=spider_name,
            source_platform=source_platform
        )

        metrics.record_interaction(interaction_type)

        self.logger.info(
            f"👤 User interaction recorded: {interaction_type} on {source_platform} "
            f"(quality={metrics.quality_score:.1f})"
        )

    def get_optimized_source_priorities(self) -> dict:
        """
        Get optimized source priorities for spider fetching

        Returns:
            dict: {source_platform: {priority, quality_score, confidence}}
        """
        all_metrics = SpiderQualityMetrics.objects.all()

        priorities = {}
        for metric in all_metrics:
            priorities[metric.source_platform] = {
                'priority': metric.fetch_priority,
                'quality_score': metric.quality_score,
                'confidence': metric.confidence_level
            }

        return priorities

    def generate_spider_insights(self) -> dict:
        """
        Generate insights about spider performance
        """
        top_sources = SpiderQualityMetrics.get_top_sources(5)
        low_performing = SpiderQualityMetrics.objects.filter(
            quality_score__lt=30,
            confidence_level__gte=0.5
        )

        return {
            'top_sources': [
                {
                    'platform': m.source_platform,
                    'quality_score': m.quality_score,
                    'click_rate': m.click_rate,
                    'application_rate': m.application_rate
                }
                for m in top_sources
            ],
            'underperforming_sources': [
                {
                    'platform': m.source_platform,
                    'quality_score': m.quality_score,
                    'recommendation': 'Consider reducing fetch frequency'
                }
                for m in low_performing
            ],
            'recommendations': self._generate_recommendations(top_sources, low_performing)
        }

    def _generate_recommendations(self, top_sources, low_performing):
        """Generate actionable recommendations"""
        recommendations = []

        if top_sources:
            best = top_sources[0]
            recommendations.append(
                f"🎯 Focus on {best.source_platform} - "
                f"{best.quality_score:.0f}% quality score"
            )

        if low_performing.count() > 0:
            recommendations.append(
                f"⚠️ {low_performing.count()} sources underperforming - "
                f"consider reducing fetch frequency"
            )

        return recommendations


# Global instance
spider_learning_loop = SpiderLearningLoop()


# Signal handlers
try:
    from core.models_engagement_metrics import OpportunityInteraction

    @receiver(post_save, sender=OpportunityInteraction)
    def on_opportunity_interaction_created(sender, instance, created, **kwargs):
        """
        Connect user interactions to spider learning
        """
        if created:
            try:
                from core.models_unified_system import Opportunity
                opportunity = Opportunity.objects.filter(
                    id=instance.opportunity_id
                ).first()

                if opportunity:
                    spider_learning_loop.on_opportunity_interaction(
                        opportunity,
                        instance.interaction_type
                    )
            except Exception as e:
                logger.error(f"Error in spider learning loop signal: {e}", exc_info=True)
except ImportError:
    logger.warning("OpportunityInteraction model not found - spider learning signals not registered")

# LEARNING LOOP: Connect job applications to spider quality
try:
    from core.models.jobs.models import JobApplication

    @receiver(post_save, sender=JobApplication)
    def on_job_application_created(sender, instance, created, **kwargs):
        """
        LEARNING LOOP: When user applies to job, update spider quality metrics
        """
        if created:
            try:
                # Extract spider source from job metadata
                if hasattr(instance, 'metadata') and isinstance(instance.metadata, dict):
                    spider_name = instance.metadata.get('spider_name', 'JobSpider')
                    source_platform = instance.platform or 'unknown'

                    # Get or create metrics for this spider/platform
                    metrics, _ = SpiderQualityMetrics.objects.get_or_create(
                        spider_name=spider_name,
                        source_platform=source_platform
                    )

                    # Record application (high-value interaction)
                    metrics.record_interaction('apply')

                    logger.info(
                        f"🎯 Job application recorded for spider quality: "
                        f"{source_platform} (quality={metrics.quality_score:.1f})"
                    )
            except Exception as e:
                logger.error(f"Error updating spider quality from job application: {e}")

    @receiver(post_save, sender=JobApplication)
    def on_job_application_outcome(sender, instance, **kwargs):
        """
        LEARNING LOOP: When job application has outcome, update spider quality
        """
        # Only process status updates (not creation)
        if instance.pk and instance.status in ['offer_accepted', 'hired']:
            try:
                if hasattr(instance, 'metadata') and isinstance(instance.metadata, dict):
                    spider_name = instance.metadata.get('spider_name', 'JobSpider')
                    source_platform = instance.platform or 'unknown'

                    # Get or create metrics
                    metrics, _ = SpiderQualityMetrics.objects.get_or_create(
                        spider_name=spider_name,
                        source_platform=source_platform
                    )

                    # Record acceptance (highest-value interaction)
                    metrics.record_interaction('accept')

                    logger.info(
                        f"✅ Job acceptance recorded for spider quality: "
                        f"{source_platform} (quality={metrics.quality_score:.1f})"
                    )
            except Exception as e:
                logger.error(f"Error updating spider quality from job outcome: {e}")

except ImportError:
    logger.warning("JobApplication model not found - job application learning signals not registered")
