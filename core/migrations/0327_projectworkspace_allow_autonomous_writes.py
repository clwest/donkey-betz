"""
Add allow_autonomous_writes flag to ProjectWorkspace.

Fixes silent misrouting of autonomous agent deliverables into whatever
workspace happened to be user.is_active. Personal/game workspaces
(Ironwood, Build-in-Video, MentorForge, etc.) should be excluded from
autonomous write fallbacks — they're for specific interactive work,
not for autopilot content output.

Content workspaces (Operator Edge, Newsletter Studio, Donkey Betz,
Exit & Sale, Ebook Launch, etc.) stay allow_autonomous_writes=True
since that's where autonomous content belongs.

Default for all existing + new rows: True. Data migration flips the
known personal/tool/game workspaces to False by name match.
"""
from django.db import migrations, models


# Workspaces that should NOT receive silent autonomous deliverable writes.
# Substring-matched case-insensitively against ProjectWorkspace.name.
PERSONAL_OR_GAME_NAME_SUBSTRINGS = (
    'ironwood',
    'build-in-video',
    'live app tutorial',
    'mentorforge',
    'dealflowtracker',
    'pitchdeckforge',
    'sellerpilot',
    'scoutplays',
    'signalstudio',
    'codeclinic',
    'contract concierge',
    'conceptforge',
    'appforge',
    'complianceforge',
    'compliance sentinel',
    'testuser',
    'personal',
    'codebase',
)


def seed_autonomous_flag(apps, schema_editor):
    """Flip known personal/game workspaces to allow_autonomous_writes=False."""
    ProjectWorkspace = apps.get_model('core', 'ProjectWorkspace')
    from django.db.models import Q

    q = Q()
    for sub in PERSONAL_OR_GAME_NAME_SUBSTRINGS:
        q |= Q(name__icontains=sub)

    updated = ProjectWorkspace.objects.filter(q).update(allow_autonomous_writes=False)
    print(f'  [migration] Flipped {updated} personal/game workspaces to allow_autonomous_writes=False')


def reverse_seed(apps, schema_editor):
    """Reverse leaves the column at its default True — safe rollback."""
    ProjectWorkspace = apps.get_model('core', 'ProjectWorkspace')
    ProjectWorkspace.objects.update(allow_autonomous_writes=True)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0326_newsletter_subscriber'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectworkspace',
            name='allow_autonomous_writes',
            field=models.BooleanField(
                default=True,
                help_text=(
                    'Allow autonomous/scheduled agents to write deliverables into '
                    'this workspace as a fallback. Set False for personal, game, '
                    'or tool workspaces that should only receive content from '
                    'explicit user-initiated runs.'
                ),
            ),
        ),
        migrations.RunPython(seed_autonomous_flag, reverse_code=reverse_seed),
    ]
