"""
ATS Optimization Models - Session 866
=====================================

Models for ATS keyword optimization and persona-tailored resume templates.

Built from HiveMind brainstorm "Persona Synthesis Engine" proposal:
- PersonaResumeTemplate: Industry/role-specific resume templates
- ATSKeywordMapping: Keyword mappings and variations
- ResumeOptimizationLog: Track optimization requests and conversions
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class PersonaResumeTemplate(models.Model):
    """
    Persona-tailored resume templates for specific industries and roles.

    Each template contains:
    - Optimized section structures
    - Industry-specific keywords
    - Example bullet points
    - ATS-friendly formatting guidelines
    """

    TEMPLATE_TYPE_CHOICES = [
        ('free_guide', 'Free Guide'),
        ('paid_basic', 'Paid Basic ($79)'),
        ('paid_premium', 'Paid Premium ($149)'),
        ('paid_executive', 'Paid Executive ($249)'),
    ]

    INDUSTRY_CHOICES = [
        ('tech', 'Technology'),
        ('fintech', 'Fintech'),
        ('healthcare', 'Healthcare'),
        ('ecommerce', 'E-commerce'),
        ('saas', 'SaaS'),
        ('ai_ml', 'AI/ML'),
        ('consulting', 'Consulting'),
        ('marketing', 'Marketing'),
        ('sales', 'Sales'),
        ('general', 'General'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('entry', 'Entry Level (0-2 years)'),
        ('mid', 'Mid Level (3-5 years)'),
        ('senior', 'Senior (6-10 years)'),
        ('lead', 'Lead/Principal (10+ years)'),
        ('executive', 'Executive'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Template identification
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    # Targeting
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, default='tech')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default='mid')
    target_roles = models.JSONField(
        default=list,
        help_text="List of role titles this template is optimized for"
    )

    # Template content
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPE_CHOICES, default='free_guide')
    price_cents = models.IntegerField(default=0, help_text="Price in cents (0 for free)")

    # Structure
    sections = models.JSONField(
        default=list,
        help_text="Ordered list of resume sections with guidelines"
    )
    # Example: [{"name": "Summary", "required": true, "guidelines": "..."}, ...]

    # Keywords
    required_keywords = models.JSONField(
        default=list,
        help_text="Keywords that should appear in resumes using this template"
    )
    recommended_keywords = models.JSONField(
        default=list,
        help_text="Keywords that are good to include"
    )
    action_verbs = models.JSONField(
        default=list,
        help_text="Recommended action verbs for bullet points"
    )

    # Example content
    example_summary = models.TextField(blank=True, help_text="Example professional summary")
    example_bullets = models.JSONField(
        default=list,
        help_text="Example bullet points for experience section"
    )

    # Formatting guidelines
    formatting_guidelines = models.JSONField(
        default=dict,
        help_text="ATS-friendly formatting rules"
    )

    # Analytics
    downloads = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0, help_text="Number of users who got interviews")
    avg_ats_score_improvement = models.FloatField(default=0)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = 'core'
        ordering = ['industry', 'experience_level', 'name']
        verbose_name = 'Persona Resume Template'
        verbose_name_plural = 'Persona Resume Templates'

    def __str__(self):
        return f"{self.name} ({self.industry}/{self.experience_level})"

    def get_price_display(self) -> str:
        """Get formatted price string."""
        if self.price_cents == 0:
            return "Free"
        return f"${self.price_cents / 100:.0f}"


class ATSKeywordMapping(models.Model):
    """
    Store canonical keyword mappings and variations.

    This allows the system to learn from successful resumes
    which keyword variations perform best with ATS systems.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Canonical keyword
    canonical = models.CharField(max_length=100, unique=True, db_index=True)

    # Variations that map to this keyword
    variations = models.JSONField(
        default=list,
        help_text="List of variations that should be normalized to canonical"
    )

    # Categorization
    category = models.CharField(
        max_length=50,
        choices=[
            ('technical_skill', 'Technical Skill'),
            ('soft_skill', 'Soft Skill'),
            ('certification', 'Certification'),
            ('tool', 'Tool/Software'),
            ('methodology', 'Methodology'),
            ('industry_term', 'Industry Term'),
        ],
        default='technical_skill'
    )

    # Industry relevance (which industries value this keyword)
    industries = models.JSONField(
        default=list,
        help_text="Industries where this keyword is particularly valuable"
    )

    # Performance metrics
    resume_frequency = models.IntegerField(default=0, help_text="How often this appears in resumes")
    job_frequency = models.IntegerField(default=0, help_text="How often this appears in job descriptions")
    interview_correlation = models.FloatField(
        default=0,
        help_text="Correlation with getting interviews (0-1)"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        ordering = ['-job_frequency', 'canonical']
        verbose_name = 'ATS Keyword Mapping'
        verbose_name_plural = 'ATS Keyword Mappings'

    def __str__(self):
        return f"{self.canonical} ({len(self.variations)} variations)"


class ResumeOptimizationLog(models.Model):
    """
    Track resume optimization requests and outcomes for conversion tracking.

    Tracks the funnel: signup → optimization → download → rewrite → interview
    """

    STAGE_CHOICES = [
        ('signup', 'Signed Up'),
        ('analyzed', 'Resume Analyzed'),
        ('downloaded_free', 'Downloaded Free Guide'),
        ('purchased_basic', 'Purchased Basic Rewrite'),
        ('purchased_premium', 'Purchased Premium Rewrite'),
        ('purchased_executive', 'Purchased Executive Rewrite'),
        ('resume_delivered', 'Rewrite Delivered'),
        ('applied', 'Applied to Jobs'),
        ('interview', 'Got Interview'),
        ('offer', 'Received Offer'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # User tracking (can be anonymous)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resume_optimizations'
    )
    session_id = models.CharField(max_length=100, blank=True, db_index=True)

    # What was analyzed
    job_title_target = models.CharField(max_length=200, blank=True)
    industry = models.CharField(max_length=50, blank=True)
    experience_level = models.CharField(max_length=20, blank=True)

    # Scores
    initial_ats_score = models.FloatField(null=True, blank=True)
    final_ats_score = models.FloatField(null=True, blank=True)

    # Keywords
    missing_keywords_count = models.IntegerField(default=0)
    keywords_added = models.JSONField(default=list)

    # Template used
    template = models.ForeignKey(
        PersonaResumeTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='optimization_logs'
    )

    # Conversion tracking
    current_stage = models.CharField(max_length=30, choices=STAGE_CHOICES, default='signup')
    stage_timestamps = models.JSONField(
        default=dict,
        help_text="Timestamp for each stage reached"
    )

    # Revenue
    revenue_cents = models.IntegerField(default=0)

    # A/B test tracking
    ab_test_variant = models.CharField(max_length=50, blank=True, db_index=True)

    # Source tracking
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        verbose_name = 'Resume Optimization Log'
        verbose_name_plural = 'Resume Optimization Logs'
        indexes = [
            models.Index(fields=['current_stage', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['ab_test_variant', 'current_stage']),
        ]

    def __str__(self):
        user_str = self.user.username if self.user else f"Anonymous ({self.session_id[:8]})"
        return f"{user_str}: {self.current_stage} ({self.created_at.date()})"

    def advance_stage(self, new_stage: str) -> bool:
        """
        Advance to a new stage in the funnel.

        Returns True if stage was advanced, False if invalid transition.
        """
        stage_order = [s[0] for s in self.STAGE_CHOICES]
        current_index = stage_order.index(self.current_stage)
        new_index = stage_order.index(new_stage)

        if new_index > current_index:
            self.current_stage = new_stage
            self.stage_timestamps[new_stage] = timezone.now().isoformat()
            self.save(update_fields=['current_stage', 'stage_timestamps', 'updated_at'])
            return True
        return False

    @property
    def conversion_value(self) -> str:
        """Get the conversion value category."""
        if self.current_stage in ['offer']:
            return 'high_value'
        elif self.current_stage in ['interview', 'applied']:
            return 'medium_value'
        elif self.current_stage in ['purchased_basic', 'purchased_premium', 'purchased_executive']:
            return 'paid'
        elif self.current_stage in ['downloaded_free']:
            return 'lead'
        return 'prospect'

    @property
    def score_improvement(self) -> float:
        """Calculate ATS score improvement."""
        if self.initial_ats_score and self.final_ats_score:
            return self.final_ats_score - self.initial_ats_score
        return 0


class ResumeRewriteOrder(models.Model):
    """
    Track paid resume rewrite orders.

    This model handles the paid rewrite product:
    - Free guide (lead magnet)
    - Basic rewrite ($79)
    - Premium rewrite ($149)
    - Executive rewrite ($249)
    """

    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('in_progress', 'In Progress'),
        ('review', 'Ready for Review'),
        ('revision', 'Revision Requested'),
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
    ]

    PRODUCT_CHOICES = [
        ('free_guide', 'Free Guide', 0),
        ('basic', 'Basic Rewrite', 7900),
        ('premium', 'Premium Rewrite', 14900),
        ('executive', 'Executive Rewrite', 24900),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resume_rewrite_orders'
    )

    # Product
    product = models.CharField(max_length=20, choices=[(p[0], p[1]) for p in PRODUCT_CHOICES])
    price_cents = models.IntegerField()

    # Order status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Input materials
    original_resume = models.ForeignKey(
        'ResumeVersion',
        on_delete=models.SET_NULL,
        null=True,
        related_name='rewrite_orders'
    )
    target_job_description = models.TextField(blank=True)
    target_industry = models.CharField(max_length=50, blank=True)
    additional_notes = models.TextField(blank=True)

    # Output
    rewritten_resume = models.ForeignKey(
        'ResumeVersion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='source_orders'
    )

    # Scoring
    before_ats_score = models.FloatField(null=True, blank=True)
    after_ats_score = models.FloatField(null=True, blank=True)

    # Payment
    payment_intent_id = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    # Delivery
    delivered_at = models.DateTimeField(null=True, blank=True)
    revision_count = models.IntegerField(default=0)

    # Outcome tracking
    optimization_log = models.OneToOneField(
        ResumeOptimizationLog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rewrite_order'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        verbose_name = 'Resume Rewrite Order'
        verbose_name_plural = 'Resume Rewrite Orders'

    def __str__(self):
        return f"{self.user.username}: {self.product} ({self.status})"

    @property
    def score_improvement(self) -> float:
        """Calculate ATS score improvement."""
        if self.before_ats_score and self.after_ats_score:
            return self.after_ats_score - self.before_ats_score
        return 0

    def mark_paid(self, payment_intent_id: str = ''):
        """Mark order as paid."""
        self.status = 'paid'
        self.payment_intent_id = payment_intent_id
        self.paid_at = timezone.now()
        self.save(update_fields=['status', 'payment_intent_id', 'paid_at', 'updated_at'])

        # Update optimization log
        if self.optimization_log:
            stage_map = {
                'basic': 'purchased_basic',
                'premium': 'purchased_premium',
                'executive': 'purchased_executive',
            }
            if self.product in stage_map:
                self.optimization_log.advance_stage(stage_map[self.product])
                self.optimization_log.revenue_cents = self.price_cents
                self.optimization_log.save(update_fields=['revenue_cents'])

    def mark_delivered(self, rewritten_resume):
        """Mark order as delivered."""
        self.status = 'completed'
        self.rewritten_resume = rewritten_resume
        self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'rewritten_resume', 'delivered_at', 'updated_at'])

        # Update optimization log
        if self.optimization_log:
            self.optimization_log.advance_stage('resume_delivered')
            if self.after_ats_score:
                self.optimization_log.final_ats_score = self.after_ats_score
                self.optimization_log.save(update_fields=['final_ats_score'])
