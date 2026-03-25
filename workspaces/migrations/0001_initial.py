from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Workspace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='owned_workspaces',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('members', models.ManyToManyField(
                    blank=True,
                    related_name='workspaces',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
