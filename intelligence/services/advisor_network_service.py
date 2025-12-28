"""
Advisor Network Service - Managing 25+ Expert Advisors
Implements recruitment, verification, and collaboration orchestration
"""

from typing import Dict, List
from datetime import timedelta
from django.db.models import Avg
from django.utils import timezone
from django.core.cache import cache
import logging

from intelligence.models.advisor_network import (
    Advisor, AdvisorCategory, AdvisorSpecialization,
    AdvisorVerification, AdvisorCollaboration, AdvisorVote,
    AdvisorRecruitment
)

logger = logging.getLogger(__name__)


class AdvisorNetworkService:
    """Service for managing the scaled advisor network"""

    # Target advisor counts by category
    ADVISOR_TARGETS = {
        'SPORTS_BETTING': {
            'target': 8,
            'specializations': [
                'NBA Line Movement Specialist',
                'NFL Injury Impact Analyst',
                'MLB Pitching Matchup Expert',
                'Soccer Value Betting Specialist',
                'Tennis Live Betting Expert',
                'College Basketball Insider',
                'MMA/Boxing Odds Analyst',
                'Props & Player Performance Expert'
            ]
        },
        'CRYPTO': {
            'target': 7,
            'specializations': [
                'DeFi Yield Strategist',
                'Whale Movement Tracker',
                'NFT Market Analyst',
                'Layer 2 Specialist',
                'Stablecoin Arbitrage Expert',
                'Mining & Staking Optimizer',
                'Crypto Options Trader'
            ]
        },
        'OPTIONS': {
            'target': 5,
            'specializations': [
                'Volatility Crush Specialist',
                'Earnings Play Expert',
                'Greeks Management Pro',
                'Credit Spread Strategist',
                'Weekly Options Scalper'
            ]
        },
        'REAL_ESTATE': {
            'target': 5,
            'specializations': [
                'Austin Market Timing Expert',
                'REITs Analyst',
                'Commercial Property Specialist',
                'Rental Income Optimizer',
                'Real Estate Crowdfunding Expert'
            ]
        }
    }

    def __init__(self):
        self.cache_timeout = 300  # 5 minutes

    def get_network_status(self) -> Dict:
        """Get current advisor network status vs targets"""

        status = {
            'total_advisors': 0,
            'target_advisors': 25,
            'categories': {},
            'verification_pending': 0,
            'online_now': 0,
            'average_success_rate': 0.0,
            'top_performers': []
        }

        # Get counts by category
        for category_key, targets in self.ADVISOR_TARGETS.items():
            try:
                category = AdvisorCategory.objects.get(name=category_key)
                advisors = Advisor.objects.filter(
                    category=category,
                    is_active=True
                )

                verified = advisors.filter(trust_level__in=['VERIFIED', 'HIGH']).count()
                total = advisors.count()

                status['categories'][category_key] = {
                    'current': total,
                    'verified': verified,
                    'target': targets['target'],
                    'completion_percentage': (total / targets['target']) * 100,
                    'specializations_covered': self._get_specialization_coverage(category)
                }

                status['total_advisors'] += total

            except AdvisorCategory.DoesNotExist:
                logger.warning(f"Category {category_key} not found")

        # Overall metrics
        all_advisors = Advisor.objects.filter(is_active=True)
        status['verification_pending'] = all_advisors.filter(trust_level='PENDING').count()
        status['online_now'] = all_advisors.filter(is_online=True).count()

        # Average success rate
        avg_success = all_advisors.aggregate(Avg('success_rate'))['success_rate__avg']
        status['average_success_rate'] = round(avg_success or 0, 4)

        # Top performers
        top_advisors = all_advisors.filter(
            trust_level__in=['VERIFIED', 'HIGH'],
            total_decisions__gte=20
        ).order_by('-success_rate')[:5]

        status['top_performers'] = [
            {
                'name': advisor.name,
                'title': advisor.title,
                'category': advisor.category.name,
                'success_rate': float(advisor.success_rate),
                'roi': float(advisor.roi_percentage),
                'tier': advisor.tier
            }
            for advisor in top_advisors
        ]

        return status

    def _get_specialization_coverage(self, category: AdvisorCategory) -> Dict:
        """Check which specializations are covered"""

        target_specs = self.ADVISOR_TARGETS.get(category.name, {}).get('specializations', [])
        covered_specs = AdvisorSpecialization.objects.filter(
            category=category,
            advisors__is_active=True
        ).distinct().values_list('name', flat=True)

        return {
            'total_needed': len(target_specs),
            'covered': len(covered_specs),
            'missing': [spec for spec in target_specs if spec not in covered_specs]
        }

    def recruit_advisor(self, recruitment_data: Dict) -> AdvisorRecruitment:
        """Add a new advisor to the recruitment pipeline"""

        recruitment = AdvisorRecruitment.objects.create(
            name=recruitment_data['name'],
            category_id=recruitment_data['category_id'],
            specializations=recruitment_data.get('specializations', []),
            email=recruitment_data.get('email', ''),
            linkedin_url=recruitment_data.get('linkedin_url', ''),
            twitter_handle=recruitment_data.get('twitter_handle', ''),
            source=recruitment_data.get('source', 'Manual'),
            verified_track_record=recruitment_data.get('track_record', {}),
            evaluation_notes=recruitment_data.get('notes', '')
        )

        logger.info(f"Added {recruitment.name} to recruitment pipeline")
        return recruitment

    def verify_advisor_track_record(self, advisor_id: int, verification_data: Dict) -> AdvisorVerification:
        """Verify an advisor's track record"""

        advisor = Advisor.objects.get(id=advisor_id)

        verification = AdvisorVerification.objects.create(
            advisor=advisor,
            verification_type=verification_data['type'],
            platform=verification_data.get('platform', ''),
            record_url=verification_data.get('url', ''),
            performance_data=verification_data.get('performance_data', {}),
            verified_roi=verification_data.get('roi'),
            verified_win_rate=verification_data.get('win_rate'),
            verified_picks_count=verification_data.get('picks_count', 0),
            time_period_days=verification_data.get('period_days', 0),
            notes=verification_data.get('notes', '')
        )

        # Update advisor trust level based on verifications
        self._update_advisor_trust_level(advisor)

        return verification

    def _update_advisor_trust_level(self, advisor: Advisor):
        """Update advisor trust level based on verifications"""

        verifications = advisor.verifications.filter(is_valid=True)

        if verifications.count() >= 3:
            # Multiple verifications with good performance
            avg_win_rate = verifications.aggregate(
                Avg('verified_win_rate')
            )['verified_win_rate__avg']

            if avg_win_rate and avg_win_rate >= 0.65:
                advisor.trust_level = 'VERIFIED'
            elif avg_win_rate and avg_win_rate >= 0.60:
                advisor.trust_level = 'HIGH'
            else:
                advisor.trust_level = 'MEDIUM'

        elif verifications.count() >= 1:
            advisor.trust_level = 'MEDIUM'

        # Auto-calculate tier
        advisor.tier = advisor.calculate_tier()
        advisor.save()

    def create_advisor_collaboration(self, collaboration_data: Dict) -> AdvisorCollaboration:
        """Create a new multi-advisor collaboration"""

        collaboration = AdvisorCollaboration.objects.create(
            title=collaboration_data['title'],
            description=collaboration_data['description'],
            domain=collaboration_data['domain'],
            entity=collaboration_data['entity'],
            creator_id=collaboration_data['creator_id'],
            deadline=collaboration_data.get('deadline')
        )

        # Add advisors based on expertise
        advisors = self.select_advisors_for_domain(
            domain=collaboration_data['domain'],
            count=collaboration_data.get('advisor_count', 5)
        )

        collaboration.advisors.set(advisors)

        # Calculate initial diversity score
        self._calculate_collaboration_diversity(collaboration)

        return collaboration

    def select_advisors_for_domain(self, domain: str, count: int = 5) -> List[Advisor]:
        """Select best advisors for a specific domain"""

        # Try cache first
        cache_key = f"advisors_domain_{domain}_{count}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        advisors = []

        # Map domain to categories
        domain_category_map = {
            'SPORTS': ['SPORTS_BETTING'],
            'CRYPTO': ['CRYPTO'],
            'OPTIONS': ['OPTIONS'],
            'REAL_ESTATE': ['REAL_ESTATE'],
            'STOCKS': ['STOCKS', 'OPTIONS'],
            'FOREX': ['FOREX'],
        }

        categories = domain_category_map.get(domain, [])

        # Get top advisors from relevant categories
        base_query = Advisor.objects.filter(
            is_active=True,
            trust_level__in=['VERIFIED', 'HIGH', 'MEDIUM']
        )

        if categories:
            base_query = base_query.filter(category__name__in=categories)

        # Score advisors
        scored_advisors = []
        for advisor in base_query:
            score = self._calculate_advisor_score(advisor, domain)
            scored_advisors.append((score, advisor))

        # Sort by score and take top N
        scored_advisors.sort(key=lambda x: x[0], reverse=True)
        advisors = [advisor for score, advisor in scored_advisors[:count]]

        # Cache for 5 minutes
        cache.set(cache_key, advisors, self.cache_timeout)

        return advisors

    def _calculate_advisor_score(self, advisor: Advisor, domain: str) -> float:
        """Calculate advisor score for a specific domain"""

        score = 0.0

        # Base score from overall success rate
        score += float(advisor.success_rate) * 40

        # Domain-specific performance
        if domain in advisor.domain_performance:
            domain_rate = advisor.domain_performance[domain].get('rate', 0)
            score += domain_rate * 30

        # Reputation and trust
        score += float(advisor.reputation_score) * 10

        if advisor.trust_level == 'VERIFIED':
            score += 10
        elif advisor.trust_level == 'HIGH':
            score += 7
        elif advisor.trust_level == 'MEDIUM':
            score += 4

        # Recent activity bonus
        if advisor.last_seen > timezone.now() - timedelta(hours=24):
            score += 5

        # Experience bonus
        if advisor.total_decisions >= 100:
            score += 5
        elif advisor.total_decisions >= 50:
            score += 3

        return score

    def _calculate_collaboration_diversity(self, collaboration: AdvisorCollaboration):
        """Calculate diversity score for advisor collaboration"""

        advisors = collaboration.advisors.all()

        if not advisors:
            collaboration.diversity_score = 0.0
            collaboration.save()
            return

        # Category diversity
        categories = advisors.values_list('category__name', flat=True).distinct()
        category_diversity = len(categories) / len(self.ADVISOR_TARGETS)

        # Specialization diversity
        specs = []
        for advisor in advisors:
            specs.extend(advisor.expertise_tags)
        spec_diversity = len(set(specs)) / max(len(specs), 1)

        # Experience diversity (mix of tiers)
        tiers = advisors.values_list('tier', flat=True).distinct()
        tier_diversity = len(tiers) / 5  # 5 total tiers

        # Calculate weighted diversity
        diversity = (
            category_diversity * 0.3 +
            spec_diversity * 0.4 +
            tier_diversity * 0.3
        )

        collaboration.diversity_score = round(diversity, 4)
        collaboration.save()

    def process_advisor_vote(self, vote_data: Dict) -> AdvisorVote:
        """Process an advisor's vote on a collaboration"""

        vote = AdvisorVote.objects.create(
            collaboration_id=vote_data['collaboration_id'],
            advisor_id=vote_data['advisor_id'],
            vote=vote_data['vote'],
            confidence=vote_data['confidence'],
            reasoning=vote_data['reasoning'],
            stake_amount=vote_data.get('stake_amount', 0)
        )

        # Update collaboration consensus
        collaboration = vote.collaboration
        collaboration.calculate_consensus()

        # Check if voting is complete
        total_advisors = collaboration.advisors.count()
        total_votes = collaboration.votes.count()

        if total_votes >= total_advisors * 0.8:  # 80% have voted
            collaboration.status = 'DECIDED'
            collaboration.decision_date = timezone.now()
            collaboration.save()

        return vote

    def get_advisor_recommendations(self, context: Dict) -> List[Dict]:
        """Get advisor recommendations for a specific decision context"""

        domain = context.get('domain', 'GENERAL')
        urgency = context.get('urgency', 'MEDIUM')
        stake_size = context.get('stake_size', 1000)

        # Select advisors
        advisors = self.select_advisors_for_domain(domain, count=7)

        recommendations = []
        for advisor in advisors[:5]:  # Top 5 recommendations
            recommendation = {
                'advisor': {
                    'id': advisor.external_id,
                    'name': advisor.name,
                    'title': advisor.title,
                    'tier': advisor.tier,
                    'trust_level': advisor.trust_level
                },
                'relevance_score': self._calculate_advisor_score(advisor, domain),
                'availability': 'online' if advisor.is_online else 'offline',
                'last_seen': advisor.last_seen.isoformat(),
                'performance': {
                    'success_rate': float(advisor.success_rate),
                    'roi': float(advisor.roi_percentage),
                    'total_decisions': advisor.total_decisions
                },
                'specializations': advisor.expertise_tags,
                'fee_estimate': self._calculate_fee_estimate(advisor, stake_size)
            }

            # Add domain-specific performance if available
            if domain in advisor.domain_performance:
                recommendation['domain_performance'] = advisor.domain_performance[domain]

            recommendations.append(recommendation)

        return recommendations

    def _calculate_fee_estimate(self, advisor: Advisor, stake_size: float) -> Dict:
        """Calculate estimated fees for an advisor"""

        base_fee = float(advisor.base_fee)
        performance_fee = float(advisor.performance_fee_percentage) / 100

        return {
            'base_fee': base_fee,
            'performance_fee_percentage': float(advisor.performance_fee_percentage),
            'estimated_total': base_fee + (stake_size * performance_fee * 0.1)  # Assume 10% return
        }

    def generate_recruitment_report(self) -> Dict:
        """Generate advisor recruitment status report"""

        report = {
            'timestamp': timezone.now().isoformat(),
            'network_status': self.get_network_status(),
            'recruitment_pipeline': {},
            'verification_backlog': 0,
            'recommendations': []
        }

        # Recruitment pipeline
        pipeline = AdvisorRecruitment.objects.exclude(
            status__in=['ACTIVE', 'REJECTED', 'WITHDRAWN']
        )

        report['recruitment_pipeline'] = {
            'identified': pipeline.filter(status='IDENTIFIED').count(),
            'contacted': pipeline.filter(status='CONTACTED').count(),
            'evaluating': pipeline.filter(status='EVALUATING').count(),
            'negotiating': pipeline.filter(status='NEGOTIATING').count(),
            'onboarding': pipeline.filter(status='ONBOARDING').count(),
            'total_in_pipeline': pipeline.count()
        }

        # Verification backlog
        report['verification_backlog'] = Advisor.objects.filter(
            trust_level='PENDING'
        ).count()

        # Recommendations for recruitment focus
        for category_key, targets in self.ADVISOR_TARGETS.items():
            current = report['network_status']['categories'].get(category_key, {})
            if current.get('current', 0) < targets['target']:
                shortage = targets['target'] - current.get('current', 0)
                report['recommendations'].append({
                    'category': category_key,
                    'shortage': shortage,
                    'priority': 'HIGH' if shortage >= 3 else 'MEDIUM',
                    'missing_specializations': current.get('specializations_covered', {}).get('missing', [])
                })

        return report