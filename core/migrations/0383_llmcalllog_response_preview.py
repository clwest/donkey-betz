"""Add response_preview field to LLMCallLog for stall diagnostics.

I-0302 Sub-phase 3 close-out (S2749). Ships with the Rigby gpt-5.2 stall
fix — provider fallback on stall + response body capture on stall.
See feedback_gpt5_stalls_on_multifold_design_prompts.md and
core/services/unified_pa_entrypoint.py for the diagnostic that led here.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0382_i0302_initiative_owner_not_null"),
    ]

    operations = [
        migrations.AddField(
            model_name="llmcalllog",
            name="response_preview",
            field=models.TextField(
                blank=True,
                help_text=(
                    "First 500 chars of the LLM response — populated on stall "
                    "(success=True but completion_tokens < 100)"
                ),
            ),
        ),
    ]
