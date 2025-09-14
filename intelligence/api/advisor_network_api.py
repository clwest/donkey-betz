"""
Advisor Network API Views
Exposes endpoints for interacting with 25+ expert advisors
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Avg
import json

from intelligence.models.advisor_network import (
    Advisor, AdvisorCategory, AdvisorCollaboration,
    AdvisorVote, AdvisorRecruitment
)
from intelligence.services.advisor_network_service import AdvisorNetworkService


class AdvisorNetworkViewSet(viewsets.ViewSet):
    """API endpoints for advisor network operations"""

    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = AdvisorNetworkService()

    @action(detail=False, methods=['GET'])
    def network_status(self, request):
        """Get current advisor network status and metrics"""

        status_data = self.service.get_network_status()

        return Response({
            'success': True,
            'data': status_data
        })

    @action(detail=False, methods=['GET'])
    def list_advisors(self, request):
        """List all active advisors with filters"""

        category = request.query_params.get('category')
        trust_level = request.query_params.get('trust_level')
        tier = request.query_params.get('tier')
        online_only = request.query_params.get('online_only', False)

        advisors = Advisor.objects.filter(is_active=True)

        if category:
            advisors = advisors.filter(category__name=category)
        if trust_level:
            advisors = advisors.filter(trust_level=trust_level)
        if tier:
            advisors = advisors.filter(tier=tier)
        if online_only:
            advisors = advisors.filter(is_online=True)

        advisor_data = []
        for advisor in advisors[:50]:  # Limit to 50 for performance
            advisor_data.append({
                'id': advisor.external_id,
                'name': advisor.name,
                'title': advisor.title,
                'bio': advisor.bio,
                'category': advisor.category.name,
                'expertise': advisor.expertise_tags,
                'trust_level': advisor.trust_level,
                'tier': advisor.tier,
                'performance': {
                    'success_rate': float(advisor.success_rate),
                    'roi': float(advisor.roi_percentage),
                    'reputation': float(advisor.reputation_score),
                    'total_decisions': advisor.total_decisions
                },
                'is_online': advisor.is_online,
                'last_seen': advisor.last_seen.isoformat()
            })

        return Response({
            'success': True,
            'count': len(advisor_data),
            'advisors': advisor_data
        })

    @action(detail=False, methods=['POST'])
    def get_recommendations(self, request):
        """Get advisor recommendations for a decision context"""

        context = request.data
        recommendations = self.service.get_advisor_recommendations(context)

        return Response({
            'success': True,
            'recommendations': recommendations
        })

    @action(detail=False, methods=['POST'])
    def create_collaboration(self, request):
        """Create a new multi-advisor collaboration"""

        collaboration_data = request.data
        collaboration_data['creator_id'] = request.user.id

        try:
            collaboration = self.service.create_advisor_collaboration(collaboration_data)

            return Response({
                'success': True,
                'collaboration_id': collaboration.id,
                'message': f'Created collaboration with {collaboration.advisors.count()} advisors'
            })

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def collaborations(self, request):
        """List active collaborations"""

        collaborations = AdvisorCollaboration.objects.filter(
            status__in=['REVIEW', 'VOTING']
        ).order_by('-created_at')[:20]

        collab_data = []
        for collab in collaborations:
            collab_data.append({
                'id': collab.id,
                'title': collab.title,
                'description': collab.description,
                'domain': collab.domain,
                'status': collab.status,
                'advisors_count': collab.advisors.count(),
                'votes_count': collab.votes.count(),
                'consensus': float(collab.consensus_score),
                'confidence': float(collab.confidence_score),
                'diversity': float(collab.diversity_score),
                'created_at': collab.created_at.isoformat(),
                'deadline': collab.deadline.isoformat() if collab.deadline else None
            })

        return Response({
            'success': True,
            'collaborations': collab_data
        })

    @action(detail=False, methods=['POST'])
    def submit_vote(self, request):
        """Submit an advisor vote on a collaboration"""

        vote_data = request.data

        try:
            vote = self.service.process_advisor_vote(vote_data)

            return Response({
                'success': True,
                'vote_id': vote.id,
                'collaboration_status': vote.collaboration.status
            })

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def categories(self, request):
        """List all advisor categories with counts"""

        categories = AdvisorCategory.objects.all()

        category_data = []
        for category in categories:
            active_count = category.advisors.filter(is_active=True).count()
            verified_count = category.advisors.filter(
                is_active=True,
                trust_level__in=['VERIFIED', 'HIGH']
            ).count()

            category_data.append({
                'name': category.name,
                'display_name': category.display_name,
                'description': category.description,
                'icon': category.icon,
                'color': category.color,
                'active_advisors': active_count,
                'verified_advisors': verified_count,
                'target_advisors': self.service.ADVISOR_TARGETS.get(category.name, {}).get('target', 0)
            })

        return Response({
            'success': True,
            'categories': category_data
        })

    @action(detail=True, methods=['GET'])
    def advisor_detail(self, request, pk=None):
        """Get detailed information about a specific advisor"""

        try:
            advisor = Advisor.objects.get(external_id=pk)

            # Get recent verifications
            verifications = advisor.verifications.filter(is_valid=True)[:5]
            verification_data = [
                {
                    'type': v.get_verification_type_display(),
                    'platform': v.platform,
                    'roi': float(v.verified_roi) if v.verified_roi else None,
                    'win_rate': float(v.verified_win_rate) if v.verified_win_rate else None,
                    'date': v.verification_date.isoformat()
                }
                for v in verifications
            ]

            # Get recent collaborations
            recent_collabs = advisor.collaborations.order_by('-created_at')[:5]
            collab_data = [
                {
                    'title': c.title,
                    'domain': c.domain,
                    'status': c.status,
                    'consensus': float(c.consensus_score)
                }
                for c in recent_collabs
            ]

            return Response({
                'success': True,
                'advisor': {
                    'id': advisor.external_id,
                    'name': advisor.name,
                    'title': advisor.title,
                    'bio': advisor.bio,
                    'category': advisor.category.name,
                    'expertise': advisor.expertise_tags,
                    'trust_level': advisor.trust_level,
                    'tier': advisor.tier,
                    'performance': {
                        'success_rate': float(advisor.success_rate),
                        'roi': float(advisor.roi_percentage),
                        'reputation': float(advisor.reputation_score),
                        'total_decisions': advisor.total_decisions,
                        'domain_performance': advisor.domain_performance
                    },
                    'fees': {
                        'base_fee': float(advisor.base_fee),
                        'performance_fee': float(advisor.performance_fee_percentage)
                    },
                    'verifications': verification_data,
                    'recent_collaborations': collab_data,
                    'is_online': advisor.is_online,
                    'last_seen': advisor.last_seen.isoformat(),
                    'joined': advisor.joined_date.isoformat()
                }
            })

        except Advisor.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Advisor not found'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['GET'])
    def recruitment_pipeline(self, request):
        """Get recruitment pipeline status"""

        report = self.service.generate_recruitment_report()

        return Response({
            'success': True,
            'report': report
        })

    @action(detail=False, methods=['POST'])
    def recruit_advisor(self, request):
        """Add a new advisor to recruitment pipeline"""

        recruitment_data = request.data

        try:
            recruitment = self.service.recruit_advisor(recruitment_data)

            return Response({
                'success': True,
                'recruitment_id': recruitment.id,
                'message': f'Added {recruitment.name} to recruitment pipeline'
            })

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def verify_advisor(self, request):
        """Submit advisor verification"""

        advisor_id = request.data.get('advisor_id')
        verification_data = request.data.get('verification')

        try:
            verification = self.service.verify_advisor_track_record(
                advisor_id,
                verification_data
            )

            return Response({
                'success': True,
                'verification_id': verification.id,
                'advisor_trust_level': verification.advisor.trust_level
            })

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def top_performers(self, request):
        """Get top performing advisors across categories"""

        days = int(request.query_params.get('days', 30))
        limit = int(request.query_params.get('limit', 10))

        # Get top performers
        cutoff_date = timezone.now() - timezone.timedelta(days=days)

        top_advisors = Advisor.objects.filter(
            is_active=True,
            trust_level__in=['VERIFIED', 'HIGH'],
            last_seen__gte=cutoff_date,
            total_decisions__gte=20
        ).order_by('-success_rate', '-roi_percentage')[:limit]

        advisor_data = []
        for advisor in top_advisors:
            advisor_data.append({
                'id': advisor.external_id,
                'name': advisor.name,
                'title': advisor.title,
                'category': advisor.category.name,
                'tier': advisor.tier,
                'performance': {
                    'success_rate': float(advisor.success_rate),
                    'roi': float(advisor.roi_percentage),
                    'reputation': float(advisor.reputation_score),
                    'total_decisions': advisor.total_decisions
                },
                'recent_activity': advisor.last_seen.isoformat()
            })

        return Response({
            'success': True,
            'period_days': days,
            'top_performers': advisor_data
        })