# Session 783: Spider Data Annotation model
# Generated manually for focused migration

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0176_learning_journey_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="SpiderDataAnnotation",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "annotation_type",
                    models.CharField(
                        choices=[
                            ("useful", "Useful"),
                            ("profitable", "Profitable Opportunity"),
                            ("podcast_worthy", "Podcast Worthy"),
                            ("breaking_news", "Breaking News"),
                            ("investment_opportunity", "Investment Opportunity"),
                            ("action_required", "Action Required"),
                            ("warning", "Warning/Risk"),
                            ("trending", "Trending"),
                        ],
                        db_index=True,
                        max_length=50,
                    ),
                ),
                ("confidence_score", models.FloatField(default=0.5)),
                ("note", models.TextField(blank=True)),
                ("agent_name", models.CharField(db_index=True, max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("upvotes", models.IntegerField(default=0)),
                ("downvotes", models.IntegerField(default=0)),
                ("view_count", models.IntegerField(default=0)),
                (
                    "spider_data",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="annotations",
                        to="core.spiderdata",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "unique_together": {("spider_data", "agent_name", "annotation_type")},
            },
        ),
        migrations.AddIndex(
            model_name="spiderdataannotation",
            index=models.Index(
                fields=["annotation_type", "created_at"],
                name="core_spider_annotat_612e35_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="spiderdataannotation",
            index=models.Index(
                fields=["agent_name", "created_at"],
                name="core_spider_agent_n_ec1187_idx",
            ),
        ),
    ]
