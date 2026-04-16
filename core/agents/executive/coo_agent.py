"""
COO Agent - Clean Architecture
===============================

Session 280: Phase 2 - Agent Architecture Unification

The COO Agent provides operational planning and risk analysis.
Phase 1 is READ-ONLY - it provides analysis and plans but does not execute.

Tools Available:
    - analyze_roadmap: Analyze project roadmap
    - plan_sprint: Plan a development sprint
    - assess_risks: Identify and assess project risks

Usage:
    from core.agents.executive import COOAgent

    agent = COOAgent(user=request.user)
    result = agent.execute(
        task="Plan the next sprint",
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


def analyze_operations_with_ml(ops_data: dict) -> dict:
    """Analyze operations data using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=ops_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'ops_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML operations analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class COOAgent(BaseAgent):
    """
    COO Agent - Operations Planning and Risk Analysis (Read-Only).

    This agent:
    1. Analyzes project roadmaps
    2. Plans development sprints
    3. Assesses project risks

    It CANNOT:
    - Execute changes
    - Modify schedules automatically
    """

    name = "COOAgent"
    requires_system_context = True  # Session 820: Inject CLAUDE.md + critical docs

    system_prompt = """You are COOAgent, the Chief Operating Officer AI assistant.

IMPORTANT - Response Guidelines:
- Be CONCISE. Operations needs action items, not lengthy reports.
- For questions: Direct answer, then 3-5 bullet point recommendations.
- For planning: Timeline + key milestones only. Skip obvious steps.
- For risks: Top 3 risks with one-line mitigations each.
- EVERY factual claim MUST be backed by tool data. Never invent stats.

Your job: Operational planning, sprint planning, and risk analysis.
READ-ONLY mode - analyze and plan, do NOT execute.

You have REAL-TIME operations tools:
- get_operations_snapshot: Full ops view (initiatives, action items, SLOs, agent health, failures, costs)
- get_work_status: Real initiative progress, action items, blockers
- get_risk_assessment: Real failure patterns, SLO breaches, circuit breakers, cost overruns

CRITICAL RULE: Always call get_operations_snapshot FIRST before making any claims
about operational state. Your analysis must cite the evidence returned by your tools.
If a tool returns no data for a topic, say "no data available" — do NOT fabricate.

You CANNOT execute changes - only analyze and recommend."""

    # Session 1089: Tools backed by PlatformContextService — real data, not stubs.
    # Initiative: "Agent Data Grounding: Facts Not Fiction" (111b5af1)
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_operations_snapshot",
                "description": (
                    "Get a comprehensive, REAL-TIME operations snapshot with evidence. "
                    "Returns: initiative progress, action items, SLO status, agent execution "
                    "stats, failure patterns, LLM costs, spider health, governor state. "
                    "ALL data is queried live from the database."
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
                "name": "get_work_status",
                "description": (
                    "Get real initiative and action item progress — active initiatives, "
                    "blockers, recently completed work, pending action items."
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
                "name": "get_risk_assessment",
                "description": (
                    "Get real operational risks — SLO breaches, failure signatures, "
                    "circuit breakers tripped, cost overruns, agent timeout patterns."
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
        """Execute operational analysis based on the task."""
        start_time = time.time()
        tool_calls_made = []

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence")

        with self.time_travel_session("coo_analysis", task, input_data=context):
            try:
                # Handle simple diagnostic/identification queries
                task_lower = task.lower() if task else ''
                if any(keyword in task_lower for keyword in ['state your name', 'who are you', 'your capability', 'what can you do', 'introduce yourself']):
                    execution_time = int((time.time() - start_time) * 1000)
                    return AgentResult(
                        success=True,
                        message=f"I am {self.name}, the Chief Operating Officer AI assistant. One capability: I plan development sprints with timeline, milestones, task breakdown, and capacity notes to help teams organize their work effectively.",
                        data={'type': 'self_description', 'capabilities': ['roadmap_analysis', 'sprint_planning', 'risk_assessment']},
                        agent_name=self.name,
                        execution_time_ms=execution_time
                    )

                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing operational request",
                    reasoning=f"Received task: {task[:100]}",
                    alternatives=["delegate_to_cto", "request_more_info"],
                    confidence=0.9
                )

                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                logger.info(f"COOAgent executing: {task[:50]}...")

                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Operational analysis: {arguments}",
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

                    # Session 954: Build provenance for operational analysis
                    from datetime import timezone
                    provenance_sources = [{
                        'name': 'OperationalAnalysis',
                        'endpoint': 'coo/analysis',
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
                        report_type='operational_analysis',
                        agent_name=self.name,
                        sources=provenance_sources,
                        stale_threshold_hours=24.0,
                    )
                    provenance.disclaimer = "Operational analysis and planning. Verify timelines and resources with team leads."

                    # Session 1200: Synthesize tool results into real analysis
                    tool_results_list = [tc.get('result', {}) for tc in tool_calls_made]
                    synthesis = self._synthesize_tool_results(tool_calls_made, tool_results_list, task)
                    analysis_msg = synthesis if synthesis else "Operational analysis completed"

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
                        title=f"COO Analysis: {task[:80]}",
                        content=analysis_msg,
                        deliverable_type='analysis',
                        category='Executive Operations',
                        tags=['coo', 'operations'],
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
                logger.error(f"COOAgent error: {e}")
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
        """Execute a COO tool call — all backed by PlatformContextService."""
        from core.services.platform_context_service import PlatformContextService
        pcs = PlatformContextService()

        if tool_name == "get_operations_snapshot":
            return self._get_operations_snapshot(pcs, arguments)
        elif tool_name == "get_work_status":
            return self._get_work_status(pcs, arguments)
        elif tool_name == "get_risk_assessment":
            return self._get_risk_assessment(pcs, arguments)

        return super()._execute_tool_call(tool_name, arguments)

    def _get_operations_snapshot(self, pcs, arguments: Dict) -> Dict:
        """Full operations snapshot — real data from every subsystem."""
        hours_back = arguments.get('hours_back', 24)
        modules = arguments.get('modules')
        logger.info(f"COOAgent: operations snapshot ({hours_back}h)")

        result = pcs.snapshot(hours_back=hours_back, modules=modules)
        return {
            'success': True,
            'snapshot': result['facts'],
            'evidence_count': len(result['evidence']),
            'evidence': result['evidence'],
            'warnings': result['warnings'],
        }

    def _get_work_status(self, pcs, arguments: Dict) -> Dict:
        """Initiative and action item progress — real data."""
        hours_back = arguments.get('hours_back', 24)
        logger.info(f"COOAgent: work status ({hours_back}h)")

        result = pcs.work_progress(hours_back=hours_back)
        return {
            'success': True,
            'work': result['facts'],
            'evidence': result['evidence'],
        }

    def _get_risk_assessment(self, pcs, arguments: Dict) -> Dict:
        """Operational risk assessment from real failure/SLO/governor data."""
        hours_back = arguments.get('hours_back', 24)
        logger.info(f"COOAgent: risk assessment ({hours_back}h)")

        # Combine failure signatures + SLO status + governor state for risk view
        failures = pcs.failure_signatures(hours_back=hours_back)
        slos = pcs.slo_status(hours_back=hours_back)
        governor = pcs.governor_status()
        costs = pcs.cost_metrics(hours_back=hours_back)

        return {
            'success': True,
            'risks': {
                'slo_breaches': slos['facts'].get('breach_details', []),
                'failure_signatures': failures['facts'],
                'circuit_breakers_tripped': governor['facts'].get('circuit_breakers_tripped', []),
                'cost_24h_usd': costs['facts'].get('total_cost_usd', 0),
                'governor_enabled': governor['facts'].get('governor_enabled', False),
            },
            'evidence': (
                failures.get('evidence', []) +
                slos.get('evidence', []) +
                governor.get('evidence', []) +
                costs.get('evidence', [])
            ),
        }

    def _validate_task(self, task: str) -> bool:
        """Validate the task is appropriate for COO analysis."""
        return bool(task and task.strip())
