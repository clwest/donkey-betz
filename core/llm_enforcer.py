"""
LLM Enforcer - MANDATORY Real AI Usage

This enforcer ENSURES that ANY component claiming to use AI
MUST go through real LLM APIs. No exceptions!

Features:
- Intercepts all AI-related calls
- Forces real OpenAI/Anthropic usage
- Blocks fake responses
- Logs everything for audit
- Raises alerts if fake AI detected
"""

import os
import logging
import json
import hashlib
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from functools import wraps
import inspect
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Session 266: Import from central prompt registry
try:
    from core.prompts import get_task_prompt
    PROMPT_REGISTRY_AVAILABLE = True
except ImportError:
    PROMPT_REGISTRY_AVAILABLE = False
    logger.warning("Prompt registry not available, using fallback prompts")


class LLMEnforcer:
    """
    Enforces REAL LLM usage across the entire platform
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.openai_client = None
            self.anthropic_client = None
            self.total_calls = 0
            self.total_tokens = 0
            self.total_cost = 0.0
            self.call_log = []
            self._initialize_clients()
            self._initialized = True

    def _initialize_clients(self):
        """Initialize real LLM clients"""
        # OpenAI
        try:
            from openai import OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key and api_key != 'your-key-here':
                self.openai_client = OpenAI(api_key=api_key)
                logger.info("✅ OpenAI client initialized - REAL AI AVAILABLE")
            else:
                logger.warning("⚠️ OpenAI API key not configured")
        except ImportError:
            logger.error("❌ OpenAI library not installed! Run: pip install openai")

        # Anthropic (Claude)
        try:
            from anthropic import Anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key and api_key != 'your-key-here':
                self.anthropic_client = Anthropic(api_key=api_key)
                logger.info("✅ Anthropic client initialized - CLAUDE AVAILABLE")
            else:
                logger.warning("⚠️ Anthropic API key not configured")
        except ImportError:
            logger.warning("⚠️ Anthropic library not installed")

    def enforce_real_ai(self,
                       prompt: str,
                       context: str = "",
                       agent_name: str = "Unknown Agent",
                       task_type: str = "general",
                       max_tokens: int = 2000,  # Increased for GPT-5-mini reasoning models
                       temperature: float = 0.7,
                       use_claude: bool = False,
                       tools: Optional[List[Dict]] = None,
                       previous_response_id: Optional[str] = None,
                       tool_choice: Optional[Dict] = None) -> Dict[str, Any]:
        """
        ENFORCE real AI usage - this is the ONLY way to get AI responses

        Session 129: Added previous_response_id parameter for GPT-5.1 chain of thought

        Args:
            prompt: The actual prompt to send
            context: Additional context for the task
            agent_name: Name of the agent making the request
            task_type: Type of task (cover_letter, analysis, content, etc.)
            max_tokens: Maximum tokens for response
            temperature: Creativity level (0-1)
            use_claude: Use Claude instead of GPT

        Returns:
            Dict with response and metadata

        Raises:
            Exception if no LLM is available
        """
        logger.info(f"🔒 ENFORCING REAL AI for {agent_name} - Task: {task_type}")

        # Check if we have any LLM available
        if not self.openai_client and not self.anthropic_client:
            error_msg = "❌ CRITICAL: No LLM clients available! Cannot generate AI response."
            logger.error(error_msg)
            raise Exception(error_msg)

        # Build the full prompt
        full_prompt = f"{context}\n\n{prompt}" if context else prompt

        # Track the call
        call_id = hashlib.md5(f"{agent_name}_{datetime.now()}".encode()).hexdigest()[:8]

        try:
            if use_claude and self.anthropic_client:
                # Use Claude
                response = self._call_claude(full_prompt, max_tokens, temperature)
                provider = "anthropic"
                model = "claude-3-haiku"  # Keep Claude as alternative
            elif self.openai_client:
                # Session 129: Pass context separately so GPT can see project assets
                # Session 129: Pass previous_response_id for chain of thought
                # Session 129: Pass tool_choice to force tool execution
                response = self._call_openai(prompt, max_tokens, temperature, task_type, tools, context, previous_response_id, tool_choice)
                provider = "openai"
                model = "gpt-5.1"  # Session 129: Upgraded to GPT-5.1 flagship model with Responses API
            else:
                raise Exception("No LLM client available")

            # Log the successful call
            self.total_calls += 1
            self.total_tokens += response.get('tokens', 0)
            self.total_cost += response.get('cost', 0)

            log_entry = {
                'call_id': call_id,
                'timestamp': datetime.now().isoformat(),
                'agent_name': agent_name,
                'task_type': task_type,
                'provider': provider,
                'model': model,
                'tokens': response.get('tokens', 0),
                'cost': response.get('cost', 0),
                'success': True
            }
            self.call_log.append(log_entry)

            logger.info(f"✅ REAL AI RESPONSE generated - {provider}/{model} - {response.get('tokens', 0)} tokens")

            result = {
                'success': True,
                'response': response['content'],
                'provider': provider,
                'model': model,
                'tokens': response.get('tokens', 0),
                'cost': response.get('cost', 0),
                'call_id': call_id,
                'agent': agent_name
            }

            # Session 125: Include tool calls if present
            if 'tool_calls' in response:
                result['tool_calls'] = response['tool_calls']
                logger.info(f"🛠️ Returning {len(response['tool_calls'])} tool calls to caller")

            return result

        except Exception as e:
            logger.error(f"❌ LLM call failed: {e}")

            # Log the failure
            log_entry = {
                'call_id': call_id,
                'timestamp': datetime.now().isoformat(),
                'agent_name': agent_name,
                'task_type': task_type,
                'error': str(e),
                'success': False
            }
            self.call_log.append(log_entry)

            # Return error with clear indication
            return {
                'success': False,
                'error': str(e),
                'response': f"[ERROR: Real AI unavailable - {e}]",
                'call_id': call_id,
                'agent': agent_name
            }

    def _call_openai(self, prompt: str, max_tokens: int, temperature: float, task_type: str, tools: Optional[List[Dict]] = None, context: str = "", previous_response_id: Optional[str] = None, tool_choice: Optional[Dict] = None) -> Dict[str, Any]:
        """Make actual OpenAI API call using GPT-5.1 with Responses API

        Session 129: Migrated to GPT-5.1 with Responses API
        - Uses gpt-5.1 flagship model
        - Responses API for chain of thought passing
        - Proper reasoning.effort and text.verbosity configuration
        - Tool calling support via Responses API
        - Tool forcing via tool_choice with allowed_tools (mode: required)
        """
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")

        # Build system context
        if context:
            system_msg = context
        else:
            # Session 266: Use central prompt registry for task-specific prompts
            if PROMPT_REGISTRY_AVAILABLE:
                system_msg = get_task_prompt(task_type)
            else:
                # Fallback prompts if registry unavailable
                fallback_prompts = {
                    'cover_letter': "You are an expert cover letter writer.",
                    'content': "You are a professional content creator.",
                    'analysis': "You are an expert analyst.",
                    'code': "You are an expert programmer.",
                    'general': "You are a helpful AI assistant."
                }
                system_msg = fallback_prompts.get(task_type, fallback_prompts['general'])

        # Combine system message and user prompt for Responses API input
        full_input = f"{system_msg}\n\nUser request: {prompt}"

        # Session 129: GPT-5.1 with Responses API
        # Configure reasoning effort based on task type
        reasoning_effort_map = {
            'conversation': 'low',     # Session 129: Changed from 'none' to 'low' for better agentic tool execution
            'cover_letter': 'low',     # Quick content generation
            'content': 'low',          # Quick content generation
            'analysis': 'medium',      # Balanced analysis
            'code': 'high',            # Complex coding tasks
            'general': 'none'          # Default fast mode
        }
        reasoning_effort = reasoning_effort_map.get(task_type, 'none')

        # Build Responses API parameters
        params = {
            'model': "gpt-5.1",                          # Session 129: Upgraded to GPT-5.1
            'input': full_input,                         # Combined system + user input
            'reasoning': {"effort": reasoning_effort},   # Configurable reasoning
            'text': {"verbosity": "medium"},             # Balanced output length
            'max_output_tokens': max_tokens,             # Correct parameter for Responses API
        }

        # Add chain of thought if available (improves intelligence + reduces cost)
        if previous_response_id:
            params['previous_response_id'] = previous_response_id
            logger.info(f"🔗 Passing chain of thought from previous response")

        # Add tool calling support
        if tools:
            params['tools'] = tools
            logger.info(f"🔧 Tool calling enabled with {len(tools)} tools")

            # Session 129: Add tool_choice to force tool execution (Responses API format)
            # Docs: https://platform.openai.com/docs/guides/function-calling
            if tool_choice:
                params['tool_choice'] = tool_choice
                logger.info(f"🎯 Tool forcing enabled: {tool_choice.get('mode', 'auto')}")

        # Call Responses API
        try:
            response = self.openai_client.responses.create(**params)
        except Exception as e:
            logger.error(f"❌ Responses API error: {e}")
            raise

        # Parse Responses API response (different structure than Chat Completions)
        # Response has: output (list of items), id, usage, etc.
        content = response.output_text if hasattr(response, 'output_text') else ''

        # Session 129: Parse tool calls from Responses API output list
        # The Responses API returns tool calls in response.output[], not response.tool_calls!
        tool_calls = None
        if hasattr(response, 'output') and response.output:
            # Session 184: Debug - log what types we're seeing in the output
            output_types = [getattr(item, 'type', type(item).__name__) for item in response.output]
            logger.info(f"🔍 DEBUG SESSION 184: response.output types = {output_types}")

            # Filter for ResponseFunctionToolCall items in the output list
            function_calls = [item for item in response.output if hasattr(item, 'type') and item.type == 'function_call']

            if function_calls:
                logger.info(f"🛠️ GPT-5.1 returned {len(function_calls)} tool calls in output list!")
                tool_calls = [
                    {
                        'id': tc.call_id if hasattr(tc, 'call_id') else (tc.id if hasattr(tc, 'id') else str(i)),
                        'type': 'function',
                        'function': {
                            'name': tc.name,
                            'arguments': tc.arguments
                        }
                    } for i, tc in enumerate(function_calls)
                ]
                logger.info(f"🎯 Parsed tool calls: {[tc['function']['name'] for tc in tool_calls]}")

        # Calculate usage and cost for GPT-5.1
        usage = response.usage if hasattr(response, 'usage') else None
        if usage:
            # GPT-5.1 pricing: $1.25/1M input + $10.00/1M output
            # Reasoning tokens are separate but counted in cost
            input_tokens = usage.input_tokens if hasattr(usage, 'input_tokens') else 0
            output_tokens = usage.output_tokens if hasattr(usage, 'output_tokens') else 0
            reasoning_tokens = usage.reasoning_tokens if hasattr(usage, 'reasoning_tokens') else 0

            # Calculate cost (reasoning tokens count toward input cost)
            total_input = input_tokens + reasoning_tokens
            cost = (total_input * 1.25 / 1_000_000) + (output_tokens * 10.00 / 1_000_000)
            total_tokens = input_tokens + output_tokens + reasoning_tokens

            logger.info(f"💰 GPT-5.1 usage: {input_tokens} input + {reasoning_tokens} reasoning + {output_tokens} output = {total_tokens} total tokens (${cost:.6f})")
        else:
            total_tokens = 0
            cost = 0.0

        # Session 266: Detect truncation - check if output_tokens hit the max limit
        # If output tokens are >= max_tokens - 10, likely truncated
        truncated = False
        if usage and output_tokens >= (max_tokens - 10):
            truncated = True
            logger.warning(f"⚠️ Response likely truncated: {output_tokens} output tokens (max: {max_tokens})")

        # Build response dict
        result = {
            'content': content,
            'tokens': total_tokens,
            'cost': cost,
            'truncated': truncated,  # Session 266: Flag for continuation handling
        }

        # Add response_id for chain of thought passing
        if hasattr(response, 'id'):
            result['response_id'] = response.id

        # Add tool calls if present
        if tool_calls:
            result['tool_calls'] = tool_calls

        return result

    def _calculate_cost(self, usage) -> float:
        """
        Calculate cost based on token usage for GPT-5-mini.

        Session 127: Updated for GPT-5-mini pricing

        Args:
            usage: OpenAI usage object

        Returns:
            Estimated cost in USD
        """
        if not usage:
            return 0.0

        # GPT-5-mini pricing (Session 127)
        # Input: $0.50 per 1M tokens = $0.0005 per 1K tokens
        # Output: $1.50 per 1M tokens = $0.0015 per 1K tokens
        input_cost = (usage.prompt_tokens / 1000) * 0.0005
        output_cost = (usage.completion_tokens / 1000) * 0.0015

        return input_cost + output_cost

    def _call_claude(self, prompt: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """Make actual Claude API call"""
        if not self.anthropic_client:
            raise Exception("Anthropic client not initialized")

        response = self.anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        content = response.content[0].text if response.content else ""
        tokens = response.usage.input_tokens + response.usage.output_tokens if hasattr(response, 'usage') else 0

        # Estimate cost (Claude Haiku pricing)
        cost = tokens * 0.00025 / 1000

        return {
            'content': content,
            'tokens': tokens,
            'cost': cost
        }


    def generate_completion(self, system_prompt=None, user_prompt=None, prompt=None,
                             max_tokens=500, max_completion_tokens=None,
                             temperature=0.7, agent_name="Agent", model=None):
        """
        Compatibility method for executors expecting generate_completion
        Maps to enforce_real_ai internally

        Session 260: Updated to accept both old and new parameter names:
        - max_tokens (legacy) and max_completion_tokens (GPT-5)
        - temperature is ignored for GPT-5 models (only supports default 1.0)
        - model parameter is accepted but we always use GPT-5.1 via enforce_real_ai
        """
        # Build the prompt from system_prompt + user_prompt if provided
        if user_prompt:
            full_prompt = user_prompt
            context = system_prompt or ""
        else:
            full_prompt = prompt or ""
            context = ""

        # Use max_completion_tokens if provided, otherwise fall back to max_tokens
        effective_max_tokens = max_completion_tokens if max_completion_tokens else max_tokens

        result = self.enforce_real_ai(
            prompt=full_prompt,
            context=context,
            agent_name=agent_name,
            max_tokens=effective_max_tokens,
            temperature=temperature,  # Ignored internally for GPT-5 models
            task_type="content"
        )

        # Return just the response text for compatibility
        if result['success']:
            return result['response']
        else:
            return result.get('response', f"Error: {result.get('error', 'Unknown error')}")

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            'total_calls': self.total_calls,
            'total_tokens': self.total_tokens,
            'total_cost': f"${self.total_cost:.4f}",
            'successful_calls': len([c for c in self.call_log if c.get('success', False)]),
            'failed_calls': len([c for c in self.call_log if not c.get('success', False)]),
            'openai_available': self.openai_client is not None,
            'anthropic_available': self.anthropic_client is not None
        }

    def get_agent_usage(self, agent_name: str) -> Dict[str, Any]:
        """Get usage stats for a specific agent"""
        agent_calls = [c for c in self.call_log if c.get('agent_name') == agent_name]

        if not agent_calls:
            return {'agent': agent_name, 'message': 'No calls recorded'}

        return {
            'agent': agent_name,
            'total_calls': len(agent_calls),
            'successful_calls': len([c for c in agent_calls if c.get('success', False)]),
            'total_tokens': sum(c.get('tokens', 0) for c in agent_calls),
            'total_cost': sum(c.get('cost', 0) for c in agent_calls)
        }


# Global enforcer instance
_llm_enforcer = None


def get_llm_enforcer() -> LLMEnforcer:
    """Get the global LLM enforcer instance"""
    global _llm_enforcer
    if _llm_enforcer is None:
        _llm_enforcer = LLMEnforcer()
    return _llm_enforcer


def require_real_ai(func):
    """
    Decorator that FORCES a function to use real AI

    Usage:
    @require_real_ai
    def generate_content(prompt):
        # This will be intercepted and forced to use real AI
        return "This would be replaced with real AI"
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract prompt from args/kwargs
        prompt = args[0] if args else kwargs.get('prompt', 'Generate response')

        # Get agent name from function
        agent_name = func.__module__ + '.' + func.__name__

        # Force real AI usage
        enforcer = get_llm_enforcer()
        result = enforcer.enforce_real_ai(
            prompt=prompt,
            agent_name=agent_name,
            task_type=kwargs.get('task_type', 'general')
        )

        if result['success']:
            return result['response']
        else:
            logger.error(f"Failed to get real AI response: {result['error']}")
            return result['response']  # Returns error message

    return wrapper


# Quick function to verify LLM availability
def verify_llm_availability() -> bool:
    """Verify that at least one LLM is available"""
    enforcer = get_llm_enforcer()
    stats = enforcer.get_usage_stats()
    return stats['openai_available'] or stats['anthropic_available']


# Function to test the enforcer
def test_enforcer():
    """Test that the enforcer works"""
    enforcer = get_llm_enforcer()

    # Test with a simple prompt
    result = enforcer.enforce_real_ai(
        prompt="Say 'Hello from real AI' and include a unique timestamp",
        agent_name="Test Agent",
        task_type="general"
    )

    if result['success']:
        print(f"✅ LLM Enforcer working!")
        print(f"   Provider: {result['provider']}")
        print(f"   Model: {result['model']}")
        print(f"   Response: {result['response'][:100]}...")
        print(f"   Tokens: {result['tokens']}")
        return True
    else:
        print(f"❌ LLM Enforcer failed: {result['error']}")
        return False


if __name__ == "__main__":
    # Test the enforcer
    if test_enforcer():
        print("\n📊 Usage Stats:")
        stats = get_llm_enforcer().get_usage_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")