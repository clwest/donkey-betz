"""
Management command to create sample agents for testing
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models.agents_registry import UnifiedAgentTemplate, AgentRegistry


class Command(BaseCommand):
    help = 'Create sample agents for testing the unified platform'
    
    def handle(self, *args, **options):
        self.stdout.write("Creating sample agents...")
        
        sample_agents = [
            {
                'name': 'research_agent',
                'display_name': 'Research Agent',
                'description': 'Expert in market research, data analysis, and trend identification',
                'specialization': 'research',
                'capabilities': [
                    'Market research and sizing',
                    'Competitor analysis',
                    'Data synthesis',
                    'Trend identification'
                ],
                'required_tools': ['web_search', 'document_generator'],
                'system_prompt': 'You are a Research Agent specializing in thorough, data-driven analysis. Always verify information from multiple sources and provide specific data points with citations.',
                'personality_traits': {
                    'style': 'analytical',
                    'tone': 'professional',
                    'detail_level': 'comprehensive'
                },
                'routing_keywords': ['research', 'analyze', 'investigate', 'market'],
                'domain_tags': ['business', 'research'],
                'confidence_score': 0.8
            },
            {
                'name': 'sports_analytics_agent',
                'display_name': 'Sports Analytics Agent',
                'description': 'Specialized in sports data analysis and betting intelligence',
                'specialization': 'sports-analytics',
                'capabilities': [
                    'Sports performance analysis',
                    'Betting odds calculation',
                    'Team statistics evaluation',
                    'Injury impact assessment'
                ],
                'required_tools': ['sports_api', 'odds_calculator'],
                'system_prompt': 'You are a Sports Analytics Agent with expertise in sports betting and performance analysis. Provide data-driven insights based on statistical analysis.',
                'personality_traits': {
                    'style': 'analytical',
                    'tone': 'confident',
                    'detail_level': 'detailed'
                },
                'routing_keywords': ['sports', 'betting', 'odds', 'analytics'],
                'domain_tags': ['sports', 'analytics'],
                'confidence_score': 0.9
            },
            {
                'name': 'content_creator_agent',
                'display_name': 'Content Creator Agent',
                'description': 'Expert content creator for blogs, tutorials, and marketing materials',
                'specialization': 'content',
                'capabilities': [
                    'Blog post writing',
                    'SEO optimization',
                    'Tutorial creation',
                    'Marketing copy'
                ],
                'required_tools': ['text_editor', 'seo_analyzer'],
                'system_prompt': 'You are a Content Creator Agent specializing in engaging, high-quality content. Focus on clarity, engagement, and SEO optimization.',
                'personality_traits': {
                    'style': 'creative',
                    'tone': 'engaging',
                    'detail_level': 'balanced'
                },
                'routing_keywords': ['content', 'write', 'blog', 'marketing'],
                'domain_tags': ['content', 'marketing'],
                'confidence_score': 0.85
            }
        ]
        
        created_count = 0
        
        with transaction.atomic():
            for agent_data in sample_agents:
                agent, created = UnifiedAgentTemplate.objects.get_or_create(
                    name=agent_data['name'],
                    defaults=agent_data
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f"Created agent: {agent.display_name}")
                else:
                    self.stdout.write(f"Agent already exists: {agent.display_name}")
            
            # Create/update agent registry
            registry, created = AgentRegistry.objects.get_or_create(
                registry_name='unified_agent_registry'
            )
            registry.rebuild_indexes()
            
        self.stdout.write(self.style.SUCCESS(
            f"Sample agent creation complete. {created_count} new agents created."
        ))
        self.stdout.write(self.style.SUCCESS(
            f"Agent registry updated: {registry.total_agents} total agents"
        ))