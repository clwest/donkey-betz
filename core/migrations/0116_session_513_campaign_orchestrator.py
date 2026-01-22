# Generated for Session 513 - Campaign Orchestrator Models

from django.db import migrations, models
import django.db.models.deletion
import uuid
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0115_session_507_narrative_alert_watch_fields'),
    ]

    operations = [
        # 1. Create Campaign model
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[
                    ('intake', 'Intake'),
                    ('research', 'Research'),
                    ('strategy', 'Strategy'),
                    ('creation', 'Creation'),
                    ('review', 'Review'),
                    ('revision', 'Revision'),
                    ('complete', 'Complete'),
                    ('delivered', 'Delivered'),
                    ('cancelled', 'Cancelled'),
                ], default='intake', max_length=20)),
                ('budget_tier', models.CharField(default='starter', max_length=20)),
                ('client_name', models.CharField(blank=True, max_length=255)),
                ('product_name', models.CharField(max_length=255)),
                ('product_description', models.TextField()),
                ('product_features', models.JSONField(blank=True, default=list)),
                ('target_market', models.TextField(help_text='Who is the target audience?')),
                ('target_location', models.CharField(blank=True, max_length=255)),
                ('target_demographics', models.JSONField(blank=True, default=dict)),
                ('competitors', models.JSONField(blank=True, default=list)),
                ('brand_colors', models.JSONField(blank=True, default=list)),
                ('brand_fonts', models.JSONField(blank=True, default=list)),
                ('brand_style', models.CharField(blank=True, max_length=100)),
                ('logo_image_id', models.UUIDField(blank=True, null=True)),
                ('platforms', models.JSONField(blank=True, default=list)),
                ('research_data', models.JSONField(blank=True, default=dict)),
                ('competitor_analysis', models.JSONField(blank=True, default=dict)),
                ('market_trends', models.JSONField(blank=True, default=dict)),
                ('content_strategy', models.JSONField(blank=True, default=dict)),
                ('brand_direction', models.JSONField(blank=True, default=dict)),
                ('seo_keywords', models.JSONField(blank=True, default=list)),
                ('progress_percent', models.IntegerField(default=0)),
                ('current_phase', models.CharField(default='intake', max_length=50)),
                ('phase_details', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('delivered_at', models.DateTimeField(blank=True, null=True)),
                ('total_api_calls', models.IntegerField(default=0)),
                ('total_tokens_used', models.IntegerField(default=0)),
                ('execution_log', models.JSONField(blank=True, default=list)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campaigns', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Campaign',
                'verbose_name_plural': 'Campaigns',
                'ordering': ['-created_at'],
            },
        ),
        # 2. Create CampaignDeliverable model
        migrations.CreateModel(
            name='CampaignDeliverable',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('deliverable_type', models.CharField(choices=[
                    ('ad_copy', 'Ad Copy'),
                    ('image', 'Image'),
                    ('video', 'Video'),
                    ('email', 'Email'),
                    ('social_post', 'Social Post'),
                    ('banner', 'Banner Ad'),
                    ('voiceover', 'Voiceover'),
                    ('brand_guide', 'Brand Guide'),
                    ('other', 'Other'),
                ], max_length=20)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(choices=[
                    ('pending', 'Pending'),
                    ('creating', 'Creating'),
                    ('complete', 'Complete'),
                    ('failed', 'Failed'),
                    ('approved', 'Approved'),
                    ('rejected', 'Rejected'),
                ], default='pending', max_length=20)),
                ('platform', models.CharField(choices=[
                    ('facebook', 'Facebook'),
                    ('instagram', 'Instagram'),
                    ('twitter', 'Twitter/X'),
                    ('linkedin', 'LinkedIn'),
                    ('craigslist', 'Craigslist'),
                    ('youtube', 'YouTube'),
                    ('email', 'Email'),
                    ('website', 'Website'),
                    ('print', 'Print'),
                    ('general', 'General'),
                ], default='general', max_length=20)),
                ('content_text', models.TextField(blank=True)),
                ('content_data', models.JSONField(blank=True, default=dict)),
                ('file_url', models.URLField(blank=True)),
                ('file_path', models.CharField(blank=True, max_length=500)),
                ('image_history_id', models.UUIDField(blank=True, null=True)),
                ('video_id', models.UUIDField(blank=True, null=True)),
                ('audio_id', models.UUIDField(blank=True, null=True)),
                ('width', models.IntegerField(blank=True, null=True)),
                ('height', models.IntegerField(blank=True, null=True)),
                ('version', models.IntegerField(default=1)),
                ('variant', models.CharField(blank=True, max_length=50)),
                ('tags', models.JSONField(blank=True, default=list)),
                ('created_by_agent', models.CharField(blank=True, max_length=100)),
                ('agent_prompt', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deliverables', to='core.campaign')),
            ],
            options={
                'verbose_name': 'Campaign Deliverable',
                'verbose_name_plural': 'Campaign Deliverables',
                'ordering': ['deliverable_type', 'created_at'],
            },
        ),
        # 3. Create CampaignResearch model
        migrations.CreateModel(
            name='CampaignResearch',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('research_type', models.CharField(choices=[
                    ('market_trends', 'Market Trends'),
                    ('competitor', 'Competitor Analysis'),
                    ('customer', 'Customer Research'),
                    ('seo', 'SEO Keywords'),
                    ('pricing', 'Pricing Research'),
                    ('content', 'Content Ideas'),
                    ('web_search', 'Web Search Results'),
                ], max_length=30)),
                ('title', models.CharField(max_length=255)),
                ('summary', models.TextField(blank=True)),
                ('data', models.JSONField(default=dict)),
                ('source', models.CharField(blank=True, max_length=100)),
                ('source_urls', models.JSONField(blank=True, default=list)),
                ('agent_name', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='research_items', to='core.campaign')),
            ],
            options={
                'verbose_name': 'Campaign Research',
                'verbose_name_plural': 'Campaign Research Items',
                'ordering': ['research_type', '-created_at'],
            },
        ),
    ]
