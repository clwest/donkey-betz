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

import json
import logging
from typing import Dict, Any, List

from core.agents.base_agent import BaseAgent, AgentResult, strip_simulated_tool_json
from ml.auto_selection import TaskType
from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51

logger = logging.getLogger(__name__)


def analyze_system_health_with_ml(health_data: dict) -> dict:
    """Analyze system health data using ML models (ANOMALY for detecting issues)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=health_data,
            task_hint=TaskType.ANOMALY,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'anomaly'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'health_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML system health analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


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
    requires_system_context = True  # Session 820: Inject CLAUDE.md + critical docs

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

    def execute(
        self,
        task: str,
        context: Dict[str, Any] = None,
        scifi_context: Dict[str, Any] = None,
        spider_context: Dict[str, Any] = None
    ) -> AgentResult:
        """
        Execute a system intelligence query.

        Args:
            task: The user's question about system status/health
            context: Optional additional context
            scifi_context: Sci-fi feature context (unused by this agent)
            spider_context: Spider data context (unused by this agent)

        Returns:
            AgentResult with system status information
        """
        import time
        start_time = time.time()
        context = context or {}

        # Session 663: Use time travel session for decision tracking
        with self.time_travel_session("system_intelligence", task, input_data=context):
            try:
                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing system status request",
                    reasoning=f"Received system query: {task[:100]}",
                    confidence=0.9
                )

                # Get attention items
                from core.services.system_state_aggregator import get_system_state_aggregator

                aggregator = get_system_state_aggregator()
                items = aggregator.get_attention_items(max_per_section=10, force_refresh=True)

                self.record_decision(
                    decision_type="data_retrieval",
                    action=f"Retrieved {len(items)} attention items",
                    reasoning="Queried SystemStateAggregator for platform health data",
                    confidence=0.95
                )

                # Build rich context for LLM
                items_context = self._format_items_for_llm(items)

                # Session 819: Use intelligent prompting for full context
                intelligent_prompt = self._build_intelligent_prompt(
                    task=task,
                    scifi_context=scifi_context or {},
                    spider_context=spider_context or {},
                    additional_context=f"\n\n## Current System Attention Items\n{items_context}"
                )

                # Build messages for GPT
                messages = [
                    {"role": "system", "content": intelligent_prompt},
                    {"role": "user", "content": f"User question: {task}"}
                ]

                # Session 761: Call GPT with tools enabled for LLM-driven tool use
                client = get_openai_client()

                tool_calls_made = []
                # Session 919: Increase max_completion_tokens for GPT-5-mini
                # Reasoning models need more headroom for reasoning_tokens
                response = client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=messages,
                    tools=self.get_tools_with_delegation(),
                    tool_choice="auto",
                    max_completion_tokens=4000
                )

                assistant_message = response.choices[0].message

                # Session 761: Handle tool calls if LLM requests them
                if assistant_message.tool_calls:
                    # Session 919: Build assistant message for tool calls
                    # When tool_calls are present, content is typically None
                    # Some models require content to be omitted or empty string
                    assistant_msg = {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                            }
                            for tc in assistant_message.tool_calls
                        ]
                    }
                    # Only include content if it's not None (per OpenAI API spec)
                    if assistant_message.content is not None:
                        assistant_msg["content"] = assistant_message.content
                    messages.append(assistant_msg)

                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"LLM requested tool: {tool_name}",
                            reasoning=f"Tool args: {json.dumps(tool_args)[:100]}",
                            confidence=0.9
                        )

                        tool_result = self._execute_tool_call(tool_name, tool_args)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': tool_args,
                            'result_summary': str(tool_result)[:200]
                        })

                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(tool_result)[:8000]
                        })

                    # Get final synthesis from LLM after tool execution
                    # Session 919: Increase max_completion_tokens for GPT-5-mini reasoning model
                    # Reasoning tokens consume part of the budget, so we need more headroom
                    final_response = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=messages,
                        max_completion_tokens=4000
                    )
                    result_text = final_response.choices[0].message.content

                    # Session 919: Log if content is empty for debugging
                    if not result_text:
                        logger.warning(
                            f"GPT-5-mini returned empty content after tool calls. "
                            f"Usage: {final_response.usage}"
                        )
                        # Fallback: Generate report from tool results directly
                        result_text = self._generate_fallback_report(items, tool_calls_made)
                else:
                    result_text = strip_simulated_tool_json(assistant_message.content)
                execution_time_ms = int((time.time() - start_time) * 1000)

                # Count by SIA-reclassified severity (not raw aggregator severity)
                sia_severities = [self._classify_severity(i) for i in items]
                critical_count = sia_severities.count('critical')
                warning_count = sia_severities.count('warning')
                info_count = sia_severities.count('info')

                self.mark_decision_outcome(
                    success=True,
                    result_summary=f"Reported {critical_count} critical, {warning_count} warnings, {info_count} info items"
                )

                result = AgentResult(
                    success=True,
                    message=result_text,
                    data={
                        'items_count': len(items),
                        'critical_count': critical_count,
                        'warning_count': warning_count,
                        'info_count': info_count,
                        'execution_time': execution_time_ms / 1000,
                        'result_preview': result_text[:2000],
                    },
                    agent_name=self.name,
                    execution_time_ms=execution_time_ms,
                    decisions_made=self._tt_decision_count,
                    tool_calls=tool_calls_made  # Session 761: Track tool usage
                )

                # Save report to Deliverables (DB-based, works on Railway)
                # This replaces filesystem workspace writes which fail on Railway
                self._save_to_deliverable(
                    title=f"System Intelligence Report: {task[:80]}",
                    content=result_text,
                    deliverable_type='document',
                    category='System Reports',
                    tags=['system_intelligence', 'health_report', 'automated'],
                    metadata={
                        'critical_count': critical_count,
                        'warning_count': warning_count,
                        'info_count': info_count,
                        'items_count': len(items),
                        'task': task,
                    },
                )

                # Escalate warning/critical items to HumanAttentionItem queue
                escalation_stats = self._escalate_to_attention_items(items)
                if escalation_stats:
                    result.data['escalation'] = escalation_stats

                # === Session 663: Learning Infrastructure Integration ===
                # Record learning outcome for XP and pattern detection
                self._record_learning_outcome(
                    result=result,
                    task=task,
                    context=context,
                    spider_data_used=False,  # Uses SystemStateAggregator, not spiders
                    scifi_context_used=False
                )

                # Create memory of successful system check
                self._create_execution_memory(
                    result=result,
                    task=task,
                    memory_type="success",
                    importance=0.5  # System checks are routine
                )

                # Share knowledge if there are critical issues (valuable insight)
                if critical_count > 0:
                    critical_titles = [
                        i.title for i, s in zip(items, sia_severities)
                        if s == 'critical'
                    ][:5]
                    self._share_knowledge(
                        knowledge_type='observation',
                        title=f"System Alert: {critical_count} critical items",
                        knowledge_value={
                            'query': task,
                            'critical_count': critical_count,
                            'warning_count': warning_count,
                            'critical_items': critical_titles,
                            'timestamp': time.time()
                        },
                        confidence=0.9
                    )

                return result

            except Exception as e:
                logger.error(f"SystemIntelligenceAgent error: {e}", exc_info=True)
                execution_time_ms = int((time.time() - start_time) * 1000)

                result = AgentResult(
                    success=False,
                    message=f"Error checking system status: {str(e)}",
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=execution_time_ms
                )

                # Record failure for learning
                self._record_learning_outcome(
                    result=result,
                    task=task,
                    context=context,
                    spider_data_used=False,
                    scifi_context_used=False
                )

                # Create failure memory for pattern detection
                self._create_execution_memory(
                    result=result,
                    task=task,
                    memory_type="failure",
                    importance=0.7  # Failures are important to remember
                )

                return result

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

    def _generate_fallback_report(self, items: List, tool_calls_made: List[Dict]) -> str:
        """
        Session 919: Generate a fallback report when GPT-5-mini returns empty content.
        This ensures we always return useful information even if the LLM fails.
        """
        # Count by severity
        critical = [i for i in items if i.severity == 'critical']
        warnings = [i for i in items if i.severity == 'warning']
        info = [i for i in items if i.severity == 'info']

        parts = ["## System Status Report\n"]

        # Summary
        parts.append(f"**Overview:** {len(critical)} critical, {len(warnings)} warnings, {len(info)} informational items\n")

        if critical:
            parts.append("### Critical Items (Immediate Attention)")
            for item in critical:
                parts.append(f"- **{item.title}**: {item.summary}")
                if item.recommended_action:
                    parts.append(f"  - Action: {item.recommended_action}")
            parts.append("")

        if warnings:
            parts.append("### Warnings (Should Address)")
            for item in warnings:
                parts.append(f"- **{item.title}**: {item.summary}")
            parts.append("")

        if info:
            parts.append("### Informational")
            for item in info[:5]:  # Limit info items
                parts.append(f"- **{item.title}**: {item.summary}")
            if len(info) > 5:
                parts.append(f"- ...and {len(info) - 5} more informational items")
            parts.append("")

        # Health assessment
        if not critical and not warnings:
            parts.append("**Overall Health:** The system is healthy with no critical issues or warnings.")
        elif not critical:
            parts.append("**Overall Health:** No critical issues. Address warnings when convenient.")
        else:
            parts.append("**Overall Health:** Critical issues detected. Please address them promptly.")

        return "\n".join(parts)

    def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 761: Execute tool calls for system intelligence.

        Renamed from handle_tool_call for BaseAgent compatibility.

        Tools:
        - get_system_attention: Get all current system attention items
        - get_item_details: Get detailed information about a specific attention item
        """
        # Session 744: Handle delegation tool
        if tool_name == "get_system_attention":
            return self._tool_get_system_attention(arguments)
        elif tool_name == "get_item_details":
            return self._tool_get_item_details(arguments)
        # Session 1002C: Fall through to BaseAgent for web_search, spider_query, delegation
        return super()._execute_tool_call(tool_name, arguments)

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

    # ── Key spiders whose staleness warrants escalation ──────────────────
    _KEY_SPIDERS = frozenset({
        'theodds', 'polygon_finance', 'newsapi', 'etherscan_api', 'coingecko',
    })

    @staticmethod
    def _classify_severity(item) -> str:
        """
        Re-classify item severity for escalation purposes.

        The SystemStateAggregator marks most items as 'info'. SIA applies
        its own rules to decide which deserve warning/critical status.
        """
        title_lower = item.title.lower() if item.title else ''
        category_lower = item.category.lower() if item.category else ''
        # Spider names appear in summary, not title (e.g. "No data in 24h: coingecko")
        searchable = f"{title_lower} {(item.summary or '').lower()}"

        # Stale spiders → warning (key spiders → critical)
        if 'stale' in category_lower and 'spider' in title_lower:
            return 'critical' if any(
                s in searchable for s in (
                    'theodds', 'polygon_finance', 'newsapi',
                    'etherscan_api', 'coingecko',
                )
            ) else 'warning'

        # Stale signal clusters (large count) → warning
        if 'stale' in category_lower and 'signal' in title_lower:
            # Extract count from title like "Stale Signal Clusters: 80"
            import re
            m = re.search(r'(\d+)', item.title or '')
            count = int(m.group(1)) if m else 0
            if count >= 50:
                return 'critical'
            if count >= 10:
                return 'warning'

        # Smoke suite failures → warning (multiple → critical)
        if 'smoke' in title_lower and ('fail' in title_lower or 'failing' in title_lower):
            return 'warning'

        # Deploy drift → critical
        if 'deploy' in title_lower and 'drift' in title_lower:
            return 'critical'

        # Keep original severity
        return item.severity

    def _escalate_to_attention_items(self, items) -> Dict[str, Any]:
        """
        Upsert HumanAttentionItems for warning/critical findings.

        Uses deterministic source_id (sia:<item.id>) so repeated SIA runs
        update existing items instead of creating duplicates.  Items that
        were previously escalated but are no longer in the findings list
        get auto-resolved.
        """
        try:
            from core.services.human_interface_service import get_human_interface_service

            user = self.user
            if not user:
                logger.debug("SIA escalation skipped — no user on agent")
                return {}

            service = get_human_interface_service(user)

            created, updated, resolved = 0, 0, 0
            item_ids_seen = []

            for item in items:
                effective_severity = self._classify_severity(item)
                if effective_severity not in ('critical', 'warning'):
                    continue

                source_id = f"sia:{item.id}"
                item_ids_seen.append(source_id)

                urgency = 'critical' if effective_severity == 'critical' else 'medium'
                # Promote key-spider staleness (only elevate, never downgrade)
                if urgency != 'critical' and 'stale' in (item.category or '').lower():
                    searchable = f"{(item.title or '').lower()} {(item.summary or '').lower()}"
                    for spider in self._KEY_SPIDERS:
                        if spider in searchable:
                            urgency = 'high'
                            break

                result = service.create_attention_item(
                    source_type='system_intelligence',
                    source_id=source_id,
                    source_agent=self.name,
                    item_type='alert',
                    title=f"[SIA] {item.title[:180]}",
                    summary=item.summary or item.explanation or item.title,
                    urgency=urgency,
                    payload={
                        'sia_category': item.category,
                        'sia_section': item.section,
                        'sia_priority': item.priority,
                        'recommended_action': item.recommended_action,
                        'action_url': item.action_url,
                        'location': item.location,
                    },
                    deduplicate=True,
                )

                if result.get('deduplicated'):
                    updated += 1
                else:
                    created += 1

            # Auto-resolve previously escalated items that are no longer flagged
            # Policy: warning items auto-resolve; critical items get deferred
            # for human sign-off (too important to silently dismiss)
            from core.models_human_interface import HumanAttentionItem

            stale_items = HumanAttentionItem.objects.filter(
                user=user,
                source_type='system_intelligence',
                source_agent=self.name,
                status__in=['pending', 'viewed'],
            ).exclude(
                source_id__in=item_ids_seen,
            )

            deferred = 0
            for stale in stale_items:
                if stale.urgency == 'critical':
                    # Critical items need human confirmation before closing
                    stale.status = 'deferred'
                    stale.decision_feedback = (
                        'SIA: issue no longer detected — pending human confirmation '
                        'to close (critical items require sign-off)'
                    )
                    stale.save(update_fields=['status', 'decision_feedback'])
                    deferred += 1
                else:
                    # Warning/medium/low items auto-resolve
                    stale.status = 'acted'
                    stale.decision = 'approve'
                    stale.decision_feedback = 'Auto-resolved: issue no longer detected by SIA'
                    stale.save(update_fields=['status', 'decision', 'decision_feedback'])
                    resolved += 1

            if created or updated or resolved or deferred:
                logger.info(
                    f"[SIA] Escalation: {created} created, {updated} deduped, "
                    f"{resolved} auto-resolved, {deferred} deferred-for-review"
                )

            return {
                'created': created,
                'updated': updated,
                'resolved': resolved,
                'deferred_for_review': deferred,
                'total_escalated': created + updated,
            }

        except Exception as e:
            logger.warning(f"[SIA] Escalation failed: {e}")
            return {'error': str(e)}
