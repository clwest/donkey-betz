"""
🧠 UNIFIED LEARNING PIPELINE
Cross-domain learning: Sports success → Job matching, Job success → Betting confidence
"""

from django.db import models
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta


class UnifiedLearningPipeline:
    """Apply cross-domain insights across the unified revenue system"""

    def __init__(self):
        self.insights_log = []

    def apply_cross_domain_insights(self, user):
        """Apply learning from one domain to boost performance in others"""
        from core.models import UserAgentLearning
        from intelligence.models import OpportunityTracking, OpportunityType

        insights_applied = []
        top_learnings = UserAgentLearning.objects.filter(
            user=user,
            confidence_score__gte=0.7
        ).order_by('-confidence_score')[:5]

        for learning in top_learnings:
            domain = learning.learning_domain

            # Sports Betting Success → Job Matching Boost
            if 'sports_betting' in domain or 'betting' in domain:
                win_rate = learning.learning_content.get('win_rate', 0)
                total_bets = learning.learning_content.get('total_bets', 0)

                if win_rate >= 0.58 and total_bets >= 20:
                    updated = OpportunityTracking.objects.filter(
                        user=user,
                        opportunity_type=OpportunityType.JOB,
                        status='discovered',
                        opportunity_data__skills__icontains='data'
                    ).update(
                        match_score=models.F('match_score') * 1.15,
                        confidence_score=models.F('confidence_score') * 1.10
                    )

                    if updated > 0:
                        insights_applied.append({
                            'source': 'sports_betting',
                            'target': 'job_matching',
                            'boost': 0.15,
                            'affected_opportunities': updated,
                            'reason': f'User has {win_rate:.0%} sports win rate - strong analytical skills'
                        })

        self.insights_log.extend(insights_applied)
        return insights_applied
