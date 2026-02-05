# Generated manually for Session 930 - User Learning System
# Django makemigrations wasn't detecting the new models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0227_session_928_hivemind_initiative_fk'),
    ]

    operations = [
        # AgentFeedback - Track user feedback on agent executions
        migrations.CreateModel(
            name='AgentFeedback',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('execution_id', models.UUIDField(blank=True, help_text='AgentExecution ID this feedback is for', null=True)),
                ('rating', models.IntegerField(choices=[(1, 'Helpful'), (0, 'Neutral'), (-1, 'Not Helpful')])),
                ('feedback_text', models.TextField(blank=True, help_text='Optional detailed feedback')),
                ('context_snapshot', models.JSONField(default=dict, help_text='Snapshot of user context used for this execution')),
                ('task_description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_feedbacks', to='core.agent')),
                ('deliverable', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='feedbacks', to='core.deliverable')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agent_feedbacks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='agentfeedback',
            index=models.Index(fields=['user', 'agent'], name='core_agentf_user_id_5f8c3a_idx'),
        ),
        migrations.AddIndex(
            model_name='agentfeedback',
            index=models.Index(fields=['user', 'rating'], name='core_agentf_user_id_rating_idx'),
        ),
        migrations.AddIndex(
            model_name='agentfeedback',
            index=models.Index(fields=['created_at'], name='core_agentf_created_idx'),
        ),

        # GoalProgress - Track progress toward goals
        migrations.CreateModel(
            name='GoalProgress',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('progress_delta', models.IntegerField(help_text='Percentage points added (e.g., 5 for +5%)')),
                ('milestone_reached', models.CharField(blank=True, help_text='Optional milestone description', max_length=200)),
                ('notes', models.TextField(blank=True)),
                ('is_automatic', models.BooleanField(default=False, help_text='True if system-detected, False if user-entered')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('goal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goal_progress_entries', to='core.usergoal')),
                ('deliverable', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='goal_contributions', to='core.deliverable')),
                ('initiative', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='goal_contributions', to='core.initiative')),
            ],
            options={
                'verbose_name_plural': 'Goal progress entries',
                'ordering': ['-created_at'],
            },
        ),

        # UserSkill - Track user skill proficiency levels
        migrations.CreateModel(
            name='UserSkill',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('skill_name', models.CharField(max_length=100)),
                ('category', models.CharField(choices=[('technical', 'Technical'), ('creative', 'Creative'), ('analytical', 'Analytical'), ('communication', 'Communication'), ('leadership', 'Leadership'), ('domain', 'Domain Knowledge')], default='technical', max_length=50)),
                ('proficiency_level', models.IntegerField(default=1, help_text='Skill level from 1 (beginner) to 10 (expert)')),
                ('evidence_count', models.IntegerField(default=0, help_text='Number of times skill was demonstrated')),
                ('confidence', models.FloatField(default=0.5, help_text='Confidence in proficiency assessment (0-1)')),
                ('first_demonstrated', models.DateTimeField(auto_now_add=True)),
                ('last_demonstrated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tracked_skills', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-proficiency_level', '-evidence_count'],
            },
        ),
        migrations.AddConstraint(
            model_name='userskill',
            constraint=models.UniqueConstraint(fields=('user', 'skill_name'), name='unique_user_skill'),
        ),
        migrations.AddIndex(
            model_name='userskill',
            index=models.Index(fields=['user', 'category'], name='core_usersk_user_cat_idx'),
        ),
        migrations.AddIndex(
            model_name='userskill',
            index=models.Index(fields=['user', 'proficiency_level'], name='core_usersk_user_prof_idx'),
        ),

        # SkillDemonstration - Record individual skill demonstrations
        migrations.CreateModel(
            name='SkillDemonstration',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('quality_score', models.FloatField(help_text='Quality of this demonstration (0-1)')),
                ('context', models.TextField(blank=True, help_text='How the skill was demonstrated')),
                ('inference_source', models.CharField(default='deliverable', help_text='How skill was inferred (deliverable, manual, import)', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='demonstrations', to='core.userskill')),
                ('deliverable', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='skill_demonstrations', to='core.deliverable')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),

        # ProfileCompletionPrompt - Track profile completion prompts
        migrations.CreateModel(
            name='ProfileCompletionPrompt',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('field_category', models.CharField(max_length=50)),
                ('field_name', models.CharField(max_length=100)),
                ('prompt_text', models.TextField()),
                ('was_completed', models.BooleanField(default=False)),
                ('was_dismissed', models.BooleanField(default=False)),
                ('response_value', models.TextField(blank=True)),
                ('prompted_at', models.DateTimeField(auto_now_add=True)),
                ('responded_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_prompts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-prompted_at'],
            },
        ),
        migrations.AddIndex(
            model_name='profilecompletionprompt',
            index=models.Index(fields=['user', 'was_completed'], name='core_profcp_user_comp_idx'),
        ),
    ]
