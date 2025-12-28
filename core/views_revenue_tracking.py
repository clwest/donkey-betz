"""
Revenue Tracking Views
Handles revenue tracking and reporting for the unified platform
"""

from django.views import View
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from datetime import timedelta
import json

from .models import Revenue


@method_decorator(login_required, name='dispatch')
class RevenueStatsView(View):
    """Get comprehensive revenue statistics for the user"""

    def get(self, request):
        """Return revenue statistics"""
        user = request.user

        # Get time ranges
        today = timezone.now().date()
        this_week = today - timedelta(days=7)
        this_month = today - timedelta(days=30)

        # Calculate statistics
        stats = {
            'total_revenue': {
                'all': Revenue.get_user_total(user),
                'potential': Revenue.get_user_total(user, 'potential'),
                'pending': Revenue.get_user_total(user, 'pending'),
                'confirmed': Revenue.get_user_total(user, 'confirmed'),
                'received': Revenue.get_user_total(user, 'received'),
            },
            'time_based': {
                'today': Revenue.objects.filter(
                    user=user,
                    created_at__date=today
                ).aggregate(total=Sum('amount'))['total'] or 0,
                'this_week': Revenue.objects.filter(
                    user=user,
                    created_at__gte=this_week
                ).aggregate(total=Sum('amount'))['total'] or 0,
                'this_month': Revenue.objects.filter(
                    user=user,
                    created_at__gte=this_month
                ).aggregate(total=Sum('amount'))['total'] or 0,
            },
            'by_source': Revenue.objects.filter(user=user).values('source').annotate(
                total=Sum('amount'),
                count=Count('id')
            ),
            'recent_applications': Revenue.objects.filter(
                user=user
            ).order_by('-created_at')[:5].values(
                'opportunity_title',
                'company',
                'amount',
                'status',
                'created_at'
            ),
            'success_rate': self._calculate_success_rate(user),
            'average_amount': Revenue.objects.filter(
                user=user
            ).aggregate(avg=Avg('amount'))['avg'] or 0,
        }

        return JsonResponse(stats)

    def _calculate_success_rate(self, user):
        """Calculate application success rate"""
        total = Revenue.objects.filter(user=user).count()
        if total == 0:
            return 0

        successful = Revenue.objects.filter(
            user=user,
            status__in=['confirmed', 'received']
        ).count()

        return (successful / total) * 100


@method_decorator(login_required, name='dispatch')
class TrackRevenueView(View):
    """Track new revenue from various sources"""

    def post(self, request):
        """Create a new revenue record"""
        try:
            data = json.loads(request.body or b"{}")

            # Create revenue record
            revenue = Revenue.objects.create(
                user=request.user,
                amount=data.get('amount', 0),
                source=data.get('source', 'other'),
                status=data.get('status', 'potential'),
                opportunity_id=data.get('opportunity_id', ''),
                opportunity_title=data.get('opportunity_title', ''),
                company=data.get('company', ''),
                description=data.get('description', ''),
                spider_source=data.get('spider_source', ''),
                agent_involved=data.get('agent_involved', ''),
                match_score=data.get('match_score', 0.5),
                application_date=timezone.now() if data.get('source') == 'quick_apply' else None
            )

            # Update WebSocket consumers with new revenue
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'revenue_dashboard_{request.user.id}',
                {
                    'type': 'revenue_update',
                    'revenue': {
                        'id': str(revenue.id),
                        'amount': float(revenue.amount),
                        'source': revenue.source,
                        'status': revenue.status,
                        'title': revenue.opportunity_title,
                        'company': revenue.company,
                        'created_at': revenue.created_at.isoformat()
                    }
                }
            )

            return JsonResponse({
                'success': True,
                'revenue_id': str(revenue.id),
                'message': 'Revenue tracked successfully'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


@method_decorator(login_required, name='dispatch')
class UpdateRevenueStatusView(View):
    """Update the status of a revenue record"""

    def post(self, request, revenue_id):
        """Update revenue status"""
        try:
            data = json.loads(request.body or b"{}")
            new_status = data.get('status')

            if not new_status:
                return JsonResponse({
                    'success': False,
                    'error': 'Status is required'
                }, status=400)

            # Get and update revenue
            revenue = Revenue.objects.get(id=revenue_id, user=request.user)
            revenue.status = new_status

            # Update dates based on status
            if new_status == 'confirmed':
                revenue.confirmation_date = timezone.now()
            elif new_status == 'received':
                revenue.payment_date = timezone.now()

            revenue.save()

            # Broadcast update
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'revenue_dashboard_{request.user.id}',
                {
                    'type': 'revenue_status_update',
                    'revenue_id': str(revenue_id),
                    'new_status': new_status,
                    'amount': float(revenue.amount)
                }
            )

            return JsonResponse({
                'success': True,
                'message': f'Revenue status updated to {new_status}'
            })

        except Revenue.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Revenue record not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


@method_decorator(login_required, name='dispatch')
class RevenueHistoryView(View):
    """Get detailed revenue history with filtering"""

    def get(self, request):
        """Return paginated revenue history"""
        # Get query parameters
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        status_filter = request.GET.get('status', None)
        source_filter = request.GET.get('source', None)
        date_from = request.GET.get('date_from', None)
        date_to = request.GET.get('date_to', None)

        # Build query
        query = Revenue.objects.filter(user=request.user)

        if status_filter:
            query = query.filter(status=status_filter)
        if source_filter:
            query = query.filter(source=source_filter)
        if date_from:
            query = query.filter(created_at__gte=date_from)
        if date_to:
            query = query.filter(created_at__lte=date_to)

        # Get total count
        total = query.count()

        # Paginate
        offset = (page - 1) * per_page
        revenues = query.order_by('-created_at')[offset:offset + per_page]

        # Format response
        revenue_data = []
        for revenue in revenues:
            revenue_data.append({
                'id': str(revenue.id),
                'amount': float(revenue.amount),
                'source': revenue.source,
                'status': revenue.status,
                'opportunity_title': revenue.opportunity_title,
                'company': revenue.company,
                'description': revenue.description,
                'spider_source': revenue.spider_source,
                'agent_involved': revenue.agent_involved,
                'match_score': revenue.match_score,
                'application_date': revenue.application_date.isoformat() if revenue.application_date else None,
                'confirmation_date': revenue.confirmation_date.isoformat() if revenue.confirmation_date else None,
                'payment_date': revenue.payment_date.isoformat() if revenue.payment_date else None,
                'created_at': revenue.created_at.isoformat(),
            })

        return JsonResponse({
            'revenues': revenue_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })


# Export views for URL configuration
revenue_stats_view = RevenueStatsView.as_view()
track_revenue_view = TrackRevenueView.as_view()
update_revenue_status_view = UpdateRevenueStatusView.as_view()
revenue_history_view = RevenueHistoryView.as_view()