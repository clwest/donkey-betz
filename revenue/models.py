"""
Revenue Reality Models

This module provides comprehensive revenue tracking and verification models
to prove that real money is being generated, tracked, and attributed correctly.
"""

import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class RevenueSource(models.TextChoices):
    """Types of revenue sources"""
    FREELANCE_GIG = 'freelance_gig', 'Freelance Gig'
    CONTENT_CREATION = 'content_creation', 'Content Creation'
    AFFILIATE_COMMISSION = 'affiliate_commission', 'Affiliate Commission'
    CONSULTATION = 'consultation', 'Consultation'
    DIGITAL_PRODUCT = 'digital_product', 'Digital Product'
    AUTOMATION_SERVICE = 'automation_service', 'Automation Service'
    AI_TRAINING = 'ai_training', 'AI Training'
    API_CREDITS = 'api_credits', 'API Credits'


class PaymentStatus(models.TextChoices):
    """Payment verification status"""
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    VERIFIED = 'verified', 'Verified'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    REFUNDED = 'refunded', 'Refunded'


class VerificationMethod(models.TextChoices):
    """How revenue was verified"""
    STRIPE_WEBHOOK = 'stripe_webhook', 'Stripe Webhook'
    PAYPAL_IPN = 'paypal_ipn', 'PayPal IPN'
    BANK_STATEMENT = 'bank_statement', 'Bank Statement'
    CRYPTO_BLOCKCHAIN = 'crypto_blockchain', 'Blockchain Verified'
    MANUAL_VERIFICATION = 'manual', 'Manually Verified'
    API_CONFIRMATION = 'api_confirmation', 'API Confirmed'


class RevenueTransaction(models.Model):
    """
    Core model for tracking real revenue transactions with verification
    """
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    # User and timing
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='revenue_transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Revenue details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    source = models.CharField(max_length=50, choices=RevenueSource.choices)
    description = models.TextField()

    # Verification
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    verification_method = models.CharField(max_length=30, choices=VerificationMethod.choices, null=True, blank=True)
    external_transaction_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    verification_timestamp = models.DateTimeField(null=True, blank=True)
    verification_proof = models.JSONField(default=dict)

    # Attribution (what caused this revenue)
    attributed_to_agent = models.CharField(max_length=100, null=True, blank=True)
    attributed_to_spider = models.CharField(max_length=100, null=True, blank=True)
    opportunity_id = models.CharField(max_length=100, null=True, blank=True)

    # Costs associated
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ai_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        app_label = 'revenue'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['external_transaction_id']),
        ]

    def __str__(self):
        return f"${self.amount} - {self.source} - {self.status}"

    @property
    def net_revenue(self):
        """Calculate net revenue after all fees"""
        return self.amount - self.platform_fee - self.processing_fee - self.ai_costs

    @property
    def roi(self):
        """Calculate return on investment"""
        if self.ai_costs > 0:
            return ((self.net_revenue - self.ai_costs) / self.ai_costs) * 100
        return 100.0

    def verify_transaction(self, method, proof):
        """Mark transaction as verified with proof"""
        self.status = PaymentStatus.VERIFIED
        self.verification_method = method
        self.verification_timestamp = timezone.now()
        self.verification_proof = proof
        self.save()

        # LEARNING LOOP: Update agent learning from successful revenue
        if self.attributed_to_agent and self.status in [PaymentStatus.VERIFIED, PaymentStatus.COMPLETED]:
            self._update_agent_learning()

        return True

    def _update_agent_learning(self):
        """Update UserAgentLearning based on successful revenue transaction"""
        from core.models import UserAgentLearning

        try:
            learning, created = UserAgentLearning.objects.get_or_create(
                user=self.user,
                agent_name=self.attributed_to_agent,
                learning_domain='revenue_optimization',
                defaults={
                    'learning_content': {},
                    'confidence_score': 0.5
                }
            )

            # Track successful revenue sources
            if 'successful_sources' not in learning.learning_content:
                learning.learning_content['successful_sources'] = []

            learning.learning_content['successful_sources'].append({
                'source': self.source,
                'amount': float(self.amount),
                'net_revenue': float(self.net_revenue),
                'roi': float(self.roi),
                'timestamp': self.created_at.isoformat(),
                'opportunity_id': self.opportunity_id
            })

            # Track total revenue generated
            learning.learning_content['total_revenue'] = (
                learning.learning_content.get('total_revenue', 0) + float(self.amount)
            )
            learning.learning_content['transaction_count'] = (
                learning.learning_content.get('transaction_count', 0) + 1
            )

            # Calculate average transaction value
            learning.learning_content['avg_transaction'] = (
                learning.learning_content['total_revenue'] /
                learning.learning_content['transaction_count']
            )

            # Record success (increases confidence)
            learning.record_success()
            learning.last_interaction = timezone.now()
            learning.save()

        except Exception as e:
            # Don't fail verification if learning update fails
            import logging
            logging.error(f"Failed to update agent learning for revenue: {e}")


class RevenueFlow(models.Model):
    """
    Track the complete flow from opportunity to revenue
    """
    flow_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    started_at = models.DateTimeField(auto_now_add=True)

    # Flow stages
    opportunity_discovered = models.DateTimeField(null=True, blank=True)
    agent_assigned = models.DateTimeField(null=True, blank=True)
    work_started = models.DateTimeField(null=True, blank=True)
    work_completed = models.DateTimeField(null=True, blank=True)
    payment_initiated = models.DateTimeField(null=True, blank=True)
    payment_received = models.DateTimeField(null=True, blank=True)

    # Entities involved
    spider_id = models.CharField(max_length=100)
    agent_id = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Data at each stage
    opportunity_data = models.JSONField(default=dict)
    work_data = models.JSONField(default=dict)
    payment_data = models.JSONField(default=dict)

    # Final transaction
    transaction = models.OneToOneField(
        RevenueTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='flow'
    )

    class Meta:
        app_label = 'revenue'
        ordering = ['-started_at']

    def __str__(self):
        return f"Flow {self.flow_id} - {self.spider_id} → {self.agent_id}"

    def get_total_time(self):
        """Get total time from discovery to payment"""
        if self.payment_received and self.opportunity_discovered:
            return (self.payment_received - self.opportunity_discovered).total_seconds()
        return None

    def get_conversion_rate(self):
        """Calculate conversion rate through the funnel"""
        stages = [
            self.opportunity_discovered,
            self.agent_assigned,
            self.work_started,
            self.work_completed,
            self.payment_initiated,
            self.payment_received
        ]
        completed = sum(1 for stage in stages if stage is not None)
        return (completed / len(stages)) * 100


class AgentRevenuePerformance(models.Model):
    """
    Track revenue performance metrics per agent
    """
    agent_id = models.CharField(max_length=100, unique=True)
    agent_name = models.CharField(max_length=200)

    # Lifetime metrics
    total_revenue_generated = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_transactions = models.IntegerField(default=0)
    total_costs_incurred = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Success metrics
    success_rate = models.FloatField(default=0.0)
    average_transaction_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_completion_time = models.FloatField(default=0.0, help_text="Hours")

    # Time-based metrics
    revenue_last_24h = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    revenue_last_7d = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    revenue_last_30d = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Efficiency metrics
    roi = models.FloatField(default=0.0)
    cost_per_transaction = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'revenue'
        ordering = ['-total_revenue_generated']

    def __str__(self):
        return f"{self.agent_name}: ${self.total_revenue_generated}"

    def update_metrics(self):
        """Recalculate all metrics based on transactions"""
        from django.db.models import Sum
        from datetime import timedelta

        now = timezone.now()

        # Get all transactions for this agent
        transactions = RevenueTransaction.objects.filter(
            attributed_to_agent=self.agent_id,
            status=PaymentStatus.COMPLETED
        )

        # Lifetime metrics
        self.total_transactions = transactions.count()
        self.total_revenue_generated = transactions.aggregate(
            total=Sum('amount')
        )['total'] or 0
        self.total_costs_incurred = transactions.aggregate(
            total=Sum('ai_costs')
        )['total'] or 0

        # Time-based metrics
        self.revenue_last_24h = transactions.filter(
            created_at__gte=now - timedelta(hours=24)
        ).aggregate(total=Sum('amount'))['total'] or 0

        self.revenue_last_7d = transactions.filter(
            created_at__gte=now - timedelta(days=7)
        ).aggregate(total=Sum('amount'))['total'] or 0

        self.revenue_last_30d = transactions.filter(
            created_at__gte=now - timedelta(days=30)
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Calculate averages
        if self.total_transactions > 0:
            self.average_transaction_value = self.total_revenue_generated / self.total_transactions
            self.cost_per_transaction = self.total_costs_incurred / self.total_transactions

            # Calculate ROI
            if self.total_costs_incurred > 0:
                self.roi = ((self.total_revenue_generated - self.total_costs_incurred) / self.total_costs_incurred) * 100
            else:
                self.roi = 100.0

        self.save()


class RevenueVerificationLog(models.Model):
    """
    Audit log for all revenue verification attempts
    """
    log_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    timestamp = models.DateTimeField(auto_now_add=True)

    transaction = models.ForeignKey(RevenueTransaction, on_delete=models.CASCADE, related_name='verification_logs')

    verification_type = models.CharField(max_length=50)
    verification_result = models.BooleanField()
    verification_details = models.JSONField(default=dict)

    # External verification
    external_api_called = models.CharField(max_length=100, null=True, blank=True)
    api_response_code = models.IntegerField(null=True, blank=True)
    api_response_data = models.JSONField(null=True, blank=True)

    # Verification metadata
    verified_by = models.CharField(max_length=100, default='system')
    confidence_score = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Verification {self.log_id} - {'✓' if self.verification_result else '✗'}"