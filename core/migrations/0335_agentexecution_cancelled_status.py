# Session 1098 PR #3: add 'cancelled' to AgentExecution.status choices so
# cooperative cancellation (via CancelTokenRegistry) can land a distinct
# terminal state rather than reusing 'failed'. Dashboards filter
# cancelled-by-user runs out of the crash-class "failed" bucket.
#
# No data migration required — existing rows keep their current status.
# The only change is the choices list on the CharField.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0334_llmcallevent"),
    ]

    operations = [
        migrations.AlterField(
            model_name="agentexecution",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("in_progress", "In Progress"),
                    ("completed", "Completed"),
                    ("failed", "Failed"),
                    ("cancelled", "Cancelled"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
    ]
