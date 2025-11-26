"""
WorkflowCoordinatorAgent - Master Agent Orchestrator

Philosophy: One command → Complete workflow → Perfect result

This is the MASTER AGENT that coordinates all other agents to execute
complete end-to-end workflows.

Example workflow:
User: "Create a coffee shop logo and save it as a brand template"

WorkflowCoordinatorAgent orchestrates:
1. CreativeDirectorAgent.generate_options() → 3 options
2. User picks favorite
3. CreativeDirectorAgent.record_choice() → learns taste
4. TemplateManagerAgent.save_as_template() → saved forever
5. VersionControlAgent.track_generation() → full history
6. BrandStyleAgent.create_brand_style() → optional FLUX training

ALL OF THIS FROM ONE VOICE COMMAND!

Session 90 - The Perfect Workflow: Complete Orchestration
"""

import uuid
from typing import Dict, List, Optional
from datetime import datetime

from django.contrib.auth.models import User
from django.utils import timezone

from ai_core.agents.agent_memory_interface import AgentMemoryInterface
from ai_core.agents.creative_director_agent import CreativeDirectorAgent
from ai_core.agents.template_manager_agent import TemplateManagerAgent
from ai_core.agents.version_control_agent import VersionControlAgent
from ai_core.agents.brand_style_agent import BrandStyleAgent
from ai_core.agents.reference_library_agent import ReferenceLibraryAgent
# Session 206: EditingOrchestratorAgent was merged into ImageAgent in Phase 1
from agents.image_agent import ImageAgent as EditingOrchestratorAgent
from ai_core.agents.iteration_agent import IterationAgent


class WorkflowCoordinatorAgent:
    """
    Master orchestrator for complete creative workflows.

    This agent coordinates ALL other agents to execute complex,
    multi-step workflows from simple voice commands.

    Available workflows:
    1. "Generate with options" - CreativeDirector multi-generation
    2. "Save as template" - Template creation + version tracking
    3. "Train brand style" - FLUX LoRA training on aesthetics
    4. "Refine and perfect" - Iteration + editing + saving
    5. "Complete brand package" - Logo + style training + reference library

    This is what makes the platform MAGICAL!
    """

    def __init__(self, user: User, session_id: Optional[str] = None):
        self.user = user
        self.session_id = session_id or f"workflow_coord_{user.id}_{uuid.uuid4().hex[:8]}"

        self.memory = AgentMemoryInterface(
            agent_name="workflow_coordinator",
            user_id=user.id,
            agent_id=self.session_id,
            redis_db=3
        )

        # Initialize all sub-agents
        self.creative_director = CreativeDirectorAgent(user=user)
        self.template_manager = TemplateManagerAgent(user=user)
        self.version_control = VersionControlAgent(user=user)
        self.brand_style = BrandStyleAgent(user=user)
        self.reference_library = ReferenceLibraryAgent(user=user)
        self.editing_orchestrator = EditingOrchestratorAgent(user=user)
        self.iteration_agent = IterationAgent(user=user)

        # TODO: Add logging once AgentMemoryInterface supports it
        # self.memory.log_agent_action(
        #     action="coordinator_initialized",
        #     details={
        #         "user_id": user.id,
        #         "agents_initialized": 7
        #     }
        # )

    def execute_generate_with_options_workflow(
        self,
        prompt: str,
        count: int = 3,
        style: Optional[str] = None,
        model: Optional[str] = None,
        session = None  # Session 96: For content linking
    ) -> Dict:
        """
        Execute "Generate with Options" workflow.

        Steps:
        1. Generate multiple options (CreativeDirector)
        2. Track all options (VersionControl)
        3. Return options for user selection

        Args:
            prompt: Generation prompt
            count: Number of options
            style: Optional style
            model: Optional model
            session: AISession for linking generated content (Session 96)

        Returns:
            Dict with options and workflow info
        """
        try:
            # Step 1: Generate options
            generation_result = self.creative_director.generate_options(
                prompt=prompt,
                count=count,
                style=style,
                model=model,
                session=session  # Session 96: Pass session for linking
            )

            if not generation_result.get('options'):
                return {
                    'success': False,
                    'error': 'Failed to generate options',
                    'details': generation_result
                }

            # Step 2: Track all options in version control
            tracked_versions = []
            for option in generation_result['options']:
                version_result = self.version_control.track_generation(
                    image_id=option['id']
                )
                if version_result['success']:
                    tracked_versions.append(version_result['version_id'])

            # self.memory.log_agent_action(
            #     action="generate_with_options_workflow_completed",
            #     details={
            #         'prompt': prompt,
            #         'options_count': len(generation_result['options']),
            #         'tracked_versions': len(tracked_versions)
            #     }
            # )

            result = {
                'success': True,
                'workflow': 'generate_with_options',
                'batch_id': generation_result['batch_id'],
                'options': generation_result['options'],
                'learning_message': generation_result['learning_message'],
                'tracked_versions': tracked_versions,
                'message': f'✅ Generated {len(generation_result["options"])} options! Pick your favorite to help AI learn your taste.'
            }

            # Session 96: Pass through project creation info if provided
            if 'project_created' in generation_result:
                result['project_created'] = generation_result['project_created']
                result['project_id'] = generation_result.get('project_id')
                result['project_name'] = generation_result.get('project_name')

            return result

        except Exception as e:
            # self.memory.log_agent_action(
                # action="generate_with_options_workflow_error",
                # details={'error': str(e)}
            # )
            return {'success': False, 'error': str(e)}

    def execute_save_as_template_workflow(
        self,
        image_id: str,  # Session 95: Changed to str for UUID support
        template_name: str,
        tags: List[str] = None,
        also_add_to_references: bool = True
    ) -> Dict:
        """
        Execute "Save as Template" workflow.

        Steps:
        1. Record choice (CreativeDirector learns)
        2. Save as template (TemplateManager)
        3. Mark version (VersionControl)
        4. Optionally add to reference library

        Args:
            image_id: Image to save
            template_name: Name for template
            tags: Tags for organization
            also_add_to_references: Add to reference library?

        Returns:
            Dict with workflow results
        """
        try:
            results = {}

            # Step 1: Record choice (AI learns)
            choice_result = self.creative_director.record_choice(image_id)
            results['choice_recorded'] = choice_result

            # Step 2: Save as template
            template_result = self.template_manager.save_as_template(
                image_id=image_id,
                template_name=template_name,
                tags=tags or []
            )
            results['template_saved'] = template_result

            if not template_result['success']:
                return {
                    'success': False,
                    'error': 'Failed to save template',
                    'details': results
                }

            # Step 3: Mark version as used for template
            # Find the version for this image
            versions = self.version_control.list_versions()
            matching_version = next(
                (v for v in versions if v['image_id'] == image_id),
                None
            )

            if matching_version:
                mark_result = self.version_control.mark_used_for_template(
                    matching_version['version_id']
                )
                results['version_marked'] = mark_result

            # Step 4: Optionally add to reference library
            if also_add_to_references:
                ref_result = self.reference_library.add_reference(
                    name=template_name,
                    image_id=image_id,
                    tags=tags or []
                )
                results['reference_added'] = ref_result

            # self.memory.log_agent_action(
            #     action="save_as_template_workflow_completed",
            #     details={
            #         'image_id': image_id,
            #         'template_name': template_name,
            #         'template_id': template_result.get('template_id'),
            #         'added_to_references': also_add_to_references
            #     }
            # )

            return {
                'success': True,
                'workflow': 'save_as_template',
                'template_id': template_result['template_id'],
                'template_name': template_name,
                'results': results,
                'message': f'✅ Template "{template_name}" saved! You can now reproduce this style anytime. AI also learned your taste!'
            }

        except Exception as e:
            # self.memory.log_agent_action(
                # action="save_as_template_workflow_error",
                # details={'error': str(e)}
            # )
            return {'success': False, 'error': str(e)}

    def execute_train_brand_style_workflow(
        self,
        brand_name: str,
        image_ids: List[str],  # Session 95: Changed to List[str] for UUID support
        auto_submit: bool = False
    ) -> Dict:
        """
        Execute "Train Brand Style" workflow.

        Steps:
        1. Create brand style (BrandStyleAgent)
        2. Optionally submit for training
        3. Track in version control

        Args:
            brand_name: Brand name
            image_ids: Images representing brand aesthetic
            auto_submit: Auto-submit for training?

        Returns:
            Dict with workflow results
        """
        try:
            # Step 1: Create brand style
            brand_result = self.brand_style.create_brand_style(
                brand_name=brand_name,
                image_ids=image_ids
            )

            if not brand_result['success']:
                return brand_result

            # Step 2: Auto-submit if requested
            if auto_submit:
                training_result = self.brand_style.submit_training(
                    brand_result['character_id']
                )
                brand_result['training_submitted'] = training_result

            # self.memory.log_agent_action(
            #     action="train_brand_style_workflow_completed",
            #     details={
            #         'brand_name': brand_name,
            #         'character_id': brand_result['character_id'],
            #         'trigger_word': brand_result['trigger_word'],
            #         'auto_submitted': auto_submit
            #     }
            # )

            return {
                'success': True,
                'workflow': 'train_brand_style',
                'character_id': brand_result['character_id'],
                'trigger_word': brand_result['trigger_word'],
                'training_submitted': auto_submit,
                'message': f'✅ Brand style "{brand_name}" created! {"Training started (30-60 min)." if auto_submit else "Ready to train when you are."}'
            }

        except Exception as e:
            # self.memory.log_agent_action(
                # action="train_brand_style_workflow_error",
                # details={'error': str(e)}
            # )
            return {'success': False, 'error': str(e)}

    def execute_refine_and_perfect_workflow(
        self,
        image_id: int,
        refinement_request: str,
        save_as_template: bool = False,
        template_name: Optional[str] = None
    ) -> Dict:
        """
        Execute "Refine and Perfect" workflow.

        Steps:
        1. Refine image (IterationAgent)
        2. Optionally save refined result as template

        Args:
            image_id: Image to refine
            refinement_request: Natural language refinement
            save_as_template: Save result as template?
            template_name: Template name if saving

        Returns:
            Dict with workflow results
        """
        try:
            # Step 1: Refine image
            refinement_result = self.iteration_agent.refine_image(
                image_id=image_id,
                refinement_request=refinement_request
            )

            if not refinement_result['success']:
                return refinement_result

            # Step 2: Optionally save as template
            if save_as_template and template_name:
                refined_image_id = refinement_result.get('result_image_id') or refinement_result.get('final_image_id')

                if refined_image_id:
                    template_result = self.execute_save_as_template_workflow(
                        image_id=refined_image_id,
                        template_name=template_name
                    )
                    refinement_result['template_saved'] = template_result

            # self.memory.log_agent_action(
            #     action="refine_and_perfect_workflow_completed",
            #     details={
            #         'image_id': image_id,
            #         'refinement_request': refinement_request,
            #         'saved_as_template': save_as_template
            #     }
            # )

            return {
                'success': True,
                'workflow': 'refine_and_perfect',
                'refinement_result': refinement_result,
                'template_saved': save_as_template,
                'message': f'✅ Image refined! {" and saved as template" if save_as_template else ""}'
            }

        except Exception as e:
            # self.memory.log_agent_action(
                # action="refine_and_perfect_workflow_error",
                # details={'error': str(e)}
            # )
            return {'success': False, 'error': str(e)}

    def get_state_summary(self) -> Dict:
        """Get complete ecosystem state."""
        return {
            'agent_name': 'WorkflowCoordinatorAgent',
            'session_id': self.session_id,
            'user_id': self.user.id,
            'sub_agents': {
                'creative_director': self.creative_director.get_state_summary(),
                'template_manager': self.template_manager.get_state_summary(),
                'version_control': self.version_control.get_state_summary(),
                'brand_style': self.brand_style.get_state_summary(),
                'reference_library': self.reference_library.get_state_summary()
            },
            'available_workflows': [
                'generate_with_options',
                'save_as_template',
                'train_brand_style',
                'refine_and_perfect'
            ]
        }
