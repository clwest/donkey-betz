"""
Autonomous Situations Models - Session 479

14 New Tier 1 Autonomous Situations:

CREATIVE & CONTENT:
1. Trend-Driven Design System - Auto-updates brand styles from design trends
2. Viral Content Predictor - Scores content ideas by viral potential
3. Thumbnail A/B Optimizer - Auto-generates and tests thumbnails

INCOME & OPPORTUNITIES:
4. Job Match Intelligence - Monitors jobs, scores matches to profile
5. Freelance Opportunity Scout - Tracks freelance gigs
6. Side Hustle Detector - Finds trending micro-opportunities

FINANCIAL INTELLIGENCE:
7. SEC Filing Analyzer - Deep analysis of institutional filings
8. Crypto Sentiment Monitor - Tracks crypto social sentiment
9. Earnings Surprise Predictor - Pre-earnings analysis

RESEARCH & LEARNING:
10. Tech Stack Evolution Tracker - Monitors rising/falling technologies
11. AI Model Release Monitor - Alerts on new AI models
12. Course & Skill Gap Analyzer - Matches skills to courses

LEGAL INTELLIGENCE:
13. Case Law Monitor - Tracks relevant case decisions
14. Regulatory Change Detector - Monitors regulatory changes
"""

__all__ = [
    # Creative & Content
    'DesignTrendCategory',
    'DesignTrend',
    'DesignSystemUpdate',
    'ViralContentPrediction',
    'ThumbnailVariant',
    # Income & Opportunities
    'JobMatchProfile',
    'JobMatch',
    'FreelanceOpportunity',
    'SideHustle',
    # Financial Intelligence
    'SECFilingAnalysis',
    'CryptoSentiment',
    'EarningsPrediction',
    # Research & Learning
    'TechStackTrend',
    'AIModelRelease',
    'SkillGapAnalysis',
    # Legal Intelligence
    'CaseLawUpdate',
    'RegulatoryChange',
    # Monitoring
    'AutonomousSituationSession',
]

import uuid
from django.conf import settings
from django.db import models


# =============================================================================
# CREATIVE & CONTENT SITUATIONS
# =============================================================================

class DesignTrendCategory(models.TextChoices):
    """Categories for design trends."""
    COLOR = 'color', 'Color Palette'
    TYPOGRAPHY = 'typography', 'Typography'
    LAYOUT = 'layout', 'Layout Pattern'
    ILLUSTRATION = 'illustration', 'Illustration Style'
    ANIMATION = 'animation', 'Animation/Motion'
    UI_PATTERN = 'ui_pattern', 'UI Pattern'
    BRAND_STYLE = 'brand_style', 'Brand Style'


class DesignTrend(models.Model):
    """
    Situation #6: Trend-Driven Design System
    Tracks design trends extracted from Dribbble, Behance, Awwwards.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Trend identification
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=DesignTrendCategory.choices)
    description = models.TextField(blank=True)

    # Trend data
    colors = models.JSONField(default=list, help_text="List of hex colors")
    fonts = models.JSONField(default=list, help_text="List of font names")
    keywords = models.JSONField(default=list, help_text="Associated keywords")
    example_urls = models.JSONField(default=list, help_text="Example design URLs")

    # Scoring
    popularity_score = models.FloatField(default=0.0)
    momentum_score = models.FloatField(default=0.0)  # Rising or falling
    confidence_score = models.FloatField(default=0.0)

    # Sources
    source_spiders = models.JSONField(default=list)  # Which spiders contributed
    spider_data_ids = models.JSONField(default=list)  # Referenced spider data

    # Timestamps
    first_detected = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    peak_date = models.DateTimeField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_rising = models.BooleanField(default=True)

    class Meta:
        db_table = 'design_trend'
        ordering = ['-popularity_score', '-momentum_score']

    def __str__(self):
        return f"{self.name} ({self.category})"


class DesignSystemUpdate(models.Model):
    """
    Records updates to the design system based on trends.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # What was updated
    update_type = models.CharField(max_length=50, choices=[
        ('color_palette', 'Color Palette'),
        ('typography', 'Typography'),
        ('component_style', 'Component Style'),
        ('animation', 'Animation'),
        ('full_refresh', 'Full Refresh'),
    ])

    # The changes
    previous_values = models.JSONField(default=dict)
    new_values = models.JSONField(default=dict)

    # Source trends
    source_trends = models.ManyToManyField(DesignTrend, related_name='system_updates')

    # Impact tracking
    applied = models.BooleanField(default=False)
    applied_at = models.DateTimeField(null=True, blank=True)
    user_feedback = models.CharField(max_length=20, null=True, blank=True, choices=[
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ])

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'design_system_update'
        ordering = ['-created_at']


class ViralContentPrediction(models.Model):
    """
    Situation #7: Viral Content Predictor
    Scores content ideas by viral potential.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Content info
    title = models.CharField(max_length=500)
    content_type = models.CharField(max_length=50, choices=[
        ('article', 'Article'),
        ('video', 'Video'),
        ('image', 'Image'),
        ('thread', 'Thread/Post'),
        ('meme', 'Meme'),
    ])
    topic = models.CharField(max_length=200)
    keywords = models.JSONField(default=list)

    # Viral scoring
    viral_score = models.FloatField(default=0.0)  # 0-100
    engagement_potential = models.FloatField(default=0.0)
    shareability_score = models.FloatField(default=0.0)
    timing_score = models.FloatField(default=0.0)  # Is timing right?

    # Factors
    trend_alignment = models.FloatField(default=0.0)  # Aligns with current trends
    emotional_trigger = models.CharField(max_length=50, null=True, blank=True)
    controversy_level = models.FloatField(default=0.0)  # 0-1

    # Sources used for prediction
    similar_viral_content = models.JSONField(default=list)  # URLs of similar viral content
    spider_signals = models.JSONField(default=dict)  # Spider data that informed prediction

    # Recommendation
    recommended_platforms = models.JSONField(default=list)
    optimal_posting_time = models.DateTimeField(null=True, blank=True)
    suggested_hashtags = models.JSONField(default=list)

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    prediction_expires = models.DateTimeField(null=True, blank=True)

    # Outcome (if content was created)
    content_created = models.BooleanField(default=False)
    actual_engagement = models.JSONField(null=True, blank=True)
    prediction_accuracy = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'viral_content_prediction'
        ordering = ['-viral_score', '-created_at']


class ThumbnailVariant(models.Model):
    """
    Situation #8: Thumbnail A/B Optimizer
    Tracks thumbnail variants and their performance.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Parent content
    content_title = models.CharField(max_length=500)
    content_url = models.URLField(null=True, blank=True)

    # Variant info
    variant_name = models.CharField(max_length=100)  # A, B, C, etc.
    image_url = models.URLField(null=True, blank=True)
    image_path = models.CharField(max_length=500, null=True, blank=True)

    # Design attributes
    primary_color = models.CharField(max_length=20, null=True, blank=True)
    has_face = models.BooleanField(default=False)
    has_text = models.BooleanField(default=False)
    text_content = models.CharField(max_length=200, null=True, blank=True)
    style = models.CharField(max_length=50, null=True, blank=True)

    # Performance metrics
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    ctr = models.FloatField(default=0.0)  # Click-through rate

    # A/B test info
    is_control = models.BooleanField(default=False)
    is_winner = models.BooleanField(default=False)
    test_started = models.DateTimeField(null=True, blank=True)
    test_ended = models.DateTimeField(null=True, blank=True)

    # Learning
    learned_insights = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'thumbnail_variant'
        ordering = ['-ctr', '-clicks']


# =============================================================================
# INCOME & OPPORTUNITIES SITUATIONS
# =============================================================================

class JobMatchProfile(models.Model):
    """
    User profile for job matching.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )  # Session 484: Fixed to use AUTH_USER_MODEL instead of 'auth.User'

    # Skills & experience
    skills = models.JSONField(default=list)
    experience_years = models.IntegerField(default=0)
    preferred_roles = models.JSONField(default=list)
    industries = models.JSONField(default=list)

    # Preferences
    remote_only = models.BooleanField(default=True)
    min_salary = models.IntegerField(null=True, blank=True)
    max_commute_miles = models.IntegerField(null=True, blank=True)
    preferred_company_sizes = models.JSONField(default=list)

    # Location
    location = models.CharField(max_length=200, null=True, blank=True)
    willing_to_relocate = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_match_profile'


class JobMatch(models.Model):
    """
    Situation #9: Job Match Intelligence
    Scored job matches based on user profile.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Job info
    title = models.CharField(max_length=500)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200, null=True, blank=True)
    is_remote = models.BooleanField(default=False)
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    job_url = models.URLField()

    # Source
    source_spider = models.CharField(max_length=100)
    spider_data_id = models.UUIDField(null=True, blank=True)

    # Match scoring
    overall_match_score = models.FloatField(default=0.0)  # 0-100
    skills_match = models.FloatField(default=0.0)
    experience_match = models.FloatField(default=0.0)
    salary_match = models.FloatField(default=0.0)
    location_match = models.FloatField(default=0.0)
    culture_match = models.FloatField(default=0.0)

    # Match details
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    match_reasons = models.JSONField(default=list)
    concerns = models.JSONField(default=list)

    # User interaction
    profile = models.ForeignKey(JobMatchProfile, on_delete=models.CASCADE, null=True, blank=True)
    viewed = models.BooleanField(default=False)
    saved = models.BooleanField(default=False)
    applied = models.BooleanField(default=False)
    dismissed = models.BooleanField(default=False)

    # Alerts
    alert_sent = models.BooleanField(default=False)
    alert_sent_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    posted_date = models.DateTimeField(null=True, blank=True)
    discovered_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'job_match'
        ordering = ['-overall_match_score', '-discovered_at']


class FreelanceOpportunity(models.Model):
    """
    Situation #10: Freelance Opportunity Scout
    Tracked freelance gigs and opportunities.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Gig info
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    client_name = models.CharField(max_length=200, null=True, blank=True)
    platform = models.CharField(max_length=100)  # upwork, freelancer, fiverr, etc.
    gig_url = models.URLField()

    # Budget
    budget_type = models.CharField(max_length=20, choices=[
        ('fixed', 'Fixed Price'),
        ('hourly', 'Hourly'),
        ('negotiable', 'Negotiable'),
    ])
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Requirements
    required_skills = models.JSONField(default=list)
    experience_level = models.CharField(max_length=50, null=True, blank=True)
    estimated_duration = models.CharField(max_length=100, null=True, blank=True)

    # Scoring
    opportunity_score = models.FloatField(default=0.0)
    pay_rate_score = models.FloatField(default=0.0)
    skill_match_score = models.FloatField(default=0.0)
    competition_score = models.FloatField(default=0.0)  # Lower competition = higher score

    # Competition analysis
    proposals_count = models.IntegerField(null=True, blank=True)
    avg_competitor_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Source
    source_spider = models.CharField(max_length=100)
    spider_data_id = models.UUIDField(null=True, blank=True)

    # Timestamps
    posted_date = models.DateTimeField(null=True, blank=True)
    discovered_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'freelance_opportunity'
        ordering = ['-opportunity_score', '-discovered_at']


class SideHustle(models.Model):
    """
    Situation #11: Side Hustle Detector
    Trending micro-opportunity detection.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Hustle info
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, choices=[
        ('dropshipping', 'Dropshipping'),
        ('print_on_demand', 'Print on Demand'),
        ('digital_products', 'Digital Products'),
        ('affiliate', 'Affiliate Marketing'),
        ('content_creation', 'Content Creation'),
        ('services', 'Services'),
        ('arbitrage', 'Arbitrage'),
        ('saas', 'SaaS/Software'),
        ('other', 'Other'),
    ])
    description = models.TextField()

    # Opportunity analysis
    trend_score = models.FloatField(default=0.0)  # How trending is this
    difficulty_score = models.FloatField(default=0.0)  # 0=easy, 100=hard
    startup_cost_estimate = models.CharField(max_length=100, null=True, blank=True)
    income_potential = models.CharField(max_length=100, null=True, blank=True)
    time_to_first_dollar = models.CharField(max_length=100, null=True, blank=True)

    # Evidence
    success_stories = models.JSONField(default=list)  # URLs to success stories
    reddit_discussions = models.JSONField(default=list)
    market_size_signals = models.JSONField(default=dict)

    # Requirements
    required_skills = models.JSONField(default=list)
    required_tools = models.JSONField(default=list)

    # Risks
    saturation_level = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('oversaturated', 'Oversaturated'),
    ], default='medium')
    risks = models.JSONField(default=list)

    # Source
    source_spiders = models.JSONField(default=list)
    spider_data_ids = models.JSONField(default=list)

    # Timestamps
    first_detected = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'side_hustle'
        ordering = ['-trend_score', '-first_detected']


# =============================================================================
# FINANCIAL INTELLIGENCE SITUATIONS
# =============================================================================

class SECFilingAnalysis(models.Model):
    """
    Situation #12: SEC Filing Analyzer
    Deep analysis of SEC filings.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Filing info
    company_name = models.CharField(max_length=200)
    ticker = models.CharField(max_length=20, null=True, blank=True)
    cik = models.CharField(max_length=20, null=True, blank=True)
    form_type = models.CharField(max_length=20)  # 13F, 13D, 8-K, 10-K, etc.
    filing_date = models.DateField()
    filing_url = models.URLField()

    # Analysis
    summary = models.TextField()
    key_findings = models.JSONField(default=list)
    sentiment = models.CharField(max_length=20, choices=[
        ('bullish', 'Bullish'),
        ('bearish', 'Bearish'),
        ('neutral', 'Neutral'),
    ])
    significance_score = models.FloatField(default=0.0)  # How important is this filing

    # For 13F filings (institutional holdings)
    position_changes = models.JSONField(default=list)  # New positions, exits, increases
    notable_moves = models.JSONField(default=list)  # Significant position changes

    # For 8-K filings (material events)
    event_type = models.CharField(max_length=100, null=True, blank=True)
    material_impact = models.BooleanField(default=False)

    # Market impact
    price_before = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_after = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    volume_change_percent = models.FloatField(null=True, blank=True)

    # Alert
    alert_sent = models.BooleanField(default=False)
    alert_sent_at = models.DateTimeField(null=True, blank=True)

    # Source
    spider_data_id = models.UUIDField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sec_filing_analysis'
        ordering = ['-filing_date', '-significance_score']


class CryptoSentiment(models.Model):
    """
    Situation #13: Crypto Sentiment Monitor
    Tracks sentiment across crypto communities.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Asset info
    symbol = models.CharField(max_length=20)
    name = models.CharField(max_length=100)

    # Sentiment scores
    overall_sentiment = models.FloatField(default=0.0)  # -100 to 100
    reddit_sentiment = models.FloatField(null=True, blank=True)
    twitter_sentiment = models.FloatField(null=True, blank=True)
    news_sentiment = models.FloatField(null=True, blank=True)

    # Volume metrics
    social_volume = models.IntegerField(default=0)  # Total mentions
    social_volume_change = models.FloatField(null=True, blank=True)  # % change

    # Key signals
    trending_topics = models.JSONField(default=list)
    influencer_mentions = models.JSONField(default=list)
    fear_greed_index = models.IntegerField(null=True, blank=True)

    # Notable content
    bullish_posts = models.JSONField(default=list)
    bearish_posts = models.JSONField(default=list)

    # Price context
    price_at_measurement = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    price_change_24h = models.FloatField(null=True, blank=True)

    # Alert thresholds
    sentiment_alert_triggered = models.BooleanField(default=False)
    volume_alert_triggered = models.BooleanField(default=False)

    # Source
    source_spiders = models.JSONField(default=list)
    spider_data_ids = models.JSONField(default=list)

    # Timestamps
    measured_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'crypto_sentiment'
        ordering = ['-measured_at']


class EarningsPrediction(models.Model):
    """
    Situation #14: Earnings Surprise Predictor
    Pre-earnings analysis with predictions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Company info
    company_name = models.CharField(max_length=200)
    ticker = models.CharField(max_length=20)
    sector = models.CharField(max_length=100, null=True, blank=True)

    # Earnings info
    earnings_date = models.DateField()
    earnings_time = models.CharField(max_length=20, null=True, blank=True)  # before_market, after_market

    # Consensus estimates
    eps_estimate = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    revenue_estimate = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)

    # Our prediction
    predicted_surprise = models.CharField(max_length=20, choices=[
        ('beat', 'Will Beat'),
        ('miss', 'Will Miss'),
        ('inline', 'In Line'),
    ])
    confidence_score = models.FloatField(default=0.0)

    # Bull/Bear debate
    bull_case = models.TextField(blank=True)
    bear_case = models.TextField(blank=True)
    bull_confidence = models.FloatField(default=0.0)
    bear_confidence = models.FloatField(default=0.0)

    # Signals used
    insider_activity = models.JSONField(default=dict)
    options_flow = models.JSONField(default=dict)
    analyst_revisions = models.JSONField(default=list)
    sector_performance = models.JSONField(default=dict)

    # Pre-earnings price action
    price_5d_before = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    implied_move = models.FloatField(null=True, blank=True)  # Options implied move %

    # Actual results (filled after earnings)
    actual_eps = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    actual_revenue = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    actual_surprise = models.CharField(max_length=20, null=True, blank=True)
    prediction_correct = models.BooleanField(null=True)

    # Source
    spider_data_ids = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'earnings_prediction'
        ordering = ['earnings_date', '-confidence_score']


# =============================================================================
# RESEARCH & LEARNING SITUATIONS
# =============================================================================

class TechStackTrend(models.Model):
    """
    Situation #15: Tech Stack Evolution Tracker
    Monitors rising/falling technologies.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Technology info
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, choices=[
        ('language', 'Programming Language'),
        ('framework', 'Framework'),
        ('library', 'Library'),
        ('database', 'Database'),
        ('devops', 'DevOps/Infrastructure'),
        ('cloud', 'Cloud Service'),
        ('ai_ml', 'AI/ML Tool'),
        ('other', 'Other'),
    ])
    description = models.TextField(blank=True)

    # Trend metrics
    popularity_score = models.FloatField(default=0.0)
    momentum_score = models.FloatField(default=0.0)  # Positive = rising, negative = falling
    job_demand_score = models.FloatField(default=0.0)

    # Historical data
    github_stars = models.IntegerField(null=True, blank=True)
    github_stars_growth = models.FloatField(null=True, blank=True)
    npm_downloads = models.IntegerField(null=True, blank=True)
    stackoverflow_questions = models.IntegerField(null=True, blank=True)

    # Job market signals
    job_postings_count = models.IntegerField(null=True, blank=True)
    avg_salary = models.IntegerField(null=True, blank=True)

    # Community signals
    hackernews_mentions = models.IntegerField(null=True, blank=True)
    reddit_mentions = models.IntegerField(null=True, blank=True)

    # Status
    trend_direction = models.CharField(max_length=20, choices=[
        ('rising_fast', 'Rising Fast'),
        ('rising', 'Rising'),
        ('stable', 'Stable'),
        ('declining', 'Declining'),
        ('declining_fast', 'Declining Fast'),
    ])

    # Recommendations
    should_learn = models.BooleanField(default=False)
    learning_resources = models.JSONField(default=list)

    # Source
    source_spiders = models.JSONField(default=list)
    spider_data_ids = models.JSONField(default=list)

    # Timestamps
    first_tracked = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tech_stack_trend'
        ordering = ['-momentum_score', '-popularity_score']


class AIModelRelease(models.Model):
    """
    Situation #16: AI Model Release Monitor
    Tracks new AI model releases.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Model info
    name = models.CharField(max_length=200)
    organization = models.CharField(max_length=200)
    model_type = models.CharField(max_length=100, choices=[
        ('llm', 'Large Language Model'),
        ('image', 'Image Generation'),
        ('video', 'Video Generation'),
        ('audio', 'Audio/Speech'),
        ('multimodal', 'Multimodal'),
        ('embedding', 'Embedding Model'),
        ('code', 'Code Generation'),
        ('other', 'Other'),
    ])

    # Release info
    release_date = models.DateField()
    version = models.CharField(max_length=50, null=True, blank=True)
    is_open_source = models.BooleanField(default=False)
    license_type = models.CharField(max_length=100, null=True, blank=True)

    # Links
    announcement_url = models.URLField(null=True, blank=True)
    paper_url = models.URLField(null=True, blank=True)
    model_url = models.URLField(null=True, blank=True)  # HuggingFace, etc.
    api_url = models.URLField(null=True, blank=True)

    # Capabilities
    capabilities = models.JSONField(default=list)
    benchmark_scores = models.JSONField(default=dict)
    context_length = models.IntegerField(null=True, blank=True)

    # Analysis
    significance_score = models.FloatField(default=0.0)
    innovation_notes = models.TextField(blank=True)
    use_cases = models.JSONField(default=list)
    limitations = models.JSONField(default=list)

    # Comparison to existing
    compared_to = models.JSONField(default=list)  # Other model names
    improvements = models.JSONField(default=list)

    # Alert
    alert_sent = models.BooleanField(default=False)
    alert_sent_at = models.DateTimeField(null=True, blank=True)

    # Source
    source_spiders = models.JSONField(default=list)
    spider_data_ids = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_model_release'
        ordering = ['-release_date', '-significance_score']


class SkillGapAnalysis(models.Model):
    """
    Situation #17: Course & Skill Gap Analyzer
    Matches trending skills to available courses.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Skill info
    skill_name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)

    # Market demand
    demand_score = models.FloatField(default=0.0)
    demand_trend = models.CharField(max_length=20, choices=[
        ('rising_fast', 'Rising Fast'),
        ('rising', 'Rising'),
        ('stable', 'Stable'),
        ('declining', 'Declining'),
    ])
    job_count = models.IntegerField(null=True, blank=True)
    avg_salary_premium = models.FloatField(null=True, blank=True)  # % above average

    # User's current level (if profile exists)
    user_current_level = models.CharField(max_length=20, null=True, blank=True, choices=[
        ('none', 'No Experience'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ])

    # Gap analysis
    gap_score = models.FloatField(default=0.0)  # Higher = bigger gap to fill
    estimated_learning_time = models.CharField(max_length=100, null=True, blank=True)

    # Recommended courses
    recommended_courses = models.JSONField(default=list)
    # Structure: [{name, platform, url, price, duration, rating, reviews}]

    # Related skills
    prerequisite_skills = models.JSONField(default=list)
    complementary_skills = models.JSONField(default=list)

    # Source
    source_spiders = models.JSONField(default=list)
    spider_data_ids = models.JSONField(default=list)

    # Timestamps
    analyzed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'skill_gap_analysis'
        ordering = ['-demand_score', '-gap_score']


# =============================================================================
# LEGAL INTELLIGENCE SITUATIONS
# =============================================================================

class CaseLawUpdate(models.Model):
    """
    Situation #18: Case Law Monitor
    Tracks relevant case decisions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Case info
    case_name = models.CharField(max_length=500)
    case_number = models.CharField(max_length=100, null=True, blank=True)
    court = models.CharField(max_length=200)
    jurisdiction = models.CharField(max_length=100)

    # Decision info
    decision_date = models.DateField()
    decision_type = models.CharField(max_length=50, choices=[
        ('opinion', 'Opinion'),
        ('order', 'Order'),
        ('ruling', 'Ruling'),
        ('judgment', 'Judgment'),
        ('dismissal', 'Dismissal'),
    ])

    # Content
    summary = models.TextField()
    key_holdings = models.JSONField(default=list)
    legal_issues = models.JSONField(default=list)

    # Categorization
    practice_areas = models.JSONField(default=list)  # family, criminal, civil, etc.
    topics = models.JSONField(default=list)

    # Relevance
    relevance_score = models.FloatField(default=0.0)
    precedential_value = models.CharField(max_length=20, choices=[
        ('binding', 'Binding'),
        ('persuasive', 'Persuasive'),
        ('limited', 'Limited'),
    ], null=True, blank=True)

    # Impact
    overrules = models.JSONField(default=list)  # Cases overruled
    distinguishes = models.JSONField(default=list)  # Cases distinguished

    # Links
    case_url = models.URLField(null=True, blank=True)
    pdf_url = models.URLField(null=True, blank=True)

    # Alert
    alert_sent = models.BooleanField(default=False)
    alert_sent_at = models.DateTimeField(null=True, blank=True)

    # Source
    source_spider = models.CharField(max_length=100)
    spider_data_id = models.UUIDField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'case_law_update'
        ordering = ['-decision_date', '-relevance_score']


class RegulatoryChange(models.Model):
    """
    Situation #19: Regulatory Change Detector
    Monitors regulatory changes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Change info
    title = models.CharField(max_length=500)
    agency = models.CharField(max_length=200)
    regulation_type = models.CharField(max_length=50, choices=[
        ('proposed_rule', 'Proposed Rule'),
        ('final_rule', 'Final Rule'),
        ('guidance', 'Guidance'),
        ('enforcement', 'Enforcement Action'),
        ('notice', 'Notice'),
        ('executive_order', 'Executive Order'),
    ])

    # Content
    summary = models.TextField()
    key_changes = models.JSONField(default=list)
    affected_parties = models.JSONField(default=list)

    # Dates
    published_date = models.DateField()
    effective_date = models.DateField(null=True, blank=True)
    comment_deadline = models.DateField(null=True, blank=True)

    # Impact analysis
    impact_score = models.FloatField(default=0.0)
    industries_affected = models.JSONField(default=list)
    compliance_requirements = models.JSONField(default=list)
    estimated_compliance_cost = models.CharField(max_length=100, null=True, blank=True)

    # Links
    document_url = models.URLField(null=True, blank=True)
    federal_register_url = models.URLField(null=True, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=[
        ('proposed', 'Proposed'),
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('withdrawn', 'Withdrawn'),
    ])

    # Alert
    alert_sent = models.BooleanField(default=False)
    alert_sent_at = models.DateTimeField(null=True, blank=True)

    # Source
    source_spider = models.CharField(max_length=100)
    spider_data_id = models.UUIDField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'regulatory_change'
        ordering = ['-published_date', '-impact_score']


# =============================================================================
# MONITORING SESSIONS (Unified for all situations)
# =============================================================================

class AutonomousSituationSession(models.Model):
    """
    Tracks monitoring sessions for all autonomous situations.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    situation_type = models.CharField(max_length=50, choices=[
        # Creative
        ('design_trends', 'Design Trends'),
        ('viral_prediction', 'Viral Prediction'),
        ('thumbnail_optimization', 'Thumbnail Optimization'),
        ('content_studio', 'Content Studio'),  # Session 497
        # Income
        ('job_matching', 'Job Matching'),
        ('freelance_scout', 'Freelance Scout'),
        ('side_hustle', 'Side Hustle Detection'),
        # Financial
        ('sec_filing', 'SEC Filing Analysis'),
        ('crypto_sentiment', 'Crypto Sentiment'),
        ('earnings_prediction', 'Earnings Prediction'),
        ('stock_market', 'Stock Market Intelligence'),  # Session 497
        ('blockchain', 'Blockchain Security'),  # Session 497
        # Research
        ('tech_stack', 'Tech Stack Evolution'),
        ('ai_model', 'AI Model Releases'),
        ('skill_gap', 'Skill Gap Analysis'),
        ('market_intelligence', 'Market Intelligence Desk'),  # Session 497
        ('narrative_drift', 'Narrative Drift Detector'),  # Session 497
        # Legal
        ('case_law', 'Case Law Monitor'),
        ('regulatory', 'Regulatory Changes'),
        # System
        ('trigger_processing', 'Trigger Event Processing'),  # Session 497
    ])

    # Session timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    next_scheduled = models.DateTimeField(null=True, blank=True)

    # Stats
    items_processed = models.IntegerField(default=0)
    items_created = models.IntegerField(default=0)
    items_updated = models.IntegerField(default=0)
    alerts_generated = models.IntegerField(default=0)

    # Status
    status = models.CharField(max_length=20, choices=[
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='running')
    error_message = models.TextField(null=True, blank=True)

    # Performance
    duration_seconds = models.FloatField(null=True, blank=True)
    spider_data_analyzed = models.IntegerField(default=0)

    class Meta:
        db_table = 'autonomous_situation_session'
        ordering = ['-started_at']
