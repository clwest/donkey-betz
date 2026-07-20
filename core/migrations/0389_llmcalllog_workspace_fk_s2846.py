"""
Session 2846 (A1 Week 1) — LLMCallLog.workspace ForeignKey.

Per-workspace attribution for the A1 SaaS product substrate.

Design ratified at S2846 (D1-D6 + zoom-out folds):
  * D1 SET_NULL: preserves history when workspace is deleted; BudgetController
    treats the resulting null bucket explicitly (Fold 3 guardrail).
  * D2 no backfill: existing rows stay null; a separate mgmt command can
    be added later if backfill is needed.
  * D5 (Rigby tweak): callers pass ProjectWorkspace object via workspace_resolver
    .get_active_workspace(user), not the id string.

Scope: single AddField + single AddIndex on LLMCallLog. Deliberately does
NOT include the unrelated model changes (Narrative*, HaiDispatchLog) that
`makemigrations` flagged as pending — those are separate arcs.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0388_legalresearchresult_case_profile_fk'),
    ]

    operations = [
        migrations.AddField(
            model_name='llmcalllog',
            name='workspace',
            field=models.ForeignKey(
                blank=True,
                help_text=(
                    'Workspace this call was attributed to (Session 2846). '
                    'Null when caller has no user or no active workspace, or '
                    'when the referenced workspace was later deleted.'
                ),
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name='llm_calls',
                to='core.projectworkspace',
            ),
        ),
        migrations.AddIndex(
            model_name='llmcalllog',
            index=models.Index(
                fields=['workspace', '-created_at'],
                name='llmcalllog_ws_created_idx',
            ),
        ),
    ]
