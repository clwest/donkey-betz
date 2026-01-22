# Generated manually for Session 479
# 14 New Autonomous Situations

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0108_session_477_situation_triggers"),
    ]

    operations = [
        # =====================================================================
        # CREATIVE & CONTENT
        # =====================================================================

        # DesignTrend
        migrations.CreateModel(
            name="DesignTrend",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=200)),
                ("category", models.CharField(choices=[
                    ("color", "Color Palette"),
                    ("typography", "Typography"),
                    ("layout", "Layout Pattern"),
                    ("illustration", "Illustration Style"),
                    ("animation", "Animation/Motion"),
                    ("ui_pattern", "UI Pattern"),
                    ("brand_style", "Brand Style"),
                ], max_length=50)),
                ("description", models.TextField(blank=True)),
                ("colors", models.JSONField(default=list)),
                ("fonts", models.JSONField(default=list)),
                ("keywords", models.JSONField(default=list)),
                ("example_urls", models.JSONField(default=list)),
                ("popularity_score", models.FloatField(default=0.0)),
                ("momentum_score", models.FloatField(default=0.0)),
                ("confidence_score", models.FloatField(default=0.0)),
                ("source_spiders", models.JSONField(default=list)),
                ("spider_data_ids", models.JSONField(default=list)),
                ("first_detected", models.DateTimeField(auto_now_add=True)),
                ("last_seen", models.DateTimeField(auto_now=True)),
                ("peak_date", models.DateTimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("is_rising", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "design_trend",
                "ordering": ["-popularity_score", "-momentum_score"],
            },
        ),

        # DesignSystemUpdate
        migrations.CreateModel(
            name="DesignSystemUpdate",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("update_type", models.CharField(choices=[
                    ("color_palette", "Color Palette"),
                    ("typography", "Typography"),
                    ("component_style", "Component Style"),
                    ("animation", "Animation"),
                    ("full_refresh", "Full Refresh"),
                ], max_length=50)),
                ("previous_values", models.JSONField(default=dict)),
                ("new_values", models.JSONField(default=dict)),
                ("applied", models.BooleanField(default=False)),
                ("applied_at", models.DateTimeField(blank=True, null=True)),
                ("user_feedback", models.CharField(blank=True, choices=[
                    ("positive", "Positive"),
                    ("neutral", "Neutral"),
                    ("negative", "Negative"),
                ], max_length=20, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("source_trends", models.ManyToManyField(related_name="system_updates", to="core.designtrend")),
            ],
            options={
                "db_table": "design_system_update",
                "ordering": ["-created_at"],
            },
        ),

        # ViralContentPrediction
        migrations.CreateModel(
            name="ViralContentPrediction",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=500)),
                ("content_type", models.CharField(choices=[
                    ("article", "Article"),
                    ("video", "Video"),
                    ("image", "Image"),
                    ("thread", "Thread/Post"),
                    ("meme", "Meme"),
                ], max_length=50)),
                ("topic", models.CharField(max_length=200)),
                ("keywords", models.JSONField(default=list)),
                ("viral_score", models.FloatField(default=0.0)),
                ("engagement_potential", models.FloatField(default=0.0)),
                ("shareability_score", models.FloatField(default=0.0)),
                ("timing_score", models.FloatField(default=0.0)),
                ("trend_alignment", models.FloatField(default=0.0)),
                ("emotional_trigger", models.CharField(blank=True, max_length=50, null=True)),
                ("controversy_level", models.FloatField(default=0.0)),
                ("similar_viral_content", models.JSONField(default=list)),
                ("spider_signals", models.JSONField(default=dict)),
                ("recommended_platforms", models.JSONField(default=list)),
                ("optimal_posting_time", models.DateTimeField(blank=True, null=True)),
                ("suggested_hashtags", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("prediction_expires", models.DateTimeField(blank=True, null=True)),
                ("content_created", models.BooleanField(default=False)),
                ("actual_engagement", models.JSONField(blank=True, null=True)),
                ("prediction_accuracy", models.FloatField(blank=True, null=True)),
            ],
            options={
                "db_table": "viral_content_prediction",
                "ordering": ["-viral_score", "-created_at"],
            },
        ),

        # ThumbnailVariant
        migrations.CreateModel(
            name="ThumbnailVariant",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("content_title", models.CharField(max_length=500)),
                ("content_url", models.URLField(blank=True, null=True)),
                ("variant_name", models.CharField(max_length=100)),
                ("image_url", models.URLField(blank=True, null=True)),
                ("image_path", models.CharField(blank=True, max_length=500, null=True)),
                ("primary_color", models.CharField(blank=True, max_length=20, null=True)),
                ("has_face", models.BooleanField(default=False)),
                ("has_text", models.BooleanField(default=False)),
                ("text_content", models.CharField(blank=True, max_length=200, null=True)),
                ("style", models.CharField(blank=True, max_length=50, null=True)),
                ("impressions", models.IntegerField(default=0)),
                ("clicks", models.IntegerField(default=0)),
                ("ctr", models.FloatField(default=0.0)),
                ("is_control", models.BooleanField(default=False)),
                ("is_winner", models.BooleanField(default=False)),
                ("test_started", models.DateTimeField(blank=True, null=True)),
                ("test_ended", models.DateTimeField(blank=True, null=True)),
                ("learned_insights", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "thumbnail_variant",
                "ordering": ["-ctr", "-clicks"],
            },
        ),

        # =====================================================================
        # INCOME & OPPORTUNITIES
        # =====================================================================

        # JobMatchProfile
        migrations.CreateModel(
            name="JobMatchProfile",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("skills", models.JSONField(default=list)),
                ("experience_years", models.IntegerField(default=0)),
                ("preferred_roles", models.JSONField(default=list)),
                ("industries", models.JSONField(default=list)),
                ("remote_only", models.BooleanField(default=True)),
                ("min_salary", models.IntegerField(blank=True, null=True)),
                ("max_commute_miles", models.IntegerField(blank=True, null=True)),
                ("preferred_company_sizes", models.JSONField(default=list)),
                ("location", models.CharField(blank=True, max_length=200, null=True)),
                ("willing_to_relocate", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "job_match_profile",
            },
        ),

        # JobMatch
        migrations.CreateModel(
            name="JobMatch",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=500)),
                ("company", models.CharField(max_length=200)),
                ("location", models.CharField(blank=True, max_length=200, null=True)),
                ("is_remote", models.BooleanField(default=False)),
                ("salary_min", models.IntegerField(blank=True, null=True)),
                ("salary_max", models.IntegerField(blank=True, null=True)),
                ("job_url", models.URLField()),
                ("source_spider", models.CharField(max_length=100)),
                ("spider_data_id", models.UUIDField(blank=True, null=True)),
                ("overall_match_score", models.FloatField(default=0.0)),
                ("skills_match", models.FloatField(default=0.0)),
                ("experience_match", models.FloatField(default=0.0)),
                ("salary_match", models.FloatField(default=0.0)),
                ("location_match", models.FloatField(default=0.0)),
                ("culture_match", models.FloatField(default=0.0)),
                ("matched_skills", models.JSONField(default=list)),
                ("missing_skills", models.JSONField(default=list)),
                ("match_reasons", models.JSONField(default=list)),
                ("concerns", models.JSONField(default=list)),
                ("viewed", models.BooleanField(default=False)),
                ("saved", models.BooleanField(default=False)),
                ("applied", models.BooleanField(default=False)),
                ("dismissed", models.BooleanField(default=False)),
                ("alert_sent", models.BooleanField(default=False)),
                ("alert_sent_at", models.DateTimeField(blank=True, null=True)),
                ("posted_date", models.DateTimeField(blank=True, null=True)),
                ("discovered_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("profile", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="core.jobmatchprofile")),
            ],
            options={
                "db_table": "job_match",
                "ordering": ["-overall_match_score", "-discovered_at"],
            },
        ),

        # FreelanceOpportunity
        migrations.CreateModel(
            name="FreelanceOpportunity",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=500)),
                ("description", models.TextField(blank=True)),
                ("client_name", models.CharField(blank=True, max_length=200, null=True)),
                ("platform", models.CharField(max_length=100)),
                ("gig_url", models.URLField()),
                ("budget_type", models.CharField(choices=[
                    ("fixed", "Fixed Price"),
                    ("hourly", "Hourly"),
                    ("negotiable", "Negotiable"),
                ], max_length=20)),
                ("budget_min", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("budget_max", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("required_skills", models.JSONField(default=list)),
                ("experience_level", models.CharField(blank=True, max_length=50, null=True)),
                ("estimated_duration", models.CharField(blank=True, max_length=100, null=True)),
                ("opportunity_score", models.FloatField(default=0.0)),
                ("pay_rate_score", models.FloatField(default=0.0)),
                ("skill_match_score", models.FloatField(default=0.0)),
                ("competition_score", models.FloatField(default=0.0)),
                ("proposals_count", models.IntegerField(blank=True, null=True)),
                ("avg_competitor_rate", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("source_spider", models.CharField(max_length=100)),
                ("spider_data_id", models.UUIDField(blank=True, null=True)),
                ("posted_date", models.DateTimeField(blank=True, null=True)),
                ("discovered_at", models.DateTimeField(auto_now_add=True)),
                ("deadline", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "db_table": "freelance_opportunity",
                "ordering": ["-opportunity_score", "-discovered_at"],
            },
        ),

        # SideHustle
        migrations.CreateModel(
            name="SideHustle",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=200)),
                ("category", models.CharField(choices=[
                    ("dropshipping", "Dropshipping"),
                    ("print_on_demand", "Print on Demand"),
                    ("digital_products", "Digital Products"),
                    ("affiliate", "Affiliate Marketing"),
                    ("content_creation", "Content Creation"),
                    ("services", "Services"),
                    ("arbitrage", "Arbitrage"),
                    ("saas", "SaaS/Software"),
                    ("other", "Other"),
                ], max_length=100)),
                ("description", models.TextField()),
                ("trend_score", models.FloatField(default=0.0)),
                ("difficulty_score", models.FloatField(default=0.0)),
                ("startup_cost_estimate", models.CharField(blank=True, max_length=100, null=True)),
                ("income_potential", models.CharField(blank=True, max_length=100, null=True)),
                ("time_to_first_dollar", models.CharField(blank=True, max_length=100, null=True)),
                ("success_stories", models.JSONField(default=list)),
                ("reddit_discussions", models.JSONField(default=list)),
                ("market_size_signals", models.JSONField(default=dict)),
                ("required_skills", models.JSONField(default=list)),
                ("required_tools", models.JSONField(default=list)),
                ("saturation_level", models.CharField(choices=[
                    ("low", "Low"),
                    ("medium", "Medium"),
                    ("high", "High"),
                    ("oversaturated", "Oversaturated"),
                ], default="medium", max_length=20)),
                ("risks", models.JSONField(default=list)),
                ("source_spiders", models.JSONField(default=list)),
                ("spider_data_ids", models.JSONField(default=list)),
                ("first_detected", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "side_hustle",
                "ordering": ["-trend_score", "-first_detected"],
            },
        ),

        # =====================================================================
        # FINANCIAL INTELLIGENCE
        # =====================================================================

        # SECFilingAnalysis
        migrations.CreateModel(
            name="SECFilingAnalysis",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("company_name", models.CharField(max_length=200)),
                ("ticker", models.CharField(blank=True, max_length=20, null=True)),
                ("cik", models.CharField(blank=True, max_length=20, null=True)),
                ("form_type", models.CharField(max_length=20)),
                ("filing_date", models.DateField()),
                ("filing_url", models.URLField()),
                ("summary", models.TextField()),
                ("key_findings", models.JSONField(default=list)),
                ("sentiment", models.CharField(choices=[
                    ("bullish", "Bullish"),
                    ("bearish", "Bearish"),
                    ("neutral", "Neutral"),
                ], max_length=20)),
                ("significance_score", models.FloatField(default=0.0)),
                ("position_changes", models.JSONField(default=list)),
                ("notable_moves", models.JSONField(default=list)),
                ("event_type", models.CharField(blank=True, max_length=100, null=True)),
                ("material_impact", models.BooleanField(default=False)),
                ("price_before", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("price_after", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("volume_change_percent", models.FloatField(blank=True, null=True)),
                ("alert_sent", models.BooleanField(default=False)),
                ("alert_sent_at", models.DateTimeField(blank=True, null=True)),
                ("spider_data_id", models.UUIDField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "sec_filing_analysis",
                "ordering": ["-filing_date", "-significance_score"],
            },
        ),

        # CryptoSentiment
        migrations.CreateModel(
            name="CryptoSentiment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("symbol", models.CharField(max_length=20)),
                ("name", models.CharField(max_length=100)),
                ("overall_sentiment", models.FloatField(default=0.0)),
                ("reddit_sentiment", models.FloatField(blank=True, null=True)),
                ("twitter_sentiment", models.FloatField(blank=True, null=True)),
                ("news_sentiment", models.FloatField(blank=True, null=True)),
                ("social_volume", models.IntegerField(default=0)),
                ("social_volume_change", models.FloatField(blank=True, null=True)),
                ("trending_topics", models.JSONField(default=list)),
                ("influencer_mentions", models.JSONField(default=list)),
                ("fear_greed_index", models.IntegerField(blank=True, null=True)),
                ("bullish_posts", models.JSONField(default=list)),
                ("bearish_posts", models.JSONField(default=list)),
                ("price_at_measurement", models.DecimalField(blank=True, decimal_places=8, max_digits=20, null=True)),
                ("price_change_24h", models.FloatField(blank=True, null=True)),
                ("sentiment_alert_triggered", models.BooleanField(default=False)),
                ("volume_alert_triggered", models.BooleanField(default=False)),
                ("source_spiders", models.JSONField(default=list)),
                ("spider_data_ids", models.JSONField(default=list)),
                ("measured_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "crypto_sentiment",
                "ordering": ["-measured_at"],
            },
        ),

        # EarningsPrediction
        migrations.CreateModel(
            name="EarningsPrediction",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("company_name", models.CharField(max_length=200)),
                ("ticker", models.CharField(max_length=20)),
                ("sector", models.CharField(blank=True, max_length=100, null=True)),
                ("earnings_date", models.DateField()),
                ("earnings_time", models.CharField(blank=True, max_length=20, null=True)),
                ("eps_estimate", models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ("revenue_estimate", models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ("predicted_surprise", models.CharField(choices=[
                    ("beat", "Will Beat"),
                    ("miss", "Will Miss"),
                    ("inline", "In Line"),
                ], max_length=20)),
                ("confidence_score", models.FloatField(default=0.0)),
                ("bull_case", models.TextField(blank=True)),
                ("bear_case", models.TextField(blank=True)),
                ("bull_confidence", models.FloatField(default=0.0)),
                ("bear_confidence", models.FloatField(default=0.0)),
                ("insider_activity", models.JSONField(default=dict)),
                ("options_flow", models.JSONField(default=dict)),
                ("analyst_revisions", models.JSONField(default=list)),
                ("sector_performance", models.JSONField(default=dict)),
                ("price_5d_before", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("implied_move", models.FloatField(blank=True, null=True)),
                ("actual_eps", models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ("actual_revenue", models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ("actual_surprise", models.CharField(blank=True, max_length=20, null=True)),
                ("prediction_correct", models.BooleanField(null=True)),
                ("spider_data_ids", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "earnings_prediction",
                "ordering": ["earnings_date", "-confidence_score"],
            },
        ),

        # =====================================================================
        # RESEARCH & LEARNING
        # =====================================================================

        # TechStackTrend
        migrations.CreateModel(
            name="TechStackTrend",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=200)),
                ("category", models.CharField(choices=[
                    ("language", "Programming Language"),
                    ("framework", "Framework"),
                    ("library", "Library"),
                    ("database", "Database"),
                    ("devops", "DevOps/Infrastructure"),
                    ("cloud", "Cloud Service"),
                    ("ai_ml", "AI/ML Tool"),
                    ("other", "Other"),
                ], max_length=100)),
                ("description", models.TextField(blank=True)),
                ("popularity_score", models.FloatField(default=0.0)),
                ("momentum_score", models.FloatField(default=0.0)),
                ("job_demand_score", models.FloatField(default=0.0)),
                ("github_stars", models.IntegerField(blank=True, null=True)),
                ("github_stars_growth", models.FloatField(blank=True, null=True)),
                ("npm_downloads", models.IntegerField(blank=True, null=True)),
                ("stackoverflow_questions", models.IntegerField(blank=True, null=True)),
                ("job_postings_count", models.IntegerField(blank=True, null=True)),
                ("avg_salary", models.IntegerField(blank=True, null=True)),
                ("hackernews_mentions", models.IntegerField(blank=True, null=True)),
                ("reddit_mentions", models.IntegerField(blank=True, null=True)),
                ("trend_direction", models.CharField(choices=[
                    ("rising_fast", "Rising Fast"),
                    ("rising", "Rising"),
                    ("stable", "Stable"),
                    ("declining", "Declining"),
                    ("declining_fast", "Declining Fast"),
                ], max_length=20)),
                ("should_learn", models.BooleanField(default=False)),
                ("learning_resources", models.JSONField(default=list)),
                ("source_spiders", models.JSONField(default=list)),
                ("spider_data_ids", models.JSONField(default=list)),
                ("first_tracked", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "tech_stack_trend",
                "ordering": ["-momentum_score", "-popularity_score"],
            },
        ),

        # AIModelRelease
        migrations.CreateModel(
            name="AIModelRelease",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=200)),
                ("organization", models.CharField(max_length=200)),
                ("model_type", models.CharField(choices=[
                    ("llm", "Large Language Model"),
                    ("image", "Image Generation"),
                    ("video", "Video Generation"),
                    ("audio", "Audio/Speech"),
                    ("multimodal", "Multimodal"),
                    ("embedding", "Embedding Model"),
                    ("code", "Code Generation"),
                    ("other", "Other"),
                ], max_length=100)),
                ("release_date", models.DateField()),
                ("version", models.CharField(blank=True, max_length=50, null=True)),
                ("is_open_source", models.BooleanField(default=False)),
                ("license_type", models.CharField(blank=True, max_length=100, null=True)),
                ("announcement_url", models.URLField(blank=True, null=True)),
                ("paper_url", models.URLField(blank=True, null=True)),
                ("model_url", models.URLField(blank=True, null=True)),
                ("api_url", models.URLField(blank=True, null=True)),
                ("capabilities", models.JSONField(default=list)),
                ("benchmark_scores", models.JSONField(default=dict)),
                ("context_length", models.IntegerField(blank=True, null=True)),
                ("significance_score", models.FloatField(default=0.0)),
                ("innovation_notes", models.TextField(blank=True)),
                ("use_cases", models.JSONField(default=list)),
                ("limitations", models.JSONField(default=list)),
                ("compared_to", models.JSONField(default=list)),
                ("improvements", models.JSONField(default=list)),
                ("alert_sent", models.BooleanField(default=False)),
                ("alert_sent_at", models.DateTimeField(blank=True, null=True)),
                ("source_spiders", models.JSONField(default=list)),
                ("spider_data_ids", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "ai_model_release",
                "ordering": ["-release_date", "-significance_score"],
            },
        ),

        # SkillGapAnalysis
        migrations.CreateModel(
            name="SkillGapAnalysis",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("skill_name", models.CharField(max_length=200)),
                ("category", models.CharField(max_length=100)),
                ("demand_score", models.FloatField(default=0.0)),
                ("demand_trend", models.CharField(choices=[
                    ("rising_fast", "Rising Fast"),
                    ("rising", "Rising"),
                    ("stable", "Stable"),
                    ("declining", "Declining"),
                ], max_length=20)),
                ("job_count", models.IntegerField(blank=True, null=True)),
                ("avg_salary_premium", models.FloatField(blank=True, null=True)),
                ("user_current_level", models.CharField(blank=True, choices=[
                    ("none", "No Experience"),
                    ("beginner", "Beginner"),
                    ("intermediate", "Intermediate"),
                    ("advanced", "Advanced"),
                    ("expert", "Expert"),
                ], max_length=20, null=True)),
                ("gap_score", models.FloatField(default=0.0)),
                ("estimated_learning_time", models.CharField(blank=True, max_length=100, null=True)),
                ("recommended_courses", models.JSONField(default=list)),
                ("prerequisite_skills", models.JSONField(default=list)),
                ("complementary_skills", models.JSONField(default=list)),
                ("source_spiders", models.JSONField(default=list)),
                ("spider_data_ids", models.JSONField(default=list)),
                ("analyzed_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "skill_gap_analysis",
                "ordering": ["-demand_score", "-gap_score"],
            },
        ),

        # =====================================================================
        # LEGAL INTELLIGENCE
        # =====================================================================

        # CaseLawUpdate
        migrations.CreateModel(
            name="CaseLawUpdate",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("case_name", models.CharField(max_length=500)),
                ("case_number", models.CharField(blank=True, max_length=100, null=True)),
                ("court", models.CharField(max_length=200)),
                ("jurisdiction", models.CharField(max_length=100)),
                ("decision_date", models.DateField()),
                ("decision_type", models.CharField(choices=[
                    ("opinion", "Opinion"),
                    ("order", "Order"),
                    ("ruling", "Ruling"),
                    ("judgment", "Judgment"),
                    ("dismissal", "Dismissal"),
                ], max_length=50)),
                ("summary", models.TextField()),
                ("key_holdings", models.JSONField(default=list)),
                ("legal_issues", models.JSONField(default=list)),
                ("practice_areas", models.JSONField(default=list)),
                ("topics", models.JSONField(default=list)),
                ("relevance_score", models.FloatField(default=0.0)),
                ("precedential_value", models.CharField(blank=True, choices=[
                    ("binding", "Binding"),
                    ("persuasive", "Persuasive"),
                    ("limited", "Limited"),
                ], max_length=20, null=True)),
                ("overrules", models.JSONField(default=list)),
                ("distinguishes", models.JSONField(default=list)),
                ("case_url", models.URLField(blank=True, null=True)),
                ("pdf_url", models.URLField(blank=True, null=True)),
                ("alert_sent", models.BooleanField(default=False)),
                ("alert_sent_at", models.DateTimeField(blank=True, null=True)),
                ("source_spider", models.CharField(max_length=100)),
                ("spider_data_id", models.UUIDField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "case_law_update",
                "ordering": ["-decision_date", "-relevance_score"],
            },
        ),

        # RegulatoryChange
        migrations.CreateModel(
            name="RegulatoryChange",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=500)),
                ("agency", models.CharField(max_length=200)),
                ("regulation_type", models.CharField(choices=[
                    ("proposed_rule", "Proposed Rule"),
                    ("final_rule", "Final Rule"),
                    ("guidance", "Guidance"),
                    ("enforcement", "Enforcement Action"),
                    ("notice", "Notice"),
                    ("executive_order", "Executive Order"),
                ], max_length=50)),
                ("summary", models.TextField()),
                ("key_changes", models.JSONField(default=list)),
                ("affected_parties", models.JSONField(default=list)),
                ("published_date", models.DateField()),
                ("effective_date", models.DateField(blank=True, null=True)),
                ("comment_deadline", models.DateField(blank=True, null=True)),
                ("impact_score", models.FloatField(default=0.0)),
                ("industries_affected", models.JSONField(default=list)),
                ("compliance_requirements", models.JSONField(default=list)),
                ("estimated_compliance_cost", models.CharField(blank=True, max_length=100, null=True)),
                ("document_url", models.URLField(blank=True, null=True)),
                ("federal_register_url", models.URLField(blank=True, null=True)),
                ("status", models.CharField(choices=[
                    ("proposed", "Proposed"),
                    ("pending", "Pending"),
                    ("active", "Active"),
                    ("withdrawn", "Withdrawn"),
                ], max_length=20)),
                ("alert_sent", models.BooleanField(default=False)),
                ("alert_sent_at", models.DateTimeField(blank=True, null=True)),
                ("source_spider", models.CharField(max_length=100)),
                ("spider_data_id", models.UUIDField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "regulatory_change",
                "ordering": ["-published_date", "-impact_score"],
            },
        ),

        # =====================================================================
        # MONITORING
        # =====================================================================

        # AutonomousSituationSession
        migrations.CreateModel(
            name="AutonomousSituationSession",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("situation_type", models.CharField(choices=[
                    ("design_trends", "Design Trends"),
                    ("viral_prediction", "Viral Prediction"),
                    ("thumbnail_optimization", "Thumbnail Optimization"),
                    ("job_matching", "Job Matching"),
                    ("freelance_scout", "Freelance Scout"),
                    ("side_hustle", "Side Hustle Detection"),
                    ("sec_filing", "SEC Filing Analysis"),
                    ("crypto_sentiment", "Crypto Sentiment"),
                    ("earnings_prediction", "Earnings Prediction"),
                    ("tech_stack", "Tech Stack Evolution"),
                    ("ai_model", "AI Model Releases"),
                    ("skill_gap", "Skill Gap Analysis"),
                    ("case_law", "Case Law Monitor"),
                    ("regulatory", "Regulatory Changes"),
                ], max_length=50)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("next_scheduled", models.DateTimeField(blank=True, null=True)),
                ("items_processed", models.IntegerField(default=0)),
                ("items_created", models.IntegerField(default=0)),
                ("items_updated", models.IntegerField(default=0)),
                ("alerts_generated", models.IntegerField(default=0)),
                ("status", models.CharField(choices=[
                    ("running", "Running"),
                    ("completed", "Completed"),
                    ("failed", "Failed"),
                ], default="running", max_length=20)),
                ("error_message", models.TextField(blank=True, null=True)),
                ("duration_seconds", models.FloatField(blank=True, null=True)),
                ("spider_data_analyzed", models.IntegerField(default=0)),
            ],
            options={
                "db_table": "autonomous_situation_session",
                "ordering": ["-started_at"],
            },
        ),
    ]
