"""Seed initial workspace templates for Newsletter, LeadGen, Research, and Custom."""

from django.db import migrations


TEMPLATES = [
    {
        'name': 'Newsletter Studio',
        'slug': 'newsletter',
        'description': 'Automated newsletter business — research, draft, review, and publish on schedule. Includes content curation from spider feeds, AI-powered writing, editorial review pipeline, and multi-channel distribution.',
        'icon': '📰',
        'category': 'content',
        'sort_order': 1,
        'is_featured': True,
        'pipeline_stages': [
            {'name': 'Research', 'agent': 'ResearchAgent', 'auto': True, 'description': 'Gather trending topics and source material from spider feeds'},
            {'name': 'Outline', 'agent': 'ContentWriterAgent', 'auto': True, 'description': 'Generate newsletter outline from research'},
            {'name': 'Draft', 'agent': 'ContentWriterAgent', 'auto': True, 'description': 'Write full newsletter content with citations'},
            {'name': 'Edit', 'agent': 'EditorAgent', 'auto': True, 'description': 'Polish, fact-check, and optimize for engagement'},
            {'name': 'Review', 'agent': None, 'auto': False, 'requires_approval': True, 'description': 'Human review before publishing'},
            {'name': 'Publish', 'agent': None, 'auto': False, 'description': 'Distribute via email platform'},
        ],
        'agent_pool': [
            'ResearchAgent', 'ContentWriterAgent', 'EditorAgent',
            'SEOOptimizerAgent', 'TopicMinerAgent', 'TrendAnalysisAgent',
        ],
        'spider_subscriptions': [
            'techcrunch', 'hackernews', 'reddit', 'newsapi', 'theverge',
            'venturebeat', 'wired', 'arstechnica',
        ],
        'deliverable_categories': [
            'Newsletter Outline', 'Newsletter Draft', 'Newsletter HTML',
            'Newsletter Markdown', 'Subject Lines', 'Publish Checklist',
            'Subscriber Report', 'Performance Analytics',
        ],
        'default_settings': {
            'publish_schedule': 'weekly',
            'max_drafts_per_cycle': 3,
            'auto_publish': False,
            'quality_threshold': 0.7,
            'review_required': True,
            'target_word_count': 1500,
        },
        'default_quotas': {
            'max_deliverables_per_day': 10,
            'max_agent_runs_per_hour': 15,
            'max_initiatives': 3,
        },
    },
    {
        'name': 'LeadGen Studio',
        'slug': 'leadgen',
        'description': 'Automated lead generation — ICP research, prospect discovery, outreach content creation, and pipeline tracking. AI agents research markets, find prospects, and generate personalized outreach.',
        'icon': '🎯',
        'category': 'sales',
        'sort_order': 2,
        'is_featured': True,
        'pipeline_stages': [
            {'name': 'ICP Research', 'agent': 'CustomerResearchAgent', 'auto': True, 'description': 'Define ideal customer profile from market data'},
            {'name': 'Prospect Discovery', 'agent': 'ResearchAgent', 'auto': True, 'description': 'Find and score potential leads'},
            {'name': 'Content Creation', 'agent': 'ContentWriterAgent', 'auto': True, 'description': 'Generate personalized outreach content'},
            {'name': 'Review & Approve', 'agent': None, 'auto': False, 'requires_approval': True, 'description': 'Review prospects and outreach before sending'},
            {'name': 'Outreach', 'agent': None, 'auto': False, 'description': 'Execute outreach campaigns'},
            {'name': 'Track & Optimize', 'agent': 'PerformanceAnalystAgent', 'auto': True, 'description': 'Track responses and optimize approach'},
        ],
        'agent_pool': [
            'ResearchAgent', 'CustomerResearchAgent', 'CompetitorAnalysisAgent',
            'ContentWriterAgent', 'BrandStrategyAgent', 'MarketIntelligenceAgent',
            'PerformanceAnalystAgent',
        ],
        'spider_subscriptions': [
            'crunchbase', 'github', 'producthunt', 'remoteok',
            'weworkremotely', 'adzuna', 'venturebeat',
        ],
        'deliverable_categories': [
            'ICP Profile', 'Prospect List', 'Outreach Email',
            'Cold DM Script', 'Follow-up Sequence', 'Campaign Report',
            'Competitor Analysis', 'Market Brief',
        ],
        'default_settings': {
            'outreach_cadence': 'daily',
            'max_prospects_per_batch': 25,
            'auto_outreach': False,
            'personalization_level': 'high',
            'review_required': True,
        },
        'default_quotas': {
            'max_deliverables_per_day': 20,
            'max_agent_runs_per_hour': 20,
            'max_initiatives': 5,
        },
    },
    {
        'name': 'Research Hub',
        'slug': 'research',
        'description': 'Deep research workspace — market intelligence, competitive analysis, trend tracking, and strategic briefs. Ideal for due diligence, market entry research, and ongoing intelligence gathering.',
        'icon': '🔬',
        'category': 'intelligence',
        'sort_order': 3,
        'is_featured': True,
        'pipeline_stages': [
            {'name': 'Signal Collection', 'agent': None, 'auto': True, 'description': 'Gather signals from spider feeds and data sources'},
            {'name': 'Analysis', 'agent': 'ResearchAgent', 'auto': True, 'description': 'Analyze signals and generate insights'},
            {'name': 'Synthesis', 'agent': 'ThinkingAgent', 'auto': True, 'description': 'Synthesize findings into actionable briefs'},
            {'name': 'Review', 'agent': None, 'auto': False, 'requires_approval': True, 'description': 'Expert review of findings'},
            {'name': 'Deliver', 'agent': None, 'auto': False, 'description': 'Package and deliver research report'},
        ],
        'agent_pool': [
            'ResearchAgent', 'ThinkingAgent', 'CompetitorAnalysisAgent',
            'TrendAnalysisAgent', 'MarketIntelligenceAgent',
            'StockAnalystAgent', 'ContentWriterAgent',
        ],
        'spider_subscriptions': [
            'newsapi', 'techcrunch', 'crunchbase', 'hackernews',
            'reddit', 'sec_edgar', 'yahoo_finance', 'google_news',
        ],
        'deliverable_categories': [
            'Research Brief', 'Market Analysis', 'Competitive Landscape',
            'Trend Report', 'Due Diligence Pack', 'Strategic Memo',
            'Dossier', 'Intelligence Summary',
        ],
        'default_settings': {
            'research_depth': 'deep',
            'auto_generate_briefs': True,
            'review_required': True,
            'citation_required': True,
        },
        'default_quotas': {
            'max_deliverables_per_day': 15,
            'max_agent_runs_per_hour': 25,
            'max_initiatives': 10,
        },
    },
    {
        'name': 'Custom Workspace',
        'slug': 'custom',
        'description': 'Start from scratch — configure your own agent pool, pipeline stages, and data feeds. Full flexibility for unique business models.',
        'icon': '🛠️',
        'category': 'general',
        'sort_order': 10,
        'is_featured': False,
        'pipeline_stages': [],
        'agent_pool': [],
        'spider_subscriptions': [],
        'deliverable_categories': [],
        'default_settings': {
            'review_required': True,
        },
        'default_quotas': {
            'max_deliverables_per_day': 10,
            'max_agent_runs_per_hour': 10,
            'max_initiatives': 5,
        },
    },
]


def seed_templates(apps, schema_editor):
    WorkspaceTemplate = apps.get_model('core', 'WorkspaceTemplate')
    for tmpl in TEMPLATES:
        WorkspaceTemplate.objects.update_or_create(
            slug=tmpl['slug'],
            defaults=tmpl,
        )


def reverse(apps, schema_editor):
    WorkspaceTemplate = apps.get_model('core', 'WorkspaceTemplate')
    WorkspaceTemplate.objects.filter(slug__in=[t['slug'] for t in TEMPLATES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0316_workspace_templates_and_config'),
    ]

    operations = [
        migrations.RunPython(seed_templates, reverse),
    ]
