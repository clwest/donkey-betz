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

Your job: Operational planning, sprint planning, and risk analysis.
READ-ONLY mode - analyze and plan, do NOT execute.

Planning areas:
- Roadmap analysis: Timeline and priorities
- Sprint planning: Work breakdown, capacity
- Risk assessment: Blockers, dependencies, risks

You CANNOT execute changes - only analyze and recommend."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "analyze_roadmap",
                "description": "Analyze project roadmap and provide recommendations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "scope": {
                            "type": "string",
                            "description": "Scope of analysis",
                            "enum": ["project", "feature", "platform"]
                        },
                        "timeframe": {
                            "type": "string",
                            "description": "Timeframe to analyze",
                            "enum": ["week", "month", "quarter"]
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "plan_sprint",
                "description": "Plan a development sprint",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sprint_name": {
                            "type": "string",
                            "description": "Name or number of the sprint"
                        },
                        "duration_days": {
                            "type": "integer",
                            "description": "Sprint duration in days",
                            "default": 14
                        },
                        "focus_area": {
                            "type": "string",
                            "description": "Main focus area for the sprint"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "assess_risks",
                "description": "Identify and assess project risks",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "area": {
                            "type": "string",
                            "description": "Area to assess",
                            "enum": ["technical", "timeline", "resources", "dependencies", "all"]
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
        """Execute a COO tool call."""
        if tool_name == "analyze_roadmap":
            return self._analyze_roadmap(
                scope=arguments.get('scope', 'project'),
                timeframe=arguments.get('timeframe', 'month')
            )

        elif tool_name == "plan_sprint":
            return self._plan_sprint(
                sprint_name=arguments.get('sprint_name', 'Next Sprint'),
                duration_days=arguments.get('duration_days', 14),
                focus_area=arguments.get('focus_area', 'General')
            )

        elif tool_name == "assess_risks":
            return self._assess_risks(
                area=arguments.get('area', 'all')
            )

        return super()._execute_tool_call(tool_name, arguments)

    def _analyze_roadmap(self, scope: str, timeframe: str) -> Dict[str, Any]:
        """Analyze project roadmap."""
        logger.info(f"Analyzing roadmap: scope={scope}, timeframe={timeframe}")

        analysis = {
            'scope': scope,
            'timeframe': timeframe,
            'priorities': [
                {'priority': 1, 'item': 'Complete current phase', 'status': 'in_progress'},
                {'priority': 2, 'item': 'Testing and validation', 'status': 'pending'},
                {'priority': 3, 'item': 'Documentation updates', 'status': 'pending'}
            ],
            'recommendations': [
                'Focus on completing in-progress work',
                'Plan for testing phase',
                'Schedule documentation updates'
            ]
        }

        return {
            'success': True,
            'analysis': analysis
        }

    def _plan_sprint(
        self,
        sprint_name: str,
        duration_days: int,
        focus_area: str
    ) -> Dict[str, Any]:
        """Plan a development sprint."""
        logger.info(f"Planning sprint: {sprint_name}")

        plan = {
            'sprint_name': sprint_name,
            'duration_days': duration_days,
            'focus_area': focus_area,
            'suggested_tasks': [
                {'task': f'Complete {focus_area} implementation', 'estimate': 'medium'},
                {'task': f'Write tests for {focus_area}', 'estimate': 'small'},
                {'task': 'Code review and refinement', 'estimate': 'small'},
                {'task': 'Documentation', 'estimate': 'small'}
            ],
            'capacity_notes': 'Adjust based on team availability',
            'notes': 'This is a read-only plan - no execution'
        }

        return {
            'success': True,
            'plan': plan
        }

    def _assess_risks(self, area: str) -> Dict[str, Any]:
        """Assess project risks."""
        logger.info(f"Assessing risks in area: {area}")

        risks = {
            'area': area,
            'identified_risks': [
                {'risk': 'Scope creep', 'severity': 'medium', 'mitigation': 'Clear requirements definition'},
                {'risk': 'Technical debt', 'severity': 'low', 'mitigation': 'Regular refactoring'},
                {'risk': 'Resource constraints', 'severity': 'low', 'mitigation': 'Realistic planning'}
            ],
            'overall_risk_level': 'low',
            'recommendations': [
                'Continue monitoring progress',
                'Address technical debt incrementally',
                'Maintain clear communication'
            ]
        }

        return {
            'success': True,
            'assessment': risks
        }

    def _validate_task(self, task: str) -> bool:
        """Validate the task is appropriate for COO analysis."""
        return bool(task and task.strip())
