"""Session 1244 — delete core.AgentLearningSession.

Removed as part of the Cat 2 dormant cleanup batch. Was registered in both
`core.AgentLearningSession` (this) and `ai_intelligence.AgentLearningSession`
(in ai_core.intelligence.models). The ai_intelligence variant has a writer
in `persistent_learning_engine.py:65` (gracefully wrapped in try/except).
The core variant had ZERO consumers anywhere in the codebase — verified via
AST import scan + grep across all production files.

Table is empty (0 rows). Safe DeleteModel.

Audit: deliverable 86870fdd-… Finding 2.3 cross-app duplicate inventory.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0367_session_1243_rename_spiderdata_to_legacy"),
    ]

    operations = [
        migrations.DeleteModel(
            name="AgentLearningSession",
        ),
    ]
