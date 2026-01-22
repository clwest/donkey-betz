"""
Session 223: Opportunity Engine Migration
=========================================

Phase 1 of The Creative Intelligence Empire

Adds:
- New scoring fields to existing Opportunity model
- OpportunityScore model (detailed scoring breakdown)
- OpportunityAction model (track actions taken)
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0027_session_221_analytics'),
    ]

    operations = [
        # Add new scoring fields to existing Opportunity model
        migrations.AddField(
            model_name='opportunity',
            name='spider_data',
            field=models.ForeignKey(
                blank=True,
                help_text='Link to spider-collected data that generated this opportunity',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='scored_opportunities',
                to='core.spiderdata'
            ),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='source_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('trend', 'Trending Topic'),
                    ('job', 'Job/Gig Opportunity'),
                    ('product', 'Product Demand'),
                    ('news', 'News Event'),
                    ('competition', 'Competitor Gap'),
                    ('seasonal', 'Seasonal Demand'),
                    ('viral', 'Viral Content'),
                    ('tech', 'Technology Trend'),
                ],
                help_text='What kind of data generated this opportunity',
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='category',
            field=models.CharField(
                blank=True,
                choices=[
                    ('digital_product', 'Digital Product'),
                    ('freelance', 'Freelance Service'),
                    ('content', 'Content Creation'),
                    ('template', 'Template/Asset'),
                    ('course', 'Course/Education'),
                    ('software', 'Software/Tool'),
                    ('consulting', 'Consulting'),
                    ('affiliate', 'Affiliate Marketing'),
                ],
                help_text='Category for content creation opportunity',
                max_length=30,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='profit_potential',
            field=models.IntegerField(
                blank=True,
                help_text='Estimated profit potential (1-100)',
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(100)
                ],
            ),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='competition_level',
            field=models.IntegerField(
                blank=True,
                help_text='Competition level - higher means MORE competition (1-100)',
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(100)
                ],
            ),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='effort_required',
            field=models.IntegerField(
                blank=True,
                help_text='Effort required - higher means MORE effort (1-100)',
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(100)
                ],
            ),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='time_sensitivity',
            field=models.IntegerField(
                blank=True,
                help_text='Time sensitivity - higher means MORE urgent (1-100)',
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(100)
                ],
            ),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='overall_score',
            field=models.IntegerField(
                blank=True,
                help_text='Overall opportunity score (calculated from other scores)',
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(100)
                ],
            ),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='suggested_content_types',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="List of content types: ['logo', 'thumbnail', 'video']"
            ),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='suggested_workflows',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='List of recommended workflows to execute'
            ),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='estimated_cost',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Estimated cost to create content for this opportunity',
                max_digits=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='keywords',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='Related keywords/tags'
            ),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='market_data',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Market research data'
            ),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='competitor_info',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Competitor analysis'
            ),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='advisor_recommendations',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Recommendations from advisors consulted about this opportunity'
            ),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='scored_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When this opportunity was scored',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='acted_on_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When user started acting on this opportunity',
                null=True,
            ),
        ),

        # OpportunityScore Model
        migrations.CreateModel(
            name='OpportunityScore',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('profit_reasoning', models.TextField(blank=True, help_text='Explanation for profit potential score')),
                ('competition_reasoning', models.TextField(blank=True, help_text='Explanation for competition level score')),
                ('effort_reasoning', models.TextField(blank=True, help_text='Explanation for effort required score')),
                ('timing_reasoning', models.TextField(blank=True, help_text='Explanation for time sensitivity score')),
                ('confidence_level', models.IntegerField(
                    default=70,
                    help_text='Confidence in the accuracy of this scoring (1-100)',
                    validators=[
                        django.core.validators.MinValueValidator(1),
                        django.core.validators.MaxValueValidator(100)
                    ]
                )),
                ('data_sources', models.JSONField(default=list, help_text='List of data sources used to calculate scores')),
                ('advisors_consulted', models.JSONField(default=list, help_text='List of advisors who provided input')),
                ('scoring_model_version', models.CharField(default='v1.0', help_text='Version of the scoring algorithm used', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('opportunity', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='score_details',
                    to='core.opportunity'
                )),
            ],
            options={
                'app_label': 'core',
            },
        ),

        # OpportunityAction Model
        migrations.CreateModel(
            name='OpportunityAction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action_type', models.CharField(
                    choices=[
                        ('viewed', 'Viewed'),
                        ('analyzed', 'Analyzed'),
                        ('approved', 'Approved'),
                        ('rejected', 'Rejected'),
                        ('started', 'Started Creating'),
                        ('content_created', 'Content Created'),
                        ('published', 'Published'),
                        ('revenue_logged', 'Revenue Logged'),
                    ],
                    max_length=30
                )),
                ('content_ids', models.JSONField(default=list, help_text='IDs of content created for this opportunity')),
                ('workflow_used', models.CharField(blank=True, help_text='Which workflow was used', max_length=100)),
                ('outcome', models.JSONField(default=dict, help_text='Outcome data: revenue, engagement, etc.')),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('opportunity', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='actions',
                    to='core.opportunity'
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'ordering': ['-created_at'],
                'app_label': 'core',
            },
        ),
    ]
