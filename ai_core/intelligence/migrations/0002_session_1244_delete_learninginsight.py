"""Session 1244 — delete ai_intelligence.LearningInsight.

Cat 2 dormant cleanup batch. The canonical `core.LearningInsight` (in
`core.models.ai_learning.models`) has 2 active consumers
(`models_feedback_processing.py` + `implementation_executor.py`).

`ai_intelligence.LearningInsight` was imported in
`persistent_learning_engine.py:25` inside a try/except block, but
NEVER used in any `.objects.X` call. Pure dead import. Removed from the
import block in the same PR.

Note: `ai_core/intelligence/learning_loop.py:92` and
`ai_core/intelligence/bluesky_learning_bridge.py:25` reference a class
also named `LearningInsight` — but those are non-Django namespace classes
(dataclasses), not the Django model being deleted here. No collision.

Table is empty (0 rows). The model has a ManyToManyField to
AgentLearningEvent (via `source_events` related_name='insights') — the
implicit through table will also be dropped automatically by Django.

Audit: deliverable 86870fdd-… Finding 2.3.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ai_intelligence", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(
            name="LearningInsight",
        ),
    ]
