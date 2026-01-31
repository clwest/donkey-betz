"""
Agent LLM Integration Module
Connects AI agents to actual LLM providers for real intelligence
"""
import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import openai
import anthropic
from abc import ABC, abstractmethod
from ai_core.llm_adapter_async import AsyncLLMAdapter

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Base class for LLM providers"""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass

    @abstractmethod
    def get_cost(self, tokens_in: int, tokens_out: int) -> float:
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider - Using Responses API for GPT-5 reasoning models"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("OpenAI API key not found")

    async def generate(self, prompt: str, model: str = "gpt-5-mini",
                      reasoning_effort: str = "low",
                      verbosity: str = "medium",
                      max_output_tokens: int = 1000,
                      previous_response_id: Optional[str] = None,
                      **kwargs) -> Dict[str, Any]:
        """Generate response using OpenAI Responses API

        Args:
            prompt: Input text for the model
            model: Model to use (gpt-5, gpt-5-mini, gpt-5-nano)
            reasoning_effort: Reasoning level (minimal, low, medium, high)
            verbosity: Output verbosity (low, medium, high)
            max_output_tokens: Maximum output tokens (not including reasoning)
            previous_response_id: ID from previous response for chain of thought

        Returns:
            Dict containing content, response_id, and usage stats
        """
        if not self.client:
            return {
                'content': "OpenAI API key not configured",
                'response_id': None,
                'usage': None,
                'error': True
            }

        try:
            # Use Responses API for GPT-5 models
            # Note: GPT-5 uses max_completion_tokens, not max_tokens
            # GPT-5 reasoning models don't support temperature parameter
            model = getattr(self, 'model_name', None) or getattr(self, 'model', None) or 'qwen2.5:14b-instruct'
            is_gpt5 = 'gpt-5' in model.lower() if model else False

            kwargs = {
                'model': model,
                'tools': getattr(self, 'tools_schema', None),
            }

            # GPT-5 uses max_completion_tokens and doesn't support temperature
            # GPT-5 reasoning models need higher token limits for thinking
            if is_gpt5:
                kwargs['max_completion_tokens'] = getattr(self, 'max_tokens', 6000)  # Higher for reasoning
            else:
                kwargs['max_tokens'] = getattr(self, 'max_tokens', 800)
                kwargs['temperature'] = getattr(self, 'temperature', 0.2)

            response = await AsyncLLMAdapter().chat(messages, **kwargs)
            return {
                'content': response.output_text,
                'response_id': response.id,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens,
                    'reasoning_tokens': getattr(response.usage, 'reasoning_tokens', 0)
                },
                'error': False
            }
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            return {
                'content': f"Error generating response: {e}",
                'response_id': None,
                'usage': None,
                'error': True
            }

    def get_cost(self, tokens_in: int, tokens_out: int, reasoning_tokens: int = 0, model: str = "gpt-5-mini") -> float:
        """Calculate cost for OpenAI usage including reasoning tokens

        GPT-5 Pricing (per 1M tokens):
        - gpt-5: $1.25 input / $10.00 output
        - gpt-5-mini: $0.25 input / $2.00 output
        - gpt-5-nano: $0.05 input / $0.40 output
        """
        pricing = {
            'gpt-5': {'input': 1.25, 'output': 10.00},
            'gpt-5-mini': {'input': 0.25, 'output': 2.00},
            'gpt-5-nano': {'input': 0.05, 'output': 0.40}
        }

        model_pricing = pricing.get(model, pricing['gpt-5-mini'])

        # Input tokens + reasoning tokens are both billed as input
        total_input_tokens = tokens_in + reasoning_tokens
        input_cost = (total_input_tokens / 1_000_000) * model_pricing['input']
        output_cost = (tokens_out / 1_000_000) * model_pricing['output']

        return input_cost + output_cost


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if self.api_key:
            self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("Anthropic API key not found")

    async def generate(self, prompt: str, model: str = "claude-3-haiku-20240307",
                      temperature: float = 0.7, max_tokens: int = 1000,
                      **kwargs) -> str:
        """Generate response using Anthropic Claude"""
        if not self.client:
            return "Anthropic API key not configured"

        try:
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic generation error: {e}")
            return f"Error generating response: {e}"

    def get_cost(self, tokens_in: int, tokens_out: int) -> float:
        """Calculate cost for Anthropic usage"""
        # Claude Haiku pricing (per 1M tokens)
        input_cost = (tokens_in / 1_000_000) * 0.25
        output_cost = (tokens_out / 1_000_000) * 1.25
        return input_cost + output_cost


class MockLLMProvider(LLMProvider):
    """Mock LLM for testing without API costs"""

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate mock response"""
        await asyncio.sleep(0.1)  # Simulate API delay

        # Generate contextual mock responses
        if "sports" in prompt.lower() or "betting" in prompt.lower():
            return "Based on analysis: Chiefs have 65% win probability. Recommended bet: Under 48.5 total points with confidence 72%."
        elif "job" in prompt.lower() or "opportunity" in prompt.lower():
            return "Identified 3 high-value opportunities matching your skills. Senior Developer role at TechCorp offers $150k with remote flexibility."
        elif "content" in prompt.lower() or "viral" in prompt.lower():
            return "Trending topic analysis: AI productivity tools gaining 340% engagement. Suggested content angle: '5 AI Tools That Save 10 Hours Weekly'."
        elif "trading" in prompt.lower() or "crypto" in prompt.lower():
            return "Market signal detected: BTC showing bullish divergence on 4H chart. Entry point: $42,350 with stop loss at $41,800."
        else:
            return f"Processed request: {prompt[:100]}... Generated intelligent response based on context."

    def get_cost(self, tokens_in: int, tokens_out: int) -> float:
        """No cost for mock provider"""
        return 0.0


class AgentLLMIntegration:
    """Main integration class connecting agents to LLMs"""

    def __init__(self):
        self.providers = {
            'openai': OpenAIProvider(),
            'anthropic': AnthropicProvider(),
            'mock': MockLLMProvider()
        }

        # Default to mock if no API keys are configured
        self.default_provider = 'mock'
        if os.getenv('OPENAI_API_KEY'):
            self.default_provider = 'openai'
        elif os.getenv('ANTHROPIC_API_KEY'):
            self.default_provider = 'anthropic'

        self.usage_stats = {
            'total_requests': 0,
            'total_tokens_in': 0,
            'total_tokens_out': 0,
            'total_cost': 0.0,
            'by_agent': {}
        }

        logger.info(f"LLM Integration initialized with default provider: {self.default_provider}")

    async def generate_for_agent(self, agent_name: str, prompt: str,
                                provider: Optional[str] = None,
                                learned_context: Optional[Dict[str, Any]] = None,
                                reasoning_effort: str = "low",
                                verbosity: str = "medium",
                                max_output_tokens: int = 1000,
                                previous_response_id: Optional[str] = None,
                                model: str = "gpt-5-mini",
                                **kwargs) -> Dict[str, Any]:
        """Generate LLM response for a specific agent with proper GPT-5 reasoning configuration

        Args:
            agent_name: Name of the agent requesting generation
            prompt: Input prompt for the model
            provider: LLM provider to use (openai, anthropic, mock)
            learned_context: Previous learning data to include in context
            reasoning_effort: Reasoning level for GPT-5 (minimal, low, medium, high)
            verbosity: Output verbosity (low, medium, high)
            max_output_tokens: Maximum output tokens
            previous_response_id: Previous response ID for chain of thought
            model: Model to use (gpt-5, gpt-5-mini, gpt-5-nano)
        """
        provider_name = provider or self.default_provider
        llm_provider = self.providers.get(provider_name)

        if not llm_provider:
            return {
                'success': False,
                'error': f'Provider {provider_name} not found',
                'response': None
            }

        try:
            # Build enhanced prompt with learned context
            enhanced_prompt = f"[Agent: {agent_name}]\n"

            # Add learned knowledge if available
            if learned_context and learned_context.get('total_learning_entries', 0) > 0:
                enhanced_prompt += "\n🧠 LEARNED KNOWLEDGE (from past experiences):\n"

                if learned_context.get('domains'):
                    enhanced_prompt += f"\nDomains you've learned about: {', '.join(learned_context['domains'])}\n"

                if learned_context.get('sources'):
                    sources_str = ', '.join(learned_context['sources'])
                    enhanced_prompt += f"\nReliable data sources: {sources_str}\n"

                if learned_context.get('key_patterns'):
                    enhanced_prompt += f"\nKey patterns identified ({len(learned_context['key_patterns'])} insights):\n"
                    for pattern in learned_context['key_patterns'][:3]:  # Top 3 patterns
                        enhanced_prompt += f"  - {pattern['source']}: {pattern.get('potential', 'N/A')} (confidence: {pattern['confidence']:.0%})\n"

                if learned_context.get('data_quality_insights'):
                    enhanced_prompt += "\nData quality insights:\n"
                    for insight in learned_context['data_quality_insights'][:3]:  # Top 3 insights
                        enhanced_prompt += f"  - {insight['source']}: {insight.get('reliability', 'N/A')} reliability\n"

                enhanced_prompt += "\n💡 Use this learned knowledge to improve your response quality and accuracy.\n\n"

            enhanced_prompt += prompt

            # Generate response with proper GPT-5 configuration
            if provider_name == 'openai':
                result = await llm_provider.generate(
                    enhanced_prompt,
                    model=model,
                    reasoning_effort=reasoning_effort,
                    verbosity=verbosity,
                    max_output_tokens=max_output_tokens,
                    previous_response_id=previous_response_id,
                    **kwargs
                )

                if result.get('error'):
                    return {
                        'success': False,
                        'error': result.get('content'),
                        'response': None
                    }

                # Track usage with reasoning tokens
                usage = result.get('usage', {})
                self._track_usage(
                    agent_name,
                    provider_name,
                    usage.get('input_tokens', len(enhanced_prompt)),
                    usage.get('output_tokens', len(result['content'])),
                    usage.get('reasoning_tokens', 0),
                    model
                )

                return {
                    'success': True,
                    'response': result['content'],
                    'response_id': result.get('response_id'),  # For chain of thought
                    'usage': usage,
                    'provider': provider_name,
                    'agent': agent_name,
                    'model': model,
                    'timestamp': datetime.now().isoformat()
                }

            else:
                # For non-OpenAI providers (Anthropic, Mock)
                response = await llm_provider.generate(enhanced_prompt, **kwargs)

                # Track usage (estimated for non-OpenAI)
                self._track_usage(agent_name, provider_name, len(enhanced_prompt), len(response))

                return {
                    'success': True,
                    'response': response,
                    'provider': provider_name,
                    'agent': agent_name,
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"LLM generation failed for {agent_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': None
            }

    async def process_spider_data_with_llm(self, agent_name: str,
                                          spider_data: Dict[str, Any],
                                          analysis_type: str = "general") -> Dict[str, Any]:
        """Process spider data through LLM for intelligent analysis"""

        prompt_templates = {
            'betting': "Analyze this sports betting data and provide recommendations:\n{data}",
            'trading': "Analyze this market data and identify trading opportunities:\n{data}",
            'content': "Analyze these trending topics and suggest content strategies:\n{data}",
            'jobs': "Review these job opportunities and rank by fit:\n{data}",
            'general': "Analyze this data and provide actionable insights:\n{data}"
        }

        template = prompt_templates.get(analysis_type, prompt_templates['general'])
        prompt = template.format(data=json.dumps(spider_data, indent=2)[:2000])

        result = await self.generate_for_agent(agent_name, prompt)

        if result['success']:
            return {
                'success': True,
                'analysis': result['response'],
                'original_data': spider_data,
                'analysis_type': analysis_type,
                'timestamp': datetime.now().isoformat()
            }
        else:
            return result

    def _track_usage(self, agent_name: str, provider: str,
                    tokens_in: int, tokens_out: int,
                    reasoning_tokens: int = 0, model: str = "gpt-5-mini"):
        """Track LLM usage statistics including reasoning tokens"""
        self.usage_stats['total_requests'] += 1
        self.usage_stats['total_tokens_in'] += tokens_in
        self.usage_stats['total_tokens_out'] += tokens_out

        # Calculate cost including reasoning tokens
        if provider in self.providers:
            if provider == 'openai':
                cost = self.providers[provider].get_cost(tokens_in, tokens_out, reasoning_tokens, model)
            else:
                cost = self.providers[provider].get_cost(tokens_in, tokens_out)
            self.usage_stats['total_cost'] += cost
        else:
            cost = 0

        # Track per-agent usage
        if agent_name not in self.usage_stats['by_agent']:
            self.usage_stats['by_agent'][agent_name] = {
                'requests': 0,
                'tokens_in': 0,
                'tokens_out': 0,
                'reasoning_tokens': 0,
                'cost': 0.0
            }

        agent_stats = self.usage_stats['by_agent'][agent_name]
        agent_stats['requests'] += 1
        agent_stats['tokens_in'] += tokens_in
        agent_stats['tokens_out'] += tokens_out
        agent_stats['reasoning_tokens'] = agent_stats.get('reasoning_tokens', 0) + reasoning_tokens
        agent_stats['cost'] += cost

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        return self.usage_stats

    async def enable_agent_with_llm(self, agent_name: str,
                                   agent_instance: Any) -> bool:
        """Enable an agent with LLM capabilities"""
        try:
            # Add LLM methods to agent instance with learned context support
            agent_instance.generate_llm_response = lambda prompt: self.generate_for_agent(
                agent_name,
                prompt,
                learned_context=getattr(agent_instance, 'learned_context', None)
            )
            agent_instance.process_with_llm = lambda data, analysis_type: self.process_spider_data_with_llm(
                agent_name, data, analysis_type
            )

            logger.info(f"Enabled LLM for agent: {agent_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to enable LLM for {agent_name}: {e}")
            return False


# Singleton instance
agent_llm_integration = AgentLLMIntegration()


# Helper functions for easy integration
async def enable_agent_intelligence(agent_name: str, agent_instance: Any):
    """Enable AI intelligence for an agent"""
    return await agent_llm_integration.enable_agent_with_llm(agent_name, agent_instance)


async def analyze_with_ai(agent_name: str, data: Dict[str, Any],
                         analysis_type: str = "general") -> Dict[str, Any]:
    """Analyze data using AI"""
    return await agent_llm_integration.process_spider_data_with_llm(
        agent_name, data, analysis_type
    )


def get_llm_usage_stats() -> Dict[str, Any]:
    """Get current LLM usage statistics"""
    return agent_llm_integration.get_usage_stats()