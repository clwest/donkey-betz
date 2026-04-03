"""Remove TrendAnalysisAgent from Newsletter pipeline — too slow, blocks discovery."""

from django.db import migrations

NEWSLETTER_PIPELINE = [
    {
        'name': 'Topic Mining',
        'agent': 'TopicMinerAgent',
        'auto': True,
        'parallel_group': 'discovery',
        'description': 'Mine spider data and trending feeds for the hottest topics right now',
    },
    # TrendAnalysisAgent REMOVED — Session 1103: blocks pipeline for 20+ min,
    # 45% success rate, and ResearchAgent already covers the evidence gathering.
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
        'parallel_group': 'polish',
        'description': 'Polish prose, strengthen hooks, improve structure, fix any issues',
    },
    {
        'name': 'SEO & Headlines',
        'agent': 'SEOOptimizerAgent',
        'auto': True,
        'parallel_group': 'polish',
        'description': 'Optimize headline, subject lines, meta description, keywords for maximum reach',
    },
    {
        'name': 'Fact Check',
        'agent': 'ContrarianAgent',
        'auto': True,
        'description': 'Challenge claims, verify facts, flag anything that needs evidence or correction',
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
    'EditorAgent', 'SEOOptimizerAgent', 'ContrarianAgent',
    'DistributionAgent',
]


def upgrade(apps, schema_editor):
    WorkspaceTemplate = apps.get_model('core', 'WorkspaceTemplate')
    try:
        tmpl = WorkspaceTemplate.objects.get(slug='newsletter')
        tmpl.pipeline_stages = NEWSLETTER_PIPELINE
        tmpl.agent_pool = NEWSLETTER_AGENTS
        tmpl.description = (
            'Newsletter powered by 7 AI agents. '
            'Parallel discovery (topic mining + deep research with evidence cards), '
            'strategic content planning, AI writing with GPT-5.2 citations, '
            'parallel polish (editing + SEO), fact-checking, and distribution — '
            'all before human review and publishing.'
        )
        tmpl.save()
    except WorkspaceTemplate.DoesNotExist:
        pass

    # Also update any existing workspace configs using the newsletter template
    try:
        WorkspaceConfig = apps.get_model('core', 'WorkspaceConfig')
        for config in WorkspaceConfig.objects.filter(template__slug='newsletter'):
            config.pipeline_config = NEWSLETTER_PIPELINE
            config.save(update_fields=['pipeline_config'])
    except LookupError:
        pass  # Model may not exist in this migration state


def reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0320_upgrade_newsletter_pipeline'),
    ]

    operations = [
        migrations.RunPython(upgrade, reverse),
    ]
