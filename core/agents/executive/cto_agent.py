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

Your job: Technical analysis, planning, and architectural guidance.
READ-ONLY mode - analyze and plan, do NOT execute.

Analysis areas:
- Feature analysis: Requirements, complexity estimate
- Architecture review: Design evaluation, improvements
- Implementation planning: Step-by-step plans
- Risk assessment: Risks and mitigations

You CANNOT execute code or make changes - only analyze and plan."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "analyze_feature",
                "description": "Analyze a feature request and provide technical assessment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "feature_description": {
                            "type": "string",
                            "description": "Description of the feature to analyze"
                        },
                        "scope": {
                            "type": "string",
                            "description": "Scope of analysis",
                            "enum": ["quick", "detailed", "comprehensive"],
                            "default": "detailed"
                        }
                    },
                    "required": ["feature_description"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "plan_implementation",
                "description": "Create an implementation plan for a feature or change",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "feature": {
                            "type": "string",
                            "description": "Feature to plan"
                        },
                        "approach": {
                            "type": "string",
                            "description": "Implementation approach",
                            "enum": ["incremental", "big_bang", "parallel"]
                        }
                    },
                    "required": ["feature"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "review_architecture",
                "description": "Review system architecture and provide recommendations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "area": {
                            "type": "string",
                            "description": "Area to review",
                            "enum": ["agents", "database", "api", "frontend", "infrastructure", "overall"]
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
        """Execute a CTO tool call."""
        if tool_name == "analyze_feature":
            return self._analyze_feature(
                feature_description=arguments.get('feature_description', ''),
                scope=arguments.get('scope', 'detailed')
            )

        elif tool_name == "plan_implementation":
            return self._plan_implementation(
                feature=arguments.get('feature', ''),
                approach=arguments.get('approach', 'incremental')
            )

        elif tool_name == "review_architecture":
            return self._review_architecture(
                area=arguments.get('area', 'overall')
            )

        return super()._execute_tool_call(tool_name, arguments)

    def _analyze_feature(
        self,
        feature_description: str,
        scope: str
    ) -> Dict[str, Any]:
        """Analyze a feature request."""
        logger.info(f"Analyzing feature: {feature_description[:50]}")

        # Provide structured analysis
        analysis = {
            'feature': feature_description,
            'scope': scope,
            'complexity': 'medium',  # Would be computed in full implementation
            'estimated_effort': 'TBD',
            'dependencies': [],
            'risks': [],
            'recommendations': [
                'Break into smaller tasks',
                'Create unit tests first',
                'Review with team before implementation'
            ]
        }

        return {
            'success': True,
            'analysis': analysis
        }

    def _plan_implementation(
        self,
        feature: str,
        approach: str
    ) -> Dict[str, Any]:
        """Create an implementation plan."""
        logger.info(f"Planning implementation for: {feature[:50]}")

        plan = {
            'feature': feature,
            'approach': approach,
            'phases': [
                {'phase': 1, 'name': 'Research & Design', 'tasks': ['Analyze requirements', 'Design architecture']},
                {'phase': 2, 'name': 'Implementation', 'tasks': ['Build core functionality', 'Write tests']},
                {'phase': 3, 'name': 'Integration', 'tasks': ['Integrate with existing code', 'End-to-end testing']},
                {'phase': 4, 'name': 'Deployment', 'tasks': ['Deploy to staging', 'Monitor & iterate']}
            ],
            'notes': 'This is a read-only plan - no execution'
        }

        return {
            'success': True,
            'plan': plan
        }

    def _review_architecture(self, area: str) -> Dict[str, Any]:
        """Review system architecture."""
        logger.info(f"Reviewing architecture area: {area}")

        review = {
            'area': area,
            'status': 'reviewed',
            'strengths': [
                'Clean separation of concerns',
                'Well-defined agent boundaries',
                'Good use of composition'
            ],
            'improvements': [
                'Consider adding caching layer',
                'Document API contracts',
                'Add integration tests'
            ],
            'recommendations': [
                'Continue with incremental refactoring',
                'Prioritize test coverage',
                'Document architectural decisions'
            ]
        }

        return {
            'success': True,
            'review': review
        }

    def _validate_task(self, task: str) -> bool:
        """Validate the task is appropriate for CTO analysis."""
        return bool(task and task.strip())
