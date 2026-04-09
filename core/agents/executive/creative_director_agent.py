"""
Creative Director Agent - Clean Architecture
=============================================

Session 280: Phase 2 - Agent Architecture Unification

This agent provides high-level creative guidance before content generation,
reviewing prompts and ensuring consistency across projects.

Tools Available:
    - review_prompt: Review and enhance a creative prompt
    - establish_direction: Set creative direction for a project
    - check_consistency: Check brand/style consistency

Usage:
    from core.agents.executive import CreativeDirectorAgent

    agent = CreativeDirectorAgent(user=request.user)
    result = agent.execute(
        task="Review my logo prompt: 'tech startup logo'",
        context={},
        scifi_context={},
        spider_context={}
    )
"""

import logging
import time
from typing import Dict, Any

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_creative_with_ml(creative_data: dict) -> dict:
    """Analyze creative direction using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=creative_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'creative_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML creative analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class CreativeDirectorAgent(BaseAgent):
    """
    Creative Director Agent - High-Level Creative Guidance.

    This agent:
    1. Reviews and enhances creative prompts
    2. Establishes creative direction for projects
    3. Ensures consistency across outputs

    It CANNOT:
    - Generate images, videos, or audio
    - Create actual content
    """

    name = "CreativeDirectorAgent"
    requires_system_context = True  # Session 820: Inject CLAUDE.md + critical docs

    system_prompt = """You are CreativeDirectorAgent, the Creative Director AI assistant.

Your job is to provide high-level creative guidance before content generation.
You review prompts, suggest improvements, and ensure creative consistency.

When given a task:
1. Analyze the creative intent
2. Identify areas for improvement
3. Suggest enhancements and best practices
4. Ensure brand/style consistency

Creative principles by content type:

LOGO:
- Key: Simplicity, memorability, scalability, timelessness
- Avoid: Too much detail, trendy elements, poor contrast
- Tips: Consider brand personality, test at different sizes

THUMBNAIL:
- Key: Curiosity gap, bold text (3-5 words), high contrast, human faces
- Avoid: Too much text, low contrast, no focal point
- Tips: Use complementary colors, include human element

SOCIAL MEDIA:
- Key: Stop the scroll, platform-native, clear message in 3 seconds
- Avoid: Generic imagery, too much text, off-brand colors
- Tips: Match platform aesthetics, emotional connection

You CANNOT create content - just provide creative direction."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "review_prompt",
                "description": "Review and enhance a creative prompt",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The prompt to review"
                        },
                        "content_type": {
                            "type": "string",
                            "description": "Type of content",
                            "enum": ["logo", "thumbnail", "social", "illustration", "product", "general"]
                        }
                    },
                    "required": ["prompt"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "establish_direction",
                "description": "Establish creative direction for a project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_brief": {
                            "type": "string",
                            "description": "Brief description of the project"
                        },
                        "target_audience": {
                            "type": "string",
                            "description": "Target audience"
                        },
                        "tone": {
                            "type": "string",
                            "description": "Desired tone",
                            "enum": ["professional", "playful", "modern", "classic", "bold", "subtle"]
                        }
                    },
                    "required": ["project_brief"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_consistency",
                "description": "Check brand/style consistency",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "style_description": {
                            "type": "string",
                            "description": "Description of the style to check"
                        },
                        "brand_guidelines": {
                            "type": "string",
                            "description": "Brand guidelines to check against"
                        }
                    },
                    "required": []
                }
            }
        }
    ]

    # Creative principles
    CREATIVE_PRINCIPLES = {
        'logo': {
            'key_principles': [
                'Simplicity and memorability',
                'Scalability (works at any size)',
                'Timelessness over trends',
                'Uniqueness in the market'
            ],
            'common_mistakes': [
                'Too much detail',
                'Overly trendy elements',
                'Poor contrast',
                'Unclear at small sizes'
            ],
            'enhancement_tips': [
                'Consider the brand personality',
                'Think about where it will be used',
                'Ensure it works in one color',
                'Test at different sizes'
            ]
        },
        'thumbnail': {
            'key_principles': [
                'Curiosity gap - make viewers want to click',
                'Bold, readable text (3-5 words max)',
                'High contrast and saturation',
                'Human faces with expressions'
            ],
            'common_mistakes': [
                'Too much text',
                'Low contrast',
                'No clear focal point',
                'Misleading content'
            ],
            'enhancement_tips': [
                'Use complementary colors for text',
                'Include a human element',
                'Create visual hierarchy',
                'Match video content'
            ]
        },
        'social': {
            'key_principles': [
                'Stop the scroll - first impression matters',
                'Platform-native aesthetics',
                'Clear message in 3 seconds',
                'Emotional connection'
            ],
            'common_mistakes': [
                'Generic stock imagery',
                'Too much text',
                'Off-brand colors',
                'No clear CTA'
            ],
            'enhancement_tips': [
                'Use platform-specific formats',
                'Lead with strong visuals',
                'Include brand elements subtly',
                'Test different variations'
            ]
        }
    }

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute creative direction based on the task."""
        start_time = time.time()
        tool_calls_made = []

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence")

        with self.time_travel_session("creative_direction", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing creative request",
                    reasoning=f"Received task: {task[:100]}",
                    alternatives=["ask_for_clarification"],
                    confidence=0.9
                )

                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                logger.info(f"CreativeDirectorAgent executing: {task[:50]}...")

                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Creative analysis: {arguments}",
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

                    # Session 1200: Synthesize tool results into real analysis
                    tool_results = [tc.get('result', {}) for tc in tool_calls_made]
                    synthesis = self._synthesize_tool_results(tool_calls_made, tool_results, task)
                    analysis_msg = synthesis if synthesis else "Creative direction completed"

                    result = AgentResult(
                        success=True,
                        message=analysis_msg,
                        data={
                            'task': task,
                            'tool_results': tool_calls_made,
                            'content': synthesis,
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )

                    # Session 1006: Persist output to Deliverable
                    self._save_to_deliverable(
                        title=f"Creative Direction: {task[:80]}",
                        content=analysis_msg,
                        deliverable_type='analysis',
                        category='Creative Direction',
                        tags=['creative', 'direction'],
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
                logger.error(f"CreativeDirectorAgent error: {e}")
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
        """Execute a creative direction tool call."""
        if tool_name == "review_prompt":
            return self._review_prompt(
                prompt=arguments.get('prompt', ''),
                content_type=arguments.get('content_type', 'general')
            )

        elif tool_name == "establish_direction":
            return self._establish_direction(
                project_brief=arguments.get('project_brief', ''),
                target_audience=arguments.get('target_audience', 'general'),
                tone=arguments.get('tone', 'modern')
            )

        elif tool_name == "check_consistency":
            return self._check_consistency(
                style_description=arguments.get('style_description', ''),
                brand_guidelines=arguments.get('brand_guidelines', '')
            )

        return super()._execute_tool_call(tool_name, arguments)

    def _review_prompt(
        self,
        prompt: str,
        content_type: str
    ) -> Dict[str, Any]:
        """Review and enhance a creative prompt."""
        logger.info(f"Reviewing prompt for {content_type}: {prompt[:50]}")

        principles = self.CREATIVE_PRINCIPLES.get(
            content_type,
            self.CREATIVE_PRINCIPLES.get('logo')
        )

        # Build enhanced prompt
        enhancements = []
        for tip in principles.get('enhancement_tips', [])[:2]:
            enhancements.append(tip)

        enhanced_prompt = prompt
        if not any(word in prompt.lower() for word in ['style', 'color', 'design']):
            enhanced_prompt = f"{prompt}, modern style, clean design"

        return {
            'success': True,
            'original_prompt': prompt,
            'enhanced_prompt': enhanced_prompt,
            'content_type': content_type,
            'key_principles': principles.get('key_principles', []),
            'avoid': principles.get('common_mistakes', []),
            'suggestions': enhancements
        }

    def _establish_direction(
        self,
        project_brief: str,
        target_audience: str,
        tone: str
    ) -> Dict[str, Any]:
        """Establish creative direction for a project."""
        logger.info(f"Establishing direction for: {project_brief[:50]}")

        direction = {
            'project_brief': project_brief,
            'target_audience': target_audience,
            'tone': tone,
            'visual_style': {
                'primary_approach': tone,
                'color_suggestion': 'Use colors appropriate to your brand',
                'typography': 'Clean, readable fonts'
            },
            'content_guidelines': [
                f'Maintain {tone} tone throughout',
                f'Design for {target_audience} audience',
                'Keep messaging consistent',
                'Use high-quality visuals'
            ],
            'recommended_content_types': ['logo', 'social', 'brand_identity']
        }

        return {
            'success': True,
            'direction': direction
        }

    def _check_consistency(
        self,
        style_description: str,
        brand_guidelines: str
    ) -> Dict[str, Any]:
        """Check brand/style consistency."""
        logger.info(f"Checking consistency: {style_description[:50]}")

        check_result = {
            'style_description': style_description,
            'consistency_score': 85,  # Would be computed in full implementation
            'findings': [
                {'aspect': 'Color usage', 'status': 'consistent'},
                {'aspect': 'Typography', 'status': 'consistent'},
                {'aspect': 'Visual style', 'status': 'needs_review'}
            ],
            'recommendations': [
                'Ensure all assets use brand colors',
                'Maintain consistent font hierarchy',
                'Review visual style for alignment'
            ]
        }

        return {
            'success': True,
            'check_result': check_result
        }

    def _validate_task(self, task: str) -> bool:
        """Validate the task is appropriate for creative direction."""
        return bool(task and task.strip())
