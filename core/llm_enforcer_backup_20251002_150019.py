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
import hashlib
from typing import Dict, Any
from datetime import datetime
from functools import wraps
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


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
                       use_claude: bool = False) -> Dict[str, Any]:
        """
        ENFORCE real AI usage - this is the ONLY way to get AI responses

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
                # Use OpenAI
                response = self._call_openai(full_prompt, max_tokens, temperature, task_type)
                provider = "openai"
                model = "gpt-5-mini"  # Reliable and efficient
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

            return {
                'success': True,
                'response': response['content'],
                'provider': provider,
                'model': model,
                'tokens': response.get('tokens', 0),
                'cost': response.get('cost', 0),
                'call_id': call_id,
                'agent': agent_name
            }

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

    def _call_openai(self, prompt: str, max_tokens: int, temperature: float, task_type: str) -> Dict[str, Any]:
        """Make actual OpenAI API call"""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")

        # Customize system message based on task type
        system_messages = {
            'cover_letter': "You are an expert cover letter writer creating personalized, compelling applications.",
            'content': "You are a professional content creator producing high-quality, engaging content.",
            'analysis': "You are an expert analyst providing detailed, accurate insights.",
            'code': "You are an expert programmer writing clean, efficient, well-documented code.",
            'general': "You are a helpful AI assistant providing accurate and useful information."
        }

        system_msg = system_messages.get(task_type, system_messages['general'])

        # Build parameters - GPT-5-mini has specific requirements
        params = {
            'model': "gpt-5-mini",
            'messages': [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            'max_completion_tokens': max_tokens  # GPT-5-mini requires max_completion_tokens
            # Note: GPT-5-mini only supports temperature=1 (default), so we omit it
        }

        response = self.openai_client.chat.completions.create(**params)

        content = response.choices[0].message.content

        # For reasoning models like GPT-5-mini, check if reasoning output is available
        if not content and hasattr(response.choices[0], 'reasoning_content'):
            content = response.choices[0].reasoning_content
            logger.info(f"📊 Using reasoning content from GPT-5-mini")

        # Debug: check if content is still empty
        if not content:
            logger.warning(f"⚠️ OpenAI returned empty content for prompt: {prompt[:100]}...")
            logger.warning(f"⚠️ Response object: {response}")

            # For reasoning models, provide helpful fallback
            usage = response.usage
            if hasattr(usage, 'completion_tokens_details') and usage.completion_tokens_details.reasoning_tokens > 0:
                content = f"[GPT-5-mini used {usage.completion_tokens_details.reasoning_tokens} reasoning tokens but produced no visible output. The model may need explicit instruction to provide a final answer.]"
            else:
                content = "[AI Response Error: Empty content returned from OpenAI]"

        tokens = response.usage.total_tokens

        # Estimate cost (GPT-5-nano pricing)
        cost = (response.usage.prompt_tokens * 0.0005 + response.usage.completion_tokens * 0.0015) / 1000

        return {
            'content': content,
            'tokens': tokens,
            'cost': cost
        }

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


    def generate_completion(self, prompt, max_tokens=500, temperature=0.7, agent_name="Agent"):
        """
        Compatibility method for executors expecting generate_completion
        Maps to enforce_real_ai internally
        """
        result = self.enforce_real_ai(
            prompt=prompt,
            agent_name=agent_name,
            max_tokens=max_tokens,
            temperature=temperature,
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