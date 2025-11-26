"""
EditingOrchestratorAgent - Coordinate Multi-Step Image Editing

Philosophy: Generate → Edit → Refine → Perfect

This agent orchestrates all Stability AI editing operations:
- Inpaint (fix specific areas)
- Outpaint (extend canvas)
- Recolor (change colors while preserving structure)
- Image-to-image (style transfer with reference)
- Remove background
- Upscale (4x quality enhancement)

Handles complex multi-step workflows like:
"Make the text bigger, then change it to blue, then add a shadow"

Session 90 - The Perfect Workflow: Phase 2 "Refine with Editing Tools"
Session 197 - Fixed to call Stability AI APIs directly (not via ImageGenerationService)
"""

import os
import uuid
import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from content.models import ImageHistory
from ai_core.agents.agent_memory_interface import AgentMemoryInterface

logger = logging.getLogger(__name__)


@dataclass
class EditingResult:
    """Result of an editing operation."""
    success: bool
    images: List[str] = None  # List of image URLs/paths
    error_message: str = None
    model_used: str = None

    def __post_init__(self):
        if self.images is None:
            self.images = []


class EditingStep:
    """Represents a single editing operation in a workflow."""

    def __init__(
        self,
        step_id: str,
        operation: str,  # 'inpaint', 'outpaint', 'recolor', 'image_to_image', 'remove_bg', 'upscale'
        parameters: Dict,
        source_image_id: int,
        result_image_id: Optional[int] = None,
        status: str = 'pending',  # 'pending', 'completed', 'failed'
        error: Optional[str] = None
    ):
        self.step_id = step_id
        self.operation = operation
        self.parameters = parameters
        self.source_image_id = source_image_id
        self.result_image_id = result_image_id
        self.status = status
        self.error = error

    def to_dict(self) -> Dict:
        return {
            'step_id': self.step_id,
            'operation': self.operation,
            'parameters': self.parameters,
            'source_image_id': self.source_image_id,
            'result_image_id': self.result_image_id,
            'status': self.status,
            'error': self.error
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'EditingStep':
        return cls(**data)


class EditingOrchestratorAgent:
    """
    Orchestrates multi-step image editing workflows.

    This agent coordinates all Stability AI editing operations,
    enabling complex refinement workflows.
    """

    def __init__(self, user: User, session_id: Optional[str] = None):
        self.user = user
        self.session_id = session_id or f"editing_orch_{user.id}_{uuid.uuid4().hex[:8]}"

        self.memory = AgentMemoryInterface(
            agent_name="EditingOrchestratorAgent",
            user_id=user.id,
            agent_id=self.session_id,
            redis_db=3
        )

        # Session 197: Get API key for direct Stability AI calls
        self.stability_api_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEYS')

        self.memory.log_agent_action(
            action="agent_initialized",
            details={"user_id": user.id}
        )

    # ========================================
    # STABILITY AI API METHODS (Session 197)
    # ========================================

    def _call_stability_api(self, endpoint: str, image_path: str, data: Dict, mask_path: str = None) -> EditingResult:
        """
        Call Stability AI editing API with local image file.

        Args:
            endpoint: API endpoint (e.g., 'edit/inpaint', 'edit/erase')
            image_path: Absolute path to local image file
            data: Form data for the API
            mask_path: Optional path to mask file

        Returns:
            EditingResult with success status and image URL
        """
        if not self.stability_api_key:
            return EditingResult(success=False, error_message="Stability AI API key not configured")

        url = f"https://api.stability.ai/v2beta/stable-image/{endpoint}"

        try:
            # Read the image file
            with open(image_path, 'rb') as f:
                image_content = f.read()

            files = {
                'image': ('image.png', image_content, 'image/png')
            }

            # Add mask if provided
            if mask_path and os.path.exists(mask_path):
                with open(mask_path, 'rb') as f:
                    mask_content = f.read()
                files['mask'] = ('mask.png', mask_content, 'image/png')

            headers = {
                'Authorization': f'Bearer {self.stability_api_key}',
                'Accept': 'image/*'
            }

            # Session 198: Enhanced logging for debugging
            logger.info(f"🎨 Calling Stability AI: {endpoint}")
            logger.info(f"📤 API Request URL: {url}")
            logger.info(f"📤 API Request data: {data}")
            logger.info(f"📤 Image file size: {len(image_content)} bytes")
            if mask_path:
                logger.info(f"📤 Mask file provided: {mask_path}")

            response = requests.post(url, headers=headers, files=files, data=data, timeout=120)

            # Session 198: Enhanced response logging
            logger.info(f"📥 Response status: {response.status_code}")
            logger.info(f"📥 Response size: {len(response.content)} bytes")

            if response.status_code == 200:
                # Session 198: Compare input vs output size to verify modification
                size_diff = len(response.content) - len(image_content)
                size_ratio = len(response.content) / len(image_content) if len(image_content) > 0 else 0
                logger.info(f"📊 Size comparison: input={len(image_content)} bytes, output={len(response.content)} bytes, diff={size_diff}, ratio={size_ratio:.2f}")

                # Save result image
                result_filename = f"generated_images/{self.user.id}/{uuid.uuid4()}.png"
                saved_path = default_storage.save(result_filename, ContentFile(response.content))
                saved_url = default_storage.url(saved_path)

                logger.info(f"✅ Stability AI {endpoint} complete - saved to {saved_path}")

                return EditingResult(
                    success=True,
                    images=[saved_path],
                    model_used='stability-ai'
                )
            else:
                error_msg = response.text
                logger.error(f"❌ Stability AI error: {response.status_code} - {error_msg}")
                return EditingResult(success=False, error_message=f"API error: {error_msg}")

        except Exception as e:
            logger.error(f"❌ Stability API call failed: {str(e)}")
            return EditingResult(success=False, error_message=str(e))

    def _inpaint(self, image_path: str, prompt: str, mask_path: str = None) -> EditingResult:
        """Inpaint areas of an image using Stability AI."""
        data = {
            'prompt': prompt,
            'output_format': 'png'
        }
        return self._call_stability_api('edit/inpaint', image_path, data, mask_path)

    def _erase(self, image_path: str, mask_path: str = None, search_prompt: str = None) -> EditingResult:
        """
        Erase objects from an image using Stability AI.

        If mask_path is provided, uses the erase endpoint with mask.
        If search_prompt is provided (no mask), uses search-and-replace to find and remove objects.
        """
        logger.info(f"🧹 _erase() called: image_path={image_path}, mask_path={mask_path}, search_prompt={search_prompt}")

        if mask_path and os.path.exists(mask_path):
            # Use mask-based erase
            logger.info(f"🧹 Using MASK-BASED erase with mask: {mask_path}")
            data = {
                'output_format': 'png'
            }
            return self._call_stability_api('edit/erase', image_path, data, mask_path)
        elif search_prompt:
            # Session 197/198: No mask - use search-and-replace to find and remove objects
            # This uses AI to identify the object and remove it
            # Session 198 FIX: Stability AI search-and-replace REQUIRES a 'prompt' parameter
            # Session 198 v2: Different prompts work better for different image types:
            # - For photos: "seamless continuation of the surrounding image"
            # - For graphics/logos: "empty space, nothing, blank area matching the background"
            # We'll use a more aggressive removal prompt that works for both
            data = {
                'search_prompt': search_prompt,
                'prompt': 'nothing, empty space, blank area, remove completely',  # Session 198 v2: More aggressive removal
                'output_format': 'png'
            }
            logger.info(f"🧹 Using SEARCH-AND-REPLACE to erase: search_prompt='{search_prompt}'")
            logger.info(f"🧹 API data being sent: {data}")
            return self._call_stability_api('edit/search-and-replace', image_path, data)
        else:
            logger.error("🧹 Erase FAILED: No mask or search_prompt provided!")
            return EditingResult(
                success=False,
                error_message="Erase requires either a mask or a search prompt describing what to remove"
            )

    def _outpaint(self, image_path: str, prompt: str, left: int = 0, right: int = 0, up: int = 0, down: int = 0) -> EditingResult:
        """Outpaint (extend) an image using Stability AI."""
        data = {
            'prompt': prompt,
            'output_format': 'png',
            'left': left,
            'right': right,
            'up': up,
            'down': down
        }
        return self._call_stability_api('edit/outpaint', image_path, data)

    def _remove_background(self, image_path: str) -> EditingResult:
        """Remove background from an image using Stability AI."""
        data = {
            'output_format': 'png'
        }
        return self._call_stability_api('edit/remove-background', image_path, data)

    def _upscale(self, image_path: str, creative: bool = False, prompt: str = None) -> EditingResult:
        """Upscale an image using Stability AI."""
        endpoint = 'upscale/creative' if creative else 'upscale/conservative'
        data = {
            'output_format': 'png'
        }
        if creative and prompt:
            data['prompt'] = prompt
        return self._call_stability_api(endpoint, image_path, data)

    def _search_and_replace(self, image_path: str, search_prompt: str, replace_prompt: str = None) -> EditingResult:
        """Search and replace objects in an image using Stability AI."""
        # Session 198 FIX: Stability AI search-and-replace REQUIRES a 'prompt' parameter
        # For removal (no replace_prompt), use a smart prompt that blends with surroundings
        if replace_prompt:
            effective_prompt = replace_prompt
        else:
            effective_prompt = 'seamless continuation of the surrounding image, clean and smooth'

        data = {
            'search_prompt': search_prompt,
            'prompt': effective_prompt,  # Session 198: Always required
            'output_format': 'png'
        }
        logger.info(f"🔍 Search-and-replace: search='{search_prompt}', prompt='{effective_prompt}'")
        return self._call_stability_api('edit/search-and-replace', image_path, data)

    def _recolor(self, image_path: str, prompt: str, select_prompt: str = None) -> EditingResult:
        """Recolor objects in an image using Stability AI."""
        data = {
            'prompt': prompt,
            'output_format': 'png'
        }
        if select_prompt:
            data['select_prompt'] = select_prompt
        return self._call_stability_api('edit/search-and-recolor', image_path, data)

    def create_editing_workflow(
        self,
        workflow_name: str,
        source_image_id: int,
        steps: List[Dict]
    ) -> Dict:
        """
        Create a multi-step editing workflow.

        Args:
            workflow_name: User-friendly name
            source_image_id: Starting image
            steps: List of editing operations
                [
                    {'operation': 'inpaint', 'parameters': {...}},
                    {'operation': 'recolor', 'parameters': {...}}
                ]

        Returns:
            Dict with workflow info
        """
        try:
            # Verify source image
            source_image = ImageHistory.objects.get(id=source_image_id, user=self.user)

            workflow_id = f"workflow_{uuid.uuid4().hex[:12]}"

            # Store workflow metadata
            workflow_data = {
                'workflow_id': workflow_id,
                'workflow_name': workflow_name,
                'user_id': self.user.id,
                'source_image_id': source_image_id,
                'steps': steps,
                'current_step': 0,
                'status': 'created',
                'created_at': timezone.now().isoformat()
            }

            workflow_key = f"editing_orchestrator:user_{self.user.id}:workflows:{workflow_id}"
            self.memory.redis.set(workflow_key, str(workflow_data))

            # Add to workflow list
            list_key = f"editing_orchestrator:user_{self.user.id}:workflow_list"
            self.memory.redis.sadd(list_key, workflow_id)

            self.memory.log_agent_action(
                action="workflow_created",
                details={
                    'workflow_id': workflow_id,
                    'workflow_name': workflow_name,
                    'steps_count': len(steps)
                }
            )

            return {
                'success': True,
                'workflow_id': workflow_id,
                'workflow_name': workflow_name,
                'total_steps': len(steps),
                'message': f'✅ Editing workflow "{workflow_name}" created with {len(steps)} steps'
            }

        except ImageHistory.DoesNotExist:
            return {'success': False, 'error': 'Source image not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def execute_single_edit(
        self,
        image_id: int,
        operation: str,
        parameters: Dict
    ) -> Dict:
        """
        Execute a single editing operation.

        Args:
            image_id: Source image ID (UUID or numeric index like "213")
            operation: Operation type
            parameters: Operation-specific parameters

        Returns:
            Dict with result
        """
        try:
            # Session 122/197: Support hybrid IDs - numeric IDs like "213" or full UUIDs
            # Resolve numeric ID to UUID if needed
            if isinstance(image_id, str) and image_id.isdigit():
                # User asked for "image 101" - first try sequential_number field
                numeric_index = int(image_id)
                # Session 197: Try sequential_number field first (matches what UI displays)
                source_image = ImageHistory.objects.filter(user=self.user, sequential_number=numeric_index).first()
                if not source_image:
                    # Fallback to positional index for backward compatibility
                    try:
                        source_image = ImageHistory.objects.filter(user=self.user).order_by('created_at')[numeric_index - 1]  # 1-indexed
                    except (IndexError, ImageHistory.DoesNotExist):
                        return {
                            'success': False,
                            'error': f'Image {numeric_index} not found. You have {ImageHistory.objects.filter(user=self.user).count()} images.'
                        }
                if not source_image:
                    return {
                        'success': False,
                        'error': f'Image {numeric_index} not found. You have {ImageHistory.objects.filter(user=self.user).count()} images.'
                    }
            else:
                # Full UUID provided
                try:
                    source_image = ImageHistory.objects.get(id=image_id, user=self.user)
                except ImageHistory.DoesNotExist:
                    return {
                        'success': False,
                        'error': f'Image with ID {image_id} not found.'
                    }

            # Check if it's a placeholder/data URI - can't edit those
            if source_image.file_path.startswith('data:'):
                return {
                    'success': False,
                    'error': f'Cannot edit placeholder image #{image_id}. Please generate a real image first using AI Studio.'
                }

            # Convert relative path to absolute if needed
            import os
            from django.conf import settings

            image_path = source_image.file_path
            if not image_path.startswith(('http://', 'https://', 'data:')):
                # It's a relative path - make it absolute
                # Session 197: Use MEDIA_ROOT not BASE_DIR - database stores paths relative to MEDIA_ROOT
                # e.g., "generated_images/user_id/uuid.png" is stored in "media/generated_images/user_id/uuid.png"
                image_path = os.path.join(settings.MEDIA_ROOT, image_path)

                # Check if file exists
                if not os.path.exists(image_path):
                    return {
                        'success': False,
                        'error': f'Image file not found at: {image_path}. The file may have been moved or deleted.'
                    }

            # Session 197: Execute operation using internal Stability AI methods
            if operation == 'inpaint':
                result = self._inpaint(
                    image_path=image_path,
                    prompt=parameters.get('prompt', ''),
                    mask_path=parameters.get('mask')
                )

            elif operation == 'erase':
                # Session 197: Support both mask-based erase and text-based erase
                result = self._erase(
                    image_path=image_path,
                    mask_path=parameters.get('mask'),
                    search_prompt=parameters.get('search_prompt') or parameters.get('prompt')
                )

            elif operation == 'outpaint':
                result = self._outpaint(
                    image_path=image_path,
                    prompt=parameters.get('prompt', ''),
                    left=parameters.get('left', 0),
                    right=parameters.get('right', 0),
                    up=parameters.get('up', 0),
                    down=parameters.get('down', 0)
                )

            elif operation == 'recolor':
                result = self._recolor(
                    image_path=image_path,
                    prompt=parameters.get('prompt', ''),
                    select_prompt=parameters.get('select_prompt')
                )

            elif operation == 'search_and_replace':
                result = self._search_and_replace(
                    image_path=image_path,
                    search_prompt=parameters.get('search_prompt', ''),
                    replace_prompt=parameters.get('replace_prompt')
                )

            elif operation == 'remove_bg' or operation == 'remove_background':
                result = self._remove_background(
                    image_path=image_path
                )

            elif operation == 'upscale':
                result = self._upscale(
                    image_path=image_path,
                    creative=parameters.get('creative', False),
                    prompt=parameters.get('prompt')
                )

            else:
                return {
                    'success': False,
                    'error': f'Unknown operation: {operation}. Supported: inpaint, erase, outpaint, recolor, search_and_replace, remove_bg, upscale'
                }

            if result.success:
                # Create ImageHistory record for result
                # EditingResult.images is a list, get the first one (file path)
                result_image_path = result.images[0] if result.images else None

                if not result_image_path:
                    return {
                        'success': False,
                        'error': 'No image returned from operation'
                    }

                # Session 197: Inherit project from source image so edited images appear in same project
                result_image = ImageHistory.objects.create(
                    user=self.user,
                    prompt=f"{operation}: {parameters.get('prompt', 'N/A')}",
                    filename=f'{operation}_{uuid.uuid4().hex[:8]}.png',
                    file_path=result_image_path,
                    image_type='generated',  # Use standard type for display compatibility
                    model_used=result.model_used or source_image.model_used,
                    style=source_image.style,
                    image_width=source_image.image_width,
                    image_height=source_image.image_height,
                    project=source_image.project,  # Session 197: Inherit project from source
                    session=source_image.session   # Session 197: Inherit session too
                )

                self.memory.log_agent_action(
                    action="edit_executed",
                    details={
                        'operation': operation,
                        'source_image_id': image_id,
                        'result_image_id': str(result_image.id),
                        'project_id': str(source_image.project.id) if source_image.project else None
                    }
                )

                # Session 197: Return proper URL for frontend display
                result_url = default_storage.url(result_image_path) if result_image_path else None

                return {
                    'success': True,
                    'operation': operation,
                    'result_image_id': str(result_image.id),
                    'result_image_url': result_url,
                    'result_image_path': result_image_path,
                    'project_id': str(source_image.project.id) if source_image.project else None,
                    'message': f'✅ {operation} completed successfully'
                }
            else:
                return {
                    'success': False,
                    'error': result.error_message or 'Operation failed'
                }

        except ImageHistory.DoesNotExist:
            return {'success': False, 'error': 'Source image not found'}
        except Exception as e:
            self.memory.log_agent_action(
                action="execute_edit_error",
                details={'operation': operation, 'error': str(e)}
            )
            return {'success': False, 'error': str(e)}

    def execute_workflow(self, workflow_id: str) -> Dict:
        """
        Execute all steps in a workflow sequentially.

        Args:
            workflow_id: Workflow to execute

        Returns:
            Dict with execution results
        """
        try:
            # Get workflow
            workflow_key = f"editing_orchestrator:user_{self.user.id}:workflows:{workflow_id}"
            workflow_data_raw = self.memory.redis.get(workflow_key)

            if not workflow_data_raw:
                return {'success': False, 'error': 'Workflow not found'}

            import ast
            workflow_data = ast.literal_eval(workflow_data_raw.decode('utf-8'))

            current_image_id = workflow_data['source_image_id']
            results = []

            for idx, step in enumerate(workflow_data['steps']):
                # Execute step
                result = self.execute_single_edit(
                    image_id=current_image_id,
                    operation=step['operation'],
                    parameters=step['parameters']
                )

                results.append(result)

                if result['success']:
                    # Use result as source for next step
                    current_image_id = result['result_image_id']
                else:
                    # Stop on error
                    break

            # Update workflow status
            workflow_data['status'] = 'completed' if all(r['success'] for r in results) else 'failed'
            workflow_data['results'] = results
            workflow_data['final_image_id'] = current_image_id if results and results[-1]['success'] else None

            self.memory.redis.set(workflow_key, str(workflow_data))

            self.memory.log_agent_action(
                action="workflow_executed",
                details={
                    'workflow_id': workflow_id,
                    'total_steps': len(results),
                    'successful_steps': len([r for r in results if r['success']]),
                    'final_image_id': workflow_data['final_image_id']
                }
            )

            return {
                'success': workflow_data['status'] == 'completed',
                'workflow_id': workflow_id,
                'total_steps': len(results),
                'successful_steps': len([r for r in results if r['success']]),
                'final_image_id': workflow_data['final_image_id'],
                'results': results,
                'message': f'✅ Workflow completed! {len([r for r in results if r["success"]])}/{len(results)} steps successful'
            }

        except Exception as e:
            self.memory.log_agent_action(
                action="execute_workflow_error",
                details={'workflow_id': workflow_id, 'error': str(e)}
            )
            return {'success': False, 'error': str(e)}

    def get_state_summary(self) -> Dict:
        """Get agent state summary."""
        try:
            list_key = f"editing_orchestrator:user_{self.user.id}:workflow_list"
            workflow_ids = self.memory.redis.smembers(list_key)

            return {
                'agent_name': 'EditingOrchestratorAgent',
                'session_id': self.session_id,
                'user_id': self.user.id,
                'total_workflows': len(workflow_ids)
            }

        except Exception as e:
            return {
                'agent_name': 'EditingOrchestratorAgent',
                'session_id': self.session_id,
                'user_id': self.user.id,
                'total_workflows': 0,
                'error': str(e)
            }
