# Session 1077: Fix initiative owner_id column type from integer to UUID
# The FK was created as integer but core_unifieduser.id is UUID
# Can't cast integer→UUID, so drop column and re-add as correct type

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0309_deliverable_workspace_fk"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Step 1: Drop the broken integer column entirely
        migrations.RemoveField(
            model_name='initiative',
            name='owner',
        ),
        # Step 2: Re-add as proper UUID FK
        migrations.AddField(
            model_name='initiative',
            name='owner',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='owned_initiatives',
                to=settings.AUTH_USER_MODEL,
                help_text='Session 996: Human owner accountable for this initiative',
            ),
        ),
    ]
