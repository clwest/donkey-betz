"""
Revenue tracking endpoints
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models_unified_system import Revenue, Agent
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import timedelta
import json
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_revenue(request):
    """
    Manual revenue entry
    POST /api/revenue/create/
    Body: {
        "amount": 1500,
        "source_type": "freelance",
        "description": "Project completed",
        "status": "completed"
    }
    """
    try:
        data = json.loads(request.body) if isinstance(request.body, bytes) else request.data

        # Get agent if specified
        agent = None
        if data.get('agent_id'):
            agent = Agent.objects.get(id=data['agent_id'])

        revenue = Revenue.objects.create(
            user=request.user,
            source_type=data.get('source_type', 'manual'),
            source_id=data.get('source_id', ''),
            agent=agent,
            amount=data.get('amount'),
            currency=data.get('currency', 'USD'),
            status=data.get('status', 'completed'),
            description=data.get('description', ''),
            earned_at=timezone.now(),
            paid_at=timezone.now() if data.get('status') == 'completed' else None,
            metadata=data.get('metadata', {})
        )

        logger.info(f"✅ Revenue created: ${revenue.amount} for {request.user.username}")

        return Response({
            'success': True,
            'message': 'Revenue created successfully',
            'revenue': {
                'id': str(revenue.id),
                'amount': float(revenue.amount),
                'source_type': revenue.source_type,
                'status': revenue.status,
                'created_at': revenue.created_at.isoformat()
            }
        })

    except Exception as e:
        logger.error(f"Error creating revenue: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_revenue_summary(request):
    """
    Get revenue summary for user
    GET /api/revenue/summary/?days=30
    """
    try:
        days = int(request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        revenues = Revenue.objects.filter(
            user=request.user,
            created_at__gte=start_date
        )

        summary = revenues.aggregate(
            total_revenue=Sum('amount'),
            total_count=Count('id'),
            completed_revenue=Sum('amount', filter=Q(status='completed')),
            pending_revenue=Sum('amount', filter=Q(status='pending'))
        )

        by_source = revenues.values('source_type').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')

        return Response({
            'success': True,
            'summary': {
                'total_revenue': float(summary['total_revenue'] or 0),
                'completed_revenue': float(summary['completed_revenue'] or 0),
                'pending_revenue': float(summary['pending_revenue'] or 0),
                'total_count': summary['total_count'],
                'by_source': [
                    {
                        'source_type': item['source_type'],
                        'total': float(item['total']),
                        'count': item['count']
                    }
                    for item in by_source
                ]
            }
        })

    except Exception as e:
        logger.error(f"Error getting revenue summary: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
