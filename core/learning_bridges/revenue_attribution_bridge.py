"""
Revenue Attribution Learning Bridge
Connects revenue generation events to agent learning system

When revenue is generated, this bridge:
1. Identifies which agent/strategy was responsible
2. Updates agent's learning profile with success
3. Feeds insights to UnifiedLearningPipeline
4. Updates user's revenue generation patterns

Session 1115 batch-9: refactored to inherit from `LearningBridge` ABC.
Proof-of-concept for the broader multi-bridge migration tracked in
AUDIT_FINDINGS.md finding #9. Public `process_revenue_event` kept as a
back-compat shim so the existing `on_revenue_saved` signal handler
keeps working unchanged.
"""

import logging
from typing import Any, Dict, List

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from core.learning_bridges.base import LearningBridge
from core.models_unified_system import Revenue, UserAgentLearning

logger = logging.getLogger(__name__)


class RevenueAttributionLearningLoop(LearningBridge):
    """
    Bidirectional learning loop for revenue attribution.

    First concrete consumer of the `LearningBridge` ABC contract
    (Session 1115 batch-9). The four abstract methods map to the
    original implementation as follows:

      - `process_event(revenue)`     wraps the original
        `process_revenue_event(revenue)` — same logic, now via the ABC
        observability helpers (log_event / log_success / log_error).
      - `_extract_patterns(revenue)` → `_extract_success_factors` (renamed
        in the ABC vocabulary but identical behavior).
      - `_update_learning(patterns)` → calls both
        `_update_agent_learning` and `_update_user_revenue_patterns`,
        which read the Revenue instance out of `patterns['_revenue']`.
      - `_generate_insights(patterns)` → derives human-readable insight
        strings from the success factors. These are returned in the
        `process_event` result dict for downstream pipelines.
    """

    def __init__(self):
        super().__init__(bridge_name='revenue_attribution')

    # ------------------------------------------------------------------
    # ABC contract
    # ------------------------------------------------------------------
    def process_event(self, event_data: Any) -> Dict:
        """Process a Revenue event end-to-end."""
        revenue: Revenue = event_data
        self.log_event(
            f"Processing revenue event: ${revenue.amount} from {revenue.source_type}"
        )
        try:
            patterns = self._extract_patterns(revenue)
            self._update_learning(patterns)
            insights = self._generate_insights(patterns)
            self.log_success(f"Revenue learning loop completed for revenue {revenue.id}")
            return {
                'status': 'ok',
                'revenue_id': str(revenue.id),
                'success_factors': patterns,
                'insights': insights,
            }
        except Exception as e:
            self.log_error(f"Error in revenue learning loop: {e}")
            return {'status': 'error', 'error': str(e)}

    def _extract_patterns(self, event_data: Any) -> Dict:
        """Extract success factors from a Revenue instance."""
        revenue: Revenue = event_data
        factors: Dict[str, Any] = {
            'source_type': revenue.source_type,
            'source_id': str(revenue.source_id) if revenue.source_id else None,
            'amount': float(revenue.amount),
            'currency': revenue.currency if hasattr(revenue, 'currency') else 'USD',
            'time_to_revenue': None,
            'agent_strategy': {},
            'opportunity_characteristics': {},
            # Thread the Revenue instance through so `_update_learning` can
            # use it without breaking the 1-argument ABC contract.
            '_revenue': revenue,
        }

        if (
            hasattr(revenue, 'earned_at') and revenue.earned_at
            and hasattr(revenue, 'created_at') and revenue.created_at
        ):
            time_delta = revenue.earned_at - revenue.created_at
            factors['time_to_revenue'] = time_delta.total_seconds() / 86400  # days

        if hasattr(revenue, 'metadata') and revenue.metadata:
            factors['agent_strategy'] = revenue.metadata.get('strategy', {})
            factors['opportunity_characteristics'] = revenue.metadata.get('opportunity', {})

        if revenue.amount >= 5000:
            factors['revenue_quality'] = 'high'
        elif revenue.amount >= 1000:
            factors['revenue_quality'] = 'medium'
        else:
            factors['revenue_quality'] = 'low'

        return factors

    def _update_learning(self, patterns: Dict) -> None:
        """Update agent + user learning rows from extracted patterns."""
        revenue: Revenue = patterns['_revenue']
        if revenue.agent:
            self._update_agent_learning(revenue, patterns)
        self._update_user_revenue_patterns(revenue, patterns)

    def _generate_insights(self, patterns: Dict) -> List[str]:
        """Derive human-readable insight strings from success factors."""
        insights: List[str] = []
        quality = patterns.get('revenue_quality', 'low')
        amount = patterns.get('amount', 0.0)
        source = patterns.get('source_type', 'unknown')
        insights.append(
            f"{quality}-quality revenue: ${amount:.2f} from {source}"
        )
        ttr = patterns.get('time_to_revenue')
        if ttr is not None:
            insights.append(f"time-to-revenue: {ttr:.1f} days")
        platform = patterns.get('opportunity_characteristics', {}).get('platform')
        if platform:
            insights.append(f"platform attribution: {platform}")
        strategy = patterns.get('agent_strategy', {})
        if strategy:
            insights.append(f"strategy signals: {sorted(strategy.keys())}")
        return insights

    # ------------------------------------------------------------------
    # Bridge-specific helpers (unchanged from pre-refactor implementation)
    # ------------------------------------------------------------------
    def _update_agent_learning(self, revenue: Revenue, success_factors: Dict):
        """Update agent's learning with revenue generation success."""
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
                    'success_factors': {
                        k: v for k, v in success_factors.items() if not k.startswith('_')
                    },
                    'timestamp': timezone.now().isoformat(),
                },
                'confidence_score': 0.9,
                'learning_source': 'performance_tracking',
                'context_metadata': {
                    'revenue_id': str(revenue.id),
                    'revenue_quality': success_factors.get('revenue_quality'),
                    'time_to_revenue_days': success_factors.get('time_to_revenue'),
                },
            },
        )

        if not created:
            learning.record_success()

        logger.info(
            f"✅ Updated agent learning: {revenue.agent.name} → revenue_optimization"
        )

    def _update_user_revenue_patterns(self, revenue: Revenue, success_factors: Dict):
        """Update user's revenue generation patterns."""
        learning, created = UserAgentLearning.objects.update_or_create(
            user=revenue.user,
            agent_name='SystemIntelligence',
            learning_domain='success_factors',
            defaults={
                'learning_content': {
                    'successful_revenue_type': revenue.source_type,
                    'successful_platforms': [
                        success_factors['opportunity_characteristics'].get('platform', 'unknown')
                    ],
                    'average_revenue': float(revenue.amount),
                    'total_revenues': 1,
                    'last_revenue_date': timezone.now().isoformat(),
                },
                'confidence_score': 0.8,
                'learning_source': 'success_pattern',
            },
        )

        if not created and isinstance(learning.learning_content, dict):
            content = learning.learning_content
            content['total_revenues'] = content.get('total_revenues', 0) + 1

            total = content.get('total_revenues', 1)
            current_avg = content.get('average_revenue', 0)
            new_avg = ((current_avg * (total - 1)) + float(revenue.amount)) / total
            content['average_revenue'] = new_avg

            learning.learning_content = content
            learning.save()

    # ------------------------------------------------------------------
    # Back-compat alias used by `on_revenue_saved` signal handler
    # ------------------------------------------------------------------
    def process_revenue_event(self, revenue: Revenue) -> Dict:
        """Back-compat shim — delegates to `process_event`."""
        return self.process_event(revenue)


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
    if created or instance.status == 'completed':
        try:
            revenue_learning_loop.process_revenue_event(instance)
        except Exception as e:
            logger.error(f"Error in revenue learning loop signal: {e}", exc_info=True)
