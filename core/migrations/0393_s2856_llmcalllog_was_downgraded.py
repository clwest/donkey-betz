"""Session 2856 — LLMCallLog.was_downgraded + pre_downgrade_model_id.

Adds two additive nullable fields to the billing-plane LLMCallLog so
`enforcement_report --include_downgrade_savings` (S2853) can distinguish
enforcer-forced downgrades from calls whose primary model is already the
downgrade target (PersonalAssistantAgent, orchestration coordinators —
see DEFAULT_AGENT_LLM_CONFIGS). Removes the OVER-estimate caveat that
shipped with S2853.

Backfill policy: historical rows default to was_downgraded=False /
pre_downgrade_model_id=''. Windows overlapping the migration boundary
under-report by the pre-migration forced-downgrade count — no inference
backfill (fragile; would reintroduce the ambiguity we're removing).

Companion runtime change: llm_enforcer.enforce_real_ai now resets
self._budget_downgrade_model = None at the top of each call so the
process-wide singleton doesn't leak a live downgrade forward across
subsequent calls after the flag becomes inactive.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0392_s2854_align_llmmodel_prices_to_canonical'),
    ]

    operations = [
        migrations.AddField(
            model_name='llmcalllog',
            name='was_downgraded',
            field=models.BooleanField(
                default=False,
                help_text=(
                    'True when the enforcer forced this call off its '
                    'originally-requested model via the budget-downgrade '
                    'path. False for calls that natively target the '
                    'downgrade model.'
                ),
            ),
        ),
        migrations.AddField(
            model_name='llmcalllog',
            name='pre_downgrade_model_id',
            field=models.CharField(
                blank=True,
                default='',
                help_text=(
                    'The model that would have been called had the '
                    'downgrade not fired. Empty string when '
                    'was_downgraded=False.'
                ),
                max_length=100,
            ),
        ),
    ]
