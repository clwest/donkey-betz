"""
Management command to set up the content management system with initial data
"""

import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone

from content.models import (
    ContentTemplate, KnowledgeBase, EmbeddingModel,
    ContentWorkflow, ContentAnalytics
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up the content management system with initial templates, knowledge bases, and workflows'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-templates',
            action='store_true',
            help='Create initial content templates',
        )
        parser.add_argument(
            '--create-knowledge-bases',
            action='store_true',
            help='Create initial knowledge bases',
        )
        parser.add_argument(
            '--create-workflows',
            action='store_true',
            help='Create initial content workflows',
        )
        parser.add_argument(
            '--create-all',
            action='store_true',
            help='Create all initial content system components',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Setting up Unified Content Management System...')
        )
        
        # Get or create system user
        system_user = self.get_or_create_system_user()
        
        if options['create_all'] or options['create_templates']:
            self.create_initial_templates(system_user)
        
        if options['create_all'] or options['create_knowledge_bases']:
            self.create_initial_knowledge_bases(system_user)
        
        if options['create_all'] or options['create_workflows']:
            self.create_initial_workflows(system_user)
        
        self.stdout.write(
            self.style.SUCCESS('Content Management System setup completed!')
        )
    
    def get_or_create_system_user(self):
        """Get or create system user for initial data"""
        try:
            return User.objects.get(username='system')
        except User.DoesNotExist:
            user = User.objects.create_user(
                username='system',
                email='system@unified-donkey-betz.com',
                first_name='System',
                last_name='User',
                platform_role='admin'
            )
            self.stdout.write('Created system user')
            return user
    
    def create_initial_templates(self, system_user):
        """Create initial content templates"""
        templates = [
            {
                'name': 'sports_game_summary',
                'display_name': 'Sports Game Summary',
                'description': 'Generate comprehensive sports game summaries with statistics and key moments',
                'template_type': 'sports_report',
                'system_prompt': '''You are a professional sports analyst and writer. Create engaging, accurate, and comprehensive game summaries that include:

1. Game overview with final score and key statistics
2. Turning points and crucial moments
3. Player performances and standout statistics
4. Team strategy analysis
5. Historical context when relevant
6. Clear, engaging writing suitable for sports fans

Focus on accuracy, insight, and readability. Use specific statistics and concrete examples.''',
                'user_prompt_template': '''Create a comprehensive summary of the {{game_type}} game between {{team_1}} and {{team_2}}.

Game Details:
- Date: {{game_date}}
- Venue: {{venue}}
- Final Score: {{final_score}}
{{#if additional_stats}}
- Key Statistics: {{additional_stats}}
{{/if}}

{{#if key_moments}}
Key Moments:
{{key_moments}}
{{/if}}

Please provide a detailed analysis covering the game flow, standout performances, strategic decisions, and what this result means for both teams.''',
                'variables': {
                    'game_type': {'type': 'string', 'description': 'Type of sport (e.g., NFL, NBA, MLB)', 'required': True},
                    'team_1': {'type': 'string', 'description': 'First team name', 'required': True},
                    'team_2': {'type': 'string', 'description': 'Second team name', 'required': True},
                    'game_date': {'type': 'string', 'description': 'Game date', 'required': True},
                    'venue': {'type': 'string', 'description': 'Game venue', 'required': False},
                    'final_score': {'type': 'string', 'description': 'Final score', 'required': True},
                    'additional_stats': {'type': 'string', 'description': 'Additional key statistics', 'required': False},
                    'key_moments': {'type': 'string', 'description': 'Key moments or plays', 'required': False}
                },
                'category': 'sports',
                'tags': ['sports', 'analysis', 'games', 'summary'],
                'llm_provider': 'openai',
                'llm_model': 'gpt-4-turbo-preview',
                'generation_config': {
                    'temperature': 0.7,
                    'max_tokens': 2000,
                    'top_p': 0.9
                }
            },
            {
                'name': 'betting_analysis_report',
                'display_name': 'Betting Analysis Report',
                'description': 'Generate comprehensive betting analysis with odds, value assessment, and risk evaluation',
                'template_type': 'betting_guide',
                'system_prompt': '''You are a professional sports betting analyst with expertise in statistical analysis, odds evaluation, and risk management. Create detailed betting analysis reports that include:

1. Market analysis with current odds and line movements
2. Statistical analysis supporting betting decisions
3. Value assessment and edge calculation
4. Risk evaluation and bankroll management recommendations
5. Historical context and relevant trends
6. Clear recommendations with confidence levels

Always emphasize responsible gambling and proper risk management. Base all analysis on data and statistical evidence.''',
                'user_prompt_template': '''Create a comprehensive betting analysis report for the {{game_type}} matchup between {{team_1}} and {{team_2}}.

Market Information:
- Current Spread: {{spread}}
- Money Line: {{moneyline}}
- Total Points: {{total}}
{{#if line_movement}}
- Line Movement: {{line_movement}}
{{/if}}

Team Statistics:
{{team_stats}}

{{#if recent_form}}
Recent Form:
{{recent_form}}
{{/if}}

{{#if injuries}}
Injury Report:
{{injuries}}
{{/if}}

Please provide a detailed analysis including value assessment, recommended bets (if any), confidence levels, and risk management suggestions.''',
                'variables': {
                    'game_type': {'type': 'string', 'description': 'Type of sport', 'required': True},
                    'team_1': {'type': 'string', 'description': 'First team name', 'required': True},
                    'team_2': {'type': 'string', 'description': 'Second team name', 'required': True},
                    'spread': {'type': 'string', 'description': 'Point spread', 'required': True},
                    'moneyline': {'type': 'string', 'description': 'Moneyline odds', 'required': True},
                    'total': {'type': 'string', 'description': 'Over/under total', 'required': True},
                    'line_movement': {'type': 'string', 'description': 'Recent line movements', 'required': False},
                    'team_stats': {'type': 'string', 'description': 'Relevant team statistics', 'required': True},
                    'recent_form': {'type': 'string', 'description': 'Recent team performance', 'required': False},
                    'injuries': {'type': 'string', 'description': 'Injury report', 'required': False}
                },
                'category': 'betting',
                'tags': ['betting', 'analysis', 'odds', 'sports'],
                'llm_provider': 'openai',
                'llm_model': 'gpt-4-turbo-preview',
                'generation_config': {
                    'temperature': 0.3,
                    'max_tokens': 2500,
                    'top_p': 0.9
                }
            },
            {
                'name': 'content_article',
                'display_name': 'General Content Article',
                'description': 'Generate well-structured articles on various topics with research integration',
                'template_type': 'article',
                'system_prompt': '''You are a professional content writer with expertise in creating engaging, informative, and well-structured articles. Your writing should be:

1. Clear and accessible to the target audience
2. Well-organized with logical flow
3. Factually accurate and well-researched
4. Engaging and compelling
5. Optimized for readability
6. Include relevant examples and data when appropriate

Always maintain a professional tone while making complex topics understandable.''',
                'user_prompt_template': '''Write a comprehensive article on the topic: "{{title}}"

Article Requirements:
- Target Audience: {{target_audience}}
- Article Length: {{length}}
- Tone: {{tone}}
{{#if key_points}}
- Key Points to Cover: {{key_points}}
{{/if}}
{{#if research_context}}
- Research Context: {{research_context}}
{{/if}}

Please create an engaging, well-structured article that covers the topic thoroughly while maintaining reader interest throughout.''',
                'variables': {
                    'title': {'type': 'string', 'description': 'Article title/topic', 'required': True},
                    'target_audience': {'type': 'string', 'description': 'Target audience description', 'required': True},
                    'length': {'type': 'string', 'description': 'Desired article length', 'required': True},
                    'tone': {'type': 'string', 'description': 'Article tone (professional, casual, etc.)', 'required': True},
                    'key_points': {'type': 'string', 'description': 'Key points to cover', 'required': False},
                    'research_context': {'type': 'string', 'description': 'Relevant research or context', 'required': False}
                },
                'category': 'general',
                'tags': ['article', 'content', 'writing'],
                'llm_provider': 'openai',
                'llm_model': 'gpt-4-turbo-preview',
                'generation_config': {
                    'temperature': 0.7,
                    'max_tokens': 3000,
                    'top_p': 0.9
                }
            }
        ]
        
        created_count = 0
        for template_data in templates:
            template, created = ContentTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    **template_data,
                    'creator': system_user,
                    'is_public': True,
                    'is_verified': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created template: {template.display_name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} content templates')
        )
    
    def create_initial_knowledge_bases(self, system_user):
        """Create initial knowledge bases"""
        knowledge_bases = [
            {
                'name': 'sports_analytics_kb',
                'description': 'Comprehensive knowledge base for sports analytics, statistics, and betting information',
                'domain': 'sports',
                'embedding_model': EmbeddingModel.OPENAI_SMALL,
                'chunk_size': 1000,
                'chunk_overlap': 200,
                'categories': [
                    'NFL', 'NBA', 'MLB', 'NHL', 'NCAA Football', 'NCAA Basketball',
                    'Statistics', 'Analytics', 'Betting', 'Historical Data'
                ],
                'tags': ['sports', 'analytics', 'betting', 'statistics'],
                'is_public': True
            },
            {
                'name': 'general_content_kb',
                'description': 'General knowledge base for content creation, writing guidelines, and research',
                'domain': 'general',
                'embedding_model': EmbeddingModel.OPENAI_SMALL,
                'chunk_size': 800,
                'chunk_overlap': 150,
                'categories': [
                    'Writing Guidelines', 'Content Strategy', 'Research Methods',
                    'SEO Best Practices', 'Social Media', 'Marketing'
                ],
                'tags': ['content', 'writing', 'marketing', 'research'],
                'is_public': True
            },
            {
                'name': 'betting_strategies_kb',
                'description': 'Knowledge base focused on betting strategies, risk management, and market analysis',
                'domain': 'betting',
                'embedding_model': EmbeddingModel.OPENAI_SMALL,
                'chunk_size': 1200,
                'chunk_overlap': 250,
                'categories': [
                    'Betting Strategies', 'Risk Management', 'Market Analysis',
                    'Statistical Models', 'Bankroll Management', 'Line Shopping'
                ],
                'tags': ['betting', 'strategy', 'risk-management', 'analysis'],
                'is_public': True
            }
        ]
        
        created_count = 0
        for kb_data in knowledge_bases:
            kb, created = KnowledgeBase.objects.get_or_create(
                name=kb_data['name'],
                defaults={
                    **kb_data,
                    'owner': system_user
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created knowledge base: {kb.name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} knowledge bases')
        )
    
    def create_initial_workflows(self, system_user):
        """Create initial content workflows"""
        workflows = [
            {
                'name': 'sports_content_workflow',
                'description': 'Complete workflow for generating sports-related content with analysis',
                'domain': 'sports',
                'workflow_steps': [
                    {
                        'name': 'Research Game Data',
                        'type': 'rag_search',
                        'query': '{{game_type}} {{team_1}} {{team_2}} statistics recent performance',
                        'knowledge_base_id': None,  # Will be set to sports KB if it exists
                        'limit': 5
                    },
                    {
                        'name': 'Generate Game Summary',
                        'type': 'content_generation',
                        'template_id': None,  # Will be set to sports template if it exists
                        'prompt': 'Generate comprehensive game summary using research data',
                        'use_rag': True,
                        'save_as_document': True
                    },
                    {
                        'name': 'Create Betting Analysis',
                        'type': 'content_generation',
                        'template_id': None,  # Will be set to betting template if it exists
                        'prompt': 'Create betting analysis based on game data and summary',
                        'use_rag': True,
                        'save_as_document': True
                    }
                ],
                'default_config': {
                    'auto_save_documents': True,
                    'enable_rag': True,
                    'quality_check': True
                },
                'is_public': True
            },
            {
                'name': 'content_research_workflow',
                'description': 'Research and content creation workflow with fact-checking',
                'domain': 'general',
                'workflow_steps': [
                    {
                        'name': 'Research Topic',
                        'type': 'rag_search',
                        'query': '{{topic}} {{key_points}}',
                        'knowledge_base_id': None,
                        'limit': 8
                    },
                    {
                        'name': 'Generate Content Outline',
                        'type': 'content_generation',
                        'prompt': 'Create detailed content outline based on research: {{topic}}',
                        'use_rag': True,
                        'generation_config': {
                            'temperature': 0.5,
                            'max_tokens': 1500
                        }
                    },
                    {
                        'name': 'Write Full Article',
                        'type': 'content_generation',
                        'template_id': None,  # Will be set to article template
                        'prompt': 'Write comprehensive article based on outline and research',
                        'use_rag': True,
                        'save_as_document': True
                    }
                ],
                'default_config': {
                    'research_depth': 'comprehensive',
                    'fact_check': True,
                    'citation_style': 'inline'
                },
                'is_public': True
            }
        ]
        
        created_count = 0
        for workflow_data in workflows:
            workflow, created = ContentWorkflow.objects.get_or_create(
                name=workflow_data['name'],
                defaults={
                    **workflow_data,
                    'creator': system_user
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created workflow: {workflow.name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} content workflows')
        )