"""Session 1243 — rename intelligence.AgentExecution → ActionPlanExecution.

Removes the class-name collision with `core.AgentExecution` (canonical
orchestration model, 984 live rows) and `agents.AgentExecution` (dormant
rich-execution surface). The intelligence variant is a different concept —
per-step execution tracking for `ActionPlan` flows — and was just confusingly
named.

Table is empty (0 rows) so the rename is data-safe. RenameModel atomically
updates Django's app registry + renames the underlying Postgres table from
`intelligence_agentexecution` → `intelligence_actionplanexecution`.

Audit trail: Cat 2 Finding 2.2 in deliverable 86870fdd-e8d8-48d3-9760-
4bea75ec10e3 (Phantom Dependencies).
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("intelligence", "0002_earningrecord_revenuemetrics_spiderintelligencenode"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="AgentExecution",
            new_name="ActionPlanExecution",
        ),
    ]
