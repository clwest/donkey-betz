from django.db import migrations


def set_donkey_betz_test_command(apps, schema_editor):
    Repo = apps.get_model('executor_repos', 'Repo')
    Repo.objects.filter(
        repo_url='https://github.com/clwest/donkey-betz-platform',
        test_command='',
    ).update(test_command='make test-fast')
    # Also match by slug in case URL differs
    Repo.objects.filter(
        repo_url__contains='donkey-betz-platform',
        test_command='',
    ).update(test_command='make test-fast')


def reverse_set_donkey_betz_test_command(apps, schema_editor):
    Repo = apps.get_model('executor_repos', 'Repo')
    Repo.objects.filter(
        repo_url__contains='donkey-betz-platform',
        test_command='make test-fast',
    ).update(test_command='')


class Migration(migrations.Migration):

    dependencies = [
        ('executor_repos', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            set_donkey_betz_test_command,
            reverse_set_donkey_betz_test_command,
        ),
    ]
