"""Add Final Rewrite stage to Newsletter pipeline — combines editor + fact check feedback into corrected draft."""

from django.db import migrations


NEWSLETTER_PIPELINE = [
    {
        'name': 'Topic Mining',
        'agent': 'TopicMinerAgent',
        'auto': True,
        'parallel_group': 'discovery',
        'description': 'Mine spider data and trending feeds for the hottest topics right now',
    },
    {
        'name': 'Deep Research',
        'agent': 'ResearchAgent',
        'auto': True,
        'parallel_group': 'discovery',
        'description': 'Deep dive research on the top trending topics using web search and spider data',
    },
    {
        'name': 'Content Strategy',
        'agent': 'ContentStrategyAgent',
        'auto': True,
        'description': 'Choose the best angle, structure the narrative arc, decide what makes this issue unique',
    },
    {
        'name': 'Write Draft',
        'agent': 'ContentWriterAgent',
        'auto': True,
        'description': 'Write the full newsletter with citations, engaging hooks, and clear structure',
    },
    {
        'name': 'Edit & Polish',
        'agent': 'EditorAgent',
        'auto': True,
        'parallel_group': 'review',
        'description': 'Review draft against workspace brief — check topic alignment, hook enforcement, audience relevance, actionability, and evidence quality. PASS or FAIL with specific fix instructions.',
    },
    {
        'name': 'Fact Check',
        'agent': 'ContrarianAgent',
        'auto': True,
        'parallel_group': 'review',
        'description': 'Challenge claims, verify facts, flag anything that needs evidence or correction. Check for saturation and suggest unique angles.',
    },
    {
        'name': 'Final Rewrite',
        'agent': 'ContentWriterAgent',
        'auto': True,
        'description': 'REWRITE the draft incorporating ALL feedback from the Editor and Fact Check stages. Fix every issue they flagged: cut off-topic sections, reinforce the hook, add missing evidence, improve actionability. This is the corrected final version.',
    },
    {
        'name': 'SEO & Headlines',
        'agent': 'SEOOptimizerAgent',
        'auto': True,
        'description': 'Optimize headline, subject lines, meta description, keywords for maximum reach',
    },
    {
        'name': 'Hooks & Distribution',
        'agent': 'DistributionAgent',
        'auto': True,
        'description': 'Generate subject line variants, optimize hooks, create CTAs, build distribution plan with social media snippets',
    },
    {
        'name': 'Review & Approve',
        'agent': None,
        'auto': False,
        'requires_approval': True,
        'description': 'Human review of the final newsletter before publishing',
    },
    {
        'name': 'Publish',
        'agent': None,
        'auto': False,
        'description': 'Distribute via email platform',
    },
]

NEWSLETTER_AGENTS = [
    'TopicMinerAgent', 'ResearchAgent',
    'ContentStrategyAgent', 'ContentWriterAgent',
    'EditorAgent', 'ContrarianAgent',
    'ContentWriterAgent',  # Rewrite stage
    'SEOOptimizerAgent', 'DistributionAgent',
]


def update_newsletter_pipeline(apps, schema_editor):
    WorkspaceTemplate = apps.get_model('core', 'WorkspaceTemplate')
    WorkspaceConfig = apps.get_model('core', 'WorkspaceConfig')

    try:
        template = WorkspaceTemplate.objects.get(slug='newsletter')
        template.pipeline_config = NEWSLETTER_PIPELINE
        template.agent_pool = NEWSLETTER_AGENTS
        template.save(update_fields=['pipeline_config', 'agent_pool'])

        # Update all existing newsletter workspace configs
        for config in WorkspaceConfig.objects.filter(template__slug='newsletter'):
            config.pipeline_config = NEWSLETTER_PIPELINE
            config.agent_pool = NEWSLETTER_AGENTS
            config.save(update_fields=['pipeline_config', 'agent_pool'])

    except WorkspaceTemplate.DoesNotExist:
        pass


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0321_remove_trend_analysis_from_newsletter'),
    ]

    operations = [
        migrations.RunPython(update_newsletter_pipeline, migrations.RunPython.noop),
    ]
