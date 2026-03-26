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
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from functools import wraps
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
                # Session 802: Add 60-second timeout to prevent browser timeout (default is 10 min)
                self.openai_client = OpenAI(api_key=api_key, timeout=60.0)
                logger.info("✅ OpenAI client initialized - REAL AI AVAILABLE (60s timeout)")
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
                       tool_choice: Optional[Dict] = None,
                       input_messages: Optional[List[Dict]] = None,
                       trace_id: str = "") -> Dict[str, Any]:
        """
        ENFORCE real AI usage - this is the ONLY way to get AI responses

        Session 129: Added previous_response_id parameter for GPT-5.1 chain of thought
        Session 1036: Added input_messages for structured Responses API input

        Args:
            prompt: The actual prompt to send
            context: Additional context for the task
            agent_name: Name of the agent making the request
            task_type: Type of task (cover_letter, analysis, content, etc.)
            max_tokens: Maximum tokens for response
            temperature: Creativity level (0-1)
            use_claude: Use Claude instead of GPT
            input_messages: Structured messages array for Responses API (overrides prompt+context)

        Returns:
            Dict with response and metadata

        Raises:
            Exception if no LLM is available
        """
        logger.info(f"🔒 ENFORCING REAL AI for {agent_name} - Task: {task_type}")

        # Session 1064: Check LUNGS budget before making LLM call
        try:
            from django.conf import settings as django_settings
            if getattr(django_settings, 'LUNGS_ENFORCE_HARD_LIMIT', True):
                from core.services.lungs import get_lungs_monitor
                lungs = get_lungs_monitor()
                can_proceed, reason = lungs.can_breathe(agent=agent_name)
                if not can_proceed:
                    logger.warning(f"LUNGS hard limit: blocking LLM call for {agent_name}: {reason}")
                    return {
                        'success': False,
                        'response': f'[BLOCKED: {reason}]',
                        'error': f'Budget exhausted: {reason}',
                        'blocked_by_lungs': True,
                        'agent': agent_name,
                        'call_id': hashlib.md5(f"{agent_name}_{datetime.now()}".encode()).hexdigest()[:8],
                    }
        except Exception:
            pass  # Never block LLM calls due to LUNGS errors

        # Session 1088: Check BudgetController flags
        try:
            from core.models.system import SystemConfiguration

            # Hard freeze check — only critical purposes allowed
            freeze_flag = SystemConfiguration.objects.filter(
                key='budget_freeze_active',
                is_active=True,
            ).values_list('value', flat=True).first()
            if freeze_flag:
                critical_purposes = {'governance', 'auth', 'incident_response', 'pa_chat'}
                critical_agents = {'PersonalAssistant'}
                if task_type not in critical_purposes and agent_name not in critical_agents:
                    logger.warning(
                        f"[BudgetController] FROZEN: blocking {agent_name}/{task_type}"
                    )
                    return {
                        'success': False,
                        'response': '[BLOCKED: Budget freeze active — non-critical calls paused]',
                        'error': 'Budget freeze active',
                        'blocked_by_budget': True,
                        'agent': agent_name,
                        'call_id': hashlib.md5(
                            f"{agent_name}_{datetime.now()}".encode()
                        ).hexdigest()[:8],
                    }

            # Downgrade check — route to cheaper model
            downgrade_flag = SystemConfiguration.objects.filter(
                key='budget_downgrade_active',
            ).values_list('value', flat=True).first()
            if downgrade_flag and not use_claude:
                downgrade_model = SystemConfiguration.objects.filter(
                    key='autopilot_tuning:BUDGET_DOWNGRADE_MODEL',
                ).values_list('value', flat=True).first()
                if not downgrade_model:
                    downgrade_model = 'gpt-5-mini'
                # Override will happen via _call_openai model selection
                if not hasattr(self, '_budget_downgrade_model'):
                    self._budget_downgrade_model = None
                self._budget_downgrade_model = downgrade_model
        except Exception:
            pass  # Never block LLM calls due to budget check errors

        # Session 1088: ROI throttle check — cooldown for low-ROI agents
        try:
            from core.services.ops_autopilot import ROIEnforcer
            throttle = ROIEnforcer().check_throttle(agent_name)
            if throttle and task_type not in {'pa_chat', 'governance', 'auth', 'incident_response'} and agent_name not in {'PersonalAssistant'}:
                logger.info(
                    f"[ROIEnforcer] Throttled: {agent_name} "
                    f"(cooldown {throttle.get('cooldown_minutes')}min, "
                    f"ROI {throttle.get('roi', 0):.1%})"
                )
                return {
                    'success': False,
                    'response': (
                        f'[THROTTLED: {agent_name} on ROI cooldown — '
                        f'next call allowed after {throttle.get("expires_at", "soon")}]'
                    ),
                    'error': 'ROI throttle active',
                    'throttled_by_roi': True,
                    'agent': agent_name,
                    'call_id': hashlib.md5(
                        f"{agent_name}_{datetime.now()}".encode()
                    ).hexdigest()[:8],
                }
        except Exception:
            pass  # Never block due to ROI check errors

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
            # Session 803: Track latency for analytics
            start_time = time.time()

            if use_claude and self.anthropic_client:
                # Use Claude
                response = self._call_claude(full_prompt, max_tokens, temperature)
                provider = "anthropic"
                model = "claude-3-haiku"
            elif self.openai_client:
                # Session 129: Pass context separately so GPT can see project assets
                # Session 129: Pass previous_response_id for chain of thought
                # Session 129: Pass tool_choice to force tool execution
                # Session 1036: Pass input_messages for structured Responses API input
                response = self._call_openai(prompt, max_tokens, temperature, task_type, tools, context, previous_response_id, tool_choice, input_messages)
                provider = "openai"
                model = "gpt-5.2"  # Session 1036: Upgraded to GPT-5.2 (agentic tool calling optimized)
            else:
                raise Exception("No LLM client available")

            # Session 803: Calculate latency in milliseconds
            latency_ms = int((time.time() - start_time) * 1000)

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
                'latency_ms': latency_ms,  # Session 803: Track latency
                'success': True
            }
            self.call_log.append(log_entry)

            logger.info(f"✅ REAL AI RESPONSE generated - {provider}/{model} - {response.get('tokens', 0)} tokens ({latency_ms}ms)")

            # Session 802/803: Persist to CostTracking and LLMCallLog databases
            self._save_cost_tracking(
                provider=provider,
                model=model,
                agent_name=agent_name,
                task_type=task_type,
                input_tokens=response.get('input_tokens', 0),
                output_tokens=response.get('output_tokens', 0),
                total_tokens=response.get('tokens', 0),
                cost=response.get('cost', 0),
                latency_ms=latency_ms,
                success=True,
                trace_id=trace_id,
            )

            result = {
                'success': True,
                'response': response['content'],
                'provider': provider,
                'model': model,
                'tokens': response.get('tokens', 0),
                'cost': response.get('cost', 0),
                'call_id': call_id,
                'agent': agent_name,
                'truncated': response.get('truncated', False),
            }

            # Session 125: Include tool calls if present
            if 'tool_calls' in response:
                result['tool_calls'] = response['tool_calls']
                logger.info(f"🛠️ Returning {len(response['tool_calls'])} tool calls to caller")

            # Session 1036: Always include response_id for chaining
            if 'response_id' in response:
                result['response_id'] = response['response_id']

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

    def _call_openai(self, prompt: str, max_tokens: int, temperature: float, task_type: str, tools: Optional[List[Dict]] = None, context: str = "", previous_response_id: Optional[str] = None, tool_choice: Optional[Dict] = None, input_messages: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Make actual OpenAI API call using GPT-5.2 with Responses API

        Session 129: Migrated to GPT-5.1 with Responses API
        Session 1036: Upgraded to GPT-5.2, added input_messages for structured input
        - Uses gpt-5.2 (optimized for agentic tool calling, 90% cached discount)
        - Responses API for chain of thought passing
        - Proper reasoning.effort and text.verbosity configuration
        - Tool calling support via Responses API
        - Tool forcing via tool_choice with allowed_tools (mode: required)
        - input_messages: structured messages array (overrides prompt+context)
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

        # Session 1036: If structured input_messages provided, use directly
        if input_messages:
            full_input = input_messages
        else:
            # Combine system message and user prompt for Responses API input
            full_input = f"{system_msg}\n\nUser request: {prompt}"

        # Session 129: GPT-5.1 with Responses API
        # Configure reasoning effort based on task type
        # Valid values: none, low, medium, high, xhigh
        reasoning_effort_map = {
            'conversation': 'low',     # Session 129: Changed from 'none' to 'low' for better agentic tool execution
            'cover_letter': 'low',     # Quick content generation
            'content': 'low',          # Quick content generation
            'analysis': 'medium',      # Balanced analysis
            'code': 'high',            # Complex coding tasks
            'general': 'low'           # Default fast mode
        }
        reasoning_effort = reasoning_effort_map.get(task_type, 'low')
        _VALID_EFFORTS = {'none', 'low', 'medium', 'high', 'xhigh'}
        if reasoning_effort not in _VALID_EFFORTS:
            logger.warning(f"[LLMEnforcer] Invalid reasoning.effort={reasoning_effort!r}; coercing to 'low'")
            reasoning_effort = 'low'

        # Build Responses API parameters
        # Session 1036: GPT-5.2 pricing: $1.75/1M input, $14/1M output
        #   Cached input (via previous_response_id): $0.18/1M (90% discount)
        # Session 1088: Apply budget downgrade if active
        effective_model = "gpt-5.2"
        if getattr(self, '_budget_downgrade_model', None):
            effective_model = self._budget_downgrade_model
            logger.info(
                f"[BudgetController] Downgrading {task_type} from gpt-5.2 → {effective_model}"
            )

        params = {
            'model': effective_model,                    # Session 1036/1088: Budget-aware model selection
            'input': full_input,                         # Messages array or combined string
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
                logger.info(f"🛠️ GPT-5.2 returned {len(function_calls)} tool calls in output list!")
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

        # Calculate usage and cost for GPT-5.2
        usage = response.usage if hasattr(response, 'usage') else None
        if usage:
            # GPT-5.2 pricing: $1.75/1M input, $14.00/1M output
            # Cached input (via previous_response_id): $0.18/1M (90% discount)
            input_tokens = usage.input_tokens if hasattr(usage, 'input_tokens') else 0
            output_tokens = usage.output_tokens if hasattr(usage, 'output_tokens') else 0
            reasoning_tokens = usage.reasoning_tokens if hasattr(usage, 'reasoning_tokens') else 0

            # Calculate cost (reasoning tokens count toward input cost)
            total_input = input_tokens + reasoning_tokens
            cost = (total_input * 1.75 / 1_000_000) + (output_tokens * 14.00 / 1_000_000)
            total_tokens = input_tokens + output_tokens + reasoning_tokens

            logger.info(f"💰 GPT-5.2 usage: {input_tokens} input + {reasoning_tokens} reasoning + {output_tokens} output = {total_tokens} total tokens (${cost:.6f})")
        else:
            total_tokens = 0
            cost = 0.0

        # Session 266/1065: Detect truncation — authoritative API check first, heuristic fallback
        truncated = False
        if hasattr(response, 'status') and response.status == 'incomplete':
            truncated = True
            reason = getattr(getattr(response, 'incomplete_details', None), 'reason', 'unknown')
            logger.warning(f"⚠️ Response truncated (status=incomplete, reason={reason})")
        elif usage and output_tokens >= (max_tokens - 10):
            truncated = True
            logger.warning(f"⚠️ Response likely truncated (heuristic): {output_tokens} output tokens (max: {max_tokens})")

        # Build response dict
        result = {
            'content': content,
            'tokens': total_tokens,
            'cost': cost,
            'truncated': truncated,  # Session 266: Flag for continuation handling
            # Session 802: Add detailed token breakdown for CostTracking
            'input_tokens': input_tokens if usage else 0,
            'output_tokens': output_tokens if usage else 0,
            'reasoning_tokens': reasoning_tokens if usage else 0,
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

        content = response.content[0].text if response.content else ""  # type: ignore[union-attr]

        # Session 802: Extract detailed token usage for CostTracking
        input_tokens = response.usage.input_tokens if hasattr(response, 'usage') else 0
        output_tokens = response.usage.output_tokens if hasattr(response, 'usage') else 0
        tokens = input_tokens + output_tokens

        # Estimate cost (Claude Haiku pricing)
        cost = tokens * 0.00025 / 1000

        return {
            'content': content,
            'tokens': tokens,
            'cost': cost,
            # Session 802: Add detailed token breakdown for CostTracking
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
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

    def _save_cost_tracking(
        self,
        provider: str,
        model: str,
        agent_name: str,
        task_type: str,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        cost: float,
        latency_ms: int = 0,
        success: bool = True,
        error_message: str = "",
        trace_id: str = "",
    ) -> None:
        """
        Session 802: Persist LLM usage to both CostTracking and LLMCallLog.

        Session 803: Added LLMCallLog for analytics UI display.
        This enables the LLM Routing page to show actual API costs over time.
        """
        # Save to LLMCallLog (used by LLM Routing analytics UI)
        try:
            from core.models_llm_routing import LLMCallLog

            LLMCallLog.objects.create(
                agent_name=agent_name,
                provider=provider,
                model_id=model,
                task_type=task_type,
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens,
                total_tokens=total_tokens,
                cost=cost,
                latency_ms=latency_ms,
                success=success,
                error_message=error_message,
                trace_id=trace_id,
            )
            logger.debug(f"💾 Saved LLM call log: {provider}/{model} - ${cost:.6f}")
        except Exception as e:
            # Don't fail the LLM call if logging fails
            logger.warning(f"⚠️ Failed to save LLM call log: {e}")

        # Also save to CostTracking (for broader cost analysis)
        try:
            from core.models_unified_system import CostTracking

            CostTracking.objects.create(
                provider=provider,
                service=model,
                operation=task_type,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=cost,
                # TODO(Session 1064): populate tenant= once request-context
                # tenant resolution is available in the LLM call path.
                metadata={
                    'agent_name': agent_name,
                    'model': model,
                },
            )
        except Exception as e:
            logger.warning(f"⚠️ Failed to save cost tracking: {e}")

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