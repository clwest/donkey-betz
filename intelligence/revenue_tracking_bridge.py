"""
Revenue Tracking Bridge
Connects all income-generating activities to Revenue Dashboard
"""

import logging
from typing import Dict, Any
from datetime import timedelta
from django.utils import timezone
from django.db import models
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


class RevenueSource(models.Model):
    """Track different revenue sources"""
    source_name = models.CharField(max_length=100)
    source_type = models.CharField(max_length=50)  # job, freelance, income_stream, passive
    platform = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source_name} ({self.source_type})"


class RevenueRecord(models.Model):
    """Track actual revenue generated"""
    user_id = models.CharField(max_length=100)
    source = models.ForeignKey(RevenueSource, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    revenue_type = models.CharField(max_length=50)  # payment, milestone, recurring
    description = models.TextField()
    received_date = models.DateTimeField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    # Metadata
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_category = models.CharField(max_length=50, default='freelance')

    class Meta:
        ordering = ['-received_date']

    def save(self, *args, **kwargs):
        if not self.net_amount:
            self.net_amount = self.amount - self.platform_fee
        super().save(*args, **kwargs)

    def __str__(self):
        return f"${self.amount} from {self.source.source_name}"


class ProposalTracker(models.Model):
    """Track proposals and their outcomes"""
    user_id = models.CharField(max_length=100)
    opportunity_id = models.CharField(max_length=200)
    platform = models.CharField(max_length=100)
    job_title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)

    # Proposal details
    proposed_rate = models.DecimalField(max_digits=10, decimal_places=2)
    proposal_text = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    # Outcome tracking
    status = models.CharField(max_length=50, default='submitted')  # submitted, viewed, rejected, accepted, hired
    response_date = models.DateTimeField(null=True, blank=True)
    final_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Revenue connection
    revenue_generated = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.job_title} - {self.status}"


class RevenueDashboardMetrics(models.Model):
    """Aggregate metrics for dashboard"""
    user_id = models.CharField(max_length=100)
    date = models.DateField()

    # Daily metrics
    proposals_submitted = models.IntegerField(default=0)
    proposals_responded = models.IntegerField(default=0)
    proposals_accepted = models.IntegerField(default=0)

    # Revenue metrics
    revenue_generated = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    revenue_pending = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Performance metrics
    response_rate = models.FloatField(default=0.0)
    acceptance_rate = models.FloatField(default=0.0)
    average_project_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ['user_id', 'date']

    def __str__(self):
        return f"Metrics {self.date} - {self.user_id}"


class RevenueTrackingBridge:
    """Bridge that connects all revenue activities to dashboard"""

    def __init__(self):
        self.channel_layer = get_channel_layer()
        self.cache_timeout = 3600

    # =====================
    # Revenue Recording
    # =====================

    async def record_revenue(self, user_id: str, source_name: str, amount: float,
                           revenue_type: str = 'payment', description: str = '',
                           platform: str = 'unknown', platform_fee: float = 0) -> bool:
        """Record actual revenue received"""
        try:
            # Get or create revenue source
            source, created = await self._get_or_create_source(
                user_id, source_name, platform
            )

            # Create revenue record
            revenue_record = await self._create_revenue_record(
                user_id=user_id,
                source=source,
                amount=amount,
                revenue_type=revenue_type,
                description=description,
                platform_fee=platform_fee
            )

            # Update metrics
            await self._update_daily_metrics(user_id, amount)

            # Notify components
            await self._notify_revenue_generated(user_id, revenue_record)

            logger.info(f"💰 Recorded ${amount} revenue for {user_id} from {source_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to record revenue: {e}")
            return False

    async def _get_or_create_source(self, user_id: str, source_name: str, platform: str):
        """Get or create revenue source"""
        from asgiref.sync import sync_to_async

        @sync_to_async
        def get_or_create():
            return RevenueSource.objects.get_or_create(
                source_name=source_name,
                user_id=user_id,
                platform=platform,
                defaults={
                    'source_type': self._determine_source_type(source_name, platform)
                }
            )

        source, created = await get_or_create()
        return source

    def _determine_source_type(self, source_name: str, platform: str) -> str:
        """Determine the type of revenue source"""
        if any(word in source_name.lower() for word in ['freelance', 'upwork', 'fiverr']):
            return 'freelance'
        elif any(word in source_name.lower() for word in ['job', 'employment', 'salary']):
            return 'job'
        elif any(word in source_name.lower() for word in ['passive', 'recurring', 'subscription']):
            return 'passive'
        else:
            return 'income_stream'

    async def _create_revenue_record(self, **kwargs):
        """Create revenue record in database"""
        from asgiref.sync import sync_to_async

        @sync_to_async
        def create_record():
            return RevenueRecord.objects.create(
                received_date=timezone.now(),
                **kwargs
            )

        return await create_record()

    # =====================
    # Proposal Tracking
    # =====================

    async def track_proposal(self, user_id: str, opportunity_id: str, platform: str,
                           job_title: str, company: str, proposed_rate: float,
                           proposal_text: str = '') -> str:
        """Track a submitted proposal"""
        try:
            from asgiref.sync import sync_to_async

            @sync_to_async
            def create_proposal():
                return ProposalTracker.objects.create(
                    user_id=user_id,
                    opportunity_id=opportunity_id,
                    platform=platform,
                    job_title=job_title,
                    company=company,
                    proposed_rate=proposed_rate,
                    proposal_text=proposal_text
                )

            proposal = await create_proposal()

            # Update daily metrics
            await self._update_proposal_metrics(user_id)

            # Notify components
            await self._notify_proposal_submitted(user_id, proposal)

            logger.info(f"📤 Tracked proposal: {job_title} at {company} for ${proposed_rate}")
            return str(proposal.id)

        except Exception as e:
            logger.error(f"Failed to track proposal: {e}")
            return ''

    async def update_proposal_status(self, proposal_id: str, status: str,
                                   final_rate: float = None) -> bool:
        """Update proposal status"""
        try:
            from asgiref.sync import sync_to_async

            @sync_to_async
            def update_proposal():
                proposal = ProposalTracker.objects.get(id=proposal_id)
                proposal.status = status
                proposal.response_date = timezone.now()
                if final_rate:
                    proposal.final_rate = final_rate
                proposal.save()
                return proposal

            proposal = await update_proposal()

            # Update metrics
            await self._update_response_metrics(proposal.user_id, status)

            # Notify components
            await self._notify_proposal_updated(proposal.user_id, proposal, status)

            logger.info(f"📨 Updated proposal {proposal_id} status to {status}")
            return True

        except Exception as e:
            logger.error(f"Failed to update proposal status: {e}")
            return False

    # =====================
    # Metrics Management
    # =====================

    async def _update_daily_metrics(self, user_id: str, revenue_amount: float):
        """Update daily metrics"""
        try:
            from asgiref.sync import sync_to_async

            @sync_to_async
            def update_metrics():
                today = timezone.now().date()
                metrics, created = RevenueDashboardMetrics.objects.get_or_create(
                    user_id=user_id,
                    date=today,
                    defaults={'revenue_generated': 0}
                )

                metrics.revenue_generated += revenue_amount
                metrics.save()
                return metrics

            await update_metrics()

        except Exception as e:
            logger.error(f"Failed to update daily metrics: {e}")

    async def _update_proposal_metrics(self, user_id: str):
        """Update proposal metrics"""
        try:
            from asgiref.sync import sync_to_async

            @sync_to_async
            def update_metrics():
                today = timezone.now().date()
                metrics, created = RevenueDashboardMetrics.objects.get_or_create(
                    user_id=user_id,
                    date=today,
                    defaults={'proposals_submitted': 0}
                )

                metrics.proposals_submitted += 1
                metrics.save()
                return metrics

            await update_metrics()

        except Exception as e:
            logger.error(f"Failed to update proposal metrics: {e}")

    async def _update_response_metrics(self, user_id: str, status: str):
        """Update response metrics"""
        try:
            from asgiref.sync import sync_to_async

            @sync_to_async
            def update_metrics():
                today = timezone.now().date()
                metrics, created = RevenueDashboardMetrics.objects.get_or_create(
                    user_id=user_id,
                    date=today
                )

                if status in ['viewed', 'rejected', 'accepted', 'hired']:
                    metrics.proposals_responded += 1

                if status in ['accepted', 'hired']:
                    metrics.proposals_accepted += 1

                # Recalculate rates
                if metrics.proposals_submitted > 0:
                    metrics.response_rate = metrics.proposals_responded / metrics.proposals_submitted
                    metrics.acceptance_rate = metrics.proposals_accepted / metrics.proposals_submitted

                metrics.save()
                return metrics

            await update_metrics()

        except Exception as e:
            logger.error(f"Failed to update response metrics: {e}")

    # =====================
    # Component Notifications
    # =====================

    async def _notify_revenue_generated(self, user_id: str, revenue_record):
        """Notify components of revenue generation"""
        try:
            notification_data = {
                'type': 'revenue_generated',
                'user_id': user_id,
                'amount': float(revenue_record.amount),
                'source': revenue_record.source.source_name,
                'platform': revenue_record.source.platform,
                'description': revenue_record.description,
                'timestamp': timezone.now().isoformat()
            }

            # Notify Revenue Dashboard
            await self.channel_layer.group_send(
                "hub_revenue_dashboard_updates",
                {
                    'type': 'revenue_update',
                    'data': notification_data
                }
            )

            # Notify Personal Assistant
            await self.channel_layer.group_send(
                "hub_personal_assistant_updates",
                {
                    'type': 'revenue_celebration',
                    'data': notification_data
                }
            )

            logger.info(f"🔔 Notified components of ${revenue_record.amount} revenue")

        except Exception as e:
            logger.error(f"Failed to notify revenue generation: {e}")

    async def _notify_proposal_submitted(self, user_id: str, proposal):
        """Notify components of proposal submission"""
        try:
            notification_data = {
                'type': 'proposal_submitted',
                'user_id': user_id,
                'proposal_id': str(proposal.id),
                'job_title': proposal.job_title,
                'company': proposal.company,
                'proposed_rate': float(proposal.proposed_rate),
                'platform': proposal.platform,
                'timestamp': timezone.now().isoformat()
            }

            # Notify components
            components = [
                "hub_revenue_dashboard_updates",
                "hub_personal_assistant_updates",
                "hub_decision_command_updates"
            ]

            for component in components:
                await self.channel_layer.group_send(
                    component,
                    {
                        'type': 'proposal_update',
                        'data': notification_data
                    }
                )

        except Exception as e:
            logger.error(f"Failed to notify proposal submission: {e}")

    async def _notify_proposal_updated(self, user_id: str, proposal, status: str):
        """Notify components of proposal status update"""
        try:
            notification_data = {
                'type': 'proposal_status_update',
                'user_id': user_id,
                'proposal_id': str(proposal.id),
                'job_title': proposal.job_title,
                'company': proposal.company,
                'status': status,
                'final_rate': float(proposal.final_rate) if proposal.final_rate else None,
                'timestamp': timezone.now().isoformat()
            }

            # Notify components
            components = [
                "hub_revenue_dashboard_updates",
                "hub_personal_assistant_updates"
            ]

            for component in components:
                await self.channel_layer.group_send(
                    component,
                    {
                        'type': 'proposal_status_update',
                        'data': notification_data
                    }
                )

        except Exception as e:
            logger.error(f"Failed to notify proposal update: {e}")

    # =====================
    # Dashboard Data
    # =====================

    async def get_dashboard_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard metrics"""
        try:
            from asgiref.sync import sync_to_async

            @sync_to_async
            def get_metrics():
                # Get current metrics
                today = timezone.now().date()

                try:
                    daily_metrics = RevenueDashboardMetrics.objects.get(
                        user_id=user_id, date=today
                    )
                except RevenueDashboardMetrics.DoesNotExist:
                    daily_metrics = RevenueDashboardMetrics(
                        user_id=user_id, date=today
                    )

                # Get total revenue
                total_revenue = RevenueRecord.objects.filter(
                    user_id=user_id
                ).aggregate(total=models.Sum('amount'))['total'] or 0

                # Get recent revenue (last 30 days)
                thirty_days_ago = today - timedelta(days=30)
                recent_revenue = RevenueRecord.objects.filter(
                    user_id=user_id,
                    received_date__gte=thirty_days_ago
                ).aggregate(total=models.Sum('amount'))['total'] or 0

                # Get revenue by source
                revenue_by_source = {}
                for record in RevenueRecord.objects.filter(user_id=user_id)[:20]:
                    source_name = record.source.source_name
                    if source_name not in revenue_by_source:
                        revenue_by_source[source_name] = 0
                    revenue_by_source[source_name] += float(record.amount)

                return {
                    'daily_metrics': {
                        'proposals_submitted': daily_metrics.proposals_submitted,
                        'proposals_responded': daily_metrics.proposals_responded,
                        'proposals_accepted': daily_metrics.proposals_accepted,
                        'revenue_generated': float(daily_metrics.revenue_generated),
                        'response_rate': daily_metrics.response_rate,
                        'acceptance_rate': daily_metrics.acceptance_rate
                    },
                    'totals': {
                        'total_revenue': float(total_revenue),
                        'recent_revenue': float(recent_revenue),
                        'revenue_by_source': revenue_by_source
                    }
                }

            return await get_metrics()

        except Exception as e:
            logger.error(f"Failed to get dashboard metrics: {e}")
            return {}

    # =====================
    # Quick Apply Integration
    # =====================

    async def execute_quick_apply(self, user_id: str, opportunity: Dict[str, Any],
                                resume_content: str, cover_letter: str) -> Dict[str, Any]:
        """Execute quick apply and track the proposal"""
        try:
            # Extract opportunity details
            job_title = opportunity.get('title', 'Unknown Position')
            company = opportunity.get('company', 'Unknown Company')
            platform = opportunity.get('source', 'unknown')
            url = opportunity.get('url', '')

            # Estimate rate based on opportunity
            estimated_rate = self._extract_rate_from_opportunity(opportunity)

            # Track the proposal
            proposal_id = await self.track_proposal(
                user_id=user_id,
                opportunity_id=opportunity.get('id', ''),
                platform=platform,
                job_title=job_title,
                company=company,
                proposed_rate=estimated_rate,
                proposal_text=cover_letter
            )

            # Simulate application submission (in real implementation, this would
            # actually submit to the platform)
            application_result = {
                'success': True,
                'proposal_id': proposal_id,
                'submitted_to': platform,
                'job_title': job_title,
                'company': company,
                'estimated_rate': estimated_rate,
                'submission_time': timezone.now().isoformat(),
                'tracking_url': url
            }

            logger.info(f"🚀 Quick applied to {job_title} at {company}")
            return application_result

        except Exception as e:
            logger.error(f"Failed to execute quick apply: {e}")
            return {'success': False, 'error': str(e)}

    def _extract_rate_from_opportunity(self, opportunity: Dict[str, Any]) -> float:
        """Extract or estimate rate from opportunity"""
        salary = opportunity.get('salary', '').lower()

        if 'hour' in salary:
            # Try to extract hourly rate
            import re
            numbers = re.findall(r'\d+', salary)
            if numbers:
                return float(numbers[0])

        # Default estimate based on opportunity type
        if 'senior' in opportunity.get('title', '').lower():
            return 75.0
        elif 'junior' in opportunity.get('title', '').lower():
            return 35.0
        else:
            return 50.0


# Global instance
revenue_bridge = RevenueTrackingBridge()