"""S2805 Phase 3.1 P1 — CaseProfile/LegalCase unification (scoped migration).

Adds `LegalDocument.case_profile` FK → CaseProfile so the LegalDocDrafterAgent
can bind newly-drafted documents to the richer Session 406 CaseProfile model
instead of the legacy Session 403 LegalCase model.

Scoped by hand — Django's makemigrations detected ~43 unrelated model-drift
operations (narrative, haidispatchlog, index renames, etc.) that pre-date
this arc; those belong to their own migrations and are deliberately NOT
smuggled into this P1 change.

Zero-row backfill: LegalDocument.case_profile starts NULL for all existing
rows (only 1 row exists at S2805 open — case=None already).
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0386_s2803_legal_document_dispatch_log"),
    ]

    operations = [
        migrations.AddField(
            model_name="legaldocument",
            name="case_profile",
            field=models.ForeignKey(
                blank=True,
                help_text=(
                    "S2805 Phase 3.1 P1: canonical case linkage. "
                    "Replaces `case` (LegalCase) for new saves."
                ),
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="legal_documents",
                to="core.caseprofile",
            ),
        ),
    ]
