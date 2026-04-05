"""
Campaign Models - Marketing Campaign Orchestration
===================================================

Session 513: The hub that connects Intelligence + Agents + Delivery

A Campaign represents a complete marketing package for a client:
- Client provides: Product, target market, budget tier, brand assets
- System produces: Ad copy, images, videos, email sequences, social posts

The CampaignOrchestratorAgent uses these models to:
1. Track campaign state through Research -> Strategy -> Creation -> Delivery
2. Store deliverables as they're created
3. Learn from campaign outcomes to improve future campaigns
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class Campaign(models.Model):
    """
    A complete marketing campaign for a client.

    This is the HUB that finally connects:
    - Intelligence (spider data, web search, research)
    - Agents (creation, strategy, writing)
    - Autonomous (performance monitoring)
    - Delivery (Discord, download, client management)

    Example:
        Campaign: "Mike's Auto - Honda Civic Sale"
        - Product: 2019 Honda Civic, low miles
        - Target: Denver metro, 25-45 year olds
        - Budget: Pro ($2,000)
        - Deliverables: 5 ad copies, 10 images, 1 video, 5 emails
    """

    # Budget tiers with their included deliverables
    BUDGET_TIERS = {
        'starter': {
            'name': 'Starter',
            'price': 500,
            'includes': ['ad_copy', 'images_basic', 'social_posts'],
            'description': '5 ad variations, 5 images, 7 social posts'
        },
        'pro': {
            'name': 'Pro',
            'price': 2000,
            'includes': ['ad_copy', 'images_full', 'social_posts', 'email_sequence', 'banners'],
            'description': '10 ad variations, 15 images, 14 social posts, 5-email sequence, banner ads'
        },
        'enterprise': {
            'name': 'Enterprise',
            'price': 5000,
            'includes': ['ad_copy', 'images_full', 'social_posts', 'email_sequence', 'banners', 'video', 'voiceover'],
            'description': 'Everything in Pro + 30s video ad with voiceover'
        },
        'premium': {
            'name': 'Premium',
            'price': 10000,
            'includes': ['ad_copy', 'images_full', 'social_posts', 'email_sequence', 'banners', 'video_series', 'voiceover', 'brand_guide'],
            'description': 'Full brand package with 3 videos and brand guidelines'
        }
    }

    STATUS_CHOICES = [
        ('intake', 'Intake'),           # Gathering requirements
        ('research', 'Research'),       # Researching market/competitors
        ('strategy', 'Strategy'),       # Planning content strategy
        ('creation', 'Creation'),       # Creating deliverables
        ('review', 'Review'),           # Client review
        ('revision', 'Revision'),       # Making changes
        ('complete', 'Complete'),       # All deliverables done
        ('delivered', 'Delivered'),     # Sent to client
        ('cancelled', 'Cancelled'),     # Campaign cancelled
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Workspace linkage
    workspace = models.ForeignKey(
        'core.ProjectWorkspace', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='campaigns', db_index=True,
    )

    # Owner
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='campaigns'
    )

    # Campaign basics
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='intake')
    budget_tier = models.CharField(max_length=20, default='starter')

    # Client/Product info
    client_name = models.CharField(max_length=255, blank=True)
    product_name = models.CharField(max_length=255)
    product_description = models.TextField()
    product_features = models.JSONField(default=list, blank=True)  # Key selling points

    # Target market
    target_market = models.TextField(help_text="Who is the target audience?")
    target_location = models.CharField(max_length=255, blank=True)
    target_demographics = models.JSONField(default=dict, blank=True)  # age, income, interests

    # Competitors (for research phase)
    competitors = models.JSONField(default=list, blank=True)  # List of competitor names/URLs

    # Brand assets (if provided)
    brand_colors = models.JSONField(default=list, blank=True)  # Hex colors
    brand_fonts = models.JSONField(default=list, blank=True)
    brand_style = models.CharField(max_length=100, blank=True)  # e.g., "professional", "playful"
    logo_image_id = models.UUIDField(null=True, blank=True)  # Reference to uploaded logo

    # Distribution platforms
    platforms = models.JSONField(default=list, blank=True)  # ['facebook', 'instagram', 'craigslist', 'email']

    # Research results (populated by Research phase)
    research_data = models.JSONField(default=dict, blank=True)
    competitor_analysis = models.JSONField(default=dict, blank=True)
    market_trends = models.JSONField(default=dict, blank=True)

    # Strategy results (populated by Strategy phase)
    content_strategy = models.JSONField(default=dict, blank=True)
    brand_direction = models.JSONField(default=dict, blank=True)
    seo_keywords = models.JSONField(default=list, blank=True)

    # Progress tracking
    progress_percent = models.IntegerField(default=0)
    current_phase = models.CharField(max_length=50, default='intake')
    phase_details = models.JSONField(default=dict, blank=True)  # Detailed phase status

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    # Execution tracking
    total_api_calls = models.IntegerField(default=0)
    total_tokens_used = models.IntegerField(default=0)
    execution_log = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    def get_budget_info(self):
        """Get budget tier details."""
        return self.BUDGET_TIERS.get(self.budget_tier, self.BUDGET_TIERS['starter'])

    def get_included_deliverables(self):
        """Get list of deliverable types included in this tier."""
        return self.get_budget_info().get('includes', [])

    def update_progress(self, phase: str, percent: int, details: dict = None):
        """Update campaign progress."""
        self.current_phase = phase
        self.progress_percent = min(100, max(0, percent))
        if details:
            self.phase_details[phase] = details
        self.save(update_fields=['current_phase', 'progress_percent', 'phase_details', 'updated_at'])

    def log_execution(self, action: str, details: dict = None):
        """Add entry to execution log."""
        entry = {
            'timestamp': timezone.now().isoformat(),
            'action': action,
            'details': details or {}
        }
        self.execution_log.append(entry)
        self.save(update_fields=['execution_log', 'updated_at'])

    def start_campaign(self):
        """Mark campaign as started."""
        self.started_at = timezone.now()
        self.status = 'research'
        self.save(update_fields=['started_at', 'status', 'updated_at'])

    def complete_campaign(self):
        """Mark campaign as complete."""
        self.completed_at = timezone.now()
        self.status = 'complete'
        self.progress_percent = 100
        self.save(update_fields=['completed_at', 'status', 'progress_percent', 'updated_at'])


class CampaignDeliverable(models.Model):
    """
    A single deliverable created for a campaign.

    Types include:
    - ad_copy: Text ad variations
    - image: Generated images (hero shots, banners, etc.)
    - video: Generated video ads
    - email: Email sequence content
    - social_post: Social media posts
    - banner: Display ad banners
    - voiceover: Audio voiceover files
    """

    TYPE_CHOICES = [
        ('ad_copy', 'Ad Copy'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('email', 'Email'),
        ('social_post', 'Social Post'),
        ('banner', 'Banner Ad'),
        ('voiceover', 'Voiceover'),
        ('brand_guide', 'Brand Guide'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('creating', 'Creating'),
        ('complete', 'Complete'),
        ('failed', 'Failed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter/X'),
        ('linkedin', 'LinkedIn'),
        ('craigslist', 'Craigslist'),
        ('youtube', 'YouTube'),
        ('email', 'Email'),
        ('website', 'Website'),
        ('print', 'Print'),
        ('general', 'General'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='deliverables'
    )

    # Deliverable details
    deliverable_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='general')

    # Content
    content_text = models.TextField(blank=True)  # For ad copy, emails, social posts
    content_data = models.JSONField(default=dict, blank=True)  # Structured content

    # File references (for images, videos, audio)
    file_url = models.URLField(blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    image_history_id = models.UUIDField(null=True, blank=True)  # Link to ImageHistory
    video_id = models.UUIDField(null=True, blank=True)  # Link to video generation
    audio_id = models.UUIDField(null=True, blank=True)  # Link to audio generation

    # Dimensions (for images/banners)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)

    # Metadata
    version = models.IntegerField(default=1)
    variant = models.CharField(max_length=50, blank=True)  # e.g., "A", "B" for A/B tests
    tags = models.JSONField(default=list, blank=True)

    # Agent that created it
    created_by_agent = models.CharField(max_length=100, blank=True)
    agent_prompt = models.TextField(blank=True)  # The prompt used

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['deliverable_type', 'created_at']
        verbose_name = 'Campaign Deliverable'
        verbose_name_plural = 'Campaign Deliverables'

    def __str__(self):
        return f"{self.name} ({self.get_deliverable_type_display()})"


class CampaignResearch(models.Model):
    """
    Research findings for a campaign.

    Stores results from:
    - Web search (SmartTrendingService with fallback)
    - Spider data
    - Competitor analysis
    - Customer research
    """

    RESEARCH_TYPE_CHOICES = [
        ('market_trends', 'Market Trends'),
        ('competitor', 'Competitor Analysis'),
        ('customer', 'Customer Research'),
        ('seo', 'SEO Keywords'),
        ('pricing', 'Pricing Research'),
        ('content', 'Content Ideas'),
        ('web_search', 'Web Search Results'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='research_items'
    )

    research_type = models.CharField(max_length=30, choices=RESEARCH_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    data = models.JSONField(default=dict)

    # Source tracking
    source = models.CharField(max_length=100, blank=True)  # e.g., "web_search", "spider:techcrunch"
    source_urls = models.JSONField(default=list, blank=True)

    # Agent that performed research
    agent_name = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['research_type', '-created_at']
        verbose_name = 'Campaign Research'
        verbose_name_plural = 'Campaign Research Items'

    def __str__(self):
        return f"{self.title} ({self.get_research_type_display()})"
