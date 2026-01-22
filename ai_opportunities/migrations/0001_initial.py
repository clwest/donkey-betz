# Generated manually for AI Opportunities
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
            name='AIStrategy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('strategy_id', models.CharField(max_length=100, unique=True)),
                ('title', models.CharField(max_length=300)),
                ('source', models.CharField(max_length=100)),
                ('url', models.URLField(blank=True, max_length=500)),
                ('strategy_type', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('potential_revenue', models.CharField(max_length=100)),
                ('time_to_implement', models.CharField(max_length=100)),
                ('difficulty', models.CharField(max_length=50)),
                ('final_score', models.FloatField()),
                ('discovered_date', models.DateTimeField(auto_now_add=True)),
                ('actionable_steps', models.JSONField(default=list)),
            ],
            options={
                'ordering': ['-final_score', '-discovered_date'],
            },
        ),
        migrations.CreateModel(
            name='GeneratedProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_id', models.CharField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('project_type', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('generated', 'Generated'), ('testing', 'Testing'), ('deployed', 'Deployed'), ('archived', 'Archived')], default='generated', max_length=20)),
                ('revenue_potential', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('advisor_insights', models.JSONField(blank=True, default=list)),
                ('ready_to_launch', models.BooleanField(default=False)),
                ('launch_command', models.CharField(blank=True, max_length=200)),
                ('strategy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ai_opportunities.aistrategy')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_projects', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProjectFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=200)),
                ('file_type', models.CharField(choices=[('python', 'Python'), ('javascript', 'JavaScript'), ('html', 'HTML'), ('css', 'CSS'), ('markdown', 'Markdown'), ('json', 'JSON'), ('yaml', 'YAML'), ('txt', 'Text'), ('requirements', 'Requirements'), ('env', 'Environment')], max_length=20)),
                ('content', models.TextField()),
                ('file_size', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='ai_opportunities.generatedproject')),
            ],
            options={
                'ordering': ['filename'],
                'unique_together': {('project', 'filename')},
            },
        ),
        migrations.CreateModel(
            name='ProjectDeployment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deployed', models.BooleanField(default=False)),
                ('deployment_url', models.URLField(blank=True, max_length=500)),
                ('deployment_platform', models.CharField(blank=True, max_length=100)),
                ('has_openai_key', models.BooleanField(default=False)),
                ('has_other_keys', models.BooleanField(default=False)),
                ('total_runs', models.IntegerField(default=0)),
                ('successful_runs', models.IntegerField(default=0)),
                ('last_run', models.DateTimeField(blank=True, null=True)),
                ('actual_revenue', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('currency', models.CharField(default='USD', max_length=3)),
                ('deployed_at', models.DateTimeField(blank=True, null=True)),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='deployment', to='ai_opportunities.generatedproject')),
            ],
        ),
    ]