"""
Image Agent - Specialized for Image Generation ONLY
====================================================

Session 268: Phase 1 - Foundation
Session 304: Added Learning Infrastructure Integration
Session 334: Added Project Context Support - Works within projects!

This agent creates images. That's ALL it does.
It has NO access to video, audio, 3D, or research tools.

This isolation prevents the tool selection confusion where GPT
picks the wrong tool (e.g., video_generation for a logo request).

Tools Available:
    - generate_image: Generate images from text prompts

Tools NOT Available (by design):
    - video generation
    - audio generation
    - 3D generation
    - web search
    - spider queries
    - any editing operations

Session 334: Project Context Support
    When project_id is in context, the agent:
    - Fetches project name, description, and brand info
    - Enhances vague prompts with project context
    - Example: "create logo" → "create logo for 'TechCorp': AI solutions company"

Usage:
    from core.agents import ImageAgent

    agent = ImageAgent(user=request.user)
    result = agent.execute(
        task="create a modern logo for a bakery",
        context={'count': 3, 'style': 'minimalist', 'project_id': 'uuid...'},
        scifi_context=scifi_service.get_context('ImageAgent'),
        spider_context=spider_service.get_insights_for_prompt(task)
    )
"""

import logging
import time
from typing import Dict, Any, List, Optional

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class ImageAgent(BaseAgent):
    """
    Agent specialized in image generation. Cannot do anything else.

    This agent:
    1. Takes a task like "create a professional logo"
    2. Enhances the prompt using GPT
    3. Calls generate_image with Stability AI
    4. Returns the generated images

    It CANNOT:
    - Generate videos
    - Generate audio
    - Generate 3D models
    - Search the web
    - Query spiders
    - Edit existing images (that's ImageEditingAgent)
    """

    name = "ImageAgent"

    system_prompt = """You are ImageAgent, a specialist in creating images.

Your ONLY job is to generate images based on the task given to you.
You have ONE tool: generate_image.

When given a task:
1. Analyze what the user wants
2. Enhance the prompt for better image generation results
3. Choose appropriate style based on the CONTEXT (brand, industry, use case)
4. Call generate_image with optimized parameters

IMPORTANT - Style Selection Guidelines:
- Match style to the PROJECT/BRAND context, not to a default preference
- For AI/tech companies: Consider clean, modern, minimalist, or professional styles first
- For creative agencies: Consider artistic, colorful, or unique brand-appropriate styles
- For corporate: Consider professional, clean, or photorealistic styles
- ONLY use cyberpunk/neon styles when the brand explicitly calls for it
- When in doubt, prefer: minimalist, modern, professional, or clean styles

Common image types and optimal settings:
- Logos: 1024x1024 (square), style varies by brand (modern, minimalist, geometric)
- Social media banners: 1280x720 (landscape) or 1080x1080 (square)
- Product photos: 1024x1024, photorealistic style
- Illustrations: 1024x1024, artistic/illustration style
- Thumbnails: 1280x720, eye-catching vibrant style

Available styles: photorealistic, cinematic, anime, watercolor, oil_painting,
digital_art, 3d_render, minimalist, vintage, pop_art, modern, professional,
clean, geometric, flat_design, gradient, elegant, bold, playful

SPECIAL STYLES (use only when explicitly requested or matching brand):
- cyberpunk: For explicitly futuristic/dystopian/neon-focused brands
- fantasy: For gaming, entertainment, or magical themes
- steampunk: For Victorian/mechanical aesthetics

You CANNOT create videos, audio, 3D models, or search the web. Just images.
If asked to do something outside image generation, politely explain you can only create images."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_image",
                "description": "Generate an image from a text prompt using Stability AI",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Detailed text description of the image to generate. Be specific about colors, style, composition, lighting, and mood."
                        },
                        "count": {
                            "type": "integer",
                            "description": "Number of images to generate (1-5)",
                            "default": 1,
                            "minimum": 1,
                            "maximum": 5
                        },
                        "style": {
                            "type": "string",
                            "description": "Visual style preset (photorealistic, cinematic, anime, watercolor, etc.)",
                            "default": "photorealistic"
                        },
                        "size": {
                            "type": "string",
                            "description": "Image dimensions (1024x1024, 1280x720, 720x1280, 1080x1080)",
                            "default": "1024x1024",
                            "enum": ["1024x1024", "1280x720", "720x1280", "1080x1080", "1024x768", "768x1024"]
                        },
                        "negative_prompt": {
                            "type": "string",
                            "description": "What to avoid in the image (e.g., 'blurry, low quality, text')",
                            "default": "blurry, low quality, distorted, ugly, deformed"
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
        """
        Execute image generation based on the task.

        Args:
            task: User's image request (e.g., "create a company logo")
            context: Additional context (count, style preferences)
            scifi_context: Mood, memory, evolution context
            spider_context: Trends, market data context

        Returns:
            AgentResult with generated images
        """
        start_time = time.time()
        tool_calls_made = []

        # Record time travel session for debugging
        with self.time_travel_session("image_generation", task, input_data=context):
            try:
                # Validate task
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                # Session 334: Get project context if project_id is provided
                project_id = context.get('project_id') if context else None
                project_context = self._get_project_context(project_id) if project_id else {}

                # Session 334: Enhance task with project context
                enhanced_task = self._enhance_task_with_project(task, project_context)
                if enhanced_task != task:
                    logger.info(f"Session 334: Enhanced task with project context")

                # Record initial analysis decision
                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing image generation request",
                    reasoning=f"Received task: {enhanced_task[:100]}",
                    alternatives=["reject_task", "request_clarification"],
                    confidence=0.9
                )

                # Build enhanced prompt with all context (including project)
                full_prompt = self._build_prompt_with_project(
                    enhanced_task, scifi_context, spider_context, project_context
                )

                logger.info(f"ImageAgent executing: {task[:50]}...")

                # Call GPT to decide on image parameters
                gpt_response = self._call_openai(full_prompt)

                # Process tool calls
                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        # Record the decision to call this tool
                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"GPT determined image generation with prompt: {arguments.get('prompt', '')[:50]}...",
                            alternatives=[],
                            confidence=0.95
                        )

                        # Execute the tool
                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        # Mark decision outcome
                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=tool_result.get('message', '')[:100]
                        )

                    # Compile results from all tool calls
                    all_images = []
                    for tc in tool_calls_made:
                        if tc['result'].get('success'):
                            images = tc['result'].get('images', [])
                            all_images.extend(images)

                    execution_time = int((time.time() - start_time) * 1000)

                    if all_images:
                        # Session 334: Include project context in result for "Add to Project" button
                        result_data = {
                            'images': all_images,
                            'count': len(all_images),
                            'task': enhanced_task,  # Use enhanced task for display
                            'original_task': task,
                        }
                        # Include project info for frontend "Add to Project" flow
                        if project_context:
                            result_data['project_id'] = project_context.get('project_id')
                            result_data['project_name'] = project_context.get('project_name')

                        result = AgentResult(
                            success=True,
                            message=f"Generated {len(all_images)} image(s)",
                            data=result_data,
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            decisions_made=self._tt_decision_count,
                            tool_calls=tool_calls_made
                        )

                        # === Session 304: Learning Infrastructure ===
                        # Record outcome for XP and pattern learning
                        self._record_learning_outcome(
                            result=result,
                            task=task,
                            context=context,
                            spider_data_used=bool(spider_context),
                            scifi_context_used=bool(scifi_context)
                        )

                        # Create memory of successful execution
                        self._create_execution_memory(
                            result=result,
                            task=task,
                            memory_type="success",
                            importance=0.6  # Successful generations are moderately important
                        )

                        # Track contribution to generated images
                        for img in all_images:
                            if img.get('id'):
                                self._track_contribution(
                                    content_type='image',
                                    content_id=img['id'],
                                    contribution_type='primary_creator',
                                    contribution_score=1.0
                                )

                        # Share knowledge about what styles/prompts worked
                        if tool_calls_made:
                            for tc in tool_calls_made:
                                if tc.get('result', {}).get('success'):
                                    args = tc.get('arguments', {})
                                    self._share_knowledge(
                                        knowledge_type='technique',
                                        title=f"Style: {args.get('style', 'default')} works well",
                                        knowledge_value={
                                            'style': args.get('style'),
                                            'prompt_pattern': args.get('prompt', '')[:100],
                                            'size': args.get('size'),
                                            'success': True
                                        },
                                        confidence=0.8
                                    )

                        return result
                    else:
                        result = AgentResult(
                            success=False,
                            error="No images were generated",
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            tool_calls=tool_calls_made
                        )

                        # Record failed outcome for learning
                        self._record_learning_outcome(
                            result=result,
                            task=task,
                            context=context,
                            spider_data_used=bool(spider_context),
                            scifi_context_used=bool(scifi_context)
                        )

                        # Create memory of failure to learn from
                        self._create_execution_memory(
                            result=result,
                            task=task,
                            memory_type="failure",
                            importance=0.7  # Failures are important to learn from
                        )

                        return result

                else:
                    # GPT responded without tool calls - return conversational response
                    return AgentResult(
                        success=True,
                        message=gpt_response.get('content', ''),
                        data={'type': 'conversation'},
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000)
                    )

            except Exception as e:
                logger.error(f"ImageAgent error: {e}")
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
        """
        Execute a tool call for image generation.

        Args:
            tool_name: Should be "generate_image"
            arguments: Image generation parameters

        Returns:
            Dict with success status and generated images
        """
        if tool_name != "generate_image":
            return {
                'success': False,
                'error': f"Unknown tool: {tool_name}. ImageAgent only supports generate_image."
            }

        # Import the actual image generation function
        from core.views_image import _execute_generate_image

        # Prepare parameters for the existing function
        parameters = {
            'prompt': arguments.get('prompt', ''),
            'count': arguments.get('count', 1),
            'style': arguments.get('style', 'photorealistic'),
            'size': arguments.get('size', '1024x1024'),
            'negative_prompt': arguments.get('negative_prompt', 'blurry, low quality, distorted'),
        }

        # Parse size into width/height
        size = parameters['size']
        if 'x' in size:
            parts = size.split('x')
            parameters['width'] = int(parts[0])
            parameters['height'] = int(parts[1])

        logger.info(f"ImageAgent generating: {parameters['prompt'][:50]}...")

        try:
            # Call the existing image generation function
            result = _execute_generate_image(
                user=self.user,
                parameters=parameters,
                session=None  # TODO: Pass session when available
            )

            if result.get('success'):
                # Format images for AgentResult
                images = result.get('images', [])
                if not images and result.get('image_url'):
                    # Single image returned
                    images = [{
                        'url': result['image_url'],
                        'id': result.get('image_id'),
                        'prompt': parameters['prompt']
                    }]

                return {
                    'success': True,
                    'message': f"Generated {len(images)} image(s)",
                    'images': images
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Image generation failed')
                }

        except Exception as e:
            logger.error(f"Image generation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _validate_task(self, task: str) -> bool:
        """
        Validate the task is appropriate for image generation.

        Args:
            task: The task string

        Returns:
            True if valid image generation request
        """
        if not task or not task.strip():
            return False

        # Check for keywords that suggest this is NOT an image request
        non_image_keywords = [
            'video', 'movie', 'animate', 'motion',
            'audio', 'sound', 'music', 'voice', 'speech',
            '3d model', 'mesh', 'render 3d',
            'search for', 'find', 'look up', 'research'
        ]

        task_lower = task.lower()
        for keyword in non_image_keywords:
            if keyword in task_lower:
                logger.warning(f"ImageAgent received non-image task: {task[:50]}")
                # Still return True - let GPT explain it can't do this
                # The agent will respond conversationally

        return True
