"""
Unified Agent Registry Models

This module provides the comprehensive agent registry system for the Unified Donkey Betz Platform.
It consolidates and enhances agent management from the donkey-betz-agent-orchestra into a
unified, scalable, and self-aware agent system.

Features:
- Unified agent templates with rich metadata
- Cross-domain capabilities (sports, content, orchestration)
- Version control and capability mapping
- Execution tracking and performance metrics
- Real-time status monitoring
- Self-aware registry system
"""

import uuid
import json
from decimal import Decimal
from enum import Enum

from django.db import models
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from core.models import UnifiedBaseModel


User = get_user_model()


class AgentSpecialization(models.TextChoices):
    """Agent specialization categories"""
    # Original categories
    RESEARCH = 'research', 'Research & Analysis'
    CONTENT = 'content', 'Content Creation'
    BUSINESS = 'business', 'Business Development'
    CAREER = 'career', 'Career Development'
    TECHNICAL = 'technical', 'Technical Analysis'
    CREATIVE = 'creative', 'Creative Design'
    MARKETING = 'marketing', 'Marketing & Growth'
    FINANCIAL = 'financial', 'Financial Analysis'
    LEGAL = 'legal', 'Legal & Compliance'
    COMMUNICATION = 'communication', 'Communication & Outreach'
    
    # Sports & Betting Intelligence
    SPORTS_ANALYTICS = 'sports-analytics', 'Sports Analytics & Betting Intelligence'
    ODDS_CALCULATION = 'odds-calculation', 'Odds Calculation & Betting Mathematics'
    RISK_ASSESSMENT = 'risk-assessment', 'Risk Assessment & Management'
    
    # Advanced Analytics
    IMPLEMENTATION = 'implementation', 'Implementation & Deployment'
    TOKEN_BUDGET = 'token-budget', 'Token Budget & Context Optimization'
    RAG_DIAGNOSTICS = 'rag-diagnostics', 'RAG Diagnostics & Grounding Optimization'
    
    # Specialized Orchestration
    GLOSSARY_ANCHOR_CURATOR = 'glossary-anchor-curator', 'Glossary Anchor Curation & RAG Optimization'
    MEMORY_BRIDGE_COORDINATOR = 'memory-bridge-coordinator', 'Memory Bridge Coordination & Context Management'
    CORE_AGENTS_ENABLEMENT = 'core-agents-enablement-coordinator', 'Core Agents Enablement Coordinator'
    
    # Advanced AI Agents
    NARRATIVE_PREDICTOR = 'narrative-predictor-agent', 'Narrative Predictor Agent'
    EMPIRE_BUILDER = 'empire-builder-orchestrator', 'Empire Builder Orchestrator'
    CORRELATION_HUNTER = 'correlation-hunter', 'Correlation Hunter'
    SHIT_TALKER = 'shit-talker', 'Shit Talker & Motivational Combat Agent'
    KNOWLEDGE_EVOLUTION = 'autonomous-knowledge-evolution-engine', 'Autonomous Knowledge Evolution Engine'
    
    # Meta-orchestration
    ORCHESTRATION = 'orchestration', 'Multi-Agent Orchestration'
    SELF_AWARENESS = 'self-awareness', 'Self-Awareness & Introspection'


class LLMProvider(models.TextChoices):
    """Supported LLM providers"""
    OPENAI = 'openai', 'OpenAI'
    ANTHROPIC = 'anthropic', 'Anthropic'
    GOOGLE = 'google', 'Google AI'
    AZURE = 'azure', 'Azure OpenAI'
    LOCAL = 'local', 'Local Model'


class AgentStatus(models.TextChoices):
    """Agent execution status"""
    PENDING = 'pending', 'Pending'
    INITIALIZING = 'initializing', 'Initializing'
    RUNNING = 'running', 'Running'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'
    PAUSED = 'paused', 'Paused'


class AgentPriority(models.TextChoices):
    """Agent execution priority"""
    LOW = 'low', 'Low Priority'
    NORMAL = 'normal', 'Normal Priority'
    HIGH = 'high', 'High Priority'
    URGENT = 'urgent', 'Urgent Priority'
    CRITICAL = 'critical', 'Critical Priority'


class UnifiedAgentTemplate(UnifiedBaseModel):
    """
    Unified agent template that consolidates all agent types into a single,
    flexible model suitable for sports, content, and orchestration domains.
    """
    
    # Basic identification
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Unique agent name"
    )
    
    display_name = models.CharField(
        max_length=250,
        blank=True,
        help_text="Human-friendly display name"
    )
    
    description = models.TextField(
        help_text="Detailed agent description and purpose"
    )
    
    specialization = models.CharField(
        max_length=100,
        choices=AgentSpecialization.choices,
        help_text="Primary specialization area"
    )
    
    # Agent capabilities and configuration
    capabilities = models.JSONField(
        default=list,
        help_text="List of specific capabilities this agent provides"
    )
    
    required_tools = models.JSONField(
        default=list,
        help_text="Tools required for this agent to function"
    )
    
    optional_tools = models.JSONField(
        default=list,
        help_text="Optional tools that enhance agent performance"
    )
    
    # AI model configuration
    system_prompt = models.TextField(
        help_text="System prompt that defines agent behavior and personality"
    )
    
    personality_traits = models.JSONField(
        default=dict,
        help_text="Personality configuration (style, tone, detail_level, etc.)"
    )
    
    llm_provider = models.CharField(
        max_length=50,
        choices=LLMProvider.choices,
        default=LLMProvider.OPENAI,
        help_text="Primary LLM provider"
    )
    
    llm_model = models.CharField(
        max_length=100,
        default='gpt-5-mini',
        help_text="Specific model name"
    )
    
    llm_config = models.JSONField(
        default=dict,
        help_text="LLM configuration (temperature, max_tokens, etc.)"
    )

    # Tool integrations - NEW ENHANCEMENT!
    tool_integrations = models.JSONField(
        default=dict,
        help_text="""Tool integration configuration:
        {
            "web_search": {"enabled": true, "provider": "serper", "max_results": 10},
            "api_calls": {"enabled": true, "allowed_apis": ["openai", "serper"]},
            "data_access": {"spider_data": true, "learning_context": true},
            "content_generation": {"types": ["blog", "social"], "max_length": 5000}
        }"""
    )

    fallback_provider = models.CharField(
        max_length=50,
        choices=LLMProvider.choices,
        blank=True,
        null=True,
        help_text="Fallback LLM provider if primary fails"
    )
    
    fallback_model = models.CharField(
        max_length=100,
        blank=True,
        help_text="Fallback model name"
    )
    
    # Routing and discovery
    routing_keywords = models.JSONField(
        default=list,
        help_text="Keywords used for intelligent agent routing"
    )
    
    routing_patterns = models.JSONField(
        default=list,
        help_text="Regex patterns for advanced routing"
    )
    
    domain_tags = models.JSONField(
        default=list,
        help_text="Domain tags (sports, content, orchestration, etc.)"
    )
    
    # Performance metrics
    confidence_score = models.FloatField(
        default=0.5,
        help_text="Base confidence score for routing decisions"
    )
    
    avg_completion_time = models.IntegerField(
        default=300,
        help_text="Average completion time in seconds"
    )
    
    success_rate = models.FloatField(
        default=0.95,
        help_text="Success rate percentage (0-1)"
    )
    
    usage_count = models.PositiveIntegerField(
        default=0,
        help_text="Total number of times agent has been used"
    )
    
    avg_user_rating = models.FloatField(
        default=0.0,
        help_text="Average user rating (0-5)"
    )
    
    # Cost and resource management
    estimated_cost_per_execution = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        default=Decimal('0.000000'),
        help_text="Estimated cost per execution in USD"
    )
    
    avg_token_usage = models.JSONField(
        default=dict,
        help_text="Average token usage statistics"
    )
    
    resource_requirements = models.JSONField(
        default=dict,
        help_text="Compute and memory requirements"
    )
    
    # Version control and lifecycle
    agent_version = models.CharField(
        max_length=20,
        default='1.0.0',
        help_text="Semantic version number"
    )
    
    parent_template = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='child_templates',
        help_text="Parent template if this is a derived agent"
    )
    
    is_template = models.BooleanField(
        default=True,
        help_text="Whether this is a template or instance"
    )
    
    is_public = models.BooleanField(
        default=True,
        help_text="Whether this agent is available in the marketplace"
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether this agent has been verified/approved"
    )
    
    # Advanced features
    supports_streaming = models.BooleanField(
        default=False,
        help_text="Whether agent supports streaming responses"
    )
    
    supports_interruption = models.BooleanField(
        default=False,
        help_text="Whether agent execution can be interrupted"
    )
    
    supports_collaboration = models.BooleanField(
        default=False,
        help_text="Whether agent can work with other agents"
    )
    
    max_concurrent_executions = models.PositiveIntegerField(
        default=1,
        help_text="Maximum concurrent executions allowed"
    )
    
    # Self-awareness and learning
    learning_enabled = models.BooleanField(
        default=False,
        help_text="Whether agent can learn from executions"
    )
    
    self_improvement_enabled = models.BooleanField(
        default=False,
        help_text="Whether agent can modify itself"
    )
    
    collaboration_history = models.JSONField(
        default=list,
        help_text="History of successful collaborations with other agents"
    )
    
    # Creator and ownership
    creator = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_agent_templates'
    )
    
    organization = models.CharField(
        max_length=200,
        blank=True,
        help_text="Organization that owns this agent"
    )
    
    class Meta:
        verbose_name = "Unified Agent Template"
        verbose_name_plural = "Unified Agent Templates"
        ordering = ['-usage_count', 'name']
        indexes = [
            models.Index(fields=['specialization']),
            models.Index(fields=['llm_provider']),
            models.Index(fields=['is_active']),
            models.Index(fields=['usage_count']),
            models.Index(fields=['success_rate']),
        ]
    
    def __str__(self):
        return f"{self.display_name or self.name} ({self.specialization})"
    
    def clean(self):
        """Validate agent template"""
        if not self.capabilities:
            raise ValidationError("Agent must have at least one capability")
        
        if not self.system_prompt.strip():
            raise ValidationError("System prompt cannot be empty")
    
    def get_capability_tags(self):
        """Get capability tags for search and filtering"""
        tags = set(self.capabilities)
        tags.add(self.specialization)
        tags.update(self.domain_tags)
        tags.update(self.routing_keywords)
        return list(tags)
    
    def update_metrics(self, execution_time=None, success=True, cost=None, tokens=None, rating=None):
        """Update agent performance metrics"""
        self.usage_count += 1
        
        if execution_time is not None:
            # Update average completion time
            total_time = self.avg_completion_time * (self.usage_count - 1) + execution_time
            self.avg_completion_time = int(total_time / self.usage_count)
        
        if success is not None:
            # Update success rate
            total_success = self.success_rate * (self.usage_count - 1) + (1 if success else 0)
            self.success_rate = total_success / self.usage_count
        
        if cost is not None:
            # Update average cost
            total_cost = self.estimated_cost_per_execution * (self.usage_count - 1) + cost
            self.estimated_cost_per_execution = total_cost / self.usage_count
        
        if tokens is not None:
            # Update token usage statistics
            if not self.avg_token_usage:
                self.avg_token_usage = tokens
            else:
                for key, value in tokens.items():
                    if key in self.avg_token_usage:
                        total = self.avg_token_usage[key] * (self.usage_count - 1) + value
                        self.avg_token_usage[key] = int(total / self.usage_count)
                    else:
                        self.avg_token_usage[key] = value
        
        if rating is not None:
            # Update average rating
            total_rating = self.avg_user_rating * (self.usage_count - 1) + rating
            self.avg_user_rating = total_rating / self.usage_count
        
        self.save()
    
    def can_handle_task(self, task_description, required_capabilities=None):
        """Check if agent can handle a specific task"""
        if not self.is_active:
            return False, "Agent is not active"
        
        if required_capabilities:
            missing_capabilities = set(required_capabilities) - set(self.capabilities)
            if missing_capabilities:
                return False, f"Missing capabilities: {', '.join(missing_capabilities)}"
        
        # Check keywords in task description
        task_lower = task_description.lower()
        keyword_matches = sum(1 for keyword in self.routing_keywords if keyword.lower() in task_lower)
        
        if keyword_matches == 0 and self.routing_keywords:
            return False, "No routing keyword matches"
        
        return True, f"Confidence: {self.confidence_score}, Keywords: {keyword_matches}"


class AgentExecution(UnifiedBaseModel):
    """
    Individual agent execution instance with comprehensive tracking
    """
    
    # Execution identification
    template = models.ForeignKey(
        UnifiedAgentTemplate,
        on_delete=models.CASCADE,
        related_name='executions'
    )
    
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='agent_executions'
    )
    
    execution_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="Human-readable execution identifier"
    )
    
    # Task definition
    task_description = models.TextField(
        help_text="Description of the task to be performed"
    )
    
    task_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="Categorization of task type"
    )
    
    context = models.JSONField(
        default=dict,
        help_text="Additional context and parameters for execution"
    )
    
    input_data = models.JSONField(
        default=dict,
        help_text="Input data provided to the agent"
    )
    
    # Execution status and progress
    status = models.CharField(
        max_length=20,
        choices=AgentStatus.choices,
        default=AgentStatus.PENDING
    )
    
    priority = models.CharField(
        max_length=20,
        choices=AgentPriority.choices,
        default=AgentPriority.NORMAL
    )
    
    progress_percentage = models.IntegerField(
        default=0,
        help_text="Completion progress (0-100)"
    )
    
    current_step = models.CharField(
        max_length=500,
        blank=True,
        help_text="Description of current execution step"
    )
    
    steps_completed = models.JSONField(
        default=list,
        help_text="List of completed steps"
    )
    
    estimated_completion_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Estimated completion time"
    )
    
    # Results and output
    result = models.JSONField(
        null=True,
        blank=True,
        help_text="Execution result data"
    )
    
    output_data = models.JSONField(
        default=dict,
        help_text="Structured output data from agent execution"
    )
    
    llm_response = models.TextField(
        blank=True,
        help_text="Raw response from the LLM"
    )
    
    output_files = models.JSONField(
        default=list,
        help_text="List of generated output files"
    )
    
    error_message = models.TextField(
        blank=True,
        help_text="Error message if execution failed"
    )
    
    error_details = models.JSONField(
        null=True,
        blank=True,
        help_text="Detailed error information"
    )
    
    warnings = models.JSONField(
        default=list,
        help_text="Non-critical warnings during execution"
    )
    
    # Timing and performance
    started_at = models.DateTimeField(
        null=True,
        blank=True
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )
    
    execution_time_seconds = models.IntegerField(
        null=True,
        blank=True,
        help_text="Total execution time in seconds"
    )
    
    # Resource usage
    token_usage = models.JSONField(
        default=dict,
        help_text="Token usage statistics (input, output, total)"
    )
    
    cost_breakdown = models.JSONField(
        default=dict,
        help_text="Detailed cost breakdown"
    )
    
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        default=Decimal('0.000000')
    )
    
    memory_usage_mb = models.FloatField(
        null=True,
        blank=True,
        help_text="Peak memory usage in MB"
    )
    
    # Quality and feedback
    user_rating = models.IntegerField(
        null=True,
        blank=True,
        help_text="User rating (1-5)"
    )
    
    user_feedback = models.TextField(
        blank=True,
        help_text="User feedback on execution quality"
    )
    
    quality_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Automated quality assessment score"
    )
    
    # Orchestration and collaboration
    parent_orchestration = models.ForeignKey(
        'AgentOrchestration',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='agent_executions'
    )
    
    collaboration_context = models.JSONField(
        default=dict,
        help_text="Context for multi-agent collaboration"
    )
    
    # WebSocket and real-time updates
    websocket_channel = models.CharField(
        max_length=255,
        blank=True,
        help_text="WebSocket channel for real-time updates"
    )
    
    class Meta:
        verbose_name = "Agent Execution"
        verbose_name_plural = "Agent Executions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['started_at']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.template.name} - {self.execution_id} ({self.status})"
    
    def save(self, *args, **kwargs):
        if not self.execution_id:
            # Generate human-readable execution ID
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            short_uuid = str(uuid.uuid4())[:8]
            self.execution_id = f"{self.template.name.lower()}_{timestamp}_{short_uuid}"
        
        super().save(*args, **kwargs)
    
    def start_execution(self):
        """Mark execution as started"""
        self.status = AgentStatus.RUNNING
        self.started_at = timezone.now()
        self.save()
    
    def complete_execution(self, result=None, output_files=None):
        """Mark execution as completed"""
        self.status = AgentStatus.COMPLETED
        self.completed_at = timezone.now()
        self.progress_percentage = 100
        
        if result is not None:
            self.result = result
        
        if output_files:
            self.output_files = output_files
        
        if self.started_at:
            self.execution_time_seconds = int((self.completed_at - self.started_at).total_seconds())
        
        self.save()
        
        # Update template metrics
        self.template.update_metrics(
            execution_time=self.execution_time_seconds,
            success=True,
            cost=self.total_cost,
            tokens=self.token_usage,
            rating=self.user_rating
        )
    
    def fail_execution(self, error_message, error_details=None):
        """Mark execution as failed"""
        self.status = AgentStatus.FAILED
        self.error_message = error_message
        self.completed_at = timezone.now()
        
        if error_details:
            self.error_details = error_details
        
        if self.started_at:
            self.execution_time_seconds = int((self.completed_at - self.started_at).total_seconds())
        
        self.save()
        
        # Update template metrics
        self.template.update_metrics(
            execution_time=self.execution_time_seconds,
            success=False
        )
    
    def update_progress(self, percentage, step_description=None):
        """Update execution progress"""
        self.progress_percentage = min(100, max(0, percentage))
        
        if step_description:
            self.current_step = step_description
            if step_description not in self.steps_completed:
                self.steps_completed.append({
                    'step': step_description,
                    'completed_at': timezone.now().isoformat(),
                    'progress': percentage
                })
        
        self.save()


class AgentContribution(UnifiedBaseModel):
    """
    Session 120: Track which agents contributed to which content/project.

    Supports both simple single-agent tracking and complex multi-agent
    collaboration workflows.
    """

    # Agent reference
    agent = models.ForeignKey(
        UnifiedAgentTemplate,
        on_delete=models.CASCADE,
        related_name='contributions',
        help_text="Agent that made this contribution"
    )

    # Project reference (always required)
    # Session 324: Unified from CreativeProject
    project = models.ForeignKey(
        'core.PartnershipProject',
        on_delete=models.CASCADE,
        related_name='agent_contributions',
        help_text="Project this contribution belongs to"
    )

    # Optional: Link to specific content (one of these)
    image = models.ForeignKey(
        'content.ImageHistory',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='agent_contributions',
        help_text="Image created/edited by agent"
    )

    video = models.ForeignKey(
        'content.VideoHistory',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='agent_contributions',
        help_text="Video created/edited by agent"
    )

    minifig_asset = models.ForeignKey(
        'content.MiniFigAsset',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='agent_contributions',
        help_text="3D model created by agent"
    )

    # NOTE: AudioHistory model pending implementation in content app
    # audio = models.ForeignKey(
    #     'content.AudioHistory',
    #     null=True,
    #     blank=True,
    #     on_delete=models.CASCADE,
    #     related_name='agent_contributions',
    #     help_text="Audio created/edited by agent"
    # )

    # Contribution details
    CONTRIBUTION_TYPES = [
        ('generation', 'Content Generation'),
        ('editing', 'Editing/Enhancement'),
        ('orchestration', 'Workflow Orchestration'),
        ('analysis', 'Analysis/Planning'),
        ('recommendation', 'Recommendation'),
        ('iteration', 'Iterative Improvement'),
    ]

    contribution_type = models.CharField(
        max_length=50,
        choices=CONTRIBUTION_TYPES,
        default='generation',
        help_text="Type of contribution"
    )

    contribution_role = models.CharField(
        max_length=100,
        default="Primary Creator",
        help_text="Role in creation process"
    )

    contribution_percentage = models.IntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Contribution percentage (0-100)"
    )

    # Execution tracking
    execution = models.ForeignKey(
        AgentExecution,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='content_contributions',
        help_text="Link to agent execution record"
    )

    task_description = models.TextField(
        blank=True,
        help_text="Description of what agent did"
    )

    # Performance metrics
    execution_time_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Execution time in seconds"
    )

    tokens_used = models.IntegerField(
        null=True,
        blank=True,
        help_text="AI tokens consumed"
    )

    # User feedback (optional)
    user_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="User rating (1-5 stars)"
    )

    user_selected = models.BooleanField(
        default=False,
        help_text="True if user selected this agent's output as favorite"
    )

    class Meta:
        db_table = 'agent_contributions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', '-created_at']),
            models.Index(fields=['agent', '-created_at']),
            models.Index(fields=['contribution_type']),
        ]
        verbose_name = "Agent Contribution"
        verbose_name_plural = "Agent Contributions"

    def __str__(self):
        content_type = "project"
        if self.image:
            content_type = f"image #{self.image.get_sequential_number()}"
        elif self.video:
            content_type = f"video #{self.video.get_sequential_number()}"
        elif self.minifig_asset:
            content_type = f"3D model #{self.minifig_asset.id}"
        # elif self.audio:  # NOTE: Enable when AudioHistory model is created
        #     content_type = f"audio #{self.audio.id}"

        return f"{self.agent.display_name} → {content_type} ({self.contribution_type})"

    @property
    def content_reference(self):
        """Get reference to the content item"""
        if self.image:
            return {'type': 'image', 'id': str(self.image.id), 'number': self.image.get_sequential_number()}
        elif self.video:
            return {'type': 'video', 'id': str(self.video.id), 'number': self.video.get_sequential_number()}
        elif self.minifig_asset:
            return {'type': '3d_model', 'id': str(self.minifig_asset.id)}
        # elif self.audio:  # NOTE: Enable when AudioHistory model is created
        #     return {'type': 'audio', 'id': str(self.audio.id)}
        return {'type': 'project', 'id': str(self.project.id)}


class AgentOrchestration(UnifiedBaseModel):
    """
    Multi-agent orchestration for complex tasks requiring multiple agents
    """
    
    # Basic orchestration info
    name = models.CharField(
        max_length=200,
        help_text="Human-readable orchestration name"
    )
    
    description = models.TextField(
        help_text="Description of the orchestration workflow"
    )
    
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='orchestrations'
    )
    
    # Orchestration definition
    workflow_definition = models.JSONField(
        help_text="Complete workflow definition with steps and dependencies"
    )
    
    agent_sequence = models.JSONField(
        default=list,
        help_text="Ordered sequence of agents to execute"
    )
    
    execution_strategy = models.CharField(
        max_length=50,
        choices=[
            ('sequential', 'Sequential Execution'),
            ('parallel', 'Parallel Execution'),
            ('conditional', 'Conditional Execution'),
            ('adaptive', 'Adaptive Execution'),
        ],
        default='sequential'
    )
    
    # Status and progress
    status = models.CharField(
        max_length=20,
        choices=AgentStatus.choices,
        default=AgentStatus.PENDING
    )
    
    current_agent_index = models.IntegerField(
        default=0,
        help_text="Index of currently executing agent"
    )
    
    progress_percentage = models.IntegerField(
        default=0
    )
    
    # Results aggregation
    intermediate_results = models.JSONField(
        default=list,
        help_text="Results from each agent in the orchestration"
    )
    
    final_result = models.JSONField(
        null=True,
        blank=True,
        help_text="Aggregated final result"
    )
    
    # Performance tracking
    total_execution_time = models.IntegerField(
        null=True,
        blank=True,
        help_text="Total orchestration time in seconds"
    )
    
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=Decimal('0.000000')
    )
    
    # WebSocket and real-time updates
    websocket_channel = models.CharField(
        max_length=255,
        blank=True,
        help_text="WebSocket channel for orchestration updates"
    )
    
    class Meta:
        verbose_name = "Agent Orchestration"
        verbose_name_plural = "Agent Orchestrations"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.status} ({len(self.agent_sequence)} agents)"
    
    def get_current_agent(self):
        """Get the currently executing agent template"""
        if self.current_agent_index < len(self.agent_sequence):
            agent_name = self.agent_sequence[self.current_agent_index]
            try:
                return UnifiedAgentTemplate.objects.get(name=agent_name, is_active=True)
            except UnifiedAgentTemplate.DoesNotExist:
                return None
        return None
    
    def advance_to_next_agent(self):
        """Advance to next agent in sequence"""
        self.current_agent_index += 1
        if self.current_agent_index >= len(self.agent_sequence):
            self.status = AgentStatus.COMPLETED
            self.progress_percentage = 100
        else:
            self.progress_percentage = int((self.current_agent_index / len(self.agent_sequence)) * 100)
        self.save()


class AgentTool(UnifiedBaseModel):
    """
    Tools and integrations available to agents
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique tool name"
    )
    
    display_name = models.CharField(
        max_length=150,
        help_text="Human-friendly display name"
    )
    
    description = models.TextField(
        help_text="Tool description and capabilities"
    )
    
    tool_type = models.CharField(
        max_length=50,
        choices=[
            ('api', 'API Integration'),
            ('computation', 'Computation Tool'),
            ('data_processing', 'Data Processing'),
            ('communication', 'Communication Tool'),
            ('content_generation', 'Content Generation'),
            ('analysis', 'Analysis Tool'),
            ('monitoring', 'Monitoring Tool'),
            ('integration', 'System Integration'),
        ],
        help_text="Category of tool"
    )
    
    # Configuration
    endpoint_url = models.URLField(
        blank=True,
        help_text="Primary endpoint URL if applicable"
    )
    
    authentication_config = models.JSONField(
        default=dict,
        help_text="Authentication configuration"
    )
    
    tool_config = models.JSONField(
        default=dict,
        help_text="Tool-specific configuration parameters"
    )
    
    # Capabilities and requirements
    supported_operations = models.JSONField(
        default=list,
        help_text="List of operations this tool supports"
    )
    
    required_permissions = models.JSONField(
        default=list,
        help_text="Required permissions to use this tool"
    )
    
    # Usage and performance
    usage_count = models.PositiveIntegerField(
        default=0
    )
    
    avg_response_time_ms = models.FloatField(
        default=0.0,
        help_text="Average response time in milliseconds"
    )
    
    success_rate = models.FloatField(
        default=1.0,
        help_text="Success rate (0-1)"
    )
    
    # Version and compatibility
    tool_version = models.CharField(
        max_length=20,
        default='1.0.0'
    )
    
    compatible_agents = models.ManyToManyField(
        UnifiedAgentTemplate,
        blank=True,
        related_name='compatible_tools',
        help_text="Agents compatible with this tool"
    )
    
    class Meta:
        verbose_name = "Agent Tool"
        verbose_name_plural = "Agent Tools"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.display_name} ({self.tool_type})"


class AgentRegistry(UnifiedBaseModel):
    """
    Central registry for agent discovery and capability mapping
    """
    
    registry_name = models.CharField(
        max_length=100,
        unique=True,
        default='unified_agent_registry'
    )
    
    description = models.TextField(
        default="Central registry for the Unified Donkey Betz Platform agents"
    )
    
    # Registry statistics
    total_agents = models.PositiveIntegerField(
        default=0
    )
    
    active_agents = models.PositiveIntegerField(
        default=0
    )
    
    total_executions = models.PositiveIntegerField(
        default=0
    )
    
    # Capability index
    capability_index = models.JSONField(
        default=dict,
        help_text="Index mapping capabilities to agent lists"
    )
    
    specialization_index = models.JSONField(
        default=dict,
        help_text="Index mapping specializations to agent lists"
    )
    
    keyword_index = models.JSONField(
        default=dict,
        help_text="Index mapping keywords to agent lists"
    )
    
    # Performance metrics
    avg_success_rate = models.FloatField(
        default=0.0
    )
    
    avg_execution_time = models.IntegerField(
        default=0
    )
    
    last_updated = models.DateTimeField(
        auto_now=True
    )
    
    class Meta:
        verbose_name = "Agent Registry"
        verbose_name_plural = "Agent Registries"
    
    def __str__(self):
        return f"{self.registry_name} ({self.total_agents} agents)"
    
    def rebuild_indexes(self):
        """Rebuild all capability and keyword indexes"""
        agents = UnifiedAgentTemplate.objects.filter(is_active=True)
        
        # Reset indexes
        self.capability_index = {}
        self.specialization_index = {}
        self.keyword_index = {}
        
        for agent in agents:
            # Build capability index
            for capability in agent.capabilities:
                if capability not in self.capability_index:
                    self.capability_index[capability] = []
                self.capability_index[capability].append({
                    'name': agent.name,
                    'confidence': agent.confidence_score,
                    'success_rate': agent.success_rate
                })
            
            # Build specialization index
            spec = agent.specialization
            if spec not in self.specialization_index:
                self.specialization_index[spec] = []
            self.specialization_index[spec].append({
                'name': agent.name,
                'confidence': agent.confidence_score,
                'success_rate': agent.success_rate
            })
            
            # Build keyword index
            for keyword in agent.routing_keywords:
                if keyword not in self.keyword_index:
                    self.keyword_index[keyword] = []
                self.keyword_index[keyword].append({
                    'name': agent.name,
                    'confidence': agent.confidence_score,
                    'success_rate': agent.success_rate
                })
        
        # Update statistics
        self.total_agents = agents.count()
        self.active_agents = agents.filter(is_active=True).count()
        self.avg_success_rate = agents.aggregate(
            models.Avg('success_rate')
        )['success_rate__avg'] or 0.0
        self.avg_execution_time = agents.aggregate(
            models.Avg('avg_completion_time')
        )['avg_completion_time__avg'] or 0
        
        self.save()
    
    def find_agents_for_task(self, task_description, required_capabilities=None, specialization=None, limit=5):
        """Find suitable agents for a given task"""
        scoring = {}
        task_lower = task_description.lower()
        
        # Score agents based on keyword matches
        for keyword, agents in self.keyword_index.items():
            if keyword.lower() in task_lower:
                for agent_info in agents:
                    agent_name = agent_info['name']
                    if agent_name not in scoring:
                        scoring[agent_name] = 0
                    scoring[agent_name] += agent_info['confidence'] * agent_info['success_rate']
        
        # Score agents based on capabilities
        if required_capabilities:
            for capability in required_capabilities:
                if capability in self.capability_index:
                    for agent_info in self.capability_index[capability]:
                        agent_name = agent_info['name']
                        if agent_name not in scoring:
                            scoring[agent_name] = 0
                        scoring[agent_name] += agent_info['confidence'] * agent_info['success_rate'] * 2  # Higher weight
        
        # Score agents based on specialization
        if specialization and specialization in self.specialization_index:
            for agent_info in self.specialization_index[specialization]:
                agent_name = agent_info['name']
                if agent_name not in scoring:
                    scoring[agent_name] = 0
                scoring[agent_name] += agent_info['confidence'] * agent_info['success_rate'] * 1.5
        
        # Return top scoring agents
        sorted_agents = sorted(scoring.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return [
            {
                'agent_name': agent_name,
                'score': score,
                'agent': UnifiedAgentTemplate.objects.get(name=agent_name, is_active=True)
            }
            for agent_name, score in sorted_agents
        ]


# Signal handlers for maintaining registry indexes
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=UnifiedAgentTemplate)
def update_registry_on_agent_save(sender, instance, created, **kwargs):
    """Update agent registry when agents are created or modified"""
    try:
        registry, _ = AgentRegistry.objects.get_or_create(
            registry_name='unified_agent_registry'
        )
        registry.rebuild_indexes()
    except Exception:
        pass  # Fail silently to avoid breaking agent saves

@receiver(post_delete, sender=UnifiedAgentTemplate)
def update_registry_on_agent_delete(sender, instance, **kwargs):
    """Update agent registry when agents are deleted"""
    try:
        registry = AgentRegistry.objects.get(registry_name='unified_agent_registry')
        registry.rebuild_indexes()
    except AgentRegistry.DoesNotExist:
        pass  # Registry doesn't exist yet


# =============================================================================
# AGENT CHANNELS - "Slack for AI Agents" System
# =============================================================================

class AgentChannel(UnifiedBaseModel):
    """
    Communication channels for agents - "Slack for AI Agents"
    Allows users to watch agents communicate and collaborate in real-time
    """
    
    CHANNEL_TYPES = [
        ('project', 'Project Channel'),
        ('topic', 'Topic Channel'),
        ('team', 'Team Channel'),
        ('general', 'General Channel'),
        ('system', 'System Channel'),
        ('orchestration', 'Orchestration Channel'),
    ]
    
    # Basic channel info
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique channel name (e.g., 'general', 'orchestration-123')"
    )
    
    display_name = models.CharField(
        max_length=200,
        help_text="Human-friendly display name"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Channel description and purpose"
    )
    
    channel_type = models.CharField(
        max_length=20,
        choices=CHANNEL_TYPES,
        default='project'
    )
    
    # Channel settings
    is_public = models.BooleanField(
        default=True,
        help_text="Whether channel is visible to all users"
    )
    
    is_archived = models.BooleanField(
        default=False,
        help_text="Whether channel is archived"
    )
    
    # Channel metadata
    metadata = models.JSONField(
        default=dict,
        help_text="Additional channel metadata (orchestration_id, etc.)"
    )
    
    active_agents = models.JSONField(
        default=list,
        help_text="List of currently active agent IDs in this channel"
    )
    
    # Metrics
    message_count = models.PositiveIntegerField(
        default=0,
        help_text="Total number of messages in channel"
    )
    
    # Relations
    orchestration = models.ForeignKey(
        AgentOrchestration,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='channels',
        help_text="Associated orchestration if this is an orchestration channel"
    )
    
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_channels'
    )
    
    class Meta:
        verbose_name = "Agent Channel"
        verbose_name_plural = "Agent Channels"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['channel_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"#{self.display_name or self.name} ({self.channel_type})"


class AgentChannelMessage(UnifiedBaseModel):
    """
    Individual messages within agent channels
    """
    
    MESSAGE_TYPES = [
        ('agent_message', 'Agent Message'),
        ('system_message', 'System Message'),
        ('user_message', 'User Message'),
        ('status_update', 'Status Update'),
        ('task_update', 'Task Update'),
        ('tool_usage', 'Tool Usage'),
        ('collaboration_request', 'Collaboration Request'),
        ('result_share', 'Result Share'),
        ('error_report', 'Error Report'),
    ]
    
    # Message basics
    channel = models.ForeignKey(
        AgentChannel,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    
    message_type = models.CharField(
        max_length=30,
        choices=MESSAGE_TYPES,
        default='agent_message'
    )
    
    content = models.TextField(
        help_text="Message content"
    )
    
    rich_content = models.JSONField(
        default=dict,
        help_text="Rich content (code blocks, attachments, etc.)"
    )
    
    # Message sender (either agent or user)
    agent_instance = models.ForeignKey(
        'AgentExecution',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='channel_messages',
        help_text="Agent execution that sent this message"
    )
    
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='channel_messages',
        help_text="User that sent this message"
    )
    
    # Threading and organization
    thread_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Thread ID for message threading"
    )
    
    parent_message = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    
    # Interactions
    reactions = models.JSONField(
        default=dict,
        help_text="Emoji reactions to this message"
    )
    
    is_pinned = models.BooleanField(
        default=False,
        help_text="Whether message is pinned in channel"
    )
    
    # Metadata
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Message timestamp"
    )
    
    edited_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last edit timestamp"
    )
    
    class Meta:
        verbose_name = "Agent Channel Message"
        verbose_name_plural = "Agent Channel Messages"
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['channel', 'timestamp']),
            models.Index(fields=['message_type']),
            models.Index(fields=['thread_id']),
        ]
    
    def __str__(self):
        sender = self.agent_instance or self.user or 'System'
        return f"{sender} in #{self.channel.name}: {self.content[:50]}..."


class AgentChannelMembership(UnifiedBaseModel):
    """
    Track which agents/users are members of which channels
    """
    
    NOTIFICATION_LEVELS = [
        ('all', 'All Messages'),
        ('mentions', 'Mentions Only'),
        ('none', 'No Notifications'),
    ]
    
    MEMBER_ROLES = [
        ('member', 'Member'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
        ('observer', 'Observer'),
    ]
    
    channel = models.ForeignKey(
        AgentChannel,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    
    # Member can be either agent or user
    agent_template = models.ForeignKey(
        UnifiedAgentTemplate,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='channel_memberships'
    )
    
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='channel_memberships'
    )
    
    # Membership settings
    joined_at = models.DateTimeField(auto_now_add=True)
    
    role = models.CharField(
        max_length=20,
        choices=MEMBER_ROLES,
        default='member'
    )
    
    notification_level = models.CharField(
        max_length=20,
        choices=NOTIFICATION_LEVELS,
        default='all'
    )
    
    last_read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time member read messages in this channel"
    )
    
    # Status tracking
    is_watching = models.BooleanField(
        default=True,
        help_text="Whether member is actively watching this channel"
    )
    
    class Meta:
        verbose_name = "Agent Channel Membership"
        verbose_name_plural = "Agent Channel Memberships"
        unique_together = [
            ('channel', 'agent_template'),
            ('channel', 'user'),
        ]
        indexes = [
            models.Index(fields=['channel', 'is_active']),
            models.Index(fields=['last_read_at']),
        ]
    
    def __str__(self):
        member = self.agent_template or self.user or 'Unknown'
        return f"{member} in #{self.channel.name} ({self.role})"
    
    def clean(self):
        """Ensure either agent_template or user is set, but not both"""
        if not self.agent_template and not self.user:
            raise ValidationError("Either agent_template or user must be set")
        
        if self.agent_template and self.user:
            raise ValidationError("Cannot set both agent_template and user")


class AgentPerformanceMetrics(UnifiedBaseModel):
    """
    Track individual agent prediction performance for agent learning system
    Enables agents to learn from their own track record and adapt strategies
    """

    agent = models.ForeignKey(
        UnifiedAgentTemplate,
        on_delete=models.CASCADE,
        related_name='performance_metrics',
        help_text="Agent being tracked"
    )

    # Overall metrics
    total_predictions = models.IntegerField(
        default=0,
        help_text="Total predictions made by this agent"
    )
    correct_predictions = models.IntegerField(
        default=0,
        help_text="Number of correct predictions"
    )
    accuracy = models.FloatField(
        default=0.0,
        help_text="Overall accuracy (0.0-1.0)"
    )

    # Sport-specific metrics
    sport_type = models.CharField(
        max_length=10,
        choices=[
            ('nfl', 'NFL'),
            ('nba', 'NBA'),
            ('mlb', 'MLB'),
            ('nhl', 'NHL'),
        ],
        help_text="Sport type for these metrics"
    )
    sport_predictions = models.IntegerField(
        default=0,
        help_text="Predictions made for this sport"
    )
    sport_correct = models.IntegerField(
        default=0,
        help_text="Correct predictions for this sport"
    )
    sport_accuracy = models.FloatField(
        default=0.0,
        help_text="Accuracy for this sport (0.0-1.0)"
    )

    # Confidence calibration
    avg_confidence_when_correct = models.FloatField(
        default=0.0,
        help_text="Average confidence when prediction was correct"
    )
    avg_confidence_when_wrong = models.FloatField(
        default=0.0,
        help_text="Average confidence when prediction was wrong"
    )
    confidence_calibration_score = models.FloatField(
        default=0.0,
        help_text="How well-calibrated confidence is (-1.0 to 1.0)"
    )

    # Learning metrics
    last_10_predictions_accuracy = models.FloatField(
        default=0.0,
        help_text="Accuracy of last 10 predictions"
    )
    last_30_predictions_accuracy = models.FloatField(
        default=0.0,
        help_text="Accuracy of last 30 predictions"
    )
    trend = models.CharField(
        max_length=20,
        choices=[
            ('improving', 'Improving'),
            ('stable', 'Stable'),
            ('declining', 'Declining'),
        ],
        default='stable',
        help_text="Performance trend"
    )

    # Specializations
    best_sport = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Sport agent performs best in"
    )
    worst_sport = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Sport agent performs worst in"
    )
    confidence_level = models.CharField(
        max_length=20,
        choices=[
            ('overconfident', 'Overconfident'),
            ('well_calibrated', 'Well Calibrated'),
            ('underconfident', 'Underconfident'),
        ],
        default='well_calibrated',
        help_text="Confidence calibration assessment"
    )

    class Meta:
        verbose_name = "Agent Performance Metrics"
        verbose_name_plural = "Agent Performance Metrics"
        unique_together = [('agent', 'sport_type')]
        indexes = [
            models.Index(fields=['agent', 'sport_type']),
            models.Index(fields=['accuracy']),
            models.Index(fields=['sport_accuracy']),
        ]

    def __str__(self):
        return f"{self.agent.name} - {self.sport_type.upper()} ({self.sport_accuracy:.1%})"

    def update_from_prediction(self, prediction):
        """
        Update metrics based on new prediction result

        Args:
            prediction: MLPrediction instance with was_correct populated
        """
        # Update total predictions
        self.total_predictions += 1
        if prediction.sport_type == self.sport_type:
            self.sport_predictions += 1

        # Update correct predictions
        if prediction.was_correct:
            self.correct_predictions += 1
            if prediction.sport_type == self.sport_type:
                self.sport_correct += 1

        # Recalculate accuracy
        if self.total_predictions > 0:
            self.accuracy = self.correct_predictions / self.total_predictions
        if self.sport_predictions > 0:
            self.sport_accuracy = self.sport_correct / self.sport_predictions

        # Update confidence calibration
        if prediction.was_correct:
            # Running average of confidence when correct
            if self.correct_predictions > 1:
                self.avg_confidence_when_correct = (
                    (self.avg_confidence_when_correct * (self.correct_predictions - 1) + prediction.confidence) /
                    self.correct_predictions
                )
            else:
                self.avg_confidence_when_correct = prediction.confidence
        else:
            # Running average of confidence when wrong
            wrong_count = self.total_predictions - self.correct_predictions
            if wrong_count > 1:
                self.avg_confidence_when_wrong = (
                    (self.avg_confidence_when_wrong * (wrong_count - 1) + prediction.confidence) /
                    wrong_count
                )
            else:
                self.avg_confidence_when_wrong = prediction.confidence

        # Calculate calibration score (positive = well calibrated)
        if self.avg_confidence_when_correct > 0 and self.avg_confidence_when_wrong > 0:
            self.confidence_calibration_score = (
                self.avg_confidence_when_correct - self.avg_confidence_when_wrong
            ) / 100.0  # Normalize to -1.0 to 1.0

        self.save()


# Channel management signals
@receiver(post_save, sender=AgentChannelMessage)
def update_channel_message_count(sender, instance, created, **kwargs):
    """Update channel message count when new messages are added"""
    if created:
        instance.channel.message_count += 1
        instance.channel.save(update_fields=['message_count'])


@receiver(post_save, sender=AgentOrchestration)
def create_orchestration_channel(sender, instance, created, **kwargs):
    """Automatically create a channel for new orchestrations"""
    if created:
        channel_name = f"orchestration-{instance.id}"
        channel, channel_created = AgentChannel.objects.get_or_create(
            name=channel_name,
            defaults={
                'display_name': f"Orchestration: {instance.name}",
                'description': f"Real-time communication for orchestration: {instance.description}",
                'channel_type': 'orchestration',
                'orchestration': instance,
                'created_by': instance.user,
                'metadata': {
                    'orchestration_id': str(instance.id),
                    'auto_created': True,
                }
            }
        )
