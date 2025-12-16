"""
User-related models for profiles, preferences, and statistics
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from ..base.models import UnifiedBaseModel


class UserProfile(models.Model):
    """
    Extended user profile information for persistent storage.
    """
    ACCOUNT_TYPES = [
        ('free', 'Free'),
        ('pro', 'Professional'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]

    CONTENT_TONES = [
        ('professional', 'Professional'),
        ('casual', 'Casual'),
        ('academic', 'Academic'),
        ('creative', 'Creative'),
        ('technical', 'Technical'),
    ]

    AI_MODELS = [
        ('gpt-5', 'GPT-5'),
        ('gpt-5-mini', 'GPT-5 Mini'),
        ('gpt-5-nano', 'GPT-5 Nano'),
        ('gpt-5-mini', 'GPT-4'),
        ('claude-3-sonnet', 'Claude 3 Sonnet'),
    ]

    # Link to user
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='userprofile')

    # Profile information
    avatar = models.URLField(max_length=500, blank=True, null=True)
    avatar_file = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    display_name = models.CharField(max_length=100, blank=True, default='')
    occupation = models.CharField(max_length=100, blank=True, default='')
    location = models.CharField(max_length=100, blank=True, default='')

    # Professional information
    skills = models.JSONField(default=list, blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    current_role = models.CharField(max_length=200, blank=True, default='')
    industries = models.JSONField(default=list, blank=True, null=True)
    portfolio_url = models.URLField(blank=True, default='')
    linkedin_url = models.URLField(blank=True, default='')
    github_url = models.URLField(blank=True, default='')
    resume_id = models.CharField(max_length=100, blank=True, null=True)

    # Job preferences
    remote_only = models.BooleanField(default=True)
    contract_work = models.BooleanField(default=True)
    full_time = models.BooleanField(default=True)
    hourly_rate_min = models.IntegerField(default=50)
    salary_min = models.IntegerField(default=50000)

    # Preferences
    preferred_ai_model = models.CharField(max_length=20, default='gpt-5-mini')
    default_content_tone = models.CharField(max_length=20, default='professional')
    auto_save = models.BooleanField(default=True)
    dark_mode = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    default_citation_style = models.CharField(max_length=10, default='APA')
    preferred_book_length = models.CharField(max_length=10, default='medium')
    research_topics = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True
    )

    # Account information
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='premium')
    credits_remaining = models.IntegerField(default=10000)
    storage_used_mb = models.FloatField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_userprofile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username}'s profile"

    def get_avatar_url(self):
        """Get the avatar URL, with fallback to default."""
        if self.avatar_file:
            # avatar_file is an ImageField, so use its url property if available
            try:
                url = self.avatar_file.url
                # Ensure it's an absolute URL for frontend compatibility
                if url and not url.startswith('http'):
                    return f"http://localhost:8000{url}"
                return url
            except:
                # Fallback if file doesn't exist
                return f"http://localhost:8000/media/{self.avatar_file}"
        elif self.avatar:
            # If avatar is already set (could be external URL or local)
            if self.avatar and not self.avatar.startswith('http'):
                return f"http://localhost:8000{self.avatar}"
            return self.avatar
        else:
            # Default avatar
            return f"https://api.dicebear.com/7.x/avataaars/svg?seed={self.user.username}"

    def get_display_name(self):
        """Get display name or fallback to full name or username."""
        if self.display_name:
            return self.display_name
        elif self.user.first_name or self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}".strip()
        else:
            return self.user.username


class UserPreferences(models.Model):
    """
    User AI preferences and configuration settings
    """
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='ai_preferences')

    # AI Configuration
    default_model = models.CharField(max_length=50, default='gpt-5')
    reasoning_level = models.CharField(max_length=20, default='medium')
    automation_level = models.CharField(max_length=20, default='semi-auto')
    daily_token_limit = models.IntegerField(default=100000)
    monthly_spending_limit = models.FloatField(default=500.0)
    memory_retention_days = models.IntegerField(default=30)
    share_memory_across_agents = models.BooleanField(default=True)

    # Assigned agents
    assigned_agents = models.JSONField(default=list, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_userpreferences'
        verbose_name = 'User Preferences'
        verbose_name_plural = 'User Preferences'

    def __str__(self):
        return f"{self.user.username}'s preferences"


class UserStatistics(models.Model):
    """
    User content generation statistics for tracking.
    """
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='userstatistics')

    # Content counts
    total_contents = models.IntegerField(default=0)
    total_images = models.IntegerField(default=0)
    total_videos = models.IntegerField(default=0)
    total_blogs = models.IntegerField(default=0)
    total_social_posts = models.IntegerField(default=0)
    total_ebooks = models.IntegerField(default=0)
    total_research_docs = models.IntegerField(default=0)
    total_campaigns = models.IntegerField(default=0)

    # Usage statistics
    total_ai_requests = models.IntegerField(default=0)
    total_tokens_used = models.BigIntegerField(default=0)
    total_exports = models.IntegerField(default=0)

    # Preferences
    favorite_style = models.CharField(max_length=50, blank=True, default='')

    # Activity tracking
    last_7_days_activity = models.IntegerField(default=0)
    last_30_days_activity = models.IntegerField(default=0)

    # Storage
    images_storage_mb = models.FloatField(default=0)
    videos_storage_mb = models.FloatField(default=0)
    documents_storage_mb = models.FloatField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_userstatistics'
        verbose_name = 'User Statistics'
        verbose_name_plural = 'User Statistics'

    def __str__(self):
        return f"{self.user.username}'s statistics"

    def get_total_storage_mb(self):
        """Calculate total storage used."""
        return self.images_storage_mb + self.videos_storage_mb + self.documents_storage_mb


class ExtendedUserProfile(UnifiedBaseModel):
    """
    Extended user profile with professional information for job applications.

    This model extends the basic UserProfile with detailed career information,
    skills, work history, and job preferences needed for AI workforce automation.
    """
    REMOTE_PREFERENCES = [
        ('remote', 'Remote Only'),
        ('hybrid', 'Hybrid (Remote + Office)'),
        ('onsite', 'On-site Only'),
        ('no_preference', 'No Preference'),
    ]

    EXPERIENCE_LEVELS = [
        ('entry', 'Entry Level (0-2 years)'),
        ('junior', 'Junior (2-4 years)'),
        ('mid', 'Mid Level (4-7 years)'),
        ('senior', 'Senior (7-10 years)'),
        ('lead', 'Lead/Principal (10+ years)'),
        ('executive', 'Executive (C-Level)'),
    ]

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='extended_profile'
    )

    # Personal Information
    full_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200, blank=True)
    timezone = models.CharField(max_length=50, blank=True)

    # Professional Profile
    current_title = models.CharField(max_length=200, blank=True)
    years_experience = models.IntegerField(default=0)
    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_LEVELS,
        default='entry'
    )
    desired_salary_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    desired_salary_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Skills & Certifications (JSON fields for flexibility)
    skills = models.JSONField(
        default=list,
        help_text="List of skills with proficiency levels: [{'name': 'Python', 'proficiency': 'Expert', 'years': 5}]"
    )
    certifications = models.JSONField(
        default=list,
        help_text="List of certifications: [{'name': 'AWS Certified', 'issued_by': 'Amazon', 'date': '2023-01-01'}]"
    )

    # Work History & Education
    work_history = models.JSONField(
        default=list,
        help_text="Work experience entries with company, role, dates, responsibilities"
    )
    education = models.JSONField(
        default=list,
        help_text="Education entries with degree, institution, graduation year"
    )

    # Documents
    resume = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True,
        help_text="Primary resume file"
    )
    portfolio_url = models.URLField(blank=True)
    cover_letters = models.JSONField(
        default=dict,
        help_text="Cover letter templates by industry/role type"
    )

    # Platform Credentials for Job Applications
    linkedin_url = models.URLField(blank=True)
    indeed_profile = models.CharField(max_length=200, blank=True)
    github_username = models.CharField(max_length=100, blank=True)

    # Job Preferences
    job_preferences = models.JSONField(
        default=dict,
        help_text="Job search preferences including industries, role types, company sizes"
    )
    remote_preference = models.CharField(
        max_length=20,
        choices=REMOTE_PREFERENCES,
        default='no_preference'
    )
    willing_to_relocate = models.BooleanField(default=False)

    # Profile Completion Tracking
    profile_completeness = models.FloatField(
        default=0.0,
        help_text="Percentage of profile completion (0-100)"
    )

    def calculate_profile_completeness(self):
        """Calculate and update profile completion percentage."""
        required_fields = [
            'full_name', 'phone', 'location', 'current_title',
            'years_experience', 'skills', 'work_history', 'resume'
        ]

        completed_fields = 0
        total_fields = len(required_fields)

        for field in required_fields:
            value = getattr(self, field)
            if value:  # Check if field has a value
                if isinstance(value, list) and len(value) > 0:
                    completed_fields += 1
                elif isinstance(value, str) and value.strip():
                    completed_fields += 1
                elif isinstance(value, (int, float)) and value > 0:
                    completed_fields += 1
                elif hasattr(value, 'name'):  # File field
                    completed_fields += 1

        self.profile_completeness = (completed_fields / total_fields) * 100
        return self.profile_completeness

    def get_skills_list(self):
        """Get list of skill names for easy access."""
        return [skill.get('name', '') for skill in self.skills if skill.get('name')]

    def get_top_skills(self, limit=5):
        """Get top skills by proficiency for display."""
        sorted_skills = sorted(
            self.skills,
            key=lambda x: x.get('years', 0),
            reverse=True
        )
        return sorted_skills[:limit]

    class Meta:
        verbose_name = "Extended User Profile"
        verbose_name_plural = "Extended User Profiles"

    def __str__(self):
        return f"{self.user.username}'s extended profile ({self.profile_completeness:.1f}% complete)"


class EnhancedUserProfile(models.Model):
    """
    Comprehensive user profile for deep personalization and memory retrieval.
    """

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='enhanced_profile')

    # ========== 1. KEY ROLES & LONG-TERM GOALS ==========
    primary_role = models.CharField(
        max_length=200,
        help_text="Primary professional role (e.g., CEO, Software Engineer, PhD Student)",
        blank=True
    )
    secondary_roles = models.JSONField(
        default=list,
        help_text="Additional roles and responsibilities"
    )
    long_term_goals = models.JSONField(
        default=list,
        help_text="Major life/career goals with target dates"
    )
    current_projects = models.JSONField(
        default=list,
        help_text="Active projects with priority levels and deadlines"
    )
    quarterly_objectives = models.JSONField(
        default=dict,
        help_text="OKRs or quarterly goals"
    )

    # ========== 2. COMMUNICATION & DECISION PREFERENCES ==========
    communication_style = models.CharField(
        max_length=50,
        choices=[
            ('concise', 'Concise - Brief and to the point'),
            ('detailed', 'Detailed - Comprehensive information'),
            ('balanced', 'Balanced - Mix based on context'),
            ('visual', 'Visual - Prefer charts and diagrams'),
            ('narrative', 'Narrative - Story-based explanations')
        ],
        default='balanced'
    )

    preferred_channels = models.JSONField(
        default=dict,
        help_text="Preferred communication channels by context (e.g., {urgent: 'phone', updates: 'email'})"
    )

    optimal_meeting_times = models.JSONField(
        default=list,
        help_text="Best times for meetings/calls (e.g., ['9-11am PST', '2-4pm PST'])"
    )

    decision_framework = models.CharField(
        max_length=50,
        choices=[
            ('data_driven', 'Data-Driven - Metrics and analytics focused'),
            ('intuitive', 'Intuitive - Gut feeling and experience'),
            ('collaborative', 'Collaborative - Team consensus'),
            ('analytical', 'Analytical - Pros/cons analysis'),
            ('rapid', 'Rapid - Quick decisions, iterate later')
        ],
        default='analytical'
    )

    delegation_preferences = models.JSONField(
        default=dict,
        help_text="What to delegate vs handle personally"
    )

    # ========== 3. PERSONAL PREFERENCES & ROUTINES ==========
    work_schedule = models.JSONField(
        default=dict,
        help_text="Typical work hours by day of week"
    )

    time_zone = models.CharField(
        max_length=50,
        default='America/Los_Angeles'
    )

    morning_routine = models.TextField(
        blank=True,
        help_text="Morning routine for optimal productivity"
    )

    energy_patterns = models.JSONField(
        default=dict,
        help_text="Energy levels throughout the day (e.g., {morning: 'high', afternoon: 'medium'})"
    )

    dietary_preferences = models.JSONField(
        default=dict,
        help_text="Dietary restrictions, allergies, preferences"
    )

    travel_preferences = models.JSONField(
        default=dict,
        help_text="Travel hubs, airline preferences, hotel chains, etc."
    )

    personal_values = models.JSONField(
        default=list,
        help_text="Core personal values that guide decisions"
    )

    stress_indicators = models.JSONField(
        default=list,
        help_text="Signs of stress and preferred interventions"
    )

    # ========== 4. SKILL LEVELS & LEARNING INTERESTS ==========
    core_competencies = models.JSONField(
        default=dict,
        help_text="Skills with proficiency levels (1-10)"
    )

    learning_style = models.CharField(
        max_length=50,
        choices=[
            ('visual', 'Visual - Images, diagrams, videos'),
            ('auditory', 'Auditory - Lectures, discussions'),
            ('reading', 'Reading/Writing - Text-based'),
            ('kinesthetic', 'Kinesthetic - Hands-on practice'),
            ('mixed', 'Mixed - Combination of styles')
        ],
        default='mixed'
    )

    current_learning_goals = models.JSONField(
        default=list,
        help_text="Skills or topics currently learning"
    )

    knowledge_gaps = models.JSONField(
        default=list,
        help_text="Identified areas for improvement"
    )

    preferred_learning_resources = models.JSONField(
        default=dict,
        help_text="Favorite learning platforms, authors, courses"
    )

    certifications = models.JSONField(
        default=list,
        help_text="Professional certifications with expiry dates"
    )

    # ========== 5. PRIVACY & UPDATE SETTINGS ==========
    privacy_level = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public - Share with all agents'),
            ('professional', 'Professional - Work-related only'),
            ('personal', 'Personal - Close assistants only'),
            ('private', 'Private - Encrypted, user only')
        ],
        default='professional'
    )

    sensitive_topics = models.JSONField(
        default=list,
        help_text="Topics to handle with extra care"
    )

    data_retention_days = models.IntegerField(
        default=90,
        validators=[
            MinValueValidator(7),
            MaxValueValidator(365)
        ],
        help_text="How long to retain interaction history"
    )

    update_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily - High-frequency updates'),
            ('weekly', 'Weekly - Regular check-ins'),
            ('biweekly', 'Bi-weekly - Every two weeks'),
            ('monthly', 'Monthly - Monthly review'),
            ('quarterly', 'Quarterly - Seasonal updates')
        ],
        default='weekly'
    )

    last_profile_review = models.DateTimeField(
        auto_now_add=True,
        help_text="Last time profile was reviewed/updated"
    )

    # ========== ORGANIZATION: STABLE VS DYNAMIC FIELDS ==========
    stable_attributes = models.JSONField(
        default=dict,
        help_text="Rarely changing attributes (personality, core values)"
    )

    dynamic_attributes = models.JSONField(
        default=dict,
        help_text="Frequently changing attributes (current mood, energy)"
    )

    # ========== METADATA & ANALYTICS ==========
    profile_completeness = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(100.0)
        ]
    )

    interaction_count = models.IntegerField(default=0)

    memory_retrieval_stats = models.JSONField(
        default=dict,
        help_text="Statistics on which profile fields are most accessed"
    )

    ai_insights = models.JSONField(
        default=dict,
        help_text="AI-generated insights about user patterns"
    )

    # ========== SESSION 438: SUBSCRIPTION & BILLING ==========
    SUBSCRIPTION_TIERS = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('premium', 'Premium'),
    ]

    SUBSCRIPTION_STATUS = [
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('past_due', 'Past Due'),
        ('trialing', 'Trialing'),
        ('incomplete', 'Incomplete'),
    ]

    subscription_tier = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_TIERS,
        default='free',
        help_text="User's subscription tier"
    )

    stripe_customer_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Stripe customer ID for billing"
    )

    stripe_subscription_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Stripe subscription ID for recurring billing"
    )

    subscription_status = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_STATUS,
        default='active',
        help_text="Current subscription status"
    )

    subscription_started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When subscription started"
    )

    subscription_ends_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When subscription ends (for canceled subscriptions)"
    )

    discord_role_synced = models.BooleanField(
        default=False,
        help_text="Whether Discord role matches subscription tier"
    )

    discord_alerts_enabled = models.BooleanField(
        default=True,
        help_text="Whether to receive Discord opportunity alerts"
    )

    # Usage tracking for tier limits
    daily_task_count = models.IntegerField(
        default=0,
        help_text="Number of agent tasks used today"
    )

    daily_task_reset = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When daily task counter was last reset"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Enhanced User Profile"
        verbose_name_plural = "Enhanced User Profiles"

    def calculate_completeness(self) -> float:
        """Calculate profile completeness percentage.

        Session 457: Removed dietary_preferences and travel_preferences from
        completeness calculation - they're personal assistant prefs, not
        relevant to income-focused profile completion.
        """
        required_fields = [
            'primary_role', 'long_term_goals', 'communication_style',
            'work_schedule', 'core_competencies', 'learning_style'
        ]

        completed = 0
        for field in required_fields:
            value = getattr(self, field, None)
            if value and (not isinstance(value, (list, dict)) or len(value) > 0):
                completed += 1

        # Session 457: Only income-relevant optional fields
        optional_fields = [
            'secondary_roles', 'current_projects', 'quarterly_objectives',
            'certifications'
        ]

        for field in optional_fields:
            value = getattr(self, field, None)
            if value and (not isinstance(value, (list, dict)) or len(value) > 0):
                completed += 0.5

        total_possible = len(required_fields) + (len(optional_fields) * 0.5)
        self.profile_completeness = (completed / total_possible) * 100
        return self.profile_completeness

    def get_context_for_ai(self, context_type: str = 'general') -> dict:
        """
        Get relevant profile context for AI assistants based on context type.

        Args:
            context_type: Type of context needed ('general', 'work', 'personal', 'learning')

        Returns:
            Dictionary with relevant profile information
        """
        base_context = {
            'user_id': self.user_id,
            'primary_role': self.primary_role,
            'communication_style': self.communication_style,
            'decision_framework': self.decision_framework,
            'timezone': self.time_zone
        }

        if context_type == 'work':
            base_context.update({
                'current_projects': self.current_projects,
                'quarterly_objectives': self.quarterly_objectives,
                'work_schedule': self.work_schedule,
                'delegation_preferences': self.delegation_preferences,
                'optimal_meeting_times': self.optimal_meeting_times
            })

        elif context_type == 'personal':
            if self.privacy_level in ['personal', 'public']:
                base_context.update({
                    'personal_values': self.personal_values,
                    'dietary_preferences': self.dietary_preferences,
                    'travel_preferences': self.travel_preferences,
                    'energy_patterns': self.energy_patterns,
                    'stress_indicators': self.stress_indicators
                })

        elif context_type == 'learning':
            base_context.update({
                'learning_style': self.learning_style,
                'current_learning_goals': self.current_learning_goals,
                'knowledge_gaps': self.knowledge_gaps,
                'core_competencies': self.core_competencies,
                'preferred_learning_resources': self.preferred_learning_resources
            })

        else:  # general
            base_context.update({
                'long_term_goals': self.long_term_goals[:3] if self.long_term_goals else [],
                'current_projects': self.current_projects[:2] if self.current_projects else [],
                'core_competencies': list(self.core_competencies.keys())[:5] if self.core_competencies else []
            })

        return base_context

    def track_memory_access(self, field_name: str):
        """Track which fields are accessed for memory optimization."""
        if not self.memory_retrieval_stats:
            self.memory_retrieval_stats = {}

        if field_name not in self.memory_retrieval_stats:
            self.memory_retrieval_stats[field_name] = 0

        self.memory_retrieval_stats[field_name] += 1
        self.save(update_fields=['memory_retrieval_stats'])

    def should_update_profile(self) -> bool:
        """Check if profile needs updating based on frequency setting."""
        from datetime import datetime

        if not self.last_profile_review:
            return True

        days_since_update = (datetime.now().date() - self.last_profile_review.date()).days

        update_intervals = {
            'daily': 1,
            'weekly': 7,
            'biweekly': 14,
            'monthly': 30,
            'quarterly': 90
        }

        return days_since_update >= update_intervals.get(self.update_frequency, 7)

    # ========== SESSION 438: SUBSCRIPTION METHODS ==========
    def get_tier_limits(self) -> dict:
        """Get the limits and features for the user's subscription tier."""
        tier_configs = {
            'free': {
                'daily_tasks': 5,
                'priority_alerts': False,
                'dm_notifications': False,
                'advisor_access': False,
                'custom_workflows': False,
                'discord_role': None,
                'price': 0,
            },
            'pro': {
                'daily_tasks': 50,
                'priority_alerts': True,
                'dm_notifications': True,
                'advisor_access': False,
                'custom_workflows': True,
                'discord_role': 'Pro Member',
                'price': 9.99,
            },
            'premium': {
                'daily_tasks': -1,  # Unlimited
                'priority_alerts': True,
                'dm_notifications': True,
                'advisor_access': True,
                'custom_workflows': True,
                'discord_role': 'Premium Member',
                'price': 29.99,
            },
        }
        return tier_configs.get(self.subscription_tier, tier_configs['free'])

    def can_use_task(self) -> tuple:
        """Check if user can use another agent task today."""
        from django.utils import timezone
        from datetime import timedelta

        limits = self.get_tier_limits()
        daily_limit = limits['daily_tasks']

        # Unlimited for premium
        if daily_limit == -1:
            return True, "Unlimited tasks available"

        # Reset counter if it's a new day
        now = timezone.now()
        if self.daily_task_reset is None or self.daily_task_reset.date() < now.date():
            self.daily_task_count = 0
            self.daily_task_reset = now
            self.save(update_fields=['daily_task_count', 'daily_task_reset'])

        if self.daily_task_count >= daily_limit:
            return False, f"Daily limit of {daily_limit} tasks reached. Upgrade to Pro or Premium for more!"

        return True, f"{daily_limit - self.daily_task_count} tasks remaining today"

    def use_task(self) -> bool:
        """Increment task counter. Returns True if successful."""
        can_use, _ = self.can_use_task()
        if can_use:
            self.daily_task_count += 1
            self.save(update_fields=['daily_task_count'])
            return True
        return False

    def has_feature(self, feature: str) -> bool:
        """Check if user's tier includes a specific feature."""
        limits = self.get_tier_limits()
        return limits.get(feature, False)

    def get_discord_role_name(self):
        """Get the Discord role name for this subscription tier."""
        return self.get_tier_limits().get('discord_role')

    def __str__(self):
        return f"{self.user.username} - {self.primary_role} ({self.profile_completeness:.0f}% complete)"


class UserEmbedding(UnifiedBaseModel):
    """
    Store user-specific knowledge embeddings for personalized AI responses.

    This model creates a learning loop where the system stores and learns
    from user interactions, preferences, and successful patterns.
    """
    CONTENT_TYPES = [
        ('successful_application', 'Successful Application Pattern'),
        ('rejected_application', 'Rejected Application Analysis'),
        ('interview_notes', 'Interview Experience'),
        ('skill_validation', 'Skill Validation Data'),
        ('preference_update', 'User Preference Change'),
        ('success_pattern', 'General Success Pattern'),
        ('failure_pattern', 'Failure Pattern Analysis'),
        ('memory', 'Memory Embedding'),
        ('conversation', 'Conversation Embedding'),
        ('document', 'Document Embedding'),
        ('query', 'Query Embedding'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    # Embedding Data
    embedding_vector = models.JSONField(
        help_text="Vector representation for similarity search",
        default=list
    )
    content = models.TextField(help_text="Original content that was embedded")
    content_type = models.CharField(max_length=30, choices=CONTENT_TYPES)

    # Source tracking
    source = models.CharField(
        max_length=100,
        default='system',
        help_text="Source of embedding (e.g., 'assistant', 'agent:JobMatcher')"
    )

    # Metadata
    metadata = models.JSONField(
        default=dict,
        help_text="Additional metadata for the embedding"
    )
    confidence_score = models.FloatField(
        default=0.5,
        help_text="Confidence in this embedding (0-1)"
    )
    usage_count = models.IntegerField(
        default=0,
        help_text="How many times this embedding has been used"
    )
    last_used = models.DateTimeField(null=True, blank=True)

    # Source Information
    source_application = models.ForeignKey(
        'JobApplication',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Associated job application if applicable"
    )
    source_metadata = models.JSONField(
        default=dict,
        help_text="Additional source information"
    )

    def increment_usage(self):
        """Increment usage counter and update last used."""
        from django.utils import timezone
        self.usage_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=['usage_count', 'last_used'])

    def update_confidence(self, feedback_score):
        """Update confidence based on feedback."""
        # Simple confidence update algorithm
        self.confidence_score = (self.confidence_score + feedback_score) / 2
        self.save(update_fields=['confidence_score'])

    class Meta:
        verbose_name = "User Embedding"
        verbose_name_plural = "User Embeddings"
        indexes = [
            models.Index(fields=['user', 'content_type']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['-last_used']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.content_type} (confidence: {self.confidence_score:.2f})"


class UserPreference(models.Model):
    """
    Key-value store for user preferences.

    Session 309: Created for BrandIdentityAgent brand data persistence.
    Provides flexible storage for agent-specific user settings.

    Usage:
        pref, created = UserPreference.objects.get_or_create(
            user=user,
            key='brand_identity',
            defaults={'value': json.dumps({'primary': '#FF5733'})}
        )
    """
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='user_preferences'  # Note: 'preferences' conflicts with User model
    )
    key = models.CharField(max_length=100, db_index=True)
    value = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_userpreference'
        unique_together = ['user', 'key']
        verbose_name = 'User Preference'
        verbose_name_plural = 'User Preferences'
        indexes = [
            models.Index(fields=['user', 'key']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.key}"


class UserCertification(models.Model):
    """
    Session 457: Store user certifications with file uploads.

    Supports PDF certificates, images, and links to online credentials.
    Each certification can have a file upload and/or a verification URL.
    """
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='certifications'
    )

    # Certificate details
    name = models.CharField(
        max_length=200,
        help_text="Certificate name (e.g., 'AWS Solutions Architect')"
    )
    issuer = models.CharField(
        max_length=200,
        blank=True,
        help_text="Issuing organization (e.g., 'Udemy', 'AWS', 'Google')"
    )
    issue_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date the certificate was issued"
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text="Expiration date (if applicable)"
    )
    credential_id = models.CharField(
        max_length=200,
        blank=True,
        help_text="Credential ID or certificate number"
    )

    # File upload
    certificate_file = models.FileField(
        upload_to='certifications/%Y/%m/',
        blank=True,
        null=True,
        help_text="PDF or image of the certificate"
    )

    # Online verification
    verification_url = models.URLField(
        blank=True,
        help_text="URL to verify the credential online"
    )

    # Metadata
    skills = models.JSONField(
        default=list,
        blank=True,
        help_text="Skills associated with this certification"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_usercertification'
        verbose_name = 'User Certification'
        verbose_name_plural = 'User Certifications'
        ordering = ['-issue_date', '-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.name} ({self.issuer})"

    def get_file_url(self):
        """Get the certificate file URL."""
        if self.certificate_file:
            return self.certificate_file.url
        return None


# Signal handlers to create profile and statistics when user is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=get_user_model())
def create_user_profile_and_stats(sender, instance, created, **kwargs):
    """Create UserProfile, ExtendedUserProfile, and UserStatistics when a new user is created."""
    if created:
        UserProfile.objects.create(user=instance)
        UserStatistics.objects.create(user=instance)
        ExtendedUserProfile.objects.create(user=instance)
    else:
        # Ensure profile and stats exist for existing users
        UserProfile.objects.get_or_create(user=instance)
        UserStatistics.objects.get_or_create(user=instance)
        ExtendedUserProfile.objects.get_or_create(user=instance)