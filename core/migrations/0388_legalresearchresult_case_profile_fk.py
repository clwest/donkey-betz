"""S2807 Phase 3.1 P1.b — LegalResearchResult unification (scoped migration).

Adds `LegalResearchResult.case_profile` FK → CaseProfile so the
LegalDocDrafterAgent's research-save path binds to the richer Session 406
CaseProfile model instead of the legacy Session 403 LegalCase model. Mirrors
the S2805 P1 pattern for LegalDocument (`0387_legal_document_case_profile_fk`).

Scoped by hand — Django's makemigrations tends to smuggle unrelated model
drift into auto-generated migrations. This file contains ONLY the P1.b
AddField.

Zero-row backfill: LegalResearchResult.case_profile starts NULL for all
existing rows (only 1 row exists at S2807 open — case FK already NULL;
LegalCase table = 0 rows).
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0387_legal_document_case_profile_fk"),
    ]

    operations = [
        migrations.AddField(
            model_name="legalresearchresult",
            name="case_profile",
            field=models.ForeignKey(
                blank=True,
                help_text=(
                    "S2807 Phase 3.1 P1.b: canonical case linkage. "
                    "Replaces `case` (LegalCase) for new saves."
                ),
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="legal_research_results",
                to="core.caseprofile",
            ),
        ),
    ]
