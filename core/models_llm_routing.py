"""
LLM Routing Models - Enhanced Nervous System
Session 697: Multi-model intelligence routing

This module defines the database models for routing agents to
specialized LLMs based on their task domain.

The Human Body Metaphor:
- NERVOUS SYSTEM (ML) = Agent-Model Router (routes to ML models)
- NERVOUS SYSTEM (LLM) = Agent-LLM Router (routes to specialized LLMs) ← NEW
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class LLMProvider(models.Model):
    """
    Registered LLM providers (OpenAI, Anthropic, DeepSeek, Gemini, Ollama).

    Each provider can have multiple models and different capabilities.
    """

    PROVIDER_CHOICES = [
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('deepseek', 'DeepSeek'),
        ('together', 'Together AI'),  # Session 697: Hosts DeepSeek, Llama, Mixtral
        ('gemini', 'Google Gemini'),
        ('ollama', 'Ollama (Local)'),
        ('replicate', 'Replicate'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True, choices=PROVIDER_CHOICES)
    display_name = models.CharField(max_length=100)

    # API Configuration
    api_key_env_var = models.CharField(
        max_length=100,
        help_text="Environment variable name for API key (e.g., OPENAI_API_KEY)"
    )
    base_url = models.URLField(
        blank=True,
        help_text="Custom base URL (for Ollama or proxies)"
    )

    # Status
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(
        default=False,
        help_text="Set by health check - indicates if provider is responding"
    )
    last_health_check = models.DateTimeField(null=True, blank=True)

    # Capabilities
    supports_tools = models.BooleanField(default=True, help_text="Supports function/tool calling")
    supports_vision = models.BooleanField(default=False, help_text="Supports image input")
    supports_streaming = models.BooleanField(default=True, help_text="Supports streaming responses")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_llm_providers'
        verbose_name = 'LLM Provider'
        verbose_name_plural = 'LLM Providers'

    def __str__(self):
        status = "✅" if self.is_available else "❌"
        return f"{status} {self.display_name}"


class LLMModel(models.Model):
    """
    Individual LLM models available from each provider.

    Examples:
    - OpenAI: gpt-5-mini, gpt-5.1, gpt-5.2
    - Anthropic: claude-3.5-sonnet, claude-3.5-haiku, claude-3.5-opus
    - DeepSeek: deepseek-coder-v2, deepseek-chat
    - Gemini: gemini-pro, gemini-ultra
    - Ollama: llama3.1:8b, codellama:34b, mistral:7b
    """

    CATEGORY_CHOICES = [
        ('general', 'General Purpose'),
        ('coding', 'Code Generation'),
        ('reasoning', 'Complex Reasoning'),
        ('creative', 'Creative Writing'),
        ('fast', 'Fast/Cheap'),
        ('vision', 'Vision/Multimodal'),
        ('local', 'Local/Private'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(
        LLMProvider,
        on_delete=models.CASCADE,
        related_name='models'
    )

    # Model Identity
    model_id = models.CharField(
        max_length=100,
        help_text="API model identifier (e.g., 'gpt-5.1', 'claude-3.5-sonnet')"
    )
    display_name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')

    # Capabilities & Characteristics
    context_window = models.IntegerField(
        default=128000,
        help_text="Maximum context window in tokens"
    )
    max_output_tokens = models.IntegerField(
        default=4096,
        help_text="Maximum output tokens"
    )
    supports_tools = models.BooleanField(default=True)
    supports_vision = models.BooleanField(default=False)
    supports_streaming = models.BooleanField(default=True)

    # Performance Characteristics
    speed_rating = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="1=slowest, 10=fastest"
    )
    quality_rating = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="1=lowest, 10=highest quality"
    )

    # Cost (per 1M tokens)
    cost_per_1m_input = models.DecimalField(
        max_digits=10, decimal_places=4, default=0,
        help_text="Cost per 1M input tokens in USD"
    )
    cost_per_1m_output = models.DecimalField(
        max_digits=10, decimal_places=4, default=0,
        help_text="Cost per 1M output tokens in USD"
    )

    # Specializations (JSON for flexibility)
    specializations = models.JSONField(
        default=list,
        help_text="List of task types this model excels at: ['coding', 'analysis', 'creative', 'legal', 'finance']"
    )

    # Default Parameters
    default_temperature = models.FloatField(default=0.7)
    default_max_tokens = models.IntegerField(default=2000)

    # Status
    is_active = models.BooleanField(default=True)
    is_recommended = models.BooleanField(
        default=False,
        help_text="Recommended model for its category"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_llm_models'
        verbose_name = 'LLM Model'
        verbose_name_plural = 'LLM Models'
        unique_together = ['provider', 'model_id']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['provider', 'is_active']),
        ]

    def __str__(self):
        return f"{self.display_name} ({self.provider.name})"

    @property
    def full_model_id(self):
        """Return provider:model_id format"""
        return f"{self.provider.name}:{self.model_id}"


class AgentLLMConfig(models.Model):
    """
    Configuration mapping agents to their preferred LLM models.

    This is the core routing table for the Enhanced Nervous System.
    Each agent can have:
    - Primary model (main choice)
    - Fallback model (if primary fails)
    - Task-specific overrides
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Agent Identity
    agent_name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Agent class name (e.g., 'CodeGeneratorAgent')"
    )
    agent_category = models.CharField(
        max_length=50,
        blank=True,
        help_text="Agent category for grouping (e.g., 'development', 'content', 'analysis')"
    )

    # Model Assignment
    primary_model = models.ForeignKey(
        LLMModel,
        on_delete=models.SET_NULL,
        null=True,
        related_name='primary_agents',
        help_text="Primary LLM model for this agent"
    )
    fallback_model = models.ForeignKey(
        LLMModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fallback_agents',
        help_text="Fallback model if primary fails"
    )

    # Task-Specific Overrides
    task_overrides = models.JSONField(
        default=dict,
        help_text="""
        Task-specific model overrides. Example:
        {
            "complex_analysis": {"model_id": "uuid-of-reasoning-model"},
            "quick_response": {"model_id": "uuid-of-fast-model"}
        }
        """
    )

    # Parameters
    temperature = models.FloatField(
        default=0.7,
        validators=[MinValueValidator(0), MaxValueValidator(2)]
    )
    max_tokens = models.IntegerField(default=2000)
    custom_params = models.JSONField(
        default=dict,
        help_text="Additional model-specific parameters"
    )

    # Auto-Selection
    use_auto_selection = models.BooleanField(
        default=False,
        help_text="Let system auto-select model based on task analysis"
    )

    # Performance Tracking
    total_calls = models.IntegerField(default=0)
    successful_calls = models.IntegerField(default=0)
    total_tokens_used = models.BigIntegerField(default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=6, default=0)
    avg_latency_ms = models.FloatField(default=0)

    # Status
    is_active = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, help_text="Configuration notes")

    class Meta:
        db_table = 'core_agent_llm_configs'
        verbose_name = 'Agent LLM Config'
        verbose_name_plural = 'Agent LLM Configs'
        indexes = [
            models.Index(fields=['agent_category', 'is_active']),
        ]

    def __str__(self):
        model_name = self.primary_model.display_name if self.primary_model else "Auto"
        return f"{self.agent_name} → {model_name}"

    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.total_calls == 0:
            return 0
        return (self.successful_calls / self.total_calls) * 100


class LLMCallLog(models.Model):
    """
    Audit log of all LLM calls for performance tracking and debugging.

    Used to:
    - Track costs per agent
    - Identify slow/failing models
    - Optimize routing decisions
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Call Context
    agent_name = models.CharField(max_length=100, db_index=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Model Used
    provider = models.CharField(max_length=50)
    model_id = models.CharField(max_length=100)
    was_fallback = models.BooleanField(default=False)
    was_auto_selected = models.BooleanField(default=False)

    # Request Details
    task_type = models.CharField(max_length=50, blank=True)
    prompt_tokens = models.IntegerField(default=0)

    # Response Details
    success = models.BooleanField(default=True)
    completion_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    latency_ms = models.IntegerField(default=0)

    # Cost
    cost = models.DecimalField(max_digits=10, decimal_places=6, default=0)

    # Correlation
    trace_id = models.CharField(max_length=64, blank=True, db_index=True,
                                help_text='PA request trace ID for joining LLM calls to Celery tasks')

    # Error Info (if failed)
    error_type = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_llm_call_logs'
        verbose_name = 'LLM Call Log'
        verbose_name_plural = 'LLM Call Logs'
        indexes = [
            models.Index(fields=['agent_name', '-created_at']),
            models.Index(fields=['provider', 'model_id', '-created_at']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['success', '-created_at']),
        ]

    def __str__(self):
        status = "✅" if self.success else "❌"
        return f"{status} {self.agent_name} → {self.provider}:{self.model_id}"


# =============================================================================
# Default Configurations
# =============================================================================

DEFAULT_PROVIDERS = [
    {
        'name': 'openai',
        'display_name': 'OpenAI',
        'api_key_env_var': 'OPENAI_API_KEY',
        'base_url': '',
        'supports_tools': True,
        'supports_vision': True,
        'supports_streaming': True,
    },
    {
        'name': 'anthropic',
        'display_name': 'Anthropic',
        'api_key_env_var': 'ANTHROPIC_API_KEY',
        'base_url': '',
        'supports_tools': True,
        'supports_vision': True,
        'supports_streaming': True,
    },
    {
        'name': 'deepseek',
        'display_name': 'DeepSeek',
        'api_key_env_var': 'DEEPSEEK_API_KEY',
        'base_url': 'https://api.deepseek.com',
        'supports_tools': True,
        'supports_vision': False,
        'supports_streaming': True,
    },
    {
        'name': 'gemini',
        'display_name': 'Google Gemini',
        'api_key_env_var': 'GEMINI_API_KEY',
        'base_url': '',
        'supports_tools': True,
        'supports_vision': True,
        'supports_streaming': True,
    },
    {
        'name': 'ollama',
        'display_name': 'Ollama (Local)',
        'api_key_env_var': '',  # No API key needed
        'base_url': 'http://localhost:11434',
        'supports_tools': True,
        'supports_vision': False,
        'supports_streaming': True,
    },
    {
        'name': 'together',
        'display_name': 'Together AI',
        'api_key_env_var': 'TOGETHER_AI_API_KEY',
        'base_url': 'https://api.together.xyz/v1',
        'supports_tools': True,
        'supports_vision': True,
        'supports_streaming': True,
    },
]

DEFAULT_MODELS = [
    # OpenAI Models
    {
        'provider': 'openai',
        'model_id': 'gpt-5-mini',
        'display_name': 'GPT-5 Mini',
        'category': 'fast',
        'context_window': 128000,
        'max_output_tokens': 16384,
        'speed_rating': 9,
        'quality_rating': 7,
        'cost_per_1m_input': 0.15,
        'cost_per_1m_output': 0.60,
        'specializations': ['general', 'quick_tasks', 'routing'],
        'is_recommended': True,
    },
    {
        'provider': 'openai',
        'model_id': 'gpt-5.1',
        'display_name': 'GPT-5.1',
        'category': 'general',
        'context_window': 200000,
        'max_output_tokens': 32768,
        'speed_rating': 7,
        'quality_rating': 9,
        'cost_per_1m_input': 1.25,
        'cost_per_1m_output': 10.00,
        'specializations': ['analysis', 'reasoning', 'coding', 'content'],
        'is_recommended': True,
    },
    {
        'provider': 'openai',
        'model_id': 'gpt-5.2',
        'display_name': 'GPT-5.2',
        'category': 'reasoning',
        'context_window': 200000,
        'max_output_tokens': 65536,
        'speed_rating': 5,
        'quality_rating': 10,
        'cost_per_1m_input': 5.00,
        'cost_per_1m_output': 20.00,
        'specializations': ['complex_reasoning', 'research', 'strategy'],
        'is_recommended': False,
    },

    # Anthropic Claude 4 Models (January 2026)
    {
        'provider': 'anthropic',
        'model_id': 'claude-sonnet-4-20250514',
        'display_name': 'Claude Sonnet 4',
        'category': 'general',
        'context_window': 200000,
        'max_output_tokens': 16384,
        'speed_rating': 8,
        'quality_rating': 9,
        'cost_per_1m_input': 3.00,
        'cost_per_1m_output': 15.00,
        'specializations': ['coding', 'creative', 'analysis', 'legal'],
        'is_recommended': True,
    },
    {
        'provider': 'anthropic',
        'model_id': 'claude-opus-4-20250514',
        'display_name': 'Claude Opus 4',
        'category': 'reasoning',
        'context_window': 200000,
        'max_output_tokens': 16384,
        'speed_rating': 5,
        'quality_rating': 10,
        'cost_per_1m_input': 15.00,
        'cost_per_1m_output': 75.00,
        'specializations': ['complex_reasoning', 'research', 'strategy', 'legal'],
        'is_recommended': True,
    },

    # DeepSeek Models
    {
        'provider': 'deepseek',
        'model_id': 'deepseek-coder',
        'display_name': 'DeepSeek Coder V2',
        'category': 'coding',
        'context_window': 128000,
        'max_output_tokens': 8192,
        'speed_rating': 8,
        'quality_rating': 9,
        'cost_per_1m_input': 0.14,
        'cost_per_1m_output': 0.28,
        'specializations': ['coding', 'code_review', 'devops'],
        'is_recommended': True,
    },
    {
        'provider': 'deepseek',
        'model_id': 'deepseek-chat',
        'display_name': 'DeepSeek Chat',
        'category': 'general',
        'context_window': 64000,
        'max_output_tokens': 4096,
        'speed_rating': 9,
        'quality_rating': 7,
        'cost_per_1m_input': 0.07,
        'cost_per_1m_output': 0.14,
        'specializations': ['general', 'quick_tasks'],
        'is_recommended': False,
    },

    # Gemini Models (Session 698: Updated to available models)
    {
        'provider': 'gemini',
        'model_id': 'gemini-2.5-flash',
        'display_name': 'Gemini 2.5 Flash',
        'category': 'fast',
        'context_window': 1000000,
        'max_output_tokens': 8192,
        'speed_rating': 10,
        'quality_rating': 8,
        'cost_per_1m_input': 0.075,
        'cost_per_1m_output': 0.30,
        'specializations': ['quick_tasks', 'long_context', 'analysis'],
        'is_recommended': True,
    },
    {
        'provider': 'gemini',
        'model_id': 'gemini-3-flash-preview',
        'display_name': 'Gemini 3 Flash (Preview)',
        'category': 'general',
        'context_window': 1000000,
        'max_output_tokens': 8192,
        'speed_rating': 9,
        'quality_rating': 9,
        'cost_per_1m_input': 0.15,
        'cost_per_1m_output': 0.60,
        'specializations': ['analysis', 'research', 'long_context', 'coding'],
        'is_recommended': True,
    },

    # Ollama Local Models
    {
        'provider': 'ollama',
        'model_id': 'llama3.1:70b',
        'display_name': 'Llama 3.1 70B (Local)',
        'category': 'local',
        'context_window': 128000,
        'max_output_tokens': 4096,
        'speed_rating': 5,
        'quality_rating': 8,
        'cost_per_1m_input': 0,
        'cost_per_1m_output': 0,
        'specializations': ['general', 'private', 'offline'],
        'is_recommended': True,
    },
    {
        'provider': 'ollama',
        'model_id': 'codellama:34b',
        'display_name': 'CodeLlama 34B (Local)',
        'category': 'coding',
        'context_window': 16000,
        'max_output_tokens': 4096,
        'speed_rating': 6,
        'quality_rating': 7,
        'cost_per_1m_input': 0,
        'cost_per_1m_output': 0,
        'specializations': ['coding', 'private', 'offline'],
        'is_recommended': False,
    },
    {
        'provider': 'ollama',
        'model_id': 'mistral:7b',
        'display_name': 'Mistral 7B (Local)',
        'category': 'fast',
        'context_window': 32000,
        'max_output_tokens': 4096,
        'speed_rating': 9,
        'quality_rating': 6,
        'cost_per_1m_input': 0,
        'cost_per_1m_output': 0,
        'specializations': ['quick_tasks', 'private', 'offline'],
        'is_recommended': False,
    },

    # Together AI Models (serverless only - Session 698)
    {
        'provider': 'together',
        'model_id': 'deepseek-ai/DeepSeek-V3',
        'display_name': 'DeepSeek V3 (Together)',
        'category': 'coding',
        'context_window': 64000,
        'max_output_tokens': 8192,
        'speed_rating': 8,
        'quality_rating': 9,
        'cost_per_1m_input': 0.50,
        'cost_per_1m_output': 0.50,
        'specializations': ['coding', 'code_review', 'analysis', 'reasoning'],
        'is_recommended': True,
    },
    {
        'provider': 'together',
        'model_id': 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo',
        'display_name': 'Llama 3.1 70B Turbo (Together)',
        'category': 'general',
        'context_window': 131072,
        'max_output_tokens': 4096,
        'speed_rating': 8,
        'quality_rating': 8,
        'cost_per_1m_input': 0.88,
        'cost_per_1m_output': 0.88,
        'specializations': ['general', 'analysis', 'coding'],
        'is_recommended': True,
    },
    {
        'provider': 'together',
        'model_id': 'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo',
        'display_name': 'Llama 3.1 8B Turbo (Together)',
        'category': 'fast',
        'context_window': 131072,
        'max_output_tokens': 4096,
        'speed_rating': 10,
        'quality_rating': 7,
        'cost_per_1m_input': 0.18,
        'cost_per_1m_output': 0.18,
        'specializations': ['quick_tasks', 'routing', 'simple_content'],
        'is_recommended': True,
    },
    {
        'provider': 'together',
        'model_id': 'mistralai/Mixtral-8x7B-Instruct-v0.1',
        'display_name': 'Mixtral 8x7B (Together)',
        'category': 'general',
        'context_window': 32768,
        'max_output_tokens': 4096,
        'speed_rating': 8,
        'quality_rating': 8,
        'cost_per_1m_input': 0.60,
        'cost_per_1m_output': 0.60,
        'specializations': ['general', 'coding', 'analysis'],
        'is_recommended': True,
    },
]

# Agent → Model Mappings (what model each agent type should use)
DEFAULT_AGENT_LLM_CONFIGS = [
    # Development Agents → Together AI Llama 70B (serverless, good at coding) or Claude (reliable)
    {'agent_name': 'CodeGeneratorAgent', 'agent_category': 'development', 'primary': 'together:meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo', 'fallback': 'anthropic:claude-sonnet-4-20250514'},
    {'agent_name': 'FullStackDeveloperAgent', 'agent_category': 'development', 'primary': 'together:meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo', 'fallback': 'anthropic:claude-sonnet-4-20250514'},
    {'agent_name': 'CodeReviewAgent', 'agent_category': 'development', 'primary': 'anthropic:claude-sonnet-4-20250514', 'fallback': 'together:meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo'},
    {'agent_name': 'DevOpsAgent', 'agent_category': 'development', 'primary': 'together:meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo', 'fallback': 'openai:gpt-5.1'},

    # Content/Creative Agents → Claude (excellent writing)
    {'agent_name': 'ContentWriterAgent', 'agent_category': 'content', 'primary': 'anthropic:claude-sonnet-4-20250514', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'ContentStrategyAgent', 'agent_category': 'content', 'primary': 'anthropic:claude-sonnet-4-20250514', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'BrandIdentityAgent', 'agent_category': 'content', 'primary': 'anthropic:claude-sonnet-4-20250514', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'SEOOptimizerAgent', 'agent_category': 'content', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},

    # Analysis/Research Agents → GPT-5.1 (strong analysis) or Gemini (long context)
    {'agent_name': 'ResearchAgent', 'agent_category': 'research', 'primary': 'openai:gpt-5.1', 'fallback': 'gemini:gemini-3-flash-preview'},
    {'agent_name': 'TrendAnalysisAgent', 'agent_category': 'analysis', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},
    {'agent_name': 'MarketIntelligenceAgent', 'agent_category': 'analysis', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},
    {'agent_name': 'CompetitorAnalysisAgent', 'agent_category': 'analysis', 'primary': 'gemini:gemini-3-flash-preview', 'fallback': 'openai:gpt-5.1'},

    # Legal Agent → Claude (procedural, careful, good with rules)
    {'agent_name': 'LegalDocDrafterAgent', 'agent_category': 'legal', 'primary': 'anthropic:claude-sonnet-4-20250514', 'fallback': 'openai:gpt-5.1'},

    # Stock/Market Agents → GPT-5.1 (financial analysis)
    {'agent_name': 'StockAnalystAgent', 'agent_category': 'markets', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},
    {'agent_name': 'BullCaseAgent', 'agent_category': 'markets', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},
    {'agent_name': 'BearCaseAgent', 'agent_category': 'markets', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},

    # ThinkingAgent → Claude Opus or GPT-5.2 (deep reasoning)
    {'agent_name': 'ThinkingAgent', 'agent_category': 'reasoning', 'primary': 'anthropic:claude-opus-4-20250514', 'fallback': 'openai:gpt-5.2'},

    # Orchestration Agents → Fast models for routing
    {'agent_name': 'PersonalAssistantAgent', 'agent_category': 'orchestration', 'primary': 'openai:gpt-5-mini', 'fallback': 'openai:gpt-5-mini'},
    {'agent_name': 'WorkflowAgent', 'agent_category': 'orchestration', 'primary': 'openai:gpt-5-mini', 'fallback': 'openai:gpt-5-mini'},

    # Creation Agents → GPT-5.1 (good prompts for image/video generation)
    {'agent_name': 'ImageAgent', 'agent_category': 'creation', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},
    {'agent_name': 'VideoAgent', 'agent_category': 'creation', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},

    # System Agent → Fast reliable model
    {'agent_name': 'SystemIntelligenceAgent', 'agent_category': 'system', 'primary': 'openai:gpt-5-mini', 'fallback': 'openai:gpt-5-mini'},

    # ============================================================================
    # SESSION 697: Additional Agent Configs (43 more agents)
    # ============================================================================

    # Executive/Strategy Agents → GPT-5.1 (good reasoning for leadership)
    {'agent_name': 'CTOAgent', 'agent_category': 'executive', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},
    {'agent_name': 'COOAgent', 'agent_category': 'executive', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},
    {'agent_name': 'CreativeDirectorAgent', 'agent_category': 'executive', 'primary': 'anthropic:claude-sonnet-4-20250514', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'MeetingCoordinatorAgent', 'agent_category': 'executive', 'primary': 'openai:gpt-5-mini', 'fallback': 'openai:gpt-5-mini'},

    # Content/Creative Agents → Claude (excellent writing)
    {'agent_name': 'AudioAgent', 'agent_category': 'creation', 'primary': 'anthropic:claude-sonnet-4-20250514', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'ThreeDAgent', 'agent_category': 'creation', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},
    {'agent_name': 'BrandStrategyAgent', 'agent_category': 'content', 'primary': 'anthropic:claude-sonnet-4-20250514', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'MarketingStrategyAgent', 'agent_category': 'content', 'primary': 'anthropic:claude-sonnet-4-20250514', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'SocialMediaAgent', 'agent_category': 'content', 'primary': 'anthropic:claude-sonnet-4-20250514', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'TechnicalDocumentAgent', 'agent_category': 'content', 'primary': 'anthropic:claude-sonnet-4-20250514', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'ContentAuditAgent', 'agent_category': 'content', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},
    {'agent_name': 'ContentExecutorAgent', 'agent_category': 'content', 'primary': 'openai:gpt-5-mini', 'fallback': 'openai:gpt-5-mini'},

    # Analysis/Research Agents → GPT-5.1 (strong analysis)
    {'agent_name': 'CustomerResearchAgent', 'agent_category': 'analysis', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},
    {'agent_name': 'OpportunityScoringAgent', 'agent_category': 'analysis', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},

    # Narrative/Cultural Agents → Claude (nuanced understanding)
    {'agent_name': 'CulturalImpactAgent', 'agent_category': 'narrative', 'primary': 'anthropic:claude-sonnet-4-20250514', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'NarrativeHistorianAgent', 'agent_category': 'narrative', 'primary': 'anthropic:claude-sonnet-4-20250514', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'TrendBreakDetectorAgent', 'agent_category': 'narrative', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},

    # Editing/Technical Agents → Together AI Llama 70B (coding/technical)
    {'agent_name': 'ImageEditingAgent', 'agent_category': 'editing', 'primary': 'together:meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'VideoEditingAgent', 'agent_category': 'editing', 'primary': 'together:meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'ResolveAgent', 'agent_category': 'editing', 'primary': 'together:meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo', 'fallback': 'openai:gpt-5.1'},

    # Blockchain/Security Agents → GPT-5.1 (careful analysis required)
    {'agent_name': 'SmartContractAuditorAgent', 'agent_category': 'blockchain', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},
    {'agent_name': 'TransactionMonitorAgent', 'agent_category': 'blockchain', 'primary': 'openai:gpt-5-mini', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'WhaleWatcherAgent', 'agent_category': 'blockchain', 'primary': 'openai:gpt-5-mini', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'ExploitDetectorAgent', 'agent_category': 'blockchain', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},

    # Market Monitoring Agents → GPT-5-mini (fast) or GPT-5.1 (analysis)
    {'agent_name': 'InstitutionalWatcherAgent', 'agent_category': 'markets', 'primary': 'openai:gpt-5-mini', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'MarketMovementMonitorAgent', 'agent_category': 'markets', 'primary': 'openai:gpt-5-mini', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'MarketAnomalyDetectorAgent', 'agent_category': 'markets', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},
    {'agent_name': 'SignalScannerAgent', 'agent_category': 'markets', 'primary': 'openai:gpt-5-mini', 'fallback': 'openai:gpt-5.1'},

    # Orchestration/Workflow Agents → GPT-5-mini (fast routing)
    {'agent_name': 'WorkflowOrchestrationAgent', 'agent_category': 'orchestration', 'primary': 'openai:gpt-5-mini', 'fallback': 'openai:gpt-5-mini'},
    {'agent_name': 'OpportunityPipelineAgent', 'agent_category': 'orchestration', 'primary': 'openai:gpt-5-mini', 'fallback': 'openai:gpt-5-mini'},
    {'agent_name': 'CampaignOrchestratorAgent', 'agent_category': 'orchestration', 'primary': 'openai:gpt-5-mini', 'fallback': 'openai:gpt-5-mini'},
    {'agent_name': 'AISeriesWorkflowAgent', 'agent_category': 'orchestration', 'primary': 'openai:gpt-5-mini', 'fallback': 'openai:gpt-5-mini'},
    {'agent_name': 'PodcastCoordinatorAgent', 'agent_category': 'orchestration', 'primary': 'openai:gpt-5-mini', 'fallback': 'openai:gpt-5-mini'},

    # Debate/Discussion Agents → Claude (argumentative writing)
    {'agent_name': 'DebateAdvocateAgent', 'agent_category': 'debate', 'primary': 'anthropic:claude-sonnet-4-20250514', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'DebateSkepticAgent', 'agent_category': 'debate', 'primary': 'anthropic:claude-sonnet-4-20250514', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'ModeratorAgent', 'agent_category': 'debate', 'primary': 'anthropic:claude-sonnet-4-20250514', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'ContrarianAgent', 'agent_category': 'debate', 'primary': 'anthropic:claude-sonnet-4-20250514', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'TopicMinerAgent', 'agent_category': 'debate', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},
    {'agent_name': 'PerformanceAnalystAgent', 'agent_category': 'debate', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},

    # Training/Generation Agents → Claude or Together AI
    {'agent_name': 'CharacterTrainingAgent', 'agent_category': 'training', 'primary': 'anthropic:claude-sonnet-4-20250514', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'TrainedCreationAgent', 'agent_category': 'training', 'primary': 'anthropic:claude-sonnet-4-20250514', 'fallback': 'openai:gpt-5.1'},

    # Security Agent → GPT-5.1 (careful analysis)
    {'agent_name': 'MemoryIsolationAgent', 'agent_category': 'security', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},

    # ============================================================================
    # SESSION 699: Additional Agent Configs (11 more agents - completing 64→75)
    # ============================================================================

    # Coordinator Agents → GPT-5-mini (fast routing for orchestration)
    {'agent_name': 'AutonomousContentStudioCoordinator', 'agent_category': 'orchestration', 'primary': 'openai:gpt-5-mini', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'BlockchainAuditCoordinator', 'agent_category': 'blockchain', 'primary': 'openai:gpt-5-mini', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'MarketIntelligenceCoordinator', 'agent_category': 'markets', 'primary': 'openai:gpt-5-mini', 'fallback': 'openai:gpt-5.1'},
    {'agent_name': 'NarrativeDriftCoordinator', 'agent_category': 'narrative', 'primary': 'openai:gpt-5-mini', 'fallback': 'anthropic:claude-sonnet-4-20250514'},
    {'agent_name': 'StockAuditCoordinator', 'agent_category': 'markets', 'primary': 'openai:gpt-5-mini', 'fallback': 'openai:gpt-5.1'},

    # Sports/Betting Agents → GPT-5.1 (financial analysis)
    {'agent_name': 'ArbitrageDetector', 'agent_category': 'betting', 'primary': 'openai:gpt-5.1', 'fallback': 'openai:gpt-5-mini'},
    {'agent_name': 'BookmakerAgent', 'agent_category': 'betting', 'primary': 'openai:gpt-5.1', 'fallback': 'openai:gpt-5-mini'},
    {'agent_name': 'PredictionMarketAnalyst', 'agent_category': 'betting', 'primary': 'openai:gpt-5.1', 'fallback': 'anthropic:claude-sonnet-4-20250514'},
    {'agent_name': 'SportsOddsAnalyst', 'agent_category': 'betting', 'primary': 'openai:gpt-5.1', 'fallback': 'openai:gpt-5-mini'},

    # Business/Strategy Agents → Claude (nuanced strategy)
    {'agent_name': 'BusinessContentStrategyAgent', 'agent_category': 'business', 'primary': 'anthropic:claude-sonnet-4-20250514', 'fallback': 'openai:gpt-5.1'},

    # Technical Agents → Claude (careful prompt engineering)
    {'agent_name': 'PromptEngineeringAgent', 'agent_category': 'technical', 'primary': 'anthropic:claude-sonnet-4-20250514', 'fallback': 'openai:gpt-5.1'},
]
