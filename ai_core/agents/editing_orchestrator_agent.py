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
"""

import uuid
from typing import Dict, List, Optional
from datetime import datetime

from django.contrib.auth.models import User
from django.utils import timezone

from content.models import ImageHistory
from content.image_generation import ImageGenerationService
from ai_core.agents.agent_memory_interface import AgentMemoryInterface


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

        self.stability = ImageGenerationService()

        self.memory.log_agent_action(
            action="agent_initialized",
            details={"user_id": user.id}
        )

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
            # Session 122: Support hybrid IDs - numeric IDs like "213" or full UUIDs
            # Resolve numeric ID to UUID if needed
            if isinstance(image_id, str) and image_id.isdigit():
                # User asked for "image 213" - get the 213th image chronologically
                numeric_index = int(image_id)
                try:
                    source_image = ImageHistory.objects.filter(user=self.user).order_by('created_at')[numeric_index - 1]  # 1-indexed
                except (IndexError, ImageHistory.DoesNotExist):
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

            # Execute operation based on type
            if operation == 'inpaint':
                result = self.stability.inpaint(
                    image_url=source_image.image_url,
                    prompt=parameters.get('prompt'),
                    mask=parameters.get('mask'),
                    **{k: v for k, v in parameters.items() if k not in ['prompt', 'mask']}
                )

            elif operation == 'outpaint':
                result = self.stability.outpaint(
                    image_url=source_image.image_url,
                    **parameters
                )

            elif operation == 'recolor':
                result = self.stability.recolor(
                    image_url=source_image.image_url,
                    prompt=parameters.get('prompt'),
                    **{k: v for k, v in parameters.items() if k != 'prompt'}
                )

            elif operation == 'image_to_image':
                result = self.stability.image_to_image(
                    image_url=source_image.image_url,
                    prompt=parameters.get('prompt'),
                    strength=parameters.get('strength', 0.65),
                    **{k: v for k, v in parameters.items() if k not in ['prompt', 'strength']}
                )

            elif operation == 'remove_bg':
                result = self.stability.remove_background(
                    image_url=source_image.image_url
                )

            elif operation == 'upscale':
                result = self.stability.upscale(
                    image_url=source_image.image_url,
                    **parameters
                )

            else:
                return {
                    'success': False,
                    'error': f'Unknown operation: {operation}'
                }

            if result.get('success'):
                # Create ImageHistory record for result
                result_image = ImageHistory.objects.create(
                    user=self.user,
                    prompt=f"{operation}: {parameters.get('prompt', 'N/A')}",
                    image_url=result['image_url'],
                    model=source_image.model,
                    style=source_image.style,
                    width=source_image.width,
                    height=source_image.height
                )

                self.memory.log_agent_action(
                    action="edit_executed",
                    details={
                        'operation': operation,
                        'source_image_id': image_id,
                        'result_image_id': result_image.id
                    }
                )

                return {
                    'success': True,
                    'operation': operation,
                    'result_image_id': result_image.id,
                    'result_image_url': result['image_url'],
                    'message': f'✅ {operation} completed successfully'
                }
            else:
                return result

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
