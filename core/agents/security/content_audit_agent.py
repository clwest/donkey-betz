"""
Content Audit Agent - Clean Architecture
==========================================

Session 295: Bias & Ethics Transparency Agent

This agent provides intelligent content auditing by analyzing prompts
and generated content for bias, safety concerns, and ethical issues.

Tools Available:
    - audit_prompt: Analyze a prompt for bias and safety concerns
    - audit_content: Full audit of generated content
    - get_transparency_card: Generate user-friendly transparency card

Usage:
    from core.agents.security import ContentAuditAgent

    agent = ContentAuditAgent(user=request.user)
    result = agent.execute(
        task="Audit this prompt for bias: 'A beautiful exotic woman'",
        context={},
        scifi_context={},
        spider_context={}
    )
"""

import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_content_safety_with_ml(content_data: dict) -> dict:
    """Analyze content for safety using ML models (Text classification)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=content_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'safety_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML content safety analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


@dataclass
class AuditReport:
    """Result from content audit."""
    success: bool
    prompt: str
    safety_score: int
    bias_detected: bool
    bias_categories: List[str] = field(default_factory=list)
    ethics_flags: List[str] = field(default_factory=list)
    prompt_suggestions: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    model_notes: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'prompt': self.prompt,
            'safety_score': self.safety_score,
            'safety_level': 'high' if self.safety_score >= 80 else
                           'medium' if self.safety_score >= 50 else 'low',
            'bias_detected': self.bias_detected,
            'bias_categories': self.bias_categories,
            'ethics_flags': self.ethics_flags,
            'prompt_suggestions': self.prompt_suggestions,
            'recommendations': self.recommendations,
            'model_notes': self.model_notes,
            'error': self.error,
        }


class ContentAuditAgent(BaseAgent):
    """
    Content Audit Agent - Bias & Ethics Guardian.

    This agent:
    1. Analyzes prompts for potential bias
    2. Flags safety and ethical concerns
    3. Provides transparent model limitation documentation
    4. Suggests prompt improvements

    It CANNOT:
    - Generate images
    - Execute workflows
    """

    name = "ContentAuditAgent"

    system_prompt = """You are ContentAuditAgent, the Bias & Ethics Guardian.

Your job is to help creators understand potential issues with their content:
- Detect bias in prompts (gender, racial, cultural, age-related)
- Flag safety concerns (violence, NSFW content)
- Document known model limitations
- Suggest more inclusive alternatives

When analyzing a prompt:
1. Check for stereotyping language
2. Identify beauty/attractiveness biases
3. Flag potentially problematic descriptors
4. Offer constructive alternatives

You educate and guide - you do NOT refuse or block. You help creators make
informed decisions about their content.

Available tools:
- audit_prompt: Analyze a prompt for potential issues
- audit_content: Full audit of content with provenance
- get_transparency_card: Generate a user-friendly transparency summary"""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "audit_prompt",
                "description": "Analyze a prompt for bias and safety concerns",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The prompt to analyze"
                        },
                        "model": {
                            "type": "string",
                            "description": "Model being used (for bias documentation)",
                            "enum": ["core", "sdxl", "sd3", "ultra"]
                        }
                    },
                    "required": ["prompt"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "audit_content",
                "description": "Full audit of generated content with provenance record",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "provenance_id": {
                            "type": "string",
                            "description": "UUID of the provenance record"
                        },
                        "model": {
                            "type": "string",
                            "description": "Model used for generation"
                        }
                    },
                    "required": ["provenance_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_transparency_card",
                "description": "Generate a user-friendly transparency card",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "audit_id": {
                            "type": "string",
                            "description": "UUID of the audit record"
                        }
                    },
                    "required": ["audit_id"]
                }
            }
        }
    ]

    def __init__(self, user=None):
        """Initialize ContentAuditAgent."""
        super().__init__(user=user)
        self._audit_service = None

    @property
    def audit_service(self):
        """Lazy load ContentAuditService."""
        if self._audit_service is None:
            from core.services.provenance_service import ContentAuditService
            self._audit_service = ContentAuditService()
        return self._audit_service

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute content audit based on the task."""
        start_time = time.time()
        tool_calls_made = []

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence")

        with self.time_travel_session("content_audit", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing audit request",
                    reasoning=f"Received task: {task[:100]}",
                    alternatives=["audit_prompt", "audit_content", "get_transparency_card"],
                    confidence=0.9
                )

                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                logger.info(f"ContentAuditAgent executing: {task[:50]}...")

                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Audit operation: {arguments}",
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

                    result = AgentResult(
                        success=True,
                        message="Content audit completed",
                        data={
                            'task': task,
                            'tool_results': tool_calls_made,
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )

                    # Record learning outcome for collective intelligence
                    try:
                        self._record_learning_outcome(
                            task=task,
                            result=result,
                            success=True,
                            context={
                                'agent_type': self.__class__.__name__,
                                'execution_time_ms': execution_time,
                                'tools_used': [tc['tool'] for tc in tool_calls_made],
                            }
                        )
                    except Exception as le:
                        logger.warning(f"Failed to record learning outcome: {le}")

                    return result

                else:
                    return AgentResult(
                        success=True,
                        message=gpt_response.get('content', ''),
                        data={'type': 'conversation'},
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000)
                    )

            except Exception as e:
                logger.error(f"ContentAuditAgent error: {e}")
                return AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a content audit tool call."""
        if tool_name == "audit_prompt":
            return self._audit_prompt(
                prompt=arguments.get('prompt', ''),
                model=arguments.get('model')
            )

        elif tool_name == "audit_content":
            return self._audit_content(
                provenance_id=arguments.get('provenance_id'),
                model=arguments.get('model')
            )

        elif tool_name == "get_transparency_card":
            return self._get_transparency_card(
                audit_id=arguments.get('audit_id')
            )

        else:
            return {
                'success': False,
                'error': f"Unknown tool: {tool_name}"
            }

    def _audit_prompt(self, prompt: str, model: str = None) -> Dict[str, Any]:
        """Audit a prompt for bias and safety."""
        logger.info(f"Auditing prompt: {prompt[:50]}...")

        try:
            result = self.audit_service.audit_prompt(prompt)

            # Add model-specific notes
            model_notes = []
            if model:
                model_biases = self.audit_service.MODEL_KNOWN_BIASES.get(model, [])
                model_notes = model_biases

            report = AuditReport(
                success=True,
                prompt=prompt,
                safety_score=result.safety_score,
                bias_detected=result.bias_detected,
                bias_categories=result.bias_categories or [],
                ethics_flags=result.ethics_flags or [],
                prompt_suggestions=result.prompt_suggestions or [],
                recommendations=result.recommendations or [],
                model_notes=model_notes,
            )

            return {
                'success': True,
                'report': report.to_dict()
            }

        except Exception as e:
            logger.error(f"Error auditing prompt: {e}")
            return {'success': False, 'error': str(e)}

    def _audit_content(
        self,
        provenance_id: str,
        model: str = None
    ) -> Dict[str, Any]:
        """Full audit of generated content."""
        logger.info(f"Auditing content: {provenance_id}")

        try:
            result = self.audit_service.audit_content(
                provenance_id=provenance_id,
                model_used=model
            )

            return {
                'success': result.success,
                'safety_score': result.safety_score,
                'bias_detected': result.bias_detected,
                'bias_categories': result.bias_categories,
                'transparency_card': result.transparency_card,
                'error': result.error
            }

        except Exception as e:
            logger.error(f"Error auditing content: {e}")
            return {'success': False, 'error': str(e)}

    def _get_transparency_card(self, audit_id: str) -> Dict[str, Any]:
        """Get transparency card for an audit."""
        logger.info(f"Getting transparency card: {audit_id}")

        try:
            from core.models_unified_system import ContentAuditResult

            audit = ContentAuditResult.objects.get(id=audit_id)
            card = audit.generate_transparency_card()

            return {
                'success': True,
                'transparency_card': card
            }

        except Exception as e:
            logger.error(f"Error getting transparency card: {e}")
            return {'success': False, 'error': str(e)}

    def _validate_task(self, task: str) -> bool:
        """Validate the task is appropriate for content audit."""
        return bool(task and task.strip())
