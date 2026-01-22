# Generated migration for Session 259: Time Capsule Messages
# Sci-Fi Feature #13 - The Final Feature!

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0048_session_258_agent_predictions'),
    ]

    operations = [
        # TimeCapsule - Main time capsule model
        migrations.CreateModel(
            name='TimeCapsule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(help_text='Short title for the capsule', max_length=200)),
                ('message', models.TextField(help_text='Message to future self')),
                ('trigger', models.CharField(
                    choices=[
                        ('reflection', 'Self Reflection'),
                        ('milestone', 'Milestone Reached'),
                        ('prediction', 'Making a Prediction'),
                        ('lesson', 'Lesson Learned'),
                        ('goal', 'Setting a Goal'),
                        ('dream', 'Recording a Dream'),
                        ('question', 'Question for Future'),
                        ('celebration', 'Celebrating Success'),
                        ('change', 'Noting a Change'),
                        ('random', 'Random Thought'),
                    ],
                    default='reflection',
                    max_length=20
                )),
                ('context', models.JSONField(default=dict, help_text='Agent state at creation (mood, level, stats)')),
                ('tags', models.JSONField(default=list, help_text='Tags for categorization')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reveal_at', models.DateTimeField(help_text='When this capsule will be revealed')),
                ('status', models.CharField(
                    choices=[
                        ('sealed', 'Sealed'),
                        ('revealed', 'Revealed'),
                        ('expired', 'Expired'),
                    ],
                    default='sealed',
                    max_length=10
                )),
                ('revealed_at', models.DateTimeField(blank=True, null=True)),
                ('reflection', models.TextField(blank=True, help_text="Agent's thoughts when capsule was opened")),
                ('reflection_at', models.DateTimeField(blank=True, null=True)),
                ('comparison', models.JSONField(default=dict, help_text='Comparison of then vs now state')),
                ('is_featured', models.BooleanField(default=False)),
                ('views', models.PositiveIntegerField(default=0)),
                ('agent', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='time_capsules',
                    to='core.agent'
                )),
            ],
            options={
                'verbose_name': 'Time Capsule',
                'verbose_name_plural': 'Time Capsules',
                'ordering': ['-created_at'],
            },
        ),
        # Indexes for TimeCapsule
        migrations.AddIndex(
            model_name='timecapsule',
            index=models.Index(fields=['agent', 'status'], name='core_timeca_agent_i_a1b2c3_idx'),
        ),
        migrations.AddIndex(
            model_name='timecapsule',
            index=models.Index(fields=['status', 'reveal_at'], name='core_timeca_status__d4e5f6_idx'),
        ),
        migrations.AddIndex(
            model_name='timecapsule',
            index=models.Index(fields=['reveal_at'], name='core_timeca_reveal__g7h8i9_idx'),
        ),

        # TimeCapsuleReaction - User reactions to capsules
        migrations.CreateModel(
            name='TimeCapsuleReaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('reaction', models.CharField(
                    choices=[
                        ('touching', 'Touching'),
                        ('insightful', 'Insightful'),
                        ('funny', 'Funny'),
                        ('inspiring', 'Inspiring'),
                        ('nostalgic', 'Nostalgic'),
                        ('surprising', 'Surprising'),
                    ],
                    max_length=15
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('capsule', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='reactions',
                    to='core.timecapsule'
                )),
                ('user', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='time_capsule_reactions',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Time Capsule Reaction',
                'verbose_name_plural': 'Time Capsule Reactions',
                'unique_together': {('capsule', 'user', 'reaction')},
            },
        ),

        # TimeCapsuleStats - Agent statistics
        migrations.CreateModel(
            name='TimeCapsuleStats',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('total_capsules', models.PositiveIntegerField(default=0)),
                ('sealed_capsules', models.PositiveIntegerField(default=0)),
                ('revealed_capsules', models.PositiveIntegerField(default=0)),
                ('total_views', models.PositiveIntegerField(default=0)),
                ('total_reactions', models.PositiveIntegerField(default=0)),
                ('longest_seal_days', models.PositiveIntegerField(default=0)),
                ('avg_seal_days', models.FloatField(default=0.0)),
                ('favorite_trigger', models.CharField(blank=True, max_length=20)),
                ('capsules_this_month', models.PositiveIntegerField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('agent', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='time_capsule_stats',
                    to='core.agent'
                )),
            ],
            options={
                'verbose_name': 'Time Capsule Statistics',
                'verbose_name_plural': 'Time Capsule Statistics',
            },
        ),
    ]
