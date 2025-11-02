"""
Opportunity and application endpoints
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models_unified_system import Application, Opportunity
from core.models_engagement_metrics import OpportunityInteraction
import json
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quick_apply(request):
    """
    Quick Apply to an opportunity
    POST /api/opportunities/quick-apply/
    Body: {"opportunity_id": "uuid"}
    """
    try:
        data = json.loads(request.body or b"{}") if isinstance(request.body, bytes) else request.data
        opportunity_id = data.get('opportunity_id')

        # Get opportunity
        opportunity = Opportunity.objects.get(id=opportunity_id)

        # Check if already applied
        existing = Application.objects.filter(
            user=request.user,
            opportunity=opportunity
        ).first()

        if existing:
            return Response({
                'success': False,
                'message': 'You have already applied to this opportunity',
                'application_id': str(existing.id)
            }, status=400)

        # Create application
        application = Application.objects.create(
            user=request.user,
            opportunity=opportunity,
            status='submitted',
            cover_letter=data.get('cover_letter', ''),
            resume_url=data.get('resume_url', '')
        )

        # Update opportunity status
        opportunity.status = 'applied'
        opportunity.save()

        # Track interaction in engagement metrics
        OpportunityInteraction.objects.create(
            user=request.user,
            opportunity_id=str(opportunity.id),
            opportunity_title=opportunity.title,
            opportunity_platform=opportunity.source,
            opportunity_salary=opportunity.potential_revenue,
            interaction_type='apply',
            was_personalized=True,
            resulted_in_application=True
        )

        logger.info(f"✅ Application created: {request.user.username} → {opportunity.title}")

        return Response({
            'success': True,
            'message': 'Application submitted successfully!',
            'application': {
                'id': str(application.id),
                'opportunity_title': opportunity.title,
                'status': application.status,
                'created_at': application.created_at.isoformat()
            }
        })

    except Opportunity.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Opportunity not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error creating application: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
