"""
Session 1006: Register market analysis agents in Agent DB.

GamePredictor, LineMovementAnalyzer, and SharpActionDetector were added
to AGENT_MAP in Session 995B but never registered in the Agent table.
GamePredictor's _store_predictions() silently skips MLPrediction storage
when the Agent record is missing.
"""

from django.db import migrations


MARKET_AGENTS = [
    {
        'name': 'GamePredictor',
        'agent_type': 'core',
        'description': (
            'Predicts game outcomes using odds data, historical patterns, '
            'and LLM analysis. Stores predictions in MLPrediction model.'
        ),
        'specialization': 'sports_prediction',
        'is_active': True,
    },
    {
        'name': 'LineMovementAnalyzer',
        'agent_type': 'core',
        'description': (
            'Detects meaningful line movements across bookmakers to identify '
            'sharp money action, reverse line movement, and steam moves.'
        ),
        'specialization': 'line_movement',
        'is_active': True,
    },
    {
        'name': 'SharpActionDetector',
        'agent_type': 'core',
        'description': (
            'Identifies professional betting patterns by analyzing odds across '
            'multiple bookmakers for signs of syndicate action and smart money.'
        ),
        'specialization': 'sharp_action',
        'is_active': True,
    },
]


def register_agents(apps, schema_editor):
    Agent = apps.get_model('core', 'Agent')
    for agent_data in MARKET_AGENTS:
        Agent.objects.get_or_create(
            name=agent_data['name'],
            defaults=agent_data,
        )


def unregister_agents(apps, schema_editor):
    Agent = apps.get_model('core', 'Agent')
    Agent.objects.filter(
        name__in=[a['name'] for a in MARKET_AGENTS]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0243_session_1003_backfill_founder_intent'),
    ]

    operations = [
        migrations.RunPython(register_agents, unregister_agents),
    ]
