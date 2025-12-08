"""
Register All Creative Workflow Agents - Session 94

This management command registers all 8 creative workflow agents in the database,
ensuring they're connected and ready for orchestration.

Agents registered:
1. CreativeDirectorAgent - Multi-option generation with learning
2. WorkflowCoordinatorAgent - Master orchestrator
3. TemplateManagerAgent - Save and reuse perfect results
4. BrandStyleAgent - FLUX LoRA brand training
5. VersionControlAgent - Generation history tracking
6. EditingOrchestratorAgent - Multi-step image editing
7. IterationAgent - Intelligent refinement
8. ReferenceLibraryAgent - Reference image management

Usage:
    python manage.py register_creative_agents
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models.agents_registry import UnifiedAgentTemplate, AgentSpecialization

User = get_user_model()


class Command(BaseCommand):
    help = 'Register all creative workflow agents in the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🎨 Registering Creative Workflow Agents...'))

        agents_to_register = [
            {
                'name': 'CreativeDirectorAgent',
                'display_name': 'Creative Director (AI Learning)',
                'description': 'AI-powered multi-option image generation with taste learning. Generates 3-5 creative options, learns from user choices, and gets smarter over time. 69 style presets available.',
                'specialization': AgentSpecialization.CREATIVE,
                'capabilities': [
                    'multi_option_generation',
                    'taste_learning',
                    'style_recommendation',
                    'preference_tracking',
                    'smart_parameter_selection'
                ],
                'routing_keywords': [
                    'generate', 'create', 'image', 'options', 'creative',
                    'logo', 'banner', 'design', 'art', 'illustration',
                    'multiple options', 'give me choices', 'show me options'
                ],
                'required_tools': ['stability_ai'],
                'system_prompt': (
                    "You are the Creative Director Agent. You specialize in generating multiple "
                    "creative options for users to choose from, then learning their taste preferences. "
                    "You maintain a learning system that tracks user choices and generates increasingly "
                    "personalized results over time. You have access to 69 style presets across "
                    "photography, digital art, animation, and more."
                ),
                'metadata': {
                    'learning_stages': ['new', 'learning', 'patterns', 'knows_taste'],
                    'min_choices_for_recommendations': 5,
                    'style_count': 69
                }
            },
            {
                'name': 'WorkflowCoordinatorAgent',
                'display_name': 'Workflow Coordinator (Master Orchestrator)',
                'description': 'Master orchestrator that coordinates all creative workflow agents to execute complete end-to-end workflows from simple voice commands. Coordinates 7 specialized agents.',
                'specialization': AgentSpecialization.ORCHESTRATION,
                'capabilities': [
                    'workflow_orchestration',
                    'agent_coordination',
                    'multi_step_execution',
                    'state_management',
                    'error_recovery'
                ],
                'routing_keywords': [
                    'workflow', 'complete', 'full process', 'end-to-end',
                    'orchestrate', 'coordinate', 'automated workflow',
                    'save as template', 'train brand style', 'complete package'
                ],
                'required_tools': ['all_creative_agents'],
                'system_prompt': (
                    "You are the Workflow Coordinator Agent. You are the MASTER ORCHESTRATOR that "
                    "coordinates all other creative agents to execute complete workflows. You understand "
                    "how to break down complex requests into multi-step workflows and coordinate the "
                    "right agents in the right sequence to achieve perfect results."
                ),
                'metadata': {
                    'managed_agents': 7,
                    'available_workflows': [
                        'generate_with_options',
                        'save_as_template',
                        'train_brand_style',
                        'refine_and_perfect',
                        'complete_brand_package'
                    ]
                }
            },
            {
                'name': 'TemplateManagerAgent',
                'display_name': 'Template Manager',
                'description': 'Saves approved creative results as reusable templates with all parameters for exact reproduction. Philosophy: Perfect once → Save forever → Use everywhere.',
                'specialization': AgentSpecialization.CONTENT,
                'capabilities': [
                    'template_saving',
                    'parameter_preservation',
                    'template_library_management',
                    'exact_reproduction',
                    'template_tagging'
                ],
                'routing_keywords': [
                    'save', 'template', 'save as template', 'reuse', 'library',
                    'save this', 'remember this', 'use again', 'brand template'
                ],
                'required_tools': ['redis_memory'],
                'system_prompt': (
                    "You are the Template Manager Agent. You specialize in saving perfect creative "
                    "results as reusable templates. You preserve ALL parameters (seed, prompt, model, "
                    "style, dimensions) needed for exact reproduction. You manage the template library "
                    "with tags and notes for easy organization."
                ),
                'metadata': {
                    'storage_backend': 'redis',
                    'supports_exact_reproduction': True
                }
            },
            {
                'name': 'BrandStyleAgent',
                'display_name': 'Brand Style Trainer',
                'description': 'Trains FLUX LoRA models on complete brand aesthetics (logos, colors, compositions, lighting). Train once → Use trigger word forever → Perfect consistency.',
                'specialization': AgentSpecialization.CREATIVE,
                'capabilities': [
                    'flux_lora_training',
                    'brand_aesthetic_learning',
                    'trigger_word_creation',
                    'visual_identity_training',
                    'consistency_enforcement'
                ],
                'routing_keywords': [
                    'train', 'brand', 'style', 'flux', 'lora', 'consistency',
                    'train on brand', 'learn my style', 'brand training',
                    'visual identity', 'trigger word'
                ],
                'required_tools': ['replicate', 'flux_lora'],
                'system_prompt': (
                    "You are the Brand Style Agent. You specialize in training FLUX LoRA models on "
                    "complete brand aesthetics. Unlike character training (one character, multiple angles), "
                    "you train on entire visual identities (logos, colors, compositions, lighting, mood). "
                    "You create trigger words that enable perfect brand consistency across all future content."
                ),
                'metadata': {
                    'min_training_images': 5,
                    'max_training_images': 10,
                    'training_platform': 'replicate'
                }
            },
            {
                'name': 'VersionControlAgent',
                'display_name': 'Version Control',
                'description': 'Tracks complete generation history with full parameter preservation. Enables rollback, comparison, and version management for all creative work.',
                'specialization': AgentSpecialization.CONTENT,
                'capabilities': [
                    'version_tracking',
                    'parameter_history',
                    'rollback_support',
                    'version_comparison',
                    'generation_lineage'
                ],
                'routing_keywords': [
                    'version', 'history', 'rollback', 'previous', 'compare',
                    'version control', 'track changes', 'show history'
                ],
                'required_tools': ['database', 'redis_memory'],
                'system_prompt': (
                    "You are the Version Control Agent. You track every generation with complete "
                    "parameter history, enabling users to see exactly how each result was created. "
                    "You support rollback to previous versions and side-by-side comparison of different "
                    "versions. You maintain the complete lineage of creative work."
                ),
                'metadata': {
                    'auto_tracking': True,
                    'supports_comparison': True
                }
            },
            {
                'name': 'EditingOrchestratorAgent',
                'display_name': 'Editing Orchestrator',
                'description': 'Coordinates multi-step image editing workflows using Stability AI editing operations (inpaint, outpaint, recolor, image-to-image, remove bg, upscale).',
                'specialization': AgentSpecialization.CREATIVE,
                'capabilities': [
                    'inpaint',
                    'outpaint',
                    'recolor',
                    'image_to_image',
                    'remove_background',
                    'upscale_4x',
                    'multi_step_editing'
                ],
                'routing_keywords': [
                    'edit', 'inpaint', 'outpaint', 'recolor', 'fix', 'change',
                    'remove background', 'upscale', 'enhance', 'refine',
                    'make bigger', 'change color', 'extend'
                ],
                'required_tools': ['stability_ai_editing'],
                'system_prompt': (
                    "You are the Editing Orchestrator Agent. You coordinate multi-step image editing "
                    "workflows using all Stability AI editing operations. You can execute complex "
                    "refinement sequences like 'make text bigger, then blue, then add shadow'. You "
                    "track editing history and enable iterative refinement."
                ),
                'metadata': {
                    'available_operations': [
                        'inpaint', 'outpaint', 'recolor',
                        'image_to_image', 'remove_bg', 'upscale'
                    ],
                    'supports_multi_step': True
                }
            },
            {
                'name': 'IterationAgent',
                'display_name': 'Iteration Agent',
                'description': 'Intelligent iteration and refinement system. Analyzes what worked/didn\'t work, suggests targeted improvements, and learns from user feedback.',
                'specialization': AgentSpecialization.CREATIVE,
                'capabilities': [
                    'iteration_analysis',
                    'improvement_suggestions',
                    'feedback_learning',
                    'iteration_history',
                    'refinement_tracking'
                ],
                'routing_keywords': [
                    'iterate', 'refine', 'improve', 'make better', 'try again',
                    'iteration', 'refinement', 'enhancement', 'optimize'
                ],
                'required_tools': ['analysis', 'redis_memory'],
                'system_prompt': (
                    "You are the Iteration Agent. You specialize in intelligent iteration and refinement. "
                    "You analyze previous generations to understand what worked and what didn't, then "
                    "suggest targeted improvements. You learn from user feedback to make better suggestions "
                    "over time. You track iteration history to show progress."
                ),
                'metadata': {
                    'learns_from_feedback': True,
                    'tracks_history': True
                }
            },
            {
                'name': 'ReferenceLibraryAgent',
                'display_name': 'Reference Library Manager',
                'description': 'Manages reference image library for consistent results. Stores references by category, auto-suggests relevant references, and builds visual style guides.',
                'specialization': AgentSpecialization.CONTENT,
                'capabilities': [
                    'reference_storage',
                    'category_management',
                    'auto_suggestion',
                    'style_guide_creation',
                    'reference_based_generation'
                ],
                'routing_keywords': [
                    'reference', 'library', 'style guide', 'examples',
                    'reference images', 'inspiration', 'similar to',
                    'based on', 'like this'
                ],
                'required_tools': ['database', 'file_storage'],
                'system_prompt': (
                    "You are the Reference Library Agent. You manage a library of reference images "
                    "that ensure consistent creative results. You categorize references, suggest relevant "
                    "ones for new projects, and help build visual style guides. You enable reference-based "
                    "generation for better creative control."
                ),
                'metadata': {
                    'supports_categories': True,
                    'auto_suggestion': True
                }
            }
        ]

        registered_count = 0
        updated_count = 0

        for agent_data in agents_to_register:
            agent_name = agent_data['name']

            # Check if agent already exists
            agent, created = UnifiedAgentTemplate.objects.update_or_create(
                name=agent_name,
                defaults={
                    'display_name': agent_data['display_name'],
                    'description': agent_data['description'],
                    'specialization': agent_data['specialization'],
                    'capabilities': agent_data['capabilities'],
                    'routing_keywords': agent_data['routing_keywords'],
                    'required_tools': agent_data['required_tools'],
                    'system_prompt': agent_data['system_prompt'],
                    'metadata': agent_data['metadata'],
                    'is_active': True,
                    'llm_provider': 'openai',
                    'llm_model': 'gpt-5-mini'
                }
            )

            if created:
                registered_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Registered: {agent_name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'🔄 Updated: {agent_name}')
                )

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✅ Registration Complete!'))
        self.stdout.write(f'  New agents registered: {registered_count}')
        self.stdout.write(f'  Existing agents updated: {updated_count}')
        self.stdout.write(f'  Total creative agents: {registered_count + updated_count}')

        # Verify all agents are active
        total_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()
        self.stdout.write(f'  Total active agents in system: {total_agents}')

        self.stdout.write('\n' + self.style.SUCCESS('🎉 All creative workflow agents are now registered and ready!'))
