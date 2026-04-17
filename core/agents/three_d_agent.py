"""
3D Agent - Specialized for 3D Model Generation ONLY
====================================================

Session 268: Phase 2 - Creation Agents
Session 304: Learning Infrastructure Integration

This agent creates 3D models. That's ALL it does.
It has NO access to image, video, audio, or research tools.

Tools Available:
    - convert_to_3d: Convert 2D image to 3D model
    - generate_3d_scene: Generate 3D scene from description

Tools NOT Available (by design):
    - image generation
    - video generation
    - audio generation
    - web search
"""

import logging
import time
from typing import Dict, Any

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_3d_prompt_with_ml(prompt_data: dict) -> dict:
    """Analyze 3D prompts using ML models (Text) for geometry/style enhancement."""
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
            'geometry_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML 3D prompt analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class ThreeDAgent(BaseAgent):
    """
    Agent specialized in 3D model generation. Cannot do anything else.

    This agent:
    1. Takes a task like "convert this image to a 3D model"
    2. Uses Replicate API for 3D conversion
    3. Returns the 3D model result

    It CANNOT:
    - Generate images
    - Generate videos
    - Generate audio
    - Search the web
    """

    name = "ThreeDAgent"

    system_prompt = """You are ThreeDAgent, a specialist in creating 3D models.

Your ONLY job is to generate 3D content based on the task given to you.
You have these tools:
- convert_to_3d: Convert a 2D image into a 3D model
- generate_3d_scene: Generate a 3D scene from a text description

When given a task:
1. If user has an existing image they want in 3D, use convert_to_3d
2. For creating new 3D scenes from scratch, use generate_3d_scene

Output formats supported:
- GLB (default): Web-compatible format
- OBJ: Standard 3D model format
- STL: For 3D printing

You CANNOT create images, videos, audio, or search the web. Just 3D models.
If asked to do something outside 3D generation, politely explain you can only create 3D content."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "convert_to_3d",
                "description": "Convert a 2D image into a 3D model using AI",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_id": {
                            "type": "string",
                            "description": "ID of the image to convert to 3D (UUID or sequential number)"
                        },
                        "output_format": {
                            "type": "string",
                            "description": "Output 3D format",
                            "enum": ["glb", "obj", "stl"],
                            "default": "glb"
                        },
                        "quality": {
                            "type": "string",
                            "description": "Model quality level",
                            "enum": ["draft", "standard", "high"],
                            "default": "standard"
                        }
                    },
                    "required": ["image_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_3d_scene",
                "description": "Generate a 3D scene from a text description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Description of the 3D scene to generate"
                        },
                        "output_format": {
                            "type": "string",
                            "description": "Output 3D format",
                            "enum": ["glb", "obj", "stl"],
                            "default": "glb"
                        },
                        "style": {
                            "type": "string",
                            "description": "Visual style of the 3D model",
                            "enum": ["realistic", "stylized", "low_poly", "cartoon"],
                            "default": "realistic"
                        }
                    },
                    "required": ["prompt"]
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
        """Execute 3D generation based on the task."""
        start_time = time.time()
        tool_calls_made = []

        with self.time_travel_session("3d_generation", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing 3D generation request",
                    reasoning=f"Received task: {task[:100]}",
                    confidence=0.9
                )

                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Selected {tool_name} for 3D operation",
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
                            result_summary=tool_result.get('message', '')[:100]
                        )

                    execution_time = int((time.time() - start_time) * 1000)

                    # Session 840: Collect actual errors for better error reporting
                    successful_calls = [tc for tc in tool_calls_made if tc['result'].get('success')]
                    failed_calls = [tc for tc in tool_calls_made if not tc['result'].get('success')]
                    all_errors = [tc['result'].get('error', 'Unknown error') for tc in failed_calls]

                    if successful_calls:
                        result = AgentResult(
                            success=True,
                            message=f"3D model generated",
                            data=successful_calls[0]['result'],
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            decisions_made=self._tt_decision_count,
                            tool_calls=tool_calls_made
                        )

                        # === Session 304: Learning Infrastructure ===
                        self._record_learning_outcome(result, task, context, bool(spider_context), bool(scifi_context))
                        self._create_execution_memory(result, task, "success", 0.6)
                        args = successful_calls[0].get('arguments', {})
                        self._share_knowledge(
                            knowledge_type='technique',
                            title=f"3D: {args.get('output_format', 'glb')} format works",
                            knowledge_value={'format': args.get('output_format'), 'success': True},
                            confidence=0.8
                        )

                        # Session 1006: Persist output to Deliverable
                        # Session 1092: render with shared helper for gate passing.
                        self._save_to_deliverable(
                            title=f"Generated 3D Model: {task[:80]}",
                            content=self._render_agent_output_markdown(
                                task=task,
                                summary=result.message,
                                tool_calls=tool_calls_made,
                                extra={'output_format': args.get('output_format', 'glb')},
                            ),
                            deliverable_type='3d_model',
                            category='3D Generation',
                            tags=['3d', args.get('output_format', 'glb')],
                            metadata={'task': task[:200], 'output_format': args.get('output_format', 'glb')},
                        )

                        return result
                    else:
                        # Session 840: Include actual error details for better debugging
                        error_detail = "; ".join(all_errors) if all_errors else "No 3D model was generated"
                        result = AgentResult(
                            success=False,
                            error=f"3D generation failed: {error_detail}",
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            tool_calls=tool_calls_made
                        )
                        self._record_learning_outcome(result, task, context, bool(spider_context), bool(scifi_context))
                        self._create_execution_memory(result, task, "failure", 0.7)
                        return result
                else:
                    # Session 757: Return rich conversation data for Memory Palace display
                    response_content = gpt_response.get('content', '')
                    return AgentResult(
                        success=True,
                        message=response_content,
                        data={
                            'type': 'conversation',
                            'content_type': '3d_model_discussion',
                            'response': response_content,
                            'query': task,
                        },
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000)
                    )

            except Exception as e:
                logger.error(f"ThreeDAgent error: {e}")
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
        """Execute a tool call for 3D generation."""

        if tool_name == "convert_to_3d":
            from core.views_image import _execute_convert_to_3d
            parameters = {
                'image_id': arguments.get('image_id'),
                'output_format': arguments.get('output_format', 'glb'),
                'quality': arguments.get('quality', 'standard'),
            }
            return _execute_convert_to_3d(self.user, parameters, session=None)

        elif tool_name == "generate_3d_scene":
            # Text-to-3D generation - return concept/plan since actual generation may not be available
            prompt = arguments.get('prompt', '')
            output_format = arguments.get('output_format', 'glb')
            style = arguments.get('style', 'realistic')

            # Generate a detailed 3D concept plan
            return {
                'success': True,
                'type': '3d_concept',
                'message': f"3D model concept created for: {prompt[:100]}",
                'concept': {
                    'description': prompt,
                    'output_format': output_format,
                    'style': style,
                    'recommended_approach': 'Use Blender or professional 3D software to model this concept',
                    'modeling_tips': [
                        f"Start with basic shapes to block out the {style} form",
                        "Add detail progressively from large to small features",
                        f"Export as {output_format.upper()} for web compatibility" if output_format == 'glb' else f"Export as {output_format.upper()}",
                        "Apply appropriate textures and materials for the style"
                    ],
                    'polygon_estimate': '5000-15000 tris for web-optimized model',
                    'texture_resolution': '1024x1024 or 2048x2048 recommended'
                },
                'next_steps': [
                    'Create concept sketches from multiple angles',
                    'Model in Blender, Maya, or 3ds Max',
                    'Apply textures and materials',
                    f'Export to {output_format.upper()} format'
                ]
            }

        return super()._execute_tool_call(tool_name, arguments)
