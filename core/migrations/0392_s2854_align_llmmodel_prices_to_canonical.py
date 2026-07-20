"""
S2854 pricing canonicalization arc — Phase 1 (C+).

Realigns existing ``LLMModel`` rows for gpt-5.2 + gpt-5-mini to match the
canonical ``core/services/pricing_catalog.py`` rates. The seed data in
``models_llm_routing.DEFAULT_MODELS`` was updated in the same PR, so fresh
installs come up correctly; this migration corrects any existing rows created
by prior ``setup_llm_routing`` runs.

Semantic delta this migration ships:
- gpt-5-mini: cost_per_1m_input 0.15 → 0.50 (3.33× higher; was under-priced
  by the ``LLMProviderRegistry``-populated seed vs the ``llm_enforcer`` billing
  lineage that produces real ``LLMCallLog`` rows).
- gpt-5-mini: cost_per_1m_output 0.60 → 1.50 (2.5× higher, same reason).
- gpt-5.2: cost_per_1m_input 5.00 → 1.75 (2.86× lower; was over-priced by the
  seed vs the enforcer billing lineage).
- gpt-5.2: cost_per_1m_output 20.00 → 14.00 (1.43× lower, same reason).

Only display + admin surfaces read these columns today; the router uses the
inline provider-adapter tables (which are also migrated to delegate to
pricing_catalog in the same PR). No LLMCallLog row is retroactively repriced.
"""

from django.db import migrations
from decimal import Decimal


_CANONICAL_ALIGNMENTS = [
    ('openai', 'gpt-5-mini', Decimal('0.50'), Decimal('1.50')),
    ('openai', 'gpt-5.2', Decimal('1.75'), Decimal('14.00')),
]


def _align_forward(apps, _schema_editor):
    LLMModel = apps.get_model('core', 'LLMModel')
    LLMProvider = apps.get_model('core', 'LLMProvider')
    for provider_name, model_id, input_price, output_price in _CANONICAL_ALIGNMENTS:
        provider = LLMProvider.objects.filter(name=provider_name).first()
        if provider is None:
            continue
        LLMModel.objects.filter(provider=provider, model_id=model_id).update(
            cost_per_1m_input=input_price,
            cost_per_1m_output=output_price,
        )


def _align_backward(apps, _schema_editor):
    """Restore pre-S2854 rates if this migration is unapplied."""
    LLMModel = apps.get_model('core', 'LLMModel')
    LLMProvider = apps.get_model('core', 'LLMProvider')
    reverse = [
        ('openai', 'gpt-5-mini', Decimal('0.15'), Decimal('0.60')),
        ('openai', 'gpt-5.2', Decimal('5.00'), Decimal('20.00')),
    ]
    for provider_name, model_id, input_price, output_price in reverse:
        provider = LLMProvider.objects.filter(name=provider_name).first()
        if provider is None:
            continue
        LLMModel.objects.filter(provider=provider, model_id=model_id).update(
            cost_per_1m_input=input_price,
            cost_per_1m_output=output_price,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0391_s2849_autopilotaction_workspace_default_cap_type'),
    ]

    operations = [
        migrations.RunPython(_align_forward, _align_backward),
    ]
