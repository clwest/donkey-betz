"""
Unified System Models - The Complete AI Ecosystem
These models represent ALL agents, advisors, and system components
"""

from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import json
import uuid
import logging
from datetime import datetime

# Import base models
from .models.base.models import UnifiedBaseModel

class AgentCategory(models.Model):
    """Categories for organizing agents"""
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=10)
    description = models.TextField(blank=True)

    class Meta:
        app_label = 'core'
        verbose_name_plural = "Agent Categories"

    def __str__(self):
        return self.name


class Agent(models.Model):
    """
    Represents one of the 149 specialized AI agents in the system
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    agent_type = models.CharField(max_length=50)
    category = models.ForeignKey(AgentCategory, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    specialization = models.CharField(max_length=100)

    # Capabilities
    capabilities = models.JSONField(default=dict)
    effectiveness_score = models.IntegerField(default=85)  # 0-100

    # Status
    is_active = models.BooleanField(default=True)
    last_active = models.DateTimeField(auto_now=True)

    # User assignments
    user_assignments = models.ManyToManyField(settings.AUTH_USER_MODEL, through='AgentAssignment', related_name='assigned_agents')

    # Metrics
    total_executions = models.IntegerField(default=0)
    successful_executions = models.IntegerField(default=0)
    total_revenue_generated = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    # Integration
    api_endpoint = models.CharField(max_length=200, blank=True)
    webhook_url = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def success_rate(self):
        if self.total_executions == 0:
            return 0
        return (self.successful_executions / self.total_executions) * 100

    def __str__(self):
        return f"{self.name} ({self.agent_type})"

    class Meta:
        app_label = 'core'
        ordering = ['-effectiveness_score', 'name']


class Advisor(models.Model):
    """
    Represents one of the 25 legendary advisors (Warren Buffett, Cathie Wood, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    expertise = models.TextField()
    category = models.CharField(max_length=50)

    # Influence and reputation
    influence_score = models.IntegerField(default=90)  # 0-100
    avatar_url = models.CharField(max_length=500, blank=True)

    # Wisdom and philosophy
    wisdom = models.JSONField(default=dict)  # Contains philosophy, principles, quotes

    # Status
    is_active = models.BooleanField(default=True)
    last_consultation = models.DateTimeField(null=True, blank=True)

    # Metrics
    total_consultations = models.IntegerField(default=0)
    total_insights_provided = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.title}"

    class Meta:
        app_label = 'core'
        ordering = ['-influence_score', 'name']


class AgentAssignment(models.Model):
    """
    Links users to their assigned agents
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # Custom settings for this user-agent pair
    custom_settings = models.JSONField(default=dict)
    priority = models.IntegerField(default=5)  # 1-10

    class Meta:
        app_label = 'core'
        unique_together = ['user', 'agent']


class AgentExecution(models.Model):
    """
    Tracks every execution of an agent
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='executions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    task = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')

    # Execution details
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)

    # Performance metrics
    execution_time_ms = models.IntegerField(null=True)
    tokens_used = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=8, decimal_places=4, default=Decimal('0.00'))

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'

    def __str__(self):
        return f"{self.agent.name} - {self.task[:50]}"


class Collaboration(models.Model):
    """
    Tracks collaborations between agents and/or advisors
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Participants
    lead_agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='led_collaborations')
    collaborating_agents = models.ManyToManyField(Agent, related_name='collaborations')
    advisors = models.ManyToManyField(Advisor, related_name='consultations', blank=True)

    # Collaboration details
    objective = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ])

    # Results
    outcome = models.JSONField(default=dict)
    success_metrics = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'

    def __str__(self):
        return f"Collaboration: {self.objective[:50]}"


class Revenue(models.Model):
    """
    Tracks all revenue generated through the platform
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='revenues')

    # Source
    source_type = models.CharField(max_length=50)  # job, gig, investment, etc.
    source_id = models.CharField(max_length=100, blank=True)
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True)

    # Amount
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')

    # Status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='pending')

    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    earned_at = models.DateTimeField(null=True)
    paid_at = models.DateTimeField(null=True)

    # Details
    description = models.TextField()
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return f"${self.amount} - {self.source_type}"

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']


class Opportunity(models.Model):
    """
    Represents an income opportunity (job, gig, investment, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='opportunities')

    # Opportunity details
    title = models.CharField(max_length=200)
    opportunity_type = models.CharField(max_length=50)
    source = models.CharField(max_length=100)

    # Financial
    potential_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('pending', 'Pending Review'),
        ('applied', 'Applied'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ], default='active')

    # Matching
    match_score = models.IntegerField(default=0)  # 0-100
    recommended_by = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True)

    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Details
    description = models.TextField()
    requirements = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)

    # NEW (Session Pre-38): Partnership Enhancement Fields (Additive - won't break existing)
    # These fields enable human-AI partnership tracking WITHOUT changing existing functionality
    partnership_mode = models.CharField(
        max_length=20,
        choices=[
            ('solo', 'Traditional - User Only'),
            ('ai_assisted', 'AI-Assisted - User Leads'),
            ('collaborative', 'True Partnership - Equal'),
            ('ai_led', 'AI-Led - User Validates'),
        ],
        default='solo',
        null=True,
        blank=True,
        help_text="How human + AI will work together (optional)"
    )

    # Collaboration potential
    ai_contribution_potential = models.IntegerField(
        default=0,
        help_text="0-100: How much can AI contribute? (0 = no AI help possible)"
    )
    collaboration_feasibility = models.CharField(
        max_length=20,
        choices=[
            ('not_applicable', 'Not a partnership opportunity'),
            ('low', 'Minimal AI contribution possible'),
            ('medium', 'Moderate AI assistance available'),
            ('high', 'Strong partnership potential'),
            ('ideal', 'Perfect for human-AI collaboration'),
        ],
        default='not_applicable',
        null=True,
        blank=True,
        help_text="Partnership assessment (optional)"
    )

    # Execution planning (optional - for partnership opportunities)
    partnership_workflow = models.JSONField(
        null=True,
        blank=True,
        help_text="Step-by-step collaboration plan (optional)"
    )
    required_human_skills = models.JSONField(
        default=list,
        help_text="What human brings to partnership (optional)"
    )
    ai_capabilities_match = models.JSONField(
        default=list,
        help_text="What AI brings to partnership (optional)"
    )

    # Value metrics (optional - for showing partnership ROI)
    estimated_solo_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Hours if user did alone (optional)"
    )
    estimated_partnership_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Hours with AI partnership (optional)"
    )
    time_multiplier = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Efficiency gain (e.g., 3.5x faster) (optional)"
    )

    def __str__(self):
        return f"{self.title} - ${self.potential_revenue}"

    def calculate_partnership_metrics(self):
        """
        Calculate partnership value proposition (NEW - Session Pre-38)

        Returns dict showing potential ROI of human-AI partnership
        Only applicable if partnership fields are set
        """
        if not self.estimated_solo_hours or not self.estimated_partnership_hours:
            return {
                'available': False,
                'message': 'Partnership metrics not calculated for this opportunity'
            }

        self.time_multiplier = self.estimated_solo_hours / self.estimated_partnership_hours

        time_saved = self.estimated_solo_hours - self.estimated_partnership_hours
        effective_rate = self.potential_revenue / self.estimated_partnership_hours

        return {
            'available': True,
            'time_saved_hours': float(time_saved),
            'efficiency_gain': float(self.time_multiplier),
            'effective_hourly_rate': float(effective_rate),
            'solo_estimate': f"{float(self.estimated_solo_hours):.1f} hours",
            'partnership_estimate': f"{float(self.estimated_partnership_hours):.1f} hours",
            'ai_contribution': f"{self.ai_contribution_potential}%",
            'value_proposition': (
                f"${self.potential_revenue:.2f} in {float(self.estimated_partnership_hours):.1f}h "
                f"(vs {float(self.estimated_solo_hours):.1f}h solo) = "
                f"${float(effective_rate):.2f}/h effective rate"
            )
        }

    def mark_as_accepted(self, actual_amount=None):
        """
        CRITICAL FIX: Mark opportunity as accepted and create Revenue record
        This is the missing link for revenue tracking!
        """
        from decimal import Decimal

        self.status = 'accepted'
        self.save()

        # Create Revenue record
        revenue_amount = actual_amount or self.potential_revenue

        Revenue.objects.create(
            user=self.user,
            source_type=self.opportunity_type,
            source_id=str(self.id),
            agent=self.recommended_by,
            amount=Decimal(str(revenue_amount)),
            currency='USD',
            status='pending',
            description=f"Revenue from opportunity: {self.title}",
            metadata={
                'opportunity_id': str(self.id),
                'opportunity_title': self.title,
                'source_platform': self.source,
                'match_score': self.match_score,
                'created_via': 'opportunity_acceptance'
            }
        )

        logger = logging.getLogger(__name__)
        logger.info(f"✅ Created Revenue record for opportunity {self.id}: ${revenue_amount}")

    def mark_as_completed(self, actual_amount=None, paid_date=None):
        """
        CRITICAL FIX: Mark opportunity as completed and update Revenue to received
        """
        from django.utils import timezone

        self.status = 'completed'
        self.save()

        # Find and update the Revenue record
        revenue = Revenue.objects.filter(
            user=self.user,
            source_id=str(self.id),
            status='pending'
        ).first()

        if revenue:
            revenue.status = 'completed'
            revenue.earned_at = timezone.now()
            revenue.paid_at = paid_date or timezone.now()
            if actual_amount:
                revenue.amount = actual_amount
            revenue.save()

            logger = logging.getLogger(__name__)
            logger.info(f"✅ Updated Revenue record {revenue.id} to completed: ${revenue.amount}")
        else:
            # If no revenue record exists, create one
            self.mark_as_accepted(actual_amount)

    class Meta:
        app_label = 'core'
        ordering = ['-match_score', '-created_at']


class Application(models.Model):
    """
    Tracks applications to opportunities
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE)

    # Application details
    cover_letter = models.TextField(blank=True)
    resume_version = models.CharField(max_length=100, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ], default='draft')

    # AI assistance
    assisted_by = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True)
    ai_confidence = models.IntegerField(default=0)  # 0-100

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def submit_application(self):
        """
        CRITICAL FIX: Submit application and create Application record
        This ensures applications are tracked in the database
        """
        from django.utils import timezone

        self.status = 'submitted'
        self.submitted_at = timezone.now()
        self.save()

        # Also update the opportunity status
        self.opportunity.status = 'applied'
        self.opportunity.save()

        logger = logging.getLogger(__name__)
        logger.info(f"✅ Application {self.id} submitted for opportunity {self.opportunity.id}")

    def mark_as_accepted(self):
        """
        CRITICAL FIX: Mark application as accepted and trigger revenue creation
        """
        self.status = 'accepted'
        self.save()

        # Mark the opportunity as accepted and create revenue
        self.opportunity.mark_as_accepted()

        logger = logging.getLogger(__name__)
        logger.info(f"✅ Application {self.id} accepted, revenue record created")

    class Meta:
        app_label = 'core'


class AgentSolution(models.Model):
    """
    Represents a solution created by an agent
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='solutions')

    title = models.CharField(max_length=200)
    description = models.TextField()
    solution_type = models.CharField(max_length=50)

    # Solution content
    code_snippet = models.TextField(blank=True)
    language = models.CharField(max_length=20, blank=True)

    # Metrics
    metrics = models.JSONField(default=dict)
    tags = models.JSONField(default=list)

    # Usage tracking
    times_used = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.agent.name}: {self.title}"

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']


class AgentLearning(models.Model):
    """
    Tracks learning and knowledge transfer between agents
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    teacher_agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='teachings')
    student_agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='learnings')
    solution = models.ForeignKey(AgentSolution, on_delete=models.CASCADE, related_name='learning_records')

    # Learning details
    learning_type = models.CharField(max_length=50)
    effectiveness_before = models.FloatField()
    effectiveness_after = models.FloatField()

    # Impact metrics
    time_saved_hours = models.IntegerField(default=0)
    cost_savings = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    # Status
    implementation_success = models.BooleanField(default=True)
    feedback = models.TextField(blank=True)

    # Metadata
    metadata = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher_agent.name} → {self.student_agent.name}"

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']


class SpiderData(models.Model):
    """
    Data collected by spider network for intelligence gathering
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Source
    spider_name = models.CharField(max_length=100)
    source_url = models.CharField(max_length=500)
    data_type = models.CharField(max_length=50)

    # Data
    raw_data = models.JSONField()
    processed_data = models.JSONField(default=dict)

    # Analysis
    relevance_score = models.IntegerField(default=0)  # 0-100
    insights = models.JSONField(default=list)

    # Status
    is_processed = models.BooleanField(default=False)
    is_actionable = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Spider Data: {self.spider_name} - {self.data_type}"

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']


class AdvisorInsight(models.Model):
    """
    Insights and recommendations from legendary advisors
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    advisor = models.ForeignKey(Advisor, on_delete=models.CASCADE, related_name='insights')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Insight details
    content = models.TextField()
    category = models.CharField(max_length=50)
    confidence = models.IntegerField(default=80)  # 0-100

    # Context
    context = models.JSONField(default=dict)
    related_opportunity = models.ForeignKey(Opportunity, on_delete=models.SET_NULL, null=True, blank=True)

    # Actionability
    is_actionable = models.BooleanField(default=True)
    action_plan = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Insight from {self.advisor.name}: {self.content[:50]}"

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']


class UserAgentLearning(UnifiedBaseModel):
    """
    Connects user profiles to agent learning - making agents learn FOR specific users

    This model enables personalized agent learning where agents track what works
    for each individual user, building user-specific knowledge over time.

    Example:
        For User A (software engineer):
        - Job Matcher Agent learns A prefers remote Python roles at startups
        - Content Creator Agent learns A likes technical blog style
        - Income Builder learns A's best opportunities are on HackerNews

        For User B (designer):
        - Job Matcher Agent learns B prefers agency creative director roles
        - Content Creator Agent learns B likes visual portfolio style
        - Income Builder learns B's best opportunities are on Dribbble
    """

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='agent_learnings',
        help_text="User this learning applies to"
    )

    agent_name = models.CharField(
        max_length=200,
        help_text="Name of the agent (e.g., 'JobMatcherAgent', 'IncomeBuilder')"
    )

    learning_domain = models.CharField(
        max_length=100,
        choices=[
            ('opportunity_matching', 'Job/Opportunity Matching'),
            ('content_creation', 'Content Creation Style'),
            ('communication', 'Communication Preferences'),
            ('decision_making', 'Decision Making Patterns'),
            ('skill_development', 'Skill Development Path'),
            ('revenue_optimization', 'Revenue Optimization'),
            ('platform_preferences', 'Platform Preferences'),
            ('salary_preferences', 'Salary Range Preferences'),
            ('skill_preferences', 'Skill Type Preferences'),
            ('company_size_preferences', 'Company Size Preferences'),
            ('remote_preferences', 'Remote Work Preferences'),
            ('timing_patterns', 'Optimal Timing Patterns'),
            ('success_factors', 'Success Factor Analysis'),
            # Sports Betting Learning Domains (integrated via SportsBettingLearningBridge)
            ('sports_betting_nfl', 'Sports Betting - NFL'),
            ('sports_betting_nba', 'Sports Betting - NBA'),
            ('sports_betting_mlb', 'Sports Betting - MLB'),
            ('sports_betting_nhl', 'Sports Betting - NHL'),
            ('betting_risk_management', 'Betting Risk Management'),
            ('kelly_criterion_optimization', 'Kelly Criterion Optimization'),
            # Partnership Learning Domain (Session 40)
            ('partnership_success', 'Partnership Success'),
            ('general', 'General Learning'),
        ],
        default='general',
        help_text="What domain is this learning about"
    )

    # What the agent learned
    learning_content = models.JSONField(
        help_text="Structured learning data specific to this agent-user pair"
    )

    # How confident is the agent in this learning
    confidence_score = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Agent's confidence in this learning (0-1)"
    )

    # How many times this learning was validated
    validation_count = models.IntegerField(
        default=0,
        help_text="How many times this learning proved correct"
    )

    # How many times this learning failed
    failure_count = models.IntegerField(
        default=0,
        help_text="How many times this learning proved incorrect"
    )

    # Success rate calculated from validation/failure
    success_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Success rate of this learning"
    )

    # Source of this learning
    learning_source = models.CharField(
        max_length=100,
        choices=[
            ('user_feedback', 'Direct User Feedback'),
            ('success_pattern', 'Observed Success Pattern'),
            ('failure_analysis', 'Failure Analysis'),
            ('interaction_mining', 'Interaction Pattern Mining'),
            ('explicit_instruction', 'Explicit User Instruction'),
            ('performance_tracking', 'Performance Tracking'),
        ],
        default='success_pattern'
    )

    # Context when this was learned
    context_metadata = models.JSONField(
        default=dict,
        help_text="Context when learning occurred (time, situation, etc.)"
    )

    # When this learning expires (if temporary)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this learning becomes obsolete (null = never expires)"
    )

    # How many times this learning was used
    usage_count = models.IntegerField(
        default=0,
        help_text="How many times this learning influenced agent behavior"
    )

    last_used = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this learning was last applied"
    )

    class Meta:
        verbose_name = "User-Agent Learning"
        verbose_name_plural = "User-Agent Learnings"
        app_label = 'core'
        indexes = [
            models.Index(fields=['user', 'agent_name', 'learning_domain']),
            models.Index(fields=['user', '-confidence_score']),
            models.Index(fields=['user', '-success_rate']),
            models.Index(fields=['agent_name', '-confidence_score']),
        ]

    def __str__(self):
        return f"{self.agent_name} → {self.user.username}: {self.learning_domain} (confidence: {self.confidence_score:.1%})"

    def record_success(self):
        """Record that this learning proved correct"""
        self.validation_count += 1
        self.usage_count += 1
        self.last_used = timezone.now()
        self._update_metrics()
        self.save()

    def record_failure(self):
        """Record that this learning proved incorrect"""
        self.failure_count += 1
        self.usage_count += 1
        self.last_used = timezone.now()
        self._update_metrics()
        self.save()

    def _update_metrics(self):
        """Update confidence and success rate based on validation/failure counts"""
        total_attempts = self.validation_count + self.failure_count

        if total_attempts > 0:
            # Calculate success rate
            self.success_rate = self.validation_count / total_attempts

            # Adjust confidence based on success rate and sample size
            # More samples = more confidence in the success rate
            sample_weight = min(total_attempts / 20.0, 1.0)  # Fully confident after 20 samples

            # Confidence approaches success rate as sample size grows
            self.confidence_score = (
                self.confidence_score * (1 - sample_weight) +  # Old confidence
                self.success_rate * sample_weight  # New evidence
            )

    @classmethod
    def get_user_agent_knowledge(cls, user, agent_name, domain=None):
        """
        Get all learnings for a specific user-agent pair

        Args:
            user: User instance
            agent_name: Name of the agent
            domain: Optional domain filter

        Returns:
            QuerySet of learnings, ordered by confidence and recency
        """
        learnings = cls.objects.filter(
            user=user,
            agent_name=agent_name,
            is_active=True
        )

        if domain:
            learnings = learnings.filter(learning_domain=domain)

        # Filter out expired learnings
        learnings = learnings.filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now())
        )

        return learnings.order_by('-confidence_score', '-updated_at')

    @classmethod
    def create_learning(cls, user, agent_name, domain, content, source='success_pattern', confidence=0.5):
        """
        Create a new learning or update existing one

        Args:
            user: User instance
            agent_name: Name of the agent
            domain: Learning domain
            content: Learning content (JSON)
            source: Learning source
            confidence: Initial confidence score

        Returns:
            UserAgentLearning instance
        """
        learning, created = cls.objects.get_or_create(
            user=user,
            agent_name=agent_name,
            learning_domain=domain,
            defaults={
                'learning_content': content,
                'confidence_score': confidence,
                'learning_source': source,
                'context_metadata': {
                    'created_at': timezone.now().isoformat()
                }
            }
        )

        if not created:
            # Update existing learning
            learning.learning_content = content
            learning.confidence_score = confidence
            learning.save()

        return learning

    @classmethod
    def get_similar_users_learnings(cls, user, domain, min_confidence=0.6):
        """
        Collaborative filtering: Find learnings from similar users

        Args:
            user: Current user instance
            domain: Learning domain to find similar learnings
            min_confidence: Minimum confidence threshold

        Returns:
            QuerySet of learnings from similar users
        """
        # Get current user's learnings in this domain
        user_learnings = cls.objects.filter(
            user=user,
            learning_domain=domain,
            is_active=True,
            confidence_score__gte=min_confidence
        )

        if not user_learnings.exists():
            return cls.objects.none()

        # Find users with similar learnings
        similar_users = cls.objects.filter(
            learning_domain=domain,
            is_active=True,
            confidence_score__gte=min_confidence
        ).exclude(
            user=user
        ).values_list('user', flat=True).distinct()

        # Get their learnings in other domains
        return cls.objects.filter(
            user__in=similar_users,
            is_active=True,
            confidence_score__gte=min_confidence
        ).exclude(
            user=user
        ).order_by('-confidence_score', '-success_rate')

    @classmethod
    def get_collaborative_recommendations(cls, user, limit=10):
        """
        Get collaborative filtering recommendations across all agents

        "Users who learned X also learned Y"

        Args:
            user: User instance
            limit: Maximum number of recommendations

        Returns:
            List of recommended learning domains with reasoning
        """
        recommendations = []

        # Get user's current learnings
        user_learnings = cls.objects.filter(
            user=user,
            is_active=True,
            confidence_score__gte=0.5
        )

        if not user_learnings.exists():
            return recommendations

        user_domains = set(user_learnings.values_list('learning_domain', flat=True))

        # Find users with similar learnings
        similar_users_learnings = cls.objects.filter(
            learning_domain__in=user_domains,
            is_active=True,
            confidence_score__gte=0.6
        ).exclude(user=user).values_list('user', flat=True).distinct()

        # Get what they learned that current user hasn't
        other_learnings = cls.objects.filter(
            user__in=similar_users_learnings,
            is_active=True,
            confidence_score__gte=0.6
        ).exclude(
            learning_domain__in=user_domains
        ).values(
            'learning_domain', 'agent_name'
        ).annotate(
            count=models.Count('id'),
            avg_confidence=models.Avg('confidence_score'),
            avg_success=models.Avg('success_rate')
        ).order_by('-count', '-avg_confidence')[:limit]

        for learning_data in other_learnings:
            recommendations.append({
                'domain': learning_data['learning_domain'],
                'agent': learning_data['agent_name'],
                'similar_users_count': learning_data['count'],
                'avg_confidence': learning_data['avg_confidence'],
                'avg_success_rate': learning_data['avg_success'],
                'reason': f"{learning_data['count']} similar users found this valuable"
            })

        return recommendations

    @classmethod
    def share_learning_between_agents(cls, source_user, target_users, domain, min_confidence=0.7):
        """
        Share high-confidence learnings from one user to similar users
        Multi-agent learning propagation

        Args:
            source_user: User whose learning to share
            target_users: List of users to share with
            domain: Learning domain to share
            min_confidence: Minimum confidence to share

        Returns:
            Number of learnings shared
        """
        shared_count = 0

        # Get source user's high-confidence learnings
        source_learnings = cls.objects.filter(
            user=source_user,
            learning_domain=domain,
            is_active=True,
            confidence_score__gte=min_confidence
        )

        for learning in source_learnings:
            for target_user in target_users:
                # Check if target already has this learning
                existing = cls.objects.filter(
                    user=target_user,
                    agent_name=learning.agent_name,
                    learning_domain=learning.learning_domain
                ).first()

                if existing:
                    # Blend learnings - weighted average
                    existing.confidence_score = (
                        existing.confidence_score * 0.7 +  # Keep 70% of original
                        learning.confidence_score * 0.3     # Add 30% of shared
                    )
                    existing.learning_content = {
                        **existing.learning_content,
                        'shared_from_users': existing.learning_content.get('shared_from_users', []) + [source_user.id]
                    }
                    existing.save()
                else:
                    # Create new learning with lower confidence
                    cls.objects.create(
                        user=target_user,
                        agent_name=learning.agent_name,
                        learning_domain=learning.learning_domain,
                        learning_content={
                            **learning.learning_content,
                            'shared_from_user': source_user.id,
                            'collaborative': True
                        },
                        confidence_score=learning.confidence_score * 0.6,  # Reduce confidence for shared
                        learning_source='interaction_mining',
                        context_metadata={
                            'shared_at': timezone.now().isoformat(),
                            'original_confidence': learning.confidence_score
                        }
                    )

                shared_count += 1

        return shared_count

    def get_learning_cohort(self, min_similarity=0.5):
        """
        Find users with similar learning patterns

        Args:
            min_similarity: Minimum similarity score (0-1)

        Returns:
            List of similar users with similarity scores
        """
        # Get this user's learning profile
        user_profile = self.__class__.objects.filter(
            user=self.user,
            is_active=True
        ).values_list('learning_domain', 'confidence_score')

        user_domains = {domain: conf for domain, conf in user_profile}

        # Find users with overlapping learnings
        similar_users = []

        all_users = get_user_model().objects.exclude(id=self.user.id)

        for other_user in all_users:
            other_profile = self.__class__.objects.filter(
                user=other_user,
                is_active=True
            ).values_list('learning_domain', 'confidence_score')

            other_domains = {domain: conf for domain, conf in other_profile}

            # Calculate Jaccard similarity
            common_domains = set(user_domains.keys()) & set(other_domains.keys())
            all_domains = set(user_domains.keys()) | set(other_domains.keys())

            if len(all_domains) == 0:
                continue

            jaccard_similarity = len(common_domains) / len(all_domains)

            # Calculate confidence correlation for common domains
            if common_domains:
                conf_correlation = sum(
                    abs(user_domains[d] - other_domains[d])
                    for d in common_domains
                ) / len(common_domains)

                # Invert so higher is better (0 = identical, 1 = completely different)
                conf_correlation = 1 - conf_correlation
            else:
                conf_correlation = 0

            # Combined similarity score
            similarity = (jaccard_similarity + conf_correlation) / 2

            if similarity >= min_similarity:
                similar_users.append({
                    'user': other_user,
                    'similarity': similarity,
                    'common_learnings': len(common_domains)
                })

        return sorted(similar_users, key=lambda x: x['similarity'], reverse=True)