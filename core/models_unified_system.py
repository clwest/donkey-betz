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

    # =========================================================================
    # Session 223: Creative Intelligence Empire - Opportunity Scoring Fields
    # =========================================================================

    # Source linkage to spider data
    spider_data = models.ForeignKey(
        'SpiderData',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scored_opportunities',
        help_text="Link to spider-collected data that generated this opportunity"
    )

    # Source type categorization
    SOURCE_TYPE_CHOICES = [
        ('trend', 'Trending Topic'),
        ('job', 'Job/Gig Opportunity'),
        ('product', 'Product Demand'),
        ('news', 'News Event'),
        ('competition', 'Competitor Gap'),
        ('seasonal', 'Seasonal Demand'),
        ('viral', 'Viral Content'),
        ('tech', 'Technology Trend'),
    ]
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPE_CHOICES,
        null=True,
        blank=True,
        help_text="What kind of data generated this opportunity"
    )

    # Category for content creation
    CATEGORY_CHOICES = [
        ('digital_product', 'Digital Product'),
        ('freelance', 'Freelance Service'),
        ('content', 'Content Creation'),
        ('template', 'Template/Asset'),
        ('course', 'Course/Education'),
        ('software', 'Software/Tool'),
        ('consulting', 'Consulting'),
        ('affiliate', 'Affiliate Marketing'),
    ]
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        null=True,
        blank=True,
        help_text="Category for content creation opportunity"
    )

    # Scoring fields (1-100) - THE CORE OF THE OPPORTUNITY ENGINE
    profit_potential = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Estimated profit potential (1-100)"
    )
    competition_level = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Competition level - higher means MORE competition (1-100)"
    )
    effort_required = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Effort required - higher means MORE effort (1-100)"
    )
    time_sensitivity = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Time sensitivity - higher means MORE urgent (1-100)"
    )
    overall_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Overall opportunity score (calculated from other scores)"
    )

    # Content suggestions for capitalizing on opportunity
    suggested_content_types = models.JSONField(
        default=list,
        blank=True,
        help_text="List of content types: ['logo', 'thumbnail', 'video']"
    )
    suggested_workflows = models.JSONField(
        default=list,
        blank=True,
        help_text="List of recommended workflows to execute"
    )

    # Financial estimates
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated cost to create content for this opportunity"
    )

    # Supporting data
    keywords = models.JSONField(
        default=list,
        blank=True,
        help_text="Related keywords/tags"
    )
    market_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Market research data"
    )
    competitor_info = models.JSONField(
        default=dict,
        blank=True,
        help_text="Competitor analysis"
    )

    # Advisor consultation
    advisor_recommendations = models.JSONField(
        default=dict,
        blank=True,
        help_text="Recommendations from advisors consulted about this opportunity"
    )

    # Additional timestamps
    scored_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this opportunity was scored"
    )
    acted_on_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When user started acting on this opportunity"
    )

    @property
    def is_scored(self):
        """Check if this opportunity has been scored."""
        return all([
            self.profit_potential is not None,
            self.competition_level is not None,
            self.effort_required is not None,
            self.time_sensitivity is not None,
            self.overall_score is not None
        ])

    @property
    def estimated_roi(self):
        """Calculate estimated ROI."""
        if self.estimated_cost and self.estimated_cost > 0:
            return ((self.potential_revenue - self.estimated_cost) / self.estimated_cost) * 100
        return 0

    @property
    def urgency_level(self):
        """Categorize urgency based on time sensitivity."""
        if not self.time_sensitivity:
            return 'unknown'
        if self.time_sensitivity >= 80:
            return 'critical'
        elif self.time_sensitivity >= 60:
            return 'high'
        elif self.time_sensitivity >= 40:
            return 'medium'
        else:
            return 'low'

    def calculate_overall_score(self):
        """
        Calculate the overall score based on individual factors.

        Formula:
        - Profit potential contributes positively (weight: 0.35)
        - Low competition contributes positively (invert: 100 - competition)
        - Low effort contributes positively (invert: 100 - effort) (weight: 0.20)
        - Time sensitivity adds urgency bonus (weight: 0.10)
        """
        if not all([self.profit_potential, self.competition_level,
                    self.effort_required, self.time_sensitivity]):
            return None

        # Invert competition and effort (lower is better for overall score)
        competition_score = 100 - self.competition_level
        effort_score = 100 - self.effort_required

        # Weighted combination
        score = (
            self.profit_potential * 0.35 +
            competition_score * 0.35 +
            effort_score * 0.20 +
            self.time_sensitivity * 0.10
        )

        return min(100, max(1, int(score)))

    def score_opportunity(self, save=True):
        """Calculate and save the overall score."""
        from django.utils import timezone
        self.overall_score = self.calculate_overall_score()
        if self.overall_score:
            self.scored_at = timezone.now()
            if save:
                self.save()
        return self.overall_score

    class Meta:
        app_label = 'core'
        ordering = ['-match_score', '-created_at']


# =============================================================================
# Session 223: Opportunity Scoring Support Models
# =============================================================================

class OpportunityScore(models.Model):
    """
    Detailed scoring breakdown and reasoning for an opportunity.

    This provides transparency into how an opportunity was scored
    and allows for score refinement over time.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.OneToOneField(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='score_details'
    )

    # Scoring breakdown with reasoning
    profit_reasoning = models.TextField(
        blank=True,
        help_text="Explanation for profit potential score"
    )
    competition_reasoning = models.TextField(
        blank=True,
        help_text="Explanation for competition level score"
    )
    effort_reasoning = models.TextField(
        blank=True,
        help_text="Explanation for effort required score"
    )
    timing_reasoning = models.TextField(
        blank=True,
        help_text="Explanation for time sensitivity score"
    )

    # Confidence in scoring
    confidence_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        default=70,
        help_text="Confidence in the accuracy of this scoring (1-100)"
    )

    # Data sources used for scoring
    data_sources = models.JSONField(
        default=list,
        help_text="List of data sources used to calculate scores"
    )

    # Advisor input
    advisors_consulted = models.JSONField(
        default=list,
        help_text="List of advisors who provided input"
    )

    # Scoring metadata
    scoring_model_version = models.CharField(
        max_length=20,
        default='v1.0',
        help_text="Version of the scoring algorithm used"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'

    def __str__(self):
        return f"Score Details for: {self.opportunity.title}"


class OpportunityAction(models.Model):
    """
    Track actions taken on opportunities.

    This enables the learning loop by recording what was done
    and eventually tracking the outcomes.
    """

    ACTION_TYPE_CHOICES = [
        ('viewed', 'Viewed'),
        ('analyzed', 'Analyzed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('started', 'Started Creating'),
        ('content_created', 'Content Created'),
        ('published', 'Published'),
        ('revenue_logged', 'Revenue Logged'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='actions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    action_type = models.CharField(max_length=30, choices=ACTION_TYPE_CHOICES)

    # What was created/done
    content_ids = models.JSONField(
        default=list,
        help_text="IDs of content created for this opportunity"
    )
    workflow_used = models.CharField(
        max_length=100,
        blank=True,
        help_text="Which workflow was used"
    )

    # Outcome tracking (for learning loop)
    outcome = models.JSONField(
        default=dict,
        help_text="Outcome data: revenue, engagement, etc."
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action_type} on {self.opportunity.title}"


class OpportunityRevenue(models.Model):
    """
    Session 224: Track actual revenue generated from opportunities.

    This closes the loop between discovered opportunities and real income,
    enabling the learning system to improve predictions over time.
    """

    REVENUE_STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('received', 'Received'),
        ('partial', 'Partial Payment'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    CONTENT_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('3d_model', '3D Model'),
        ('template', 'Template'),
        ('bundle', 'Bundle'),
        ('service', 'Service/Freelance'),
        ('other', 'Other'),
    ]

    PLATFORM_CHOICES = [
        ('direct', 'Direct Sale'),
        ('etsy', 'Etsy'),
        ('gumroad', 'Gumroad'),
        ('creative_market', 'Creative Market'),
        ('shutterstock', 'Shutterstock'),
        ('adobe_stock', 'Adobe Stock'),
        ('envato', 'Envato Elements'),
        ('fiverr', 'Fiverr'),
        ('upwork', 'Upwork'),
        ('freelancer', 'Freelancer'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='revenues'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    # Revenue details
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Total revenue amount"
    )
    currency = models.CharField(max_length=3, default='USD')
    platform_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Platform/marketplace fee"
    )
    net_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Amount after fees"
    )

    # Revenue classification
    status = models.CharField(
        max_length=20,
        choices=REVENUE_STATUS_CHOICES,
        default='received'
    )
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        default='image'
    )
    platform = models.CharField(
        max_length=30,
        choices=PLATFORM_CHOICES,
        default='direct'
    )

    # Content linkage (what content generated this revenue?)
    image_history = models.ForeignKey(
        'content.ImageHistory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opportunity_revenues'
    )
    video_history = models.ForeignKey(
        'content.VideoHistory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opportunity_revenues'
    )
    content_ids = models.JSONField(
        default=list,
        help_text="Additional content IDs associated with this revenue"
    )

    # Prediction accuracy tracking
    estimated_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="What was predicted vs actual"
    )
    prediction_accuracy = models.FloatField(
        null=True,
        blank=True,
        help_text="Accuracy percentage: actual/estimated * 100"
    )

    # Metadata
    description = models.TextField(
        blank=True,
        help_text="Description of the sale/revenue"
    )
    sale_date = models.DateTimeField(
        help_text="When the sale occurred"
    )
    payment_received_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When payment was actually received"
    )
    external_reference = models.CharField(
        max_length=200,
        blank=True,
        help_text="External order ID or reference"
    )

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        ordering = ['-sale_date']
        indexes = [
            models.Index(fields=['opportunity', 'status']),
            models.Index(fields=['user', 'sale_date']),
            models.Index(fields=['platform', 'status']),
        ]

    def save(self, *args, **kwargs):
        # Auto-calculate net amount if not set
        if self.net_amount is None:
            self.net_amount = self.amount - self.platform_fee

        # Calculate prediction accuracy if we have an estimate
        if self.estimated_revenue and self.estimated_revenue > 0:
            self.prediction_accuracy = float(self.amount / self.estimated_revenue * 100)
        elif self.opportunity.potential_revenue and self.opportunity.potential_revenue > 0:
            # Use opportunity's predicted revenue as fallback
            self.estimated_revenue = self.opportunity.potential_revenue
            self.prediction_accuracy = float(self.amount / self.opportunity.potential_revenue * 100)

        super().save(*args, **kwargs)

        # Update opportunity status to 'earning' when revenue is logged
        if self.opportunity.status not in ['earning', 'closed']:
            self.opportunity.status = 'earning'
            self.opportunity.save(update_fields=['status'])

    def __str__(self):
        return f"${self.amount} from {self.opportunity.title}"

    @property
    def prediction_error(self):
        """Calculate the prediction error (actual - estimated)"""
        if self.estimated_revenue:
            return float(self.amount - self.estimated_revenue)
        return None

    @property
    def is_better_than_predicted(self):
        """Did we do better than predicted?"""
        if self.estimated_revenue:
            return self.amount > self.estimated_revenue
        return None


class OpportunityContent(models.Model):
    """
    Session 224: Link content created from opportunities.

    Tracks which content was created as a result of pursuing an opportunity,
    enabling revenue attribution when that content generates income.
    """

    CONTENT_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('3d_model', '3D Model'),
        ('template', 'Template'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='created_content'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)

    # Direct links to content models
    image_history = models.ForeignKey(
        'content.ImageHistory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opportunity_created'
    )
    video_history = models.ForeignKey(
        'content.VideoHistory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opportunity_created'
    )

    # Workflow tracking
    workflow_used = models.CharField(
        max_length=100,
        blank=True,
        help_text="Which workflow created this content"
    )
    workflow_execution_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="ID of the workflow execution"
    )

    # Cost tracking
    production_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Cost to create this content (API costs, etc.)"
    )

    # Status
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    published_platforms = models.JSONField(
        default=list,
        help_text="Where this content was published"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.content_type} for {self.opportunity.title}"

    @property
    def total_revenue(self):
        """Calculate total revenue generated by this content"""
        if self.content_type == 'image' and self.image_history:
            return sum(r.amount for r in self.image_history.opportunity_revenues.all())
        elif self.content_type == 'video' and self.video_history:
            return sum(r.amount for r in self.video_history.opportunity_revenues.all())
        return 0

    @property
    def roi(self):
        """Calculate ROI for this content"""
        if self.production_cost and self.production_cost > 0:
            return float((self.total_revenue - self.production_cost) / self.production_cost * 100)
        return None


class OpportunityPredictionAccuracy(models.Model):
    """
    Session 224: Aggregate prediction accuracy tracking.

    Stores historical accuracy data for the learning loop to improve predictions.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="User-specific accuracy (null for system-wide)"
    )

    # Time period
    period_start = models.DateField()
    period_end = models.DateField()
    period_type = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ]
    )

    # Accuracy metrics
    total_opportunities = models.IntegerField(default=0)
    opportunities_with_revenue = models.IntegerField(default=0)
    conversion_rate = models.FloatField(
        default=0,
        help_text="% of opportunities that generated revenue"
    )

    # Revenue predictions
    total_predicted_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )
    total_actual_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )
    revenue_accuracy = models.FloatField(
        default=0,
        help_text="Actual/Predicted * 100"
    )
    mean_absolute_error = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Average absolute difference between predicted and actual"
    )

    # By category breakdown
    accuracy_by_category = models.JSONField(
        default=dict,
        help_text="Accuracy broken down by opportunity category"
    )
    accuracy_by_source = models.JSONField(
        default=dict,
        help_text="Accuracy broken down by source type"
    )

    # Scoring accuracy
    avg_predicted_score = models.FloatField(default=0)
    avg_actual_performance = models.FloatField(
        default=0,
        help_text="Normalized actual performance score"
    )
    score_correlation = models.FloatField(
        default=0,
        help_text="Correlation between predicted scores and actual outcomes"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-period_start']
        unique_together = ['user', 'period_start', 'period_type']

    def __str__(self):
        user_str = f"User {self.user_id}" if self.user else "System-wide"
        return f"{user_str} Accuracy {self.period_start} to {self.period_end}"


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


# =============================================================================
# SESSION 214: AGENT COLLABORATION MODELS
# =============================================================================

class CollaborationSession(models.Model):
    """
    Track agent collaboration sessions.

    Session 214: Enhanced collaboration tracking with detailed workflow support.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Requester
    requester_agent = models.CharField(max_length=200)

    # Collaboration details
    collaboration_type = models.CharField(max_length=50)  # delegation, consultation, parallel, etc.
    task_description = models.TextField()
    input_data = models.JSONField(default=dict)

    # Participating agents
    participating_agents = models.JSONField(default=list)

    # Status and results
    status = models.CharField(max_length=50, default='pending')
    output_data = models.JSONField(default=dict, blank=True)
    quality_score = models.FloatField(default=0.0)

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    execution_time_ms = models.FloatField(default=0.0)

    # Context
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='collaboration_sessions',
        null=True, blank=True
    )
    workflow_execution_id = models.UUIDField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ['-started_at']
        verbose_name = 'Collaboration Session'
        verbose_name_plural = 'Collaboration Sessions'

    def __str__(self):
        return f"{self.requester_agent} collaboration ({self.collaboration_type})"


class InterAgentMessage(models.Model):
    """
    Store inter-agent messages for communication tracking.

    Session 214: Enables asynchronous agent-to-agent communication.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Message routing
    sender_agent = models.CharField(max_length=200)
    receiver_agent = models.CharField(max_length=200)
    message_type = models.CharField(max_length=50)  # request, response, notification, etc.

    # Content
    content = models.JSONField(default=dict)
    context = models.JSONField(default=dict)

    # Metadata
    priority = models.IntegerField(default=5)  # 1-10, 10 is highest
    correlation_id = models.UUIDField(null=True, blank=True)  # Links related messages
    response_to = models.UUIDField(null=True, blank=True)  # ID of message this responds to

    # Status
    is_read = models.BooleanField(default=False)
    is_processed = models.BooleanField(default=False)

    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        verbose_name = 'Inter-Agent Message'
        verbose_name_plural = 'Inter-Agent Messages'

    def __str__(self):
        return f"{self.sender_agent} -> {self.receiver_agent} ({self.message_type})"


class SharedKnowledge(models.Model):
    """
    Shared knowledge base for agent learning and knowledge transfer.

    Session 214: Enables agents to share and learn from each other's insights.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Knowledge source
    source_agent = models.CharField(max_length=200)

    # Knowledge content
    knowledge_type = models.CharField(max_length=50)  # technique, pattern, insight, skill
    title = models.CharField(max_length=500)
    description = models.TextField()
    knowledge_content = models.JSONField(default=dict)

    # Metadata
    domain = models.CharField(max_length=100)  # image, video, audio, research, etc.
    tags = models.JSONField(default=list)

    # Usage tracking
    applied_count = models.IntegerField(default=0)
    effectiveness_score = models.FloatField(default=0.0)

    # Agents that have learned this
    learned_by_agents = models.JSONField(default=list)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        ordering = ['-effectiveness_score', '-applied_count']
        verbose_name = 'Shared Knowledge'
        verbose_name_plural = 'Shared Knowledge'

    def __str__(self):
        return f"{self.title} by {self.source_agent} ({self.knowledge_type})"


class AgentPerformanceMetric(models.Model):
    """
    Track agent performance metrics over time.

    Session 214: Comprehensive performance tracking for agent optimization.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent_name = models.CharField(max_length=200, unique=True)

    # Execution metrics
    total_executions = models.IntegerField(default=0)
    successful_executions = models.IntegerField(default=0)
    failed_executions = models.IntegerField(default=0)

    # Collaboration metrics
    total_collaborations = models.IntegerField(default=0)
    successful_collaborations = models.IntegerField(default=0)
    delegations_made = models.IntegerField(default=0)
    delegations_received = models.IntegerField(default=0)
    consultations_given = models.IntegerField(default=0)
    consultations_received = models.IntegerField(default=0)

    # Performance metrics
    avg_response_time_ms = models.FloatField(default=0.0)
    quality_score = models.FloatField(default=0.0)

    # Knowledge metrics
    knowledge_contributions = models.IntegerField(default=0)
    knowledge_consumed = models.IntegerField(default=0)

    # Specialization scores (domain -> score)
    specialization_scores = models.JSONField(default=dict)

    # Activity tracking
    last_execution = models.DateTimeField(null=True, blank=True)
    last_collaboration = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        ordering = ['-quality_score', '-total_executions']
        verbose_name = 'Agent Performance Metric'
        verbose_name_plural = 'Agent Performance Metrics'

    def __str__(self):
        success_rate = self.successful_executions / self.total_executions if self.total_executions > 0 else 0
        return f"{self.agent_name} ({success_rate:.1%} success)"


# =============================================================================
# SESSION 219 PHASE D: WORKFLOW MARKETPLACE MODELS
# =============================================================================

class PublishedWorkflow(models.Model):
    """
    Published workflow in the marketplace.

    Session 219 Phase D: Wraps CustomWorkflow for community sharing.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # The actual workflow
    workflow = models.OneToOneField(
        CustomWorkflow, on_delete=models.CASCADE,
        related_name='publication'
    )

    # Author info
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='published_workflows'
    )

    # Marketplace metadata
    title = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)

    # Categorization
    CATEGORY_CHOICES = [
        ('image_generation', 'Image Generation'),
        ('video_creation', 'Video Creation'),
        ('audio_production', 'Audio Production'),
        ('brand_identity', 'Brand Identity'),
        ('social_media', 'Social Media'),
        ('ecommerce', 'E-Commerce'),
        ('research', 'Research & Analysis'),
        ('productivity', 'Productivity'),
        ('other', 'Other'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    tags = models.JSONField(default=list)

    # Media
    preview_image = models.URLField(blank=True)
    preview_images = models.JSONField(default=list)  # List of preview URLs

    # Stats
    download_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)

    # Rating cache (updated when reviews change)
    average_rating = models.FloatField(default=0.0)
    review_count = models.IntegerField(default=0)

    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('removed', 'Removed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    is_featured = models.BooleanField(default=False)

    # Pricing (future: monetization)
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Timestamps
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Published Workflow'
        verbose_name_plural = 'Published Workflows'
        ordering = ['-is_featured', '-download_count', '-published_at']

    def __str__(self):
        return f"{self.title} by {self.author}"

    def update_rating_cache(self):
        """Update cached rating stats from reviews."""
        from django.db.models import Avg, Count
        stats = self.reviews.aggregate(avg=Avg('rating'), count=Count('id'))
        self.average_rating = stats['avg'] or 0.0
        self.review_count = stats['count'] or 0
        self.save(update_fields=['average_rating', 'review_count'])

    def increment_download(self):
        """Increment download count."""
        self.download_count += 1
        self.save(update_fields=['download_count'])
        # Also update the underlying workflow
        if self.workflow:
            self.workflow.use_count += 1
            self.workflow.save(update_fields=['use_count'])

    def increment_view(self):
        """Increment view count."""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class WorkflowReview(models.Model):
    """
    User review of a published workflow.

    Session 219 Phase D: Ratings and reviews for marketplace.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # References
    published_workflow = models.ForeignKey(
        PublishedWorkflow, on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='workflow_reviews'
    )

    # Rating
    rating = models.IntegerField()  # 1-5
    review_text = models.TextField(blank=True)

    # Helpful votes
    helpful_count = models.IntegerField(default=0)
    not_helpful_count = models.IntegerField(default=0)

    # Status
    is_verified_purchase = models.BooleanField(default=False)  # User actually used it

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Workflow Review'
        verbose_name_plural = 'Workflow Reviews'
        ordering = ['-helpful_count', '-created_at']
        unique_together = [('published_workflow', 'user')]

    def __str__(self):
        return f"{self.rating}⭐ by {self.user} on {self.published_workflow.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update parent's rating cache
        self.published_workflow.update_rating_cache()


class WorkflowInstallation(models.Model):
    """
    Track user installations of published workflows.

    Session 219 Phase D: Know who installed what for analytics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # References
    published_workflow = models.ForeignKey(
        PublishedWorkflow, on_delete=models.CASCADE,
        related_name='installations'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='installed_workflows'
    )

    # The cloned workflow
    installed_workflow = models.ForeignKey(
        CustomWorkflow, on_delete=models.SET_NULL,
        null=True, related_name='installation_source'
    )

    # Usage stats
    times_executed = models.IntegerField(default=0)
    last_executed = models.DateTimeField(null=True, blank=True)

    # Timestamps
    installed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Workflow Installation'
        verbose_name_plural = 'Workflow Installations'
        unique_together = [('published_workflow', 'user')]

    def __str__(self):
        return f"{self.user} installed {self.published_workflow.title}"


# =============================================================================
# SESSION 220: REAL-TIME COLLABORATION MODELS
# =============================================================================

class SharedProject(models.Model):
    """
    Collaborative project workspace for multi-user real-time editing.

    Session 220 Phase E: Enable multiple users to work on the same
    creative project simultaneously with real-time sync.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Project details
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    thumbnail = models.URLField(blank=True)

    # Ownership
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='owned_projects'
    )

    # Project content (JSON structure of all content items)
    content = models.JSONField(default=dict)

    # Project settings/configuration
    project_settings = models.JSONField(default=dict)

    # Visibility
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('team', 'Team Only'),
        ('public', 'Public'),
    ]
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')

    # Project status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Version tracking
    version = models.IntegerField(default=1)
    last_edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='last_edited_projects'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Shared Project'
        verbose_name_plural = 'Shared Projects'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} by {self.owner}"

    def increment_version(self):
        """Bump version number after content change"""
        self.version += 1
        self.save(update_fields=['version', 'updated_at'])


class ProjectCollaborator(models.Model):
    """
    Collaborator access to a shared project.

    Session 220 Phase E: Manage who can access and edit projects.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    project = models.ForeignKey(
        SharedProject, on_delete=models.CASCADE,
        related_name='collaborators'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='project_collaborations'
    )

    # Permissions
    ROLE_CHOICES = [
        ('viewer', 'Viewer'),
        ('editor', 'Editor'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='editor')

    # Invitation status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Invited by
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='sent_invitations'
    )

    # Timestamps
    invited_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Project Collaborator'
        verbose_name_plural = 'Project Collaborators'
        unique_together = [('project', 'user')]

    def __str__(self):
        return f"{self.user} ({self.role}) on {self.project.name}"

    def can_edit(self):
        return self.role in ['editor', 'admin'] and self.status == 'accepted'

    def can_manage(self):
        return self.role == 'admin' and self.status == 'accepted'


class ProjectActivity(models.Model):
    """
    Activity log for shared projects.

    Session 220 Phase E: Track all changes for audit and undo.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    project = models.ForeignKey(
        SharedProject, on_delete=models.CASCADE,
        related_name='activities'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='project_activities'
    )

    # Activity type
    ACTION_CHOICES = [
        ('created', 'Created Project'),
        ('edited', 'Edited Content'),
        ('added_content', 'Added Content'),
        ('removed_content', 'Removed Content'),
        ('invited', 'Invited Collaborator'),
        ('joined', 'Joined Project'),
        ('left', 'Left Project'),
        ('settings_changed', 'Changed Settings'),
        ('commented', 'Added Comment'),
    ]
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)

    # Activity details
    details = models.JSONField(default=dict)

    # For undo capability
    previous_state = models.JSONField(null=True, blank=True)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Project Activity'
        verbose_name_plural = 'Project Activities'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} {self.action} on {self.project.name}"


class ProjectPresence(models.Model):
    """
    Track who is currently viewing/editing a project.

    Session 220 Phase E: Real-time presence for collaboration UI.
    This model is frequently updated via WebSocket.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    project = models.ForeignKey(
        SharedProject, on_delete=models.CASCADE,
        related_name='presences'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='project_presences'
    )

    # Connection info
    channel_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    # Cursor/selection state (for showing what others are working on)
    cursor_position = models.JSONField(default=dict)  # {x, y} or element_id
    selection = models.JSONField(default=dict)  # Current selection state

    # Activity status
    STATUS_CHOICES = [
        ('viewing', 'Viewing'),
        ('editing', 'Editing'),
        ('idle', 'Idle'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='viewing')

    # User color (for UI differentiation)
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color

    # Timestamps
    connected_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Project Presence'
        verbose_name_plural = 'Project Presences'
        unique_together = [('project', 'user', 'channel_name')]

    def __str__(self):
        return f"{self.user} ({self.status}) in {self.project.name}"

    @classmethod
    def cleanup_stale(cls, minutes=5):
        """Remove presence records older than X minutes"""
        from django.utils import timezone
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(minutes=minutes)
        return cls.objects.filter(last_activity__lt=cutoff).delete()


class ProjectComment(models.Model):
    """
    Comments on project content for collaboration.

    Session 220 Phase E: Allow discussion within projects.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    project = models.ForeignKey(
        SharedProject, on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='project_comments'
    )

    # Comment content
    text = models.TextField()

    # Position reference (where in the project this comment is attached)
    target_type = models.CharField(max_length=50, blank=True)  # 'content_item', 'canvas', etc.
    target_id = models.CharField(max_length=100, blank=True)  # ID of the target element

    # Threading
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True, related_name='replies'
    )

    # Status
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='resolved_comments'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Project Comment'
        verbose_name_plural = 'Project Comments'
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user} on {self.project.name}"


# =============================================================================
# Session 221 Phase F: Advanced Analytics Models
# =============================================================================

class UsageMetric(models.Model):
    """
    Track usage metrics for all platform features.

    Session 221 Phase F: Analytics foundation for understanding platform usage.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='usage_metrics', null=True, blank=True
    )

    # Metric identification
    METRIC_CATEGORIES = [
        ('image', 'Image Generation'),
        ('video', 'Video Generation'),
        ('audio', 'Audio Generation'),
        ('3d', '3D Generation'),
        ('workflow', 'Workflow Execution'),
        ('agent', 'Agent Execution'),
        ('spider', 'Spider Data'),
        ('collaboration', 'Collaboration'),
        ('api', 'API Call'),
    ]
    category = models.CharField(max_length=20, choices=METRIC_CATEGORIES)
    metric_type = models.CharField(max_length=50)  # e.g., 'generate', 'edit', 'export'
    feature_name = models.CharField(max_length=100)  # e.g., 'ultra_generation', 'runway_video'

    # Metric values
    count = models.IntegerField(default=1)
    value = models.DecimalField(max_digits=15, decimal_places=4, default=0)  # For storing amounts

    # Context
    metadata = models.JSONField(default=dict)  # Additional context

    # API provider tracking
    provider = models.CharField(max_length=50, blank=True)  # 'stability', 'runway', 'elevenlabs'
    endpoint = models.CharField(max_length=200, blank=True)

    # Time tracking
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    duration_ms = models.IntegerField(null=True, blank=True)  # Processing time

    # Aggregation helpers
    hour = models.IntegerField(default=0)  # 0-23
    day_of_week = models.IntegerField(default=0)  # 0-6 (Monday=0)

    class Meta:
        app_label = 'core'
        verbose_name = 'Usage Metric'
        verbose_name_plural = 'Usage Metrics'
        indexes = [
            models.Index(fields=['category', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['feature_name', 'timestamp']),
        ]

    def save(self, *args, **kwargs):
        # Auto-populate time fields
        if self.timestamp:
            self.hour = self.timestamp.hour
            self.day_of_week = self.timestamp.weekday()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category}:{self.metric_type} at {self.timestamp}"


class PerformanceLog(models.Model):
    """
    Track performance metrics for system operations.

    Session 221 Phase F: Monitor system health and performance.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Component identification
    COMPONENT_TYPES = [
        ('api', 'API Endpoint'),
        ('websocket', 'WebSocket'),
        ('database', 'Database'),
        ('cache', 'Cache'),
        ('external', 'External API'),
        ('worker', 'Background Worker'),
        ('ml', 'ML Model'),
    ]
    component_type = models.CharField(max_length=20, choices=COMPONENT_TYPES)
    component_name = models.CharField(max_length=100)

    # Performance data
    response_time_ms = models.IntegerField()  # Milliseconds
    status_code = models.IntegerField(null=True, blank=True)
    success = models.BooleanField(default=True)

    # Error tracking
    error_message = models.TextField(blank=True)
    error_type = models.CharField(max_length=100, blank=True)

    # Resource usage
    memory_mb = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cpu_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Context
    endpoint = models.CharField(max_length=200, blank=True)
    method = models.CharField(max_length=10, blank=True)  # GET, POST, etc.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='performance_logs'
    )

    # Timestamp
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Performance Log'
        verbose_name_plural = 'Performance Logs'
        indexes = [
            models.Index(fields=['component_type', 'timestamp']),
            models.Index(fields=['success', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.component_type}:{self.component_name} - {self.response_time_ms}ms"


class CostTracking(models.Model):
    """
    Track API costs and token usage across all providers.

    Session 221 Phase F: Enable cost monitoring and budget management.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='cost_records', null=True, blank=True
    )

    # Provider and service
    PROVIDERS = [
        ('stability', 'Stability AI'),
        ('runway', 'Runway ML'),
        ('elevenlabs', 'ElevenLabs'),
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('replicate', 'Replicate'),
        ('other', 'Other'),
    ]
    provider = models.CharField(max_length=20, choices=PROVIDERS)
    service = models.CharField(max_length=100)  # e.g., 'ultra_generation', 'gen3_turbo'
    operation = models.CharField(max_length=100)  # e.g., 'generate', 'upscale', 'tts'

    # Cost data
    credits_used = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    estimated_cost_usd = models.DecimalField(max_digits=15, decimal_places=6, default=0)

    # Token tracking (for LLM APIs)
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)

    # Resource tracking (for generation APIs)
    resolution = models.CharField(max_length=20, blank=True)  # e.g., '1024x1024'
    duration_seconds = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Billing period
    billing_period = models.CharField(max_length=7, blank=True)  # YYYY-MM format

    # Context
    request_id = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict)

    # Timestamp
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Cost Tracking'
        verbose_name_plural = 'Cost Tracking Records'
        indexes = [
            models.Index(fields=['provider', 'timestamp']),
            models.Index(fields=['user', 'billing_period']),
            models.Index(fields=['service', 'timestamp']),
        ]

    def save(self, *args, **kwargs):
        # Auto-populate billing period
        if self.timestamp and not self.billing_period:
            self.billing_period = self.timestamp.strftime('%Y-%m')
        # Calculate total tokens
        if self.input_tokens or self.output_tokens:
            self.total_tokens = self.input_tokens + self.output_tokens
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.provider}:{self.service} - ${self.estimated_cost_usd}"


class AnalyticsDashboard(models.Model):
    """
    User-customizable analytics dashboard configuration.

    Session 221 Phase F: Allow users to create custom dashboards.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='analytics_dashboards'
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)

    # Dashboard layout
    layout = models.JSONField(default=dict)  # Grid positions and sizes

    # Widgets configuration
    widgets = models.JSONField(default=list)  # List of widget configs

    # Time range defaults
    DEFAULT_RANGES = [
        ('1h', 'Last Hour'),
        ('24h', 'Last 24 Hours'),
        ('7d', 'Last 7 Days'),
        ('30d', 'Last 30 Days'),
        ('90d', 'Last 90 Days'),
        ('custom', 'Custom Range'),
    ]
    default_time_range = models.CharField(max_length=10, choices=DEFAULT_RANGES, default='24h')

    # Refresh settings
    auto_refresh = models.BooleanField(default=True)
    refresh_interval_seconds = models.IntegerField(default=60)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Analytics Dashboard'
        verbose_name_plural = 'Analytics Dashboards'
        unique_together = [('user', 'name')]

    def __str__(self):
        return f"{self.user}'s Dashboard: {self.name}"


class AnalyticsAlert(models.Model):
    """
    Configurable alerts based on analytics thresholds.

    Session 221 Phase F: Notify users of important metric changes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='analytics_alerts'
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    # Alert conditions
    METRIC_TYPES = [
        ('cost_daily', 'Daily Cost'),
        ('cost_monthly', 'Monthly Cost'),
        ('api_errors', 'API Errors'),
        ('response_time', 'Response Time'),
        ('usage_count', 'Usage Count'),
        ('credits_remaining', 'Credits Remaining'),
    ]
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES)

    OPERATORS = [
        ('gt', 'Greater Than'),
        ('lt', 'Less Than'),
        ('eq', 'Equal To'),
        ('gte', 'Greater Than or Equal'),
        ('lte', 'Less Than or Equal'),
    ]
    operator = models.CharField(max_length=5, choices=OPERATORS)
    threshold_value = models.DecimalField(max_digits=15, decimal_places=4)

    # Notification settings
    notify_email = models.BooleanField(default=False)
    notify_websocket = models.BooleanField(default=True)
    cooldown_minutes = models.IntegerField(default=60)  # Minimum time between alerts

    # Tracking
    last_triggered = models.DateTimeField(null=True, blank=True)
    trigger_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Analytics Alert'
        verbose_name_plural = 'Analytics Alerts'

    def can_trigger(self):
        """Check if alert can be triggered based on cooldown"""
        if not self.last_triggered:
            return True
        elapsed = (timezone.now() - self.last_triggered).total_seconds() / 60
        return elapsed >= self.cooldown_minutes

    def __str__(self):
        return f"Alert: {self.name} ({self.metric_type} {self.operator} {self.threshold_value})"


# =============================================================================
# SESSION 227: PHASE 3 - TEAM POWER (Multi-Agent Collaboration)
# =============================================================================

class AgentRole(models.Model):
    """
    Session 227: Define specialized roles for agents in collaborative workflows.
    Each role has specific capabilities and tool access.
    """
    ROLE_TYPES = [
        ('designer', 'Designer - Creates visual content'),
        ('researcher', 'Researcher - Gathers information'),
        ('reviewer', 'Reviewer - Reviews and critiques work'),
        ('writer', 'Writer - Creates written content'),
        ('analyst', 'Analyst - Analyzes data and trends'),
        ('strategist', 'Strategist - Plans and coordinates'),
        ('optimizer', 'Optimizer - Improves and refines'),
        ('communicator', 'Communicator - Handles messaging'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    role_type = models.CharField(max_length=50, choices=ROLE_TYPES)
    description = models.TextField(blank=True)

    # Capabilities - what this role can do
    capabilities = models.JSONField(default=list, help_text='List of capability strings')
    # e.g., ['image_generation', 'style_transfer', 'logo_design']

    # Tools - which tools this role has access to
    available_tools = models.JSONField(default=list, help_text='List of tool names this role can use')
    # e.g., ['stability_ai', 'runway_ml', 'elevenlabs']

    # Constraints - limits on what this role can do
    constraints = models.JSONField(default=dict, help_text='Role-specific constraints')
    # e.g., {'max_images_per_task': 10, 'requires_approval': False}

    # System prompt additions for this role
    role_prompt = models.TextField(blank=True, help_text='Additional system prompt for this role')

    # Priority (higher = more important in team decisions)
    priority = models.IntegerField(default=5)  # 1-10

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Agent Role'
        verbose_name_plural = 'Agent Roles'
        ordering = ['-priority', 'name']

    def __str__(self):
        return f"{self.name} ({self.role_type})"


class AgentTeam(models.Model):
    """
    Session 227: A team of agents working together on tasks.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Team composition
    agents = models.ManyToManyField('Agent', through='AgentTeamMembership', related_name='teams')

    # Team lead (optional - coordinates the team)
    lead_agent = models.ForeignKey('Agent', on_delete=models.SET_NULL, null=True, blank=True, related_name='led_teams')

    # Team type
    TEAM_TYPES = [
        ('creative', 'Creative Team'),
        ('research', 'Research Team'),
        ('marketing', 'Marketing Team'),
        ('content', 'Content Production Team'),
        ('custom', 'Custom Team'),
    ]
    team_type = models.CharField(max_length=50, choices=TEAM_TYPES, default='custom')

    # Team settings
    settings = models.JSONField(default=dict)
    # e.g., {'auto_assign': True, 'max_concurrent_tasks': 5}

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Agent Team'
        verbose_name_plural = 'Agent Teams'

    def __str__(self):
        return f"{self.name} ({self.team_type})"


class AgentTeamMembership(models.Model):
    """
    Session 227: Membership of an agent in a team with specific role.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(AgentTeam, on_delete=models.CASCADE, related_name='memberships')
    agent = models.ForeignKey('Agent', on_delete=models.CASCADE, related_name='team_memberships')
    role = models.ForeignKey(AgentRole, on_delete=models.SET_NULL, null=True, blank=True)

    # Membership settings
    is_lead = models.BooleanField(default=False)
    can_delegate = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        unique_together = ['team', 'agent']
        verbose_name = 'Agent Team Membership'
        verbose_name_plural = 'Agent Team Memberships'

    def __str__(self):
        return f"{self.agent.name} in {self.team.name}"


class AgentMessage(models.Model):
    """
    Session 227: Inter-agent communication messages.
    Allows agents to communicate and coordinate with each other.
    """
    MESSAGE_TYPES = [
        ('request', 'Task Request'),
        ('response', 'Task Response'),
        ('feedback', 'Feedback'),
        ('handoff', 'Task Handoff'),
        ('notification', 'Notification'),
        ('question', 'Question'),
        ('answer', 'Answer'),
        ('status', 'Status Update'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Sender and receiver
    sender_agent = models.ForeignKey('Agent', on_delete=models.CASCADE, related_name='sent_messages')
    receiver_agent = models.ForeignKey('Agent', on_delete=models.CASCADE, related_name='received_messages')

    # Message content
    message_type = models.CharField(max_length=50, choices=MESSAGE_TYPES)
    subject = models.CharField(max_length=255)
    content = models.TextField()

    # Attachments (references to content)
    attachments = models.JSONField(default=list)
    # e.g., [{'type': 'image', 'id': 'uuid'}, {'type': 'document', 'url': '...'}]

    # Threading
    parent_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    thread_id = models.UUIDField(default=uuid.uuid4)  # Groups related messages

    # Context
    task_context = models.JSONField(default=dict)
    # e.g., {'workflow_id': 'uuid', 'opportunity_id': 'uuid'}

    # Status
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')

    # Priority
    priority = models.IntegerField(default=5)  # 1-10, higher = more urgent

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Agent Message'
        verbose_name_plural = 'Agent Messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['thread_id']),
            models.Index(fields=['sender_agent', 'created_at']),
            models.Index(fields=['receiver_agent', 'status']),
        ]

    def __str__(self):
        return f"{self.sender_agent.name} -> {self.receiver_agent.name}: {self.subject[:50]}"


class TeamWorkflow(models.Model):
    """
    Session 227: Collaborative workflows involving multiple agents.
    """
    WORKFLOW_STATUSES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Team executing this workflow
    team = models.ForeignKey(AgentTeam, on_delete=models.CASCADE, related_name='workflows')

    # Related opportunity (optional)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.SET_NULL, null=True, blank=True, related_name='team_workflows')

    # Workflow definition
    workflow_template = models.CharField(max_length=100, blank=True)  # e.g., 'research_and_create_logos'
    steps = models.JSONField(default=list)
    # e.g., [
    #   {'step': 1, 'agent_role': 'researcher', 'action': 'research_trends', 'status': 'completed'},
    #   {'step': 2, 'agent_role': 'designer', 'action': 'create_concepts', 'status': 'in_progress'},
    #   {'step': 3, 'agent_role': 'reviewer', 'action': 'review_designs', 'status': 'pending'},
    # ]

    # Current state
    status = models.CharField(max_length=20, choices=WORKFLOW_STATUSES, default='draft')
    current_step = models.IntegerField(default=0)
    current_agent = models.ForeignKey('Agent', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_workflows')

    # Progress tracking
    progress = models.IntegerField(default=0)  # 0-100%
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Results
    results = models.JSONField(default=dict)
    # e.g., {'images_created': 5, 'research_findings': {...}, 'review_score': 8.5}

    # Errors and issues
    errors = models.JSONField(default=list)

    # Metadata
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Team Workflow'
        verbose_name_plural = 'Team Workflows'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.status}) - {self.team.name}"

    def advance_step(self):
        """Move to the next step in the workflow"""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.progress = int((self.current_step / len(self.steps)) * 100)
            self.save()
            return True
        return False


class TeamWorkflowStep(models.Model):
    """
    Session 227: Individual step execution in a team workflow.
    """
    STEP_STATUSES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(TeamWorkflow, on_delete=models.CASCADE, related_name='step_executions')

    # Step definition
    step_number = models.IntegerField()
    step_name = models.CharField(max_length=100)
    action = models.CharField(max_length=100)

    # Assignment
    assigned_agent = models.ForeignKey('Agent', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_steps')
    required_role = models.ForeignKey(AgentRole, on_delete=models.SET_NULL, null=True, blank=True)

    # Execution
    status = models.CharField(max_length=20, choices=STEP_STATUSES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Input/Output
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict)

    # Feedback from reviewers
    review_score = models.FloatField(null=True, blank=True)  # 0-10
    review_feedback = models.TextField(blank=True)
    reviewer_agent = models.ForeignKey('Agent', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_steps')

    # Dependencies
    depends_on = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='required_by')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Team Workflow Step'
        verbose_name_plural = 'Team Workflow Steps'
        ordering = ['workflow', 'step_number']

    def __str__(self):
        return f"Step {self.step_number}: {self.step_name} ({self.status})"