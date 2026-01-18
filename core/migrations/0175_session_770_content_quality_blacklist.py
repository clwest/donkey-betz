# Session 770: Content Quality Blacklist and Topic Diversity Tracking
# Generated manually

import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0174_session_770_podcast_tts_cost"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ContentQualityBlacklist",
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
                    "block_type",
                    models.CharField(
                        choices=[
                            ("topic", "Topic"),
                            ("pattern", "Pattern"),
                            ("concept", "Concept"),
                        ],
                        default="topic",
                        max_length=20,
                    ),
                ),
                (
                    "pattern",
                    models.CharField(
                        help_text="The topic, phrase, or regex pattern to block",
                        max_length=500,
                    ),
                ),
                (
                    "pattern_normalized",
                    models.CharField(
                        db_index=True,
                        help_text="Lowercase normalized version for matching",
                        max_length=500,
                    ),
                ),
                (
                    "reason",
                    models.CharField(
                        choices=[
                            ("test_probe", "Test/Probe"),
                            ("joke", "Joke/Humor"),
                            ("unrealistic", "Unrealistic"),
                            ("harmful", "Harmful"),
                            ("low_quality", "Low Quality"),
                            ("recycled", "Over-recycled"),
                            ("user_rejected", "User Rejected"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "reason_detail",
                    models.TextField(blank=True, help_text="Detailed explanation"),
                ),
                (
                    "is_global",
                    models.BooleanField(default=True, help_text="Applies to all users"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "expires_at",
                    models.DateTimeField(
                        blank=True,
                        help_text="When this blacklist item expires (null = permanent)",
                        null=True,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("times_blocked", models.IntegerField(default=0)),
                ("last_blocked_at", models.DateTimeField(blank=True, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="blacklist_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        help_text="User-specific blacklist item (if not global)",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="content_blacklist",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Content Quality Blacklist",
                "verbose_name_plural": "Content Quality Blacklist Items",
            },
        ),
        migrations.CreateModel(
            name="TopicDiversityTracker",
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
                ("topic", models.CharField(db_index=True, max_length=200)),
                ("topic_normalized", models.CharField(db_index=True, max_length=200)),
                ("dream_count", models.IntegerField(default=0)),
                ("knowledge_count", models.IntegerField(default=0)),
                ("last_used_at", models.DateTimeField(auto_now=True)),
                ("first_used_at", models.DateTimeField(auto_now_add=True)),
                (
                    "cooldown_until",
                    models.DateTimeField(
                        blank=True,
                        help_text="Topic is on cooldown until this time",
                        null=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "Topic Diversity Tracker",
                "verbose_name_plural": "Topic Diversity Trackers",
            },
        ),
        migrations.AddIndex(
            model_name="contentqualityblacklist",
            index=models.Index(
                fields=["pattern_normalized", "is_active"],
                name="core_conten_pattern_552d39_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="contentqualityblacklist",
            index=models.Index(
                fields=["block_type", "is_active"],
                name="core_conten_block_t_fab5b9_idx",
            ),
        ),
    ]
