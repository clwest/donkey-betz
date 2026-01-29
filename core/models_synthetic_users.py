# Session 862: Synthetic User Profiles for System Testing
# These profiles simulate diverse user types to test agent recommendations
# before real users see them.

import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class SyntheticUserProfile(models.Model):
    """
    Synthetic user profile for testing agent recommendations.
    Mirrors real UserProfile/EnhancedUserProfile structure so agents
    treat synthetic users identically to real users.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Identity
    name = models.CharField(max_length=100, help_text="Synthetic user display name")
    archetype = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Persona archetype (e.g., 'career_pivoter', 'new_grad', 'freelancer')"
    )
    description = models.TextField(
        blank=True,
        help_text="Human-readable description of this persona"
    )

    # Demographics
    age_bracket = models.CharField(
        max_length=20,
        choices=[
            ('18-24', '18-24'),
            ('25-34', '25-34'),
            ('35-44', '35-44'),
            ('45-54', '45-54'),
            ('55-64', '55-64'),
            ('65+', '65+'),
        ],
        default='25-34'
    )
    location = models.CharField(max_length=100, default="United States")
    income_bracket = models.CharField(
        max_length=30,
        choices=[
            ('under_25k', 'Under $25,000'),
            ('25k_50k', '$25,000 - $50,000'),
            ('50k_75k', '$50,000 - $75,000'),
            ('75k_100k', '$75,000 - $100,000'),
            ('100k_150k', '$100,000 - $150,000'),
            ('150k_200k', '$150,000 - $200,000'),
            ('over_200k', 'Over $200,000'),
        ],
        default='50k_75k'
    )

    # Career Profile (mirrors UserProfile)
    occupation = models.CharField(max_length=200, blank=True)
    current_role = models.CharField(max_length=200, blank=True)
    experience_years = models.IntegerField(default=0)
    skills = models.JSONField(
        default=list,
        help_text="List of skills (e.g., ['Python', 'SQL', 'Project Management'])"
    )
    industries = models.JSONField(
        default=list,
        help_text="Industries of experience (e.g., ['Technology', 'Finance'])"
    )
    education_level = models.CharField(
        max_length=50,
        choices=[
            ('high_school', 'High School'),
            ('some_college', 'Some College'),
            ('associates', 'Associate Degree'),
            ('bachelors', 'Bachelor\'s Degree'),
            ('masters', 'Master\'s Degree'),
            ('phd', 'PhD/Doctorate'),
            ('bootcamp', 'Bootcamp/Certification'),
        ],
        default='bachelors'
    )

    # Work Preferences (mirrors UserProfile)
    remote_only = models.BooleanField(default=False)
    contract_work = models.BooleanField(default=True)
    full_time = models.BooleanField(default=True)
    part_time = models.BooleanField(default=False)
    hourly_rate_min = models.IntegerField(null=True, blank=True, help_text="Minimum hourly rate")
    salary_min = models.IntegerField(null=True, blank=True, help_text="Minimum salary expectation")

    # Goals & Motivations (mirrors EnhancedUserProfile)
    primary_goal = models.CharField(
        max_length=50,
        choices=[
            ('find_job', 'Find a New Job'),
            ('increase_income', 'Increase Income'),
            ('career_change', 'Change Careers'),
            ('start_freelancing', 'Start Freelancing'),
            ('build_passive_income', 'Build Passive Income'),
            ('learn_new_skills', 'Learn New Skills'),
            ('start_business', 'Start a Business'),
            ('work_life_balance', 'Improve Work-Life Balance'),
        ],
        default='find_job'
    )
    secondary_goals = models.JSONField(default=list, help_text="Additional goals")
    income_target = models.IntegerField(null=True, blank=True, help_text="Target annual income")
    timeline = models.CharField(
        max_length=30,
        choices=[
            ('immediate', 'Immediate (0-1 month)'),
            ('short_term', 'Short-term (1-3 months)'),
            ('medium_term', 'Medium-term (3-6 months)'),
            ('long_term', 'Long-term (6-12 months)'),
            ('exploratory', 'Exploratory (no timeline)'),
        ],
        default='short_term'
    )

    # Behavioral Patterns
    engagement_level = models.CharField(
        max_length=20,
        choices=[
            ('passive', 'Passive - Just browsing'),
            ('moderate', 'Moderate - Occasionally engages'),
            ('active', 'Active - Regularly engages'),
            ('power_user', 'Power User - Daily engagement'),
        ],
        default='moderate'
    )
    decision_style = models.CharField(
        max_length=20,
        choices=[
            ('impulsive', 'Impulsive - Quick decisions'),
            ('deliberate', 'Deliberate - Careful analysis'),
            ('collaborative', 'Collaborative - Seeks input'),
            ('risk_averse', 'Risk-Averse - Very cautious'),
        ],
        default='deliberate'
    )
    tech_comfort = models.CharField(
        max_length=20,
        choices=[
            ('novice', 'Novice'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
            ('expert', 'Expert'),
        ],
        default='intermediate'
    )

    # Constraints & Context
    constraints = models.JSONField(
        default=dict,
        help_text="Constraints like location restrictions, visa status, availability"
    )
    context = models.JSONField(
        default=dict,
        help_text="Additional context (family situation, health, etc.)"
    )

    # Expected Outcomes (for validation)
    expected_recommendations = models.JSONField(
        default=list,
        help_text="Types of recommendations this persona should receive"
    )
    expected_agents = models.JSONField(
        default=list,
        help_text="Agents that should be particularly relevant for this persona"
    )
    success_criteria = models.JSONField(
        default=dict,
        help_text="Criteria for evaluating recommendation quality"
    )

    # Test Metadata
    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.CharField(
        max_length=50,
        default='system',
        help_text="Who created this persona (system, manual, generated)"
    )
    generation_seed = models.CharField(
        max_length=100,
        blank=True,
        help_text="Seed used if this was randomly generated"
    )

    # Usage Tracking
    times_used = models.IntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    test_results = models.JSONField(
        default=list,
        help_text="History of test results for this persona"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_synthetic_user_profile'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['archetype', 'is_active']),
            models.Index(fields=['primary_goal', 'is_active']),
            models.Index(fields=['experience_years', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.archetype})"

    def to_user_context(self) -> dict:
        """
        Convert to user context dict that agents expect.
        Matches the format from Session 858 user context injection.
        """
        return {
            'user_id': str(self.id),
            'is_synthetic': True,
            'display_name': self.name,
            'occupation': self.occupation,
            'current_role': self.current_role,
            'experience_years': self.experience_years,
            'skills': self.skills,
            'industries': self.industries,
            'location': self.location,
            'remote_only': self.remote_only,
            'contract_work': self.contract_work,
            'full_time': self.full_time,
            'part_time': self.part_time,
            'hourly_rate_min': self.hourly_rate_min,
            'salary_min': self.salary_min,
            'goals': {
                'primary': self.primary_goal,
                'secondary': self.secondary_goals,
                'income_target': self.income_target,
                'timeline': self.timeline,
            },
            'preferences': {
                'engagement_level': self.engagement_level,
                'decision_style': self.decision_style,
                'tech_comfort': self.tech_comfort,
            },
            'constraints': self.constraints,
            'context': self.context,
            'archetype': self.archetype,
            'description': self.description,
        }

    def record_test_result(self, result: dict):
        """Record a test result for this persona."""
        from django.utils import timezone

        self.times_used += 1
        self.last_used_at = timezone.now()

        # Append to test results (keep last 100)
        self.test_results.append({
            'timestamp': timezone.now().isoformat(),
            **result
        })
        if len(self.test_results) > 100:
            self.test_results = self.test_results[-100:]

        self.save(update_fields=['times_used', 'last_used_at', 'test_results', 'updated_at'])


class SyntheticUserTestRun(models.Model):
    """
    Records a test run using synthetic users.
    Tracks which personas were used and aggregate results.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Test Configuration
    name = models.CharField(max_length=200, help_text="Test run name/description")
    test_type = models.CharField(
        max_length=50,
        choices=[
            ('agent_validation', 'Agent Validation'),
            ('recommendation_quality', 'Recommendation Quality'),
            ('coverage_test', 'Coverage Test'),
            ('regression_test', 'Regression Test'),
            ('a_b_test', 'A/B Test'),
        ],
        default='agent_validation'
    )

    # What was tested
    agents_tested = models.JSONField(default=list, help_text="List of agent names that were tested")
    personas_used = models.ManyToManyField(
        SyntheticUserProfile,
        related_name='test_runs',
        blank=True
    )

    # Results
    total_executions = models.IntegerField(default=0)
    successful_executions = models.IntegerField(default=0)
    failed_executions = models.IntegerField(default=0)

    # Quality Metrics
    avg_relevance_score = models.FloatField(null=True, blank=True)
    avg_quality_score = models.FloatField(null=True, blank=True)
    coverage_percentage = models.FloatField(null=True, blank=True)

    # Detailed Results
    results = models.JSONField(default=dict, help_text="Detailed results by persona and agent")
    issues_found = models.JSONField(default=list, help_text="Issues or anomalies discovered")
    recommendations = models.JSONField(default=list, help_text="Recommendations for improvement")

    # Metadata
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    triggered_by = models.CharField(
        max_length=50,
        default='manual',
        choices=[
            ('manual', 'Manual'),
            ('scheduled', 'Scheduled'),
            ('ci_cd', 'CI/CD Pipeline'),
            ('pre_deploy', 'Pre-Deployment'),
        ]
    )

    class Meta:
        db_table = 'core_synthetic_user_test_run'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.name} ({self.test_type}) - {self.started_at.strftime('%Y-%m-%d')}"
