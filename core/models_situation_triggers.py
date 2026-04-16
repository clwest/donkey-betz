"""
Situation Triggers - Session 477 (Part 2)

Event-driven triggers for Tier 1 Autonomous Situations.
Instead of only running on schedules, triggers fire IMMEDIATELY when
significant events are detected in spider data.

This transforms the system from reactive (check every 2-4 hours) to
proactive (alert within seconds of significant events).
"""

import uuid
import re
from django.db import models
from django.utils import timezone
from datetime import timedelta


class TriggerType(models.TextChoices):
    """Types of situation triggers."""
    # =========================================================================
    # BLOCKCHAIN/CRYPTO TRIGGERS (Financial Domain)
    # =========================================================================
    WHALE_MOVEMENT = 'whale_movement', 'Whale Movement (Large Transfer)'
    PRICE_CRASH = 'price_crash', 'Price Crash (Significant Drop)'
    PRICE_SURGE = 'price_surge', 'Price Surge (Significant Rise)'
    VOLUME_SPIKE = 'volume_spike', 'Volume Spike (Unusual Activity)'
    EXPLOIT_KEYWORD = 'exploit_keyword', 'Exploit/Hack Keyword Detected'
    CRYPTO_SENTIMENT = 'crypto_sentiment', 'Crypto Sentiment Shift'

    # =========================================================================
    # STOCK MARKET TRIGGERS (Financial Domain)
    # =========================================================================
    STOCK_MOVER = 'stock_mover', 'Stock Mover (Price Change)'
    SEC_FILING = 'sec_filing', 'SEC Filing Detected'
    BREAKING_NEWS = 'breaking_news', 'Breaking News (Market Keywords)'
    EARNINGS_SURPRISE = 'earnings_surprise', 'Earnings Surprise'
    INSTITUTIONAL_FILING = 'institutional_filing', 'Institutional Filing (13F/13D)'
    MARKET_INTELLIGENCE = 'market_intelligence', 'Market Intelligence Signal'

    # =========================================================================
    # CONTENT TRIGGERS (Content Domain)
    # =========================================================================
    CONTENT_TREND = 'content_trend', 'Content Trend Detected'
    NARRATIVE_DRIFT = 'narrative_drift', 'Narrative Drift Detected'
    VIRAL_CONTENT = 'viral_content', 'Viral Content Signal'

    # =========================================================================
    # CREATIVE TRIGGERS (Creative Domain)
    # =========================================================================
    DESIGN_TREND = 'design_trend', 'Design Trend Detected'
    VISUAL_TREND = 'visual_trend', 'Visual/Thumbnail Trend'
    CREATIVE_OPPORTUNITY = 'creative_opportunity', 'Creative Opportunity'

    # =========================================================================
    # INCOME TRIGGERS (Income Domain)
    # =========================================================================
    JOB_MATCH = 'job_match', 'Job Match Found'
    FREELANCE_OPPORTUNITY = 'freelance_opportunity', 'Freelance Opportunity'
    SIDE_HUSTLE = 'side_hustle', 'Side Hustle Opportunity'
    HIGH_PAYING_GIG = 'high_paying_gig', 'High-Paying Gig Detected'

    # =========================================================================
    # RESEARCH TRIGGERS (Research Domain)
    # =========================================================================
    TECH_STACK_CHANGE = 'tech_stack_change', 'Tech Stack Change'
    AI_MODEL_RELEASE = 'ai_model_release', 'AI Model Release'
    SKILL_GAP = 'skill_gap', 'Skill Gap Opportunity'
    TECH_BREAKTHROUGH = 'tech_breakthrough', 'Tech Breakthrough'

    # =========================================================================
    # LEGAL TRIGGERS (Legal Domain)
    # =========================================================================
    CASE_LAW_UPDATE = 'case_law_update', 'Case Law Update'
    REGULATORY_CHANGE = 'regulatory_change', 'Regulatory Change'
    LEGAL_PRECEDENT = 'legal_precedent', 'Legal Precedent Set'


class TriggerOperator(models.TextChoices):
    """Comparison operators for trigger evaluation."""
    GT = 'gt', 'Greater Than'
    GTE = 'gte', 'Greater Than or Equal'
    LT = 'lt', 'Less Than'
    LTE = 'lte', 'Less Than or Equal'
    EQ = 'eq', 'Equal To'
    NEQ = 'neq', 'Not Equal To'
    CONTAINS = 'contains', 'Contains (text)'
    REGEX = 'regex', 'Regex Match'


class SituationType(models.TextChoices):
    """Which autonomous situation this trigger belongs to."""
    # Financial Domain
    BLOCKCHAIN = 'blockchain', 'Blockchain Security'
    STOCK_MARKET = 'stock_market', 'Stock Market Intelligence'
    MARKET_INTELLIGENCE = 'market_intelligence', 'Market Intelligence Desk'
    SEC_FILING = 'sec_filing', 'SEC Filing Analyzer'
    CRYPTO_SENTIMENT = 'crypto_sentiment', 'Crypto Sentiment Monitor'
    EARNINGS_PREDICTION = 'earnings_prediction', 'Earnings Surprise Predictor'

    # Content Domain
    CONTENT_STUDIO = 'content_studio', 'Autonomous Content Studio'
    NARRATIVE_DRIFT = 'narrative_drift', 'Narrative Drift Detector'

    # Creative Domain
    DESIGN_TRENDS = 'design_trends', 'Design Trends Monitor'
    VIRAL_PREDICTION = 'viral_prediction', 'Viral Content Predictor'
    THUMBNAIL_OPTIMIZATION = 'thumbnail_optimization', 'Thumbnail A/B Optimizer'

    # Income Domain
    JOB_MATCHING = 'job_matching', 'Job Match Intelligence'
    FREELANCE_SCOUT = 'freelance_scout', 'Freelance Opportunity Scout'
    SIDE_HUSTLE = 'side_hustle', 'Side Hustle Detector'

    # Research Domain
    TECH_STACK = 'tech_stack', 'Tech Stack Evolution Tracker'
    AI_MODEL = 'ai_model', 'AI Model Release Monitor'
    SKILL_GAP = 'skill_gap', 'Course & Skill Gap Analyzer'

    # Legal Domain
    CASE_LAW = 'case_law', 'Case Law Monitor'
    REGULATORY = 'regulatory', 'Regulatory Change Detector'

    # Legacy (for backwards compatibility)
    BOTH = 'both', 'Multiple Systems'


class SituationTrigger(models.Model):
    """
    Configurable trigger for autonomous situation alerts.

    When spider data arrives matching the trigger conditions,
    an immediate alert is generated instead of waiting for scheduled runs.

    Example triggers:
    - "Alert immediately if ETH transfer > 500 ETH"
    - "Alert immediately if any stock drops > 8%"
    - "Alert immediately if SEC 13F filing detected"
    - "Alert immediately if news contains 'crash' or 'plunge'"
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Trigger identification
    name = models.CharField(
        max_length=100,
        help_text="Human-readable trigger name"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of what this trigger detects"
    )

    # Situation and type
    situation_type = models.CharField(
        max_length=30,  # Session 484: Increased from 20 to fit 'thumbnail_optimization' (22 chars)
        choices=SituationType.choices,
        default=SituationType.BLOCKCHAIN,
        db_index=True
    )
    trigger_type = models.CharField(
        max_length=30,
        choices=TriggerType.choices,
        db_index=True
    )

    # Spider targeting
    target_spiders = models.JSONField(
        default=list,
        help_text="List of spider names to monitor (empty = all spiders)"
    )

    # Condition: which field to check
    target_field = models.CharField(
        max_length=100,
        help_text="JSON path in raw_data to check (e.g., 'items.0.value', 'price_change_percentage_24h')"
    )

    # Condition: how to compare
    operator = models.CharField(
        max_length=20,
        choices=TriggerOperator.choices,
        default=TriggerOperator.GT
    )

    # Condition: threshold value
    threshold_value = models.CharField(
        max_length=200,
        help_text="Value to compare against (number or text pattern)"
    )

    # Alert configuration
    severity = models.CharField(
        max_length=20,
        choices=[
            ('critical', 'Critical'),
            ('high', 'High'),
            ('medium', 'Medium'),
            ('low', 'Low'),
        ],
        default='high'
    )
    alert_title_template = models.CharField(
        max_length=200,
        default="{trigger_name}: {matched_value}",
        help_text="Template for alert title. Use {trigger_name}, {matched_value}, {spider_name}"
    )

    # Cooldown to prevent alert spam
    cooldown_minutes = models.IntegerField(
        default=30,
        help_text="Minimum minutes between alerts from this trigger"
    )
    last_triggered_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this trigger last fired"
    )

    # Status and stats
    is_active = models.BooleanField(default=True, db_index=True)
    priority = models.IntegerField(
        default=50,
        help_text="Higher priority triggers are evaluated first (0-100)"
    )
    total_fires = models.IntegerField(default=0)
    total_alerts_generated = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        db_table = 'situation_trigger'
        ordering = ['-priority', 'name']
        indexes = [
            models.Index(fields=['situation_type', 'is_active']),
            models.Index(fields=['trigger_type', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_trigger_type_display()})"

    def is_on_cooldown(self) -> bool:
        """Check if trigger is still in cooldown period."""
        if not self.last_triggered_at:
            return False
        cooldown_end = self.last_triggered_at + timedelta(minutes=self.cooldown_minutes)
        return timezone.now() < cooldown_end

    def get_nested_value(self, data: dict, path: str):
        """
        Extract nested value from dict using dot notation.
        e.g., 'items.0.value' gets data['items'][0]['value']
        """
        if not data or not path:
            return None

        keys = path.split('.')
        value = data

        for key in keys:
            if value is None:
                return None
            if isinstance(value, dict):
                value = value.get(key)
            elif isinstance(value, list):
                try:
                    idx = int(key)
                    value = value[idx] if idx < len(value) else None
                except (ValueError, IndexError):
                    return None
            else:
                return None

        return value

    def evaluate(self, spider_data) -> tuple[bool, any]:
        """
        Evaluate if spider data matches this trigger's conditions.

        Returns:
            (matches: bool, matched_value: any)
        """
        # Check if trigger is active
        if not self.is_active:
            return False, None

        # Check cooldown
        if self.is_on_cooldown():
            return False, None

        # Check if spider matches
        if self.target_spiders and spider_data.spider_name not in self.target_spiders:
            return False, None

        # Get raw data
        raw_data = spider_data.raw_data or {}

        # Handle 'items' array - check each item
        items = raw_data.get('items', [raw_data])
        if not isinstance(items, list):
            items = [items]

        for item in items:
            # Get the value to check
            if '.' in self.target_field:
                value = self.get_nested_value(item, self.target_field)
            else:
                value = item.get(self.target_field)

            if value is None:
                continue

            # Evaluate the condition
            matches = self._evaluate_condition(value)
            if matches:
                return True, value

        return False, None

    def _evaluate_condition(self, value) -> bool:
        """Evaluate if a value matches the trigger condition."""
        try:
            threshold = self.threshold_value

            # Numeric comparisons
            if self.operator in ['gt', 'gte', 'lt', 'lte', 'eq', 'neq']:
                # Convert to numbers
                if isinstance(value, str):
                    value = float(value.replace(',', '').replace('$', ''))
                else:
                    value = float(value)
                threshold = float(threshold)

                if self.operator == 'gt':
                    return value > threshold
                elif self.operator == 'gte':
                    return value >= threshold
                elif self.operator == 'lt':
                    return value < threshold
                elif self.operator == 'lte':
                    return value <= threshold
                elif self.operator == 'eq':
                    return value == threshold
                elif self.operator == 'neq':
                    return value != threshold

            # Text comparisons
            elif self.operator == 'contains':
                value_str = str(value).lower()
                # Support multiple keywords separated by |
                keywords = [k.strip().lower() for k in threshold.split('|')]
                return any(kw in value_str for kw in keywords)

            elif self.operator == 'regex':
                value_str = str(value)
                return bool(re.search(threshold, value_str, re.IGNORECASE))

        except (ValueError, TypeError):
            return False

        return False

    def fire(self, spider_data, matched_value) -> 'TriggerEvent':
        """
        Fire this trigger and create a TriggerEvent.

        This is called when evaluate() returns True.
        """
        # Update trigger stats
        self.total_fires += 1
        self.last_triggered_at = timezone.now()
        self.save(update_fields=['total_fires', 'last_triggered_at'])

        # Create trigger event
        event = TriggerEvent.objects.create(
            trigger=self,
            spider_data=spider_data,
            spider_name=spider_data.spider_name,
            matched_field=self.target_field,
            matched_value=str(matched_value)[:500],
            raw_data_snapshot=spider_data.raw_data or {}
        )

        return event


class TriggerEvent(models.Model):
    """
    Record of a trigger firing.

    Each time a SituationTrigger evaluates to True, a TriggerEvent is created.
    This provides an audit trail and feeds into the alert generation system.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Which trigger fired
    trigger = models.ForeignKey(
        SituationTrigger,
        on_delete=models.CASCADE,
        related_name='events'
    )

    # What data caused it
    spider_data = models.ForeignKey(
        'core.SpiderData',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trigger_events'
    )
    spider_name = models.CharField(max_length=100)
    matched_field = models.CharField(max_length=100)
    matched_value = models.CharField(max_length=500)
    raw_data_snapshot = models.JSONField(default=dict)

    # Alert generation
    alert_generated = models.BooleanField(default=False)
    alert_id = models.UUIDField(null=True, blank=True)
    alert_type = models.CharField(max_length=50, blank=True)  # 'blockchain' or 'stock'

    # Discord notification
    discord_sent = models.BooleanField(default=False)
    discord_sent_at = models.DateTimeField(null=True, blank=True)

    # Processing status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Processing'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('skipped', 'Skipped (Cooldown/Duplicate)'),
        ],
        default='pending'
    )
    error_message = models.TextField(blank=True)

    # Timestamps
    fired_at = models.DateTimeField(default=timezone.now, db_index=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        db_table = 'trigger_event'
        ordering = ['-fired_at']
        indexes = [
            models.Index(fields=['trigger', '-fired_at']),
            models.Index(fields=['status', '-fired_at']),
            models.Index(fields=['spider_name', '-fired_at']),
        ]

    def __str__(self):
        return f"{self.trigger.name} @ {self.fired_at.strftime('%Y-%m-%d %H:%M')}"


# =============================================================================
# Default Trigger Definitions
# =============================================================================
# These are created via data migration or management command

DEFAULT_TRIGGERS = [
    # =========================================================================
    # BLOCKCHAIN TRIGGERS
    # =========================================================================
    {
        'name': 'Whale Movement (100+ ETH)',
        'description': 'Alert when ETH transfer exceeds 100 ETH (~$350k+)',
        'situation_type': 'blockchain',
        'trigger_type': 'whale_movement',
        'target_spiders': ['etherscan', 'etherscan_api'],
        'target_field': 'value',
        'operator': 'gt',
        'threshold_value': '100',
        'severity': 'high',
        'alert_title_template': 'Whale Alert: {matched_value} ETH Transfer',
        'cooldown_minutes': 15,
        'priority': 90,
    },
    {
        'name': 'Mega Whale (1000+ ETH)',
        'description': 'Critical alert for massive transfers over 1000 ETH (~$3.5M+)',
        'situation_type': 'blockchain',
        'trigger_type': 'whale_movement',
        'target_spiders': ['etherscan', 'etherscan_api'],
        'target_field': 'value',
        'operator': 'gt',
        'threshold_value': '1000',
        'severity': 'critical',
        'alert_title_template': 'MEGA WHALE: {matched_value} ETH Moving!',
        'cooldown_minutes': 5,
        'priority': 100,
    },
    {
        'name': 'Price Crash (>10% Drop)',
        'description': 'Alert when any token drops more than 10% in 24h',
        'situation_type': 'blockchain',
        'trigger_type': 'price_crash',
        'target_spiders': ['coingecko'],
        'target_field': 'price_change_percentage_24h',
        'operator': 'lt',
        'threshold_value': '-10',
        'severity': 'high',
        'alert_title_template': 'Price Crash: {matched_value}% Drop Detected',
        'cooldown_minutes': 30,
        'priority': 85,
    },
    {
        'name': 'Severe Crash (>20% Drop)',
        'description': 'Critical alert for crashes exceeding 20%',
        'situation_type': 'blockchain',
        'trigger_type': 'price_crash',
        'target_spiders': ['coingecko'],
        'target_field': 'price_change_percentage_24h',
        'operator': 'lt',
        'threshold_value': '-20',
        'severity': 'critical',
        'alert_title_template': 'SEVERE CRASH: {matched_value}% Collapse!',
        'cooldown_minutes': 15,
        'priority': 95,
    },
    {
        'name': 'Exploit/Hack Keywords',
        'description': 'Alert when news mentions exploit, hack, or rug pull',
        'situation_type': 'blockchain',
        'trigger_type': 'exploit_keyword',
        'target_spiders': ['hackernews', 'techcrunch', 'reddit', 'business_news'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'exploit|hack|rug pull|drained|stolen|vulnerability|breach',
        'severity': 'critical',
        'alert_title_template': 'Security Alert: Potential Exploit Detected',
        'cooldown_minutes': 60,
        'priority': 95,
    },

    # =========================================================================
    # STOCK MARKET TRIGGERS
    # =========================================================================
    {
        'name': 'Stock Mover (>5% Change)',
        'description': 'Alert when any stock moves more than 5%',
        'situation_type': 'stock_market',
        'trigger_type': 'stock_mover',
        'target_spiders': ['yahoo_finance', 'finnhub'],
        'target_field': 'regularMarketChangePercent',
        'operator': 'gt',
        'threshold_value': '5',
        'severity': 'medium',
        'alert_title_template': 'Stock Mover: {matched_value}% Change',
        'cooldown_minutes': 30,
        'priority': 70,
    },
    {
        'name': 'Major Stock Move (>10% Change)',
        'description': 'Alert when stock moves more than 10%',
        'situation_type': 'stock_market',
        'trigger_type': 'stock_mover',
        'target_spiders': ['yahoo_finance', 'finnhub'],
        'target_field': 'regularMarketChangePercent',
        'operator': 'gt',
        'threshold_value': '10',
        'severity': 'high',
        'alert_title_template': 'Major Move: {matched_value}% Stock Swing!',
        'cooldown_minutes': 15,
        'priority': 85,
    },
    {
        'name': 'Stock Crash (>5% Drop)',
        'description': 'Alert when stock drops more than 5%',
        'situation_type': 'stock_market',
        'trigger_type': 'stock_mover',
        'target_spiders': ['yahoo_finance', 'finnhub'],
        'target_field': 'regularMarketChangePercent',
        'operator': 'lt',
        'threshold_value': '-5',
        'severity': 'high',
        'alert_title_template': 'Stock Drop: {matched_value}% Decline',
        'cooldown_minutes': 30,
        'priority': 80,
    },
    {
        'name': 'SEC Filing (13F/13D)',
        'description': 'Alert on institutional filings (13F, 13D, 13G)',
        'situation_type': 'stock_market',
        'trigger_type': 'sec_filing',
        'target_spiders': ['sec_edgar'],
        'target_field': 'form',
        'operator': 'contains',
        'threshold_value': '13F|13D|13G|8-K',
        'severity': 'medium',
        'alert_title_template': 'SEC Filing: {matched_value} Detected',
        'cooldown_minutes': 60,
        'priority': 75,
    },
    {
        'name': 'Breaking Market News',
        'description': 'Alert on breaking news with market-moving keywords',
        'situation_type': 'stock_market',
        'trigger_type': 'breaking_news',
        'target_spiders': ['business_news', 'reuters_rss', 'google_news'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'crash|surge|plunge|soar|collapse|rally|breakout|bankruptcy|merger|acquisition',
        'severity': 'high',
        'alert_title_template': 'Breaking: Market-Moving News Detected',
        'cooldown_minutes': 30,
        'priority': 80,
    },
    {
        # Session 1092: Downgraded from high → medium and cooldown 60 → 720 (12h).
        # Rationale: Every Fed-related news headline was firing as 'high' urgency,
        # producing 5+ "Fed Alert" attention items per 24h with no actionable signal.
        # Truly market-moving Fed events are now caught by 'FOMC Rate Decision' below.
        'name': 'Fed/Interest Rate News',
        'description': 'Background signal on general Federal Reserve / interest rate news',
        'situation_type': 'stock_market',
        'trigger_type': 'breaking_news',
        'target_spiders': ['business_news', 'reuters_rss', 'google_news'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'fed |federal reserve|interest rate|rate hike|rate cut|powell|fomc',
        'severity': 'medium',
        'alert_title_template': 'Fed Alert: {matched_value}',
        'cooldown_minutes': 720,
        'priority': 60,
    },
    {
        # Session 1092: Narrow high-severity trigger for actually-actionable Fed events.
        # Keywords scoped to rate-decision artifacts and emergency actions.
        'name': 'FOMC Rate Decision',
        'description': 'High-priority alert on FOMC decisions, dot plots, and emergency Fed action',
        'situation_type': 'stock_market',
        'trigger_type': 'breaking_news',
        'target_spiders': ['business_news', 'reuters_rss', 'google_news'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'fomc statement|fomc minutes|rate decision|basis points|dot plot|emergency meeting|inter-meeting|surprise cut|surprise hike|liquidity facility',
        'severity': 'high',
        'alert_title_template': 'FOMC: {matched_value}',
        'cooldown_minutes': 60,
        'priority': 92,
    },

    # =========================================================================
    # CONTENT TRIGGERS (Content Domain)
    # =========================================================================
    {
        'name': 'Trending Content Topic',
        'description': 'Alert when viral or trending content topics are detected',
        'situation_type': 'content_studio',
        'trigger_type': 'content_trend',
        'target_spiders': ['reddit', 'hackernews', 'techcrunch', 'youtube_trending'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'viral|trending|million views|breaking|exclusive|leaked',
        'severity': 'medium',
        'alert_title_template': 'Content Trend: {matched_value}',
        'cooldown_minutes': 120,
        'priority': 70,
    },
    {
        'name': 'High Engagement Signal',
        'description': 'Alert when content shows high engagement metrics',
        'situation_type': 'content_studio',
        'trigger_type': 'viral_content',
        'target_spiders': ['reddit', 'hackernews'],
        'target_field': 'score',
        'operator': 'gt',
        'threshold_value': '500',
        'severity': 'medium',
        'alert_title_template': 'High Engagement: {matched_value} points',
        'cooldown_minutes': 60,
        'priority': 75,
    },
    {
        'name': 'Narrative Shift Detection',
        'description': 'Alert when significant narrative shifts are detected in news',
        'situation_type': 'narrative_drift',
        'trigger_type': 'narrative_drift',
        'target_spiders': ['google_news', 'techcrunch', 'reddit', 'hackernews'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'pivot|shift|change|new direction|announces|reveals|confirms',
        'severity': 'medium',
        'alert_title_template': 'Narrative Shift: {matched_value}',
        'cooldown_minutes': 180,
        'priority': 65,
    },

    # =========================================================================
    # CREATIVE TRIGGERS (Creative Domain)
    # =========================================================================
    {
        'name': 'Design Trend Alert',
        'description': 'Alert when new design trends are detected on creative platforms',
        'situation_type': 'design_trends',
        'trigger_type': 'design_trend',
        'target_spiders': ['dribbble', 'behance', 'unsplash'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': '2024|2025|trend|minimal|gradient|3d|ai generated|neon|glassmorphism|neumorphism',
        'severity': 'low',
        'alert_title_template': 'Design Trend: {matched_value}',
        'cooldown_minutes': 240,
        'priority': 50,
    },
    {
        'name': 'Viral Visual Content',
        'description': 'Alert when visual content shows viral potential',
        'situation_type': 'viral_prediction',
        'trigger_type': 'viral_content',
        'target_spiders': ['dribbble', 'behance', 'unsplash', 'reddit'],
        'target_field': 'likes',
        'operator': 'gt',
        'threshold_value': '1000',
        'severity': 'medium',
        'alert_title_template': 'Viral Visual: {matched_value} likes',
        'cooldown_minutes': 120,
        'priority': 60,
    },
    {
        'name': 'Thumbnail Style Trend',
        'description': 'Alert when new thumbnail styles gain traction',
        'situation_type': 'thumbnail_optimization',
        'trigger_type': 'visual_trend',
        'target_spiders': ['youtube_trending', 'dribbble'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'thumbnail|click|ctr|convert|attention|hook',
        'severity': 'low',
        'alert_title_template': 'Thumbnail Trend: {matched_value}',
        'cooldown_minutes': 360,
        'priority': 45,
    },

    # =========================================================================
    # INCOME TRIGGERS (Income Domain)
    # =========================================================================
    {
        'name': 'High-Paying Remote Job',
        'description': 'Alert when high-paying remote jobs are posted',
        'situation_type': 'job_matching',
        'trigger_type': 'job_match',
        'target_spiders': ['remoteok', 'weworkremotely', 'adzuna'],
        'target_field': 'salary',
        'operator': 'gt',
        'threshold_value': '150000',
        'severity': 'high',
        'alert_title_template': 'High-Paying Job: ${matched_value}',
        'cooldown_minutes': 30,
        'priority': 85,
    },
    {
        'name': 'Senior/Lead Position',
        'description': 'Alert when senior or lead positions are posted',
        'situation_type': 'job_matching',
        'trigger_type': 'job_match',
        'target_spiders': ['remoteok', 'weworkremotely', 'adzuna'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'senior|lead|principal|staff|architect|director|head of',
        'severity': 'medium',
        'alert_title_template': 'Senior Role: {matched_value}',
        'cooldown_minutes': 60,
        'priority': 75,
    },
    {
        'name': 'Freelance Opportunity',
        'description': 'Alert when freelance/contract opportunities are posted',
        'situation_type': 'freelance_scout',
        'trigger_type': 'freelance_opportunity',
        'target_spiders': ['remoteok', 'weworkremotely', 'adzuna'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'freelance|contract|consultant|part-time|remote',
        'severity': 'medium',
        'alert_title_template': 'Freelance: {matched_value}',
        'cooldown_minutes': 120,
        'priority': 70,
    },
    {
        'name': 'High-Rate Freelance Gig',
        'description': 'Alert when high-rate freelance gigs are detected',
        'situation_type': 'freelance_scout',
        'trigger_type': 'high_paying_gig',
        'target_spiders': ['remoteok', 'weworkremotely', 'adzuna'],
        'target_field': 'salary',
        'operator': 'gt',
        'threshold_value': '100',  # Hourly rate
        'severity': 'high',
        'alert_title_template': 'High-Rate Gig: ${matched_value}/hr',
        'cooldown_minutes': 60,
        'priority': 80,
    },
    {
        'name': 'Side Hustle Opportunity',
        'description': 'Alert when side hustle opportunities are detected',
        'situation_type': 'side_hustle',
        'trigger_type': 'side_hustle',
        'target_spiders': ['reddit', 'hackernews', 'indiegogo', 'kickstarter'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'passive income|side hustle|make money|earn|revenue|monetize|saas|startup',
        'severity': 'low',
        'alert_title_template': 'Side Hustle: {matched_value}',
        'cooldown_minutes': 240,
        'priority': 55,
    },

    # =========================================================================
    # RESEARCH TRIGGERS (Research Domain)
    # =========================================================================
    {
        'name': 'New Tech Stack Trend',
        'description': 'Alert when new technology trends are discussed',
        'situation_type': 'tech_stack',
        'trigger_type': 'tech_stack_change',
        'target_spiders': ['hackernews', 'techcrunch', 'devto', 'reddit'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'rust|go|kubernetes|docker|terraform|react|vue|svelte|nextjs|bun|deno',
        'severity': 'low',
        'alert_title_template': 'Tech Trend: {matched_value}',
        'cooldown_minutes': 360,
        'priority': 50,
    },
    {
        'name': 'Framework/Library Release',
        'description': 'Alert when major framework releases are announced',
        'situation_type': 'tech_stack',
        'trigger_type': 'tech_stack_change',
        'target_spiders': ['hackernews', 'devto', 'reddit'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'release|v2|v3|stable|launch|announces|introduced|available',
        'severity': 'medium',
        'alert_title_template': 'Release: {matched_value}',
        'cooldown_minutes': 120,
        'priority': 65,
    },
    {
        'name': 'AI Model Release',
        'description': 'Alert when new AI models are released',
        'situation_type': 'ai_model',
        'trigger_type': 'ai_model_release',
        'target_spiders': ['hackernews', 'techcrunch', 'reddit', 'devto'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'gpt-5|claude|gemini|llama|mistral|ai model|language model|llm|diffusion|stable diffusion|midjourney|dall-e|openai|anthropic',
        'severity': 'high',
        'alert_title_template': 'AI Model: {matched_value}',
        'cooldown_minutes': 60,
        'priority': 85,
    },
    {
        'name': 'AI Breakthrough',
        'description': 'Alert when AI breakthroughs are announced',
        'situation_type': 'ai_model',
        'trigger_type': 'tech_breakthrough',
        'target_spiders': ['hackernews', 'techcrunch', 'mit_tech_review'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'breakthrough|revolutionary|groundbreaking|state-of-the-art|beats|outperforms|achieves',
        'severity': 'high',
        'alert_title_template': 'AI Breakthrough: {matched_value}',
        'cooldown_minutes': 120,
        'priority': 80,
    },
    {
        'name': 'In-Demand Skill',
        'description': 'Alert when job postings mention in-demand skills',
        'situation_type': 'skill_gap',
        'trigger_type': 'skill_gap',
        'target_spiders': ['remoteok', 'weworkremotely', 'adzuna', 'coursera'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'ai|ml|machine learning|deep learning|python|rust|kubernetes|aws|cloud|devops',
        'severity': 'low',
        'alert_title_template': 'Skill Demand: {matched_value}',
        'cooldown_minutes': 480,
        'priority': 40,
    },

    # =========================================================================
    # LEGAL TRIGGERS (Legal Domain)
    # =========================================================================
    {
        'name': 'Case Law Update',
        'description': 'Alert when significant case law updates are detected',
        'situation_type': 'case_law',
        'trigger_type': 'case_law_update',
        'target_spiders': ['google_news', 'reuters_rss'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'court|ruling|verdict|decision|appeal|supreme court|lawsuit|settlement|judgment',
        'severity': 'medium',
        'alert_title_template': 'Case Law: {matched_value}',
        'cooldown_minutes': 240,
        'priority': 60,
    },
    {
        'name': 'Tech Industry Legal',
        'description': 'Alert when tech-related legal news is detected',
        'situation_type': 'case_law',
        'trigger_type': 'legal_precedent',
        'target_spiders': ['techcrunch', 'hackernews', 'google_news'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'antitrust|patent|copyright|privacy|gdpr|ftc|doj|sec|regulation|compliance',
        'severity': 'medium',
        'alert_title_template': 'Tech Legal: {matched_value}',
        'cooldown_minutes': 180,
        'priority': 65,
    },
    {
        'name': 'Regulatory Change',
        'description': 'Alert when regulatory changes are announced',
        'situation_type': 'regulatory',
        'trigger_type': 'regulatory_change',
        'target_spiders': ['google_news', 'reuters_rss', 'business_news'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'regulation|regulatory|law|legislation|bill|act|policy|mandate|requirement|compliance',
        'severity': 'medium',
        'alert_title_template': 'Regulatory: {matched_value}',
        'cooldown_minutes': 240,
        'priority': 60,
    },
    {
        'name': 'Crypto Regulation',
        'description': 'Alert when crypto-related regulatory news is detected',
        'situation_type': 'regulatory',
        'trigger_type': 'regulatory_change',
        'target_spiders': ['google_news', 'techcrunch', 'reddit'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'crypto regulation|sec crypto|bitcoin regulation|stablecoin|cbdc|digital currency law',
        'severity': 'high',
        'alert_title_template': 'Crypto Regulation: {matched_value}',
        'cooldown_minutes': 120,
        'priority': 75,
    },

    # =========================================================================
    # MARKET INTELLIGENCE & EARNINGS TRIGGERS
    # =========================================================================
    {
        'name': 'Market Intelligence Signal',
        'description': 'Alert when market-moving news is detected',
        'situation_type': 'market_intelligence',
        'trigger_type': 'market_intelligence',
        'target_spiders': ['business_news', 'reuters_rss', 'yahoo_finance'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'market|dow|nasdaq|s&p|trading|investors|wall street|stocks',
        'severity': 'medium',
        'alert_title_template': 'Market: {matched_value}',
        'cooldown_minutes': 60,
        'priority': 70,
    },
    {
        'name': 'Earnings Report',
        'description': 'Alert when earnings reports are released',
        'situation_type': 'earnings_prediction',
        'trigger_type': 'earnings_surprise',
        'target_spiders': ['business_news', 'yahoo_finance', 'sec_edgar'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'earnings|quarterly|q1|q2|q3|q4|revenue|profit|eps|beat|miss|guidance',
        'severity': 'high',
        'alert_title_template': 'Earnings: {matched_value}',
        'cooldown_minutes': 30,
        'priority': 85,
    },
    {
        'name': 'Crypto Sentiment Shift',
        'description': 'Alert when crypto sentiment shifts significantly',
        'situation_type': 'crypto_sentiment',
        'trigger_type': 'crypto_sentiment',
        'target_spiders': ['reddit', 'hackernews', 'coingecko'],
        'target_field': 'title',
        'operator': 'contains',
        'threshold_value': 'bitcoin|ethereum|btc|eth|crypto|defi|nft|bull|bear|moon|dump',
        'severity': 'medium',
        'alert_title_template': 'Crypto Sentiment: {matched_value}',
        'cooldown_minutes': 120,
        'priority': 65,
    },
]
