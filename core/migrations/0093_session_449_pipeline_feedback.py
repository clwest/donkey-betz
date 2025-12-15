# Generated manually for Session 449
# Pipeline Feedback Models for Learning Loops

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0092_session_445_ai_series'),
    ]

    operations = [
        migrations.CreateModel(
            name='PipelineStageFeedback',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('stage', models.CharField(choices=[
                    ('research', 'Research - Topic and audience analysis'),
                    ('script', 'Script - Script/narration generation'),
                    ('image', 'Image - Character and scene generation'),
                    ('voice', 'Voice - Voiceover generation'),
                    ('video', 'Video - Video content generation'),
                    ('package', 'Package - Final content packaging')
                ], db_index=True, max_length=20)),
                ('feedback_type', models.CharField(choices=[
                    ('user_rating', 'User Rating (1-5 stars)'),
                    ('implicit', 'Implicit (completion, engagement)'),
                    ('automated', 'Automated (quality checks)'),
                    ('ab_test', 'A/B Test Result')
                ], default='user_rating', max_length=20)),
                ('rating', models.DecimalField(decimal_places=2, help_text='Rating from 1.0 to 5.0', max_digits=3, validators=[django.core.validators.MinValueValidator(1.0), django.core.validators.MaxValueValidator(5.0)])),
                ('context', models.JSONField(default=dict, help_text='Stage-specific context (style, voice, audience, etc.)')),
                ('comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('series', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stage_feedback', to='core.aiseries')),
                ('episode', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stage_feedback', to='core.seriesepisode')),
                ('content_package', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stage_feedback', to='core.contentpackage')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pipeline_feedback', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='StylePresetPerformance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('style_preset', models.CharField(db_index=True, help_text='Style preset (pixar, disney, anime, etc.)', max_length=50)),
                ('target_audience', models.CharField(db_index=True, help_text='Target audience category', max_length=100)),
                ('series_type', models.CharField(blank=True, help_text='Series type (educational, entertainment, marketing)', max_length=50)),
                ('total_uses', models.IntegerField(default=0)),
                ('avg_rating', models.DecimalField(decimal_places=2, default=0.0, max_digits=3)),
                ('approval_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Percentage of content approved/published (0-100)', max_digits=5)),
                ('engagement_score', models.DecimalField(decimal_places=2, default=0.0, help_text='Normalized engagement score (0-100)', max_digits=5)),
                ('successful_series_count', models.IntegerField(default=0)),
                ('viral_content_count', models.IntegerField(default=0)),
                ('rejection_count', models.IntegerField(default=0)),
                ('confidence_score', models.DecimalField(decimal_places=2, default=0.0, help_text='Confidence in this recommendation (0-1)', max_digits=3)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-avg_rating', '-total_uses'],
                'unique_together': {('style_preset', 'target_audience', 'series_type')},
            },
        ),
        migrations.CreateModel(
            name='VoicePerformance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('voice_id', models.CharField(db_index=True, help_text='ElevenLabs voice ID', max_length=100)),
                ('voice_name', models.CharField(db_index=True, max_length=100)),
                ('voice_style', models.CharField(blank=True, help_text='Voice style category (friendly, authoritative, etc.)', max_length=50)),
                ('series_type', models.CharField(blank=True, max_length=50)),
                ('target_audience', models.CharField(blank=True, max_length=100)),
                ('total_uses', models.IntegerField(default=0)),
                ('avg_rating', models.DecimalField(decimal_places=2, default=0.0, max_digits=3)),
                ('approval_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('completion_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Video completion rate when this voice is used', max_digits=5)),
                ('confidence_score', models.DecimalField(decimal_places=2, default=0.0, max_digits=3)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-avg_rating', '-total_uses'],
                'unique_together': {('voice_id', 'series_type', 'target_audience')},
            },
        ),
        migrations.CreateModel(
            name='ContentEngagement',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('platform', models.CharField(db_index=True, help_text='Platform where content is published', max_length=50)),
                ('external_id', models.CharField(blank=True, help_text='External platform ID for tracking', max_length=200)),
                ('views', models.IntegerField(default=0)),
                ('likes', models.IntegerField(default=0)),
                ('shares', models.IntegerField(default=0)),
                ('comments', models.IntegerField(default=0)),
                ('saves', models.IntegerField(default=0)),
                ('avg_watch_time_seconds', models.IntegerField(default=0)),
                ('completion_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Percentage who watched to completion (0-100)', max_digits=5)),
                ('revenue', models.DecimalField(decimal_places=2, default=0.0, help_text='Revenue generated by this content', max_digits=10)),
                ('outcome', models.CharField(choices=[
                    ('pending', 'Pending - Not yet delivered'),
                    ('delivered', 'Delivered - Sent to client'),
                    ('approved', 'Approved - Client accepted'),
                    ('rejected', 'Rejected - Client rejected'),
                    ('published', 'Published - Live on platform'),
                    ('viral', 'Viral - High engagement')
                ], default='pending', max_length=20)),
                ('outcome_notes', models.TextField(blank=True)),
                ('content_context', models.JSONField(default=dict, help_text='Content configuration at time of creation')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('series', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='engagement_metrics', to='core.aiseries')),
                ('episode', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='engagement_metrics', to='core.seriesepisode')),
                ('content_package', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='engagement_metrics', to='core.contentpackage')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ResearchQueryPerformance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('query_type', models.CharField(db_index=True, help_text='Type of research query', max_length=50)),
                ('query_keywords', models.JSONField(default=list, help_text='Keywords used in query')),
                ('series_type', models.CharField(blank=True, max_length=50)),
                ('target_audience', models.CharField(blank=True, max_length=100)),
                ('total_uses', models.IntegerField(default=0)),
                ('avg_content_rating', models.DecimalField(decimal_places=2, default=0.0, help_text='Average rating of content produced', max_digits=3)),
                ('avg_engagement_score', models.DecimalField(decimal_places=2, default=0.0, help_text='Average engagement from this research', max_digits=5)),
                ('successful_series_count', models.IntegerField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-avg_content_rating', '-total_uses'],
            },
        ),
        migrations.CreateModel(
            name='PipelineLearningInsight',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('stage', models.CharField(choices=[
                    ('research', 'Research - Topic and audience analysis'),
                    ('script', 'Script - Script/narration generation'),
                    ('image', 'Image - Character and scene generation'),
                    ('voice', 'Voice - Voiceover generation'),
                    ('video', 'Video - Video content generation'),
                    ('package', 'Package - Final content packaging')
                ], db_index=True, max_length=20)),
                ('insight_type', models.CharField(help_text='Type of insight', max_length=50)),
                ('insight_summary', models.CharField(help_text='Human-readable insight summary', max_length=500)),
                ('insight_data', models.JSONField(default=dict, help_text='Structured insight data')),
                ('applicable_to', models.JSONField(default=dict, help_text='Conditions where this insight applies')),
                ('confidence', models.DecimalField(decimal_places=2, default=0.0, help_text='Confidence in this insight (0-1)', max_digits=3)),
                ('sample_size', models.IntegerField(default=0, help_text='Number of data points')),
                ('estimated_impact', models.DecimalField(decimal_places=2, default=0.0, help_text='Estimated improvement percentage', max_digits=5)),
                ('is_active', models.BooleanField(default=True, help_text='Whether to apply this insight')),
                ('times_applied', models.IntegerField(default=0)),
                ('times_validated', models.IntegerField(default=0, help_text='Times insight was validated')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('expires_at', models.DateTimeField(blank=True, help_text='When to re-evaluate', null=True)),
            ],
            options={
                'ordering': ['-confidence', '-sample_size'],
            },
        ),
        migrations.AddIndex(
            model_name='pipelinestagefeedback',
            index=models.Index(fields=['stage', 'created_at'], name='core_pipeli_stage_5c3d4c_idx'),
        ),
        migrations.AddIndex(
            model_name='pipelinestagefeedback',
            index=models.Index(fields=['series', 'stage'], name='core_pipeli_series__8e4a2b_idx'),
        ),
        migrations.AddIndex(
            model_name='contentengagement',
            index=models.Index(fields=['platform', 'outcome'], name='core_conten_platfor_3d8e1a_idx'),
        ),
        migrations.AddIndex(
            model_name='contentengagement',
            index=models.Index(fields=['series', 'outcome'], name='core_conten_series__9f7b3c_idx'),
        ),
        migrations.AddIndex(
            model_name='pipelinelearninginsight',
            index=models.Index(fields=['stage', 'is_active'], name='core_pipeli_stage_a2c8d1_idx'),
        ),
    ]
