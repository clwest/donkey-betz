"""Session 1244 — delete ai_opportunities.GeneratedProject + dependent models.

Cat 2 dormant cleanup batch. The canonical `core.GeneratedProject` model
(in `core.models.projects.models`) has 13+ active importers and is the
actual generated-project model used throughout the platform. The
`ai_opportunities.GeneratedProject` model had ZERO importers anywhere
in the codebase — verified via AST import scan.

Dependent chain (deleted in reverse-dependency order):
1. ProjectDeployment (OneToOne to GeneratedProject)
2. ProjectFile (FK to GeneratedProject)
3. GeneratedProject (the model itself)

All 3 tables empty (0 rows). Safe cascade delete.

Audit: deliverable 86870fdd-… Finding 2.3.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ai_opportunities", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ProjectDeployment",
        ),
        migrations.DeleteModel(
            name="ProjectFile",
        ),
        migrations.DeleteModel(
            name="GeneratedProject",
        ),
    ]
