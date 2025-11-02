from .action_plan import ActionPlan
"""
Models for Intelligence System - Action Plans and Execution
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import json
import uuid

# Import SpiderQualityMetrics so Django discovers it
from .spider_quality_tracker import SpiderQualityMetrics

User = get_user_model()


class ActionPlan(models.Model):
    """Store and track action plan execution"""

    STATUS_CHOICES = [
        ('created', 'Created'),
        ('in_progress', 'In Progress'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='action_plans', null=True, blank=True)

    # Opportunity details
    opportunity_id = models.CharField(max_length=100)
    opportunity_title = models.CharField(max_length=255)
    opportunity_data = models.JSONField(default=dict)

    # Plan details
    plan_data = models.JSONField(default=dict)  # Full plan from AI
    steps = models.JSONField(default=list)  # Extracted steps
    resources = models.JSONField(default=list)
    timeline = models.CharField(max_length=255, blank=True)
    expected_outcome = models.TextField(blank=True)

    # Execution tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    progress = models.IntegerField(default=0)  # 0-100
    current_step = models.IntegerField(default=0)
    completed_steps = models.JSONField(default=list)

    # Execution details
    execution_logs = models.JSONField(default=list)
    agent_tasks = models.JSONField(default=list)  # Track which agents are working
    results = models.JSONField(default=dict)  # Store results from each step

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)

    # Celery task tracking
    celery_task_id = models.CharField(max_length=255, blank=True)

    class Meta:
        app_label = 'intelligence_rt'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['opportunity_id']),
        ]

    def __str__(self):
        return f"{self.opportunity_title} - {self.status} ({self.progress}%)"

    def start_execution(self):
        """Start executing this plan"""
        from intelligence.tasks import execute_action_plan

        self.status = 'in_progress'
        self.started_at = timezone.now()
        self.save()

        # Launch Celery task
        result = execute_action_plan.delay(str(self.id))
        self.celery_task_id = result.id
        self.save()

        return result.id

    def add_log(self, message, level='info', agent=None):
        """Add execution log entry"""
        log_entry = {
            'timestamp': timezone.now().isoformat(),
            'level': level,
            'message': message,
            'agent': agent
        }
        self.execution_logs.append(log_entry)
        self.save()

    def update_progress(self, step_number=None, step_completed=False):
        """Update execution progress"""
        if step_number:
            self.current_step = step_number

        if step_completed and step_number not in self.completed_steps:
            self.completed_steps.append(step_number)

        # Calculate progress based on completed steps
        if self.steps:
            self.progress = int((len(self.completed_steps) / len(self.steps)) * 100)

        self.last_activity = timezone.now()
        self.save()

    def mark_completed(self):
        """Mark plan as completed"""
        self.status = 'completed'
        self.progress = 100
        self.completed_at = timezone.now()
        self.save()

    def mark_failed(self, error_message):
        """Mark plan as failed"""
        self.status = 'failed'
        self.add_log(f"Execution failed: {error_message}", level='error')
        self.save()


class ActionPlanStep(models.Model):
    """Individual step in an action plan"""

    action_plan = models.ForeignKey(ActionPlan, on_delete=models.CASCADE, related_name='step_details')
    step_number = models.IntegerField()
    description = models.TextField()

    # Agent assignment
    assigned_agent = models.CharField(max_length=100, blank=True)
    agent_task_data = models.JSONField(default=dict)

    # Execution
    status = models.CharField(max_length=20, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    result = models.JSONField(default=dict)

    class Meta:
        app_label = 'intelligence_rt'
        ordering = ['action_plan', 'step_number']
        unique_together = ['action_plan', 'step_number']

    def __str__(self):
        return f"Step {self.step_number}: {self.description[:50]}..."


class OpportunityActionPlan(models.Model):
    """Link table connecting revenue opportunities to action plans"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Opportunity information
    opportunity_id = models.CharField(max_length=255, db_index=True)
    platform = models.CharField(max_length=50, db_index=True)
    opportunity_data = models.JSONField(default=dict)

    # Action plan connection
    action_plan = models.ForeignKey(ActionPlan, on_delete=models.CASCADE, related_name='opportunity_links')

    # Proposal information
    proposal_id = models.CharField(max_length=255, blank=True, db_index=True)
    proposal_content = models.TextField(blank=True)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Status tracking
    STATUS_CHOICES = [
        ('identified', 'Identified'),
        ('analyzing', 'Analyzing'),
        ('plan_created', 'Plan Created'),
        ('proposal_generated', 'Proposal Generated'),
        ('proposal_submitted', 'Proposal Submitted'),
        ('awaiting_response', 'Awaiting Response'),
        ('client_responded', 'Client Responded'),
        ('negotiating', 'Negotiating'),
        ('converted', 'Converted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='identified', db_index=True)

    # Success metrics
    success_score = models.FloatField(null=True, blank=True)
    ml_confidence = models.FloatField(null=True, blank=True)
    priority_level = models.CharField(max_length=20, default='medium')

    # Revenue tracking
    revenue_generated = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    revenue_potential = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    converted_at = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    # Files generated
    files_generated = models.JSONField(default=list)

    class Meta:
        app_label = 'intelligence_rt'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['platform', 'status']),
            models.Index(fields=['created_at', 'status']),
            models.Index(fields=['success_score', 'priority_level']),
        ]

    def __str__(self):
        return f"{self.platform} - {self.opportunity_id} ({self.status})"

    def update_status(self, new_status, **kwargs):
        """Update status with timestamp tracking"""
        self.status = new_status

        if new_status == 'proposal_submitted':
            self.submitted_at = timezone.now()
        elif new_status == 'client_responded':
            self.responded_at = timezone.now()
        elif new_status == 'converted':
            self.converted_at = timezone.now()

        # Update any additional fields passed
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.save()

    def calculate_response_time(self):
        """Calculate time between submission and response"""
        if self.submitted_at and self.responded_at:
            return (self.responded_at - self.submitted_at).total_seconds() / 3600  # Hours
        return None

    def calculate_conversion_time(self):
        """Calculate time from opportunity to conversion"""
        if self.converted_at:
            return (self.converted_at - self.created_at).total_seconds() / 86400  # Days
        return None


class RevenueMetrics(models.Model):
    """Track overall revenue metrics and performance"""

    date = models.DateField(unique=True, db_index=True)

    # Opportunity metrics
    opportunities_identified = models.IntegerField(default=0)
    opportunities_analyzed = models.IntegerField(default=0)

    # Proposal metrics
    proposals_generated = models.IntegerField(default=0)
    proposals_submitted = models.IntegerField(default=0)
    proposals_responded = models.IntegerField(default=0)

    # Conversion metrics
    conversions = models.IntegerField(default=0)
    conversion_rate = models.FloatField(default=0)
    response_rate = models.FloatField(default=0)

    # Revenue metrics
    revenue_generated = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_deal_size = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Performance metrics
    average_response_time_hours = models.FloatField(null=True, blank=True)
    average_conversion_time_days = models.FloatField(null=True, blank=True)
    ml_accuracy = models.FloatField(null=True, blank=True)

    # Platform breakdown
    platform_metrics = models.JSONField(default=dict)

    class Meta:
        app_label = 'intelligence_rt'
        ordering = ['-date']

    def __str__(self):
        return f"Metrics for {self.date}"

    @classmethod
    def update_metrics_for_date(cls, date):
        """Update or create metrics for a specific date"""
        from django.db.models import Count, Avg, Sum

        metrics, created = cls.objects.get_or_create(date=date)

        # Get all opportunities for this date
        opportunities = OpportunityActionPlan.objects.filter(
            created_at__date=date
        )

        # Update counts
        metrics.opportunities_identified = opportunities.count()
        metrics.opportunities_analyzed = opportunities.exclude(
            status='identified'
        ).count()

        metrics.proposals_generated = opportunities.filter(
            status__in=['proposal_generated', 'proposal_submitted', 'awaiting_response',
                       'client_responded', 'negotiating', 'converted']
        ).count()

        metrics.proposals_submitted = opportunities.filter(
            status__in=['proposal_submitted', 'awaiting_response',
                       'client_responded', 'negotiating', 'converted']
        ).count()

        metrics.proposals_responded = opportunities.filter(
            status__in=['client_responded', 'negotiating', 'converted', 'rejected']
        ).count()

        metrics.conversions = opportunities.filter(status='converted').count()

        # Calculate rates
        if metrics.proposals_submitted > 0:
            metrics.response_rate = (metrics.proposals_responded / metrics.proposals_submitted) * 100

        if metrics.proposals_responded > 0:
            metrics.conversion_rate = (metrics.conversions / metrics.proposals_responded) * 100

        # Revenue metrics
        revenue_data = opportunities.filter(status='converted').aggregate(
            total_revenue=Sum('revenue_generated'),
            avg_deal=Avg('revenue_generated')
        )

        metrics.revenue_generated = revenue_data['total_revenue'] or 0
        metrics.average_deal_size = revenue_data['avg_deal'] or 0

        # Platform breakdown
        platform_stats = {}
        for platform in opportunities.values_list('platform', flat=True).distinct():
            platform_opps = opportunities.filter(platform=platform)
            platform_stats[platform] = {
                'count': platform_opps.count(),
                'submitted': platform_opps.filter(
                    status__in=['proposal_submitted', 'awaiting_response',
                               'client_responded', 'negotiating', 'converted']
                ).count(),
                'converted': platform_opps.filter(status='converted').count(),
                'revenue': float(
                    platform_opps.filter(status='converted').aggregate(
                        Sum('revenue_generated')
                    )['revenue_generated__sum'] or 0
                )
            }

        metrics.platform_metrics = platform_stats
        metrics.save()

        return metrics


class UserIncomeProfile(models.Model):
    """Track user's financial status, skills, and availability for income opportunities"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='income_profile')

    # Financial status
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Skills and experience
    skills = models.JSONField(default=list)  # List of skills
    skill_level = models.CharField(max_length=20, default='beginner')  # beginner, intermediate, advanced, expert
    interests = models.JSONField(default=list)  # List of interests

    # Availability
    available_hours_per_week = models.IntegerField(default=10)

    # Progress tracking
    completed_projects = models.JSONField(default=list)
    active_streams = models.JSONField(default=list)
    reputation_score = models.FloatField(default=0.0)
    learning_progress = models.JSONField(default=dict)

    # Analysis data
    analysis_data = models.JSONField(default=dict)  # Store latest opportunity analysis

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'intelligence_rt'
        indexes = [
            models.Index(fields=['skill_level', 'available_hours_per_week']),
        ]

    def __str__(self):
        return f"{self.user.username} - ${self.current_balance} - {self.skill_level}"

    def add_earnings(self, amount, source, opportunity_id=None):
        """Add earnings and update balance"""
        self.current_balance += amount
        self.total_earned += amount
        self.save()

        # Create earning record
        EarningRecord.objects.create(
            user=self.user,
            amount=amount,
            source=source,
            opportunity_id=opportunity_id or ''
        )


class OpportunityTracking(models.Model):
    """Track user progress on specific opportunities"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tracked_opportunities')
    opportunity_id = models.CharField(max_length=100, db_index=True)
    opportunity_title = models.CharField(max_length=255)
    opportunity_type = models.CharField(max_length=50)  # content_creation, freelance_services, etc.

    # Status tracking
    STATUS_CHOICES = [
        ('identified', 'Identified'),
        ('analyzing', 'Analyzing'),
        ('planning', 'Planning'),
        ('started', 'Started'),
        ('in_progress', 'In Progress'),
        ('first_income', 'First Income'),
        ('scaling', 'Scaling'),
        ('optimized', 'Optimized'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='identified')

    # Progress metrics
    progress_percentage = models.IntegerField(default=0)  # 0-100
    current_step = models.CharField(max_length=255, blank=True)
    steps_completed = models.JSONField(default=list)

    # Financial tracking
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    target_monthly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Time tracking
    hours_invested = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    # Data storage
    opportunity_data = models.JSONField(default=dict)  # Store full opportunity details
    tracking_notes = models.TextField(blank=True)

    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    first_income_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'intelligence_rt'
        unique_together = ['user', 'opportunity_id']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['opportunity_type', 'status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.opportunity_title} ({self.status})"

    def update_progress(self, new_status=None, step_completed=None, earnings=0):
        """Update tracking progress"""
        if new_status:
            self.status = new_status
            if new_status == 'started' and not self.started_at:
                self.started_at = timezone.now()
            elif new_status == 'first_income' and not self.first_income_at:
                self.first_income_at = timezone.now()

        if step_completed and step_completed not in self.steps_completed:
            self.steps_completed.append(step_completed)

        if earnings > 0:
            self.total_earned += earnings
            # Update user profile
            if hasattr(self.user, 'income_profile'):
                self.user.income_profile.add_earnings(earnings, self.opportunity_title, self.opportunity_id)

        self.save()


class EarningRecord(models.Model):
    """Record individual earnings from opportunities"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earnings')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    source = models.CharField(max_length=255)  # Description of earning source
    opportunity_id = models.CharField(max_length=100, blank=True)

    # Categorization
    EARNING_TYPES = [
        ('freelance', 'Freelance Work'),
        ('product_sales', 'Product Sales'),
        ('affiliate', 'Affiliate Commission'),
        ('investment', 'Investment Return'),
        ('service', 'Service Payment'),
        ('other', 'Other'),
    ]
    earning_type = models.CharField(max_length=20, choices=EARNING_TYPES, default='other')

    # Additional data
    client_info = models.JSONField(default=dict, blank=True)
    transaction_data = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)

    # Timestamps
    earned_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'intelligence_rt'
        ordering = ['-earned_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'earned_date']),
            models.Index(fields=['earning_type', 'earned_date']),
        ]

    def __str__(self):
        return f"{self.user.username} - ${self.amount} from {self.source}"


class ActionStep(models.Model):
    """Individual action steps within action plans"""

    action_plan = models.ForeignKey(ActionPlan, on_delete=models.CASCADE, related_name='action_steps')
    step_number = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()

    # Step details
    estimated_duration = models.CharField(max_length=50, blank=True)  # e.g., "2 hours", "1 day"
    required_tools = models.JSONField(default=list)
    prerequisites = models.JSONField(default=list)

    # Status tracking
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
        ('blocked', 'Blocked'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Execution tracking
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    actual_duration = models.DurationField(null=True, blank=True)

    # Results
    completion_notes = models.TextField(blank=True)
    output_data = models.JSONField(default=dict)

    class Meta:
        app_label = 'intelligence_rt'
        ordering = ['action_plan', 'step_number']
        unique_together = ['action_plan', 'step_number']

    def __str__(self):
        return f"Step {self.step_number}: {self.title}"

    def mark_completed(self, notes='', output_data=None):
        """Mark step as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if self.started_at:
            self.actual_duration = self.completed_at - self.started_at
        self.completion_notes = notes
        if output_data:
            self.output_data = output_data
        self.save()

        # Update parent action plan progress
        self.action_plan.update_progress(self.step_number, step_completed=True)

class AgentExecution(models.Model):
    """Track individual agent executions for action plans"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('executing', 'Executing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action_plan = models.ForeignKey(
        ActionPlan,
        on_delete=models.CASCADE,
        related_name='agent_executions'
    )

    # Agent information
    agent_type = models.CharField(max_length=100)
    agent_name = models.CharField(max_length=255)
    instruction = models.TextField()
    parameters = models.JSONField(default=dict)

    # Execution tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Results
    result = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    files_generated = models.JSONField(default=list)

    # Metadata
    step_number = models.IntegerField()
    week = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'intelligence_rt'
        ordering = ['action_plan', 'step_number', 'created_at']

    def __str__(self):
        return f"{self.agent_name} - {self.instruction[:50]}"

    def mark_executing(self):
        """Mark as executing"""
        self.status = 'executing'
        self.started_at = timezone.now()
        self.save()

    def mark_completed(self, result=None):
        """Mark as completed with result"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if result:
            self.result = result
        self.save()

    def mark_failed(self, error_message):
        """Mark as failed with error"""
        self.status = 'failed'
        self.completed_at = timezone.now()
        self.error_message = error_message
        self.save()
