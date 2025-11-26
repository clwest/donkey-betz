"""
IterationAgent - Natural Language Image Refinement

Philosophy: "Make it bigger" → AI understands → Perfect result

This agent handles natural language iteration requests like:
- "Make the text bigger"
- "Change it to dark blue"
- "Add more contrast"
- "Make the character smile more"

Translates human intent into precise editing operations.

Session 90 - The Perfect Workflow: Iteration & Refinement
"""

import uuid
from typing import Dict, Optional

from django.contrib.auth.models import User

from ai_core.agents.agent_memory_interface import AgentMemoryInterface
# Session 206: EditingOrchestratorAgent was merged into ImageAgent in Phase 1
from agents.image_agent import ImageAgent as EditingOrchestratorAgent


class IterationAgent:
    """
    Handles natural language iteration requests.

    Workflow:
    1. User: "Make the text bigger and darker"
    2. IterationAgent: Parses request → determines operations
    3. Creates editing workflow: [inpaint text area, recolor darker]
    4. Delegates to EditingOrchestratorAgent
    5. Returns refined result

    This enables conversational refinement!
    """

    def __init__(self, user: User, session_id: Optional[str] = None):
        self.user = user
        self.session_id = session_id or f"iteration_{user.id}_{uuid.uuid4().hex[:8]}"

        self.memory = AgentMemoryInterface(
            agent_name="IterationAgent",
            user_id=user.id,
            agent_id=self.session_id,
            redis_db=3
        )

        # Editing orchestrator for executing operations
        self.editing_orchestrator = EditingOrchestratorAgent(user=user)

        self.memory.log_agent_action(
            action="agent_initialized",
            details={"user_id": user.id}
        )

    def refine_image(
        self,
        image_id: str,  # Session 95: Changed to str for UUID support
        refinement_request: str
    ) -> Dict:
        """
        Refine an image based on natural language request.

        Args:
            image_id: Image to refine
            refinement_request: Natural language description
                Examples:
                - "Make the text bigger"
                - "Change background to blue"
                - "Add more contrast"

        Returns:
            Dict with refinement result
        """
        try:
            # Parse refinement request into operations
            # (In production, this would use GPT-5 to parse the request)
            operations = self._parse_refinement_request(refinement_request)

            if not operations:
                return {
                    'success': False,
                    'error': 'Could not understand refinement request'
                }

            # Execute single operation or create workflow
            if len(operations) == 1:
                # Single operation - execute directly
                result = self.editing_orchestrator.execute_single_edit(
                    image_id=image_id,
                    operation=operations[0]['operation'],
                    parameters=operations[0]['parameters']
                )

                self.memory.log_agent_action(
                    action="refinement_executed",
                    details={
                        'image_id': image_id,
                        'request': refinement_request,
                        'operation': operations[0]['operation']
                    }
                )

                return result

            else:
                # Multiple operations - create workflow
                workflow_result = self.editing_orchestrator.create_editing_workflow(
                    workflow_name=f"Refine: {refinement_request}",
                    source_image_id=image_id,
                    steps=operations
                )

                if workflow_result['success']:
                    # Execute workflow
                    execution_result = self.editing_orchestrator.execute_workflow(
                        workflow_result['workflow_id']
                    )

                    self.memory.log_agent_action(
                        action="refinement_workflow_executed",
                        details={
                            'image_id': image_id,
                            'request': refinement_request,
                            'workflow_id': workflow_result['workflow_id'],
                            'operations_count': len(operations)
                        }
                    )

                    return execution_result
                else:
                    return workflow_result

        except Exception as e:
            self.memory.log_agent_action(
                action="refine_image_error",
                details={'image_id': image_id, 'error': str(e)}
            )
            return {'success': False, 'error': str(e)}

    def _parse_refinement_request(self, request: str) -> list:
        """
        Parse natural language refinement request into operations.

        This is a simplified version. In production, this would use
        GPT-5 function calling to parse complex requests.

        Args:
            request: Natural language request

        Returns:
            List of operation dictionaries
        """
        request_lower = request.lower()
        operations = []

        # Simple keyword matching (production would use GPT-5)
        if 'bigger' in request_lower or 'larger' in request_lower or 'size' in request_lower:
            # Assume scaling operation
            operations.append({
                'operation': 'upscale',
                'parameters': {}
            })

        # Session 123: Support brightness/darkness adjustments
        if 'darker' in request_lower or 'dark' in request_lower or 'brightness' in request_lower or 'lighter' in request_lower or 'brighter' in request_lower:
            # Use image_to_image for brightness adjustments
            operations.append({
                'operation': 'image_to_image',
                'parameters': {'prompt': request, 'strength': 0.65}
            })

        elif 'color' in request_lower or 'recolor' in request_lower:
            # Extract color if mentioned - use image_to_image
            operations.append({
                'operation': 'image_to_image',
                'parameters': {'prompt': request, 'strength': 0.7}
            })

        elif 'background' in request_lower and 'remove' in request_lower:
            operations.append({
                'operation': 'remove_bg',
                'parameters': {}
            })

        elif 'style' in request_lower or 'look like' in request_lower:
            # Style transfer operation
            operations.append({
                'operation': 'image_to_image',
                'parameters': {'prompt': request, 'strength': 0.7}
            })

        # If no specific keywords matched, use image_to_image as default
        if not operations:
            operations.append({
                'operation': 'image_to_image',
                'parameters': {'prompt': request, 'strength': 0.65}
            })

        return operations

    def get_state_summary(self) -> Dict:
        """Get agent state summary."""
        return {
            'agent_name': 'IterationAgent',
            'session_id': self.session_id,
            'user_id': self.user.id,
            'available_operations': [
                'upscale', 'recolor', 'remove_bg',
                'image_to_image', 'inpaint', 'outpaint'
            ]
        }
