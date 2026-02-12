"""
Seed learning journey templates and achievements.
Session 990: Populate production database with learning content.
Session 988: Added step_type and content_meta to templates.
"""
from django.core.management.base import BaseCommand

TEMPLATES = [
    {
        'name': 'Getting Started with AI Agents',
        'description': 'Learn the basics of working with AI agents, from understanding their capabilities to having productive conversations.',
        'category': 'agent_basics',
        'difficulty': 'beginner',
        'estimated_hours': 1.5,
        'steps_count': 5,
        'tags': ['beginner', 'agents', 'basics'],
        'steps_data': [
            {
                'title': 'Understanding AI Agents',
                'description': 'Learn what AI agents are and how they can help you.',
                'step_type': 'lesson',
            },
            {
                'title': 'Navigating the Agent List',
                'description': 'Explore the 72 available agents and their specialties.',
                'step_type': 'explore',
                'content_meta': {
                    'navigation_hints': ['/workspace?tab=agents', '/workspace?tab=overview'],
                },
            },
            {
                'title': 'Starting Your First Conversation',
                'description': 'Have your first conversation with an agent.',
                'step_type': 'exercise',
                'content_meta': {
                    'suggested_prompts': [
                        'What agents are available to help me?',
                        'Summarize today\'s top tech news',
                        'Help me brainstorm content ideas for my blog',
                    ],
                },
            },
            {
                'title': 'Understanding Agent Responses',
                'description': 'Learn how to interpret and act on agent recommendations.',
                'step_type': 'lesson',
            },
            {
                'title': 'Best Practices for Agent Interactions',
                'description': 'Tips and tricks for getting the most from your agents.',
                'step_type': 'lesson',
            },
        ],
    },
    {
        'name': 'Content Creation Mastery',
        'description': 'Master the art of content creation with AI assistance. Learn to generate images, videos, audio, and written content.',
        'category': 'content_creation',
        'difficulty': 'intermediate',
        'estimated_hours': 3.0,
        'steps_count': 6,
        'tags': ['content', 'images', 'video', 'audio', 'writing'],
        'steps_data': [
            {
                'title': 'Overview of Content Agents',
                'description': 'Meet the content creation team: Image, Video, Audio, and Content Writer agents.',
                'step_type': 'lesson',
            },
            {
                'title': 'Creating AI Images',
                'description': 'Learn to generate stunning images with the Image Agent.',
                'step_type': 'exercise',
                'content_meta': {
                    'suggested_prompts': [
                        'Generate a futuristic city skyline at sunset',
                        'Create a logo concept for a tech startup called NovaMind',
                        'Design a social media banner for a podcast about AI',
                    ],
                },
            },
            {
                'title': 'Video Generation Basics',
                'description': 'Create engaging videos with the Video Agent.',
                'step_type': 'exercise',
                'content_meta': {
                    'suggested_prompts': [
                        'Create a short explainer video about machine learning',
                        'Generate a product demo animation',
                        'Make a 15-second social media clip about AI tools',
                    ],
                },
            },
            {
                'title': 'Audio and Voice Content',
                'description': 'Generate podcasts, voiceovers, and audio content.',
                'step_type': 'exercise',
                'content_meta': {
                    'suggested_prompts': [
                        'Generate a podcast intro script about technology trends',
                        'Create a voiceover for a product walkthrough',
                        'Write and narrate a 2-minute news summary',
                    ],
                },
            },
            {
                'title': 'Writing Compelling Content',
                'description': 'Create articles, blogs, and copy with the Content Writer Agent.',
                'step_type': 'exercise',
                'content_meta': {
                    'suggested_prompts': [
                        'Write a blog post about the future of AI assistants',
                        'Create social media copy for a product launch',
                        'Draft an email newsletter about this week\'s AI news',
                    ],
                },
            },
            {
                'title': 'Content Strategy Integration',
                'description': 'Combine all content types into a cohesive strategy.',
                'step_type': 'lesson',
            },
        ],
    },
    {
        'name': 'Automation and Workflows',
        'description': 'Automate your work with AI-powered workflows. Set up autonomous agents that work 24/7.',
        'category': 'automation',
        'difficulty': 'intermediate',
        'estimated_hours': 2.5,
        'steps_count': 5,
        'tags': ['automation', 'workflows', 'autonomous'],
        'steps_data': [
            {
                'title': 'Understanding Automation Concepts',
                'description': 'Learn the fundamentals of AI automation.',
                'step_type': 'lesson',
            },
            {
                'title': 'Creating Your First Workflow',
                'description': 'Build a simple automated workflow.',
                'step_type': 'lesson',
            },
            {
                'title': 'Autonomous Agent Configuration',
                'description': 'Set up agents to work autonomously.',
                'step_type': 'exercise',
                'content_meta': {
                    'suggested_prompts': [
                        'Show me how to set up a daily news monitoring workflow',
                        'Configure an agent to track competitor pricing',
                        'Create an automated content pipeline for my blog',
                    ],
                },
            },
            {
                'title': 'Monitoring and Adjusting',
                'description': 'Learn to monitor and optimize your automations.',
                'step_type': 'explore',
                'content_meta': {
                    'navigation_hints': ['/workspace?tab=health', '/workspace?tab=overview'],
                },
            },
            {
                'title': 'Advanced Workflow Patterns',
                'description': 'Master complex multi-agent workflows.',
                'step_type': 'lesson',
            },
        ],
    },
    {
        'name': 'Analytics and Intelligence',
        'description': 'Unlock the power of data with AI analytics. Learn to interpret insights and make data-driven decisions.',
        'category': 'analytics',
        'difficulty': 'advanced',
        'estimated_hours': 4.0,
        'steps_count': 6,
        'tags': ['analytics', 'data', 'intelligence', 'insights'],
        'steps_data': [
            {
                'title': 'Introduction to AI Analytics',
                'description': 'Understand how AI transforms raw data into actionable insights.',
                'step_type': 'lesson',
            },
            {
                'title': 'Working with Spider Data',
                'description': 'Learn how spiders gather and process data from multiple sources.',
                'step_type': 'explore',
                'content_meta': {
                    'navigation_hints': ['/workspace?tab=spiders', '/workspace?tab=overview'],
                },
            },
            {
                'title': 'Trend Analysis Deep Dive',
                'description': 'Use the Trend Analysis Agent to identify patterns.',
                'step_type': 'exercise',
                'content_meta': {
                    'suggested_prompts': [
                        'What are the trending topics in AI this week?',
                        'Analyze recent tech industry trends',
                        'Show me emerging patterns in cryptocurrency markets',
                    ],
                },
            },
            {
                'title': 'Market Intelligence',
                'description': 'Leverage market data for business insights.',
                'step_type': 'exercise',
                'content_meta': {
                    'suggested_prompts': [
                        'Give me a market overview for the AI industry',
                        'What are the top-performing tech stocks this month?',
                        'Analyze competitive landscape for SaaS startups',
                    ],
                },
            },
            {
                'title': 'Building Custom Dashboards',
                'description': 'Create personalized analytics views.',
                'step_type': 'lesson',
            },
            {
                'title': 'Predictive Analytics',
                'description': 'Use AI predictions to anticipate future trends.',
                'step_type': 'lesson',
            },
        ],
    },
    {
        'name': 'Agent Integration Patterns',
        'description': 'Learn advanced integration patterns to connect agents with external systems and maximize their potential.',
        'category': 'integration',
        'difficulty': 'advanced',
        'estimated_hours': 3.5,
        'steps_count': 5,
        'tags': ['integration', 'api', 'advanced', 'systems'],
        'steps_data': [
            {
                'title': 'Integration Architecture Overview',
                'description': 'Understand how agents connect with external systems.',
                'step_type': 'lesson',
            },
            {
                'title': 'Spider Network Integration',
                'description': 'Connect agents with real-time data sources.',
                'step_type': 'explore',
                'content_meta': {
                    'navigation_hints': ['/workspace?tab=spiders', '/workspace?tab=agents'],
                },
            },
            {
                'title': 'Cross-Agent Communication',
                'description': 'Enable agents to collaborate on complex tasks.',
                'step_type': 'exercise',
                'content_meta': {
                    'suggested_prompts': [
                        'Research AI trends and then write a blog post about the findings',
                        'Analyze this topic from multiple agent perspectives',
                        'Start a multi-agent deliberation on the future of remote work',
                    ],
                },
            },
            {
                'title': 'Custom Tool Development',
                'description': 'Create custom tools for specialized tasks.',
                'step_type': 'exercise',
                'content_meta': {
                    'suggested_prompts': [
                        'What tools are available in the platform?',
                        'Show me how agents use tools to complete tasks',
                        'Explain the tool calling workflow',
                    ],
                },
            },
            {
                'title': 'Production Deployment',
                'description': 'Deploy integrated solutions to production.',
                'step_type': 'lesson',
            },
        ],
    },
]

ACHIEVEMENTS = [
    {'name': 'First Steps', 'description': 'Complete your first learning journey step', 'icon': 'footsteps', 'requirement_type': 'steps_completed', 'requirement_value': 1, 'points': 10},
    {'name': 'Quick Learner', 'description': 'Complete 5 learning steps', 'icon': 'bolt', 'requirement_type': 'steps_completed', 'requirement_value': 5, 'points': 25},
    {'name': 'Journey Complete', 'description': 'Complete your first learning journey', 'icon': 'trophy', 'requirement_type': 'journeys_completed', 'requirement_value': 1, 'points': 50},
    {'name': 'Dedicated Learner', 'description': 'Maintain a 7-day learning streak', 'icon': 'fire', 'requirement_type': 'streak_days', 'requirement_value': 7, 'points': 75},
    {'name': 'Explorer', 'description': 'Complete 3 different learning journeys', 'icon': 'compass', 'requirement_type': 'journeys_completed', 'requirement_value': 3, 'points': 100},
    {'name': 'Master', 'description': 'Complete all available learning journeys', 'icon': 'crown', 'requirement_type': 'journeys_completed', 'requirement_value': 5, 'points': 500},
]


class Command(BaseCommand):
    help = 'Seed learning journey templates and achievements'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Update existing templates with new step_type/content_meta data',
        )

    def handle(self, *args, **options):
        from core.models_learning_journey import LearningJourneyTemplate, LearningAchievement

        force = options.get('force', False)

        # Seed templates
        created_t = 0
        updated_t = 0
        for data in TEMPLATES:
            template, was_created = LearningJourneyTemplate.objects.get_or_create(
                name=data['name'],
                defaults=data,
            )
            if was_created:
                created_t += 1
            elif force:
                template.steps_data = data['steps_data']
                template.save(update_fields=['steps_data'])
                updated_t += 1

        # Seed achievements
        created_a = 0
        for data in ACHIEVEMENTS:
            _, was_created = LearningAchievement.objects.get_or_create(
                name=data['name'],
                defaults=data,
            )
            if was_created:
                created_a += 1

        msg = f'Seeded {created_t} templates (of {len(TEMPLATES)})'
        if updated_t:
            msg += f', updated {updated_t} existing'
        msg += f' and {created_a} achievements (of {len(ACHIEVEMENTS)})'
        self.stdout.write(self.style.SUCCESS(msg))
