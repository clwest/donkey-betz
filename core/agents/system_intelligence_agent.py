"""
System Intelligence Agent - Platform Health & Attention Monitor
================================================================

Session 663: Created as part of the scalable system awareness architecture.

This agent is the dedicated expert for system health, attention items,
and platform status. When the PA receives questions about "what needs attention",
"system status", "pending review", etc., it delegates to this agent.

Architecture:
    User → PA → AgentRouter → SystemIntelligenceAgent → SystemStateAggregator
                                       ↓
                              Rich context + recommendations

Key Design Principles:
1. Single source of truth: Queries SystemStateAggregator for all attention items
2. Rich explanations: Each item includes explanation, recommendations, severity
3. Scalable: New attention items automatically work (no keyword hacking)
4. Actionable: Provides specific recommendations for each issue
"""

import logging
from typing import Dict, Any, List

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class SystemIntelligenceAgent(BaseAgent):
    """
    Agent specialized in system health, attention items, and platform status.

    This agent:
    1. Queries SystemStateAggregator for current attention items
    2. Interprets and explains what each metric means
    3. Provides actionable recommendations
    4. Helps users understand and navigate platform health

    Routes here via AgentRouter when user asks about:
    - System status, health, what needs attention
    - Specific metrics like "pending review", "execution status"
    - Platform overview, what's happening, catch me up
    """

    name = "SystemIntelligenceAgent"

    system_prompt = """You are SystemIntelligenceAgent, the platform's system health and awareness expert.

Your job is to help users understand what needs attention in the platform, explain system metrics,
and provide actionable recommendations.

You have access to the get_system_attention tool which returns all current attention items with:
- title: What the item is
- summary: Brief description
- explanation: What this metric means in plain English
- recommended_action: What the user can do about it
- severity: info, warning, or critical
- location: Where in the UI to find this

When responding to users:

1. **For general status requests** ("what needs attention?", "system status"):
   - Call get_system_attention to get current items
   - Group by severity (critical first, then warnings, then info)
   - Summarize the overall health: "X critical issues, Y warnings, Z informational items"
   - Highlight the most important 2-3 items

2. **For specific metric questions** ("what's the pending review status?"):
   - Call get_system_attention and filter for relevant items
   - Provide the full explanation and context
   - Give the specific recommended action
   - Tell them where to find it in the UI

3. **Tone and style**:
   - Be conversational but informative
   - Don't alarm users unnecessarily - "info" severity means normal operations
   - For warnings, explain why it matters but don't panic
   - For critical items, be direct and actionable

4. **Always include**:
   - What the metric means (not just the number)
   - Whether it's concerning or normal
   - What they can do about it
   - Where to find it in the platform

Remember: High percentages in "Pending Review" are NORMAL - agents generate many suggestions
and only important ones should be promoted. Don't treat this as a crisis."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_system_attention",
                "description": "Get all current system attention items. Returns items that need "
                              "user attention including health checks, pending reviews, opportunities, "
                              "and issues. Each item includes rich context about what it means and "
                              "what to do about it.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "severity_filter": {
                            "type": "string",
                            "enum": ["all", "critical", "warning", "info"],
                            "description": "Filter by severity level. Default 'all' returns everything."
                        },
                        "section_filter": {
                            "type": "string",
                            "enum": ["all", "command_center", "autonomous", "research"],
                            "description": "Filter by platform section. Default 'all'."
                        },
                        "max_items": {
                            "type": "integer",
                            "description": "Maximum items to return. Default 10.",
                            "default": 10
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_item_details",
                "description": "Get detailed information about a specific attention item by ID. "
                              "Use this when user asks for more details about a specific metric.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "item_id": {
                            "type": "string",
                            "description": "The ID of the attention item (e.g., 'pending_review_backlog')"
                        }
                    },
                    "required": ["item_id"]
                }
            }
        }
    ]

    def execute(self, task: str, context: Dict[str, Any] = None) -> AgentResult:
        """
        Execute a system intelligence query.

        Args:
            task: The user's question about system status/health
            context: Optional additional context

        Returns:
            AgentResult with system status information
        """
        start_time = __import__('time').time()
        context = context or {}

        try:
            # Get attention items
            from core.services.system_state_aggregator import get_system_state_aggregator

            aggregator = get_system_state_aggregator()
            items = aggregator.get_attention_items(max_per_section=10, force_refresh=True)

            # Build rich context for LLM
            items_context = self._format_items_for_llm(items)

            # Build messages for GPT
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"User question: {task}\n\nCurrent system attention items:\n{items_context}"}
            ]

            # Call GPT to interpret and respond
            from openai import OpenAI
            client = OpenAI()

            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=messages,
                max_completion_tokens=2000
            )

            result_text = response.choices[0].message.content

            execution_time = __import__('time').time() - start_time

            return AgentResult(
                success=True,
                result=result_text,
                metadata={
                    'agent': self.name,
                    'items_count': len(items),
                    'critical_count': len([i for i in items if i.severity == 'critical']),
                    'warning_count': len([i for i in items if i.severity == 'warning']),
                    'execution_time': execution_time
                }
            )

        except Exception as e:
            logger.error(f"SystemIntelligenceAgent error: {e}", exc_info=True)
            return AgentResult(
                success=False,
                result=f"Error checking system status: {str(e)}",
                error=str(e),
                metadata={'agent': self.name}
            )

    def _format_items_for_llm(self, items: List) -> str:
        """Format attention items as rich context for the LLM."""
        if not items:
            return "No attention items currently. The system is healthy."

        # Group by severity
        critical = [i for i in items if i.severity == 'critical']
        warnings = [i for i in items if i.severity == 'warning']
        info = [i for i in items if i.severity == 'info']

        parts = []

        if critical:
            parts.append("=== CRITICAL (Immediate Attention) ===")
            for item in critical:
                parts.append(item.to_rich_context())
                parts.append("")

        if warnings:
            parts.append("=== WARNINGS (Should Address) ===")
            for item in warnings:
                parts.append(item.to_rich_context())
                parts.append("")

        if info:
            parts.append("=== INFORMATIONAL (Normal Operations) ===")
            for item in info:
                parts.append(item.to_rich_context())
                parts.append("")

        return "\n".join(parts)

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Handle tool calls from the LLM.

        Args:
            tool_name: Name of the tool being called
            arguments: Tool arguments

        Returns:
            Tool result
        """
        if tool_name == "get_system_attention":
            return self._tool_get_system_attention(arguments)
        elif tool_name == "get_item_details":
            return self._tool_get_item_details(arguments)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def _tool_get_system_attention(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get current system attention items."""
        try:
            from core.services.system_state_aggregator import get_system_state_aggregator

            aggregator = get_system_state_aggregator()
            items = aggregator.get_attention_items(
                max_per_section=arguments.get('max_items', 10) // 3,
                force_refresh=True
            )

            # Apply filters
            severity_filter = arguments.get('severity_filter', 'all')
            section_filter = arguments.get('section_filter', 'all')

            if severity_filter != 'all':
                items = [i for i in items if i.severity == severity_filter]
            if section_filter != 'all':
                items = [i for i in items if i.section == section_filter]

            # Limit
            max_items = arguments.get('max_items', 10)
            items = items[:max_items]

            return {
                'success': True,
                'total_items': len(items),
                'items': [i.to_dict() for i in items],
                'summary': {
                    'critical': len([i for i in items if i.severity == 'critical']),
                    'warning': len([i for i in items if i.severity == 'warning']),
                    'info': len([i for i in items if i.severity == 'info'])
                }
            }

        except Exception as e:
            logger.error(f"Error in get_system_attention: {e}")
            return {'success': False, 'error': str(e)}

    def _tool_get_item_details(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get details for a specific attention item."""
        try:
            item_id = arguments.get('item_id')
            if not item_id:
                return {'success': False, 'error': 'item_id is required'}

            from core.services.system_state_aggregator import get_system_state_aggregator

            aggregator = get_system_state_aggregator()
            items = aggregator.get_attention_items(force_refresh=True)

            for item in items:
                if item.id == item_id:
                    return {
                        'success': True,
                        'item': item.to_dict(),
                        'rich_context': item.to_rich_context()
                    }

            return {'success': False, 'error': f'Item not found: {item_id}'}

        except Exception as e:
            logger.error(f"Error in get_item_details: {e}")
            return {'success': False, 'error': str(e)}
