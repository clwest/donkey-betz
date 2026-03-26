"""Backfill role='tool' for conversation messages from code-worker/claude-code."""
from django.db import migrations


def backfill_tool_roles(apps, schema_editor):
    """
    Idempotent: set role='tool' for any PAConversationMessage whose
    source is 'code-worker' or 'claude-code' and whose role is NULL or 'user'.
    """
    try:
        PAConversationMessage = apps.get_model('core', 'PAConversationMessage')
    except LookupError:
        return  # Model doesn't exist yet – skip safely

    updated = PAConversationMessage.objects.filter(
        source__in=['code-worker', 'claude-code'],
    ).exclude(role='tool').update(role='tool')
    if updated:
        print(f"  Backfilled role='tool' on {updated} PAConversationMessage records.")


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0229_workflowrun'),  # adjust to latest real migration
    ]

    operations = [
        migrations.RunPython(backfill_tool_roles, migrations.RunPython.noop),
    ]
