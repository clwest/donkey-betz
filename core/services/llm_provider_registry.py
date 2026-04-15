"""
LLM Provider Registry - Unified Multi-Model Interface
Session 697: Enhanced Nervous System

This service provides a unified interface to multiple LLM providers:
- OpenAI (GPT-5-mini, GPT-5.1, GPT-5.2)
- Anthropic (Claude 3.5 Sonnet, Haiku, Opus)
- DeepSeek (Coder V2, Chat)
- Gemini (2.0 Flash, 2.0 Pro)
- Ollama (Local models - Llama, CodeLlama, Mistral)

Each provider is abstracted behind a common interface, allowing
agents to use any model without knowing provider-specific details.
"""

import os
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from functools import lru_cache

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class LLMResponse:
    """Standardized response from any LLM provider"""
    success: bool
    content: str
    provider: str
    model: str
    tokens_input: int = 0
    tokens_output: int = 0
    tokens_total: int = 0
    cost: float = 0.0
    latency_ms: int = 0
    tool_calls: Optional[List[Dict]] = None
    error: Optional[str] = None
    raw_response: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMRequest:
    """Standardized request to any LLM provider"""
    prompt: str
    system_prompt: Optional[str] = None
    messages: Optional[List[Dict]] = None  # For chat-based APIs
    max_tokens: int = 2000
    temperature: float = 0.7
    tools: Optional[List[Dict]] = None
    tool_choice: Optional[Dict] = None
    stream: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Base Provider Interface
# =============================================================================

class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
        self.client = None
        self._initialize()

    @abstractmethod
    def _initialize(self):
        """Initialize the provider client"""
        pass

    @abstractmethod
    def complete(self, request: LLMRequest, model_id: str) -> LLMResponse:
        """Generate completion from the model"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available"""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider identifier"""
        pass

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on provider"""
        try:
            start = time.time()
            available = self.is_available()
            latency = int((time.time() - start) * 1000)
            return {
                'provider': self.provider_name,
                'available': available,
                'latency_ms': latency,
                'error': None
            }
        except Exception as e:
            return {
                'provider': self.provider_name,
                'available': False,
                'latency_ms': 0,
                'error': str(e)
            }


# =============================================================================
# OpenAI Provider (GPT-5 Family)
# =============================================================================

class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider supporting GPT-5-mini, GPT-5.1, GPT-5.2"""

    @property
    def provider_name(self) -> str:
        return 'openai'

    def _initialize(self):
        try:
            from openai import OpenAI
            import httpx
            api_key = self.api_key or os.getenv('OPENAI_API_KEY')
            if api_key and api_key not in ['', 'your-key-here']:
                # Session 831: Add timeout configuration for reliability
                timeout = httpx.Timeout(60.0, connect=20.0, read=90.0)
                self.client = OpenAI(api_key=api_key, timeout=timeout, max_retries=2)
                logger.info("✅ OpenAI provider initialized (timeout: 60s)")
            else:
                logger.warning("⚠️ OpenAI API key not configured")
        except ImportError:
            logger.error("❌ OpenAI library not installed")

    def is_available(self) -> bool:
        return self.client is not None

    def complete(self, request: LLMRequest, model_id: str) -> LLMResponse:
        if not self.client:
            return LLMResponse(
                success=False,
                content='',
                provider=self.provider_name,
                model=model_id,
                error='OpenAI client not initialized'
            )

        start_time = time.time()

        try:
            # Build messages
            messages = request.messages or []
            if not messages:
                if request.system_prompt:
                    messages.append({'role': 'system', 'content': request.system_prompt})
                messages.append({'role': 'user', 'content': request.prompt})

            # Determine API to use based on model
            if model_id.startswith('gpt-5'):
                # Use Responses API for GPT-5 family
                response = self._call_responses_api(request, model_id, messages)
            else:
                # Use Chat Completions for older models
                response = self._call_chat_api(request, model_id, messages)

            latency_ms = int((time.time() - start_time) * 1000)
            response.latency_ms = latency_ms
            return response

        except Exception as e:
            # Session 841: Record errors for provider health tracking
            error_type = 'server_error'
            try:
                from openai import RateLimitError, APIStatusError, APITimeoutError, APIConnectionError
                from core.services.provider_health_tracker import record_provider_error

                if isinstance(e, RateLimitError):
                    error_type = 'rate_limit'
                elif isinstance(e, APITimeoutError):
                    error_type = 'timeout'
                elif isinstance(e, APIConnectionError):
                    error_type = 'connection_error'
                elif isinstance(e, APIStatusError) and hasattr(e, 'status_code'):
                    if e.status_code >= 500:
                        error_type = 'server_error'

                record_provider_error('openai', error_type)
            except ImportError as _hi:
                # Session 1103c: was 'except ImportError: pass' which
                # silently dropped provider error tracking for OpenAI
                # if the health tracker module failed to import. The
                # tracker is what feeds is_provider_degraded() which
                # in turn feeds agent_llm_router fallback decisions —
                # without it, the router can't route around degraded
                # providers, and every error here is invisible.
                logger.warning(
                    "llm_provider_registry: provider_health_tracker "
                    "unavailable for OpenAI error recording (%s) — "
                    "router cannot react to OpenAI degradation",
                    _hi,
                )

            logger.error(f"OpenAI API error ({error_type}): {e}")
            return LLMResponse(
                success=False,
                content='',
                provider=self.provider_name,
                model=model_id,
                error=str(e),
                latency_ms=int((time.time() - start_time) * 1000)
            )

    def _call_responses_api(self, request: LLMRequest, model_id: str, messages: List[Dict]) -> LLMResponse:
        """Call OpenAI Responses API (for GPT-5 family)"""
        # Combine messages into input
        full_input = ""
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'system':
                full_input += f"{content}\n\n"
            else:
                full_input += f"User: {content}\n"

        params = {
            'model': model_id,
            'input': full_input.strip(),
            'max_output_tokens': request.max_tokens,
        }

        # Add reasoning effort based on metadata
        reasoning_effort = request.metadata.get('reasoning_effort', 'low')
        params['reasoning'] = {'effort': reasoning_effort}

        if request.tools:
            params['tools'] = request.tools
        if request.tool_choice:
            params['tool_choice'] = request.tool_choice

        response = self.client.responses.create(**params)

        # Parse response
        content = response.output_text if hasattr(response, 'output_text') else ''

        # Parse tool calls
        tool_calls = None
        if hasattr(response, 'output') and response.output:
            function_calls = [item for item in response.output
                           if hasattr(item, 'type') and item.type == 'function_call']
            if function_calls:
                tool_calls = [
                    {
                        'id': tc.call_id if hasattr(tc, 'call_id') else str(i),
                        'type': 'function',
                        'function': {'name': tc.name, 'arguments': tc.arguments}
                    } for i, tc in enumerate(function_calls)
                ]

        # Calculate tokens and cost
        usage = response.usage if hasattr(response, 'usage') else None
        tokens_input = usage.input_tokens if usage and hasattr(usage, 'input_tokens') else 0
        tokens_output = usage.output_tokens if usage and hasattr(usage, 'output_tokens') else 0
        reasoning_tokens = usage.reasoning_tokens if usage and hasattr(usage, 'reasoning_tokens') else 0

        # Cost calculation (GPT-5.1 pricing)
        cost = self._calculate_cost(model_id, tokens_input + reasoning_tokens, tokens_output)

        return LLMResponse(
            success=True,
            content=content,
            provider=self.provider_name,
            model=model_id,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            tokens_total=tokens_input + tokens_output + reasoning_tokens,
            cost=cost,
            tool_calls=tool_calls,
            raw_response=response,
            metadata={'reasoning_tokens': reasoning_tokens}
        )

    def _call_chat_api(self, request: LLMRequest, model_id: str, messages: List[Dict]) -> LLMResponse:
        """Call OpenAI Chat Completions API (for non-GPT-5 models)"""
        params = {
            'model': model_id,
            'messages': messages,
            'max_tokens': request.max_tokens,
            'temperature': request.temperature,
        }

        if request.tools:
            params['tools'] = request.tools
        if request.tool_choice:
            params['tool_choice'] = request.tool_choice

        response = self.client.chat.completions.create(**params)

        content = response.choices[0].message.content or ''
        tool_calls = None
        if response.choices[0].message.tool_calls:
            tool_calls = [
                {
                    'id': tc.id,
                    'type': 'function',
                    'function': {'name': tc.function.name, 'arguments': tc.function.arguments}
                } for tc in response.choices[0].message.tool_calls
            ]

        tokens_input = response.usage.prompt_tokens if response.usage else 0
        tokens_output = response.usage.completion_tokens if response.usage else 0
        cost = self._calculate_cost(model_id, tokens_input, tokens_output)

        return LLMResponse(
            success=True,
            content=content,
            provider=self.provider_name,
            model=model_id,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            tokens_total=tokens_input + tokens_output,
            cost=cost,
            tool_calls=tool_calls,
            raw_response=response
        )

    def _calculate_cost(self, model_id: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on model pricing"""
        pricing = {
            'gpt-5-mini': (0.15, 0.60),      # per 1M tokens
            'gpt-5.1': (1.25, 10.00),
            'gpt-5.2': (5.00, 20.00),
            'gpt-4-turbo': (10.00, 30.00),
            'gpt-4o': (2.50, 10.00),
            'gpt-4o-mini': (0.15, 0.60),
        }
        input_price, output_price = pricing.get(model_id, (1.00, 3.00))
        return (input_tokens * input_price / 1_000_000) + (output_tokens * output_price / 1_000_000)


# =============================================================================
# Anthropic Provider (Claude Family)
# =============================================================================

class AnthropicProvider(BaseLLMProvider):
    """Anthropic provider supporting Claude 3.5 Sonnet, Haiku, Opus"""

    @property
    def provider_name(self) -> str:
        return 'anthropic'

    def _initialize(self):
        try:
            from anthropic import Anthropic
            import httpx
            api_key = self.api_key or os.getenv('ANTHROPIC_API_KEY')
            if api_key and api_key not in ['', 'your-key-here']:
                # Session 831: Add timeout configuration for reliability
                timeout = httpx.Timeout(60.0, connect=20.0, read=90.0)
                self.client = Anthropic(api_key=api_key, timeout=timeout, max_retries=2)
                logger.info("✅ Anthropic provider initialized (timeout: 60s)")
            else:
                logger.warning("⚠️ Anthropic API key not configured")
        except ImportError:
            logger.error("❌ Anthropic library not installed")

    def is_available(self) -> bool:
        return self.client is not None

    def complete(self, request: LLMRequest, model_id: str) -> LLMResponse:
        if not self.client:
            return LLMResponse(
                success=False,
                content='',
                provider=self.provider_name,
                model=model_id,
                error='Anthropic client not initialized'
            )

        start_time = time.time()

        try:
            # Build messages
            messages = []
            system_prompt = request.system_prompt or ''

            if request.messages:
                for msg in request.messages:
                    if msg.get('role') == 'system':
                        system_prompt = msg.get('content', '')
                    else:
                        messages.append({
                            'role': msg.get('role', 'user'),
                            'content': msg.get('content', '')
                        })
            else:
                messages.append({'role': 'user', 'content': request.prompt})

            params = {
                'model': model_id,
                'messages': messages,
                'max_tokens': request.max_tokens,
                'temperature': request.temperature,
            }

            if system_prompt:
                params['system'] = system_prompt

            if request.tools:
                # Convert OpenAI tool format to Anthropic format
                params['tools'] = self._convert_tools(request.tools)

            response = self.client.messages.create(**params)

            # Parse response
            content = ''
            tool_calls = None
            for block in response.content:
                if hasattr(block, 'text'):
                    content += block.text
                elif hasattr(block, 'type') and block.type == 'tool_use':
                    if tool_calls is None:
                        tool_calls = []
                    tool_calls.append({
                        'id': block.id,
                        'type': 'function',
                        'function': {
                            'name': block.name,
                            'arguments': str(block.input)
                        }
                    })

            tokens_input = response.usage.input_tokens if response.usage else 0
            tokens_output = response.usage.output_tokens if response.usage else 0
            cost = self._calculate_cost(model_id, tokens_input, tokens_output)
            latency_ms = int((time.time() - start_time) * 1000)

            return LLMResponse(
                success=True,
                content=content,
                provider=self.provider_name,
                model=model_id,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                tokens_total=tokens_input + tokens_output,
                cost=cost,
                latency_ms=latency_ms,
                tool_calls=tool_calls,
                raw_response=response
            )

        except Exception as e:
            # Session 841: Record errors for provider health tracking
            error_type = 'server_error'
            try:
                from anthropic import RateLimitError, APIStatusError, APITimeoutError, APIConnectionError
                from core.services.provider_health_tracker import record_provider_error

                if isinstance(e, RateLimitError):
                    error_type = 'rate_limit'
                elif isinstance(e, APITimeoutError):
                    error_type = 'timeout'
                elif isinstance(e, APIConnectionError):
                    error_type = 'connection_error'
                elif isinstance(e, APIStatusError) and hasattr(e, 'status_code'):
                    if e.status_code >= 500:
                        error_type = 'server_error'

                record_provider_error('anthropic', error_type)
            except ImportError as _hi:
                # Session 1103c: same pattern as the OpenAI block
                # above — silent ImportError on the health tracker
                # leaves the router blind to Anthropic degradation.
                logger.warning(
                    "llm_provider_registry: provider_health_tracker "
                    "unavailable for Anthropic error recording (%s) — "
                    "router cannot react to Anthropic degradation",
                    _hi,
                )

            logger.error(f"Anthropic API error ({error_type}): {e}")
            return LLMResponse(
                success=False,
                content='',
                provider=self.provider_name,
                model=model_id,
                error=str(e),
                latency_ms=int((time.time() - start_time) * 1000)
            )

    def _convert_tools(self, openai_tools: List[Dict]) -> List[Dict]:
        """Convert OpenAI tool format to Anthropic format"""
        anthropic_tools = []
        for tool in openai_tools:
            if tool.get('type') == 'function':
                func = tool.get('function', {})
                anthropic_tools.append({
                    'name': func.get('name'),
                    'description': func.get('description', ''),
                    'input_schema': func.get('parameters', {})
                })
        return anthropic_tools

    def _calculate_cost(self, model_id: str, input_tokens: int, output_tokens: int) -> float:
        pricing = {
            'claude-3.5-sonnet': (3.00, 15.00),
            'claude-3.5-haiku': (0.25, 1.25),
            'claude-3.5-opus': (15.00, 75.00),
            'claude-3-sonnet-20240229': (3.00, 15.00),
            'claude-3-haiku-20240307': (0.25, 1.25),
        }
        input_price, output_price = pricing.get(model_id, (3.00, 15.00))
        return (input_tokens * input_price / 1_000_000) + (output_tokens * output_price / 1_000_000)


# =============================================================================
# DeepSeek Provider
# =============================================================================

class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek provider - excellent coding models at low cost"""

    @property
    def provider_name(self) -> str:
        return 'deepseek'

    def _initialize(self):
        try:
            from openai import OpenAI  # DeepSeek uses OpenAI-compatible API
            import httpx
            api_key = self.api_key or os.getenv('DEEPSEEK_API_KEY')
            base_url = self.base_url or 'https://api.deepseek.com'
            if api_key and api_key not in ['', 'your-key-here']:
                # Session 831: Add timeout configuration for reliability
                timeout = httpx.Timeout(60.0, connect=20.0, read=90.0)
                self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout, max_retries=2)
                logger.info("✅ DeepSeek provider initialized (timeout: 60s)")
            else:
                logger.warning("⚠️ DeepSeek API key not configured")
        except ImportError:
            logger.error("❌ OpenAI library not installed (needed for DeepSeek)")

    def is_available(self) -> bool:
        return self.client is not None

    def complete(self, request: LLMRequest, model_id: str) -> LLMResponse:
        if not self.client:
            return LLMResponse(
                success=False,
                content='',
                provider=self.provider_name,
                model=model_id,
                error='DeepSeek client not initialized'
            )

        start_time = time.time()

        try:
            messages = request.messages or []
            if not messages:
                if request.system_prompt:
                    messages.append({'role': 'system', 'content': request.system_prompt})
                messages.append({'role': 'user', 'content': request.prompt})

            params = {
                'model': model_id,
                'messages': messages,
                'max_tokens': request.max_tokens,
                'temperature': request.temperature,
            }

            if request.tools:
                params['tools'] = request.tools
            if request.tool_choice:
                params['tool_choice'] = request.tool_choice

            response = self.client.chat.completions.create(**params)

            content = response.choices[0].message.content or ''
            tool_calls = None
            if response.choices[0].message.tool_calls:
                tool_calls = [
                    {
                        'id': tc.id,
                        'type': 'function',
                        'function': {'name': tc.function.name, 'arguments': tc.function.arguments}
                    } for tc in response.choices[0].message.tool_calls
                ]

            tokens_input = response.usage.prompt_tokens if response.usage else 0
            tokens_output = response.usage.completion_tokens if response.usage else 0
            cost = self._calculate_cost(model_id, tokens_input, tokens_output)
            latency_ms = int((time.time() - start_time) * 1000)

            return LLMResponse(
                success=True,
                content=content,
                provider=self.provider_name,
                model=model_id,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                tokens_total=tokens_input + tokens_output,
                cost=cost,
                latency_ms=latency_ms,
                tool_calls=tool_calls,
                raw_response=response
            )

        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            return LLMResponse(
                success=False,
                content='',
                provider=self.provider_name,
                model=model_id,
                error=str(e),
                latency_ms=int((time.time() - start_time) * 1000)
            )

    def _calculate_cost(self, model_id: str, input_tokens: int, output_tokens: int) -> float:
        pricing = {
            'deepseek-coder': (0.14, 0.28),
            'deepseek-chat': (0.07, 0.14),
        }
        input_price, output_price = pricing.get(model_id, (0.14, 0.28))
        return (input_tokens * input_price / 1_000_000) + (output_tokens * output_price / 1_000_000)


# =============================================================================
# Together AI Provider (hosts DeepSeek, Llama, Mixtral, Qwen)
# =============================================================================

class TogetherProvider(BaseLLMProvider):
    """Together AI provider - hosts many open-source models including DeepSeek"""

    @property
    def provider_name(self) -> str:
        return 'together'

    def _initialize(self):
        try:
            from openai import OpenAI  # Together uses OpenAI-compatible API
            import httpx
            api_key = self.api_key or os.getenv('TOGETHER_AI_API_KEY')
            base_url = self.base_url or 'https://api.together.xyz/v1'
            if api_key and api_key not in ['', 'your-key-here']:
                # Session 831: Increase timeout to 60s connect, 120s read for Together AI
                # Together AI can be slow, especially for larger models
                timeout = httpx.Timeout(60.0, connect=30.0, read=120.0)
                self.client = OpenAI(
                    api_key=api_key,
                    base_url=base_url,
                    timeout=timeout,
                    max_retries=2  # Retry failed requests
                )
                logger.info("✅ Together AI provider initialized (timeout: 60s connect, 120s read)")
            else:
                logger.warning("⚠️ Together AI API key not configured")
        except ImportError:
            logger.error("❌ OpenAI library not installed (needed for Together)")

    def is_available(self) -> bool:
        return self.client is not None

    def complete(self, request: LLMRequest, model_id: str) -> LLMResponse:
        if not self.client:
            return LLMResponse(
                success=False,
                content='',
                provider=self.provider_name,
                model=model_id,
                error='Together AI client not initialized'
            )

        start_time = time.time()

        try:
            messages = request.messages or []
            if not messages:
                if request.system_prompt:
                    messages.append({'role': 'system', 'content': request.system_prompt})
                messages.append({'role': 'user', 'content': request.prompt})

            params = {
                'model': model_id,
                'messages': messages,
                'max_tokens': request.max_tokens,
                'temperature': request.temperature,
            }

            if request.tools:
                params['tools'] = request.tools
            if request.tool_choice:
                params['tool_choice'] = request.tool_choice

            response = self.client.chat.completions.create(**params)

            content = response.choices[0].message.content or ''
            tool_calls = None
            if response.choices[0].message.tool_calls:
                tool_calls = [
                    {
                        'id': tc.id,
                        'type': 'function',
                        'function': {'name': tc.function.name, 'arguments': tc.function.arguments}
                    } for tc in response.choices[0].message.tool_calls
                ]

            tokens_input = response.usage.prompt_tokens if response.usage else 0
            tokens_output = response.usage.completion_tokens if response.usage else 0
            cost = self._calculate_cost(model_id, tokens_input, tokens_output)
            latency_ms = int((time.time() - start_time) * 1000)

            return LLMResponse(
                success=True,
                content=content,
                provider=self.provider_name,
                model=model_id,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                tokens_total=tokens_input + tokens_output,
                cost=cost,
                latency_ms=latency_ms,
                tool_calls=tool_calls,
                raw_response=response
            )

        except Exception as e:
            logger.error(f"Together AI API error: {e}")
            return LLMResponse(
                success=False,
                content='',
                provider=self.provider_name,
                model=model_id,
                error=str(e),
                latency_ms=int((time.time() - start_time) * 1000)
            )

    def _calculate_cost(self, model_id: str, input_tokens: int, output_tokens: int) -> float:
        # Together AI pricing per 1M tokens (approximate)
        pricing = {
            'deepseek-ai/deepseek-coder-33b-instruct': (0.80, 0.80),
            'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo': (0.88, 0.88),
            'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo': (0.18, 0.18),
            'mistralai/Mixtral-8x7B-Instruct-v0.1': (0.60, 0.60),
            'Qwen/Qwen2.5-Coder-32B-Instruct': (0.80, 0.80),
        }
        input_price, output_price = pricing.get(model_id, (0.80, 0.80))
        return (input_tokens * input_price / 1_000_000) + (output_tokens * output_price / 1_000_000)


# =============================================================================
# Gemini Provider
# =============================================================================

class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini provider - massive context windows.

    Session 698: Updated to use new google-genai SDK (GA as of May 2025).
    The old google-generativeai library was deprecated Nov 30, 2025.

    Supports both GEMINI_API_KEY and GOOGLE_AI_STUDIO_API_KEY env vars.
    """

    @property
    def provider_name(self) -> str:
        return 'gemini'

    def _initialize(self):
        try:
            from google import genai
            from google.genai.types import HttpOptions

            # Check for API key (support both env var names)
            api_key = (
                self.api_key or
                os.getenv('GOOGLE_AI_STUDIO_API_KEY') or
                os.getenv('GEMINI_API_KEY')
            )

            if api_key and api_key not in ['', 'your-key-here']:
                # Session 1084: Enforce request timeout so a hung Gemini
                # call can't wedge the worker. HttpOptions.timeout is in
                # milliseconds. 90s matches the 90s read timeout used by
                # OpenAI/Anthropic/DeepSeek providers above.
                http_options = HttpOptions(timeout=90_000)
                self.client = genai.Client(
                    api_key=api_key,
                    http_options=http_options,
                )
                logger.info("✅ Gemini provider initialized (google-genai SDK, timeout: 90s)")
            else:
                logger.warning("⚠️ Gemini API key not configured (set GOOGLE_AI_STUDIO_API_KEY or GEMINI_API_KEY)")
        except ImportError:
            logger.warning("⚠️ google-genai library not installed (pip install google-genai)")

    def is_available(self) -> bool:
        return self.client is not None

    def complete(self, request: LLMRequest, model_id: str) -> LLMResponse:
        if not self.client:
            return LLMResponse(
                success=False,
                content='',
                provider=self.provider_name,
                model=model_id,
                error='Gemini client not initialized'
            )

        start_time = time.time()

        try:
            # Build prompt
            full_prompt = ''
            if request.system_prompt:
                full_prompt = f"{request.system_prompt}\n\n"
            if request.messages:
                for msg in request.messages:
                    if msg.get('role') == 'user':
                        full_prompt += msg.get('content', '') + '\n'
            else:
                full_prompt += request.prompt

            # New SDK uses client.models.generate_content()
            config = {
                'temperature': request.temperature,
                'max_output_tokens': request.max_tokens,
            }

            response = self.client.models.generate_content(
                model=model_id,
                contents=full_prompt,
                config=config
            )

            content = response.text if hasattr(response, 'text') else ''

            # Get token counts if available, otherwise estimate
            usage = getattr(response, 'usage_metadata', None)
            if usage:
                tokens_input = getattr(usage, 'prompt_token_count', len(full_prompt) // 4)
                tokens_output = getattr(usage, 'candidates_token_count', len(content) // 4)
            else:
                tokens_input = len(full_prompt) // 4
                tokens_output = len(content) // 4

            cost = self._calculate_cost(model_id, tokens_input, tokens_output)
            latency_ms = int((time.time() - start_time) * 1000)

            return LLMResponse(
                success=True,
                content=content,
                provider=self.provider_name,
                model=model_id,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                tokens_total=tokens_input + tokens_output,
                cost=cost,
                latency_ms=latency_ms,
                raw_response=response
            )

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return LLMResponse(
                success=False,
                content='',
                provider=self.provider_name,
                model=model_id,
                error=str(e),
                latency_ms=int((time.time() - start_time) * 1000)
            )

    def _calculate_cost(self, model_id: str, input_tokens: int, output_tokens: int) -> float:
        # Pricing per 1M tokens (Jan 2026)
        pricing = {
            'gemini-2.0-flash': (0.075, 0.30),
            'gemini-2.5-flash': (0.075, 0.30),
            'gemini-2.0-pro': (1.25, 5.00),
            'gemini-2.5-pro': (1.25, 5.00),
            'gemini-pro': (0.50, 1.50),
        }
        input_price, output_price = pricing.get(model_id, (0.50, 1.50))
        return (input_tokens * input_price / 1_000_000) + (output_tokens * output_price / 1_000_000)


# =============================================================================
# Ollama Provider (Local Models)
# =============================================================================

class OllamaProvider(BaseLLMProvider):
    """Ollama provider for local models - free, private, offline"""

    @property
    def provider_name(self) -> str:
        return 'ollama'

    def _initialize(self):
        base_url = self.base_url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        try:
            import requests
            # Check if Ollama is running
            response = requests.get(f"{base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                self.base_url = base_url
                self.client = True
                logger.info(f"✅ Ollama provider initialized at {base_url}")
            else:
                logger.warning(f"⚠️ Ollama not responding at {base_url}")
        except Exception as e:
            logger.warning(f"⚠️ Ollama not available: {e}")

    def is_available(self) -> bool:
        return self.client is not None

    def complete(self, request: LLMRequest, model_id: str) -> LLMResponse:
        if not self.client:
            return LLMResponse(
                success=False,
                content='',
                provider=self.provider_name,
                model=model_id,
                error='Ollama not available'
            )

        start_time = time.time()

        try:
            import requests

            # Build prompt
            full_prompt = ''
            if request.system_prompt:
                full_prompt = f"System: {request.system_prompt}\n\n"
            if request.messages:
                for msg in request.messages:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    full_prompt += f"{role.capitalize()}: {content}\n"
            else:
                full_prompt += f"User: {request.prompt}\n"
            full_prompt += "Assistant:"

            payload = {
                'model': model_id,
                'prompt': full_prompt,
                'stream': False,
                'options': {
                    'temperature': request.temperature,
                    'num_predict': request.max_tokens,
                }
            }

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            data = response.json()

            content = data.get('response', '')
            tokens_input = data.get('prompt_eval_count', 0)
            tokens_output = data.get('eval_count', 0)
            latency_ms = int((time.time() - start_time) * 1000)

            return LLMResponse(
                success=True,
                content=content,
                provider=self.provider_name,
                model=model_id,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                tokens_total=tokens_input + tokens_output,
                cost=0.0,  # Local models are free
                latency_ms=latency_ms,
                raw_response=data
            )

        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return LLMResponse(
                success=False,
                content='',
                provider=self.provider_name,
                model=model_id,
                error=str(e),
                latency_ms=int((time.time() - start_time) * 1000)
            )


# =============================================================================
# Provider Registry - Central Access Point
# =============================================================================

class LLMProviderRegistry:
    """
    Central registry for all LLM providers.

    Provides unified access to multiple providers through a single interface.
    Handles provider initialization, health checking, and model routing.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.providers: Dict[str, BaseLLMProvider] = {}
            self._initialize_providers()
            self._initialized = True

    def _initialize_providers(self):
        """Initialize all configured providers"""
        logger.info("🧠 Initializing LLM Provider Registry...")

        # Initialize each provider
        provider_classes = {
            'openai': OpenAIProvider,
            'anthropic': AnthropicProvider,
            'deepseek': DeepSeekProvider,
            'together': TogetherProvider,  # Session 697: Together AI hosts DeepSeek, Llama, etc.
            'gemini': GeminiProvider,
            'ollama': OllamaProvider,
        }

        for name, provider_class in provider_classes.items():
            try:
                provider = provider_class()
                self.providers[name] = provider
                status = "✅" if provider.is_available() else "❌"
                logger.info(f"  {status} {name}: {'available' if provider.is_available() else 'not configured'}")
            except Exception as e:
                logger.error(f"  ❌ {name}: failed to initialize - {e}")

    def get_provider(self, provider_name: str) -> Optional[BaseLLMProvider]:
        """Get a specific provider by name"""
        return self.providers.get(provider_name)

    def complete(self, provider: str, model_id: str, request: LLMRequest) -> LLMResponse:
        """
        Make a completion request to any provider/model.

        Args:
            provider: Provider name ('openai', 'anthropic', etc.)
            model_id: Model identifier (e.g., 'gpt-5.1', 'claude-3.5-sonnet')
            request: Standardized LLMRequest

        Returns:
            Standardized LLMResponse
        """
        provider_instance = self.providers.get(provider)
        if not provider_instance:
            return LLMResponse(
                success=False,
                content='',
                provider=provider,
                model=model_id,
                error=f"Provider '{provider}' not found"
            )

        if not provider_instance.is_available():
            return LLMResponse(
                success=False,
                content='',
                provider=provider,
                model=model_id,
                error=f"Provider '{provider}' not available"
            )

        return provider_instance.complete(request, model_id)

    def health_check_all(self) -> Dict[str, Any]:
        """Check health of all providers"""
        results = {}
        for name, provider in self.providers.items():
            results[name] = provider.health_check()
        return results

    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return [name for name, provider in self.providers.items()
                if provider.is_available()]

    def get_available_models(self) -> List[Dict[str, str]]:
        """Get list of all available models across providers"""
        models = []
        for name, provider in self.providers.items():
            if provider.is_available():
                # This would ideally query the provider for available models
                # For now, return based on provider
                if name == 'openai':
                    models.extend([
                        {'provider': name, 'model': 'gpt-5-mini'},
                        {'provider': name, 'model': 'gpt-5.1'},
                        {'provider': name, 'model': 'gpt-5.2'},
                    ])
                elif name == 'anthropic':
                    models.extend([
                        {'provider': name, 'model': 'claude-3.5-sonnet'},
                        {'provider': name, 'model': 'claude-3.5-haiku'},
                        {'provider': name, 'model': 'claude-3.5-opus'},
                    ])
                elif name == 'deepseek':
                    models.extend([
                        {'provider': name, 'model': 'deepseek-coder'},
                        {'provider': name, 'model': 'deepseek-chat'},
                    ])
                elif name == 'gemini':
                    models.extend([
                        {'provider': name, 'model': 'gemini-2.0-flash'},
                        {'provider': name, 'model': 'gemini-2.0-pro'},
                    ])
        return models


# =============================================================================
# Singleton Access
# =============================================================================

_registry_instance: Optional[LLMProviderRegistry] = None


def get_llm_provider_registry() -> LLMProviderRegistry:
    """Get singleton instance of LLM Provider Registry"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = LLMProviderRegistry()
    return _registry_instance


def get_provider(provider_name: str) -> Optional[BaseLLMProvider]:
    """Convenience function to get a provider"""
    return get_llm_provider_registry().get_provider(provider_name)
