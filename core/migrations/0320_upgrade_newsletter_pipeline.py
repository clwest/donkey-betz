"""Upgrade Newsletter Studio template with 8-agent parallel pipeline."""

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
        'name': 'Trend Analysis',
        'agent': 'TrendAnalysisAgent',
        'auto': True,
        'parallel_group': 'discovery',
        'description': 'Analyze patterns — what topics are emerging vs fading, connect the dots across sources',
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
    'TopicMinerAgent', 'TrendAnalysisAgent', 'ResearchAgent',
    'ContentStrategyAgent', 'ContentWriterAgent',
    'EditorAgent', 'SEOOptimizerAgent', 'ContrarianAgent',
]

NEWSLETTER_CATEGORIES = [
    'Pipeline — Topic Mining', 'Pipeline — Trend Analysis', 'Pipeline — Deep Research',
    'Pipeline — Content Strategy', 'Pipeline — Write Draft',
    'Pipeline — Edit & Polish', 'Pipeline — SEO & Headlines', 'Pipeline — Fact Check',
    'Newsletter Draft', 'Newsletter HTML', 'Newsletter Markdown',
    'Subject Lines', 'Publish Checklist',
]


def upgrade_newsletter(apps, schema_editor):
    WorkspaceTemplate = apps.get_model('core', 'WorkspaceTemplate')
    try:
        tmpl = WorkspaceTemplate.objects.get(slug='newsletter')
        tmpl.pipeline_stages = NEWSLETTER_PIPELINE
        tmpl.agent_pool = NEWSLETTER_AGENTS
        tmpl.deliverable_categories = NEWSLETTER_CATEGORIES
        tmpl.description = (
            'World-class newsletter business powered by 8 AI agents. '
            'Parallel discovery (topic mining + trend analysis + deep research), '
            'strategic content planning, AI writing with citations, '
            'parallel polish (editing + SEO), and fact-checking — '
            'all before human review and publishing.'
        )
        tmpl.save()
    except WorkspaceTemplate.DoesNotExist:
        pass


def reverse(apps, schema_editor):
    pass  # No reverse needed — template can be updated again


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0319_workspace_config_brief'),
    ]

    operations = [
        migrations.RunPython(upgrade_newsletter, reverse),
    ]
