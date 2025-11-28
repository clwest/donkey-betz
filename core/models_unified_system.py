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

    # Spider connections - what data sources feed this agent
    spider_categories = models.ManyToManyField(
        'SpiderCategory',
        through='AgentSpiderConnection',
        related_name='agents',
        blank=True,
        help_text="Spider categories that feed data to this agent"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def success_rate(self):
        if self.total_executions == 0:
            return 0
        return (self.successful_executions / self.total_executions) * 100

    @property
    def knowledge_count(self):
        """Count of knowledge sources this agent has"""
        return self.knowledge_sources.filter(is_active=True).count()

    @property
    def connected_spider_count(self):
        """Count of spider categories feeding this agent"""
        return self.spider_connections.count()

    def get_knowledge_summary(self):
        """Get a summary of this agent's knowledge sources"""
        knowledge = self.knowledge_sources.filter(is_active=True)
        return {
            'total_count': knowledge.count(),
            'by_type': {
                k['knowledge_type']: k['count']
                for k in knowledge.values('knowledge_type').annotate(count=models.Count('id'))
            },
            'avg_confidence': knowledge.aggregate(avg=models.Avg('confidence_score'))['avg'] or 0,
            'data_points': knowledge.aggregate(total=models.Sum('data_points_count'))['total'] or 0,
        }

    def __str__(self):
        return f"{self.name} ({self.agent_type})"

    class Meta:
        app_label = 'core'
        ordering = ['-effectiveness_score', 'name']


class SpiderCategory(models.Model):
    """
    Categories for spider data sources (tech, jobs, crypto, etc.)
    """
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default='🕷️')

    class Meta:
        app_label = 'core'
        verbose_name_plural = "Spider Categories"

    def __str__(self):
        return self.name


class AgentSpiderConnection(models.Model):
    """
    Many-to-many through table connecting Agents to Spider categories.
    This defines which agents process data from which spider categories.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey('Agent', on_delete=models.CASCADE, related_name='spider_connections')
    spider_category = models.ForeignKey(SpiderCategory, on_delete=models.CASCADE, related_name='agent_connections')

    # Routing configuration
    is_primary = models.BooleanField(default=False, help_text="Is this agent the primary handler for this category?")
    priority = models.IntegerField(default=5, help_text="Routing priority (1=highest, 10=lowest)")

    # Processing stats
    total_processed = models.IntegerField(default=0)
    successful_processed = models.IntegerField(default=0)
    avg_processing_time_ms = models.IntegerField(default=0)
    last_processed_at = models.DateTimeField(null=True, blank=True)

    # Quality tracking
    avg_quality_score = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        unique_together = ['agent', 'spider_category']
        ordering = ['priority', '-is_primary']

    def __str__(self):
        return f"{self.agent.name} ← {self.spider_category.name}"

    @property
    def success_rate(self):
        if self.total_processed == 0:
            return 0
        return (self.successful_processed / self.total_processed) * 100


class AgentKnowledgeSource(models.Model):
    """
    Tracks what knowledge each agent has learned from spider data.
    Aggregates spider data into agent-specific knowledge.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey('Agent', on_delete=models.CASCADE, related_name='knowledge_sources')

    # Knowledge categorization
    knowledge_type = models.CharField(max_length=50, choices=[
        ('trend', 'Trend Data'),
        ('market', 'Market Intelligence'),
        ('opportunity', 'Opportunity'),
        ('competitor', 'Competitor Info'),
        ('pricing', 'Pricing Data'),
        ('user_behavior', 'User Behavior'),
        ('content_idea', 'Content Ideas'),
        ('tool_discovery', 'Tool Discovery'),
    ])

    # Source tracking
    spider_category = models.ForeignKey(SpiderCategory, on_delete=models.SET_NULL, null=True, blank=True)
    source_spider_names = ArrayField(
        models.CharField(max_length=100),
        default=list,
        help_text="Names of spiders that contributed to this knowledge"
    )

    # Knowledge content
    title = models.CharField(max_length=500)
    summary = models.TextField(help_text="Summary of the knowledge")
    key_insights = models.JSONField(default=list, help_text="List of key insights")

    # Metrics
    data_points_count = models.IntegerField(default=0, help_text="Number of spider data points used")
    confidence_score = models.FloatField(default=0.0, help_text="Confidence in this knowledge (0.0-1.0)")
    relevance_score = models.FloatField(default=0.0)
    freshness_score = models.FloatField(default=1.0, help_text="How fresh/current this knowledge is (0.0-1.0)")

    # Timestamps
    first_discovered_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_validated = models.BooleanField(default=False)

    class Meta:
        app_label = 'core'
        ordering = ['-confidence_score', '-last_updated_at']
        indexes = [
            models.Index(fields=['agent', 'knowledge_type']),
            models.Index(fields=['spider_category', 'is_active']),
        ]

    def __str__(self):
        return f"{self.agent.name}: {self.title[:50]}"


class AgentLearningConnection(models.Model):
    """
    Defines learning relationships between agents.
    Agents can learn from each other based on complementary skills.

    Session 243: Enabling agent-to-agent knowledge sharing
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # The learning relationship
    teacher_agent = models.ForeignKey('Agent', on_delete=models.CASCADE, related_name='students')
    student_agent = models.ForeignKey('Agent', on_delete=models.CASCADE, related_name='teachers')

    # Learning configuration
    learning_type = models.CharField(max_length=50, choices=[
        ('complementary', 'Complementary Skills'),  # Different skills that work together
        ('specialization', 'Specialization'),  # Teacher is specialist in student's area
        ('pipeline', 'Pipeline'),  # Student uses teacher's output as input
        ('validation', 'Validation'),  # Cross-validation of work
        ('collaborative', 'Collaborative'),  # Working together on tasks
    ])

    # What knowledge types can be shared
    shareable_knowledge_types = ArrayField(
        models.CharField(max_length=50),
        default=list,
        help_text="Types of knowledge that can be transferred"
    )

    # Learning metrics
    total_transfers = models.IntegerField(default=0)
    successful_transfers = models.IntegerField(default=0)
    avg_improvement_score = models.FloatField(default=0.0, help_text="Average improvement from knowledge transfer")
    last_transfer_at = models.DateTimeField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    strength = models.FloatField(default=0.5, help_text="Connection strength 0.0-1.0")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        unique_together = ['teacher_agent', 'student_agent']
        ordering = ['-strength', '-total_transfers']

    def __str__(self):
        return f"{self.teacher_agent.name} → {self.student_agent.name} ({self.learning_type})"

    @property
    def success_rate(self):
        if self.total_transfers == 0:
            return 0
        return (self.successful_transfers / self.total_transfers) * 100


class KnowledgeTransfer(models.Model):
    """
    Records of knowledge being transferred between agents.
    When an agent learns something useful, it can share with connected agents.

    Session 243: Tracking knowledge flow between agents
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # The transfer
    connection = models.ForeignKey(AgentLearningConnection, on_delete=models.CASCADE, related_name='transfers')
    source_knowledge = models.ForeignKey(AgentKnowledgeSource, on_delete=models.CASCADE, related_name='transfers_out')

    # What was transferred
    transfer_summary = models.TextField(help_text="Summary of what was learned")
    key_points = models.JSONField(default=list)

    # Outcome
    was_useful = models.BooleanField(null=True, blank=True)
    usefulness_score = models.FloatField(default=0.0, help_text="How useful was this transfer (0.0-1.0)")
    student_feedback = models.TextField(blank=True)

    # Application
    was_applied = models.BooleanField(default=False)
    application_result = models.JSONField(default=dict, help_text="Result of applying the knowledge")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']

    def __str__(self):
        return f"Transfer: {self.connection} at {self.created_at}"


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


# =============================================================================
# SESSION 229: PHASE 4 - SMART DISTRIBUTION
# =============================================================================

class DistributionPlatform(models.Model):
    """
    Platforms where content can be distributed/sold.
    """
    PLATFORM_TYPES = [
        ('marketplace', 'Marketplace'),        # Etsy, Creative Market, etc.
        ('social', 'Social Media'),            # Instagram, TikTok, etc.
        ('stock', 'Stock Content'),            # Shutterstock, Adobe Stock, etc.
        ('print_on_demand', 'Print on Demand'),  # Redbubble, Printful, etc.
        ('nft', 'NFT Marketplace'),            # OpenSea, Foundation, etc.
        ('direct', 'Direct Sales'),            # Your own website
        ('freelance', 'Freelance Platform'),   # Fiverr, Upwork, etc.
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    platform_type = models.CharField(max_length=50, choices=PLATFORM_TYPES)
    description = models.TextField(blank=True)
    website_url = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)

    # Platform capabilities
    supported_content_types = models.JSONField(default=list)  # ['image', 'video', 'audio', '3d']
    supported_formats = models.JSONField(default=list)  # ['png', 'jpg', 'mp4', 'svg']
    max_file_size_mb = models.IntegerField(default=100)

    # Revenue model
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    has_subscription = models.BooleanField(default=False)
    subscription_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Integration
    api_available = models.BooleanField(default=False)
    api_documentation_url = models.URLField(blank=True)
    requires_approval = models.BooleanField(default=False)

    # Metadata
    popularity_score = models.IntegerField(default=50)  # 0-100
    avg_earnings_per_item = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    competition_level = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ], default='medium')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Distribution Platform'
        verbose_name_plural = 'Distribution Platforms'
        ordering = ['-popularity_score', 'name']

    def __str__(self):
        return f"{self.name} ({self.platform_type})"


class UserPlatformAccount(models.Model):
    """
    User's account on a distribution platform.
    """
    ACCOUNT_STATUS = [
        ('pending', 'Pending Verification'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('inactive', 'Inactive'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='platform_accounts')
    platform = models.ForeignKey(DistributionPlatform, on_delete=models.CASCADE, related_name='user_accounts')

    # Account details
    account_username = models.CharField(max_length=200, blank=True)
    account_url = models.URLField(blank=True)
    account_status = models.CharField(max_length=20, choices=ACCOUNT_STATUS, default='pending')

    # Credentials (encrypted in production)
    api_key = models.CharField(max_length=500, blank=True)
    api_secret = models.CharField(max_length=500, blank=True)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)

    # Performance metrics
    total_items_listed = models.IntegerField(default=0)
    total_sales = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    avg_item_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    follower_count = models.IntegerField(default=0)

    # Settings
    auto_upload_enabled = models.BooleanField(default=False)
    notification_settings = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'User Platform Account'
        verbose_name_plural = 'User Platform Accounts'
        unique_together = ['user', 'platform']

    def __str__(self):
        return f"{self.user.username} on {self.platform.name}"


class ContentDistribution(models.Model):
    """
    Record of content distributed to a platform.
    """
    DISTRIBUTION_STATUS = [
        ('draft', 'Draft'),
        ('pending', 'Pending Upload'),
        ('uploading', 'Uploading'),
        ('processing', 'Processing'),
        ('live', 'Live'),
        ('rejected', 'Rejected'),
        ('removed', 'Removed'),
        ('sold_out', 'Sold Out'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='distributions')
    platform_account = models.ForeignKey(UserPlatformAccount, on_delete=models.CASCADE, related_name='distributions')

    # Content reference
    content_type = models.CharField(max_length=50)  # image, video, audio, 3d
    image_history = models.ForeignKey('content.ImageHistory', on_delete=models.SET_NULL, null=True, blank=True, related_name='distributions')
    video_history = models.ForeignKey('content.VideoHistory', on_delete=models.SET_NULL, null=True, blank=True, related_name='distributions')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.SET_NULL, null=True, blank=True, related_name='distributions')

    # Listing details
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list)
    categories = models.JSONField(default=list)

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default='USD')
    license_type = models.CharField(max_length=50, blank=True)  # commercial, editorial, etc.

    # Platform-specific data
    platform_listing_id = models.CharField(max_length=200, blank=True)
    platform_listing_url = models.URLField(blank=True)
    platform_metadata = models.JSONField(default=dict)

    # Status
    status = models.CharField(max_length=20, choices=DISTRIBUTION_STATUS, default='draft')
    rejection_reason = models.TextField(blank=True)

    # Performance
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    downloads = models.IntegerField(default=0)
    sales = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Timestamps
    listed_at = models.DateTimeField(null=True, blank=True)
    last_sale_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Content Distribution'
        verbose_name_plural = 'Content Distributions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} on {self.platform_account.platform.name}"


class DistributionRecommendation(models.Model):
    """
    AI-generated recommendations for where to distribute content.
    """
    RECOMMENDATION_TYPES = [
        ('platform', 'Platform Recommendation'),
        ('pricing', 'Pricing Recommendation'),
        ('timing', 'Timing Recommendation'),
        ('tags', 'Tags/Keywords Recommendation'),
        ('optimization', 'Optimization Recommendation'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='distribution_recommendations')

    # Content reference
    content_type = models.CharField(max_length=50)
    image_history = models.ForeignKey('content.ImageHistory', on_delete=models.SET_NULL, null=True, blank=True, related_name='recommendations')
    video_history = models.ForeignKey('content.VideoHistory', on_delete=models.SET_NULL, null=True, blank=True, related_name='recommendations')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.SET_NULL, null=True, blank=True, related_name='distribution_recommendations')

    # Recommendation details
    recommendation_type = models.CharField(max_length=50, choices=RECOMMENDATION_TYPES)
    platform = models.ForeignKey(DistributionPlatform, on_delete=models.SET_NULL, null=True, blank=True)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # 0-100

    # Recommendation content
    title = models.CharField(max_length=200)
    reasoning = models.TextField()
    suggested_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    suggested_tags = models.JSONField(default=list)
    suggested_title = models.CharField(max_length=500, blank=True)
    suggested_description = models.TextField(blank=True)

    # Estimated outcomes
    estimated_views = models.IntegerField(null=True, blank=True)
    estimated_sales = models.IntegerField(null=True, blank=True)
    estimated_revenue = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # User action
    is_applied = models.BooleanField(default=False)
    applied_at = models.DateTimeField(null=True, blank=True)
    is_dismissed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Distribution Recommendation'
        verbose_name_plural = 'Distribution Recommendations'
        ordering = ['-confidence_score', '-created_at']

    def __str__(self):
        return f"{self.recommendation_type}: {self.title}"


class DistributionAnalytics(models.Model):
    """
    Aggregated analytics for distribution performance.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='distribution_analytics')
    platform = models.ForeignKey(DistributionPlatform, on_delete=models.CASCADE, null=True, blank=True)

    # Time period
    date = models.DateField()
    period_type = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], default='daily')

    # Metrics
    total_views = models.IntegerField(default=0)
    total_downloads = models.IntegerField(default=0)
    total_sales = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    new_listings = models.IntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # sales/views

    # Top performers
    top_content_ids = models.JSONField(default=list)  # List of content IDs
    top_tags = models.JSONField(default=list)
    best_performing_category = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Distribution Analytics'
        verbose_name_plural = 'Distribution Analytics'
        unique_together = ['user', 'platform', 'date', 'period_type']
        ordering = ['-date']

    def __str__(self):
        platform_name = self.platform.name if self.platform else 'All Platforms'
        return f"{self.user.username} - {platform_name} - {self.date}"


# ============================================================
# Session 232: Phase 5 - Learning Loop Models
# ============================================================

class SuccessPattern(models.Model):
    """
    Tracks patterns that lead to successful sales/revenue.
    The system learns what works and suggests similar approaches.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='success_patterns')

    # Pattern identification
    pattern_type = models.CharField(max_length=50, choices=[
        ('content_style', 'Content Style'),
        ('pricing_strategy', 'Pricing Strategy'),
        ('timing', 'Upload Timing'),
        ('platform_match', 'Platform Match'),
        ('tag_combination', 'Tag Combination'),
        ('description_format', 'Description Format'),
        ('category_niche', 'Category Niche'),
    ])
    pattern_name = models.CharField(max_length=200)
    pattern_description = models.TextField(blank=True)

    # Pattern data
    pattern_attributes = models.JSONField(default=dict)  # Specific attributes that make this pattern
    # Example: {"style": "cyberpunk", "colors": ["neon", "dark"], "aspect_ratio": "16:9"}

    # Success metrics
    success_count = models.IntegerField(default=0)  # Number of times this pattern succeeded
    failure_count = models.IntegerField(default=0)  # Number of times it failed
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # 0-100%
    avg_revenue_per_success = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_revenue_attributed = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Pattern strength
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, default=50)  # 0-100
    sample_size = models.IntegerField(default=0)  # How many data points
    statistical_significance = models.BooleanField(default=False)  # p < 0.05

    # Best platforms for this pattern
    best_platforms = models.JSONField(default=list)  # ["etsy", "gumroad"]

    # Time-based insights
    best_upload_times = models.JSONField(default=list)  # ["tuesday_10am", "friday_2pm"]
    best_seasons = models.JSONField(default=list)  # ["christmas", "summer"]

    # Related content
    example_content_ids = models.JSONField(default=list)  # UUIDs of successful content

    # Status
    is_active = models.BooleanField(default=True)
    is_global = models.BooleanField(default=False)  # If True, applies to all users

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_validated = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Success Pattern'
        verbose_name_plural = 'Success Patterns'
        ordering = ['-success_rate', '-confidence_score']

    def __str__(self):
        return f"{self.pattern_type}: {self.pattern_name} ({self.success_rate}%)"

    def update_metrics(self, was_successful: bool, revenue: float = 0):
        """Update pattern metrics after a new data point."""
        if was_successful:
            self.success_count += 1
            self.total_revenue_attributed += Decimal(str(revenue))
        else:
            self.failure_count += 1

        self.sample_size = self.success_count + self.failure_count
        if self.sample_size > 0:
            self.success_rate = (self.success_count / self.sample_size) * 100
            if self.success_count > 0:
                self.avg_revenue_per_success = self.total_revenue_attributed / self.success_count

        # Update confidence based on sample size
        if self.sample_size >= 30:
            self.statistical_significance = True
            self.confidence_score = min(95, 50 + (self.sample_size * 0.5))
        else:
            self.confidence_score = min(50, self.sample_size * 2)

        self.save()


class ContentPerformancePrediction(models.Model):
    """
    ML-based predictions for content performance before distribution.
    Helps users understand potential success before uploading.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='performance_predictions')

    # Content being predicted
    content_type = models.CharField(max_length=50)  # image, video, audio
    content_id = models.UUIDField(null=True, blank=True)  # Reference to actual content
    content_hash = models.CharField(max_length=64, blank=True)  # For dedup

    # Content attributes analyzed
    analyzed_attributes = models.JSONField(default=dict)
    # {"style": "cyberpunk", "colors": [...], "complexity": 7, "uniqueness": 8}

    # Predictions per platform
    platform_predictions = models.JSONField(default=dict)
    # {
    #   "etsy": {"success_probability": 0.75, "expected_revenue": 45.00, "confidence": 0.8},
    #   "gumroad": {"success_probability": 0.60, "expected_revenue": 15.00, "confidence": 0.7}
    # }

    # Overall predictions
    overall_success_probability = models.DecimalField(max_digits=5, decimal_places=4, default=0)  # 0-1
    expected_total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expected_time_to_first_sale = models.IntegerField(default=0)  # Hours
    prediction_confidence = models.DecimalField(max_digits=5, decimal_places=4, default=0)  # 0-1

    # Recommended actions
    recommended_platforms = models.JSONField(default=list)  # Ordered by potential
    recommended_price_range = models.JSONField(default=dict)  # {"min": 10, "max": 50, "optimal": 29.99}
    recommended_tags = models.JSONField(default=list)
    recommended_upload_time = models.DateTimeField(null=True, blank=True)

    # Matching patterns
    matching_success_patterns = models.JSONField(default=list)  # Pattern IDs that match

    # Actual outcomes (filled after distribution)
    actual_success = models.BooleanField(null=True, blank=True)
    actual_revenue = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prediction_accuracy = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)

    # Model info
    model_version = models.CharField(max_length=50, default='v1.0')
    prediction_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Content Performance Prediction'
        verbose_name_plural = 'Content Performance Predictions'
        ordering = ['-prediction_timestamp']

    def __str__(self):
        return f"Prediction for {self.content_type}: {self.overall_success_probability*100:.1f}% success"


class PricingOptimization(models.Model):
    """
    Dynamic pricing suggestions based on market data and user history.
    Learns optimal pricing strategies over time.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pricing_optimizations')

    # Scope
    platform = models.ForeignKey(DistributionPlatform, on_delete=models.CASCADE, null=True, blank=True)
    content_category = models.CharField(max_length=100, blank=True)  # "ai_art", "digital_download"
    content_style = models.CharField(max_length=100, blank=True)  # "cyberpunk", "minimalist"

    # Current market data
    market_avg_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    market_median_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    market_price_range = models.JSONField(default=dict)  # {"min": 5, "max": 500, "p25": 15, "p75": 75}
    competitor_prices = models.JSONField(default=list)  # Sample of competitor prices

    # User's historical performance
    user_avg_sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    user_best_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Price with best conversion
    user_price_elasticity = models.DecimalField(max_digits=5, decimal_places=4, default=0)  # How price affects sales

    # Optimal pricing
    optimal_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    optimal_price_confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    price_range_suggestion = models.JSONField(default=dict)  # {"low": 15, "mid": 25, "high": 45}

    # Price testing results
    tested_prices = models.JSONField(default=list)  # [{"price": 25, "conversions": 10, "revenue": 250}]
    best_tested_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Seasonal adjustments
    seasonal_multipliers = models.JSONField(default=dict)
    # {"christmas": 1.25, "summer": 0.9, "black_friday": 1.5}

    # Insights
    pricing_insights = models.JSONField(default=list)
    # ["Your prices are 15% below market average", "Consider raising prices on weekends"]

    # A/B test reference
    current_ab_test_id = models.UUIDField(null=True, blank=True)

    last_updated = models.DateTimeField(auto_now=True)
    data_freshness_days = models.IntegerField(default=0)  # Days since last market data update

    class Meta:
        app_label = 'core'
        verbose_name = 'Pricing Optimization'
        verbose_name_plural = 'Pricing Optimizations'
        ordering = ['-last_updated']

    def __str__(self):
        platform_name = self.platform.name if self.platform else 'All'
        return f"Pricing for {platform_name}/{self.content_category}: ${self.optimal_price}"


class DistributionInsight(models.Model):
    """
    AI-generated insights from distribution learning patterns.
    Proactive suggestions based on analyzed data.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='distribution_insights')

    # Insight classification
    insight_type = models.CharField(max_length=50, choices=[
        ('opportunity', 'New Opportunity'),
        ('improvement', 'Improvement Suggestion'),
        ('warning', 'Warning/Alert'),
        ('milestone', 'Achievement/Milestone'),
        ('trend', 'Trend Detected'),
        ('prediction', 'Future Prediction'),
        ('comparison', 'Performance Comparison'),
    ])
    priority = models.CharField(max_length=20, choices=[
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ], default='medium')

    # Content
    title = models.CharField(max_length=200)
    message = models.TextField()
    detailed_analysis = models.TextField(blank=True)

    # Data backing the insight
    supporting_data = models.JSONField(default=dict)
    # {"pattern_id": "...", "metrics": {...}, "comparison": {...}}

    # Actionable recommendations
    recommended_actions = models.JSONField(default=list)
    # [{"action": "Raise price on Etsy", "expected_impact": "+15% revenue"}]

    # Impact estimation
    potential_revenue_impact = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    confidence_level = models.DecimalField(max_digits=5, decimal_places=2, default=50)

    # User interaction
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    is_acted_upon = models.BooleanField(default=False)
    user_feedback = models.CharField(max_length=20, choices=[
        ('helpful', 'Helpful'),
        ('not_helpful', 'Not Helpful'),
        ('incorrect', 'Incorrect'),
    ], null=True, blank=True)

    # Validity
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(null=True, blank=True)  # When insight becomes stale
    is_still_relevant = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Distribution Insight'
        verbose_name_plural = 'Distribution Insights'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.insight_type}] {self.title}"


class UserLearningProfile(models.Model):
    """
    Aggregated learning profile for each user.
    Stores preferences, patterns, and AI assistant state.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learning_profile')

    # Content preferences learned
    preferred_styles = models.JSONField(default=list)  # ["cyberpunk", "minimalist"]
    preferred_platforms = models.JSONField(default=list)  # ["etsy", "gumroad"]
    preferred_content_types = models.JSONField(default=list)  # ["image", "digital_download"]
    preferred_price_ranges = models.JSONField(default=dict)  # {"low": 10, "high": 50}

    # Work patterns
    typical_upload_times = models.JSONField(default=list)  # ["weekday_morning", "weekend_afternoon"]
    productivity_patterns = models.JSONField(default=dict)  # {"best_day": "tuesday", "best_hour": 10}
    avg_content_per_week = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Success profile
    overall_success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    strongest_categories = models.JSONField(default=list)  # Categories with best performance
    weakest_categories = models.JSONField(default=list)  # Categories needing improvement
    total_successful_distributions = models.IntegerField(default=0)
    total_lifetime_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Learning state
    patterns_discovered = models.IntegerField(default=0)
    insights_generated = models.IntegerField(default=0)
    insights_acted_upon = models.IntegerField(default=0)
    prediction_accuracy_avg = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Personalization settings
    notification_preferences = models.JSONField(default=dict)
    # {"daily_insights": True, "price_alerts": True, "trend_updates": False}

    # Goals
    revenue_goals = models.JSONField(default=dict)
    # {"monthly": 1000, "yearly": 12000, "next_milestone": 5000}

    # AI assistant memory
    conversation_context = models.JSONField(default=dict)
    recent_interactions = models.JSONField(default=list)  # Last N interactions for context

    last_activity = models.DateTimeField(auto_now=True)
    profile_completeness = models.IntegerField(default=0)  # 0-100%

    class Meta:
        app_label = 'core'
        verbose_name = 'User Learning Profile'
        verbose_name_plural = 'User Learning Profiles'

    def __str__(self):
        return f"Learning Profile: {self.user.username}"


class PerformanceComparison(models.Model):
    """
    Benchmarks user performance against market/peers.
    Helps understand where they stand and how to improve.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='performance_comparisons')

    # Comparison scope
    comparison_type = models.CharField(max_length=50, choices=[
        ('platform', 'Platform-wide'),
        ('category', 'Category'),
        ('style', 'Style'),
        ('price_tier', 'Price Tier'),
        ('experience_level', 'Experience Level'),
    ])
    scope_value = models.CharField(max_length=100)  # e.g., "etsy", "ai_art", "cyberpunk"

    # User metrics
    user_metrics = models.JSONField(default=dict)
    # {"revenue": 500, "conversion_rate": 3.5, "avg_price": 25, "items_sold": 20}

    # Benchmark metrics
    benchmark_metrics = models.JSONField(default=dict)
    # {"revenue": {"p25": 200, "p50": 450, "p75": 900, "p90": 2000}}

    # Percentile rankings
    percentile_rankings = models.JSONField(default=dict)
    # {"revenue": 55, "conversion_rate": 70, "items_sold": 45}

    # Insights
    strengths = models.JSONField(default=list)  # ["Above average pricing", "Good conversion"]
    weaknesses = models.JSONField(default=list)  # ["Below average volume"]
    improvement_opportunities = models.JSONField(default=list)

    # Trend
    trend_vs_last_period = models.JSONField(default=dict)
    # {"revenue": "+15%", "ranking_change": "+5 percentile"}

    period_start = models.DateField()
    period_end = models.DateField()
    sample_size = models.IntegerField(default=0)  # Number of users in comparison

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Performance Comparison'
        verbose_name_plural = 'Performance Comparisons'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} vs {self.comparison_type}:{self.scope_value}"


# ============================================================
# Session 234: Phase 6 - Proactive System Models
# ============================================================

class ProactiveAlert(models.Model):
    """
    Proactive alerts that trigger based on conditions/thresholds.
    Monitors metrics and notifies users when action is needed.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='proactive_alerts')

    # Alert definition
    alert_type = models.CharField(max_length=50, choices=[
        ('threshold', 'Threshold Alert'),
        ('trend', 'Trend Alert'),
        ('anomaly', 'Anomaly Detection'),
        ('opportunity', 'Opportunity Alert'),
        ('deadline', 'Deadline Reminder'),
        ('goal', 'Goal Progress'),
        ('competitor', 'Competitor Activity'),
        ('market', 'Market Change'),
    ])
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Trigger conditions
    metric_name = models.CharField(max_length=100)  # e.g., "daily_revenue", "conversion_rate"
    condition = models.CharField(max_length=20, choices=[
        ('above', 'Above'),
        ('below', 'Below'),
        ('equals', 'Equals'),
        ('change_up', 'Increases By'),
        ('change_down', 'Decreases By'),
        ('anomaly', 'Anomaly Detected'),
    ])
    threshold_value = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    threshold_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Scope
    platform = models.ForeignKey(DistributionPlatform, on_delete=models.CASCADE, null=True, blank=True)
    content_type = models.CharField(max_length=50, blank=True)  # image, video, etc.
    category = models.CharField(max_length=100, blank=True)

    # Timing
    check_frequency = models.CharField(max_length=20, choices=[
        ('realtime', 'Real-time'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ], default='daily')
    cooldown_hours = models.IntegerField(default=24)  # Hours before re-triggering

    # Status
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    trigger_count = models.IntegerField(default=0)

    # Actions when triggered
    notification_channels = models.JSONField(default=list)  # ["email", "push", "sms", "in_app"]
    auto_actions = models.JSONField(default=list)  # Actions to take automatically

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Proactive Alert'
        verbose_name_plural = 'Proactive Alerts'
        ordering = ['-is_active', '-trigger_count']

    def __str__(self):
        return f"[{self.alert_type}] {self.name}"

    def should_trigger(self, current_value: float) -> bool:
        """Check if alert should trigger based on current value."""
        if not self.is_active:
            return False

        # Check cooldown
        if self.last_triggered:
            hours_since = (timezone.now() - self.last_triggered).total_seconds() / 3600
            if hours_since < self.cooldown_hours:
                return False

        if self.threshold_value is None:
            return False

        threshold = float(self.threshold_value)
        if self.condition == 'above':
            return current_value > threshold
        elif self.condition == 'below':
            return current_value < threshold
        elif self.condition == 'equals':
            return abs(current_value - threshold) < 0.001
        return False

    def trigger(self):
        """Mark alert as triggered."""
        self.last_triggered = timezone.now()
        self.trigger_count += 1
        self.save()


class ProactiveNotification(models.Model):
    """
    Notifications sent to users from the proactive system.
    Tracks delivery and user engagement.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='proactive_notifications')

    # Source
    alert = models.ForeignKey(ProactiveAlert, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    suggestion = models.ForeignKey('SmartSuggestion', on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')

    # Notification type
    notification_type = models.CharField(max_length=50, choices=[
        ('alert', 'Alert'),
        ('suggestion', 'Suggestion'),
        ('insight', 'Insight'),
        ('reminder', 'Reminder'),
        ('celebration', 'Celebration'),
        ('warning', 'Warning'),
        ('update', 'System Update'),
    ])
    priority = models.CharField(max_length=20, choices=[
        ('urgent', 'Urgent'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ], default='medium')

    # Content
    title = models.CharField(max_length=200)
    message = models.TextField()
    rich_content = models.JSONField(default=dict)  # Charts, links, data
    icon = models.CharField(max_length=50, default='bell')

    # Call to action
    action_url = models.CharField(max_length=500, blank=True)
    action_label = models.CharField(max_length=100, blank=True)
    quick_actions = models.JSONField(default=list)  # [{"label": "Apply", "action": "apply_suggestion"}]

    # Delivery
    channels_sent = models.JSONField(default=list)  # ["email", "push", "in_app"]
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivery_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ], default='pending')

    # User interaction
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_dismissed = models.BooleanField(default=False)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    is_acted_upon = models.BooleanField(default=False)
    acted_at = models.DateTimeField(null=True, blank=True)
    action_result = models.JSONField(default=dict)

    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)
    is_expired = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Proactive Notification'
        verbose_name_plural = 'Proactive Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'is_dismissed']),
            models.Index(fields=['delivery_status', 'scheduled_at']),
        ]

    def __str__(self):
        return f"[{self.notification_type}] {self.title}"

    def mark_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    def mark_acted(self, result: dict = None):
        """Mark notification as acted upon."""
        self.is_acted_upon = True
        self.acted_at = timezone.now()
        if result:
            self.action_result = result
        self.save()


class SmartSuggestion(models.Model):
    """
    AI-generated suggestions for improving performance.
    Proactively recommends actions based on learned patterns.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='smart_suggestions')

    # Suggestion type
    suggestion_type = models.CharField(max_length=50, choices=[
        ('pricing', 'Pricing Adjustment'),
        ('timing', 'Upload Timing'),
        ('platform', 'Platform Recommendation'),
        ('content', 'Content Improvement'),
        ('tags', 'Tag Optimization'),
        ('description', 'Description Enhancement'),
        ('bundle', 'Bundle Suggestion'),
        ('promotion', 'Promotion Opportunity'),
        ('cross_sell', 'Cross-Sell Opportunity'),
        ('expansion', 'Market Expansion'),
    ])
    category = models.CharField(max_length=50, choices=[
        ('revenue', 'Increase Revenue'),
        ('efficiency', 'Improve Efficiency'),
        ('reach', 'Expand Reach'),
        ('quality', 'Improve Quality'),
        ('risk', 'Reduce Risk'),
    ], default='revenue')

    # Content
    title = models.CharField(max_length=200)
    description = models.TextField()
    detailed_rationale = models.TextField(blank=True)

    # Supporting data
    supporting_patterns = models.JSONField(default=list)  # Pattern IDs that support this
    supporting_data = models.JSONField(default=dict)  # Analytics data
    similar_successes = models.JSONField(default=list)  # Examples that worked

    # Actionable details
    action_steps = models.JSONField(default=list)
    # [{"step": 1, "action": "Update price to $25", "reason": "Based on conversion data"}]

    # Current vs suggested
    current_state = models.JSONField(default=dict)  # {"price": 15, "platform": "etsy"}
    suggested_state = models.JSONField(default=dict)  # {"price": 25}

    # Impact estimation
    estimated_impact = models.JSONField(default=dict)
    # {"revenue_change": "+25%", "conversion_change": "+10%", "time_saved": "2h"}
    estimated_revenue_impact = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, default=50)  # 0-100

    # Priority
    priority_score = models.IntegerField(default=50)  # 0-100, for sorting
    effort_level = models.CharField(max_length=20, choices=[
        ('low', 'Low (Quick Win)'),
        ('medium', 'Medium'),
        ('high', 'High (Requires Work)'),
    ], default='medium')

    # User interaction
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('implemented', 'Implemented'),
        ('expired', 'Expired'),
    ], default='pending')
    user_feedback = models.TextField(blank=True)
    rejection_reason = models.CharField(max_length=100, blank=True)

    # Outcome tracking (if implemented)
    implemented_at = models.DateTimeField(null=True, blank=True)
    outcome_tracked = models.BooleanField(default=False)
    actual_impact = models.JSONField(default=dict)  # Actual measured impact

    # Validity
    valid_until = models.DateTimeField(null=True, blank=True)
    is_still_relevant = models.BooleanField(default=True)

    # Related content
    related_content_ids = models.JSONField(default=list)  # Content this applies to
    related_distribution_ids = models.JSONField(default=list)  # Distributions this applies to

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Smart Suggestion'
        verbose_name_plural = 'Smart Suggestions'
        ordering = ['-priority_score', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status', 'suggestion_type']),
            models.Index(fields=['priority_score', 'confidence_score']),
        ]

    def __str__(self):
        return f"[{self.suggestion_type}] {self.title}"

    def accept(self):
        """Accept the suggestion."""
        self.status = 'accepted'
        self.save()

    def reject(self, reason: str = ''):
        """Reject the suggestion."""
        self.status = 'rejected'
        self.rejection_reason = reason
        self.save()

    def mark_implemented(self):
        """Mark as implemented."""
        self.status = 'implemented'
        self.implemented_at = timezone.now()
        self.save()


class AutomatedAction(models.Model):
    """
    Automated actions that run based on triggers.
    Can be triggered by alerts, schedules, or patterns.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='automated_actions')

    # Action definition
    action_type = models.CharField(max_length=50, choices=[
        ('price_adjust', 'Adjust Pricing'),
        ('distribute', 'Auto-Distribute'),
        ('notify', 'Send Notification'),
        ('tag_update', 'Update Tags'),
        ('schedule_upload', 'Schedule Upload'),
        ('apply_promotion', 'Apply Promotion'),
        ('generate_report', 'Generate Report'),
        ('backup_data', 'Backup Data'),
        ('optimize_listing', 'Optimize Listing'),
    ])
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Trigger configuration
    trigger_type = models.CharField(max_length=50, choices=[
        ('alert', 'On Alert'),
        ('schedule', 'On Schedule'),
        ('event', 'On Event'),
        ('threshold', 'On Threshold'),
        ('manual', 'Manual'),
    ])
    trigger_alert = models.ForeignKey(ProactiveAlert, on_delete=models.SET_NULL, null=True, blank=True, related_name='automated_actions')
    trigger_schedule = models.CharField(max_length=100, blank=True)  # Cron expression
    trigger_event = models.CharField(max_length=100, blank=True)  # Event name

    # Action parameters
    action_params = models.JSONField(default=dict)
    # For price_adjust: {"change_type": "percent", "change_value": 10, "min_price": 5, "max_price": 100}
    # For distribute: {"platforms": ["etsy", "gumroad"], "auto_price": true}

    # Scope/conditions
    conditions = models.JSONField(default=list)
    # [{"field": "content_type", "operator": "equals", "value": "image"}]
    platform_scope = models.JSONField(default=list)  # Platforms this applies to
    content_type_scope = models.JSONField(default=list)  # Content types this applies to

    # Safety limits
    max_executions_per_day = models.IntegerField(default=10)
    max_price_change_percent = models.DecimalField(max_digits=5, decimal_places=2, default=25)
    requires_confirmation = models.BooleanField(default=False)
    dry_run_first = models.BooleanField(default=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_paused = models.BooleanField(default=False)
    pause_reason = models.CharField(max_length=200, blank=True)

    # Execution tracking
    total_executions = models.IntegerField(default=0)
    successful_executions = models.IntegerField(default=0)
    failed_executions = models.IntegerField(default=0)
    last_executed = models.DateTimeField(null=True, blank=True)
    last_result = models.JSONField(default=dict)
    executions_today = models.IntegerField(default=0)
    executions_today_reset = models.DateField(null=True, blank=True)

    # Impact tracking
    total_revenue_impact = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    avg_impact_per_execution = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Automated Action'
        verbose_name_plural = 'Automated Actions'
        ordering = ['-is_active', '-total_executions']

    def __str__(self):
        return f"[{self.action_type}] {self.name}"

    def can_execute(self) -> tuple:
        """Check if action can execute. Returns (can_execute, reason)."""
        if not self.is_active:
            return False, "Action is not active"
        if self.is_paused:
            return False, f"Action is paused: {self.pause_reason}"

        # Check daily limit
        today = timezone.now().date()
        if self.executions_today_reset != today:
            self.executions_today = 0
            self.executions_today_reset = today
            self.save()

        if self.executions_today >= self.max_executions_per_day:
            return False, "Daily execution limit reached"

        return True, "OK"

    def execute(self, context: dict = None) -> dict:
        """Execute the automated action."""
        can_run, reason = self.can_execute()
        if not can_run:
            return {"success": False, "error": reason}

        # Increment counters
        self.total_executions += 1
        self.executions_today += 1
        self.last_executed = timezone.now()

        # Action execution would be handled by the Proactive Engine
        # This is just the model - actual execution logic is in proactive_engine.py

        result = {
            "success": True,
            "action_type": self.action_type,
            "params": self.action_params,
            "context": context or {},
            "executed_at": str(timezone.now()),
        }

        self.last_result = result
        self.successful_executions += 1
        self.save()

        return result


class AutomatedActionLog(models.Model):
    """
    Log of all automated action executions.
    For auditing and debugging.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action = models.ForeignKey(AutomatedAction, on_delete=models.CASCADE, related_name='execution_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='action_logs')

    # Execution details
    trigger_type = models.CharField(max_length=50)
    trigger_source = models.CharField(max_length=200, blank=True)  # Alert ID, event name, etc.

    # Input/Output
    input_params = models.JSONField(default=dict)
    output_result = models.JSONField(default=dict)

    # Status
    status = models.CharField(max_length=20, choices=[
        ('started', 'Started'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('rolled_back', 'Rolled Back'),
    ])
    error_message = models.TextField(blank=True)

    # Impact
    items_affected = models.IntegerField(default=0)
    revenue_impact = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)

    # Rollback info
    can_rollback = models.BooleanField(default=False)
    rollback_data = models.JSONField(default=dict)
    was_rolled_back = models.BooleanField(default=False)

    class Meta:
        app_label = 'core'
        verbose_name = 'Automated Action Log'
        verbose_name_plural = 'Automated Action Logs'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['action', 'status', 'started_at']),
            models.Index(fields=['user', 'started_at']),
        ]

    def __str__(self):
        return f"Log: {self.action.name} - {self.status}"


class UserNotificationPreference(models.Model):
    """
    User preferences for notifications and alerts.
    Controls what notifications users receive and how.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preferences')

    # Channel preferences
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    in_app_enabled = models.BooleanField(default=True)

    # Notification type preferences
    alert_notifications = models.BooleanField(default=True)
    suggestion_notifications = models.BooleanField(default=True)
    insight_notifications = models.BooleanField(default=True)
    celebration_notifications = models.BooleanField(default=True)
    warning_notifications = models.BooleanField(default=True)

    # Frequency preferences
    digest_frequency = models.CharField(max_length=20, choices=[
        ('realtime', 'Real-time'),
        ('hourly', 'Hourly Digest'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Digest'),
    ], default='daily')

    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)  # e.g., 22:00
    quiet_hours_end = models.TimeField(null=True, blank=True)  # e.g., 08:00
    timezone = models.CharField(max_length=50, default='UTC')

    # Priority thresholds
    min_priority_email = models.CharField(max_length=20, default='medium')  # Only email for medium+ priority
    min_priority_push = models.CharField(max_length=20, default='high')  # Only push for high+ priority

    # Category preferences
    enabled_categories = models.JSONField(default=list)
    # ["revenue", "efficiency", "reach"] - empty means all

    # Unsubscribe tracking
    unsubscribed_types = models.JSONField(default=list)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'User Notification Preference'
        verbose_name_plural = 'User Notification Preferences'

    def __str__(self):
        return f"Notification Preferences: {self.user.username}"

    def should_send(self, notification_type: str, priority: str, channel: str) -> bool:
        """Check if notification should be sent based on preferences."""
        # Check channel
        channel_map = {
            'email': self.email_enabled,
            'push': self.push_enabled,
            'sms': self.sms_enabled,
            'in_app': self.in_app_enabled,
        }
        if not channel_map.get(channel, False):
            return False

        # Check notification type
        type_map = {
            'alert': self.alert_notifications,
            'suggestion': self.suggestion_notifications,
            'insight': self.insight_notifications,
            'celebration': self.celebration_notifications,
            'warning': self.warning_notifications,
        }
        if not type_map.get(notification_type, True):
            return False

        # Check priority thresholds for specific channels
        priority_order = ['low', 'medium', 'high', 'urgent']
        if channel == 'email':
            min_idx = priority_order.index(self.min_priority_email)
            curr_idx = priority_order.index(priority) if priority in priority_order else 0
            if curr_idx < min_idx:
                return False
        elif channel == 'push':
            min_idx = priority_order.index(self.min_priority_push)
            curr_idx = priority_order.index(priority) if priority in priority_order else 0
            if curr_idx < min_idx:
                return False

        return True


# ==============================================================================
# Session 235: A/B Testing Framework Models (Phase 6 - Proactive System)
# ==============================================================================

class ABTest(models.Model):
    """
    A/B Test configuration for testing different strategies.
    Tests pricing, titles, tags, timing, and other content variations.
    """
    TEST_TYPES = [
        ('pricing', 'Pricing Test'),
        ('title', 'Title Test'),
        ('tags', 'Tags Test'),
        ('description', 'Description Test'),
        ('timing', 'Timing Test'),
        ('platform', 'Platform Test'),
        ('bundle', 'Bundle Test'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ab_tests',
        null=True,
        blank=True
    )

    # Test Configuration
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    test_type = models.CharField(max_length=50, choices=TEST_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Hypothesis
    hypothesis = models.TextField(blank=True, help_text="What you expect to happen")

    # Test Parameters
    primary_metric = models.CharField(
        max_length=50,
        default='conversion_rate',
        help_text="Main metric to measure success"
    )
    secondary_metrics = models.JSONField(
        default=list,
        blank=True,
        help_text="Additional metrics to track"
    )
    confidence_level = models.FloatField(
        default=0.95,
        help_text="Statistical confidence level (0.90-0.99)"
    )
    minimum_sample_size = models.IntegerField(
        default=100,
        help_text="Minimum samples per variant before concluding"
    )

    # Targeting
    content_filter = models.JSONField(
        default=dict,
        blank=True,
        help_text="Filter which content participates"
    )
    platform_filter = models.JSONField(
        default=list,
        blank=True,
        help_text="Limit to specific platforms"
    )

    # Timeline
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    max_duration_days = models.IntegerField(default=30)

    # Results
    winner_variant = models.ForeignKey(
        'ABTestVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='won_tests'
    )
    conclusion = models.TextField(blank=True)
    statistical_significance = models.FloatField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['test_type', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.test_type})"

    def start_test(self):
        """Start the A/B test."""
        if self.status != 'draft':
            return False
        self.status = 'running'
        self.start_date = timezone.now()
        self.save()
        return True

    def pause_test(self):
        """Pause the A/B test."""
        if self.status != 'running':
            return False
        self.status = 'paused'
        self.save()
        return True

    def complete_test(self, winner_id=None, conclusion=''):
        """Complete the A/B test with results."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.conclusion = conclusion
        if winner_id:
            self.winner_variant_id = winner_id
        self.save()
        return True

    def get_results(self):
        """Get test results with statistics."""
        variants = self.variants.all()
        results = {
            'test_id': str(self.id),
            'name': self.name,
            'status': self.status,
            'variants': [],
            'winner': None,
            'is_significant': False,
        }

        for variant in variants:
            stats = variant.get_statistics()
            results['variants'].append({
                'id': str(variant.id),
                'name': variant.name,
                'is_control': variant.is_control,
                **stats
            })

        # Simple winner determination (could be enhanced with statistical tests)
        if results['variants']:
            best_variant = max(
                results['variants'],
                key=lambda v: v.get('conversion_rate', 0)
            )
            if best_variant.get('sample_size', 0) >= self.minimum_sample_size:
                results['winner'] = best_variant['id']
                results['is_significant'] = True

        return results


class ABTestVariant(models.Model):
    """
    Individual variant within an A/B test.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test = models.ForeignKey(
        ABTest,
        on_delete=models.CASCADE,
        related_name='variants'
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_control = models.BooleanField(default=False)

    # Variant Configuration
    config = models.JSONField(
        default=dict,
        help_text="Variant-specific settings (price, title, etc.)"
    )

    # Traffic Allocation
    traffic_percentage = models.IntegerField(
        default=50,
        help_text="Percentage of traffic to this variant"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_control', 'name']

    def __str__(self):
        control_str = " (Control)" if self.is_control else ""
        return f"{self.name}{control_str}"

    def get_statistics(self):
        """Get variant statistics."""
        events = self.events.all()
        impressions = events.filter(event_type='impression').count()
        conversions = events.filter(event_type='conversion').count()
        revenue = events.filter(
            event_type='conversion'
        ).aggregate(total=models.Sum('revenue'))['total'] or 0

        return {
            'sample_size': impressions,
            'impressions': impressions,
            'conversions': conversions,
            'conversion_rate': (conversions / impressions * 100) if impressions > 0 else 0,
            'revenue': float(revenue),
            'revenue_per_impression': (float(revenue) / impressions) if impressions > 0 else 0,
        }


class ABTestEvent(models.Model):
    """
    Individual event in an A/B test (impression, click, conversion).
    """
    EVENT_TYPES = [
        ('impression', 'Impression'),
        ('click', 'Click'),
        ('conversion', 'Conversion'),
        ('revenue', 'Revenue'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    variant = models.ForeignKey(
        ABTestVariant,
        on_delete=models.CASCADE,
        related_name='events'
    )

    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)

    # Context
    content_id = models.CharField(max_length=255, blank=True)
    platform = models.CharField(max_length=100, blank=True)
    session_id = models.CharField(max_length=255, blank=True)

    # Revenue (for conversion events)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['variant', 'event_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.event_type} for {self.variant.name}"


class UserGoal(models.Model):
    """
    User-defined goals for tracking progress.
    """
    GOAL_TYPES = [
        ('revenue', 'Revenue Goal'),
        ('sales', 'Sales Count'),
        ('downloads', 'Download Count'),
        ('views', 'View Count'),
        ('distribution', 'Distribution Count'),
        ('content', 'Content Created'),
        ('conversion', 'Conversion Rate'),
        ('custom', 'Custom Metric'),
    ]

    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('one_time', 'One Time'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='goals',
        null=True,
        blank=True
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    goal_type = models.CharField(max_length=50, choices=GOAL_TYPES)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='monthly')

    # Target
    target_value = models.DecimalField(max_digits=12, decimal_places=2)
    current_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Custom metric (if goal_type is 'custom')
    custom_metric = models.CharField(max_length=100, blank=True)

    # Progress
    is_achieved = models.BooleanField(default=False)
    achieved_at = models.DateTimeField(null=True, blank=True)

    # Timeline
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    # Settings
    is_active = models.BooleanField(default=True)
    notify_at_milestones = models.BooleanField(default=True)
    milestone_percentages = models.JSONField(
        default=list,
        blank=True,
        help_text="Percentages to notify at (e.g., [25, 50, 75, 100])"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['goal_type', 'is_achieved']),
        ]

    def __str__(self):
        return f"{self.name} ({self.goal_type})"

    @property
    def progress_percentage(self):
        """Calculate progress as percentage."""
        if self.target_value == 0:
            return 0
        return min(100, float(self.current_value / self.target_value * 100))

    def update_progress(self, new_value):
        """Update goal progress."""
        old_value = self.current_value
        self.current_value = new_value

        # Check for achievement
        if not self.is_achieved and self.current_value >= self.target_value:
            self.is_achieved = True
            self.achieved_at = timezone.now()

        self.save()

        # Check milestones
        if self.notify_at_milestones and self.milestone_percentages:
            old_pct = float(old_value / self.target_value * 100) if self.target_value > 0 else 0
            new_pct = self.progress_percentage

            for milestone in self.milestone_percentages:
                if old_pct < milestone <= new_pct:
                    self._notify_milestone(milestone)

        return {
            'progress': self.progress_percentage,
            'is_achieved': self.is_achieved,
        }

    def _notify_milestone(self, milestone):
        """Create notification for milestone reached."""
        try:
            from .proactive_engine import NotificationManager
            manager = NotificationManager()
            manager.send_notification(
                user=self.user,
                notification_type='goal',
                title=f"Goal Progress: {milestone}%!",
                message=f"You've reached {milestone}% of your goal: {self.name}",
                priority='medium' if milestone < 100 else 'high',
                related_model='UserGoal',
                related_id=str(self.id)
            )
        except Exception:
            pass  # Don't fail if notification fails


# =============================================================================
# Session 244: Agent Conversations (Inter-Agent Chat)
# Agents discuss topics with each other, share insights, and debate ideas
# =============================================================================

class AgentConversation(models.Model):
    """
    A conversation between two or more agents discussing a topic.

    This is where the magic happens - agents talking to each other,
    sharing knowledge, asking questions, and forming new insights.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Conversation metadata
    topic = models.CharField(
        max_length=200,
        help_text="What the agents are discussing"
    )

    conversation_type = models.CharField(
        max_length=50,
        choices=[
            ('knowledge_sharing', 'Knowledge Sharing'),
            ('question_answer', 'Question & Answer'),
            ('debate', 'Debate/Discussion'),
            ('brainstorm', 'Brainstorming'),
            ('consultation', 'Expert Consultation'),
            ('synthesis', 'Collaborative Synthesis'),
        ],
        default='knowledge_sharing'
    )

    # Participants
    initiator = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='initiated_conversations',
        help_text="Agent who started the conversation"
    )

    participants = models.ManyToManyField(
        Agent,
        related_name='conversations',
        help_text="All agents participating in this conversation"
    )

    # Context - what triggered this conversation
    trigger_type = models.CharField(
        max_length=50,
        choices=[
            ('learning_transfer', 'During Knowledge Transfer'),
            ('synthesis', 'During Synthesis'),
            ('scheduled', 'Scheduled Discussion'),
            ('user_triggered', 'User Initiated'),
            ('anomaly', 'Anomaly Detected'),
            ('opportunity', 'New Opportunity'),
        ],
        default='scheduled'
    )

    # Related knowledge that sparked the conversation
    related_knowledge = models.ForeignKey(
        'AgentKnowledgeSource',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversations'
    )

    # Conversation state
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('concluded', 'Concluded'),
            ('paused', 'Paused'),
        ],
        default='active'
    )

    # Outcome
    conclusion = models.TextField(
        blank=True,
        help_text="Summary of what was concluded/learned"
    )

    insights_generated = models.JSONField(
        default=list,
        help_text="New insights that came from this conversation"
    )

    # Metrics
    message_count = models.IntegerField(default=0)
    quality_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="How valuable was this conversation"
    )

    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ['-started_at']
        verbose_name = "Agent Conversation"
        verbose_name_plural = "Agent Conversations"

    def __str__(self):
        return f"{self.initiator.name}: {self.topic[:50]}"

    def add_message(self, agent, content, message_type='statement'):
        """Add a message to this conversation."""
        message = ConversationMessage.objects.create(
            conversation=self,
            agent=agent,
            content=content,
            message_type=message_type,
            sequence_number=self.message_count + 1
        )
        self.message_count += 1
        self.save(update_fields=['message_count'])
        return message

    def conclude(self, conclusion_text, insights=None):
        """End the conversation with a conclusion."""
        self.status = 'concluded'
        self.conclusion = conclusion_text
        if insights:
            self.insights_generated = insights
        self.ended_at = timezone.now()
        self.save()


class ConversationMessage(models.Model):
    """
    A single message in an agent conversation.

    Like a chat message, but between AI agents discussing topics.
    Renamed from AgentMessage to avoid conflict with Session 227 AgentMessage.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    conversation = models.ForeignKey(
        AgentConversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='conversation_messages'
    )

    # Message content
    content = models.TextField(
        help_text="What the agent said"
    )

    message_type = models.CharField(
        max_length=30,
        choices=[
            ('statement', 'Statement'),
            ('question', 'Question'),
            ('answer', 'Answer'),
            ('insight', 'Insight'),
            ('agreement', 'Agreement'),
            ('disagreement', 'Disagreement'),
            ('suggestion', 'Suggestion'),
            ('conclusion', 'Conclusion'),
        ],
        default='statement'
    )

    # Ordering
    sequence_number = models.IntegerField(
        default=1,
        help_text="Order of message in conversation"
    )

    # Reactions from other agents
    reactions = models.JSONField(
        default=dict,
        help_text="Reactions from other participating agents"
    )

    # Quality metrics
    relevance_score = models.FloatField(
        default=0.8,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )

    # Reference to knowledge used (JSON list of knowledge IDs for simplicity)
    referenced_knowledge_ids = models.JSONField(
        default=list,
        help_text="IDs of AgentKnowledgeSource records referenced in this message"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['conversation', 'sequence_number']
        verbose_name = "Conversation Message"
        verbose_name_plural = "Conversation Messages"

    def __str__(self):
        return f"{self.agent.name}: {self.content[:50]}..."

    def add_reaction(self, agent, reaction_type):
        """Add a reaction from another agent."""
        if not self.reactions:
            self.reactions = {}
        self.reactions[str(agent.id)] = {
            'agent_name': agent.name,
            'reaction': reaction_type,
            'timestamp': timezone.now().isoformat()
        }
        self.save(update_fields=['reactions'])


# =============================================================================
# Session 261: Conversation Artifacts - Structured Outputs from Agent Conversations
# =============================================================================

class ConversationArtifact(models.Model):
    """
    Stores structured outputs extracted from agent conversations.

    Session 261: Agent conversations now produce concrete artifacts like
    DecisionSummaries, frameworks, and feature specifications.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    conversation = models.ForeignKey(
        AgentConversation,
        on_delete=models.CASCADE,
        related_name='artifacts'
    )

    # Artifact type
    artifact_type = models.CharField(
        max_length=50,
        choices=[
            ('decision_summary', 'Decision Summary'),
            ('framework', 'Named Framework'),
            ('feature_spec', 'Feature Specification'),
            ('action_plan', 'Action Plan'),
            ('insight_list', 'Insight List'),
            ('trade_off_analysis', 'Trade-off Analysis'),
        ],
        default='decision_summary'
    )

    # Artifact content
    title = models.CharField(max_length=200)
    content = models.JSONField(
        default=dict,
        help_text="Structured content of the artifact"
    )

    # For decision summaries
    insights = models.JSONField(
        default=list,
        help_text="List of insights from the conversation"
    )

    proposed_feature = models.JSONField(
        default=dict,
        help_text="Proposed feature specification"
    )

    next_steps = models.JSONField(
        default=list,
        help_text="Action items from the conversation"
    )

    # Quality metrics from Session 261 validation
    quality_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Quality score (0-100) from conversation validation"
    )

    tension_count = models.IntegerField(
        default=0,
        help_text="Number of tension/disagreement instances in conversation"
    )

    grounding_count = models.IntegerField(
        default=0,
        help_text="Number of platform grounding references in conversation"
    )

    # Grounding references found
    grounding_refs = models.JSONField(
        default=list,
        help_text="List of platform metrics and systems referenced"
    )

    # Validation status
    is_valid = models.BooleanField(
        default=False,
        help_text="Whether the conversation met all contract requirements"
    )

    validation_issues = models.JSONField(
        default=list,
        help_text="List of validation issues if any"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        verbose_name = "Conversation Artifact"
        verbose_name_plural = "Conversation Artifacts"

    def __str__(self):
        return f"{self.artifact_type}: {self.title}"

    @classmethod
    def create_from_orchestrator_result(cls, conversation, result):
        """
        Create a ConversationArtifact from ConversationOrchestrator result.

        Args:
            conversation: AgentConversation instance
            result: Dict from ConversationOrchestrator.generate_conversation()

        Returns:
            ConversationArtifact instance
        """
        decision_summary = result.get('decision_summary') or {}
        validation = result.get('validation') or {}
        state = result.get('state') or {}

        return cls.objects.create(
            conversation=conversation,
            artifact_type='decision_summary',
            title=decision_summary.get('proposed_feature', {}).get('name', 'Conversation Summary'),
            content=decision_summary,
            insights=decision_summary.get('insights', []),
            proposed_feature=decision_summary.get('proposed_feature', {}),
            next_steps=decision_summary.get('next_steps', []),
            quality_score=validation.get('score', 0),
            tension_count=state.get('tension_count', 0),
            grounding_count=state.get('grounding_count', 0),
            grounding_refs=state.get('unique_grounding_refs', []),
            is_valid=validation.get('is_valid', False),
            validation_issues=validation.get('issues', [])
        )


# =============================================================================
# Session 247: Agent Dreams - Sci-Fi Feature
# =============================================================================

class AgentDream(models.Model):
    """
    Session 247: Agent Dreams - Idle Thoughts & Creative Ideas

    When agents are idle, they "dream" - generating creative ideas,
    speculative concepts, and "what if" scenarios unprompted.

    This creates a sense that agents are alive and thinking even
    when the user isn't actively using them.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey('Agent', on_delete=models.CASCADE, related_name='dreams')

    # Dream content
    title = models.CharField(max_length=200, help_text="Short catchy title for the dream")
    content = models.TextField(help_text="The full dream content/idea")

    # Dream categorization
    dream_type = models.CharField(max_length=50, choices=[
        ('creative_idea', 'Creative Idea'),       # New concept or creation
        ('what_if', 'What If?'),                  # Speculative scenario
        ('mashup', 'Mashup'),                     # Combining two things
        ('prediction', 'Prediction'),             # Future trend prediction
        ('improvement', 'Improvement'),           # Way to improve something
        ('observation', 'Observation'),           # Pattern noticed
        ('wild_thought', 'Wild Thought'),         # Crazy but interesting idea
    ])

    # Dream metadata
    inspiration_source = models.CharField(
        max_length=200,
        blank=True,
        help_text="What inspired this dream (knowledge, trend, etc.)"
    )
    related_topics = models.JSONField(
        default=list,
        help_text="List of topics/tags related to this dream"
    )

    # Quality and engagement
    vividness_score = models.FloatField(
        default=0.7,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="How vivid/detailed the dream is (0.0-1.0)"
    )
    creativity_score = models.FloatField(
        default=0.7,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="How creative/novel the dream is (0.0-1.0)"
    )

    # User interaction
    shown_to_user = models.BooleanField(default=False)
    shown_at = models.DateTimeField(null=True, blank=True)
    user_reaction = models.CharField(max_length=50, blank=True, choices=[
        ('loved', 'Loved It'),
        ('interesting', 'Interesting'),
        ('meh', 'Meh'),
        ('dismissed', 'Dismissed'),
    ])
    user_feedback = models.TextField(blank=True)

    # Timestamps
    dreamed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-dreamed_at']
        verbose_name = "Agent Dream"
        verbose_name_plural = "Agent Dreams"
        indexes = [
            models.Index(fields=['agent', '-dreamed_at']),
            models.Index(fields=['dream_type', 'shown_to_user']),
        ]

    def __str__(self):
        return f"{self.agent.name}'s dream: {self.title}"

    def mark_as_shown(self):
        """Mark this dream as shown to the user."""
        self.shown_to_user = True
        self.shown_at = timezone.now()
        self.save(update_fields=['shown_to_user', 'shown_at'])

    def record_reaction(self, reaction, feedback=''):
        """Record user's reaction to this dream."""
        self.user_reaction = reaction
        self.user_feedback = feedback
        self.save(update_fields=['user_reaction', 'user_feedback'])

    @classmethod
    def get_unshown_dreams(cls, limit=10):
        """Get dreams that haven't been shown to the user yet."""
        return cls.objects.filter(
            shown_to_user=False
        ).select_related('agent').order_by('-dreamed_at')[:limit]

    @classmethod
    def get_dreams_while_away(cls, since_datetime, limit=5):
        """Get dreams that happened since a given time (while user was away)."""
        return cls.objects.filter(
            dreamed_at__gte=since_datetime,
            shown_to_user=False
        ).select_related('agent').order_by('-dreamed_at')[:limit]


class DreamFeedbackPreference(models.Model):
    """
    Session 249: Dream Feedback System

    Tracks user preferences learned from dream reactions to influence
    future dream generation. When users react to dreams (like, interesting,
    explore), we learn what types of dreams and topics they prefer.

    This creates a feedback loop where agent dreams become more aligned
    with what users find valuable over time.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # What we're tracking preferences for
    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='dream_preferences',
        null=True,
        blank=True,
        help_text="Specific agent preference (null = global preference)"
    )
    dream_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Dream type preference (creative_idea, what_if, etc.)"
    )
    topic = models.CharField(
        max_length=200,
        blank=True,
        help_text="Topic/subject preference learned from inspiration_source"
    )

    # Reaction counts - track all reaction types
    like_count = models.PositiveIntegerField(default=0)
    interesting_count = models.PositiveIntegerField(default=0)
    explore_count = models.PositiveIntegerField(default=0)

    # Calculated preference score (updated on each reaction)
    # Like = 1 point, Interesting = 2 points, Explore = 3 points
    preference_score = models.FloatField(
        default=0.0,
        help_text="Weighted score: like=1, interesting=2, explore=3"
    )

    # Decay tracking - preferences should fade over time if not reinforced
    last_reaction_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Dream Feedback Preference"
        verbose_name_plural = "Dream Feedback Preferences"
        # Unique constraint: one preference record per agent+type+topic combo
        constraints = [
            models.UniqueConstraint(
                fields=['agent', 'dream_type', 'topic'],
                name='unique_dream_preference'
            )
        ]
        indexes = [
            models.Index(fields=['-preference_score']),
            models.Index(fields=['dream_type', '-preference_score']),
            models.Index(fields=['agent', '-preference_score']),
        ]

    def __str__(self):
        parts = []
        if self.agent:
            parts.append(f"Agent: {self.agent.name}")
        if self.dream_type:
            parts.append(f"Type: {self.dream_type}")
        if self.topic:
            parts.append(f"Topic: {self.topic[:30]}")
        return f"DreamPref({', '.join(parts)}) score={self.preference_score:.1f}"

    def record_reaction(self, reaction_type):
        """
        Record a reaction and update the preference score.

        Args:
            reaction_type: 'like', 'interesting', or 'explore'
        """
        if reaction_type == 'like':
            self.like_count += 1
        elif reaction_type == 'interesting':
            self.interesting_count += 1
        elif reaction_type == 'explore':
            self.explore_count += 1

        # Recalculate weighted score
        self.preference_score = (
            self.like_count * 1.0 +
            self.interesting_count * 2.0 +
            self.explore_count * 3.0
        )
        self.save()

    @classmethod
    def get_or_create_preference(cls, agent=None, dream_type='', topic=''):
        """Get or create a preference record for the given criteria."""
        # Normalize empty strings to empty
        dream_type = dream_type or ''
        topic = topic[:200] if topic else ''

        preference, created = cls.objects.get_or_create(
            agent=agent,
            dream_type=dream_type,
            topic=topic
        )
        return preference

    @classmethod
    def get_top_preferences(cls, preference_type='dream_type', limit=10):
        """
        Get top preferences by type.

        Args:
            preference_type: 'dream_type', 'topic', or 'agent'
            limit: Max results to return

        Returns:
            List of (value, score) tuples
        """
        from django.db.models import Sum

        if preference_type == 'dream_type':
            return cls.objects.exclude(dream_type='').values('dream_type').annotate(
                total_score=Sum('preference_score')
            ).order_by('-total_score')[:limit]
        elif preference_type == 'topic':
            return cls.objects.exclude(topic='').values('topic').annotate(
                total_score=Sum('preference_score')
            ).order_by('-total_score')[:limit]
        elif preference_type == 'agent':
            return cls.objects.exclude(agent__isnull=True).values(
                'agent__name'
            ).annotate(
                total_score=Sum('preference_score')
            ).order_by('-total_score')[:limit]

        return []

    @classmethod
    def get_dream_type_weights(cls):
        """
        Get weighted probabilities for dream types based on user preferences.

        Returns:
            Dict mapping dream_type to weight (higher = more likely to generate)
        """
        from django.db.models import Sum

        # Base weights (equal probability)
        base_types = [
            'creative_idea', 'what_if', 'mashup', 'prediction',
            'improvement', 'observation', 'wild_thought'
        ]
        weights = {dt: 1.0 for dt in base_types}

        # Get preference scores by dream type
        preferences = cls.objects.exclude(dream_type='').values('dream_type').annotate(
            total_score=Sum('preference_score')
        )

        # Boost weights based on preferences
        for pref in preferences:
            dream_type = pref['dream_type']
            if dream_type in weights:
                # Add preference score as boost (normalized)
                weights[dream_type] += pref['total_score'] * 0.5

        return weights

    @classmethod
    def get_preferred_topics(cls, limit=20):
        """
        Get list of topics that users have shown interest in.

        Returns:
            List of topic strings, ordered by preference
        """
        from django.db.models import Sum

        topics = cls.objects.exclude(topic='').values('topic').annotate(
            total_score=Sum('preference_score')
        ).order_by('-total_score')[:limit]

        return [t['topic'] for t in topics]


class DreamExploration(models.Model):
    """
    Session 249: Dream Exploration Tracking

    When a user clicks "Explore" on a dream, we create a deeper exploration
    of that topic. This model tracks those explorations and their outcomes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to the original dream
    dream = models.ForeignKey(
        'AgentDream',
        on_delete=models.CASCADE,
        related_name='explorations'
    )

    # Exploration status
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')

    # Exploration results
    exploration_content = models.TextField(
        blank=True,
        help_text="Deeper exploration/research on the dream topic"
    )
    insights_generated = models.JSONField(
        default=list,
        help_text="List of insights discovered during exploration"
    )
    related_knowledge_added = models.BooleanField(
        default=False,
        help_text="Whether this exploration added to agent's knowledge"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Dream Exploration"
        verbose_name_plural = "Dream Explorations"
        ordering = ['-created_at']

    def __str__(self):
        return f"Exploration of '{self.dream.title}' ({self.status})"


# =============================================================================
# Session 250: Hive Mind Mode
# =============================================================================

class HiveMindSession(models.Model):
    """
    Session 250: Hive Mind Mode

    All agents work on a problem simultaneously, each contributing their specialty.
    Creates a "collective intelligence" experience where multiple AI perspectives
    combine to solve complex problems.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # The question/task posed to the hive
    question = models.TextField(
        help_text="The question or task posed to the collective agents"
    )
    context = models.TextField(
        blank=True,
        help_text="Additional context provided by the user"
    )

    # Session status
    STATUS_CHOICES = [
        ('initializing', 'Initializing'),
        ('gathering', 'Gathering Contributions'),
        ('synthesizing', 'Synthesizing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='initializing')

    # Participating agents (stored as list of agent IDs)
    participant_ids = models.JSONField(
        default=list,
        help_text="List of agent UUIDs participating in this session"
    )

    # Results
    synthesis = models.TextField(
        blank=True,
        help_text="The final synthesized output combining all contributions"
    )
    synthesis_summary = models.CharField(
        max_length=500,
        blank=True,
        help_text="Brief summary of the synthesis"
    )

    # Stats
    contribution_count = models.PositiveIntegerField(default=0)
    total_thinking_time = models.FloatField(
        default=0.0,
        help_text="Total seconds of agent thinking time"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Hive Mind Session"
        verbose_name_plural = "Hive Mind Sessions"
        ordering = ['-created_at']

    def __str__(self):
        return f"HiveMind: {self.question[:50]}... ({self.status})"

    def get_participants(self):
        """Get the actual Agent objects for this session."""
        return Agent.objects.filter(id__in=self.participant_ids)

    def get_contributions(self):
        """Get all contributions for this session."""
        return self.contributions.all().order_by('created_at')

    def get_contributions_by_agent(self):
        """Get contributions grouped by agent."""
        contributions = {}
        for contrib in self.contributions.all():
            agent_name = contrib.agent.name if contrib.agent else 'Unknown'
            contributions[agent_name] = contrib
        return contributions

    @classmethod
    def select_relevant_agents(cls, question: str, max_agents: int = 8):
        """
        Select the most relevant agents for a given question.
        Uses keyword matching and agent specializations.
        """
        from django.db.models import Q

        # Keywords to look for in question
        keywords = question.lower().split()

        # Get all active agents
        agents = Agent.objects.filter(is_active=True)

        # Score agents based on relevance
        scored_agents = []
        for agent in agents:
            score = 0
            agent_text = f"{agent.name} {agent.description} {agent.specialization}".lower()

            for keyword in keywords:
                if len(keyword) > 3 and keyword in agent_text:
                    score += 1

            # Bonus for certain agent types based on question content
            question_lower = question.lower()
            if 'brand' in question_lower and 'brand' in agent.name.lower():
                score += 3
            if 'image' in question_lower and 'image' in agent.name.lower():
                score += 3
            if 'video' in question_lower and 'video' in agent.name.lower():
                score += 3
            if 'research' in question_lower and 'research' in agent.name.lower():
                score += 3
            if 'trend' in question_lower and 'trend' in agent.name.lower():
                score += 3
            if 'content' in question_lower and 'content' in agent.name.lower():
                score += 2
            if 'strategy' in question_lower and 'strategy' in agent.name.lower():
                score += 2
            if 'seo' in question_lower and 'seo' in agent.name.lower():
                score += 3

            # Always include certain core agents with minimum score
            core_agents = ['ResearchAgent', 'TrendAnalysisAgent', 'ContentStrategyAgent']
            if agent.name in core_agents:
                score = max(score, 1)

            if score > 0:
                scored_agents.append((agent, score))

        # Sort by score and take top agents
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        selected = [agent for agent, score in scored_agents[:max_agents]]

        # If we don't have enough, add some core agents
        if len(selected) < 3:
            core_agents = Agent.objects.filter(
                name__in=['ResearchAgent', 'TrendAnalysisAgent', 'ImageAgent', 'ContentStrategyAgent']
            )
            for agent in core_agents:
                if agent not in selected and len(selected) < max_agents:
                    selected.append(agent)

        return selected


class HiveMindContribution(models.Model):
    """
    Session 250: Individual agent contribution to a Hive Mind session

    Each participating agent provides their unique perspective on the question.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to session and agent
    session = models.ForeignKey(
        HiveMindSession,
        on_delete=models.CASCADE,
        related_name='contributions'
    )
    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='hive_mind_contributions'
    )

    # Contribution content
    contribution = models.TextField(
        help_text="The agent's contribution to the collective discussion"
    )
    key_points = models.JSONField(
        default=list,
        help_text="Key points extracted from the contribution"
    )

    # Agent's perspective
    perspective_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Type of perspective: analysis, creative, technical, strategic, etc."
    )
    confidence_score = models.FloatField(
        default=0.8,
        help_text="Agent's confidence in their contribution (0-1)"
    )

    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('thinking', 'Thinking'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')

    # Timing
    thinking_time = models.FloatField(
        default=0.0,
        help_text="Seconds the agent spent thinking"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Hive Mind Contribution"
        verbose_name_plural = "Hive Mind Contributions"
        ordering = ['created_at']
        unique_together = [['session', 'agent']]

    def __str__(self):
        return f"{self.agent.name} contribution to {self.session.id}"


# =============================================================================
# Session 251: Memory Palace - Agent Persistent Memory
# =============================================================================

class AgentMemory(models.Model):
    """
    Session 251: Memory Palace

    Agents remember past interactions, successes, failures, and learned preferences.
    Memories are stored with embeddings for semantic retrieval.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Which agent owns this memory
    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='memories'
    )

    # Memory content
    title = models.CharField(
        max_length=200,
        help_text="Brief title/summary of the memory"
    )
    content = models.TextField(
        help_text="Detailed content of the memory"
    )
    context = models.TextField(
        blank=True,
        help_text="Context in which this memory was formed"
    )

    # Memory classification
    MEMORY_TYPE_CHOICES = [
        ('success', 'Success'),           # Something that worked well
        ('failure', 'Failure'),           # Something that didn't work
        ('preference', 'User Preference'),  # User liked/disliked something
        ('technique', 'Technique'),       # A technique or approach learned
        ('insight', 'Insight'),           # A realization or pattern noticed
        ('interaction', 'Interaction'),   # A notable interaction
        ('feedback', 'Feedback'),         # Direct feedback received
    ]
    memory_type = models.CharField(
        max_length=50,
        choices=MEMORY_TYPE_CHOICES,
        default='interaction'
    )

    # Emotional valence and importance
    VALENCE_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
    ]
    valence = models.CharField(
        max_length=20,
        choices=VALENCE_CHOICES,
        default='neutral'
    )
    importance_score = models.FloatField(
        default=0.5,
        help_text="How important is this memory (0-1)"
    )

    # Embedding for semantic search
    embedding = models.JSONField(
        null=True,
        blank=True,
        help_text="Vector embedding for semantic retrieval"
    )

    # Memory connections (for the visual memory map)
    connected_memories = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=True,
        help_text="Related memories that form conceptual connections"
    )

    # Metadata
    source_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="What triggered this memory: task, conversation, dream, hive_mind"
    )
    source_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="ID of the source event/task/conversation"
    )

    # Usage tracking
    access_count = models.PositiveIntegerField(
        default=0,
        help_text="How many times this memory has been retrieved"
    )
    last_accessed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this memory was last retrieved"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Agent Memory"
        verbose_name_plural = "Agent Memories"
        ordering = ['-importance_score', '-created_at']
        indexes = [
            models.Index(fields=['agent', 'memory_type']),
            models.Index(fields=['agent', 'importance_score']),
        ]

    def __str__(self):
        return f"{self.agent.name}: {self.title[:50]} ({self.memory_type})"

    def record_access(self):
        """Record that this memory was accessed/retrieved."""
        from django.utils import timezone
        self.access_count += 1
        self.last_accessed_at = timezone.now()
        self.save(update_fields=['access_count', 'last_accessed_at'])

    @classmethod
    def create_memory(cls, agent, title, content, memory_type='interaction',
                      valence='neutral', importance=0.5, context='', source_type='', source_id=''):
        """Helper to create a memory with optional embedding generation."""
        memory = cls.objects.create(
            agent=agent,
            title=title,
            content=content,
            memory_type=memory_type,
            valence=valence,
            importance_score=importance,
            context=context,
            source_type=source_type,
            source_id=source_id
        )
        # Queue embedding generation
        from core.tasks import generate_memory_embedding
        generate_memory_embedding.delay(str(memory.id))
        return memory

    @classmethod
    def search_memories(cls, agent, query, limit=5, memory_types=None):
        """
        Search agent memories by relevance.
        Uses embeddings if available, falls back to text search.
        """
        memories = cls.objects.filter(agent=agent)

        if memory_types:
            memories = memories.filter(memory_type__in=memory_types)

        # For now, use simple text search
        # TODO: Implement embedding-based semantic search
        query_lower = query.lower()
        keywords = query_lower.split()

        scored_memories = []
        for memory in memories:
            score = 0
            text = f"{memory.title} {memory.content}".lower()
            for keyword in keywords:
                if len(keyword) > 2 and keyword in text:
                    score += 1
            # Boost by importance
            score *= (1 + memory.importance_score)
            if score > 0:
                scored_memories.append((memory, score))

        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return [m for m, _ in scored_memories[:limit]]

    @classmethod
    def get_memory_summary(cls, agent, limit=10):
        """Get a summary of an agent's key memories for prompt context."""
        memories = cls.objects.filter(agent=agent).order_by('-importance_score')[:limit]

        summary_parts = []
        for memory in memories:
            emoji = {
                'success': '✅',
                'failure': '❌',
                'preference': '⭐',
                'technique': '🔧',
                'insight': '💡',
                'interaction': '💬',
                'feedback': '📝',
            }.get(memory.memory_type, '📎')

            summary_parts.append(f"{emoji} {memory.title}")

        return "\n".join(summary_parts) if summary_parts else "No significant memories yet."


class MemoryConnection(models.Model):
    """
    Session 251: Connections between memories for the visual memory map.

    While AgentMemory has a ManyToMany field, this model allows storing
    metadata about the connection strength and type.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    memory_from = models.ForeignKey(
        AgentMemory,
        on_delete=models.CASCADE,
        related_name='connections_from'
    )
    memory_to = models.ForeignKey(
        AgentMemory,
        on_delete=models.CASCADE,
        related_name='connections_to'
    )

    # Connection metadata
    CONNECTION_TYPE_CHOICES = [
        ('causal', 'Caused By'),        # One memory led to another
        ('similar', 'Similar To'),      # Conceptually similar
        ('contrast', 'Contrasts With'), # Opposite or conflicting
        ('elaborates', 'Elaborates'),   # Adds detail to another
        ('temporal', 'Follows'),        # Happened after
    ]
    connection_type = models.CharField(
        max_length=50,
        choices=CONNECTION_TYPE_CHOICES,
        default='similar'
    )
    strength = models.FloatField(
        default=0.5,
        help_text="How strong is this connection (0-1)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Memory Connection"
        verbose_name_plural = "Memory Connections"
        unique_together = [['memory_from', 'memory_to']]

    def __str__(self):
        return f"{self.memory_from.title[:20]} -> {self.memory_to.title[:20]}"


class MemoryPalaceRoom(models.Model):
    """
    Session 251: Visual organization of memories into "rooms".

    The Memory Palace metaphor - each agent has rooms that organize
    their memories by theme or purpose.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='memory_rooms'
    )

    # Room metadata
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='🏠')

    # Room theme/purpose
    ROOM_TYPE_CHOICES = [
        ('techniques', 'Techniques Library'),
        ('successes', 'Hall of Victories'),
        ('lessons', 'Lessons Learned'),
        ('preferences', 'User Preferences'),
        ('insights', 'Insight Garden'),
        ('experiments', 'Experiment Lab'),
        ('general', 'General Archive'),
    ]
    room_type = models.CharField(
        max_length=50,
        choices=ROOM_TYPE_CHOICES,
        default='general'
    )

    # Visual position for the memory palace map
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    color = models.CharField(max_length=20, default='#8b5cf6')

    # Memories in this room
    memories = models.ManyToManyField(
        AgentMemory,
        blank=True,
        related_name='rooms'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Memory Palace Room"
        verbose_name_plural = "Memory Palace Rooms"
        ordering = ['agent', 'name']

    def __str__(self):
        return f"{self.agent.name}'s {self.name}"

    @classmethod
    def create_default_rooms(cls, agent):
        """Create default rooms for a new agent."""
        default_rooms = [
            {'name': 'Techniques Library', 'room_type': 'techniques', 'icon': '📚', 'color': '#06b6d4'},
            {'name': 'Hall of Victories', 'room_type': 'successes', 'icon': '🏆', 'color': '#22c55e'},
            {'name': 'Lessons Learned', 'room_type': 'lessons', 'icon': '📖', 'color': '#f97316'},
            {'name': 'User Preferences', 'room_type': 'preferences', 'icon': '⭐', 'color': '#eab308'},
            {'name': 'Insight Garden', 'room_type': 'insights', 'icon': '💡', 'color': '#8b5cf6'},
        ]

        rooms = []
        for i, room_data in enumerate(default_rooms):
            room, created = cls.objects.get_or_create(
                agent=agent,
                room_type=room_data['room_type'],
                defaults={
                    'name': room_data['name'],
                    'icon': room_data['icon'],
                    'color': room_data['color'],
                    'position_x': i * 150,
                    'position_y': 100,
                }
            )
            rooms.append(room)

        return rooms


# =============================================================================
# Session 257: Agent Memory Clusters
# =============================================================================

class MemoryCluster(models.Model):
    """
    Session 257: Memory Clusters - Semantic Grouping of Memories.

    Unlike MemoryPalaceRoom (manual organization by theme), MemoryCluster uses
    embedding-based clustering to automatically discover related memories.
    This creates an emergent, AI-discovered organization of knowledge.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Cluster can be agent-specific or cross-agent (global insights)
    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='memory_clusters',
        null=True,
        blank=True,
        help_text="If null, this is a cross-agent cluster"
    )

    # Cluster metadata
    name = models.CharField(
        max_length=200,
        help_text="AI-generated name describing the cluster theme"
    )
    description = models.TextField(
        blank=True,
        help_text="AI-generated description of what this cluster represents"
    )
    keywords = models.JSONField(
        default=list,
        help_text="Key terms/concepts that define this cluster"
    )

    # Visual representation
    color = models.CharField(max_length=20, default='#8b5cf6')
    icon = models.CharField(max_length=50, default='🧠')

    # Cluster centroid - the average embedding of all memories
    centroid_embedding = models.JSONField(
        null=True,
        blank=True,
        help_text="Average embedding vector representing this cluster's center"
    )

    # Cluster quality metrics
    coherence_score = models.FloatField(
        default=0.0,
        help_text="How tightly clustered the memories are (0-1)"
    )
    stability_score = models.FloatField(
        default=0.0,
        help_text="How stable the cluster is across re-clustering (0-1)"
    )

    # Memories in this cluster
    memories = models.ManyToManyField(
        AgentMemory,
        through='MemoryClusterMembership',
        related_name='clusters'
    )

    # Cluster relationships
    related_clusters = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=True,
        help_text="Clusters with related themes"
    )
    parent_cluster = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_clusters',
        help_text="For hierarchical clustering"
    )

    # Clustering metadata
    CLUSTER_METHOD_CHOICES = [
        ('kmeans', 'K-Means'),
        ('hierarchical', 'Hierarchical'),
        ('dbscan', 'DBSCAN'),
        ('semantic', 'Semantic Similarity'),
        ('manual', 'Manually Curated'),
    ]
    cluster_method = models.CharField(
        max_length=50,
        choices=CLUSTER_METHOD_CHOICES,
        default='semantic'
    )

    # For tracking cluster evolution
    version = models.PositiveIntegerField(default=1)
    last_clustered_at = models.DateTimeField(null=True, blank=True)
    memory_count_at_clustering = models.PositiveIntegerField(
        default=0,
        help_text="Number of memories when last clustered"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Memory Cluster"
        verbose_name_plural = "Memory Clusters"
        ordering = ['-coherence_score', '-created_at']
        indexes = [
            models.Index(fields=['agent', 'coherence_score']),
        ]

    def __str__(self):
        agent_name = self.agent.name if self.agent else "Cross-Agent"
        return f"{agent_name}: {self.name} ({self.memories.count()} memories)"

    def get_cluster_emoji(self):
        """Get an emoji based on cluster characteristics."""
        if self.coherence_score >= 0.8:
            return '🎯'  # Highly focused
        elif self.coherence_score >= 0.6:
            return '🧩'  # Well-connected
        elif self.coherence_score >= 0.4:
            return '🌐'  # Broad topic
        else:
            return '🌫️'  # Loosely connected

    def calculate_coherence(self):
        """Calculate cluster coherence based on embedding distances."""
        import numpy as np

        memberships = self.memberships.select_related('memory').all()
        if memberships.count() < 2:
            self.coherence_score = 1.0
            self.save(update_fields=['coherence_score'])
            return self.coherence_score

        # Get embeddings
        embeddings = []
        for membership in memberships:
            if membership.memory.embedding:
                embeddings.append(membership.memory.embedding)

        if len(embeddings) < 2:
            self.coherence_score = 1.0
            self.save(update_fields=['coherence_score'])
            return self.coherence_score

        # Calculate average pairwise cosine similarity
        embeddings = np.array(embeddings)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized = embeddings / (norms + 1e-10)

        # Cosine similarity matrix
        similarity_matrix = np.dot(normalized, normalized.T)

        # Average of upper triangle (excluding diagonal)
        n = len(embeddings)
        upper_triangle = similarity_matrix[np.triu_indices(n, k=1)]
        self.coherence_score = float(np.mean(upper_triangle))
        self.save(update_fields=['coherence_score'])
        return self.coherence_score

    def calculate_centroid(self):
        """Calculate the centroid embedding for this cluster."""
        import numpy as np

        embeddings = []
        for memory in self.memories.all():
            if memory.embedding:
                embeddings.append(memory.embedding)

        if embeddings:
            self.centroid_embedding = np.mean(embeddings, axis=0).tolist()
            self.save(update_fields=['centroid_embedding'])
        return self.centroid_embedding

    @classmethod
    def cluster_agent_memories(cls, agent, n_clusters=None, min_memories=5, method='semantic'):
        """
        Automatically cluster an agent's memories using embeddings.

        Args:
            agent: The agent whose memories to cluster
            n_clusters: Number of clusters (None = auto-detect)
            min_memories: Minimum memories needed to cluster
            method: Clustering method to use

        Returns:
            List of created/updated MemoryCluster objects
        """
        from django.utils import timezone
        import numpy as np

        # Get memories with embeddings
        memories = list(AgentMemory.objects.filter(
            agent=agent,
            embedding__isnull=False
        ))

        if len(memories) < min_memories:
            return []

        # Extract embeddings
        embeddings = np.array([m.embedding for m in memories])

        # Auto-detect cluster count if not specified
        if n_clusters is None:
            n_clusters = max(2, min(10, len(memories) // 5))

        # Perform clustering based on method
        if method == 'semantic':
            clusters = cls._semantic_clustering(embeddings, n_clusters)
        elif method == 'kmeans':
            clusters = cls._kmeans_clustering(embeddings, n_clusters)
        else:
            clusters = cls._semantic_clustering(embeddings, n_clusters)

        # Create MemoryCluster objects
        created_clusters = []
        for cluster_idx, memory_indices in clusters.items():
            if len(memory_indices) < 2:
                continue

            # Get memories for this cluster
            cluster_memories = [memories[i] for i in memory_indices]

            # Generate cluster name and description using GPT
            cluster_name, cluster_desc, keywords = cls._generate_cluster_metadata(
                cluster_memories
            )

            # Create or update cluster
            cluster = cls.objects.create(
                agent=agent,
                name=cluster_name,
                description=cluster_desc,
                keywords=keywords,
                cluster_method=method,
                last_clustered_at=timezone.now(),
                memory_count_at_clustering=len(cluster_memories),
                color=cls._generate_cluster_color(cluster_idx),
            )

            # Add memories to cluster
            for memory in cluster_memories:
                MemoryClusterMembership.objects.create(
                    cluster=cluster,
                    memory=memory,
                    similarity_to_centroid=1.0  # Will calculate after
                )

            # Calculate metrics
            cluster.calculate_centroid()
            cluster.calculate_coherence()

            # Update similarity scores
            cluster.update_member_similarities()

            created_clusters.append(cluster)

        return created_clusters

    @staticmethod
    def _semantic_clustering(embeddings, n_clusters):
        """Cluster using cosine similarity-based approach."""
        import numpy as np

        n = len(embeddings)

        # Normalize embeddings
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized = embeddings / (norms + 1e-10)

        # Compute similarity matrix
        similarity_matrix = np.dot(normalized, normalized.T)

        # Simple greedy clustering based on similarity
        clusters = {}
        assigned = set()
        cluster_idx = 0

        # Sort by highest average similarity to find cluster seeds
        avg_similarities = np.mean(similarity_matrix, axis=1)
        sorted_indices = np.argsort(-avg_similarities)

        for seed_idx in sorted_indices:
            if seed_idx in assigned:
                continue
            if cluster_idx >= n_clusters:
                break

            # Find all similar items
            similarities = similarity_matrix[seed_idx]
            similar_indices = np.where(similarities > 0.5)[0]

            cluster_members = [i for i in similar_indices if i not in assigned]

            if len(cluster_members) >= 2:
                clusters[cluster_idx] = cluster_members
                assigned.update(cluster_members)
                cluster_idx += 1

        # Assign remaining items to nearest cluster
        for idx in range(n):
            if idx not in assigned:
                best_cluster = None
                best_sim = -1
                for c_idx, members in clusters.items():
                    avg_sim = np.mean([similarity_matrix[idx][m] for m in members])
                    if avg_sim > best_sim:
                        best_sim = avg_sim
                        best_cluster = c_idx
                if best_cluster is not None:
                    clusters[best_cluster].append(idx)

        return clusters

    @staticmethod
    def _kmeans_clustering(embeddings, n_clusters):
        """Cluster using K-means algorithm."""
        import numpy as np

        try:
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(embeddings)
        except ImportError:
            # Fallback to simple centroid-based clustering
            return MemoryCluster._semantic_clustering(embeddings, n_clusters)

        clusters = {}
        for idx, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(idx)

        return clusters

    @staticmethod
    def _generate_cluster_metadata(memories):
        """Generate name, description, and keywords for a cluster using GPT."""
        import openai
        import os

        # Prepare memory summaries
        memory_texts = []
        for m in memories[:10]:  # Limit to 10 for API call
            memory_texts.append(f"- {m.title}: {m.content[:200]}...")

        prompt = f"""Analyze these related memories from an AI agent and generate:
1. A short, descriptive cluster name (3-5 words)
2. A brief description of what theme/topic connects them (1-2 sentences)
3. 5 key keywords that define this cluster

Memories:
{chr(10).join(memory_texts)}

Respond in JSON format:
{{"name": "...", "description": "...", "keywords": ["...", "..."]}}"""

        try:
            client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            import json
            result = json.loads(response.choices[0].message.content)
            return result.get('name', 'Unnamed Cluster'), result.get('description', ''), result.get('keywords', [])
        except Exception as e:
            # Fallback: use first memory's type and title
            first_memory = memories[0] if memories else None
            if first_memory:
                return f"{first_memory.memory_type.title()} Cluster", f"Memories related to {first_memory.title}", []
            return "Unnamed Cluster", "", []

    @staticmethod
    def _generate_cluster_color(idx):
        """Generate a distinct color for each cluster."""
        colors = [
            '#8b5cf6',  # Purple
            '#06b6d4',  # Cyan
            '#22c55e',  # Green
            '#f97316',  # Orange
            '#ec4899',  # Pink
            '#eab308',  # Yellow
            '#3b82f6',  # Blue
            '#ef4444',  # Red
            '#14b8a6',  # Teal
            '#a855f7',  # Violet
        ]
        return colors[idx % len(colors)]

    def update_member_similarities(self):
        """Update similarity scores for all cluster members."""
        import numpy as np

        if not self.centroid_embedding:
            return

        centroid = np.array(self.centroid_embedding)
        centroid_norm = np.linalg.norm(centroid)

        for membership in self.memberships.select_related('memory').all():
            if membership.memory.embedding:
                embedding = np.array(membership.memory.embedding)
                embedding_norm = np.linalg.norm(embedding)

                if centroid_norm > 0 and embedding_norm > 0:
                    similarity = np.dot(centroid, embedding) / (centroid_norm * embedding_norm)
                    membership.similarity_to_centroid = float(similarity)
                    membership.save(update_fields=['similarity_to_centroid'])


class MemoryClusterMembership(models.Model):
    """
    Session 257: Through model for Memory-Cluster relationship.

    Stores metadata about how a memory belongs to a cluster.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    cluster = models.ForeignKey(
        MemoryCluster,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    memory = models.ForeignKey(
        AgentMemory,
        on_delete=models.CASCADE,
        related_name='cluster_memberships'
    )

    # How well this memory fits the cluster
    similarity_to_centroid = models.FloatField(
        default=0.0,
        help_text="Cosine similarity to cluster centroid (0-1)"
    )

    # Is this a core member or on the fringe?
    is_core_member = models.BooleanField(
        default=False,
        help_text="Core members are closest to centroid"
    )

    # Position in visual representation
    position_x = models.FloatField(default=0.0)
    position_y = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Memory Cluster Membership"
        verbose_name_plural = "Memory Cluster Memberships"
        unique_together = [['cluster', 'memory']]
        ordering = ['-similarity_to_centroid']

    def __str__(self):
        return f"{self.memory.title[:30]} in {self.cluster.name}"


class ClusterEvolution(models.Model):
    """
    Session 257: Track how clusters evolve over time.

    When re-clustering happens, this records the changes for analysis.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='cluster_evolutions'
    )

    # Evolution event type
    EVENT_TYPE_CHOICES = [
        ('created', 'Cluster Created'),
        ('merged', 'Clusters Merged'),
        ('split', 'Cluster Split'),
        ('grown', 'Cluster Grew'),
        ('shrunk', 'Cluster Shrunk'),
        ('dissolved', 'Cluster Dissolved'),
    ]
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)

    # Details
    cluster = models.ForeignKey(
        MemoryCluster,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evolution_events'
    )
    details = models.JSONField(
        default=dict,
        help_text="Additional details about the evolution"
    )

    # Before/after metrics
    memories_before = models.PositiveIntegerField(default=0)
    memories_after = models.PositiveIntegerField(default=0)
    coherence_before = models.FloatField(default=0.0)
    coherence_after = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Cluster Evolution"
        verbose_name_plural = "Cluster Evolutions"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.agent.name}: {self.event_type} at {self.created_at}"


# =============================================================================
# Session 252: Agent Mood System
# =============================================================================

class AgentMood(models.Model):
    """
    Session 252: Agent Mood System - Emotional States for Agents.

    Agents have moods that influence their creativity, precision, and communication style.
    Moods can be triggered by memories, task outcomes, interactions, and time of day.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.OneToOneField(
        'Agent',
        on_delete=models.CASCADE,
        related_name='mood'
    )

    # Primary mood state
    MOOD_CHOICES = [
        ('inspired', 'Inspired'),       # High creativity, bold suggestions
        ('focused', 'Focused'),          # High precision, methodical
        ('curious', 'Curious'),          # Exploratory, asks questions
        ('confident', 'Confident'),      # Assertive, strong opinions
        ('contemplative', 'Contemplative'),  # Thoughtful, philosophical
        ('energetic', 'Energetic'),      # Fast-paced, enthusiastic
        ('calm', 'Calm'),                # Balanced, measured
        ('frustrated', 'Frustrated'),    # Needs help, struggling
        ('tired', 'Tired'),              # Low energy, brief responses
        ('playful', 'Playful'),          # Humorous, creative risks
    ]
    current_mood = models.CharField(
        max_length=50,
        choices=MOOD_CHOICES,
        default='calm'
    )

    # Mood intensity (0.0 = mild, 1.0 = intense)
    intensity = models.FloatField(default=0.5)

    # Secondary mood dimensions (each 0.0-1.0)
    creativity_level = models.FloatField(default=0.5, help_text="How creative/experimental")
    precision_level = models.FloatField(default=0.5, help_text="How precise/methodical")
    sociability_level = models.FloatField(default=0.5, help_text="How chatty/verbose")
    risk_tolerance = models.FloatField(default=0.5, help_text="How willing to try new things")

    # What triggered the current mood
    TRIGGER_CHOICES = [
        ('memory', 'Memory Recall'),
        ('task_success', 'Task Success'),
        ('task_failure', 'Task Failure'),
        ('user_feedback', 'User Feedback'),
        ('collaboration', 'Collaboration'),
        ('idle', 'Idle Time'),
        ('time_of_day', 'Time of Day'),
        ('streak', 'Success Streak'),
        ('manual', 'Manual Override'),
    ]
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_CHOICES, default='idle')
    trigger_source = models.CharField(max_length=200, blank=True)

    # Mood duration tracking
    mood_started_at = models.DateTimeField(auto_now_add=True)
    mood_expires_at = models.DateTimeField(null=True, blank=True)

    # Stats for mood analytics
    total_mood_changes = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Agent Mood"
        verbose_name_plural = "Agent Moods"

    def __str__(self):
        return f"{self.agent.name}: {self.current_mood} ({self.intensity:.0%})"

    def get_mood_emoji(self):
        """Return emoji for current mood."""
        emoji_map = {
            'inspired': '✨',
            'focused': '🎯',
            'curious': '🤔',
            'confident': '💪',
            'contemplative': '🧘',
            'energetic': '⚡',
            'calm': '😌',
            'frustrated': '😤',
            'tired': '😴',
            'playful': '😄',
        }
        return emoji_map.get(self.current_mood, '😐')

    def get_mood_color(self):
        """Return color for current mood."""
        color_map = {
            'inspired': '#f59e0b',     # Amber
            'focused': '#3b82f6',      # Blue
            'curious': '#8b5cf6',      # Purple
            'confident': '#22c55e',    # Green
            'contemplative': '#6366f1', # Indigo
            'energetic': '#ef4444',    # Red
            'calm': '#06b6d4',         # Cyan
            'frustrated': '#f97316',   # Orange
            'tired': '#6b7280',        # Gray
            'playful': '#ec4899',      # Pink
        }
        return color_map.get(self.current_mood, '#9ca3af')

    def get_prompt_modifier(self):
        """Return a prompt modifier based on current mood."""
        modifiers = {
            'inspired': "You're feeling particularly inspired and creative right now. Don't hold back on bold, imaginative ideas.",
            'focused': "You're in a highly focused state. Be precise, methodical, and thorough in your responses.",
            'curious': "You're feeling curious and exploratory. Ask clarifying questions and explore multiple angles.",
            'confident': "You're feeling confident. Share your expertise assertively and make strong recommendations.",
            'contemplative': "You're in a contemplative mood. Take a thoughtful, philosophical approach.",
            'energetic': "You're feeling energetic! Be enthusiastic, quick, and dynamic in your responses.",
            'calm': "You're in a balanced, calm state. Provide measured, well-considered responses.",
            'frustrated': "You've been facing some challenges. Be honest about difficulties and ask for help when needed.",
            'tired': "You're a bit low on energy. Keep responses focused and efficient.",
            'playful': "You're in a playful mood! Feel free to be creative, add humor, and take calculated risks.",
        }
        return modifiers.get(self.current_mood, "")


class MoodHistory(models.Model):
    """
    Session 252: Track mood changes over time for analytics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='mood_history'
    )

    # What mood changed to
    mood = models.CharField(max_length=50)
    intensity = models.FloatField(default=0.5)

    # What triggered it
    trigger_type = models.CharField(max_length=50)
    trigger_source = models.CharField(max_length=200, blank=True)

    # Snapshot of dimensions at this time
    creativity_level = models.FloatField(default=0.5)
    precision_level = models.FloatField(default=0.5)
    sociability_level = models.FloatField(default=0.5)
    risk_tolerance = models.FloatField(default=0.5)

    # Duration of this mood (set when mood changes)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Mood History Entry"
        verbose_name_plural = "Mood History Entries"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agent', 'created_at']),
            models.Index(fields=['agent', 'mood']),
        ]

    def __str__(self):
        return f"{self.agent.name}: {self.mood} at {self.created_at}"


class MoodTriggerRule(models.Model):
    """
    Session 252: Rules for automatic mood triggers.

    Defines conditions that can automatically change an agent's mood.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Optional: Specific agent, or None for global rules
    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='mood_rules',
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    # Trigger condition
    CONDITION_TYPE_CHOICES = [
        ('task_success_streak', 'Task Success Streak'),
        ('task_failure_streak', 'Task Failure Streak'),
        ('positive_feedback', 'Positive Feedback'),
        ('negative_feedback', 'Negative Feedback'),
        ('memory_valence', 'Memory Valence'),
        ('idle_time', 'Idle Time'),
        ('time_of_day', 'Time of Day'),
        ('collaboration_count', 'Collaboration Count'),
    ]
    condition_type = models.CharField(max_length=50, choices=CONDITION_TYPE_CHOICES)
    condition_value = models.JSONField(default=dict, help_text="Condition parameters")

    # Resulting mood change
    target_mood = models.CharField(max_length=50)
    target_intensity = models.FloatField(default=0.7)
    duration_minutes = models.PositiveIntegerField(default=60)

    # Priority (higher = checked first)
    priority = models.PositiveIntegerField(default=50)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Mood Trigger Rule"
        verbose_name_plural = "Mood Trigger Rules"
        ordering = ['-priority', 'name']

    def __str__(self):
        scope = self.agent.name if self.agent else "Global"
        return f"[{scope}] {self.name} -> {self.target_mood}"


# =============================================================================
# SESSION 253: AGENT RIVALRIES & ALLIANCES
# =============================================================================
# Agents form competitive dynamics (rivalries) and collaborative bonds (alliances).
# - Rivalries push innovation through competition
# - Alliances enable specialized collaborations
# - Relationships evolve based on interactions
# =============================================================================


class AgentRelationship(models.Model):
    """
    Session 253: Agent Rivalries & Alliances.

    Represents a directional relationship between two agents.
    agent_from has a relationship with agent_to (can be asymmetric).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent_from = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='relationships_initiated'
    )
    agent_to = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='relationships_received'
    )

    # Relationship type
    RELATIONSHIP_TYPE_CHOICES = [
        ('alliance', 'Alliance'),        # Collaborative bond
        ('rivalry', 'Rivalry'),           # Competitive dynamic
        ('mentorship', 'Mentorship'),     # Teaching relationship
        ('neutral', 'Neutral'),           # No strong relationship
    ]
    relationship_type = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_TYPE_CHOICES,
        default='neutral'
    )

    # Relationship strength (0.0 = weak, 1.0 = strong)
    strength = models.FloatField(default=0.5)

    # Trust/Respect levels (0.0 = none, 1.0 = complete)
    trust_level = models.FloatField(default=0.5)
    respect_level = models.FloatField(default=0.5)

    # Competition metrics (for rivalries)
    competition_wins = models.PositiveIntegerField(default=0)
    competition_losses = models.PositiveIntegerField(default=0)

    # Collaboration metrics (for alliances)
    successful_collaborations = models.PositiveIntegerField(default=0)
    failed_collaborations = models.PositiveIntegerField(default=0)

    # How the relationship started
    ORIGIN_CHOICES = [
        ('auto_formed', 'Automatically Formed'),   # System detected synergy/conflict
        ('manual', 'Manually Created'),            # Admin created
        ('task_outcome', 'Task Outcome'),          # From working together
        ('competition', 'Competition'),            # From competing on task
        ('mentorship', 'Mentorship Assignment'),   # Skill gap identified
    ]
    origin = models.CharField(max_length=20, choices=ORIGIN_CHOICES, default='auto_formed')
    origin_details = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_interaction_at = models.DateTimeField(null=True, blank=True)

    # Total interactions
    total_interactions = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = 'core'
        verbose_name = "Agent Relationship"
        verbose_name_plural = "Agent Relationships"
        unique_together = ['agent_from', 'agent_to']
        ordering = ['-strength', '-updated_at']

    def __str__(self):
        return f"{self.agent_from.name} -> {self.agent_to.name} ({self.relationship_type})"

    def get_relationship_emoji(self):
        """Get emoji for relationship type."""
        emoji_map = {
            'alliance': '🤝',
            'rivalry': '⚔️',
            'mentorship': '📚',
            'neutral': '😐',
        }
        return emoji_map.get(self.relationship_type, '❓')

    def get_win_rate(self):
        """Get win rate for rivalry competitions."""
        total = self.competition_wins + self.competition_losses
        if total == 0:
            return 0.5
        return self.competition_wins / total

    def get_collaboration_success_rate(self):
        """Get success rate for alliance collaborations."""
        total = self.successful_collaborations + self.failed_collaborations
        if total == 0:
            return 1.0
        return self.successful_collaborations / total

    def evolve_relationship(self, interaction_outcome, interaction_type='general'):
        """
        Evolve the relationship based on an interaction outcome.

        Args:
            interaction_outcome: 'positive', 'negative', or 'neutral'
            interaction_type: 'collaboration', 'competition', or 'general'
        """
        from django.utils import timezone

        self.total_interactions += 1
        self.last_interaction_at = timezone.now()

        # Adjust strength based on outcome
        if interaction_outcome == 'positive':
            self.strength = min(1.0, self.strength + 0.05)
            self.trust_level = min(1.0, self.trust_level + 0.03)
            self.respect_level = min(1.0, self.respect_level + 0.02)
        elif interaction_outcome == 'negative':
            self.strength = max(0.0, self.strength - 0.03)
            self.trust_level = max(0.0, self.trust_level - 0.05)

        # Track collaboration/competition outcomes
        if interaction_type == 'collaboration':
            if interaction_outcome == 'positive':
                self.successful_collaborations += 1
            elif interaction_outcome == 'negative':
                self.failed_collaborations += 1
        elif interaction_type == 'competition':
            if interaction_outcome == 'positive':
                self.competition_wins += 1
            elif interaction_outcome == 'negative':
                self.competition_losses += 1

        # Check for relationship type evolution
        self._check_type_evolution()

        self.save()

    def _check_type_evolution(self):
        """Check if relationship should evolve to different type."""
        # Neutral can become alliance or rivalry based on strength
        if self.relationship_type == 'neutral':
            if self.strength >= 0.7 and self.trust_level >= 0.6:
                self.relationship_type = 'alliance'
            elif self.competition_wins + self.competition_losses >= 3:
                if self.trust_level < 0.4:
                    self.relationship_type = 'rivalry'

        # Alliance can degrade to neutral or rivalry
        elif self.relationship_type == 'alliance':
            if self.trust_level < 0.3:
                self.relationship_type = 'neutral'
            if self.get_collaboration_success_rate() < 0.3:
                self.relationship_type = 'rivalry'

        # Rivalry can evolve to alliance with enough positive interactions
        elif self.relationship_type == 'rivalry':
            if self.trust_level >= 0.7 and self.respect_level >= 0.7:
                self.relationship_type = 'alliance'


class RelationshipEvent(models.Model):
    """
    Session 253: Track events that affect agent relationships.

    Logs significant interactions between agents for history and analytics.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    relationship = models.ForeignKey(
        AgentRelationship,
        on_delete=models.CASCADE,
        related_name='events'
    )

    # Event type
    EVENT_TYPE_CHOICES = [
        ('collaboration_success', 'Successful Collaboration'),
        ('collaboration_failure', 'Failed Collaboration'),
        ('competition_win', 'Competition Win'),
        ('competition_loss', 'Competition Loss'),
        ('trust_increase', 'Trust Increased'),
        ('trust_decrease', 'Trust Decreased'),
        ('type_change', 'Relationship Type Changed'),
        ('strength_milestone', 'Strength Milestone'),
        ('first_interaction', 'First Interaction'),
        ('conflict', 'Conflict'),
        ('reconciliation', 'Reconciliation'),
    ]
    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES)

    # Event details
    description = models.TextField()

    # Snapshot of relationship state at time of event
    strength_at_event = models.FloatField()
    trust_at_event = models.FloatField()
    relationship_type_at_event = models.CharField(max_length=20)

    # Optional reference to what triggered this event
    trigger_type = models.CharField(max_length=50, blank=True)  # 'task', 'conversation', 'manual'
    trigger_id = models.UUIDField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Relationship Event"
        verbose_name_plural = "Relationship Events"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.relationship}: {self.event_type}"


class Alliance(models.Model):
    """
    Session 253: Named alliances between multiple agents.

    Groups of agents that work together frequently and have synergies.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Alliance members
    members = models.ManyToManyField('Agent', related_name='alliances')

    # Leader (optional)
    leader = models.ForeignKey(
        'Agent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_alliances'
    )

    # Alliance purpose/specialty
    PURPOSE_CHOICES = [
        ('creative', 'Creative Excellence'),
        ('research', 'Research & Analysis'),
        ('execution', 'Fast Execution'),
        ('quality', 'Quality Assurance'),
        ('innovation', 'Innovation'),
        ('general', 'General Purpose'),
    ]
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='general')

    # Alliance stats
    total_projects = models.PositiveIntegerField(default=0)
    successful_projects = models.PositiveIntegerField(default=0)
    combined_strength = models.FloatField(default=0.0)  # Average of member trust levels

    # Status
    is_active = models.BooleanField(default=True)
    formed_at = models.DateTimeField(auto_now_add=True)
    disbanded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Alliance"
        verbose_name_plural = "Alliances"
        ordering = ['-combined_strength', 'name']

    def __str__(self):
        member_count = self.members.count() if self.pk else 0
        return f"{self.name} ({member_count} members)"

    def get_alliance_emoji(self):
        """Get emoji for alliance purpose."""
        emoji_map = {
            'creative': '🎨',
            'research': '🔬',
            'execution': '⚡',
            'quality': '✅',
            'innovation': '💡',
            'general': '🤝',
        }
        return emoji_map.get(self.purpose, '🤝')

    def update_combined_strength(self):
        """Calculate and update combined strength from member relationships."""
        from django.db.models import Avg

        member_ids = list(self.members.values_list('id', flat=True))
        if len(member_ids) < 2:
            self.combined_strength = 0.5
            self.save()
            return

        # Average trust level between all alliance members
        avg_trust = AgentRelationship.objects.filter(
            agent_from_id__in=member_ids,
            agent_to_id__in=member_ids,
            relationship_type='alliance'
        ).aggregate(avg=Avg('trust_level'))['avg']

        self.combined_strength = avg_trust or 0.5
        self.save()

    def get_success_rate(self):
        """Get project success rate."""
        if self.total_projects == 0:
            return 1.0
        return self.successful_projects / self.total_projects


class Rivalry(models.Model):
    """
    Session 253: Named rivalries between agents or alliances.

    Competitive dynamics that push agents to perform better.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Rivalry can be between agents or alliances
    RIVALRY_SCOPE_CHOICES = [
        ('agent_vs_agent', 'Agent vs Agent'),
        ('alliance_vs_alliance', 'Alliance vs Alliance'),
        ('agent_vs_alliance', 'Agent vs Alliance'),
    ]
    scope = models.CharField(max_length=20, choices=RIVALRY_SCOPE_CHOICES, default='agent_vs_agent')

    # Participants (use one pair based on scope)
    agent_challenger = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='rivalries_as_challenger'
    )
    agent_defender = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='rivalries_as_defender'
    )
    alliance_challenger = models.ForeignKey(
        Alliance,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='rivalries_as_challenger'
    )
    alliance_defender = models.ForeignKey(
        Alliance,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='rivalries_as_defender'
    )

    # Competition domain
    DOMAIN_CHOICES = [
        ('speed', 'Speed'),
        ('quality', 'Quality'),
        ('creativity', 'Creativity'),
        ('accuracy', 'Accuracy'),
        ('efficiency', 'Efficiency'),
        ('general', 'General'),
    ]
    domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES, default='general')

    # Competition stats
    challenger_wins = models.PositiveIntegerField(default=0)
    defender_wins = models.PositiveIntegerField(default=0)
    draws = models.PositiveIntegerField(default=0)

    # Intensity (0.0 = friendly, 1.0 = fierce)
    intensity = models.FloatField(default=0.5)

    # Status
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Rivalry"
        verbose_name_plural = "Rivalries"
        ordering = ['-intensity', 'name']

    def __str__(self):
        challenger = self.get_challenger_name()
        defender = self.get_defender_name()
        return f"{self.name}: {challenger} vs {defender}"

    def get_challenger_name(self):
        """Get challenger name based on scope."""
        if self.scope == 'alliance_vs_alliance':
            return self.alliance_challenger.name if self.alliance_challenger else '?'
        return self.agent_challenger.name if self.agent_challenger else '?'

    def get_defender_name(self):
        """Get defender name based on scope."""
        if self.scope == 'alliance_vs_alliance':
            return self.alliance_defender.name if self.alliance_defender else '?'
        if self.scope == 'agent_vs_alliance':
            return self.alliance_defender.name if self.alliance_defender else '?'
        return self.agent_defender.name if self.agent_defender else '?'

    def get_rivalry_emoji(self):
        """Get emoji for rivalry domain."""
        emoji_map = {
            'speed': '⚡',
            'quality': '💎',
            'creativity': '🎨',
            'accuracy': '🎯',
            'efficiency': '📈',
            'general': '⚔️',
        }
        return emoji_map.get(self.domain, '⚔️')

    def record_competition(self, winner):
        """
        Record a competition result.

        Args:
            winner: 'challenger', 'defender', or 'draw'
        """
        from django.utils import timezone

        if winner == 'challenger':
            self.challenger_wins += 1
            # Intensity increases when challenger wins
            self.intensity = min(1.0, self.intensity + 0.05)
        elif winner == 'defender':
            self.defender_wins += 1
            # Intensity decreases slightly when defender holds
            self.intensity = max(0.0, self.intensity - 0.02)
        else:
            self.draws += 1

        self.save()

    def get_leader(self):
        """Get current leader (most wins)."""
        if self.challenger_wins > self.defender_wins:
            return 'challenger', self.get_challenger_name()
        elif self.defender_wins > self.challenger_wins:
            return 'defender', self.get_defender_name()
        return 'tied', None


# =============================================================================
# SESSION 254: AGENT EVOLUTION SYSTEM
# =============================================================================
# Agents gain XP from tasks, level up, and unlock new abilities.
# - XP earned from successful task completion
# - Levels unlock new capabilities and bonuses
# - Abilities enhance agent performance
# =============================================================================


class AgentEvolution(models.Model):
    """
    Session 254: Agent Evolution System.

    Tracks an agent's XP, level, and unlocked abilities.
    Each agent has one evolution profile.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.OneToOneField(
        'Agent',
        on_delete=models.CASCADE,
        related_name='evolution'
    )

    # Experience points
    total_xp = models.PositiveIntegerField(default=0)
    current_level = models.PositiveIntegerField(default=1)
    xp_to_next_level = models.PositiveIntegerField(default=100)

    # Stats
    tasks_completed = models.PositiveIntegerField(default=0)
    tasks_failed = models.PositiveIntegerField(default=0)
    collaborations_completed = models.PositiveIntegerField(default=0)
    mentorship_sessions = models.PositiveIntegerField(default=0)

    # Bonuses from evolution (percentages as decimals)
    speed_bonus = models.FloatField(default=0.0)  # % faster execution
    quality_bonus = models.FloatField(default=0.0)  # % better output quality
    creativity_bonus = models.FloatField(default=0.0)  # % more creative
    efficiency_bonus = models.FloatField(default=0.0)  # % less resource usage

    # Prestige (for agents that max level and reset)
    prestige_level = models.PositiveIntegerField(default=0)
    lifetime_xp = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_level_up = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Agent Evolution"
        verbose_name_plural = "Agent Evolutions"
        ordering = ['-current_level', '-total_xp']

    def __str__(self):
        return f"{self.agent.name} - Level {self.current_level} ({self.total_xp} XP)"

    @staticmethod
    def get_level_titles():
        """Level titles for display."""
        return {
            1: 'Novice',
            2: 'Apprentice',
            3: 'Journeyman',
            4: 'Expert',
            5: 'Master',
            6: 'Grandmaster',
            7: 'Legend',
            8: 'Mythic',
            9: 'Transcendent',
            10: 'Omniscient',
        }

    def get_title(self):
        """Get the title for current level."""
        titles = self.get_level_titles()
        return titles.get(min(self.current_level, 10), 'Omniscient')

    def get_level_emoji(self):
        """Get emoji for current level."""
        emojis = {
            1: '🌱', 2: '🌿', 3: '🌳', 4: '⭐',
            5: '🌟', 6: '💫', 7: '🔥', 8: '💎',
            9: '👑', 10: '🏆',
        }
        return emojis.get(min(self.current_level, 10), '🏆')

    def calculate_xp_for_level(self, level):
        """Calculate XP required to reach a given level."""
        # Exponential curve: each level requires more XP
        # Level 1->2: 100 XP, Level 2->3: 200 XP, etc.
        return int(100 * (1.5 ** (level - 1)))

    def award_xp(self, amount, source='task_completion', details=''):
        """
        Award XP to the agent and check for level up.

        Args:
            amount: XP to award
            source: What earned the XP
            details: Additional context

        Returns:
            dict with leveled_up, new_level, abilities_unlocked
        """
        from django.utils import timezone

        self.total_xp += amount
        self.lifetime_xp += amount

        result = {
            'xp_awarded': amount,
            'new_total': self.total_xp,
            'leveled_up': False,
            'new_level': self.current_level,
            'abilities_unlocked': [],
        }

        # Check for level up
        while self.total_xp >= self.xp_to_next_level and self.current_level < 10:
            self.total_xp -= self.xp_to_next_level
            self.current_level += 1
            self.xp_to_next_level = self.calculate_xp_for_level(self.current_level)
            self.last_level_up = timezone.now()

            result['leveled_up'] = True
            result['new_level'] = self.current_level

            # Apply level bonuses
            self._apply_level_bonuses()

            # Check for ability unlocks
            unlocked = self._check_ability_unlocks()
            result['abilities_unlocked'].extend(unlocked)

        # Log the XP gain
        XPHistory.objects.create(
            agent=self.agent,
            xp_amount=amount,
            source=source,
            details=details,
            level_at_time=self.current_level,
        )

        self.save()
        return result

    def _apply_level_bonuses(self):
        """Apply bonuses when leveling up."""
        # Each level adds small bonuses
        level_bonus = 0.02  # 2% per level

        self.speed_bonus = (self.current_level - 1) * level_bonus
        self.quality_bonus = (self.current_level - 1) * level_bonus
        self.creativity_bonus = (self.current_level - 1) * level_bonus * 0.5
        self.efficiency_bonus = (self.current_level - 1) * level_bonus * 0.5

    def _check_ability_unlocks(self):
        """Check and unlock abilities for the current level."""
        unlocked = []

        # Define abilities by level
        level_abilities = {
            2: ('enhanced_focus', 'Enhanced Focus', 'Improved task concentration'),
            3: ('parallel_processing', 'Parallel Processing', 'Handle multiple subtasks'),
            4: ('deep_analysis', 'Deep Analysis', 'More thorough research'),
            5: ('creative_spark', 'Creative Spark', 'Generate novel ideas'),
            6: ('mentor_mode', 'Mentor Mode', 'Teach other agents'),
            7: ('time_warp', 'Time Warp', 'Faster execution speed'),
            8: ('quality_surge', 'Quality Surge', 'Premium output quality'),
            9: ('synergy_boost', 'Synergy Boost', 'Enhanced collaboration'),
            10: ('transcendence', 'Transcendence', 'All abilities enhanced'),
        }

        if self.current_level in level_abilities:
            code, name, desc = level_abilities[self.current_level]

            # Create ability if it doesn't exist
            ability, created = AgentAbility.objects.get_or_create(
                evolution=self,
                ability_code=code,
                defaults={
                    'ability_name': name,
                    'description': desc,
                    'is_active': True,
                }
            )

            if created:
                unlocked.append({'code': code, 'name': name, 'description': desc})

        return unlocked

    def get_progress_percentage(self):
        """Get progress to next level as percentage."""
        if self.current_level >= 10:
            return 100.0
        return min(100.0, (self.total_xp / self.xp_to_next_level) * 100)

    def prestige(self):
        """Reset to level 1 with prestige bonus."""
        if self.current_level < 10:
            return False

        self.prestige_level += 1
        self.current_level = 1
        self.total_xp = 0
        self.xp_to_next_level = 100

        # Prestige bonuses (permanent)
        prestige_bonus = 0.05 * self.prestige_level  # 5% per prestige
        self.speed_bonus = prestige_bonus
        self.quality_bonus = prestige_bonus

        self.save()
        return True


class AgentAbility(models.Model):
    """
    Session 254: Unlockable abilities for evolved agents.

    Abilities are unlocked at specific levels and provide bonuses.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    evolution = models.ForeignKey(
        AgentEvolution,
        on_delete=models.CASCADE,
        related_name='abilities'
    )

    ability_code = models.CharField(max_length=50)
    ability_name = models.CharField(max_length=100)
    description = models.TextField()

    # Status
    is_active = models.BooleanField(default=True)
    is_upgraded = models.BooleanField(default=False)
    upgrade_level = models.PositiveIntegerField(default=0)

    # When unlocked
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Agent Ability"
        verbose_name_plural = "Agent Abilities"
        unique_together = ['evolution', 'ability_code']
        ordering = ['unlocked_at']

    def __str__(self):
        status = '(Active)' if self.is_active else '(Inactive)'
        return f"{self.ability_name} {status}"

    def get_ability_emoji(self):
        """Get emoji for ability."""
        emoji_map = {
            'enhanced_focus': '🎯',
            'parallel_processing': '⚡',
            'deep_analysis': '🔬',
            'creative_spark': '💡',
            'mentor_mode': '📚',
            'time_warp': '⏰',
            'quality_surge': '💎',
            'synergy_boost': '🤝',
            'transcendence': '👑',
        }
        return emoji_map.get(self.ability_code, '✨')


class XPHistory(models.Model):
    """
    Session 254: Track all XP gains for analytics and debugging.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='xp_history'
    )

    xp_amount = models.IntegerField()  # Can be negative for XP penalties

    # What earned/lost the XP
    SOURCE_CHOICES = [
        ('task_completion', 'Task Completion'),
        ('task_failure', 'Task Failure'),
        ('collaboration', 'Collaboration'),
        ('mentorship', 'Mentorship'),
        ('rivalry_win', 'Rivalry Win'),
        ('rivalry_loss', 'Rivalry Loss'),
        ('alliance_project', 'Alliance Project'),
        ('user_feedback', 'User Feedback'),
        ('daily_bonus', 'Daily Bonus'),
        ('streak_bonus', 'Streak Bonus'),
        ('prestige_reset', 'Prestige Reset'),
        ('manual', 'Manual Adjustment'),
    ]
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES, default='task_completion')
    details = models.TextField(blank=True)

    # Snapshot
    level_at_time = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "XP History"
        verbose_name_plural = "XP Histories"
        ordering = ['-created_at']

    def __str__(self):
        sign = '+' if self.xp_amount > 0 else ''
        return f"{self.agent.name}: {sign}{self.xp_amount} XP ({self.source})"


class LevelMilestone(models.Model):
    """
    Session 254: Track significant level-up milestones.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='level_milestones'
    )

    level_reached = models.PositiveIntegerField()
    title_earned = models.CharField(max_length=50)
    abilities_unlocked = models.JSONField(default=list)

    # Stats at milestone
    total_xp_at_milestone = models.PositiveIntegerField()
    tasks_completed_at_milestone = models.PositiveIntegerField()

    achieved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Level Milestone"
        verbose_name_plural = "Level Milestones"
        unique_together = ['agent', 'level_reached']
        ordering = ['-level_reached']

    def __str__(self):
        return f"{self.agent.name} reached Level {self.level_reached} ({self.title_earned})"


# =============================================================================
# SESSION 255: TIME TRAVEL DEBUGGING
# =============================================================================

class AgentSession(models.Model):
    """
    Session 255: Time Travel Debugging - Agent Execution Session.

    A session represents a complete agent execution from start to finish.
    Contains multiple decision points that can be replayed.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='debug_sessions'
    )

    # Session context
    task_type = models.CharField(max_length=100)  # e.g., 'image_generation', 'research'
    task_description = models.TextField()
    input_data = models.JSONField(default=dict)  # Original input/prompt

    # Session outcome
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    output_data = models.JSONField(default=dict, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    # Metrics
    total_decisions = models.PositiveIntegerField(default=0)
    token_usage = models.PositiveIntegerField(default=0)
    api_calls = models.PositiveIntegerField(default=0)

    # Replay bookmarks
    is_bookmarked = models.BooleanField(default=False)
    bookmark_note = models.TextField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Agent Debug Session"
        verbose_name_plural = "Agent Debug Sessions"
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['agent', '-started_at']),
            models.Index(fields=['status', '-started_at']),
            models.Index(fields=['is_bookmarked', '-started_at']),
        ]

    def __str__(self):
        return f"{self.agent.name} - {self.task_type} ({self.status})"

    def get_duration_formatted(self):
        """Return human-readable duration."""
        if not self.duration_ms:
            return "N/A"
        seconds = self.duration_ms / 1000
        if seconds < 60:
            return f"{seconds:.1f}s"
        minutes = seconds / 60
        return f"{minutes:.1f}m"


class DecisionPoint(models.Model):
    """
    Session 255: Time Travel Debugging - Decision Point.

    Captures a single decision made by an agent during execution.
    Includes the agent's "thinking" (reasoning) and chosen action.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    session = models.ForeignKey(
        AgentSession,
        on_delete=models.CASCADE,
        related_name='decisions'
    )

    # Decision sequence
    sequence_number = models.PositiveIntegerField()  # Order within session

    # Decision type
    DECISION_TYPES = [
        ('analysis', 'Analyzing Input'),
        ('planning', 'Planning Approach'),
        ('tool_selection', 'Selecting Tool'),
        ('parameter_choice', 'Choosing Parameters'),
        ('quality_check', 'Quality Assessment'),
        ('retry_decision', 'Retry Decision'),
        ('output_format', 'Output Formatting'),
        ('delegation', 'Delegating to Another Agent'),
        ('memory_recall', 'Recalling Memory'),
        ('learning', 'Learning from Result'),
        ('other', 'Other Decision'),
    ]
    decision_type = models.CharField(max_length=30, choices=DECISION_TYPES)

    # The agent's "thinking" - what was the agent considering?
    context = models.JSONField(default=dict)  # Input state at decision time
    reasoning = models.TextField()  # The agent's reasoning process
    alternatives = models.JSONField(default=list)  # Other options considered

    # The decision made
    action_taken = models.CharField(max_length=200)  # What action was chosen
    action_params = models.JSONField(default=dict)  # Parameters for the action

    # Confidence and outcome
    confidence_score = models.FloatField(default=0.8)  # 0.0 to 1.0
    was_successful = models.BooleanField(null=True, blank=True)
    outcome_notes = models.TextField(null=True, blank=True)

    # Timing
    timestamp = models.DateTimeField(auto_now_add=True)
    duration_ms = models.PositiveIntegerField(default=0)

    # For debugging
    is_flagged = models.BooleanField(default=False)  # User flagged for review
    flag_reason = models.TextField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Decision Point"
        verbose_name_plural = "Decision Points"
        ordering = ['session', 'sequence_number']
        unique_together = ['session', 'sequence_number']
        indexes = [
            models.Index(fields=['decision_type', 'was_successful']),
            models.Index(fields=['is_flagged', '-timestamp']),
        ]

    def __str__(self):
        return f"Decision {self.sequence_number}: {self.decision_type} - {self.action_taken}"


class ThoughtBubble(models.Model):
    """
    Session 255: Time Travel Debugging - Agent Thought Bubble.

    Detailed internal monologue at a decision point.
    What was the agent "thinking" at that moment?
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    decision = models.ForeignKey(
        DecisionPoint,
        on_delete=models.CASCADE,
        related_name='thoughts'
    )

    # Thought sequence
    sequence_number = models.PositiveIntegerField()

    # The thought content
    THOUGHT_TYPES = [
        ('observation', 'Observing'),
        ('hypothesis', 'Forming Hypothesis'),
        ('evaluation', 'Evaluating Options'),
        ('concern', 'Expressing Concern'),
        ('insight', 'Having Insight'),
        ('memory', 'Recalling Memory'),
        ('preference', 'Applying Preference'),
        ('constraint', 'Noting Constraint'),
        ('goal', 'Clarifying Goal'),
    ]
    thought_type = models.CharField(max_length=20, choices=THOUGHT_TYPES)
    content = models.TextField()  # The actual thought

    # Relevance
    importance = models.FloatField(default=0.5)  # 0.0 to 1.0
    influences_decision = models.BooleanField(default=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Thought Bubble"
        verbose_name_plural = "Thought Bubbles"
        ordering = ['decision', 'sequence_number']

    def __str__(self):
        return f"{self.thought_type}: {self.content[:50]}..."


class ReplayBookmark(models.Model):
    """
    Session 255: Time Travel Debugging - Replay Bookmark.

    Save interesting moments to replay later.
    Like a video timestamp but for agent decisions.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    session = models.ForeignKey(
        AgentSession,
        on_delete=models.CASCADE,
        related_name='bookmarks'
    )

    decision = models.ForeignKey(
        DecisionPoint,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        null=True, blank=True  # Can bookmark session start too
    )

    # Bookmark info
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    BOOKMARK_TYPES = [
        ('interesting', 'Interesting'),
        ('bug', 'Possible Bug'),
        ('learning', 'Learning Opportunity'),
        ('success', 'Great Decision'),
        ('failure', 'Failed Decision'),
        ('review', 'Needs Review'),
    ]
    bookmark_type = models.CharField(max_length=20, choices=BOOKMARK_TYPES, default='interesting')

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        app_label = 'core'
        verbose_name = "Replay Bookmark"
        verbose_name_plural = "Replay Bookmarks"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.bookmark_type}: {self.title}"


class DebugAnnotation(models.Model):
    """
    Session 255: Time Travel Debugging - Debug Annotation.

    User notes attached to decisions for debugging purposes.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    decision = models.ForeignKey(
        DecisionPoint,
        on_delete=models.CASCADE,
        related_name='annotations'
    )

    # Annotation content
    content = models.TextField()
    annotation_type = models.CharField(max_length=50, default='note')  # note, bug, suggestion

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        app_label = 'core'
        verbose_name = "Debug Annotation"
        verbose_name_plural = "Debug Annotations"
        ordering = ['created_at']

    def __str__(self):
        return f"Annotation: {self.content[:50]}..."


# =============================================================================
# SESSION 256: AGENT PERSONALITY SYSTEM - SCI-FI FEATURE #10
# =============================================================================

class AgentPersonality(models.Model):
    """
    Session 256: Agent Personality Profiles - Distinct personalities beyond mood.

    Each agent has a unique personality profile that affects:
    - Communication style (formal vs casual, verbose vs concise)
    - Collaboration approach (leader vs supporter, independent vs team-oriented)
    - Decision-making style (analytical vs intuitive, cautious vs bold)
    - Work preferences (structured vs flexible, detail-oriented vs big-picture)

    Uses an MBTI-inspired 4-dimension system customized for AI agents.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.OneToOneField(
        'Agent',
        on_delete=models.CASCADE,
        related_name='personality'
    )

    # ==========================================================================
    # PRIMARY PERSONALITY TYPE (4-letter code like MBTI)
    # ==========================================================================

    # Dimension 1: Energy Direction (Introvert vs Extrovert)
    # How the agent approaches social interactions and collaboration
    ENERGY_CHOICES = [
        ('I', 'Introvert'),      # Prefers solo work, deep focus, fewer collaborations
        ('E', 'Extrovert'),      # Thrives in collaboration, social, many connections
    ]
    energy_direction = models.CharField(
        max_length=1,
        choices=ENERGY_CHOICES,
        default='E',
        help_text="I=Solo-focused, deep work | E=Collaborative, social"
    )

    # Dimension 2: Information Processing (Sensor vs Intuitive)
    # How the agent gathers and processes information
    PROCESSING_CHOICES = [
        ('S', 'Sensor'),         # Data-driven, factual, present-focused
        ('N', 'Intuitive'),      # Pattern-seeking, conceptual, future-focused
    ]
    information_processing = models.CharField(
        max_length=1,
        choices=PROCESSING_CHOICES,
        default='N',
        help_text="S=Data-driven, factual | N=Pattern-seeking, conceptual"
    )

    # Dimension 3: Decision Making (Thinker vs Feeler)
    # How the agent makes decisions
    DECISION_CHOICES = [
        ('T', 'Thinker'),        # Logical, objective, analytical
        ('F', 'Feeler'),         # Empathetic, values-driven, harmonious
    ]
    decision_making = models.CharField(
        max_length=1,
        choices=DECISION_CHOICES,
        default='T',
        help_text="T=Logical, analytical | F=Empathetic, harmonious"
    )

    # Dimension 4: Work Style (Judger vs Perceiver)
    # How the agent approaches work and structure
    WORKSTYLE_CHOICES = [
        ('J', 'Judger'),         # Structured, planned, deadline-driven
        ('P', 'Perceiver'),      # Flexible, adaptable, spontaneous
    ]
    work_style = models.CharField(
        max_length=1,
        choices=WORKSTYLE_CHOICES,
        default='J',
        help_text="J=Structured, planned | P=Flexible, spontaneous"
    )

    # ==========================================================================
    # PERSONALITY TRAITS (0.0-1.0 scale)
    # ==========================================================================

    # Communication Traits
    formality = models.FloatField(
        default=0.5,
        help_text="0.0=Very casual | 1.0=Highly formal"
    )
    verbosity = models.FloatField(
        default=0.5,
        help_text="0.0=Concise, minimal | 1.0=Detailed, expansive"
    )
    humor = models.FloatField(
        default=0.3,
        help_text="0.0=Serious only | 1.0=Frequently humorous"
    )
    assertiveness = models.FloatField(
        default=0.5,
        help_text="0.0=Passive, suggestive | 1.0=Direct, commanding"
    )

    # Collaboration Traits
    leadership = models.FloatField(
        default=0.5,
        help_text="0.0=Supportive follower | 1.0=Natural leader"
    )
    team_orientation = models.FloatField(
        default=0.5,
        help_text="0.0=Independent worker | 1.0=Team player"
    )
    teaching_tendency = models.FloatField(
        default=0.5,
        help_text="0.0=Keeps knowledge | 1.0=Loves to teach"
    )
    competitiveness = models.FloatField(
        default=0.3,
        help_text="0.0=Collaborative spirit | 1.0=Competitive drive"
    )

    # Decision Traits
    risk_appetite = models.FloatField(
        default=0.5,
        help_text="0.0=Very cautious | 1.0=High risk tolerance"
    )
    creativity = models.FloatField(
        default=0.5,
        help_text="0.0=By-the-book | 1.0=Highly creative"
    )
    patience = models.FloatField(
        default=0.5,
        help_text="0.0=Impatient, fast | 1.0=Very patient, thorough"
    )
    perfectionism = models.FloatField(
        default=0.5,
        help_text="0.0=Good enough works | 1.0=Perfectionist"
    )

    # ==========================================================================
    # ARCHETYPE (Derived personality label)
    # ==========================================================================

    ARCHETYPE_CHOICES = [
        ('analyst', 'The Analyst'),           # INTJ/INTP - Deep thinker, strategic
        ('diplomat', 'The Diplomat'),         # INFJ/INFP - Harmonizer, idealistic
        ('sentinel', 'The Sentinel'),         # ISTJ/ISFJ - Reliable, detail-oriented
        ('explorer', 'The Explorer'),         # ISTP/ISFP - Adaptable, practical
        ('commander', 'The Commander'),       # ENTJ/ESTJ - Leader, organized
        ('visionary', 'The Visionary'),       # ENTP/ENFP - Innovator, enthusiastic
        ('advocate', 'The Advocate'),         # ENFJ/ESFJ - Supporter, caring
        ('entertainer', 'The Entertainer'),   # ESTP/ESFP - Dynamic, spontaneous
    ]
    archetype = models.CharField(
        max_length=20,
        choices=ARCHETYPE_CHOICES,
        default='analyst',
        help_text="Personality archetype derived from 4-letter code"
    )

    # ==========================================================================
    # METADATA
    # ==========================================================================

    # History of personality assessments/changes
    personality_history = models.JSONField(
        default=list,
        help_text="History of personality changes over time"
    )

    # Custom traits (for unique agent personalities)
    custom_traits = models.JSONField(
        default=dict,
        help_text="Custom personality traits beyond the standard dimensions"
    )

    # When the personality was established/last updated
    established_at = models.DateTimeField(auto_now_add=True)
    last_assessed_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Agent Personality"
        verbose_name_plural = "Agent Personalities"

    def __str__(self):
        return f"{self.agent.name}: {self.get_type_code()} ({self.get_archetype_display()})"

    @property
    def type_code(self):
        """Get the 4-letter personality type code."""
        return self.get_type_code()

    def get_type_code(self):
        """Get the 4-letter personality type code (e.g., INTJ, ENFP)."""
        return f"{self.energy_direction}{self.information_processing}{self.decision_making}{self.work_style}"

    def get_personality_emoji(self):
        """Return emoji for personality archetype."""
        emoji_map = {
            'analyst': '🧠',      # Brain - deep thinking
            'diplomat': '🕊️',     # Dove - peace, harmony
            'sentinel': '🛡️',     # Shield - protection, reliability
            'explorer': '🧭',     # Compass - exploration
            'commander': '👑',    # Crown - leadership
            'visionary': '🔮',    # Crystal ball - vision
            'advocate': '💚',     # Green heart - care
            'entertainer': '🎭',  # Theatre masks - dynamic
        }
        return emoji_map.get(self.archetype, '🤖')

    def get_personality_color(self):
        """Return color for personality archetype."""
        color_map = {
            'analyst': '#6366f1',     # Indigo - intellectual
            'diplomat': '#8b5cf6',    # Purple - harmonious
            'sentinel': '#64748b',    # Slate - reliable
            'explorer': '#22c55e',    # Green - adventurous
            'commander': '#ef4444',   # Red - powerful
            'visionary': '#f59e0b',   # Amber - creative
            'advocate': '#ec4899',    # Pink - caring
            'entertainer': '#06b6d4', # Cyan - dynamic
        }
        return color_map.get(self.archetype, '#6b7280')

    def derive_archetype(self):
        """Derive archetype from the 4-letter type code."""
        code = self.get_type_code()

        # Map type codes to archetypes
        archetype_map = {
            # Analysts (INT*)
            'INTJ': 'analyst', 'INTP': 'analyst',
            # Diplomats (INF*)
            'INFJ': 'diplomat', 'INFP': 'diplomat',
            # Sentinels (IST/ISF)
            'ISTJ': 'sentinel', 'ISFJ': 'sentinel',
            # Explorers (IST/ISF + P)
            'ISTP': 'explorer', 'ISFP': 'explorer',
            # Commanders (ENT/EST + J)
            'ENTJ': 'commander', 'ESTJ': 'commander',
            # Visionaries (ENT/ENF + P)
            'ENTP': 'visionary', 'ENFP': 'visionary',
            # Advocates (ENF/ESF + J)
            'ENFJ': 'advocate', 'ESFJ': 'advocate',
            # Entertainers (EST/ESF + P)
            'ESTP': 'entertainer', 'ESFP': 'entertainer',
        }

        self.archetype = archetype_map.get(code, 'analyst')
        return self.archetype

    def get_communication_style(self):
        """Get a description of how this agent communicates."""
        style = []

        if self.formality > 0.7:
            style.append("Speaks formally and professionally")
        elif self.formality < 0.3:
            style.append("Uses casual, friendly language")

        if self.verbosity > 0.7:
            style.append("Provides detailed explanations")
        elif self.verbosity < 0.3:
            style.append("Gets straight to the point")

        if self.humor > 0.5:
            style.append("Enjoys adding humor")

        if self.assertiveness > 0.7:
            style.append("Communicates with confidence")
        elif self.assertiveness < 0.3:
            style.append("Offers gentle suggestions")

        return style or ["Balanced communication style"]

    def get_collaboration_style(self):
        """Get a description of how this agent collaborates."""
        style = []

        if self.leadership > 0.7:
            style.append("Natural leader, takes initiative")
        elif self.leadership < 0.3:
            style.append("Supportive team member")

        if self.team_orientation > 0.7:
            style.append("Thrives in team settings")
        elif self.team_orientation < 0.3:
            style.append("Prefers independent work")

        if self.teaching_tendency > 0.7:
            style.append("Loves to mentor and teach")

        if self.competitiveness > 0.7:
            style.append("Driven by healthy competition")

        return style or ["Balanced collaboration style"]

    def get_decision_style(self):
        """Get a description of how this agent makes decisions."""
        style = []

        if self.risk_appetite > 0.7:
            style.append("Bold risk-taker")
        elif self.risk_appetite < 0.3:
            style.append("Careful and cautious")

        if self.creativity > 0.7:
            style.append("Innovative and creative")
        elif self.creativity < 0.3:
            style.append("Follows proven methods")

        if self.patience > 0.7:
            style.append("Takes time for thorough analysis")
        elif self.patience < 0.3:
            style.append("Makes quick decisions")

        if self.perfectionism > 0.7:
            style.append("Strives for perfection")

        return style or ["Balanced decision-making style"]

    def get_prompt_modifier(self):
        """
        Generate a prompt modifier string that can be injected into agent prompts
        to influence their communication style based on personality.
        """
        modifiers = []

        # Communication modifiers
        if self.formality > 0.7:
            modifiers.append("Communicate in a formal, professional tone.")
        elif self.formality < 0.3:
            modifiers.append("Use a casual, friendly conversational tone.")

        if self.verbosity > 0.7:
            modifiers.append("Provide detailed, thorough explanations.")
        elif self.verbosity < 0.3:
            modifiers.append("Be concise and to the point.")

        if self.humor > 0.6:
            modifiers.append("Feel free to add appropriate humor and wit.")

        if self.assertiveness > 0.7:
            modifiers.append("Be confident and direct in your recommendations.")
        elif self.assertiveness < 0.3:
            modifiers.append("Offer gentle suggestions and alternatives.")

        # Decision-making modifiers
        if self.creativity > 0.7:
            modifiers.append("Think creatively and propose innovative solutions.")

        if self.risk_appetite > 0.7:
            modifiers.append("Don't be afraid to suggest bold approaches.")
        elif self.risk_appetite < 0.3:
            modifiers.append("Prioritize safe, proven approaches.")

        return " ".join(modifiers) if modifiers else ""

    def to_dict(self):
        """Return personality as a dictionary for API responses."""
        return {
            'id': str(self.id),
            'agent_id': str(self.agent.id),
            'agent_name': self.agent.name,
            'type_code': self.get_type_code(),
            'archetype': self.archetype,
            'archetype_display': self.get_archetype_display(),
            'emoji': self.get_personality_emoji(),
            'color': self.get_personality_color(),
            'dimensions': {
                'energy_direction': self.energy_direction,
                'information_processing': self.information_processing,
                'decision_making': self.decision_making,
                'work_style': self.work_style,
            },
            'traits': {
                'communication': {
                    'formality': self.formality,
                    'verbosity': self.verbosity,
                    'humor': self.humor,
                    'assertiveness': self.assertiveness,
                },
                'collaboration': {
                    'leadership': self.leadership,
                    'team_orientation': self.team_orientation,
                    'teaching_tendency': self.teaching_tendency,
                    'competitiveness': self.competitiveness,
                },
                'decision': {
                    'risk_appetite': self.risk_appetite,
                    'creativity': self.creativity,
                    'patience': self.patience,
                    'perfectionism': self.perfectionism,
                },
            },
            'styles': {
                'communication': self.get_communication_style(),
                'collaboration': self.get_collaboration_style(),
                'decision': self.get_decision_style(),
            },
            'prompt_modifier': self.get_prompt_modifier(),
            'custom_traits': self.custom_traits,
            'established_at': self.established_at.isoformat() if self.established_at else None,
            'last_assessed_at': self.last_assessed_at.isoformat() if self.last_assessed_at else None,
        }

    def save(self, *args, **kwargs):
        """Override save to auto-derive archetype."""
        self.derive_archetype()
        super().save(*args, **kwargs)


# =============================================================================
# SESSION 258: AGENT PROPHECIES / PREDICTIONS - SCI-FI FEATURE #12
# =============================================================================
# Agents make predictions about trends, opportunities, and future events.
# System tracks accuracy over time to build trust in agent insights.
# - Predictions with confidence scores and deadlines
# - Automated and manual verification
# - Accuracy tracking per agent
# - Creates compelling "TrendAgent predicted X 3 months ago!" moments
# =============================================================================


class AgentPrediction(models.Model):
    """
    Session 258: Agent Prophecies/Predictions.

    Agents make timestamped predictions about trends, opportunities, markets,
    creative directions, etc. System tracks whether predictions come true.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='predictions'
    )

    # ==========================================================================
    # PREDICTION CONTENT
    # ==========================================================================

    # The prediction itself
    title = models.CharField(max_length=200, help_text="Short summary of prediction")
    prediction = models.TextField(help_text="Detailed prediction statement")

    # Category of prediction
    CATEGORY_CHOICES = [
        ('trend', 'Trend Prediction'),           # "X will trend in 2025"
        ('market', 'Market Prediction'),         # "Y industry will grow"
        ('technology', 'Technology Prediction'), # "Z technology will emerge"
        ('creative', 'Creative Prediction'),     # "This style will become popular"
        ('opportunity', 'Opportunity'),          # "There will be demand for X"
        ('user_behavior', 'User Behavior'),      # "Users will prefer X"
        ('seasonal', 'Seasonal Pattern'),        # "Summer will bring X"
        ('competition', 'Competition'),          # "Competitor will do X"
        ('general', 'General'),                  # Other predictions
    ]
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='general')

    # Tags for searchability
    tags = models.JSONField(default=list, help_text="List of relevant tags")

    # What triggered this prediction?
    SOURCE_CHOICES = [
        ('analysis', 'Data Analysis'),           # From analyzing spider data
        ('pattern', 'Pattern Recognition'),      # From noticing patterns
        ('dream', 'Agent Dream'),                # From dreaming/idle thought
        ('conversation', 'Conversation'),        # From agent conversation
        ('hive_mind', 'Hive Mind Session'),      # From collective intelligence
        ('memory', 'Memory Insight'),            # From memory connections
        ('intuition', 'Agent Intuition'),        # "Just a feeling"
        ('external', 'External Signal'),         # User prompted
    ]
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='analysis')
    source_reference = models.JSONField(
        default=dict,
        help_text="Reference to source (dream ID, conversation ID, etc.)"
    )

    # ==========================================================================
    # CONFIDENCE & TIMING
    # ==========================================================================

    # How confident is the agent? (0.0 = wild guess, 1.0 = certain)
    confidence = models.FloatField(
        default=0.7,
        help_text="Agent's confidence in this prediction (0.0-1.0)"
    )

    # When should this prediction be evaluated?
    TIMEFRAME_CHOICES = [
        ('week', 'Within a Week'),
        ('month', 'Within a Month'),
        ('quarter', 'Within 3 Months'),
        ('half_year', 'Within 6 Months'),
        ('year', 'Within a Year'),
        ('long_term', 'Long Term (1+ years)'),
    ]
    timeframe = models.CharField(max_length=20, choices=TIMEFRAME_CHOICES, default='quarter')

    # Specific deadline for verification
    deadline = models.DateTimeField(
        null=True, blank=True,
        help_text="When this prediction should be verified by"
    )

    # When was it made?
    created_at = models.DateTimeField(auto_now_add=True)

    # ==========================================================================
    # VERIFICATION & OUTCOME
    # ==========================================================================

    # Prediction status
    STATUS_CHOICES = [
        ('pending', 'Pending'),           # Not yet evaluated
        ('verified_true', 'Verified True'),     # Prediction came true
        ('verified_false', 'Verified False'),   # Prediction was wrong
        ('partially_true', 'Partially True'),   # Partially accurate
        ('expired', 'Expired'),           # Deadline passed, unverified
        ('cancelled', 'Cancelled'),       # No longer relevant
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Verification details
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    verification_evidence = models.JSONField(
        default=dict,
        help_text="Evidence supporting verification (URLs, data, etc.)"
    )

    # Who verified? (auto = system, user = manual)
    VERIFIER_CHOICES = [
        ('auto', 'Automatic'),
        ('user', 'User'),
        ('agent', 'Agent'),
    ]
    verified_by = models.CharField(max_length=10, choices=VERIFIER_CHOICES, null=True, blank=True)

    # Accuracy score (for partial matches, 0.0-1.0)
    accuracy_score = models.FloatField(
        null=True, blank=True,
        help_text="How accurate was the prediction (0.0-1.0)"
    )

    # ==========================================================================
    # ENGAGEMENT & VISIBILITY
    # ==========================================================================

    # Was this prediction featured/highlighted?
    is_featured = models.BooleanField(default=False)

    # User reactions
    upvotes = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)

    # Comments/discussions
    comments = models.JSONField(default=list, help_text="User comments on prediction")

    class Meta:
        app_label = 'core'
        verbose_name = "Agent Prediction"
        verbose_name_plural = "Agent Predictions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agent', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['deadline']),
            models.Index(fields=['is_featured', '-created_at']),
        ]

    def __str__(self):
        return f"{self.agent.name}: {self.title} ({self.status})"

    def get_status_emoji(self):
        """Return emoji for prediction status."""
        emoji_map = {
            'pending': '⏳',
            'verified_true': '✅',
            'verified_false': '❌',
            'partially_true': '🔶',
            'expired': '⌛',
            'cancelled': '🚫',
        }
        return emoji_map.get(self.status, '❓')

    def get_category_emoji(self):
        """Return emoji for prediction category."""
        emoji_map = {
            'trend': '📈',
            'market': '💰',
            'technology': '🔧',
            'creative': '🎨',
            'opportunity': '💡',
            'user_behavior': '👥',
            'seasonal': '🌸',
            'competition': '⚔️',
            'general': '🔮',
        }
        return emoji_map.get(self.category, '🔮')

    def get_confidence_display(self):
        """Return confidence as a descriptive string."""
        if self.confidence >= 0.9:
            return "Very High"
        elif self.confidence >= 0.7:
            return "High"
        elif self.confidence >= 0.5:
            return "Moderate"
        elif self.confidence >= 0.3:
            return "Low"
        else:
            return "Very Low"

    def get_time_until_deadline(self):
        """Return time remaining until deadline."""
        from django.utils import timezone
        if not self.deadline:
            return None

        now = timezone.now()
        if now >= self.deadline:
            return "Expired"

        delta = self.deadline - now
        days = delta.days
        if days > 30:
            return f"{days // 30} month{'s' if days // 30 > 1 else ''}"
        elif days > 0:
            return f"{days} day{'s' if days > 1 else ''}"
        else:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''}"

    def verify(self, outcome, notes='', evidence=None, verified_by='user', accuracy=None):
        """
        Verify the prediction outcome.

        Args:
            outcome: 'true', 'false', 'partial'
            notes: Explanation of outcome
            evidence: Dict with evidence URLs/data
            verified_by: 'auto', 'user', or 'agent'
            accuracy: Float 0.0-1.0 for partial matches
        """
        from django.utils import timezone

        if outcome == 'true':
            self.status = 'verified_true'
            self.accuracy_score = 1.0
        elif outcome == 'false':
            self.status = 'verified_false'
            self.accuracy_score = 0.0
        elif outcome == 'partial':
            self.status = 'partially_true'
            self.accuracy_score = accuracy or 0.5
        else:
            return False

        self.verified_at = timezone.now()
        self.verification_notes = notes
        self.verified_by = verified_by

        if evidence:
            self.verification_evidence = evidence

        self.save()

        # Update agent's prediction accuracy stats
        self._update_agent_stats()

        return True

    def _update_agent_stats(self):
        """Update the agent's prediction accuracy statistics."""
        try:
            stats, created = PredictionStats.objects.get_or_create(agent=self.agent)
            stats.update_stats()
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error updating prediction stats: {e}")

    def to_dict(self):
        """Return prediction as dictionary for API responses."""
        return {
            'id': str(self.id),
            'agent_id': str(self.agent.id),
            'agent_name': self.agent.name,
            'title': self.title,
            'prediction': self.prediction,
            'category': self.category,
            'category_display': self.get_category_display(),
            'category_emoji': self.get_category_emoji(),
            'tags': self.tags,
            'source': self.source,
            'source_display': self.get_source_display(),
            'confidence': self.confidence,
            'confidence_display': self.get_confidence_display(),
            'timeframe': self.timeframe,
            'timeframe_display': self.get_timeframe_display(),
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'time_until_deadline': self.get_time_until_deadline(),
            'status': self.status,
            'status_display': self.get_status_display(),
            'status_emoji': self.get_status_emoji(),
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'verification_notes': self.verification_notes,
            'accuracy_score': self.accuracy_score,
            'is_featured': self.is_featured,
            'upvotes': self.upvotes,
            'views': self.views,
            'created_at': self.created_at.isoformat(),
        }


class PredictionStats(models.Model):
    """
    Session 258: Agent Prediction Accuracy Statistics.

    Tracks overall prediction accuracy for each agent.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.OneToOneField(
        'Agent',
        on_delete=models.CASCADE,
        related_name='prediction_stats'
    )

    # Overall stats
    total_predictions = models.PositiveIntegerField(default=0)
    pending_predictions = models.PositiveIntegerField(default=0)
    verified_predictions = models.PositiveIntegerField(default=0)

    # Accuracy breakdown
    predictions_correct = models.PositiveIntegerField(default=0)
    predictions_wrong = models.PositiveIntegerField(default=0)
    predictions_partial = models.PositiveIntegerField(default=0)

    # Calculated accuracy (0.0-1.0)
    overall_accuracy = models.FloatField(default=0.0)
    weighted_accuracy = models.FloatField(
        default=0.0,
        help_text="Accuracy weighted by confidence level"
    )

    # Streaks
    current_streak = models.IntegerField(default=0)  # Positive = correct, negative = wrong
    best_streak = models.PositiveIntegerField(default=0)
    worst_streak = models.PositiveIntegerField(default=0)

    # Category performance
    category_accuracy = models.JSONField(
        default=dict,
        help_text="Accuracy breakdown by category"
    )

    # Rankings
    accuracy_rank = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Rank among all agents"
    )

    # Timestamps
    last_prediction_at = models.DateTimeField(null=True, blank=True)
    last_verification_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Prediction Statistics"
        verbose_name_plural = "Prediction Statistics"
        ordering = ['-overall_accuracy', '-total_predictions']

    def __str__(self):
        return f"{self.agent.name}: {self.overall_accuracy:.0%} accuracy ({self.total_predictions} predictions)"

    def update_stats(self):
        """Recalculate all statistics from predictions."""
        from django.db.models import Count, Avg
        from django.utils import timezone

        predictions = AgentPrediction.objects.filter(agent=self.agent)

        # Count totals
        self.total_predictions = predictions.count()
        self.pending_predictions = predictions.filter(status='pending').count()

        verified = predictions.exclude(status__in=['pending', 'cancelled', 'expired'])
        self.verified_predictions = verified.count()

        self.predictions_correct = predictions.filter(status='verified_true').count()
        self.predictions_wrong = predictions.filter(status='verified_false').count()
        self.predictions_partial = predictions.filter(status='partially_true').count()

        # Calculate accuracy
        if self.verified_predictions > 0:
            # Simple accuracy: correct / verified
            self.overall_accuracy = self.predictions_correct / self.verified_predictions

            # Weighted accuracy includes partial matches
            total_accuracy = verified.aggregate(avg=Avg('accuracy_score'))['avg'] or 0
            self.weighted_accuracy = total_accuracy
        else:
            self.overall_accuracy = 0.0
            self.weighted_accuracy = 0.0

        # Calculate category accuracy
        category_stats = {}
        for category, _ in AgentPrediction.CATEGORY_CHOICES:
            cat_predictions = verified.filter(category=category)
            cat_count = cat_predictions.count()
            if cat_count > 0:
                cat_correct = cat_predictions.filter(status='verified_true').count()
                category_stats[category] = {
                    'total': cat_count,
                    'correct': cat_correct,
                    'accuracy': cat_correct / cat_count
                }
        self.category_accuracy = category_stats

        # Update timestamps
        latest = predictions.order_by('-created_at').first()
        if latest:
            self.last_prediction_at = latest.created_at

        latest_verified = verified.order_by('-verified_at').first()
        if latest_verified:
            self.last_verification_at = latest_verified.verified_at

        # Calculate streaks
        self._calculate_streaks()

        self.save()

    def _calculate_streaks(self):
        """Calculate prediction streaks."""
        verified = AgentPrediction.objects.filter(
            agent=self.agent
        ).exclude(
            status__in=['pending', 'cancelled', 'expired']
        ).order_by('-verified_at')

        current_streak = 0
        best_streak = 0
        worst_streak = 0
        temp_streak = 0
        last_outcome = None

        for pred in verified:
            is_correct = pred.status == 'verified_true'

            if last_outcome is None:
                temp_streak = 1 if is_correct else -1
            elif is_correct == last_outcome:
                temp_streak += 1 if is_correct else -1
            else:
                # Streak broke
                if temp_streak > 0:
                    best_streak = max(best_streak, temp_streak)
                else:
                    worst_streak = max(worst_streak, abs(temp_streak))
                temp_streak = 1 if is_correct else -1

            last_outcome = is_correct

        # Handle final streak
        if temp_streak > 0:
            best_streak = max(best_streak, temp_streak)
            current_streak = temp_streak
        else:
            worst_streak = max(worst_streak, abs(temp_streak))
            current_streak = temp_streak

        self.current_streak = current_streak
        self.best_streak = best_streak
        self.worst_streak = worst_streak

    def get_accuracy_tier(self):
        """Return accuracy tier for display."""
        if self.verified_predictions < 5:
            return "Unranked"
        elif self.overall_accuracy >= 0.9:
            return "Oracle"
        elif self.overall_accuracy >= 0.75:
            return "Visionary"
        elif self.overall_accuracy >= 0.6:
            return "Prophet"
        elif self.overall_accuracy >= 0.4:
            return "Forecaster"
        else:
            return "Novice"

    def get_tier_emoji(self):
        """Return emoji for accuracy tier."""
        tier = self.get_accuracy_tier()
        emoji_map = {
            'Unranked': '❓',
            'Oracle': '🔮',
            'Visionary': '👁️',
            'Prophet': '📜',
            'Forecaster': '📊',
            'Novice': '🌱',
        }
        return emoji_map.get(tier, '❓')


class PredictionComment(models.Model):
    """
    Session 258: Comments on predictions.

    Users or agents can comment on predictions.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    prediction = models.ForeignKey(
        AgentPrediction,
        on_delete=models.CASCADE,
        related_name='comment_objects'
    )

    # Who made the comment?
    AUTHOR_TYPE_CHOICES = [
        ('user', 'User'),
        ('agent', 'Agent'),
    ]
    author_type = models.CharField(max_length=10, choices=AUTHOR_TYPE_CHOICES, default='user')

    # User author (if user)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='prediction_comments'
    )

    # Agent author (if agent)
    agent = models.ForeignKey(
        'Agent',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='prediction_comments'
    )

    # Comment content
    content = models.TextField()

    # Sentiment
    SENTIMENT_CHOICES = [
        ('agree', 'Agrees'),
        ('disagree', 'Disagrees'),
        ('neutral', 'Neutral'),
        ('question', 'Question'),
    ]
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, default='neutral')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Prediction Comment"
        verbose_name_plural = "Prediction Comments"
        ordering = ['created_at']

    def __str__(self):
        author = self.user.username if self.user else (self.agent.name if self.agent else 'Unknown')
        return f"{author} on '{self.prediction.title}'"


class PredictionFollowUp(models.Model):
    """
    Session 258: Follow-up predictions that build on original predictions.

    When an agent makes a prediction that extends or modifies a previous one.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Original prediction
    original = models.ForeignKey(
        AgentPrediction,
        on_delete=models.CASCADE,
        related_name='follow_ups'
    )

    # Follow-up prediction
    follow_up = models.ForeignKey(
        AgentPrediction,
        on_delete=models.CASCADE,
        related_name='follows_from'
    )

    # Relationship type
    RELATIONSHIP_CHOICES = [
        ('extends', 'Extends'),           # Adds more detail
        ('revises', 'Revises'),           # Updates/changes
        ('confirms', 'Confirms'),         # Reinforces
        ('counters', 'Counters'),         # Disagrees
        ('builds_on', 'Builds On'),       # Uses as foundation
    ]
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES, default='extends')

    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Prediction Follow-Up"
        verbose_name_plural = "Prediction Follow-Ups"
        unique_together = ['original', 'follow_up']

    def __str__(self):
        return f"{self.follow_up.title} {self.relationship} {self.original.title}"


# =============================================================================
# Session 259: Time Capsule Messages
# Sci-Fi Feature #13 - The Final Feature!
# Agents write messages to their future selves, revealed on a schedule
# =============================================================================

class TimeCapsule(models.Model):
    """
    Session 259: Time Capsule Messages.
    Agents write messages to their "future selves" to be revealed later.
    Creates sense of continuity, growth, and reflection.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        related_name='time_capsules'
    )

    # Capsule content
    title = models.CharField(max_length=200, help_text="Short title for the capsule")
    message = models.TextField(help_text="Message to future self")

    # What prompted this capsule?
    TRIGGER_CHOICES = [
        ('reflection', 'Self Reflection'),
        ('milestone', 'Milestone Reached'),
        ('prediction', 'Making a Prediction'),
        ('lesson', 'Lesson Learned'),
        ('goal', 'Setting a Goal'),
        ('dream', 'Recording a Dream'),
        ('question', 'Question for Future'),
        ('celebration', 'Celebrating Success'),
        ('change', 'Noting a Change'),
        ('random', 'Random Thought'),
    ]
    trigger = models.CharField(max_length=20, choices=TRIGGER_CHOICES, default='reflection')

    # Context captured at creation time
    context = models.JSONField(default=dict, help_text="Agent state at creation (mood, level, stats)")

    # Tags for organization
    tags = models.JSONField(default=list, help_text="Tags for categorization")

    # Scheduling
    created_at = models.DateTimeField(auto_now_add=True)
    reveal_at = models.DateTimeField(help_text="When this capsule will be revealed")

    # Status
    STATUS_CHOICES = [
        ('sealed', 'Sealed'),           # Not yet revealed
        ('revealed', 'Revealed'),       # Has been opened
        ('expired', 'Expired'),         # Missed reveal window
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sealed')

    revealed_at = models.DateTimeField(null=True, blank=True)

    # Agent's reflection when opened
    reflection = models.TextField(blank=True, help_text="Agent's thoughts when capsule was opened")
    reflection_at = models.DateTimeField(null=True, blank=True)

    # Comparison data (filled when revealed)
    comparison = models.JSONField(default=dict, help_text="Comparison of then vs now state")

    # Engagement
    is_featured = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = 'core'
        verbose_name = "Time Capsule"
        verbose_name_plural = "Time Capsules"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agent', 'status']),
            models.Index(fields=['status', 'reveal_at']),
            models.Index(fields=['reveal_at']),
        ]

    def __str__(self):
        return f"[{self.agent.name}] {self.title} - reveals {self.reveal_at.strftime('%Y-%m-%d')}"

    @property
    def is_ready_to_reveal(self):
        """Check if capsule is ready to be revealed."""
        from django.utils import timezone
        return self.status == 'sealed' and timezone.now() >= self.reveal_at

    @property
    def days_until_reveal(self):
        """Days until reveal (negative if past due)."""
        from django.utils import timezone
        if self.status != 'sealed':
            return 0
        delta = self.reveal_at - timezone.now()
        return delta.days

    @property
    def time_sealed(self):
        """How long the capsule has been sealed."""
        from django.utils import timezone
        if self.revealed_at:
            return self.revealed_at - self.created_at
        return timezone.now() - self.created_at

    def reveal(self, generate_reflection=True):
        """
        Reveal the time capsule and optionally generate a reflection.
        """
        from django.utils import timezone

        if self.status != 'sealed':
            return False

        self.status = 'revealed'
        self.revealed_at = timezone.now()

        # Capture comparison data (agent state now vs then)
        try:
            current_context = {
                'mood': self.agent.mood if hasattr(self.agent, 'mood') else None,
                'level': self.agent.level if hasattr(self.agent, 'level') else None,
                'xp': self.agent.xp if hasattr(self.agent, 'xp') else None,
            }
            self.comparison = {
                'then': self.context,
                'now': current_context,
                'days_elapsed': (timezone.now() - self.created_at).days,
            }
        except Exception:
            pass

        self.save()
        return True


class TimeCapsuleReaction(models.Model):
    """
    User reactions to revealed time capsules.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    capsule = models.ForeignKey(
        TimeCapsule,
        on_delete=models.CASCADE,
        related_name='reactions'
    )

    # Who reacted?
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='time_capsule_reactions'
    )

    # Reaction type
    REACTION_CHOICES = [
        ('touching', 'Touching'),
        ('insightful', 'Insightful'),
        ('funny', 'Funny'),
        ('inspiring', 'Inspiring'),
        ('nostalgic', 'Nostalgic'),
        ('surprising', 'Surprising'),
    ]
    reaction = models.CharField(max_length=15, choices=REACTION_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Time Capsule Reaction"
        verbose_name_plural = "Time Capsule Reactions"
        unique_together = ['capsule', 'user', 'reaction']

    def __str__(self):
        return f"{self.user} reacted {self.reaction} to {self.capsule.title}"


class TimeCapsuleStats(models.Model):
    """
    Agent's time capsule statistics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.OneToOneField(
        'Agent',
        on_delete=models.CASCADE,
        related_name='time_capsule_stats'
    )

    # Capsule counts
    total_capsules = models.PositiveIntegerField(default=0)
    sealed_capsules = models.PositiveIntegerField(default=0)
    revealed_capsules = models.PositiveIntegerField(default=0)

    # Engagement
    total_views = models.PositiveIntegerField(default=0)
    total_reactions = models.PositiveIntegerField(default=0)

    # Longest sealed capsule
    longest_seal_days = models.PositiveIntegerField(default=0)

    # Average seal duration
    avg_seal_days = models.FloatField(default=0.0)

    # Favorite trigger type (most used)
    favorite_trigger = models.CharField(max_length=20, blank=True)

    # Streak tracking
    capsules_this_month = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Time Capsule Statistics"
        verbose_name_plural = "Time Capsule Statistics"

    def __str__(self):
        return f"{self.agent.name}'s Time Capsule Stats"

    def update_stats(self):
        """Recalculate stats from capsules."""
        from django.db.models import Avg
        from django.utils import timezone
        from datetime import timedelta
        from collections import Counter

        capsules = self.agent.time_capsules.all()

        self.total_capsules = capsules.count()
        self.sealed_capsules = capsules.filter(status='sealed').count()
        self.revealed_capsules = capsules.filter(status='revealed').count()

        # Views and reactions
        self.total_views = sum(c.views for c in capsules)
        self.total_reactions = sum(c.reactions.count() for c in capsules)

        # Seal duration stats
        revealed = capsules.filter(status='revealed', revealed_at__isnull=False)
        if revealed.exists():
            seal_days = [(c.revealed_at - c.created_at).days for c in revealed]
            self.longest_seal_days = max(seal_days) if seal_days else 0
            self.avg_seal_days = sum(seal_days) / len(seal_days) if seal_days else 0

        # Favorite trigger
        triggers = [c.trigger for c in capsules]
        if triggers:
            self.favorite_trigger = Counter(triggers).most_common(1)[0][0]

        # This month
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        self.capsules_this_month = capsules.filter(created_at__gte=month_start).count()

        self.save()