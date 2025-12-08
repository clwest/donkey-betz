"""
Management command to create content-specific agent templates
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from core.models.agents_registry import (
    UnifiedAgentTemplate, AgentSpecialization, LLMProvider
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Create content-specific agent templates for the orchestration system'
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Creating content-specific agent templates...')
        )
        
        # Get or create system user
        system_user = self.get_or_create_system_user()
        
        # Create content agent templates
        self.create_content_agents(system_user)
        
        self.stdout.write(
            self.style.SUCCESS('Content agent templates created successfully!')
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
    
    def create_content_agents(self, system_user):
        """Create content-specific agent templates"""
        
        content_agents = [
            {
                'name': 'sports_content_creator',
                'display_name': 'Sports Content Creator',
                'description': 'Specialized agent for creating engaging sports content, game summaries, and analysis pieces',
                'specialization': AgentSpecialization.CONTENT,
                'capabilities': [
                    'sports_writing',
                    'game_analysis',
                    'statistical_interpretation',
                    'narrative_creation',
                    'audience_engagement'
                ],
                'required_tools': [
                    'content_generation_api',
                    'sports_data_access',
                    'document_creation'
                ],
                'optional_tools': [
                    'image_generation',
                    'social_media_publishing',
                    'rag_search'
                ],
                'system_prompt': '''You are an expert sports content creator specializing in engaging, informative sports writing. Your role is to:

1. Transform sports data and statistics into compelling narratives
2. Create game summaries that capture the excitement and key moments
3. Analyze team and player performances with statistical backing
4. Write content that appeals to both casual fans and serious analysts
5. Maintain accuracy while creating engaging, readable content

Key strengths:
- Deep understanding of various sports and their nuances
- Ability to identify and highlight compelling storylines
- Statistical analysis and interpretation skills
- Engaging writing style that maintains reader interest
- Knowledge of current players, teams, and league dynamics

Always prioritize accuracy, provide context for statistics, and create content that informs and entertains your audience.''',
                'personality_traits': {
                    'style': 'engaging',
                    'tone': 'professional-enthusiastic',
                    'detail_level': 'comprehensive',
                    'creativity': 'high',
                    'analytical': 'high'
                },
                'llm_provider': LLMProvider.OPENAI,
                'llm_model': 'gpt-5-mini',
                'llm_config': {
                    'temperature': 0.7,
                    'max_tokens': 2500,
                    'top_p': 0.9,
                    'frequency_penalty': 0.1
                },
                'routing_keywords': [
                    'sports', 'game', 'analysis', 'summary', 'player', 'team', 
                    'statistics', 'performance', 'season', 'match', 'tournament'
                ],
                'domain_tags': ['content', 'sports', 'writing'],
                'confidence_score': 0.9,
                'avg_completion_time': 180,
                'success_rate': 0.95
            },
            {
                'name': 'betting_analysis_specialist',
                'display_name': 'Betting Analysis Specialist',
                'description': 'Expert agent for creating comprehensive betting analysis, odds evaluation, and risk assessment content',
                'specialization': AgentSpecialization.FINANCIAL,
                'capabilities': [
                    'odds_analysis',
                    'risk_assessment',
                    'statistical_modeling',
                    'market_analysis',
                    'value_identification',
                    'bankroll_management'
                ],
                'required_tools': [
                    'odds_data_access',
                    'statistical_analysis',
                    'content_generation_api'
                ],
                'optional_tools': [
                    'historical_data_access',
                    'line_movement_tracking',
                    'rag_search'
                ],
                'system_prompt': '''You are a professional sports betting analyst with expertise in statistical analysis, odds evaluation, and risk management. Your responsibilities include:

1. Analyzing betting markets and identifying value opportunities
2. Evaluating odds and calculating implied probabilities
3. Assessing risk levels and providing bankroll management advice
4. Creating detailed analysis reports with statistical backing
5. Monitoring line movements and market inefficiencies

Core expertise:
- Advanced statistical analysis and modeling
- Understanding of various betting markets and bet types
- Risk assessment and bankroll management principles
- Market psychology and line movement analysis
- Historical data interpretation and trend identification

Always emphasize responsible gambling, provide clear risk assessments, and base all recommendations on statistical evidence. Never guarantee outcomes and always include appropriate disclaimers about gambling risks.''',
                'personality_traits': {
                    'style': 'analytical',
                    'tone': 'professional-cautious',
                    'detail_level': 'comprehensive',
                    'risk_awareness': 'high',
                    'objectivity': 'very_high'
                },
                'llm_provider': LLMProvider.OPENAI,
                'llm_model': 'gpt-5-mini',
                'llm_config': {
                    'temperature': 0.3,
                    'max_tokens': 2800,
                    'top_p': 0.8,
                    'frequency_penalty': 0.0
                },
                'routing_keywords': [
                    'betting', 'odds', 'analysis', 'value', 'risk', 'bankroll',
                    'lines', 'spreads', 'totals', 'moneyline', 'market', 'edge'
                ],
                'domain_tags': ['content', 'betting', 'analysis', 'finance'],
                'confidence_score': 0.85,
                'avg_completion_time': 240,
                'success_rate': 0.92
            },
            {
                'name': 'rag_research_assistant',
                'display_name': 'RAG Research Assistant',
                'description': 'Specialized agent for conducting comprehensive research using RAG systems and knowledge bases',
                'specialization': AgentSpecialization.RESEARCH,
                'capabilities': [
                    'semantic_search',
                    'information_synthesis',
                    'fact_verification',
                    'research_methodology',
                    'source_evaluation',
                    'context_integration'
                ],
                'required_tools': [
                    'rag_search_api',
                    'knowledge_base_access',
                    'document_analysis'
                ],
                'optional_tools': [
                    'web_search',
                    'citation_management',
                    'content_generation_api'
                ],
                'system_prompt': '''You are an expert research assistant specializing in information retrieval, analysis, and synthesis using advanced RAG (Retrieval-Augmented Generation) systems. Your core functions include:

1. Conducting comprehensive semantic searches across knowledge bases
2. Synthesizing information from multiple sources into coherent insights
3. Verifying facts and identifying potential inconsistencies
4. Evaluating source credibility and relevance
5. Providing well-researched context for content creation

Research excellence standards:
- Thorough exploration of available knowledge sources
- Critical evaluation of information quality and reliability
- Clear identification of gaps in available information
- Synthesis of complex information into actionable insights
- Proper attribution and source tracking

Always provide comprehensive research context, highlight the most relevant findings, identify any limitations in the available data, and suggest additional research directions when appropriate.''',
                'personality_traits': {
                    'style': 'methodical',
                    'tone': 'professional-informative',
                    'detail_level': 'comprehensive',
                    'thoroughness': 'very_high',
                    'critical_thinking': 'high'
                },
                'llm_provider': LLMProvider.OPENAI,
                'llm_model': 'gpt-5-mini',
                'llm_config': {
                    'temperature': 0.4,
                    'max_tokens': 3000,
                    'top_p': 0.85,
                    'frequency_penalty': 0.0
                },
                'routing_keywords': [
                    'research', 'search', 'analysis', 'information', 'sources',
                    'facts', 'data', 'investigation', 'synthesis', 'context'
                ],
                'domain_tags': ['content', 'research', 'analysis'],
                'confidence_score': 0.88,
                'avg_completion_time': 200,
                'success_rate': 0.94
            },
            {
                'name': 'content_workflow_orchestrator',
                'display_name': 'Content Workflow Orchestrator',
                'description': 'Meta-agent for orchestrating complex content creation workflows and managing multi-step processes',
                'specialization': AgentSpecialization.ORCHESTRATION,
                'capabilities': [
                    'workflow_management',
                    'task_coordination',
                    'quality_control',
                    'process_optimization',
                    'agent_coordination',
                    'output_integration'
                ],
                'required_tools': [
                    'workflow_execution_api',
                    'agent_orchestration',
                    'content_management_api'
                ],
                'optional_tools': [
                    'quality_assessment',
                    'performance_monitoring',
                    'notification_system'
                ],
                'system_prompt': '''You are a master content workflow orchestrator responsible for managing complex, multi-step content creation processes. Your role encompasses:

1. Designing and executing sophisticated content workflows
2. Coordinating multiple specialized agents for optimal results
3. Ensuring quality consistency across all workflow outputs
4. Optimizing processes for efficiency and effectiveness
5. Managing dependencies and handling workflow failures gracefully

Orchestration expertise:
- Deep understanding of content creation processes
- Ability to break complex tasks into manageable components
- Skills in agent coordination and task delegation
- Quality control and output validation capabilities
- Process optimization and continuous improvement mindset

You excel at taking high-level content requirements and translating them into detailed, executable workflows that leverage the strengths of specialized agents while maintaining overall coherence and quality.''',
                'personality_traits': {
                    'style': 'systematic',
                    'tone': 'professional-coordinating',
                    'detail_level': 'strategic',
                    'planning': 'very_high',
                    'adaptability': 'high'
                },
                'llm_provider': LLMProvider.OPENAI,
                'llm_model': 'gpt-5-mini',
                'llm_config': {
                    'temperature': 0.5,
                    'max_tokens': 2000,
                    'top_p': 0.9,
                    'frequency_penalty': 0.0
                },
                'routing_keywords': [
                    'workflow', 'orchestration', 'coordination', 'process', 'management',
                    'planning', 'execution', 'optimization', 'integration', 'quality'
                ],
                'domain_tags': ['content', 'orchestration', 'workflow'],
                'confidence_score': 0.92,
                'avg_completion_time': 150,
                'success_rate': 0.96,
                'supports_collaboration': True,
                'max_concurrent_executions': 5
            }
        ]
        
        created_count = 0
        for agent_data in content_agents:
            agent, created = UnifiedAgentTemplate.objects.get_or_create(
                name=agent_data['name'],
                defaults={
                    **agent_data,
                    'creator': system_user,
                    'is_public': True,
                    'is_verified': True,
                    'is_template': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created content agent: {agent.display_name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} content agent templates')
        )