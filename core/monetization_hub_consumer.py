"""
Monetization Hub WebSocket Consumer
===================================
Real-time revenue tracking and earnings monitoring
"""

import json
import logging
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.db.models import Sum, Count, Q
from django.utils import timezone

logger = logging.getLogger(__name__)


class MonetizationHubConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for Monetization Hub
    Tracks real earnings, payment status, and revenue metrics
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.room_group_name = None
        self.revenue_update_task = None

    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope.get('user', AnonymousUser())

        if isinstance(self.user, AnonymousUser):
            await self.close()
            return

        self.room_group_name = f'monetization_hub_{self.user.id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send initial revenue data
        await self.send_revenue_summary()

        # Start periodic updates
        self.revenue_update_task = asyncio.create_task(self.stream_revenue_updates())

        logger.info(f"✅ Monetization Hub WebSocket connected for user {self.user.username}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        if self.revenue_update_task:
            self.revenue_update_task.cancel()

        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

        logger.info(f"Monetization Hub WebSocket disconnected")

    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'refresh':
                await self.send_revenue_summary()
            elif action == 'get_transactions':
                await self.send_transaction_history(data.get('filters', {}))
            elif action == 'get_analytics':
                await self.send_revenue_analytics()
            elif action == 'withdraw':
                await self.handle_withdrawal(data)
            elif action == 'get_payment_methods':
                await self.send_payment_methods()

        except json.JSONDecodeError:
            await self.send_error('Invalid JSON')
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send_error(str(e))

    async def send_revenue_summary(self):
        """Send comprehensive revenue summary"""
        summary = await self.get_revenue_data()

        await self.send(text_data=json.dumps({
            'type': 'revenue_summary',
            'data': summary
        }))

    @database_sync_to_async
    def get_revenue_data(self) -> Dict[str, Any]:
        """Get revenue data from database"""
        from core.models import JobApplication, Revenue, WithdrawalRequest

        # Calculate total earnings
        total_earned = Revenue.objects.filter(
            user=self.user,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        # Calculate pending earnings
        pending_earned = Revenue.objects.filter(
            user=self.user,
            status='pending'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        # Calculate available balance (completed - withdrawn)
        withdrawn = WithdrawalRequest.objects.filter(
            user=self.user,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        available_balance = total_earned - withdrawn

        # Get recent earnings (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_earnings = Revenue.objects.filter(
            user=self.user,
            created_at__gte=thirty_days_ago,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        # Get active projects count
        active_projects = JobApplication.objects.filter(
            user=self.user,
            status__in=['in_progress', 'under_review']
        ).count()

        # Get completed projects count
        completed_projects = JobApplication.objects.filter(
            user=self.user,
            status='offer_accepted'
        ).count()

        # Calculate success rate
        total_applications = JobApplication.objects.filter(user=self.user).count()
        success_rate = (completed_projects / total_applications * 100) if total_applications > 0 else 0

        # Get recent transactions
        recent_transactions = []
        for revenue in Revenue.objects.filter(user=self.user).order_by('-created_at')[:5]:
            recent_transactions.append({
                'id': str(revenue.id),
                'type': revenue.revenue_type,
                'amount': float(revenue.amount),
                'status': revenue.status,
                'date': revenue.created_at.isoformat(),
                'description': revenue.description,
                'source': revenue.source_platform
            })

        return {
            'total_earned': float(total_earned),
            'pending_earnings': float(pending_earned),
            'available_balance': float(available_balance),
            'withdrawn': float(withdrawn),
            'recent_earnings': float(recent_earnings),
            'active_projects': active_projects,
            'completed_projects': completed_projects,
            'success_rate': round(success_rate, 1),
            'recent_transactions': recent_transactions,
            'currency': 'USD',
            'last_updated': datetime.now().isoformat()
        }

    async def send_transaction_history(self, filters: Dict[str, Any]):
        """Send filtered transaction history"""
        transactions = await self.get_transaction_history(filters)

        await self.send(text_data=json.dumps({
            'type': 'transaction_history',
            'data': {
                'transactions': transactions,
                'total': len(transactions),
                'filters': filters
            }
        }))

    @database_sync_to_async
    def get_transaction_history(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get filtered transaction history"""
        from core.models import Revenue

        queryset = Revenue.objects.filter(user=self.user)

        # Apply filters
        if filters.get('status'):
            queryset = queryset.filter(status=filters['status'])

        if filters.get('type'):
            queryset = queryset.filter(revenue_type=filters['type'])

        if filters.get('start_date'):
            start_date = datetime.fromisoformat(filters['start_date'])
            queryset = queryset.filter(created_at__gte=start_date)

        if filters.get('end_date'):
            end_date = datetime.fromisoformat(filters['end_date'])
            queryset = queryset.filter(created_at__lte=end_date)

        transactions = []
        for revenue in queryset.order_by('-created_at')[:50]:  # Limit to 50
            transactions.append({
                'id': str(revenue.id),
                'type': revenue.revenue_type,
                'amount': float(revenue.amount),
                'status': revenue.status,
                'date': revenue.created_at.isoformat(),
                'description': revenue.description,
                'source': revenue.source_platform,
                'job_id': str(revenue.source_job.id) if revenue.source_job else None
            })

        return transactions

    async def send_revenue_analytics(self):
        """Send revenue analytics data"""
        analytics = await self.get_revenue_analytics()

        await self.send(text_data=json.dumps({
            'type': 'revenue_analytics',
            'data': analytics
        }))

    @database_sync_to_async
    def get_revenue_analytics(self) -> Dict[str, Any]:
        """Generate revenue analytics"""
        from core.models import Revenue, JobApplication
        from django.db.models import Sum, Count, Avg
        from django.db.models.functions import TruncMonth, TruncWeek

        # Monthly revenue trend (last 6 months)
        six_months_ago = timezone.now() - timedelta(days=180)
        monthly_revenue = Revenue.objects.filter(
            user=self.user,
            created_at__gte=six_months_ago,
            status='completed'
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('month')

        monthly_data = []
        for item in monthly_revenue:
            monthly_data.append({
                'month': item['month'].isoformat() if item['month'] else '',
                'revenue': float(item['total']) if item['total'] else 0,
                'projects': item['count']
            })

        # Weekly revenue (last 8 weeks)
        eight_weeks_ago = timezone.now() - timedelta(weeks=8)
        weekly_revenue = Revenue.objects.filter(
            user=self.user,
            created_at__gte=eight_weeks_ago,
            status='completed'
        ).annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            total=Sum('amount')
        ).order_by('week')

        weekly_data = []
        for item in weekly_revenue:
            weekly_data.append({
                'week': item['week'].isoformat() if item['week'] else '',
                'revenue': float(item['total']) if item['total'] else 0
            })

        # Revenue by platform
        platform_revenue = Revenue.objects.filter(
            user=self.user,
            status='completed'
        ).values('source_platform').annotate(
            total=Sum('amount'),
            count=Count('id')
        )

        platform_data = []
        for item in platform_revenue:
            platform_data.append({
                'platform': item['source_platform'] or 'Unknown',
                'revenue': float(item['total']) if item['total'] else 0,
                'projects': item['count']
            })

        # Average project value
        avg_project_value = Revenue.objects.filter(
            user=self.user,
            status='completed'
        ).aggregate(avg=Avg('amount'))['avg'] or 0

        # Growth metrics
        current_month_revenue = Revenue.objects.filter(
            user=self.user,
            status='completed',
            created_at__month=timezone.now().month,
            created_at__year=timezone.now().year
        ).aggregate(total=Sum('amount'))['total'] or 0

        last_month = timezone.now() - timedelta(days=30)
        last_month_revenue = Revenue.objects.filter(
            user=self.user,
            status='completed',
            created_at__month=last_month.month,
            created_at__year=last_month.year
        ).aggregate(total=Sum('amount'))['total'] or 0

        growth_rate = 0
        if last_month_revenue > 0:
            growth_rate = ((current_month_revenue - last_month_revenue) / last_month_revenue) * 100

        return {
            'monthly_trend': monthly_data,
            'weekly_trend': weekly_data,
            'platform_breakdown': platform_data,
            'average_project_value': float(avg_project_value),
            'current_month_revenue': float(current_month_revenue),
            'last_month_revenue': float(last_month_revenue),
            'growth_rate': round(growth_rate, 1),
            'generated_at': datetime.now().isoformat()
        }

    async def handle_withdrawal(self, data: Dict[str, Any]):
        """Handle withdrawal request"""
        amount = data.get('amount')
        method = data.get('method')
        account_details = data.get('account_details', {})

        if not amount or not method:
            await self.send_error('Amount and method required')
            return

        result = await self.process_withdrawal(amount, method, account_details)

        await self.send(text_data=json.dumps({
            'type': 'withdrawal_result',
            'data': result
        }))

    @database_sync_to_async
    def process_withdrawal(self, amount: float, method: str, account_details: Dict) -> Dict[str, Any]:
        """Process withdrawal request"""
        from core.models import Revenue, WithdrawalRequest

        try:
            # Check available balance
            total_earned = Revenue.objects.filter(
                user=self.user,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

            withdrawn = WithdrawalRequest.objects.filter(
                user=self.user,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

            available = total_earned - withdrawn

            if Decimal(str(amount)) > available:
                return {
                    'success': False,
                    'error': 'Insufficient balance',
                    'available': float(available)
                }

            # Create withdrawal request
            withdrawal = WithdrawalRequest.objects.create(
                user=self.user,
                amount=Decimal(str(amount)),
                method=method,
                account_details=json.dumps(account_details),
                status='pending'
            )

            # Process withdrawal (in real system, this would connect to payment provider)
            # For now, we'll simulate processing
            withdrawal.status = 'processing'
            withdrawal.save()

            return {
                'success': True,
                'withdrawal_id': str(withdrawal.id),
                'amount': float(withdrawal.amount),
                'method': method,
                'status': withdrawal.status,
                'message': 'Withdrawal request submitted successfully. Processing time: 1-3 business days.'
            }

        except Exception as e:
            logger.error(f"Withdrawal error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def send_payment_methods(self):
        """Send available payment methods"""
        methods = await self.get_payment_methods()

        await self.send(text_data=json.dumps({
            'type': 'payment_methods',
            'data': methods
        }))

    @database_sync_to_async
    def get_payment_methods(self) -> List[Dict[str, Any]]:
        """Get user's saved payment methods"""
        # In a real system, this would fetch from payment provider
        return [
            {
                'id': 'paypal_default',
                'type': 'PayPal',
                'name': 'PayPal Account',
                'email': self.user.email,
                'is_default': True,
                'min_withdrawal': 10.0,
                'fee': 0.0
            },
            {
                'id': 'bank_account',
                'type': 'Bank Transfer',
                'name': 'Bank Account',
                'last_four': '****1234',
                'is_default': False,
                'min_withdrawal': 50.0,
                'fee': 2.50
            },
            {
                'id': 'crypto_wallet',
                'type': 'Cryptocurrency',
                'name': 'Bitcoin Wallet',
                'address': '1A1zP1...XuNMhW',
                'is_default': False,
                'min_withdrawal': 25.0,
                'fee': 0.0
            }
        ]

    async def stream_revenue_updates(self):
        """Stream real-time revenue updates"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute

                # Send updated summary
                summary = await self.get_revenue_data()

                # Only send if there are changes
                await self.send(text_data=json.dumps({
                    'type': 'revenue_update',
                    'data': summary
                }))

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in stream_revenue_updates: {str(e)}")
                await asyncio.sleep(120)  # Back off on error

    async def send_error(self, message: str):
        """Send error message"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))

    # Group send handlers
    async def revenue_notification(self, event):
        """Handle revenue notifications from channel layer"""
        await self.send(text_data=json.dumps({
            'type': 'revenue_notification',
            'data': event['data']
        }))

    async def payment_update(self, event):
        """Handle payment status updates"""
        await self.send(text_data=json.dumps({
            'type': 'payment_update',
            'data': event['data']
        }))