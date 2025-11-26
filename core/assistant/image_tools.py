"""
Image Tool Handlers for AI Assistant
====================================

Tool execution handlers for image generation and editing operations.
Delegates to unified ImageAgent for actual execution.

Session 184: Extracted from personal_ai_assistant_enhanced.py
Session 202: Updated to use unified ImageAgent
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ImageToolsMixin:
    """
    Mixin class providing image tool handler methods.

    This mixin expects the following attributes on the class it's mixed into:
    - self.user: Django User object
    - self.project: Optional CreativeProject object
    """

    def _tool_upscale_image(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the upscale_image tool."""
        logger.info("UPSCALE_IMAGE TOOL CALLED!")
        logger.info("Delegating to Image Editing Agent...")

        try:
            image_id = arguments['image_id']
            current_project = getattr(self, 'project', None)

            from agents.image_agent import ImageAgent

            agent = ImageAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

            result = agent.edit(
                operation='upscale',
                image_id=image_id
            )

            return result

        except Exception as e:
            logger.error(f"Upscale tool error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to upscale image: {str(e)}"
            }

    def _tool_remove_background(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the remove_background tool."""
        logger.info("REMOVE_BACKGROUND TOOL CALLED!")
        logger.info("Delegating to Image Editing Agent...")

        try:
            image_id = arguments['image_id']
            current_project = getattr(self, 'project', None)

            from agents.image_agent import ImageAgent

            agent = ImageAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

            result = agent.edit(
                operation='remove_background',
                image_id=image_id
            )

            return result

        except Exception as e:
            logger.error(f"Remove background tool error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to remove background: {str(e)}"
            }

    def _tool_create_variations(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the create_image_variations tool."""
        logger.info("CREATE_VARIATIONS TOOL CALLED!")
        logger.debug(f"User: {getattr(self.user, 'username', 'N/A')}")
        logger.info("Delegating to Image Editing Agent...")

        try:
            image_id = arguments['image_id']
            count = arguments.get('count', 3)
            prompt = arguments.get('prompt', 'creative variation')

            logger.debug(f"Image ID: {image_id}, Count: {count}")

            current_project = getattr(self, 'project', None)

            from agents.image_agent import ImageAgent

            agent = ImageAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )
            logger.debug(f"Created agent with user: {agent.user.username}")

            result = agent.edit(
                operation='variations',
                image_id=image_id,
                count=count,
                prompt=prompt
            )

            return result

        except Exception as e:
            logger.error(f"Create variations tool error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to create variations: {str(e)}"
            }

    def _tool_erase_object(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the erase_object tool."""
        logger.info("ERASE_OBJECT TOOL CALLED!")
        logger.info("Delegating to Image Editing Agent...")

        try:
            image_id = arguments['image_id']
            object_description = arguments['object_description']
            current_project = getattr(self, 'project', None)

            from agents.image_agent import ImageAgent

            agent = ImageAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

            result = agent.edit(
                operation='erase_object',
                image_id=image_id,
                search_prompt=object_description
            )

            return result

        except Exception as e:
            logger.error(f"Erase object tool error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to erase object: {str(e)}"
            }

    def _tool_recolor_image(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the recolor_image tool."""
        logger.info("RECOLOR_IMAGE TOOL CALLED!")
        logger.info("Delegating to Image Editing Agent...")

        try:
            image_id = arguments['image_id']
            prompt = arguments['prompt']
            select_prompt = arguments.get('select_prompt')
            current_project = getattr(self, 'project', None)

            from agents.image_agent import ImageAgent

            agent = ImageAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

            result = agent.edit(
                operation='recolor',
                image_id=image_id,
                prompt=prompt,
                select_prompt=select_prompt
            )

            return result

        except Exception as e:
            logger.error(f"Recolor tool error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to recolor image: {str(e)}"
            }

    def _tool_refine_image(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the refine_image tool."""
        logger.info("REFINE_IMAGE TOOL CALLED!")
        logger.info("Delegating to Image Editing Agent...")

        try:
            image_id = arguments['image_id']
            refinement_request = arguments['refinement_request']
            current_project = getattr(self, 'project', None)

            from agents.image_agent import ImageAgent

            agent = ImageAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

            result = agent.edit(
                operation='refine',
                image_id=image_id,
                prompt=refinement_request
            )

            return result

        except Exception as e:
            logger.error(f"Refine image tool error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to refine image: {str(e)}"
            }

    def _tool_search_and_replace(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute search_and_replace tool - Remove/replace specific objects in images."""
        logger.info("SEARCH_AND_REPLACE TOOL CALLED!")
        logger.info("Delegating to Image Editing Agent...")

        try:
            image_id = arguments['image_id']
            search_prompt = arguments['search_prompt']
            replace_prompt = arguments.get('replace_prompt', '')
            current_project = getattr(self, 'project', None)

            from agents.image_agent import ImageAgent

            agent = ImageAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

            result = agent.edit(
                operation='search_and_replace',
                image_id=image_id,
                search_prompt=search_prompt,
                replace_prompt=replace_prompt
            )

            return result

        except Exception as e:
            logger.error(f"Search and replace tool error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to search and replace: {str(e)}"
            }

    def _tool_creative_upscale(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute creative_upscale tool - Upscale with AI-generated creative details."""
        logger.info("CREATIVE_UPSCALE TOOL CALLED!")
        logger.info("Delegating to Image Editing Agent...")

        try:
            image_id = arguments['image_id']
            prompt = arguments['prompt']
            creativity = arguments.get('creativity', 0.3)
            current_project = getattr(self, 'project', None)

            from agents.image_agent import ImageAgent

            agent = ImageAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

            result = agent.edit(
                operation='creative_upscale',
                image_id=image_id,
                prompt=prompt,
                creativity=creativity
            )

            return result

        except Exception as e:
            logger.error(f"Creative upscale tool error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to creative upscale: {str(e)}"
            }
