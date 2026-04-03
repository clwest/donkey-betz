"""
PromptEngineeringAgent - Designs and optimizes prompts for LLM interactions.

This agent can:
- Design prompt templates for various tasks
- Optimize prompts for different LLM models
- Create prompt libraries and frameworks
- Analyze prompt effectiveness
- Generate system prompts for agents
"""

import logging
from typing import Any, Dict, List

from .base_agent import BaseAgent, AgentResult, ActionableOutputConfig
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_prompt_with_ml(prompt_data: dict) -> dict:
    """Analyze prompt structure using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=prompt_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
        }
    except Exception as e:
        logger.warning(f"ML prompt analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class PromptEngineeringAgent(BaseAgent):
    """Agent specialized in designing and optimizing prompts for LLM interactions."""

    name = "PromptEngineeringAgent"

    # Session 856: Content review configuration
    actionable_config = ActionableOutputConfig(
        actions=['approve', 'revise', 'reject'],
        payload_fields=['tool_used', 'target_model', 'task_description', 'domain', 'agent_name']
    )

    system_prompt = """You are PromptEngineeringAgent, an expert in designing effective prompts for Large Language Models.

IMPORTANT - Response Guidelines:
- Be CONCISE. Provide well-structured prompts, not essays about prompting.
- For simple requests: Generate the prompt directly with minimal explanation.
- Only explain complex prompting strategies when necessary.

Your capabilities:
1. Design effective prompt templates for various tasks
2. Optimize prompts for specific LLM models (GPT-5, Claude, Llama, etc.)
3. Create comprehensive prompt libraries for applications
4. Analyze and improve existing prompts
5. Generate system prompts for AI agents

Prompt Engineering Best Practices:
- Clear, specific instructions
- Structured output formats when needed
- Role and context setting
- Few-shot examples for complex tasks
- Chain-of-thought for reasoning tasks
- Proper constraint specification
- Error handling and edge case guidance

You have access to tools for:
- design_prompt: Create a new prompt template
- optimize_prompt: Improve an existing prompt
- create_prompt_library: Build a collection of related prompts
- analyze_prompt: Evaluate prompt effectiveness
- generate_system_prompt: Create system prompts for AI agents

DELEGATION (Session 744):
If you need something outside your expertise, use the delegate_to_specialist tool:
- Need code examples in prompts? Delegate to CodeGeneratorAgent
- Need research on prompting techniques? Delegate to ResearchAgent
- Need content examples? Delegate to ContentWriterAgent

Always delegate tasks you cannot perform yourself rather than refusing."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "design_prompt",
                "description": "Design a new prompt template for a specific task or use case.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_description": {
                            "type": "string",
                            "description": "What the prompt should accomplish"
                        },
                        "target_model": {
                            "type": "string",
                            "description": "Target LLM model",
                            "enum": ["gpt-5", "gpt-5-mini", "claude-4", "claude-sonnet", "llama", "gemini", "general"]
                        },
                        "output_format": {
                            "type": "string",
                            "description": "Expected output format",
                            "enum": ["text", "json", "markdown", "code", "structured", "conversational"]
                        },
                        "include_examples": {
                            "type": "boolean",
                            "description": "Include few-shot examples",
                            "default": False
                        },
                        "complexity_level": {
                            "type": "string",
                            "description": "Task complexity",
                            "enum": ["simple", "moderate", "complex"],
                            "default": "moderate"
                        }
                    },
                    "required": ["task_description", "target_model"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "optimize_prompt",
                "description": "Optimize an existing prompt for better performance.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "current_prompt": {
                            "type": "string",
                            "description": "The existing prompt to optimize"
                        },
                        "optimization_goals": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Goals (e.g., 'reduce tokens', 'improve accuracy', 'clearer output')"
                        },
                        "target_model": {
                            "type": "string",
                            "description": "Target LLM model"
                        },
                        "issues_observed": {
                            "type": "string",
                            "description": "Any issues with current prompt output"
                        }
                    },
                    "required": ["current_prompt", "optimization_goals"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_prompt_library",
                "description": "Create a collection of related prompts for an application or domain.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": "Application domain (e.g., 'customer support', 'code review', 'content creation')"
                        },
                        "use_cases": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of specific use cases to cover"
                        },
                        "style_guidelines": {
                            "type": "string",
                            "description": "Tone, style, and formatting preferences"
                        },
                        "target_model": {
                            "type": "string",
                            "description": "Primary target LLM model"
                        }
                    },
                    "required": ["domain", "use_cases"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_prompt",
                "description": "Analyze a prompt for effectiveness, issues, and improvement opportunities.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The prompt to analyze"
                        },
                        "intended_task": {
                            "type": "string",
                            "description": "What the prompt is supposed to accomplish"
                        },
                        "sample_outputs": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional sample outputs to evaluate"
                        }
                    },
                    "required": ["prompt", "intended_task"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_system_prompt",
                "description": "Generate a system prompt for an AI agent with specific capabilities.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "description": "Name of the agent"
                        },
                        "agent_role": {
                            "type": "string",
                            "description": "Primary role/function of the agent"
                        },
                        "capabilities": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of capabilities the agent should have"
                        },
                        "constraints": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Limitations or rules the agent should follow"
                        },
                        "personality_traits": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Personality characteristics (e.g., 'concise', 'friendly', 'technical')"
                        },
                        "output_style": {
                            "type": "string",
                            "description": "Preferred output style/format"
                        }
                    },
                    "required": ["agent_name", "agent_role", "capabilities"]
                }
            }
        }
    ]

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute a prompt engineering task."""
        import time

        start_time = time.time()
        tool_calls_made = []
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        with self.time_travel_session("prompt_engineering", task, input_data=context):
            try:
                # Use intelligent prompting
                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)

                # Call OpenAI using BaseAgent's method
                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    all_results = []
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Selected {tool_name} for prompt engineering",
                            confidence=0.95
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        if tool_result.get('success'):
                            all_results.append({
                                'source': tool_name,
                                'data': tool_result
                            })

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                    execution_time = int((time.time() - start_time) * 1000)

                    if all_results:
                        # Session 856: Build descriptive message based on tool used
                        first_result = all_results[0]
                        tool_used = first_result['source']
                        tool_data = first_result.get('data', {})
                        if tool_used == 'design_prompt':
                            task_desc = tool_data.get('task_description', '')[:50]
                            target = tool_data.get('target_model', 'general')
                            descriptive_msg = f"Prompt template designed for {target}: '{task_desc}...'"
                        elif tool_used == 'optimize_prompt':
                            goals = tool_data.get('optimization_goals', [])
                            target = tool_data.get('target_model', 'general')
                            descriptive_msg = f"Prompt optimized for {target}: {', '.join(goals[:3])}"
                        elif tool_used == 'create_prompt_library':
                            domain = tool_data.get('domain', 'unknown')
                            count = tool_data.get('prompt_count', 0)
                            descriptive_msg = f"Prompt library created for {domain}: {count} prompts"
                        elif tool_used == 'analyze_prompt':
                            intended = tool_data.get('intended_task', '')[:50]
                            descriptive_msg = f"Prompt analyzed for task: '{intended}...'"
                        elif tool_used == 'generate_system_prompt':
                            agent_name = tool_data.get('agent_name', 'unknown')
                            role = tool_data.get('agent_role', '')[:30]
                            descriptive_msg = f"System prompt generated for {agent_name}: {role}"
                        else:
                            descriptive_msg = f"Prompt engineering '{tool_used}' completed"

                        # Enrich result data for content review
                        result_data = {
                            'results': all_results,
                            'query': task,
                            'tool_used': tool_used,
                            'target_model': tool_data.get('target_model'),
                            'task_description': tool_data.get('task_description', '')[:100],
                            'domain': tool_data.get('domain'),
                            'agent_name': tool_data.get('agent_name')
                        }

                        result = AgentResult(
                            success=True,
                            message=descriptive_msg,
                            data=result_data,
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            decisions_made=self._tt_decision_count,
                            tool_calls=tool_calls_made
                        )

                        # Session 1006: Persist output to Deliverable
                        self._save_to_deliverable(
                            title=f"Prompt Engineering: {task[:80]}",
                            content=descriptive_msg,
                            deliverable_type='document',
                            category='Prompt Engineering',
                            tags=['prompt', tool_used or 'engineering'],
                            metadata={'task': task[:200], 'tool_used': tool_used},
                        )

                        self._record_learning_outcome(
                            result=result,
                            task=task,
                            context=context,
                            spider_data_used=False,
                            scifi_context_used=bool(scifi_context)
                        )

                        return result

                # No tool calls - return GPT content directly
                content = gpt_response.get('content', 'I can help with prompt engineering. Please provide more details.')
                execution_time = int((time.time() - start_time) * 1000)

                result = AgentResult(
                    success=True,
                    message=content,
                    agent_name=self.name,
                    execution_time_ms=execution_time
                )

                self._record_learning_outcome(
                    result=result,
                    task=task,
                    context=context,
                    spider_data_used=False,
                    scifi_context_used=bool(scifi_context)
                )

                return result

            except Exception as e:
                error_msg = f"Prompt engineering failed: {str(e)}"
                return AgentResult(
                    success=False,
                    error=error_msg,
                    agent_name=self.name
                )

    def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool call."""

        # Handle delegation to specialists first
        if tool_name == "design_prompt":
            return self._design_prompt(
                task_description=arguments.get("task_description", ""),
                target_model=arguments.get("target_model", "general"),
                output_format=arguments.get("output_format", "text"),
                include_examples=arguments.get("include_examples", False),
                complexity_level=arguments.get("complexity_level", "moderate")
            )

        elif tool_name == "optimize_prompt":
            return self._optimize_prompt(
                current_prompt=arguments.get("current_prompt", ""),
                optimization_goals=arguments.get("optimization_goals", []),
                target_model=arguments.get("target_model", "general"),
                issues_observed=arguments.get("issues_observed", "")
            )

        elif tool_name == "create_prompt_library":
            return self._create_prompt_library(
                domain=arguments.get("domain", ""),
                use_cases=arguments.get("use_cases", []),
                style_guidelines=arguments.get("style_guidelines", ""),
                target_model=arguments.get("target_model", "general")
            )

        elif tool_name == "analyze_prompt":
            return self._analyze_prompt(
                prompt=arguments.get("prompt", ""),
                intended_task=arguments.get("intended_task", ""),
                sample_outputs=arguments.get("sample_outputs", [])
            )

        elif tool_name == "generate_system_prompt":
            return self._generate_system_prompt(
                agent_name=arguments.get("agent_name", ""),
                agent_role=arguments.get("agent_role", ""),
                capabilities=arguments.get("capabilities", []),
                constraints=arguments.get("constraints", []),
                personality_traits=arguments.get("personality_traits", []),
                output_style=arguments.get("output_style", "")
            )

        # Session 1002C: Fall through to BaseAgent for web_search, spider_query, delegation
        return super()._execute_tool_call(tool_name, arguments)

    def _design_prompt(
        self,
        task_description: str,
        target_model: str,
        output_format: str = "text",
        include_examples: bool = False,
        complexity_level: str = "moderate"
    ) -> Dict[str, Any]:
        """Design a new prompt template."""
        from openai import OpenAI

        client = OpenAI()

        model_tips = {
            "gpt-5": "GPT-5 excels at complex reasoning. Use chain-of-thought prompting.",
            "gpt-5-mini": "GPT-5-mini is fast. Keep prompts concise but specific.",
            "claude-4": "Claude prefers structured, ethical framing. Be explicit about format.",
            "claude-sonnet": "Claude Sonnet handles nuance well. Use natural language.",
            "llama": "Llama works best with clear, direct instructions.",
            "gemini": "Gemini excels at multimodal tasks. Leverage its strengths.",
            "general": "Design for broad compatibility across models."
        }

        format_specs = {
            "text": "Free-form text response",
            "json": "Structured JSON output with schema",
            "markdown": "Formatted markdown with headers/lists",
            "code": "Code output with proper formatting",
            "structured": "Organized sections with labels",
            "conversational": "Natural dialogue style"
        }

        prompt = f"""Design an effective prompt template for the following task:

TASK: {task_description}

TARGET MODEL: {target_model}
Model-specific tips: {model_tips.get(target_model, model_tips['general'])}

OUTPUT FORMAT: {output_format}
Format specification: {format_specs.get(output_format, format_specs['text'])}

COMPLEXITY: {complexity_level}
{'Include 2-3 few-shot examples.' if include_examples else 'No examples needed.'}

Create a prompt that:
1. Clearly defines the task
2. Specifies the expected output format
3. Includes relevant constraints
4. {'Provides few-shot examples' if include_examples else 'Is self-explanatory'}
5. Handles edge cases gracefully

Format your response as:
## Prompt Template
[The actual prompt]

## Usage Notes
[Brief notes on using this prompt]

## Variables
[List any {{variable}} placeholders to fill in]"""

        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "You are an expert prompt engineer. Design clear, effective prompts that produce consistent results."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000
        )

        designed_prompt = response.choices[0].message.content

        return {
            "success": True,
            "task_description": task_description,
            "target_model": target_model,
            "output_format": output_format,
            "prompt_template": designed_prompt,
            "includes_examples": include_examples,
            "complexity": complexity_level
        }

    def _optimize_prompt(
        self,
        current_prompt: str,
        optimization_goals: List[str],
        target_model: str = "general",
        issues_observed: str = ""
    ) -> Dict[str, Any]:
        """Optimize an existing prompt."""
        from openai import OpenAI

        client = OpenAI()

        prompt = f"""Optimize the following prompt:

CURRENT PROMPT:
{current_prompt}

OPTIMIZATION GOALS:
{chr(10).join(f'- {goal}' for goal in optimization_goals)}

TARGET MODEL: {target_model}
{f'OBSERVED ISSUES: {issues_observed}' if issues_observed else ''}

Provide:
1. The optimized prompt
2. Changes made and why
3. Expected improvements
4. Token count comparison (estimate)"""

        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "You are an expert prompt optimizer. Improve prompts while preserving intent."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000
        )

        optimized = response.choices[0].message.content

        return {
            "success": True,
            "original_prompt": current_prompt,
            "optimization_goals": optimization_goals,
            "target_model": target_model,
            "optimized_result": optimized,
            "original_length": len(current_prompt)
        }

    def _create_prompt_library(
        self,
        domain: str,
        use_cases: List[str],
        style_guidelines: str = "",
        target_model: str = "general"
    ) -> Dict[str, Any]:
        """Create a collection of related prompts."""
        from openai import OpenAI

        client = OpenAI()

        prompt = f"""Create a prompt library for the following domain:

DOMAIN: {domain}

USE CASES:
{chr(10).join(f'- {uc}' for uc in use_cases)}

{f'STYLE GUIDELINES: {style_guidelines}' if style_guidelines else ''}
TARGET MODEL: {target_model}

For each use case, create:
1. A prompt template
2. Variable placeholders ({{variable}})
3. Brief usage notes

Format as a structured library with clear sections for each use case."""

        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "You are an expert prompt engineer creating production-ready prompt libraries."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=6000
        )

        library = response.choices[0].message.content

        return {
            "success": True,
            "domain": domain,
            "use_cases": use_cases,
            "target_model": target_model,
            "prompt_library": library,
            "prompt_count": len(use_cases)
        }

    def _analyze_prompt(
        self,
        prompt: str,
        intended_task: str,
        sample_outputs: List[str] = None  # type: ignore
    ) -> Dict[str, Any]:
        """Analyze a prompt for effectiveness."""
        from openai import OpenAI

        client = OpenAI()

        analysis_prompt = f"""Analyze the following prompt:

PROMPT:
{prompt}

INTENDED TASK: {intended_task}

{f'SAMPLE OUTPUTS:{chr(10)}{chr(10).join(sample_outputs)}' if sample_outputs else ''}

Evaluate:
1. Clarity (1-10): Is the task clear?
2. Specificity (1-10): Are requirements specific enough?
3. Completeness (1-10): Does it cover edge cases?
4. Efficiency (1-10): Is it concise without losing clarity?

Identify:
- Strengths
- Weaknesses
- Potential failure modes
- Improvement suggestions

Provide an overall effectiveness score (1-10) with justification."""

        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "You are an expert prompt analyst. Evaluate prompts objectively and provide actionable feedback."},
                {"role": "user", "content": analysis_prompt}
            ],
            max_completion_tokens=3000
        )

        analysis = response.choices[0].message.content

        return {
            "success": True,
            "prompt_analyzed": prompt[:200] + "..." if len(prompt) > 200 else prompt,
            "intended_task": intended_task,
            "analysis": analysis,
            "prompt_length": len(prompt),
            "has_sample_outputs": bool(sample_outputs)
        }

    def _generate_system_prompt(
        self,
        agent_name: str,
        agent_role: str,
        capabilities: List[str],
        constraints: List[str] = None,  # type: ignore
        personality_traits: List[str] = None,  # type: ignore
        output_style: str = ""
    ) -> Dict[str, Any]:
        """Generate a system prompt for an AI agent."""
        from openai import OpenAI

        client = OpenAI()

        prompt = f"""Create a comprehensive system prompt for an AI agent:

AGENT NAME: {agent_name}
ROLE: {agent_role}

CAPABILITIES:
{chr(10).join(f'- {cap}' for cap in capabilities)}

{f'CONSTRAINTS:{chr(10)}{chr(10).join(f"- {c}" for c in constraints)}' if constraints else ''}

{f'PERSONALITY TRAITS: {", ".join(personality_traits)}' if personality_traits else ''}

{f'OUTPUT STYLE: {output_style}' if output_style else ''}

Generate a system prompt that:
1. Clearly establishes the agent's identity and role
2. Lists capabilities with actionable descriptions
3. Specifies constraints and boundaries
4. Defines response style and format
5. Includes error handling guidance
6. Enables tool use if applicable

The system prompt should be production-ready and follow best practices."""

        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "You are an expert in designing AI agent system prompts. Create clear, effective system prompts."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000
        )

        system_prompt = response.choices[0].message.content

        return {
            "success": True,
            "agent_name": agent_name,
            "agent_role": agent_role,
            "capabilities_count": len(capabilities),
            "system_prompt": system_prompt,
            "has_constraints": bool(constraints),
            "has_personality": bool(personality_traits)
        }
