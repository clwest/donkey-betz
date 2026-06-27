"""Session 1244 — rename coleadership.AgentRecommendation → AdvisorDecisionRecommendation.

Cat 2 dormant cleanup batch. Removes the cross-app naming collision with
`core.AgentRecommendation` (in `core.models_agent_memory`) by giving the
coleadership variant a more descriptive name.

The coleadership variant has fields like `decision`, `agent_template`,
`stance`, `summary`, `recommendation_text`, `risk_analysis`,
`alternative_paths` — clearly an Advisor's Decision Recommendation
artifact. The core variant is a PA-side agent-recommendation surface
(different concept).

Both tables empty (0 rows). RenameModel is atomic and data-safe.

Audit: deliverable 86870fdd-… Finding 2.3.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("coleadership", "0003_alter_coleadershipdecision_project"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="AgentRecommendation",
            new_name="AdvisorDecisionRecommendation",
        ),
    ]
