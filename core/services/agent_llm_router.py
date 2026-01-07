"""
Agent LLM Router - Enhanced Nervous System
Session 697: Routes agents to their optimal LLM models

This service is the routing layer that connects agents to their
configured LLM models based on task type, performance history,
and fallback rules.

The Human Body Metaphor:
- NERVOUS SYSTEM (LLM) = This file - routes neural signals (prompts)
  to the appropriate brain region (LLM model) based on the type of thought needed.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from core.services.llm_provider_registry import (
    get_llm_provider_registry,
    LLMRequest,
    LLMResponse,
)

logger = logging.getLogger(__name__)


class AgentLLMRouter:
    """
    Routes agents to their optimal LLM models.

    Features:
    - Database-driven configuration (AgentLLMConfig)
    - Automatic fallback to secondary model on failure
    - Performance tracking and logging
    - Task-specific model overrides
    - Cost optimization

    Usage:
        router = AgentLLMRouter()
        response = router.route_completion(
            agent_name='CodeGeneratorAgent',
            prompt='Write a Python function to...',
            system_prompt='You are an expert Python developer.',
            user=request.user  # Optional for tracking
        )
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.registry = get_llm_provider_registry()
            self._config_cache: Dict[str, Dict] = {}
            self._cache_loaded = False
            AgentLLMRouter._initialized = True
            logger.info("🧠 AgentLLMRouter initialized")

    def _load_config_cache(self):
        """Load agent configurations from database into memory"""
        if self._cache_loaded:
            return

        try:
            from core.models_llm_routing import AgentLLMConfig

            configs = AgentLLMConfig.objects.filter(is_active=True).select_related(
                'primary_model', 'primary_model__provider',
                'fallback_model', 'fallback_model__provider'
            )

            for config in configs:
                primary = None
                fallback = None

                if config.primary_model:
                    primary = {
                        'provider': config.primary_model.provider.name,
                        'model_id': config.primary_model.model_id,
                        'model_uuid': str(config.primary_model.id),
                    }

                if config.fallback_model:
                    fallback = {
                        'provider': config.fallback_model.provider.name,
                        'model_id': config.fallback_model.model_id,
                        'model_uuid': str(config.fallback_model.id),
                    }

                self._config_cache[config.agent_name] = {
                    'primary': primary,
                    'fallback': fallback,
                    'temperature': config.temperature,
                    'max_tokens': config.max_tokens,
                    'task_overrides': config.task_overrides or {},
                    'custom_params': config.custom_params or {},
                    'use_auto_selection': config.use_auto_selection,
                }

            self._cache_loaded = True
            logger.info(f"📋 Loaded {len(self._config_cache)} agent LLM configs")

        except Exception as e:
            logger.warning(f"Could not load agent configs from DB: {e}")
            # Fall back to in-memory defaults
            self._load_default_configs()

    def _load_default_configs(self):
        """Load default configurations from the models file"""
        from core.models_llm_routing import DEFAULT_AGENT_LLM_CONFIGS

        for config in DEFAULT_AGENT_LLM_CONFIGS:
            agent_name = config['agent_name']
            primary_parts = config['primary'].split(':')
            fallback_parts = config['fallback'].split(':')

            self._config_cache[agent_name] = {
                'primary': {
                    'provider': primary_parts[0],
                    'model_id': primary_parts[1],
                },
                'fallback': {
                    'provider': fallback_parts[0],
                    'model_id': fallback_parts[1],
                },
                'temperature': 0.7,
                'max_tokens': 2000,
                'task_overrides': {},
                'custom_params': {},
                'use_auto_selection': False,
            }

        self._cache_loaded = True
        logger.info(f"📋 Loaded {len(self._config_cache)} default agent configs")

    def get_agent_config(self, agent_name: str) -> Dict:
        """Get LLM configuration for an agent"""
        self._load_config_cache()

        if agent_name in self._config_cache:
            return self._config_cache[agent_name]

        # Return default config if agent not found
        return {
            'primary': {'provider': 'openai', 'model_id': 'gpt-5.1'},
            'fallback': {'provider': 'anthropic', 'model_id': 'claude-3.5-sonnet'},
            'temperature': 0.7,
            'max_tokens': 2000,
            'task_overrides': {},
            'custom_params': {},
            'use_auto_selection': False,
        }

    def route_completion(
        self,
        agent_name: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        messages: Optional[List[Dict]] = None,
        task_type: Optional[str] = None,
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[Dict] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        user: Optional[Any] = None,
        metadata: Optional[Dict] = None,
    ) -> LLMResponse:
        """
        Route a completion request to the appropriate LLM for an agent.

        Args:
            agent_name: Name of the calling agent (e.g., 'CodeGeneratorAgent')
            prompt: The prompt text
            system_prompt: System prompt (optional)
            messages: Full message history (optional, overrides prompt)
            task_type: Type of task for override lookup (optional)
            tools: Tool definitions for function calling (optional)
            tool_choice: Tool choice configuration (optional)
            max_tokens: Override max tokens (optional)
            temperature: Override temperature (optional)
            user: User object for tracking (optional)
            metadata: Additional metadata (optional)

        Returns:
            LLMResponse with the completion
        """
        config = self.get_agent_config(agent_name)

        # Check for task-specific override
        model_config = config['primary']
        if task_type and task_type in config.get('task_overrides', {}):
            override = config['task_overrides'][task_type]
            if 'provider' in override and 'model_id' in override:
                model_config = override
                logger.debug(f"Using task override for {agent_name}/{task_type}")

        # Build request
        request = LLMRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            messages=messages,
            max_tokens=max_tokens or config.get('max_tokens', 2000),
            temperature=temperature if temperature is not None else config.get('temperature', 0.7),
            tools=tools,
            tool_choice=tool_choice,
            metadata=metadata or {},
        )

        # Try primary model
        start_time = time.time()
        response = self.registry.complete(
            provider=model_config['provider'],
            model_id=model_config['model_id'],
            request=request
        )

        # Log the call
        self._log_call(
            agent_name=agent_name,
            provider=model_config['provider'],
            model_id=model_config['model_id'],
            response=response,
            task_type=task_type,
            user=user,
            was_fallback=False,
        )

        # If primary failed, try fallback
        if not response.success and config.get('fallback'):
            fallback_config = config['fallback']
            logger.warning(
                f"Primary model failed for {agent_name}, trying fallback: "
                f"{fallback_config['provider']}:{fallback_config['model_id']}"
            )

            response = self.registry.complete(
                provider=fallback_config['provider'],
                model_id=fallback_config['model_id'],
                request=request
            )

            # Log fallback call
            self._log_call(
                agent_name=agent_name,
                provider=fallback_config['provider'],
                model_id=fallback_config['model_id'],
                response=response,
                task_type=task_type,
                user=user,
                was_fallback=True,
            )

        return response

    def _log_call(
        self,
        agent_name: str,
        provider: str,
        model_id: str,
        response: LLMResponse,
        task_type: Optional[str],
        user: Optional[Any],
        was_fallback: bool,
    ):
        """Log an LLM call to the database for tracking"""
        try:
            from core.models_llm_routing import LLMCallLog, AgentLLMConfig

            # Create log entry
            LLMCallLog.objects.create(
                agent_name=agent_name,
                user=user,
                provider=provider,
                model_id=model_id,
                was_fallback=was_fallback,
                was_auto_selected=False,
                task_type=task_type or '',
                prompt_tokens=response.tokens_input,
                success=response.success,
                completion_tokens=response.tokens_output,
                total_tokens=response.tokens_total,
                latency_ms=response.latency_ms,
                cost=Decimal(str(response.cost)),
                error_type='' if response.success else 'api_error',
                error_message=response.error or '',
            )

            # Update agent config stats
            try:
                config = AgentLLMConfig.objects.get(agent_name=agent_name, is_active=True)
                config.total_calls += 1
                if response.success:
                    config.successful_calls += 1
                config.total_tokens_used += response.tokens_total
                config.total_cost += Decimal(str(response.cost))

                # Update rolling average latency
                if config.avg_latency_ms == 0:
                    config.avg_latency_ms = response.latency_ms
                else:
                    # Exponential moving average
                    alpha = 0.1
                    config.avg_latency_ms = (alpha * response.latency_ms +
                                            (1 - alpha) * config.avg_latency_ms)

                config.save(update_fields=[
                    'total_calls', 'successful_calls', 'total_tokens_used',
                    'total_cost', 'avg_latency_ms', 'updated_at'
                ])
            except Exception:
                pass  # Config may not exist in DB yet

        except Exception as e:
            logger.warning(f"Failed to log LLM call: {e}")

    def get_model_for_task(
        self,
        task_type: str,
        requirements: Optional[Dict] = None,
    ) -> Dict[str, str]:
        """
        Get the optimal model for a specific task type.

        Used for auto-selection mode.

        Args:
            task_type: Type of task (coding, creative, analysis, etc.)
            requirements: Optional requirements (speed, cost, quality)

        Returns:
            Dict with 'provider' and 'model_id'
        """
        # Task type to model mapping for auto-selection
        task_models = {
            'coding': {'provider': 'deepseek', 'model_id': 'deepseek-coder'},
            'code_review': {'provider': 'anthropic', 'model_id': 'claude-3.5-sonnet'},
            'creative': {'provider': 'anthropic', 'model_id': 'claude-3.5-sonnet'},
            'analysis': {'provider': 'openai', 'model_id': 'gpt-5.1'},
            'research': {'provider': 'gemini', 'model_id': 'gemini-2.0-pro'},
            'reasoning': {'provider': 'anthropic', 'model_id': 'claude-3.5-opus'},
            'quick_task': {'provider': 'openai', 'model_id': 'gpt-5-mini'},
            'routing': {'provider': 'openai', 'model_id': 'gpt-5-mini'},
            'legal': {'provider': 'anthropic', 'model_id': 'claude-3.5-sonnet'},
            'financial': {'provider': 'openai', 'model_id': 'gpt-5.1'},
            'private': {'provider': 'ollama', 'model_id': 'llama3.1:70b'},
        }

        if task_type in task_models:
            return task_models[task_type]

        # Check requirements for optimization
        requirements = requirements or {}

        if requirements.get('prioritize_speed'):
            return {'provider': 'openai', 'model_id': 'gpt-5-mini'}

        if requirements.get('prioritize_cost'):
            return {'provider': 'deepseek', 'model_id': 'deepseek-chat'}

        if requirements.get('prioritize_quality'):
            return {'provider': 'anthropic', 'model_id': 'claude-3.5-opus'}

        if requirements.get('prioritize_privacy'):
            return {'provider': 'ollama', 'model_id': 'llama3.1:70b'}

        # Default
        return {'provider': 'openai', 'model_id': 'gpt-5.1'}

    def invalidate_cache(self):
        """Invalidate the config cache to reload from database"""
        self._config_cache = {}
        self._cache_loaded = False
        logger.info("🔄 Agent LLM config cache invalidated")

    def get_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        try:
            from core.models_llm_routing import LLMCallLog, AgentLLMConfig
            from django.db.models import Sum, Avg, Count
            from datetime import timedelta

            now = timezone.now()
            last_24h = now - timedelta(hours=24)
            last_7d = now - timedelta(days=7)

            # Last 24 hours stats
            recent_logs = LLMCallLog.objects.filter(created_at__gte=last_24h)
            stats_24h = recent_logs.aggregate(
                total_calls=Count('id'),
                successful_calls=Count('id', filter=models.Q(success=True)),
                total_tokens=Sum('total_tokens'),
                total_cost=Sum('cost'),
                avg_latency=Avg('latency_ms'),
            )

            # By provider
            by_provider = recent_logs.values('provider').annotate(
                calls=Count('id'),
                tokens=Sum('total_tokens'),
                cost=Sum('cost'),
            )

            # By agent
            by_agent = recent_logs.values('agent_name').annotate(
                calls=Count('id'),
                tokens=Sum('total_tokens'),
                cost=Sum('cost'),
            ).order_by('-calls')[:10]

            return {
                'last_24h': stats_24h,
                'by_provider': list(by_provider),
                'top_agents': list(by_agent),
                'available_providers': self.registry.get_available_providers(),
                'configured_agents': len(self._config_cache),
            }

        except Exception as e:
            logger.warning(f"Failed to get routing stats: {e}")
            return {
                'error': str(e),
                'available_providers': self.registry.get_available_providers(),
            }

    def health_check(self) -> Dict[str, Any]:
        """Check health of the routing system"""
        return {
            'router_status': 'healthy',
            'providers': self.registry.health_check_all(),
            'configured_agents': len(self._config_cache) if self._cache_loaded else 'not_loaded',
            'cache_loaded': self._cache_loaded,
        }


# =============================================================================
# Singleton Access
# =============================================================================

_router_instance: Optional[AgentLLMRouter] = None


def get_agent_llm_router() -> AgentLLMRouter:
    """Get singleton instance of Agent LLM Router"""
    global _router_instance
    if _router_instance is None:
        _router_instance = AgentLLMRouter()
    return _router_instance


def route_agent_completion(
    agent_name: str,
    prompt: str,
    system_prompt: Optional[str] = None,
    **kwargs
) -> LLMResponse:
    """
    Convenience function to route an agent completion.

    Usage:
        response = route_agent_completion(
            agent_name='CodeGeneratorAgent',
            prompt='Write a function to...',
            system_prompt='You are an expert.'
        )
        if response.success:
            print(response.content)
    """
    router = get_agent_llm_router()
    return router.route_completion(
        agent_name=agent_name,
        prompt=prompt,
        system_prompt=system_prompt,
        **kwargs
    )
