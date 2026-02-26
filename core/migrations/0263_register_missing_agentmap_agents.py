"""
Session 1088: Register 6 AGENT_MAP agents missing from Agent DB table.

These agents exist in code (AGENT_MAP) and execute successfully, but have no
Agent row, so AgentExecution records can't be created (FK to Agent is required).

Also retires PromptEngineeringAgent (is_active=False, 0 executions).
"""
from django.db import migrations


# AGENT_MAP agents that have no Agent DB record
MISSING_AGENTS = [
    {
        'name': 'BookmakerAgent',
        'agent_type': 'market',
        'specialization': 'sports_analysis',
        'description': (
            'Analyzes bookmaker behavior patterns, line-setting tendencies, '
            'and market-making strategies across sportsbooks.'
        ),
    },
    {
        'name': 'DecisionEnforcerAgent',
        'agent_type': 'core',
        'specialization': 'decision_enforcement',
        'description': (
            'Enforces pending decisions from the boardroom by converting '
            'approved items into concrete agent tasks and tracking completion.'
        ),
    },
    {
        'name': 'EditorAgent',
        'agent_type': 'content',
        'specialization': 'content_enhancement',
        'description': (
            'Enhances and polishes written content: structural editing, '
            'tone adjustment, clarity improvements, and style consistency.'
        ),
    },
    {
        'name': 'PlatformAuditAgent',
        'agent_type': 'core',
        'specialization': 'platform_audit',
        'description': (
            'Internal platform health inspector: checks agent execution stats, '
            'spider freshness, service uptime, and system configuration.'
        ),
    },
    {
        'name': 'TalkingCharacterAgent',
        'agent_type': 'creative',
        'specialization': 'talking_head_video',
        'description': (
            'Creates talking-head character videos: TTS audio generation, '
            'base image selection, and lip-sync video compositing.'
        ),
    },
    {
        'name': 'VoiceCriticAgent',
        'agent_type': 'content',
        'specialization': 'voice_quality',
        'description': (
            'Scores and critiques AI-generated voice/audio quality: '
            'naturalness, pacing, emotional tone, and clarity.'
        ),
    },
]


def register_agents(apps, schema_editor):
    Agent = apps.get_model('core', 'Agent')
    for agent_data in MISSING_AGENTS:
        Agent.objects.get_or_create(
            name=agent_data['name'],
            defaults={
                'agent_type': agent_data['agent_type'],
                'specialization': agent_data['specialization'],
                'description': agent_data['description'],
                'is_active': True,
            },
        )


def unregister_agents(apps, schema_editor):
    Agent = apps.get_model('core', 'Agent')
    names = [a['name'] for a in MISSING_AGENTS]
    Agent.objects.filter(name__in=names, total_executions=0).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0262_add_plan_v1_step_resume_fields'),
    ]

    operations = [
        migrations.RunPython(register_agents, unregister_agents),
    ]
