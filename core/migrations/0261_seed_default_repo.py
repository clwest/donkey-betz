"""
Session 1075: Seed the default donkey-betz-platform repo.
"""

from django.db import migrations


def seed_repo(apps, schema_editor):
    Repo = apps.get_model('core', 'Repo')
    Repo.objects.get_or_create(
        name='donkey-betz-platform',
        defaults={
            'repo_url': 'https://github.com/clwest/donkey-betz-platform',
            'default_base_branch': 'main',
            'allowed_base_branches': ['main'],
            'protected_branches': ['main'],
            'policy_profile': 'moderate',
            'is_active': True,
        },
    )


def unseed_repo(apps, schema_editor):
    Repo = apps.get_model('core', 'Repo')
    Repo.objects.filter(name='donkey-betz-platform').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0260_add_repo_model_and_link_to_execution_run'),
    ]

    operations = [
        migrations.RunPython(seed_repo, unseed_repo),
    ]
