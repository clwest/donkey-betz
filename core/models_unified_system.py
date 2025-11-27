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


# =============================================================================
# Session 209: Spider Analytics Models
# =============================================================================

class SpiderAnalytics(models.Model):
    """
    Track spider performance and data quality metrics.

    This model stores daily aggregated statistics for each spider,
    enabling performance monitoring and optimization.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Spider identification
    spider_name = models.CharField(max_length=100, db_index=True)
    date = models.DateField(db_index=True)

    # Collection metrics
    items_collected = models.IntegerField(default=0)
    unique_topics = models.IntegerField(default=0)
    unique_sources = models.IntegerField(default=0)

    # Quality metrics
    avg_relevance_score = models.FloatField(default=0.0)
    data_freshness_hours = models.FloatField(default=0.0)  # Avg age of data

    # Performance metrics
    execution_time_seconds = models.FloatField(default=0.0)
    errors = models.IntegerField(default=0)
    success_rate = models.FloatField(default=1.0)  # 0.0 to 1.0

    # Storage metrics
    raw_data_size_kb = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        unique_together = ['spider_name', 'date']
        ordering = ['-date', 'spider_name']
        verbose_name = 'Spider Analytics'
        verbose_name_plural = 'Spider Analytics'

    def __str__(self):
        return f"{self.spider_name} - {self.date}"

    @classmethod
    def record_execution(
        cls,
        spider_name: str,
        items_collected: int,
        execution_time: float,
        errors: int = 0,
        topics: list = None,
        sources: list = None
    ):
        """
        Record a spider execution for analytics.

        Args:
            spider_name: Name of the spider
            items_collected: Number of items collected
            execution_time: Execution time in seconds
            errors: Number of errors encountered
            topics: List of extracted topics
            sources: List of data sources
        """
        from django.utils import timezone
        today = timezone.now().date()

        analytics, created = cls.objects.get_or_create(
            spider_name=spider_name,
            date=today,
            defaults={
                'items_collected': items_collected,
                'execution_time_seconds': execution_time,
                'errors': errors,
                'unique_topics': len(topics) if topics else 0,
                'unique_sources': len(sources) if sources else 0,
                'success_rate': 1.0 if errors == 0 else 0.5,
            }
        )

        if not created:
            # Update existing record
            analytics.items_collected += items_collected
            analytics.execution_time_seconds += execution_time
            analytics.errors += errors
            if topics:
                analytics.unique_topics += len(topics)
            if sources:
                analytics.unique_sources += len(sources)
            analytics.success_rate = 1 - (analytics.errors / max(1, analytics.items_collected + analytics.errors))
            analytics.save()

        return analytics

    @classmethod
    def get_spider_performance(cls, spider_name: str, days: int = 7) -> dict:
        """Get performance summary for a spider over the given period."""
        from django.utils import timezone
        from django.db.models import Sum, Avg

        since = timezone.now().date() - timezone.timedelta(days=days)

        stats = cls.objects.filter(
            spider_name=spider_name,
            date__gte=since
        ).aggregate(
            total_items=Sum('items_collected'),
            total_errors=Sum('errors'),
            avg_execution_time=Avg('execution_time_seconds'),
            avg_success_rate=Avg('success_rate'),
            total_topics=Sum('unique_topics'),
        )

        return {
            'spider_name': spider_name,
            'period_days': days,
            'total_items': stats['total_items'] or 0,
            'total_errors': stats['total_errors'] or 0,
            'avg_execution_time': stats['avg_execution_time'] or 0,
            'avg_success_rate': stats['avg_success_rate'] or 0,
            'total_topics': stats['total_topics'] or 0,
        }


class TrendSnapshot(models.Model):
    """
    Store trending topic snapshots over time.

    This enables historical trend analysis and tracking
    how topics rise and fall in popularity.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Topic identification
    topic = models.CharField(max_length=200, db_index=True)
    category = models.CharField(max_length=50, db_index=True, blank=True, default='')

    # Trend metrics
    score = models.FloatField(default=0.0)  # Calculated trend score
    mention_count = models.IntegerField(default=1)
    source_count = models.IntegerField(default=1)

    # Sources tracking
    sources = models.JSONField(default=list)  # List of spider names

    # Time tracking
    first_seen = models.DateTimeField()
    last_seen = models.DateTimeField()
    snapshot_date = models.DateField(db_index=True)

    # Velocity (change tracking)
    previous_score = models.FloatField(default=0.0)
    score_change = models.FloatField(default=0.0)  # Positive = rising, negative = falling
    is_emerging = models.BooleanField(default=False)  # New/fast-growing topic
    is_declining = models.BooleanField(default=False)  # Losing momentum

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        unique_together = ['topic', 'snapshot_date']
        ordering = ['-snapshot_date', '-score']
        verbose_name = 'Trend Snapshot'
        verbose_name_plural = 'Trend Snapshots'

    def __str__(self):
        return f"{self.topic} ({self.snapshot_date}) - Score: {self.score:.2f}"

    @classmethod
    def capture_snapshot(cls, trends: list, category: str = '') -> list:
        """
        Capture a snapshot of current trends.

        Args:
            trends: List of trend dicts from SpiderIntelligenceService
            category: Optional category filter

        Returns:
            List of created/updated TrendSnapshot objects
        """
        from django.utils import timezone
        now = timezone.now()
        today = now.date()

        snapshots = []
        for trend in trends:
            topic = trend.get('topic', '')
            if not topic:
                continue

            # Get or create snapshot for today
            snapshot, created = cls.objects.get_or_create(
                topic=topic,
                snapshot_date=today,
                defaults={
                    'category': category,
                    'score': trend.get('score', 0),
                    'mention_count': trend.get('mentions', 1),
                    'source_count': trend.get('source_count', 1),
                    'sources': trend.get('sources', []),
                    'first_seen': now,
                    'last_seen': now,
                }
            )

            if not created:
                # Update existing
                snapshot.previous_score = snapshot.score
                snapshot.score = trend.get('score', snapshot.score)
                snapshot.mention_count = trend.get('mentions', snapshot.mention_count)
                snapshot.source_count = trend.get('source_count', snapshot.source_count)
                snapshot.sources = trend.get('sources', snapshot.sources)
                snapshot.last_seen = now

                # Calculate change
                if snapshot.previous_score > 0:
                    snapshot.score_change = (snapshot.score - snapshot.previous_score) / snapshot.previous_score
                else:
                    snapshot.score_change = 1.0 if snapshot.score > 0 else 0

                # Mark emerging/declining
                snapshot.is_emerging = snapshot.score_change > 0.2  # 20% growth
                snapshot.is_declining = snapshot.score_change < -0.2  # 20% decline

                snapshot.save()

            snapshots.append(snapshot)

        return snapshots

    @classmethod
    def get_trend_history(cls, topic: str, days: int = 30) -> list:
        """Get historical trend data for a topic."""
        from django.utils import timezone

        since = timezone.now().date() - timezone.timedelta(days=days)

        return list(cls.objects.filter(
            topic=topic,
            snapshot_date__gte=since
        ).order_by('snapshot_date').values(
            'snapshot_date', 'score', 'mention_count', 'source_count'
        ))

    @classmethod
    def get_emerging_trends(cls, days: int = 7, limit: int = 10) -> list:
        """Get topics that are emerging (fast-growing)."""
        from django.utils import timezone

        since = timezone.now().date() - timezone.timedelta(days=days)

        return list(cls.objects.filter(
            snapshot_date__gte=since,
            is_emerging=True
        ).order_by('-score_change')[:limit].values(
            'topic', 'score', 'score_change', 'mention_count', 'sources'
        ))

    @classmethod
    def get_declining_trends(cls, days: int = 7, limit: int = 10) -> list:
        """Get topics that are declining (losing momentum)."""
        from django.utils import timezone

        since = timezone.now().date() - timezone.timedelta(days=days)

        return list(cls.objects.filter(
            snapshot_date__gte=since,
            is_declining=True
        ).order_by('score_change')[:limit].values(
            'topic', 'score', 'score_change', 'mention_count', 'sources'
        ))


# =============================================================================
# Session 210: Implicit Learning Models
# =============================================================================

class UserBehaviorSignal(models.Model):
    """
    Track individual user behavior signals for implicit learning.

    Each signal represents a user action (download, share, delete, etc.)
    that indicates their preference toward certain styles/models.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # User and content
    user_id = models.IntegerField(db_index=True)
    content_id = models.CharField(max_length=100, db_index=True, blank=True, default='')

    # Signal type and weight
    signal_type = models.CharField(max_length=50, db_index=True)
    # Types: 'generation', 'download', 'share', 'delete', 'view_long', 'view_short',
    #        'regenerate', 'style_use', 'favorite'

    weight = models.FloatField(default=0.0)
    # Weight indicates signal strength: positive = liked, negative = disliked
    # share=1.0, download=0.7, favorite=0.8, view_long=0.4, delete=-0.5, etc.

    # Metadata (style, model, prompt keywords, etc.)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id', 'signal_type']),
            models.Index(fields=['user_id', 'created_at']),
        ]
        verbose_name = 'User Behavior Signal'
        verbose_name_plural = 'User Behavior Signals'

    def __str__(self):
        return f"User {self.user_id} - {self.signal_type} ({self.weight:+.2f})"


class UserPreferenceProfile(models.Model):
    """
    Aggregated user preference profile built from behavior signals.

    This is updated incrementally as new signals come in, providing
    a quick lookup of user preferences without recalculating.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user_id = models.IntegerField(unique=True, db_index=True)

    # Aggregated scores
    style_scores = models.JSONField(default=dict)  # {"cyberpunk": 5.2, "anime": 3.1, ...}
    model_scores = models.JSONField(default=dict)  # {"stable-diffusion": 4.0, "dall-e": 2.5}

    # Quick access fields
    top_styles = models.JSONField(default=list)  # Top 5 styles
    top_models = models.JSONField(default=list)  # Top 3 models

    # Stats
    total_signals = models.IntegerField(default=0)
    total_generations = models.IntegerField(default=0)
    total_downloads = models.IntegerField(default=0)
    total_shares = models.IntegerField(default=0)

    # Confidence in preferences (0-1)
    confidence = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'User Preference Profile'
        verbose_name_plural = 'User Preference Profiles'

    def __str__(self):
        return f"Preferences for User {self.user_id} ({self.total_signals} signals)"

    def get_top_style(self) -> str:
        """Get user's favorite style."""
        if self.top_styles:
            return self.top_styles[0]
        if self.style_scores:
            return max(self.style_scores.items(), key=lambda x: x[1])[0]
        return None

    def recalculate_top_styles(self):
        """Recalculate top styles from scores."""
        if self.style_scores:
            sorted_styles = sorted(
                self.style_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            self.top_styles = [s[0] for s in sorted_styles[:5]]

    def recalculate_top_models(self):
        """Recalculate top models from scores."""
        if self.model_scores:
            sorted_models = sorted(
                self.model_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            self.top_models = [m[0] for m in sorted_models[:3]]


class StyleEvolution(models.Model):
    """
    Track how user's style preferences evolve over time.

    Daily snapshots of style distribution allow us to see
    how preferences change and identify trends.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user_id = models.IntegerField(db_index=True)
    date = models.DateField(db_index=True)
    domain = models.CharField(max_length=50, default='image')  # image, video, audio, 3d

    # Style distribution for this day
    style_distribution = models.JSONField(default=dict)
    # {"cyberpunk": 0.35, "anime": 0.25, "watercolor": 0.15, ...}

    # Top styles for quick access
    top_styles = models.JSONField(default=list)  # ["cyberpunk", "anime", "watercolor"]

    # Metrics
    total_generations = models.IntegerField(default=0)
    total_downloads = models.IntegerField(default=0)
    satisfaction_rate = models.FloatField(default=0.0)  # Downloads / Generations

    # Confidence in this snapshot (based on data volume)
    confidence = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        unique_together = ['user_id', 'date', 'domain']
        ordering = ['-date']
        verbose_name = 'Style Evolution'
        verbose_name_plural = 'Style Evolutions'

    def __str__(self):
        return f"User {self.user_id} - {self.date} ({self.domain})"

    @classmethod
    def capture_daily_snapshot(cls, user_id: int, domain: str = 'image'):
        """Capture a daily snapshot of user's style preferences."""
        from django.utils import timezone
        from django.db.models import Count, Sum

        today = timezone.now().date()

        # Get today's signals for this user
        signals = UserBehaviorSignal.objects.filter(
            user_id=user_id,
            created_at__date=today
        )

        # Calculate style distribution
        style_counts = {}
        total_weight = 0

        for signal in signals:
            style = (signal.metadata or {}).get('style')
            if style and signal.weight > 0:
                style_counts[style] = style_counts.get(style, 0) + signal.weight
                total_weight += signal.weight

        # Normalize to distribution
        style_distribution = {}
        if total_weight > 0:
            style_distribution = {
                k: v / total_weight
                for k, v in style_counts.items()
            }

        # Get top styles
        top_styles = sorted(
            style_distribution.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        top_style_names = [s[0] for s in top_styles]

        # Calculate metrics
        total_generations = signals.filter(signal_type='generation').count()
        total_downloads = signals.filter(signal_type='download').count()
        satisfaction = total_downloads / max(1, total_generations)

        # Create or update snapshot
        snapshot, created = cls.objects.update_or_create(
            user_id=user_id,
            date=today,
            domain=domain,
            defaults={
                'style_distribution': style_distribution,
                'top_styles': top_style_names,
                'total_generations': total_generations,
                'total_downloads': total_downloads,
                'satisfaction_rate': satisfaction,
                'confidence': min(1.0, total_generations / 10),
            }
        )

        return snapshot

    @classmethod
    def get_evolution_timeline(cls, user_id: int, days: int = 30, domain: str = 'image'):
        """Get user's style evolution over time."""
        from django.utils import timezone

        since = timezone.now().date() - timezone.timedelta(days=days)

        return list(cls.objects.filter(
            user_id=user_id,
            domain=domain,
            date__gte=since
        ).order_by('date').values(
            'date', 'style_distribution', 'top_styles',
            'total_generations', 'satisfaction_rate'
        ))


class StyleTrend(models.Model):
    """
    Track global style trends across all users.

    This helps identify what's popular and can inform recommendations.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    style_name = models.CharField(max_length=100, db_index=True)
    date = models.DateField(db_index=True)
    domain = models.CharField(max_length=50, default='image')

    # Usage metrics
    usage_count = models.IntegerField(default=0)  # Total uses
    unique_users = models.IntegerField(default=0)  # Unique users
    download_count = models.IntegerField(default=0)  # Downloads

    # Quality metrics
    avg_satisfaction = models.FloatField(default=0.0)  # Avg download rate

    # Trend indicators
    previous_usage = models.IntegerField(default=0)
    growth_rate = models.FloatField(default=0.0)  # Percentage growth from yesterday
    is_trending = models.BooleanField(default=False)  # Fast growth
    is_declining = models.BooleanField(default=False)  # Losing popularity

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        unique_together = ['style_name', 'date', 'domain']
        ordering = ['-date', '-usage_count']
        verbose_name = 'Style Trend'
        verbose_name_plural = 'Style Trends'

    def __str__(self):
        status = "📈" if self.is_trending else ("📉" if self.is_declining else "")
        return f"{self.style_name} - {self.date} ({self.usage_count} uses) {status}"

    @classmethod
    def get_trending_styles(cls, days: int = 7, limit: int = 10, domain: str = 'image'):
        """Get currently trending styles."""
        from django.utils import timezone

        since = timezone.now().date() - timezone.timedelta(days=days)

        return list(cls.objects.filter(
            date__gte=since,
            domain=domain,
            is_trending=True
        ).order_by('-growth_rate')[:limit].values(
            'style_name', 'usage_count', 'growth_rate', 'avg_satisfaction'
        ))

    @classmethod
    def get_popular_styles(cls, days: int = 7, limit: int = 10, domain: str = 'image'):
        """Get most popular styles by usage."""
        from django.utils import timezone
        from django.db.models import Sum

        since = timezone.now().date() - timezone.timedelta(days=days)

        return list(cls.objects.filter(
            date__gte=since,
            domain=domain
        ).values('style_name').annotate(
            total_usage=Sum('usage_count'),
            total_downloads=Sum('download_count')
        ).order_by('-total_usage')[:limit])


# =============================================================================
# SESSION 211: A/B TESTING FRAMEWORK
# =============================================================================

class ABExperiment(models.Model):
    """
    Define an A/B test experiment.

    Experiments can test different recommendation strategies, UI variations,
    or any feature where we want to measure user engagement.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Experiment type
    EXPERIMENT_TYPES = [
        ('recommendation', 'Recommendation Strategy'),
        ('ui', 'UI Variation'),
        ('feature', 'Feature Toggle'),
        ('algorithm', 'Algorithm Comparison'),
    ]
    experiment_type = models.CharField(max_length=50, choices=EXPERIMENT_TYPES, default='recommendation')

    # Domain (what area of the app)
    domain = models.CharField(max_length=50, default='style_recommendations')

    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Traffic allocation (percentage of users to include)
    traffic_percentage = models.IntegerField(default=100)  # 0-100

    # Timing
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    # Success metric
    primary_metric = models.CharField(max_length=100, default='conversion_rate')
    # conversion_rate, click_rate, engagement_time, satisfaction_score

    # Configuration
    config = models.JSONField(default=dict, blank=True)
    # {"min_sample_size": 100, "confidence_level": 0.95}

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by_id = models.IntegerField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        verbose_name = 'A/B Experiment'
        verbose_name_plural = 'A/B Experiments'

    def __str__(self):
        return f"{self.name} ({self.status})"

    @property
    def is_active(self):
        """Check if experiment is currently active."""
        from django.utils import timezone
        now = timezone.now()

        if self.status != 'running':
            return False

        if self.start_date and now < self.start_date:
            return False

        if self.end_date and now > self.end_date:
            return False

        return True


class ABVariant(models.Model):
    """
    A variant within an A/B experiment.

    Each experiment has at least 2 variants (control + treatment).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    experiment = models.ForeignKey(ABExperiment, on_delete=models.CASCADE, related_name='variants')

    name = models.CharField(max_length=100)  # 'control', 'variant_a', 'variant_b'
    description = models.TextField(blank=True)

    is_control = models.BooleanField(default=False)

    # Traffic weight within this experiment (relative to other variants)
    weight = models.IntegerField(default=50)  # Default 50/50 split

    # Variant configuration (what's different about this variant)
    config = models.JSONField(default=dict)
    # For recommendations: {"strategy": "temporal_first", "boost_trending": true}
    # For UI: {"button_color": "green", "show_explanations": true}

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['is_control', 'name']
        verbose_name = 'A/B Variant'
        verbose_name_plural = 'A/B Variants'

    def __str__(self):
        control = " (control)" if self.is_control else ""
        return f"{self.experiment.name} - {self.name}{control}"


class ABAssignment(models.Model):
    """
    Track which variant a user is assigned to.

    Users are consistently assigned to the same variant for the duration
    of an experiment (sticky assignment).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    experiment = models.ForeignKey(ABExperiment, on_delete=models.CASCADE, related_name='assignments')
    variant = models.ForeignKey(ABVariant, on_delete=models.CASCADE, related_name='assignments')

    user_id = models.IntegerField(db_index=True)
    # Or for anonymous users:
    session_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)

    assigned_at = models.DateTimeField(auto_now_add=True)

    # Track if user has seen the variant (exposure)
    exposed = models.BooleanField(default=False)
    exposed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        unique_together = [
            ['experiment', 'user_id'],
            ['experiment', 'session_id'],
        ]
        verbose_name = 'A/B Assignment'
        verbose_name_plural = 'A/B Assignments'

    def __str__(self):
        user = f"User {self.user_id}" if self.user_id else f"Session {self.session_id}"
        return f"{user} -> {self.variant.name}"


class ABConversion(models.Model):
    """
    Track conversions (successful outcomes) for A/B tests.

    A conversion is when a user takes the desired action
    (e.g., applies a recommended style, downloads content).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    assignment = models.ForeignKey(ABAssignment, on_delete=models.CASCADE, related_name='conversions')

    # What action triggered the conversion
    CONVERSION_TYPES = [
        ('click', 'Clicked Recommendation'),
        ('apply', 'Applied Style'),
        ('download', 'Downloaded Content'),
        ('share', 'Shared Content'),
        ('purchase', 'Made Purchase'),
        ('signup', 'Signed Up'),
        ('engagement', 'Engaged with Feature'),
    ]
    conversion_type = models.CharField(max_length=50, choices=CONVERSION_TYPES)

    # Value of the conversion (for revenue tracking)
    value = models.FloatField(default=1.0)

    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)
    # {"style_applied": "cyberpunk", "time_to_convert": 5.2}

    converted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-converted_at']
        verbose_name = 'A/B Conversion'
        verbose_name_plural = 'A/B Conversions'

    def __str__(self):
        return f"{self.assignment} - {self.conversion_type}"


class ABExperimentResult(models.Model):
    """
    Cached/computed results for an experiment.

    Updated periodically to avoid recalculating on every request.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    experiment = models.OneToOneField(ABExperiment, on_delete=models.CASCADE, related_name='results')

    # Per-variant statistics (JSON)
    variant_stats = models.JSONField(default=dict)
    # {
    #     "variant_id": {
    #         "assignments": 150,
    #         "exposures": 140,
    #         "conversions": 35,
    #         "conversion_rate": 0.25,
    #         "total_value": 35.0,
    #         "avg_value": 1.0
    #     }
    # }

    # Statistical significance
    is_significant = models.BooleanField(default=False)
    confidence_level = models.FloatField(default=0.0)  # 0.0 to 1.0
    p_value = models.FloatField(null=True, blank=True)

    # Winner (if significant)
    winning_variant = models.ForeignKey(
        ABVariant, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='won_experiments'
    )
    lift_percentage = models.FloatField(null=True, blank=True)  # % improvement over control

    # Timing
    computed_at = models.DateTimeField(auto_now=True)
    sample_size = models.IntegerField(default=0)

    class Meta:
        app_label = 'core'
        verbose_name = 'A/B Experiment Result'
        verbose_name_plural = 'A/B Experiment Results'

    def __str__(self):
        status = "Significant" if self.is_significant else "Not Significant"
        return f"{self.experiment.name} Results ({status})"


# =============================================================================
# SESSION 212: CUSTOM WORKFLOW BUILDER MODELS
# =============================================================================

class CustomWorkflow(models.Model):
    """
    User-created custom workflow templates.

    Session 212: Allows users to create, save, and share their own workflows.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Ownership
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='custom_workflows'
    )

    # Basic info
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)  # URL-friendly name
    description = models.TextField(blank=True)
    content_type = models.CharField(max_length=50, default='custom')
    category = models.CharField(max_length=50, default='custom')

    # Sharing
    is_public = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    use_count = models.IntegerField(default=0)

    # Configuration
    config = models.JSONField(default=dict, blank=True)  # Global workflow config

    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    schedule_cron = models.CharField(max_length=100, blank=True)  # Cron expression
    last_run_at = models.DateTimeField(null=True, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True)

    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Custom Workflow'
        verbose_name_plural = 'Custom Workflows'
        ordering = ['-updated_at']
        unique_together = [('created_by', 'slug')]

    def __str__(self):
        return f"{self.name} (by {self.created_by})"

    def to_workflow_definition(self):
        """Convert to the format expected by WorkflowOrchestrationAgent."""
        return {
            'description': self.description,
            'content_type': self.content_type,
            'steps': [step.to_step_definition() for step in self.steps.all().order_by('order')]
        }


class CustomWorkflowStep(models.Model):
    """
    Individual step within a custom workflow.

    Session 212: Each step references an agent and defines parameters.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    workflow = models.ForeignKey(
        CustomWorkflow, on_delete=models.CASCADE,
        related_name='steps'
    )

    # Step definition
    order = models.IntegerField()  # 1, 2, 3...
    name = models.CharField(max_length=100)  # Human-readable step name
    description = models.TextField(blank=True)

    # Agent reference
    AGENT_CHOICES = [
        ('web_search', 'Web Search'),
        ('coleadership_agent', 'Executive Team Review'),
        ('image_generation_agent', 'Image Generation'),
        ('video_generation_agent', 'Video Generation'),
        ('audio_generation_agent', 'Audio Generation'),
        ('image_selection', 'Image Selection'),
        ('image_variation_agent', 'Image Variations'),
        ('create_project_from_research', 'Create Project'),
    ]
    agent = models.CharField(max_length=50, choices=AGENT_CHOICES)

    # Step configuration
    config = models.JSONField(default=dict, blank=True)  # Step-specific config
    # Example config: {"prompt_template": "...", "width": 1024, "height": 1024}

    # Conditional execution
    condition = models.JSONField(default=dict, blank=True)  # Run if condition met
    # Example: {"previous_step_success": true, "has_images": true}

    # Error handling
    is_required = models.BooleanField(default=True)  # If false, workflow continues on failure
    retry_count = models.IntegerField(default=0)  # Number of retries on failure

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Custom Workflow Step'
        verbose_name_plural = 'Custom Workflow Steps'
        ordering = ['workflow', 'order']
        unique_together = [('workflow', 'order')]

    def __str__(self):
        return f"Step {self.order}: {self.name} ({self.agent})"

    def to_step_definition(self):
        """Convert to the format expected by WorkflowOrchestrationAgent."""
        return {
            'step': self.order,
            'name': self.name,
            'agent': self.agent,
            'description': self.description,
            'config': self.config,
        }


class WorkflowExecution(models.Model):
    """
    Track workflow execution history.

    Session 212: Records each time a workflow (built-in or custom) is executed.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Execution info
    workflow_type = models.CharField(max_length=50)  # 'builtin' or 'custom'
    workflow_name = models.CharField(max_length=200)
    custom_workflow = models.ForeignKey(
        CustomWorkflow, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='executions'
    )

    # User who triggered
    executed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='core_workflow_executions'
    )

    # Execution parameters
    topic = models.CharField(max_length=500)
    parameters = models.JSONField(default=dict)

    # Results
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    step_results = models.JSONField(default=list)  # List of step outcomes
    error_message = models.TextField(blank=True)

    # Output references
    project_id = models.UUIDField(null=True, blank=True)
    image_ids = models.JSONField(default=list)
    video_ids = models.JSONField(default=list)

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Workflow Execution'
        verbose_name_plural = 'Workflow Executions'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.workflow_name} ({self.status}) - {self.topic[:50]}"

    def complete(self, success: bool, error: str = None):
        """Mark workflow as complete."""
        self.status = 'completed' if success else 'failed'
        self.error_message = error or ''
        self.completed_at = timezone.now()
        self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        self.save()


class ScheduledWorkflow(models.Model):
    """
    Track scheduled workflow runs.

    Session 212: Manages scheduled workflow executions via Celery Beat.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Workflow reference
    custom_workflow = models.OneToOneField(
        CustomWorkflow, on_delete=models.CASCADE,
        related_name='schedule'
    )

    # Schedule info
    cron_expression = models.CharField(max_length=100)  # e.g., "0 9 * * 1" (9am every Monday)
    timezone = models.CharField(max_length=50, default='America/Denver')

    # Default parameters for scheduled runs
    default_topic = models.CharField(max_length=500)
    default_parameters = models.JSONField(default=dict)

    # Status
    is_active = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    last_run_status = models.CharField(max_length=20, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True)
    run_count = models.IntegerField(default=0)

    # Celery task reference
    celery_task_id = models.CharField(max_length=200, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Scheduled Workflow'
        verbose_name_plural = 'Scheduled Workflows'

    def __str__(self):
        return f"Schedule: {self.custom_workflow.name} ({self.cron_expression})"