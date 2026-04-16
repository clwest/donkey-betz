"""
CTO Agent - Clean Architecture
===============================

Session 280: Phase 2 - Agent Architecture Unification

The CTO Agent provides technical analysis and planning capabilities.
Phase 1 is READ-ONLY - it provides analysis and plans but does not execute changes.

Tools Available:
    - analyze_feature: Analyze a feature request
    - plan_implementation: Create an implementation plan
    - review_architecture: Review system architecture

Usage:
    from core.agents.executive import CTOAgent

    agent = CTOAgent(user=request.user)
    result = agent.execute(
        task="Analyze the authentication system",
        context={},
        scifi_context={},
        spider_context={}
    )
"""

import logging
import time
from typing import Dict, Any

from core.agents.base_agent import BaseAgent, AgentResult
from core.agents.report_schemas import build_provenance, format_disclaimer
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_tech_with_ml(tech_data: dict) -> dict:
    """Analyze technical requirements using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=tech_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'tech_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML tech analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class CTOAgent(BaseAgent):
    """
    CTO Agent - Technical Planning and Analysis (Read-Only).

    This agent:
    1. Analyzes feature requests
    2. Creates implementation plans
    3. Reviews architecture decisions

    It CANNOT:
    - Write or modify code
    - Execute file operations
    - Make destructive changes
    """

    name = "CTOAgent"
    llm_timeout = 180.0  # Session 1074: Architecture blueprints need 3 min
    requires_system_context = True  # Session 820: Inject CLAUDE.md + critical docs

    system_prompt = """You are CTOAgent, the Chief Technology Officer AI assistant.

IMPORTANT - Response Guidelines:
- Be CONCISE. Executives need decisions, not dissertations.
- For questions: Direct answer in 2-3 sentences, then brief supporting points.
- For analysis: Bullet points, not paragraphs. Max 5-7 key points.
- Skip obvious context - assume the reader knows the basics.
- EVERY factual claim MUST be backed by tool data. Never invent stats.

Your job: Technical analysis, planning, and architectural guidance.
READ-ONLY mode - analyze and plan, do NOT execute.

You have REAL-TIME platform tools:
- get_platform_snapshot: Full system status (agents, SLOs, governor, costs, spiders, content, failures)
- get_agent_health: Real execution stats for specific agents
- get_cost_breakdown: Actual LLM spend by agent and model
- get_failure_analysis: Real error patterns and failure signatures

CRITICAL RULE: Always call get_platform_snapshot FIRST before making any claims
about system state. Your analysis must cite the evidence returned by your tools.
If a tool returns no data for a topic, say "no data available" — do NOT fabricate.

You CANNOT execute code or make changes - only analyze and plan."""

    # Session 1089: Tools backed by PlatformContextService — real data, not stubs.
    # Initiative: "Agent Data Grounding: Facts Not Fiction" (111b5af1)
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_platform_snapshot",
                "description": (
                    "Get a comprehensive, REAL-TIME platform snapshot with evidence. "
                    "Returns: agent execution stats, SLO status, governor state, "
                    "initiative progress, LLM costs, spider health, content pipeline, "
                    "and failure signatures. ALL data is queried live from the database."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "hours_back": {
                            "type": "integer",
                            "description": "Time window in hours (default 24)",
                            "default": 24
                        },
                        "modules": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "Which modules to include. Options: agent_exec, slo, governor, "
                                "work, cost, spiders, content, failures. Default: all."
                            )
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_agent_health",
                "description": (
                    "Get real execution stats for specific agents — success rates, "
                    "failure counts, top errors. Use this when analyzing agent performance."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific agents to check (null = all agents)"
                        },
                        "hours_back": {
                            "type": "integer",
                            "description": "Time window in hours (default 24)",
                            "default": 24
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_cost_breakdown",
                "description": (
                    "Get real LLM spend data — total cost, cost by agent, cost by model, "
                    "token usage. Use this for budget and cost analysis."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "hours_back": {
                            "type": "integer",
                            "description": "Time window in hours (default 24)",
                            "default": 24
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_failure_analysis",
                "description": (
                    "Get real failure patterns — agent failures, LLM errors, timeout agents, "
                    "error signatures. Use this for reliability and incident analysis."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "hours_back": {
                            "type": "integer",
                            "description": "Time window in hours (default 24)",
                            "default": 24
                        }
                    },
                    "required": []
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
        """Execute technical analysis based on the task."""
        start_time = time.time()
        tool_calls_made = []

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence")

        with self.time_travel_session("cto_analysis", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing technical request",
                    reasoning=f"Received task: {task[:100]}",
                    alternatives=["delegate_to_coo", "request_more_info"],
                    confidence=0.9
                )

                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                logger.info(f"CTOAgent executing: {task[:50]}...")

                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Technical analysis: {arguments}",
                            alternatives=[],
                            confidence=0.95
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                    execution_time = int((time.time() - start_time) * 1000)

                    # Session 954: Build provenance for technical analysis
                    from datetime import timezone
                    provenance_sources = [{
                        'name': 'TechnicalAnalysis',
                        'endpoint': 'cto/analysis',
                        'retrieved_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                        'record_count': len(tool_calls_made),
                    }]
                    if spider_context:
                        provenance_sources.append({
                            'name': 'SpiderNetwork',
                            'endpoint': 'spider/context',
                            'retrieved_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                            'record_count': 1,
                        })
                    provenance = build_provenance(
                        report_type='technical_analysis',
                        agent_name=self.name,
                        sources=provenance_sources,
                        stale_threshold_hours=24.0,
                    )
                    provenance.disclaimer = "Technical analysis and recommendations. Verify with engineering team before implementation."

                    # Session 1200: Synthesize tool results into real analysis
                    tool_results_list = [tc.get('result', {}) for tc in tool_calls_made]
                    synthesis = self._synthesize_tool_results(tool_calls_made, tool_results_list, task)
                    analysis_msg = synthesis if synthesis else "Technical analysis completed"

                    result = AgentResult(
                        success=True,
                        message=analysis_msg,
                        data={
                            'task': task,
                            'tool_results': tool_calls_made,
                            'content': synthesis,
                            # Session 954: Add provenance
                            'provenance': provenance.to_dict(),
                            'publishable': provenance.publishable,
                            'validation_status': provenance.validation_status,
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )

                    # Session 1006: Persist output to Deliverable
                    self._save_to_deliverable(
                        title=f"CTO Analysis: {task[:80]}",
                        content=analysis_msg,
                        deliverable_type='analysis',
                        category='Executive Technical',
                        tags=['cto', 'technical'],
                        metadata={'task': task[:200]},
                    )

                    # Session 380: Learning hooks for collective intelligence
                    self._record_learning_outcome(
                        result=result,
                        task=task,
                        context=context,
                        spider_data_used=bool(spider_context),
                        scifi_context_used=bool(scifi_context)
                    )
                    self._create_execution_memory(
                        result=result,
                        task=task,
                        memory_type="success",
                        importance=0.7
                    )

                    return result

                else:
                    result = AgentResult(
                        success=True,
                        message=gpt_response.get('content', ''),
                        data={'type': 'conversation'},
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000)
                    )

                    # Session 380: Learning hooks for collective intelligence
                    self._record_learning_outcome(
                        result=result,
                        task=task,
                        context=context,
                        spider_data_used=bool(spider_context),
                        scifi_context_used=bool(scifi_context)
                    )
                    self._create_execution_memory(
                        result=result,
                        task=task,
                        memory_type="success",
                        importance=0.6
                    )

                    return result

            except Exception as e:
                logger.error(f"CTOAgent error: {e}")
                result = AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

                # Session 380: Learning hooks for collective intelligence (failures too)
                self._record_learning_outcome(
                    result=result,
                    task=task,
                    context=context,
                    spider_data_used=bool(spider_context),
                    scifi_context_used=bool(scifi_context)
                )
                self._create_execution_memory(
                    result=result,
                    task=task,
                    memory_type="failure",
                    importance=0.8
                )

                return result

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a CTO tool call — all backed by PlatformContextService."""
        from core.services.platform_context_service import PlatformContextService
        pcs = PlatformContextService()

        if tool_name == "get_platform_snapshot":
            return self._get_platform_snapshot(pcs, arguments)
        elif tool_name == "get_agent_health":
            return self._get_agent_health(pcs, arguments)
        elif tool_name == "get_cost_breakdown":
            return self._get_cost_breakdown(pcs, arguments)
        elif tool_name == "get_failure_analysis":
            return self._get_failure_analysis(pcs, arguments)

        return super()._execute_tool_call(tool_name, arguments)

    def _get_platform_snapshot(self, pcs, arguments: Dict) -> Dict:
        """Full platform snapshot — real data from every subsystem."""
        hours_back = arguments.get('hours_back', 24)
        modules = arguments.get('modules')
        logger.info(f"CTOAgent: platform snapshot ({hours_back}h, modules={modules or 'all'})")

        result = pcs.snapshot(hours_back=hours_back, modules=modules)
        return {
            'success': True,
            'snapshot': result['facts'],
            'evidence_count': len(result['evidence']),
            'evidence': result['evidence'],
            'warnings': result['warnings'],
        }

    def _get_agent_health(self, pcs, arguments: Dict) -> Dict:
        """Agent execution stats — real success rates and failure patterns."""
        hours_back = arguments.get('hours_back', 24)
        agent_names = arguments.get('agent_names')
        logger.info(f"CTOAgent: agent health ({hours_back}h, agents={agent_names or 'all'})")

        result = pcs.agent_execution_stats(
            hours_back=hours_back,
            agent_names=agent_names,
        )
        return {
            'success': True,
            'agent_stats': result['facts'],
            'evidence': result['evidence'],
        }

    def _get_cost_breakdown(self, pcs, arguments: Dict) -> Dict:
        """LLM cost analysis — real spend data."""
        hours_back = arguments.get('hours_back', 24)
        logger.info(f"CTOAgent: cost breakdown ({hours_back}h)")

        result = pcs.cost_metrics(hours_back=hours_back)
        return {
            'success': True,
            'costs': result['facts'],
            'evidence': result['evidence'],
        }

    def _get_failure_analysis(self, pcs, arguments: Dict) -> Dict:
        """Failure pattern analysis — real error signatures."""
        hours_back = arguments.get('hours_back', 24)
        logger.info(f"CTOAgent: failure analysis ({hours_back}h)")

        result = pcs.failure_signatures(hours_back=hours_back)
        return {
            'success': True,
            'failures': result['facts'],
            'evidence': result['evidence'],
        }

    def _validate_task(self, task: str) -> bool:
        """Validate the task is appropriate for CTO analysis."""
        return bool(task and task.strip())
