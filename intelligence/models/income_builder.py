"""
Income Builder Models
====================

Models for tracking user income profiles, opportunities, earnings, and action steps.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
User = get_user_model()


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
        app_label = 'intelligence'
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


class OpportunityType(models.TextChoices):
    """Types of income opportunities"""
    JOB = 'job', 'Job Opportunity'
    FREELANCE = 'freelance', 'Freelance Gig'
    CONTENT = 'content', 'Content Creation'
    SPORTS_BET = 'sports_bet', 'Sports Betting Opportunity'
    CRYPTO = 'crypto', 'Cryptocurrency Trade'
    COURSE = 'course', 'Course Creation'
    CONSULTING = 'consulting', 'Consulting Engagement'
    AFFILIATE = 'affiliate', 'Affiliate Marketing'
    INVESTMENT = 'investment', 'Investment Opportunity'
    OTHER = 'other', 'Other'


class OpportunityStatus(models.TextChoices):
    """Status of opportunities in the pipeline"""
    DISCOVERED = 'discovered', 'Discovered'
    VIEWED = 'viewed', 'Viewed'
    ANALYZING = 'analyzing', 'Analyzing'
    PLANNING = 'planning', 'Planning'
    ACTION_TAKEN = 'action_taken', 'Action Taken'
    IN_PROGRESS = 'in_progress', 'In Progress'
    FIRST_INCOME = 'first_income', 'First Income'
    SCALING = 'scaling', 'Scaling'
    OPTIMIZED = 'optimized', 'Optimized'
    PAUSED = 'paused', 'Paused'
    COMPLETED = 'completed', 'Completed'
    REJECTED = 'rejected', 'Rejected'
    EXPIRED = 'expired', 'Expired'


class OpportunityTracking(models.Model):
    """Track user progress on specific opportunities - UNIFIED MODEL for all opportunity types"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tracked_opportunities')
    opportunity_id = models.CharField(max_length=100, db_index=True)
    opportunity_title = models.CharField(max_length=255)
    opportunity_type = models.CharField(
        max_length=50,
        choices=OpportunityType.choices,
        default=OpportunityType.OTHER
    )

    # Unified fields for all opportunity types
    title = models.CharField(max_length=500, blank=True)  # Detailed title
    description = models.TextField(blank=True)  # Detailed description
    potential_revenue = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Estimated earnings potential"
    )
    confidence_score = models.FloatField(
        default=0.5,
        help_text="AI confidence in this recommendation (0-1)"
    )
    match_score = models.FloatField(
        default=0.5,
        help_text="How well this matches user profile (0-1)"
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=OpportunityStatus.choices,
        default=OpportunityStatus.DISCOVERED
    )

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
    opportunity_data = models.JSONField(default=dict)  # Store full opportunity details (type-specific)
    tracking_notes = models.TextField(blank=True)

    # Revenue tracking
    actual_revenue = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Actual revenue earned from this opportunity"
    )
    revenue_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date revenue was received"
    )

    # Learning integration
    success_outcome = models.BooleanField(
        null=True,
        blank=True,
        help_text="Did user benefit from this opportunity?"
    )
    feedback_provided = models.BooleanField(
        default=False,
        help_text="Has user provided feedback?"
    )
    learning_insights = models.JSONField(
        default=dict,
        help_text="Insights learned from this opportunity"
    )

    # Spider tracking
    spider_source = models.CharField(
        max_length=100,
        blank=True,
        help_text="Spider that discovered this opportunity"
    )
    discovery_metadata = models.JSONField(
        default=dict,
        help_text="Metadata about how opportunity was discovered"
    )

    # Timestamps
    discovered_at = models.DateTimeField(auto_now_add=True)
    viewed_at = models.DateTimeField(null=True, blank=True)
    action_taken_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    first_income_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this opportunity expires (for time-sensitive opps like sports bets)"
    )

    class Meta:
        app_label = 'intelligence'
        unique_together = ['user', 'opportunity_id']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['opportunity_type', 'status']),
            models.Index(fields=['discovered_at']),
            models.Index(fields=['expires_at']),
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


class RevenueStream(models.TextChoices):
    """Revenue stream categories"""
    JOB_APPLICATION = 'job_application', 'Job Application'
    FREELANCE_GIG = 'freelance_gig', 'Freelance Gig'
    SPORTS_BETTING = 'sports_betting', 'Sports Betting'
    CONTENT_CREATION = 'content_creation', 'Content Creation'
    AFFILIATE = 'affiliate', 'Affiliate Income'
    CRYPTO_TRADING = 'crypto_trading', 'Crypto Trading'
    COURSE_SALES = 'course_sales', 'Course Sales'
    CONSULTING = 'consulting', 'Consulting'
    INVESTMENT = 'investment', 'Investment Return'
    OTHER = 'other', 'Other'


class UnifiedRevenueTracking(models.Model):
    """Track actual revenue from all sources - NEW unified revenue model"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='unified_revenue')

    # Source
    revenue_stream = models.CharField(
        max_length=50,
        choices=RevenueStream.choices,
        help_text="Category of revenue"
    )
    source_opportunity = models.ForeignKey(
        OpportunityTracking,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='revenue_records',
        help_text="Link to original opportunity if applicable"
    )

    # Revenue details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Revenue amount"
    )
    revenue_date = models.DateTimeField(
        help_text="Date revenue was received"
    )
    description = models.TextField(
        help_text="Description of revenue source"
    )

    # Metadata
    revenue_data = models.JSONField(
        default=dict,
        help_text="Additional details specific to revenue type"
    )

    # Verification
    verified = models.BooleanField(
        default=False,
        help_text="Has this revenue been verified?"
    )
    verification_method = models.CharField(
        max_length=50,
        blank=True,
        help_text="How was this verified (e.g., 'bank_statement', 'api_callback')"
    )

    # Learning integration
    contributed_to_learning = models.BooleanField(
        default=False,
        help_text="Has this revenue contributed to the learning loop?"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'intelligence'
        ordering = ['-revenue_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'revenue_stream', 'revenue_date']),
            models.Index(fields=['revenue_date']),
        ]

    def __str__(self):
        return f"{self.user.username} - ${self.amount} from {self.revenue_stream} on {self.revenue_date.date()}"


class EarningRecord(models.Model):
    """Record individual earnings from opportunities - LEGACY MODEL (kept for backward compatibility)"""

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
        app_label = 'intelligence'
        ordering = ['-earned_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'earned_date']),
            models.Index(fields=['earning_type', 'earned_date']),
        ]

    def __str__(self):
        return f"{self.user.username} - ${self.amount} from {self.source}"


# class ActionStep(models.Model):
#     """Individual action steps within action plans"""

#     action_plan = models.ForeignKey('intelligence.ActionPlan', on_delete=models.CASCADE, related_name='action_steps')
#     step_number = models.IntegerField()
#     title = models.CharField(max_length=255)
#     description = models.TextField()

#     # Step details
#     estimated_duration = models.CharField(max_length=50, blank=True)  # e.g., "2 hours", "1 day"
#     required_tools = models.JSONField(default=list)
#     prerequisites = models.JSONField(default=list)

#     # Status tracking
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('in_progress', 'In Progress'),
#         ('completed', 'Completed'),
#         ('skipped', 'Skipped'),
#         ('blocked', 'Blocked'),
#     ]
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

#     # Execution tracking
#     started_at = models.DateTimeField(null=True, blank=True)
#     completed_at = models.DateTimeField(null=True, blank=True)
#     actual_duration = models.DurationField(null=True, blank=True)

#     # Results
#     completion_notes = models.TextField(blank=True)
#     output_data = models.JSONField(default=dict)

#     class Meta:
#         app_label = 'intelligence'
#         ordering = ['action_plan', 'step_number']
#         unique_together = ['action_plan', 'step_number']

#     def __str__(self):
#         return f"Step {self.step_number}: {self.title}"

#     def mark_completed(self, notes='', output_data=None):
#         """Mark step as completed"""
#         self.status = 'completed'
#         self.completed_at = timezone.now()
#         if self.started_at:
#             self.actual_duration = self.completed_at - self.started_at
#         self.completion_notes = notes
#         if output_data:
#             self.output_data = output_data
#         self.save()

#         # Update parent action plan progress
#         self.action_plan.update_progress(self.step_number, step_completed=True)