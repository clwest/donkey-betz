"""
Session 1038: DynamicPersonaAgent — makes all 218 agent personas routable.

Instead of creating 139 separate Python files for DB-only agent personas,
this single class loads its identity from the Agent DB record at construction
time. The AgentRouter falls back to this when AGENT_MAP lookup fails.

Usage:
    agent = DynamicPersonaAgent(persona_name="Hidden Job Market Explorer", user=user)
    result = agent.execute(task, context, scifi_context, spider_context)
"""

import logging
import time
from typing import Any, Dict, List

from core.agents.base_agent import AgentResult, BaseAgent

logger = logging.getLogger(__name__)


class DynamicPersonaAgent(BaseAgent):
    """
    A generic agent that loads its persona from the Agent DB record.

    Handles any of the 139 DB-only agent personas (e.g. "Hidden Job Market Explorer",
    "Resume Optimizer AI") that don't have dedicated Python classes.

    Tools: web_search + spider_query (standard research tools).
    System prompt: synthesized from Agent.name + description + specialization.
    """

    name = "DynamicPersonaAgent"
    system_prompt = ""  # Set dynamically in __init__

    tools = [
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for current information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of results (1-20)",
                            "default": 10
                        },
                        "search_type": {
                            "type": "string",
                            "description": "Type of search",
                            "enum": ["search", "news"],
                            "default": "search"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "spider_query",
                "description": "Query the spider network for intelligence from 70+ data sources",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for spider data"
                        },
                        "category": {
                            "type": "string",
                            "description": "Filter by category",
                            "enum": ["tech", "financial", "jobs", "news", "social", "creative", "crypto"]
                        },
                        "hours": {
                            "type": "integer",
                            "description": "Look back period in hours",
                            "default": 72
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results",
                            "default": 20
                        }
                    },
                    "required": ["query"]
                }
            }
        },
    ]

    def __init__(self, persona_name: str = "", user=None, health_check_mode: bool = False):
        super().__init__(user=user, health_check_mode=health_check_mode)

        self._persona_name = persona_name
        self._persona_record = None

        if persona_name:
            self.name = persona_name
            self.agent_name = persona_name
            self._load_persona()

    def _load_persona(self) -> None:
        """Load persona identity from the Agent DB record."""
        try:
            from core.models_unified_system import Agent
            self._persona_record = Agent.objects.get(name=self._persona_name)

            desc = self._persona_record.description or ""
            spec = self._persona_record.specialization or ""
            agent_type = self._persona_record.agent_type or ""

            self.system_prompt = (
                f"You are {self._persona_name}, a specialized AI agent.\n\n"
                f"Your specialization: {spec}\n"
                f"Your domain: {agent_type}\n"
                f"Your role: {desc}\n\n"
                "Use the tools available to you (web_search, spider_query) to gather "
                "real data and provide evidence-based analysis. Be specific, actionable, "
                "and grounded in facts. Cite sources when possible.\n\n"
                "IMPORTANT: You must use your tools to gather real information. "
                "Do not fabricate data or make claims without evidence."
            )

            logger.info(
                f"[DynamicPersona] Loaded persona '{self._persona_name}' "
                f"(type={agent_type}, spec={spec})"
            )

        except Exception as e:
            logger.warning(
                f"[DynamicPersona] Failed to load persona '{self._persona_name}': {e}. "
                f"Using fallback prompt."
            )
            self.system_prompt = (
                f"You are {self._persona_name}, a specialized AI agent. "
                "Provide thorough, evidence-based analysis using available tools."
            )

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute a task using the loaded persona identity."""
        start_time = time.time()
        tool_calls_made = []

        if not isinstance(context, dict):
            context = {}

        with self.time_travel_session("dynamic_persona", task, input_data=context):
            self.record_decision(
                decision_type="task_analysis",
                action=f"Processing as {self._persona_name}",
                reasoning=f"Task: {task[:100] if task else 'No task'}",
                confidence=0.8
            )

            try:
                prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)

                execution_context = {
                    'spider_context': spider_context,
                    'scifi_context': scifi_context,
                    'task': task,
                }
                response = self._call_openai(prompt, execution_context=execution_context)

                # Process tool calls if any
                if response.get('tool_calls'):
                    tool_results = []
                    for tool_call in response['tool_calls']:
                        tool_name = tool_call['name']
                        tool_input = tool_call['arguments']
                        tool_calls_made.append({"name": tool_name, "input": tool_input})
                        result = self._execute_tool_call(tool_name, tool_input)
                        tool_results.append(result)

                    # Make a follow-up call with tool results
                    follow_up_messages = [
                        {"role": "assistant", "content": None, "tool_calls": [
                            {"id": tc.get('id', f"call_{i}"), "type": "function",
                             "function": {"name": tc['name'], "arguments": str(tc['arguments'])}}
                            for i, tc in enumerate(response['tool_calls'])
                        ]},
                    ]
                    for i, tr in enumerate(tool_results):
                        follow_up_messages.append({
                            "role": "tool",
                            "tool_call_id": response['tool_calls'][i].get('id', f"call_{i}"),
                            "content": str(tr)[:4000],
                        })

                    final_response = self._call_openai(
                        prompt,
                        conversation_history=follow_up_messages,
                        execution_context=execution_context
                    )
                    message = final_response.get('content') or response.get('content') or "Analysis complete."
                else:
                    message = response.get('content') or "Analysis complete."

                execution_time_ms = int((time.time() - start_time) * 1000)

                result = AgentResult(
                    success=True,
                    message=message,
                    data={"persona": self._persona_name},
                    agent_name=self.name,
                    execution_time_ms=execution_time_ms,
                    tool_calls=tool_calls_made,
                    output_category="analysis",
                )

                try:
                    self._record_learning_outcome(
                        task=task,
                        result=result,
                        success=True,
                        context={
                            'agent_type': 'DynamicPersonaAgent',
                            'persona': self._persona_name,
                            'execution_time_ms': execution_time_ms,
                            'tools_used': [tc['name'] for tc in tool_calls_made],
                        }
                    )
                except Exception as _e:
                    logger.warning(
                        "dynamic_persona_agent.execute: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

                self._save_to_deliverable(
                    title=f"{self._persona_name}: {task[:80]}",
                    content=message,
                    category="analysis",
                )

                return result

            except Exception as e:
                execution_time_ms = int((time.time() - start_time) * 1000)
                logger.error(f"[DynamicPersona] {self._persona_name} failed: {e}")

                return AgentResult(
                    success=False,
                    message="",
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=execution_time_ms,
                    tool_calls=tool_calls_made,
                )
