"""
Image Editing Agent - Specialized for Image EDITING ONLY
=========================================================

Session 268: Phase 2 - Editing Agents
Session 304: Learning Infrastructure Integration

This agent EDITS existing images. That's ALL it does.
It has NO access to creation, video, audio, or research tools.

Tools Available:
    - upscale: Upscale image resolution
    - remove_background: Remove image background
    - create_variations: Generate variations of an image
    - recolor: Change colors in an image
    - search_replace: Replace objects in an image

Tools NOT Available (by design):
    - image generation (that's ImageAgent)
    - video generation/editing
    - audio generation
    - web search
"""

import logging
import time
from typing import Dict, Any

from core.agents.base_agent import BaseAgent, AgentResult, ActionableOutputConfig
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_image_edit_with_ml(edit_data: dict) -> dict:
    """Analyze image edit requests using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=edit_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'edit_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML image edit analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class ImageEditingAgent(BaseAgent):
    """
    Agent specialized in editing existing images. Cannot create new ones.

    This agent:
    1. Takes a task like "upscale image 5" or "remove background from my logo"
    2. Identifies the image to edit
    3. Applies the appropriate edit operation
    4. Returns the edited image

    It CANNOT:
    - Generate new images (use ImageAgent)
    - Generate videos
    - Generate audio
    - Search the web
    """

    name = "ImageEditingAgent"

    # Session 856: Content review configuration
    actionable_config = ActionableOutputConfig(
        actions=['approve', 'revise', 'reject'],
        payload_fields=['tool_used', 'image_id', 'operation', 'scale_factor', 'variations']
    )

    system_prompt = """You are ImageEditingAgent, a specialist in modifying existing images.

Your ONLY job is to EDIT existing images. You do NOT create new images from scratch.
You have these tools:
- upscale: Increase image resolution (2x or 4x)
- remove_background: Remove the background from an image
- create_variations: Generate style variations of an existing image
- recolor: Change colors in an image
- search_replace: Find and replace objects within an image
- process_image: General-purpose PIL processing — resize, center_crop, circular_mask, enhance, convert format. Use this for badges, thumbnails, cropping, circular masks, brightness/contrast/sharpness adjustments, and format conversion. Chain multiple operations in one call.

When given a task:
1. Identify which image the user wants to edit (by UUID, sequential number, or Cloudinary URL)
2. Determine which editing operation is needed
3. Apply the operation with appropriate parameters
4. For image_id: pass whatever identifier you have — UUID, sequential number, or full URL all work

Common operations:
- "Make it bigger" / "Higher resolution" → upscale
- "Remove the background" / "Transparent background" → remove_background
- "Give me variations" / "Different versions" → create_variations
- "Change the color to..." / "Make it blue" → recolor
- "Replace the X with Y" → search_replace
- "Make a badge" / "Crop and resize" / "Circle mask" / "Thumbnail" → process_image
- "Enhance brightness/contrast" / "Sharpen" → process_image

IMPORTANT: You MUST always use your tools to perform edits. NEVER return scripts or instructions.
If a task needs multiple steps (e.g. remove background then crop to circle), call the tools in sequence.
For badge/headshot creation: use remove_background first, then process_image with center_crop + circular_mask + enhance.

You CANNOT create new images, videos, or audio. Only edit existing images.
If asked to create something new, explain you can only edit existing images."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "upscale",
                "description": "Upscale an image to higher resolution",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_id": {
                            "type": "string",
                            "description": "ID of the image to upscale (UUID or sequential number)"
                        },
                        "scale_factor": {
                            "type": "integer",
                            "description": "How much to scale (2 or 4)",
                            "enum": [2, 4],
                            "default": 2
                        },
                        "creative_upscale": {
                            "type": "boolean",
                            "description": "Use AI to add detail (true) or just resize (false)",
                            "default": False
                        }
                    },
                    "required": ["image_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "remove_background",
                "description": "Remove the background from an image, making it transparent",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_id": {
                            "type": "string",
                            "description": "ID of the image to process"
                        }
                    },
                    "required": ["image_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_variations",
                "description": "Generate style variations of an existing image",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_id": {
                            "type": "string",
                            "description": "ID of the image to create variations from"
                        },
                        "count": {
                            "type": "integer",
                            "description": "Number of variations to generate (1-4)",
                            "default": 3,
                            "minimum": 1,
                            "maximum": 4
                        },
                        "variation_strength": {
                            "type": "number",
                            "description": "How different the variations should be (0.0-1.0)",
                            "default": 0.5
                        }
                    },
                    "required": ["image_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "recolor",
                "description": "Change colors in an image",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_id": {
                            "type": "string",
                            "description": "ID of the image to recolor"
                        },
                        "target_color": {
                            "type": "string",
                            "description": "Color to change (e.g., 'red', 'blue', '#FF5733')"
                        },
                        "new_color": {
                            "type": "string",
                            "description": "New color to apply"
                        }
                    },
                    "required": ["image_id", "target_color", "new_color"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_replace",
                "description": "Find and replace objects within an image using AI",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_id": {
                            "type": "string",
                            "description": "ID of the image to modify"
                        },
                        "search_prompt": {
                            "type": "string",
                            "description": "What to find/select in the image"
                        },
                        "replace_prompt": {
                            "type": "string",
                            "description": "What to replace it with"
                        }
                    },
                    "required": ["image_id", "search_prompt", "replace_prompt"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "process_image",
                "description": "General-purpose image processing using PIL: resize, crop, circular mask, enhance, convert format. Use this for badge creation, thumbnails, format conversion, or any local image manipulation that doesn't need AI.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_id": {
                            "type": "string",
                            "description": "ID of the image (UUID, sequential number, or Cloudinary URL)"
                        },
                        "operations": {
                            "type": "array",
                            "description": "List of operations to apply in order",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "op": {
                                        "type": "string",
                                        "enum": ["resize", "center_crop", "circular_mask", "enhance", "convert"],
                                        "description": "Operation to perform"
                                    },
                                    "width": {"type": "integer", "description": "Target width (for resize/center_crop)"},
                                    "height": {"type": "integer", "description": "Target height (for resize/center_crop)"},
                                    "brightness": {"type": "number", "description": "Brightness factor for enhance (1.0 = no change)"},
                                    "contrast": {"type": "number", "description": "Contrast factor for enhance (1.0 = no change)"},
                                    "sharpness": {"type": "number", "description": "Sharpness factor for enhance (1.0 = no change)"},
                                    "format": {"type": "string", "enum": ["PNG", "JPEG", "WEBP"], "description": "Output format for convert"}
                                },
                                "required": ["op"]
                            }
                        },
                        "output_format": {
                            "type": "string",
                            "enum": ["PNG", "JPEG", "WEBP"],
                            "description": "Final output format (default: PNG)",
                            "default": "PNG"
                        }
                    },
                    "required": ["image_id", "operations"]
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
        """Execute image editing based on the task."""
        start_time = time.time()
        tool_calls_made = []

        with self.time_travel_session("image_editing", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing image editing request",
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
                            reasoning=f"Selected {tool_name} for image editing",
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

                    successful_calls = [tc for tc in tool_calls_made if tc['result'].get('success')]
                    if successful_calls:
                        # Session 856: Build descriptive message based on tool used
                        tool_used = successful_calls[0]['tool']
                        args = successful_calls[0].get('arguments', {})
                        tool_result = successful_calls[0]['result']
                        image_id = args.get('image_id', 'unknown')
                        if tool_used == 'upscale':
                            scale = args.get('scale_factor', 2)
                            creative = 'creative' if args.get('creative_upscale') else 'standard'
                            descriptive_msg = f"Image upscaled: {image_id} at {scale}x ({creative} mode)"
                        elif tool_used == 'remove_background':
                            descriptive_msg = f"Background removed from image {image_id}"
                        elif tool_used == 'create_variations':
                            count = args.get('count', 3)
                            strength = args.get('variation_strength', 0.5)
                            descriptive_msg = f"Created {count} variations of image {image_id} (strength: {strength:.0%})"
                        elif tool_used == 'recolor':
                            target = args.get('target_color', '')
                            new_color = args.get('new_color', '')
                            descriptive_msg = f"Recolored {image_id}: {target} → {new_color}"
                        elif tool_used == 'search_replace':
                            search = args.get('search_prompt', '')[:30]
                            replace = args.get('replace_prompt', '')[:30]
                            descriptive_msg = f"Search/replace on {image_id}: '{search}' → '{replace}'"
                        else:
                            descriptive_msg = f"Image editing '{tool_used}' completed on {image_id}"

                        # Merge tool result with additional context
                        result_data = tool_result.copy() if isinstance(tool_result, dict) else {'result': tool_result}
                        result_data['tool_used'] = tool_used
                        result_data['image_id'] = image_id
                        result_data['operation'] = tool_used

                        result = AgentResult(
                            success=True,
                            message=descriptive_msg,
                            data=result_data,
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            decisions_made=self._tt_decision_count,
                            tool_calls=tool_calls_made
                        )

                        # === Session 304: Learning Infrastructure ===
                        self._record_learning_outcome(result, task, context, bool(spider_context), bool(scifi_context))
                        self._create_execution_memory(result, task, "success", 0.6)
                        tool_used = successful_calls[0]['tool']
                        self._share_knowledge(
                            knowledge_type='technique',
                            title=f"ImageEdit: {tool_used} works",
                            knowledge_value={'tool': tool_used, 'success': True},
                            confidence=0.8
                        )

                        # Session 1006: Persist output to Deliverable
                        args = successful_calls[0].get('arguments', {})
                        # Session 1092: render with shared helper so short status
                        # messages don't fall below the 300-char gate.
                        self._save_to_deliverable(
                            title=f"Image Edit ({tool_used}): {task[:80]}",
                            content=self._render_agent_output_markdown(
                                task=task,
                                summary=result.message,
                                tool_calls=tool_calls_made,
                                extra={'tool_used': tool_used, 'image_id': args.get('image_id')},
                            ),
                            deliverable_type='image',
                            category='Image Editing',
                            tags=['image_edit', tool_used],
                            metadata={'task': task[:200], 'tool_used': tool_used, 'image_id': args.get('image_id')},
                        )

                        return result
                    else:
                        result = AgentResult(
                            success=False,
                            error="Image editing failed",
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
                            'content_type': 'image_editing_discussion',
                            'response': response_content,
                            'query': task,
                        },
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000)
                    )

            except Exception as e:
                logger.error(f"ImageEditingAgent error: {e}")
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
        """Execute a tool call for image editing."""

        if tool_name == "upscale":
            from core.views_image import _execute_upscale
            parameters = {
                'image_id': arguments.get('image_id'),
                'scale_factor': arguments.get('scale_factor', 2),
                'creative_upscale': arguments.get('creative_upscale', False),
            }
            return _execute_upscale(self.user, parameters, session=None)

        elif tool_name == "remove_background":
            from core.views_image import _execute_remove_background
            parameters = {
                'image_id': arguments.get('image_id'),
            }
            return _execute_remove_background(self.user, parameters, session=None)

        elif tool_name == "create_variations":
            from core.views_image import _execute_create_variations
            parameters = {
                'image_id': arguments.get('image_id'),
                'count': arguments.get('count', 3),
                'variation_strength': arguments.get('variation_strength', 0.5),
            }
            return _execute_create_variations(self.user, parameters, session=None)

        elif tool_name == "recolor":
            from core.views_image import _execute_recolor
            parameters = {
                'image_id': arguments.get('image_id'),
                'target_color': arguments.get('target_color'),
                'new_color': arguments.get('new_color'),
            }
            return _execute_recolor(self.user, parameters, session=None)

        elif tool_name == "search_replace":
            from core.views_image import _execute_search_replace
            parameters = {
                'image_id': arguments.get('image_id'),
                'search_prompt': arguments.get('search_prompt'),
                'replace_prompt': arguments.get('replace_prompt'),
            }
            return _execute_search_replace(self.user, parameters, session=None)

        elif tool_name == "process_image":
            from core.views_image_edit import _execute_process_image
            return _execute_process_image(self.user, arguments)

        return super()._execute_tool_call(tool_name, arguments)
