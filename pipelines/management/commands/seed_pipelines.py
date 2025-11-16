"""
Seed initial pipeline templates

Session 109 - Creative Pipelines v1
"""

from django.core.management.base import BaseCommand
from pipelines.models import CreativePipelineTemplate


class Command(BaseCommand):
    help = 'Seed initial creative pipeline templates'

    def handle(self, *args, **options):
        self.stdout.write('Seeding pipeline templates...')

        templates = [
            {
                'slug': 'idea_to_image_set',
                'name': 'Idea to Image Set',
                'description': (
                    'Transform a creative idea into a set of 3-5 detailed AI-generated images. '
                    'Perfect for brainstorming visual concepts, creating social media content, '
                    'or exploring different artistic directions.'
                ),
                'config': {
                    'steps': [
                        {
                            'id': 1,
                            'name': 'Expand Idea',
                            'type': 'gpt_expansion',
                            'description': 'Use GPT to expand user idea into detailed image prompts',
                            'tool': 'openai_gpt',
                            'params': {
                                'num_prompts': 5,
                                'creativity': 'high'
                            }
                        },
                        {
                            'id': 2,
                            'name': 'Generate Images',
                            'type': 'image_generation',
                            'description': 'Generate images from expanded prompts',
                            'tool': 'stability_ai',
                            'params': {
                                'model': 'stable-diffusion-3',
                                'aspect_ratio': '1:1'
                            }
                        },
                        {
                            'id': 3,
                            'name': 'Save to Session',
                            'type': 'save_assets',
                            'description': 'Attach generated images to session/project',
                            'tool': 'internal'
                        }
                    ],
                    'inputs': {
                        'idea': {'type': 'string', 'required': True, 'label': 'Describe your idea'},
                        'num_images': {'type': 'int', 'default': 5, 'min': 3, 'max': 10, 'label': 'Number of images'}
                    },
                    'outputs': {
                        'images': {'type': 'array', 'description': 'Generated image URLs and metadata'}
                    }
                }
            },
            {
                'slug': 'idea_to_promo_video',
                'name': 'Idea to Promo Video',
                'description': (
                    'Create a professional promo video from your idea. This pipeline generates '
                    'a script, creates keyframe images, and assembles them into a compelling video '
                    'perfect for product launches, event promotions, or social media campaigns.'
                ),
                'config': {
                    'steps': [
                        {
                            'id': 1,
                            'name': 'Create Script',
                            'type': 'gpt_script',
                            'description': 'Generate script and shot list from idea',
                            'tool': 'openai_gpt',
                            'params': {
                                'duration_target': 30,
                                'tone': 'professional'
                            }
                        },
                        {
                            'id': 2,
                            'name': 'Generate Keyframes',
                            'type': 'image_generation',
                            'description': 'Create visual keyframes for each shot',
                            'tool': 'stability_ai',
                            'params': {
                                'num_keyframes': 8,
                                'aspect_ratio': '16:9'
                            }
                        },
                        {
                            'id': 3,
                            'name': 'Create Video',
                            'type': 'video_creation',
                            'description': 'Assemble keyframes into video',
                            'tool': 'runway_ml',
                            'params': {
                                'duration_per_frame': 4,
                                'transitions': 'smooth'
                            }
                        },
                        {
                            'id': 4,
                            'name': 'Save Results',
                            'type': 'save_assets',
                            'description': 'Save video and supporting assets',
                            'tool': 'internal'
                        }
                    ],
                    'inputs': {
                        'idea': {'type': 'string', 'required': True, 'label': 'Promo concept'},
                        'duration': {'type': 'int', 'default': 30, 'min': 15, 'max': 60, 'label': 'Target duration (seconds)'}
                    },
                    'outputs': {
                        'video_url': {'type': 'string', 'description': 'Final video URL'},
                        'keyframes': {'type': 'array', 'description': 'Supporting keyframe images'},
                        'script': {'type': 'string', 'description': 'Generated script'}
                    }
                }
            },
            {
                'slug': 'images_to_minifigs',
                'name': 'Images → 3D Mini-Figs',
                'description': (
                    'Transform 1-4 character images into 3D-printable mini-fig assets. '
                    'Perfect for creating custom game pieces, collectible figures, or '
                    'desk decorations from your AI-generated characters. '
                    '(v1: Placeholder 3D files; v2+: Real 3D generation)'
                ),
                'config': {
                    'steps': [
                        {
                            'id': 1,
                            'name': 'Create 3D Mini-Figs',
                            'type': 'minifig_creation',
                            'description': 'Generate 3D-printable files from character images',
                            'tool': 'placeholder_3d_provider',  # v1: placeholder, v2+: real service
                            'params': {
                                'style': 'toy',
                                'scale': 'medium'
                            }
                        }
                    ],
                    'inputs': {
                        'image_asset_ids': {
                            'type': 'array',
                            'item_type': 'uuid',
                            'required': True,
                            'min_length': 1,
                            'max_length': 4,
                            'label': 'Select 1-4 character images'
                        },
                        'style': {
                            'type': 'string',
                            'default': 'toy',
                            'choices': ['toy', 'semi-realistic'],
                            'label': 'Mini-fig style'
                        },
                        'scale': {
                            'type': 'string',
                            'default': 'medium',
                            'choices': ['small', 'medium', 'large'],
                            'label': 'Size'
                        }
                    },
                    'outputs': {
                        'minifig_asset_ids': {
                            'type': 'array',
                            'description': 'Created MiniFigAsset UUIDs'
                        },
                        'minifig_count': {
                            'type': 'int',
                            'description': 'Number of mini-figs created'
                        }
                    }
                }
            }
        ]

        created_count = 0
        updated_count = 0

        for template_data in templates:
            template, created = CreativePipelineTemplate.objects.update_or_create(
                slug=template_data['slug'],
                defaults={
                    'name': template_data['name'],
                    'description': template_data['description'],
                    'config': template_data['config'],
                    'is_active': True
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created template: {template.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Updated template: {template.name}')
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done! Created {created_count} templates, updated {updated_count} templates.'
        ))
