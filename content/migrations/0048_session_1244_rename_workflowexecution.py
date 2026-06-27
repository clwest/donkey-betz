"""Session 1244 — rename content.WorkflowExecution → content.ContentWorkflowExecution.

Cat 2 dormant cleanup batch. Removes the cross-app naming collision with
`core.WorkflowExecution` (in `core.models_unified_system`) by giving the
content variant a more descriptive name that reflects its scope.

The content variant ties to the content pipeline (UnifiedBaseModel base
+ workflow/user fields). The core variant is generic orchestration
execution tracking (different concept).

Both tables empty (0 rows). RenameModel is atomic and data-safe.

Audit: deliverable 86870fdd-… Finding 2.3.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0047_session_1235_backfill_clobbered_extracted_metadata"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="WorkflowExecution",
            new_name="ContentWorkflowExecution",
        ),
    ]
