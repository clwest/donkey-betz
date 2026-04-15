"""
AI Providers Integration

Unified interface for multiple AI providers supporting content generation.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from django.conf import settings

logger = logging.getLogger(__name__)

# Import AI provider libraries
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    from google import generativeai as genai
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False


@dataclass
class GenerationResult:
    """Result from content generation"""
    success: bool
    content: str = ""
    token_usage: Dict[str, int] = None
    cost: float = 0.0
    generation_time_ms: int = 0
    model_used: str = ""
    error_message: str = ""
    
    def __post_init__(self):
        if self.token_usage is None:
            self.token_usage = {}


class BaseAIProvider(ABC):
    """Base class for AI providers"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize the provider's client"""
        pass
    
    @abstractmethod
    def generate_content(self, model: str, system_prompt: str, user_prompt: str, 
                        config: Dict[str, Any] = None) -> GenerationResult:
        """Generate content using the provider"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        pass
    
    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate generation cost"""
        # Default implementation - providers should override with actual pricing
        return 0.0


class OpenAIProvider(BaseAIProvider):
    """OpenAI provider implementation"""
    
    def __init__(self, api_key: str):
        if not HAS_OPENAI:
            raise ImportError("OpenAI library not installed")
        super().__init__(api_key)
        
        # Model pricing (per 1K tokens)
        self.pricing = {
            # GPT-5 Models (Released August 2025)
            'gpt-5': {'input': 1.25, 'output': 10.0},
            'gpt-5-mini': {'input': 0.25, 'output': 2.0},
            'gpt-5-nano': {'input': 0.05, 'output': 0.40},
            'gpt-5-chat-latest': {'input': 1.25, 'output': 10.0},
            # GPT-4 Models (kept for fallback)
            'gpt-5-mini': {'input': 0.03, 'output': 0.06},
            'gpt-5-mini': {'input': 0.01, 'output': 0.03},
            'gpt-5-mini': {'input': 0.01, 'output': 0.03},
            'gpt-5-mini': {'input': 0.005, 'output': 0.015},
            'gpt-5-nano': {'input': 0.001, 'output': 0.002},
            'gpt-5-nano': {'input': 0.003, 'output': 0.004},
        }
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        # Session 1084: Mirror timeout config from core/services/llm_provider_registry.py
        # (Session 831). Without this, a hung upstream can wedge the entire
        # Celery worker process and starve background heartbeat threads.
        import httpx
        timeout = httpx.Timeout(60.0, connect=20.0, read=90.0)
        self.client = openai.OpenAI(api_key=self.api_key, timeout=timeout, max_retries=2)
    
    def generate_content(self, model: str, system_prompt: str, user_prompt: str, 
                        config: Dict[str, Any] = None) -> GenerationResult:
        """Generate content using OpenAI"""
        if not self.client:
            return GenerationResult(
                success=False,
                error_message="OpenAI client not initialized"
            )
        
        config = config or {}
        start_time = time.time()
        
        try:
            messages = []
            if system_prompt.strip():
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_prompt})
            
            # Build base parameters
            completion_params = {
                "model": model,
                "messages": messages,
                "stream": False
            }
            
            # Handle GPT-5 models differently - they have different parameters
            try:
                if 'gpt-5-mini' in model.lower():
                    # GPT-4o models use standard parameters
                    completion_params["max_tokens"] = config.get('max_tokens', 4000)
                    completion_params["temperature"] = config.get('temperature', 0.7)
                    # Add other standard parameters if needed
                    if config.get('top_p') is not None:
                        completion_params["top_p"] = config.get('top_p')
                    if config.get('frequency_penalty') is not None:
                        completion_params["frequency_penalty"] = config.get('frequency_penalty')
                    if config.get('presence_penalty') is not None:
                        completion_params["presence_penalty"] = config.get('presence_penalty')
                elif 'gpt-5' in model.lower():
                    # GPT-5 models (for future use when available)
                    # For now, treat them like GPT-4o
                    completion_params["max_tokens"] = config.get('max_tokens', 4000)
                    completion_params["temperature"] = config.get('temperature', 0.7)
                else:
                    # Other models use standard parameters
                    completion_params["max_tokens"] = config.get('max_tokens', 2000)
                    completion_params["temperature"] = config.get('temperature', 0.7)
                    completion_params["top_p"] = config.get('top_p', 1.0)
                    completion_params["frequency_penalty"] = config.get('frequency_penalty', 0.0)
                    completion_params["presence_penalty"] = config.get('presence_penalty', 0.0)
                
                response = self.client.chat.completions.create(**completion_params)
            except Exception as e:
                # If max_completion_tokens fails, try without any token limit
                if 'gpt-5' in model.lower() and 'max_completion_tokens' in str(e):
                    logger.warning(f"Retrying GPT-5 without token limit due to: {e}")
                    completion_params = {
                        "model": model,
                        "messages": messages,
                        "stream": False
                    }
                    response = self.client.chat.completions.create(**completion_params)
                else:
                    raise
            
            generation_time = int((time.time() - start_time) * 1000)
            
            # Debug and handle potential None content
            content = response.choices[0].message.content
            logger.info(f"Raw content from {model}: '{content}' (type: {type(content)})")

            if content is None or content == "":
                logger.warning(f"OpenAI returned None/empty content for model {model}")
                if content is None:
                    logger.debug(f"Content is None")
                else:
                    logger.debug(f"Content is empty string")

                # For GPT-5-mini, empty content often means system prompt interference
                if 'gpt-5-mini' in model.lower():
                    logger.warning(f"GPT-5-mini returned empty content - likely system prompt issue")
                    # Try without system prompt for GPT-5-mini
                    try:
                        logger.info("Retrying GPT-5-mini without system prompt")
                        simple_messages = [{"role": "user", "content": user_prompt}]
                        retry_response = self.client.chat.completions.create(
                            model=model,
                            messages=simple_messages,
                            max_completion_tokens=config.get('max_completion_tokens', config.get('max_tokens', 4000))
                        )
                        content = retry_response.choices[0].message.content or ""
                        if content:
                            logger.info(f"GPT-5-mini retry without system prompt successful")
                        else:
                            logger.error(f"GPT-5-mini still empty after retry")
                            content = ""
                    except Exception as e:
                        logger.error(f"GPT-5-mini retry failed: {e}")
                        content = ""
                else:
                    # Try to get any available text for other models
                    if hasattr(response.choices[0], 'text'):
                        content = response.choices[0].text
                        logger.info(f"Used text field instead: {content[:50] if content else 'empty'}...")
                    elif hasattr(response.choices[0].message, 'text'):
                        content = response.choices[0].message.text
                        logger.info(f"Used message.text field: {content[:50] if content else 'empty'}...")
                    else:
                        content = ""
                        logger.error(f"No content field found in response for {model}")
                        logger.debug(f"Response structure: {response}")
            
            token_usage = {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
            
            cost = self.estimate_cost(
                model, 
                response.usage.prompt_tokens, 
                response.usage.completion_tokens
            )
            
            # Final check for empty content after all retries
            if not content or len(str(content).strip()) == 0:
                logger.warning(f"Empty content after all processing for {model}")

                # For GPT-4o models, provide helpful guidance
                if 'gpt-5-mini' in model.lower():
                    logger.error(f"GPT-4o failed to generate content - retrying with fallback")
                    content = ""  # Don't show error message, let fallback handle it
                else:
                    # Try a simpler retry for other models
                    try:
                        logger.info(f"Attempting simplified retry for {model}")
                        # Use correct parameter for GPT-5
                        if 'gpt-5' in model.lower():
                            retry_response = self.client.chat.completions.create(
                                model=model,
                                messages=messages,
                                max_completion_tokens=300
                            )
                        else:
                            retry_response = self.client.chat.completions.create(
                                model=model,
                                messages=messages,
                                max_completion_tokens=300
                            )
                        content = retry_response.choices[0].message.content or ""
                        if content:
                            logger.info(f"Simplified retry successful for {model}")
                    except Exception as e:
                        logger.error(f"Fallback attempt failed: {e}")
                        content = f"Error: Model {model} failed after retry. Try simpler prompt."
            
            return GenerationResult(
                success=True,
                content=content or "",  # Ensure never None
                token_usage=token_usage,
                cost=cost,
                generation_time_ms=generation_time,
                model_used=model
            )
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {str(e)}")
            return GenerationResult(
                success=False,
                error_message=str(e),
                generation_time_ms=int((time.time() - start_time) * 1000),
                model_used=model
            )
    
    def get_available_models(self) -> List[str]:
        """Get available OpenAI models"""
        return [
            'gpt-5',
            'gpt-5-mini',
            'gpt-5-nano',
            'gpt-5-chat-latest',
            'gpt-5-mini',
            'gpt-5-mini', 
            'gpt-5-mini',
            'gpt-5-mini',
            'gpt-5-nano',
            'gpt-5-nano'
        ]
    
    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for OpenAI generation"""
        if model not in self.pricing:
            # Default to GPT-5-mini pricing if model not found
            model = 'gpt-5-mini'
        
        pricing = self.pricing.get(model, self.pricing['gpt-5-mini'])
        input_cost = (input_tokens / 1000) * pricing['input']
        output_cost = (output_tokens / 1000) * pricing['output']
        
        return input_cost + output_cost


class AnthropicProvider(BaseAIProvider):
    """Anthropic (Claude) provider implementation"""
    
    def __init__(self, api_key: str):
        if not HAS_ANTHROPIC:
            raise ImportError("Anthropic library not installed")
        super().__init__(api_key)
        
        # Model pricing (per 1K tokens)
        self.pricing = {
            'claude-3-5-sonnet-20241022': {'input': 0.003, 'output': 0.015},
            'claude-3-5-sonnet-20240620': {'input': 0.003, 'output': 0.015},
            'claude-3-opus-20240229': {'input': 0.015, 'output': 0.075},
            'claude-3-sonnet-20240229': {'input': 0.003, 'output': 0.015},
            'claude-3-haiku-20240307': {'input': 0.00025, 'output': 0.00125},
        }
    
    def _initialize_client(self):
        """Initialize Anthropic client"""
        # Session 1084: Mirror timeout config from core/services/llm_provider_registry.py
        import httpx
        timeout = httpx.Timeout(60.0, connect=20.0, read=90.0)
        self.client = anthropic.Anthropic(api_key=self.api_key, timeout=timeout, max_retries=2)
    
    def generate_content(self, model: str, system_prompt: str, user_prompt: str, 
                        config: Dict[str, Any] = None) -> GenerationResult:
        """Generate content using Anthropic Claude"""
        if not self.client:
            return GenerationResult(
                success=False,
                error_message="Anthropic client not initialized"
            )
        
        config = config or {}
        start_time = time.time()
        
        try:
            message = self.client.messages.create(
                model=model,
                max_tokens=config.get('max_tokens', 2000),
                temperature=config.get('temperature', 0.7),
                system=system_prompt if system_prompt.strip() else None,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            generation_time = int((time.time() - start_time) * 1000)
            
            content = message.content[0].text
            token_usage = {
                'input_tokens': message.usage.input_tokens,
                'output_tokens': message.usage.output_tokens,
                'total_tokens': message.usage.input_tokens + message.usage.output_tokens
            }
            
            cost = self.estimate_cost(
                model,
                message.usage.input_tokens,
                message.usage.output_tokens
            )
            
            return GenerationResult(
                success=True,
                content=content,
                token_usage=token_usage,
                cost=cost,
                generation_time_ms=generation_time,
                model_used=model
            )
            
        except Exception as e:
            logger.error(f"Anthropic generation failed: {str(e)}")
            return GenerationResult(
                success=False,
                error_message=str(e),
                generation_time_ms=int((time.time() - start_time) * 1000),
                model_used=model
            )
    
    def get_available_models(self) -> List[str]:
        """Get available Anthropic models"""
        return [
            'claude-3-5-sonnet-20241022',
            'claude-3-5-sonnet-20240620',
            'claude-3-opus-20240229',
            'claude-3-sonnet-20240229',
            'claude-3-haiku-20240307'
        ]
    
    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for Anthropic generation"""
        if model not in self.pricing:
            # Default to Sonnet pricing if model not found
            model = 'claude-3-sonnet-20240229'
        
        pricing = self.pricing.get(model, self.pricing['claude-3-sonnet-20240229'])
        input_cost = (input_tokens / 1000) * pricing['input']
        output_cost = (output_tokens / 1000) * pricing['output']
        
        return input_cost + output_cost


class GoogleProvider(BaseAIProvider):
    """Google AI provider implementation"""
    
    def __init__(self, api_key: str):
        if not HAS_GOOGLE:
            raise ImportError("Google GenerativeAI library not installed")
        super().__init__(api_key)
        
        # Google AI pricing (rough estimates)
        self.pricing = {
            'gemini-pro': {'input': 0.00025, 'output': 0.0005},
            'gemini-pro-vision': {'input': 0.00025, 'output': 0.0005},
            'gemini-1.5-pro': {'input': 0.0035, 'output': 0.0105},
            'gemini-1.5-flash': {'input': 0.000075, 'output': 0.0003},
        }
    
    def _initialize_client(self):
        """Initialize Google AI client"""
        genai.configure(api_key=self.api_key)
    
    def generate_content(self, model: str, system_prompt: str, user_prompt: str, 
                        config: Dict[str, Any] = None) -> GenerationResult:
        """Generate content using Google AI"""
        config = config or {}
        start_time = time.time()
        
        try:
            # Combine system and user prompts for Google AI
            full_prompt = ""
            if system_prompt.strip():
                full_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"
            else:
                full_prompt = user_prompt
            
            model_instance = genai.GenerativeModel(model)
            
            generation_config = genai.types.GenerationConfig(
                temperature=config.get('temperature', 0.7),
                max_output_tokens=config.get('max_tokens', 2000),
                top_p=config.get('top_p', 0.8),
                top_k=config.get('top_k', 40),
            )
            
            # Session 1084: Enforce request timeout — google.generativeai
            # sets timeout via request_options per-call (there's no
            # client-level config on this SDK). 90s matches the 90s read
            # timeout used by the other providers.
            response = model_instance.generate_content(
                full_prompt,
                generation_config=generation_config,
                request_options={'timeout': 90},
            )
            
            generation_time = int((time.time() - start_time) * 1000)
            
            content = response.text
            
            # Google AI doesn't provide token usage in the same way
            # Estimate tokens based on content length
            estimated_input_tokens = len(full_prompt.split()) * 1.3
            estimated_output_tokens = len(content.split()) * 1.3
            
            token_usage = {
                'input_tokens': int(estimated_input_tokens),
                'output_tokens': int(estimated_output_tokens),
                'total_tokens': int(estimated_input_tokens + estimated_output_tokens)
            }
            
            cost = self.estimate_cost(
                model,
                token_usage['input_tokens'],
                token_usage['output_tokens']
            )
            
            return GenerationResult(
                success=True,
                content=content,
                token_usage=token_usage,
                cost=cost,
                generation_time_ms=generation_time,
                model_used=model
            )
            
        except Exception as e:
            logger.error(f"Google AI generation failed: {str(e)}")
            return GenerationResult(
                success=False,
                error_message=str(e),
                generation_time_ms=int((time.time() - start_time) * 1000),
                model_used=model
            )
    
    def get_available_models(self) -> List[str]:
        """Get available Google AI models"""
        return [
            'gemini-1.5-pro',
            'gemini-1.5-flash',
            'gemini-pro',
            'gemini-pro-vision'
        ]
    
    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for Google AI generation"""
        if model not in self.pricing:
            # Default to Gemini Pro pricing if model not found
            model = 'gemini-pro'
        
        pricing = self.pricing.get(model, self.pricing['gemini-pro'])
        input_cost = (input_tokens / 1000) * pricing['input']
        output_cost = (output_tokens / 1000) * pricing['output']
        
        return input_cost + output_cost


class AIProviderManager:
    """Manages multiple AI providers"""
    
    def __init__(self):
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available AI providers"""
        # OpenAI
        if HAS_OPENAI and settings.AI_PROVIDERS.get('OPENAI_API_KEY'):
            try:
                self.providers['openai'] = OpenAIProvider(
                    settings.AI_PROVIDERS['OPENAI_API_KEY']
                )
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI provider: {str(e)}")
        
        # Anthropic
        if HAS_ANTHROPIC and settings.AI_PROVIDERS.get('ANTHROPIC_API_KEY'):
            try:
                self.providers['anthropic'] = AnthropicProvider(
                    settings.AI_PROVIDERS['ANTHROPIC_API_KEY']
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic provider: {str(e)}")
        
        # Google AI
        if HAS_GOOGLE and settings.AI_PROVIDERS.get('GOOGLE_API_KEY'):
            try:
                self.providers['google'] = GoogleProvider(
                    settings.AI_PROVIDERS['GOOGLE_API_KEY']
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Google AI provider: {str(e)}")
    
    def get_provider(self, provider_name: str) -> Optional[BaseAIProvider]:
        """Get AI provider by name"""
        return self.providers.get(provider_name.lower())
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return list(self.providers.keys())
    
    def generate_content(self, provider: str, model: str, system_prompt: str, 
                        user_prompt: str, config: Dict[str, Any] = None) -> GenerationResult:
        """Generate content using specified provider"""
        provider_instance = self.get_provider(provider)
        
        if not provider_instance:
            return GenerationResult(
                success=False,
                error_message=f"Provider '{provider}' not available",
                model_used=model
            )
        
        return provider_instance.generate_content(model, system_prompt, user_prompt, config)
    
    def get_available_models(self, provider: str = None) -> Dict[str, List[str]]:
        """Get available models for providers"""
        if provider:
            provider_instance = self.get_provider(provider)
            if provider_instance:
                return {provider: provider_instance.get_available_models()}
            else:
                return {}
        else:
            return {
                name: instance.get_available_models()
                for name, instance in self.providers.items()
            }
    
    def estimate_cost(self, provider: str, model: str, input_tokens: int, 
                     output_tokens: int) -> float:
        """Estimate generation cost"""
        provider_instance = self.get_provider(provider)
        if provider_instance:
            return provider_instance.estimate_cost(model, input_tokens, output_tokens)
        return 0.0

    def generate_embeddings(self, texts: List[str], model: str = "text-embedding-3-small") -> Dict[str, Any]:
        """Generate embeddings for texts using OpenAI"""
        # Use OpenAI provider for embeddings
        provider_instance = self.get_provider('openai')

        if not provider_instance:
            # Try to initialize OpenAI if not already done
            if HAS_OPENAI and settings.AI_PROVIDERS.get('OPENAI_API_KEY'):
                try:
                    provider_instance = OpenAIProvider(settings.AI_PROVIDERS['OPENAI_API_KEY'])
                    self.providers['openai'] = provider_instance
                except Exception as e:
                    logger.error(f"Failed to initialize OpenAI for embeddings: {e}")
                    return {'error': str(e)}
            else:
                return {'error': 'OpenAI provider not available for embeddings'}

        # Generate embeddings
        try:
            if not hasattr(provider_instance, 'client'):
                provider_instance._initialize_client()

            response = provider_instance.client.embeddings.create(
                model=model,
                input=texts
            )

            embeddings = [item.embedding for item in response.data]

            return {
                'embeddings': embeddings,
                'model': model,
                'usage': response.usage.total_tokens if hasattr(response, 'usage') else 0
            }

        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return {'error': str(e)}


# Convenience function for backward compatibility
def get_ai_provider():
    """Get the default AI provider instance."""
    manager = AIProviderManager()
    # Try to get OpenAI first, then any available provider
    for provider_name in ['openai', 'anthropic', 'google']:
        provider = manager.get_provider(provider_name)
        if provider:
            return provider
    return None