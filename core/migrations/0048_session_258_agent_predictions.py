# Generated migration for Session 258: Agent Predictions / Prophecies
# Sci-Fi Feature #12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0047_session_257_memory_clusters'),
    ]

    operations = [
        # AgentPrediction - Main prediction model
        migrations.CreateModel(
            name='AgentPrediction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(help_text='Short summary of prediction', max_length=200)),
                ('prediction', models.TextField(help_text='Detailed prediction statement')),
                ('category', models.CharField(
                    choices=[
                        ('trend', 'Trend Prediction'),
                        ('market', 'Market Prediction'),
                        ('technology', 'Technology Prediction'),
                        ('creative', 'Creative Prediction'),
                        ('opportunity', 'Opportunity'),
                        ('user_behavior', 'User Behavior'),
                        ('seasonal', 'Seasonal Pattern'),
                        ('competition', 'Competition'),
                        ('general', 'General'),
                    ],
                    default='general',
                    max_length=30
                )),
                ('tags', models.JSONField(default=list, help_text='List of relevant tags')),
                ('source', models.CharField(
                    choices=[
                        ('analysis', 'Data Analysis'),
                        ('pattern', 'Pattern Recognition'),
                        ('dream', 'Agent Dream'),
                        ('conversation', 'Conversation'),
                        ('hive_mind', 'Hive Mind Session'),
                        ('memory', 'Memory Insight'),
                        ('intuition', 'Agent Intuition'),
                        ('external', 'External Signal'),
                    ],
                    default='analysis',
                    max_length=20
                )),
                ('source_reference', models.JSONField(default=dict, help_text='Reference to source (dream ID, conversation ID, etc.)')),
                ('confidence', models.FloatField(default=0.7, help_text="Agent's confidence in this prediction (0.0-1.0)")),
                ('timeframe', models.CharField(
                    choices=[
                        ('week', 'Within a Week'),
                        ('month', 'Within a Month'),
                        ('quarter', 'Within 3 Months'),
                        ('half_year', 'Within 6 Months'),
                        ('year', 'Within a Year'),
                        ('long_term', 'Long Term (1+ years)'),
                    ],
                    default='quarter',
                    max_length=20
                )),
                ('deadline', models.DateTimeField(blank=True, help_text='When this prediction should be verified by', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending'),
                        ('verified_true', 'Verified True'),
                        ('verified_false', 'Verified False'),
                        ('partially_true', 'Partially True'),
                        ('expired', 'Expired'),
                        ('cancelled', 'Cancelled'),
                    ],
                    default='pending',
                    max_length=20
                )),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('verification_notes', models.TextField(blank=True)),
                ('verification_evidence', models.JSONField(default=dict, help_text='Evidence supporting verification (URLs, data, etc.)')),
                ('verified_by', models.CharField(
                    blank=True,
                    choices=[
                        ('auto', 'Automatic'),
                        ('user', 'User'),
                        ('agent', 'Agent'),
                    ],
                    max_length=10,
                    null=True
                )),
                ('accuracy_score', models.FloatField(blank=True, help_text='How accurate was the prediction (0.0-1.0)', null=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('upvotes', models.PositiveIntegerField(default=0)),
                ('views', models.PositiveIntegerField(default=0)),
                ('comments', models.JSONField(default=list, help_text='User comments on prediction')),
                ('agent', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='predictions',
                    to='core.agent'
                )),
            ],
            options={
                'verbose_name': 'Agent Prediction',
                'verbose_name_plural': 'Agent Predictions',
                'ordering': ['-created_at'],
            },
        ),
        # Indexes for AgentPrediction
        migrations.AddIndex(
            model_name='agentprediction',
            index=models.Index(fields=['agent', '-created_at'], name='core_agentp_agent_i_a1b2c3_idx'),
        ),
        migrations.AddIndex(
            model_name='agentprediction',
            index=models.Index(fields=['status', '-created_at'], name='core_agentp_status__d4e5f6_idx'),
        ),
        migrations.AddIndex(
            model_name='agentprediction',
            index=models.Index(fields=['category', 'status'], name='core_agentp_categor_g7h8i9_idx'),
        ),
        migrations.AddIndex(
            model_name='agentprediction',
            index=models.Index(fields=['deadline'], name='core_agentp_deadlin_j0k1l2_idx'),
        ),
        migrations.AddIndex(
            model_name='agentprediction',
            index=models.Index(fields=['is_featured', '-created_at'], name='core_agentp_is_feat_m3n4o5_idx'),
        ),

        # PredictionStats - Agent prediction accuracy statistics
        migrations.CreateModel(
            name='PredictionStats',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('total_predictions', models.PositiveIntegerField(default=0)),
                ('pending_predictions', models.PositiveIntegerField(default=0)),
                ('verified_predictions', models.PositiveIntegerField(default=0)),
                ('predictions_correct', models.PositiveIntegerField(default=0)),
                ('predictions_wrong', models.PositiveIntegerField(default=0)),
                ('predictions_partial', models.PositiveIntegerField(default=0)),
                ('overall_accuracy', models.FloatField(default=0.0)),
                ('weighted_accuracy', models.FloatField(default=0.0, help_text='Accuracy weighted by confidence level')),
                ('current_streak', models.IntegerField(default=0)),
                ('best_streak', models.PositiveIntegerField(default=0)),
                ('worst_streak', models.PositiveIntegerField(default=0)),
                ('category_accuracy', models.JSONField(default=dict, help_text='Accuracy breakdown by category')),
                ('accuracy_rank', models.PositiveIntegerField(blank=True, help_text='Rank among all agents', null=True)),
                ('last_prediction_at', models.DateTimeField(blank=True, null=True)),
                ('last_verification_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('agent', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='prediction_stats',
                    to='core.agent'
                )),
            ],
            options={
                'verbose_name': 'Prediction Statistics',
                'verbose_name_plural': 'Prediction Statistics',
                'ordering': ['-overall_accuracy', '-total_predictions'],
            },
        ),

        # PredictionComment - Comments on predictions
        migrations.CreateModel(
            name='PredictionComment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('author_type', models.CharField(
                    choices=[('user', 'User'), ('agent', 'Agent')],
                    default='user',
                    max_length=10
                )),
                ('content', models.TextField()),
                ('sentiment', models.CharField(
                    choices=[
                        ('agree', 'Agrees'),
                        ('disagree', 'Disagrees'),
                        ('neutral', 'Neutral'),
                        ('question', 'Question'),
                    ],
                    default='neutral',
                    max_length=10
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('prediction', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='comment_objects',
                    to='core.agentprediction'
                )),
                ('user', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='prediction_comments',
                    to=settings.AUTH_USER_MODEL
                )),
                ('agent', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='prediction_comments',
                    to='core.agent'
                )),
            ],
            options={
                'verbose_name': 'Prediction Comment',
                'verbose_name_plural': 'Prediction Comments',
                'ordering': ['created_at'],
            },
        ),

        # PredictionFollowUp - Follow-up predictions
        migrations.CreateModel(
            name='PredictionFollowUp',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('relationship', models.CharField(
                    choices=[
                        ('extends', 'Extends'),
                        ('revises', 'Revises'),
                        ('confirms', 'Confirms'),
                        ('counters', 'Counters'),
                        ('builds_on', 'Builds On'),
                    ],
                    default='extends',
                    max_length=20
                )),
                ('explanation', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('original', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='follow_ups',
                    to='core.agentprediction'
                )),
                ('follow_up', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='follows_from',
                    to='core.agentprediction'
                )),
            ],
            options={
                'verbose_name': 'Prediction Follow-Up',
                'verbose_name_plural': 'Prediction Follow-Ups',
                'unique_together': {('original', 'follow_up')},
            },
        ),
    ]
