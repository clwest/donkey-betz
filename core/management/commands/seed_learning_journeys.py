"""
Seed learning journey templates and achievements.
Session 990: Populate production database with learning content.
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
            {'title': 'Understanding AI Agents', 'description': 'Learn what AI agents are and how they can help you.'},
            {'title': 'Navigating the Agent List', 'description': 'Explore the 72 available agents and their specialties.'},
            {'title': 'Starting Your First Conversation', 'description': 'Have your first conversation with an agent.'},
            {'title': 'Understanding Agent Responses', 'description': 'Learn how to interpret and act on agent recommendations.'},
            {'title': 'Best Practices for Agent Interactions', 'description': 'Tips and tricks for getting the most from your agents.'},
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
            {'title': 'Overview of Content Agents', 'description': 'Meet the content creation team: Image, Video, Audio, and Content Writer agents.'},
            {'title': 'Creating AI Images', 'description': 'Learn to generate stunning images with the Image Agent.'},
            {'title': 'Video Generation Basics', 'description': 'Create engaging videos with the Video Agent.'},
            {'title': 'Audio and Voice Content', 'description': 'Generate podcasts, voiceovers, and audio content.'},
            {'title': 'Writing Compelling Content', 'description': 'Create articles, blogs, and copy with the Content Writer Agent.'},
            {'title': 'Content Strategy Integration', 'description': 'Combine all content types into a cohesive strategy.'},
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
            {'title': 'Understanding Automation Concepts', 'description': 'Learn the fundamentals of AI automation.'},
            {'title': 'Creating Your First Workflow', 'description': 'Build a simple automated workflow.'},
            {'title': 'Autonomous Agent Configuration', 'description': 'Set up agents to work autonomously.'},
            {'title': 'Monitoring and Adjusting', 'description': 'Learn to monitor and optimize your automations.'},
            {'title': 'Advanced Workflow Patterns', 'description': 'Master complex multi-agent workflows.'},
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
            {'title': 'Introduction to AI Analytics', 'description': 'Understand how AI transforms raw data into actionable insights.'},
            {'title': 'Working with Spider Data', 'description': 'Learn how spiders gather and process data from multiple sources.'},
            {'title': 'Trend Analysis Deep Dive', 'description': 'Use the Trend Analysis Agent to identify patterns.'},
            {'title': 'Market Intelligence', 'description': 'Leverage market data for business insights.'},
            {'title': 'Building Custom Dashboards', 'description': 'Create personalized analytics views.'},
            {'title': 'Predictive Analytics', 'description': 'Use AI predictions to anticipate future trends.'},
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
            {'title': 'Integration Architecture Overview', 'description': 'Understand how agents connect with external systems.'},
            {'title': 'Spider Network Integration', 'description': 'Connect agents with real-time data sources.'},
            {'title': 'Cross-Agent Communication', 'description': 'Enable agents to collaborate on complex tasks.'},
            {'title': 'Custom Tool Development', 'description': 'Create custom tools for specialized tasks.'},
            {'title': 'Production Deployment', 'description': 'Deploy integrated solutions to production.'},
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

    def handle(self, *args, **options):
        from core.models_learning_journey import LearningJourneyTemplate, LearningAchievement

        # Seed templates
        created_t = 0
        for data in TEMPLATES:
            _, was_created = LearningJourneyTemplate.objects.get_or_create(
                name=data['name'],
                defaults=data,
            )
            if was_created:
                created_t += 1

        # Seed achievements
        created_a = 0
        for data in ACHIEVEMENTS:
            _, was_created = LearningAchievement.objects.get_or_create(
                name=data['name'],
                defaults=data,
            )
            if was_created:
                created_a += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {created_t} templates (of {len(TEMPLATES)}) and {created_a} achievements (of {len(ACHIEVEMENTS)})'
        ))
