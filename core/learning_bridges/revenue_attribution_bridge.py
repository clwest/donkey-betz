"""
Revenue Attribution Learning Bridge
Connects revenue generation events to agent learning system

When revenue is generated, this bridge:
1. Identifies which agent/strategy was responsible
2. Updates agent's learning profile with success
3. Feeds insights to UnifiedLearningPipeline
4. Updates user's revenue generation patterns
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal
from typing import Dict

from core.models_unified_system import Revenue, UserAgentLearning, Agent

logger = logging.getLogger(__name__)


class RevenueAttributionLearningLoop:
    """
    Bidirectional learning loop for revenue attribution
    """

    def process_revenue_event(self, revenue: Revenue):
        """
        Process revenue creation/completion event

        Args:
            revenue: Revenue instance that triggered learning
        """
        logger.info(f"💰 Processing revenue event: ${revenue.amount} from {revenue.source_type}")

        try:
            # Step 1: Extract success factors
            success_factors = self._extract_success_factors(revenue)

            # Step 2: Update agent learning if agent attributed
            if revenue.agent:
                self._update_agent_learning(revenue, success_factors)

            # Step 3: Update user's revenue patterns
            self._update_user_revenue_patterns(revenue, success_factors)

            logger.info(f"✅ Revenue learning loop completed for revenue {revenue.id}")

        except Exception as e:
            logger.error(f"Error in revenue learning loop: {e}", exc_info=True)

    def _extract_success_factors(self, revenue: Revenue) -> Dict:
        """
        Extract what made this revenue generation successful

        Returns:
            dict of success factors
        """
        factors = {
            'source_type': revenue.source_type,
            'source_id': str(revenue.source_id) if revenue.source_id else None,
            'amount': float(revenue.amount),
            'currency': revenue.currency if hasattr(revenue, 'currency') else 'USD',
            'time_to_revenue': None,
            'agent_strategy': {},
            'opportunity_characteristics': {}
        }

        # Extract timing if we have earned_at
        if hasattr(revenue, 'earned_at') and revenue.earned_at and hasattr(revenue, 'created_at') and revenue.created_at:
            time_delta = revenue.earned_at - revenue.created_at
            factors['time_to_revenue'] = time_delta.total_seconds() / 86400  # days

        # Extract metadata if available
        if hasattr(revenue, 'metadata') and revenue.metadata:
            factors['agent_strategy'] = revenue.metadata.get('strategy', {})
            factors['opportunity_characteristics'] = revenue.metadata.get('opportunity', {})

        # Determine revenue quality
        if revenue.amount >= 5000:
            factors['revenue_quality'] = 'high'
        elif revenue.amount >= 1000:
            factors['revenue_quality'] = 'medium'
        else:
            factors['revenue_quality'] = 'low'

        return factors

    def _update_agent_learning(self, revenue: Revenue, success_factors: Dict):
        """
        Update agent's learning with revenue generation success
        """
        learning, created = UserAgentLearning.objects.update_or_create(
            user=revenue.user,
            agent_name=revenue.agent.name,
            learning_domain='revenue_optimization',
            defaults={
                'learning_content': {
                    'revenue_generated': float(revenue.amount),
                    'revenue_source': revenue.source_type,
                    'source_platform': success_factors['opportunity_characteristics'].get('platform', 'unknown'),
                    'strategy_used': success_factors['agent_strategy'],
                    'success_factors': success_factors,
                    'timestamp': timezone.now().isoformat()
                },
                'confidence_score': 0.9,  # High confidence - actual revenue
                'learning_source': 'performance_tracking',
                'context_metadata': {
                    'revenue_id': str(revenue.id),
                    'revenue_quality': success_factors.get('revenue_quality'),
                    'time_to_revenue_days': success_factors.get('time_to_revenue')
                }
            }
        )

        # Record success
        if not created:
            learning.record_success()

        logger.info(f"✅ Updated agent learning: {revenue.agent.name} → revenue_optimization")

    def _update_user_revenue_patterns(self, revenue: Revenue, success_factors: Dict):
        """
        Update user's revenue generation patterns
        """
        learning, created = UserAgentLearning.objects.update_or_create(
            user=revenue.user,
            agent_name='SystemIntelligence',
            learning_domain='success_factors',
            defaults={
                'learning_content': {
                    'successful_revenue_type': revenue.source_type,
                    'successful_platforms': [success_factors['opportunity_characteristics'].get('platform', 'unknown')],
                    'average_revenue': float(revenue.amount),
                    'total_revenues': 1,
                    'last_revenue_date': timezone.now().isoformat()
                },
                'confidence_score': 0.8,
                'learning_source': 'success_pattern'
            }
        )

        # Update counts if not created
        if not created and isinstance(learning.learning_content, dict):
            content = learning.learning_content
            content['total_revenues'] = content.get('total_revenues', 0) + 1

            # Update average revenue
            total = content.get('total_revenues', 1)
            current_avg = content.get('average_revenue', 0)
            new_avg = ((current_avg * (total - 1)) + float(revenue.amount)) / total
            content['average_revenue'] = new_avg

            learning.learning_content = content
            learning.save()


# ============================================
# Django Signal Integration
# ============================================

revenue_learning_loop = RevenueAttributionLearningLoop()


@receiver(post_save, sender=Revenue)
def on_revenue_saved(sender, instance, created, **kwargs):
    """
    Signal handler for Revenue model
    Triggers learning loop when revenue is created or completed
    """
    # Only process when revenue is completed (or created)
    if created or instance.status == 'completed':
        try:
            revenue_learning_loop.process_revenue_event(instance)
        except Exception as e:
            logger.error(f"Error in revenue learning loop signal: {e}", exc_info=True)
