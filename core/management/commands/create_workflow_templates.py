"""
Create Workflow Templates
==========================

Session 768: Management command to create built-in workflow templates
for common multi-agent orchestrations.

Usage:
    python manage.py create_workflow_templates
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create built-in workflow templates for orchestration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Recreate templates even if they exist',
        )

    def handle(self, *args, **options):
        from core.models_unified_system import CustomWorkflow, CustomWorkflowStep

        # Get or create system user for templates
        system_user, _ = User.objects.get_or_create(
            username='system',
            defaults={'email': 'system@localhost', 'is_staff': True}
        )

        force = options.get('force', False)

        templates = [
            # =====================================================
            # Research & Content Workflow
            # =====================================================
            {
                'name': 'Research to Blog Post',
                'slug': 'research-to-blog',
                'description': 'Research a topic and generate a blog post with SEO optimization.',
                'execution_mode': 'sequential',
                'max_retries': 2,
                'timeout_seconds': 1800,
                'cost_budget': '1.0000',
                'steps': [
                    {
                        'order': 1,
                        'name': 'Research Topic',
                        'description': 'Deep research on the provided topic using multiple sources.',
                        'agent': 'ResearchAgent',
                        'config': {'prompt_template': 'Research the topic: {topic}. Provide comprehensive findings.'},
                        'timeout_seconds': 300,
                    },
                    {
                        'order': 2,
                        'name': 'Write Blog Post',
                        'description': 'Create a blog post based on research findings.',
                        'agent': 'ContentWriterAgent',
                        'config': {'prompt_template': 'Based on the research, write a compelling blog post about {topic}. Research: {step_1}'},
                        'depends_on_steps': [1],
                        'timeout_seconds': 300,
                    },
                    {
                        'order': 3,
                        'name': 'SEO Optimization',
                        'description': 'Optimize the blog post for search engines.',
                        'agent': 'SEOOptimizerAgent',
                        'config': {'prompt_template': 'Optimize this content for SEO: {step_2}'},
                        'depends_on_steps': [2],
                        'timeout_seconds': 180,
                    },
                ],
            },
            # =====================================================
            # Market Analysis Workflow
            # =====================================================
            {
                'name': 'Stock Analysis Pipeline',
                'slug': 'stock-analysis',
                'description': 'Comprehensive stock analysis with bull/bear cases.',
                'execution_mode': 'dependency',
                'max_retries': 2,
                'timeout_seconds': 1200,
                'cost_budget': '0.5000',
                'steps': [
                    {
                        'order': 1,
                        'name': 'Stock Research',
                        'description': 'Gather fundamental and technical data.',
                        'agent': 'StockAnalystAgent',
                        'config': {'prompt_template': 'Analyze stock: {ticker}. Include fundamentals and technicals.'},
                        'timeout_seconds': 300,
                    },
                    {
                        'order': 2,
                        'name': 'Bull Case Analysis',
                        'description': 'Build the bull case for the stock.',
                        'agent': 'BullCaseAgent',
                        'config': {'prompt_template': 'Build a bull case for {ticker} based on: {step_1}'},
                        'depends_on_steps': [1],
                        'timeout_seconds': 180,
                    },
                    {
                        'order': 3,
                        'name': 'Bear Case Analysis',
                        'description': 'Build the bear case for the stock.',
                        'agent': 'BearCaseAgent',
                        'config': {'prompt_template': 'Build a bear case for {ticker} based on: {step_1}'},
                        'depends_on_steps': [1],
                        'timeout_seconds': 180,
                    },
                    {
                        'order': 4,
                        'name': 'Market Intelligence Summary',
                        'description': 'Synthesize bull/bear cases into actionable intelligence.',
                        'agent': 'MarketIntelligenceAgent',
                        'config': {'prompt_template': 'Synthesize analysis for {ticker}. Bull: {step_2}. Bear: {step_3}'},
                        'depends_on_steps': [2, 3],
                        'requires_approval': True,
                        'approval_config': {
                            'approval_message': 'Review the final stock analysis before publishing.',
                            'timeout_hours': 48,
                            'auto_approve_on_timeout': False,
                        },
                        'timeout_seconds': 240,
                    },
                ],
            },
            # =====================================================
            # Creative Content Workflow
            # =====================================================
            {
                'name': 'Image Campaign Creator',
                'slug': 'image-campaign',
                'description': 'Create a visual content campaign with strategy and images.',
                'execution_mode': 'sequential',
                'max_retries': 3,
                'timeout_seconds': 2400,
                'cost_budget': '2.0000',
                'steps': [
                    {
                        'order': 1,
                        'name': 'Brand Strategy',
                        'description': 'Develop brand identity and visual strategy.',
                        'agent': 'BrandIdentityAgent',
                        'config': {'prompt_template': 'Create brand identity for: {brand_description}'},
                        'timeout_seconds': 300,
                    },
                    {
                        'order': 2,
                        'name': 'Content Strategy',
                        'description': 'Plan content strategy for the campaign.',
                        'agent': 'ContentStrategyAgent',
                        'config': {'prompt_template': 'Plan content strategy based on brand: {step_1}'},
                        'depends_on_steps': [1],
                        'timeout_seconds': 300,
                    },
                    {
                        'order': 3,
                        'name': 'Generate Hero Image',
                        'description': 'Create the main campaign image.',
                        'agent': 'ImageAgent',
                        'config': {'prompt_template': 'Create a hero image for the campaign. Brand: {step_1}. Strategy: {step_2}'},
                        'depends_on_steps': [1, 2],
                        'timeout_seconds': 300,
                        'cost_limit': '0.5000',
                    },
                    {
                        'order': 4,
                        'name': 'Creative Review',
                        'description': 'Review all creative assets.',
                        'agent': 'CreativeDirectorAgent',
                        'config': {'prompt_template': 'Review the campaign. Brand: {step_1}. Strategy: {step_2}. Image: {step_3}'},
                        'depends_on_steps': [1, 2, 3],
                        'requires_approval': True,
                        'approval_config': {
                            'approval_message': 'Review the complete campaign before launch.',
                            'timeout_hours': 24,
                            'auto_approve_on_timeout': False,
                        },
                        'timeout_seconds': 300,
                    },
                ],
            },
            # =====================================================
            # Code Review Workflow
            # =====================================================
            {
                'name': 'Code Review Pipeline',
                'slug': 'code-review',
                'description': 'Comprehensive code review with security and best practices.',
                'execution_mode': 'parallel',
                'max_retries': 1,
                'timeout_seconds': 600,
                'cost_budget': '0.3000',
                'steps': [
                    {
                        'order': 1,
                        'name': 'Code Analysis',
                        'description': 'Analyze code quality and patterns.',
                        'agent': 'CodeReviewAgent',
                        'config': {'prompt_template': 'Review this code: {code}'},
                        'timeout_seconds': 180,
                    },
                    {
                        'order': 2,
                        'name': 'Security Audit',
                        'description': 'Check for security vulnerabilities.',
                        'agent': 'ContentAuditAgent',
                        'config': {'prompt_template': 'Security audit this code: {code}'},
                        'timeout_seconds': 180,
                    },
                    {
                        'order': 3,
                        'name': 'CTO Review',
                        'description': 'Final technical review.',
                        'agent': 'CTOAgent',
                        'config': {'prompt_template': 'Final review. Code Review: {step_1}. Security: {step_2}'},
                        'depends_on_steps': [1, 2],
                        'timeout_seconds': 180,
                    },
                ],
            },
            # =====================================================
            # Competitor Intelligence Workflow
            # =====================================================
            {
                'name': 'Competitor Analysis',
                'slug': 'competitor-analysis',
                'description': 'Deep competitor research and strategic recommendations.',
                'execution_mode': 'sequential',
                'max_retries': 2,
                'timeout_seconds': 1500,
                'cost_budget': '0.7500',
                'steps': [
                    {
                        'order': 1,
                        'name': 'Market Research',
                        'description': 'Research the competitive landscape.',
                        'agent': 'ResearchAgent',
                        'config': {'prompt_template': 'Research competitors of {company} in {industry}'},
                        'timeout_seconds': 300,
                    },
                    {
                        'order': 2,
                        'name': 'Competitor Deep Dive',
                        'description': 'Detailed competitor analysis.',
                        'agent': 'CompetitorAnalysisAgent',
                        'config': {'prompt_template': 'Analyze top competitors from: {step_1}'},
                        'depends_on_steps': [1],
                        'timeout_seconds': 300,
                    },
                    {
                        'order': 3,
                        'name': 'Customer Insights',
                        'description': 'Research customer preferences and pain points.',
                        'agent': 'CustomerResearchAgent',
                        'config': {'prompt_template': 'Research customer needs in {industry}. Context: {step_1}'},
                        'depends_on_steps': [1],
                        'timeout_seconds': 300,
                    },
                    {
                        'order': 4,
                        'name': 'Marketing Strategy',
                        'description': 'Develop competitive marketing strategy.',
                        'agent': 'MarketingStrategyAgent',
                        'config': {'prompt_template': 'Create strategy. Competitors: {step_2}. Customers: {step_3}'},
                        'depends_on_steps': [2, 3],
                        'timeout_seconds': 300,
                    },
                ],
            },
            # =====================================================
            # Podcast Production Workflow
            # =====================================================
            {
                'name': 'Podcast Episode Production',
                'slug': 'podcast-episode',
                'description': 'Create a podcast episode with research, debate, and production.',
                'execution_mode': 'sequential',
                'max_retries': 2,
                'timeout_seconds': 3600,
                'cost_budget': '1.5000',
                'steps': [
                    {
                        'order': 1,
                        'name': 'Topic Research',
                        'description': 'Deep research on the podcast topic.',
                        'agent': 'ResearchAgent',
                        'config': {'prompt_template': 'Research topic for podcast: {topic}'},
                        'timeout_seconds': 300,
                    },
                    {
                        'order': 2,
                        'name': 'Debate Advocate',
                        'description': 'Build the supporting argument.',
                        'agent': 'DebateAdvocateAgent',
                        'config': {'prompt_template': 'Build case FOR this position: {topic}. Research: {step_1}'},
                        'depends_on_steps': [1],
                        'timeout_seconds': 300,
                    },
                    {
                        'order': 3,
                        'name': 'Debate Skeptic',
                        'description': 'Build the opposing argument.',
                        'agent': 'DebateSkepticAgent',
                        'config': {'prompt_template': 'Build case AGAINST this position: {topic}. Research: {step_1}'},
                        'depends_on_steps': [1],
                        'timeout_seconds': 300,
                    },
                    {
                        'order': 4,
                        'name': 'Moderation',
                        'description': 'Moderate and synthesize the debate.',
                        'agent': 'ModeratorAgent',
                        'config': {'prompt_template': 'Moderate debate. For: {step_2}. Against: {step_3}'},
                        'depends_on_steps': [2, 3],
                        'timeout_seconds': 300,
                    },
                    {
                        'order': 5,
                        'name': 'Podcast Coordination',
                        'description': 'Coordinate final podcast episode.',
                        'agent': 'PodcastCoordinatorAgent',
                        'config': {'prompt_template': 'Create podcast episode. Topic: {topic}. Debate: {step_4}'},
                        'depends_on_steps': [4],
                        'requires_approval': True,
                        'approval_config': {
                            'approval_message': 'Review podcast episode before publishing.',
                            'timeout_hours': 24,
                            'auto_approve_on_timeout': False,
                        },
                        'timeout_seconds': 300,
                    },
                ],
            },
        ]

        created_count = 0
        updated_count = 0

        for template in templates:
            workflow, created = CustomWorkflow.objects.get_or_create(
                slug=template['slug'],
                created_by=system_user,
                defaults={
                    'name': template['name'],
                    'description': template['description'],
                    'execution_mode': template.get('execution_mode', 'sequential'),
                    'max_retries': template.get('max_retries', 3),
                    'timeout_seconds': template.get('timeout_seconds', 3600),
                    'cost_budget': template.get('cost_budget'),
                    'status': 'active',
                    'is_public': True,
                    'is_featured': True,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(f'  Created workflow: {template["name"]}')
            elif force:
                # Update existing workflow
                workflow.name = template['name']
                workflow.description = template['description']
                workflow.execution_mode = template.get('execution_mode', 'sequential')
                workflow.max_retries = template.get('max_retries', 3)
                workflow.timeout_seconds = template.get('timeout_seconds', 3600)
                workflow.cost_budget = template.get('cost_budget')
                workflow.status = 'active'
                workflow.save()
                updated_count += 1
                self.stdout.write(f'  Updated workflow: {template["name"]}')

                # Remove old steps
                workflow.steps.all().delete()
            else:
                self.stdout.write(f'  Skipped existing: {template["name"]}')
                continue

            # Create steps (only if workflow was just created or force=True)
            if created or force:
                for step_data in template['steps']:
                    CustomWorkflowStep.objects.create(
                        workflow=workflow,
                        order=step_data['order'],
                        name=step_data['name'],
                        description=step_data.get('description', ''),
                        agent=step_data['agent'],
                        config=step_data.get('config', {}),
                        timeout_seconds=step_data.get('timeout_seconds', 300),
                        requires_approval=step_data.get('requires_approval', False),
                        approval_config=step_data.get('approval_config', {}),
                        depends_on_steps=step_data.get('depends_on_steps', []),
                        cost_limit=step_data.get('cost_limit'),
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nWorkflow templates: {created_count} created, {updated_count} updated'
            )
        )
