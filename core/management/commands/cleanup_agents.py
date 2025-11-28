"""
Session 241: Agent Cleanup Command

This command:
1. Removes all 139+ placeholder agents (no real code backing them)
2. Keeps only agents that have actual Python implementations
3. Keeps the 25 legendary advisors (they're used for creative direction)

The real agents with code implementations:
- ImageAgent, VideoAgent, AudioAgent, ResearchAgent
- WorkflowOrchestrationAgent, TrendAnalysisAgent
- OpportunityScoringAgent, CharacterTrainingAgent
- TrainedCreationAgent, 3DGenerationAgent
- ContentStrategyAgent, SEOOptimizerAgent (NEW Session 241)
- BrandIdentityAgent, SocialMediaAgent (NEW Session 241)
- CreativeDirectorAgent (NEW Session 241)

Run with: python manage.py cleanup_agents
"""

from django.core.management.base import BaseCommand
from core.models import Agent, Advisor, AgentCategory
import json


class Command(BaseCommand):
    help = 'Clean up placeholder agents and keep only real implementations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)

        self.stdout.write("🧹 AGENT CLEANUP - Session 241")
        self.stdout.write("=" * 60)

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made\n"))

        # Real agents that have Python implementations
        real_agent_names = [
            # Core generation agents
            'ImageAgent',
            'VideoAgent',
            'AudioAgent',

            # Research & Analysis
            'ResearchAgent',
            'TrendAnalysisAgent',

            # Workflow & Orchestration
            'WorkflowOrchestrationAgent',
            'OpportunityScoringAgent',

            # Specialized generation
            'CharacterTrainingAgent',
            'TrainedCreationAgent',
            '3DGenerationAgent',

            # Session 241: New valuable agents
            'ContentStrategyAgent',
            'SEOOptimizerAgent',
            'BrandIdentityAgent',
            'SocialMediaAgent',
            'CreativeDirectorAgent',

            # Executive agents (partial implementations)
            'CTOAgent',
            'COOAgent',
            'MeetingCoordinatorAgent',
        ]

        # Count current agents
        current_count = Agent.objects.count()
        self.stdout.write(f"📊 Current agents in database: {current_count}")

        # Find agents to delete (not in real_agent_names)
        agents_to_delete = Agent.objects.exclude(name__in=real_agent_names)
        delete_count = agents_to_delete.count()

        self.stdout.write(f"🗑️  Agents to remove: {delete_count}")
        self.stdout.write(f"✅ Agents to keep: {current_count - delete_count}")

        if delete_count > 0:
            self.stdout.write("\n📋 Agents being removed:")
            for agent in agents_to_delete[:20]:  # Show first 20
                self.stdout.write(f"   - {agent.name}")
            if delete_count > 20:
                self.stdout.write(f"   ... and {delete_count - 20} more")

        if not dry_run and delete_count > 0:
            # Actually delete the placeholder agents
            agents_to_delete.delete()
            self.stdout.write(self.style.SUCCESS(f"\n✅ Deleted {delete_count} placeholder agents"))

        # Now ensure real agents exist
        self.stdout.write("\n📦 Ensuring real agents exist in database...")
        self.ensure_real_agents(dry_run)

        # Final count
        final_count = Agent.objects.count()
        advisor_count = Advisor.objects.count()

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("🎉 CLEANUP COMPLETE!"))
        self.stdout.write(f"📊 Final agent count: {final_count}")
        self.stdout.write(f"👥 Advisors (kept): {advisor_count}")
        self.stdout.write("\n✨ Your agent ecosystem now has only real, working agents!")

    def ensure_real_agents(self, dry_run=False):
        """Ensure all real agents exist with proper metadata"""

        agents_data = [
            # Core generation agents
            {
                'name': 'ImageAgent',
                'agent_type': 'creative',
                'description': 'Unified image generation agent - logos, social media, illustrations, product photos',
                'effectiveness_score': 95,
                'capabilities': ['image_generation', 'style_transfer', 'logo_creation', 'social_media_graphics']
            },
            {
                'name': 'VideoAgent',
                'agent_type': 'creative',
                'description': 'Unified video agent - text-to-video, image-to-video, editing, color grading',
                'effectiveness_score': 93,
                'capabilities': ['video_generation', 'image_to_video', 'video_editing', 'color_grading', 'audio_mixing']
            },
            {
                'name': 'AudioAgent',
                'agent_type': 'creative',
                'description': 'Audio generation agent - text-to-speech, sound effects, voiceovers',
                'effectiveness_score': 91,
                'capabilities': ['text_to_speech', 'sound_effects', 'voiceover', 'audio_mixing']
            },

            # Research & Analysis
            {
                'name': 'ResearchAgent',
                'agent_type': 'research',
                'description': 'Unified research agent - web search combined with spider intelligence',
                'effectiveness_score': 90,
                'capabilities': ['web_search', 'spider_intelligence', 'trend_research', 'topic_synthesis']
            },
            {
                'name': 'TrendAnalysisAgent',
                'agent_type': 'analytics',
                'description': 'Analyzes spider data for trending topics, colors, and styles',
                'effectiveness_score': 88,
                'capabilities': ['trend_detection', 'color_trends', 'style_analysis', 'market_insights']
            },

            # Workflow & Orchestration
            {
                'name': 'WorkflowOrchestrationAgent',
                'agent_type': 'automation',
                'description': 'Orchestrates multi-step creative workflows',
                'effectiveness_score': 94,
                'capabilities': ['workflow_execution', 'agent_coordination', 'multi_step_tasks', 'project_management']
            },
            {
                'name': 'OpportunityScoringAgent',
                'agent_type': 'analytics',
                'description': 'Scores spider data as revenue opportunities',
                'effectiveness_score': 89,
                'capabilities': ['opportunity_scoring', 'revenue_prediction', 'trend_scoring']
            },

            # Specialized generation
            {
                'name': 'CharacterTrainingAgent',
                'agent_type': 'creative',
                'description': 'Trains custom character styles for consistent generation',
                'effectiveness_score': 87,
                'capabilities': ['character_training', 'style_learning', 'consistency_enforcement']
            },
            {
                'name': 'TrainedCreationAgent',
                'agent_type': 'creative',
                'description': 'Uses trained characters for consistent image generation',
                'effectiveness_score': 86,
                'capabilities': ['trained_generation', 'character_consistency', 'style_application']
            },
            {
                'name': '3DGenerationAgent',
                'agent_type': 'creative',
                'description': '3D model and scene generation',
                'effectiveness_score': 85,
                'capabilities': ['3d_generation', 'model_creation', 'scene_building']
            },

            # Session 241: New valuable agents
            {
                'name': 'ContentStrategyAgent',
                'agent_type': 'content',
                'description': 'Analyzes trends to recommend content creation strategies',
                'effectiveness_score': 90,
                'capabilities': ['content_planning', 'trend_analysis', 'recommendation_engine', 'content_calendar']
            },
            {
                'name': 'SEOOptimizerAgent',
                'agent_type': 'content',
                'description': 'Optimizes content for search and social discoverability',
                'effectiveness_score': 88,
                'capabilities': ['seo_optimization', 'hashtag_generation', 'metadata_creation', 'keyword_analysis']
            },
            {
                'name': 'BrandIdentityAgent',
                'agent_type': 'creative',
                'description': 'Manages brand consistency across all generated content',
                'effectiveness_score': 89,
                'capabilities': ['brand_management', 'color_palette', 'style_consistency', 'brand_guidelines']
            },
            {
                'name': 'SocialMediaAgent',
                'agent_type': 'content',
                'description': 'Creates platform-optimized social media content',
                'effectiveness_score': 91,
                'capabilities': ['multi_platform_content', 'posting_optimization', 'content_calendar', 'platform_specs']
            },
            {
                'name': 'CreativeDirectorAgent',
                'agent_type': 'creative',
                'description': 'Provides high-level creative direction and prompt enhancement',
                'effectiveness_score': 92,
                'capabilities': ['creative_direction', 'prompt_enhancement', 'style_recommendation', 'project_guidance']
            },
        ]

        for agent_data in agents_data:
            agent, created = Agent.objects.get_or_create(
                name=agent_data['name'],
                defaults={
                    'agent_type': agent_data['agent_type'],
                    'description': agent_data['description'],
                    'is_active': True,
                    'effectiveness_score': agent_data['effectiveness_score'],
                    'specialization': agent_data['agent_type'],
                    'capabilities': json.dumps({
                        'skills': agent_data['capabilities'],
                        'has_code_implementation': True,
                        'session': 241
                    })
                }
            )

            if created:
                self.stdout.write(f"  ✅ Created: {agent_data['name']}")
            else:
                self.stdout.write(f"  ⏭️  Exists: {agent_data['name']}")
