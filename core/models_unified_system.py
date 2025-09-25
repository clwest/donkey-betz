"""
Unified System Models - The Complete AI Ecosystem
These models represent ALL agents, advisors, and system components
"""

from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from decimal import Decimal
import json
import uuid
from datetime import datetime

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

    def __str__(self):
        return f"{self.title} - ${self.potential_revenue}"

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